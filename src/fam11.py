"""FAM11 (COV: phi/2 con las demás entradas del padre conservadas; COV12: B1 y B2 sobre las doce afirmaciones COL no decididas).

Operaciones del catálogo (no se confunden):
- F11-COV26 (RN): las seis tareas ABL-COV-T1…T6 por tarea_lote.py (26 techos certificados de rama y cota con conexion_coord_cert y el
  núcleo C0; aceptación en la escala NORMALIZADA, error_normalizado <= 1e-7; 8 techos tienen error_R > 1e-7 y no por eso se rechazan),
  el ensamblado de las 1.724 celdas (ensamblar_coord.py) y la conciliación COV de las 1.728 afirmaciones (src/conciliar_cov.py):
  1.693 inconclusa_preservada, 28 no_decidida_por_testigos, 3 parcial_no_robusta_factible y 4 parcial_no_robusta_infactible. Un cambio
  de signo certificado no es un cambio de categoría. La síntesis posterior P7/B2 no sustituye a esta conciliación.
- F11-B1 (RN): una solicitud c2_normalizado en la raíz D7 COV (diseño G, menú f): U_C2 = extremo superior CERTIFICADO del encierro con
  redondeo hacia afuera (0x1.628ed46d42e18p-3 en la referencia); no es un máximo. B1 solo produce candidatos (lectura candidato_B2).
- F11-B2 (RN): cota inferior global L_K1 de cada grupo K1…K6 con la forma acoplada, el intervalo q exacto y s_Pi (sin suponer el signo de
  n_min ni usar q.hi = 3 ingenuo); 4.608 contextos antes de deduplicar, 2.304 por grupo sumados, 1.920 efectivos, 480 puentes y 60 Q. Los
  seis grupos se solapan (K5 ⊂ K1∩K3; K6 ⊂ K2∩K4) y COL-2024p pertenece al soporte E2. Regla: G_hi = U_C2 − L_K1 <= −1/100 (borde
  incluido, exacta). Las categorías padre se conservan aparte de la conclusión transformada.
No se extiende a los 16 casos mexicanos, a causalidad ni a un orden de canales; la integración en la síntesis pertenece a FAM10.

Adaptaciones (no cambian fórmulas, claves, tolerancias, presupuestos, garantías ni criterios; cada original se sustituye una sola vez):
- GUION-v1: cada pieza de nucleo_s6/cov, nucleo_s6/b1, nucleo_s6/b2 y src/conciliar_cov.py se ejecuta desde sus bytes exactos con las
  sustituciones de SUSTITUCIONES; validar_coord_rec (COV) y comun_b1/puerta_b1, comun_b2/puerta_b2 se cargan como módulos desde su texto
  adaptado (MODULOS-v1) y las piezas que los importaban por nombre usan esos módulos.
- NUCLEO-C0-v1: el núcleo es nucleo_s6/c0 (FAM05). B1/B2 cargan su cierre C0 desde los bytes autenticados de nucleo_s6/c0/src/paper2b
  en un proceso propio (sin paper2b precargado ni buscadores ajenos); COV lo importa como FAM05–FAM08.
- RUTAS-FUENTES-v1: cada fuente que el código LEE sale de su copia en la base (tabla por clave o por ruta histórica) y se sigue
  autenticando por sus bytes; las fuentes de solo procedencia (libros, dictámenes, inventarios) no se leen al ejecutar (se autenticaron
  en la extracción) y una lectura no declarada falla.
- SANEADO-v1: las proyecciones saneadas (comun_b1/comun_b2, índices y manifiestos B1/B2, mapa derivado, censo) se autentican por la
  correspondencia proyección -> original (ORIGINAL) y la huella registrada es la del original. Los manifiestos B1/B2 se reconstruyen con
  los marcadores de la proyección en las rutas históricas (RAIZ-MARCADORES-v1: R y W son rutas puras con el marcador).
- PUERTA-v1: las puertas de producción (alcance verificado y decisión humana nativa) no se ejecutan ni se reconstruyen. El sha256 de la
  declaración datos/fam11/ejecucion_limpia.json (NO OFICIAL) ocupa el alcance de los trabajadores y validadores; no hay decisión.
- PROCEDENCIA-LOCAL-v1: B1/B2 no tienen área p3ctl: la fuente de ejecución es el registro local de fam11-unidad (ejecucion.json con la
  orden relativa, el código de salida y la última línea; trabajo_stdout.txt) y la validación solo se admite dentro de la misma unidad.
- PAQUETE-v1: B1/B2 comprueban solo sus cuatro piezas copiadas contra su índice (proyección -> original).
- ENLACE-B1-v1: B2 no usa el B1 histórico ni el libro rem167: consume los bytes del B1 NUEVO validado (registro de fam11-validar
  aceptado para esos mismos bytes y su revalidación en el mismo proceso con las funciones del validador B1, sin motor); el bloque «b1»
  del manifiesto B2 se reconstruye de ellos (MANIFIESTO_B2_ENLAZADO.json). Verifica la validación; no recalcula B1.
- ENSAMBLADOR-ENTRADAS-v1 (de FAM07): una carpeta declarada por tarea (guardada o nueva); ENTRADAS-CONCILIADOR-v1: el conciliador lee
  cada tarea desde la carpeta relativa a la base que registró el ensamblador.
- RELOJ-PILOTO-v1 (de FAM05): reloj interno COV = 2400 − 120 = 2280 s; el límite externo lo pone el supervisor.
"""
from __future__ import annotations

import builtins
import contextlib
import datetime as dt
import importlib.util
import io
import json
import re
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
F7 = _src("fam07")
F8 = _src("fam08")
sha, sha_archivo, leer, leer_jsonl, rel, F1 = F5.sha, F5.sha_archivo, F5.leer, F5.leer_jsonl, F5.rel, F5.F1
COV = BASE / "nucleo_s6" / "cov"
DATOS = BASE / "datos" / "fam11"
GUARD = DATOS / "guardadas" / "cov_rem151"
REF = BASE / "referencias" / "fam11"
CODIGO = {"nucleo_s6/cov/tarea_lote.py": "9ba4ce357423167dc34a2ae1c15517b053fd3e33f7fef3720d14f9941bd8d1b1",
          "nucleo_s6/cov/conexion_coord_cert.py": "e5776de970b72535ec7b72340604abfd9e8448479ea78dac4b714d870d273d61",
          "nucleo_s6/cov/validar_lote.py": "070ae81d15119735369b08bf083e9ff3b7652ca99a2956547b9f290db4022ee4",
          "nucleo_s6/cov/validar_coord_rec.py": "be36386430764fd9c1b487f0485e3c4fa3a0282edd7f4f18baa27e18a3a7bbe3",
          "nucleo_s6/cov/ensamblar_coord.py": "5115ba4eb430a0b09c65d7a6b9375a156e15aa376863c782e11648233d1e0c93",
          "src/conciliar_cov.py": "fef92f1c34b314021f0ecc3ff7f4a990686ff2f2c318c233968bc9dbe4ef7161",
          "nucleo_s6/b1/comun_b1.py": "076dbc26ef0546044f4d048b281bda466c9f2faca4d01799126b156423bb7f2c",
          "nucleo_s6/b1/puerta_b1.py": "a24bdb76c6af381236af544e2c2a678eddd76ac8abb1ba230b9c5f8fa69ba260",
          "nucleo_s6/b1/b1_trabajo.py": "2ddd202c6ef1cee2f15a0bfde4a561730586349f7677bbf423a5c9f4e43c7799",
          "nucleo_s6/b1/validar_b1.py": "a43114db4540c2ccf0627878f4d54559e3a97d44df6a9571285073834b10bacd",
          "nucleo_s6/b2/comun_b2.py": "105172d887de5b8d8f20963dd75fb32f9865b71170db635f11f6c62c966fce1d",
          "nucleo_s6/b2/puerta_b2.py": "1e43464b30fd0d79f91c02096f86b91e9ad3864c7f7ee7de575ec7244c6e2300",
          "nucleo_s6/b2/b2_trabajo.py": "3b9cb6c7c1c73f7a59fd4f5da0b5833bf5db2eef8e95bdbb70c51691398e00a1",
          "nucleo_s6/b2/validar_b2.py": "de51d0cf2f0ad7c8bf2a9cd855ccf568ff2c24c8a1ba77c5b4f2dc2add629be9"}
MAN_COV = ("cov/MANIFIESTO_ABL_COV.json", "a38f9e95b83af3fd921f240f26fd1d8a242f46009c770c5123a8b7c72932c9c3")
COB_COV = ("cov/COBERTURA_ABL_COV.json", "510201a8e593aa5a8f9fbf9592e376b4f5b975658d508b7e414625ecc7c6f5f5")
IDX_COV = ("cov/PAQUETE_ABL_COV.json", "cd197300152b73d391b2b9a223bd9585425618ae2a383df7004804a232e94ec1")
ENF_AF = ("cov/ENF_POR_AFIRMACION.jsonl", "e0670acc74ac1aaf92686b4fd207c11da1aa8636833b140e40c0a08ddc30ac3c")
ALC_COV = ("cov/alcance_cov.json", "69900e10f8e7b1ff9bb947fd1f8e54d53f1399d6344803e48b97d2bc997f0f89")
CONC_FUENTE = ("fuentes/CONCILIACION_COV.jsonl", "5ba0142304deb949777ad3ae3443556250f2237d214cb4e4fb0d427aa5ea049f")
CENSO = ("datos/fam08/CENSO_REMANENTE.json", "f9940081b3fca85a6641443a340bbb73b7be5119b83434d87d9aca98876dab08",
         "78e51627014c11778b5388ee9aaa07074b3a33fbade09b226bd49933aa5d3129")
# (archivo relativo a la base, sha256 de la proyección, sha256 del original)
MAN_B = {"B1": ("datos/fam11/b1/MANIFIESTO_B1.json", "b064ca43668a9012af30da0c5eaf57f3bf2388e11856ad1c8d94ef9b853b464a",
                "1194923c273da998db23a83700dac1669693490d01f7fc52668ae39c105fe33e"),
         "B2": ("datos/fam11/b2/MANIFIESTO_B2.json", "af2679ee6ff828bfc3d2f04d8771b93cb577679f004c23a0d06da6584d7f9926",
                "0f1582cc3718f2f5545ab4a112d108d7e4d4639505dec4826d21d22045664d7b")}
IDX_B = {"B1": ("nucleo_s6/b1/PAQUETE_B1.json", "9ad7e49232de6528681a365ec6473b0d565494c480353b22ff93bc5d3c87e5dd",
                "9244a279c4b5ede08b9a48b9f2f0ebe99a22ed91cd137b8ae24aa7ae4aa3f13d"),
         "B2": ("nucleo_s6/b2/PAQUETE_B2.json", "0113dfc6c65a019c187aea65f84ba6d162df41bd24e6c9e348d5b7adf7234203",
                "5f7ec64bc4027aa9dd2893042622a027a480ba410474d01041938cb56295f9de")}
COMUN_B = {"B1": ("nucleo_s6/b1/comun_b1.py", "076dbc26ef0546044f4d048b281bda466c9f2faca4d01799126b156423bb7f2c",
                  "25bf92ffcb13efd57af9a80336bf5f3374a823e0c364ef9c8943c774183ad5bf"),
           "B2": ("nucleo_s6/b2/comun_b2.py", "105172d887de5b8d8f20963dd75fb32f9865b71170db635f11f6c62c966fce1d",
                  "9035e3b19c152c2e68f8e0b65146187b964a1b37d9351ed06c4b64a7737da1a5")}
MAPA = ("datos/fam11/fuentes/MAPA_SOPORTE_REUTILIZACION.derivado.jsonl", "624d8fc665d225f9d62fe33ce86bf0cca4646b054999e32a7fc00cf2e81fa421",
        "92d5e082aa6d28e113fc16748998146bf999f3dcf07bf2a1184d6f68041eb502")
ORIGINAL_B = {x[1]: x[2] for x in list(MAN_B.values()) + list(IDX_B.values()) + list(COMUN_B.values()) + [MAPA]}
DECLARACION = "ejecucion_limpia.json"
DECLARACION_KIND = "declaracion-ejecucion-limpia-fam11"
ETIQUETA = "REPRODUCCION LIMPIA FAM11 NO OFICIAL"
TAREAS = tuple("ABL-COV-T%d" % i for i in range(1, 7))
T1 = TAREAS[0]
UNIDADES_B = ("B1", "B2")
ENSAMBLADO = "ENSAMBLADO"
PRODUCTOS = ("cov_techos.jsonl", "cov_comparacion.jsonl")
PRODUCTOS_ENS = ("cov_techos_ensamblados.jsonl", "cov_comparacion_ensamblada.jsonl")
PRODUCTOS_CONC = ("CONCILIACION_COV.jsonl", "CONCILIACION_COV.json")
GUARDADO = "guardado"
REGENERACION = "regeneración sobre entradas guardadas"
MIXTA = "conexión mixta (salidas nuevas y entradas guardadas)"
NUEVA = "sobre salidas nuevas"
EPS = Fraction(1, 100)
U_C2_HEX = "0x1.628ed46d42e18p-3"
GRUPOS = ("K1", "K2", "K3", "K4", "K5", "K6")
OPERACIONES = {"F11-COV26": "ABL-COV-T1…T6 (26 techos certificados de phi/2), ensamblado de 1.724 celdas y conciliación de 1.728 afirmaciones",
               "F11-B1": "una solicitud c2_normalizado sobre la raíz D7 COV: U_C2 (cota superior certificada) y lectura de seis grupos/doce afirmaciones",
               "F11-B2": "L_K1 global de K1…K6 (forma acoplada, q exacto, s_Pi; 1.920 contextos, 480 puentes, 60 Q) y G_hi = U_C2 − L_K1"}
ACEPTADO = {   # referencias (catálogo; ENSAMBLADO.json es la proyección del catálogo, original 1f0eb893…)
    "ensamblado": {"cov_techos_ensamblados.jsonl": "0bae15d406b24773e2ff66c0765a777e0787bff90beb90da21af9927f70de676",
                   "cov_comparacion_ensamblada.jsonl": "cad40d17bb55074dd167e756f6dc32cbe35eefdef3ac56ba796dd9a5e94d8a80"},
    "ensamblado_json": ("cdd71ebc22f340a87da177a92dac718993230d5f6c2334314df017275276b336", "1f0eb893ab4184ed9cf597fe5cec0f68b51a5a9f11f8dcdae84978caa4ae11f4"),
    "conciliacion": {"CONCILIACION_COV.jsonl": "5ba0142304deb949777ad3ae3443556250f2237d214cb4e4fb0d427aa5ea049f",
                     "CONCILIACION_COV.json": "927e77aaefd24f27f9d50dfbfaf3d6eb3274db0a22d43cac502be24ed211a9e2"}}
REF_ENS = REF / "rem151" / "ENSAMBLADO"
REF_CONC = REF / "rem151" / "CONCILIACION"
REF_B = {"B1": REF / "rem166", "B2": REF / "rem169"}
STDOUT_B = {"B1": ("B1PROD166_TRABAJO.stdout.txt", "B1PROD166_VALIDACION.stdout.txt"), "B2": ("B2PROD169_TRABAJO.stdout.txt", "B2PROD169_VALIDACION.stdout.txt")}
DOCS_B = {"B1": (("TRABAJO", "SOLICITUD_INICIO.json"), ("TRABAJO", "EVIDENCIA_B1.json"), ("VALIDACION", "VALIDACION_B1.json"), ("VALIDACION", "LECTURA_B1.json")),
          "B2": (("TRABAJO", "PLAN_INICIO.json"), ("TRABAJO", "EVIDENCIA_B2.json"), ("VALIDACION", "VALIDACION_B2.json"), ("VALIDACION", "LECTURA_B2.json"))}
SCRIPTS_B = {"B1": ("b1_trabajo.py", "validar_b1.py"), "B2": ("b2_trabajo.py", "validar_b2.py")}
PIEZAS_B = {u: ("comun_%s.py" % u.lower(), "puerta_%s.py" % u.lower()) + SCRIPTS_B[u] for u in UNIDADES_B}
RESOLUCION = REF / "rem170" / "COV12_RESOLUCION_GLOBAL.jsonl"
RUTAS_COV = {"tmp/paso4_remanente_lotes_desde_rem113/censo/CENSO_REMANENTE.json": CENSO[0],
             "tmp/paso4_ablaciones_exp8_desde_rem147/paquete_ablaciones/censo/CENSO_COV_REM147.json": "datos/fam11/cov/CENSO_COV_REM147.json"}
_D7 = "nucleo_s6/raiz/salidas_s6/d7/versions/2a25893b09c097b2af22ed2e5be9a4014851faf55bbaaf380c7a078f1a740591/"
RUTAS_B = {"B1": {"x162_preparacion_b1_b2": "datos/fam11/fuentes/PREPARACION_B1_B2.json", "x162_contexto_col": "datos/fam11/fuentes/CONTEXTO_COL_POR_GRUPO.json",
                  "x161_plan": "datos/fam11/fuentes/PLAN_MINIMO_PROPUESTO.json", "cov_conciliacion_rem151": "datos/fam11/" + CONC_FUENTE[0],
                  "d7_manifest": _D7 + "d7_manifest.json", "d7_support_set": _D7 + "support_set.csv", "d7_tau_domains": _D7 + "tau_domains.csv",
                  "c0_run_py": "nucleo_s6/c0/src/paper2b/run.py", "cov_i5_tarea_lote": "nucleo_s6/cov/tarea_lote.py",
                  "cov_i5_preparar_manifiesto": "datos/fam11/fuentes/preparar_manifiesto_cov.py"},
           "B2": {"x162_contexto_col": "datos/fam11/fuentes/CONTEXTO_COL_POR_GRUPO.json", "x162_mapa_derivado": MAPA[0],
                  "x162_preparacion_b1_b2": "datos/fam11/fuentes/PREPARACION_B1_B2.json", "b1_indice": IDX_B["B1"][0], "b1_manifiesto": MAN_B["B1"][0],
                  "d7_manifest": _D7 + "d7_manifest.json", "d7_support_set": _D7 + "support_set.csv",
                  "grilla": "nucleo_s6/raiz/fase5_cuantificacion/extraccion_grilla/grilla_efectiva.csv",
                  "ca2_bundle_E2": "nucleo_s6/raiz/fase2_datos/ca2_bundles/bundles/73cf4e4499eb2e3327a27e01f9e87e1fd6b14a160bee4718fc945636420ae48e.json",
                  "ca2_bundle_E1": "nucleo_s6/raiz/fase2_datos/ca2_bundles/bundles/b2a90d7d89f12d4fd2b48a8af1b6e0fed5aca2cb46ee8d3a3db88cd742489151.json",
                  "d6_tax_marg": "nucleo_s6/raiz/fase2_datos/d6_tax_shares_v2/versions/8cea18486cdc83d6a2d25fd7060670cc229b80de2d61de4477ddb57613779441/tax_shares_marg.csv",
                  "c0_run_py": "nucleo_s6/c0/src/paper2b/run.py", "c0_contexto_s6": "datos/fam11/fuentes/contexto_s6.py",
                  "c0_cobertura": "nucleo_s6/c0/src/paper2b/cobertura.py", "nacional_instalacion": "nucleo_s6/raiz/herramientas/b/nacional.py"}}
