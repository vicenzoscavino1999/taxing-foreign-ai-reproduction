"""Ensayo pequeño de COSTO de las búsquedas de quiebre (Hito 4; CIERRE DF Y PASO 4 3.7, NO OFICIAL; medición, no
producción).

  <py_integracion> -m codigo.ensayo_quiebres <salida.json> <eventos.jsonl> <seg_por_evaluacion> <tope_por_busqueda_s> <tope_total_s> <k>

Universo de búsquedas NO triviales de la opción B (review/PASO4_OPCION_B.md §4; código: paper2b.run.Run.robustness y
paper2b.robustness.search). Solo las 16 afirmaciones robust_infeasible del registro candidato v4 (resolucion_3_7,
autenticado por su audit/entrega.json) llegan a la búsqueda con línea base 'verified'; las 1712 restantes tienen veredicto
inconclusive y la búsqueda devuelve not_applicable_baseline_inconclusive sin evaluar. Las 16 son 8 pares G/N con G idéntica
en f (C2_G = C2_N en f; K1 no depende del diseño; mismos contextos), así que se ensayan solo las 8 de diseño G.
Búsquedas ESTRUCTURALES ensayadas: a inferior/superior, rho inferior, kappa_tilde inferior/superior (rho superior es
theoretical_boundary sin evaluar). 8 x 5 = 40 pares; se eligen k por orden de sha256("SEL-ENSAYO-QUIEBRES-v1|cid|eje|dir"),
sin mirar costos. Método SIN CAMBIOS: RB.search con la escalera y la tolerancia de RunConfig y la escala de D7.
claim_holds = el de codigo.quiebre_nacional (intento 2, resolucion_3_7) generalizado al eje ensayado: sondeo de testigos
certificados de fallo en la esquina de C2 alto y K1 bajo con el eje en su NUEVO extremo y luego cobertura M4 del soporte
estructural completo con el eje ampliado ('holds' solo si todas las hojas cierran; 'incomplete' si se agota el tiempo).
Cada evaluación se escribe al instante en eventos.jsonl (fsync) y la salida se reescribe de forma atómica tras cada búsqueda.
"""
from __future__ import annotations

import hashlib
import json
import os
import statistics
import sys
import time
from pathlib import Path

from codigo import cobertura_m4 as C4
from codigo import testigos as T
from codigo.demo import c2_normalizado as C2N
from codigo.demo import memo_c2 as MEMO
from codigo.demo import nucleo_v as N
from codigo.demo.cobertura_compartida import q_pot_exact
from paper2b import cobertura as COV
from paper2b import robustness as RB
from paper2b import run as RUNMOD
from paper2b.claims import EPS_ECON as COV_EPS

RES = N.AREA.parent / "resolucion_3_7_2026-10-04_lima1941"
SEL = "SEL-ENSAYO-QUIEBRES-v1"
PARES = (("a", "inferior"), ("a", "superior"), ("rho", "inferior"), ("kappa_tilde", "inferior"), ("kappa_tilde", "superior"))


def autenticado(rel):
    inv = json.loads((RES / "audit/entrega.json").read_bytes())
    raw = (RES / rel).read_bytes()
    N.need(inv["files"][rel]["sha256"] == hashlib.sha256(raw).hexdigest(), "NO_AUTENTICADO:" + rel)
    return json.loads(raw)


