"""E12 DE UNA CELDA CON RUTA NO APLICABLE (VALIDACION DETALLADA Y D-S1-d H4 3.7, NO OFICIAL; módulo candidato NUEVO).

No cambia paper2b.rules (frentes 1-2 y productor de S1 intactos): para una celda cuyo instrumento ESTÁ disponible delega
sin cambios en paper2b.rules.e12_verificar_celda; solo añade la ruta que E12 no resolvía de forma coherente.

Contrato vigente (núcleo, sin cambios):
- paper2b.run.Run.frontier_cases: instrumento disponible solo en los casos D4 domestic_unchanged y conditional_full.
- Run.ceiling_rows: sin instrumento, capture_ceiling_result con computation_status = not_applicable, reason_code =
  INSTRUMENT_NOT_AVAILABLE, C_2/numerical_error/tasas/laterales nulos y monotonicity_check = not_applicable; la frontera
  es solo estructural (Run.structural_only, sin barras ni malla).
- Run.cell: confrontation_result not_applicable / INSTRUMENT_NOT_AVAILABLE con C_2, K_comp_1 y G nulos, verdict
  no_verdict y run_readiness_flag = false; la evidencia de G (convergencia.fila_G) queda incomplete, sin cifras.
- Run.inversions: con C_2 indefinido ninguna inversión es numérica (valores nulos; result_status sin cifra).
- Run.geometry: celda no completa -> r1_summary con el estado y el motivo de la confrontación, sin componentes; cada
  sección R2 con el estado de la celda y CELL_NOT_COMPLETE, sin raíces. NO hay barras: no se evalúa sections._path.
Salida: estado "no_aplicable" (motivo INSTRUMENT_NOT_AVAILABLE) si TODA la ruta es coherente con ese contrato; "invalida"
si algo contradice la no aplicabilidad (cifras, estados completos, filas ausentes, duplicadas o de otra celda). Nunca
"completa": un caso no aplicable no se presenta como cálculo numérico completo. Con instrumento disponible y barras
nulas o no finitas, "invalida" con motivo (sin excepción).
"""
import math
from collections import Counter

from paper2b import rules as RULES

MOTIVO_NA = "INSTRUMENT_NOT_AVAILABLE"
NO_NUMERICOS = ("undefined_denominator", "not_identified")
VALORES_INVERSION = ("lambda_pi_required", "delta_y_required", "C_2_required", "external_factor_required", "phi_critical_partial",
                     "phi_critical_total", "n_scalar_solutions", "n_scalar_intervals")


def _filas(rows, tabla, **k):
    return [x for x in rows.get(tabla, []) if all(x.get(a) == b for a, b in k.items())]


def senal_no_aplicable(rows, cid, fid):
    """La celda declara (en cualquiera de sus filas) instrumento no disponible."""
    ce = _filas(rows, "capture_ceiling_result", frontier_id=fid)
    cx = _filas(rows, "cell_context", cell_id=cid)
    cf = _filas(rows, "confrontation_result", cell_id=cid)
    return (any(x.get("instrument_available") is False or x.get("reason_code") == MOTIVO_NA for x in ce)
            or any(x.get("instrument_available") is False for x in cx) or any(x.get("reason_code") == MOTIVO_NA for x in cf))


def verificar_celda(rows, cid, fid, *, instrumento, barras, tasa, run_geometry=True, con_unidad=True, omega_id=None):
    if senal_no_aplicable(rows, cid, fid):
        return verificar_no_aplicable(rows, cid, fid, run_geometry=run_geometry, omega_id=omega_id)
    if (not isinstance(barras, (list, tuple)) or len(barras) != 2
            or any(not isinstance(b, (int, float)) or isinstance(b, bool) or not math.isfinite(b) for b in barras)):
        return {"estado": "invalida", "partes": {"barras": {"estado": "relacion_rota", "motivo": "barras nulas o no finitas con instrumento disponible: %r" % (barras,)}},
                "motivos": ["barras: relacion_rota (nulas o no finitas con instrumento disponible)"], "n_partes": 1}
    return RULES.e12_verificar_celda(rows, cid, fid, instrumento=instrumento, barras=tuple(barras), tasa=tasa, run_geometry=run_geometry,
                                     con_unidad=con_unidad, omega_id=omega_id)


