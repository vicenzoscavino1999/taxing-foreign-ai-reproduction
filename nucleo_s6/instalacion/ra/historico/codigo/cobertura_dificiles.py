"""Cobertura de las 84 afirmaciones restantes en las CINCO cajas difíciles (G y N): método dirigido M3 frente a M2r,
con persistencia por hoja y por testigo, y verificación de testigos nuevos (CONSOLIDACIÓN 3.7, NO OFICIAL).

  <py_integracion> -m codigo.cobertura_dificiles dirigido <familia> <k_caja,...> <salida_dir> <seg_por_caja> <hojas> <tope_s>
  <py_integracion> -m codigo.cobertura_dificiles medir <salida.json> <n_faciles> <semilla> <cajas_m2r k,...> <tope_s>

Universo: las 84 candidatas del registro CANDIDATO autenticado (testigos_cobertura, 1512 / 132 / 84): 42 G y 42 N,
todas del menú f (muestra_costo.pendientes() ya lee ese registro por defecto). Cajas difíciles: las 5 cajas L0 de la
muestra aleatoria que quedaron pendientes en G y en N (las mismas; κ̃ en su intervalo superior), autenticadas desde
testigos_cobertura/demo/costo/medicion_corregida.json.

Dominio, cuantificadores y tolerancias SIN CAMBIOS: por afirmación y hoja, G = C2 − K1 en TODOS sus contextos
(cobertura.g_enclosure con C2 normalizado compartido por hoja); cerrada en la hoja si max_contextos G.hi <= −ε;
posible testigo si max_contextos G.lo > −ε (toda la hoja, o el punto sondeado); ε = claims.EPS_ECON. Una afirmación
queda cerrada en la caja solo si TODAS sus hojas terminales la cierran.

M3 (dirigido), diferencias con M2r (cola FIFO, 64 hojas, 120 s, ejes del ranking de la raíz en ciclo):
1. ORDEN mejor-primero: se procesa la hoja de mayor potencial = max sobre afirmaciones pendientes de G.hi (la que
   puede contener testigos o es la cota limitante), en lugar del orden FIFO.
2. SONDEO de testigos en la raíz: además del centro, los centros de las 6 caras de los 3 ejes del ranking (un encierro
   de C2 puntual compartido por las 42 afirmaciones de la familia).
3. EJE por hoja: entre los 3 ejes del ranking de la raíz, el de mayor anchura relativa restante (bisección
   equilibrada), en lugar del ciclo por profundidad.
4. PRESUPUESTO declarado por caja (hojas y segundos); lo no cerrado al agotarse queda PENDIENTE.
Persistencia: cada hoja (caja, C2, q_pot y G.hi/G.lo por afirmación pendiente) y cada posible testigo se escriben al
instante (JSONL + fsync). Después, por afirmación con posible testigo: ficha en el punto (C2 puntual
c2_struct_enclosure, como el verificador) y verificación con verificador_v2.verificar_completo (rol A) + testigo
complementario B de nudo de la evidencia 3.7.1 (autenticada), como en testigos.py.
`medir`: costo por caja con las 42 afirmaciones de cada familia (M2r sin cambios, muestra_costo.cubrir) en n cajas
de la muestra que cerraban en la raíz (selección con semilla declarada) y M2r en las cajas difíciles indicadas.
"""
from __future__ import annotations

import hashlib
import heapq
import json
import math
import os
import random
import sys
import time
from decimal import Decimal
from pathlib import Path

from codigo import muestra_costo as MC
from codigo import testigos as T
from codigo.demo import nucleo_v as N
from codigo.demo import c2_normalizado as C2N
from codigo.demo import memo_c2 as MEMO
from codigo.demo.cobertura_compartida import q_pot_exact
from codigo.demo.verificador_v2 import Verificador
from paper2b import claims as CL
from paper2b import cobertura as COV
from paper2b import run as RUNMOD

EPS = CL.EPS_ECON
PREV = N.ROOT / "tmp/testigos_cobertura_3_7_2026-10-04"
PREV_INV = "a56a37e72484de2d02709185416e3c44880cc4acc1ab932b75641b94e0b308fa"
CERT = N.ROOT / "tmp/certificacion_3_7_2026-10-04"
CERT_INV = "99d51784614d96a099bc3371028818d45851146e3c088131fda902dcf81ce8e5"


