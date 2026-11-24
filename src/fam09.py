"""FAM09 (tabla T8: 13.656 filas; filas históricas preservadas, emisión λ, captura por fila, testigo alto y cota C5B).

Operaciones del catálogo, en el orden de sus dependencias (no se confunden):
- F09-HIST (integridad): las 9.434 filas definitivas del anexo T8 (rem108, estado_es_por_unidad = false) se recuperan del insumo previo con
  su clave estable y sus campos, y se comprueba su integridad (huella del anexo y de su inventario, claves únicas, banderas históricas). No se
  vuelven a correr las 14 corridas históricas.
- F09-LAMBDA (regeneración, rem138): materializar_lambda.py y verificar_producto_lambda.py del paquete de emisión λ (rem136) sobre la entrada
  autenticada rem134: 2.111 filas λ finalizadas (2.042 outside_support, 69 computed, 68 cambios); 11.545 definitivas y 2.111 de captura
  pendientes.
- F09-CAPTURA (regeneración, rem140): materializar_captura.py y verificar_captura.py (candidato_v3, rem137) sobre el producto λ NUEVO: de las
  2.111 seleccionadas, 2.071 se resuelven (928 computed: 365 misma corrida, 563 transferidas; 1.143 outside_support: 264 por 33/10, 879 por U)
  y 40 quedan pendientes (SIN_PRUEBA_POR_FILA), cada una con su prueba y su procedencia.
- F09-TESTIGO: (a) CÁLCULO del techo alto e8b1f7fd… (grupo EQ-TECHO-T8-1) con el trabajador auténtico trabajador_testigo.py, el núcleo
  histórico lima1855 y la configuración de su manifiesto v2, una vez, un proceso, límite externo 600 s (supervisor); (b) VALIDACIÓN U36 con
  validar_testigo.py (69989e41…, sin cambios) sobre los bytes NUEVOS; (c) EMISIÓN: incorporación (construir_incorporacion.py), lector de la
  fuente nueva (lector_fuente_testigo.py), cobertura exacta independiente y materializar_t8_testigo.py / verificar_t8_testigo.py: las mismas
  35 filas cubiertas y las mismas 5 pendientes. El techo se calcula aparte de la emisión de las 35 filas.
- F09-C5B (regeneración, rem145/rem147): materializar_t8_c5b.py y verificar_t8_c5b.py sobre la vista del testigo NUEVA: el certificado C5B
  (fc403d40…) y la regla racional estricta Fraction(v) > U_global_hi + banda (la igualdad no excluye) se REUTILIZAN; su derivación (guiones
  C3/M2 de rem144) no se regenera. Las otras 13.651 filas se conservan byte a byte; la vista final se compara con rem147 (12826a05…).

Adaptaciones (no cambian fórmulas, claves, tolerancias, presupuestos, garantías ni criterios; cada original se sustituye una sola vez):
- GUION-v1 / MODULOS-v1: cada guion se ejecuta desde sus bytes exactos con las sustituciones de SUSTITUCIONES; los módulos que los guiones
  importan por nombre (validar_emision_lambda, conexion_captura, testigo_comun, adaptador_fila_testigo, lector_fuente_testigo, conexion_testigo,
  conexion_c5b) se cargan antes desde su texto adaptado. Los módulos que el código carga por ruta y huella (entrada λ, finalizador unidades.py,
  certificacion_fila, lector) pasan por _MODULO9 (misma huella, texto adaptado si lo tiene).
- RAIZ-T8-v1: la raíz es nucleo_s6/t8 (espejo de las rutas tmp/<área>/<rel>); paso4/instalacion -> nucleo_s6/instalacion (FAM01: finalizador
  a8aded1d… y paper2b de la instalación), fase2_datos -> nucleo_s6/raiz/fase2_datos (D7 10a0bd5b…, FAM01), salidas/ y datos/ -> la base.
- NUCLEO-C0-v1 (de FAM05): la identidad del C0 (d0bf5cd6…) es la de nucleo_s6/c0; no se importa el aprobacion_alcance histórico.
- SANEADO-v1: una proyección (rutas privadas por marcadores) cuenta con la huella de su ORIGINAL (correspondencia de fuentes_fam09.json); los
  marcadores de W de conexion_testigo / conexion_c5b se escriben como en sus manifiestos proyectados.
- PAQUETE-v1: cada paquete comprueba solo las piezas copiadas (recetas .sh, emisores de alcance, admisión y manifiestos de ENSAYO no se copian).
- MODO-CANDIDATA-v1: λ, captura, emisión del testigo y C5B corren en modo candidata (sin alcance ni decisión): su producto es el mismo; solo el
  resumen dice CANDIDATA.
- PUERTA-v1: la puerta de producción del testigo (alcance v3 verificado y decisión humana nativa) no se ejecuta ni se reconstruye; la declaración
  NO OFICIAL datos/fam09/ejecucion_limpia.json fija antes de calcular las entradas esperadas, asignaciones y límites, y ocupa el alcance; nunca
  hay decisión (el lector y el constructor exigen su ausencia).
- AUTORIDAD-EXTRAIDA-v1: los actos de autoridad históricos (notas rem135/rem137, dictamen rem137, despliegue y acta P3, dictamen y nota rem145)
  no se copian: su huella se autenticó en la extracción y se coteja con la registrada; de la aceptación técnica C5B rem145 se usa su RESUMEN sin
  rutas (datos/fam09/autoridad), ligado a la huella del original.
- PROCEDENCIA-LOCAL-v1: la entrega del testigo es la carpeta local de fam09-etapa (inventario audit/entrega.json escrito por fam09-validar); el
  «dictamen» que cita la incorporación es el REGISTRO de fam09-validar (inventario y RESULTADO citados por huella), no un dictamen de Codex.
- ENLACE-v1: una salida nueva sustituye a su homóloga histórica SOLO si tiene la misma huella fijada (λ 1b4881c3… -> captura; captura 66891b45…
  -> lector y emisión del testigo): el inventario histórico sigue autenticando el pin y los bytes salen de la salida nueva.
- ENLACE-TESTIGO-v1 / ENLACE-C5B-v1: la autoridad de conexion_testigo / conexion_c5b se enlaza a las salidas NUEVAS validadas (incorporación,
  aceptación técnica local por cobertura exacta, registro de validación, evidencia del lector y techo superior nuevo; vista del testigo nueva y su
  registro), declarado en ENLACE_*.json; el manifiesto histórico indexado se sigue cotejando con la autoridad histórica y el certificado C5B se
  liga por las cinco líneas idénticas (linea_vista_sha256).
"""
from __future__ import annotations

import builtins
import contextlib
import datetime as dt
import importlib.util
import io
import json
import sys
import time
import traceback
import types
from collections import Counter
from fractions import Fraction
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def _src(nombre: str):
    if nombre not in sys.modules:
        sp = importlib.util.spec_from_file_location(nombre, BASE / "src" / (nombre + ".py"))
        m = importlib.util.module_from_spec(sp)
        sys.modules[nombre] = m
        sp.loader.exec_module(m)
    return sys.modules[nombre]


F5 = _src("fam05")
sha, sha_archivo, leer, leer_jsonl, rel, F1 = F5.sha, F5.sha_archivo, F5.leer, F5.leer_jsonl, F5.rel, F5.F1
T9 = "nucleo_s6/t8"
R9 = BASE / T9
DATOS = BASE / "datos" / "fam09"
REF = BASE / "referencias" / "fam09"
A108 = "paso4_conciliacion_portabilidad_desde_rem108"
A136 = "paso4_procedencia_cota_desde_rem136"
A137 = "paso4_emision_lambda_conexion_captura_desde_rem137"
A139 = "paso4_emision_captura_correcciones_testigo_desde_rem139"
A140 = "paso4_estado_testigo_lector_desde_rem140"
A142 = "paso4_incorporacion_testigo_desde_rem142"
A145 = "paso4_conexion_cinco_filas_t8_desde_rem145"
LAMBDA = "tmp/%s/lote_emision_lambda" % A136
CAPTURA = "tmp/%s/c2_conexion/candidato_v3" % A137
TESTIGO = "tmp/%s/testigo_alto_v3" % A140
CONEXION_T = "tmp/%s/conexion_testigo/paquete" % A142
CONEXION_C = "tmp/%s/conexion_c5b/paquete" % A145


def _c(d: str, n: str) -> str:
    return "%s/%s/%s" % (T9, d, n)


# código ejecutado o cargado por nombre: archivo de la base -> sha256 del ORIGINAL (las proyecciones se autentican por su original)
CODIGO = {_c(LAMBDA, "validar_emision_lambda.py"): "4fd9d680247c6d9d464698e78c545580f357623a3c0ee88ada69f875682cffdb",
          _c(LAMBDA, "materializar_lambda.py"): "6beb73b45fa49d7acbd35ddfd857dd9c80fa65999e53065d3ed1af623b43d5e9",
          _c(LAMBDA, "verificar_producto_lambda.py"): "ef459e8d5fe0c8697a10aa5879ef3e0a3e4d129d6638cf4a396de8ce6ab27ef5",
          _c(CAPTURA, "conexion_captura.py"): "f7a8d23f5d2558843f4620052b49d20250cf23c67ac8a02d54ea57db1c05dba7",
          _c(CAPTURA, "certificacion_fila.py"): "4741b4ea3b72fc2f754cc2d8c79dd9dd718f8e37205bf3e4ee5c0c539be60f4b",
          _c(CAPTURA, "materializar_captura.py"): "8ef790ffccbc4b8875f29f986fcca36c8d184ef7b1d6066fe696387236786263",
          _c(CAPTURA, "verificar_captura.py"): "18d6872a13527aa590406db33d9e6e901fb8e9596b301d1a60f09d14051c6860",
          _c(TESTIGO, "testigo_comun.py"): "3f8ec27b92c9e04c6d1b5e688f38fe3663440c1e3aa54a9fd9392e6617f28b52",
          _c(TESTIGO, "trabajador_testigo.py"): "fefa171c21f74248860a7ac984d562d21ee74a0f7b5d47a3058c40554a4741fa",
          _c(TESTIGO, "validar_testigo.py"): "69989e41136706f995d4e24b33fbde0c8e63d98440b61d7cdc9b5b7fe5fb80fe",
          _c(TESTIGO, "adaptador_fila_testigo.py"): "7cbebc7691c68d7d902d4c0944f30f8b3b4a1844c409a9f089f88fd7da60b0e2",
          _c(TESTIGO, "construir_incorporacion.py"): "bfa2d5ba3f41b4f8aa4ade3c4243c4d045388a008e24e3b7f5fff8262fe4d775",
          _c(TESTIGO, "lector_fuente_testigo.py"): "9e25706026743e1b92221029f0e30faaf3c64df703f8c07451848b9696ad7d7a",
          _c(CONEXION_T, "conexion_testigo.py"): "a292a929d1e74178726777d32e103b3897d1e39ad01b7b3ffab324c5c904657c",
          _c(CONEXION_T, "materializar_t8_testigo.py"): "c6f0db6b86dd001785dbb6ac0334a46d1903daae76b1304aa38e7cc25bb5361d",
          _c(CONEXION_T, "verificar_t8_testigo.py"): "3e20c16b6e5b50aeed542a9e0c9c09926c45cdecc81b6d2d3e80334a675cbb97",
          _c(CONEXION_C, "conexion_c5b.py"): "006ec4fa2a4f5d1d7b60c09f9a226f6b83282cd1b9640dc8cacadaca6ecfb461",
          _c(CONEXION_C, "materializar_t8_c5b.py"): "df22d8903e5e7c90547d4e924402892b374550de1df64f6e3e96a9b9c1908d75",
          _c(CONEXION_C, "verificar_t8_c5b.py"): "8e78b261ce4b534ab899d365ca22549451e912a182086928f15f8dad8976220d"}
MAN = {"LAMBDA": (_c(LAMBDA, "MANIFIESTO_EMISION_LAMBDA.json"), "e6207fa8ec6a9402c2b86d67ea0d91a7b2eff9c010e2f34139e00a3f44875474"),
       "CAPTURA": (_c(CAPTURA, "MANIFIESTO_CAPTURA.json"), "952c6512db0bcf81cca0c53a15342f444262405cb66cfad8f85a5c898d77aba7"),
       "TESTIGO": ("%s/tmp/%s/testigo_alto_corregido/MANIFIESTO_TESTIGO_v2.json" % (T9, A139), "3ed91d323c7f0f0e56eb31b01b41ef864c68bea029936afd4d090f36c9939ad4"),
       "INCORPORACION": (_c(CONEXION_T, "MANIFIESTO_T8_TESTIGO.json"), "c07f0c3e4cc11fe803c3f09908ea08a451e66eeccda7bc7e022d01a738c2e9a2"),
       "C5B": (_c(CONEXION_C, "MANIFIESTO_T8_C5B.json"), "dc34c455608490c2fa065e13e5bfd7d9f752613863359f55160a26b604395623")}
ANEXO = ("%s/tmp/%s/conciliacion/ensamblajes/T8_anexo.json" % (T9, A108), "e63ae329777ca04342a2d86c439b70008e52965adf801b23b3339bd657074bc9",
         "%s/tmp/%s/audit/entrega.json" % (T9, A108), "b6ccab3ded6e957df5ebfd585a5402b5a10948aaa3e0bfa52192165fb6022cf4", "conciliacion/ensamblajes/T8_anexo.json")
# huellas aceptadas (libros; solo para comparar) y pines históricos que enlazan una salida nueva con la etapa siguiente (ENLACE-v1)
ACEPTADO = {"LAMBDA": "1b4881c3211263909e5aafedef7b5a56b2147143853c43a1e38e12dd772e6996",
            "CAPTURA": "66891b45282cae1c08c0a86131d194631e1d9a39351e26cfc137255e6b489992",
            "INCORPORACION": "ec6e3929dd6be8dbb56b17493ce51061b95dde7991722832045a1c4411c8fd93",
            "C5B": "12826a0518b4a7479f135d47b4e387cf73e43d73744d576e53b375f969a199a2",
            "TESTIGO": "981ff0f2121bde1841e3bccfc76f53a3f21d2e60ba95b14ef3b08f0bd812b457"}
PIN_LAMBDA = "tmp/%s/lambda_producto_CANDIDATA_REAL/PRODUCTO_T8_LAMBDA.jsonl" % A136
PIN_CAPTURA = "tmp/%s/captura_vista_CAPTURA_T8/VISTA_T8_CAPTURA.jsonl" % A139
PRODUCTO = {"LAMBDA": "PRODUCTO_T8_LAMBDA.jsonl", "CAPTURA": "VISTA_T8_CAPTURA.jsonl", "INCORPORACION": "VISTA_T8_CAPTURA.jsonl", "C5B": "VISTA_T8_CAPTURA.jsonl"}
GUIONES = {"LAMBDA": (_c(LAMBDA, "materializar_lambda.py"), _c(LAMBDA, "verificar_producto_lambda.py")),
           "CAPTURA": (_c(CAPTURA, "materializar_captura.py"), _c(CAPTURA, "verificar_captura.py")),
           "INCORPORACION": (_c(CONEXION_T, "materializar_t8_testigo.py"), _c(CONEXION_T, "verificar_t8_testigo.py")),
           "C5B": (_c(CONEXION_C, "materializar_t8_c5b.py"), _c(CONEXION_C, "verificar_t8_c5b.py"))}
