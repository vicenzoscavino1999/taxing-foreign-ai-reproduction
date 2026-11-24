"""FAM08 (ENF: contraste eta_f/2 frente al padre, con phi y las demás entradas del padre conservadas).

Operaciones del catálogo (no se confunden):
- F08-MALLAS (RN): las 29 mallas del manifiesto de mallas ENF (26 de rol ENF y 3 padres a evaluar con C0; 365 filas de puntos) por la
  ruta L1-ELAST del lote 2 (la misma de FAM05/FAM06) con el núcleo C0. Las otras 23 mallas padre se REUTILIZAN de sus productos aceptados
  (no se recalculan). Una malla no acredita un supremo.
- F08-PARES (RD): conciliar_mallas_enf.py (rem126) sobre el producto de mallas: 26 pares padre/ENF y 330 puntos, control del menú d
  (R(τ_d, 0) no depende de eta_f) y diferencias de topología declaradas.
- F08-TECHOS (RN): las seis tareas ABL-ENF-T1…T6 por tarea_lote.py (techos certificados de rama y cota con conexion_coord_cert y el
  núcleo C0) y el tratamiento del caso no alcanzado: T1 terminó incompleta (clave d59edf8a9d1461d1, SUP_ATTAINMENT_UNDECIDED_AT_JUMP_CURVE);
  recuperar_t1.py recupera sus 17 techos cerrados sin convertirla en completa; certificado_salto.py demuestra el supremo lateral NO
  alcanzado de esa clave exacta (sin argmax); el punto factible guardado sigue siendo solo una cota inferior.
- F08-INTEGRAL (RD): ensamblar_integracion.py y conciliar_integracion.py (ruta única validar_integracion.validar_fuentes): 26 claves
  (17 T1 recuperadas + 8 de T2–T6 + 1 resolución), 1.724 celdas, 144 de ellas de la clave resuelta. COL-2024p queda fuera (pendiente, no NA).

Adaptaciones (no cambian fórmulas, claves, tolerancias, presupuestos, garantías ni criterios; cada original se sustituye una sola vez):
- GUION-v1 (de FAM07): cada archivo de nucleo_s6/enf se ejecuta desde sus bytes exactos con las sustituciones de SUSTITUCIONES;
  validar_coord_rec, certificado_salto, recuperar_t1 y validar_integracion se cargan como módulos desde su texto adaptado (MODULOS-v1) y
  las piezas que antes los cargaban de su archivo usan esos módulos.
- NUCLEO-C0-v1 (de FAM05): el núcleo es nucleo_s6/c0; aprobacion_alcance.identidad_instalacion es el módulo mínimo de FAM05.
- RUTAS-FUENTES-v1: toda fuente se lee de su copia en la base (tabla RUTAS_FUENTES, ruta histórica -> archivo) y se sigue autenticando
  por sus bytes; una ruta no declarada falla (sin respaldo).
- SANEADO-v1: el certificado y el censo son PROYECCIONES saneadas (solo procedencia privada sustituida por un marcador; la extracción
  comprobó que restituyen el original). Se autentican por la correspondencia proyección -> original (ORIGINAL) y la huella registrada en
  los productos es la del original.
- PUERTA-v1: las puertas de producción (alcance v3 verificado y decisión humana nativa) no se ejecutan ni se reconstruyen. El sha256 de la
  declaración datos/fam08/ejecucion_limpia.json (NO OFICIAL) ocupa el alcance_sha256 del trabajador y el de la puerta de integración; no
  hay decisión (campo «decision» = null). Diferencias visibles, nunca valores.
- PAQUETE-v1: la integración autentica las cinco piezas copiadas contra su índice (datos/fam08/PAQUETE_INTEGRACION_ENF.json, 43b24726…);
  las otras tres (emisión de alcance, admisión, guion de receta) pertenecen a la autorización histórica y no se copian.
- ENTRADAS-v1 / ENTRADAS-MALLAS-v1: cada tarea y las mallas entran desde una carpeta declarada: «guardado» (bytes aceptados en
  datos/fam08/guardadas, con los pines del manifiesto integral) o una salida nueva de fam08 (sus pines pasan a ser las huellas de SUS bytes:
  vínculo declarado). Una entrada no declarada no se sustituye por la referencia: la validación falla. «Mixta»: filas de mallas piloto
  nuevas y validadas en lugar de las guardadas de esas mallas.
- VALIDADOR-ELAST-v1: el validador ELAST del lote 2 (VALIDADOR-v2 de FAM05) se ejecuta en el mismo proceso en lugar de un subproceso
  (mismos argumentos y criterio); su ruta se registra relativa (ubicación).
- RUTA-VISIBLE-v1: el certificador registra la ruta de su fuente relativa a la raíz (el original escribía la absoluta).
- RELOJ-PILOTO-v1 (de FAM05): reloj interno = 2400 − 120 = 2280 s (el tope_efectivo_s histórico); el límite externo lo pone el supervisor.
"""
from __future__ import annotations

import builtins
import contextlib
import importlib.util
import io
import json
import re
import sys
import time
import traceback
import types
from collections import Counter
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
sha, sha_archivo, leer, leer_jsonl, rel, F1 = F5.sha, F5.sha_archivo, F5.leer, F5.leer_jsonl, F5.rel, F5.F1
ENF = BASE / "nucleo_s6" / "enf"
DATOS = BASE / "datos" / "fam08"
GUARD = DATOS / "guardadas"
REF = BASE / "referencias" / "fam08"
CODIGO = {"mallas/conciliar_mallas_enf.py": "82d1a20beb01dd239bbe08f49174912c4810f209ea439fd1e1ee40c5e841fda7",
          "techos/tarea_lote.py": "1fbe5cbc0525428788ac775f1a2e8c5e55b03079cb37a195b5ad997ed7bc0b40",
          "techos/conexion_coord_cert.py": "e5776de970b72535ec7b72340604abfd9e8448479ea78dac4b714d870d273d61",
          "techos/validar_lote.py": "070ae81d15119735369b08bf083e9ff3b7652ca99a2956547b9f290db4022ee4",
          "techos/validar_coord_rec.py": "086ea05688d9eb520982cc3e57a01eb5b45b37f3bb9b77503f3c0a2822ed0864",
          "integracion/validar_integracion.py": "107435df1c35fab654a665a256997dc0d52b22b6138c05d6667ead7398ddd494",
          "integracion/recuperar_t1.py": "1a5108b2ed4ff78d5da200b50ccb733f35fdef30626928f14817cfe9af6e15b2",
          "integracion/certificado_salto.py": "a9b4e6ad712845e2452e40c727d31818927c2f5fe5a42c0feb9ade278ab43837",
          "integracion/ensamblar_integracion.py": "7f04fafe4110bc22407c0016799b81832a78baa0aa736f60cea80b20e4a95522",
          "integracion/conciliar_integracion.py": "e97edc15bb4e458e5c4cb2f9aa38d2c5fe55fb3d07c2259ea9cb4d0f6cdc221a",
          "integracion/pruebas_certificado.py": "194ec1c74c89f4754d2d25919f0f531c2428ae32307e68d474a8a2c998ffc9bc"}
INDICE_DE = {"integracion/": "PAQUETE_INTEGRACION_ENF.json", "techos/": "PAQUETE_ABL_ENF.json", "mallas/": "PAQUETE_MALLAS_ENF.json"}
MAN_MALLAS = ("MANIFIESTO_MALLAS_ENF.json", "8ae8f1ca1d23bcb6fb5e9ac3eff3cbc7b2495f9fb2d40b22f583157ecd67e224")
COB_MALLAS = ("COBERTURA_MALLAS_ENF.json", "a39438a13a2b4f479f60e73eb3ac4b1ae45e1482d9d00be8c18e8817132c899c")
MAN_ENF = ("MANIFIESTO_ABL_ENF.json", "0b27b32abdfb4eaf0db11427a8a8bb93c7d4014c6c7acd1bdbfbe6e32d28b3ad")
COB_ENF = ("COBERTURA_ABL_ENF.json", "b7b2616c4f89f15d5469ad460e71697af910a6a0c2a2a60390b6a0fe367772d9")
MI_ENF = ("MANIFIESTO_INTEGRACION_ENF.json", "b752249a446ce4f16a4c4d80e6608811787b9b99d0c6fd6aef6480a6ace10b85")
INDICES = {"PAQUETE_INTEGRACION_ENF.json": "43b24726f76ead77717c642176fc0e2880e60db0e4ac1b44a30d803a5e0f1673",
           "PAQUETE_ABL_ENF.json": "039c85beb88e5912867ef8ebadcf47995cc8f9a99a5fd92e20bc072a7abda57c",
           "PAQUETE_MALLAS_ENF.json": "c0bfe525f58825d7926b6ef9208ab77407170a0edaf9e0fb7aa43aac0d19b0ad"}
PAQUETE_LOTE1 = ("datos/fam05/PAQUETE_LOTE1.json", "265c29f43ac4ad9c16dfe70da7c830cd027e0bab6bd9dffa561536b114981f32")
ALC_ENF = ("alcance_abl_enf.json", "5c64a6da4d9182f03e1739cf3ff006b14b23787db5b1076cf349df66f1be58cc")
ALC_MALLAS = ("alcance_mallas_enf.json", "432e705246e5d19b5c58fb34414333caf9020358e60a833a5582357021147bf8")
CERT = ("CERTIFICADO_d59edf8a_I2.json", "9e2ac47289e8c239c8352a70819babb285e28c03f3c3cfd906230950a9039f72",
        "cc1aa49abf64585dd500838d1120d02c938a571f4be6fe159e3ab42fc697daaa")
CENSO = ("CENSO_REMANENTE.json", "f9940081b3fca85a6641443a340bbb73b7be5119b83434d87d9aca98876dab08",
         "78e51627014c11778b5388ee9aaa07074b3a33fbade09b226bd49933aa5d3129")
ORIGINAL = {CERT[1]: CERT[2], CENSO[1]: CENSO[2]}              # SANEADO-v1: proyección -> original (comprobado en la extracción)
DECLARACION = "ejecucion_limpia.json"
DECLARACION_KIND = "declaracion-ejecucion-limpia-fam08"
ETIQUETA = "REPRODUCCION LIMPIA FAM08 NO OFICIAL"
ELAST = "L1-ELAST"
T1 = "ABL-ENF-T1"
TAREAS = tuple("ABL-ENF-T%d" % i for i in range(1, 7))
PARES, INTEGRAL, RECUPERACION = "PARES", "INTEGRAL", "RECUPERACION"
CLAVE_NA = "d59edf8a9d1461d1"
MOTIVO_NA = "SUP_ATTAINMENT_UNDECIDED_AT_JUMP_CURVE"
PRODUCTOS = ("enf_techos.jsonl", "enf_comparacion.jsonl")
PRODUCTOS_ENS = ("enf_techos_integrados.jsonl", "enf_comparacion_ensamblada.jsonl", "enf_brechas_resueltas.jsonl", "enf_comparacion_integral.jsonl")
PRODUCTOS_CONC = ("techos_pares.jsonl", "brechas_celdas.jsonl")
GUARDADO = "guardado"
REGENERACION = "regeneración sobre entradas guardadas"
MIXTA = "procedencia mixta (salidas nuevas y entradas guardadas)"
NUEVA = "sobre salidas nuevas"
OPERACIONES = {"F08-MALLAS": "29 mallas (26 ENF + 3 padres a evaluar con C0; 365 filas de puntos); 23 mallas padre reutilizadas",
               "F08-PARES": "26 pares padre/ENF y 330 puntos (conciliar_mallas_enf.py)",
               "F08-TECHOS": "ABL-ENF-T1…T6 (26 techos certificados) y el caso no alcanzado d59edf8a9d1461d1 (recuperación de T1 y certificado)",
               "F08-INTEGRAL": "26 claves y 1.724 celdas (ensamblado y conciliación integrales)"}
MALLAS_GUARDADA = GUARD / "mallas_rem127" / ELAST
REF_PARES = REF / "rem128" / "conciliacion_mallas"
REF_ENS = REF / "rem131" / "ensamblado"
REF_CONC = REF / "rem131" / "conciliacion"
REF_DIAG = REF / "rem128" / "diagnostico"
ACEPTADO = {   # referencias (catálogo; los tres documentos .json son las proyecciones del catálogo)
    "pares": {"pares_puntos.jsonl": "11a9d2d73574243e4665afdaef5b8f61fcfae7022ac08df5325b5b4c473f8aa9",
              "CONCILIACION_MALLAS_ENF.json": "c3e9cf5a78698a552b22cd22fec431c19fd5c9b1a6477b6a02ddac9f89ea3f2d"},
    "ensamblado": {"enf_techos_integrados.jsonl": "31ee1d746870391f227c11df28035b2299ed33a7493f978be9cb111607baac28",
                   "enf_comparacion_ensamblada.jsonl": "504f0b28b4d60c29421f0b4cc893d24af4fdbb3c67b9390b7070636c2a1a58cc",
                   "enf_brechas_resueltas.jsonl": "b987ec77948c5ad5c3859305a1b9ea688f8a56cd07c497b78fa8c6f3eb4148ab",
                   "enf_comparacion_integral.jsonl": "0220543dce3b4187b557d0ca6175513b88037408146a8d7f6968b29e585fed1b",
                   "ENSAMBLADO_INTEGRAL.json": "f4ddf8c398420641b1978e22fed956671da24dcee7b77d1c07460c6f335a9959"},
    "conciliacion": {"techos_pares.jsonl": "3d8aa516c64f7c24d6e6dbe4ea0301c64c37ddf0950e952a840def684e356d1f",
                     "brechas_celdas.jsonl": "0220543dce3b4187b557d0ca6175513b88037408146a8d7f6968b29e585fed1b",
                     "CONCILIACION_INTEGRAL_ENF.json": "18a2cfdb65b5484333999e2456893232a7949f5f7fa8f3c8bc17301f31d7cd68"},
    "pruebas": {"PRUEBAS_CERTIFICADO_REM128.json": "dae673535ccab961a4cf70d8664c72cefa8cd1e286f52e03ae2aa52b99fc7607"}}
RUTAS_FUENTES = {
    "tmp/paso4_enforcement_desde_rem125/lote_enf/PAQUETE_ABL_ENF.json": "datos/fam08/PAQUETE_ABL_ENF.json",
    "tmp/paso4_enforcement_desde_rem125/lote_enf/MANIFIESTO_ABL_ENF.json": "datos/fam08/MANIFIESTO_ABL_ENF.json",
    "tmp/paso4_enforcement_desde_rem125/lote_enf/COBERTURA_ABL_ENF.json": "datos/fam08/COBERTURA_ABL_ENF.json",
    "tmp/paso4_enf_continuacion_salto_desde_rem128/diagnostico/CERTIFICADO_d59edf8a_I2.json": "datos/fam08/CERTIFICADO_d59edf8a_I2.json",
    "tmp/paso4_mallas_enforcement_desde_rem126/mallas_enf/MANIFIESTO_MALLAS_ENF.json": "datos/fam08/MANIFIESTO_MALLAS_ENF.json",
    "tmp/paso4_mallas_enforcement_desde_rem126/mallas_enf/COBERTURA_MALLAS_ENF.json": "datos/fam08/COBERTURA_MALLAS_ENF.json",
    "tmp/paso4_remanente_lotes_desde_rem113/censo/CENSO_REMANENTE.json": "datos/fam08/CENSO_REMANENTE.json",
    "tmp/paso4_conciliacion_portabilidad_desde_rem111/lote/LOTE1_MANIFIESTO.json": "datos/fam04/LOTE1_MANIFIESTO.json",
    "tmp/paso4_suplemento_topologia_desde_rem119/lote2/LOTE2_MANIFIESTO.json": "datos/fam05/LOTE2_MANIFIESTO.json",
    "tmp/paso4_suplemento_topologia_desde_rem119/lote2/LOTE2E4_MANIFIESTO.json": "datos/fam06/LOTE2E4_MANIFIESTO.json",
    "tmp/paso4_lote1_desde_rem112/lote1_LOTE1_REM112/L1-ELAST/salida/frontier_result.jsonl": "referencias/fam04/rem112/L1-ELAST/salida/frontier_result.jsonl",
    "tmp/paso4_lote2_e4_desde_rem120/lote2_REM120_LOTE2/L1-ELAST/salida/frontier_result.jsonl": "referencias/fam05/rem120/L1-ELAST/salida/frontier_result.jsonl",
    "tmp/paso4_lote2_e4_desde_rem120/lote2_REM120_LOTE2/L1-ELAST/salida/suplemento_procedencia.jsonl":
        "referencias/fam05/rem120/L1-ELAST/salida/suplemento_procedencia.jsonl",
    "tmp/paso4_e4_coord_desde_rem121/lote2e4_REM121_E4/L1-ELAST/salida/frontier_result.jsonl": "referencias/fam06/rem121/L1-ELAST/salida/frontier_result.jsonl"}
ADAPTACIONES = ("GUION-v1", "MODULOS-v1", "NUCLEO-C0-v1", "RUTAS-FUENTES-v1", "SANEADO-v1", "PUERTA-v1", "PAQUETE-v1", "ENTRADAS-v1",
                "ENTRADAS-MALLAS-v1", "VALIDADOR-ELAST-v1", "RUTA-VISIBLE-v1", "RELOJ-PILOTO-v1")
_C0_HIST = '"paso4_raices_impacto_desde_rem116/candidato_c0/instalacion"'
_TABLAS = ("RUTAS_FUENTES = %s    # FAM08 RUTAS-FUENTES-v1: ruta histórica -> archivo de la base limpia\n"
           "ORIGINAL = %s    # FAM08 SANEADO-v1: sha256 de la proyección saneada -> sha256 de su original (correspondencia comprobada)\n"
           % (json.dumps(RUTAS_FUENTES, ensure_ascii=False), json.dumps(ORIGINAL)))
_CONC = (   # conciliadores de mallas (rem126 y su copia rem129): mismo texto en ambos
    ("RUTAS-FUENTES-v1 (lectura)", '    p = R / ref["ruta"]\n',
     '    if ref["ruta"] not in RUTAS_FUENTES:                  # FAM08 RUTAS-FUENTES-v1: solo fuentes declaradas\n'
     '        return None, "FUENTE_NO_DECLARADA_EN_LA_BASE_LIMPIA:" + ref["ruta"]\n'
     '    p = R / RUTAS_FUENTES[ref["ruta"]]\n'),
    ("ENTRADAS-MALLAS-v1 (carpeta)", 'd_m = LM / "L1-ELAST"\n',
     'd_m = Path(ENTRADAS["mallas_dir"])                   # FAM08 ENTRADAS-MALLAS-v1: carpeta declarada (guardada o nueva)\n'),
    ("VALIDADOR-ELAST-v1", 'p = subprocess.run([sys.executable, "-B", "-I", "-X", "utf8", str(L119 / "validar_lote.py"), str(R), str(MAN), '
                           'str(d_m / "resultado.json"), str(d_m / "salida"), str(COB)],\n'
                           '                   capture_output=True, text=True, encoding="utf-8", errors="replace")\n',
     'p = VALIDADOR_ELAST(MAN, d_m / "resultado.json", d_m / "salida", COB)   # FAM08 VALIDADOR-ELAST-v1: el mismo validador, en proceso\n'),
    ("ENTRADAS-MALLAS-v1 (filas)", 'filas_m = [json.loads(x) for x in pb.decode("utf-8").splitlines() if x.strip()]\n',
     'filas_m = [json.loads(x) for x in pb.decode("utf-8").splitlines() if x.strip()]\n'
     'filas_m = ENTRADAS["filas_mallas"](filas_m)          # FAM08 ENTRADAS-MALLAS-v1: filas de mallas piloto nuevas y validadas (mixta) o identidad\n'),
    ("VALIDADOR-ELAST-v1 (ruta)", '"validador_elast": {"ruta": str(L119 / "validar_lote.py"),', '"validador_elast": {"ruta": "nucleo_s6/lote2/validar_lote.py",'))
