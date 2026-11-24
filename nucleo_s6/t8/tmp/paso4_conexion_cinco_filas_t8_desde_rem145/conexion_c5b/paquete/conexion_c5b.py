"""rem145 — CONEXIÓN DE LA PRUEBA C5B A LAS CINCO FILAS T8 PENDIENTES (P4-T8-C5B; candidato aislado, NO habilitado; ningún alcance real ni acto).
Derivada de conexion_testigo.py (rem142, a292a929…, índice db64d37e…; no se edita): mismo patrón puerta → contexto autenticado → cargar por
la autoridad fijada → construir → ÚNICA validación común con procedencia. Novedad: una regla adicional de EXCLUSIÓN C5B (aceptación técnica
rem145 a816420c…, certificado fc403d40…, salida M2 05c10ea6…) ligada a las cinco claves aceptadas, con la misma forma que exclusion_cota_U de
certificacion_fila (4741b4ea…, cuyo Contexto aceptado se reutiliza sin cambios) y la cota U_global_hi EXACTA en lugar de U.
  puerta(...)             — igual que rem142 (candidata = manifiesto real sin alcance ni decisión; ensayo = manifiesto -ENSAYO + alcance FIXTURE
                            ligado a ESTE paquete; produccion = manifiesto real + alcance v3 CAPTURA_T8_EXCLUSION_C5B verificado por C0, igual
                            campo a campo al documento que este módulo deriva, + decisión humana nativa). Alcances históricos se rechazan.
  cargar(...)             — base = vista vigente (rem143, ec6e3929…, por su inventario sellado 0dd9b3d8…); ledger rem144 (7ed13ccf…),
                            aceptación (a816420c…), dictamen (b77f436a…) y nota (893abeec…) por sus bytes; certificado, M2 y scripts C3/M2 por el
                            inventario sellado rem144 (f64f14c2…); Contexto de certificacion_fila por el inventario rem137 (59188e65…): corrida
                            destino, plan, banda del contrato, magnitud y premisas U de D7; finalizador instalado _finalize (a8aded1d…).
                            Aceptación, certificado, M2, ledger y vista se cotejan ENTRE SÍ y con la autoridad; un fallo es un rechazo GLOBAL.
  validar_c5b(...)        — la regla adicional: fila de las cinco (clave, corrida, valor, línea), magnitud C2/share, plan, premisas U, banda,
                            referencias y la desigualdad estricta recalculada Fraction(v) > U_global_hi + banda. Igualdad o banda: no excluye.
  construir_vista(...)    — 13.656 líneas en el mismo orden: las 13.651 restantes con sus BYTES; en cada una de las cinco solo cambia «captura_c2»
                            (resultado histórico, identidad e insumos intactos); el encierro exterior (-inf, U_global_hi + banda] se pasa a
                            _finalize SOLO después de demostrar la exclusión, y su salida debe ser outside_support (nunca pertenencia).
  validar_contenido(...)  — ÚNICA validación del contenido; la usan el materializador ANTES de escribir y el verificador (y las pruebas).
  verificar(...)          — contexto re-autenticado + sello + procedencia (kind/productivo derivados del modo) + validar_contenido.
cerrar queda interno: ninguna función acepta filas, callbacks ni hashes del llamador; una fila no demostrada no se promueve (nunca NA)."""
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
INDICE = "PAQUETE_T8_C5B.json"
PIEZAS = ("conexion_c5b.py", "materializar_t8_c5b.py", "verificar_t8_c5b.py", "admision_integracion.py", "receta_t8_c5b.sh")
DATOS = ("MANIFIESTO_T8_C5B.json", "MANIFIESTO_T8_C5B-ENSAYO.json")
TAREAS = ("T8-C5B-MATERIALIZAR", "T8-C5B-VERIFICAR")
OPERACION = "CAPTURA_T8_EXCLUSION_C5B"
LIMITES = {"procesos": 1, "tope_s": 600.0, "intentos": 1, "union_s": 10800.0}
KIND_MANIFIESTO = "manifiesto-t8-exclusion-c5b-v1"
KIND_ALCANCE = "autorizacion-alcance-paso4-v3"
DESPLIEGUE = "f293a0a62d2cb6bf3517e72a0bfc589ee703685d4434c2cdae4b4cd1b5085d6c"
ACTA_P3 = "8e59ea4870c987ecca4ea1e5a8cb3f95581fcc1a64b3e7aa61c035a9b8e0dcfc"
HISTORICOS = {"d3076d0d501e76f716eb1ef7afe4d2a88b1023acab05fd9418cdd509e670d379": "alcance λ rem137 (consumido)",
              "01b9633aa382b49dce7af78a8af8ec939c88aaffb0175ab91b8edec94991e4bd": "alcance de captura rem139 (consumido)",
              "210015d7b949ba0eff708c082c25536bcabe80ca70a8c5351df701611978895a": "alcance del testigo alto rem141 (consumido)",
              "b5565c3fab41967d6c99f5b6ae3c9c7e79c0a58268660520f91f72303fb913b1": "alcance de emisión del testigo rem143 (consumido)"}
FIXTURE = "FIXTURE — documento de prueba rem145, NO productivo: "
ETIQUETA = ("ALCANCE v3 CAPTURA_T8_EXCLUSION_C5B — autoriza SOLO materializar y verificar la vista de captura T8 que aplica la exclusión C5B "
            "aceptada (aceptación técnica rem145 a816420c…, certificado fc403d40…, cota U_global_hi exacta + banda) a EXACTAMENTE las cinco filas "
            "pendientes 7028/7208/8144/8186/9578 de la vista vigente ec6e3929…; las 13.651 restantes se copian sin cambios; ningún modelo, techo, "
            "malla, quiebre, Q, barrido, reproducción, exportación ni publicación; aprobación solo por decisión humana nativa sobre su sha256")
H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
HF = lambda p: H(Path(p).read_bytes())  # noqa: E731
PRODUCTO, RESUMEN, SELLO = "VISTA_T8_CAPTURA.jsonl", "VISTA_RESUMEN.json", "VISTA.sha256"
KIND_PRODUCTO = {"produccion": "vista-t8-captura-c5b-PRODUCCION", "candidata": "vista-t8-captura-c5b-CANDIDATA",
                 "ensayo": "vista-t8-captura-c5b-ENSAYO"}
