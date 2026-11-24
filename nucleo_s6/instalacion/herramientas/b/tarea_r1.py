"""TRABAJADOR de UNA tarea R1 del plan (candidato S6; NO OFICIAL), lanzado por el EjecutorSupervisado dentro de un cupo (mismas
identidades efectivas que tarea_paso4: --despliegue-sha256, --fuentes-sha256). rem43: CONECTADO BAJO S6 mediante el adaptador r1_s6.
  entrada sellada (plan + tarea + cobertura_r1 autenticada de lima1857 con sus ids) -> referencias históricas autenticadas ->
  ContextoS6 de la corrida (seleccion_paso4.contexto, el MISMO de R2/R3) -> pila histórica del método v5 con el NÚCLEO S6 (r1_s6.PilaR1S6:
  bytes de lima1351 autenticados + sustituciones registradas; guarda contra el paper2b aislado) -> PREFLIGHT sin cálculo (registro v4 =
  afirmaciones S6, dependencias derivadas, cierre y rutas de la muestra, productor cargado) + PLAN del orquestador regenerado bajo S6 y
  comparado con el histórico (plan_1728) -> [CÁLCULO, solo con autorización] productor -> verificación/comparación histórica del
  orquestador -> registro R1 (registro_productivo.generar_r1) -> coordinador.
  Ruta de CÁLCULO conectada: R1-C1..C6 (ci-df, método v5 del orquestador: ejecutar + verificar). Las demás tareas R1 (A*, B*, D, F, V)
  quedan conectadas hasta el PREFLIGHT; su cálculo devuelve «rechazada» con la brecha EXACTA de su punto de entrada (RUTA_CALCULO_R1).
  --hasta-seleccion: se detiene tras el preflight (sin productos). Quiebres y Q (producción inicial) no son tareas del plan; D4/E16 aparte.
  rem49: OPCIONES candidatas conectadas y DESACTIVADAS salvo que la autorización reconstruida las declare (opciones_p1.opciones_autorizadas):
  B3 y A3 -> validación inicial de la opción (registro_productivo.generar_r1_opcion; igualdad en su comparación, comparar_tarea -> comparar_r1);
  A1/A2 -> ruta_intercambio (SRED propio de A1 + opciones_p1.intercambio_aceptado). Sin declaración: ruta vigente (bloqueada por sus observaciones).
  rem51 (P4-R1-V-REGISTRO-GLOBAL): R1-V valida el CIERRE de sus dependencias del plan (D, F y, por D, A*, B*, C*) con la procedencia de la ruta
  común y lo registra registro_productivo.generar_r1_global (fuentes ligadas; nunca la ruta por comando); su referencia es la cobertura R1
  autenticada completa; R1-D registra en su árbol las fuentes que consumió (enlace D -> V).
  rem52: también las fuentes de esta corrida se ligan con su autoridad reconstruida (corrida_paso4.procedencia_vigente).
  python -B herramientas/b/tarea_r1.py --despliegue <d> --despliegue-sha256 <h> --plan <p> --tarea <R1-…> --fuentes <f> --fuentes-sha256 <h>
         --salida <dir> --resultado <r.json> [--tope <s>] [--hasta-seleccion]"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path

INSTALACION = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(INSTALACION / "herramientas/b"))

COBERTURA = ("validacion_evidencia_comparador_paso4_3_7_2026-10-12_lima1857", "369beaa07cc56fffc966112b6d1faaebac60d072529dc299e761eebf523bca42",
             "demo/plan15/cobertura_r1.json")
P1351 = "p0_completo_h4_paso4_3_7_2026-10-09_lima1351"
PRODUCTORES = {      # tarea R1 -> productor histórico (lima1351 codigo/; el plan de cobertura cita la referencia de cada tarea)
    "R1-A1": ["codigo/c2_extremos.py"], "R1-A2": ["codigo/c2_extremos.py"],
    "R1-A3-G-U": ["codigo/certificar_inf_df.py"], "R1-A3-N-U": ["codigo/certificar_inf_df.py"],
    "R1-A3-G-L": ["codigo/inf_df_bb_v3.py", "codigo/cota_un_umbral_v2.py"], "R1-A3-N-L": ["codigo/inf_df_bb_v3.py", "codigo/cota_un_umbral_v2.py"],
    "R1-B1": ["codigo/orquestador_b.py", "codigo/extremos_G.py"], "R1-B2": ["codigo/orquestador_b.py", "codigo/extremos_G.py"],
    "R1-B3": ["codigo/orquestador_b.py", "codigo/extremos_dfd.py"],
    **{"R1-C%d" % i: ["codigo/orquestador_b.py", "codigo/extremos_G_df_v5.py"] for i in range(1, 7)},
    "R1-D": ["codigo/orquestador_b.py"], "R1-F": ["codigo/sensibilidad_q.py"], "R1-V": ["codigo/orquestador_b.py"]}


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    o = {k: a[a.index(k) + 1] for k in ("--despliegue", "--despliegue-sha256", "--plan", "--tarea", "--fuentes", "--fuentes-sha256", "--salida", "--resultado", "--tope",
                                        "--raiz-corrida", "--corridas-previas") if k in a}
    t0 = time.time()
    res_p = Path(o["--resultado"])
    sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731

    def fin(**x):
        x["segundos"] = round(time.time() - t0, 1)
        res_p.write_text(json.dumps(x, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
        return 0

    for k, kh in (("--despliegue", "--despliegue-sha256"), ("--fuentes", "--fuentes-sha256")):
        if not o.get(kh) or sha(Path(o[k]).read_bytes()) != o[kh]:
            return fin(estado="rechazada", motivo="IDENTIDAD_EFECTIVA_DISTINTA_DE_LA_ADMITIDA: %s" % k)
    plan = json.loads(Path(o["--plan"]).read_bytes())
    t = {x["id"]: x for x in plan["r1"]}.get(o["--tarea"])
    if t is None:
        return fin(estado="rechazada", motivo="TAREA_R1_FUERA_DEL_PLAN")
    d = json.loads(Path(o["--despliegue"]).read_bytes())
    T = Path(d["raiz_fuentes"])
    ent, h, rel = COBERTURA
    inv_raw = (T / ent / "audit/entrega.json").read_bytes()
    if sha(inv_raw) != h:
        return fin(estado="rechazada", motivo="COBERTURA_R1_NO_AUTENTICADA")
    iv = json.loads(inv_raw)["files"]
    cr_raw = (T / ent / rel).read_bytes()
    if (iv[rel]["sha256"] if isinstance(iv[rel], dict) else iv[rel]) != sha(cr_raw):
        return fin(estado="rechazada", motivo="COBERTURA_R1_NO_AUTENTICADA")
    cob = {x["tarea"]: x for x in json.loads(cr_raw)["tareas"]}
    refs = {k: v for k, v in cob.items() if k == t["id"] or k.startswith(t["id"] + "-")}
    autent = {}
    for k, v in refs.items():
        c = (v.get("referencia") or {}).get("cita")
        if not c:
            autent[k] = {"referencia": None, "nota": v.get("nota")}
            continue
        ir = (T / c["entrega"] / "audit/entrega.json").read_bytes()
        ivr = json.loads(ir)["files"]
        fb = (T / c["entrega"] / c["archivo"]).read_bytes()
        ok = sha(ir) == c["inventario_sha256"] and sha(fb) == c["sha256"] and (ivr[c["archivo"]]["sha256"] if isinstance(ivr[c["archivo"]], dict) else ivr[c["archivo"]]) == c["sha256"]
        autent[k] = {"referencia": c, "autenticada": ok}
    if t["id"] in VALIDACION_GLOBAL and not refs:                         # rem51: R1-V no tiene ids propios; su referencia es la cobertura
        autent[t["id"]] = {"referencia": {"entrega": ent, "inventario_sha256": h, "archivo": rel, "sha256": sha(cr_raw)}, "autenticada": True,
                           "nota": "validación global: su referencia es la cobertura R1 autenticada completa (las tareas que valida)"}
    elif not refs or not all(x.get("autenticada", True) for x in autent.values()):
        return fin(estado="rechazada", motivo="REFERENCIA_R1_NO_AUTENTICADA", referencias=autent)
    prods = {}
    i1351 = json.loads((T / P1351 / "audit/entrega.json").read_bytes())["files"]
    for p in PRODUCTORES.get(t["id"], []):
        b = (T / P1351 / p).read_bytes()
        prods[p] = {"sha256": sha(b), "autenticado_por_inventario": (i1351[p]["sha256"] if isinstance(i1351.get(p), dict) else i1351.get(p)) == sha(b)}
    info = {"tarea": t["id"], "contenido": t.get("contenido"), "depende_de": t.get("depende_de_expandido"), "referencias": autent, "productor_historico": {"entrega": P1351,
            "archivos": prods}}
    # ---- rem43: contexto S6 de la corrida y pila histórica con el núcleo S6 (adaptador r1_s6)
    SP = _carga("seleccion_paso4", "herramientas/b/seleccion_paso4.py")
    RS = _carga("r1_s6", "herramientas/b/r1_s6.py")
    dd = SP.configurar(o["--despliegue"])
    a0 = time.time()
    ctx = SP.contexto()
    t_ctx = round(time.time() - a0, 1)
    ids = [x for v in refs.values() for x in (v.get("ids") or [])]
    sal = Path(o["--salida"])
    sal.mkdir(parents=True, exist_ok=True)
    try:
        P = RS.PilaR1S6(ctx, dd)
        pre = P.preflight(t["id"], ids)
        (sal / "paquete").mkdir(parents=True, exist_ok=True)
        plan_s6 = sal / "paquete" / "plan_orquestador_s6.json"
        P.OB.plan(str(plan_s6))                                           # orquestador_b.plan: SIN cálculo (dependencias y cierre de las 1728)
        rel_p = "demo/orquestador3/plan_1728_v3.json"                    # plan del orquestador FINAL de lima1351 (posterior a su código final)
        hraw = (T / P1351 / rel_p).read_bytes()
        if (i1351[rel_p]["sha256"] if isinstance(i1351[rel_p], dict) else i1351[rel_p]) != sha(hraw):
            return fin(estado="rechazada", motivo="PLAN_HISTORICO_NO_AUTENTICADO", **info)
        hist = json.loads(hraw)["filas"]
        nuevo = json.loads(plan_s6.read_bytes())["filas"]
        clave = lambda f: (f["afirmacion"], f["ruta"], tuple(f["dependencias"]))  # noqa: E731
        pre["plan_orquestador_s6"] = {"sha256": sha(plan_s6.read_bytes()), "filas": len(nuevo), "igual_al_historico_en_afirmaciones_rutas_y_dependencias":
                                      sorted(map(clave, nuevo)) == sorted(map(clave, hist))}
    except Exception as ex:  # noqa: BLE001  (RutaNoSoportada, R1S6Error, ContextoError...: rechazo ANTES del cálculo)
        return fin(estado="rechazada", motivo="PREFLIGHT_R1_S6: %s: %s" % (type(ex).__name__, str(ex)[:300]), contexto_s=t_ctx, **info)
    info.update(preflight={k: v for k, v in pre.items() if k != "afirmaciones_muestra"}, afirmaciones_muestra_sha256=sha(json.dumps(pre.get("afirmaciones_muestra") or []).encode()), nucleos=RS.comparar_nucleos(T), contexto_s=t_ctx, identidad_contexto_sha256=getattr(ctx, "identity_sha256", None))
    if not pre["plan_orquestador_s6"]["igual_al_historico_en_afirmaciones_rutas_y_dependencias"]:
        return fin(estado="rechazada", motivo="PLAN_ORQUESTADOR_S6_DISTINTO_DEL_HISTORICO", **info)
    RR = _carga("r1_rutas", "herramientas/b/r1_rutas.py")
    plan_ruta = None
    if t["id"] in RUTAS_POR_COMANDO:                                      # rem44: rutas por COMANDO HISTÓRICO (A*, B*, F)
        try:
            plan_ruta = RR.derivar(t["id"], T)
            # rem50 (P4-R1-ARTEFACTO-PREFLIGHT): el plan del orquestador que ESTE preflight escribió en el paquete se DECLARA con su sha256; la
            # validación común lo comprueba (bytes y contenido frente al histórico autenticado) y lo liga al registro (plan_ruta_sha256)
            plan_ruta["artefactos_del_trabajador"] = {RR.ARTEFACTO_PREFLIGHT: pre["plan_orquestador_s6"]["sha256"]}
            info["ruta"] = {"comandos": [{k: c[k] for k in ("entrega", "registro", "registro_sha256", "modulo", "argv")} for c in plan_ruta["comandos"]],
                            "ids": len(plan_ruta["ids"]), "observaciones": plan_ruta["observaciones"], "importados": preflight_comandos(RR, RS, plan_ruta, T, ctx)}
        except Exception as ex:  # noqa: BLE001
            return fin(estado="rechazada", motivo="PREFLIGHT_RUTA_R1: %s: %s" % (type(ex).__name__, str(ex)[:300]), **info)
    opcion = None
    if plan_ruta is not None:                                             # rem49: OPCIÓN candidata SOLO si la autorización reconstruida la declara
        OPm = _carga("opciones_p1", "herramientas/b/opciones_p1.py")
        activas, info["opciones"] = OPm.opciones_autorizadas(plan, o.get("--raiz-corrida"), t, "--modo-arnes" in a)
        opcion = next(iter(activas), None)
    if "--hasta-seleccion" in a:
        return fin(estado="incompleta", motivo="DETENIDA_ANTES_DEL_CALCULO (R1: preflight bajo S6 conectado; sin productos)", **info)
    if plan_ruta is not None:                                             # ---- CÁLCULO (solo con autorización): comandos históricos bajo S6
        RP = _carga("registro_productivo", "herramientas/b/registro_productivo.py")
        if opcion == "A1A2_INTERCAMBIO_DE_TESTIGOS":                     # rem49: intercambio auténtico en lugar de los comandos vigentes
            info["artefactos_del_trabajador"] = plan_ruta["artefactos_del_trabajador"]       # rem50: el SRED de A1 comparte paquete con el preflight
            return fin(**ruta_intercambio(OPm, RR, RS, RP, P, ctx, plan, t, T, sal, o, a, info))
        acept = productos_aceptados(a, o, plan, t, T, procedencia=info.setdefault("dependencias_consumidas", {}))
        dep = plan_ruta.get("entrada_de_dependencia")
        archivos = {}
        if dep:
            d0 = acept.get(dep["tarea"])
            if d0 is None:
                return fin(estado="rechazada", motivo="DEPENDENCIA_NO_ACEPTADA: %s" % dep["tarea"], **info)
            sal_dep = json.loads((d0 / "r1_productos.json").read_bytes())
            archivos[dep["tarea"]] = d0 / "paquete" / sorted(sal_dep["archivos"])[0]
        (sal / "paquete").mkdir(parents=True, exist_ok=True)
        rcs, info["ejecucion_comandos"] = ejecutar_ruta(RR, RS, plan_ruta, T, sal / "paquete", archivos, ctx)
        if opcion in ("B3_VALIDEZ_Y_COMPARACION", "A3_CRITERIO_GLOBAL"):  # rem49: validación INICIAL de la opción; la igualdad, en su comparación
            ev = dict(OPm.validacion_inicial(opcion, plan_ruta, T, sal / "paquete", rcs), autorizacion=info["opciones"])
            reg = RP.generar_r1_opcion(P, sal, t["id"], ev, salida=sal / "registro_productivo.json", dictamen=sal / "dictamen_validacion.json")
            ok = reg["verificacion"]["cumple"] is True
            return fin(estado="completa" if ok else "rechazada", productos={"R1:" + t["id"]: {"documento": "r1_productos.json", "filas": "validacion_opcion.json"}},
                       motivo=None if ok else reg["verificacion"]["codigos"], **info)
        reg = RP.generar_r1_ruta(P, sal, t["id"], plan_ruta, rcs, salida=sal / "registro_productivo.json", dictamen=sal / "dictamen_validacion.json")
        ok = reg["verificacion"]["cumple"] is True
        return fin(estado="completa" if ok else "rechazada", productos={"R1:" + t["id"]: {"documento": "r1_productos.json", "filas": "validacion_ruta.json"}},
                   motivo=None if ok else reg["verificacion"]["codigos"], **info)
    if t["id"] not in RUTA_CALCULO_R1 + ("R1-D", "R1-V"):
        return fin(estado="rechazada", motivo="R1_SIN_RUTA_DE_CALCULO_BAJO_S6: %s" % BRECHA_R1.get(t["id"], "sin punto de entrada"), **info)
    if t["id"] == "R1-V":                                                 # validación global sobre los registros ACEPTADOS
        # rem51 (P4-R1-V-REGISTRO-GLOBAL): las fuentes son el CIERRE de las dependencias del PLAN (R1-V -> R1-D, R1-F; R1-D -> A*, B*, C*),
        # cada una con la procedencia de la ruta común; las registra y valida registro_productivo.generar_r1_global (nunca la ruta por comando)
        cierre = cierre_dependencias(plan, t)
        acept = productos_aceptados(a, o, plan, dict(t, depende_de_expandido=cierre), T, procedencia=info.setdefault("dependencias_consumidas", {}))
        # rem52: las fuentes de ESTA corrida también con su autoridad RECONSTRUIDA por la ruta común (corrida_paso4.procedencia_vigente), para
        # ligarlas completas (autorización, acto, modo); una que no se reconstruye exactamente igual no se consume
        CO = _carga("corrida_paso4", "herramientas/b/corrida_paso4.py")
        locales = sorted(x for x in acept if info["dependencias_consumidas"][x].get("origen") == "esta_corrida")
        if locales:
            modo = "--modo-arnes" in a
            ef = CO.identidades_efectivas(o["--despliegue"], {"fuentes_v2": o["--fuentes"]}, {"tope_s": float(o.get("--tope", 2400.0)), "procesos": CO.CARRILES}, modo)
            inf = []
            rec = CO.procedencia_vigente(plan, Path(o["--raiz-corrida"]), locales, ef, modo, inf)
            for x in locales:
                p0, p = info["dependencias_consumidas"][x], rec.get(x)
                if p is None or (p["salida"], p["arbol_sha256"], p["identidad_sha256"]) != (p0["salida"], p0["arbol_sha256"], p0["identidad_sha256"]):
                    acept.pop(x)
                    info["dependencias_consumidas"][x] = dict(p0, rechazo="AUTORIDAD_DE_LA_CORRIDA_NO_RECONSTRUIDA", informe=[e for e in inf if e.get("tarea") == x])
                else:
                    info["dependencias_consumidas"][x] = dict(p, origen="esta_corrida")
        RP = _carga("registro_productivo", "herramientas/b/registro_productivo.py")
        por_id = {x["id"]: x for x in plan["r1"]}
        reg = RP.generar_r1_global(P, sal, t["id"], {x: info["dependencias_consumidas"][x] for x in acept}, cierre,
                                   consumos={x: [d_ for d_ in por_id[x].get("depende_de_expandido") or [] if d_ != "F0"] for x in CONSUMO_REGISTRADO if x in cierre},
                                   artefactos={RR.ARTEFACTO_PREFLIGHT: pre["plan_orquestador_s6"]["sha256"]}, salida=sal / "registro_productivo.json",
                                   dictamen=sal / "dictamen_validacion.json")
        ok = reg["verificacion"]["cumple"] is True
        return fin(estado="completa" if ok else "rechazada", productos={"R1:R1-V": {"documento": "r1_productos.json", "filas": "validacion_global.json"}},
                   motivo=None if ok else reg["verificacion"]["codigos"], **info)
    # ---- CÁLCULO CIENTÍFICO (solo tras la admisión del coordinador con autorización): método v5 del orquestador con el ContextoS6
    RP = _carga("registro_productivo", "herramientas/b/registro_productivo.py")
    muestra = sal / "paquete" / "muestra.json"
    muestra.write_bytes(json.dumps({"afirmaciones": pre["afirmaciones_muestra"]}, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    tope = float(o.get("--tope", 2400.0))
    evid_d = None
    if t["id"] == "R1-D":                                                 # rem44: INTERCAMBIO de productos ACEPTADOS (nunca hojas recalculadas)
        acept = productos_aceptados(a, o, plan, t, T, procedencia=info.setdefault("dependencias_consumidas", {}))
        (sal / "paquete/dependencias_consumidas.json").write_bytes(RP.canon({x: info["dependencias_consumidas"][x] for x in sorted(acept)}) + b"\n")   # rem51: enlace D -> V
        deps_plan = {f["afirmacion"]: f["dependencias"] for f in json.loads(plan_s6.read_bytes())["filas"]}
        hojas, fuentes = hojas_y_fuentes_de(P, pre["afirmaciones_muestra"], acept, deps_plan)
        evid_d = P.intercambio(sal / "paquete" / "corrida", hojas, fuentes, set(hojas))
    rc = P.producir(sal / "paquete" / "corrida", muestra, ["--tope-afirmacion", "300", "--tope-proceso", str(max(60.0, tope - 300.0))])
    if evid_d is not None and not P.hojas_intactas(sal / "paquete" / "corrida", evid_d, hojas):
        return fin(estado="rechazada", motivo="HOJAS_ACEPTADAS_ALTERADAS_O_RECALCULADAS", **info)
    rel_h = "demo/e13v4b/hojas_ci_v2.json"                               # hojas E13 v4 CENSO-v2 (filas) de lima1351, autenticadas
    hojas = T / P1351 / rel_h
    if (i1351[rel_h]["sha256"] if isinstance(i1351[rel_h], dict) else i1351[rel_h]) != sha(hojas.read_bytes()):
        return fin(estado="rechazada", motivo="HOJAS_HISTORICAS_NO_AUTENTICADAS", **info)
    P.verificar(sal / "paquete" / "corrida", hojas, plan_s6, sal / "verificacion.json")
    reg = RP.generar_r1(P, sal, t["id"], "paquete/corrida", "verificacion.json", salida=sal / "registro_productivo.json", dictamen=sal / "dictamen_validacion.json", rc_productor=rc)
    ok = reg["verificacion"].get("cumple") is True
    return fin(estado="completa" if ok else "rechazada", productos={"R1:" + t["id"]: {"documento": reg["unidades"]["R1:" + t["id"]]["documento"],
                                                                                      "filas": "verificacion.json"}},
               motivo=None if ok else reg["verificacion"].get("codigos"), **info)


def _carga(nombre, rel):
    if nombre not in sys.modules:
        sp = importlib.util.spec_from_file_location(nombre, INSTALACION / rel)
        m = importlib.util.module_from_spec(sp)
        sys.modules[nombre] = m
        sp.loader.exec_module(m)
    return sys.modules[nombre]


RUTA_CALCULO_R1 = tuple("R1-C%d" % i for i in range(1, 7))
VALIDACION_GLOBAL = ("R1-V",)            # rem51: tarea R1 sin ids propios en la cobertura (valida la cobertura completa)
CONSUMO_REGISTRADO = ("R1-D",)          # rem51: tareas que registran en su árbol aceptado las fuentes que consumieron (enlace D -> V)


def cierre_dependencias(plan, t) -> list:
    """rem51: CIERRE de las dependencias de la tarea en el plan sellado (depende_de_expandido, sin F0), ordenado."""
    por_id = {x["id"]: x for x in plan["tareas"] + plan["r1"]}
    out, pend = set(), [d_ for d_ in t.get("depende_de_expandido") or [] if d_ != "F0"]
    while pend:
        x = pend.pop()
        if x not in out:
            out.add(x)
            pend += [d_ for d_ in (por_id.get(x) or {}).get("depende_de_expandido") or [] if d_ != "F0"]
    return sorted(out)
RUTAS_POR_COMANDO = ("R1-A1", "R1-A2", "R1-A3-G-U", "R1-A3-N-U", "R1-A3-G-L", "R1-A3-N-L", "R1-B1", "R1-B2", "R1-B3", "R1-F")


def desinstalar(imp):
    """Quita la pila de UNA entrega (paquete «codigo») para cargar la de la siguiente en el mismo proceso; el núcleo S6 se conserva."""
    for k in [k for k in sys.modules if k == "codigo" or k.startswith("codigo.")]:
        sys.modules.pop(k)
    if imp in sys.meta_path:
        sys.meta_path.remove(imp)


def ejecutar_ruta(RR, RS, plan_ruta, T, paquete, archivos, ctx):
    """rem45 (P4-R1-ENTRADA-COMANDO): secuencia REAL de las rutas por comando (la que usa main): copia de entradas (preparar) y, por comando,
    importador de SU entrega (bytes autenticados, sustituciones, núcleo S6, ContextoS6) -> ejecutar_comando (runpy -m con argv y cwd del
    paquete) -> limpieza entre entregas (desinstalar antes y después). Devuelve (códigos, registro de cada importador y sus errores)."""
    argvs = RR.preparar(plan_ruta, T, paquete, archivos)
    rcs, regs = {}, {}
    for n, c in enumerate(plan_ruta["comandos"]):
        imp = RR.ImportadorEntrega(T, c["entrega"], RS.NUCLEO_S6, ctx)
        desinstalar(imp)
        try:
            rcs[n] = RR.ejecutar_comando(c, argvs[n], paquete, imp)
        finally:
            regs[n] = {"modulo": c["modulo"], "entrega": c["entrega"], "rc": rcs.get(n), "modulos": sorted(imp.registro), "errores": list(imp.errores),
                       "sustituciones": sorted({x["original"][:60] for v in imp.registro.values() for x in v["sustituciones"]})}
            desinstalar(imp)
    return rcs, regs


def ruta_intercambio(OPm, RR, RS, RP, P, ctx, plan, t, T, sal, o, a, info):
    """rem49 (P4-A1A2-VINCULO): R1-A1/A2 con la opción A1/A2 ACTIVA. A1 genera SU SRED-G/N (comandos autenticados de opciones_p1.plan_sred,
    importador por entrega con el núcleo S6 y el ContextoS6 de la corrida); después la ENTRADA DE LA CADENA opciones_p1.intercambio_aceptado
    reconstruye la aceptación de R1-B3 (esta corrida y --corridas-previas), lee sus bytes verificados, liga el SRED propio a su generación y
    validación y hace la correspondencia exacta. A2 no ejecuta productor. El registro sale de registro_productivo.generar_r1_opcion; la
    aceptación FINAL de la tarea la hace el coordinador sobre su árbol."""
    paquete = sal / "paquete"
    paquete.mkdir(parents=True, exist_ok=True)
    ejec = None
    if t["id"] == "R1-A1":
        rcs, regs = ejecutar_ruta(RR, RS, OPm.plan_sred(T), T, paquete, {}, ctx)
        info["ejecucion_comandos"], ejec = regs, (rcs, regs)
    CO = _carga("corrida_paso4", "herramientas/b/corrida_paso4.py")
    modo = "--modo-arnes" in a
    ef = CO.identidades_efectivas(o["--despliegue"], {"fuentes_v2": o["--fuentes"]}, {"tope_s": float(o.get("--tope", 2400.0)), "procesos": CO.CARRILES}, modo)
    raices = [p for p in [o.get("--raiz-corrida", "")] + o.get("--corridas-previas", "").split(",") if p]
    x = OPm.intercambio_aceptado(plan, raices, ef, modo, t["id"], T, paquete if ejec else None, ejec, artefactos=info.get("artefactos_del_trabajador"))
    (paquete / ("intercambio_%s.json" % t["id"])).write_bytes(json.dumps(x, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8"))
    ev = {"opcion": "A1A2_INTERCAMBIO_DE_TESTIGOS", "cumple": bool(x["aceptable"]),
          "codigos": [] if x["aceptable"] else [(x.get("rechazo") or {}).get("codigo") or "CORRESPONDENCIA_INCOMPLETA"],
          "intercambio": {k: x.get(k) for k in ("satisfechos", "requeridos", "rechazo", "procedencia", "sred", "naturaleza")}, "autorizacion": info.get("opciones")}
    reg = RP.generar_r1_opcion(P, sal, t["id"], ev, salida=sal / "registro_productivo.json", dictamen=sal / "dictamen_validacion.json")
    ok = reg["verificacion"]["cumple"] is True
    return dict(estado="completa" if ok else "rechazada", productos={"R1:" + t["id"]: {"documento": "r1_productos.json", "filas": "validacion_opcion.json"}},
                motivo=None if ok else ev["codigos"], intercambio=ev["intercambio"], **info)


def preflight_comandos(RR, RS, plan_ruta, T, ctx):
    """Importa (sin ejecutar su bloque principal) cada módulo productor con el importador de SU entrega y el núcleo S6."""
    import importlib
    out = []
    for c in plan_ruta["comandos"]:
        imp = RR.ImportadorEntrega(T, c["entrega"], RS.NUCLEO_S6, ctx)
        desinstalar(imp)
        imp.instalar()
        importlib.import_module(c["modulo"])
        imp.guarda()
        out.append({"modulo": c["modulo"], "entrega": c["entrega"], "modulos_cargados": len(imp.registro), "nucleo": RR.nucleo_por_entrega(T, c["entrega"], RS.NUCLEO_S6)})
        desinstalar(imp)
    return out


def productos_aceptados(a, o, plan, t, T, procedencia=None, modo_arnes=None):
    """{dependencia: salida aceptada} de las dependencias de la tarea: aceptadas en ESTA corrida (árbol íntegro) o en corridas PREVIAS con
    toda su autoridad RECONSTRUIDA (corrida_paso4.aceptaciones_previas). rem45: se consume la SALIDA EXACTA de la procedencia validada (nunca
    una búsqueda posterior por id en otra raíz) y se re-comprueba su árbol justo antes de consumirla; `procedencia` (dict) recibe el origen
    de cada dependencia consumida o el motivo por el que no se consumió. Modo productivo salvo --modo-arnes."""
    CO = _carga("corrida_paso4", "herramientas/b/corrida_paso4.py")
    modo = ("--modo-arnes" in a) if modo_arnes is None else bool(modo_arnes)
    deps = [x for x in (t.get("depende_de_expandido") or []) if x != "F0"]
    out = {}
    prov = procedencia if procedencia is not None else {}
    raiz = Path(o.get("--raiz-corrida", ""))
    if o.get("--raiz-corrida") and raiz.exists():
        for x, h in CO.estado_tareas(CO.Diario(raiz / "diario_corrida.jsonl")).items():
            ac = [e for e in h if e["op"] == "fin" and e["estado"] == "completa_verificada"]
            if x in deps and len(ac) == 1 and ac[0].get("arbol") and CO._arbol(raiz / "salidas" / x) == ac[0]["arbol"]:
                out[x] = raiz / "salidas" / x
                prov[x] = {"origen": "esta_corrida", "raiz": str(raiz.resolve()), "salida": str(out[x].resolve()), "identidad_sha256": ac[0].get("identidad_sha256"),
                           "arbol_sha256": CO.sha(CO.canon(ac[0]["arbol"]))}
    previas = [p for p in o.get("--corridas-previas", "").split(",") if p]
    if set(deps) - set(out) and previas:
        ef = CO.identidades_efectivas(o["--despliegue"], {"fuentes_v2": o["--fuentes"]}, {"tope_s": float(o.get("--tope", 2400.0)), "procesos": CO.CARRILES}, modo)
        informe = []
        for x, pv in CO.aceptaciones_previas(plan, previas, ef, modo, informe).items():
            if x not in deps or x in out:
                continue
            s_ = Path(pv["salida"])
            if CO._arbol(s_) != pv["arbol"]:                               # alterada entre la validación y el consumo: no se consume
                prov[x] = {"origen": "corrida_previa", "rechazo": "DEPENDENCIA_PREVIA_ALTERADA_ANTES_DE_CONSUMIR", "raiz": pv["raiz"]}
                continue
            out[x] = s_
            prov[x] = dict({k: v for k, v in pv.items() if k not in ("arbol", "productos")}, origen="corrida_previa")
        for e in informe:
            if e.get("tarea") in deps and e.get("tarea") not in out and e.get("motivo"):
                prov.setdefault(e["tarea"], {"origen": "corrida_previa", "rechazos": []}).setdefault("rechazos", []).append(e)
    return out


def hojas_y_fuentes_de(P, afirmaciones, acept, deps=None):
    """Componentes AUTORIZADOS de R1-D desde los productos ACEPTADOS: hojas ci-df inf (registros aceptados de C1..C6, solo sus requeridos)
    y fuentes PRV/XDD/CAN/SRED (salidas aceptadas de B1/B2/B3/A1). Una hoja requerida ausente -> la siembra falla (nunca se recupera
    en silencio un producto ajeno)."""
    comp = P.componentes_de(afirmaciones, deps)
    hojas = {}
    for x, d0 in sorted(acept.items()):
        if x.startswith("R1-C"):
            req = set(P.requeridos_orquestador(x))
            for f in sorted((d0 / "paquete/corrida/resultados").glob("*.json")):
                r = json.loads(f.read_bytes())
                k = (r["afirmacion"], r["sentido"])
                if k in req and r["afirmacion"] in comp["hojas"]:
                    hojas[k] = r
    fuentes = {}
    mapa = {"R1-B1": ("PRV", "demo/hito2/produccion_inf_G_cid_G.json"), "R1-B2": ("PRV", "demo/hito2/produccion_inf_G_cid_N.json")}
    for x, (clave, rel) in mapa.items():
        if x in acept:
            fuentes[(clave, rel)] = acept[x] / "paquete" / rel
    if "R1-B3" in acept:
        fuentes[("XDD", "demo/extremos/extremos_G_d.json")] = acept["R1-B3"] / "paquete/demo/extremos/extremos_G_d.json"
        fuentes[("CAN", "demo/extremos/extremos_G_f.json")] = acept["R1-B3"] / "paquete/demo/extremos/extremos_G_f.json"
    if "R1-A1" in acept:
        for d in ("G", "N"):
            fuentes[("PRV", "demo/hito2/sred_%s_df.json" % d)] = acept["R1-A1"] / "paquete" / ("demo/hito2/sred_%s_df.json" % d)
    return hojas, fuentes
BRECHA_R1 = {      # punto de entrada histórico EXACTO que falta enlazar al trabajador (preflight ya conectado bajo S6)
    "R1-A1": "c2_extremos.techo/evaluador/bb (C2: supremos) con su orden de subcomandos", "R1-A2": "c2_extremos.bb (C2: ínfimos d y f)",
    "R1-A3-G-U": "certificar_inf_df.certificar (cota U)", "R1-A3-N-U": "certificar_inf_df.certificar (cota U)",
    "R1-A3-G-L": "inf_df_bb_v3.main + cota_un_umbral_v2 (cota L con el certificado U NUEVO)", "R1-A3-N-L": "inf_df_bb_v3.main + cota_un_umbral_v2",
    "R1-B1": "extremos_G (ínfimos ci-d; el orquestador RECUPERA ci-d de XDD/PRV, no la calcula)", "R1-B2": "extremos_G (ínfimos ci-d)",
    "R1-B3": "extremos_dfd (ci-d sup / ci-f)", "R1-D": "orquestador_b.ejecutar sobre la corrida COMPARTIDA de las hojas (identidad de muestra) + censo_b_v2",
    "R1-F": "sensibilidad_q.main (ENSAYO QSEN2; no producción)", "R1-V": "orquestador_b.verificar + E13 sobre la corrida completa"}

if __name__ == "__main__":
    raise SystemExit(main())
