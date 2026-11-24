"""FAM02 (R1: salidas globales de afirmaciones y extremos; 18 tareas): plan y cobertura, comprobación sin cálculo de las 18 tareas,
y por tarea: cálculo y validación (C1..C6 y D por el orquestador; A*, B*, F por sus comandos históricos; V validación global sin
cálculo), enlace local de aceptación entre tareas de una misma ejecución (ENLACE-LOCAL-FAM02-v1), prueba de conexión sin cálculo con
las salidas guardadas de los comandos, comparación con las referencias y receta completa (sin ejecutarla).

Piezas (todas copias exactas; ver fuentes_fam02.json):
- ruta R1 instalada (nucleo_s6/instalacion/herramientas/b): tarea_r1.py (fdf4ba1e…; despacho, productores, rutas por comando),
  r1_s6.py (PilaR1S6: pila histórica del método v5 con el núcleo S6, preflight, cobertura y referencias), r1_rutas.py (e6f922fb…),
  opciones_p1.py, registro_productivo.py (d9addec6…), comparar_tarea.py y datos/paso4/opciones_r1.json (00c27b59…);
- núcleo S6 de la instalación (nucleo_s6/instalacion/src/paper2b = nucleo_s6/raiz/src/paper2b, archivo por archivo);
- entregas históricas que la ruta lee, con su ruta relativa (nucleo_s6/raiz/tmp/<entrega>/...): la pila de lima1351 (codigo/, cargada
  por bytes autenticados con las sustituciones registradas de r1_s6), sus inventarios (anclas de huellas), las entradas del método
  (registro v4, puntos U, SRED, XDD, CAN, PRV, plan C2), la cobertura y el presupuesto de lima1857 y las referencias.

Adaptaciones de interfaz (no cambian fórmulas, tolerancias, topes ni criterios):
- contexto: el de FAM01 (fam01.Contexto: misma construcción que ContextoS6, sin autoridad viva), con etiqueta FAM02;
- despliegue: solo lo que la pila usa (raiz_fuentes = nucleo_s6/raiz/tmp, resuelta al ejecutar; s6_package, d7_tree y run_class de
  datos/fam01/contexto_s6.json; ancla = null: no hay acto de autorización histórico);
- plan R1: corrida_paso4.construir_plan (rama R1: dependencias con «*» expandidas y orden topológico) sobre el presupuesto autenticado,
  sin lotes R2/R3 ni calendario; la autorización histórica de la corrida (diario, admisión, acto) no se reconstruye;
- tarea C: los pasos de tarea_r1.main para R1-C* (preflight bajo S6, plan del orquestador = histórico, muestra, producir con
  --tope-afirmacion 300 y --tope-proceso max(60, tope − 300), verificar con hojas_ci_v2, registro); con la TAREA COMPLETA el registro
  es registro_productivo.generar_r1 sin cambios; con una asignación PARCIAL (piloto) es su mismo cuerpo con los requeridos de la
  asignación (registro_r1_parcial), y la condición de tarea «al menos un comparable con medición histórica» se informa aparte;
- rutas por comando (A*, B*, F): los pasos de tarea_r1.main / ruta_intercambio (derivar, preflight_comandos, ejecutar_ruta, validar y
  generar_r1_ruta / generar_r1_opcion); la opción se activa con la decisión «aprobada» del catálogo instalado (en lugar de
  opciones_autorizadas) y los productos aceptados se leen del enlace local (en lugar de corrida_paso4.aceptaciones_previas);
- D: tarea_r1.hojas_y_fuentes_de + PilaR1S6.intercambio con las 15 dependencias aceptadas en la ejecución; V: generar_r1_global con
  las procedencias del enlace local;
- SAN-RUTAS-v1: los registros de lanzamiento públicos sin rutas personales se autentican por su correspondencia declarada;
- AREA-ESCRITURA-v1: la guarda de escritura de nucleo_v admite el paquete (cwd del comando) en lugar de la carpeta de la entrega;
- IGUALDAD-R1F-TIEMPOS-v1 (solo R1-F): en la igualdad con la salida histórica, además de r1_rutas.OPERATIVOS, se tratan como operativos
  /contexto_s y preparacion_s, rama_y_cota_s y por_contexto_s directamente bajo cada afirmación (duraciones de reloj de sensibilidad_q);
  se conservan en las salidas y sus diferencias se informan; el resto del contenido sigue con igualdad exacta.
- IGUALDAD-R1B-TIEMPOS-v1 (solo R1-B1 y R1-B2; autorizada por el autor el 2026-11-20): en la igualdad con la salida histórica del comando
  extremos_G_d_inf_v3 de lima1958, además de OPERATIVOS, se apartan /C2/<d>/segundos_subintervalos y /C2/<d>/segundos_techos (duraciones
  de reloj, origen comprobado en el módulo histórico) y /identidad_sha256, esta solo si se recomprueba en cada lado (la nueva = la identidad
  recalculada del contexto que valida y la registrada por el cálculo; la histórica = la misma en las dos salidas G y N de la entrega); el
  resto del contenido sigue con igualdad exacta.
- IGUALDAD-SRED-TIEMPOS-v1 (solo las dos salidas SRED de R1-A1; autorizada por el autor el 2026-11-20): en la igualdad con la salida
  histórica de sup_reducido (lima1958), además de OPERATIVOS, se aparta el tiempo de reloj /traza/<k>/0 (round(time.time() - t0, 1),
  origen comprobado en el módulo histórico) solo si cada entrada de las dos trazas tiene los cuatro campos previstos [tiempo, cajas, L, U]
  con un tiempo válido; longitud, orden, cajas, L, U y el resto del contenido siguen con igualdad exacta. Los archivos y sus huellas no
  cambian; los tiempos apartados se informan.
- CIERRE-MUESTRA-R1D-v1 (solo R1-D; autorizada por el autor el 2026-11-21 tras el diagnóstico DIAG-R1D-MUESTRA-v1). Tres partes:
  (a) la muestra del orquestador es su cierre por dependencias: las 1.088 afirmaciones de D más 640 hojas ci-d/ci-f. Antes de calcular se
      comprueba que esas 640 son de las rutas de recuperación, que la cobertura asigna sus 1.280 extremos exactamente a R1-B1/B2/B3, que
      las tres están aceptadas y que las fuentes inyectadas son sus productos aceptados; si algo falla, rechazo controlado sin cálculo;
  (b) los 1.280 son dependencias verificadas (iguales al producto aceptado), contadas aparte de los 1.856 extremos propios de D;
  (c) los 1.856 se comparan con una referencia compuesta:
      - ci_df_sup: la tabla autenticada hojas_ci_v4;
      - country_global: E13 v4 sobre las hojas que el plan histórico autenticado asigna a cada escenario, sin mezcla de escenarios;
      - conditional_none: referencia derivada; la lectura literal de cg_hojas se informa;
      - el comparador exige G exacto, hoja ganadora, punto y estado, y coteja el índice de contexto donde el testigo lo registra.
  La pila se adapta solo en su instancia durante generar_r1 y se restaura; fam02-comparar lo recalcula sobre los bytes.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import json
import math
import os
import sys
import time
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RAIZ = BASE / "nucleo_s6" / "raiz"
INST = BASE / "nucleo_s6" / "instalacion"
T = RAIZ / "tmp"
DATOS = BASE / "datos" / "fam02"
ETIQUETA = "REPRODUCCION LIMPIA FAM02 NO OFICIAL"
L1857 = ("validacion_evidencia_comparador_paso4_3_7_2026-10-12_lima1857", "369beaa07cc56fffc966112b6d1faaebac60d072529dc299e761eebf523bca42")
COBERTURA = L1857 + ("demo/plan15/cobertura_r1.json",)
PRESUPUESTO = L1857 + ("demo/plan15/presupuesto_lotes.json",)
P1351 = ("p0_completo_h4_paso4_3_7_2026-10-09_lima1351", "ba473a76059faa9719e0f2a0638ce51878a872e74fccf6c680b9d9d73fb14743")
RES = ("resolucion_3_7_2026-10-04_lima1941", "d6fd4e384c5309e3d5720813d4e8770d7b849ad0bd9e90d1a6534af2a7bfa17f", "demo/registro/registro_candidato_v4.json")
HOJAS_V2 = "demo/e13v4b/hojas_ci_v2.json"            # hojas E13 v4 CENSO-v2 de lima1351 (tarea_r1, rama C)
OPCIONES = ("datos/paso4/opciones_r1.json", "00c27b5976adf5074a2448a12d401786a4d9770405ffeb7b47342d5b510db24f")
# Consumo de productos aceptados entre tareas que NO está en depende_de del presupuesto, sino en la decisión firmada R1-A1A2 (opciones_r1:
# «R1-A1 y R1-A2 dependen de R1-B3») y en las rutas instaladas (r1_rutas.DEPENDENCIA_DE_ENTRADA; tarea_r1.hojas_y_fuentes_de).
CONSUMO = {"R1-A1": (["R1-B3"], "decisión R1-A1A2 (opciones_r1): 4 testigos supremos d/f del producto aceptado de R1-B3; produce SRED-G/N"),
           "R1-A2": (["R1-B3"], "decisión R1-A1A2 (opciones_r1): 4 testigos ínfimos d/f del producto aceptado de R1-B3"),
           "R1-A3-G-L": (["R1-A3-G-U"], "r1_rutas.DEPENDENCIA_DE_ENTRADA: certificado U NUEVO de su tarea U (nunca la L histórica)"),
           "R1-A3-N-L": (["R1-A3-N-U"], "r1_rutas.DEPENDENCIA_DE_ENTRADA: certificado U NUEVO de su tarea U"),
           "R1-D": (["R1-A1", "R1-B1", "R1-B2", "R1-B3"] + ["R1-C%d" % i for i in range(1, 7)],
                    "tarea_r1.hojas_y_fuentes_de: hojas ci-df aceptadas de C1..C6 y fuentes PRV/XDD/CAN/SRED aceptadas de B1/B2/B3/A1"),
           "R1-V": (["R1-D", "R1-F"], "cierre de dependencias del plan (R1-V -> D, F; D -> A*, B*, C*) con su procedencia")}
ESTADOS_TERMINALES_ADMISIBLES = ("convergido", "detenido")
ESTADOS_VALIDADOS = ("completa_validada", "hojas_validadas", "hojas_validadas_por_referencia_citada")   # registro productivo que cumple


class Fam02Error(RuntimeError):
    pass


def need(t, codigo):
    if not t:
        raise Fam02Error(codigo)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def cargar(nombre: str, ruta: Path):
    if nombre not in sys.modules:
        sp = importlib.util.spec_from_file_location(nombre, ruta)
        m = importlib.util.module_from_spec(sp)
        sys.modules[nombre] = m
        sp.loader.exec_module(m)
    return sys.modules[nombre]


def F1():
    return cargar("fam01", BASE / "src" / "fam01.py")


def canon(o) -> bytes:
    return F1().canon(o)


def eid(cid: str, s: str) -> str:
    """extreme_id de la cobertura R1 (global_extreme_v4.eid = r1_s6.preflight)."""
    return sha((cid + "|" + s).encode("utf-8"))[:16]


def autenticado(entrega: str, inv_h: str, rel: str, raiz_fuentes: Path | None = None) -> bytes:
    """Bytes de <entrega>/<rel> autenticados por el inventario ANCLADO de su entrega (mismo vínculo que tarea_r1 y r1_s6)."""
    R = Path(raiz_fuentes or T)
    inv_raw = (R / entrega / "audit/entrega.json").read_bytes()
    need(sha(inv_raw) == inv_h, "INVENTARIO_ALTERADO:%s" % entrega)
    raw = (R / entrega / rel).read_bytes()
    x = json.loads(inv_raw)["files"].get(rel)
    need(x is not None and (x["sha256"] if isinstance(x, dict) else x) == sha(raw), "NO_AUTENTICADO:%s/%s" % (entrega, rel))
    return raw


# ================================================================================================ plan, cobertura y selección (sin modelo)
def plan_r1(raiz_fuentes: Path | None = None) -> dict:
    """Las 18 tareas R1 del presupuesto autenticado con sus dependencias expandidas y orden topológico (corrida_paso4.construir_plan,
    rama R1, sin cambios de criterio), más el consumo de productos aceptados que fijan la decisión R1-A1A2 y las rutas instaladas."""
    raw = autenticado(*PRESUPUESTO, raiz_fuentes=raiz_fuentes)
    pres = json.loads(raw)
    mot = []
    r1 = [{"id": t["tarea"], "fase": "R1", "depende_de": list(t.get("depende_de") or []), "pared_s": t["pared_s"], "cpu_s": t["cpu_s"],
           "contenido": t.get("contenido")} for t in pres["R1"]]
    ids = {t["id"] for t in r1} | {"F0"}
    for t in r1:
        exp = []
        for d in t["depende_de"]:
            m = sorted(x for x in ids if x.startswith(d[:-1]) and x != t["id"]) if d.endswith("*") else ([d] if d in ids else [])
            if not m:
                mot.append("R1 %s depende de %s inexistente" % (t["id"], d))
            exp += m
        t["depende_de_expandido"] = sorted(set(exp))
        c = CONSUMO.get(t["id"])
        t["consume_aceptados"] = {"tareas": c[0], "fuente": c[1]} if c else None
    orden, hecho, pend = [], {"F0"}, {t["id"]: set(t["depende_de_expandido"]) for t in r1}
    while pend:
        listos = sorted(k for k, v in pend.items() if v <= hecho)
        if not listos:
            mot.append("R1 con dependencias cíclicas: %s" % sorted(pend))
            break
        for k in listos:
            orden.append(k)
            hecho.add(k)
            pend.pop(k)
    # orden de ejecución que respeta también el consumo de aceptados (A1/A2 tras B3; L tras U; D tras A*, B*, C*; V al final)
    orden_ej, hecho2, pend2 = [], {"F0"}, {t["id"]: set(t["depende_de_expandido"]) | set((t["consume_aceptados"] or {}).get("tareas") or []) for t in r1}
    while pend2:
        listos = [t["id"] for t in r1 if t["id"] in pend2 and pend2[t["id"]] <= hecho2]
        if not listos:
            mot.append("consumo cíclico: %s" % sorted(pend2))
            break
        for k in listos:
            orden_ej.append(k)
            hecho2.add(k)
            pend2.pop(k)
    return {"presupuesto": {"entrega": PRESUPUESTO[0], "archivo": PRESUPUESTO[2], "sha256": sha(raw)}, "r1": r1, "orden_topologico": orden,
            "orden_de_ejecucion": orden_ej, "motivos": mot, "tareas": len(r1)}


def cobertura(raiz_fuentes: Path | None = None) -> dict:
    return {t["tarea"]: t for t in json.loads(autenticado(*COBERTURA, raiz_fuentes=raiz_fuentes))["tareas"]}


def registro_v4(raiz_fuentes: Path | None = None) -> dict:
    return json.loads(autenticado(*RES, raiz_fuentes=raiz_fuentes))["afirmaciones"]


def campos(cid: str) -> dict:
    """= orquestador_b.campos / extremos_G_df_v5.campos (identificador de afirmación del registro v4)."""
    p = cid.split(":")
    if p[3] == "ci":
        return {"fam": "ci", "pais": p[4], "j": p[5], "dis": p[7]}
    if p[3] == "c":
        return {"fam": "c", "pais": p[4], "scen": p[5], "dis": p[6]}
    return {"fam": "g", "scen": p[4], "dis": p[5]}


def requeridos(tarea: str, cob: dict, reg: dict) -> list:
    """[(afirmación, sentido)] de la tarea (ids EXACTOS de su entrada en la cobertura, resueltos contra el registro v4), ordenados: la
    misma derivación que r1_s6.PilaR1S6.requeridos_orquestador; fam02-unidad la vuelve a hacer con la pila y exige igualdad."""
    e = {eid(c, s): (c, s) for c in reg for s in ("sup", "inf")}
    ids = (cob.get(tarea) or {}).get("ids") or []
    need(ids and all(i in e for i in ids), "COBERTURA_NO_RESUELTA:%s" % tarea)
    return sorted(e[i] for i in ids)


def seleccion_piloto(plan: dict, cob: dict, reg: dict) -> dict:
    """Regla del encargo: primera hoja numérica por identificador estable (afirmación, en el orden de los requeridos) de la primera tarea C
    del plan que tenga hojas numéricas (ruta calculo_v5_ci_df: ci con menú df)."""
    for t in [x["id"] for x in plan["r1"] if x["id"].startswith("R1-C")]:
        req = requeridos(t, cob, reg)
        num = [(c, s) for c, s in req if campos(c)["fam"] == "ci" and campos(c)["j"] == "df"]
        if num:
            c, s = num[0]
            return {"tarea": t, "hoja": c, "sentido": s, "extreme_id": eid(c, s), "requeridos_de_la_tarea": len(req), "hojas_numericas_de_la_tarea": len(num),
                    "regla": "primera tarea C del plan con hojas numéricas (ci-df, ruta calculo_v5_ci_df); su primera hoja por identificador "
                             "estable (orden de (afirmación, sentido) de los requeridos de la cobertura autenticada)"}
    raise Fam02Error("SIN_HOJAS_NUMERICAS_EN_LAS_TAREAS_C")


def ruta_de_tarea(tid: str, TR=None) -> str:
    if tid.startswith("R1-C"):
        return "calculo_orquestador_v5 (orquestador_b.ejecutar sobre hojas ci-df) + verificar + registro_productivo.generar_r1"
    if tid == "R1-D":
        return "intercambio de productos aceptados (r1_s6.intercambio) + orquestador_b.ejecutar (supremos ci-df cerrados, agregados) + verificar + generar_r1"
    if tid == "R1-V":
        return "validación global (registro_productivo.generar_r1_global sobre el cierre D, F)"
    op = {"R1-B3": "B3_VALIDEZ_Y_COMPARACION", "R1-A1": "A1A2_INTERCAMBIO_DE_TESTIGOS", "R1-A2": "A1A2_INTERCAMBIO_DE_TESTIGOS"}.get(tid)
    if tid.startswith("R1-A3"):
        op = "A3_CRITERIO_GLOBAL"
    base = "comandos históricos (r1_rutas.derivar -> tarea_r1.ejecutar_ruta)"
    if op == "A1A2_INTERCAMBIO_DE_TESTIGOS":
        return ("opción aprobada %s: tarea_r1.ruta_intercambio (A1 ejecuta los 2 comandos SRED de plan_sred; A2 sin comandos) + correspondencia "
                "de testigos con el producto de R1-B3 ACEPTADO en la ejecución (fam02.intercambio_local) + generar_r1_opcion" % op)
    if op:
        return base + " + opción aprobada %s (opciones_p1.validacion_inicial; igualdad en su comparación)" % op
    return base + " + r1_rutas.validar + registro_productivo.generar_r1_ruta"


# ================================================================================================ contexto S6 y pila R1 instalada
def preparar():
    """sys.path como seleccion_paso4.configurar: el núcleo S6 de la instalación (src/paper2b) delante y la raíz del proyecto copiada
    (herramientas/) después; nunca la raíz/src."""
    for p in (str(RAIZ / "src"), str(RAIZ), str(INST / "src")):
        while p in sys.path:
            sys.path.remove(p)
    sys.path.insert(0, str(RAIZ))
    sys.path.insert(0, str(INST / "src"))
    import paper2b
    need(Path(paper2b.__file__).resolve().parent == (INST / "src" / "paper2b").resolve(), "NUCLEO_S6_NO_ES_EL_DE_LA_INSTALACION:" + paper2b.__file__)


def contexto():
    preparar()
    f = F1()
    return f.Contexto(dict(f.parametros(), etiqueta=ETIQUETA), raiz=RAIZ, inst=INST)


def despliegue(raiz_fuentes: Path | None = None) -> dict:
    p = F1().parametros()
    return {"raiz_fuentes": str(Path(raiz_fuentes or T)), "s6_package": p["s6_package"], "ancla": None, "d7_dir": p["d7_dir"], "d7_tree": p["d7_tree"],
            "run_class": p["run_class"], "etiqueta": ETIQUETA}


def pila(ctx, raiz_fuentes: Path | None = None):
    """(PilaR1S6, r1_s6, r1_rutas, tarea_r1) de la instalación copiada, con el contexto de la corrida; r1_rutas con la lectura
    SAN-RUTAS-v1 de los registros de lanzamiento públicos (adaptar_san_rutas)."""
    TR = cargar("tarea_r1", INST / "herramientas/b/tarea_r1.py")
    RS = TR._carga("r1_s6", "herramientas/b/r1_s6.py")
    RR = TR._carga("r1_rutas", "herramientas/b/r1_rutas.py")
    adaptar_san_rutas(RR)
    adaptar_area_de_escritura(RR)
    return RS.PilaR1S6(ctx, despliegue(raiz_fuentes)), RS, RR, TR


# ================================================================================================ AREA-ESCRITURA-v1 (rutas por comando)
# codigo/demo/nucleo_v.write_json_atomic (idéntica en las 6 entregas de las rutas por comando) solo escribe dentro de AREA = la carpeta de SU
# entrega: el comando histórico se lanzaba con cwd = la entrega (registro de lanzamiento: «cwd» tmp/<entrega>). r1_rutas.ejecutar_comando lo
# ejecuta con cwd = el paquete nuevo, así que la misma guarda rechaza la salida (DEMO_WRITE_OUTSIDE_AREA). Adaptación de interfaz, con el
# mecanismo de r1_rutas.GENERICAS (sustitución textual registrada al portar los bytes autenticados): el área de escritura pasa a ser el
# paquete (cwd del comando). La guarda se conserva (nada fuera del paquete) y no cambia ningún cálculo; sin ella el comando escribiría en
# la entrega histórica copiada.
AREA_ESCRITURA = ('need(path.resolve().is_relative_to(AREA.resolve()), "DEMO_WRITE_OUTSIDE_AREA:" + str(path))',
                  'need(path.resolve().is_relative_to(Path.cwd().resolve()), "DEMO_WRITE_OUTSIDE_AREA:" + str(path))  '
                  '# FAM02 AREA-ESCRITURA-v1: área de escritura = paquete (cwd de r1_rutas.ejecutar_comando)')


def adaptar_area_de_escritura(RR) -> None:
    if AREA_ESCRITURA not in RR.GENERICAS:
        RR.GENERICAS.append(AREA_ESCRITURA)


# ================================================================================================ IGUALDAD-R1F-TIEMPOS-v1 (solo R1-F)
# r1_rutas.igual_a_historica compara la salida de un comando con la histórica tras quitar las claves de r1_rutas.OPERATIVOS (segundos,
# pared_s, cpu_s, ...). sensibilidad_q (lima1958) escribe además cuatro duraciones de reloj que esa lista no incluye (round(time.time() - t, …)
# en sensibilidad_q.py, l. 124, 132, 142, 151 y 191), y por eso ninguna nueva ejecución de R1-F podía igualar a la histórica. Corrección
# técnica indicada por el autor (2026-11-16): SOLO en R1-F y SOLO en estas rutas exactas se tratan como operativas:
#   /contexto_s  y  /afirmaciones/<afirmación>/{preparacion_s, rama_y_cota_s, por_contexto_s}
# Cualquier otra clave con esos nombres, cualquier otra tarea y todo el contenido científico siguen con la regla instalada (igualdad exacta
# tras OPERATIVOS). Un campo de tiempo solo se aparta si está en las dos salidas y es una duración (número finito >= 0); si falta en una o no
# es una duración, la igualdad falla. Los campos se conservan en las salidas y sus diferencias se informan. OPERATIVOS y r1_rutas.py no
# cambian: la regla se activa solo mientras se valida R1-F (regla_r1f) y fam02-comparar la recalcula por su cuenta.
R1F_TIEMPOS = {"regla": "IGUALDAD-R1F-TIEMPOS-v1", "tarea": "R1-F", "entrega": "cierre_df_paso4_3_7_2026-10-05_lima1958",
               "modulo": "codigo.sensibilidad_q", "salida": "demo/paso4/sensibilidad_q.json",
               "raiz": ("contexto_s",), "bajo_cada_afirmacion": ("preparacion_s", "rama_y_cota_s", "por_contexto_s")}


def _duracion(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v >= 0


def _tiempos_r1f(doc) -> tuple:
    """(documento sin las rutas exactas de R1F_TIEMPOS, {ruta: valor apartado}); nada más se aparta."""
    if not isinstance(doc, dict):
        return doc, {}
    d, q = dict(doc), {}
    for k in R1F_TIEMPOS["raiz"]:
        if k in d and _duracion(d[k]):
            q["/" + k] = d.pop(k)
    af = d.get("afirmaciones")
    if isinstance(af, dict):
        d["afirmaciones"] = {}
        for cid, a in af.items():
            if isinstance(a, dict):
                a = dict(a)
                for k in R1F_TIEMPOS["bajo_cada_afirmacion"]:
                    if k in a and _duracion(a[k]):
                        q["/afirmaciones/%s/%s" % (cid, k)] = a.pop(k)
            d["afirmaciones"][cid] = a
    return d, q


def igualdad_r1f(RR, producido: bytes, historico: bytes) -> dict:
    """IGUALDAD-R1F-TIEMPOS-v1: igual = mismos campos de tiempo en las dos salidas y, sin ellos, igualdad exacta con r1_rutas._sin_operativos
    (la regla instalada). Informa también el juicio de la regla instalada sin la adaptación y cada diferencia de tiempo."""
    p, h = RR._cargar(producido), RR._cargar(historico)
    p2, qp = _tiempos_r1f(p)
    h2, qh = _tiempos_r1f(h)
    mismos = set(qp) == set(qh)
    cient = RR._sin_operativos(p2) == RR._sin_operativos(h2)
    return {"regla": R1F_TIEMPOS["regla"], "igual": bool(mismos and cient), "contenido_cientifico_igual": cient, "campos_de_tiempo_en_ambas": mismos,
            "campos_de_tiempo": len(qp), "solo_en_la_nueva": sorted(set(qp) - set(qh)), "solo_en_la_historica": sorted(set(qh) - set(qp)),
            "diferencias_de_tiempo": [{"campo": k, "nuevo": qp[k], "historico": qh[k]} for k in sorted(set(qp) & set(qh)) if qp[k] != qh[k]],
            "igual_con_la_regla_instalada_sin_adaptacion": RR._sin_operativos(p) == RR._sin_operativos(h)}


@contextlib.contextmanager
def regla_r1f(RR, tarea: str, plan_ruta: dict):
    """Solo en R1-F, y solo si la ruta es exactamente el comando sensibilidad_q de lima1958 con su única salida: mientras dura la validación,
    r1_rutas.igual_a_historica = igualdad_r1f (informe en el valor devuelto); se restaura siempre. En otra tarea no cambia nada (None)."""
    if tarea != R1F_TIEMPOS["tarea"]:
        yield None
        return
    cs = plan_ruta["comandos"]
    need(len(cs) == 1 and (cs[0]["entrega"], cs[0]["modulo"]) == (R1F_TIEMPOS["entrega"], R1F_TIEMPOS["modulo"])
         and RR.salidas_del_comando(cs[0], T) == [R1F_TIEMPOS["salida"]], "R1F_RUTA_DISTINTA_DE_LA_PREVISTA (IGUALDAD-R1F-TIEMPOS-v1 no se aplica)")
    need(sys.modules.get("r1_rutas") is RR, "R1_RUTAS_DISTINTO_DEL_DE_LA_VALIDACION")
    instalada, informe = RR.igual_a_historica, {"regla": R1F_TIEMPOS["regla"], "aplicada": False}

    def igual(producido: bytes, historico: bytes) -> bool:
        informe.update(igualdad_r1f(RR, producido, historico), aplicada=True)
        return informe["igual"]
    RR.igual_a_historica = igual
    try:
        yield informe
    finally:
        RR.igual_a_historica = instalada


# ================================================================================================ IGUALDAD-R1B-TIEMPOS-v1 (solo R1-B1 y R1-B2)
# extremos_G_d_inf_v3 (lima1958) escribe bajo C2/<diseño> dos duraciones de reloj que r1_rutas.OPERATIVOS no incluye
# (t_sub = round(time.time() - tp, 1) y t_pts = round(time.time() - tp, 1)) y, antes de calcular, la huella del contexto
# (identidad_sha256 = ctx.identity_sha256). En la corrida, r1_s6 sustituye nucleo_v.Contexto por el contexto S6 de la corrida, cuya
# identidad es otra por construcción; por eso ninguna nueva ejecución de R1-B1/R1-B2 podía igualar a la histórica. Corrección autorizada
# por el autor (2026-11-20), limitada a R1-B1 (diseño G) y R1-B2 (diseño N), al comando exacto de lima1958 con su única salida y a:
#   /C2/<d>/segundos_subintervalos y /C2/<d>/segundos_techos: se apartan solo si están en las dos salidas y son duraciones (finitas >= 0);
#   /identidad_sha256: se aparta solo si se recomprueba en cada lado: la NUEVA = la identidad del contexto que valida, recalculada como
#   sha256(canon(ctx.identity)) e igual a la registrada por la ejecución de cálculo; la HISTÓRICA = la de su entrega, la misma en las dos
#   salidas del comando (G y N), autenticadas por el inventario de lima1958.
# El origen se comprueba en los bytes autenticados del módulo histórico (cada fragmento exactamente una vez). El resto del contenido sigue
# con igualdad exacta tras OPERATIVOS. OPERATIVOS y r1_rutas.py no cambian: la regla solo actúa mientras se valida R1-B1/R1-B2
# (regla_r1b), y fam02-comparar la recalcula por su cuenta.
R1B_TIEMPOS = {"regla": "IGUALDAD-R1B-TIEMPOS-v1", "tareas": {"R1-B1": "G", "R1-B2": "N"}, "entrega": "cierre_df_paso4_3_7_2026-10-05_lima1958",
               "modulo": "codigo.extremos_G_d_inf_v3", "fuente": "codigo/extremos_G_d_inf_v3.py", "salida": "demo/hito2/produccion_inf_G_cid_%s.json",
               "bajo_C2_del_diseno": ("segundos_subintervalos", "segundos_techos"), "identidad": "identidad_sha256",
               "origen": ("t_sub = round(time.time() - tp, 1)", "t_pts = round(time.time() - tp, 1)",
                          '"segundos_subintervalos": t_sub, "segundos_techos": t_pts}', '"identidad_sha256": ctx.identity_sha256')}


def _hex64(v) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def origen_r1b(RR) -> dict:
    """Los fragmentos de R1B_TIEMPOS["origen"] en los bytes AUTENTICADOS del módulo histórico, cada uno exactamente una vez."""
    raw = RR._aut(T, R1B_TIEMPOS["entrega"], R1B_TIEMPOS["fuente"])
    src = raw.decode("utf-8")
    cuentas = {f: src.count(f) for f in R1B_TIEMPOS["origen"]}
    return {"fuente": "%s/%s" % (R1B_TIEMPOS["entrega"], R1B_TIEMPOS["fuente"]), "sha256": sha(raw), "fragmentos": cuentas,
            "demostrado": all(n == 1 for n in cuentas.values())}


def _tiempos_r1b(doc, d: str) -> tuple:
    """(documento sin las dos duraciones de C2/<d> ni identidad_sha256, {ruta: valor apartado}, identidad); nada más se aparta."""
    if not isinstance(doc, dict):
        return doc, {}, None
    x, q = dict(doc), {}
    ident = x.pop(R1B_TIEMPOS["identidad"], None)
    c2 = x.get("C2")
    if isinstance(c2, dict) and isinstance(c2.get(d), dict):
        c = dict(c2[d])
        for k in R1B_TIEMPOS["bajo_C2_del_diseno"]:
            if k in c and _duracion(c[k]):
                q["/C2/%s/%s" % (d, k)] = c.pop(k)
        x["C2"] = dict(c2, **{d: c})
    return x, q, ident


def igualdad_r1b(RR, tarea: str, producido: bytes, historico: bytes, historico_otro: bytes, ctx, identidad_del_calculo) -> dict:
    """IGUALDAD-R1B-TIEMPOS-v1: igual = origen demostrado, las dos duraciones de C2/<d> en las dos salidas, identidad recomprobada en cada
    lado y, sin esos tres campos, igualdad exacta con r1_rutas._sin_operativos (la regla instalada). Informa también cada diferencia."""
    d = R1B_TIEMPOS["tareas"][tarea]
    p, h = RR._cargar(producido), RR._cargar(historico)
    p2, qp, ip = _tiempos_r1b(p, d)
    h2, qh, ih = _tiempos_r1b(h, d)
    esperados = {"/C2/%s/%s" % (d, k) for k in R1B_TIEMPOS["bajo_C2_del_diseno"]}
    mismos = set(qp) == set(qh) == esperados
    cient = RR._sin_operativos(p2) == RR._sin_operativos(h2)
    recalc = sha(canon(ctx.identity))
    nueva = {"en_la_salida": ip, "contexto_que_valida": ctx.identity_sha256, "recalculada_del_contexto": recalc,
             "registrada_por_el_calculo": identidad_del_calculo}
    nueva["cumple"] = _hex64(ip) and ip == ctx.identity_sha256 == recalc == identidad_del_calculo
    otro = RR._cargar(historico_otro)
    io_ = otro.get(R1B_TIEMPOS["identidad"]) if isinstance(otro, dict) else None
    hist = {"en_la_salida": ih, "en_la_otra_salida_del_comando": io_, "cumple": _hex64(ih) and ih == io_}
    orig = origen_r1b(RR)
    instalada = RR._sin_operativos(p) == RR._sin_operativos(h)        # si la regla instalada ya acepta, su veredicto no cambia
    adaptada = bool(orig["demostrado"] and mismos and cient and nueva["cumple"] and hist["cumple"])
    igual = bool(instalada or adaptada)
    return {"regla": R1B_TIEMPOS["regla"], "tarea": tarea, "diseno": d, "igual": igual,
            "por": "regla_instalada" if instalada else ("adaptacion" if adaptada else None), "contenido_cientifico_igual": cient,
            "campos_de_tiempo_en_ambas": mismos, "campos_de_tiempo": sorted(qp), "solo_en_la_nueva": sorted(set(qp) - set(qh)),
            "solo_en_la_historica": sorted(set(qh) - set(qp)),
            "diferencias_de_tiempo": [{"campo": k, "nuevo": qp[k], "historico": qh[k]} for k in sorted(set(qp) & set(qh)) if qp[k] != qh[k]],
            "identidad_nueva": nueva, "identidad_historica": hist, "origen": orig,
            "igual_con_la_regla_instalada_sin_adaptacion": instalada}


def _salidas_r1b(RR, tarea: str) -> tuple:
    """(ruta de la salida del comando, bytes históricos autenticados de esa salida y de la del otro diseño)."""
    d = R1B_TIEMPOS["tareas"][tarea]
    o = "N" if d == "G" else "G"
    s = R1B_TIEMPOS["salida"] % d
    return s, RR._aut(T, R1B_TIEMPOS["entrega"], s), RR._aut(T, R1B_TIEMPOS["entrega"], R1B_TIEMPOS["salida"] % o)


@contextlib.contextmanager
def regla_r1b(RR, tarea: str, plan_ruta: dict, ctx, identidad_del_calculo):
    """Solo en R1-B1/R1-B2, y solo si la ruta es exactamente el comando extremos_G_d_inf_v3 de lima1958 con su única salida: mientras dura
    la validación, r1_rutas.igual_a_historica = igualdad_r1b (informe en el valor devuelto); se restaura siempre. En otra tarea, None."""
    if tarea not in R1B_TIEMPOS["tareas"]:
        yield None
        return
    cs = plan_ruta["comandos"]
    s, _, otro = _salidas_r1b(RR, tarea)
    need(len(cs) == 1 and (cs[0]["entrega"], cs[0]["modulo"]) == (R1B_TIEMPOS["entrega"], R1B_TIEMPOS["modulo"])
         and RR.salidas_del_comando(cs[0], T) == [s], "R1B_RUTA_DISTINTA_DE_LA_PREVISTA (IGUALDAD-R1B-TIEMPOS-v1 no se aplica)")
    need(sys.modules.get("r1_rutas") is RR, "R1_RUTAS_DISTINTO_DEL_DE_LA_VALIDACION")
    instalada, informe = RR.igual_a_historica, {"regla": R1B_TIEMPOS["regla"], "aplicada": False}

    def igual(producido: bytes, historico: bytes) -> bool:
        informe.update(igualdad_r1b(RR, tarea, producido, historico, otro, ctx, identidad_del_calculo), aplicada=True)
        return informe["igual"]
    RR.igual_a_historica = igual
    try:
        yield informe
    finally:
        RR.igual_a_historica = instalada


# ================================================================================================ IGUALDAD-SRED-TIEMPOS-v1 (solo R1-A1)
# sup_reducido (lima1958), el módulo de los comandos SRED-G y SRED-N que R1-A1 ejecuta bajo la opción A1/A2, anota cada 200 cajas una entrada
# [round(time.time() - t0, 1), n["cajas"], best["L"] / gam, Ucur / gam] en «traza» y la escribe submuestreada por número de entradas. El
# elemento 0 es el TIEMPO DE RELOJ transcurrido, que r1_rutas.OPERATIVOS no cubre (sí /segundos); por eso ninguna nueva ejecución de R1-A1
# podía igualar a la histórica. Corrección autorizada por el autor (2026-11-20), limitada a las DOS salidas SRED de R1-A1 (identificadas por
# los bytes autenticados de la salida histórica) y a /traza/<k>/0, que se aparta solo si:
#   - el origen está en los bytes AUTENTICADOS del módulo histórico (cada fragmento de SRED_TIEMPOS["origen"] exactamente una vez);
#   - las dos salidas tienen «traza» como lista de entradas con exactamente los cuatro campos previstos: tiempo (número finito >= 0, no
#     booleano; no decreciente a lo largo de la traza), cajas (entero >= 0, no booleano), L y U (números, no booleanos);
#   - longitud, orden, cajas, L y U de cada entrada y el resto del contenido son exactamente iguales tras OPERATIVOS (la regla instalada).
# Los archivos no se tocan: sus bytes, sus huellas y los tiempos originales quedan como están, y el informe da los tiempos apartados de cada
# lado y la huella de cada archivo. El límite de ejecución (argumento tope_s del comando, límite del plan) y el criterio de convergencia (T2 y
# «estado», comparado exactamente) no cambian. La regla solo actúa mientras se valida R1-A1 (regla_sred) y fam02-comparar la recalcula.
SRED_TIEMPOS = {"regla": "IGUALDAD-SRED-TIEMPOS-v1", "tarea": "R1-A1", "entrega": "cierre_df_paso4_3_7_2026-10-05_lima1958",
                "modulo": "codigo.sup_reducido", "fuente": "codigo/sup_reducido.py",
                "registros": ("logs/H2/SRED-G.tarea.json", "logs/H2/SRED-N.tarea.json"),
                "salidas": ("demo/hito2/sred_G_df.json", "demo/hito2/sred_N_df.json"), "campo": "traza", "campos_por_entrada": 4,
                "origen": ('traza.append([round(time.time() - t0, 1), n["cajas"], best["L"] / gam, Ucur / gam])',
                           'if n["cajas"] % 200 == 0:',
                           'traza=traza[:: max(1, len(traza) // 60)] + traza[-1:]')}


def origen_sred(RR) -> dict:
    """Los fragmentos de SRED_TIEMPOS["origen"] en los bytes AUTENTICADOS de sup_reducido.py, cada uno exactamente una vez."""
    raw = RR._aut(T, SRED_TIEMPOS["entrega"], SRED_TIEMPOS["fuente"])
    src = raw.decode("utf-8")
    cuentas = {f: src.count(f) for f in SRED_TIEMPOS["origen"]}
    return {"fuente": "%s/%s" % (SRED_TIEMPOS["entrega"], SRED_TIEMPOS["fuente"]), "sha256": sha(raw), "fragmentos": cuentas,
            "demostrado": all(n == 1 for n in cuentas.values())}


def _numero(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _traza_sred(doc) -> tuple:
    """(documento con cada entrada de /traza sin su elemento 0, [tiempos apartados], None) si la traza tiene la forma prevista; si no,
    (documento sin cambios, None, motivo). Nada más se aparta."""
    if not isinstance(doc, dict) or not isinstance(doc.get(SRED_TIEMPOS["campo"]), list):
        return doc, None, "SIN_TRAZA"
    tr = doc[SRED_TIEMPOS["campo"]]
    if not all(isinstance(e, list) and len(e) == SRED_TIEMPOS["campos_por_entrada"] for e in tr):
        return doc, None, "ENTRADA_SIN_LOS_CUATRO_CAMPOS"
    if not all(_duracion(e[0]) for e in tr):
        return doc, None, "TIEMPO_NO_VALIDO"
    if [e[0] for e in tr] != sorted(e[0] for e in tr):
        return doc, None, "TIEMPOS_DECRECIENTES"
    if not all(isinstance(e[1], int) and not isinstance(e[1], bool) and e[1] >= 0 for e in tr):
        return doc, None, "CAJAS_NO_ENTERAS"
    if not all(_numero(e[2]) and _numero(e[3]) for e in tr):
        return doc, None, "L_O_U_NO_NUMERICOS"
    return dict(doc, **{SRED_TIEMPOS["campo"]: [e[1:] for e in tr]}), [e[0] for e in tr], None


def igualdad_sred(RR, salida: str, producido: bytes, historico: bytes) -> dict:
    """IGUALDAD-SRED-TIEMPOS-v1 sobre una de las dos salidas SRED: igual = la regla instalada ya acepta, o (origen demostrado, forma prevista
    en las dos trazas, misma longitud y, sin /traza/<k>/0, igualdad exacta con r1_rutas._sin_operativos). Informa cada tiempo apartado, la
    huella de cada archivo y, si el contenido difiere, las primeras rutas distintas."""
    p, h = RR._cargar(producido), RR._cargar(historico)
    instalada = RR._sin_operativos(p) == RR._sin_operativos(h)
    p2, tp, mp = _traza_sred(p)
    h2, th, mh = _traza_sred(h)
    forma = tp is not None and th is not None
    longitud = forma and len(tp) == len(th)
    cient = bool(longitud) and RR._sin_operativos(p2) == RR._sin_operativos(h2)
    orig = origen_sred(RR)
    adaptada = bool(orig["demostrado"] and forma and longitud and cient)
    dif = []
    if not cient:
        def hojas(x, r=""):
            if isinstance(x, dict):
                for k, v in x.items():
                    yield from hojas(v, r + "/" + str(k))
            elif isinstance(x, list):
                for i, v in enumerate(x):
                    yield from hojas(v, r + "/%d" % i)
            else:
                yield r, x
        a, b = dict(hojas(RR._sin_operativos(p2))), dict(hojas(RR._sin_operativos(h2)))
        dif = [{"ruta": k, "nuevo": a.get(k, "<ausente>"), "historico": b.get(k, "<ausente>")} for k in sorted(set(a) | set(b))
               if a.get(k, "<ausente>") != b.get(k, "<ausente>")][:20]
    return {"regla": SRED_TIEMPOS["regla"], "salida": salida, "igual": bool(instalada or adaptada),
            "por": "regla_instalada" if instalada else ("adaptacion" if adaptada else None), "origen": orig,
            "forma_nueva": mp or "conforme", "forma_historica": mh or "conforme", "entradas": [len(tp or []), len(th or [])],
            "misma_longitud": bool(longitud), "contenido_cientifico_igual": cient,
            "tiempos_apartados": {"nuevo": tp, "historico": th}, "diferencias_de_tiempo": sum(1 for x, y in zip(tp or [], th or []) if x != y),
            "estado": {"nuevo": p.get("estado") if isinstance(p, dict) else None, "historico": h.get("estado") if isinstance(h, dict) else None},
            "huellas": {"nuevo": sha(producido), "historico": sha(historico)}, "diferencias_de_contenido": dif,
            "igual_con_la_regla_instalada_sin_adaptacion": instalada}


def _salidas_sred(RR, OPm) -> dict:
    """{bytes autenticados de la salida histórica: salida} de los dos comandos SRED de plan_sred, tras comprobar que son los previstos."""
    cs = OPm.plan_sred(T)["comandos"]
    need(len(cs) == 2 and all((c["entrega"], c["modulo"]) == (SRED_TIEMPOS["entrega"], SRED_TIEMPOS["modulo"]) for c in cs)
         and tuple(c["registro"] for c in cs) == SRED_TIEMPOS["registros"]
         and tuple(tuple(RR.salidas_del_comando(c, T)) for c in cs) == tuple((s,) for s in SRED_TIEMPOS["salidas"]),
         "SRED_RUTA_DISTINTA_DE_LA_PREVISTA (IGUALDAD-SRED-TIEMPOS-v1 no se aplica)")
    return {RR._aut(T, SRED_TIEMPOS["entrega"], s): s for s in SRED_TIEMPOS["salidas"]}


@contextlib.contextmanager
def regla_sred(RR, OPm, tarea: str):
    """Solo en R1-A1, y solo para las dos salidas SRED previstas: mientras dura la validación, r1_rutas.igual_a_historica = igualdad_sred
    para esas dos salidas (identificadas por los bytes autenticados de la histórica) y la regla instalada para cualquier otra; se restaura
    siempre. En otra tarea no cambia nada (None)."""
    if tarea != SRED_TIEMPOS["tarea"]:
        yield None
        return
    hist = _salidas_sred(RR, OPm)
    need(sys.modules.get("r1_rutas") is RR, "R1_RUTAS_DISTINTO_DEL_DE_LA_VALIDACION")
    instalada, informe = RR.igual_a_historica, {"regla": SRED_TIEMPOS["regla"], "aplicada": False, "salidas": {}, "llamadas": {}}

    def igual(producido: bytes, historico: bytes) -> bool:
        s = hist.get(historico)
        if s is None:
            return instalada(producido, historico)
        r = igualdad_sred(RR, s, producido, historico)
        informe["salidas"][s] = r
        informe["llamadas"][s] = informe["llamadas"].get(s, 0) + 1
        informe["aplicada"] = True
        return r["igual"]
    RR.igual_a_historica = igual
    try:
        yield informe
    finally:
        RR.igual_a_historica = instalada
        informe["igual"] = bool(informe["salidas"]) and set(informe["salidas"]) == set(SRED_TIEMPOS["salidas"]) and all(
            r["igual"] for r in informe["salidas"].values())


# ================================================================================================ CIERRE-MUESTRA-R1D-v1 (solo R1-D)
# Autorizada por el autor el 2026-11-21, tras el diagnóstico sin efecto DIAG-R1D-MUESTRA-v1 (D:\paso3\diag_r1d_20261121). Tres partes:
# (a) MUESTRA. orquestador_b.ejecutar exige que la muestra sea su propio cierre por dependencias (MUESTRA_NO_CERRADA_POR_DEPENDENCIAS) y los
#     agregados de D dependen de 640 hojas ci-d/ci-f que la cobertura asigna a R1-B1/B2/B3. La muestra de D pasa a ser ese cierre
#     (1.088 + 640). Antes de calcular se exige: que las 640 sean hojas ci-d/ci-f de las rutas de recuperación histórica; que la cobertura
#     autenticada asigne cada uno de sus 1.280 extremos exactamente a una de R1-B1/B2/B3; que las tres estén aceptadas en esta ejecución; y
#     que cada fuente inyectada sea el producto aceptado (huella = árbol del enlace). Si falla, el rechazo es controlado y no se calcula.
# (b) COBERTURA. Los 1.280 extremos son DEPENDENCIAS VERIFICADAS de B1/B2/B3 y se cuentan aparte de los 1.856 extremos propios de D y de
#     los 320 subproductos ci-df inf. Cada uno debe estar presente, ser terminal, venir de la recuperación sin recálculo, tener G, estado y
#     punto iguales al producto aceptado y pasar la verificación instalada. La muestra debe ser requeridas + dependencias. El resto sigue el
#     cuerpo de PilaR1S6.cobertura_orquestador; la diferencia es que TODO requerido debe igualar su fila de la referencia compuesta (y la
#     verificación histórica, cuando juzga, no puede contradecirse).
# (c) REFERENCIA COMPUESTA de los 1.856:
#     - ci_df_sup: las filas de la tabla autenticada que cita la cobertura (hojas_ci_v4, lima1913).
#     - country_global: el agregado E13 v4 (global_extreme_v4.py 4e841874…: ci_de y Referencia.fila; sup [max L, max U], inf [min L,
#       min U], desempate d < df < f, país, claim_id; pass si U − L <= 1e-4 y todas las hojas convergidas) sobre las hojas que el plan
#       histórico autenticado (lima1351, plan_1728_v3.json) asigna a cada agregado según su escenario. Un escenario no admite hojas de
#       otro: una mezcla es un rechazo explícito.
#     - conditional_none: la referencia es DERIVADA (E13 v4 nunca construyó esos agregados). La lectura literal de cg_hojas, que también
#       pone d/df/f en conditional_none, se conserva como dato informado y no se usa como criterio.
#     - Comparador: exige G exacto en sus dos límites, la hoja ganadora, el punto (mismas claves y valores) y el estado. El índice de
#       contexto se coteja donde el testigo producido lo registra (ganadora df). Su ausencia se documenta (ganadora d/f: el testigo
#       recuperado solo tiene el punto).
# Mientras dura la validación de R1-D, en la INSTANCIA de la pila se sustituyen referencia_cobertura y cobertura_orquestador; al terminar se
# restauran siempre. registro_productivo.generar_r1 se llama sin cambios. fam02-comparar lo recalcula todo sobre los bytes guardados.
R1D_CIERRE = {"regla": "CIERRE-MUESTRA-R1D-v1", "tarea": "R1-D", "autorizacion": "autor, 2026-11-21 (tras DIAG-R1D-MUESTRA-v1)",
              "dependencias_de": ("R1-B1", "R1-B2", "R1-B3"),
              "rutas_de_dependencia": ("recuperacion_historica_XDD_PRV", "recuperacion_historica_CAN"),
              "plan": P1351 + ("demo/orquestador3/plan_1728_v3.json",),
              "plan_sha256": "a282e0ec02eb5a89f94b49456563f2e9234b8364634f402f398ce1e04244bf3c",
              "regla_e13": {"archivo": "codigo/global_extreme_v4.py", "sha256": "4e841874ca5b71c86a55fe8f64b386aacfcceb4956b7d2fa01ba23b7aba7680e",
                            "funciones": "ci_de (l. 107-111) y Referencia.fila (l. 614-638), reproducidas aquí",
                            "registrado_en": "inventarios de lima1913 y lima1351 (el archivo no se distribuye en el paquete)"},
              "regla_citada": "E13 v4 (codigo/global_extreme_v4.py: ci_de; agregado max/min de L y U de las hojas)",
              "T2_G": 1e-4, "orden_j": {"d": 0, "df": 1, "f": 2},
              "disponibilidad": {"d": "domestic_unchanged", "df": "conditional_full", "f": "conditional_full"},          # = ci_de
              "escenarios": {"conditional_full": ("d", "df", "f"), "conditional_none": ("d",)},                           # hojas admitidas
              "productos": {"R1-B3": {"XDD": "paquete/demo/extremos/extremos_G_d.json", "CAN": "paquete/demo/extremos/extremos_G_f.json"},
                            "R1-B1": {"G": "paquete/demo/hito2/produccion_inf_G_cid_G.json"},
                            "R1-B2": {"N": "paquete/demo/hito2/produccion_inf_G_cid_N.json"}}}
R1D_NOTA_CN = ("referencia DERIVADA: E13 v4 no construyó agregados conditional_none (su selección fuentes_df solo arma países conditional_full "
               "y sus globales); se aplica la regla E13 v4 a las hojas que el plan histórico asigna a esos agregados (la hoja d domestic_unchanged "
               "de cada país). La lectura literal de cg_hojas (d, df y f también en conditional_none) se informa y no es criterio")


def _finito(v) -> bool:
    return _numero(v) and math.isfinite(v)


def _entero(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _punto_exacto(a, b) -> bool:
    """Mismas claves y mismos valores (números finitos)."""
    return (isinstance(a, dict) and isinstance(b, dict) and bool(a) and set(a) == set(b)
            and all(_finito(a[k]) and _finito(b[k]) and float(a[k]) == float(b[k]) for k in a))


def _punto_en_claves(r: dict, pt) -> bool:
    """Punto del testigo igual al de referencia en las claves de esta (criterio de orquestador_b.verificar / igual_a_referencia)."""
    try:
        tp = (r.get("testigo") or {}).get("punto") or {}
        return isinstance(pt, dict) and bool(pt) and {k: float(v) for k, v in tp.items() if k in pt} == {k: float(v) for k, v in pt.items()}
    except (TypeError, ValueError, AttributeError):
        return False


def _ci_de(campos_, a: str, j: str) -> str:
    """= global_extreme_v4.ci_de (4e841874…, l. 107-111): hoja ci del instrumento j del país de la afirmación country a."""
    f = campos_(a)
    return ":".join(["CLM", f["pid"], f["kind"], "ci", f["pais"], j, R1D_CIERRE["disponibilidad"][j], f["dis"]] + list(f["resto"]))


def _agregado_e13(hs: list, sentido: str) -> dict:
    """= global_extreme_v4.Referencia.fila (l. 614-638) sobre filas de hojas {claim_id, instrumento, pais, L, U, convergida, punto,
    indice_contexto}: sup [max L, max U], inf [min L, min U]; ganadora con desempate d < df < f, país, claim_id; pass si U − L <= T2_G y todas
    las hojas convergidas."""
    oj = R1D_CIERRE["orden_j"]
    if sentido == "sup":
        L, U = max(x["L"] for x in hs), max(x["U"] for x in hs)
        real = min(hs, key=lambda x: (-x["L"], oj[x["instrumento"]], x["pais"], x["claim_id"]))
    else:
        L, U = min(x["L"] for x in hs), min(x["U"] for x in hs)
        real = min(hs, key=lambda x: (x["U"], oj[x["instrumento"]], x["pais"], x["claim_id"]))
    estado = "pass" if (U - L <= R1D_CIERRE["T2_G"] and all(x["convergida"] for x in hs)) else "incomplete"
    return {"L": L, "U": U, "estado": estado, "hoja_ganadora": real["claim_id"], "instrumento_ganador": real["instrumento"], "punto": dict(real["punto"]),
            "indice_contexto": real["indice_contexto"], "hojas": sorted(x["claim_id"] for x in hs)}


def _fila_hoja_valida(x: dict, h: str, s: str) -> None:
    need(x.get("testigo") == "definitivo", "REFERENCIA_R1D_HOJA_NO_DEFINITIVA: %s|%s" % (h, s))
    p = x.get("punto")
    need(_finito(x.get("L")) and _finito(x.get("U")) and x["L"] <= x["U"] and isinstance(p, dict) and bool(p) and all(_finito(v) for v in p.values())
         and _entero(x.get("indice_contexto")) and x.get("estado") in ("convergido", "detenido"), "REFERENCIA_R1D_HOJA_INVALIDA: %s|%s" % (h, s))


def _hoja_e13(campos_, h: str, s: str, hv4: dict) -> dict:
    x = hv4.get((h, s))
    need(x is not None, "REFERENCIA_R1D_HOJA_AUSENTE: %s|%s" % (h, s))
    _fila_hoja_valida(x, h, s)
    c = campos_(h)
    return {"claim_id": h, "instrumento": c["j"], "pais": c["pais"], "L": x["L"], "U": x["U"], "convergida": x["estado"] == "convergido",
            "punto": x["punto"], "indice_contexto": x["indice_contexto"]}


def _hojas_del_pais(campos_, plan: dict, a: str) -> list:
    """Hojas que el plan histórico asigna a la afirmación country a, comprobadas: cada una es la hoja ci_de de a (mismo pid, kind, país,
    diseño y resto; disponibilidad = la de su instrumento), del escenario de a (si no, MEZCLA_DE_ESCENARIOS), sin repetir, y en conjunto las
    del escenario (conditional_full: d, df, f; conditional_none: d)."""
    f, c = plan.get(a), campos_(a)
    need(f is not None, "REFERENCIA_R1D_PLAN_SIN_AGREGADO: %s" % a)
    esc = c["scen"]
    need(f.get("familia") == "c" and f.get("escenario") == esc and f.get("diseno") == c["dis"] and esc in R1D_CIERRE["escenarios"],
         "REFERENCIA_R1D_ESTRUCTURA_DISTINTA: fila del plan de %s" % a)
    hs = list(f.get("dependencias") or [])
    for h in hs:
        ch = campos_(h)
        need(ch["fam"] == "ci" and (ch["pid"], ch["kind"], ch["pais"], ch["dis"], ch["resto"]) == (c["pid"], c["kind"], c["pais"], c["dis"], c["resto"]),
             "REFERENCIA_R1D_HOJA_INVALIDA: %s no es hoja de %s" % (h, a))
        need(ch["j"] in R1D_CIERRE["disponibilidad"] and ch["avail"] == R1D_CIERRE["disponibilidad"][ch["j"]], "REFERENCIA_R1D_HOJA_INVALIDA: %s fuera de ci_de" % h)
        need(ch["j"] in R1D_CIERRE["escenarios"][esc], "REFERENCIA_R1D_MEZCLA_DE_ESCENARIOS: hoja %s (%s) en %s (%s)" % (h, ch["avail"], a, esc))
    need(len(set(hs)) == len(hs) and sorted(hs) == sorted(_ci_de(campos_, a, j) for j in R1D_CIERRE["escenarios"][esc]),
         "REFERENCIA_R1D_PLAN_DISTINTO_DE_LA_REGLA: hojas de %s" % a)
    return hs


def _hojas_del_agregado(campos_, plan: dict, a: str) -> list:
    """Hojas del agregado a: las de su país (country) o la unión de las de sus países (global), todos del MISMO escenario, pid, kind,
    diseño y resto que a."""
    c = campos_(a)
    if c["fam"] == "c":
        return sorted(_hojas_del_pais(campos_, plan, a))
    f = plan.get(a)
    need(f is not None, "REFERENCIA_R1D_PLAN_SIN_AGREGADO: %s" % a)
    need(f.get("familia") == "g" and f.get("escenario") == c["scen"] and f.get("diseno") == c["dis"], "REFERENCIA_R1D_ESTRUCTURA_DISTINTA: fila del plan de %s" % a)
    paises = list(f.get("dependencias") or [])
    need(paises and len(set(paises)) == len(paises), "REFERENCIA_R1D_ESTRUCTURA_DISTINTA: países de %s" % a)
    hs = []
    for p in paises:
        cp = campos_(p)
        need(cp["fam"] == "c", "REFERENCIA_R1D_ESTRUCTURA_DISTINTA: componente %s de %s" % (p, a))
        need(cp["scen"] == c["scen"], "REFERENCIA_R1D_MEZCLA_DE_ESCENARIOS: país %s (%s) en %s (%s)" % (p, cp["scen"], a, c["scen"]))
        need((cp["pid"], cp["kind"], cp["dis"], cp["resto"]) == (c["pid"], c["kind"], c["dis"], c["resto"]), "REFERENCIA_R1D_ESTRUCTURA_DISTINTA: país %s de %s" % (p, a))
        hs += _hojas_del_pais(campos_, plan, p)
    need(len(set(hs)) == len(hs), "REFERENCIA_R1D_ESTRUCTURA_DISTINTA: hojas repetidas en %s" % a)
    return sorted(hs)


def construir_referencia_r1d(campos_, req, ref_d, cg_hojas, hv4_raw: bytes, plan_raw: bytes) -> dict:
    """(c) Referencia compuesta de los requeridos de R1-D sobre bytes ya autenticados: {"cita", "filas" {(afirmación, sentido): fila},
    "literal_cg_hojas" (solo informativa)}. Cualquier incoherencia -> Fam02Error con un código REFERENCIA_R1D_*."""
    need(isinstance(ref_d, dict) and set(ref_d) == {"ci_df_sup", "country_global"}, "REFERENCIA_R1D_ESTRUCTURA_DISTINTA: claves de la referencia de R1-D")
    cita = (ref_d.get("ci_df_sup") or {}).get("cita")
    cg = ref_d.get("country_global") or {}
    need(isinstance(cita, dict) and all(isinstance(cita.get(k), str) for k in ("entrega", "inventario_sha256", "archivo", "sha256")),
         "REFERENCIA_R1D_ESTRUCTURA_DISTINTA: cita de ci_df_sup")
    need(cg.get("cita_hojas") == cita, "REFERENCIA_R1D_ESTRUCTURA_DISTINTA: cita_hojas de country_global distinta de la cita de ci_df_sup")
    need(cg.get("regla") == R1D_CIERRE["regla_citada"], "REFERENCIA_R1D_REGLA_DISTINTA: %s" % cg.get("regla"))
    need(sha(hv4_raw) == cita["sha256"], "REFERENCIA_R1D_NO_AUTENTICADA: tabla de hojas %s" % cita["archivo"])
    need(sha(plan_raw) == R1D_CIERRE["plan_sha256"], "REFERENCIA_R1D_PLAN_NO_AUTENTICADO: %s" % R1D_CIERRE["plan"][2])
    try:
        filas_v4, filas_plan = json.loads(hv4_raw)["filas"], json.loads(plan_raw)["filas"]
        hv4, plan = {}, {}
        for x in filas_v4:
            k = (x["hoja"], x["sentido"])
            need(k not in hv4, "REFERENCIA_R1D_HOJA_DUPLICADA: %s|%s" % k)
            hv4[k] = x
        for x in filas_plan:
            need(x["afirmacion"] not in plan, "REFERENCIA_R1D_ESTRUCTURA_DISTINTA: afirmación repetida en el plan %s" % x["afirmacion"])
            plan[x["afirmacion"]] = x
    except (ValueError, KeyError, TypeError) as ex:
        raise Fam02Error("REFERENCIA_R1D_ESTRUCTURA_DISTINTA: %s: %s" % (type(ex).__name__, ex))
    filas, lit, por_esc, lit_rep = {}, {}, Counter(), {}
    req = sorted({tuple(x) for x in req})
    need(req, "REFERENCIA_R1D_INCOMPLETA: sin requeridos")
    for a, s in req:
        c = campos_(a)
        if c["fam"] == "ci":
            need(c["j"] == "df" and s == "sup", "REFERENCIA_R1D_INCOMPLETA: requerido sin regla de referencia %s|%s" % (a, s))
            x = hv4.get((a, s))
            need(x is not None, "REFERENCIA_R1D_HOJA_AUSENTE: %s|%s" % (a, s))
            _fila_hoja_valida(x, a, s)
            filas[(a, s)] = dict(x, comparador="hoja_citada")
            continue
        need(c["fam"] in ("c", "g") and c["scen"] in R1D_CIERRE["escenarios"], "REFERENCIA_R1D_INCOMPLETA: requerido sin regla de referencia %s|%s" % (a, s))
        hs = _hojas_del_agregado(campos_, plan, a)
        ag = _agregado_e13([_hoja_e13(campos_, h, s, hv4) for h in hs], s)
        filas[(a, s)] = {"L": ag["L"], "U": ag["U"], "punto": ag["punto"], "indice_contexto": ag["indice_contexto"], "testigo": "definitivo",
                         "estado": "convergido" if ag["estado"] == "pass" else "detenido", "estado_e13": ag["estado"], "hoja_ganadora": ag["hoja_ganadora"],
                         "instrumento_ganador": ag["instrumento_ganador"], "componentes": sorted(plan[a]["dependencias"]), "hojas": hs,
                         "ruta": plan[a]["ruta"], "escenario": c["scen"], "derivada": c["scen"] == "conditional_none", "comparador": "agregado_e13"}
        por_esc["%s_%s" % ({"c": "country", "g": "global"}[c["fam"]], c["scen"])] += 1
        # lectura LITERAL de cg_hojas (informativa): mismas filas autenticadas, hojas según la cobertura
        r_ = lit_rep.setdefault(c["scen"], Counter())
        r_["agregados"] += 1
        hl = (cg_hojas or {}).get(eid(a, s)) if isinstance(cg_hojas, dict) else None
        if not isinstance(hl, list) or not hl or not all((h, s) in hv4 for h in hl):
            r_["sin_hojas_en_la_tabla"] += 1
            continue
        r_["hojas_iguales_a_las_del_plan"] += sorted(hl) == hs
        try:
            al = _agregado_e13([_hoja_e13(campos_, h, s, hv4) for h in hl], s)
        except (Fam02Error, KeyError, TypeError):
            r_["no_agregables"] += 1
            continue
        lit[(a, s)] = {"L": al["L"], "U": al["U"], "hoja_ganadora": al["hoja_ganadora"], "punto": al["punto"],
                       "estado": "convergido" if al["estado"] == "pass" else "detenido"}
    lista = [[a, s, filas[(a, s)]] for a, s in sorted(filas)]
    n_sup = sum(1 for f in filas.values() if f["comparador"] == "hoja_citada")
    cita_c = {"regla": R1D_CIERRE["regla"], "filas": len(filas), "filas_sha256": sha(canon(lista)),
              "ci_df_sup": {"cita": cita, "filas": n_sup, "regla": "fila de la tabla citada por la cobertura (igual_a_referencia instalado, punto completo y estado)"},
              "country_global": {"regla_citada": cg.get("regla"), "regla_e13": R1D_CIERRE["regla_e13"], "cita_hojas": cita,
                                 "plan": {"entrega": P1351[0], "inventario_sha256": P1351[1], "archivo": R1D_CIERRE["plan"][2], "sha256": sha(plan_raw)},
                                 "hojas": "las que el plan histórico asigna a cada agregado según su escenario (conditional_full: d, df y f de cada país; "
                                          "conditional_none: d domestic_unchanged)",
                                 "agregados": len(filas) - n_sup, "por_escenario": dict(por_esc), "conditional_none": R1D_NOTA_CN,
                                 "hojas_en_la_cobertura": cg.get("hojas"), "validacion_original": cg.get("validacion_original")},
              "lectura_literal_cg_hojas": {k: dict(v) for k, v in sorted(lit_rep.items())}}
    return {"cita": cita_c, "filas": filas, "literal_cg_hojas": lit}


def entradas_referencia_r1d(raiz_fuentes: Path | None = None) -> dict:
    """Bytes AUTENTICADOS de la referencia compuesta: entrada de R1-D y cg_hojas de la cobertura (lima1857), tabla de hojas que cita
    (hojas_ci_v4, lima1913) y plan histórico del orquestador (lima1351)."""
    try:
        cobj = json.loads(autenticado(*COBERTURA, raiz_fuentes=raiz_fuentes))
        ref_d = ({t["tarea"]: t for t in cobj["tareas"]}.get("R1-D") or {}).get("referencia")
        cita = ((ref_d or {}).get("ci_df_sup") or {}).get("cita") or {}
        hv4_raw = autenticado(cita["entrega"], cita["inventario_sha256"], cita["archivo"], raiz_fuentes=raiz_fuentes)
    except (Fam02Error, OSError, KeyError, TypeError, ValueError) as ex:
        raise Fam02Error("REFERENCIA_R1D_NO_AUTENTICADA: %s: %s" % (type(ex).__name__, ex))
    try:
        plan_raw = autenticado(*R1D_CIERRE["plan"], raiz_fuentes=raiz_fuentes)
    except (Fam02Error, OSError, KeyError, TypeError, ValueError) as ex:
        raise Fam02Error("REFERENCIA_R1D_PLAN_NO_AUTENTICADO: %s: %s" % (type(ex).__name__, ex))
    return {"ref_d": ref_d, "cg_hojas": cobj.get("cg_hojas"), "hv4_raw": hv4_raw, "plan_raw": plan_raw}


def referencia_r1d(P, raiz_fuentes: Path | None = None) -> dict:
    return construir_referencia_r1d(P.OB.campos, [tuple(x) for x in type(P).requeridos_orquestador(P, R1D_CIERRE["tarea"])],
                                    **entradas_referencia_r1d(raiz_fuentes))


def _referencia_o_invalida(P) -> dict:
    """La referencia compuesta, o su rechazo explícito: {"cita": None, "filas": {}, "invalida": código}."""
    try:
        return referencia_r1d(P)
    except Fam02Error as ex:
        return {"cita": None, "filas": {}, "literal_cg_hojas": {}, "invalida": str(ex)}
    except (OSError, KeyError, TypeError, ValueError) as ex:
        return {"cita": None, "filas": {}, "literal_cg_hojas": {}, "invalida": "REFERENCIA_R1D_ESTRUCTURA_DISTINTA: %s: %s" % (type(ex).__name__, ex)}


def comparar_r1d(P, r: dict, fila: dict) -> dict:
    """Comparador de CIERRE-MUESTRA-R1D-v1 de un extremo propio de D con su fila de la referencia compuesta ({campo: bool}, «igual» = todos).
    ci_df_sup: igual_a_referencia instalado (G, punto en las claves de la cita, índice, testigo definitivo) + punto completo + estado + ruta.
    country/global: G exacto en ambos límites, hoja ganadora, punto completo, estado, componentes y ruta del plan; índice de contexto
    cotejado si el testigo lo registra; si no, solo se admite con ganadora d/f (testigo recuperado, solo punto). «indice_cotejado» informa."""
    t = r.get("testigo") if isinstance(r.get("testigo"), dict) else {}
    G = r.get("G")
    q = {"G": isinstance(G, list) and len(G) == 2 and _finito(G[0]) and _finito(G[1]) and _finito(fila.get("L")) and _finito(fila.get("U"))
              and G[0] == fila["L"] and G[1] == fila["U"],
         "punto": _punto_exacto(t.get("punto"), fila.get("punto")),
         "estado": r.get("estado") == fila.get("estado")}
    if fila.get("comparador") == "hoja_citada":
        q["igual_a_referencia_instalado"] = type(P).igual_a_referencia(r, fila)
        q["indice_contexto"] = _entero(t.get("indice_contexto")) and t["indice_contexto"] == fila.get("indice_contexto")
        q["ruta"] = r.get("ruta") == "calculo_v5_ci_df"
    else:
        q["hoja_ganadora"] = r.get("hoja_ganadora") == fila.get("hoja_ganadora")
        q["componentes"] = sorted(r.get("componentes") or []) == fila.get("componentes")
        q["ruta"] = r.get("ruta") == fila.get("ruta")
        q["indice_contexto"] = (_entero(t["indice_contexto"]) and t["indice_contexto"] == fila.get("indice_contexto")) if "indice_contexto" in t else (
            fila.get("instrumento_ganador") in ("d", "f"))
    q["igual"] = all(q.values())
    q["indice_cotejado"] = "indice_contexto" in t
    return q


def _categoria_r1d(k: tuple, campos_) -> str:
    c = campos_(k[0])
    if c["fam"] == "ci":
        return "ci_%s_%s" % (c["j"], k[1])
    return "%s_%s" % ({"c": "country", "g": "global"}[c["fam"]], {"conditional_full": "cf", "conditional_none": "cn"}.get(c["scen"], c["scen"]))


def cierre_r1d(P, cob: dict, afs: list) -> dict:
    """(a) SIN CÁLCULO: cierre por dependencias (orquestador_b.cierre con las dependencias de la autoridad) de las afirmaciones de D y
    comprobación de las que no son de D: hojas ci-d/ci-f de las rutas de recuperación, cada extremo asignado por la cobertura autenticada
    exactamente a una de R1-B1/B2/B3, y la muestra ampliada cerrada."""
    OB = P.OB
    dps = OB.dependencias(P.ctx.claims)
    orden = OB.cierre(list(afs), dps)
    fuera = sorted(set(orden) - set(afs))
    tarea_de = {}
    for k, v in cob.items():
        for i in v.get("ids") or []:
            tarea_de.setdefault(i, []).append(k)
    ext = {"%s|%s" % (c, s): sorted(tarea_de.get(eid(c, s), [])) for c in fuera for s in ("sup", "inf")}
    no_ci = [c for c in fuera if not (OB.campos(c)["fam"] == "ci" and OB.campos(c)["j"] in ("d", "f"))]
    otra_ruta = [c for c in fuera if OB.ruta_de(c) not in R1D_CIERRE["rutas_de_dependencia"]]
    fuera_b = [k for k, v in ext.items() if not (len(v) == 1 and v[0] in R1D_CIERRE["dependencias_de"])]
    muestra = sorted(set(afs) | set(fuera))
    cerrada = OB.cierre(muestra, dps) == orden and sorted(orden) == muestra
    cods = [c for c, malo in (("DEPENDENCIA_QUE_NO_ES_HOJA_CI_D_O_CI_F", no_ci), ("DEPENDENCIA_CON_OTRA_RUTA", otra_ruta),
                              ("EXTREMO_DE_DEPENDENCIA_FUERA_DE_B1_B2_B3", fuera_b), ("MUESTRA_AMPLIADA_NO_CERRADA", not cerrada)) if malo]
    return {"regla": R1D_CIERRE["regla"], "afirmaciones_de_D": len(afs), "dependencias": fuera, "muestra": muestra, "tarea_de": ext,
            "por_ruta": dict(Counter(OB.ruta_de(c) for c in fuera)),
            "extremos_por_tarea_y_sentido": dict(Counter("%s|%s" % (v[0] if len(v) == 1 else "+".join(v) or "(ninguna)", k.rsplit("|", 1)[1]) for k, v in ext.items())),
            "codigos": cods, "ejemplos": {"no_ci": no_ci[:5], "otra_ruta": otra_ruta[:5], "fuera_de_B": fuera_b[:5]}}


def fuentes_r1d(fuentes_d: dict, acept: dict, prov: dict) -> tuple:
    """(a) SIN CÁLCULO: cada fuente que tarea_r1.hojas_y_fuentes_de inyecta es un archivo de un producto aceptado en esta ejecución con la huella
    de su árbol aceptado; las de las dependencias (todas salvo SRED) vienen exactamente de R1-B1/B2/B3."""
    out, cods = {}, []
    for (clave, rel), ruta in sorted(fuentes_d.items()):
        x = next((t for t, d0 in sorted(acept.items()) if Path(ruta).resolve().is_relative_to(Path(d0).resolve())), None)
        if x is None:
            cods.append("FUENTE_FUERA_DE_LOS_PRODUCTOS_ACEPTADOS:%s:%s" % (clave, rel))
            continue
        r_ = Path(ruta).resolve().relative_to(Path(acept[x]).resolve()).as_posix()
        h = sha(Path(ruta).read_bytes())
        out["%s:%s" % (clave, rel)] = {"tarea": x, "archivo": r_, "sha256": h, "igual_al_arbol_del_enlace": prov[x]["arbol"].get(r_) == h}
    if any(not v["igual_al_arbol_del_enlace"] for v in out.values()):
        cods.append("FUENTE_INYECTADA_DISTINTA_DEL_PRODUCTO_ACEPTADO")
    if {v["tarea"] for k, v in out.items() if not k.startswith("PRV:demo/hito2/sred_")} != set(R1D_CIERRE["dependencias_de"]):
        cods.append("FUENTES_DE_LAS_DEPENDENCIAS_INCOMPLETAS")
    return out, cods


def productos_r1d(acept: dict, prov: dict) -> tuple:
    """Productos aceptados de B1/B2/B3 que verifican las dependencias (bytes = árbol del enlace)."""
    prod, cods = {}, []
    for t, m in sorted(R1D_CIERRE["productos"].items()):
        for k, rel in sorted(m.items()):
            if t not in acept:
                cods.append("PRODUCTO_NO_ACEPTADO:%s" % t)
                continue
            try:
                raw = (Path(acept[t]) / rel).read_bytes()
                prod[k] = json.loads(raw)
            except (OSError, ValueError):
                cods.append("PRODUCTO_ILEGIBLE:%s:%s" % (t, rel))
                continue
            if prov[t]["arbol"].get(rel) != sha(raw):
                cods.append("PRODUCTO_DISTINTO_DE_SU_ACEPTACION:%s:%s" % (t, rel))
    return prod, cods


def dependencias_r1d(P, E: Path, RP, cob: dict) -> dict:
    """Dependencias de D para la cobertura: cierre (a) y productos ACEPTADOS de R1-B1/B2/B3 en la ejecución E (enlace local re-leído)."""
    acept, prov, rech = aceptados(Path(E), list(R1D_CIERRE["dependencias_de"]), RP)
    afs = sorted({c for c, _ in type(P).requeridos_orquestador(P, R1D_CIERRE["tarea"])})
    ci = cierre_r1d(P, cob, afs)
    prod, cods = productos_r1d(acept, prov)
    cods = ["DEPENDENCIA_NO_ACEPTADA_EN_LA_EJECUCION:%s:%s" % (t, m) for t, m in sorted(rech.items())] + ci["codigos"] + cods
    return {"afirmaciones": ci["dependencias"], "muestra": ci["muestra"], "tarea_de": ci["tarea_de"], "productos": prod, "codigos": cods,
            "aceptadas": {t: {k: prov[t][k] for k in ("arbol_sha256", "aceptacion_sha256")} for t in sorted(prov)}}


def esperado_dependencia_r1d(prod: dict, campos_, h: str, s: str) -> tuple:
    """(tarea, G, estado, punto) del extremo h|s en los productos aceptados de B1/B2/B3: lectura independiente de la de orquestador_b.ci_hist
    (ci-d sup: XDD de B3, p_max; ci-d inf: PRV de B1 (G) o B2 (N), punto_cota_superior; ci-f: CAN de B3, puntos C2)."""
    c = campos_(h)
    d, j = c["dis"], c["j"]
    if j == "d" and s == "sup":
        x = prod["XDD"]["afirmaciones"][h]
        return "R1-B3", list(x["sup_G"]), x["estado_sup"], prod["XDD"]["p_max"]
    if j == "d":
        x = prod[d]["afirmaciones"][h]
        return ("R1-B1" if d == "G" else "R1-B2"), list(x["inf_G"]), x["estado_inf"], x["punto_cota_superior"]
    x = prod["CAN"]["afirmaciones"][h]
    return "R1-B3", list(x[s + "_G"]), x["estado"], prod["CAN"]["puntos"]["sup_C2" if s == "sup" else "inf_C2"]


def cobertura_r1d(P, cd, verificacion_p, requeridos, muestra_p, referencia, deps: dict) -> dict:
    """(b) Contrato de aceptación de R1-D con CIERRE-MUESTRA-R1D-v1: cuerpo de PilaR1S6.cobertura_orquestador (resultados canónicos e
    íntegros, únicos, sin ajenos, subproductos aparte, requeridos presentes y terminales, muestra ligada a identidad.json), con:
    dependencias verificadas de B1/B2/B3 contadas aparte; muestra = requeridas + dependencias; TODO requerido igual a su fila de la
    referencia compuesta (comparar_r1d) sin que la verificación histórica, cuando juzga, lo contradiga; referencia inválida -> rechazo."""
    RS = sys.modules[type(P).__module__]
    OB = P.OB
    cd = Path(cd)
    C = object.__new__(OB.Corrida)
    C.d = cd
    req = {tuple(x) for x in requeridos}
    afs_req = {c for c, _ in req}
    recs, dup, malos = {}, [], []
    for f in sorted((cd / "resultados").glob("*.json")) if (cd / "resultados").exists() else []:
        try:
            r = json.loads(f.read_bytes())
            k = (r.get("afirmacion"), r.get("sentido"))
            if f.resolve() != C.f(*k).resolve():
                malos.append(f.name)
                continue
            C.leer(*k)
        except (ValueError, SystemExit, TypeError) as ex:
            malos.append("%s: %s" % (f.name, str(ex)[:80]))
            continue
        if k in recs:
            dup.append(k)
        recs[k] = r
    dep_afs = set(deps.get("afirmaciones") or [])
    ajenos = sorted(k for k in recs if k[0] not in afs_req and k[0] not in dep_afs)
    subproductos = sorted(k for k in recs if k[0] in afs_req and k not in req)
    faltan = sorted(req - set(recs))
    vb = Path(verificacion_p).read_bytes() if Path(verificacion_p).exists() else b"{}"
    filas = {(x.get("afirmacion"), x.get("sentido")): x for x in json.loads(vb).get("filas", [])}
    referencia = referencia or {}
    invalida = referencia.get("invalida")
    ref, lit = referencia.get("filas") or {}, referencia.get("literal_cg_hojas") or {}
    no_adm, no_val, sin_ref = [], [], []
    por_ref, por_ver = 0, 0
    rep, lit_rep, indice = {}, {}, Counter()
    for k in sorted(req & set(recs)):
        r, f, fr = recs[k], filas.get(k) or {}, ref.get(k)
        h = f.get("estado_historico", (fr or {}).get("estado"))
        h = RS.ESTADO_EQUIVALENTE.get(h, h)
        if r.get("estado") in RS.ESTADOS_NO_ADMISIBLES or r.get("estado") not in OB.TERMINALES or (h is not None and r.get("estado") != h):
            no_adm.append(k)
        cat = _categoria_r1d(k, OB.campos)
        rc_ = rep.setdefault(cat, Counter())
        rc_["total"] += 1
        v_orq = f.get("comparable") is True and f.get("ok") is True
        rc_["con_medicion_historica"] += f.get("comparable") is True
        if fr is None:
            sin_ref.append(k)
            no_val.append(k)
            continue
        q = comparar_r1d(P, r, fr)
        for kk, b in q.items():
            rc_[kk] += bool(b)
        if fr.get("comparador") == "agregado_e13":
            indice["agregados_con_indice_cotejado" if q["indice_cotejado"] else "agregados_sin_indice_en_el_testigo"] += 1
            if not q["indice_cotejado"]:
                indice["sin_indice_con_ganadora_%s" % fr.get("instrumento_ganador")] += 1
            lr = lit_rep.setdefault(fr["escenario"], Counter())
            lr["agregados"] += 1
            li = lit.get(k)
            lr["iguales_al_producto"] += bool(li) and r.get("G") == [li["L"], li["U"]] and r.get("hoja_ganadora") == li["hoja_ganadora"] and _punto_exacto(
                (r.get("testigo") or {}).get("punto"), li["punto"]) and r.get("estado") == li["estado"]
        else:
            indice["ci_df_sup_con_indice_cotejado"] += q["indice_cotejado"]
        if f.get("comparable") is True and not v_orq:            # la verificación histórica, cuando juzga, no se puede contradecir
            no_val.append(k)
        elif not q["igual"]:
            no_val.append(k)
        else:
            por_ref += 1
            por_ver += v_orq
    # ---- dependencias de B1/B2/B3 (aparte de los extremos propios)
    dep_k = sorted((a, s) for a in dep_afs for s in ("sup", "inf"))
    dep_falt = [k for k in dep_k if k not in recs]
    dep_rep, dep_mal = {}, []
    for k in dep_k:
        r = recs.get(k)
        if r is None:
            continue
        try:
            tb, G, e, pt = esperado_dependencia_r1d(deps.get("productos") or {}, OB.campos, *k)
        except (KeyError, TypeError, ValueError):
            tb, G, e, pt = None, None, None, None
        f = filas.get(k) or {}
        q = {"tarea_de_la_cobertura": tb is not None and (deps.get("tarea_de") or {}).get("%s|%s" % k) == [tb],
             "terminal_admisible": r.get("estado") in OB.TERMINALES and r.get("estado") not in RS.ESTADOS_NO_ADMISIBLES,
             "recuperacion_sin_recalculo": r.get("ruta") == "recuperacion_historica" and r.get("recalculado") is False,
             "G_igual_al_producto_aceptado": G is not None and r.get("G") == G,
             "estado_igual_al_producto_aceptado": e is not None and r.get("estado") == ("convergido" if e == "convergida" else "detenido"),
             "punto_igual_al_producto_aceptado": pt is not None and _punto_en_claves(r, pt),
             "verificacion_instalada_ok": f.get("comparable") is True and f.get("ok") is True}
        q["verificada"] = all(q.values())
        d_ = dep_rep.setdefault(tb or "(sin producto)", Counter())
        d_["extremos"] += 1
        for kk, b in q.items():
            d_[kk] += bool(b)
        if not q["verificada"]:
            dep_mal.append({"afirmacion": k[0], "sentido": k[1], **{kk: b for kk, b in q.items() if not b}})
    mraw = Path(muestra_p).read_bytes() if Path(muestra_p).exists() else b""
    esperada = sorted(afs_req | dep_afs)
    muestra_ok = bool(mraw) and json.loads(mraw).get("afirmaciones") == esperada and (not deps.get("muestra") or deps["muestra"] == esperada)
    ident = json.loads((cd / "identidad.json").read_bytes()) if (cd / "identidad.json").exists() else {}
    ident_ok = bool(mraw) and ident.get("muestra_sha256") == sha(mraw)
    cods = [c for c, v in (("SIN_REQUERIDOS", not req), ("REFERENCIA_COMPUESTA_INVALIDA:%s" % str(invalida).split(":")[0], invalida),
                           ("DEPENDENCIAS_DE_D_NO_DISPONIBLES", deps.get("codigos")), ("RESULTADO_NO_CANONICO_O_ALTERADO", malos),
                           ("RESULTADO_DUPLICADO", dup), ("RESULTADO_AJENO", ajenos), ("DEPENDENCIA_FALTANTE", dep_falt),
                           ("DEPENDENCIA_NO_VERIFICADA", dep_mal), ("REQUERIDO_FALTANTE", faltan), ("ESTADO_NO_ADMISIBLE", no_adm),
                           ("REQUERIDO_SIN_FILA_DE_REFERENCIA", sin_ref), ("REQUERIDO_NO_VALIDADO", no_val),
                           ("MUESTRA_DISTINTA_DE_LA_ASIGNACION_MAS_DEPENDENCIAS", not muestra_ok), ("IDENTIDAD_DE_MUESTRA_DISTINTA", not ident_ok)) if v]
    return {"regla": R1D_CIERRE["regla"], "cumple": not cods, "codigos": cods, "requeridos": len(req), "presentes": len(req & set(recs)),
            "faltan": [list(x) for x in faltan[:20]], "n_faltan": len(faltan), "ajenos": [list(x) for x in ajenos[:20]], "duplicados": [list(x) for x in dup[:20]],
            "no_canonicos": malos[:20], "no_admisibles": [list(x) for x in no_adm[:20]], "no_validados": [list(x) for x in no_val[:20]], "n_no_validados": len(no_val),
            "sin_fila_de_referencia": [list(x) for x in sin_ref[:20]], "subproductos": len(subproductos), "muestra_ok": muestra_ok, "identidad_muestra_ok": ident_ok,
            "validados_por_verificacion_historica": por_ver, "validados_por_referencia_citada": por_ref, "referencia": referencia.get("cita"),
            "referencia_invalida": invalida,
            "extremos_propios_de_D": {"total": len(req), "por_categoria": {c: dict(v) for c, v in sorted(rep.items())}},
            "indice_contexto": dict(indice, nota="cotejado donde el testigo producido lo registra (ganadora df); ausente donde la ganadora es d o f "
                                                 "(testigo recuperado de B1/B2/B3: solo punto), ausencia documentada"),
            "dependencias": {"regla": "dependencias verificadas de R1-B1/B2/B3 (no son extremos de D)", "extremos": len(dep_k),
                             "presentes": len(dep_k) - len(dep_falt), "verificadas": sum(v["verificada"] for v in dep_rep.values()),
                             "por_tarea": {t: dict(v) for t, v in sorted(dep_rep.items())}, "no_verificadas": dep_mal[:20], "n_no_verificadas": len(dep_mal),
                             "faltantes": [list(x) for x in dep_falt[:20]], "codigos": deps.get("codigos") or [], "aceptadas": deps.get("aceptadas")},
            "lectura_literal_cg_hojas": {"nota": R1D_NOTA_CN, "por_escenario": {e: dict(v) for e, v in sorted(lit_rep.items())},
                                         "hojas": (referencia.get("cita") or {}).get("lectura_literal_cg_hojas")}}


@contextlib.contextmanager
def regla_r1d(P, RP, salida: Path, tarea: str):
    """Solo en R1-D: mientras dura registro_productivo.generar_r1, la INSTANCIA de la pila usa la referencia compuesta (o su rechazo explícito)
    y cobertura_r1d con las dependencias de B1/B2/B3 aceptadas en la ejecución de `salida`; se restaura siempre. Otra tarea: None."""
    if tarea != R1D_CIERRE["tarea"]:
        yield None
        return
    metodos = ("referencia_cobertura", "cobertura_orquestador")
    need(type(P).__name__ == "PilaR1S6" and not set(metodos) & set(vars(P)), "PILA_YA_ADAPTADA")
    instaladas = tuple(getattr(type(P), m) for m in metodos)
    ref = _referencia_o_invalida(P)
    deps = dependencias_r1d(P, Path(salida).resolve().parent, RP, cobertura())
    informe = {"regla": R1D_CIERRE["regla"], "referencia": ref.get("cita"), "referencia_invalida": ref.get("invalida"),
               "dependencias": {"afirmaciones": len(deps["afirmaciones"]), "codigos": deps["codigos"], "aceptadas": deps["aceptadas"]},
               "llamadas": {m: 0 for m in metodos}}

    def referencia_cobertura(t):
        need(t == R1D_CIERRE["tarea"], "REGLA_R1D_FUERA_DE_R1-D: %s" % t)
        informe["llamadas"]["referencia_cobertura"] += 1
        return ref

    def cobertura_orquestador(cd, verificacion_p, requeridos, muestra_p, referencia=None):
        informe["llamadas"]["cobertura_orquestador"] += 1
        need(referencia is ref, "REFERENCIA_DISTINTA_DE_LA_COMPUESTA")
        c = cobertura_r1d(P, cd, verificacion_p, requeridos, muestra_p, referencia, deps)
        informe["cobertura"] = {k: c[k] for k in ("cumple", "codigos", "requeridos", "presentes", "subproductos", "validados_por_referencia_citada",
                                                  "validados_por_verificacion_historica")}
        return c
    P.referencia_cobertura, P.cobertura_orquestador = referencia_cobertura, cobertura_orquestador
    try:
        yield informe
    finally:
        for m in metodos:
            vars(P).pop(m, None)
        informe["restaurada"] = not set(metodos) & set(vars(P)) and tuple(getattr(type(P), m) for m in metodos) == instaladas


def rechazo_r1d(salida: Path, ctx, prov: dict, codigos: list, cierre_d: dict, t0: float, c0: float, rastro) -> dict:
    """(a) Rechazo CONTROLADO de R1-D antes del cálculo: ejecucion.json con exito=false y los códigos; sin cálculo, registro ni enlace."""
    ej = {"comando": "fam02-unidad", "tarea": R1D_CIERRE["tarea"], "exito": False,
          "naturaleza": "rechazo controlado de %s antes del cálculo (no se calculó nada)" % R1D_CIERRE["regla"],
          "reproduccion": all(p["reproduccion"] for p in prov.values()),
          "dependencias_consumidas": {x: {k: prov[x][k] for k in ("salida", "arbol_sha256", "aceptacion_sha256", "reproduccion")} for x in sorted(prov)},
          "identidad_contexto_sha256": getattr(ctx, "identity_sha256", None),
          "calculo": {"estado": "no_ejecutado", "rc_productor": None, "motivo": codigos[0]},
          "validacion": {"estado": "rechazada", "cumple": False, "codigos": ["CIERRE_MUESTRA_R1D_RECHAZADA"] + list(codigos)},
          "cierre_muestra_r1d": {k: v for k, v in (cierre_d or {}).items() if k not in ("dependencias", "muestra", "tarea_de")} | {"codigos": list(codigos)},
          "tiempos_s": {"total": round(time.time() - t0, 2), "cpu": round(time.process_time() - c0, 2)},
          "aceptacion": {"aceptada": False, "motivos": list(codigos)}}
    (salida / "archivos_leidos.json").write_bytes((json.dumps(rastro.informe(), ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    (salida / "ejecucion.json").write_bytes(json.dumps(ej, ensure_ascii=False, indent=1, sort_keys=True, default=list).encode("utf-8") + b"\n")
    return ej


def recomprobar_r1d(P, RP, nueva: Path) -> dict:
    """fam02-comparar de R1-D, SIN CÁLCULO: referencia compuesta, dependencias y cobertura de CIERRE-MUESTRA-R1D-v1 recalculadas sobre los
    bytes guardados (sin sustituir nada en la pila) y contrastadas con la cobertura registrada en el dictamen de la validación."""
    nueva = Path(nueva).resolve()
    ref = _referencia_o_invalida(P)
    deps = dependencias_r1d(P, nueva.parent, RP, cobertura())
    cob = cobertura_r1d(P, nueva / "paquete/corrida", nueva / "verificacion.json", type(P).requeridos_orquestador(P, R1D_CIERRE["tarea"]),
                        nueva / "paquete/muestra.json", ref, deps)
    try:
        reg_c = json.loads((nueva / "dictamen_validacion.json").read_bytes()).get("cobertura") or {}
    except (OSError, ValueError):
        reg_c = {}
    claves = ("regla", "cumple", "codigos", "requeridos", "presentes", "subproductos", "validados_por_referencia_citada", "validados_por_verificacion_historica",
              "extremos_propios_de_D", "indice_contexto", "lectura_literal_cg_hojas")
    distintas = [k for k in claves if reg_c.get(k) != cob.get(k)]
    distintas += [k for k in ("filas_sha256", "filas") if (reg_c.get("referencia") or {}).get(k) != (cob.get("referencia") or {}).get(k)]
    distintas += [k for k in ("extremos", "presentes", "verificadas", "por_tarea") if (reg_c.get("dependencias") or {}).get(k) != cob["dependencias"].get(k)]
    return {"regla": R1D_CIERRE["regla"], "calculo": "ninguno (bytes guardados)", "cumple": cob["cumple"] is True and not distintas,
            "igual_a_la_cobertura_registrada": not distintas, "distintas": distintas,
            "cobertura_recalculada": {k: cob.get(k) for k in claves + ("n_no_validados", "referencia", "referencia_invalida", "muestra_ok", "identidad_muestra_ok")}
            | {"dependencias": {k: v for k, v in cob["dependencias"].items() if k != "aceptadas"}}}


# ================================================================================================ SAN-RUTAS-v1 (registros de lanzamiento)
SAN_RUTAS = ("SAN-RUTAS-v1 (saneamiento del paquete público, el de FAM01; no es una regla científica). Los registros de lanzamiento "
             "históricos (logs/**.tarea.json) se publican con el prefijo absoluto de la raíz del proyecto quitado de «cwd» y del lanzador de "
             "«comando»; módulo, argumentos y demás campos sin cambios (extraccion/extraer_fam02.sanear_registro lo comprueba contra el "
             "original, que no se distribuye). fuentes_fam02.json declara de cada copia pública su sha256 y el de origen (sha256_origen). "
             "r1_rutas._aut acepta una copia pública solo si sus bytes tienen la huella pública declarada y el inventario ANCLADO de su "
             "entrega lista la huella de origen declarada; cualquier otro archivo se autentica sin cambios.")


def publicas() -> dict:
    """{(entrega, ruta): (sha256 público, sha256 de origen)} de las copias públicas declaradas en fuentes_fam02.json."""
    fu = json.loads((BASE / "fuentes_fam02.json").read_bytes())
    pref = "nucleo_s6/raiz/tmp/"
    return {tuple(x["archivo"][len(pref):].split("/", 1)): (x["sha256"], x["sha256_origen"]) for x in fu["archivos"]
            if x.get("sha256_origen") and x["archivo"].startswith(pref)}


def adaptar_san_rutas(RR) -> int:
    """Adaptación de interfaz SAN-RUTAS-v1 de r1_rutas._aut (ver SAN_RUTAS). Devuelve el número de copias públicas declaradas."""
    if getattr(RR, "_aut_historico", None) is None:
        pub = publicas()
        orig = RR._aut

        def _aut(T_, entrega, rel, inv=None):
            try:
                return orig(T_, entrega, rel, inv)
            except RR.RutaError:
                par = pub.get((entrega, rel))
                if par is None:
                    raise
                raw = (Path(T_) / entrega / rel).read_bytes()
                x = (inv or RR._inv(Path(T_), entrega)).get(rel)
                RR.need(sha(raw) == par[0] and x is not None and (x["sha256"] if isinstance(x, dict) else x) == par[1],
                        "COPIA_PUBLICA_SIN_CORRESPONDENCIA", "%s/%s" % (entrega, rel))
                return raw
        RR._aut_historico, RR._aut, RR._san_rutas = orig, _aut, len(pub)
    return RR._san_rutas


def correspondencia_san_rutas(RR, raiz_fuentes: Path | None = None) -> dict:
    """Por copia pública declarada: bytes = huella pública, inventario ANCLADO de su entrega (r1_rutas.ENTREGAS) = huella de origen, y
    sin rutas absolutas."""
    import re
    R = Path(raiz_fuentes or T)
    absoluta = re.compile(rb"(?<![A-Za-z])[A-Za-z]:[\\/]|/[a-z]/Users/")
    mal = []
    pub = publicas()
    for (e, rel), (hp, ho) in sorted(pub.items()):
        inv_raw = (R / e / "audit/entrega.json").read_bytes()
        x = json.loads(inv_raw)["files"].get(rel)
        raw = (R / e / rel).read_bytes()
        if not (sha(inv_raw) == RR.ENTREGAS.get(e) and x is not None and (x["sha256"] if isinstance(x, dict) else x) == ho and sha(raw) == hp
                and not absoluta.search(raw)):
            mal.append("%s/%s" % (e, rel))
    return {"regla": "SAN-RUTAS-v1", "copias_publicas": len(pub), "con_correspondencia": len(pub) - len(mal), "sin_correspondencia": mal[:10]}


def referencias(tid: str, cob: dict, raiz_fuentes: Path | None = None) -> dict:
    """Referencias citadas por la cobertura para la tarea y sus subtareas, autenticadas (= tarea_r1.main l.77-93)."""
    R = Path(raiz_fuentes or T)
    refs = {k: v for k, v in cob.items() if k == tid or k.startswith(tid + "-")}
    out = {}
    for k, v in refs.items():
        c = (v.get("referencia") or {}).get("cita")
        if not c:
            out[k] = {"referencia": None, "nota": v.get("nota")}
            continue
        ir = (R / c["entrega"] / "audit/entrega.json").read_bytes()
        ivr = json.loads(ir)["files"]
        fb = (R / c["entrega"] / c["archivo"]).read_bytes()
        x = ivr.get(c["archivo"])
        out[k] = {"referencia": {kk: c[kk] for kk in ("entrega", "archivo", "sha256")},
                  "autenticada": sha(ir) == c["inventario_sha256"] and sha(fb) == c["sha256"] and x is not None and (x["sha256"] if isinstance(x, dict) else x) == c["sha256"]}
    if tid == "R1-V" and not refs:
        out[tid] = {"referencia": {"entrega": COBERTURA[0], "archivo": COBERTURA[2]}, "autenticada": True, "nota": "validación global: la cobertura R1 completa"}
    return out


def productores(tid: str, TR, raiz_fuentes: Path | None = None) -> dict:
    R = Path(raiz_fuentes or T)
    inv = json.loads((R / P1351[0] / "audit/entrega.json").read_bytes())["files"]
    out = {}
    for p in TR.PRODUCTORES.get(tid, []):
        b = (R / P1351[0] / p).read_bytes()
        x = inv.get(p)
        out[p] = {"sha256": sha(b), "autenticado_por_inventario": (x["sha256"] if isinstance(x, dict) else x) == sha(b)}
    return out


def plan_orquestador(P, out: Path, raiz_fuentes: Path | None = None) -> dict:
    """orquestador_b.plan bajo S6 (SIN cálculo: rutas, dependencias y cierre de las 1.728) contrastado con el plan histórico final
    autenticado de lima1351 (= tarea_r1.main l.115-125)."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        rc = P.OB.plan(str(out))
    hist = json.loads(autenticado(P1351[0], P1351[1], "demo/orquestador3/plan_1728_v3.json", raiz_fuentes))["filas"]
    nuevo = json.loads(out.read_bytes())["filas"]
    clave = lambda f: (f["afirmacion"], f["ruta"], tuple(f["dependencias"]))  # noqa: E731
    return {"rc": rc, "sha256": sha(out.read_bytes()), "filas": len(nuevo), "por_ruta": dict(Counter(f["ruta"] for f in nuevo)),
            "igual_al_historico_en_afirmaciones_rutas_y_dependencias": sorted(map(clave, nuevo)) == sorted(map(clave, hist))}


