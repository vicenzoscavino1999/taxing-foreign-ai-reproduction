"""Ensayo de COSTO de las búsquedas de quiebre por la RUTA MACRO y verificación de la deduplicación G/N bajo los dominios
AMPLIADOS (Hito 4.B; CIERRE DF Y PASO 4 3.7, NO OFICIAL; medición, no producción).

  <py_integracion> -m codigo.ensayo_quiebres_macro <salida.json> <eventos.jsonl> <seg_por_evaluacion> <tope_por_busqueda_s> <tope_total_s> <k>

Búsquedas macro de paper2b.run.Run.robustness para una afirmación robust_infeasible: η_w (la dirección que no es hueco de
soporte), π_iva, π_otros_productos y π_produccion (inferior y superior), π conjunto (los tres con el intervalo de π_iva,
inferior y superior) y η_H (escalera declarada, RB.ladder_search). claim_holds macro = réplica de Run.claim_holds para
soportes macro AMPLIADOS: los vértices macro se recalculan con el intervalo ampliado (sin filtro de bloque cuando se amplía
η_w, como en run.py), MC.bridge no admisible -> 'inadmissible', y la región estructural CONTINUA se certifica con la
cobertura M4 (cobertura_m4.cubrir_m4) sobre la caja raíz con los contextos ampliados, tras un sondeo de testigos de
fallo en la esquina de C2 alto y K1 bajo (como codigo/ensayo_quiebres.py). Métodos RB.search / RB.ladder_search SIN
cambios. Selección: k pares de 8 afirmaciones G x 10 búsquedas macro por orden de sha256("SEL-ENSAYO-QUIEBRES-MACRO-v1|...").
Deduplicación G/N: (i) C2_G = C2_N (encierro normalizado) en puntos y cajas de los dominios estructurales ampliados que
usan las búsquedas (κ̃ hasta 0,317, a hasta 4,6, ρ hasta 7e-5, escalera 4) y (ii) contextos idénticos salvo el diseño
para las 8 parejas (s_π, s_T, η_H, y, n_min).
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import statistics
import sys
import time
from decimal import Decimal
from itertools import product
from pathlib import Path

from codigo import cobertura_m4 as C4
from codigo import testigos as T
from codigo.demo import c2_normalizado as C2N
from codigo.demo import memo_c2 as MEMO
from codigo.demo import nucleo_v as N
from codigo.demo.cobertura_compartida import q_pot_exact
from codigo.demo.universo import MACRO, Universo
from paper2b import cobertura as COV
from paper2b import robustness as RB
from paper2b import run as RUNMOD
from paper2b.claims import EPS_ECON as COV_EPS

RES = N.AREA.parent / "resolucion_3_7_2026-10-04_lima1941"
SEL = "SEL-ENSAYO-QUIEBRES-MACRO-v1"
PI = ("pi_iva", "pi_otros_productos", "pi_produccion")


class Inadmisible(Exception):
    pass


class UniversoAmpliado(Universo):
    def __init__(self, base, ov):
        super().__init__(base.runs, base.qmin)
        self.ov = ov

    def base(self, set_id, block, countries, years, corner):
        key = (set_id, block, tuple(countries), tuple(years))
        if key in self._base:
            return self._base[key]
        r = self.runs[set_id]
        d7 = r.inp.d7
        axes = {}
        for pid in MACRO:
            if pid in self.ov:
                axes[pid] = list(self.ov[pid])
            else:
                lo, hi = d7.interval(set_id, pid)
                axes[pid] = [lo] if lo == hi else [lo, hi]
        axes["eta_H"] = list(self.ov["eta_H"]) if "eta_H" in self.ov else d7.nodes(set_id, "eta_H")
        fixed = self.fixed(set_id)
        names = sorted(axes)
        out = []
        for combo in product(*[axes[n] for n in names]):
            mv = dict(zip(names, combo))
            v = dict(corner, **mv, **fixed)
            if "eta_w" not in self.ov and r.block_of(v["eta_w"]) != block:
                continue
            for country in countries:
                for st in r.states_for({"set": set_id, "values": v}, country):
                    if st.anchor_year not in years:
                        continue
                    m = RUNMOD.MC.bridge(st.share_dict(), v)
                    if not m.admissible:
                        raise Inadmisible(str(getattr(m, "reasons", ""))[:120])
                    out.append((country, st, {k: str(x) for k, x in mv.items()}, float(m.s_Pi_marg), float(m.s_T_marg),
                                float(v["eta_H"]), float(v["gain_share"])))
        self._base[key] = (out, fixed)
        return self._base[key]


def autenticado(rel):
    inv = json.loads((RES / "audit/entrega.json").read_bytes())
    raw = (RES / rel).read_bytes()
    N.need(inv["files"][rel]["sha256"] == hashlib.sha256(raw).hexdigest(), "NO_AUTENTICADO:" + rel)
    return json.loads(raw)


def busquedas_macro(cid):
    bloque_w = cid.split(":")[-2]
    dw = "inferior" if bloque_w == "micro" else "superior"
    out = [("eta_w", dw)] + [(p, d) for p in PI for d in ("inferior", "superior")] + [("pi_joint", d) for d in ("inferior", "superior")]
    return out + [("eta_H", "ladder")]


def main():
    out, ev_p = Path(sys.argv[1]), Path(sys.argv[2])
    seg, tope_b, tope_t, k = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6])
    t0 = time.time()
    reg = autenticado("demo/registro/registro_candidato_v4.json")["afirmaciones"]
    rob = sorted(c for c, v in reg.items() if v["categoria"] == "robusta_infactible_certificada")
    gs = [c for c in rob if ":G:" in c]
    N.need(len(gs) == 8, "NO_8_G")
    orden = sorted((hashlib.sha256(f"{SEL}|{c}|{p}|{d}".encode()).hexdigest(), c, p, d) for c in gs for p, d in busquedas_macro(c))
    elegidos = [(c, p, d) for _, c, p, d in orden[:k]]
    ctx = N.Contexto()
    COV.q_pot = q_pot_exact
    cfg = RUNMOD.RunConfig()
    fh = open(ev_p, "a", encoding="utf-8")
    memo = MEMO.Memo(True)
    nulo = lambda **kw: None  # noqa: E731
    prep = {}
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "objeto": "costo de RB.search/ladder_search por la ruta macro (opción B)",
           "identidad_sha256": ctx.identity_sha256, "regla": SEL, "universo_pares": len(orden), "k": k, "elegidos": [list(e) for e in elegidos],
           "contexto_s": round(time.time() - t0, 1), "seg_por_evaluacion": seg, "tope_por_busqueda_s": tope_b, "tope_total_s": tope_t,
           "escalera": list(cfg.robustness_ladder), "tolerancia_biseccion": cfg.robustness_bisect_tol, "busquedas": []}

    def log(**kw):
        kw["t"] = round(time.time() - t0, 2)
        fh.write(json.dumps(kw, ensure_ascii=False, default=str) + "\n")
        fh.flush()
        os.fsync(fh.fileno())

    def preparar(cid, dis="G"):
        if (cid, dis) not in prep:
            prep[(cid, dis)] = T.preparar(ctx, dis, [cid])
        return prep[(cid, dis)]

    for cid, pid, dirn in elegidos:
        if time.time() - t0 > tope_t:
            doc["busquedas"].append({"afirmacion": cid, "eje": pid, "direccion": dirn, "estado": "no_iniciada_por_tope_total"})
            continue
        tp = time.time()
        st = preparar(cid)
        prep_s = round(time.time() - tp, 1)
        cl = st["claims"][cid]
        axes, fx = st["axes"], st["fixed"]
        root = {p: (axes[p][0][0], axes[p][-1][1]) for p in COV.STRUCT}
        s0 = cl.support_sets[0]
        r0 = st["runs"][s0]
        tb = time.time()
        limite = min(tb + tope_b, t0 + tope_t)
        evals = []

        def claim_holds_ov(ov, etiqueta, cid=cid, cl=cl, st=st, fx=fx, root=root, limite=limite, evals=evals, tb=tb):
            te = time.time()
            res = None
            if te > limite:
                res = ("incomplete", None)
            else:
                U2 = UniversoAmpliado(st["U"], ov)
                try:
                    cx = []
                    for sid in cl.support_sets:
                        c_, _ = U2.contexts(cl, sid, st["corner"])
                        cx += [x for x, _ in c_]
                except Inadmisible as e:
                    res = ("inadmissible", "bridge:" + str(e)[:60])
                if res is None and not cx:
                    res = ("incomplete", None)
                if res is None:
                    for av in (1.1, 1.3, 1.5, 2.0, 2.5):          # sondeo de testigos de fallo (C2 alto, K1 bajo)
                        pt = {p: ((v[0] + v[1]) / 2,) * 2 for p, v in root.items()}
                        pt.update(a=(av, av), kappa_tilde=(root["kappa_tilde"][1],) * 2, rho=(root["rho"][1],) * 2, phi=(root["phi"][1],) * 2,
                                  eta_f=(root["eta_f"][0],) * 2, z_cost=(root["z_cost"][0],) * 2, beta_tilde=(2.125, 2.125),
                                  eta_d=(2.05, 2.05), u_theta=(0.5, 0.5))
                        if not COV.box_admissible(pt, fx):
                            continue
                        c2p = C2N.c2_normalizado(st["model"], pt, "G", "f", float(fx["bar_tau_d"]), float(fx["bar_tau_f"]), fixed=fx)
                        glo = max(COV.g_enclosure(st["model"], pt, c, fx, c2p).lo for c in cx)
                        if glo > -COV_EPS:
                            res = ("fails", [{"punto": {p: v[0] for p, v in pt.items()}, "G_lo": glo}])
                            break
                if res is None:
                    resto = max(1.0, min(seg, limite - time.time()))
                    sts = {"G": dict(st, cand=[cid], univ={cid: cx}), "N": dict(st, cand=[])}
                    rr = C4.cubrir_m4(sts, root, memo, ctx.identity_sha256, log, nulo, "%s %s" % (pid, etiqueta), resto, 400)
                    est = rr["por_afirmacion"]["G|" + cid]["estado"]
                    res = {"cerrada": ("holds", None), "testigo": ("fails", [{pid: etiqueta}])}.get(est, ("incomplete", None))
            evals.append({"sustitucion": etiqueta, "resultado": res[0], "segundos": round(time.time() - te, 2), "acumulado_s": round(time.time() - tb, 1)})
            log(evento="evaluacion", afirmacion=cid, eje=pid, direccion=dirn, sustitucion=etiqueta, resultado=res[0])
            return res
        if pid == "eta_H":
            ladders = ctx.C.F["parameters"]["eta_H"]["sensitivity_ladders"]
            bk = RB.ladder_search("incidencia_laboral", "eta_H", ladders,
                                  lambda lv: claim_holds_ov({"eta_H": [Decimal(str(x)) for x in lv]}, "eta_H=%s" % list(lv)), baseline_status="verified")
            dom = None
        else:
            p0 = "pi_iva" if pid == "pi_joint" else pid
            lo, hi = (float(x) for x in r0.inp.d7.interval(s0, p0))
            scale = "arithmetic" if pid == "pi_joint" else (r0.inp.d7.support(s0, p0)["scale"] or "arithmetic")
            sust = PI if pid == "pi_joint" else (pid,)
            comp = (cl.eta_w_block if pid == "eta_w" else p0.split("_", 1)[1]) if pid != "pi_joint" else None
            block = "incidencia_laboral" if pid == "eta_w" else "cuna_tributaria"
            bk = RB.search(block, None if pid == "pi_joint" else pid, comp, dirn, lo, hi, scale,
                           lambda iv: claim_holds_ov({p: [Decimal(repr(float(iv[0]))), Decimal(repr(float(iv[1])))] for p in sust}, "%r" % (list(iv),)),
                           ladder=cfg.robustness_ladder, bisect_tol=cfg.robustness_bisect_tol, baseline_status="verified", joint=pid == "pi_joint")
            dom = [lo, hi]
        doc["busquedas"].append({"afirmacion": cid, "eje": pid, "direccion": dirn, "soporte_primario": dom, "preparacion_s": prep_s,
                                 "busqueda_s": round(time.time() - tb, 1), "evaluaciones": evals, "status": bk.status,
                                 "computation_status": bk.computation_status, "reason": bk.reason, "r_critical": getattr(bk, "r_critical", None),
                                 "reached_expansion_factor": getattr(bk, "reached_expansion_factor", None),
                                 "evaluated_domain": getattr(bk, "evaluated_domain", None)})
        ts = [b["busqueda_s"] + b.get("preparacion_s", 0.0) for b in doc["busquedas"] if "busqueda_s" in b]
        doc["resumen"] = {"n": len(ts), "media_s": statistics.fmean(ts), "mediana_s": statistics.median(ts), "max_s": max(ts), "min_s": min(ts),
                          "estados": {s: sum(1 for b in doc["busquedas"] if b.get("status") == s) for s in sorted({b.get("status") for b in doc["busquedas"]} - {None})}}
        doc["segundos"] = round(time.time() - t0, 1)
        N.write_json_atomic(out, doc)
    # ---------------------------------------------------------------- deduplicación G/N bajo dominios ampliados
    tp = time.time()
    st = preparar(gs[0])
    fx, axes = st["fixed"], st["axes"]
    root = {p: (axes[p][0][0], axes[p][-1][1]) for p in COV.STRUCT}
    amp = dict(root, kappa_tilde=(root["kappa_tilde"][0] / 253.0, 0.3171666350274487), a=(root["a"][0], 4.6), rho=(7.0e-5, 1.0))
    rng = random.Random(20261006)
    bd, bf = float(fx["bar_tau_d"]), float(fx["bar_tau_f"])
    difs, n_ok, n_tot = [], 0, 0
    for i in range(50):
        if i < 40:
            b = {p: ((x := rng.uniform(lo, hi)), x) for p, (lo, hi) in amp.items()}
        else:
            b = {}
            for p, (lo, hi) in amp.items():
                c0 = rng.uniform(lo, hi)
                w = (hi - lo) * 0.01
                b[p] = (max(lo, c0 - w), min(hi, c0 + w))
        if not COV.box_admissible(b, fx):
            continue
        g = C2N.c2_normalizado(st["model"], b, "G", "f", bd, bf, fixed=fx)
        nn = C2N.c2_normalizado(st["model"], b, "N", "f", bd, bf, fixed=fx)
        n_tot += 1
        if g is not None and nn is not None and g.lo == nn.lo and g.hi == nn.hi:
            n_ok += 1
        elif g is not None and nn is not None:
            difs.append(max(abs(g.lo - nn.lo), abs(g.hi - nn.hi)))
    ctx_iguales = {}
    for c in gs:
        cn = c.replace(":G:", ":N:")
        sg, sn = preparar(c, "G"), preparar(cn, "N")
        fg = [(x.instrument, x.bars, x.s_pi, x.s_t, x.eta_h, x.gain, x.n_min) for x in sg["univ"][c]]
        fn = [(x.instrument, x.bars, x.s_pi, x.s_t, x.eta_h, x.gain, x.n_min) for x in sn["univ"][cn]]
        ctx_iguales[c.split(":", 1)[1]] = fg == fn
    doc["deduplicacion_GN"] = {"dominio_ampliado": {p: list(v) for p, v in amp.items()}, "puntos_y_cajas": n_tot, "C2_G_igual_C2_N": n_ok,
                               "max_diferencia": max(difs) if difs else 0.0, "contextos_iguales_salvo_diseno": ctx_iguales,
                               "cumple": n_ok == n_tot and n_tot > 0 and all(ctx_iguales.values()), "segundos": round(time.time() - tp, 1)}
    doc["segundos"] = round(time.time() - t0, 1)
    doc["estado"] = "completo" if all("status" in b for b in doc["busquedas"]) else "parcial_por_tope"
    N.write_json_atomic(out, doc)
    print(json.dumps({"resumen": doc.get("resumen"), "dedup": doc["deduplicacion_GN"]["cumple"], "estado": doc["estado"], "s": doc["segundos"]}, default=str))


if __name__ == "__main__":
    raise SystemExit(main())
