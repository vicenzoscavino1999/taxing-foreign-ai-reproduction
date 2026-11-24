"""PLAN EJECUTABLE v1 (rem43; candidato; NO OFICIAL; sin cálculo): partición v2 con COSTES RECONCILIADOS y CALENDARIO SECUENCIAL para el
mecanismo vigente (UNA tarea activa a la vez; 3 procesos por tarea como máximo). Cadena verificable:
  presupuesto autenticado -> plan sellado (construir_plan) -> ESPECIFICACIÓN fijada (datos/paso4/calendario_v1.json, sha256 en
  ESPECIFICACION: parámetros medidos y particiones) -> aplicar() -> plan ejecutable (tareas, dependencias de caché, suites, rondas) que el
  VÍNCULO reconstruye (escenarios «*-ejecutable-v1»).
COSTES (por tarea; s de pared):
  preparación = la MEDIDA del trabajador real hasta la frontera (contexto S6 + Referencia + vínculo + selección) con el contexto del
    escenario si es mayor: prep_medida - ctx_medido + max(ctx_medido, ctx_modelo[esc]) (central 50,3 / prudente 99,1 s);
  cálculo = modelo del presupuesto SIN su contexto por proceso (ya incluido en la preparación medida: no se cuenta dos veces) = Σ pared
    propia + Σ macro por frontera distinta + frío por clave distinta no disponible + carga de disco por clave disponible;
  validación = plan15 (central 53,5 / prudente 116,7 s por tarea);  margen = (factor-1) × cálculo, SEPARADO;
  sin_margen = preparación + cálculo + validación;  con_margen = sin_margen + margen.
CACHÉ CONDICIONADA: una clave se presupuesta caliente SOLO si la pagó una parte ANTERIOR de la MISMA tarea original; la parte que la usa
  DECLARA depende_de esa parte (el coordinador no la lanza si la anterior no quedó aceptada, y el almacén de techos verifica la identidad
  al cargar). Si la pagadora requiere excepción (o es a su vez condicionada), el coste SEGURO es en FRÍO; si en frío no cabe pero en
  caliente sí, la parte queda «condicionada_a» esa excepción: fuera del calendario ejecutable hasta que se decida y termine. Entre tareas
  distintas: siempre FRÍO.
PARTICIÓN v2: una tarea R2/R3 cabe entera si su con_margen <= tope; si no, empaquetado SECUENCIAL por fronteras en el orden del plan con
  esos costes; una unidad que sola no cabe con margen queda en su propia parte «requiere_excepcion» (no se parte ni se suben topes).
CALENDARIO: orden = calendario sellado aplanado (R2 y R3) y luego R1 en orden topológico; las partes de una tarea forman una CADENA
  indivisible por ronda (su caché vive en la corrida de la ronda); suites <= 3600 s y rondas <= 10 800 s de unión (con margen); las
  tareas «requiere_excepcion» quedan FUERA del calendario ejecutable (pendientes de decisión, sin excluir sus unidades).
  aplicar(plan_base, presupuesto, espec, clase_de) -> plan ejecutable;  verificar(plan_base, plan) -> informe"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import rebalanceo_paso4 as RB

INSTALACION = Path(__file__).resolve().parents[2]
ESPECIFICACION = ("datos/paso4/calendario_v2.json", "d21b962a7cd2543b3e5468f8631786becdffc6ed9ef9a0c7f3fcedbfe507dfb2")      # rem44: v2 (topes, comparación supervisada, estado operativo)
ESCENARIOS = {"central-ejecutable-v2": "central", "prudente-ejecutable-v2": "prudente"}
LIMITES = {"tarea_s": 2400.0, "suite_s": 3600.0, "ronda_union_s": 10800.0, "factor_margen": 1.25}
# rem44 (P4-CALENDARIO-EFECTIVO): cada lanzamiento (tarea o comparación) se ADMITE si unión/suite transcurridas + su tope + 90 s caben; el
# calendario se empaqueta con los TOPES (peor caso que garantiza la admisión de todos) y la comparación SUPERVISADA cuenta en la unión.
MARGEN_TERMINACION_S, TOPE_COMPARACION_S = 90.0, 120.0


def tope_de(con_margen_s: float) -> float:
    """Tope asignado = el coste con margen redondeado al alza a 10 s (nunca por encima del tope ordinario)."""
    import math
    return float(min(LIMITES["tarea_s"], math.ceil(con_margen_s / 10.0) * 10.0))


class CalendarioError(RuntimeError):
    pass


def need(t, c, d=""):
    if not t:
        raise CalendarioError("%s: %s" % (c, d) if d else c)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canon(o) -> bytes:
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")


def parametros(presupuesto: dict, esc: str, medidos: dict) -> dict:
    """medidos: {"R2": {"preparacion_s", "contexto_s"}, "R3": {...}, "R1": {...}} (trabajador real hasta la frontera, esta ronda)."""
    par = presupuesto["parametros_registrados"]
    k = "central" if esc == "central" else "prudente"
    ctxm = float(par["contexto_por_proceso_s"][k])
    prep = {f: round(m["preparacion_s"] - m["contexto_s"] + max(m["contexto_s"], ctxm), 1) for f, m in medidos.items()}
    return {"escenario": esc, "preparacion_s": prep, "validacion_s": float(par["validacion_por_tarea"]["%s_pared" % k]), "contexto_modelo_s": ctxm,
            "medidos": medidos, **LIMITES}


def coste(presupuesto: dict, esc: str, unidades: list, pagadas: set, fase: str, P: dict) -> dict:
    c = RB.coste_calculo(presupuesto, esc, unidades, pagadas)
    calc = round(c["calculo_s"] - c["contexto"], 1)
    prep, val, f = P["preparacion_s"][fase], P["validacion_s"], P["factor_margen"]
    sin = round(prep + calc + val, 1)
    return {"preparacion_s": prep, "calculo_s": calc, "validacion_s": val, "margen_s": round((f - 1) * calc, 1), "sin_margen_s": sin,
            "con_margen_s": round(sin + (f - 1) * calc, 1), "detalle_calculo": {k: c[k] for k in ("propia", "macro", "frio", "carga_disco", "fronteras", "claves")}}


def particion(plan: dict, presupuesto: dict, P: dict) -> dict:
    esc, tope, cu = plan["escenario"], P["tarea_s"], presupuesto["costes_por_unidad"]
    part, no_caben = {}, []
    clave = lambda us: {cu[u]["clave"] for u in us}  # noqa: E731
    for t in plan["tareas"]:
        if t.get("requiere_excepcion"):
            continue                                                   # suspendida en el plan sellado: intacta
        cabe = lambda us, pag: coste(presupuesto, esc, us, pag, t["fase"], P)["con_margen_s"] <= tope  # noqa: E731
        if cabe(t["unidades"], set()):
            continue
        grupos = {}
        for u in t["unidades"]:
            grupos.setdefault(cu[u]["frontera"], []).append(u)
        partes, actual, pag = [], [], set()                           # pag: claves pagadas por partes ANTERIORES (las de excepción, en condicional)
        for g in grupos.values():
            trozos = [g] if cabe(g, pag) or len(g) == 1 else [[u] for u in g]
            for tr in trozos:
                if cabe(actual + tr, pag):
                    actual += tr
                    continue
                if actual:
                    partes.append(actual)
                    pag |= clave(actual)
                    actual = []
                if cabe(tr, pag):
                    actual = list(tr)
                elif len(tr) == 1:                                     # la UNIDAD sola no cabe: parte propia en excepción (su caché, CONDICIONAL)
                    no_caben.append(tr[0])
                    partes.append(list(tr))
                    pag |= clave(tr)
                else:
                    for u in tr:
                        if cabe(actual + [u], pag):
                            actual.append(u)
                            continue
                        if actual:
                            partes.append(actual)
                            pag |= clave(actual)
                            actual = []
                        if cabe([u], pag):
                            actual = [u]
                        else:
                            no_caben.append(u)
                            partes.append([u])
                            pag |= clave([u])
        if actual:
            partes.append(actual)
        part[t["id"]] = [[u for u in t["unidades"] if u in set(p)] for p in partes]
    return {"particiones": part, "no_caben": sorted(no_caben)}


def aplicar(plan: dict, presupuesto: dict, espec: dict, clase_de) -> dict:
    need(espec.get("plan_base_sha256") == plan["plan_sha256"], "CALENDARIO_DE_OTRO_PLAN")
    need(espec.get("presupuesto_sha256") == plan["presupuesto_sha256"], "CALENDARIO_DE_OTRO_PRESUPUESTO")
    P, esc, cu = espec["parametros"], plan["escenario"], presupuesto["costes_por_unidad"]
    need(set(espec["particiones"]) <= {t["id"] for t in plan["tareas"]}, "PARTICION_DE_TAREA_INEXISTENTE")
    nc = set(espec.get("no_caben", []))
    tareas, sust = [], {}
    for t in plan["tareas"]:
        ps = espec["particiones"].get(t["id"]) or [list(t["unidades"])]
        planos = [u for p in ps for u in p]
        need(all(ps) and len(planos) == len(set(planos)) and sorted(planos) == sorted(t["unidades"]), "PARTICION_NO_EXACTA", t["id"])
        pagadoras, ids = {}, []
        for i, p in enumerate(ps, 1):
            us = [u for u in t["unidades"] if u in set(p)]
            need(us == list(p), "PARTE_FUERA_DE_ORDEN", t["id"])
            nid = t["id"] if len(ps) == 1 else "%s.p%d" % (t["id"], i)
            usadas = {cu[u]["clave"] for u in us}
            seguras = {k: pagadoras[k][0] for k in usadas if k in pagadoras and not pagadoras[k][1]}
            condic = {k: pagadoras[k][0] for k in usadas if k in pagadoras and pagadoras[k][1]}
            c = coste(presupuesto, esc, us, set(seguras), t["fase"], P)          # SIN depender de partes en excepción o condicionadas
            cond = []
            calientes = dict(seguras)
            if c["con_margen_s"] > P["tarea_s"] and condic:
                cc = coste(presupuesto, esc, us, set(seguras) | set(condic), t["fase"], P)
                if cc["con_margen_s"] <= P["tarea_s"]:                     # cabe SOLO si la parte en excepción se autoriza y termina
                    c, cond = cc, sorted(set(condic.values()))
                    calientes.update(condic)
            exc = bool(t.get("requiere_excepcion")) or (c["con_margen_s"] > P["tarea_s"])
            need(not exc or t.get("requiere_excepcion") or (len(us) == 1 and us[0] in nc), "PARTE_NO_CABE", "%s %.1f" % (nid, c["con_margen_s"]))
            clases = {}
            for u in us:
                clases[clase_de(u)] = clases.get(clase_de(u), 0) + 1
            tareas.append({"id": nid, "fase": t["fase"], "carril": t["carril"], "unidades": us, "asignacion_sha256": sha(canon(us)), "pared_s": c["sin_margen_s"],
                           "cpu_s": None, "requiere_excepcion": exc, "clases": clases, "coste": c,
                           "depende_de_expandido": sorted(set(calientes.values())), "cache_caliente": sorted(calientes), "condicionada_a": cond,
                           "origen": {"tarea": t["id"], "asignacion_sha256": t["asignacion_sha256"], "parte": i if len(ps) > 1 else None}})
            for k in usadas:                                                    # (parte, condicional): excepción o condicionada -> caché CONDICIONAL
                pagadoras.setdefault(k, (nid, bool(exc or cond)))
            ids.append(nid)
        sust[t["id"]] = ids
    r1 = []
    for t in plan["r1"]:
        prep, f = P["preparacion_s"]["R1"], P["factor_margen"]
        calc = round(float(t["pared_s"]), 1)
        cr = {"preparacion_s": prep, "calculo_s": calc, "validacion_s": 0.0, "margen_s": round((f - 1) * calc, 1),
              "sin_margen_s": round(prep + calc, 1), "con_margen_s": round(prep + f * calc, 1)}
        r1.append(dict(t, coste=cr, requiere_excepcion=bool(t["requiere_excepcion"]) or cr["con_margen_s"] > P["tarea_s"]))
    est_r1 = espec.get("estado_r1") or {}
    for t in tareas:
        t["tope_asignado_s"] = tope_de(t["coste"]["con_margen_s"])
        t["comparacion"] = {"supervisada": True, "tope_s": TOPE_COMPARACION_S}
        t["estado_operativo"] = {"presupuestada": True, "implementada": True, "decision_pendiente": [], "autorizada": False, "comprobada_productivamente": False}
    for t in r1:
        e = est_r1.get(t["id"]) or {"implementada": False, "decision_pendiente": ["sin conexión registrada"]}
        t["tope_asignado_s"] = tope_de(t["coste"]["con_margen_s"])
        t["comparacion"] = {"supervisada": False, "nota": "R1: la comparación con las referencias es parte de su aceptación (cobertura/validación) y de R1-V"}
        t["estado_operativo"] = {"presupuestada": True, "implementada": bool(e["implementada"]), "decision_pendiente": list(e["decision_pendiente"]),
                                 "autorizada": False, "comprobada_productivamente": False}
    cal, pendientes = calendario(plan, tareas, r1, sust, P)
    cuerpo = {k: v for k, v in plan.items() if k not in ("plan_sha256", "anexo_comandos")}
    cuerpo.update(kind="plan-corrida-paso4-ejecutable-v2", escenario="%s-ejecutable-v2" % esc, tareas=tareas, r1=r1, calendario=cal,
                  ejecutable={"plan_base_sha256": plan["plan_sha256"], "especificacion_sha256": sha(canon(espec)), "parametros": P,
                              "pendientes_de_decision": pendientes, "sustituciones": {k: v for k, v in sust.items() if v != [k]}})
    cuerpo["resumen"] = dict(plan["resumen"], tareas_R2=sum(t["fase"] == "R2" for t in tareas), tareas_R3=sum(t["fase"] == "R3" for t in tareas),
                             requieren_excepcion=[t["id"] for t in tareas + r1 if t["requiere_excepcion"]])
    return dict(cuerpo, plan_sha256=sha(canon(cuerpo)))


def calendario(plan: dict, tareas: list, r1: list, sust: dict, P: dict):
    """Rondas secuenciales (una tarea activa): cadenas indivisibles por ronda, suites <= suite_s, unión de ronda <= ronda_union_s."""
    por = {t["id"]: t for t in tareas}
    fuera = {t["id"] for t in tareas if t["requiere_excepcion"] or t.get("condicionada_a")} | {t["id"] for t in r1 if t["requiere_excepcion"]} | \
        {t["id"] for t in tareas + r1 if not t["estado_operativo"]["implementada"] or t["estado_operativo"]["decision_pendiente"]}
    for x in plan["r1_orden"]:                                            # una R1 cuyas dependencias quedan pendientes, también
        t = next(y for y in r1 if y["id"] == x)
        if any(d in fuera for d in t.get("depende_de_expandido") or []):
            fuera.add(x)
    plano = [x for r in plan["calendario"] for c in r["carriles"] for g in c for x in g]
    cadenas, vistos = [], set()
    for x in plano:
        if x in sust and x not in vistos:
            vistos.add(x)
            ch = [por[y] for y in sust[x] if y not in fuera]
            if ch:
                cadenas.append(ch)
    rid = {t["id"]: t for t in r1}
    for x in plan["r1_orden"]:
        if x not in fuera:
            cadenas.append([rid[x]])
    pend = [{"tarea": t["id"], "tipo": "requiere_excepcion" if t["requiere_excepcion"] else ("condicionada" if t.get("condicionada_a") else
                                                                                         "decision_pendiente" if t["estado_operativo"]["decision_pendiente"] else
                                                                                         "sin_conexion" if not t["estado_operativo"]["implementada"] else "dependencia_pendiente"),
             "decision_pendiente": t["estado_operativo"]["decision_pendiente"],
             "condicionada_a": t.get("condicionada_a") or [], "con_margen_s": t["coste"]["con_margen_s"], "sin_margen_s": t["coste"]["sin_margen_s"]}
            for t in tareas + r1 if t["id"] in fuera]
    lim_r, lim_s = P["ronda_union_s"] - MARGEN_TERMINACION_S, P["suite_s"] - MARGEN_TERMINACION_S
    peso = lambda t: t["tope_asignado_s"] + (t["comparacion"]["tope_s"] if t["comparacion"].get("supervisada") else 0.0)  # noqa: E731
    rondas, actual, carga = [], [], 0.0
    for ch in cadenas:
        s_ = sum(peso(t) for t in ch)
        need(s_ <= lim_r, "CADENA_MAYOR_QUE_UNA_RONDA", ch[0]["id"])
        if carga + s_ > lim_r and actual:
            rondas.append(actual)
            actual, carga = [], 0.0
        actual += ch
        carga += s_
    if actual:
        rondas.append(actual)
    out = []
    for n, ts in enumerate(rondas, 1):
        suites, su, cs = [], [], 0.0
        for t in ts:
            c = peso(t)
            if cs + c > lim_s and su:
                suites.append(su)
                su, cs = [], 0.0
            su.append(t)
            cs += c
        if su:
            suites.append(su)
        cg = lambda xs, k: round(sum(x["coste"][k] for x in xs), 1)  # noqa: E731
        sus = [{"tareas": [x["id"] for x in s2], "topes_s": {x["id"]: x["tope_asignado_s"] for x in s2},
                "comparaciones": [x["id"] for x in s2 if x["comparacion"].get("supervisada")], "topes_total_s": round(sum(peso(x) for x in s2), 1),
                "con_margen_s": round(cg(s2, "con_margen_s") + sum(TOPE_COMPARACION_S for x in s2 if x["comparacion"].get("supervisada")) * 0 + 17.6 * sum(1 for x in s2 if x["comparacion"].get("supervisada")), 1),
                "sin_margen_s": round(cg(s2, "sin_margen_s") + 17.6 * sum(1 for x in s2 if x["comparacion"].get("supervisada")), 1)} for s2 in suites]
        out.append({"ronda": n, "suites": sus, "union_topes_s": round(sum(x["topes_total_s"] for x in sus), 1),
                    "union_con_margen_s": round(sum(x["con_margen_s"] for x in sus), 1), "union_sin_margen_s": round(sum(x["sin_margen_s"] for x in sus), 1)})
    return out, pend


def verificar(base: dict, nuevo: dict) -> dict:
    """Cobertura exacta y disjunta; cada tarea nueva ⊆ su original; calendario = tareas ejecutables una vez; dependencias de caché y R1
    ANTERIORES en el calendario y (caché) en la MISMA ronda; suites y rondas dentro de sus límites."""
    P = nuevo["ejecutable"]["parametros"]
    pb = {t["id"]: t for t in base["tareas"]}
    vistas, mot = {}, []
    for t in nuevo["tareas"]:
        o = pb.get(t["origen"]["tarea"])
        if o is None or not set(t["unidades"]) <= set(o["unidades"]) or (t["fase"], t["carril"]) != (o["fase"], o["carril"]):
            mot.append("tarea %s fuera de su original" % t["id"])
        for u in t["unidades"]:
            vistas.setdefault(u, []).append(t["id"])
    pos, ronda = {}, {}
    for r in nuevo["calendario"]:
        for s in r["suites"]:
            for x in s["tareas"]:
                pos[x] = len(pos)
                ronda[x] = r["ronda"]
    fuera = {x["tarea"] for x in nuevo["ejecutable"]["pendientes_de_decision"]}
    ejecutables = [t["id"] for t in nuevo["tareas"] + nuevo["r1"] if t["id"] not in fuera]
    dep_ok = all(d in pos and pos[d] < pos[t["id"]] and (ronda[d] == ronda[t["id"]] or not t.get("cache_caliente")) for t in nuevo["tareas"] + nuevo["r1"]
                 if t["id"] in pos for d in (t.get("depende_de_expandido") or []) if d != "F0")
    return {"cobertura_exacta": set(vistas) == {u for t in base["tareas"] for u in t["unidades"]}, "disjuntas": all(len(v) == 1 for v in vistas.values()),
            "subconjuntos": not mot, "calendario_tareas_ejecutables_una_vez": sorted(pos) == sorted(ejecutables) and len(pos) == len(ejecutables),
            "dependencias_anteriores_y_cache_en_la_misma_ronda": dep_ok,
            "suites_dentro_del_limite": all(s["topes_total_s"] + MARGEN_TERMINACION_S <= P["suite_s"] for r in nuevo["calendario"] for s in r["suites"]),
            "rondas_dentro_del_limite": all(r["union_topes_s"] + MARGEN_TERMINACION_S <= P["ronda_union_s"] for r in nuevo["calendario"]),
            "topes_cubren_el_coste_con_margen": all(t["tope_asignado_s"] >= t["coste"]["con_margen_s"] and t["tope_asignado_s"] <= P["tarea_s"]
                                                    for t in nuevo["tareas"] + nuevo["r1"] if t["id"] in pos),
            "sin_rutas_no_conectadas_ni_con_decision_en_el_calendario": all(t["estado_operativo"]["implementada"] and not t["estado_operativo"]["decision_pendiente"]
                                                                             for t in nuevo["tareas"] + nuevo["r1"] if t["id"] in pos),
            "tareas_dentro_del_tope": all(t["coste"]["con_margen_s"] <= P["tarea_s"] for t in nuevo["tareas"] + nuevo["r1"] if t["id"] in pos),
            "pendientes_fuera_del_calendario": all(x not in pos for x in fuera),
            "motivos": mot[:5]}
