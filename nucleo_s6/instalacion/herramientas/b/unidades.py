"""Ejecución de Paquete B por UNIDADES de memoria acotada, con checkpoints verificables, reanudación y presupuestos
(ESTRATEGIA_DE_CALCULO §6).

Partición (determinista, identificada por el hash del plan): por set evaluado, prefijo de índices de nudos de los
primeros k ejes estructurales (orden fijo STRUCT) con k mínimo tal que el resto del producto <= max_unit_nodes.
Cada unidad se ejecuta con paper2b.run.Run(unit=...) — solo sus omegas —, se valida (reglas contratadas + FK con D7
sobre sus propias filas) y se escribe como archivos JSONL por tabla ORDENADOS por la clave canónica, más un resumen
acotado (rangos de soporte, contribuciones de claims y de sensibilidad de Q, cajas certificadas). Tras cada unidad el
checkpoint (checkpoint.json) se reemplaza atómicamente con el hash de cada archivo. Nunca se acumulan en RAM el
producto cartesiano ni las tablas completas: la fase global usa solo resúmenes y el ensamblado es una mezcla externa
(heapq.merge) de archivos ordenados escrita en flujo (tables.StreamTable) hacia la familia B vía staging atómico.

Reanudación: solo con la MISMA identidad (autoridad, contrato, D7, entradas técnicas y de datos, código, configuración
sin el presupuesto total de pared budget_seconds, presupuesto por inversión, proveedor de modelo y plan); cualquier
diferencia -> CHECKPOINT_INCOMPATIBLE:<campo>. El presupuesto por inversión (RunConfig.inversion_budget_seconds) SÍ es
parte de la identidad: cambia qué inversiones terminan, así que un checkpoint hecho con otro valor nunca se reanuda. Cada archivo
de unidad se reverifica por hash (CHECKPOINT_CORRUPT). Las rutas son relativas al directorio del checkpoint: se puede
reubicar. Presupuestos (pared, pico de memoria por unidad, disco): al agotarse, el estado queda 'incomplete' con
RESOURCE_BUDGET_EXHAUSTED y las unidades terminadas se conservan; una unidad interrumpida no se escribe.
Un checkpoint parcial es diagnóstico: nunca se emite como versión B.
"""
from __future__ import annotations

import hashlib
import heapq
import json
import math
import os
import shutil
import time
import tracemalloc
import uuid
from dataclasses import dataclass, replace
from itertools import product
from pathlib import Path

from paper2b import claims as CL
from paper2b import cobertura as COV
from paper2b import keys as K
from paper2b import run as RUN
from paper2b import rules as RULES
from paper2b import tables as T
from paper2b.supports import level_nodes

SCHEMA = "paper2b-b-checkpoint-v1"
VOLATILE = {"computation_coverage": ("elapsed_seconds", "peak_bytes")}
_INTERRUPT_HOOK = None      # SOLO pruebas: llamado tras cada unidad escrita (simula interrupción del proceso)


class CheckpointError(RuntimeError):
    pass


class BudgetStop(RuntimeError):
    pass


def need(test, code):
    if not test:
        raise CheckpointError(code)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canon(obj) -> bytes:
    return K.canon(obj) + b"\n"


@dataclass(frozen=True)
class Budgets:
    wall_seconds: float | None = None
    peak_bytes_per_unit: int | None = None
    disk_bytes: int | None = None

    def as_dict(self):
        return {"wall_seconds": self.wall_seconds, "peak_bytes_per_unit": self.peak_bytes_per_unit, "disk_bytes": self.disk_bytes}


def plan_units(inp: RUN.RunInputs, cfg: RUN.RunConfig) -> list:
    probe = RUN.Run(inp, cfg)
    units = []
    for set_id in probe.evaluated_sets():
        axes = {pid: level_nodes(inp.d7.nodes(set_id, pid), inp.d7.support(set_id, pid)["scale"], cfg.level) for pid in RUN.STRUCT}
        sizes = [len(axes[p]) for p in RUN.STRUCT]
        rest, k = math.prod(sizes), 0
        while rest > cfg.max_unit_nodes and k < len(sizes):
            rest //= sizes[k]
            k += 1
        for idx in product(*[range(sizes[i]) for i in range(k)]):
            prefix = {RUN.STRUCT[i]: idx[i] for i in range(k)}
            units.append({"unit_id": "U" + K.H([set_id, sorted(prefix.items())])[:24], "set_id": set_id, "prefix": prefix})
    return units


