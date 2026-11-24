"""Frontera detallada (B/frontier_result) y techo de captura (B/capture_ceiling_result, B/sup_witness).

Elasticidades eps_ij = dlnB_i/dln x_j = -x_j (dB_i/dtau_j)/B_i (3.10)-(3.13), por diferencias finitas DENTRO de la
misma topología de adopción (misma rama). Si el estencil cruza de régimen, el punto no tiene derivada bilateral:
la fila 'point' deja esas elasticidades nulas con motivo y se añaden filas 'left_limit'/'right_limit' con las
derivadas laterales (V8b: no se promedian laterales). Una base no positiva deja nulas sus elasticidades (P1).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from . import model as M
from .supremum import SupConfig, SupResult, supremum, nodes, axes

H_DIFF = 1e-6


def location(td: float, tf: float, bar_d: float, bar_f: float) -> str:
    if td == 0.0 and tf == 0.0:
        return "origen"
    if tf == 0.0:
        return "esquina_f"
    if td == 0.0:
        return "esquina_d"
    if td == bar_d or tf == bar_f:
        return "borde"
    return "interior"


@dataclass
class PointRow:
    point_id: str
    side: str
    tau_d: float
    tau_f: float
    B_d: float | None
    B_f: float | None
    R: float | None
    B_pot: float | None
    eps: dict
    s_P: float | None
    regime: str
    kink_adjacent: bool
    audit_status: str
    computation_status: str
    reason_code: str | None
    topology: str


def _deriv(s: M.State, design: str, td: float, tf: float, axis: str, side: int, topo: str):
    """Derivada (dB_d, dB_f) en el eje por diferencia lateral o central dentro de la misma topología."""
    h = H_DIFF
    def ev(x, y):
        return M.evaluate(s, x, y, design)
    if side == 0:
        a = ev(td - h, tf) if axis == "d" else ev(td, tf - h)
        b = ev(td + h, tf) if axis == "d" else ev(td, tf + h)
        if a.topology != topo or b.topology != topo:
            return None
        return (b.B_d - a.B_d) / (2 * h), (b.B_f - a.B_f) / (2 * h)
    c = ev(td, tf)
    o = ev(td + side * h, tf) if axis == "d" else ev(td, tf + side * h)
    if o.topology != topo:
        return None
    return side * (o.B_d - c.B_d) / h, side * (o.B_f - c.B_f) / h


def _elasticities(ev: M.Evaluation, deriv_d, deriv_f):
    x_d, x_f = 1.0 - ev.tau_d, 1.0 - ev.tau_f
    out = {"eps_dd": None, "eps_df": None, "eps_fd": None, "eps_ff": None}
    if deriv_d is not None:
        if ev.B_d > 0:
            out["eps_dd"] = -x_d * deriv_d[0] / ev.B_d
        if ev.B_f > 0:
            out["eps_fd"] = -x_d * deriv_d[1] / ev.B_f
    if deriv_f is not None:
        if ev.B_d > 0:
            out["eps_df"] = -x_f * deriv_f[0] / ev.B_d
        if ev.B_f > 0:
            out["eps_ff"] = -x_f * deriv_f[1] / ev.B_f
    return out


def point_rows(s: M.State, design: str, td: float, tf: float, bar_d: float, bar_f: float, point_id: str) -> list[PointRow]:
    """Fila 'point' y, si el estencil cruza de régimen, filas laterales. Derivadas del objeto base en todo su dominio."""
    try:
        ev = M.evaluate(s, td, tf, design)
    except (M.DomainError, ValueError):
        return [PointRow(point_id, "point", td, tf, None, None, None, None, {}, None,
                         location(td, tf, bar_d, bar_f), False, "fail", "failed", "EVALUATION_FAILED", "")]
    topo = ev.topology
    sides = {}
    kink = False
    for axis, t in (("d", td), ("f", tf)):
        can_left = t - H_DIFF >= 0.0
        central = _deriv(s, design, td, tf, axis, 0, topo) if can_left else None
        if central is not None:
            sides[axis] = {"point": central}
            continue
        right = _deriv(s, design, td, tf, axis, +1, topo)
        left = _deriv(s, design, td, tf, axis, -1, topo) if can_left else None
        if can_left:
            kink = True
            sides[axis] = {"point": None, "left_limit": left, "right_limit": right}
        else:
            sides[axis] = {"point": right}   # borde inferior del dominio de tasas: derivada lateral natural
    sP = None if tf == 0.0 else M.provider_share(tf, s.phi)
    rows = []
    reason = None
    eps = _elasticities(ev, sides["d"].get("point"), sides["f"].get("point"))
    if kink:
        reason = "KINK_NO_DERIVATIVE"
    elif any(v is None for v in eps.values()) and (ev.B_d <= 0 or ev.B_f <= 0):
        reason = "BASE_NONPOSITIVE"
    elif tf == 0.0:
        reason = "SP_LIMIT_AT_ZERO_RATE"
    rows.append(PointRow(point_id, "point", td, tf, ev.B_d, ev.B_f, ev.R, ev.B_pot, eps, sP,
                         location(td, tf, bar_d, bar_f), kink, "limitation" if kink else "pass", "complete", reason, topo))
    if kink:
        for side in ("left_limit", "right_limit"):
            dd = sides["d"].get(side, sides["d"].get("point"))
            df = sides["f"].get(side, sides["f"].get("point"))
            rows.append(PointRow(point_id, side, td, tf, ev.B_d, ev.B_f, ev.R, ev.B_pot, _elasticities(ev, dd, df), sP,
                                 location(td, tf, bar_d, bar_f), True, "pass", "complete", "LATERAL_DERIVATIVE", topo))
    return rows


@dataclass
class Ceiling:
    instrument_available: bool
    sup: SupResult | None
    C2: float | None
    B_pot: float
    numerical_error: float | None
    status: str
    reason: str | None


def capture_ceiling(s: M.State, design: str, instrument: str, bar_d: float, bar_f: float, available: bool,
                    cfg: SupConfig) -> Ceiling:
    """C_2 = sup R/B_pot sobre T; instrumento ausente => not_applicable (nunca cero)."""
    if not available:
        return Ceiling(False, None, None, s.B_pot, None, "not_applicable", "INSTRUMENT_NOT_AVAILABLE")
    res = supremum(lambda d, f: M.revenue(s, d, f, design), instrument, bar_d, bar_f,
                   jumps=M.jump_functions(s, design), config=cfg)
    C2 = res.sup / s.B_pot
    err = res.numerical_error / s.B_pot if math.isfinite(res.numerical_error) else None
    return Ceiling(True, res, C2, s.B_pot, err, res.status, res.reason)


def frontier_grid(s: M.State, design: str, instrument: str, bar_d: float, bar_f: float, n: int) -> list[PointRow]:
    (dl, dh), (fl, fh) = axes(instrument, bar_d, bar_f)
    dn = nodes(dl, dh, n) if dh > dl else [dl]
    fn = nodes(fl, fh, n) if fh > fl else [fl]
    rows = []
    for i, td in enumerate(dn):
        for j, tf in enumerate(fn):
            rows.extend(point_rows(s, design, td, tf, bar_d, bar_f, f"P{i:04d}_{j:04d}"))
    return rows
