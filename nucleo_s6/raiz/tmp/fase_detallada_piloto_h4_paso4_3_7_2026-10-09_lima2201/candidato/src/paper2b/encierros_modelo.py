"""Encierros DEMOSTRATIVOS del modelo teórico v2.2 (paper2b.model) sobre cajas de tasas, de phi y de primitivas.

Fundamento (review/FUNDAMENTO_ENCIERROS.md de la entrega):
1. Parámetros como intervalos: el estado puntual es una caja degenerada; una caja de primitivas se propaga por las
   fórmulas de derive() en aritmética de intervalos (theta, delta, kappa0, beta, B_pot).
2. Funciones de tasa en forma estable y con derivadas (aritmética de intervalos en modo directo sobre (tau_d, tau_f,
   phi)): l = log1p(-tau); tilde_d = -l E((1+eta_d) l); r* = e^(eta_d l); tilde_f = tau e^(alpha l) + eta_f (-l)
   [E(alpha l) - E((alpha+1) l)] con alpha = eta_f - phi y E(y) = expm1(y)/y (entera, creciente, E(0) = 1);
   q* = e^(eta_f l_f); x_f^(-phi) = e^(-phi l_f); k_F = kappa0 (1 + phi tilde_f).
3. Regímenes: cada diferencia de ganancias es un trinomio T_k(z) = A z^theta + B z + C z^rho con coeficientes
   encerrados. El eje s = ln z se parte en celdas; en una celda donde los seis encierros excluyen el cero el régimen
   (label, prior) es el MISMO para toda tasa de la caja y se decide con la regla de model.partition(). Las celdas que
   no se deciden (cortes que se mueven dentro de la caja, empates, raíces múltiples) se refinan con un presupuesto y
   las que quedan se tratan con COTAS UNIVERSALES del integrando: E0 en beta m1 [-1, 1]; W en m_rho [0, 1]; A en
   gamma m1 [0, 1] (G) o [-k_F m_rho, gamma m1] (N). La cola z -> inf se certifica por dominancia del término líder.
4. Momentos Pareto cerrados (Lema 1) crecientes en el extremo superior y decrecientes en el inferior: se encierran
   con los extremos desfavorables de cada celda.
5. Derivadas (para monotonía de R1/R2, raíces endógenas y la forma de valor medio): derivadas explícitas por
   aritmética directa + términos de Leibniz por cada corte posible en celdas indecisas:
   |salto del integrando| * densidad * |dc/dv|, dc/dv = -(dT/dv)/(dT/dz); si dT/dz contiene 0 (posible raíz múltiple o
   empate) la derivada NO se acota (se devuelve None): la monotonía no se certifica y la caja queda sin decidir.
   Donde R tiene quiebres (cambios de régimen) el encierro contiene todas las derivadas laterales, que es lo que exige
   el teorema del valor medio para funciones continuas a trozos C1.
6. Redondeo: operaciones básicas con redondeo hacia afuera (paper2b.intervalos). Funciones trascendentales (exp, log,
   log1p, E = expm1(y)/y, E', potencias) con cotas DEMOSTRADAS de paper2b.elementales, que solo usa aritmética IEEE 754
   binary64 con redondeo al más cercano (comprobada al importar: elementales.PLATAFORMA), operaciones exactas y
   constantes racionales. Ninguna cota depende de la exactitud de libm; sin plataforma conforme el motor no se construye.
7. Continuidad: con rho < 1 los cortes se mueven continuamente y R es continua (con quiebres); con rho = 1 hay curvas
   de salto (S13): los encierros las contienen (cubren ambos lados) pero la derivada no se acota en cajas que las
   cruzan, de modo que ninguna raíz se "demuestra" a través de un salto.
Nada de esto usa diferencias entre mallas, muestreo, residuos observados ni estimaciones de convergencia.
"""
from __future__ import annotations

import heapq
import itertools
import math
from dataclasses import dataclass

from . import elementales as EL
from . import model as M
from .intervalos import Iv

INF = math.inf
ALL = Iv(-INF, INF)
TRI_NAMES = ("F0-I0", "I1-I0", "I1-F0", "F1-F0", "F1-I0", "F1-I1")


# ============================================================================================ elementales
# Cotas DEMOSTRADAS de paper2b.elementales (solo aritmética IEEE 754 binary64 con redondeo al más cercano, operaciones
# exactas y constantes racionales; ninguna cota depende de la exactitud de libm). Todas son funciones crecientes.
def iexp(X: Iv) -> Iv:
    return Iv(EL.exp_bounds(X.lo)[0] if X.lo != -INF else 0.0, EL.exp_bounds(X.hi)[1])


def ilog(X: Iv) -> Iv:
    if not X.lo > 0.0:
        raise ValueError("log de intervalo no positivo")
    return Iv(EL.log_bounds(X.lo)[0], EL.log_bounds(X.hi)[1])


def ilog1m(T: Iv) -> Iv:
    """log1p(-t) para t en [0, 1): decreciente. Fuera de ese dominio (tasas no admisibles) se RECHAZA."""
    if not (T.hi < 1.0 and T.lo >= 0.0):
        raise ValueError("tasa fuera de [0, 1)")
    return Iv(EL.log1p_bounds(-T.hi)[0], EL.log1p_bounds(-T.lo)[1])


def iE(Y: Iv) -> Iv:
    """E(y) = expm1(y)/y, creciente."""
    return Iv(EL.E_bounds(Y.lo)[0], EL.E_bounds(Y.hi)[1])


def iEp(Y: Iv) -> Iv:
    """E'(y), creciente (E es convexa)."""
    return Iv(EL.Ep_bounds(Y.lo)[0], EL.Ep_bounds(Y.hi)[1])


def ipow(X: Iv, P) -> Iv:
    """X^P para X > 0 (P número o intervalo)."""
    P = Iv.of(P)
    if P.lo == P.hi == 1.0:
        return X
    if not X.lo > 0.0:
        raise ValueError("potencia de base no positiva")
    if P.lo > 0.0:                                   # z^q creciente en z para todo q del encierro
        return Iv(EL.pow_range(X.lo, P.lo, P.hi)[0], EL.pow_range(X.hi, P.lo, P.hi)[1] if X.hi != INF else INF)
    if P.hi < 0.0:                                   # decreciente en z
        return Iv(EL.pow_range(X.hi, P.lo, P.hi)[0] if X.hi != INF else 0.0, EL.pow_range(X.lo, P.lo, P.hi)[1])
    return iexp(P * ilog(X))


# ============================================================================================ diferenciación directa
ZERO = Iv(0.0, 0.0)


class AD:
    """Valor encerrado + gradiente encerrado respecto de (tau_d, tau_f, phi). g=None: gradiente nulo (constante)."""
    __slots__ = ("v", "g")

    def __init__(self, v: Iv, g=None):
        self.v, self.g = v, g

    @staticmethod
    def var(v: Iv, k: int, grad: bool):
        if not grad:
            return AD(v)
        g = [ZERO, ZERO, ZERO]
        g[k] = Iv(1.0, 1.0)
        return AD(v, tuple(g))


def _ad(x) -> AD:
    return x if isinstance(x, AD) else AD(Iv.of(x))


