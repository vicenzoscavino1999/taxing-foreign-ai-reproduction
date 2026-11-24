"""FAM07 (COORD del lote 2, variante B): comprobación sin cálculo de entradas, fuentes, reutilizaciones, comparaciones previas y referencias;
cálculo de una tarea de la partición (dos techos certificados y sus comparaciones) por la ruta de tarea_lote.py del paquete COORD con el
núcleo C0; validación por validar_lote.py (validar_coord_rec.validar_tarea); ensamblado de las 1.532 comparaciones con ensamblar_coord.py
sobre tareas nuevas o guardadas; comparación con la ejecución aceptada rem124 y receta completa (sin ejecutarla).

Operaciones del catálogo (no se confunden):
- F07-RECALCULO (RN): los seis techos certificados (claves_recalculadas; partición L1-COORD-R1/R2/R3, dos por tarea) por
  conexion_coord_cert.techo con model = RUN.provider_for(RUN.RunConfig()) (ModeloTeorico, rama y cota con encierros, configuración
  fijada en el manifiesto; frontier.capture_ceiling queda sustituida por una función que falla) y sus 30 comparaciones dependientes
  (16 + 12 + 2), G_coord = C2' − K1 con K1 reutilizado sin cambio. Cierre normalizado <= 1e-7, error en R conservado.
- F07-REUTILIZADAS (VI): 20 techos reutilizados (12 de rem112 y 8 de rem120) autenticados en SU fuente con su garantía original
  convergence_estimate (nunca promovida a certified_bound, aunque su error almacenado sea 0) y las 1.502 comparaciones del ensamblado que
  dependen de ellos (cotejadas con las comparaciones rem120). No cuentan como cálculo nuevo.
- F07-PREVIAS-192 (VI): las 192 comparaciones previas aceptadas (lote 1, rem112), verificadas contra las celdas del lote 1 y los techos
  rem112 y separadas de las 1.532: 1.724 celdas declaradas sin duplicados. COL-2024p queda fuera (pendiente, no NA).

Piezas: fuentes_fam07.json (nucleo_s6/coord: los cinco guiones COORD; datos/fam07: manifiesto B, anexo, índice del paquete, alcance
nativo, fuentes rem120, pilotos y declaración de ejecución limpia; referencias/fam07/rem124) y las reutilizadas de FAM05 (núcleo C0 y
manifiesto del lote 2), FAM04 (techos y 192 comparaciones rem112, manifiesto del lote 1) y FAM01 (filas padre de las 30 celdas afectadas).

Adaptaciones (no cambian fórmulas, claves, tolerancias, presupuestos ni criterios):
- GUION-v1: los cinco archivos se ejecutan desde sus bytes exactos (nucleo_s6/coord, con __file__ en esa carpeta: el código del trabajador
  que registra el resultado y que exige el validador es el de esos bytes) con las sustituciones de SUSTITUCIONES (cada original, una
  sola vez); validar_coord_rec se carga como módulo desde su texto adaptado antes de que lo importen trabajador, validador y ensamblador.
- NUCLEO-C0-v1 (de FAM05): el núcleo es nucleo_s6/c0; aprobacion_alcance.identidad_instalacion se sirve con el módulo mínimo de FAM05.
- RUTAS-FUENTES-v1: leer_autenticado lee cada fuente de su ruta en la base limpia (tabla RUTAS_FUENTES, ruta histórica -> archivo del
  paquete) y la sigue autenticando por sus bytes antes de deserializarla; una ruta no declarada es FUENTE_NO_DECLARADA (sin respaldo).
- RAIZ-v1: R del trabajador = base limpia (solo la usa el modo hasta-seleccion, que aquí no se ejecuta).
- PUERTA-v1: la puerta de producción (alcance v3 verificado + decisión humana nativa) no se ejecuta ni se reconstruye; el campo
  alcance_sha256 que el trabajador escribe tras ella y que el validador exige a un resultado real lleva el sha256 de la declaración
  datos/fam07/ejecucion_limpia.json (NO OFICIAL; no es un alcance ni una decisión). modo = «produccion» es el que exige el validador.
- ENSAMBLADOR-ENTRADAS-v1: el ensamblador recibe una carpeta declarada por tarea (nueva o guardada; sin carpeta, la tarea falta y el
  ensamblado se rechaza: no hay sustitución por referencias), escribe en una carpeta nueva explícita y registra directorio y lanzamiento
  relativos a la base (el original guardaba rutas absolutas).
- RELOJ-PILOTO-v1 (de FAM05): reloj interno = tope de trabajo − holgura del conductor (2400 − 120 = 2280 s, el tope_efectivo_s
  histórico); el límite externo lo pone el supervisor.
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


def _fam05():
    if "fam05" not in sys.modules:
        sp = importlib.util.spec_from_file_location("fam05", BASE / "src" / "fam05.py")
        m = importlib.util.module_from_spec(sp)
        sys.modules["fam05"] = m
        sp.loader.exec_module(m)
    return sys.modules["fam05"]


F5 = _fam05()
sha, sha_archivo, leer, leer_jsonl, rel, F1 = F5.sha, F5.sha_archivo, F5.leer, F5.leer_jsonl, F5.rel, F5.F1
COORD = BASE / "nucleo_s6" / "coord"
DATOS = BASE / "datos" / "fam07"
REF = BASE / "referencias" / "fam07" / "rem124"
CODIGO = {"tarea_lote.py": "ffd44b60534922410fbbb99c7c68064ffc84b7e7b467d9b30510cbd06e852ed4",
          "conexion_coord_cert.py": "e5776de970b72535ec7b72340604abfd9e8448479ea78dac4b714d870d273d61",
          "validar_lote.py": "070ae81d15119735369b08bf083e9ff3b7652ca99a2956547b9f290db4022ee4",
          "validar_coord_rec.py": "cc83b778cfc4d7f56417084cb9222a4c40d8c097138eaf519aedf94ee37fa0a8",
          "ensamblar_coord.py": "fcb4046962a930aea76495a59bee861882336df4cd97686c8ad0c59607825793"}
MANIFIESTO = ("MANIFIESTO_COORD_REC_B.json", "108bf2edc0261769e3f8a3d962c12610c9045b5898dfbfe70409607c278979e6")
ANEXO = ("COBERTURA_COORD_REC_B.json", "a4d8c58e7dcf3403b388737ba0e2bfc75055673af374ea21c20d64626c72260e")
PAQUETE = ("PAQUETE_COORD_REC.json", "644876a1aba23e9c5214dc01fccd9b5dc2bf06a699cb058ec7d109f46897f042")
ALCANCE = ("alcance_coord_rec_B.json", "0555825f50439fcf0b7c9cdafe011c2570fe017c23c416576a7ab5052c3af227")
DECLARACION = "ejecucion_limpia.json"
TAREAS = ("L1-COORD-R1", "L1-COORD-R2", "L1-COORD-R3")
ENSAMBLADO = "ENSAMBLADO"
PRODUCTOS = ("coord_techos_rec.jsonl", "coord_comparacion_rec.jsonl")
PRODUCTOS_ENS = ("coord_techos_ensamblados.jsonl", "coord_comparacion_ensamblada.jsonl")
GUARDADO = "guardado"
ETIQUETA = "REPRODUCCION LIMPIA FAM07 NO OFICIAL"
REGENERACION = "regeneración sobre entradas guardadas"
MIXTA = "procedencia mixta (tareas nuevas y tareas guardadas)"
NUEVA = "ensamblado sobre salidas nuevas"
OPERACIONES = {"F07-RECALCULO": "6 techos certificados (L1-COORD-R1/R2/R3, dos por tarea) y sus 30 comparaciones dependientes",
               "F07-REUTILIZADAS": "20 techos reutilizados (12 rem112 + 8 rem120, convergence_estimate) y sus 1.502 comparaciones del ensamblado",
               "F07-PREVIAS-192": "192 comparaciones previas aceptadas del lote 1, aparte de las 1.532 (1.724 celdas)"}
# resultado.json y productos aceptados por tarea (catálogo: datos_configuracion y productos L_rem125 de F07-RECALCULO)
RESULTADO_ACEPTADO = {"L1-COORD-R1": "b0985048096b0f8982287fe333ae623e2f91f03b1dae91c85d63d40fc64f0617",
                      "L1-COORD-R2": "d347d884d02452074395b798be3cc9701fa47f716e9d44b29015140c3afedec3",
                      "L1-COORD-R3": "597ea1317497aafb3fd845e1a79e06d748c60d961971e11e9a85ce3e254bdc96"}
ENS_ACEPTADO = {"coord_comparacion_ensamblada.jsonl": "7e45e7e694255ee7d97491b6a0e06adbf509f18f81c33a0c750b4775616bf2e7",
                "coord_techos_ensamblados.jsonl": "f1889ee6d05fd102d3d1995d9e25fc2b7376af83130c252165225d2de42d6568",
                "ENSAMBLADO.json": "962be1dcbc53bbe189df0a0fd5105c7ea4712209821072f7194bd29b7e0e609e"}     # proyección del catálogo (original 4ef5820d…)
PREVIAS = ("referencias/fam04/rem112/L1-COORD/salida/coord_comparacion.jsonl", "9de71ea11467bdedfe9584cc6eaf9bc325500fdb621c4d929d4739bc2820f999")
LOTE1 = "datos/fam04/LOTE1_MANIFIESTO.json"
RUTAS_FUENTES = {"tmp/paso4_suplemento_topologia_desde_rem119/lote2/LOTE2_MANIFIESTO.json": "datos/fam05/LOTE2_MANIFIESTO.json",
                 "tmp/paso4_lote1_desde_rem112/lote1_LOTE1_REM112/L1-COORD/salida/coord_techos.jsonl":
                     "referencias/fam04/rem112/L1-COORD/salida/coord_techos.jsonl",
                 "tmp/paso4_lote2_e4_desde_rem120/lote2_REM120_LOTE2/L1-COORD/salida/coord_techos.jsonl": "datos/fam07/rem120/L1-COORD/salida/coord_techos.jsonl",
                 "tmp/paso4_lote2_e4_desde_rem120/lote2_REM120_LOTE2/L1-COORD/salida/coord_comparacion.jsonl":
                     "datos/fam07/rem120/L1-COORD/salida/coord_comparacion.jsonl"}
ADAPTACIONES = ("GUION-v1", "NUCLEO-C0-v1", "RUTAS-FUENTES-v1", "RAIZ-v1", "PUERTA-v1", "ENSAMBLADOR-ENTRADAS-v1", "RELOJ-PILOTO-v1")
_NUCLEO_HIST = 'AQUI.parents[1] / "paso4_raices_impacto_desde_rem116/candidato_c0/instalacion"'
SUSTITUCIONES = {
    "tarea_lote.py": (
        ("RAIZ-v1", "R = AQUI.parents[2]\n", "R = AQUI.parents[1]                                         # FAM07 RAIZ-v1: base limpia (solo hasta-seleccion)\n"),
        ("PUERTA-v1",
         'if modo == "produccion":\n'
         '    if not ("--alcance" in o and "--decision" in o and "--instalacion" in o):\n'
         '        fin("rechazada", "PRODUCCION_SIN_ALCANCE_NI_DECISION (no autorizada en rem122)")\n'
         '    sys.path.insert(0, str(Path(o["--instalacion"]) / "herramientas/b"))\n'
         '    import aprobacion_alcance as AA  # noqa: E402\n'
         '    ab = Path(o["--alcance"]).read_bytes()\n'
         '    al = json.loads(ab)\n'
         '    try:\n'
         '        AA.verificar_documento(al)                                       # documento de alcance v3 completo y no oficial\n'
         '    except AA.Rechazo as ex:\n'
         '        fin("rechazada", ex.codigo)\n'
         '    if al.get("lote_manifiesto_sha256") != H(raw) or (al.get("entradas") or {}).get("lote_manifiesto") != H(raw):\n'
         '        fin("rechazada", "ALCANCE_DE_OTRO_MANIFIESTO")\n'
         '    if tarea not in (al.get("tareas") or []):\n'
         '        fin("rechazada", "TAREA_FUERA_DEL_ALCANCE")\n'
         '    if (al.get("entradas") or {}).get("codigo_lote") != out["codigo_sha256"]:\n'
         '        fin("rechazada", "ALCANCE_DE_OTRO_CODIGO_DEL_LOTE")\n'
         '    if al.get("instalacion_identidad") != AA.identidad_instalacion(Path(o["--instalacion"])):\n'
         '        fin("rechazada", "ALCANCE_DE_OTRA_INSTALACION")\n'
         '    try:\n'
         '        AA.decision_humana(o["--decision"], H(ab), al["emitida_utc"])\n'
         '    except AA.Rechazo as ex:\n'
         '        fin("rechazada", ex.codigo)\n'
         '    out["alcance_sha256"] = H(ab)\n',
         'if modo == "produccion":                    # FAM07 PUERTA-v1: sin puerta de producción (ni alcance v3 ni decisión humana)\n'
         '    if "--declaracion" not in o:\n'
         '        fin("rechazada", "PRODUCCION_SIN_DECLARACION_DE_EJECUCION_LIMPIA")\n'
         '    out["alcance_sha256"] = H(Path(o["--declaracion"]).read_bytes())    # sha256 de datos/fam07/ejecucion_limpia.json (NO OFICIAL)\n')),
    "validar_coord_rec.py": (
        ("NUCLEO-C0-v1", 'NUCLEO = Path(__file__).resolve().parents[2] / "paso4_raices_impacto_desde_rem116/candidato_c0/instalacion"',
         'NUCLEO = Path(__file__).resolve().parents[1] / "c0"'),
        ("RUTAS-FUENTES-v1 (tabla)", 'SIN_CALCULO = ("PROVEEDOR_NO_CERTIFICADO", "CONFIGURACION_DISTINTA_DE_LA_DECLARADA", "DETENIDO_POR_TOPE")\n',
         'SIN_CALCULO = ("PROVEEDOR_NO_CERTIFICADO", "CONFIGURACION_DISTINTA_DE_LA_DECLARADA", "DETENIDO_POR_TOPE")\n'
         'RUTAS_FUENTES = %s    # FAM07 RUTAS-FUENTES-v1: ruta histórica -> archivo de la base limpia\n' % json.dumps(RUTAS_FUENTES, ensure_ascii=False)),
        ("RUTAS-FUENTES-v1 (lectura)", '    p = Path(R) / ref["ruta"]\n',
         '    if ref["ruta"] not in RUTAS_FUENTES:                              # FAM07 RUTAS-FUENTES-v1: solo fuentes declaradas\n'
         '        return None, "FUENTE_NO_DECLARADA_EN_LA_BASE_LIMPIA:%s" % ref["ruta"]\n'
         '    p = Path(R) / RUTAS_FUENTES[ref["ruta"]]\n')),
    "validar_lote.py": (
        ("NUCLEO-C0-v1", "NUCLEO = " + _NUCLEO_HIST, 'NUCLEO = AQUI.parents[0] / "c0"'),),
    "ensamblar_coord.py": (
        ("NUCLEO-C0-v1", "NUCLEO = " + _NUCLEO_HIST, 'NUCLEO = AQUI.parents[0] / "c0"'),
        ("ENSAMBLADOR-ENTRADAS-v1 (argumento)", "LANZ = [Path(x) for x in sys.argv[4:]]\n",
         'ENT = json.loads(sys.argv[4])                     # FAM07 ENSAMBLADOR-ENTRADAS-v1: carpeta declarada por tarea y salida explícita\n'
         'LANZ = [Path(x) for x in ENT["tareas"].values()]\n'),
        ("ENSAMBLADOR-ENTRADAS-v1 (tarea)", '    dirs = [d / tarea for d in LANZ if (d / tarea / "resultado.json").is_file()]\n',
         '    dirs = [Path(ENT["tareas"][tarea])] if tarea in ENT["tareas"] and (Path(ENT["tareas"][tarea]) / "resultado.json").is_file() else []\n'),
        ("ENSAMBLADOR-ENTRADAS-v1 (procedencia relativa)", '"directorio": str(dirs[0]), "lanzamiento": str(dirs[0].parent)',
         '"directorio": ENT["directorio"][tarea], "lanzamiento": ENT["lanzamiento"][tarea]'),
        ("ENSAMBLADOR-ENTRADAS-v1 (salida)", 'D = LANZ[0] / "ENSAMBLADO"\n', 'D = Path(ENT["salida"]) / "ENSAMBLADO"\n'))}


class Fam07Error(RuntimeError):
    pass


def need(t, codigo):
    if not t:
        raise Fam07Error(codigo)


def fuentes() -> dict:
    return leer(BASE / "fuentes_fam07.json")


def piezas() -> list:
    """fuentes_fam07.json (archivos y reutilizados) y los archivos copiados del núcleo C0 (fuentes_fam05.json)."""
    fu = fuentes()
    c0 = [dict(x, papel="núcleo C0 (reutilizado de FAM05)") for x in F5.fuentes()["archivos"] if x["archivo"].startswith("nucleo_s6/c0/")]
    return fu["archivos"] + fu["reutilizados"] + c0


def uso_de(a: str) -> str:
    if a.startswith("referencias/fam07/"):
        return "referencia"
    if a in RUTAS_FUENTES.values():
        return "fuente"
    if a.startswith(("nucleo_s6/coord/", "nucleo_s6/c0/")) or a in ("datos/fam07/" + MANIFIESTO[0], "datos/fam07/" + ANEXO[0], "datos/fam07/" + DECLARACION):
        return "comun"
    return "verificacion"


def fuentes_alteradas(uso: str = "todo") -> list:
    """Piezas ausentes o con otra huella. calculo/validacion: código, núcleo, manifiesto, anexo y declaración; ensamblado: además las
    fuentes autenticadas (manifiesto del lote 2, techos rem112/rem120, comparaciones rem120); las tareas guardadas se autentican por
    entrada. Nunca las referencias del ensamblado (no se leen para producirlo)."""
    adm = {"todo": None, "calculo": {"comun"}, "validacion": {"comun"}, "ensamblado": {"comun", "fuente"}}[uso]
    return [x["archivo"] for x in piezas() if (adm is None or uso_de(x["archivo"]) in adm) and sha_archivo(BASE / x["archivo"]) != x["sha256"]]


def manifiesto() -> tuple:
    raw = (DATOS / MANIFIESTO[0]).read_bytes()
    need(sha(raw) == MANIFIESTO[1], "MANIFIESTO_COORD_DISTINTO")
    man = json.loads(raw)
    need(not str(man.get("kind", "")).endswith("-SINTETICO"), "MANIFIESTO_SINTETICO")
    return raw, man


def catalogo_op(op: str) -> dict:
    return next(o for o in leer(BASE / "catalogo.json")["operaciones"] if o["clave"] == op)


# ================================================================================================ guiones adaptados
def adaptado(n: str) -> str:
    """GUION-v1: bytes exactos de nucleo_s6/coord/<n> con sus sustituciones declaradas (cada original, una sola vez)."""
    src = (COORD / n).read_bytes()
    need(sha(src) == CODIGO[n], "CODIGO_COORD_DISTINTO: %s" % n)
    txt = src.decode("utf-8")
    for i, a, b in SUSTITUCIONES.get(n, ()):
        need(txt.count(a) == 1, "SUSTITUCION_NO_UNICA: %s %s" % (n, i))
        txt = txt.replace(a, b)
    return txt


def sustituciones_ok() -> bool:
    try:
        for n in SUSTITUCIONES:
            adaptado(n)
        return True
    except Fam07Error:
        return False


def preparar():
    """Núcleo C0 delante y módulo de identidad (FAM05); validar_coord_rec desde su texto adaptado (RUTAS-FUENTES-v1, NUCLEO-C0-v1)."""
    F5.preparar()
    txt = adaptado("validar_coord_rec.py")
    m = sys.modules.get("validar_coord_rec")
    if m is None or getattr(m, "FAM07_ADAPTADO_SHA256", None) != sha(txt.encode("utf-8")):
        m = types.ModuleType("validar_coord_rec")
        m.__file__ = str(COORD / "validar_coord_rec.py")
        sys.modules["validar_coord_rec"] = m
        ruta = list(sys.path)
        try:
            exec(compile(txt, str(COORD / "validar_coord_rec.py"), "exec"), m.__dict__)
        finally:
            sys.path[:] = ruta
        m.FAM07_ADAPTADO_SHA256 = sha(txt.encode("utf-8"))
    cx = sys.modules.get("conexion_coord_cert")
    if cx is not None:
        need(Path(cx.__file__).resolve() == (COORD / "conexion_coord_cert.py").resolve(), "CONEXION_COORD_DE_OTRO_PAQUETE: %s" % cx.__file__)
    return m


def guion(n: str, args: list) -> tuple:
    """Ejecuta el guion adaptado como __main__ con sys.argv = [nucleo_s6/coord/<n>, *args]; devuelve (rc, última línea JSON, stdout, excepción)."""
    VC = preparar()
    txt = adaptado(n)
    viejo, ruta, buf, rc, exc = sys.argv, list(sys.path), io.StringIO(), None, None
    sys.argv = [str(COORD / n)] + [str(x) for x in args]
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(txt, str(COORD / n), "exec"), {"__name__": "__main__", "__file__": str(COORD / n), "__builtins__": builtins})
    except SystemExit as ex:
        rc = ex.code
    except Exception:  # noqa: BLE001  (se registra; nunca se toma por éxito)
        exc = traceback.format_exc()
    finally:
        sys.argv = viejo
        sys.path[:] = ruta
    need(sys.modules.get("validar_coord_rec") is VC, "VALIDADOR_COORD_SUSTITUIDO_DURANTE_EL_GUION")
    lineas = [x for x in buf.getvalue().splitlines() if x.strip()]
    try:
        ult = json.loads(lineas[-1]) if lineas else {}
    except ValueError:
        ult = {}
    return rc, ult, buf.getvalue(), exc


# ================================================================================================ declaración y pilotos
def regla_declaracion() -> dict:
    return {"kind": "declaracion-ejecucion-limpia-fam07", "etiqueta": ETIQUETA, "oficial": False,
            "naturaleza": ("PUERTA-v1: la puerta de producción del trabajador COORD (alcance v3 verificado y decisión humana nativa) no se ejecuta ni "
                           "se reconstruye. El sha256 de este documento ocupa el campo alcance_sha256 que el trabajador escribe tras la puerta y que el "
                           "validador exige a un resultado real para ligar cada techo con su resultado. No es un alcance ni una decisión; no autoriza "
                           "producción oficial ni sustituye al alcance histórico (0555825f…, que solo se usa para cruzar huellas)."),
            "manifiesto_sha256": MANIFIESTO[1], "codigo_trabajador": {n: CODIGO[n] for n in ("tarea_lote.py", "conexion_coord_cert.py")},
            "validador": {n: CODIGO[n] for n in ("validar_lote.py", "validar_coord_rec.py")}, "ensamblador": CODIGO["ensamblar_coord.py"],
            "instalacion_identidad": F5.C0_IDENTIDAD, "tareas": list(TAREAS)}


def regla_pilotos(man: dict) -> dict:
    co = man["L1-COORD-REC"]
    t = TAREAS[0]
    cl = co["tareas"][t]
    cel = [c for c in co["celdas_afectadas"] if c["clave_transformada_sha256"] in cl]
    return {"regla": ("fijado por el encargo de FAM07, antes de conocer resultados nuevos: la tarea histórica completa L1-COORD-R1, primera de la "
                      "partición B (sus dos techos certificados y sus comparaciones dependientes, sin reducir el problema)"),
            "pilotos": [{"tarea": t, "operacion": "F07-RECALCULO",
                         "claves": [{"clave": k, "diseno": co["claves_recalculadas"][k]["diseno"], "j": co["claves_recalculadas"][k]["j"],
                                     "celdas": sum(1 for c in cel if c["clave_transformada_sha256"] == k)} for k in cl],
                         "techos": len(cl), "comparaciones": len(cel), "limite_externo_s": F5.TOPE_TRABAJO,
                         "reloj_interno_s": F5.TOPE_TRABAJO - F5.HOLGURA}]}


def fijar(nombre: str, doc: dict) -> dict:
    raw = (json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True) + "\n").encode("utf-8")
    p = DATOS / nombre
    if p.exists():
        need(p.read_bytes() == raw, "DATO_FIJADO_DISTINTO_DE_SU_REGLA: %s" % nombre)
    else:
        p.write_bytes(raw)
    return doc


def declaracion() -> tuple:
    """La declaración de ejecución limpia: bytes iguales a su regla y a los declarados en fuentes_fam07.json."""
    p = DATOS / DECLARACION
    raw = p.read_bytes() if p.is_file() else b""
    esp = (json.dumps(regla_declaracion(), ensure_ascii=False, indent=1, sort_keys=True) + "\n").encode("utf-8")
    need(raw == esp, "DECLARACION_DE_EJECUCION_LIMPIA_AUSENTE_O_DISTINTA")
    return sha(raw), json.loads(raw)


def listar() -> dict:
    raw, man = manifiesto()
    co = man["L1-COORD-REC"]
    tarea_de = {k: t for t, ks in co["tareas"].items() for k in ks}
    lote2 = leer(BASE / RUTAS_FUENTES[co["lote2_manifiesto"]["ruta"]])["L1-COORD"]["celdas"]
    por_clave = Counter(c["clave_transformada_sha256"] for c in lote2)
    claves = [{"clave": k, "origen": "recalculado" if k in co["claves_recalculadas"] else "reutilizado:" + co["claves_reutilizadas"][k]["fuente"],
               "tarea": tarea_de.get(k), "diseno": (co["claves_recalculadas"].get(k) or {}).get("diseno"),
               "garantia": "certified_bound (a recalcular)" if k in co["claves_recalculadas"] else co["claves_reutilizadas"][k]["error_kind_original"],
               "celdas": por_clave.get(k, 0)} for k in co["claves_coord_total"]]
    return {"comando": "fam07-listar", "calculo": "ninguno", "manifiesto_sha256": sha(raw), "operaciones": OPERACIONES,
            "recuento": {"claves": len(claves), "recalculadas": len(co["claves_recalculadas"]), "reutilizadas": len(co["claves_reutilizadas"]),
                         "reutilizadas_por_fuente": dict(Counter(v["fuente"] for v in co["claves_reutilizadas"].values())),
                         "tareas": {t: len(v) for t, v in co["tareas"].items()}, "celdas_afectadas": len(co["celdas_afectadas"]),
                         "celdas_total": co["celdas_total"], "previas": co["comparaciones_previas_aceptadas"]["filas"],
                         "fuera_del_lote": sorted(co["fuera_del_lote"])},
            "claves": claves, "pilotos": fijar("pilotos.json", regla_pilotos(man)), "declaracion": fijar(DECLARACION, regla_declaracion())}


# ================================================================================================ comprobación (sin cálculo científico)
def cobertura(man: dict) -> dict:
    """Recuentos y partición desde el manifiesto B, el manifiesto del lote 2 y las 30 filas padre (sin calcular)."""
    co = man["L1-COORD-REC"]
    mot = []
    rec, reu, tot = set(co["claves_recalculadas"]), set(co["claves_reutilizadas"]), co["claves_coord_total"]
    part = [k for ks in co["tareas"].values() for k in ks]
    lote2 = leer(BASE / RUTAS_FUENTES[co["lote2_manifiesto"]["ruta"]])
    celdas = lote2["L1-COORD"]["celdas"]
    fuera = lote2.get("L1-COORD_fuera") or {}
    idx = {(c["unidad"], c["cell_id"]): c for c in celdas}
    afect = co["celdas_afectadas"]
    distintas = [c["cell_id"] for c in afect if (idx.get((c["unidad"], c["cell_id"])) or {}).get("clave_transformada_sha256") != c["clave_transformada_sha256"]
                 or any(idx[(c["unidad"], c["cell_id"])].get(x) != c[x] for x in ("K1_reutilizado", "G_padre"))]
    padres = []
    for c in afect:
        p = BASE / "referencias/fam01/originales" / ("%s_filas.json" % c["unidad"])
        b = p.read_bytes() if p.is_file() else b""
        cr = (json.loads(b).get("confrontation_result") or [{}])[0] if sha(b) == c["filas_sha256"] else None
        padres.append(cr is not None and cr.get("K_comp_1") == c["K1_reutilizado"] and cr.get("G") == c["G_padre"])
    r = {"claves": len(tot), "claves_unicas": len(set(tot)), "recalculadas": len(rec), "reutilizadas": len(reu),
         "reutilizadas_por_fuente": dict(Counter(v["fuente"] for v in co["claves_reutilizadas"].values())),
         "recalculadas_y_reutilizadas_disjuntas": not (rec & reu), "union_igual_a_las_claves": rec | reu == set(tot),
         "particion": {t: len(v) for t, v in co["tareas"].items()}, "particion_exacta_de_las_recalculadas": sorted(part) == sorted(rec) and len(part) == len(set(part)),
         "celdas_lote2": len(celdas), "celdas_total_del_manifiesto": co["celdas_total"], "celdas_unicas": len(idx),
         "celdas_de_claves_ajenas": sum(1 for c in celdas if c["clave_transformada_sha256"] not in set(tot)),
         "celdas_de_recalculadas": sum(1 for c in celdas if c["clave_transformada_sha256"] in rec),
         "celdas_de_reutilizadas": sum(1 for c in celdas if c["clave_transformada_sha256"] in reu),
         "celdas_afectadas": len(afect), "celdas_afectadas_por_tarea": {t: sum(1 for c in afect if c["clave_transformada_sha256"] in ks) for t, ks in co["tareas"].items()},
         "celdas_afectadas_iguales_al_lote2": not distintas, "celdas_afectadas_de_las_recalculadas": {c["clave_transformada_sha256"] for c in afect} <= rec,
         "filas_padre_autenticadas_con_K1_y_G": sum(padres),
         "fuera_del_lote": {k: v.get("estado") for k, v in co["fuera_del_lote"].items()},
         "fuera_del_lote_igual_al_lote2_y_sin_celdas": set(co["fuera_del_lote"]) == set(fuera) and not any(c.get("conjunto_coord") in fuera for c in celdas)
                                                       and all("no NA" in str(v.get("estado")) for v in co["fuera_del_lote"].values())}
    if not (r["claves"] == r["claves_unicas"] == 26 and r["recalculadas"] == 6 and r["reutilizadas"] == 20
            and r["reutilizadas_por_fuente"] == {"rem112_coord_techos": 12, "rem120_coord_techos": 8} and r["recalculadas_y_reutilizadas_disjuntas"]
            and r["union_igual_a_las_claves"] and r["particion"] == {t: 2 for t in TAREAS} and r["particion_exacta_de_las_recalculadas"]):
        mot.append("CLAVES_O_PARTICION_DISTINTAS")
    if not (r["celdas_lote2"] == r["celdas_total_del_manifiesto"] == r["celdas_unicas"] == 1532 and r["celdas_de_claves_ajenas"] == 0
            and r["celdas_de_recalculadas"] == r["celdas_afectadas"] == 30 and r["celdas_de_reutilizadas"] == 1502):
        mot.append("CELDAS_DISTINTAS")
    if not (r["celdas_afectadas_por_tarea"] == {"L1-COORD-R1": 16, "L1-COORD-R2": 12, "L1-COORD-R3": 2} and r["celdas_afectadas_iguales_al_lote2"]
            and r["celdas_afectadas_de_las_recalculadas"] and r["filas_padre_autenticadas_con_K1_y_G"] == 30):
        mot.append("CELDAS_AFECTADAS_DISTINTAS")
    if not (len(r["fuera_del_lote"]) == 2 and r["fuera_del_lote_igual_al_lote2_y_sin_celdas"]):
        mot.append("FUERA_DEL_LOTE_DISTINTO")
    r["cumple"], r["motivos"] = not mot, mot
    return r


def reutilizaciones(man: dict) -> dict:
    """F07-REUTILIZADAS: validar_coord_rec.reutilizados_autenticados (adaptado) sobre las fuentes de la base limpia, sin cálculo."""
    VC = preparar()
    co = man["L1-COORD-REC"]
    filas, fallos = VC.reutilizados_autenticados(BASE, co)
    fu = {k: v for k, v in co["fuentes"].items()}
    auth = {k: sha_archivo(BASE / RUTAS_FUENTES[v["ruta"]]) == v["sha256"] for k, v in fu.items()}
    r = {"funcion": "validar_coord_rec.reutilizados_autenticados (RUTAS-FUENTES-v1)", "filas": len(filas), "fallos": fallos,
         "por_fuente": dict(Counter(co["claves_reutilizadas"][f["clave_transformada_sha256"]]["fuente"] for f in filas)),
         "garantia_original": dict(Counter(f["error_kind_original"] for f in filas)),
         "promovidas_a_certificado": sum(1 for k in co["claves_reutilizadas"] if co["claves_reutilizadas"][k].get("certificado") is True),
         "error_almacenado_cero": sum(1 for f in filas if f["error"] == 0.0), "completas": sum(1 for f in filas if f["estado"] == "complete"),
         "fuentes_autenticas": auth, "rutas_declaradas": sorted(RUTAS_FUENTES) == sorted({v["ruta"] for v in fu.values()} | {co["lote2_manifiesto"]["ruta"]}),
         "cuentan_como_recalculadas": 0}
    r["cumple"] = (not fallos and r["filas"] == 20 and r["por_fuente"] == {"rem112_coord_techos": 12, "rem120_coord_techos": 8}
                   and r["garantia_original"] == {"convergence_estimate": 20} and r["promovidas_a_certificado"] == 0 and r["completas"] == 20
                   and all(auth.values()) and r["rutas_declaradas"])
    return r


def previas(man: dict) -> dict:
    """F07-PREVIAS-192: las 192 comparaciones previas frente a las celdas del lote 1 y los techos rem112 (G = C2 − K1 recompuesto) y su
    separación de las 1.532 del lote 2 (sin cálculo)."""
    co = man["L1-COORD-REC"]
    ref = co["comparaciones_previas_aceptadas"]
    p = BASE / PREVIAS[0]
    b = p.read_bytes()
    filas = [json.loads(x) for x in b.decode("utf-8").splitlines() if x.strip()]
    l1 = {(c["unidad"], c["cell_id"]): c for c in leer(BASE / LOTE1)["L1-COORD"]["celdas"]}
    tec = {t["clave_transformada_sha256"]: t for t in leer_jsonl(BASE / RUTAS_FUENTES[co["fuentes"]["rem112_coord_techos"]["ruta"]])}
    l2 = {(c["unidad"], c["cell_id"]) for c in leer(BASE / RUTAS_FUENTES[co["lote2_manifiesto"]["ruta"]])["L1-COORD"]["celdas"]}
    ks = [(x["unidad"], x["cell_id"]) for x in filas]
    malas = []
    for x in filas:
        c = l1.get((x["unidad"], x["cell_id"]))
        t = tec.get((c or {}).get("clave_transformada_sha256"))
        if c is None or t is None or x["K1_reutilizado"] != c["K1_reutilizado"] or x["G_padre"] != c["G_padre"] or x["C2_coord"] != t["C_2"] \
                or x["estado_techo"] != t["estado"] or x["G_coord"] != (t["C_2"] - c["K1_reutilizado"]):
            malas.append(x["cell_id"])
    r = {"archivo": PREVIAS[0], "sha256": sha(b), "igual_al_catalogo": sha(b) == PREVIAS[1] == ref["sha256"]
         == next(p_["sha256_aceptado"] for p_ in catalogo_op("F07-PREVIAS-192")["productos"] if p_["id"] == "P_coord_192"),
         "filas": len(filas), "filas_del_manifiesto": ref["filas"], "unicas": len(set(ks)), "celdas_del_lote1": len(l1),
         "iguales_a_las_celdas_del_lote1": set(ks) == set(l1), "filas_que_no_cuadran_con_lote1_y_techos_rem112": malas[:5],
         "claves_rem112": len({l1[k]["clave_transformada_sha256"] for k in ks if k in l1}),
         "disjuntas_de_las_1532": not (set(ks) & l2), "celdas_declaradas_total": len(set(ks) | l2)}
    r["cumple"] = (r["igual_al_catalogo"] and r["filas"] == r["filas_del_manifiesto"] == r["unicas"] == r["celdas_del_lote1"] == 192
                   and r["iguales_a_las_celdas_del_lote1"] and not malas and r["disjuntas_de_las_1532"] and r["celdas_declaradas_total"] == 1724)
    return r


def referencias(man: dict) -> dict:
    co = man["L1-COORD-REC"]
    mot, tareas = [], {}
    cat = {p["sha256_aceptado"] for p in catalogo_op("F07-RECALCULO")["productos"]}
    catd = {p["id"]: p["sha256_aceptado"] for p in catalogo_op("F07-RECALCULO")["datos_configuracion"]}
    for t in TAREAS:
        res = leer(REF / t / "resultado.json")
        prods = {p["archivo"]: p for p in res["productos"]}
        filas = {n: len(leer_jsonl(REF / t / "salida" / n)) for n in PRODUCTOS}
        ok = (sha_archivo(REF / t / "resultado.json") == RESULTADO_ACEPTADO[t] == catd.get(t)
              and all(sha_archivo(REF / t / "salida" / n) == prods[n]["sha256"] and prods[n]["sha256"] in cat for n in PRODUCTOS)
              and filas[PRODUCTOS[0]] == len(co["tareas"][t])
              and filas[PRODUCTOS[1]] == sum(1 for c in co["celdas_afectadas"] if c["clave_transformada_sha256"] in co["tareas"][t])
              and res["alcance_sha256"] == ALCANCE[1] and res["estado"] == "completa")
        tareas[t] = {"resultado_sha256": sha_archivo(REF / t / "resultado.json"), "filas": filas, "pared_s": res["pared_s"],
                     "segundos_por_techo": {x["clave_transformada_sha256"]: x["segundos"] for x in leer_jsonl(REF / t / "salida" / PRODUCTOS[0])},
                     "iguales_al_catalogo": ok}
        if not ok:
            mot.append("REFERENCIA_DE_TAREA_DISTINTA: %s" % t)
    E = REF / ENSAMBLADO
    ens = {n: sha_archivo(E / n) for n in ENS_ACEPTADO}
    filas = leer_jsonl(E / "coord_comparacion_ensamblada.jsonl")
    if ens != ENS_ACEPTADO or ENS_ACEPTADO["coord_comparacion_ensamblada.jsonl"] not in cat or ENS_ACEPTADO["coord_techos_ensamblados.jsonl"] not in cat:
        mot.append("REFERENCIA_DEL_ENSAMBLADO_DISTINTA")
    pro = re.search(r'"objeto": "proyecciones/([0-9a-f]{64})/ENSAMBLADO.json"', json.dumps(catalogo_op("F07-RECALCULO"), ensure_ascii=False))
    r = {"tareas": tareas, "ensamblado": {"sha256": ens, "proyeccion_igual_al_catalogo": bool(pro) and pro.group(1) == ENS_ACEPTADO["ENSAMBLADO.json"],
                                           "filas": len(filas), "por_origen": dict(Counter(x["origen_techo"] for x in filas)),
                                           "techos": len(leer_jsonl(E / "coord_techos_ensamblados.jsonl"))}}
    if not (r["ensamblado"]["proyeccion_igual_al_catalogo"] and r["ensamblado"]["filas"] == 1532 and r["ensamblado"]["techos"] == 6
            and r["ensamblado"]["por_origen"] == {"recalculado": 30, "reutilizado": 1502}):
        mot.append("RECUENTOS_DEL_ENSAMBLADO_DISTINTOS")
    r["cumple"], r["motivos"] = not mot, mot
    return r


def motor() -> dict:
    """Identidad y configuración del motor certificado SIN calcular: identidad de código de C0 (7 archivos), configuración del proveedor
    de RUN.provider_for(RUN.RunConfig()) frente a la declarada y certificación de la plataforma (elementales)."""
    preparar()
    CX = F5.cargar("conexion_coord_cert", COORD / "conexion_coord_cert.py")
    need(Path(CX.__file__).resolve() == (COORD / "conexion_coord_cert.py").resolve(), "CONEXION_COORD_DE_OTRO_PAQUETE")
    from paper2b import run as RUN
    raw, man = manifiesto()
    mo = man["L1-COORD-REC"]["motor"]
    cfg = RUN.RunConfig()
    model = RUN.provider_for(cfg)
    return {"identidad_de_codigo_igual": CX.identidad_codigo(F5.C0 / "src" / "paper2b") == mo["codigo"],
            "configuracion_igual": CX.configuracion(model, cfg.sup) == mo["configuracion"],
            "proveedor": getattr(model, "kind", None), "certificado_en_esta_plataforma": getattr(model, "certified", None) is True,
            "garantia": getattr(model, "garantia", None), "garantia_igual": getattr(model, "garantia", None) == mo["garantia"] == CX.GARANTIA,
            "tol_converge": cfg.sup.tol_converge, "instalacion_identidad_igual": mo["instalacion_identidad"] == F5.C0_IDENTIDAD}


def comprobar() -> dict:
    """fam07-comprobar: SIN CÁLCULO CIENTÍFICO (ningún techo; la revalidación de las referencias aplica el validador a bytes guardados).
    Con una pieza ausente o alterada no cumple y la informa; si esa ausencia impide seguir, se registra la interrupción (sin rutas)."""
    r = {"comando": "fam07-comprobar", "calculo": "ninguno"}
    malos = fuentes_alteradas()
    fu = fuentes()
    r["fuentes"] = {"archivos": len(fu["archivos"]), "reutilizados": len(fu["reutilizados"]),
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
    raw, man = manifiesto()
    co = man["L1-COORD-REC"]
    an, al, pq = leer(DATOS / ANEXO[0]), leer(DATOS / ALCANCE[0]), leer(DATOS / PAQUETE[0])
    cod = {n: sha_archivo(COORD / n) for n in CODIGO}
    ent = al["entradas"]
    r["procedencia"] = {
        "codigo_igual_al_paquete": all(pq["piezas"][n]["sha256"] == cod[n] for n in CODIGO) and pq["piezas"][MANIFIESTO[0]]["sha256"] == sha(raw)
                                   and pq["piezas"][ANEXO[0]]["sha256"] == ANEXO[1],
        "codigo_igual_al_alcance": ent["codigo_lote"] == {n: cod[n] for n in ("tarea_lote.py", "conexion_coord_cert.py")}
                                   and (ent["validador_lote"], ent["validador_coord_rec"], ent["ensamblador"])
                                   == (cod["validar_lote.py"], cod["validar_coord_rec.py"], cod["ensamblar_coord.py"]),
        "manifiesto_igual_al_alcance": sha(raw) == al["lote_manifiesto_sha256"] == ent["lote_manifiesto"],
        "anexo_igual_al_alcance": ANEXO[1] == ent["cobertura_nacional"],
        "anexo_ligado_al_manifiesto": an.get("kind") == "cobertura-nacional-lote1" and an.get("manifiesto_sha256") == sha(raw),
        "alcance_igual_al_catalogo": sha_archivo(DATOS / ALCANCE[0]) == ALCANCE[1]
                                     == next(p["sha256_aceptado"] for p in catalogo_op("F07-RECALCULO")["datos_configuracion"] if p["id"] == "alcance nativo COORD"),
        "alcance_con_las_tres_tareas": al.get("tareas") == list(TAREAS) == list(co["tareas"]),
        "alcance_y_manifiesto_no_oficiales": all(al.get(k) is False and man.get(k) is False
                                                 for k in ("b_official_run_authorized", "freeze_run_authorized", "official_export_authorized")),
        "identidad_c0_igual": al["instalacion_identidad"] == pq["nucleo"]["identidad"] == co["motor"]["instalacion_identidad"] == F5.C0_IDENTIDAD,
        "fuentes_iguales_al_paquete": pq["fuentes"] == dict(co["fuentes"], lote2_manifiesto=co["lote2_manifiesto"]),
        "variante_B": man.get("variante") == co.get("variante") == "B",
        "sustituciones_unicas": sustituciones_ok()}
    try:
        h, _ = declaracion()
        r["procedencia"]["declaracion_de_ejecucion_limpia"] = h == next((x["sha256"] for x in fu["archivos"] if x["archivo"] == "datos/fam07/" + DECLARACION), None)
    except Fam07Error:
        r["procedencia"]["declaracion_de_ejecucion_limpia"] = False
    F5.preparar()
    import paper2b
    r["nucleo"] = {"identidad_recalculada": F5.identidad_c0(), "igual": F5.identidad_c0() == F5.C0_IDENTIDAD,
                   "paper2b_cargado_de": rel(Path(paper2b.__file__).parent), "declarado_en": "fuentes_fam05.json (nucleo_c0, mismo núcleo que FAM05/FAM06)"}
    r["motor"] = motor()
    r["cobertura"] = cobertura(man)
    r["reutilizaciones"] = reutilizaciones(man)
    r["previas"] = previas(man)
    r["referencias"] = referencias(man)
    lb = fu.get("libro_rem125") or {}
    pares = []
    if lb.get("presente") is True:
        rr, cb, ru, pv = r["referencias"], r["cobertura"], r["reutilizaciones"], r["previas"]
        pares = [("claves_total ↔ claves del manifiesto", lb["claves_total"], cb["claves"]),
                 ("claves ↔ claves del manifiesto (conjunto)", sorted(lb["claves"]), sorted(co["claves_coord_total"])),
                 ("techos_certificados_nuevos_n ↔ recalculadas", lb["techos_certificados_nuevos_n"], cb["recalculadas"]),
                 ("techos_certificados_nuevos ↔ techos de las tres tareas guardadas",
                  {x["clave_transformada_sha256"]: (x["C_2"], x["error_normalizado"], x["final_n"]) for x in lb["techos_certificados_nuevos"]},
                  {x["clave_transformada_sha256"]: (x["C_2"], x["error_normalizado"], x["final_n"]) for t in TAREAS for x in leer_jsonl(REF / t / "salida" / PRODUCTOS[0])}),
                 ("reutilizados ↔ claves_reutilizadas del manifiesto", lb["reutilizados"],
                  {k: {c: v.get(c) for c in ("fuente", "C_2", "estado", "error", "motivo", "error_kind_original")} for k, v in co["claves_reutilizadas"].items()}),
                 ("reutilizados_por_fuente ↔ fuentes autenticadas", [lb["reutilizados_por_fuente"].get(k) for k in ("previously_accepted_rem112", "rem120_d_accepted_now_for_reuse")],
                  [ru["por_fuente"].get("rem112_coord_techos"), ru["por_fuente"].get("rem120_coord_techos")]),
                 ("ensamblado.filas ↔ filas de la referencia", lb["ensamblado"]["filas"], rr["ensamblado"]["filas"]),
                 ("ensamblado.por_origen ↔ origen_techo de la referencia", lb["ensamblado"]["por_origen"], rr["ensamblado"]["por_origen"]),
                 ("ensamblado.reused_roofs ↔ reutilizados autenticados", lb["ensamblado"]["reused_roofs"], ru["filas"]),
                 ("ensamblado.fuera_del_lote ↔ manifiesto", sorted(lb["ensamblado"]["fuera_del_lote"]), sorted(co["fuera_del_lote"])),
                 ("previas_192.count ↔ filas", lb["previas_192"]["count"], pv["filas"]),
                 ("previas_192.disjoint_from_new_1532 ↔ comprobado", lb["previas_192"]["disjoint_from_new_1532"], pv["disjuntas_de_las_1532"]),
                 ("previas_192.total_declared_coord_cells ↔ comprobado", lb["previas_192"]["total_declared_coord_cells"], pv["celdas_declaradas_total"]),
                 ("comparaciones_declaradas_total ↔ comprobado", lb["comparaciones_declaradas_total"], pv["celdas_declaradas_total"])]
    r["libro_rem125"] = {"presente": lb.get("presente"), "solo_extraccion": True,
                         "recuentos": [{"recuento": a, "igual": b == c} for a, b, c in pares],
                         "recuentos_iguales": bool(pares) and all(b == c for _, b, c in pares),
                         "productos_iguales": lb.get("presente") is True
                         and {t: (v["resultado_sha256"], v["productos_sha256"]) for t, v in lb["tareas"].items()}
                         == {t: (RESULTADO_ACEPTADO[t], {n: sha_archivo(REF / t / "salida" / n) for n in PRODUCTOS}) for t in TAREAS}
                         and lb["ensamblado"]["products"] == {n: ENS_ACEPTADO[n] for n in PRODUCTOS_ENS} and lb["previas_192"]["sha256"] == PREVIAS[1],
                         "manifiesto_paquete_y_c0": lb.get("presente") is True and (lb["manifiesto_sha256"], lb["indice_del_paquete_sha256"], lb["identidad_c0"])
                         == (MANIFIESTO[1], PAQUETE[1], F5.C0_IDENTIDAD),
                         "alcance_de_la_decision": lb.get("alcance_de_la_decision_sha256") == ALCANCE[1],
                         "garantia_de_los_reutilizados_preservada": "not promoted" in str(lb.get("garantia_de_los_reutilizados")),
                         "dictamen_consultado_es_el_del_libro": (lb.get("dictamen") or {}).get("sha256_del_archivo") == (lb.get("dictamen") or {}).get("sha256_en_el_libro") is not None}
    rv = {}
    for t in TAREAS:
        rc, ver, _, exc = guion("validar_lote.py", [BASE, DATOS / MANIFIESTO[0], REF / t / "resultado.json", REF / t / "salida", DATOS / ANEXO[0]])
        hist = json.loads((REF / t / "validacion_stdout.txt").read_text(encoding="utf-8"))
        rv[t] = {"rc": rc, "dictamen": ver.get("dictamen"), "fallos": ver.get("fallos"), "igual_a_la_validacion_historica": ver == hist, "excepcion": exc}
    r["revalidacion_de_las_referencias"] = rv
    pil = leer(DATOS / "pilotos.json") if (DATOS / "pilotos.json").is_file() else None
    r["pilotos"] = {"fijados": [(p["tarea"], [c["clave"] for c in p["claves"]]) for p in (pil or {}).get("pilotos", [])], "iguales_a_la_regla": pil == regla_pilotos(man)}
    r["receta"] = {"pasos": len(receta()["pasos"])}
    r["cumple"] = (not malos and all(r["procedencia"].values()) and r["nucleo"]["igual"]
                   and all(r["motor"][k] for k in ("identidad_de_codigo_igual", "configuracion_igual", "certificado_en_esta_plataforma", "garantia_igual",
                                                   "instalacion_identidad_igual"))
                   and r["cobertura"]["cumple"] and r["reutilizaciones"]["cumple"] and r["previas"]["cumple"] and r["referencias"]["cumple"]
                   and all(v is True for k, v in r["libro_rem125"].items() if k != "recuentos")
                   and all(v["rc"] == 0 and v["igual_a_la_validacion_historica"] for v in rv.values()) and r["pilotos"]["iguales_a_la_regla"])
    return r


# ================================================================================================ cálculo (F07-RECALCULO)
def declarados() -> set:
    out = set(F5.declarados())
    if (BASE / "fuentes_fam07.json").is_file():
        out |= {x["archivo"] for x in piezas()}
    return out


def lecturas(informe: dict) -> dict:
    dec = declarados()
    propios = ("src/", "reproducir.py", "datos/fam01/", "datos/fam07/", "fuentes_fam0", "catalogo.json")
    en = informe["en_el_paquete"]
    sin = [x for x in en if x not in dec and not x.startswith(".venv-fam01/") and not x.startswith(propios)]
    return {"archivo": "archivos_leidos.json", "en_el_paquete": len(en), "del_entorno_venv": sum(1 for x in en if x.startswith(".venv-fam01/")),
            "aperturas_del_interprete": informe["aperturas_del_interprete"], "fuera_del_paquete_y_del_interprete": informe["fuera_del_paquete_y_del_interprete"],
            "sin_manifiesto": sin, "nucleo_c0_leidos": sum(1 for x in en if x.startswith("nucleo_s6/c0/")),
            "codigo_coord_leido": sorted(x for x in en if x.startswith("nucleo_s6/coord/")),
            "src_de_otra_raiz_leidos": sum(1 for x in en if x.startswith(("nucleo_s6/instalacion/src/", "nucleo_s6/raiz/src/"))),
            "fuentes_leidas": sorted(x for x in en if x in RUTAS_FUENTES.values()),
            "referencias_leidas": sorted(x for x in en if x.startswith("referencias/") and not x.startswith("referencias/fam01/")),
            "ensamblado_esperado_leido": any(x.startswith("referencias/fam07/rem124/ENSAMBLADO/") for x in en)}


def entorno() -> dict:
    e = F5._entorno(None)
    e["f2_alcance"] = "adoptada solo para FAM01; aquí se informa y no es requisito de FAM07"
    return e


def importados() -> dict:
    return {"paper2b": sorted({rel(Path(m.__file__).parent) for k, m in list(sys.modules.items())
                               if (k == "paper2b" or k.startswith("paper2b.")) and getattr(m, "__file__", None)}),
            "conexion_coord_cert": rel(Path(sys.modules["conexion_coord_cert"].__file__)) if "conexion_coord_cert" in sys.modules else None,
            "validar_coord_rec": {"archivo": rel(Path(sys.modules["validar_coord_rec"].__file__)),
                                  "texto_adaptado_sha256": getattr(sys.modules["validar_coord_rec"], "FAM07_ADAPTADO_SHA256", None)}
            if "validar_coord_rec" in sys.modules else None}


def correr(tarea: str, salida: Path, tope: float = F5.TOPE_TRABAJO) -> dict:
    """fam07-unidad: una tarea de la partición (sus dos techos certificados y sus comparaciones) por la ruta de producción de tarea_lote.py
    (GUION-v1, PUERTA-v1) en la carpeta NUEVA `salida`: resultado.json y salida/<productos> (los escribe el trabajador), trabajo_stdout.txt,
    ejecucion.json y archivos_leidos.json."""
    T0, c0 = time.time(), time.process_time()
    rastro = F1().Rastro()                       # desde el principio: también las lecturas previas al cálculo
    need(tarea in TAREAS, "TAREA_FUERA_DE_LA_PARTICION: %s" % tarea)
    raw, man = manifiesto()
    malos = fuentes_alteradas("calculo")
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam07.json; no se calcula): %s" % malos[:5])
    hdec, _ = declaracion()
    TOPE = float(tope) - F5.HOLGURA
    need(TOPE > 0, "TOPE_INVALIDO")
    preparar()
    need(F5.identidad_c0() == F5.C0_IDENTIDAD, "NUCLEO_C0_DE_OTRA_IDENTIDAD (no se calcula)")
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    sal = salida.resolve()
    args = ["--tarea", tarea, "--modo", "produccion", "--manifiesto", DATOS / MANIFIESTO[0], "--manifiesto-sha256", MANIFIESTO[1],
            "--salida", sal / "salida", "--resultado", sal / "resultado.json", "--tope-efectivo", repr(TOPE), "--instalacion", F5.C0,
            "--declaracion", DATOS / DECLARACION]
    a0 = time.time()
    rc, ult, stdout, exc = guion("tarea_lote.py", args)
    t_calc = round(time.time() - a0, 2)
    (sal / "trabajo_stdout.txt").write_text(stdout, encoding="utf-8")
    res = leer(sal / "resultado.json") if (sal / "resultado.json").is_file() else {}
    informe = rastro.informe()
    (sal / "archivos_leidos.json").write_bytes((json.dumps(informe, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    co = man["L1-COORD-REC"]
    techos = leer_jsonl(sal / "salida" / PRODUCTOS[0]) if (sal / "salida" / PRODUCTOS[0]).is_file() else []
    ej = {"tarea": tarea, "operacion": "F07-RECALCULO", "claves": co["tareas"][tarea], "manifiesto_sha256": sha(raw), "etiqueta": ETIQUETA,
          "naturaleza": ("cálculo: ruta de producción de tarea_lote.py (bytes exactos, GUION-v1) con conexion_coord_cert y "
                         "RUN.provider_for(RUN.RunConfig()) (ModeloTeorico certificado) en la base limpia; sin puerta de producción (PUERTA-v1)"),
          "declaracion_sha256": hdec, "adaptaciones": list(ADAPTACIONES),
          "sustituciones": [x[0] for x in SUSTITUCIONES["tarea_lote.py"]] + ["validar_coord_rec.py: " + x[0] for x in SUSTITUCIONES["validar_coord_rec.py"]],
          "trabajador_adaptado_sha256": sha(adaptado("tarea_lote.py").encode("utf-8")),
          "reloj": "RELOJ-PILOTO-v1: tope interno %.0f s (= %.0f − %.0f); el límite externo lo pone el supervisor" % (TOPE, float(tope), F5.HOLGURA),
          "rc_del_trabajador": rc, "excepcion": exc, "ultima_linea": ult,
          "resultado": {"estado": res.get("estado"), "motivo": res.get("motivo"), "productos": res.get("productos")},
          "techos": [{k: t.get(k) for k in ("clave_transformada_sha256", "diseno", "estado", "motivo", "error_kind", "garantia", "C_2", "error_normalizado",
                                            "error_R", "cierre_por_escala", "final_n", "segundos")} for t in techos],
          "nucleo": {"identidad": F5.identidad_c0(), "importados": importados()},
          "tiempos_s": {"calculo": t_calc, "total": round(time.time() - T0, 2), "cpu": round(time.process_time() - c0, 2)},
          "entorno": entorno(), "lecturas": lecturas(informe), "dependencias_fuera_de_la_biblioteca_estandar": F1().dependencias_cargadas()}
    ej["exito"] = exc is None and rc == 0 and res.get("estado") == "completa"
    (sal / "ejecucion.json").write_bytes(json.dumps(ej, ensure_ascii=False, indent=1, sort_keys=True, default=str).encode("utf-8") + b"\n")
    return ej


# ================================================================================================ validación
def productos_de(nueva: Path, res: dict) -> dict:
    return {p["archivo"]: sha_archivo(Path(nueva) / "salida" / p["archivo"]) for p in res.get("productos") or []}


def validar(nueva: Path) -> dict:
    """fam07-validar: SIN CÁLCULO. validar_lote.py (validar_coord_rec.validar_tarea) sobre los bytes guardados de `nueva` (carpeta de una
    tarea: resultado.json y salida/)."""
    t0 = time.time()
    nueva = Path(nueva).resolve()
    malos = fuentes_alteradas("validacion")
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam07.json; no se valida): %s" % malos[:5])
    rb = (nueva / "resultado.json").read_bytes() if (nueva / "resultado.json").is_file() else b"{}"
    rc, ver, _, exc = guion("validar_lote.py", [BASE, DATOS / MANIFIESTO[0], nueva / "resultado.json", nueva / "salida", DATOS / ANEXO[0]])
    return {"comando": "fam07-validar", "naturaleza": "validación sin cálculo de bytes guardados", "tarea": json.loads(rb).get("tarea"),
            "origen": rel(nueva), "resultado_sha256": sha(rb), "productos_sha256": productos_de(nueva, json.loads(rb)),
            "validador": {"archivos": {n: CODIGO[n] for n in ("validar_lote.py", "validar_coord_rec.py")},
                          "adaptacion": {n: [x[0] for x in SUSTITUCIONES[n]] for n in ("validar_lote.py", "validar_coord_rec.py")},
                          "adaptado_sha256": {n: sha(adaptado(n).encode("utf-8")) for n in ("validar_lote.py", "validar_coord_rec.py")},
                          "nucleo": "nucleo_s6/c0 (NUCLEO-C0-v1)"},
            "rc": rc, "veredicto": ver, "excepcion": exc,
            "aceptada": exc is None and rc == 0 and ver.get("aceptada") is True and ver.get("dictamen") == "completa_validada", "segundos": round(time.time() - t0, 3)}


# ================================================================================================ comparación de una tarea
# COMPARACION-FAM07-v1. Mismo perfil de entorno .venv-fam01 y MISMO núcleo C0 que la referencia rem124. CR-HASH-CANONICO (cada fila
# idéntica campo a campo con su serialización JSON: valores, cotas, errores en las dos escalas, testigos, niveles, configuración) y
# CR-DISCRETOS (claves, celdas, estados, error_kind, garantía, cierre por escala, motivo, final_n y conteos exactos, con precedencia). Las
# tolerancias internas del validador (Iv, 1e-7) son suyas y no se usan aquí. Se apartan, visibles, solo dos campos de los techos:
# «segundos» (OPERATIVO: tiempo de pared del techo) y «alcance_sha256» (VINCULO: en la nueva, el sha256 de la declaración de ejecución
# limpia que lleva SU resultado; en la referencia, el del alcance histórico que lleva el suyo). Huella derivada: los techos nuevos con esos
# dos campos repuestos de la referencia y serializados como el trabajador reproducen los bytes del producto de referencia.
CLAVE_FILA = {"coord_techos_rec.jsonl": ("clave_transformada_sha256",), "coord_comparacion_rec.jsonl": ("unidad", "cell_id"),
              "coord_techos_ensamblados.jsonl": ("clave_transformada_sha256",), "coord_comparacion_ensamblada.jsonl": ("unidad", "cell_id")}
OPERATIVOS = {"coord_techos_rec.jsonl": ("/segundos",), "coord_techos_ensamblados.jsonl": ("/segundos",)}
VINCULO = "/alcance_sha256"
DISCRETOS_NUMERICOS = ("final_n",)


def comparar_filas(nuevas_l: list, ref_l: list, clave: tuple, operativos=(), vinculos: dict | None = None) -> dict:
    vinculos = vinculos or {}
    nuevas, refs = [json.loads(x) for x in nuevas_l], [json.loads(x) for x in ref_l]
    kn, kr = [tuple(f.get(k) for k in clave) for f in nuevas], [tuple(f.get(k) for k in clave) for f in refs]
    dn, dr = dict(zip(kn, nuevas)), dict(zip(kr, refs))
    cob = {"filas_nuevas": len(nuevas), "filas_referencia": len(refs), "faltan": [list(k) for k in kr if k not in dn][:5],
           "ajenas": [list(k) for k in kn if k not in dr][:5], "duplicadas": (len(kn) - len(set(kn))) + (len(kr) - len(set(kr))), "mismo_orden": kn == kr}
    disc, num, oper, vis = [], [], [], Counter()
    for k in kr:
        if k not in dn:
            continue
        hn, hr = F5.hojas(dn[k]), F5.hojas(dr[k])
        for p in sorted(set(hn) | set(hr)):
            a, b = hn.get(p, "<ausente>"), hr.get(p, "<ausente>")
            v = vinculos.get(k, vinculos.get(None, {})).get(p) if vinculos else None
            if v is not None:
                vis[(p, a == v[0], b == v[1])] += 1
                continue
            if p in operativos:
                oper.append({"fila": list(k), "puntero": p, "nueva": a, "referencia": b})
                continue
            if json.dumps(a) == json.dumps(b):
                continue
            d = {"fila": list(k), "puntero": p, "nueva": a, "referencia": b}
            numerico = all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in (a, b)) and p.split("/")[-1] not in DISCRETOS_NUMERICOS
            (num if numerico else disc).append(d)
    vin = {"filas": sum(vis.values()), "nueva_ligada": sum(c for (p, a, b), c in vis.items() if a),
           "referencia_ligada": sum(c for (p, a, b), c in vis.items() if b)} if vinculos else None
    return {"cobertura": cob, "lineas_identicas": nuevas_l == ref_l, "n_discretas": len(disc), "n_numericas": len(num),
            "discretas": disc[:20], "numericas": num[:20], "operativos": oper, "vinculo": vin}


def serie(filas: list, fin: str = "\n") -> bytes:
    return "".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + fin for x in filas).encode("utf-8")


def huella_derivada(nuevas_b: bytes, ref_b: bytes, campos=("segundos", "alcance_sha256")) -> dict:
    """Techos nuevos con los campos apartados repuestos de su fila de referencia y serializados como el trabajador (persistir: sort_keys,
    ensure_ascii=False, una fila por línea en modo texto, con el fin de línea de los bytes nuevos). La huella se compara con los BYTES del
    producto de referencia (no con una reserialización)."""
    fin = "\r\n" if b"\r\n" in nuevas_b else "\n"
    nuevas = [json.loads(x) for x in nuevas_b.decode("utf-8").splitlines() if x.strip()]
    dr = {x["clave_transformada_sha256"]: x for x in (json.loads(y) for y in ref_b.decode("utf-8").splitlines() if y.strip())}
    rep = [dict(x, **{c: dr[x["clave_transformada_sha256"]][c] for c in campos if c in dr.get(x["clave_transformada_sha256"], {})}) for x in nuevas]
    der = serie(rep, fin)
    return {"campos_repuestos": list(campos), "fin_de_linea": "CRLF" if fin == "\r\n" else "LF", "sha256": sha(der),
            "referencia_sha256_de_sus_bytes": sha(ref_b), "igual": der == ref_b}


def g_ok(x: dict, t: dict | None) -> bool:
    """G_coord = C2' − K1 con el techo COMPLETO de su clave (regla de conexion_coord_cert.comparaciones), recompuesta en binary64."""
    c2, k1 = (t or {}).get("C_2"), x.get("K1_reutilizado")
    return (t or {}).get("estado") == "complete" and isinstance(c2, float) and isinstance(k1, float) and x.get("C2_coord") == c2 and x.get("G_coord") == c2 - k1


