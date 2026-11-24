"""Cota inferior de C2(φ) por PUNTOS FISCALES (integración candidata 3.7; fundamento y pruebas en
codigo/phi_cota_fiscal.py del área: C2(φ) >= R(τ*;φ)/B_pot >= ([R](τ*, I)/[B_pot]).lo para τ* del menú y todo φ de I)."""
from __future__ import annotations

import math
import time

from .intervalos import Iv

DIRS = [(math.cos(2 * math.pi * k / 64), math.sin(2 * math.pi * k / 64)) for k in range(64)]


# ================================================================================ núcleo genérico
def argmax(Rf, menu, phi, start=None, n=41, refinar=True):
    """Máximo en flotante de R(., φ) sobre el menú (sin certificar: solo elige τ*). `refinar`: Nelder-Mead + Hooke-Jeeves
    (caro); la partición lo usa solo cuando la búsqueda barata no decide el tramo."""
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
            v, x, y = _refinar(Rf, menu, phi, v, x, y)
        if best is None or v > best[0]:
            best = (v, x, y)
    return best


def _refinar(Rf, menu, phi, v, x, y):
    """Refinamiento para crestas con quiebre (intento 2): Nelder-Mead 2-D con simplex inicial pequeño y movimientos de
    patrón (Hooke-Jeeves: extrapolar el último desplazamiento), alternados con la búsqueda por patrones. Sin certificar:
    solo mejora la elección de τ* (la validez de la cota no depende de ella)."""
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
        # movimientos de patrón (Hooke-Jeeves) desde el mejor punto
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


def particion(Ri, Rf, B, menu, K, *, k_min=16, n_ini=32, tope=None, log=None, hechos=None, parar_bajo=None):
    """Partición adaptativa de [0, 1]. Devuelve (decididos, pendientes) con (a, b, cota, τ*)."""
    t0 = time.time()
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
        if tope is not None and time.time() - t0 > tope:
            cortados.append((a, b))
            continue
        m = 0.5 * (a + b)
        cand = []
        for p in (m, a, b):
            if p not in taus:
                taus[p] = argmax(Rf, menu, p, start=ultimo, n=0 if ultimo is not None else 41, refinar=False)
            cand.append(taus[p])
        best = max(((cota_inferior(Ri, B, x, y, a, b), (x, y)) for _, x, y in cand), key=lambda t: t[0])
        # Sin decisión con la búsqueda barata. Si el máximo barato en el punto medio ya supera K, lo que limita es el ancho
        # del tramo en φ (se divide); solo si NO lo supera puede ayudar un τ* mejor: refinamiento de crestas
        # (Nelder-Mead + Hooke-Jeeves) y, en tramos de ancho >= 1/256, malla completa.
        if best[0] <= K and m not in refinados and taus[m][0] / B.lo <= K:
            refinados.add(m)
            g = _refinar(Rf, menu, m, *taus[m])
            if g[0] > taus[m][0]:
                taus[m] = g
            best = max(best, (cota_inferior(Ri, B, g[1], g[2], a, b), (g[1], g[2])), key=lambda t: t[0])
        if best[0] <= K and m not in malla and taus[m][0] / B.lo <= K and b - a >= 1.0 / 256:
            # sin decisión con el arranque del vecino: búsqueda completa (malla + patrones) en el punto medio
            malla.add(m)
            g = argmax(Rf, menu, m, start=best[1], n=41)
            if g[0] > taus[m][0]:
                taus[m] = g
            best = max(best, (cota_inferior(Ri, B, g[1], g[2], a, b), (g[1], g[2])), key=lambda t: t[0])
        ultimo = best[1]
        if best[0] > K:
            estado = "positivo"
            dec.append((a, b, best[0], best[1]))
        elif parar_bajo is not None and taus[m][0] / B.lo < K - parar_bajo:
            # REGLA DE PARADA (resolución 3.7): el máximo aproximado en el punto medio está claramente bajo K; una cota
            # inferior no puede decidir ahí y subdividir no aporta. Queda PENDIENTE (no se afirma C2 < K ni raíz).
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