def autenticado(base, inv_h, rel):
    inv_raw = (base / "audit/entrega.json").read_bytes()
    N.need(N.sha(inv_raw) == inv_h, "INVENTARIO:" + base.name)
    raw = (base / rel).read_bytes()
    N.need(json.loads(inv_raw)["files"][rel]["sha256"] == N.sha(raw), "NO_AUTENTICADO:" + rel)
    return json.loads(raw)


def cajas_dificiles():
    med = autenticado(PREV, PREV_INV, "demo/costo/medicion_corregida.json")
    g = [tuple(x) for x in med["estimaciones"]["G"]["pendientes_indices"]]
    n = [tuple(x) for x in med["estimaciones"]["N"]["pendientes_indices"]]
    N.need(sorted(g) == sorted(n), "CAJAS_DIFICILES_DISTINTAS_EN_G_Y_N")
    return sorted(g)


def cubrir_dirigido(st, dis, root, memo, ident, log, hoja_log, tarea, seg, max_hojas):
    model, fixed, univ, cand, meta = st["model"], st["fixed"], st["univ"], st["cand"], st["meta"]
    bd, bf = float(fixed["bar_tau_d"]), float(fixed["bar_tau_f"])
    n_c2 = [0]
    tb = time.time()

    def c2_of(b):
        n_c2[0] += 1
        k = MEMO.clave(b, dis, "f", bd, bf, fixed, model, "normalizado", ident)
        return memo.obtener(k, lambda: C2N.c2_normalizado(model, b, dis, "f", bd, bf, fixed=fixed), b)

    estado = {cid: "pendiente" for cid in cand}
    mejor_lo = {cid: -1e300 for cid in cand}

    def g_claim(b, cid, c2):
        ghi, glo, best = -1e300, -1e300, None
        for k, c in enumerate(univ[cid]):
            g = COV.g_enclosure(model, b, c, fixed, c2)
            if g is None:
                return None, None, None
            if g.lo > glo:
                best = (k, g)
            ghi, glo = max(ghi, g.hi), max(glo, g.lo)
        return ghi, glo, best

    def testigo(cid, b, best, c2, tipo):
        k, g = best
        c = univ[cid][k]
        k1 = T.k1_de(b, c)
        estado[cid] = "testigo"
        rec = dict(tarea=tarea, afirmacion=cid, tipo=tipo, conjunto=meta[cid][k][0], indice_contexto_nacional=meta[cid][k][1],
                   indice_contexto=k, contexto=T._ctx(c), nacional=T._nac(st, cid, meta[cid][k][0], meta[cid][k][1]),
                   C2=[c2.lo, c2.hi], K1=[k1.lo, k1.hi], G=[g.lo, g.hi])
        if tipo == "hoja":
            rec["caja"] = {p: list(v) for p, v in b.items()}
        else:
            rec["punto"] = {p: v[0] for p, v in b.items()}
        log(**rec)

    def sondear(pt, act, tipo):
        if not COV.box_admissible(pt, fixed):
            return
        c2c = c2_of(pt)
        if c2c is None:
            return
        for cid in list(act):
            if estado[cid] == "testigo":
                continue
            ghi, glo, best = g_claim(pt, cid, c2c)
            if glo is not None:
                mejor_lo[cid] = max(mejor_lo[cid], glo)
                if glo > -EPS:
                    testigo(cid, pt, best, c2c, tipo)

    def split_axis(box, p):
        lo, hi = box[p]
        m = lo + (hi - lo) / 2
        return dict(box, **{p: (lo, m)}), dict(box, **{p: (m, hi)})

    # ranking de ejes en la raíz (como M2r)
    a_r = time.time()
    score = []
    for p in COV.STRUCT:
        if root[p][1] > root[p][0]:
            hs = split_axis(root, p)
            cs = [c2_of(h) if COV.box_admissible(h, fixed) else None for h in hs]
            score.append((max((x.hi if x is not None else float("inf")) for x in cs), p))
    ejes = [p for _, p in sorted(score)[:3]]
    ranking_s = time.time() - a_r
    # sondeo de testigos en la raíz: centro y centros de las 6 caras de los 3 ejes del ranking
    cen = {p: (lo + (hi - lo) / 2,) * 2 for p, (lo, hi) in root.items()}
    sondear(cen, set(cand), "centro")
    for p in ejes:
        for v in root[p]:
            sondear(dict(cen, **{p: (v, v)}), set(cand), "cara")
    pend_final = {cid: [] for cid in cand}          # hojas terminales pendientes por afirmación (G.hi, volumen)
    full = {p: root[p][1] - root[p][0] for p in root}
    vol = lambda b: math.prod(((b[p][1] - b[p][0]) / full[p]) if full[p] > 0 else 1.0 for p in b)  # noqa: E731
    heap = [(0.0, 0, 0, root, frozenset(cand))]
    cont, hojas = 1, 0
    while heap:
        _, _, depth, b, act = heapq.heappop(heap)
        act = {c for c in act if estado[c] != "testigo"}
        if not act:
            continue
        if hojas >= max_hojas or time.time() - tb > seg:
            for c in act:
                pend_final[c].append((None, vol(b)))
            continue
        hojas += 1
        adm = COV.box_admissible(b, fixed)
        c2 = c2_of(b) if adm else None
        pend_, info = {}, {}
        for cid in act:
            if c2 is None:
                pend_[cid] = float("inf")
                continue
            ghi, glo, best = g_claim(b, cid, c2)
            if ghi is None:
                pend_[cid] = float("inf")
            elif ghi <= -EPS:
                continue
            elif glo > -EPS:
                testigo(cid, b, best, c2, "hoja")
            else:
                pend_[cid] = ghi
                info[cid] = [glo, ghi]
        q = COV.q_pot(b) if adm else None
        hoja_log(tarea=tarea, hoja=hojas, profundidad=depth, caja={p: list(v) for p, v in b.items()},
                 C2=None if c2 is None else [c2.lo, c2.hi], q_pot=None if q is None else [q.lo, q.hi],
                 activas=len(act), pendientes=len(pend_), G_pendientes=info)
        if pend_:
            cenb = {p: (lo + (hi - lo) / 2,) * 2 for p, (lo, hi) in b.items()}
            sondear(cenb, set(pend_), "centro")
            pend_ = {c: v for c, v in pend_.items() if estado[c] != "testigo"}
        if pend_:
            p = max(ejes, key=lambda e: (b[e][1] - b[e][0]) / full[e] if full[e] > 0 else 0.0) if ejes else None
            sub = split_axis(b, p) if (p and b[p][1] > b[p][0]) else COV._split(b)
            if not sub:
                for c, v in pend_.items():
                    pend_final[c].append((v, vol(b)))
                continue
            prio = -max(pend_.values())
            for s in sub:
                heapq.heappush(heap, (prio, cont, depth + 1, s, frozenset(pend_)))
                cont += 1
    res = {}
    for cid in cand:
        if estado[cid] == "testigo":
            res[cid] = {"estado": "testigo"}
        elif not pend_final[cid]:
            res[cid] = {"estado": "cerrada"}
        else:
            ghis = [v for v, _ in pend_final[cid] if v is not None]
            res[cid] = {"estado": "pendiente", "hojas_pendientes": len(pend_final[cid]),
                        "volumen_pendiente": sum(w for _, w in pend_final[cid]),
                        "max_G_hi_evaluado": max(ghis) if ghis else None, "mejor_G_lo_sondeado": mejor_lo[cid]}
    cnt = {k: sum(1 for v in res.values() if v["estado"] == k) for k in ("cerrada", "testigo", "pendiente")}
    return {"segundos": round(time.time() - tb, 3), "hojas": hojas, "encierros_pedidos": n_c2[0], "ranking_s": round(ranking_s, 2),
            "ejes": ejes, "conteo": cnt, "completa": cnt["pendiente"] == 0, "por_afirmacion": res}


