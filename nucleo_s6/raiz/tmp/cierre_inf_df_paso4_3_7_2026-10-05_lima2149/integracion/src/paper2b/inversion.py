"""Inversiones del diseño §7.9: cuatro despejes cerrados y dos problemas endógenos (punto fijo).

- lambda_required (29) = N/(C2 y); gain_required (30) = N/(C2 lambda); capture_required (7.9.3) = K1;
- phi_partial (28) = log(tau_f s + 1 - tau_f)/log(1 - tau_f), con tau_f y umbral PREDECLARADOS;
- external_factor (7.9.4): C2(f) = K1 sobre f en [0,1] recalculando adopción; exige mapeo identificado;
- phi_total (7.9.5b): C2(phi) = K1 sobre phi en [0,1] recalculando todos los canales de phi.
N = Q + DME_gAI. Estados del contrato: computed/no_feasible_solution/outside_support/not_identified/
undefined_denominator/failed/incomplete. Los valores algebraicos fuera del soporte no se truncan.
Las raíces endógenas: todas las aisladas; una identidad solo con prueba (p. ej. menú d: C2 no depende de phi).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from .numeric import brent, golden_max

INVERSIONS = ("capture_required", "external_factor", "gain_required", "lambda_required", "phi_partial", "phi_total")
STATUS_TO_COMPUTATION = {"computed": "complete", "outside_support": "complete", "no_feasible_solution": "complete",
                         "not_identified": "not_applicable", "undefined_denominator": "excluded", "failed": "failed",
                         "incomplete": "incomplete"}
EQUATION = {"lambda_required": "EQ29", "gain_required": "EQ30", "capture_required": "EQ7_9_3",
            "external_factor": "EQ7_9_4", "phi_partial": "EQ28", "phi_total": "EQ7_9_5b"}
VALUE_FIELD = {"lambda_required": "lambda_pi_required", "gain_required": "delta_y_required",
               "capture_required": "C_2_required", "external_factor": "external_factor_required",
               "phi_partial": "phi_critical_partial", "phi_total": "phi_critical_total"}


@dataclass
class ScalarRoot:
    value: float
    bracket_low: float
    bracket_high: float
    residual: float
    converged: bool
    kind: str = "crossing"


@dataclass
class Inversion:
    inversion_id: str
    value: float | None = None
    result_status: str = "incomplete"
    reason: str | None = None
    outside_support: bool = False
    no_solution: bool = False
    corner_binding: bool = False
    kink_adjacent: bool = False
    admissibility_violated: bool = False
    fixed_point_converged: bool | None = None
    roots: list = field(default_factory=list)
    intervals: list = field(default_factory=list)
    method_id: str = "algebraic_closed_form"
    target_value: float = 0.0
    target_unit: str = "share"
    tau_f_given: float | None = None
    supplier_share_target: float | None = None
    definition: str = ""
    coverage: str = "not_applicable"      # certified | not_certified | not_applicable (algebraicas)
    diagnostics: dict = field(default_factory=dict)

    @property
    def computation_status(self) -> str:
        return STATUS_TO_COMPUTATION[self.result_status]


def _in(v, support):
    lo, hi = support
    return lo <= v <= hi


def algebraic(N: float, C2: float | None, lam: float | None, y: float | None, K1: float | None,
              supports: dict) -> list[Inversion]:
    """Tres despejes cerrados de G=0. supports: rangos declarados/derivados de lambda, gain_share y C2."""
    out = []
    # lambda_required
    inv = Inversion("lambda_required", definition="lambda tal que G = C2 - N/(lambda y) = 0 (29)")
    if C2 is None or y is None or C2 * y == 0.0:
        inv.result_status, inv.reason = "undefined_denominator", "C2_OR_GAIN_UNDEFINED_OR_ZERO"
    else:
        inv.value = N / (C2 * y)
        if not inv.value > 0:
            inv.result_status, inv.no_solution, inv.admissibility_violated = "no_feasible_solution", True, True
            inv.reason = "LAMBDA_REQUIRED_NONPOSITIVE"
        elif not _in(inv.value, supports["lambda"]):
            inv.result_status, inv.outside_support = "outside_support", True
        else:
            inv.result_status = "computed"
    out.append(inv)
    inv = Inversion("gain_required", definition="gain_share tal que G = 0 (30)", target_unit="share")
    if C2 is None or lam is None or C2 * lam == 0.0:
        inv.result_status, inv.reason = "undefined_denominator", "C2_OR_LAMBDA_UNDEFINED_OR_ZERO"
    else:
        inv.value = N / (C2 * lam)
        if not inv.value > 0:
            inv.result_status, inv.no_solution = "no_feasible_solution", True
            inv.reason = "GAIN_REQUIRED_NONPOSITIVE"
        elif not _in(inv.value, supports["gain_share"]):
            inv.result_status, inv.outside_support = "outside_support", True
        else:
            inv.result_status = "computed"
    out.append(inv)
    inv = Inversion("capture_required", definition="C2 requerido = K1 (7.9.3)")
    if K1 is None:
        inv.result_status, inv.reason = "undefined_denominator", "K1_UNDEFINED"
    else:
        inv.value = K1
        if C2 is not None and not _in(K1, supports["C2"]):
            inv.result_status, inv.outside_support = "outside_support", True
        else:
            inv.result_status = "computed"
    out.append(inv)
    return out


def phi_partial(tau_f: float | None, target: float | None) -> Inversion:
    inv = Inversion("phi_partial", definition="phi tal que s_P(tau_f, phi) = umbral declarado (28)",
                    tau_f_given=tau_f, supplier_share_target=target)
    if tau_f is None or target is None:
        inv.result_status, inv.reason = "not_identified", "TARGETS_NOT_PREDECLARED"
        return inv
    if not (0.0 < tau_f < 1.0):
        inv.result_status, inv.reason = "undefined_denominator", "TAU_F_NOT_IN_OPEN_UNIT"
        return inv
    arg = tau_f * target + 1.0 - tau_f
    if not arg > 0:
        inv.result_status, inv.reason = "undefined_denominator", "LOG_ARGUMENT_NONPOSITIVE"
        return inv
    inv.target_value = target
    inv.value = math.log(arg) / math.log(1.0 - tau_f)
    if not (0.0 <= inv.value <= 1.0):
        inv.result_status, inv.outside_support = "outside_support", True
    else:
        inv.result_status = "computed"
    return inv


def _from_search(inv: Inversion, rs, lo: float, hi: float) -> Inversion:
    """Traduce una búsqueda de raíces (raices.RootSearch) a los estados contractuales de la inversión.
    complete + raíces/intervalos -> computed; complete sin raíces -> no_feasible_solution (inexistencia DEMOSTRADA por
    cobertura certificada); incomplete -> incomplete con diagnósticos (las raíces halladas no se publican como filas)."""
    inv.coverage = rs.coverage
    inv.diagnostics = rs.diagnostics
    if rs.status == "failed":
        inv.result_status, inv.reason = "failed", rs.reason or "ROOT_SOLVER_FAILED"
        return inv
    if rs.status != "complete":
        inv.result_status, inv.reason = "incomplete", rs.reason
        inv.fixed_point_converged = None
        return inv
    inv.roots = [ScalarRoot(r.x, r.lo, r.hi, r.residual, r.converged, r.kind) for r in rs.roots]
    inv.intervals = [(a, b, True, True, 0.0) for a, b in _merge(rs.zero_intervals)]
    inv.fixed_point_converged = all(r.converged for r in inv.roots)
    if not inv.fixed_point_converged:
        inv.result_status, inv.reason = "incomplete", "ROOT_NOT_LOCALIZED_TO_TOLERANCE"
        inv.roots, inv.intervals = [], []
        return inv
    if inv.roots or inv.intervals:
        inv.result_status = "computed"
        if len(inv.roots) == 1 and not inv.intervals:
            inv.value = inv.roots[0].value
        inv.corner_binding = any(r.value in (lo, hi) for r in inv.roots)
    else:
        inv.result_status, inv.no_solution, inv.reason = "no_feasible_solution", True, "NO_ROOT_CERTIFIED_COVERAGE"
    return inv


def _merge(ivs):
    out = []
    for a, b in sorted(ivs):
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def _shift(ev, K1: float):
    """Evidencia de g = C2 - K1 a partir de la evidencia de C2 (rango desplazado; derivadas iguales)."""
    if ev is None:
        return None
    from .raices import shift_evidence
    return shift_evidence(ev, K1)


def endogenous(inversion_id: str, C2_of, K1: float | None, lo: float, hi: float, *, n: int = 16,
               xtol: float = 1e-12, tol_residual: float = 1e-9, invariance_proof: str | None = None,
               constant_value: float | None = None, evidence=None) -> Inversion:
    """Raíces de C2(x) - K1 = 0 en [lo, hi] recalculando el modelo en cada x.

    invariance_proof: el llamador DEMUESTRA que C2 no depende de x (p. ej. menú d y phi): igualdad exacta => intervalo
    [lo, hi]; si no, inexistencia demostrada. En otro caso la búsqueda es certificada solo con `evidence` (encierro de
    C2(x)); sin ella el resultado es `incomplete` aunque aparezcan raíces."""
    inv = Inversion(inversion_id, method_id="fixed_point_bracket_bisection",
                    definition=("C2(x) = K1 con x en [%s, %s], recalculando adopción y bases en cada x" % (lo, hi)))
    if K1 is None:
        inv.result_status, inv.reason = "undefined_denominator", "K1_UNDEFINED"
        return inv
    if invariance_proof is not None:
        g0 = constant_value - K1
        inv.fixed_point_converged = True
        inv.coverage = "certified"
        if abs(g0) <= tol_residual:
            inv.intervals.append((lo, hi, True, True, abs(g0)))
            inv.result_status = "computed"
        else:
            inv.result_status, inv.no_solution = "no_feasible_solution", True
            inv.reason = "INVARIANT_" + invariance_proof
        return inv
    from .raices import find_roots
    try:
        rs = find_roots(lambda x: C2_of(x) - K1, lo, hi, evidence=_shift(evidence, K1), n=n, tol_residual=tol_residual,
                        xtol=xtol)
    except (TypeError, ValueError):
        inv.result_status, inv.reason = "incomplete", "C2_NOT_COMPLETE_ON_SEARCH"
        return inv
    except Exception:  # noqa: BLE001
        inv.result_status, inv.reason = "failed", "C2_EVALUATION_FAILED"
        return inv
    return _from_search(inv, rs, lo, hi)


class Profile:
    """Perfil C2(x) en [lo, hi] compartido por todas las celdas de una misma clave estructural (C2 no depende de K1):
    las evaluaciones se cachean y se reutilizan entre celdas. `evidence` (opcional) es un encierro DEMOSTRATIVO de
    C2(x) (raices.Evidence1D); sin él ninguna búsqueda puede certificar cobertura."""

    def __init__(self, C2_of, lo: float, hi: float, n: int, *, xtol: float = 1e-12, evidence=None):
        self.lo, self.hi, self.n, self.xtol = lo, hi, n, xtol
        self.points: dict = {}
        self._f = C2_of
        self.evidence = evidence

    def __call__(self, x: float):
        if x not in self.points:
            self.points[x] = self._f(x)
        v = self.points[x]
        if v is None:
            raise ValueError("C2_NOT_COMPLETE")
        return v


def endogenous_profile(inversion_id: str, prof: Profile, K1: float | None, *, xtol: float = 1e-12,
                       tol_residual: float = 1e-9) -> Inversion:
    return endogenous(inversion_id, prof, K1, prof.lo, prof.hi, n=prof.n, xtol=xtol, tol_residual=tol_residual,
                      evidence=prof.evidence)


def not_identified(inversion_id: str, reason: str) -> Inversion:
    return Inversion(inversion_id, result_status="not_identified", reason=reason,
                     method_id="fixed_point_bracket_bisection", definition="rama no identificada: " + reason)
