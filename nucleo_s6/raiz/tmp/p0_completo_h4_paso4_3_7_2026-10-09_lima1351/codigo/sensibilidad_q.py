"""Medición PROPIA de la sensibilidad de Q en la opción B: corrección y costo (CIERRE DF Y PASO 4 3.7, NO OFICIAL).

  <py_integracion> -m codigo.sensibilidad_q <salida.json> <tope_s>

paper2b.robustness.q_sensitivity (sin cambios): para una afirmación robust_infeasible, m* = máx sobre el universo de
m_w = ((C2 + err + ε) λ y − D)/min Q; la afirmación deja de sostenerse para m < m*. En el universo CONTINUO de la opción B
(θ en el soporte continuo x contextos: vértice macro, estado nacional, celda externa), con λ = s_π/(1 − s(θ)) y
s = q_pot(θ) (cobertura.g_enclosure), y D, min Q, s_π, y dependientes solo del contexto:
   m_w(θ, c) = (Φ(θ) s_π,c y_c − D)/Q_c,   Φ(θ) = (C2(θ) + ε)/(1 − s(θ)),
creciente en Φ: m* = máx_c (Φ* s_π,c y_c − D)/Q_c con Φ* = sup_θ Φ(θ) (UNA sola rama y cota en θ para todos los
contextos). Φ* se encierra por rama y cota en θ (ejes de f; β̃ y η_d no intervienen) con el encierro normalizado de C2
sobre cajas (codigo/demo/c2_normalizado, el mismo de la cobertura) y s(caja) exacto; cota inferior en puntos admisibles.
CORRECCIÓN: (1) se evalúa RB.q_sensitivity del código sobre el universo testigo (punto de Φ* x contextos) y debe dar el
m* de la fórmula; (2) se evalúa RB.q_sensitivity sobre un universo de NUDOS L0 (muestra determinista de nudos x
contextos) y debe dar m*_nudos <= m*_continuo con el mismo estado; (3) G y su gemela N dan el mismo m* (C2_G = C2_N en f).
COSTO: segundos de preparación, de la rama y cota y por contexto. Afirmaciones: la robusta de menor margen (G, MEX f
histórica, sin_addback, micro), su gemela N y una primaria (G, addback_completo, macro).
"""
from __future__ import annotations

import hashlib
import heapq
import itertools
import json
import math
import sys
import time
from decimal import Decimal
from pathlib import Path

from codigo import testigos as T
from codigo.demo import c2_normalizado as C2N
from codigo.demo import nucleo_v as N
from codigo.demo.cobertura_compartida import q_pot_exact
from paper2b import cobertura as COV
from paper2b import robustness as RB
from paper2b.claims import EPS_ECON
from paper2b.intervalos import Iv

RES = N.AREA.parent / "resolucion_3_7_2026-10-04_lima1941"
RES_INV = "d6fd4e384c5309e3d5720813d4e8770d7b849ad0bd9e90d1a6534af2a7bfa17f"
AFIRMACIONES = [
    "CLM:PREG-COMPARACION-E1:historical_anchor:ci:MEX:f:conditional_full:G:sin_addback:micro:guardrail_deuda",
    "CLM:PREG-COMPARACION-E1:historical_anchor:ci:MEX:f:conditional_full:N:sin_addback:micro:guardrail_deuda",
    "CLM:PREG-COMPARACION-E1:primary:ci:MEX:f:conditional_full:G:addback_completo:macro:guardrail_deuda"]
IRREL_F = ("beta_tilde", "eta_d")


def autenticado(rel):
    raw_inv = (RES / "audit/entrega.json").read_bytes()
    N.need(hashlib.sha256(raw_inv).hexdigest() == RES_INV, "INVENTARIO_RESOLUCION")
    raw = (RES / rel).read_bytes()
    N.need(json.loads(raw_inv)["files"][rel]["sha256"] == hashlib.sha256(raw).hexdigest(), "NO_AUTENTICADO:" + rel)
    return json.loads(raw)