def fichas(ctx, st, regs, doc, res_p, t0, tope):
    """Ficha y verificación de cada afirmación con posible testigo (mismo procedimiento que testigos.py)."""
    mejor = {}
    for w in regs:
        if w["afirmacion"] not in mejor or w["G"][0] > mejor[w["afirmacion"]]["G"][0]:
            mejor[w["afirmacion"]] = w
    V = Verificador(ctx, permitir_continuo=True)
    Vn = Verificador(ctx, permitir_continuo=False)
    inv_raw = (T.VAL / "audit/entrega.json").read_bytes()
    N.need(N.sha(inv_raw) == T.VAL_INV, "INVENTARIO_VALIDACION")
    raw = (T.VAL / "demo/R/evidencia_testigos.json").read_bytes()
    N.need(json.loads(inv_raw)["files"]["demo/R/evidencia_testigos.json"]["sha256"] == N.sha(raw), "R_NO_AUTENTICADA")
    R = json.loads(raw)["afirmaciones"]
    claims, U, corner = st["claims"], st["U"], st["corner"]
    for cid, w in sorted(mejor.items()):
        if time.time() - t0 > tope:
            doc["fichas"][cid] = {"estado_A": "candidato_no_verificado", "motivo": "TOPE_ANTES_DE_LA_FICHA", "testigo": w}
            continue
        cl = claims[cid]
        sid = w["conjunto"]
        r = V.run(sid)
        pt = {p: lo + (hi - lo) / 2 for p, (lo, hi) in w["caja"].items()} if "caja" in w else dict(w["punto"])
        vals = {p: Decimal(repr(float(pt[p]))) for p in RUNMOD.STRUCT}
        dbox = {p: (float(v), float(v)) for p, v in vals.items()}
        cx, fixed = U.contexts(cl, sid, corner)
        c2 = r.model.c2_struct_enclosure(dbox, cl.design, "f", float(fixed["bar_tau_d"]), float(fixed["bar_tau_f"]), fixed=fixed)
        g, c, bi = max(((COV.g_enclosure(r.model, dbox, c, fixed, c2), c, bi) for c, bi in cx), key=lambda t: t[0].lo)
        q = COV.q_pot(dbox)
        lam = c.s_pi / (1.0 - q)
        k1 = c.n_min / (lam * c.gain)
        ficha = {"flujo": "cobertura_dificiles_" + w["tipo"], "nudo": None, "conjunto": sid, "valores_estructurales": {p: str(v) for p, v in vals.items()},
                 **U.meta(cl, sid, corner, bi), "instrumento": c.instrument, "diseno": c.design, "cotas_fiscales": list(c.bars),
                 "contexto": {"s_pi": c.s_pi, "s_t": c.s_t, "eta_h": c.eta_h, "gain": c.gain, "n_min": c.n_min},
                 "q_pot": [q.lo, q.hi], "lambda": [lam.lo, lam.hi], "K1": [k1.lo, k1.hi],
                 "C2": {"lo": c2.lo, "hi": c2.hi, "metodo": "c2_struct_enclosure_punto", "estado": None,
                        "origen": {"tarea": w["tarea"], "tipo": w["tipo"], "t_registro": w["t"], "G_del_registro": w["G"]}},
                 "G": [g.lo, g.hi]}
        vA = V.verificar_completo(ficha, cl, "A")
        vP = V.verificar_completo(ficha, cl, "pos") if g.lo >= EPS else None
        base = R[cid]
        vB = Vn.verificar_completo(base["B"], cl, "B") if base.get("B") else None
        doc["fichas"][cid] = {"ficha": ficha, "testigo_registrado": w, "verificacion_A": vA, "verificacion_pos": vP,
                              "verificacion_B_nudo": vB, "G_lo": g.lo, "estado_A": "verificada" if vA["valida"] else "rechazada",
                              "estado_B": None if vB is None else ("verificada" if vB["valida"] else "rechazada")}
        N.write_json_atomic(res_p, doc)


