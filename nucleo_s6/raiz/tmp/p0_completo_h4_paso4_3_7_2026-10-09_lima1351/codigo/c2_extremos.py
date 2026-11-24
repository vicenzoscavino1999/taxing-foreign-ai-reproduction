"""C2 en df y d: diferencia entre el encierro de caja degenerada y el techo puntual, y rama y cota ESTRUCTURAL de las
envolventes (CONSOLIDACIÓN 3.7, NO OFICIAL).

  <py_integracion> -m codigo.c2_extremos evaluador <salida.json> <tope_por_variante_s> <tope_total_s>
  <py_integracion> -m codigo.c2_extremos bb <diseno> <instrumento> <sup|inf> <eventos.jsonl> <salida.json> <tope_s>

Grupos: los del plan autenticado de certificacion_3_7 (demo/C2/plan.json): por (diseño, instrumento) una caja completa
del soporte con fijos y barras comunes a sus 10 conjuntos (conjunto de referencia PER-E0E3.micro). T2 = 1e-4.

`evaluador` (pregunta: ¿por qué en el vértice superior G de df la caja degenerada da [0,00028; 0,718] con 400 cajas y el
techo puntual 0,0019140 ± 4e-8?). Mismo objeto (caja degenerada en el vértice superior: todos los ejes en su máximo;
ρ = 1, con curvas de SALTO S13) y el mismo motor normalizado; variantes de EM.sup_bound, cada una con su tope de reloj
(la evaluación se interrumpe si lo supera y se informa "sin terminar"):
  V0 jump_budget = 0, 400 cajas, tolerancia del proveedor (= c2_normalizado);
  V1 jump_budget = 600, 400 cajas (refinar solo las cajas vivas que tocan el salto);
  V2 jump_budget = 0, 2000 cajas;
  V3 jump_budget = 600, 2000 cajas.
Por variante: encierro, cajas, cajas vivas que tocan el salto y si la caja viva de mayor cota superior toca el salto.
También en N (mismo vértice) para obtener su cota puntual.

`bb` (rama y cota estructural, mejor primero): cola de cajas de parámetros ordenada por la cota LIMITANTE (sup: la de
mayor U = encierro.hi; inf: la de menor L = encierro.lo). Cada caja se divide por la mitad en el eje del ranking de la
raíz (los 3 ejes cuyo corte reduce más la cota limitante, en ciclo por profundidad). Cotas válidas sin evaluar puntos
aparte: para el supremo, L = máx de encierro.lo de las cajas evaluadas (C2 >= encierro.lo en toda la caja) y U = máx de
encierro.hi de las vivas; para el ínfimo, U' = mín de encierro.hi y L' = mín de encierro.lo de las vivas. Se poda una
caja con encierro.hi <= L (sup) o encierro.lo >= U' (inf). Cada caja evaluada se guarda al instante (JSONL + fsync).
Se parte de las cotas ya existentes (entregas certificacion y testigos_cobertura, autenticadas) para L (sup) y U' (inf).
"""
from __future__ import annotations

import heapq
import json
import os
import sys
import time
from pathlib import Path

from .demo import nucleo_v as N
from .demo import c2_normalizado as C2N
from .demo.cobertura_compartida import q_pot_exact
from paper2b import cobertura as COV
from paper2b import encierros_modelo as EM
from paper2b.intervalos import Iv
from paper2b.supremum import axes as sup_axes

T2 = 1e-4
CERT = N.ROOT / "tmp/certificacion_3_7_2026-10-04"
CERT_INV = "99d51784614d96a099bc3371028818d45851146e3c088131fda902dcf81ce8e5"
PREV = N.ROOT / "tmp/testigos_cobertura_3_7_2026-10-04"
PREV_INV = "a56a37e72484de2d02709185416e3c44880cc4acc1ab932b75641b94e0b308fa"


class Tope(Exception):
    pass


def autenticado(base, inv_h, rel):
    inv_raw = (base / "audit/entrega.json").read_bytes()
    N.need(N.sha(inv_raw) == inv_h, "INVENTARIO:" + base.name)
    raw = (base / rel).read_bytes()
    N.need(json.loads(inv_raw)["files"][rel]["sha256"] == N.sha(raw), "NO_AUTENTICADO:" + rel)
    return json.loads(raw)


