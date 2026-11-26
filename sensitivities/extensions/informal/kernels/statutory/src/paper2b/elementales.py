"""Funciones elementales con cotas DEMOSTRADAS sin libm: exp, log, log1p, E(y) = expm1(y)/y, E'(y) y potencias.

Base de la garantía (única hipótesis de plataforma, comprobada al importar en PLATAFORMA):
  - aritmética IEEE 754 binary64 con redondeo al más cercano (par) en +, -, x y / (IEEE 754-2019 §4.3.1, §5.4.1);
  - operaciones exactas: comparaciones, math.frexp, math.ldexp (exacta si el resultado es normal), math.nextafter;
  - aritmética racional exacta (fractions.Fraction, enteros de precisión arbitraria) para las constantes.
Ninguna cota usa exp/log/pow/expm1/log1p de libm (su error no está documentado de forma aplicable).

Regla de redondeo dirigido: si r = fl(a o b) con redondeo al más cercano, el valor exacto está en
[nextafter(r, -inf), nextafter(r, +inf)] (el error no supera media separación entre r y su vecino hacia el valor exacto).
Desbordamiento: una cota inferior +inf proviene de un valor exacto finito mayor que DBL_MAX, así que se reemplaza por
DBL_MAX (y -inf superior por -DBL_MAX): nunca se asigna un límite infinito del lado que excluiría el valor.

Métodos (detalle y demostración en review/FUNDAMENTO_COTAS.md de la entrega):
  exp(x):  x = k ln2 + j/64 + s con ln2 en dos partes (C1 de 32 bits: k*C1 exacto) y error de ln2 acotado;
           exp(s), |s| < 0.0099, por Taylor de grado 7 evaluado con Horner por intervalos + resto de Lagrange;
           exp(j/64) de una tabla de encierros racionales; escala por 2^k con ldexp (exacto salvo sub/desbordamiento).
  log(x):  x = m 2^e, m en [sqrt(1/2), sqrt(2)); m = c (1 + ...) con c = j/64 de tabla; log m = log c + 2 atanh(s),
           s = (m - c)/(m + c) (m - c exacto por Sterbenz), atanh por serie con resto acotado; + e ln2.
  log1p(z): 1 + z = w + err EXACTO (TwoSum de Knuth); log1p(z) = log w + log1p(err/w) con log1p(d) en [d - d^2, d].
  E, E':   series con resto acotado para |y| <= 1/2; fórmulas por exp para |y| > 1/2 (y > 700: forma e^(y - log y) para
           no desbordar antes que el valor).
Todas las funciones son monótonas crecientes (E y E' incluidas: E es convexa), así que un intervalo se encierra con las
cotas en sus extremos.
"""
from __future__ import annotations

import math
import sys
from fractions import Fraction as Fr

INF = math.inf
DMAX = sys.float_info.max
TINY = 5e-324                                   # 2^-1074
NORMAL_MIN = sys.float_info.min                 # 2^-1022


# ============================================================================================ plataforma
def _plataforma() -> dict:
    fi = sys.float_info
    h = 2.0 ** -53
    checks = {
        "binary64": fi.mant_dig == 53 and fi.radix == 2 and fi.max_exp == 1024 and fi.min_exp == -1021,
        "redondeo_al_mas_cercano_par": ((1.0 + h) == 1.0 and (1.0 + 2 * h) + h == 1.0 + 4 * h
                                        and (1.0 + h * (1.0 + 2.0 ** -10)) == 1.0 + 2 * h and -(1.0 + h) == -1.0
                                        and (1.0 + 2.0 ** -30) * (1.0 + 2.0 ** -30) == 1.0 + 2.0 ** -29),
        "division_correcta": abs(Fr(1.0 / 3.0) - Fr(1, 3)) <= Fr(1, 2 ** 55) and Fr(2.0 / 3.0) != Fr(2, 3),
        "subnormales": TINY > 0.0 and TINY / 2.0 == 0.0 and TINY * 3.0 == 3 * TINY,
        "nextafter": hasattr(math, "nextafter") and math.nextafter(1.0, INF) == 1.0 + 2.0 ** -52,
    }
    return {"garantia": "ieee754_binary64_rn" if all(checks.values()) else None, "controles": checks}


