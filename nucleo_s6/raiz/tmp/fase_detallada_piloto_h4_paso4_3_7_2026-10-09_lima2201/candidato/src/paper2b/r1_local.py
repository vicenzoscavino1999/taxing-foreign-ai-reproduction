"""Subdivisión LOCAL de cajas de R1 sin resolver, con aristas certificadas (CONSOLIDACIÓN 3.7, NO OFICIAL; versión 2).

Cambios de la versión 2 (defecto A del revisor):
- Las raíces de las aristas EXTERIORES reciben los MISMOS controles que las interiores y que el criterio estándar
  (`_cruces`): una raíz `tangent` -> CRUCE_TANGENTE; residuo no finito o > tol_residual -> RESIDUO_SOBRE_TOLERANCIA.
  Los controles se aplican también en la recursión (las aristas de una subcaja se vuelven a controlar).
- COMPROBACIÓN FINAL independiente antes de declarar `resuelta` (`comprobar_resuelta`): cada tramo con extremos dentro
  de la caja madre cerrada y residuo finito <= tol_residual; cota geométrica finita y <= diagonal de la madre. Si falla,
  la madre queda pendiente con motivo COMPROBACION_FINAL.
- EVIDENCIA de aristas en el resultado (`evidencia`): por arista exterior e interior, estado de la búsqueda y raíces
  (punto, x, intervalo aislante, residuo, tipo); la de cada subcaja subdividida se anida.

Texto de la versión 1:

Problema: en el nivel máximo, una caja madre (x0, x1, y0, y1) no tiene monotonía certificada en x ni en y. Se divide en
m x m subcajas, recursivamente hasta `profundidad`, SIN cambiar la caja madre ni sus vecinas.

Aristas y consistencia:
- Las 4 aristas EXTERIORES de la madre son las mismas que ven sus vecinas: sus raíces certificadas se calculan sobre
  la arista COMPLETA, con la misma llamada que el algoritmo estándar (`edge_madre`), y NO se recalculan.
- Cada raíz de una arista exterior se ASIGNA a un subsegmento solo si su intervalo aislante certificado [lo, hi] está
  dentro de él. Si [lo, hi] contiene un punto de división interior p:
    * se exige que el vértice p sea limpio (encierro de f en el punto sin 0);
    * se decide el lado con encierros certificados de f en [lo, p] y [p, hi]: si f no se anula en [lo, p] (encierro
      sin 0), la raíz está en (p, hi]; si no se anula en [p, hi], está en [lo, p). Si ninguno lo demuestra, el cruce
      queda SIN ASIGNAR y las subcajas adyacentes quedan pendientes (CRUCE_EN_LIMITE_COMPARTIDO).
- Las aristas INTERIORES se calculan con la misma búsqueda certificada en 1-D (`_edge_roots`), una vez por
  subsegmento (compartidas por las dos subcajas). Todo vértice interior con cruce posible (encierro de f en el punto
  con 0) deja pendientes las subcajas que lo comparten (CRUCE_EN_VERTICE_COMPARTIDO).
Subcaja: vacía (encierro sin 0), resuelta (monotonía en y o en x, cruces certificados sin tangencias, residuo bajo
tolerancia, número par, emparejados como en el algoritmo estándar) o subdividida otra vez. La madre queda resuelta
solo si TODAS sus subcajas no vacías lo están; si no, pendiente (con motivos). Cobertura: las subcajas forman una
partición exacta de la madre (coordenadas compartidas). Cota geométrica de cada tramo = diagonal de su subcaja.
"""
from __future__ import annotations

import math

from .intervalos import Iv


def _edge_roots(*a, **k):
    from .contour import _edge_roots as er
    return er(*a, **k)


def _malla(a, b, m):
    return [a] + [a + (b - a) * k / m for k in range(1, m)] + [b]


def _limpio(ev, x, y):
    return ev.range(x, x, y, y).excludes_zero()


def _f_sin_cero(ev, eje, c, a, b):
    """Encierro certificado de f en el segmento (eje 'y' fija y = c; 'x' fija x = c) sin 0."""
    if a > b:
        a, b = b, a
    return ev.range(a, b, c, c).excludes_zero() if eje == "y" else ev.range(c, c, a, b).excludes_zero()


def control_raiz(r, tol_residual):
    """Controles de una raíz certificada, iguales para aristas exteriores e interiores y para el criterio estándar.
    Devuelve None si la raíz es aceptable o el motivo de rechazo (un residuo NaN también se rechaza)."""
    if r.kind == "tangent":
        return "CRUCE_TANGENTE"
    if not (math.isfinite(r.residual) and r.residual <= tol_residual):
        return "RESIDUO_SOBRE_TOLERANCIA"
    return None


def _ser(rs, found):
    return {"estado": rs.status, "raices": [[pt[0], pt[1], r.x, r.lo, r.hi, r.residual, r.kind] for pt, r in found]}


