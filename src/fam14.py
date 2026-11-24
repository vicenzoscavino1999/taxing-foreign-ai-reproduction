"""FAM14 (conciliaciones G/N rem174, localización §18.7 y adopción rem176).

Operaciones del catálogo (las cuatro etapas de la orden única fam14-reproducir):
- F14-GN-REGEN (regeneración documental; sin modelo): etapa GN_REGEN. pares_gn_rem174.py (U62) corre como __main__ sobre el mapa de impacto
  rem117, los certificados aceptados en rem118 (§3), la conciliación E4 rem121 aceptada por L_rem122 y los manifiestos LOTE2/LOTE2E4, y escribe
  PARES_GN_REM174.json, COBERTURA_GN_REM174.json y FUENTES_BLOQUE_A_REM174.json. Validación independiente, SIN referencias: la ligadura G/N
  de verificar_relaciones_rem175.py (U63, validador vigente) re-deriva pares y cobertura desde las mismas entradas y juzga las salidas nuevas
  (_gn_pares y _gn_cobertura deben quedar sin hallazgos); además, recuentos propios desde las filas y la ligadura de cada lado con su registro.
  Después, la comparación fila a fila (ambos lados) con la referencia aceptada.
- F14-GN (verificación de integridad): etapa GN. La cobertura aceptada 3ef08df8…, la MISMA copia que sirve de referencia a la regeneración.
- F14-187 (verificación de integridad): etapa LOC_187. Proyección pública 98bffc5d… del registro §18.7; identidad histórica 429dd087….
- F14-176 (verificación de integridad): etapa ADOPCION_176. Derivado público, con huella propia, de REFERENCIA_ADOPCION_REM176.json (a975e3f9…).

Adaptaciones (no cambian fórmulas, claves, criterios ni la serialización; cada original se sustituye una sola vez y se autentica por su huella):
- GUION-v1: U62 corre desde sus bytes con SUSTITUCIONES como __main__ (sys.argv = [U62, <raíz>, <etapa>, salida_1]), en el proceso, con
  cwd = la base. La raíz histórica R es nucleo_s6/raiz (espejo de las rutas que lee).
- BLOQUE-U63-v1: de U63 se ejecuta solo la ligadura G/N (desde «_INVF = {}» hasta antes de «# ---- localización §18.7») con SUSTITUCIONES_U63;
  el resto de U63 juzga productos de rem175 que FAM14 no regenera (matriz, enlaces, registro §18.7 contra su corpus, correspondencia rem174).
- RAIZ-PROYECTADA-v1: las raíces de fuentes rem174 (196b4e24…) y rem175 (ef581a7a…) se leen de su resumen sin rutas (datos/fam14/autoridad):
  sección source_files_sha256 restringida a las fuentes que lee la ruta, con clave relativa a la raíz.
- LIBROS-PROYECTADOS-v1: dictamen rem118 (l.11 y l.32), certificados rem118 (filas de las unidades del mapa) y L_rem122 (inventory_sha256),
  de sus resúmenes ligados a la huella del libro.
- LECTURA-PAQUETE-v1: la conciliación E4 (referencias/fam06) y los manifiestos (datos/fam05, datos/fam06) se leen de su copia ya en el paquete,
  con la huella de su miembro histórico; las claves de FUENTES_BLOQUE_A son relativas a la raíz.
- HUELLA-SANEADA-v1: el mapa rem117 se distribuye como proyección (un marcador en nucleo_corregido_src, campo que no lee ningún código); al
  autenticarlo contra el inventario rem117 y las raíces, su huella y su tamaño son los del original declarado en fuentes_fam14.json.
"""
from __future__ import annotations

import builtins
import contextlib
import datetime as dt
import importlib.util
import io
import json
import os
import re
import sys
import time
import traceback
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
sha, sha_archivo, leer, rel, F1 = F5.sha, F5.sha_archivo, F5.leer, F5.rel, F5.F1
ETIQUETA = "REPRODUCCION LIMPIA FAM14 NO OFICIAL"
RAIZ = BASE / "nucleo_s6/raiz"
DATOS = BASE / "datos/fam14"
REF = BASE / "referencias/fam14"
A174 = "paso4_supremos_gn_auditoria_desde_rem174"
A175 = "paso4_correcciones_extension_global_desde_rem175"
U62 = "nucleo_s6/raiz/tmp/%s/bloque_a/pares_gn_rem174.py" % A174
U63 = "nucleo_s6/raiz/tmp/%s/verificacion/verificar_relaciones_rem175.py" % A175
ORIGINAL = {U62: "01653ca6c88a50e021728bd09f527c6f74873ccf519b528d04e0e5958dd92c70", U63: "d0040eb622d83350373988a3f1c278e6116e00a10270536ff272bb5d497fe872"}
MAPA = "nucleo_s6/raiz/tmp/paso4_impacto_certificados_desde_rem117/impacto/MAPA_IMPACTO_REM117.json"
COB_REF, PARES_REF = "referencias/fam14/COBERTURA_GN_REM174.json", "referencias/fam14/PARES_GN_REM174.json"
PARES_ACEPTADO = "c6a3ee7a895bfb3b564db1e54d0eab09ae3ed31c4b28bff6a5f0004c23865e3f"   # miembro del inventario rem174 d35d4690… (cotejado en la extracción)
LOC = "datos/fam14/187/REGISTRO_LOCALIZACION_18_7_REM174.json"
ADOP = "datos/fam14/176/REFERENCIA_ADOPCION_REM176.publica.json"
ETAPAS = ("GN_REGEN", "GN", "LOC_187", "ADOPCION_176")
OPERACION_DE = {"GN_REGEN": "F14-GN-REGEN", "GN": "F14-GN", "LOC_187": "F14-187", "ADOPCION_176": "F14-176"}
OBJETO_DE = {"GN": COB_REF, "LOC_187": LOC, "ADOPCION_176": ADOP}      # lo que juzga cada etapa de integridad
PROHIBIDAS = ("referencias/fam14/",)                                     # ninguna etapa ni validación las lee, salvo su propio objeto (GN)
JUZGADOS = ("referencias/fam14/", "datos/fam14/187/", "datos/fam14/176/")
ADAPTACIONES = ("GUION-v1", "BLOQUE-U63-v1", "RAIZ-PROYECTADA-v1", "LIBROS-PROYECTADOS-v1", "LECTURA-PAQUETE-v1", "HUELLA-SANEADA-v1")
NATURALEZA = {"GN_REGEN": "regeneración documental: pares_gn_rem174 (U62) sobre el mapa rem117, los certificados rem118, la conciliación E4 rem121 y LOTE2/LOTE2E4",
              "GN": "verificación de integridad: cobertura aceptada (huella, tamaño y recuento desde sus filas)",
              "LOC_187": "verificación de integridad: proyección pública del registro §18.7 (huella, marcadores y contenido)",
              "ADOPCION_176": "verificación de integridad: derivado público de la referencia de adopción rem176 (huella, texto del autor y cinco transiciones)"}
# hechos aceptados que la validación vuelve a contar desde las filas (encargo FAM14; resumen rem174 aceptado)
ESPERADO_GN = {"filas": 391, "ambos": 8, "uno": 383, "ninguno": 0, "ambos_por_menu": {"d": 6, "f": 2}, "uno_por_menu": {"d": 172, "df": 110, "f": 101},
               "existentes": 8, "contrapartes_E4": 383}
SENTIDO_176 = {"C3.supremos_G_N": "satisfecho_en_alcance", "E4.supremos_G_N": "parcial_con_limite_adoptado", "EXP2.supremos_G_N": "parcial_con_limite_adoptado",
               "T4.valores_supremos": "parcial_con_limite_adoptado", "AUD.double_counting_audit_18_7": "limitacion_adoptada"}
NOMBRADOS_176 = ("C3", "E4", "Exp. 2", "T4", "§18.7")
HEX64 = re.compile(r"[0-9a-f]{64}")
UUID = re.compile(rb"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
ABSOLUTA = re.compile(rb"(?<![A-Za-z])[A-Za-z]:[\\/]|/[a-z]/Users/")


class Fam14Error(Exception):
    pass


def need(c, m: str):
    if not c:
        raise Fam14Error(m)


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _js(x) -> str:
    return json.dumps(x, ensure_ascii=False, sort_keys=True)


def _escribir(p: Path, doc):
    Path(p).write_bytes(json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True, default=str).encode("utf-8") + b"\n")