def identity(inp: RUN.RunInputs, cfg: RUN.RunConfig, *, authority, code_manifest_sha256: str, units: list) -> dict:
    cfgd = dict(cfg.as_dict())
    cfgd.pop("budget_seconds", None)          # presupuesto TOTAL de pared: operativo, no cambia el conjunto económico
    model = inp.model.kind if inp.model is not None else "modelo_teorico_v2_2"
    return {"authority_package_sha256": authority.package_sha256, "authority_manifest_sha256": authority.manifest_sha256,
            "inversion_budget_seconds": cfg.inversion_budget_seconds,     # también dentro de configuration_sha256
            "contract_sha256": inp.contract_sha256, "code_manifest_sha256": code_manifest_sha256,
            "configuration_sha256": K.H(cfgd), "model_provider": model, "d7_tree_sha256": inp.d7.manifest["tree_sha256"],
            "inputs_sha256": K.H({"grid": inp.grid_sha256, "matrix": inp.availability_matrix_hash, "registry": K.H(inp.registry),
                                  "model_case_map": K.H(inp.model_case_map), "theory": list(inp.theory), "protocol": list(inp.protocol),
                                  "technical": inp.technical, "crosswalk": inp.crosswalk_sha256, "dme": repr(inp.dme_gai),
                                  "tolerances": inp.tolerances}),
            "plan_sha256": K.H(units)}