def grupo(ctx, dis, j):
    plan = autenticado(CERT, CERT_INV, "demo/C2/plan.json")
    gs = [g for g in plan["grupos"] if g["clave"]["diseno"] == dis and g["clave"]["instrumento"] == j]
    N.need(len(gs) == 1, "GRUPO_NO_UNICO")
    g = gs[0]
    sid = g["sid_ref"]
    r = ctx.run(sid, "c2ext:" + sid)
    key = g["clave"]
    full = {p: (float.fromhex(v[0]), float.fromhex(v[1])) for p, v in key["caja"].items()}
    fixed = {pid: next(n for n in r.inp.d7.nodes(sid, pid) if str(n) == key["fijos"][pid]) for pid in key["fijos"]}
    return g, r.model, full, fixed, float(fixed["bar_tau_d"]), float(fixed["bar_tau_f"])


def sup_bound_con_tope(model, box, dis, j, bd, bf, fixed, max_boxes, jump_budget, tope):
    """c2_normalizado con límite de cajas y presupuesto de salto dados, misma tolerancia; interrumpible por reloj."""
    P = EM.IParams.from_primitive_box(box, fixed)
    eng = C2N.MotorNormalizado(P, dis)
    fin = time.time() + tope
    orig = eng.R_box_g

    def rbg(*a, **k):
        if time.time() > fin:
            raise Tope()
        return orig(*a, **k)
    eng.R_box_g = rbg
    (dl, dh), (fl, fh) = sup_axes(j, bd, bf)
    c0, _ = eng.R(Iv.point(0.5 * (dl + dh)), Iv.point(0.5 * (fl + fh)))
    tol = max(model.struct_tol * P.gamma.lo, c0.hi - c0.lo)
    t = time.time()
    try:
        sb = EM.sup_bound(eng, j, bd, bf, tol=tol, max_boxes=max_boxes, jump_budget=jump_budget)
    except Tope:
        return {"terminado": False, "segundos": round(time.time() - t, 1), "evaluaciones": eng.evaluations}
    e = Iv(sb.lower, max(sb.lower, sb.upper)) / P.gamma
    live = sb.live
    ev_live = [orig(Iv(b[0], b[1]), Iv(b[2], b[3])) for b in live]
    jumps = sum(1 for _, info in ev_live if info.get("jump"))
    top_jump = bool(max(ev_live, key=lambda t: t[0].hi)[1].get("jump")) if ev_live else None
    return {"terminado": True, "encierro": [e.lo, e.hi], "ancho": e.hi - e.lo, "cajas": sb.boxes, "vivas": len(live),
            "vivas_que_tocan_salto": jumps, "mayor_cota_toca_salto": top_jump, "salto_vivo": sb.jump_live,
            "punto": list(sb.point), "segundos": round(time.time() - t, 1), "evaluaciones": eng.evaluations}


def evaluador(out, tope_var, tope_total):
    t0 = time.time()
    ctx = N.Contexto()
    COV.q_pot = q_pot_exact
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "identidad_sha256": ctx.identity_sha256, "T2": T2, "puntos": {}}
    diag = autenticado(PREV, PREV_INV, "demo/C2/df_diagnostico.json")
    doc["anterior"] = diag["puntos"]["vertice_superior:G"]
    for dis in ("G", "N"):
        g, model, full, fixed, bd, bf = grupo(ctx, dis, "df")
        vert = {p: (hi, hi) for p, (lo, hi) in full.items()}
        fila = {"punto": {p: v[0] for p, v in vert.items()}, "admisible": COV.box_admissible(vert, fixed),
                "coincide_con_el_anterior": {p: v[0] for p, v in vert.items()} == diag["puntos"]["vertice_superior:G"]["punto"]}
        for nombre, mb, jb in (("V0_salto0_400", 400, 0), ("V1_salto600_400", 400, 600), ("V2_salto0_2000", 2000, 0), ("V3_salto600_2000", 2000, 600)):
            if time.time() - t0 > tope_total:
                fila[nombre] = {"terminado": False, "motivo": "TOPE_TOTAL"}
                continue
            if dis == "N" and nombre in ("V0_salto0_400", "V2_salto0_2000"):
                continue                                  # en N solo las variantes con salto (cota puntual)
            fila[nombre] = sup_bound_con_tope(model, vert, dis, "df", bd, bf, fixed, mb, jb, tope_var)
            doc["puntos"]["vertice_superior:" + dis] = fila
            N.write_json_atomic(Path(out), doc)
        doc["puntos"]["vertice_superior:" + dis] = fila
        N.write_json_atomic(Path(out), doc)
    doc["segundos"] = round(time.time() - t0, 1)
    N.write_json_atomic(Path(out), doc)
    print(json.dumps({k: {n: (v.get("encierro"), v.get("segundos"), v.get("vivas_que_tocan_salto")) for n, v in f.items() if isinstance(v, dict) and n.startswith("V")}
                      for k, f in doc["puntos"].items()}, ensure_ascii=False))