def _escribir_x(p: Path, doc):
    with Path(p).open("xb") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True, default=str).encode("utf-8") + b"\n")


def _sin_base(t):
    if t is None:
        return None
    for f in (str(BASE).replace("\\", "\\\\"), str(BASE), BASE.as_posix()):
        t = t.replace(f, "<base>")
    return t


def _dentro(p) -> Path:
    p = Path(p).resolve()
    need(p.is_relative_to(BASE.resolve()), "SALIDA_FUERA_DE_LA_BASE: %s" % p.name)
    return p


# ================================================================================================ fuentes
_CACHE: dict = {}


def fuentes() -> dict:
    if "fu" not in _CACHE:
        _CACHE["fu"] = leer(BASE / "fuentes_fam14.json")
    return _CACHE["fu"]


def _datos(n: str) -> dict:
    if n not in _CACHE:
        p = DATOS / n
        h = next((x["sha256"] for x in fuentes()["archivos"] if x["archivo"] == rel(p)), None)
        need(p.is_file() and h is not None and sha(p.read_bytes()) == h, "DATO_FAM14_AUSENTE_O_ALTERADO: %s" % rel(p))
        _CACHE[n] = json.loads(p.read_bytes())
    return _CACHE[n]


def original() -> dict:
    """Huella de una proyección saneada -> huella de su original (fuentes_fam14.json)."""
    return {x["sha256"]: x["sha256_original"] for x in fuentes()["saneado"] if x.get("restituye_el_original") is True}


def piezas() -> list:
    fu = fuentes()
    return fu["archivos"] + fu["reutilizados"]


def fuentes_alteradas(uso: str = "todo") -> list:
    """«calculo»: código y datos que lee la regeneración (sin referencias ni los objetos que juzgan las etapas de integridad); «todo»: todo."""
    return [x["archivo"] for x in piezas() if (uso == "todo" or not x["archivo"].startswith(JUZGADOS)) and sha_archivo(BASE / x["archivo"]) != x["sha256"]]


# ================================================================================================ sustituciones
SUSTITUCIONES = {
    U62: (("HUELLA-SANEADA-v1 (H)", "H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731\n",
           "H = _H14   # FAM14 HUELLA-SANEADA-v1: sha256; para la proyección declarada del mapa rem117, la huella de su original\n"),
          ("LECTURA-PAQUETE-v1 (lee)", "    b = Path(p).read_bytes()\n",
           "    b = _LEE14(p)   # FAM14 LECTURA-PAQUETE-v1: la ruta bajo la raíz o la pieza ya en el paquete (conciliación E4, manifiestos)\n"),
          ("LECTURA-PAQUETE-v1 (FUENTES)", '    FUENTES[str(p)] = {"sha256": h, "bytes": len(b)}\n',
           '    FUENTES[_CLAVE14(p)] = {"sha256": h, "bytes": _LEN14(b)}   # FAM14 LECTURA-PAQUETE-v1: clave relativa a la raíz\n'),
          ("HUELLA-SANEADA-v1 (miembro)", '    assert H(b) == e["sha256"] and len(b) == e["bytes"], ("MIEMBRO_NO_AUTENTICO", area, rel)\n',
           '    assert H(b) == e["sha256"] and _LEN14(b) == e["bytes"], ("MIEMBRO_NO_AUTENTICO", area, rel)   # FAM14 HUELLA-SANEADA-v1\n'),
          ("RAIZ-PROYECTADA-v1", ('RAIZ = json.loads(lee(W / "FUENTES_SUPREMOS_GN_AUDITORIA_PROD4_6_REM174.json"',
                                  '"196b4e24750d4bb1234a71d36a672b4056487c96b7300bd23c253c0e4db9e0ea"))\n'),
           'RAIZ = _RAIZ14("rem174", R)   # FAM14 RAIZ-PROYECTADA-v1: source_files_sha256 de la raíz rem174 (196b4e24…), fuentes leídas, bajo R\n'),
          ("LIBROS-PROYECTADOS-v1", ('D118 = lee(W / "review_20261029_rem118_dictamen.txt"', '"8b70afc6398664534451f3945fe3b93e9dfdca48190deaf887a70e92eca19608"))\n'),
           "D118, CERT, L122 = _LIBROS14()   # FAM14 LIBROS-PROYECTADOS-v1: dictamen rem118 (l.11 y l.32), certificados rem118 y L_rem122\n")),
}
BLOQUE_U63 = ("_INVF = {}", "# ---- localización §18.7")   # primera línea del bloque y primera línea que ya NO forma parte de él (cada una, única)
SUSTITUCIONES_U63 = (
    ("LIBROS-PROYECTADOS-v1", ('    d118 = fijada(WD / "review_20261029_rem118_dictamen.txt")', '    l122 = json.loads(fijada(WD / "review_20261029_rem122_E4_aceptada.json"))\n'),
     "    d118, cert, l122 = _LIBROS14()   # FAM14 LIBROS-PROYECTADOS-v1: dictamen rem118 (l.11 y l.32), certificados rem118 y L_rem122\n"),
    ("HUELLA-SANEADA-v1 (fijada)", "    if h is None or sha(b) != h:\n", "    if h is None or _H14(b) != h:   # FAM14 HUELLA-SANEADA-v1\n"),
    ("HUELLA-SANEADA-v1 (miembro_fijado)", '    if e.get("sha256") != sha(b) or e.get("bytes") != len(b):\n',
     '    if e.get("sha256") != _H14(b) or e.get("bytes") != _LEN14(b):   # FAM14 HUELLA-SANEADA-v1\n'))


def sha14(b: bytes) -> str:
    h = sha(b)
    return original().get(h, h)


def _sustituir(txt: str, subs, n: str) -> str:
    for i, a, b in subs:
        if isinstance(a, tuple):
            need(txt.count(a[0]) == 1 and txt.count(a[1]) == 1 and txt.index(a[0]) < txt.index(a[1]), "SUSTITUCION_NO_UNICA: %s %s" % (n, i))
            a = txt[txt.index(a[0]):txt.index(a[1]) + len(a[1])]
        need(txt.count(a) == 1, "SUSTITUCION_NO_UNICA: %s %s" % (n, i))
        txt = txt.replace(a, b)
    return txt


def _codigo(n: str) -> str:
    src = (BASE / n).read_bytes()
    need(sha14(src) == ORIGINAL[n], "CODIGO_FAM14_DISTINTO: %s" % n)
    txt = src.decode("utf-8")
    need("\r" not in txt, "FINALES_DE_LINEA_CRLF: %s" % n)
    return txt


def adaptado(n: str) -> str:
    """GUION-v1: bytes de <n> (autenticados por la huella de su original) con sus sustituciones (cada original, una sola vez)."""
    return _sustituir(_codigo(n), SUSTITUCIONES.get(n, ()), n)


def bloque_u63() -> tuple:
    """BLOQUE-U63-v1: (texto sustituido, primera línea, última línea) de la ligadura G/N de U63 (nivel de módulo; sin sangría que quitar)."""
    lin = _codigo(U63).splitlines(keepends=True)
    ia = [i for i, x in enumerate(lin) if x.rstrip("\n") == BLOQUE_U63[0]]
    ib = [i for i, x in enumerate(lin) if x.startswith(BLOQUE_U63[1])]
    need(len(ia) == 1 and len(ib) == 1 and ia[0] < ib[0], "BLOQUE_NO_UNICO: U63 ligadura G/N")
    return _sustituir("".join(lin[ia[0]:ib[0]]), SUSTITUCIONES_U63, "U63:LIGADURA-GN"), ia[0] + 1, ib[0]


def sustituciones_ok() -> dict:
    out = {}
    for k, f in ((U62, lambda: adaptado(U62)), ("U63:LIGADURA-GN", lambda: bloque_u63()[0])):
        try:
            compile(f(), k, "exec")
            out[k] = True
        except Exception as e:  # noqa: BLE001
            out[k] = _sin_base("%s: %s" % (type(e).__name__, e))[:200]
    return out