class Executor:
    def __init__(self, inp: RUN.RunInputs, cfg: RUN.RunConfig, checkpoint_dir: Path, *, authority, code_manifest_sha256: str,
                 budgets: Budgets = Budgets(), resolver=None):
        self.inp, self.cfg, self.dir = inp, cfg, Path(checkpoint_dir)
        self.C = inp.contracts
        self.authority, self.budgets, self.resolver = authority, budgets, resolver
        self.units = plan_units(inp, cfg)
        self.ident = identity(inp, cfg, authority=authority, code_manifest_sha256=code_manifest_sha256, units=self.units)

    # --------------------------------------------------------------------------------- checkpoint
    def _ck_path(self):
        return self.dir / "checkpoint.json"

    def _save(self, state: dict):
        tmp = self.dir / (".checkpoint." + uuid.uuid4().hex)
        tmp.write_bytes(canon(state))
        os.replace(tmp, self._ck_path())

    def load(self, *, resume: bool) -> dict:
        if self._ck_path().exists():
            need(resume, "CHECKPOINT_EXISTS_USE_RESUME")
            state = json.loads(self._ck_path().read_bytes())
            need(state.get("schema") == SCHEMA, "CHECKPOINT_SCHEMA")
            for k, v in self.ident.items():
                need(state["identity"].get(k) == v, "CHECKPOINT_INCOMPATIBLE:" + k)
            need(state["identity"] == self.ident, "CHECKPOINT_INCOMPATIBLE:identity")
            for uid, d in state["done"].items():
                for rel, h in d["files"].items():
                    q = self.dir / rel
                    need(q.is_file() and sha(q.read_bytes()) == h, "CHECKPOINT_CORRUPT:" + uid)
            return state
        need(not resume or not self.dir.exists() or not any(self.dir.iterdir()), "CHECKPOINT_MISSING")
        self.dir.mkdir(parents=True, exist_ok=True)
        state = {"schema": SCHEMA, "identity": self.ident, "units": [u["unit_id"] for u in self.units], "done": {},
                 "status": "in_progress", "reason": None, "budgets": self.budgets.as_dict()}
        self._save(state)
        return state

    # --------------------------------------------------------------------------------- unidades
    def _disk_used(self) -> int:
        return sum(q.stat().st_size for q in self.dir.rglob("*") if q.is_file())

    def _write_unit(self, unit: dict, rows: dict, summary: dict) -> dict:
        udir = self.dir / "unidades" / unit["unit_id"]
        stage = self.dir / "unidades" / (".tmp-" + uuid.uuid4().hex)
        stage.mkdir(parents=True)
        files = {}
        try:
            for name in sorted(rows):
                if not rows[name]:
                    continue
                key = T.order_key(self.C, name)
                norm = []
                for r in rows[name]:
                    fin = r.pop("_fin", None)
                    n = T.normalize_row(self.C, name, r)
                    if fin is not None:
                        n["_fin"] = fin
                    norm.append(n)
                norm.sort(key=lambda r: key({k: v for k, v in r.items() if k != "_fin"}))
                raw = b"".join(K.canon(r) + b"\n" for r in norm)
                (stage / (name + ".jsonl")).write_bytes(raw)
                files[f"unidades/{unit['unit_id']}/{name}.jsonl"] = sha(raw)
            sraw = canon(summary)
            (stage / "resumen.json").write_bytes(sraw)
            files[f"unidades/{unit['unit_id']}/resumen.json"] = sha(sraw)
            if udir.exists():
                shutil.rmtree(udir)          # restos de una unidad no registrada (interrupción previa)
            os.replace(stage, udir)
        finally:
            if stage.exists():
                shutil.rmtree(stage)
        return files

    def _validate_unit(self, rows: dict):
        tables = {n: T.sort_rows(self.C, n, [T.normalize_row(self.C, n, {k: v for k, v in r.items() if k != "_fin"})
                                             for r in rows.get(n, [])]) for n in B_TABLES()}
        self.C.references(dict(tables, **self.inp.d7.tables))
        errs = RULES.check_b(tables, self.C, self.inp.d7, technical=self.inp.technical, protocol_sha256=self.inp.protocol[2],
                             grid_cells=self.inp.grid_cells, resolver=self.resolver, tolerances=self.inp.tolerances)
        need(not errs, "UNIT_RULES:" + "; ".join(errs[:3]))

    def execute(self, *, resume: bool = False) -> dict:
        state = self.load(resume=resume)
        t0 = time.time()
        try:
            for unit in self.units:
                if unit["unit_id"] in state["done"]:
                    continue
                elapsed = time.time() - t0
                if self.budgets.wall_seconds is not None and elapsed >= self.budgets.wall_seconds:
                    raise BudgetStop("RESOURCE_BUDGET_EXHAUSTED:wall")
                if self.budgets.disk_bytes is not None and self._disk_used() >= self.budgets.disk_bytes:
                    raise BudgetStop("RESOURCE_BUDGET_EXHAUSTED:disk")
                remaining = None if self.budgets.wall_seconds is None else self.budgets.wall_seconds - elapsed
                tracemalloc.start()
                try:
                    r = RUN.Run(self.inp, replace(self.cfg, budget_seconds=remaining), unit=unit)
                    rows = r.execute_unit()
                    _, peak = tracemalloc.get_traced_memory()
                finally:
                    tracemalloc.stop()
                if r.incomplete_reasons:
                    raise BudgetStop("RESOURCE_BUDGET_EXHAUSTED:wall")        # unidad parcial: no se escribe
                self._validate_unit(rows)
                summary = dict(r.unit_summary(), peak_bytes=peak, phase_seconds=r.phase_seconds)
                files = self._write_unit(unit, rows, summary)
                state["done"][unit["unit_id"]] = {"files": files, "summary_sha256": files[f"unidades/{unit['unit_id']}/resumen.json"]}
                self._save(state)
                del r, rows
                if _INTERRUPT_HOOK is not None:
                    _INTERRUPT_HOOK(unit)
                if self.budgets.peak_bytes_per_unit is not None and peak > self.budgets.peak_bytes_per_unit:
                    raise BudgetStop("RESOURCE_BUDGET_EXHAUSTED:memory")
        except BudgetStop as exc:
            state.update(status="incomplete", reason=str(exc))
            self._save(state)
            return state
        state.update(status="units_complete", reason=None)
        self._save(state)
        return state

    # --------------------------------------------------------------------------------- fase global
    def summaries(self, state: dict):
        for u in self.units:
            d = state["done"][u["unit_id"]]
            raw = (self.dir / "unidades" / u["unit_id"] / "resumen.json").read_bytes()
            need(sha(raw) == d["summary_sha256"], "CHECKPOINT_CORRUPT:" + u["unit_id"])
            yield json.loads(raw)

    def global_phase(self, state: dict) -> dict:
        """Claims, cobertura del continuo por claim, robustez y sensibilidad de Q desde RESÚMENES (sin celdas)."""
        need(state["status"] in ("units_complete", "complete"), "UNITS_NOT_COMPLETE")
        lam, c2, claims, reasons = {}, None, {}, []
        for s in self.summaries(state):
            reasons += s["incomplete_reasons"]
            for k, (lo, hi) in s["lambda"].items():
                a, b = lam.get(k, (math.inf, -math.inf))
                lam[k] = (min(a, lo), max(b, hi))
            if s["c2"] is not None:
                c2 = (min(c2[0], s["c2"][0]), max(c2[1], s["c2"][1])) if c2 else tuple(s["c2"])
            for cid, c in s["claims"].items():
                agg = claims.setdefault(cid, {"n": 0, "sup": None, "inf": None, "any_none": False, "complete": True,
                                              "tally": COV.Tally(), "q": {}})
                agg["n"] += c["n"]
                agg["sup"] = c["sup"] if agg["sup"] is None else (agg["sup"] if c["sup"] is None else max(agg["sup"], c["sup"]))
                agg["inf"] = c["inf"] if agg["inf"] is None else (agg["inf"] if c["inf"] is None else min(agg["inf"], c["inf"]))
                agg["any_none"] |= c["any_none"]
                agg["complete"] &= c["complete"]
                agg["tally"].merge(COV.Tally.of(c["tally"]))
                for qk, q in c["q"].items():
                    a = agg["q"].setdefault(qk, {"best": None, "wit": None, "bad": False, "n": 0})
                    a["bad"] |= q["bad"]
                    a["n"] += q["n"]
                    if q["wit"] is not None and (a["wit"] is None or q["best"] > a["best"] or
                                                 (q["best"] == a["best"] and tuple(q["wit"]["key"]) < tuple(a["wit"]["key"]))):
                        a["best"], a["wit"] = q["best"], q["wit"]
        g = RUN.Run(self.inp, self.cfg)
        g.incomplete_reasons = list(dict.fromkeys(reasons))
        cls = CL.derive(self.inp.registry, self.inp.model_case_map, g.claim_sets())
        g.claim_list, g.verdicts, g.claim_tally = cls, {}, {}
        for cl in cls:
            if not set(cl.support_sets) <= set(self.cfg.base_sets):
                v = CL.Verdict("not_evaluated", "not_evaluated", None, None, 0, "SETS_NOT_IN_RUN")
            else:
                a = claims.get(cl.claim_id, {"n": 0, "sup": None, "inf": None, "any_none": False, "complete": True,
                                             "tally": COV.Tally(), "q": {}})
                v = CL.evaluate_summary(a["sup"], a["inf"], a["n"], complete=a["complete"] and not g.incomplete_reasons,
                                        any_none=a["any_none"])
                g.claim_tally[cl.claim_id] = a["tally"]
                v = RUN.claim_verdict(v, a["tally"])
            g.verdicts[cl.claim_id] = v
            g.rows["claims"].append(cl.row(v.status))
        g.claim_coverage_rows()
        if self.cfg.run_robustness:
            for cl in cls:
                g.robustness(cl, reduced_q=claims.get(cl.claim_id, {}).get("q", {}))
        g.evidence("pruning", "reducción macro: con estado estructural fijo lambda es afín en (eta_w, pi_j) y G = C2 - N/(lambda y) "
                   "es monótona en lambda y en y para N = Q + DME > 0; los extremos sobre la caja macro están en vértices "
                   "(verificado en pruebas sintéticas independientes)", None, {}, {}, None, "none", "vertex_reduction_proof")
        rows = {n: g.rows[n] for n in g.rows if g.rows[n]}
        tables = {n: T.sort_rows(self.C, n, [T.normalize_row(self.C, n, r) for r in rows.get(n, [])]) for n in B_TABLES()}
        errs = RULES.check_b(tables, self.C, self.inp.d7, technical=self.inp.technical, protocol_sha256=self.inp.protocol[2],
                             grid_cells=self.inp.grid_cells, resolver=self.resolver, tolerances=self.inp.tolerances)
        need(not errs, "GLOBAL_RULES:" + "; ".join(errs[:3]))
        files = self._write_unit({"unit_id": "GLOBAL"}, rows, {"lambda": {k: list(v) for k, v in lam.items()},
                                                              "c2": list(c2) if c2 else None, "run_id": g.run_id})
        state["done"]["GLOBAL"] = {"files": files, "summary_sha256": files["unidades/GLOBAL/resumen.json"]}
        state.update(status="complete", reason=None)
        self._save(state)
        return state

    def run(self, *, resume: bool = False) -> dict:
        state = self.execute(resume=resume)
        if state["status"] == "units_complete":
            state = self.global_phase(state)
        return state

    # --------------------------------------------------------------------------------- ensamblado en flujo
    def _stream(self, uid: str, name: str):
        q = self.dir / "unidades" / uid / (name + ".jsonl")
        if not q.is_file():
            return
        with q.open("rb") as fh:
            for line in fh:
                yield json.loads(line)

    def assemble(self, state: dict, out_dir: Path) -> dict:
        """Mezcla externa de las unidades + fase global en archivos CSV contratados (en flujo) dentro de out_dir.
        Cierra los soportes globales de los despejes (_fin) y calcula los conteos del run_manifest sin cargar tablas."""
        need(state["status"] == "complete", "CHECKPOINT_NOT_COMPLETE")
        for uid, d in state["done"].items():
            for rel, h in d["files"].items():
                q = self.dir / rel
                need(q.is_file() and sha(q.read_bytes()) == h, "CHECKPOINT_CORRUPT:" + uid)
        gl = json.loads((self.dir / "unidades/GLOBAL/resumen.json").read_bytes())
        lam = {k: tuple(v) for k, v in gl["lambda"].items()}
        c2 = tuple(gl["c2"]) if gl["c2"] else (math.inf, -math.inf)
        uids = [u["unit_id"] for u in self.units] + ["GLOBAL"]
        stats = {"n_omega": 0, "n_inadmissible": 0, "n_cells": 0, "by_case": {}, "sets": set(), "incomplete": False}
        info = {}
        for name in B_TABLES():
            key = T.order_key(self.C, name)
            merged = heapq.merge(*[self._stream(u, name) for u in uids],
                                 key=lambda r: key({k: v for k, v in r.items() if k != "_fin"}))
            st = T.StreamTable(self.C, name, Path(out_dir) / self.C.C["tables"][name]["file"].split("/", 1)[1])
            try:
                for r in merged:
                    fin = r.pop("_fin", None)
                    if fin is not None:
                        _finalize(r, fin, lam, c2)
                    if st.write(r):
                        _count(name, r, stats)
            finally:
                info[name] = st.close()
        stats["sets"] = sorted(stats["sets"])
        return {"files": info, "stats": stats, "run_id": gl["run_id"]}