PLATAFORMA = _plataforma()
GARANTIA = PLATAFORMA["garantia"]


class PlataformaNoConforme(RuntimeError):
    """La plataforma no superó los controles IEEE 754: no hay cotas demostradas disponibles."""


def exigir_plataforma() -> None:
    if GARANTIA is None:
        raise PlataformaNoConforme(str(PLATAFORMA["controles"]))


# ============================================================================================ redondeo dirigido
def dn(x: float) -> float:
    if x == INF:
        return DMAX
    if x == -INF:
        return x
    return math.nextafter(x, -INF)


def up(x: float) -> float:
    if x == -INF:
        return -DMAX
    if x == INF:
        return x
    return math.nextafter(x, INF)


def _fr_dn(q: Fr) -> float:
    f = float(q)
    while Fr(f) > q:
        f = math.nextafter(f, -INF)
    return f


def _fr_up(q: Fr) -> float:
    f = float(q)
    while Fr(f) < q:
        f = math.nextafter(f, INF)
    return f


def _mul(a: tuple, b: tuple) -> tuple:
    """Producto de intervalos (lo, hi) con redondeo hacia afuera; 0 * inf = 0 (factor exactamente nulo)."""
    def m(x, y):
        return 0.0 if x == 0.0 or y == 0.0 else x * y
    ps = (m(a[0], b[0]), m(a[0], b[1]), m(a[1], b[0]), m(a[1], b[1]))
    return dn(min(ps)), up(max(ps))


def _div(a: tuple, b: tuple) -> tuple:
    """a / b con b sin cero: 1/b en [1/b.hi, 1/b.lo] (vale para ambos signos; 1/inf = 0)."""
    if b[0] <= 0.0 <= b[1]:
        raise ZeroDivisionError("divisor que contiene cero")
    return _mul(a, (dn(1.0 / b[1]), up(1.0 / b[0])))


def _horner_pos(s: float, coefs: list) -> tuple:
    """Encierro de sum c_i s^i (coefs[i] = (lo, hi), grado creciente) en el punto s por Horner con redondeo hacia afuera.
    Requiere sumas parciales positivas (se verifica)."""
    qlo, qhi = coefs[-1]
    for clo, chi in reversed(coefs[:-1]):
        if s >= 0.0:
            plo, phi = s * qlo, s * qhi
        else:
            plo, phi = s * qhi, s * qlo
        qlo, qhi = dn(dn(plo) + clo), up(up(phi) + chi)
        if not qlo > 0.0:
            raise ArithmeticError("Horner: suma parcial no positiva fuera del rango previsto")
    return qlo, qhi


# ============================================================================================ constantes racionales
def _ln2() -> tuple:
    """ln 2 = sum_{k>=1} 1/(k 2^k); resto tras N términos < 1/((N+1) 2^N)."""
    n, s, p = 160, Fr(0), Fr(1)
    for k in range(1, n + 1):
        p /= 2
        s += p / k
    return s, s + Fr(1, (n + 1) * 2 ** n)


def _exp_q(q: Fr, terms: int = 32) -> tuple:
    """exp(q) racional para |q| < 1: suma de Taylor + resto |t| (terms+1)/(terms+1-|q|) (serie geométrica mayorante)."""
    s, t = Fr(0), Fr(1)
    for i in range(terms):
        s += t
        t = t * q / (i + 1)
    rem = abs(t) * Fr(terms + 1) / (Fr(terms + 1) - abs(q))
    return s - rem, s + rem


def _log_q(c: Fr, terms: int = 30) -> tuple:
    """log(c) = 2 atanh(s), s = (c - 1)/(c + 1), |s| < 1/2; resto |s|^(2K+1)/((2K+1)(1 - s^2))."""
    s = (c - 1) / (c + 1)
    acc, p = Fr(0), s
    for k in range(terms):
        acc += p / (2 * k + 1)
        p *= s * s
    rem = abs(p) / ((2 * terms + 1) * (1 - s * s))
    return 2 * (acc - rem), 2 * (acc + rem)


