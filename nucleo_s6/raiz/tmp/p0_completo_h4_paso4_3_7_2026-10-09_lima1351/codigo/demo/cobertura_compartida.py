"""3.7.2 — cobertura compartida de las candidatas del menú f (OBSTÁCULOS 3.7, NO OFICIAL; copia de validacion_testigos_3_7 con
M2r, selección de cajas, subconjunto de afirmaciones y registro de testigos; M1 y M2 sin cambios de lógica).

  <py_integracion> -m codigo.demo.cobertura_compartida <M1|M2|M2r> <salida.json> <tope_cooperativo_s>
      [--desde i --hasta j] [--dificiles n] [--faciles m] [--solo <archivo de claim_ids>]
- M2r: igual que M2, pero evalúa primero la caja raíz y solo paga la mirada adelante si la raíz no resuelve todas las
  afirmaciones (mismas hojas, mismo orden y mismas particiones que M2 en cuanto la raíz no cierra).

- Cajas: pendientes de P3b en el orden de su checkpoint (las 9 de N3/N4 primero, luego las siguientes).
- Afirmaciones: las 82 candidatas de diseño G y menú f de la ronda anterior (cada una con su universo completo).
- Por hoja: UN encierro de C2(G, f) compartido por todas las afirmaciones cuyos fijos coinciden; por afirmación,
  G = C2 - K1 en todos sus contextos. Hoja cerrada para la afirmación si max G.hi <= -eps; testigo si max G.lo > -eps
  (en la hoja: todo punto es testigo; o en el centro de la hoja: sondeo puntual).
- M1: partición por el eje relativo más ancho (cobertura._split). M2: partición dirigida (mirada adelante de un nivel en
  la caja L0: por eje, máximo de C2.hi de las dos mitades; ciclo por los 3 ejes que más lo reducen).
- q_pot exacto por vértices cuando a>1, a>rho, rho<=1, kappa>0 (si no, el ingenuo). Nada pendiente se declara cerrado.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from collections import deque
from decimal import Decimal
from pathlib import Path

from . import nucleo_v as N
from .universo import Universo, qmin_table
from paper2b import claims as CL
from paper2b import cobertura as COV
from paper2b import run as RUNMOD
from paper2b.intervalos import Iv

EPS = CL.EPS_ECON
NAIVE = COV.q_pot
V = N.ROOT / "tmp/viabilidad_alternativa_2026-10-03"
P3B_REL = "pilotos/P3/P3-PREG-PER-APLICACION-E0E3_P3b.parcial.json"
PIL = N.ROOT / "tmp/pilotos_b36_b37_2026-10-02"
CLAIM_P3B = "CLM:PREG-PER-APLICACION-E0E3:primary:ci:PER:f:conditional_full:G:sin_addback:micro:guardrail_deuda"
HOJAS, SEG_CAJA = 64, 180.0
DIS = sys.argv[sys.argv.index("--diseno") + 1] if "--diseno" in sys.argv else "G"   # familia (G por defecto)
if "--sin-tope-tiempo" in sys.argv:          # adenda 1: tope determinista solo por hojas (64), sin tope de reloj por caja
    SEG_CAJA = float("inf")


def q_pot_exact(box):
    a, rho, k = box["a"], box["rho"], box["kappa_tilde"]
    if not (a[0] > 1.0 and rho[1] <= 1.0 and a[0] - rho[1] > 0 and k[0] > 0):
        return NAIVE(box)
    lo = NAIVE({"a": (a[0], a[0]), "rho": (rho[0], rho[0]), "kappa_tilde": (k[0], k[0])}).lo
    hi = NAIVE({"a": (a[1], a[1]), "rho": (rho[1], rho[1]), "kappa_tilde": (k[1], k[1])}).hi
    return Iv(lo, hi)


def autenticados():
    inv = json.loads((V / "audit/entrega.json").read_bytes())
    raw = (V / "demo/analisis/analisis_final.json").read_bytes()
    N.need(inv["files"]["demo/analisis/analisis_final.json"]["sha256"] == hashlib.sha256(raw).hexdigest(), "ANALISIS_NO_AUTENTICADO")
    cand = json.loads(raw)["candidatas"]
    pinv = json.loads((PIL / "audit/entrega.json").read_bytes())
    praw = (PIL / P3B_REL).read_bytes()
    N.need(pinv["files"][P3B_REL]["sha256"] == hashlib.sha256(praw).hexdigest(), "P3B_NO_AUTENTICADO")
    return cand, json.loads(praw)["cajas"]


def split_axis(box, p):
    lo, hi = box[p]
    m = lo + (hi - lo) / 2
    return dict(box, **{p: (lo, m)}), dict(box, **{p: (m, hi)})


def main():
    metodo, out, budget = sys.argv[1], Path(sys.argv[2]), float(sys.argv[3])
    t0 = time.time()
    ctx = N.Contexto()
    COV.q_pot = q_pot_exact
    cand_all, p3b = autenticados()
    cand = sorted(c for c in cand_all if f":{DIS}:" in c and ":ci:" in c and c.split(":")[5] == "f")
    if "--solo" in sys.argv:
        solo = set(Path(sys.argv[sys.argv.index("--solo") + 1]).read_text(encoding="utf-8").split())
        cand = [c for c in cand if c in solo]
        N.need(cand and len(cand) == len(solo), "SOLO_FUERA_DE_LAS_CANDIDATAS")
    claims = {c.claim_id: c for c in ctx.claims}
    sets = sorted({s for cid in cand for s in claims[cid].support_sets})
    runs = {sid: ctx.run(sid, "cob:" + sid) for sid in sets}
    ref_sid = claims[CLAIM_P3B].support_sets[0]
    if ref_sid not in runs:
        runs[ref_sid] = ctx.run(ref_sid, "cob:" + ref_sid)
    axes = runs[ref_sid].struct_axes(ref_sid)
    N.need(all(runs[s].struct_axes(s) == axes for s in runs), "EJES_DISTINTOS_NO_SE_COMPARTE")
    ax0 = N.axes_nodes(ctx, ref_sid)
    corner = {p: Decimal(str(ax0[p][0])) for p in RUNMOD.STRUCT}
    U = Universo(runs, qmin_table(ctx.inp.grid_cells))
    univ, fixed_ref = {}, None
    compartir = {}
    for cid in cand:
        cl = claims[cid]
        cx = []
        for sid in cl.support_sets:
            c, fx = U.contexts(cl, sid, corner)
            cx += [x for x, _ in c]
            fixed_ref = fixed_ref or fx
            compartir.setdefault(json.dumps(fx, sort_keys=True, default=str), []).append(cid)
        univ[cid] = cx
    N.need(len(compartir) == 1, "FIJOS_DISTINTOS: no se comparte C2 entre afirmaciones con fijos distintos")
    fixed = fixed_ref
    model = runs[ref_sid].model
    bd, bf = float(fixed["bar_tau_d"]), float(fixed["bar_tau_f"])
    pend = [k for _, k in sorted((v["orden"], k) for k, v in p3b.items() if v["clase"] == "pending")]
    # adenda 1: --desde i --hasta j limita a las cajas pendientes de índices [i, j) en el mismo orden (completar las 9 de N3/N4)
    if "--desde" in sys.argv:
        i, j = int(sys.argv[sys.argv.index("--desde") + 1]), int(sys.argv[sys.argv.index("--hasta") + 1])
        pend = pend[i:j]
    if "--dificiles" in sys.argv or "--faciles" in sys.argv:
        nd = int(sys.argv[sys.argv.index("--dificiles") + 1]) if "--dificiles" in sys.argv else 0
        nf = int(sys.argv[sys.argv.index("--faciles") + 1]) if "--faciles" in sys.argv else 0
        faciles = [k for _, k in sorted((v["orden"], k) for k, v in p3b.items() if v["clase"] == "infeasible")][:nf]
        pend = pend[:nd] + faciles
    if "--trabajador" in sys.argv:          # escalamiento: reparto determinista por turnos (cajas i, i+n, i+2n, ...)
        i_t, n_t = int(sys.argv[sys.argv.index("--trabajador") + 1]), int(sys.argv[sys.argv.index("--de") + 1])
        pend = pend[i_t::n_t]
    tipo_caja = {k: p3b[k]["clase"] for k in pend}
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "metodo": metodo, "identidad_sha256": ctx.identity_sha256,
           "afirmaciones": cand, "n_afirmaciones": len(cand), "contextos_por_afirmacion": {c: len(v) for c, v in univ.items()},
           "compartido": {"clave": "diseño G, menú f, cotas y fijos idénticos; ejes idénticos entre conjuntos", "grupos_de_fijos": len(compartir)},
           "preparacion_s": round(time.time() - t0, 1), "cajas": [], "parada": None}
    n_c2 = [0]
    testigos = {}
    doc["testigos"] = testigos

    def c2_of(b):
        n_c2[0] += 1
        return model.c2_struct_enclosure(b, DIS, "f", bd, bf, fixed=fixed)

    def eval_leaf(b, activos, c2):
        cerr, test, pend_ = set(), set(), set()
        for cid in activos:
            ghi, glo = -1e300, -1e300
            for c in univ[cid]:
                g = COV.g_enclosure(model, b, c, fixed, c2)
                if g is None:
                    ghi = glo = None
                    break
                ghi, glo = max(ghi, g.hi), max(glo, g.lo)
            if ghi is None:
                pend_.add(cid)
            elif ghi <= -EPS:
                cerr.add(cid)
            elif glo > -EPS:
                test.add(cid)
            else:
                pend_.add(cid)
        return cerr, test, pend_

    for key in pend:
        if time.time() - t0 > budget:
            doc["parada"] = "TOPE_COOPERATIVO"
            break
        tb = time.time()
        idx = [int(t) for t in key.split("|")[1].split(",")]
        root = {p: axes[p][i] for p, i in zip(COV.STRUCT, idx)}
        orden_ejes = None
        ranking_s = 0.0
        if metodo == "M2":
            score = []
            for p in COV.STRUCT:
                if root[p][1] > root[p][0]:
                    halves = split_axis(root, p)
                    cs = [c2_of(h) if COV.box_admissible(h, fixed) else None for h in halves]
                    score.append((max((x.hi if x is not None else float("inf")) for x in cs), p))
            orden_ejes = [p for _, p in sorted(score)[:3]]
            ranking_s = time.time() - tb
        estado = {cid: "pendiente" for cid in cand}
        hojas_pend = {cid: 0 for cid in cand}
        q = deque([(root, set(cand), 0)])
        hojas = 0
        while q:
            b, act, depth = q.popleft()
            act = {c for c in act if estado[c] != "testigo"}
            if not act:
                continue
            hojas += 1
            if not COV.box_admissible(b, fixed):
                pend_ = set(act)
                cerr, test = set(), set()
            else:
                c2 = c2_of(b)
                cerr, test, pend_ = eval_leaf(b, act, c2) if c2 is not None else (set(), set(), set(act))
            for c in test:
                estado[c] = "testigo"
                testigos.setdefault(c, {"tipo": "hoja", "caja_l0": key, "hoja": {p: list(v) for p, v in b.items()},
                                        "punto": {p: (lo + (hi - lo) / 2) for p, (lo, hi) in b.items()}})
            if pend_:
                cen = {p: (lo + (hi - lo) / 2,) * 2 for p, (lo, hi) in b.items()}
                if COV.box_admissible(cen, fixed):
                    c2c = c2_of(cen)
                    if c2c is not None:
                        for cid in list(pend_):
                            if any(g is not None and g.lo > -EPS for g in (COV.g_enclosure(model, cen, c, fixed, c2c) for c in univ[cid])):
                                estado[cid] = "testigo"
                                pend_.discard(cid)
                                testigos.setdefault(cid, {"tipo": "centro", "caja_l0": key, "punto": {p: v[0] for p, v in cen.items()}})
            if pend_:
                if hojas + len(q) + 2 <= HOJAS and time.time() - tb < SEG_CAJA:
                    if metodo == "M2r" and orden_ejes is None and depth == 0:
                        a_r = time.time()            # M2r: la raíz no resolvió todo; recién ahora se paga la mirada adelante
                        score = []
                        for p in COV.STRUCT:
                            if root[p][1] > root[p][0]:
                                halves = split_axis(root, p)
                                cs = [c2_of(h) if COV.box_admissible(h, fixed) else None for h in halves]
                                score.append((max((x.hi if x is not None else float("inf")) for x in cs), p))
                        orden_ejes = [p for _, p in sorted(score)[:3]]
                        ranking_s = time.time() - a_r
                    if metodo in ("M2", "M2r") and orden_ejes:
                        p = orden_ejes[depth % len(orden_ejes)]
                        sub = split_axis(b, p) if b[p][1] > b[p][0] else COV._split(b)
                    else:
                        sub = COV._split(b)
                    for s in sub or []:
                        q.append((s, set(pend_), depth + 1))
                    if not sub:
                        for c in pend_:
                            hojas_pend[c] += 1
                else:
                    for c in pend_:
                        hojas_pend[c] += 1
        res = {}
        for cid in cand:
            if estado[cid] == "testigo":
                fin = "testigo"
            elif hojas_pend[cid] == 0:
                fin = "cerrada"
            else:
                fin = "pendiente"
            res[cid] = fin
        cnt = {k: sum(1 for v in res.values() if v == k) for k in ("cerrada", "testigo", "pendiente")}
        doc["cajas"].append({"clave_p3b": key, "tipo_p3b": tipo_caja.get(key), "ranking_s": round(ranking_s, 2),
                             "segundos": round(time.time() - tb, 2), "hojas": hojas, "orden_ejes_M2": orden_ejes,
                             "conteo": cnt, "afirmacion_P3b": res.get(CLAIM_P3B), "por_afirmacion": res,
                             "segundos_p3b": p3b[key]["segundos"], "hojas_p3b": p3b[key]["hojas"]})
        doc["encierros_c2"] = n_c2[0]
        doc["consumido_s"] = round(time.time() - t0, 1)
        tw = time.time()
        N.write_json_atomic(out, doc)
        doc["escritura_s"] = round(doc.get("escritura_s", 0.0) + time.time() - tw, 3)
    doc["consumido_s"] = round(time.time() - t0, 1)
    doc["encierros_c2"] = n_c2[0]
    doc["parada"] = doc["parada"] or "TODAS_LAS_PENDIENTES"
    N.write_json_atomic(out, doc)
    print(json.dumps({"metodo": metodo, "cajas": len(doc["cajas"]), "parada": doc["parada"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