def entradas_ci_df(P, disenos=("G", "N")) -> dict:
    """SIN CÁLCULO: las entradas que orquestador_b.ejecutar lee ANTES del bucle de cálculo de las hojas ci-df (identidad: registro, código,
    puntos U citados por lima0754 y SRED; caja del grupo del plan C2; fuentes PRV/XDD/CAN), autenticadas con sus propias funciones."""
    E5 = P.modulo("codigo.extremos_G_df_v5")
    XD = P.modulo("codigo.extremos_dfd")
    P.modulo("codigo.extremos_G")
    P.modulo("codigo.demo.cobertura_mejorada")
    P.modulo("codigo.demo.universo")
    ident = P.OB.identidad(sha(b""), {"comprobacion": "sin calculo"})
    out = {"registro_sha256": ident["registro_sha256"], "codigo": ident["codigo"], "sred": ident["sred"], "puntos_U": {}, "grupos": {}, "fuentes": {}}
    for d in disenos:
        filas = 0
        for base, rel, h in ident["puntos_U"][d]:
            raw = (P.OB.T / base / rel).read_bytes()
            need(sha(raw) == h, "PUNTOS_U_ALTERADOS:%s" % rel)
            filas += sum(1 for f in json.loads(raw)["filas"] if f.get("admisible") and "U" in f and not f.get("incompatible"))
        out["puntos_U"][d] = {"fuentes": [[b, r, h] for b, r, h in ident["puntos_U"][d]], "puntos_admisibles": filas}
        g = XD.grupo(d, "df")
        out["grupos"][d] = {"grupo": g["grupo"], "plan_sha256": g["plan_sha256"]}
        E5.auth("PRV", "demo/hito2/sred_%s_df.json" % d)
        out["fuentes"]["PRV:produccion_inf_G_cid_%s" % d] = bool(E5.auth("PRV", "demo/hito2/produccion_inf_G_cid_%s.json" % d))
    out["fuentes"]["XDD:extremos_G_d"] = bool(E5.auth("XDD", "demo/extremos/extremos_G_d.json"))
    out["fuentes"]["CAN:extremos_G_f"] = bool(E5.auth("CAN", "demo/extremos/extremos_G_f.json"))
    return out