_L2LO, _L2HI = _ln2()
C1 = float(Fr(math.floor(_L2LO * 2 ** 32), 2 ** 32))            # 32 bits significativos: k*C1 exacto para |k| < 2^21
C2 = float(_L2LO - Fr(C1))
EPS_LN2 = _fr_up(max(abs(_L2LO - Fr(C1) - Fr(C2)), abs(_L2HI - Fr(C1) - Fr(C2))))
assert Fr(C1) == Fr(math.floor(_L2LO * 2 ** 32), 2 ** 32)

_EXP_T = {}
for _j in range(-24, 25):
    _lo, _hi = _exp_q(Fr(_j, 64))
    _EXP_T[_j] = (_fr_dn(_lo), _fr_up(_hi))
_LOG_T = {}
for _j in range(45, 92):
    if _j == 64:
        _LOG_T[_j] = (0.0, 0.0)
    else:
        _lo, _hi = _log_q(Fr(_j, 64))
        _LOG_T[_j] = (_fr_dn(_lo), _fr_up(_hi))


def _coef(q: Fr) -> tuple:
    return _fr_dn(q), _fr_up(q)


_EXP_C = [_coef(Fr(1, math.factorial(i))) for i in range(8)]                   # grado 7
_S_MAX = Fr(1, 100)                                                           # |s| <= 1/128 + redondeo < 0.0099 (se verifica)
_S_GUARD = 0.0099                                                             # float(0.0099) < 1/100
_EXP_REM = _fr_up(_S_MAX ** 8 / math.factorial(8) * Fr(10101, 10000))         # e^(1/100) < 1.0101
_ATANH_C = [_coef(Fr(1, 2 * k + 1)) for k in range(4)]                        # 1 + w/3 + w^2/5 + w^3/7
_E_N = 18
_E_C = [_coef(Fr(1, math.factorial(k + 1))) for k in range(_E_N + 1)]          # E(y) = sum y^k/(k+1)!
_E_REM = _fr_up(Fr(1, 2) ** (_E_N + 1) / math.factorial(_E_N + 2) / (1 - Fr(1, 2) / (_E_N + 3)))
_EP_C = [_coef(Fr(k + 1, math.factorial(k + 2))) for k in range(_E_N + 1)]     # E'(y) = sum (k+1) y^k/(k+2)!
_EP_REM = _fr_up(Fr(_E_N + 2) * Fr(1, 2) ** (_E_N + 1) / math.factorial(_E_N + 3) / (1 - Fr(1, 2)))
LN_DMAX_LO = 709.78                          # log(DBL_MAX) > 709.78 (DBL_MAX > 2^1023.99)
_EXP_OVER = 709.79                           # 709.79 > 1024 ln 2 > log(DBL_MAX): exp(x) > DBL_MAX
_EXP_UNDER = -745.2                          # -745.2 < -1075 ln 2: exp(x) < 2^-1075 < TINY


# ============================================================================================ escalado por 2^k
def _ldexp_dn(v: float, k: int) -> float:
    try:
        r = math.ldexp(v, k)
    except OverflowError:
        return DMAX
    if r == INF:
        return DMAX
    if abs(r) < NORMAL_MIN:                   # subnormal: ldexp redondea
        r = math.nextafter(r, -INF)
    return r


def _ldexp_up(v: float, k: int) -> float:
    try:
        r = math.ldexp(v, k)
    except OverflowError:
        return INF
    if abs(r) < NORMAL_MIN:
        r = math.nextafter(r, INF)
    return r


# ============================================================================================ exp
_CACHE_EXP: dict = {}
_CACHE_LOG: dict = {}
_CACHE_MAX = 400000


def exp_bounds(x: float) -> tuple:
    c = _CACHE_EXP.get(x)
    if c is None:
        c = _exp_bounds(x)
        if len(_CACHE_EXP) > _CACHE_MAX:
            _CACHE_EXP.clear()
        _CACHE_EXP[x] = c
    return c