def main():
    out, ev_p = Path(sys.argv[1]), Path(sys.argv[2])
    seg, tope_b, tope_t, k = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6])
    t0 = time.time()
    reg = autenticado("demo/registro/registro_candidato_v4.json")["afirmaciones"]
    rob = sorted(c for c, v in reg.items() if v["categoria"] == "robusta_infactible_certificada")
    N.need(len(rob) == 16, "NO_16_ROBUSTAS")
    gs = [c for c in rob if ":G:" in c]
    N.need(len(gs) == 8 and all(c.replace(":G:", ":N:") in rob for c in gs), "PARES_GN_INCOMPLETOS")
    orden = sorted(((hashlib.sha256(f"{SEL}|{c}|{p}|{d}".encode()).hexdigest(), c, p, d) for c in gs for p, d in PARES))
    elegidos = [(c, p, d) for _, c, p, d in orden[:k]]
    ctx = N.Contexto()
    COV.q_pot = q_pot_exact
    cfg = RUNMOD.RunConfig()
    fh = open(ev_p, "a", encoding="utf-8")
    memo = MEMO.Memo(True)
    nulo = lambda **kw: None  # noqa: E731
    prep = {}
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "objeto": "costo de RB.search (quiebres estructurales) en la opción B",
           "identidad_sha256": ctx.identity_sha256, "regla": SEL, "universo_pares": len(orden), "k": k,
           "elegidos": [list(e) for e in elegidos], "contexto_s": round(time.time() - t0, 1), "seg_por_evaluacion": seg,
           "tope_por_busqueda_s": tope_b, "tope_total_s": tope_t, "escalera": list(cfg.robustness_ladder),
           "tolerancia_biseccion": cfg.robustness_bisect_tol, "busquedas": []}

    def log(**kw):
        kw["t"] = round(time.time() - t0, 2)
        fh.write(json.dumps(kw, ensure_ascii=False, default=str) + "\n")
        fh.flush()
        os.fsync(fh.fileno())

    for cid, pid, dirn in elegidos:
        if time.time() - t0 > tope_t:
            doc["busquedas"].append({"afirmacion": cid, "eje": pid, "direccion": dirn, "estado": "no_iniciada_por_tope_total"})
            continue
        tp = time.time()
        if cid not in prep:
            try:
                prep[cid] = T.preparar(ctx, "G", [cid])
            except N.DemoError as e:
                prep[cid] = e
        st = prep[cid]
        if isinstance(st, N.DemoError):
            doc["busquedas"].append({"afirmacion": cid, "eje": pid, "direccion": dirn, "estado": "preparacion_fallida", "error": str(st)})
            N.write_json_atomic(out, doc)
            continue
        prep_s = round(time.time() - tp, 1)
        axes, fx = st["axes"], st["fixed"]
        root = {p: (axes[p][0][0], axes[p][-1][1]) for p in COV.STRUCT}
        sid = st["claims"][cid].support_sets[0]
        r = ctx.run(sid, "ensayo_quiebres:" + sid)
        lo, hi = (float(x) for x in r.inp.d7.interval(sid, pid))
        scale = r.inp.d7.support(sid, pid)["scale"] or "arithmetic"
        sts = {"G": dict(st, cand=[cid]), "N": dict(st, cand=[])}
        tb = time.time()
        limite = min(tb + tope_b, t0 + tope_t)
        evals = []

        def claim_holds(iv, cid=cid, pid=pid, dirn=dirn, root=root, fx=fx, st=st, sts=sts, limite=limite, evals=evals, tb=tb):
            a, b = float(iv[0]), float(iv[1])
            box = dict(root, **{pid: (a, b)})
            te = time.time()
            res = None
            if te > limite:
                res = ("incomplete", None)
            elif not COV.box_admissible(box, fx):
                res = ("inadmissible", "box_admissible")
            else:
                nuevo = b if dirn == "superior" else a
                for av in ((nuevo,) if pid == "a" else (1.1, 1.3, 1.5, 2.0, 2.5)):
                    pt = {p: ((v[0] + v[1]) / 2,) * 2 for p, v in box.items()}
                    pt.update(a=(av, av), kappa_tilde=(box["kappa_tilde"][1],) * 2, rho=(box["rho"][1],) * 2, phi=(box["phi"][1],) * 2,
                              eta_f=(box["eta_f"][0],) * 2, z_cost=(box["z_cost"][0],) * 2, beta_tilde=(2.125, 2.125),
                              eta_d=(2.05, 2.05), u_theta=(0.5, 0.5))
                    pt[pid] = (nuevo, nuevo)
                    if not COV.box_admissible(pt, fx):
                        continue
                    c2p = C2N.c2_normalizado(st["model"], pt, "G", "f", float(fx["bar_tau_d"]), float(fx["bar_tau_f"]), fixed=fx)
                    glo = max(COV.g_enclosure(st["model"], pt, cx, fx, c2p).lo for cx in st["univ"][cid])
                    log(evento="sondeo", afirmacion=cid, eje=pid, direccion=dirn, intervalo=[a, b], a=av, C2=[c2p.lo, c2p.hi], G_lo=glo)
                    if glo > -COV_EPS:
                        res = ("fails", [{"punto": {p: v[0] for p, v in pt.items()}, "G_lo": glo, "C2": [c2p.lo, c2p.hi]}])
                        break
                if res is None:
                    resto = max(1.0, min(seg, limite - time.time()))
                    rr = C4.cubrir_m4(sts, box, memo, ctx.identity_sha256, log, nulo, "%s %s %r" % (pid, dirn, [a, b]), resto, 400)
                    est = rr["por_afirmacion"]["G|" + cid]["estado"]
                    res = {"cerrada": ("holds", None), "testigo": ("fails", [{pid: [a, b]}])}.get(est, ("incomplete", None))
            evals.append({"intervalo": [a, b], "resultado": res[0], "segundos": round(time.time() - te, 2),
                          "acumulado_s": round(time.time() - tb, 1)})
            log(evento="evaluacion", afirmacion=cid, eje=pid, direccion=dirn, intervalo=[a, b], resultado=res[0])
            return res
        bk = RB.search("tecnologia", pid, None, dirn, lo, hi, scale, claim_holds, ladder=cfg.robustness_ladder,
                       bisect_tol=cfg.robustness_bisect_tol, baseline_status="verified")
        doc["busquedas"].append({"afirmacion": cid, "eje": pid, "direccion": dirn, "soporte_primario": [lo, hi], "escala": scale,
                                 "preparacion_s": prep_s, "busqueda_s": round(time.time() - tb, 1), "evaluaciones": evals,
                                 "status": bk.status, "computation_status": bk.computation_status, "reason": bk.reason,
                                 "r_critical": bk.r_critical, "bracket": bk.bracket, "reached_expansion_factor": bk.reached_expansion_factor,
                                 "evaluated_domain": bk.evaluated_domain, "witnesses": bk.witnesses})
        ts = [b["busqueda_s"] for b in doc["busquedas"] if "busqueda_s" in b]
        doc["resumen"] = {"n": len(ts), "media_s": statistics.fmean(ts), "mediana_s": statistics.median(ts), "max_s": max(ts),
                          "min_s": min(ts), "estados": {s: sum(1 for b in doc["busquedas"] if b.get("status") == s)
                                                       for s in sorted({b.get("status") for b in doc["busquedas"]} - {None})}}
        doc["segundos"] = round(time.time() - t0, 1)
        N.write_json_atomic(out, doc)
        log(evento="busqueda", afirmacion=cid, eje=pid, direccion=dirn, status=bk.status, s=doc["busquedas"][-1]["busqueda_s"])
    doc["segundos"] = round(time.time() - t0, 1)
    doc["estado"] = "completo" if all("status" in b for b in doc["busquedas"]) else "parcial_por_tope"
    N.write_json_atomic(out, doc)
    print(json.dumps({"resumen": doc.get("resumen"), "estado": doc["estado"], "s": doc["segundos"]}))


if __name__ == "__main__":
    raise SystemExit(main())