def referencias_ci_df(P, tareas=tuple("R1-C%d" % i for i in range(1, 7)), raiz_fuentes: Path | None = None) -> dict:
    """Referencias de comparación de las tareas C (se leen solo en la verificación y la comparación, después del cálculo): mediciones
    históricas ci-df autenticadas (orquestador_b.historicos), hojas E13 v4 CENSO-v2 de lima1351 y la referencia citada por la cobertura."""
    hist, agr = P.OB.historicos()
    hv2 = json.loads(autenticado(P1351[0], P1351[1], HOJAS_V2, raiz_fuentes))["filas"]
    out = {"mediciones_historicas_ci_df": len(hist), "agregados_historicos": len(agr), "hojas_ci_v2": len(hv2), "citadas": {}}
    for t in tareas:
        rc = P.referencia_cobertura(t)
        req = P.requeridos_orquestador(t)
        out["citadas"][t] = {"cita": {k: rc["cita"][k] for k in ("entrega", "archivo", "sha256")}, "requeridos": len(req),
                             "con_fila_citada": sum(1 for k in req if k in rc["filas"]), "con_medicion_historica": sum(1 for c, _ in req if c in hist)}
    return out


def ids_de(tid: str, cob: dict) -> list:
    """ids que tarea_r1 pasa al preflight: los de la tarea y sus subtareas de la cobertura."""
    return [x for k, v in cob.items() if k == tid or k.startswith(tid + "-") for x in (v.get("ids") or [])]


