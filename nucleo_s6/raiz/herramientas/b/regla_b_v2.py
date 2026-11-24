"""REGLA CANDIDATA SEL-PASO4-B-v2: conteo, sello y validación de S1/S2/S3 (P0 COMPLETO H4 3.7, NO OFICIAL; candidata, NO
activada, NO incorporada; no autoriza la fase global P1 ni la detallada).

Texto vigente (autenticado, sin cambios): ENM-PASO4-B-v5 §2 de la entrega cierre_374_3_7_2026-10-06_lima2333
(review/ENMIENDA_CANDIDATA_PASO4_B_v5.md, por su inventario). Esta biblioteca NO cambia la regla científica: la implementa.
- §2.1 celda = (contexto, ω, celda externa, cota, diseño, menú); ω por valores (omega_row). El cell_id candidato es el sha256
  COMPLETO del contenido canónico de esos componentes (más conjunto de soporte, país, estado nacional y caso, que los fija);
  los prefijos de 16 caracteres solo se muestran.
- §2.2 S1: ci (960) sup = punto de L, inf = punto de U (del testigo validado por E13 v4); country y global (768) heredan la
  celda de la hoja ci que realiza el extremo (sup máximo, inf mínimo; desempate d < df < f, país, claim_id), con fila propia y
  sin duplicar la celda; claves de C2 (12): punto que realiza la cota, contexto = primer contexto (orden de Universo.contexts)
  de la primera afirmación ci (claim_id) del mismo diseño y menú; motivo witness_c2.
- §2.3 S2: 168 estratos × 3; índice = int(sha256("SEL-PASO4-B-v2|<estrato>|<k>|<componente>"), 16) mod tamaño (formato del
  índice: el de la implementación parcial previa codigo/medir_lote_v2.modo_s2, con <estrato> = json.dumps de la tupla).
- §2.4 S3: pilotos declarados P1 (24) y P2 (8) del preregistro autenticado de pilotos_b36_b37.
- §2.5 deduplicación y precedencia; §2.6 cotas (4004 filas, 2468 celdas); §2.7 R3 (reparto exacto).
S1 es función determinista de los resultados globales: con resultados parciales, las filas sin testigo definitivo quedan
PENDIENTES con su motivo (nunca se fabrican); los conteos se separan en exactos y pendientes.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

REGLA = "SEL-PASO4-B-v2"
ESPEC = {"entrega": "cierre_374_3_7_2026-10-06_lima2333", "inventario_sha256": "eeb159023044c087f250ace07eeed76b6959db40df0d2f86a76cd3cead57c314",
         "archivo": "review/ENMIENDA_CANDIDATA_PASO4_B_v5.md"}
PRECEDENCIA = ("witness_sup", "witness_inf", "witness_c2", "declared_pilot", "stratified_sample")
N_ESTRATOS_S2, CELDAS_POR_ESTRATO, N_P1, N_P2 = 168, 3, 24, 8
N_AFIRMACIONES, N_CI, N_C2 = 1728, 960, 12
COTA_FILAS = 2 * N_AFIRMACIONES + N_C2 + N_ESTRATOS_S2 * CELDAS_POR_ESTRATO + N_P1 + N_P2      # 4004
COTA_CELDAS = 2 * N_CI + N_C2 + N_ESTRATOS_S2 * CELDAS_POR_ESTRATO + N_P1 + N_P2              # 2468
ORDEN_J = {"d": 0, "df": 1, "f": 2}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")


def campos(cid):
    p = cid.split(":")
    if p[3] == "ci":
        return {"pid": p[1], "kind": p[2], "fam": "ci", "pais": p[4], "j": p[5], "avail": p[6], "dis": p[7], "resto": tuple(p[8:])}
    if p[3] == "c":
        return {"pid": p[1], "kind": p[2], "fam": "c", "pais": p[4], "scen": p[5], "dis": p[6], "resto": tuple(p[7:])}
    return {"pid": p[1], "kind": p[2], "fam": "g", "scen": p[4], "dis": p[5], "resto": tuple(p[6:])}


# ============================================================================================== texto y sello
def texto_regla(raiz):
    """§2 del texto autenticado (inventario de lima2333 + sha256 del archivo)."""
    base = Path(raiz) / ESPEC["entrega"]
    inv_raw = (base / "audit/entrega.json").read_bytes()
    if sha(inv_raw) != ESPEC["inventario_sha256"]:
        raise ValueError("ESPEC_INVENTARIO_ALTERADO")
    raw = (base / ESPEC["archivo"]).read_bytes()
    if json.loads(inv_raw)["files"][ESPEC["archivo"]]["sha256"] != sha(raw):
        raise ValueError("ESPEC_NO_AUTENTICADA")
    txt = raw.decode("utf-8")
    i0 = txt.index("## 2. Texto candidato de la regla `SEL-PASO4-B-v2`")
    i1 = txt.index("## 3. Correspondencia exacta")
    return txt[i0:i1], sha(raw)


def sello(texto, codigo_sha256, parametros):
    """Sello de la regla ANTES de seleccionar: sha256 del texto §2, del código de esta biblioteca y de los parámetros."""
    cuerpo = {"regla": REGLA, "texto_sha256": sha(texto.encode("utf-8")), "codigo_sha256": codigo_sha256, "parametros": parametros}
    return dict(cuerpo, sello_sha256=sha(canon(cuerpo)))


def cell_id(contenido):
    return sha(canon(contenido))


# ============================================================================================== S1
def clave_hoja(sentido):
    if sentido == "sup":
        return lambda x: (-x[1], ORDEN_J[campos(x[0])["j"]], campos(x[0])["pais"], x[0])
    return lambda x: (x[2], ORDEN_J[campos(x[0])["j"]], campos(x[0])["pais"], x[0])


def s1(hojas, deps):
    """hojas: {(hoja_ci, sentido): {"L", "U", "definitivo", "cell_id"}} (testigos validados); deps: {afirmación: [dependencias]}
    de la AUTORIDAD (country -> hojas ci; global -> country). Una fila por afirmación y sentido (2 x 1728)."""
    memo = {}

    def gan(cid, s):
        """(hoja que realiza el extremo, su L, su U) o None si alguna hoja necesaria no tiene testigo definitivo."""
        if (cid, s) in memo:
            return memo[(cid, s)]
        if campos(cid)["fam"] == "ci":
            x = hojas.get((cid, s))
            r = (cid, x["L"], x["U"]) if x is not None and x["definitivo"] else None
        else:
            xs = [gan(d, s) for d in deps[cid]]
            r = None if any(x is None for x in xs) else min(xs, key=clave_hoja(s))
        memo[(cid, s)] = r
        return r

    def faltan(cid, s):
        if campos(cid)["fam"] == "ci":
            x = hojas.get((cid, s))
            return [] if x is not None and x["definitivo"] else [cid]
        return sorted({h for d in deps[cid] for h in faltan(d, s)})

    filas = []
    for cid in sorted(deps):
        for s in ("sup", "inf"):
            g = gan(cid, s)
            f = {"afirmacion": cid, "familia": campos(cid)["fam"], "reason": "witness_" + s, "witness_of": "%s:%s" % (cid, s)}
            if g is None:
                fl = faltan(cid, s)
                f.update(estado="pendiente", cell_id=None, hoja=None, motivo="hojas sin testigo definitivo: %d (p. ej. %s)" % (len(fl), fl[:2]))
            else:
                f.update(estado="definitivo", hoja=g[0], cell_id=hojas[(g[0], s)]["cell_id"])
                if f["cell_id"] is None:
                    f.update(estado="pendiente", motivo="celda de la hoja ganadora sin identificar")
            filas.append(f)
    return filas


# ============================================================================================== S2
def estratos_s2(claims_ci):
    """claims_ci: iterable de (support_sets, país, diseño, menú, cota) de las afirmaciones ci. Estratos h = (conjunto, país,
    diseño, menú, cota), ordenados por el sha256 de la regla (como modo_s2)."""
    es = {(sid, p, d, j, b) for sets, p, d, j, b in claims_ci for sid in sets}
    return sorted(es, key=lambda x: sha(("%s|estrato|%s" % (REGLA, json.dumps(list(x)))).encode()))


def indice(estrato, k, componente, n):
    if n <= 0:
        raise ValueError("TAMAÑO_NULO:%s" % componente)
    return int(sha(("%s|%s|%d|%s" % (REGLA, json.dumps(list(estrato)), k, componente)).encode()), 16) % n


def omega_l0(nodos, i):
    """ω estructural de índice i en el producto (orden de STRUCT, último eje más rápido) de los nudos L0 por eje."""
    vals = {}
    for p in reversed(list(nodos)):
        n = len(nodos[p])
        vals[p] = nodos[p][i % n]
        i //= n
    return {p: vals[p] for p in nodos}


# ============================================================================================== deduplicación, cotas, R3
def deduplicar(filas):
    """Celdas distintas (cell_id) con su motivo PRIMARIO por precedencia; una fila por (cell_id, reason, witness_of)."""
    vistas, celdas, dup = set(), {}, []
    for f in filas:
        if f.get("cell_id") is None:
            continue
        k = (f["cell_id"], f["reason"], f["witness_of"])
        if k in vistas:
            dup.append(k)
            continue
        vistas.add(k)
        c = celdas.setdefault(f["cell_id"], {"motivos": set(), "filas": 0})
        c["motivos"].add(f["reason"])
        c["filas"] += 1
    for c in celdas.values():
        c["motivo_primario"] = min(c["motivos"], key=PRECEDENCIA.index)
        c["motivos"] = sorted(c["motivos"], key=PRECEDENCIA.index)
    return celdas, dup


def reparto_r3(N_h, tasa=0.05):
    """§2.7: q_h = tasa N_h; n = ceil(Σ q_h); n_h = floor(q_h) + 1 para las n − Σ floor(q_h) cuotas de MAYOR parte fraccionaria
    (desempate: menor sha256("SEL-PASO4-B-v2|repro|" + h)). Σ n_h = n exactamente."""
    from fractions import Fraction
    q = {h: Fraction(tasa).limit_denominator(1000) * n for h, n in N_h.items()}
    n = math.ceil(sum(q.values()))
    base = {h: math.floor(v) for h, v in q.items()}
    resto = n - sum(base.values())
    orden = sorted(q, key=lambda h: (-(q[h] - base[h]), sha(("%s|repro|%s" % (REGLA, h)).encode())))
    out = dict(base)
    for h in orden[:resto]:
        out[h] += 1
    return {"n": n, "n_h": out, "suma": sum(out.values())}


def validar(filas_s1, celdas, dup, hojas, deps):
    """Validación de S1 y de la selección: completitud (2 x 1728), claves únicas, herencia (country/global = celda de la hoja
    ganadora, sin duplicarla), precedencia, cotas."""
    errores = []
    if len(filas_s1) != 2 * len(deps):
        errores.append("S1_INCOMPLETA:%d" % len(filas_s1))
    ids = [(f["witness_of"]) for f in filas_s1]
    if len(set(ids)) != len(ids):
        errores.append("S1_WITNESS_OF_DUPLICADO")
    for f in filas_s1:
        if f["estado"] != "definitivo":
            continue
        if f["familia"] == "ci":
            if f["hoja"] != f["afirmacion"]:
                errores.append("CI_HOJA_DISTINTA:%s" % f["afirmacion"])
        elif hojas[(f["hoja"], f["witness_of"].rsplit(":", 1)[1])]["cell_id"] != f["cell_id"]:
            errores.append("HERENCIA_DISTINTA:%s" % f["afirmacion"])
    if dup:
        errores.append("FILAS_DUPLICADAS:%d" % len(dup))
    filas_con_celda = sum(1 for f in filas_s1 if f.get("cell_id"))
    return {"errores": errores, "filas_s1": len(filas_s1), "filas_s1_con_celda": filas_con_celda, "celdas_distintas": len(celdas),
            "cotas": {"filas_max": COTA_FILAS, "celdas_max": COTA_CELDAS}, "cumple": not errores}