ENLACE_CLAVES = ("b1_estado", "b1_evidencia", "b1_validacion", "b1_lectura")
ADAPTACIONES = ("GUION-v1", "MODULOS-v1", "NUCLEO-C0-v1", "RUTAS-FUENTES-v1", "SANEADO-v1", "RAIZ-MARCADORES-v1", "PUERTA-v1", "PROCEDENCIA-LOCAL-v1",
                "PAQUETE-v1", "ENLACE-B1-v1", "ENSAMBLADOR-ENTRADAS-v1", "ENTRADAS-CONCILIADOR-v1", "RELOJ-PILOTO-v1")
_C0_HIST = '"paso4_raices_impacto_desde_rem116/candidato_c0/instalacion"'
_TABLAS_COV = ("RUTAS_FUENTES = %s    # FAM11 RUTAS-FUENTES-v1: ruta histórica -> archivo de la base limpia\n"
               "ORIGINAL = %s    # FAM11 SANEADO-v1: sha256 de la proyección saneada -> sha256 de su original (correspondencia comprobada)\n"
               % (json.dumps(RUTAS_COV, ensure_ascii=False), json.dumps({CENSO[1]: CENSO[2]})))


def _tabla_b(u: str) -> str:
    t = ("BASE_LIMPIA = AQUI.parents[1]                       # FAM11 RUTAS-FUENTES-v1: raíz de la base limpia\n"
         'C0_LOCAL = AQUI.parent / "c0" / "src"                # FAM11 NUCLEO-C0-v1: núcleo C0 de la base limpia (mismos bytes del cierre)\n'
         "RUTAS_FUENTES = %s    # FAM11 RUTAS-FUENTES-v1: clave -> archivo de la base (las demás claves son solo de procedencia)\n"
         "ORIGINAL = %s    # FAM11 SANEADO-v1: sha256 de la proyección -> sha256 del original\n"
         "PIEZAS_COPIADAS = %s    # FAM11 PAQUETE-v1: piezas del índice copiadas a la base\n"
         "DECLARACION_KIND = %s    # FAM11 PUERTA-v1\n"
         "ETIQUETA = %s\n"
         "LANZAMIENTO = %s    # FAM11 PROCEDENCIA-LOCAL-v1: unidad de fam11-unidad\n"
         "ENLACE_B1 = {}    # FAM11 ENLACE-B1-v1: {clave: (ruta relativa, sha256)} del B1 nuevo validado; la fija src/fam11.py (solo B2)\n"
         "\n\n"
         "def _relativa(p):\n"
         "    p = Path(p).resolve()\n"
         "    return p.relative_to(BASE_LIMPIA.resolve()).as_posix() if p.is_relative_to(BASE_LIMPIA.resolve()) else p.name\n"
         % (json.dumps(RUTAS_B[u], ensure_ascii=False), json.dumps(ORIGINAL_B), json.dumps(list(PIEZAS_B[u])), json.dumps(DECLARACION_KIND),
            json.dumps(ETIQUETA, ensure_ascii=False), json.dumps(u)))
    if u == "B2":
        t += ("\n\n"
              "def _raiz_b1():\n"
              '    """FAM11 ENLACE-B1-v1: raíz binaria de la evidencia B1 nueva (ocupa domain.root_binary del libro rem167, que no se lee)."""\n'
              '    return json.loads(leer("b1_evidencia")[0])["raiz_binaria"]\n')
    return t + "\n\n"


def _procedencia_b(u: str) -> str:
    ev = "EVIDENCIA_B1.json" if u == "B1" else "EVIDENCIA_B2.json"
    sol = ' or rw.get("solicitudes") != 1' if u == "B1" else ""
    ini = '    (dT / "SOLICITUD_INICIO.json").read_bytes()\n' if u == "B1" else ""     # como el original: solo B1 lee su inicio
    return (
        "def _procedencia(fuente, modo, man_sha, alcance_sha, propia, info):\n"
        '    """FAM11 PROCEDENCIA-LOCAL-v1: sin área p3ctl. La fuente de ejecución es el registro local de fam11-unidad (ejecucion.json: orden\n'
        "    relativa, código de salida, última línea, inicio y fin; trabajo_stdout.txt); el resto del orden y de los fallos es el original:\n"
        "    misma orden (modo, manifiesto, alcance), salida del trabajador completa, huella de la evidencia emitida, evidencia dentro de su\n"
        '    ejecución y validación solo dentro de la misma unidad (carpeta hermana de TRABAJO)."""\n'
        '    if modo != "produccion":\n'
        '        return ["FAM11_SOLO_PRODUCCION"], None, info\n'
        '    if fuente.get("tipo") != "lanzamiento":\n'
        '        return ["FAM11_SIN_CONTINUACION_ENTRE_RONDAS"], None, info\n'
        '    area, lanz = Path(fuente["area"]), str(fuente["lanzamiento"])\n'
        "    if lanz != LANZAMIENTO:\n"
        '        return ["LANZAMIENTO_DE_OTRA_UNIDAD"], None, info\n'
        '    eb = (area / "ejecucion.json").read_bytes()\n'
        "    ej = json.loads(eb)\n"
        "    info.update(area=_relativa(area), lanzamiento=lanz, ejecucion_sha256=H(eb))\n"
        '    if not (ej.get("etiqueta") == ETIQUETA and ej.get("unidad") == LANZAMIENTO and ej.get("tarea") == TAREA_TRABAJO and ej.get("rc") == 0\n'
        '            and ej.get("excepcion") is None):\n'
        '        return ["EJECUCION_DE_TRABAJO_AUSENTE_O_NO_CONFORME"], None, info\n'
        '    op = ej.get("argumentos") or {}\n'
        '    if set(op) - set(ARGS_TRABAJO) or op.get("--modo") != modo or op.get("--decision") is not None:\n'
        '        return ["ARGUMENTOS_DE_TRABAJO_NO_PREVISTOS"], None, info\n'
        '    if HF(BASE_LIMPIA / op["--manifiesto"]) != man_sha:\n'
        '        return ["EJECUCION_DE_OTRO_MANIFIESTO"], None, info\n'
        '    if (HF(BASE_LIMPIA / op["--alcance"]) if op.get("--alcance") else None) != alcance_sha:\n'
        '        return ["EJECUCION_DE_OTRO_ALCANCE"], None, info\n'
        '    dT = BASE_LIMPIA / op["--salida"]\n'
        '    if dT.resolve() != (area / "TRABAJO").resolve():\n'
        '        return ["SALIDA_DEL_TRABAJO_FUERA_DE_SU_UNIDAD"], None, info\n'
        '    so = (area / "trabajo_stdout.txt").read_bytes()\n'
        "    try:\n"
        '        rw = json.loads(so.decode("utf-8").strip().splitlines()[-1])\n'
        "    except (ValueError, IndexError):\n"
        '        return ["SALIDA_DEL_TRABAJADOR_ILEGIBLE"], None, info\n'
        '    if rw != ej.get("ultima_linea"):\n'
        '        return ["SALIDA_DEL_TRABAJADOR_DISTINTA_DE_LA_REGISTRADA"], None, info\n'
        '    if rw.get("tarea") != TAREA_TRABAJO or rw.get("estado") != "complete"%s or not isinstance(rw.get("evidencia_sha256"), str):\n'
        '        return ["TRABAJADOR_SIN_RESULTADO_COMPLETO"], None, info\n'
        '    h_rec = rw["evidencia_sha256"]\n'
        "    info.update(trabajo_dir=_relativa(dT), salida_trabajador_sha256=H(so), evidencia_sha256=h_rec)\n"
        '    if fuente.get("evidencia_sha256") is not None and fuente["evidencia_sha256"] != h_rec:\n'
        '        return ["EVIDENCIA_DISTINTA_DE_LA_DEL_CONDUCTOR"], None, info\n'
        '%s'
        '    raw = (dT / "%s").read_bytes()\n'
        "    if H(raw) != h_rec:\n"
        '        return ["EVIDENCIA_DISTINTA_DE_LA_EJECUCION"], None, info\n'
        "    e = json.loads(raw)\n"
        '    t_ini, t_fin, e_ini, e_fin = _utc(ej.get("inicio_utc")), _utc(ej.get("fin_utc")), _utc(e.get("inicio_utc")), _utc(e.get("fin_utc"))\n'
        "    if None in (t_ini, t_fin, e_ini, e_fin) or not (t_ini <= e_ini <= e_fin <= t_fin):\n"
        '        return ["EVIDENCIA_FUERA_DE_SU_EJECUCION"], None, info\n'
        "    if propia is not None:\n"
        '        pa, av = Path(propia["area"]), [str(x) for x in propia.get("argv") or []]\n'
        '        if pa.resolve() != area.resolve() or str(propia["lanzamiento"]) != lanz:\n'
        '            return ["VALIDACION_DE_OTRO_LANZAMIENTO"], None, info\n'
        '        if len(av) < 3 or av[1] != modo or Path(av[2]).resolve().parent != area.resolve() or Path(av[2]).name == "TRABAJO":\n'
        '            return ["VALIDACION_FUERA_DE_SU_UNIDAD"], None, info\n'
        '        info["validacion_id"] = "%%s_%%s" %% (lanz, Path(av[2]).name)\n'
        "    return [], raw, info\n" % (sol, ini, ev))


def _puerta_b(u: str) -> str:
    err = "B1Error" if u == "B1" else "B2Error"
    return (
        "    # FAM11 PUERTA-v1: ni alcance verificado ni decisión humana (no se ejecutan ni se reconstruyen). Solo producción, con la\n"
        "    # declaración de ejecución limpia (NO OFICIAL) como alcance y sin decisión; su sha256 ocupa el alcance de evidencias y validaciones.\n"
        '    if modo != "produccion" or not alcance_p or decision_p:\n'
        '        raise C.%s("FAM11_PUERTA: solo producción con la declaración de ejecución limpia y sin decisión")\n'
        '    if str(man.get("kind", "")).endswith("-SINTETICO") or man.get("modo") != modo:\n'
        '        raise C.%s("MEZCLA_REAL_SINTETICO")\n'
        "    raw = Path(alcance_p).read_bytes()\n"
        "    doc, s = json.loads(raw), C.H(raw)\n"
        '    if doc.get("kind") != C.DECLARACION_KIND or doc.get("oficial") is not False or doc.get("etiqueta") != C.ETIQUETA \\\n'
        '            or tarea not in (doc.get("tareas") or []):\n'
        '        raise C.%s("DECLARACION_DE_EJECUCION_LIMPIA_DISTINTA")\n'
        '    return s, {"tipo": C.DECLARACION_KIND, "oficial": False, "decision": None, "alcance_sha256": s}\n' % (err, err, err))


_FUENTE_B1 = (
    "def fuente_b1(datos=None):\n"
    '    """FAM11 ENLACE-B1-v1: U_C2 del B1 NUEVO validado (no del libro rem167 ni del B1 histórico). Exige el registro de fam11-validar\n'
    "    aceptado para ESTOS bytes (evidencia, validación y lectura), evidencia completa de producción del manifiesto e índice B1 (original por\n"
    "    la proyección), U_C2 finito y igual al extremo superior del intervalo, validación aceptada coherente y lectura de seis grupos y doce\n"
    '    afirmaciones candidato_B2. datos: no se usa (ensayos históricos)."""\n'
    "    if sorted(ENLACE_B1) != sorted((\"b1_estado\", \"b1_evidencia\", \"b1_validacion\", \"b1_lectura\")):\n"
    '        raise B2Error("B1_SIN_ENLACE_VALIDADO (el B1 histórico no se usa)")\n'
    '    sb, sh = leer("b1_estado")\n'
    '    eb, eh = leer("b1_evidencia")\n'
    '    vb, vh = leer("b1_validacion")\n'
    '    rb_, rh = leer("b1_lectura")\n'
    "    reg, ev, va, le = json.loads(sb), json.loads(eb), json.loads(vb), json.loads(rb_)\n"
    '    if not (reg.get("comando") == "fam11-validar" and reg.get("unidad") == "B1" and reg.get("aceptada") is True and reg.get("rc") == 0):\n'
    '        raise B2Error("VALIDACION_B1_NO_ACEPTADA")\n'
    '    if (reg.get("evidencia_sha256"), reg.get("validacion_sha256"), reg.get("lectura_sha256")) != (eh, vh, rh):\n'
    '        raise B2Error("VALIDACION_B1_DE_OTROS_BYTES")\n'
    '    if not (ev.get("kind") == "evidencia-b1-rem163" and ev.get("estado") == "complete" and ev.get("modo") == "produccion"\n'
    '            and ORIGINAL.get(ev.get("manifiesto_sha256")) == FUENTES["b1_manifiesto"][1] and ORIGINAL.get(ev.get("indice_sha256")) == FUENTES["b1_indice"][1]):\n'
    '        raise B2Error("EVIDENCIA_B1_AJENA_O_INCOMPLETA")\n'
    '    U, hi = ev.get("U_C2"), (ev.get("intervalo_normalizado") or {}).get("hi")\n'
    '    if not (isinstance(U, float) and math.isfinite(U) and iguales_bits(U, hi) and ev.get("U_C2_hex") == float.hex(U)):\n'
    '        raise B2Error("U_C2_DE_LA_EVIDENCIA_B1_INCOHERENTE")\n'
    '    if not (va.get("aceptada") is True and va.get("dictamen") == "validada" and va.get("evidencia_sha256") == eh and va.get("lectura_sha256") == rh\n'
    '            and iguales_bits((va.get("datos") or {}).get("U_C2"), U) and va.get("alcance_sha256") == ev.get("alcance_sha256")):\n'
    '        raise B2Error("VALIDACION_B1_INCOHERENTE")\n'
    '    lec = le.get("lectura") or {}\n'
    '    if not (le.get("evidencia_sha256") == eh and lec.get("valida") is True and iguales_bits(lec.get("U_C2"), U)):\n'
    '        raise B2Error("LECTURA_B1_INCOHERENTE")\n'
    '    grupos = {g["grupo"]: g for g in lec.get("grupos") or []}\n'
    '    claims = {c["afirmacion"]: c["grupo"] for c in lec.get("afirmaciones") or []}\n'
    '    if sorted(grupos) != list(GRUPOS) or len(claims) != 12 or any(g.get("lectura") != "candidato_B2" for g in grupos.values()) \\\n'
    '            or any(c.get("lectura") != "candidato_B2" for c in lec["afirmaciones"]):\n'
    '        raise B2Error("LECTURA_B1_NO_SON_SEIS_CANDIDATOS")\n'
    '    return {"U_C2": U, "U_C2_hex": float.hex(U), "U_C2_exacto": fs(Fraction(U)), "libro_sha256": None, "evidencia_sha256": eh,\n'
    '            "validacion_sha256": vh, "lectura_sha256": rh, "estado_sha256": sh, "acto_B1": None,\n'
    '            "alcance_B1_sha256": ev.get("alcance_sha256"), "afirmacion_grupo": dict(sorted(claims.items())),\n'
    '            "naturaleza": "cota superior certificada sobre la raiz fija; NO es maximo puntual, argmax ni prueba de alcanzabilidad"}\n')


def _sust_comun(u: str) -> tuple:
    err = "B1Error" if u == "B1" else "B2Error"
    s = [("RAIZ-MARCADORES-v1 (importación)", "from pathlib import Path\n", "from pathlib import Path, PureWindowsPath\n"),
         ("RAIZ-MARCADORES-v1 (R)", "R = AQUI.parents[2]\n",
          'R = PureWindowsPath("@@R_BS2@@")      # FAM11 RAIZ-MARCADORES-v1: ruta pura con el marcador de la proyección (solo texto del manifiesto)\n'),
         ("RAIZ-MARCADORES-v1 (W)", 'W = Path(r"@@W_WIN@@")\n', 'W = PureWindowsPath("@@W_BS2@@")      # FAM11 RAIZ-MARCADORES-v1\n'),
         ("RUTAS-FUENTES-v1 (tabla)", "\nCONJUNTOS_COV = (", "\n" + _tabla_b(u) + "CONJUNTOS_COV = ("),
         ("RUTAS-FUENTES-v1 (lectura)", "    p, h = FUENTES[nombre]\n    b = Path(p).read_bytes()\n    if H(b) != h:\n",
          ("    if nombre in ENLACE_B1:                        # FAM11 ENLACE-B1-v1: bytes del B1 nuevo validado (ruta y huella fijadas)\n"
           "        p, h = BASE_LIMPIA / ENLACE_B1[nombre][0], ENLACE_B1[nombre][1]\n"
           "    elif nombre in RUTAS_FUENTES:                  # FAM11 RUTAS-FUENTES-v1\n"
           "        p, h = BASE_LIMPIA / RUTAS_FUENTES[nombre], FUENTES[nombre][1]\n"
           "    else:\n"
           '        raise %s("FUENTE_SOLO_DE_PROCEDENCIA_O_NO_DECLARADA:%%s" %% nombre)\n'
           "    b = Path(p).read_bytes()\n"
           "    if ORIGINAL.get(H(b), H(b)) != h:              # FAM11 SANEADO-v1: la huella registrada es la del original\n" % err)),
         ("RUTAS-FUENTES-v1 (construcción)", "    for k in FUENTES:\n        leer(k)\n",
          ("    fuentes.update({k: {\"ruta\": r, \"sha256\": h} for k, (r, h) in sorted(ENLACE_B1.items())})   # FAM11 ENLACE-B1-v1\n"
           "    for k in FUENTES:\n"
           "        if k in RUTAS_FUENTES or k in ENLACE_B1:      # FAM11 RUTAS-FUENTES-v1: las de solo procedencia no se leen al ejecutar\n"
           "            leer(k)\n")),
         ("NUCLEO-C0-v1 (cierre)", '    src = Path(src or C0_SRC) / "paper2b"\n', '    src = Path(src or C0_LOCAL) / "paper2b"      # FAM11 NUCLEO-C0-v1\n'),
         ("PAQUETE-v1", '        return [n for n, h in idx["piezas"].items() if HF(AQUI / n) != h]\n',
          ('        return ([n for n, h in idx["piezas"].items() if n in PIEZAS_COPIADAS and ORIGINAL.get(HF(AQUI / n), HF(AQUI / n)) != h]\n'
           '                + [n for n in PIEZAS_COPIADAS if n not in idx["piezas"]])    # FAM11 PAQUETE-v1: las piezas copiadas (proyección -> original)\n')),
         ("PUERTA-v1 (evidencia)", '        if not pe or pe.get("modo_arnes") is not False or any(pe.get(k) != pv.get(k) for k in ("uuid", "linea", "alcance_sha256", "registro_sha256")):\n',
          '        if not pe or pe != pv or pe.get("tipo") != DECLARACION_KIND or pe.get("decision") is not None:   # FAM11 PUERTA-v1\n'),
         ("PROCEDENCIA-LOCAL-v1", ("def _procedencia(fuente, modo, man_sha, alcance_sha, propia, info):\n", '        info["validacion_id"] = tv\n    return [], raw, info\n'),
          _procedencia_b(u))]
    if u == "B2":
        s += [("ENLACE-B1-v1 (fuente)", ("def fuente_b1(datos=None):\n",
                                         '            "naturaleza": "cota superior certificada sobre la raiz fija; NO es maximo puntual, argmax ni prueba de alcanzabilidad"}\n'),
               _FUENTE_B1),
              ("ENLACE-B1-v1 (raíz)", '    lib = json.loads(leer("libro_B1_rem167")[0])\n',
               '    lib = {"domain": {"root_binary": _raiz_b1()}}     # FAM11 ENLACE-B1-v1: raíz de la evidencia B1 nueva (el libro rem167 no se lee)\n')]
    return tuple(s)


