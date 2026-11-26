"""Supremo de R sobre el menú fiscal T (C_2 = sup R/B_pot, (8.6) de la teoría; (26) del diseño).

Método (declarado antes de correr y autenticado por algorithm_config):
1. mallas anidadas n_l = n0*2^l + 1 por eje activo; coordenadas exactas anidadas (bar*i/n);
2. pulido local de los k mejores nodos de cada nivel: ascenso por coordenadas (sección áurea) y búsqueda de compás;
3. bordes: la malla y el pulido respetan el compacto cerrado; las esquinas son nodos;
4. saltos (solo rho = 1): se localizan las curvas c(tau)=0 donde F1-F0 es idénticamente nula; en cada punto de la
   curva se estiman los dos límites laterales por extrapolación de Richardson y el valor en la curva (regla S13);
   el mejor límite lateral se maximiza a lo largo de la curva. Los candidatos pegados a la curva (a menos de
   delta_jump en el eje de cruce) aproximan un límite y no cuentan como valores alcanzados. Si el mejor límite
   supera todo valor alcanzado, el supremo NO se alcanza: tasas nulas, dos laterales y secuencia testigo;
5. error numérico = cambio del supremo entre los dos últimos niveles + error de extrapolación lateral.

No se supone concavidad ni continuidad del gradiente: los cruces se detectan por evaluación (V8d).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from .numeric import brent, golden_max


@dataclass(frozen=True)
class SupConfig:
    n0: int = 8
    levels: int = 3
    top_k: int = 6
    polish_xtol: float = 1e-11
    richardson_eps: float = 1e-6
    delta_jump: float = 1e-7
    tol_attain: float = 1e-10
    tol_converge: float = 1e-7
    scout_xtol: float = 1e-7

    def as_dict(self) -> dict:
        return {"n0": self.n0, "levels": self.levels, "top_k": self.top_k, "polish_xtol": self.polish_xtol,
                "scout_xtol": self.scout_xtol,
                "richardson_eps": self.richardson_eps, "delta_jump": self.delta_jump,
                "tol_attain": self.tol_attain, "tol_converge": self.tol_converge}


@dataclass
class Witness:
    sequence_index: int
    side: str
    tau_d: float
    tau_f: float
    value: float
    limit_value: float
    approach_distance: float
    branch_id: str


@dataclass
class Lateral:
    tau_d: float
    tau_f: float
    axis: str
    minus: float | None     # límite desde tasas menores en el eje
    plus: float | None      # límite desde tasas mayores
    at_curve: float         # valor en la curva (regla S13)
    err: float

    def best(self):
        opts = [(v, s) for v, s in ((self.minus, -1.0), (self.plus, 1.0)) if v is not None]
        return max(opts) if opts else (None, 0.0)


@dataclass
class SupResult:
    sup: float
    attained: bool
    tau_d: float | None
    tau_f: float | None
    lateral_low: float | None
    lateral_high: float | None
    witnesses: list = field(default_factory=list)
    level_values: list = field(default_factory=list)
    numerical_error: float = math.inf
    converged: bool = False
    status: str = "incomplete"
    reason: str | None = None
    evaluations: dict = field(default_factory=dict)
    lateral_axis: str | None = None
    final_n: int = 0
    # Naturaleza del error informado: 'convergence_estimate' (cambio entre niveles de malla con pulido: NO es cota) o
    # 'certified_bound' (rama y cota con encierros demostrativos: sup en [lower, upper] y |sup - valor| <= error).
    error_kind: str = "convergence_estimate"
    upper: float | None = None
    lower: float | None = None
    n_jump_points: int = 0


class _Cache:
    def __init__(self, fn):
        self.fn = fn
        self.values: dict[tuple[float, float], float] = {}

    def __call__(self, td: float, tf: float) -> float:
        key = (td, tf)
        v = self.values.get(key)
        if v is None:
            v = self.fn(td, tf)
            self.values[key] = v
        return v


def axes(instrument: str, bar_d: float, bar_f: float):
    if instrument == "d":
        return (0.0, bar_d), (0.0, 0.0)
    if instrument == "f":
        return (0.0, 0.0), (0.0, bar_f)
    if instrument == "df":
        return (0.0, bar_d), (0.0, bar_f)
    raise ValueError("instrumento desconocido")


def nodes(lo: float, hi: float, n: int) -> list[float]:
    """Nodos anidados exactos: bar*i/n con lo = 0 (menús del contrato empiezan en tasa cero)."""
    if hi == lo:
        return [lo]
    if lo != 0.0:
        return [lo + (hi - lo) * i / n for i in range(n + 1)]
    return [hi * i / n for i in range(n + 1)]


def _profile_1d(g, lo: float, hi: float, xtol: float, scan: int = 8):
    """Máximo de g en [lo,hi]: barrido de scan+1 puntos y sección áurea alrededor del mejor (robusto a kinks)."""
    if hi <= lo:
        return lo, g(lo)
    xs = [lo + (hi - lo) * k / scan for k in range(scan + 1)]
    vs = [g(x) for x in xs]
    k = max(range(len(xs)), key=lambda i: (vs[i], -i))
    a, b = xs[max(k - 1, 0)], xs[min(k + 1, scan)]
    x, v = golden_max(g, a, b, xtol=xtol)
    if vs[k] >= v:
        return xs[k], vs[k]
    return x, v


def _profile_search(f, box, n: int, xtol: float) -> list:
    """Búsqueda global por perfiles en 2D (ambos órdenes): g(t) = max_s R(s,t) con barrido de n+1 nudos y sección
    áurea; el perfil se barre en n+1 nudos y se refina con sección áurea alrededor de CADA máximo local del barrido.
    Evita quedar atrapado en la cuenca de un nodo de malla cuando R cae bruscamente al cambiar de régimen."""
    (dl, dh), (fl, fh) = box
    out = []
    for order in ("f_outer", "d_outer"):
        if order == "f_outer":
            olo, ohi, ilo, ihi = fl, fh, dl, dh
            point = lambda o, i: (i, o)
        else:
            olo, ohi, ilo, ihi = dl, dh, fl, fh
            point = lambda o, i: (o, i)
        memo = {}

        def inner(o):
            if o not in memo:
                memo[o] = _profile_1d(lambda i: f(*point(o, i)), ilo, ihi, xtol, scan=n)
            return memo[o][1]
        os_ = [olo + (ohi - olo) * k / n for k in range(n + 1)]
        gs = [inner(o) for o in os_]
        peaks = [k for k in range(n + 1) if (k == 0 or gs[k] >= gs[k - 1]) and (k == n or gs[k] >= gs[k + 1])]
        for k in peaks:
            o, v = golden_max(inner, os_[max(k - 1, 0)], os_[min(k + 1, n)], xtol=xtol)
            if gs[k] >= v:
                o, v = os_[k], gs[k]
            i = memo[o][0] if o in memo else _profile_1d(lambda i: f(*point(o, i)), ilo, ihi, xtol, scan=n)[0]
            x, y = point(o, i)
            out.append((f(x, y), x, y))
    return out


def _polish(f, x0: float, y0: float, box, xtol: float):
    """Pulido local: en 2D maximización de perfil anidada (max_tf max_td R); en 1D sección áurea con barrido."""
    (dl, dh), (fl, fh) = box
    if dh > dl and fh > fl:
        memo = {}

        def inner(tf):
            if tf not in memo:
                memo[tf] = _profile_1d(lambda td: f(td, tf), dl, dh, xtol)
            return memo[tf][1]
        y, best = _profile_1d(inner, fl, fh, xtol)
        x = memo[y][0] if y in memo else _profile_1d(lambda td: f(td, y), dl, dh, xtol)[0]
        best = f(x, y)
        if f(x0, y0) > best:
            x, y, best = x0, y0, f(x0, y0)
        return _snap(f, x, y, best, box, xtol)
    x, y, best = x0, y0, f(x0, y0)
    for _ in range(40):
        moved = False
        if dh > dl:
            nx, v = golden_max(lambda t: f(t, y), dl, dh, xtol=xtol)
            if v > best:
                moved = moved or abs(nx - x) > xtol
                x, best = nx, v
        if fh > fl:
            ny, v = golden_max(lambda t: f(x, t), fl, fh, xtol=xtol)
            if v > best:
                moved = moved or abs(ny - y) > xtol
                y, best = ny, v
        if not moved:
            break
    step = max(dh - dl, fh - fl) / 4.0
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    while step > xtol:
        improved = False
        for dx, dy in dirs:
            nx = min(max(x + dx * step, dl), dh)
            ny = min(max(y + dy * step, fl), fh)
            v = f(nx, ny)
            if v > best:
                x, y, best, improved = nx, ny, v, True
                break
        if not improved:
            step /= 2.0
    return _snap(f, x, y, best, box, xtol)


def _snap(f, x, y, best, box, xtol):
    """Los bordes del compacto son alcanzables: un pulido a menos de xtol de un borde se ubica en el borde."""
    (dl, dh), (fl, fh) = box
    for edge in (dl, dh):
        if abs(x - edge) <= xtol and f(edge, y) >= best:
            x, best = edge, f(edge, y)
    for edge in (fl, fh):
        if abs(y - edge) <= xtol and f(x, edge) >= best:
            y, best = edge, f(x, edge)
    return x, y, best


def jump_points(c, dnodes, fnodes):
    """Puntos de la curva c=0 sobre las líneas de la malla, con el eje de cruce."""
    pts = []
    if len(dnodes) > 1:
        for tf in fnodes:
            vals = [c(td, tf) for td in dnodes]
            for i in range(len(dnodes) - 1):
                if vals[i] == 0.0:
                    pts.append((dnodes[i], tf, "d"))
                elif vals[i + 1] != 0.0 and (vals[i] > 0) != (vals[i + 1] > 0):
                    pts.append((brent(lambda t: c(t, tf), dnodes[i], dnodes[i + 1], vals[i], vals[i + 1]), tf, "d"))
    if len(fnodes) > 1:
        for td in dnodes:
            vals = [c(td, tf) for tf in fnodes]
            for i in range(len(fnodes) - 1):
                if vals[i] == 0.0:
                    pts.append((td, fnodes[i], "f"))
                elif vals[i + 1] != 0.0 and (vals[i] > 0) != (vals[i + 1] > 0):
                    pts.append((td, brent(lambda t: c(td, t), fnodes[i], fnodes[i + 1], vals[i], vals[i + 1]), "f"))
    return pts


def lateral_limits(f, td: float, tf: float, axis: str, box, eps: float) -> Lateral:
    (dl, dh), (fl, fh) = box
    out = {}
    errs = []
    for sign in (-1.0, 1.0):
        vals = []
        for e in (eps, eps / 2.0, eps / 4.0):
            x = td + sign * e if axis == "d" else td
            y = tf + sign * e if axis == "f" else tf
            if not (dl <= x <= dh and fl <= y <= fh):
                vals = None
                break
            vals.append(f(x, y))
        if vals is None:
            out[sign] = None
            continue
        lim_coarse = 2.0 * vals[1] - vals[0]    # Richardson de orden 1 con (eps, eps/2)
        lim = 2.0 * vals[2] - vals[1]           # con (eps/2, eps/4)
        out[sign] = lim
        errs.append(abs(lim - lim_coarse))      # error estimado: diferencia entre extrapolaciones
    return Lateral(td, tf, axis, out[-1.0], out[1.0], f(td, tf), max(errs) if errs else math.inf)


def _near_curve(jumps, x, y, axis_box, delta):
    (dl, dh), (fl, fh) = axis_box
    for c in jumps:
        for ax in ("d", "f"):
            lo = (max(x - delta, dl), y) if ax == "d" else (x, max(y - delta, fl))
            hi = (min(x + delta, dh), y) if ax == "d" else (x, min(y + delta, fh))
            if lo == hi:
                continue
            a, b = c(*lo), c(*hi)
            if a == 0.0 or b == 0.0 or (a > 0) != (b > 0):
                return True
    return False


def _refine_on_curve(f, c, lat: Lateral, sign: float, box, cfg: SupConfig, width: float) -> Lateral:
    (dl, dh), (fl, fh) = box
    axis = lat.axis

    def point(t):
        try:
            if axis == "d":
                return brent(lambda s: c(s, t), dl, dh), t
            return t, brent(lambda s: c(t, s), fl, fh)
        except ValueError:
            return None

    span = (fl, fh) if axis == "d" else (dl, dh)
    if span[1] <= span[0]:
        return lat
    t0 = lat.tau_f if axis == "d" else lat.tau_d

    def obj(t):
        p = point(t)
        if p is None:
            return -math.inf
        v = lateral_limits(f, p[0], p[1], axis, box, cfg.richardson_eps)
        val = v.plus if sign > 0 else v.minus
        return -math.inf if val is None else val

    t_star, v_star = golden_max(obj, max(span[0], t0 - width), min(span[1], t0 + width), xtol=cfg.polish_xtol)
    cur = lat.plus if sign > 0 else lat.minus
    if cur is None or v_star > cur:
        p = point(t_star)
        if p is not None:
            return lateral_limits(f, p[0], p[1], axis, box, cfg.richardson_eps)
    return lat


def supremum(value, instrument: str, bar_d: float, bar_f: float, *, jumps=(), config: SupConfig = SupConfig()) -> SupResult:
    cfg = config
    f = _Cache(value)
    box = axes(instrument, bar_d, bar_f)
    (dl, dh), (fl, fh) = box
    res = SupResult(sup=-math.inf, attained=True, tau_d=None, tau_f=None, lateral_low=None, lateral_high=None)
    final = None
    for level in range(cfg.levels):
        n = cfg.n0 * (2 ** level)
        dn = nodes(dl, dh, n) if dh > dl else [dl]
        fn = nodes(fl, fh, n) if fh > fl else [fl]
        grid = [(f(td, tf), td, tf, i, j) for i, td in enumerate(dn) for j, tf in enumerate(fn)]
        grid.sort(key=lambda r: (-r[0], r[1], r[2]))
        cands = [(grid[0][0], grid[0][1], grid[0][2])]
        if dh > dl and fh > fl:
            # búsqueda global de exploración (tolerancia gruesa) y pulido local fino del mejor candidato explorado
            ps = _profile_search(f, box, n, cfg.scout_xtol)
            cands += ps
            if ps:
                _, x0, y0 = max(ps, key=lambda r: (r[0], -r[1], -r[2]))
                hd, hf = (dh - dl) / n, (fh - fl) / n
                sub = ((max(dl, x0 - hd), min(dh, x0 + hd)), (max(fl, y0 - hf), min(fh, y0 + hf)))
                x, y, pv = _polish(f, x0, y0, sub, cfg.polish_xtol)
                cands.append((pv, x, y))
        for v, td, tf, i, j in grid[: cfg.top_k]:
            sub = ((dn[max(i - 1, 0)], dn[min(i + 1, len(dn) - 1)]), (fn[max(j - 1, 0)], fn[min(j + 1, len(fn) - 1)]))
            x, y, pv = _polish(f, td, tf, sub, cfg.polish_xtol)
            cands.append((pv, x, y))
        laterals = []
        for c in jumps:
            for td, tf, axis in jump_points(c, dn, fn):
                laterals.append((c, lateral_limits(f, td, tf, axis, box, cfg.richardson_eps)))
        attained = [cand for cand in cands if not (jumps and _near_curve(jumps, cand[1], cand[2], box, cfg.delta_jump))]
        attained += [(lat.at_curve, lat.tau_d, lat.tau_f) for _, lat in laterals]
        if not attained:
            attained = cands
        a_best = max(attained, key=lambda r: (r[0], -r[1], -r[2]))
        l_best = None
        if laterals:
            c, lat = max(laterals, key=lambda cl: cl[1].best()[0] if cl[1].best()[0] is not None else -math.inf)
            v, sign = lat.best()
            if v is not None:
                width = (max(dh - dl, fh - fl)) / n
                lat = _refine_on_curve(f, c, lat, sign, box, cfg, width)
                v, sign = lat.best()
                l_best = (v, sign, lat)
        if final is not None and final[0][0] > a_best[0]:
            a_best = final[0]           # todo valor alcanzado es cota inferior válida: la estimación no retrocede
        if final is not None and final[1] is not None and (l_best is None or final[1][0] > l_best[0]):
            l_best = final[1]
        if l_best is not None and l_best[0] > a_best[0] + cfg.tol_attain:
            level_sup = l_best[0]
        else:
            level_sup = a_best[0]
        res.level_values.append(level_sup)
        final = (a_best, l_best)
        res.final_n = n
        res.n_jump_points = len(laterals)
    a_best, l_best = final
    res.sup = res.level_values[-1]
    lateral_err = 0.0
    if l_best is not None and l_best[0] > a_best[0] + cfg.tol_attain:
        v, sign, lat = l_best
        res.attained = False
        res.lateral_low, res.lateral_high = lat.minus, lat.plus
        res.lateral_axis = lat.axis
        lateral_err = lat.err
        side = "right_limit" if sign > 0 else "left_limit"
        for k, e in enumerate(10.0 ** (-j) for j in range(3, 10)):
            x = lat.tau_d + sign * e if lat.axis == "d" else lat.tau_d
            y = lat.tau_f + sign * e if lat.axis == "f" else lat.tau_f
            if dl <= x <= dh and fl <= y <= fh:
                res.witnesses.append(Witness(len(res.witnesses), side, x, y, f(x, y), v, e,
                                             "jump:" + ("plus" if sign > 0 else "minus")))
    else:
        res.attained = True
        res.tau_d, res.tau_f = a_best[1], a_best[2]
    if len(res.level_values) >= 2:
        res.numerical_error = abs(res.level_values[-1] - res.level_values[-2]) + lateral_err
    res.converged = res.numerical_error <= cfg.tol_converge
    res.status = "complete" if res.converged else "incomplete"
    res.reason = None if res.converged else "SUP_NOT_CONVERGED"
    res.evaluations = f.values
    return res


def certified_supremum(value, instrument: str, bar_d: float, bar_f: float, enclosure, *, tol: float = 1e-10,
                       max_boxes: int = 200000) -> SupResult:
    """Supremo CERTIFICADO por rama y cota: enclosure(x0, x1, y0, y1) -> Iv que contiene value en la caja.
    Cota inferior DEMOSTRADA = máximo de los encierros PUNTUALES enclosure(x, x, y, y).lo en los puntos visitados (el
    valor en flotante no es una cota); superior = máximo de los encierros de las cajas vivas. El valor informado es el
    mejor valor evaluado y `numerical_error` = max(upper - valor, valor - lower) es una COTA demostrada de |sup - valor|
    (error_kind='certified_bound'). Sin cierre dentro del presupuesto: status 'incomplete' con las cotas alcanzadas."""
    import heapq
    (dl, dh), (fl, fh) = axes(instrument, bar_d, bar_f)
    res = SupResult(sup=-math.inf, attained=True, tau_d=None, tau_f=None, lateral_low=None, lateral_high=None)
    res.error_kind = "certified_bound"
    best = [-math.inf, None, None]
    low = [-math.inf]

    def visit(x, y):
        v = value(x, y)
        if v > best[0]:
            best[:] = [v, x, y]
        low[0] = max(low[0], enclosure(x, x, y, y).lo)

    for x in {dl, dh, 0.5 * (dl + dh)}:
        for y in {fl, fh, 0.5 * (fl + fh)}:
            visit(x, y)
    heap = [(-enclosure(dl, dh, fl, fh).hi, (dl, dh, fl, fh))]
    boxes = 0
    while heap:
        neg_hi, (x0, x1, y0, y1) = heap[0]
        upper = -neg_hi
        if upper - low[0] <= tol:
            break
        heapq.heappop(heap)
        boxes += 1
        if boxes > max_boxes:
            heapq.heappush(heap, (neg_hi, (x0, x1, y0, y1)))
            break
        if x1 - x0 >= y1 - y0:
            m = 0.5 * (x0 + x1)
            kids = ((x0, m, y0, y1), (m, x1, y0, y1))
        else:
            m = 0.5 * (y0 + y1)
            kids = ((x0, x1, y0, m), (x0, x1, m, y1))
        for b in kids:
            visit(0.5 * (b[0] + b[1]), 0.5 * (b[2] + b[3]))
            hi = enclosure(*b).hi
            if hi >= low[0]:
                heapq.heappush(heap, (-hi, b))
    upper = max(low[0], -heap[0][0]) if heap else low[0]
    res.sup, res.tau_d, res.tau_f = best[0], best[1], best[2]
    res.upper, res.lower = upper, low[0]
    res.numerical_error = max(0.0, upper - best[0], best[0] - low[0])
    res.level_values = [best[0]]
    res.converged = res.numerical_error <= tol
    res.status = "complete" if res.converged else "incomplete"
    res.reason = None if res.converged else "CERTIFIED_BOUND_NOT_CLOSED"
    res.final_n = boxes
    return res
