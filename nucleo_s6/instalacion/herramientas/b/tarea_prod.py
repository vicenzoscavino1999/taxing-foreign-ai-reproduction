"""TRABAJADOR de UNA tarea de PRODUCCIÓN del paso 4 (PROD1/PROD2 quiebres; PROD3 Q) — candidato rem56 (P4-P2-COHERENCIA); NO OFICIAL.
rem63: el CÁLCULO por unidad usa los evaluadores R-A ensayados en i2 (herramientas/b/evaluadores_ra.py, especificación «evaluadores_ra» sellada
en el plan), no Run.claim_holds/Run.q_sensitivity; el ensamblaje sigue por Run.breakdown_row, validador_prod y registro_productivo. PROD3 queda
rechazado antes del contexto mientras el plan no selle «decision_q». --hasta-evaluadores: se detiene tras cargar y verificar los módulos R-A.
buscar()/q_ambito() (ruta del núcleo) se conservan solo como referencia de la convención de filas; main ya no los llama.
Lo lanza el EjecutorSupervisado de corrida_paso4 dentro de un cupo, como tarea_paso4/tarea_r1. No añade ciencia: cada unidad es UNA iteración
de paper2b.run.Run.robustness (RB.search / RB.ladder_search con Run.claim_holds y Run.breakdown_row) o de Run.q_sensitivity para UN ámbito,
con los MISMOS argumentos que construye el núcleo (buscar / q_ambito replican literalmente sus ramas; prueba de equivalencia en
pruebas/prod_enlace.py).
  (a) identidades efectivas admitidas (--despliegue-sha256, --fuentes-sha256) como tarea_paso4;
  (b) plan de PRODUCCIÓN (plan_prod.py) verificado por la ruta común; unidades = las de la tarea; cada una con su especificación de la LISTA
      INSTALADA (datos/paso4/lista_PROD.json, sha256 fijado por el plan);
  --hasta-seleccion: se detiene tras (b), ANTES del contexto S6 y de todo cálculo (preflight sin D7);
  (c) contexto S6 UNA vez (seleccion_paso4.configurar/contexto), Run del conjunto de soporte, afirmación por CL.derive, línea base certificada
      del registro autenticado (status verified, robust_infeasible);
  --hasta-contexto: se detiene tras (c), sin evaluar ninguna búsqueda; rem71: su resultado lleva el VÍNCULO efectivo (vinculo(): contexto construido,
      despliegue, fuentes, plan, tarea, evaluadores) + sha256 de los bytes del plan leídos y la asignación recalculada (evidencia del preflight P3);
  (d) [CÁLCULO] una búsqueda/ámbito por unidad -> documento y filas por unidad -> validación productiva (validador_prod.ValidadorProdS6, que
      reutiliza paper2b.rules.Checker) -> registro_productivo.generar_prod -> resultado «completa» solo si el dictamen CUMPLE.
  PROD3 exige el resumen agregado de las unidades de detalle ACEPTADAS fijado por el plan («resumen_q»: archivo y sha256; parte del
  plan_sha256 que cita la autorización): si el plan no lo fija o sus bytes difieren, rechazo antes del contexto.
  python -B herramientas/b/tarea_prod.py --despliegue <d.json> --despliegue-sha256 <h> --plan <plan_prod.json> --tarea <id> --fuentes <f.json>
         --fuentes-sha256 <h> --salida <dir> --resultado <r.json> [--hasta-seleccion | --hasta-contexto]"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import time
from decimal import Decimal
from pathlib import Path

INSTALACION = Path(__file__).resolve().parents[2]
LISTA_REL = "datos/paso4/lista_PROD.json"
KIND_PLAN = "plan-corrida-paso4-produccion-v1"
PI = ("pi_iva", "pi_otros_productos", "pi_produccion")
# (parámetro, bloque) tal como los recorre Run.robustness
BLOQUE = {"eta_w": "incidencia_laboral", "pi_iva": "cuna_tributaria", "pi_otros_productos": "cuna_tributaria", "pi_produccion": "cuna_tributaria",
          "rho": "tecnologia", "a": "tecnologia", "kappa_tilde": "tecnologia"}


def _carga(nombre, rel):
    if nombre not in sys.modules:
        sp = importlib.util.spec_from_file_location(nombre, INSTALACION / rel)
        m = importlib.util.module_from_spec(sp)
        sys.modules[nombre] = m
        sp.loader.exec_module(m)
    return sys.modules[nombre]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def lista_instalada() -> tuple:
    raw = (INSTALACION / LISTA_REL).read_bytes()
    return json.loads(raw), sha(raw)


def especificaciones(plan: dict, t: dict) -> dict:
    """{unidad: especificación} de la LISTA instalada; exige plan de producción, lista fijada por sha256 y unidades conocidas."""
    if plan.get("kind") != KIND_PLAN:
        raise ValueError("PLAN_NO_ES_DE_PRODUCCION")
    lista, h = lista_instalada()
    if (plan.get("lista_prod") or {}).get("sha256") != h:
        raise ValueError("LISTA_DE_PRODUCCION_DISTINTA_DE_LA_INSTALADA")
    por_id = {u["id"]: u for u in lista["unidades"]}
    fuera = [u for u in t["unidades"] if u not in por_id]
    if fuera:
        raise ValueError("UNIDAD_FUERA_DE_LA_LISTA: %s" % fuera[:2])
    if any(por_id[u]["fase"] != t["fase"] for u in t["unidades"]):
        raise ValueError("UNIDAD_DE_OTRA_FASE")
    return {u: por_id[u] for u in t["unidades"]}


def buscar(r, cl, vd, spec, RB, K):
    """UNA iteración de Run.robustness para la búsqueda de la especificación (mismas llamadas y argumentos que el núcleo)."""
    pid, d = spec["parametro"], spec["direccion"]
    s0 = cl.support_sets[0]
    if pid == "eta_H":
        ladders = r.C.F["parameters"]["eta_H"]["sensitivity_ladders"]
        res = RB.ladder_search("incidencia_laboral", "eta_H", ladders,
                               lambda lv: r.claim_holds(cl, vd, {"eta_H": [Decimal(str(x)) for x in lv]}), baseline_status=vd.status)
        return res, "BRK:" + K.H([cl.claim_id, "eta_H", "ladder"])[:40], "eta_H", None
    if pid == "pi_joint":
        lo, hi = (float(x) for x in r.inp.d7.interval(s0, "pi_iva"))
        res = RB.search("cuna_tributaria", None, None, d, lo, hi, "arithmetic",
                        lambda iv: r.claim_holds(cl, vd, {p: iv for p in PI}),
                        ladder=r.cfg.robustness_ladder, bisect_tol=r.cfg.robustness_bisect_tol, baseline_status=vd.status, joint=True)
        return res, "BRK:" + K.H([cl.claim_id, "pi_joint", d])[:40], None, None
    block = BLOQUE[pid]
    comp = cl.eta_w_block if pid == "eta_w" else (pid.split("_", 1)[1] if pid in PI else None)
    lo, hi = (float(x) for x in r.inp.d7.interval(s0, pid))
    scale = r.inp.d7.support(s0, pid)["scale"] or "arithmetic"
    res = RB.search(block, pid, comp if pid.startswith("pi_") or pid == "eta_w" else None, d, lo, hi, scale,
                    lambda iv, pid=pid: r.claim_holds(cl, vd, {pid: iv}), ladder=r.cfg.robustness_ladder,
                    bisect_tol=r.cfg.robustness_bisect_tol, baseline_status=vd.status)
    return res, "BRK:" + K.H([cl.claim_id, pid, d])[:40], pid, comp if pid.startswith("pi_") else None


def q_ambito(r, cl, vd, spec, resumen):
    """Run.q_sensitivity en modo unidades (reduced) restringido al ámbito de la especificación: se ejecuta el método del núcleo y se
    conservan solo las filas del ámbito pedido (las del otro ámbito no se publican en esta unidad)."""
    antes = len(r.rows["external_requirement_sensitivity_result"])
    r.q_sensitivity(cl, vd, reduced=resumen)
    nuevas = r.rows["external_requirement_sensitivity_result"][antes:]
    scope, sc = spec["ambito"]
    return [x for x in nuevas if x["scale_scope"] == scope and (x["scale_country_id"] or None) == sc]


ER_REL = "herramientas/b/evaluadores_ra.py"


def ident_busqueda(cl, spec, K):
    """(breakdown_id, parameter_id de la fila, componente de la fila) con la MISMA convención que buscar() (ruta del núcleo)."""
    pid, d = spec["parametro"], spec["direccion"]
    if pid == "eta_H":
        return "BRK:" + K.H([cl.claim_id, "eta_H", "ladder"])[:40], "eta_H", None
    if pid == "pi_joint":
        return "BRK:" + K.H([cl.claim_id, "pi_joint", d])[:40], None, None
    comp = cl.eta_w_block if pid == "eta_w" else (pid.split("_", 1)[1] if pid in PI else None)
    return "BRK:" + K.H([cl.claim_id, pid, d])[:40], pid, comp if pid.startswith("pi_") else None


def vinculo(ctx, o, plan, t, era, imp):
    """Identidades EFECTIVAS que ligan cada producto (rem63): contexto S6 construido, despliegue y fuentes verificados por sus bytes al admitir
    la tarea, plan, tarea, piezas R-A del plan y módulos efectivamente importados. El encargo de procedencia (identidad del contexto) se
    conserva aparte del ACTO que autoriza la ejecución, que verifica la admisión común (corrida_paso4) y queda en su diario."""
    return {"contexto_identidad_sha256": getattr(ctx, "identity_sha256", None), "encargo_procedencia_sha256": (getattr(ctx, "identity", None) or {}).get("autorizacion_sha256"),
            "despliegue_sha256": o["--despliegue-sha256"], "fuentes_sha256": o["--fuentes-sha256"], "plan_sha256": plan["plan_sha256"], "tarea": t["id"],
            "dependencias_ra_sha256": era["dependencias"]["sha256"], "puerto_ra_sha256": era["puerto"]["sha256"], "adaptador_sha256": era["adaptador"]["sha256"],
            "modulos_ra": sorted(str(x) for x in imp.registro) if imp is not None else [], "decision_q": plan.get("decision_q")}


CAMPOS_VINCULO = ("contexto_identidad_sha256", "despliegue_sha256", "fuentes_sha256", "plan_sha256", "tarea", "dependencias_ra_sha256", "puerto_ra_sha256",
                  "adaptador_sha256", "decision_q")


def vinculo_esperado(v):
    """Campos del vínculo que el validador exige iguales (rem64); en el trabajador salen de SUS identidades verificadas."""
    return {k: v[k] for k in CAMPOS_VINCULO}


def ensamblar_quiebre(sal, u, e, r, cl, vd, bk, ev, ctx, vinc, K, ER, o):
    """Documento y filas de UNA unidad PROD1/PROD2 por la ruta común (Run.breakdown_row del contexto S6) con los testigos del contrato derivados
    de la evidencia R-A (ER.testigos_contrato). Sin valor en la evidencia no se publica testigo: la unidad queda con rechazo técnico."""
    import copy
    CO = _carga("corrida_paso4", "herramientas/b/corrida_paso4.py")
    for tb in ("support_breakdown_result", "witness_sets", "breakdown_witnesses", "external_requirement_sensitivity_result"):
        r.rows[tb] = []
    n = u.replace(":", "_").replace("|", "_")
    doc = {"id": u, "familia": e["familia"], "afirmacion": e["afirmacion"], "especificacion": e, "identidad_productor_sha256": getattr(ctx, "identity_sha256", None),
           "run_class": ctx.identity["run_class"], "origen": "evaluadores_ra", "evaluador": ER.identidad(), "vinculo": vinc,
           "evidencia_ra": json.loads(json.dumps(ev, ensure_ascii=False, default=str))}
    filas = {}
    from paper2b import rules as RU
    if bk is None:
        doc["rechazo_tecnico"] = ("NO_INICIADA_POR_LIMITE_GLOBAL" if ev.get("estado") == "no_iniciada_por_limite_global" else "PREPARACION_FALLIDA: %s" % ev.get("error"))
    elif bk.domain_edge_reached not in RU.EDGES:             # rem64: borde sin causa contractual: pendiente, con su detalle original
        doc["rechazo_tecnico"] = "BORDE_NO_CLASIFICABLE: %s" % str(bk.domain_edge_reached)[:120]
    else:
        try:
            bk2 = copy.copy(bk)
            bk2.witnesses = ER.testigos_contrato(e["familia"], e, bk, None)
            bid, pid_row, comp_row = ident_busqueda(cl, e, K)
            r.breakdown_row(cl, bid, bk2, pid_row, comp_row)
            filas = {tb: list(r.rows[tb]) for tb in ("support_breakdown_result", "witness_sets", "breakdown_witnesses")}
            filas["claims"] = [cl.row(vd.status)]
        except ER.TestigoNoSerializable as x:
            doc["rechazo_tecnico"] = str(x)
    fb = CO.canon(filas) + b"\n"
    (sal / "unidades" / (n + "_filas.json")).write_bytes(fb)
    doc["filas"] = {"archivo": n + "_filas.json", "sha256": sha(fb)}
    (sal / "unidades" / (n + ".json")).write_bytes(CO.canon(doc) + b"\n")
    return {"documento": "unidades/%s.json" % n, "filas": "unidades/%s_filas.json" % n}


def ensamblar_q(sal, u, e, r, cl, vd, ev, ctx, vinc, K, ER, decision):
    """rem64: documento y filas de UNA salida PROD3 (afirmación, ámbito): fila external_requirement_sensitivity_result con los MISMOS campos que
    Run.q_sensitivity, valores de ER.mapear_q (decisión sellada en el plan; sin ella, rechazo técnico) y testigo del contexto que fija m_U."""
    CO = _carga("corrida_paso4", "herramientas/b/corrida_paso4.py")
    VPm = _carga("validador_prod", "herramientas/b/validador_prod.py")
    n = u.replace(":", "_").replace("|", "_")
    doc = {"id": u, "familia": e["familia"], "afirmacion": e["afirmacion"], "especificacion": e, "identidad_productor_sha256": getattr(ctx, "identity_sha256", None),
           "run_class": ctx.identity["run_class"], "origen": "evaluadores_ra", "evaluador": ER.identidad(), "vinculo": vinc,
           "evidencia_ra": json.loads(json.dumps(ev, ensure_ascii=False, default=str))}
    filas = {}
    try:
        scope, sc = e["ambito"]
        fq = ER.mapear_q(decision, e, ev, VPm.identidad_claim(e["afirmacion"]), getattr(getattr(ctx, "inp", None), "dme_gai", None))
        sid = "QSN:" + K.H([cl.claim_id, scope, sc])[:40]
        ws = "WSET:" + sid[4:] if fq["testigo"] else None
        q = dict(fq["fila"])
        filas["external_requirement_sensitivity_result"] = [{
            "sensitivity_id": sid, "run_id": r.run_id, "design_v": cl.design, "instrument_j": cl.instrument_j, "availability_case_id": cl.availability_case_id,
            "bound_variant": cl.bound_variant, "eta_w_block": cl.eta_w_block, "claim_id": cl.claim_id, "scale_scope": scope, "claim_scope": cl.claim_scope,
            "country_id": cl.country_id, "m_Q_critical": q["m_Q_critical"], "reduction_from_reported": q["reduction_from_reported"], "status": q["status"],
            "witness_set_id": ws, "epsilon_econ": "0.01", "external_grid_sha256": r.inp.grid_sha256, "computation_status": q["computation_status"],
            "reason_code": q["reason_code"], "scale_country_id": sc}]
        filas["witness_sets"] = [{"witness_set_id": ws, "scope": "external_requirement",
                                  "definition": "contexto que fija la cota superior mU de m* para %s (%s); identifica el contexto de la cota, no un punto que la alcance" % (
                                      cl.claim_id, scope)}] if ws else []
        filas["breakdown_witnesses"] = [dict(fq["testigo"], witness_set_id=ws, component_index=0, witness_index=0)] if ws else []
        filas["claims"] = [cl.row(vd.status)]
    except ValueError as x:
        doc["rechazo_tecnico"] = str(x)[:300]
        filas = {}
    fb = CO.canon(filas) + b"\n"
    (sal / "unidades" / (n + "_filas.json")).write_bytes(fb)
    doc["filas"] = {"archivo": n + "_filas.json", "sha256": sha(fb)}
    (sal / "unidades" / (n + ".json")).write_bytes(CO.canon(doc) + b"\n")
    return {"documento": "unidades/%s.json" % n, "filas": "unidades/%s_filas.json" % n}


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    o = {k: a[a.index(k) + 1] for k in ("--despliegue", "--despliegue-sha256", "--plan", "--tarea", "--fuentes", "--fuentes-sha256", "--salida", "--resultado", "--replica-arnes",
                                     "--tope-efectivo") if k in a}
    t0 = time.time()
    res_p, sal = Path(o["--resultado"]), Path(o["--salida"])

    info = {}

    def fin(**x):
        x.update({k: v for k, v in info.items() if k not in x})
        x["segundos"] = round(time.time() - t0, 1)
        res_p.write_text(json.dumps(x, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
        return 0

    for k, kh in (("--despliegue", "--despliegue-sha256"), ("--fuentes", "--fuentes-sha256")):
        if not o.get(kh) or sha(Path(o[k]).read_bytes()) != o[kh]:
            return fin(estado="rechazada", motivo="IDENTIDAD_EFECTIVA_DISTINTA_DE_LA_ADMITIDA: %s" % k)
    CO = _carga("corrida_paso4", "herramientas/b/corrida_paso4.py")
    try:
        plan_raw = Path(o["--plan"]).read_bytes()                          # rem71: los MISMOS bytes que se verifican se hashean en la evidencia
        plan = CO.verificar_plan(json.loads(plan_raw))
    except CO.CorridaError as ex:
        return fin(estado="rechazada", motivo="PLAN_NO_VERIFICA: %s" % ex.codigo)
    t = {x["id"]: x for x in plan["tareas"]}.get(o["--tarea"])
    if t is None or t.get("fase") not in ("quiebres", "Q"):
        return fin(estado="rechazada", motivo="TAREA_FUERA_DEL_PLAN_DE_PRODUCCION")
    try:
        esp = especificaciones(plan, t)
    except ValueError as ex:
        return fin(estado="rechazada", motivo=str(ex))
    era = plan.get("evaluadores_ra")                                     # rem63: evaluadores R-A ensayados, por especificación SELLADA en el plan
    if not isinstance(era, dict) or not all(isinstance(era.get(k), dict) and era[k].get("sha256") for k in ("dependencias", "puerto", "adaptador")):
        return fin(estado="rechazada", motivo="PLAN_SIN_EVALUADORES_RA")
    if sha((INSTALACION / ER_REL).read_bytes()) != era["adaptador"]["sha256"]:
        return fin(estado="rechazada", motivo="ADAPTADOR_RA_DISTINTO_DEL_PLAN")
    # rem65 (P4-P2-RELOJ-RA): el reloj del trabajador usa el tope EFECTIVO admitido y supervisado, que el coordinador transporta en el comando
    # (el mismo valor de los límites autorizados y del supervisor); nunca mayor que el de la tarea en el plan. Sin él, o incoherente: rechazo.
    try:
        tope_ef = float(o["--tope-efectivo"])
    except (KeyError, ValueError):
        return fin(estado="rechazada", motivo="TOPE_EFECTIVO_NO_TRANSPORTADO")
    if not float(era["parametros"]["margen_cierre_s"]) < tope_ef <= float(t["tope_s"]):
        return fin(estado="rechazada", motivo="TOPE_EFECTIVO_INCOHERENTE_CON_EL_PLAN: %s frente a %s" % (tope_ef, t["tope_s"]))
    info["tope_efectivo_s"] = tope_ef
    if t["fase"] == "Q" and plan.get("decision_q") is None:          # rem63: el paso del intervalo continuo de Q a la fila contractual está pendiente
        return fin(estado="rechazada", motivo="DECISION_Q_PENDIENTE (PROD3 suspendido antes del contexto; ver paquete de decisiones)")
    if "--hasta-seleccion" in a:
        return fin(estado="incompleta", motivo="DETENIDA_ANTES_DEL_CONTEXTO (PROD: plan, asignación y especificaciones autenticadas; sin contexto ni cálculo)",
                   especificaciones={u: {k: v[k] for k in ("familia", "afirmacion", "parametro", "direccion", "ambito", "motor", "llamada") if k in v} for u, v in esp.items()})
    SP = _carga("seleccion_paso4", "herramientas/b/seleccion_paso4.py")
    RP = _carga("registro_productivo", "herramientas/b/registro_productivo.py")
    VPm = _carga("validador_prod", "herramientas/b/validador_prod.py")
    sys.path.insert(0, str(INSTALACION / "src"))
    from paper2b import claims as CL
    from paper2b import keys as K
    from paper2b import robustness as RB
    SP.configurar(o["--despliegue"])
    a0 = time.time()
    ctx = SP.contexto()
    afirm = sorted({v["afirmacion"] for v in esp.values()})
    lista, _ = lista_instalada()
    reg = lista["fuentes"]["registro"]                                   # registro candidato v4 autenticado (categoría certificada)
    base = {c: CL.Verdict("verified", "robust_infeasible", None, None, 0, None) for c in afirm}   # solo status/verdict los usa la búsqueda
    runs, cls = {}, {}
    derivadas = CL.derive(ctx.inp.registry, ctx.inp.model_case_map, dict(ctx.inp.set_index.items()))   # = Run.claim_sets()
    for c in afirm:
        cl = next((x for x in derivadas if x.claim_id == c), None)
        if cl is None:
            return fin(estado="rechazada", motivo="AFIRMACION_NO_DERIVABLE_BAJO_S6: %s" % c)
        cls[c] = cl
        runs[c] = ctx.run(cl.support_sets[0], "PROD:" + c)
        runs[c].verdicts = {c: base[c]}
    t_ctx = round(time.time() - a0, 1)
    ce = plan.get("contexto_esperado") or {}                         # rem64: el contexto del plan ADMITIDO, antes de cualquier cálculo
    if ce.get("despliegue_sha256") != o["--despliegue-sha256"] or ce.get("identidad_sha256") != getattr(ctx, "identity_sha256", None):
        return fin(estado="rechazada", motivo="CONTEXTO_DISTINTO_DEL_ESPERADO_POR_EL_PLAN", contexto_s=t_ctx)
    if "--hasta-contexto" in a:
        # rem71 (P3-PLAN-PROD): la evidencia del preflight NACE AQUÍ, tras las comprobaciones reales (identidades efectivas, plan verificado, contexto
        # construido e igual al esperado): el MISMO vínculo del trabajador, el sha256 de los bytes del plan leídos y la asignación RECALCULADA.
        asg = sha(CO.canon(list(t["unidades"])))
        if asg != t.get("asignacion_sha256"):
            return fin(estado="rechazada", motivo="ASIGNACION_DISTINTA_DEL_PLAN", contexto_s=t_ctx)
        return fin(estado="incompleta", motivo="DETENIDA_ANTES_DEL_CALCULO (PROD: contexto S6, Run del soporte y afirmaciones derivadas; ninguna búsqueda evaluada)",
                   afirmaciones=afirm, contexto_s=t_ctx, registro_de_la_linea_base=reg, vinculo=vinculo(ctx, o, plan, t, era, None),
                   preflight=dict(plan_archivo_sha256=sha(plan_raw), asignacion_sha256=asg, unidades=list(t["unidades"]), contexto_construido=True))
    ER = _carga("evaluadores_ra", ER_REL)
    M, imp = ER.cargar(ctx, sal / "ra_importaciones", era)              # mismos módulos portados y verificados que el ensayo i2
    vinc = vinculo(ctx, o, plan, t, era, imp)
    if "--hasta-evaluadores" in a:
        return fin(estado="incompleta", motivo="DETENIDA_ANTES_DEL_CALCULO (PROD: contexto S6 y evaluadores R-A cargados y verificados; ninguna búsqueda evaluada)",
                   afirmaciones=afirm, contexto_s=t_ctx, vinculo=vinc, modulos_ra=sorted(imp.registro))
    (sal / "unidades").mkdir(parents=True, exist_ok=True)
    productos, prep, memo, phi_cache = {}, {}, None, {}
    par = era["parametros"]
    limite_global = ER.limite_global_tarea(t0, tope_ef, float(par["margen_cierre_s"]))      # rem64/rem65: reloj GLOBAL con el tope EFECTIVO
    replica = json.loads(Path(o["--replica-arnes"]).read_bytes()) if "--replica-arnes" in o else None  # ARNÉS: resultados registrados de i2
    for u, e in esp.items():                                              # CÁLCULO CIENTÍFICO (solo con autorización)
        r, cl, vd = runs[e["afirmacion"]], cls[e["afirmacion"]], base[e["afirmacion"]]
        if e["familia"] == "PROD3":
            if replica is not None:
                ev = dict((replica.get("afirmaciones") or {}).get(e["afirmacion"]) or {}, afirmacion=e["afirmacion"], origen_evidencia="REPLICA_ARNES")
                if "D_dme_gai" not in ev and "D_dme_gai" in replica:       # rem65: D del MISMO documento registrado (i2 lo guarda en la cabecera)
                    ev["D_dme_gai"] = replica["D_dme_gai"]
            else:
                reg_q = M["QSEN2"].autenticado("demo/registro/registro_candidato_v4.json")["afirmaciones"]
                ev = ER.q_afirmacion(M["QSEN2"], ctx, e["afirmacion"], par["QSEN2"]["tope_s"], phi_cache, reg_q, limite_global)
            imp.guarda()
            productos[u] = ensamblar_q(sal, u, e, r, cl, vd, ev, ctx, vinc, K, ER, plan.get("decision_q"))
            continue
        caso = "EQ" if e["familia"] == "PROD1" else "EQM"
        if replica is not None:
            b = next((x for x in replica.get("busquedas", []) if (x["afirmacion"], x["eje"], x["direccion"]) == (e["afirmacion"], e["parametro"], e["direccion"])), None)
            if b is None:
                return fin(estado="rechazada", motivo="REPLICA_SIN_LA_UNIDAD: %s" % u)
            bk, ev = ER.replica_arnes(M[caso], ctx, e, b, cl)
        else:
            if memo is None:
                memo = M["EQ"].MEMO.Memo(True)
            f = ER.estructural if caso == "EQ" else ER.macro
            bk, ev = f(M[caso], ctx, prep, e["afirmacion"], e["parametro"], e["direccion"], par[caso]["seg_por_evaluacion"], par[caso]["tope_por_busqueda_s"], memo, limite_global)
        imp.guarda()
        productos[u] = ensamblar_quiebre(sal, u, e, r, cl, vd, bk, ev, ctx, vinc, K, ER, o)
    VR = VPm.ValidadorProdS6(ctx, esperado=vinculo_esperado(vinc), modo_arnes=replica is not None)
    import decision_d4 as D4                      # rem66: D4 solo si el plan la sella (desactivada por defecto)
    d4 = t["fase"] == "quiebres" and D4.activa(plan)
    reg = RP.generar_prod(VR, sal, productos, esp, salida=sal / CO.REGISTRO, dictamen=sal / CO.DICTAMEN, d4=d4)
    ok = reg["verificacion"].get("cumple") is True and all(x["estado"] in ("completa_validada", "no_aplicable_validada") or x.get("declarada_D4") for x in reg["unidades"].values())
    return fin(estado="completa" if ok else "rechazada", productos=productos, motivo=None if ok else reg["verificacion"].get("codigos"), contexto_s=t_ctx,
               unidades={x: v["estado"] for x, v in reg["unidades"].items()}, replica_arnes=replica is not None)


if __name__ == "__main__":
    raise SystemExit(main())