MODULOS = {"LAMBDA": (("validar_emision_lambda", _c(LAMBDA, "validar_emision_lambda.py")),),
           "CAPTURA": (("conexion_captura", _c(CAPTURA, "conexion_captura.py")),),
           "TESTIGO": (("testigo_comun", _c(TESTIGO, "testigo_comun.py")),),
           "LECTOR": (("testigo_comun", _c(TESTIGO, "testigo_comun.py")), ("adaptador_fila_testigo", _c(TESTIGO, "adaptador_fila_testigo.py")),
                      ("lector_fuente_testigo", _c(TESTIGO, "lector_fuente_testigo.py"))),
           "INCORPORACION": (("conexion_testigo", _c(CONEXION_T, "conexion_testigo.py")),),
           "C5B": (("conexion_c5b", _c(CONEXION_C, "conexion_c5b.py")),)}
ETAPAS = ("HIST", "LAMBDA", "CAPTURA", "TESTIGO", "INCORPORACION", "C5B")
OPERACION_DE = {"HIST": "F09-HIST", "LAMBDA": "F09-LAMBDA", "CAPTURA": "F09-CAPTURA", "TESTIGO": "F09-TESTIGO", "INCORPORACION": "F09-TESTIGO",
                "C5B": "F09-C5B"}
# entradas por etapa: clave -> (etapa productora, ¿exige registro de fam09-validar aceptado?)
ENTRADAS_DE = {"CAPTURA": {"lambda": "LAMBDA"}, "INCORPORACION": {"captura": "CAPTURA", "testigo": "TESTIGO"}, "C5B": {"testigo_vista": "INCORPORACION"}}
OPERACIONES = {"F09-HIST": "integridad de las 9.434 filas definitivas del anexo T8 (rem108); sin recálculo de las 14 corridas",
               "F09-LAMBDA": "regeneración rem138: 2.111 filas λ (2.042 outside_support, 69 computed); 11.545 definitivas + 2.111 de captura",
               "F09-CAPTURA": "regeneración rem140 sobre el λ nuevo: 2.071 resueltas (928 computed, 1.143 outside_support) y 40 pendientes",
               "F09-TESTIGO": "piloto numérico rem141 (techo alto e8b1f7fd…, 600 s, un proceso) con validación U36 y emisión rem144 de 35 filas",
               "F09-C5B": "regeneración rem147 sobre la vista del testigo nueva: 5 filas por U_global_hi + banda (estricta); 13.651 conservadas"}
DECLARACION = "ejecucion_limpia.json"
DECL_KIND = "declaracion-ejecucion-limpia-fam09"
ETIQUETA = "REPRODUCCION LIMPIA FAM09 NO OFICIAL"
EMITIDA = "2026-11-18T00:00:00+00:00"
SALIDA_TESTIGO = "testigo_salida_TESTIGO_ALTO"
ETIQUETA_TESTIGO = "TESTIGO_ALTO"
TEXTO_INC = "techo alto e8b1f7fd… (fuente nueva: reproducción limpia FAM09, no oficial)"
KIND_ACEPTACION = "aceptacion-local-cobertura-exacta-testigo-fam09-no-oficial"
KIND_LEDGER = "registro-validacion-vista-t8-testigo-fam09-no-oficial"
CLAVE_TECHO, GRUPO = "e8b1f7fdb9c7017605e0a4162fc6688e7b6ed01d2308ff72106ed6cf6834a97b", "EQ-TECHO-T8-1"
FILAS_TESTIGO = [6884, 6902, 6926, 7172, 7196, 7244, 7322, 7598, 7682, 7772, 7916, 7958, 7964, 8288, 8378, 8462, 8552, 8606, 8636, 8654,
                 8786, 8876, 8930, 9014, 9020, 9188, 9224, 9260, 9350, 9398, 9458, 9542, 9560, 9680, 9686]
FILAS_C5B = [7028, 7208, 8144, 8186, 9578]
EXTREMO_INFERIOR = "83037518495931418279937/151115727451828646838272"     # CEI:dc4e1ba9… de la fila 9638 (aceptado)
REF_TESTIGO = {"C2": 0.7651580128158672, "tau_d_at_sup": 0.6, "tau_f_at_sup": 0.6}
ESPERADO = {"filas": 13656, "hist": 9434, "lambda": 2111, "captura_resueltas": 2071, "testigo": 35, "c5b": 5,
            "outside_support_historicas": 5580, "outside_support_vigentes": 4549, "diferencia_captura": 963, "diferencia_lambda": 68}
# campos locales del RESULTADO del techo (no científicos): fechas, duración, procedencia del alcance y del ejecutable
LOCALES_RESULTADO = ("inicio_utc", "fin_utc", "pared_s", "puerta.alcance_sha256", "puerta.ejecutado", "evidencia_real.ejecutable")
LOCALES_VALIDACION = ("validada_utc", "resultado_sha256", "puerta_validador")
# campos de vínculo de las filas emitidas (apuntan a la fuente nueva o a la vista nueva); todo lo demás debe ser idéntico a rem147
VINCULOS_TESTIGO = ("captura_c2.procedencia.incorporacion_sha256", "captura_c2.procedencia.aceptacion_sha256", "captura_c2.procedencia.dictamen_sha256",
                    "captura_c2.procedencia.evidencia_filas_sha256", "captura_c2.procedencia.testigo_superior.alcance_origen_sha256",
                    "captura_c2.procedencia.testigo_superior.decision_origen_uuid", "captura_c2.procedencia.testigo_superior.fuente_base",
                    "captura_c2.procedencia.testigo_superior.fuente_inventario_sha256", "captura_c2.procedencia.testigo_superior.resultado_sha256",
                    "captura_c2.procedencia.testigo_superior.run_origen", "captura_c2.prueba.testigo_superior_nuevo.incorporacion_sha256",
                    "captura_c2.prueba.testigo_superior_nuevo.fuente_base", "captura_c2.prueba.testigo_superior_nuevo.fuente_inventario_sha256",
                    "captura_c2.prueba.testigo_superior_nuevo.resultado_sha256", "captura_c2.prueba.testigo_superior_nuevo.validacion_recalculada_sha256",
                    "captura_c2.prueba.testigo_superior_nuevo.run_origen", "captura_c2.prueba_sha256")
VINCULOS_C5B = ("captura_c2.procedencia.base_vista_sha256", "captura_c2.procedencia.base_vista_inventario_sha256", "captura_c2.procedencia.ledger_sha256")
ADAPTACIONES = ("GUION-v1", "MODULOS-v1", "RAIZ-T8-v1", "NUCLEO-C0-v1", "SANEADO-v1", "PAQUETE-v1", "MODO-CANDIDATA-v1", "PUERTA-v1",
                "AUTORIDAD-EXTRAIDA-v1", "PROCEDENCIA-LOCAL-v1", "ENLACE-v1", "ENLACE-TESTIGO-v1", "ENLACE-C5B-v1")


class Fam09Error(RuntimeError):
    pass


def need(t, codigo):
    if not t:
        raise Fam09Error(codigo)


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def canon(o) -> bytes:
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")


_CACHE = {}


def fuentes() -> dict:
    if "fu" not in _CACHE:
        _CACHE["fu"] = leer(BASE / "fuentes_fam09.json")
    return _CACHE["fu"]


def original() -> dict:
    """SANEADO-v1: huella de una proyección -> huella de su original (fuentes_fam09.json)."""
    return {x["sha256"]: x["sha256_original"] for x in fuentes()["saneado"] if x.get("restituye_el_original") is True}


# ================================================================================================ ayudas inyectadas en el código histórico
ENTRADAS9: dict = {}          # ENLACE-v1: ruta histórica bajo la raíz T8 -> archivo NUEVO de la base (mismo pin)
ENLACE9: dict = {"autoridad": {}, "kind_aceptacion": None, "kind_ledger": None}
PREFIJOS9 = (("paso4/instalacion", "nucleo_s6/instalacion"), ("fase2_datos", "nucleo_s6/raiz/fase2_datos"), ("salidas", "salidas"), ("datos", "datos"))


def ruta9(R, r) -> Path:
    """RAIZ-T8-v1 / ENLACE-v1: ruta relativa histórica -> archivo de la base."""
    r = str(r).replace("\\", "/")
    if r in ENTRADAS9:
        return BASE / ENTRADAS9[r]
    for pre, dst in PREFIJOS9:
        if r == pre or r.startswith(pre + "/"):
            return BASE / (dst + r[len(pre):])
    return Path(R) / r


def sha9(b: bytes) -> str:
    h = sha(b)
    return original().get(h, h)


def autoridad9(ruta) -> str:
    """AUTORIDAD-EXTRAIDA-v1: huella registrada en la extracción de un acto de autoridad no copiado (por ruta relativa o, en los libros de W,
    por nombre). Nunca lee el original."""
    r = str(ruta).replace("\\", "/")
    for x in fuentes()["solo_procedencia"].values():
        o = x["origen"]
        if r == o or (o.startswith("<directorio de los libros>/") and r.startswith("@@W_") and r.rsplit("/", 1)[-1] == o.rsplit("/", 1)[-1]):
            return x["sha256"]
    raise Fam09Error("AUTORIDAD_NO_EXTRAIDA: %s" % r[-90:])


def aceptacion_c5b9(h: str) -> dict:
    d = leer(BASE / "datos/fam09/autoridad/ACEPTACION_C5B_REM145.resumen.json")
    need(d.get("kind") == "resumen-aceptacion-tecnica-c5b-rem145" and d.get("original_sha256") == h
         and h == fuentes()["solo_procedencia"]["aceptacion_rem145"]["sha256"], "RESUMEN_DE_ACEPTACION_C5B_AJENO")
    return d["campos"]


def modulo9(nombre: str, ruta, h: str):
    p = Path(ruta).resolve()
    need(sha9(p.read_bytes()) == h, "PIEZA_NO_AUTENTICA:%s" % nombre)
    return modulo(nombre, p.relative_to(BASE.resolve()).as_posix())


def enlazar9(A: dict) -> dict:
    out = json.loads(json.dumps(A))
    for k, v in (ENLACE9.get("autoridad") or {}).items():
        need(k in out, "ENLACE_DE_CLAVE_AJENA:%s" % k)
        out[k] = json.loads(json.dumps(v))
    return out


def copiadas(d: str) -> frozenset:
    return frozenset(Path(x["archivo"]).name for x in fuentes()["archivos"] if Path(x["archivo"]).parent.as_posix() == d)


def _ayudas(n: str) -> dict:
    return {"_RUTA9": ruta9, "_SHA9": sha9, "_AUTORIDAD9": autoridad9, "_MODULO9": modulo9, "_C0_9": F5.modulo_identidad,
            "_COPIADAS9": copiadas(Path(n).parent.as_posix()), "_ENLACE9": ENLACE9, "_ENLAZAR9": enlazar9, "_LOCAL9": lambda p: rel(Path(p)),
            "_ACEPTACION_C5B9": aceptacion_c5b9, "_DECLARACION9": {"kind": DECL_KIND, "etiqueta": ETIQUETA}}


# ================================================================================================ sustituciones
_C0_ORIG = ('    sys.path.insert(0, str(C0 / "herramientas/b"))\n    import aprobacion_alcance as AA\n    if AA.identidad_instalacion(C0) != NUCLEO_IDENTIDAD')
_C0_NUEVO = ('    AA = _C0_9()                                   # FAM09 NUCLEO-C0-v1: identidad del C0 de la base (FAM05, nucleo_s6/c0)\n'
             '    if AA.identidad_instalacion(None) != NUCLEO_IDENTIDAD')
_PAQ_ORIG = '    mal = [n for n in PIEZAS if n not in idx.get("piezas", {}) or not (AQUI / n).is_file() or HF(AQUI / n) != idx["piezas"][n]["sha256"]]\n'
_PAQ_NUEVO = ('    mal = [n for n in PIEZAS if n in _COPIADAS9 and (n not in idx.get("piezas", {}) or not (AQUI / n).is_file()\n'
              '                                                  or HF(AQUI / n) != idx["piezas"][n]["sha256"])]   # FAM09 PAQUETE-v1: piezas copiadas\n')
_PAQ2_ORIG = ('    mal = [n for n in PIEZAS + DATOS if not (AQUI / n).is_file()\n'
              '           or HF(AQUI / n) != (idx["piezas"] if n in PIEZAS else idx["datos"])[n]["sha256"]]\n')
_PAQ2_NUEVO = ('    mal = [n for n in PIEZAS + DATOS if n in _COPIADAS9 and (not (AQUI / n).is_file()        # FAM09 PAQUETE-v1: piezas copiadas\n'
               '           or HF(AQUI / n) != (idx["piezas"] if n in PIEZAS else idx["datos"])[n]["sha256"])]\n')
_H_ORIG = "H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731\n"
_H_NUEVO = "H = lambda b: _SHA9(b)  # noqa: E731   FAM09 SANEADO-v1: una proyección cuenta con la huella de su original\n"
_W_ORIG = 'W = r"@@W_WIN@@"\n'
_W_NUEVO = 'W = "@@W_BS2@@"   # FAM09 SANEADO-v1: el marcador como lo escriben los manifiestos proyectados (la ruta privada no se usa)\n'
_CAMPOS = 'CAMPOS_MANIFIESTO = frozenset(AUTORIDAD) | {"kind", "destinos", "nota", "produccion_habilitada"}\n'
_ENLAZAR = (_CAMPOS + "AUTORIDAD_HISTORICA, AUTORIDAD = AUTORIDAD, _ENLAZAR9(AUTORIDAD)   # FAM09 ENLACE-*: la histórica coteja el manifiesto "
            "indexado; la enlazada (salidas nuevas validadas, ENLACE_*.json) se usa al cargar\n")
_AUT_MAN_ORIG = '    return ["MANIFIESTO_DISTINTO_DE_LA_AUTORIDAD:%s" % k for k, v in AUTORIDAD.items() if canon(me[k]) != canon(v)]\n'
_AUT_MAN_NUEVO = '    return ["MANIFIESTO_DISTINTO_DE_LA_AUTORIDAD:%s" % k for k, v in AUTORIDAD_HISTORICA.items() if canon(me[k]) != canon(v)]\n'
_CARGAR_ORIG = '    need(isinstance(me, dict) and all(canon(me.get(k)) == canon(v) for k, v in AUTORIDAD.items()), "MANIFIESTO_DISTINTO_DE_LA_AUTORIDAD")\n'
_CARGAR_NUEVO = '    need(isinstance(me, dict) and all(canon(me.get(k)) == canon(v) for k, v in AUTORIDAD_HISTORICA.items()), "MANIFIESTO_DISTINTO_DE_LA_AUTORIDAD")\n'
_RUTAS_FIN = ('    rutas_fin = [str(R / p) for p in fin["sys_path"]]\n', '    rutas_fin = [str(_RUTA9(R, p)) for p in fin["sys_path"]]          # FAM09 RAIZ-T8-v1\n')
_SRC_INST = ('    src_inst = (R / fin["sys_path"][0]).resolve()\n', '    src_inst = _RUTA9(R, fin["sys_path"][0]).resolve()\n')


def _fin(nombre: str) -> tuple:
    return ('    for p in fin.get("sys_path", []):\n        if str(R / p) not in sys.path:\n            sys.path.insert(0, str(R / p))\n'
            '    UN = _modulo("%s", R / fin["ruta"], fin["sha256"])\n' % nombre,
            '    for p in fin.get("sys_path", []):                # FAM09 RAIZ-T8-v1: paso4/instalacion -> nucleo_s6/instalacion (FAM01)\n'
            '        if str(_RUTA9(R, p)) not in sys.path:\n            sys.path.insert(0, str(_RUTA9(R, p)))\n'
            '    UN = _modulo("%s", _RUTA9(R, fin["ruta"]), fin["sha256"])\n' % nombre)