SUSTITUCIONES = {
    "techos/tarea_lote.py": (
        ("PUERTA-v1", F7.SUSTITUCIONES["tarea_lote.py"][1][1],
         'if modo == "produccion":                    # FAM08 PUERTA-v1: sin puerta de producción (ni alcance v3 ni decisión humana)\n'
         '    if "--declaracion" not in o:\n'
         '        fin("rechazada", "PRODUCCION_SIN_DECLARACION_DE_EJECUCION_LIMPIA")\n'
         '    out["alcance_sha256"] = H(Path(o["--declaracion"]).read_bytes())    # sha256 de datos/fam08/ejecucion_limpia.json (NO OFICIAL)\n'),),
    "techos/validar_coord_rec.py": (
        ("NUCLEO-C0-v1", "NUCLEO = Path(__file__).resolve().parents[2] / " + _C0_HIST, 'NUCLEO = Path(__file__).resolve().parents[2] / "c0"'),
        ("RUTAS-FUENTES-v1 (tabla)", 'SIN_CALCULO = ("PROVEEDOR_NO_CERTIFICADO", "CONFIGURACION_DISTINTA_DE_LA_DECLARADA", "DETENIDO_POR_TOPE")\n',
         'SIN_CALCULO = ("PROVEEDOR_NO_CERTIFICADO", "CONFIGURACION_DISTINTA_DE_LA_DECLARADA", "DETENIDO_POR_TOPE")\n' + _TABLAS),
        ("RUTAS-FUENTES-v1 (lectura)", '    p = Path(R) / ref["ruta"]\n',
         '    if ref["ruta"] not in RUTAS_FUENTES:                              # FAM08 RUTAS-FUENTES-v1: solo fuentes declaradas\n'
         '        return None, "FUENTE_NO_DECLARADA_EN_LA_BASE_LIMPIA:%s" % ref["ruta"]\n'
         '    p = Path(R) / RUTAS_FUENTES[ref["ruta"]]\n'),
        ("SANEADO-v1", '    if hashlib.sha256(b).hexdigest() != ref["sha256"]:\n',
         '    if ORIGINAL.get(hashlib.sha256(b).hexdigest(), hashlib.sha256(b).hexdigest()) != ref["sha256"]:   # FAM08 SANEADO-v1\n')),
    "techos/validar_lote.py": (
        ("NUCLEO-C0-v1", "NUCLEO = AQUI.parents[1] / " + _C0_HIST, 'NUCLEO = AQUI.parents[1] / "c0"'),),
    "integracion/certificado_salto.py": (
        ("NUCLEO-C0-v1", "C0 = AQUI.parents[2] / " + _C0_HIST, 'C0 = AQUI.parents[2] / "c0"'),
        ("RUTA-VISIBLE-v1 (función)", 'CODIGO_C0 = ("model.py", "encierros_modelo.py", "elementales.py", "intervalos.py")\n',
         'CODIGO_C0 = ("model.py", "encierros_modelo.py", "elementales.py", "intervalos.py")\n\n\n'
         'def _ruta_visible(R, p):                     # FAM08 RUTA-VISIBLE-v1: relativa a la raíz (el original escribía la absoluta)\n'
         '    p, R = Path(p).resolve(), Path(R).resolve()\n'
         '    return p.relative_to(R).as_posix() if p.is_relative_to(R) else p.name\n'),
        ("RUTA-VISIBLE-v1 (uso)", '"fuente_techo": {"ruta": str(Path(techos_p)),', '"fuente_techo": {"ruta": _ruta_visible(R, techos_p),')),
    "integracion/recuperar_t1.py": (
        ("MODULOS-v1 (validador)", '    VC = _cargar("validar_coord_rec_recuperacion", LENF / "validar_coord_rec.py")\n',
         '    VC = sys.modules["validar_coord_rec"]          # FAM08 MODULOS-v1: validar_coord_rec adaptado (src/fam08.py)\n'),
        ("MODULOS-v1 (certificador)", '            CS = cert_mod or _cargar("certificado_salto_recuperacion", AQUI.parent / "certificado_salto.py")\n',
         '            CS = cert_mod or sys.modules["certificado_salto"]   # FAM08 MODULOS-v1\n')),
    "integracion/validar_integracion.py": (
        ("CONSTANTES-FAM08", 'LIMITES = {"procesos": 3, "tope_s": 2400.0, "suite_s": 3600.0, "union_s": 10800.0}\n',
         'LIMITES = {"procesos": 3, "tope_s": 2400.0, "suite_s": 3600.0, "union_s": 10800.0}\n'
         'NUCLEO_C0 = AQUI.parents[1] / "c0"                                       # FAM08 NUCLEO-C0-v1\n'
         'INDICE = AQUI.parents[2] / "datos/fam08/PAQUETE_INTEGRACION_ENF.json"     # FAM08 PAQUETE-v1: índice en los datos de la base limpia\n'
         'PIEZAS_COPIADAS = ("validar_integracion.py", "recuperar_t1.py", "certificado_salto.py", "ensamblar_integracion.py", "conciliar_integracion.py")\n'
         'DECLARACION_KIND = "%s"   # FAM08 PUERTA-v1\n' % DECLARACION_KIND + _TABLAS +
         'ENTRADAS = {"dirs": {}, "pins": {}}   # FAM08 ENTRADAS-v1: la fija src/fam08.py antes de cada ejecución\n'),
        ("PAQUETE-v1 (índice)", '    p = AQUI / "PAQUETE_INTEGRACION_ENF.json"\n', '    p = INDICE\n'),
        ("PAQUETE-v1 (piezas)", '    mal = [n for n in PIEZAS if n not in idx.get("piezas", {})', '    mal = [n for n in PIEZAS_COPIADAS if n not in idx.get("piezas", {})'),
        ("NUCLEO-C0-v1", '    C0 = R / mi["nucleo"]["ruta"]\n', '    C0 = NUCLEO_C0\n'),
        ("PUERTA-v1", ('    if not alcance or not decision:\n',
                       '    return True, {"modo": modo, "indice_sha256": idx_sha, "alcance_sha256": H(ab), "decision": dec}\n'),
         '    if not alcance or decision:              # FAM08 PUERTA-v1: sin puerta de producción (ni alcance v3 de integración ni decisión humana)\n'
         '        return False, {"motivo": "PRODUCCION_SIN_DECLARACION_DE_EJECUCION_LIMPIA"}\n'
         '    ab = Path(alcance).read_bytes() if Path(alcance).is_file() else b"{}"\n'
         '    if json.loads(ab).get("kind") != DECLARACION_KIND:\n'
         '        return False, {"motivo": "DECLARACION_DE_EJECUCION_LIMPIA_DISTINTA"}\n'
         '    return True, {"modo": modo, "indice_sha256": idx_sha, "alcance_sha256": H(ab), "decision": None}\n'),
        ("RUTAS-FUENTES-v1 (índice histórico)", '    ip = R / ph["indice"]["ruta"]\n', '    ip = R / RUTAS_FUENTES[ph["indice"]["ruta"]]\n'),
        ("MODULOS-v1 (lote_enf)", '    LENF = ip.parent\n', '    LENF = AQUI.parent / "techos"                     # FAM08 MODULOS-v1: piezas históricas de lote_enf\n'),
        ("MODULOS-v1 (carga)", '    VC = _cargar("validar_coord_rec_historico_integracion", LENF / "validar_coord_rec.py")\n'
                               '    RT = _cargar("recuperar_t1_integracion", AQUI / "recuperar_t1.py")\n'
                               '    CS = _cargar("certificado_salto_integracion", AQUI / "certificado_salto.py")\n',
         '    VC, RT, CS = sys.modules["validar_coord_rec"], sys.modules["recuperar_t1"], sys.modules["certificado_salto"]   # FAM08 MODULOS-v1\n'),
        ("RUTAS-FUENTES-v1 (manifiesto)", '    mp = R / ph["manifiesto"]["ruta"]\n', '    mp = R / RUTAS_FUENTES[ph["manifiesto"]["ruta"]]\n'),
        ("ENTRADAS-v1 (tareas)", '        d = R / e["directorio"]\n',
         '        e = dict(e, **ENTRADAS["pins"].get(t, {}))       # FAM08 ENTRADAS-v1: pines de una tarea nueva = huellas de SUS bytes\n'
         '        d = R / ENTRADAS["dirs"].get(t, "<tarea sin carpeta declarada>")   # FAM08 ENTRADAS-v1: sin carpeta, la tarea falla\n'),
        ("ENTRADAS-v1 (T1)", '    t1 = mi["t1"]\n', '    t1 = dict(mi["t1"], **ENTRADAS["pins"].get(mi["t1"]["tarea"], {}))   # FAM08 ENTRADAS-v1\n'),
        ("ENTRADAS-v1 (T1, carpeta)", 'R / t1["directorio"]', 'R / ENTRADAS["dirs"].get(t1["tarea"], "<T1 sin carpeta declarada>")'),
        ("ENTRADAS-v1 (resolución)", '    rm = mi.get("resolucion") or {}\n',
         '    rm = dict(mi.get("resolucion") or {}, **ENTRADAS.get("resolucion", {}))   # FAM08 ENTRADAS-v1: certificado reemitido (receta)\n'),
        ("RUTAS-FUENTES-v1 (certificado)", '        cp = R / rm["certificado"]["ruta"]\n',
         '        cp = R / RUTAS_FUENTES.get(rm["certificado"]["ruta"], rm["certificado"]["ruta"])   # FAM08 RUTAS-FUENTES-v1\n'),
        ("SANEADO-v1 (certificado)", '        if H(cb) != rm["certificado"]["sha256"]:\n',
         '        if ORIGINAL.get(H(cb), H(cb)) != rm["certificado"]["sha256"]:   # FAM08 SANEADO-v1\n'),
        ("SANEADO-v1 (huella registrada)", '"sha256": H(cb), "recalculado_identico": True}', '"sha256": ORIGINAL.get(H(cb), H(cb)), "recalculado_identico": True}')),
    "integracion/conciliar_integracion.py": _CONC + (
        ("RUTAS-FUENTES-v1 (mallas)", 'MAN, COB, LM = (R / MI["mallas"]["manifiesto"]["ruta"]), (R / MI["mallas"]["cobertura"]["ruta"]), (R / MI["mallas"]["lanzamiento"])\n',
         'MAN, COB, LM = (R / RUTAS_FUENTES[MI["mallas"]["manifiesto"]["ruta"]]), (R / RUTAS_FUENTES[MI["mallas"]["cobertura"]["ruta"]]), None   # FAM08\n'),
        ("ENTRADAS-MALLAS-v1 (pines)", 'if H(pb) != MI["mallas"]["producto_sha256"] or H(rb) != MI["mallas"]["resultado_sha256"]:\n',
         'if H(pb) != ENTRADAS["mallas_pins"]["producto_sha256"] or H(rb) != ENTRADAS["mallas_pins"]["resultado_sha256"]:   # FAM08 ENTRADAS-MALLAS-v1\n'),
        ("RUTAS-FUENTES-v1 (techos)", '        raw_t = (R / ph["ruta"]).read_bytes()\n', '        raw_t = (R / RUTAS_FUENTES[ph["ruta"]]).read_bytes()   # FAM08 RUTAS-FUENTES-v1\n')),
    "mallas/conciliar_mallas_enf.py": _CONC,
    "integracion/pruebas_certificado.py": (
        ("MODULOS-v1", 'sp = importlib.util.spec_from_file_location("certificado_salto", AQUI.parent / "certificado_salto.py")\n'
                       'CS = importlib.util.module_from_spec(sp)\nsp.loader.exec_module(CS)\n',
         'CS = sys.modules["certificado_salto"]       # FAM08 MODULOS-v1: certificador adaptado (NUCLEO-C0-v1)\n'),
        ("RUTAS-FUENTES-v1", 'man_p = R / "tmp/paso4_enforcement_desde_rem125/lote_enf/MANIFIESTO_ABL_ENF.json"\n',
         'man_p = R / RUTAS_FUENTES["tmp/paso4_enforcement_desde_rem125/lote_enf/MANIFIESTO_ABL_ENF.json"]   # FAM08 RUTAS-FUENTES-v1\n'))}
MODULOS = {"validar_coord_rec": "techos/validar_coord_rec.py", "certificado_salto": "integracion/certificado_salto.py",
           "recuperar_t1": "integracion/recuperar_t1.py", "validar_integracion": "integracion/validar_integracion.py"}


class Fam08Error(RuntimeError):
    pass


def need(t, codigo):
    if not t:
        raise Fam08Error(codigo)


def fuentes() -> dict:
    return leer(BASE / "fuentes_fam08.json")


def piezas() -> list:
    fu = fuentes()
    c0 = [dict(x, papel="núcleo C0 (reutilizado de FAM05)") for x in F5.fuentes()["archivos"] if x["archivo"].startswith("nucleo_s6/c0/")]
    return fu["archivos"] + fu["reutilizados"] + c0


def _uso(a: str, uso: str, guardadas=None) -> bool:
    if uso == "todo":
        return True
    if uso == "calculo":                    # el cálculo y la validación no abren salidas aceptadas ni referencias (ni para su huella)
        return not a.startswith(("datos/fam08/guardadas/", "referencias/"))
    if a.startswith("datos/fam08/guardadas/") and guardadas is not None:   # regeneración: solo las guardadas declaradas como entrada
        return any(a.startswith(g.rstrip("/") + "/") for g in guardadas)
    return not a.startswith("referencias/fam08/")      # regeneración: las guardadas son sus entradas; las referencias, nunca


def fuentes_alteradas(uso: str = "todo", guardadas=None) -> list:
    """Piezas ausentes o con otra huella. «calculo»: código, núcleo y entradas (sin las salidas aceptadas guardadas ni las referencias,
    para que el rastro del cálculo no las registre abiertas); «regeneracion»: además las mallas padre reutilizadas y las guardadas
    declaradas como entrada (`guardadas`: sus carpetas relativas; una tarea nueva no abre la guardada de su tarea), nunca las referencias
    de FAM08; «todo»: todo (fam08-comprobar)."""
    return [x["archivo"] for x in piezas() if _uso(x["archivo"], uso, guardadas) and sha_archivo(BASE / x["archivo"]) != x["sha256"]]


def _manifiesto(par: tuple) -> tuple:
    raw = (DATOS / par[0]).read_bytes()
    need(sha(raw) == par[1], "MANIFIESTO_DISTINTO: %s" % par[0])
    man = json.loads(raw)
    need(not str(man.get("kind", "")).endswith(("-SINTETICO", "-ENSAYO")), "MANIFIESTO_SINTETICO_O_DE_ENSAYO: %s" % par[0])
    return raw, man


def manifiesto_mallas() -> tuple:
    return _manifiesto(MAN_MALLAS)


def manifiesto_enf() -> tuple:
    return _manifiesto(MAN_ENF)


def mi() -> dict:
    return _manifiesto(MI_ENF)[1]


def guardada(t: str) -> Path:
    return GUARD / ("techos_rem127" if t == T1 else "techos_rem128") / t


def pines() -> dict:
    m = mi()
    return {e["tarea"]: e for e in [m["t1"]] + m["tareas_completas"]}


def catalogo_op(op: str) -> dict:
    return next(o for o in leer(BASE / "catalogo.json")["operaciones"] if o["clave"] == op)


# ================================================================================================ guiones y módulos adaptados
def adaptado(n: str) -> str:
    """GUION-v1: bytes exactos de nucleo_s6/enf/<n> con sus sustituciones (cada original, una sola vez; un bloque se fija por su primera y
    su última línea, ambas únicas)."""
    src = (ENF / n).read_bytes()
    need(sha(src) == CODIGO[n], "CODIGO_ENF_DISTINTO: %s" % n)
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
            adaptado(n)
        return True
    except Fam08Error:
        return False


def modulo(nombre: str, n: str):
    txt = adaptado(n)
    h = sha(txt.encode("utf-8"))
    m = sys.modules.get(nombre)
    if m is None or getattr(m, "FAM08_ADAPTADO_SHA256", None) != h:
        m = types.ModuleType(nombre)
        m.__file__ = str(ENF / n)
        sys.modules[nombre] = m
        ruta = list(sys.path)
        try:
            exec(compile(txt, str(ENF / n), "exec"), m.__dict__)
        finally:
            sys.path[:] = ruta
        m.FAM08_ADAPTADO_SHA256 = h
    return m


def preparar() -> dict:
    """Núcleo C0 delante y módulo de identidad (FAM05); los cuatro módulos ENF desde su texto adaptado (MODULOS-v1)."""
    F5.preparar()
    M = {k: modulo(k, n) for k, n in MODULOS.items()}
    cx = sys.modules.get("conexion_coord_cert")
    if cx is not None:
        need(Path(cx.__file__).resolve() == (ENF / "techos/conexion_coord_cert.py").resolve(), "CONEXION_COORD_DE_OTRO_PAQUETE")
    return M


def _sin_base(t):
    return None if t is None else t.replace(str(BASE), "<base>")


def guion(n: str, args: list, extra: dict | None = None) -> tuple:
    """Ejecuta el guion adaptado como __main__ con sys.argv = [nucleo_s6/enf/<n>, *args]; devuelve (rc, última línea JSON, stdout, excepción)."""
    M = preparar()
    txt = adaptado(n)
    p = ENF / n
    g = dict(extra or {}, __name__="__main__", __file__=str(p), __builtins__=builtins)
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
    need(all(sys.modules.get(k) is m for k, m in M.items()), "MODULO_ENF_SUSTITUIDO_DURANTE_EL_GUION")
    lineas = [x for x in buf.getvalue().splitlines() if x.strip()]
    try:
        ult = json.loads(lineas[-1]) if lineas else {}
    except ValueError:
        ult = {}
    return rc, ult, buf.getvalue(), exc


def validador_elast(man_p, res, sal, cob, sel=None):
    """VALIDADOR-ELAST-v1: validar_lote.py del lote 2 (VALIDADOR-v2 de FAM05) como guion en este proceso (argv: raíz, manifiesto, resultado,
    salida, anexo [, selección]; raíz = datos/fam08: el manifiesto ENF no declara rutas relativas)."""
    F5.preparar()
    txt = F5.validador_adaptado()
    if "conexion_lambda" in sys.modules:
        need(Path(sys.modules["conexion_lambda"].__file__).resolve() == (F5.LOTE / "conexion_lambda.py").resolve(), "CONEXION_LAMBDA_DE_OTRO_LOTE")
    v = F5.LOTE / "validar_lote.py"
    viejo, ruta, buf, rc = sys.argv, list(sys.path), io.StringIO(), None
    sys.argv = [str(v), str(DATOS), str(man_p), str(res), str(sal), str(cob)] + ([json.dumps(sel)] if sel is not None else [])
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(txt, str(v), "exec"), {"__name__": "__main__", "__file__": str(v), "__builtins__": builtins})
    except SystemExit as ex:
        rc = ex.code
    finally:
        sys.argv = viejo
        sys.path[:] = ruta
    return types.SimpleNamespace(returncode=rc, stdout=buf.getvalue())