def asignar(rs, found, cortes, eje, c, ev, motivos, tol_residual):
    """Asigna las raíces certificadas de una arista exterior a sus subsegmentos [cortes[k], cortes[k+1]], después de
    aplicarles los mismos controles que a las interiores. Devuelve (lista por subsegmento de [(pt, r)], ok)."""
    out = [[] for _ in range(len(cortes) - 1)]
    if rs.status != "complete":
        motivos.append("ARISTA_MADRE_SIN_COBERTURA")
        return out, False
    for _, r in found:
        mal = control_raiz(r, tol_residual)
        if mal is not None:
            motivos.append(mal)
            return out, False
    for pt, r in found:
        lo, hi = (r.lo, r.hi) if getattr(r, "lo", None) is not None else (r.x, r.x)
        k = None
        for j in range(len(cortes) - 1):
            a, b = cortes[j], cortes[j + 1]
            ext_a = j == 0                      # los extremos de la madre se aceptan inclusivos
            ext_b = j == len(cortes) - 2
            if (lo > a or (ext_a and lo >= a)) and (hi < b or (ext_b and hi <= b)):
                k = j
                break
        if k is None:
            interiores = [p for p in cortes[1:-1] if lo <= p <= hi]
            if len(interiores) != 1:
                motivos.append("CRUCE_EN_LIMITE_COMPARTIDO")
                return out, False
            p = interiores[0]
            vx, vy = (p, c) if eje == "y" else (c, p)
            if not _limpio(ev, vx, vy):
                motivos.append("CRUCE_EN_LIMITE_COMPARTIDO")
                return out, False
            j = cortes.index(p)
            if _f_sin_cero(ev, eje, c, lo, p):
                k = j                           # raíz en (p, hi]: subsegmento que empieza en p
            elif _f_sin_cero(ev, eje, c, p, hi):
                k = j - 1                       # raíz en [lo, p)
            else:
                motivos.append("CRUCE_EN_LIMITE_COMPARTIDO")
                return out, False
        out[k].append((pt, r))
    return out, True


