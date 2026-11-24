"""Cota inferior de C2 (y de G = C2 − k(1 − s)) que ADMITE EMPRESAS INFORMALES: «cota de un umbral» (CIERRE G DF 3.7,
NO OFICIAL). Fundamento: review/FUNDAMENTO_G_DF.md §2.

VERSIÓN v2 (cota_un_umbral.py se conserva: la usó DUU): única diferencia, el crecimiento δ z^(θ−1) del umbral se encierra
como γ·exp((θ − 1)(ln z − ln z_cost)) (z_m = 1: δ = z_cost^(1−θ) γ, identidad exacta), con UNA aparición de u_θ, a y
z_cost; v1 multiplicaba δ.lo (u_θ alto) por z^((θ−1).lo) (u_θ bajo) y el umbral apenas crecía con z en cajas anchas.

Para una caja Θ de primitivas (z_m = 1) y un τ = (τ_d, τ_f) fijo del menú df (todo τ del menú es admisible: C2(θ) =
sup_τ Rn(τ; θ)/γ >= Rn(τ; θ)/γ), si en TODA la caja valen
  (P)  δ − tb >= 0                         (todo z >= 1 tiene estado previo F: δ z^(θ−1) − tb creciente)
  (F)  G: (1 − t̃_d) γ − k_F > 0;  N: γ − k_F > 0   (F1-F0 > 0 en todo z >= 1: el corchete crece con z^(1−ρ))
y z_hi >= 1 cumple H(z_hi) = δ z_hi^(θ−1) − b + min(0, C z_hi^(ρ−1)) >= 0 (encierro por intervalos, .lo), con
  b = tb + t̃_d γ,  C = −φ κ0 t̃_f (G)  o  C = κ0 [t̃_d − φ t̃_f (1 − t̃_d)] (N),
entonces F1-I1(z)/z = δ z^(θ−1) − b + C z^(ρ−1) >= H(z_hi) >= 0 para todo z >= z_hi (θ > 1, ρ <= 1), y todo z >= z_hi
está en el régimen final F (previo F, F1-F0 > 0, F1-I1 >= 0: encierros_modelo._regime). Cada empresa con z en [1, z_hi)
aporta al menos lo que aportaría si pasara a informal (−τ_d β z): N aporta 0 y F aporta un integrando >= 0. Así, con las
integrales normalizadas por μ (M1(z, ∞) = z^(1−a), M1(1, z) = 1 − z^(1−a), Mρ(z, ∞) = q z^(ρ−a)) y s = κ̃ q:
  Rn/γ >= f(z_hi) = τ_d [ −β̃ (1 − z_hi^(1−a)) + r* z_hi^(1−a) ] + s [ τ_f q* g_f − [N] τ_d r* (1 + φ t̃_f) ] z_hi^(ρ−a)
(en N el término de A es r* ∫ (z − (k_F/γ) z^ρ) >= 0 sobre [z_hi, ∞)). f es AFÍN en s para z_hi fijo, y s solo depende de
(κ̃, a, ρ) con rango exacto (inf_df_bb_v3.s_rango): el mínimo está en un extremo. Para G conjunta se suma k s − k
(mismo θ). Con z_hi = 1 se recupera exactamente la cota «todos formales» (inf_df_bb_v3.cota_inf_tau_v3).
"""
from __future__ import annotations

import math

from codigo.inf_df_bb_v3 import s_rango
from paper2b import encierros_modelo as EM
from paper2b.intervalos import Iv

ZERO = Iv(0.0, 0.0)


def _zp(z: float, e: Iv) -> Iv:
    if z == 1.0:
        return Iv(1.0, 1.0)
    return EM.iexp(EM.ilog(Iv(z, z)) * e)


