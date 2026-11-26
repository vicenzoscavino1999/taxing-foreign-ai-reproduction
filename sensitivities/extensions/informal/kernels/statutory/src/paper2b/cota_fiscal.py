"""Cota inferior de C2(φ) por PUNTOS FISCALES con PLAZO COMÚN (CORRECCIÓN COTAS Y PASO 4 3.7, NO OFICIAL).

Se copia BYTE A BYTE como paper2b/cota_fiscal.py de la integración candidata (construir_integracion.py, paso 4).
Fundamento de la cota (sin cambios): C2(φ) >= R(τ*; φ)/B_pot >= ([R](τ*, I)/[B_pot]).lo para todo τ* del menú y todo φ de I.

Defecto corregido (reproducido por el revisor y en codigo/prueba_plazo_fiscal.py): la versión anterior solo miraba el
reloj ENTRE tramos de la partición; argmax, _refinar y sus búsquedas internas podían hacer miles de evaluaciones sin
mirarlo (presupuesto 1 s, 32 184 evaluaciones y 321,84 s simulados). Ahora:
- un único Plazo (reloj MONOTÓNICO) para TODA la inversión: lo crea el llamador (Run.phi_total) antes de la ruta fiscal
  y lo hereda la búsqueda posterior, sin reiniciarlo al cambiar de ruta;
- CADA evaluación de Rf y de Ri pasa por plazo.comprobar(): el agotamiento se detecta dentro de argmax, _refinar y de la
  malla, no solo entre tramos;
- agotado el plazo, el tramo en curso y los que quedan pasan a «cortados»; se conservan los decididos (resultados
  parciales) y la partición NO certifica nada (el llamador exige cobertura completa, sin pendientes ni cortes). Una
  búsqueda inconclusa nunca se convierte en inexistencia certificada.
El algoritmo (orden de evaluaciones, reglas de decisión) es el mismo de la versión anterior cuando el plazo no se agota.
"""
from __future__ import annotations

import math
import time

from .intervalos import Iv

DIRS = [(math.cos(2 * math.pi * k / 64), math.sin(2 * math.pi * k / 64)) for k in range(64)]


class PlazoAgotado(Exception):
    """El plazo común de la inversión se agotó durante la ruta fiscal."""


class Plazo:
    """Plazo absoluto en un reloj MONOTÓNICO (inyectable para pruebas). limite = None: sin plazo."""

    def __init__(self, limite: float | None, reloj=time.monotonic):
        self.limite, self.reloj = limite, reloj
        self.comprobaciones = 0

    @classmethod
    def desde(cls, segundos: float | None, reloj=time.monotonic) -> "Plazo":
        return cls(None if segundos is None else reloj() + float(segundos), reloj)

    def restante(self) -> float:
        return math.inf if self.limite is None else self.limite - self.reloj()

    def agotado(self) -> bool:
        return self.limite is not None and self.reloj() > self.limite

    def comprobar(self) -> None:
        self.comprobaciones += 1
        if self.agotado():
            raise PlazoAgotado("plazo agotado")

    def reserva(self, fraccion: float, tope: float | None = None) -> "Plazo":
        """Plazo hijo para una ruta previa: vence en min(este plazo, ahora + fraccion * restante, ahora + tope)."""
        r = self.restante()
        seg = fraccion * r if math.isfinite(r) else None
        if tope is not None:
            seg = tope if seg is None else min(seg, tope)
        return self.acotado(seg)

    def acotado(self, segundos: float | None) -> "Plazo":
        """Plazo hijo que vence en min(este plazo, ahora + segundos), sobre el MISMO reloj (no reinicia el común)."""
        if segundos is None:
            return Plazo(self.limite, self.reloj)
        lim = self.reloj() + float(segundos)
        return Plazo(lim if self.limite is None else min(lim, self.limite), self.reloj)


SIN_PLAZO = None
# Fracción MÁXIMA del plazo común restante que puede usar la ruta fiscal (complemento previo a la búsqueda): la búsqueda
# existente conserva al menos el resto del MISMO plazo (no se amplía nada). Medido en codigo/perfil_presupuesto.py: sin
# esta reserva la ruta fiscal consumía todo el plazo de 1 s y la búsqueda quedaba agotada en las 96 inversiones de la
# corrida pequeña, cuando en el original 80 terminaban.
FRACCION_RUTA_FISCAL = 0.25


def _vigilado(f, plazo: Plazo | None):
    if plazo is None:
        return f

    def g(*a):
        plazo.comprobar()
        return f(*a)
    return g


