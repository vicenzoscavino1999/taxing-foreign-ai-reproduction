"""inf_ω G de las afirmaciones ci-d por PARTICIÓN en a (CIERRE DF Y PASO 4 3.7, NO OFICIAL). Versión candidata v2,
separada de codigo/extremos_G_d_inf.py (GEXTI2: 0/160 convergidas en G porque el mínimo de C2 está en a = 2,5 y el máximo
de K1 en s mínimo, a = 1,1: la combinación individual no basta).

  <py_integracion> -m codigo.extremos_G_d_inf_v3 <salida.json> <M_subintervalos_a> <K_puntos_a> <tope_s> <seleccion.json>

VERSIÓN v3 (CIERRE DF Y PASO 4 3.7): igual que v2, restringida a la lista de afirmaciones de <seleccion.json> (regla de
selección declarada en ese archivo) y con la cota inferior de la COMBINACIÓN INDIVIDUAL en el mismo proceso
(G: H_min − k_c (1 − s_min,global); N: H_min (1 − s_max,global) − k_c (1 − s_min,global)), para medir la diferencia
conjunta − individual por afirmación.

Hechos usados (review/FUNDAMENTO_COTAS_POR_DISENO.md §7 y §9):
- K1_c(θ) = n_min (1 − s)/(s_π gain), s = q_pot(θ) (cobertura.g_enclosure: λ = s_π/(1 − q_pot)): k_c = n_min/(s_π gain)
  depende solo del contexto y K1_c = k_c (1 − s) EXACTAMENTE;
- menú d, «todos formales» (inf_cota_formal.cota_inf_tau): para todo τ_d factible en G, C2_G(θ) >= τ_d r* =: h y
  C2_N(θ) >= τ_d r* (1 − s) (las condiciones de G implican las de N en d); H(A) = mejor_tau de G sobre la caja con a ∈ A y
  los demás ejes en su rango COMPLETO es cota inferior de h en esa caja.
Para cada contexto c y subintervalo A_i de a (κ̃, ρ y el resto en su rango completo; s ∈ [s_min(A_i), s_max(A_i)]):
  G: inf G_c >= H_i − k_c.hi (1 − s_min(A_i));
  N: G_c >= (h − k_c)(1 − s) >= (H_i − k_c.hi)(1 − s), mínimo en s_min si H_i − k_c.hi < 0 (si no, en s_max).
Cota inferior de la afirmación: min sobre contextos y subintervalos. Cota superior (MISMO ω): en K puntos admisibles
p_j = (a_j, κ̃ = κ̃_min, ρ = ρ_min, z_cost = 100, u_θ = 0,9, β̃ = 4, η_d = 4), C2(p_j).hi (techo certificado) − K1_c(p_j).lo,
con K1_c(p_j) por la misma fórmula exacta en intervalos; el mejor punto se recomprueba con cobertura.g_enclosure.
Convergida si U − L <= T2 = 1e-4.
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
from codigo import inf_cota_formal_v2 as ICF  # noqa: E402
from codigo.demo import nucleo_v as N  # noqa: E402
from codigo.demo.cobertura_compartida import q_pot_exact  # noqa: E402
from paper2b import cobertura as COV  # noqa: E402
from paper2b.intervalos import Iv  # noqa: E402

T2_G = 1e-4
PREV = N.ROOT / "tmp/resolucion_3_7_2026-10-04_lima1941"
PREV_INV = "d6fd4e384c5309e3d5720813d4e8770d7b849ad0bd9e90d1a6534af2a7bfa17f"
ESQ = {"z_cost": 100.0, "u_theta": 0.9, "beta_tilde": 4.0, "eta_d": 4.0, "eta_f": 4.05, "phi": 0.5}


def main():
    out, M, K, tope = Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
    sel = json.loads(Path(sys.argv[5]).read_text(encoding="utf-8"))
    t0 = time.time()
    ctx = N.Contexto()
    COV.q_pot = q_pot_exact
    reg = EG.auth(PREV, PREV_INV, "demo/registro/registro_candidato_v4.json")["afirmaciones"]
    cd = sorted(k for k in reg if k.split(":")[3] == "ci" and k.split(":")[5] == "d")
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "identidad_sha256": ctx.identity_sha256, "T2_G": T2_G, "universo": len(cd),
           "M": M, "K": K, "esquina": ESQ, "seleccion": sel, "C2": {}, "afirmaciones": {}}
    for d in ("G", "N"):
        cids = [c for c in cd if c.split(":")[-4] == d and c in set(sel["afirmaciones"])]
        if not cids:
            continue
        st = EG.preparar(ctx, d, cids)
        fixed, axes = st["fixed"], st["axes"]
        bd, bf = float(fixed["bar_tau_d"]), float(fixed["bar_tau_f"])
        root = {p: (axes[p][0][0], axes[p][-1][1]) for p in COV.STRUCT}
        a0, a1 = root["a"]
        kmin, rmin = root["kappa_tilde"][0], root["rho"][0]
        tp = time.time()
        sub = []
        for i in range(M):
            A = (a0 + (a1 - a0) * i / M, a0 + (a1 - a0) * (i + 1) / M if i < M - 1 else a1)
            bA = dict(root, a=A)
            H, _ = ICF.mejor_tau(bA, fixed, "G", "d", bd, bf)        # condiciones de G (implican las de N en d)
            smin = q_pot_exact(dict(bA, kappa_tilde=(kmin, kmin), rho=(rmin, rmin), a=(A[0], A[0]))).lo
            sfull = q_pot_exact(bA)
            sub.append((A, H, min(smin, sfull.lo), sfull.hi))
        t_sub = round(time.time() - tp, 1)
        tp = time.time()
        pts = []
        for j in range(K):
            aj = a0 + (a1 - a0) * j / (K - 1)
            pt = dict(ESQ, a=aj, kappa_tilde=kmin, rho=rmin)
            bx = {p: (pt[p], pt[p]) for p in COV.STRUCT}
            if not COV.box_admissible(bx, fixed):
                continue
            c2 = XD.c2_punto_cert(pt, fixed, d, "d", bd, bf)
            pts.append((pt, bx, c2, q_pot_exact(bx)))
        t_pts = round(time.time() - tp, 1)
        doc["C2"][d] = {"H_min": min(h for _, h, _, _ in sub), "H_en_a_max": sub[-1][1], "subintervalos_sin_tau": sum(1 for _, h, _, _ in sub if h == -math.inf),
                        "techos": [[p["a"], c[0], c[1]] for p, _, c, _ in pts], "segundos_subintervalos": t_sub, "segundos_techos": t_pts}
        N.write_json_atomic(out, doc)
        for cid in cids:
            if time.time() - t0 > tope:
                doc["afirmaciones"][cid] = {"estado": "no_procesada_por_tope"}
                continue
            cx = st["univ"][cid]
            if not cx:
                doc["afirmaciones"][cid] = {"estado": "incompleta", "motivo": "CONTEXTOS_VACIOS"}
                continue
            L, U, arg = math.inf, math.inf, None
            L_ind = math.inf
            Hmin = min(h for _, h, _, _ in sub)
            smin_g, smax_g = min(x[2] for x in sub), max(x[3] for x in sub)
            ok = True
            for c in cx:
                if not (c.s_pi > 0 and c.gain > 0):
                    ok = False
                    break
                k = Iv(c.n_min, c.n_min) / (Iv(c.s_pi, c.s_pi) * Iv(c.gain, c.gain))
                c2_ind = Iv(Hmin, Hmin) if d == "G" else Iv(Hmin, Hmin) * (1.0 - Iv(smax_g, smax_g))
                L_ind = min(L_ind, (c2_ind - k * (1.0 - Iv(smin_g, smin_g))).lo)
                for A, H, smin, smax in sub:
                    if H == -math.inf:
                        L = -math.inf
                        break
                    if d == "G":
                        v = Iv(H, H) - k * (1.0 - Iv(smin, smin))
                        lb = v.lo
                    else:
                        dif = Iv(H, H) - k
                        lb = (dif * (1.0 - Iv(smin, smin))).lo if dif.lo < 0.0 else (dif * (1.0 - Iv(smax, smax))).lo
                    if lb < L:
                        L = lb
                for pt, bx, c2, s in pts:
                    u = c2[1] - (k * (1.0 - s)).lo
                    if u < U:
                        U, arg = u, (pt, bx, c)
            if not ok:
                doc["afirmaciones"][cid] = {"estado": "incompleta", "motivo": "CONTEXTO_SIN_K1", "contextos": len(cx)}
                continue
            # recomprobación directa del techo conjunto en el mejor punto con cobertura.g_enclosure (mismo ω)
            pt, bx, c = arg
            g = COV.g_enclosure(st["model"], bx, c, fixed, Iv(*XD.c2_punto_cert(pt, fixed, d, "d", bd, bf)))
            U_dir = g.hi if g is not None else math.inf
            doc["afirmaciones"][cid] = {"categoria_v4": reg[cid]["categoria"], "contextos": len(cx), "inf_G": [L, max(U, U_dir) if U_dir < math.inf else U],
                                        "U_directo": U_dir, "brecha_inf": (max(U, U_dir) if U_dir < math.inf else U) - L, "a_cota_superior": pt["a"],
                                        "punto_cota_superior": pt, "L_individual": L_ind, "diferencia_conjunta_menos_individual": L - L_ind,
                                        "mismo_estado": {"C2_y_K1_en_el_mismo_punto": True, "s_del_punto": [arg[1] and q_pot_exact(bx).lo, q_pot_exact(bx).hi]}}
            v = doc["afirmaciones"][cid]
            v["estado_inf"] = "convergida" if v["brecha_inf"] <= T2_G else "no_convergida"
        N.write_json_atomic(out, doc)
    a = [v for v in doc["afirmaciones"].values() if "inf_G" in v]
    doc["resumen"] = {
        "procesadas": len(a), "inf_convergidas": sum(1 for v in a if v["estado_inf"] == "convergida"),
        "max_brecha_inf": max((v["brecha_inf"] for v in a), default=None),
        "por_diseno": {d: sum(1 for k, v in doc["afirmaciones"].items() if "inf_G" in v and k.split(":")[-4] == d and v["estado_inf"] == "convergida")
                       for d in ("G", "N")},
        "coherencia_con_registro_v4": {
            "cambio_de_signo": sum(1 for v in a if v["categoria_v4"] == "cambio_de_signo_certificado"),
            "cambio_de_signo_con_inf_U_menor_o_igual_menos_eps": sum(1 for v in a if v["categoria_v4"] == "cambio_de_signo_certificado" and v["inf_G"][1] <= -0.01)}}
    doc["segundos"] = round(time.time() - t0, 1)
    N.write_json_atomic(out, doc)
    print(json.dumps(doc["resumen"], ensure_ascii=False))


if __name__ == "__main__":
    raise SystemExit(main())