# ================================================================================================ ayudas inyectadas
def _orig_datos() -> dict:
    """HUELLA-SANEADA-v1: solo la proyección declarada del mapa rem117 (huella de la proyección -> huella y tamaño del original)."""
    return {x["sha256"]: (x["sha256_original"], x["bytes_original"]) for x in fuentes()["saneado"]
            if x["archivo"] == MAPA and x.get("restituye_el_original") is True}


def _h14(b: bytes) -> str:
    h = sha(b)
    return _orig_datos().get(h, (h, None))[0]


def _len14(b: bytes) -> int:
    return _orig_datos().get(sha(b), (None, len(b)))[1]


def _relraiz(p) -> str | None:
    try:
        return Path(p).resolve().relative_to(RAIZ.resolve()).as_posix()
    except ValueError:
        return None


def _lee14(p) -> bytes:
    """LECTURA-PAQUETE-v1: una ruta histórica bajo la raíz se lee de su copia en el espejo o, si es pieza reutilizada, de su sitio en el paquete."""
    a = {x["ruta_historica"]: x["archivo"] for x in fuentes()["reutilizados"]}.get(_relraiz(p))
    return (BASE / a).read_bytes() if a else Path(p).read_bytes()


def _clave14(p) -> str:
    r = _relraiz(p)
    return r if r is not None else Path(p).name


def _raiz14(nombre: str, R) -> dict:
    """RAIZ-PROYECTADA-v1: {"source_files_sha256": {<R>/<clave relativa>: huella}} de la raíz <nombre> (solo las fuentes que lee la ruta)."""
    f = _datos("autoridad/RAICES_FIJADAS.json")["raices"][nombre]
    return {"source_files_sha256": {(Path(R) / k).as_posix(): v for k, v in f["fijadas"].items()}}


def _libros14() -> tuple:
    """LIBROS-PROYECTADOS-v1: (líneas del dictamen rem118 con solo l.11 y l.32, certificados rem118, L_rem122)."""
    d = _datos("autoridad/D118_LINEAS.json")
    lineas = [""] * d["original"]["lineas_totales"]
    for k, v in d["lineas"].items():
        lineas[int(k) - 1] = v
    c = _datos("autoridad/CERT_REM118.json")
    return lineas, {"failures": c["failures"], "units": c["units"], "rows": c["rows"]}, {"inventory_sha256": _datos("autoridad/L122.json")["inventory_sha256"]}


def _ayudas() -> dict:
    return {"_H14": _h14, "_LEN14": _len14, "_LEE14": _lee14, "_CLAVE14": _clave14, "_RAIZ14": _raiz14, "_LIBROS14": _libros14}


@contextlib.contextmanager
def _en_base():
    cwd = os.getcwd()
    try:
        os.chdir(BASE)
        yield
    finally:
        os.chdir(cwd)


def _ejecutar(n: str, args: list) -> tuple:
    """Texto adaptado de <n> como __main__ (sys.argv = [<base>/<n>, *args], cwd = la base) -> (rc, salida JSON, stdout, excepción)."""
    txt = adaptado(n)
    p = BASE / n
    g = {"__name__": "__main__", "__file__": str(p), "__builtins__": builtins}
    g.update(_ayudas())
    viejo, buf, rc, exc = sys.argv, io.StringIO(), 0, None
    sys.argv = [str(p)] + [str(x) for x in args]
    try:
        with _en_base(), contextlib.redirect_stdout(buf):
            exec(compile(txt, str(p), "exec"), g)
    except SystemExit as ex:
        rc = 0 if ex.code is None else ex.code
    except Exception:  # noqa: BLE001  (se registra; nunca se toma por éxito)
        rc, exc = None, _sin_base(traceback.format_exc())
    finally:
        sys.argv = viejo
    texto = _sin_base(buf.getvalue())
    try:
        ult = json.loads(texto)
    except ValueError:
        ult = {}
    return rc, ult, texto, exc


def ligadura_u63() -> dict:
    """BLOQUE-U63-v1: ejecuta la ligadura G/N de U63 (re-deriva pares completos, filas de cobertura y resumen desde las entradas aceptadas) y
    devuelve su espacio de nombres (AG, RES_GN, _gn_pares, _gn_cobertura). Las globales que el bloque toma del resto de U63 se inyectan:
    sha (sha256), _bytes (lectura del paquete), TT (raíz/tmp), PINF (raíz rem175 proyectada, claves bajo la raíz) y E175 (origen histórico)."""
    txt, a, b = bloque_u63()
    g = {"__name__": "fam14_u63_ligadura_gn", "__builtins__": builtins, "json": json, "Path": Path, "Fraction": Fraction, "Counter": Counter,
         "sha": sha, "_bytes": _lee14, "TT": RAIZ / "tmp", "WD": None,
         "PINF": {(RAIZ / k).as_posix(): v for k, v in _datos("autoridad/RAICES_FIJADAS.json")["raices"]["rem175"]["fijadas"].items()},
         "E175": {"ligadura_gn": dict(_datos("autoridad/ESQUEMA_REM175.json")["ligadura_gn"])}}
    g.update(_ayudas())
    with _en_base():
        exec(compile(txt, "%s:LIGADURA-GN" % U63, "exec"), g)
    g["_lineas"] = [a, b]
    return g


def _productos(d: Path) -> dict:
    return {rel(p): sha_archivo(p) for p in sorted(Path(d).rglob("*")) if p.is_file() and p.name not in ("ejecucion.json", "archivos_leidos.json")}


# ================================================================================================ recuentos (desde las filas)
def recuento_cobertura(cob: dict) -> dict:
    """Desde las FILAS (no desde su resumen): pares con techo en ambos diseños / en uno / en ninguno, reparto por menú, y la contraparte de
    malla: en cada fila contraparte_E4, exactamente un lado es la malla del otro diseño (frontera FRN-E4:<diseño>:…, LOTE2E4_MANIFIESTO, sin
    registro) y el otro lado lleva un registro (LOTE2_MANIFIESTO); el identificador del par es «E4:<frontera de la malla>»."""
    filas = cob.get("pares") or []
    n_reg = [sum(1 for d in ("G", "N") if f["lados"][d]["registros"]) for f in filas]
    ambos = Counter(f["instrumento"] for f, n in zip(filas, n_reg) if n == 2)
    uno = Counter(f["instrumento"] for f, n in zip(filas, n_reg) if n == 1)
    tipos = Counter(f["tipo"] for f in filas)
    malla_mal, techo_mal = [], []
    for f in filas:
        if f["tipo"] == "contraparte_E4":
            m = [d for d in ("G", "N") if f["lados"][d]["frontera"].startswith("FRN-E4:%s:" % d)]
            ok = (len(m) == 1 and f["lados"][m[0]]["manifiesto"] == "LOTE2E4_MANIFIESTO" and f["lados"][m[0]]["registros"] == []
                  and f["par"] == "E4:" + f["lados"][m[0]]["frontera"])
            otro = [d for d in ("G", "N") if d not in m]
            ok = ok and len(otro) == 1 and f["lados"][otro[0]]["manifiesto"] == "LOTE2_MANIFIESTO" and len(f["lados"][otro[0]]["registros"]) == 1
            if not ok:
                malla_mal.append(f["par"])
        elif f["tipo"] == "existente":
            if not all(len(f["lados"][d]["registros"]) == 1 and not f["lados"][d]["frontera"].startswith("FRN-E4:") for d in ("G", "N")):
                techo_mal.append(f["par"])
    ids = [f["par"] for f in filas]
    out = {"filas": len(filas), "pares_unicos": len(set(ids)), "ambos": sum(1 for n in n_reg if n == 2), "uno": sum(1 for n in n_reg if n == 1),
           "ninguno": sum(1 for n in n_reg if n == 0), "ambos_por_menu": dict(sorted(ambos.items())), "uno_por_menu": dict(sorted(uno.items())),
           "existentes": tipos.get("existente", 0), "contrapartes_E4": tipos.get("contraparte_E4", 0),
           "lados_de_malla_sin_registro": sum(1 for f in filas for d in ("G", "N") if f["lados"][d]["manifiesto"] == "LOTE2E4_MANIFIESTO" and not f["lados"][d]["registros"]),
           "lados_de_malla_con_registro": sum(1 for f in filas for d in ("G", "N") if f["lados"][d]["manifiesto"] == "LOTE2E4_MANIFIESTO" and f["lados"][d]["registros"]),
           "contrapartes_mal_etiquetadas": malla_mal[:10], "existentes_sin_techo_en_ambos": techo_mal[:10]}
    rs = cob.get("resumen") or {}
    out["resumen_igual_al_recuento"] = (rs.get("pares_E4_conciliados") == out["filas"] and rs.get("pares_completos") == out["ambos"]
                                        and rs.get("pares_un_lado") == out["uno"] and rs.get("pares_sin_lado") == out["ninguno"]
                                        and rs.get("pares_completos_por_menu") == out["ambos_por_menu"] and rs.get("pares_un_lado_por_menu") == out["uno_por_menu"])
    out["igual_a_lo_aceptado"] = all(out[k] == v for k, v in ESPERADO_GN.items())
    out["conforme"] = (out["igual_a_lo_aceptado"] and out["pares_unicos"] == out["filas"] and not malla_mal and not techo_mal
                       and out["lados_de_malla_con_registro"] == 0 and out["lados_de_malla_sin_registro"] == 383 and out["resumen_igual_al_recuento"])
    return out


