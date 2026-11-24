"""Extremos sup_ω G e inf_ω G CONVERGIDOS (encierro certificado <= T2_G) para las afirmaciones del menú f
(CIERRE CANDIDATO 3.7, NO OFICIAL; §19.6 del antecedente incorporado por DI-08; matriz review/MATRIZ_CONTRACTUAL.md).

  <py_integracion> -m codigo.extremos_G <salida.json> <tope_s>

Universo: las 320 afirmaciones country_instrument con instrumento f del registro candidato v4 (160 G, 160 N), cada una
con TODOS sus contextos (cobertura.Universo, como la cobertura). Dominio: soporte estructural COMPLETO × contextos.
G(ω) = C2(θ) − K1(θ, contexto) con C2 y K1 en el MISMO ω (catálogo: no combinar sup C2 de un ω con inf K1 de otro).

Cotas, por afirmación (máximo / mínimo sobre sus contextos c):
- sup: U = max_c [C2(Θ).hi − K1_c(Θ).lo] con Θ = soporte completo (cota VÁLIDA: para todo ω de la caja, C2(θ) <= C2(Θ).hi
  y K1_c(θ) >= K1_c(Θ).lo); L = max_c [C2(p⁺).lo − K1_c(p⁺).hi] en el punto ADMISIBLE p⁺ del supremo de C2(f)
  (envolventes de certificacion_3_7, autenticadas), C2 puntual certificado y K1 en el mismo p⁺.
- inf: L = min_c [C2(Θ).lo − K1_c(Θ).hi]; U = min_c [C2(p⁻).hi − K1_c(p⁻).lo] en el punto admisible p⁻ del ínfimo de C2(f).
Convergido si U − L <= T2_G = 1e-4 en ambos extremos. Por qué puede cerrar sin subdividir (no se supone, se comprueba):
en p⁺ (a = 1,1, κ̃ = 0,2, ρ = 1) q_pot = κ̃ (a−1)/(a−ρ) = κ̃ = máximo de q_pot en la caja (ρ = 1 hace q_pot = κ̃ para todo a),
así que K1_c es mínima en el mismo ω donde C2 es máxima; en p⁻ (κ̃ = 0,005, ρ = 0,4, a = 1,1) q_pot es mínimo y K1_c
máxima donde C2 es mínima. Si para alguna afirmación no converge, se informa su hueco (no se fuerza).
C2 de la caja completa y de los puntos: c2_normalizado con los motores G y N (la equivalencia en f se comprueba aquí).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from codigo.demo import nucleo_v as N
from codigo.demo import c2_normalizado as C2N
from codigo.demo.cobertura_compartida import q_pot_exact
from paper2b import cobertura as COV

T2_G = 1e-4
CERT = N.ROOT / "tmp/certificacion_3_7_2026-10-04"
CERT_INV = "99d51784614d96a099bc3371028818d45851146e3c088131fda902dcf81ce8e5"
PREV = N.ROOT / "tmp/resolucion_3_7_2026-10-04_lima1941"
PREV_INV = "d6fd4e384c5309e3d5720813d4e8770d7b849ad0bd9e90d1a6534af2a7bfa17f"


def auth(base, inv_h, rel):
    inv_raw = (base / "audit/entrega.json").read_bytes()
    N.need(N.sha(inv_raw) == inv_h, "INVENTARIO:" + base.name)
    raw = (base / rel).read_bytes()
    N.need(json.loads(inv_raw)["files"][rel]["sha256"] == N.sha(raw), "NO_AUTENTICADO:" + rel)
    return json.loads(raw)


def preparar(ctx, dis, cids):
    """Copia de testigos.preparar SIN la restricción a las candidatas de rondas anteriores (aquí el universo es el de las
    afirmaciones f del registro v4): contextos oficiales por conjunto (Universo), fijos y ejes comunes comprobados."""
    from decimal import Decimal
    from codigo.demo import cobertura_mejorada as CM
    from codigo.demo.universo import Universo, qmin_table
    from paper2b import run as RUNMOD
    claims = {c.claim_id: c for c in ctx.claims}
    sets = sorted({s for cid in cids for s in claims[cid].support_sets})
    runs = {sid: ctx.run(sid, "extremos:" + sid) for sid in sets}
    ref_sid = claims[CM.CLAIM_P3B].support_sets[0]
    if ref_sid not in runs:
        runs[ref_sid] = ctx.run(ref_sid, "extremos:" + ref_sid)
    axes = runs[ref_sid].struct_axes(ref_sid)
    N.need(all(runs[s].struct_axes(s) == axes for s in runs), "EJES_DISTINTOS_NO_SE_COMPARTE")
    ax0 = N.axes_nodes(ctx, ref_sid)
    corner = {p: Decimal(str(ax0[p][0])) for p in RUNMOD.STRUCT}
    U = Universo(runs, qmin_table(ctx.inp.grid_cells))
    univ, fixed_ref, fx_set = {}, None, set()
    for cid in cids:
        cl = claims[cid]
        cx = []
        for sid in cl.support_sets:
            c, fx = U.contexts(cl, sid, corner)
            cx += [x for x, _ in c]
            fixed_ref = fixed_ref or fx
            fx_set.add(json.dumps(fx, sort_keys=True, default=str))
        univ[cid] = cx
    N.need(len(fx_set) == 1, "FIJOS_DISTINTOS")
    return {"univ": univ, "fixed": fixed_ref, "model": runs[ref_sid].model, "axes": axes}


def main():
    out, tope = Path(sys.argv[1]), float(sys.argv[2])
    t0 = time.time()
    ctx = N.Contexto()
    COV.q_pot = q_pot_exact
    reg = auth(PREV, PREV_INV, "demo/registro/registro_candidato_v4.json")["afirmaciones"]
    env = {d: [g for g in auth(CERT, CERT_INV, f"demo/C2/envolventes_{k}.json")["grupos"] if g["instrumento"] == "f" and g["diseno"] == d][0]
           for k, d in ((0, "G"), (1, "N"))}
    p_sup = {p: (float(v), float(v)) for p, v in env["G"]["sup"]["punto_L"].items()}
    p_inf = {p: (float(v), float(v)) for p, v in env["G"]["inf"]["punto_U"].items()}
    cf = sorted(k for k in reg if k.split(":")[3] == "ci" and k.split(":")[5] == "f")
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "identidad_sha256": ctx.identity_sha256, "T2_G": T2_G, "universo": len(cf),
           "puntos": {"sup_C2": env["G"]["sup"]["punto_L"], "inf_C2": env["G"]["inf"]["punto_U"]}, "afirmaciones": {}}
    for d in ("G", "N"):
        cids = [c for c in cf if c.split(":")[-4] == d]
        st = preparar(ctx, d, cids)
        fixed, axes = st["fixed"], st["axes"]
        bd, bf = float(fixed["bar_tau_d"]), float(fixed["bar_tau_f"])
        root = {p: (axes[p][0][0], axes[p][-1][1]) for p in COV.STRUCT}
        N.need(COV.box_admissible(root, fixed) and COV.box_admissible(p_sup, fixed) and COV.box_admissible(p_inf, fixed), "NO_ADMISIBLE")
        c2 = {k: C2N.c2_normalizado(st["model"], b, d, "f", bd, bf, fixed=fixed) for k, b in (("caja", root), ("p_sup", p_sup), ("p_inf", p_inf))}
        doc["C2_" + d] = {k: [v.lo, v.hi] for k, v in c2.items()}
        for cid in cids:
            if time.time() - t0 > tope:
                doc["afirmaciones"][cid] = {"estado": "no_procesada_por_tope"}
                continue
            cx = st["univ"][cid]
            gb = [COV.g_enclosure(st["model"], root, c, fixed, c2["caja"]) for c in cx]
            gs = [COV.g_enclosure(st["model"], p_sup, c, fixed, c2["p_sup"]) for c in cx]
            gi = [COV.g_enclosure(st["model"], p_inf, c, fixed, c2["p_inf"]) for c in cx]
            if not cx or any(g is None for g in gb + gs + gi):
                doc["afirmaciones"][cid] = {"estado": "incompleta", "motivo": "CONTEXTOS_VACIOS_O_G_INDEFINIDA", "contextos": len(cx)}
                continue
            sup = [max(g.lo for g in gs), max(g.hi for g in gb)]
            inf = [min(g.lo for g in gb), min(g.hi for g in gi)]
            conv = (sup[1] - sup[0] <= T2_G) and (inf[1] - inf[0] <= T2_G)
            doc["afirmaciones"][cid] = {"categoria_v4": reg[cid]["categoria"], "contextos": len(cx), "sup_G": sup, "brecha_sup": sup[1] - sup[0],
                                        "inf_G": inf, "brecha_inf": inf[1] - inf[0], "estado": "convergida" if conv else "no_convergida"}
        N.write_json_atomic(out, doc)
    a = [v for v in doc["afirmaciones"].values() if "sup_G" in v]
    doc["resumen"] = {"procesadas": len(a), "convergidas": sum(1 for v in a if v["estado"] == "convergida"),
                      "max_brecha_sup": max((v["brecha_sup"] for v in a), default=None), "max_brecha_inf": max((v["brecha_inf"] for v in a), default=None),
                      "coherencia_con_registro": {
                          "robusta_infactible_con_sup_U_menor_que_menos_eps": sum(1 for v in a if v["categoria_v4"] == "robusta_infactible_certificada" and v["sup_G"][1] <= -0.01),
                          "robustas": sum(1 for v in a if v["categoria_v4"] == "robusta_infactible_certificada"),
                          "cambio_de_signo_con_sup_L_mayor_o_igual_eps_e_inf_U_menor_o_igual_menos_eps": sum(
                              1 for v in a if v["categoria_v4"] == "cambio_de_signo_certificado" and v["sup_G"][0] >= 0.01 and v["inf_G"][1] <= -0.01),
                          "cambio_de_signo": sum(1 for v in a if v["categoria_v4"] == "cambio_de_signo_certificado")},
                      "equivalencia_G_N": doc["C2_G"] == doc["C2_N"]}
    doc["segundos"] = round(time.time() - t0, 1)
    N.write_json_atomic(out, doc)
    print(json.dumps(doc["resumen"], ensure_ascii=False))


if __name__ == "__main__":
    raise SystemExit(main())
