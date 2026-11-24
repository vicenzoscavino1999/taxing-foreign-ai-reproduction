"""Testigos de las cajas A y B de la muestra: persistencia inmediata, fichas y verificación (TESTIGOS Y COBERTURA 3.7, NO OFICIAL).

  <py_integracion> -m codigo.testigos <familia G|N> <salida_dir> <tope_cooperativo_s>

1. Reproduce las tareas (A, familia) y (B, familia) de la muestra de costo con la MISMA configuración numérica
   (codigo/muestra_costo.py copiado sin cambios: M2r, memo, C2 normalizado, 64 hojas, 120 s por caja) y el mismo
   universo (157 pendientes del registro vigente, autenticado). La lógica de cobertura es una copia de
   muestra_costo.cubrir; lo ÚNICO añadido es el registro: cada posible testigo (hoja con max G.lo > -eps sobre los
   contextos de la afirmación, o centro sondeado) se escribe al instante (JSONL + fsync) con afirmación, conjunto,
   índice de contexto nacional, contexto, caja o punto, procedencia y encierros de C2, K1 y G.
2. Por afirmación (sin duplicados): el testigo de mayor G.lo; punto concreto = centro de la hoja (todo punto de la
   hoja cumple G.lo > -eps para ese contexto) o el centro sondeado. Ficha completa en ese punto con C2 por el método
   que reproduce el verificador (c2_struct_enclosure puntual) y el contexto de mayor G.lo del conjunto.
3. Verificación con el verificador corregido (verificador_v2, continuo permitido, verificar_completo: pasos 1-9, C2
   reproducido y universo oficial) en el rol A (G.lo > -eps) y, si G.lo >= eps, también en el rol pos.
4. Testigos complementarios de NUDO de la evidencia 3.7.1 (validacion_testigos_3_7/demo/R, autenticada): B (G.hi < eps)
   y neg (G.hi <= -eps), verificados con verificador_v2 (malla) para cada afirmación con ficha A.
"""
from __future__ import annotations

import copy
import dataclasses
import hashlib
import json
import os
import sys
import time
from collections import deque
from decimal import Decimal
from pathlib import Path

from codigo import muestra_costo as MC
from codigo.demo import nucleo_v as N
from codigo.demo import c2_normalizado as C2N
from codigo.demo import memo_c2 as MEMO
from codigo.demo.cobertura_compartida import q_pot_exact
from codigo.demo.universo import Universo, qmin_table
from codigo.demo.verificador_v2 import Verificador
from paper2b import claims as CL
from paper2b import cobertura as COV
from paper2b import run as RUNMOD

CAJAS = {"A": [0, 1, 2, 0, 4, 3, 2, 1, 0], "B": [0, 0, 2, 0, 4, 2, 3, 0, 1]}
EPS = CL.EPS_ECON
VAL = N.ROOT / "tmp/validacion_testigos_3_7_2026-10-03"
VAL_INV = "3e37c8c13acc6bfb111923ac98899429bb68650e99b74f06a653cddbc97cf95c"


def preparar(ctx, dis, pend_ids):
    from codigo.demo import cobertura_mejorada as CM
    cand_all, _ = CM.autenticados()
    cand = sorted(c for c in pend_ids if f":{dis}:" in c)
    N.need(all(c in cand_all for c in cand), "PENDIENTE_FUERA_DE_LAS_CANDIDATAS")
    claims = {c.claim_id: c for c in ctx.claims}
    sets = sorted({s for cid in cand for s in claims[cid].support_sets})
    runs = {sid: ctx.run(sid, "testigos:" + sid) for sid in sets}
    ref_sid = claims[CM.CLAIM_P3B].support_sets[0]
    if ref_sid not in runs:
        runs[ref_sid] = ctx.run(ref_sid, "testigos:" + ref_sid)
    axes = runs[ref_sid].struct_axes(ref_sid)
    N.need(all(runs[s].struct_axes(s) == axes for s in runs), "EJES_DISTINTOS_NO_SE_COMPARTE")
    ax0 = N.axes_nodes(ctx, ref_sid)
    corner = {p: Decimal(str(ax0[p][0])) for p in RUNMOD.STRUCT}
    U = Universo(runs, qmin_table(ctx.inp.grid_cells))
    univ, meta, fixed_ref, compartir = {}, {}, None, {}
    for cid in cand:
        cl = claims[cid]
        cx, mt = [], []
        for sid in cl.support_sets:
            c, fx = U.contexts(cl, sid, corner)
            cx += [x for x, _ in c]
            mt += [(sid, bi) for _, bi in c]
            fixed_ref = fixed_ref or fx
            compartir.setdefault(json.dumps(fx, sort_keys=True, default=str), []).append(cid)
        univ[cid], meta[cid] = cx, mt
    N.need(len(compartir) == 1, "FIJOS_DISTINTOS")
    return {"cand": cand, "univ": univ, "meta": meta, "fixed": fixed_ref, "model": runs[ref_sid].model, "axes": axes,
            "U": U, "corner": corner, "runs": runs, "claims": claims}