def _gadd(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return tuple(x + y for x, y in zip(a, b))


def _gscale(g, s: Iv):
    return None if g is None else tuple(x * s for x in g)


def add(a, b) -> AD:
    a, b = _ad(a), _ad(b)
    return AD(a.v + b.v, _gadd(a.g, b.g))


def sub(a, b) -> AD:
    a, b = _ad(a), _ad(b)
    return AD(a.v - b.v, _gadd(a.g, _gscale(b.g, Iv(-1.0, -1.0))))


def mul(a, b) -> AD:
    a, b = _ad(a), _ad(b)
    return AD(a.v * b.v, _gadd(_gscale(a.g, b.v), _gscale(b.g, a.v)))


def div(a, b) -> AD:
    a, b = _ad(a), _ad(b)
    q = a.v / b.v
    g = None
    if a.g is not None or b.g is not None:
        num = _gadd(a.g, _gscale(b.g, -q))
        g = _gscale(num, Iv(1.0, 1.0) / b.v)
    return AD(q, g)


def neg(a) -> AD:
    a = _ad(a)
    return AD(-a.v, _gscale(a.g, Iv(-1.0, -1.0)))


def ad_exp(a) -> AD:
    a = _ad(a)
    v = iexp(a.v)
    return AD(v, _gscale(a.g, v))


def ad_log1m(a) -> AD:
    a = _ad(a)
    return AD(ilog1m(a.v), _gscale(a.g, Iv(-1.0, -1.0) / (1.0 - a.v)))


def ad_E(a) -> AD:
    a = _ad(a)
    return AD(iE(a.v), _gscale(a.g, iEp(a.v)))


# ============================================================================================ parámetros
@dataclass(frozen=True)
class IParams:
    a: Iv
    rho: Iv
    kappa0: Iv
    beta: Iv
    delta: Iv
    theta: Iv
    gamma: Iv
    z_m: Iv
    eta_d: Iv
    eta_f: Iv
    phi: Iv

    @property
    def B_pot(self) -> Iv:
        return self.gamma * self.a * self.z_m / (self.a - 1.0)

    @property
    def rho_is_one(self) -> bool:
        return self.rho.lo == self.rho.hi == 1.0

    @classmethod
    def from_state(cls, s: M.State) -> "IParams":
        p = Iv.point
        return cls(p(s.a), p(s.rho), p(s.kappa0), p(s.beta), p(s.delta), p(s.theta), p(s.gamma), p(s.z_m), p(s.eta_d),
                   p(s.eta_f), p(s.phi))

    @classmethod
    def from_primitive_box(cls, box: dict, fixed: dict) -> "IParams":
        """Caja de primitivas estructurales {pid: (lo, hi)} + fijos (gamma, z_m, ...) -> derivados por intervalos
        (mismas fórmulas que model.derive; el dominio de la caja debe estar demostrado por cobertura.box_admissible)."""
        I = lambda pid: Iv(float(box[pid][0]), float(box[pid][1]))  # noqa: E731
        gamma, z_m = Iv.point(float(fixed["gamma"])), Iv.point(float(fixed["z_m"]))
        a, rho, kt, bt, ut, zc = I("a"), I("rho"), I("kappa_tilde"), I("beta_tilde"), I("u_theta"), I("z_cost")
        theta = 1.0 + ut * (a - 1.0)
        delta = ipow(zc, 1.0 - theta) * gamma * ipow(z_m, 1.0 - theta)
        kappa0 = kt * gamma * ipow(z_m, 1.0 - rho)
        return cls(a, rho, kappa0, bt * gamma, delta, theta, gamma, z_m, I("eta_d"), I("eta_f"), I("phi"))


def ip_with_phi(P: IParams, Phi: Iv) -> IParams:
    return IParams(P.a, P.rho, P.kappa0, P.beta, P.delta, P.theta, P.gamma, P.z_m, P.eta_d, P.eta_f, Phi)


# ============================================================================================ núcleo
@dataclass
class Tax:
    td: AD
    one_td: AD
    rstar: AD
    tf: AD
    kF: AD
    qstar: AD
    gf: AD
    tb: AD


def tax_side(P: IParams, Td: AD, Tf: AD, Ph: AD) -> Tax:
    ld = ad_log1m(Td)
    td = neg(mul(ld, ad_E(mul(1.0 + P.eta_d, ld))))
    rstar = ad_exp(mul(P.eta_d, ld))
    lf = ad_log1m(Tf)
    alpha = sub(P.eta_f, Ph)
    tf = add(mul(Tf, ad_exp(mul(alpha, lf))),
             mul(mul(neg(lf), P.eta_f), sub(ad_E(mul(alpha, lf)), ad_E(mul(add(alpha, 1.0), lf)))))
    kF = mul(P.kappa0, add(1.0, mul(Ph, tf)))
    qstar = ad_exp(mul(P.eta_f, lf))
    gf = ad_exp(neg(mul(Ph, lf)))
    tb = mul(Td, P.beta)
    return Tax(td, sub(1.0, td), rstar, tf, kF, qstar, gf, tb)


def trinomials(P: IParams, x: Tax, design: str) -> dict:
    """(A: Iv, B: AD, C: AD, L: AD) por diferencia; mismas fórmulas simbólicas que model.pair_trinomials. La
    diferencia N 'F1-F0' se representa por su factor de signo (gamma z - k_F z^rho): mismo signo y mismos cortes."""
    g, d, k0 = P.gamma, P.delta, P.kappa0
    tb, td, one_td, kF, tf = x.tb, x.td, x.one_td, x.kF, x.tf
    out = {"F0-I0": (d, neg(tb), _ad(0.0), neg(tb)),
           "I1-I0": (ZERO, _ad(g), _ad(-k0), _ad(g - k0)),
           "I1-F0": (-d, add(tb, g), _ad(-k0), add(tb, g - k0))}
    if design == "G":
        out["F1-F0"] = (ZERO, mul(one_td, g), neg(kF), sub(mul(one_td, g), kF))
        out["F1-I0"] = (d, sub(mul(one_td, g), tb), neg(kF), sub(sub(mul(one_td, g), kF), tb))
        phitf = mul(mul(k0, P.phi if not hasattr(x, "_ph") else x._ph), tf)
        out["F1-I1"] = (d, neg(add(tb, mul(td, g))), neg(phitf), neg(add(add(tb, mul(td, g)), phitf)))
    elif design == "N":
        out["F1-F0"] = (ZERO, _ad(g), neg(kF), sub(g, kF))
        out["F1-I0"] = (d, sub(mul(one_td, g), tb), neg(mul(one_td, kF)), sub(mul(one_td, sub(g, kF)), tb))
        cn = sub(k0, mul(one_td, kF))
        out["F1-I1"] = (d, neg(add(tb, mul(td, g))), cn, sub(cn, add(tb, mul(td, g))))
    else:
        raise M.DomainError("DESIGN")
    return out


def _thr(num: float, den: float, e: float) -> float:
    """z con (den z^e > num) DEMOSTRADO para todo z >= z (z^e creciente): candidato (num/den)^(1/e) en coma flotante,
    verificado con la cota inferior demostrada de den z^e; si no se verifica se agranda (o no hay umbral: INF)."""
    if num <= 0.0:
        return 1.0
    if not (den > 0.0 and e > 0.0):
        return INF
    try:
        z = max(1.0, (num / den) ** (1.0 / e) * (1.0 + 1e-9))
    except OverflowError:
        return INF
    for _ in range(60):
        if not math.isfinite(z):
            return INF
        if EL.dn(den * EL.pow_bounds(z, e)[0]) > num:
            return z
        z *= 1.001
    return INF


def _crit(A: Iv, p: float, b: float, U: Iv) -> float | None:
    """Punto crítico aproximado de A u^p + b u (derivada A p u^(p-1) + b = 0) si cae dentro de U."""
    a = 0.5 * (A.lo + A.hi)
    if a == 0.0 or p <= 1.0:
        return None
    r = -b / (a * p)
    if not r > 0.0:
        return None
    try:
        u = r ** (1.0 / (p - 1.0))
    except OverflowError:
        return None
    return u if U.lo < u < U.hi else None


def _edge(s: float, s_m: float, z_m: Iv) -> Iv:
    """Encierro del borde z = e^s de una celda (el primero es z_m exacto; el último, infinito)."""
    if s == s_m:
        return z_m
    if not math.isfinite(s):
        return Iv(INF, INF)
    return Iv(*EL.exp_bounds(s))


def _sign(v: Iv) -> int:
    return 1 if v.lo > 0.0 else (-1 if v.hi < 0.0 else 0)


def _regime(sg: dict) -> tuple[str, str]:
    prior = "F" if sg["F0-I0"] >= 0 else "I"
    if prior == "F":
        f_v0, i_v0 = sg["F1-F0"], sg["I1-F0"]
    else:
        f_v0, i_v0 = sg["F1-I0"], sg["I1-I0"]
    f_i1 = sg["F1-I1"]
    if f_v0 > 0 and f_i1 >= 0:
        return "F", prior
    if i_v0 > 0 and f_i1 < 0:
        return "I", prior
    return "N", prior


class Engine:
    """Encierros de R(tau_d, tau_f; phi) y de su gradiente para un estado (o caja de estados) y diseño fijos."""

    def __init__(self, P: IParams, design: str, *, ds_min: float = 1e-14, budget: int = 900, cache_size: int = 20000):
        EL.exigir_plataforma()                    # sin aritmética IEEE 754 conforme no hay cotas demostradas
        if design not in M.DESIGNS:
            raise M.DomainError("DESIGN")
        self.P, self.design = P, design
        self.ds_min, self.budget = ds_min, budget
        self.B_pot = P.B_pot
        self._cache: dict = {}
        self._exps: dict = {}
        self.cache_size = cache_size
        self.evaluations = 0

    # ---------------------------------------------------------------------------------------- trinomios en celdas
    def _tri_sign(self, A: Iv, B: Iv, C: Iv, L: Iv, Z: Iv) -> int:
        """Signo DEMOSTRADO de T(z) = A z^theta + B z + C z^rho para todo z en Z, todo coeficiente en su encierro y todo
        theta, rho en los suyos. T es creciente en A, B y C (z > 0), así que su envolvente inferior usa (A.lo, B.lo, C.lo)
        y la superior (A.hi, B.hi, C.hi). Con theta, rho por intervalos, a un lado de z = 1 cada término a z^x es monótono
        en x (derivada a z^x ln z), así que la envolvente se alcanza en una ESQUINA fija de (theta, rho) para todo z de
        la celda (si Z contiene 1 se parte en z = 1). Con exponentes puntuales, T = z^rho g(u), u = z^(1-rho),
        g(u) = a u^p + b u + c (p > 1) es convexa si a > 0 y cóncava si a < 0: extremos + desigualdad de la tangente."""
        P = self.P
        if P.rho_is_one:
            w = ipow(Z, P.theta - 1.0)            # T = z (A w + L), w creciente en z
            return _sign(A * w + L)
        pt = P.theta.lo == P.theta.hi and P.rho.lo == P.rho.hi
        if not pt and Z.lo < 1.0 < Z.hi:
            s1 = self._tri_sign(A, B, C, L, Iv(Z.lo, 1.0))
            return s1 if s1 != 0 and s1 == self._tri_sign(A, B, C, L, Iv(1.0, Z.hi)) else 0
        lnpos = Z.lo >= 1.0

        def corner(coef: float, ex: Iv, minimize: bool) -> float:
            if pt:
                return ex.lo
            inc = (coef >= 0.0) == lnpos          # coef z^x creciente en x
            return (ex.lo if inc else ex.hi) if minimize else (ex.hi if inc else ex.lo)
        lo = self._env(A.lo, B.lo, C.lo, Z, corner(A.lo, P.theta, True), corner(C.lo, P.rho, True), True)
        if lo > 0.0:
            return 1
        hi = self._env(A.hi, B.hi, C.hi, Z, corner(A.hi, P.theta, False), corner(C.hi, P.rho, False), False)
        if hi < 0.0:
            return -1
        return 0

    def _env(self, a: float, b: float, c: float, Z: Iv, th: float, rh: float, want_min: bool) -> float:
        """Cota inferior (want_min) o superior de una cantidad con el MISMO signo que a z^th + b z + c z^rh en Z."""
        if rh == 1.0:                             # z (a w + b + c), w = z^(th - 1) creciente
            W = ipow(Z, Iv.point(th) - 1.0)
            v = a * W + (Iv.point(b) + c)
            return v.lo if want_min else v.hi
        # exponentes EXACTOS encerrados (1 - rh y (th - rh)/(1 - rh) pueden no ser representables): u = z^(1 - rh) con
        # U que contiene su rango; p en pe; la convexidad usa el p verdadero (> 1 porque th > 1)
        ex = self._exps.get((th, rh))
        if ex is None:
            ie = Iv.point(1.0) - Iv.point(rh)
            pe = (Iv.point(th) - Iv.point(rh)) / ie
            ex = self._exps[(th, rh)] = (ie, pe, pe - 1.0, 0.5 * (pe.lo + pe.hi))
        ie, pe, pe1, p = ex                      # p (punto medio) solo ubica el punto crítico aproximado
        U = ipow(Z, ie)
        # Evaluación ESCALAR con redondeo dirigido explícito (EL.dn/EL.up tras cada operación) y u^p con cotas
        # demostradas: mismo rigor que la aritmética de intervalos, mucho más rápida.
        dn, up = EL.dn, EL.up

        def g(u: float) -> float:
            tlo, thi = EL.pow_range(u, pe.lo, pe.hi)
            if want_min:
                m = dn(a * tlo) if a >= 0.0 else dn(a * thi)
                return dn(dn(m + dn(b * u)) + c)
            m = up(a * thi) if a >= 0.0 else up(a * tlo)
            return up(up(m + up(b * u)) + c)

        def slope(u: float) -> float:
            """Cota superior de |a p u^(p-1) + b| (p en su encierro)."""
            tlo, thi = EL.pow_range(u, pe1.lo, pe1.hi)
            ap = Iv.point(a) * pe
            v = ap * Iv(tlo, thi) + b
            return max(abs(v.lo), abs(v.hi))

        if want_min:
            best = min(g(U.lo), g(U.hi))
            if a > 0.0:                           # convexa: el mínimo puede estar dentro
                ustar = _crit(Iv(a, a), p, b, U)
                if ustar is not None:
                    span = up(max(ustar - U.lo, U.hi - ustar))
                    best = min(best, dn(g(ustar) - up(slope(ustar) * span)))
            return best
        best = max(g(U.lo), g(U.hi))
        if a < 0.0:                               # cóncava: el máximo puede estar dentro
            ustar = _crit(Iv(a, a), p, b, U)
            if ustar is not None:
                span = up(max(ustar - U.lo, U.hi - ustar))
                best = max(best, up(g(ustar) + up(slope(ustar) * span)))
        return best

    def _eval_cell(self, tri: dict, Z: Iv, want: bool):
        sg, amb = {}, []
        for k, (A, B, C, L) in tri.items():
            s = self._tri_sign(A, B.v, C.v, L.v, Z)
            sg[k] = s
            if s == 0:
                amb.append(k)
        return sg, amb, None, None

    def _tail_z(self, tri: dict) -> float | None:
        """z desde el cual TODOS los signos quedan fijados por el término dominante (None si alguno no se fija)."""
        P = self.P
        zt = [P.z_m.hi]
        for k, (A, B, C, L) in tri.items():
            Bv, Cv, Lv = B.v, C.v, L.v
            if A.lo > 0.0 or A.hi < 0.0:
                num = max(abs(Bv.lo), abs(Bv.hi)) + max(abs(Cv.lo), abs(Cv.hi))
                den = min(abs(A.lo), abs(A.hi))
                if not (P.theta.lo > 1.0 and den > 0.0):
                    return None
                zt.append(max(1.0, _thr(num, den, P.theta.lo - 1.0)))
            elif P.rho_is_one:
                if _sign(Lv) == 0:
                    return None
            else:
                if _sign(Bv) == 0 or not P.rho.hi < 1.0:
                    return None
                num = max(abs(Cv.lo), abs(Cv.hi))
                den = min(abs(Bv.lo), abs(Bv.hi))
                zt.append(max(1.0, _thr(num, den, 1.0 - P.rho.hi)))
        z = max(zt)
        return z if math.isfinite(z) else None

    def _seeds(self, tri: dict, s_m: float, s_top: float) -> list:
        """Cortes CANDIDATOS (ln z) del centro de la caja con model.trinomial_roots en flotante: solo orientan dónde
        poner bordes de celda; la clasificación de cada celda se demuestra después con encierros."""
        P = self.P
        th, rh = 0.5 * (P.theta.lo + P.theta.hi), 0.5 * (P.rho.lo + P.rho.hi)
        mid = lambda v: 0.5 * (v.lo + v.hi)  # noqa: E731
        out = []
        for k, (A, B, C, L) in tri.items():
            try:
                rt = M.trinomial_roots(M.Trinomial(mid(A), mid(B.v), mid(C.v), mid(L.v)), th, rh)
            except Exception:  # noqa: BLE001
                continue
            out += [r for r in rt.lnz if s_m < r < s_top]
        return sorted(out)

    def partition(self, tri: dict, ds_min: float | None = None):
        """Celdas en s = ln z: [(s0, s1, Z, estado, regimen|None, ambiguos)] con estado 'certain'/'uncertain'."""
        P = self.P
        s_m = math.log(P.z_m.lo)
        zt = self._tail_z(tri)
        s_top = (s_m + 60.0) if zt is None else max(s_m + 1e-6, math.log(zt))
        if zt is not None:
            # la celda de cola empieza en e^s_top: su cota inferior DEMOSTRADA debe ser >= zt (dominancia probada ahí)
            while EL.exp_bounds(s_top)[0] < zt:
                s_top = math.nextafter(s_top, INF)
        edges = {s_m, s_top}
        for r in self._seeds(tri, s_m, s_top):
            for w in (1e-13 * max(1.0, abs(r)), 1e-10 * max(1.0, abs(r)), 1e-6, 1e-3):
                for e in (r - w, r + w):
                    if s_m < e < s_top:
                        edges.add(e)
        edges = sorted(edges)
        cells_done, heap = [], []
        evals = 0

        def zbox(s0, s1):
            return Iv(_edge(s0, s_m, P.z_m).lo, _edge(s1, s_m, P.z_m).hi)

        def classify(s0, s1):
            nonlocal evals
            sg, amb, _, _ = self._eval_cell(tri, zbox(s0, s1), False)
            evals += 1
            return sg, amb

        def push(s0, s1, sat=0):
            sg, amb = classify(s0, s1)
            if not amb:
                cells_done.append((s0, s1, zbox(s0, s1), "certain", _regime(sg), ()))
            else:
                heapq.heappush(heap, (-(s1 - s0), s0, s1, tuple(amb), sat))
        for a, b in zip(edges, edges[1:]):
            push(a, b)
        while heap:
            negw, s0, s1, amb, sat = heap[0]
            if -negw <= (self.ds_min if ds_min is None else ds_min) or evals >= self.budget:
                break
            heapq.heappop(heap)
            m = 0.5 * (s0 + s1)
            if not (s0 < m < s1):
                cells_done.append((s0, s1, zbox(s0, s1), "uncertain", None, amb))
                continue
            (sa, aa), (sb, ab) = classify(s0, m), classify(m, s1)
            common = set(aa) & set(ab)
            if common and sat >= 2:
                # la ambigüedad llena la celda (el corte se mueve dentro de la caja): refinar no la reduce
                cells_done.append((s0, s1, zbox(s0, s1), "uncertain", None, amb))
                continue
            for (x0, x1, sg, ab_) in ((s0, m, sa, aa), (m, s1, sb, ab)):
                if not ab_:
                    cells_done.append((x0, x1, zbox(x0, x1), "certain", _regime(sg), ()))
                else:
                    heapq.heappush(heap, (-(x1 - x0), x0, x1, tuple(ab_), sat + 1 if common else 0))
        for negw, s0, s1, amb, sat in heap:
            cells_done.append((s0, s1, zbox(s0, s1), "uncertain", None, amb))
        # cola
        if zt is not None:
            Z = Iv(_edge(s_top, s_m, P.z_m).lo, INF)
            sg = {}
            for k, (A, B, C, L) in tri.items():
                if A.lo > 0.0 or A.hi < 0.0:
                    sg[k] = 1 if A.lo > 0.0 else -1
                elif P.rho_is_one:
                    sg[k] = _sign(L.v)
                else:
                    sg[k] = _sign(B.v)
            cells_done.append((s_top, INF, Z, "certain", _regime(sg), ()))
        else:
            cells_done.append((s_top, INF, Iv(_edge(s_top, s_m, P.z_m).lo, INF), "uncertain", None, TRI_NAMES))
        cells_done.sort(key=lambda c: c[0])
        self.evaluations += evals
        self.s_m = s_m
        return cells_done

    # ---------------------------------------------------------------------------------------- momentos Pareto
    def moment(self, m: Iv, Zlo: Iv, Zhi: Iv) -> Iv:
        """int_{z in [lo, hi)} z^m dF, Pareto(a, z_m), con bordes ENCERRADOS Zlo, Zhi: creciente en hi y decreciente en
        lo, así que la cota inferior usa (Zlo.hi, Zhi.lo) y la superior (Zlo.lo, Zhi.hi)."""
        P = self.P

        def F(lo: float, hi: float) -> Iv:
            k = m - P.a
            c = P.a / (P.a - m) * ipow(P.z_m, m)
            tlo = iexp(k * ilog(Iv.point(lo) / P.z_m))
            thi = ZERO if not math.isfinite(hi) else iexp(k * ilog(Iv.point(hi) / P.z_m))
            return c * (tlo - thi)
        small = F(Zlo.hi, Zhi.lo) if Zhi.lo > Zlo.hi else ZERO
        big = F(max(Zlo.lo, P.z_m.lo), Zhi.hi)
        return Iv(max(0.0, min(small.lo, big.hi)), max(0.0, big.hi))

    def density(self, Z: Iv) -> Iv:
        P = self.P
        return P.a * ipow(P.z_m, P.a) * ipow(Z, -(P.a + 1.0))

    # ---------------------------------------------------------------------------------------- R y gradiente
    def R(self, Td: Iv, Tf: Iv, Phi: Iv | None = None, *, grad: bool = False, force: tuple = ()):
        """(encierro de R, gradiente encerrado respecto de (tau_d, tau_f, phi) o None si no se acota)."""
        v, g, _ = self.R_full(Td, Tf, Phi, grad=grad, force=force)
        return v, g

    def R_full(self, Td: Iv, Tf: Iv, Phi: Iv | None = None, *, grad: bool = False, force: tuple = ()):
        """Como R, más la descomposición en ramas de un pliegue (None si no hay): cuando el primer tramo indeciso
        empieza en z_m con un único trinomio ambiguo k, R = rama_fuera (corte de k bajo z_m: todo el tramo en el
        régimen derecho) o rama_dentro (corte c(tau) en el tramo), ambas SUAVES en toda la caja (la segunda
        prolongada con la fórmula de Pareto bajo z_m). Si el salto J del integrando tiene signo demostrado,
        R = max(fuera, dentro) (J > 0) o min(fuera, dentro) (J < 0).

        Salto (solo rho = 1): un trinomio con A = 0 (I1-I0, F1-F0) tiene signo uniforme en z, el de L; si el encierro
        de L contiene 0 la caja toca la curva de salto S13. Entonces R en la caja es R+ (L > 0) o R- (L <= 0: la regla
        de desempate S13 exige '> 0' para adoptar, así que el empate cae en R-), cada una suave; se devuelven ambas
        ramas FORZADAS (`force`: pares (trinomio, signo)) y el encierro es su envolvente, sin gradiente."""
        P = self.P
        Phi = P.phi if Phi is None else Phi
        key = (Td.lo, Td.hi, Tf.lo, Tf.hi, Phi.lo, Phi.hi, grad, force)
        hit = self._cache.get(key)
        if hit is not None:
            return hit
        Pp = P if Phi is P.phi else ip_with_phi(P, Phi)
        td_, tf_, ph_ = AD.var(Td, 0, grad), AD.var(Tf, 1, grad), AD.var(Phi, 2, grad)
        x = tax_side(Pp, td_, tf_, ph_)
        x._ph = ph_
        tri = trinomials(Pp, x, self.design)
        if P.rho_is_one:
            forced = dict(force)
            jumps = [k for k in ("I1-I0", "F1-F0") if k not in forced and tri[k][0].lo == 0.0 == tri[k][0].hi
                     and _sign(tri[k][3].v) == 0]
            if jumps:
                parts, vals = [], []
                for signs in itertools.product((1, -1), repeat=len(jumps)):
                    f2 = tuple(sorted(tuple(force) + tuple(zip(jumps, signs))))
                    v_, _, _ = self.R_full(Td, Tf, Phi, grad=grad, force=f2)
                    parts.append(f2)
                    vals.append(v_)
                lg = None
                for k in jumps:
                    gk = tri[k][3].g
                    if gk is not None:
                        lg = gk if lg is None else tuple(a.hull(b) for a, b in zip(lg, gk))
                v = vals[0]
                for v_ in vals[1:]:
                    v = v.hull(v_)
                out = (v, None, {"kind": "jump", "parts": parts, "lg": lg})
                if len(self._cache) < self.cache_size:
                    self._cache[key] = out
                return out
            for k, sgn in force:
                A_, B_, C_, _L = tri[k]
                tri[k] = (A_, B_, C_, AD(Iv(float(sgn), float(sgn))))
        # refinar celdas indecisas por debajo del desplazamiento de los cortes dentro de la caja no las decide:
        # ds_min proporcional al ancho de la caja (1e-14 en cajas degeneradas)
        wbox = max(Td.hi - Td.lo, Tf.hi - Tf.lo, Phi.hi - Phi.lo)
        cells = self.partition(tri, max(self.ds_min, 1e-4 * wbox))
        s_m = self.s_m
        # tramos: celdas ciertas consecutivas con el mismo régimen; celdas indecisas consecutivas
        items = []
        for (s0, s1, Z, state, reg, amb) in cells:
            if state == "certain":
                if items and items[-1][0] == "c" and items[-1][3] == reg and items[-1][2] == s0:
                    items[-1] = ("c", items[-1][1], s1, reg)
                else:
                    items.append(("c", s0, s1, reg))
            else:
                if items and items[-1][0] == "u" and items[-1][2] == s0:
                    items[-1] = ("u", items[-1][1], s1, tuple(sorted(set(items[-1][3]) | set(amb))), items[-1][4] + [(s0, s1, Z, amb)])
                else:
                    items.append(("u", s0, s1, tuple(amb), [(s0, s1, Z, amb)]))
        E0, A, W = AD(ZERO, None), AD(ZERO, None), AD(ZERO, None)
        grad_ok = True
        kink = None
        for it in items:
            Zlo, Zhi = _edge(it[1], s_m, P.z_m), _edge(it[2], s_m, P.z_m)
            if it[0] == "c":
                dE, dA, dW = self._certain(it[3], Zlo, Zhi, x)
            else:
                dE, dA, dW, ok = self._uncertain(it, Zlo, Zhi, tri, x, grad and grad_ok)
                grad_ok = grad_ok and ok
                if grad and ok and kink is None and it[1] == s_m:
                    kb = self._kink_branches(it, Zlo, Zhi, tri, x, td_, tf_)
                    if kb is not None:
                        kink = (kb, (dE, dA, dW))
                        continue
            E0, A, W = add(E0, dE), add(A, dA), add(W, dW)

        def comb(e, a, w):
            Bd = add(e, mul(x.rstar, a))
            Bf = mul(mul(mul(x.qstar, P.kappa0), x.gf), w)
            return add(mul(td_, Bd), mul(tf_, Bf))
        branch = None
        if kink is None:
            R = comb(E0, A, W)
        else:
            (d_out, d_in, kind, info), d_main = kink
            R = comb(add(E0, d_main[0]), add(A, d_main[1]), add(W, d_main[2]))
            Ro = comb(add(E0, d_out[0]), add(A, d_out[1]), add(W, d_out[2]))
            Ri = comb(add(E0, d_in[0]), add(A, d_in[1]), add(W, d_in[2]))
            if grad_ok and Ro.g is not None and Ri.g is not None:
                branch = {"kind": kind, "g_out": Ro.g, "g_in": Ri.g, "info": info}
        out = (R.v, (R.g if (grad and grad_ok and R.g is not None) else None), branch)
        if len(self._cache) < self.cache_size:
            self._cache[key] = out
        self.evaluations += 1
        return out

    # integrandos por régimen: E0 = beta z (d1 - d0); A = gamma z [F] (G) o (gamma z - k_F z^rho) [F] (N); W = z^rho [F]
    @staticmethod
    def _coef(reg) -> tuple[float, float]:
        label, prior = reg
        d0 = 1.0 if prior == "F" else 0.0
        d1 = 1.0 if label == "F" else (0.0 if label == "I" else d0)
        return d1 - d0, (1.0 if label == "F" else 0.0)

    def _certain(self, reg, Zlo, Zhi, x):
        P = self.P
        e, fF = self._coef(reg)
        M1 = self.moment(Iv.point(1.0), Zlo, Zhi)
        dE = AD(P.beta * M1 * e) if e != 0.0 else AD(ZERO)
        if fF == 0.0:
            return dE, AD(ZERO), AD(ZERO)
        Mr = self.moment(P.rho, Zlo, Zhi)
        dA = AD(P.gamma * M1) if self.design == "G" else sub(AD(P.gamma * M1), mul(x.kF, Mr))
        return dE, dA, AD(Mr)

    def _uncertain(self, it, Zlo, Zhi, tri, x, grad):
        """Tramo indeciso. Con UN solo trinomio ambiguo k, sin raíz múltiple (dT_k/dz sin cero) y los demás signos
        ciertos, los regímenes a izquierda y derecha del corte se conocen: el aporte vale entre los dos extremos
        (corte en un borde u otro) y el término de Leibniz usa el salto CON SIGNO. Si no, cotas universales."""
        P = self.P
        _, s0, s1, amb, sub_cells = it
        Zu = Iv(Zlo.lo, Zhi.hi)
        M1 = self.moment(Iv.point(1.0), Zlo, Zhi)
        Mr = self.moment(P.rho, Zlo, Zhi)
        at_start = s0 == self.s_m
        if len(amb) == 1 and math.isfinite(s1):
            k = amb[0]
            dz = self._dz(tri, k, Zu)
            others = {kk: self._tri_sign(A_, B.v, C.v, L.v, Zu) for kk, (A_, B, C, L) in tri.items() if kk != k}
            if _sign(dz) != 0 and all(v != 0 for v in others.values()):
                sL, sR = (-1, 1) if dz.lo > 0.0 else (1, -1)
                eL, fL = self._coef(_regime(dict(others, **{k: sL})))
                eR, fR = self._coef(_regime(dict(others, **{k: sR})))
                vE = (P.beta * M1 * eL).hull(P.beta * M1 * eR)
                vW = (Mr * fL).hull(Mr * fR)
                gE = gA = gW = None
                a_ok = True
                if self.design == "G":
                    vA = AD((P.gamma * M1 * fL).hull(P.gamma * M1 * fR))
                elif fL == fR:
                    vA = sub(AD(P.gamma * M1), mul(x.kF, Mr)) if fL else AD(ZERO)
                else:
                    h = P.gamma * ipow(Zu, 1.0 - P.rho) - x.kF.v      # signo de gamma z - k_F z^rho
                    if _sign(h) != 0:
                        full = sub(AD(P.gamma * M1), mul(x.kF, Mr))
                        vA = AD(full.v.hull(ZERO), None if full.g is None else tuple(gi.hull(ZERO) for gi in full.g))
                    else:
                        a_ok = False
                        vA = AD(Iv(-(x.kF.v.hi * Mr.hi), (P.gamma * M1).hi),
                                None if x.kF.g is None else tuple(gi * (Mr * Iv(-1.0, 0.0)) for gi in x.kF.g))
                if grad:
                    A_, B, C, L = tri[k]
                    Zr = Zu if P.rho_is_one else ipow(Zu, P.rho)
                    gv = _gscale(L.g, Zu) if P.rho_is_one else _gadd(_gscale(B.g, Zu), _gscale(C.g, Zr))
                    if gv is not None:
                        f = self.density(Zu)
                        dc = tuple(Iv(-1.0, -1.0) * gi / dz for gi in gv)
                        mask = Iv(0.0, 1.0) if at_start else Iv(1.0, 1.0)   # el corte puede no estar en el dominio
                        jE = P.beta * Zu * (eL - eR) * f * mask
                        jW = Zr * (fL - fR) * f * mask
                        if self.design == "G":
                            jA = P.gamma * Zu * (fL - fR) * f * mask
                        else:
                            jA = (P.gamma * Zu - x.kF.v * Zr) * (fL - fR) * f * mask
                        if not a_ok:
                            jA = jA.hull(-jA)
                        gE = tuple(jE * d for d in dc)
                        gW = tuple(jW * d for d in dc)
                        gA = tuple(jA * d for d in dc)
                return (AD(vE, gE), AD(vA.v, _gadd(vA.g, gA)), AD(vW, gW), True)
        # cotas universales (varios cortes posibles o raíz múltiple)
        unit = Iv(0.0, 1.0)
        dE = AD(P.beta * M1 * Iv(-1.0, 1.0))
        dW = AD(Mr * unit)
        if self.design == "G":
            dA = AD(P.gamma * M1 * unit)
        else:
            dA = AD(Iv(-(x.kF.v.hi * Mr.hi), (P.gamma * M1).hi),
                    None if x.kF.g is None else tuple(gi * (Mr * Iv(-1.0, 0.0)) for gi in x.kF.g))
        if not grad:
            return dE, dA, dW, True
        per_tri = {}
        for (a, b, Z, amb_c) in sub_cells:
            for k in amb_c:
                t = self._leibniz_cell(tri, k, Z, x)
                if t is None:
                    return dE, dA, dW, False
                per_tri.setdefault(k, []).append((a, b, t))
        agg = self._leibniz_aggregate(tri, per_tri)
        if agg is None:
            return dE, dA, dW, False
        gE, gA, gW = agg
        return AD(dE.v, _gadd(dE.g, gE)), AD(dA.v, _gadd(dA.g, gA)), AD(dW.v, _gadd(dW.g, gW)), True

    def _omoment(self, m: Iv, C: Iv) -> Iv:
        """int_{z_m}^{c} z^m f(z) dz ORIENTADO (negativo si c < z_m), con f la fórmula de Pareto prolongada; creciente
        en c (una sola aparición de C: la aritmética de intervalos da el encierro correcto)."""
        P = self.P
        k = m - P.a
        coef = P.a / (P.a - m) * ipow(P.z_m, m)
        return coef * (1.0 - iexp(k * ilog(C / P.z_m)))

    def _kink_branches(self, it, Zlo, Zhi, tri, x, td_, tf_):
        P = self.P
        _, s0, s1, amb, _ = it
        if len(amb) != 1 or not math.isfinite(s1):
            return None
        k = amb[0]
        Zu = Iv(Zlo.lo, Zhi.hi)
        ds = _sign(self._dz(tri, k, Zu))
        if ds == 0:
            return None
        others = {kk: self._tri_sign(A_, B.v, C.v, L.v, Zu) for kk, (A_, B, C, L) in tri.items() if kk != k}
        if any(v == 0 for v in others.values()):
            return None
        sL, sR = (-1, 1) if ds > 0 else (1, -1)
        A_, B, C, L = tri[k]
        if self._tri_sign(A_, B.v, C.v, L.v, Zhi) != sR:
            return None
        w = max(s1 - s0, 1e-12)
        zl = None
        for t in (1.0, 2.0, 4.0, 8.0, 16.0, 64.0):
            z = math.exp(s0 - t * w)
            if self._tri_sign(A_, B.v, C.v, L.v, Iv(z, z)) == sL:
                zl = z
                break
        if zl is None:
            return None
        CB = Iv(zl, Zhi.hi)
        dzB = self._dz(tri, k, CB)
        if _sign(dzB) != ds:
            return None
        CBr = CB if P.rho_is_one else ipow(CB, P.rho)
        gv = _gscale(L.g, CB) if P.rho_is_one else _gadd(_gscale(B.g, CB), _gscale(C.g, CBr))
        dc = (ZERO, ZERO, ZERO) if gv is None else tuple(Iv(-1.0, -1.0) * gi / dzB for gi in gv)
        f = self.density(CB)
        m1c = AD(self._omoment(Iv.point(1.0), CB), tuple(CB * f * d for d in dc))
        mrc = AD(self._omoment(P.rho, CB), tuple(CBr * f * d for d in dc))
        eL, fL = self._coef(_regime(dict(others, **{k: sL})))
        eR, fR = self._coef(_regime(dict(others, **{k: sR})))
        M1 = self.moment(Iv.point(1.0), Zlo, Zhi)
        Mr = self.moment(P.rho, Zlo, Zhi)
        E_out, W_out = AD(P.beta * M1 * eR), AD(Mr * fR)
        E_in = add(E_out, mul(AD(P.beta * (eL - eR)), m1c))
        W_in = add(W_out, mul(fL - fR, mrc))
        A_out = AD(P.gamma * M1 * fR)
        A_in = add(A_out, mul(AD(P.gamma * (fL - fR)), m1c))
        if self.design == "N":
            A_out = sub(A_out, mul(x.kF, W_out))
            A_in = sub(A_in, mul(x.kF, W_in))
        # signo del salto J(z; tau) = R_dentro - R_fuera por unidad de masa, en z entre z_m y c(tau)
        jA = P.gamma * CB * (fL - fR) if self.design == "G" else (P.gamma * CB - x.kF.v * CBr) * (fL - fR)
        J = td_.v * (P.beta * CB * (eL - eR) + x.rstar.v * jA) + tf_.v * x.qstar.v * P.kappa0 * x.gf.v * CBr * (fL - fR)
        kind = "max" if J.lo > 0.0 else ("min" if J.hi < 0.0 else "amb")
        info = {"k": k, "ds": ds, "sL": sL, "sR": sR, "eL": eL, "eR": eR, "fL": fL, "fR": fR}
        return (E_out, A_out, W_out), (E_in, A_in, W_in), kind, info

    def _kink_D(self, td: float, tf: float, ph: float, info: dict):
        """D(centro) = R_dentro - R_fuera en un PUNTO, con la raíz c de T_k encerrada y verificada por signos
        (corte de signo sL -> sR y dT_k/dz sin cero); None si no se verifica."""
        P = self.P
        Pp = P if (P.phi.lo == ph == P.phi.hi) else ip_with_phi(P, Iv(ph, ph))
        x = tax_side(Pp, AD(Iv(td, td)), AD(Iv(tf, tf)), AD(Iv(ph, ph)))
        x._ph = AD(Iv(ph, ph))
        tri = trinomials(Pp, x, self.design)
        k = info["k"]
        A_, B, C, L = tri[k]
        th, rh = 0.5 * (P.theta.lo + P.theta.hi), 0.5 * (P.rho.lo + P.rho.hi)
        mid = lambda v: 0.5 * (v.lo + v.hi)  # noqa: E731
        try:
            rt = M.trinomial_roots(M.Trinomial(mid(A_), mid(B.v), mid(C.v), mid(L.v)), th, rh)
        except Exception:  # noqa: BLE001
            return None
        if not rt.lnz:
            return None
        s_m = math.log(P.z_m.lo)
        c0 = math.exp(min(rt.lnz, key=lambda r: abs(r - s_m)))
        Cc = None
        for eps in (1e-13, 1e-11, 1e-9, 1e-7):
            zl, zh = c0 * (1.0 - eps), c0 * (1.0 + eps)
            if (self._tri_sign(A_, B.v, C.v, L.v, Iv(zl, zl)) == info["sL"]
                    and self._tri_sign(A_, B.v, C.v, L.v, Iv(zh, zh)) == info["sR"]
                    and _sign(self._dz(tri, k, Iv(zl, zh))) == info["ds"]):
                Cc = Iv(zl, zh)
                break
        if Cc is None:
            return None
        eL, eR, fL, fR = info["eL"], info["eR"], info["fL"], info["fR"]
        m1c = self._omoment(Iv.point(1.0), Cc)
        mrc = self._omoment(P.rho, Cc)
        dE = P.beta * (eL - eR) * m1c
        dW = (fL - fR) * mrc
        dA = P.gamma * (fL - fR) * m1c
        if self.design == "N":
            dA = dA - x.kF.v * dW
        D = Iv(td, td) * (dE + x.rstar.v * dA) + Iv(tf, tf) * x.qstar.v * P.kappa0 * x.gf.v * dW
        return D, Cc

    def _dz(self, tri, k, Z) -> Iv:
        P = self.P
        A_, B, C, L = tri[k]
        if P.rho_is_one:
            return A_ * P.theta * ipow(Z, P.theta - 1.0) + L.v
        return A_ * P.theta * ipow(Z, P.theta - 1.0) + B.v + C.v * P.rho * ipow(Z, P.rho - 1.0)

    def _leibniz_cell(self, tri, k, Z, x):
        """Término de Leibniz de UNA raíz de T_k situada en la celda Z: |salto| * densidad * |dc/dv| por componente
        (None si dT_k/dz puede anularse en Z: posible raíz múltiple o empate, derivada no acotable)."""
        P = self.P
        A_, B, C, L = tri[k]
        Zr = Z if P.rho_is_one else ipow(Z, P.rho)
        dz = self._dz(tri, k, Z)
        if _sign(dz) == 0:
            return None
        gv = _gscale(L.g, Z) if P.rho_is_one else _gadd(_gscale(B.g, Z), _gscale(C.g, Zr))
        if gv is None:
            return ((ZERO,) * 3, (ZERO,) * 3, (ZERO,) * 3)
        f = self.density(Z)
        dc = tuple(Iv(-1.0, -1.0) * gi / dz for gi in gv)
        sym = Iv(-1.0, 1.0)
        jE = 2.0 * P.beta * Z * f
        jA = (P.gamma * Z * f) if self.design == "G" else ((P.gamma * Z + x.kF.v * Zr) * f)
        jW = Zr * f
        return (tuple(sym * jE * d for d in dc), tuple(sym * jA * d for d in dc), tuple(sym * jW * d for d in dc))

    def _leibniz_aggregate(self, tri, per_tri: dict):
        """Una raíz de T_k aporta UN término aunque su ubicación posible abarque varias celdas: por tramo contiguo de
        celdas ambiguas se toma la envolvente (no la suma) de los términos por celda, multiplicada por el máximo de
        raíces del tramo: 1 si dT_k/dz no se anula en el tramo; 2 si se anula (T_k/z^rho es convexa o cóncava en
        u = z^(1-rho): a lo sumo dos raíces en total)."""
        gE = gA = gW = None
        for k, items in per_tri.items():
            items.sort(key=lambda t: t[0])
            runs, cur = [], [items[0]]
            for it in items[1:]:
                if it[0] <= cur[-1][1]:
                    cur.append(it)
                else:
                    runs.append(cur)
                    cur = [it]
            runs.append(cur)
            total_roots = 0
            for r in runs:
                Zu = Iv(min(_edge(t[0], self.s_m, self.P.z_m).lo for t in r), max(_edge(t[1], self.s_m, self.P.z_m).hi for t in r))
                nmax = 1 if _sign(self._dz(tri, k, Zu)) != 0 else 2
                total_roots += nmax
                hulls = []
                for comp in range(3):
                    h = [None, None, None]
                    for (_, _, t) in r:
                        for c in range(3):
                            v = t[comp][c]
                            h[c] = v if h[c] is None else h[c].hull(v)
                    hulls.append(tuple(hh * float(nmax) for hh in h))
                gE, gA, gW = _gadd(gE, hulls[0]), _gadd(gA, hulls[1]), _gadd(gW, hulls[2])
            if total_roots > 2 and not self.P.rho_is_one:
                pass   # la cota por tramos ya es válida; el máximo global de 2 raíces solo podría estrecharla
        return gE, gA, gW

    # ---------------------------------------------------------------------------------------- formas de encierro
    def R_box(self, Td: Iv, Tf: Iv, Phi: Iv | None = None) -> Iv:
        return self.R_box_g(Td, Tf, Phi)[0]

    def R_box_g(self, Td: Iv, Tf: Iv, Phi: Iv | None = None, *, force: tuple = ()):
        """(encierro de R sobre la caja, {'score': puntaje por eje para bisección o None, 'jump': la caja toca una
        curva de salto}). Encierro = natural ∩ forma de valor medio; con pliegue de ramas suaves, forma de valor medio
        POR RAMA combinada con max/min (orden dos en el pliegue); con salto, envolvente de las ramas forzadas."""
        nat, g, br = self.R_full(Td, Tf, Phi, grad=True, force=force)
        if br is not None and br["kind"] == "jump":
            lo, hi = INF, -INF
            for f2 in br["parts"]:
                e2, _ = self.R_box_g(Td, Tf, Phi, force=f2)
                lo, hi = min(lo, e2.lo), max(hi, e2.hi)
            lo, hi = max(nat.lo, lo), min(nat.hi, hi)
            score = None if br["lg"] is None else tuple(max(abs(x.lo), abs(x.hi)) for x in br["lg"])
            return (Iv(lo, hi) if lo <= hi else nat), {"score": score, "jump": True}
        if g is None:
            return nat, {"score": None, "jump": False}
        Phi_ = self.P.phi if Phi is None else Phi
        cd, cf, cp = 0.5 * (Td.lo + Td.hi), 0.5 * (Tf.lo + Tf.hi), 0.5 * (Phi_.lo + Phi_.hi)
        vc, _ = self.R(Iv(cd, cd), Iv(cf, cf), Iv(cp, cp), grad=False, force=force)
        Dl = (Td - cd, Tf - cf, Phi_ - cp)
        mv = vc + g[0] * Dl[0] + g[1] * Dl[1] + g[2] * Dl[2]
        lo, hi = max(nat.lo, mv.lo), min(nat.hi, mv.hi)
        score = tuple(max(abs(gi.lo), abs(gi.hi)) for gi in g)
        if br is not None:
            dd = self._kink_D(cd, cf, cp, br["info"])
            if dd is not None:
                D, Cc = dd
                zm = self.P.z_m
                if Cc.lo > zm.hi:
                    v_in, v_out = vc, vc - D
                elif Cc.hi < zm.lo:
                    v_out, v_in = vc, vc + D
                else:
                    v_out, v_in = vc.hull(vc - D), vc.hull(vc + D)
                blo, bhi = _branch_bounds(br["kind"], (v_out, br["g_out"]), (v_in, br["g_in"]), Dl)
                lo, hi = max(lo, blo), min(hi, bhi)
                score = tuple(max(br["g_out"][i].hi - br["g_out"][i].lo, br["g_in"][i].hi - br["g_in"][i].lo)
                              for i in range(3))
        return (Iv(lo, hi) if lo <= hi else nat), {"score": score, "jump": False}

    def R_box_shear(self, X: Iv, Y: Iv, Phi: Iv, sigma: float, axis: int, m: float, lim: tuple):
        """Encierro de R~(tau', phi) = R(tau' + sigma (phi - m) e_axis, phi) sobre los (tau', phi) de X x Y x Phi cuya
        imagen real es factible (tau_axis en lim = (lo, hi) del menú), o None si la caja real recortada es vacía.

        R~ es R compuesta con un corte afín, así que su gradiente es (dR/dtau_d, dR/dtau_f, dR/dphi + sigma dR/dtau_axis)
        evaluado en la región REAL: la caja (X + sigma (Phi - m)) recortada al menú, que contiene la imagen de todo punto
        factible. Forma de valor medio en coordenadas cortadas: el centro c se toma en coordenadas reales dentro de esa
        caja y su preimagen cortada se ENCIERRA; el segmento real entre c y cualquier punto factible queda en la caja
        (convexa), donde valen los encierros de gradiente. En quiebres, por rama (R = min/max de ramas suaves, Lema 3)
        con gradientes de rama cortados. Vale para cualquier sigma; sigma solo decide la estrechez (FUNDAMENTO_COTAS §3)."""
        shift = Iv.point(sigma) * (Phi - m)
        Ta = (X if axis == 0 else Y) + shift
        lo_a, hi_a = max(Ta.lo, lim[0]), min(Ta.hi, lim[1])
        if lo_a > hi_a:
            return None, None
        Td, Tf = (Iv(lo_a, hi_a), Y) if axis == 0 else (X, Iv(lo_a, hi_a))
        nat, g, br = self.R_full(Td, Tf, Phi, grad=True)
        if g is None or (br is not None and br["kind"] == "jump"):
            return self.R_box_g(Td, Tf, Phi)                    # región real completa: válido (superconjunto)
        cp = 0.5 * (Phi.lo + Phi.hi)
        cx, cy = 0.5 * (X.lo + X.hi), 0.5 * (Y.lo + Y.hi)
        if axis == 0:
            ax, ay = min(max(cx + sigma * (cp - m), Td.lo), Td.hi), cy
        else:
            ax, ay = cx, min(max(cy + sigma * (cp - m), Tf.lo), Tf.hi)
        vc, _ = self.R(Iv(ax, ax), Iv(ay, ay), Iv(cp, cp), grad=False)
        back = Iv.point(sigma) * (Iv.point(cp) - m)
        cxs, cys = (Iv.point(ax) - back, Iv.point(ay)) if axis == 0 else (Iv.point(ax), Iv.point(ay) - back)
        Dl = (X - cxs, Y - cys, Phi - cp)
        sg = Iv.point(sigma)

        def shear(gr):
            return gr[0], gr[1], gr[2] + sg * gr[axis]
        gs = shear(g)
        mv = vc + gs[0] * Dl[0] + gs[1] * Dl[1] + gs[2] * Dl[2]
        lo, hi = max(nat.lo, mv.lo), min(nat.hi, mv.hi)
        score = tuple(max(abs(gi.lo), abs(gi.hi)) for gi in gs)
        if br is not None:
            dd = self._kink_D(ax, ay, cp, br["info"])
            if dd is not None:
                D, Cc = dd
                zm = self.P.z_m
                if Cc.lo > zm.hi:
                    v_in, v_out = vc, vc - D
                elif Cc.hi < zm.lo:
                    v_out, v_in = vc, vc + D
                else:
                    v_out, v_in = vc.hull(vc - D), vc.hull(vc + D)
                go, gi = shear(br["g_out"]), shear(br["g_in"])
                blo, bhi = _branch_bounds(br["kind"], (v_out, go), (v_in, gi), Dl)
                lo, hi = max(lo, blo), min(hi, bhi)
                score = tuple(max(go[i].hi - go[i].lo, gi[i].hi - gi[i].lo) for i in range(3))
        return (Iv(lo, hi) if lo <= hi else nat), {"score": score, "jump": False}


def _lin(v: Iv, g, D) -> Iv:
    return v + g[0] * D[0] + g[1] * D[1] + g[2] * D[2]


def _branch_bounds(kind: str, b0, b1, D) -> tuple[float, float]:
    """Cotas (inferior, superior) de R sobre la caja con R = max(R0, R1) ('max'), min(R0, R1) ('min') o R en {R0, R1}
    ('amb'), cada rama con forma de valor medio v_b + g_b . (tau - centro). Para 'min' la cota superior es el
    supremo EXACTO (con redondeo dirigido) de min(U0, U1), con U_b la cota lineal superior por ortante: el máximo de
    un mínimo de dos funciones lineales sobre una caja está en un vértice o en el cruce U0 = U1 sobre una arista."""
    l0, l1 = _lin(b0[0], b0[1], D), _lin(b1[0], b1[1], D)
    if kind == "max":
        return max(l0.lo, l1.lo), max(l0.hi, l1.hi)
    if kind == "amb":
        return min(l0.lo, l1.lo), max(l0.hi, l1.hi)
    lower = min(l0.lo, l1.lo)
    pieces = []
    for Di in D:
        if Di.lo < 0.0 < Di.hi:
            pieces.append(((Di.lo, 0.0, False), (0.0, Di.hi, True)))
        else:
            pieces.append(((Di.lo, Di.hi, Di.lo >= 0.0),))
    best = -INF

    def U(b, slopes, d):
        v = Iv(b[0].hi, b[0].hi)
        for sl, di in zip(slopes, d):
            v = v + Iv(sl, sl) * Iv(di, di)
        return v
    for orth in itertools.product(*pieces):
        sl0 = [b0[1][i].hi if o[2] else b0[1][i].lo for i, o in enumerate(orth)]
        sl1 = [b1[1][i].hi if o[2] else b1[1][i].lo for i, o in enumerate(orth)]
        axes_ = [i for i, o in enumerate(orth) if o[1] > o[0]]
        verts = list(itertools.product(*[(o[0], o[1]) if o[1] > o[0] else (o[0],) for o in orth]))
        for v in verts:
            best = max(best, min(U(b0, sl0, v).hi, U(b1, sl1, v).hi))
        for j in axes_:
            for v in verts:
                if v[j] != orth[j][0]:
                    continue
                q = list(v)
                q[j] = orth[j][1]
                a0, e0 = U(b0, sl0, v), U(b0, sl0, q)
                a1, e1 = U(b1, sl1, v), U(b1, sl1, q)
                den = (e0 - a0) - (e1 - a1)
                if den.lo <= 0.0 <= den.hi:
                    best = max(best, min(max(a0.hi, e0.hi), max(a1.hi, e1.hi)))
                    continue
                T = (a1 - a0) / den
                tlo, thi = max(0.0, T.lo), min(1.0, T.hi)
                if tlo <= thi:
                    Tt = Iv(tlo, thi)
                    best = max(best, min((a0 + Tt * (e0 - a0)).hi, (a1 + Tt * (e1 - a1)).hi))
    return lower, best


# ============================================================================================ supremo certificado
@dataclass
class SupBound:
    approx: float            # valor en flotante del mejor punto (diagnóstico)
    lower: float             # cota inferior DEMOSTRADA del supremo (encierro puntual en `point`)
    upper: float             # cota superior DEMOSTRADA (máximo de encierros de cajas vivas)
    point: tuple
    live: list
    boxes: int
    jump_live: bool          # alguna caja viva toca una curva de salto (rho = 1): alcance no decidido
    shear: tuple | None = None   # (sigma, eje, m, E): cajas vivas en coordenadas cortadas (sup_bound_shear)


def sup_bound(eng: Engine, instrument: str, bar_d: float, bar_f: float, *, tol: float, max_boxes: int = 4000,
              Phi: Iv | None = None, value=None, jump_budget: int = 600, goal: float | None = None,
              start: list | None = None) -> SupBound:
    """Rama y cota sobre el menú. Cota inferior = encierro puntual en el mejor punto visitado; superior = máximo de
    los encierros de las cajas vivas. Se poda solo con cota superior ESTRICTAMENTE menor que la inferior, así que las
    cajas vivas cubren el conjunto de maximizadores para todo phi en Phi. `goal` (unidades de R): se detiene en cuanto
    el encierro [inferior, superior] del supremo excluye ese nivel (decisión de signo, no cierre); también puede ser una
    función (inferior, superior) -> bool que decide con la misma cuenta que hará el llamador (_goal_decided).
    `start`: cajas iniciales en lugar del menú completo. SOLO es válido si el llamador demuestra que fuera de su unión
    R(., phi) < sup_tau R(., phi) para todo phi de Phi (p. ej. cajas vivas de una rama y cota con Phi' ⊇ Phi: lo
    podado tiene cota superior < inferior demostrada <= C2(phi) B_pot); entonces el supremo es el de la unión."""
    from .supremum import axes
    (dl, dh), (fl, fh) = axes(instrument, bar_d, bar_f)
    best = [-INF, -INF, None, None]          # (aprox, cota inferior demostrada, x, y)

    def visit(x, y):
        v, _ = eng.R(Iv(x, x), Iv(y, y), Phi, grad=False)
        approx = value(x, y) if value is not None else 0.5 * (v.lo + v.hi)
        if v.lo > best[1]:
            best[:] = [approx, v.lo, x, y]
    for x in {dl, dh, 0.5 * (dl + dh)}:
        for y in {fl, fh, 0.5 * (fl + fh)}:
            visit(x, y)
    if start:
        for b in start:
            visit(0.5 * (b[0] + b[1]), 0.5 * (b[2] + b[3]))
        heap = []
        for b in start:
            e0, i0_ = eng.R_box_g(Iv(b[0], b[1]), Iv(b[2], b[3]), Phi)
            if e0.hi >= best[1]:
                heap.append((-e0.hi, tuple(b), i0_))
        heapq.heapify(heap)
    else:
        root = (dl, dh, fl, fh)
        e0, i0_ = eng.R_box_g(Iv(dl, dh), Iv(fl, fh), Phi)
        heap = [(-e0.hi, root, i0_)]
    boxes = 0
    while heap:
        neg_hi, b, info = heap[0]
        if -neg_hi - best[1] <= tol or boxes >= max_boxes:
            break
        if goal is not None and _goal_decided(goal, best[1], -neg_hi):
            break
        heapq.heappop(heap)
        boxes += 1
        x0, x1, y0, y1 = b
        if x1 == x0 and y1 == y0:
            heapq.heappush(heap, (neg_hi, b, info))    # caja degenerada: no se puede refinar más
            break
        sc = info["score"]
        wx = (x1 - x0) * (sc[0] if sc is not None else 1.0)
        wy = (y1 - y0) * (sc[1] if sc is not None else 1.0)
        if y1 == y0 or (x1 > x0 and wx >= wy):
            m = 0.5 * (x0 + x1)
            kids = ((x0, m, y0, y1), (m, x1, y0, y1))
        else:
            m = 0.5 * (y0 + y1)
            kids = ((x0, x1, y0, m), (x0, x1, m, y1))
        if not (b[0] <= m <= b[1] or b[2] <= m <= b[3]) or kids[0] == b or kids[1] == b:
            heapq.heappush(heap, (neg_hi, b, info))
            break
        for k in kids:
            visit(0.5 * (k[0] + k[1]), 0.5 * (k[2] + k[3]))
            ek, ik = eng.R_box_g(Iv(k[0], k[1]), Iv(k[2], k[3]), Phi)
            if ek.hi >= best[1]:
                heapq.heappush(heap, (-ek.hi, k, ik))
    # alcance: con cajas vivas que tocan un salto, refinar SOLO esas (sin tocar la cota global) hasta podarlas; si
    # sobreviven, el alcance del supremo queda sin decidir (nunca se afirma alcanzado sin prueba)
    extra = 0
    while any(i["jump"] for _, _, i in heap) and extra < jump_budget:
        idx = max((q for q in range(len(heap)) if heap[q][2]["jump"]), key=lambda q: -heap[q][0])
        neg_hi, b, info = heap[idx]
        heap[idx] = heap[-1]
        heap.pop()
        heapq.heapify(heap)
        extra += 1
        x0, x1, y0, y1 = b
        sc = info["score"]
        wx = (x1 - x0) * (sc[0] if sc is not None else 1.0)
        wy = (y1 - y0) * (sc[1] if sc is not None else 1.0)
        if y1 == y0 or (x1 > x0 and wx >= wy):
            m = 0.5 * (x0 + x1)
            kids = ((x0, m, y0, y1), (m, x1, y0, y1))
        else:
            m = 0.5 * (y0 + y1)
            kids = ((x0, x1, y0, m), (x0, x1, m, y1))
        if kids[0] == b or kids[1] == b:
            heapq.heappush(heap, (neg_hi, b, info))
            break
        for k in kids:
            visit(0.5 * (k[0] + k[1]), 0.5 * (k[2] + k[3]))
            ek, ik = eng.R_box_g(Iv(k[0], k[1]), Iv(k[2], k[3]), Phi)
            if ek.hi >= best[1]:
                heapq.heappush(heap, (-ek.hi, k, ik))
    upper = max(best[1], -heap[0][0]) if heap else best[1]
    live = [b for nh, b, _ in heap if -nh >= best[1]]     # con cota superior < inferior no hay maximizadores
    return SupBound(best[0], best[1], upper, (best[2], best[3]), live, boxes + extra,
                    any(i["jump"] for _, _, i in heap))


def _goal_decided(goal, lower: float, upper: float) -> bool:
    """Parada dirigida: `goal` numérico (unidades de R) o función (inferior, superior) -> bool."""
    return goal(lower, upper) if callable(goal) else (upper < goal or lower > goal)


def sup_bound_shear(eng: Engine, instrument: str, bar_d: float, bar_f: float, *, tol: float, Phi: Iv, sigma: float,
                    axis: int, m: float, max_boxes: int = 4000, goal: float | None = None, seed=None,
                    floor_mult: float = 2.0) -> SupBound:
    """Encierro de {sup_tau R(tau, phi): phi en Phi} por rama y cota en coordenadas CORTADAS tau' = tau - sigma (phi - m)
    e_axis (FUNDAMENTO_COTAS §3). Cota superior: máximo de encierros de R~ sobre cajas que cubren el menú ampliado en
    E = |sigma| max|phi - m| (toda pareja factible (tau, phi) tiene preimagen ahí: superconjunto). Cota inferior: solo en
    puntos tau' cuyo segmento completo {tau' + sigma (phi - m) e_axis} está dentro del menú, así que
    C2(phi) B_pot >= R~(tau', phi) para todo phi de Phi. Se poda solo con cota superior < inferior; `goal` detiene la
    búsqueda en cuanto el encierro excluye ese nivel. Parada por tolerancia: max(tol, floor_mult x ancho del encierro en
    el mejor punto), porque la brecha no baja de la variación de R~ con phi (solo decide cuándo parar, no el rigor)."""
    from .supremum import axes
    (dl, dh), (fl, fh) = axes(instrument, bar_d, bar_f)
    lo_ax, hi_ax = (dl, fl), (dh, fh)
    E = EL.up(abs(sigma) * max(abs(Phi.lo - m), abs(Phi.hi - m)))
    best = [-INF, None, None, 0.0]

    lim = (lo_ax[axis], hi_ax[axis])

    def visit(x, y):
        c = x if axis == 0 else y
        if c - E < lim[0] or c + E > lim[1]:
            return
        e, _ = eng.R_box_shear(Iv(x, x), Iv(y, y), Phi, sigma, axis, m, lim)
        if e is not None and e.lo > best[0]:
            best[:] = [e.lo, x, y, e.hi - e.lo]
    rx0, rx1, ry0, ry1 = dl, dh, fl, fh
    if axis == 0:
        rx0, rx1 = EL.dn(dl - E), EL.up(dh + E)
    else:
        ry0, ry1 = EL.dn(fl - E), EL.up(fh + E)
    pts = {(0.5 * (dl + dh), 0.5 * (fl + fh))}
    if seed is not None:
        pts.add(tuple(seed))
    for x, y in pts:
        visit(x, y)
    root = (rx0, rx1, ry0, ry1)
    e0, i0_ = eng.R_box_shear(Iv(rx0, rx1), Iv(ry0, ry1), Phi, sigma, axis, m, lim)
    heap = [(-e0.hi, root, i0_)]
    boxes = 0
    while heap:
        neg_hi, b, info = heap[0]
        if -neg_hi - best[0] <= max(tol, floor_mult * best[3]) or boxes >= max_boxes:
            break
        if goal is not None and _goal_decided(goal, best[0], -neg_hi):
            break
        heapq.heappop(heap)
        boxes += 1
        x0, x1, y0, y1 = b
        sc = info["score"]
        wx = (x1 - x0) * (sc[0] if sc is not None else 1.0)
        wy = (y1 - y0) * (sc[1] if sc is not None else 1.0)
        if y1 == y0 or (x1 > x0 and wx >= wy):
            mm = 0.5 * (x0 + x1)
            kids = ((x0, mm, y0, y1), (mm, x1, y0, y1))
        else:
            mm = 0.5 * (y0 + y1)
            kids = ((x0, x1, y0, mm), (x0, x1, mm, y1))
        if kids[0] == b or kids[1] == b:
            heapq.heappush(heap, (neg_hi, b, info))
            break
        for k in kids:
            visit(0.5 * (k[0] + k[1]), 0.5 * (k[2] + k[3]))
            ek, ik = eng.R_box_shear(Iv(k[0], k[1]), Iv(k[2], k[3]), Phi, sigma, axis, m, lim)
            if ek is not None and ek.hi >= best[0]:          # None: sin puntos factibles en la caja
                heapq.heappush(heap, (-ek.hi, k, ik))
    upper = max(best[0], -heap[0][0]) if heap else best[0]
    return SupBound(best[0], best[0], upper, (best[1], best[2]), [b for nh, b, _ in heap if -nh >= best[0]], boxes, False,
                    shear=(sigma, axis, m, E))
