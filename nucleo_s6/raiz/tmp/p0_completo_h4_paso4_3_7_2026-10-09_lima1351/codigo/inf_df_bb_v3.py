"""Ínfimo de C2 en df (G o N): rama y cota en θ para la COTA INFERIOR global, con el valor «todos formales» encerrado
de forma EXACTA en s = κ̃ q (CIERRE INF DF Y PASO 4 3.7, NO OFICIAL). Módulo nuevo; inf_df_bb_v2 se conserva.

  <py_integracion> -m codigo.inf_df_bb_v3 <G|N> <certificado_U.json> <salida.json> <tope_s>

Cambio respecto de v2 (motivado por la medición de INFBB2-N, review/FUNDAMENTO_INFIMOS_DF.md §3): en la región
«todos formales» (lema de inf_cota_formal_v2: (P), (F), (I) en z_m = 1 para toda la caja) y con z_m = 1, κ0 = κ̃ γ,
k_F = κ0 (1 + φ t̃_f), q = (a − 1)/(a − ρ), s = κ̃ q:
  G: Rn/γ = τ_d r* + s · τ_f q* g_f
  N: Rn/γ = τ_d r* + s · [τ_f q* g_f − τ_d r* (1 + φ t̃_f)]
Ambas son AFINES en s, y s solo depende de (κ̃, a, ρ), con q creciente en a y en ρ (dq/da = (1 − ρ)/(a − ρ)² >= 0,
dq/dρ = (a − 1)/(a − ρ)² > 0): el rango exacto de s en la caja es [κ̃.lo q(a.lo, ρ.lo), κ̃.hi q(a.hi, ρ.hi)] y el mínimo
de una función afín en s está en un extremo. v2 encerraba κ0, k_F y q por separado (dependencia: en N el término
−τ_d r* k_F q usaba κ̃.hi y q.hi a la vez que el término de τ_f usaba κ̃.lo y q.lo).
Condiciones (P), (F), (I): las de inf_cota_formal_v2.cota_inf_tau sin cambios.
Techo U: el CERTIFICADO por codigo/certificar_inf_df.py (techo v3 en un punto admisible), leído de <certificado_U.json>.
Poda: caja con cota >= U − T2. Parada: U − L <= T2 o tope. INCOMPATIBLE (se detiene y se informa) si L > U.
Parte el eje de mayor anchura relativa (como v2).
"""
from __future__ import annotations

import heapq
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
from codigo.demo import nucleo_v as N  # noqa: E402
from paper2b import cobertura as COV  # noqa: E402
from paper2b import encierros_modelo as EM  # noqa: E402
from paper2b.intervalos import Iv  # noqa: E402

T2 = 1e-4


def s_rango(th) -> Iv:
    """Rango exacto (redondeo hacia afuera) de s = κ̃ (a − 1)/(a − ρ) en la caja (z_m = 1)."""
    a0, a1 = Iv.point(th["a"][0]), Iv.point(th["a"][1])
    r0, r1 = Iv.point(th["rho"][0]), Iv.point(th["rho"][1])
    qlo = ((a0 - 1.0) / (a0 - r0)).lo
    qhi = ((a1 - 1.0) / (a1 - r1)).hi
    return Iv((Iv.point(th["kappa_tilde"][0]) * Iv(qlo, qlo)).lo, (Iv.point(th["kappa_tilde"][1]) * Iv(qhi, qhi)).hi)


def cota_inf_tau_v3(th, fixed, dis, td_, tf_):
    """Cota inferior de Rn(τ; θ)/γ en la caja θ para τ = (td_, tf_), o None si (P), (F), (I) no se demuestran."""
    P = EM.IParams.from_primitive_box(th, fixed)
    Td, Tf = Iv(td_, td_), Iv(tf_, tf_)
    x = EM.tax_side(P, EM.AD(Td), EM.AD(Tf), EM.AD(P.phi))
    g, d, k0, kF, tdv, tfv = P.gamma, P.delta, P.kappa0, x.kF.v, x.td.v, x.tf.v
    tb = Td * P.beta
    # --- condiciones: idénticas a inf_cota_formal_v2.cota_inf_tau
    if not (d - tb).lo >= 0.0:
        return None
    if dis == "G":
        if not ((1.0 - tdv) * g - kF).lo > 0.0:
            return None
        if not (d - tb - tdv * g - P.phi * k0 * tfv).lo >= 0.0:
            return None
    else:
        if not (g - kF).lo > 0.0:
            return None
        c = k0 * (tdv - P.phi * tfv * (1.0 - tdv))
        cl = c.lo if c.lo < 0.0 else 0.0
        if not (d - tb - tdv * g).lo + cl >= 0.0:
            return None
    # --- valor afín en s, mínimo en un extremo del rango exacto de s
    S = s_rango(th)
    base = Td * x.rstar.v
    if dis == "G":
        D = Tf * x.qstar.v * x.gf.v
    else:
        D = Tf * x.qstar.v * x.gf.v - Td * x.rstar.v * (1.0 + P.phi * tfv)
    cand = [(base + Iv(s, s) * D).lo for s in (S.lo, S.hi)]
    return min(cand)