_PUERTA_TC = '''def puerta(raiz, modo, alcance, decision, m, manifiesto_sha, rol, script, script_sha):
    """FAM09 PUERTA-v1 (sustituye a la puerta de producción rem140): sin alcance v3 ni decisión humana. El «alcance» es la declaración NO
    OFICIAL datos/fam09/ejecucion_limpia.json, que fija ANTES de calcular las entradas esperadas (entradas_esperadas: manifiesto, clave,
    grupo, núcleo, módulos, controles, puente, piezas y D7), las asignaciones y los límites; nunca hay decisión. Se conservan la asignación
    de rol, la identidad del C0 (FAM05), la autoridad P3 (huellas extraídas) y los bytes ejecutados."""
    raiz, script = Path(raiz), Path(script).resolve()
    need(modo == "produccion", "MODO_INVALIDO", modo)
    need(rol in ROL_TAREA, "ROL_INVALIDO", rol)
    need(decision is None, "DECISION_EN_EJECUCION_LIMPIA")
    need(alcance is not None, "ALCANCE_AUSENTE")
    raw = Path(alcance).read_bytes()
    al = json.loads(raw)
    need(al.get("kind") == _DECLARACION9["kind"] and al.get("oficial") is False and al.get("etiqueta") == _DECLARACION9["etiqueta"]
         and al.get("decision") is None, "DECLARACION_AJENA")
    t = al.get("testigo") or {}
    need(al.get("operaciones") == [OPERACION] and t.get("tareas") == TAREAS, "ALCANCE_DE_OTRA_OPERACION", str(al.get("operaciones")))
    ent = t.get("entradas") or {}
    need(ent.get("manifiesto_testigo") == manifiesto_sha, "MANIFIESTO_AJENO")
    piezas = ent.get("piezas")
    need(isinstance(piezas, dict) and tuple(sorted(piezas)) == tuple(sorted(PIEZAS)), "PIEZAS_AUSENTES_O_INCOMPLETAS", str(sorted(piezas or {})))
    need(all(isinstance(h, str) and len(h) == 64 and all(c in "0123456789abcdef" for c in h) for h in piezas.values()), "HUELLA_NO_COMPLETA")
    esperadas = entradas_esperadas(m, manifiesto_sha, piezas)
    need(ent == esperadas, "ENTRADAS_DISTINTAS", ",".join(sorted(k for k in set(ent) | set(esperadas) if ent.get(k) != esperadas.get(k))))
    need(t.get("asignaciones") == json.loads(json.dumps(ASIGNACIONES)) and t.get("limites") == LIMITES and t.get("instalacion_identidad") == C0_ID,
         "ALCANCE_DISTINTO_DEL_ESPERADO", "asignaciones/limites/instalacion")
    need(isinstance(al.get("emitida_utc"), str), "ALCANCE_DISTINTO_DEL_ESPERADO", "emitida_utc")
    for rel, h in AUTORIDAD.items():
        need(_AUTORIDAD9(rel) == h, "AUTORIDAD_AJENA", rel)
    need(_C0_9().identidad_instalacion(None) == C0_ID, "C0_IDENTIDAD")
    asig = t["asignaciones"][ROL_TAREA[rol]]
    need(script.parent == AQUI and script.name == asig.get(rol), "ASIGNACION_INCOMPATIBLE", "%s como %s" % (script.name, rol))
    need(asig.get("procesos") == 1 and asig.get("tope_s") == 600.0, "ASIGNACION_INCOMPATIBLE", "procesos/tope")
    ejecutado = {"testigo_comun.py": PROPIO, script.name: script_sha}
    for n in PIEZAS:
        ejecutado.setdefault(n, HF(AQUI / n))
    need(HF(AQUI / "testigo_comun.py") == PROPIO and HF(script) == script_sha, "CODIGO_CAMBIADO_DURANTE_LA_EJECUCION")
    distintas = sorted(n for n, h in ejecutado.items() if piezas.get(n) != h)
    need(not distintas, "CODIGO_DISTINTO_DEL_ALCANCE", ",".join(distintas))
    return {"modo": modo, "alcance_sha256": sha(raw), "fixture": False, "decision": None, "rol": rol, "ejecutado": ejecutado, "piezas_alcance": piezas}
'''

SUSTITUCIONES = {
    _c(LAMBDA, "validar_emision_lambda.py"): (
        ("NUCLEO-C0-v1", _C0_ORIG, _C0_NUEVO),
        ("PAQUETE-v1", _PAQ_ORIG, _PAQ_NUEVO),
        ("RAIZ-T8-v1", *_fin("unidades_finalizador_emision"))),
    _c(CAPTURA, "conexion_captura.py"): (
        ("SANEADO-v1", _H_ORIG, _H_NUEVO),
        ("NUCLEO-C0-v1", _C0_ORIG, _C0_NUEVO),
        ("PAQUETE-v1", _PAQ_ORIG, _PAQ_NUEVO),
        ("ENLACE-v1", '    b = (R / "tmp" / x["area"] / x["rel"]).read_bytes()\n',
         '    b = _RUTA9(R, "tmp/%s/%s" % (x["area"], x["rel"])).read_bytes()   # FAM09 ENLACE-v1: salida nueva con el mismo pin\n'),
        ("RAIZ-T8-v1", *_fin("unidades_finalizador_captura")),
        ("MODULOS-v1", '    CF = _modulo("certificacion_fila_v3_captura", ', '    CF = _MODULO9("certificacion_fila_v3_captura", ')),
    _c(CAPTURA, "certificacion_fila.py"): (
        ("SANEADO-v1", _H_ORIG, _H_NUEVO),
        ("AUTORIDAD-EXTRAIDA-v1 (nota rem135)", 'H(Path(F["nota"]["ruta"]).read_bytes())', '_AUTORIDAD9(F["nota"]["ruta"])'),
        ("AUTORIDAD-EXTRAIDA-v1 (nota U rem137)", 'H(Path(F["nota_U"]["ruta"]).read_bytes())', '_AUTORIDAD9(F["nota_U"]["ruta"])'),
        ("AUTORIDAD-EXTRAIDA-v1 (dictamen rem137)", 'H(Path(F["dictamen_rem137"]["ruta"]).read_bytes())', '_AUTORIDAD9(F["dictamen_rem137"]["ruta"])'),
        ("RAIZ-T8-v1 (modelo)", 'H((self.R / F["modelo"]["ruta"]).read_bytes())', 'H(_RUTA9(self.R, F["modelo"]["ruta"]).read_bytes())'),
        ("RAIZ-T8-v1 (D7)", '            b = (self.R / x["ruta"]).read_bytes()\n',
         '            b = _RUTA9(self.R, x["ruta"]).read_bytes()          # FAM09 RAIZ-T8-v1: D7 10a0bd5b… de la base\n')),
    _c(TESTIGO, "testigo_comun.py"): (
        ("SANEADO-v1", "sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731\n",
         "sha = lambda b: _SHA9(b)  # noqa: E731   FAM09 SANEADO-v1: una proyección cuenta con la huella de su original\n"),
        ("PUERTA-v1 (piezas)", 'PIEZAS = ("testigo_comun.py", "trabajador_testigo.py", "validar_testigo.py", "receta_testigo.sh", "emitir_alcance_testigo.py")\n',
         'PIEZAS = ("testigo_comun.py", "trabajador_testigo.py", "validar_testigo.py")   # FAM09 PUERTA-v1: sin receta .sh ni emisor de alcance\n'),
        ("PUERTA-v1", ("def puerta(raiz, modo, alcance, decision, m, manifiesto_sha, rol, script, script_sha):\n",
                       '        need(decision is None, "DECISION_EN_FIXTURE")\n    return ev\n'), _PUERTA_TC),
        ("AUTORIDAD-EXTRAIDA-v1 (P3)", '        need(HF(raiz / rel) == h, "AUTORIDAD_AJENA", rel)\n',
         '        need(_AUTORIDAD9(rel) == h, "AUTORIDAD_AJENA", rel)          # FAM09 AUTORIDAD-EXTRAIDA-v1 (despliegue y acta P3)\n'),
        ("RAIZ-T8-v1 (D7, manifiesto)", '    d7 = raiz / m["d7"]["ruta"]\n', '    d7 = _RUTA9(raiz, m["d7"]["ruta"])                  # FAM09 RAIZ-T8-v1\n'),
        ("RAIZ-T8-v1 (D7, valores)", '    d7 = Path(raiz) / m["d7"]["ruta"]\n', '    d7 = _RUTA9(raiz, m["d7"]["ruta"])                  # FAM09 RAIZ-T8-v1\n')),
    _c(TESTIGO, "trabajador_testigo.py"): (
        ("PROCEDENCIA-LOCAL-v1 (ejecutable)", '"ejecutable": sys.executable}', '"ejecutable": _LOCAL9(sys.executable)}'),),
    _c(TESTIGO, "lector_fuente_testigo.py"): (
        ("SANEADO-v1", "MI_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()\n", "MI_SHA = _SHA9(Path(__file__).read_bytes())   # FAM09 SANEADO-v1\n"),
        ("PROCEDENCIA-LOCAL-v1 (inventario)", '            b = (self.R / base / "audit/entrega.json").read_bytes()\n',
         '            b = _RUTA9(self.R, base + "/audit/entrega.json").read_bytes()   # FAM09 PROCEDENCIA-LOCAL-v1\n'),
        ("PROCEDENCIA-LOCAL-v1 (base)", 'e["base"].startswith("tmp/")', 'e["base"].startswith(("tmp/", "salidas/"))'),
        ("PROCEDENCIA-LOCAL-v1 (archivo)", '        b = (self.R / e["base"] / e["rel"]).read_bytes()\n',
         '        b = _RUTA9(self.R, e["base"] + "/" + e["rel"]).read_bytes()   # FAM09 PROCEDENCIA-LOCAL-v1 / ENLACE-v1\n'),
        ("PUERTA-v1 (sin decisión)", '        TC.need(inc["fuente"].get("decision_ref") is not None, "DECISION_REFERENCIA_AUSENTE")\n',
         '        TC.need(inc["fuente"].get("decision_ref") is None, "DECISION_EN_EJECUCION_LIMPIA")   # FAM09 PUERTA-v1: nunca hay decisión\n'),
        ("PROCEDENCIA-LOCAL-v1 (alcance)", '    pal = raiz / ent["alcance"]["base"] / ent["alcance"]["rel"]\n',
         '    pal = _RUTA9(raiz, ent["alcance"]["base"] + "/" + ent["alcance"]["rel"])   # FAM09 PROCEDENCIA-LOCAL-v1\n'),
        ("PUERTA-v1 (cotejo de decisión)",
         '        TC.need(ev.get("decision_ref_sha256") == TC.sha(B["decision_ref"]) and TC.HF(pdec) == TC.sha(B["decision_ref"]), "DECISION_AJENA")\n',
         '        TC.need(ev.get("decision") is None and pdec is None and "decision_ref" not in B, "DECISION_AJENA")   # FAM09 PUERTA-v1\n'),
        ("PROCEDENCIA-LOCAL-v1 (registro de validación)", '        dp = Path(inc["dictamen"]["ruta"])\n',
         '        dp = _RUTA9(raiz, inc["dictamen"]["ruta"])   # FAM09 PROCEDENCIA-LOCAL-v1: registro de fam09-validar de la base\n')),
    _c(TESTIGO, "adaptador_fila_testigo.py"): (
        ("MODULOS-v1", ('    s = importlib.util.spec_from_file_location("certificacion_fila_aceptada", p)\n', "    return CF\n"),
         '    return _MODULO9("certificacion_fila_aceptada", p, CF_SHA256)   # FAM09 MODULOS-v1: texto adaptado de los bytes fijados\n'),),
    _c(TESTIGO, "construir_incorporacion.py"): (
        ("PUERTA-v1", '        TC.need((modo == "produccion") == bool(dec) == bool(dicta), "MEZCLA_SINTETICA_PRODUCTIVA", "produccion exige decisión y dictamen; sintético ninguno")\n',
         '        TC.need((modo == "produccion") == bool(dicta) and not dec, "MEZCLA_SINTETICA_PRODUCTIVA",\n'
         '                "FAM09 PUERTA-v1: produccion exige el registro de fam09-validar (dictamen) y ninguna decisión")\n'),
        ("PROCEDENCIA-LOCAL-v1", '"dictamen": {"ruta": str(Path(dicta)), "sha256": TC.HF(dicta)} if dicta else None,',
         '"dictamen": {"ruta": Path(dicta).as_posix(), "sha256": TC.HF(R / dicta)} if dicta else None,   # FAM09 PROCEDENCIA-LOCAL-v1')),
    _c(CONEXION_T, "conexion_testigo.py"): (
        ("SANEADO-v1", _H_ORIG, _H_NUEVO),
        ("SANEADO-v1 (marcador W)", _W_ORIG, _W_NUEVO),
        ("ENLACE-TESTIGO-v1", _CAMPOS, _ENLAZAR),
        ("ENLACE-TESTIGO-v1 (manifiesto)", _AUT_MAN_ORIG, _AUT_MAN_NUEVO),
        ("PAQUETE-v1", _PAQ2_ORIG, _PAQ2_NUEVO),
        ("NUCLEO-C0-v1", _C0_ORIG, _C0_NUEVO),
        ("ENLACE-v1", '    b = (Path(R) / "tmp" / x["area"] / x["rel"]).read_bytes()\n',
         '    b = _RUTA9(R, "tmp/%s/%s" % (x["area"], x["rel"])).read_bytes()   # FAM09 ENLACE-v1: vista de captura nueva con el mismo pin\n'),
        ("ENLACE-TESTIGO-v1 (aceptación)", '(acc.get("kind") == "accepted-high-witness-source-rem142-not-T8-finalization", "ACEPTACION_FUERA_DE_ESQUEMA")',
         '(acc.get("kind") == _ENLACE9["kind_aceptacion"], "ACEPTACION_FUERA_DE_ESQUEMA")'),
        ("ENLACE-TESTIGO-v1 (cargar)", _CARGAR_ORIG, _CARGAR_NUEVO),
        ("RAIZ-T8-v1 (rutas del finalizador)", *_RUTAS_FIN),
        ("ENLACE-TESTIGO-v1 (incorporación)", '    inc_p = R / AUTORIDAD["incorporacion"]["ruta"]\n', '    inc_p = _RUTA9(R, AUTORIDAD["incorporacion"]["ruta"])\n'),
        ("ENLACE-TESTIGO-v1 (aceptación local)", '    acc_raw = _bytes_fijados(AUTORIDAD["aceptacion"]["ruta"], ',
         '    acc_raw = _bytes_fijados(_RUTA9(R, AUTORIDAD["aceptacion"]["ruta"]), '),
        ("ENLACE-TESTIGO-v1 (registro de validación)", '    dic_raw = _bytes_fijados(AUTORIDAD["dictamen"]["ruta"], ',
         '    dic_raw = _bytes_fijados(_RUTA9(R, AUTORIDAD["dictamen"]["ruta"]), '),
        ("MODULOS-v1 (lector)", '    LT = _modulo("lector_fuente_testigo_t8_testigo", ', '    LT = _MODULO9("lector_fuente_testigo_t8_testigo", '),
        ("RAIZ-T8-v1 (finalizador)", '    UN = _modulo("unidades_finalizador_t8_testigo", R / fin["ruta"], fin["sha256"])\n',
         '    UN = _modulo("unidades_finalizador_t8_testigo", _RUTA9(R, fin["ruta"]), fin["sha256"])\n'),
        ("RAIZ-T8-v1 (src de la instalación)", *_SRC_INST)),
    _c(CONEXION_C, "conexion_c5b.py"): (
        ("SANEADO-v1", _H_ORIG, _H_NUEVO),
        ("SANEADO-v1 (marcador W)", _W_ORIG, _W_NUEVO),
        ("ENLACE-C5B-v1", _CAMPOS, _ENLAZAR),
        ("ENLACE-C5B-v1 (manifiesto)", _AUT_MAN_ORIG, _AUT_MAN_NUEVO),
        ("PAQUETE-v1", _PAQ2_ORIG, _PAQ2_NUEVO),
        ("NUCLEO-C0-v1", _C0_ORIG, _C0_NUEVO),
        ("ENLACE-C5B-v1 (pines de la aceptación)",
         '            "vista_sha256": AUTORIDAD["base_vista"]["sha256"], "ledger_rem144_sha256": AUTORIDAD["ledger"]["sha256"],\n',
         '            "vista_sha256": AUTORIDAD_HISTORICA["base_vista"]["sha256"], "ledger_rem144_sha256": AUTORIDAD_HISTORICA["ledger"]["sha256"],\n'),
        ("AUTORIDAD-EXTRAIDA-v1 (dictamen y nota rem145)",
         '(acc.get("review_sha256") == H(dic_raw) == AUTORIDAD["dictamen"]["sha256"]\n'
         '                         and acc.get("note_sha256") == H(nota_raw) == AUTORIDAD["nota_cota"]["sha256"]',
         '(acc.get("review_sha256") == _AUTORIDAD9(AUTORIDAD["dictamen"]["ruta"]) == AUTORIDAD["dictamen"]["sha256"]\n'
         '                         and acc.get("note_sha256") == _AUTORIDAD9(AUTORIDAD["nota_cota"]["ruta"]) == AUTORIDAD["nota_cota"]["sha256"]'),
        ("ENLACE-C5B-v1 (vista de la aceptación)", 'and acc.get("current_T8_product_sha256") == AUTORIDAD["base_vista"]["sha256"], "ACEPTACION_CON_OTRO_ESTADO_FORMAL")',
         'and acc.get("current_T8_product_sha256") == AUTORIDAD_HISTORICA["base_vista"]["sha256"], "ACEPTACION_CON_OTRO_ESTADO_FORMAL")'),
        ("ENLACE-C5B-v1 (registro)", 'need(led.get("kind") == "accepted-T8-high-witness-emission-rem144" and ',
         'need(led.get("kind") == _ENLACE9["kind_ledger"] and '),
        ("ENLACE-C5B-v1 (cargar)", _CARGAR_ORIG, _CARGAR_NUEVO),
        ("RAIZ-T8-v1 (rutas del finalizador)", *_RUTAS_FIN),
        ("ENLACE-C5B-v1 (vista y registro)",
         ('    base_raw = _bytes_inventariados(R, AUTORIDAD["base_vista"])\n',
          '    nota_raw = _bytes_fijados(AUTORIDAD["nota_cota"]["ruta"], AUTORIDAD["nota_cota"]["sha256"], "NOTA_DE_LA_COTA_NO_AUTENTICA")\n'),
         '    base_raw = _bytes_fijados(_RUTA9(R, AUTORIDAD["base_vista"]["rel"]), AUTORIDAD["base_vista"]["sha256"], "BASE_ENLAZADA_NO_AUTENTICA")\n'
         '    led_raw = _bytes_fijados(_RUTA9(R, AUTORIDAD["ledger"]["ruta"]), AUTORIDAD["ledger"]["sha256"], "LEDGER_NO_AUTENTICO")\n'
         '    acc_raw = dic_raw = nota_raw = None   # FAM09 AUTORIDAD-EXTRAIDA-v1: aceptación por su resumen; dictamen y nota por su huella extraída\n'),
        ("AUTORIDAD-EXTRAIDA-v1 (aceptación rem145)", '    acc = json.loads(acc_raw)\n',
         '    acc = _ACEPTACION_C5B9(AUTORIDAD["aceptacion"]["sha256"])   # FAM09 AUTORIDAD-EXTRAIDA-v1: campos cotejados, ligados al original\n'),
        ("MODULOS-v1 (certificación)", '    CF = _modulo("certificacion_fila_t8_c5b", ', '    CF = _MODULO9("certificacion_fila_t8_c5b", '),
        ("RAIZ-T8-v1 (finalizador)", '    UN = _modulo("unidades_finalizador_t8_c5b", R / fin["ruta"], fin["sha256"])\n',
         '    UN = _modulo("unidades_finalizador_t8_c5b", _RUTA9(R, fin["ruta"]), fin["sha256"])\n'),
        ("RAIZ-T8-v1 (src de la instalación)", *_SRC_INST))}