# ================================================================================================ comprobación sin cálculo
def fuentes_alteradas() -> list:
    """Archivos de fuentes_fam02.json ausentes o con otra huella (código, entradas, referencias y autenticación de FAM02)."""
    fu = json.loads((BASE / "fuentes_fam02.json").read_bytes())
    return [x["archivo"] for x in fu["archivos"] if not (BASE / x["archivo"]).is_file() or sha((BASE / x["archivo"]).read_bytes()) != x["sha256"]]


def entradas_en_ejecucion(raiz_fuentes: Path | None = None) -> dict:
    """Archivos que los módulos de las rutas por comando leen AL EJECUTARSE (análisis estático de extraccion/extraer_fam02.lecturas:
    literales con extensión de datos en su entrega y en sus entregas base; declarado en fuentes_fam02.json «lecturas_en_ejecucion»):
    presentes y, los que lista el inventario de su entrega, con su huella (o copia pública con correspondencia SAN-RUTAS-v1). El análisis
    estático no prueba que no haya otras lecturas: eso lo muestra el rastro de un cálculo real."""
    fu = json.loads((BASE / "fuentes_fam02.json").read_bytes())
    le = fu.get("lecturas_en_ejecucion")
    if not le:
        return {"cumple": False, "motivo": "LECTURAS_EN_EJECUCION_NO_DECLARADAS"}
    q = BASE / le["archivo"]
    if not q.is_file() or sha(q.read_bytes()) != le["sha256"]:
        return {"cumple": False, "motivo": "LECTURAS_EN_EJECUCION_ALTERADAS"}
    d = json.loads(q.read_bytes())
    R, pub, invs = Path(raiz_fuentes or T), publicas(), {}
    faltan, distintas, sin_inventario = [], [], []
    for a in d["archivos"] + (d.get("salidas_guardadas") or []) + (d.get("referencias_a3") or []):
        e, rel = a[len("tmp/"):].split("/", 1)
        f = R / e / rel
        if not f.is_file():
            faltan.append(a)
            continue
        if rel == "audit/entrega.json":
            continue
        ip = R / e / "audit/entrega.json"
        inv = invs.setdefault(e, json.loads(ip.read_bytes())["files"] if ip.is_file() else {})
        x = inv.get(rel)
        if x is None:
            sin_inventario.append(a)
            continue
        h, hf = (x["sha256"] if isinstance(x, dict) else x), sha(f.read_bytes())
        if hf != h and pub.get((e, rel)) != (hf, h):
            distintas.append(a)
    return {"cumple": not faltan and not distintas, "archivos": len(d["archivos"]), "salidas_guardadas_de_los_comandos": len(d.get("salidas_guardadas") or []),
            "referencias_a3": len(d.get("referencias_a3") or []),
            "faltan": faltan[:20], "distintas": distintas[:20],
            "presentes_sin_inventario_de_su_entrega": sin_inventario, "declaracion": le["archivo"], "declaracion_sha256": le["sha256"],
            "alcance": "análisis estático de literales; no prueba la ausencia de otras lecturas"}


