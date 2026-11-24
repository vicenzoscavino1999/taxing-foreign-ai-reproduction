"""REBALANCEO DE TAREAS DEL PLAN (rem42; candidato; NO OFICIAL; sin cálculo). Transformación DETERMINISTA y verificable:
  presupuesto autenticado (lima1857 plan15/presupuesto_lotes.json = plan.presupuesto_sha256) -> plan sellado (construir_plan) ->
  ESPECIFICACIÓN DE PARTICIÓN fijada en la instalación (datos/paso4/rebalanceo_v1.json, sha256 en ESPECIFICACION) -> plan rebalanceado.
Reglas (mismas unidades, ciencia y límites; nunca se parte una UNIDAD, que es el experimento):
  - cada tarea nueva es un subconjunto de UNA tarea original, misma fase y carril; las partes de una tarea son disjuntas y la cubren
    EXACTAMENTE (orden del plan conservado); tareas no partidas quedan idénticas (misma asignación);
  - fronteras intactas: las unidades de una misma frontera van a la misma parte salvo que la frontera sola no quepa (se declara y se
    paga su macro en cada parte);
  - coste por parte con el MODELO del presupuesto (punto 4 del modelo de lima1426/lima1618): contexto por proceso + Σ pared propia de
    las unidades + Σ macro por frontera distinta (memoria del proceso: cada parte la reconstruye) + frío por clave distinta la PRIMERA
    vez que la usa una parte de la tarea (las siguientes partes, consecutivas en el mismo carril, la cargan del almacén de techos en
    disco); cota CONSERVADORA: el frío de una clave se carga a la tarea aunque el plan original lo atribuyera a otra anterior;
  - presupuesto COMPLETO por parte (= rem41): preparación medida de la fase + margen × cálculo + validación (peor de plan15) <= tope;
  - una unidad cuyo presupuesto completo, sola, supera el tope NO CABE: se declara y no se reparte ni se suben topes.
  aplicar(plan, presupuesto, espec, clase_de) -> plan rebalanceado (plan_sha256 nuevo; cada tarea con «origen»); verificar(...) -> informe."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

INSTALACION = Path(__file__).resolve().parents[2]
ESPECIFICACION = ("datos/paso4/rebalanceo_v1.json", "8e15ac607d3a011b8c6ff7a6b34a3c0db8981dcf13585a87974d4f9de887358b")     # sha256 fijado al congelar la especificación (ver fijar())
ESCENARIOS = {"central-rebalanceado-v1": "central", "prudente-rebalanceado-v1": "prudente"}


class RebalanceoError(RuntimeError):
    pass


def need(t, c, d=""):
    if not t:
        raise RebalanceoError("%s: %s" % (c, d) if d else c)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canon(o) -> bytes:
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")


def coste_calculo(presupuesto: dict, escenario: str, unidades: list, pagadas: set | None = None) -> dict:
    """Cálculo (pared, s) de UN proceso con estas unidades según el modelo del presupuesto. `pagadas`: claves ya en el almacén de disco."""
    cu, par = presupuesto["costes_por_unidad"], presupuesto["parametros_registrados"]
    k = "central" if escenario == "central" else "prudente"
    need(all(u in cu for u in unidades), "UNIDAD_SIN_COSTE_REGISTRADO")
    ctx = float(par["contexto_por_proceso_s"][k])
    propia = sum(float(cu[u]["propia_%s_s" % k]) for u in unidades)
    fr, cl = {}, {}
    for u in unidades:
        fr.setdefault(cu[u]["frontera"], float(cu[u]["macro_frontera_%s_s" % k]))
        cl.setdefault(cu[u]["clave"], float(cu[u]["frio_clave_%s_s" % k]))
    pag = pagadas or set()
    carga = max(float(v) for v in par["carga_disco_mediana_s_por_instrumento"].values())
    frio = sum(v for c, v in cl.items() if c not in pag)
    cargas = carga * sum(1 for c in cl if c in pag)
    total = ctx + propia + sum(fr.values()) + frio + cargas
    return {"contexto": ctx, "propia": round(propia, 3), "macro": round(sum(fr.values()), 3), "frio": round(frio, 3), "carga_disco": round(cargas, 3),
            "fronteras": len(fr), "claves": len(cl), "calculo_s": round(total, 1)}


def completo(calc_s: float, prep_s: float, valid_s: float, margen: float) -> float:
    return round(prep_s + margen * calc_s + valid_s, 1)


def particion(plan: dict, presupuesto: dict, param: dict) -> dict:
    """Especificación determinista: para cada tarea R2/R3 cuyo presupuesto COMPLETO (con el cálculo del PLAN) no cabe con margen, partes
    por frontera (primer ajuste decreciente) hasta que cada parte quepa con margen. Devuelve {particiones, no_caben, informe}."""
    esc, tope, mg, val = plan["escenario"], float(param["tope_s"]), float(param["margen"]), float(param["validacion_s"])
    cu = presupuesto["costes_por_unidad"]
    part, no_caben, inf = {}, [], {}
    for t in plan["tareas"]:
        prep = float(param["preparacion_s"][t["fase"]])
        if t.get("requiere_excepcion") or completo(t["pared_s"], prep, val, mg) <= tope:
            continue
        grupos = {}
        for u in t["unidades"]:
            grupos.setdefault(cu[u]["frontera"], []).append(u)
        claves = lambda us: {cu[u]["clave"] for u in us}  # noqa: E731

        def cabe(us, pag):
            return completo(coste_calculo(presupuesto, esc, us, pag)["calculo_s"], prep, val, mg) <= tope
        # empaquetado SECUENCIAL por fronteras en el orden del plan: las partes se ejecutan consecutivas en el carril, así que el frío de
        # una clave lo paga la primera parte que la usa y las siguientes la cargan del almacén de disco (= cómputo de aplicar)
        partes, actual, pag, fronteras_partidas = [], [], set(), []
        for g in grupos.values():
            if cabe(actual + g, pag):
                actual += g
                continue
            if actual:
                partes.append(actual)
                pag |= claves(actual)
                actual = []
            if cabe(g, pag):
                actual = list(g)
                continue
            fronteras_partidas.append(cu[g[0]]["frontera"])     # la frontera sola no cabe: se reparte por unidades (macro en cada parte)
            for u in g:
                if cabe(actual + [u], pag):
                    actual.append(u)
                    continue
                if actual:
                    partes.append(actual)
                    pag |= claves(actual)
                    actual = []
                if cabe([u], pag):
                    actual = [u]
                else:                                              # la UNIDAD sola no cabe: no se parte ni se suben topes
                    no_caben.append(u)
                    partes.append([u])
                    pag |= claves([u])
        if actual:
            partes.append(actual)
        partes = [[u for u in t["unidades"] if u in set(p)] for p in partes]      # orden del plan DENTRO de cada parte; partes en orden de ejecución
        part[t["id"]] = partes
        inf[t["id"]] = {"partes": len(partes), "fronteras_partidas": fronteras_partidas}
    return {"particiones": part, "no_caben": sorted(no_caben), "informe": inf}


def aplicar(plan: dict, presupuesto: dict, espec: dict, clase_de) -> dict:
    """Plan rebalanceado desde el plan sellado y la especificación. Verifica exactitud, disjunción, subconjunto, fase/carril y cabida."""
    need(espec.get("plan_base_sha256") == plan["plan_sha256"], "REBALANCEO_DE_OTRO_PLAN")
    need(espec.get("presupuesto_sha256") == plan["presupuesto_sha256"], "REBALANCEO_DE_OTRO_PRESUPUESTO")
    param, esc = espec["parametros"], plan["escenario"]
    por = {t["id"]: t for t in plan["tareas"]}
    need(set(espec["particiones"]) <= set(por), "PARTICION_DE_TAREA_INEXISTENTE")
    tareas, sust = [], {}
    for t in plan["tareas"]:
        ps = espec["particiones"].get(t["id"])
        if ps is None:
            tareas.append(dict(t, origen={"tarea": t["id"], "asignacion_sha256": t["asignacion_sha256"], "parte": None}))
            sust[t["id"]] = [t["id"]]
            continue
        planos = [u for p in ps for u in p]
        need(all(p for p in ps) and len(planos) == len(set(planos)) and sorted(planos) == sorted(t["unidades"]), "PARTICION_NO_EXACTA", t["id"])
        prep, pagadas, ids = float(param["preparacion_s"][t["fase"]]), set(), []
        for i, p in enumerate(ps, 1):
            us = [u for u in t["unidades"] if u in set(p)]
            need(us == list(p), "PARTE_FUERA_DE_ORDEN", "%s.p%d" % (t["id"], i))
            c = coste_calculo(presupuesto, esc, us, pagadas)
            pagadas |= {presupuesto["costes_por_unidad"][u]["clave"] for u in us}
            tot = completo(c["calculo_s"], prep, float(param["validacion_s"]), float(param["margen"]))
            nc = len(us) == 1 and us[0] in espec.get("no_caben", [])
            need(tot <= float(param["tope_s"]) or nc, "PARTE_NO_CABE", "%s.p%d %.1f" % (t["id"], i, tot))
            nid = "%s.p%d" % (t["id"], i)
            clases = {}
            for u in us:
                c_ = clase_de(u)
                clases[c_] = clases.get(c_, 0) + 1
            tareas.append({"id": nid, "fase": t["fase"], "carril": t["carril"], "unidades": us, "asignacion_sha256": sha(canon(us)), "pared_s": c["calculo_s"],
                           "cpu_s": None, "requiere_excepcion": bool(nc), "clases": clases, "coste_modelo": c,
                           "presupuesto_completo_s": tot, "origen": {"tarea": t["id"], "asignacion_sha256": t["asignacion_sha256"], "parte": i}})
            ids.append(nid)
        sust[t["id"]] = ids
    cal = [dict(r, carriles=[[[y for x in g for y in sust.get(x, [x])] for g in c] for c in r["carriles"]]) for r in plan["calendario"]]
    cuerpo = {k: v for k, v in plan.items() if k not in ("plan_sha256", "anexo_comandos")}
    cuerpo.update(kind="plan-corrida-paso4-rebalanceado-v1", escenario="%s-rebalanceado-v1" % esc, tareas=tareas, calendario=cal,
                  rebalanceo={"plan_base_sha256": plan["plan_sha256"], "especificacion_sha256": sha(canon(espec)), "sustituciones": {k: v for k, v in sust.items() if v != [k]},
                              "no_caben": espec.get("no_caben", []), "parametros": param})
    cuerpo["resumen"] = dict(plan["resumen"], tareas_R2=sum(t["fase"] == "R2" for t in tareas), tareas_R3=sum(t["fase"] == "R3" for t in tareas))
    return dict(cuerpo, plan_sha256=sha(canon(cuerpo)))


def verificar(base: dict, nuevo: dict) -> dict:
    """Cobertura exacta y disjunta, cada tarea nueva ⊆ su original (misma fase y carril), R1 intacto, calendario: cada tarea una vez."""
    pb = {t["id"]: t for t in base["tareas"]}
    vistas = {}
    mot = []
    for t in nuevo["tareas"]:
        o = pb.get(t["origen"]["tarea"])
        if o is None or not set(t["unidades"]) <= set(o["unidades"]) or (t["fase"], t["carril"]) != (o["fase"], o["carril"]):
            mot.append("tarea %s fuera de su original" % t["id"])
        for u in t["unidades"]:
            vistas.setdefault(u, []).append(t["id"])
    dup = [u for u, v in vistas.items() if len(v) > 1]
    todas = {u for t in base["tareas"] for u in t["unidades"]}
    en_cal = [x for r in nuevo["calendario"] for c in r["carriles"] for g in c for x in g]
    ids = [t["id"] for t in nuevo["tareas"]] + [t["id"] for t in nuevo["r1"]]
    return {"cobertura_exacta": set(vistas) == todas, "disjuntas": not dup, "subconjuntos": not mot, "r1_intacto": nuevo["r1"] == base["r1"],
            "calendario_cada_tarea_una_vez": sorted(en_cal) == sorted(ids), "motivos": mot[:5] + ["duplicadas: %d" % len(dup)] * bool(dup)}
