"""Teoría v2.2 (fase4_teoria/baseline_model_v2_2.md) evaluada de forma exacta por intervalos de tamaño.

Ecuaciones implementadas (numeración de la teoría):
- reporte doméstico (1.18), (1.23): r* = x_d^eta_d, tau~_d = (1 - x_d^(1+eta_d))/(1+eta_d);
- reporte extranjero (1.40), (1.40e/f): q* = x_f^eta_f, tau~_f = obligación + costo de ocultamiento;
- costo formal del pago (1.42): k_F = kappa0 (1 + phi tau~_f);
- ganancias (2.2), (2.3), (2.6), (2.7), (2.8) y regla de desempate S13;
- bases incrementales (3.3)-(3.9): B_d = E0 + r* A_v, B_f = q* kappa0 x_f^-phi W_F, R = tau_d B_d + tau_f B_f;
- potencial (8.3) B_pot = gamma a z_m/(a-1); incidencia exacta (1.50) s_P.

Cada diferencia de ganancias es un trinomio generalizado A z^theta + B z + C z^rho (theta > 1 >= rho >= 0). Sus
raíces positivas se aíslan de forma exacta en u = z^(1-rho), donde el trinomio es convexo o cóncavo (a lo sumo dos
raíces). El signo en cada intervalo se deduce del signo en z -> 0+ y del número de raíces simples previas: nunca se
evalúa una diferencia casi nula en un punto medio. Las integrales son momentos Pareto cerrados (Lema 1, (4.5)).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .numeric import brent, NumericError

DESIGNS = ("G", "N")
EPS = 2.220446049250313e-16


class DomainError(ValueError):
    """Primitivas o tasas fuera del dominio en que la teoría está demostrada."""


@dataclass(frozen=True)
class State:
    """Estado estructural dimensional (derivados ya calculados)."""
    a: float
    rho: float
    kappa0: float
    beta: float
    delta: float
    theta: float
    gamma: float
    z_m: float
    eta_d: float
    eta_f: float
    phi: float
    t: float = 0.0
    c_legal: float = 1.0

    def __post_init__(self):
        if not (self.a > 1.0):
            raise DomainError("A_GT1")
        if not (0.0 <= self.rho <= 1.0):
            raise DomainError("RHO_OUTSIDE_S4")
        if not (self.theta > 1.0):
            raise DomainError("THETA_GT1")
        if not (self.rho < self.a):
            raise DomainError("RHO_LT_A")
        if not (self.gamma > 0 and self.z_m > 0 and self.delta > 0 and self.kappa0 > 0 and self.beta >= 0):
            raise DomainError("POSITIVE_SCALES")
        if not (self.eta_d >= 0 and self.eta_f > 0 and 0.0 <= self.phi <= 1.0):
            raise DomainError("REPORTING_DOMAIN")
        if self.t != 0.0:
            raise DomainError("T_EXTENSION_INACTIVE")
        if self.c_legal != 1.0:
            raise DomainError("C_LEGAL_EXTENSION_INACTIVE")

    @property
    def B_pot(self) -> float:
        return self.gamma * self.a * self.z_m / (self.a - 1.0)


def derive(prim: dict) -> dict:
    """Primitivas comunes normalizadas -> derivados (formulas.json; DOMINIOS_Y_FORMULAS.md).

    Condiciones antes de potencias/divisiones. rho debe ser interior (0<rho<=1): rho=0 es límite S18 y no se evalúa.
    """
    need = ("a", "rho", "kappa_tilde", "beta_tilde", "u_theta", "z_cost", "eta_d", "eta_f", "phi", "gamma", "z_m", "t", "c_legal")
    missing = [k for k in need if k not in prim]
    if missing:
        raise DomainError("MISSING_PRIMITIVE:" + ",".join(missing))
    a, rho = float(prim["a"]), float(prim["rho"])
    gamma, z_m, z_cost = float(prim["gamma"]), float(prim["z_m"]), float(prim["z_cost"])
    kt, bt, ut = float(prim["kappa_tilde"]), float(prim["beta_tilde"]), float(prim["u_theta"])
    if not (gamma > 0 and z_m > 0 and z_cost > 0 and kt > 0 and bt > 0):
        raise DomainError("POSITIVE_SCALES")
    if not a > 1.0:
        raise DomainError("A_GT1")
    if not 0.0 < ut < 1.0:
        raise DomainError("U_THETA_OPEN")
    if rho > 1.0:
        raise DomainError("RHO_UPPER_S4")
    if not rho > 0.0:
        raise DomainError("RHO_ZERO_LIMIT")
    if not a - rho > 0:
        raise DomainError("RHO_LT_A")
    theta = 1.0 + ut * (a - 1.0)
    if not (1.0 < theta < a):
        raise DomainError("THETA_BOUNDS")
    delta_tilde = z_cost ** (1.0 - theta)
    return {
        "theta": theta,
        "delta_tilde": delta_tilde,
        "beta": bt * gamma,
        "delta": delta_tilde * gamma * z_m ** (1.0 - theta),
        "kappa0": kt * gamma * z_m ** (1.0 - rho),
        "q_pot": kt * (a - 1.0) / (a - rho),
        "B_pot": gamma * a * z_m / (a - 1.0),
    }


def state_from_primitives(prim: dict) -> State:
    d = derive(prim)
    return State(a=float(prim["a"]), rho=float(prim["rho"]), kappa0=d["kappa0"], beta=d["beta"], delta=d["delta"],
                 theta=d["theta"], gamma=float(prim["gamma"]), z_m=float(prim["z_m"]), eta_d=float(prim["eta_d"]),
                 eta_f=float(prim["eta_f"]), phi=float(prim["phi"]), t=float(prim["t"]), c_legal=float(prim["c_legal"]))


# ----------------------------------------------------------------------------------------- reporte e incidencia
def _check_rate(tau: float) -> float:
    if not (0.0 <= tau < 1.0):
        raise DomainError("RATE_OUTSIDE_[0,1)")
    return math.log1p(-tau)


def r_star(tau_d: float, eta_d: float) -> float:
    return math.exp(eta_d * _check_rate(tau_d))


def tilde_d(tau_d: float, eta_d: float) -> float:
    lx = _check_rate(tau_d)
    if eta_d == 0.0:
        return tau_d
    return -math.expm1((1.0 + eta_d) * lx) / (1.0 + eta_d)


def q_star(tau_f: float, eta_f: float) -> float:
    return math.exp(eta_f * _check_rate(tau_f))


def tilde_f(tau_f: float, eta_f: float, phi: float) -> float:
    """Carga efectiva de la coalición por unidad de pago mundial, (1.40e) y (1.40f)."""
    lx = _check_rate(tau_f)
    if tau_f == 0.0:
        return 0.0
    alpha = eta_f - phi
    obligation = tau_f * math.exp(alpha * lx)
    if alpha == 0.0:
        hiding = -eta_f * lx - eta_f * tau_f
    else:
        hiding = eta_f * (-math.expm1(alpha * lx)) / alpha
        hiding -= eta_f * (-math.expm1((alpha + 1.0) * lx)) / (alpha + 1.0)
    return obligation + hiding


def tilde_f_prime(tau_f: float, eta_f: float, phi: float) -> float:
    """Envolvente (1.40i): q* x_f^(-phi-1) (x_f + phi tau_f)."""
    x = 1.0 - tau_f
    return math.exp((eta_f - phi - 1.0) * _check_rate(tau_f)) * (x + phi * tau_f)


def gross_factor(tau_f: float, phi: float) -> float:
    return math.exp(-phi * _check_rate(tau_f))


def k_formal(s: State, tau_f: float) -> float:
    return s.kappa0 * (1.0 + s.phi * tilde_f(tau_f, s.eta_f, s.phi))


def provider_share(tau_f: float, phi: float) -> float:
    """s_P exacta (1.50); en tau_f = 0 su límite 1-phi (1.52), rotulado como límite por el llamador."""
    if tau_f == 0.0:
        return 1.0 - phi
    x = 1.0 - tau_f
    return (math.exp(phi * _check_rate(tau_f)) - x) / tau_f


# ----------------------------------------------------------------------------------------- trinomios
@dataclass(frozen=True)
class Trinomial:
    """A z^theta + B z + C z^rho; L = B + C calculado simbólicamente para rho = 1 (empates exactos)."""
    A: float
    B: float
    C: float
    L: float


def _sign(x: float) -> int:
    return (x > 0) - (x < 0)


class Roots:
    """Raíces positivas (ln z) con multiplicidad; signo en z -> 0+; identicamente nulo."""
    __slots__ = ("lnz", "double", "sign0", "identical")

    def __init__(self, lnz, double, sign0, identical=False):
        self.lnz = lnz
        self.double = double
        self.sign0 = sign0
        self.identical = identical

    def sign_after(self, ln_point: float) -> int:
        """Signo en un punto que no es raíz, a la derecha de ln_point inclusive de raíces <= ln_point."""
        if self.identical:
            return 0
        s = self.sign0
        for r, dbl in zip(self.lnz, self.double):
            if r <= ln_point and not dbl:
                s = -s
        return s


def trinomial_roots(tri: Trinomial, theta: float, rho: float) -> Roots:
    A, B, C = tri.A, tri.B, tri.C
    if rho == 1.0:
        L = tri.L
        if A == 0.0:
            return Roots([], [], _sign(L), identical=(L == 0.0))
        sign0 = _sign(L) if L != 0.0 else _sign(A)
        ratio = -L / A
        if ratio > 0.0:
            return Roots([math.log(ratio) / (theta - 1.0)], [False], sign0)
        return Roots([], [], sign0)
    one = 1.0 - rho
    if A == 0.0:
        if B == 0.0:
            return Roots([], [], _sign(C), identical=(C == 0.0))
        sign0 = _sign(C) if C != 0.0 else _sign(B)
        ratio = -C / B
        if ratio > 0.0:
            return Roots([math.log(ratio) / one], [False], sign0)
        return Roots([], [], sign0)
    p = (theta - rho) / one
    sign0 = _sign(C) if C != 0.0 else (_sign(B) if B != 0.0 else _sign(A))
    if C == 0.0:
        # rem116 (P4-RAICES-C0-SUBDESBORDAMIENTO): con C = 0 exacto el trinomio es el binomio z·(A z^(theta-1) + B), A != 0. Su única raíz
        # positiva (A·B < 0) es SIMPLE, ln z* = [ln|B| - ln|A|]/(theta - 1), calculada en logaritmos sin formar z*. La rama general evaluaba el
        # punto estacionario, donde ambas exponenciales pueden subdesbordar a 0 (g* = 0 y tol = 0 se tomaban por tangencia: raíz doble falsa y
        # signo equivocado tras ella). C pequeño pero no nulo sigue la rama general.
        if B == 0.0 or (A > 0.0) == (B > 0.0):
            return Roots([], [], sign0)
        return Roots([(math.log(abs(B)) - math.log(abs(A))) / (theta - 1.0)], [False], sign0)
    # g(s) = A e^{p s} + B e^{s} + C, s = ln u, u = z^{1-rho}
    flip = -1.0 if A < 0 else 1.0
    a_, b_, c_ = A * flip, B * flip, C * flip  # a_ > 0: g convexa en u

    def g(s: float) -> float:
        ps = p * s
        if ps > 700.0:
            return 1.0e300  # a_ > 0 domina: signo positivo, valor finito para el acotador
        return a_ * math.exp(ps) + b_ * math.exp(s) + c_ if s > -745.0 else c_

    def scale(s: float) -> float:
        return abs(a_ * math.exp(min(p * s, 700.0))) + abs(b_ * math.exp(min(s, 700.0))) + abs(c_)

    roots: list[tuple[float, bool]] = []

    def bracket_right(s0: float) -> float:
        s1 = max(s0 + 1.0, 1.0)
        while g(s1) <= 0.0:
            s1 = s1 * 2.0 + 1.0
            if s1 > 1e4:
                raise NumericError("sin cota superior de raíz")
        return s1

    def bracket_left(s0: float, target_sign: int) -> float:
        s1 = min(s0 - 1.0, -1.0)
        while _sign(g(s1)) != target_sign:
            s1 = s1 * 2.0 - 1.0
            if s1 < -1e4:
                raise NumericError("sin cota inferior de raíz")
        return s1

    ratio = -b_ / (a_ * p)
    if ratio > 0.0:
        s_star = math.log(ratio) / (p - 1.0)
        g_star = g(s_star)
        tol = 64.0 * EPS * scale(s_star)
        if abs(g_star) <= tol:
            # tangencia (raíz doble); si c_ < 0 además hay cruce a la izquierda imposible (g decrece desde c_<0)
            if c_ > 0.0:
                roots.append((s_star, True))
            elif c_ < 0.0:
                # g(-inf)=c_<0, mínimo ~0: el "mínimo" no puede ser 0 si g decrece desde c_<0; raíz a la derecha simple
                s_hi = bracket_right(s_star)
                roots.append((brent(g, s_star, s_hi), False))
            else:
                roots.append((s_star, True))
        elif g_star < 0.0:
            if c_ > 0.0:
                s_lo = bracket_left(s_star, 1)
                roots.append((brent(g, s_lo, s_star), False))
            s_hi = bracket_right(s_star)
            roots.append((brent(g, s_star, s_hi), False))
    else:
        if c_ < 0.0:
            s_lo = bracket_left(0.0, -1)
            s_hi = bracket_right(max(s_lo, 0.0))
            roots.append((brent(g, s_lo, s_hi), False))
    roots.sort()
    return Roots([s / one for s, _ in roots], [d for _, d in roots], sign0)


def pair_trinomials(s: State, tau_d: float, tau_f: float, design: str) -> dict[str, Trinomial]:
    """Diferencias de ganancias (sección 2) con coeficientes simplificados simbólicamente."""
    if design not in DESIGNS:
        raise DomainError("DESIGN")
    td = tilde_d(tau_d, s.eta_d)
    tf = tilde_f(tau_f, s.eta_f, s.phi)
    kF = s.kappa0 * (1.0 + s.phi * tf)
    one_td = 1.0 - td
    beta, gamma, delta, k0 = s.beta, s.gamma, s.delta, s.kappa0
    tb = tau_d * beta
    out = {"F0-I0": Trinomial(delta, -tb, 0.0, -tb),
           "I1-I0": Trinomial(0.0, gamma, -k0, gamma - k0),
           "I1-F0": Trinomial(-delta, tb + gamma, -k0, tb + (gamma - k0))}
    if design == "G":
        out["F1-F0"] = Trinomial(0.0, one_td * gamma, -kF, one_td * gamma - kF)
        out["F1-I0"] = Trinomial(delta, one_td * gamma - tb, -kF, (one_td * gamma - kF) - tb)
        out["F1-I1"] = Trinomial(delta, -(tb + td * gamma), -k0 * s.phi * tf, -(tb + td * gamma + k0 * s.phi * tf))
    else:
        out["F1-F0"] = Trinomial(0.0, one_td * gamma, -one_td * kF, one_td * (gamma - kF))
        out["F1-I0"] = Trinomial(delta, one_td * gamma - tb, -one_td * kF, one_td * (gamma - kF) - tb)
        cn = k0 - one_td * kF
        out["F1-I1"] = Trinomial(delta, -(tb + td * gamma), cn, cn - (tb + td * gamma))
    return out


# ----------------------------------------------------------------------------------------- partición y bases
def pareto_moment(a: float, z_m: float, m: float, lo: float, hi: float) -> float:
    """Integral de z^m dF sobre [lo, hi) con Pareto(a, z_m); Lema 1 (4.5), estable para lo ~ hi."""
    if m >= a:
        raise DomainError("MOMENT_ORDER")
    k = m - a
    tlo = math.exp(k * math.log(lo / z_m))
    if math.isinf(hi):
        diff = tlo
    else:
        diff = -tlo * math.expm1(k * math.log(hi / lo))
    return a / (a - m) * (z_m ** m) * diff


@dataclass(frozen=True)
class Interval:
    lo: float
    hi: float
    label: str   # F (adopción formal), I (adopción informal), N (no adopción)
    prior: str   # F o I (estatus previo)


@dataclass(frozen=True)
class Evaluation:
    tau_d: float
    tau_f: float
    design: str
    B_d: float
    B_f: float
    R: float
    B_pot: float
    E0: float
    A: float
    W_F: float
    mass_F: float
    mass_I: float
    mass_prior_F: float
    r: float
    q: float
    intervals: tuple

    @property
    def CS(self) -> float:
        return self.R / self.B_pot

    @property
    def topology(self) -> str:
        return "->".join(f"{iv.label}{iv.prior}" for iv in self.intervals)


def partition(s: State, tau_d: float, tau_f: float, design: str) -> list[Interval]:
    tri = pair_trinomials(s, tau_d, tau_f, design)
    roots = {k: trinomial_roots(v, s.theta, s.rho) for k, v in tri.items()}
    lzm = math.log(s.z_m)
    cuts = sorted({r for rt in roots.values() for r in rt.lnz if r > lzm})
    edges = [lzm] + cuts
    out: list[Interval] = []
    for i, lo in enumerate(edges):
        hi = edges[i + 1] if i + 1 < len(edges) else math.inf
        sg = {k: rt.sign_after(lo) for k, rt in roots.items()}
        prior = "F" if sg["F0-I0"] >= 0 else "I"
        if prior == "F":
            f_v0, i_v0 = sg["F1-F0"], sg["I1-F0"]
        else:
            f_v0, i_v0 = sg["F1-I0"], sg["I1-I0"]
        f_i1 = sg["F1-I1"]
        if f_v0 > 0 and f_i1 >= 0:
            label = "F"
        elif i_v0 > 0 and f_i1 < 0:
            label = "I"
        else:
            label = "N"
        z_lo = math.exp(lo)
        z_hi = math.inf if math.isinf(hi) else math.exp(hi)
        if out and out[-1].label == label and out[-1].prior == prior:
            out[-1] = Interval(out[-1].lo, z_hi, label, prior)
        else:
            out.append(Interval(z_lo if i else s.z_m, z_hi, label, prior))
    return out


def evaluate(s: State, tau_d: float, tau_f: float, design: str) -> Evaluation:
    intervals = partition(s, tau_d, tau_f, design)
    td_r = r_star(tau_d, s.eta_d)
    kF = k_formal(s, tau_f)
    E0 = A = W = mF = mI = mPF = 0.0
    for iv in intervals:
        m0 = pareto_moment(s.a, s.z_m, 0.0, iv.lo, iv.hi)
        m1 = pareto_moment(s.a, s.z_m, 1.0, iv.lo, iv.hi)
        d0 = 1.0 if iv.prior == "F" else 0.0
        if iv.prior == "F":
            mPF += m0
        if iv.label == "F":
            d1 = 1.0
            mr = pareto_moment(s.a, s.z_m, s.rho, iv.lo, iv.hi)
            mF += m0
            W += mr
            A += s.gamma * m1 if design == "G" else s.gamma * m1 - kF * mr
        elif iv.label == "I":
            d1 = 0.0
            mI += m0
        else:
            d1 = d0
        E0 += s.beta * m1 * (d1 - d0)
    q = q_star(tau_f, s.eta_f)
    B_d = E0 + td_r * A
    B_f = q * s.kappa0 * gross_factor(tau_f, s.phi) * W
    R = tau_d * B_d + tau_f * B_f
    return Evaluation(tau_d, tau_f, design, B_d, B_f, R, s.B_pot, E0, A, W, mF, mI, mPF, td_r, q, tuple(intervals))


def revenue(s: State, tau_d: float, tau_f: float, design: str) -> float:
    return evaluate(s, tau_d, tau_f, design).R


def jump_functions(s: State, design: str):
    """Curvas donde R puede saltar: solo con rho = 1, cuando F1-F0 es idénticamente nula (S13: no adopta).

    Para rho < 1 todas las raíces se mueven continuamente con las tasas y R es continua (con kinks).
    Devuelve funciones c(tau_d, tau_f) cuyo cero es la curva de salto; c > 0 es el lado de adopción formal previa.
    """
    if s.rho != 1.0:
        return []
    if design == "G":
        return [lambda td, tf: (1.0 - tilde_d(td, s.eta_d)) * s.gamma - k_formal(s, tf)]
    return [lambda td, tf: s.gamma - k_formal(s, tf)]