def comprobar_validacion(val: dict | None, nueva: Path, rb: bytes, res: dict, tarea: str) -> list:
    if val is None:
        return ["VALIDACION_AUSENTE"]
    mot = []
    if val.get("comando") != "fam07-validar" or val.get("origen") != rel(nueva) or val.get("resultado_sha256") != sha(rb) \
            or val.get("productos_sha256") != productos_de(nueva, res) or val.get("tarea") != tarea:
        mot.append("VALIDACION_DE_OTROS_BYTES")
    if val.get("aceptada") is not True:
        mot.append("VALIDACION_NO_ACEPTADA: %s" % ((val.get("veredicto") or {}).get("fallos") or [])[:3])
    return mot


def comparar(tarea: str, nueva: Path, validacion: Path) -> dict:
    """fam07-comparar --tarea L1-COORD-R*: salida de fam07-unidad (`nueva`) y su validación (fam07-validar) frente a la tarea aceptada rem124."""
    nueva = Path(nueva).resolve()
    raw, man = manifiesto()
    co = man["L1-COORD-REC"]
    mot = []
    ej = leer(nueva / "ejecucion.json") if (nueva / "ejecucion.json").is_file() else {}
    rb = (nueva / "resultado.json").read_bytes() if (nueva / "resultado.json").is_file() else b"{}"
    res = json.loads(rb)
    if ej.get("tarea") != tarea or res.get("tarea") != tarea or ej.get("etiqueta") != ETIQUETA:
        mot.append("SALIDA_DE_OTRA_TAREA_O_SIN_EJECUCION_FAM07: %s / %s" % (res.get("tarea"), ej.get("tarea")))
    mot += comprobar_validacion(leer(validacion) if Path(validacion).is_file() else None, nueva, rb, res, tarea)
    if res.get("estado") != "completa":
        mot.append("CALCULO_NO_COMPLETO: %s" % res.get("motivo"))
    ref_d = REF / tarea
    ref_rb = (ref_d / "resultado.json").read_bytes()
    ref_res = json.loads(ref_rb)
    if sha(ref_rb) != RESULTADO_ACEPTADO[tarea]:
        mot.append("REFERENCIA_ALTERADA_O_AJENA: resultado.json")
    hdec = sha_archivo(DATOS / DECLARACION)
    decl = {p["archivo"]: p for p in res.get("productos") or []}
    if sorted(decl) != sorted(PRODUCTOS):
        mot.append("PRODUCTOS_DISTINTOS: %s" % sorted(decl))
    objetos, deriv = {}, {}
    for n in PRODUCTOS:
        fref, fn = ref_d / "salida" / n, nueva / "salida" / n
        pref = next((p for p in ref_res["productos"] if p["archivo"] == n), {})
        if sha_archivo(fref) is None or sha_archivo(fref) != pref.get("sha256"):
            mot.append("REFERENCIA_ALTERADA_O_AJENA: %s" % n)
            continue
        d = decl.get(n)
        if d is None or sha_archivo(fn) != d.get("sha256"):
            mot.append("PRODUCTO_AUSENTE_O_ALTERADO: %s" % n)
            continue
        ref_l = [x for x in fref.read_text(encoding="utf-8").splitlines() if x.strip()]
        nue_l = [x for x in fn.read_text(encoding="utf-8").splitlines() if x.strip()]
        es_techo = n == PRODUCTOS[0]
        o = comparar_filas(nue_l, ref_l, CLAVE_FILA[n], OPERATIVOS.get(n, ()),
                           {None: {VINCULO: (res.get("alcance_sha256"), ref_res.get("alcance_sha256"))}} if es_techo else None)
        c = o["cobertura"]
        if c["faltan"] or c["ajenas"] or c["duplicadas"] or not c["mismo_orden"] or c["filas_nuevas"] != c["filas_referencia"] or not ref_l:
            mot.append("COBERTURA_DISTINTA (CR-DISCRETOS): %s" % n)
        if o["n_discretas"]:
            mot.append("DIFERENCIA_DISCRETA (CR-DISCRETOS, precedencia): %s %s" % (n, [x["puntero"] for x in o["discretas"][:4]]))
        if o["n_numericas"]:
            mot.append("DIFERENCIA_NUMERICA (CR-HASH-CANONICO): %s %s" % (n, [x["puntero"] for x in o["numericas"][:4]]))
        if es_techo:
            v = o["vinculo"]
            if not (v["filas"] == v["nueva_ligada"] == v["referencia_ligada"] == c["filas_referencia"]) or res.get("alcance_sha256") != hdec \
                    or ref_res.get("alcance_sha256") != ALCANCE[1]:
                mot.append("VINCULO_ROTO: alcance_sha256 (nueva = declaración de ejecución limpia; referencia = alcance histórico)")
            deriv["huella_derivada_de_los_techos"] = huella_derivada(fn.read_bytes(), fref.read_bytes())
            if not deriv["huella_derivada_de_los_techos"]["igual"] and not o["n_discretas"] and not o["n_numericas"]:
                mot.append("HUELLA_DERIVADA_DISTINTA: techos")
        elif not o["lineas_identicas"]:
            mot.append("BYTES_DISTINTOS: %s" % n)
        o["filas_decl"] = d.get("filas")
        objetos[n] = o
    nuevas_t = leer_jsonl(nueva / "salida" / PRODUCTOS[0]) if (nueva / "salida" / PRODUCTOS[0]).is_file() else []
    nuevas_c = leer_jsonl(nueva / "salida" / PRODUCTOS[1]) if (nueva / "salida" / PRODUCTOS[1]).is_file() else []
    cel = [c for c in co["celdas_afectadas"] if c["clave_transformada_sha256"] in co["tareas"][tarea]]
    por_t = {t["clave_transformada_sha256"]: t for t in nuevas_t}
    deriv["techos"] = {t["clave_transformada_sha256"]: {"estado": t.get("estado"), "error_kind": t.get("error_kind"), "garantia": t.get("garantia"),
                                                         "error_normalizado": t.get("error_normalizado"), "error_R": t.get("error_R"),
                                                         "cierre_por_escala": t.get("cierre_por_escala"), "final_n": t.get("final_n")} for t in nuevas_t}
    deriv["certificados_y_cerrados"] = sum(1 for t in nuevas_t if t.get("estado") == "complete" and t.get("error_kind") == "certified_bound"
                                           and t.get("garantia") == "ieee754_binary64_rn" and (t.get("error_normalizado") or 1) <= 1e-7
                                           and (t.get("cierre_por_escala") or {}).get("normalizada") is True)
    deriv["comparaciones_G_igual_C2_menos_K1"] = sum(1 for x in nuevas_c if g_ok(x, por_t.get(x.get("clave_transformada_sha256"))))
    deriv["cobertura"] = {"claves": sorted(por_t) == sorted(co["tareas"][tarea]), "celdas": sorted((x["unidad"], x["cell_id"]) for x in nuevas_c)
                          == sorted((c["unidad"], c["cell_id"]) for c in cel), "techos": len(nuevas_t), "comparaciones": len(nuevas_c)}
    if not (deriv["certificados_y_cerrados"] == len(co["tareas"][tarea]) == len(nuevas_t) and deriv["comparaciones_G_igual_C2_menos_K1"] == len(cel) == len(nuevas_c)
            and deriv["cobertura"]["claves"] and deriv["cobertura"]["celdas"]):
        mot.append("COBERTURA_CERTIFICADOS_O_CLASIFICACION_INCOMPLETOS")
    rr = {}
    for k in ("tarea", "modo", "sintetico", "estado", "motivo", "tope_efectivo_s"):
        rr[k] = {"nueva": res.get(k), "referencia": ref_res.get(k), "igual": res.get(k) == ref_res.get(k)}
        if not rr[k]["igual"]:
            mot.append("RESULTADO_DISTINTO: %s" % k)
    ident = {"manifiesto_sha256": res.get("manifiesto_sha256") == ref_res.get("manifiesto_sha256") == MANIFIESTO[1],
             "codigo_sha256": res.get("codigo_sha256") == ref_res.get("codigo_sha256") == {n: CODIGO[n] for n in ("tarea_lote.py", "conexion_coord_cert.py")},
             "nucleo_c0": (ej.get("nucleo") or {}).get("identidad") == F5.C0_IDENTIDAD,
             "producto_de_comparaciones_igual": (decl.get(PRODUCTOS[1]) or {}).get("sha256") == next(p["sha256"] for p in ref_res["productos"] if p["archivo"] == PRODUCTOS[1])}
    if not all(ident.values()):
        mot.append("IDENTIDAD_DISTINTA: %s" % [k for k, v in ident.items() if not v])
    vh = json.loads((ref_d / "validacion_stdout.txt").read_text(encoding="utf-8"))
    vn = (leer(validacion) if Path(validacion).is_file() else {}).get("veredicto") or {}
    deriv["validacion_frente_a_la_historica"] = {
        "iguales_salvo_huellas_propias": {k: v for k, v in vn.items() if k not in ("resultado_sha256", "productos_sha256")}
        == {k: v for k, v in vh.items() if k not in ("resultado_sha256", "productos_sha256")},
        "huellas_propias": vn.get("resultado_sha256") == sha(rb) and vn.get("productos_sha256") == productos_de(nueva, res)}
    if not all(deriv["validacion_frente_a_la_historica"].values()):
        mot.append("VALIDACION_DISTINTA_DE_LA_HISTORICA")
    return {"comando": "fam07-comparar", "tarea": tarea, "operacion": "F07-RECALCULO", "regla": "COMPARACION-FAM07-v1 (src/fam07.py)",
            "criterios": ["CR-HASH-CANONICO (mismo perfil de entorno y mismo núcleo C0; exacta)", "CR-DISCRETOS (precedencia)",
                          "OPERATIVO segundos y VINCULO alcance_sha256 (apartados, visibles)"],
            "no_aplicado": "CR-OBJETO-OTRO-ENTORNO: no es otro entorno; la tolerancia interna del validador no es una tolerancia de reproducción",
            "referencia": {"ejecucion": rel(ref_d), "resultado_sha256": sha(ref_rb), "productos": {p["archivo"]: p["sha256"] for p in ref_res["productos"]}},
            "nueva": rel(nueva), "validacion": rel(Path(validacion)), "objetos": objetos, "resultado": rr, "identidades": ident, "derivados": deriv,
            "operativos": {"pared_s": {"nueva": res.get("pared_s"), "referencia": ref_res.get("pared_s")},
                           "segundos_por_techo": {"nueva": {t["clave_transformada_sha256"]: t.get("segundos") for t in nuevas_t},
                                                  "referencia": {t["clave_transformada_sha256"]: t.get("segundos") for t in leer_jsonl(ref_d / "salida" / PRODUCTOS[0])}}},
            "estado": {"reproduccion": "aceptada" if not mot else "no_aceptada", "motivos": mot}}