SUSTITUCIONES = {
    "nucleo_s6/cov/tarea_lote.py": (
        ("RAIZ-v1", "R = AQUI.parents[2]\n", "R = AQUI.parents[1]                                         # FAM11 RAIZ-v1: base limpia (solo hasta-seleccion)\n"),
        ("PUERTA-v1", F7.SUSTITUCIONES["tarea_lote.py"][1][1],
         'if modo == "produccion":                    # FAM11 PUERTA-v1: sin puerta de producción (ni alcance v3 ni decisión humana)\n'
         '    if "--declaracion" not in o:\n'
         '        fin("rechazada", "PRODUCCION_SIN_DECLARACION_DE_EJECUCION_LIMPIA")\n'
         '    out["alcance_sha256"] = H(Path(o["--declaracion"]).read_bytes())    # sha256 de datos/fam11/ejecucion_limpia.json (NO OFICIAL)\n')),
    "nucleo_s6/cov/validar_coord_rec.py": (
        ("NUCLEO-C0-v1", "NUCLEO = Path(__file__).resolve().parents[2] / " + _C0_HIST, 'NUCLEO = Path(__file__).resolve().parents[1] / "c0"'),
        ("RUTAS-FUENTES-v1 (tabla)", 'SIN_CALCULO = ("PROVEEDOR_NO_CERTIFICADO", "CONFIGURACION_DISTINTA_DE_LA_DECLARADA", "DETENIDO_POR_TOPE")\n',
         'SIN_CALCULO = ("PROVEEDOR_NO_CERTIFICADO", "CONFIGURACION_DISTINTA_DE_LA_DECLARADA", "DETENIDO_POR_TOPE")\n' + _TABLAS_COV),
        ("RUTAS-FUENTES-v1 (lectura)", '    p = Path(R) / ref["ruta"]\n',
         '    if ref["ruta"] not in RUTAS_FUENTES:                              # FAM11 RUTAS-FUENTES-v1: solo fuentes declaradas\n'
         '        return None, "FUENTE_NO_DECLARADA_EN_LA_BASE_LIMPIA:%s" % ref["ruta"]\n'
         '    p = Path(R) / RUTAS_FUENTES[ref["ruta"]]\n'),
        ("SANEADO-v1", '    if hashlib.sha256(b).hexdigest() != ref["sha256"]:\n',
         '    if ORIGINAL.get(hashlib.sha256(b).hexdigest(), hashlib.sha256(b).hexdigest()) != ref["sha256"]:   # FAM11 SANEADO-v1\n')),
    "nucleo_s6/cov/validar_lote.py": (("NUCLEO-C0-v1", "NUCLEO = AQUI.parents[1] / " + _C0_HIST, 'NUCLEO = AQUI.parents[0] / "c0"'),),
    "nucleo_s6/cov/ensamblar_coord.py": tuple((i, a, b.replace("FAM07", "FAM11")) for i, a, b in F7.SUSTITUCIONES["ensamblar_coord.py"]),
    "src/conciliar_cov.py": (("ENTRADAS-CONCILIADOR-v1", '        d = Path(o["directorio"])\n',
                              '        d = Path(R) / o["directorio"]            # FAM11 ENTRADAS-CONCILIADOR-v1: carpeta relativa a la base (la registra el ensamblador)\n'),),
    "nucleo_s6/b1/comun_b1.py": _sust_comun("B1"),
    "nucleo_s6/b2/comun_b2.py": _sust_comun("B2"),
    "nucleo_s6/b1/puerta_b1.py": (("PUERTA-v1", ("    import alcance_b1 as AP\n", "    return s, ev\n"), _puerta_b("B1")),),
    "nucleo_s6/b2/puerta_b2.py": (("PUERTA-v1", ("    import alcance_b2 as AP\n", "    return s, ev\n"), _puerta_b("B2")),),
    "nucleo_s6/b1/b1_trabajo.py": (("NUCLEO-C0-v1 (ruta visible)", 'str(C.C0_SRC / "paper2b")', 'C._relativa(C.C0_LOCAL / "paper2b")'),),
    "nucleo_s6/b2/b2_trabajo.py": (("NUCLEO-C0-v1 (ruta visible)", 'str(C.C0_SRC / "paper2b")', 'C._relativa(C.C0_LOCAL / "paper2b")'),)}


class Fam11Error(RuntimeError):
    pass


# Procesos: un cálculo o validación COV y uno B1/B2 nunca comparten proceso (el cierre C0 de B1/B2 rechaza paper2b precargado). Solo
# fam11-comprobar (sin cálculo: reconstrucción documental de los manifiestos B1/B2 antes de cargar el núcleo COV) marca el proceso como
# documental y admite ambos.
_DOCUMENTAL = []


def need(t, codigo):
    if not t:
        raise Fam11Error(codigo)


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def fuentes() -> dict:
    return leer(BASE / "fuentes_fam11.json")


def piezas() -> list:
    fu = fuentes()
    c0 = [dict(x, papel="núcleo C0 (reutilizado de FAM05)") for x in F5.fuentes()["archivos"] if x["archivo"].startswith("nucleo_s6/c0/")]
    return fu["archivos"] + fu["reutilizados"] + c0


def _uso(a: str, uso: str, guardadas=None) -> bool:
    if uso == "todo":
        return True
    if uso == "calculo":                    # el cálculo y la validación no abren salidas aceptadas ni referencias (ni para su huella)
        return not a.startswith(("datos/fam11/guardadas/", "referencias/"))
    if a.startswith("datos/fam11/guardadas/") and guardadas is not None:   # regeneración: solo las guardadas declaradas como entrada
        return any(a.startswith(g.rstrip("/") + "/") for g in guardadas)
    return not a.startswith("referencias/")


def fuentes_alteradas(uso: str = "todo", guardadas=None) -> list:
    """Piezas ausentes o con otra huella. «calculo»: código, núcleo y entradas (sin salidas guardadas ni referencias); «regeneracion»: además
    las guardadas declaradas como entrada; «todo»: todo (fam11-comprobar)."""
    return [x["archivo"] for x in piezas() if _uso(x["archivo"], uso, guardadas) and sha_archivo(BASE / x["archivo"]) != x["sha256"]]


def manifiesto_cov() -> tuple:
    raw = (DATOS / MAN_COV[0]).read_bytes()
    need(sha(raw) == MAN_COV[1], "MANIFIESTO_COV_DISTINTO")
    man = json.loads(raw)
    need(not str(man.get("kind", "")).endswith(("-SINTETICO", "-ENSAYO")), "MANIFIESTO_SINTETICO_O_DE_ENSAYO")
    return raw, man


def manifiesto_b(u: str) -> tuple:
    raw = (BASE / MAN_B[u][0]).read_bytes()
    need(sha(raw) == MAN_B[u][1], "MANIFIESTO_%s_DISTINTO" % u)
    return raw, json.loads(raw)


def pines() -> dict:
    """Bytes guardados de rem151 (declarados en fuentes_fam11.json; resultado ligado además al libro rem152)."""
    arch = {x["archivo"]: x["sha256"] for x in fuentes()["archivos"]}
    lb = (fuentes().get("libros") or {}).get("rem152") or {}
    out = {}
    for t in TAREAS:
        g = "datos/fam11/guardadas/cov_rem151/%s/" % t
        out[t] = {"resultado_sha256": arch.get(g + "resultado.json"), "productos": {n: arch.get(g + "salida/" + n) for n in PRODUCTOS},
                  "libro_resultado_sha256": ((lb.get("tareas") or {}).get(t) or {}).get("resultado_sha256")}
    return out


def catalogo_op(op: str) -> dict:
    return next(o for o in leer(BASE / "catalogo.json")["operaciones"] if o["clave"] == op)


# ================================================================================================ guiones y módulos adaptados
def adaptado(n: str) -> str:
    """GUION-v1: bytes exactos de <n> (relativo a la base) con sus sustituciones (cada original, una sola vez; un bloque se fija por su
    primera y su última línea, ambas únicas)."""
    src = (BASE / n).read_bytes()
    need(sha(src) == CODIGO[n], "CODIGO_FAM11_DISTINTO: %s" % n)
    txt = src.decode("utf-8")
    for i, a, b in SUSTITUCIONES.get(n, ()):
        if isinstance(a, tuple):
            need(txt.count(a[0]) == 1 and txt.count(a[1]) == 1 and txt.index(a[0]) < txt.index(a[1]), "SUSTITUCION_NO_UNICA: %s %s" % (n, i))
            a = txt[txt.index(a[0]):txt.index(a[1]) + len(a[1])]
        need(txt.count(a) == 1, "SUSTITUCION_NO_UNICA: %s %s" % (n, i))
        txt = txt.replace(a, b)
    return txt


def sustituciones_ok() -> bool:
    try:
        for n in SUSTITUCIONES:
            compile(adaptado(n), n, "exec")
        return True
    except (Fam11Error, SyntaxError):
        return False


def modulo(nombre: str, n: str):
    txt = adaptado(n)
    h = sha(txt.encode("utf-8"))
    m = sys.modules.get(nombre)
    if m is None or getattr(m, "FAM11_ADAPTADO_SHA256", None) != h:
        m = types.ModuleType(nombre)
        m.__file__ = str(BASE / n)
        sys.modules[nombre] = m
        ruta = list(sys.path)
        try:
            exec(compile(txt, str(BASE / n), "exec"), m.__dict__)
        except BaseException:
            sys.modules.pop(nombre, None)
            raise
        finally:
            sys.path[:] = ruta
        m.FAM11_ADAPTADO_SHA256 = h
    return m


def _sin_base(t):
    return None if t is None else t.replace(str(BASE), "<base>")


def _ejecutar(n: str, args: list, mods: dict) -> tuple:
    """Ejecuta el texto adaptado de <n> como __main__ con sys.argv = [<base>/<n>, *args]; devuelve (rc, última línea JSON, stdout, excepción)."""
    txt = adaptado(n)
    p = BASE / n
    g = {"__name__": "__main__", "__file__": str(p), "__builtins__": builtins}
    viejo, ruta, buf, rc, exc = sys.argv, list(sys.path), io.StringIO(), None, None
    sys.argv = [str(p)] + [str(x) for x in args]
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(txt, str(p), "exec"), g)
    except SystemExit as ex:
        rc = ex.code
    except Exception:  # noqa: BLE001  (se registra; nunca se toma por éxito)
        exc = _sin_base(traceback.format_exc())
    finally:
        sys.argv = viejo
        sys.path[:] = ruta
    need(all(sys.modules.get(k) is m for k, m in mods.items()), "MODULO_FAM11_SUSTITUIDO_DURANTE_EL_GUION")
    lineas = [x for x in buf.getvalue().splitlines() if x.strip()]
    try:
        ult = json.loads(lineas[-1]) if lineas else {}
    except ValueError:
        ult = {}
    return rc, ult, buf.getvalue(), exc


# ---------------------------------------------------------------------------------------------------------------- COV (paper2b importado)
def preparar_cov() -> dict:
    """Núcleo C0 delante y módulo de identidad (FAM05); validar_coord_rec COV desde su texto adaptado (MODULOS-v1)."""
    need(_DOCUMENTAL or not any(k.startswith(("comun_b", "puerta_b")) for k in sys.modules), "PROCESO_B_MEZCLADO_CON_COV")
    F5.preparar()
    M = {"validar_coord_rec": modulo("validar_coord_rec", "nucleo_s6/cov/validar_coord_rec.py")}
    cx = sys.modules.get("conexion_coord_cert")
    if cx is not None:
        need(Path(cx.__file__).resolve() == (COV / "conexion_coord_cert.py").resolve(), "CONEXION_COORD_DE_OTRO_PAQUETE")
    return M


def guion_cov(n: str, args: list) -> tuple:
    return _ejecutar(n, args, preparar_cov())


# ---------------------------------------------------------------------------------------------------------------- B1/B2 (cierre C0 propio)
def _paper2b_cargado() -> list:
    return sorted(m for m in sys.modules if m == "paper2b" or m.startswith("paper2b."))


def preparar_b(u: str) -> dict:
    """comun_bX y puerta_bX desde su texto adaptado. Exige un proceso sin paper2b precargado (el cierre C0 de B1/B2 lo rechazaría) y sin
    piezas COV cargadas. comun_b1 puede convivir con comun_b2: B2 revalida el B1 nuevo con las funciones del validador B1 (sin motor)."""
    need(u in UNIDADES_B, "UNIDAD_B_DESCONOCIDA: %s" % u)
    need(not _paper2b_cargado(), "PAPER2B_PRECARGADO: B1/B2 se ejecutan en un proceso propio (sin COV ni FAM05.preparar)")
    need(_DOCUMENTAL or "validar_coord_rec" not in sys.modules, "PROCESO_MEZCLADO_CON_COV: %s" % u)
    d = "nucleo_s6/%s/" % u.lower()
    C = modulo("comun_%s" % u.lower(), d + "comun_%s.py" % u.lower())
    P = modulo("puerta_%s" % u.lower(), d + "puerta_%s.py" % u.lower())
    return {C.__name__: C, P.__name__: P}


def guion_b(u: str, script: str, args: list) -> tuple:
    mods = preparar_b(u)
    return _ejecutar("nucleo_s6/%s/%s" % (u.lower(), script), args, mods)


def comun(u: str):
    return preparar_b(u)["comun_%s" % u.lower()]


# ================================================================================================ declaración y pilotos
def regla_declaracion() -> dict:
    return {"kind": DECLARACION_KIND, "etiqueta": ETIQUETA, "oficial": False, "decision": None,
            "naturaleza": ("PUERTA-v1: las puertas de producción de COV, B1 y B2 (alcance verificado y decisión humana nativa) no se ejecutan "
                           "ni se reconstruyen. El sha256 de este documento ocupa el alcance que escriben los trabajadores y que exigen los "
                           "validadores. No es un alcance ni una decisión; no autoriza producción oficial ni sustituye a los alcances históricos "
                           "(69900e10… de COV y los de B1/B2, que solo se usan para cruzar huellas)."),
            "manifiestos": {"cov": MAN_COV[1], "b1": MAN_B["B1"][2], "b2": MAN_B["B2"][2]},
            "indices": {"cov": IDX_COV[1], "b1": IDX_B["B1"][2], "b2": IDX_B["B2"][2]}, "codigo": dict(CODIGO),
            "instalacion_identidad": F5.C0_IDENTIDAD,
            "tareas": list(TAREAS) + ["B1-TRABAJO", "B1-VALIDACION", "B2-TRABAJO", "B2-VALIDACION"],
            "integracion": ["COV-ENSAMBLADO", "COV-CONCILIACION"]}


def regla_pilotos(man: dict) -> dict:
    co = man["ABL-COV"]
    cl = co["tareas"][T1]
    cel = [c for c in co["celdas_afectadas"] if c["clave_transformada_sha256"] in cl]
    return {"regla": ("fijados por el encargo de FAM11 antes de calcular y sin mirar resultados: (1) la tarea completa ABL-COV-T1 (sus 18 "
                      "claves, con los presupuestos científicos originales; límite externo 2.400 s); (2) B1 completo con su única solicitud "
                      "(600 s); (3) B2 completo consumiendo el B1 NUEVO validado del piloto 2 (600 s). Un supervisor, una invocación cada vez; "
                      "un vencimiento real se informa y no se relanza."),
            "pilotos": [{"unidad": T1, "operacion": "F11-COV26", "claves": len(cl), "comparaciones": len(cel), "limite_externo_s": F5.TOPE_TRABAJO,
                         "reloj_interno_s": F5.TOPE_TRABAJO - F5.HOLGURA, "duracion_historica": "≈70 s según el encargo (informativa; no es un tope)"},
                        {"unidad": "B1", "operacion": "F11-B1", "solicitudes": 1, "limite_externo_s": 600.0,
                         "presupuestos": "los del manifiesto B1 (param_budget_s 3600, struct_max_boxes 400; sin recortes)"},
                        {"unidad": "B2", "operacion": "F11-B2", "consume": "el B1 nuevo del piloto 2, validado por fam11-validar (ENLACE-B1-v1)",
                         "contextos_efectivos": 1920, "puentes": 480, "Q": 60, "limite_externo_s": 600.0}]}


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
    return sha(raw), json.loads(raw)


def listar() -> dict:
    raw, man = manifiesto_cov()
    co = man["ABL-COV"]
    _, m1 = manifiesto_b("B1")
    _, m2 = manifiesto_b("B2")
    return {"comando": "fam11-listar", "calculo": "ninguno", "operaciones": OPERACIONES,
            "manifiestos": {"cov": sha(raw), "b1": {"proyeccion": MAN_B["B1"][1], "original": MAN_B["B1"][2]},
                            "b2": {"proyeccion": MAN_B["B2"][1], "original": MAN_B["B2"][2]}},
            "recuento": {"cov": {"claves": len(co["claves_recalculadas"]), "claves_reutilizadas": len(co.get("claves_reutilizadas") or {}),
                                 "tareas": {t: len(v) for t, v in co["tareas"].items()}, "celdas_afectadas": len(co["celdas_afectadas"]),
                                 "celdas_por_tarea": {t: sum(1 for c in co["celdas_afectadas"] if c["clave_transformada_sha256"] in v) for t, v in co["tareas"].items()}},
                         "b1": {"grupos": len(m1.get("grupos") or []), "afirmaciones": sum(len(g["afirmaciones"]) for g in m1.get("grupos") or [])},
                         "b2": {"grupos": len(m2.get("grupos") or []), "afirmaciones": len(m2.get("afirmaciones") or []),
                                "entradas_nacionales": len(m2.get("entradas_nacionales") or {}), "celdas_Q": len((m2.get("celdas") or {}).get("ids") or [])}},
            "pilotos": fijar("pilotos.json", regla_pilotos(man)), "declaracion": fijar(DECLARACION, regla_declaracion())}


# ================================================================================================ lecturas y entorno
def declarados() -> set:
    out = set(F8.declarados())
    if (BASE / "fuentes_fam11.json").is_file():
        out |= {x["archivo"] for x in piezas()}
    return out


def lecturas(rastro, informe: dict, prohibidas: tuple = ()) -> dict:
    dec = declarados()
    propios = ("src/", "reproducir.py", "datos/fam01/", "datos/fam11/pilotos.json", "datos/fam11/" + DECLARACION, "fuentes_fam0", "fuentes_fam1",
               "catalogo.json")
    en = informe["en_el_paquete"]
    sal = sorted(x for x in rastro.dentro if x.startswith("salidas/") and (BASE / x).is_file())
    return {"archivo": "archivos_leidos.json", "en_el_paquete": len(en), "del_entorno_venv": sum(1 for x in en if x.startswith(".venv-fam01/")),
            "aperturas_del_interprete": informe["aperturas_del_interprete"], "fuera_del_paquete_y_del_interprete": informe["fuera_del_paquete_y_del_interprete"],
            "sin_manifiesto": [x for x in en if x not in dec and not x.startswith((".venv-fam01/",) + propios)],
            "nucleo_c0_leidos": sum(1 for x in en if x.startswith("nucleo_s6/c0/")),
            "codigo_fam11_leido": sorted(x for x in en if x in CODIGO),
            "guardadas_leidas": sorted({"/".join(x.split("/")[:5]) for x in en if x.startswith("datos/fam11/guardadas/")}),
            "fuentes_leidas": sorted(x for x in en if x.startswith(("datos/fam11/fuentes/", "nucleo_s6/raiz/", "datos/fam08/"))),
            "referencias_leidas": sorted(x for x in en if x.startswith("referencias/") and not x.startswith("referencias/fam01/")),
            "salidas_leidas": sal, "referencia_esperada_leida": any(x.startswith(prohibidas) for x in en) if prohibidas else False}


