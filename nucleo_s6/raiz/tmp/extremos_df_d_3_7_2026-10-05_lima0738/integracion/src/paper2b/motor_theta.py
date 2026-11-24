"""Motor θ: encierro de Rn(τ; θ) = R/μ con GRADIENTE ENCERRADO respecto de las variables estructurales y las tasas
(EXTREMOS df/d 3.7, NO OFICIAL). Fundamento: review/METODO_EXTREMOS_DF_D.md.

Por qué. En df y d el corte de régimen F0-I0 vale c = z_cost z_m (τ_d β̃)^(1/(θ-1)) con θ - 1 = u_θ (a - 1) desde 0,01:
sobre una caja de θ el corte recorre rangos enormes de z y el encierro NATURAL (motor normalizado) toma la envolvente de
los dos regímenes en esas celdas: sobreestimación de primer orden (diagnóstico DTH de cierre_candidato_3_7). La forma de
VALOR MEDIO en las 11 variables v = (τ_d, τ_f, a, ρ, κ̃, β̃, u_θ, z_cost, η_d, η_f, φ)
        Rn(v) ∈ Rn(v_c) + Σ_i ∂_i Rn(V) · (V_i - v_c,i)
es de SEGUNDO orden donde el gradiente es continuo, y el signo demostrado de ∂_i Rn permite fijar el eje i en una cara
(prueba de monotonía) en la rama y cota.

Qué se reutiliza sin cambios: la partición en celdas de ln z, los signos demostrados de los trinomios, la clasificación de
régimen y el VALOR encerrado (codigo/demo/c2_normalizado.MotorNormalizado, subclase del motor original). Lo nuevo es el
gradiente respecto de θ, por diferenciación directa (paper2b.encierros_modelo.AD con tuplas de 11 componentes):
- parámetros derivados como funciones de θ: θ_exp = 1 + u_θ (a - 1), δ = γ (z_cost z_m)^(1-θ_exp), κ0 = κ̃ γ z_m^(1-ρ),
  β = β̃ γ (las fórmulas de IParams.from_primitive_box);
- lado tributario y trinomios con los MISMOS operadores que el motor (tax_side, trinomials), con parámetros AD;
- momentos normalizados en forma cerrada M_n(m; lo, hi) = c_n(m) [(lo/z_m)^(m-a) - (hi/z_m)^(m-a)], c_n(1) = 1,
  c_n(ρ) = (a-1)/(a-ρ) z_m^(ρ-1), derivados respecto de a y ρ con los bordes de celda como intervalos (fijos en θ);
- celda indecisa con UN solo trinomio ambiguo k (dT_k/dz sin cero, demás signos ciertos): la derivada parcial (corte
  fijo) se encierra con los momentos parciales [lo, c] y [c, hi] con c en toda la celda, más el término de Leibniz
  (g_izq(c) - g_der(c)) f_n(c) dc/dv, dc/dv = -(∂T_k/∂v)/(∂T_k/∂z), con ∂T_k/∂v = gradiente AD de
  T_k(z) = A z^θ + B z + C z^ρ evaluado en z en la celda (incluye z^θ ln z ∂θ y z^ρ ln z ∂ρ); máscara [0, 1] si la
  celda empieza en z_m (el corte puede caer fuera del dominio).
Sin gradiente (None: se usa SOLO el encierro natural, válido): curvas de salto con ρ = 1, celdas con varios trinomios
ambiguos o raíz múltiple posible, cola sin dominancia demostrada. La validez del valor medio exige Rn continua y C1 a
trozos en la caja: es la misma condición con la que el motor original usa la forma de valor medio en (τ_d, τ_f, φ);
donde hay salto no se usa.
Redondeo: todo con paper2b.intervalos (hacia afuera) y cotas demostradas de paper2b.elementales.
"""
from __future__ import annotations

import itertools
import math

from paper2b import encierros_modelo as EM
from paper2b.encierros_modelo import (AD, ZERO, _edge, _regime, _sign, add, ad_E, ad_exp, ad_log1m, div, ilog, ipow, mul,
                                      neg, sub)
from paper2b.intervalos import Iv

