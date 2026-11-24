"""OPCIONES CANDIDATAS DE P1 (rem46; PROPUESTAS DESACTIVADAS; NO OFICIAL). Ninguna se usa en la ruta del trabajador: las rutas R1 con
decisión siguen bloqueadas (r1_rutas: observaciones de derivación). Activarlas exige la decisión del autor, una autorización que la declare
y la conexión del parámetro en el trabajador (no hecha). Aquí se implementan y se ensayan con fixtures declarados; nada se calcula.

rem47: B3 con tipos/finitud estrictos y VÍNCULO con la aceptación auténtica (sin él, nada es conforme); A3 basada en evidencia LEÍDA de los
productos aceptados y validadores existentes (ver las secciones 1 y 3).
rem48: la validación auténtica de B3 solo la emite b3_clasificar_aceptada (aceptación reconstruida por la ruta común -> lectura de los
productos autenticados -> clasificación de esos mismos datos); b3_clasificar queda como clasificador PURO de coherencia y rechaza vínculos
declarados por quien llama.
rem49: A1/A2 por la entrada de la cadena intercambio_aceptado (aceptación de B3 reconstruida, bytes verificados, SRED propio ligado a su
generación y validación; intercambio_testigos queda como auxiliar PURO sin autoridad); A3 por a3_evaluar_aceptada; activación de las opciones
por la AUTORIZACIÓN reconstruida (opciones_autorizadas) y validación/comparación conectadas (validacion_inicial, comparar_r1).
1. B3/A2 — VALIDEZ y COMPARACIÓN SEPARADAS (b3_clasificar_aceptada; b3_clasificar puro): por unidad requerida (afirmación|sentido de la cobertura R1 auténtica),
   (a) validez de la salida NUEVA bajo S6 con sus propios certificados (estado convergida, encierro [L, U] finito con L <= U, brecha
   declarada = U − L y <= T2_G del contrato histórico, T2_G sin cambios); (b) igualdad o divergencia frente a la referencia (fila E13 v4 =
   valor citado de XDD/CAN); (c) respaldo de la referencia (E13 v4 «respalda»). Dictamen por unidad: conforme (válida, igual y
   respaldada) | igual_a_referencia_no_respaldada (NO la rehabilita) | divergente_conservada (con su diferencia; NO sustituye la
   referencia) | salida_no_valida (aunque sea igual). Nunca se cambia una referencia.
2. A1/A2 — INTERCAMBIO DE TESTIGOS (intercambio_testigos): A2 = 4 testigos ínfimos d/f desde el producto ACEPTADO de R1-B3; A1 = 4 supremos
   d/f desde R1-B3 + 2 df desde SRED-G/N (producidos por la propia A1). Correspondencia EXACTA: unidad (witness_of), fuente (archivo de la
   referencia), localizador, identidad (procedencia reconstruida: raíz, corrida, identidad y árbol aceptados), contrato (registro del
   validador R1 de la tarea R1-B3 que lista el archivo) y punto θ estructural (las tasas adicionales del archivo SRED se registran aparte).
   Una dependencia no se acepta porque el archivo exista.
3. A3 — CRITERIO GLOBAL HISTÓRICO (a3_evaluar), limitado a las 4 rutas A3: U = techo v3 certificado en un punto admisible (con su
   evidencia), del productor de la corrida (no copia de la instantánea histórica); L = cota inferior global (INFBB5) podada con la U ACEPTADA
   de la corrida; mismo problema, dominio y ω exacto; aceptación de U SEPARADA de la convergencia del par: L <= U y U − L <= T2 = 1e-4
   -> convergido; si no, pendiente (o incompatible si L > U). No sustituye el requisito puntual 1e-7 ni admite un certificado C2 global
   como techo puntual."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

ESTADO = "PROPUESTA DESACTIVADA (rem46): requiere decisión del autor y autorización que la declare"
OPCIONES = ("B3_VALIDEZ_Y_COMPARACION", "A1A2_INTERCAMBIO_DE_TESTIGOS", "A3_CRITERIO_GLOBAL")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _loc(doc, ruta):
    for k in ruta:
        doc = doc[k]
    return doc


def _id(af, se):
    return hashlib.sha256(("%s|%s" % (af, se)).encode("utf-8")).hexdigest()[:16]


# ------------------------------------------------------------------------------------------------ 1. B3/A2
# rem47 (P4-P1-B3-FINITUD). QUÉ VALIDA b3_clasificar: la COHERENCIA CONTRACTUAL de los campos de la salida nueva por unidad (tipos numéricos,
# finitud, encierro [L, U] con L <= U, estado «convergida», brecha numérica, finita, >= 0, igual a U − L y <= T2_G del contrato, T2_G de la
# salida = T2_G de la referencia). NO es una certificación numérica: la validez numérica la aporta la VALIDACIÓN AUTÉNTICA del producto.
# rem48: esa validación NO se recibe como argumento: b3_clasificar_aceptada la OBTIENE ella misma (aceptación de R1-B3 reconstruida por la
# ruta común —autoridad, identidad, árbol íntegro, registro del validador R1— y bytes leídos = los del árbol aceptado) y clasifica esos
# documentos; b3_clasificar (puro) no confiere autenticidad. Sin esa cadena ninguna unidad es «conforme».
def _num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _meta(doc, clave, sentido):
    a = doc["afirmaciones"][clave]
    est = a.get("estado_%s" % sentido, a.get("estado"))
    return est, a.get("brecha_%s" % sentido)


def b3_campos(nue, ref_doc, ruta, clave, sentido) -> tuple:
    """Coherencia contractual de UNA unidad de la salida nueva -> (valor [L, U] o None, motivos). Rechazo CONTROLADO de ausentes, NaN,
    infinitos, tipos inválidos, intervalos incompatibles, brechas que no corresponden al intervalo o exceden el contrato."""
    mot = []
    t2r, t2n = ref_doc.get("T2_G"), nue.get("T2_G")
    if not (_num(t2r) and t2r > 0):
        mot.append("CONTRATO_T2_DE_LA_REFERENCIA_INVALIDO")
    if not (_num(t2n) and t2n == t2r):
        mot.append("CONTRATO_T2_DISTINTO_O_INVALIDO")
    try:
        val = _loc(nue, ruta)
        est, br = _meta(nue, clave, sentido)
    except (KeyError, TypeError, IndexError, AttributeError) as ex:
        return None, mot + ["SALIDA_SIN_LA_UNIDAD:%s" % type(ex).__name__]
    if not (isinstance(val, (list, tuple)) and len(val) == 2 and _num(val[0]) and _num(val[1])):
        return None, mot + ["COTAS_AUSENTES_NO_NUMERICAS_O_NO_FINITAS"]
    L, U = float(val[0]), float(val[1])
    if L > U:
        mot.append("INTERVALO_INCOMPATIBLE")
    if est != "convergida":
        mot.append("NO_CONVERGIDA:%s" % est)
    if not _num(br):
        mot.append("BRECHA_AUSENTE_NO_NUMERICA_O_NO_FINITA")
    elif br < 0:
        mot.append("BRECHA_NEGATIVA")
    elif abs(br - (U - L)) > 1e-12 * max(1.0, abs(U), abs(L)):
        mot.append("BRECHA_NO_CORRESPONDE_AL_INTERVALO")
    elif _num(t2r) and br > t2r:
        mot.append("BRECHA_SOBRE_T2_DEL_CONTRATO")
    return [L, U], mot


B3_TAREA = "R1-B3"
B3_ARCHIVOS = ("demo/extremos/extremos_G_d.json", "demo/extremos/extremos_G_f.json")


def _ruta_comun():
    """rem48: la RUTA COMÚN es el corrida_paso4 HERMANO de este archivo (el mismo que usa el coordinador). Si ya hay un módulo
    «corrida_paso4» cargado desde OTRO archivo, se rechaza: la autenticidad de B3 nunca se obtiene de un homónimo del sys.path."""
    p = Path(__file__).resolve().with_name("corrida_paso4.py")
    m = sys.modules.get("corrida_paso4")
    if m is not None:
        if Path(getattr(m, "__file__", "") or "").resolve() != p:
            raise ValueError("B3_RUTA_COMUN_AJENA:%s" % getattr(m, "__file__", None))
        return m
    import importlib.util
    sp = importlib.util.spec_from_file_location("corrida_paso4", p)
    m = importlib.util.module_from_spec(sp)
    sys.modules["corrida_paso4"] = m
    sp.loader.exec_module(m)
    return m


def _leer_b3(pv: dict, arbol, archivos=B3_ARCHIVOS) -> tuple:
    """Lectura AUTENTICADA de los productos de una procedencia de R1-B3: re-enumera el árbol (= el aceptado), r1_productos.json es de R1-B3
    y lista cada archivo con el hash del árbol aceptado, y cada archivo se lee UNA vez: el documento se decodifica de ESOS bytes, cuyo sha256
    se comprueba. Devuelve ({archivo: documento}, {archivo: sha256 de los bytes leídos}, registro)."""
    sal = Path(pv["salida"])
    if arbol(sal) != pv.get("arbol"):
        raise ValueError("PRODUCTO_B3_ALTERADO_TRAS_LA_ACEPTACION")
    reg = json.loads((sal / "r1_productos.json").read_bytes())
    if reg.get("tarea") != B3_TAREA:
        raise ValueError("PRODUCTO_NO_ES_DE_R1-B3")
    docs, leidos = {}, {}
    for a in archivos:
        h = pv["arbol"].get("paquete/" + a)
        b = (sal / "paquete" / a).read_bytes()
        if h is None or (reg.get("archivos") or {}).get(a) != h or sha(b) != h:
            raise ValueError("ARCHIVO_NO_LIGADO_A_LA_ACEPTACION:%s" % a)
        docs[a], leidos[a] = json.loads(b), h
    return docs, leidos, reg


def b3_nuevas_desde_aceptacion(pv: dict, arbol, archivos=B3_ARCHIVOS) -> tuple:
    """Lectura de los productos de R1-B3 desde una procedencia (diagnóstico y A1/A2). rem48: devuelve ({archivo: documento}, descripción de
    la procedencia); esa descripción NO confiere autenticidad a nadie: la validación auténtica de B3 solo la emite b3_clasificar_aceptada."""
    docs, leidos, _ = _leer_b3(pv, arbol, archivos)
    return docs, {"tarea": B3_TAREA, "raiz": pv.get("raiz"), "identidad_sha256": pv.get("identidad_sha256"), "arbol_sha256": pv.get("arbol_sha256"),
                  "autorizacion_sha256": pv.get("autorizacion_sha256"), "archivos": leidos,
                  "nota": "descripción de lectura; no es un vínculo que b3_clasificar acepte (rem48)"}


def _b3_unidades(ids, e13_filas, nuevas: dict, referencias: dict) -> list:
    """Ejes de COHERENCIA, IGUALDAD y RESPALDO por unidad requerida, sin autenticidad (que no se deriva de los argumentos)."""
    por_id = {_id(f["hoja"], f["sentido"]): f for f in e13_filas}
    out = []
    for i in ids:
        f = por_id.get(i)
        if f is None:
            out.append({"id": i, "dictamen": "sin_fila_de_referencia"})
            continue
        fc = f["fuente_cota"]
        arch, ruta = fc["archivo"], fc["localizador"]
        clave, sentido = ruta[1], f["sentido"]
        nue = nuevas.get(arch)
        if nue is None:
            val, mot = None, ["SALIDA_NUEVA_AUSENTE"]
        else:
            val, mot = b3_campos(nue, referencias[arch], ruta, clave, sentido)
        ref = [f.get("L"), f.get("U")]
        igual = val is not None and val == ref
        out.append({"id": i, "afirmacion": f["hoja"], "sentido": sentido, "fuente": fc.get("clave"), "archivo": arch,
                    "validez": {"campos_ok": not mot, "motivos": mot, "validacion_autentica": False},
                    "comparacion": {"igual": igual, "referencia": ref, "nueva": val, "diferencia": [val[0] - ref[0], val[1] - ref[1]] if val and not igual and _num(ref[0]) and _num(ref[1]) else None},
                    "referencia_respaldada": f.get("respalda") is True, "referencia_sin_cambios": True})
    return out


def _b3_dictaminar(out: list) -> dict:
    resumen = {}
    for u in out:
        if "validez" in u:
            v = u["validez"]
            u["dictamen"] = ("salida_no_valida" if not v["campos_ok"] else "sin_validacion_autentica" if not v["validacion_autentica"] else
                             "divergente_conservada" if not u["comparacion"]["igual"] else "conforme" if u["referencia_respaldada"] else "igual_a_referencia_no_respaldada")
        resumen[u["dictamen"]] = resumen.get(u["dictamen"], 0) + 1
    return resumen


def b3_clasificar(ids, e13_filas, nuevas: dict, referencias: dict, vinculo: dict | None = None) -> dict:
    """Clasificador PURO de coherencia (rem48). ids: requeridos (cobertura R1-B3). e13_filas: filas E13 v4. nuevas: {archivo: documento}
    de la salida nueva; referencias: documentos históricos autenticados. Tres ejes SEPARADOS: validez de campos, igualdad frente a la
    referencia y respaldo de la referencia. NUNCA confiere validación auténtica: documentos entregados por quien llama no están ligados a
    una aceptación, así que ninguna unidad es «conforme» ni «igual_a_referencia_no_respaldada» por esta vía. Un vínculo declarado (nombres,
    hashes, booleanos) se RECHAZA de forma controlada: la autenticidad solo la emite b3_clasificar_aceptada. No modifica ninguna referencia."""
    if vinculo is not None:
        raise ValueError("B3_VINCULO_DECLARADO_NO_CONFIERE_AUTENTICIDAD: use b3_clasificar_aceptada (ruta común)")
    out = _b3_unidades(ids, e13_filas, nuevas, referencias)
    resumen = _b3_dictaminar(out)
    return {"opcion": "B3_VALIDEZ_Y_COMPARACION", "estado": ESTADO, "unidades": out, "resumen": resumen, "vinculo": None, "procedencia": None,
            "alcance_de_la_validacion": "SOLO coherencia contractual de campos, igualdad y respaldo; sin validación auténtica (clasificador puro); NO certificación numérica",
            "aceptables_sin_decision": 0, "requieren_dictamen": sum(resumen.values())}


def b3_clasificar_aceptada(plan: dict, raices, efectivas: dict, modo_arnes: bool, ids, e13_filas, referencias: dict) -> dict:
    """ÚNICA entrada que emite validación auténtica de B3 (rem48, P4-P1-B3 vínculo). Cadena obligatoria, sin documentos ni vínculos del
    llamante: (1) aceptación de R1-B3 RECONSTRUIDA por la ruta común (corrida_paso4.aceptaciones_previas sobre «raices» con las identidades
    efectivas y el modo actuales: corrida íntegra del plan, admisión con autoridad reconstruida, identidad, árbol aceptado byte a byte y
    productos aceptables); (2) lectura de los productos AUTENTICADOS de ESA procedencia (bytes leídos una vez, sha256 = árbol aceptado =
    r1_productos); (3) clasificación de EXACTAMENTE esos documentos; (4) el árbol se re-enumera tras clasificar (un producto sustituido
    durante la clasificación anula el resultado). Solo las unidades cuyo archivo se leyó así son auténticas. Un modo arnés queda marcado
    como PRUEBA y no es un resultado científico. Rechazos controlados: sin aceptación única de R1-B3, autoridad/entradas/despliegue
    incompatibles, árbol o archivo alterado, producto de otra tarea, ruta común ajena."""
    base = {"opcion": "B3_VALIDEZ_Y_COMPARACION", "estado": ESTADO, "entrada": "b3_clasificar_aceptada (ruta común)"}
    try:
        CO = _ruta_comun()
    except ValueError as ex:
        return dict(base, rechazo={"codigo": str(ex).split(":")[0], "detalle": str(ex)}, unidades=[], resumen={}, procedencia=None, aceptables_sin_decision=0,
                    requieren_dictamen=len(ids))
    inf = []
    pv = CO.aceptaciones_previas(plan, [str(r) for r in raices], efectivas, modo_arnes, inf).get(B3_TAREA)
    if pv is None:
        mot = [e.get("motivo") for e in inf if e.get("tarea") in (B3_TAREA, None) and e.get("motivo")]
        return dict(base, rechazo={"codigo": "SIN_ACEPTACION_AUTENTICA_DE_R1-B3", "motivos": mot or ["SIN_ACEPTACION"], "informe": inf}, unidades=[], resumen={},
                    procedencia=None, aceptables_sin_decision=0, requieren_dictamen=len(ids))
    try:
        docs, leidos, reg = _leer_b3(pv, CO._arbol)
    except (OSError, ValueError) as ex:
        return dict(base, rechazo={"codigo": str(ex).split(":")[0], "detalle": str(ex)}, unidades=[], resumen={}, procedencia=None, aceptables_sin_decision=0,
                    requieren_dictamen=len(ids))
    out = _b3_unidades(ids, e13_filas, docs, referencias)
    for u in out:
        if "validez" in u:
            u["validez"]["validacion_autentica"] = u["archivo"] in leidos
            u["validez"]["bytes_clasificados_sha256"] = leidos.get(u["archivo"])
    if CO._arbol(Path(pv["salida"])) != pv["arbol"]:
        return dict(base, rechazo={"codigo": "PRODUCTO_B3_ALTERADO_DURANTE_LA_CLASIFICACION"}, unidades=[], resumen={}, procedencia=None, aceptables_sin_decision=0,
                    requieren_dictamen=len(ids))
    resumen = _b3_dictaminar(out)
    proc = {k: pv.get(k) for k in ("tarea", "raiz", "salida", "corrida_id", "identidad_sha256", "arbol_sha256", "autorizacion_sha256", "acto_mensaje_sha256", "modo_arnes")}
    return dict(base, unidades=out, resumen=resumen, procedencia=proc, bytes_clasificados=leidos, rechazo=None,
                naturaleza=("PRUEBA DE ARNÉS: autoridad del arnés y productos declarados por su ejecutor; NO es un resultado científico" if pv.get("modo_arnes")
                            else "ruta productiva: requiere la autorización vigente de esa corrida"),
                doble_declarado=reg.get("DOBLE_DECLARADO"),
                alcance_de_la_validacion="coherencia contractual de campos + aceptación de R1-B3 reconstruida por la ruta común y bytes clasificados = bytes aceptados; NO certificación numérica",
                aceptables_sin_decision=resumen.get("conforme", 0), requieren_dictamen=sum(v for k, v in resumen.items() if k != "conforme"))


# ------------------------------------------------------------------------------------------------ 2. A1/A2
TESTIGOS = {"R1-A2": ("C2:G:d:inf", "C2:N:d:inf", "C2:G:f:inf", "C2:N:f:inf"),
            "R1-A1": ("C2:G:d:sup", "C2:N:d:sup", "C2:G:f:sup", "C2:N:f:sup", "C2:G:df:sup", "C2:N:df:sup")}
ORIGEN_B3 = {"demo/extremos/extremos_G_d.json", "demo/extremos/extremos_G_f.json"}
ORIGEN_SRED = {"demo/hito2/sred_G_df.json", "demo/hito2/sred_N_df.json"}


def _intercambio(tarea: str, cell_selection: dict, b3: dict | None, sred: dict | None) -> dict:
    """NÚCLEO PURO (rem49): correspondencia EXACTA de los testigos C2 (unidad witness_of, fuente, localizador, contexto, punto θ estructural;
    las tasas adicionales del archivo SRED se registran aparte) con documentos YA LEÍDOS. b3 / sred: {"docs": {archivo: documento},
    "sha256": {archivo: sha256 de los bytes leídos}, "origen": {...}} o None. No lee archivos ni atribuye autoridad."""
    c2 = {e["witness_of"]: e for e in cell_selection["C2"]}
    out = []
    for w in TESTIGOS[tarea]:
        e = c2.get(w)
        r = {"witness_of": w, "ok": False, "motivos": []}
        if e is None or not e.get("fuente_punto"):
            r["motivos"].append("TESTIGO_SIN_FUENTE_EN_LA_REFERENCIA")
            out.append(r)
            continue
        fp = e["fuente_punto"]
        r.update(fuente={k: fp.get(k) for k in ("entrega", "archivo", "localizador", "sha256")}, indice_contexto=e.get("indice_contexto"), contexto_de=e.get("contexto_de"),
                 cell_id=e.get("cell_id"), punto_referencia=e.get("punto"))
        if fp["archivo"] in ORIGEN_B3:
            if b3 is None or fp["archivo"] not in b3["docs"]:
                r["motivos"].append("DEPENDENCIA_R1-B3_NO_ACEPTADA")
                out.append(r)
                continue
            doc = b3["docs"][fp["archivo"]]
            r["origen"] = dict(b3["origen"], archivo=fp["archivo"], archivo_sha256=b3["sha256"][fp["archivo"]])
        elif fp["archivo"] in ORIGEN_SRED:
            if tarea != "R1-A1" or sred is None or fp["archivo"] not in sred["docs"]:
                r["motivos"].append("SRED_DE_ESTA_TAREA_AUSENTE")
                out.append(r)
                continue
            doc = sred["docs"][fp["archivo"]]
            r["origen"] = dict(sred["origen"], archivo=fp["archivo"], archivo_sha256=sred["sha256"][fp["archivo"]])
        else:
            r["motivos"].append("FUENTE_NO_PREVISTA_EN_EL_INTERCAMBIO")
            out.append(r)
            continue
        try:
            v = _loc(doc, fp["localizador"])
        except (KeyError, TypeError, IndexError):
            r["motivos"].append("LOCALIZADOR_AUSENTE_EN_EL_PRODUCTO")
            out.append(r)
            continue
        theta_k = list((e.get("punto") or {}).keys())
        if not isinstance(v, dict) or not theta_k or not set(theta_k) <= set(v):
            r["motivos"].append("PUNTO_SIN_THETA_COMPLETO")
            out.append(r)
            continue
        theta = {k: v[k] for k in theta_k}
        r["punto_producto"] = theta
        r["tasas_adicionales_del_archivo"] = {k: v[k] for k in sorted(v) if k not in theta_k}      # SRED: τ_d, τ_f (no forman parte de θ)
        if theta != e["punto"]:
            r["motivos"].append("TESTIGO_DISTINTO_DE_LA_REFERENCIA")
        r["ok"] = not r["motivos"]
        out.append(r)
    return {"testigos": out, "requeridos": len(TESTIGOS[tarea]), "satisfechos": sum(1 for x in out if x["ok"]), "correspondencia_completa": all(x["ok"] for x in out)}


def intercambio_testigos(tarea: str, cell_selection: dict, procedencias: dict, sred: dict | None = None, arbol=None) -> dict:
    """AUXILIAR PURO (rem49, P4-A1A2-VINCULO): correspondencia de testigos sobre documentos leídos de lo que DECLARA quien llama (procedencia,
    árbol, SRED). NUNCA atribuye autoridad: «aceptable» y «completo» son siempre False y la autoridad queda como declarada. La cadena usa
    intercambio_aceptado (aceptación de R1-B3 reconstruida por la ruta común, bytes verificados y SRED validado contra su generación)."""
    b3, mot = None, []
    pv = (procedencias or {}).get("R1-B3")
    if pv is not None:
        try:
            sal = Path(pv["salida"])
            docs = {a: json.loads((sal / "paquete" / a).read_bytes()) for a in B3_ARCHIVOS if (sal / "paquete" / a).is_file()}
            b3 = {"docs": docs, "sha256": {a: sha((sal / "paquete" / a).read_bytes()) for a in docs}, "origen": {"tarea": "R1-B3", "autoridad": "DECLARADA_POR_QUIEN_LLAMA"}}
        except (OSError, ValueError, KeyError, TypeError):
            mot.append("PROCEDENCIA_DECLARADA_ILEGIBLE")
    s = {"docs": dict(sred), "sha256": {a: None for a in sred}, "origen": {"tarea": "R1-A1", "autoridad": "DECLARADA_POR_QUIEN_LLAMA"}} if sred else None
    res = _intercambio(tarea, cell_selection, b3, s)
    return dict({"opcion": "A1A2_INTERCAMBIO_DE_TESTIGOS", "estado": ESTADO, "tarea": tarea, "motivos": mot}, **res, completo=False, aceptable=False,
                autoridad="DECLARADA_POR_QUIEN_LLAMA (auxiliar puro; no apto para la cadena: use intercambio_aceptado)")


def _hermano(nombre):
    """Módulo HERMANO de este archivo (r1_rutas: autenticación de la cobertura, comandos y validación de rutas); nunca un homónimo ajeno."""
    p = Path(__file__).resolve().with_name(nombre + ".py")
    m = sys.modules.get(nombre)
    if m is not None:
        if Path(getattr(m, "__file__", "") or "").resolve() != p:
            raise ValueError("MODULO_AJENO:%s" % nombre)
        return m
    import importlib.util
    sp = importlib.util.spec_from_file_location(nombre, p)
    m = importlib.util.module_from_spec(sp)
    sys.modules[nombre] = m
    sp.loader.exec_module(m)
    return m


def seleccion_c2(T) -> dict:
    """Testigos C2 de la REFERENCIA de R1-A1/A2 citada por la cobertura R1 AUTENTICADA (inventario anclado y bytes): nunca del llamante."""
    RR = _hermano("r1_rutas")
    cob = {x["tarea"]: x for x in RR.cobertura(Path(T))["tareas"]}
    c = cob["R1-A1"]["referencia"]
    c = (json.loads(c) if isinstance(c, str) else c)["cita"]
    if sha((Path(T) / c["entrega"] / "audit/entrega.json").read_bytes()) != c["inventario_sha256"]:
        raise ValueError("REFERENCIA_C2_NO_ANCLADA")
    return json.loads(RR._aut(Path(T), c["entrega"], c["archivo"]))


def plan_sred(T) -> dict:
    """Comandos AUTENTICADOS de SRED-G/N (base de A1 en r1_rutas.A1_BASE; SUPC no se ejecuta bajo la opción A1/A2)."""
    RR = _hermano("r1_rutas")
    coms = [dict(RR._comando(Path(T), e, r), salida="demo/hito2/sred_%s_df.json" % r.split("SRED-")[1][0]) for e, r in RR.A1_BASE if "/SRED-" in r]
    if len(coms) != 2:
        raise ValueError("SRED_NO_DERIVABLE")
    return {"tarea": "R1-A1", "comandos": coms, "id_fuente": {}, "observaciones": [], "nota": "SRED-G/N de la opción A1/A2 (rem49)"}


# rem50 (P4-R1-ARTEFACTO-PREFLIGHT): el artefacto del preflight lo admite la RUTA COMÚN (r1_rutas.validar) cuando el trabajador lo declara
# con su sha256 y su contenido es el del plan histórico autenticado; aquí ya no hay tolerancia propia.
def _sred_validados(T, paquete, ejecucion, artefactos=None) -> dict:
    """SRED PROPIO de esta tarea A1, todavía en validación (no aceptado): comandos autenticados de plan_sred ejecutados en ESTE paquete con
    código 0 y sin errores de importador (ejecucion = (códigos, registros) de tarea_r1.ejecutar_ruta: solo pueden RECHAZAR), salidas IGUALES
    a las históricas autenticadas del mismo comando (r1_rutas.validar) y bytes leídos UNA vez (documento decodificado de esos bytes)."""
    RR = _hermano("r1_rutas")
    ps = plan_sred(T)
    rcs, regs = ejecucion if ejecucion else ({}, {})
    if any(rcs.get(n) != 0 for n in range(len(ps["comandos"]))) or any((regs.get(n) or {}).get("errores") for n in range(len(ps["comandos"]))):
        raise ValueError("SRED_GENERACION_FALLIDA:%s" % {n: rcs.get(n) for n in range(len(ps["comandos"]))})
    v = RR.validar(dict(ps, artefactos_del_trabajador=dict(artefactos or {})), Path(T), Path(paquete), rcs)
    cods = v["codigos"]
    if cods:
        raise ValueError("SRED_NO_VALIDADO:%s" % cods)
    docs, hs = {}, {}
    for c in ps["comandos"]:
        s = c["salida"]
        b = (Path(paquete) / s).read_bytes()
        if not RR.igual_a_historica(b, RR._aut(Path(T), c["entrega"], s)):
            raise ValueError("SRED_DISTINTO_DE_LA_GENERACION_VALIDADA:%s" % s)
        docs[s], hs[s] = json.loads(b), sha(b)
    if set(docs) != ORIGEN_SRED:
        raise ValueError("SRED_INCOMPLETO")
    return {"docs": docs, "sha256": hs, "origen": {"tarea": "R1-A1", "producto": "SRED propio de esta tarea (en validación, no aceptado)",
                                                   "generacion": [{"entrega": c["entrega"], "registro": c["registro"], "registro_sha256": c["registro_sha256"]} for c in ps["comandos"]],
                                                   "validacion": {"cumple": v["cumple"], "salidas_validadas": v["salidas_validadas"], "codigos_de_la_ruta": v["codigos"],
                                                                  "artefactos_del_trabajador": v["artefactos_del_trabajador"]}, "paquete": str(Path(paquete).resolve())}}


def intercambio_aceptado(plan: dict, raices, efectivas: dict, modo_arnes: bool, tarea: str, T, sred_paquete=None, sred_ejecucion=None, artefactos=None) -> dict:
    """ENTRADA DE LA CADENA para A1/A2 (rem49, P4-A1A2-VINCULO). No recibe procedencias, árboles ni documentos: (1) la aceptación de R1-B3
    se RECONSTRUYE con corrida_paso4.aceptaciones_previas sobre «raices» (corrida actual y previas) con las identidades efectivas y el modo
    actuales (entrada previamente aceptada); (2) sus productos se leen UNA vez con los bytes del árbol aceptado; (3) para R1-A1, el SRED
    PROPIO (producto todavía en validación de ESTA tarea) se liga a su generación y validación (_sred_validados); (4) los testigos C2 se
    toman de la referencia AUTENTICADA (seleccion_c2); (5) correspondencia exacta (_intercambio); (6) el árbol de B3 y los bytes SRED se
    re-comprueban al terminar. La aceptación FINAL de esta tarea la hace después el coordinador sobre su árbol (sin circularidad)."""
    base = {"opcion": "A1A2_INTERCAMBIO_DE_TESTIGOS", "estado": ESTADO, "tarea": tarea, "entrada": "intercambio_aceptado (ruta común)"}

    def rech(cod, **x):
        return dict(base, rechazo=dict(codigo=cod, **x), testigos=[], requeridos=len(TESTIGOS.get(tarea, ())), satisfechos=0, correspondencia_completa=False,
                    completo=False, aceptable=False, procedencia=None, sred=None)
    if tarea not in TESTIGOS:
        return rech("TAREA_SIN_INTERCAMBIO")
    try:
        CO = _ruta_comun()
        cs = seleccion_c2(T)
    except Exception as ex:  # noqa: BLE001  (ruta común ajena, referencia no autenticada)
        return rech(str(ex).split(":")[0] if isinstance(ex, ValueError) else "REFERENCIA_C2_NO_AUTENTICADA", detalle=str(ex)[:200])
    inf = []
    pv = CO.aceptaciones_previas(plan, [str(r) for r in raices], efectivas, modo_arnes, inf).get(B3_TAREA)
    if pv is None:
        return rech("SIN_ACEPTACION_AUTENTICA_DE_R1-B3", motivos=[e.get("motivo") for e in inf if e.get("tarea") in (B3_TAREA, None) and e.get("motivo")] or ["SIN_ACEPTACION"])
    try:
        docs, leidos, _ = _leer_b3(pv, CO._arbol)
    except (OSError, ValueError) as ex:
        return rech(str(ex).split(":")[0], detalle=str(ex))
    proc = {k: pv.get(k) for k in ("tarea", "raiz", "salida", "corrida_id", "identidad_sha256", "arbol_sha256", "autorizacion_sha256", "acto_mensaje_sha256", "modo_arnes")}
    sred = None
    if tarea == "R1-A1":
        try:
            sred = _sred_validados(T, sred_paquete, sred_ejecucion, artefactos)
        except Exception as ex:  # noqa: BLE001  (RutaError, ValueError, OSError: rechazo controlado)
            return rech("SRED_NO_VALIDADO", detalle=str(ex)[:300])
    res = _intercambio(tarea, cs, {"docs": docs, "sha256": leidos, "origen": proc}, sred)
    if CO._arbol(Path(pv["salida"])) != pv["arbol"]:
        return rech("PRODUCTO_B3_ALTERADO_DURANTE_EL_INTERCAMBIO")
    if sred and any(sha((Path(sred_paquete) / a).read_bytes()) != h for a, h in sred["sha256"].items()):
        return rech("SRED_ALTERADO_DURANTE_EL_INTERCAMBIO")
    ok = res["correspondencia_completa"]
    return dict(base, **res, completo=ok, aceptable=ok, rechazo=None, procedencia=proc, sred=(sred or {}).get("origen"),
                naturaleza=("PRUEBA DE ARNÉS: autoridad del arnés y productos declarados por su ejecutor; NO es un resultado científico" if pv.get("modo_arnes")
                            else "ruta productiva: requiere la autorización vigente de esa corrida"))


# ------------------------------------------------------------------------------------------------ 3. A3
# rem47 (P4-P1-A3-EVIDENCIA). Nada se toma de campos declarados por quien llama: el CONTEXTO (ω/plan, dominio, problema, puntos declarados,
# huellas históricas) se DERIVA de fuentes autenticadas (a3_contexto); U y L se LEEN de los productos ACEPTADOS por la ruta común en la corrida
# (procedencia de corrida_paso4: autoridad reconstruida, árbol íntegro), con el árbol re-enumerado; la ADMISIBILIDAD de cada punto se
# RECALCULA con el validador existente (paper2b.cobertura.box_admissible sobre la caja degenerada del punto, con q_pot_exact de lima2149 y los
# fijos del grupo del plan C2 autenticado); el enlace de poda es el certificado_U que el PRODUCTO L nombra (archivo, sha256 y punto) frente al
# producto U aceptado. Criterio GLOBAL histórico (cierre_infimos): L <= U y U − L <= T2 = 1e-4. No sustituye el requisito puntual 1e-7; un
# certificado C2 global no es un techo puntual (solo semilla). LÍMITE: el positivo final requiere productos CERTA/INFBB5 NUEVOS de una corrida
# autorizada; aquí solo se ensaya con dobles estructurales declarados.
T2_A3 = 1e-4
A3_PLAN = ("certificacion_3_7_2026-10-04", "99d51784614d96a099bc3371028818d45851146e3c088131fda902dcf81ce8e5", "demo/C2/plan.json")
A3_HIST = "cierre_inf_df_paso4_3_7_2026-10-05_lima2149"
A3_REF = "demo/hito2/cierre_infimos_df.json"
CTX_OBLIGATORIO = ("corrida_id", "diseno", "omega_plan_sha256", "dominio", "problema", "puntos_declarados", "historicos_sha256")


def _aut(T, entrega, ancla, rel):
    inv_raw = (Path(T) / entrega / "audit/entrega.json").read_bytes()
    if sha(inv_raw) != ancla:
        raise ValueError("INVENTARIO_NO_ANCLADO:%s" % entrega)
    raw = (Path(T) / entrega / rel).read_bytes()
    x = json.loads(inv_raw)["files"][rel]
    if (x["sha256"] if isinstance(x, dict) else x) != sha(raw):
        raise ValueError("NO_AUTENTICADO:%s/%s" % (entrega, rel))
    return raw


def a3_grupo(T, diseno):
    raw = _aut(T, *A3_PLAN)
    plan = json.loads(raw)
    gs = [g for g in plan["grupos"] if g["clave"]["diseno"] == diseno and g["clave"]["instrumento"] == "df"]
    if len(gs) != 1:
        raise ValueError("GRUPO_NO_UNICO")
    k = gs[0]["clave"]
    return {"plan_sha256": sha(raw), "grupo": gs[0]["grupo"], "fixed": dict(k["fijos"]), "full": {p: (float.fromhex(v[0]), float.fromhex(v[1])) for p, v in k["caja"].items()}}


_QX = {}


def a3_admisible(T, diseno, theta, nucleo_s6) -> dict:
    """Admisibilidad RECALCULADA del punto exacto con el validador existente (no se lee ningún booleano del producto)."""
    import importlib
    import importlib.util as ilu
    g = a3_grupo(T, diseno)
    if not isinstance(theta, dict) or set(theta) != set(g["full"]) or not all(_num(v) for v in theta.values()):
        return {"admisible": False, "motivo": "PUNTO_INCOMPLETO_O_NO_NUMERICO", "plan_sha256": g["plan_sha256"]}
    dentro = all(g["full"][p][0] <= theta[p] <= g["full"][p][1] for p in theta)
    if "q" not in _QX:
        sp = ilu.spec_from_file_location("r1_rutas_a3", Path(__file__).resolve().parent / "r1_rutas.py")
        RR = ilu.module_from_spec(sp)
        sp.loader.exec_module(RR)
        imp = RR.ImportadorEntrega(T, A3_HIST, nucleo_s6, None)
        for k_ in [k_ for k_ in sys.modules if k_ == "codigo" or k_.startswith("codigo.")]:
            sys.modules.pop(k_)
        imp.instalar()
        try:
            _QX["q"] = importlib.import_module("codigo.demo.cobertura_compartida").q_pot_exact
        finally:
            for k_ in [k_ for k_ in sys.modules if k_ == "codigo" or k_.startswith("codigo.")]:
                sys.modules.pop(k_)
            if imp in sys.meta_path:
                sys.meta_path.remove(imp)
    from paper2b import cobertura as COV
    viejo = COV.q_pot
    COV.q_pot = _QX["q"]
    try:
        ok = bool(COV.box_admissible({p: (v, v) for p, v in theta.items()}, g["fixed"]))
    finally:
        COV.q_pot = viejo
    return {"admisible": bool(ok and dentro), "box_admissible": ok, "dentro_del_soporte": dentro, "plan_sha256": g["plan_sha256"], "grupo": g["grupo"],
            "validador": "paper2b.cobertura.box_admissible (S6) + q_pot_exact (lima2149) + fijos del grupo del plan C2 autenticado"}


def a3_contexto(T, diseno, corrida_id, comando_U_argv) -> dict:
    """Contexto DERIVADO de fuentes autenticadas: ω/plan (sha256 del plan C2 autenticado), dominio y problema (L histórica citada por el
    cierre de lima2149), puntos declarados (argumentos del comando CERTA derivado: φ y la rejilla de a sobre la esquina del grupo, como
    codigo/certificar_puntos.py) y huellas de los productos históricos (para detectar copias)."""
    g = a3_grupo(T, diseno)
    ci = json.loads(_aut(T, A3_HIST, "646202ea417e4a874498c26cd940788d26bb7dd33d4f6932e9f2eec1efa973bb", A3_REF))["disenos"][diseno]
    lrel = ci["L_fuente"]["fuente"].split(" ")[0]
    lref = json.loads(_aut(T, A3_HIST, "646202ea417e4a874498c26cd940788d26bb7dd33d4f6932e9f2eec1efa973bb", lrel))
    phi, aa = float(comando_U_argv[1]), [float(x) for x in comando_U_argv[2].split(",")]
    esq = {p: v[1] for p, v in g["full"].items()}
    esq.update(kappa_tilde=g["full"]["kappa_tilde"][0], rho=g["full"]["rho"][0], phi=phi)
    hist = sorted({x["sha256"] for x in ci["todas_U"] + ci["todas_L"] if x.get("sha256")})
    # CONTENIDO canónico de los productos históricos de lima2149 (una copia re-serializada tiene otros bytes pero el mismo contenido)
    cont = set()
    for x in ci["todas_U"] + ci["todas_L"]:
        rel = str(x.get("fuente", "")).split(" ")[0]
        if rel.startswith("demo/"):
            cont.add(_contenido(json.loads(_aut(T, A3_HIST, "646202ea417e4a874498c26cd940788d26bb7dd33d4f6932e9f2eec1efa973bb", rel))))
    return {"corrida_id": corrida_id, "diseno": diseno, "omega_plan_sha256": g["plan_sha256"], "dominio": lref["dominio"],
            "problema": {"instrumento": lref.get("instrumento"), "objeto": "inf C2 df", "diseno": diseno}, "puntos_declarados": [dict(esq, a=a) for a in aa],
            "historicos_sha256": hist, "historicos_contenido": sorted(cont)}


def _contenido(doc) -> str:
    return sha(json.dumps(doc, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def _producto(pv, arbol, tarea, ctx, patron):
    """Producto ACEPTADO por la ruta común en ESTA corrida: procedencia de la tarea, árbol re-enumerado, archivo listado en r1_productos con
    los bytes aceptados, y no copia de un producto histórico."""
    if not isinstance(pv, dict) or pv.get("tarea") != tarea or not pv.get("corrida_id") or pv.get("corrida_id") != ctx["corrida_id"]:
        return None, None, ["PROCEDENCIA_AUSENTE_O_DE_OTRA_CORRIDA"]
    sal = Path(pv["salida"])
    if arbol(sal) != pv.get("arbol"):
        return None, None, ["PRODUCTO_ALTERADO_TRAS_LA_ACEPTACION"]
    reg = json.loads((sal / "r1_productos.json").read_bytes())
    cands = [a for a in (reg.get("archivos") or {}) if patron(a)]
    if reg.get("tarea") != tarea or len(cands) != 1:
        return None, None, ["PRODUCTO_NO_UNICO_O_DE_OTRA_TAREA"]
    a = cands[0]
    h = pv["arbol"].get("paquete/" + a)
    if h is None or reg["archivos"][a] != h:
        return None, None, ["ARCHIVO_NO_LIGADO_A_LA_ACEPTACION"]
    if h in ctx["historicos_sha256"]:
        return None, None, ["COTA_COPIADA_DE_UN_PRODUCTO_HISTORICO"]
    return a, h, []


def a3_cota_U(T, nucleo_s6, pv_U, ctx, arbol) -> dict:
    d = ctx["diseno"]
    a, h, mot = _producto(pv_U, arbol, "R1-A3-%s-U" % d, ctx, lambda x: x.startswith("demo/hito2/") and ("puntos_U_%s" % d in x or "certificar_U_%s" % d in x))
    if mot:
        return {"aceptada": False, "motivos": mot}
    doc = json.loads((Path(pv_U["salida"]) / "paquete" / a).read_bytes())
    if _contenido(doc) in (ctx.get("historicos_contenido") or ()):
        return {"aceptada": False, "motivos": ["COTA_COPIADA_DE_UN_PRODUCTO_HISTORICO"]}
    if doc.get("plan_sha256") not in (None, ctx["omega_plan_sha256"]):
        return {"aceptada": False, "motivos": ["OMEGA_DISTINTO"]}
    validas, rechazos = [], []
    for n, r in enumerate(doc.get("filas") or []):
        m = []
        th, tc = r.get("theta"), r.get("techo")
        if th not in ctx["puntos_declarados"]:
            m.append("PUNTO_NO_DECLARADO_POR_EL_COMANDO")
        if not (isinstance(tc, dict) and _num(r.get("U")) and r["U"] > 0 and tc.get("U_C2") == r["U"] and isinstance(tc.get("cajas"), int) and tc["cajas"] > 0
                and isinstance(tc.get("vivas"), int) and tc["vivas"] >= 0 and tc.get("estado") in ("convergido", "tope_tiempo")):
            m.append("CERTIFICADO_SIN_EVIDENCIA_DE_TECHO_PUNTUAL")
        if r.get("incompatible") is not False:
            m.append("FILA_INCOMPATIBLE_O_SIN_DECLARAR")
        if not m:
            adm = a3_admisible(T, d, th, nucleo_s6)
            if adm["plan_sha256"] != ctx["omega_plan_sha256"]:
                m.append("OMEGA_DISTINTO")
            if not adm["admisible"]:
                m.append("PUNTO_NO_ADMISIBLE_SEGUN_EL_VALIDADOR")
            if r.get("admisible") is not adm["admisible"]:
                m.append("EVIDENCIA_DE_ADMISIBILIDAD_CONTRADICTORIA")
        (rechazos if m else validas).append({"fila": n, "U": r.get("U"), "punto": th, "motivos": m})
    if not validas:
        return {"aceptada": False, "motivos": ["SIN_FILA_VALIDA"], "filas": rechazos}
    mejor = min(validas, key=lambda x: x["U"])
    return {"aceptada": True, "motivos": [], "U": mejor["U"], "punto": mejor["punto"], "archivo": a, "sha256": h, "filas_validas": len(validas), "filas_rechazadas": rechazos,
            "nota": "U válida para el criterio GLOBAL A3; no acredita precisión puntual 1e-7"}


def a3_cota_L(pv_L, ctx, ua, arbol) -> dict:
    d = ctx["diseno"]
    a, h, mot = _producto(pv_L, arbol, "R1-A3-%s-L" % d, ctx, lambda x: x.startswith("demo/hito2/infbb") and x.endswith("_%s_df.json" % d))
    if mot:
        return {"aceptada": False, "motivos": mot}
    doc = json.loads((Path(pv_L["salida"]) / "paquete" / a).read_bytes())
    if _contenido(doc) in (ctx.get("historicos_contenido") or ()):
        return {"aceptada": False, "motivos": ["COTA_COPIADA_DE_UN_PRODUCTO_HISTORICO"]}
    m = []
    if doc.get("instrumento") != ctx["problema"]["instrumento"] or doc.get("diseno") != d:
        m.append("PROBLEMA_DISTINTO")
    if doc.get("plan_sha256") != ctx["omega_plan_sha256"]:
        m.append("OMEGA_DISTINTO_O_AUSENTE")
    if doc.get("dominio") != ctx["dominio"]:
        m.append("DOMINIO_DISTINTO_O_AUSENTE")
    if doc.get("T2") != T2_A3:
        m.append("T2_DISTINTO_DEL_CRITERIO")
    if not (_num(doc.get("L")) and _num(doc.get("U")) and _num(doc.get("brecha"))) or abs(doc["brecha"] - (doc["U"] - doc["L"])) > 1e-12:
        m.append("COTA_L_SIN_EVIDENCIA_COHERENTE")
    cu = doc.get("certificado_U") or {}
    # enlace por BYTES y punto: el comando L recibe la U aceptada copiada con el nombre de SU argumento (r1_rutas.DEPENDENCIA_DE_ENTRADA)
    if not ua.get("aceptada") or cu.get("sha256") != ua.get("sha256") or cu.get("punto") != ua.get("punto") or doc.get("U") != ua.get("U"):
        m.append("L_NO_PODADA_CON_LA_U_ACEPTADA_DE_LA_CORRIDA")
    return {"aceptada": not m, "motivos": m, "L": doc.get("L"), "archivo": a, "sha256": h, "estado": doc.get("estado"), "certificado_U_nombrado": cu}


def a3_evaluar(T, nucleo_s6, pv_U, pv_L, ctx, arbol) -> dict:
    """Par (U, L) de UN diseño por el criterio GLOBAL histórico. ctx: el de a3_contexto (obligatorio y completo)."""
    falta = [k for k in CTX_OBLIGATORIO if not (isinstance(ctx, dict) and ctx.get(k))]
    if falta:
        return {"opcion": "A3_CRITERIO_GLOBAL", "estado": ESTADO, "par": "rechazado", "motivos": ["CONTEXTO_INCOMPLETO:%s" % ",".join(falta)], "U": None, "L": None}
    ua = a3_cota_U(T, nucleo_s6, pv_U, ctx, arbol)
    la = a3_cota_L(pv_L, ctx, ua, arbol) if ua["aceptada"] else {"aceptada": False, "motivos": ["SIN_U_ACEPTADA"]}
    if not (ua["aceptada"] and la["aceptada"]):
        par = "rechazado"
    elif la["L"] > ua["U"]:
        par = "incompatible"
    elif ua["U"] - la["L"] <= T2_A3:
        par = "convergido"
    else:
        par = "pendiente"
    return {"opcion": "A3_CRITERIO_GLOBAL", "estado": ESTADO, "U": ua, "L": la, "par": par,
            "brecha": (ua["U"] - la["L"]) if ua.get("aceptada") and la.get("aceptada") else None, "T2": T2_A3,
            "alcance": "solo R1-A3-G-U/G-L/N-U/N-L (ínfimo C2 df); no sustituye el requisito puntual 1e-7"}


def a3_evaluar_aceptada(plan: dict, raices, efectivas: dict, modo_arnes: bool, diseno: str, T, nucleo_s6) -> dict:
    """ENTRADA DE LA CADENA para A3 (rem49): U y L desde aceptaciones RECONSTRUIDAS por la ruta común (nunca procedencias del llamante), con
    el árbol de la ruta común, y el contexto DERIVADO de fuentes autenticadas (a3_contexto con el comando U derivado por r1_rutas y la
    corrida de la aceptación de L). Criterio GLOBAL 1e-4; no sustituye el puntual 1e-7."""
    CO, RR = _ruta_comun(), _hermano("r1_rutas")
    inf = []
    pvs = CO.aceptaciones_previas(plan, [str(r) for r in raices], efectivas, modo_arnes, inf)
    tU, tL = "R1-A3-%s-U" % diseno, "R1-A3-%s-L" % diseno
    if tU not in pvs or tL not in pvs:
        return {"opcion": "A3_CRITERIO_GLOBAL", "estado": ESTADO, "par": "rechazado", "U": None, "L": None,
                "motivos": ["SIN_ACEPTACION_AUTENTICA_DE_%s" % x for x in (tU, tL) if x not in pvs], "informe": [e for e in inf if e.get("tarea") in (tU, tL)]}
    ctx = a3_contexto(Path(T), diseno, pvs[tL]["corrida_id"], RR.derivar(tU, Path(T))["comandos"][0]["argv"])
    r = a3_evaluar(Path(T), nucleo_s6, pvs[tU], pvs[tL], ctx, CO._arbol)
    r["procedencias"] = {x: {k: pvs[x].get(k) for k in ("raiz", "salida", "corrida_id", "identidad_sha256", "arbol_sha256", "autorizacion_sha256", "acto_mensaje_sha256", "modo_arnes")}
                         for x in (tU, tL)}
    r["contexto_sha256"] = CO.sha(CO.canon(ctx))
    return r


# ------------------------------------------------------------------------------------------------ 4. CONEXIÓN (rem49)
# Activación de una opción para UNA tarea con el MECANISMO EXISTENTE de autoridad (el mismo que sella las reglas DR-1/DR-2): la AUTORIZACIÓN
# de la admisión que cubrió la tarea se RECONSTRUYE (corrida_paso4.reconstruir_admision: bytes conservados en <raíz>/autoridad, encargo y acto
# dedicado auténticos, en el modo de la corrida; una fuente de arnés solo vale en el arnés) y ESA autorización declara «opciones_r1»: cada
# opción con el sha256 de SU texto de decisión y el sha256 de la implementación INSTALADA (este archivo), comprobados contra el CATÁLOGO
# instalado (datos/paso4/opciones_r1.json). Uso PRODUCTIVO: además del acto, el catálogo debe marcar la opción «aprobada» (hoy todas
# «propuesta»): las opciones quedan DESACTIVADAS fuera del arnés hasta la decisión aplicable y su incorporación. Sin autorización que las
# declare, la tarea sigue la ruta vigente (bloqueada por sus observaciones de derivación).
CATALOGO_REL = "datos/paso4/opciones_r1.json"
KIND_CATALOGO = "catalogo-opciones-r1-paso4-v1"
OPCION_DE_TAREA = {"R1-B3": "B3_VALIDEZ_Y_COMPARACION", "R1-A1": "A1A2_INTERCAMBIO_DE_TESTIGOS", "R1-A2": "A1A2_INTERCAMBIO_DE_TESTIGOS",
                   **{"R1-A3-%s-%s" % (d, s): "A3_CRITERIO_GLOBAL" for d in ("G", "N") for s in ("U", "L")}}


def catalogo() -> dict:
    p = Path(__file__).resolve().parents[2] / CATALOGO_REL
    doc = json.loads(p.read_bytes())
    if doc.get("kind") != KIND_CATALOGO or set(doc.get("opciones") or {}) != set(OPCIONES):
        raise ValueError("CATALOGO_DE_OPCIONES_INVALIDO")
    for k, v in doc["opciones"].items():
        if sha(v["texto"].encode("utf-8")) != v["texto_sha256"] or sorted(v["tareas"]) != sorted(t for t, o in OPCION_DE_TAREA.items() if o == k):
            raise ValueError("CATALOGO_DE_OPCIONES_INCOHERENTE:%s" % k)
    return doc


def opciones_autorizadas(plan: dict, raiz, t: dict, modo_arnes: bool) -> tuple:
    """(opciones activas para la tarea t, informe). Sin raíz de corrida, sin admisión, sin autoridad reconstruida o sin declaración: ninguna
    activa (la tarea sigue su ruta vigente). Una declaración ajena o alterada RECHAZA la activación (nunca se ignora en silencio)."""
    inf = {"tarea": t["id"], "modo_arnes": bool(modo_arnes), "activas": []}
    op = OPCION_DE_TAREA.get(t["id"])
    if op is None:
        return frozenset(), dict(inf, motivo="TAREA_SIN_OPCION")
    if not raiz or not (Path(raiz) / "diario_corrida.jsonl").is_file():
        return frozenset(), dict(inf, motivo="SIN_CORRIDA")
    try:
        CO = _ruta_comun()
    except ValueError as ex:                       # un corrida_paso4 ajeno en el proceso: rechazo controlado (ninguna opción activa)
        return frozenset(), dict(inf, motivo=str(ex))
    raiz = Path(raiz)
    ev = CO.Diario(raiz / "diario_corrida.jsonl").leer()
    ini = [e for e in ev if e.get("op") == "inicio" and e.get("tarea") == t["id"]]
    adm = [e for e in ev if e.get("op") == "admision" and t["id"] in (e.get("tareas") or []) and (not ini or e.get("t", 0) <= ini[-1].get("t", 0))]
    if not adm:
        return frozenset(), dict(inf, motivo="SIN_ADMISION")
    try:
        aut = CO.reconstruir_admision(plan, raiz, adm[-1], t, modo_arnes)
    except CO.CorridaError as ex:
        return frozenset(), dict(inf, motivo="SIN_AUTORIDAD_RECONSTRUIDA:%s" % ex.codigo)
    ab = json.loads((raiz / CO.AUTORIDAD_DIR / ("autorizacion_%s.json" % aut["autorizacion_sha256"])).read_bytes())
    inf.update(autorizacion_sha256=aut["autorizacion_sha256"], acto_mensaje_sha256=aut["acto"]["mensaje_sha256"], arnes=bool(aut["modo_arnes"]))
    decl = ab.get("opciones_r1")
    if not decl:
        return frozenset(), dict(inf, motivo="AUTORIZACION_SIN_OPCIONES")
    cat = catalogo()["opciones"]
    impl = sha(Path(__file__).resolve().read_bytes())
    activas = set()
    for x in decl if isinstance(decl, list) else [decl]:
        k = x.get("id") if isinstance(x, dict) else None
        if k not in cat or x.get("texto_sha256") != cat[k]["texto_sha256"] or x.get("implementacion_sha256") != impl:
            return frozenset(), dict(inf, motivo="OPCION_DECLARADA_AJENA_O_ALTERADA:%s" % k)
        if not modo_arnes and cat[k].get("estado") != "aprobada":
            return frozenset(), dict(inf, motivo="OPCION_NO_APROBADA_PARA_USO_PRODUCTIVO:%s" % k)
        activas.add(k)
    act = frozenset(activas & {op})
    return act, dict(inf, activas=sorted(act), declaradas=sorted(activas), motivo=None if act else "OPCION_DE_LA_TAREA_NO_DECLARADA")


def validacion_inicial(opcion: str, plan_ruta: dict, T, paquete, rcs: dict) -> dict:
    """VALIDACIÓN INICIAL de una ruta R1 por comando bajo una opción ACTIVA (B3 o A3): cada comando con código 0, sus salidas presentes,
    cada id requerido con su fuente entre esas salidas y nada ajeno en el paquete; las observaciones de derivación deben ser exactamente las
    que la opción resuelve según el catálogo. La IGUALDAD con la salida histórica no se exige aquí: se difiere a la comparación de la opción
    (B3: b3_clasificar_aceptada por unidad; A3: el par por el criterio global), que exige la aceptación previa de esta tarea."""
    RR = _hermano("r1_rutas")
    T, paquete = Path(T), Path(paquete)
    v = RR.validar(plan_ruta, T, paquete, rcs)
    res = set(catalogo()["opciones"][opcion]["observaciones_que_resuelve"])
    cmds = plan_ruta["comandos"]
    fallidos = [c["registro"] for n, c in enumerate(cmds) if rcs.get(n) != 0]
    faltan = [s for n, c in enumerate(cmds) if rcs.get(n) == 0 for s in RR.salidas_del_comando(c, T) if not (paquete / s).is_file()]
    presentes = {(c["entrega"], s) for n, c in enumerate(cmds) if rcs.get(n) == 0 for s in RR.salidas_del_comando(c, T) if (paquete / s).is_file()}
    sin = [i for i, f in plan_ruta["id_fuente"].items() if (f["entrega"], f["archivo"]) not in presentes]
    if opcion == "A3_CRITERIO_GLOBAL":            # A3: la cota de la opción es la SALIDA del comando derivado (no la instantánea histórica que cita
        sin = [] if presentes else list(plan_ruta["id_fuente"])   # la referencia); su validez se evalúa en la comparación del par (a3_evaluar_aceptada)
    pend = [o["codigo"] for o in plan_ruta.get("observaciones") or [] if o["codigo"] not in res]
    cods = [k for k, x in (("SIN_COMANDOS", not cmds), ("COMANDO_FALLIDO", fallidos), ("SALIDA_FALTANTE", faltan), ("ID_REQUERIDO_SIN_SALIDA", sin),
                           ("ARCHIVO_AJENO_EN_EL_PAQUETE", "ARCHIVO_AJENO_EN_EL_PAQUETE" in v["codigos"]),
                           ("ARTEFACTO_DEL_TRABAJADOR_NO_ADMITIDO", [x for x in v["codigos"] if x.startswith("ARTEFACTO_")]),
                           ("OBSERVACIONES_NO_RESUELTAS_POR_LA_OPCION", pend)) if x]
    return {"opcion": opcion, "cumple": not cods, "codigos": cods, "comandos": len(cmds), "ids": len(plan_ruta["id_fuente"]), "ids_sin_salida": len(sin),
            "observaciones_resueltas": sorted({o["codigo"] for o in plan_ruta.get("observaciones") or []} & res), "observaciones_pendientes": pend,
            "artefactos_del_trabajador": v["artefactos_del_trabajador"],
            "igualdad_historica": {"diferida_a": "comparación de la opción", "validacion_ruta_vigente": {"cumple": v["cumple"], "codigos": v["codigos"]}}}


def comparar_r1(plan: dict, raiz, t: dict, despliegue, fuentes, modo_arnes: bool = False, previas=(), solo_reutilizar: bool = False) -> dict:
    """COMPARACIÓN de una tarea R1 con OPCIÓN (rem49; llamada por comparar_tarea): exige la opción ACTIVA para la tarea en ESTA corrida
    (opciones_autorizadas) y la tarea ACEPTADA (árbol íntegro); B3: b3_clasificar_aceptada (validez, igualdad y respaldo separados);
    A3 (en la tarea L del par): a3_evaluar_aceptada. Productos en <raíz>/comparaciones/<tarea>/ y op «comparacion» en el diario, como R2/R3.
    «aceptado_global» solo si no queda nada que requiera dictamen (B3) o el par converge (A3).
    rem50 (P4-A3-REUTILIZACION-PAR): la validación ACTUAL se reconstruye SIEMPRE (también con --solo-reutilizar, sin escribir) y la
    CORRESPONDENCIA que da acceso a un dictamen guardado contiene la IDENTIDAD ACTUAL completa —B3: procedencia reconstruida y bytes
    clasificados; A3: aceptaciones reconstruidas de U y L (raíz, corrida, identidad, árbol, autorización, acto), cotas leídas, contexto
    derivado y criterio— más el estado y el resumen que da esa validación actual. Un rechazo actual nunca coincide con un dictamen aceptado
    antiguo. Un dictamen guardado alterado o eliminado se retira con su evidencia (op «dictamen_retirado»); uno válido de otra correspondencia
    se conserva como histórico (dictamen.<sha16>.json) antes de escribir el nuevo."""
    CO = _ruta_comun()
    raiz = Path(raiz)
    act, inf = opciones_autorizadas(plan, raiz, t, modo_arnes)
    CO.need(act, "OPCION_NO_AUTORIZADA_PARA_LA_COMPARACION", "%s: %s" % (t["id"], inf.get("motivo")))
    op = next(iter(act))
    c = json.loads((raiz / "corrida.json").read_bytes())
    ef = CO.identidades_efectivas(despliegue, {"fuentes_v2": fuentes}, {"tope_s": 1.0}, modo_arnes)   # como verificar_aceptada: sha256 contrastados por la ruta común
    CO.need(c.get("despliegue_sha256") == ef["despliegue_sha256"], "COMPARACION_CON_OTRA_IDENTIDAD_DE_CORRIDA")
    hist = CO.estado_tareas(CO.Diario(raiz / "diario_corrida.jsonl")).get(t["id"], [])
    acept = [e for e in hist if e["op"] == "fin" and e["estado"] == "completa_verificada"]
    CO.need(len(acept) == 1 and CO._arbol(raiz / "salidas" / t["id"]) == acept[0]["arbol"], "TAREA_NO_ACEPTADA_O_ALTERADA", t["id"])
    T = Path(json.loads(Path(despliegue).read_bytes())["raiz_fuentes"])
    raices = [raiz] + [Path(p) for p in previas]
    if op == "B3_VALIDEZ_Y_COMPARACION":
        RR = _hermano("r1_rutas")
        cob = {x["tarea"]: x for x in RR.cobertura(T)["tareas"]}
        rf = cob["R1-B3"]["referencia"]
        rf = (json.loads(rf) if isinstance(rf, str) else rf)["cita"]
        e13_raw = RR._aut(T, rf["entrega"], rf["archivo"])
        e13 = json.loads(e13_raw)["filas"]
        refs_raw = {a: RR._aut(T, ent, a) for ent, a in REFERENCIAS_B3}
        refs = {a: json.loads(b) for a, b in refs_raw.items()}
        out = b3_clasificar_aceptada(plan, raices, ef, modo_arnes, cob["R1-B3"]["ids"], e13, refs)
        ok = out["rechazo"] is None and out["requieren_dictamen"] == 0
        resumen = {"resumen": out["resumen"], "rechazo": out["rechazo"], "aceptables_sin_decision": out["aceptables_sin_decision"], "requieren_dictamen": out["requieren_dictamen"]}
        ident = {"procedencia": out.get("procedencia"), "bytes_clasificados": out.get("bytes_clasificados"), "e13_sha256": sha(e13_raw),
                 "referencias_sha256": {a: sha(b) for a, b in refs_raw.items()}, "ids_sha256": sha(CO.canon(cob["R1-B3"]["ids"]))}
    elif op == "A3_CRITERIO_GLOBAL" and t["id"].endswith("-L"):
        out = a3_evaluar_aceptada(plan, raices, ef, modo_arnes, t["id"].split("-")[2], T, Path(__file__).resolve().parents[2] / "src/paper2b")
        ok = out["par"] == "convergido"
        resumen = {"par": out["par"], "brecha": out.get("brecha"), "T2": out.get("T2", T2_A3)}
        ident = {"procedencias": out.get("procedencias"), "contexto_sha256": out.get("contexto_sha256"), "motivos": out.get("motivos"),
                 "U": {k: (out.get("U") or {}).get(k) for k in ("aceptada", "archivo", "sha256", "U", "punto")},
                 "L": {k: (out.get("L") or {}).get(k) for k in ("aceptada", "archivo", "sha256", "L")},
                 "criterio": {"global_T2": T2_A3, "puntual_1e-7": "no sustituido", "C2_global": "solo semilla"}}
    else:
        CO.need(False, "TAREA_SIN_COMPARACION_DE_OPCION", "%s (%s): la U de A3 se compara en su par L; A1/A2 se validan por el intercambio" % (t["id"], op))
    estado = "aceptada" if ok else "rechazada"
    cdir = raiz / "comparaciones" / t["id"]
    cor = {"tarea": t["id"], "opcion": op, "arbol_aceptado_sha256": CO.sha(CO.canon(acept[0]["arbol"])), "raices": [str(x) for x in raices], "autorizacion": inf,
           "implementacion_sha256": sha(Path(__file__).resolve().read_bytes()), "texto_de_la_opcion_sha256": catalogo()["opciones"][op]["texto_sha256"],
           "identidad_actual": ident, "estado_actual": estado, "resumen_actual": resumen}
    cb = CO.canon(cor) + b"\n"
    csha = CO.sha(cb)
    d = CO.Diario(raiz / "diario_corrida.jsonl")
    ev = d.leer()
    mias = [e for e in ev if e.get("op") == "comparacion" and e.get("tarea") == t["id"]]
    prev = [e for e in mias if e.get("correspondencia_sha256") == csha]
    dp = cdir / "dictamen.json"
    if prev and dp.is_file() and CO.sha(dp.read_bytes()) == prev[-1]["dictamen_sha256"]:
        g = json.loads(dp.read_bytes())
        if g.get("estado") == estado:                # la correspondencia ya fija el estado actual: comprobación defensiva
            return {"tarea": t["id"], "ya_comparada": True, "estado": g["estado"], "dictamen_sha256": prev[-1]["dictamen_sha256"], "correspondencia_sha256": csha, **g["resumen"]}
    if solo_reutilizar:                              # consulta: NUNCA escribe ni lanza trabajo; informa la validación actual
        return {"tarea": t["id"], "ya_comparada": False, "estado": "sin_dictamen_valido", "dictamen_sha256": None, "correspondencia_sha256": csha,
                "motivo": "DICTAMEN_ALTERADO" if prev and dp.is_file() else "DICTAMEN_AUSENTE" if prev else "SIN_COMPARACION_PARA_LA_CORRESPONDENCIA_ACTUAL",
                "validacion_actual": dict(resumen, estado=estado)}
    cdir.mkdir(parents=True, exist_ok=True)
    registrados = {e.get("dictamen_sha256") for e in mias}
    if dp.is_file():                                 # conservar SIEMPRE lo que había: histórico válido o evidencia de alteración
        h = CO.sha(dp.read_bytes())
        if h in registrados:
            dp.replace(cdir / ("dictamen.%s.json" % h[:16]))
        else:
            n = sum(1 for e in ev if e.get("op") == "dictamen_retirado" and e.get("tarea") == t["id"])
            destino = cdir / ("dictamen.alterado-%d.json" % n)
            dp.replace(destino)
            d(op="dictamen_retirado", tarea=t["id"], motivo="alterado", destino=str(destino), dictamen_sha256_encontrado=h,
              dictamen_sha256_registrado=(mias[-1].get("dictamen_sha256") if mias else None))
    elif prev:
        d(op="dictamen_retirado", tarea=t["id"], motivo="eliminado", destino=None, dictamen_sha256_registrado=prev[-1]["dictamen_sha256"])
    cp = cdir / "correspondencia.json"
    if cp.is_file() and CO.sha(cp.read_bytes()) != csha:
        cp.replace(cdir / ("correspondencia.%s.json" % CO.sha(cp.read_bytes())[:16]))
    cp.write_bytes(cb)
    g = {"estado": estado, "resumen": resumen, "resultado": out}
    db = (json.dumps(g, ensure_ascii=False, indent=1, default=str) + "\n").encode("utf-8")
    dp.write_bytes(db)
    d(op="comparacion", tarea=t["id"], correspondencia_sha256=csha, dictamen_sha256=CO.sha(db), opcion=op, aceptado_global=ok, resumen=resumen)
    return {"tarea": t["id"], "ya_comparada": False, "estado": estado, "dictamen_sha256": CO.sha(db), "correspondencia_sha256": csha, **resumen}

REFERENCIAS_B3 = (("extremos_df_d_3_7_2026-10-05_lima0738", "demo/extremos/extremos_G_d.json"), ("cierre_candidato_3_7_2026-10-04_lima2103", "demo/extremos/extremos_G_f.json"))
