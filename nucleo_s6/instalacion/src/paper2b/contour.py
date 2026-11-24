"""R1: curva de nivel {tau : CS(tau) = K1} sobre el menú factible, por régimen (diseño §7.9, H23).

- Marching squares con valores y régimen (topología de adopción) en cada nodo.
- En una arista con cambio de signo se localiza el cero por Brent DENTRO de un mismo régimen. Si el régimen cambia a
  lo largo de la arista se localiza la frontera de régimen y se miden los límites laterales: si hay salto (> tol_jump)
  y el cambio de signo ocurre a través del salto, el cruce se RECHAZA y se registra con su caja y sus ramas.
- Componentes conexas por aristas compartidas; tipología closed_loop / open_arc / branched / isolated_point; el
  contacto con el borde se informa aparte (closed_curve solo si lazo cerrado sin extremos libres).
- Estabilidad: se repite con malla 2n; n_components y tipologías deben coincidir; error geométrico = Hausdorff
  simétrico entre los vértices de ambos niveles.
En menús unidimensionales (d o f) el conjunto de nivel son puntos aislados sobre el segmento.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from .numeric import brent
from .supremum import axes, nodes


@dataclass
class Vertex:
    vertex_id: int
    tau_d: float
    tau_f: float
    side: str
    branch_id: str
    residual: float
    is_boundary: bool
    boundary_label: str | None


@dataclass
class Edge:
    edge_id: int
    from_vertex_id: int
    to_vertex_id: int
    branch_id: str
    max_residual: float
    geometric_error_bound: float


@dataclass
class Component:
    component_id: int
    vertices: list
    edges: list
    arc_length: float
    closed_curve: bool
    topology_kind: str
    n_boundary_intersections: int


@dataclass
class Crossing:
    crossing_id: int
    box: tuple
    branch_left: str
    branch_right: str
    reason_code: str


@dataclass
class R1Result:
    components: list = field(default_factory=list)
    rejected: list = field(default_factory=list)
    n: int = 0
    topology_stable: bool = False
    residual_bound: float | None = None
    geometry_error_bound: float | None = None
    status: str = "incomplete"
    reason: str | None = None
    kink_adjacent: bool = False
    n_coarse: int = 0
    certified: bool = False
    # garantías por separado (ruta certificada): cobertura del conjunto de cruces, localización demostrada y residuo
    # demostrado; 'complete' exige las tres dentro de su tolerancia
    diagnostics: dict = field(default_factory=dict)


def _position_bound(r) -> float:
    """Cota DEMOSTRADA de la distancia entre el punto publicado r.x y la raíz: la raíz está en [r.lo, r.hi] (intervalo
    aislante demostrado), así que |raíz - r.x| <= max(r.x - r.lo, r.hi - r.x), redondeado hacia arriba."""
    d = max(r.x - r.lo, r.hi - r.x)
    return 0.0 if d == 0.0 else math.nextafter(d, math.inf)


def _boundary_label(x, y, box, tol=0.0):
    (dl, dh), (fl, fh) = box
    labels = []
    if abs(x - dl) <= tol and dh > dl:
        labels.append("tau_d_0")
    if abs(x - dh) <= tol and dh > dl:
        labels.append("tau_d_bar")
    if abs(y - fl) <= tol and fh > fl:
        labels.append("tau_f_0")
    if abs(y - fh) <= tol and fh > fl:
        labels.append("tau_f_bar")
    return "+".join(labels) if labels else None


class _Edge1D:
    """Arista de malla parametrizada: localiza ceros por régimen y rechaza cruces a través de saltos."""

    def __init__(self, f, regime, jump_tol):
        self.f, self.regime, self.jump_tol = f, regime, jump_tol

    def crossing(self, p0, p1, v0, v1, r0, r1):
        """Devuelve ('zero', (x,y), branch) | ('rejected', box, bl, br) | None."""
        f, regime = self.f, self.regime

        def at(t):
            return (p0[0] + t * (p1[0] - p0[0]), p0[1] + t * (p1[1] - p0[1]))

        if v0 == 0.0:
            return ("zero", p0, r0)
        if v1 == 0.0:
            return ("zero", p1, r1)
        if (v0 > 0) == (v1 > 0):
            return None
        if r0 == r1:
            t = brent(lambda s: f(*at(s)), 0.0, 1.0, v0, v1)
            return ("zero", at(t), r0)
        # cambio de régimen en la arista: ubicar la frontera por bisección sobre la etiqueta
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if regime(*at(mid)) == r0:
                lo = mid
            else:
                hi = mid
        fl, fr = f(*at(lo)), f(*at(hi))
        jump = abs(fl - fr) > self.jump_tol
        if not jump:
            # kink continuo: el cero es válido; se busca en el tramo con cambio de signo
            if (v0 > 0) != (fl > 0) or fl == 0.0:
                t = brent(lambda s: f(*at(s)), 0.0, lo, v0, fl) if fl != 0.0 else lo
                return ("zero", at(t), r0)
            t = brent(lambda s: f(*at(s)), hi, 1.0, fr, v1) if fr != 0.0 else hi
            return ("zero", at(t), r1)
        if (v0 > 0) != (fl > 0):
            t = brent(lambda s: f(*at(s)), 0.0, lo, v0, fl)
            return ("zero", at(t), r0)
        if (fr > 0) != (v1 > 0):
            t = brent(lambda s: f(*at(s)), hi, 1.0, fr, v1)
            return ("zero", at(t), r1)
        a, b = at(lo), at(hi)
        return ("rejected", (min(a[0], b[0]), max(a[0], b[0]), min(a[1], b[1]), max(a[1], b[1])), r0, r1)


def _components_from_segments(points, segments, box, residual_of):
    adj: dict[int, set] = {}
    for a, b in segments:
        if a == b:
            continue
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    for k in points:
        adj.setdefault(k, set())
    seen = set()
    comps = []
    for start in sorted(adj, key=lambda k: (points[k][1][0], points[k][1][1], k)):
        if start in seen:
            continue
        stack, members = [start], []
        seen.add(start)
        while stack:
            u = stack.pop()
            members.append(u)
            for w in sorted(adj[u]):
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        comps.append(sorted(members, key=lambda k: (points[k][1][0], points[k][1][1], k)))
    out = []
    for cid, members in enumerate(comps):
        index = {k: i for i, k in enumerate(members)}
        verts = []
        for k in members:
            (x, y), branch = points[k][1], points[k][2]
            lab = _boundary_label(x, y, box)
            verts.append(Vertex(index[k], x, y, "point", branch, residual_of(x, y), lab is not None, lab))
        edges = []
        length = 0.0
        for a in members:
            for b in sorted(adj[a]):
                if index[a] < index[b]:
                    xa, ya = points[a][1]
                    xb, yb = points[b][1]
                    length += math.hypot(xb - xa, yb - ya)
                    mid = residual_of((xa + xb) / 2, (ya + yb) / 2)
                    edges.append(Edge(len(edges), index[a], index[b], points[a][2], mid, 0.0))
        degrees = [len(adj[k]) for k in members]
        nb = sum(1 for v in verts if v.is_boundary)
        if len(members) == 1:
            kind = "isolated_point"
        elif any(d >= 3 for d in degrees):
            kind = "branched"
        elif all(d == 2 for d in degrees):
            kind = "closed_loop"
        else:
            kind = "open_arc"
        closed = kind == "closed_loop" and not any(d == 1 for d in degrees)
        out.append(Component(cid, verts, edges, length, closed, kind, nb))
    return out


def _level(f, regime, instrument, bar_d, bar_f, n, jump_tol):
    box = axes(instrument, bar_d, bar_f)
    (dl, dh), (fl, fh) = box
    dn = nodes(dl, dh, n) if dh > dl else [dl]
    fn = nodes(fl, fh, n) if fh > fl else [fl]
    val = {(i, j): f(x, y) for i, x in enumerate(dn) for j, y in enumerate(fn)}
    reg = {(i, j): regime(x, y) for i, x in enumerate(dn) for j, y in enumerate(fn)}
    E = _Edge1D(f, regime, jump_tol)
    points: dict = {}
    rejected = []
    kink = False

    nonlocal_kink = [False]
    edge_cache: dict = {}

    def edge_point(i0, j0, i1, j1):
        """Clave canónica del cero de la arista (compartida entre celdas) o None."""
        key = ("e", min((i0, j0), (i1, j1)), max((i0, j0), (i1, j1)))
        if key in edge_cache:
            return edge_cache[key]
        p0, p1 = (dn[i0], fn[j0]), (dn[i1], fn[j1])
        res = E.crossing(p0, p1, val[(i0, j0)], val[(i1, j1)], reg[(i0, j0)], reg[(i1, j1)])
        if res is None:
            edge_cache[key] = None
            return None
        if res[0] == "rejected":
            edge_cache[key] = None
            rejected.append(res)
            return None
        _, pt, branch = res
        nonlocal_kink[0] |= reg[(i0, j0)] != reg[(i1, j1)]
        if pt == p0 and val[(i0, j0)] == 0.0:
            canon = ("n", (i0, j0))      # un cero exactamente en un nodo se comparte entre aristas
        elif pt == p1 and val[(i1, j1)] == 0.0:
            canon = ("n", (i1, j1))
        else:
            canon = key
        points.setdefault(canon, (canon, pt, str(branch)))
        edge_cache[key] = canon
        return canon
    segments = []
    if len(dn) > 1 and len(fn) > 1:
        for i in range(len(dn) - 1):
            for j in range(len(fn) - 1):
                es = [edge_point(i, j, i + 1, j), edge_point(i + 1, j, i + 1, j + 1),
                      edge_point(i, j + 1, i + 1, j + 1), edge_point(i, j, i, j + 1)]
                hits = [e for e in dict.fromkeys(e for e in es if e is not None)]
                if len(hits) == 2:
                    segments.append((hits[0], hits[1]))
                elif len(hits) == 4:
                    center = f((dn[i] + dn[i + 1]) / 2, (fn[j] + fn[j + 1]) / 2)
                    s_sw = val[(i, j)] > 0
                    if (center > 0) == s_sw:
                        segments += [(hits[0], hits[1]), (hits[2], hits[3])]
                    else:
                        segments += [(hits[0], hits[3]), (hits[1], hits[2])]
                elif len(hits) == 3:
                    segments += [(hits[0], hits[1]), (hits[1], hits[2])]
        # nodos con valor cero exacto sin aristas adyacentes: punto aislado
        for (i, j), v in val.items():
            if v == 0.0 and ("n", (i, j)) not in points:
                points[("n", (i, j))] = (("n", (i, j)), (dn[i], fn[j]), str(reg[(i, j)]))
    else:
        line = [(dn[i], fn[0], (i, 0)) for i in range(len(dn))] if len(dn) > 1 else [(dn[0], fn[j], (0, j)) for j in range(len(fn))]
        for k in range(len(line) - 1):
            a, b = line[k][2], line[k + 1][2]
            edge_point(a[0], a[1], b[0], b[1])
        for idx, (x, y, ij) in enumerate(line):
            if val[ij] == 0.0 and ("n", ij) not in points:
                points[("n", ij)] = (("n", ij), (x, y), str(reg[ij]))
    real = {k: v for k, v in points.items() if v is not None and v[0] == k}
    comps = _components_from_segments(real, [(a, b) for a, b in segments], box, lambda x, y: abs(f(x, y)))
    crossings = [Crossing(k, r[1], str(r[2]), str(r[3]), "DISCONTINUITY_CROSSING") for k, r in enumerate(rejected)]
    return comps, crossings, nonlocal_kink[0]


def _seg_dist(p, a, b) -> float:
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0.0 if L == 0.0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def _polyline_distance(points: list, comps: list) -> float:
    """Distancia máxima de puntos (nivel grueso) a la polilínea fina (aristas y vértices aislados)."""
    segs = []
    iso = []
    for c in comps:
        coords = {v.vertex_id: (v.tau_d, v.tau_f) for v in c.vertices}
        if not c.edges:
            iso.extend(coords.values())
        for e in c.edges:
            segs.append((coords[e.from_vertex_id], coords[e.to_vertex_id]))
    if not points:
        return 0.0
    if not segs and not iso:
        return math.inf
    worst = 0.0
    for p in points:
        d = min([_seg_dist(p, a, b) for a, b in segs] + [math.hypot(p[0] - q[0], p[1] - q[1]) for q in iso])
        worst = max(worst, d)
    return worst


def _sagitta(f, comps, h=1e-7) -> float:
    """Cota de primer orden de la distancia de cada arista a la curva: |f(medio)|/|grad f(medio)|."""
    worst = 0.0
    for c in comps:
        coords = {v.vertex_id: (v.tau_d, v.tau_f) for v in c.vertices}
        for e in c.edges:
            (xa, ya), (xb, yb) = coords[e.from_vertex_id], coords[e.to_vertex_id]
            mx, my = (xa + xb) / 2, (ya + yb) / 2
            v = f(mx, my)
            gx = (f(mx + h, my) - f(mx - h, my)) / (2 * h)
            gy = (f(mx, my + h) - f(mx, my - h)) / (2 * h)
            gn = math.hypot(gx, gy)
            bound = abs(v) / gn if gn > 0 else math.inf
            e.geometric_error_bound = bound
            worst = max(worst, bound)
    return worst


def level_set(f, regime, instrument: str, bar_d: float, bar_f: float, *, n: int = 16, jump_tol: float = 1e-9,
              evidence=None, max_level: int = 6, geometry_tol: float = 1e-3, tol_residual: float = 1e-9) -> R1Result:
    """R1. Con `evidence` (Evidence2D demostrativa) el conjunto de nivel se CERTIFICA (level_set_certified). Sin ella,
    marching squares n y 2n solo aportan HALLAZGOS: dos mallas estables no certifican ausencia de componentes entre nudos
    (ESTRATEGIA §5 y §8), así que el estado es `incomplete` con motivo CONTOUR_COVERAGE_NOT_CERTIFIED."""
    if evidence is not None:
        return level_set_certified(f, instrument, bar_d, bar_f, evidence, n0=max(1, n), max_level=max_level,
                                   geometry_tol=geometry_tol, tol_residual=tol_residual)
    c1, x1, k1 = _level(f, regime, instrument, bar_d, bar_f, n, jump_tol)
    c2, x2, k2 = _level(f, regime, instrument, bar_d, bar_f, 2 * n, jump_tol)
    kinds1 = sorted(c.topology_kind for c in c1)
    kinds2 = sorted(c.topology_kind for c in c2)
    res = R1Result(components=c2, rejected=x2, n=2 * n, kink_adjacent=k1 or k2, n_coarse=len(c1))
    res.topology_stable = len(c1) == len(c2) and kinds1 == kinds2
    pts1 = [(v.tau_d, v.tau_f) for c in c1 for v in c.vertices]
    res.geometry_error_bound = max(_polyline_distance(pts1, c2), _sagitta(f, c2))
    res.residual_bound = max((v.residual for c in c2 for v in c.vertices), default=0.0)
    res.status = "incomplete"
    res.reason = "CONTOUR_COVERAGE_NOT_CERTIFIED" if res.topology_stable else "TOPOLOGY_UNSTABLE_UNDER_REFINEMENT"
    res.certified = False
    return res


@dataclass
class Evidence2D:
    """Encierros demostrativos de f = CS - K1 en cajas (x0, x1, y0, y1) y derivadas puntuales para cruces tangentes."""
    range: object
    dx: object
    dy: object
    dxx: object
    dyy: object
    fx: object
    fy: object
    source: str = ""


def _edge_roots(f, ev, fixed_axis: str, c: float, a: float, b: float, tol_residual: float):
    from .raices import Evidence1D, find_roots
    if fixed_axis == "y":
        e1 = Evidence1D(range=lambda s, t: ev.range(s, t, c, c), d1=lambda s, t: ev.dx(s, t, c, c),
                        d2=lambda s, t: ev.dxx(s, t, c, c), deriv=lambda s: ev.fx(s, c), source=ev.source)
        rs = find_roots(lambda s: f(s, c), a, b, evidence=e1, tol_residual=tol_residual)
        pts = [((r.x, c), r) for r in rs.roots]
    else:
        e1 = Evidence1D(range=lambda s, t: ev.range(c, c, s, t), d1=lambda s, t: ev.dy(c, c, s, t),
                        d2=lambda s, t: ev.dyy(c, c, s, t), deriv=lambda s: ev.fy(c, s), source=ev.source)
        rs = find_roots(lambda s: f(c, s), a, b, evidence=e1, tol_residual=tol_residual)
        pts = [((c, r.x), r) for r in rs.roots]
    return rs, pts


def level_set_certified(f, instrument: str, bar_d: float, bar_f: float, ev, *, n0: int = 4, max_level: int = 6,
                        geometry_tol: float = 1e-3, tol_residual: float = 1e-9, checkpoint=None) -> R1Result:
    """INTEGRACIÓN CANDIDATA 3.7: en 2-D delega en r1_reanudable (v4: controles de raíces, comprobación final,
    subdivisión local m = 4 / profundidad 4 y dirección adaptativa por ramas; checkpoint opcional, en memoria si no se
    da ruta). La ruta 1-D (menú f o d) no cambia."""
    (dl, dh), (fl, fh) = axes(instrument, bar_d, bar_f)
    if dh > dl and fh > fl:
        from . import r1_reanudable as RV
        ck = checkpoint if checkpoint is not None else RV.Checkpoint(None, {"r1": "memoria", "instrumento": instrument,
                                                                            "barras": [bar_d, bar_f], "n0": n0, "max_level": max_level})
        return RV.level_set_reanudable(f, instrument, bar_d, bar_f, ev, n0=n0, max_level=max_level, geometry_tol=geometry_tol,
                                       tol_residual=tol_residual, checkpoint=ck, local={"m": 4, "profundidad": 4})
    return _level_set_certified_original(f, instrument, bar_d, bar_f, ev, n0=n0, max_level=max_level, geometry_tol=geometry_tol,
                                         tol_residual=tol_residual)


def _level_set_certified_original(f, instrument: str, bar_d: float, bar_f: float, ev, *, n0: int = 4, max_level: int = 6,
                                  geometry_tol: float = 1e-3, tol_residual: float = 1e-9) -> R1Result:
    """Conjunto de nivel CERTIFICADO por refinamiento uniforme. Cada caja es vacía (0 fuera del encierro) o monótona en
    una dirección (derivada parcial de signo estricto); los cruces de cada arista se certifican en 1-D; en una caja
    monótona en y el conjunto es un grafo sobre x y los cruces ordenados por x se emparejan de forma consecutiva (y
    viceversa). Cota geométrica certificada = diagonal máxima de las cajas con tramo (curva y segmento dentro de la
    caja). Cajas sin certificado al nivel máximo quedan pendientes: estado `incomplete`."""
    from .raices import Evidence1D, find_roots
    box = axes(instrument, bar_d, bar_f)
    (dl, dh), (fl, fh) = box
    res = R1Result()
    res.certified = True
    if dh == dl or fh == fl:
        if dh > dl:
            e1 = Evidence1D(range=lambda s, t: ev.range(s, t, fl, fl), d1=lambda s, t: ev.dx(s, t, fl, fl),
                            d2=lambda s, t: ev.dxx(s, t, fl, fl), deriv=lambda s: ev.fx(s, fl), source=ev.source)
            rs = find_roots(lambda s: f(s, fl), dl, dh, evidence=e1, tol_residual=tol_residual)
            pts = [((r.x, fl), r) for r in rs.roots]
        else:
            e1 = Evidence1D(range=lambda s, t: ev.range(dl, dl, s, t), d1=lambda s, t: ev.dy(dl, dl, s, t),
                            d2=lambda s, t: ev.dyy(dl, dl, s, t), deriv=lambda s: ev.fy(dl, s), source=ev.source)
            rs = find_roots(lambda s: f(dl, s), fl, fh, evidence=e1, tol_residual=tol_residual)
            pts = [((dl, r.x), r) for r in rs.roots]
        # la cobertura (todas las raíces aisladas, ninguna omitida) NO implica precisión: la posición se acota con el
        # intervalo aislante DEMOSTRADO de cada raíz y el residuo publicado es la cota demostrada de |f| en el punto
        pos = max((_position_bound(r) for _, r in pts), default=0.0)
        resid = max((r.residual for _, r in pts), default=0.0)
        res.diagnostics = {"cobertura_certificada": rs.status == "complete", "n_raices": len(pts),
                           "cota_posicion": pos, "cota_residuo": resid, "tolerancia_geometrica": geometry_tol,
                           "tolerancia_residuo": tol_residual, "pendientes": rs.pending[:10],
                           "hallazgos": [(r.x, r.lo, r.hi) for _, r in pts][:10]}
        res.n = 1
        if rs.status != "complete":
            res.status, res.reason = "incomplete", "CONTOUR_BOXES_UNRESOLVED"
            return res
        res.geometry_error_bound, res.residual_bound = pos, resid
        if pos > geometry_tol:
            res.status, res.reason = "incomplete", "GEOMETRY_TOLERANCE_NOT_REACHED"
            return res
        if resid > tol_residual:
            res.status, res.reason = "incomplete", "ROOT_RESIDUAL_ABOVE_TOLERANCE"
            return res
        points = {("p", k): (("p", k), p, "certificada") for k, (p, _) in enumerate(pts)}
        res.components = _components_from_segments(points, [], box, lambda x, y: abs(f(x, y)))
        res.status, res.reason, res.topology_stable = "complete", None, True
        return res
    active = [(i, j) for i in range(n0) for j in range(n0)]
    not_localized = False
    for level in range(max_level + 1):
        N = n0 * (2 ** level)
        X = lambda i, N=N: dl + (dh - dl) * i / N  # noqa: E731
        Y = lambda j, N=N: fl + (fh - fl) * j / N  # noqa: E731
        unresolved, pieces, diag, kept = [], [], 0.0, []
        edge_cache = {}

        def edge(axis, k, m, X=X, Y=Y, edge_cache=edge_cache):
            key = (axis, k, m)
            if key not in edge_cache:
                if axis == "h":
                    edge_cache[key] = _edge_roots(f, ev, "y", Y(k), X(m), X(m + 1), tol_residual)
                else:
                    edge_cache[key] = _edge_roots(f, ev, "x", X(k), Y(m), Y(m + 1), tol_residual)
            return edge_cache[key]
        # cajas vacías (encierro sin cero en la caja CERRADA) se descartan y no se refinan: la curva no toca su borde,
        # así que las cajas no vacías, todas del mismo nivel, comparten aristas exactas (cruces consistentes)
        for i, j in active:
            x0, x1, y0, y1 = X(i), X(i + 1), Y(j), Y(j + 1)
            if ev.range(x0, x1, y0, y1).excludes_zero():
                continue
            kept.append((i, j))
            mono_y = ev.dy(x0, x1, y0, y1).excludes_zero()
            mono_x = (not mono_y) and ev.dx(x0, x1, y0, y1).excludes_zero()
            if not (mono_x or mono_y):
                unresolved.append((x0, x1, y0, y1))
                continue
            pts, ok = {}, True
            for axis, k, m in (("h", j, i), ("h", j + 1, i), ("v", i, j), ("v", i + 1, j)):
                rs, found = edge(axis, k, m)
                if rs.status != "complete" or any(r.kind == "tangent" for _, r in found):
                    ok = False
                    break
                # el vértice publicado está en su arista (la cota geométrica = diagonal lo cubre), pero su residuo
                # publicado debe ser una cota demostrada bajo la tolerancia: si no, la caja queda sin resolver
                if any(r.residual > tol_residual for _, r in found):
                    ok, not_localized = False, True
                    break
                for pt, r in found:
                    pts[(round(pt[0], 15), round(pt[1], 15))] = (pt, r)
            if not ok or len(pts) % 2:
                unresolved.append((x0, x1, y0, y1))
                continue
            order = sorted(pts.values(), key=lambda pr: (pr[0][0], pr[0][1]) if mono_y else (pr[0][1], pr[0][0]))
            for q in range(0, len(order), 2):
                pieces.append((order[q][0], order[q + 1][0], max(order[q][1].residual, order[q + 1][1].residual)))
            if order:
                diag = max(diag, math.hypot(x1 - x0, y1 - y0))
        active = [(2 * i + a, 2 * j + b) for i, j in kept for a in (0, 1) for b in (0, 1)]
        res.n = N
        if (unresolved or diag > geometry_tol) and level < max_level:
            continue
        if unresolved:
            res.status = "incomplete"
            res.reason = "EDGE_CROSSING_NOT_LOCALIZED" if not_localized else "CONTOUR_BOXES_UNRESOLVED"
            res.diagnostics = {"cajas_sin_resolver": len(unresolved), "nivel": level, "tolerancia_residuo": tol_residual}
            return res
        if diag > geometry_tol:
            # topología certificada pero la cota geométrica no alcanzó la tolerancia al nivel máximo: no se publica
            res.status, res.reason, res.geometry_error_bound = "incomplete", "GEOMETRY_TOLERANCE_NOT_REACHED", diag
            return res
        keyof, points = {}, {}
        for (pa, pb, _) in pieces:
            for pt in (pa, pb):
                k = ("q", round(pt[0], 12), round(pt[1], 12))
                keyof[pt] = k
                points.setdefault(k, (k, pt, "certificada"))
        segs = [(keyof[pa], keyof[pb]) for pa, pb, _ in pieces]
        res.components = _components_from_segments(points, segs, box, lambda x, y: abs(f(x, y)))
        for c in res.components:
            for e in c.edges:
                e.geometric_error_bound = diag
        res.geometry_error_bound = diag
        res.residual_bound = max((r for _, _, r in pieces), default=0.0)
        res.topology_stable = True
        res.status, res.reason = "complete", None
        return res
    return res
