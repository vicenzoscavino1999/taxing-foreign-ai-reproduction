"""Ínfimos de C2 en df: TECHO CERTIFICADO v3 en un punto θ0 con ρ <= 1 cualquiera (CIERRE INF DF Y PASO 4 3.7, NO OFICIAL).
Módulo nuevo; sustituye como candidato a inf_df_techo_general (que se conserva sin cambios). Fundamento:
review/FUNDAMENTO_INFIMOS_DF.md §2.

Hipótesis (todas comprobadas en el código o demostradas en el fundamento): z_m = 1 (fijo del plan), θ = 1 + u_θ(a − 1) > 1,
ρ <= 1, a > 1, τ_d, τ_f >= 0, t̃_d, t̃_f >= 0 (crecientes en su τ), κ̃ <= 0,2 (k_F/γ <= 0,534 < 1).

Rn = τ_d (E0 + r* A) + τ_f q* κ0 g_f W  (motor normalizado: integrales contra dF/μ). Con:
  (a) E0 <= 0 (lema E0: el régimen final F exige F1-I1 >= 0, que implica el estado previo F);
  (b) A y W integran solo sobre el conjunto final F ⊆ {z >= 1 : F1-I1(z) >= 0} (_regime: F exige F1-I1 >= 0);
  (c) F1-I1(z)/z = h(z) = δ z^(θ−1) − b + C z^(ρ−1), b = tb + t̃_d γ >= 0, C = −φ κ0 t̃_f <= 0 (G) o
      C = κ0 [t̃_d − φ t̃_f (1 − t̃_d)] (N, forma factorizada idéntica a κ0 − (1 − t̃_d) k_F);
      para z >= 1: h(z) <= H(z) = δ z^(θ−1) − b + C⁻ z^(ρ−1) + C⁺, con C⁻ = min(C, 0), C⁺ = max(C, 0);
      H es NO DECRECIENTE en z (θ − 1 > 0; C⁻ z^(ρ−1) crece hacia 0 si ρ <= 1). Si H(z1) < 0 (demostrado por intervalos
      para todo τ de la caja), entonces h < 0 en [1, z1] y F ⊆ (z1, ∞): z* = max(1, z1);
  (d) en z >= 1 los integrandos son >= 0 (G: γ z; N: γ z − k_F z^ρ >= γ z (1 − k_F/γ) > 0; W: z^ρ), así que
      A <= γ M1(z*) − [N] k_F Mρ(z*),  W <= Mρ(z*),  M1(z) = z^(1−a),  Mρ(z) = q z^(ρ−a),  q = (a − 1)/(a − ρ);
  (e) r*, q*, g_f, κ0 >= 0.
Por tanto Rn(τ; θ0) <= U(τ) = τ_d r* (γ M1(z*) − [N] k_F Mρ(z*)) + τ_f q* κ0 g_f Mρ(z*), y sobre una caja de τ el
encierro por intervalos (redondeo hacia afuera) de esa expresión, con z* demostrado para TODA la caja, es una cota
superior. C2(θ0) = sup_τ Rn/γ <= max de las cotas de las cajas vivas de una rama y cota en τ. Es una cota SUPERIOR de
C2(θ0) y por tanto del ínfimo (θ0 admisible, comprobado con cobertura.box_admissible).

Rama y cota en τ: mejor primero; τ_d se parte primero en escala geométrica (el máximo vive en τ_d ~ δ/β); en cada
caja se elige el eje cuyo corte baja más la mayor cota de las hijas (se prueban los dos). La holgura del techo se
mide contra la cota inferior CERTIFICADA del motor normalizado en el mejor τ del punto (encierro puntual, .lo).
"""
from __future__ import annotations

import heapq
import math
import time

from paper2b import encierros_modelo as EM
from paper2b.intervalos import Iv

ZERO = Iv(0.0, 0.0)


def _zpow(z: float, e: Iv) -> Iv:
    """z^e para z >= 1 puntual y exponente intervalo, con redondeo hacia afuera."""
    if z == 1.0:
        return Iv(1.0, 1.0)
    return EM.iexp(EM.ilog(Iv(z, z)) * e)


