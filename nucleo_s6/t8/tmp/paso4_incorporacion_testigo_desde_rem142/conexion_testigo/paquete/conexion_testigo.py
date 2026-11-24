"""rem142 — CONEXIÓN DEL TESTIGO ALTO A LA CAPTURA T8 (P4-T8-CAPTURA-TESTIGO; candidato aislado, NO habilitado; ningún alcance real ni acto).
Extensión mínima de conexion_captura.py (P = c2_conexion/candidato_v3 de rem137, f7a8d23f…; ni P ni T3 se editan): mismo patrón
puerta → contexto autenticado → cargar por la autoridad fijada → construir → ÚNICA validación común con procedencia; la única novedad es el
CONSUMO de la fuente nueva aceptada (testigo alto e8b1f7fd…, RESULTADO 981ff0f2… de la entrega rem141 58067a5a…, TRUN-278e8977…) a través
del lector aceptado de T3 (9e257060…, sin modificar, modo produccion) y su prueba de pertenencia por fila.
  puerta(...)             — antes de leer fuentes o escribir: candidata = manifiesto real sin alcance ni decisión (vista CANDIDATA, nunca
                            productiva); ensayo = manifiesto -ENSAYO + alcance FIXTURE ligado a ESTE paquete, sin decisión (vista ENSAYO);
                            produccion = manifiesto real + alcance v3 CAPTURA_T8_TESTIGO_ALTO verificado por C0 (verificar_documento), igual
                            campo a campo al documento que este módulo deriva (manifiesto, índice, código, instalación, límites, plan, autoridad)
                            + decisión humana nativa (decision_humana de C0). Alcances históricos (λ, captura, testigo) se rechazan.
  cargar(...)             — base = vista de captura aceptada (A139, 66891b45…, por su inventario sellado 79484151…); incorporación c54a618b…,
                            aceptación 3c3905a3… y dictamen 72bf8d72… por sus bytes; lector/adaptador/testigo_comun por el inventario de A140
                            (be0c63bc…) y CONGELAMIENTO_TESTIGO_v3 (66a107d6…); el lector se ejecuta por sus bytes exactos (leer, produccion),
                            su evidencia por fila debe reproducir c073aef8… y su lectura debe coincidir con la aceptación; finalizador instalado
                            _finalize (a8aded1d…). La AUTORIDAD (constante de este módulo) es la que fija el manifiesto: un manifiesto distinto
                            se rechaza aunque traiga huellas coherentes consigo mismo.
  construir_vista(...)    — 13.656 líneas en el mismo orden: todas las filas salvo las 35 se copian con sus BYTES; en cada una de las 35 solo
                            cambia «captura_c2» (resultado histórico, identidad e insumos intactos): prueba de pertenencia del lector, ambas
                            desigualdades exactas C2_inf + err_inf <= v <= C2_sup - err_sup y su procedencia propia (TRUN del superior, inferior
                            CEI:dc4e1ba9… de la fila 9638, plantilla BRUN-cb33… solo como referencia de equivalencia) y el adaptador a _finalize.
  validar_contenido(...)  — ÚNICA validación del contenido; la usan el materializador ANTES de escribir y el verificador (y las pruebas):
                            universo, orden, claves, duplicados/faltantes/ajenas, bytes preservados fuera del diferencial, exactamente las 35,
                            las 5 pendientes sin cambios, desigualdades recalculadas desde la propia fila, procedencia, recomputación, recuentos
                            derivados de las filas con su identidad (no solo el total) y las 14 corridas.
  verificar(...)          — contexto re-autenticado + sello + procedencia (kind/productivo derivados del modo, corrección rem136) + validar_contenido.
cerrar queda interno: ninguna función acepta filas, callbacks ni hashes del llamador; una fila no cubierta queda pendiente (nunca NA)."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

AQUI = Path(__file__).resolve().parent
NUCLEO_IDENTIDAD = "d0bf5cd6e413ae4dcdd18eafb0bf7269cac22a487b4d46cb6b1737b5e5c971ae"
INDICE = "PAQUETE_T8_TESTIGO.json"
PIEZAS = ("conexion_testigo.py", "materializar_t8_testigo.py", "verificar_t8_testigo.py", "admision_integracion.py", "receta_t8_testigo.sh")
DATOS = ("MANIFIESTO_T8_TESTIGO.json", "MANIFIESTO_T8_TESTIGO-ENSAYO.json")
TAREAS = ("T8-TESTIGO-MATERIALIZAR", "T8-TESTIGO-VERIFICAR")
OPERACION = "CAPTURA_T8_TESTIGO_ALTO"
LIMITES = {"procesos": 1, "tope_s": 600.0, "intentos": 1, "union_s": 10800.0}
KIND_MANIFIESTO = "manifiesto-t8-testigo-alto-v1"
KIND_ALCANCE = "autorizacion-alcance-paso4-v3"
DESPLIEGUE = "f293a0a62d2cb6bf3517e72a0bfc589ee703685d4434c2cdae4b4cd1b5085d6c"
ACTA_P3 = "8e59ea4870c987ecca4ea1e5a8cb3f95581fcc1a64b3e7aa61c035a9b8e0dcfc"
HISTORICOS = {"d3076d0d501e76f716eb1ef7afe4d2a88b1023acab05fd9418cdd509e670d379": "alcance λ rem137 (consumido)",
              "01b9633aa382b49dce7af78a8af8ec939c88aaffb0175ab91b8edec94991e4bd": "alcance de captura rem139 (consumido)",
              "210015d7b949ba0eff708c082c25536bcabe80ca70a8c5351df701611978895a": "alcance del testigo alto rem141 (consumido)"}
FIXTURE = "FIXTURE — documento de prueba rem142, NO productivo: "
ETIQUETA = ("ALCANCE v3 CAPTURA_T8_TESTIGO_ALTO — autoriza SOLO materializar y verificar la vista de captura T8 que incorpora la fuente "
            "aceptada del testigo alto e8b1f7fd… (RESULTADO 981ff0f2…, entrega rem141 58067a5a…, TRUN-278e8977…) en EXACTAMENTE 35 filas "
            "pendientes, por pertenencia certificada con el inferior aceptado CEI:dc4e1ba9…; las 5 filas no cubiertas siguen pendientes y las "
            "13.616 restantes se copian sin cambios; ningún modelo, techo, malla, quiebre, Q, C5, barrido, reproducción, exportación ni "
            "publicación; aprobación solo por decisión humana nativa sobre su sha256")
H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
HF = lambda p: H(Path(p).read_bytes())  # noqa: E731
PRODUCTO, RESUMEN, SELLO = "VISTA_T8_CAPTURA.jsonl", "VISTA_RESUMEN.json", "VISTA.sha256"
KIND_PRODUCTO = {"produccion": "vista-t8-captura-testigo-PRODUCCION", "candidata": "vista-t8-captura-testigo-CANDIDATA",
                 "ensayo": "vista-t8-captura-testigo-ENSAYO"}
COMPARTIDOS = ("modo", "manifiesto_sha256", "indice_sha256", "alcance_sha256", "decision")
DERIVADOS_DEL_MODO = ("kind", "productivo")
POR_OPERACION = ("tarea", "entradas")
DUPLICADOS_DEL_RESUMEN = ("modo", "manifiesto_sha256")
TIPO_CAPTURA = "captura_pendiente_sin_soporte_C2"
TIPO_PRUEBA = "pertenencia_testigo_alto"
SEMANTICA = "encierro_interior_certificado"
REGLA = ("C2_inf + err_inf <= v <= C2_sup - err_sup  =>  computed (inferior aceptado CEI:dc4e1ba9… de la fila 9638; superior: fuente nueva "
         "TRUN-278e8977… del testigo alto e8b1f7fd…)")
CLAVE_TECHO, GRUPO = "e8b1f7fdb9c7017605e0a4162fc6688e7b6ed01d2308ff72106ed6cf6834a97b", "EQ-TECHO-T8-1"
W = r"@@W_WIN@@"
FILAS_ACTUALIZABLES = [6884, 6902, 6926, 7172, 7196, 7244, 7322, 7598, 7682, 7772, 7916, 7958, 7964, 8288, 8378, 8462, 8552, 8606, 8636, 8654,
                       8786, 8876, 8930, 9014, 9020, 9188, 9224, 9260, 9350, 9398, 9458, 9542, 9560, 9680, 9686]
FILAS_PENDIENTES = [7028, 7208, 8144, 8186, 9578]
ESPERADO = {"filas": 13656, "no_captura": 11545, "definitivo_almacenado": 9434, "lambda_finalizadas": 2111, "captura_filas": 2111,
            "captura_computed": 963, "captura_outside_support": 1143, "captura_pendiente": 5, "definitivas_candidatas": 13651, "pendientes": 5,
            "captura_por_tipo": {"exclusion_cota_33_10": 264, "exclusion_cota_U": 879, "pertenencia_misma_corrida": 365,
                                 "pertenencia_testigo_alto": 35, "pertenencia_transferida": 563},
            "captura_pendientes_por_causa": {"SIN_PRUEBA_POR_FILA": 5}, "captura_cambios": 963,
            "actualizadas_por_testigo": FILAS_ACTUALIZABLES, "pendientes_filas": FILAS_PENDIENTES}
AUTORIDAD = {
    "base_vista": {"area": "paso4_emision_captura_correcciones_testigo_desde_rem139",
                   "inventario": {"ruta": "tmp/paso4_emision_captura_correcciones_testigo_desde_rem139/audit/entrega.json",
                                  "sha256": "794841511784da49ab9d357db7de4bdbf4ff967ab02570c475d0d182af2ce5fd"},
                   "rel": "captura_vista_CAPTURA_T8/VISTA_T8_CAPTURA.jsonl",
                   "sha256": "66891b45282cae1c08c0a86131d194631e1d9a39351e26cfc137255e6b489992",
                   "estado_formal": {"definitivas": 13616, "pendientes": 40}},
    "incorporacion": {"ruta": "tmp/paso4_incorporacion_testigo_desde_rem142/incorporacion/INCORPORACION_TESTIGO.json",
                      "sha256": "c54a618bff30dccb257ea6de18c580a360f4360b9bfb00c2b0a9bdb96fd7eca2",
                      "origen_revisor": W + r"\review_20261104_rem142_INCORPORACION_TESTIGO.json"},
    "aceptacion": {"ruta": W + r"\review_20261104_rem142_testigo_alto_aceptado.json",
                   "sha256": "3c3905a37672162165dbc9062e2c8186b6bb5f76c5d862f2f5e0794e2d027e0b"},
    "dictamen": {"ruta": W + r"\review_20261104_rem142_dictamen.txt", "sha256": "72bf8d72b7fa1233394b652c5ad3dbf81270bfd95cfee7b6177667636f7ce263"},
    "lector": {"area": "paso4_estado_testigo_lector_desde_rem140",
               "inventario": {"ruta": "tmp/paso4_estado_testigo_lector_desde_rem140/audit/entrega.json",
                              "sha256": "be0c63bce4ad32d4fabbfa04eea419b5536fa553cfdf41df3a0cbc14a956ddf1"},
               "dir": "testigo_alto_v3",
               "piezas": {"lector_fuente_testigo.py": "9e25706026743e1b92221029f0e30faaf3c64df703f8c07451848b9696ad7d7a",
                          "adaptador_fila_testigo.py": "7cbebc7691c68d7d902d4c0944f30f8b3b4a1844c409a9f089f88fd7da60b0e2",
                          "testigo_comun.py": "3f8ec27b92c9e04c6d1b5e688f38fe3663440c1e3aa54a9fd9392e6617f28b52"},
               "congelamiento": {"rel": "testigo_alto_v3/CONGELAMIENTO_TESTIGO_v3.json",
                                 "sha256": "66a107d6df08788856306561df58f9350d04a9b1d559074286d8608cbe51622a"},
               "certificacion_fila_sha256": "4741b4ea3b72fc2f754cc2d8c79dd9dd718f8e37205bf3e4ee5c0c539be60f4b",
               "modo": "produccion"},
    "evidencia_filas_sha256": "c073aef80437e54907ba2cf194b2b2211dfc7cdd0ff5fe110c57dcd1f4005590",
    "testigo_superior": {"clave": CLAVE_TECHO, "grupo": GRUPO, "run_origen": "TRUN-278e8977db98756eaf6313e8",
                         "resultado_sha256": "981ff0f2121bde1841e3bccfc76f53a3f21d2e60ba95b14ef3b08f0bd812b457",
                         "fuente_inventario_sha256": "58067a5a95cb8683ba57372957cd87b239e7839fec65ed7728a6f0d72df9f606",
                         "fuente_base": "tmp/paso4_testigo_alto_desde_rem141",
                         "alcance_origen_sha256": "210015d7b949ba0eff708c082c25536bcabe80ca70a8c5351df701611978895a",
                         "decision_origen_uuid": "57f5d10b-896f-44f2-b8df-013abaae1d30",
                         "extremo_exacto": "231254813940860032385023/302231454903657293676544"},
    "testigo_inferior": {"ceiling_id": "CEI:dc4e1ba95f168fdd846cb39a44b404f204efbb47", "prueba_aceptada_fila": 9638,
                         "run_origen": "BRUN-cb33e6b24039acc84fb1a065",
                         "pruebas_fila_sha256": "690dfef933447410fd9653201ec92631cb7af52a6364db4b70606833e8be5efa",
                         "extremo_exacto": "83037518495931418279937/151115727451828646838272"},
    "plantilla_equivalencia": "BRUN-cb33e6b24039acc84fb1a065",
    "finalizador": {"ruta": "paso4/instalacion/herramientas/b/unidades.py",
                    "sha256": "a8aded1db50f80feffd62bcb655e62e5f93487364a3c4e625f47dcdbd1f17c86",
                    "sys_path": ["paso4/instalacion/src", "paso4/instalacion"]},
    "nucleo": {"identidad": NUCLEO_IDENTIDAD, "ruta": "tmp/paso4_raices_impacto_desde_rem116/candidato_c0/instalacion"},
    "control": {"admision_cierre": {"origen": "tmp/paso4_emision_lambda_conexion_captura_desde_rem137/c2_conexion/candidato_v3/admision_integracion.py",
                                    "sha256": "7304ac8be5e2d2c33fd16ccf79611285aba2baf4ebd089ba73f33679363603c9"},
                "p3ctl": "codigo/p3ctl.py", "sha256": "546271b057a9635ab39ca3f94e0fd79da46cc7091a4bff873ab8c54e6d875841"},
    "filas_actualizables": FILAS_ACTUALIZABLES,
    "filas_pendientes": FILAS_PENDIENTES,
    "corridas": ["BRUN-050091213b198d7cd7ba9ea2", "BRUN-1368187e9a43de0d95926dca", "BRUN-47e3d9f48d2b65e9ddeed02f", "BRUN-4ef8507fcdefbddc55dbc3b7",
                 "BRUN-5b35ba3f51bc08bd48b384bd", "BRUN-612818cb081c6797d4923b4d", "BRUN-63a9e9ea157b2faaf317ae61", "BRUN-7bdfe0a1bee57298e31e1b34",
                 "BRUN-991c466a1938ddbf2192eefb", "BRUN-9c6c66e7af8b139a613b1c3f", "BRUN-a81e3f45f7111e18b1f39370", "BRUN-c5af32a993773f5258ce570f",
                 "BRUN-cb33e6b24039acc84fb1a065", "BRUN-f5f58960bbf9017776d3d7fc"],
    "esperado": ESPERADO,
    "operacion": OPERACION, "tareas": list(TAREAS), "limites": LIMITES,
    "plan_sha256": "6cec0a6d662104dab6a490cea647cd24ae995819a416eaf3cfd4fd9f3c060e42"}
CAMPOS_MANIFIESTO = frozenset(AUTORIDAD) | {"kind", "destinos", "nota", "produccion_habilitada"}


class Rechazo(Exception):
    pass


def need(c, codigo):
    if not c:
        raise Rechazo(codigo)


def canon(o) -> bytes:
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")


def autenticar_paquete():
    """Índice del paquete: sus cinco piezas y sus dos manifiestos, con las huellas de sus bytes actuales."""
    p = AQUI / INDICE
    if not p.is_file():
        return None, None, ["INDICE_DEL_PAQUETE_AUSENTE"]
    raw = p.read_bytes()
    idx = json.loads(raw)
    if set(idx.get("piezas", {})) != set(PIEZAS) or set(idx.get("datos", {})) != set(DATOS) or idx.get("productivo") is not False:
        return H(raw), idx, ["INDICE_FUERA_DE_ESQUEMA"]
    mal = [n for n in PIEZAS + DATOS if not (AQUI / n).is_file()
           or HF(AQUI / n) != (idx["piezas"] if n in PIEZAS else idx["datos"])[n]["sha256"]]
    return H(raw), idx, (["CODIGO_DEL_PAQUETE_NO_AUTENTICO:%s" % mal] if mal else [])


def es_ensayo(me):
    return str(me.get("kind", "")).endswith("-ENSAYO")


def autoridad_del_manifiesto(me_raw, me, idx):
    """El manifiesto debe ser uno de los dos indexados y llevar EXACTAMENTE la autoridad de este módulo (no basta con huellas coherentes)."""
    if not isinstance(me, dict) or set(me) != CAMPOS_MANIFIESTO:
        return ["MANIFIESTO_FUERA_DE_ESQUEMA"]
    nombre = DATOS[1] if es_ensayo(me) else DATOS[0]
    if idx is None or idx["datos"][nombre]["sha256"] != H(me_raw):
        return ["MANIFIESTO_NO_INDEXADO"]
    if me["kind"] != (KIND_MANIFIESTO + ("-ENSAYO" if es_ensayo(me) else "")) or me["produccion_habilitada"] is not False:
        return ["MANIFIESTO_FUERA_DE_ESQUEMA"]
    return ["MANIFIESTO_DISTINTO_DE_LA_AUTORIDAD:%s" % k for k, v in AUTORIDAD.items() if canon(me[k]) != canon(v)]


def entradas_alcance(me_raw, idx_sha):
    return {"manifiesto_t8_testigo": H(me_raw), "paquete_t8_testigo": idx_sha, "codigo_t8_testigo": {n: HF(AQUI / n) for n in PIEZAS},
            "datos_paquete": {n: HF(AQUI / n) for n in DATOS}, "base_vista": AUTORIDAD["base_vista"], "incorporacion": AUTORIDAD["incorporacion"],
            "aceptacion": AUTORIDAD["aceptacion"], "dictamen": AUTORIDAD["dictamen"], "lector": AUTORIDAD["lector"],
            "evidencia_filas_sha256": AUTORIDAD["evidencia_filas_sha256"], "testigo_superior": AUTORIDAD["testigo_superior"],
            "testigo_inferior": AUTORIDAD["testigo_inferior"], "plantilla_equivalencia": AUTORIDAD["plantilla_equivalencia"],
            "finalizador": AUTORIDAD["finalizador"], "nucleo": AUTORIDAD["nucleo"], "control": AUTORIDAD["control"],
            "filas_actualizables": FILAS_ACTUALIZABLES, "filas_pendientes": FILAS_PENDIENTES, "corridas": AUTORIDAD["corridas"],
            "esperado_no_aceptado": ESPERADO}


def documento_alcance(me_raw, me, idx_sha, fixture):
    """Documento del alcance SIN emitida_utc: el que debe emitir el emisor y el que exige la puerta, campo a campo."""
    sm = H(me_raw)
    return {"kind": KIND_ALCANCE, "etiqueta": (FIXTURE + ETIQUETA) if fixture else ETIQUETA, "plan_sha256": me["plan_sha256"],
            "operaciones": [OPERACION], "tareas": list(TAREAS),
            "asignaciones": {t: H(json.dumps({"tarea": t, "manifiesto": sm, "limites": LIMITES}, sort_keys=True).encode()) for t in TAREAS},
            "despliegue_sha256": DESPLIEGUE, "entradas": entradas_alcance(me_raw, idx_sha), "limites": dict(LIMITES), "repetir": [],
            "excepciones": [], "instalacion_identidad": NUCLEO_IDENTIDAD, "congelamiento_p3_sha256": ACTA_P3, "continua_alcance": None,
            "lote_manifiesto_sha256": sm, "b_official_run_authorized": False, "freeze_run_authorized": False, "official_export_authorized": False}


def _alcance_ligado(AA, ab, al, me_raw, me, idx_sha, tarea, fixture):
    try:
        AA.verificar_documento(al)
    except AA.Rechazo as ex:
        return "ALCANCE_NO_VERIFICABLE:%s" % ex.codigo
    if H(ab) in HISTORICOS:
        return "ALCANCE_HISTORICO_CONSUMIDO"
    ent = al.get("entradas") or {}
    esp = documento_alcance(me_raw, me, idx_sha, fixture)
    for cond, causa in ((al.get("operaciones") == [OPERACION], "ALCANCE_DE_OTRA_OPERACION"),
                        (tarea in (al.get("tareas") or []), "TAREA_FUERA_DEL_ALCANCE"),
                        (al.get("lote_manifiesto_sha256") == ent.get("manifiesto_t8_testigo") == H(me_raw), "ALCANCE_DE_OTRO_MANIFIESTO"),
                        (ent.get("paquete_t8_testigo") == idx_sha and ent.get("codigo_t8_testigo") == esp["entradas"]["codigo_t8_testigo"],
                         "ALCANCE_DE_OTRO_CODIGO"),
                        (al.get("instalacion_identidad") == NUCLEO_IDENTIDAD, "ALCANCE_DE_OTRA_INSTALACION"),
                        (al.get("limites") == LIMITES, "ALCANCE_CON_OTROS_LIMITES"),
                        (al.get("plan_sha256") == me["plan_sha256"], "ALCANCE_DE_OTRO_PLAN")):
        if not cond:
            return causa
    otros = [k for k in sorted(set(esp) | set(al)) if k != "emitida_utc" and canon(al.get(k)) != canon(esp.get(k))]
    return "ALCANCE_DISTINTO_DEL_PAQUETE:%s" % ",".join(otros) if otros else None


def _puerta_invocacion(R, me_raw, me, modo, alcance, decision, tarea):
    R = Path(R)
    C0 = R / AUTORIDAD["nucleo"]["ruta"]
    sys.path.insert(0, str(C0 / "herramientas/b"))
    import aprobacion_alcance as AA
    if AA.identidad_instalacion(C0) != NUCLEO_IDENTIDAD or (me.get("nucleo") or {}).get("identidad") != NUCLEO_IDENTIDAD:
        return False, {"motivo": "NUCLEO_DE_OTRA_IDENTIDAD"}
    idx_sha, idx, mal = autenticar_paquete()
    if mal:
        return False, {"motivo": mal[0]}
    if tarea not in TAREAS:
        return False, {"motivo": "TAREA_DESCONOCIDA"}
    if modo not in ("produccion", "candidata", "ensayo"):
        return False, {"motivo": "MODO_NO_ADMITIDO"}
    fa = autoridad_del_manifiesto(me_raw, me, idx)
    if fa:
        return False, {"motivo": fa[0]}
    if modo == "ensayo":
        if not es_ensayo(me):
            return False, {"motivo": "ENSAYO_CON_MANIFIESTO_REAL"}
        if decision:
            return False, {"motivo": "DECISION_EN_ENSAYO"}
        if not alcance or not Path(alcance).is_file():
            return False, {"motivo": "ENSAYO_SIN_ALCANCE_FIXTURE"}
        ab = Path(alcance).read_bytes()
        al = json.loads(ab)
        if not str(al.get("etiqueta", "")).startswith(FIXTURE):
            return False, {"motivo": "ENSAYO_REQUIERE_ALCANCE_FIXTURE"}
        causa = _alcance_ligado(AA, ab, al, me_raw, me, idx_sha, tarea, True)
        if causa:
            return False, {"motivo": causa}
        return True, {"modo": modo, "indice_sha256": idx_sha, "alcance_sha256": H(ab)}
    if es_ensayo(me):
        return False, {"motivo": "MANIFIESTO_DE_ENSAYO_EN_%s" % modo.upper()}
    if modo == "candidata":
        if alcance or decision:
            return False, {"motivo": "CANDIDATA_NO_ADMITE_ALCANCE"}
        return True, {"modo": modo, "indice_sha256": idx_sha}
    if not alcance or not decision:
        return False, {"motivo": "PRODUCCION_SIN_ALCANCE_NI_DECISION"}
    ap = Path(alcance)
    if not ap.is_file():
        return False, {"motivo": "ALCANCE_NO_MATERIALIZADO"}
    ab = ap.read_bytes()
    al = json.loads(ab)
    if "FIXTURE" in str(al.get("etiqueta", "")).upper():
        return False, {"motivo": "ALCANCE_FIXTURE_EN_PRODUCCION"}
    causa = _alcance_ligado(AA, ab, al, me_raw, me, idx_sha, tarea, False)
    if causa:
        return False, {"motivo": causa}
    try:
        dec = AA.decision_humana(str(decision), H(ab), al["emitida_utc"])
    except AA.Rechazo as ex:
        return False, {"motivo": "DECISION_NO_VALIDA:%s" % ex.codigo}
    except (OSError, ValueError, KeyError, TypeError) as ex:
        return False, {"motivo": "DECISION_NO_VALIDA:ILEGIBLE_%s" % type(ex).__name__}
    return True, {"modo": modo, "indice_sha256": idx_sha, "alcance_sha256": H(ab), "decision": dec}


def puerta(R, me_raw, me, modo, alcance, decision, tarea):
    """Puerta de cada invocación; si admite, devuelve el CONTEXTO AUTENTICADO (COMPARTIDOS + POR_OPERACION) de esa invocación."""
    try:
        ok, p = _puerta_invocacion(R, me_raw, me, modo, alcance, decision, tarea)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as ex:
        return False, {"motivo": "PUERTA_ILEGIBLE:%s" % type(ex).__name__}
    if not ok:
        return ok, p
    return True, {"modo": modo, "manifiesto_sha256": H(me_raw), "indice_sha256": p["indice_sha256"], "alcance_sha256": p.get("alcance_sha256"),
                  "decision": p.get("decision"), "tarea": tarea,
                  "entradas": {"alcance": str(alcance) if alcance else None, "decision": str(decision) if decision else None}}


def contexto_autentico(R, me_raw, me, contexto):
    if not isinstance(contexto, dict) or not isinstance(contexto.get("entradas"), dict) or contexto.get("tarea") not in TAREAS:
        return ["CONTEXTO_AUSENTE_O_MAL_FORMADO"]
    ent = contexto["entradas"]
    ok, p = puerta(R, me_raw, me, contexto.get("modo"), ent.get("alcance"), ent.get("decision"), contexto["tarea"])
    if not ok:
        return ["CONTEXTO_NO_AUTENTICO:%s" % p.get("motivo")]
    return [] if canon(p) == canon(contexto) else ["CONTEXTO_NO_AUTENTICO:DISTINTO_DE_SU_PUERTA"]


def cotejar_procedencia(res, contexto):
    pu = res.get("puerta")
    if not isinstance(pu, dict):
        return ["PROCEDENCIA_AUSENTE:puerta"]
    fallos = ["PROCEDENCIA_AUSENTE:puerta.%s" % k for k in COMPARTIDOS + ("tarea",) if k not in pu]
    fallos += ["PROCEDENCIA_AUSENTE:%s" % k for k in DUPLICADOS_DEL_RESUMEN + DERIVADOS_DEL_MODO if k not in res]
    if fallos:
        return fallos
    fallos += ["PROCEDENCIA_CONTRADICTORIA:%s" % k for k in DUPLICADOS_DEL_RESUMEN if canon(res[k]) != canon(pu[k])]
    if pu["tarea"] != "T8-TESTIGO-MATERIALIZAR":
        fallos.append("PROCEDENCIA_DE_OTRA_OPERACION:%s" % pu["tarea"])
    fallos += ["PROCEDENCIA_DISTINTA_DEL_CONTEXTO:%s" % k for k in COMPARTIDOS if canon(pu[k]) != canon(contexto[k])]
    if res["kind"] != KIND_PRODUCTO[contexto["modo"]]:
        fallos.append("PROCEDENCIA_KIND_NO_CORRESPONDE_AL_MODO:%s" % res["kind"])
    if res["productivo"] is not (contexto["modo"] == "produccion"):
        fallos.append("PROCEDENCIA_PRODUCTIVO_NO_CORRESPONDE_AL_MODO")
    fuentes = fuentes_del_resumen()
    fallos += ["PROCEDENCIA_DE_FUENTES_DISTINTA:%s" % k for k, v in fuentes.items() if canon(res.get("fuentes", {}).get(k)) != canon(v)]
    return fallos


def fuentes_del_resumen():
    return {"base_vista_sha256": AUTORIDAD["base_vista"]["sha256"], "incorporacion_sha256": AUTORIDAD["incorporacion"]["sha256"],
            "aceptacion_sha256": AUTORIDAD["aceptacion"]["sha256"], "dictamen_sha256": AUTORIDAD["dictamen"]["sha256"],
            "evidencia_filas_sha256": AUTORIDAD["evidencia_filas_sha256"], "lector": AUTORIDAD["lector"]["piezas"],
            "testigo_superior_run_origen": AUTORIDAD["testigo_superior"]["run_origen"],
            "resultado_sha256": AUTORIDAD["testigo_superior"]["resultado_sha256"], "finalizador_sha256": AUTORIDAD["finalizador"]["sha256"],
            "estado_formal_base": AUTORIDAD["base_vista"]["estado_formal"]}


def _modulo(nombre, ruta, sha_esperado):
    b = Path(ruta).read_bytes()
    if H(b) != sha_esperado:
        raise Rechazo("PIEZA_NO_AUTENTICA:%s" % nombre)
    sp = importlib.util.spec_from_loader(nombre, loader=None, origin=str(ruta))
    m = importlib.util.module_from_spec(sp)
    m.__file__ = str(ruta)
    sys.modules[nombre] = m
    exec(compile(b, str(ruta), "exec"), m.__dict__)
    return m


def _inventario(R, inv):
    ib = (Path(R) / inv["ruta"]).read_bytes()
    if H(ib) != inv["sha256"]:
        raise Rechazo("INVENTARIO_NO_AUTENTICO:%s" % inv["ruta"])
    return json.loads(ib)["files"]


def _bytes_inventariados(R, x):
    """Bytes de una fuente sellada: inventario fijado → archivo listado → sha256 fijado (los mismos bytes se usan)."""
    files = _inventario(R, x["inventario"])
    b = (Path(R) / "tmp" / x["area"] / x["rel"]).read_bytes()
    if H(b) != x["sha256"] or files.get(x["rel"], {}).get("sha256") != x["sha256"]:
        raise Rechazo("FUENTE_NO_AUTENTICA:%s" % x["rel"])
    return b


def _bytes_fijados(ruta, sha, codigo):
    b = Path(ruta).read_bytes()
    if H(b) != sha:
        raise Rechazo(codigo)
    return b


def lineas(raw):
    partes = raw.split(b"\n")
    if partes[-1] != b"":
        raise Rechazo("VISTA_SIN_FIN_DE_LINEA")
    return partes[:-1]


def _cotejar_lectura(lect):
    lec, TS = AUTORIDAD["lector"], AUTORIDAD["testigo_superior"]
    en = lect.get("ejecucion_nueva") or {}
    for cond, causa in ((lect.get("modo") == "produccion" and lect.get("sintetico") is False and lect.get("promueve") is False, "LECTURA_NO_PRODUCTIVA"),
                        (lect.get("incorporacion_sha256") == AUTORIDAD["incorporacion"]["sha256"], "LECTURA_DE_OTRA_INCORPORACION"),
                        (lect.get("lector_sha256") == lec["piezas"]["lector_fuente_testigo.py"]
                         and lect.get("adaptador_sha256") == lec["piezas"]["adaptador_fila_testigo.py"]
                         and lect.get("testigo_comun_sha256") == lec["piezas"]["testigo_comun.py"]
                         and lect.get("certificacion_fila_sha256") == lec["certificacion_fila_sha256"], "LECTURA_DE_OTRO_CODIGO"),
                        (lect.get("clave") == CLAVE_TECHO and lect.get("grupo") == GRUPO, "LECTURA_DE_OTRA_CLAVE"),
                        (en.get("run_origen") == TS["run_origen"] and en.get("base") == TS["fuente_base"]
                         and en.get("inventario_sha256") == TS["fuente_inventario_sha256"] and en.get("alcance_sha256") == TS["alcance_origen_sha256"]
                         and en.get("decision_uuid") == TS["decision_origen_uuid"] and en.get("sintetico") is False, "LECTURA_DE_OTRA_EJECUCION"),
                        ((lect.get("techo") or {}).get("resultado_sha256") == TS["resultado_sha256"]
                         and (lect.get("techo") or {}).get("run_origen") == TS["run_origen"], "LECTURA_DE_OTRO_RESULTADO"),
                        ((lect.get("plantilla") or {}).get("run") == AUTORIDAD["plantilla_equivalencia"] != TS["run_origen"], "PLANTILLA_PRESENTADA_COMO_PRODUCTORA"),
                        ((lect.get("testigo_inferior") or {}).get("ceiling_id") == AUTORIDAD["testigo_inferior"]["ceiling_id"]
                         and (lect.get("testigo_inferior") or {}).get("prueba_aceptada_fila") == AUTORIDAD["testigo_inferior"]["prueba_aceptada_fila"]
                         and (lect.get("testigo_inferior") or {}).get("extremo_superior") == AUTORIDAD["testigo_inferior"]["extremo_exacto"],
                         "LECTURA_CON_OTRO_INFERIOR"),
                        (lect.get("cubiertas") == FILAS_ACTUALIZABLES and sorted(int(k) for k in (lect.get("no_cubiertas") or {})) == FILAS_PENDIENTES
                         and lect.get("filas") == 40, "LECTURA_CON_OTRA_COBERTURA")):
        need(cond, causa)


def _cotejar_aceptacion(acc, dic_raw):
    TS, TI = AUTORIDAD["testigo_superior"], AUTORIDAD["testigo_inferior"]
    ce = acc.get("coverage_exact") or {}
    filas = {x.get("row"): x for x in ce.get("covered_rows_pending_emission") or []}
    for cond, causa in ((acc.get("kind") == "accepted-high-witness-source-rem142-not-T8-finalization", "ACEPTACION_FUERA_DE_ESQUEMA"),
                        (acc.get("review_sha256") == H(dic_raw) == AUTORIDAD["dictamen"]["sha256"], "ACEPTACION_DE_OTRO_DICTAMEN"),
                        (acc.get("inventory_sha256") == TS["fuente_inventario_sha256"] and acc.get("result_sha256") == TS["resultado_sha256"]
                         and acc.get("scope_sha256") == TS["alcance_origen_sha256"] and acc.get("new_run_origin") == TS["run_origen"]
                         and acc.get("key") == CLAVE_TECHO and acc.get("group") == GRUPO, "ACEPTACION_DE_OTRA_FUENTE"),
                        (acc.get("reader_evidence_sha256") == AUTORIDAD["evidencia_filas_sha256"]
                         and acc.get("review_incorporation_document_sha256") == AUTORIDAD["incorporacion"]["sha256"], "ACEPTACION_DE_OTRA_LECTURA"),
                        ((acc.get("lower_accepted_witness") or {}).get("ceiling_id") == TI["ceiling_id"]
                         and (acc.get("lower_accepted_witness") or {}).get("run_origen") == TI["run_origen"], "ACEPTACION_CON_OTRO_INFERIOR"),
                        (ce.get("lower_endpoint") == TI["extremo_exacto"] and ce.get("upper_endpoint") == TS["extremo_exacto"], "ACEPTACION_CON_OTROS_EXTREMOS"),
                        (sorted(filas) == FILAS_ACTUALIZABLES and len(filas) == 35
                         and all(x.get("lower_ok") is True and x.get("upper_ok") is True and x.get("covered") is True for x in filas.values())
                         and sorted(int(x["row"]) if isinstance(x, dict) else int(x) for x in ce.get("five_pending_rows_not_excluded") or []) == FILAS_PENDIENTES,
                         "ACEPTACION_CON_OTRA_COBERTURA"),
                        (acc.get("T8_definitive") == 13616 and acc.get("T8_formal_pending") == 40 and acc.get("T8_new_finalized") == 0,
                         "ACEPTACION_CON_OTRO_ESTADO_FORMAL")):
        need(cond, causa)
    return filas


def _paper2b():
    return {k: getattr(m, "__file__", None) for k, m in list(sys.modules.items()) if k == "paper2b" or k.startswith("paper2b.")}


def _aislar_paper2b():
    """(corrección tras REM142-H1) el lector valida con el núcleo histórico fijado y el finalizador usa el de la instalación: cada uno se
    carga en un espacio de módulos paper2b LIMPIO, para que ninguno herede los módulos del otro (sys.modules es del proceso)."""
    for k in _paper2b():
        del sys.modules[k]


def cargar(R, me):
    """Fuentes SOLO por la AUTORIDAD de este módulo (igual a la del manifiesto); los mismos bytes autenticados se usan."""
    R = Path(R)
    need(isinstance(me, dict) and all(canon(me.get(k)) == canon(v) for k, v in AUTORIDAD.items()), "MANIFIESTO_DISTINTO_DE_LA_AUTORIDAD")
    fin = AUTORIDAD["finalizador"]
    rutas_fin = [str(R / p) for p in fin["sys_path"]]
    base_raw = _bytes_inventariados(R, AUTORIDAD["base_vista"])
    inc_p = R / AUTORIDAD["incorporacion"]["ruta"]
    inc_raw = _bytes_fijados(inc_p, AUTORIDAD["incorporacion"]["sha256"], "INCORPORACION_NO_AUTENTICA")
    acc_raw = _bytes_fijados(AUTORIDAD["aceptacion"]["ruta"], AUTORIDAD["aceptacion"]["sha256"], "ACEPTACION_NO_AUTENTICA")
    dic_raw = _bytes_fijados(AUTORIDAD["dictamen"]["ruta"], AUTORIDAD["dictamen"]["sha256"], "DICTAMEN_NO_AUTENTICO")
    filas_acc = _cotejar_aceptacion(json.loads(acc_raw), dic_raw)
    lec = AUTORIDAD["lector"]
    files = _inventario(R, lec["inventario"])
    T3 = R / "tmp" / lec["area"] / lec["dir"]
    for n, s in lec["piezas"].items():
        need(files.get(lec["dir"] + "/" + n, {}).get("sha256") == s == HF(T3 / n), "LECTOR_NO_AUTENTICO:%s" % n)
    cg = lec["congelamiento"]
    cong_raw = (R / "tmp" / lec["area"] / cg["rel"]).read_bytes()
    need(files.get(cg["rel"], {}).get("sha256") == cg["sha256"] == H(cong_raw), "CONGELAMIENTO_DEL_LECTOR_NO_AUTENTICO")
    cong = json.loads(cong_raw)
    need(cong.get("conforme") is True and cong.get("productivo") is False
         and all(cong["indice"].get(n, {}).get("sha256") == s for n, s in lec["piezas"].items()), "LECTOR_FUERA_DEL_CONGELAMIENTO")
    LT = _modulo("lector_fuente_testigo_t8_testigo", T3 / "lector_fuente_testigo.py", lec["piezas"]["lector_fuente_testigo.py"])
    need(Path(LT.AD.__file__).resolve() == (T3 / "adaptador_fila_testigo.py").resolve() and HF(LT.AD.__file__) == lec["piezas"]["adaptador_fila_testigo.py"]
         and Path(LT.TC.__file__).resolve() == (T3 / "testigo_comun.py").resolve() and LT.TC.PROPIO == lec["piezas"]["testigo_comun.py"]
         and LT.MI_SHA == lec["piezas"]["lector_fuente_testigo.py"] and LT.AD.CF_SHA256 == lec["certificacion_fila_sha256"], "LECTOR_CARGADO_DISTINTO")
    # 1) lector: espacio paper2b limpio y sin las rutas de la instalación (valida con el núcleo histórico que fija su manifiesto)
    _aislar_paper2b()
    sys.path[:] = [p for p in sys.path if p not in rutas_fin]
    try:
        lect, ev = LT.leer(R, inc_p, AUTORIDAD["incorporacion"]["sha256"], lec["modo"])
    except LT.TC.Rechazo as ex:
        raise Rechazo("LECTURA_RECHAZADA:%s" % ex.codigo) from None
    mod_lector = _paper2b()
    ev_raw = b"".join((json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8") for x in ev)
    need(H(ev_raw) == AUTORIDAD["evidencia_filas_sha256"], "EVIDENCIA_DISTINTA_DE_LA_ACEPTADA")
    _cotejar_lectura(lect)
    # 2) finalizador instalado: espacio paper2b limpio y rutas de la instalación delante; sus módulos deben ser los de la instalación
    _aislar_paper2b()
    for p in reversed(rutas_fin):
        sys.path.insert(0, p)
    UN = _modulo("unidades_finalizador_t8_testigo", R / fin["ruta"], fin["sha256"])
    src_inst = (R / fin["sys_path"][0]).resolve()
    mod_fin = _paper2b()
    need(all(f and src_inst in Path(f).resolve().parents for f in mod_fin.values()), "FINALIZADOR_CON_MODULOS_AJENOS")
    need(not any(f and src_inst in Path(f).resolve().parents for f in mod_lector.values()), "LECTOR_CON_MODULOS_DE_LA_INSTALACION")
    base = lineas(base_raw)
    bfilas = [json.loads(x) for x in base]
    rb = resumen_de(bfilas)
    need(rb["definitivas_candidatas"] == AUTORIDAD["base_vista"]["estado_formal"]["definitivas"]
         and rb["pendientes"] == AUTORIDAD["base_vista"]["estado_formal"]["pendientes"] and rb["filas"] == ESPERADO["filas"], "BASE_CON_OTRO_ESTADO_FORMAL")
    return {"finalizar": UN._finalize, "base_raw": base_raw, "base": base, "bfilas": bfilas, "evidencia": {x["fila"]: x for x in ev},
            "evidencia_raw": ev_raw, "aceptacion": filas_acc, "incorporacion_raw": inc_raw,
            "lectura": {k: lect[k] for k in ("modo", "sintetico", "filas", "por_estado", "cubiertas", "promueve")}
            | {"aislamiento_modulos": {"lector_paper2b": len(mod_lector), "finalizador_paper2b": len(mod_fin)}}}


def desigualdades(p, v):
    """Ambas desigualdades exactas desde la PROPIA prueba de la fila (Fraction) y sus testigos contra la autoridad. -> (ok, fallos, (lo, hi, det))."""
    TI, TS = AUTORIDAD["testigo_inferior"], AUTORIDAD["testigo_superior"]
    wi = p.get("testigo_inferior") if isinstance(p, dict) else None
    ws = p.get("testigo_superior_nuevo") if isinstance(p, dict) else None
    wi, ws = wi if isinstance(wi, dict) else {}, ws if isinstance(ws, dict) else {}
    fallos = []
    if (wi.get("ceiling_id") != TI["ceiling_id"] or wi.get("run_origen") != TI["run_origen"] or wi.get("computation_status") != "complete"
            or wi.get("sup_not_attained") is not False):
        fallos.append("TESTIGO_INFERIOR_AJENO")
    if (ws.get("run_origen") != TS["run_origen"] or ws.get("resultado_sha256") != TS["resultado_sha256"] or ws.get("clave") != TS["clave"]
            or ws.get("fuente_inventario_sha256") != TS["fuente_inventario_sha256"] or ws.get("fuente_base") != TS["fuente_base"]
            or ws.get("incorporacion_sha256") != AUTORIDAD["incorporacion"]["sha256"] or ws.get("grupo") != TS["grupo"]
            or ws.get("sintetico") is not False or ws.get("computation_status") != "complete" or ws.get("sup_not_attained") is not False):
        fallos.append("TESTIGO_SUPERIOR_AJENO")
    if ws.get("plantilla_equivalencia") != AUTORIDAD["plantilla_equivalencia"] or ws.get("run_origen") == AUTORIDAD["plantilla_equivalencia"]:
        fallos.append("PLANTILLA_PRESENTADA_COMO_PRODUCTORA")
    try:
        lo = Fraction(wi["C_2"]) + Fraction(wi["numerical_error"])
        hi = Fraction(ws["C_2"]) - Fraction(ws["numerical_error"])
        fv = Fraction(v)
    except (KeyError, TypeError, ValueError):
        return False, fallos + ["DESIGUALDAD_ILEGIBLE"], None
    if str(lo) != TI["extremo_exacto"]:
        fallos.append("EXTREMO_INFERIOR_DISTINTO_DEL_ACEPTADO")
    if str(hi) != TS["extremo_exacto"]:
        fallos.append("EXTREMO_SUPERIOR_DISTINTO_DEL_ACEPTADO")
    if not lo <= fv:
        fallos.append("DESIGUALDAD_INFERIOR_NO_CUMPLE")
    if not fv <= hi:
        fallos.append("DESIGUALDAD_SUPERIOR_NO_CUMPLE")
    det = {"valor": str(fv), "regla": REGLA,
           "inferior": {"C_2": wi["C_2"], "numerical_error": wi["numerical_error"], "extremo": str(lo), "holgura": str(fv - lo), "cumple": lo <= fv},
           "superior": {"C_2": ws["C_2"], "numerical_error": ws["numerical_error"], "extremo": str(hi), "holgura": str(hi - fv), "cumple": fv <= hi}}
    return not fallos, fallos, (lo, hi, det)


def procedencia_fila(anterior):
    TS, TI, lec = AUTORIDAD["testigo_superior"], AUTORIDAD["testigo_inferior"], AUTORIDAD["lector"]
    return {"base_vista_sha256": AUTORIDAD["base_vista"]["sha256"], "base_vista_inventario_sha256": AUTORIDAD["base_vista"]["inventario"]["sha256"],
            "incorporacion_sha256": AUTORIDAD["incorporacion"]["sha256"], "aceptacion_sha256": AUTORIDAD["aceptacion"]["sha256"],
            "dictamen_sha256": AUTORIDAD["dictamen"]["sha256"], "evidencia_filas_sha256": AUTORIDAD["evidencia_filas_sha256"],
            "lector": {"piezas": lec["piezas"], "congelamiento_sha256": lec["congelamiento"]["sha256"], "inventario_sha256": lec["inventario"]["sha256"]},
            "certificacion_fila_sha256": lec["certificacion_fila_sha256"], "finalizador_sha256": AUTORIDAD["finalizador"]["sha256"],
            "plan_sha256": AUTORIDAD["plan_sha256"],
            "testigo_superior": {k: TS[k] for k in ("run_origen", "resultado_sha256", "fuente_inventario_sha256", "fuente_base", "clave", "grupo",
                                                    "alcance_origen_sha256", "decision_origen_uuid")}
            | {"rol": "productor del techo superior (fuente nueva aceptada; su alcance y su decisión solo se releen para autenticarla)"},
            "testigo_inferior": {k: TI[k] for k in ("ceiling_id", "prueba_aceptada_fila", "run_origen", "pruebas_fila_sha256")}
            | {"rol": "testigo inferior aceptado"},
            "plantilla_equivalencia": {"run": AUTORIDAD["plantilla_equivalencia"],
                                       "rol": "referencia de equivalencia y del dominio de destino; NO es la corrida que calculó el techo superior"},
            "captura_c2_anterior_sha256": H(canon(anterior)), "procedencia_anterior": anterior.get("procedencia")}


def captura_nueva(carga, i, f):
    """captura_c2 de una de las 35 filas desde la base f y la evidencia autenticada; cualquier incoherencia es un rechazo."""
    ev, ac = carga["evidencia"].get(i), carga["aceptacion"].get(i)
    need(ev is not None and ac is not None, "FILA_SIN_EVIDENCIA:%d" % i)
    old = f.get("captura_c2") or {}
    need(f.get("tipo") == TIPO_CAPTURA and f.get("fila_anexo") == i and old.get("estado_candidato") == "pendiente"
         and old.get("causa_pendiente") == "SIN_PRUEBA_POR_FILA" and old.get("prueba_sha256") is None, "FILA_BASE_NO_PENDIENTE:%d" % i)
    p = ev["prueba_candidata"]
    need(f["clave_fila"] == ev["clave_fila"] == ac["row_key"], "CLAVE_DE_FILA_DISTINTA:%d" % i)
    need(f["run_id"] == ev["run_destino"] == ac["destination_run"] == p["run_destino"], "CORRIDA_DESTINO_DISTINTA:%d" % i)
    v = f["historico"]["fin_por_unidad"]["value"]
    need(v == ev["valor_requerido"] == p["valor_requerido"] and Fraction(v) == Fraction(ac["required_exact"]), "VALOR_REQUERIDO_DISTINTO:%d" % i)
    need(ev["estado_candidato"] == "computed_candidato" and ev["promueve"] is False and ev["sintetico"] is False and ev["candidata"] is True
         and p.get("tipo") == "pertenencia_testigo_alto_candidata" and p.get("fila") == i, "EVIDENCIA_NO_CUBRE:%d" % i)
    ok, fl, r = desigualdades(p, v)
    need(ok, "%s:%d" % (fl[0] if fl else "DESIGUALDAD", i))
    lo, hi, det = r
    salida = {}
    carga["finalizar"](salida, f["historico"]["fin_por_unidad"], {}, (lo, hi))
    need(salida.get("result_status") == "computed", "ADAPTADOR_DISCREPA_DEL_FINALIZADOR:%d" % i)
    return {"estado_candidato": "computed", "clasificacion_derivada": "computed", "finalizacion_candidata": True, "causa_pendiente": None,
            "tipo_prueba": TIPO_PRUEBA, "prueba_sha256": ev["prueba_sha256"], "cambio": f["estado_historico"] != "computed",
            "adaptador": {"finalizador_sha256": AUTORIDAD["finalizador"]["sha256"], "c2": [str(lo), str(hi)], "semantica": SEMANTICA,
                          "salida": salida, "regla": REGLA},
            "desigualdades": det, "prueba": p, "procedencia": procedencia_fila(old)}


def construir_vista(carga, me):
    """Líneas de la vista candidata: bytes de la base salvo las 35, donde solo cambia captura_c2."""
    act = set(FILAS_ACTUALIZABLES)
    out = []
    for i, (b, f) in enumerate(zip(carga["base"], carga["bfilas"])):
        if i not in act:
            out.append(b)
            continue
        g = dict(f)
        g["captura_c2"] = captura_nueva(carga, i, f)
        out.append(canon(g))
    return out


def resumen_de(filas):
    cap = [f["captura_c2"] for f in filas if f.get("tipo") == TIPO_CAPTURA]
    pend = [c for c in cap if c["estado_candidato"] == "pendiente"]
    return {"filas": len(filas), "no_captura": len(filas) - len(cap), "definitivo_almacenado": sum(f.get("tipo") == "definitivo_almacenado" for f in filas),
            "lambda_finalizadas": sum(f.get("tipo") == "lambda_candidato_por_demostracion" for f in filas), "captura_filas": len(cap),
            "captura_computed": sum(c["estado_candidato"] == "computed" for c in cap),
            "captura_outside_support": sum(c["estado_candidato"] == "outside_support" for c in cap),
            "captura_pendiente": len(pend), "definitivas_candidatas": len(filas) - len(pend), "pendientes": len(pend),
            "captura_por_tipo": dict(sorted(Counter(c["tipo_prueba"] for c in cap if c["finalizacion_candidata"]).items())),
            "captura_pendientes_por_causa": dict(sorted(Counter(c["causa_pendiente"] for c in cap if c["causa_pendiente"]).items())),
            "captura_cambios": sum(bool(c["cambio"]) for c in cap),
            "actualizadas_por_testigo": sorted(f["fila_anexo"] for f in filas if f.get("tipo") == TIPO_CAPTURA and f["captura_c2"]["tipo_prueba"] == TIPO_PRUEBA),
            "pendientes_filas": sorted(f["fila_anexo"] for f in filas if f.get("tipo") == TIPO_CAPTURA and f["captura_c2"]["estado_candidato"] == "pendiente"),
            "corridas": sorted({f["run_id"] for f in filas}), "plan_sha256": AUTORIDAD["plan_sha256"]}


def _sin_c2(f):
    return {k: v for k, v in f.items() if k != "captura_c2"}


def validar_contenido(carga, ls):
    """ÚNICA validación del contenido de una vista (lista de líneas sin «\\n»): la usan el materializador antes de escribir y el verificador.
    Devuelve (fallos, resumen derivado de las filas o None)."""
    if not isinstance(ls, list) or not all(isinstance(x, bytes) for x in ls):
        return ["VISTA_MAL_FORMADA"], None
    fallos, base, bfilas = [], carga["base"], carga["bfilas"]
    try:
        filas = [json.loads(x) for x in ls]
    except ValueError:
        return ["VISTA_MAL_FORMADA"], None
    if not all(isinstance(f, dict) for f in filas):
        return ["VISTA_MAL_FORMADA"], None
    if len(ls) != len(base):
        fallos.append("UNIVERSO_DISTINTO:%d!=%d" % (len(ls), len(base)))
    claves = [f.get("clave_fila") for f in filas]
    bclaves = [f["clave_fila"] for f in bfilas]
    if len(set(claves)) != len(claves):
        fallos.append("CLAVES_DUPLICADAS:%d" % (len(claves) - len(set(claves))))
    if set(claves) != set(bclaves):
        fallos.append("CLAVES_FALTANTES_O_AJENAS:%d" % len(set(bclaves) ^ set(claves)))
    elif claves != bclaves and len(set(claves)) == len(claves):
        fallos.append("ORDEN_DISTINTO")
    act, pen = set(FILAS_ACTUALIZABLES), set(FILAS_PENDIENTES)
    por_clave = {k: (i, f) for i, (k, f) in enumerate(zip(bclaves, bfilas))}
    cat = {k: [] for k in ("FILA_FUERA_DEL_DIFERENCIAL_REESCRITA", "PENDIENTE_PROMOVIDA_O_ALTERADA", "IDENTIDAD_O_INSUMOS_REESCRITOS",
                           "FILA_DISTINTA_DEL_RECALCULO", "PROCEDENCIA_DE_FILA_DISTINTA", "FILA_NO_CANONICA", "DESIGUALDAD_O_TESTIGO")}
    for j, (x, f) in enumerate(zip(ls, filas)):
        k = f.get("clave_fila")
        if k not in por_clave:
            continue
        i, g = por_clave[k]
        if i not in act:
            if x != base[i]:
                cat["PENDIENTE_PROMOVIDA_O_ALTERADA" if i in pen else "FILA_FUERA_DEL_DIFERENCIAL_REESCRITA"].append(i)
            continue
        if canon(_sin_c2(f)) != canon(_sin_c2(g)):
            cat["IDENTIDAD_O_INSUMOS_REESCRITOS"].append(i)
        c = f.get("captura_c2") if isinstance(f.get("captura_c2"), dict) else {}
        try:
            v = f["historico"]["fin_por_unidad"]["value"]
        except (KeyError, TypeError):
            v = None
        ok, fl, _ = desigualdades(c.get("prueba") or {}, v)
        if not ok:
            cat["DESIGUALDAD_O_TESTIGO"].append("%d:%s" % (i, "+".join(fl)))
        if canon(c.get("procedencia")) != canon(procedencia_fila(g["captura_c2"])):
            cat["PROCEDENCIA_DE_FILA_DISTINTA"].append(i)
        try:
            esp = captura_nueva(carga, i, g)
        except Rechazo as ex:
            esp = None
            fallos.append("RECALCULO_RECHAZADO:%s" % ex)
        if esp is None or canon(c) != canon(esp):
            cat["FILA_DISTINTA_DEL_RECALCULO"].append(i)
        if x != canon(f):
            cat["FILA_NO_CANONICA"].append(i)
    fallos += ["%s:%d:%s" % (k, len(v), v[:5]) for k, v in cat.items() if v]
    try:
        rs = resumen_de(filas)
    except (KeyError, TypeError, AttributeError):
        return fallos + ["VISTA_SIN_CAMPOS_REQUERIDOS"], None
    fallos += ["RECUENTO_%s:%s!=%s" % (k, rs.get(k), v) for k, v in ESPERADO.items() if canon(rs.get(k)) != canon(v)]
    # identidad de los conjuntos (no solo totales): cada estado de la vista = el de la base salvo exactamente las 35
    rb = {f["fila_anexo"]: f["captura_c2"]["estado_candidato"] for f in bfilas if f.get("tipo") == TIPO_CAPTURA}
    rv = {f.get("fila_anexo"): (f.get("captura_c2") or {}).get("estado_candidato") for f in filas if f.get("tipo") == TIPO_CAPTURA}
    cambiadas = sorted(i for i in set(rb) | set(rv) if rb.get(i) != rv.get(i))
    if cambiadas != FILAS_ACTUALIZABLES:
        fallos.append("IDENTIDAD_DE_LAS_ACTUALIZADAS_DISTINTA:%d" % len(set(cambiadas) ^ act))
    if sorted(i for i, e in rv.items() if e == "pendiente") != FILAS_PENDIENTES:
        fallos.append("IDENTIDAD_DE_LAS_PENDIENTES_DISTINTA")
    if rs["corridas"] != sorted(AUTORIDAD["corridas"]) or len(rs["corridas"]) != 14:
        fallos.append("CORRIDAS_DISTINTAS")
    return fallos, rs


def materializar(R, me_raw, me, out, contexto, carga=None):
    """Etapa 1 (la llama materializar_t8_testigo.py): construye, somete a validar_contenido ANTES de escribir y escribe en un directorio NUEVO
    la vista, su sello y el resumen (puerta = contexto autenticado; kind/productivo derivados del modo). Un fallo no deja nada escrito."""
    modo = contexto["modo"]
    if carga is None:
        carga = cargar(R, me)
    ls = construir_vista(carga, me)
    fallos, rs = validar_contenido(carga, ls)
    if fallos:
        raise Rechazo("VISTA_NO_VALIDA_ANTES_DE_ESCRIBIR:%s" % fallos[:5])
    raw = b"".join(x + b"\n" for x in ls)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    with (out / PRODUCTO).open("xb") as fh:
        fh.write(raw)
    sha = H(raw)
    with (out / SELLO).open("x", encoding="utf-8", newline="\n") as fh:
        fh.write(sha + "\n")
    doc = {"kind": KIND_PRODUCTO[modo], "modo": modo, "productivo": modo == "produccion", "puerta": contexto, "manifiesto_sha256": H(me_raw),
           "producto": PRODUCTO, "producto_sha256": sha, "resumen": rs, "fuentes": fuentes_del_resumen(), "lectura": carga["lectura"],
           "nota": "vista de captura T8 con la fuente nueva del testigo alto: solo 35 filas cambian su captura_c2; no finaliza estados reales "
                   "fuera de una emisión productiva aceptada; el estado formal sigue en 13.616 + 40 hasta entonces"}
    with (out / RESUMEN).open("x", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=1, default=str) + "\n")
    return sha, rs


def verificar(R, me_raw, prod_dir, contexto, carga=None):
    """ÚNICA validación de la vista: contexto, sello, procedencia y validar_contenido sobre los bytes leídos una vez."""
    me = json.loads(me_raw)
    fallos = contexto_autentico(R, me_raw, me, contexto)
    if fallos:
        return False, fallos, None
    prod_dir = Path(prod_dir)
    try:
        raw = (prod_dir / PRODUCTO).read_bytes()
        sello = (prod_dir / SELLO).read_text(encoding="utf-8").split()[0]
        res = json.loads((prod_dir / RESUMEN).read_bytes())
    except (OSError, ValueError, IndexError) as ex:
        return False, ["VISTA_ILEGIBLE:%s" % type(ex).__name__], None
    if not isinstance(res, dict):
        return False, ["RESUMEN_MAL_FORMADO"], None
    if H(raw) != sello or res.get("producto_sha256") != sello:
        fallos.append("VISTA_NO_COINCIDE_CON_SU_SELLO")
    fallos += cotejar_procedencia(res, contexto)
    try:
        ls = lineas(raw)
    except Rechazo as ex:
        return False, fallos + [str(ex)], None
    try:
        if carga is None:
            carga = cargar(R, me)
    except Exception as ex:  # noqa: BLE001 — una fuente no auténtica nunca es conformidad
        return False, fallos + ["RECALCULO_RECHAZADO:%s" % (str(ex) or type(ex).__name__)[:200]], None
    f2, rs = validar_contenido(carga, ls)
    fallos += f2
    if res.get("resumen") != rs:
        fallos.append("RESUMEN_NO_COINCIDE")
    return not fallos, fallos, {"resumen": rs, "producto_sha256": H(raw), "base_vista_sha256": H(carga["base_raw"]),
                                "evidencia_filas_sha256": H(carga["evidencia_raw"]),
                                "procedencia": {"cotejados": list(COMPARTIDOS + DERIVADOS_DEL_MODO + DUPLICADOS_DEL_RESUMEN) + ["fuentes"],
                                                "contexto": {k: contexto[k] for k in COMPARTIDOS}}}