try:
    from .c2_normalizado import MotorNormalizado            # dentro de paper2b (integración candidata)
except ImportError:
    from .demo.c2_normalizado import MotorNormalizado       # codigo/ del área (desarrollo)

VARS = ("tau_d", "tau_f", "a", "rho", "kappa_tilde", "beta_tilde", "u_theta", "z_cost", "eta_d", "eta_f", "phi")
NV = len(VARS)
STRUCT = VARS[2:]
ONE = Iv(1.0, 1.0)
INF = math.inf
ESTADISTICA = {"lema_violaciones": 0, "lema_aplicado": 0}      # acumulado del proceso (se informa en cada salida)


def var(v: Iv, i: int) -> AD:
    g = [ZERO] * NV
    g[i] = ONE
    return AD(v, tuple(g))


def ad_log(x: AD) -> AD:
    v = ilog(x.v)
    return AD(v, None if x.g is None else tuple(gi * (ONE / x.v) for gi in x.g))


def ad_pow_const(base: Iv, p: AD) -> AD:
    """base^p con base > 0 CONSTANTE (sin gradiente) y exponente AD."""
    return ad_exp(mul(p, ilog(base)))


class QParams:
    """Parámetros derivados como AD sobre la caja θ (mismas fórmulas que IParams.from_primitive_box)."""

    def __init__(self, box: dict, fixed: dict):
        I = lambda p: Iv(float(box[p][0]), float(box[p][1]))  # noqa: E731
        self.gamma, self.z_m = Iv.point(float(fixed["gamma"])), Iv.point(float(fixed["z_m"]))
        a, rho, kt, bt = var(I("a"), 2), var(I("rho"), 3), var(I("kappa_tilde"), 4), var(I("beta_tilde"), 5)
        ut, zc = var(I("u_theta"), 6), var(I("z_cost"), 7)
        self.a, self.rho = a, rho
        self.eta_d, self.eta_f, self.phi = var(I("eta_d"), 8), var(I("eta_f"), 9), var(I("phi"), 10)
        self.theta = add(1.0, mul(ut, sub(a, 1.0)))
        lzz = add(ad_log(zc), ilog(self.z_m))                      # ln(z_cost z_m)
        self.delta = mul(self.gamma, ad_exp(mul(sub(1.0, self.theta), lzz)))
        self.kappa0 = mul(mul(kt, self.gamma), ad_pow_const(self.z_m, sub(1.0, rho)))
        self.beta = mul(bt, self.gamma)


def tax_ad(Q: QParams, Td: AD, Tf: AD) -> EM.Tax:
    """paper2b.encierros_modelo.tax_side con η_d, η_f, φ, κ0, β como AD."""
    ld = ad_log1m(Td)
    td = neg(mul(ld, ad_E(mul(add(1.0, Q.eta_d), ld))))
    rstar = ad_exp(mul(Q.eta_d, ld))
    lf = ad_log1m(Tf)
    alpha = sub(Q.eta_f, Q.phi)
    tf = add(mul(Tf, ad_exp(mul(alpha, lf))),
             mul(mul(neg(lf), Q.eta_f), sub(ad_E(mul(alpha, lf)), ad_E(mul(add(alpha, 1.0), lf)))))
    kF = mul(Q.kappa0, add(1.0, mul(Q.phi, tf)))
    qstar = ad_exp(mul(Q.eta_f, lf))
    gf = ad_exp(neg(mul(Q.phi, lf)))
    tb = mul(Td, Q.beta)
    return EM.Tax(td, sub(1.0, td), rstar, tf, kF, qstar, gf, tb)