def recuento_pares(pares: dict) -> dict:
    """Los 8 pares con techo en ambos diseños, desde sus filas: cada lado en su diseño y menú, cota certificada, intervalo exacto C2 ± error
    normalizado (Fraction) igual al publicado; d: intervalos disjuntos con G > N; f: mismo C2 almacenado e intervalos solapados (orden de los
    supremos indeterminado)."""
    filas = pares.get("pares") or []
    malos, d_gn, f_ind, otros = [], [], [], []
    for p in filas:
        j = p["instrumento"]
        iv = {}
        ok = p["par"] == "existente:%d" % p["indice_pares_existentes"]
        for d in ("G", "N"):
            s = p[d]
            e = s["escala_normalizada"]
            c2, er = Fraction(e["C2"]), Fraction(e["error_normalizado"])
            iv[d] = (c2 - er, c2 + er)
            ok = (ok and s["diseno"] == d and s["menu"] == j and s["garantia"]["clase"] == "cota_certificada_techo"
                  and s["garantia"]["error_kind"] == "certified_bound" and e["encierro_exacto"] == [str(iv[d][0]), str(iv[d][1])]
                  and isinstance(s.get("dominio_tau"), dict) and s["estado"] == "complete")
        gl, gh = iv["G"]
        nl, nh = iv["N"]
        res = ("G_sobre_N_certificado" if gl > nh else "N_sobre_G_certificado" if nl > gh else
               "C2_almacenado_igual" if p["G"]["escala_normalizada"]["C2"] == p["N"]["escala_normalizada"]["C2"] else "intervalos_solapados")
        ok = ok and p["comparacion_normalizada"]["resultado"] == res and p["comparacion_normalizada"]["G"] == [str(gl), str(gh)] \
            and p["comparacion_normalizada"]["N"] == [str(nl), str(nh)] and p["emparejamiento"]["disenos"] == ["G", "N"] \
            and p["emparejamiento"]["primitivas_iguales"] and p["emparejamiento"]["dominio_tau_igual"] and p["emparejamiento"]["menu_igual"]
        if not ok:
            malos.append(p["par"])
        if j == "d" and res == "G_sobre_N_certificado" and gl > nh:
            d_gn.append(p["par"])
        elif j == "f" and res == "C2_almacenado_igual" and not (gl > nh or nl > gh):
            f_ind.append(p["par"])
        else:
            otros.append({"par": p["par"], "menu": j, "resultado": res})
    out = {"pares": len(filas), "por_menu": dict(sorted(Counter(p["instrumento"] for p in filas).items())),
           "d_disjuntos_G_sobre_N": d_gn, "f_C2_igual_orden_indeterminado": f_ind, "otros": otros, "filas_inconsistentes": malos}
    out["conforme"] = len(filas) == 8 and len(d_gn) == 6 and len(f_ind) == 2 and not otros and not malos
    return out


def ligadura_de_lados(cob: dict) -> dict:
    """Cada lado con registro, ligado por clave a su fuente: el registro (copia exacta en el espejo) es un techo certificado de ESE diseño y
    ESE menú (payload.design_v y payload.instrument_j). Detecta una asignación G/N equivocada aunque los totales cuadren."""
    n, malos = 0, []
    for f in cob.get("pares") or []:
        for d in ("G", "N"):
            for r in f["lados"][d]["registros"]:
                doc = json.loads(_lee14(RAIZ / "tmp" / r))
                pl, c = doc["contenido"]["payload"], doc["contenido"]["ceiling"]
                n += 1
                if not (pl["design_v"] == d and pl["instrument_j"] == f["instrumento"] and doc["esquema"] == "techo-persistente-v2"
                        and c["sup"]["error_kind"] == "certified_bound"):
                    malos.append({"par": f["par"], "lado": d, "design_v": pl["design_v"], "instrument_j": pl["instrument_j"]})
    esperado = ESPERADO_GN["uno"] + 2 * ESPERADO_GN["ambos"]   # 383 + 2·8 = 399 lados con techo (un registro distinto por lado)
    return {"lados_con_registro": n, "esperados": esperado, "ligados": n - len(malos), "mal_ligados": malos[:10], "conforme": n == esperado and not malos}


# ================================================================================================ integridad (F14-GN, F14-187, F14-176)
def _declarada(a: str) -> str | None:
    return next((x["sha256"] for x in fuentes()["archivos"] if x["archivo"] == a), None)


def integridad_gn(p: Path | None = None) -> dict:
    """F14-GN: la cobertura aceptada (la copia que también sirve de referencia a la regeneración): huella aceptada 3ef08df8…, tamaño y recuento
    desde sus filas."""
    p = Path(p) if p is not None else BASE / COB_REF
    acept = fuentes()["huellas_aceptadas"]["F14-GN"]
    out = {"archivo": COB_REF, "presente": p.is_file(), "sha256": sha_archivo(p), "aceptado": acept, "bytes": p.stat().st_size if p.is_file() else None,
           "declarada_en_fuentes": _declarada(COB_REF) == acept}
    out["huella_conforme"] = out["sha256"] == acept
    try:
        out["recuento"] = recuento_cobertura(json.loads(p.read_bytes())) if p.is_file() else {"conforme": False, "motivo": "ausente"}
    except (ValueError, KeyError, TypeError, AttributeError) as e:
        out["recuento"] = {"conforme": False, "motivo": "filas no recontables: %r" % (e,)}
    out["conforme"] = out["presente"] and out["huella_conforme"] and out["declarada_en_fuentes"] and out["recuento"].get("conforme") is True
    return out


