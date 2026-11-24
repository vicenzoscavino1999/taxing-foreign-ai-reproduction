"""Margen de robustez respecto del soporte declarado (diseño §7.9.8; DOMINIOS_Y_FORMULAS.md; DI-07/DI-07.R).

r*_B = inf{r >= 1 : la afirmación deja de sostenerse sobre S_B(r) x S_-B}, por dirección y parámetro.
Expansión: aritmética [c - r h, U] (inferior) o [L, c + r h] (superior); logarítmica sobre log(L), log(U).
Estados: breakdown_found; theoretical_boundary_no_breakdown (rho superior RHO_UPPER_S4, factor 1; rho inferior
RHO_ZERO_LIMIT, factor 7/3); admissibility_boundary_no_breakdown (borde de restricción); declared_ladder_exhausted_
no_breakdown (escalera eta_H); not_applicable_support_gap (eta_w micro-superior y macro-inferior entran en (0.20,0.40));
not_applicable_baseline_inconclusive; not_applicable_not_identified (chi_r, MOMENT_NOT_IDENTIFIED); incomplete_search
(búsqueda no terminada o sin cobertura suficiente; nunca se presenta como robustez); no_solution (fallo del solver).
domain_exhausted_no_breakdown solo con cobertura de TODO el dominio pertinente: no se emite por tocar un borde.
Sensibilidad reducida de Q (§7.9.8.2-bis): m_Q en [0,1], común global (primaria) o por país; nunca por celda.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from .claims import EPS_ECON

STATUS_TO_COMPUTATION = {
    "breakdown_found": "complete", "domain_exhausted_no_breakdown": "complete",
    "declared_ladder_exhausted_no_breakdown": "complete", "theoretical_boundary_no_breakdown": "complete",
    "admissibility_boundary_no_breakdown": "complete", "not_applicable_baseline_inconclusive": "not_applicable",
    "not_applicable_support_gap": "not_applicable", "not_applicable_not_identified": "not_applicable",
    "no_solution": "failed", "incomplete_search": "incomplete"}


@dataclass
class Breakdown:
    block_id: str
    parameter_id: str | None
    component_id: str | None
    direction: str
    support_low: float
    support_high: float
    scale_kind: str
    status: str = "incomplete_search"
    r_critical: float | None = None
    expansion_factor_r: float = 1.0
    reached_expansion_factor: float | None = None
    domain_edge_reached: str = "ninguno"
    boundary_kind: str = "none"
    boundary_value: float | None = None
    evaluated_domain: str = ""
    theoretical_domain: str = ""
    witnesses: list = field(default_factory=list)
    n_components: int | None = None
    joint: bool = False
    reason: str | None = None
    bracket: tuple | None = None       # (r_sostiene, r_condición] demostrados cuando el umbral no se localizó

    @property
    def computation_status(self) -> str:
        return STATUS_TO_COMPUTATION[self.status]


def expanded(lo: float, hi: float, direction: str, r: float, scale: str) -> tuple[float, float]:
    if scale == "logarithmic":
        a, b = math.log(lo), math.log(hi)
        c, h = (a + b) / 2, (b - a) / 2
        return (math.exp(c - r * h), hi) if direction == "inferior" else (lo, math.exp(c + r * h))
    c, h = (lo + hi) / 2, (hi - lo) / 2
    return (c - r * h, hi) if direction == "inferior" else (lo, c + r * h)


def r_for_endpoint(lo: float, hi: float, direction: str, target: float, scale: str) -> float:
    if scale == "logarithmic":
        a, b = math.log(lo), math.log(hi)
        c, h = (a + b) / 2, (b - a) / 2
        t = math.log(target)
        return (c - t) / h if direction == "inferior" else (t - c) / h
    c, h = (lo + hi) / 2, (hi - lo) / 2
    return (c - target) / h if direction == "inferior" else (target - c) / h


# Fronteras teóricas abiertas (no evaluables como punto interior): (parámetro, dirección) -> (valor, edge, reason)
THEORETICAL_EDGES = {("rho", "inferior"): (0.0, "rho_zero_limit", "RHO_ZERO_LIMIT"),
                     ("a", "inferior"): (1.0, "a_gt1", "A_GT1_OPEN"),
                     ("kappa_tilde", "inferior"): (0.0, "kappa_positive", "KAPPA_POSITIVE_OPEN")}


def search(block_id, parameter_id, component_id, direction, lo, hi, scale, claim_holds, *, ladder, bisect_tol=1e-3,
           baseline_status="verified", joint=False, admissible=None) -> Breakdown:
    """claim_holds(interval) -> 'holds' | 'fails' | 'inadmissible' | 'incomplete' (+ testigos)."""
    b = Breakdown(block_id, parameter_id, component_id, direction, lo, hi,
                  "logaritmica" if scale == "logarithmic" else "aritmetica", joint=joint)
    b.theoretical_domain = _theoretical(parameter_id)
    if baseline_status == "inconclusive":
        b.status, b.reason = "not_applicable_baseline_inconclusive", "BASELINE_INCONCLUSIVE"
        return b
    if baseline_status != "verified":
        b.status, b.reason = "incomplete_search", "BASELINE_NOT_EVALUATED"
        return b
    if parameter_id == "chi_r":
        b.status, b.reason = "not_applicable_not_identified", "MOMENT_NOT_IDENTIFIED"
        return b
    if parameter_id == "eta_w" and ((component_id == "micro" and direction == "superior")
                                    or (component_id == "macro" and direction == "inferior")):
        b.status, b.reason = "not_applicable_support_gap", "SUPPORT_GAP_ETA_W"
        return b
    if parameter_id == "rho" and direction == "superior":
        b.status, b.reason = "theoretical_boundary_no_breakdown", "RHO_UPPER_S4"
        b.domain_edge_reached, b.boundary_kind, b.boundary_value = "rho_upper_S4", "theoretical", 1.0
        b.reached_expansion_factor, b.expansion_factor_r = 1.0, 1.0
        b.evaluated_domain = f"[{lo},{hi}] (primario; hi=1 es la frontera S4)"
        return b
    if not hi > lo:
        # semiamplitud nula: el factor r sobre la semiamplitud no define expansión (soporte singleton)
        b.status, b.reason = "incomplete_search", "ZERO_SEMIWIDTH_NO_EXPANSION_METRIC"
        b.evaluated_domain = f"[{lo},{hi}] (singleton)"
        return b
    edge = THEORETICAL_EDGES.get((parameter_id, direction))
    r_edge = r_for_endpoint(lo, hi, direction, edge[0], scale) if edge and not (scale == "logarithmic" and edge[0] <= 0) else math.inf
    last_ok = 1.0

    def at(x):
        return claim_holds(expanded(lo, hi, direction, x, scale))

    for r in ladder:
        if edge and r >= r_edge:
            break
        res, wit = at(r)
        if res == "holds":
            last_ok = r
            continue
        if res == "incomplete":
            b.status, b.reason = "incomplete_search", "EVALUATION_INCOMPLETE"
            b.reached_expansion_factor = last_ok
            b.evaluated_domain = _dom(lo, hi, direction, last_ok, scale) + f"; r={r!r} sin resolver"
            return b
        if res == "inadmissible":
            return _admissibility(b, at, lo, hi, direction, scale, last_ok, r, wit, bisect_tol)
        return _breakdown(b, at, lo, hi, direction, scale, last_ok, r, wit, bisect_tol)
    if edge and r_edge < math.inf:
        # rho inferior hasta 7/3, a y kappa hasta su frontera abierta: se aproxima lateralmente sin evaluar el borde
        approach = [r_edge * (1 - 10.0 ** (-k)) for k in (2, 3, 4)]
        for r in approach:
            if r <= last_ok:
                continue
            res, wit = at(r)
            if res == "fails":
                return _breakdown(b, at, lo, hi, direction, scale, last_ok, r, wit, bisect_tol)
            if res != "holds":
                b.status, b.reason = "incomplete_search", "LATERAL_APPROACH_INCOMPLETE"
                b.reached_expansion_factor = last_ok
                b.evaluated_domain = _dom(lo, hi, direction, last_ok, scale) + f"; aproximación r={r!r}: {res}"
                return b
            last_ok = r
        b.status, b.reason = "theoretical_boundary_no_breakdown", edge[2]
        b.domain_edge_reached, b.boundary_kind, b.boundary_value = edge[1], "theoretical", edge[0]
        b.reached_expansion_factor = r_edge
        b.expansion_factor_r = r_edge
        b.evaluated_domain = _dom(lo, hi, direction, last_ok, scale) + " + aproximación lateral a la frontera abierta"
        return b
    b.status, b.reason = "incomplete_search", "EXPANSION_LADDER_LIMIT_WITHOUT_BOUNDARY"
    b.reached_expansion_factor = last_ok
    b.expansion_factor_r = last_ok
    b.evaluated_domain = _dom(lo, hi, direction, last_ok, scale)
    return b


def _bisect3(evaluate, lo, hi, tol):
    """Bisección con TRES estados. Invariante: en `lo` la afirmación se sostiene (demostrado) y en `hi` se cumple la
    condición buscada (demostrado). evaluate(x) -> ('ok' | 'hit' | 'unknown', dato). Una evaluación desconocida NO
    confirma ningún lado: la bisección se detiene y devuelve el intervalo demostrado. -> (lo, hi, resuelto, dato_en_hi)."""
    data = None
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        state, d = evaluate(mid)
        if state == "ok":
            lo = mid
        elif state == "hit":
            hi, data = mid, d
        else:
            return lo, hi, False, data
    return lo, hi, True, data


def _breakdown(b, at, lo, hi, direction, scale, r_ok, r_fail, wit, tol):
    """Falla demostrada en r_fail con testigo; se sostiene en r_ok. Localiza r* solo si toda evaluación intermedia es
    'holds' o 'fails'; si alguna queda sin resolver, el umbral queda ACOTADO en (r_lo, r_hi] pero no localizado."""
    def ev(x):
        rr, ww = at(x)
        return ("ok" if rr == "holds" else ("hit" if rr == "fails" else "unknown")), ww
    r_lo, r_hi, resolved, w = _bisect3(ev, r_ok, r_fail, tol)
    b.witnesses = (w if w is not None else wit) or []
    b.n_components = 1 if b.witnesses else None
    if resolved and b.witnesses:
        b.status = "breakdown_found"
        b.r_critical = b.expansion_factor_r = b.reached_expansion_factor = r_hi
        b.evaluated_domain = _dom(lo, hi, direction, r_hi, scale)
        return b
    b.status = "incomplete_search"
    b.reason = "BREAKDOWN_THRESHOLD_NOT_LOCALIZED" if b.witnesses else "WITNESS_MISSING"
    b.r_critical = None
    b.reached_expansion_factor = b.expansion_factor_r = r_lo
    b.bracket = (r_lo, r_hi)
    b.evaluated_domain = (_dom(lo, hi, direction, r_lo, scale) + f"; umbral acotado en ({r_lo!r}, {r_hi!r}]"
                          + ("; testigo de fallo demostrado en r=%r" % r_hi if b.witnesses else "")
                          + "; evaluación intermedia sin resolver")
    return b


def _admissibility(b, at, lo, hi, direction, scale, r_ok, r_bad, wit, tol):
    """En r_bad el soporte ampliado es inadmisible; en r_ok la afirmación se sostiene. Si en el camino aparece una falla,
    la búsqueda pasa a localizar el quiebre; una evaluación sin resolver deja el borde sin localizar."""
    found = {}

    def ev(x):
        rr, ww = at(x)
        if rr == "fails":
            found.setdefault("fail", (x, ww))
        return ("ok" if rr == "holds" else ("hit" if rr == "inadmissible" else "unknown")), ww
    r_lo, r_hi, resolved, _ = _bisect3(ev, r_ok, r_bad, tol)
    if "fail" in found:
        x, ww = found["fail"]
        return _breakdown(b, at, lo, hi, direction, scale, r_lo, x, ww, tol)
    if not resolved:
        b.status, b.reason = "incomplete_search", "ADMISSIBILITY_BOUNDARY_NOT_LOCALIZED"
        b.reached_expansion_factor = b.expansion_factor_r = r_lo
        b.bracket = (r_lo, r_hi)
        b.evaluated_domain = _dom(lo, hi, direction, r_lo, scale) + f"; borde de admisibilidad en ({r_lo!r}, {r_hi!r}] sin localizar"
        return b
    b.status, b.reason = "admissibility_boundary_no_breakdown", "ADMISSIBILITY_BOUNDARY"
    b.domain_edge_reached = wit if isinstance(wit, str) else "lambda_pi"
    b.boundary_kind = "admissibility"
    b.reached_expansion_factor = b.expansion_factor_r = r_lo
    b.boundary_value = expanded(lo, hi, direction, r_lo, scale)[0 if direction == "inferior" else 1]
    b.evaluated_domain = _dom(lo, hi, direction, r_lo, scale) + f"; inadmisible desde r<={r_hi!r}"
    return b


def ladder_search(block_id, parameter_id, levels, claim_holds, baseline_status="verified") -> Breakdown:
    """Escalera discreta anidada (eta_H: H0 subset H1 subset H2). Agotarla NO es agotar el dominio."""
    b = Breakdown(block_id, parameter_id, None, "superior", min(levels[0]), max(levels[0]), "escalera_discreta")
    b.theoretical_domain = "eta_H > -1 (sin cota superior económica declarada)"
    if baseline_status == "inconclusive":
        b.status, b.reason = "not_applicable_baseline_inconclusive", "BASELINE_INCONCLUSIVE"
        return b
    if baseline_status != "verified":
        b.status, b.reason = "incomplete_search", "BASELINE_NOT_EVALUATED"
        return b
    for k, level in enumerate(levels[1:], start=1):
        res, wit = claim_holds(tuple(level))
        if res == "fails":
            b.status, b.r_critical, b.expansion_factor_r, b.reached_expansion_factor = "breakdown_found", float(k), float(k), float(k)
            b.witnesses = wit or []
            b.n_components = 1 if b.witnesses else None
            b.evaluated_domain = "escalera H%d = %s" % (k, list(level))
            return b
        if res != "holds":
            b.status, b.reason = "incomplete_search", "LADDER_EVALUATION_INCOMPLETE"
            return b
    b.status, b.reason = "declared_ladder_exhausted_no_breakdown", "ETA_H_LADDER_EXHAUSTED"
    b.expansion_factor_r = b.reached_expansion_factor = float(len(levels) - 1)
    b.evaluated_domain = "escalera H%d = %s" % (len(levels) - 1, list(levels[-1]))
    return b


def _dom(lo, hi, direction, r, scale):
    a, b = expanded(lo, hi, direction, r, scale)
    return f"[{a!r},{b!r}] (r={r!r}, {scale})"


def _theoretical(pid):
    return {"rho": "S4: 0 <= rho <= 1 (rho=0 límite S18)", "a": "a > 1", "kappa_tilde": "kappa_tilde > 0; q_pot < 1",
            "eta_w": "sin cota teórica; admisibilidad lambda > 0", "pi_iva": "s_T_marg >= 0; s_Pi_marg > 0",
            "pi_otros_productos": "s_T_marg >= 0; s_Pi_marg > 0", "pi_produccion": "s_T_marg >= 0; s_Pi_marg > 0",
            "eta_H": "eta_H > -1", "chi_r": "rama no identificada"}.get(pid or "", "admisibilidad conjunta")


# ------------------------------------------------------------------------------ sensibilidad reducida de Q
@dataclass
class QSensitivity:
    status: str
    m_Q_critical: float | None
    witness: dict | None
    reason: str | None = None

    @property
    def computation_status(self) -> str:
        return {"breakdown_found": "complete", "scale_range_exhausted_no_breakdown": "complete",
                "not_applicable_baseline_inconclusive": "not_applicable", "no_solution": "failed",
                "incomplete_search": "incomplete"}[self.status]


def q_sensitivity(verdict: str, universe, eps: float = EPS_ECON) -> QSensitivity:
    """universe: iterable de dicts por omega-estado con C2, err, lambda, gain, D (=DME_gAI) y Qs (requerimientos de la capa).

    G_best(m) = C2 - min_c (m Q_c + D)/(lambda y) es creciente al reducir m. Una infactibilidad robusta deja de
    sostenerse cuando algún punto alcanza G_best > -eps: m_w = ((C2 + err + eps) lambda y - D)/min Q; m* = max_w m_w
    (supremo del conjunto de fallo [0, m*), no alcanzado). Reducir Q nunca rompe una factibilidad robusta.
    """
    if verdict == "inconclusive":
        return QSensitivity("not_applicable_baseline_inconclusive", None, None, "BASELINE_INCONCLUSIVE")
    if verdict not in ("robust_infeasible", "robust_feasible"):
        return QSensitivity("incomplete_search", None, None, "BASELINE_NOT_EVALUATED")
    if verdict == "robust_feasible":
        return QSensitivity("scale_range_exhausted_no_breakdown", None, None, None)
    best, wit = -math.inf, None
    for u in universe:
        qmin = min(u["Qs"])
        if not qmin > 0:
            return QSensitivity("no_solution", None, None, "QMIN_NONPOSITIVE")
        m = ((u["C2"] + u["err"] + eps) * u["lambda"] * u["gain"] - u["D"]) / qmin
        # desempate determinista por clave (independiente del orden de iteración / de la partición en unidades)
        if m > best or (m == best and wit is not None and tuple(u["key"]) < tuple(wit["key"])):
            best, wit = m, u
    if best is -math.inf:
        return QSensitivity("incomplete_search", None, None, "EMPTY_UNIVERSE")
    if best <= 0.0:
        return QSensitivity("scale_range_exhausted_no_breakdown", None, None, None)
    if best >= 1.0:
        return QSensitivity("no_solution", None, wit, "BASELINE_CONTRADICTION_M_GE_1")
    return QSensitivity("breakdown_found", best, wit, None)


def q_sensitivity_reduced(verdict: str, agg: dict | None, eps: float = EPS_ECON) -> QSensitivity:
    """Mismo resultado que q_sensitivity a partir del resumen agregado de unidades {best, wit, bad, n}: el máximo de
    m_w es asociativo (desempate por clave) y 'algún Q_min <= 0' es un O lógico."""
    if verdict == "inconclusive":
        return QSensitivity("not_applicable_baseline_inconclusive", None, None, "BASELINE_INCONCLUSIVE")
    if verdict not in ("robust_infeasible", "robust_feasible"):
        return QSensitivity("incomplete_search", None, None, "BASELINE_NOT_EVALUATED")
    if verdict == "robust_feasible":
        return QSensitivity("scale_range_exhausted_no_breakdown", None, None, None)
    if agg is None or agg["n"] == 0:
        return QSensitivity("incomplete_search", None, None, "EMPTY_UNIVERSE")
    if agg["bad"]:
        return QSensitivity("no_solution", None, None, "QMIN_NONPOSITIVE")
    best, wit = agg["best"], agg["wit"]
    if best is None:
        return QSensitivity("incomplete_search", None, None, "EMPTY_UNIVERSE")
    wit = dict(wit, key=tuple(wit["key"]))
    if best <= 0.0:
        return QSensitivity("scale_range_exhausted_no_breakdown", None, None, None)
    if best >= 1.0:
        return QSensitivity("no_solution", None, wit, "BASELINE_CONTRADICTION_M_GE_1")
    return QSensitivity("breakdown_found", best, wit, None)
