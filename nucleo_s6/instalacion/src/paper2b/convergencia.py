"""Filas `convergence_result` CORREGIDAS para inversiones endógenas, G y clasificación (CIERRE CANDIDATO 3.7, NO OFICIAL).

Sustituye a codigo/convergencia_candidata.py de la entrega anterior, cuyo defecto (línea 55) daba `status = pass` con
`change_bound = null` para una raíz (n_scalar_solutions >= 1): la tabla exige change_bound <= tolerance para `pass` y el
validador real (paper2b.rules.Checker.audit) no puede aceptar un `pass` sin cota.

Reglas (catálogo integracion_s4/.../catalogo_contratos.json, tabla convergence_result; rules.py:553-559; DI-08; §19.6
del antecedente PLAN_DISENO_v2_2_30.md incorporado por DI-08):
- `pass` exige: cobertura completa del dominio pertinente, change_bound NO nulo, finito y <= tolerancia, 0 cambios de
  veredicto y topología antes = después. Cualquier evidencia ausente, inválida o incompleta da `incomplete` (o `fail`
  si la evidencia es válida pero la cota supera la tolerancia). Nunca `pass` por omisión.
- Respaldo por COTA CERTIFICADA (no por refinamiento de malla): se usa la convención que ya usa run.py para C2
  (líneas 536-546): level_before = 0, level_after = 1, method_id que dice «certified_…», value_before/value_after =
  extremos del intervalo certificado y change_bound = su anchura (cota del error). No se inventan niveles de malla.
- RAÍCES (φ total y demás inversiones de punto fijo): el error es de LOCALIZACIÓN en la coordenada: anchura del
  intervalo aislante certificado [lo, hi] de cada raíz (ScalarRoot.lo/hi; raices.Root1D). El RESIDUO |C2(x) − K1| NO es
  un error de coordenada y nunca se usa como change_bound. Tolerancia: la de raíces declarada (endogenous_xtol, T2_root).
  Topología = n_raíces + n_intervalos (entero, como exige el catálogo); un intervalo de raíces exige cota en sus dos extremos.
- AUSENCIA de raíces: change_bound = 0 solo con inexistencia CERTIFICADA sobre TODO el dominio declarado
  (coverage == "certified", no_solution, dominio cubierto = [lo, hi] completo); si no, `incomplete`.
- G = C2 − K1 (misma ω, misma celda): |G − Ĝ| <= err(C2) + err(K1). err(C2) = numerical_error certificado del techo
  (capture_ceiling, error_kind certified_bound); err(K1) = cota de redondeo de la forma cerrada (T1 relativa:
  8 ulp·|K1|, documentada). verdict_changes = 1 si [G − cota, G + cota] contiene ±ε (la clasificación podría cambiar).
  Tolerancia T2_G = 1e-4 (§19.6, T3). C2 sin cota certificada -> `incomplete`.
- result_ref = "<tabla>:<PK JSON canónico>" que debe resolver una fila B (la comprueba el validador real).
"""
from __future__ import annotations

import json
import math

T2_G = 1e-4
COLUMNAS = ("quantity_id", "level_before", "level_after", "result_ref", "method_id", "value_before", "value_after",
            "change_bound", "tolerance", "unit", "topology_before", "topology_after", "verdict_changes", "coverage_complete",
            "status", "evidence_ref")
EPS_ECON = 0.01
ULP_REL_K1 = 8 * 2.0 ** -52          # cota de redondeo relativa de la forma cerrada K1 = N/(λ y) (T1; pocas operaciones)


def ref(tabla: str, pk: dict) -> str:
    return tabla + ":" + json.dumps(pk, sort_keys=True, separators=(",", ":"))


