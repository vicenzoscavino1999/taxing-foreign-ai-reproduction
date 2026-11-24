"""Extremos sup_ω G e inf_ω G de las afirmaciones ci-d (EXTREMOS df/d 3.7, NO OFICIAL): la ruta desde los extremos de C2
hasta los de G con C2 y K1 en el MISMO ω, y la diferencia entre la combinación INDIVIDUAL (sup C2 − mín K1 en ω
distintos, prohibida por el catálogo) y la CONJUNTA.

  <py_integracion> -m codigo.extremos_G_d <salida.json> <tope_s>

Estructura demostrada para el menú d (review/METODO_EXTREMOS_DF_D.md §2.3):
- C2(θ) <= g* (1 − [N] s), s = q_pot(θ) = κ̃ (a−1)/(a−ρ), g* = max τ (1−τ)^η = 0,6 · 0,4^0,1 (η_d >= 0,1, τ <= 0,6);
- K1_c(θ) = n_min (1 − s) / (s_π gain) (cobertura.g_enclosure: λ = s_π / (1 − q_pot)): depende de θ SOLO por s y es
  LINEAL en s;
- por lo tanto sup_θ G_c <= max_{s ∈ [s_min, s_max]} [g* (1 − [N] s) − K1_c(s)], función LINEAL de s: el máximo está en
  un extremo, s_min (κ̃ = 0,005, a = 1,1, ρ = 0,4) o s_max (κ̃ = 0,2, ρ = 1).
- Cota inferior en los dos puntos ADMISIBLES p_min y p_max (β̃ = 0,25, z_cost = 1, η_d = 0,1, u_θ = 0,5): C2 certificado
  (techo puntual sup_bound) y K1_c en el mismo punto. En ambos puntos todas las empresas son formales antes y después, así
  que C2(p) = g* (1 − [N] s(p)) salvo redondeo: la brecha es la del techo puntual más el ancho de K1.
inf: cota inferior global L = min_c [0 − K1_c(Θ).hi] (C2 >= 0); superior en el punto del ínfimo de C2 (demo/C2/inf_*_d.json)
con K1 en el mismo punto. Se informa sin forzar convergencia.
Comparación INDIVIDUAL: U_ind = max_c [sup C2 − K1_c(Θ).lo] (sup de C2 en un ω y mínimo de K1 en otro).
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

AREA = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AREA / "integracion/src"))
import paper2b  # noqa: E402

assert Path(paper2b.__file__).resolve().parent == (AREA / "integracion/src/paper2b").resolve(), "PAPER2B_NO_AISLADO"
from codigo import extremos_dfd as XD  # noqa: E402
from codigo import extremos_G as EG  # noqa: E402
from codigo.demo import nucleo_v as N  # noqa: E402
from codigo.demo.cobertura_compartida import q_pot_exact  # noqa: E402
from paper2b import cobertura as COV  # noqa: E402
from paper2b import encierros_modelo as EM  # noqa: E402
from paper2b.intervalos import Iv  # noqa: E402

T2_G = 1e-4
PREV = N.ROOT / "tmp/resolucion_3_7_2026-10-04_lima1941"
PREV_INV = "d6fd4e384c5309e3d5720813d4e8770d7b849ad0bd9e90d1a6534af2a7bfa17f"
BASE = {"beta_tilde": 0.25, "z_cost": 1.0, "eta_d": 0.1, "u_theta": 0.5, "eta_f": 4.05, "phi": 0.5}
P_MIN = dict(BASE, a=1.1, rho=0.4, kappa_tilde=0.005)
P_MAX = dict(BASE, a=1.1, rho=1.0, kappa_tilde=0.2)


def g_estrella() -> Iv:
    t = Iv(0.6, 0.6)
    return t * EM.iexp(Iv(0.1, 0.1) * EM.ilog1m(t))


def main():
    out, tope = Path(sys.argv[1]), float(sys.argv[2])
    t0 = time.time()
    ctx = N.Contexto()
    COV.q_pot = q_pot_exact
    reg = EG.auth(PREV, PREV_INV, "demo/registro/registro_candidato_v4.json")["afirmaciones"]
    cd = sorted(k for k in reg if k.split(":")[3] == "ci" and k.split(":")[5] == "d")
    gs = g_estrella()
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "identidad_sha256": ctx.identity_sha256, "T2_G": T2_G, "universo": len(cd),
           "g_estrella": [gs.lo, gs.hi], "p_min": P_MIN, "p_max": P_MAX, "afirmaciones": {}, "C2": {}}
    for d in ("G", "N"):
        cids = [c for c in cd if c.split(":")[-4] == d]
        st = EG.preparar(ctx, d, cids)
        fixed, axes = st["fixed"], st["axes"]
        bd, bf = float(fixed["bar_tau_d"]), float(fixed["bar_tau_f"])
        root = {p: (axes[p][0][0], axes[p][-1][1]) for p in COV.STRUCT}
        bmin = {p: (v, v) for p, v in P_MIN.items()}
        bmax = {p: (v, v) for p, v in P_MAX.items()}
        N.need(all(COV.box_admissible(b, fixed) for b in (root, bmin, bmax)), "NO_ADMISIBLE")
        s_min, s_max = q_pot_exact(bmin), q_pot_exact(bmax)
        c2p = {k: XD.c2_punto_cert(pt, fixed, d, "d", bd, bf) for k, pt in (("p_min", P_MIN), ("p_max", P_MAX))}
        sup_json = json.loads((AREA / f"demo/C2/sup_{d}_d.json").read_text(encoding="utf-8"))
        inf_p = AREA / f"demo/C2/inf_{d}_d.json"
        inf_json = json.loads(inf_p.read_text(encoding="utf-8")) if inf_p.exists() else None
        p_inf = (inf_json or {}).get("punto_cota_superior")
        c2inf = XD.c2_punto_cert(p_inf, fixed, d, "d", bd, bf) if p_inf else None
        binf = {p: (p_inf[p], p_inf[p]) for p in COV.STRUCT} if p_inf else None
        doc["C2"][d] = {"p_min": c2p["p_min"], "p_max": c2p["p_max"], "s_min": [s_min.lo, s_min.hi], "s_max": [s_max.lo, s_max.hi],
                        "sup_C2": [sup_json["L"], sup_json["U"], sup_json["estado"]], "inf_C2_punto": c2inf, "punto_inf": p_inf,
                        "cota_C2_en_s": "g* (1 - s)" if d == "N" else "g*"}
        fac = (lambda s: Iv(1.0, 1.0) - s) if d == "N" else (lambda s: Iv(1.0, 1.0))
        for cid in cids:
            if time.time() - t0 > tope:
                doc["afirmaciones"][cid] = {"estado": "no_procesada_por_tope"}
                continue
            cx = st["univ"][cid]
            if not cx:
                doc["afirmaciones"][cid] = {"estado": "incompleta", "motivo": "CONTEXTOS_VACIOS"}
                continue
            mk1 = lambda b, c: COV.g_enclosure(st["model"], b, c, fixed, Iv(0.0, 0.0))   # noqa: E731  (= −K1)
            U = L = U_ind = Linf = Uinf = -math.inf
            Linf, Uinf = math.inf, math.inf
            ok = True
            for c in cx:
                km = [mk1(b, c) for b in (bmin, bmax, root)]
                if any(k is None for k in km):
                    ok = False
                    break
                k1min, k1max, k1box = (-k for k in km)
                ub = max((gs * fac(s_min) - k1min).hi, (gs * fac(s_max) - k1max).hi)       # lineal en s: extremos
                lb = max(c2p["p_min"][0] - k1min.hi, c2p["p_max"][0] - k1max.hi)
                U, L = max(U, ub), max(L, lb)
                U_ind = max(U_ind, sup_json["U"] - k1box.lo)
                Linf = min(Linf, 0.0 - k1box.hi)
                if binf is not None:
                    ki = -mk1(binf, c)
                    Uinf = min(Uinf, c2inf[1] - ki.lo)
            if not ok:
                doc["afirmaciones"][cid] = {"estado": "incompleta", "motivo": "G_INDEFINIDA_EN_ALGUN_CONTEXTO", "contextos": len(cx)}
                continue
            doc["afirmaciones"][cid] = {"categoria_v4": reg[cid]["categoria"], "contextos": len(cx), "sup_G": [L, U], "brecha_sup": U - L,
                                        "sup_G_individual_U": U_ind, "exceso_individual": U_ind - U,
                                        "inf_G": [Linf, Uinf], "brecha_inf": Uinf - Linf,
                                        "estado_sup": "convergida" if U - L <= T2_G else "no_convergida",
                                        "estado_inf": "convergida" if Uinf - Linf <= T2_G else "no_convergida"}
        N.write_json_atomic(out, doc)
    a = [v for v in doc["afirmaciones"].values() if "sup_G" in v]
    doc["resumen"] = {
        "procesadas": len(a), "sup_convergidas": sum(1 for v in a if v["estado_sup"] == "convergida"),
        "inf_convergidas": sum(1 for v in a if v["estado_inf"] == "convergida"),
        "max_brecha_sup": max((v["brecha_sup"] for v in a), default=None),
        "max_exceso_individual_sobre_conjunto": max((v["exceso_individual"] for v in a), default=None),
        "por_diseno": {d: {"sup_convergidas": sum(1 for k, v in doc["afirmaciones"].items() if "sup_G" in v and k.split(":")[-4] == d and v["estado_sup"] == "convergida"),
                           "max_exceso_individual": max((v["exceso_individual"] for k, v in doc["afirmaciones"].items() if "sup_G" in v and k.split(":")[-4] == d), default=None)}
                       for d in ("G", "N")},
        "coherencia_con_registro_v4": {
            "robustas_con_sup_U_menor_que_menos_eps": sum(1 for v in a if v["categoria_v4"] == "robusta_infactible_certificada" and v["sup_G"][1] <= -0.01),
            "robustas": sum(1 for v in a if v["categoria_v4"] == "robusta_infactible_certificada"),
            "cambio_de_signo_con_sup_L_mayor_o_igual_eps": sum(1 for v in a if v["categoria_v4"] == "cambio_de_signo_certificado" and v["sup_G"][0] >= 0.01),
            "cambio_de_signo": sum(1 for v in a if v["categoria_v4"] == "cambio_de_signo_certificado")}}
    doc["segundos"] = round(time.time() - t0, 1)
    N.write_json_atomic(out, doc)
    print(json.dumps(doc["resumen"], ensure_ascii=False))


if __name__ == "__main__":
    raise SystemExit(main())
