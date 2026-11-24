"""Cobertura M4 para las 40 afirmaciones pendientes del registro candidato v2 (RESOLUCIÓN 3.7, NO OFICIAL).

  <py_integracion> -m codigo.cobertura_m4 cajas <salida_dir> <seg_por_caja> <hojas> <tope_s> <i,j,...;i,j,...>
  <py_integracion> -m codigo.cobertura_m4 muestra <salida_dir> <seg_por_caja> <hojas> <tope_s> <n> <semilla> <parte> <de>

Universo: las 40 `candidata_sin_decision` de consolidacion_3_7/demo/registro/registro_candidato_v2.json (autenticado):
20 G y 20 N, todas del menú f (COL 24, MEX 16). Dominio, cuantificadores y ε SIN CAMBIOS (cobertura.g_enclosure, todos
los contextos de cada afirmación; cerrada en la hoja si max G.hi <= −ε; posible testigo si max G.lo > −ε).

Cambios respecto de M3 (cobertura_dificiles.py), motivados por el análisis de las hojas persistidas de la ronda anterior
(review/INFORME_REVISOR.md §2):
1. C2 COMPARTIDO G/N en el menú f. Con τ_d = 0 R(τ; θ, G) ≡ R(τ; θ, N) (model.trinomials con 1 − τ_d = 1 y
   cn = κ0 − kF = −κ0 φ τ_f; A solo entra en B_d multiplicado por τ_d; curvas de salto iguales), así que un encierro
   válido de C2(G, f) sobre una caja lo es de C2(N, f). Se calcula UNO por hoja (motor de G) y se evalúan con él las
   afirmaciones de ambas familias, cada una con SUS contextos, umbrales y K1 (no se comparten). En cada raíz se calcula
   además C2(N, f) con el motor de N y se registra la comparación (comprobación de la equivalencia).
2. RAÍZ PRIMERO: la raíz se evalúa antes de cualquier ranking (en M3 el ranking de 18 encierros consumió los 180 s de
   la caja (3,0,0,2,4,3,1,1,1) sin evaluarla).
3. RANKING POR G, no por C2: en las cajas difíciles C2.hi no baja al partir ningún eje (el máximo de C2 está en una
   esquina) y M3 elegía ejes por orden alfabético; lo que impide cerrar es la dependencia G.hi = máx C2 − mín K1 con
   K1 = κ_c (1 − q_pot(κ̃, a, ρ)). Puntaje de un eje = (máx sobre afirmaciones pendientes del máx sobre las dos hijas de
   G.hi, media de lo mismo), con el C2 y la K1 (q_pot exacto) de CADA hija; se eligen los 3 mejores.
4. Por hoja: eje de mayor anchura relativa entre los 3; orden mejor-primero por max G.hi pendiente; sondeo del centro.
Persistencia: hojas y posibles testigos al instante (JSONL + fsync); resultado tras cada caja; la reanudación salta las
cajas ya registradas. `muestra`: cajas L0 NUEVAS (no evaluadas antes en la muestra de costo ni entre las difíciles),
selección aleatoria simple con semilla declarada, para medir el costo de la carga pendiente real.
"""
from __future__ import annotations

import heapq
import json
import math
import os
import random
import sys
import time
from pathlib import Path

from codigo import muestra_costo as MC
from codigo import testigos as T
from codigo import cobertura_dificiles as CD
from codigo.demo import nucleo_v as N
from codigo.demo import c2_normalizado as C2N
from codigo.demo import memo_c2 as MEMO
from codigo.demo.cobertura_compartida import q_pot_exact
from paper2b import claims as CL
from paper2b import cobertura as COV

EPS = CL.EPS_ECON
CONS = N.ROOT / "tmp/consolidacion_3_7_2026-10-04"
CONS_INV = "1b3a62bc9baa452b71e11597c70d18576ba622583e03400bc5432b243fb9d0bc"
REG_REL = "demo/registro/registro_candidato_v2.json"


def pendientes_v2():
    reg = CD.autenticado(CONS, CONS_INV, REG_REL)
    raw = (CONS / REG_REL).read_bytes()
    return sorted(c for c, v in reg["afirmaciones"].items() if v["categoria"] == "candidata_sin_decision"), N.sha(raw)