def verificar_no_aplicable(rows, cid, fid, *, run_geometry=True, omega_id=None):
    C = RULES.e12_contrato()
    partes, motivos = {}, []

    def parte(nombre, estado, motivo=None):
        partes[nombre] = {"estado": estado, "motivo": motivo}
        if estado in RULES.DEFECTUOSOS or estado == "incompleta":
            motivos.append("%s: %s%s" % (nombre, estado, (" (" + motivo + ")") if motivo else ""))

    def unica(tabla, nombre, **k):
        fs = _filas(rows, tabla, **k)
        if len(fs) != 1:
            parte(nombre, "ausente" if not fs else "duplicada", "%d filas %s para %s" % (len(fs), tabla, k))
            return None
        return fs[0]

    def na(nombre, cond, detalle):
        parte(nombre, "no_aplicable_justificada" if cond else "relacion_rota", MOTIVO_NA if cond else detalle)

    cx = unica("cell_context", "contexto", cell_id=cid)
    if cx is not None:
        ok = cx.get("instrument_available") is False and (omega_id is None or cx.get("omega_id") == omega_id)
        parte("contexto", "completa" if ok else "relacion_rota", None if ok else "instrument_available u omega_id incoherentes con la no aplicabilidad")
    if unica("frontier_context", "frontera", frontier_id=fid) is not None:
        parte("frontera", "completa")
    ce = unica("capture_ceiling_result", "techo", frontier_id=fid)
    if ce is not None:
        na("techo", ce.get("ceiling_id") == "CEI:" + fid[4:] and ce.get("instrument_available") is False and ce.get("computation_status") == "not_applicable"
           and ce.get("reason_code") == MOTIVO_NA and ce.get("monotonicity_check") == "not_applicable"
           and all(ce.get(k) is None for k in ("C_2", "numerical_error", "tau_d_at_sup", "tau_f_at_sup", "sup_not_attained", "sup_lateral_low", "sup_lateral_high")),
           "techo no aplicable con cifras, estado o motivo distintos del contrato")
    cf = unica("confrontation_result", "confrontacion", cell_id=cid)
    if cf is not None:
        na("confrontacion", (ce is None or cf.get("ceiling_id") == ce.get("ceiling_id")) and cf.get("computation_status") == "not_applicable"
           and cf.get("reason_code") == MOTIVO_NA and all(cf.get(k) is None for k in ("C_2", "K_comp_1", "G"))
           and cf.get("verdict") == "no_verdict" and cf.get("run_readiness_flag") is False,
           "confrontación no aplicable con cifras, veredicto o motivo distintos del contrato")
        mac = _filas(rows, "lambda_pi_envelope", macro_id=cf.get("macro_id"))
        if len(mac) != 1:
            parte("macro", "ausente" if not mac else "duplicada", "%d filas lambda_pi_envelope" % len(mac))
        else:
            # el estado macro no depende del instrumento; se informa, pero no convierte la celda en numérica
            parte("macro", "completa" if mac[0].get("computation_status") == "complete" else "no_aplicable_justificada", mac[0].get("reason_code"))
        g = _filas(rows, "convergence_result", quantity_id="G:" + cid)
        if len(g) != 1:
            parte("evidencia_G", "evidencia_ausente" if not g else "duplicada", "%d filas G:%s" % (len(g), cid))
        else:
            na("evidencia_G", g[0].get("status") == "incomplete" and g[0].get("coverage_complete") is False
               and all(g[0].get(k) is None for k in ("value_before", "value_after", "change_bound")),
               "la evidencia de G de una celda no aplicable no puede tener cifras ni pasar")
    inv = _filas(rows, "inversion_result", cell_id=cid)
    cnt = Counter(x.get("inversion_id") for x in inv)
    for k in sorted(set(cnt) - set(C["inversiones"]), key=str):
        parte("inversion:%s" % k, "id_inesperado", "inversion_id fuera de paper2b.inversion.INVERSIONS")
    for iid in C["inversiones"]:
        fs = [x for x in inv if x.get("inversion_id") == iid]
        if len(fs) != 1:
            parte("inversion:" + iid, "ausente" if not fs else "duplicada", "%d filas" % len(fs))
            continue
        f = fs[0]
        rs, st = f.get("result_status"), f.get("computation_status")
        metodo = "algebraic_closed_form" if iid in C["algebraicas"] else "fixed_point_bracket_bisection"
        ev = _filas(rows, "convergence_result", quantity_id="INV:%s:%s" % (cid, iid))
        na("inversion:" + iid, rs in NO_NUMERICOS and C["status_to_computation"].get(rs) == st and f.get("method_id") == metodo
           and bool(f.get("reason_code")) and all(f.get(k) is None for k in VALORES_INVERSION) and not ev,
           "inversión con cifra, estado %r/%r, método %r o evidencia numérica en una celda no aplicable" % (rs, st, f.get("method_id")))
    if run_geometry:
        r1 = unica("r1_summary", "r1", cell_id=cid)
        if r1 is not None:
            na("r1", r1.get("computation_status") == "not_applicable" and r1.get("reason_code") == MOTIVO_NA and r1.get("n_components") is None
               and not any(_filas(rows, t, cell_id=cid) for t in ("r1_components", "r1_vertices", "r1_edges"))
               and not _filas(rows, "convergence_result", quantity_id="R1:" + cid),
               "R1 de una celda no aplicable con estado, motivo o geometría distintos del contrato")
        sec = _filas(rows, "r2_sections", cell_id=cid)
        cnt = Counter(x.get("section_id") for x in sec)
        for k in sorted(set(cnt) - set(C["secciones"]), key=str):
            parte("r2:%s" % k, "id_inesperado", "section_id fuera de paper2b.sections.SECTIONS")
        for s in C["secciones"]:
            fs = [x for x in sec if x.get("section_id") == s]
            if len(fs) != 1:
                parte("r2:" + s, "ausente" if not fs else "duplicada", "%d filas" % len(fs))
                continue
            # justificada por la NO APLICABILIDAD DE LA CELDA (no por la trayectoria: sin barras no se evalúa sections._path)
            na("r2:" + s, fs[0].get("computation_status") == "not_applicable" and fs[0].get("reason_code") == "CELL_NOT_COMPLETE"
               and fs[0].get("n_roots_by_section") is None and not _filas(rows, "r2_roots", cell_id=cid, section_id=s),
               "sección R2 de una celda no aplicable con estado, motivo o raíces distintos del contrato")
    defect = [p["estado"] for p in partes.values() if p["estado"] in RULES.DEFECTUOSOS]
    return {"estado": "invalida" if defect else "no_aplicable", "motivo_celda": MOTIVO_NA, "partes": partes, "motivos": motivos, "n_partes": len(partes)}