class CotaCaja:
    """Precalcula lo que no depende de τ para una caja θ."""

    def __init__(self, th: dict, fixed: dict, dis: str):
        self.th, self.dis = th, dis
        self.P = EM.IParams.from_primitive_box(th, fixed)
        P = self.P
        if not (P.z_m.lo == P.z_m.hi == 1.0 and P.theta.lo > 1.0 and P.rho.hi <= 1.0 and P.a.lo > 1.0):
            raise ValueError("HIPOTESIS_ZM_THETA_RHO_A")
        self.S = s_rango(th)
        self.th1, self.rh1 = P.theta - 1.0, P.rho - 1.0
        self.one_a, self.rho_a = 1.0 - P.a, P.rho - P.a
        self.bt = P.beta / P.gamma                      # β̃
        self.evaluaciones = 0

    def cota(self, td: float, tf: float, k: float | None = None, zmax: float = 1e6, nbis: int = 40):
        """(cota inferior de Rn/γ [o de G si k] en la caja con τ, z_hi) o (None, None) si (P)/(F) no se demuestran."""
        self.evaluaciones += 1
        P, dis = self.P, self.dis
        Td, Tf = Iv(td, td), Iv(tf, tf)
        x = EM.tax_side(P, EM.AD(Td), EM.AD(Tf), EM.AD(P.phi))
        g, d, k0, kF = P.gamma, P.delta, P.kappa0, x.kF.v
        tdv, tfv = x.td.v, x.tf.v
        tdv, tfv = Iv(max(tdv.lo, 0.0), tdv.hi), Iv(max(tfv.lo, 0.0), tfv.hi)   # t̃ >= 0 (ver inf_df_techo_v3)
        tb = Td * P.beta
        if not (d - tb).lo >= 0.0:
            return None, None
        if not (((1.0 - tdv) * g - kF) if dis == "G" else (g - kF)).lo > 0.0:
            return None, None
        b = tb + tdv * g
        C = (-(P.phi * k0 * tfv)) if dis == "G" else (k0 * (tdv - P.phi * tfv * (1.0 - tdv)))

        lzc = EM.ilog(Iv(float(self.th["z_cost"][0]), float(self.th["z_cost"][1])))

        def H_lo(z):
            X = C * _zp(z, self.rh1)
            lz = EM.ilog(Iv(z, z)) if z != 1.0 else ZERO
            dz = P.gamma * EM.iexp(self.th1 * (lz - lzc))          # = δ z^(θ−1) (z_m = 1)
            return (dz - b).lo + min(0.0, X.lo)
        if H_lo(1.0) >= 0.0:
            z = 1.0
        else:
            lo, hi = 1.0, 2.0
            while not H_lo(hi) >= 0.0:
                lo, hi = hi, hi * 2.0
                if hi > zmax:
                    return None, None
            for _ in range(nbis):
                m = math.sqrt(lo * hi)
                if m <= lo or m >= hi:
                    break
                if H_lo(m) >= 0.0:
                    hi = m
                else:
                    lo = m
            z = hi
        M1 = _zp(z, self.one_a)
        Mr = _zp(z, self.rho_a)
        base = Td * ((-self.bt) * (1.0 - M1) + x.rstar.v * M1)
        D = Tf * x.qstar.v * x.gf.v
        if dis == "N":
            D = D - Td * x.rstar.v * (1.0 + P.phi * tfv)
        D = D * Mr
        if k is not None:
            D = D + Iv(k, k)
        v = min((base + Iv(s, s) * D).lo for s in (self.S.lo, self.S.hi))
        if k is not None:
            v = (Iv(v, v) - Iv(k, k)).lo
        return v, z


def mejor_tau(cc: CotaCaja, bd: float, bf: float, k: float | None = None, semilla=None, pasos: int = 14):
    """Mayor cota sobre τ: rejilla (τ_d relativo a δ.lo/(γ(β̃.hi + 1)), τ_f absoluto) + búsqueda por patrones; con
    `semilla` (τ de la caja madre) se empieza por ella y una rejilla corta alrededor. Devuelve (cota, τ)."""
    P = cc.P
    td0 = max(1e-12, (P.delta.lo / P.gamma.hi) / (cc.bt.hi + 1.0))
    best = (-math.inf, None)

    def ev(td, tf):
        nonlocal best
        td, tf = min(max(td, 0.0), bd), min(max(tf, 0.0), bf)
        v, _ = cc.cota(td, tf, k)
        if v is not None and v > best[0]:
            best = (v, (td, tf))
    if k is not None:
        S = cc.S
        best = (min((Iv(s, s) * Iv(k, k) - Iv(k, k)).lo for s in (S.lo, S.hi)), (0.0, 0.0))   # C2 >= 0
    if semilla is not None:
        sd, sf = semilla
        for fd in (0.9, 1.0, 1.1):
            for ff in (0.8, 1.0, 1.2):
                ev(sd * fd, sf * ff)
    else:
        for fd in (0.5, 0.8, 0.95, 1.0, 1.1, 1.25, 1.5):
            for tf in (0.0, 0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.15, 0.2):
                ev(td0 * fd, tf)
    if best[1] is None or best[1] == (0.0, 0.0):
        return best
    td, tf = best[1]
    hd, hf = 0.1, max(0.01, tf * 0.2)
    for _ in range(pasos):
        b0 = best[0]
        for sd in (-1, 0, 1):
            for sf in (-1, 0, 1):
                if sd or sf:
                    ev(td * (1 + sd * hd), tf + sf * hf)
        if best[0] <= b0:
            hd, hf = hd / 2, hf / 2
        td, tf = best[1]
    return best