def phi_star(model, root, fixed, dis, tope, eps):
    """Rama y cota de sup_θ (C2 + ε)/(1 − s) sobre la caja raíz (menú f)."""
    bd, bf = float(fixed["bar_tau_d"]), float(fixed["bar_tau_f"])
    libres = [p for p in COV.STRUCT if root[p][1] > root[p][0] and p not in IRREL_F]
    W = {p: root[p][1] - root[p][0] for p in libres}

    def cota(b):
        c2 = C2N.c2_normalizado(model, b, dis, "f", bd, bf, fixed=fixed)
        s = q_pot_exact(b)
        if c2 is None or not s.hi < 1.0:
            return math.inf
        return ((Iv(c2.hi, c2.hi) + eps) / (1.0 - Iv(s.hi, s.hi))).hi

    def punto(b):
        pt = {p: ((lo + hi) / 2,) * 2 for p, (lo, hi) in b.items()}
        c2 = C2N.c2_normalizado(model, pt, dis, "f", bd, bf, fixed=fixed)
        s = q_pot_exact(pt)
        if c2 is None:
            return -math.inf, pt
        return ((Iv(c2.lo, c2.lo) + eps) / (1.0 - Iv(s.lo, s.lo))).lo, pt
    t0 = time.time()
    best = (-math.inf, None)
    # vértices de la caja (favorables a Φ: s alto y C2 alto)
    for combo in itertools.product(*[(root[p][0], root[p][1]) if p in ("kappa_tilde", "rho", "a", "phi", "eta_f") else ((root[p][0] + root[p][1]) / 2,)
                                     for p in COV.STRUCT]):
        vb = {p: (v, v) for p, v in zip(COV.STRUCT, combo)}
        if not COV.box_admissible(vb, fixed):
            continue
        v, pt = punto(vb)
        if v > best[0]:
            best = (v, pt)
    heap, cont, n = [(-cota(root), 0, root)], 1, 0
    while heap and time.time() - t0 < tope:
        nu, _, b = heapq.heappop(heap)
        if -nu - best[0] <= 1e-7:
            heapq.heappush(heap, (nu, cont, b))
            break
        n += 1
        ls = [p for p in libres if b[p][1] > b[p][0]]
        if not ls:
            heapq.heappush(heap, (nu, cont, b))
            break
        p = max(ls, key=lambda q: (b[q][1] - b[q][0]) / W[q])
        lo, hi = b[p]
        m = lo + (hi - lo) / 2
        for h in (dict(b, **{p: (lo, m)}), dict(b, **{p: (m, hi)})):
            if not COV.box_admissible(h, fixed):
                continue
            u = min(cota(h), -nu)
            v, pt = punto(h)
            if v > best[0]:
                best = (v, pt)
            if u > best[0]:
                heapq.heappush(heap, (-u, cont, h))
                cont += 1
    U = max(-heap[0][0], best[0]) if heap else best[0]
    return {"L": best[0], "U": U, "brecha": U - best[0], "cajas": n, "punto": {p: v[0] for p, v in best[1].items()},
            "segundos": round(time.time() - t0, 1), "estado": "convergido" if U - best[0] <= 1e-7 else "tope"}


