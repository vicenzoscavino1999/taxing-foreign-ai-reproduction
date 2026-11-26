"""Soportes declarados: nudos anidados por nivel y transformaciones de formulas.json (sin muestreo aleatorio).

Nivel 0 = nudos declarados. Nivel l+1 inserta el punto medio de cada par consecutivo (2n-1 nudos): aritmético
(a+b)/2 en escala aritmética; geométrico sqrt(ab) en logarítmica (DOMINIOS: log en kappa_tilde, beta_tilde, z_cost,
eta_d, eta_f; aritmético en a, rho, u_theta, phi, pi). Los nudos declarados se conservan como Decimal exacto.
"""
from __future__ import annotations

import math
from decimal import Decimal, getcontext

getcontext().prec = 50


def _mid(a, b, scale):
    if scale == "logarithmic":
        return math.sqrt(float(a) * float(b))
    if isinstance(a, Decimal) and isinstance(b, Decimal):
        return (a + b) / 2
    return (float(a) + float(b)) / 2.0


def level_nodes(level0: list, scale: str | None, level: int) -> list:
    nodes = [Decimal(str(x)) if not isinstance(x, Decimal) else x for x in level0]
    for _ in range(level):
        out = []
        for a, b in zip(nodes, nodes[1:]):
            out.append(a)
            out.append(_mid(a, b, scale or "arithmetic"))
        out.append(nodes[-1])
        nodes = out
    return nodes


def transform(parameter: str, support: dict, transformation: str | None, stress_value=None) -> dict:
    """Aplica una transformación declarada de formulas.json a un soporte primario."""
    s = dict(support)
    halve = (transformation == "coordination_half" and parameter in ("eta_f", "phi")) or \
            (transformation == "enforcement_half" and parameter == "eta_f") or \
            (transformation == "coverage_half" and parameter == "phi")
    if halve and s["domain_kind"] == "continuous":
        s["lower"] = Decimal(str(s["lower"])) / 2
        s["upper"] = Decimal(str(s["upper"])) / 2
        s["level0_nodes"] = [Decimal(str(x)) / 2 for x in s["level0_nodes"]]
    if transformation == "tax_domain_stress":
        if parameter in ("bar_tau_d", "bar_tau_f"):
            s.update(lower=stress_value, upper=stress_value, level0_nodes=[stress_value])
        if parameter in ("tau_d", "tau_f") and s.get("variant_id") == "full":
            s.update(upper=stress_value, level0_nodes=[Decimal(0), stress_value])
    return s
