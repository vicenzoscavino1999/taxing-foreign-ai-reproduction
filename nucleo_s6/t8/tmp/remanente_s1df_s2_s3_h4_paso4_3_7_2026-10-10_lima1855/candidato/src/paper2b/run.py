"""Paquete B: ejecución de las tablas contratadas a partir de un D7 validado (CONTRATOS_D7_B_D8, RE-05/RE-06).

Fronteras de implementación (RE-05): normalización/admisibilidad -> decisiones y bases -> frontera/captura ->
lambda -> requerimiento -> confrontación -> raíces/inversiones -> afirmaciones/robustez -> convergencia/cobertura.
Reutilización (ESTRATEGIA §2): C2 y la frontera se calculan una vez por clave estructural y se enlazan a los contextos
nacionales; la clave macro distingue estados nacionales; nunca se une C2 y K1 de omegas distintos.
Reducción macro demostrada (ESTRATEGIA §3): con estado estructural fijo, lambda es afín en (eta_w, pi) y G es monótona
en lambda y en gain_share (signo de N verificado por celda): los extremos sobre las cajas macro están en vértices.
Los ejes estructurales NO se reducen: se evalúan en nudos del nivel pedido. La cobertura del continuo entre nudos la
decide paper2b.cobertura por cajas: 'certified_pruned' solo con encierro demostrativo de G en toda la caja; si no,
'pending' (el modelo teórico no aporta encierros: ESTRATEGIA §4). Los claims exigen cobertura del continuo y la
robustez de parámetros ESTRUCTURALES exige certificar la región ampliada (no se supone monotonía no demostrada).
Modo por unidades (herramientas/b/unidades.py): `unit` restringe la corrida a un prefijo de nudos estructurales de un
set; las cifras que dependen de agregados globales (soportes de lambda y C2 de los despejes, claims, robustez,
sensibilidad de Q) se cierran después con los resúmenes de todas las unidades.
Presupuestos (tres, distintos):
- RunConfig.budget_seconds: presupuesto TOTAL de la corrida (pared; se comprueba entre celdas); agotado -> corrida
  'incomplete' con RESOURCE_BUDGET_EXHAUSTED en incomplete_reasons.
- RunConfig.inversion_budget_seconds: presupuesto POR INVERSIÓN endógena con evidencia (segundos de pared de la
  evidencia C2(phi) de UNA búsqueda de raíces). Entrada técnica: forma parte de la configuración serializada y de su
  hash (sellos de freeze-run, identidad de checkpoints). Agotado -> esa inversión 'incomplete' con
  EVIDENCE_BUDGET_EXHAUSTED, cobertura parcial y pendientes registrados; nunca se publican sus raíces.
- herramientas/b/unidades.Budgets: presupuestos de la ejecución por unidades (pared, memoria por unidad, disco).
"""
from __future__ import annotations

import json
import math
import time
import tracemalloc
from dataclasses import dataclass, field
from decimal import Decimal
from fractions import Fraction
from itertools import product

from . import claims as CL
from . import cobertura as COV
from . import contour as R1M
from . import external as X
from . import frontier as FR
from . import inversion as INV
from . import keys as K
from . import macro as MC
from . import model as M
from . import robustness as RB
from . import sections as R2M
from .numeric import canon_dec
from .supports import level_nodes
from .supremum import SupConfig
from .supremum import axes as sup_axes
from .modelos import ModeloTeorico
from .intervalos import Iv

# Presupuesto por inversión (segundos): valor por defecto y límites admitidos en una configuración. No hay presupuesto
# ilimitado. Los casos de agotamiento inmediato de las pruebas se ejercitan con el proveedor directamente
# (ModeloTeorico(param_budget_s=...)), nunca con una configuración de corrida inválida.
INVERSION_BUDGET_DEFAULT_S = 3600.0
INVERSION_BUDGET_MIN_S = 1.0
INVERSION_BUDGET_MAX_S = 86400.0


