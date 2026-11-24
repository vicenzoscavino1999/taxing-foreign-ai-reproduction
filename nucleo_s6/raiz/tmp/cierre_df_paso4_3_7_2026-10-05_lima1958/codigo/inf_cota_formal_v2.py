"""Ínfimo de C2 con COTA INFERIOR por puntos fiscales «todos formales» (CIERRE DF Y PASO 4 3.7, NO OFICIAL).
VERSIÓN CANDIDATA v2 (separada de codigo/inf_cota_formal.py, que se estaba ejecutando): única diferencia, el término c
de la condición (I) de N se encierra en su forma factorizada idéntica κ0 [t̃_d − φ t̃_f (1 − t̃_d)] (ver cota_inf_tau).
En v1 el encierro κ0 − (1 − t̃_d) k_F perdía la correlación entre κ0 y k_F (c.lo ≈ −0,195 γ en d, donde c = κ0 t̃_d >= 0)
y (I) no se demostraba salvo en cajas diminutas en κ̃ (INFF-Nd: L = −inf).

  <py_integracion> -m codigo.inf_cota_formal_v2 <G|N> <d|df> <salida.json> <tope_s>

Lema (review/FUNDAMENTO_COTAS_POR_DISENO.md §7). Para τ = (τ_d, τ_f) del menú y una caja Θ, si en z = z_m (= 1) y para
TODO θ de Θ:
  (P) F0-I0 >= 0:          δ − tb >= 0                                   (estado previo F)
  (F) F1-F0 > 0:           G: (1 − t̃_d) γ − k_F > 0;   N: γ − k_F > 0
  (I) F1-I1 >= 0:          G: δ − tb − t̃_d γ − φ κ0 t̃_f >= 0;   N: δ − tb − t̃_d γ + c >= 0, c = κ0 − (1 − t̃_d) k_F
y estas diferencias divididas por z son monótonas en z >= z_m (crecientes: δ z^(θ−1) con θ > 1; los términos en z^(ρ−1)
con coeficiente >= 0 decrecen y se acotan en z_m de forma conservadora: en (F) se usa z^(ρ−1) <= 1; en (I) de N, si
c < 0 se exige la condición con c z^(ρ−1) >= c), entonces TODO z >= z_m es F antes y después: E0 = 0, A = γ (G) o
γ − k_F q (N), W = q, y
   Rn(τ; θ) = τ_d r* A + τ_f q* κ0 x_f^(−φ) q   EXACTAMENTE.
Por tanto C2(θ) >= Rn(τ; θ)/γ y inf_Θ C2 >= inf_Θ [Rn(τ; θ)/γ], encerrado por intervalos con redondeo hacia afuera.
Se prueban varios τ por caja (rejilla en τ_d y τ_f, y el τ_d máximo que cumple las condiciones por bisección) y se toma
el mayor encierro inferior. Rama y cota en θ para el ÍNFIMO: mejor primero por la menor cota inferior; poda si
cota >= U − T2. U = techo CERTIFICADO en puntos admisibles (extremos_dfd.c2_punto_cert = sup_bound del motor normalizado)
en el centro de la caja de menor cota (y en la esquina inicial). Convergido si U − L <= T2.
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
from paper2b import encierros_modelo as EM  # noqa: E402
from paper2b import motor_theta as MT  # noqa: E402
from paper2b.intervalos import Iv  # noqa: E402

T2 = 1e-4


def cota_inf_tau(th, fixed, dis, td_, tf_):
    """Cota inferior de Rn(τ; θ)/γ sobre la caja θ en el punto fiscal τ = (td_, tf_), o None si las condiciones (P),(F),(I)
    no se demuestran en toda la caja."""
    P = EM.IParams.from_primitive_box(th, fixed)
    Td, Tf = Iv(td_, td_), Iv(tf_, tf_)
    x = EM.tax_side(P, EM.AD(Td), EM.AD(Tf), EM.AD(P.phi))
    g, d, k0, kF, tdv, tfv = P.gamma, P.delta, P.kappa0, x.kF.v, x.td.v, x.tf.v
    tb = Td * P.beta
    if not (d - tb).lo >= 0.0:                                     # (P) en z_m (δ z^(θ−1) − tb creciente)
        return None
    if dis == "G":
        if not ((1.0 - tdv) * g - kF).lo > 0.0:                    # (F): (1−t̃_d)γ − k_F z^(ρ−1) >= ... en z_m
            return None
        if not (d - tb - tdv * g - P.phi * k0 * tfv).lo >= 0.0:    # (I) en z_m; −φκ0 t̃_f z^(ρ−1) crece hacia 0
            return None
    else:
        if not (g - kF).lo > 0.0:
            return None
        # c = κ0 − (1 − t̃_d) k_F con k_F = κ0 (1 + φ t̃_f) (encierros_modelo.tax_side) es IDÉNTICAMENTE
        # κ0 [t̃_d − φ t̃_f (1 − t̃_d)]: la forma factorizada evita la dependencia de intervalos (κ0 aparece una vez);
        # en d (τ_f = 0, t̃_f = 0) vale κ0 t̃_d >= 0
        c = k0 * (tdv - P.phi * tfv * (1.0 - tdv))
        cl = c.lo if c.lo < 0.0 else 0.0                          # c z^(ρ−1) >= min(c, 0) para z >= z_m
        if not (d - tb - tdv * g).lo + cl >= 0.0:
            return None
    q = (P.a - 1.0) / (P.a - P.rho)                               # Mρn(z_m, ∞) con z_m = 1
    A = g if dis == "G" else g - kF * q
    R = Td * x.rstar.v * A + Tf * x.qstar.v * k0 * x.gf.v * q
    return (R / g).lo


def mejor_tau(th, fixed, dis, j, bd, bf):
    """Mayor cota inferior sobre una rejilla de τ y el τ_d máximo factible por bisección (con τ_f = 0)."""
    best = (-math.inf, None)
    tds = [0.0] if j == "f" else [bd * k / 16 for k in range(17)] + [bd * 2.0 ** -k for k in range(5, 20)]
    tfs = [0.0] if j == "d" else [bf * k / 8 for k in range(9)] + [bf * 2.0 ** -k for k in range(4, 14, 2)]
    for a in sorted(set(tds)):
        for b in sorted(set(tfs)):
            if a == 0.0 and b == 0.0:
                continue
            v = cota_inf_tau(th, fixed, dis, a, b)
            if v is not None and v > best[0]:
                best = (v, (a, b))
    if j in ("d", "df"):                                            # τ_d máximo factible (τ_f = 0) por bisección
        lo, hi = 0.0, bd
        for _ in range(50):
            m = 0.5 * (lo + hi)
            if cota_inf_tau(th, fixed, dis, m, 0.0) is not None:
                lo = m
            else:
                hi = m
        if lo > 0.0:
            v = cota_inf_tau(th, fixed, dis, lo, 0.0)
            if v is not None and v > best[0]:
                best = (v, (lo, 0.0))
    return best


def main():
    dis, j, out, tope = sys.argv[1], sys.argv[2], Path(sys.argv[3]), float(sys.argv[4])
    t0 = time.time()
    G = XD.grupo(dis, j)
    fixed, bd, bf = G["fixed"], G["bd"], G["bf"]
    N.need(float(fixed["z_m"]) == 1.0, "Z_M_DISTINTO_DE_1")
    full = G["full"]
    irr = set(XD.IRRELEVANTES[j])
    libres0 = [p for p in MT.STRUCT if p not in irr and full[p][1] > full[p][0]]
    W = {p: full[p][1] - full[p][0] for p in libres0}
    n = {"cajas": 0, "techos": 0, "podadas": 0, "sin_tau": 0}
    best = {"U": math.inf, "pt": None, "techo": None}
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "objeto": "inf C2: cota inferior por puntos fiscales «todos formales»",
           "diseno": dis, "instrumento": j, "plan_sha256": G["plan_sha256"], "dominio": {p: list(v) for p, v in full.items()}, "T2": T2}

    def techo(pt):
        n["techos"] += 1
        lo, hi = XD.c2_punto_cert(pt, fixed, dis, j, bd, bf)
        if hi < best["U"]:
            best.update(U=hi, pt=dict(pt), techo=[lo, hi])
    # esquina de C2 mínima sugerida por la monotonía de la cota (z_cost, u_θ, a, β̃, η_d al máximo; N: κ̃, ρ al máximo;
    # df: además η_f al máximo, φ = 0 y κ̃ al mínimo en G) y el punto de la ronda anterior
    esq = {p: v[1] for p, v in full.items()}
    esq.update(phi=full["phi"][0])
    if dis == "G":
        esq["kappa_tilde"] = full["kappa_tilde"][0]
    techo(esq)
    prev = {"G": {"d": {"a": 2.499658203125, "beta_tilde": 4.0, "eta_d": 4.0, "eta_f": 4.05, "kappa_tilde": 0.2, "phi": 0.5, "rho": 1.0, "u_theta": 0.9, "z_cost": 100.0}},
            "N": {"d": {"a": 2.5, "beta_tilde": 3.765625, "eta_d": 4.0, "eta_f": 4.05, "kappa_tilde": 0.2, "phi": 0.5, "rho": 1.0, "u_theta": 0.9, "z_cost": 100.0}}}
    if j in prev.get(dis, {}):
        techo(prev[dis][j])
    v0, t0_ = mejor_tau(full, fixed, dis, j, bd, bf)
    n["cajas"] += 1
    heap = [(v0 if v0 > -math.inf else -math.inf, 0, full, t0_)]
    cont, estado, traza = 1, "tope", []
    t_esc = [0.0]
    while heap:
        L = min(heap[0][0], best["U"])
        brecha = best["U"] - L
        if n["cajas"] % 20 == 0:
            traza.append([round(time.time() - t0, 1), n["cajas"], L, best["U"]])
        if time.time() - t_esc[0] > 15:
            doc.update(L=L, U=best["U"], brecha=brecha, vivas=len(heap), punto_cota_superior=best["pt"], techo_punto=best["techo"],
                       segundos=round(time.time() - t0, 1), **n)
            N.write_json_atomic(out, doc)
            t_esc[0] = time.time()
        if brecha <= T2:
            estado = "convergido"
            break
        if time.time() - t0 > tope:
            break
        lb, _, th, tau = heapq.heappop(heap)
        if lb >= best["U"] - T2:
            n["podadas"] += 1
            heapq.heappush(heap, (lb, cont, th, tau))       # se conserva: es la menor cota viva (ya basta para T2)
            cont += 1
            estado = "convergido"
            break
        libres = [p for p in libres0 if th[p][1] > th[p][0]]
        if not libres:
            heapq.heappush(heap, (lb, cont, th, tau))
            estado = "caja_degenerada_viva"
            break
        if n["cajas"] % 25 == 0:
            techo({p: lo + (hi - lo) / 2 for p, (lo, hi) in th.items()})
        p = max(libres, key=lambda q: (th[q][1] - th[q][0]) / W[q])
        lo, hi = th[p]
        m = lo + (hi - lo) / 2
        for h in (dict(th, **{p: (lo, m)}), dict(th, **{p: (m, hi)})):
            v, t = mejor_tau(h, fixed, dis, j, bd, bf)
            n["cajas"] += 1
            if t is None:
                n["sin_tau"] += 1
                v = -math.inf
            v = max(v, lb)                                       # la cota del padre vale en la hija
            heapq.heappush(heap, (v, cont, h, t))
            cont += 1
    L = min(heap[0][0], best["U"]) if heap else best["U"]
    doc.update(L=L, U=best["U"], brecha=best["U"] - L, estado=estado, vivas=len(heap), punto_cota_superior=best["pt"],
               techo_punto=best["techo"], caja_de_menor_cota={q: list(v) for q, v in heap[0][2].items()} if heap else None,
               tau_de_la_cota=heap[0][3] if heap else None, traza=traza[:: max(1, len(traza) // 60)] + traza[-1:],
               segundos=round(time.time() - t0, 1), **n)
    N.write_json_atomic(out, doc)
    print(json.dumps({k: doc.get(k) for k in ("diseno", "instrumento", "L", "U", "brecha", "estado", "cajas", "techos", "segundos")}))


if __name__ == "__main__":
    raise SystemExit(main())