COMPARTIDOS = ("modo", "manifiesto_sha256", "indice_sha256", "alcance_sha256", "decision")
DERIVADOS_DEL_MODO = ("kind", "productivo")
POR_OPERACION = ("tarea", "entradas")
DUPLICADOS_DEL_RESUMEN = ("modo", "manifiesto_sha256")
TIPO_CAPTURA = "captura_pendiente_sin_soporte_C2"
TIPO_PRUEBA = "exclusion_cota_U_global"
SEMANTICA = "encierro_exterior_por_cota_U_global"
REGLA = "Fraction(v) > U_global + banda  =>  outside_support (la igualdad no excluye; nunca prueba pertenencia)"
REGLA_ACEPTADA = "Fraction(v) > U_global_hi + banda; strict exclusion only; no membership inference"
MAGNITUD = {"k": "C2", "target_unit": "share"}
W = r"@@W_WIN@@"
FILAS_C5B = [
    {"fila": 7028, "clave_fila": "273d71ee0f67962a2f407f0874046e684c599650a1aaac6783996cc481482051", "run_destino": "BRUN-9c6c66e7af8b139a613b1c3f",
     "valor_exacto": "7089940826878089/9007199254740992", "linea_vista_sha256": "26f9150c25f0703c04d55689ed3040b0de45281648a11bde397d3700f0c219fb"},
    {"fila": 7208, "clave_fila": "869cc35d96ad584bc0dc9619bda895cc17713bd2c7861a3030ca9c3b68a8aa30", "run_destino": "BRUN-63a9e9ea157b2faaf317ae61",
     "valor_exacto": "3544220821268237/4503599627370496", "linea_vista_sha256": "21a4f0df4b15ea30f74b24a5062fddb8c616ae0767e3ff4c4d62b66fd5b260d4"},
    {"fila": 8144, "clave_fila": "314a614e7e163b62587dc10f8a2bcc84ad02c92c38375d5f27e6bc4a1bbc7bed", "run_destino": "BRUN-991c466a1938ddbf2192eefb",
     "valor_exacto": "3550769140379883/4503599627370496", "linea_vista_sha256": "6b5920a24e079790d35dc54eaa636c208bff1fd3eeb10efa9e6194921a85a63d"},
    {"fila": 8186, "clave_fila": "9c2782cf675d790889a46f269733c51dc1b62f0b23806f6a14cf04223c73d433", "run_destino": "BRUN-1368187e9a43de0d95926dca",
     "valor_exacto": "3537073397432819/4503599627370496", "linea_vista_sha256": "93bb989720d2be5047162039b7dc748027af3633f75cb17c7b93ba7712e7f5bb"},
    {"fila": 9578, "clave_fila": "4a16cc773f46a0424a4c4903de1358cebd501a04715f697c62168698d8b4a012", "run_destino": "BRUN-cb33e6b24039acc84fb1a065",
     "valor_exacto": "7051605380861609/9007199254740992", "linea_vista_sha256": "981d500cb3a590fd08c38eada7fd1125923fc060ca7e09cee6fc0114f97f03b3"}]
FILA_C5B = {x["fila"]: x for x in FILAS_C5B}
INDICES_C5B = sorted(FILA_C5B)
TESTIGO_ALTO_PRESERVADAS = [6884, 6902, 6926, 7172, 7196, 7244, 7322, 7598, 7682, 7772, 7916, 7958, 7964, 8288, 8378, 8462, 8552, 8606, 8636, 8654,
                            8786, 8876, 8930, 9014, 9020, 9188, 9224, 9260, 9350, 9398, 9458, 9542, 9560, 9680, 9686]
ESPERADO = {"filas": 13656, "no_captura": 11545, "definitivo_almacenado": 9434, "lambda_finalizadas": 2111, "captura_filas": 2111,
            "captura_computed": 963, "captura_outside_support": 1148, "captura_pendiente": 0, "definitivas_candidatas": 13656, "pendientes": 0,
            "captura_por_tipo": {"exclusion_cota_33_10": 264, "exclusion_cota_U": 879, "exclusion_cota_U_global": 5, "pertenencia_misma_corrida": 365,
                                 "pertenencia_testigo_alto": 35, "pertenencia_transferida": 563},
            "captura_pendientes_por_causa": {}, "captura_cambios": 963, "actualizadas_por_c5b": INDICES_C5B,
            "testigo_alto_preservadas": TESTIGO_ALTO_PRESERVADAS, "pendientes_filas": []}