def tri_ad(Q: QParams, x: EM.Tax, design: str) -> dict:
    """paper2b.encierros_modelo.trinomials con A también AD (δ depende de θ)."""
    g, d, k0 = Q.gamma, Q.delta, Q.kappa0
    tb, td, one_td, kF, tf = x.tb, x.td, x.one_td, x.kF, x.tf
    z = AD(ZERO)
    out = {"F0-I0": (d, neg(tb), z, neg(tb)),
           "I1-I0": (z, AD(g), neg(k0), sub(g, k0)),
           "I1-F0": (neg(d), add(tb, g), neg(k0), sub(add(tb, g), k0))}
    if design == "G":
        out["F1-F0"] = (z, mul(one_td, g), neg(kF), sub(mul(one_td, g), kF))
        out["F1-I0"] = (d, sub(mul(one_td, g), tb), neg(kF), sub(sub(mul(one_td, g), kF), tb))
        phitf = mul(mul(k0, Q.phi), tf)
        out["F1-I1"] = (d, neg(add(tb, mul(td, g))), neg(phitf), neg(add(add(tb, mul(td, g)), phitf)))
    else:
        out["F1-F0"] = (z, AD(g), neg(kF), sub(g, kF))
        out["F1-I0"] = (d, sub(mul(one_td, g), tb), neg(mul(one_td, kF)), sub(mul(one_td, sub(g, kF)), tb))
        cn = sub(k0, mul(one_td, kF))
        out["F1-I1"] = (d, neg(add(tb, mul(td, g))), cn, sub(cn, add(tb, mul(td, g))))
    return out


def P_ok(P) -> bool:
    """Hipótesis del lema sobre los parámetros derivados: γ > 0, z_m > 0, a > 1."""
    return P.gamma.lo > 0.0 and P.z_m.lo > 0.0 and P.a.lo > 1.0


def _gz(g):
    return tuple(ZERO for _ in range(NV)) if g is None else g