def entorno_cov() -> dict:
    e = F5._entorno(None)
    e["f2_alcance"] = "adoptada solo para FAM01; aquí se informa y no es requisito de FAM11"
    return e


def entorno_b() -> dict:
    import os
    import platform
    return {"python": platform.python_version(), "hash_seed": os.environ.get("PYTHONHASHSEED"), "hash_randomization": sys.flags.hash_randomization,
            "hilos": {k: os.environ.get(k) for k in F1().HILOS}, "TZ": os.environ.get("TZ"),
            "meta_path": [getattr(x, "__name__", type(x).__name__) for x in sys.meta_path],
            "f2": ("no evaluada en el proceso B (evaluarla importaría herramientas de la raíz y paper2b por sys.path, que el cierre C0 de B1/B2 "
                   "rechaza); F2 es solo de FAM01 y no es requisito de FAM11")}


def importados_cov() -> dict:
    return {"paper2b": sorted({rel(Path(m.__file__).parent) for k, m in list(sys.modules.items())
                               if (k == "paper2b" or k.startswith("paper2b.")) and getattr(m, "__file__", None)}),
            "validar_coord_rec": {"archivo": rel(Path(sys.modules["validar_coord_rec"].__file__)),
                                  "texto_adaptado_sha256": getattr(sys.modules["validar_coord_rec"], "FAM11_ADAPTADO_SHA256", None)}
            if "validar_coord_rec" in sys.modules else None,
            "conexion_coord_cert": rel(Path(sys.modules["conexion_coord_cert"].__file__)) if "conexion_coord_cert" in sys.modules else None}


def _escribir(p: Path, doc: dict):
    p.write_bytes(json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True, default=str).encode("utf-8") + b"\n")


def productos_de(nueva: Path, res: dict) -> dict:
    return {p["archivo"]: sha_archivo(Path(nueva) / "salida" / p["archivo"]) for p in res.get("productos") or []}


# ================================================================================================ cálculo
def correr(unidad: str, salida: Path, b1=None, validacion_b1=None, tope: float = F5.TOPE_TRABAJO) -> dict:
    """fam11-unidad: ABL-COV-T* (tarea_lote.py) o B1/B2 (trabajador del paquete) en la carpeta NUEVA `salida`."""
    if unidad in TAREAS:
        need(b1 is None and validacion_b1 is None, "--b1/--validacion-b1 SOLO PARA B2")
        return correr_cov(unidad, salida, tope)
    need(unidad in UNIDADES_B, "UNIDAD_FUERA_DE_FAM11: %s" % unidad)
    return correr_b(unidad, salida, b1, validacion_b1)