# ================================================================================================ guiones y módulos adaptados
def adaptado(n: str) -> str:
    """GUION-v1: bytes exactos de <n> (proyección: se autentica por su original) con sus sustituciones (cada original, una sola vez; un
    bloque se fija por su primera y su última línea)."""
    src = (BASE / n).read_bytes()
    need(sha9(src) == CODIGO[n], "CODIGO_FAM09_DISTINTO: %s" % n)
    txt = src.decode("utf-8")
    for i, a, b in SUSTITUCIONES.get(n, ()):
        if isinstance(a, tuple):
            need(txt.count(a[0]) == 1 and txt.count(a[1]) == 1 and txt.index(a[0]) < txt.index(a[1]), "SUSTITUCION_NO_UNICA: %s %s" % (n, i))
            a = txt[txt.index(a[0]):txt.index(a[1]) + len(a[1])]
        need(txt.count(a) == 1, "SUSTITUCION_NO_UNICA: %s %s" % (n, i))
        txt = txt.replace(a, b)
    return txt


def sustituciones_ok() -> dict:
    out = {}
    for n in SUSTITUCIONES:
        try:
            compile(adaptado(n), n, "exec")
            out[n] = True
        except Exception as e:  # noqa: BLE001  (pieza ausente o distinta: se informa, no se interrumpe la comprobación)
            out[n] = _sin_base("%s: %s" % (type(e).__name__, e))[:200]
    return out


def modulo(nombre: str, n: str):
    txt = adaptado(n)
    h = sha(txt.encode("utf-8"))
    m = sys.modules.get(nombre)
    if m is None or getattr(m, "FAM09_ADAPTADO_SHA256", None) != h:
        m = types.ModuleType(nombre)
        m.__file__ = str(BASE / n)
        m.__dict__.update(_ayudas(n))
        sys.modules[nombre] = m
        ruta = list(sys.path)
        try:
            exec(compile(txt, str(BASE / n), "exec"), m.__dict__)
        except BaseException:
            sys.modules.pop(nombre, None)
            raise
        finally:
            sys.path[:] = ruta
        m.FAM09_ADAPTADO_SHA256 = h
    return m


def preparar(grupo: str) -> dict:
    return {k: modulo(k, n) for k, n in MODULOS[grupo]}


def _sin_base(t):
    """Sin la ruta de la base en ninguna de sus formas (JSON escapada, nativa, POSIX)."""
    if t is None:
        return None
    for f in (str(BASE).replace("\\", "\\\\"), str(BASE), BASE.as_posix()):
        t = t.replace(f, "<base>")
    return t


def _ejecutar(n: str, args: list, mods: dict) -> tuple:
    """Texto adaptado de <n> como __main__ (sys.argv = [<base>/<n>, *args]) -> (rc, última línea JSON, stdout, excepción)."""
    txt = adaptado(n)
    p = BASE / n
    g = {"__name__": "__main__", "__file__": str(p), "__builtins__": builtins}
    g.update(_ayudas(n))
    viejo, ruta, buf, rc, exc = sys.argv, list(sys.path), io.StringIO(), 0, None     # fin normal del guion = código 0
    sys.argv = [str(p)] + [str(x) for x in args]
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(txt, str(p), "exec"), g)
    except SystemExit as ex:
        rc = 0 if ex.code is None else ex.code
    except Exception:  # noqa: BLE001  (se registra; nunca se toma por éxito)
        rc, exc = None, _sin_base(traceback.format_exc())
    finally:
        sys.argv = viejo
        sys.path[:] = ruta
    need(all(sys.modules.get(k) is m for k, m in mods.items()), "MODULO_FAM09_SUSTITUIDO_DURANTE_EL_GUION")
    texto = _sin_base(buf.getvalue())
    lineas = [x for x in texto.splitlines() if x.strip()]
    try:
        ult = json.loads(lineas[-1]) if lineas else {}
    except ValueError:
        ult = {}
    return rc, ult, texto, exc


def _paper2b_cargado() -> list:
    return sorted(m for m in sys.modules if m == "paper2b" or m.startswith("paper2b."))


def _paper2b_origen() -> list:
    return sorted({rel(Path(m.__file__).parent) for k, m in list(sys.modules.items())
                   if (k == "paper2b" or k.startswith("paper2b.")) and getattr(m, "__file__", None)})


# ================================================================================================ fuentes, declaración y pilotos
def piezas() -> list:
    fu = fuentes()
    return fu["archivos"] + [x for x in fu["reutilizados"] if (BASE / x["archivo"]).is_file()]


def fuentes_alteradas(uso: str = "todo") -> list:
    """«calculo»: código, núcleo y entradas (sin referencias); «todo»: también las referencias (fam09-comprobar)."""
    return [x["archivo"] for x in piezas() if (uso == "todo" or not x["archivo"].startswith("referencias/"))
            and sha_archivo(BASE / x["archivo"]) != x["sha256"]]


def manifiesto(etapa: str) -> tuple:
    p, h = MAN[etapa]
    raw = (BASE / p).read_bytes()
    need(sha9(raw) == h, "MANIFIESTO_%s_DISTINTO" % etapa)
    return raw, json.loads(raw)


def entradas_testigo() -> dict:
    """Entradas esperadas del testigo (testigo_comun.entradas_esperadas sobre el manifiesto v2 cargado y comprobado por testigo_comun)."""
    TC = preparar("TESTIGO")["testigo_comun"]
    m, msha = TC.cargar_manifiesto(R9, BASE / MAN["TESTIGO"][0])
    need(msha == MAN["TESTIGO"][1], "MANIFIESTO_TESTIGO_DISTINTO")
    piezas_ = {n: CODIGO[_c(TESTIGO, n)] for n in TC.PIEZAS}
    return {"tareas": list(TC.TAREAS), "entradas": TC.entradas_esperadas(m, msha, piezas_), "asignaciones": json.loads(json.dumps(TC.ASIGNACIONES)),
            "limites": dict(TC.LIMITES), "instalacion_identidad": TC.C0_ID, "operacion": TC.OPERACION}


def regla_declaracion() -> dict:
    t = entradas_testigo()
    return {"kind": DECL_KIND, "etiqueta": ETIQUETA, "oficial": False, "decision": None, "emitida_utc": EMITIDA,
            "naturaleza": ("PUERTA-v1: las puertas de producción (alcance v3 verificado por C0 y decisión humana nativa) no se ejecutan ni se "
                           "reconstruyen. λ, captura, emisión del testigo y C5B corren en modo candidata (sin alcance ni decisión). El testigo alto "
                           "corre en modo produccion con ESTE documento como alcance: fija antes de calcular las entradas esperadas, las asignaciones y "
                           "los límites (un proceso, 600 s). No es un alcance ni una decisión; no autoriza producción oficial ni sustituye a los "
                           "alcances históricos (210015d7… del testigo; los de rem137/rem139/rem143/rem146)."),
            "operaciones": [t.pop("operacion")], "testigo": t, "codigo": dict(CODIGO),
            "modos": {"F09-LAMBDA": "candidata", "F09-CAPTURA": "candidata", "F09-TESTIGO (cálculo y validación)": "produccion con esta declaración",
                      "F09-TESTIGO (emisión)": "candidata", "F09-C5B": "candidata"}}


def regla_pilotos() -> dict:
    _, m = manifiesto("TESTIGO")
    return {"regla": ("fijado por el encargo de FAM09 antes de calcular y sin mirar resultados: el techo alto del grupo EQ-TECHO-T8-1, clave "
                      "e8b1f7fd…, UNA vez, con el trabajador auténtico (trabajador_testigo.py fefa171c…), el núcleo histórico lima1855 y la "
                      "configuración de su manifiesto v2 (3ed91d32…), bajo el supervisor existente, un proceso y límite externo de 600 s. Un "
                      "vencimiento real se informa y no se relanza. La referencia rem141 solo se lee después del cálculo (fam09-comparar)."),
            "pilotos": [{"unidad": "TESTIGO", "operacion": "F09-TESTIGO", "clave": m["clave"], "grupo": m["grupo"], "procesos": 1,
                         "limite_externo_s": 600.0, "nucleo": m["nucleo"]["raiz"], "configuracion": m["config"],
                         "duracion_historica": "≈1 s de cálculo según el RESULTADO rem141 (informativa; no es un tope)"}]}


def fijar(nombre: str, doc: dict) -> dict:
    raw = (json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True) + "\n").encode("utf-8")
    p = DATOS / nombre
    if p.exists():
        need(p.read_bytes() == raw, "DATO_FIJADO_DISTINTO_DE_SU_REGLA: %s" % nombre)
    else:
        p.write_bytes(raw)
    return doc


def declaracion() -> tuple:
    p = DATOS / DECLARACION
    raw = p.read_bytes() if p.is_file() else b""
    need(raw == (json.dumps(regla_declaracion(), ensure_ascii=False, indent=1, sort_keys=True) + "\n").encode("utf-8"),
         "DECLARACION_DE_EJECUCION_LIMPIA_AUSENTE_O_DISTINTA")
    return sha(raw), raw


def anexo() -> list:
    raw = (BASE / ANEXO[0]).read_bytes()
    need(sha(raw) == ANEXO[1], "ANEXO_T8_DISTINTO")
    ib = (BASE / ANEXO[2]).read_bytes()
    need(sha(ib) == ANEXO[3] and json.loads(ib)["files"].get(ANEXO[4], {}).get("sha256") == ANEXO[1], "ANEXO_T8_FUERA_DE_SU_INVENTARIO")
    return json.loads(raw)["filas"]


def clave_fila(a: dict) -> str:
    return sha(canon({"ref": a["ref"], "fila_en_unidad": a["fila_en_unidad"], "inversion_id": a["inversion_id"], "cell_id": a["cell_id"]}))


def listar() -> dict:
    filas = anexo()
    _, ml = manifiesto("LAMBDA")
    _, mc = manifiesto("CAPTURA")
    return {"comando": "fam09-listar", "calculo": "ninguno", "operaciones": OPERACIONES,
            "recuento": {"anexo": len(filas), "definitivas_previas": sum(1 for f in filas if not f["estado_es_por_unidad"]),
                         "lambda_required": sum(1 for f in filas if f["estado_es_por_unidad"] and f["inversion_id"] == "lambda_required"),
                         "capture_required": sum(1 for f in filas if f["estado_es_por_unidad"] and f["inversion_id"] == "capture_required"),
                         "esperado_lambda": ml["esperado"], "esperado_captura": mc["esperado"]},
            "manifiestos": {k: v[1] for k, v in MAN.items()},
            "pilotos": fijar("pilotos.json", regla_pilotos()), "declaracion": fijar(DECLARACION, regla_declaracion())}


# ================================================================================================ lecturas y entorno
def declarados() -> set:
    out = set(_src("fam08").declarados())
    out |= {x["archivo"] for x in piezas()}
    return out