def bb(dis, j, objetivo, ev_p, out, tope):
    t0 = time.time()
    ctx = N.Contexto()
    COV.q_pot = q_pot_exact
    g, model, full, fixed, bd, bf = grupo(ctx, dis, j)
    N.need(COV.box_admissible(full, fixed), "CAJA_NO_ADMISIBLE")
    prev_name = {"G": "demo/C2/envolventes_d_G.json", "N": "demo/C2/envolventes_d.json"} if j == "d" else None
    L0 = U0 = None
    if prev_name:
        prev = autenticado(PREV, PREV_INV, prev_name[dis])
        pg = [x for x in prev["grupos"] if x["diseno"] == dis and x["instrumento"] == j][0]
        L0, U0 = (pg["sup"]["L"], None) if objetivo == "sup" else (None, pg["inf"]["U"])
    fh = open(ev_p, "a", encoding="utf-8")

    def log(**kw):
        kw["t"] = round(time.time() - t0, 2)
        fh.write(json.dumps(kw, ensure_ascii=False, default=str) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    n_eval = [0]

    def enc(b):
        n_eval[0] += 1
        return C2N.c2_normalizado(model, b, dis, j, bd, bf, fixed=fixed) if COV.box_admissible(b, fixed) else None

    def half(b, p):
        lo, hi = b[p]
        m = lo + (hi - lo) / 2
        return dict(b, **{p: (lo, m)}), dict(b, **{p: (m, hi)})
    E = enc(full)
    log(evento="raiz", caja={p: list(v) for p, v in full.items()}, E=[E.lo, E.hi])
    sgn = 1 if objetivo == "sup" else -1
    # ranking de ejes en la raíz por la cota limitante de los hijos
    score = []
    for p in COV.STRUCT:
        if full[p][1] > full[p][0]:
            hs = half(full, p)
            es = [enc(h) for h in hs]
            lim = max(e.hi for e in es) if objetivo == "sup" else -min(e.lo for e in es)
            score.append((lim if all(e is not None for e in es) else float("inf"), p))
            log(evento="ranking", eje=p, hijos=[[e.lo, e.hi] if e else None for e in es])
    ejes = [p for _, p in sorted(score)[:3]]
    L = max([E.lo] + ([L0] if L0 is not None else [])) if objetivo == "sup" else None
    U = min([E.hi] + ([U0] if U0 is not None else [])) if objetivo == "inf" else None
    heap = [(-sgn * (E.hi if objetivo == "sup" else E.lo), 0, 0, full, E)]
    cont = 1
    tray = []
    estado = "acotado"
    while heap:
        lim = -heap[0][0] * sgn
        if objetivo == "sup":
            U = lim
            brecha = U - L
        else:
            Lp = lim
            brecha = U - Lp
        tray.append([round(time.time() - t0, 1), n_eval[0], (L, U) if objetivo == "sup" else (Lp, U), brecha])
        if brecha <= T2:
            estado = "encerrado_a_tolerancia"
            break
        if time.time() - t0 > tope:
            estado = "acotado (tope)"
            break
        _, _, depth, b, eb = heapq.heappop(heap)
        p = ejes[depth % len(ejes)]
        for h in half(b, p):
            e = enc(h)
            if e is None:
                log(evento="hija_no_admisible", caja={q: list(v) for q, v in h.items()})
                heapq.heappush(heap, (-sgn * (eb.hi if objetivo == "sup" else eb.lo), cont, depth + 1, h, eb))   # conserva la cota del padre
                cont += 1
                continue
            if objetivo == "sup":
                L = max(L, e.lo)
                vivo = e.hi > L
            else:
                U = min(U, e.hi)
                vivo = e.lo < U
            log(evento="caja", profundidad=depth + 1, eje=p, caja={q: list(v) for q, v in h.items()}, E=[e.lo, e.hi], viva=vivo)
            if vivo:
                heapq.heappush(heap, (-sgn * (e.hi if objetivo == "sup" else e.lo), cont, depth + 1, h, e))
                cont += 1
        heap = [x for x in heap if (x[4].hi > L if objetivo == "sup" else x[4].lo < U)]
        heapq.heapify(heap)
    if not heap:                                          # todo podado: el extremo queda en la cota alcanzada
        estado = "encerrado_a_tolerancia"
        if objetivo == "sup":
            U = L
        else:
            Lp = U
    if objetivo == "sup":
        res = {"L": L, "U": U, "brecha": U - L}
    else:
        res = {"L": Lp, "U": U, "brecha": U - Lp}
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "identidad_sha256": ctx.identity_sha256, "grupo": g["grupo"], "diseno": dis,
           "instrumento": j, "objetivo": objetivo, "dominio": {p: list(v) for p, v in full.items()}, "fijos": {k: str(v) for k, v in fixed.items()},
           "T2": T2, "raiz": [E.lo, E.hi], "partida": {"L_sup_previa": L0, "U_inf_previa": U0}, "ejes": ejes, **res, "estado": estado,
           "encierros": n_eval[0], "vivas": len(heap), "trayectoria": tray[:: max(1, len(tray) // 60)] + tray[-1:], "segundos": round(time.time() - t0, 1)}
    N.write_json_atomic(Path(out), doc)
    print(json.dumps({k: doc[k] for k in ("diseno", "instrumento", "objetivo", "raiz", "L", "U", "brecha", "estado", "encierros", "segundos")}))


def techo(dis, out, tope):
    """Techo PUNTUAL certificado del proveedor (Run.ceiling -> capture_ceiling, como en c2_df_diagnostico) en el vértice
    superior del grupo df: si el vértice es admisible, C2 + error es una cota superior VÁLIDA del ínfimo del grupo (punto
    admisible del dominio); no sustituye ninguna cota sobre cajas."""
    from decimal import Decimal
    t0 = time.time()
    ctx = N.Contexto()
    COV.q_pot = q_pot_exact
    g, model, full, fixed, bd, bf = grupo(ctx, dis, "df")
    r = ctx.run(g["sid_ref"], "c2techo:" + g["sid_ref"])
    pt = {p: hi for p, (lo, hi) in full.items()}
    b = {p: (v, v) for p, v in pt.items()}
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "identidad_sha256": ctx.identity_sha256, "grupo": g["grupo"], "diseno": dis,
           "instrumento": "df", "punto": pt, "admisible": COV.box_admissible(b, fixed)}
    if doc["admisible"]:
        _, hit = r.ceiling(dict({p: Decimal(repr(float(v))) for p, v in pt.items()}, **fixed), dis, "df")
        ce = hit["ceiling"]
        doc["techo"] = {"C2": ce.C2, "error": ce.numerical_error, "estado": ce.status, "motivo": ce.reason}
        if ce.C2 is not None and ce.numerical_error is not None:
            doc["techo"]["intervalo"] = [ce.C2 - ce.numerical_error, ce.C2 + ce.numerical_error]
    doc["segundos"] = round(time.time() - t0, 1)
    N.write_json_atomic(Path(out), doc)
    print(json.dumps({k: doc.get(k) for k in ("diseno", "admisible", "techo", "segundos")}, default=str))


def main():
    if sys.argv[1] == "techo":
        techo(sys.argv[2], sys.argv[3], float(sys.argv[4]))
        return 0
    if sys.argv[1] == "evaluador":
        evaluador(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]))
    elif sys.argv[1] == "bb":
        bb(sys.argv[2], sys.argv[3], sys.argv[4], Path(sys.argv[5]), sys.argv[6], float(sys.argv[7]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