# ================================================================================ núcleo genérico
def argmax(Rf, menu, phi, start=None, n=41, refinar=True, plazo: Plazo | None = None):
    """Máximo en flotante de R(., φ) sobre el menú (sin certificar: solo elige τ*). Lanza PlazoAgotado si se agota."""
    Rf = _vigilado(Rf, plazo)
    (dl, dh), (fl, fh) = menu
    pts = []
    if start is None or n:
        for i in range(n + 1):
            for k in range(n + 1):
                x, y = dl + (dh - dl) * i / n, fl + (fh - fl) * k / n
                pts.append((Rf(x, y, phi), x, y))
        pts.sort(reverse=True)
        starts = [(p[1], p[2]) for p in pts[:4]]
    else:
        starts = []
    if start is not None:
        starts = [start] + starts
    best = None
    for (x, y) in starts:
        v = Rf(x, y, phi)
        s = 0.05 * max(dh - dl, fh - fl, 1e-12)
        while s > 1e-12:
            mejor = None
            for dx, dy in DIRS:
                xx, yy = min(max(x + s * dx, dl), dh), min(max(y + s * dy, fl), fh)
                w = Rf(xx, yy, phi)
                if w > v and (mejor is None or w > mejor[0]):
                    mejor = (w, xx, yy)
            if mejor is None:
                s *= 0.5
            else:
                v, x, y = mejor
        if refinar:
            v, x, y = _refinar(Rf, menu, phi, v, x, y)          # Rf ya vigilado
        if best is None or v > best[0]:
            best = (v, x, y)
    return best


def _refinar(Rf, menu, phi, v, x, y, plazo: Plazo | None = None):
    """Nelder-Mead 2-D + movimientos de patrón (Hooke-Jeeves). Sin certificar. Lanza PlazoAgotado si se agota."""
    Rf = _vigilado(Rf, plazo)
    (dl, dh), (fl, fh) = menu
    cl = lambda p: (min(max(p[0], dl), dh), min(max(p[1], fl), fh))  # noqa: E731
    F = lambda p: Rf(p[0], p[1], phi)  # noqa: E731
    for escala in (1e-3, 1e-5, 1e-7):
        S = [cl((x, y)), cl((x + escala, y)), cl((x, y + escala))]
        V = [F(p) for p in S]
        for _ in range(400):
            o = sorted(range(3), key=lambda i: -V[i])
            S, V = [S[i] for i in o], [V[i] for i in o]
            c = ((S[0][0] + S[1][0]) / 2, (S[0][1] + S[1][1]) / 2)
            r = cl((2 * c[0] - S[2][0], 2 * c[1] - S[2][1]))
            fr = F(r)
            if fr > V[0]:
                e = cl((3 * c[0] - 2 * S[2][0], 3 * c[1] - 2 * S[2][1]))
                fe = F(e)
                S[2], V[2] = (e, fe) if fe > fr else (r, fr)
            elif fr > V[1]:
                S[2], V[2] = r, fr
            else:
                k = cl(((c[0] + S[2][0]) / 2, (c[1] + S[2][1]) / 2))
                fk = F(k)
                if fk > V[2]:
                    S[2], V[2] = k, fk
                else:
                    S = [S[0]] + [cl(((S[0][0] + p[0]) / 2, (S[0][1] + p[1]) / 2)) for p in S[1:]]
                    V = [V[0]] + [F(p) for p in S[1:]]
            if max(abs(S[i][j] - S[0][j]) for i in (1, 2) for j in (0, 1)) < 1e-14:
                break
        i = max(range(3), key=lambda i: V[i])
        if V[i] > v:
            v, (x, y) = V[i], S[i]
        s, prev = 1e-4, None
        while s > 1e-13:
            mejor = None
            for dx, dy in DIRS:
                p = cl((x + s * dx, y + s * dy))
                w = F(p)
                if w > v and (mejor is None or w > mejor[0]):
                    mejor = (w, p)
            if mejor is None:
                s *= 0.5
                prev = None
                continue
            w, p = mejor
            if prev is not None:
                q = cl((2 * p[0] - prev[0], 2 * p[1] - prev[1]))
                wq = F(q)
                if wq > w:
                    prev, (x, y), v = (x, y), q, wq
                    s *= 2.0
                    continue
            prev, (x, y), v = (x, y), p, w
    return v, x, y