class Techo:
    def __init__(self, P: EM.IParams, dis: str):
        if not (P.z_m.lo == P.z_m.hi == 1.0):
            raise ValueError("Z_M_DISTINTO_DE_1")
        if not (P.theta.lo > 1.0 and P.rho.hi <= 1.0 and P.a.lo > 1.0 and P.a.lo > P.rho.hi):
            raise ValueError("HIPOTESIS_THETA_RHO_A")
        self.P, self.dis = P, dis
        self.th1, self.rh1 = P.theta - 1.0, P.rho - 1.0
        self.q = (P.a - 1.0) / (P.a - P.rho)
        self.evaluaciones = 0

    def _coef(self, Td: Iv, Tf: Iv):
        P = self.P
        x = EM.tax_side(P, EM.AD(Td), EM.AD(Tf), EM.AD(P.phi))
        g, k0 = P.gamma, P.kappa0
        # t̃_d = −l_d E((1+η_d) l_d) >= 0 y t̃_f = τ_f e^(α l_f) + (−l_f) η_f [E(α l_f) − E((α+1) l_f)] >= 0 para τ >= 0
        # (l <= 0, E > 0 creciente): se intersecta el encierro con [0, ∞) (en τ = 0 el redondeo hacia afuera da lo < 0)
        tdv, tfv = x.td.v, x.tf.v
        if not (tdv.hi >= 0.0 and tfv.hi >= 0.0):
            raise ValueError("TILDE_NEGATIVO")
        tdv, tfv = Iv(max(tdv.lo, 0.0), tdv.hi), Iv(max(tfv.lo, 0.0), tfv.hi)
        kF = x.kF.v
        if not (kF / g).hi < 1.0:
            raise ValueError("KF_SOBRE_GAMMA")
        b = Td * P.beta + tdv * g
        C = (-(P.phi * k0 * tfv)) if self.dis == "G" else (k0 * (tdv - P.phi * tfv * (1.0 - tdv)))
        return x, b, C, kF

    def _H_hi(self, z: float, b: Iv, C: Iv) -> float:
        P = self.P
        Cm = Iv(min(C.lo, 0.0), min(C.hi, 0.0))
        Cp = max(C.hi, 0.0)
        H = P.delta * _zpow(z, self.th1) - b + Cm * _zpow(z, self.rh1) + Iv(Cp, Cp)
        return H.hi

    def zstar(self, b: Iv, C: Iv, n_bis=48) -> float:
        """z* >= 1 con H(z*) < 0 demostrado (o 1): todo z del conjunto F de toda la caja cumple z > z* (o z >= 1)."""
        if not self._H_hi(1.0, b, C) < 0.0:
            return 1.0
        lo, hi = 1.0, 2.0
        while self._H_hi(hi, b, C) < 0.0:
            lo, hi = hi, hi * 2.0
            if hi > 1e300:
                return lo
        for _ in range(n_bis):
            m = math.sqrt(lo * hi)
            if m <= lo or m >= hi:
                break
            if self._H_hi(m, b, C) < 0.0:
                lo = m
            else:
                hi = m
        return lo

    def U(self, Td: Iv, Tf: Iv) -> tuple[float, float]:
        """(cota superior de Rn sobre la caja de τ, z* usado)."""
        self.evaluaciones += 1
        P = self.P
        x, b, C, kF = self._coef(Td, Tf)
        z = self.zstar(b, C)
        M1 = _zpow(z, 1.0 - P.a)
        Mr = self.q * _zpow(z, P.rho - P.a)
        A = P.gamma * M1 - (kF * Mr if self.dis == "N" else ZERO)
        val = Td * x.rstar.v * A + Tf * x.qstar.v * P.kappa0 * x.gf.v * Mr
        return max(0.0, val.hi), z


def techo(th_pt: dict, fixed: dict, dis: str, bd: float, bf: float, tol: float = 2e-7, max_cajas: int = 60000,
          tope_s: float = 600.0):
    """Cota superior certificada de C2(θ0) por rama y cota en τ ∈ [0, bd] x [0, bf] con Techo.U."""
    t0 = time.time()
    P = EM.IParams.from_primitive_box({p: (v, v) for p, v in th_pt.items()}, fixed)
    T = Techo(P, dis)
    gam = P.gamma.lo

    def u(d0, d1, f0, f1):
        return T.U(Iv(d0, d1), Iv(f0, f1))[0]
    # partición inicial: τ_d en escala geométrica (0, bd·10^-9, ..., bd) x τ_f en 8 tramos
    cortes_d = [0.0] + [bd * 10.0 ** (-k / 4.0) for k in range(36, -1, -1)]
    cortes_f = [bf * i / 8 for i in range(9)]
    heap, cont, best_pt, best_tau = [], 0, 0.0, (0.0, 0.0)
    for i in range(len(cortes_d) - 1):
        for k in range(len(cortes_f) - 1):
            b = (cortes_d[i], cortes_d[i + 1], cortes_f[k], cortes_f[k + 1])
            heapq.heappush(heap, (-u(*b), cont, b))
            cont += 1
    n = 0

    def punto(d, f):
        nonlocal best_pt, best_tau
        v = u(d, d, f, f)
        if v > best_pt:
            best_pt, best_tau = v, (d, f)
    for (_, _, b) in list(heap):
        punto(b[0] + (b[1] - b[0]) / 2, b[2] + (b[3] - b[2]) / 2)
    estado = "tope_cajas"
    while heap:
        if -heap[0][0] - best_pt <= tol * gam:
            estado = "convergido"
            break
        if n >= max_cajas or time.time() - t0 > tope_s:
            estado = "tope_cajas" if n >= max_cajas else "tope_tiempo"
            break
        nu, _, b = heapq.heappop(heap)
        n += 1
        d0, d1, f0, f1 = b
        md = math.sqrt(d0 * d1) if d0 > 0.0 and d1 / d0 > 1.5 else d0 + (d1 - d0) / 2
        mf = f0 + (f1 - f0) / 2
        opc = []
        for hijos in (((d0, md, f0, f1), (md, d1, f0, f1)), ((d0, d1, f0, mf), (d0, d1, mf, f1))):
            us = [min(u(*h), -nu) for h in hijos]
            opc.append((max(us), hijos, us))
        _, hijos, us = min(opc, key=lambda o: o[0])
        for h, uh in zip(hijos, us):
            punto(h[0] + (h[1] - h[0]) / 2, h[2] + (h[3] - h[2]) / 2)
            if uh > best_pt:
                heapq.heappush(heap, (-uh, cont, h))
                cont += 1
    U = max(-heap[0][0], best_pt) if heap else best_pt
    return {"U_C2": (Iv(U, U) / P.gamma).hi, "sup_puntos_U": best_pt / gam, "tau_sup_puntos": list(best_tau), "cajas": n, "vivas": len(heap),
            "evaluaciones": T.evaluaciones, "estado": estado, "segundos": round(time.time() - t0, 2)}