def _ctx(c):
    return dataclasses.asdict(c) if dataclasses.is_dataclass(c) else str(c)


def _nac(st, cid, sid, bi):
    m = st["U"].meta(st["claims"][cid], sid, st["corner"], bi)
    return {"pais": m["pais"], "estado_nacional": m["estado_nacional"], "celda_externa": m["celda_externa"],
            "macro": {k: str(v) for k, v in m["macro"].items()}}


def k1_de(box, c):
    q = COV.q_pot(box)
    lam = c.s_pi / (1.0 - q)
    return c.n_min / (lam * c.gain)


def cubrir(st, dis, root, memo, ident, log, tarea):
    """COPIA de muestra_costo.cubrir (misma lógica y límites) + registro inmediato de cada posible testigo."""
    model, fixed, univ, cand, meta = st["model"], st["fixed"], st["univ"], st["cand"], st["meta"]
    bd, bf = float(fixed["bar_tau_d"]), float(fixed["bar_tau_f"])
    n_c2 = [0]

    def c2_of(b):
        n_c2[0] += 1
        k = MEMO.clave(b, dis, "f", bd, bf, fixed, model, "normalizado", ident)
        return memo.obtener(k, lambda: C2N.c2_normalizado(model, b, dis, "f", bd, bf, fixed=fixed), b)

    def eval_leaf(b, activos, c2):
        cerr, test, pend_ = set(), set(), set()
        for cid in activos:
            ghi, glo, best = -1e300, -1e300, None
            for k, c in enumerate(univ[cid]):
                g = COV.g_enclosure(model, b, c, fixed, c2)
                if g is None:
                    ghi = glo = None
                    break
                if g.lo > glo:
                    best = (k, g)
                ghi, glo = max(ghi, g.hi), max(glo, g.lo)
            if ghi is None:
                pend_.add(cid)
            elif ghi <= -EPS:
                cerr.add(cid)
            elif glo > -EPS:
                test.add(cid)
                k, g = best
                c = univ[cid][k]
                k1 = k1_de(b, c)
                log(tarea=tarea, afirmacion=cid, tipo="hoja", conjunto=meta[cid][k][0], indice_contexto_nacional=meta[cid][k][1],
                    indice_contexto=k, contexto=_ctx(c), nacional=_nac(st, cid, meta[cid][k][0], meta[cid][k][1]), caja={p: list(v) for p, v in b.items()},
                    C2=[c2.lo, c2.hi], K1=[k1.lo, k1.hi], G=[g.lo, g.hi])
            else:
                pend_.add(cid)
        return cerr, test, pend_

    def split_axis(box, p):
        lo, hi = box[p]
        m = lo + (hi - lo) / 2
        return dict(box, **{p: (lo, m)}), dict(box, **{p: (m, hi)})
    tb = time.time()
    estado = {cid: "pendiente" for cid in cand}
    hojas_pend = {cid: 0 for cid in cand}
    q = deque([(root, set(cand), 0)])
    hojas, orden_ejes, ranking_s, tope_reloj = 0, None, 0.0, False
    while q:
        b, act, depth = q.popleft()
        act = {c for c in act if estado[c] != "testigo"}
        if not act:
            continue
        hojas += 1
        if not COV.box_admissible(b, fixed):
            pend_, cerr, test = set(act), set(), set()
        else:
            c2 = c2_of(b)
            cerr, test, pend_ = eval_leaf(b, act, c2) if c2 is not None else (set(), set(), set(act))
        for c in test:
            estado[c] = "testigo"
        if pend_:
            cen = {p: (lo + (hi - lo) / 2,) * 2 for p, (lo, hi) in b.items()}
            if COV.box_admissible(cen, fixed):
                c2c = c2_of(cen)
                if c2c is not None:
                    for cid in list(pend_):
                        gs = [(k, COV.g_enclosure(model, cen, c, fixed, c2c)) for k, c in enumerate(univ[cid])]
                        if any(g is not None and g.lo > -EPS for _, g in gs):
                            estado[cid] = "testigo"
                            pend_.discard(cid)
                            k, g = max(((k, g) for k, g in gs if g is not None), key=lambda t: t[1].lo)
                            c = univ[cid][k]
                            k1 = k1_de(cen, c)
                            log(tarea=tarea, afirmacion=cid, tipo="centro", conjunto=meta[cid][k][0], indice_contexto_nacional=meta[cid][k][1],
                                indice_contexto=k, contexto=_ctx(c), nacional=_nac(st, cid, meta[cid][k][0], meta[cid][k][1]),
                                punto={p: v[0] for p, v in cen.items()}, C2=[c2c.lo, c2c.hi], K1=[k1.lo, k1.hi], G=[g.lo, g.hi])
        if pend_:
            if hojas + len(q) + 2 <= MC.HOJAS and time.time() - tb < MC.SEG_CAJA:
                if orden_ejes is None and depth == 0:
                    a_r = time.time()
                    score = []
                    for p in COV.STRUCT:
                        if root[p][1] > root[p][0]:
                            hs = split_axis(root, p)
                            cs = [c2_of(h) if COV.box_admissible(h, fixed) else None for h in hs]
                            score.append((max((x.hi if x is not None else float("inf")) for x in cs), p))
                    orden_ejes = [p for _, p in sorted(score)[:3]]
                    ranking_s = time.time() - a_r
                p = orden_ejes[depth % len(orden_ejes)] if orden_ejes else None
                sub = split_axis(b, p) if (p and b[p][1] > b[p][0]) else COV._split(b)
                for s in sub or []:
                    q.append((s, set(pend_), depth + 1))
                if not sub:
                    for c in pend_:
                        hojas_pend[c] += 1
            else:
                tope_reloj = tope_reloj or not (time.time() - tb < MC.SEG_CAJA)
                for c in pend_:
                    hojas_pend[c] += 1
    res = {cid: ("testigo" if estado[cid] == "testigo" else ("cerrada" if hojas_pend[cid] == 0 else "pendiente")) for cid in cand}
    cnt = {k: sum(1 for v in res.values() if v == k) for k in ("cerrada", "testigo", "pendiente")}
    return {"segundos": round(time.time() - tb, 3), "hojas": hojas, "encierros_pedidos": n_c2[0], "ranking_s": round(ranking_s, 2),
            "conteo": cnt, "tope_reloj": tope_reloj, "completa": cnt["pendiente"] == 0, "por_afirmacion": res}