def lecturas(rastro, informe: dict, prohibidas: tuple = ()) -> dict:
    dec = declarados()
    propios = ("src/", "reproducir.py", "datos/fam01/", "datos/fam09/", "fuentes_fam0", "fuentes_fam1", "catalogo.json")
    en = informe["en_el_paquete"]
    sal = sorted(x for x in rastro.dentro if x.startswith("salidas/") and (BASE / x).is_file())
    return {"archivo": "archivos_leidos.json", "en_el_paquete": len(en), "del_entorno_venv": sum(1 for x in en if x.startswith(".venv-fam01/")),
            "aperturas_del_interprete": informe["aperturas_del_interprete"], "fuera_del_paquete_y_del_interprete": informe["fuera_del_paquete_y_del_interprete"],
            "sin_manifiesto": [x for x in en if x not in dec and not x.startswith((".venv-fam01/",) + propios)],
            "codigo_fam09_leido": sorted(x for x in en if x in CODIGO),
            "nucleo_lima1855_leidos": sum(1 for x in en if "_lima1855/candidato/src/paper2b/" in x),
            "instalacion_leidos": sum(1 for x in en if x.startswith("nucleo_s6/instalacion/")),
            "nucleo_c0_leidos": sum(1 for x in en if x.startswith("nucleo_s6/c0/")),
            "d7_leidos": sum(1 for x in en if x.startswith("nucleo_s6/raiz/fase2_datos/")),
            "referencias_leidas": sorted(x for x in en if x.startswith("referencias/") and not x.startswith("referencias/fam01/")),
            "salidas_leidas": sal, "referencia_esperada_leida": any(x.startswith(prohibidas) for x in en) if prohibidas else False}


def entorno() -> dict:
    import os
    import platform
    return {"python": platform.python_version(), "hash_seed": os.environ.get("PYTHONHASHSEED"), "hash_randomization": sys.flags.hash_randomization,
            "hilos": {k: os.environ.get(k) for k in F1().HILOS}, "TZ": os.environ.get("TZ"),
            "f2": "F2 es solo de FAM01; no se evalúa aquí (importaría paper2b de la raíz en el proceso del testigo)"}


def _escribir(p: Path, doc: dict):
    p.write_bytes(json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True, default=str).encode("utf-8") + b"\n")


def _escribir_x(p: Path, doc: dict):
    with Path(p).open("xb") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True, default=str).encode("utf-8") + b"\n")


def lineas(raw: bytes) -> list:
    partes = raw.split(b"\n")
    need(partes[-1] == b"", "VISTA_SIN_FIN_DE_LINEA")
    return partes[:-1]


# ================================================================================================ entradas por etapa
def registro_aceptado(p: Path, tarea: str, origen: Path) -> dict:
    """Registro de fam09-validar ACEPTADO para esa carpeta y esos bytes (sus productos siguen con la misma huella)."""
    p = Path(p).resolve()
    need(p.is_file(), "REGISTRO_DE_VALIDACION_AUSENTE: %s" % rel(p))
    r = leer(p)
    need(r.get("comando") == "fam09-validar" and r.get("tarea") == tarea and r.get("aceptada") is True and r.get("origen") == rel(origen),
         "REGISTRO_DE_VALIDACION_NO_ACEPTADO_O_AJENO: %s" % rel(p))
    for k, v in (r.get("productos_sha256") or {}).items():
        need(sha_archivo(BASE / k) == v, "PRODUCTO_CAMBIADO_DESPUES_DE_VALIDAR: %s" % k)
    need(r.get("productos_sha256"), "REGISTRO_SIN_PRODUCTOS")
    return r


def entradas_de(tarea: str, entradas: dict) -> dict:
    """--entrada <clave>=<carpeta de fam09-etapa> y --entrada validacion_<clave>=<registro de fam09-validar aceptado> por etapa."""
    req = ENTRADAS_DE.get(tarea, {})
    entradas = dict(entradas or {})
    esperadas = set(req) | {"validacion_" + k for k in req}
    need(set(entradas) == esperadas, "ENTRADAS_DE_%s: se esperan exactamente %s" % (tarea, sorted(esperadas)))
    out = {}
    for k, et in req.items():
        d = Path(entradas[k]).resolve()
        ej = leer(d / "ejecucion.json") if (d / "ejecucion.json").is_file() else {}
        need(ej.get("etiqueta") == ETIQUETA and ej.get("tarea") == et and ej.get("exito") is True, "ENTRADA_%s_NO_ES_UNA_ETAPA_%s_COMPLETA" % (k, et))
        r = registro_aceptado(Path(entradas["validacion_" + k]), et, d)
        out[k] = {"carpeta": d, "ejecucion": ej, "registro": Path(entradas["validacion_" + k]).resolve(), "validacion": r}
    return out


def _desc_entradas(ent: dict) -> dict:
    return {k: {"carpeta": rel(v["carpeta"]), "registro_validacion": rel(v["registro"]), "registro_sha256": sha_archivo(v["registro"]),
                "productos_sha256": v["validacion"]["productos_sha256"]} for k, v in ent.items()}


# ================================================================================================ etapas
def _hist(sal: Path, ent: dict) -> dict:
    filas = anexo()
    claves = [clave_fila(a) for a in filas]
    need(len(set(claves)) == len(filas), "CLAVES_DUPLICADAS_EN_EL_ANEXO")
    pres = []
    for i, a in enumerate(filas):
        if not a["estado_es_por_unidad"]:
            pres.append({"fila": i, "clave_fila": claves[i], "result_status": a["result_status"], "outside_support": a["outside_support"],
                         "computation_status": a["computation_status"], "inversion_id": a["inversion_id"], "historico_sha256": sha(canon(a))})
    raw = b"".join(canon(x) + b"\n" for x in pres)
    (sal / "FILAS_PRESERVADAS.jsonl").write_bytes(raw)
    doc = {"kind": "filas-historicas-preservadas-t8-fam09", "anexo_sha256": ANEXO[1], "anexo_inventario_sha256": ANEXO[3], "filas_anexo": len(filas),
           "preservadas": len(pres), "preservadas_sha256": sha(raw), "claves_unicas": len(set(claves)),
           "preservadas_por_estado": dict(sorted(Counter(x["result_status"] for x in pres).items())),
           "preservadas_por_inversion": dict(sorted(Counter(x["inversion_id"] for x in pres).items())),
           "por_unidad": dict(sorted(Counter(a["inversion_id"] for a in filas if a["estado_es_por_unidad"]).items())),
           "outside_support_historicas": sum(1 for a in filas if a["outside_support"] is True),
           "outside_support_preservadas": sum(1 for x in pres if x["outside_support"] is True),
           "coherencia_bandera_estado": sum(1 for x in pres if (x["result_status"] == "outside_support") != (x["outside_support"] is True)),
           "regla": "definitivo_almacenado <=> estado_es_por_unidad = false (EntradaLambda.vista); clave_fila = sha256(canon(ref, fila_en_unidad, "
                    "inversion_id, cell_id)) como validar_emision_lambda.clave_fila"}
    _escribir(sal / "HIST.json", doc)
    ok = doc["preservadas"] == ESPERADO["hist"] and doc["filas_anexo"] == ESPERADO["filas"] and doc["claves_unicas"] == ESPERADO["filas"]
    return {"rc": 0 if ok else 4, "resumen": doc, "productos_sha256": {rel(sal / "FILAS_PRESERVADAS.jsonl"): sha(raw), rel(sal / "HIST.json"): sha_archivo(sal / "HIST.json")},
            "exito": ok}


def _materializar(tarea: str, sal: Path, mods: dict) -> dict:
    me = BASE / MAN[tarea][0]
    rc, ult, stdout, exc = _ejecutar(GUIONES[tarea][0], [R9, me, sal / "producto", "--modo", "candidata"], mods)
    (sal / "materializar_stdout.txt").write_text(stdout, encoding="utf-8")
    pp = sal / "producto" / PRODUCTO[tarea]
    h = sha_archivo(pp) if pp.is_file() else None
    return {"rc": rc, "ultima_linea": ult, "excepcion": exc, "guion": GUIONES[tarea][0],
            "argumentos": ["<raiz T8: %s>" % T9, rel(me), rel(sal / "producto"), "--modo", "candidata"],
            "productos_sha256": {rel(pp): h} if h else {}, "producto_sha256": h,
            "exito": exc is None and rc == 0 and h is not None and ult.get("producto_sha256") == h}


def _lambda(sal: Path, ent: dict) -> dict:
    need(not _paper2b_cargado(), "PAPER2B_PRECARGADO (el finalizador carga el de la instalación)")
    r = _materializar("LAMBDA", sal, preparar("LAMBDA"))
    r["paper2b"] = _paper2b_origen()
    return r


def _captura(sal: Path, ent: dict) -> dict:
    need(not _paper2b_cargado(), "PAPER2B_PRECARGADO (el finalizador carga el de la instalación)")
    lam = ent["lambda"]["carpeta"] / "producto" / PRODUCTO["LAMBDA"]
    ENTRADAS9[PIN_LAMBDA] = rel(lam)
    r = _materializar("CAPTURA", sal, preparar("CAPTURA"))
    r["paper2b"] = _paper2b_origen()
    return r


def _testigo(sal: Path, ent: dict) -> dict:
    """CÁLCULO del techo alto: entrega local (alcance = declaración, código copiado) y trabajador auténtico, una vez."""
    need(not _paper2b_cargado(), "PAPER2B_PRECARGADO: el testigo se calcula en un proceso propio con el núcleo lima1855")
    d = sal / "testigo"
    (d / "alcance").mkdir(parents=True)
    (d / "alcance" / DECLARACION).write_bytes((DATOS / DECLARACION).read_bytes())
    (d / "codigo").mkdir()
    mods = preparar("TESTIGO")
    for n in mods["testigo_comun"].PIEZAS:
        (d / "codigo" / n).write_bytes((BASE / _c(TESTIGO, n)).read_bytes())
    args = [R9, BASE / MAN["TESTIGO"][0], d / SALIDA_TESTIGO, "--modo", "produccion", "--alcance", d / "alcance" / DECLARACION]
    a0 = time.time()
    rc, ult, stdout, exc = _ejecutar(_c(TESTIGO, "trabajador_testigo.py"), args, mods)
    t = round(time.time() - a0, 3)
    (sal / "trabajo_stdout.txt").write_text(stdout, encoding="utf-8")
    res = d / SALIDA_TESTIGO / "RESULTADO.json"
    prod = {rel(p): sha_archivo(p) for p in sorted(d.rglob("*")) if p.is_file()}
    return {"rc": rc, "ultima_linea": ult, "excepcion": exc, "guion": _c(TESTIGO, "trabajador_testigo.py"), "segundos_trabajador": t,
            "argumentos": ["<raiz T8: %s>" % T9, MAN["TESTIGO"][0], rel(d / SALIDA_TESTIGO), "--modo", "produccion", "--alcance", rel(d / "alcance" / DECLARACION)],
            "resultado_sha256": sha_archivo(res) if res.is_file() else None, "productos_sha256": prod, "paper2b": _paper2b_origen(),
            "fallo": leer(d / SALIDA_TESTIGO / "FALLO.json") if (d / SALIDA_TESTIGO / "FALLO.json").is_file() else None,
            "exito": exc is None and rc == 0 and res.is_file()}


def aceptacion_local(lect: dict, ev: list, inc_sha: str, ev_sha: str, reg_testigo: Path, inv_sha: str, res: dict, res_sha: str, decl_sha: str) -> dict:
    """Cobertura EXACTA independiente de las 40 pendientes con la regla aceptada (C2_inf + err_inf <= v <= C2_sup - err_sup), desde la
    evidencia del lector y el RESULTADO nuevo; ocupa la aceptación técnica rem142 (mismos campos que coteja conexion_testigo). No es un acto
    de Codex: es la comprobación local que el registro de esta reproducción conserva."""
    lo = Fraction(EXTREMO_INFERIOR)
    hi = Fraction(res["C2"]) - Fraction(res["numerical_error_share"])
    cub, pend = [], []
    for x in ev:
        v = Fraction(x["valor_requerido"])
        lo_ok, hi_ok = lo <= v, v <= hi
        if lo_ok and hi_ok:
            cub.append({"row": x["fila"], "row_key": x["clave_fila"], "destination_run": x["run_destino"], "required_exact": str(v),
                        "lower_ok": True, "upper_ok": True, "covered": True, "upper_margin_exact": str(hi - v)})
        else:
            pend.append(x["fila"])
    return {"kind": KIND_ACEPTACION, "oficial": False, "review_sha256": sha_archivo(reg_testigo), "inventory_sha256": inv_sha, "result_sha256": res_sha,
            "scope_sha256": decl_sha, "new_run_origin": lect["ejecucion_nueva"]["run_origen"], "key": CLAVE_TECHO, "group": GRUPO,
            "reader_evidence_sha256": ev_sha, "review_incorporation_document_sha256": inc_sha,
            "lower_accepted_witness": {"ceiling_id": lect["testigo_inferior"]["ceiling_id"], "run_origen": "BRUN-cb33e6b24039acc84fb1a065"},
            "coverage_exact": {"lower_endpoint": EXTREMO_INFERIOR, "upper_endpoint": str(hi), "covered_rows_pending_emission": cub,
                               "five_pending_rows_not_excluded": sorted(pend)},
            "coincide_con_el_lector": sorted(x["row"] for x in cub) == sorted(lect["cubiertas"]),
            "T8_definitive": 13616, "T8_formal_pending": 40, "T8_new_finalized": 0,
            "nota": "aceptación LOCAL (no oficial) por cobertura exacta recalculada; el dictamen de esta reproducción corresponde a Codex"}