class MotorTheta(MotorNormalizado):
    """Valor: el del motor normalizado sobre la caja θ (natural). Gradiente: 11 componentes o None."""

    def __init__(self, box: dict, fixed: dict, design: str, **kw):
        super().__init__(EM.IParams.from_primitive_box(box, fixed), design, **kw)
        self.box, self.fixed = box, fixed
        self.Q = QParams(box, fixed)
        self.motivo = None
        # Lema E0 <= 0 (sin transición informal -> formal): hipótesis sobre la caja θ; las de τ se comprueban en R_full
        self._lema_caja = (float(box["phi"][0]) >= 0.0 and float(box["kappa_tilde"][1]) <= 1.0 and float(box["rho"][1]) <= 1.0
                           and float(box["kappa_tilde"][0]) >= 0.0 and P_ok(self.P))
        self._lema = False
        self.lema_violaciones = 0

    # ------------------------------------------------------------------ lema E0 <= 0
    def R_full(self, Td: Iv, Tf: Iv, Phi: Iv | None = None, *, grad: bool = False, force: tuple = ()):
        """LEMA (sin transición informal -> formal). Con τ_d, τ_f en [0, 1), φ >= 0, 0 <= κ̃ <= 1, ρ <= 1, γ > 0:
        tilde_d = (1 - (1-τ_d)^(1+η_d))/(1+η_d) ∈ [0, 1) y tilde_f >= 0 (E creciente y l_f <= 0). El régimen final es F
        solo si F1-I1 >= 0 (model.partition / _regime). En G, F1-I1 = δ z^θ - (tb + td γ) z - φ κ0 tf z^ρ >= 0 implica
        F0-I0 = δ z^θ - tb z >= td γ z >= 0; en N, F1-I1 = δ z^θ - (tb + td γ) z + c z^ρ con
        c = κ0 [td - φ tf (1 - td)] <= κ0 td, de modo que F0-I0 >= td (γ z^(1-ρ) - κ0) z^ρ >= 0 porque
        γ z^(1-ρ) >= γ z_m^(1-ρ) >= κ̃ γ z_m^(1-ρ) = κ0 para z >= z_m. Así el estado previo es F (F0-I0 >= 0) siempre que
        el final sea F: e = d1 - d0 ∈ {0, -1} en todo z y el integrando de E0 = β ∫ z e dFn es <= 0. Se usa como cota
        del VALOR en los tramos indecisos (E0 ∩ (-inf, 0]); en los tramos ciertos se CUENTA toda violación (debe ser 0)."""
        self._lema = self._lema_caja and Td.lo >= 0.0 and Tf.lo >= 0.0 and Td.hi < 1.0 and Tf.hi < 1.0
        return super().R_full(Td, Tf, Phi, grad=grad, force=force)

    def _certain(self, reg, Zlo, Zhi, x):
        e, _ = self._coef(reg)
        if self._lema and e > 0.0:
            self.lema_violaciones += 1
            ESTADISTICA["lema_violaciones"] += 1
        return super()._certain(reg, Zlo, Zhi, x)

    # ------------------------------------------------------------------ valor: regímenes ENUMERADOS en tramos con varios cortes
    def _uncertain(self, it, Zlo, Zhi, tri, x, grad):
        """Valor del tramo indeciso = encierro del motor normalizado ∩ envolvente por regímenes ENUMERADOS.

        Para cada z del tramo y cada (τ, θ) de la caja, el vector de signos de los seis trinomios es uno de los vectores
        compatibles con los signos demostrados sobre el tramo completo (los ambiguos toman -1, 0 o +1); el régimen es el
        de model.partition para ese vector (_regime), así que el coeficiente del integrando (e = d1 - d0 en E0, f_F en A
        y W) está en la envolvente de esos regímenes, y la integral en la envolvente por el momento del tramo (M >= 0).
        Es la cota universal del motor (e en [-1, 1], f_F en [0, 1]) restringida a los regímenes posibles. Solo valor
        (grad=False); con gradiente se devuelve el del motor sin cambios."""
        out = super()._uncertain(it, Zlo, Zhi, tri, x, grad)
        if grad:
            return out
        dE, dA, dW, ok = out
        if self._lema:                                            # lema E0 <= 0 (ver R_full)
            if dE.v.lo > 0.0:
                self.lema_violaciones += 1
                ESTADISTICA["lema_violaciones"] += 1
            else:
                ESTADISTICA["lema_aplicado"] += 1
                dE = AD(Iv(dE.v.lo, min(dE.v.hi, 0.0)), dE.g)
                out = (dE, dA, dW, ok)
        P = self.P
        Zu = Iv(Zlo.lo, Zhi.hi)
        if not math.isfinite(Zu.hi):
            return out
        sg = {k: self._tri_sign(A_, B.v, C.v, L.v, Zu) for k, (A_, B, C, L) in tri.items()}
        amb = [k for k, s in sg.items() if s == 0]
        if len(amb) > 5:
            return out
        es, fs = set(), set()
        for combo in itertools.product((-1, 0, 1), repeat=len(amb)):
            e, f = self._coef(_regime(dict(sg, **dict(zip(amb, combo)))))
            es.add(e)
            fs.add(f)
        M1 = self.moment(Iv.point(1.0), Zlo, Zhi)
        Mr = self.moment(P.rho, Zlo, Zhi)
        eh, fh = Iv(min(es), max(es)), Iv(min(fs), max(fs))
        vE = P.beta * M1 * eh
        vW = Mr * fh
        if self.design == "G":
            vA = P.gamma * M1 * fh
        elif fh.lo == fh.hi == 1.0:
            vA = P.gamma * M1 - x.kF.v * Mr
        elif fh.lo == fh.hi == 0.0:
            vA = ZERO
        else:
            vA = (P.gamma * M1 - x.kF.v * Mr).hull(ZERO)

        def cap(a: AD, b: Iv) -> AD:
            lo, hi = max(a.v.lo, b.lo), min(a.v.hi, b.hi)
            return AD(Iv(lo, hi) if lo <= hi else a.v, a.g)
        return cap(dE, vE), cap(dA, vA), cap(dW, vW), ok

    # ------------------------------------------------------------------ momentos normalizados en forma cerrada (AD)
    def mom_ad(self, m, Zlo: Iv, Zhi: Iv) -> AD:
        Q = self.Q
        if m == 1.0:
            cn, k = AD(ONE), sub(1.0, Q.a)
        else:
            cn = mul(div(sub(Q.a, 1.0), sub(Q.a, m)), ad_pow_const(Q.z_m, sub(m, 1.0)))
            k = sub(m, Q.a)

        def term(Zb: Iv) -> AD:
            if not math.isfinite(Zb.lo):
                return AD(ZERO)                                   # z^(m-a) -> 0 (m <= 1 < a)
            r = Zb / Q.z_m
            r = Iv(max(r.lo, 1.0), max(r.hi, 1.0))               # bordes >= z_m
            if not math.isfinite(r.hi):
                lo_t = ad_exp(mul(k, ilog(Iv(r.lo, r.lo))))
                return AD(Iv(0.0, lo_t.v.hi), None if lo_t.g is None else tuple(gi.hull(ZERO) for gi in lo_t.g))
            return ad_exp(mul(k, ilog(r)))
        return mul(cn, sub(term(Zlo), term(Zhi)))

    def _Tz(self, tri_k, Z: Iv) -> AD:
        """T_k(z) = A z^θ + B z + C z^ρ como AD (z en Z, constante)."""
        Q = self.Q
        A_, B, C, L = tri_k
        lz = ilog(Z)
        zth = ad_exp(mul(Q.theta, lz))
        if self.P.rho_is_one:
            return add(mul(A_, zth), mul(L, Z))
        return add(add(mul(A_, zth), mul(B, Z)), mul(C, ad_exp(mul(Q.rho, lz))))

    # ------------------------------------------------------------------ contribuciones
    def _certain_ad(self, reg, Zlo, Zhi, x):
        Q = self.Q
        e, fF = self._coef(reg)
        M1 = self.mom_ad(1.0, Zlo, Zhi)
        dE = mul(Q.beta, mul(M1, e)) if e != 0.0 else AD(ZERO)
        if fF == 0.0:
            return dE, AD(ZERO), AD(ZERO)
        Mr = self.mom_ad(Q.rho, Zlo, Zhi)
        dA = mul(Q.gamma, M1) if self.design == "G" else sub(mul(Q.gamma, M1), mul(x.kF, Mr))
        return dE, dA, Mr

    def _uncertain_ad(self, it, Zlo, Zhi, tri0, tri, x0, x):
        P, Q = self.P, self.Q
        _, s0, s1, amb, _ = it
        if not (len(amb) == 1 and math.isfinite(s1)):
            self.motivo = "VARIOS_CORTES_O_COLA"
            return None
        Zu = Iv(Zlo.lo, Zhi.hi)
        k = amb[0]
        dz = self._dz(tri0, k, Zu)
        others = {kk: self._tri_sign(A_, B.v, C.v, L.v, Zu) for kk, (A_, B, C, L) in tri0.items() if kk != k}
        if _sign(dz) == 0 or any(v == 0 for v in others.values()):
            self.motivo = "RAIZ_MULTIPLE_O_OTRO_SIGNO_INDECISO"
            return None
        sL, sR = (-1, 1) if dz.lo > 0.0 else (1, -1)
        eL, fL = self._coef(_regime(dict(others, **{k: sL})))
        eR, fR = self._coef(_regime(dict(others, **{k: sR})))
        # derivada parcial con el corte c fijo: momentos parciales [lo, c] y [c, hi] con c en toda la celda
        M1a, M1b = self.mom_ad(1.0, Zlo, Zu), self.mom_ad(1.0, Zu, Zhi)
        Mra, Mrb = self.mom_ad(Q.rho, Zlo, Zu), self.mom_ad(Q.rho, Zu, Zhi)
        dE = mul(Q.beta, add(mul(M1a, float(eL)), mul(M1b, float(eR))))
        dW = add(mul(Mra, float(fL)), mul(Mrb, float(fR)))
        G1 = add(mul(M1a, float(fL)), mul(M1b, float(fR)))
        dA = mul(Q.gamma, G1) if self.design == "G" else sub(mul(Q.gamma, G1), mul(x.kF, dW))
        # Leibniz: (g_izq - g_der)(c) f_n(c) dc/dv
        Tz = self._Tz(tri[k], Zu)
        gv = _gz(Tz.g)
        f = self.density(Zu)
        dc = tuple(Iv(-1.0, -1.0) * gi / dz for gi in gv)
        mask = Iv(0.0, 1.0) if s0 == self.s_m else ONE
        Zr = Zu if P.rho_is_one else ipow(Zu, P.rho)
        jE = P.beta * Zu * float(eL - eR) * f * mask
        jW = Zr * float(fL - fR) * f * mask
        jA = (P.gamma * Zu * float(fL - fR) * f * mask if self.design == "G"
              else (P.gamma * Zu - x0.kF.v * Zr) * float(fL - fR) * f * mask)
        ge = tuple(a_ + jE * d for a_, d in zip(_gz(dE.g), dc))
        gw = tuple(a_ + jW * d for a_, d in zip(_gz(dW.g), dc))
        ga = tuple(a_ + jA * d for a_, d in zip(_gz(dA.g), dc))
        return AD(dE.v, ge), AD(dA.v, ga), AD(dW.v, gw)

    # ------------------------------------------------------------------ gradiente de Rn sobre (Td x Tf x caja θ)
    def gradiente(self, Td: Iv, Tf: Iv):
        P = self.P
        self.motivo = None
        td0, tf0, ph0 = AD.var(Td, 0, False), AD.var(Tf, 1, False), AD.var(P.phi, 2, False)
        x0 = EM.tax_side(P, td0, tf0, ph0)
        x0._ph = ph0
        tri0 = EM.trinomials(P, x0, self.design)
        if P.rho_is_one and [k for k in ("I1-I0", "F1-F0") if tri0[k][0].lo == 0.0 == tri0[k][0].hi and _sign(tri0[k][3].v) == 0]:
            self.motivo = "SALTO_RHO_1"
            return None
        wbox = max(Td.hi - Td.lo, Tf.hi - Tf.lo, P.phi.hi - P.phi.lo)
        cells = self.partition(tri0, max(self.ds_min, 1e-4 * wbox))
        s_m = self.s_m
        items = []
        for (s0, s1, Z, state, reg, amb) in cells:                 # misma fusión de tramos que R_full
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
        Q = self.Q
        tdv, tfv = var(Td, 0), var(Tf, 1)
        x = tax_ad(Q, tdv, tfv)
        tri = tri_ad(Q, x, self.design)
        E0 = A = W = AD(ZERO, _gz(None))
        for it in items:
            Zlo, Zhi = _edge(it[1], s_m, P.z_m), _edge(it[2], s_m, P.z_m)
            if it[0] == "c":
                dE, dA, dW = self._certain_ad(it[3], Zlo, Zhi, x)
            else:
                r = self._uncertain_ad(it, Zlo, Zhi, tri0, tri, x0, x)
                if r is None:
                    return None
                dE, dA, dW = r
            E0, A, W = add(E0, dE), add(A, dA), add(W, dW)
        Bd = add(E0, mul(x.rstar, A))
        Bf = mul(mul(mul(x.qstar, Q.kappa0), x.gf), W)
        R = add(mul(tdv, Bd), mul(tfv, Bf))
        return _gz(R.g)