def integridad_187(p: Path | None = None) -> dict:
    """F14-187: la proyección pública del registro de localización §18.7. Identidad pública (huella de la proyección, verificable con el
    paquete) e identidad histórica (huella del original, cotejada en origen durante la extracción; restituirla exige rutas privadas)."""
    p = Path(p) if p is not None else BASE / LOC
    s = next(x for x in fuentes()["saneado"] if x["archivo"] == LOC)
    acept = fuentes()["huellas_aceptadas"]["F14-187"]
    raw = p.read_bytes() if p.is_file() else b""
    out = {"archivo": LOC, "presente": p.is_file(), "sha256": sha_archivo(p), "bytes": len(raw) if raw else None,
           "identidad_publica": {"sha256": s["sha256"], "bytes": s["bytes"], "verificable_con_el_paquete": True},
           "identidad_historica": {"sha256": s["sha256_original"], "bytes": s["bytes_original"], "aceptada_en_el_catalogo": acept,
                                   "verificable_con_el_paquete": False,
                                   "como_se_comprobo": ("en la extracción, la proyección restituye byte a byte el original al cambiar cada marcador por su ruta; "
                                                        "el original es miembro del inventario rem174 d35d4690…")},
           "declarada_en_fuentes": _declarada(LOC) == s["sha256"], "original_es_el_aceptado": s["sha256_original"] == acept and s.get("restituye_el_original") is True}
    out["huella_conforme"] = out["sha256"] == s["sha256"] and out["bytes"] == s["bytes"]
    c = {"conforme": False, "motivo": "ausente"}
    if raw:
        try:
            mk = {k: raw.count(k.encode()) for k in s["marcadores"]}
            doc = json.loads(raw)
            co = doc["corridas"]
            res = Counter(x["resultado"] for x in co)
            c = {"marcadores": mk, "marcadores_declarados": s["marcadores"], "sin_ruta_absoluta": not ABSOLUTA.search(raw), "kind": doc["kind"],
                 "objeto_buscado": doc["objeto_buscado"]["diseno"], "campos_de_diseno": doc["objeto_buscado"]["campos_de_diseno"],
                 "corridas": len(co), "run_id_unicos": len({x["run_id"] for x in co}), "resultados": dict(res),
                 "copias_auditor_d8_en_las_entregas": sum(len(x["copias_auditor_d8_en_la_entrega"]) for x in co),
                 "tablas_con_los_seis_campos": sum(len(x["tablas_con_los_seis_campos_de_esta_corrida"]) for x in co),
                 "resumen": {k: doc["resumen"][k] for k in ("corridas", "localizadas", "no_localizadas", "copias_auditor_d8")},
                 "ausencia_no_es_inexistencia": "no inexistencia" in doc["naturaleza"],
                 "codigo_original_D8": [x["ruta"] for x in doc.get("codigo_original_D8", [])]}
            c["conforme"] = (mk == s["marcadores"] and c["sin_ruta_absoluta"] and c["kind"] == "registro-localizacion-18-7-rem174" and c["corridas"] == 14
                             and c["run_id_unicos"] == 14 and c["resultados"] == {"no localizado en el corpus revisado": 14}
                             and c["copias_auditor_d8_en_las_entregas"] == 0 and c["tablas_con_los_seis_campos"] == 0
                             and c["resumen"] == {"corridas": 14, "localizadas": 0, "no_localizadas": 14, "copias_auditor_d8": 0}
                             and c["ausencia_no_es_inexistencia"] and len(c["campos_de_diseno"]) == 6)
        except (ValueError, KeyError, TypeError, AttributeError) as e:
            c = {"conforme": False, "motivo": "contenido no legible: %r" % (e,)}
    out["contenido"] = c
    out["auditor_ejecutado"] = ("cuestión abierta: el registro documenta que el objeto de §18.7 no se localizó en el corpus examinado (14 corridas T8); "
                                "no establece si el auditor D8 llegó a ejecutarse, y esta comprobación no lo decide")
    out["conforme"] = out["presente"] and out["huella_conforme"] and out["declarada_en_fuentes"] and out["original_es_el_aceptado"] and c.get("conforme") is True
    return out


def integridad_176(p: Path | None = None) -> dict:
    """F14-176: el derivado público de la referencia de adopción rem176 (huella propia), su texto del autor (huella y bytes recalculados), las
    cinco transiciones y su estado previo, y la ausencia de identificadores de la conversación y de rutas."""
    p = Path(p) if p is not None else BASE / ADOP
    dv = fuentes()["derivado_176"]
    acept = fuentes()["huellas_aceptadas"]["F14-176"]
    raw = p.read_bytes() if p.is_file() else b""
    out = {"archivo": ADOP, "presente": p.is_file(), "sha256": sha_archivo(p), "aceptado_derivado": dv["sha256"], "declarada_en_fuentes": _declarada(ADOP) == dv["sha256"],
           "original": {"sha256": dv["sha256_original"], "aceptado_en_el_catalogo": acept, "verificable_con_el_paquete": False},
           "proyeccion_rem197": {"sha256": dv["proyeccion_rem197_no_distribuida"]["sha256"], "distribuida": False, "motivo": dv["motivo"]},
           "verificable_por_terceros": dv["verificable_por_terceros"], "solo_en_origen": dv["solo_en_origen"]}
    out["huella_conforme"] = out["sha256"] == dv["sha256"]
    c = {"conforme": False, "motivo": "ausente"}
    if raw:
        try:
            doc = json.loads(raw)
            ta = doc["texto_del_autor"]
            tb = ta["texto"].encode("utf-8")
            tr = doc["transiciones"]
            c = {"texto_sha256_recalculado": sha(tb), "texto_bytes_recalculados": len(tb), "texto_ligado": sha(tb) == ta["sha256"] and len(tb) == ta["bytes"],
                 "nombra": {x: x in ta["texto"] for x in NOMBRADOS_176}, "deriva_de": doc["deriva_de"]["sha256"],
                 "transiciones": tr["estados"], "estado_previo": tr["estado_previo"],
                 "sentido_conservado": tr["estados"] == SENTIDO_176 and tr["estado_previo"] == "pendiente_de_localizacion",
                 "sin_identificadores_de_conversacion": not UUID.search(raw) and b".jsonl" not in raw and b"@@" not in raw,
                 "sin_ruta_absoluta": not ABSOLUTA.search(raw)}
            c["conforme"] = (c["texto_ligado"] and all(c["nombra"].values()) and c["deriva_de"] == acept == dv["sha256_original"] and c["sentido_conservado"]
                             and c["sin_identificadores_de_conversacion"] and c["sin_ruta_absoluta"])
        except (ValueError, KeyError, TypeError, AttributeError) as e:
            c = {"conforme": False, "motivo": "contenido no legible: %r" % (e,)}
    out["contenido"] = c
    out["conforme"] = out["presente"] and out["huella_conforme"] and out["declarada_en_fuentes"] and c.get("conforme") is True
    return out


INTEGRIDAD_FN = {"GN": integridad_gn, "LOC_187": integridad_187, "ADOPCION_176": integridad_176}
INTEGRIDAD_ARCHIVO = {"GN": "INTEGRIDAD_GN.json", "LOC_187": "INTEGRIDAD_18_7.json", "ADOPCION_176": "INTEGRIDAD_176.json"}


# ================================================================================================ etapas
def _etapa_gn_regen(sal: Path) -> dict:
    rc, ult, texto, exc = _ejecutar(U62, [RAIZ, sal, "salida_1"])
    need(rc == 0 and exc is None, "U62 sin éxito (rc=%s): %s" % (rc, (exc or texto or "")[-1500:]))
    return {"guiones": [U62], "resumen_impreso_por_U62": ult, "productos": sorted(p.name for p in (sal / "salida_1").iterdir()), "exito": True}


def _etapa_integridad(tarea: str):
    def f(sal: Path) -> dict:
        r = INTEGRIDAD_FN[tarea]()
        _escribir_x(sal / INTEGRIDAD_ARCHIVO[tarea], r)
        return {"guiones": [], "objeto": OBJETO_DE[tarea], "conforme": r["conforme"], "exito": True}
    return f


ETAPA_FN = {"GN_REGEN": _etapa_gn_regen, "GN": _etapa_integridad("GN"), "LOC_187": _etapa_integridad("LOC_187"), "ADOPCION_176": _etapa_integridad("ADOPCION_176")}


def entorno() -> dict:
    import platform
    return {"python": platform.python_version(), "hash_seed": os.environ.get("PYTHONHASHSEED"), "hash_randomization": sys.flags.hash_randomization,
            "TZ": os.environ.get("TZ"), "separador_de_rutas": os.sep}


def _prohibidas(en: list, tarea: str) -> list:
    return sorted(x for x in en if x.startswith(PROHIBIDAS) and x != OBJETO_DE.get(tarea))


