"""Supremo de C2 en df con la RESTRICCIÓN FORMAL r <= 1 (lema de dominación; CIERRE DF Y PASO 4 3.7, NO OFICIAL).
Versión candidata SEPARADA de codigo/sup_formal_mvf.py (que no se modifica); reutiliza su cota formal UB y su encierro.

  <py_integracion> -m codigo.sup_restringido <G|N> <df|d|f> <salida.json> <tope_s>

Lema de dominación (review/FUNDAMENTO_COTAS_POR_DISENO.md §8). Con z_m = 1, κ0 = κ̃ γ y r = κ̃ c(τ, θ), donde
c = (1 + φ t̃_f)/(1 − t̃_d) en G y c = 1 + φ t̃_f en N no dependen de κ̃ (encierros_modelo.tax_side). Para (τ, θ) con
r > 1 sea θ' = θ con κ̃' = κ̃/r (r(θ') = 1; θ' ∈ Θ si 1/c >= κ̃_min, que se COMPRUEBA en la raíz; q_pot baja, así que
θ' es admisible). Entonces Rn(τ, θ) <= UB(τ, θ'):
  - ρ = 1: [F] vacío (F1-F0 = (c' − k_F) z <= 0), Rn = τ_d E0 <= 0 <= UB(τ, θ');
  - ρ < 1: Rn <= ∫_{z > z_c} h, z_c = r^{1/(1−ρ)} > 1 (§3), y término a término
      G: τ_d r* γ z_c^{1−a} <= τ_d r* γ;   τ_f q* κ0 g_f q z_c^{ρ−a} <= τ_f q* (κ0/r) g_f q   (z_c^{ρ−a} = r^{(ρ−a)/(1−ρ)} <= 1/r ⟺ a >= 1)
      N: además τ_d r* (γ z_c^{1−a} − k_F q z_c^{ρ−a}) = τ_d r* γ z_c^{1−a} (1 − q) <= τ_d r* γ (1 − q) = τ_d r* (γ − k_F' q),
         con k_F = r γ, k_F' = γ y 0 <= q <= 1.
Por tanto sup_{Π×Θ} Rn <= sup {UB(τ, θ): r(τ, θ) <= 1}, y en r <= 1 UB >= Rn (G y N; §3 con z_c <= z_m). Sobre una caja B:
  U(B) = min(encierro natural, valor medio) de UB en B' = B con κ̃ <= κ̃*_hi(B) = 1/c_lo(B). NO se usa la cota analítica
  de B: acota Rn en B, pero el lema necesita una cota de UB(τ, θ') en el punto DOMINANTE θ' (que puede estar en B);
  los encierros de UB sobre B' lo son por construcción (B' ⊇ B ∩ {r <= 1}). Corrección previa a la primera ejecución;
La precondición 1/c >= κ̃_min se comprueba por SUBDIVISIÓN (precondicion: t̃_d solo depende de (τ_d, η_d) y φ t̃_f de
(τ_f, η_f, φ)); el encierro natural de c sobre la raíz entera es demasiado ancho (c.lo < 0: SRES2 falló ahí sin calcular).
Si κ̃*_hi(B) < κ̃_lo(B), todo punto de B tiene r > 1 y B está DOMINADA (se descarta: su supremo lo alcanza la parte
r <= 1 de otras cajas). Las hijas heredan B' ⊆ B' del padre, así que la monotonía demostrada en B' se hereda (κ̃ no se
colapsa). L = encierros puntuales del motor normalizado en puntos admisibles (como sup_formal_mvf). Controles:
  - PUNTO_SOBRE_CAJA: un punto con r <= 1 DEMOSTRADO cuyo encierro supera la cota de su caja;
  - PUNTO_SOBRE_COTA_GLOBAL: L > U global en cualquier momento;
  cualquiera detiene la corrida como INVALIDO_COTA_INCOMPATIBLE.
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
from codigo import sup_formal_mvf as SF  # noqa: E402
from codigo.demo import nucleo_v as N  # noqa: E402
from paper2b import encierros_modelo as EM  # noqa: E402
from paper2b import motor_theta as MT  # noqa: E402
from paper2b.intervalos import Iv  # noqa: E402

T2 = SF.T2
EJES, FIJOS_PUNTO, PUNTOS_PREVIOS, Incompatible = SF.EJES, SF.FIJOS_PUNTO, SF.PUNTOS_PREVIOS, SF.Incompatible


def factor_c(box, fixed, dis) -> Iv:
    """c(τ, θ) = r/κ̃ encerrado sobre la caja (no depende de κ̃)."""
    th = {p: box[p] for p in MT.STRUCT}
    P = EM.IParams.from_primitive_box(th, fixed)
    x = EM.tax_side(P, EM.AD(Iv(*box["tau_d"])), EM.AD(Iv(*box["tau_f"])), EM.AD(P.phi))
    num = 1.0 + P.phi * x.tf.v
    return num / (1.0 - x.td.v) if dis == "G" else num


def precondicion(root, fixed, dis, k_td=64, k_tf=24, k_phi=8):
    """c_hi(Π×Θ) por SUBDIVISIÓN: t̃_d depende solo de (τ_d, η_d) y φ t̃_f solo de (τ_f, η_f, φ) (tax_side), así que
    c_G <= (1 + max φ t̃_f)/(1 − max t̃_d) y c_N <= 1 + max φ t̃_f. Devuelve (c_hi, max t̃_d, max φ t̃_f)."""
    def tramos(p, k):
        lo, hi = root[p]
        return [(lo + (hi - lo) * i / k, lo + (hi - lo) * (i + 1) / k) for i in range(k)] if hi > lo else [(lo, hi)]
    base = {p: root[p] for p in MT.STRUCT}
    td_max, ptf_max = -math.inf, -math.inf
    for t in tramos("tau_d", k_td):
        for e in tramos("eta_d", k_td):
            P = EM.IParams.from_primitive_box(dict(base, eta_d=e), fixed)
            x = EM.tax_side(P, EM.AD(Iv(*t)), EM.AD(Iv(0.0, 0.0)), EM.AD(P.phi))
            td_max = max(td_max, x.td.v.hi)
    for t in tramos("tau_f", k_tf):
        for e in tramos("eta_f", k_tf):
            for f in tramos("phi", k_phi):
                P = EM.IParams.from_primitive_box(dict(base, eta_f=e, phi=f), fixed)
                x = EM.tax_side(P, EM.AD(Iv(0.0, 0.0)), EM.AD(Iv(*t)), EM.AD(P.phi))
                ptf_max = max(ptf_max, (P.phi * x.tf.v).hi)
    if dis == "G":
        c_hi = (1.0 + ptf_max) / (1.0 - td_max) if td_max < 1.0 else math.inf
    else:
        c_hi = 1.0 + ptf_max
    return c_hi * (1.0 + 1e-12), td_max, ptf_max


def cota_caja(box, fixed, dis, n, col=None):
    """(U, gradiente sobre B' o None); U = None si la caja está DOMINADA (todo r > 1)."""
    col = col or {}
    c = factor_c(box, fixed, dis)
    klo, khi = box["kappa_tilde"]
    ks = 1.0 / c.lo if c.lo > 0.0 else math.inf
    if ks < klo:
        n["dominadas"] += 1
        return None, None
    bm = dict(box, kappa_tilde=(klo, min(khi, ks)))
    ad_full, _ = SF.ub_formal(bm, fixed, dis)
    U = ad_full.v.hi                                   # encierro natural de UB en B' (cota válida de sup_B' UB)
    if ad_full.g is None:
        n["sin_gradiente"] += 1
        return U, None
    face = dict(bm, **{k: (v, v) for k, v in col.items()})
    ad, _ = SF.ub_formal(face, fixed, dis)
    cc = {p: (lo + (hi - lo) / 2,) * 2 for p, (lo, hi) in face.items()}
    adc, _ = SF.ub_formal(cc, fixed, dis)
    mv = adc.v
    for i, p in enumerate(MT.VARS):
        mv = mv + ad.g[i] * (Iv(*face[p]) - cc[p][0])
    n["valor_medio"] += 1
    return min(U, mv.hi, ad.v.hi), ad_full.g        # cara: sup_B' UB = sup_cara UB por monotonía demostrada en B'


def main():
    dis, j, out, tope = sys.argv[1], sys.argv[2], Path(sys.argv[3]), float(sys.argv[4])
    t0 = time.time()
    G = XD.grupo(dis, j)
    fixed = G["fixed"]
    N.need(float(fixed["z_m"]) == 1.0, "Z_M_DISTINTO_DE_1")
    mm = dict(XD.menu(j, G["bd"], G["bf"]), **G["full"])
    root = {p: mm[p] for p in MT.VARS}
    c_hi, td_max, ptf_max = precondicion(root, fixed, dis)
    N.need(c_hi < math.inf and 1.0 / c_hi >= root["kappa_tilde"][0], "LEMA_FUERA_DEL_SOPORTE_KAPPA")
    irr = set(XD.IRRELEVANTES[j])
    libres0 = [p for p in EJES if p not in irr and root[p][1] > root[p][0]]
    W = {p: root[p][1] - root[p][0] for p in libres0}
    gam = float(fixed["gamma"])
    n = {"cajas": 0, "podadas": 0, "dominadas": 0, "puntos": 0, "analiticas": 0, "valor_medio": 0, "sin_gradiente": 0, "colapsos": 0}
    best = {"L": -math.inf, "pt": None}
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "objeto": "sup C2: UB sobre la región r <= 1 (lema de dominación) + cota analítica",
           "diseno": dis, "instrumento": j, "plan_sha256": G["plan_sha256"], "dominio": {p: list(v) for p, v in root.items()},
           "T2": T2, "ejes_partidos": libres0, "valores_de_punto_para_ejes_no_usados_por_la_cota": FIJOS_PUNTO,
           "lema_precondicion": {"c_hi_por_subdivision": c_hi, "max_t_d": td_max, "max_phi_t_f": ptf_max, "kappa_prima_min": 1.0 / c_hi,
                                 "kappa_min_soporte": root["kappa_tilde"][0]}}
    t_esc = [0.0]

    def punto(pt, techo=math.inf):
        pt = dict(pt, **{k: v for k, v in FIJOS_PUNTO.items() if root[k][0] <= v <= root[k][1]})
        n["puntos"] += 1
        v = XD.punto(pt, fixed, dis)
        bx = {p: (pt[p], pt[p]) for p in root}
        r = factor_c(bx, fixed, dis) * pt["kappa_tilde"]
        if r.hi <= 1.0 and v.lo > techo:
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
        c2 = dict(col)
        for i, p in enumerate(MT.VARS):
            if p in libres0 and p != "kappa_tilde" and p not in c2 and box[p][1] > box[p][0] and g is not None:
                if g[i].lo > 0.0:
                    c2[p] = box[p][1]
                elif g[i].hi < 0.0:
                    c2[p] = box[p][0]
        return c2
    estado, traza, heap = "tope", [], []
    try:
        if dis in PUNTOS_PREVIOS and j == "df":
            punto(PUNTOS_PREVIOS[dis])
        u0, g0 = cota_caja(root, fixed, dis, n)
        N.need(u0 is not None, "RAIZ_DOMINADA")
        heap = [(-u0, 0, root, g0, {})]
        cont = 1
        while heap:
            Ucur = max(-heap[0][0], best["L"])
            if best["L"] > -heap[0][0] + 1e-12 * max(1.0, abs(best["L"])):
                raise Incompatible("PUNTO_SOBRE_COTA_GLOBAL: L %r > U %r" % (best["L"], -heap[0][0]))
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
            if g is not None:
                c2 = colapsar(box, col, g)
                if c2 != col:
                    n["colapsos"] += 1
                    u2, g2 = cota_caja(box, fixed, dis, n, c2)
                    if u2 is None:
                        continue
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
                u, gh = cota_caja(h, fixed, dis, n, col)
                if u is None:
                    continue
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
    print(json.dumps({k: doc.get(k) for k in ("diseno", "instrumento", "L", "U", "brecha", "estado", "cajas", "dominadas", "colapsos", "valor_medio", "puntos", "segundos")}))


if __name__ == "__main__":
    raise SystemExit(main())