def centro(box: dict) -> dict:
    return {p: (0.5 * (lo + hi),) * 2 for p, (lo, hi) in box.items()}


def valor(box: dict, fixed: dict, design: str, Td: Iv, Tf: Iv) -> Iv:
    """Encierro natural de Rn (motor normalizado) sobre Td x Tf x caja θ."""
    eng = MotorNormalizado(EM.IParams.from_primitive_box(box, fixed), design)
    return eng.R(Td, Tf)[0]


def encierro(box: dict, fixed: dict, design: str, Td: Iv, Tf: Iv, stats: dict | None = None):
    """(encierro de Rn sobre Td x Tf x caja θ = natural ∩ valor medio, gradiente o None).

    Valor medio con centro v_c = punto medio (redondeado) de la caja: Rn(v) ∈ Rn(v_c) + Σ g_i (V_i - v_c,i). Válido
    porque el segmento entre v_c y cualquier v de la caja está en la caja, donde g encierra el gradiente (Rn continua y C1
    a trozos: los términos de Leibniz cubren los quiebres en los cortes)."""
    mt = MotorTheta(box, fixed, design)
    nat = mt.R(Td, Tf)[0]
    g = mt.gradiente(Td, Tf)
    if stats is not None:
        stats["motivo_sin_gradiente"] = mt.motivo
    if g is None:
        return nat, None
    cb = centro(box)
    cd, cf = 0.5 * (Td.lo + Td.hi), 0.5 * (Tf.lo + Tf.hi)
    vc = valor(cb, fixed, design, Iv(cd, cd), Iv(cf, cf))
    D = [Td - cd, Tf - cf] + [Iv(*box[p]) - cb[p][0] for p in STRUCT]
    mv = vc
    for gi, di in zip(g, D):
        mv = mv + gi * di
    lo, hi = max(nat.lo, mv.lo), min(nat.hi, mv.hi)
    return (Iv(lo, hi) if lo <= hi else nat), g