def correr(tarea: str, sal: Path) -> dict:
    """Una etapa en la carpeta NUEVA sal (dentro de la base); registra lecturas y productos."""
    T0 = time.time()
    need(tarea in ETAPAS, "ETAPA_FUERA_DE_FAM14: %s" % tarea)
    rastro = F1().Rastro()
    sal = _dentro(sal)
    need(not sal.exists(), "LA_SALIDA_YA_EXISTE")
    sal.mkdir(parents=True)
    inicio = utc()
    try:
        det = ETAPA_FN[tarea](sal)
        exc = None
    except Exception:  # noqa: BLE001  (se registra; nunca se toma por éxito)
        det, exc = {"exito": False}, _sin_base(traceback.format_exc())[-3000:]
    fin = utc()
    informe = rastro.informe()
    (sal / "archivos_leidos.json").write_bytes((json.dumps(informe, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    en = informe["en_el_paquete"]
    lect = {"en_el_paquete": len(en), "fuera_del_paquete_y_del_interprete": informe["fuera_del_paquete_y_del_interprete"],
            "codigo_leido": sorted(x for x in en if x in ORIGINAL), "registros_de_techo_leidos": sum(1 for x in en if "/almacen_techos/" in x),
            "referencias_leidas": sorted(x for x in en if x.startswith("referencias/")), "referencia_prohibida_leida": _prohibidas(en, tarea)}
    ej = {"etiqueta": ETIQUETA, "tarea": tarea, "operacion": OPERACION_DE[tarea], "naturaleza": NATURALEZA[tarea], "adaptaciones": list(ADAPTACIONES),
          "inicio_utc": inicio, "fin_utc": fin, "detalle": det, "excepcion": exc, "productos_sha256": _productos(sal),
          "codigo": {n: {"archivo_sha256": sha_archivo(BASE / n), "original_sha256": ORIGINAL[n], "adaptado_sha256": sha(adaptado(n).encode("utf-8")),
                         "sustituciones": [s[0] for s in SUSTITUCIONES.get(n, ())]} for n in det.get("guiones", [])},
          "segundos": round(time.time() - T0, 3), "entorno": entorno(), "lecturas": lect}
    ej["exito"] = bool(det.get("exito")) and exc is None and not lect["fuera_del_paquete_y_del_interprete"] and not lect["referencia_prohibida_leida"]
    _escribir(sal / "ejecucion.json", ej)
    return ej


# ================================================================================================ validación (sin referencias)
def _validar_gn_regen(d: Path) -> dict:
    S = d / "salida_1"
    pares = json.loads((S / "PARES_GN_REM174.json").read_bytes())
    cob = json.loads((S / "COBERTURA_GN_REM174.json").read_bytes())
    fu = json.loads((S / "FUENTES_BLOQUE_A_REM174.json").read_bytes())
    g = ligadura_u63()
    fp, fc = g["_gn_pares"](pares), g["_gn_cobertura"](cob)
    rc, rp, rl = recuento_cobertura(cob), recuento_pares(pares), ligadura_de_lados(cob)
    claves_abs = [k for k in fu["fuentes"] if ABSOLUTA.search(k.encode())]
    comp = {"U63_gn_pares_sin_hallazgos": not fp, "U63_gn_cobertura_sin_hallazgos": not fc,
            "U63_resumen_derivado_igual_a_lo_aceptado": (g["RES_GN"]["pares_completos_por_menu"] == ESPERADO_GN["ambos_por_menu"]
                                                         and g["RES_GN"]["pares_un_lado_por_menu"] == ESPERADO_GN["uno_por_menu"]
                                                         and g["RES_GN"]["pares_sin_lado"] == 0 and g["RES_GN"]["pares_E4_conciliados"] == 391),
            "recuento_de_filas_cobertura": rc["conforme"], "pares_ocho_desde_filas": rp["conforme"], "lados_ligados_a_su_registro": rl["conforme"],
            "fuentes_sin_rutas_absolutas": not claves_abs}
    return {"comprobaciones": comp, "hallazgos_U63": {"pares": [list(x) for x in fp[:20]], "cobertura": [list(x) for x in fc[:20]]},
            "recuentos": {"cobertura": rc, "pares": rp, "lados": rl},
            "U63": {"bloque": "%s líneas %d–%d (ligadura G/N rem175)" % (U63, g["_lineas"][0], g["_lineas"][1]),
                    "ejecutado": ["_ligadura_gn (AG: registros del mapa, filas de la conciliación, pares completos)", "_resumen_esperado (RES_GN)",
                                  "_gn_pares(PARES nuevo)", "_gn_cobertura(COBERTURA nueva)"],
                    "no_ejecutado": "resto de U63 (matriz rem175, enlaces, §18.7 contra su corpus, correspondencia rem174): juzga productos que FAM14 no regenera",
                    "RES_GN": g["RES_GN"], "sustituciones": [s[0] for s in SUSTITUCIONES_U63]},
            "aceptada": all(comp.values())}


def _validar_integridad(tarea: str):
    def f(d: Path) -> dict:
        r = json.loads((d / INTEGRIDAD_ARCHIVO[tarea]).read_bytes())
        return {"comprobaciones": {"integridad_conforme": r["conforme"] is True}, "aceptada": r["conforme"] is True}
    return f


VALIDAR_FN = {"GN_REGEN": _validar_gn_regen, "GN": _validar_integridad("GN"), "LOC_187": _validar_integridad("LOC_187"), "ADOPCION_176": _validar_integridad("ADOPCION_176")}


def validar(d: Path) -> dict:
    """Comprobaciones independientes sobre la salida NUEVA, sin leer las referencias (para GN_REGEN, la ligadura G/N de U63 y recuentos propios)."""
    d = _dentro(d)
    ej = leer(d / "ejecucion.json")
    need(ej.get("etiqueta") == ETIQUETA, "CARPETA_AJENA")
    t0 = time.time()
    rastro = F1().Rastro()
    try:
        r = VALIDAR_FN[ej["tarea"]](d) if ej.get("exito") else {"comprobaciones": {}, "aceptada": False, "motivo": "etapa sin éxito"}
    except Exception:  # noqa: BLE001
        r = {"comprobaciones": {}, "aceptada": False, "excepcion": _sin_base(traceback.format_exc())[-1500:]}
    inf = rastro.informe()
    r.update({"comando": "fam14-validar", "tarea": ej["tarea"], "origen": rel(d), "inventory_sha256": sha_archivo(d / "ejecucion.json"),
              "validador": ("U63 verificar_relaciones_rem175.py (validador vigente): ligadura G/N re-derivada desde las entradas aceptadas, más recuentos "
                            "propios desde las filas" if ej["tarea"] == "GN_REGEN" else "comprobación de integridad de la etapa"),
              "lecturas": {"en_el_paquete": len(inf["en_el_paquete"]), "fuera_del_paquete_y_del_interprete": inf["fuera_del_paquete_y_del_interprete"],
                           "referencia_prohibida_leida": _prohibidas(inf["en_el_paquete"], ej["tarea"])},
              "segundos": round(time.time() - t0, 3)})
    r["aceptada"] = bool(r["aceptada"]) and not r["lecturas"]["referencia_prohibida_leida"] and not r["lecturas"]["fuera_del_paquete_y_del_interprete"]
    return r


# ================================================================================================ comparación (después de producir y validar)
_FALTA = object()


def _hojas(x, pre=()):
    if isinstance(x, dict) and x:
        for k, v in x.items():
            yield from _hojas(v, pre + (k,))
    elif isinstance(x, list) and x:
        for i, v in enumerate(x):
            yield from _hojas(v, pre + (i,))
    else:
        yield pre, x


def _clasificar(p: tuple, a, b, ctx: dict) -> dict:
    """Tipo de una diferencia: procedencia (tiempo, huella) con su vínculo comprobado, o científica."""
    d = {"campo": "/".join(str(x) for x in p), "nuevo": a if a is not _FALTA else "<ausente>", "referencia": b if b is not _FALTA else "<ausente>"}
    if a is _FALTA or b is _FALTA:
        return dict(d, tipo="cientifica")
    if p and p[-1] == "segundos" and isinstance(a, (int, float)):
        return dict(d, tipo="procedencia:tiempo", vinculo="segundos de esta ejecución", vinculo_ok=True)
    if isinstance(a, str) and isinstance(b, str) and HEX64.fullmatch(a) and HEX64.fullmatch(b):
        v = ctx["hashes"].get(a)
        return dict(d, tipo="procedencia:huella", vinculo=v, vinculo_ok=v is not None)
    return dict(d, tipo="cientifica")


def _dif(nuevo, ref, ctx: dict) -> list:
    hn, hr = dict(_hojas(nuevo)), dict(_hojas(ref))
    out = []
    for p in sorted(set(hn) | set(hr), key=lambda t: [str(x) for x in t]):
        a, b = hn.get(p, _FALTA), hr.get(p, _FALTA)
        if a is not _FALTA and b is not _FALTA and _js(a) == _js(b):
            continue
        out.append(_clasificar(p, a, b, ctx))
    return out


def _resumen(difs: list) -> dict:
    cient = [x for x in difs if x["tipo"] == "cientifica"]
    proc = {}
    for x in difs:
        if x["tipo"] != "cientifica":
            k = "%s | %s" % (re.sub(r"/\d+(?=/|$)", "/[]", x["campo"]), x["tipo"])
            g = proc.setdefault(k, {"tipo": x["tipo"], "campo": re.sub(r"/\d+(?=/|$)", "/[]", x["campo"]), "n": 0, "vinculos_ok": 0, "ejemplo": x})
            g["n"] += 1
            g["vinculos_ok"] += bool(x.get("vinculo_ok"))
    return {"cientificas_n": len(cient), "cientificas": cient[:40], "procedencia": sorted(proc.values(), key=lambda g: g["campo"]),
            "procedencia_vinculada": all(g["n"] == g["vinculos_ok"] for g in proc.values())}


def _lado(f: dict, d: str):
    """Lado d de una fila: en la cobertura, bajo «lados»; en los pares, en la propia fila."""
    return (f.get("lados") or {}).get(d) if "lados" in f else f.get(d)


def _comparar_filas(nuevas: list, refs: list, clave: str, ctx: dict) -> dict:
    kn, kr = [f[clave] for f in nuevas], [f[clave] for f in refs]
    N, Rf = dict(zip(kn, nuevas)), dict(zip(kr, refs))
    difs = []
    for k in kn:
        if k in Rf:
            difs += [dict(x, clave=k) for x in _dif(N[k], Rf[k], ctx)]
    r = _resumen(difs)
    comunes = [k for k in kn if k in Rf]
    r.update({"filas_nuevas": len(nuevas), "filas_referencia": len(refs), "faltan": sorted(set(kr) - set(kn))[:20], "ajenas": sorted(set(kn) - set(kr))[:20],
              "duplicadas": len(kn) - len(set(kn)), "mismo_orden": kn == kr, "filas_identicas": sum(1 for k in comunes if _js(N[k]) == _js(Rf[k])),
              "lados_iguales": {d: sum(1 for k in comunes if _js(_lado(N[k], d)) == _js(_lado(Rf[k], d))) for d in ("G", "N")}})
    r["cumple"] = r["cientificas_n"] == 0 and not r["faltan"] and not r["ajenas"] and not r["duplicadas"] and r["procedencia_vinculada"]
    return r


def _bytes(nuevo: Path, ref: Path, aceptada: str | None = None) -> dict:
    hn, hr = sha_archivo(nuevo), sha_archivo(ref)
    return {"nuevo": rel(nuevo), "nuevo_sha256": hn, "referencia": rel(ref), "referencia_sha256": hr, "aceptada_sha256": aceptada,
            "bytes_identicos": hn == hr, "igual_a_la_huella_aceptada": aceptada is not None and hn == aceptada}


def _contexto(d: Path) -> dict:
    hs = {}
    for p in sorted(Path(d).rglob("*")):
        if p.is_file():
            hs.setdefault(sha_archivo(p), rel(p))
    for x in piezas():
        hs.setdefault(x["sha256"], x["archivo"])
    return {"hashes": hs}


def _comparar_gn_regen(d: Path, ctx: dict) -> dict:
    hu = fuentes()["huellas_aceptadas"]
    S = d / "salida_1"
    out = {}
    for k, n, ref, acept in (("COBERTURA", "COBERTURA_GN_REM174.json", COB_REF, hu["F14-GN-REGEN"]), ("PARES", "PARES_GN_REM174.json", PARES_REF, PARES_ACEPTADO)):
        b = _bytes(S / n, BASE / ref, acept)
        if b["referencia_sha256"] != acept:
            motivo = "referencia ausente" if b["referencia_sha256"] is None else "huella de referencia distinta de la aceptada"
            out[k] = {"bytes": b, "cumple": False, "motivo": motivo}
            continue
        nv, rf = json.loads((S / n).read_bytes()), json.loads((BASE / ref).read_bytes())
        f = _comparar_filas(nv["pares"], rf["pares"], "par", ctx)
        resto = _resumen(_dif({x: y for x, y in nv.items() if x != "pares"}, {x: y for x, y in rf.items() if x != "pares"}, ctx))
        resto["cumple"] = resto["cientificas_n"] == 0 and resto["procedencia_vinculada"]
        out[k] = {"bytes": b, "filas": f, "resumen_y_regla": resto,
                  "cumple": f["cumple"] and resto["cumple"] and f["lados_iguales"] == {"G": f["filas_referencia"], "N": f["filas_referencia"]}
                  and b["bytes_identicos"] and b["igual_a_la_huella_aceptada"]}
    fu = S / "FUENTES_BLOQUE_A_REM174.json"
    return {"productos": out, "FUENTES_BLOQUE_A": {"nuevo_sha256": sha_archivo(fu), "fuentes": len(json.loads(fu.read_bytes())["fuentes"]),
                                                   "nota": ("sin referencia en el catálogo: la histórica tiene claves absolutas (rutas privadas); la nueva, "
                                                            "claves relativas a la raíz (LECTURA-PAQUETE-v1)")},
            "cumple": all(x["cumple"] for x in out.values())}


def comparar(d: Path, validacion: Path) -> dict:
    """DESPUÉS de producir y validar: igualdad exacta por clave «par» (ambos lados) de la cobertura y de los pares contra sus referencias,
    resumen y regla aparte, y bytes contra la huella aceptada; una diferencia científica deja el producto pendiente."""
    t0 = time.time()
    d, validacion = _dentro(d), _dentro(validacion)
    ej = leer(d / "ejecucion.json")
    val = leer(validacion)
    need(ej.get("etiqueta") == ETIQUETA and ej.get("tarea") == "GN_REGEN" and val.get("comando") == "fam14-validar" and val.get("origen") == rel(d)
         and val.get("inventory_sha256") == sha_archivo(d / "ejecucion.json"), "VALIDACION_AJENA")
    det = _comparar_gn_regen(d, _contexto(d))
    motivos = []
    if not val.get("aceptada"):
        motivos.append("validación no aceptada")
    if not det["cumple"]:
        motivos.append("diferencias científicas, lados distintos, procedencia sin vínculo o bytes distintos de la huella aceptada")
    return {"comando": "fam14-comparar", "tarea": "GN_REGEN", "operacion": "F14-GN-REGEN", "nueva": rel(d), "validacion": rel(validacion),
            "regla": "COMPARACION-FAM14-v1 (src/fam14.py)", **det, "estado": {"reproduccion": "aceptada" if not motivos else "no_aceptada", "motivos": motivos},
            "segundos": round(time.time() - t0, 3)}


# ================================================================================================ orden única, comprobación y receta
def _balance(comp: dict, vals: dict, ejs: dict, integ: dict) -> list:
    hu = fuentes()["huellas_aceptadas"]
    filas = []
    for k, n in (("COBERTURA", "COBERTURA_GN_REM174.json"), ("PARES", "PARES_GN_REM174.json")):
        c = (comp.get("productos") or {}).get(k) or {}
        b, fl = c.get("bytes") or {}, c.get("filas") or {}
        pend = []
        if not ejs["GN_REGEN"].get("exito"):
            pend.append("etapa sin éxito")
        if not vals["GN_REGEN"].get("aceptada"):
            pend.append("validación independiente (U63 y recuentos) no aceptada")
        if fl.get("cientificas_n"):
            pend.append("%d diferencias científicas" % fl["cientificas_n"])
        if c and not c.get("cumple"):
            pend.append(c.get("motivo", "comparación no cumple"))
        filas.append({"operacion": "F14-GN-REGEN", "producto": n, "papel": "producto del catálogo" if k == "COBERTURA" else "producto hermano de U62 (no está en el catálogo)",
                      "sha256_aceptado": hu["F14-GN-REGEN"] if k == "COBERTURA" else PARES_ACEPTADO, "regenerado": bool(b.get("nuevo_sha256")),
                      "sha256_nuevo": b.get("nuevo_sha256"), "bytes_iguales_a_la_huella_aceptada": b.get("igual_a_la_huella_aceptada"),
                      "filas": {x: fl.get(x) for x in ("filas_nuevas", "filas_referencia", "filas_identicas", "lados_iguales", "cientificas_n")}, "pendiente": pend})
    for t in ("GN", "LOC_187", "ADOPCION_176"):
        r = integ.get(t) or {}
        filas.append({"operacion": OPERACION_DE[t], "producto": OBJETO_DE[t], "regenerado": False, "comprobado_por_huella": r.get("huella_conforme"),
                      "conforme": r.get("conforme"), "pendiente": [] if r.get("conforme") else ["integridad no conforme"]})
    return filas


def reproducir(salida: Path) -> dict:
    """fam14-reproducir: GN_REGEN (con su validación U63), GN, LOC_187 y ADOPCION_176; después, la comparación de GN_REGEN y el balance."""
    t0 = time.time()
    sal = _dentro(salida)
    need(not sal.exists(), "LA_SALIDA_YA_EXISTE")
    malos = fuentes_alteradas("calculo")
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam14.json; no se calcula): %s" % malos[:5])
    sal.mkdir(parents=True)
    pasos, ejs, vals, integ = [], {}, {}, {}
    for t in ETAPAS:
        d, v = sal / t.lower(), sal / (t.lower() + ".validacion.json")
        ej = correr(t, d)
        ejs[t] = ej
        r = validar(d)
        _escribir_x(v, r)
        vals[t] = r
        if t in INTEGRIDAD_ARCHIVO and (d / INTEGRIDAD_ARCHIVO[t]).is_file():
            integ[t] = json.loads((d / INTEGRIDAD_ARCHIVO[t]).read_bytes())
        pasos.append({"etapa": t, "operacion": OPERACION_DE[t], "carpeta": rel(d), "exito": ej["exito"], "excepcion": (ej["excepcion"] or "")[-600:] or None,
                      "validacion": rel(v), "aceptada": r["aceptada"], "segundos": ej["segundos"],
                      "referencia_prohibida_leida": ej["lecturas"]["referencia_prohibida_leida"] + r["lecturas"]["referencia_prohibida_leida"]})
    comp = {}
    if ejs["GN_REGEN"]["exito"]:
        comp = comparar(sal / "gn_regen", sal / "gn_regen.validacion.json")
        _escribir_x(sal / "gn_regen.comparacion.json", comp)
    vr = vals["GN_REGEN"]
    regen = {"exito": ejs["GN_REGEN"]["exito"], "validacion_aceptada": vr["aceptada"], "comprobaciones": vr.get("comprobaciones"),
             "recuentos": {"ambos": (vr.get("recuentos") or {}).get("cobertura", {}).get("ambos"), "uno": (vr.get("recuentos") or {}).get("cobertura", {}).get("uno"),
                           "ninguno": (vr.get("recuentos") or {}).get("cobertura", {}).get("ninguno"),
                           "ambos_por_menu": (vr.get("recuentos") or {}).get("cobertura", {}).get("ambos_por_menu"),
                           "uno_por_menu": (vr.get("recuentos") or {}).get("cobertura", {}).get("uno_por_menu"),
                           "d_disjuntos_G_sobre_N": len((vr.get("recuentos") or {}).get("pares", {}).get("d_disjuntos_G_sobre_N", [])),
                           "f_C2_igual_orden_indeterminado": len((vr.get("recuentos") or {}).get("pares", {}).get("f_C2_igual_orden_indeterminado", [])),
                           "lados_de_malla_sin_registro": (vr.get("recuentos") or {}).get("cobertura", {}).get("lados_de_malla_sin_registro")},
             "comparacion": {"archivo": rel(sal / "gn_regen.comparacion.json") if comp else None, "estado": (comp.get("estado") or {})}}
    regen["cumple"] = regen["exito"] and regen["validacion_aceptada"] and (comp.get("estado") or {}).get("reproduccion") == "aceptada"
    out = {"comando": "fam14-reproducir", "etiqueta": ETIQUETA, "salida": rel(sal), "pasos": pasos, "F14_GN_REGEN": regen,
           "F14_GN": {"conforme": (integ.get("GN") or {}).get("conforme"), "sha256": (integ.get("GN") or {}).get("sha256"),
                      "recuento": {k: ((integ.get("GN") or {}).get("recuento") or {}).get(k) for k in ("filas", "ambos", "uno", "ninguno", "ambos_por_menu", "uno_por_menu")}},
           "F14_187": {k: (integ.get("LOC_187") or {}).get(k) for k in ("conforme", "sha256", "identidad_publica", "identidad_historica", "auditor_ejecutado")},
           "F14_176": {k: (integ.get("ADOPCION_176") or {}).get(k) for k in ("conforme", "sha256", "original", "proyeccion_rem197", "solo_en_origen")},
           "balance": _balance(comp, vals, ejs, integ)}
    out["F14_176"]["transiciones"] = ((integ.get("ADOPCION_176") or {}).get("contenido") or {}).get("transiciones")
    out["cumple"] = (regen["cumple"] and all(ejs[t]["exito"] and vals[t]["aceptada"] for t in ETAPAS)
                     and all((integ.get(t) or {}).get("conforme") is True for t in INTEGRIDAD_ARCHIVO))
    out["segundos"] = round(time.time() - t0, 3)
    out["entorno"] = entorno()
    return out


def comprobar() -> dict:
    t0 = time.time()
    malos = fuentes_alteradas("todo")
    out = {"comando": "fam14-comprobar", "calculo": "ninguno", "fuentes": {"piezas": len(piezas()), "alteradas": malos},
           "sustituciones": sustituciones_ok(),
           "codigo": {n: {"archivo_sha256": sha_archivo(BASE / n), "original_sha256": h, "corresponde": (BASE / n).is_file() and sha14((BASE / n).read_bytes()) == h}
                      for n, h in ORIGINAL.items()},
           "referencias": {a: sha_archivo(BASE / a) == _declarada(a) for a in (COB_REF, PARES_REF)},
           "integridad": {t: {"conforme": f()["conforme"]} for t, f in INTEGRIDAD_FN.items()},
           "receta": {"pasos": len(receta()["pasos"])}}
    out["cumple"] = (not malos and all(v is True for v in out["sustituciones"].values()) and all(x["corresponde"] for x in out["codigo"].values())
                     and all(out["referencias"].values()) and all(x["conforme"] for x in out["integridad"].values()))
    out["segundos"] = round(time.time() - t0, 3)
    return out


def receta() -> dict:
    py = "<python de .venv-fam01> -B -P -s -X utf8 reproducir.py"
    s = "salidas/fam14/<ejecucion>"
    pasos = [{"paso": "comprobar", "orden": py + " fam14-comprobar --salida " + s + "_comprobar.json", "calculo": "ninguno"},
             {"paso": "orden única", "orden": py + " fam14-reproducir --salida " + s,
              "calculo": ("GN_REGEN: U62 regenera pares y cobertura G/N (sin modelo; aritmética racional exacta de la fuente); la ligadura G/N de U63 "
                          "y recuentos propios los validan sin referencias; después, comparación fila a fila (ambos lados) con la referencia. GN, LOC_187 "
                          "y ADOPCION_176: integridad por huella y contenido. Balance por producto en resumen.json")}]
    return {"comando": "fam14-receta", "estado": "lista (no ejecuta nada)", "pasos": pasos,
            "cobertura": {"operaciones": list(OPERACION_DE.values()), "etapas": list(ETAPAS)},
            "nota": ("sin entradas externas: todas las piezas están en el paquete (nucleo_s6/raiz, datos/fam14, y la conciliación E4 y los manifiestos "
                     "de FAM06/FAM05); las referencias (referencias/fam14) solo se leen al comparar y, la cobertura, como objeto de F14-GN")}