def validate_inversion_budget(value) -> float:
    """Presupuesto por inversión como float finito en [INVERSION_BUDGET_MIN_S, INVERSION_BUDGET_MAX_S]; ValueError si no.
    Se aceptan int y float (se normaliza a float para que la serialización y su hash no dependan del tipo)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("RUNCONFIG_INVERSION_BUDGET_TYPE:%s" % type(value).__name__)
    v = float(value)
    if not math.isfinite(v):
        raise ValueError("RUNCONFIG_INVERSION_BUDGET_NOT_FINITE:%r" % v)
    if not (INVERSION_BUDGET_MIN_S <= v <= INVERSION_BUDGET_MAX_S):
        raise ValueError("RUNCONFIG_INVERSION_BUDGET_OUT_OF_RANGE:%r not in [%r, %r]" % (v, INVERSION_BUDGET_MIN_S,
                                                                                     INVERSION_BUDGET_MAX_S))
    return v

STRUCT = ("a", "beta_tilde", "eta_d", "eta_f", "kappa_tilde", "phi", "rho", "u_theta", "z_cost")
FIXED = ("c_legal", "gamma", "t", "z_m")
MACRO = ("eta_H", "eta_w", "gain_share", "pi_iva", "pi_otros_productos", "pi_produccion")
BARS = ("bar_tau_d", "bar_tau_f")
COMMON_DERIVED = ("B_pot", "beta", "delta", "delta_tilde", "kappa0", "q_pot", "theta")
DERIVED_FORMULA = {k: k for k in COMMON_DERIVED}


@dataclass(frozen=True)
class RunConfig:
    run_class: str = "synthetic_validation"
    base_sets: tuple = ()
    derived_suffixes: tuple = ()
    level: int = 0
    designs: tuple = ("G", "N")
    sup: SupConfig = SupConfig()
    frontier_n: int = 4
    r1_n: int = 8
    r2_n: int = 64
    phi_n: int = 8
    r1_geometry_tol: float = 1e-3
    r1_max_level: int = 6
    endogenous_xtol: float = 1e-10
    robustness_ladder: tuple = (1.25, 1.5, 2.0, 3.0, 4.0)
    robustness_bisect_tol: float = 0.01
    phi_fiscal_budget_s: float = 120.0
    coverage_union: bool = True
    run_robustness: bool = True
    run_geometry: bool = True
    run_endogenous: bool = True
    budget_seconds: float | None = None
    coverage_max_depth: int = 4
    max_unit_nodes: int = 64
    struct_cache_max: int | None = None
    inversion_budget_seconds: float = INVERSION_BUDGET_DEFAULT_S

    def __post_init__(self):
        object.__setattr__(self, "inversion_budget_seconds", validate_inversion_budget(self.inversion_budget_seconds))

    def as_dict(self) -> dict:
        return {"run_class": self.run_class, "base_sets": list(self.base_sets), "derived_suffixes": list(self.derived_suffixes),
                "level": self.level, "designs": list(self.designs), "sup": self.sup.as_dict(), "frontier_n": self.frontier_n,
                "r1_n": self.r1_n, "r1_geometry_tol": self.r1_geometry_tol, "r1_max_level": self.r1_max_level, "endogenous_xtol": self.endogenous_xtol, "r2_n": self.r2_n, "phi_n": self.phi_n, "robustness_ladder": list(self.robustness_ladder),
                "robustness_bisect_tol": self.robustness_bisect_tol, "run_robustness": self.run_robustness,
                "run_geometry": self.run_geometry, "run_endogenous": self.run_endogenous, "budget_seconds": self.budget_seconds,
                "coverage_max_depth": self.coverage_max_depth, "max_unit_nodes": self.max_unit_nodes,
                "struct_cache_max": self.struct_cache_max, "inversion_budget_seconds": self.inversion_budget_seconds}


def provider_for(cfg: RunConfig):
    """Proveedor por defecto de la corrida (modelo teórico v2.2 con encierros) con el presupuesto por inversión DE LA
    CONFIGURACIÓN. Única construcción del proveedor por defecto en la ruta de B."""
    return ModeloTeorico(param_budget_s=cfg.inversion_budget_seconds)


def provider_inversion_budget(model, cfg: RunConfig):
    """Presupuesto por inversión EFECTIVO del proveedor: el de la configuración si el proveedor lo consume (atributo
    param_budget_s), None si su evidencia no tiene presupuesto (sustitutos, modelo sin encierros). Un proveedor con otro
    presupuesto que el configurado se rechaza: nunca se ejecuta con un valor distinto del declarado."""
    b = getattr(model, "param_budget_s", None)
    if b is None:
        return None
    if float(b) != cfg.inversion_budget_seconds:
        raise ValueError("PROVIDER_INVERSION_BUDGET_MISMATCH:%r!=%r" % (float(b), cfg.inversion_budget_seconds))
    return float(b)


@dataclass
class RunInputs:
    contracts: object
    d7: object                      # D7View
    registry: dict
    grid_cells: list
    grid_sha256: str
    grid_dependency: dict           # shape 'dependency' de CLAVES (manifiesto D7, artefacto grilla)
    model_case_map: list
    availability_matrix_hash: str
    national: object                # national(set_id, country) -> list[NationalState | dict(strict domain)]
    conditional_key: object | None  # (state, omega, block, (design, instrument, case)) -> (payload, sha)
    technical: dict
    theory: tuple
    protocol: tuple
    manifest_hash: str
    contract_sha256: str
    producer_sha256: str
    environment_manifest_sha256: str
    algorithm_config_sha256: str
    crosswalk_sha256: str
    dme_gai: float = 0.0
    supplier_targets: dict = field(default_factory=dict)
    external_factor_mapping: object | None = None
    set_index: dict = field(default_factory=dict)   # preregistro -> edición -> bloque -> base set
    created_at: str = ""
    model: object | None = None                      # proveedor de modelo (por defecto el modelo teórico v2.2)
    tolerances: dict = field(default_factory=dict)   # T2 validado, residuo de raíces, etc. (entrada técnica)


class Budget:
    def __init__(self, seconds):
        self.seconds, self.t0 = seconds, time.time()

    def exhausted(self) -> bool:
        return self.seconds is not None and time.time() - self.t0 > self.seconds


def _dec(x) -> str:
    return canon_dec(x)


def _to_state_prim(values: dict) -> dict:
    return {k: float(v) for k, v in values.items()}


class _LRU(dict):
    """Caché acotada (memoria por lotes): expulsa la entrada más antigua al superar max_size."""

    def __init__(self, max_size):
        super().__init__()
        self.max_size = max_size

    def __setitem__(self, k, v):
        if k in self:
            super().__delitem__(k)
        super().__setitem__(k, v)
        if self.max_size is not None and len(self) > self.max_size:
            super().__delitem__(next(iter(self)))


class Run:
    def __init__(self, inp: RunInputs, cfg: RunConfig, *, unit: dict | None = None, techos_compartidos: dict | None = None):
        self.inp, self.cfg = inp, cfg
        self.unit = unit            # {"unit_id", "set_id", "prefix": {pid: índice de nudo}} o None (corrida monolítica)
        # CANDIDATO E11 (paso 4, NO OFICIAL): caché de techos de PROCESO compartida entre Run. None = comportamiento
        # original. La clave es compat_techo(skey): clave estructural + autoridad (run_id: D7, configuración, productor,
        # contrato) + configuración del supremo (SupConfig) + proveedor (tipo, garantía, cajas, presupuesto de saltos).
        # Solo se reutiliza si TODO coincide; nunca entre corridas de identidad distinta (p. ej. una reproducción R2).
        self.techos_compartidos = techos_compartidos
        self.C = inp.contracts
        self.model = inp.model if inp.model is not None else provider_for(cfg)
        self.inversion_budget_s = provider_inversion_budget(self.model, cfg)
        tol = inp.tolerances or {}
        self.t2 = float(tol.get("T2_target_capture_share", "1e-4"))
        self.tol_root = float(tol.get("T_root_residual", "1e-9"))
        self.units = {pid: p.get("unit", "not_applicable") for pid, p in self.C.F["parameters"].items()}
        self.budget = Budget(cfg.budget_seconds)
        self.rows = {n: [] for n in ("omega", "omega_values", "cell_context", "frontier_context", "frontier_result",
                                      "capture_ceiling_result", "sup_witness", "lambda_pi_envelope", "confrontation_result",
                                      "inversion_result", "inversion_targets", "r1_summary", "r1_components", "r1_vertices",
                                      "r1_edges", "r1_rejected_crossings", "r2_sections", "r2_roots", "claims",
                                      "support_breakdown_result", "breakdown_witnesses", "external_requirement_sensitivity_result",
                                      "convergence_result", "computation_coverage", "witness_sets", "scalar_inversion_roots",
                                      "scalar_inversion_intervals", "numerical_evidence")}
        self.struct_cache: dict = _LRU(cfg.struct_cache_max)
        self.profiles: dict = _LRU(cfg.struct_cache_max)
        self.run_id = "BRUN-" + K.H({"d7": inp.d7.manifest["tree_sha256"], "config": inp.algorithm_config_sha256,
                                      "producer": inp.producer_sha256, "contract": inp.contract_sha256})[:24]
        self.omegas: dict = {}
        self.macros: dict = {}
        self.cells: dict = {}
        self.ceiling_ids: dict = {}
        self.incomplete_reasons: list = []

    # ------------------------------------------------------------------------------------ evidencia numérica
    def evidence(self, kind, definition, table, pk, box, err, unit, method, status="pass") -> str:
        # identificador por CONTENIDO completo: dos evidencias distintas (p. ej. misma definición con otra caja de
        # dominio, cota o estado) nunca comparten referencia; las idénticas se deduplican
        ref = "NEV:" + K.H({"k": kind, "t": table, "pk": pk, "d": definition, "box": box, "err": _dec(err) if err is not None else None,
                            "u": unit, "m": method, "s": status})[:40]
        if not any(r["evidence_ref"] == ref for r in self.rows["numerical_evidence"]):
            self.rows["numerical_evidence"].append({"evidence_ref": ref, "kind": kind, "definition": definition,
                                                    "result_table": table, "record_pk": pk if table else {},
                                                    "domain_box": box, "error_bound": err, "unit": unit,
                                                    "method_id": method, "status": status})
        return ref

    # ------------------------------------------------------------------------------------ omegas
    def omega_points(self, set_id: str, *, overrides: dict | None = None):
        """Producto de nudos estructurales (nivel pedido) x vértices macro (reducción demostrada) x fijos."""
        d7 = self.inp.d7
        overrides = overrides or {}
        axes = {}
        for pid in STRUCT:
            s = d7.support(set_id, pid)
            if pid in overrides:
                axes[pid] = overrides[pid]
            else:
                axes[pid] = level_nodes(d7.nodes(set_id, pid), s["scale"], self.cfg.level)
                if self.unit is not None and not overrides and set_id == self.unit["set_id"] and pid in self.unit["prefix"]:
                    axes[pid] = [axes[pid][self.unit["prefix"][pid]]]
        for pid in ("eta_w", "gain_share", "pi_iva", "pi_otros_productos", "pi_produccion"):
            if pid in overrides:
                axes[pid] = overrides[pid]
            else:
                lo, hi = d7.interval(set_id, pid)
                axes[pid] = [lo] if lo == hi else [lo, hi]
        axes["eta_H"] = overrides.get("eta_H", d7.nodes(set_id, "eta_H"))
        for pid in FIXED + BARS:
            axes[pid] = d7.nodes(set_id, pid)
        names = sorted(axes)
        for combo in product(*[axes[n] for n in names]):
            yield dict(zip(names, combo))

    def omega_row(self, set_id: str, values: dict) -> tuple[str, dict, bool, str | None]:
        common = K.common_values(values, self.C.K, self.units)
        self.C.key("common_values", common)
        ident = K.omega_identity(set_id, self.inp.d7.layer_scenario(set_id), common)
        oid = K.omega_id(ident)
        reason = None
        try:
            derived = self.model.derive({**values, "t": values["t"], "c_legal": values["c_legal"]})
        except M.DomainError as e:
            derived, reason = None, str(e).split(":")[0]
        if derived is not None:
            if values["c_legal"] != 1:
                reason = "C_LEGAL_EXTENSION_INACTIVE"
            elif values["t"] != 0:
                reason = "T_EXTENSION_INACTIVE"
        return oid, common, reason is None, reason, derived, ident

    def build_omegas(self):
        for set_id in self.evaluated_sets():
            for values in self.omega_points(set_id):
                oid, common, ok, reason, derived, ident = self.omega_row(set_id, values)
                if oid in self.omegas:
                    continue
                self.omegas[oid] = {"set": set_id, "values": values, "admissible": ok, "derived": derived,
                                    "common_sha": K.H(common), "block": self.block_of(values["eta_w"])}
                self.rows["omega"].append({"omega_id": oid, "support_set_id": set_id,
                                           "scenario_id": self.inp.d7.layer_scenario(set_id),
                                           "primitive_values_sha256": ident["primitive_values_sha256"],
                                           "domain_status": "admissible" if ok else "excluded", "reason_code": reason})
                for pid in sorted(values):
                    self.rows["omega_values"].append({"omega_id": oid, "parameter_id": pid, "value": _dec(values[pid]),
                                                      "value_unit": self.units[pid], "binding_id": f"BND:{set_id}:{pid}:global",
                                                      "formula_id": None, "reason_code": None})
                for pid in COMMON_DERIVED:
                    self.rows["omega_values"].append({"omega_id": oid, "parameter_id": pid,
                                                      "value": _dec(derived[pid]) if derived else None,
                                                      "value_unit": self.units[pid], "binding_id": f"BND:{set_id}:{pid}:global",
                                                      "formula_id": DERIVED_FORMULA[pid],
                                                      "reason_code": None if derived else (reason or "DERIVED_UNDEFINED")})

    def block_of(self, eta_w) -> str:
        v = Decimal(str(eta_w))
        if Decimal("0.05") <= v <= Decimal("0.2"):
            return "micro"
        if Decimal("0.4") <= v <= Decimal("1"):
            return "macro"
        return "micro" if v < Decimal("0.3") else "macro"

    def evaluated_sets(self) -> list:
        if self.unit is not None:
            return [self.unit["set_id"]]
        out = []
        for base in self.cfg.base_sets:
            out.append(base)
            out += [f"{base}.{s}" for s in self.cfg.derived_suffixes]
        return out

    # ------------------------------------------------------------------------------------ estructura y techo
    def structural(self, values: dict, design: str, instrument: str) -> tuple[str, dict]:
        payload = K.structural(values, self.C.K, self.units, design, instrument, values["bar_tau_d"], values["bar_tau_f"],
                               self.inp.theory[2], self.inp.technical)
        return self.C.key("structural", payload), payload

    def ceiling(self, values: dict, design: str, instrument: str, *, phi_override=None, kappa_override=None):
        v = dict(values)
        if phi_override is not None:
            v["phi"] = phi_override
        if kappa_override is not None:
            v["kappa_tilde"] = kappa_override
        skey, payload = self.structural(v, design, instrument)
        hit = self.struct_cache.get(skey)
        if hit is None and self.techos_compartidos is not None:
            hit = self.techos_compartidos.get(self.compat_techo(skey))
            if hit is not None:
                self.struct_cache[skey] = hit
        if hit is None:
            state = self.model.state(_to_state_prim(v))
            bd, bf = float(v["bar_tau_d"]), float(v["bar_tau_f"])
            ceil = self.model.capture_ceiling(state, design, instrument, bd, bf, True, self.cfg.sup)
            hit = {"state": state, "ceiling": ceil, "payload": payload, "bars": (bd, bf), "frontier": None, "cs_cache": {}}
            self.struct_cache[skey] = hit
            if self.techos_compartidos is not None:
                self.techos_compartidos[self.compat_techo(skey)] = hit
        return skey, hit

    def compat_techo(self, skey: str) -> str:
        """CANDIDATO E11: clave de compatibilidad de un techo para reutilizarlo entre Run del MISMO proceso."""
        m = self.model
        return K.H({"skey": skey, "run_id": self.run_id, "sup": self.cfg.sup.as_dict(), "modelo": getattr(m, "kind", None),
                    "garantia": getattr(m, "garantia", None), "certificado": bool(getattr(m, "certified", False)),
                    "cajas": getattr(m, "sup_max_boxes", None), "saltos": getattr(m, "jump_budget", None)})

    def cs_function(self, hit, design):
        s = hit["state"]
        cache = hit["cs_cache"]
        B = s.B_pot

        def cs(td, tf):
            k = (td, tf)
            v = cache.get(k)
            if v is None:
                ev = self.model.evaluate(s, td, tf, design)
                v = (ev.R / B, ev.topology)
                cache[k] = v
            return v
        return cs

    # ------------------------------------------------------------------------------------ ejecución completa
    def execute(self) -> dict:
        tracemalloc.start()
        t0 = time.time()
        self.phase_seconds = {}
        for name, step in (("omegas", self.build_omegas), ("frontiers", self.build_frontiers), ("macro", self.build_macro),
                           ("cells", self.build_cells), ("claims", self.build_claims)):
            t1 = time.time()
            step()
            self.phase_seconds[name] = round(time.time() - t1, 3)
        self.build_coverage(time.time() - t0)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.peak = peak
        return self.rows

    def execute_unit(self) -> dict:
        """Modo unidad: omegas, fronteras, macro y celdas SOLO del prefijo de nudos de la unidad + cobertura de nudos.
        Afirmaciones, robustez y sensibilidad de Q no se calculan aquí: la unidad aporta su resumen (unit_summary)."""
        assert self.unit is not None
        t0 = time.time()
        self.phase_seconds = {}
        for name, step in (("omegas", self.build_omegas), ("frontiers", self.build_frontiers), ("macro", self.build_macro),
                           ("cells", self.build_cells)):
            t1 = time.time()
            step()
            self.phase_seconds[name] = round(time.time() - t1, 3)
        self.build_coverage(time.time() - t0)
        return self.rows

    def unit_summary(self) -> dict:
        """Resumen acotado de la unidad para el cierre global (tamaño independiente del número de celdas)."""
        lam = {}
        for (oid, country), ms in self.macros.items():
            key = self.omegas[oid]["set"] + "|" + country
            for m in ms:
                if m["row"]["admissible"] and m["row"]["lambda_pi"] is not None:
                    lo, hi = lam.get(key, (math.inf, -math.inf))
                    lam[key] = (min(lo, m["row"]["lambda_pi"]), max(hi, m["row"]["lambda_pi"]))
        c2s = [r["C_2"] for r in self.ceiling_ids.values() if r["C_2"] is not None]
        cls = CL.derive(self.inp.registry, self.inp.model_case_map, self.claim_sets())
        claims = {}
        sid = self.unit["set_id"]
        for cl in cls:
            if not set(cl.support_sets) <= set(self.cfg.base_sets) or sid not in cl.support_sets:
                continue
            pts, complete = self.universe_raw(cl)
            tally = self.certify_claim_region(cl, sid, self.struct_axes(sid), prefix=self.unit["prefix"])
            q = {}
            for scope, sc in self.q_scopes(cl):
                best, wit, bad, n = -math.inf, None, False, 0
                for u in self.q_universe(cl, sc):
                    n += 1
                    qmin = min(u["Qs"])
                    if not qmin > 0:
                        bad = True
                        continue
                    m = ((u["C2"] + u["err"] + CL.EPS_ECON) * u["lambda"] * u["gain"] - u["D"]) / qmin
                    if m > best or (m == best and wit is not None and tuple(u["key"]) < tuple(wit["key"])):
                        best, wit = m, {"gain": u["gain"], "key": list(u["key"])}
                q[f"{scope}|{sc or ''}"] = {"best": best if wit is not None else None, "wit": wit, "bad": bad, "n": n}
            claims[cl.claim_id] = {"n": len(pts), "sup": max((g + e for g, e in pts), default=None),
                                   "inf": min((g - e for g, e in pts), default=None), "any_none": any(g is None for g, _ in pts),
                                   "complete": complete, "tally": tally.as_dict(), "q": q}
        return {"unit_id": self.unit["unit_id"], "set_id": sid, "lambda": {k: list(v) for k, v in sorted(lam.items())},
                "c2": [min(c2s), max(c2s)] if c2s else None, "claims": claims,
                "incomplete_reasons": list(self.incomplete_reasons), "n_cells": len(self.cells), "n_omega": len(self.omegas)}

    # frontier_context / capture_ceiling_result / frontier_result / sup_witness
    def frontier_cases(self, country: str):
        out = []
        for r in self.inp.model_case_map:
            if r["country_id"] != country:
                continue
            j = r["model_menu"].removeprefix("j_")
            available = r["case_id"] in ("domestic_unchanged", "conditional_full")
            out.append((j, r["case_id"], available, r))
        return sorted(out, key=lambda x: (x[0], x[1]))

    def build_frontiers(self):
        self.frontiers = {}
        for oid, om in sorted(self.omegas.items()):
            if not om["admissible"]:
                continue
            for country in self.inp.d7.countries(om["set"]):
                for design in self.cfg.designs:
                    for j, case, available, d4row in self.frontier_cases(country):
                        if self.budget.exhausted():
                            self.incomplete_reasons.append("RESOURCE_BUDGET_EXHAUSTED")
                            return
                        tau_id = f"TAU:{om['set']}:{j}"
                        fid = "FRN:" + K.H({"r": self.run_id, "d": design, "c": country, "j": j, "a": case, "o": oid, "t": tau_id})[:40]
                        skey, hit = self.ceiling(om["values"], design, j) if available else self.structural_only(om["values"], design, j)
                        self.rows["frontier_context"].append({
                            "frontier_id": fid, "run_id": self.run_id, "design_v": design, "country_id": country, "instrument_j": j,
                            "availability_case_id": case, "availability_matrix_hash": self.inp.availability_matrix_hash,
                            "omega_id": oid, "structural_key_sha256": skey, "tau_domain_id": tau_id,
                            "structural_key_payload": hit["payload"]})
                        self.frontiers[(oid, country, design, j, case)] = {"frontier_id": fid, "skey": skey, "hit": hit,
                                                                           "available": available, "d4": d4row}
                        self.ceiling_rows(fid, hit, available, d4row, om)
                        if available:
                            self.frontier_rows(fid, hit, design, j)
        self.monotonicity()

    def monotonicity(self):
        """C2^d <= C2^df y C2^f <= C2^df (dominio df contiene los de d y f; CS no depende del menú). Solo disponibles."""
        groups = {}
        for (oid, country, design, j, case), fr in self.frontiers.items():
            row = self.ceiling_ids[fr["frontier_id"]]
            if fr["available"] and row["computation_status"] == "complete":
                groups.setdefault((oid, country, design), {})[j] = row
        for byj in groups.values():
            df = byj.get("df")
            if df is None:
                continue
            oks = []
            for j in ("d", "f"):
                r = byj.get(j)
                if r is None:
                    continue
                ok = r["C_2"] <= df["C_2"] + (r["numerical_error"] or 0.0) + (df["numerical_error"] or 0.0)
                r["monotonicity_check"] = "pass" if ok else "fail"
                oks.append(ok)
            if oks:
                df["monotonicity_check"] = "pass" if all(oks) else "fail"

    def structural_only(self, values, design, j):
        skey, payload = self.structural(values, design, j)
        return skey, {"payload": payload, "ceiling": None, "state": None}

    def ceiling_rows(self, fid, hit, available, d4row, om):
        cid = "CEI:" + fid[4:]
        base = {"ceiling_id": cid, "frontier_id": fid, "instrument_available": available,
                "availability_status": d4row["national_availability_status"], "availability_source": d4row["quantitative_use"],
                "availability_assumed": d4row["availability_assumed"] == "true",
                "coordination_scenario_id": self.inp.d7.scenarios[self.inp.d7.layer_scenario(om["set"])]["coordination_scenario_id"]}
        if not available:
            row = dict(base, C_2=None, tau_d_at_sup=None, tau_f_at_sup=None, sup_not_attained=None,
                       sup_lateral_low=None, sup_lateral_high=None, monotonicity_check="not_applicable",
                       numerical_error=None, computation_status="not_applicable", reason_code="INSTRUMENT_NOT_AVAILABLE")
            self.rows["capture_ceiling_result"].append(row)
            self.ceiling_ids[fid] = row
            return
        ce = hit["ceiling"]
        res = ce.sup
        row = dict(base, C_2=ce.C2, numerical_error=ce.numerical_error, computation_status=ce.status,
                   reason_code=ce.reason, monotonicity_check="not_applicable")
        if res.attained:
            row.update(tau_d_at_sup=res.tau_d, tau_f_at_sup=res.tau_f, sup_not_attained=False, sup_lateral_low=None,
                       sup_lateral_high=None)
        else:
            B = hit["state"].B_pot
            row.update(tau_d_at_sup=None, tau_f_at_sup=None, sup_not_attained=True,
                       sup_lateral_low=None if res.lateral_low is None else res.lateral_low / B,
                       sup_lateral_high=None if res.lateral_high is None else res.lateral_high / B)
            for w in res.witnesses:
                self.rows["sup_witness"].append({"ceiling_id": cid, "sequence_index": w.sequence_index, "side": w.side,
                                                 "tau_d": w.tau_d, "tau_f": w.tau_f, "limit_value": w.limit_value / B,
                                                 "residual": abs(w.limit_value - w.value) / B, "approach_distance": w.approach_distance,
                                                 "branch_id": w.branch_id})
            self.evidence("limit", "supremo no alcanzado: límite lateral por Richardson en la curva de salto S13 (rho=1); "
                          "el valor en la curva usa la regla de no adopción", "capture_ceiling_result", {"ceiling_id": cid},
                          {}, ce.numerical_error, "share", "supremum_multilevel_lateral")
        certified = getattr(res, "error_kind", "convergence_estimate") == "certified_bound"
        hit["certified"] = certified
        if certified:
            ev = self.evidence("convergence", "C_2 por rama y cota con encierros demostrativos del proveedor %s (base de las "
                               "cotas: %s): |sup - C_2| <= numerical_error, COTA certificada (el supremo está entre las "
                               "cotas inferior y superior demostradas)" % (self.model.kind,
                                                                             getattr(self.model, "garantia", None) or "exacta"),
                               "capture_ceiling_result", {"ceiling_id": cid}, {}, ce.numerical_error, "share",
                               "certified_branch_and_bound", "pass" if ce.status == "complete" else "fail")
            self.rows["convergence_result"].append({
                "quantity_id": f"C2:{cid}", "level_before": 0, "level_after": 1,
                "result_ref": "capture_ceiling_result:" + json.dumps({"ceiling_id": cid}, sort_keys=True, separators=(",", ":")),
                "method_id": "certified_branch_and_bound", "value_before": ce.C2, "value_after": res.upper / hit["state"].B_pot,
                "change_bound": ce.numerical_error, "tolerance": self.cfg.sup.tol_converge, "unit": "share", "topology_before": None,
                "topology_after": None, "verdict_changes": 0, "coverage_complete": ce.status == "complete",
                "status": "pass" if ce.status == "complete" and ce.numerical_error <= self.cfg.sup.tol_converge else "fail",
                "evidence_ref": ev})
            self.rows["capture_ceiling_result"].append(row)
            self.ceiling_ids[fid] = row
            return
        self.evidence("convergence", "C_2 con error ESTIMADO (cambio entre niveles de malla con pulido y laterales): no es una "
                      "cota certificada. El veredicto usa margen max(estimación, T2 validado=%s) medido en familias con "
                      "solución conocida (DI-08); sin cota demostrada no se certifica inexistencia de R1/R2" % self.t2,
                      "capture_ceiling_result", {"ceiling_id": cid}, {}, ce.numerical_error, "share", "supremum_multilevel",
                      "limitation")
        levels = res.level_values
        for k in range(1, len(levels)):
            before, after = levels[k - 1] / hit["state"].B_pot, levels[k] / hit["state"].B_pot
            ev = self.evidence("convergence", f"C_2 por niveles de malla anidada {k-1}->{k} con pulido local: ESTIMACIÓN de "
                               "convergencia (cambio entre niveles), no cota certificada", "capture_ceiling_result",
                               {"ceiling_id": cid}, {}, abs(after - before), "share", "supremum_multilevel",
                               "pass" if abs(after - before) <= self.cfg.sup.tol_converge else "fail")
            self.rows["convergence_result"].append({
                "quantity_id": f"C2:{cid}", "level_before": k - 1, "level_after": k,
                "result_ref": "capture_ceiling_result:" + json.dumps({"ceiling_id": cid}, sort_keys=True, separators=(",", ":")),
                "method_id": "supremum_multilevel", "value_before": before, "value_after": after, "change_bound": abs(after - before),
                "tolerance": self.cfg.sup.tol_converge, "unit": "share", "topology_before": None, "topology_after": None,
                "verdict_changes": 0, "coverage_complete": True,
                "status": "pass" if abs(after - before) <= self.cfg.sup.tol_converge else "fail", "evidence_ref": ev})
        self.rows["capture_ceiling_result"].append(row)
        self.ceiling_ids[fid] = row

    def frontier_rows(self, fid, hit, design, j):
        if hit["frontier"] is None:
            bd, bf = hit["bars"]
            hit["frontier"] = self.model.frontier_grid(hit["state"], design, j, bd, bf, self.cfg.frontier_n)
            topos = {}
            for r in hit["frontier"]:
                topos[r.topology] = topos.get(r.topology, 0) + 1
            hit["regime_evidence"] = topos
        for r in hit["frontier"]:
            self.rows["frontier_result"].append({
                "frontier_id": fid, "point_id": r.point_id, "side": r.side, "tau_d": r.tau_d, "tau_f": r.tau_f,
                "B_d": r.B_d, "B_f": r.B_f, "B_f_grav": r.B_f, "R": r.R, "B_pot": r.B_pot,
                "CS": None if r.R is None else r.R / r.B_pot, "eps_dd": r.eps.get("eps_dd"), "eps_df": r.eps.get("eps_df"),
                "eps_fd": r.eps.get("eps_fd"), "eps_ff": r.eps.get("eps_ff"), "s_P": r.s_P, "regime": r.regime,
                "kink_adjacent": r.kink_adjacent, "audit_status": r.audit_status, "computation_status": r.computation_status,
                "reason_code": r.reason_code})
        self.evidence("regime", "topologías de adopción en la malla de frontera: " + json.dumps(hit["regime_evidence"], sort_keys=True),
                      "frontier_context", {"frontier_id": fid}, {}, None, "none", "exact_root_partition")

    # ------------------------------------------------------------------------------------ lambda / pi
    def build_macro(self):
        for oid, om in sorted(self.omegas.items()):
            if not om["admissible"]:
                continue
            for country in self.inp.d7.countries(om["set"]):
                for st in self.states_for(om, country):
                    if st.channel == "strict":
                        self.macro_row(oid, om, country, st, None)
                        continue
                    # macro-ca2-v2: el case_id del bundle incluye el contexto de celda (diseño-menú-caso D4)
                    for design in self.cfg.designs:
                        for j, case, _, _ in self.frontier_cases(country):
                            self.macro_row(oid, om, country, st, (design, j, case))

    def states_for(self, om, country):
        out = []
        for st in self.inp.national(om["set"], country):
            if isinstance(st, dict) and st.get("kind") == "strict_domain":
                verts = MC.strict_vertices(st["domains"], st["terms"], st["denominator"], om["values"])
                for label, (prim, shares) in sorted(verts.items()):
                    out.append(MC.NationalState(country, st["preregistration_id"], "strict", st["edition"], st["anchor_year"], label,
                                                tuple((p, MC.F(v), st["unit"]) for p, v in sorted(prim.items())),
                                                tuple((k, shares[k]) for k in MC.SHARE_KEYS), st["joint_domain_sha256"],
                                                tuple(st["dependencies"])))
            else:
                out.append(st)
        return out

    def macro_row(self, oid, om, country, st: MC.NationalState, context=None):
        v = om["values"]
        m = MC.bridge(st.share_dict(), v)
        block = om["block"]
        prim_rows = [{"parameter_id": p.replace("!", "_").replace(":", "_"), "value": canon_dec(float(x)) if not _finite_dec(x) else canon_dec(x),
                      "value_unit": u} for p, x, u in st.primitive_values]
        national = K.national_state(sorted(prim_rows, key=lambda r: r["parameter_id"]),
                                    {k: float(x) for k, x in st.shares}, st.joint_domain_sha256)
        nsha = K.H(national)
        if st.channel == "strict":
            payload = K.macro_strict(country, block, v, self.C.K, self.units, national, list(st.dependencies),
                                     self.inp.protocol[2], self.inp.technical)
            msha = self.C.key("macro", payload)
        else:
            payload, msha = self.inp.conditional_key(st, om, block, context)
        mid = "MAC:" + K.H({"r": self.run_id, "c": country, "o": oid, "b": block, "m": msha})[:40]
        admissible = m.admissible and v["eta_H"] > -1
        lam = float(m.lambda_pi) if m.lambda_pi is not None else None
        row = {"macro_id": mid, "run_id": self.run_id, "country_id": country, "omega_id": oid,
               "s_L_bar": float(dict(st.shares)["s_L_bar"]), "eta_w": _dec(v["eta_w"]), "eta_H": _dec(v["eta_H"]),
               "theta_W": float(m.theta_W), "s_T_marg": float(m.s_T_marg), "q_pot": float(m.q_pot), "lambda_pi": lam,
               "admissible": admissible, "eta_w_block": block, "theta_W_negative": m.theta_W_negative,
               "computation_status": "complete" if admissible else "excluded",
               "reason_code": None if admissible else (m.reasons[0] if m.reasons else "INADMISSIBLE"),
               "macro_key_sha256": msha, "macro_key_payload": payload, "national_state_sha256": nsha}
        self.rows["lambda_pi_envelope"].append(row)
        self.macros.setdefault((oid, country), []).append({"row": row, "state": st, "m": m, "context": context})

    # ------------------------------------------------------------------------------------ celdas
    def build_cells(self):
        grid = [c for c in self.inp.grid_cells]
        for (oid, country, design, j, case), fr in sorted(self.frontiers.items(), key=lambda kv: kv[1]["frontier_id"]):
            om = self.omegas[oid]
            cells_c = [c for c in grid if c.country_id == country]
            for mac in self.macros.get((oid, country), []):
                if mac["context"] not in (None, (design, j, case)):
                    continue
                for cell in cells_c:
                    for bound in X.BOUNDS:
                        if self.budget.exhausted():
                            self.incomplete_reasons.append("RESOURCE_BUDGET_EXHAUSTED")
                            return
                        self.cell(om, oid, country, design, j, case, fr, mac, cell, bound)

    def cell(self, om, oid, country, design, j, case, fr, mac, gcell, bound):
        v = om["values"]
        row = mac["row"]
        uk = {"run_id": self.run_id, "design_v": design, "country_id": country, "instrument_j": j, "availability_case_id": case,
              "omega_id": oid, "eta_w_block": row["eta_w_block"], "policy_variant_id": gcell.policy_variant_id,
              "regime_id": gcell.regime_id, "requirement_basis": gcell.requirement_basis, "xi": gcell.xi, "layer": gcell.layer,
              "bound_variant": bound, "external_cell_id": gcell.external_cell_id,
              "national_state_sha256": row["national_state_sha256"], "expected_macro_key_sha256": row["macro_key_sha256"]}
        cid = "CEL:" + K.H(uk)[:44]
        d4 = fr["d4"]
        coord = self.inp.d7.scenarios[self.inp.d7.layer_scenario(om["set"])]["coordination_scenario_id"]
        ctx = dict(uk, cell_id=cid, availability_matrix_hash=self.inp.availability_matrix_hash,
                   availability_assumed=d4["availability_assumed"] == "true",
                   availability_status=d4["national_availability_status"], availability_source=d4["quantitative_use"],
                   instrument_available=fr["available"], coordination_scenario_id=coord, xi=_dec(gcell.xi))
        self.rows["cell_context"].append(ctx)
        ceiling = self.ceiling_ids[fr["frontier_id"]]
        C2 = ceiling["C_2"]
        certified = bool(fr["hit"].get("certified")) if fr.get("hit") else False
        est = ceiling["numerical_error"] or 0.0
        # margen respaldado: cota certificada, o máx(estimación, T2 validado) si el error solo es una estimación
        err = est if certified else max(est, self.t2)
        Q = gcell.Q(bound)
        lam = row["lambda_pi"]
        y = float(v["gain_share"])
        K1 = X.K1(Q, self.inp.dme_gai, lam, y) if (row["admissible"] and lam is not None) else None
        status, reason, verdict, G = "complete", None, "no_verdict", None
        if not fr["available"]:
            status, reason = "not_applicable", "INSTRUMENT_NOT_AVAILABLE"
        elif not row["admissible"]:
            status, reason = "excluded", row["reason_code"]
        elif ceiling["computation_status"] != "complete":
            status, reason = "incomplete", ceiling["reason_code"] or "CEILING_INCOMPLETE"
        else:
            G = C2 - K1
            if G - err >= CL.EPS_ECON:
                verdict = "factible"
            elif G + err <= -CL.EPS_ECON:
                verdict = "infactible"
            else:
                verdict = "inconcluso"
        self.rows["confrontation_result"].append({
            "cell_id": cid, "ceiling_id": ceiling["ceiling_id"], "macro_id": row["macro_id"],
            "sup_not_attained": ceiling["sup_not_attained"], "C_2": C2 if status == "complete" else None,
            "K_comp_1": K1 if status == "complete" else None, "G": G, "verdict": verdict if status == "complete" else "no_verdict",
            "run_readiness_flag": False, "computation_status": status, "reason_code": reason})
        from . import convergencia as CV
        fg = CV.fila_G(cid, C2=C2 if status == "complete" else None, err_C2=est, K1=K1 if status == "complete" else None,
                       error_kind="certified_bound" if certified else "convergence_estimate",
                       ceiling_status=ceiling["computation_status"], evidence_ref=None)
        fg["evidence_ref"] = self.evidence("convergence", "G = C2 - K1 en el mismo omega: cota = error certificado de C2 + "
                                           "redondeo de K1 (T1); %s" % (fg.get("motivo") or "ok"), "confrontation_result",
                                           {"cell_id": cid}, {}, fg["change_bound"], "share", fg["method_id"],
                                           "pass" if fg["status"] == "pass" else "limitation")
        self.rows["convergence_result"].append({k: fg[k] for k in CV.COLUMNAS})
        self.cells[cid] = {"ctx": ctx, "C2": C2, "err": err, "certified": certified, "K1": K1, "G": G, "status": status,
                           "om": om, "fr": fr,
                           "mac": mac, "Q": Q, "lam": lam, "y": y, "gcell": gcell, "bound": bound}
        self.inversions(cid)
        if self.cfg.run_geometry:
            self.geometry(cid)

    # ------------------------------------------------------------------------------------ inversiones
    def inversions(self, cid):
        c = self.cells[cid]
        N = c["Q"] + self.inp.dme_gai
        C2 = c["C2"] if c["status"] == "complete" else None
        lam = c["lam"] if c["status"] == "complete" else None
        y = c["y"] if c["status"] == "complete" else None
        K1 = c["K1"] if c["status"] == "complete" else None
        supports = {"lambda": self.lambda_range(c), "gain_share": tuple(float(x) for x in self.inp.d7.interval(c["om"]["set"], "gain_share")),
                    "C2": self.c2_range(c)}
        invs = INV.algebraic(N, C2, lam, y, K1, supports)
        tgt = self.inp.supplier_targets.get(c["om"]["set"])
        invs.append(INV.phi_partial(tgt[0] if tgt else None, tgt[1] if tgt else None) if C2 is not None
                    else INV.Inversion("phi_partial", result_status="undefined_denominator", reason="C2_UNDEFINED"))
        if C2 is None:
            invs.append(INV.Inversion("external_factor", result_status="undefined_denominator", reason="C2_UNDEFINED",
                                      method_id="fixed_point_bracket_bisection"))
            invs.append(INV.Inversion("phi_total", result_status="undefined_denominator", reason="C2_UNDEFINED",
                                      method_id="fixed_point_bracket_bisection"))
        else:
            invs.append(self.external_factor(c, K1))
            invs.append(self.phi_total(c, K1))
        for inv in invs:
            self.inversion_rows(cid, inv)
            if self.unit is not None and inv.inversion_id in ("lambda_required", "capture_required") and \
                    inv.result_status in ("computed", "outside_support"):
                # soporte GLOBAL (todas las unidades): el estado computed/outside_support se cierra al ensamblar
                self.rows["inversion_result"][-1]["_fin"] = {
                    "k": "lambda" if inv.inversion_id == "lambda_required" else "C2", "set": c["om"]["set"],
                    "country": c["ctx"]["country_id"], "value": inv.value, "c2_defined": C2 is not None}

    def lambda_range(self, c):
        vals = [m["row"]["lambda_pi"] for (o, cc), ms in self.macros.items() if cc == c["ctx"]["country_id"]
                and self.omegas[o]["set"] == c["om"]["set"] for m in ms if m["row"]["admissible"]]
        return (min(vals), max(vals)) if vals else (math.inf, -math.inf)

    def c2_range(self, c):
        vals = [r["C_2"] for r in self.ceiling_ids.values() if r["C_2"] is not None]
        return (min(vals), max(vals)) if vals else (math.inf, -math.inf)

    def phi_total(self, c, K1):
        if not self.cfg.run_endogenous:
            return INV.Inversion("phi_total", result_status="incomplete", reason="ENDOGENOUS_NOT_RUN",
                                 method_id="fixed_point_bracket_bisection")
        design, j = c["ctx"]["design_v"], c["ctx"]["instrument_j"]
        v = c["om"]["values"]
        if j == "d":
            return INV.endogenous("phi_total", None, K1, 0.0, 1.0, invariance_proof="MENU_D_TAU_F_ZERO_PHI_ABSENT",
                                  constant_value=c["C2"])
        key = ("phi", self.structural(v, design, j)[0])
        prof = self.profiles.get(key)
        if prof is None:
            def C2_of(phi):
                _, hit = self.ceiling(v, design, j, phi_override=Decimal(repr(phi)))
                ce = hit["ceiling"]
                return ce.C2 if ce.status == "complete" else None
            prof = self.profiles[key] = INV.Profile(C2_of, 0.0, 1.0, self.cfg.phi_n, xtol=self.cfg.endogenous_xtol)
        # evidencia NUEVA por inversión: su reloj de presupuesto (inversion_budget_seconds) empieza con ESTA búsqueda de
        # raíces. Las evaluaciones en flotante del perfil se comparten entre inversiones de la misma clave estructural.
        bd, bf = float(v["bar_tau_d"]), float(v["bar_tau_f"])
        # INTEGRACIÓN 3.7 (paso 12): un único plazo MONOTÓNICO para toda la inversión (ruta fiscal + búsqueda), creado
        # antes de ambas; la evidencia del modelo teórico lo respeta en cada encierro y no lo reinicia al cambiar de ruta
        from . import cota_fiscal as CF
        from .modelos import ModeloTeorico as _MTp
        plazo = CF.Plazo.desde(self.inversion_budget_s)
        if isinstance(self.model, _MTp):
            ev = self.model.c2_param_evidence(_to_state_prim(v), design, j, "phi", bd, bf, limite=plazo.limite)
        else:
            ev = self.model.c2_param_evidence(_to_state_prim(v), design, j, "phi", bd, bf)
        one = INV.Profile(prof._f, prof.lo, prof.hi, prof.n, xtol=prof.xtol, evidence=ev)
        one.points = prof.points
        fis = self.phi_fiscal(v, design, j, bd, bf, K1, plazo)
        if fis is not None:
            return fis
        res = INV.endogenous_profile("phi_total", one, K1, xtol=self.cfg.endogenous_xtol, tol_residual=self.tol_root)
        res.budget_s = self.inversion_budget_s if ev is not None else None     # presupuesto consumido por ESTA inversión
        return res

    def phi_fiscal(self, v, design, j, bd, bf, K1, plazo=None):
        """INTEGRACIÓN 3.7 (complemento): partición de [0, 1] por cota inferior con puntos fiscales. Solo decide si
        certifica C2 > K1 en TODO [0, 1] (inexistencia de raíz demostrada); en otro caso devuelve None y la búsqueda
        existente se ejecuta sin cambios. No afirma nunca C2 < K1."""
        import dataclasses as _dc
        from . import cota_fiscal as CF
        from .modelos import ModeloTeorico as _MT
        # la cota usa el MOTOR de intervalos del modelo teórico (eng.R con φ como argumento); otros proveedores
        # (p. ej. sustitutos sintéticos) siguen solo la búsqueda existente
        if K1 is None or j not in ("f", "df") or not isinstance(self.model, _MT) or not getattr(self.model, "certified", False):
            return None
        st = M.state_from_primitives(dict(_to_state_prim(v), phi=0.5))
        eng = self.model.engine(st, design)
        Bi = eng.P.B_pot

        def Ri(x, y, a, b):
            X, Y, P = Iv(x, x), Iv(y, y), Iv(a, b)
            e1, _ = eng.R(X, Y, P)
            e2, _ = eng.R_box_g(X, Y, P)
            return Iv(max(e1.lo, e2.lo), min(e1.hi, e2.hi))

        def Rf(x, y, p):
            return self.model.evaluate(_dc.replace(st, phi=p), x, y, design).R
        dec, pend, cort = CF.particion(Ri, Rf, Bi, sup_axes(j, bd, bf), K1, k_min=12, plazo=(plazo.reserva(CF.FRACCION_RUTA_FISCAL, self.cfg.phi_fiscal_budget_s) if plazo is not None else CF.Plazo.desde(self.cfg.phi_fiscal_budget_s)), parar_bajo=1e-3)
        if not (CF.cubre(dec) and not pend and not cort):
            return None
        inv = INV.Inversion("phi_total", method_id="fixed_point_bracket_bisection",
                            definition="C2(phi) = K1 en [0, 1]: C2 > K1 certificado en todo [0, 1] por cota inferior con puntos fiscales")
        inv.result_status, inv.no_solution, inv.coverage = "no_feasible_solution", True, "certified"
        inv.reason, inv.fixed_point_converged = "NO_ROOT_CERTIFIED_FISCAL_LOWER_BOUND", True
        inv.diagnostics = {"tramos": len(dec), "cota_minima": min(c for _, _, c, _ in dec)}
        return inv

    def external_factor(self, c, K1):
        mapping = self.inp.external_factor_mapping
        if mapping is None:
            return INV.not_identified("external_factor", "EXTERNAL_FACTOR_NOT_IDENTIFIED")
        if not self.cfg.run_endogenous:
            return INV.Inversion("external_factor", result_status="incomplete", reason="ENDOGENOUS_NOT_RUN",
                                 method_id="fixed_point_bracket_bisection")
        design, j = c["ctx"]["design_v"], c["ctx"]["instrument_j"]
        v = c["om"]["values"]

        key = ("ext", self.structural(v, design, j)[0])
        prof = self.profiles.get(key)
        if prof is None:
            def C2_of(f):
                kt = mapping(v, f)
                _, hit = self.ceiling(v, design, j, kappa_override=Decimal(repr(kt)))
                ce = hit["ceiling"]
                return ce.C2 if ce.status == "complete" else None
            prof = self.profiles[key] = INV.Profile(C2_of, 1e-6, 1.0, self.cfg.phi_n, xtol=self.cfg.endogenous_xtol)
        return INV.endogenous_profile("external_factor", prof, K1, xtol=self.cfg.endogenous_xtol, tol_residual=self.tol_root)

    def inversion_rows(self, cid, inv: INV.Inversion):
        algebraic = inv.method_id == "algebraic_closed_form"
        endo_complete = (not algebraic) and inv.computation_status == "complete"
        row = {"cell_id": cid, "inversion_id": inv.inversion_id, "lambda_pi_required": None, "delta_y_required": None,
               "C_2_required": None, "external_factor_required": None, "fixed_point_converged": None,
               "phi_critical_partial": None, "phi_critical_total": None, "outside_support": inv.outside_support,
               "no_solution": inv.no_solution, "corner_binding": inv.corner_binding, "kink_adjacent": inv.kink_adjacent,
               "admissibility_violated": inv.admissibility_violated, "target_value": inv.target_value, "target_unit": inv.target_unit,
               "equation_id": INV.EQUATION[inv.inversion_id], "method_id": inv.method_id, "result_status": inv.result_status,
               "computation_status": inv.computation_status, "reason_code": inv.reason,
               "n_scalar_solutions": len(inv.roots) if endo_complete else None,
               "n_scalar_intervals": len(inv.intervals) if endo_complete else None}
        if not algebraic:
            row["fixed_point_converged"] = inv.fixed_point_converged
        vf = INV.VALUE_FIELD[inv.inversion_id]
        if algebraic or (endo_complete and len(inv.roots) == 1 and not inv.intervals):
            row[vf] = inv.value
        if row[vf] is not None and vf in ("external_factor_required", "phi_critical_total") and not (0 <= row[vf] <= 1):
            row[vf] = None
        self.rows["inversion_result"].append(row)
        if not algebraic and inv.result_status not in ("not_identified", "undefined_denominator"):
            from . import convergencia as CV
            fr_ = CV.fila_raices("INV:%s:%s" % (cid, inv.inversion_id),
                                 CV.ref("inversion_result", {"cell_id": cid, "inversion_id": inv.inversion_id}),
                                 raices=inv.roots, intervalos=inv.intervals, coverage=inv.coverage,
                                 computation_status=inv.computation_status, no_solution=inv.no_solution, dominio=(0.0, 1.0),
                                 dominio_cubierto=(0.0, 1.0) if inv.coverage == "certified" else None,
                                 tolerancia=self.cfg.endogenous_xtol, unidad="phi" if inv.inversion_id == "phi_total" else "share",
                                 evidence_ref=None)
            fr_["evidence_ref"] = self.evidence("root", "localización de raíces: anchura del intervalo aislante certificado "
                                                "(no el residuo); %s" % (fr_.get("motivo") or "ok"), "inversion_result",
                                                {"cell_id": cid, "inversion_id": inv.inversion_id}, {}, fr_["change_bound"],
                                                fr_["unit"], fr_["method_id"], "pass" if fr_["status"] == "pass" else "limitation")
            self.rows["convergence_result"].append({k: fr_[k] for k in CV.COLUMNAS})
        if not algebraic and inv.coverage != "not_applicable" and inv.result_status not in ("not_identified", "undefined_denominator"):
            budget = self.budget_note(inv)
            if inv.computation_status == "complete":
                self.evidence("root", "búsqueda de raíces CERTIFICADA por encierros (%s): todas las raíces del dominio, cada una "
                              "con residuo <= %s; ausencia de raíces demostrada en el resto; %s" % (self.model.kind, self.tol_root,
                                                                                                    budget),
                              "inversion_result", {"cell_id": cid, "inversion_id": inv.inversion_id}, {}, self.tol_root, "share",
                              "certified_root_search", "pass")
            else:
                d = inv.diagnostics or {}
                pend = [[round(p[0], 12), round(p[1], 12), p[2]] for p in d.get("pending", [])][:10]
                self.evidence("root", "búsqueda SIN cobertura certificada completa (%s; cobertura %s): hallazgos=%s; saltos "
                              "rechazados=%s; pendientes=%s %s. No se publican raíces ni se declara inexistencia; %s" % (
                                  inv.reason, inv.coverage, json.dumps([round(x[0], 12) for x in d.get("roots_found", [])][:10]),
                                  len(d.get("rejected_jumps", [])), d.get("n_pending", 0), json.dumps(pend), budget),
                              "inversion_result", {"cell_id": cid, "inversion_id": inv.inversion_id},
                              {}, None, "share", "uncertified_root_scan", "limitation")
        self.rows["inversion_targets"].append({"cell_id": cid, "inversion_id": inv.inversion_id,
                                               "tau_f_given": inv.tau_f_given, "supplier_share_target": inv.supplier_share_target,
                                               "definition": inv.definition or inv.inversion_id,
                                               "evidence_ref": "CONTRATOS_D7_B_D8.md#inversion_result; grilla " + self.inp.grid_sha256[:16]})
        for k, r in enumerate(inv.roots):
            self.rows["scalar_inversion_roots"].append({"cell_id": cid, "inversion_id": inv.inversion_id, "root_index": k,
                                                        "value": r.value, "bracket_low": r.bracket_low, "bracket_high": r.bracket_high,
                                                        "residual": r.residual, "method_id": "certified_root_search",
                                                        "converged": r.converged})
        for k, (lo, hi, lc, hc, rb) in enumerate(inv.intervals):
            self.rows["scalar_inversion_intervals"].append({"cell_id": cid, "inversion_id": inv.inversion_id, "interval_index": k,
                                                            "lower": lo, "upper": hi, "lower_closed": lc, "upper_closed": hc,
                                                            "residual_bound": rb, "method_id": "invariance_proof"})
            self.evidence("root", "identidad demostrada en todo el intervalo: " + (inv.reason or "C2 invariante en phi (menú d)"),
                          "inversion_result", {"cell_id": cid, "inversion_id": inv.inversion_id}, {"phi": {"lower": lo, "upper": hi,
                          "lower_closed": lc, "upper_closed": hc}}, rb, "share", "invariance_proof")

    def budget_note(self, inv: INV.Inversion) -> str:
        """Presupuesto por inversión efectivo, legible en la evidencia del paquete."""
        b = getattr(inv, "budget_s", None)
        if b is None:
            return "presupuesto por inversión: no aplica (sin evidencia con presupuesto: %s)" % (
                "proveedor sin presupuesto" if inv.inversion_id == "phi_total" and self.inversion_budget_s is None
                else "invariancia demostrada o inversión sin evidencia C2(phi)")
        return "presupuesto por inversión: inversion_budget_seconds=%r s%s" % (
            b, " (AGOTADO: se repite solo con otra configuración, identidad distinta)"
            if inv.reason == "EVIDENCE_BUDGET_EXHAUSTED" else "")

    # ------------------------------------------------------------------------------------ R1 / R2
    def r1_level(self, j, bd, bf) -> int:
        """Nivel máximo del contorno certificado: el configurado o el mínimo con el que la diagonal de caja
        hypot(bd, bf) / (r1_n 2^L) alcanza r1_geometry_tol (con menos, R1 no podría completarse nunca), con tope 10."""
        (dl, dh), (fl, fh) = sup_axes(j, bd, bf)
        need = math.hypot(dh - dl, fh - fl) / (self.cfg.r1_n * self.cfg.r1_geometry_tol)
        lvl = math.ceil(math.log2(need)) if need > 1.0 else 0
        return max(self.cfg.r1_max_level, min(10, lvl))

    def geometry(self, cid):
        c = self.cells[cid]
        flags = {"outside_support": False, "corner_binding": False, "kink_adjacent": False,
                 "admissibility_violated": c["status"] == "excluded"}
        if c["status"] != "complete":
            self.rows["r1_summary"].append(dict(flags, cell_id=cid, n_components=None, n_rejected_crossings=0, no_solution=False,
                                                topology_stable=False, residual_bound=None, geometry_error_bound=None,
                                                computation_status=c["status"] if c["status"] != "complete" else "incomplete",
                                                reason_code=self.rows["confrontation_result"][-1]["reason_code"] or "CELL_NOT_COMPLETE"))
            for sec in R2M.SECTIONS:
                self.rows["r2_sections"].append(dict(flags, cell_id=cid, section_id=sec, n_roots_by_section=None,
                                                     n_tangential_roots=None, rate_input_id=None, no_solution=False,
                                                     computation_status=c["status"], reason_code="CELL_NOT_COMPLETE"))
            return
        design, j = c["ctx"]["design_v"], c["ctx"]["instrument_j"]
        hit = c["fr"]["hit"]
        bd, bf = hit["bars"]
        cs = self.cs_function(hit, design)
        K1 = c["K1"]
        f = lambda td, tf: cs(td, tf)[0] - K1  # noqa: E731
        reg = lambda td, tf: cs(td, tf)[1]  # noqa: E731
        # inexistencia DEMOSTRADA solo con cota superior certificada de C2 (CS <= C2 + cota < K1 en todo el menú)
        demonstrated_empty = bool(c.get("certified")) and K1 > c["C2"] + c["err"]
        if demonstrated_empty:
            r1 = R1M.R1Result(status="complete", topology_stable=True, residual_bound=0.0, geometry_error_bound=0.0)
            r1.certified = True
        else:
            ev2 = self.model.contour_evidence(hit["state"], design, K1)
            r1 = R1M.level_set(f, reg, j, bd, bf, n=self.cfg.r1_n, evidence=ev2, max_level=self.r1_level(j, bd, bf),
                               geometry_tol=self.cfg.r1_geometry_tol, tol_residual=self.tol_root)
        status = r1.status
        no_sol = status == "complete" and not r1.components
        gb = r1.geometry_error_bound if (r1.geometry_error_bound is not None and math.isfinite(r1.geometry_error_bound)) else None
        if r1.certified and status == "complete":
            conv_ok = gb is not None and gb <= self.cfg.r1_geometry_tol
            how = ("cota superior certificada de C2 menor que K1: conjunto vacío demostrado" if demonstrated_empty else
                   "refinamiento uniforme con encierros: cajas vacías o monótonas, cruces certificados con residuo "
                   "demostrado <= tolerancia; cota geométrica = diagonal máxima de caja con tramo (2-D) o semiancho del "
                   "intervalo aislante demostrado (1-D)")
            ev = self.evidence("convergence", "R1 CERTIFICADO: " + how, "r1_summary", {"cell_id": cid}, {}, gb, "tau",
                               "certified_contour", "pass" if conv_ok else "fail")
            conv = {"method_id": "certified_contour", "topology_before": len(r1.components), "topology_after": len(r1.components),
                    "coverage_complete": True, "status": "pass" if conv_ok else "fail"}
        elif r1.certified:
            ev = self.evidence("coverage", "R1 con encierros pero NO completo (%s): cota geométrica %s frente a tolerancia %s "
                               "o cajas sin resolver al nivel máximo %d; no se publican componentes" % (
                                   r1.reason, gb, self.cfg.r1_geometry_tol, self.cfg.r1_max_level), "r1_summary",
                               {"cell_id": cid}, {}, gb, "tau", "certified_contour_incomplete", "limitation")
            conv = {"method_id": "certified_contour_incomplete", "topology_before": None, "topology_after": None,
                    "coverage_complete": False, "status": "fail" if r1.reason == "GEOMETRY_TOLERANCE_NOT_REACHED" else "incomplete"}
        else:
            ev = self.evidence("coverage", "R1 SIN cobertura certificada (%s): marching squares n=%d y 2n aportan hallazgos (%d "
                               "componentes); dos mallas estables no certifican ausencia de componentes entre nudos" % (
                                   r1.reason, self.cfg.r1_n, len(r1.components)), "r1_summary", {"cell_id": cid}, {}, gb, "tau",
                               "uncertified_contour", "limitation")
            conv = {"method_id": "uncertified_contour", "topology_before": r1.n_coarse if r1.components else None,
                    "topology_after": len(r1.components) if r1.components else None, "coverage_complete": False,
                    "status": "incomplete"}
        self.rows["convergence_result"].append(dict(conv, **{
            "quantity_id": f"R1:{cid}", "level_before": 0, "level_after": 1,
            "result_ref": "r1_summary:" + json.dumps({"cell_id": cid}, sort_keys=True, separators=(",", ":")),
            "value_before": None, "value_after": None, "change_bound": gb, "tolerance": self.cfg.r1_geometry_tol, "unit": "tau",
            "verdict_changes": 0, "evidence_ref": ev}))
        complete = status == "complete"
        self.rows["r1_summary"].append(dict(flags, cell_id=cid, n_components=len(r1.components) if complete else None,
                                            n_rejected_crossings=len(r1.rejected), no_solution=no_sol,
                                            topology_stable=bool(r1.topology_stable), residual_bound=r1.residual_bound if complete else None,
                                            geometry_error_bound=gb if complete else None,
                                            computation_status=status, reason_code=None if complete else r1.reason,
                                            kink_adjacent=r1.kink_adjacent,
                                            corner_binding=complete and any(v.is_boundary and "+" in (v.boundary_label or "")
                                                                            for comp in r1.components for v in comp.vertices)))
        for comp in (r1.components if complete else []):
            ds = [v.tau_d for v in comp.vertices]
            fs = [v.tau_f for v in comp.vertices]
            self.rows["r1_components"].append({"cell_id": cid, "component_id": comp.component_id, "arc_length": comp.arc_length,
                                               "tau_d_min": min(ds), "tau_d_max": max(ds), "tau_f_min": min(fs), "tau_f_max": max(fs),
                                               "n_boundary_intersections": comp.n_boundary_intersections,
                                               "closed_curve": comp.closed_curve, "topology_kind": comp.topology_kind})
            for vx in comp.vertices:
                self.rows["r1_vertices"].append({"cell_id": cid, "component_id": comp.component_id, "vertex_id": vx.vertex_id,
                                                 "tau_d": vx.tau_d, "tau_f": vx.tau_f, "side": vx.side, "branch_id": _bid(vx.branch_id),
                                                 "residual": vx.residual, "is_boundary": vx.is_boundary,
                                                 "boundary_label": vx.boundary_label})
            for e in comp.edges:
                self.rows["r1_edges"].append({"cell_id": cid, "component_id": comp.component_id, "edge_id": e.edge_id,
                                              "from_vertex_id": e.from_vertex_id, "to_vertex_id": e.to_vertex_id,
                                              "branch_id": _bid(e.branch_id), "max_residual": e.max_residual,
                                              "geometric_error_bound": e.geometric_error_bound if math.isfinite(e.geometric_error_bound) else 1.0})
        for x in r1.rejected:
            self.rows["r1_rejected_crossings"].append({"cell_id": cid, "crossing_id": x.crossing_id, "tau_d_low": x.box[0],
                                                       "tau_d_high": x.box[1], "tau_f_low": x.box[2], "tau_f_high": x.box[3],
                                                       "branch_left": _bid(x.branch_left), "branch_right": _bid(x.branch_right),
                                                       "reason_code": x.reason_code})
        rate = self.inp.d7.rates.get(c["ctx"]["country_id"])
        for sec_id in R2M.SECTIONS:
            verified = rate is not None and rate["status"] == "verified"
            rv = float(rate["value"]) if verified else None
            rid_ = rate["rate_input_id"] if (sec_id == "tau_d_estatutario" and rate) else None
            applicable = R2M._path(sec_id, j, bd, bf, rv) is not None
            if demonstrated_empty and applicable and (sec_id != "tau_d_estatutario" or verified):
                sec = R2M.Section(sec_id, rate_input_id=rid_, n_roots=0, n_tangential=0, status="complete", no_solution=True)
            else:
                ev_sec = self.model.path_evidence(hit["state"], design, sec_id, rv, K1) if applicable else None
                sec = R2M.solve_section(f, reg, sec_id, j, bd, bf, rate=rv, rate_input_id=rid_, rate_verified=verified,
                                        n=self.cfg.r2_n, evidence=ev_sec, tol_residual=self.tol_root)
            if sec.status == "complete":
                how = ("cota superior certificada de C2 menor que K1 en todo el menú" if demonstrated_empty else
                       "búsqueda de raíces certificada por encierros del proveedor %s" % self.model.kind)
                self.evidence("root", "R2 %s CERTIFICADA: %s; residuo de cada raíz <= %s" % (sec_id, how, self.tol_root),
                              "r2_sections", {"cell_id": cid, "section_id": sec_id}, {}, self.tol_root, "tau",
                              "certified_empty_by_C2_bound" if demonstrated_empty else "certified_root_search", "pass")
            if sec.status == "incomplete" and sec.diagnostics.get("roots_found"):
                self.evidence("root", "R2 %s SIN cobertura certificada: hallazgos %s (no publicados como raíces)" % (
                    sec_id, json.dumps([round(r[0], 12) for r in sec.diagnostics["roots_found"]][:10])), "r2_sections",
                    {"cell_id": cid, "section_id": sec_id}, {}, None, "tau", "uncertified_root_scan", "limitation")
            self.rows["r2_sections"].append({"cell_id": cid, "section_id": sec_id, "n_roots_by_section": sec.n_roots,
                                             "n_tangential_roots": sec.n_tangential, "rate_input_id": sec.rate_input_id,
                                             "no_solution": sec.no_solution, "computation_status": sec.status,
                                             "reason_code": sec.reason, "outside_support": False,
                                             "corner_binding": sec.corner_binding, "kink_adjacent": sec.kink_adjacent,
                                             "admissibility_violated": False})
            for r in sec.roots:
                self.rows["r2_roots"].append({"cell_id": cid, "section_id": sec_id, "root_index": r.root_index,
                                              "tau_d_root": r.tau_d, "tau_f_root": r.tau_f, "parameter_low": r.parameter_low,
                                              "parameter_high": r.parameter_high, "root_type": r.root_type, "side": r.side,
                                              "branch_id": _bid(r.branch_id), "residual": r.residual, "method_id": "certified_root_search",
                                              "corner_binding": r.corner_binding, "kink_adjacent": r.kink_adjacent})

    # ------------------------------------------------------------------------------------ afirmaciones y robustez
    def universe(self, claim: CL.Claim, *, macro_filter=None) -> tuple[list, bool]:
        pts, complete = self.universe_raw(claim)
        return pts, complete and bool(pts)

    def universe_raw(self, claim: CL.Claim) -> tuple[list, bool]:
        """Puntos (G_best, err) del universo del claim en las celdas de ESTA corrida y si ninguna celda requerida quedó
        incompleta (sin exigir puntos: la agregación por unidades lo exige sobre el total)."""
        groups = {}
        complete = True
        sets = set(claim.support_sets)
        want_instr = set(claim.instruments)
        for cid, c in self.cells.items():
            ctx = c["ctx"]
            if c["om"]["set"] not in sets or ctx["design_v"] != claim.design or ctx["country_id"] not in claim.countries:
                continue
            if ctx["bound_variant"] != claim.bound_variant or ctx["layer"] != claim.layer or ctx["eta_w_block"] != claim.eta_w_block:
                continue
            if ctx["instrument_j"] not in want_instr:
                continue
            if claim.claim_scope == "country_instrument" and ctx["availability_case_id"] != claim.availability_case_id:
                continue
            if claim.claim_scope != "country_instrument":
                allowed = {"domestic_unchanged", claim.availability_case_id}
                if ctx["availability_case_id"] not in allowed:
                    continue
            st = c["mac"]["state"]
            if st.anchor_year not in claim.years:
                continue
            if c["status"] == "not_applicable":
                continue
            key = (ctx["omega_id"], ctx["national_state_sha256"], ctx["country_id"], ctx["instrument_j"], ctx["availability_case_id"])
            if c["status"] != "complete":
                complete = False
                continue
            g = groups.get(key)
            if g is None or c["K1"] < g[1]:
                groups[key] = (c["C2"], c["K1"], c["err"])
        pts = [(C2 - K1, err) for C2, K1, err in groups.values()]
        return pts, complete

    def build_claims(self):
        cls = CL.derive(self.inp.registry, self.inp.model_case_map, self.claim_sets())
        self.claim_list = cls
        self.verdicts, self.claim_tally = {}, {}
        for cl in cls:
            if not set(cl.support_sets) <= set(self.cfg.base_sets):
                self.verdicts[cl.claim_id] = CL.Verdict("not_evaluated", "not_evaluated", None, None, 0, "SETS_NOT_IN_RUN")
            else:
                pts, complete = self.universe(cl)
                tally = COV.Tally()
                for sid in cl.support_sets:
                    tally.merge(self.certify_claim_region(cl, sid, self.struct_axes(sid)))
                self.claim_tally[cl.claim_id] = tally
                self.verdicts[cl.claim_id] = claim_verdict(CL.evaluate(pts, complete=complete and not self.incomplete_reasons),
                                                           tally)
            self.rows["claims"].append(cl.row(self.verdicts[cl.claim_id].status))
        self.claim_coverage_rows()
        if self.cfg.run_robustness:
            for cl in cls:
                self.robustness(cl)

    # ------------------------------------------------------------------------------------ cobertura del continuo
    def struct_axes(self, set_id: str, overrides: dict | None = None) -> dict:
        """Intervalos entre nudos del nivel por eje estructural (override: nudos del soporte ampliado)."""
        d7 = self.inp.d7
        axes = {}
        for pid in STRUCT:
            if overrides and pid in overrides:
                axes[pid] = COV.axis_intervals(overrides[pid])
            else:
                axes[pid] = COV.axis_intervals(level_nodes(d7.nodes(set_id, pid), d7.support(set_id, pid)["scale"], self.cfg.level))
        return axes

    def claim_contexts(self, cl: CL.Claim, set_id: str, corner: dict, macro_overrides: dict | None = None) -> tuple[list, dict]:
        """Universo del claim para la certificación por cajas: vértices macro (reducción demostrada) x estados x menús
        disponibles, con N = Q_min + DME de la capa/cota del país. Devuelve (contextos, valores fijos)."""
        d7 = self.inp.d7
        mo = macro_overrides or {}
        axes = {}
        for pid in ("eta_w", "gain_share", "pi_iva", "pi_otros_productos", "pi_produccion"):
            if pid in mo:
                axes[pid] = mo[pid]
            else:
                lo, hi = d7.interval(set_id, pid)
                axes[pid] = [lo] if lo == hi else [lo, hi]
        axes["eta_H"] = mo.get("eta_H", d7.nodes(set_id, "eta_H"))
        fixed_axes = {pid: d7.nodes(set_id, pid) for pid in FIXED + BARS}
        out, fixed = [], None
        names = sorted(axes)
        fnames = sorted(fixed_axes)
        for fcombo in product(*[fixed_axes[n] for n in fnames]):
            fv = dict(zip(fnames, fcombo))
            if fixed is None:
                fixed = fv
            elif fv != fixed:
                return [], {"MULTIPLE_FIXED_COMBINATIONS": True}
        for combo in product(*[axes[n] for n in names]):
            v = dict(corner, **dict(zip(names, combo)), **fixed)
            if "eta_w" not in mo and self.block_of(v["eta_w"]) != cl.eta_w_block:
                continue
            for country in cl.countries:
                for st in self.states_for({"set": set_id, "values": v}, country):
                    if st.anchor_year not in cl.years:
                        continue
                    m = MC.bridge(st.share_dict(), v)
                    ks = [g.Q(cl.bound_variant) for g in self.inp.grid_cells if g.country_id == country and g.layer == cl.layer]
                    if not ks:
                        continue
                    for j in cl.instruments:
                        if not [c for jj, c, avail, _ in self.frontier_cases(country) if jj == j and avail]:
                            continue
                        out.append(COV.Context(cl.design, j, (float(fixed["bar_tau_d"]), float(fixed["bar_tau_f"])),
                                               float(m.s_Pi_marg), float(m.s_T_marg), float(v["eta_H"]), float(v["gain_share"]),
                                               min(ks) + self.inp.dme_gai))
        return out, fixed or {}

    def certify_claim_region(self, cl: CL.Claim, set_id: str, axes: dict, *, prefix: dict | None = None,
                             macro_overrides: dict | None = None) -> COV.Tally:
        """Clases certificadas de las cajas del claim en el set (restringidas al prefijo de la unidad si procede).
        Caja degenerada (todos los ejes singleton) = nudo evaluado; sin encierro del proveedor: pending."""
        t = COV.Tally()
        corner = {pid: Decimal(repr(axes[pid][0][0])) for pid in STRUCT}
        ctxs, fixed = self.claim_contexts(cl, set_id, corner, macro_overrides)
        cajas = [COV.union_box(axes, prefix)] if self.cfg.coverage_union else list(COV.boxes(axes, prefix))
        # la caja unión necesita ceil(log2(nº de cajas L0 que reúne)) niveles más para llegar al tamaño L0: el peor caso
        # es del orden de la enumeración L0 original (no exponencial en una profundidad arbitraria)
        extra = COV.niveles_union(axes, prefix) if self.cfg.coverage_union else 0
        for box in cajas:
            if box is None:
                continue
            if all(lo == hi for lo, hi in box.values()):
                t.add(COV.BoxResult("evaluated", max_width=0.0))
            else:
                t.add(COV.certify_box(self.model, box, ctxs, fixed, CL.EPS_ECON, self.cfg.coverage_max_depth + extra))
        return t

    def claim_coverage_rows(self):
        """Una fila de cobertura del continuo POR AFIRMACIÓN (salida que cuantifica sobre soportes continuos)."""
        for cl in self.claim_list:
            t = self.claim_tally.get(cl.claim_id)
            if t is None:
                continue
            self.coverage_row_for_claim(cl, t)

    def coverage_row_for_claim(self, cl: CL.Claim, t: COV.Tally):
        d7 = self.inp.d7
        sid = cl.support_sets[0]
        box = {pid: {"lower": float(d7.interval(sid, pid)[0]), "upper": float(d7.interval(sid, pid)[1]), "lower_closed": True,
                     "upper_closed": True} for pid in STRUCT}
        wid = "WU:" + K.H([self.run_id, "claim", cl.claim_id])[:40]
        nondeg = t.n_boxes - t.evaluated
        if t.pending:
            kind, status = "pending", "incomplete"
            ev = self.evidence("coverage", "continuo de %s: %d cajas pendientes de %d (%s); no se publica veredicto sobre el "
                               "continuo" % (cl.claim_id, t.pending, t.n_boxes, ",".join(sorted(t.reasons)) or "sin encierro"),
                               None, {}, box, None, "share", "box_coverage_pending", "limitation")
        elif nondeg == 0:
            kind, status = "evaluated", "complete"
            ev = self.evidence("coverage", "continuo de %s: soportes estructurales singleton; las %d cajas son nudos evaluados" % (
                cl.claim_id, t.n_boxes), None, {}, box, None, "share", "tensor_nodes_level%d" % self.cfg.level, "pass")
        else:
            kind, status = "certified_pruned", "complete"
            ev = self.evidence("pruning", "continuo de %s CERTIFICADO por cajas: %d cajas (%d hojas tras refinamiento) con clase "
                               "de G determinada por encierro demostrativo del proveedor %s (infeasible=%d, feasible=%d, "
                               "mixed=%d, nudos=%d); cota: |G| >= epsilon_econ en toda hoja" % (
                                   cl.claim_id, t.n_boxes, t.leaves, self.model.kind, t.infeasible, t.feasible, t.mixed,
                                   t.evaluated), None, {}, box, CL.EPS_ECON, "share", "certified_box_classification", "pass")
        self.rows["computation_coverage"].append({
            "work_unit_id": wid, "parent_work_unit_id": None, "support_set_id": sid, "domain_box": box,
            "algorithm_id": "box_classification_depth%d" % self.cfg.coverage_max_depth, "checkpoint_sha256": None,
            "coverage_kind": kind, "unresolved_boxes": t.pending, "estimated_error": None, "unit": "share",
            "elapsed_seconds": 0.0, "peak_bytes": 0, "status": status,
            "reason_code": None if status == "complete" else "CONTINUUM_COVERAGE_PENDING", "evidence_ref": ev})

    def claim_sets(self):
        out = {}
        for preg, eds in self.inp.set_index.items():
            out[preg] = eds
        return out


    def robustness(self, cl: CL.Claim, *, reduced_q: dict | None = None):
        vd = self.verdicts[cl.claim_id]
        base = vd.status
        if not set(cl.support_sets) <= set(self.cfg.base_sets):
            return
        country = cl.country_id
        rid = lambda *parts: "BRK:" + K.H([cl.claim_id, *parts])[:40]
        for pid, block, comp, directions in (("eta_w", "incidencia_laboral", cl.eta_w_block, ("inferior", "superior")),
                                             ("pi_iva", "cuna_tributaria", "iva", ("inferior", "superior")),
                                             ("pi_otros_productos", "cuna_tributaria", "otros_productos", ("inferior", "superior")),
                                             ("pi_produccion", "cuna_tributaria", "produccion", ("inferior", "superior")),
                                             ("chi_r", "cobertura_residual", None, ("inferior", "superior")),
                                             ("rho", "tecnologia", None, ("inferior", "superior")),
                                             ("a", "tecnologia", None, ("inferior", "superior")),
                                             ("kappa_tilde", "tecnologia", None, ("inferior", "superior"))):
            if pid == "chi_r":
                # cobertura residual: sin momento/crosswalk D19 admisible (formulas.json: inactivo, MOMENT_NOT_IDENTIFIED)
                lo, hi = (float(x) for x in self.C.F["parameters"]["chi_r"]["conditional_domain"])
                for direction in directions:
                    res = RB.Breakdown(block, None, None, direction, lo, hi, "aritmetica", status="not_applicable_not_identified",
                                       reason="MOMENT_NOT_IDENTIFIED", boundary_kind="epistemic",
                                       evaluated_domain="no evaluado: momento/crosswalk D19 no identificado",
                                       theoretical_domain="dominio condicional declarado [0,1] (formulas.json chi_r)")
                    self.breakdown_row(cl, rid(pid, direction), res, "chi_r", None)
                continue
            for direction in directions:
                s0 = cl.support_sets[0]
                lo, hi = (float(x) for x in self.inp.d7.interval(s0, pid))
                scale = self.inp.d7.support(s0, pid)["scale"] or "arithmetic"
                res = RB.search(block, pid, comp if pid.startswith("pi_") or pid == "eta_w" else None, direction, lo, hi, scale,
                                lambda iv, pid=pid: self.claim_holds(cl, vd, {pid: iv}), ladder=self.cfg.robustness_ladder,
                                bisect_tol=self.cfg.robustness_bisect_tol, baseline_status=base)
                self.breakdown_row(cl, rid(pid, direction), res, pid, comp if pid.startswith("pi_") else None)
        # eta_H: escalera anidada declarada
        ladders = self.C.F["parameters"]["eta_H"]["sensitivity_ladders"]
        res = RB.ladder_search("incidencia_laboral", "eta_H", ladders,
                               lambda lv: self.claim_holds(cl, vd, {"eta_H": [Decimal(str(x)) for x in lv]}), baseline_status=base)
        self.breakdown_row(cl, rid("eta_H", "ladder"), res, "eta_H", None)
        # pi conjunto (los tres componentes a la vez)
        for direction in ("inferior", "superior"):
            s0 = cl.support_sets[0]
            lo, hi = (float(x) for x in self.inp.d7.interval(s0, "pi_iva"))
            res = RB.search("cuna_tributaria", None, None, direction, lo, hi, "arithmetic",
                            lambda iv: self.claim_holds(cl, vd, {p: iv for p in ("pi_iva", "pi_otros_productos", "pi_produccion")}),
                            ladder=self.cfg.robustness_ladder, bisect_tol=self.cfg.robustness_bisect_tol, baseline_status=base, joint=True)
            self.breakdown_row(cl, rid("pi_joint", direction), res, None, None)
        self.q_sensitivity(cl, vd, reduced=reduced_q)

    def claim_holds(self, cl, vd, overrides):
        """Reevalúa el universo del claim con soportes modificados (macro: vértices; estructura: nudos nuevos y región
        continua certificada por cajas). Memoria acotada: se conserva el peor punto, no la lista completa."""
        pts = _Worst(vd.verdict)
        for set_id in cl.support_sets:
            for values in self.omega_points(set_id, overrides=self._as_nodes(overrides)):
                if values["eta_w"] is not None and self.block_of(values["eta_w"]) != cl.eta_w_block and "eta_w" not in overrides:
                    continue
                try:
                    self.model.derive(values)
                except M.DomainError:
                    return "inadmissible", "a_gt1"
                for country in cl.countries:
                    for st in self.states_for({"set": set_id, "values": values}, country):
                        if st.anchor_year not in cl.years:
                            continue
                        m = MC.bridge(st.share_dict(), values)
                        if not m.admissible:
                            return "inadmissible", _edge(m.reasons)
                        lam, y = float(m.lambda_pi), float(values["gain_share"])
                        for j in cl.instruments:
                            cases = [c for jj, c, avail, _ in self.frontier_cases(country) if jj == j and avail]
                            if not cases:
                                continue
                            _, hit = self.ceiling(values, cl.design, j)
                            ce = hit["ceiling"]
                            if ce.status != "complete":
                                return "incomplete", None
                            ks = [g.Q(cl.bound_variant) for g in self.inp.grid_cells if g.country_id == country and g.layer == cl.layer]
                            if not ks:
                                continue
                            K1 = (min(ks) + self.inp.dme_gai) / (lam * y)
                            cert = getattr(ce.sup, "error_kind", "") == "certified_bound"
                            e = (ce.numerical_error or 0.0) if cert else max(ce.numerical_error or 0.0, self.t2)
                            pts.append((ce.C2 - K1, e, values, country, st))
        if not pts:
            return "incomplete", None
        ok = pts.holds()
        struct_over = {p: v for p, v in self._as_nodes(overrides).items() if p in STRUCT}
        if ok and struct_over:
            # la región ampliada es CONTINUA: los nudos no bastan (no se supone monotonía); se certifica por cajas
            want = {"robust_infeasible": "infeasible", "robust_feasible": "feasible"}[vd.verdict]
            tally = COV.Tally()
            witness = None
            for set_id in cl.support_sets:
                axes = self.struct_axes(set_id, struct_over)
                corner = {pid: Decimal(repr(axes[pid][0][0])) for pid in STRUCT}
                ctxs, fixed = self.claim_contexts(cl, set_id, corner)
                cajas = [COV.union_box(axes)] if self.cfg.coverage_union else list(COV.boxes(axes))
                extra = COV.niveles_union(axes) if self.cfg.coverage_union else 0
                for box in cajas:
                    if all(lo == hi for lo, hi in box.values()):
                        tally.add(COV.BoxResult("evaluated"))
                        continue
                    r = COV.certify_box(self.model, box, ctxs, fixed, CL.EPS_ECON, self.cfg.coverage_max_depth + extra)
                    tally.add(r)
                    if r.klass not in (want, "pending") and witness is None:
                        witness = {pid: (lo + hi) / 2 for pid, (lo, hi) in box.items()}
            if witness is not None:
                return "fails", [{"parameter_id": pid, "value": float(witness[pid])} for pid in sorted(struct_over)]
            if tally.pending and self.cfg.coverage_union:
                # INTEGRACIÓN 3.7: con cajas sin decidir, un punto certificado que viola la afirmación prueba el fallo
                for set_id in cl.support_sets:
                    axes = self.struct_axes(set_id, struct_over)
                    corner = {pid: Decimal(repr(axes[pid][0][0])) for pid in STRUCT}
                    ctxs, fixed = self.claim_contexts(cl, set_id, corner)
                    w = COV.testigo_de_fallo(self.model, COV.union_box(axes), ctxs, fixed, want, CL.EPS_ECON)
                    if w is not None:
                        return "fails", [{"parameter_id": pid, "value": float(w[pid])} for pid in sorted(struct_over)]
            if tally.pending:
                return "incomplete", None
            return "holds", None
        if ok:
            return "holds", None
        g, e, v, c, s = pts.first_bad
        return "fails", [{"parameter_id": p, "value": float(v[p])} for p in sorted(set(overrides) | {"eta_w", "eta_H"}) if p in v]

    def _as_nodes(self, overrides):
        out = {}
        for pid, iv in overrides.items():
            if pid in ("eta_H",) or isinstance(iv, list):
                out[pid] = [Decimal(repr(float(x))) for x in iv]
            else:
                lo, hi = iv
                out[pid] = [Decimal(repr(lo)), Decimal(repr(hi))]
        return out

    def breakdown_row(self, cl, bid, res: RB.Breakdown, pid, comp):
        ws = None
        if res.witnesses and res.status in ("breakdown_found", "incomplete_search"):
            # un testigo de fallo DEMOSTRADO se conserva aunque el umbral no se haya localizado (sin r_critical)
            ws = "WSET:" + bid[4:]
            what = ("testigos del quiebre" if res.status == "breakdown_found" else
                    "testigo de fallo (umbral acotado en %s, NO localizado)" % (res.bracket,))
            self.rows["witness_sets"].append({"witness_set_id": ws, "scope": "support_breakdown",
                                              "definition": f"{what} {res.block_id}/{pid or 'conjunto'}/{res.direction} de {cl.claim_id}"})
            for k, w in enumerate(res.witnesses):
                self.rows["breakdown_witnesses"].append({"witness_set_id": ws, "component_index": 0, "witness_index": k,
                                                         "parameter_id": w["parameter_id"], "value": w["value"], "omega_id": None})
        self.rows["support_breakdown_result"].append({
            "breakdown_id": bid, "run_id": self.run_id, "design_v": cl.design, "country_id": cl.country_id,
            "instrument_j": cl.instrument_j, "availability_case_id": cl.availability_case_id, "bound_variant": cl.bound_variant,
            "eta_w_block": cl.eta_w_block, "omega_id": None, "claim_id": cl.claim_id, "block_id": res.block_id,
            "parameter_id": pid, "component_id": comp if pid and pid.startswith("pi_") else None, "direction": res.direction,
            "support_low_primary": res.support_low, "support_high_primary": res.support_high,
            "expansion_factor_r": res.expansion_factor_r, "r_critical": res.r_critical if res.status == "breakdown_found" else None,
            "witness_set_id": ws, "status": res.status, "domain_edge_reached": res.domain_edge_reached,
            "boundary_kind": res.boundary_kind, "boundary_value": res.boundary_value,
            "reached_expansion_factor": res.reached_expansion_factor, "evaluated_domain": res.evaluated_domain or "no evaluado",
            "theoretical_domain": res.theoretical_domain or "no aplica", "n_components": res.n_components,
            "epsilon_econ": "0.01", "joint_breakdown": res.joint, "scale_kind": res.scale_kind,
            "computation_status": res.computation_status,
            "reason_code": res.reason if res.computation_status != "complete" or res.status != "breakdown_found" else None})

    @staticmethod
    def q_scopes(cl) -> list:
        scopes = [("global", None)] + ([("country", c) for c in cl.countries] if cl.claim_scope == "global" else [])
        if cl.claim_scope != "global":
            scopes = [("global", None), ("country", cl.country_id)]
        return scopes

    def q_universe(self, cl, sc) -> list:
        uni = []
        for cid, c in self.cells.items():
            ctx = c["ctx"]
            if c["status"] != "complete" or c["om"]["set"] not in cl.support_sets or ctx["design_v"] != cl.design:
                continue
            if ctx["bound_variant"] != cl.bound_variant or ctx["layer"] != cl.layer or ctx["eta_w_block"] != cl.eta_w_block:
                continue
            if ctx["country_id"] not in cl.countries or (sc and ctx["country_id"] != sc) or ctx["instrument_j"] not in cl.instruments:
                continue
            uni.append({"C2": c["C2"], "err": c["err"], "lambda": c["lam"], "gain": c["y"], "D": self.inp.dme_gai, "Qs": [c["Q"]],
                        "key": (ctx["omega_id"], ctx["national_state_sha256"], ctx["country_id"], ctx["instrument_j"])})
        merged = {}
        for u in uni:
            m = merged.setdefault(u["key"], dict(u, Qs=[]))
            m["Qs"].extend(u["Qs"])
        return list(merged.values())

    def q_sensitivity(self, cl, vd, *, reduced: dict | None = None):
        """reduced: {'scope|país': resumen agregado de unidades} (modo unidades) o None (universo desde celdas)."""
        for scope, sc in self.q_scopes(cl):
            verdict = vd.verdict if vd.status != "not_evaluated" else "not_evaluated"
            if reduced is None:
                res = RB.q_sensitivity(verdict, self.q_universe(cl, sc))
            else:
                res = RB.q_sensitivity_reduced(verdict, reduced.get(f"{scope}|{sc or ''}"))
            sid = "QSN:" + K.H([cl.claim_id, scope, sc])[:40]
            ws = None
            if res.status == "breakdown_found":
                ws = "WSET:" + sid[4:]
                self.rows["witness_sets"].append({"witness_set_id": ws, "scope": "external_requirement",
                                                  "definition": f"punto que fija m_Q* para {cl.claim_id} ({scope})"})
                self.rows["breakdown_witnesses"].append({"witness_set_id": ws, "component_index": 0, "witness_index": 0,
                                                         "parameter_id": "gain_share", "value": res.witness["gain"],
                                                         "omega_id": res.witness["key"][0]})
            self.rows["external_requirement_sensitivity_result"].append({
                "sensitivity_id": sid, "run_id": self.run_id, "design_v": cl.design, "instrument_j": cl.instrument_j,
                "availability_case_id": cl.availability_case_id, "bound_variant": cl.bound_variant, "eta_w_block": cl.eta_w_block,
                "claim_id": cl.claim_id, "scale_scope": scope, "claim_scope": cl.claim_scope, "country_id": cl.country_id,
                "m_Q_critical": res.m_Q_critical, "reduction_from_reported": (1 - res.m_Q_critical) if res.m_Q_critical is not None else None,
                "status": res.status, "witness_set_id": ws, "epsilon_econ": "0.01", "external_grid_sha256": self.inp.grid_sha256,
                "computation_status": res.computation_status, "reason_code": res.reason, "scale_country_id": sc})

    # ------------------------------------------------------------------------------------ cobertura
    def build_coverage(self, elapsed):
        """Cobertura de NUDOS por set (o por unidad): los nudos del nivel se evaluaron todos o la corrida se detuvo.
        La cobertura del CONTINUO se registra por afirmación (claim_coverage_rows)."""
        d7 = self.inp.d7
        peak = tracemalloc.get_traced_memory()[1] if tracemalloc.is_tracing() else 0
        for s in self.evaluated_sets():
            box = {}
            for pid in STRUCT:
                nodes = level_nodes(d7.nodes(s, pid), d7.support(s, pid)["scale"], self.cfg.level)
                if self.unit is not None and pid in self.unit["prefix"]:
                    nodes = [nodes[self.unit["prefix"][pid]]]
                box[pid] = {"lower": float(nodes[0]), "upper": float(nodes[-1]), "lower_closed": True, "upper_closed": True}
            status = "complete" if not self.incomplete_reasons else "incomplete"
            ev = self.evidence("coverage", "nudos del nivel %d evaluados%s; el continuo entre nudos se certifica (o queda "
                               "pendiente) por afirmación" % (self.cfg.level, "" if status == "complete" else ": DETENIDA (" +
                                                              self.incomplete_reasons[0] + ")"),
                               None, {}, box, None, "none", "tensor_nodes_level%d" % self.cfg.level,
                               "pass" if status == "complete" else "limitation")
            wid = "WU:" + K.H([self.run_id, s] + ([self.unit["unit_id"]] if self.unit is not None else []))[:40]
            self.rows["computation_coverage"].append({
                "work_unit_id": wid, "parent_work_unit_id": None, "support_set_id": s,
                "domain_box": box, "algorithm_id": "tensor_nodes_level%d" % self.cfg.level, "checkpoint_sha256": None,
                "coverage_kind": "evaluated", "unresolved_boxes": 0, "estimated_error": None,
                "unit": "share", "elapsed_seconds": round(elapsed, 3), "peak_bytes": peak, "status": status,
                "reason_code": None if status == "complete" else self.incomplete_reasons[0], "evidence_ref": ev})
        self.evidence("pruning", "reducción macro: con estado estructural fijo lambda es afín en (eta_w, pi_j) y G = C2 - N/(lambda y) "
                      "es monótona en lambda y en y para N = Q + DME > 0; los extremos sobre la caja macro están en vértices "
                      "(verificado en pruebas sintéticas independientes)", None, {}, {}, None, "none", "vertex_reduction_proof")


class _Worst:
    """Acumulador acotado para claim_holds: el veredicto de robustez solo necesita el peor punto y el primer testigo."""

    def __init__(self, verdict: str):
        self.verdict, self.n, self.first_bad = verdict, 0, None

    def append(self, p):
        self.n += 1
        g, e = p[0], p[1]
        bad = (self.verdict == "robust_infeasible" and g + e > -CL.EPS_ECON) or \
              (self.verdict == "robust_feasible" and g - e < CL.EPS_ECON)
        if bad and self.first_bad is None:
            self.first_bad = p

    def __bool__(self):
        return self.n > 0

    def holds(self) -> bool:
        if self.verdict not in ("robust_infeasible", "robust_feasible"):
            raise ValueError("sin afirmación en la línea base")
        return self.first_bad is None


def claim_verdict(v: CL.Verdict, tally: COV.Tally) -> CL.Verdict:
    """Veredicto sobre el CONTINUO: nudos + clases certificadas de las cajas. Pendiente -> no evaluado; región
    certificada de clase opuesta o mixta -> inconcluso (testigo en el continuo); si no, el veredicto de los nudos."""
    if v.status == "not_evaluated":
        return v
    if tally.pending:
        return CL.Verdict("not_evaluated", "not_evaluated", None, None, v.n_points, "CONTINUUM_COVERAGE_PENDING")
    if v.verdict in ("robust_infeasible", "robust_feasible") and not tally.covers(v.verdict):
        return CL.Verdict("inconclusive", "inconclusive", v.sup_upper, v.inf_lower, v.n_points, "CONTINUUM_CERTIFIED_OTHER_CLASS")
    return v


def _finite_dec(x) -> bool:
    try:
        canon_dec(x)
        return True
    except Exception:
        return False


def _bid(b: str) -> str:
    import re
    s = re.sub(r"[^A-Za-z0-9_.:-]", "_", str(b)) or "branch"
    return "BR:" + K.H(s)[:16] if len(s) > 60 else s


def _edge(reasons):
    m = {"Q_POT_GE_1": "q_pot", "S_T_MARG_NEGATIVE": "s_T_marg", "S_PI_MARG_NONPOSITIVE": "s_Pi_marg",
         "LAMBDA_NONPOSITIVE": "lambda_pi"}
    return m.get(reasons[0] if reasons else "", "lambda_pi")