def _exp_bounds(x: float) -> tuple:
    if x != x:
        raise ValueError("exp de NaN")
    if x >= _EXP_OVER:
        return DMAX, INF
    if x <= _EXP_UNDER:
        return 0.0, TINY
    if x == 0.0:
        return 1.0, 1.0
    k = int(round(x * 1.4426950408889634))            # cualquier entero sirve: solo decide el tamaño de s
    t = x - k * C1                                    # k*C1 exacto; la resta se redondea -> se acota
    tlo, thi = dn(t), up(t)
    p = k * C2
    plo, phi = dn(p), up(p)
    ke = up(abs(k) * EPS_LN2)
    rlo = dn(dn(tlo - phi) - ke)
    rhi = up(up(thi - plo) + ke)
    j = max(-24, min(24, int(round((rlo + rhi) * 32.0))))
    q = j / 64.0                                      # exacto
    slo, shi = dn(rlo - q), up(rhi - q)
    if not (-_S_GUARD < slo <= shi < _S_GUARD):
        raise ArithmeticError("exp: reducción fuera del rango demostrado")
    elo = dn(_horner_pos(slo, _EXP_C)[0] - _EXP_REM)
    ehi = up(_horner_pos(shi, _EXP_C)[1] + _EXP_REM)
    tl, th = _EXP_T[j]
    lo, hi = dn(tl * elo), up(th * ehi)
    return max(0.0, _ldexp_dn(lo, k)), _ldexp_up(hi, k)


# ============================================================================================ log, log1p
def _atanh_bounds(s: float) -> tuple:
    a = abs(s)
    if a == 0.0:
        return 0.0, 0.0
    wlo, whi = max(0.0, dn(a * a)), up(a * a)
    plo, phi = _horner_pos(wlo, _ATANH_C)[0], _horner_pos(whi, _ATANH_C)[1]
    t = a
    for _ in range(8):
        t = up(t * a)
    tail = up(t / dn(9.0 * dn(1.0 - whi)))          # |s|^9 / (9 (1 - s^2)) mayora el resto de la serie
    base_lo, base_hi = dn(a * plo), up(a * phi)
    if s > 0.0:
        return base_lo, up(base_hi + tail)
    return -up(base_hi + tail), -base_lo


def log_bounds(x: float) -> tuple:
    c = _CACHE_LOG.get(x)
    if c is None:
        c = _log_bounds(x)
        if len(_CACHE_LOG) > _CACHE_MAX:
            _CACHE_LOG.clear()
        _CACHE_LOG[x] = c
    return c


def _log_bounds(x: float) -> tuple:
    if not x > 0.0:
        raise ValueError("log de un número no positivo")
    if x == INF:
        return LN_DMAX_LO, INF
    m, e = math.frexp(x)                              # x = m 2^e, m en [1/2, 1): exacto
    m, e = m * 2.0, e - 1                             # [1, 2)
    if m > 1.4142135623730951:
        m, e = m * 0.5, e + 1                         # [sqrt(1/2), sqrt(2))
    j = int(round(m * 64.0))
    c = j / 64.0
    num = m - c                                       # exacto (Sterbenz: c/2 <= m <= 2c)
    if num == 0.0:
        alo = ahi = 0.0
    else:
        den = m + c
        dlo, dhi = dn(den), up(den)
        if num > 0.0:
            slo, shi = dn(num / dhi), up(num / dlo)
        else:
            slo, shi = dn(num / dlo), up(num / dhi)
        alo, ahi = _atanh_bounds(slo)[0], _atanh_bounds(shi)[1]
    tl, th = _LOG_T[j]
    llo, lhi = dn(tl + 2.0 * alo), up(th + 2.0 * ahi)
    if e == 0:
        return llo, lhi
    p1 = e * C1                                       # exacto
    p2 = e * C2
    ee = up(abs(e) * EPS_LN2)
    elo = dn(dn(p1 + dn(p2)) - ee)
    ehi = up(up(p1 + up(p2)) + ee)
    return dn(elo + llo), up(ehi + lhi)


def log1p_bounds(z: float) -> tuple:
    """log(1 + z), z > -1."""
    if not z > -1.0:
        raise ValueError("log1p fuera de dominio")
    if z == 0.0:
        return 0.0, 0.0
    w = 1.0 + z
    bb = w - 1.0
    err = (1.0 - (w - bb)) + (z - bb)                 # TwoSum: 1 + z = w + err EXACTAMENTE
    L = log_bounds(w)
    if err == 0.0:
        return L
    d = err / w
    dlo, dhi = dn(d), up(d)
    da = max(abs(dlo), abs(dhi))
    return dn(L[0] + dn(dlo - up(da * da))), up(L[1] + dhi)   # d - d^2 <= log1p(d) <= d para |d| <= 1/2