# ================================================================================================ declaración y pilotos
def regla_declaracion() -> dict:
    return {"kind": DECLARACION_KIND, "etiqueta": ETIQUETA, "oficial": False,
            "naturaleza": ("PUERTA-v1: las puertas de producción del trabajador ABL-ENF y de la integración (alcance v3 verificado y decisión "
                           "humana nativa) no se ejecutan ni se reconstruyen. El sha256 de este documento ocupa el campo alcance_sha256 que el "
                           "trabajador escribe tras su puerta y el de la puerta de integración. No es un alcance ni una decisión; no autoriza "
                           "producción oficial ni sustituye a los alcances históricos (5c64a6da… y 432e7052…, que solo se usan para cruzar huellas)."),
            "manifiestos": {"mallas": MAN_MALLAS[1], "techos": MAN_ENF[1], "integracion": MI_ENF[1]}, "codigo": dict(CODIGO),
            "instalacion_identidad": F5.C0_IDENTIDAD, "tareas": [ELAST] + list(TAREAS), "integracion": ["ENF-ENSAMBLADO-INTEGRAL", "ENF-CONCILIACION-INTEGRAL"]}


def regla_pilotos(man_m: dict, man_e: dict) -> dict:
    fr_ = man_m["L1-ELAST"]["fronteras"]
    pil = []
    for j in ("d", "f", "df"):
        k = next(k for k, v in fr_.items() if v.get("rol") == "ENF" and k.split("|")[1] == j)
        v = fr_[k]
        pil.append({"tarea": ELAST, "operacion": "F08-MALLAS", "unidad": v["frontier_id"], "clave": k, "instrumento": j, "clave_enf": v["clave_enf"],
                    "nodos": v["puntos_frontier_n4"], "dimension_malla": v["dimension_malla"], "limite_externo_s": 600.0,
                    "reloj_interno_s": F5.TOPE_TRABAJO - F5.HOLGURA,
                    "cobertura": "malla ENF completa (%d nodos, dimensión %d) con su topología; no es un supremo" % (v["puntos_frontier_n4"], v["dimension_malla"])})
    co = man_e["ABL-ENF"]
    t = "ABL-ENF-T2"
    cl = co["tareas"][t]
    cel = [c for c in co["celdas_afectadas"] if c["clave_transformada_sha256"] in cl]
    pil.append({"tarea": t, "operacion": "F08-TECHOS", "claves": [{"clave": k, "diseno": co["claves_recalculadas"][k]["diseno"], "j": co["claves_recalculadas"][k]["j"],
                                                                   "celdas": sum(1 for c in cel if c["clave_transformada_sha256"] == k)} for k in cl],
                "techos": len(cl), "comparaciones": len(cel), "limite_externo_s": F5.TOPE_TRABAJO, "reloj_interno_s": F5.TOPE_TRABAJO - F5.HOLGURA})
    return {"regla": ("fijados por el encargo de FAM08 antes de calcular y sin mirar resultados: la primera frontera de rol ENF de cada "
                      "instrumento d, f y df en el orden del manifiesto de mallas (cada piloto, la malla entera) y la tarea completa ABL-ENF-T2 "
                      "(sus dos techos y siete comparaciones, con los presupuestos científicos originales)"), "pilotos": pil}


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


def unidades(man_m: dict) -> list:
    return [{"unidad": v["frontier_id"], "clave": k, "rol": v.get("rol"), "diseno": k.split("|")[0], "instrumento": k.split("|")[1],
             "dimension_malla": v["dimension_malla"], "nodos": v["puntos_frontier_n4"]} for k, v in man_m["L1-ELAST"]["fronteras"].items()]


def seleccion(man_m: dict, unidad: str | None):
    if unidad is None:
        return None
    need(unidad in {v["frontier_id"] for v in man_m["L1-ELAST"]["fronteras"].values()}, "MALLA_FUERA_DEL_MANIFIESTO_ENF: %s" % unidad)
    return {"fronteras": [unidad]}


def listar() -> dict:
    raw_m, man_m = manifiesto_mallas()
    raw_e, man_e = manifiesto_enf()
    co, mm = man_e["ABL-ENF"], man_m["ABL-ENF-MALLAS"]
    u = unidades(man_m)
    return {"comando": "fam08-listar", "calculo": "ninguno", "manifiestos": {"mallas": sha(raw_m), "techos": sha(raw_e), "integracion": MI_ENF[1]},
            "operaciones": OPERACIONES,
            "recuento": {"mallas": len(u), "por_rol": dict(Counter(x["rol"] for x in u)), "nodos": sum(x["nodos"] for x in u),
                         "por_instrumento": dict(Counter(x["instrumento"] for x in u)), "pares": len(mm["pares"]),
                         "padres_por_modo": dict(Counter(p["padre"]["modo"] for p in mm["pares"])), "puntos_de_pares": sum(len(p["puntos"]) for p in mm["pares"]),
                         "controles_d": sum(1 for p in mm["pares"] if p["control_menu_d"]), "claves": len(co["claves_recalculadas"]),
                         "tareas": {t: len(v) for t, v in co["tareas"].items()},
                         "celdas_afectadas_por_tarea": {t: sum(1 for c in co["celdas_afectadas"] if c["clave_transformada_sha256"] in v) for t, v in co["tareas"].items()}},
            "unidades": u, "pilotos": fijar("pilotos.json", regla_pilotos(man_m, man_e)), "declaracion": fijar(DECLARACION, regla_declaracion())}


# ================================================================================================ lecturas y entorno
def declarados() -> set:
    out = set(F7.declarados())
    if (BASE / "fuentes_fam08.json").is_file():
        out |= {x["archivo"] for x in piezas()}
    return out


def lecturas(informe: dict, prohibidas: tuple = ()) -> dict:
    dec = declarados()
    propios = ("src/", "reproducir.py", "datos/fam01/", "datos/fam08/pilotos.json", "datos/fam08/" + DECLARACION, "fuentes_fam0", "catalogo.json")
    en = informe["en_el_paquete"]
    return {"archivo": "archivos_leidos.json", "en_el_paquete": len(en), "del_entorno_venv": sum(1 for x in en if x.startswith(".venv-fam01/")),
            "aperturas_del_interprete": informe["aperturas_del_interprete"], "fuera_del_paquete_y_del_interprete": informe["fuera_del_paquete_y_del_interprete"],
            "sin_manifiesto": [x for x in en if x not in dec and not x.startswith((".venv-fam01/",) + propios)],
            "nucleo_c0_leidos": sum(1 for x in en if x.startswith("nucleo_s6/c0/")), "codigo_enf_leido": sorted(x for x in en if x.startswith("nucleo_s6/enf/")),
            "guardadas_leidas": sorted({"/".join(x.split("/")[:5]) for x in en if x.startswith("datos/fam08/guardadas/")}),
            "fuentes_leidas": sorted(x for x in en if x in RUTAS_FUENTES.values()),
            "referencias_leidas": sorted(x for x in en if x.startswith("referencias/") and x not in RUTAS_FUENTES.values() and not x.startswith("referencias/fam01/")),
            "referencia_esperada_leida": any(x.startswith(prohibidas) for x in en) if prohibidas else False}


def entorno() -> dict:
    e = F5._entorno(None)
    e["f2_alcance"] = "adoptada solo para FAM01; aquí se informa y no es requisito de FAM08"
    return e


def importados() -> dict:
    return {"paper2b": sorted({rel(Path(m.__file__).parent) for k, m in list(sys.modules.items())
                               if (k == "paper2b" or k.startswith("paper2b.")) and getattr(m, "__file__", None)}),
            "modulos_enf": {k: {"archivo": rel(Path(sys.modules[k].__file__)), "texto_adaptado_sha256": getattr(sys.modules[k], "FAM08_ADAPTADO_SHA256", None)}
                            for k in MODULOS if k in sys.modules},
            "conexion_coord_cert": rel(Path(sys.modules["conexion_coord_cert"].__file__)) if "conexion_coord_cert" in sys.modules else None}


def _escribir(p: Path, doc: dict):
    p.write_bytes(json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True, default=str).encode("utf-8") + b"\n")


def productos_de(nueva: Path, res: dict) -> dict:
    return {p["archivo"]: sha_archivo(Path(nueva) / "salida" / p["archivo"]) for p in res.get("productos") or []}