def preparar(ctx):
    COV.q_pot = q_pot_exact
    pend, reg_sha = pendientes_v2()
    N.need(len(pend) == 40, "UNIVERSO_DISTINTO_DE_40")
    sts = {d: T.preparar(ctx, d, pend) for d in ("G", "N")}
    N.need(all(len(sts[d]["cand"]) == 20 for d in sts), "NO_20_POR_FAMILIA")
    N.need(sts["G"]["fixed"] == sts["N"]["fixed"] and sts["G"]["axes"] == sts["N"]["axes"], "FIJOS_O_EJES_DISTINTOS_G_N")
    return sts, pend, reg_sha


def cubrir_m4(sts, root, memo, ident, log, hoja_log, tarea, seg, max_hojas):
    stG = sts["G"]
    model, fixed = stG["model"], stG["fixed"]
    bd, bf = float(fixed["bar_tau_d"]), float(fixed["bar_tau_f"])
    claims = [(d, cid) for d in ("G", "N") for cid in sts[d]["cand"]]
    n_c2 = [0]
    tb = time.time()

    def c2_of(b, dis="G"):
        n_c2[0] += 1
        k = MEMO.clave(b, dis, "f", bd, bf, fixed, model, "normalizado", ident)
        return memo.obtener(k, lambda: C2N.c2_normalizado(model, b, dis, "f", bd, bf, fixed=fixed), b)

    estado = {c: "pendiente" for c in claims}
    mejor_lo = {c: -1e300 for c in claims}

    def g_claim(b, c, c2):
        d, cid = c
        st = sts[d]
        ghi, glo, best = -1e300, -1e300, None
        for k, cx in enumerate(st["univ"][cid]):
            g = COV.g_enclosure(st["model"], b, cx, fixed, c2)
            if g is None:
                return None, None, None
            if g.lo > glo:
                best = (k, g)
            ghi, glo = max(ghi, g.hi), max(glo, g.lo)
        return ghi, glo, best

    def testigo(c, b, best, c2, tipo):
        d, cid = c
        st = sts[d]
        k, g = best
        cx = st["univ"][cid][k]
        k1 = T.k1_de(b, cx)
        estado[c] = "testigo"
        rec = dict(tarea=tarea, familia=d, afirmacion=cid, tipo=tipo, conjunto=st["meta"][cid][k][0], indice_contexto_nacional=st["meta"][cid][k][1],
                   indice_contexto=k, contexto=T._ctx(cx), nacional=T._nac(st, cid, st["meta"][cid][k][0], st["meta"][cid][k][1]),
                   C2=[c2.lo, c2.hi], C2_compartido_desde="G", K1=[k1.lo, k1.hi], G=[g.lo, g.hi])
        rec["caja" if tipo == "hoja" else "punto"] = {p: (list(v) if tipo == "hoja" else v[0]) for p, v in b.items()}
        log(**rec)

    def evaluar(b, act):
        """(cerradas, pendientes {c: G.hi}, info) en la hoja b para las afirmaciones activas."""
        adm = COV.box_admissible(b, fixed)
        c2 = c2_of(b) if adm else None
        pend_, info, cerr = {}, {}, []
        for c in act:
            if c2 is None:
                pend_[c] = math.inf
                continue
            ghi, glo, best = g_claim(b, c, c2)
            if ghi is None:
                pend_[c] = math.inf
            elif ghi <= -EPS:
                cerr.append(c)
            elif glo > -EPS:
                testigo(c, b, best, c2, "hoja")
            else:
                pend_[c] = ghi
                info["%s|%s" % c] = [glo, ghi]
        return c2, cerr, pend_, info

    def sondear(pt, act):
        if not COV.box_admissible(pt, fixed):
            return
        c2c = c2_of(pt)
        if c2c is None:
            return
        for c in act:
            if estado[c] == "testigo":
                continue
            ghi, glo, best = g_claim(pt, c, c2c)
            if glo is not None:
                mejor_lo[c] = max(mejor_lo[c], glo)
                if glo > -EPS:
                    testigo(c, pt, best, c2c, "centro")

    def half(box, p):
        lo, hi = box[p]
        m = lo + (hi - lo) / 2
        return dict(box, **{p: (lo, m)}), dict(box, **{p: (m, hi)})
    full = {p: root[p][1] - root[p][0] for p in root}
    vol = lambda b: math.prod(((b[p][1] - b[p][0]) / full[p]) if full[p] > 0 else 1.0 for p in b)  # noqa: E731
    # 1) raíz primero (y comprobación de la equivalencia G/N en la raíz)
    c2r, cerr, pend_, info = evaluar(root, set(claims))
    c2N = c2_of(root, "N") if COV.box_admissible(root, fixed) else None
    equiv = {"C2_G": None if c2r is None else [c2r.lo, c2r.hi], "C2_N": None if c2N is None else [c2N.lo, c2N.hi]}
    equiv["se_intersecan"] = (c2r is not None and c2N is not None and max(c2r.lo, c2N.lo) <= min(c2r.hi, c2N.hi))
    hojas = 1
    hoja_log(tarea=tarea, hoja=1, profundidad=0, caja={p: list(v) for p, v in root.items()}, C2=equiv["C2_G"], C2_N=equiv["C2_N"],
             pendientes=len(pend_), G_pendientes=info)
    pend_final = {c: [] for c in claims}
    ejes, ranking, ranking_s = [], [], 0.0
    if pend_:
        cen = {p: (lo + (hi - lo) / 2,) * 2 for p, (lo, hi) in root.items()}
        sondear(cen, set(pend_))
        pend_ = {c: v for c, v in pend_.items() if estado[c] != "testigo"}
    if pend_:
        # 2) ranking por G (no por C2): hijas de cada eje con su C2 y su K1
        a_r = time.time()
        for p in COV.STRUCT:
            if root[p][1] <= root[p][0]:
                continue
            peor = {c: -math.inf for c in pend_}
            for h in half(root, p):
                c2h = c2_of(h) if COV.box_admissible(h, fixed) else None
                for c in pend_:
                    ghi = g_claim(h, c, c2h)[0] if c2h is not None else None
                    peor[c] = max(peor[c], math.inf if ghi is None else ghi)
            vals = list(peor.values())
            ranking.append((max(vals), sum(vals) / len(vals), p))
            if time.time() - tb > seg:
                break
        ranking.sort()
        ejes = [p for _, _, p in ranking[:3]]
        ranking_s = time.time() - a_r
        heap = []
        cont = 0
        prio = -max(pend_.values())
        p = max(ejes, key=lambda e: (root[e][1] - root[e][0]) / full[e]) if ejes else None
        for s in (half(root, p) if p else (COV._split(root) or [])):
            heapq.heappush(heap, (prio, cont, 1, s, frozenset(pend_)))
            cont += 1
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
            c2, cerr_b, pb, inf_b = evaluar(b, act)
            hoja_log(tarea=tarea, hoja=hojas, profundidad=depth, caja={q: list(v) for q, v in b.items()}, C2=None if c2 is None else [c2.lo, c2.hi],
                     pendientes=len(pb), G_pendientes=inf_b)
            if pb:
                cenb = {q: (lo + (hi - lo) / 2,) * 2 for q, (lo, hi) in b.items()}
                sondear(cenb, set(pb))
                pb = {c: v for c, v in pb.items() if estado[c] != "testigo"}
            if not pb:
                continue
            q = max(ejes, key=lambda e: (b[e][1] - b[e][0]) / full[e] if full[e] > 0 else 0.0) if ejes else None
            sub = half(b, q) if (q and b[q][1] > b[q][0]) else COV._split(b)
            if not sub:
                for c, v in pb.items():
                    pend_final[c].append((v, vol(b)))
                continue
            for s in sub:
                heapq.heappush(heap, (-max(pb.values()), cont, depth + 1, s, frozenset(pb)))
                cont += 1
    res = {}
    for c in claims:
        k = "%s|%s" % c
        if estado[c] == "testigo":
            res[k] = {"estado": "testigo"}
        elif not pend_final[c] and c not in pend_:
            res[k] = {"estado": "cerrada"}
        elif not pend_final[c]:
            res[k] = {"estado": "cerrada"}
        else:
            ghis = [v for v, _ in pend_final[c] if v is not None]
            res[k] = {"estado": "pendiente", "hojas_pendientes": len(pend_final[c]), "volumen_pendiente": sum(w for _, w in pend_final[c]),
                      "max_G_hi_evaluado": max(ghis) if ghis else None, "mejor_G_lo_sondeado": mejor_lo[c]}
    cnt = {(d, k): sum(1 for c, v in res.items() if c.startswith(d + "|") and v["estado"] == k) for d in ("G", "N") for k in ("cerrada", "testigo", "pendiente")}
    return {"segundos": round(time.time() - tb, 3), "hojas": hojas, "encierros_pedidos": n_c2[0], "ranking_s": round(ranking_s, 2),
            "ranking": [[a, b_, p] for a, b_, p in ranking], "ejes": ejes, "equivalencia_raiz": equiv,
            "conteo": {"%s:%s" % k: v for k, v in cnt.items()}, "completa": all(v["estado"] != "pendiente" for v in res.values()),
            "por_afirmacion": res}


