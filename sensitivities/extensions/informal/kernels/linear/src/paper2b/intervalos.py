"""Aritmética de intervalos con redondeo hacia afuera (un ulp por operación) para ENCIERROS demostrativos.

Un encierro [lo, hi] de g sobre una caja contiene TODOS los valores de g en la caja. Solo se usa como evidencia de
cobertura cuando la función tiene una extensión por intervalos exacta (polinomios, seno/coseno, productos y cocientes
de factores monótonos); una estimación por muestreo nunca se representa con esta clase.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


def _down(x: float) -> float:
    return math.nextafter(x, -math.inf) if math.isfinite(x) else x


def _up(x: float) -> float:
    return math.nextafter(x, math.inf) if math.isfinite(x) else x


@dataclass(frozen=True)
class Iv:
    lo: float
    hi: float

    def __post_init__(self):
        if not (self.lo <= self.hi) or math.isnan(self.lo) or math.isnan(self.hi):
            raise ValueError(f"intervalo inválido [{self.lo}, {self.hi}]")

    @staticmethod
    def point(x: float) -> "Iv":
        return Iv(float(x), float(x))

    @staticmethod
    def of(x) -> "Iv":
        return x if isinstance(x, Iv) else Iv.point(x)

    def __add__(self, o):
        o = Iv.of(o)
        return Iv(_down(self.lo + o.lo), _up(self.hi + o.hi))

    __radd__ = __add__

    def __neg__(self):
        return Iv(-self.hi, -self.lo)

    def __sub__(self, o):
        return self + (-Iv.of(o))

    def __rsub__(self, o):
        return Iv.of(o) - self

    def __mul__(self, o):
        o = Iv.of(o)
        ps = (self.lo * o.lo, self.lo * o.hi, self.hi * o.lo, self.hi * o.hi)
        return Iv(_down(min(ps)), _up(max(ps)))

    __rmul__ = __mul__

    def __truediv__(self, o):
        o = Iv.of(o)
        if o.lo <= 0.0 <= o.hi:
            raise ZeroDivisionError("divisor que contiene cero")
        return self * Iv(_down(1.0 / o.hi), _up(1.0 / o.lo))

    def __rtruediv__(self, o):
        return Iv.of(o) / self

    def sqr(self) -> "Iv":
        if self.lo >= 0:
            return Iv(_down(self.lo * self.lo), _up(self.hi * self.hi))
        if self.hi <= 0:
            return Iv(_down(self.hi * self.hi), _up(self.lo * self.lo))
        return Iv(0.0, _up(max(self.lo * self.lo, self.hi * self.hi)))

    def contains(self, x: float) -> bool:
        return self.lo <= x <= self.hi

    def excludes_zero(self) -> bool:
        return self.lo > 0.0 or self.hi < 0.0

    def width(self) -> float:
        return self.hi - self.lo

    def hull(self, o) -> "Iv":
        o = Iv.of(o)
        return Iv(min(self.lo, o.lo), max(self.hi, o.hi))


def sin(x: Iv) -> Iv:
    """Encierro de sin sobre x: extremos en los bordes y en pi/2 + k pi interiores."""
    lo, hi = math.sin(x.lo), math.sin(x.hi)
    vals = [lo, hi]
    k0 = math.ceil((x.lo - math.pi / 2) / math.pi)
    k1 = math.floor((x.hi - math.pi / 2) / math.pi)
    for k in range(k0, k1 + 1):
        vals.append(1.0 if k % 2 == 0 else -1.0)
    return Iv(max(-1.0, _down(min(vals) - 1e-16)), min(1.0, _up(max(vals) + 1e-16)))


def cos(x: Iv) -> Iv:
    return sin(x + math.pi / 2)


def poly(coeffs, x: Iv) -> Iv:
    """Horner por intervalos; coeffs de mayor a menor grado. Encierro válido (no necesariamente el rango exacto)."""
    acc = Iv.point(0.0)
    for c in coeffs:
        acc = acc * x + c
    return acc


def poly_eval(coeffs, x: float) -> float:
    acc = 0.0
    for c in coeffs:
        acc = acc * x + c
    return acc


def poly_deriv(coeffs):
    n = len(coeffs) - 1
    return [c * (n - i) for i, c in enumerate(coeffs[:-1])] or [0.0]


def poly_mul(p, q):
    out = [0.0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            out[i + j] += a * b
    return out