AUTORIDAD = {
    "base_vista": {"area": "paso4_emision_t8_testigo_desde_rem143",
                   "inventario": {"ruta": "tmp/paso4_emision_t8_testigo_desde_rem143/audit/entrega.json",
                                  "sha256": "0dd9b3d81e120ad685995ce5ba988ddf356c29bce24e1a88505e258c67e1a8da"},
                   "rel": "t8_testigo_vista_T8_TESTIGO/VISTA_T8_CAPTURA.jsonl",
                   "sha256": "ec6e3929dd6be8dbb56b17493ce51061b95dde7991722832045a1c4411c8fd93",
                   "estado_formal": {"definitivas": 13651, "pendientes": 5}},
    "ledger": {"ruta": W + r"\review_20261104_rem144_T8_testigo_aceptado.json",
               "sha256": "7ed13ccf8123e1bce9e013bdbdce56d5df29de37699a192f1aaa32c55555241c"},
    "aceptacion": {"ruta": W + r"\review_20261104_rem145_COTA_C5B_ACEPTADA.json",
                   "sha256": "a816420c6a495996959195c238185a9ad90f2e29b3601fb1239b5a16a49badea"},
    "dictamen": {"ruta": W + r"\review_20261104_rem145_dictamen.txt", "sha256": "b77f436a8647f82a4c641f0b801970317853d917ebccc40bccce8eb091a7ca51"},
    "nota_cota": {"ruta": W + r"\review_20261104_rem145_cota.txt", "sha256": "893abeeca3baf6bdba3c6fd5069eb80bfd06376a24827706551a8dffa0128da1"},
    "prueba_c5b": {"area": "paso4_cinco_filas_exp0_desde_rem144",
                   "inventario": {"ruta": "tmp/paso4_cinco_filas_exp0_desde_rem144/audit/entrega.json",
                                  "sha256": "f64f14c270940b44ef6db094cd5eb4a5e03e7febd13976c45388e551ce12fddd"},
                   "certificado": {"rel": "cinco_filas/certificado/CERTIFICADO_C5B_CANDIDATO.json",
                                   "sha256": "fc403d40b1eb6ba50e5f8dc551ecd301b19b1092e15c5e50ff4e163fc51afa16"},
                   "salida_m2": {"rel": "cinco_filas/salida/C5B_MASA_M2.json", "sha256": "05c10ea6d2e8f87b96704f66d9c1edb6c188a2d6c528b4d086ab3061d9da4691"},
                   "script_certificado": {"rel": "cinco_filas/ejecutado/certificado_c5b.C3.py",
                                          "sha256": "cd0bae74e80c66ed1a1268229ad82db14336bba80796a6356987887130bbaf5d"},
                   "script_m2": {"rel": "cinco_filas/ejecutado/cota_masa_c5b.M2.py",
                                 "sha256": "f725f028ff1fa63281a69d5ff30fa51df988cb9ac4f9654ab62e9a29355b3a1b"}},
    "cota": {"U_global_hi": "15432592858721952385078662585664465762806429615972266476412514029254334532321/"
                            "19815838360430182000000000000000000000000000000000000000000000000000000000000",
             "banda": "944473296573929/9444732965739290427392", "regla": REGLA, "regla_aceptada": REGLA_ACEPTADA, "tipo_prueba": TIPO_PRUEBA},
    "certificacion": {"area": "paso4_emision_lambda_conexion_captura_desde_rem137",
                      "inventario": {"ruta": "tmp/paso4_emision_lambda_conexion_captura_desde_rem137/audit/entrega.json",
                                     "sha256": "59188e65c2d8dd665679f3b47780e2859633505b260127cc435c772431bf92b2"},
                      "dir": "c2_conexion/candidato_v3",
                      "certificacion_fila_sha256": "4741b4ea3b72fc2f754cc2d8c79dd9dd718f8e37205bf3e4ee5c0c539be60f4b",
                      "fuentes_sha256": "77d9a10b409416a0f148ff665584c20e4a8f8d997862e4b79cc7f8b5f1c506e1",
                      "conexion_captura_sha256": "f7a8d23f5d2558843f4620052b49d20250cf23c67ac8a02d54ea57db1c05dba7",
                      "nota_U_sha256": "cf738de6945a86ffb55ed0994610bc6d8d9d21860a5cd0b7e92a27f0afe0f34a"},
    "plan_config": {"base_sets": ["CMP-E1.macro", "CMP-E1.micro", "COL-E2-2023.2023p.macro", "COL-E2-2023.2023p.micro", "COL-E2-2023.2024p.macro",
                                  "COL-E2-2023.2024p.micro", "PER-E0E3.macro", "PER-E0E3.micro", "PER-E1.macro", "PER-E1.micro"],
                    "derived_suffixes": [], "level": 0, "max_unit_nodes": 64, "designs": ["G", "N"]},
    "finalizador": {"ruta": "paso4/instalacion/herramientas/b/unidades.py",
                    "sha256": "a8aded1db50f80feffd62bcb655e62e5f93487364a3c4e625f47dcdbd1f17c86",
                    "sys_path": ["paso4/instalacion/src", "paso4/instalacion"]},
    "nucleo": {"identidad": NUCLEO_IDENTIDAD, "ruta": "tmp/paso4_raices_impacto_desde_rem116/candidato_c0/instalacion"},
    "control": {"admision_cierre": {"origen": "tmp/paso4_emision_lambda_conexion_captura_desde_rem137/c2_conexion/candidato_v3/admision_integracion.py",
                                    "sha256": "7304ac8be5e2d2c33fd16ccf79611285aba2baf4ebd089ba73f33679363603c9"},
                "p3ctl": "codigo/p3ctl.py", "sha256": "546271b057a9635ab39ca3f94e0fd79da46cc7091a4bff873ab8c54e6d875841"},
    "filas_c5b": FILAS_C5B,
    "corridas": ["BRUN-050091213b198d7cd7ba9ea2", "BRUN-1368187e9a43de0d95926dca", "BRUN-47e3d9f48d2b65e9ddeed02f", "BRUN-4ef8507fcdefbddc55dbc3b7",
                 "BRUN-5b35ba3f51bc08bd48b384bd", "BRUN-612818cb081c6797d4923b4d", "BRUN-63a9e9ea157b2faaf317ae61", "BRUN-7bdfe0a1bee57298e31e1b34",
                 "BRUN-991c466a1938ddbf2192eefb", "BRUN-9c6c66e7af8b139a613b1c3f", "BRUN-a81e3f45f7111e18b1f39370", "BRUN-c5af32a993773f5258ce570f",
                 "BRUN-cb33e6b24039acc84fb1a065", "BRUN-f5f58960bbf9017776d3d7fc"],
    "esperado": ESPERADO,
    "operacion": OPERACION, "tareas": list(TAREAS), "limites": LIMITES,
    "plan_sha256": "6cec0a6d662104dab6a490cea647cd24ae995819a416eaf3cfd4fd9f3c060e42"}