def resolver(f, ev, caja, exteriores, tol_residual, *, m=4, profundidad=2, cont=None, _nivel=1):
    """caja = (x0, x1, y0, y1); exteriores = {'abajo','arriba','izq','der'}: (rs, found) de las aristas COMPLETAS.
    Devuelve dict con resultado 'resuelta' o 'pendiente', piezas, diag, motivos y estadísticas."""
    x0, x1, y0, y1 = caja
    xs, ys = _malla(x0, x1, m), _malla(y0, y1, m)
    motivos = []
    stats = {"subcajas": 0, "vacias": 0, "resueltas": 0, "subdivididas": 0, "pendientes": 0, "aristas_interiores": 0}
    # aristas exteriores: asignación certificada a subsegmentos
    evid = {"caja": list(caja), "exteriores": {k: _ser(*v) for k, v in exteriores.items()}, "interiores": {}, "sub": {}}
    abajo, ok1 = asignar(*exteriores["abajo"], xs, "y", y0, ev, motivos, tol_residual)
    arriba, ok2 = asignar(*exteriores["arriba"], xs, "y", y1, ev, motivos, tol_residual)
    izq, ok3 = asignar(*exteriores["izq"], ys, "x", x0, ev, motivos, tol_residual)
    der, ok4 = asignar(*exteriores["der"], ys, "x", x1, ev, motivos, tol_residual)
    if not (ok1 and ok2 and ok3 and ok4):
        return {"resultado": "pendiente", "motivos": sorted(set(motivos)), "piezas": [], "diag": 0.0, "estadisticas": stats,
                "evidencia": evid}
    # vértices interiores (incluidos los puntos de división de las aristas exteriores ya tratados al asignar)
    sucios = {(a, b) for a in range(1, m) for b in range(1, m) if not _limpio(ev, xs[a], ys[b])}
    cache = {}

    def seg(eje, k, j):
        """Raíces del subsegmento j de la línea k (eje 'h': y = ys[k], x en [xs[j], xs[j+1]]; 'v': x = xs[k])."""
        if eje == "h" and k == 0:
            return ("ok", abajo[j])
        if eje == "h" and k == m:
            return ("ok", arriba[j])
        if eje == "v" and k == 0:
            return ("ok", izq[j])
        if eje == "v" and k == m:
            return ("ok", der[j])
        key = (eje, k, j)
        if key not in cache:
            stats["aristas_interiores"] += 1
            if eje == "h":
                rs, found = _edge_roots(f, ev, "y", ys[k], xs[j], xs[j + 1], tol_residual)
            else:
                rs, found = _edge_roots(f, ev, "x", xs[k], ys[j], ys[j + 1], tol_residual)
            evid["interiores"]["%s,%d,%d" % key] = _ser(rs, found)
            malos = [control_raiz(r, tol_residual) for _, r in found]
            if rs.status != "complete":
                cache[key] = ("ARISTA_SIN_COBERTURA_CERTIFICADA", [])
            elif "CRUCE_TANGENTE" in malos:
                cache[key] = ("CRUCE_TANGENTE", [])
            elif any(x is not None for x in malos):
                cache[key] = ("RESIDUO_SOBRE_TOLERANCIA", [])
            else:
                cache[key] = ("ok", found)
        return cache[key]
    piezas, diag, pendiente = [], 0.0, False
    for a in range(m):
        for b in range(m):
            stats["subcajas"] += 1
            sx0, sx1, sy0, sy1 = xs[a], xs[a + 1], ys[b], ys[b + 1]
            if ev.range(sx0, sx1, sy0, sy1).excludes_zero():
                stats["vacias"] += 1
                continue
            vert = [(a, b), (a + 1, b), (a, b + 1), (a + 1, b + 1)]
            if any(v in sucios for v in vert):
                motivos.append("CRUCE_EN_VERTICE_COMPARTIDO")
                stats["pendientes"] += 1
                pendiente = True
                continue
            mono_y = ev.dy(sx0, sx1, sy0, sy1).excludes_zero()
            mono_x = (not mono_y) and ev.dx(sx0, sx1, sy0, sy1).excludes_zero()
            lados = {"abajo": seg("h", b, a), "arriba": seg("h", b + 1, a), "izq": seg("v", a, b), "der": seg("v", a + 1, b)}
            if not (mono_x or mono_y):
                if _nivel < profundidad and all(v[0] == "ok" for v in lados.values()):
                    sub = resolver(f, ev, (sx0, sx1, sy0, sy1), {k: (_Completo(), v[1]) for k, v in lados.items()}, tol_residual,
                                   m=m, profundidad=profundidad, cont=cont, _nivel=_nivel + 1)
                    stats["subdivididas"] += 1
                    evid["sub"]["%d,%d" % (a, b)] = sub["evidencia"]
                    if sub["resultado"] == "resuelta":
                        piezas += sub["piezas"]
                        diag = max(diag, sub["diag"])
                        continue
                    motivos += sub["motivos"]
                else:
                    motivos.append("SIN_MONOTONIA_CERTIFICADA")
                stats["pendientes"] += 1
                pendiente = True
                continue
            malos = [v[0] for v in lados.values() if v[0] != "ok"]
            if malos:
                motivos += malos
                stats["pendientes"] += 1
                pendiente = True
                continue
            pts = {}
            for _, found in lados.values():
                for pt, r in found:
                    pts[(round(pt[0], 15), round(pt[1], 15))] = (pt, r)
            if len(pts) % 2:
                motivos.append("CRUCES_IMPARES")
                stats["pendientes"] += 1
                pendiente = True
                continue
            order = sorted(pts.values(), key=lambda pr: (pr[0][0], pr[0][1]) if mono_y else (pr[0][1], pr[0][0]))
            for q in range(0, len(order), 2):
                piezas.append([list(order[q][0]), list(order[q + 1][0]), max(order[q][1].residual, order[q + 1][1].residual)])
            if order:
                diag = max(diag, math.hypot(sx1 - sx0, sy1 - sy0))
            stats["resueltas"] += 1
    if not pendiente:
        fallos = comprobar_resuelta(caja, piezas, diag, tol_residual)
        if fallos:
            motivos += ["COMPROBACION_FINAL: " + x for x in fallos]
            pendiente = True
    if pendiente:
        return {"resultado": "pendiente", "motivos": sorted(set(motivos)), "piezas": [], "diag": 0.0, "estadisticas": stats,
                "evidencia": evid}
    return {"resultado": "resuelta", "motivos": [], "piezas": piezas, "diag": diag, "estadisticas": stats, "evidencia": evid}


def comprobar_resuelta(caja, piezas, diag, tol_residual):
    """Comprobación INDEPENDIENTE de las condiciones necesarias para aceptar una caja resuelta por subdivisión local
    (no reutiliza las decisiones de la asignación): extremos dentro de la caja madre cerrada, residuo finito <=
    tol_residual en cada tramo y cota geométrica finita, positiva si hay tramos y <= diagonal de la madre."""
    x0, x1, y0, y1 = caja
    fallos = []
    for k, (pa, pb, rr) in enumerate(piezas):
        for x, y in (pa, pb):
            if not (x0 <= x <= x1 and y0 <= y <= y1):
                fallos.append("TRAMO_%d_FUERA_DE_LA_CAJA" % k)
        if not (isinstance(rr, (int, float)) and math.isfinite(rr) and rr <= tol_residual):
            fallos.append("TRAMO_%d_RESIDUO_%r" % (k, rr))
    if not (math.isfinite(diag) and diag <= math.hypot(x1 - x0, y1 - y0)) or (piezas and not diag > 0):
        fallos.append("COTA_GEOMETRICA_%r" % (diag,))
    return sorted(set(fallos))


class _Completo:
    """Estado 'complete' para listas de raíces ya certificadas de una arista de una subcaja (recursión)."""
    status = "complete"
