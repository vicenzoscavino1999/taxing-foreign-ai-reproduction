"""R2: raíces de CS - K1 sobre las cuatro trayectorias declaradas (diseño §7.9 tabla congelada).

Trayectorias: tau_f_0: (t, 0); tau_d_0: (0, t); paridad: (t, t); tau_d_estatutario: (rate, t).
Cada sección se intersecta con el menú factible; si la intersección es vacía o degenerada (un punto), la sección es
'not_applicable' con motivo y conteos nulos (no cero ficticio). En la sección estatutaria, sin tasa verificada:
'incomplete' con conteos nulos.
Raíces (raices.find_roots): existencia por cambio de signo con residuo bajo tolerancia (un salto no es raíz),
convergencia por residuo y cobertura solo con evidencia demostrativa; tangencias y raíces en extremos se conservan.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from .numeric import brent, golden_max

SECTIONS = ("paridad", "tau_d_0", "tau_d_estatutario", "tau_f_0")


@dataclass
class SectionRoot:
    root_index: int
    tau_d: float
    tau_f: float
    parameter_low: float
    parameter_high: float
    root_type: str
    side: str
    branch_id: str
    residual: float
    corner_binding: bool
    kink_adjacent: bool


@dataclass
class Section:
    section_id: str
    roots: list = field(default_factory=list)
    n_roots: int | None = None
    n_tangential: int | None = None
    status: str = "incomplete"
    reason: str | None = None
    rate_input_id: str | None = None
    no_solution: bool = False
    corner_binding: bool = False
    kink_adjacent: bool = False
    diagnostics: dict = field(default_factory=dict)


def _path(section: str, instrument: str, bar_d: float, bar_f: float, rate: float | None):
    """(función t -> (tau_d, tau_f), t_min, t_max) o None si la intersección con el menú es vacía/degenerada."""
    d_ok = instrument in ("d", "df")
    f_ok = instrument in ("f", "df")
    if section == "tau_f_0":
        return (lambda t: (t, 0.0), 0.0, bar_d) if d_ok else None
    if section == "tau_d_0":
        return (lambda t: (0.0, t), 0.0, bar_f) if f_ok else None
    if section == "paridad":
        return (lambda t: (t, t), 0.0, min(bar_d, bar_f)) if (d_ok and f_ok) else None
    if section == "tau_d_estatutario":
        if rate is None or not (0.0 <= rate <= bar_d):
            return None
        if instrument == "df":
            return (lambda t: (rate, t), 0.0, bar_f)
        return None  # 'd' fija tau_f=0 (un punto); 'f' fija tau_d=0
    raise ValueError("sección desconocida")


def solve_section(f, regime, section: str, instrument: str, bar_d: float, bar_f: float, *, rate: float | None = None,
                  rate_input_id: str | None = None, rate_verified: bool = True, n: int = 256, jump_tol: float = 1e-9,
                  tangent_tol: float = 1e-10, evidence=None, tol_residual: float = 1e-9) -> Section:
    """Raíces de f sobre la trayectoria de la sección (raices.find_roots). `evidence` es un encierro DEMOSTRATIVO de
    g(t) = f(path(t)); sin él la búsqueda por malla solo aporta hallazgos y la sección queda `incomplete`
    (ROOT_SET_COVERAGE_NOT_CERTIFIED): encontrar raíces no demuestra haberlas encontrado todas. Un cambio de signo cuyo
    residuo final supera la tolerancia es un salto, no una raíz (diagnóstico). Conteos solo con cobertura certificada."""
    from .raices import find_roots
    sec = Section(section, rate_input_id=rate_input_id)
    if section == "tau_d_estatutario" and not rate_verified:
        sec.status, sec.reason = "incomplete", "STATUTORY_RATE_NOT_VERIFIED"
        return sec
    p = _path(section, instrument, bar_d, bar_f, rate)
    if p is None:
        sec.status, sec.reason = "not_applicable", "SECTION_OUTSIDE_MENU"
        return sec
    pt, t0, t1 = p
    g = lambda t: f(*pt(t))  # noqa: E731
    try:
        rs = find_roots(g, t0, t1, evidence=evidence, n=n, tol_residual=tol_residual)
    except Exception:  # noqa: BLE001
        sec.status, sec.reason = "failed", "SECTION_EVALUATION_FAILED"
        return sec
    sec.diagnostics = rs.diagnostics
    sec.kink_adjacent = bool(rs.rejected_jumps)
    if rs.status != "complete":
        sec.status, sec.reason = ("failed" if rs.status == "failed" else "incomplete"), rs.reason
        return sec
    if not all(r.converged for r in rs.roots) or rs.zero_intervals:
        sec.status = "incomplete"
        sec.reason = "ROOT_NOT_LOCALIZED_TO_TOLERANCE" if rs.zero_intervals == [] else "ZERO_INTERVAL_ON_SECTION"
        return sec
    for idx, r in enumerate(rs.roots):
        x, y = pt(r.x)
        kind = r.kind
        if r.x in (t0, t1) and kind == "crossing":
            kind = "boundary"
        corner = (x in (0.0, bar_d) and y in (0.0, bar_f))
        sec.roots.append(SectionRoot(idx, x, y, r.lo, r.hi, kind, "point", str(regime(x, y)), r.residual, corner,
                                     sec.kink_adjacent))
    sec.n_roots = len(sec.roots)
    sec.n_tangential = sum(1 for r in sec.roots if r.root_type == "tangent")
    sec.corner_binding = any(r.corner_binding for r in sec.roots)
    sec.no_solution = sec.n_roots == 0
    sec.status, sec.reason = "complete", None
    return sec