def lb_caja(th, fixed, dis, bd, bf, fr_d=(1.0, 0.75, 0.5, 0.25, 0.0), nbis=32):
    ok = lambda a, b: cota_inf_tau_v3(th, fixed, dis, a, b) is not None  # noqa: E731
    best = (0.0, None)
    lo, hi = 0.0, bd
    for _ in range(nbis + 8):
        m = 0.5 * (lo + hi)
        if m > 0 and ok(m, 0.0):
            lo = m
        else:
            hi = m
    td_max = lo
    for fr in fr_d:
        td = fr * td_max
        a, b = 0.0, bf
        for _ in range(nbis):
            m = 0.5 * (a + b)
            if ok(td, m):
                a = m
            else:
                b = m
        for k in (1.0, 0.5):
            tf = k * a
            if td == 0.0 and tf == 0.0:
                continue
            v = cota_inf_tau_v3(th, fixed, dis, td, tf)
            if v is not None and v > best[0]:
                best = (v, (td, tf))
    return best


def main():
    dis, cert_p, out, tope = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), float(sys.argv[4])
    t0 = time.time()
    G = XD.grupo(dis, "df")
    fixed, bd, bf, full = G["fixed"], G["bd"], G["bf"], G["full"]
    N.need(float(fixed["z_m"]) == 1.0, "Z_M_DISTINTO_DE_1")
    cert = json.loads(cert_p.read_text(encoding="utf-8"))
    N.need(cert["diseno"] == dis and cert["mejor"] is not None and not cert["mejor"]["incompatible"], "CERTIFICADO_U_INVALIDO")
    U = float(cert["U"])
    W = {p: (full[p][1] - full[p][0]) or 1.0 for p in COV.STRUCT}
    libres = [p for p in COV.STRUCT if full[p][1] > full[p][0]]
    n = {"cajas": 0}
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "objeto": "inf C2 df: cota inferior global v3 (afín en s exacto)",
           "diseno": dis, "instrumento": "df", "plan_sha256": G["plan_sha256"], "dominio": {p: list(v) for p, v in full.items()},
           "T2": T2, "U": U, "certificado_U": {"archivo": str(cert_p.as_posix()), "sha256": N.sha(cert_p.read_bytes()),
                                              "punto": cert["mejor"]["theta"]}}
    v0 = lb_caja(full, fixed, dis, bd, bf)
    heap = [(v0[0], 0, full, v0[1])]
    cont, estado, traza, t_esc = 1, "tope", [], [0.0]
    while heap:
        L = heap[0][0]
        if L > U:
            estado = "INCOMPATIBLE_L_MAYOR_QUE_U"
            break
        if n["cajas"] % 50 == 0:
            traza.append([round(time.time() - t0, 1), n["cajas"], L])
        if time.time() - t_esc[0] > 15:
            doc.update(L=L, brecha=U - L, vivas=len(heap), segundos=round(time.time() - t0, 1), **n)
            N.write_json_atomic(out, doc)
            t_esc[0] = time.time()
        if U - L <= T2:
            estado = "convergido"
            break
        if time.time() - t0 > tope:
            break
        lb, _, th, tau = heapq.heappop(heap)
        n["cajas"] += 1
        ls = [p for p in libres if th[p][1] > th[p][0]]
        if not ls:
            heapq.heappush(heap, (lb, cont, th, tau))
            estado = "caja_degenerada_viva"
            break
        p = max(ls, key=lambda q: (th[q][1] - th[q][0]) / W[q])
        lo, hi = th[p]
        m = lo + (hi - lo) / 2
        for h in (dict(th, **{p: (lo, m)}), dict(th, **{p: (m, hi)})):
            v, t = lb_caja(h, fixed, dis, bd, bf)
            heapq.heappush(heap, (max(v, lb), cont, h, t))
            cont += 1
    L = heap[0][0] if heap else U
    doc.update(L=L, brecha=U - L, estado=estado, vivas=len(heap),
               caja_de_menor_cota={q: list(v) for q, v in heap[0][2].items()} if heap else None, tau_de_la_cota=heap[0][3] if heap else None,
               traza=traza[:: max(1, len(traza) // 60)] + traza[-1:], segundos=round(time.time() - t0, 1), **n)
    N.write_json_atomic(out, doc)
    print(json.dumps({k: doc.get(k) for k in ("diseno", "L", "U", "brecha", "estado", "cajas", "segundos")}))


if __name__ == "__main__":
    raise SystemExit(main())
