"""Muestra REPRESENTATIVA del trabajo pendiente de cobertura (CERTIFICACIÓN 3.7, NO OFICIAL).

  <py_integracion> -m codigo.muestra_costo --plan <plan.json> <n_por_familia> <semilla>
  <py_integracion> -m codigo.muestra_costo --trabajador <plan.json> <i> <n> <salida.json> <tope_cooperativo_s>
  python -m codigo.muestra_costo --agregar <plan.json> <salida.json> <t0.json> <t1.json> ...

Universo: las 157 afirmaciones pendientes del registro vigente (verificador_rendimiento_3_7/demo/registro/registro_v2.json,
autenticado), G 75 y N 82, todas del menú f. Unidad de trabajo: una caja L0 de la malla estructural (producto de los
intervalos de los ejes del soporte, idénticos en los 10 conjuntos) para UNA familia; en cada hoja se calcula UN encierro
de C2(familia, f) compartido por todas las afirmaciones pendientes de esa familia, y por afirmación G = C2 - K1 en todos
sus contextos (mismo código que cobertura_mejorada.py, M2r). Población por familia = todas las cajas L0.
Selección: muestra aleatoria simple sin reemplazo de cajas L0 con semilla fija; las MISMAS cajas para G y N (estratos
= familia). Pruebas de esfuerzo IDENTIFICADAS aparte (no entran en las estimaciones): las 3 cajas difíciles conocidas.
Método: M2r, memo, C2 normalizado, inicialización reutilizable; límites por caja: 64 hojas y 120 s de reloj
(cooperativo; al agotarse, lo no cerrado queda PENDIENTE y su costo cuenta).
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import statistics
import sys
import time
from collections import deque
from decimal import Decimal
from pathlib import Path

A = Path(__file__).resolve().parents[1]
ROOT = A.parents[1]
REG = ROOT / "tmp/verificador_rendimiento_3_7_2026-10-04"
REG_INV = "f09a37e7691c2c8b842772881519885e731a64956fba5fde775312ee14131d24"
REG_REL = "demo/registro/registro_v2.json"
HOJAS, SEG_CAJA = 64, 120.0
ESFUERZO = ["PER-E0E3.micro|2,0,0,0,3,2,0,0,1", "PER-E0E3.micro|2,1,2,1,4,0,2,1,1", "PER-E0E3.micro|1,2,1,0,4,1,2,0,1"]


def sha(b):
    return hashlib.sha256(b).hexdigest()


# CONSOLIDACIÓN 3.7: el lector ya NO carga por defecto las 157 pendientes del registro anterior. Por defecto lee el
# registro CANDIDATO autenticado de testigos_cobertura (1512 / 132 / 84); el registro_v2 (157) solo se lee si se pide
# explícitamente ("v2"), para reproducir experimentos de rondas anteriores.
CAND = ROOT / "tmp/testigos_cobertura_3_7_2026-10-04"
CAND_INV = "a56a37e72484de2d02709185416e3c44880cc4acc1ab932b75641b94e0b308fa"
CAND_REL = "demo/registro/registro_candidato.json"
REGISTROS = {"v2": (REG, REG_INV, REG_REL), "candidato": (CAND, CAND_INV, CAND_REL)}


def pendientes(registro="candidato"):
    base, inv_h, rel = REGISTROS[registro]
    inv = json.loads((base / "audit/entrega.json").read_bytes())
    assert sha((base / "audit/entrega.json").read_bytes()) == inv_h, "INVENTARIO_REGISTRO"
    raw = (base / rel).read_bytes()
    assert inv["files"][rel]["sha256"] == sha(raw), "REGISTRO_NO_AUTENTICADO"
    reg = json.loads(raw)["afirmaciones"]
    p = sorted(c for c, v in reg.items() if v["categoria"] == "candidata_sin_decision")
    return p, sha(raw)


def registro_de_plan(plan):
    """Registro con el que se hizo un plan (por su sha256): un trabajador nunca mezcla universos."""
    for nombre in REGISTROS:
        p, h = pendientes(nombre)
        if h == plan["registro_sha256"]:
            return p, h
    raise AssertionError("REGISTRO_DEL_PLAN_DESCONOCIDO")


def preparar(ctx, dis, pend_ids):
    from codigo.demo import cobertura_mejorada as CM
    from codigo.demo.universo import Universo, qmin_table
    from codigo.demo import nucleo_v as N
    from paper2b import run as RUNMOD
    cand_all, _ = CM.autenticados()
    cand = sorted(c for c in pend_ids if f":{dis}:" in c)
    N.need(all(c in cand_all for c in cand), "PENDIENTE_FUERA_DE_LAS_CANDIDATAS")
    claims = {c.claim_id: c for c in ctx.claims}
    sets = sorted({s for cid in cand for s in claims[cid].support_sets})
    runs = {sid: ctx.run(sid, "muestra:" + sid) for sid in sets}
    ref_sid = claims[CM.CLAIM_P3B].support_sets[0]
    if ref_sid not in runs:
        runs[ref_sid] = ctx.run(ref_sid, "muestra:" + ref_sid)
    axes = runs[ref_sid].struct_axes(ref_sid)
    N.need(all(runs[s].struct_axes(s) == axes for s in runs), "EJES_DISTINTOS_NO_SE_COMPARTE")
    ax0 = N.axes_nodes(ctx, ref_sid)
    corner = {p: Decimal(str(ax0[p][0])) for p in RUNMOD.STRUCT}
    U = Universo(runs, qmin_table(ctx.inp.grid_cells))
    univ, fixed_ref, compartir = {}, None, {}
    for cid in cand:
        cl = claims[cid]
        cx = []
        for sid in cl.support_sets:
            c, fx = U.contexts(cl, sid, corner)
            cx += [x for x, _ in c]
            fixed_ref = fixed_ref or fx
            compartir.setdefault(json.dumps(fx, sort_keys=True, default=str), []).append(cid)
        univ[cid] = cx
    N.need(len(compartir) == 1, "FIJOS_DISTINTOS")
    return {"cand": cand, "univ": univ, "fixed": fixed_ref, "model": runs[ref_sid].model, "axes": axes, "sets": sets}


def cubrir(st, dis, root, memo, MEMO, C2N, COV, ident):
    """Misma lógica que cobertura_mejorada (M2r, memo, normalizado) para UNA caja; devuelve conteos."""
    from paper2b import claims as CL
    EPS = CL.EPS_ECON
    model, fixed, univ, cand = st["model"], st["fixed"], st["univ"], st["cand"]
    bd, bf = float(fixed["bar_tau_d"]), float(fixed["bar_tau_f"])
    n_c2 = [0]

    def c2_of(b):
        n_c2[0] += 1
        k = MEMO.clave(b, dis, "f", bd, bf, fixed, model, "normalizado", ident)
        return memo.obtener(k, lambda: C2N.c2_normalizado(model, b, dis, "f", bd, bf, fixed=fixed), b)

    def eval_leaf(b, activos, c2):
        cerr, test, pend_ = set(), set(), set()
        for cid in activos:
            ghi, glo = -1e300, -1e300
            for c in univ[cid]:
                g = COV.g_enclosure(model, b, c, fixed, c2)
                if g is None:
                    ghi = glo = None
                    break
                ghi, glo = max(ghi, g.hi), max(glo, g.lo)
            if ghi is None:
                pend_.add(cid)
            elif ghi <= -EPS:
                cerr.add(cid)
            elif glo > -EPS:
                test.add(cid)
            else:
                pend_.add(cid)
        return cerr, test, pend_

    def split_axis(box, p):
        lo, hi = box[p]
        m = lo + (hi - lo) / 2
        return dict(box, **{p: (lo, m)}), dict(box, **{p: (m, hi)})
    tb = time.time()
    estado = {cid: "pendiente" for cid in cand}
    hojas_pend = {cid: 0 for cid in cand}
    q = deque([(root, set(cand), 0)])
    hojas, orden_ejes, ranking_s, tope_reloj = 0, None, 0.0, False
    while q:
        b, act, depth = q.popleft()
        act = {c for c in act if estado[c] != "testigo"}
        if not act:
            continue
        hojas += 1
        if not COV.box_admissible(b, fixed):
            pend_, cerr, test = set(act), set(), set()
        else:
            c2 = c2_of(b)
            cerr, test, pend_ = eval_leaf(b, act, c2) if c2 is not None else (set(), set(), set(act))
        for c in test:
            estado[c] = "testigo"
        if pend_:
            cen = {p: (lo + (hi - lo) / 2,) * 2 for p, (lo, hi) in b.items()}
            if COV.box_admissible(cen, fixed):
                c2c = c2_of(cen)
                if c2c is not None:
                    for cid in list(pend_):
                        if any(g is not None and g.lo > -EPS for g in (COV.g_enclosure(model, cen, c, fixed, c2c) for c in univ[cid])):
                            estado[cid] = "testigo"
                            pend_.discard(cid)
        if pend_:
            if hojas + len(q) + 2 <= HOJAS and time.time() - tb < SEG_CAJA:
                if orden_ejes is None and depth == 0:
                    a_r = time.time()
                    score = []
                    for p in COV.STRUCT:
                        if root[p][1] > root[p][0]:
                            hs = split_axis(root, p)
                            cs = [c2_of(h) if COV.box_admissible(h, fixed) else None for h in hs]
                            score.append((max((x.hi if x is not None else float("inf")) for x in cs), p))
                    orden_ejes = [p for _, p in sorted(score)[:3]]
                    ranking_s = time.time() - a_r
                p = orden_ejes[depth % len(orden_ejes)] if orden_ejes else None
                sub = split_axis(b, p) if (p and b[p][1] > b[p][0]) else COV._split(b)
                for s in sub or []:
                    q.append((s, set(pend_), depth + 1))
                if not sub:
                    for c in pend_:
                        hojas_pend[c] += 1
            else:
                tope_reloj = tope_reloj or not (time.time() - tb < SEG_CAJA)
                for c in pend_:
                    hojas_pend[c] += 1
    res = {cid: ("testigo" if estado[cid] == "testigo" else ("cerrada" if hojas_pend[cid] == 0 else "pendiente")) for cid in cand}
    cnt = {k: sum(1 for v in res.values() if v == k) for k in ("cerrada", "testigo", "pendiente")}
    return {"segundos": round(time.time() - tb, 3), "hojas": hojas, "subdivisiones": max(0, hojas - 1), "encierros_pedidos": n_c2[0],
            "ranking_s": round(ranking_s, 2), "conteo": cnt, "tope_reloj": tope_reloj, "cerrada_en_la_raiz": hojas == 1 and cnt["pendiente"] == 0,
            "completa": cnt["pendiente"] == 0}


def decodificar(k, radices):
    out = []
    for r in reversed(radices):
        out.append(k % r)
        k //= r
    return list(reversed(out))


def main():
    modo = sys.argv[1]
    if modo == "--agregar":
        return agregar(Path(sys.argv[2]), Path(sys.argv[3]), [Path(x) for x in sys.argv[4:]])
    from codigo.demo import nucleo_v as N
    from codigo.demo import c2_normalizado as C2N
    from codigo.demo import memo_c2 as MEMO
    from codigo.demo.cobertura_compartida import q_pot_exact
    from paper2b import cobertura as COV
    t0 = time.time()
    ctx = N.Contexto()
    COV.q_pot = q_pot_exact
    pend_ids, reg_sha = pendientes()
    if modo == "--plan":
        out, n, semilla = Path(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        sts = {d: preparar(ctx, d, pend_ids) for d in ("G", "N")}
        axes = sts["G"]["axes"]
        radices = [len(axes[p]) for p in COV.STRUCT]
        pob = math.prod(radices)
        idx = random.Random(semilla).sample(range(pob), n)
        muestra = [decodificar(k, radices) for k in idx]
        full = {p: (axes[p][0][0], axes[p][-1][1]) for p in COV.STRUCT}
        vol = lambda t: math.prod((axes[p][i][1] - axes[p][i][0]) / (full[p][1] - full[p][0]) for p, i in zip(COV.STRUCT, t))  # noqa: E731
        doc = {"etiqueta": N.ETIQUETA, "identidad_sha256": ctx.identity_sha256, "registro_sha256": reg_sha,
               "universo": {"pendientes": len(pend_ids), "G": len(sts["G"]["cand"]), "N": len(sts["N"]["cand"]),
                            "conjuntos_G": sts["G"]["sets"], "conjuntos_N": sts["N"]["sets"]},
               "unidad": "caja L0 x familia; un encierro de C2(familia, f) por hoja compartido por las afirmaciones pendientes de la familia",
               "poblacion_por_familia": pob, "radices": dict(zip(COV.STRUCT, radices)), "semilla": semilla, "n_por_familia": n,
               "seleccion": "muestra aleatoria simple sin reemplazo de cajas L0 (random.Random(semilla).sample); mismas cajas para G y N",
               "limites": {"hojas_por_caja": HOJAS, "segundos_por_caja": SEG_CAJA},
               "tareas": [{"familia": d, "indices": t, "volumen_relativo": vol(t), "tipo": "muestra"} for d in ("G", "N") for t in muestra],
               "esfuerzo": [{"familia": d, "clave": k, "indices": [int(x) for x in k.split("|")[1].split(",")], "tipo": "esfuerzo"}
                            for d in ("G", "N") for k in ESFUERZO]}
        N.write_json_atomic(out, doc)
        print(json.dumps({"poblacion_por_familia": pob, "tareas": len(doc["tareas"]), "esfuerzo": len(doc["esfuerzo"]), "universo": doc["universo"]})[:800])
        return 0
    plan_p, i_t, n_t, out, tope = Path(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), Path(sys.argv[5]), float(sys.argv[6])
    plan = json.loads(plan_p.read_text(encoding="utf-8"))
    pend_ids, reg_sha = registro_de_plan(plan)
    tareas = (plan["tareas"] + plan["esfuerzo"])[i_t::n_t]
    prep0 = time.time()
    sts = {d: preparar(ctx, d, pend_ids) for d in sorted({t["familia"] for t in tareas})}
    memo = MEMO.Memo(True)
    doc = {"etiqueta": N.ETIQUETA, "no_exportable": True, "identidad_sha256": ctx.identity_sha256, "plan_sha256": sha(plan_p.read_bytes()),
           "trabajador": i_t, "de": n_t, "inicializacion": ctx.init_info.get("modo"), "preparacion_s": round(time.time() - t0, 1),
           "preparacion_familias_s": round(time.time() - prep0, 1), "resultados": [], "no_procesadas_por_tope": []}
    for t in tareas:
        if time.time() - t0 > tope:
            doc["no_procesadas_por_tope"].append(t)
            continue
        st = sts[t["familia"]]
        root = {p: st["axes"][p][i] for p, i in zip(COV.STRUCT, t["indices"])}
        r = cubrir(st, t["familia"], root, memo, MEMO, C2N, COV, ctx.identity_sha256)
        doc["resultados"].append(dict(t, **r))
        doc["consumido_s"] = round(time.time() - t0, 1)
        N.write_json_atomic(out, doc)
    doc["consumido_s"] = round(time.time() - t0, 1)
    doc["memo"] = {"pedidos": memo.pedidos, "calculados": memo.calculados, "reutilizados": memo.reutilizados}
    N.write_json_atomic(out, doc)
    print(json.dumps({"resultados": len(doc["resultados"]), "no_procesadas": len(doc["no_procesadas_por_tope"]), "s": doc["consumido_s"]}))
    return 0


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


def media_ic(xs, z=1.96):
    if not xs:
        return None
    m = statistics.mean(xs)
    if len(xs) < 2:
        return {"media": m, "ic95": None, "n": len(xs)}
    s = statistics.stdev(xs) / math.sqrt(len(xs))
    return {"media": round(m, 3), "ic95": [round(m - z * s, 3), round(m + z * s, 3)], "n": len(xs), "max": round(max(xs), 3)}


def agregar(plan_p, out, partes):
    plan = json.loads(plan_p.read_text(encoding="utf-8"))
    res, sin, preps = [], [], []
    vistos = set()
    for q in partes:
        d = json.loads(q.read_text(encoding="utf-8"))
        res += d["resultados"]
        sin += d["no_procesadas_por_tope"]
        preps.append(d["preparacion_s"])
    # toda tarea del plan sin resultado (p. ej. trabajador cortado por el tope duro a mitad de una caja) cuenta como
    # PENDIENTE no procesada (agregado posterior al lanzamiento; ver adenda_2b)
    for r in res + sin:
        vistos.add((r["familia"], tuple(r["indices"]), r["tipo"]))
    for t in plan["tareas"] + plan["esfuerzo"]:
        if (t["familia"], tuple(t["indices"]), t["tipo"]) not in vistos:
            sin.append(dict(t, motivo="sin resultado: trabajador cortado o sin terminar"))
    pob = plan["poblacion_por_familia"]
    est = {}
    for fam in ("G", "N"):
        m = [r for r in res if r["familia"] == fam and r["tipo"] == "muestra"]
        np_ = [t for t in sin if t["familia"] == fam and t["tipo"] == "muestra"]
        n = len(m) + len(np_)
        raiz = [r for r in m if r["cerrada_en_la_raiz"]]
        sub = [r for r in m if r["completa"] and not r["cerrada_en_la_raiz"]]
        pen = [r for r in m if not r["completa"]]
        n_af = (len(m[0]["conteo"]) and sum(m[0]["conteo"].values())) if m else 0
        vol_tot = sum(r["volumen_relativo"] for r in m)
        est[fam] = {
            "muestra_planeada": plan["n_por_familia"], "procesadas": len(m), "no_procesadas_por_tope (cuentan como pendientes)": len(np_),
            "tramo_1_cierra_en_la_raiz": {"cajas": len(raiz), "proporcion_ic95": wilson(len(raiz), n), "segundos": media_ic([r["segundos"] for r in raiz])},
            "tramo_2_cierra_tras_subdividir": {"cajas": len(sub), "proporcion_ic95": wilson(len(sub), n), "segundos": media_ic([r["segundos"] for r in sub]),
                                               "subdivisiones": media_ic([r["subdivisiones"] for r in sub])},
            "tramo_3_pendiente (incluye topes y no procesadas)": {"cajas": len(pen) + len(np_), "proporcion_ic95": wilson(len(pen) + len(np_), n),
                                                                  "segundos_hasta_el_tope": media_ic([r["segundos"] for r in pen]),
                                                                  "por_tope_de_reloj": sum(1 for r in pen if r["tope_reloj"])},
            "pares_caja_afirmacion": {"afirmaciones": n_af, "cerrados": sum(r["conteo"]["cerrada"] for r in m), "testigo": sum(r["conteo"]["testigo"] for r in m),
                                      "pendientes": sum(r["conteo"]["pendiente"] for r in m)},
            "cajas_muestreadas_que_cierran_proporcion": wilson(len(raiz) + len(sub), n),
            "dominio_continuo_certificado_estimado": {"fraccion_de_volumen_de_las_cajas_muestreadas_cerradas": round(sum(r["volumen_relativo"] for r in raiz + sub) / vol_tot, 4) if vol_tot else None,
                                                      "nota": "estimador de razón por volumen relativo de cada caja L0; las cajas tienen volúmenes distintos"},
            "segundos_por_caja_todas": media_ic([r["segundos"] for r in m])}
        e = est[fam]
        if e["segundos_por_caja_todas"]:
            mm = e["segundos_por_caja_todas"]
            e["proyeccion_cpu_horas_si_todo_se_comportara_como_la_muestra"] = {
                "poblacion": pob, "media_h": round(pob * mm["media"] / 3600, 1),
                "ic95_h": [round(pob * x / 3600, 1) for x in mm["ic95"]] if mm.get("ic95") else None,
                "advertencia": "subestima: las cajas pendientes solo aportan su costo hasta el tope y NO quedan cerradas"}
    esf = [r for r in res if r["tipo"] == "esfuerzo"]
    doc = {"etiqueta": "CERTIFICACIÓN 3.7 NO OFICIAL", "plan_sha256": sha(plan_p.read_bytes()), "poblacion_por_familia": pob,
           "estimaciones": est, "pruebas_de_esfuerzo": [{k: r[k] for k in ("familia", "clave", "segundos", "hojas", "conteo", "tope_reloj", "completa")} for r in esf],
           "preparacion_por_trabajador_s": preps}
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(doc, ensure_ascii=False)[:3000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
