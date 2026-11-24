"""Búsqueda de raíces 1-D con garantías SEPARADAS (hallazgos B y ronda 3 del revisor).

Cada raíz publicada distingue:
1. APROXIMACIÓN numérica `x` (punto medio de su intervalo aislante) y su residuo |g(x)| — DIAGNÓSTICO, nunca prueba.
2. EXISTENCIA demostrada: cambio de signo DEMOSTRADO (encierros puntuales que excluyen el cero) en los extremos de un
   intervalo donde g es continua (derivada encerrada y finita), o conteo exacto (Sturm) en la ruta polinómica exacta.
3. UNICIDAD en el intervalo aislante: monotonía estricta demostrada (g' encerrada sin cero) o conteo exacto.
4. MULTIPLICIDAD/TANGENCIA: solo con prueba exacta (descomposición libre de cuadrados en aritmética racional); una
   tangencia NUNCA se declara porque |g(c)| sea pequeño en un punto crítico aproximado.
5. COBERTURA del conjunto completo: `complete` solo si cada subintervalo del dominio quedó demostrado vacío, con una
   raíz aislada, o idénticamente nulo. Si no, `incomplete` con cajas pendientes y hallazgos como diagnóstico.

Rutas:
- EXACTA para evidencia polinómica (`evidence_from_factors`): los coeficientes flotantes dados se interpretan como
  racionales exactos; el polinomio producto se descompone libre de cuadrados (Yun) y cada parte se aísla y refina con
  sucesiones de Sturm y evaluación exacta de signos. Raíces dobles, en extremos e idénticamente nulas son exactas.
- GENERAL por encierros (`Evidence1D.range/d1/d2`): exclusión por rango; en cajas monótonas, existencia y unicidad por
  signos DEMOSTRADOS en los extremos y localización por bisección con encierros puntuales; en cajas convexas/cóncavas
  (g'' sin cero), exclusión por la desigualdad de la tangente g(x) >= g(c) + g'(c)(x - c) (o su inversa) y por el
  máximo/mínimo en los extremos; lo que no se decide se subdivide y, al ancho mínimo, queda pendiente
  (POSSIBLE_TANGENCY_OR_CLOSE_ROOTS). Un salto nunca produce una raíz.
- SIN evidencia: malla + Brent + mínimos locales = HALLAZGOS, estado `incomplete` (ROOT_SET_COVERAGE_NOT_CERTIFIED).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from fractions import Fraction

from .intervalos import Iv
from .numeric import brent


@dataclass
class Evidence1D:
    """Evidencia demostrativa sobre g en [a, b]. range/d1/d2 devuelven Iv que CONTIENEN g, g', g'' en [a, b] (también
    para cajas degeneradas [x, x]: encierro puntual riguroso). deriv: evaluador puntual aproximado de g' (solo para
    ubicar un punto crítico; la prueba usa siempre encierros). exact_poly: (factores, escala) con coeficientes
    tomados como racionales exactos -> ruta exacta. range_goal(a, b, nivel): encierro igualmente válido que puede
    detenerse en cuanto excluye `nivel` (evaluaciones costosas); las decisiones de signo lo usan con nivel 0."""
    range: object
    d1: object | None = None
    d2: object | None = None
    deriv: object | None = None
    source: str = ""
    exact_poly: tuple | None = None
    range_goal: object | None = None


@dataclass
class Root1D:
    x: float
    lo: float
    hi: float
    residual: float
    kind: str               # crossing | tangent | boundary
    converged: bool         # intervalo aislante demostrado de ancho <= xtol (localización), no "residuo pequeño"
    certified_unique: bool  # única raíz del intervalo [lo, hi] demostrada
    existence: bool = False     # existencia demostrada
    multiplicity: int | None = None


@dataclass
class RootSearch:
    roots: list = field(default_factory=list)
    zero_intervals: list = field(default_factory=list)   # (lo, hi): g idénticamente nula demostrada
    rejected_jumps: list = field(default_factory=list)   # (a, b, residuo): cambio de signo sin raíz (salto)
    pending: list = field(default_factory=list)          # (a, b, motivo): cajas sin certificar
    certified_empty: list = field(default_factory=list)  # (a, b): cajas sin raíz demostrada
    candidates: list = field(default_factory=list)       # hallazgos no demostrados (diagnóstico)
    status: str = "incomplete"                           # complete | incomplete | failed
    reason: str | None = None
    coverage: str = "not_certified"                      # certified | not_certified
    evaluations: int = 0
    route: str = "none"                                  # exact_polynomial | enclosure | scan

    @property
    def diagnostics(self) -> dict:
        return {"roots_found": [(r.x, r.residual, r.kind) for r in self.roots] + [tuple(c) for c in self.candidates],
                "rejected_jumps": self.rejected_jumps[:20], "pending": self.pending[:20], "n_pending": len(self.pending),
                "coverage": self.coverage, "route": self.route}


class _Counted:
    def __init__(self, g):
        self.g, self.n, self.cache = g, 0, {}

    def __call__(self, x):
        if x not in self.cache:
            self.n += 1
            self.cache[x] = self.g(x)
        return self.cache[x]


def _solve(g, a, b, ga, gb, xtol, tol_res, out: RootSearch, *, unique: bool) -> None:
    """Solo barrido NO certificado: Brent en un cambio de signo de flotantes. Hallazgo si el residuo es pequeño;
    si no, salto rechazado."""
    try:
        r = brent(g, a, b, ga, gb, xtol=xtol)
        res = abs(g(r))
    except Exception:  # noqa: BLE001
        out.pending.append((a, b, "ROOT_SOLVER_FAILED"))
        return
    if res <= tol_res:
        out.roots.append(Root1D(r, a, b, res, "crossing", True, unique))
    else:
        out.rejected_jumps.append((a, b, res))


def find_roots(g, lo: float, hi: float, *, evidence: Evidence1D | None = None, n: int = 16, tol_residual: float = 1e-9,
               xtol: float = 1e-12, min_width: float = 1e-9, max_boxes: int = 20000) -> RootSearch:
    """Raíces de g en [lo, hi] con las garantías del encabezado."""
    g = _Counted(g)
    out = RootSearch()
    if hi < lo:
        out.status, out.reason = "failed", "EMPTY_DOMAIN"
        return out
    if evidence is None:
        out.route = "scan"
        _scan_uncertified(g, lo, hi, n, tol_residual, xtol, out)
        _dedupe(out)
    elif evidence.exact_poly is not None:
        out.route = "exact_polynomial"
        _certified_poly(g, lo, hi, evidence.exact_poly, xtol, out, tol_residual)
    else:
        out.route = "enclosure"
        _certified(g, lo, hi, evidence, xtol, min_width, max_boxes, out, tol_residual)
    out.roots.sort(key=lambda r: r.x)
    out.evaluations = g.n
    if out.status != "failed":
        if out.coverage == "certified" and not out.pending and not out.rejected_jumps:
            out.status, out.reason = "complete", None
        else:
            out.status = "incomplete"
            if out.rejected_jumps and out.coverage == "certified":
                out.reason = "DISCONTINUITY_NOT_ROOT"
            elif out.coverage != "certified":
                out.reason = "ROOT_SET_COVERAGE_NOT_CERTIFIED" + (";DISCONTINUITY_NOT_ROOT" if out.rejected_jumps else "")
            else:
                reasons = {p[2] for p in out.pending}
                out.reason = ("EVIDENCE_BUDGET_EXHAUSTED" if "EVIDENCE_BUDGET_EXHAUSTED" in reasons
                              else (sorted(reasons)[0] if reasons else "UNRESOLVED_BOXES"))
    return out


# ============================================================================================ barrido sin cobertura
def _scan_uncertified(g, lo, hi, n, tol_res, xtol, out: RootSearch) -> None:
    """Malla + Brent + mínimos locales: HALLAZGOS sin cobertura. Nunca produce `complete`."""
    out.coverage = "not_certified"
    xs = [lo + (hi - lo) * k / n for k in range(n + 1)] if hi > lo else [lo]
    gs = [g(x) for x in xs]
    for k in range(len(xs) - 1):
        a, b, ga, gb = xs[k], xs[k + 1], gs[k], gs[k + 1]
        if ga == 0.0:
            out.roots.append(Root1D(a, a, a, 0.0, "boundary" if a in (lo, hi) else "crossing", True, False))
        elif gb != 0.0 and (ga > 0) != (gb > 0):
            _solve(g, a, b, ga, gb, xtol, tol_res, out, unique=False)
    if gs[-1] == 0.0:
        out.roots.append(Root1D(xs[-1], xs[-1], xs[-1], 0.0, "boundary", True, False))
    from .numeric import golden_max
    for k in range(1, len(xs) - 1):
        if abs(gs[k]) <= abs(gs[k - 1]) and abs(gs[k]) <= abs(gs[k + 1]) and gs[k - 1] != 0 and gs[k + 1] != 0 \
                and (gs[k - 1] > 0) == (gs[k + 1] > 0):
            # prefiltro parabólico (costo): solo se busca un mínimo de |g| si la parábola por tres nudos puede
            # acercarse a cero. Es un filtro de HALLAZGOS: sin cobertura el resultado es incomplete de todos modos.
            h = xs[k + 1] - xs[k]
            curv = (gs[k + 1] - 2 * gs[k] + gs[k - 1]) / (h * h)
            slope = (gs[k + 1] - gs[k - 1]) / (2 * h)
            pred = gs[k] - slope * slope / (2 * curv) if curv != 0 else gs[k]
            if (pred > 0) == (gs[k] > 0) and abs(pred) > max(10 * tol_res, 0.25 * abs(gs[k])):
                continue
            sgn = 1.0 if gs[k] > 0 else -1.0
            x, v = golden_max(lambda t: -sgn * g(t), xs[k - 1], xs[k + 1], xtol=xtol)
            if abs(v) <= tol_res:
                out.roots.append(Root1D(x, xs[k - 1], xs[k + 1], abs(v), "tangent", True, False))


def _dedupe(out: RootSearch) -> None:
    """Solo para HALLAZGOS del barrido (las rutas certificadas producen intervalos aislantes disjuntos)."""
    roots = sorted(out.roots, key=lambda r: (r.x, r.kind != "tangent"))
    keep = []
    for r in roots:
        if keep and abs(r.x - keep[-1].x) <= 1e-12 * max(1.0, abs(r.x)):
            keep[-1] = Root1D(keep[-1].x, min(keep[-1].lo, r.lo), max(keep[-1].hi, r.hi), min(keep[-1].residual, r.residual),
                              keep[-1].kind, keep[-1].converged and r.converged, False)
            continue
        keep.append(r)
    out.roots = keep


# ============================================================================================ ruta general por encierros
def _sign(iv: Iv) -> int:
    """Signo DEMOSTRADO de un encierro (0 si contiene el cero)."""
    return 1 if iv.lo > 0.0 else (-1 if iv.hi < 0.0 else 0)


def _enc(ev: Evidence1D, a: float, b: float) -> Iv:
    """Encierro para DECIDIR el signo en [a, b] (con range_goal si la evidencia lo ofrece)."""
    return ev.range_goal(a, b, 0.0) if ev.range_goal is not None else ev.range(a, b)


def _point(ev: Evidence1D, x: float) -> Iv:
    return _enc(ev, x, x)


def _split_point(ev: Evidence1D, a: float, b: float) -> float:
    """Punto de corte cuyo encierro puntual excluye el cero (así una raíz nunca queda en el borde de dos cajas)."""
    m = 0.5 * (a + b)
    if _sign(_point(ev, m)) != 0:
        return m
    for k in (1, -1, 2, -2, 3, -3, 5, -5, 7, -7):
        t = m + k * (b - a) / 64.0
        if a < t < b and _sign(_point(ev, t)) != 0:
            return t
    return m


class EvidenceBudgetExhausted(RuntimeError):
    """La evidencia agotó su presupuesto explícito de cómputo: la búsqueda queda incompleta (sin veredicto)."""


def _certified(g, lo, hi, ev: Evidence1D, xtol, min_width, max_boxes, out: RootSearch, tol_res: float = 1e-9) -> None:
    queue, cur = [(lo, hi)], [None]
    try:
        _certified_loop(g, lo, hi, ev, xtol, min_width, max_boxes, out, tol_res, queue, cur)
    except EvidenceBudgetExhausted:
        rest = ([cur[0]] if cur[0] is not None else []) + queue
        out.pending.extend((x, y, "EVIDENCE_BUDGET_EXHAUSTED") for x, y in rest)


def _certified_loop(g, lo, hi, ev, xtol, min_width, max_boxes, out, tol_res, queue, cur) -> None:
    out.coverage = "certified"
    boxes = 0
    while queue:
        a, b = queue.pop()
        cur[0] = (a, b)
        boxes += 1
        if boxes > max_boxes:
            out.pending.append((a, b, "BOX_BUDGET_EXHAUSTED"))
            out.pending.extend((x, y, "BOX_BUDGET_EXHAUSTED") for x, y in queue)
            return
        r = _enc(ev, a, b)
        if _sign(r) != 0:
            out.certified_empty.append((a, b))
            continue
        if r.lo == 0.0 and r.hi == 0.0:
            out.zero_intervals.append((a, b))
            continue
        d1 = ev.d1(a, b) if ev.d1 is not None else None
        if d1 is not None and math.isfinite(d1.lo) and math.isfinite(d1.hi) and _sign(d1) != 0:
            _monotone(g, ev, a, b, d1, lo, hi, xtol, out, tol_res)
            continue
        d2 = ev.d2(a, b) if ev.d2 is not None else None
        if d2 is not None and math.isfinite(d2.lo) and math.isfinite(d2.hi) and _sign(d2) != 0 and ev.d1 is not None:
            if _convex_excludes(ev, a, b, _sign(d2)):
                out.certified_empty.append((a, b))
                continue
        if b - a <= min_width:
            reason = "POSSIBLE_TANGENCY_OR_CLOSE_ROOTS" if (d2 is not None and _sign(d2) != 0) else "MIN_WIDTH_WITHOUT_CERTIFICATE"
            out.pending.append((a, b, reason))
            m = 0.5 * (a + b)
            out.candidates.append((m, abs(g(m)), "unresolved_" + reason.lower()))
            continue
        m = _split_point(ev, a, b)
        queue.append((m, b))
        queue.append((a, m))


def _convex_excludes(ev: Evidence1D, a: float, b: float, curv: int) -> bool:
    """g'' de signo `curv` en [a, b]. Convexa: g(x) >= g(c) + g'(c)(x - c) y max g = max(g(a), g(b)); cóncava: al revés.
    Devuelve True si queda DEMOSTRADO que g no se anula en [a, b]. c es solo una aproximación del punto crítico: la
    desigualdad de la tangente vale para cualquier c en [a, b]."""
    ga, gb = _point(ev, a), _point(ev, b)
    if curv > 0 and max(ga.hi, gb.hi) < 0.0:
        return True
    if curv < 0 and min(ga.lo, gb.lo) > 0.0:
        return True
    c = 0.5 * (a + b)
    if ev.deriv is not None:
        try:
            da, db = ev.deriv(a), ev.deriv(b)
            if da == 0.0:
                c = a
            elif db == 0.0:
                c = b
            elif (da > 0) != (db > 0):
                c = brent(ev.deriv, a, b, da, db, xtol=0.0)
            else:
                c = a if abs(da) < abs(db) else b
        except Exception:  # noqa: BLE001
            c = 0.5 * (a + b)
    gc, dc = _point(ev, c), ev.d1(c, c)
    if not (math.isfinite(dc.lo) and math.isfinite(dc.hi)):
        return False
    span = max(c - a, b - c)
    slope = max(abs(dc.lo), abs(dc.hi))
    if curv > 0:
        return gc.lo - slope * span > 0.0
    return gc.hi + slope * span < 0.0


def _bound(e: Iv) -> float:
    """Cota DEMOSTRADA de |g| en el punto cuyo encierro es e."""
    return max(abs(e.lo), abs(e.hi))


def _monotone(g, ev: Evidence1D, a, b, d1: Iv, lo, hi, xtol, out: RootSearch, tol_res: float = 1e-9) -> None:
    """g estrictamente monótona y continua en [a, b] (g' encerrada, finita y sin cero): a lo sumo una raíz; existencia
    solo si los signos en los extremos están DEMOSTRADOS y son opuestos, o si el encierro en un extremo es EXACTAMENTE
    cero (raíz en el extremo; la monotonía estricta excluye otra en el resto). La raíz se localiza hasta que el intervalo
    aislante mide <= xtol Y la cota demostrada de |g| en el punto publicado es <= tol_res (el residuo publicado es esa
    cota, no una evaluación en flotante); si no se alcanza, la raíz queda no convergida."""
    ea, eb = _point(ev, a), _point(ev, b)
    sa, sb = _sign(ea), _sign(eb)
    exact_a = ea.lo == 0.0 and ea.hi == 0.0
    exact_b = eb.lo == 0.0 and eb.hi == 0.0
    if exact_a or exact_b:
        for x, ex in ((a, exact_a), (b, exact_b)):
            if ex and not any(r.lo <= x <= r.hi for r in out.roots):
                kind = "boundary" if x in (lo, hi) else "crossing"
                out.roots.append(Root1D(x, x, x, 0.0, kind, True, True, existence=True, multiplicity=1))
        if not (exact_a and exact_b):
            out.certified_empty.append((a, b))      # monotonía estricta: ninguna otra raíz en el resto de [a, b]
        return
    if sa != 0 and sb != 0:
        if sa == sb:
            out.certified_empty.append((a, b))
            return
        x0, x1 = a, b
        mind = min(abs(d1.lo), abs(d1.hi))
        xr, res = None, math.inf
        while True:
            m = 0.5 * (x0 + x1)
            if not (x0 < m < x1):
                break
            gm = _point(ev, m)
            s = _sign(gm)
            if s == 0:
                # |g(m)| por debajo de la resolución del encierro: la raíz está a distancia <= |g(m)|/min|g'| de m, con
                # min|g'| sobre el intervalo ACTUAL (más ajustado que sobre la caja monótona original); dos pasadas
                for _ in range(2):
                    dc = ev.d1(x0, x1)
                    if math.isfinite(dc.lo) and math.isfinite(dc.hi) and _sign(dc) != 0:
                        mind = max(mind, min(abs(dc.lo), abs(dc.hi)))
                    w = _bound(gm) / mind if mind > 0 else x1 - x0
                    x0, x1 = max(x0, m - w), min(x1, m + w)
                xr, res = m, _bound(gm)
                break
            if s == sa:
                x0 = m
            else:
                x1 = m
            if x1 - x0 <= xtol:
                xm = 0.5 * (x0 + x1)
                r = _bound(_point(ev, xm))
                if r <= tol_res:
                    xr, res = xm, r
                    break
        if xr is None:
            xr = 0.5 * (x0 + x1)
            res = _bound(_point(ev, xr))
        conv = (x1 - x0) <= max(xtol, 4 * math.ulp(max(abs(xr), 1.0))) and res <= tol_res
        out.roots.append(Root1D(xr, x0, x1, res, "crossing", conv, True, existence=True, multiplicity=1))
        return
    # algún extremo con encierro que contiene el cero: sin prueba de existencia ni de ausencia
    reason = "BOUNDARY_ZERO_NOT_DECIDABLE" if (a == lo and sa == 0) or (b == hi and sb == 0) else "ROOT_AT_UNRESOLVED_SPLIT"
    out.pending.append((a, b, reason))
    x = a if sa == 0 else b
    out.candidates.append((x, abs(g(x)), "unresolved_endpoint_zero"))


# ============================================================================================ ruta exacta (polinomios)
def _P(coeffs) -> list:
    """Coeficientes (mayor a menor grado) como racionales exactos; se eliminan ceros líderes."""
    p = [Fraction(c) for c in coeffs]
    while len(p) > 1 and p[0] == 0:
        p.pop(0)
    return p


def _mul(p, q):
    out = [Fraction(0)] * (len(p) + len(q) - 1)
    for i, x in enumerate(p):
        for j, y in enumerate(q):
            out[i + j] += x * y
    return out


def _deriv(p):
    n = len(p) - 1
    return [c * (n - i) for i, c in enumerate(p[:-1])] or [Fraction(0)]


def _is_zero(p):
    return all(c == 0 for c in p)


def _divmod(n, d):
    n = list(n)
    if _is_zero(d):
        raise ZeroDivisionError
    q = [Fraction(0)] * max(1, len(n) - len(d) + 1)
    while len(n) >= len(d) and not _is_zero(n):
        coef = n[0] / d[0]
        k = len(n) - len(d)
        q[len(q) - 1 - k] = coef
        for i in range(len(d)):
            n[i] -= coef * d[i]
        n.pop(0)
    while len(n) > 1 and n[0] == 0:
        n.pop(0)
    return q, (n or [Fraction(0)])


def _gcd(p, q):
    a, b = _P(p), _P(q)
    while not _is_zero(b):
        _, r = _divmod(a, b)
        a, b = b, _P(r)
    return [c / a[0] for c in a]


def _eval(p, x: Fraction) -> Fraction:
    acc = Fraction(0)
    for c in p:
        acc = acc * x + c
    return acc


def _sub(p, q):
    n = max(len(p), len(q))
    p = [Fraction(0)] * (n - len(p)) + list(p)
    q = [Fraction(0)] * (n - len(q)) + list(q)
    return _P([x - y for x, y in zip(p, q)])


def _squarefree(p):
    """Yun: p = c * prod_i q_i^i con q_i libres de cuadrados y coprimos; devuelve [(q_i, i)] con grado >= 1."""
    p = _P(p)
    dp = _deriv(p)
    a = _gcd(p, dp)
    b, _ = _divmod(p, a)
    c, _ = _divmod(dp, a)
    b, c = _P(b), _P(c)
    d = _sub(c, _deriv(b))
    out, i = [], 1
    while len(b) > 1:
        a = _gcd(b, d) if not _is_zero(d) else b
        if len(a) > 1:
            out.append((a, i))
        b, _ = _divmod(b, a)
        c, _ = _divmod(d, a) if not _is_zero(d) else ([Fraction(0)], None)
        b, c = _P(b), _P(c)
        d = _sub(c, _deriv(b))
        i += 1
    return out


def _sturm(p):
    seq = [_P(p), _P(_deriv(p))]
    while not _is_zero(seq[-1]) and len(seq[-1]) > 1:
        _, r = _divmod(seq[-2], seq[-1])
        r = [-x for x in _P(r)]
        if _is_zero(r):
            break
        seq.append(r)
    return seq


def _variations(seq, x: Fraction) -> int:
    signs = [s for s in ((_eval(p, x) > 0) - (_eval(p, x) < 0) for p in seq) if s != 0]
    return sum(1 for u, v in zip(signs, signs[1:]) if u != v)


def _count(seq, a: Fraction, b: Fraction) -> int:
    """Raíces distintas de un polinomio libre de cuadrados en (a, b]."""
    return _variations(seq, a) - _variations(seq, b)


def _certified_poly(g, lo, hi, exact, xtol, out: RootSearch, tol_res: float = 1e-9) -> None:
    """Ruta exacta: residuo publicado = |P(x)| EXACTO en el punto publicado (racionales); se localiza hasta ancho <= xtol
    y residuo <= tol_res o hasta la resolución de coma flotante (entonces, no convergida si no se alcanzó)."""
    out.coverage = "certified"
    factors, scale = exact
    if Fraction(scale) == 0 or any(_is_zero(_P(f)) for f in factors):
        out.zero_intervals.append((lo, hi))
        return
    P = [Fraction(scale)]
    for f in factors:
        P = _mul(P, _P(f))
    if len(P) == 1:
        out.certified_empty.append((lo, hi))
        return
    L, H = Fraction(lo), Fraction(hi)
    tol = Fraction(xtol) if xtol > 0 else Fraction(1, 2 ** 60)
    tres = Fraction(tol_res)

    def resid(xf: float) -> Fraction:
        return abs(_eval(P, Fraction(xf)))
    for q, mult in _squarefree(P):
        seq = _sturm(q)
        stack = [(L, H)]
        isolated = []
        if _eval(q, L) == 0:
            isolated.append((L, L))
        while stack:
            a, b = stack.pop()
            n = _count(seq, a, b)
            if n == 0:
                continue
            if n == 1:
                isolated.append((a, b))
                continue
            m = (a + b) / 2
            stack.append((m, b))
            stack.append((a, m))
        for a, b in isolated:
            if a == b:
                x0 = x1 = a
            else:
                x0, x1 = a, b
                if _eval(q, b) == 0:
                    x0 = x1 = b
                floor = Fraction(1, 2 ** 60) * max(1, abs(x0))
                while x0 != x1 and x1 - x0 > floor and (x1 - x0 > tol or resid(float((x0 + x1) / 2)) > tres):
                    m = (x0 + x1) / 2
                    vm = _eval(q, m)
                    if vm == 0:
                        x0 = x1 = m
                        break
                    if _count(seq, x0, m) == 1:
                        x1 = m
                    else:
                        x0 = m
            x = float((x0 + x1) / 2)
            r = resid(x)
            exact_at_end = (x0 == x1) and (x0 == L or x0 == H)
            kind = "boundary" if exact_at_end else ("tangent" if mult % 2 == 0 else "crossing")
            conv = (x1 - x0) <= max(tol, Fraction(4 * math.ulp(max(abs(x), 1.0)))) and r <= tres
            out.roots.append(Root1D(x, float(x0), float(x1), float(r), kind, conv, True, existence=True,
                                    multiplicity=mult))


# ============================================================================================ evidencia polinómica
def evidence_from_factors(factors, *, scale: float = 1.0, source: str) -> Evidence1D:
    """Evidencia para g = scale * prod_i p_i(x) con polinomios p_i de coeficientes exactos (mayor a menor grado).
    Encierros de rango, g' y g'' por la regla del producto; además `exact_poly` habilita la ruta exacta (racionales)."""
    from .intervalos import poly, poly_deriv, poly_eval
    ps = [list(p) for p in factors]
    d1s = [poly_deriv(p) for p in ps]
    d2s = [poly_deriv(d) for d in d1s]

    def enc(a, b):
        x = Iv(a, b)
        return [poly(p, x) for p in ps], [poly(d, x) for d in d1s], [poly(d, x) for d in d2s]

    def prod(ivs, skip=()):
        acc = Iv.point(scale)
        for k, v in enumerate(ivs):
            if k not in skip:
                acc = acc * v
        return acc

    def rng(a, b):
        return prod(enc(a, b)[0])

    def d1(a, b):
        P, D1, _ = enc(a, b)
        acc = Iv.point(0.0)
        for i in range(len(P)):
            acc = acc + D1[i] * prod(P, skip=(i,))
        return acc

    def d2(a, b):
        P, D1, D2 = enc(a, b)
        acc = Iv.point(0.0)
        for i in range(len(P)):
            acc = acc + D2[i] * prod(P, skip=(i,))
            for j in range(len(P)):
                if j != i:
                    acc = acc + D1[i] * D1[j] * prod(P, skip=(i, j))
        return acc

    def deriv(x):
        vals = [poly_eval(p, x) for p in ps]
        out = 0.0
        for i in range(len(ps)):
            t = scale * poly_eval(d1s[i], x)
            for j, v in enumerate(vals):
                if j != i:
                    t *= v
            out += t
        return out
    return Evidence1D(range=rng, d1=d1, d2=d2, deriv=deriv, source=source, exact_poly=(ps, scale))


def without_exact(ev: Evidence1D) -> Evidence1D:
    """La misma evidencia sin la ruta exacta (para probar la ruta general por encierros)."""
    return Evidence1D(range=ev.range, d1=ev.d1, d2=ev.d2, deriv=ev.deriv, source=ev.source + "+encierros",
                      range_goal=ev.range_goal)


def shift_evidence(ev: Evidence1D, k: float) -> Evidence1D:
    """Evidencia de g - k a partir de la de g (rango desplazado; derivadas iguales; ruta exacta conservada)."""
    exact = None
    if ev.exact_poly is not None:
        factors, scale = ev.exact_poly
        P = [Fraction(scale)]
        for f in factors:
            P = _mul(P, _P(f))
        P = list(P)
        P[-1] -= Fraction(k)
        exact = ([P], 1)
    goal = None
    if ev.range_goal is not None:
        goal = lambda a, b, level: ev.range_goal(a, b, level + k) - k  # noqa: E731
    return Evidence1D(range=lambda a, b: ev.range(a, b) - k, d1=ev.d1, d2=ev.d2, deriv=ev.deriv, source=ev.source,
                      exact_poly=exact, range_goal=goal)
