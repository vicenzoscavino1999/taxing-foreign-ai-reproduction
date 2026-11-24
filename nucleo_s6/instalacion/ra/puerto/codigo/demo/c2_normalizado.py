"""Encierro NORMALIZADO de C2 = sup R / B_pot (MEJORAS DE CÁLCULO 3.7, NO OFICIAL). Fundamento: review/FUNDAMENTO_C2_NORMALIZADO.md.

Idea. En paper2b.encierros_modelo, R(tau; theta) es una combinación de integrales contra la medida de Pareto
dF_theta(z) = a z_m^a z^(-a-1) dz (momentos `moment`, momentos orientados `_omoment` y la densidad `density` de los
términos de Leibniz y de salto), con coeficientes que NO contienen la constante de normalización
mu(theta) = a z_m / (a - 1), y B_pot = gamma mu (IParams.B_pot). El método actual encierra sup_tau R sobre la caja de
theta y divide por el encierro de B_pot: a/(a-1) aparece en el numerador (dentro de cada momento, como
a/(a-m)) y en el denominador como intervalos INDEPENDIENTES, y z_m^m frente a z_m también.

Reformulación algebraicamente equivalente: integrar contra la medida normalizada dF_theta / mu(theta). Para cada
theta fijo, mu(theta) > 0 no depende de tau, de modo que
    C2(theta) = sup_tau R(tau; theta) / (gamma mu(theta)) = (1/gamma) sup_tau Rn(tau; theta),
    Rn = R / mu = la MISMA combinación con cada integral dividida por mu(theta).
Las tres funciones se sustituyen por su versión dividida por mu, con la cancelación hecha a mano (exacta):
    moment_n(m)  = c_n(m) [ (lo/z_m)^(m-a) - (hi/z_m)^(m-a) ],  c_n(m) = (a-1)/(a-m) z_m^(m-1)
    (original:     c(m)   = a/(a-m) z_m^m;  c(m)/mu = (a-1)/(a-m) z_m^(m-1))
    c_n(1) = 1 EXACTAMENTE (no se evalúa (a-1)/(a-1) por intervalos);
    c_n(rho) = q(a, rho) z_m^(rho-1), q(a, rho) = (a-1)/(a-rho), con q creciente en a (dq/da = (1-rho)/(a-rho)^2 >= 0
    si rho <= 1) y en rho (dq/drho = (a-1)/(a-rho)^2 > 0 si a > 1): si a.lo > 1, rho.hi <= 1 y a.lo > rho.hi, el rango
    exacto es [q(a.lo, rho.lo), q(a.hi, rho.hi)] (vértices con redondeo hacia afuera); si no, se usa el cociente por
    intervalos (válido, más ancho);
    _omoment_n(m, C) = c_n(m) [1 - (C/z_m)^(m-a)];
    density_n(Z) = (a-1) z_m^(a-1) Z^(-a-1)   (= a z_m^a Z^(-a-1) / mu).
Todo lo demás (regímenes, particiones, cotas universales, ramas de pliegue, signos de salto, formas de valor medio
y la rama y cota de sup_bound) es el código ORIGINAL sin cambios (subclase). Los signos (saltos J, regímenes) no
dependen de la escala positiva. Requisitos: gamma y z_m puntuales (fijos) y a.lo > 1 (mu > 0); si no, se devuelve
el encierro original.
"""
from __future__ import annotations

import math
import time

from paper2b import encierros_modelo as EM
from paper2b.intervalos import Iv
from paper2b.supremum import axes

ONE = Iv(1.0, 1.0)