def correr_cov(tarea: str, salida: Path, tope: float = F5.TOPE_TRABAJO) -> dict:
    T0, c0 = time.time(), time.process_time()
    rastro = F1().Rastro()
    malos = fuentes_alteradas("calculo")
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam11.json; no se calcula): %s" % malos[:5])
    hdec, _ = declaracion()
    TOPE = float(tope) - F5.HOLGURA
    need(TOPE > 0, "TOPE_INVALIDO")
    raw, man = manifiesto_cov()
    preparar_cov()
    need(F5.identidad_c0() == F5.C0_IDENTIDAD, "NUCLEO_C0_DE_OTRA_IDENTIDAD (no se calcula)")
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    sal = salida.resolve()
    args = ["--tarea", tarea, "--modo", "produccion", "--manifiesto", DATOS / MAN_COV[0], "--manifiesto-sha256", MAN_COV[1],
            "--salida", sal / "salida", "--resultado", sal / "resultado.json", "--tope-efectivo", repr(TOPE), "--instalacion", F5.C0,
            "--declaracion", DATOS / DECLARACION]
    a0 = time.time()
    rc, ult, stdout, exc = guion_cov("nucleo_s6/cov/tarea_lote.py", args)
    t_calc = round(time.time() - a0, 2)
    (sal / "trabajo_stdout.txt").write_text(stdout, encoding="utf-8")
    res = leer(sal / "resultado.json") if (sal / "resultado.json").is_file() else {}
    techos = leer_jsonl(sal / "salida" / PRODUCTOS[0]) if (sal / "salida" / PRODUCTOS[0]).is_file() else []
    co = man["ABL-COV"]
    informe = rastro.informe()
    (sal / "archivos_leidos.json").write_bytes((json.dumps(informe, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    ej = {"tarea": tarea, "unidad": tarea, "operacion": "F11-COV26", "claves": co["tareas"][tarea],
          "naturaleza": ("cálculo: ruta de producción de tarea_lote.py ABL-COV (bytes exactos, GUION-v1) con conexion_coord_cert y "
                         "RUN.provider_for(RUN.RunConfig()) (ModeloTeorico certificado) en la base limpia; sin puerta de producción (PUERTA-v1)"),
          "alcance": "tarea completa de la partición (phi/2 exacto; las otras entradas del padre intactas)",
          "adaptaciones": ["GUION-v1", "MODULOS-v1", "NUCLEO-C0-v1", "RUTAS-FUENTES-v1", "SANEADO-v1", "RAIZ-v1", "PUERTA-v1", "RELOJ-PILOTO-v1"],
          "trabajador_adaptado_sha256": sha(adaptado("nucleo_s6/cov/tarea_lote.py").encode("utf-8")), "rc_del_trabajador": rc, "excepcion": exc,
          "ultima_linea": ult, "manifiesto_sha256": sha(raw), "etiqueta": ETIQUETA, "declaracion_sha256": hdec,
          "reloj": "RELOJ-PILOTO-v1: tope interno %.0f s (= %.0f − %.0f); el límite externo lo pone el supervisor" % (TOPE, float(tope), F5.HOLGURA),
          "resultado": {"estado": res.get("estado"), "motivo": res.get("motivo"), "productos": res.get("productos")},
          "techos": [{k: t.get(k) for k in ("clave_transformada_sha256", "diseno", "estado", "motivo", "attained", "error_kind", "garantia", "C_2",
                                            "error_normalizado", "error_R", "cierre_por_escala", "final_n", "segundos")} for t in techos],
          "nucleo": {"identidad": F5.identidad_c0(), "importados": importados_cov()},
          "tiempos_s": {"calculo": t_calc, "total": round(time.time() - T0, 2), "cpu": round(time.process_time() - c0, 2)},
          "entorno": entorno_cov(), "lecturas": lecturas(rastro, informe), "dependencias_fuera_de_la_biblioteca_estandar": F1().dependencias_cargadas()}
    ej["termino"] = exc is None and res.get("estado") in ("completa", "incompleta")
    ej["exito"] = res.get("estado") == "completa" and exc is None
    _escribir(sal / "ejecucion.json", ej)
    return ej


def enlace_b1(b1, validacion_b1) -> dict:
    """ENLACE-B1-v1: el B1 nuevo (carpeta de fam11-unidad B1 con éxito) y el registro de fam11-validar ACEPTADO para esos mismos bytes."""
    need(b1 is not None and validacion_b1 is not None, "B2_EXIGE_--b1_Y_--validacion-b1")
    d, v = Path(b1).resolve(), Path(validacion_b1).resolve()
    need(d.is_relative_to(BASE.resolve()) and v.is_relative_to(BASE.resolve()), "B1_FUERA_DE_LA_BASE")
    need(v.is_file() and (d / "ejecucion.json").is_file(), "B1_SIN_VALIDACION_O_SIN_EJECUCION")
    reg, ej = leer(v), leer(d / "ejecucion.json")
    need(ej.get("etiqueta") == ETIQUETA and ej.get("unidad") == "B1" and ej.get("exito") is True, "B1_SIN_EJECUCION_FAM11_COMPLETA")
    need(reg.get("comando") == "fam11-validar" and reg.get("unidad") == "B1" and reg.get("origen") == rel(d), "VALIDACION_DE_OTRA_UNIDAD")
    need(reg.get("aceptada") is True and reg.get("rc") == 0, "VALIDACION_B1_NO_ACEPTADA")
    vd = BASE / str(reg.get("validacion_dir") or "<sin carpeta de validación>")
    fu = {"b1_estado": v, "b1_evidencia": d / "TRABAJO" / "EVIDENCIA_B1.json", "b1_validacion": vd / "VALIDACION_B1.json", "b1_lectura": vd / "LECTURA_B1.json"}
    need(all(p.is_file() for p in fu.values()) and vd.resolve().parent == d, "PIEZA_DEL_B1_AUSENTE")
    need((sha_archivo(fu["b1_evidencia"]), sha_archivo(fu["b1_validacion"]), sha_archivo(fu["b1_lectura"]))
         == (reg.get("evidencia_sha256"), reg.get("validacion_sha256"), reg.get("lectura_sha256")), "VALIDACION_B1_DE_OTROS_BYTES")
    rv = revalidar_b1(d, ej, fu)
    return {"unidad_b1": rel(d), "registro_validacion": rel(v), "fuentes": {k: {"ruta": rel(p), "sha256": sha_archivo(p)} for k, p in fu.items()},
            "revalidacion_b1": rv,
            "naturaleza": ("ENLACE-B1-v1: B2 consume los bytes del B1 nuevo: el registro de fam11-validar aceptado para esos bytes y, además, su "
                           "revalidación en este proceso con las funciones del validador B1 (procedencia local, validar_evidencia y lectura; sin "
                           "motor) con la misma lectura y los mismos datos validados. No usa el B1 histórico ni el libro rem167 (sus huellas solo "
                           "se cruzan en la comparación)")}


def revalidar_b1(d: Path, ej: dict, fu: dict) -> dict:
    """ENLACE-B1-v1: rehace, sin escribir y sin el motor, la validación del B1 nuevo con comun_b1/puerta_b1 adaptados (los mismos que
    validar_b1.py): puerta (declaración), procedencia local de la unidad, validar_evidencia y lectura; exige que coincidan con la validación y
    la lectura registradas. Un registro «aceptado» que no corresponda a una validación real de esos bytes no basta."""
    C1 = comun("B1")
    P1 = preparar_b("B1")["puerta_b1"]
    man_p = BASE / ej["argumentos"]["--manifiesto"]
    raw = man_p.read_bytes()
    man = json.loads(raw)
    need(ORIGINAL_B.get(sha(raw)) == MAN_B["B1"][2], "B1_DE_OTRO_MANIFIESTO")
    alc, pv = P1.puerta_comun("produccion", man, C1.H(raw), C1.TAREA_VALIDACION, str(DATOS / DECLARACION), None)
    eh = sha_archivo(fu["b1_evidencia"])
    fp, er, _ = C1.procedencia({"tipo": "lanzamiento", "area": str(d), "lanzamiento": "B1", "evidencia_sha256": eh}, "produccion", C1.H(raw), alc)
    need(not fp, "PROCEDENCIA_B1_NO_AUTENTICA: %s" % fp[:2])
    f, datos = C1.validar_evidencia(man, C1.H(raw), er, "produccion", alc, C1.HF(C1.AQUI / "PAQUETE_B1.json"), pv)
    need(not f, "EVIDENCIA_B1_NO_VALIDA: %s" % [str(x)[:120] for x in f[:3]])
    va, le = leer(fu["b1_validacion"]), leer(fu["b1_lectura"])
    lec = C1.lectura(man, datos)
    need(C1.canon(lec) == C1.canon(le.get("lectura")) and C1.canon(datos) == C1.canon(le.get("datos_validados")) == C1.canon(va.get("datos")),
         "LECTURA_O_DATOS_B1_DISTINTOS_DE_SU_REVALIDACION")
    need(va.get("aceptada") is True and va.get("dictamen") == "validada" and va.get("evidencia_sha256") == eh == le.get("evidencia_sha256")
         and va.get("lectura_sha256") == sha_archivo(fu["b1_lectura"]) and va.get("alcance_sha256") == alc == le.get("alcance_sha256"),
         "VALIDACION_B1_INCOHERENTE_CON_SU_REVALIDACION")
    return {"procedencia": "conforme", "evidencia": "validada", "lectura_igual": True, "U_C2_hex": datos["U_C2_hex"],
            "grupos": {g["grupo"]: g["lectura"] for g in lec["grupos"]}}


def _fijar_enlace(C, enlace: dict | None):
    C.ENLACE_B1.clear()
    if enlace:
        for k, v in enlace["fuentes"].items():
            need(sha_archivo(BASE / v["ruta"]) == v["sha256"], "ENLACE_B1_ALTERADO: %s" % k)
            C.ENLACE_B1[k] = (v["ruta"], v["sha256"])
    C._CONSTRUIDO.clear()


def correr_b(u: str, salida: Path, b1=None, validacion_b1=None) -> dict:
    T0, c0 = time.time(), time.process_time()
    rastro = F1().Rastro()
    need((u == "B2") == (b1 is not None) and (b1 is None) == (validacion_b1 is None), "--b1 Y --validacion-b1 SOLO (Y SIEMPRE) PARA B2")
    malos = fuentes_alteradas("calculo")
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam11.json; no se calcula): %s" % malos[:5])
    hdec, _ = declaracion()
    enlace = enlace_b1(b1, validacion_b1) if u == "B2" else None
    C = comun(u)
    _fijar_enlace(C, enlace)
    need(F5.identidad_c0() == F5.C0_IDENTIDAD, "NUCLEO_C0_DE_OTRA_IDENTIDAD (no se calcula)")
    man_enl = None
    if u == "B2":            # el manifiesto enlazado se reconstruye ANTES de crear la salida: un B1 incoherente se niega sin carpeta
        man_enl = (json.dumps(C.construir_manifiesto(), ensure_ascii=False, indent=1) + "\n").encode("utf-8")
        need(not C.validar_cobertura(json.loads(man_enl)), "COBERTURA_DEL_MANIFIESTO_ENLAZADO_NO_CONFORME")
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    sal = salida.resolve()
    if u == "B1":
        man_p = BASE / MAN_B["B1"][0]
    else:
        man_p = sal / "MANIFIESTO_B2_ENLAZADO.json"
        man_p.write_bytes(man_enl)
    op = {"--modo": "produccion", "--manifiesto": man_p, "--salida": sal / "TRABAJO", "--alcance": DATOS / DECLARACION}
    inicio = utc()
    a0 = time.time()
    rc, ult, stdout, exc = guion_b(u, SCRIPTS_B[u][0], [x for k, v in op.items() for x in (k, v)])
    t_calc = round(time.time() - a0, 2)
    fin = utc()
    (sal / "trabajo_stdout.txt").write_text(stdout, encoding="utf-8")
    informe = rastro.informe()
    (sal / "archivos_leidos.json").write_bytes((json.dumps(informe, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    evp = sal / "TRABAJO" / DOCS_B[u][1][1]
    ej = {"etiqueta": ETIQUETA, "unidad": u, "tarea": C.TAREA_TRABAJO, "operacion": "F11-" + u,
          "naturaleza": ("cálculo: trabajador %s del paquete (bytes exactos, GUION-v1) con su cierre C0 cargado desde los bytes autenticados de "
                         "nucleo_s6/c0 en un proceso propio; sin puerta de producción (PUERTA-v1)" % SCRIPTS_B[u][0]),
          "adaptaciones": ["GUION-v1", "MODULOS-v1", "NUCLEO-C0-v1", "RUTAS-FUENTES-v1", "SANEADO-v1", "RAIZ-MARCADORES-v1", "PUERTA-v1",
                           "PROCEDENCIA-LOCAL-v1", "PAQUETE-v1"] + (["ENLACE-B1-v1"] if u == "B2" else []),
          "argumentos": {k: (v if k == "--modo" else rel(v)) for k, v in op.items()}, "rc": rc, "excepcion": exc, "ultima_linea": ult,
          "inicio_utc": inicio, "fin_utc": fin, "enlace_b1": enlace, "etiqueta_declaracion": ETIQUETA, "declaracion_sha256": hdec,
          "manifiesto": {"archivo": rel(man_p), "sha256": sha_archivo(man_p), "original": MAN_B[u][2] if u == "B1" else None,
                         "nota": None if u == "B1" else "MANIFIESTO_B2_ENLAZADO.json: reconstruido con el B1 nuevo; frente a la proyección solo cambian b1/* y fuentes/b1_*"},
          "evidencia_sha256": sha_archivo(evp) if evp.is_file() else None,
          "adaptado_sha256": {n: sha(adaptado(n).encode("utf-8")) for n in CODIGO if n.startswith("nucleo_s6/%s/" % u.lower())},
          "nucleo": {"identidad": F5.identidad_c0(), "paper2b_cargado": _paper2b_cargado()},
          "tiempos_s": {"calculo": t_calc, "total": round(time.time() - T0, 2), "cpu": round(time.process_time() - c0, 2)},
          "entorno": entorno_b(), "lecturas": lecturas(rastro, informe), "dependencias_fuera_de_la_biblioteca_estandar": F1().dependencias_cargadas()}
    ej["termino"] = exc is None and rc in (0, 4)
    ej["exito"] = exc is None and rc == 0 and ult.get("estado") == "complete" and ej["evidencia_sha256"] == ult.get("evidencia_sha256")
    _escribir(sal / "ejecucion.json", ej)
    return ej


# ================================================================================================ validación (sin cálculo)
def validar(nueva: Path) -> dict:
    """fam11-validar: SIN CÁLCULO. COV: validar_lote.py ABL-COV; B1/B2: validar_bX.py en una carpeta nueva de la unidad."""
    nueva = Path(nueva).resolve()
    ej = leer(nueva / "ejecucion.json") if (nueva / "ejecucion.json").is_file() else {}
    if ej.get("unidad") in UNIDADES_B:
        return validar_b(nueva, ej)
    t0 = time.time()
    malos = fuentes_alteradas("calculo")
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam11.json; no se valida): %s" % malos[:5])
    rb = (nueva / "resultado.json").read_bytes() if (nueva / "resultado.json").is_file() else b"{}"
    res = json.loads(rb)
    rc, ver, _, exc = guion_cov("nucleo_s6/cov/validar_lote.py", [BASE, DATOS / MAN_COV[0], nueva / "resultado.json", nueva / "salida"])
    ns = ("nucleo_s6/cov/validar_lote.py", "nucleo_s6/cov/validar_coord_rec.py")
    return {"comando": "fam11-validar", "naturaleza": "validación sin cálculo de bytes guardados", "tarea": res.get("tarea"), "unidad": res.get("tarea"),
            "origen": rel(nueva), "resultado_sha256": sha(rb), "productos_sha256": productos_de(nueva, res),
            "validador": {"archivos": {n: CODIGO[n] for n in ns}, "adaptacion": {n: [x[0] for x in SUSTITUCIONES[n]] for n in ns},
                          "adaptado_sha256": {n: sha(adaptado(n).encode("utf-8")) for n in ns}, "nucleo": "nucleo_s6/c0 (NUCLEO-C0-v1)"},
            "rc": rc, "veredicto": ver, "excepcion": exc,
            "aceptada": exc is None and rc == 0 and ver.get("aceptada") is True and ver.get("dictamen") == "completa_validada", "segundos": round(time.time() - t0, 3)}


def validar_b(nueva: Path, ej: dict) -> dict:
    t0 = time.time()
    rastro = F1().Rastro()
    u = ej["unidad"]
    malos = fuentes_alteradas("calculo")
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam11.json; no se valida): %s" % malos[:5])
    need(ej.get("etiqueta") == ETIQUETA, "UNIDAD_SIN_EJECUCION_FAM11")
    enlace = ej.get("enlace_b1")
    if u == "B2":
        need(enlace and enlace_b1(BASE / enlace["unidad_b1"], BASE / enlace["registro_validacion"]) == enlace, "ENLACE_B1_DISTINTO_DEL_REGISTRADO")
    C = comun(u)
    _fijar_enlace(C, enlace if u == "B2" else None)
    i = 1
    while (nueva / ("VALIDACION" if i == 1 else "VALIDACION_%d" % i)).exists():
        i += 1
    vdir = nueva / ("VALIDACION" if i == 1 else "VALIDACION_%d" % i)
    man_p = BASE / ej["argumentos"]["--manifiesto"]
    h_ev = (ej.get("ultima_linea") or {}).get("evidencia_sha256")
    args = [man_p, "produccion", vdir, "--area", nueva, "--lanzamiento", u, "--alcance", DATOS / DECLARACION]
    if isinstance(h_ev, str):
        args[5:5] = []
        args += ["--evidencia-sha256", h_ev]
    rc, ver, stdout, exc = guion_b(u, SCRIPTS_B[u][1], args)
    if vdir.is_dir():
        (vdir / "validacion_stdout.txt").write_text(stdout, encoding="utf-8")
    vf, lf = vdir / DOCS_B[u][2][1], vdir / DOCS_B[u][3][1]
    evp = nueva / "TRABAJO" / DOCS_B[u][1][1]
    informe = rastro.informe()
    return {"comando": "fam11-validar", "naturaleza": "validación sin cálculo (validador del paquete; no llama al encierro ni al modelo)", "unidad": u,
            "tarea": C.TAREA_VALIDACION, "origen": rel(nueva), "validacion_dir": rel(vdir), "manifiesto": rel(man_p),
            "manifiesto_sha256": sha_archivo(man_p), "evidencia_sha256": sha_archivo(evp) if evp.is_file() else None,
            "validacion_sha256": sha_archivo(vf) if vf.is_file() else None, "lectura_sha256": sha_archivo(lf) if lf.is_file() else None,
            "enlace_b1": enlace if u == "B2" else None, "rc": rc, "veredicto": ver, "excepcion": exc,
            "aceptada": exc is None and rc == 0 and ver.get("aceptada") is True and ver.get("dictamen") == "validada" and lf.is_file(),
            "lecturas": lecturas(rastro, informe), "entorno": entorno_b(), "segundos": round(time.time() - t0, 3)}


def _validacion_de(val: dict | None, nueva: Path, rb: bytes, res: dict, tarea: str) -> list:
    if val is None:
        return ["VALIDACION_AUSENTE"]
    mot = []
    if val.get("comando") != "fam11-validar" or val.get("origen") != rel(nueva) or val.get("resultado_sha256") != sha(rb) \
            or val.get("productos_sha256") != productos_de(nueva, res) or val.get("tarea") != tarea:
        mot.append("VALIDACION_DE_OTROS_BYTES")
    if val.get("aceptada") is not True:
        mot.append("VALIDACION_NO_ACEPTADA: %s" % ((val.get("veredicto") or {}).get("fallos") or [])[:3])
    return mot


# ================================================================================================ comparación
# COMPARACION-FAM11-v1. Mismo perfil de entorno .venv-fam01 y MISMO núcleo C0 que las referencias. CR-HASH-CANONICO (cada fila o documento
# idéntico campo a campo: valores, cotas, errores en sus dos escalas, encierros en binario) y CR-DISCRETOS (claves, celdas, estados,
# clasificaciones, lecturas, garantías y conteos, con precedencia). Las tolerancias internas de los validadores son suyas y no se usan aquí.
# Se apartan, visibles, solo: OPERATIVO (duraciones e instantes medidos); UBICACION (carpetas y rutas); PUERTA (puerta nativa, procedencia
# p3ctl frente al registro local y los campos del acto/libro histórico de B1); VINCULO (huellas derivadas: alcance = declaración frente al
# alcance histórico, manifiesto/índice = proyección frente a original, evidencia/validación/lectura nuevas frente a las del libro), que se
# recomprueban una a una.
def _fs(q) -> str:
    q = Fraction(q)
    return str(q.numerator) if q.denominator == 1 else "%d/%d" % (q.numerator, q.denominator)


def _cmp_doc(n: dict, r: dict, oper=(), ubic=(), puerta=(), vinc: dict | None = None) -> dict:
    """Documento nuevo frente al de referencia, hoja a hoja. vinc: {regex del puntero: (valor nuevo esperado, valor de referencia esperado)}."""
    hn, hr = F5.hojas(n), F5.hojas(r)
    out = {"operativos": [], "ubicacion": [], "puerta": [], "vinculos": [], "discretas": [], "numericas": []}
    vinc = vinc or {}
    vistos = set()
    for p in sorted(set(hn) | set(hr)):
        a, b = hn.get(p, "<ausente>"), hr.get(p, "<ausente>")
        v = next((k for k in vinc if re.fullmatch(k, p)), None)
        if v is not None:
            vistos.add(v)
            out["vinculos"].append({"puntero": p, "nueva_ligada": a == vinc[v][0], "referencia_ligada": vinc[v][1] is None or b == vinc[v][1]})
        elif any(re.fullmatch(x, p) for x in puerta):
            out["puerta"].append({"puntero": p, "nueva": a, "referencia": b})
        elif any(re.fullmatch(x, p) for x in ubic):
            out["ubicacion"].append({"puntero": p, "nueva": a, "referencia": b})
        elif any(re.fullmatch(x, p) for x in oper):
            out["operativos"].append({"puntero": p, "nueva": a, "referencia": b})
        elif json.dumps(a) != json.dumps(b):
            numerico = all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in (a, b))
            (out["numericas"] if numerico else out["discretas"]).append({"puntero": p, "nueva": a, "referencia": b})
    out["vinculos_completos"] = vistos == set(vinc) and all(x["nueva_ligada"] and x["referencia_ligada"] for x in out["vinculos"])
    out["iguales_salvo_apartados"] = not out["discretas"] and not out["numericas"] and out["vinculos_completos"]
    return out


def comparar(tarea: str, nueva: Path, validacion: Path | None = None) -> dict:
    if tarea in TAREAS:
        return comparar_cov(tarea, nueva, validacion)
    if tarea in UNIDADES_B:
        return comparar_b(tarea, nueva, validacion)
    need(tarea == ENSAMBLADO, "TAREA_DE_COMPARACION_DESCONOCIDA: %s" % tarea)
    return comparar_ensamblado(nueva)


def comparar_cov(tarea: str, nueva: Path, validacion: Path) -> dict:
    """fam11-comparar --tarea ABL-COV-T*: salida de fam11-unidad frente a la tarea aceptada (bytes guardados de rem151) y la validación frente
    a la histórica."""
    nueva = Path(nueva).resolve()
    raw, man = manifiesto_cov()
    co = man["ABL-COV"]
    mot = []
    ej = leer(nueva / "ejecucion.json") if (nueva / "ejecucion.json").is_file() else {}
    rb = (nueva / "resultado.json").read_bytes() if (nueva / "resultado.json").is_file() else b"{}"
    res = json.loads(rb)
    if ej.get("tarea") != tarea or res.get("tarea") != tarea or ej.get("etiqueta") != ETIQUETA:
        mot.append("SALIDA_DE_OTRA_TAREA_O_SIN_EJECUCION_FAM11")
    val = leer(validacion) if validacion and Path(validacion).is_file() else None
    mot += _validacion_de(val, nueva, rb, res, tarea)
    ref_d = GUARD / tarea
    pin = pines()[tarea]
    ref_rb = (ref_d / "resultado.json").read_bytes()
    ref_res = json.loads(ref_rb)
    if sha(ref_rb) != pin["resultado_sha256"] or sha(ref_rb) != pin["libro_resultado_sha256"] \
            or any(sha_archivo(ref_d / "salida" / n) != pin["productos"][n] for n in PRODUCTOS):
        mot.append("REFERENCIA_ALTERADA_O_AJENA: %s" % tarea)
    if res.get("estado") != ref_res.get("estado"):
        mot.append("ESTADO_DISTINTO_DEL_ACEPTADO: %s frente a %s" % (res.get("estado"), ref_res.get("estado")))
    hdec = sha_archivo(DATOS / DECLARACION)
    decl = {p["archivo"]: p for p in res.get("productos") or []}
    objetos, deriv = {}, {}
    for n in PRODUCTOS:
        fref, fn = ref_d / "salida" / n, nueva / "salida" / n
        d = decl.get(n)
        if d is None or sha_archivo(fn) != d.get("sha256"):
            mot.append("PRODUCTO_AUSENTE_O_ALTERADO: %s" % n)
            continue
        es_techo = n == PRODUCTOS[0]
        o = F7.comparar_filas(F8._lineas(fn), F8._lineas(fref), ("clave_transformada_sha256",) if es_techo else ("unidad", "cell_id"),
                              ("/segundos",) if es_techo else (), {None: {"/alcance_sha256": (res.get("alcance_sha256"), ref_res.get("alcance_sha256"))}} if es_techo else None)
        F8._motivos_filas(o, n, mot, bytes_exactos=not es_techo)
        if es_techo:
            v = o["vinculo"]
            if not (v["filas"] == v["nueva_ligada"] == v["referencia_ligada"] == o["cobertura"]["filas_referencia"]) or res.get("alcance_sha256") != hdec \
                    or ref_res.get("alcance_sha256") != ALC_COV[1]:
                mot.append("VINCULO_ROTO: alcance_sha256 (nueva = declaración de ejecución limpia; referencia = alcance histórico)")
            deriv["huella_derivada_de_los_techos"] = F7.huella_derivada(fn.read_bytes(), fref.read_bytes())
            if not deriv["huella_derivada_de_los_techos"]["igual"] and not o["n_discretas"] and not o["n_numericas"]:
                mot.append("HUELLA_DERIVADA_DISTINTA: techos")
        objetos[n] = o
    nuevas_t = leer_jsonl(nueva / "salida" / PRODUCTOS[0]) if (nueva / "salida" / PRODUCTOS[0]).is_file() else []
    nuevas_c = leer_jsonl(nueva / "salida" / PRODUCTOS[1]) if (nueva / "salida" / PRODUCTOS[1]).is_file() else []
    ref_t = leer_jsonl(ref_d / "salida" / PRODUCTOS[0])
    por_t = {t["clave_transformada_sha256"]: t for t in nuevas_t}
    cel = [c for c in co["celdas_afectadas"] if c["clave_transformada_sha256"] in co["tareas"][tarea]]
    cert = [t for t in nuevas_t if t.get("estado") == "complete" and t.get("error_kind") == "certified_bound" and t.get("garantia") == "ieee754_binary64_rn"
            and (t.get("error_normalizado") or 1) <= 1e-7 and (t.get("cierre_por_escala") or {}).get("normalizada") is True]
    deriv["techos_certificados_y_cerrados_en_escala_normalizada"] = len(cert)
    deriv["techos_con_error_R_mayor_que_1e-7"] = {"nueva": sum(1 for t in nuevas_t if (t.get("error_R") or 0) > 1e-7),
                                                   "referencia": sum(1 for t in ref_t if (t.get("error_R") or 0) > 1e-7),
                                                   "nota": "aceptación en la escala normalizada; error_R > 1e-7 no rechaza (8 de 26 en la producción aceptada)"}
    deriv["comparaciones_G_igual_C2_menos_K1"] = sum(1 for x in nuevas_c if F7.g_ok(x, por_t.get(x.get("clave_transformada_sha256"))))
    deriv["cobertura"] = {"claves": sorted(por_t) == sorted(co["tareas"][tarea]), "celdas": sorted((x["unidad"], x["cell_id"]) for x in nuevas_c)
                          == sorted((c["unidad"], c["cell_id"]) for c in cel), "techos": len(nuevas_t), "comparaciones": len(nuevas_c)}
    if not (deriv["cobertura"]["claves"] and deriv["cobertura"]["celdas"] and len(cert) == len(nuevas_t) == len(co["tareas"][tarea])
            and deriv["comparaciones_G_igual_C2_menos_K1"] == len(nuevas_c) == len(cel)
            and deriv["techos_con_error_R_mayor_que_1e-7"]["nueva"] == deriv["techos_con_error_R_mayor_que_1e-7"]["referencia"]):
        mot.append("COBERTURA_CERTIFICADOS_O_CLASIFICACION_INCOMPLETOS")
    rr = F8._resultado_igual(res, ref_res, mot)
    ident = {"manifiesto_sha256": res.get("manifiesto_sha256") == ref_res.get("manifiesto_sha256") == MAN_COV[1],
             "codigo_sha256": res.get("codigo_sha256") == ref_res.get("codigo_sha256") == {Path(n).name: CODIGO[n] for n in ("nucleo_s6/cov/tarea_lote.py", "nucleo_s6/cov/conexion_coord_cert.py")},
             "nucleo_c0": (ej.get("nucleo") or {}).get("identidad") == F5.C0_IDENTIDAD,
             "producto_de_comparaciones_igual": (decl.get(PRODUCTOS[1]) or {}).get("sha256") == pin["productos"][PRODUCTOS[1]]}
    if not all(ident.values()):
        mot.append("IDENTIDAD_DISTINTA: %s" % [k for k, v in ident.items() if not v])
    vh = json.loads((REF / "rem151" / tarea / "validacion_stdout.txt").read_text(encoding="utf-8"))
    vn = (val or {}).get("veredicto") or {}
    deriv["validacion_frente_a_la_historica"] = {
        "iguales_salvo_huellas_propias": {k: v for k, v in vn.items() if k not in ("resultado_sha256", "productos_sha256")}
        == {k: v for k, v in vh.items() if k not in ("resultado_sha256", "productos_sha256")},
        "huellas_propias": vn.get("resultado_sha256") == sha(rb) and vn.get("productos_sha256") == productos_de(nueva, res)}
    if not all(deriv["validacion_frente_a_la_historica"].values()):
        mot.append("VALIDACION_DISTINTA_DE_LA_HISTORICA")
    th = F8._ultima(REF / "rem151" / tarea / "trabajo_stdout.txt")
    tn = F8._ultima(nueva / "trabajo_stdout.txt")
    deriv["salida_del_trabajador"] = {"igual_salvo_pared_s": {k: v for k, v in tn.items() if k != "pared_s"} == {k: v for k, v in th.items() if k != "pared_s"}}
    if not deriv["salida_del_trabajador"]["igual_salvo_pared_s"]:
        mot.append("SALIDA_DEL_TRABAJADOR_DISTINTA")
    return {"comando": "fam11-comparar", "tarea": tarea, "operacion": "F11-COV26", "regla": "COMPARACION-FAM11-v1 (src/fam11.py)",
            "criterios": ["CR-HASH-CANONICO (mismo entorno y núcleo C0; exacta)", "CR-DISCRETOS (precedencia)",
                          "OPERATIVO segundos/pared_s y VINCULO alcance_sha256 (apartados, visibles)"],
            "referencia": {"ejecucion": rel(ref_d), "resultado_sha256": sha(ref_rb), "productos": pin["productos"]},
            "nueva": rel(nueva), "validacion": rel(Path(validacion)) if validacion else None, "objetos": objetos, "resultado": rr, "identidades": ident,
            "derivados": deriv,
            "operativos": {"pared_s": {"nueva": res.get("pared_s"), "referencia": ref_res.get("pared_s")},
                           "segundos_por_techo": {"nueva": {t["clave_transformada_sha256"]: t.get("segundos") for t in nuevas_t},
                                                  "referencia": {t["clave_transformada_sha256"]: t.get("segundos") for t in ref_t}}},
            "estado": {"reproduccion": "aceptada" if not mot else "no_aceptada", "motivos": mot}}


def _saneado() -> dict:
    return {x["archivo"]: (x["sha256"], x["sha256_original"]) for x in fuentes().get("saneado") or []}


def _libro(n: str) -> dict:
    return (fuentes().get("libros") or {}).get(n) or {}


def _ref_b(u: str) -> dict:
    """Bytes de referencia de B1 (rem166) o B2 (rem169): proyección declarada y su original fijado por el libro (rem167 / rem170)."""
    sane, lb = _saneado(), _libro("rem167" if u == "B1" else "rem170")
    arch = {x["archivo"]: x["sha256"] for x in fuentes()["archivos"]}
    out = {}
    for d, n in DOCS_B[u]:
        a = rel(REF_B[u] / d / n)
        hp = sha_archivo(BASE / a)
        ho = sane.get(a, (hp, hp))[1]
        out[n] = {"archivo": a, "sha256": hp, "original": ho, "declarado": hp == (sane.get(a, (None,))[0] or arch.get(a)),
                  "en_el_libro": (lb.get("productos") or {}).get(n) == ho}
    return out


def _vinc_b(u: str, nueva: Path, val: dict | None, ej: dict) -> tuple:
    """Vínculos de B1/B2: (nuevo esperado, referencia esperada) por puntero; y los punteros apartados (operativos, ubicación, puerta)."""
    hdec = sha_archivo(DATOS / DECLARACION)
    refs = _ref_b(u)
    trab = nueva / "TRABAJO"
    vdir = BASE / ((val or {}).get("validacion_dir") or "<sin validación>")
    n_ev, n_va, n_le = (sha_archivo(trab / DOCS_B[u][1][1]) if (trab / DOCS_B[u][1][1]).is_file() else None,
                        sha_archivo(vdir / DOCS_B[u][2][1]) if (vdir / DOCS_B[u][2][1]).is_file() else None,
                        sha_archivo(vdir / DOCS_B[u][3][1]) if (vdir / DOCS_B[u][3][1]).is_file() else None)
    r_ev, r_va, r_le = (refs[DOCS_B[u][i][1]]["original"] for i in (1, 2, 3))
    man_n = (ej.get("manifiesto") or {}).get("sha256")
    v = {r"/manifiesto_sha256": (man_n, MAN_B[u][2]), r"/indice_sha256": (IDX_B[u][1], IDX_B[u][2]), r"/alcance_sha256": (hdec, None),
         r"/evidencia_sha256": (n_ev, r_ev), r"/lectura_sha256": (n_le, r_le)}
    oper = (r"/inicio_utc", r"/fin_utc", r"/solicitud/(inicio_utc|fin_utc|pared_s)", r"/estadisticas/segundos", r"/(datos|datos_validados)/segundos_encierro")
    ubic = (r"/pieza/ruta",)
    puerta = (r"/puerta_nativa(/.*)?", r"/procedencia(/.*)?")
    if u == "B2":
        b1 = (ej.get("enlace_b1") or {}).get("fuentes") or {}
        r1 = _ref_b("B1")
        v.update({r"/b1/evidencia_sha256": ((b1.get("b1_evidencia") or {}).get("sha256"), r1["EVIDENCIA_B1.json"]["original"]),
                  r"/b1/validacion_sha256": ((b1.get("b1_validacion") or {}).get("sha256"), r1["VALIDACION_B1.json"]["original"]),
                  r"/b1/lectura_sha256": ((b1.get("b1_lectura") or {}).get("sha256"), r1["LECTURA_B1.json"]["original"]),
                  r"/b1/estado_sha256": ((b1.get("b1_estado") or {}).get("sha256"), (_libro("rem167").get("productos") or {}).get("estado_b1.json"))})
        puerta += (r"/b1/(libro_sha256|acto_B1(/.*)?|alcance_B1_sha256)",)
    return v, oper, ubic, puerta, (n_ev, n_va, n_le)


def comparar_b(u: str, nueva: Path, validacion: Path | None) -> dict:
    """fam11-comparar --tarea B1|B2: documentos y salidas de la unidad nueva frente a la producción aceptada (rem166 / rem169) y, en B2, la
    resolución de las doce afirmaciones frente a la aceptada en rem170."""
    nueva = Path(nueva).resolve()
    mot = []
    ej = leer(nueva / "ejecucion.json") if (nueva / "ejecucion.json").is_file() else {}
    if ej.get("unidad") != u or ej.get("etiqueta") != ETIQUETA:
        mot.append("SALIDA_DE_OTRA_UNIDAD_O_SIN_EJECUCION_FAM11")
    val = leer(validacion) if validacion and Path(validacion).is_file() else None
    vinc, oper, ubic, puerta, (n_ev, n_va, n_le) = _vinc_b(u, nueva, val, ej)
    if val is None:
        mot.append("VALIDACION_AUSENTE")
    else:
        if val.get("comando") != "fam11-validar" or val.get("unidad") != u or val.get("origen") != rel(nueva) \
                or (val.get("evidencia_sha256"), val.get("validacion_sha256"), val.get("lectura_sha256")) != (n_ev, n_va, n_le) or n_ev is None:
            mot.append("VALIDACION_DE_OTROS_BYTES")
        if val.get("aceptada") is not True:
            mot.append("VALIDACION_NO_ACEPTADA: %s" % ((val.get("veredicto") or {}).get("fallos") or [])[:3])
    if not ej.get("exito"):
        mot.append("CALCULO_NO_COMPLETO: %s" % (ej.get("ultima_linea") or {}).get("motivo"))
    refs = _ref_b(u)
    if not all(x["declarado"] and x["en_el_libro"] for x in refs.values()):
        mot.append("REFERENCIA_ALTERADA_O_AJENA: %s" % [n for n, x in refs.items() if not (x["declarado"] and x["en_el_libro"])])
    vdir = BASE / ((val or {}).get("validacion_dir") or "<sin validación>")
    docs = {}
    for d, n in DOCS_B[u]:
        pn = (nueva / "TRABAJO" / n) if d == "TRABAJO" else (vdir / n)
        dn = leer(pn) if pn.is_file() else {}
        docs[n] = _cmp_doc(dn, leer(REF_B[u] / d / n), oper, ubic, puerta, {k: x for k, x in vinc.items()
                                                                            if any(re.fullmatch(k, p) for p in F5.hojas(dn))})
        if not dn:
            mot.append("DOCUMENTO_AUSENTE: %s" % n)
        elif not docs[n]["iguales_salvo_apartados"]:
            mot.append("DOCUMENTO_DISTINTO: %s %s" % (n, [x["puntero"] for x in (docs[n]["discretas"] + docs[n]["numericas"])[:4]]
                                                     + [x["puntero"] for x in docs[n]["vinculos"] if not (x["nueva_ligada"] and x["referencia_ligada"])][:4]))
    salidas = {}
    for i, (n_s, p_n) in enumerate(zip(STDOUT_B[u], (nueva / "trabajo_stdout.txt", vdir / "validacion_stdout.txt"))):
        sn, sr = F8._ultima(p_n), F8._ultima(REF_B[u] / n_s)
        salidas[n_s] = _cmp_doc(sn, sr, vinc={k: x for k, x in vinc.items() if any(re.fullmatch(k, p) for p in F5.hojas(sn))})
        if not sn or not salidas[n_s]["iguales_salvo_apartados"]:
            mot.append("SALIDA_DISTINTA: %s" % n_s)
    deriv = {}
    ev = leer(nueva / "TRABAJO" / DOCS_B[u][1][1]) if (nueva / "TRABAJO" / DOCS_B[u][1][1]).is_file() else {}
    le = leer(vdir / DOCS_B[u][3][1]) if (vdir / DOCS_B[u][3][1]).is_file() else {}
    lec = le.get("lectura") or {}
    if u == "B1":
        lb = _libro("rem167")
        deriv["U_C2"] = {"hex": ev.get("U_C2_hex"), "igual_al_libro": ev.get("U_C2_hex") == lb.get("U_C2_hex") == U_C2_HEX,
                         "exacto": _fs(ev["U_C2"]) if isinstance(ev.get("U_C2"), float) else None,
                         "naturaleza": "extremo superior CERTIFICADO del encierro (redondeo hacia afuera); no es un máximo ni un argmax"}
        deriv["lectura"] = {"grupos": {g["grupo"]: g["lectura"] for g in lec.get("grupos") or []},
                            "afirmaciones": dict(Counter(a["lectura"] for a in lec.get("afirmaciones") or [])),
                            "umbrales_iguales_al_libro": {g["grupo"]: g.get("umbral_exacto") == ((lb.get("lectura_por_grupo") or {}).get(g["grupo"]) or {}).get("threshold_exact")
                                                          for g in lec.get("grupos") or []}}
        if not (deriv["U_C2"]["igual_al_libro"] and deriv["lectura"]["grupos"] == {g: "candidato_B2" for g in GRUPOS}
                and deriv["lectura"]["afirmaciones"] == {"candidato_B2": 12} and all(deriv["lectura"]["umbrales_iguales_al_libro"].values())):
            mot.append("LECTURA_B1_DISTINTA_DEL_LIBRO")
    else:
        lb = _libro("rem170")
        g_ev = ev.get("grupos") or {}
        deriv["grupos"] = {g: {"contextos": (g_ev.get(g) or {}).get("contextos"), "pendientes": (g_ev.get(g) or {}).get("pendientes"),
                               "L_K1_hex": (g_ev.get(g) or {}).get("L_K1_hex"),
                               "G_hi_exacto": next((x.get("G_hi_exacto") for x in lec.get("grupos") or [] if x["grupo"] == g), None),
                               "lectura": next((x.get("lectura") for x in lec.get("grupos") or [] if x["grupo"] == g), None)} for g in GRUPOS}
        deriv["grupos_iguales_al_libro"] = {g: (d["contextos"], d["L_K1_hex"], d["G_hi_exacto"], d["pendientes"])
                                            == (((lb.get("grupos") or {}).get(g) or {}).get("contexts"), ((lb.get("grupos") or {}).get(g) or {}).get("L_K1_hex"),
                                                ((lb.get("grupos") or {}).get(g) or {}).get("G_hi_exact"), 0) for g, d in deriv["grupos"].items()}
        ll = ev.get("llamadas_trabajo") or {}
        deriv["llamadas"] = {"macro.bridge": ll.get("macro.bridge"), "GridCell.Q": ll.get("GridCell.Q"), "k1_intervalar": ll.get("k1_intervalar"),
                             "new_C2": ll.get("C2"), "iguales_al_libro": (ll.get("macro.bridge"), ll.get("GridCell.Q"), ll.get("k1_intervalar"), ll.get("C2"))
                             == tuple((lb.get("llamadas") or {}).get(k) for k in ("macro.bridge", "GridCell.Q", "k1_intervalar", "new_C2")) == (480, 60, 1920, 0)}
        deriv["regla"] = {g: (Fraction(d["G_hi_exacto"]) <= -EPS) == (d["lectura"] == "certifica_G_negativo") for g, d in deriv["grupos"].items() if d["G_hi_exacto"]}
        # manifiesto enlazado frente a la proyección: solo b1/* y fuentes/b1_* pueden cambiar
        mn = leer(nueva / "MANIFIESTO_B2_ENLAZADO.json") if (nueva / "MANIFIESTO_B2_ENLAZADO.json").is_file() else {}
        b1f = (ej.get("enlace_b1") or {}).get("fuentes") or {}
        docs["MANIFIESTO_B2_ENLAZADO.json"] = _cmp_doc(mn, leer(BASE / MAN_B["B2"][0]), puerta=(r"/b1/(libro_sha256|acto_B1(/.*)?|alcance_B1_sha256)",),
                                                       ubic=(r"/fuentes/b1_(estado|evidencia|validacion|lectura)/ruta",),
                                                       vinc=dict({k: x for k, x in vinc.items() if k.startswith("/b1/")},
                                                                 **{r"/fuentes/%s/sha256" % k: ((b1f.get(k) or {}).get("sha256"), None) for k in ENLACE_CLAVES}))
        if not docs["MANIFIESTO_B2_ENLAZADO.json"]["iguales_salvo_apartados"] or not mn:
            mot.append("MANIFIESTO_ENLAZADO_DISTINTO_DE_LA_PROYECCION_FUERA_DE_B1")
        deriv["resolucion_doce"] = comparar_resolucion(lec, mn, ev)
        if not (all(deriv["grupos_iguales_al_libro"].values()) and deriv["llamadas"]["iguales_al_libro"] and all(deriv["regla"].values())
                and len(deriv["regla"]) == 6 and deriv["resolucion_doce"]["iguales"]):
            mot.append("RESULTADO_B2_DISTINTO_DEL_LIBRO_O_DE_LA_RESOLUCION")
    return {"comando": "fam11-comparar", "tarea": u, "operacion": "F11-" + u, "regla": "COMPARACION-FAM11-v1 (src/fam11.py)",
            "criterios": ["CR-HASH-CANONICO (mismo entorno y núcleo C0; exacta)", "CR-DISCRETOS (precedencia)",
                          "OPERATIVO, UBICACION, PUERTA y VINCULO apartados y visibles (vínculos recomprobados)"],
            "referencia": {n: {k: x[k] for k in ("archivo", "sha256", "original")} for n, x in refs.items()},
            "nueva": rel(nueva), "validacion": rel(Path(validacion)) if validacion else None, "documentos": docs, "salidas": salidas, "derivados": deriv,
            "enlace_b1": ej.get("enlace_b1") if u == "B2" else None,
            "operativos": {"tiempos_s": ej.get("tiempos_s"), "referencia_libro": _libro("rem167" if u == "B1" else "rem170").get("duracion")},
            "estado": {"reproduccion": "aceptada" if not mot else "no_aceptada", "motivos": mot}}


def resolucion_doce(lec: dict, man_b2: dict, ev: dict) -> list:
    """Resolución de las doce desde la lectura B2 nueva: G_hi = U_C2 − L_K1 exacto; robust_infeasible si G_hi <= −1/100 (borde incluido). La
    categoría padre y la conclusión COV histórica salen de la conciliación COV aceptada (entrada de B1) y se conservan aparte."""
    conc = {x["afirmacion"]: x for x in leer_jsonl(DATOS / CONC_FUENTE[0])}
    u_c2 = (man_b2.get("b1") or {}).get("U_C2")
    if not isinstance(u_c2, (float, int, str)) or isinstance(u_c2, bool):
        return []                                   # sin manifiesto enlazado (o sin U_C2): resolución no calculable; la comparación la rechaza
    U = Fraction(u_c2)
    out = []
    for g in lec.get("grupos") or []:
        L = Fraction(g["L_K1"]) if g.get("L_K1") is not None else None
        G = U - L if L is not None else None
        for a in sorted(g.get("afirmaciones") or []):
            c = conc.get(a) or {}
            out.append({"afirmacion": a, "grupo": g["grupo"], "categoria_original": c.get("categoria_original"), "conclusion_COV_historica": c.get("canal_phi"),
                        "conjunto_padre": "inconclusa" if c.get("inconclusa") else "robusta",
                        "veredicto": None if G is None else ("robust_infeasible" if G <= -EPS else "desconocida"),
                        "G_hi": None if G is None else {"exacto": _fs(G), "float": float(G)},
                        "L_K1": None if L is None else {"exacto": _fs(L), "float": float(L), "hex": float.hex(float(L))},
                        "U_C2": {"exacto": _fs(U), "float": float(U), "hex": float.hex(float(U))},
                        "margen_bajo_menos_eps": None if G is None else {"exacto": _fs(-EPS - G), "float": float(-EPS - G)},
                        "afirmaciones_del_grupo": sorted(g["afirmaciones"]), "contextos_del_grupo": ((ev.get("grupos") or {}).get(g["grupo"]) or {}).get("contextos")})
    return sorted(out, key=lambda x: x["afirmacion"])


def comparar_resolucion(lec: dict, man_b2: dict, ev: dict) -> dict:
    nuevas = resolucion_doce(lec, man_b2, ev)
    refs = {x["afirmacion"]: x for x in leer_jsonl(RESOLUCION)}
    filas, iguales = [], bool(nuevas) and len(nuevas) == len(refs) == 12
    for x in nuevas:
        r = refs.get(x["afirmacion"]) or {}
        rg = r.get("resolucion_global") or {}
        esperado = {"grupo": r.get("grupo"), "categoria_original": r.get("categoria_original"), "conclusion_COV_historica": r.get("conclusion_COV_historica"),
                    "conjunto_padre": r.get("conjunto_padre"), "veredicto": rg.get("veredicto"), "G_hi": rg.get("G_hi"),
                    "L_K1": {k: (rg.get("L_K1") or {}).get(k) for k in ("exacto", "float", "hex")},
                    "U_C2": {k: (rg.get("U_C2") or {}).get(k) for k in ("exacto", "float", "hex")}, "margen_bajo_menos_eps": rg.get("margen_bajo_menos_eps"),
                    "afirmaciones_del_grupo": sorted(rg.get("afirmaciones_del_grupo") or []), "contextos_del_grupo": (rg.get("soporte") or {}).get("contextos_del_grupo")}
        nuevo = {k: x[k] for k in esperado}
        dif = [k for k in esperado if json.dumps(nuevo[k], sort_keys=True) != json.dumps(esperado[k], sort_keys=True)]
        iguales = iguales and not dif and r.get("conclusion_COV_vigente") == x["veredicto"]
        filas.append({"afirmacion": x["afirmacion"], "grupo": x["grupo"], "veredicto": x["veredicto"], "G_hi": (x["G_hi"] or {}).get("exacto"),
                      "categoria_original": x["categoria_original"], "diferencias": dif})
    return {"archivo_de_referencia": rel(RESOLUCION), "calculable": bool(nuevas), "comparados": ["grupo", "categoria_original", "conclusion_COV_historica", "conjunto_padre", "veredicto",
                                                                   "G_hi", "L_K1", "U_C2", "margen_bajo_menos_eps", "afirmaciones_del_grupo", "contextos_del_grupo"],
            "no_comparados": "procedencia histórica, textos, líneas y huellas de las síntesis rem160/rem170 (no se recalculan en FAM11; integración = FAM10)",
            "veredictos": dict(Counter(x["veredicto"] for x in nuevas)), "categorias_padre": dict(Counter(x["categoria_original"] for x in nuevas)),
            "filas": filas, "iguales": iguales}


# ================================================================================================ ensamblado y conciliación COV
def entradas_cov(ent: dict) -> tuple:
    """Tareas declaradas: «guardado» (bytes aceptados rem151 en datos/fam11/guardadas) o carpeta de fam11-unidad (con la declaración)."""
    pin = pines()
    hdec = sha_archivo(DATOS / DECLARACION)
    dirs, origen = {}, {}
    for t in TAREAS:
        v = ent.get(t)
        if v is None:
            origen[t] = {"procedencia": "ausente", "nota": "sin carpeta declarada: no se sustituye por la referencia (el ensamblado se rechaza)"}
            continue
        if str(v) == GUARDADO:
            d = GUARD / t
            need(sha_archivo(d / "resultado.json") == pin[t]["resultado_sha256"] == pin[t]["libro_resultado_sha256"]
                 and all(sha_archivo(d / "salida" / n) == pin[t]["productos"][n] for n in PRODUCTOS), "TAREA_GUARDADA_ALTERADA_O_AJENA: %s" % t)
            origen[t] = {"procedencia": "guardada", "carpeta": rel(d), "naturaleza": "salida aceptada rem151 (bytes guardados; no se recalcula ni acredita cálculo nuevo)"}
        else:
            d = Path(v).resolve()
            ej = leer(d / "ejecucion.json") if (d / "ejecucion.json").is_file() else {}
            need(ej.get("etiqueta") == ETIQUETA and ej.get("tarea") == t, "CARPETA_SIN_EJECUCION_FAM11: %s" % t)
            rs = leer(d / "resultado.json")
            need(rs.get("alcance_sha256") == hdec, "TAREA_NUEVA_SIN_LA_DECLARACION_DE_EJECUCION_LIMPIA: %s" % t)
            origen[t] = {"procedencia": "nueva", "carpeta": rel(d), "naturaleza": "salida de fam11-unidad (cálculo nuevo en la base limpia)",
                         "estado_de_su_ejecucion": rs.get("estado"), "resultado_sha256": sha_archivo(d / "resultado.json"),
                         "productos": {n: sha_archivo(d / "salida" / n) for n in PRODUCTOS}}
        dirs[t] = d
    return dirs, origen


def ensamblar(salida: Path, entradas: dict) -> dict:
    """fam11-ensamblar: ensamblar_coord.py (ENSAMBLADOR-ENTRADAS-v1) con una carpeta declarada por tarea y, si el ensamblado es aceptado,
    conciliar_cov.py (ENTRADAS-CONCILIADOR-v1) sobre ese ensamblado. Nunca lee el ensamblado ni la conciliación de referencia."""
    T0 = time.time()
    rastro = F1().Rastro()
    need(set(entradas) <= set(TAREAS), "TAREA_FUERA_DE_LA_PARTICION: %s" % sorted(set(entradas) - set(TAREAS)))
    guard = [rel(GUARD / t) for t, v in entradas.items() if str(v) == GUARDADO]
    malos = fuentes_alteradas("regeneracion", guard)
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam11.json; no se ensambla): %s" % malos[:5])
    raw, man = manifiesto_cov()
    dirs, origen = entradas_cov(entradas)
    proc = {o["procedencia"] for o in origen.values()}
    naturaleza = (REGENERACION if proc == {"guardada"} else NUEVA if proc == {"nueva"} else MIXTA if "ausente" not in proc
                  else "incompleta: faltan tareas (no se sustituyen por referencias)")
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    sal = salida.resolve()
    ent = {"tareas": {t: str(d) for t, d in dirs.items()}, "directorio": {t: rel(d) for t, d in dirs.items()},
           "lanzamiento": {t: rel(d.parent) for t, d in dirs.items()}, "salida": str(sal)}
    a0 = time.time()
    rc, ult, stdout, exc = guion_cov("nucleo_s6/cov/ensamblar_coord.py", [BASE, DATOS / MAN_COV[0], DATOS / COB_COV[0], json.dumps(ent, ensure_ascii=False)])
    t_ens = round(time.time() - a0, 2)
    (sal / "ensamblado_stdout.txt").write_text(stdout, encoding="utf-8")
    E = sal / ENSAMBLADO
    ens_ok = exc is None and rc == 0 and ult.get("aceptada") is True and (E / "ENSAMBLADO.json").is_file()
    conc = {"rc": None, "veredicto": None, "excepcion": None, "nota": "no se concilia: el ensamblado no fue aceptado"}
    t_conc = None
    if ens_ok:
        a0 = time.time()
        rc2, ult2, stdout2, exc2 = guion_cov("src/conciliar_cov.py", [BASE, DATOS / MAN_COV[0], "produccion", E / "ENSAMBLADO.json", DATOS / ENF_AF[0],
                                                                      sal / "CONCILIACION"])
        t_conc = round(time.time() - a0, 2)
        (sal / "conciliacion_stdout.txt").write_text(stdout2, encoding="utf-8")
        conc = {"rc": rc2, "veredicto": ult2, "excepcion": exc2}
    informe = rastro.informe()
    (sal / "archivos_leidos.json").write_bytes((json.dumps(informe, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    ej = {"comando": "fam11-ensamblar", "naturaleza": naturaleza, "etiqueta": ETIQUETA, "manifiesto_sha256": sha(raw), "entradas": origen,
          "acredita": {REGENERACION: "el ensamblado y la conciliación documentales sobre las seis tareas guardadas; NO acredita el cálculo de F11-COV26",
                       MIXTA: "la conexión de las tareas nuevas al ensamblador y al conciliador; las tareas guardadas NO se han ejecutado aquí",
                       NUEVA: "el ensamblado y la conciliación sobre las seis tareas calculadas en la base limpia"}.get(naturaleza, "nada (ensamblado incompleto)"),
          "ensamblador": {"archivo": "nucleo_s6/cov/ensamblar_coord.py", "sha256": CODIGO["nucleo_s6/cov/ensamblar_coord.py"],
                          "adaptacion": [x[0] for x in SUSTITUCIONES["nucleo_s6/cov/ensamblar_coord.py"]],
                          "adaptado_sha256": sha(adaptado("nucleo_s6/cov/ensamblar_coord.py").encode("utf-8"))},
          "conciliador": {"archivo": "src/conciliar_cov.py", "sha256": CODIGO["src/conciliar_cov.py"],
                          "adaptacion": [x[0] for x in SUSTITUCIONES["src/conciliar_cov.py"]], "adaptado_sha256": sha(adaptado("src/conciliar_cov.py").encode("utf-8"))},
          "ensamblado": {"rc": rc, "veredicto": ult, "excepcion": exc}, "conciliacion": conc,
          "productos": {n: sha_archivo(E / n) for n in PRODUCTOS_ENS + ("ENSAMBLADO.json",) if (E / n).is_file()}
          | {n: sha_archivo(sal / "CONCILIACION" / n) for n in PRODUCTOS_CONC if (sal / "CONCILIACION" / n).is_file()},
          "tiempos_s": {"ensamblado": t_ens, "conciliacion": t_conc, "total": round(time.time() - T0, 2)},
          "nucleo": {"identidad": F5.identidad_c0(), "importados": importados_cov()},
          "entorno": entorno_cov(), "lecturas": lecturas(rastro, informe, (rel(REF_ENS), rel(REF_CONC)))}
    ej["exito"] = ens_ok and conc.get("excepcion") is None and conc.get("rc") == 0 and (conc.get("veredicto") or {}).get("aceptada") is True
    _escribir(sal / "ejecucion.json", ej)
    return ej


def recuentos_conciliacion(filas: list) -> dict:
    inc = [x for x in filas if x.get("inconclusa")]
    rob = [x for x in filas if x.get("categoria_original") == "robusta_infactible_certificada"]
    return {"afirmaciones": len(filas), "canal_phi": dict(sorted(Counter(x.get("canal_phi") for x in filas).items())),
            "inconclusas": len(inc), "robustas": len(rob), "canal_phi_inconclusas": dict(sorted(Counter(x.get("canal_phi") for x in inc).items())),
            "canal_phi_robustas": dict(sorted(Counter(x.get("canal_phi") for x in rob).items())),
            "cambios_de_signo_certificados": sum(len(x.get("cambio_de_signo_certificado_COV") or []) for x in filas),
            "categoria_original_igual_a_canal_phi_en_cambios_de_signo": all(x.get("canal_phi") == x.get("canal_eta_f_aceptado")
                                                                            for x in filas if x.get("cambio_de_signo_certificado_COV") and x.get("inconclusa"))}


def comparar_ensamblado(nueva: Path) -> dict:
    """fam11-comparar --tarea ENSAMBLADO: salida de fam11-ensamblar frente al ensamblado y la conciliación aceptados (rem151/rem152)."""
    nueva = Path(nueva).resolve()
    mot = []
    ej = leer(nueva / "ejecucion.json") if (nueva / "ejecucion.json").is_file() else {}
    if ej.get("comando") != "fam11-ensamblar" or ej.get("etiqueta") != ETIQUETA:
        mot.append("SALIDA_SIN_EJECUCION_DE_FAM11_ENSAMBLAR")
    if not ej.get("exito"):
        mot.append("ENSAMBLADO_O_CONCILIACION_NO_ACEPTADOS")
    ref_ok = ({n: sha_archivo(REF_ENS / n) for n in PRODUCTOS_ENS} == ACEPTADO["ensamblado"]
              and {n: sha_archivo(REF_CONC / n) for n in PRODUCTOS_CONC} == ACEPTADO["conciliacion"]
              and _saneado().get(rel(REF_ENS / "ENSAMBLADO.json")) == ACEPTADO["ensamblado_json"] and sha_archivo(REF_ENS / "ENSAMBLADO.json") == ACEPTADO["ensamblado_json"][0])
    if not ref_ok:
        mot.append("REFERENCIA_ALTERADA_O_AJENA: ensamblado/conciliación rem151")
    hdec = sha_archivo(DATOS / DECLARACION)
    pin = pines()
    ents = ej.get("entradas") or {}
    nuevas_t = {t: e for t, e in ents.items() if e.get("procedencia") == "nueva"}
    if any(e.get("procedencia") not in ("nueva", "guardada") for e in ents.values()) or sorted(ents) != list(TAREAS):
        mot.append("ENTRADAS_INCOMPLETAS")
    raw, man = manifiesto_cov()
    co = man["ABL-COV"]
    claves_nuevas = [k for t in nuevas_t for k in co["tareas"][t]]
    E, Cc = nueva / ENSAMBLADO, nueva / "CONCILIACION"
    objetos, deriv = {}, {}
    vt = {(k,): {"/alcance_sha256": (hdec, ALC_COV[1])} for k in claves_nuevas}
    o = F7.comparar_filas(F8._lineas(E / PRODUCTOS_ENS[0]), F8._lineas(REF_ENS / PRODUCTOS_ENS[0]), ("clave_transformada_sha256",), ("/segundos",), vt or None)
    F8._motivos_filas(o, PRODUCTOS_ENS[0], mot, bytes_exactos=not claves_nuevas)
    if claves_nuevas:
        v = o["vinculo"]
        if not (v["filas"] == v["nueva_ligada"] == v["referencia_ligada"] == len(claves_nuevas)):
            mot.append("VINCULO_ROTO: alcance_sha256 de los techos nuevos")
        deriv["huella_derivada_de_los_techos"] = F7.huella_derivada((E / PRODUCTOS_ENS[0]).read_bytes(), (REF_ENS / PRODUCTOS_ENS[0]).read_bytes())
        if not deriv["huella_derivada_de_los_techos"]["igual"]:
            mot.append("HUELLA_DERIVADA_DISTINTA: techos ensamblados")
    objetos[PRODUCTOS_ENS[0]] = o
    o = F7.comparar_filas(F8._lineas(E / PRODUCTOS_ENS[1]), F8._lineas(REF_ENS / PRODUCTOS_ENS[1]), ("unidad", "cell_id"))
    F8._motivos_filas(o, PRODUCTOS_ENS[1], mot)
    objetos[PRODUCTOS_ENS[1]] = o
    o = F7.comparar_filas(F8._lineas(Cc / PRODUCTOS_CONC[0]), F8._lineas(REF_CONC / PRODUCTOS_CONC[0]), ("afirmacion",))
    F8._motivos_filas(o, PRODUCTOS_CONC[0], mot)
    objetos[PRODUCTOS_CONC[0]] = o
    en = leer(E / "ENSAMBLADO.json") if (E / "ENSAMBLADO.json").is_file() else {}
    vin = {}
    for t in nuevas_t:
        vin.update({"/tareas/%s/alcance_sha256" % t: (hdec, ALC_COV[1]), "/tareas/%s/resultado_sha256" % t: (nuevas_t[t].get("resultado_sha256"), pin[t]["resultado_sha256"]),
                    "/tareas/%s/productos/%s" % (t, PRODUCTOS[0]): (nuevas_t[t]["productos"][PRODUCTOS[0]], pin[t]["productos"][PRODUCTOS[0]])})
    if claves_nuevas:
        vin["/productos/" + PRODUCTOS_ENS[0]] = (sha_archivo(E / PRODUCTOS_ENS[0]) if (E / PRODUCTOS_ENS[0]).is_file() else None, ACEPTADO["ensamblado"][PRODUCTOS_ENS[0]])
    docs = {"ENSAMBLADO.json": _cmp_doc(en, leer(REF_ENS / "ENSAMBLADO.json"), ubic=(r"/tareas/[^/]+/(directorio|lanzamiento)",),
                                        vinc={re.escape(k): x for k, x in vin.items()})}
    cj = leer(Cc / PRODUCTOS_CONC[1]) if (Cc / PRODUCTOS_CONC[1]).is_file() else {}
    docs[PRODUCTOS_CONC[1]] = _cmp_doc(cj, leer(REF_CONC / PRODUCTOS_CONC[1]),
                                       vinc={"/ensamblado_sha256": (sha_archivo(E / "ENSAMBLADO.json") if (E / "ENSAMBLADO.json").is_file() else None, ACEPTADO["ensamblado_json"][1])})
    for n, d in docs.items():
        if not d["iguales_salvo_apartados"]:
            mot.append("DOCUMENTO_DISTINTO: %s %s" % (n, [x["puntero"] for x in (d["discretas"] + d["numericas"])[:4]]))
    if cj.get("producto_sha256") != (sha_archivo(Cc / PRODUCTOS_CONC[0]) if (Cc / PRODUCTOS_CONC[0]).is_file() else None):
        mot.append("HUELLA_DERIVADA_DISTINTA_DE_SUS_BYTES: producto_sha256")
    filas_n = leer_jsonl(Cc / PRODUCTOS_CONC[0]) if (Cc / PRODUCTOS_CONC[0]).is_file() else []
    rn, rr = recuentos_conciliacion(filas_n), recuentos_conciliacion(leer_jsonl(REF_CONC / PRODUCTOS_CONC[0]))
    lb = (_libro("rem152").get("recuentos") or {})
    libro = {"afirmaciones": lb.get("claims"), "canal_phi": dict(sorted(((lb.get("counts") or {}).get("all") or {}).items())),
             "canal_phi_inconclusas": dict(sorted(((lb.get("counts") or {}).get("inconclusive") or {}).items())),
             "canal_phi_robustas": dict(sorted(((lb.get("counts") or {}).get("robust") or {}).items())),
             "cambios_de_signo_certificados": (lb.get("sign_changes") or {}).get("occurrences")}
    deriv["recuentos"] = rn
    deriv["recuentos_iguales_a_la_referencia"] = rn == rr
    deriv["recuentos_iguales_al_libro"] = all(rn.get(k) == v for k, v in libro.items()) and rn["canal_phi"] == {"inconclusa_preservada": 1693,
                                                                                                                   "no_decidida_por_testigos": 28,
                                                                                                                   "parcial_no_robusta_factible": 3,
                                                                                                                   "parcial_no_robusta_infactible": 4}
    deriv["ensamblado"] = {k: (en.get("ensamblado") or {}).get(k) for k in ("filas", "con_techo_incompleto", "por_origen", "fuera_del_lote")}
    if not (deriv["recuentos_iguales_a_la_referencia"] and deriv["recuentos_iguales_al_libro"] and deriv["ensamblado"]["filas"] == 1724
            and deriv["ensamblado"]["con_techo_incompleto"] == 0 and deriv["ensamblado"]["por_origen"] == {"recalculado": 1724, "reutilizado": 0}):
        mot.append("RECUENTOS_DISTINTOS")
    so = {"ensamblado": (F8._ultima(nueva / "ensamblado_stdout.txt"), F8._ultima(REF / "rem151/ensamblado_stdout.txt")),
          "conciliacion": (F8._ultima(nueva / "conciliacion_stdout.txt"), F8._ultima(REF / "rem151/conciliacion_stdout.txt"))}
    deriv["veredictos_iguales"] = {k: bool(a) and a == b for k, (a, b) in so.items()}
    if not all(deriv["veredictos_iguales"].values()):
        mot.append("VEREDICTO_DEL_ENSAMBLADOR_O_DEL_CONCILIADOR_DISTINTO")
    return {"comando": "fam11-comparar", "tarea": ENSAMBLADO, "operacion": "F11-COV26 (ensamblado y conciliación)", "naturaleza": ej.get("naturaleza"),
            "acredita": ej.get("acredita"), "entradas": {t: e.get("procedencia") for t, e in ents.items()}, "regla": "COMPARACION-FAM11-v1 (src/fam11.py)",
            "referencia": {"ensamblado": rel(REF_ENS), "conciliacion": rel(REF_CONC), "productos": ACEPTADO},
            "nueva": rel(nueva), "objetos": objetos, "documentos": docs, "derivados": deriv,
            "bytes_identicos_a_la_referencia": {n: (sha_archivo(E / n) if (E / n).is_file() else None) == h for n, h in ACEPTADO["ensamblado"].items()}
            | {n: (sha_archivo(Cc / n) if (Cc / n).is_file() else None) == h for n, h in ACEPTADO["conciliacion"].items()},
            "estado": {"reproduccion": "aceptada" if not mot else "no_aceptada", "motivos": mot}}


# ================================================================================================ comprobación (sin cálculo científico)
def comprobar() -> dict:
    """fam11-comprobar: SIN CÁLCULO CIENTÍFICO (ningún techo, encierro ni cota; los validadores se aplican a bytes guardados y los
    manifiestos B1/B2 se reconstruyen documentalmente). Con una pieza ausente o alterada no cumple y lo informa (sin rutas)."""
    r = {"comando": "fam11-comprobar", "calculo": "ninguno"}
    _DOCUMENTAL.append("fam11-comprobar")
    malos = fuentes_alteradas()
    fu = fuentes()
    r["fuentes"] = {"archivos": len(fu["archivos"]), "reutilizados": len(fu["reutilizados"]), "saneados": len(fu.get("saneado") or []),
                    "solo_procedencia": len(fu.get("solo_procedencia") or {}),
                    "nucleo_c0_reutilizado": sum(1 for x in piezas() if x["archivo"].startswith("nucleo_s6/c0/")), "ausentes_o_distintos": malos[:20]}
    try:
        return _comprobar(r, malos, fu)
    except Exception as ex:  # noqa: BLE001  (solo con dependencias ausentes o alteradas; si no, el error se propaga)
        if not malos:
            raise
        r["comprobacion_interrumpida"] = {"excepcion": type(ex).__name__, "causa": "pieza ausente o alterada (fuentes.ausentes_o_distintos)"}
        r["cumple"] = False
        return r


def reconstruir_b(u: str) -> dict:
    """Reconstrucción DOCUMENTAL del manifiesto (sin cálculo): B1 con validar_manifiesto (igualdad canónica con la proyección); B2 con el
    bloque b1 de la proyección y la raíz del manifiesto B1 en lugar del B1 nuevo (solo aquí), más validar_cobertura."""
    C = comun(u)
    _fijar_enlace(C, None)
    raw, mp = manifiesto_b(u)
    if u == "B1":
        f = C.validar_manifiesto(mp)
        return {"igual_a_la_proyeccion": f == [], "fallos": [str(x)[:200] for x in f[:4]], "grupos": len(mp["grupos"])}
    _, m1 = manifiesto_b("B1")
    orig = (C.fuente_b1, C._raiz_b1)
    C.fuente_b1 = lambda datos=None: mp["b1"]
    C._raiz_b1 = lambda: {p: [m1["raiz"]["binario"][p]["lo"], m1["raiz"]["binario"][p]["hi"]] for p in C.STRUCT}
    try:
        rec = C.construir_manifiesto()
    finally:
        C.fuente_b1, C._raiz_b1 = orig
    cob = C.validar_cobertura(mp)
    e = C.cobertura_esperada()
    p = C.plan(mp)
    return {"igual_a_la_proyeccion": C.canon(rec) == C.canon(mp), "diferencias": C.diferencias(rec, mp),
            "nota": "bloque b1 tomado de la proyección (documental): en la ejecución lo sustituye el B1 nuevo validado (ENLACE-B1-v1)",
            "cobertura_conforme": cob == [], "fallos_de_cobertura": [str(x)[:200] for x in cob[:4]],
            "recuentos": {"contextos_antes_dedup": sum(e["antes_dedup"].values()), "suma_por_grupo": sum(len(v) for v in p["por_grupo"].values()),
                          "por_grupo": {g: len(v) for g, v in sorted(p["por_grupo"].items())}, "union_efectiva": len(p["union"]), "puentes": len(p["puentes"]),
                          "celdas_Q": len(p["celdas"]), "inclusiones": e["inclusiones"],
                          "2024p_en_el_soporte_E2": sorted({u_["edicion"] for v in mp["entradas_nacionales"].values() for u_ in v["usos"]})}}


def _comprobar(r: dict, malos: list, fu: dict) -> dict:
    raw, man = manifiesto_cov()
    co = man["ABL-COV"]
    sane = _saneado()
    arch = {x["archivo"]: x["sha256"] for x in fu["archivos"] + fu["reutilizados"]}
    cat = {}
    for op in ("F11-COV26", "F11-B1", "F11-B2"):
        o = catalogo_op(op)
        cat.update({d["id"]: d.get("sha256_aceptado") for d in (o.get("datos_configuracion") or []) + (o.get("productos") or []) if "id" in d})
    pin = pines()
    idx_txt = (DATOS / IDX_COV[0]).read_text(encoding="utf-8")
    r["procedencia"] = {
        "codigo_declarado": all(arch.get(n) == h for n, h in CODIGO.items()),
        "codigo_cov_en_su_indice": all(CODIGO[n] in idx_txt for n in CODIGO if n.startswith("nucleo_s6/cov/")) and CODIGO["src/conciliar_cov.py"] in idx_txt,
        "piezas_b_en_su_indice": all(json.loads((BASE / IDX_B[u][0]).read_bytes())["piezas"].get(n) == ORIGINAL_B.get(CODIGO["nucleo_s6/%s/%s" % (u.lower(), n)],
                                                                                                                       CODIGO["nucleo_s6/%s/%s" % (u.lower(), n)])
                                     for u in UNIDADES_B for n in PIEZAS_B[u]),
        "indices": sha_archivo(DATOS / IDX_COV[0]) == IDX_COV[1] and all(sha_archivo(BASE / IDX_B[u][0]) == IDX_B[u][1] for u in UNIDADES_B),
        "proyecciones_con_correspondencia": all(sane.get(a) == (hp, ho) for a, hp, ho in list(MAN_B.values()) + list(IDX_B.values()) + list(COMUN_B.values()) + [MAPA])
                                            and sane.get(CENSO[0], (CENSO[1], CENSO[2])) == (CENSO[1], CENSO[2]),
        "manifiestos_e_indices_iguales_al_catalogo": (cat.get("manifiesto COV"), cat.get("índice del paquete COV"), cat.get("manifiesto B1"), cat.get("índice del paquete B1"),
                                                      cat.get("manifiesto B2"), cat.get("índice del paquete B2"), cat.get("alcance COV"))
                                                     == (MAN_COV[1], IDX_COV[1], MAN_B["B1"][2], IDX_B["B1"][2], MAN_B["B2"][2], IDX_B["B2"][2], ALC_COV[1]),
        "guardadas_iguales_a_sus_pines_y_al_libro": all(sha_archivo(GUARD / t / "resultado.json") == pin[t]["resultado_sha256"] == pin[t]["libro_resultado_sha256"]
                                                        and all(sha_archivo(GUARD / t / "salida" / n) == pin[t]["productos"][n] for n in PRODUCTOS) for t in TAREAS),
        "alcance_de_origen_de_las_tareas": all(leer(GUARD / t / "resultado.json").get("alcance_sha256") == ALC_COV[1] for t in TAREAS)
                                           and sha_archivo(DATOS / ALC_COV[0]) == ALC_COV[1],
        "fuente_de_celdas_declarada_y_autentica": RUTAS_COV.get(co["fuente_celdas"]["ruta"]) == CENSO[0] and co["fuente_celdas"]["sha256"] == CENSO[2]
                                                  and sha_archivo(BASE / CENSO[0]) == CENSO[1],
        "conciliacion_aceptada_como_entrada_de_B1": sha_archivo(DATOS / CONC_FUENTE[0]) == CONC_FUENTE[1] == ACEPTADO["conciliacion"]["CONCILIACION_COV.jsonl"],
        "no_oficiales": all(man.get(k) is False for k in ("b_official_run_authorized", "freeze_run_authorized", "official_export_authorized")),
        "sustituciones_unicas": sustituciones_ok()}
    try:
        h, _ = declaracion()
        r["procedencia"]["declaracion_de_ejecucion_limpia"] = h == arch.get("datos/fam11/" + DECLARACION)
    except Fam11Error:
        r["procedencia"]["declaracion_de_ejecucion_limpia"] = False
    # B1/B2: reconstrucción documental (no carga el cierre C0 ni calcula)
    rb1, rb2 = reconstruir_b("B1"), reconstruir_b("B2")
    rc2 = rb2["recuentos"]
    r["reconstruccion_b"] = {"B1": rb1, "B2": rb2}
    r["reconstruccion_b"]["cumple"] = (rb1["igual_a_la_proyeccion"] and rb2["igual_a_la_proyeccion"] and rb2["cobertura_conforme"]
                                       and (rc2["contextos_antes_dedup"], rc2["suma_por_grupo"], rc2["union_efectiva"], rc2["puentes"], rc2["celdas_Q"])
                                       == (4608, 2304, 1920, 480, 60)
                                       and rc2["por_grupo"] == {"K1": 192, "K2": 192, "K3": 864, "K4": 864, "K5": 96, "K6": 96}
                                       and rc2["inclusiones"] == {"K5": ["K1", "K3"], "K6": ["K2", "K4"]} and "2024p" in rc2["2024p_en_el_soporte_E2"])
    # COV: núcleo, motor, cobertura y revalidación de las guardadas
    M = preparar_cov()
    import paper2b
    r["nucleo"] = {"identidad_recalculada": F5.identidad_c0(), "igual": F5.identidad_c0() == F5.C0_IDENTIDAD,
                   "paper2b_cargado_de": rel(Path(paper2b.__file__).parent), "declarado_en": "fuentes_fam05.json (nucleo_c0)"}
    CX = F5.cargar("conexion_coord_cert", COV / "conexion_coord_cert.py")
    from paper2b import run as RUN
    cfg = RUN.RunConfig()
    model = RUN.provider_for(cfg)
    r["motor"] = {"identidad_de_codigo_igual": CX.identidad_codigo(F5.C0 / "src" / "paper2b") == co["motor"]["codigo"],
                  "configuracion_igual": CX.configuracion(model, cfg.sup) == co["motor"]["configuracion"],
                  "certificado_en_esta_plataforma": getattr(model, "certified", None) is True,
                  "garantia_igual": getattr(model, "garantia", None) == co["motor"].get("garantia", CX.GARANTIA) == CX.GARANTIA}
    cel, fuera, err = M["validar_coord_rec"].celdas_del_lote(BASE, co)
    cel = cel or []
    afs = leer_jsonl(DATOS / ENF_AF[0])
    cb = {"claves": len(co["claves_recalculadas"]), "claves_reutilizadas": len(co.get("claves_reutilizadas") or {}),
          "tareas": {t: len(v) for t, v in co["tareas"].items()}, "celdas_afectadas": len(co["celdas_afectadas"]), "celdas_del_censo": len(cel),
          "error_del_censo": err, "celdas_por_pais": dict(Counter(c["pais"] for c in cel)), "fuera_del_nivel": sorted(fuera or {}),
          "afirmaciones_ENF": len(afs), "enf_por_afirmacion_autentica": sha_archivo(DATOS / ENF_AF[0]) == ENF_AF[1]}
    cb["cumple"] = (cb["claves"] == 26 and cb["claves_reutilizadas"] == 0 and sum(cb["tareas"].values()) == 26 and cb["tareas"].get(T1) == 18
                    and cb["celdas_del_censo"] == cb["celdas_afectadas"] == 1724 and err is None and cb["afirmaciones_ENF"] == 1728
                    and cb["enf_por_afirmacion_autentica"] and len(cb["fuera_del_nivel"]) == 2 and all("2024p" in x for x in cb["fuera_del_nivel"]))
    r["cobertura"] = cb
    rv = {}
    for t in TAREAS:
        rc, ver, _, exc = guion_cov("nucleo_s6/cov/validar_lote.py", [BASE, DATOS / MAN_COV[0], GUARD / t / "resultado.json", GUARD / t / "salida"])
        rv[t] = {"rc": rc, "dictamen": ver.get("dictamen"), "excepcion": exc,
                 "igual_a_la_validacion_historica": ver == json.loads((REF / "rem151" / t / "validacion_stdout.txt").read_text(encoding="utf-8"))}
    techos = [x for t in TAREAS for x in leer_jsonl(GUARD / t / "salida" / PRODUCTOS[0])]
    rv["techos"] = {"total": len(techos), "cerrados_en_escala_normalizada": sum(1 for x in techos if (x.get("cierre_por_escala") or {}).get("normalizada") is True
                                                                                and (x.get("error_normalizado") or 1) <= 1e-7),
                    "error_R_mayor_que_1e-7": sum(1 for x in techos if (x.get("error_R") or 0) > 1e-7),
                    "cierre_solo_normalizado": sum(1 for x in techos if (x.get("cierre_por_escala") or {}).get("R") is False)}
    rv["techos"]["cumple"] = (rv["techos"]["total"] == rv["techos"]["cerrados_en_escala_normalizada"] == 26
                              and rv["techos"]["error_R_mayor_que_1e-7"] == 8 == _libro("rem152").get("techos_cierre_solo_normalizado"))
    r["revalidacion_de_las_guardadas"] = rv
    # referencias (abiertas solo para su huella)
    refb = {u: _ref_b(u) for u in UNIDADES_B}
    rf = {"ensamblado": {n: sha_archivo(REF_ENS / n) == h for n, h in ACEPTADO["ensamblado"].items()}
          | {"ENSAMBLADO.json": sane.get(rel(REF_ENS / "ENSAMBLADO.json")) == ACEPTADO["ensamblado_json"] and sha_archivo(REF_ENS / "ENSAMBLADO.json") == ACEPTADO["ensamblado_json"][0]},
          "conciliacion": {n: sha_archivo(REF_CONC / n) == h for n, h in ACEPTADO["conciliacion"].items()},
          "b1_b2": {"%s:%s" % (u, n): x["declarado"] and x["en_el_libro"] for u in UNIDADES_B for n, x in refb[u].items()},
          "resolucion_doce": sha_archivo(RESOLUCION) == arch.get(rel(RESOLUCION)) and len(leer_jsonl(RESOLUCION)) == 12,
          "en_el_catalogo": all(cat.get(k) == v for k, v in (("L_rem152:ENSAMBLADO.json", ACEPTADO["ensamblado_json"][1]),
                                                               ("L_rem152:cov_techos_ensamblados.jsonl", ACEPTADO["ensamblado"]["cov_techos_ensamblados.jsonl"]),
                                                               ("L_rem152:cov_comparacion_ensamblada.jsonl", ACEPTADO["ensamblado"]["cov_comparacion_ensamblada.jsonl"]),
                                                               ("L_rem152:CONCILIACION_COV.json", ACEPTADO["conciliacion"]["CONCILIACION_COV.json"]),
                                                               ("L_rem152:CONCILIACION_COV.jsonl", ACEPTADO["conciliacion"]["CONCILIACION_COV.jsonl"]),
                                                               ("L_rem167:EVIDENCIA_B1.json", refb["B1"]["EVIDENCIA_B1.json"]["original"]),
                                                               ("L_rem167:VALIDACION_B1.json", refb["B1"]["VALIDACION_B1.json"]["original"]),
                                                               ("L_rem167:LECTURA_B1.json", refb["B1"]["LECTURA_B1.json"]["original"]),
                                                               ("L_rem167:SOLICITUD_INICIO.json", refb["B1"]["SOLICITUD_INICIO.json"]["original"]),
                                                               ("L_rem170:EVIDENCIA_B2.json", refb["B2"]["EVIDENCIA_B2.json"]["original"]),
                                                               ("L_rem170:PLAN_INICIO.json", refb["B2"]["PLAN_INICIO.json"]["original"]),
                                                               ("L_rem170:VALIDACION_B2.json", refb["B2"]["VALIDACION_B2.json"]["original"]),
                                                               ("L_rem170:LECTURA_B2.json", refb["B2"]["LECTURA_B2.json"]["original"]),
                                                               ("X_cov12", sha_archivo(RESOLUCION))))}
    rf["cumple"] = (all(rf["ensamblado"].values()) and all(rf["conciliacion"].values()) and all(rf["b1_b2"].values()) and rf["resolucion_doce"]
                    and rf["en_el_catalogo"])
    r["referencias"] = rf
    # libros (solo extracción)
    lb = fu.get("libros") or {}
    l2, l7, l0 = lb.get("rem152") or {}, lb.get("rem167") or {}, lb.get("rem170") or {}
    conc_ref = recuentos_conciliacion(leer_jsonl(REF_CONC / PRODUCTOS_CONC[0]))
    pares = [("rem152 índice y manifiesto ↔ datos", (l2.get("indice_sha256"), l2.get("manifiesto_sha256")), (IDX_COV[1], MAN_COV[1])),
             ("rem152 resultados de tarea ↔ guardadas", {t: (v or {}).get("resultado_sha256") for t, v in (l2.get("tareas") or {}).items()},
              {t: sha_archivo(GUARD / t / "resultado.json") for t in TAREAS}),
             ("rem152 techos ↔ manifiesto", l2.get("techos"), len(co["claves_recalculadas"])),
             ("rem152 techos con cierre solo normalizado ↔ guardadas", l2.get("techos_cierre_solo_normalizado"), rv["techos"]["error_R_mayor_que_1e-7"]),
             ("rem152 celdas y afirmaciones ↔ manifiesto y ENF", ((l2.get("recuentos") or {}).get("cells"), (l2.get("recuentos") or {}).get("claims")), (1724, len(afs))),
             ("rem152 recuentos ↔ conciliación de referencia", dict(sorted((((l2.get("recuentos") or {}).get("counts") or {}).get("all") or {}).items())), conc_ref["canal_phi"]),
             ("rem152 cambios de signo ↔ conciliación de referencia", ((l2.get("recuentos") or {}).get("sign_changes") or {}).get("occurrences"),
              conc_ref["cambios_de_signo_certificados"]),
             ("rem167 U_C2 ↔ extremo certificado de la referencia", (l7.get("U_C2_hex"), l7.get("U_C2_exacto")),
              (U_C2_HEX, _fs(float.fromhex(U_C2_HEX)))),
             ("rem167 afirmaciones ↔ manifiesto B1", l7.get("afirmaciones"), rb1.get("grupos") and sum(len(g["afirmaciones"]) for g in manifiesto_b("B1")[1]["grupos"])),
             ("rem170 contextos por grupo ↔ reconstrucción B2", {g: (v or {}).get("contexts") for g, v in (l0.get("grupos") or {}).items()}, rc2["por_grupo"]),
             ("rem170 llamadas ↔ plan B2", tuple((l0.get("llamadas") or {}).get(k) for k in ("macro.bridge", "GridCell.Q", "k1_intervalar", "new_C2")),
              (rc2["puentes"], rc2["celdas_Q"], rc2["union_efectiva"], 0)),
             ("rem170 índice y manifiesto ↔ originales", (l0.get("indice_sha256"), l0.get("manifiesto_sha256")), (IDX_B["B2"][2], MAN_B["B2"][2])),
             ("rem170 regla G_hi ↔ veredictos", all((Fraction(v["G_hi_exact"]) <= -EPS) == (v["accepted_transformed_verdict"] == "robust_infeasible")
                                                   for v in (l0.get("grupos") or {}).values()) and len(l0.get("grupos") or {}) == 6, True)]
    r["libros"] = {"presentes": {k: v.get("presente") for k, v in lb.items()}, "solo_extraccion": True,
                   "recuentos": [{"recuento": a, "igual": b == c} for a, b, c in pares], "recuentos_iguales": bool(pares) and all(b == c for _, b, c in pares),
                   "dictamenes_consultados": all((v.get("dictamen") or {}).get("sha256_del_archivo") == (v.get("dictamen") or {}).get("sha256_en_el_libro") is not None
                                                 for v in lb.values() if "dictamen" in v)}
    pil = leer(DATOS / "pilotos.json") if (DATOS / "pilotos.json").is_file() else None
    r["pilotos"] = {"fijados": [p["unidad"] for p in (pil or {}).get("pilotos", [])], "iguales_a_la_regla": pil == regla_pilotos(man),
                    "declarados": any(x["archivo"] == "datos/fam11/pilotos.json" for x in fu["archivos"])}
    r["receta"] = {"pasos": len(receta()["pasos"])}
    r["cumple"] = (not malos and all(r["procedencia"].values()) and r["reconstruccion_b"]["cumple"] and r["nucleo"]["igual"] and all(r["motor"].values())
                   and cb["cumple"] and rf["cumple"] and all(v.get("rc") == 0 and v.get("igual_a_la_validacion_historica") for k, v in rv.items() if k in TAREAS)
                   and rv["techos"]["cumple"] and r["libros"]["recuentos_iguales"] and r["libros"]["dictamenes_consultados"] and all(r["libros"]["presentes"].values())
                   and r["pilotos"]["iguales_a_la_regla"] and r["pilotos"]["declarados"])
    return r


# ================================================================================================ receta completa (sin ejecutarla)
def receta() -> dict:
    raw, man = manifiesto_cov()
    co = man["ABL-COV"]
    d = "salidas/fam11/<ejecucion>"
    pasos = [{"paso": "comprobar", "ordenes": ["reproducir.py fam11-comprobar --salida %s/comprobar.json (sin cálculo científico)" % d]}]
    for t in TAREAS:
        pasos.append({"paso": t, "operacion": "F11-COV26", "claves": co["tareas"][t], "calculo": "nuevo (%d techos)" % len(co["tareas"][t]),
                      "celdas": sum(1 for c in co["celdas_afectadas"] if c["clave_transformada_sha256"] in co["tareas"][t]),
                      "ordenes": ["reproducir.py fam11-unidad --tarea %s --salida %s/%s" % (t, d, t),
                                  "reproducir.py fam11-validar --nueva %s/%s --salida %s/%s.validacion.json" % (d, t, d, t),
                                  "reproducir.py fam11-comparar --tarea %s --nueva %s/%s --validacion %s/%s.validacion.json --salida %s/%s.comparacion.json"
                                  % (t, d, t, d, t, d, t)]})
    ent = " ".join("--entrada %s=%s/%s" % (t, d, t) for t in TAREAS)
    pasos.append({"paso": "ensamblado_y_conciliacion", "operacion": "F11-COV26", "calculo": "regeneración sobre las seis tareas nuevas",
                  "ordenes": ["reproducir.py fam11-ensamblar %s --salida %s/ensamblado" % (ent, d),
                              "reproducir.py fam11-comparar --tarea ENSAMBLADO --nueva %s/ensamblado --salida %s/ensamblado.comparacion.json" % (d, d)]})
    pasos.append({"paso": "B1", "operacion": "F11-B1", "calculo": "nuevo (una solicitud c2_normalizado)",
                  "ordenes": ["reproducir.py fam11-unidad --tarea B1 --salida %s/B1" % d,
                              "reproducir.py fam11-validar --nueva %s/B1 --salida %s/B1.validacion.json" % (d, d),
                              "reproducir.py fam11-comparar --tarea B1 --nueva %s/B1 --validacion %s/B1.validacion.json --salida %s/B1.comparacion.json" % (d, d, d)]})
    pasos.append({"paso": "B2", "operacion": "F11-B2", "calculo": "nuevo (1.920 contextos, 480 puentes, 60 Q) sobre el B1 nuevo validado",
                  "ordenes": ["reproducir.py fam11-unidad --tarea B2 --b1 %s/B1 --validacion-b1 %s/B1.validacion.json --salida %s/B2" % (d, d, d),
                              "reproducir.py fam11-validar --nueva %s/B2 --salida %s/B2.validacion.json" % (d, d),
                              "reproducir.py fam11-comparar --tarea B2 --nueva %s/B2 --validacion %s/B2.validacion.json --salida %s/B2.comparacion.json" % (d, d, d)]})
    return {"comando": "fam11-receta", "estado": "receta completa preparada; NO ejecutada (el cálculo completo pertenece al Paso 3)",
            "manifiestos": {"cov": sha(raw), "b1": MAN_B["B1"][2], "b2": MAN_B["B2"][2]},
            "orden": list(TAREAS) + ["ensamblado_y_conciliacion", "B1", "B2"], "pasos": pasos,
            "cobertura": {"techos": len(co["claves_recalculadas"]), "celdas": len(co["celdas_afectadas"]), "afirmaciones_conciliadas": 1728,
                          "afirmaciones_B": 12, "grupos_B": 6, "fuera_del_nivel": "COL-2024p en COV (pendiente, no NA); sí pertenece al soporte E2 de la cota B2"},
            "ejecucion": {"procesos": "un cálculo a la vez, sin reintentos; COV y B1/B2 en procesos separados (el cierre C0 de B1/B2 rechaza paper2b precargado)",
                          "tope_trabajo_s": F5.TOPE_TRABAJO, "reloj_interno_s": F5.TOPE_TRABAJO - F5.HOLGURA, "limite_externo_B_s": 600.0,
                          "lanzador": "supervisor que termina el árbol de procesos (el mismo de los pilotos), con el límite externo de cada unidad",
                          "parada": ("si una tarea COV no termina completa y validada no se ensambla; si B1 no se valida, B2 no se lanza (ENLACE-B1-v1 lo "
                                     "rechaza); una entrada faltante no se sustituye por su referencia"),
                          "duracion": "sin estimación global: los pilotos no la permiten"},
            "F1": {"reutilizado": ["censo de las 1.724 celdas (K1 y G padre fijos)", "ENF por afirmación (1.728)", "núcleo C0", "fuentes D7, grilla, CA2 y D6",
                                   "manifiestos COV/B1/B2 (la selección no se re-ejecuta)", "conciliación COV aceptada como entrada de B1 (categorías padre)"],
                   "se_genera_de_nuevo": ["26 techos certificados de T1–T6 y sus comparaciones", "ensamblado de 1.724 celdas y conciliación de 1.728 afirmaciones",
                                          "U_C2 de B1 y su lectura", "L_K1 de los seis grupos y G_hi de las doce"],
                   "solo_para_comparar": ["salidas aceptadas rem151 (guardadas)", "productos rem151/rem166/rem169 y resolución rem170 (referencias del catálogo)"],
                   "no_cubre": ["los 16 casos mexicanos", "causalidad u orden de canales", "integración en la síntesis (FAM10)", "Paso 3 y 2.4.2"]},
            "pilotos": leer(DATOS / "pilotos.json") if (DATOS / "pilotos.json").is_file() else None}
