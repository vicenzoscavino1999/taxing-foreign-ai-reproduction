"""Ínfimo de C2 en df (G o N): rama y cota en θ para la COTA INFERIOR global con la cota «todos formales» afín en s (v3) y
partición RESTRINGIDA a (a, κ̃, φ) con elección del eje por anchura normalizada (CIERRE INF DF Y PASO 4 3.7, NO OFICIAL).
VERSIÓN v5 (inf_df_bb_v4 y v4b no se modifican): el OBJETIVO de brecha es un argumento (para medir cuánto margen bajo T2
se alcanza) y el eje se elige por mayor anchura NORMALIZADA entre (a, κ̃, φ) (κ̃ en escala log), no por ramificación fuerte
(miope: INFBB4b-N, logs/INCIDENCIAS_RONDA.txt); el estado «convergido» sigue refiriéndose a T2 y se informa aparte si se alcanzó el
objetivo.

  <py_integracion> -m codigo.inf_df_bb_v5 <G|N> <certificado_U.json> <salida.json> <tope_s> <objetivo_brecha>

Por qué basta partir (a, κ̃, φ) (review/FUNDAMENTO_INFIMOS_DF.md §3). La cota de una caja es, para un τ común,
  min_{s ∈ {s.lo, s.hi}} [τ_d r* + s D(τ)]   si (P), (F), (I) valen en toda la caja,
y cada eje entra así:
  - z_cost, u_θ, β̃: solo en las condiciones, por δ = z_cost^(−u_θ (a − 1)) γ (decreciente en los tres) y tb = τ_d β̃ γ;
    el encierro natural las evalúa en la esquina peor (una sola aparición): partirlos no cambia la cota en esa esquina;
  - ρ: solo en s (exacto por s_rango, en ρ.lo / ρ.hi);
  - η_f: q* = (1 − τ_f)^η_f (valor) y t̃_f (condiciones) empeoran ambos al crecer η_f: sin pérdida por dependencia;
  - η_d: r* (valor) empeora al crecer η_d y t̃_d (condiciones) al decrecer: pérdida O(τ_d²) (< 1e-6 relativo aquí);
  - a: δ (condiciones, peor en a.hi) y q (valor, peor en a.lo): dependencia ⇒ se parte;
  - κ̃: condiciones (peor en κ̃.hi) y s (valor, peor en κ̃.lo) ⇒ se parte (en escala geométrica);
  - φ: condiciones (peor en φ.hi) y g_f, t̃_f (valor) ⇒ se parte.
Partir solo estos ejes da una cota VÁLIDA en toda caja (los demás ejes quedan en su rango completo, encerrados); la
restricción solo decide dónde se refina. Eje elegido: el que maximiza la menor cota de sus dos hijas (se prueban los
tres). U: el CERTIFICADO (techo v3 en un punto admisible) leído de <certificado_U.json>. Poda: cota >= U − T2.
INCOMPATIBLE (se detiene y se informa) si L > U.
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
from codigo.inf_df_bb_v3 import lb_caja  # noqa: E402
from codigo.demo import nucleo_v as N  # noqa: E402

T2 = 1e-4
EJES = ("a", "kappa_tilde", "phi")


def partir(th, p):
    lo, hi = th[p]
    m = math.sqrt(lo * hi) if p == "kappa_tilde" else lo + (hi - lo) / 2
    return dict(th, **{p: (lo, m)}), dict(th, **{p: (m, hi)})


def main():
    dis, cert_p, out, tope, objetivo = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
    t0 = time.time()
    G = XD.grupo(dis, "df")
    fixed, bd, bf, full = G["fixed"], G["bd"], G["bf"], G["full"]
    N.need(float(fixed["z_m"]) == 1.0, "Z_M_DISTINTO_DE_1")
    cert = json.loads(cert_p.read_text(encoding="utf-8"))
    # salida (final o instantánea parcial) de certificar_inf_df / certificar_puntos: el menor U de las filas admisibles y
    # compatibles (U >= L_punto) del diseño
    filas = [f for f in cert["filas"] if f.get("admisible") and "U" in f and not f["incompatible"]]
    N.need(filas and all(f.get("diseno", dis) == dis for f in filas), "CERTIFICADO_U_INVALIDO")
    mejor = min(filas, key=lambda f: f["U"])
    U = float(mejor["U"])
    n = {"divisiones": 0, "evaluaciones_caja": 0}
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True,
           "objeto": "inf C2 df: cota inferior global v5 (afín en s; partición en a, κ̃, φ por anchura normalizada)",
           "diseno": dis, "instrumento": "df", "plan_sha256": G["plan_sha256"], "dominio": {p: list(v) for p, v in full.items()},
           "T2": T2, "U": U, "ejes_partidos": list(EJES),
           "certificado_U": {"archivo": cert_p.as_posix(), "sha256": N.sha(cert_p.read_bytes()), "punto": mejor["theta"],
                             "L_punto": mejor["L_punto"]}}

    def lb(th):
        n["evaluaciones_caja"] += 1
        return lb_caja(th, fixed, dis, bd, bf)
    v0 = lb(full)
    heap = [(v0[0], 0, full, v0[1])]
    cont, estado, traza, t_esc = 1, "tope", [], [0.0]
    usos = {p: 0 for p in EJES}
    while heap:
        L = heap[0][0]
        if L > U:
            estado = "INCOMPATIBLE_L_MAYOR_QUE_U"
            break
        if n["divisiones"] % 25 == 0:
            traza.append([round(time.time() - t0, 1), n["divisiones"], L])
        if time.time() - t_esc[0] > 15:
            doc.update(L=L, brecha=U - L, vivas=len(heap), segundos=round(time.time() - t0, 1), usos_por_eje=usos, **n)
            N.write_json_atomic(out, doc)
            t_esc[0] = time.time()
        if U - L <= objetivo:
            estado = "objetivo_alcanzado"
            break
        if time.time() - t0 > tope:
            break
        plb, _, th, tau = heapq.heappop(heap)
        n["divisiones"] += 1
        ls = [q for q in EJES if th[q][1] > th[q][0]]
        if not ls:
            heapq.heappush(heap, (plb, cont, th, tau))
            estado = "caja_degenerada_viva"
            break
        p = max(ls, key=lambda q: (math.log(th[q][1] / th[q][0]) / math.log(full[q][1] / full[q][0])) if q == "kappa_tilde"
                else (th[q][1] - th[q][0]) / (full[q][1] - full[q][0]))
        hs = partir(th, p)
        vs = [lb(h) for h in hs]
        usos[p] += 1
        for h, (v, t) in zip(hs, vs):
            heapq.heappush(heap, (max(v, plb), cont, h, t))
            cont += 1
    L = heap[0][0] if heap else U
    doc.update(objetivo=objetivo, convergido_T2=(U - L <= T2), L=L, brecha=U - L, estado=estado, vivas=len(heap), usos_por_eje=usos,
               caja_de_menor_cota={q: list(v) for q, v in heap[0][2].items()} if heap else None, tau_de_la_cota=heap[0][3] if heap else None,
               traza=traza[:: max(1, len(traza) // 60)] + traza[-1:], segundos=round(time.time() - t0, 1), **n)
    N.write_json_atomic(out, doc)
    print(json.dumps({k: doc.get(k) for k in ("diseno", "L", "U", "brecha", "estado", "divisiones", "segundos")}))


if __name__ == "__main__":
    raise SystemExit(main())
