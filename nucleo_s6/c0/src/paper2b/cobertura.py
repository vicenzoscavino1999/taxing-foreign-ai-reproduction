"""Cobertura del continuo estructural (ESTRATEGIA_DE_CALCULO §4-§6): partición en cajas, refinamiento y certificación.

- Partición: por eje estructural, intervalos entre nudos consecutivos del nivel (eje singleton = intervalo degenerado).
  Las cajas son el producto de esos intervalos; se ENUMERAN PEREZOSAMENTE (nunca se materializa el producto) y su
  número se obtiene por multiplicación.
- Certificación de una caja para una afirmación: para cada contexto del universo del claim (diseño, menú, caso D4
  disponible, país, estado nacional, vértice macro —reducción demostrada—, capa/cota con su Q mínimo) se encierra
  G = C2 - K1 sobre la caja con aritmética de intervalos: C2 con el encierro DEMOSTRATIVO del proveedor de modelo y
  K1 = (Q_min + D)/(lambda y) con lambda = s_Pi/(1 - q_pot(a, rho, kappa)) por intervalos. Clase de la caja:
  'infeasible' si G.hi <= -eps en todo contexto, 'feasible' si G.lo >= eps, 'mixed' si todas determinadas pero
  distintas, 'pending' si alguna queda indeterminada tras refinar (bisección del eje más ancho hasta max_depth).
- Sin encierro (modelo teórico) o con admisibilidad no demostrada en toda la caja: la caja queda 'pending'. Nunca se
  convierte pendiente en completo, no se reemplaza un soporte continuo por puntos, no se supone monotonía no
  demostrada, dos mallas estables no cuentan como cobertura y no hallar raíz no declara inexistencia.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from itertools import product

from .intervalos import Iv

STRUCT = ("a", "beta_tilde", "eta_d", "eta_f", "kappa_tilde", "phi", "rho", "u_theta", "z_cost")


def axis_intervals(nodes) -> list:
    vs = [float(x) for x in nodes]
    if len(vs) == 1:
        return [(vs[0], vs[0])]
    return [(vs[k], vs[k + 1]) for k in range(len(vs) - 1)]


def n_boxes(axes: dict) -> int:
    n = 1
    for pid in STRUCT:
        n *= len(axes[pid])
    return n


def boxes(axes: dict, prefix: dict | None = None):
    """Cajas en orden determinista; `prefix` {pid: índice} restringe ejes iniciales (unidad de trabajo)."""
    lists = []
    for pid in STRUCT:
        ivs = axes[pid]
        if prefix and pid in prefix:
            k = prefix[pid]
            ivs = [ivs[k]] if k < len(ivs) else []
        lists.append(ivs)
    for combo in product(*lists):
        yield dict(zip(STRUCT, combo))


def box_admissible(box: dict, fixed: dict) -> bool:
    """Dominio teórico (model.derive) y q_pot < 1 demostrados en TODA la caja por intervalos (condiciones estrictas)."""
    a, rho, u = Iv(*box["a"]), Iv(*box["rho"]), Iv(*box["u_theta"])
    k, bt, z = Iv(*box["kappa_tilde"]), Iv(*box["beta_tilde"]), Iv(*box["z_cost"])
    if not (k.lo > 0 and bt.lo > 0 and z.lo > 0 and a.lo > 1.0 and u.lo > 0.0 and u.hi < 1.0 and rho.hi <= 1.0 and rho.lo > 0.0):
        return False
    if not (a - rho).lo > 0:
        return False
    if float(fixed.get("c_legal", 1)) != 1 or float(fixed.get("t", 0)) != 0:
        return False
    if not (float(fixed.get("gamma", 1)) > 0 and float(fixed.get("z_m", 1)) > 0):
        return False
    return q_pot(box).hi < 1.0


def q_pot(box: dict) -> Iv:
    a, rho, k = Iv(*box["a"]), Iv(*box["rho"]), Iv(*box["kappa_tilde"])
    return k * (a - 1.0) / (a - rho)


@dataclass
class Context:
    design: str
    instrument: str
    bars: tuple
    s_pi: float               # s_Pi_marg del vértice macro y estado nacional (no depende de la estructura)
    s_t: float
    eta_h: float
    gain: float
    n_min: float              # Q_min + DME_gAI del universo (capa, cota, país)


def g_enclosure(model, box: dict, ctx: Context, fixed: dict | None = None, c2: Iv | None = None):
    if c2 is None:
        c2 = model.c2_struct_enclosure(box, ctx.design, ctx.instrument, ctx.bars[0], ctx.bars[1], fixed=fixed)
    if c2 is None:
        return None
    if not (ctx.s_pi > 0 and ctx.s_t >= 0 and ctx.eta_h > -1 and ctx.gain > 0):
        return None
    lam = ctx.s_pi / (1.0 - q_pot(box))
    if not lam.lo > 0:
        return None
    k1 = ctx.n_min / (lam * ctx.gain)
    return c2 - k1


def classify(g: Iv | None, eps: float) -> str | None:
    if g is None:
        return None
    if g.hi <= -eps:
        return "infeasible"
    if g.lo >= eps:
        return "feasible"
    return None


def _split(box: dict) -> tuple[dict, dict] | None:
    best, w = None, 0.0
    for pid in STRUCT:
        lo, hi = box[pid]
        rel = (hi - lo) / max(abs(hi), abs(lo), 1e-300)
        if rel > w:
            best, w = pid, rel
    if best is None or w == 0.0:
        return None
    lo, hi = box[best]
    mid = lo + (hi - lo) / 2
    return dict(box, **{best: (lo, mid)}), dict(box, **{best: (mid, hi)})


@dataclass
class BoxResult:
    klass: str                 # infeasible | feasible | mixed | pending | evaluated (caja degenerada = nudo evaluado)
    n_leaves: int = 1
    n_pending: int = 0
    max_width: float = 0.0
    reasons: list = field(default_factory=list)


_C2_MEMO: dict = {}


def clase_c2(design: str, instrument: str) -> str:
    """Clave de cálculo de C2: G y N COMPARTEN encierro SOLO en el menú f (τ_d = 0: trinomios iguales, A solo en B_d
    multiplicado por τ_d, curvas de salto iguales; demostración y comprobación numérica en el área 3.7). En df y d no."""
    return "GN" if instrument == "f" else design


def c2_encierro(model, box: dict, design: str, instrument: str, bars, fixed: dict):
    """Encierro normalizado de C2 (c2_normalizado, V1-V5) con memo por (caja, clase, menú, cotas, fijos)."""
    from . import c2_normalizado as C2N
    from .modelos import ModeloTeorico
    if not isinstance(model, ModeloTeorico):
        # el encierro normalizado y la equivalencia G/N en f están demostrados para el MODELO TEÓRICO; otro proveedor
        # (p. ej. el sustituto sintético, cuyo C2 sí cambia con el diseño) usa su propio encierro y no comparte
        return model.c2_struct_enclosure(box, design, instrument, bars[0], bars[1], fixed=fixed)
    k = (tuple((p, box[p]) for p in STRUCT), clase_c2(design, instrument), instrument, tuple(bars),
         tuple(sorted((str(a), str(b)) for a, b in fixed.items())))
    if k not in _C2_MEMO:
        d = "G" if clase_c2(design, instrument) == "GN" else design
        _C2_MEMO[k] = C2N.c2_normalizado(model, box, d, instrument, bars[0], bars[1], fixed=fixed)
    return _C2_MEMO[k]


def testigo_de_fallo(model, box: dict, contexts: list, fixed: dict, want: str, eps: float):
    """Punto ADMISIBLE de la caja donde la afirmación robusta deja de sostenerse, certificado: para want = infeasible,
    algún contexto con G.lo > −eps (sup G > −eps); para want = feasible, G.hi < eps. Se sondean el centro y las 8
    esquinas de (κ̃, ρ, a) con el resto en el centro (K1 extrema: q_pot es monótono en los tres); C2 y K1 se evalúan en
    el MISMO punto. Devuelve el punto o None (no encontrar testigo no prueba nada)."""
    from itertools import product as _prod
    cen = {p: ((lo + hi) / 2,) * 2 for p, (lo, hi) in box.items()}
    pts = [cen] + [dict(cen, kappa_tilde=(box["kappa_tilde"][i],) * 2, rho=(box["rho"][j],) * 2, a=(box["a"][k],) * 2)
                   for i, j, k in _prod((1, 0), (1, 0), (0, 1))]

    def violacion(pt):
        """(medida, punto o None): max_c G.lo (want infeasible) o −min_c G.hi (want feasible); punto si certifica."""
        if not box_admissible(pt, fixed):
            return -float("inf"), None
        c2s, mejor = {}, -float("inf")
        for ctx in contexts:
            ck = (ctx.design, ctx.instrument, tuple(ctx.bars))
            if ck not in c2s:
                c2s[ck] = c2_encierro(model, pt, ctx.design, ctx.instrument, ctx.bars, fixed)
            if c2s[ck] is None:
                continue
            g = g_enclosure(model, pt, ctx, fixed, c2s[ck])
            if g is None:
                continue
            m = g.lo if want == "infeasible" else -g.hi
            mejor = max(mejor, m)
            if (want == "infeasible" and g.lo > -eps) or (want == "feasible" and g.hi < eps):
                return mejor, {p: v[0] for p, v in pt.items()}
        return mejor, None
    for pt in pts:
        _, w = violacion(pt)
        if w is not None:
            return w
    # ascenso por coordenadas sobre VÉRTICES (2 barridas): solo elige dónde evaluar; el certificado es el encierro del punto
    cur = dict(cen)
    vcur, w = violacion(cur)
    for _ in range(2):
        for p in STRUCT:
            for v in box[p]:
                cand = dict(cur, **{p: (v, v)})
                vc, w = violacion(cand)
                if w is not None:
                    return w
                if vc > vcur:
                    cur, vcur = cand, vc
    return None


def niveles_union(axes: dict, prefix: dict | None = None) -> int:
    """ceil(log2(nº de cajas L0 de la unión)): niveles de bisección para llegar desde la unión al tamaño L0."""
    import math as _m
    n = 1
    for pid in STRUCT:
        n *= 1 if (prefix and pid in prefix) else max(1, len(axes[pid]))
    return int(_m.ceil(_m.log2(n))) if n > 1 else 0


def union_box(axes: dict, prefix: dict | None = None) -> dict:
    """Caja unión de las cajas L0 de `boxes(axes, prefix)` (producto de intervalos contiguos): la MISMA región."""
    out = {}
    for pid in STRUCT:
        ivs = axes[pid]
        if prefix and pid in prefix:
            k = prefix[pid]
            ivs = [ivs[k]] if k < len(ivs) else []
        if not ivs:
            return None
        for a, b in zip(ivs, ivs[1:]):
            assert a[1] == b[0], "EJES_NO_CONTIGUOS"
        out[pid] = (ivs[0][0], ivs[-1][1])
    return out


def certify_box(model, box: dict, contexts: list, fixed: dict, eps: float, max_depth: int) -> BoxResult:
    """Clase certificada de la caja para un universo de contextos, refinando hasta max_depth."""
    if not contexts:
        return BoxResult("pending", reasons=["EMPTY_UNIVERSE"])
    if not box_admissible(box, fixed):
        sub = _split(box) if max_depth > 0 else None
        if sub is None:
            return BoxResult("pending", n_pending=1, reasons=["ADMISSIBILITY_NOT_PROVEN_ON_BOX"])
        return _merge([certify_box(model, b, contexts, fixed, eps, max_depth - 1) for b in sub])
    classes = set()
    c2s: dict = {}
    for ctx in contexts:
        ck = (ctx.design, ctx.instrument, tuple(ctx.bars))
        if ck not in c2s:        # un encierro de C2 por (diseño, menú, cotas): los contextos solo cambian K1
            c2s[ck] = c2_encierro(model, box, ctx.design, ctx.instrument, ctx.bars, fixed)
        if c2s[ck] is None:
            return BoxResult("pending", n_pending=1, reasons=["MODEL_WITHOUT_DEMONSTRATIVE_ENCLOSURE"])
        g = g_enclosure(model, box, ctx, fixed, c2s[ck])
        c = classify(g, eps)
        if c is None:
            classes = None
            break
        classes.add(c)
    if classes is not None:
        return BoxResult(classes.pop() if len(classes) == 1 else "mixed",
                         max_width=max(hi - lo for lo, hi in box.values()))
    sub = _split(box) if max_depth > 0 else None
    if sub is None:
        return BoxResult("pending", n_pending=1, reasons=["UNDETERMINED_AT_MAX_DEPTH"])
    return _merge([certify_box(model, b, contexts, fixed, eps, max_depth - 1) for b in sub])


def _merge(parts: list) -> BoxResult:
    ks = {p.klass for p in parts}
    klass = "pending" if "pending" in ks else (ks.pop() if len(ks) == 1 else "mixed")
    return BoxResult(klass, sum(p.n_leaves for p in parts), sum(p.n_pending for p in parts),
                     max(p.max_width for p in parts), sorted({r for p in parts for r in p.reasons}))


@dataclass
class Tally:
    """Resumen acumulable (por unidad y global) de las clases de cajas de un claim."""
    n_boxes: int = 0
    evaluated: int = 0
    infeasible: int = 0
    feasible: int = 0
    mixed: int = 0
    pending: int = 0
    leaves: int = 0
    reasons: set = field(default_factory=set)

    def add(self, r: BoxResult):
        self.n_boxes += 1
        setattr(self, r.klass, getattr(self, r.klass) + 1)
        self.leaves += r.n_leaves
        self.reasons |= set(r.reasons)

    def merge(self, o: "Tally"):
        for k in ("n_boxes", "evaluated", "infeasible", "feasible", "mixed", "pending", "leaves"):
            setattr(self, k, getattr(self, k) + getattr(o, k))
        self.reasons |= set(o.reasons)

    def as_dict(self) -> dict:
        return {"n_boxes": self.n_boxes, "evaluated": self.evaluated, "infeasible": self.infeasible, "feasible": self.feasible,
                "mixed": self.mixed, "pending": self.pending, "leaves": self.leaves, "reasons": sorted(self.reasons)}

    @classmethod
    def of(cls, d: dict) -> "Tally":
        t = cls(**{k: d[k] for k in ("n_boxes", "evaluated", "infeasible", "feasible", "mixed", "pending", "leaves")})
        t.reasons = set(d.get("reasons", []))
        return t

    def covers(self, verdict: str) -> bool:
        want = {"robust_infeasible": "infeasible", "robust_feasible": "feasible"}.get(verdict)
        return want is not None and self.n_boxes > 0 and getattr(self, want) + self.evaluated == self.n_boxes


def dec_nodes(nodes) -> list:
    return [x if isinstance(x, Decimal) else Decimal(str(x)) for x in nodes]