def main():
    out, tope = Path(sys.argv[1]), float(sys.argv[2])
    t0 = time.time()
    reg = autenticado("demo/registro/registro_candidato_v4.json")["afirmaciones"]
    ctx = N.Contexto()
    COV.q_pot = q_pot_exact
    D = float(ctx.inp.dme_gai)
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "eps": EPS_ECON, "D_dme_gai": D, "contexto_s": round(time.time() - t0, 1),
           "afirmaciones": {}}
    phi_cache = {}
    for cid in AFIRMACIONES:
        N.need(reg[cid]["categoria"] == "robusta_infactible_certificada", "NO_ROBUSTA")
        dis = cid.split(":")[-4]
        tp = time.time()
        st = T.preparar(ctx, dis, [cid])
        prep_s = round(time.time() - tp, 1)
        fx, axes = st["fixed"], st["axes"]
        root = {p: (axes[p][0][0], axes[p][-1][1]) for p in COV.STRUCT}
        cx = st["univ"][cid]
        clave = json.dumps({p: list(v) for p, v in root.items()}, sort_keys=True)
        tp = time.time()
        if clave not in phi_cache:
            # C2_G = C2_N en f: el encierro de G vale para las dos (se comprueba abajo con N en un punto)
            phi_cache[clave] = phi_star(st["model"], root, fx, "G", tope, EPS_ECON)
        ph = phi_cache[clave]
        bb_s = round(time.time() - tp, 1)
        tp = time.time()
        filas = []
        for c in cx:
            Q = c.n_min - D
            filas.append({"Q": Q, "s_pi": c.s_pi, "gain": c.gain,
                          "m_L": (ph["L"] * c.s_pi * c.gain - D) / Q, "m_U": (ph["U"] * c.s_pi * c.gain - D) / Q})
        mL = max(f["m_L"] for f in filas)
        mU = max(f["m_U"] for f in filas)
        ctx_s = round(time.time() - tp, 3)
        # (1) RB.q_sensitivity del código sobre el universo testigo (punto de Φ* x contextos)
        pt = ph["punto"]
        bpt = {p: (v, v) for p, v in pt.items()}
        c2pt = C2N.c2_normalizado(st["model"], bpt, dis, "f", float(fx["bar_tau_d"]), float(fx["bar_tau_f"]), fixed=fx)
        s_pt = q_pot_exact(bpt)
        uni = [{"C2": c2pt.lo, "err": c2pt.hi - c2pt.lo, "lambda": c.s_pi / (1.0 - s_pt.lo), "gain": c.gain, "D": D, "Qs": [c.n_min - D],
                "key": (i,)} for i, c in enumerate(cx)]
        r_cont = RB.q_sensitivity("robust_infeasible", uni)
        uni0 = [dict(u, err=0.0) for u in uni]
        r_cont0 = RB.q_sensitivity("robust_infeasible", uni0)
        # fórmula en el MISMO punto testigo (C2 = cota inferior puntual, sin err)
        phi_pt = (c2pt.lo + EPS_ECON) / (1.0 - s_pt.lo)
        m_pt = max((phi_pt * c.s_pi * c.gain - D) / (c.n_min - D) for c in cx)
        err_pt = c2pt.hi - c2pt.lo
        # (2) universo de NUDOS L0: muestra determinista (hash) de nudos estructurales x todos los contextos
        sid = st["claims"][cid].support_sets[0]
        nodos = N.axes_nodes(ctx, sid)
        # muestra determinista SIN enumerar la malla: índice de cada eje por sha256("SEL-Q-NUDOS-v1|k|eje")
        orden = list(range(60))
        uni_n = []
        tp = time.time()
        for i in orden:
            vb = {}
            for p in COV.STRUCT:
                xs = [float(x) for x in nodos[p]]
                v = xs[int(hashlib.sha256(("SEL-Q-NUDOS-v1|%d|%s" % (i, p)).encode()).hexdigest(), 16) % len(xs)]
                vb[p] = (v, v)
            if not COV.box_admissible(vb, fx):
                continue
            c2 = C2N.c2_normalizado(st["model"], vb, dis, "f", float(fx["bar_tau_d"]), float(fx["bar_tau_f"]), fixed=fx)
            s = q_pot_exact(vb)
            for k, c in enumerate(cx):
                uni_n.append({"C2": c2.lo, "err": c2.hi - c2.lo, "lambda": c.s_pi / (1.0 - s.lo), "gain": c.gain, "D": D,
                              "Qs": [c.n_min - D], "key": (i, k)})
        nod_s = round(time.time() - tp, 1)
        r_nod = RB.q_sensitivity("robust_infeasible", uni_n)
        # (3) identidad G/N en f en el punto de Φ*
        c2N = C2N.c2_normalizado(st["model"], bpt, "N", "f", float(fx["bar_tau_d"]), float(fx["bar_tau_f"]), fixed=fx)
        doc["afirmaciones"][cid] = {
            "diseno": dis, "contextos": len(cx), "preparacion_s": prep_s, "rama_y_cota_s": bb_s, "por_contexto_s": ctx_s,
            "Phi_estrella": ph, "m_estrella_continuo": [mL, mU], "estado_formula": "breakdown_found" if 0 < mL and mU < 1 else "ver",
            "codigo_universo_testigo": {"status": r_cont.status, "m_Q_critical": r_cont.m_Q_critical, "m_Q_critical_err0": r_cont0.m_Q_critical,
                                        "formula_en_el_punto": m_pt, "err_encierro_puntual": err_pt},
            "codigo_universo_nudos": {"status": r_nod.status, "m_Q_critical": r_nod.m_Q_critical, "nudos": len(orden), "filas": len(uni_n), "segundos": nod_s},
            "C2_G_igual_N_en_el_punto": [list((c2pt.lo, c2pt.hi)), list((c2N.lo, c2N.hi))]}
        a = doc["afirmaciones"][cid]
        a["comprobaciones"] = {
            "formula_igual_codigo_en_testigo_err0": r_cont0.m_Q_critical is not None and abs(r_cont0.m_Q_critical - m_pt) <= 1e-12 * max(1.0, abs(m_pt)),
            "codigo_con_err_conservador": r_cont.m_Q_critical is not None and r_cont.m_Q_critical >= r_cont0.m_Q_critical,
            "punto_testigo_dentro_del_encierro_continuo": mL - 1e-12 <= m_pt <= mU + 1e-12,
            "nudos_no_superan_continuo": r_nod.m_Q_critical is None or r_nod.m_Q_critical <= mU + 1e-12,
            "mismo_estado_nudos_y_continuo": r_nod.status == r_cont.status,
            "C2_G_igual_N": abs(c2pt.lo - c2N.lo) <= 1e-12 and abs(c2pt.hi - c2N.hi) <= 1e-12}
        N.write_json_atomic(out, doc)
    ms = {k: v["m_estrella_continuo"] for k, v in doc["afirmaciones"].items()}
    gk = [k for k in ms if ":G:" in k and k.replace(":G:", ":N:") in ms]
    doc["G_N_mismo_m_estrella"] = all(abs(ms[k][0] - ms[k.replace(":G:", ":N:")][0]) <= 1e-12 and abs(ms[k][1] - ms[k.replace(":G:", ":N:")][1]) <= 1e-12 for k in gk)
    doc["cumple_todo"] = doc["G_N_mismo_m_estrella"] and all(all(v["comprobaciones"].values()) for v in doc["afirmaciones"].values())
    doc["segundos"] = round(time.time() - t0, 1)
    N.write_json_atomic(out, doc)
    print(json.dumps({"cumple_todo": doc["cumple_todo"], "m": ms, "segundos": doc["segundos"]}, ensure_ascii=False))


if __name__ == "__main__":
    raise SystemExit(main())