def correr(out_dir, cajas, seg, max_hojas, tope, meta):
    t0 = time.time()
    out_dir.mkdir(parents=True, exist_ok=True)
    ctx = N.Contexto()
    sts, pend, reg_sha = preparar(ctx)
    res_p = out_dir / "resultado.json"
    doc = json.loads(res_p.read_text(encoding="utf-8")) if res_p.exists() else {
        "etiqueta": N.ETIQUETA, "no_exportable": True, "identidad_sha256": ctx.identity_sha256, "registro_v2_sha256": reg_sha,
        "universo": {"G": 20, "N": 20}, "configuracion": {"metodo": "M4 (ver docstring)", "segundos_por_caja": seg, "hojas_por_caja": max_hojas},
        "seleccion": meta, "tareas": {}, "fichas": {}}
    N.need(doc["identidad_sha256"] == ctx.identity_sha256, "REANUDACION_CON_OTRA_IDENTIDAD")
    doc["preparacion_s"] = round(time.time() - t0, 1)
    fh = open(out_dir / "testigos.jsonl", "a", encoding="utf-8")
    fl = open(out_dir / "hojas.jsonl", "a", encoding="utf-8")

    def escritor(f):
        def w(**kw):
            kw["t"] = round(time.time() - t0, 2)
            f.write(json.dumps(kw, ensure_ascii=False, default=str) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return w
    log, hoja_log = escritor(fh), escritor(fl)
    memo = MEMO.Memo(True)
    for idx in cajas:
        nombre = ",".join(map(str, idx))
        if nombre in doc["tareas"]:
            continue
        if time.time() - t0 > tope:
            doc.setdefault("no_procesadas_por_tope", []).append(list(idx))
            continue
        root = {p: sts["G"]["axes"][p][i] for p, i in zip(COV.STRUCT, idx)}
        r = cubrir_m4(sts, root, memo, ctx.identity_sha256, log, hoja_log, nombre, seg, max_hojas)
        doc["tareas"][nombre] = dict(indices=list(idx), **r)
        doc["consumido_s"] = round(time.time() - t0, 1)
        N.write_json_atomic(res_p, doc)
    fh.close()
    fl.close()
    regs = [json.loads(x) for x in (out_dir / "testigos.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    doc["testigos_registrados"] = len(regs)
    for d in ("G", "N"):
        rd = [w for w in regs if w["familia"] == d]
        if rd:
            sub = {"fichas": {}}
            CD.fichas(ctx, sts[d], rd, sub, out_dir / f"fichas_{d}.json", t0, tope)
            doc["fichas"].update(sub["fichas"])
    doc["memo"] = {"pedidos": memo.pedidos, "calculados": memo.calculados, "reutilizados": memo.reutilizados}
    doc["consumido_s"] = round(time.time() - t0, 1)
    N.write_json_atomic(res_p, doc)
    print(json.dumps({"tareas": {k: v["conteo"] for k, v in doc["tareas"].items()}, "testigos": len(regs), "s": doc["consumido_s"]}, ensure_ascii=False))


def global_soporte(out_dir, seg, max_hojas, tope):
    """COBERTURA GLOBAL del soporte (M5): la raíz es la caja COMPLETA del soporte estructural (producto de los ejes,
    igual a la unión de las 81 920 cajas L0) y el universo, las afirmaciones que siguen sin decisión en el registro
    candidato v3 de esta área (16, MEX). Misma rutina que M4 (cubrir_m4: C2 compartido G/N, raíz primero, ranking por
    G, mejor primero). Si todas las hojas terminales cierran una afirmación (max G.hi <= −ε en todos sus contextos),
    sup G + err <= −ε en TODO el universo: veredicto `robust_infeasible` de claims.evaluate (universo completo)."""
    t0 = time.time()
    out_dir.mkdir(parents=True, exist_ok=True)
    ctx = N.Contexto()
    COV.q_pot = q_pot_exact
    v3p = N.AREA / "demo/registro/registro_candidato_v3.json"
    raw = v3p.read_bytes()
    pend = sorted(c for c, v in json.loads(raw)["afirmaciones"].items() if v["categoria"] == "candidata_sin_decision")
    sts = {d: T.preparar(ctx, d, pend) for d in ("G", "N")}
    N.need(sts["G"]["fixed"] == sts["N"]["fixed"] and sts["G"]["axes"] == sts["N"]["axes"], "FIJOS_O_EJES_DISTINTOS_G_N")
    axes = sts["G"]["axes"]
    root = {p: (axes[p][0][0], axes[p][-1][1]) for p in COV.STRUCT}
    fl = open(out_dir / "hojas.jsonl", "a", encoding="utf-8")
    ft = open(out_dir / "testigos.jsonl", "a", encoding="utf-8")

    def escritor(f):
        def w(**kw):
            kw["t"] = round(time.time() - t0, 2)
            f.write(json.dumps(kw, ensure_ascii=False, default=str) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return w
    memo = MEMO.Memo(True)
    r = cubrir_m4(sts, root, memo, ctx.identity_sha256, escritor(ft), escritor(fl), "soporte_completo", seg, max_hojas)
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "identidad_sha256": ctx.identity_sha256, "registro_v3_sha256": N.sha(raw),
           "universo": {d: len(sts[d]["cand"]) for d in sts}, "raiz": {p: list(v) for p, v in root.items()},
           "configuracion": {"metodo": "M5 = M4 sobre el soporte completo", "segundos": seg, "hojas": max_hojas}, "resultado": r,
           "veredicto_por_afirmacion": {k: ("robust_infeasible (cobertura completa, max G.hi <= -eps en todo el soporte y contextos)"
                                            if v["estado"] == "cerrada" else v["estado"]) for k, v in r["por_afirmacion"].items()},
           "memo": {"pedidos": memo.pedidos, "calculados": memo.calculados, "reutilizados": memo.reutilizados},
           "segundos": round(time.time() - t0, 1)}
    N.write_json_atomic(out_dir / "resultado.json", doc)
    print(json.dumps({"conteo": r["conteo"], "hojas": r["hojas"], "encierros": r["encierros_pedidos"], "s": doc["segundos"]}))


def vertices(out_dir, caja, tope):
    """SONDEO DE VÉRTICES (testigos): los 2^9 vértices de la caja, con C2 puntual compartido G/N y G de cada afirmación
    pendiente en todos sus contextos. Orden: primero los vértices con κ̃, ρ y a en su máximo (q_pot máximo, K1 mínimo).
    Un vértice con max G.lo > −ε es POSIBLE testigo (se verifica después con ficha); los demás informan el máximo de G
    en vértices (no es cota del supremo: solo dice dónde está G)."""
    import itertools
    t0 = time.time()
    out_dir.mkdir(parents=True, exist_ok=True)
    ctx = N.Contexto()
    sts, pend, reg_sha = preparar(ctx)
    root = {p: sts["G"]["axes"][p][i] for p, i in zip(COV.STRUCT, caja)}
    fixed = sts["G"]["fixed"]
    model = sts["G"]["model"]
    bd, bf = float(fixed["bar_tau_d"]), float(fixed["bar_tau_f"])
    claims = [(d, cid) for d in ("G", "N") for cid in sts[d]["cand"]]
    fh = open(out_dir / "vertices.jsonl", "a", encoding="utf-8")
    ft = open(out_dir / "testigos.jsonl", "a", encoding="utf-8")

    def esc(f, **kw):
        kw["t"] = round(time.time() - t0, 2)
        f.write(json.dumps(kw, ensure_ascii=False, default=str) + "\n")
        f.flush()
        os.fsync(f.fileno())
    pri ={"kappa_tilde": 1, "rho": 1, "a": 1}
    orden = sorted(itertools.product((0, 1), repeat=len(COV.STRUCT)),
                   key=lambda bits: -sum(1 for p, b_ in zip(COV.STRUCT, bits) if pri.get(p) == b_))
    mejor = {c: (-1e300, None) for c in claims}
    hechos, testigos = 0, set()
    for bits in orden:
        if time.time() - t0 > tope:
            break
        pt = {p: (root[p][b_], root[p][b_]) for p, b_ in zip(COV.STRUCT, bits)}
        if not COV.box_admissible(pt, fixed):
            continue
        c2 = C2N.c2_normalizado(model, pt, "G", "f", bd, bf, fixed=fixed)
        hechos += 1
        fila = {}
        for c in claims:
            d, cid = c
            st = sts[d]
            gs = [(k, COV.g_enclosure(st["model"], pt, cx, fixed, c2)) for k, cx in enumerate(st["univ"][cid])]
            gs = [(k, g) for k, g in gs if g is not None]
            if not gs:
                continue
            k, g = max(gs, key=lambda t: t[1].lo)
            fila["%s|%s" % c] = [g.lo, g.hi]
            if g.lo > mejor[c][0]:
                mejor[c] = (g.lo, list(bits))
            if g.lo > -EPS and c not in testigos:
                testigos.add(c)
                cx = st["univ"][cid][k]
                k1 = T.k1_de(pt, cx)
                esc(ft, tarea=",".join(map(str, caja)), familia=d, afirmacion=cid, tipo="vertice", conjunto=st["meta"][cid][k][0],
                    indice_contexto_nacional=st["meta"][cid][k][1], indice_contexto=k, contexto=T._ctx(cx),
                    nacional=T._nac(st, cid, st["meta"][cid][k][0], st["meta"][cid][k][1]), punto={p: v[0] for p, v in pt.items()},
                    C2=[c2.lo, c2.hi], C2_compartido_desde="G", K1=[k1.lo, k1.hi], G=[g.lo, g.hi])
        esc(fh, bits=list(bits), C2=[c2.lo, c2.hi], G=fila)
    fh.close()
    ft.close()
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "identidad_sha256": ctx.identity_sha256, "caja": list(caja), "vertices_evaluados": hechos,
           "afirmaciones": {"%s|%s" % c: {"max_G_lo_en_vertices": v[0], "vertice": v[1]} for c, v in mejor.items()},
           "posibles_testigos": len(testigos), "fichas": {}}
    regs = [json.loads(x) for x in (out_dir / "testigos.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    for d in ("G", "N"):
        rd = [w for w in regs if w["familia"] == d]
        if rd:
            sub = {"fichas": {}}
            CD.fichas(ctx, sts[d], rd, sub, out_dir / f"fichas_{d}.json", t0, tope + 300)
            doc["fichas"].update(sub["fichas"])
    doc["segundos"] = round(time.time() - t0, 1)
    N.write_json_atomic(out_dir / "resultado.json", doc)
    print(json.dumps({"caja": list(caja), "vertices": hechos, "posibles_testigos": len(testigos),
                      "A_verificadas": sum(1 for x in doc["fichas"].values() if x.get("estado_A") == "verificada"),
                      "pos": sum(1 for x in doc["fichas"].values() if (x.get("verificacion_pos") or {}).get("valida")), "s": doc["segundos"]}))


def main():
    if sys.argv[1] == "global":
        global_soporte(Path(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]))
        return 0
    if sys.argv[1] == "vertices":
        vertices(Path(sys.argv[2]), tuple(int(x) for x in sys.argv[3].split(",")), float(sys.argv[4]))
        return 0
    cmd, out_dir, seg, hojas, tope = sys.argv[1], Path(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5])
    if cmd == "cajas":
        cajas = [tuple(int(x) for x in s.split(",")) for s in sys.argv[6].split(";")]
        meta = {"tipo": "cajas declaradas", "cajas": [list(c) for c in cajas]}
    else:
        n, semilla, parte, de = int(sys.argv[6]), int(sys.argv[7]), int(sys.argv[8]), int(sys.argv[9])
        plan = CD.autenticado(CD.CERT, CD.CERT_INV, "demo/costo/plan.json")
        usadas = {tuple(t["indices"]) for t in plan["tareas"]} | set(CD.cajas_dificiles())
        radices = plan["radices"]
        rad = [radices[p] for p in COV.STRUCT]
        rng = random.Random(semilla)
        sel = []
        while len(sel) < n:
            t = tuple(rng.randrange(r) for r in rad)
            if t not in usadas and t not in sel:
                sel.append(t)
        cajas = sel[parte::de]
        meta = {"tipo": "muestra aleatoria simple de cajas L0 NUEVAS", "n": n, "semilla": semilla, "parte": parte, "de": de,
                "excluidas": "las 40 de la muestra de costo y las 5 difíciles", "cajas": [list(c) for c in cajas]}
    correr(out_dir, cajas, seg, hojas, tope, meta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