def B_TABLES():
    from herramientas.b.ejecutar_b import B_TABLES as BT
    return BT


def _finalize(row: dict, fin: dict, lam: dict, c2: tuple):
    """Estado computed/outside_support de lambda_required / capture_required con el soporte GLOBAL (mismo criterio que
    inversion.algebraic sobre la corrida completa)."""
    from decimal import Decimal
    v = fin["value"]
    if fin["k"] == "lambda":
        lo, hi = lam.get(fin["set"] + "|" + fin["country"], (math.inf, -math.inf))
        outside = not (lo <= v <= hi)
    else:
        outside = fin["c2_defined"] and not (c2[0] <= v <= c2[1])
    row["result_status"] = "outside_support" if outside else "computed"
    row["outside_support"] = bool(outside)
    row["computation_status"] = "complete"
    _ = Decimal


def _count(name: str, r: dict, stats: dict):
    if name == "omega":
        stats["n_omega"] += 1
        stats["n_inadmissible"] += r["domain_status"] == "excluded"
        stats["sets"].add(r["support_set_id"])
    elif name == "cell_context":
        stats["n_cells"] += 1
        stats["by_case"][r["availability_case_id"]] = stats["by_case"].get(r["availability_case_id"], 0) + 1
    elif name in ("capture_ceiling_result", "confrontation_result", "r1_summary", "r2_sections", "inversion_result",
                  "support_breakdown_result", "external_requirement_sensitivity_result", "computation_coverage"):
        if r["computation_status" if "computation_status" in r else "status"] in ("incomplete", "failed"):
            stats["incomplete"] = True


