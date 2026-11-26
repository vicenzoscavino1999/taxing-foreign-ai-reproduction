"""Aritmética y serialización numérica sin redondeo ad hoc.

- ``canon_dec``: cadena decimal canónica del catálogo (formato fijo, sin ceros finales, -0 -> 0).
  Para floats usa la representación shortest-roundtrip de CPython; para Decimal/int/str la exacta.
- ``brent``: raíz acotada (Brent-Dekker) a precisión de máquina, sin SciPy.
- ``golden_max``: máximo unidimensional acotado (sección áurea + Brent parabólico), sin SciPy.
"""
from __future__ import annotations

import math
from decimal import Decimal, InvalidOperation
from fractions import Fraction


class NumericError(ValueError):
    pass


def canon_dec(value) -> str:
    """Decimal canónico del contrato: finito, sin exponente, sin ceros finales, sin -0."""
    if isinstance(value, bool):
        raise NumericError("bool no es decimal")
    if isinstance(value, float):
        if not math.isfinite(value):
            raise NumericError("decimal no finito")
        if value == 0.0:
            return "0"
        d = Decimal(repr(value))
    elif isinstance(value, int):
        d = Decimal(value)
    elif isinstance(value, Decimal):
        d = value
    elif isinstance(value, Fraction):
        den = value.denominator
        while den % 2 == 0:
            den //= 2
        while den % 5 == 0:
            den //= 5
        if den != 1:
            raise NumericError("fracción sin expansión decimal finita")
        d = Decimal(value.numerator) / Decimal(value.denominator)
    elif isinstance(value, str):
        try:
            d = Decimal(value)
        except InvalidOperation as exc:
            raise NumericError("decimal inválido: " + value) from exc
    else:
        raise NumericError("tipo no decimal: " + type(value).__name__)
    if not d.is_finite():
        raise NumericError("decimal no finito")
    if d == 0:
        return "0"
    s = format(d, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def to_float(value) -> float:
    """Convierte una cadena decimal canónica (o número) a float sin aceptar bool/no finitos."""
    if isinstance(value, bool):
        raise NumericError("bool no es número")
    x = float(value)
    if not math.isfinite(x):
        raise NumericError("no finito")
    return x


def brent(f, a: float, b: float, fa: float | None = None, fb: float | None = None,
          *, xtol: float = 0.0, rtol: float = 4.0 * 2.220446049250313e-16, maxiter: int = 400) -> float:
    """Raíz de f en [a,b] con f(a)·f(b) <= 0 (Brent-Dekker). Devuelve un extremo si f se anula allí."""
    fa = f(a) if fa is None else fa
    fb = f(b) if fb is None else fb
    if fa == 0.0:
        return a
    if fb == 0.0:
        return b
    if (fa > 0) == (fb > 0):
        raise NumericError("raíz no acotada")
    c, fc = a, fa
    d = e = b - a
    for _ in range(maxiter):
        if (fb > 0) == (fc > 0):
            c, fc = a, fa
            d = e = b - a
        if abs(fc) < abs(fb):
            a, b, c = b, c, b
            fa, fb, fc = fb, fc, fb
        tol = 2.0 * rtol * abs(b) + 0.5 * xtol
        m = 0.5 * (c - b)
        if abs(m) <= tol or fb == 0.0:
            return b
        if abs(e) >= tol and abs(fa) > abs(fb):
            s = fb / fa
            if a == c:
                p = 2.0 * m * s
                q = 1.0 - s
            else:
                q = fa / fc
                r = fb / fc
                p = s * (2.0 * m * q * (q - r) - (b - a) * (r - 1.0))
                q = (q - 1.0) * (r - 1.0) * (s - 1.0)
            if p > 0:
                q = -q
            else:
                p = -p
            if 2.0 * p < min(3.0 * m * q - abs(tol * q), abs(e * q)):
                e, d = d, p / q
            else:
                d = e = m
        else:
            d = e = m
        a, fa = b, fb
        b = b + d if abs(d) > tol else b + (tol if m > 0 else -tol)
        fb = f(b)
    return b


_GOLD = 0.3819660112501051


def golden_max(f, lo: float, hi: float, *, xtol: float = 1e-12, maxiter: int = 500):
    """Máximo local de f en [lo,hi] (Brent: sección áurea + parabólica). Devuelve (x, f(x))."""
    if hi < lo:
        raise NumericError("intervalo invertido")
    if hi == lo:
        return lo, f(lo)
    a, b = lo, hi
    x = w = v = a + _GOLD * (b - a)
    fx = fw = fv = -f(x)
    d = e = 0.0
    for _ in range(maxiter):
        m = 0.5 * (a + b)
        tol = xtol * abs(x) + 1e-15
        if abs(x - m) <= 2.0 * tol - 0.5 * (b - a):
            break
        if abs(e) > tol:
            r = (x - w) * (fx - fv)
            q = (x - v) * (fx - fw)
            p = (x - v) * q - (x - w) * r
            q = 2.0 * (q - r)
            if q > 0:
                p = -p
            q = abs(q)
            etemp = e
            e = d
            if abs(p) >= abs(0.5 * q * etemp) or p <= q * (a - x) or p >= q * (b - x):
                e = (a - x) if x >= m else (b - x)
                d = _GOLD * e
            else:
                d = p / q
                u = x + d
                if u - a < 2 * tol or b - u < 2 * tol:
                    d = tol if m - x >= 0 else -tol
        else:
            e = (a - x) if x >= m else (b - x)
            d = _GOLD * e
        u = x + d if abs(d) >= tol else x + (tol if d >= 0 else -tol)
        fu = -f(u)
        if fu <= fx:
            if u >= x:
                a = x
            else:
                b = x
            v, fv, w, fw, x, fx = w, fw, x, fx, u, fu
        else:
            if u < x:
                a = u
            else:
                b = u
            if fu <= fw or w == x:
                v, fv, w, fw = w, fw, u, fu
            elif fu <= fv or v == x or v == w:
                v, fv = u, fu
    return x, -fx