# ============================================================================================ cotas cerradas del lema
def _g_max(T: Iv, e_lo: float, e_hi: float) -> float:
    """Cota superior DEMOSTRADA de max { t (1-t)^e : t en T, e en [e_lo, e_hi] } con T ⊆ [0, 1).
    (1-t)^e es decreciente en e (0 < 1-t <= 1): basta e = e_lo. Con e <= 0, t (1-t)^e es creciente en t (máximo en T.hi);
    con e > 0 es unimodal con máximo en t* = 1/(1+e): el máximo en T está en clamp(t*, T). La evaluación usa un
    intervalo de radio 1e-9 alrededor del punto (cubre el error de coma flotante de t*) y redondeo hacia afuera."""
    if e_lo <= 0.0:
        ts = T.hi
    else:
        ts = min(max(1.0 / (1.0 + e_lo), T.lo), T.hi)
    I = Iv(max(T.lo, ts - 1e-9), min(T.hi, ts + 1e-9))
    v = I * EM.iexp(Iv(e_lo, e_lo) * EM.ilog1m(I))
    return v.hi


def cota_analitica(box, fixed, dis) -> float:
    """Cota superior de Rn sobre la caja por el LEMA E0 <= 0 (motor_theta.MotorTheta.R_full) y la positividad de los
    integrandos (z >= z_m, κ̃ <= 1, ρ <= 1):
      Rn = τ_d (E0 + r* A) + τ_f q* κ0 x_f^(-φ) W <= τ_d r* γ (1 - [N] κ̃ q(a, ρ)) + τ_f q* κ̃ γ x_f^(-φ) q(a, ρ),
    con A <= ∫ (γ z - [N] κ0 z^ρ) dFn = γ (1 - [N] κ̃ q), W <= ∫ z^ρ dFn = q z_m^(ρ-1), q(a, ρ) = (a-1)/(a-ρ) creciente
    en a y en ρ (dq/da = (1-ρ)/(a-ρ)^2 >= 0, dq/dρ = (a-1)/(a-ρ)^2 > 0), r* = (1-τ_d)^η_d, q* x_f^(-φ) = (1-τ_f)^(η_f-φ).
    En N con τ_f > 0 el término -k_F z^ρ de A se descarta (cota válida, más holgada). z_m = 1 y γ fijos."""
    Td, Tf = Iv(*box["tau_d"]), Iv(*box["tau_f"])
    if not (Td.lo >= 0.0 and Tf.lo >= 0.0 and Td.hi < 1.0 and Tf.hi < 1.0 and box["phi"][0] >= 0.0
            and box["kappa_tilde"][1] <= 1.0 and box["rho"][1] <= 1.0 and float(fixed["z_m"]) == 1.0):
        return math.inf
    gam = Iv.point(float(fixed["gamma"]))
    q_lo = ((Iv.point(box["a"][0]) - 1.0) / (Iv.point(box["a"][0]) - Iv.point(box["rho"][0]))).lo
    q_hi = ((Iv.point(box["a"][1]) - 1.0) / (Iv.point(box["a"][1]) - Iv.point(box["rho"][1]))).hi
    fac = Iv.point(1.0)
    if dis == "N" and Tf.hi == 0.0:
        fac = Iv.point(1.0) - Iv.point(box["kappa_tilde"][0]) * Iv.point(q_lo)
    gd = _g_max(Td, box["eta_d"][0], box["eta_d"][1]) if Td.hi > 0.0 else 0.0
    t1 = Iv.point(gd) * fac
    t2 = Iv.point(0.0)
    gf_max = 0.0
    if Tf.hi > 0.0:
        e_lo = (Iv.point(box["eta_f"][0]) - Iv.point(box["phi"][1])).lo
        gf_max = _g_max(Tf, e_lo, e_lo)
        t2 = Iv.point(gf_max) * Iv.point(box["kappa_tilde"][1]) * Iv.point(q_hi)
    ub1 = ((t1 + t2) * gam).hi
    return min(ub1, cota_umbral(box, fixed, dis, gd, gf_max, q_lo, q_hi))