def comparable(rows_by_table: dict) -> dict:
    """Vista sin columnas volátiles (tiempos/memoria) para comparar corridas continua vs reanudada."""
    out = {}
    for n, rows in rows_by_table.items():
        drop = VOLATILE.get(n, ())
        out[n] = [{k: v for k, v in r.items() if k not in drop} for r in rows]
    return out


# ---------------------------------------------------------------------------------------------------------------------
# CANDIDATO PASO 4 (INTEGRACION E12 3.7, NO OFICIAL; copia aislada; no incorporado): E10 plan por la selección SELLADA.
# Misma función que codigo/flujo_paso4.planificar (la prueba de humo comprueba la igualdad sobre el paquete real).
def plan_selection(sel: dict) -> dict:
    """Lotes = grupos CA2 (preregistro, país, diseño, menú, caso D4: la validación del bundle se paga una vez por (caso,
    país) y proceso); dentro, celdas por clave estructural del punto (diseño, menú, punto) y clave de celda. Pura."""
    grupos = {}
    for f in sel["filas"]:
        g = json.dumps(f["grupo_ca2"], sort_keys=True)
        grupos.setdefault(g, []).append(f)
    lotes = []
    for i, g in enumerate(sorted(grupos)):
        cs = sorted(grupos[g], key=lambda f: (json.dumps([f["testigo"]["diseno"], f["testigo"]["instrumento_hoja"],
                                                           sorted(f["testigo"]["punto"].items())]), f["clave_celda"]))
        lotes.append({"lote_id": "L%02d" % i, "grupo_ca2": json.loads(g), "celdas": [f["clave_celda"] for f in cs]})
    plan = {"selection_rule_id": sel["selection_rule_id"], "sello_seleccion": sel["sello_sha256"],
            "regla_plan": "grupo CA2; dentro, clave estructural del punto", "lotes": lotes}
    plan["plan_sha256"] = hashlib.sha256(json.dumps({k: v for k, v in plan.items() if k != "plan_sha256"}, sort_keys=True,
                                                    ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")).hexdigest()
    return plan


# ---------------------------------------------------------------------------------------------------------------------
# CANDIDATO PASO 4 (CONTRATO PAQUETE 3.7, NO OFICIAL; copia aislada; no incorporado): conexión del paquete por SELECCIÓN
# con el ensamblaje futuro. El contrato de resultados vive en paper2b.contrato_paquete (núcleo candidato).
def exportables_seleccion(contrato: str = "v3") -> tuple:
    """Tablas que exporta (v3) o exportaba (v2) el productor del paquete por selección."""
    from paper2b import contrato_paquete as CP
    return CP.TABLAS[contrato]


def cerrar_provisionales_seleccion(rows: list, lam: dict, c2: tuple) -> list:
    """Cierra con el soporte GLOBAL (el mismo criterio que assemble/_finalize) el estado PROVISIONAL de lambda_required y
    capture_required de las filas inversion_result de un paquete por selección YA VALIDADO; devuelve filas sin `_fin`.
    El estado provisional del paquete no se consume: se sustituye aquí."""
    from paper2b import contrato_paquete as CP
    out = []
    for r in rows:
        r = dict(r)
        fin = r.pop("_fin", None)
        if r["inversion_id"] in CP.PROVISIONALES and r["result_status"] in ("computed", "outside_support"):
            need(isinstance(fin, dict), "FIN_AUSENTE:" + str(r.get("cell_id")))
            _finalize(r, fin, lam, c2)
        else:
            need(fin is None, "FIN_NO_EXIGIDO:" + str(r.get("cell_id")))
        out.append(r)
    return out
# ---------------------------------------------------------------------------------------------------------------------
# CANDIDATO PASO 4 (RELACIONES CONTRATO 3.7, NO OFICIAL; copia aislada; no incorporado): EJECUTOR POR LOTES del paquete
# por SELECCIÓN con contrato v3. Movido desde codigo/flujo_paso4_v2.Ejecutor (misma lógica) con dependencias EXPLÍCITAS:
#   ctx  autoridad S5 y RunInputs (herramientas/b/contexto_s5.ContextoS5 o compatible);
#   ref  Referencia E13 (inyectada: aún módulo del área);
#   V    Verificador de la ruta común (herramientas/s3/validadores/paquete_seleccion.py); su módulo da verificar_paquete;
#   GC   generador por valores (inyectado; su cálculo por valores ya vive en paper2b.seleccion_valores);
#   GE   congelar testigos (E13, inyectado);
#   schema, codigo (manifiesto del productor) y error (clase de error del llamador).
# Selección y plan verificados por la ruta común; el plan debe ser plan_selection (este módulo). Escritura atómica por
# lote; reanudación SOLO por la ruta común (contenido verificado, productor actual); resumen canónico obligatorio.
class EjecutorSeleccion:
    def __init__(self, pdir, ctx, ref, V, *, GC, GE, schema, codigo, error=RuntimeError, almacen_techos=None):
        import sys as _sys
        from paper2b import contrato_paquete as CP
        self.dir, self.ctx, self.ref, self.V, self.GC, self.GE = Path(pdir), ctx, ref, V, GC, GE
        self.CP, self.schema, self.error = CP, schema, error
        self.P2 = _sys.modules[type(V).__module__]
        try:
            self.sel, self.plan = V.verificar_seleccion(self.dir)
        except self.P2.Rechazo as e:
            raise error("%s: %s" % (e.codigo, e.detalle))
        self._need(self.plan == plan_selection(self.sel), "PLAN_DE_UNIDADES_DISTINTO")
        self.ident = {"autoridad": ctx.identity, "tabla_sha256": self.sel["tabla"]["sha256"], "sello_seleccion": self.sel["sello_sha256"],
                      "plan_sha256": self.plan["plan_sha256"], "codigo": codigo, "sup": ctx.cfg.sup.as_dict(), "run_class": ctx.identity["run_class"]}
        # techos compartidos entre Run: dict del proceso (por defecto) o, si se da la fábrica EXPLÍCITA almacen_techos,
        # un almacén persistente de ESTA corrida (herramientas/b/techos_persistentes.py), ligado a self.ident
        self.techos = {} if almacen_techos is None else almacen_techos(self.ident)

    def _need(self, t, code):
        if not t:
            raise self.error(code)

    def _ck(self):
        return self.dir / "checkpoint.json"

    @staticmethod
    def _atomico(p: Path, data: bytes):
        tmp = p.with_name("." + p.name + "." + uuid.uuid4().hex)
        tmp.write_bytes(data)
        os.replace(tmp, p)

    def cargar(self, reanudar):
        if self._ck().exists():
            self._need(reanudar, "CHECKPOINT_EXISTE_USE_REANUDAR")
            r = self.P2.verificar_paquete(self.V, self.dir, "reanudar")
            self._need(r["cumple"], "CHECKPOINT_CONTENIDO:%s" % r["codigos"])
            self._need(r["productor"] == "actual", "CHECKPOINT_INCOMPATIBLE:codigo (productor %s)" % r["productor"])
            return json.loads(self._ck().read_bytes())
        self._need(not reanudar, "CHECKPOINT_AUSENTE")
        st = {"schema": self.schema, "identidad": json.loads(K.canon(self.ident)), "lotes": [l["lote_id"] for l in self.plan["lotes"]], "hechos": {},
              "estado": "en_curso", "historial": []}
        self._atomico(self._ck(), K.canon(st))
        return st

    def _run(self, sid):
        from paper2b import run as RUN
        r = RUN.Run(self.ctx.inp, self.ctx.cfg, unit={"unit_id": "seleccion:" + sid, "set_id": sid, "prefix": {p: 0 for p in RUN.STRUCT}},
                    techos_compartidos=self.techos)
        self._need(r.model.kind == "modelo_teorico_v2_2" and r.model.certified, "PROVEEDOR_NO_CERTIFICADO")
        vincular = getattr(self.techos, "vincular", None)      # almacén persistente: se ata a la corrida antes de usarlo
        if vincular is not None:
            vincular(r)
        return r

    def ejecutar(self, reanudar=False, interrumpir_tras=None):
        CP, GC, P2 = self.CP, self.GC, self.P2
        st = self.cargar(reanudar)
        st["historial"].append({"inicio_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "reanudar": reanudar,
                                "pendientes": [l for l in st["lotes"] if l not in st["hechos"]]})
        self._atomico(self._ck(), K.canon(st))
        filas_sel = {f["clave_celda"]: f for f in self.sel["filas"]}
        try:
            self._lotes(st, filas_sel, interrumpir_tras)
        finally:
            liberar = getattr(self.techos, "liberar_propios", None)   # candados propios de un cálculo fallido o interrumpido
            if liberar is not None:
                liberar("fin_o_error_de_ejecucion")

    def _lotes(self, st, filas_sel, interrumpir_tras):
        CP, GC, P2 = self.CP, self.GC, self.P2
        hechos_ahora = 0
        for lote in self.plan["lotes"]:
            if lote["lote_id"] in st["hechos"]:
                continue
            gen = GC.Generador(self.ctx, self.ref, GC.Compartido(activo=False))
            hojas = sorted({filas_sel[k]["testigo"]["claim_id_hoja"] for k in lote["celdas"]})
            for sid in sorted({s for h in hojas for s in gen.claims[h].support_sets}):
                gen.runs[sid] = self._run(sid)
            gen.U = GC.Universo(gen.runs, GC.qmin_table(self.ctx.inp.grid_cells))
            res, filas = [], {}
            t0 = time.time()
            for k in lote["celdas"]:
                f = filas_sel[k]
                w = self.GE.congelar(f["testigo"])
                r = gen.celda(w, "%s:%s-%s-%s" % (lote["lote_id"], f["testigo"]["diseno"], f["testigo"]["instrumento_hoja"], f["grupo_ca2"]["pais"]))
                r.pop("filas", None)
                r["clave_celda"] = k
                if "clave_E12" in r:
                    run = gen.runs[r["set_id"]]
                    cid, fid = r["clave_E12"]["cell_id"], r["clave_E12"]["frontier_id"]
                    fv3 = CP.filas_de_celda(run.rows, cid, fid, "v3")
                    for t, xs in fv3.items():
                        for x in xs:
                            filas.setdefault(t, {})[id(x)] = x
                    previo = self.V._gen
                    self.V._gen = gen
                    try:
                        der = self.V.derivar(self.sel, f, run.run_id, lote["lote_id"])
                        der["base_resumen"]["cell_id"] = cid
                        esperado = P2.resumen_esperado(self.V, json.loads(K.canon(fv3)), der, r)
                    finally:
                        self.V._gen = previo
                    dif = CP.comprobar_resumen(json.loads(K.canon(r)), esperado)
                    self._need(not dif, "RESUMEN_NO_CANONICO:%s:%s" % (lote["lote_id"], dif[:3]))
                    r = dict(esperado, **{d: r[d] for d in CP.DIAGNOSTICO})
                res.append(r)
            self._escribir_lote(st, lote, res, {t: list(v.values()) for t, v in filas.items()}, round(time.time() - t0, 1))
            hechos_ahora += 1
            if interrumpir_tras is not None and hechos_ahora >= interrumpir_tras and len(st["hechos"]) < len(st["lotes"]):
                st["historial"][-1]["interrumpido_tras_lote"] = lote["lote_id"]
                self._atomico(self._ck(), K.canon(st))
                print(json.dumps({"interrumpido": lote["lote_id"], "hechos": sorted(st["hechos"])}))
                raise SystemExit(75)
        st["estado"] = "completo" if len(st["hechos"]) == len(st["lotes"]) else "incompleto"
        st["historial"][-1]["fin_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self._atomico(self._ck(), K.canon(st))
        print(json.dumps({"estado": st["estado"], "hechos": sorted(st["hechos"]),
                          "celdas": [(c["clave_celda"][:60], c["estado"]) for d in st["hechos"].values() for c in d.get("resumen", [])]}, ensure_ascii=False))

    def _escribir_lote(self, st, lote, res, filas, segundos):
        ldir = self.dir / "lotes" / lote["lote_id"]
        stage = self.dir / "lotes" / (".tmp-" + uuid.uuid4().hex)
        stage.mkdir(parents=True)
        archivos = {}
        try:
            for t in sorted(filas):
                raw = b"".join(K.canon(x) + b"\n" for x in filas[t])
                (stage / (t + ".jsonl")).write_bytes(raw)
                archivos["lotes/%s/%s.jsonl" % (lote["lote_id"], t)] = sha(raw)
            raw = K.canon({"lote_id": lote["lote_id"], "celdas": res, "segundos": segundos})
            (stage / "resultados.json").write_bytes(raw)
            archivos["lotes/%s/resultados.json" % lote["lote_id"]] = sha(raw)
            if ldir.exists():
                shutil.rmtree(ldir)
            os.replace(stage, ldir)
        finally:
            if stage.exists():
                shutil.rmtree(stage)
        st["hechos"][lote["lote_id"]] = {"archivos": archivos, "resumen": [{"clave_celda": c["clave_celda"], "estado": c["estado"]} for c in res],
                                         "fin_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        self._atomico(self._ck(), K.canon(st))


# ---------------------------------------------------------------------------------------------------------------------
# CANDIDATO (RELACIONES CONTRATO 3.7): ENSAMBLAJE GLOBAL de paquetes por selección y SELLO cell_selection. No emite
# freeze-run ni activa banderas: el sello es un artefacto candidato con freeze_run_authorized = False.
def _SG():
    """Familia del soporte global: implementación ÚNICA en herramientas/b/soporte_global.py (este módulo delega)."""
    import importlib.util
    import sys as _sys
    nombre = "cand_soporte_global"
    if nombre not in _sys.modules:
        spec = importlib.util.spec_from_file_location(nombre, Path(__file__).with_name("soporte_global.py"))
        m = importlib.util.module_from_spec(spec)
        _sys.modules[nombre] = m
        spec.loader.exec_module(m)
    return _sys.modules[nombre]


def _sg_llamar(fn, *a, **k):
    SG = _SG()
    try:
        return fn(*a, **k)
    except SG.SoporteError as e:
        raise CheckpointError("%s:%s" % (e.codigo, e.detalle))


def soporte_global(resumen_global: dict, plan_unidades: list, run_id: str) -> dict:
    """Soporte desde el formato GLOBAL/resumen.json (+ unidades cubiertas), validado ESTRICTAMENTE (soporte_global.py):
    esquema, intervalos [lo, hi] finitos y ordenados, run_id y unidades exactas del plan; respaldo «resumen_global»."""
    return _sg_llamar(_SG().desde_resumen_global, resumen_global, plan_unidades, run_id)


def construir_soporte_global(resumenes: list, plan_unidades: list, run_id: str, plan_sha256: str) -> dict:
    """Documento canónico desde los resúmenes de TODAS las unidades (respaldo «resumenes_de_unidad», con sha256)."""
    return _sg_llamar(_SG().construir, resumenes, plan_unidades, run_id, plan_sha256)


def cerrar_provisionales_con_soporte(rows: list, soporte: dict, *, run_id=None, plan_unidades=None, plan_sha256=None, contenidos=()) -> list:
    """Cierra los provisionales SOLO con un soporte global VÁLIDO para la corrida y el plan de la AUTORIDAD del consumidor
    (run_id y plan_unidades obligatorios: el soporte no se autocertifica) y suficiente para ESTAS filas; si no, error
    controlado (CheckpointError con código) antes de finalizar ninguna fila. El criterio es el del núcleo (_finalize)."""
    need(isinstance(run_id, str) and run_id and plan_unidades, "SOPORTE_SIN_AUTORIDAD:el consumidor debe aportar run_id y plan_unidades autenticados")
    return _sg_llamar(_SG().cerrar, rows, soporte, _finalize, run_id=run_id, plan_unidades=plan_unidades, plan_sha256=plan_sha256, contenidos=contenidos)


def sello_cell_selection(sel: dict, plan: dict, identidad: dict) -> dict:
    """Artefacto CANDIDATO del sello cell_selection para un freeze-run futuro: selección, plan, tabla y autoridad por
    hash. No autoriza nada: freeze_run_authorized y b_official_run_authorized van en False y official() no se llama."""
    cuerpo = {"kind": "cell_selection-candidato-v1", "selection_rule_id": sel["selection_rule_id"], "sello_seleccion": sel["sello_sha256"],
              "tabla_sha256": sel["tabla"]["sha256"], "plan_sha256": plan["plan_sha256"], "lotes": [l["lote_id"] for l in plan["lotes"]],
              "celdas": [c for l in plan["lotes"] for c in l["celdas"]], "autoridad": {k: identidad[k] for k in (("s6", "ancla") if "s6" in identidad else ("s5",)) + ("d7", "politica", "recibo", "contrato_sha256")},
              "freeze_run_authorized": False, "b_official_run_authorized": False, "official_export_authorized": False}
    return dict(cuerpo, sello_sha256=sha(canon(cuerpo)))


def verificar_sello_cell_selection(doc: dict, sel: dict, plan: dict, identidad: dict) -> list:
    """Motivos por los que el sello no corresponde a la selección/plan/autoridad o pretende autorizar algo."""
    mot = []
    esperado = sello_cell_selection(sel, plan, identidad)
    if doc != esperado:
        mot.append("sello cell_selection distinto del derivado de selección, plan y autoridad")
    if any(doc.get(f) is not False for f in ("freeze_run_authorized", "b_official_run_authorized", "official_export_authorized")):
        mot.append("el sello candidato no puede autorizar freeze-run, corrida ni exportación oficial")
    return mot
