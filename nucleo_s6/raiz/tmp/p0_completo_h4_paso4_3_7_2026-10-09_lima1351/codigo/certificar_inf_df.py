"""Ínfimos de C2 en df: VALIDACIÓN del techo v3 y CERTIFICACIÓN de U en puntos candidatos (CIERRE INF DF Y PASO 4 3.7,
NO OFICIAL).

  <py_integracion> -m codigo.certificar_inf_df validar <G|N> <salida.json> <tope_s>
  <py_integracion> -m codigo.certificar_inf_df certificar <G|N> <candidatos.json> <salida.json> <tope_s>

validar (casos PREDEFINIDOS, semilla fija): para θ en las esquinas y al azar (ρ < 1 y ρ = 1, φ, κ̃, η_f, a en sus
extremos e interiores) y τ en una rejilla (geométrica en τ_d, lineal en τ_f, incluidas las barras y regiones con
informales, z* > 1), comprueba U(τ) >= cota inferior certificada del motor normalizado (encierro .lo) en el MISMO
(θ, τ), y U(caja de τ) >= U(τ) de sus puntos. Cualquier violación invalida el techo.
certificar: para cada candidato (θ admisible: dentro del soporte y cobertura.box_admissible), techo v3 = U certificado
de C2(θ); cota inferior certificada de C2(θ) por el motor en el mejor τ; INCOMPATIBLE si U < L_punto (se informa, no
se ajusta). Convergencia contra la cota inferior global AUTENTICADA de la entrega anterior: U − L <= T2.
"""
from __future__ import annotations

import json
import math
import random
import sys
import time
from pathlib import Path

AREA = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AREA / "integracion/src"))
import paper2b  # noqa: E402

assert Path(paper2b.__file__).resolve().parent == (AREA / "integracion/src/paper2b").resolve(), "PAPER2B_NO_AISLADO"
from codigo import extremos_dfd as XD  # noqa: E402
from codigo import inf_df_techo_v3 as TV3  # noqa: E402
from codigo.demo import c2_normalizado as C2N  # noqa: E402
from codigo.demo import nucleo_v as N  # noqa: E402
from paper2b import cobertura as COV  # noqa: E402
from paper2b import encierros_modelo as EM  # noqa: E402
from paper2b.intervalos import Iv  # noqa: E402

T2 = 1e-4
PREVIA = "../cierre_df_paso4_3_7_2026-10-05_lima1958"
L_AUT = {"G": (0.00039847549352027784, "demo/hito2/infbb2_G_df.json"), "N": (0.0003862580013867519, "demo/hito2/infbb2_N_df.json")}


def l_autenticada(dis):
    """Cota inferior global de la entrega anterior, leída del archivo (cuyo sha está en su inventario autenticado)."""
    L, rel = L_AUT[dis]
    d = json.loads((AREA / PREVIA / rel).read_text(encoding="utf-8"))
    N.need(d["L"] == L, "L_AUTENTICADA_DISTINTA")
    return L


def admisible(th, full, fixed):
    dentro = all(full[p][0] <= th[p] <= full[p][1] for p in full)
    return dentro and bool(COV.box_admissible({p: (v, v) for p, v in th.items()}, fixed))


def l_punto(th, fixed, dis, taus):
    """Cota inferior CERTIFICADA de C2(θ): max sobre τ de (R.lo del motor normalizado)/γ, por abajo."""
    P = EM.IParams.from_primitive_box({p: (v, v) for p, v in th.items()}, fixed)
    eng = C2N.MotorNormalizado(P, dis)
    best = (-math.inf, None)
    for (x, y) in taus:
        v, _ = eng.R(Iv(x, x), Iv(y, y))
        lo = (v / P.gamma).lo
        if lo > best[0]:
            best = (lo, (x, y))
    return best


