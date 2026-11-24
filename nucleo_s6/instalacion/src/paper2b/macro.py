"""Puente macro-micro lambda_pi (diseño (18)-(20); protocolo lambda-pi S2; formulas.json).

  theta_W = (eta_w + eta_H)/(1 + eta_H);  s_L_marg = s_L_bar theta_W;  s_T_marg = sum_j pi_j s_bar_j;
  s_Pi_marg = 1 - s_L_marg - s_T_marg;     q_pot = kappa_tilde (a-1)/(a-rho);  lambda = s_Pi_marg/(1 - q_pot).

Aritmética racional exacta (Fraction) desde decimales exactos; la conversión a float solo al serializar.
Estados nacionales:
- vía condicional (E1/E2): un vector publicado por país/edición/año; sin intervalos (no se inventa precisión);
- vía estricta (E0/E3): dominio conjunto de primitivas compartidas; lambda es lineal-fraccional en ellas, así que sus
  extremos sobre la caja están en vértices (enumeración exhaustiva de vértices, sin suponer independencia de shares).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from itertools import product

SHARE_KEYS = ("s_L_bar", "s_bar_iva", "s_bar_otros_productos", "s_bar_produccion")
PI_KEYS = ("pi_iva", "pi_otros_productos", "pi_produccion")
SHARE_OF_PI = {"pi_iva": "s_bar_iva", "pi_otros_productos": "s_bar_otros_productos", "pi_produccion": "s_bar_produccion"}


def F(x) -> Fraction:
    if isinstance(x, bool):
        raise TypeError("bool no es número")
    if isinstance(x, Fraction):
        return x
    if isinstance(x, float):
        return Fraction(repr(x))
    return Fraction(str(x))


def theta_W(eta_w, eta_H) -> Fraction:
    eta_w, eta_H = F(eta_w), F(eta_H)
    if not eta_H > -1:
        raise ValueError("ETA_H_GT_MINUS1")
    return (eta_w + eta_H) / (1 + eta_H)


def q_pot(kappa_tilde, a, rho) -> Fraction:
    kappa_tilde, a, rho = F(kappa_tilde), F(a), F(rho)
    if not (a > 1 and a > rho):
        raise ValueError("MOMENT_DOMAIN")
    return kappa_tilde * (a - 1) / (a - rho)


@dataclass
class MacroValue:
    theta_W: Fraction
    s_L_marg: Fraction
    s_T_marg: Fraction
    s_Pi_marg: Fraction
    q_pot: Fraction
    lambda_pi: Fraction | None
    admissible: bool
    reasons: list = field(default_factory=list)

    @property
    def theta_W_negative(self) -> bool:
        return self.theta_W < 0


def bridge(shares: dict, omega: dict) -> MacroValue:
    """lambda y admisibilidad (q_pot<1, eta_H>-1, s_T_marg>=0, s_Pi_marg>0, lambda>0); negativos de theta_W se marcan."""
    tw = theta_W(omega["eta_w"], omega["eta_H"])
    sL = F(shares["s_L_bar"]) * tw
    sT = sum(F(omega[p]) * F(shares[SHARE_OF_PI[p]]) for p in PI_KEYS)
    sPi = 1 - sL - sT
    qp = q_pot(omega["kappa_tilde"], omega["a"], omega["rho"])
    reasons = []
    if not qp < 1:
        reasons.append("Q_POT_GE_1")
    if not sT >= 0:
        reasons.append("S_T_MARG_NEGATIVE")
    if not sPi > 0:
        reasons.append("S_PI_MARG_NONPOSITIVE")
    lam = sPi / (1 - qp) if qp < 1 else None
    if lam is not None and not lam > 0:
        reasons.append("LAMBDA_NONPOSITIVE")
    return MacroValue(tw, sL, sT, sPi, qp, lam, not reasons, reasons)


@dataclass(frozen=True)
class NationalState:
    """Punto nacional: primitivas fuente completas, cuatro shares, dominio conjunto y dependencias autenticadas."""
    country_id: str
    preregistration_id: str
    channel: str             # strict | conditional
    edition: str
    anchor_year: int
    label: str               # published_vector | vertex_lambda_min | vertex_lambda_max
    primitive_values: tuple  # ((primitive_id, Fraction, unit), ...) ordenado por id
    shares: tuple            # ((share_key, Fraction), ...) en SHARE_KEYS
    joint_domain_sha256: str
    dependencies: tuple = ()

    def share_dict(self) -> dict:
        return dict(self.shares)


def shares_from_terms(values: dict, terms: dict, denominator: str) -> dict:
    """shares = (suma de términos)/denominador, exacto; terms: share_key -> [(primitive_id, coeficiente), ...]."""
    den = F(values[denominator])
    if not den > 0:
        raise ValueError("DENOMINATOR_NONPOSITIVE")
    out = {}
    for key, tl in terms.items():
        out[key] = sum(F(c) * F(values[p]) for p, c in tl) / den
    return out


def strict_vertices(domains: dict, terms: dict, denominator: str, omega: dict):
    """Vértices de la caja de primitivas que minimizan y maximizan lambda para las coordenadas macro de omega.

    lambda(prim) = (1 - [theta_W COE + sum pi_j X_j]/PIB)/(1 - q_pot) es lineal-fraccional en las primitivas
    (PIB > 0 en toda la caja): sus extremos sobre el paralelepípedo están en vértices. Enumeración exhaustiva.
    """
    ids = sorted(domains)
    for p in ids:
        lo, hi = F(domains[p][0]), F(domains[p][1])
        if lo > hi:
            raise ValueError("DOMAIN_INVERTED:" + p)
    if F(domains[denominator][0]) <= 0:
        raise ValueError("DENOMINATOR_NOT_POSITIVE_ON_DOMAIN")
    choices = [((F(domains[p][0]),) if F(domains[p][0]) == F(domains[p][1]) else (F(domains[p][0]), F(domains[p][1]))) for p in ids]
    best_min = best_max = None
    for combo in product(*choices):
        vals = dict(zip(ids, combo))
        sh = shares_from_terms(vals, terms, denominator)
        m = bridge(sh, omega)
        key = m.s_L_marg + m.s_T_marg  # lambda es decreciente en T/PIB con q_pot fijo
        if best_min is None or key > best_min[0]:
            best_min = (key, vals, sh)
        if best_max is None or key < best_max[0]:
            best_max = (key, vals, sh)
    return {"vertex_lambda_min": (best_min[1], best_min[2]), "vertex_lambda_max": (best_max[1], best_max[2])}
