"""Supremo de C2 en df con cota de SEGUNDO ORDEN en la región formal (CIERRE DF Y PASO 4 3.7, NO OFICIAL).

  <py_integracion> -m codigo.sup_formal_mvf <G|N> <df|d|f> <salida.json> <tope_s>

Cota «todos formales» (review/FUNDAMENTO_COTAS_POR_DISENO.md §3 con z_c = z_m):
   UB(τ, θ) = τ_d r* γ − [N] τ_d r* k_F q + τ_f q* κ0 x_f^(−φ) q,   q = (a−1)/(a−ρ)   (z_m = 1)
Es cota superior DEMOSTRADA de Rn en todo punto con r <= 1 (r_G = k_F/((1−td)γ), r_N = k_F/γ); en G lo es en todo el
dominio (h_G >= 0). UB es SUAVE: sobre una caja B con r.hi <= 1 (encierro de r por tax_side) se acota por VALOR MEDIO
con su gradiente encerrado (AD de motor_theta: QParams + tax_ad), UB(B) <= UB(c) + Σ ∂_i UB(B) (B_i − c_i), y si ∂_i UB
tiene signo demostrado el supremo de UB en B está en la cara (se colapsa el eje: lo que se descarta tiene UB menor o
igual y Rn <= UB). Cajas con r.hi > 1: cota_analitica (natural, con umbral formal por diseño). Siempre
U(B) = min(cota_analitica(B), valor medio) y nunca más que el padre. L = encierros PUNTUALES del motor normalizado en
puntos admisibles (β̃ = 0,25, z_cost = 1, u_θ = 0,5: los ejes que la cota no usa; la cota vale para todos sus valores).
Toda contradicción (punto con encierro.lo > U de su caja) detiene la corrida como INVALIDO_COTA_INCOMPATIBLE.
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
from paper2b.encierros_modelo import add, div, mul, sub  # noqa: E402
from paper2b.intervalos import Iv  # noqa: E402

T2 = 1e-4
EJES = ("tau_d", "tau_f", "a", "rho", "kappa_tilde", "eta_d", "eta_f", "phi")
FIJOS_PUNTO = {"beta_tilde": 0.25, "z_cost": 1.0, "u_theta": 0.5}
PUNTOS_PREVIOS = {
    "G": {"a": 1.4498577400741268, "beta_tilde": 0.25, "eta_d": 0.1, "eta_f": 0.1, "kappa_tilde": 0.2, "phi": 0.9603619182451836,
          "rho": 1.0, "tau_d": 0.5552387624365946, "tau_f": 0.6, "u_theta": 0.438377788598704, "z_cost": 1.0},
    "N": {"a": 1.6195312500000003, "beta_tilde": 0.25, "eta_d": 0.1, "eta_f": 0.1, "kappa_tilde": 0.2, "phi": 0.6672873221579658,
          "rho": 1.0, "tau_d": 0.6, "tau_f": 0.6, "u_theta": 0.5086962260687184, "z_cost": 1.0}}


class Incompatible(RuntimeError):
    pass


def ub_formal(box, fixed, dis):
    """(valor AD de UB sobre la caja, r encerrado). Requiere z_m = 1."""
    th = {p: box[p] for p in MT.STRUCT}
    Q = MT.QParams(th, fixed)
    td, tf = MT.var(Iv(*box["tau_d"]), 0), MT.var(Iv(*box["tau_f"]), 1)
    x = MT.tax_ad(Q, td, tf)
    q = div(sub(Q.a, 1.0), sub(Q.a, Q.rho))
    ub = mul(mul(td, x.rstar), Q.gamma)
    if dis == "N":
        ub = sub(ub, mul(mul(mul(td, x.rstar), x.kF), q))
    ub = add(ub, mul(mul(mul(mul(tf, x.qstar), Q.kappa0), x.gf), q))
    r = x.kF.v / ((1.0 - x.td.v) * Q.gamma) if dis == "G" else x.kF.v / Q.gamma
    return ub, r


def cota_caja(box, fixed, dis, n, col=None):
    """(U, gradiente sobre la caja COMPLETA o None). `col`: ejes colapsados {eje: valor} por monotonía DEMOSTRADA sobre una
    caja que contiene a esta. U = min(cota_analitica(caja completa), valor medio de UB en la CARA) y la segunda solo si
    r.hi <= 1 en la caja COMPLETA (UB >= Rn allí) — por monotonía heredada, sup UB(caja) = sup UB(cara)."""
    col = col or {}
    U = MT.cota_analitica(box, fixed, dis)
    n["analiticas"] += 1
    ad_full, r = ub_formal(box, fixed, dis)
    if r.hi > 1.0 or ad_full.g is None:
        n["sin_aplicabilidad"] = n.get("sin_aplicabilidad", 0) + 1
        return U, None                       # solo la cota analítica de la caja COMPLETA (válida en toda ella)
    face = dict(box, **{k: (v, v) for k, v in col.items()})
    ad, _ = ub_formal(face, fixed, dis)
    c = {p: (lo + (hi - lo) / 2,) * 2 for p, (lo, hi) in face.items()}
    adc, _ = ub_formal(c, fixed, dis)
    mv = adc.v
    for i, p in enumerate(MT.VARS):
        mv = mv + ad.g[i] * (Iv(*face[p]) - c[p][0])
    n["valor_medio"] += 1
    return min(U, mv.hi, ad.v.hi), ad_full.g


def main():
    dis, j, out, tope = sys.argv[1], sys.argv[2], Path(sys.argv[3]), float(sys.argv[4])
    t0 = time.time()
    G = XD.grupo(dis, j)
    fixed = G["fixed"]
    N.need(float(fixed["z_m"]) == 1.0, "Z_M_DISTINTO_DE_1")
    mm = dict(XD.menu(j, G["bd"], G["bf"]), **G["full"])
    root = {p: mm[p] for p in MT.VARS}
    irr = set(XD.IRRELEVANTES[j])
    libres0 = [p for p in EJES if p not in irr and root[p][1] > root[p][0]]
    W = {p: root[p][1] - root[p][0] for p in libres0}
    gam = float(fixed["gamma"])
    n = {"cajas": 0, "podadas": 0, "puntos": 0, "analiticas": 0, "valor_medio": 0, "colapsos": 0, "estancamientos": 0}
    best = {"L": -math.inf, "pt": None}
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "objeto": "sup C2: valor medio de la cota formal + cota analítica",
           "diseno": dis, "instrumento": j, "plan_sha256": G["plan_sha256"], "dominio": {p: list(v) for p, v in root.items()},
           "T2": T2, "ejes_partidos": libres0, "valores_de_punto_para_ejes_no_usados_por_la_cota": FIJOS_PUNTO}
    t_esc = [0.0]

    def punto(pt, techo=math.inf):
        pt = dict(pt, **{k: v for k, v in FIJOS_PUNTO.items() if root[k][0] <= v <= root[k][1]})
        n["puntos"] += 1
        v = XD.punto(pt, fixed, dis)
        if v.lo > techo:
            raise Incompatible("PUNTO_SOBRE_CAJA: %r > %r en %s" % (v.lo, techo, json.dumps(pt)))
        if v.lo > best["L"]:
            best["L"], best["pt"] = v.lo, dict(pt)

    def escribir(force=False, **kw):
        doc.update(kw)
        if force or time.time() - t_esc[0] > 15:
            doc.update(L=best["L"] / gam, punto_cota_inferior=best["pt"], segundos=round(time.time() - t0, 1), **n)
            N.write_json_atomic(out, doc)
            t_esc[0] = time.time()

    def colapsar(box, col, g):
        """Ejes con signo DEMOSTRADO de ∂UB sobre la caja completa -> se fija su valor (cara favorable)."""
        c2 = dict(col)
        for i, p in enumerate(MT.VARS):
            if p in libres0 and p not in c2 and box[p][1] > box[p][0] and g is not None:
                if g[i].lo > 0.0:
                    c2[p] = box[p][1]
                elif g[i].hi < 0.0:
                    c2[p] = box[p][0]
        return c2
    estado, traza = "tope", []
    try:
        if dis in PUNTOS_PREVIOS and j == "df":
            punto(PUNTOS_PREVIOS[dis])
        u0, g0 = cota_caja(root, fixed, dis, n)
        heap = [(-u0, 0, root, g0, {})]
        cont = 1
        while heap:
            Ucur = max(-heap[0][0], best["L"])
            brecha = (Ucur - best["L"]) / gam
            if n["cajas"] % 100 == 0:
                traza.append([round(time.time() - t0, 1), n["cajas"], best["L"] / gam, Ucur / gam])
            escribir(U=Ucur / gam, brecha=brecha, vivas=len(heap))
            if brecha <= T2:
                estado = "convergido"
                break
            if time.time() - t0 > tope:
                break
            nu, _, box, g, col = heapq.heappop(heap)
            if -nu <= best["L"]:
                n["podadas"] += 1
                continue
            n["cajas"] += 1
            # colapso por monotonía de la cota formal sobre la caja COMPLETA (g no es None solo si r.hi <= 1 en ella)
            if g is not None:
                c2 = colapsar(box, col, g)
                if c2 != col:
                    n["colapsos"] += 1
                    u2, g2 = cota_caja(box, fixed, dis, n, c2)
                    u2 = min(u2, -nu)
                    punto({p: (c2[p] if p in c2 else lo + (hi - lo) / 2) for p, (lo, hi) in box.items()}, u2)
                    if u2 > best["L"]:
                        heapq.heappush(heap, (-u2, cont, box, g2, c2))
                        cont += 1
                    else:
                        n["podadas"] += 1
                    continue
            if n["cajas"] % 50 == 0:
                punto({p: (col[p] if p in col else lo + (hi - lo) / 2) for p, (lo, hi) in box.items()}, -nu)
            libres = [p for p in libres0 if box[p][1] > box[p][0] and p not in col]
            if not libres:
                punto({p: (col[p] if p in col else lo) for p, (lo, hi) in box.items()}, -nu)
                if -nu - best["L"] <= T2 * gam:
                    continue
                heapq.heappush(heap, (nu, cont, box, g, col))
                estado = "caja_degenerada_viva"
                break
            if g is not None:
                q = max(libres, key=lambda p: max(abs(g[MT.VARS.index(p)].lo), abs(g[MT.VARS.index(p)].hi)) * (box[p][1] - box[p][0]))
            else:
                q = max(libres, key=lambda p: (box[p][1] - box[p][0]) / W[p])
            lo, hi = box[q]
            m = lo + (hi - lo) / 2
            for h in (dict(box, **{q: (lo, m)}), dict(box, **{q: (m, hi)})):
                u, gh = cota_caja(h, fixed, dis, n, col)          # hija ⊆ caja: hereda la monotonía demostrada
                u = min(u, -nu)
                if u > best["L"]:
                    heapq.heappush(heap, (-u, cont, h, gh, col))
                    cont += 1
                else:
                    n["podadas"] += 1
            heap = [x for x in heap if -x[0] > best["L"]]
            heapq.heapify(heap)
        if not heap and estado != "convergido":
            estado = "convergido"
        Ufin = max(-heap[0][0], best["L"]) if heap else best["L"]
    except Incompatible as exc:
        estado, Ufin = "INVALIDO_COTA_INCOMPATIBLE", None
        doc["diagnostico"] = str(exc)[:1000]
    escribir(force=True, U=None if Ufin is None else Ufin / gam, brecha=None if Ufin is None else (Ufin - best["L"]) / gam,
             estado=estado, vivas=len(heap) if estado != "INVALIDO_COTA_INCOMPATIBLE" else None,
             mejor_caja_viva={p: list(v) for p, v in heap[0][2].items() if p in libres0} if (estado != "INVALIDO_COTA_INCOMPATIBLE" and heap) else None,
             traza=traza[:: max(1, len(traza) // 60)] + traza[-1:], lema_E0=dict(MT.ESTADISTICA))
    print(json.dumps({k: doc.get(k) for k in ("diseno", "instrumento", "L", "U", "brecha", "estado", "cajas", "colapsos", "valor_medio", "puntos", "segundos")}))


if __name__ == "__main__":
    raise SystemExit(main())