def _incorporacion(sal: Path, ent: dict) -> dict:
    """EMISIÓN de las 35 filas: incorporación de la entrega nueva validada, lector, cobertura exacta y conexión del testigo."""
    need(not _paper2b_cargado(), "PAPER2B_PRECARGADO")
    cap = ent["captura"]["carpeta"] / "producto" / PRODUCTO["CAPTURA"]
    ENTRADAS9[PIN_CAPTURA] = rel(cap)
    tdir, reg = ent["testigo"]["carpeta"], ent["testigo"]["registro"]
    base_f = rel(tdir / "testigo")
    vt = ent["testigo"]["validacion"]
    need(sha_archivo(tdir / "testigo" / "audit" / "entrega.json") == vt["inventario_sha256"], "INVENTARIO_DE_LA_ENTREGA_DISTINTO_DEL_VALIDADO")
    mods = preparar("LECTOR")
    (sal / "incorporacion").mkdir()
    inc = sal / "incorporacion" / "INCORPORACION_TESTIGO.json"
    rc1, ult1, out1, exc1 = _ejecutar(_c(TESTIGO, "construir_incorporacion.py"),
                                      [BASE, inc, "--modo", "produccion", "--fuente", base_f, "--etiqueta", ETIQUETA_TESTIGO, "--alcance",
                                       "alcance/" + DECLARACION, "--codigo", base_f, "codigo", "--dictamen", rel(reg), "--texto", TEXTO_INC], mods)
    pasos = {"incorporacion": {"rc": rc1, "ultima_linea": ult1, "excepcion": exc1}}
    if not (exc1 is None and rc1 == 0 and inc.is_file()):
        return {"rc": rc1, "excepcion": exc1, "pasos": pasos, "productos_sha256": {}, "exito": False}
    inc_sha = sha_archivo(inc)
    lec = sal / "lectura"
    rc2, ult2, out2, exc2 = _ejecutar(_c(TESTIGO, "lector_fuente_testigo.py"), [R9, inc, inc_sha, lec, "--modo", "produccion"], mods)
    pasos["lector"] = {"rc": rc2, "ultima_linea": ult2, "excepcion": exc2}
    if not (exc2 is None and rc2 == 0 and (lec / "EVIDENCIA_CANDIDATA_FILAS.jsonl").is_file()):
        return {"rc": rc2, "excepcion": exc2, "pasos": pasos, "productos_sha256": {rel(inc): inc_sha}, "exito": False}
    lect = leer(lec / "LECTURA_FUENTE_TESTIGO.json")
    ev = leer_jsonl(lec / "EVIDENCIA_CANDIDATA_FILAS.jsonl")
    ev_sha = sha_archivo(lec / "EVIDENCIA_CANDIDATA_FILAS.jsonl")
    sres = tdir / "testigo" / SALIDA_TESTIGO / "RESULTADO.json"
    res, res_sha = leer(sres), sha_archivo(sres)
    hdec = sha_archivo(tdir / "testigo" / "alcance" / DECLARACION)
    acc = aceptacion_local(lect, ev, inc_sha, ev_sha, reg, vt["inventario_sha256"], res, res_sha, hdec)
    accp = sal / "ACEPTACION_TESTIGO_FAM09.json"
    _escribir_x(accp, acc)
    hi = acc["coverage_exact"]["upper_endpoint"]
    enlace = {"kind": "enlace-fam09", "etapa": "INCORPORACION", "modulo": "conexion_testigo", "kind_aceptacion": KIND_ACEPTACION, "kind_ledger": None,
              "entradas9": dict(ENTRADAS9),
              "autoridad": {"incorporacion": {"ruta": rel(inc), "sha256": inc_sha, "origen_revisor": None},
                            "aceptacion": {"ruta": rel(accp), "sha256": sha_archivo(accp)},
                            "dictamen": {"ruta": rel(reg), "sha256": sha_archivo(reg)},
                            "evidencia_filas_sha256": ev_sha,
                            "testigo_superior": {"clave": CLAVE_TECHO, "grupo": GRUPO, "run_origen": lect["ejecucion_nueva"]["run_origen"],
                                                 "resultado_sha256": res_sha, "fuente_inventario_sha256": vt["inventario_sha256"], "fuente_base": base_f,
                                                 "alcance_origen_sha256": hdec, "decision_origen_uuid": None, "extremo_exacto": hi}},
              "nota": ("ENLACE-TESTIGO-v1: claves de la AUTORIDAD de conexion_testigo sustituidas por las salidas nuevas validadas; el resto (vista "
                       "base 66891b45… por ENLACE-v1, lector, inferior CEI:dc4e1ba9…, plantilla, finalizador, filas 35/5, esperados) es la histórica")}
    _escribir_x(sal / "ENLACE_T8_TESTIGO.json", enlace)
    fijar_enlace(enlace)
    mods2 = dict(mods)
    mods2.update(preparar("INCORPORACION"))
    r = _materializar("INCORPORACION", sal, mods2)
    r["pasos"] = pasos
    r["cobertura"] = {"cubiertas": sorted(x["row"] for x in acc["coverage_exact"]["covered_rows_pending_emission"]),
                      "pendientes": acc["coverage_exact"]["five_pending_rows_not_excluded"], "extremo_superior": hi,
                      "mismas_35": sorted(x["row"] for x in acc["coverage_exact"]["covered_rows_pending_emission"]) == FILAS_TESTIGO,
                      "mismas_5": acc["coverage_exact"]["five_pending_rows_not_excluded"] == FILAS_C5B, "coincide_con_el_lector": acc["coincide_con_el_lector"]}
    r["productos_sha256"] = dict(r["productos_sha256"], **{rel(inc): inc_sha, rel(lec / "EVIDENCIA_CANDIDATA_FILAS.jsonl"): ev_sha,
                                                          rel(accp): sha_archivo(accp), rel(sal / "ENLACE_T8_TESTIGO.json"): sha_archivo(sal / "ENLACE_T8_TESTIGO.json")})
    r["paper2b"] = _paper2b_origen()
    r["exito"] = r["exito"] and r["cobertura"]["mismas_35"] and r["cobertura"]["mismas_5"] and r["cobertura"]["coincide_con_el_lector"]
    return r


def fijar_enlace(enlace: dict):
    """Activa un ENLACE_*.json tras comprobar que cada archivo que nombra conserva su huella."""
    for k, v in enlace["autoridad"].items():
        if isinstance(v, dict) and "ruta" in v:
            need(sha_archivo(BASE / v["ruta"]) == v["sha256"], "ENLACE_CON_ARCHIVO_CAMBIADO: %s" % k)
        if isinstance(v, dict) and isinstance(v.get("inventario"), dict):
            need(sha_archivo(BASE / v["inventario"]["ruta"]) == v["inventario"]["sha256"], "ENLACE_CON_ARCHIVO_CAMBIADO: %s.inventario" % k)
        if isinstance(v, dict) and "rel" in v:
            need(sha_archivo(BASE / v["rel"]) == v["sha256"], "ENLACE_CON_ARCHIVO_CAMBIADO: %s.rel" % k)
    ENTRADAS9.clear()
    for k, v in (enlace.get("entradas9") or {}).items():
        ENTRADAS9[k] = v
    ENLACE9.clear()
    ENLACE9.update({"autoridad": enlace["autoridad"], "kind_aceptacion": enlace.get("kind_aceptacion"), "kind_ledger": enlace.get("kind_ledger")})


def _c5b(sal: Path, ent: dict) -> dict:
    need(not _paper2b_cargado(), "PAPER2B_PRECARGADO")
    e = ent["testigo_vista"]
    vista, verif, reg = e["carpeta"] / "producto" / PRODUCTO["INCORPORACION"], e["carpeta"] / "producto" / "VERIFICACION.json", e["registro"]
    need(e["validacion"].get("kind") == KIND_LEDGER and e["validacion"].get("product_sha256") == sha_archivo(vista)
         and e["validacion"].get("inventory_sha256") == sha_archivo(verif), "REGISTRO_DE_LA_VISTA_DEL_TESTIGO_AJENO")
    enlace = {"kind": "enlace-fam09", "etapa": "C5B", "modulo": "conexion_c5b", "kind_aceptacion": None, "kind_ledger": KIND_LEDGER, "entradas9": {},
              "autoridad": {"base_vista": {"area": rel(e["carpeta"]), "inventario": {"ruta": rel(verif), "sha256": sha_archivo(verif)},
                                           "rel": rel(vista), "sha256": sha_archivo(vista), "estado_formal": {"definitivas": 13651, "pendientes": 5}},
                            "ledger": {"ruta": rel(reg), "sha256": sha_archivo(reg)}},
              "certificado": "REUTILIZADO: CERTIFICADO_C5B_CANDIDATO.json fc403d40… y C5B_MASA_M2.json 05c10ea6… (rem144) por su inventario; los "
                             "guiones C3/M2 solo se autentican por huella (su derivación no se regenera)",
              "nota": ("ENLACE-C5B-v1: la vista base es la del testigo NUEVA (validada) y el registro de su validación ocupa el ledger rem144; la "
                       "aceptación técnica rem145 fija la vista histórica ec6e3929…: el certificado se liga por las cinco líneas pendientes, "
                       "que deben ser idénticas (linea_vista_sha256)")}
    _escribir_x(sal / "ENLACE_T8_C5B.json", enlace)
    fijar_enlace(enlace)
    r = _materializar("C5B", sal, preparar("C5B"))
    r["productos_sha256"] = dict(r["productos_sha256"], **{rel(sal / "ENLACE_T8_C5B.json"): sha_archivo(sal / "ENLACE_T8_C5B.json")})
    r["paper2b"] = _paper2b_origen()
    r["certificado"] = "reutilizado (no regenerado)"
    return r


ETAPA_FN = {"HIST": _hist, "LAMBDA": _lambda, "CAPTURA": _captura, "TESTIGO": _testigo, "INCORPORACION": _incorporacion, "C5B": _c5b}
NATURALEZA = {"HIST": "integridad (sin cálculo): recuento y huellas de las filas preservadas del anexo T8",
              "LAMBDA": "regeneración: materializar_lambda.py (candidata) sobre la entrada λ autenticada",
              "CAPTURA": "regeneración: materializar_captura.py (candidata) sobre el producto λ NUEVO validado",
              "TESTIGO": "CÁLCULO: trabajador_testigo.py auténtico, núcleo lima1855, una vez (techo alto e8b1f7fd…)",
              "INCORPORACION": "emisión: incorporación + lector + cobertura exacta + materializar_t8_testigo.py (candidata) sobre la captura NUEVA y el techo NUEVO validados",
              "C5B": "regeneración: materializar_t8_c5b.py (candidata) sobre la vista del testigo NUEVA validada; certificado reutilizado"}