class MotorNormalizado(EM.Engine):
    """Engine que integra contra dF/mu: R_normalizado = R / mu en cada theta de la caja."""

    def _cn(self, m: Iv) -> Iv:
        P = self.P
        if m.lo == m.hi == 1.0:
            return ONE                                    # (a-1)/(a-1) z_m^0 = 1 exacto
        a = P.a
        if a.lo > 1.0 and m.hi <= 1.0 and a.lo > m.hi:
            qlo = ((Iv.point(a.lo) - 1.0) / (Iv.point(a.lo) - Iv.point(m.lo))).lo
            qhi = ((Iv.point(a.hi) - 1.0) / (Iv.point(a.hi) - Iv.point(m.hi))).hi
            q = Iv(qlo, qhi)
        else:
            q = (a - 1.0) / (a - m)
        return q * EM.ipow(P.z_m, m - 1.0)

    def moment(self, m: Iv, Zlo: Iv, Zhi: Iv) -> Iv:
        P = self.P
        cn = self._cn(m)

        def F(lo: float, hi: float) -> Iv:
            k = m - P.a
            tlo = EM.iexp(k * EM.ilog(Iv.point(lo) / P.z_m))
            thi = EM.ZERO if not math.isfinite(hi) else EM.iexp(k * EM.ilog(Iv.point(hi) / P.z_m))
            return cn * (tlo - thi)
        small = F(Zlo.hi, Zhi.lo) if Zhi.lo > Zlo.hi else EM.ZERO
        big = F(max(Zlo.lo, P.z_m.lo), Zhi.hi)
        return Iv(max(0.0, min(small.lo, big.hi)), max(0.0, big.hi))

    def _omoment(self, m: Iv, C: Iv) -> Iv:
        P = self.P
        k = m - P.a
        return self._cn(m) * (1.0 - EM.iexp(k * EM.ilog(C / P.z_m)))

    def density(self, Z: Iv) -> Iv:
        P = self.P
        return (P.a - 1.0) * EM.ipow(P.z_m, P.a - 1.0) * EM.ipow(Z, -(P.a + 1.0))


def aplicable(P: EM.IParams) -> bool:
    return P.gamma.lo == P.gamma.hi and P.z_m.lo == P.z_m.hi and P.a.lo > 1.0 and P.gamma.lo > 0.0


def c2_normalizado(model, box: dict, design, j, bd, bf, fixed=None, stats: dict | None = None):
    """Mismo contrato que ModeloTeorico.c2_struct_enclosure (misma tolerancia en unidades de C2, mismo tope de cajas)."""
    if fixed is None or not model.certified:
        return None
    t0 = time.time()
    P = EM.IParams.from_primitive_box(box, fixed)
    if not aplicable(P):
        if stats is not None:
            stats["normalizado"] = False
        return model.c2_struct_enclosure(box, design, j, bd, bf, fixed=fixed)
    eng = MotorNormalizado(P, design)
    (dl, dh), (fl, fh) = axes(j, bd, bf)
    c0, _ = eng.R(Iv.point(0.5 * (dl + dh)), Iv.point(0.5 * (fl + fh)))
    # original: tol = max(struct_tol * B_pot.lo, ancho(c0)) en unidades de R; aquí en unidades de R/mu (B_pot/mu = gamma)
    tol = max(model.struct_tol * P.gamma.lo, c0.hi - c0.lo)
    sb = EM.sup_bound(eng, j, bd, bf, tol=tol, max_boxes=model.struct_max_boxes, jump_budget=0)
    out = Iv(sb.lower, max(sb.lower, sb.upper)) / P.gamma
    if stats is not None:
        stats.update(normalizado=True, evaluaciones=eng.evaluations, segundos=round(time.time() - t0, 3))
    return out


def c2_original_con_estadisticas(model, box, design, j, bd, bf, fixed=None, stats: dict | None = None):
    """Réplica instrumentada de ModeloTeorico.c2_struct_enclosure (mismas operaciones) para contar evaluaciones de R."""
    if fixed is None or not model.certified:
        return None
    t0 = time.time()
    P = EM.IParams.from_primitive_box(box, fixed)
    eng = EM.Engine(P, design)
    (dl, dh), (fl, fh) = axes(j, bd, bf)
    c0, _ = eng.R(Iv.point(0.5 * (dl + dh)), Iv.point(0.5 * (fl + fh)))
    tol = max(model.struct_tol * P.B_pot.lo, c0.hi - c0.lo)
    sb = EM.sup_bound(eng, j, bd, bf, tol=tol, max_boxes=model.struct_max_boxes, jump_budget=0)
    out = Iv(sb.lower, max(sb.lower, sb.upper)) / P.B_pot
    if stats is not None:
        stats.update(normalizado=False, evaluaciones=eng.evaluations, segundos=round(time.time() - t0, 3))
    return out