def dirigido(dis, ks, out_dir, seg, max_hojas, tope):
    t0 = time.time()
    out_dir.mkdir(parents=True, exist_ok=True)
    ctx = N.Contexto()
    COV.q_pot = q_pot_exact
    pend_ids, reg_sha = MC.pendientes()
    st = T.preparar(ctx, dis, pend_ids)
    N.need(len(st["cand"]) == 42, "UNIVERSO_DISTINTO_DE_42")
    todas = cajas_dificiles()
    mias = [todas[k] for k in ks]
    fh = open(out_dir / f"testigos_{dis}.jsonl", "a", encoding="utf-8")
    fl = open(out_dir / f"hojas_{dis}.jsonl", "a", encoding="utf-8")

    def escritor(f):
        def w(**kw):
            kw["t"] = round(time.time() - t0, 2)
            f.write(json.dumps(kw, ensure_ascii=False, default=str) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return w
    log, hoja_log = escritor(fh), escritor(fl)
    res_p = out_dir / f"resultado_{dis}.json"
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "familia": dis, "identidad_sha256": ctx.identity_sha256, "registro_sha256": reg_sha,
           "universo": len(st["cand"]), "configuracion": {"metodo": "M3 dirigido (ver docstring)", "hojas_por_caja": max_hojas, "segundos_por_caja": seg},
           "preparacion_s": round(time.time() - t0, 1), "tareas": {}, "fichas": {}}
    memo = MEMO.Memo(True)
    for idx in mias:
        nombre = ",".join(map(str, idx))
        if nombre in doc["tareas"]:
            continue
        root = {p: st["axes"][p][i] for p, i in zip(COV.STRUCT, idx)}
        r = cubrir_dirigido(st, dis, root, memo, ctx.identity_sha256, log, hoja_log, nombre, seg, max_hojas)
        doc["tareas"][nombre] = dict(indices=list(idx), **r)
        doc["consumido_s"] = round(time.time() - t0, 1)
        N.write_json_atomic(res_p, doc)
    fh.close()
    fl.close()
    regs = [json.loads(x) for x in (out_dir / f"testigos_{dis}.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    doc["testigos_registrados"] = len(regs)
    fichas(ctx, st, regs, doc, res_p, t0, tope)
    doc["memo"] = {"pedidos": memo.pedidos, "calculados": memo.calculados, "reutilizados": memo.reutilizados}
    doc["consumido_s"] = round(time.time() - t0, 1)
    N.write_json_atomic(res_p, doc)
    print(json.dumps({"familia": dis, "tareas": {k: v["conteo"] for k, v in doc["tareas"].items()}, "testigos": len(regs),
                      "A_verificadas": sum(1 for x in doc["fichas"].values() if x.get("estado_A") == "verificada"), "s": doc["consumido_s"]},
                     ensure_ascii=False))


def medir(out, n_fac, semilla, ks_dif, tope):
    """M2r SIN CAMBIOS (muestra_costo.cubrir) con las 42 afirmaciones de cada familia."""
    t0 = time.time()
    ctx = N.Contexto()
    COV.q_pot = q_pot_exact
    pend_ids, reg_sha = MC.pendientes()
    plan = autenticado(CERT, CERT_INV, "demo/costo/plan.json")
    dif = cajas_dificiles()
    faciles = sorted({tuple(t["indices"]) for t in plan["tareas"]} - set(dif))
    sel = random.Random(semilla).sample(faciles, n_fac)
    tareas = [(d, t, "facil") for t in sel for d in ("G", "N")] + [(d, dif[k], "dificil") for k in ks_dif for d in ("G", "N")]
    sts = {d: MC.preparar(ctx, d, pend_ids) for d in ("G", "N")}
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "identidad_sha256": ctx.identity_sha256, "registro_sha256": reg_sha,
           "universo": {d: len(sts[d]["cand"]) for d in sts}, "semilla": semilla, "metodo": "M2r sin cambios (muestra_costo.cubrir)",
           "limites": {"hojas": MC.HOJAS, "segundos": MC.SEG_CAJA}, "preparacion_s": round(time.time() - t0, 1), "resultados": [], "no_procesadas": []}
    memo = MEMO.Memo(True)
    for d, idx, tipo in tareas:
        if time.time() - t0 > tope:
            doc["no_procesadas"].append([d, list(idx), tipo])
            continue
        root = {p: sts[d]["axes"][p][i] for p, i in zip(COV.STRUCT, idx)}
        r = MC.cubrir(sts[d], d, root, memo, MEMO, C2N, COV, ctx.identity_sha256)
        doc["resultados"].append(dict(familia=d, indices=list(idx), tipo=tipo, **r))
        doc["consumido_s"] = round(time.time() - t0, 1)
        N.write_json_atomic(Path(out), doc)
    doc["memo"] = {"pedidos": memo.pedidos, "calculados": memo.calculados, "reutilizados": memo.reutilizados}
    N.write_json_atomic(Path(out), doc)
    print(json.dumps({"resultados": len(doc["resultados"]), "no_procesadas": len(doc["no_procesadas"]), "s": round(time.time() - t0, 1)}))


def main():
    cmd = sys.argv[1]
    if cmd == "dirigido":
        dirigido(sys.argv[2], [int(x) for x in sys.argv[3].split(",")], Path(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6]), float(sys.argv[7]))
    elif cmd == "medir":
        medir(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), [int(x) for x in sys.argv[5].split(",") if x], float(sys.argv[6]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