def correr(tarea: str, salida: Path, entradas: dict) -> dict:
    """fam09-etapa: una etapa en la carpeta NUEVA `salida`."""
    T0, c0 = time.time(), time.process_time()
    rastro = F1().Rastro()
    need(tarea in ETAPAS, "ETAPA_FUERA_DE_FAM09: %s" % tarea)
    malos = fuentes_alteradas("calculo")
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam09.json; no se calcula): %s" % malos[:5])
    hdec, _ = declaracion()
    ent = entradas_de(tarea, entradas)
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    sal = salida.resolve()
    inicio = utc()
    a0 = time.time()
    det = ETAPA_FN[tarea](sal, ent)
    t_calc = round(time.time() - a0, 3)
    fin = utc()
    informe = rastro.informe()
    (sal / "archivos_leidos.json").write_bytes((json.dumps(informe, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    usados = sorted(n for n in CODIGO if any(getattr(m, "__file__", None) == str(BASE / n) for m in list(sys.modules.values())))
    ej = {"etiqueta": ETIQUETA, "tarea": tarea, "operacion": OPERACION_DE[tarea], "naturaleza": NATURALEZA[tarea], "adaptaciones": list(ADAPTACIONES),
          "declaracion_sha256": hdec, "entradas": _desc_entradas(ent), "entradas9": dict(ENTRADAS9), "inicio_utc": inicio, "fin_utc": fin,
          "detalle": det, "rc": det.get("rc"), "excepcion": det.get("excepcion"), "productos_sha256": det.get("productos_sha256") or {},
          "adaptado_sha256": {n: sha(adaptado(n).encode("utf-8")) for n in usados if n in SUSTITUCIONES},
          "tiempos_s": {"etapa": t_calc, "total": round(time.time() - T0, 3), "cpu": round(time.process_time() - c0, 3)},
          "entorno": entorno(), "lecturas": lecturas(rastro, informe, ("referencias/fam09/",))}
    ej["exito"] = bool(det.get("exito")) and not ej["lecturas"]["fuera_del_paquete_y_del_interprete"] and not ej["lecturas"]["referencia_esperada_leida"]
    _escribir(sal / "ejecucion.json", ej)
    return ej


# ================================================================================================ validación (sin cálculo)
def _verificar(tarea: str, nueva: Path, mods: dict) -> tuple:
    rc, ver, stdout, exc = _ejecutar(GUIONES[tarea][1], [R9, BASE / MAN[tarea][0], nueva / "producto", "--modo", "candidata"], mods)
    vf = nueva / "producto" / "VERIFICACION.json"
    return rc, ver, stdout, exc, vf


def validar(nueva: Path) -> dict:
    """fam09-validar: SIN CÁLCULO. El verificador histórico de la etapa sobre los bytes de la carpeta (U36 en el testigo)."""
    t0 = time.time()
    rastro = F1().Rastro()
    nueva = Path(nueva).resolve()
    ej = leer(nueva / "ejecucion.json") if (nueva / "ejecucion.json").is_file() else {}
    tarea = ej.get("tarea")
    need(ej.get("etiqueta") == ETIQUETA and tarea in ETAPAS, "CARPETA_SIN_ETAPA_FAM09")
    malos = fuentes_alteradas("calculo")
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam09.json; no se valida): %s" % malos[:5])
    for k, v in (ej.get("productos_sha256") or {}).items():
        if not k.startswith(rel(nueva) + "/testigo/audit/"):
            need(sha_archivo(BASE / k) == v, "PRODUCTO_CAMBIADO_DESDE_LA_ETAPA: %s" % k)
    r = {"comando": "fam09-validar", "naturaleza": "validación sin cálculo con el verificador histórico de la etapa", "tarea": tarea,
         "operacion": OPERACION_DE[tarea], "origen": rel(nueva)}
    if tarea == "HIST":
        r.update(_validar_hist(nueva))
    elif tarea == "TESTIGO":
        r.update(_validar_testigo(nueva, ej))
    else:
        need(not _paper2b_cargado(), "PAPER2B_PRECARGADO")
        if tarea in ("INCORPORACION", "C5B"):
            fijar_enlace(leer(nueva / ("ENLACE_T8_TESTIGO.json" if tarea == "INCORPORACION" else "ENLACE_T8_C5B.json")))
            mods = preparar("LECTOR") if tarea == "INCORPORACION" else {}
            mods.update(preparar(tarea))
        else:
            ENTRADAS9.clear()
            ENTRADAS9.update(ej.get("entradas9") or {})
            mods = preparar(tarea)
        rc, ver, stdout, exc, vf = _verificar(tarea, nueva, mods)
        (nueva / "verificar_stdout.txt").write_text(stdout, encoding="utf-8")
        pp = nueva / "producto" / PRODUCTO[tarea]
        vd = leer(vf) if vf.is_file() else {}
        r.update({"guion": GUIONES[tarea][1], "rc": rc, "veredicto": ver, "excepcion": exc, "verificacion_sha256": sha_archivo(vf) if vf.is_file() else None,
                  "conforme": vd.get("conforme"), "fallos": vd.get("fallos"), "productos_sha256": {rel(pp): sha_archivo(pp)} if pp.is_file() else {},
                  "aceptada": exc is None and rc == 0 and vd.get("conforme") is True})
        if tarea == "INCORPORACION" and r["aceptada"]:
            r.update(_registro_ledger(nueva, vf, pp))
    informe = rastro.informe()
    r["lecturas"] = lecturas(rastro, informe, ("referencias/fam09/",))
    r["aceptada"] = bool(r.get("aceptada")) and not r["lecturas"]["fuera_del_paquete_y_del_interprete"]
    r["segundos"] = round(time.time() - t0, 3)
    return r


def _registro_ledger(nueva: Path, vf: Path, pp: Path) -> dict:
    """Campos del registro de validación que ocupa el ledger rem144 para conexion_c5b (ENLACE-C5B-v1)."""
    ls = lineas(pp.read_bytes())
    pend = []
    for ln in ls:
        f = json.loads(ln)
        c = f.get("captura_c2")
        if isinstance(c, dict) and c.get("estado_candidato") == "pendiente":
            pend.append({"row": f["fila_anexo"], "row_key": f["clave_fila"], "destination_run": f["run_id"],
                         "required_exact": str(Fraction(f["historico"]["fin_por_unidad"]["value"])), "product_line_sha256": sha(ln + b"\n"),
                         "classification": "pendiente"})
    return {"kind": KIND_LEDGER, "oficial": False, "inventory_sha256": sha_archivo(vf), "product_sha256": sha_archivo(pp), "pending_rows": pend,
            "papel": "registro de validación local que ocupa el registro aceptado rem144 en conexion_c5b (no es un acto de Codex)"}


def _validar_hist(nueva: Path) -> dict:
    filas = anexo()
    pres = leer_jsonl(nueva / "FILAS_PRESERVADAS.jsonl")
    esperado = [i for i, a in enumerate(filas) if not a["estado_es_por_unidad"]]
    ok = ([x["fila"] for x in pres] == esperado and all(x["clave_fila"] == clave_fila(filas[x["fila"]]) and x["historico_sha256"] == sha(canon(filas[x["fila"]]))
                                                       for x in pres))
    return {"rc": 0 if ok else 4, "veredicto": {"preservadas": len(pres), "recuento_independiente": len(esperado)},
            "productos_sha256": {rel(nueva / "FILAS_PRESERVADAS.jsonl"): sha_archivo(nueva / "FILAS_PRESERVADAS.jsonl"),
                                 rel(nueva / "HIST.json"): sha_archivo(nueva / "HIST.json")}, "aceptada": ok}


def _validar_testigo(nueva: Path, ej: dict) -> dict:
    """U36: validar_testigo.py (69989e41…, sin cambios) sobre los bytes NUEVOS; si cumple, estado de la ejecución e inventario de la entrega."""
    need(not _paper2b_cargado(), "PAPER2B_PRECARGADO: la validación del testigo usa el núcleo lima1855 en un proceso propio")
    d = nueva / "testigo"
    s = d / SALIDA_TESTIGO
    need(not (s / "VALIDACION.json").exists() and not (d / "audit").exists(), "ENTREGA_YA_VALIDADA (una sola validación)")
    mods = preparar("TESTIGO")
    rc, ver, stdout, exc = _ejecutar(_c(TESTIGO, "validar_testigo.py"),
                                     [R9, BASE / MAN["TESTIGO"][0], s, "--modo", "produccion", "--alcance", d / "alcance" / DECLARACION], mods)
    (nueva / "validar_stdout.txt").write_text(stdout, encoding="utf-8")
    vf = s / "VALIDACION.json"
    vd = leer(vf) if vf.is_file() else {}
    ok = exc is None and rc == 0 and vd.get("clase") == "complete" and vd.get("cumple_garantia") is True and not vd.get("fallos")
    out = {"guion": _c(TESTIGO, "validar_testigo.py"), "u36": "validar_testigo.py ejecutado HOY sobre los bytes nuevos (no solo cotejo de VALIDACION.json)",
           "rc": rc, "veredicto": ver, "excepcion": exc, "validacion_sha256": sha_archivo(vf) if vf.is_file() else None,
           "resultado_sha256": sha_archivo(s / "RESULTADO.json") if (s / "RESULTADO.json").is_file() else None,
           "filas_cuya_mitad_superior_cubriria": vd.get("filas_cuya_mitad_superior_cubriria"), "aceptada": ok}
    if ok:
        _escribir_x(d / ("testigo_estado_%s.json" % ETIQUETA_TESTIGO),
                    {"kind": "estado-ejecucion-limpia-testigo-fam09", "estado_final": "completo", "rc_final_esperado": 0, "cierre_conforme": True,
                     "rc_trabajador": ej.get("rc"), "rc_validador": rc, "etiqueta": ETIQUETA,
                     "nota": "estado de la ejecución local (fam09-etapa TESTIGO + fam09-validar); ocupa el estado de la receta histórica"})
        files = {p.relative_to(d).as_posix(): {"sha256": sha_archivo(p), "bytes": p.stat().st_size} for p in sorted(d.rglob("*")) if p.is_file()}
        (d / "audit").mkdir()
        _escribir_x(d / "audit" / "entrega.json", {"kind": "inventario-entrega-local-fam09", "base": rel(d), "files": files})
        out["inventario_sha256"] = sha_archivo(d / "audit" / "entrega.json")
        out["productos_sha256"] = {rel(d / "audit" / "entrega.json"): out["inventario_sha256"], rel(s / "RESULTADO.json"): out["resultado_sha256"],
                                   rel(vf): out["validacion_sha256"]}
        out["papel"] = ("registro de validación de la entrega nueva: cita el inventario %s y el RESULTADO %s; la incorporación lo usa como «dictamen» "
                        "(PROCEDENCIA-LOCAL-v1). No es un dictamen de Codex." % (out["inventario_sha256"], out["resultado_sha256"]))
    return out


# ================================================================================================ comparación
def _hojas(o, pre=""):
    if isinstance(o, dict):
        out = {}
        for k, v in o.items():
            out.update(_hojas(v, pre + "." + str(k) if pre else str(k)))
        return out
    return {pre: o}


def _dif(a, b) -> list:
    ha, hb = _hojas(a), _hojas(b)
    return sorted(k for k in set(ha) | set(hb) if canon(ha.get(k, "<ausente>")) != canon(hb.get(k, "<ausente>")))


def _vista(p: Path) -> tuple:
    raw = Path(p).read_bytes()
    ls = lineas(raw)
    return raw, ls, [json.loads(x) for x in ls]


def estado_vigente(f: dict) -> str:
    if f["tipo"] == "definitivo_almacenado":
        return f["estado_sucesor"]
    if f["tipo"] == "lambda_candidato_por_demostracion":
        return f["clasificacion_derivada"]
    c = f.get("captura_c2")
    if isinstance(c, dict):
        return c.get("clasificacion_derivada") or "pendiente"
    return "pendiente"


def particion(filas: list) -> dict:
    cap = [f for f in filas if f["tipo"] == "captura_pendiente_sin_soporte_C2"]
    tipos = Counter((f.get("captura_c2") or {}).get("tipo_prueba") for f in cap if isinstance(f.get("captura_c2"), dict))
    pend = [f["fila_anexo"] for f in cap if estado_vigente(f) == "pendiente"]
    return {"filas": len(filas), "claves_unicas": len({f["clave_fila"] for f in filas}),
            "por_tipo": dict(sorted(Counter(f["tipo"] for f in filas).items())),
            "captura_por_prueba": dict(sorted((str(k), v) for k, v in tipos.items())), "pendientes": sorted(pend),
            "outside_support_vigentes": sum(1 for f in filas if estado_vigente(f) == "outside_support"),
            "outside_support_historicas": sum(1 for f in filas if (f.get("historico") or {}).get("outside_support") is True),
            "estado_vigente": dict(sorted(Counter(estado_vigente(f) for f in filas).items()))}


def transicion(anterior: list, nueva: list, objetivo: list) -> dict:
    """Filas por clave: las de `objetivo` (índices del anexo) deben cambiar; todas las demás, idénticas (líneas)."""
    a = {json.loads(x)["clave_fila"]: x for x in anterior}
    b = {json.loads(x)["clave_fila"]: x for x in nueva}
    fila = {k: json.loads(v)["fila_anexo"] for k, v in b.items()}
    cambiadas = sorted(fila[k] for k in b if k in a and a[k] != b[k])
    return {"filas_anterior": len(anterior), "filas_nueva": len(nueva), "claves_iguales": set(a) == set(b), "omitidas": len(set(a) - set(b)),
            "ajenas": len(set(b) - set(a)), "cambiadas": len(cambiadas), "cambiadas_son_las_esperadas": cambiadas == sorted(objetivo),
            "identicas": sum(1 for k in b if k in a and a[k] == b[k]), "orden_igual": [json.loads(x)["clave_fila"] for x in anterior] == [json.loads(x)["clave_fila"] for x in nueva]}


def comparar(tarea: str, nueva: Path, validacion: Path | None) -> dict:
    """fam09-comparar: SIN CÁLCULO; la referencia se lee solo aquí, después del cálculo y de su validación."""
    t0 = time.time()
    nueva = Path(nueva).resolve()
    ej = leer(nueva / "ejecucion.json")
    need(ej.get("etiqueta") == ETIQUETA and ej.get("tarea") == tarea, "CARPETA_DE_OTRA_ETAPA")
    val = registro_aceptado(Path(validacion), tarea, nueva) if validacion is not None else None
    r = {"comando": "fam09-comparar", "tarea": tarea, "operacion": OPERACION_DE[tarea], "origen": rel(nueva),
         "validacion": rel(Path(validacion)) if validacion is not None else None, "validada": val is not None}
    if tarea == "HIST":
        h = leer(nueva / "HIST.json")
        r["hist"] = {k: h[k] for k in ("filas_anexo", "preservadas", "claves_unicas", "outside_support_historicas", "outside_support_preservadas",
                                        "preservadas_por_estado", "coherencia_bandera_estado")}
        lb = fuentes()["libros"]["rem138"]["accepted_counts"]
        r["frente_al_libro"] = {"previous_definitive_preserved": (h["preservadas"], lb["previous_definitive_preserved"]),
                                "total_rows": (h["filas_anexo"], lb["total_rows"]), "outside_support_historicas": (h["outside_support_historicas"], ESPERADO["outside_support_historicas"])}
        ok = all(a == b for a, b in r["frente_al_libro"].values()) and h["claves_unicas"] == ESPERADO["filas"]
    elif tarea == "TESTIGO":
        r.update(_comparar_testigo(nueva))
        ok = r["cientificos_iguales"] and r["validacion_igual"] and r["referencia"]["C2_igual"] and r["referencia"]["tau_iguales"]
    else:
        r.update(_comparar_vista(tarea, nueva, ej))
        ok = r["cumple"]
    r["estado"] = {"calculo_o_regeneracion": "hecho" if ej.get("exito") else "fallido", "validacion": "aceptada" if val else "ausente",
                   "reproduccion": "aceptada" if ok and val is not None and ej.get("exito") else "no_aceptada"}
    r["segundos"] = round(time.time() - t0, 3)
    return r


def _comparar_testigo(nueva: Path) -> dict:
    s = nueva / "testigo" / SALIDA_TESTIGO
    rn, rr = leer(s / "RESULTADO.json"), leer(REF / "rem141" / SALIDA_TESTIGO / "RESULTADO.json")
    vn, vr = leer(s / "VALIDACION.json"), leer(REF / "rem141" / SALIDA_TESTIGO / "VALIDACION.json")
    dr = _dif(rn, rr)
    loc = [k for k in dr if any(k == x or k.startswith(x + ".") for x in LOCALES_RESULTADO)]
    cie = [k for k in dr if k not in loc]
    dv = _dif(vn, vr)
    locv = [k for k in dv if any(k == x or k.startswith(x + ".") for x in LOCALES_VALIDACION)]
    campos = ("C2", "sup_lower", "sup_upper", "sup_R", "numerical_error_share", "numerical_error_R", "B_pot", "error_kind", "computation_status",
              "converged", "attained", "sup_not_attained", "tau_d_at_sup", "tau_f_at_sup", "final_n")
    return {"resultado_sha256": sha_archivo(s / "RESULTADO.json"), "resultado_referencia_original": ACEPTADO["TESTIGO"],
            "campos": {k: {"nuevo": rn.get(k), "referencia": rr.get(k), "igual": canon(rn.get(k)) == canon(rr.get(k))} for k in campos},
            "garantia": {"nueva": vn.get("cumple_garantia"), "referencia": vr.get("cumple_garantia"), "clase": [vn.get("clase"), vr.get("clase")]},
            "diferencias_locales_resultado": loc, "diferencias_cientificas_resultado": cie, "cientificos_iguales": not cie,
            "diferencias_locales_validacion": locv, "diferencias_validacion": [k for k in dv if k not in locv], "validacion_igual": not [k for k in dv if k not in locv],
            "referencia": {"C2_igual": rn.get("C2") == REF_TESTIGO["C2"], "tau_iguales": rn.get("tau_d_at_sup") == rn.get("tau_f_at_sup") == 0.6},
            "valores_locales": {k: _hojas(rn).get(k) for k in ("inicio_utc", "fin_utc", "pared_s", "puerta.alcance_sha256", "evidencia_real.ejecutable")}}


def _comparar_vista(tarea: str, nueva: Path, ej: dict) -> dict:
    pp = nueva / "producto" / PRODUCTO[tarea]
    raw, ls, filas = _vista(pp)
    out = {"producto_sha256": sha(raw), "aceptado_sha256": ACEPTADO[tarea], "bytes_identicos_al_aceptado": sha(raw) == ACEPTADO[tarea],
           "particion": particion(filas) if tarea != "LAMBDA" else None}
    if tarea == "LAMBDA":
        rs = leer(nueva / "producto" / "PRODUCTO_RESUMEN.json")["resumen"]
        lb = fuentes()["libros"]["rem138"]["accepted_counts"]
        out["recuento"] = rs
        out["frente_al_libro"] = {"lambda_finalizadas": (rs["lambda_finalizadas"], lb["new_lambda_finalized"]),
                                  "lambda_outside_support": (rs["lambda_outside_support"], lb["lambda_outside_support"]),
                                  "lambda_computed": (rs["lambda_computed"], lb["lambda_computed"]), "cambios": (rs["cambios"], lb["changed_classifications"]),
                                  "definitivas_preservadas": (rs["definitivas_preservadas"], lb["previous_definitive_preserved"]),
                                  "captura_pendiente": (rs["captura_pendiente"], lb["capture_pending"])}
        out["cumple"] = out["bytes_identicos_al_aceptado"] and all(a == b for a, b in out["frente_al_libro"].values())
        return out
    ant = {"CAPTURA": ("lambda", "LAMBDA"), "INCORPORACION": ("captura", "CAPTURA"), "C5B": ("testigo_vista", "INCORPORACION")}[tarea]
    pa = BASE / next(iter(ej["entradas"][ant[0]]["productos_sha256"]))
    raw_a = pa.read_bytes()
    obj = {"CAPTURA": None, "INCORPORACION": FILAS_TESTIGO, "C5B": FILAS_C5B}[tarea]
    if tarea == "CAPTURA":   # las 2.111 seleccionadas cambian: 2.071 resueltas y 40 con su pendiente anotado (captura_c2.estado_candidato)
        obj = [f["fila_anexo"] for f in filas if f["tipo"] == "captura_pendiente_sin_soporte_C2"]
    out["transicion"] = transicion(lineas(raw_a), ls, obj)
    out["transicion"]["entrada"] = rel(pa)
    p = out["particion"]
    if tarea == "CAPTURA":
        lb = fuentes()["libros"]["rem140"]["accepted_counts"]
        pc = p["captura_por_prueba"]
        res = [f for f in filas if f["tipo"] == "captura_pendiente_sin_soporte_C2" and f["captura_c2"]["estado_candidato"] != "pendiente"]
        h_lam = sha(raw_a)
        out["procedencia_por_resolucion"] = {
            "resueltas": len(res), "con_tipo_y_huella_de_prueba": sum(1 for f in res if f["captura_c2"].get("tipo_prueba") and f["captura_c2"].get("prueba_sha256")),
            "ligadas_al_lambda_nuevo": sum(1 for f in res if f["captura_c2"]["procedencia"].get("base_lambda_sha256") == h_lam),
            "con_las_cinco_huellas": sum(1 for f in res if all(f["captura_c2"]["procedencia"].get(k) for k in
                                                                ("base_lambda_sha256", "certificacion_sha256", "fuentes_sha256", "plan_sha256", "pruebas_sha256"))),
            "pendientes_sin_prueba": sum(1 for f in filas if f["tipo"] == "captura_pendiente_sin_soporte_C2" and f["captura_c2"]["estado_candidato"] == "pendiente"
                                         and f["captura_c2"]["prueba_sha256"] is None and f["captura_c2"]["causa_pendiente"] == "SIN_PRUEBA_POR_FILA")}
        pr_ = out["procedencia_por_resolucion"]
        out["frente_al_libro"] = {"resueltas": (len(res), lb["new_capture_finalized"]), "pendientes": (len(p["pendientes"]), lb["capture_pending"]),
                                  "misma_corrida": (pc.get("pertenencia_misma_corrida"), lb["computed_same_run"]),
                                  "transferidas": (pc.get("pertenencia_transferida"), lb["computed_transferred"]),
                                  "outside_33_10": (pc.get("exclusion_cota_33_10"), lb["outside_33_10"]), "outside_U": (pc.get("exclusion_cota_U"), lb["outside_U"])}
        out["cumple"] = (out["bytes_identicos_al_aceptado"] and all(a == b for a, b in out["frente_al_libro"].values()) and _transicion_ok(out["transicion"])
                         and pr_["resueltas"] == pr_["con_tipo_y_huella_de_prueba"] == pr_["ligadas_al_lambda_nuevo"] == pr_["con_las_cinco_huellas"]
                         == ESPERADO["captura_resueltas"] and pr_["pendientes_sin_prueba"] == 40)
        return out
    ref = {f["clave_fila"]: (ln, f) for ln, f in zip(*_vista(REF / "rem147" / "VISTA_T8_CAPTURA.jsonl")[1:])}
    nuevas = {f["clave_fila"]: (ln, f) for ln, f in zip(ls, filas)}
    iguales, vinc, cien, ausentes = 0, {}, {}, []
    for k, (ln, f) in nuevas.items():
        if k not in ref:
            ausentes.append(f["fila_anexo"])
            continue
        if tarea == "INCORPORACION" and f["fila_anexo"] in FILAS_C5B:
            continue
        if ln == ref[k][0]:
            iguales += 1
            continue
        permitidos = VINCULOS_TESTIGO if f["fila_anexo"] in FILAS_TESTIGO else VINCULOS_C5B if f["fila_anexo"] in FILAS_C5B else ()
        d = _dif(f, ref[k][1])
        for x in d:
            (vinc if x in permitidos else cien).setdefault(x, []).append(f["fila_anexo"])
    out["frente_a_rem147"] = {"referencia_sha256": sha_archivo(REF / "rem147" / "VISTA_T8_CAPTURA.jsonl"), "claves_iguales": set(ref) == set(nuevas),
                              "lineas_identicas": iguales, "claves_ausentes": ausentes,
                              "diferencias_de_vinculo": {k: len(v) for k, v in sorted(vinc.items())},
                              "filas_con_vinculos_distintos": sorted({i for v in vinc.values() for i in v}),
                              "diferencias_cientificas": {k: v[:10] for k, v in sorted(cien.items())},
                              "comparadas_aparte": FILAS_C5B if tarea == "INCORPORACION" else []}
    out["vinculos_derivados"] = _vinculos(tarea, nueva, ej, nuevas)
    if tarea == "C5B":
        out["hist"] = _preservadas(filas)
        out["recuentos"] = {"outside_support_historicas": p["outside_support_historicas"], "outside_support_vigentes": p["outside_support_vigentes"],
                            "diferencia": p["outside_support_historicas"] - p["outside_support_vigentes"],
                            "esperado": {k: ESPERADO[k] for k in ("outside_support_historicas", "outside_support_vigentes", "diferencia_captura", "diferencia_lambda")},
                            "explicacion": _explicar_outside(filas)}
        pc = p["captura_por_prueba"]
        part = {"preservadas": p["por_tipo"].get("definitivo_almacenado", 0), "lambda": p["por_tipo"].get("lambda_candidato_por_demostracion", 0),
                "captura": sum(pc.get(k, 0) for k in ("pertenencia_misma_corrida", "pertenencia_transferida", "exclusion_cota_33_10", "exclusion_cota_U")),
                "testigo": pc.get("pertenencia_testigo_alto", 0), "c5b": pc.get("exclusion_cota_U_global", 0), "pendientes": len(p["pendientes"])}
        part["total"] = sum(v for k, v in part.items() if k != "pendientes")
        cat = sorted({a["result_status"] for a in anexo()})
        out["particion_por_operacion"] = {"recontada_desde_las_filas": part, "esperada": {"preservadas": ESPERADO["hist"], "lambda": ESPERADO["lambda"],
                                          "captura": ESPERADO["captura_resueltas"], "testigo": ESPERADO["testigo"], "c5b": ESPERADO["c5b"], "pendientes": 0,
                                          "total": ESPERADO["filas"]},
                                          "testigo_son_las_35": sorted(f["fila_anexo"] for f in filas if (f.get("captura_c2") or {}).get("tipo_prueba") == "pertenencia_testigo_alto") == FILAS_TESTIGO,
                                          "c5b_son_las_5": sorted(f["fila_anexo"] for f in filas if (f.get("captura_c2") or {}).get("tipo_prueba") == "exclusion_cota_U_global") == FILAS_C5B,
                                          "categorias_vigentes": sorted(p["estado_vigente"]), "categorias_originales_del_anexo": cat,
                                          "categorias_conservadas": set(p["estado_vigente"]) <= set(cat)}
        pp_ = out["particion_por_operacion"]
        pp_["cumple"] = (pp_["recontada_desde_las_filas"] == pp_["esperada"] and pp_["testigo_son_las_35"] and pp_["c5b_son_las_5"] and pp_["categorias_conservadas"])
    out["cumple"] = (_transicion_ok(out["transicion"]) and out["frente_a_rem147"]["claves_iguales"] and not cien and not ausentes
                     and all(v["igual"] for v in out["vinculos_derivados"].values())
                     and (tarea != "C5B" or (out["bytes_identicos_al_aceptado"] or set(out["frente_a_rem147"]["filas_con_vinculos_distintos"]) <= set(FILAS_TESTIGO + FILAS_C5B))
                          and out["hist"]["identicas"] == 9434 and not p["pendientes"]
                          and out["recuentos"]["outside_support_historicas"] == ESPERADO["outside_support_historicas"]
                          and out["recuentos"]["outside_support_vigentes"] == ESPERADO["outside_support_vigentes"]
                          and out["recuentos"]["explicacion"]["cumple"] and out["particion_por_operacion"]["cumple"]))
    return out


def _transicion_ok(t: dict) -> bool:
    return t["claves_iguales"] and not t["omitidas"] and not t["ajenas"] and t["cambiadas_son_las_esperadas"] and t["orden_igual"]


def _preservadas(filas: list) -> dict:
    """Identidad de las filas preservadas de la vista final frente a F09-HIST (mismo recuento desde el anexo, sin leer la salida HIST)."""
    an = anexo()
    pres = [i for i, a in enumerate(an) if not a["estado_es_por_unidad"]]
    por = {f["fila_anexo"]: f for f in filas}
    ident = sum(1 for i in pres if por.get(i, {}).get("tipo") == "definitivo_almacenado" and por[i].get("clave_fila") == clave_fila(an[i])
                and canon(por[i].get("historico")) == canon(an[i]) and por[i].get("estado_sucesor") == an[i]["result_status"] and por[i].get("preservada") is True)
    return {"preservadas_en_el_anexo": len(pres), "identicas": ident}


def _explicar_outside(filas: list) -> dict:
    """5.580 históricas - 4.549 vigentes: filas que dejan outside_support (histórico true, vigente distinto) por etapa."""
    sale = [f for f in filas if (f.get("historico") or {}).get("outside_support") is True and estado_vigente(f) != "outside_support"]
    entra = [f for f in filas if (f.get("historico") or {}).get("outside_support") is not True and estado_vigente(f) == "outside_support"]
    por = Counter("captura" if f["tipo"] == "captura_pendiente_sin_soporte_C2" else "lambda" if f["tipo"] == "lambda_candidato_por_demostracion" else f["tipo"]
                  for f in sale)
    pe = Counter("captura" if f["tipo"] == "captura_pendiente_sin_soporte_C2" else "lambda" if f["tipo"] == "lambda_candidato_por_demostracion" else f["tipo"]
                 for f in entra)
    neto = {k: por.get(k, 0) - pe.get(k, 0) for k in sorted(set(por) | set(pe))}
    return {"dejan_outside_support": dict(sorted(por.items())), "pasan_a_outside_support": dict(sorted(pe.items())), "neto": neto,
            "cumple": neto.get("captura") == ESPERADO["diferencia_captura"] and neto.get("lambda") == ESPERADO["diferencia_lambda"]
                      and sum(neto.values()) == ESPERADO["outside_support_historicas"] - ESPERADO["outside_support_vigentes"]}


def _vinculos(tarea: str, nueva: Path, ej: dict, nuevas: dict) -> dict:
    """Los campos de vínculo de las filas emitidas apuntan exactamente a las salidas nuevas (derivados de sus bytes)."""
    out = {}
    if tarea == "INCORPORACION":
        en = leer(nueva / "ENLACE_T8_TESTIGO.json")["autoridad"]
        f = next(f for _, f in nuevas.values() if f["fila_anexo"] == FILAS_TESTIGO[0])
        pr = f["captura_c2"]["procedencia"]
        ts = pr["testigo_superior"]
        tdir = BASE / ej["entradas"]["testigo"]["carpeta"]
        out = {"incorporacion": {"igual": pr["incorporacion_sha256"] == en["incorporacion"]["sha256"] == sha_archivo(BASE / en["incorporacion"]["ruta"])},
               "resultado": {"igual": ts["resultado_sha256"] == sha_archivo(tdir / "testigo" / SALIDA_TESTIGO / "RESULTADO.json")},
               "inventario": {"igual": ts["fuente_inventario_sha256"] == sha_archivo(tdir / "testigo" / "audit" / "entrega.json")},
               "alcance": {"igual": ts["alcance_origen_sha256"] == sha_archivo(DATOS / DECLARACION)},
               "evidencia": {"igual": pr["evidencia_filas_sha256"] == sha_archivo(nueva / "lectura" / "EVIDENCIA_CANDIDATA_FILAS.jsonl")},
               "aceptacion_local": {"igual": pr["aceptacion_sha256"] == sha_archivo(nueva / "ACEPTACION_TESTIGO_FAM09.json")},
               "registro_validacion": {"igual": pr["dictamen_sha256"] == sha_archivo(BASE / ej["entradas"]["testigo"]["registro_validacion"])},
               "sin_decision": {"igual": ts["decision_origen_uuid"] is None},
               "prueba_sha256": {"igual": all(f2["captura_c2"]["prueba_sha256"] == sha(canon(f2["captura_c2"]["prueba"]))
                                              for _, f2 in nuevas.values() if f2["fila_anexo"] in FILAS_TESTIGO)}}
    elif tarea == "C5B":
        f = next(f for _, f in nuevas.values() if f["fila_anexo"] == FILAS_C5B[0])
        pr = f["captura_c2"]["procedencia"]
        e = ej["entradas"]["testigo_vista"]
        vista = BASE / next(iter(e["productos_sha256"]))
        out = {"vista_base": {"igual": pr["base_vista_sha256"] == sha_archivo(vista)},
               "verificacion_base": {"igual": pr["base_vista_inventario_sha256"] == sha_archivo(vista.parent / "VERIFICACION.json")},
               "registro_de_la_vista": {"igual": pr["ledger_sha256"] == sha_archivo(BASE / e["registro_validacion"])},
               "certificado_reutilizado": {"igual": pr["prueba_c5b"]["certificado_sha256"] == "fc403d40b1eb6ba50e5f8dc551ecd301b19b1092e15c5e50ff4e163fc51afa16"}}
    return out


# ================================================================================================ comprobación y receta
def comprobar() -> dict:
    t0 = time.time()
    malos = fuentes_alteradas("todo")
    out = {"comando": "fam09-comprobar", "calculo": "ninguno", "fuentes": {"piezas": len(piezas()), "alteradas": malos}}
    out["sustituciones"] = sustituciones_ok()
    try:       # la regla de la declaración carga el manifiesto del testigo y el núcleo: una pieza ausente se informa, no interrumpe
        hdec, _ = declaracion()
        out["declaracion"] = {"sha256": hdec, "conforme": True}
    except Exception as e:  # noqa: BLE001
        out["declaracion"] = {"conforme": False, "error": _sin_base("%s: %s" % (type(e).__name__, e))[:240]}
    try:
        out["pilotos"] = {"conforme": (DATOS / "pilotos.json").read_bytes() == (json.dumps(regla_pilotos(), ensure_ascii=False, indent=1, sort_keys=True) + "\n").encode("utf-8")}
    except Exception as e:  # noqa: BLE001
        out["pilotos"] = {"conforme": False, "error": _sin_base("%s: %s" % (type(e).__name__, e))[:240]}
    fu = fuentes()
    out["referencias"] = {x["archivo"]: sha_archivo(BASE / x["archivo"]) == x["sha256"] for x in fu["archivos"] if x["archivo"].startswith("referencias/fam09/")}
    out["libros"] = {k: {"presente": v.get("presente"), "product_sha256": v.get("product_sha256") or v.get("result_sha256")} for k, v in fu["libros"].items()}
    out["autoridad_extraida"] = sorted(fu["solo_procedencia"])
    out["receta"] = {"pasos": len(receta()["pasos"])}
    out["cumple"] = (not malos and all(v is True for v in out["sustituciones"].values()) and out["declaracion"]["conforme"] and out["pilotos"]["conforme"]
                     and all(out["referencias"].values()))
    out["segundos"] = round(time.time() - t0, 3)
    return out


def receta() -> dict:
    py = "<python de .venv-fam01> -B -P -s -X utf8 reproducir.py"
    s = "salidas/fam09/"
    sup = "<supervisar.py del paquete fuente> TESTIGO 600 <registro> --cwd <base> -- " + py
    pasos = [
        {"paso": "listar", "orden": py + " fam09-listar --salida " + s + "listar.json", "calculo": "ninguno (fija pilotos.json y la declaración)"},
        {"paso": "comprobar", "orden": py + " fam09-comprobar --salida " + s + "comprobar.json", "calculo": "ninguno"},
        {"paso": "HIST", "orden": py + " fam09-etapa --tarea HIST --salida " + s + "hist"},
        {"paso": "HIST-validar", "orden": py + " fam09-validar --nueva " + s + "hist --salida " + s + "hist.validacion.json"},
        {"paso": "LAMBDA", "orden": py + " fam09-etapa --tarea LAMBDA --salida " + s + "lambda"},
        {"paso": "LAMBDA-validar", "orden": py + " fam09-validar --nueva " + s + "lambda --salida " + s + "lambda.validacion.json"},
        {"paso": "CAPTURA", "orden": py + " fam09-etapa --tarea CAPTURA --entrada lambda=" + s + "lambda --entrada validacion_lambda=" + s
         + "lambda.validacion.json --salida " + s + "captura"},
        {"paso": "CAPTURA-validar", "orden": py + " fam09-validar --nueva " + s + "captura --salida " + s + "captura.validacion.json"},
        {"paso": "TESTIGO (cálculo, 600 s)", "orden": sup + " fam09-etapa --tarea TESTIGO --salida " + s + "testigo"},
        {"paso": "TESTIGO-validar (U36)", "orden": py + " fam09-validar --nueva " + s + "testigo --salida " + s + "testigo.validacion.json"},
        {"paso": "INCORPORACION (emisión de 35 filas)", "orden": py + " fam09-etapa --tarea INCORPORACION --entrada captura=" + s + "captura --entrada "
         "validacion_captura=" + s + "captura.validacion.json --entrada testigo=" + s + "testigo --entrada validacion_testigo=" + s
         + "testigo.validacion.json --salida " + s + "incorporacion"},
        {"paso": "INCORPORACION-validar", "orden": py + " fam09-validar --nueva " + s + "incorporacion --salida " + s + "incorporacion.validacion.json"},
        {"paso": "C5B", "orden": py + " fam09-etapa --tarea C5B --entrada testigo_vista=" + s + "incorporacion --entrada validacion_testigo_vista=" + s
         + "incorporacion.validacion.json --salida " + s + "c5b"},
        {"paso": "C5B-validar", "orden": py + " fam09-validar --nueva " + s + "c5b --salida " + s + "c5b.validacion.json"}]
    for t in ETAPAS:
        pasos.append({"paso": t + "-comparar", "orden": py + " fam09-comparar --tarea %s --nueva %s%s --validacion %s%s.validacion.json --salida %s%s.comparacion.json"
                      % (t, s, t.lower(), s, t.lower(), s, t.lower())})
    return {"comando": "fam09-receta", "estado": "lista (no ejecuta nada)", "pasos": pasos,
            "cobertura": {"operaciones": sorted(OPERACIONES), "etapas": list(ETAPAS)},
            "nota": ("una invocación cada vez; el testigo bajo el supervisor con límite externo de 600 s; cada etapa consume la salida NUEVA de la "
                     "anterior con su registro de validación aceptado (--entrada clave=carpeta y validacion_clave=registro)")}