def comprobar() -> dict:
    """fam02-comprobar: SIN CÁLCULO. Huellas de fuentes_fam02.json, plan y cobertura, piloto fijado, contexto S6 y entorno, carga de la
    pila R1 con el núcleo S6, plan del orquestador frente al histórico, y por cada una de las 18 tareas: referencias y productores
    autenticados, PilaR1S6.preflight y, en las rutas por comando, derivación, importación de sus módulos y presencia autenticada de sus
    entradas; para las C, las entradas del método y las referencias de comparación; correspondencia SAN-RUTAS-v1 de las copias
    públicas, ausencia de rutas personales y presencia de las entradas que los comandos leen al ejecutarse."""
    t0 = time.time()
    f = F1()
    malos = fuentes_alteradas()
    if malos:                                      # sin sus fuentes la pila no se carga: se informa y no se sigue
        return {"comando": "fam02-comprobar", "cumple": False, "comprobaciones": {"huellas_fuentes_fam02": False}, "archivos_ausentes_o_distintos": malos[:20],
                "n_archivos_ausentes_o_distintos": len(malos), "tareas": {}, "entorno": None, "segundos": round(time.time() - t0, 1)}
    op = BASE / "nucleo_s6/instalacion" / OPCIONES[0]
    plan, cob, reg = plan_r1(), cobertura(), registro_v4()
    sel = seleccion_piloto(plan, cob, reg)
    fijado = f.leer_json(DATOS / "piloto.json")
    ctx = contexto()
    t_ctx = round(time.time() - t0, 1)
    P, RS, RR, TR = pila(ctx)
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="fam02_comprobar_"))
    try:
        po = plan_orquestador(P, tmp / "plan_orquestador_s6.json")
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    tareas = {}
    for t in plan["r1"]:
        tid, r = t["id"], {}
        try:
            r["referencias"] = referencias(tid, cob)
            r["productores"] = productores(tid, TR)
            pre = P.preflight(tid, ids_de(tid, cob))
            r["preflight"] = {k: pre[k] for k in ("registro_v4_igual_a_afirmaciones_s6", "afirmaciones", "productor", "ids", "extremos_resueltos",
                                                    "ids_no_resueltos", "cierre", "dependencias_en_otras_tareas", "rutas", "sentidos", "nota") if k in pre}
            if tid in TR.RUTAS_POR_COMANDO:
                pr = RR.derivar(tid, T)
                imp = TR.preflight_comandos(RR, RS, pr, T, ctx)
                ent = entradas_de_comandos(RR, pr)
                r["ruta_por_comando"] = {"comandos": [{k: c[k] for k in ("entrega", "registro", "modulo")} for c in pr["comandos"]],
                                         "observaciones": [o["codigo"] for o in pr["observaciones"]], "modulos_importados": [x["modulos_cargados"] for x in imp],
                                         "entradas": ent}
            r["ok"] = (all(x.get("autenticada", True) for x in r["referencias"].values()) and all(x["autenticado_por_inventario"] for x in r["productores"].values())
                       and pre.get("registro_v4_igual_a_afirmaciones_s6") is True
                       and (tid not in TR.RUTAS_POR_COMANDO or r["ruta_por_comando"]["entradas"]["faltan"] == []))
        except Exception as ex:  # noqa: BLE001
            r.update(ok=False, error="%s: %s" % (type(ex).__name__, str(ex)[:300]))
        tareas[tid] = r
    ce, cr = entradas_ci_df(P), referencias_ci_df(P)
    san, lect = correspondencia_san_rutas(RR), entradas_en_ejecucion()
    personales = json.loads((BASE / "fuentes_fam02.json").read_bytes()).get("rutas_personales")
    eq = f.equivalencia_f2(ctx.env_doc, ctx.env_rec, ctx.technical["environment_sha256"])
    comp = {"huellas_fuentes_fam02": not malos, "opciones_r1": sha(op.read_bytes()) == OPCIONES[1], "plan_18_tareas_sin_ciclos": plan["tareas"] == 18 and not plan["motivos"],
            "piloto_igual_al_fijado": {k: sel[k] for k in ("tarea", "hoja", "sentido", "extreme_id")} == {k: fijado[k] for k in ("tarea", "hoja", "sentido", "extreme_id")},
            "plan_orquestador_igual_al_historico": po["igual_al_historico_en_afirmaciones_rutas_y_dependencias"],
            "preflight_18_tareas": all(x.get("ok") for x in tareas.values()) and len(tareas) == 18,
            "copias_publicas_con_correspondencia": san["copias_publicas"] > 0 and not san["sin_correspondencia"],
            "sin_rutas_personales_en_las_fuentes": personales == [],
            "entradas_en_ejecucion_presentes": lect["cumple"] is True,
            "entorno_conforme": ctx.env_doc.get("conforms") is True and not ctx.env_doc.get("mismatches")}
    return {"comando": "fam02-comprobar", "cumple": all(comp.values()), "comprobaciones": comp, "archivos_ausentes_o_distintos": malos[:20],
            "plan": {k: plan[k] for k in ("presupuesto", "orden_topologico", "orden_de_ejecucion", "motivos")}, "piloto": sel,
            "plan_orquestador": po, "tareas": tareas, "c_entradas": ce, "c_referencias": cr, "san_rutas": san, "entradas_en_ejecucion": lect,
            "rutas_personales": personales,
            "entorno": {"conforms": ctx.env_doc.get("conforms"), "mismatches": ctx.env_doc.get("mismatches"), "f2": eq,
                        "f2_alcance": "F2 adoptada para FAM01; para FAM02 su equivalencia se informa y queda como propuesta (ver RESULTADO_FAM02.md)"},
            "contexto_s": t_ctx, "dependencias_fuera_de_la_biblioteca_estandar": f.dependencias_cargadas(), "segundos": round(time.time() - t0, 1)}


def entradas_de_comandos(RR, pr: dict) -> dict:
    """Presencia AUTENTICADA (inventario de su entrega) de las entradas de cada comando de una ruta por comando, sin copiarlas: los
    argumentos que r1_rutas.preparar copiaría (en el inventario y no salidas); la entrada de dependencia (L de A3) viene de la tarea U."""
    faltan, ok, dep = [], 0, pr.get("entrada_de_dependencia")
    for c in pr["comandos"]:
        inv = RR._inv(T, c["entrega"])
        sal = set(RR.salidas_del_comando(c, T))
        for k, a in enumerate(c["argv"]):
            if dep and k == dep["argumento"]:
                continue
            if a in inv and a not in sal:
                try:
                    RR._aut(T, c["entrega"], a, inv)
                    ok += 1
                except Exception:  # noqa: BLE001
                    faltan.append("%s/%s" % (c["entrega"], a))
    return {"presentes": ok, "faltan": faltan, "de_dependencia": dep}


# ================================================================================================ tarea C: cálculo y validación
def registro_r1_parcial(P, RP, sal: Path, tarea: str, req: list, rc) -> dict:
    """Cuerpo de registro_productivo.generar_r1 (mismo validador de fase r1_s6.PilaR1S6 instalado, sin dobles) con los requeridos de una
    asignación PARCIAL de la tarea (piloto): manifiesto de la corrida, verificación del orquestador y cobertura_orquestador sobre la
    asignación con la referencia citada de la tarea. La condición de TAREA «reproduccion_y_coherencia» (al menos un comparable con
    medición histórica y todos ok) se informa; con asignación parcial se exige que ningún comparable falle."""
    mod = sys.modules.get(type(P).__module__)
    need(mod is not None and Path(mod.__file__).resolve() == (INST / RP.VALIDADOR_R1).resolve() and type(P) is getattr(mod, "PilaR1S6", None), "PILA_R1_NO_INSTALADA")
    todos = {tuple(x) for x in P.requeridos_orquestador(tarea)}
    need(req and set(map(tuple, req)) <= todos, "ASIGNACION_FUERA_DE_LA_TAREA")
    sal = Path(sal).resolve()
    cd = sal / "paquete/corrida"
    man = {q.relative_to(cd).as_posix(): sha(q.read_bytes()) for q in sorted(cd.rglob("*")) if q.is_file()} if cd.exists() else {}
    asig = {"tarea": tarea, "requeridos_de_la_tarea": len(todos), "requeridos": [list(x) for x in req], "parcial": True}
    (sal / "r1_productos.json").write_bytes(canon({"tarea": tarea, "corrida": "paquete/corrida", "archivos": man, "asignacion": asig}) + b"\n")
    vb = (sal / "verificacion.json").read_bytes() if (sal / "verificacion.json").exists() else b""
    v = json.loads(vb) if vb else {}
    cob = P.cobertura_orquestador(cd, sal / "verificacion.json", req, sal / "paquete/muestra.json", P.referencia_cobertura(tarea))
    comparables_fallidos = [[f.get("afirmacion"), f.get("sentido")] for f in v.get("filas", []) if f.get("comparable") and not f.get("ok")]
    repro = v.get("reproduccion_y_coherencia") is True
    cumple = rc == 0 and bool(man) and cob["cumple"] and bool(vb) and not comparables_fallidos
    cods = ([] if rc == 0 else ["PRODUCTOR_NO_TERMINO"]) + ([] if vb else ["VERIFICACION_AUSENTE"]) + (["COMPARABLE_NO_REPRODUCIDO"] if comparables_fallidos else []) + cob["codigos"]
    estado = ("hojas_validadas" if repro else "hojas_validadas_por_referencia_citada") if cumple else "rechazada"
    verif = {"cumple": cumple, "codigos": [] if cumple else (cods or ["R1_NO_REPRODUCIDA_O_INCOHERENTE"]), "productor": getattr(P.ctx, "identity_sha256", None),
             "rc_productor": rc, "comparables": v.get("comparables"), "verificados_ok": v.get("verificados_ok"), "por_ruta": v.get("por_ruta"), "cobertura": cob,
             "condicion_de_tarea": {"reproduccion_y_coherencia": repro, "comparables_fallidos": comparables_fallidos,
                                    "nota": "en la tarea completa generar_r1 exige reproduccion_y_coherencia (≥1 comparable con medición histórica, todos ok); "
                                            "con una asignación parcial sin medición histórica no es evaluable y se informa"},
             "asignacion": asig}
    u = "R1:%s:parcial:%s" % (tarea, sha(canon(asig["requeridos"]))[:12])
    ent = {u: {"documento_sha256": sha((sal / "r1_productos.json").read_bytes()), "filas_sha256": sha(vb), "estado": estado, "documento": "r1_productos.json",
               "filas": "verificacion.json"}}
    reg = {"validador": {"archivo": RP.VALIDADOR_R1, "sha256": sha((INST / RP.VALIDADOR_R1).read_bytes())},
           "generado_por": {"modulo": "src/fam02.py:registro_r1_parcial (cuerpo de registro_productivo.generar_r1 con la asignación)",
                            "sha256": sha(Path(__file__).read_bytes()), "registro_productivo_sha256": sha(Path(RP.__file__).read_bytes()),
                            "contexto_identidad_sha256": sha(canon(P.ctx.identity)), "autoridad": None, "paquete": "paquete", "dictamen_sha256": sha(canon(verif))},
           "verificacion": verif, "unidades": ent}
    (sal / "dictamen_validacion.json").write_bytes(canon(verif))
    (sal / "registro_productivo.json").write_bytes(canon(reg) + b"\n")
    return reg


def _validacion(P, RP, salida: Path, tarea: str, req: list, req_t: list, rc):
    """[VALIDACIÓN] orquestador_b.verificar (mediciones históricas autenticadas y hojas E13 v4 CENSO-v2) y registro productivo R1:
    registro_productivo.generar_r1 sin cambios con la tarea completa; registro_r1_parcial con una asignación parcial."""
    import contextlib
    import io
    hojas_v2 = T / P1351[0] / HOJAS_V2
    autenticado(P1351[0], P1351[1], HOJAS_V2)
    motivo_ver = None
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            P.verificar(salida / "paquete" / "corrida", hojas_v2, salida / "paquete" / "plan_orquestador_s6.json", salida / "verificacion.json")
    except SystemExit as ex:                       # p. ej. HISTORICO_NO_AUTENTICADO o CHECKPOINT_ALTERADO: sin verificación
        motivo_ver = str(ex)
    completa = set(req) == set(req_t)
    info_d = None
    if completa:
        with regla_r1d(P, RP, salida, tarea) as info_d:          # CIERRE-MUESTRA-R1D-v1 solo en R1-D (None en las tareas C)
            reg = RP.generar_r1(P, salida, tarea, "paquete/corrida", "verificacion.json", salida=salida / "registro_productivo.json",
                                dictamen=salida / "dictamen_validacion.json", rc_productor=rc)
        need(info_d is None or info_d["restaurada"], "PILA_NO_RESTAURADA_TRAS_CIERRE_MUESTRA_R1D")
        estado_val = reg["unidades"]["R1:" + tarea]["estado"]
    else:
        reg = registro_r1_parcial(P, RP, salida, tarea, req, rc)
        estado_val = next(iter(reg["unidades"].values()))["estado"]
    return reg, estado_val, motivo_ver, completa, info_d


def validar(tarea: str, origen: Path, salida: Path, enlazar: bool = False) -> dict:
    """fam02-validar: SIN CÁLCULO. Repite la validación de una salida de fam02-unidad en una carpeta NUEVA: copia su paquete (muestra,
    plan del orquestador y corrida) y vuelve a hacer verificar + registro con la asignación de su ejecucion.json. La carpeta de origen
    no se toca. Sirve para validar una salida recibida y para las pruebas de fallo."""
    import shutil
    t0 = time.time()
    origen, salida = Path(origen), Path(salida)
    ej = json.loads((origen / "ejecucion.json").read_bytes())
    need(ej.get("tarea") == tarea, "SALIDA_DE_OTRA_TAREA: %s" % ej.get("tarea"))
    need(tarea != "R1-V", "R1-V_SE_VALIDA_CON_FAM02-UNIDAD (validación global sin cálculo)")
    if not (tarea.startswith("R1-C") or tarea == "R1-D"):
        return validar_ruta(tarea, origen, salida, ej, enlazar=enlazar)
    need(not enlazar, "ENLAZAR_SOLO_EN_RUTAS_POR_COMANDO")
    salida.mkdir(parents=True, exist_ok=False)
    shutil.copytree(origen / "paquete", salida / "paquete")
    shutil.copyfile(origen / "ejecucion.json", salida / "ejecucion.json")     # registro del CÁLCULO de origen (asignación, rc); fam02-comparar lo lee
    rastro = F1().Rastro()
    ctx = contexto()
    P, RS, RR, TR = pila(ctx)
    RP = TR._carga("registro_productivo", "herramientas/b/registro_productivo.py")
    req_t = [tuple(x) for x in P.requeridos_orquestador(tarea)]
    req = req_t if tarea == "R1-D" else [tuple(x) for x in ej["asignacion"]["requeridos"]]
    rc = ej["calculo"]["rc_productor"]
    reg, estado_val, motivo_ver, completa, info_d = _validacion(P, RP, salida, tarea, req, req_t, rc)
    v = reg["verificacion"]
    out = {"comando": "fam02-validar", "tarea": tarea, "origen": origen.name, "calculo": "ninguno (corrida copiada de la salida de origen)",
           "cierre_muestra_r1d": info_d,
           "validacion": {"estado": estado_val, "cumple": v.get("cumple"), "codigos": v.get("codigos"), "motivo_verificacion": motivo_ver,
                          "comparables": v.get("comparables"), "verificados_ok": v.get("verificados_ok"),
                          "condicion_de_tarea": v.get("condicion_de_tarea"), "completa": completa,
                          "registro_sha256": sha((salida / "registro_productivo.json").read_bytes())},
           "segundos": round(time.time() - t0, 2)}
    leidos = rastro.informe()
    out["archivos_leidos"] = {"en_el_paquete": len(leidos["en_el_paquete"]), "aperturas_del_interprete": leidos["aperturas_del_interprete"],
                              "fuera_del_paquete_y_del_interprete": leidos["fuera_del_paquete_y_del_interprete"]}
    (salida / "validacion.json").write_bytes(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True).encode("utf-8") + b"\n")
    return out


def validar_ruta(tarea: str, origen: Path, salida: Path, ej: dict, enlazar: bool = False) -> dict:
    """fam02-validar de una ruta por comando: SIN CÁLCULO. Copia el paquete de la salida de origen y repite _validar_ruta con los códigos
    de su ejecucion.json; A1/A2 vuelven a leer la aceptación local de R1-B3 de la ejecución de la carpeta NUEVA. Sin enlazar no escribe
    enlace. Con enlazar (--enlazar), si el cálculo de origen terminó y la revalidación cumple, escribe el enlace de la carpeta nueva en SU
    ejecución (<ejecucion>/aceptaciones/<tarea>.json, ENLACE-LOCAL-FAM02-v1) con la revalidación como origen; la salida de origen, su
    validación y su ausencia de enlace no se tocan."""
    import shutil
    t0 = time.time()
    salida = Path(salida)
    need(not enlazar or salida.resolve().parent != (BASE / "salidas" / "fam02").resolve(),
         "ENLAZAR_REQUIERE_UNA_CARPETA_DE_EJECUCION: --salida salidas/fam02/<ejecucion>/<tarea>")
    salida.mkdir(parents=True, exist_ok=False)
    salida = salida.resolve()
    shutil.copytree(Path(origen) / "paquete", salida / "paquete")
    shutil.copyfile(Path(origen) / "ejecucion.json", salida / "ejecucion.json")
    rastro = F1().Rastro()
    ctx = contexto()
    P, RS, RR, TR = pila(ctx)
    RP = TR._carga("registro_productivo", "herramientas/b/registro_productivo.py")
    OPm = TR._carga("opciones_p1", "herramientas/b/opciones_p1.py")
    plan_ruta = RR.derivar(tarea, T)
    plan_ruta["artefactos_del_trabajador"] = {RR.ARTEFACTO_PREFLIGHT: ej["plan_orquestador"]["sha256"]}
    op, aut = opcion_activa(OPm, tarea)
    rcs = {int(k): v for k, v in (ej["calculo"].get("rcs") or {}).items()}
    regs = {int(k): v for k, v in (ej["calculo"].get("comandos") or {}).items()}
    _, prov, rech = aceptados(salida.parent, (CONSUMO.get(tarea) or ([], None))[0], RP) if op == "A1A2_INTERCAMBIO_DE_TESTIGOS" else ({}, {}, {})
    sred_ejec = (rcs, regs) if tarea == "R1-A1" else None
    reg, val = _validar_ruta(P, RR, RP, OPm, tarea, salida, plan_ruta, rcs, op, aut, prov, sred_ejec,
                             identidad_del_calculo=ej.get("identidad_contexto_sha256"))
    out = {"comando": "fam02-validar", "tarea": tarea, "origen": Path(origen).name, "calculo": "ninguno (paquete copiado de la salida de origen)",
           "naturaleza_del_origen": ej.get("naturaleza"), "validacion": dict(val, dependencias_sin_aceptacion=rech), "segundos": round(time.time() - t0, 2)}
    calc_ok = (ej.get("calculo") or {}).get("estado") == "terminado" and all(v == 0 for v in rcs.values())
    leidos = rastro.informe()
    out["archivos_leidos"] = {"en_el_paquete": len(leidos["en_el_paquete"]), "aperturas_del_interprete": leidos["aperturas_del_interprete"],
                              "fuera_del_paquete_y_del_interprete": leidos["fuera_del_paquete_y_del_interprete"]}
    out["enlace_pedido"] = bool(enlazar)
    (salida / "validacion.json").write_bytes(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True, default=str).encode("utf-8") + b"\n")
    if enlazar:
        out["aceptacion"] = (aceptar(salida, RP, revalidacion={"origen": Path(origen).resolve().relative_to(BASE).as_posix(), "validacion": "validacion.json",
                                                               "validacion_sha256": sha((salida / "validacion.json").read_bytes())})
                             if calc_ok and val["cumple"] is True else
                             {"aceptada": False, "motivos": ["CALCULO_DE_ORIGEN_O_REVALIDACION_NO_CUMPLE"]})
    return out