def _finito(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _raiz(r):
    """Normaliza una raíz al formato (valor, lo, hi, localizada) SEGÚN EL PRODUCTOR REAL.

    Productor real (paper2b.inversion._from_search): ScalarRoot(value, bracket_low, bracket_high, residual, converged,
    kind), con bracket_low/bracket_high = intervalo aislante de raices.Root1D (lo, hi) y converged = «intervalo aislante
    DEMOSTRADO de ancho <= xtol» (raices.Root1D.converged: localización, no residuo pequeño). También se acepta la tupla
    explícita (valor, lo, hi, localizada) de las pruebas. Cualquier otra forma (objeto sin bracket_*, tupla de 3 sin la
    marca de localización) devuelve localizada = None: la fila no se aprueba (nunca se inventa un intervalo)."""
    if isinstance(r, (tuple, list)):
        if len(r) >= 4 and isinstance(r[3], bool):
            return r[0], r[1], r[2], r[3]
        return (r[0] if r else None), None, None, None
    if hasattr(r, "bracket_low") and hasattr(r, "bracket_high"):
        conv = getattr(r, "converged", None)
        return getattr(r, "value", None), r.bracket_low, r.bracket_high, (conv if isinstance(conv, bool) else None)
    return getattr(r, "value", None), None, None, None


def fila_raices(quantity_id: str, result_ref: str, *, raices, intervalos, coverage: str, computation_status: str,
                no_solution: bool, dominio, dominio_cubierto, tolerancia: float, unidad: str, evidence_ref: str | None) -> dict:
    """raices: lista de paper2b.inversion.ScalarRoot (productor real) o tuplas (valor, lo, hi, localizada); intervalos:
    lista de (lo, hi, ...) de soluciones en intervalo. dominio = (a, b) declarado; dominio_cubierto = (a', b')
    efectivamente certificado.

    Raíz aprobable solo con intervalo aislante [lo, hi] FINITO, lo <= valor <= hi y localización DEMOSTRADA
    (converged = True). Sin localización demostrada -> incomplete (aunque el residuo sea pequeño); límites ausentes,
    no finitos o incoherentes -> incomplete; localizada pero hi - lo > tolerancia -> fail."""
    base = {"quantity_id": quantity_id, "level_before": 0, "level_after": 1, "result_ref": result_ref, "unit": unidad,
            "tolerance": tolerancia, "verdict_changes": 0, "evidence_ref": evidence_ref}
    rs4 = [_raiz(r) for r in (raices or [])]
    rs = [t[:3] for t in rs4]
    iv = [tuple(x[:2]) for x in (intervalos or [])]
    topo = len(rs) + len(iv)          # entero (catálogo: topology_* es int): nº de raíces + intervalos de raíces
    cubre = (coverage == "certified" and dominio_cubierto is not None and dominio is not None
             and dominio_cubierto[0] <= dominio[0] and dominio_cubierto[1] >= dominio[1])
    if computation_status != "complete" or not cubre:
        return dict(base, method_id="certified_root_search", value_before=None, value_after=None, change_bound=None,
                    topology_before=topo, topology_after=topo, coverage_complete=False, status="incomplete",
                    motivo="COBERTURA_NO_CERTIFICADA_EN_TODO_EL_DOMINIO" if computation_status == "complete" else "CALCULO_INCOMPLETO")
    if not rs and not iv:
        if not no_solution:
            return dict(base, method_id="certified_root_search", value_before=None, value_after=None, change_bound=None,
                        topology_before=topo, topology_after=topo, coverage_complete=True, status="incomplete",
                        motivo="SIN_RAICES_SIN_INEXISTENCIA_DEMOSTRADA")
        return dict(base, method_id="certified_root_search:absence", value_before=None, value_after=None, change_bound=0.0,
                    topology_before=topo, topology_after=topo, coverage_complete=True, status="pass",
                    motivo="INEXISTENCIA_CERTIFICADA_EN_TODO_EL_DOMINIO")
    anchos = []
    for v, lo, hi, loc in rs4:
        if not (_finito(lo) and _finito(hi) and lo <= hi and _finito(v) and lo <= v <= hi):
            return dict(base, method_id="certified_root_search", value_before=None, value_after=None, change_bound=None,
                        topology_before=topo, topology_after=topo, coverage_complete=True, status="incomplete",
                        motivo="RAIZ_SIN_INTERVALO_AISLANTE_CERTIFICADO")
        if loc is not True:
            return dict(base, method_id="certified_root_search", value_before=None, value_after=None, change_bound=None,
                        topology_before=topo, topology_after=topo, coverage_complete=True, status="incomplete",
                        motivo="RAIZ_SIN_LOCALIZACION_DEMOSTRADA")
        anchos.append(hi - lo)
    for lo, hi in iv:
        if not (_finito(lo) and _finito(hi) and lo <= hi):
            return dict(base, method_id="certified_root_search", value_before=None, value_after=None, change_bound=None,
                        topology_before=topo, topology_after=topo, coverage_complete=True, status="incomplete",
                        motivo="INTERVALO_DE_RAICES_SIN_EXTREMOS")
    cb = max(anchos) if anchos else 0.0
    peor = max(rs, key=lambda t: t[2] - t[1]) if rs else (None, None, None)
    return dict(base, method_id="certified_root_search:isolating_interval", value_before=peor[1], value_after=peor[2],
                change_bound=cb, topology_before=topo, topology_after=topo, coverage_complete=True,
                status="pass" if cb <= tolerancia else "fail",
                motivo=None if cb <= tolerancia else "LOCALIZACION_MAYOR_QUE_LA_TOLERANCIA")


def fila_G(cell_id: str, *, C2, err_C2, error_kind: str, ceiling_status: str, K1, evidence_ref: str | None,
           tolerancia: float = T2_G, eps: float = EPS_ECON) -> dict:
    base = {"quantity_id": "G:" + cell_id, "level_before": 0, "level_after": 1, "result_ref": ref("confrontation_result", {"cell_id": cell_id}),
            "unit": "share", "tolerance": tolerancia, "topology_before": None, "topology_after": None, "evidence_ref": evidence_ref}
    if not (_finito(C2) and _finito(K1)) or ceiling_status != "complete" or error_kind != "certified_bound" or not (_finito(err_C2) and err_C2 >= 0):
        return dict(base, method_id="certified_bound_C2_closed_form_K1", value_before=None, value_after=None, change_bound=None,
                    verdict_changes=0, coverage_complete=False, status="incomplete", motivo="C2_SIN_COTA_CERTIFICADA_O_K1_AUSENTE")
    G = C2 - K1
    cb = err_C2 + ULP_REL_K1 * abs(K1)
    cambia = int(any(G - cb <= t <= G + cb for t in (-eps, eps)))
    return dict(base, method_id="certified_bound_C2_closed_form_K1", value_before=G - cb, value_after=G + cb, change_bound=cb,
                verdict_changes=cambia, coverage_complete=True,
                status="pass" if cb <= tolerancia and not cambia else "fail",
                motivo=None if (cb <= tolerancia and not cambia) else ("VEREDICTO_PUEDE_CAMBIAR" if cambia else "COTA_MAYOR_QUE_T2_G"))


def fila_clasificacion(claim_id: str, *, veredicto: str, sup_upper, inf_lower, universo_completo: bool, evidence_ref: str | None,
                       eps: float = EPS_ECON) -> dict:
    """Clasificación de una afirmación: tolerancia CERO cambios (§19.6). verified/robust_* exige universo completo y que
    las cotas certificadas queden del mismo lado de ±ε; inconclusive por testigos no tiene cifra que converger."""
    # catálogo: tolerance es `positive` y topology_* `int`: el requisito de CERO cambios de clasificación se expresa
    # con verdict_changes = 0 y change_bound = 0; la tolerancia de las cotas que respaldan la clasificación es T2_G
    base = {"quantity_id": "CLASS:" + claim_id, "level_before": 0, "level_after": 1, "result_ref": ref("claims", {"claim_id": claim_id}),
            "unit": "label", "tolerance": T2_G, "topology_before": None, "topology_after": None, "evidence_ref": evidence_ref,
            "method_id": "certified_classification"}
    if not universo_completo or veredicto not in ("robust_infeasible", "robust_feasible", "inconclusive"):
        return dict(base, value_before=None, value_after=None, change_bound=None, verdict_changes=0, coverage_complete=False,
                    status="incomplete", motivo="UNIVERSO_INCOMPLETO_O_VEREDICTO_DESCONOCIDO")
    if veredicto == "robust_infeasible":
        ok = _finito(sup_upper) and sup_upper <= -eps
    elif veredicto == "robust_feasible":
        ok = _finito(inf_lower) and inf_lower >= eps
    else:
        ok = True                                   # inconclusa por testigos verificados: no depende de una cifra
    return dict(base, value_before=sup_upper, value_after=inf_lower, change_bound=0 if ok else None, verdict_changes=0 if ok else 1,
                coverage_complete=True, status="pass" if ok else "fail", motivo=None if ok else "COTA_DEL_LADO_EQUIVOCADO_DE_EPS")