# ================================================================================================ ensamblado
def ensamblar(salida: Path, entradas: dict) -> dict:
    """fam07-ensamblar: ensamblar_coord.py (ENSAMBLADOR-ENTRADAS-v1) con una carpeta declarada por tarea: «guardado» = la tarea aceptada
    rem124 (bytes guardados, autenticados por el catálogo) o una carpeta de fam07-unidad. El ensamblador revalida cada tarea con
    validar_tarea y construye las 1.532 comparaciones desde las fuentes autenticadas; nunca lee el ensamblado de referencia. Una tarea sin
    carpeta no se sustituye: el ensamblado queda rechazado."""
    T0 = time.time()
    rastro = F1().Rastro()
    raw, man = manifiesto()
    need(set(entradas) <= set(TAREAS), "TAREA_FUERA_DE_LA_PARTICION: %s" % sorted(set(entradas) - set(TAREAS)))
    malos = fuentes_alteradas("ensamblado")
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam07.json; no se ensambla): %s" % malos[:5])
    dirs, origen = {}, {}
    for t in TAREAS:
        if t not in entradas:
            origen[t] = {"procedencia": "ausente", "nota": "sin carpeta declarada: no se sustituye por la referencia"}
            continue
        v = entradas[t]
        if v == GUARDADO:
            d = REF / t
            res = leer(d / "resultado.json")
            need(sha_archivo(d / "resultado.json") == RESULTADO_ACEPTADO[t]
                 and all(sha_archivo(d / "salida" / p["archivo"]) == p["sha256"] for p in res["productos"]), "TAREA_GUARDADA_ALTERADA_O_AJENA: %s" % t)
            origen[t] = {"procedencia": "guardada", "naturaleza": "tarea histórica aceptada rem124 (bytes guardados; no se recalcula ni acredita cálculo nuevo)",
                         "carpeta": rel(d)}
        else:
            d = Path(v).resolve()
            ej = leer(d / "ejecucion.json") if (d / "ejecucion.json").is_file() else None
            need(ej is not None and ej.get("etiqueta") == ETIQUETA, "CARPETA_SIN_EJECUCION_FAM07: %s" % t)
            origen[t] = {"procedencia": "nueva", "naturaleza": "salida de fam07-unidad en la base limpia (cálculo nuevo)", "carpeta": rel(d),
                         "tarea_de_su_ejecucion": ej.get("tarea"), "exito_declarado": ej.get("exito")}
        dirs[t] = d
    proc = {o["procedencia"] for o in origen.values()}
    naturaleza = (REGENERACION if proc == {"guardada"} else NUEVA if proc == {"nueva"} else MIXTA if proc == {"guardada", "nueva"}
                  else "incompleta: faltan tareas (no se sustituyen por referencias)")
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    sal = salida.resolve()
    ent = {"tareas": {t: str(d) for t, d in dirs.items()}, "directorio": {t: rel(d) for t, d in dirs.items()},
           "lanzamiento": {t: rel(d.parent) for t, d in dirs.items()}, "salida": str(sal)}
    a0 = time.time()
    rc, ult, stdout, exc = guion("ensamblar_coord.py", [BASE, DATOS / MANIFIESTO[0], DATOS / ANEXO[0], json.dumps(ent, ensure_ascii=False)])
    t_ens = round(time.time() - a0, 2)
    (sal / "ensamblado_stdout.txt").write_text(stdout, encoding="utf-8")
    informe = rastro.informe()
    (sal / "archivos_leidos.json").write_bytes((json.dumps(informe, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    E = sal / ENSAMBLADO
    ens = leer(E / "ENSAMBLADO.json") if (E / "ENSAMBLADO.json").is_file() else {}
    co = man["L1-COORD-REC"]
    ej = {"comando": "fam07-ensamblar", "naturaleza": naturaleza, "etiqueta": ETIQUETA, "manifiesto_sha256": sha(raw), "entradas": origen,
          "reutilizaciones": {"techos": len(co["claves_reutilizadas"]), "procedencia": "históricas: fuentes rem112/rem120 autenticadas por el manifiesto "
                              "(convergence_estimate; no cuentan como cálculo nuevo)", "fuentes": sorted(RUTAS_FUENTES.values())},
          "acredita": {REGENERACION: "el ensamblado documental sobre las tres tareas guardadas y las reutilizaciones autenticadas; NO acredita F07-RECALCULO",
                       MIXTA: "la conexión de las tareas nuevas al ensamblador; las tareas guardadas NO se han ejecutado aquí",
                       NUEVA: "el ensamblado sobre las tres tareas calculadas en la base limpia"}.get(naturaleza, "nada (ensamblado incompleto)"),
          "ensamblador": {"archivo": "nucleo_s6/coord/ensamblar_coord.py", "sha256": CODIGO["ensamblar_coord.py"],
                          "adaptacion": [x[0] for x in SUSTITUCIONES["ensamblar_coord.py"]], "adaptado_sha256": sha(adaptado("ensamblar_coord.py").encode("utf-8"))},
          "rc": rc, "veredicto": ult, "excepcion": exc, "dictamen": ens.get("dictamen"), "aceptada": ens.get("aceptada") is True and rc == 0 and exc is None,
          "productos": {n: sha_archivo(E / n) for n in PRODUCTOS_ENS + ("ENSAMBLADO.json",)},
          "tiempos_s": {"ensamblado": t_ens, "total": round(time.time() - T0, 2)}, "lecturas": lecturas(informe)}
    ej["exito"] = ej["aceptada"] and not ej["lecturas"]["ensamblado_esperado_leido"]
    (sal / "ejecucion.json").write_bytes(json.dumps(ej, ensure_ascii=False, indent=1, sort_keys=True, default=str).encode("utf-8") + b"\n")
    return ej


def comparar_ensamblado(nueva: Path) -> dict:
    """fam07-comparar --tarea ENSAMBLADO: salida de fam07-ensamblar frente al ensamblado aceptado rem124 (todas las filas y recuentos)."""
    nueva = Path(nueva).resolve()
    mot = []
    ej = leer(nueva / "ejecucion.json") if (nueva / "ejecucion.json").is_file() else {}
    if ej.get("comando") != "fam07-ensamblar" or ej.get("etiqueta") != ETIQUETA:
        mot.append("SALIDA_SIN_EJECUCION_DE_FAM07_ENSAMBLAR")
    E, RE = nueva / ENSAMBLADO, REF / ENSAMBLADO
    ens = leer(E / "ENSAMBLADO.json") if (E / "ENSAMBLADO.json").is_file() else {}
    ref_ens = leer(RE / "ENSAMBLADO.json")
    if {n: sha_archivo(RE / n) for n in ENS_ACEPTADO} != ENS_ACEPTADO:
        mot.append("REFERENCIA_DEL_ENSAMBLADO_ALTERADA_O_AJENA")
    if not (ens.get("aceptada") is True and ens.get("dictamen") == "completa_validada" and ej.get("aceptada") is True):
        mot.append("ENSAMBLADO_NO_ACEPTADO: %s" % (ens.get("fallos") or [])[:3])
    huellas = {n: {"declarada": (ens.get("productos") or {}).get(n), "de_sus_bytes": sha_archivo(E / n)} for n in PRODUCTOS_ENS}
    if any(v["declarada"] != v["de_sus_bytes"] or v["declarada"] is None for v in huellas.values()):
        mot.append("HUELLA_DERIVADA_DISTINTA_DE_SUS_BYTES (ENSAMBLADO.json/productos)")
    nuevas_t = [t for t, o in (ej.get("entradas") or {}).items() if o.get("procedencia") == "nueva"]
    vin_t = {}
    for t in nuevas_t:
        d = BASE / ej["entradas"][t]["carpeta"]
        r_ = leer(d / "resultado.json")
        vin_t[t] = {"/tareas/%s/resultado_sha256" % t: (sha_archivo(d / "resultado.json"), RESULTADO_ACEPTADO[t]),
                    "/tareas/%s/productos/coord_techos_rec.jsonl" % t: (sha_archivo(d / "salida" / PRODUCTOS[0]),
                                                                       ref_ens["tareas"][t]["productos"]["coord_techos_rec.jsonl"]),
                    "/tareas/%s/alcance_sha256" % t: (r_.get("alcance_sha256"), ALCANCE[1]), "_alcance": r_.get("alcance_sha256")}
    objetos = {}
    for n in PRODUCTOS_ENS:
        ref_l = [x for x in (RE / n).read_text(encoding="utf-8").splitlines() if x.strip()]
        nue_l = [x for x in (E / n).read_text(encoding="utf-8").splitlines() if x.strip()] if (E / n).is_file() else []
        es_techo = n == "coord_techos_ensamblados.jsonl"
        vinc = None
        if es_techo and nuevas_t:
            vinc = {(k,): {VINCULO: (vin_t[t]["_alcance"], ALCANCE[1])} for t in nuevas_t for k in leer(BASE / "datos/fam07" / MANIFIESTO[0])["L1-COORD-REC"]["tareas"][t]}
        o = comparar_filas(nue_l, ref_l, CLAVE_FILA[n], OPERATIVOS.get(n, ()) if nuevas_t else (), vinc)
        if es_techo and nuevas_t:
            # en las filas de tareas guardadas, «segundos» y alcance deben ser idénticos: se comparan aparte
            guard = {(x["clave_transformada_sha256"],) for x in map(json.loads, ref_l) if x["tarea"] not in nuevas_t}
            o["operativos_de_tareas_guardadas_distintos"] = [x for x in o["operativos"] if tuple(x["fila"]) in guard and x["nueva"] != x["referencia"]]
            if o["operativos_de_tareas_guardadas_distintos"]:
                mot.append("OPERATIVO_DISTINTO_EN_TAREA_GUARDADA: %s" % n)
            v = o["vinculo"]
            nt = sum(len(leer(BASE / "datos/fam07" / MANIFIESTO[0])["L1-COORD-REC"]["tareas"][t]) for t in nuevas_t)
            if not (v["filas"] == v["nueva_ligada"] == v["referencia_ligada"] == nt):
                mot.append("VINCULO_ROTO: alcance_sha256 de las tareas nuevas")
            o["huella_derivada"] = huella_derivada((E / n).read_bytes(), (RE / n).read_bytes())
            if not o["huella_derivada"]["igual"] and not o["n_discretas"] and not o["n_numericas"]:
                mot.append("HUELLA_DERIVADA_DISTINTA: %s" % n)
        c = o["cobertura"]
        if c["faltan"] or c["ajenas"] or c["duplicadas"] or not c["mismo_orden"] or c["filas_nuevas"] != c["filas_referencia"] or not ref_l:
            mot.append("COBERTURA_DISTINTA (CR-DISCRETOS): %s" % n)
        if o["n_discretas"]:
            mot.append("DIFERENCIA_DISCRETA (CR-DISCRETOS, precedencia): %s %s" % (n, [x["puntero"] for x in o["discretas"][:4]]))
        if o["n_numericas"]:
            mot.append("DIFERENCIA_NUMERICA (CR-HASH-CANONICO): %s %s" % (n, [x["puntero"] for x in o["numericas"][:4]]))
        if not o["lineas_identicas"] and not (es_techo and nuevas_t):
            mot.append("BYTES_DISTINTOS: %s" % n)
        objetos[n] = o
    # ENSAMBLADO.json: todo igual salvo directorio/lanzamiento por tarea (ubicación; se muestran) y, en tareas nuevas, los vínculos a sus bytes
    hn, hr = F5.hojas(ens), F5.hojas(ref_ens)
    ubic, disc, vis = [], [], []
    vin_all = {p: v for t in nuevas_t for p, v in vin_t[t].items() if p.startswith("/")}
    if nuevas_t:
        vin_all["/productos/coord_techos_ensamblados.jsonl"] = (sha_archivo(E / "coord_techos_ensamblados.jsonl"), ENS_ACEPTADO["coord_techos_ensamblados.jsonl"])
    for p in sorted(set(hn) | set(hr)):
        a, b = hn.get(p, "<ausente>"), hr.get(p, "<ausente>")
        if re.fullmatch(r"/tareas/[^/]+/(directorio|lanzamiento)", p):
            ubic.append({"puntero": p, "nueva": a, "referencia": b})
            continue
        if p in vin_all:
            vis.append({"puntero": p, "nueva_ligada": a == vin_all[p][0], "referencia_ligada": b == vin_all[p][1]})
            continue
        if json.dumps(a) != json.dumps(b):
            disc.append({"puntero": p, "nueva": a, "referencia": b})
    if disc:
        mot.append("ENSAMBLADO_JSON_DISTINTO: %s" % [x["puntero"] for x in disc[:4]])
    if not all(x["nueva_ligada"] and x["referencia_ligada"] for x in vis) or len(vis) != len(vin_all):
        mot.append("VINCULO_ROTO: ENSAMBLADO.json de las tareas nuevas")
    filas = leer_jsonl(E / "coord_comparacion_ensamblada.jsonl") if (E / "coord_comparacion_ensamblada.jsonl").is_file() else []
    l1 = {(x["unidad"], x["cell_id"]) for x in leer_jsonl(BASE / PREVIAS[0])}
    ks = {(x["unidad"], x["cell_id"]) for x in filas}
    rec = {"filas": len(filas), "por_origen": dict(Counter(x["origen_techo"] for x in filas)),
           "con_techo_incompleto": sum(1 for x in filas if x["estado_techo"] != "complete" or x["G_coord"] is None),
           "G_igual_C2_menos_K1": sum(1 for x in filas if x["G_coord"] == x["C2_coord"] - x["K1_reutilizado"]),
           "previas_192_disjuntas": not (ks & l1), "celdas_declaradas_total": len(ks | l1),
           "fuera_del_lote": (ens.get("ensamblado") or {}).get("fuera_del_lote")}
    if not (rec["filas"] == 1532 and rec["por_origen"] == {"recalculado": 30, "reutilizado": 1502} and rec["con_techo_incompleto"] == 0
            and rec["G_igual_C2_menos_K1"] == 1532 and rec["previas_192_disjuntas"] and rec["celdas_declaradas_total"] == 1724 and len(rec["fuera_del_lote"] or {}) == 2):
        mot.append("RECUENTOS_DISTINTOS")
    so = (nueva / "ensamblado_stdout.txt").read_text(encoding="utf-8").strip().splitlines()
    sr = (REF / "ensamblado_stdout.txt").read_text(encoding="utf-8").strip().splitlines()
    stdout_igual = bool(so) and json.loads(so[-1]) == json.loads(sr[-1])
    if not stdout_igual:
        mot.append("VEREDICTO_DEL_ENSAMBLADOR_DISTINTO")
    return {"comando": "fam07-comparar", "tarea": "ENSAMBLADO", "naturaleza": ej.get("naturaleza"), "acredita": ej.get("acredita"),
            "entradas": ej.get("entradas"), "regla": "COMPARACION-FAM07-v1 (src/fam07.py)",
            "referencia": {"ensamblado": rel(RE), "productos": ENS_ACEPTADO, "ENSAMBLADO.json": "proyección del catálogo (original 4ef5820d…)"},
            "nueva": rel(nueva), "objetos": objetos, "huellas_derivadas": huellas,
            "ensamblado_json": {"ubicacion": ubic, "vinculos": vis, "discretas": disc[:20], "n_discretas": len(disc)},
            "recuentos": rec, "veredicto_del_ensamblador_igual": stdout_igual,
            "bytes_identicos_a_la_referencia": {n: sha_archivo(E / n) == ENS_ACEPTADO[n] for n in PRODUCTOS_ENS},
            "estado": {"reproduccion": "aceptada" if not mot else "no_aceptada", "motivos": mot}}


# ================================================================================================ receta completa (sin ejecutarla)
def receta() -> dict:
    raw, man = manifiesto()
    co = man["L1-COORD-REC"]
    d = "salidas/fam07/<ejecucion>"
    pasos = [{"paso": "comprobar", "ordenes": ["reproducir.py fam07-comprobar --salida %s/comprobar.json (sin cálculo científico)" % d]}]
    for t in TAREAS:
        pasos.append({"paso": t, "operacion": "F07-RECALCULO", "claves": co["tareas"][t],
                      "celdas": sum(1 for c in co["celdas_afectadas"] if c["clave_transformada_sha256"] in co["tareas"][t]),
                      "ordenes": ["reproducir.py fam07-unidad --tarea %s --salida %s/%s" % (t, d, t),
                                  "reproducir.py fam07-validar --nueva %s/%s --salida %s/%s.validacion.json" % (d, t, d, t),
                                  "reproducir.py fam07-comparar --tarea %s --nueva %s/%s --validacion %s/%s.validacion.json --salida %s/%s.comparacion.json"
                                  % (t, d, t, d, t, d, t)]})
    pasos.append({"paso": "ensamblado", "operacion": "F07-RECALCULO + F07-REUTILIZADAS (ensamblado sobre las tres salidas nuevas)",
                  "ordenes": ["reproducir.py fam07-ensamblar %s --salida %s/ensamblado" % (" ".join("--entrada %s=%s/%s" % (t, d, t) for t in TAREAS), d),
                              "reproducir.py fam07-comparar --tarea ENSAMBLADO --nueva %s/ensamblado --salida %s/ensamblado.comparacion.json" % (d, d)]})
    return {"comando": "fam07-receta", "estado": "receta completa preparada; NO ejecutada (el cálculo completo pertenece al Paso 3)", "manifiesto_sha256": sha(raw),
            "orden": list(TAREAS) + ["ensamblado"], "pasos": pasos,
            "cobertura": {"techos_nuevos": len(co["claves_recalculadas"]), "comparaciones_dependientes": len(co["celdas_afectadas"]),
                          "reutilizados_previstos": len(co["claves_reutilizadas"]), "comparaciones_ensambladas": co["celdas_total"],
                          "previas_aparte": co["comparaciones_previas_aceptadas"]["filas"], "fuera_del_lote": sorted(co["fuera_del_lote"])},
            "ejecucion": {"procesos": "una tarea a la vez, sin reintentos", "tope_trabajo_s": F5.TOPE_TRABAJO, "reloj_interno_s": F5.TOPE_TRABAJO - F5.HOLGURA,
                          "tope_validacion_s": F5.TOPE_VALIDACION,
                          "lanzador": "supervisor que termina el árbol de procesos (el mismo del piloto), con el tope de trabajo como límite externo",
                          "parada": "si una tarea no queda completa, validada y aceptada, la siguiente no se lanza ni se ensambla",
                          "ensamblado": "solo con las tres carpetas nuevas; una tarea faltante no se sustituye por su referencia (el ensamblador la rechaza)",
                          "duracion": "sin estimación: un piloto no la permite"},
            "F1": {"reutilizado": ["manifiesto B, anexo y partición (la selección no se re-ejecuta)",
                                   "20 techos reutilizados (12 rem112 + 8 rem120), autenticados en su fuente con su garantía convergence_estimate",
                                   "manifiesto del lote 2 (1.532 celdas, K1 sin cambio) y comparaciones rem120 (cotejo de las 1.502 reutilizadas)",
                                   "núcleo C0 (src/paper2b, inventario de su instalación)"],
                   "se_genera_de_nuevo": ["6 techos certificados (rama y cota, cierre normalizado <= 1e-7) y sus 30 comparaciones",
                                          "ensamblado de las 1.532 comparaciones sobre las tres tareas nuevas"],
                   "verificado_aparte": ["192 comparaciones previas (lote 1), disjuntas de las 1.532: 1.724 celdas"],
                   "solo_para_comparar": ["tareas y ensamblado aceptados rem124 (= objetos del catálogo FAM07)"],
                   "no_cubre": ["COL-2024p (pendiente, no NA)", "FAM08"]},
            "pilotos": leer(DATOS / "pilotos.json") if (DATOS / "pilotos.json").is_file() else None}