def cota_umbral(box, fixed, dis, gd, gf_max, q_lo, q_hi) -> float:
    """Cota de UMBRAL FORMAL (refina cota_analitica). Por el lema, régimen final F => previo F => F1-F0 > 0, es decir
    (1 - td) γ z - k_F z^ρ > 0 <=> z > z_c = (k_F / ((1 - td) γ))^(1/(1-ρ)) (ρ < 1; con ρ = 1: todos los z si el cociente
    r < 1 y ninguno si r >= 1). Así [F] ⊆ {z > max(z_m, z_c)} y, como el integrando es >= 0 en z > z_c (en N:
    γ z - k_F z^ρ > td γ z >= 0 allí),
      Rn <= τ_d r* γ M1n(z_c, ∞) - [N] τ_d r* k_F Mρn(z_c, ∞) + τ_f q* κ0 x_f^(-φ) Mρn(z_c, ∞),
    M1n(z, ∞) = z^(1-a), Mρn(z, ∞) = q(a, ρ) z^(ρ-a) (z_m = 1). Monotonías usadas (z >= 1): z^(1-a) y z^(ρ-a) decrecen en z
    y en a y z^(ρ-a) crece en ρ; z_c crece con r y con ρ (r > 1). r = k_F / ((1 - td) γ) se encierra con tax_side."""
    if not math.isfinite(gd + gf_max):
        return math.inf
    Td, Tf = Iv(*box["tau_d"]), Iv(*box["tau_f"])
    th = {p: box[p] for p in STRUCT}
    P = EM.IParams.from_primitive_box(th, fixed)
    x = EM.tax_side(P, EM.AD(Td), EM.AD(Tf), EM.AD(P.phi))
    gam = P.gamma
    r = x.kF.v / ((1.0 - x.td.v) * gam)
    a_lo, a_hi = box["a"]
    r_lo, r_hi = box["rho"]

    def zc(rv, rho):
        if rv <= 1.0:
            return 1.0
        if rho >= 1.0:
            return math.inf
        return None
    zl = zc(r.lo, r_lo)
    if zl is None:
        e = (Iv.point(1.0) / (Iv.point(1.0) - Iv.point(r_lo))).lo
        zl = max(1.0, EM.ipow(Iv.point(r.lo), Iv.point(e)).lo)
    zh = zc(r.hi, r_hi)
    if zh is None:
        e = (Iv.point(1.0) / (Iv.point(1.0) - Iv.point(r_hi))).hi
        zh = max(1.0, EM.ipow(Iv.point(r.hi), Iv.point(e)).hi)

    def potencia(z, ex: Iv, alta: bool) -> float:
        if not math.isfinite(z):
            return 0.0
        v = EM.ipow(Iv.point(z), ex)
        return v.hi if alta else v.lo
    M1_hi = potencia(zl, Iv.point(1.0) - Iv.point(a_lo), True)
    Mr_hi = (Iv.point(q_hi) * Iv.point(potencia(zl, Iv.point(r_hi) - Iv.point(a_lo), True))).hi
    Mr_lo = (Iv.point(q_lo) * Iv.point(potencia(zh, Iv.point(r_lo) - Iv.point(a_hi), False))).lo
    pos = Iv.point(gd) * gam * Iv.point(M1_hi) + Iv.point(gf_max) * Iv.point(box["kappa_tilde"][1]) * gam * Iv.point(Mr_hi)
    if dis == "N" and Td.lo > 0.0:
        neg = Iv.point(Td.lo) * Iv.point(x.rstar.v.lo) * Iv.point(x.kF.v.lo) * Iv.point(Mr_lo)
        pos = pos - neg
    return pos.hi