# ============================================================================================ E, E'
def E_bounds(y: float) -> tuple:
    """E(y) = expm1(y)/y (E(0) = 1)."""
    if y != y:
        raise ValueError("E de NaN")
    if abs(y) <= 0.5:
        lo, hi = _horner_pos(y, _E_C)
        return dn(lo - _E_REM), up(hi + _E_REM)
    if y > 700.0:                                     # e^y / y (1 - e^-y) sin desbordar antes que el valor
        ly = log_bounds(y)
        alo, ahi = dn(y - ly[1]), up(y - ly[0])
        ea = (exp_bounds(alo)[0], exp_bounds(ahi)[1])
        em = exp_bounds(-y)
        return _mul(ea, (dn(1.0 - em[1]), 1.0))
    ex = exp_bounds(y)
    num = (dn(ex[0] - 1.0), up(ex[1] - 1.0))
    if y > 0.0:
        return dn(num[0] / y), up(num[1] / y)
    return dn(num[1] / y), up(num[0] / y)


def Ep_bounds(y: float) -> tuple:
    """E'(y) = (y e^y - expm1(y))/y^2 = sum_{k>=0} (k+1) y^k/(k+2)!."""
    if y != y:
        raise ValueError("E' de NaN")
    if abs(y) <= 0.5:
        lo, hi = _horner_pos(y, _EP_C)
        return dn(lo - _EP_REM), up(hi + _EP_REM)
    em1 = (dn(y - 1.0), up(y - 1.0))
    if y > 700.0:                                     # e^(y - 2 log y) (y - 1 + e^-y)
        ly = log_bounds(y)
        alo, ahi = dn(y - 2.0 * ly[1]), up(y - 2.0 * ly[0])
        ea = (exp_bounds(alo)[0], exp_bounds(ahi)[1])
        em = exp_bounds(-y)
        return _mul(ea, (dn(em1[0] + em[0]), up(em1[1] + em[1])))
    ex = exp_bounds(y)
    prod = _mul(ex, em1)
    num = (dn(prod[0] + 1.0), up(prod[1] + 1.0))
    y2 = (dn(y * y), up(y * y))
    return _div(num, y2)


# ============================================================================================ potencias
_CACHE_POW: dict = {}


def pow_range(u: float, qlo: float, qhi: float) -> tuple:
    """[min, max] DEMOSTRADOS de u^q para todo q en [qlo, qhi] (u > 0): u^q = exp(q log u) con q log u encerrado."""
    key = (u, qlo, qhi)
    c = _CACHE_POW.get(key)
    if c is not None:
        return c
    if not u > 0.0:
        raise ValueError("potencia de base no positiva")
    if u == 1.0 or (qlo == 0.0 and qhi == 0.0):
        c = (1.0, 1.0)
    else:
        L = log_bounds(u)
        ps = [0.0 if (q == 0.0 or l == 0.0) else q * l for q in (qlo, qhi) for l in L]
        c = (exp_bounds(dn(min(ps)))[0], exp_bounds(up(max(ps)))[1])
    if len(_CACHE_POW) > _CACHE_MAX:
        _CACHE_POW.clear()
    _CACHE_POW[key] = c
    return c


def pow_bounds(u: float, p: float) -> tuple:
    """u^p para u > 0 (u y p números de coma flotante)."""
    if not u > 0.0:
        raise ValueError("potencia de base no positiva")
    if p == 0.0 or u == 1.0:
        return 1.0, 1.0
    if p == 1.0:
        return u, u
    L = log_bounds(u)
    if p > 0.0:
        a = (dn(p * L[0]), up(p * L[1]))
    else:
        a = (dn(p * L[1]), up(p * L[0]))
    return exp_bounds(a[0])[0], exp_bounds(a[1])[1]

assert Fr(_S_GUARD) < _S_MAX
