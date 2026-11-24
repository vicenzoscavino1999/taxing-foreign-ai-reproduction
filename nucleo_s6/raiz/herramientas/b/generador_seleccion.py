"""ORQUESTACIÓN del generador por valores del paso 4 (INTEGRACION H4 3.7, NO OFICIAL; copia candidata, no incorporada).

Movido a la estructura candidata desde codigo/generador_candidato_v2.py SIN cambios de lógica (Compartido, Generador:
preparar, localizar, previas, celda). Cambios de integración: E13 desde herramientas/s3/validadores/e13_referencia.py
(cargado por ruta relativa a ESTE archivo), E12 desde paper2b.rules (e12_verificar_celda/e12_filas_de_celda, iguales a
codigo/completitud_e12), el cálculo por valores desde paper2b.seleccion_valores; sin módulos demo del área ni constantes
del área; sin los modos de desarrollo (plan, nodo, celdas). Documentación original:
VERSIÓN v2 (INTEGRACION E12 3.7, NO OFICIAL): E12 con completitud derivada del contrato del núcleo
(codigo/completitud_e12.py) sobre las FILAS producidas; frontera, estados macro y celda una sola vez por identidad (sin
filas duplicadas cuando dos testigos comparten ω, frontera o celda); exporta las filas de cada celda para re-verificarlas
fuera del proceso; memoria de vértices estrictos DESHABILITADA (no demostrada). Estados: ok | rechazada_antes_del_calculo |
salida_invalida | incoherente | incompleta, siempre con motivos legibles.
Texto de la v1:
GENERADOR CANDIDATO E9–E12 por valores, integrado con el validador global_extreme v3 (VALIDACION 3.7.4, NO OFICIAL;
copia aislada; no es el generador oficial ni se incorpora al original).

  (Los modos de desarrollo plan/nodo/celdas del área NO existen en esta copia candidata: la ejecución se lanza desde el
   punto de entrada herramientas/b/seleccion_paso4.py, fases ejecutar/reanudar.)

E9  ω POR VALORES: Run.omega_points(conjunto, overrides = {9 estructurales: [valor exacto del testigo], 5 macro y η_H:
    [vértice del contexto]}) da UNA combinación; Run.omega_row da su identidad; se comprueba que los valores
    estructurales del ω son EXACTAMENTE los del testigo (sin aproximar a la malla) antes de calcular.
E10 PLAN de celdas testigo desde la tabla VALIDADA: el generador solo recibe testigos canónicos (GE.TestigosValidados:
    la tabla entera debe validar; los bytes de la tabla y sus campos descriptivos no se usan). Celda distinta = (hoja,
    punto, índice de contexto); filas que respalda; claves estructurales y macro distintas (modo plan, sin calcular).
E11 CACHÉS DE PROCESO EQUIVALENTES (Compartido):
    - techo por CLAVE ESTRUCTURAL entre conjuntos de soporte (Run.struct_cache ya lo hace dentro de un conjunto): la clave
      es el sha256 de la carga estructural completa (valores, diseño, menú, dominio τ, teoría, técnica), la misma que usa
      el núcleo para reutilizar dentro de un Run; el resultado (estado del techo, error, alcance, laterales) es el mismo
      objeto, no una copia reinterpretada;
    - vértices macro estrictos (macro.strict_vertices) memorizados por (dominios, términos, denominador, η_w, η_H, π):
      la enumeración ordena los vértices por s_L_marg + s_T_marg, que solo depende de esos valores; q_pot se evalúa antes
      para reproducir cualquier excepción que dependa de la estructura.
    - C2 de la fase global: NO se inyecta como techo (su anchura, 2–4e-6, no cumple tol_converge 1e-7 de la celda) ni se usa
      para podar (ver review/GENERADOR_CANDIDATO.md: en la rama y cota de mejor primero una cota inferior externa no reduce
      las cajas que deben refinarse para cerrar la brecha); se usa solo como CONTRASTE: el encierro del techo de la celda
      debe intersecar el certificado (si no, la celda es «incoherente»).
E12 TRAZABILIDAD y ESTADO: la celda guarda omega_id, set_id, contexto, hoja, filas que respalda y las comprobaciones;
    estado «ok» SOLO si todas las comprobaciones esenciales son verdaderas y todas las partes están completas;
    «rechazada_antes_del_calculo» si falla una previa (contexto, K1, ω exacto o admisible); «incoherente» si falla una
    posterior (K_comp_1 frente a K1, C2 frente al certificado); «incompleta» si alguna parte no terminó.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import time
import traceback
from collections import Counter
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

from paper2b import rules as _RULES  # noqa: E402
from paper2b import seleccion_valores as CE  # noqa: E402  (cálculo por valores en el núcleo candidato)
from paper2b.seleccion_valores import MACRO, Universo, qmin_table, state_meta  # noqa: E402


def _cargar_e13():
    import importlib.util
    nombre = "cand_e13_referencia"
    if nombre not in sys.modules:
        spec = importlib.util.spec_from_file_location(nombre, Path(__file__).resolve().parents[1] / "s3/validadores/e13_referencia.py")
        m = importlib.util.module_from_spec(spec)
        sys.modules[nombre] = m
        spec.loader.exec_module(m)
    return sys.modules[nombre]


GE = _cargar_e13()


class _E12:      # interfaz de codigo/completitud_e12 servida por las reglas E12 del núcleo candidato (resultado idéntico)
    verificar_celda = staticmethod(_RULES.e12_verificar_celda)
    filas_de_celda = staticmethod(_RULES.e12_filas_de_celda)


E12 = _E12
from paper2b import keys as K  # noqa: E402
from paper2b import macro as MC  # noqa: E402
from paper2b import run as RUNMOD  # noqa: E402

STRUCT = RUNMOD.STRUCT
TOL_K1 = 1e-9           # tolerancia del contraste K_comp_1 (redondeo de la forma cerrada), la misma del prototipo


def _log(etq, fase):
    print(time.strftime("%H:%M:%S", time.gmtime()), etq, fase, flush=True)


def _canon(x):
    if isinstance(x, Fraction):
        return "F:%d/%d" % (x.numerator, x.denominator)
    if isinstance(x, Decimal):
        return "D:" + str(x)
    if isinstance(x, dict):
        return {str(k): _canon(v) for k, v in sorted(x.items(), key=lambda kv: str(kv[0]))}
    if isinstance(x, (list, tuple)):
        return [_canon(v) for v in x]
    return x


def clave_vertices(domains, terms, denominator, omega):
    lect = {k: str(MC.F(omega[k])) for k in ("eta_w", "eta_H") + MC.PI_KEYS}
    return hashlib.sha256(json.dumps([_canon(domains), _canon(terms), denominator, lect], sort_keys=True).encode()).hexdigest()


class Compartido:
    """Cachés de proceso de E11 (ver docstring). `activo=False`: vía estándar sin compartir (control)."""

    def __init__(self, activo=True, memo_vertices=False):
        # memo_vertices: la memoria de vértices estrictos NO está demostrada (los estados de la selección son condicionales):
        # DESHABILITADA por defecto en esta vía.
        self.activo, self.techos, self.vertices = activo, {}, {}
        self.memo_vertices = bool(activo and memo_vertices)
        self.stats = Counter()
        self.seg = Counter()
        self._orig = MC.strict_vertices
        if self.memo_vertices:
            MC.strict_vertices = self._sv

    def restaurar(self):
        MC.strict_vertices = self._orig

    def _sv(self, domains, terms, denominator, omega):
        MC.q_pot(omega["kappa_tilde"], omega["a"], omega["rho"])
        k = clave_vertices(domains, terms, denominator, omega)
        if k in self.vertices:
            self.stats["vertices_reutilizados"] += 1
            return copy.deepcopy(self.vertices[k])
        t = time.time()
        v = self._orig(domains, terms, denominator, omega)
        self.seg["vertices_calculo_s"] += time.time() - t
        self.stats["vertices_calculados"] += 1
        self.vertices[k] = copy.deepcopy(v)
        return v

    def techo(self, r, oid, pais, design, j, case):
        om = r.omegas[oid]
        skey, _ = r.structural(om["values"], design, j)
        reuso = False
        if self.activo and skey in self.techos and skey not in r.struct_cache:
            r.struct_cache[skey] = self.techos[skey]
            reuso = True
        fr, secs = CE.frontier(r, oid, pais, design, j, case)
        if fr["available"]:
            if self.activo:
                self.techos.setdefault(skey, r.struct_cache[skey])
            self.stats["techos_reutilizados_entre_conjuntos" if reuso else "techos_calculados_o_del_run"] += 1
        return fr, secs, skey, reuso


omega_por_valores = CE.omega_por_valores      # movido a paper2b.seleccion_valores (misma lógica)


class Generador:
    def __init__(self, ctx, ref, compartido):
        self.ctx, self.ref, self.G = ctx, ref, compartido
        self.claims = {c.claim_id: c for c in ctx.claims}
        self.runs, self.U = {}, None
        self._fronteras, self._macros, self._celdas = {}, {}, {}

    def preparar(self, hojas):
        sets = sorted({s for h in hojas for s in self.claims[h].support_sets})
        for sid in sets:
            if sid not in self.runs:
                self.runs[sid] = self.ctx.run(sid, "generador:" + sid)
        self.U = Universo(self.runs, qmin_table(self.ctx.inp.grid_cells))

    def localizar(self, cl, idx):
        k = 0
        for sid in cl.support_sets:
            corner = {p: Decimal(str(CE.axes_nodes(self.ctx.view, self.ctx.cfg, sid)[p][0])) for p in STRUCT}
            cs, _ = self.U.contexts(cl, sid, corner)
            if idx < k + len(cs):
                c, bi = cs[idx - k]
                return sid, bi, self.U.meta(cl, sid, corner, bi), c
            k += len(cs)
        raise GE.Rechazo("E_TESTIGO_INDICE", "índice fuera del universo")

    def previas(self, w):
        """Comprobaciones ANTES del cálculo costoso (sin techo, macro ni celda). Devuelve (ok, pre, datos)."""
        cl = self.claims[w["claim_id_hoja"]]
        punto = {p: float(w["punto"][p]) for p in STRUCT}
        pre = {}
        try:
            sid, bi, meta, c = self.localizar(cl, w["indice_contexto"])
        except GE.Rechazo:
            return False, {"indice_en_universo": False}, None
        pre["indice_en_universo"] = True
        pre["contexto_coincide"] = self.ref.ctx_key(c) == json.loads(json.dumps(w["contexto"]))
        pre["diseno_instrumento"] = (c.design, c.instrument) == (cl.design, cl.instrument_j) == (w["diseno"], w["instrumento_hoja"])
        pre["pais"] = meta["pais"] == w["pais_hoja"]
        k1 = self.ref.K1(punto, c)
        pre["K1_coincide"] = [k1.lo, k1.hi] == list(w["K1_en_punto"])
        r = self.runs[sid]
        oid, ok, reason = omega_por_valores(r, sid, punto, meta["macro"])
        vals = r.omegas[oid]["values"]
        pre["omega_exacto"] = all(float(vals[p]) == punto[p] for p in STRUCT)
        pre["omega_admisible"] = bool(ok)
        return all(pre.values()), pre, {"cl": cl, "sid": sid, "bi": bi, "meta": meta, "c": c, "oid": oid, "motivo_omega": reason, "punto": punto}

    def _frontera(self, r, sid, oid, pais, design, j, case):
        """Una frontera por (conjunto, ω, país, diseño, menú, caso): como Run.build_frontiers, nunca dos filas del mismo frontier_id."""
        k = (sid, oid, pais, design, j, case)
        if k not in self._fronteras:
            self._fronteras[k] = self.G.techo(r, oid, pais, design, j, case)
            return self._fronteras[k], False
        return self._fronteras[k], True

    def _macro(self, r, sid, oid, pais, design, j, case):
        """Estados macro una vez por (conjunto, ω, país, diseño, menú, caso): como Run.build_macro, sin filas λ_π repetidas."""
        k = (sid, oid, pais, design, j, case)
        if k not in self._macros:
            self._macros[k] = CE.macro_states(r, oid, pais, design, j, case)
            return self._macros[k], False
        return self._macros[k], True

    def celda(self, w, etq):
        t = {}
        a = time.time()
        _log(etq, "inicio")
        ok, pre, dd = self.previas(w)
        t["previas_s"] = round(time.time() - a, 3)
        res = {"etiqueta": etq, "extreme_id": w["extreme_id"], "claim_id_hoja": w["claim_id_hoja"], "indice_contexto": w["indice_contexto"],
               "precomprobaciones": pre}
        if not ok:
            res.update(estado="rechazada_antes_del_calculo", motivos=["previa falsa: %s" % k for k, v in pre.items() if not v], tiempos_s=t)
            _log(etq, "rechazada antes del cálculo %s" % pre)
            return res
        cl, sid, meta, oid = dd["cl"], dd["sid"], dd["meta"], dd["oid"]
        r = self.runs[sid]
        j, case, pais, design = cl.instrument_j, cl.availability_case_id, meta["pais"], cl.design
        res.update(set_id=sid, omega_id=oid, pais=pais, diseno=design, instrumento=j, caso=case, estado_nacional=meta["estado_nacional"],
                   macro=meta["macro"], celda_externa=meta["celda_externa"])
        _log(etq, "previas ok")
        b = time.time()
        (fr, ts, skey, reuso), fr_reusada = self._frontera(r, sid, oid, pais, design, j, case)
        t["techo_s"] = round(time.time() - b, 3)
        res.update(clave_estructural=skey, techo_reutilizado_entre_conjuntos=reuso, frontera_reutilizada=fr_reusada, frontier_id=fr["frontier_id"])
        _log(etq, "techo (entre conjuntos=%s, frontera ya construida=%s)" % (reuso, fr_reusada))
        b = time.time()
        macs, mac_reusado = self._macro(r, sid, oid, pais, design, j, case)
        mac = [m for m in macs if state_meta(m["state"]) == meta["estado_nacional"]]
        gcell = [g for g in CE.grid_cells(r, pais) if g.external_cell_id == meta["celda_externa"]["id"]]
        t["macro_s"] = round(time.time() - b, 3)
        if len(mac) != 1 or len(gcell) != 1:
            res.update(estado="salida_invalida", motivos=["estado nacional no único: %d" % len(mac)] if len(mac) != 1 else ["celda externa no única: %d" % len(gcell)],
                       tiempos_s=t)
            return res
        res["macro_reutilizado"] = mac_reusado
        _log(etq, "macro (reutilizado=%s)" % mac_reusado)
        b = time.time()
        kc = (sid, oid, pais, design, j, case, mac[0]["row"]["macro_id"], gcell[0].external_cell_id, cl.bound_variant)
        if kc in self._celdas:
            cid, celda_reusada = self._celdas[kc], True
        else:
            cid, celda_reusada = CE.build_cell(r, oid, pais, design, j, case, fr, mac[0], gcell[0], cl.bound_variant), False
            self._celdas[kc] = cid
        t["resto_celda_s"] = round(time.time() - b, 3)
        _log(etq, "celda terminada (ya construida=%s)" % celda_reusada)
        # ---- E12: completitud derivada del contrato del núcleo, sobre las filas producidas (no sobre etiquetas)
        hit = fr.get("hit") or {}
        rate = r.inp.d7.rates.get(pais)
        tasa = float(rate["value"]) if (rate is not None and rate.get("status") == "verified") else None
        barras = tuple(hit.get("bars") or (None, None))
        comp = E12.verificar_celda(r.rows, cid, fr["frontier_id"], instrumento=j, barras=barras, tasa=tasa,
                                   run_geometry=bool(r.cfg.run_geometry), con_unidad=r.unit is not None, omega_id=oid)
        filas = E12.filas_de_celda(r.rows, cid, fr["frontier_id"])
        conf = filas["confrontation_result"][0] if len(filas["confrontation_result"]) == 1 else {}
        ce = filas["capture_ceiling_result"][0] if len(filas["capture_ceiling_result"]) == 1 else {}
        k1c, c2, err = conf.get("K_comp_1"), ce.get("C_2"), ce.get("numerical_error")
        post = {"K_comp_1_en_K1": k1c is not None and w["K1_en_punto"][0] - TOL_K1 <= k1c <= w["K1_en_punto"][1] + TOL_K1,
                "C2_interseca_certificado": c2 is not None and err is not None and c2 + err >= w["C2_en_punto"][0] and c2 - err <= w["C2_en_punto"][1]}
        if comp["estado"] == "invalida":
            estado = "salida_invalida"
        elif not all(post.values()):
            estado = "incoherente"
        elif comp["estado"] == "incompleta":
            estado = "incompleta"
        else:
            estado = "ok"
        motivos = list(comp["motivos"]) + ["poscomprobación falsa: %s" % k for k, v in post.items() if not v]
        res.update(estado=estado, motivos=motivos, completitud=comp, poscomprobaciones=post, cell_id=cid, celda_reutilizada=celda_reusada, tiempos_s=t,
                   techo={k: ce.get(k) for k in ("C_2", "numerical_error", "computation_status", "reason_code", "sup_not_attained")},
                   confrontacion={k: conf.get(k) for k in ("G", "K_comp_1", "verdict", "computation_status", "reason_code")},
                   clave_E12={"cell_id": cid, "frontier_id": fr["frontier_id"], "instrumento": j, "barras": list(barras), "tasa": tasa,
                              "run_geometry": bool(r.cfg.run_geometry), "con_unidad": r.unit is not None, "omega_id": oid},
                   filas=filas)
        return res
