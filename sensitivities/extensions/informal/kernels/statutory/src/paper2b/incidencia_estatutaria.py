"""Variante de incidencia estatutaria de la retencion (encargo del autor del 2026-11-22; POSTERIOR a los resultados base).

Formulacion: D:/paso3/topes_20261122/VARIANTE_ESTATUTARIA.md. Este modulo se copia dentro del paquete derivado
variante/src/paper2b y lo usan los sitios donde E11 entraba en el pago formal (model.py, encierros_modelo.py,
motor_theta.py). El paquete original (codigo/src/paper2b) no se toca.

E11 (base):           k_F(tau_f) = kappa0 * (1 + phi * tilde_f(tau_f))
Variante estatutaria: k_F(tau_f) = kappa0 * (1 + omega(tau_f, phi) * tilde_f(tau_f)),
                      omega(tau_f, phi) = 1 - s_P(tau_f, phi) = (1 - x_f^phi) / tau_f,  omega(0, phi) = phi.

SUPUESTO EXPLICITO (no lo fija ninguna norma): el coste real de ocultamiento c_f(1 - q*) de la fraccion no reportada se
reparte entre usuario y proveedor en la MISMA proporcion que el impuesto que evita: el usuario soporta 1 - s_P y el
proveedor s_P. En la fraccion reportada rige la clausula de gross-up: el usuario paga el bruto kappa0 x_f^(-phi) y soporta
1 - s_P de la retencion. Por eso toda la carga de la coalicion, tilde_f, se reparte con omega = 1 - s_P.

Lo que NO cambia: la eleccion conjunta de reporte q* = x_f^eta_f y la carga de la coalicion tilde_f (la clausula de
gross-up no altera la carga conjunta), y las formulas B_f = q* kappa0 x_f^(-phi) W_F, B_d = E_0 + r* A y
R = tau_d B_d + tau_f B_f. Lo que SI cambia: el pago formal k_F, y con el la particion de adopcion y estado, E_0, A_N,
W_F y, por tanto, las bases agregadas y la recaudacion.

Forma computable, sin singularidad en tau_f = 0: omega = phi * E(phi * l) / E(l), con l = log1p(-tau_f) y
E(y) = expm1(y)/y (E(0) = 1, E > 0 en toda la recta). En phi = 0 y phi = 1, omega es identicamente 0 y 1 para toda tasa:
se devuelve el valor exacto. En la version encerrada se conserva el gradiente encerrado de la formula general, que es
valido para el gradiente respecto de phi.
"""
from __future__ import annotations

import math

REGLA = "estatutaria_ocultamiento_proporcional"
SUPUESTO_OCULTAMIENTO = ("el coste de ocultamiento se reparte entre usuario y proveedor en la misma proporcion que el "
                         "impuesto evitado (usuario 1 - s_P, proveedor s_P)")


def _E(y: float) -> float:
    return 1.0 if y == 0.0 else math.expm1(y) / y


def omega(tau_f: float, phi: float) -> float:
    """Fraccion estatutaria del usuario, 1 - s_P(tau_f, phi), en aritmetica puntual; omega(0, phi) = phi."""
    if phi == 0.0 or phi == 1.0:
        return phi
    if not (0.0 <= tau_f < 1.0):
        raise ValueError("RATE_OUTSIDE_[0,1)")
    l = math.log1p(-tau_f)
    return phi * _E(phi * l) / _E(l)


def omega_ad(lf, Ph):
    """Encierro de omega con gradiente (operadores AD de encierros_modelo, redondeo hacia afuera).

    lf: encierro AD de log1p(-tau_f) (ya calculado por el llamador); Ph: encierro AD de phi.
    E(l) > 0 en todo el dominio, asi que el cociente esta bien definido, tambien en cajas que contienen tau_f = 0."""
    from . import encierros_modelo as EM          # diferido: encierros_modelo importa este modulo

    def formula(l_):
        return EM.div(EM.mul(Ph, EM.ad_E(EM.mul(Ph, l_))), EM.ad_E(l_))

    v = Ph.v
    if v.lo == v.hi and v.lo in (0.0, 1.0):
        # omega(., 0) = 0 y omega(., 1) = 1 para toda tasa: valor exacto y derivada respecto de tau_f exactamente nula.
        # Si phi lleva gradiente, se conserva solo su parte: d omega/d phi encerrada con l sin gradiente.
        if Ph.g is None:
            return EM.AD(EM.Iv(v.lo, v.lo))
        return EM.AD(EM.Iv(v.lo, v.lo), formula(EM.AD(lf.v)).g)
    return formula(lf)