def cota_inferior(Ri, B, x, y, a, b):
    """( [R](τ*, [a, b]) / [B] ).lo: cota inferior certificada de C2 en [a, b] desde el punto fiscal τ* = (x, y)."""
    e = Ri(x, y, a, b)
    return (e / B).lo


def particion(Ri, Rf, B, menu, K, *, k_min=16, n_ini=32, tope=None, log=None, hechos=None, parar_bajo=None,
              plazo: Plazo | None = None):
    """Partición adaptativa de [0, 1]. Devuelve (decididos, pendientes, cortados) con (a, b, cota, τ*) / (a, b).

    plazo: plazo COMÚN de la inversión (se respeta dentro de argmax/_refinar/Ri). tope: compatibilidad; si se da sin
    plazo crea uno monotónico de `tope` segundos; si se dan ambos vale el MÁS CERCANO. Agotado: el tramo en curso y los
    que quedan van a cortados (no se certifica nada)."""
    if plazo is None:
        plazo = Plazo.desde(tope)
    elif tope is not None:
        plazo = plazo.acotado(tope)
    Rf_v, Ri_v = _vigilado(Rf, plazo), _vigilado(Ri, plazo)
    hechos = hechos or {}
    cola = [(i / n_ini, (i + 1) / n_ini) for i in range(n_ini)]
    dec, pend, cortados = [], [], []
    taus, malla, refinados = {}, set(), set()
    ultimo = None
    while cola:
        a, b = cola.pop(0)
        if (a, b) in hechos:
            h = hechos[(a, b)]
            if h["estado"] == "positivo":
                dec.append((a, b, h["cota"], tuple(h["tau"])))
                ultimo = tuple(h["tau"])
            elif h["estado"] == "dividido":
                m = 0.5 * (a + b)
                cola[0:0] = [(a, m), (m, b)]
            else:
                pend.append((a, b, h["cota"], tuple(h["tau"])))
            continue
        if plazo.agotado():
            cortados.append((a, b))
            continue
        try:
            m = 0.5 * (a + b)
            cand = []
            for p in (m, a, b):
                if p not in taus:
                    taus[p] = argmax(Rf_v, menu, p, start=ultimo, n=0 if ultimo is not None else 41, refinar=False)
                cand.append(taus[p])
            best = max(((cota_inferior(Ri_v, B, x, y, a, b), (x, y)) for _, x, y in cand), key=lambda t: t[0])
            if best[0] <= K and m not in refinados and taus[m][0] / B.lo <= K:
                refinados.add(m)
                g = _refinar(Rf_v, menu, m, *taus[m])
                if g[0] > taus[m][0]:
                    taus[m] = g
                best = max(best, (cota_inferior(Ri_v, B, g[1], g[2], a, b), (g[1], g[2])), key=lambda t: t[0])
            if best[0] <= K and m not in malla and taus[m][0] / B.lo <= K and b - a >= 1.0 / 256:
                malla.add(m)
                g = argmax(Rf_v, menu, m, start=best[1], n=41)
                if g[0] > taus[m][0]:
                    taus[m] = g
                best = max(best, (cota_inferior(Ri_v, B, g[1], g[2], a, b), (g[1], g[2])), key=lambda t: t[0])
        except PlazoAgotado:
            cortados.append((a, b))                         # el tramo en curso queda sin decidir
            cortados.extend(cola)                           # y todos los que faltan
            cola = []
            break
        ultimo = best[1]
        if best[0] > K:
            estado = "positivo"
            dec.append((a, b, best[0], best[1]))
        elif parar_bajo is not None and taus[m][0] / B.lo < K - parar_bajo:
            estado = "pendiente_bajo_K"
            pend.append((a, b, best[0], best[1]))
        elif b - a > 2.0 ** -k_min:
            estado = "dividido"
            cola[0:0] = [(a, m), (m, b)]
        else:
            estado = "pendiente"
            pend.append((a, b, best[0], best[1]))
        if log:
            log(evento="tramo", a=a, b=b, estado=estado, cota=best[0], tau=list(best[1]), max_flotante_medio=taus[m][0] / B.lo,
                margen=best[0] - K)
    return dec, pend, cortados


def cubre(tramos):
    """Los tramos (a, b, ...) forman una partición exacta de [0, 1]."""
    s = sorted((t[0], t[1]) for t in tramos)
    return bool(s) and s[0][0] == 0.0 and s[-1][1] == 1.0 and all(s[k][1] == s[k + 1][0] for k in range(len(s) - 1))