# ================================================================================================ cálculo: F08-MALLAS y F08-TECHOS
def correr(tarea: str, salida: Path, unidad: str | None = None, tope: float = F5.TOPE_TRABAJO) -> dict:
    """fam08-unidad: L1-ELAST (las 29 mallas o una, --unidad) por la ruta de producción del lote 2 (TAREA-AST-v2 de FAM05) o una tarea
    ABL-ENF-T* por tarea_lote.py (GUION-v1, PUERTA-v1), en la carpeta NUEVA `salida`: resultado.json y salida/<productos>, ejecucion.json y
    archivos_leidos.json (y trabajo_stdout.txt en los techos)."""
    T0, c0 = time.time(), time.process_time()
    rastro = F1().Rastro()                       # desde el principio: también las lecturas previas al cálculo
    need(tarea == ELAST or tarea in TAREAS, "TAREA_FUERA_DE_FAM08: %s" % tarea)
    need(unidad is None or tarea == ELAST, "UNIDAD_SOLO_PARA_L1-ELAST")
    malos = fuentes_alteradas("calculo")
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam08.json; no se calcula): %s" % malos[:5])
    hdec, _ = declaracion()
    TOPE = float(tope) - F5.HOLGURA
    need(TOPE > 0, "TOPE_INVALIDO")
    salida = Path(salida)
    if tarea == ELAST:
        raw, man = manifiesto_mallas()
        sel = seleccion(man, unidad)
        mods = F5.pila()
        need(F5.identidad_c0() == F5.C0_IDENTIDAD, "NUCLEO_C0_DE_OTRA_IDENTIDAD (no se calcula)")
        salida.mkdir(parents=True, exist_ok=False)
        sal = salida.resolve()
        out = {"tarea": ELAST, "modo": "produccion", "manifiesto_sha256": sha(raw), "tope_efectivo_s": TOPE, "sintetico": False,
               "codigo_sha256": {n: sha((F5.LOTE / n).read_bytes()) for n in ("tarea_lote.py", "conexion_lambda.py", "conexion_frontera.py")}, "productos": []}
        ns, cod = F5.espacio(mods, sal / "salida", out, man, T0, TOPE)
        ns["R"] = DATOS                               # el manifiesto ENF no declara rutas relativas (sin suplemento)
        ns["fr_"] = {k: v for k, v in man["L1-ELAST"]["fronteras"].items() if sel is None or v["frontier_id"] in sel["fronteras"]}
        ruta, campos, exc, rc = list(sys.path), {}, None, None
        a0 = time.time()
        try:
            exec(cod[ELAST], ns)
            raise Fam08Error("RAMA_SIN_CIERRE")
        except F5.FinTarea as f:
            estado, motivo, campos = f.estado, f.motivo, f.campos
        finally:
            sys.path[:] = ruta
        t_calc = round(time.time() - a0, 2)
        out.update(estado=estado, motivo=motivo, pared_s=round(time.time() - T0, 2), **campos)
        (sal / "resultado.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
        res, techos = out, []
        ej = {"tarea": ELAST, "unidad": unidad, "operacion": "F08-MALLAS", "seleccion": sel,
              "naturaleza": "cálculo: ruta de producción L1-ELAST del lote 2 (bytes exactos, TAREA-AST-v2) con el manifiesto de mallas ENF y el núcleo C0",
              "alcance": "una malla ENF completa (piloto); una malla no acredita un supremo" if sel else "las 29 mallas del manifiesto ENF",
              "adaptaciones": ["TAREA-AST-v2", "FIN-v1", "PUERTA-v1", "NUCLEO-C0-v1", "SELECCION-UNIDAD-v1", "RELOJ-PILOTO-v1"]}
    else:
        raw, man = manifiesto_enf()
        preparar()
        need(F5.identidad_c0() == F5.C0_IDENTIDAD, "NUCLEO_C0_DE_OTRA_IDENTIDAD (no se calcula)")
        salida.mkdir(parents=True, exist_ok=False)
        sal = salida.resolve()
        args = ["--tarea", tarea, "--modo", "produccion", "--manifiesto", DATOS / MAN_ENF[0], "--manifiesto-sha256", MAN_ENF[1],
                "--salida", sal / "salida", "--resultado", sal / "resultado.json", "--tope-efectivo", repr(TOPE), "--instalacion", F5.C0,
                "--declaracion", DATOS / DECLARACION]
        a0 = time.time()
        rc, ult, stdout, exc = guion("techos/tarea_lote.py", args)
        t_calc = round(time.time() - a0, 2)
        (sal / "trabajo_stdout.txt").write_text(stdout, encoding="utf-8")
        res = leer(sal / "resultado.json") if (sal / "resultado.json").is_file() else {}
        estado, motivo = res.get("estado"), res.get("motivo")
        techos = leer_jsonl(sal / "salida" / PRODUCTOS[0]) if (sal / "salida" / PRODUCTOS[0]).is_file() else []
        co = man["ABL-ENF"]
        ej = {"tarea": tarea, "unidad": None, "operacion": "F08-TECHOS", "claves": co["tareas"][tarea], "seleccion": None,
              "naturaleza": ("cálculo: ruta de producción de tarea_lote.py ABL-ENF (bytes exactos, GUION-v1) con conexion_coord_cert y "
                             "RUN.provider_for(RUN.RunConfig()) (ModeloTeorico certificado) en la base limpia; sin puerta de producción (PUERTA-v1)"),
              "alcance": ("tarea completa de la partición" + (": la ruta histórica termina incompleta en la clave %s (tratamiento: fam08-recuperar)" % CLAVE_NA
                                                              if tarea == T1 else "")),
              "adaptaciones": ["GUION-v1", "MODULOS-v1", "NUCLEO-C0-v1", "RUTAS-FUENTES-v1", "SANEADO-v1", "PUERTA-v1", "RELOJ-PILOTO-v1"],
              "trabajador_adaptado_sha256": sha(adaptado("techos/tarea_lote.py").encode("utf-8")), "rc_del_trabajador": rc, "excepcion": exc, "ultima_linea": ult,
              "techos": [{k: t.get(k) for k in ("clave_transformada_sha256", "diseno", "estado", "motivo", "attained", "error_kind", "garantia", "C_2",
                                                "error_normalizado", "error_R", "cierre_por_escala", "final_n", "segundos")} for t in techos]}
    informe = rastro.informe()
    (sal / "archivos_leidos.json").write_bytes((json.dumps(informe, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    ej.update(manifiesto_sha256=sha(raw), etiqueta=ETIQUETA, declaracion_sha256=hdec,
              reloj="RELOJ-PILOTO-v1: tope interno %.0f s (= %.0f − %.0f); el límite externo lo pone el supervisor" % (TOPE, float(tope), F5.HOLGURA),
              resultado={"estado": estado, "motivo": motivo, "productos": res.get("productos")},
              nucleo={"identidad": F5.identidad_c0(), "importados": importados()},
              tiempos_s={"calculo": t_calc, "total": round(time.time() - T0, 2), "cpu": round(time.process_time() - c0, 2)},
              entorno=entorno(), lecturas=lecturas(informe), dependencias_fuera_de_la_biblioteca_estandar=F1().dependencias_cargadas())
    ej["termino"] = ej.get("excepcion") is None and estado in ("completa", "incompleta")
    ej["exito"] = estado == "completa" or (tarea == T1 and ej["termino"] and estado == "incompleta")
    if tarea == T1:
        ej["nota_T1"] = "T1 incompleta es el estado histórico aceptado; su validación es la recuperación (fam08-recuperar), no validar_lote"
    _escribir(sal / "ejecucion.json", ej)
    return ej


# ================================================================================================ validación (sin cálculo)
def validar(nueva: Path) -> dict:
    """fam08-validar: SIN CÁLCULO. Mallas: validador ELAST del lote 2 (VALIDADOR-v2) con la selección registrada; techos T2–T6:
    validar_lote.py ABL-ENF (validar_coord_rec.validar_tarea). T1 se valida con fam08-recuperar."""
    t0 = time.time()
    nueva = Path(nueva).resolve()
    malos = fuentes_alteradas("calculo")
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam08.json; no se valida): %s" % malos[:5])
    ej = leer(nueva / "ejecucion.json") if (nueva / "ejecucion.json").is_file() else {}
    rb = (nueva / "resultado.json").read_bytes() if (nueva / "resultado.json").is_file() else b"{}"
    res = json.loads(rb)
    tarea = res.get("tarea")
    need(tarea != T1, "T1_SE_VALIDA_CON_FAM08-RECUPERAR (su estado histórico es incompleta)")
    exc = None
    if tarea == ELAST:
        p = validador_elast(DATOS / MAN_MALLAS[0], nueva / "resultado.json", nueva / "salida", DATOS / COB_MALLAS[0], ej.get("seleccion"))
        rc, lineas = p.returncode, [x for x in p.stdout.splitlines() if x.strip()]
        ver = json.loads(lineas[-1]) if lineas else {}
        val = {"archivo": "nucleo_s6/lote2/validar_lote.py", "sha256": F5.CODIGO["validar_lote.py"], "adaptacion": [x[0] for x in F5.SUSTITUCIONES_VALIDADOR],
               "adaptado_sha256": sha(F5.validador_adaptado().encode("utf-8")), "manifiesto": "datos/fam08/" + MAN_MALLAS[0], "anexo": "datos/fam08/" + COB_MALLAS[0]}
    else:
        rc, ver, _, exc = guion("techos/validar_lote.py", [BASE, DATOS / MAN_ENF[0], nueva / "resultado.json", nueva / "salida"])
        val = {"archivos": {n: CODIGO[n] for n in ("techos/validar_lote.py", "techos/validar_coord_rec.py")},
               "adaptacion": {n: [x[0] for x in SUSTITUCIONES[n]] for n in ("techos/validar_lote.py", "techos/validar_coord_rec.py")},
               "adaptado_sha256": {n: sha(adaptado(n).encode("utf-8")) for n in ("techos/validar_lote.py", "techos/validar_coord_rec.py")}}
    return {"comando": "fam08-validar", "naturaleza": "validación sin cálculo de bytes guardados", "tarea": tarea, "unidad": ej.get("unidad"),
            "seleccion": ej.get("seleccion"), "origen": rel(nueva), "resultado_sha256": sha(rb), "productos_sha256": productos_de(nueva, res),
            "validador": dict(val, nucleo="nucleo_s6/c0 (NUCLEO-C0-v1)"), "rc": rc, "veredicto": ver, "excepcion": exc,
            "aceptada": exc is None and rc == 0 and ver.get("aceptada") is True and ver.get("dictamen") == "completa_validada", "segundos": round(time.time() - t0, 3)}


def _validacion_de(val: dict | None, nueva: Path, rb: bytes, res: dict, tarea: str) -> list:
    if val is None:
        return ["VALIDACION_AUSENTE"]
    mot = []
    if tarea == T1:
        t1 = val.get("t1") or {}
        if val.get("comando") != "fam08-recuperar" or t1.get("origen") != rel(nueva) or t1.get("resultado_sha256") != sha(rb):
            mot.append("RECUPERACION_DE_OTROS_BYTES")
        if t1.get("aceptada") is not True:
            mot.append("RECUPERACION_NO_ACEPTADA")
        return mot
    if val.get("comando") != "fam08-validar" or val.get("origen") != rel(nueva) or val.get("resultado_sha256") != sha(rb) \
            or val.get("productos_sha256") != productos_de(nueva, res) or val.get("tarea") != tarea:
        mot.append("VALIDACION_DE_OTROS_BYTES")
    if val.get("aceptada") is not True:
        mot.append("VALIDACION_NO_ACEPTADA: %s" % ((val.get("veredicto") or {}).get("fallos") or [])[:3])
    return mot


# ================================================================================================ comparación de mallas y techos
# COMPARACION-FAM08-v1. Mismo perfil de entorno .venv-fam01 y MISMO núcleo C0 que las referencias. CR-HASH-CANONICO (cada fila idéntica
# campo a campo con su serialización JSON: valores, cotas, errores en sus dos escalas, testigos, topología) y CR-DISCRETOS (claves, celdas,
# estados, clasificaciones, garantías, certificados y conteos exactos, con precedencia). Las tolerancias internas de los validadores (T1 =
# 1e-12 del control d, Iv, 1e-7) son suyas y no se usan aquí. Se apartan, visibles, solo: OPERATIVO «segundos»/«pared_s»; VINCULO
# «alcance_sha256» (nueva = declaración de ejecución limpia; referencia = alcance histórico) y las huellas de las entradas nuevas; PUERTA
# (puerta/decision, sin decisión humana); UBICACION (carpetas y la ruta del validador). Las huellas derivadas se recomprueban.
def _resultado_igual(res: dict, ref_res: dict, mot: list) -> dict:
    rr = {}
    for k in ("tarea", "modo", "sintetico", "estado", "motivo", "tope_efectivo_s"):
        rr[k] = {"nueva": res.get(k), "referencia": ref_res.get(k), "igual": res.get(k) == ref_res.get(k)}
        if not rr[k]["igual"]:
            mot.append("RESULTADO_DISTINTO: %s" % k)
    return rr


def _motivos_filas(o: dict, n: str, mot: list, bytes_exactos: bool = True):
    c = o["cobertura"]
    if c["faltan"] or c["ajenas"] or c["duplicadas"] or not c["mismo_orden"] or c["filas_nuevas"] != c["filas_referencia"] or not c["filas_referencia"]:
        mot.append("COBERTURA_DISTINTA (CR-DISCRETOS): %s" % n)
    if o["n_discretas"]:
        mot.append("DIFERENCIA_DISCRETA (CR-DISCRETOS, precedencia): %s %s" % (n, [x["puntero"] for x in o["discretas"][:4]]))
    if o["n_numericas"]:
        mot.append("DIFERENCIA_NUMERICA (CR-HASH-CANONICO): %s %s" % (n, [x["puntero"] for x in o["numericas"][:4]]))
    if bytes_exactos and not o["lineas_identicas"]:
        mot.append("BYTES_DISTINTOS: %s" % n)


def _lineas(p: Path) -> list:
    return [x for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.is_file() else []


def comparar_mallas(nueva: Path, validacion: Path) -> dict:
    """fam08-comparar --tarea L1-ELAST: filas de la(s) malla(s) de la nueva frente al producto aceptado (L_rem128, guardado en
    datos/fam08/guardadas; 11d55c44…), resultado y validación frente a la histórica."""
    nueva = Path(nueva).resolve()
    raw, man = manifiesto_mallas()
    mot = []
    ej = leer(nueva / "ejecucion.json") if (nueva / "ejecucion.json").is_file() else {}
    rb = (nueva / "resultado.json").read_bytes() if (nueva / "resultado.json").is_file() else b"{}"
    res = json.loads(rb)
    sel = ej.get("seleccion")
    if ej.get("tarea") != ELAST or res.get("tarea") != ELAST or ej.get("etiqueta") != ETIQUETA:
        mot.append("SALIDA_DE_OTRA_TAREA_O_SIN_EJECUCION_FAM08")
    if sel != seleccion(man, ej.get("unidad")):
        mot.append("SELECCION_INCOHERENTE")
    val = leer(validacion) if Path(validacion).is_file() else None
    mot += _validacion_de(val, nueva, rb, res, ELAST)
    if res.get("estado") != "completa":
        mot.append("CALCULO_NO_COMPLETO: %s" % res.get("motivo"))
    m = mi()["mallas"]
    ref_res = leer(MALLAS_GUARDADA / "resultado.json")
    fref = MALLAS_GUARDADA / "salida/frontier_result.jsonl"
    if sha_archivo(fref) != m["producto_sha256"] or sha_archivo(MALLAS_GUARDADA / "resultado.json") != m["resultado_sha256"]:
        mot.append("REFERENCIA_ALTERADA_O_AJENA: mallas guardadas")
    decl = {p["archivo"]: p for p in res.get("productos") or []}
    fn = nueva / "salida/frontier_result.jsonl"
    objetos = {}
    if sorted(decl) != ["frontier_result.jsonl"] or sha_archivo(fn) != (decl.get("frontier_result.jsonl") or {}).get("sha256"):
        mot.append("PRODUCTO_AUSENTE_O_ALTERADO: frontier_result.jsonl")
    else:
        ref_l = [x for x in _lineas(fref) if F5.en_unidad("frontier_result.jsonl", json.loads(x), sel)]
        o = F5.comparar_producto("frontier_result.jsonl", _lineas(fn), ref_l, None)
        _motivos_filas(o, "frontier_result.jsonl", mot)
        objetos["frontier_result.jsonl"] = o
    rr = _resultado_igual(res, ref_res, mot)
    ident = {"manifiesto_sha256": res.get("manifiesto_sha256") == ref_res.get("manifiesto_sha256") == MAN_MALLAS[1],
             "codigo_sha256": res.get("codigo_sha256") == ref_res.get("codigo_sha256"), "nucleo_c0": (ej.get("nucleo") or {}).get("identidad") == F5.C0_IDENTIDAD}
    if not all(ident.values()):
        mot.append("IDENTIDAD_DISTINTA: %s" % [k for k, v in ident.items() if not v])
    vh = json.loads((REF / "rem127/L1-ELAST/validacion_stdout.txt").read_text(encoding="utf-8"))
    deriv = {"validacion_igual_a_la_historica": ((val or {}).get("veredicto") or {}) == vh}
    if not deriv["validacion_igual_a_la_historica"]:
        mot.append("VALIDACION_DISTINTA_DE_LA_HISTORICA")
    filas = leer_jsonl(fn) if fn.is_file() else []
    deriv["filas"] = {"puntos": sum(1 for f in filas if f.get("side") == "point"), "laterales": sum(1 for f in filas if f.get("side") != "point"),
                      "regimenes": dict(Counter(f.get("regime") for f in filas)), "topologias": dict(Counter(f.get("topology") for f in filas))}
    if sel is None and res.get("productos") != ref_res.get("productos"):
        mot.append("PRODUCTOS_DISTINTOS_DE_LA_TAREA_DE_REFERENCIA")
    return {"comando": "fam08-comparar", "tarea": ELAST, "unidad": ej.get("unidad"), "operacion": "F08-MALLAS", "seleccion": sel,
            "regla": "COMPARACION-FAM08-v1 (src/fam08.py)", "criterios": ["CR-HASH-CANONICO (mismo entorno y núcleo C0; exacta)", "CR-DISCRETOS (precedencia)"],
            "referencia": {"producto": rel(fref), "sha256": m["producto_sha256"], "alcance": "misma malla (selección)" if sel else "las 29 mallas"},
            "nueva": rel(nueva), "validacion": rel(Path(validacion)), "objetos": objetos, "resultado": rr, "identidades": ident, "derivados": deriv,
            "operativos": {"pared_s": {"nueva": res.get("pared_s"), "referencia_tarea": ref_res.get("pared_s")}},
            "estado": {"reproduccion": "aceptada" if not mot else "no_aceptada", "motivos": mot}}


def comparar_techos(tarea: str, nueva: Path, validacion: Path) -> dict:
    """fam08-comparar --tarea ABL-ENF-T*: salida de fam08-unidad frente a la tarea aceptada (bytes guardados = pines del manifiesto
    integral) y la validación frente a la histórica (T1: la recuperación de fam08-recuperar)."""
    nueva = Path(nueva).resolve()
    raw, man = manifiesto_enf()
    co = man["ABL-ENF"]
    mot = []
    ej = leer(nueva / "ejecucion.json") if (nueva / "ejecucion.json").is_file() else {}
    rb = (nueva / "resultado.json").read_bytes() if (nueva / "resultado.json").is_file() else b"{}"
    res = json.loads(rb)
    if ej.get("tarea") != tarea or res.get("tarea") != tarea or ej.get("etiqueta") != ETIQUETA:
        mot.append("SALIDA_DE_OTRA_TAREA_O_SIN_EJECUCION_FAM08")
    val = leer(validacion) if Path(validacion).is_file() else None
    mot += _validacion_de(val, nueva, rb, res, tarea)
    ref_d = guardada(tarea)
    pin = pines()[tarea]
    ref_rb = (ref_d / "resultado.json").read_bytes()
    ref_res = json.loads(ref_rb)
    if sha(ref_rb) != pin["resultado_sha256"] or any(sha_archivo(ref_d / "salida" / n) != pin["productos"][n] for n in PRODUCTOS):
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
        o = F7.comparar_filas(_lineas(fn), _lineas(fref), ("clave_transformada_sha256",) if es_techo else ("unidad", "cell_id"),
                              ("/segundos",) if es_techo else (), {None: {"/alcance_sha256": (res.get("alcance_sha256"), ref_res.get("alcance_sha256"))}} if es_techo else None)
        _motivos_filas(o, n, mot, bytes_exactos=not es_techo)
        if es_techo:
            v = o["vinculo"]
            if not (v["filas"] == v["nueva_ligada"] == v["referencia_ligada"] == o["cobertura"]["filas_referencia"]) or res.get("alcance_sha256") != hdec \
                    or ref_res.get("alcance_sha256") != ALC_ENF[1]:
                mot.append("VINCULO_ROTO: alcance_sha256 (nueva = declaración de ejecución limpia; referencia = alcance histórico)")
            deriv["huella_derivada_de_los_techos"] = F7.huella_derivada(fn.read_bytes(), fref.read_bytes())
            if not deriv["huella_derivada_de_los_techos"]["igual"] and not o["n_discretas"] and not o["n_numericas"]:
                mot.append("HUELLA_DERIVADA_DISTINTA: techos")
        objetos[n] = o
    nuevas_t = leer_jsonl(nueva / "salida" / PRODUCTOS[0]) if (nueva / "salida" / PRODUCTOS[0]).is_file() else []
    nuevas_c = leer_jsonl(nueva / "salida" / PRODUCTOS[1]) if (nueva / "salida" / PRODUCTOS[1]).is_file() else []
    por_t = {t["clave_transformada_sha256"]: t for t in nuevas_t}
    cel = [c for c in co["celdas_afectadas"] if c["clave_transformada_sha256"] in co["tareas"][tarea]]
    cert = [t for t in nuevas_t if t.get("estado") == "complete" and t.get("error_kind") == "certified_bound" and t.get("garantia") == "ieee754_binary64_rn"
            and (t.get("error_normalizado") or 1) <= 1e-7 and (t.get("cierre_por_escala") or {}).get("normalizada") is True]
    abiertas = [t for t in nuevas_t if t.get("estado") != "complete"]
    deriv["techos_certificados_y_cerrados"] = len(cert)
    deriv["techos_abiertos"] = [{"clave": t["clave_transformada_sha256"], "estado": t.get("estado"), "motivo": t.get("motivo"), "attained": t.get("attained")} for t in abiertas]
    deriv["comparaciones_G_igual_C2_menos_K1"] = sum(1 for x in nuevas_c if F7.g_ok(x, por_t.get(x.get("clave_transformada_sha256"))))
    deriv["comparaciones_de_claves_abiertas_sin_G"] = sum(1 for x in nuevas_c if (por_t.get(x.get("clave_transformada_sha256")) or {}).get("estado") != "complete"
                                                          and x.get("G_coord") is None)
    deriv["cobertura"] = {"claves": sorted(por_t) == sorted(co["tareas"][tarea]), "celdas": sorted((x["unidad"], x["cell_id"]) for x in nuevas_c)
                          == sorted((c["unidad"], c["cell_id"]) for c in cel), "techos": len(nuevas_t), "comparaciones": len(nuevas_c)}
    esperadas_abiertas = [CLAVE_NA] if tarea == T1 else []
    if not (deriv["cobertura"]["claves"] and deriv["cobertura"]["celdas"] and len(cert) + len(abiertas) == len(nuevas_t)
            and [x["clave"] for x in deriv["techos_abiertos"]] == esperadas_abiertas
            and all(x["motivo"] == MOTIVO_NA and x["attained"] is False for x in deriv["techos_abiertos"])
            and deriv["comparaciones_G_igual_C2_menos_K1"] + deriv["comparaciones_de_claves_abiertas_sin_G"] == len(nuevas_c) == len(cel)):
        mot.append("COBERTURA_CERTIFICADOS_O_CLASIFICACION_INCOMPLETOS")
    rr = _resultado_igual(res, ref_res, mot)
    ident = {"manifiesto_sha256": res.get("manifiesto_sha256") == ref_res.get("manifiesto_sha256") == MAN_ENF[1],
             "codigo_sha256": res.get("codigo_sha256") == ref_res.get("codigo_sha256") == {Path(n).name: CODIGO[n] for n in ("techos/tarea_lote.py", "techos/conexion_coord_cert.py")},
             "nucleo_c0": (ej.get("nucleo") or {}).get("identidad") == F5.C0_IDENTIDAD,
             "producto_de_comparaciones_igual": (decl.get(PRODUCTOS[1]) or {}).get("sha256") == pin["productos"][PRODUCTOS[1]]}
    if not all(ident.values()):
        mot.append("IDENTIDAD_DISTINTA: %s" % [k for k, v in ident.items() if not v])
    if tarea != T1:
        vh = json.loads((REF / "rem128" / tarea / "validacion_stdout.txt").read_text(encoding="utf-8"))
        vn = (val or {}).get("veredicto") or {}
        deriv["validacion_frente_a_la_historica"] = {
            "iguales_salvo_huellas_propias": {k: v for k, v in vn.items() if k not in ("resultado_sha256", "productos_sha256")}
            == {k: v for k, v in vh.items() if k not in ("resultado_sha256", "productos_sha256")},
            "huellas_propias": vn.get("resultado_sha256") == sha(rb) and vn.get("productos_sha256") == productos_de(nueva, res)}
        if not all(deriv["validacion_frente_a_la_historica"].values()):
            mot.append("VALIDACION_DISTINTA_DE_LA_HISTORICA")
    return {"comando": "fam08-comparar", "tarea": tarea, "operacion": "F08-TECHOS", "regla": "COMPARACION-FAM08-v1 (src/fam08.py)",
            "criterios": ["CR-HASH-CANONICO (mismo entorno y núcleo C0; exacta)", "CR-DISCRETOS (precedencia)",
                          "OPERATIVO segundos y VINCULO alcance_sha256 (apartados, visibles)"],
            "referencia": {"ejecucion": rel(ref_d), "resultado_sha256": sha(ref_rb), "productos": pin["productos"]},
            "nueva": rel(nueva), "validacion": rel(Path(validacion)), "objetos": objetos, "resultado": rr, "identidades": ident, "derivados": deriv,
            "operativos": {"pared_s": {"nueva": res.get("pared_s"), "referencia": ref_res.get("pared_s")},
                           "segundos_por_techo": {"nueva": {t["clave_transformada_sha256"]: t.get("segundos") for t in nuevas_t},
                                                  "referencia": {t["clave_transformada_sha256"]: t.get("segundos") for t in leer_jsonl(ref_d / "salida" / PRODUCTOS[0])}}},
            "estado": {"reproduccion": "aceptada" if not mot else "no_aceptada", "motivos": mot}}


# ================================================================================================ entradas declaradas (guardadas o nuevas)
def _filas_mallas(sust: dict):
    def f(filas):
        if not sust:
            return filas
        out, puestas = [], set()
        for r in filas:
            fid = r.get("frontier_id")
            if fid in sust:
                if fid not in puestas:
                    out += sust[fid]
                    puestas.add(fid)
                continue
            out.append(r)
        need(puestas == set(sust), "MALLA_PILOTO_AUSENTE_DEL_PRODUCTO_GUARDADO: %s" % sorted(set(sust) - puestas))
        return out
    return f


def entradas_mallas(mallas, pilotos=()) -> tuple:
    """Mallas declaradas: «guardado» (producto aceptado rem127, pines del manifiesto integral) o una carpeta de fam08-unidad L1-ELAST
    completa; con «pilotos» (solo sobre las guardadas): las filas de cada malla piloto salen de SU salida nueva, validada por fam08-validar
    (<carpeta>.validacion.json) para esos bytes, y sustituyen a las guardadas de esa malla (procedencia mixta)."""
    m = mi()["mallas"]
    need(mallas is not None, "MALLAS_SIN_DECLARAR (carpeta nueva o «%s»)" % GUARDADO)
    if str(mallas) == GUARDADO:
        d = MALLAS_GUARDADA
        need(sha_archivo(d / "resultado.json") == m["resultado_sha256"] and sha_archivo(d / "salida/frontier_result.jsonl") == m["producto_sha256"],
             "MALLAS_GUARDADAS_ALTERADAS_O_AJENAS")
        pins = {k: m[k] for k in ("producto_sha256", "resultado_sha256")}
        proc = {"procedencia": "guardada", "carpeta": rel(d), "naturaleza": "producto aceptado L_rem128 (bytes guardados; no se recalcula)"}
    else:
        d = Path(mallas).resolve()
        ej = leer(d / "ejecucion.json") if (d / "ejecucion.json").is_file() else {}
        need(ej.get("etiqueta") == ETIQUETA and ej.get("tarea") == ELAST and ej.get("seleccion") is None, "MALLAS_NUEVAS_SIN_EJECUCION_FAM08_COMPLETA")
        pins = {"producto_sha256": sha_archivo(d / "salida/frontier_result.jsonl"), "resultado_sha256": sha_archivo(d / "resultado.json")}
        proc = {"procedencia": "nueva", "carpeta": rel(d), "naturaleza": "salida nueva de fam08-unidad L1-ELAST (las 29 mallas; el conciliador la valida)"}
    sust, pil = {}, []
    for p in pilotos or ():
        need(str(mallas) == GUARDADO, "PILOTOS_SOLO_SOBRE_LAS_MALLAS_GUARDADAS")
        p = Path(p).resolve()
        v = Path(str(p) + ".validacion.json")
        need(v.is_file() and (p / "ejecucion.json").is_file(), "PILOTO_SIN_VALIDACION_O_SIN_EJECUCION: %s" % rel(p))
        val, ej = leer(v), leer(p / "ejecucion.json")
        rb = (p / "resultado.json").read_bytes()
        res = json.loads(rb)
        need(val.get("comando") == "fam08-validar" and val.get("origen") == rel(p) and val.get("resultado_sha256") == sha(rb)
             and val.get("productos_sha256") == productos_de(p, res) and val.get("aceptada") is True, "VALIDACION_DEL_PILOTO_NO_ACEPTADA_O_DE_OTROS_BYTES: %s" % rel(p))
        need(ej.get("etiqueta") == ETIQUETA and ej.get("tarea") == ELAST and len((ej.get("seleccion") or {}).get("fronteras") or []) == 1
             and res.get("estado") == "completa", "PILOTO_NO_ES_UNA_MALLA_COMPLETA: %s" % rel(p))
        fid = ej["seleccion"]["fronteras"][0]
        need(fid not in sust, "MALLA_PILOTO_DUPLICADA: %s" % fid)
        filas = leer_jsonl(p / "salida/frontier_result.jsonl")
        need(filas and all(f.get("frontier_id") == fid for f in filas), "FILAS_AJENAS_A_LA_MALLA_PILOTO: %s" % fid)
        sust[fid] = filas
        pil.append({"malla": fid, "carpeta": rel(p), "validacion": rel(v), "producto_sha256": sha_archivo(p / "salida/frontier_result.jsonl"), "filas": len(filas)})
    if pil:
        proc = dict(proc, procedencia="mixta", naturaleza=("filas de %d mallas piloto desde sus salidas nuevas validadas; las demás, del producto "
                                                            "aceptado guardado (no acredita el cálculo de las restantes)") % len(pil))
    return {"mallas_dir": str(d), "mallas_pins": pins, "filas_mallas": _filas_mallas(sust)}, dict(proc, pilotos=pil)


def entradas_techos(ent: dict) -> tuple:
    """Tareas declaradas: «guardado» (bytes aceptados, pines del manifiesto integral) o carpeta de fam08-unidad (ENTRADAS-v1: pines = SUS
    bytes; alcance = la declaración). Una tarea no declarada no se sustituye: validar_fuentes la rechaza."""
    pin = pines()
    hdec = sha_archivo(DATOS / DECLARACION)
    dirs, pins, origen = {}, {}, {}
    for t in TAREAS:
        v = ent.get(t)
        if v is None:
            origen[t] = {"procedencia": "ausente", "nota": "sin carpeta declarada: no se sustituye por la referencia (la integración se rechaza)"}
            continue
        if str(v) == GUARDADO:
            d = guardada(t)
            need(sha_archivo(d / "resultado.json") == pin[t]["resultado_sha256"] and all(sha_archivo(d / "salida" / n) == pin[t]["productos"][n] for n in PRODUCTOS),
                 "TAREA_GUARDADA_ALTERADA_O_AJENA: %s" % t)
            origen[t] = {"procedencia": "guardada", "carpeta": rel(d),
                         "naturaleza": "salida aceptada (bytes guardados; no se recalcula ni acredita cálculo nuevo)" + ("; T1 histórica incompleta" if t == T1 else "")}
        else:
            d = Path(v).resolve()
            ej = leer(d / "ejecucion.json") if (d / "ejecucion.json").is_file() else {}
            need(ej.get("etiqueta") == ETIQUETA and ej.get("tarea") == t, "CARPETA_SIN_EJECUCION_FAM08: %s" % t)
            rs = leer(d / "resultado.json")
            need(rs.get("alcance_sha256") == hdec, "TAREA_NUEVA_SIN_LA_DECLARACION_DE_EJECUCION_LIMPIA: %s" % t)
            pins[t] = {"directorio": rel(d), "resultado_sha256": sha_archivo(d / "resultado.json"),
                       "productos": {n: sha_archivo(d / "salida" / n) for n in PRODUCTOS}, "alcance_origen_sha256": rs.get("alcance_sha256")}
            origen[t] = {"procedencia": "nueva", "carpeta": rel(d), "naturaleza": "salida de fam08-unidad (cálculo nuevo en la base limpia)",
                         "estado_de_su_ejecucion": rs.get("estado")}
        dirs[t] = str(d)
    return dirs, pins, origen


def _naturaleza(procs: set) -> str:
    return (REGENERACION if procs == {"guardada"} else NUEVA if procs == {"nueva"} else MIXTA if "ausente" not in procs
            else "incompleta: faltan entradas (no se sustituyen por referencias)")


# ================================================================================================ F08-PARES: conciliación de mallas
def conciliar(salida: Path, mallas, pilotos=()) -> dict:
    """fam08-conciliar: conciliar_mallas_enf.py (rem126; RUTAS-FUENTES-v1, ENTRADAS-MALLAS-v1, VALIDADOR-ELAST-v1) sobre las mallas
    declaradas y las 23 mallas padre reutilizadas autenticadas. Escribe en la carpeta NUEVA `salida`: conciliacion/ (CONCILIACION_MALLAS_ENF.json
    y pares_puntos.jsonl), conciliacion_stdout.txt, ejecucion.json y archivos_leidos.json. No lee la conciliación esperada."""
    T0 = time.time()
    rastro = F1().Rastro()
    malos = fuentes_alteradas("regeneracion", [rel(MALLAS_GUARDADA)] if str(mallas) == GUARDADO else [])
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam08.json; no se concilia): %s" % malos[:5])
    manifiesto_mallas()
    ent, proc = entradas_mallas(mallas, pilotos)
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    sal = salida.resolve()
    a0 = time.time()
    rc, ult, stdout, exc = guion("mallas/conciliar_mallas_enf.py", [BASE, DATOS / MAN_MALLAS[0], DATOS / COB_MALLAS[0], sal / "conciliacion", "."],
                                 {"RUTAS_FUENTES": RUTAS_FUENTES, "ENTRADAS": ent, "VALIDADOR_ELAST": validador_elast})
    t_c = round(time.time() - a0, 2)
    (sal / "conciliacion_stdout.txt").write_text(stdout, encoding="utf-8")
    informe = rastro.informe()
    (sal / "archivos_leidos.json").write_bytes((json.dumps(informe, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    nat = {"guardada": REGENERACION + ": los 26 pares desde el producto de mallas aceptado y las 23 mallas padre reutilizadas; ninguna malla se recalcula",
           "nueva": "conciliación de las 29 mallas recalculadas (salida nueva) con las 23 mallas padre reutilizadas",
           "mixta": MIXTA + ": mallas piloto recalculadas y validadas con las demás guardadas"}[proc["procedencia"]]
    ej = {"comando": "fam08-conciliar", "operacion": "F08-PARES", "etiqueta": ETIQUETA, "naturaleza": nat, "mallas": proc,
          "acredita": {"guardada": "F08-PARES como regeneración documental; NO acredita F08-MALLAS",
                       "nueva": "F08-PARES sobre mallas recalculadas en la base limpia",
                       "mixta": "la conexión de las mallas piloto a la conciliación; las demás mallas NO se han calculado aquí"}[proc["procedencia"]],
          "conciliador": {"archivo": "nucleo_s6/enf/mallas/conciliar_mallas_enf.py", "sha256": CODIGO["mallas/conciliar_mallas_enf.py"],
                          "adaptacion": [x[0] for x in SUSTITUCIONES["mallas/conciliar_mallas_enf.py"]],
                          "adaptado_sha256": sha(adaptado("mallas/conciliar_mallas_enf.py").encode("utf-8"))},
          "rc": rc, "veredicto": ult, "excepcion": exc,
          "productos": {n: sha_archivo(sal / "conciliacion" / n) for n in ("CONCILIACION_MALLAS_ENF.json", "pares_puntos.jsonl")},
          "tiempos_s": {"conciliacion": t_c, "total": round(time.time() - T0, 2)},
          "lecturas": lecturas(informe, ("referencias/fam08/rem128/conciliacion_mallas/", "referencias/fam08/rem131/"))}
    ej["exito"] = rc == 0 and exc is None and ult.get("aceptada") is True and not ej["lecturas"]["referencia_esperada_leida"]
    _escribir(sal / "ejecucion.json", ej)
    return ej


def recuentos_pares(c: dict, filas: list) -> dict:
    ctl = [p for p in c.get("pares") or [] if p.get("control_menu_d")]
    return {"pares": len(c.get("pares") or []), "filas_comparadas": len(filas), "filas_comparables": sum(p["filas_comparables"] for p in c.get("pares") or []),
            "controles_d": len(ctl), "controles_d_con_igualdad": sum(1 for p in ctl if p["max_abs_dR"] == 0.0 and p["max_abs_dCS"] == 0.0),
            "puntos_con_cambio_de_topologia": sum(p["puntos_con_cambio_topologia"] for p in c.get("pares") or []),
            "pares_con_cambio_de_topologia": [p["par_id"] for p in c.get("pares") or [] if p["puntos_con_cambio_topologia"]],
            "puntos_con_cambio_de_regimen": sum(p["puntos_con_cambio_regimen"] for p in c.get("pares") or []),
            "no_comparables": sum(len(p["no_comparables"]) for p in c.get("pares") or []),
            "origen_padre": dict(Counter(p["origen_padre"] for p in c.get("pares") or [])), "dictamen": c.get("dictamen"), "aceptada": c.get("aceptada")}


def _comparar_doc(n: dict, r: dict, ubic=(), puerta=(), vinc: dict | None = None) -> dict:
    hn, hr = F5.hojas(n), F5.hojas(r)
    out = {"ubicacion": [], "puerta": [], "vinculos": [], "discretas": [], "numericas": []}
    vinc = vinc or {}
    for p in sorted(set(hn) | set(hr)):
        a, b = hn.get(p, "<ausente>"), hr.get(p, "<ausente>")
        if any(re.fullmatch(x, p) for x in puerta):
            out["puerta"].append({"puntero": p, "nueva": a, "referencia": b})
        elif any(re.fullmatch(x, p) for x in ubic):
            out["ubicacion"].append({"puntero": p, "nueva": a, "referencia": b})
        elif p in vinc:
            out["vinculos"].append({"puntero": p, "nueva_ligada": a == vinc[p][0], "referencia_ligada": b == vinc[p][1]})
        elif json.dumps(a) != json.dumps(b):
            numerico = all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in (a, b))
            (out["numericas"] if numerico else out["discretas"]).append({"puntero": p, "nueva": a, "referencia": b})
    out["vinculos_completos"] = len(out["vinculos"]) == len(vinc) and all(x["nueva_ligada"] and x["referencia_ligada"] for x in out["vinculos"])
    return out


def _ultima(p: Path) -> dict:
    ls = [x for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.is_file() else []
    try:
        return json.loads(ls[-1]) if ls else {}
    except ValueError:
        return {}


def comparar_pares(nueva: Path) -> dict:
    """fam08-comparar --tarea PARES: salida de fam08-conciliar frente a la conciliación aceptada rem128 (pares_puntos 11a9d2d7… y la
    proyección de CONCILIACION_MALLAS_ENF.json), con los recuentos obtenidos de la NUEVA y también de la referencia."""
    nueva = Path(nueva).resolve()
    mot = []
    ej = leer(nueva / "ejecucion.json") if (nueva / "ejecucion.json").is_file() else {}
    if ej.get("comando") != "fam08-conciliar" or ej.get("etiqueta") != ETIQUETA:
        mot.append("SALIDA_SIN_EJECUCION_DE_FAM08_CONCILIAR")
    if {n: sha_archivo(REF_PARES / n) for n in ACEPTADO["pares"]} != ACEPTADO["pares"]:
        mot.append("REFERENCIA_ALTERADA_O_AJENA: conciliación rem128")
    C = nueva / "conciliacion"
    c = leer(C / "CONCILIACION_MALLAS_ENF.json") if (C / "CONCILIACION_MALLAS_ENF.json").is_file() else {}
    cr = leer(REF_PARES / "CONCILIACION_MALLAS_ENF.json")
    o = F7.comparar_filas(_lineas(C / "pares_puntos.jsonl"), _lineas(REF_PARES / "pares_puntos.jsonl"), ("par_id", "tau_d", "tau_f", "side"))
    _motivos_filas(o, "pares_puntos.jsonl", mot)
    nueva_m = (ej.get("mallas") or {}).get("procedencia") == "nueva"
    m = mi()["mallas"]
    vinc = {"/producto_mallas_sha256": (((ej.get("mallas") or {}).get("carpeta") and sha_archivo(BASE / ej["mallas"]["carpeta"] / "salida/frontier_result.jsonl")),
                                        m["producto_sha256"]),
            "/resultado_mallas_sha256": (((ej.get("mallas") or {}).get("carpeta") and sha_archivo(BASE / ej["mallas"]["carpeta"] / "resultado.json")),
                                         m["resultado_sha256"])} if nueva_m else {}
    doc = _comparar_doc(c, cr, ubic=(r"/validador_elast/ruta",), vinc=vinc)
    if doc["discretas"] or doc["numericas"] or not doc["vinculos_completos"]:
        mot.append("CONCILIACION_JSON_DISTINTA: %s" % [x["puntero"] for x in (doc["discretas"] + doc["numericas"])[:4]])
    if c.get("pares_puntos_sha256") != sha_archivo(C / "pares_puntos.jsonl"):
        mot.append("HUELLA_DERIVADA_DISTINTA_DE_SUS_BYTES: pares_puntos_sha256")
    rn, rr = recuentos_pares(c, leer_jsonl(C / "pares_puntos.jsonl") if (C / "pares_puntos.jsonl").is_file() else []), recuentos_pares(cr, leer_jsonl(REF_PARES / "pares_puntos.jsonl"))
    if rn != rr:
        mot.append("RECUENTOS_DISTINTOS: %s" % sorted(k for k in rn if rn[k] != rr.get(k)))
    so = _ultima(nueva / "conciliacion_stdout.txt")
    sh = json.loads((REF / "rem128/REM128_CONC_MALLAS.txt").read_text(encoding="utf-8"))
    if so != sh:
        mot.append("VEREDICTO_DEL_CONCILIADOR_DISTINTO")
    return {"comando": "fam08-comparar", "tarea": PARES, "operacion": "F08-PARES", "naturaleza": ej.get("naturaleza"), "acredita": ej.get("acredita"),
            "mallas": ej.get("mallas"), "regla": "COMPARACION-FAM08-v1 (src/fam08.py)",
            "referencia": {"conciliacion": rel(REF_PARES), "productos": ACEPTADO["pares"], "CONCILIACION_MALLAS_ENF.json": "proyección del catálogo (original 4d2b0748…)"},
            "nueva": rel(nueva), "objetos": {"pares_puntos.jsonl": o}, "conciliacion_json": doc, "recuentos": rn, "recuentos_de_la_referencia_iguales": rn == rr,
            "veredicto_del_conciliador_igual": so == sh, "bytes_identicos_a_la_referencia": {"pares_puntos.jsonl": sha_archivo(C / "pares_puntos.jsonl") == ACEPTADO["pares"]["pares_puntos.jsonl"]},
            "estado": {"reproduccion": "aceptada" if not mot else "no_aceptada", "motivos": mot}}


# ================================================================================================ F08-TECHOS: recuperación de T1 y certificado
def recuperar(salida: Path, t1=GUARDADO) -> dict:
    """fam08-recuperar (caso no alcanzado; sin búsqueda de techos): (1) recuperar_t1.recuperar sobre los bytes de T1 (guardada o nueva):
    17 techos cerrados validados y la clave d59edf8a9d1461d1 pendiente, no decidida, sin promoción; (2) certificado_salto.main (el
    certificador aceptado, comprobación aritmética por intervalos) REEMITE el certificado sobre la fila de T1; (3) la recuperación con el
    certificado guardado y con el reemitido; (4) pruebas_certificado.py (contrastes S1–S7, control positivo S7). T1 sigue incompleta."""
    T0 = time.time()
    rastro = F1().Rastro()
    malos = fuentes_alteradas("regeneracion", [rel(guardada(T1))] if str(t1) == GUARDADO else [])
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam08.json; no se recupera): %s" % malos[:5])
    M = preparar()
    RT, CS = M["recuperar_t1"], M["certificado_salto"]
    raw_e, _ = manifiesto_enf()
    pin = pines()[T1]
    if str(t1) == GUARDADO:
        D = guardada(T1)
        pr, pa = pin["resultado_sha256"], pin["alcance_origen_sha256"]
        proc = {"procedencia": "guardada", "carpeta": rel(D), "naturaleza": "T1 histórica rem127 (bytes guardados; incompleta; no se recalcula)"}
    else:
        D = Path(t1).resolve()
        ej = leer(D / "ejecucion.json") if (D / "ejecucion.json").is_file() else {}
        need(ej.get("etiqueta") == ETIQUETA and ej.get("tarea") == T1, "CARPETA_SIN_EJECUCION_FAM08_DE_T1")
        pr, pa = sha_archivo(D / "resultado.json"), sha_archivo(DATOS / DECLARACION)
        proc = {"procedencia": "nueva", "carpeta": rel(D), "naturaleza": "T1 de fam08-unidad (cálculo nuevo; pines = sus bytes y la declaración)"}
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    sal = salida.resolve()
    (sal / "certificado").mkdir()
    (sal / "pruebas").mkdir()
    kw = {"pin_resultado": pr, "pin_alcance": pa, "lenf": ENF / "techos", "manifiesto": DATOS / MAN_ENF[0]}

    def resumen(o, sel):
        pend = o.get("pendientes") or {}
        return {"aceptada": o.get("aceptada"), "dictamen": o.get("dictamen"), "fallos": o.get("fallos"), "resultado_sha256": o.get("resultado_sha256"),
                "productos_sha256": o.get("productos_sha256"), "alcance_sha256": o.get("alcance_sha256"), "reutilizables": o.get("reutilizables"),
                "pendientes": {k: {c: v.get(c) for c in ("estado_persistido", "motivo", "attained", "lower_R", "upper_R", "C_2", "error_normalizado",
                                                         "comparaciones", "estado_recuperacion", "certificado", "testigo_lateral")} for k, v in pend.items()},
                "lineas": {k: {"filas": len(v), "sha256": sha(b"".join(x + b"\n" for x in v))} for k, v in (sel or {}).items()}}
    a0 = time.time()
    o1, s1 = RT.recuperar(BASE, D, None, **kw)
    sin_cert = resumen(o1, s1)
    techos_p = D / "salida" / PRODUCTOS[0]
    cert_p = sal / "certificado" / CERT[0]
    buf, rc_c, exc_c = io.StringIO(), None, None
    ruta = list(sys.path)
    try:
        with contextlib.redirect_stdout(buf):
            rc_c = CS.main(BASE, DATOS / MAN_ENF[0], techos_p, sha_archivo(techos_p), CLAVE_NA, cert_p)
    except Exception:  # noqa: BLE001
        exc_c = _sin_base(traceback.format_exc())
    finally:
        sys.path[:] = ruta
    (sal / "certificado_stdout.txt").write_text(buf.getvalue(), encoding="utf-8")
    con = {}
    for nombre, cp in (("guardado", DATOS / CERT[0]), ("reemitido", cert_p)):
        if cp.is_file():
            o, s = RT.recuperar(BASE, D, cp, cert_mod=CS, **kw)
            con[nombre] = resumen(o, s)
    rc_p, ult_p, out_p, exc_p = guion("integracion/pruebas_certificado.py", [BASE, sal / "pruebas" / "PRUEBAS_CERTIFICADO.json"], {"RUTAS_FUENTES": RUTAS_FUENTES})
    (sal / "pruebas_stdout.txt").write_text(out_p, encoding="utf-8")
    try:
        ult_p = json.loads(out_p)                   # las pruebas escriben un único JSON con sangría
    except ValueError:
        pass
    t_r = round(time.time() - a0, 2)
    informe = rastro.informe()
    (sal / "archivos_leidos.json").write_bytes((json.dumps(informe, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    co = manifiesto_enf()[1]["ABL-ENF"]
    celdas_na = sum(1 for c in M["validar_coord_rec"].celdas_del_lote(BASE, co)[0] or [] if c["clave_transformada_sha256"] == CLAVE_NA)
    doc = {"comando": "fam08-recuperar", "operacion": "F08-TECHOS (caso no alcanzado)", "etiqueta": ETIQUETA, "t1_entrada": proc,
           "t1": dict(sin_cert, origen=rel(D)), "con_certificado": con,
           "certificado_reemitido": {"archivo": rel(cert_p), "sha256": sha_archivo(cert_p), "rc": rc_c, "excepcion": exc_c,
                                     "certificador": {"archivo": "nucleo_s6/enf/integracion/certificado_salto.py", "sha256": CODIGO["integracion/certificado_salto.py"],
                                                      "adaptacion": [x[0] for x in SUSTITUCIONES["integracion/certificado_salto.py"]]}},
           "pruebas": {"archivo": rel(sal / "pruebas" / "PRUEBAS_CERTIFICADO.json"), "sha256": sha_archivo(sal / "pruebas" / "PRUEBAS_CERTIFICADO.json"),
                       "rc": rc_p, "veredicto": ult_p, "excepcion": exc_p},
           "separados": {"certificado": "supremo lateral NO alcanzado de la clave exacta (sin argmax; tau_*_at_sup = null)",
                         "punto_factible": "fila persistida de T1 (lower_R / C_2 / testigo): cota inferior, NO maximizador",
                         "recuperacion": "17 techos cerrados de T1 validados (validar_techos común), sin cambiar su estado incompleta",
                         "celdas_afectadas_en_el_censo": celdas_na},
           "naturaleza": ("recuperación y certificado sobre la T1 %s; el certificador se ejecuta (comprobación aritmética existente); "
                          "ningún techo ni búsqueda nueva") % proc["procedencia"],
           "tiempos_s": {"recuperacion_y_certificado": t_r, "total": round(time.time() - T0, 2)},
           "lecturas": lecturas(informe, ("referencias/fam08/rem128/diagnostico/", "referencias/fam08/rem128/REM128_DIAG"))}
    rg = con.get("reemitido") or {}
    doc["exito"] = (o1.get("aceptada") is True and rc_c == 0 and exc_c is None and rc_p == 0 and exc_p is None
                    and ((rg.get("pendientes") or {}).get(CLAVE_NA) or {}).get("estado_recuperacion") == "no_alcanzado_demostrado"
                    and not doc["lecturas"]["referencia_esperada_leida"])
    _escribir(sal / "RECUPERACION_T1.json", doc)
    return doc


def comparar_recuperacion(nueva: Path) -> dict:
    """fam08-comparar --tarea RECUPERACION: certificado reemitido frente a la proyección del aceptado (cc1aa49a…; ubicación de su fuente
    aparte), recuperación frente al libro rem129 (17 techos, 1.294 comparaciones) y al manifiesto integral, y contrastes frente a rem128."""
    nueva = Path(nueva).resolve()
    mot = []
    r = leer(nueva / "RECUPERACION_T1.json") if (nueva / "RECUPERACION_T1.json").is_file() else {}
    if r.get("comando") != "fam08-recuperar" or r.get("etiqueta") != ETIQUETA:
        mot.append("SALIDA_SIN_EJECUCION_DE_FAM08_RECUPERAR")
    t = r.get("t1") or {}
    nueva_t1 = (r.get("t1_entrada") or {}).get("procedencia") == "nueva"
    pin = pines()[T1]
    lb = (fuentes().get("libros") or {}).get("rem129") or {}
    rec = lb.get("recuperacion_T1") or {}
    p = (t.get("pendientes") or {}).get(CLAVE_NA) or {}
    hechos = {"aceptada": t.get("aceptada") is True and t.get("dictamen") == "recuperacion_parcial_validada",
              "17_techos_reutilizables": (t.get("reutilizables") or {}).get("techos") == rec.get("roofs") == 17,
              "comparaciones_reutilizables": (t.get("reutilizables") or {}).get("comparaciones") == rec.get("comparisons"),
              "una_pendiente_exacta": sorted(t.get("pendientes") or {}) == [CLAVE_NA],
              "pendiente_no_decidida_sin_certificado": p.get("estado_recuperacion") == "no_decidido" and p.get("estado_persistido") == "incomplete"
                                                      and p.get("motivo") == MOTIVO_NA and p.get("attained") is False,
              "huellas_de_T1": nueva_t1 or (t.get("resultado_sha256") == pin["resultado_sha256"] and t.get("productos_sha256") == pin["productos"]),
              "celdas_afectadas_144": (r.get("separados") or {}).get("celdas_afectadas_en_el_censo") == 144}
    for nombre in ("guardado", "reemitido"):
        c = ((r.get("con_certificado") or {}).get(nombre) or {})
        pc = (c.get("pendientes") or {}).get(CLAVE_NA) or {}
        if nueva_t1 and nombre == "guardado":       # el certificado guardado está ligado a los bytes históricos de T1: sobre una T1 nueva no decide
            hechos["con_certificado_guardado (ligado a la T1 histórica; sobre la T1 nueva): no_decidido, fuente no auténtica, sin pasar a complete"] = (
                pc.get("estado_recuperacion") == "no_decidido" and pc.get("estado_persistido") == "incomplete"
                and (pc.get("certificado") or {}).get("fuente_autentica") is False and c.get("reutilizables") == t.get("reutilizables"))
            continue
        hechos["con_certificado_%s: no_alcanzado_demostrado, sin pasar a complete" % nombre] = (
            pc.get("estado_recuperacion") == "no_alcanzado_demostrado" and pc.get("estado_persistido") == "incomplete"
            and (pc.get("certificado") or {}).get("recalculado_coincide") is True and (pc.get("certificado") or {}).get("fuente_autentica") is True
            and c.get("reutilizables") == t.get("reutilizables"))
    for k, v in hechos.items():
        if not v:
            mot.append("RECUPERACION_DISTINTA: %s" % k)
    cp = BASE / ((r.get("certificado_reemitido") or {}).get("archivo") or "<ausente>")
    cn = leer(cp) if cp.is_file() else {}
    cpr = DATOS / CERT[0]
    if sha_archivo(cpr) != CERT[1]:
        mot.append("REFERENCIA_ALTERADA_O_AJENA: certificado")
    cref = leer(cpr)
    vinc = {"/fuente_techo/sha256": (t.get("productos_sha256", {}).get(PRODUCTOS[0]), pin["productos"][PRODUCTOS[0]])} if nueva_t1 else {}
    doc = _comparar_doc(cn, cref, ubic=(r"/fuente_techo/ruta",), vinc=vinc)
    if doc["discretas"] or doc["numericas"] or not doc["vinculos_completos"]:
        mot.append("CERTIFICADO_DISTINTO: %s" % [x["puntero"] for x in (doc["discretas"] + doc["numericas"])[:4]])
    derivada = None
    if cn:
        d2 = json.loads(json.dumps(cn))
        d2["fuente_techo"]["ruta"] = cref["fuente_techo"]["ruta"]
        if nueva_t1:
            d2["fuente_techo"]["sha256"] = cref["fuente_techo"]["sha256"]
        fin = "\r\n" if b"\r\n" in cp.read_bytes() else "\n"       # como el certificador: modo texto, fin de línea de los bytes nuevos
        b = (json.dumps(d2, ensure_ascii=False, indent=1) + "\n").replace("\n", fin).encode("utf-8")
        derivada = {"campos_repuestos": ["fuente_techo/ruta"] + (["fuente_techo/sha256"] if nueva_t1 else []), "sha256": sha(b),
                    "fin_de_linea": "CRLF" if fin == "\r\n" else "LF",
                    "proyeccion_sha256": sha_archivo(cpr), "igual_a_la_proyeccion": b == cpr.read_bytes(), "original_sha256": CERT[2]}
        if not derivada["igual_a_la_proyeccion"]:
            mot.append("HUELLA_DERIVADA_DISTINTA: certificado")
    est = ((cn.get("certificado") or {}).get("estado"), (cn.get("certificado") or {}).get("motivo"))
    sch = json.loads((REF / "rem128/REM128_DIAG_CERTIFICADO_I2.txt").read_text(encoding="utf-8"))
    so = json.loads((nueva / "certificado_stdout.txt").read_text(encoding="utf-8")) if (nueva / "certificado_stdout.txt").is_file() else {}
    if so != sch:
        mot.append("SALIDA_DEL_CERTIFICADOR_DISTINTA_DE_LA_HISTORICA")
    pp = BASE / ((r.get("pruebas") or {}).get("archivo") or "<ausente>")
    pref = REF_DIAG / "PRUEBAS_CERTIFICADO_REM128.json"
    if sha_archivo(pref) != ACEPTADO["pruebas"]["PRUEBAS_CERTIFICADO_REM128.json"]:
        mot.append("REFERENCIA_ALTERADA_O_AJENA: pruebas")
    pruebas_igual = pp.is_file() and pp.read_bytes() == pref.read_bytes()
    if not pruebas_igual:
        mot.append("CONTRASTES_DEL_CERTIFICADOR_DISTINTOS")
    sp = json.loads((nueva / "pruebas_stdout.txt").read_text(encoding="utf-8")) if (nueva / "pruebas_stdout.txt").is_file() else {}
    if sp != json.loads((REF / "rem128/REM128_DIAG_CONTRASTES.txt").read_text(encoding="utf-8")):
        mot.append("SALIDA_DE_LOS_CONTRASTES_DISTINTA_DE_LA_HISTORICA")
    pv = leer(pp) if pp.is_file() else {}
    return {"comando": "fam08-comparar", "tarea": RECUPERACION, "operacion": "F08-TECHOS (caso no alcanzado)", "regla": "COMPARACION-FAM08-v1 (src/fam08.py)",
            "t1_entrada": r.get("t1_entrada"), "nueva": rel(nueva), "hechos_de_la_recuperacion": hechos,
            "certificado": {"estado": est, "comparacion_con_la_proyeccion": doc, "huella_derivada": derivada, "salida_del_certificador_igual": so == sch},
            "contrastes": {"aprobadas": pv.get("aprobadas"), "total": pv.get("total"), "control_positivo_S7": next((c for c in pv.get("casos") or [] if c["caso"] == "S7_clave_real"), None),
                           "bytes_identicos_a_rem128": pruebas_igual},
            "estado": {"reproduccion": "aceptada" if not mot else "no_aceptada", "motivos": mot}}


# ================================================================================================ F08-INTEGRAL
def integrar(salida: Path, entradas: dict) -> dict:
    """fam08-integrar: ensamblar_integracion.py y conciliar_integracion.py --techos (ruta única validar_integracion.validar_fuentes; PUERTA-v1,
    PAQUETE-v1, ENTRADAS-v1, ENTRADAS-MALLAS-v1) con una entrada declarada por tarea, las mallas y, opcionalmente, un certificado
    reemitido. Escribe en la carpeta NUEVA `salida`: ensamblado/, conciliacion/, sus stdout, ejecucion.json y archivos_leidos.json. Nunca
    lee la integración de referencia; una entrada faltante no se sustituye (la validación la rechaza)."""
    T0 = time.time()
    rastro = F1().Rastro()
    usadas = [rel(guardada(t)) for t in TAREAS if str(entradas.get(t)) == GUARDADO] + ([rel(MALLAS_GUARDADA)] if str(entradas.get("mallas")) == GUARDADO else [])
    malos = fuentes_alteradas("regeneracion", usadas)
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam08.json; no se integra): %s" % malos[:5])
    need(set(entradas) <= set(TAREAS) | {"mallas", "pilotos", "certificado"}, "ENTRADA_NO_DECLARABLE: %s" % sorted(set(entradas) - set(TAREAS) - {"mallas", "pilotos", "certificado"}))
    hdec, _ = declaracion()
    M = preparar()
    dirs, pins, origen = entradas_techos(entradas)
    ent_m, proc_m = entradas_mallas(entradas.get("mallas"), entradas.get("pilotos") or ())
    ent = dict(ent_m, dirs=dirs, pins=pins)
    cert = entradas.get("certificado")
    if cert is not None:
        cp = Path(cert).resolve()
        need(cp.is_file(), "CERTIFICADO_DECLARADO_AUSENTE")
        ent["resolucion"] = {"certificado": {"ruta": rel(cp), "sha256": sha_archivo(cp)}}
        proc_c = {"procedencia": "nuevo", "archivo": rel(cp), "sha256": sha_archivo(cp), "naturaleza": "certificado reemitido por fam08-recuperar"}
    else:
        proc_c = {"procedencia": "guardado", "archivo": "datos/fam08/" + CERT[0], "sha256": CERT[1], "original_sha256": CERT[2],
                  "naturaleza": "certificado aceptado (proyección saneada; SANEADO-v1)"}
    M["validar_integracion"].ENTRADAS = ent
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    sal = salida.resolve()
    extra = {"RUTAS_FUENTES": RUTAS_FUENTES, "ENTRADAS": ent, "VALIDADOR_ELAST": validador_elast}
    pu = ["--modo", "produccion", "--alcance", DATOS / DECLARACION]
    a0 = time.time()
    rc_e, ult_e, out_e, exc_e = guion("integracion/ensamblar_integracion.py", [BASE, DATOS / MI_ENF[0], sal / "ensamblado"] + pu, extra)
    t_e = round(time.time() - a0, 2)
    a0 = time.time()
    rc_c, ult_c, out_c, exc_c = guion("integracion/conciliar_integracion.py", [BASE, DATOS / MI_ENF[0], sal / "conciliacion"] + pu + ["--techos"], extra)
    t_c = round(time.time() - a0, 2)
    M["validar_integracion"].ENTRADAS = {"dirs": {}, "pins": {}}
    (sal / "ensamblado_stdout.txt").write_text(out_e, encoding="utf-8")
    (sal / "conciliacion_stdout.txt").write_text(out_c, encoding="utf-8")
    informe = rastro.informe()
    (sal / "archivos_leidos.json").write_bytes((json.dumps(informe, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    procs = {o["procedencia"] for o in origen.values()} | {{"guardada": "guardada", "nueva": "nueva", "mixta": "mixta"}[proc_m["procedencia"]]}
    procs |= {"guardada" if proc_c["procedencia"] == "guardado" else "nueva"}
    nat = _naturaleza({"nueva" if x == "mixta" else x for x in procs} | ({"guardada"} if "mixta" in procs else set()))
    ej = {"comando": "fam08-integrar", "operacion": "F08-INTEGRAL (y techos_pares de F08-TECHOS)", "etiqueta": ETIQUETA, "naturaleza": nat,
          "entradas": {"tareas": origen, "mallas": proc_m, "certificado": proc_c},
          "acredita": {REGENERACION: "el ensamblado y la conciliación integrales sobre entradas guardadas; NO acredita F08-MALLAS ni F08-TECHOS",
                       MIXTA: "la conexión de las salidas nuevas a la integración; las entradas guardadas NO se han calculado aquí",
                       NUEVA: "la integración sobre salidas calculadas en la base limpia"}.get(nat, "nada (integración incompleta)"),
          "declaracion_sha256": hdec,
          "piezas": {n: {"sha256": CODIGO[n], "adaptacion": [x[0] for x in SUSTITUCIONES.get(n, ())]} for n in CODIGO if n.startswith("integracion/")},
          "ensamblado": {"rc": rc_e, "veredicto": ult_e, "excepcion": exc_e, "productos": {n: sha_archivo(sal / "ensamblado" / n) for n in PRODUCTOS_ENS + ("ENSAMBLADO_INTEGRAL.json",)}},
          "conciliacion": {"rc": rc_c, "veredicto": ult_c, "excepcion": exc_c,
                           "productos": {n: sha_archivo(sal / "conciliacion" / n) for n in PRODUCTOS_CONC + ("pares_puntos.jsonl", "CONCILIACION_INTEGRAL_ENF.json")}},
          "tiempos_s": {"ensamblado": t_e, "conciliacion": t_c, "total": round(time.time() - T0, 2)},
          "lecturas": lecturas(informe, ("referencias/fam08/rem131/", "referencias/fam08/rem128/conciliacion_mallas/"))}
    ej["exito"] = (rc_e == 0 and rc_c == 0 and exc_e is None and exc_c is None and ult_e.get("aceptada") is True and ult_c.get("aceptada") is True
                   and not ej["lecturas"]["referencia_esperada_leida"])
    _escribir(sal / "ejecucion.json", ej)
    return ej


def recuentos_integral(E: Path, censo: dict) -> dict:
    """Recuentos obtenidos de los PRODUCTOS de una integración (nueva o de referencia; los mismos cálculos para ambas)."""
    tec = leer_jsonl(E / "enf_techos_integrados.jsonl") if (E / "enf_techos_integrados.jsonl").is_file() else []
    integ = leer_jsonl(E / "enf_comparacion_integral.jsonl") if (E / "enf_comparacion_integral.jsonl").is_file() else []
    base = leer_jsonl(E / "enf_comparacion_ensamblada.jsonl") if (E / "enf_comparacion_ensamblada.jsonl").is_file() else []
    res = [x for x in integ if x.get("origen_G") == "resolucion_no_alcanzado_demostrado"]
    pais = lambda xs: dict(sorted(Counter((censo.get((x["unidad"], x["cell_id"])) or {}).get("pais") for x in xs).items(), key=str))  # noqa: E731
    na = [x for x in tec if x["clave_transformada_sha256"] == CLAVE_NA]
    fila_na = (na[0] if na else {}).get("fila_historica") or {}
    rs = (na[0] if na else {}).get("resolucion") or {}
    esq = rs.get("esquema_supremo_no_alcanzado") or {}
    return {"claves": len(tec), "claves_unicas": len({x["clave_transformada_sha256"] for x in tec}), "por_origen": dict(Counter(x["origen"] for x in tec)),
            "celdas": len(integ), "celdas_unicas": len({(x["unidad"], x["cell_id"]) for x in integ}), "por_pais": pais(integ),
            "por_menu": dict(Counter((censo.get((x["unidad"], x["cell_id"])) or {}).get("j") for x in integ)),
            "celdas_resueltas": len(res), "resueltas_por_pais": pais(res), "claves_resueltas": sorted({x["clave_transformada_sha256"] for x in res}),
            "G_enf_negativo": sum(1 for x in integ if x["G_enf"] < 0), "G_padre_negativo": sum(1 for x in integ if x["G_padre"] < 0),
            "cambios_de_signo_G": sum(1 for x in integ if (x["G_enf"] < 0) != (x["G_padre"] < 0)),
            "dG_min": min((x["dG"] for x in integ), default=None), "dG_max": max((x["dG"] for x in integ), default=None),
            "caso_no_alcanzado": {"T1_historica_incompleta": fila_na.get("estado") == "incomplete" and fila_na.get("motivo") == MOTIVO_NA and fila_na.get("attained") is False,
                                  "resolucion": rs.get("resolucion"), "sin_argmax": esq.get("tau_d_at_sup") is None and esq.get("tau_f_at_sup") is None
                                  and esq.get("sup_not_attained") is True,
                                  "punto_factible_no_maximizador": "NO es un maximizador" in str((rs.get("cota_inferior_historica") or {}).get("nota")),
                                  "certificado_recalculado_identico": (rs.get("certificado") or {}).get("recalculado_identico") is True,
                                  "celdas_ensambladas_sin_G": sum(1 for x in base if x["clave_transformada_sha256"] == CLAVE_NA and x.get("G_coord") is None
                                                                  and x.get("estado_techo") == "incomplete"),
                                  "otras_claves_sin_G": sum(1 for x in base if x["clave_transformada_sha256"] != CLAVE_NA and x.get("G_coord") is None)}}


def comparar_integral(nueva: Path) -> dict:
    """fam08-comparar --tarea INTEGRAL: salida de fam08-integrar frente a la integración aceptada rem131 (productos del catálogo y las dos
    proyecciones), todas las filas, recuentos obtenidos de los productos (de la nueva y de la referencia) y los veredictos."""
    nueva = Path(nueva).resolve()
    mot = []
    ej = leer(nueva / "ejecucion.json") if (nueva / "ejecucion.json").is_file() else {}
    if ej.get("comando") != "fam08-integrar" or ej.get("etiqueta") != ETIQUETA:
        mot.append("SALIDA_SIN_EJECUCION_DE_FAM08_INTEGRAR")
    if {n: sha_archivo(REF_ENS / n) for n in ACEPTADO["ensamblado"]} != ACEPTADO["ensamblado"] \
            or {n: sha_archivo(REF_CONC / n) for n in ACEPTADO["conciliacion"]} != ACEPTADO["conciliacion"]:
        mot.append("REFERENCIA_ALTERADA_O_AJENA: integración rem131")
    E, C = nueva / "ensamblado", nueva / "conciliacion"
    ens = leer(E / "ENSAMBLADO_INTEGRAL.json") if (E / "ENSAMBLADO_INTEGRAL.json").is_file() else {}
    conc = leer(C / "CONCILIACION_INTEGRAL_ENF.json") if (C / "CONCILIACION_INTEGRAL_ENF.json").is_file() else {}
    if not (ens.get("aceptada") is True and ens.get("dictamen") == "completa_validada_con_resolucion"):
        mot.append("ENSAMBLADO_NO_ACEPTADO: %s" % (ens.get("fallos") or [])[:3])
    if not (conc.get("aceptada") is True and conc.get("dictamen") == "integral_validada"):
        mot.append("CONCILIACION_NO_ACEPTADA: %s" % (conc.get("fallos") or [])[:3])
    en = ej.get("entradas") or {}
    nuevas = [t for t, o in (en.get("tareas") or {}).items() if o.get("procedencia") == "nueva"]
    mallas_nueva = (en.get("mallas") or {}).get("procedencia") == "nueva"
    cert_nuevo = (en.get("certificado") or {}).get("procedencia") == "nuevo"
    pin, m = pines(), mi()
    co = manifiesto_enf()[1]["ABL-ENF"]
    hdec = sha_archivo(DATOS / DECLARACION)
    vin_doc, ubic = {}, [r"/(techos/)?origen/(%s)/directorio" % "|".join(map(re.escape, nuevas))] if nuevas else []
    vin_fila = {}
    for t in nuevas:
        d = BASE / en["tareas"][t]["carpeta"]
        rs = leer(d / "resultado.json")
        prods = {n: sha_archivo(d / "salida" / n) for n in PRODUCTOS}
        for pref in ("/origen/%s" % t, "/techos/origen/%s" % t):
            vin_doc[pref + "/resultado_sha256"] = (sha_archivo(d / "resultado.json"), pin[t]["resultado_sha256"])
            vin_doc[pref + "/alcance_origen_sha256"] = (rs.get("alcance_sha256"), pin[t]["alcance_origen_sha256"])
            for n in PRODUCTOS:
                vin_doc[pref + "/productos/" + n] = (prods[n], pin[t]["productos"][n])
        for k in co["tareas"][t]:
            vin_fila[(k,)] = {"/alcance_origen_sha256": (hdec, ALC_ENF[1]), "/fila_historica/alcance_sha256": (hdec, ALC_ENF[1]),
                              "/resultado_origen_sha256": (sha_archivo(d / "resultado.json"), pin[t]["resultado_sha256"]),
                              "/producto_origen_sha256": (prods[PRODUCTOS[0]], pin[t]["productos"][PRODUCTOS[0]])}
    if cert_nuevo:
        ubic += [r"/(techos/)?resoluciones/%s/certificado/ruta" % CLAVE_NA]
        for pref in ("/resoluciones/%s/certificado/sha256" % CLAVE_NA, "/techos/resoluciones/%s/certificado/sha256" % CLAVE_NA):
            vin_doc[pref] = (en["certificado"]["sha256"], CERT[2])
        vin_fila.setdefault((CLAVE_NA,), {})["/resolucion/certificado/sha256"] = (en["certificado"]["sha256"], CERT[2])
    if mallas_nueva:
        dm = BASE / en["mallas"]["carpeta"]
        vin_doc["/producto_mallas_sha256"] = (sha_archivo(dm / "salida/frontier_result.jsonl"), m["mallas"]["producto_sha256"])
        vin_doc["/resultado_mallas_sha256"] = (sha_archivo(dm / "resultado.json"), m["mallas"]["resultado_sha256"])
    cambia_tec = bool(nuevas or cert_nuevo)
    if cambia_tec:
        vin_doc["/productos/enf_techos_integrados.jsonl/sha256"] = (sha_archivo(E / "enf_techos_integrados.jsonl"), ACEPTADO["ensamblado"]["enf_techos_integrados.jsonl"])
    if cert_nuevo:
        for n in ("enf_brechas_resueltas.jsonl", "enf_comparacion_integral.jsonl"):
            vin_doc["/productos/%s/sha256" % n] = (sha_archivo(E / n), ACEPTADO["ensamblado"][n])
        vin_doc["/productos_integrales/brechas_celdas.jsonl"] = (sha_archivo(C / "brechas_celdas.jsonl"), ACEPTADO["conciliacion"]["brechas_celdas.jsonl"])
    puerta = (r"/puerta/alcance_sha256", r"/decision(/.*)?")
    objetos = {}
    for carpeta, R_, nombres in (("ensamblado", REF_ENS, PRODUCTOS_ENS), ("conciliacion", REF_CONC, PRODUCTOS_CONC + ("pares_puntos.jsonl",))):
        for n in nombres:
            rp = R_ / n if n != "pares_puntos.jsonl" else REF_PARES / n
            clave = ("clave_transformada_sha256",) if n == "enf_techos_integrados.jsonl" else ("par_id",) if n == "techos_pares.jsonl" \
                else ("par_id", "tau_d", "tau_f", "side") if n == "pares_puntos.jsonl" else ("unidad", "cell_id")
            oper, vinc = (), None
            if n == "enf_techos_integrados.jsonl" and cambia_tec:
                oper = ("/fila_historica/segundos",) + (("/resolucion/certificado/ruta",) if cert_nuevo else ())
                vinc = vin_fila
            elif n in ("enf_brechas_resueltas.jsonl", "enf_comparacion_integral.jsonl", "brechas_celdas.jsonl") and cert_nuevo:
                vinc = {(x["unidad"], x["cell_id"]): {"/certificado_sha256": (en["certificado"]["sha256"], CERT[2])}
                        for x in leer_jsonl(rp) if x.get("certificado_sha256")}
            o = F7.comparar_filas(_lineas((E if carpeta == "ensamblado" else C) / n), _lineas(rp), clave, oper, vinc)
            exactos = vinc is None and not oper
            _motivos_filas(o, n, mot, bytes_exactos=exactos)
            if not exactos:
                guard = set() if n != "enf_techos_integrados.jsonl" else {(x["clave_transformada_sha256"],) for x in map(json.loads, _lineas(rp)) if (x["clave_transformada_sha256"],) not in vin_fila}
                o["operativos_de_entradas_guardadas_distintos"] = [x for x in o["operativos"] if tuple(x["fila"]) in guard and x["nueva"] != x["referencia"]]
                if o["operativos_de_entradas_guardadas_distintos"]:
                    mot.append("OPERATIVO_DISTINTO_EN_ENTRADA_GUARDADA: %s" % n)
                v = o["vinculo"] or {}
                esperados = sum(len(x) for x in vinc.values()) if vinc else 0
                if v.get("filas") != esperados or v.get("nueva_ligada") != esperados or v.get("referencia_ligada") != esperados:
                    mot.append("VINCULO_ROTO: %s" % n)
                o["huella_derivada"] = _huella_filas((E if carpeta == "ensamblado" else C) / n, rp, clave, [p for p in oper] + sorted({p for x in (vinc or {}).values() for p in x}))
                if not o["huella_derivada"]["igual"] and not o["n_discretas"] and not o["n_numericas"]:
                    mot.append("HUELLA_DERIVADA_DISTINTA: %s" % n)
            objetos["%s/%s" % (carpeta, n)] = o
    docs = {}
    for nombre, nd, rd in (("ENSAMBLADO_INTEGRAL.json", ens, leer(REF_ENS / "ENSAMBLADO_INTEGRAL.json")),
                           ("CONCILIACION_INTEGRAL_ENF.json", conc, leer(REF_CONC / "CONCILIACION_INTEGRAL_ENF.json"))):
        vd = {p: v for p, v in vin_doc.items() if p in F5.hojas(nd) or p in F5.hojas(rd)}
        d = _comparar_doc(nd, rd, ubic=tuple(ubic) + (r"/validador_elast/ruta",), puerta=puerta, vinc=vd)
        if d["discretas"] or d["numericas"] or not d["vinculos_completos"]:
            mot.append("DOCUMENTO_DISTINTO: %s %s" % (nombre, [x["puntero"] for x in (d["discretas"] + d["numericas"])[:4]]))
        if nd.get("puerta", {}).get("alcance_sha256") != hdec or (nd.get("decision") is not None):
            mot.append("PUERTA_DISTINTA_DE_PUERTA-v1: %s" % nombre)
        docs[nombre] = d
    for n in PRODUCTOS_ENS:
        if (ens.get("productos") or {}).get(n, {}).get("sha256") != sha_archivo(E / n):
            mot.append("HUELLA_DERIVADA_DISTINTA_DE_SUS_BYTES: ENSAMBLADO_INTEGRAL.json/productos/%s" % n)
    for n in PRODUCTOS_CONC:
        if (conc.get("productos_integrales") or {}).get(n) != sha_archivo(C / n):
            mot.append("HUELLA_DERIVADA_DISTINTA_DE_SUS_BYTES: CONCILIACION_INTEGRAL_ENF.json/productos_integrales/%s" % n)
    VC = preparar()["validar_coord_rec"]
    cel, fuera, err = VC.celdas_del_lote(BASE, co)
    censo = {(c["unidad"], c["cell_id"]): c for c in cel or []}
    rn, rr = recuentos_integral(E, censo), recuentos_integral(REF_ENS, censo)
    if rn != rr:
        mot.append("RECUENTOS_DISTINTOS: %s" % sorted(k for k in rn if rn[k] != rr.get(k)))
    rn["fuera_del_nivel"] = (ens.get("ensamblado") or {}).get("fuera_del_lote")
    if sorted(rn["fuera_del_nivel"] or {}) != sorted(m["universo"]["fuera_del_nivel"]) or any("no NA" not in str(v) for v in (rn["fuera_del_nivel"] or {}).values()):
        mot.append("FUERA_DEL_NIVEL_DISTINTO (COL-2024p: pendiente, no NA)")
    ver = {"ensamblado": _ultima(nueva / "ensamblado_stdout.txt") == json.loads((REF / "rem131/ENF_INTEGRAL_ENSAMBLADO.txt").read_text(encoding="utf-8")),
           "conciliacion": _ultima(nueva / "conciliacion_stdout.txt") == json.loads((REF / "rem131/ENF_INTEGRAL_CONCILIACION.txt").read_text(encoding="utf-8"))}
    if not all(ver.values()):
        mot.append("VEREDICTO_DISTINTO: %s" % [k for k, v in ver.items() if not v])
    return {"comando": "fam08-comparar", "tarea": INTEGRAL, "operacion": "F08-INTEGRAL", "naturaleza": ej.get("naturaleza"), "acredita": ej.get("acredita"),
            "entradas": en, "regla": "COMPARACION-FAM08-v1 (src/fam08.py)",
            "referencia": {"ensamblado": rel(REF_ENS), "conciliacion": rel(REF_CONC), "productos": {k: v for k, v in ACEPTADO.items() if k in ("ensamblado", "conciliacion")},
                           "proyecciones": "ENSAMBLADO_INTEGRAL.json (original 544b7d77…) y CONCILIACION_INTEGRAL_ENF.json (original 8e97c9b5…)"},
            "nueva": rel(nueva), "objetos": objetos, "documentos": docs, "recuentos": rn, "recuentos_de_la_referencia_iguales": {k: rn[k] == rr[k] for k in rr},
            "veredictos_iguales": ver,
            "bytes_identicos_a_la_referencia": {"ensamblado/" + n: sha_archivo(E / n) == ACEPTADO["ensamblado"][n] for n in PRODUCTOS_ENS}
            | {"conciliacion/" + n: sha_archivo(C / n) == ACEPTADO["conciliacion"][n] for n in PRODUCTOS_CONC},
            "estado": {"reproduccion": "aceptada" if not mot else "no_aceptada", "motivos": mot}}


def _tomar(d, p):
    for k in p.strip("/").split("/"):
        d = d[int(k)] if isinstance(d, list) else d[k]
    return d


def _poner(d, p, v):
    ks = p.strip("/").split("/")
    for k in ks[:-1]:
        d = d[int(k)] if isinstance(d, list) else d[k]
    if isinstance(d, list):
        d[int(ks[-1])] = v
    else:
        d[ks[-1]] = v


def _huella_filas(pn: Path, pr: Path, clave: tuple, punteros: list) -> dict:
    """Filas nuevas con los campos apartados repuestos de su fila de referencia, serializadas como el productor (sort_keys, ensure_ascii=False,
    una por línea); la huella se compara con los BYTES de la referencia."""
    rb = pr.read_bytes()
    dr = {tuple(x.get(k) for k in clave): x for x in (json.loads(y) for y in rb.decode("utf-8").splitlines() if y.strip())}
    filas = []
    for x in leer_jsonl(pn) if pn.is_file() else []:
        r = dr.get(tuple(x.get(k) for k in clave))
        for p in punteros:
            try:
                _poner(x, p, _tomar(r, p))
            except (KeyError, IndexError, TypeError):
                pass
        filas.append(x)
    fin = "\r\n" if pn.is_file() and b"\r\n" in pn.read_bytes() else "\n"      # fin de línea de los bytes nuevos (modo texto del productor)
    der = F7.serie(filas, fin)
    return {"campos_repuestos": punteros, "fin_de_linea": "CRLF" if fin == "\r\n" else "LF", "sha256": sha(der),
            "referencia_sha256_de_sus_bytes": sha(rb), "igual": der == rb}


# ================================================================================================ comprobación (sin cálculo científico)
def comprobar() -> dict:
    """fam08-comprobar: SIN CÁLCULO CIENTÍFICO (ningún techo ni malla; los validadores y la recuperación se aplican a bytes guardados).
    Con una pieza ausente o alterada no cumple y la informa; si esa ausencia impide seguir, registra la interrupción (sin rutas)."""
    r = {"comando": "fam08-comprobar", "calculo": "ninguno"}
    malos = fuentes_alteradas()
    fu = fuentes()
    r["fuentes"] = {"archivos": len(fu["archivos"]), "reutilizados": len(fu["reutilizados"]), "saneados": len(fu.get("saneado") or []),
                    "nucleo_c0_reutilizado": sum(1 for x in piezas() if x["archivo"].startswith("nucleo_s6/c0/")), "ausentes_o_distintos": malos[:20]}
    try:
        return _comprobar(r, malos, fu)
    except Exception as ex:  # noqa: BLE001  (solo con dependencias ausentes o alteradas; si no, el error se propaga)
        if not malos:
            raise
        r["comprobacion_interrumpida"] = {"excepcion": type(ex).__name__, "causa": "pieza ausente o alterada (fuentes.ausentes_o_distintos)"}
        r["cumple"] = False
        return r


def _comprobar(r: dict, malos: list, fu: dict) -> dict:
    raw_m, man_m = manifiesto_mallas()
    raw_e, man_e = manifiesto_enf()
    m = mi()
    co, mm = man_e["ABL-ENF"], man_m["ABL-ENF-MALLAS"]
    txt = {n: (DATOS / n).read_text(encoding="utf-8") for n in INDICES}
    cat = {d["id"]: d["sha256_aceptado"] for d in catalogo_op("F08-INTEGRAL")["datos_configuracion"]}
    pin = pines()
    sane = {x["archivo"]: (x["sha256"], x["sha256_original"]) for x in fu.get("saneado") or []}
    r["procedencia"] = {
        "codigo_en_su_indice": all(CODIGO[n] in txt[next(v for k, v in INDICE_DE.items() if n.startswith(k))] for n in CODIGO if n != "integracion/pruebas_certificado.py"),
        "pruebas_certificado_declarado": next((x["sha256"] for x in fu["archivos"] if x["archivo"].endswith("pruebas_certificado.py")), None) == CODIGO["integracion/pruebas_certificado.py"],
        "indices": {n: sha_archivo(DATOS / n) == h for n, h in INDICES.items()},
        "externas_del_indice_integral": all(h in txt["PAQUETE_INTEGRACION_ENF.json"] for h in (INDICES["PAQUETE_ABL_ENF.json"], INDICES["PAQUETE_MALLAS_ENF.json"], PAQUETE_LOTE1[1])),
        "codigo_del_lote2_en_su_indice": sha_archivo(BASE / PAQUETE_LOTE1[0]) == PAQUETE_LOTE1[1]
                                         and all(F5.CODIGO[n] in (BASE / PAQUETE_LOTE1[0]).read_text(encoding="utf-8") and sha_archivo(F5.LOTE / n) == F5.CODIGO[n]
                                                 for n in F5.CODIGO),
        "manifiestos_iguales_al_catalogo": (cat.get("manifiesto de mallas"), cat.get("manifiesto de techos"), cat.get("índice del paquete integral"),
                                            cat.get("manifiesto integral"), cat.get("documento de no alcance"))
                                           == (MAN_MALLAS[1], MAN_ENF[1], INDICES["PAQUETE_INTEGRACION_ENF.json"], MI_ENF[1], CERT[2]),
        "manifiesto_integral_fija_los_manifiestos": (m["paquete_historico_techos"]["manifiesto"]["sha256"], m["paquete_historico_techos"]["indice"]["sha256"],
                                                     m["mallas"]["manifiesto"]["sha256"], m["mallas"]["cobertura"]["sha256"], m["paquete_historico_techos"]["cobertura"]["sha256"])
                                                    == (MAN_ENF[1], INDICES["PAQUETE_ABL_ENF.json"], MAN_MALLAS[1], COB_MALLAS[1], COB_ENF[1])
                                                    and sha_archivo(DATOS / COB_MALLAS[0]) == COB_MALLAS[1] and sha_archivo(DATOS / COB_ENF[0]) == COB_ENF[1],
        "guardadas_iguales_a_sus_pines": all(sha_archivo(guardada(t) / "resultado.json") == pin[t]["resultado_sha256"]
                                             and all(sha_archivo(guardada(t) / "salida" / n) == pin[t]["productos"][n] for n in PRODUCTOS) for t in TAREAS)
                                         and sha_archivo(MALLAS_GUARDADA / "resultado.json") == m["mallas"]["resultado_sha256"]
                                         and sha_archivo(MALLAS_GUARDADA / "salida/frontier_result.jsonl") == m["mallas"]["producto_sha256"],
        "alcance_de_origen_de_las_tareas": all(pin[t]["alcance_origen_sha256"] == ALC_ENF[1] for t in TAREAS) and sha_archivo(DATOS / ALC_ENF[0]) == ALC_ENF[1]
                                           and sha_archivo(DATOS / ALC_MALLAS[0]) == ALC_MALLAS[1],
        "fuentes_declaradas_y_autenticas": all(RUTAS_FUENTES.get(v["ruta"]) and sha_archivo(BASE / RUTAS_FUENTES[v["ruta"]]) == v["sha256"] for v in mm["fuentes"].values()),
        "proyecciones_con_correspondencia": all(sane.get("datos/fam08/" + n) == (hp, ho) and sha_archivo(DATOS / n) == hp for n, hp, ho in (CERT, CENSO)),
        "certificado_y_censo_ligados": m["resolucion"]["certificado"]["sha256"] == CERT[2] and co["fuente_celdas"]["sha256"] == CENSO[2],
        "no_oficiales": all(x.get(k) is False for x in (man_m, man_e) for k in ("b_official_run_authorized", "freeze_run_authorized", "official_export_authorized")),
        "sustituciones_unicas": sustituciones_ok()}
    try:
        h, _ = declaracion()
        r["procedencia"]["declaracion_de_ejecucion_limpia"] = h == next((x["sha256"] for x in fu["archivos"] if x["archivo"] == "datos/fam08/" + DECLARACION), None)
    except Fam08Error:
        r["procedencia"]["declaracion_de_ejecucion_limpia"] = False
    M = preparar()
    import paper2b
    r["nucleo"] = {"identidad_recalculada": F5.identidad_c0(), "igual": F5.identidad_c0() == F5.C0_IDENTIDAD,
                   "paper2b_cargado_de": rel(Path(paper2b.__file__).parent), "declarado_en": "fuentes_fam05.json (nucleo_c0)"}
    CX = F5.cargar("conexion_coord_cert", ENF / "techos/conexion_coord_cert.py")
    from paper2b import run as RUN
    cfg = RUN.RunConfig()
    model = RUN.provider_for(cfg)
    r["motor"] = {"identidad_de_codigo_igual": CX.identidad_codigo(F5.C0 / "src" / "paper2b") == co["motor"]["codigo"],
                  "configuracion_igual": CX.configuracion(model, cfg.sup) == co["motor"]["configuracion"],
                  "certificado_en_esta_plataforma": getattr(model, "certified", None) is True,
                  "garantia_igual": getattr(model, "garantia", None) == co["motor"].get("garantia", CX.GARANTIA) == CX.GARANTIA}
    # cobertura (desde los manifiestos y el censo autenticado; sin calcular)
    fr_ = man_m["L1-ELAST"]["fronteras"]
    cel, fuera, err = M["validar_coord_rec"].celdas_del_lote(BASE, co)
    cel = cel or []
    cb = {"mallas": len(fr_), "por_rol": dict(Counter(v.get("rol") for v in fr_.values())), "puntos": sum(v["puntos_frontier_n4"] for v in fr_.values()),
          "puntos_totales_del_manifiesto": man_m["L1-ELAST"].get("puntos_totales_frontier_n4"), "pares": len(mm["pares"]),
          "padres_reutilizados": sum(1 for p in mm["pares"] if p["padre"]["modo"] != "evaluar_con_C0"),
          "padres_a_evaluar_con_C0": sum(1 for p in mm["pares"] if p["padre"]["modo"] == "evaluar_con_C0"),
          "puntos_de_pares": sum(len(p["puntos"]) for p in mm["pares"]), "controles_d": sum(1 for p in mm["pares"] if p["control_menu_d"]),
          "claves": len(co["claves_recalculadas"]), "claves_reutilizadas": len(co.get("claves_reutilizadas") or {}),
          "tareas": {t: len(v) for t, v in co["tareas"].items()},
          "celdas_afectadas": len(co["celdas_afectadas"]), "celdas_del_censo": len(cel), "error_del_censo": err,
          "celdas_por_pais": dict(Counter(c["pais"] for c in cel)), "celdas_de_la_clave_no_alcanzada": sum(1 for c in cel if c["clave_transformada_sha256"] == CLAVE_NA),
          "fuera_del_nivel": sorted(fuera or {}), "universo_igual": sorted(m["universo"]["claves"]) == sorted(co["claves_recalculadas"])
                                                                   and m["universo"]["celdas_total"] == len(cel) == len(co["celdas_afectadas"])
                                                                   and sorted(m["universo"]["fuera_del_nivel"]) == sorted(fuera or {})}
    cb["cumple"] = (cb["mallas"] == 29 and cb["por_rol"] == {"ENF": 26, "PADRE_C0": 3} and cb["puntos"] == cb["puntos_totales_del_manifiesto"] == 365
                    and cb["pares"] == 26 and cb["padres_reutilizados"] == 23 and cb["padres_a_evaluar_con_C0"] == 3 and cb["puntos_de_pares"] == 330
                    and cb["controles_d"] == 12 and cb["claves"] == 26 and cb["claves_reutilizadas"] == 0 and sum(cb["tareas"].values()) == 26
                    and cb["tareas"]["ABL-ENF-T1"] == 18 and cb["celdas_del_censo"] == cb["celdas_afectadas"] == 1724 and err is None
                    and cb["celdas_por_pais"] == {"MEX": 190, "COL": 574, "PER": 960} and cb["celdas_de_la_clave_no_alcanzada"] == 144
                    and len(cb["fuera_del_nivel"]) == 2 and all("2024p" in x for x in cb["fuera_del_nivel"]) and cb["universo_igual"])
    r["cobertura"] = cb
    # referencias
    rf = {"pares": {n: sha_archivo(REF_PARES / n) == h for n, h in ACEPTADO["pares"].items()},
          "ensamblado": {n: sha_archivo(REF_ENS / n) == h for n, h in ACEPTADO["ensamblado"].items()},
          "conciliacion": {n: sha_archivo(REF_CONC / n) == h for n, h in ACEPTADO["conciliacion"].items()},
          "pruebas": {n: sha_archivo(REF_DIAG / n) == h for n, h in ACEPTADO["pruebas"].items()},
          "en_el_catalogo": all(h in json.dumps(catalogo_op(op), ensure_ascii=False) for op, hs in (("F08-PARES", ACEPTADO["pares"].values()),
                                                                                                   ("F08-INTEGRAL", [v for k, v in ACEPTADO["ensamblado"].items() if k != "ENSAMBLADO_INTEGRAL.json"]),
                                                                                                   ("F08-TECHOS", [ACEPTADO["conciliacion"]["techos_pares.jsonl"]])) for h in hs)}
    rf["cumple"] = all(v for g in ("pares", "ensamblado", "conciliacion", "pruebas") for v in rf[g].values()) and rf["en_el_catalogo"]
    r["referencias"] = rf
    # revalidación de las entradas guardadas (validadores sobre bytes guardados; sin cálculo)
    rv = {}
    for t in TAREAS[1:]:
        rc, ver, _, exc = guion("techos/validar_lote.py", [BASE, DATOS / MAN_ENF[0], guardada(t) / "resultado.json", guardada(t) / "salida"])
        rv[t] = {"rc": rc, "dictamen": ver.get("dictamen"), "igual_a_la_validacion_historica": ver == json.loads((REF / "rem128" / t / "validacion_stdout.txt").read_text(encoding="utf-8")),
                 "excepcion": exc}
    p = validador_elast(DATOS / MAN_MALLAS[0], MALLAS_GUARDADA / "resultado.json", MALLAS_GUARDADA / "salida", DATOS / COB_MALLAS[0])
    vm = json.loads([x for x in p.stdout.splitlines() if x.strip()][-1]) if p.stdout.strip() else {}
    rv[ELAST] = {"rc": p.returncode, "dictamen": vm.get("dictamen"), "igual_a_la_validacion_historica": vm == json.loads((REF / "rem127/L1-ELAST/validacion_stdout.txt").read_text(encoding="utf-8"))}
    o, s = M["recuperar_t1"].recuperar(BASE, guardada(T1), None, pin_resultado=pin[T1]["resultado_sha256"], pin_alcance=pin[T1]["alcance_origen_sha256"],
                                       lenf=ENF / "techos", manifiesto=DATOS / MAN_ENF[0])
    rv[T1] = {"dictamen": o.get("dictamen"), "reutilizables": o.get("reutilizables"),
              "pendientes": {k: v.get("estado_recuperacion") for k, v in (o.get("pendientes") or {}).items()},
              "conforme": o.get("aceptada") is True and (o.get("reutilizables") or {}).get("techos") == 17
              and {k: v.get("estado_recuperacion") for k, v in (o.get("pendientes") or {}).items()} == {CLAVE_NA: "no_decidido"}}
    r["revalidacion_de_las_guardadas"] = rv
    lb = fu.get("libros") or {}
    l8, l9, l2 = lb.get("rem128") or {}, lb.get("rem129") or {}, lb.get("rem132") or {}
    pares = [("rem128 mallas_nuevas ↔ mallas del manifiesto", l8.get("mallas_nuevas"), cb["mallas"]),
             ("rem128 filas_de_puntos ↔ puntos del manifiesto", l8.get("filas_de_puntos"), cb["puntos"]),
             ("rem128 producto ↔ pines del manifiesto integral", ((l8.get("producto") or {}).get("result_sha256"), (l8.get("producto") or {}).get("product_sha256")),
              (m["mallas"]["resultado_sha256"], m["mallas"]["producto_sha256"])),
             ("rem128 validación ↔ revalidación de las mallas guardadas", (l8.get("producto") or {}).get("validation"), vm),
             ("rem129 pares/puntos/controles d ↔ manifiesto", ((l9.get("conciliacion_mallas") or {}).get("pairs"), (l9.get("conciliacion_mallas") or {}).get("points"),
                                                                (l9.get("conciliacion_mallas") or {}).get("controls_d")), (cb["pares"], cb["puntos_de_pares"], cb["controles_d"])),
             ("rem129 recuperación T1 ↔ revalidación", ((l9.get("recuperacion_T1") or {}).get("roofs"), (l9.get("recuperacion_T1") or {}).get("comparisons")),
              ((o.get("reutilizables") or {}).get("techos"), (o.get("reutilizables") or {}).get("comparaciones"))),
             ("rem129 certificado ↔ manifiesto integral", ((l9.get("certificado") or {}).get("document_sha256"), (l9.get("certificado") or {}).get("key")),
              (m["resolucion"]["certificado"]["sha256"], m["resolucion"]["clave"])),
             ("rem132 productos ↔ referencias", sorted(v for k, v in (l2.get("productos_aceptados") or {}).items() if k.endswith(".jsonl")),
              sorted([ACEPTADO["ensamblado"][n] for n in PRODUCTOS_ENS] + [ACEPTADO["conciliacion"][n] for n in PRODUCTOS_CONC] + [ACEPTADO["pares"]["pares_puntos.jsonl"]])),
             ("rem132 cobertura por origen ↔ 17 + 8 + 1", ((l2.get("cobertura") or {}).get("por_origen")), {"T1_recuperado": 17, "tarea_completa": 8, "resolucion_no_alcanzado": 1}),
             ("rem132 celdas por país ↔ censo", ((l2.get("estadisticas") or {}).get("countries")), cb["celdas_por_pais"]),
             ("rem132 celdas resueltas ↔ celdas de la clave no alcanzada", ((l2.get("recuentos") or {}).get("resolved_cells")), cb["celdas_de_la_clave_no_alcanzada"]),
             ("rem132 excluidos ↔ fuera del nivel", sorted((l2.get("recuentos") or {}).get("excluded") or []),
              sorted(x.replace(".ABL-ENF", "") for x in m["universo"]["fuera_del_nivel"]))]
    r["libros"] = {"presentes": {k: v.get("presente") for k, v in lb.items()}, "solo_extraccion": True,
                   "recuentos": [{"recuento": a, "igual": b == c} for a, b, c in pares], "recuentos_iguales": bool(pares) and all(b == c for _, b, c in pares),
                   "dictamenes_consultados": all((v.get("dictamen") or {}).get("sha256_del_archivo") == (v.get("dictamen") or {}).get("sha256_en_el_libro") is not None
                                                 for v in lb.values())}
    pil = leer(DATOS / "pilotos.json") if (DATOS / "pilotos.json").is_file() else None
    r["pilotos"] = {"fijados": [p.get("unidad") or p["tarea"] for p in (pil or {}).get("pilotos", [])], "iguales_a_la_regla": pil == regla_pilotos(man_m, man_e),
                    "declarados": any(x["archivo"] == "datos/fam08/pilotos.json" for x in fu["archivos"])}
    r["receta"] = {"pasos": len(receta()["pasos"])}
    r["cumple"] = (not malos and all(r["procedencia"].values()) and r["nucleo"]["igual"] and all(r["motor"].values()) and cb["cumple"] and rf["cumple"]
                   and all(v.get("rc") == 0 and v.get("igual_a_la_validacion_historica") for k, v in rv.items() if k != T1) and rv[T1]["conforme"]
                   and r["libros"]["recuentos_iguales"] and r["libros"]["dictamenes_consultados"] and all(r["libros"]["presentes"].values())
                   and r["pilotos"]["iguales_a_la_regla"] and r["pilotos"]["declarados"])
    return r


# ================================================================================================ receta completa (sin ejecutarla)
def receta() -> dict:
    raw_e, man_e = manifiesto_enf()
    co = man_e["ABL-ENF"]
    d = "salidas/fam08/<ejecucion>"
    pasos = [{"paso": "comprobar", "ordenes": ["reproducir.py fam08-comprobar --salida %s/comprobar.json (sin cálculo científico)" % d]},
             {"paso": "mallas", "operacion": "F08-MALLAS", "calculo": "nuevo (29 mallas, 365 filas)",
              "ordenes": ["reproducir.py fam08-unidad --tarea L1-ELAST --salida %s/mallas" % d,
                          "reproducir.py fam08-validar --nueva %s/mallas --salida %s/mallas.validacion.json" % (d, d),
                          "reproducir.py fam08-comparar --tarea L1-ELAST --nueva %s/mallas --validacion %s/mallas.validacion.json --salida %s/mallas.comparacion.json" % (d, d, d)]}]
    for t in TAREAS:
        o = ["reproducir.py fam08-unidad --tarea %s --salida %s/%s" % (t, d, t)]
        if t == T1:
            o += ["reproducir.py fam08-recuperar --entrada %s=%s/%s --salida %s/%s.recuperacion" % (t, d, t, d, t),
                  "reproducir.py fam08-comparar --tarea %s --nueva %s/%s --validacion %s/%s.recuperacion/RECUPERACION_T1.json --salida %s/%s.comparacion.json" % (t, d, t, d, t, d, t),
                  "reproducir.py fam08-comparar --tarea RECUPERACION --nueva %s/%s.recuperacion --salida %s/recuperacion.comparacion.json" % (d, t, d)]
        else:
            o += ["reproducir.py fam08-validar --nueva %s/%s --salida %s/%s.validacion.json" % (d, t, d, t),
                  "reproducir.py fam08-comparar --tarea %s --nueva %s/%s --validacion %s/%s.validacion.json --salida %s/%s.comparacion.json" % (t, d, t, d, t, d, t)]
        pasos.append({"paso": t, "operacion": "F08-TECHOS", "claves": co["tareas"][t], "calculo": "nuevo (%d techos)" % len(co["tareas"][t]),
                      "celdas": sum(1 for c in co["celdas_afectadas"] if c["clave_transformada_sha256"] in co["tareas"][t]),
                      "tratamiento": ("T1 termina incompleta en %s (estado histórico aceptado); la recuperación valida sus 17 techos cerrados y el certificador "
                                      "se REEMITE sobre la fila nueva (misma clave exacta; sin generalizar la regla)" % CLAVE_NA) if t == T1 else None, "ordenes": o})
    ent = " ".join("--entrada %s=%s/%s" % (t, d, t) for t in TAREAS)
    pasos.append({"paso": "pares", "operacion": "F08-PARES", "calculo": "regeneración sobre las mallas nuevas",
                  "ordenes": ["reproducir.py fam08-conciliar --entrada mallas=%s/mallas --salida %s/pares" % (d, d),
                              "reproducir.py fam08-comparar --tarea PARES --nueva %s/pares --salida %s/pares.comparacion.json" % (d, d)]})
    pasos.append({"paso": "integral", "operacion": "F08-INTEGRAL (y techos_pares de F08-TECHOS)", "calculo": "regeneración sobre las salidas nuevas",
                  "ordenes": ["reproducir.py fam08-integrar %s --entrada mallas=%s/mallas --entrada certificado=%s/%s.recuperacion/certificado/%s --salida %s/integral"
                              % (ent, d, d, T1, CERT[0], d),
                              "reproducir.py fam08-comparar --tarea INTEGRAL --nueva %s/integral --salida %s/integral.comparacion.json" % (d, d)]})
    return {"comando": "fam08-receta", "estado": "receta completa preparada; NO ejecutada (el cálculo completo pertenece al Paso 3)",
            "manifiestos": {"mallas": MAN_MALLAS[1], "techos": sha(raw_e), "integracion": MI_ENF[1]},
            "orden": ["mallas"] + list(TAREAS) + ["pares", "integral"], "pasos": pasos,
            "cobertura": {"mallas": 29, "filas_de_puntos": 365, "mallas_padre_reutilizadas": 23, "pares": 26, "techos": len(co["claves_recalculadas"]),
                          "celdas": len(co["celdas_afectadas"]), "clave_no_alcanzada": CLAVE_NA, "fuera_del_nivel": "COL-2024p (pendiente, no NA)"},
            "ejecucion": {"procesos": "un cálculo a la vez, sin reintentos", "tope_trabajo_s": F5.TOPE_TRABAJO, "reloj_interno_s": F5.TOPE_TRABAJO - F5.HOLGURA,
                          "lanzador": "supervisor que termina el árbol de procesos (el mismo de los pilotos), con el tope de trabajo como límite externo",
                          "parada": ("si una tarea no termina en su estado aceptado (T2–T6 completas y validadas; T1 incompleta solo en la clave no "
                                     "alcanzada y recuperada), no se concilia ni se integra"),
                          "integral": "solo con las salidas nuevas; una entrada faltante no se sustituye por su referencia (la validación la rechaza)",
                          "duracion": "sin estimación: los pilotos no la permiten"},
            "F1": {"reutilizado": ["23 mallas padre de sus productos aceptados (lote 2 rem120; autenticadas, origen C0)", "censo de las 1.724 celdas (K1 y G padre fijos)",
                                   "núcleo C0 y código del lote 2", "manifiestos de mallas, techos e integración (la selección no se re-ejecuta)"],
                   "se_genera_de_nuevo": ["29 mallas (L1-ELAST)", "26 techos certificados de T1–T6 y sus comparaciones",
                                          "recuperación de T1 y certificado reemitido sobre la fila nueva", "26 pares/330 puntos", "integración de 26 claves y 1.724 celdas"],
                   "solo_para_comparar": ["salidas aceptadas rem127/rem128 (guardadas) y productos rem128/rem131 (referencias del catálogo)"],
                   "no_cubre": ["COL-2024p (pendiente, no NA)", "FAM09 y siguientes"]},
            "pilotos": leer(DATOS / "pilotos.json") if (DATOS / "pilotos.json").is_file() else None}