def main():
    dis, out_dir, tope = sys.argv[1], Path(sys.argv[2]), float(sys.argv[3])
    t0 = time.time()
    out_dir.mkdir(parents=True, exist_ok=True)
    ctx = N.Contexto()
    COV.q_pot = q_pot_exact
    pend_ids, reg_sha = MC.pendientes("v2")   # reproducción de la ronda anterior: registro v2 (157) declarado
    st = preparar(ctx, dis, pend_ids)
    fh = open(out_dir / f"testigos_{dis}.jsonl", "a", encoding="utf-8")

    def log(**kw):
        kw["t"] = round(time.time() - t0, 2)
        fh.write(json.dumps(kw, ensure_ascii=False, default=str) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "familia": dis, "identidad_sha256": ctx.identity_sha256, "registro_sha256": reg_sha,
           "muestra_costo_sha256": hashlib.sha256(Path(MC.__file__).read_bytes()).hexdigest(),
           "configuracion": {"metodo": "M2r + memo + C2 normalizado", "hojas": MC.HOJAS, "segundos_por_caja": MC.SEG_CAJA},
           "preparacion_s": round(time.time() - t0, 1), "tareas": {}, "fichas": {}}
    res_p = out_dir / f"resultado_{dis}.json"
    memo = MEMO.Memo(True)
    for nombre, idx in CAJAS.items():
        root = {p: st["axes"][p][i] for p, i in zip(COV.STRUCT, idx)}
        r = cubrir(st, dis, root, memo, ctx.identity_sha256, log, nombre)
        doc["tareas"][nombre] = dict(indices=idx, **{k: v for k, v in r.items() if k != "por_afirmacion"}, por_afirmacion=r["por_afirmacion"])
        N.write_json_atomic(res_p, doc)
    fh.close()
    # ------------------------------------------------------------------ fichas por afirmación (sin duplicados)
    regs = [json.loads(x) for x in (out_dir / f"testigos_{dis}.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    mejor = {}
    for w in regs:
        if w["afirmacion"] not in mejor or w["G"][0] > mejor[w["afirmacion"]]["G"][0]:
            mejor[w["afirmacion"]] = w
    doc["testigos_registrados"] = len(regs)
    doc["afirmaciones_con_posible_testigo"] = len(mejor)
    V = Verificador(ctx, permitir_continuo=True)
    Vn = Verificador(ctx, permitir_continuo=False)
    inv_raw = (VAL / "audit/entrega.json").read_bytes()
    N.need(N.sha(inv_raw) == VAL_INV, "INVENTARIO_VALIDACION")
    raw = (VAL / "demo/R/evidencia_testigos.json").read_bytes()
    N.need(json.loads(inv_raw)["files"]["demo/R/evidencia_testigos.json"]["sha256"] == N.sha(raw), "R_NO_AUTENTICADA")
    R = json.loads(raw)["afirmaciones"]
    claims, U, corner, model = st["claims"], st["U"], st["corner"], st["model"]
    for cid, w in sorted(mejor.items()):
        if time.time() - t0 > tope:
            doc["fichas"][cid] = {"estado": "candidato_no_verificado", "motivo": "TOPE_ANTES_DE_LA_FICHA", "testigo": w}
            continue
        cl = claims[cid]
        sid = w["conjunto"]
        r = V.run(sid)
        if w["tipo"] == "hoja":
            pt = {p: lo + (hi - lo) / 2 for p, (lo, hi) in w["caja"].items()}
        else:
            pt = dict(w["punto"])
        vals = {p: Decimal(repr(float(pt[p]))) for p in RUNMOD.STRUCT}
        dbox = {p: (float(v), float(v)) for p, v in vals.items()}
        cx, fixed = U.contexts(cl, sid, corner)
        c2 = r.model.c2_struct_enclosure(dbox, cl.design, "f", float(fixed["bar_tau_d"]), float(fixed["bar_tau_f"]), fixed=fixed)
        g, c, bi = max(((COV.g_enclosure(r.model, dbox, c, fixed, c2), c, bi) for c, bi in cx), key=lambda t: t[0].lo)
        q = COV.q_pot(dbox)
        lam = c.s_pi / (1.0 - q)
        k1 = c.n_min / (lam * c.gain)
        ficha = {"flujo": "muestra_costo_" + w["tipo"], "nudo": None, "conjunto": sid, "valores_estructurales": {p: str(v) for p, v in vals.items()},
                 **U.meta(cl, sid, corner, bi), "instrumento": c.instrument, "diseno": c.design, "cotas_fiscales": list(c.bars),
                 "contexto": {"s_pi": c.s_pi, "s_t": c.s_t, "eta_h": c.eta_h, "gain": c.gain, "n_min": c.n_min},
                 "q_pot": [q.lo, q.hi], "lambda": [lam.lo, lam.hi], "K1": [k1.lo, k1.hi],
                 "C2": {"lo": c2.lo, "hi": c2.hi, "metodo": "c2_struct_enclosure_punto", "estado": None,
                        "origen": {"tarea": w["tarea"], "tipo": w["tipo"], "t_registro": w["t"], "G_del_registro": w["G"]}},
                 "G": [g.lo, g.hi]}
        rol = "pos" if g.lo >= EPS else "A"
        vA = V.verificar_completo(ficha, cl, "A")
        vP = V.verificar_completo(ficha, cl, "pos") if rol == "pos" else None
        base = R[cid]
        vB = Vn.verificar_completo(base["B"], cl, "B") if base.get("B") else None
        vN = Vn.verificar_completo(base["neg"], cl, "neg") if (base.get("neg") and rol == "pos") else None
        doc["fichas"][cid] = {"ficha": ficha, "testigo_registrado": w, "verificacion_A": vA, "verificacion_pos": vP,
                              "verificacion_B_nudo": vB, "verificacion_neg_nudo": vN, "G_lo": g.lo,
                              "estado_A": "verificada" if vA["valida"] else "rechazada"}
        N.write_json_atomic(res_p, doc)
    doc["consumido_s"] = round(time.time() - t0, 1)
    N.write_json_atomic(res_p, doc)
    print(json.dumps({"familia": dis, "tareas": {k: v["conteo"] for k, v in doc["tareas"].items()}, "testigos": len(regs),
                      "afirmaciones": len(mejor), "A_validas": sum(1 for x in doc["fichas"].values() if x.get("estado_A") == "verificada"),
                      "s": doc["consumido_s"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