def validar(dis, out, tope):
    t0 = time.time()
    G = XD.grupo(dis, "df")
    fixed, bd, bf, full = G["fixed"], G["bd"], G["bf"], G["full"]
    rng = random.Random(20261006)
    thetas = []
    esq_min = {p: v[1] for p, v in full.items()}
    esq_min["kappa_tilde"] = full["kappa_tilde"][0]
    for rho in (full["rho"][0], 0.55, 0.7, 0.85, 1.0):
        for phi in (0.0, 0.5, 1.0):
            for kt in (full["kappa_tilde"][0], 0.05, full["kappa_tilde"][1]):
                for ef in (full["eta_f"][0], 4.0, full["eta_f"][1]):
                    thetas.append(dict(esq_min, rho=rho, phi=phi, kappa_tilde=kt, eta_f=ef))
    for _ in range(60):
        thetas.append({p: (lo + (hi - lo) * rng.random()) for p, (lo, hi) in full.items()})
    for _ in range(20):                                   # esquinas al azar
        thetas.append({p: (lo if rng.random() < 0.5 else hi) for p, (lo, hi) in full.items()})
    tds = sorted([0.0] + [bd * 10.0 ** (-k / 2.0) for k in range(0, 13)])
    tfs = [0.0, bf * 0.01, bf * 0.05, bf * 0.15, bf * 0.3, bf * 0.6, bf]
    n = {"theta": 0, "pares": 0, "violaciones": 0, "cajas": 0, "violaciones_caja": 0, "con_informales": 0, "no_admisibles": 0}
    peor, viol = math.inf, []
    for th in thetas:
        if time.time() - t0 > tope:
            break
        if not admisible(th, full, fixed):
            n["no_admisibles"] += 1
            continue
        n["theta"] += 1
        P = EM.IParams.from_primitive_box({p: (v, v) for p, v in th.items()}, fixed)
        eng = C2N.MotorNormalizado(P, dis)
        T = TV3.Techo(P, dis)
        Upts = {}
        for x in tds:
            for y in tfs:
                u, z = T.U(Iv(x, x), Iv(y, y))
                v, _ = eng.R(Iv(x, x), Iv(y, y))
                n["pares"] += 1
                n["con_informales"] += z > 1.0
                Upts[(x, y)] = u
                h = u - v.lo
                peor = min(peor, h)
                if h < 0.0:
                    n["violaciones"] += 1
                    viol.append({"theta": th, "tau": [x, y], "U": u, "R_lo": v.lo})
        for i in range(len(tds) - 1):
            for k in range(len(tfs) - 1):
                ub, _ = T.U(Iv(tds[i], tds[i + 1]), Iv(tfs[k], tfs[k + 1]))
                n["cajas"] += 1
                m = max(Upts[(tds[a], tfs[b])] for a in (i, i + 1) for b in (k, k + 1))
                if ub < m:
                    n["violaciones_caja"] += 1
                    viol.append({"theta": th, "caja": [tds[i], tds[i + 1], tfs[k], tfs[k + 1]], "U_caja": ub, "max_U_vertices": m})
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "objeto": "validación predefinida del techo v3", "diseno": dis,
           "plan_sha256": G["plan_sha256"], "conteos": n, "holgura_minima_U_menos_Rlo": peor, "violaciones": viol[:50],
           "cumple": n["violaciones"] == 0 and n["violaciones_caja"] == 0 and n["con_informales"] > 0 and n["theta"] >= 100,
           "segundos": round(time.time() - t0, 1)}
    N.write_json_atomic(out, doc)
    print(json.dumps({k: doc[k] for k in ("diseno", "conteos", "holgura_minima_U_menos_Rlo", "cumple", "segundos")}))


def certificar(dis, cand_p, out, tope):
    t0 = time.time()
    G = XD.grupo(dis, "df")
    fixed, bd, bf, full = G["fixed"], G["bd"], G["bf"], G["full"]
    L = l_autenticada(dis)
    cands = json.loads(Path(cand_p).read_text(encoding="utf-8"))["candidatos"][dis]
    filas, mejor = [], None
    for c in cands:
        if time.time() - t0 > tope:
            break
        th = {p: float(c["theta"][p]) for p in full}
        fila = {"theta": th, "admisible": admisible(th, full, fixed)}
        if not fila["admisible"]:
            filas.append(fila)
            continue
        r = TV3.techo(th, fixed, dis, bd, bf, tope_s=min(300.0, max(30.0, tope - (time.time() - t0))))
        taus = [tuple(c["tau"])] if c.get("tau") else []
        taus.append(tuple(r["tau_sup_puntos"]))
        lp, tl = l_punto(th, fixed, dis, taus)
        fila.update(techo=r, U=r["U_C2"], L_punto=lp, tau_L_punto=list(tl), holgura_punto=r["U_C2"] - lp,
                    incompatible=r["U_C2"] < lp, U_menos_L_global=r["U_C2"] - L, converge=r["U_C2"] - L <= T2)
        filas.append(fila)
        if not fila["incompatible"] and (mejor is None or r["U_C2"] < mejor["U"]):
            mejor = fila
        N.write_json_atomic(out, {"etiqueta": N.ETIQUETA, "parcial": True, "filas": filas})
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "objeto": "techo certificado v3 en candidatos", "diseno": dis,
           "plan_sha256": G["plan_sha256"], "L_global_autenticada": L, "T2": T2, "filas": filas,
           "mejor": mejor, "U": mejor["U"] if mejor else None, "brecha": (mejor["U"] - L) if mejor else None,
           "convergido": bool(mejor and mejor["U"] - L <= T2), "incompatibles": sum(1 for f in filas if f.get("incompatible")),
           "segundos": round(time.time() - t0, 1)}
    N.write_json_atomic(out, doc)
    print(json.dumps({k: doc[k] for k in ("diseno", "L_global_autenticada", "U", "brecha", "convergido", "incompatibles", "segundos")}))


if __name__ == "__main__":
    modo = sys.argv[1]
    if modo == "validar":
        validar(sys.argv[2], Path(sys.argv[3]), float(sys.argv[4]))
    else:
        certificar(sys.argv[2], sys.argv[3], Path(sys.argv[4]), float(sys.argv[5]))