CAMPOS_MANIFIESTO = frozenset(AUTORIDAD) | {"kind", "destinos", "nota", "produccion_habilitada"}
ESQUEMA_PRUEBA = frozenset(("tipo", "fila", "run_destino", "cell_id", "ref_fila", "fila_en_unidad", "valor_requerido", "valor_requerido_exacto", "escala",
                            "clave_fila", "linea_vista_sha256", "magnitud", "normalizacion", "cota", "banda", "regla", "certificado_sha256",
                            "aceptacion_sha256", "analisis_salida_sha256", "nota_U_sha256", "premisas_U_sha256", "plan_sha256", "fuentes_sha256"))


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
    return {"manifiesto_t8_c5b": H(me_raw), "paquete_t8_c5b": idx_sha, "codigo_t8_c5b": {n: HF(AQUI / n) for n in PIEZAS},
            "datos_paquete": {n: HF(AQUI / n) for n in DATOS}, "base_vista": AUTORIDAD["base_vista"], "ledger": AUTORIDAD["ledger"],
            "aceptacion": AUTORIDAD["aceptacion"], "dictamen": AUTORIDAD["dictamen"], "nota_cota": AUTORIDAD["nota_cota"],
            "prueba_c5b": AUTORIDAD["prueba_c5b"], "cota": AUTORIDAD["cota"], "certificacion": AUTORIDAD["certificacion"],
            "plan_config": AUTORIDAD["plan_config"], "finalizador": AUTORIDAD["finalizador"], "nucleo": AUTORIDAD["nucleo"],
            "control": AUTORIDAD["control"], "filas_c5b": FILAS_C5B, "corridas": AUTORIDAD["corridas"], "esperado_no_aceptado": ESPERADO}


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
                        (al.get("lote_manifiesto_sha256") == ent.get("manifiesto_t8_c5b") == H(me_raw), "ALCANCE_DE_OTRO_MANIFIESTO"),
                        (ent.get("paquete_t8_c5b") == idx_sha and ent.get("codigo_t8_c5b") == esp["entradas"]["codigo_t8_c5b"],
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
    if pu["tarea"] != "T8-C5B-MATERIALIZAR":
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
    P = AUTORIDAD["prueba_c5b"]
    return {"base_vista_sha256": AUTORIDAD["base_vista"]["sha256"], "base_vista_inventario_sha256": AUTORIDAD["base_vista"]["inventario"]["sha256"],
            "ledger_sha256": AUTORIDAD["ledger"]["sha256"], "aceptacion_sha256": AUTORIDAD["aceptacion"]["sha256"],
            "dictamen_sha256": AUTORIDAD["dictamen"]["sha256"], "nota_cota_sha256": AUTORIDAD["nota_cota"]["sha256"],
            "prueba_inventario_sha256": P["inventario"]["sha256"], "certificado_sha256": P["certificado"]["sha256"],
            "salida_m2_sha256": P["salida_m2"]["sha256"], "script_certificado_sha256": P["script_certificado"]["sha256"],
            "script_m2_sha256": P["script_m2"]["sha256"], "cota": AUTORIDAD["cota"],
            "certificacion_fila_sha256": AUTORIDAD["certificacion"]["certificacion_fila_sha256"],
            "fuentes_captura_sha256": AUTORIDAD["certificacion"]["fuentes_sha256"], "finalizador_sha256": AUTORIDAD["finalizador"]["sha256"],
            "plan_sha256": AUTORIDAD["plan_sha256"], "estado_formal_base": AUTORIDAD["base_vista"]["estado_formal"]}


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


def _cotejar_aceptacion(acc, dic_raw, nota_raw):
    """La aceptación técnica rem145 debe nombrar EXACTAMENTE esta autoridad (dictamen, nota, entrega, piezas, cota, regla, fijaciones, cinco filas,
    universo) y sus banderas de no emisión; devuelve sus filas por índice."""
    P, C, Cc = AUTORIDAD["prueba_c5b"], AUTORIDAD["cota"], AUTORIDAD["certificacion"]
    pins = {"analisis_salida_sha256": P["salida_m2"]["sha256"], "analisis_script_sha256": P["script_m2"]["sha256"],
            "vista_sha256": AUTORIDAD["base_vista"]["sha256"], "ledger_rem144_sha256": AUTORIDAD["ledger"]["sha256"],
            "nota_U_sha256": Cc["nota_U_sha256"], "fuentes_captura_sha256": Cc["fuentes_sha256"], "finalizador_sha256": AUTORIDAD["finalizador"]["sha256"],
            "conexion_captura_sha256": Cc["conexion_captura_sha256"], "certificacion_fila_sha256": Cc["certificacion_fila_sha256"],
            "plan_sha256": AUTORIDAD["plan_sha256"]}
    filas = {x.get("fila"): x for x in acc.get("five_rows_evidence") or [] if isinstance(x, dict)}
    for cond, causa in ((acc.get("kind") == "aceptacion_tecnica_de_demostracion_no_emision", "ACEPTACION_FUERA_DE_ESQUEMA"),
                        (acc.get("review_sha256") == H(dic_raw) == AUTORIDAD["dictamen"]["sha256"]
                         and acc.get("note_sha256") == H(nota_raw) == AUTORIDAD["nota_cota"]["sha256"], "ACEPTACION_DE_OTRO_DICTAMEN"),
                        (acc.get("inventory_sha256") == P["inventario"]["sha256"] and acc.get("analysis_sha256") == P["script_m2"]["sha256"]
                         and acc.get("M2_sha256") == P["salida_m2"]["sha256"] and acc.get("certificate_script_sha256") == P["script_certificado"]["sha256"]
                         and acc.get("certificate_sha256") == P["certificado"]["sha256"], "ACEPTACION_DE_OTRA_PRUEBA"),
                        (acc.get("U_global_hi") == C["U_global_hi"] and acc.get("banda") == C["banda"] and acc.get("accepted_rule") == REGLA_ACEPTADA,
                         "ACEPTACION_CON_OTRA_COTA_O_REGLA"),
                        (canon(acc.get("source_pins")) == canon(pins), "ACEPTACION_CON_OTRAS_FIJACIONES"),
                        (canon(acc.get("accepted_plan_config")) == canon(AUTORIDAD["plan_config"]), "ACEPTACION_CON_OTRO_UNIVERSO"),
                        (sorted(filas) == INDICES_C5B and acc.get("only_pending_indices") == INDICES_C5B
                         and all(filas[i].get("clave_fila") == x["clave_fila"] and filas[i].get("run_destino") == x["run_destino"]
                                 and filas[i].get("valor_requerido_exacto") == x["valor_exacto"]
                                 and filas[i].get("linea_vista_sha256") == x["linea_vista_sha256"] and filas[i].get("magnitud") == MAGNITUD
                                 and filas[i].get("estado") == "demostracion_candidata_suficiente" and filas[i].get("causa") is None
                                 and (filas[i].get("cota") or {}).get("U_global_hi") == C["U_global_hi"]
                                 and (filas[i].get("cota") or {}).get("banda") == C["banda"] for i, x in FILA_C5B.items()),
                         "ACEPTACION_CON_OTRAS_FILAS"),
                        (acc.get("technical_proof_accepted") is True and acc.get("production_package_accepted") is False
                         and acc.get("production_emitted") is False and acc.get("production_authorized") is False
                         and acc.get("official_flags_enabled") is False, "ACEPTACION_CON_OTRAS_BANDERAS"),
                        (acc.get("T8_formal_definitive") == 13651 and acc.get("T8_formal_pending") == 5 and acc.get("preserve_other_lines_byte_exact") == 13651
                         and acc.get("current_T8_product_sha256") == AUTORIDAD["base_vista"]["sha256"], "ACEPTACION_CON_OTRO_ESTADO_FORMAL")):
        need(cond, causa)
    return filas


def _cotejar_certificado(cert, acc):
    """El certificado (nombre histórico CANDIDATO, intacto) debe coincidir con la aceptación; U_global_hi se recalcula como el máximo EXACTO de los
    cuatro bloques y cada holgura, desde el valor exacto. Su «conforme» no basta por sí solo."""
    C = AUTORIDAD["cota"]
    U, b = Fraction(C["U_global_hi"]), Fraction(C["banda"])
    filas = {x.get("fila"): x for x in cert.get("filas") or [] if isinstance(x, dict)}
    try:
        u_max = max(Fraction(v) for v in (cert.get("cotas_por_bloque") or {}).values())
    except (TypeError, ValueError, ZeroDivisionError):
        u_max = None
    for cond, causa in ((cert.get("kind") == "certificado-candidato-c5b-rem144" and cert.get("conforme") is True and cert.get("fallos") == []
                         and cert.get("productivo") is False, "CERTIFICADO_FUERA_DE_ESQUEMA"),
                        (cert.get("U_global_hi") == C["U_global_hi"] and cert.get("banda") == C["banda"] and u_max == U
                         and len(cert.get("cotas_por_bloque") or {}) == 4, "CERTIFICADO_CON_OTRA_COTA"),
                        (cert.get("tipo_prueba_propuesto") == TIPO_PRUEBA and cert.get("regla_propuesta") == REGLA
                         and cert.get("semantica_propuesta") == SEMANTICA, "CERTIFICADO_CON_OTRA_REGLA"),
                        (canon(cert.get("fuentes")) == canon(acc.get("source_pins")), "CERTIFICADO_CON_OTRAS_FUENTES"),
                        (canon(cert.get("premisas")) == canon(acc.get("premises")), "CERTIFICADO_CON_OTRAS_PREMISAS"),
                        (sorted(filas) == INDICES_C5B, "CERTIFICADO_CON_OTRAS_FILAS")):
        need(cond, causa)
    for i, x in FILA_C5B.items():
        c = filas[i]
        a = (acc.get("five_rows_evidence") or [])[INDICES_C5B.index(i)]
        need(c.get("clave_fila") == x["clave_fila"] and c.get("run_destino") == x["run_destino"] and c.get("valor_requerido_exacto") == x["valor_exacto"]
             and c.get("linea_vista_sha256") == x["linea_vista_sha256"] and c.get("magnitud") == MAGNITUD and c.get("cell_id") == a.get("cell_id")
             and Fraction(c.get("valor_requerido")) == Fraction(x["valor_exacto"]), "CERTIFICADO_FILA_DISTINTA:%d" % i)
        need((c.get("cota") or {}).get("U_global_hi") == C["U_global_hi"] and (c.get("cota") or {}).get("banda") == C["banda"]
             and (c.get("cota") or {}).get("U_global_mas_banda") == str(U + b)
             and c.get("holgura_exacta") == str(Fraction(x["valor_exacto"]) - (U + b)) == a.get("holgura_exacta"), "CERTIFICADO_HOLGURA_DISTINTA:%d" % i)
        need(c.get("estado") == "demostracion_candidata_suficiente" and c.get("causa") is None, "CERTIFICADO_FILA_NO_SUFICIENTE:%d" % i)
    return filas


def _cotejar_m2(m2, cert):
    """La salida M2 aceptada (análisis reproducido por el revisor) debe dar la misma cota, banda, bloques, premisas y decisión por fila."""
    C = AUTORIDAD["cota"]
    filas = {x.get("fila"): x for x in m2.get("filas") or [] if isinstance(x, dict)}
    dec = {x.get("fila"): x for x in m2.get("decision_por_fila") or [] if isinstance(x, dict)}
    for cond, causa in ((m2.get("kind") == "c5b-cota-masa-adoptante-rem144" and m2.get("modo") == "real" and m2.get("conforme") is True
                         and m2.get("fallos") == [] and m2.get("masa_ok") is True, "M2_FUERA_DE_ESQUEMA"),
                        (m2.get("U_global_hi") == C["U_global_hi"] and m2.get("banda") == C["banda"]
                         and canon(m2.get("cotas_por_bloque")) == canon(cert.get("cotas_por_bloque")), "M2_CON_OTRA_COTA"),
                        (canon(m2.get("premisas")) == canon(cert.get("premisas")), "M2_CON_OTRAS_PREMISAS"),
                        (sorted(filas) == INDICES_C5B and sorted(dec) == INDICES_C5B, "M2_CON_OTRAS_FILAS")):
        need(cond, causa)
    for i, x in FILA_C5B.items():
        f, d = filas[i], dec[i]
        need(f.get("clave_fila") == x["clave_fila"] and f.get("run") == x["run_destino"] and f.get("v_exacto") == x["valor_exacto"]
             and f.get("linea_sha256") == x["linea_vista_sha256"], "M2_FILA_DISTINTA:%d" % i)
        need(d.get("clave_fila") == x["clave_fila"] and d.get("v_exacto") == x["valor_exacto"] and d.get("cota_global_hi") == C["U_global_hi"]
             and d.get("banda") == C["banda"] and d.get("holgura_exacta") == (cert["filas"][INDICES_C5B.index(i)].get("holgura_exacta"))
             and d.get("estado") == "demostracion_candidata_suficiente_exclusion" and d.get("causa") is None, "M2_DECISION_DISTINTA:%d" % i)


def _cotejar_ledger(led):
    """Registro aceptado rem144: la vista vigente y sus cinco filas pendientes (clave, corrida, valor y huella de línea)."""
    filas = {x.get("row"): x for x in led.get("pending_rows") or [] if isinstance(x, dict)}
    need(led.get("kind") == "accepted-T8-high-witness-emission-rem144" and led.get("inventory_sha256") == AUTORIDAD["base_vista"]["inventario"]["sha256"]
         and led.get("product_sha256") == AUTORIDAD["base_vista"]["sha256"], "LEDGER_DE_OTRA_VISTA")
    need(sorted(filas) == INDICES_C5B and all(filas[i].get("row_key") == x["clave_fila"] and filas[i].get("destination_run") == x["run_destino"]
                                              and filas[i].get("required_exact") == x["valor_exacto"]
                                              and filas[i].get("product_line_sha256") == x["linea_vista_sha256"]
                                              and filas[i].get("classification") == "pendiente" for i, x in FILA_C5B.items()), "LEDGER_CON_OTRAS_PENDIENTES")


def _paper2b():
    return {k: getattr(m, "__file__", None) for k, m in list(sys.modules.items()) if k == "paper2b" or k.startswith("paper2b.")}


def _aislar_paper2b():
    """(corrección tras REM142-H1) cada uso del núcleo se carga en un espacio de módulos paper2b LIMPIO (sys.modules es del proceso)."""
    for k in _paper2b():
        del sys.modules[k]


def cargar(R, me):
    """Fuentes SOLO por la AUTORIDAD de este módulo (igual a la del manifiesto); los mismos bytes autenticados se interpretan y se usan."""
    R = Path(R)
    need(isinstance(me, dict) and all(canon(me.get(k)) == canon(v) for k, v in AUTORIDAD.items()), "MANIFIESTO_DISTINTO_DE_LA_AUTORIDAD")
    fin, P, Cc = AUTORIDAD["finalizador"], AUTORIDAD["prueba_c5b"], AUTORIDAD["certificacion"]
    rutas_fin = [str(R / p) for p in fin["sys_path"]]
    base_raw = _bytes_inventariados(R, AUTORIDAD["base_vista"])
    led_raw = _bytes_fijados(AUTORIDAD["ledger"]["ruta"], AUTORIDAD["ledger"]["sha256"], "LEDGER_NO_AUTENTICO")
    acc_raw = _bytes_fijados(AUTORIDAD["aceptacion"]["ruta"], AUTORIDAD["aceptacion"]["sha256"], "ACEPTACION_NO_AUTENTICA")
    dic_raw = _bytes_fijados(AUTORIDAD["dictamen"]["ruta"], AUTORIDAD["dictamen"]["sha256"], "DICTAMEN_NO_AUTENTICO")
    nota_raw = _bytes_fijados(AUTORIDAD["nota_cota"]["ruta"], AUTORIDAD["nota_cota"]["sha256"], "NOTA_DE_LA_COTA_NO_AUTENTICA")
    piezas = {n: _bytes_inventariados(R, {"area": P["area"], "inventario": P["inventario"], "rel": P[n]["rel"], "sha256": P[n]["sha256"]})
              for n in ("certificado", "salida_m2", "script_certificado", "script_m2")}
    acc = json.loads(acc_raw)
    filas_acc = _cotejar_aceptacion(acc, dic_raw, nota_raw)
    cert = json.loads(piezas["certificado"])
    filas_cert = _cotejar_certificado(cert, acc)
    _cotejar_m2(json.loads(piezas["salida_m2"]), cert)
    _cotejar_ledger(json.loads(led_raw))
    # regla de exclusión aceptada reutilizada: certificacion_fila (Contexto, constantes) por el inventario sellado rem137, sin cambios
    files = _inventario(R, Cc["inventario"])
    D = R / "tmp" / Cc["area"] / Cc["dir"]
    for n, s in (("certificacion_fila.py", Cc["certificacion_fila_sha256"]), ("FUENTES_CAPTURA.json", Cc["fuentes_sha256"]),
                 ("conexion_captura.py", Cc["conexion_captura_sha256"])):
        need(files.get(Cc["dir"] + "/" + n, {}).get("sha256") == s == HF(D / n), "CERTIFICACION_NO_AUTENTICA:%s" % n)
    CF = _modulo("certificacion_fila_t8_c5b", D / "certificacion_fila.py", Cc["certificacion_fila_sha256"])
    need(CF.FUENTES_SHA256 == Cc["fuentes_sha256"] and CF.NOTA_U_SHA256 == Cc["nota_U_sha256"] and CF.PLAN == AUTORIDAD["plan_sha256"],
         "CERTIFICACION_CON_OTRA_AUTORIDAD")
    try:
        ctx = CF.Contexto(R)
    except CF.Rechazo as ex:
        raise Rechazo("CONTEXTO_DE_CERTIFICACION_RECHAZADO:%s" % ex) from None
    need(ctx.banda == Fraction(AUTORIDAD["cota"]["banda"]) and (ctx.fuentes.get("cota_U") or {}).get("banda") == AUTORIDAD["cota"]["banda"],
         "BANDA_DISTINTA_DEL_CONTRATO")
    # finalizador instalado: espacio paper2b limpio y rutas de la instalación delante; sus módulos deben ser los de la instalación
    _aislar_paper2b()
    for p in reversed(rutas_fin):
        sys.path.insert(0, p)
    UN = _modulo("unidades_finalizador_t8_c5b", R / fin["ruta"], fin["sha256"])
    src_inst = (R / fin["sys_path"][0]).resolve()
    mod_fin = _paper2b()
    need(all(f and src_inst in Path(f).resolve().parents for f in mod_fin.values()), "FINALIZADOR_CON_MODULOS_AJENOS")
    base = lineas(base_raw)
    bfilas = [json.loads(x) for x in base]
    rb = resumen_de(bfilas)
    need(rb["definitivas_candidatas"] == AUTORIDAD["base_vista"]["estado_formal"]["definitivas"]
         and rb["pendientes"] == AUTORIDAD["base_vista"]["estado_formal"]["pendientes"] and rb["filas"] == ESPERADO["filas"]
         and rb["pendientes_filas"] == INDICES_C5B, "BASE_CON_OTRO_ESTADO_FORMAL")
    return {"finalizar": UN._finalize, "base_raw": base_raw, "base": base, "bfilas": bfilas, "CF": CF, "ctx": ctx,
            "certificado": filas_cert, "aceptacion": filas_acc,
            "prueba": {"certificado_sha256": P["certificado"]["sha256"], "salida_m2_sha256": P["salida_m2"]["sha256"],
                       "aceptacion_sha256": AUTORIDAD["aceptacion"]["sha256"], "premisas_U_sha256": ctx.premisas_U_sha256,
                       "premisas_U_ok": ctx.premisas_U_ok, "nota_U_ok": ctx.nota_U_ok, "conjuntos_base": ctx.premisas_U.get("conjuntos_base"),
                       "aislamiento_modulos": {"finalizador_paper2b": len(mod_fin)}}}


def desigualdad_c5b(v):
    """Regla adicional C5B, exacta: Fraction(v) > U_global_hi + banda. -> (cumple, detalle). La igualdad no excluye; nunca prueba pertenencia."""
    U, b = Fraction(AUTORIDAD["cota"]["U_global_hi"]), Fraction(AUTORIDAD["cota"]["banda"])
    fv = Fraction(v)
    lim = U + b
    return fv > lim, {"valor": str(fv), "U_global_hi": str(U), "banda": str(b), "cota_mas_banda": str(lim), "holgura": str(fv - lim),
                      "cumple": fv > lim, "regla": REGLA}


def prueba_c5b(carga, i, f):
    """Prueba por fila desde el CERTIFICADO autenticado (no del llamador); validar_c5b la coteja con el contexto, la vista y la autoridad."""
    c, ctx, CF = carga["certificado"][i], carga["ctx"], carga["CF"]
    return {"tipo": TIPO_PRUEBA, "fila": i, "run_destino": c["run_destino"], "cell_id": c["cell_id"], "ref_fila": f["historico"]["ref"],
            "fila_en_unidad": f["historico"]["fila_en_unidad"], "valor_requerido": c["valor_requerido"], "valor_requerido_exacto": c["valor_requerido_exacto"],
            "escala": CF.ESCALA, "clave_fila": c["clave_fila"], "linea_vista_sha256": c["linea_vista_sha256"], "magnitud": c["magnitud"],
            "normalizacion": CF.MAGNITUD_U, "cota": c["cota"]["U_global_hi"], "banda": c["cota"]["banda"], "regla": REGLA,
            "certificado_sha256": AUTORIDAD["prueba_c5b"]["certificado"]["sha256"], "aceptacion_sha256": AUTORIDAD["aceptacion"]["sha256"],
            "analisis_salida_sha256": AUTORIDAD["prueba_c5b"]["salida_m2"]["sha256"], "nota_U_sha256": CF.NOTA_U_SHA256,
            "premisas_U_sha256": ctx.premisas_U_sha256, "plan_sha256": AUTORIDAD["plan_sha256"], "fuentes_sha256": CF.FUENTES_SHA256}


def validar_c5b(ctx, CF, p, f, linea):
    """ÚNICA validación de la regla C5B por fila (forma de exclusion_cota_U de certificacion_fila, cota U_global_hi). -> (True, estado) | (False, motivo)."""
    if not isinstance(p, dict) or p.get("tipo") != TIPO_PRUEBA:
        return False, "TIPO_DESCONOCIDO"
    if set(p) != ESQUEMA_PRUEBA:
        return False, "PRUEBA_FUERA_DE_ESQUEMA"
    i = p["fila"]
    x = FILA_C5B.get(i) if isinstance(i, int) and not isinstance(i, bool) else None
    a = ctx.captura.get(i) if x is not None else None
    if a is None or not isinstance(f, dict):
        return False, "FILA_FUERA_DE_LA_ACEPTACION"
    dest = ctx.run_de.get(a["ref"].split("/", 1)[0])
    if (p["run_destino"] != dest or dest != x["run_destino"] or f.get("run_id") != dest or p["cell_id"] != a["cell_id"] or f.get("cell_id") != a["cell_id"]
            or p["ref_fila"] != a["ref"] or p["fila_en_unidad"] != a["fila_en_unidad"] or p["clave_fila"] != x["clave_fila"]
            or f.get("clave_fila") != x["clave_fila"] or f.get("fila_anexo") != i):
        return False, "FILA_NO_COINCIDE"
    if p["linea_vista_sha256"] != x["linea_vista_sha256"] or H(linea + b"\n") != x["linea_vista_sha256"]:
        return False, "LINEA_DE_LA_VISTA_DISTINTA"
    v = a["fin_por_unidad"]["value"]
    try:
        vf = (f.get("historico") or {}).get("fin_por_unidad", {}).get("value")
        valor_ok = (isinstance(v, float) and p["valor_requerido"] == v == vf and p["valor_requerido_exacto"] == x["valor_exacto"]
                    and Fraction(p["valor_requerido_exacto"]) == Fraction(v) and p["escala"] == CF.ESCALA and a["fin_por_unidad"].get("c2_defined") is True)
    except (TypeError, ValueError, ZeroDivisionError, AttributeError):
        valor_ok = False
    if not valor_ok:
        return False, "VALOR_O_ESCALA_NO_COINCIDE"
    if a["fin_por_unidad"].get("k") != MAGNITUD["k"] or a.get("target_unit") != MAGNITUD["target_unit"] or p["magnitud"] != MAGNITUD \
            or p["normalizacion"] != CF.MAGNITUD_U:
        return False, "UNIDAD_O_MAGNITUD_NO_ES_C2_SHARE"
    if ctx.plan.get(dest) != AUTORIDAD["plan_sha256"] or p["plan_sha256"] != AUTORIDAD["plan_sha256"]:
        return False, "PLAN_DISTINTO"
    if not (ctx.nota_U_ok and ctx.premisas_U_ok):
        return False, "PREMISA_NO_CUBIERTA"
    if ctx.premisas_U.get("conjuntos_base") != AUTORIDAD["plan_config"]["base_sets"] or ctx.premisas_U.get("menus") != ["d", "df", "f"]:
        return False, "PREMISA_NO_CUBIERTA:UNIVERSO"
    for campo, autoridad in (("certificado_sha256", AUTORIDAD["prueba_c5b"]["certificado"]["sha256"]), ("aceptacion_sha256", AUTORIDAD["aceptacion"]["sha256"]),
                             ("analisis_salida_sha256", AUTORIDAD["prueba_c5b"]["salida_m2"]["sha256"]), ("nota_U_sha256", CF.NOTA_U_SHA256),
                             ("premisas_U_sha256", ctx.premisas_U_sha256), ("fuentes_sha256", CF.FUENTES_SHA256)):
        if p[campo] != autoridad:
            return False, "EXCLUSION_C5B_REFERENCIA_DISTINTA:" + campo
    try:
        banda_ok = isinstance(p["banda"], str) and Fraction(p["banda"]) == ctx.banda == Fraction(AUTORIDAD["cota"]["banda"])
    except (ValueError, ZeroDivisionError):
        banda_ok = False
    if p["cota"] != AUTORIDAD["cota"]["U_global_hi"] or not banda_ok or p["regla"] != REGLA:
        return False, "COTA_BANDA_O_REGLA_DISTINTA"
    cumple, _ = desigualdad_c5b(v)
    if not cumple:
        return False, "V_NO_SUPERA_U_GLOBAL_MAS_BANDA"
    return True, "outside_support"


def procedencia_fila(anterior):
    P = AUTORIDAD["prueba_c5b"]
    return {"base_vista_sha256": AUTORIDAD["base_vista"]["sha256"], "base_vista_inventario_sha256": AUTORIDAD["base_vista"]["inventario"]["sha256"],
            "ledger_sha256": AUTORIDAD["ledger"]["sha256"], "aceptacion_sha256": AUTORIDAD["aceptacion"]["sha256"],
            "dictamen_sha256": AUTORIDAD["dictamen"]["sha256"], "nota_cota_sha256": AUTORIDAD["nota_cota"]["sha256"],
            "prueba_c5b": {"inventario_sha256": P["inventario"]["sha256"], "certificado_sha256": P["certificado"]["sha256"],
                           "salida_m2_sha256": P["salida_m2"]["sha256"], "script_certificado_sha256": P["script_certificado"]["sha256"],
                           "script_m2_sha256": P["script_m2"]["sha256"],
                           "rol": "prueba aceptada por la aceptación técnica rem145; el certificado conserva su nombre histórico CANDIDATO"},
            "certificacion_fila_sha256": AUTORIDAD["certificacion"]["certificacion_fila_sha256"],
            "fuentes_captura_sha256": AUTORIDAD["certificacion"]["fuentes_sha256"], "finalizador_sha256": AUTORIDAD["finalizador"]["sha256"],
            "plan_sha256": AUTORIDAD["plan_sha256"], "captura_c2_anterior_sha256": H(canon(anterior)), "procedencia_anterior": anterior.get("procedencia")}


def captura_nueva(carga, i, f, linea):
    """captura_c2 de una de las cinco filas desde la fila base f (y su línea) y las fuentes autenticadas; cualquier incoherencia es un rechazo."""
    x = FILA_C5B.get(i)
    need(x is not None and i in carga["certificado"] and i in carga["aceptacion"], "FILA_FUERA_DE_LA_ACEPTACION:%s" % i)
    old = f.get("captura_c2") or {}
    need(f.get("tipo") == TIPO_CAPTURA and f.get("fila_anexo") == i and old.get("estado_candidato") == "pendiente"
         and old.get("causa_pendiente") == "SIN_PRUEBA_POR_FILA" and old.get("prueba_sha256") is None, "FILA_BASE_NO_PENDIENTE:%d" % i)
    need(f.get("clave_fila") == x["clave_fila"], "CLAVE_DE_FILA_DISTINTA:%d" % i)
    need(f.get("run_id") == x["run_destino"], "CORRIDA_DESTINO_DISTINTA:%d" % i)
    p = prueba_c5b(carga, i, f)
    ok, motivo = validar_c5b(carga["ctx"], carga["CF"], p, f, linea)
    need(ok, "%s:%d" % (motivo, i))
    v = f["historico"]["fin_por_unidad"]["value"]
    _, det = desigualdad_c5b(v)
    lo, hi = float("-inf"), Fraction(AUTORIDAD["cota"]["U_global_hi"]) + Fraction(AUTORIDAD["cota"]["banda"])
    salida = {}
    carga["finalizar"](salida, f["historico"]["fin_por_unidad"], {}, (lo, hi))         # encierro exterior SOLO tras la exclusión demostrada
    need(salida.get("result_status") == "outside_support", "ADAPTADOR_DISCREPA_DEL_FINALIZADOR:%d" % i)
    return {"estado_candidato": "outside_support", "clasificacion_derivada": "outside_support", "finalizacion_candidata": True, "causa_pendiente": None,
            "tipo_prueba": TIPO_PRUEBA, "prueba_sha256": H(canon(p)), "cambio": f["estado_historico"] != "outside_support",
            "adaptador": {"finalizador_sha256": AUTORIDAD["finalizador"]["sha256"], "c2": [str(lo), str(hi)], "semantica": SEMANTICA,
                          "salida": salida, "regla": REGLA},
            "desigualdad": det, "prueba": p, "procedencia": procedencia_fila(old)}


def construir_vista(carga, me):
    """Líneas de la vista candidata: bytes de la base salvo las cinco, donde solo cambia captura_c2."""
    out = []
    for i, (b, f) in enumerate(zip(carga["base"], carga["bfilas"])):
        if i not in FILA_C5B:
            out.append(b)
            continue
        g = dict(f)
        g["captura_c2"] = captura_nueva(carga, i, f, b)
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
            "actualizadas_por_c5b": sorted(f["fila_anexo"] for f in filas if f.get("tipo") == TIPO_CAPTURA and f["captura_c2"]["tipo_prueba"] == TIPO_PRUEBA),
            "testigo_alto_preservadas": sorted(f["fila_anexo"] for f in filas if f.get("tipo") == TIPO_CAPTURA
                                               and f["captura_c2"]["tipo_prueba"] == "pertenencia_testigo_alto"),
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
    por_clave = {k: (i, f) for i, (k, f) in enumerate(zip(bclaves, bfilas))}
    cat = {k: [] for k in ("FILA_FUERA_DEL_DIFERENCIAL_REESCRITA", "IDENTIDAD_O_INSUMOS_REESCRITOS", "FILA_DISTINTA_DEL_RECALCULO",
                           "PROCEDENCIA_DE_FILA_DISTINTA", "FILA_NO_CANONICA", "EXCLUSION_C5B_NO_DEMOSTRADA")}
    for j, (x, f) in enumerate(zip(ls, filas)):
        k = f.get("clave_fila")
        if k not in por_clave:
            continue
        i, g = por_clave[k]
        if i not in FILA_C5B:
            if x != base[i]:
                cat["FILA_FUERA_DEL_DIFERENCIAL_REESCRITA"].append(i)
            continue
        if canon(_sin_c2(f)) != canon(_sin_c2(g)):
            cat["IDENTIDAD_O_INSUMOS_REESCRITOS"].append(i)
        c = f.get("captura_c2") if isinstance(f.get("captura_c2"), dict) else {}
        ok, motivo = validar_c5b(carga["ctx"], carga["CF"], c.get("prueba"), f, base[i])
        if not ok:
            cat["EXCLUSION_C5B_NO_DEMOSTRADA"].append("%d:%s" % (i, motivo))
        if canon(c.get("procedencia")) != canon(procedencia_fila(g["captura_c2"])):
            cat["PROCEDENCIA_DE_FILA_DISTINTA"].append(i)
        try:
            esp = captura_nueva(carga, i, g, base[i])
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
    # identidad de los conjuntos (no solo totales): cada estado de la vista = el de la base salvo exactamente las cinco
    rb = {f["fila_anexo"]: f["captura_c2"]["estado_candidato"] for f in bfilas if f.get("tipo") == TIPO_CAPTURA}
    rv = {f.get("fila_anexo"): (f.get("captura_c2") or {}).get("estado_candidato") for f in filas if f.get("tipo") == TIPO_CAPTURA}
    cambiadas = sorted(i for i in set(rb) | set(rv) if rb.get(i) != rv.get(i))
    if cambiadas != INDICES_C5B:
        fallos.append("IDENTIDAD_DE_LAS_ACTUALIZADAS_DISTINTA:%d" % len(set(cambiadas) ^ set(INDICES_C5B)))
    if any(e == "pendiente" for e in rv.values()):
        fallos.append("IDENTIDAD_DE_LAS_PENDIENTES_DISTINTA")
    if rs["corridas"] != sorted(AUTORIDAD["corridas"]) or len(rs["corridas"]) != 14:
        fallos.append("CORRIDAS_DISTINTAS")
    return fallos, rs


def materializar(R, me_raw, me, out, contexto, carga=None):
    """Etapa 1 (la llama materializar_t8_c5b.py): construye, somete a validar_contenido ANTES de escribir y escribe en un directorio NUEVO
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
           "producto": PRODUCTO, "producto_sha256": sha, "resumen": rs, "fuentes": fuentes_del_resumen(), "prueba": carga["prueba"],
           "nota": "vista de captura T8 con la exclusión C5B aceptada: solo cinco filas cambian su captura_c2 (outside_support por "
                   "exclusion_cota_U_global); no finaliza estados reales fuera de una emisión productiva aceptada; el estado formal sigue en "
                   "13.651 + 5 hasta entonces"}
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
                                "procedencia": {"cotejados": list(COMPARTIDOS + DERIVADOS_DEL_MODO + DUPLICADOS_DEL_RESUMEN) + ["fuentes"],
                                                "contexto": {k: contexto[k] for k in COMPARTIDOS}}}