def correr(tarea: str, hojas: list | None, salida: Path, tope: float = 600.0) -> dict:
    """fam02-unidad: tarea C (R1-C1..C6) completa o una asignación parcial de sus hojas, o R1-D completa, en la carpeta NUEVA `salida`:
    [R1-D: dependencias por el enlace local] -> contexto S6 -> preflight y plan del orquestador -> [R1-D: intercambio de los productos
    aceptados (tarea_r1.hojas_y_fuentes_de + PilaR1S6.intercambio) y registro de consumo] -> [CÁLCULO: orquestador_b.ejecutar] ->
    [VALIDACIÓN: verificar + registro] -> enlace de aceptación si la validación cumple. La comparación es otro paso (comparar)."""
    import platform
    f = F1()
    t0, c0 = time.time(), time.process_time()
    plan, cob, reg4 = plan_r1(), cobertura(), registro_v4()
    need(tarea in [t["id"] for t in plan["r1"]], "TAREA_FUERA_DEL_PLAN")
    es_d = tarea == "R1-D"
    need(tarea.startswith("R1-C") or es_d, "TAREA_SIN_RUTA_DEL_ORQUESTADOR: %s (ver fam02-receta)" % tarea)
    need(not (es_d and hojas), "R1-D_SOLO_COMPLETA")
    req_t = None if es_d else requeridos(tarea, cob, reg4)
    if hojas:
        need(len(set(hojas)) == len(hojas), "HOJAS_REPETIDAS")
        req = [k for k in req_t if k[0] in set(hojas)]
        need({c for c, _ in req} == set(hojas), "HOJA_FUERA_DE_LA_TAREA")
    else:
        req = None if es_d else list(req_t)
    malos = fuentes_alteradas()
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam02.json; no se calcula): %s" % malos[:5])
    salida = Path(salida)
    acept, prov = {}, {}
    if es_d:                                       # productos ACEPTADOS en esta ejecución (enlace local), antes de crear nada
        preparar()
        TR0 = cargar("tarea_r1", INST / "herramientas/b/tarea_r1.py")
        RP0 = TR0._carga("registro_productivo", "herramientas/b/registro_productivo.py")
        deps = [x for x in {t["id"]: t for t in plan["r1"]}["R1-D"]["depende_de_expandido"] if x != "F0"]
        acept, prov, rech = aceptados(salida.resolve().parent, deps, RP0)
        need(not rech, "DEPENDENCIA_NO_ACEPTADA_EN_ESTA_EJECUCION (no se calcula): %s" % rech)
        need(all(p["reproduccion"] for p in prov.values()), "DEPENDENCIA_DE_UNA_PRUEBA_DE_CONEXION_EN_UN_CALCULO")
    salida.mkdir(parents=True, exist_ok=False)
    salida = salida.resolve()
    rastro = f.Rastro()
    ctx = contexto()
    P, RS, RR, TR = pila(ctx)
    RP = TR._carga("registro_productivo", "herramientas/b/registro_productivo.py")
    t_ctx = round(time.time() - t0, 2)
    t1 = time.time()
    if es_d:
        req_t = [tuple(x) for x in P.requeridos_orquestador(tarea)]
        req = list(req_t)
        pre = P.preflight(tarea, ids_de(tarea, cob))                     # como tarea_r1: ids de D y de sus subtareas de la cobertura
    else:
        need([tuple(x) for x in P.requeridos_orquestador(tarea)] == req_t, "REQUERIDOS_DISTINTOS_DE_LA_PILA")
        pre = P.preflight(tarea, [eid(c, s) for c, s in req])
        need(pre.get("afirmaciones_muestra") == sorted({c for c, _ in req}), "MUESTRA_DISTINTA_DE_LA_ASIGNACION")
    po = plan_orquestador(P, salida / "paquete" / "plan_orquestador_s6.json")
    need(po["igual_al_historico_en_afirmaciones_rutas_y_dependencias"], "PLAN_ORQUESTADOR_S6_DISTINTO_DEL_HISTORICO")
    cierre_d = None
    if es_d:                                       # CIERRE-MUESTRA-R1D-v1 (a): muestra = cierre por dependencias, comprobado ANTES de calcular
        cierre_d = cierre_r1d(P, cob, pre["afirmaciones_muestra"])
        cods_a = (([] if pre["afirmaciones_muestra"] == sorted({c for c, _ in req}) else ["MUESTRA_DEL_PREFLIGHT_DISTINTA_DE_LOS_REQUERIDOS"]) +
                  cierre_d["codigos"] + ([] if set(R1D_CIERRE["dependencias_de"]) <= set(acept) else ["B1_B2_B3_NO_ACEPTADAS_EN_ESTA_EJECUCION"]))
        if cods_a:
            return rechazo_r1d(salida, ctx, prov, cods_a, cierre_d, t0, c0, rastro)
    muestra = salida / "paquete" / "muestra.json"
    muestra.write_bytes(json.dumps({"afirmaciones": cierre_d["muestra"] if es_d else pre["afirmaciones_muestra"]}, ensure_ascii=False,
                                   sort_keys=True).encode("utf-8"))
    ent_c = entradas_ci_df(P, ("G", "N") if es_d else sorted({campos(c)["dis"] for c, _ in req}))
    evid_d, hojas_d = None, None
    if es_d:                                       # rem44/rem51: INTERCAMBIO de productos aceptados (nunca hojas recalculadas) y enlace D -> V
        (salida / "paquete/dependencias_consumidas.json").write_bytes(RP.canon({x: _sin_arbol(prov[x]) for x in sorted(acept)}) + b"\n")
        deps_plan = {fl["afirmacion"]: fl["dependencias"] for fl in json.loads((salida / "paquete/plan_orquestador_s6.json").read_bytes())["filas"]}
        hojas_d, fuentes_d = TR.hojas_y_fuentes_de(P, pre["afirmaciones_muestra"], acept, deps_plan)
        cierre_d["fuentes_inyectadas"], cods_f = fuentes_r1d(fuentes_d, acept, prov)       # (a): fuentes = productos aceptados
        if cods_f:
            return rechazo_r1d(salida, ctx, prov, cods_f, cierre_d, t0, c0, rastro)
        evid_d = P.intercambio(salida / "paquete" / "corrida", hojas_d, fuentes_d, set(hojas_d))
    t_pre = round(time.time() - t1, 2)
    # ---- [CÁLCULO] método v5 del orquestador con el ContextoS6 (mismas opciones que tarea_r1: tope por afirmación 300 s)
    t2 = time.time()
    opts = ["--tope-afirmacion", "300", "--tope-proceso", str(max(60.0, tope - 300.0))]
    import contextlib
    import io
    buf, motivo_calc = io.StringIO(), None
    try:
        with contextlib.redirect_stdout(buf):
            rc = P.producir(salida / "paquete" / "corrida", muestra, opts)
    except SystemExit as ex:                       # rechazos del método (p. ej. PUNTOS_U_ALTERADOS): el cálculo no terminó
        rc, motivo_calc = (ex.code if isinstance(ex.code, int) else 1), str(ex)
    if evid_d is not None and not P.hojas_intactas(salida / "paquete" / "corrida", evid_d, hojas_d):
        rc, motivo_calc = rc or 1, "HOJAS_ACEPTADAS_ALTERADAS_O_RECALCULADAS"
    t_calc = round(time.time() - t2, 2)
    C = object.__new__(P.OB.Corrida)
    C.d = salida / "paquete" / "corrida"
    res = {}
    for c in sorted({c for c, _ in req}):
        for s in ("sup", "inf"):
            r = C.leer(c, s)
            res["%s|%s" % (c, s)] = None if r is None else {
                "requerido": (c, s) in set(req), "estado": r.get("estado"), "G": r.get("G"), "brecha": r.get("brecha"), "ruta": r.get("ruta"),
                "testigo": r.get("testigo"), "inf_bb": {k: v for k, v in (r.get("inf_bb") or {}).items() if k in ("estado", "L", "cajas", "segundos", "evaluaciones")} or None,
                "contenido_sha256": r.get("contenido_sha256")}
    calc_ok = rc == 0 and all(res.get("%s|%s" % k) and res["%s|%s" % k]["estado"] in ESTADOS_TERMINALES_ADMISIBLES for k in req)
    est_dep = Counter()
    for c in (cierre_d or {}).get("dependencias") or []:           # R1-D: las 640 dependencias (aparte de los extremos de D)
        for s in ("sup", "inf"):
            try:
                est_dep[(C.leer(c, s) or {}).get("estado", "ausente")] += 1
            except SystemExit:
                est_dep["alterado"] += 1
    # ---- [VALIDACIÓN] verificación del orquestador (con hojas_ci_v2) y registro productivo R1
    t3 = time.time()
    reg, estado_val, motivo_ver, completa, info_d = _validacion(P, RP, salida, tarea, req, req_t, rc)
    t_val = round(time.time() - t3, 2)
    ent = {"documento": ctx.env_doc, "records_sin_lanzadores": ctx.env_rec, "environment_sha256": ctx.technical["environment_sha256"]}
    (salida / "entorno.json").write_bytes(canon(ent) + b"\n")
    eq = f.equivalencia_f2(ctx.env_doc, ctx.env_rec, ctx.technical["environment_sha256"])
    v = reg["verificacion"]
    estados = dict(Counter((x or {}).get("estado", "ausente") for x in res.values()))
    if es_d:                                       # D: 7.040 extremos; en ejecucion.json solo los estados (los resultados están en la corrida)
        res = {"resumen": estados, "intercambio": evid_d}
    ej = {"comando": "fam02-unidad", "tarea": tarea, "naturaleza": "cálculo: orquestador_b.ejecutar con el ContextoS6" + (" sobre los productos aceptados intercambiados" if es_d else ""),
          "reproduccion": all(p["reproduccion"] for p in prov.values()),
          "dependencias_consumidas": {x: {k: prov[x][k] for k in ("salida", "arbol_sha256", "aceptacion_sha256", "reproduccion")} for x in sorted(prov)},
          "identidad_contexto_sha256": getattr(ctx, "identity_sha256", None),
          "asignacion": {"completa": completa, "requeridos": [list(x) for x in req] if not es_d else len(req), "requeridos_de_la_tarea": len(req_t),
                         "ids": [eid(c, s) for c, s in req] if not es_d else len(req)},
          "preflight": {k: pre[k] for k in ("registro_v4_igual_a_afirmaciones_s6", "afirmaciones", "dependencias_derivadas", "extremos_resueltos", "cierre",
                                            "dependencias_en_otras_tareas", "rutas", "sentidos") if k in pre},
          "plan_orquestador": po,
          "entradas_reutilizadas": {"declaracion": "entradas históricas aceptadas que el método v5 consume (no son salidas R1): registro v4 (lima1941), puntos U "
                                                   "del techo v3 citados por lima0754, SRED-G/N (lima1958; el supremo cerrado), caja del grupo del plan C2 "
                                                   "(certificacion); PRV/XDD/CAN se autentican al cargar pero las hojas ci-df no los usan",
                                    "detalle": ent_c},
          "calculo": {"estado": "terminado" if calc_ok else "incompleto", "rc_productor": rc, "motivo": motivo_calc, "opciones": opts, "resultados": res,
                      "estados": estados, "salida_del_productor": buf.getvalue()[-2000:]},
          "validacion": {"estado": estado_val, "cumple": v.get("cumple"), "codigos": v.get("codigos"), "motivo_verificacion": motivo_ver, "registro": "registro_productivo.json",
                         "registro_sha256": sha((salida / "registro_productivo.json").read_bytes()), "comparables": v.get("comparables"),
                         "verificados_ok": v.get("verificados_ok"), "cobertura": {k: (v.get("cobertura") or {}).get(k) for k in (
                             "cumple", "codigos", "requeridos", "presentes", "subproductos", "validados_por_verificacion_historica", "validados_por_referencia_citada")},
                         "condicion_de_tarea": v.get("condicion_de_tarea"),
                         "validador": "registro_productivo.generar_r1" if completa else "fam02.registro_r1_parcial (cuerpo de generar_r1 con la asignación)"},
          "tecnicas": ctx.technical,
          "entorno": {"conforms": ctx.env_doc.get("conforms"), "mismatches": ctx.env_doc.get("mismatches"), "documento": "entorno.json", "f2": eq,
                      "f2_alcance": "adoptada para FAM01; para FAM02, propuesta (RESULTADO_FAM02.md)", "python": platform.python_version(),
                      "hash_seed": os.environ.get("PYTHONHASHSEED"), "hash_randomization": sys.flags.hash_randomization,
                      "hilos": {k: os.environ.get(k) for k in f.HILOS}, "TZ": os.environ.get("TZ")},
          "tiempos_s": {"contexto": t_ctx, "preflight": t_pre, "calculo": t_calc, "validacion": t_val, "total": round(time.time() - t0, 2),
                        "cpu": round(time.process_time() - c0, 2)},
          "dependencias_fuera_de_la_biblioteca_estandar": f.dependencias_cargadas()}
    if es_d:
        ej["cierre_muestra_r1d"] = {"regla": R1D_CIERRE["regla"], "autorizacion": R1D_CIERRE["autorizacion"],
                                    "muestra": {"afirmaciones_de_D": cierre_d["afirmaciones_de_D"], "dependencias": len(cierre_d["dependencias"]),
                                                "muestra": len(cierre_d["muestra"]), "muestra_sha256": sha(muestra.read_bytes()),
                                                "dependencias_por_ruta": cierre_d["por_ruta"],
                                                "extremos_de_dependencia_por_tarea_y_sentido": cierre_d["extremos_por_tarea_y_sentido"],
                                                "estados_de_las_dependencias": dict(est_dep)},
                                    "fuentes_inyectadas": cierre_d["fuentes_inyectadas"], "validacion": info_d}
    ej["exito"] = bool(calc_ok and v.get("cumple") is True)
    (salida / "archivos_leidos.json").write_bytes((json.dumps(rastro.informe(), ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    (salida / "ejecucion.json").write_bytes(json.dumps(ej, ensure_ascii=False, indent=1, sort_keys=True, default=list).encode("utf-8") + b"\n")
    # una asignación PARCIAL (hojas_validadas*) no es admisible para consumo: aceptar lo informa y no escribe enlace
    ej["aceptacion"] = aceptar(salida, RP) if ej["exito"] else {"aceptada": False, "motivos": ["CALCULO_O_VALIDACION_NO_CUMPLE"]}
    return ej


# ================================================================================================ enlace local de aceptación
KIND_ACEPTACION = "fam02-aceptacion-local-v1"
REGLA_ENLACE = ("ENLACE-LOCAL-FAM02-v1. Sustituye, sin reconstruir la autorización histórica (corrida_paso4: diario, admisión, acto), a "
                "tarea_r1.productos_aceptados, corrida_paso4.aceptaciones_previas y procedencia_vigente. Una salida queda ACEPTADA en su "
                "ejecución (la carpeta que la contiene) cuando su registro productivo pasa las comprobaciones que "
                "registro_productivo.generar_r1_global aplica a una fuente: generado por el registro_productivo instalado, validador r1_s6 "
                "instalado, dictamen = verificación, única unidad R1:<tarea> en estado admisible (completa_validada) y ligada a sus productos. "
                "El enlace <ejecución>/aceptaciones/<tarea>.json fija la salida, su árbol (sha256 de cada archivo) y las dependencias que "
                "consumió; no se sobrescribe. Una tarea solo consume dependencias con enlace en la MISMA ejecución y árbol re-enumerado igual "
                "al fijado justo antes de consumirlas. Una salida de la prueba de conexión (--salidas-guardadas) se enlaza con "
                "reproduccion=false, que hereda todo consumidor: nunca cuenta como reproducción, y un cálculo real no la consume.")
NATURALEZA_CALCULO = "cálculo: comandos históricos ejecutados en el paquete (importador de su entrega, núcleo S6 y ContextoS6), como tarea_r1.ejecutar_ruta"
NATURALEZA_CONEXION = ("PRUEBA DE CONEXIÓN SIN CÁLCULO: ningún comando histórico se ejecutó; en su lugar se puso en el paquete la salida GUARDADA "
                       "del mismo comando (bytes autenticados por el inventario de su entrega). Prueba el enlace, la validación y los "
                       "consumidores; no es cálculo ni reproducción")


def arbol(sal: Path) -> dict:
    """= el árbol de registro_productivo.generar_r1_global y corrida_paso4._arbol: {ruta relativa: sha256} de cada archivo de la salida."""
    sal = Path(sal)
    return {q.relative_to(sal).as_posix(): sha(q.read_bytes()) for q in sorted(sal.rglob("*")) if q.is_file()}


def _registro_admisible(sal: Path, tarea: str, RP) -> tuple:
    """(datos del registro, motivos) con las comprobaciones de una fuente en registro_productivo.generar_r1_global (salvo el árbol)."""
    sal = Path(sal)
    try:
        rb, db = (sal / "registro_productivo.json").read_bytes(), (sal / "dictamen_validacion.json").read_bytes()
        reg, ver = json.loads(rb), json.loads(db)
    except (OSError, ValueError):
        return None, ["REGISTRO_AUSENTE_O_ILEGIBLE"]
    g, vd, us = reg.get("generado_por") or {}, reg.get("validador") or {}, reg.get("unidades") or {}
    e = us.get("R1:" + tarea) or {}
    a = arbol(sal)
    mot = [c for c, malo in (
        ("REGISTRO_NO_GENERADO_POR_LA_RUTA", (g.get("modulo"), g.get("sha256")) != (RP.MODULO, sha(Path(RP.__file__).read_bytes()))),
        ("REGISTRO_DE_OTRO_VALIDADOR", (vd.get("archivo"), vd.get("sha256")) != (RP.VALIDADOR_R1, sha((INST / RP.VALIDADOR_R1).read_bytes()))),
        ("DICTAMEN_DISTINTO", g.get("dictamen_sha256") != sha(db) or reg.get("verificacion") != ver),
        ("UNIDADES_AJENAS_O_DUPLICADAS", sorted(us) != ["R1:" + tarea]),
        ("ESTADO_NO_ADMISIBLE:%s" % e.get("estado"), e.get("estado") not in RP.ESTADOS_ADMISIBLES or ver.get("cumple") is not True),
        ("UNIDAD_NO_LIGADA_A_SUS_PRODUCTOS", (e.get("documento_sha256"), e.get("filas_sha256")) != (a.get(e.get("documento")), a.get(e.get("filas"))))) if malo]
    return {"registro_sha256": sha(rb), "dictamen_sha256": sha(db), "unidad": {"id": "R1:" + tarea, **{k: e.get(k) for k in ("estado", "documento", "documento_sha256",
                                                                                                                             "filas", "filas_sha256")}}}, mot


def aceptar(salida: Path, RP, revalidacion: dict | None = None) -> dict:
    """Escribe el enlace de aceptación de una salida validada (ENLACE-LOCAL-FAM02-v1) si es admisible; si no, informa por qué. Con
    revalidacion, el enlace registra que la validación es una revalidación sin cálculo de la salida de origen indicada."""
    sal = Path(salida).resolve()
    ej = json.loads((sal / "ejecucion.json").read_bytes())
    tarea = ej["tarea"]
    info, mot = _registro_admisible(sal, tarea, RP)
    if mot:
        return {"aceptada": False, "motivos": mot}
    p = sal.parent / "aceptaciones" / (tarea + ".json")
    if p.exists():
        return {"aceptada": False, "motivos": ["TAREA_YA_ACEPTADA_EN_ESTA_EJECUCION"], "enlace_existente": "aceptaciones/%s.json" % tarea}
    a = arbol(sal)
    doc = {"kind": KIND_ACEPTACION, "regla": REGLA_ENLACE.split(".")[0], "tarea": tarea, "ejecucion": sal.parent.name, "salida": sal.name,
           "arbol": a, "arbol_sha256": sha(canon(a)), **info, "identidad_contexto_sha256": ej.get("identidad_contexto_sha256"),
           "reproduccion": ej.get("reproduccion") is True, "naturaleza": ej.get("naturaleza"), "consumidas": ej.get("dependencias_consumidas") or {},
           "fam02_sha256": sha(Path(__file__).read_bytes())}
    if revalidacion is not None:
        doc["revalidacion_sin_calculo"] = revalidacion
    if tarea == R1F_TIEMPOS["tarea"]:
        doc["regla_de_igualdad"] = R1F_TIEMPOS["regla"]
    p.parent.mkdir(exist_ok=True)
    b = canon(doc) + b"\n"
    p.write_bytes(b)
    return {"aceptada": True, "motivos": [], "enlace": "aceptaciones/%s.json" % tarea, "enlace_sha256": sha(b), "reproduccion": doc["reproduccion"]}


def aceptados(ejecucion: Path, deps, RP) -> tuple:
    """({tarea: salida}, {tarea: procedencia}, {tarea: motivo}) de las dependencias con enlace en ESTA ejecución: enlace de esta regla y
    de la tarea, salida dentro de la ejecución, árbol re-enumerado = fijado y registro todavía admisible."""
    E = Path(ejecucion).resolve()
    out, prov, rech = {}, {}, {}
    for x in deps:
        p = E / "aceptaciones" / (x + ".json")
        if not p.is_file():
            rech[x] = "SIN_ACEPTACION_EN_ESTA_EJECUCION"
            continue
        b = p.read_bytes()
        try:
            doc = json.loads(b)
            sal = (E / doc["salida"]).resolve()
        except (ValueError, KeyError, TypeError):
            rech[x] = "ENLACE_ILEGIBLE"
            continue
        if doc.get("kind") != KIND_ACEPTACION or doc.get("tarea") != x or sal.parent != E:
            rech[x] = "ENLACE_AJENO_O_DE_OTRA_EJECUCION"
            continue
        a = arbol(sal) if sal.is_dir() else {}
        if a != doc.get("arbol") or sha(canon(a)) != doc.get("arbol_sha256"):
            rech[x] = "PRODUCTO_ALTERADO_TRAS_LA_ACEPTACION"
            continue
        _, mot = _registro_admisible(sal, x, RP)
        if mot:
            rech[x] = "REGISTRO_YA_NO_ADMISIBLE:%s" % ",".join(mot)
            continue
        out[x] = sal
        prov[x] = {"origen": "esta_ejecucion (enlace local FAM02)", "tarea": x, "raiz": str(E), "corrida_id": str(E), "salida": str(sal),
                   "arbol": a, "arbol_sha256": doc["arbol_sha256"], "identidad_sha256": doc.get("identidad_contexto_sha256"), "aceptacion_sha256": sha(b),
                   "registro_sha256": doc.get("registro_sha256"), "reproduccion": doc.get("reproduccion") is True}
    return out, prov, rech


def _sin_arbol(p: dict) -> dict:
    return {k: v for k, v in p.items() if k != "arbol"}


# ================================================================================================ rutas por comando (A*, B*, F)
def opcion_activa(OPm, tarea: str) -> tuple:
    """(opción, activación) de la tarea: la decisión aprobada del catálogo instalado (datos/paso4/opciones_r1.json, estado «aprobada»), en
    lugar de opciones_p1.opciones_autorizadas (autorización reconstruida de una corrida histórica, que no se reconstruye)."""
    op = OPm.OPCION_DE_TAREA.get(tarea)
    if op is None:
        return None, None
    need(sha((INST / OPCIONES[0]).read_bytes()) == OPCIONES[1], "CATALOGO_DE_OPCIONES_ALTERADO")
    cat = OPm.catalogo()["opciones"][op]
    need(cat.get("estado") == "aprobada", "OPCION_NO_APROBADA:%s" % op)
    return op, {"fuente": "catálogo instalado %s (%s…): opción «aprobada» por decisión firmada del autor (%s)" % (OPCIONES[0], OPCIONES[1][:8], cat.get("decision")),
                "opcion": op, "texto_sha256": cat["texto_sha256"], "implementacion_sha256": sha(Path(OPm.__file__).read_bytes()),
                "sustituye_a": "opciones_p1.opciones_autorizadas (autorización reconstruida de la corrida histórica: no se reconstruye)"}


def salidas_guardadas(RR, plan_ruta: dict, paquete: Path, archivos: dict) -> tuple:
    """PRUEBA DE CONEXIÓN SIN CÁLCULO (ver NATURALEZA_CONEXION): entradas preparadas como en la ruta real (r1_rutas.preparar) y, en lugar
    de ejecutar cada comando, su salida guardada (r1_rutas.salidas_del_comando, bytes autenticados). Devuelve (códigos, registros) con
    la forma de tarea_r1.ejecutar_ruta."""
    RR.preparar(plan_ruta, T, paquete, archivos)
    rcs, regs = {}, {}
    for n, c in enumerate(plan_ruta["comandos"]):
        for s in RR.salidas_del_comando(c, T):
            (paquete / s).parent.mkdir(parents=True, exist_ok=True)
            (paquete / s).write_bytes(RR._aut(T, c["entrega"], s))
        rcs[n] = 0
        regs[n] = {"modulo": c["modulo"], "entrega": c["entrega"], "rc": 0, "modulos": [], "errores": [], "sustituciones": [],
                   "naturaleza": "comando NO ejecutado: salida guardada copiada"}
    return rcs, regs


def intercambio_local(OPm, tarea: str, pv_b3: dict | None, sred_paquete=None, sred_ejecucion=None, artefactos=None) -> dict:
    """= opciones_p1.intercambio_aceptado con la aceptación de R1-B3 del ENLACE LOCAL en lugar de la reconstruida por corrida_paso4:
    lectura autenticada de sus bytes (opciones_p1._leer_b3 con el árbol fijado), SRED propio validado (_sred_validados, solo A1), testigos
    de la referencia autenticada (seleccion_c2), correspondencia exacta (_intercambio) y nueva comprobación del árbol de B3 y de los
    bytes SRED al terminar."""
    base = {"opcion": "A1A2_INTERCAMBIO_DE_TESTIGOS", "tarea": tarea, "entrada": "fam02.intercambio_local (enlace local de R1-B3)"}

    def rech(cod, **x):
        return dict(base, rechazo=dict(codigo=cod, **x), testigos=[], requeridos=len(OPm.TESTIGOS.get(tarea, ())), satisfechos=0, correspondencia_completa=False,
                    completo=False, aceptable=False, procedencia=None, sred=None)
    if tarea not in OPm.TESTIGOS:
        return rech("TAREA_SIN_INTERCAMBIO")
    if pv_b3 is None:
        return rech("SIN_ACEPTACION_LOCAL_DE_R1-B3")
    try:
        cs = OPm.seleccion_c2(T)
    except Exception as ex:  # noqa: BLE001
        return rech("REFERENCIA_C2_NO_AUTENTICADA", detalle=str(ex)[:200])
    try:
        docs, leidos, _ = OPm._leer_b3(pv_b3, arbol)
    except (OSError, ValueError) as ex:
        return rech(str(ex).split(":")[0], detalle=str(ex))
    proc = {k: pv_b3.get(k) for k in ("tarea", "raiz", "salida", "corrida_id", "identidad_sha256", "arbol_sha256", "aceptacion_sha256", "reproduccion")}
    sred = None
    if tarea == "R1-A1":
        try:
            sred = OPm._sred_validados(T, sred_paquete, sred_ejecucion, artefactos)
        except Exception as ex:  # noqa: BLE001  (RutaError, ValueError, OSError: rechazo controlado)
            return rech("SRED_NO_VALIDADO", detalle=str(ex)[:300])
    res = OPm._intercambio(tarea, cs, {"docs": docs, "sha256": leidos, "origen": proc}, sred)
    if arbol(Path(pv_b3["salida"])) != pv_b3["arbol"]:
        return rech("PRODUCTO_B3_ALTERADO_DURANTE_EL_INTERCAMBIO")
    if sred and any(sha((Path(sred_paquete) / a).read_bytes()) != h for a, h in sred["sha256"].items()):
        return rech("SRED_ALTERADO_DURANTE_EL_INTERCAMBIO")
    ok = res["correspondencia_completa"]
    return dict(base, **res, completo=ok, aceptable=ok, rechazo=None, procedencia=proc, sred=(sred or {}).get("origen"))


def _validar_ruta(P, RR, RP, OPm, tarea: str, salida: Path, plan_ruta: dict, rcs: dict, op, aut, prov: dict, sred_ejec,
                  identidad_del_calculo=None) -> tuple:
    """[VALIDACIÓN] de una ruta por comando, en el orden de tarea_r1.main / ruta_intercambio: A1/A2 por el intercambio (con el enlace
    local); B3 y A3 por opciones_p1.validacion_inicial y generar_r1_opcion (igualdad diferida a su comparación); B1, B2 y F por
    r1_rutas.validar y generar_r1_ruta (cada salida igual a la histórica del mismo comando)."""
    paquete = salida / "paquete"
    if op == "A1A2_INTERCAMBIO_DE_TESTIGOS":
        with regla_sred(RR, OPm, tarea) as isr:                     # IGUALDAD-SRED-TIEMPOS-v1 (solo R1-A1); si no, None
            x = intercambio_local(OPm, tarea, prov.get("R1-B3"), paquete if sred_ejec else None, sred_ejec, plan_ruta["artefactos_del_trabajador"])
        if isr is not None:
            x = dict(x, igualdad_sred=isr)
        (paquete / ("intercambio_%s.json" % tarea)).write_bytes(json.dumps(x, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8"))
        ev = {"opcion": op, "cumple": bool(x["aceptable"]), "codigos": [] if x["aceptable"] else [(x.get("rechazo") or {}).get("codigo") or "CORRESPONDENCIA_INCOMPLETA"],
              "intercambio": {k: x.get(k) for k in ("satisfechos", "requeridos", "rechazo", "procedencia", "sred")}, "autorizacion": aut}
        if isr is not None:
            ev["igualdad_sred"] = isr
        reg = RP.generar_r1_opcion(P, salida, tarea, ev, salida=salida / "registro_productivo.json", dictamen=salida / "dictamen_validacion.json")
        detalle, validador = ev["intercambio"], "fam02.intercambio_local + registro_productivo.generar_r1_opcion"
        if isr is not None:
            detalle = dict(detalle, igualdad_sred={s: {k: r.get(k) for k in ("igual", "por", "entradas", "diferencias_de_tiempo")} for s, r in isr["salidas"].items()})
            validador += " (igualdad SRED con IGUALDAD-SRED-TIEMPOS-v1)"
    elif op in ("B3_VALIDEZ_Y_COMPARACION", "A3_CRITERIO_GLOBAL"):
        ev = dict(OPm.validacion_inicial(op, plan_ruta, T, paquete, rcs), autorizacion=aut)
        reg = RP.generar_r1_opcion(P, salida, tarea, ev, salida=salida / "registro_productivo.json", dictamen=salida / "dictamen_validacion.json")
        detalle = {k: ev.get(k) for k in ("codigos", "comandos", "ids", "ids_sin_salida", "observaciones_resueltas", "observaciones_pendientes", "igualdad_historica")}
        validador = "opciones_p1.validacion_inicial + registro_productivo.generar_r1_opcion"
    else:
        ident = identidad_del_calculo if identidad_del_calculo is not None else getattr(P.ctx, "identity_sha256", None)
        with regla_r1f(RR, tarea, plan_ruta) as ig, regla_r1b(RR, tarea, plan_ruta, P.ctx, ident) as ib:   # R1-F / R1-B1-B2; si no, None
            reg = RP.generar_r1_ruta(P, salida, tarea, plan_ruta, rcs, salida=salida / "registro_productivo.json", dictamen=salida / "dictamen_validacion.json")
        v = reg["verificacion"]["validacion_ruta"]
        detalle = {k: v.get(k) for k in ("codigos", "comandos", "salidas_validadas", "ids", "n_ids_sin_salida", "fallos", "faltan", "ajenos")}
        validador = "r1_rutas.validar + registro_productivo.generar_r1_ruta"
        if ig is not None:
            detalle["igualdad_r1f"] = ig
            validador += " (igualdad con IGUALDAD-R1F-TIEMPOS-v1)"
        if ib is not None:
            detalle["igualdad_r1b"] = ib
            validador += " (igualdad con IGUALDAD-R1B-TIEMPOS-v1)"
    u = reg["unidades"]["R1:" + tarea]
    return reg, {"estado": u["estado"], "cumple": reg["verificacion"]["cumple"], "codigos": reg["verificacion"]["codigos"], "validador": validador,
                 "detalle": detalle, "registro": "registro_productivo.json", "registro_sha256": sha((salida / "registro_productivo.json").read_bytes())}


def _entorno(ctx, salida: Path) -> dict:
    import platform
    f = F1()
    (salida / "entorno.json").write_bytes(canon({"documento": ctx.env_doc, "records_sin_lanzadores": ctx.env_rec, "environment_sha256": ctx.technical["environment_sha256"]}) + b"\n")
    return {"conforms": ctx.env_doc.get("conforms"), "mismatches": ctx.env_doc.get("mismatches"), "documento": "entorno.json",
            "f2": f.equivalencia_f2(ctx.env_doc, ctx.env_rec, ctx.technical["environment_sha256"]),
            "f2_alcance": "adoptada para FAM01; para FAM02, propuesta (RESULTADO_FAM02.md)", "python": platform.python_version(),
            "hash_seed": os.environ.get("PYTHONHASHSEED"), "hash_randomization": sys.flags.hash_randomization,
            "hilos": {k: os.environ.get(k) for k in f.HILOS}, "TZ": os.environ.get("TZ")}


def correr_ruta(tarea: str, salida: Path, conexion: bool = False) -> dict:
    """fam02-unidad para A1, A2, A3×4, B1, B2, B3 y F: dependencias por el enlace local -> contexto S6 -> preflight, plan del orquestador
    y derivación de la ruta (artefacto del preflight declarado) -> [CÁLCULO: comandos históricos con tarea_r1.ejecutar_ruta; con
    conexion=True, salidas guardadas en su lugar] -> [VALIDACIÓN: _validar_ruta] -> enlace de aceptación si la validación cumple."""
    import contextlib
    import io
    f = F1()
    t0, c0 = time.time(), time.process_time()
    plan, cob = plan_r1(), cobertura()
    need(tarea in [t["id"] for t in plan["r1"]], "TAREA_FUERA_DEL_PLAN")
    preparar()
    TR = cargar("tarea_r1", INST / "herramientas/b/tarea_r1.py")
    need(tarea in TR.RUTAS_POR_COMANDO, "TAREA_SIN_RUTA_POR_COMANDO: %s" % tarea)
    malos = fuentes_alteradas()
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam02.json; no se calcula): %s" % malos[:5])
    RP = TR._carga("registro_productivo", "herramientas/b/registro_productivo.py")
    salida = Path(salida)
    E = salida.resolve().parent
    acept, prov, rech = aceptados(E, (CONSUMO.get(tarea) or ([], None))[0], RP)
    need(not rech, "DEPENDENCIA_NO_ACEPTADA_EN_ESTA_EJECUCION (no se calcula): %s" % rech)
    need(conexion or all(p["reproduccion"] for p in prov.values()), "DEPENDENCIA_DE_UNA_PRUEBA_DE_CONEXION_EN_UN_CALCULO: %s" % sorted(x for x in prov if not prov[x]["reproduccion"]))
    salida.mkdir(parents=True, exist_ok=False)
    salida = salida.resolve()
    rastro = f.Rastro()
    ctx = contexto()
    P, RS, RR, TR = pila(ctx)
    OPm = TR._carga("opciones_p1", "herramientas/b/opciones_p1.py")
    t_ctx = round(time.time() - t0, 2)
    t1 = time.time()
    pre = P.preflight(tarea, ids_de(tarea, cob))
    paquete = salida / "paquete"
    po = plan_orquestador(P, paquete / "plan_orquestador_s6.json")
    need(po["igual_al_historico_en_afirmaciones_rutas_y_dependencias"], "PLAN_ORQUESTADOR_S6_DISTINTO_DEL_HISTORICO")
    plan_ruta = RR.derivar(tarea, T)
    plan_ruta["artefactos_del_trabajador"] = {RR.ARTEFACTO_PREFLIGHT: po["sha256"]}
    op, aut = opcion_activa(OPm, tarea)
    importados = TR.preflight_comandos(RR, RS, plan_ruta, T, ctx)
    t_pre = round(time.time() - t1, 2)
    # ---- [CÁLCULO] comandos históricos bajo S6 (o, en la prueba de conexión, sus salidas guardadas)
    t2 = time.time()
    ejecutar = (lambda pr, ar: salidas_guardadas(RR, pr, paquete, ar)) if conexion else (lambda pr, ar: TR.ejecutar_ruta(RR, RS, pr, T, paquete, ar, ctx))
    buf, sred_ejec, rcs, regs, cmds, motivo_calc = io.StringIO(), None, {}, {}, list(plan_ruta["comandos"]), None
    try:
        with contextlib.redirect_stdout(buf):
            if op == "A1A2_INTERCAMBIO_DE_TESTIGOS":                   # opción A1/A2: SUPC no se ejecuta; A1 genera su SRED, A2 no ejecuta productor
                cmds = []
                if tarea == "R1-A1":
                    ps = OPm.plan_sred(T)
                    cmds = ps["comandos"]
                    rcs, regs = ejecutar(ps, {})
                    sred_ejec = (rcs, regs)
            else:
                archivos = {}
                dep = plan_ruta.get("entrada_de_dependencia")
                if dep:                                                # L de A3: el certificado U ACEPTADO de su tarea U (enlace local)
                    d0, dz = acept[dep["tarea"]], dep["tarea"].split("-")[2]
                    cands = [a for a in json.loads((d0 / "r1_productos.json").read_bytes())["archivos"]       # patrón de opciones_p1.a3_cota_U
                             if a.startswith("demo/hito2/") and ("puntos_U_%s" % dz in a or "certificar_U_%s" % dz in a)]
                    need(len(cands) == 1, "CERTIFICADO_U_NO_UNICO_EN_EL_PRODUCTO_ACEPTADO: %s" % cands)
                    archivos[dep["tarea"]] = d0 / "paquete" / cands[0]
                rcs, regs = ejecutar(plan_ruta, archivos)
    except Exception as ex:  # noqa: BLE001  (RutaError de preparar, etc.: el cálculo no terminó)
        motivo_calc = "%s: %s" % (type(ex).__name__, str(ex)[:300])
    t_calc = round(time.time() - t2, 2)
    calc_ok = motivo_calc is None and all(rcs.get(n) == 0 and not (regs.get(n) or {}).get("errores") for n in range(len(cmds)))
    # ---- [VALIDACIÓN]
    t3 = time.time()
    reg, val = _validar_ruta(P, RR, RP, OPm, tarea, salida, plan_ruta, rcs, op, aut, prov, sred_ejec)
    t_val = round(time.time() - t3, 2)
    ej = {"comando": "fam02-unidad", "tarea": tarea, "ruta": ruta_de_tarea(tarea), "naturaleza": NATURALEZA_CONEXION if conexion else NATURALEZA_CALCULO,
          "reproduccion": (not conexion) and all(p["reproduccion"] for p in prov.values()),
          "dependencias_consumidas": {x: {k: prov[x][k] for k in ("salida", "arbol_sha256", "aceptacion_sha256", "reproduccion")} for x in sorted(prov)},
          "preflight": {k: pre[k] for k in ("registro_v4_igual_a_afirmaciones_s6", "afirmaciones", "productor", "ids", "extremos_resueltos", "ids_no_resueltos", "nota") if k in pre},
          "plan_orquestador": po,
          "ruta_derivada": {"comandos": [{k: c[k] for k in ("entrega", "registro", "registro_sha256", "modulo", "argv")} for c in plan_ruta["comandos"]],
                            "comandos_ejecutados_o_sustituidos": [{k: c[k] for k in ("entrega", "registro", "modulo", "argv")} for c in cmds],
                            "observaciones": [o["codigo"] for o in plan_ruta["observaciones"]], "entrada_de_dependencia": plan_ruta.get("entrada_de_dependencia"),
                            "opcion": op, "activacion_de_la_opcion": aut, "importados": importados, "san_rutas": RR._san_rutas},
          "calculo": {"estado": "terminado" if calc_ok else "incompleto", "motivo": motivo_calc, "rcs": {str(k): v for k, v in rcs.items()},
                      "comandos": {str(k): v for k, v in regs.items()}, "salida_de_los_comandos": buf.getvalue()[-4000:]},
          "validacion": val, "identidad_contexto_sha256": getattr(ctx, "identity_sha256", None), "tecnicas": ctx.technical, "entorno": _entorno(ctx, salida),
          "tiempos_s": {"contexto": t_ctx, "preflight": t_pre, "calculo": t_calc, "validacion": t_val, "total": round(time.time() - t0, 2),
                        "cpu": round(time.process_time() - c0, 2)},
          "dependencias_fuera_de_la_biblioteca_estandar": f.dependencias_cargadas()}
    ej["exito"] = bool(calc_ok and val["cumple"] is True)
    (salida / "archivos_leidos.json").write_bytes((json.dumps(rastro.informe(), ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    (salida / "ejecucion.json").write_bytes(json.dumps(ej, ensure_ascii=False, indent=1, sort_keys=True, default=str).encode("utf-8") + b"\n")
    ej["aceptacion"] = aceptar(salida, RP) if ej["exito"] else {"aceptada": False, "motivos": ["CALCULO_O_VALIDACION_NO_CUMPLE"]}
    return ej


def validacion_global(salida: Path) -> dict:
    """fam02-unidad --tarea R1-V: SIN CÁLCULO. registro_productivo.generar_r1_global (= tarea_r1.main, rama R1-V) sobre el cierre de las
    dependencias del plan (D, F y las 15 de D) con las procedencias del ENLACE LOCAL de esta ejecución; consumo D -> V por el
    paquete/dependencias_consumidas.json de D. Las que no tienen enlace se informan y la validación global las rechaza."""
    f = F1()
    t0 = time.time()
    plan, cob = plan_r1(), cobertura()
    preparar()
    TR = cargar("tarea_r1", INST / "herramientas/b/tarea_r1.py")
    RP = TR._carga("registro_productivo", "herramientas/b/registro_productivo.py")
    malos = fuentes_alteradas()
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam02.json): %s" % malos[:5])
    salida = Path(salida)
    E = salida.resolve().parent
    pl = {"tareas": [], "r1": plan["r1"]}
    por_id = {x["id"]: x for x in plan["r1"]}
    cierre = TR.cierre_dependencias(pl, por_id["R1-V"])
    acept, prov, rech = aceptados(E, cierre, RP)
    salida.mkdir(parents=True, exist_ok=False)
    salida = salida.resolve()
    rastro = f.Rastro()
    ctx = contexto()
    P, RS, RR, TR = pila(ctx)
    pre = P.preflight("R1-V", ids_de("R1-V", cob))
    po = plan_orquestador(P, salida / "paquete" / "plan_orquestador_s6.json")
    need(po["igual_al_historico_en_afirmaciones_rutas_y_dependencias"], "PLAN_ORQUESTADOR_S6_DISTINTO_DEL_HISTORICO")
    reg = RP.generar_r1_global(P, salida, "R1-V", {x: _sin_arbol(prov[x]) for x in acept}, cierre,
                               consumos={x: [d for d in por_id[x]["depende_de_expandido"] if d != "F0"] for x in TR.CONSUMO_REGISTRADO if x in cierre},
                               artefactos={RR.ARTEFACTO_PREFLIGHT: po["sha256"]}, salida=salida / "registro_productivo.json", dictamen=salida / "dictamen_validacion.json")
    vg = json.loads((salida / "validacion_global.json").read_bytes())
    u = reg["unidades"]["R1:R1-V"]
    val = {"estado": u["estado"], "cumple": reg["verificacion"]["cumple"], "codigos": reg["verificacion"]["codigos"],
           "validador": "registro_productivo.generar_r1_global (validar_global de r1_s6)", "registro": "registro_productivo.json",
           "registro_sha256": sha((salida / "registro_productivo.json").read_bytes()),
           "detalle": {"validacion_global": vg.get("validacion_global"), "fuentes_ligadas": sorted(vg.get("fuentes") or {}), "fuentes_rechazadas": vg.get("fuentes_rechazadas"),
                       "fuentes_ajenas": vg.get("fuentes_ajenas"), "enlace_de_consumo": vg.get("enlace_de_consumo"), "tareas_del_plan": vg.get("tareas_del_plan")}}
    ej = {"comando": "fam02-unidad", "tarea": "R1-V", "ruta": ruta_de_tarea("R1-V"), "naturaleza": "validación global: sin cálculo",
          "reproduccion": not rech and bool(prov) and all(p["reproduccion"] for p in prov.values()),
          "dependencias_consumidas": {x: {k: prov[x][k] for k in ("salida", "arbol_sha256", "aceptacion_sha256", "reproduccion")} for x in sorted(prov)},
          "dependencias_sin_aceptacion": rech, "preflight": {k: pre[k] for k in ("registro_v4_igual_a_afirmaciones_s6", "afirmaciones", "productor", "nota") if k in pre},
          "plan_orquestador": po, "calculo": {"estado": "no_aplica", "motivo": "R1-V no calcula"}, "validacion": val,
          "identidad_contexto_sha256": getattr(ctx, "identity_sha256", None), "tecnicas": ctx.technical, "entorno": _entorno(ctx, salida),
          "tiempos_s": {"total": round(time.time() - t0, 2)}, "dependencias_fuera_de_la_biblioteca_estandar": f.dependencias_cargadas()}
    ej["exito"] = val["cumple"] is True
    (salida / "archivos_leidos.json").write_bytes((json.dumps(rastro.informe(), ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    (salida / "ejecucion.json").write_bytes(json.dumps(ej, ensure_ascii=False, indent=1, sort_keys=True, default=str).encode("utf-8") + b"\n")
    ej["aceptacion"] = aceptar(salida, RP) if ej["exito"] else {"aceptada": False, "motivos": ["VALIDACION_GLOBAL_NO_CUMPLE"]}
    return ej


def unidad(tarea: str, hojas, salida: Path, tope: float = 600.0, conexion: bool = False) -> dict:
    """fam02-unidad: despacho por tarea (C y D: orquestador; A*, B*, F: comandos; V: validación global)."""
    if tarea == "R1-V":
        need(not hojas and not conexion, "R1-V_SIN_HOJAS_NI_PRUEBA_DE_CONEXION (no calcula)")
        return validacion_global(salida)
    if tarea.startswith("R1-C") or tarea == "R1-D":
        need(not conexion, "PRUEBA_DE_CONEXION_SOLO_EN_RUTAS_POR_COMANDO: las hojas C/D no tienen salida guardada en el formato del orquestador")
        return correr(tarea, hojas, salida, tope=tope)
    need(not hojas, "HOJAS_SOLO_EN_TAREAS_C")
    return correr_ruta(tarea, salida, conexion=conexion)


def resumen_unidad(r: dict) -> dict:
    c, v = r.get("calculo") or {}, r.get("validacion") or {}
    return {"tarea": r["tarea"], "exito": r["exito"], "naturaleza": r.get("naturaleza"), "reproduccion": r.get("reproduccion"),
            "calculo": {k: c.get(k) for k in ("estado", "motivo", "rc_productor", "rcs", "estados") if k in c},
            "validacion": {k: v.get(k) for k in ("estado", "cumple", "codigos", "comparables", "verificados_ok", "validador") if k in v},
            "aceptacion": r.get("aceptacion"), "dependencias_consumidas": sorted(r.get("dependencias_consumidas") or {}),
            "comparacion": "no incluida: fam02-comparar", "entorno": {k: (r.get("entorno") or {}).get(k) for k in ("conforms", "mismatches")},
            "f2_equivalente": ((r.get("entorno") or {}).get("f2") or {}).get("equivalente"), "tiempos_s": r.get("tiempos_s")}


# ================================================================================================ comparación con las referencias
CAMPOS_COMPARADOS =("G (= [L, U] de la referencia)", "testigo.punto (claves de la referencia)", "testigo.indice_contexto", "estado", "testigo definitivo en la referencia")
CAMPOS_NO_COMPARADOS = {"brecha": "derivado: se comprueba = G[1] − G[0]", "inf_bb": "diagnóstico del B&B (cajas, evaluaciones, tiempo): no es objeto de la regla",
                        "ruta": "se comprueba = calculo_v5_ci_df", "testigo.contexto": "se informa (la referencia lo lista); la regla instalada usa indice_contexto",
                        "contenido_sha256": "integridad del checkpoint (Corrida.leer)", "afirmacion/sentido": "clave"}


def comparar(tarea: str, nueva: Path) -> dict:
    """fam02-comparar: compara una salida de fam02-unidad con (1) la REFERENCIA CITADA por la cobertura para la tarea (hojas E13 v4 de
    lima1913: regla instalada r1_s6.igual_a_referencia, G y testigo iguales, testigo definitivo) y (2) la MEDICIÓN HISTÓRICA autenticada
    de la hoja cuando existe (lima0754 / lima0003: verificación del orquestador). Lista los campos comparados y los que no, sin
    exclusiones por nombre; los subproductos (el otro sentido) se comparan aparte y no cuentan. Comprueba antes la ligadura de la salida
    (registro -> bytes) y la integridad de los checkpoints. Reproducción «aceptada» solo si cada requerido cumple la regla instalada
    (referencia citada o medición histórica; si la medición juzga, no puede contradecirse) con estado terminal igual al de referencia."""
    t0 = time.time()
    nueva = Path(nueva)
    ej = json.loads((nueva / "ejecucion.json").read_bytes())
    need(ej.get("tarea") == tarea, "SALIDA_DE_OTRA_TAREA: %s" % ej.get("tarea"))
    if not tarea.startswith("R1-C"):
        return comparar_ruta(tarea, nueva, ej)
    lig = ["validación ausente: falta %s" % x for x in ("registro_productivo.json", "verificacion.json", "r1_productos.json") if not (nueva / x).is_file()]
    reg = json.loads((nueva / "registro_productivo.json").read_bytes()) if not lig else {"unidades": {}}
    for u, e in reg["unidades"].items():
        if sha((nueva / e["documento"]).read_bytes()) != e["documento_sha256"]:
            lig.append("documento de %s distinto del registrado" % u)
        if sha((nueva / e["filas"]).read_bytes()) != e["filas_sha256"]:
            lig.append("filas de %s distintas de las registradas" % u)
    man = json.loads((nueva / "r1_productos.json").read_bytes())["archivos"] if (nueva / "r1_productos.json").is_file() else {}
    cd = nueva / "paquete" / "corrida"
    for rel, h in man.items():
        if not (cd / rel).is_file() or sha((cd / rel).read_bytes()) != h:
            lig.append("corrida: %s distinto del manifiesto" % rel)
    ctx = contexto()
    P, RS, RR, TR = pila(ctx)
    ref = P.referencia_cobertura(tarea)
    hist, _ = P.OB.historicos()
    C = object.__new__(P.OB.Corrida)
    C.d = cd
    req = [tuple(x) for x in ej["asignacion"]["requeridos"]]
    need(req and set(req) <= {tuple(x) for x in P.requeridos_orquestador(tarea)}, "ASIGNACION_FUERA_DE_LA_TAREA")
    filas, sub = [], []
    for c in sorted({c for c, _ in req}):
        for s in ("sup", "inf"):
            try:
                r = C.leer(c, s)
            except SystemExit as ex:
                r, err = None, str(ex)
            else:
                err = None
            fr = ref["filas"].get((c, s))
            f = {"afirmacion": c, "sentido": s, "requerido": (c, s) in set(req), "presente": r is not None, "checkpoint": err or "integro"}
            if r is not None and "G" in r:
                f["ruta_v5"] = r.get("ruta") == "calculo_v5_ci_df"
                f["brecha_coherente"] = r.get("brecha") == r["G"][1] - r["G"][0]
                f["nuevo"] = {"G": r["G"], "estado": r.get("estado"), "testigo_punto": r["testigo"]["punto"], "indice_contexto": r["testigo"]["indice_contexto"],
                              "contexto": r["testigo"].get("contexto")}
            if fr is not None and r is not None and "G" in r:
                tp = {k: float(v) for k, v in r["testigo"]["punto"].items() if k in fr["punto"]}
                f["referencia_citada"] = {"G": [fr["L"], fr["U"]], "estado": fr.get("estado"), "testigo": fr.get("testigo"),
                                          "G_igual": list(r["G"]) == [float(fr["L"]), float(fr["U"])],
                                          "diferencia_L": float(r["G"][0]) - float(fr["L"]), "diferencia_U": float(r["G"][1]) - float(fr["U"]),
                                          "intervalos_compatibles": max(float(r["G"][0]), float(fr["L"])) <= min(float(r["G"][1]), float(fr["U"])),
                                          "testigo_punto_igual": tp == {k: float(v) for k, v in fr["punto"].items()},
                                          "indice_contexto_igual": int(r["testigo"]["indice_contexto"]) == int(fr["indice_contexto"]),
                                          "contexto_igual": r["testigo"].get("contexto") == fr.get("contexto"),
                                          "estado_igual": RS.ESTADO_EQUIVALENTE.get(fr.get("estado"), fr.get("estado")) == r.get("estado"),
                                          "regla_instalada": P.igual_a_referencia(r, fr)}
            elif fr is None:
                f["referencia_citada"] = None
            if c in hist and r is not None and "G" in r:
                fuente, hv = hist[c]
                f["medicion_historica"] = {"fuente": fuente, "G": hv[s + "_G"], "estado": hv["estado_" + s], "G_igual": r["G"] == hv[s + "_G"],
                                           "testigo_igual": r["testigo"]["punto"] == hv["testigo_" + s]["punto"]
                                           and r["testigo"]["indice_contexto"] == hv["testigo_" + s]["indice_contexto"]}
            else:
                f["medicion_historica"] = None
            mh, rcit = f.get("medicion_historica"), f.get("referencia_citada")
            ok_h = mh is not None and mh["G_igual"] and mh["testigo_igual"] and RS.ESTADO_EQUIVALENTE.get(mh["estado"], mh["estado"]) == (r or {}).get("estado")
            ok_r = bool(rcit) and rcit["regla_instalada"] and rcit["estado_igual"]
            f["reproducida"] = (f["presente"] and f["checkpoint"] == "integro" and f.get("ruta_v5") and f.get("brecha_coherente")
                                and (r or {}).get("estado") in ESTADOS_TERMINALES_ADMISIBLES and (ok_h if mh is not None else ok_r) and (ok_r or rcit is None))
            (filas if f["requerido"] else sub).append(f)
    est_val = next(iter(reg["unidades"].values()))["estado"] if reg["unidades"] else "ausente"
    validada = est_val in ESTADOS_VALIDADOS
    acept = bool(filas) and all(x["reproducida"] for x in filas) and not lig and validada
    return {"comando": "fam02-comparar", "tarea": tarea, "nueva": str(nueva.name), "ligadura": {"cumple": not lig, "motivos": lig},
            "regla": "instalada (r1_s6.igual_a_referencia y orquestador_b.verificar): igualdad exacta de G y testigo; F1 (CR-R1-LIMA) conserva las reglas "
                     "instaladas; «intervalos_compatibles» se informa como dato (lima1618 §5), no sustituye la igualdad",
            "campos_comparados": CAMPOS_COMPARADOS, "campos_no_comparados": CAMPOS_NO_COMPARADOS,
            "referencia_citada": {k: ref["cita"][k] for k in ("entrega", "archivo", "sha256")},
            "requeridos": filas, "subproductos_no_cuentan": sub,
            "estado": {"reproduccion": "aceptada" if acept else "no_aceptada", "requeridos": len(filas), "reproducidos": sum(1 for x in filas if x["reproducida"]),
                       "validacion_registrada": est_val, "validada": validada},
            "segundos": round(time.time() - t0, 2)}


def _pv_local(E: Path, tarea: str, nueva: Path, RP) -> tuple:
    """Procedencia del enlace local de `tarea` en la ejecución E, exigiendo que sea la salida comparada (opciones_p1.comparar_r1 exige la
    tarea ACEPTADA con su árbol íntegro)."""
    _, prov, rech = aceptados(E, [tarea], RP)
    pv = prov.get(tarea)
    if pv is None:
        return None, rech.get(tarea)
    if Path(pv["salida"]) != Path(nueva).resolve():
        return None, "LA_SALIDA_COMPARADA_NO_ES_LA_ACEPTADA_EN_SU_EJECUCION"
    return pv, None


def b3_local(RR, OPm, pv: dict, ctx=None) -> dict:
    """= la rama B3 de opciones_p1.comparar_r1 / b3_clasificar_aceptada con la procedencia del ENLACE LOCAL: unidades requeridas de la
    cobertura, filas E13 v4 de la referencia citada y referencias XDD/CAN autenticadas; validez, igualdad y respaldo por unidad; bytes
    clasificados = los del árbol aceptado; árbol re-comprobado al terminar."""
    cob = {x["tarea"]: x for x in RR.cobertura(T)["tareas"]}
    rf = cob["R1-B3"]["referencia"]
    rf = (json.loads(rf) if isinstance(rf, str) else rf)["cita"]
    e13_raw = RR._aut(T, rf["entrega"], rf["archivo"])
    refs_raw = {a: RR._aut(T, ent, a) for ent, a in OPm.REFERENCIAS_B3}
    try:
        docs, leidos, _ = OPm._leer_b3(pv, arbol)
    except (OSError, ValueError) as ex:
        return {"rechazo": {"codigo": str(ex).split(":")[0], "detalle": str(ex)}, "resumen": {}, "requieren_dictamen": len(cob["R1-B3"]["ids"])}
    out = OPm._b3_unidades(cob["R1-B3"]["ids"], json.loads(e13_raw)["filas"], docs, {a: json.loads(b) for a, b in refs_raw.items()})
    for u in out:
        if "validez" in u:
            u["validez"]["validacion_autentica"] = u["archivo"] in leidos          # bytes leídos del árbol ACEPTADO (enlace local)
            u["validez"]["bytes_clasificados_sha256"] = leidos.get(u["archivo"])
    if arbol(Path(pv["salida"])) != pv["arbol"]:
        return {"rechazo": {"codigo": "PRODUCTO_B3_ALTERADO_DURANTE_LA_CLASIFICACION"}, "resumen": {}, "requieren_dictamen": len(cob["R1-B3"]["ids"])}
    resp = respaldo_e13_punto(out, json.loads(e13_raw)["filas"], sha(e13_raw), ctx)      # RESPALDO-E13-PUNTO-v1 (solo d-sup-N sin respaldo)
    resumen = OPm._b3_dictaminar(out)
    return {"rechazo": None, "resumen": resumen, "aceptables_sin_decision": resumen.get("conforme", 0),
            "requieren_dictamen": sum(v for k, v in resumen.items() if k != "conforme"), "bytes_clasificados": leidos,
            "e13_sha256": sha(e13_raw), "referencias_sha256": {a: sha(b) for a, b in refs_raw.items()},
            "unidades_no_conformes": [{k: u.get(k) for k in ("id", "afirmacion", "sentido", "dictamen", "comparacion")} for u in out if u.get("dictamen") != "conforme"][:20],
            "respaldo_e13_punto": resp,
            "regla": "opciones_p1._b3_unidades/_b3_dictaminar sin cambios; autenticidad = enlace local (en lugar de b3_clasificar_aceptada); "
                     "respaldo de las d-sup-N sin respaldo en E13 v4 solo por RESPALDO-E13-PUNTO-v1 (testigo recalculado con e13_referencia)"}


# ================================================================================================ RESPALDO-E13-PUNTO-v1 (solo R1-B3, d-sup-N)
# Encargo del autor del 2026-11-20. Con la decisión R1-B3A2 conservada (aceptación POR UNIDAD; «aceptada» global solo si ninguna unidad
# requiere dictamen), cada L de las unidades d-sup-N SIN respaldo en la tabla E13 v4 se acepta solo con un punto ADMISIBLE que lo respalde por
# la regla histórica E13, con la misma tolerancia y C2 y K1 en el MISMO punto. datos/fam02/respaldo_e13_d_sup_N.json DECLARA el testigo de
# cada unidad (punto y C2 citados de XDD; contexto, K1 y cota); aquí se RECALCULA todo con e13_referencia.py instalado (fijado por huella):
# citas autenticadas por inventario (Referencia.verificar_cita), L y U de XDD = los de la fila E13 v4, contexto (Referencia.contexto_de),
# K1 (Referencia.K1), cota y regla (Referencia.respaldo, TOL = 1e-12 sin cambios) y punto admisible (Referencia.admisible). La unidad pasa a
# respaldada solo si lo declarado coincide EXACTAMENTE con lo recalculado y la regla se cumple. No cambia la tabla E13 v4, ni la igualdad
# frente a la referencia, ni ninguna otra unidad (las que no son d-sup-N sin respaldo, o no son iguales a su referencia, no se tocan).
RESPALDO_E13 = {"regla": "RESPALDO-E13-PUNTO-v1",
                "datos": ("datos/fam02/respaldo_e13_d_sup_N.json", "35124d9e33416b9c106a29c8228767c57f47a09c8548cb9573e814fbcfbfe38e"),
                "e13_referencia": ("herramientas/s3/validadores/e13_referencia.py", "7870b5ad2827fde4ae978f35b5b24cf071e949a87dcd9e43511e9b76ba5b66d6"),
                "tabla_e13_sha256": "173c2c46353f864c1474793a5d6fcac6d2bd33984cfa5914a2f7d5e3a8aae0a8",
                "fuente": ("XDD", "demo/extremos/extremos_G_d.json"), "puntos": ("p_min", "p_max"), "menu": "d", "diseno": "N", "sentido": "sup"}


def respaldo_e13_punto(out: list, e13_filas: list, e13_sha: str, ctx=None) -> dict:
    """Aplica RESPALDO-E13-PUNTO-v1 a las unidades de b3_local (en el sitio: referencia_respaldada y respaldo_nuevo) y devuelve el informe.
    Sin datos, con datos o código E13 de otra huella, o con otra tabla E13, no se aplica y ninguna unidad cambia."""
    R = RESPALDO_E13
    t0 = time.time()
    inf = {"regla": R["regla"], "datos": R["datos"][0], "aplicada": False, "elegibles": 0, "respaldadas": 0, "rechazadas": {}, "declaradas_no_elegibles": []}
    filas = {(f["hoja"], f["sentido"]): f for f in e13_filas}

    def elegible(u):
        f = filas.get((u.get("afirmacion"), u.get("sentido")))
        return ("validez" in u and (u.get("comparacion") or {}).get("igual") is True and u.get("referencia_respaldada") is False and f is not None
                and (f.get("menu"), f.get("diseno"), f.get("sentido")) == (R["menu"], R["diseno"], R["sentido"]) and f.get("respalda") is not True)
    eleg = [u for u in out if elegible(u)]
    inf["elegibles"] = len(eleg)
    p = BASE / R["datos"][0]
    raw = p.read_bytes() if p.is_file() else None
    pe = INST / R["e13_referencia"][0]
    motivo = ("SIN_DATOS" if raw is None else "DATOS_DE_OTRA_HUELLA" if sha(raw) != R["datos"][1] else
              "E13_REFERENCIA_DE_OTRA_HUELLA" if sha(pe.read_bytes()) != R["e13_referencia"][1] else
              "OTRA_TABLA_E13" if e13_sha != R["tabla_e13_sha256"] else None)
    if motivo:
        inf["motivo"] = motivo
        return inf
    doc = json.loads(raw)
    pc, cc = doc["punto"], doc["C2_en_punto"]
    k = pc["localizador"][0] if len(pc["localizador"]) == 1 else None
    if not (doc.get("regla") == R["regla"] and doc.get("tabla_e13", {}).get("sha256") == R["tabla_e13_sha256"] and k in R["puntos"]
            and cc["localizador"] == ["C2", R["diseno"], k, [0, 1]] and (pc["clave"], pc["archivo"]) == R["fuente"] == (cc["clave"], cc["archivo"])):
        inf["motivo"] = "CITAS_O_DATOS_NO_ADMITIDOS"
        return inf
    decl = {}
    for e in doc["unidades"]:
        decl.setdefault(e["hoja"], []).append(e)
    preparar()
    V3 = cargar("cand_e13_referencia", pe)
    if Path(V3.__file__).resolve() != pe.resolve():
        inf["motivo"] = "E13_REFERENCIA_CARGADA_DE_OTRA_RUTA"
        return inf
    from paper2b import cobertura as COV
    from paper2b.intervalos import Iv
    q_previa = COV.q_pot
    try:
        ref = object.__new__(V3.Referencia)               # el estado que Referencia.__init__ deja para los métodos usados (sin la tabla entera)
        ref.T, ref.ctx, ref.COV, ref.Iv, ref.qpe = T, ctx if ctx is not None else contexto(), COV, Iv, V3.q_pot_exact
        COV.q_pot = V3.q_pot_exact
        ref._obj, ref._ref, ref._raw_sha = {}, {}, {}
        try:
            ref.verificar_cita(pc)                        # autentica (inventario + archivo) y comprueba el valor citado en el localizador
            ref.verificar_cita(cc)
        except V3.Rechazo as ex:
            inf["motivo"] = "CITA_NO_VERIFICADA: %s" % ex
            return inf
        g = V3.grupo(T, R["diseno"], R["menu"])
        ref.grupo = {(R["diseno"], R["menu"]): (g["full"], g["fixed"])}
        hs = sorted({u["afirmacion"] for u in eleg})
        ref.univ = V3.preparar(ref.ctx, R["diseno"], hs)["univ"] if hs else {}
        punto, c2 = pc["valor"], cc["valor"]
        pt = {q: float(punto[q]) for q in V3.STRUCT}
        adm, por = ref.admisible(punto, R["diseno"], R["menu"])
        inf.update(aplicada=True, punto={"localizador": pc["localizador"], "valor": pt, "admisible": adm, "admisible_por": por},
                   C2_en_punto={"localizador": cc["localizador"], "valor": c2}, identidad_del_contexto=ref.ctx.identity_sha256)
        for u in eleg:
            h = u["afirmacion"]
            es = decl.get(h) or []
            if len(es) != 1:
                inf["rechazadas"][h] = ["SIN_TESTIGO_DECLARADO" if not es else "TESTIGO_DECLARADO_REPETIDO"]
                continue
            e, f = es[0], filas[(h, R["sentido"])]
            (L, U), _ = ref.cita(R["fuente"][0], R["fuente"][1], ["afirmaciones", h, "sup_G"])
            idx = ref.contexto_de(h, R["sentido"])
            c = ref.univ[h][idx]
            k1 = ref.K1(pt, c)
            cota, ok = ref.respaldo(R["sentido"], c2, k1, L, U)
            mot = [m for m, malo in (
                ("L_U_DE_XDD_DISTINTOS_DE_LA_FILA_E13", [L, U] != [f["L"], f["U"]] or u["comparacion"]["referencia"] != [f["L"], f["U"]]),
                ("L_U_DECLARADOS_DISTINTOS", [e.get("L"), e.get("U")] != [L, U] or e.get("sentido") != R["sentido"]),
                ("PUNTO_NO_ADMISIBLE", not adm),
                ("CONTEXTO_DISTINTO", e.get("indice_contexto") != idx or e.get("contexto") != ref.ctx_key(c)),
                ("K1_DISTINTO", e.get("K1_en_punto") != [k1.lo, k1.hi]),
                ("COTA_DISTINTA", e.get("cota") != cota),
                ("NO_RESPALDA_L", not ok)) if malo]
            if mot:
                inf["rechazadas"][h] = mot
                continue
            u["referencia_respaldada"] = True
            u["respaldo_nuevo"] = {"regla": R["regla"], "punto": pc["localizador"][0], "C2_en_punto": list(c2), "indice_contexto": idx,
                                   "K1_en_punto": [k1.lo, k1.hi], "cota": cota, "L": L, "cota_menos_L": cota - L, "tolerancia": V3.TOL * max(1.0, abs(L))}
            inf["respaldadas"] += 1
        inf["declaradas_no_elegibles"] = sorted(set(decl) - {u["afirmacion"] for u in eleg})
    finally:
        COV.q_pot = q_previa
    inf["segundos"] = round(time.time() - t0, 2)
    return inf


def comparar_ruta(tarea: str, nueva: Path, ej: dict) -> dict:
    """fam02-comparar de A*, B*, F, D y V. Ligadura y validación registrada admisible (_registro_admisible) y, por ruta:
    B1/B2/F: cada salida igual a la histórica del MISMO comando (r1_rutas.validar, ya en la validación); B3: clasificación por unidad
    (b3_local); A1/A2: correspondencia de testigos (intercambio de la validación); A3-U: se compara en su par L; A3-L: el par por el
    criterio global (opciones_p1.a3_contexto + a3_evaluar con el enlace local); D: verificación del orquestador (en la validación); V: la
    validación global. «aceptada» exige además reproduccion=true: una prueba de conexión nunca es reproducción."""
    t0 = time.time()
    nueva = Path(nueva).resolve()
    E = nueva.parent
    ctx = contexto()
    P, RS, RR, TR = pila(ctx)
    RP = TR._carga("registro_productivo", "herramientas/b/registro_productivo.py")
    OPm = TR._carga("opciones_p1", "herramientas/b/opciones_p1.py")
    info, lig = _registro_admisible(nueva, tarea, RP)
    repro = ej.get("reproduccion") is True
    ok_c, juicio = None, {}
    if tarea in ("R1-B1", "R1-B2", "R1-F"):
        v = json.loads((nueva / "validacion_ruta.json").read_bytes()) if (nueva / "validacion_ruta.json").is_file() else {}
        juicio = {"regla": "r1_rutas.igual_a_historica (salida del comando = la histórica del mismo comando, sin campos operativos)",
                  "salidas_validadas": v.get("salidas_validadas"), "fallos": v.get("fallos"), "faltan": v.get("faltan"), "ids": v.get("ids"),
                  "ids_sin_salida": v.get("n_ids_sin_salida")}
        ok_c = v.get("cumple") is True
        if tarea == R1F_TIEMPOS["tarea"]:                            # IGUALDAD-R1F-TIEMPOS-v1, recalculada aquí sobre los bytes
            f = nueva / "paquete" / R1F_TIEMPOS["salida"]
            ig = igualdad_r1f(RR, f.read_bytes(), RR._aut(T, R1F_TIEMPOS["entrega"], R1F_TIEMPOS["salida"])) if f.is_file() else {"igual": False, "motivo": "SALIDA_FALTANTE"}
            juicio["regla"] += " + IGUALDAD-R1F-TIEMPOS-v1 (solo R1-F: /contexto_s y preparacion_s, rama_y_cota_s, por_contexto_s bajo cada afirmación)"
            juicio["igualdad_r1f"] = ig
            ok_c = ok_c and ig.get("igual") is True
        if tarea in R1B_TIEMPOS["tareas"]:                         # IGUALDAD-R1B-TIEMPOS-v1, recalculada aquí sobre los bytes
            s, hb, ob = _salidas_r1b(RR, tarea)
            f = nueva / "paquete" / s
            ig = (igualdad_r1b(RR, tarea, f.read_bytes(), hb, ob, ctx, ej.get("identidad_contexto_sha256")) if f.is_file()
                  else {"igual": False, "motivo": "SALIDA_FALTANTE"})
            juicio["regla"] += (" + IGUALDAD-R1B-TIEMPOS-v1 (solo R1-B1/R1-B2: /C2/<d>/segundos_subintervalos y segundos_techos; identidad_sha256 "
                                "recomprobada en cada lado)")
            juicio["igualdad_r1b"] = ig
            ok_c = ok_c and ig.get("igual") is True
    elif tarea == "R1-B3":
        pv, motivo = _pv_local(E, tarea, nueva, RP)
        juicio = b3_local(RR, OPm, pv, ctx) if pv else {"rechazo": {"codigo": motivo}}
        ok_c = juicio.get("rechazo") is None and juicio.get("requieren_dictamen") == 0
        juicio["nota"] = ("decisión R1-B3A2: aceptación POR UNIDAD; «aceptada» global solo si ninguna unidad requiere dictamen (comparar_r1). Las "
                          "unidades d-sup-N sin respaldo en E13 v4 solo quedan respaldadas por RESPALDO-E13-PUNTO-v1 (punto admisible, regla E13 "
                          "histórica recalculada, misma tolerancia, C2 y K1 en el mismo punto); sin él siguen sin respaldo")
    elif tarea in ("R1-A1", "R1-A2"):
        x = json.loads((nueva / "paquete" / ("intercambio_%s.json" % tarea)).read_bytes()) if (nueva / "paquete" / ("intercambio_%s.json" % tarea)).is_file() else {}
        juicio = {k: x.get(k) for k in ("satisfechos", "requeridos", "correspondencia_completa", "rechazo", "sred")}
        juicio["testigos"] = [{k: t.get(k) for k in ("witness_of", "ok", "motivos", "fuente", "punto_producto")} for t in x.get("testigos") or []]
        ok_c = x.get("aceptable") is True
        if tarea == SRED_TIEMPOS["tarea"]:                         # IGUALDAD-SRED-TIEMPOS-v1, recalculada aquí sobre los bytes
            hist = {s: b for b, s in _salidas_sred(RR, OPm).items()}
            ig = {s: (igualdad_sred(RR, s, (nueva / "paquete" / s).read_bytes(), hist[s]) if (nueva / "paquete" / s).is_file()
                      else {"igual": False, "motivo": "SALIDA_FALTANTE"}) for s in SRED_TIEMPOS["salidas"]}
            juicio["regla_sred"] = ("IGUALDAD-SRED-TIEMPOS-v1 (solo las dos salidas SRED de R1-A1: /traza/<k>/0, tiempo de reloj; cuatro campos por "
                                    "entrada, tiempo válido; longitud, orden, cajas, L, U y resto exactos)")
            juicio["igualdad_sred"] = ig
            ok_c = ok_c and all(r.get("igual") is True for r in ig.values())
    elif tarea.startswith("R1-A3") and tarea.endswith("-U"):
        juicio = {"nota": "la U de A3 se compara en su par L (opciones_p1.comparar_r1): fam02-comparar --tarea %s" % tarea[:-1] + "L"}
    elif tarea.startswith("R1-A3"):
        d, tU = tarea.split("-")[2], tarea[:-1] + "U"
        pv_L, motivo = _pv_local(E, tarea, nueva, RP)
        _, prov, rech = aceptados(E, [tU], RP)
        if pv_L is None or tU not in prov:
            juicio = {"par": "rechazado", "motivos": [m for m in (motivo, rech.get(tU)) if m]}
        else:
            a3c = OPm.a3_contexto(T, d, pv_L["corrida_id"], RR.derivar(tU, T)["comandos"][0]["argv"])
            r = OPm.a3_evaluar(T, INST / "src/paper2b", prov[tU], pv_L, a3c, arbol)
            juicio = {k: r.get(k) for k in ("par", "brecha", "T2", "motivos", "alcance")}
            juicio["U"] = {k: (r.get("U") or {}).get(k) for k in ("aceptada", "motivos", "archivo", "sha256", "U", "punto", "filas_validas")}
            juicio["L"] = {k: (r.get("L") or {}).get(k) for k in ("aceptada", "motivos", "archivo", "sha256", "L", "estado")}
            juicio["contexto_sha256"] = sha(canon(a3c))
        ok_c = juicio.get("par") == "convergido"
    elif tarea == "R1-D":
        v = json.loads((nueva / "verificacion.json").read_bytes()) if (nueva / "verificacion.json").is_file() else {}
        juicio = {"regla": "orquestador_b.verificar (agregados, clasificación y testigos frente a las mediciones históricas) en la validación + "
                           "CIERRE-MUESTRA-R1D-v1 (muestra = cierre; 1.280 dependencias verificadas de B1/B2/B3; los 1.856 extremos de D frente a la "
                           "referencia compuesta), recalculada aquí sobre los bytes guardados",
                  "comparables": v.get("comparables"), "verificados_ok": v.get("verificados_ok"), "reproduccion_y_coherencia": v.get("reproduccion_y_coherencia")}
        juicio["cierre_muestra_r1d"] = recomprobar_r1d(P, RP, nueva)
        ok_c = v.get("reproduccion_y_coherencia") is True and juicio["cierre_muestra_r1d"]["cumple"] is True
    elif tarea == "R1-V":
        g = json.loads((nueva / "validacion_global.json").read_bytes()) if (nueva / "validacion_global.json").is_file() else {}
        juicio = {"validacion_global": g.get("validacion_global"), "fuentes_rechazadas": g.get("fuentes_rechazadas"), "enlace_de_consumo": g.get("enlace_de_consumo")}
        ok_c = (g.get("validacion_global") or {}).get("cumple") is True and not g.get("fuentes_rechazadas")
    estado = "aceptada" if (not lig and ok_c is True and repro) else "se_compara_en_su_par" if ok_c is None and not lig else "no_aceptada"
    motivos = list(lig) + ([] if repro else ["NO_ES_REPRODUCCION: %s" % (ej.get("naturaleza") or "")[:120]]) + ([] if ok_c in (True, None) else ["COMPARACION_NO_CUMPLE"])
    return {"comando": "fam02-comparar", "tarea": tarea, "nueva": nueva.name, "ligadura_y_validacion": {"cumple": not lig, "motivos": lig, "registro": info},
            "naturaleza": ej.get("naturaleza"), "reproduccion_declarada": repro, "comparacion": juicio, "comparacion_cumple": ok_c,
            "estado": {"reproduccion": estado, "motivos": motivos}, "segundos": round(time.time() - t0, 2)}


# ================================================================================================ receta completa (no se ejecuta)
def receta() -> dict:
    """fam02-receta: las 18 tareas en orden de ejecución, con dependencias, consumo de aceptados (enlace local), ruta instalada y órdenes
    del paquete limpio; qué se reutiliza (F1) y qué debe generarse en la nueva ejecución. No ejecuta nada. Lo probado de cada tarea está
    en RESULTADO_FAM02.md (conectado no es probado; probado no es reproducido)."""
    plan, cob = plan_r1(), cobertura()
    preparar()
    TR = cargar("tarea_r1", INST / "herramientas/b/tarea_r1.py")
    RR = TR._carga("r1_rutas", "herramientas/b/r1_rutas.py")
    adaptar_san_rutas(RR)                          # registros de lanzamiento públicos (SAN-RUTAS-v1), como en pila()
    por = {t["id"]: t for t in plan["r1"]}
    E, EC = "salidas/fam02/<ejecucion>", "salidas/fam02/<prueba_de_conexion>"
    pasos = []
    for tid in plan["orden_de_ejecucion"]:
        t = por[tid]
        sal = "%s/%s" % (E, tid)
        cmp_ = ["fam02-comparar", "--tarea", tid, "--nueva", sal, "--salida", sal + ".comparacion.json"]
        p = {"tarea": tid, "contenido": t["contenido"], "depende_de": t["depende_de_expandido"], "consume_aceptados": t["consume_aceptados"],
             "consume_en_la_ejecucion": (CONSUMO.get(tid) or ([], None))[0], "regla_de_consumo": (CONSUMO.get(tid) or (None, None))[1],
             "ids_cobertura": len(ids_de(tid, cob)), "presupuesto_pared_s": t["pared_s"], "ruta_instalada": ruta_de_tarea(tid), "estado": "conectada en el paquete limpio"}
        if tid.startswith("R1-C"):
            p.update(ordenes=[["fam02-unidad", "--tarea", tid, "--salida", sal], cmp_], validacion="registro_productivo.generar_r1 sin cambios (tarea completa)")
        elif tid == "R1-D":
            p.update(ordenes=[["fam02-unidad", "--tarea", tid, "--salida", sal], cmp_],
                     validacion="registro_productivo.generar_r1 sin cambios; exige las 15 dependencias aceptadas (cálculo) en la misma ejecución")
        elif tid == "R1-V":
            p.update(ordenes=[["fam02-unidad", "--tarea", tid, "--salida", sal], cmp_], validacion="registro_productivo.generar_r1_global (sin cálculo)")
        else:
            pr = RR.derivar(tid, T)
            p.update(ordenes=[["fam02-unidad", "--tarea", tid, "--salida", sal]] + ([] if tid.endswith("-U") and tid.startswith("R1-A3") else [cmp_]),
                     prueba_de_conexion=["fam02-unidad", "--tarea", tid, "--salidas-guardadas", "--salida", "%s/%s" % (EC, tid)],
                     comandos_derivados=[{"entrega": c["entrega"], "registro": c["registro"], "modulo": c["modulo"], "argv": c["argv"]} for c in pr["comandos"]],
                     observaciones_de_la_derivacion=[o["codigo"] for o in pr["observaciones"]], entrada_de_dependencia=pr.get("entrada_de_dependencia"),
                     validacion=ruta_de_tarea(tid).split(" + ", 1)[-1])
        pasos.append(p)
    return {"estado": "preparada, no ejecutada (no autoriza las 18 tareas, las 1.728 afirmaciones ni el Paso 3)",
            "orden": plan["orden_de_ejecucion"], "presupuesto": plan["presupuesto"], "enlace_local": REGLA_ENLACE, "prueba_de_conexion": NATURALEZA_CONEXION,
            "reutilizable_segun_F1": ["entradas históricas aceptadas anteriores a R1 que el método consume como datos: registro v4 (lima1941), puntos U del "
                                      "techo v3 citados por lima0754, SRED-G/N (lima1958) en el supremo cerrado de C, caja del plan C2 (certificacion), y "
                                      "los comandos/entradas históricas de las rutas por comando con sus inventarios",
                                      "referencias (cobertura lima1857, hojas E13 v4 lima1913, mediciones lima0754/lima0003, plan lima1351): solo para comparar",
                                      "salidas guardadas de los comandos (autenticadas por su inventario): solo para la prueba de conexión, nunca como reproducción"],
            "debe_generarse_en_la_nueva_ejecucion": ["las salidas de las 18 tareas; los productos que consumen A1/A2 (de B3), las L de A3 (de su U), D (hojas de "
                                                     "C1..C6 y fuentes de B1/B2/B3/A1) y V (D y F) deben ser los ACEPTADOS en esta ejecución, nunca los históricos",
                                                     "EX-R1-POSTERIORES (F1): R1-F no produce las 32 salidas de Q histórica (FAM03) ni nada posterior a lima1618"],
            "condiciones": ["intérprete de .venv-fam01 con -B -P -s -X utf8, PYTHONHASHSEED=0, TZ=UTC y las seis variables de hilos = 1",
                            "un proceso de cálculo a la vez con el lanzador que termina el árbol al agotar su límite (supervisar.py, Job de Windows)",
                            "límites de las tareas: los del presupuesto (central/prudente) y el límite ordinario de 2.400 s por tarea de la ruta histórica "
                            "(fam02-unidad --tope 2400 bajo un lanzador de 2.400 s; una tarea C completa no cabe en 600 s: central 1.289 s; R1-B1/B2 "
                            "tampoco: central 1.194 s); --tope-afirmacion 300 s del método sin cambios",
                            "una ejecución = una carpeta %s/ con una subcarpeta nueva por tarea, en el orden de «orden»; cada tarea consume solo lo "
                            "aceptado en <ejecucion>/aceptaciones/ (ENLACE-LOCAL-FAM02-v1); nada se sobrescribe" % E],
            "pasos": pasos}
