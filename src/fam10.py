"""FAM10 (tabla final de Exp8: 1.728 afirmaciones, su resumen y la resolución de las doce COV).

Operaciones del catálogo, en el orden de sus dependencias (regeneración documental y aritmética sobre productos existentes):
- F10-ENF-AFIRMACION (etapa ENF): conciliar_exp8_rem147.py (U41, sin cambios de lógica) con T7_anexo y EXP8_TABLA de rem108, las 16 filas padre
  que lee y el integral ENF NUEVO de FAM08 (fam08-integrar con su comparación aceptada). Enlace por (unidad, cell_id) y G padre; escribe
  ENF_POR_AFIRMACION.jsonl, COBERTURA_EXP8.json/.md y RESUMEN_POR_PAIS.json. U42 (validador histórico) sigue sin localizarse: la validación de
  la etapa ejecuta la parte científica de la auditoría del revisor rem148 (líneas 49–116 de review_20261105_rem148_audit.py) sobre el producto
  NUEVO. Por decisión del autor (2026-11-18, L-ENF-AFIRMACION-AUDITORIA-REM148) ese bloque es la validación del ENF regenerado y la fila sigue
  RD; no acredita la identidad de U42 ni las partes de la auditoría que verifican la ronda histórica.
- F10-SINTESIS (etapa SINTESIS): construir_sintesis_rem160.py (U44) con el ENF NUEVO validado, la conciliación COV de FAM11, el suplemento P7 y
  las dos versiones de Q local de FAM12. P7 se aplica una vez. U45 no se ejecuta (verifica una ronda histórica completa: inventarios, libros y
  textos de rem160); la validación local recalcula enlaces, recuentos y la regla ε desde las filas y las entradas.
- F10-INTEGRACION (etapa INTEGRACION): construir_integracion_rem170.py (U47) sobre la síntesis NUEVA validada y la evidencia y lectura B1 → B2
  validadas de FAM11: G_hi = U_C2 − L_K1 por grupo, regla inclusiva G_hi ≤ −1/100; cambian solo las doce; las 1.716 restantes, byte a byte.
  U48 no se ejecuta (mismo motivo que U45); la validación local recalcula la aritmética y comprueba la conservación.

Adaptaciones (no cambian fórmulas, claves, tolerancias, criterios ni la serialización; cada original se sustituye una sola vez):
- GUION-v1: cada guion corre desde sus bytes (proyección saneada para U44/U47, autenticada por la huella de su original) con las sustituciones de
  SUSTITUCIONES, en el proceso, con cwd = la base y rutas relativas.
- RAIZ-EXP8-v1: la raíz histórica es nucleo_s6/exp8 (espejo de tmp/<área>/<rel>) para T7, EXP8_TABLA y las filas padre.
- ENTRADAS-ENF-v1: U41 lee las cuatro fuentes rem131 del integral NUEVO de FAM08 (conciliacion/, ensamblado/) con las huellas fijadas por su
  ejecución; la autenticación (argumento 2 de U41) es AUTENTICACION_LOCAL_FAM10.json, escrita por la etapa con esas huellas.
- MARCADOR-W-v1 / MARCADOR-R-v1: en U44 el directorio de los libros y la raíz histórica son marcadores (@@W_BS2@@, @@R_BS2@@): solo aparecen en
  rutas de procedencia; nada se lee de ellos.
- AUTORIDAD-EXTRAIDA-v1: los libros que U44 carga son los resúmenes datos/fam10/autoridad (solo los campos que lee, ligados a la huella del
  original); los dictámenes se autentican por la huella registrada en la extracción (no se copian).
- ENLACE-SINTESIS-v1: los cinco productos de entrada de U44 son los NUEVOS ligados a sus registros (ENF: registro fam10-validar; COV: ejecución y
  comparación de FAM11; P7: salida concordante de p7-suplemento, serializada como SUPLEMENTO_P7.jsonl; Q: salida concordante de q-local);
  Q-LOCAL-v1: las filas «posicion» y «afirmacion» de q_local_<versión>.jsonl ocupan las listas posiciones/afirmaciones de resultado.json.
- ENLACE-INTEGRACION-v1: S = la síntesis NUEVA; las 26 claves de autenticación de U47 las ocupan piezas locales declaradas en
  enlace/ENLACE_INTEGRACION.json (libros B1/B2 LOCALES derivados de la lectura validada; no son libros de Codex).
- AUDITORIA-REM148-v1: el bloque científico de la auditoría lee el integral NUEVO y el producto NUEVO (cuatro sustituciones de ruta).

Comparación (COMPARACION-FAM10-v1): igualdad exacta del contenido científico; cada diferencia de procedencia, con su vínculo comprobado.
VINCULO-CERTIFICADO-v1 (2026-11-20): la huella certificado_resolucion_sha256 de las filas ENF se liga al certificado que el integral ENF NUEVO
declara como reemitido por fam08-recuperar (bytes, clave, fuente, recuperación y su comparación aceptada, original = la referencia); ver
certificado_reemitido.
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
sha, sha_archivo, leer, leer_jsonl, rel, F1 = F5.sha, F5.sha_archivo, F5.leer, F5.leer_jsonl, F5.rel, F5.F1
ETIQUETA = "REPRODUCCION LIMPIA FAM10 NO OFICIAL"
T10 = "nucleo_s6/exp8"
R10 = BASE / T10
DATOS = BASE / "datos" / "fam10"
REF = BASE / "referencias" / "fam10"
A108 = "paso4_conciliacion_portabilidad_desde_rem108"
A131 = "paso4_integracion_final_enf_desde_rem131"
A147 = "paso4_ablaciones_exp8_desde_rem147"
A160 = "paso4_correcciones_sintesis_exp8_desde_rem160"
A170 = "paso4_integracion_final_exp8_desde_rem170"
U41 = "%s/tmp/%s/exp8/conciliar_exp8_rem147.py" % (T10, A147)
U44 = "%s/tmp/%s/sintesis/construir_sintesis_rem160.py" % (T10, A160)
U47 = "%s/tmp/%s/construccion/construir_integracion_rem170.py" % (T10, A170)
AUD = "%s/auditoria/review_20261105_rem148_audit.lineas_049_116.py" % T10
ESQUEMA = "%s/tmp/%s/construccion/ESQUEMA_DECLARADO_REM170.json" % (T10, A170)
ORIGINAL = {U41: "8e9d207c96fa3d1f6c7a816b29fe4f7c6c0d6aedaa228a2009fcaa286da937d3",
            U44: "e96814df3ae17c4c24463958b7839491ade01e5c1b3e1614cc510d6cbaf84966",
            U47: "95493c614aa367c2ad97913387aa56ee7e532e44eb1775a5227143d7063593a6"}
ETAPAS = ("ENF", "SINTESIS", "INTEGRACION")
OPERACION_DE = {"ENF": "F10-ENF-AFIRMACION", "SINTESIS": "F10-SINTESIS", "INTEGRACION": "F10-INTEGRACION"}
ENTRADAS_DE = {"ENF": ("enf_integral", "registro_enf_integral"),
               "SINTESIS": ("enf", "validacion_enf", "cov", "registro_cov", "p7", "q_local"),
               "INTEGRACION": ("sintesis", "validacion_sintesis", "b1", "validacion_b1", "b2", "validacion_b2")}
TABLA = ("enf_integral", "registro_enf_integral", "cov", "registro_cov", "p7", "q_local", "b1", "validacion_b1", "b2", "validacion_b2")
PROHIBIDAS = ("referencias/fam10/", "datos/fam11/cov/ENF_POR_AFIRMACION.jsonl", "referencias/fam11/rem170/")
ADAPTACIONES = ("GUION-v1", "RAIZ-EXP8-v1", "ENTRADAS-ENF-v1", "MARCADOR-W-v1", "MARCADOR-R-v1", "AUTORIDAD-EXTRAIDA-v1", "ENLACE-SINTESIS-v1",
                "Q-LOCAL-v1", "ENLACE-INTEGRACION-v1", "AUDITORIA-REM148-v1")
NATURALEZA = {"ENF": "regeneración documental: U41 sobre T7/EXP8 rem108 y el integral ENF NUEVO de FAM08",
              "SINTESIS": "regeneración documental: U44 sobre el ENF NUEVO validado, COV de FAM11, P7 y Q local de FAM12",
              "INTEGRACION": "regeneración documental y aritmética exacta: U47 sobre la síntesis NUEVA validada y la lectura B1 → B2 validada de FAM11"}
EPS = Fraction(1, 100)
HEX64 = re.compile(r"[0-9a-f]{64}")
ENF_NODEC = "no_decidida_por_testigos (mantener la robustez exige el supremo ENF sobre todo el soporte)"


class Fam10Error(Exception):
    pass


def need(c, m: str):
    if not c:
        raise Fam10Error(m)


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def canon(o) -> bytes:
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def fx(q: Fraction) -> str:
    return "%d/%d" % (q.numerator, q.denominator)


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


def lineas_de(p: Path) -> list:
    raw = Path(p).read_bytes()
    partes = raw.split(b"\n")
    need(partes[-1] == b"", "FILAS_SIN_FIN_DE_LINEA: %s" % rel(p))
    return [x + b"\n" for x in partes[:-1]]


def _dentro(p) -> Path:
    p = Path(p).resolve()
    need(p.is_relative_to(BASE.resolve()), "ENTRADA_FUERA_DE_LA_BASE (copie la carpeta dentro de la base): %s" % p.name)
    return p


# ================================================================================================ fuentes
_CACHE: dict = {}


def fuentes() -> dict:
    if "fu" not in _CACHE:
        _CACHE["fu"] = leer(BASE / "fuentes_fam10.json")
    return _CACHE["fu"]


def original() -> dict:
    """Huella de una proyección -> huella de su original (fuentes_fam10.json)."""
    return {x["sha256"]: x["sha256_original"] for x in fuentes()["saneado"] if x.get("restituye_el_original") is True}


def sha10(b: bytes) -> str:
    h = sha(b)
    return original().get(h, h)


def codigo() -> dict:
    out = dict(ORIGINAL)
    out[AUD] = fuentes()["auditoria_rem148"]["sha256"]
    return out


def piezas() -> list:
    fu = fuentes()
    return fu["archivos"] + fu["reutilizados"]


def fuentes_alteradas(uso: str = "todo") -> list:
    """«calculo»: código, datos y resúmenes (sin referencias); «todo»: también las referencias (fam10-comprobar)."""
    return [x["archivo"] for x in piezas() if (uso == "todo" or not x["archivo"].startswith(("referencias/",) + PROHIBIDAS))
            and sha_archivo(BASE / x["archivo"]) != x["sha256"]]


# ================================================================================================ sustituciones
_U44_PRODUCTOS = r'''qp = libro["Q"]["products"]   # FAM10 ENLACE-SINTESIS-v1: los productos de entrada son los NUEVOS ligados a sus registros (ENLACE_SINTESIS.json)
F = {}
_E10 = _ENTRADAS10()
eb, F["ENF_POR_AFIRMACION"] = producto(_E10["ENF"][0], _E10["ENF"][1], "ENF", "product / product_sha256")
cb, F["CONCILIACION_COV"] = producto(_E10["COV"][0], _E10["COV"][1], "COV", "products[...CONCILIACION_COV.jsonl]")
p7_ruta = next(r for r in libro["P7"]["products"] if r.endswith("SUPLEMENTO_P7.jsonl"))
assert libro["P7"]["products"][p7_ruta] == libro["P7"]["summary"]["producto_sha256"], "P7_HUELLA_INCOHERENTE_EN_SU_LIBRO"
pb, F["SUPLEMENTO_P7"] = producto(_E10["P7"][0], _E10["P7"][1], "P7", "products[...SUPLEMENTO_P7.jsonl] = summary.producto_sha256")
qres = {}
for v, t in (("contrato", "Q-MAT-CONTRATO"), ("conservadora", "Q-MAT-CONSERVADORA")):
    b, F["Q_" + v] = producto(_E10["Q_" + v][0], _E10["Q_" + v][1], "Q", "products[...%s\\resultado.json]" % t)
    qres[v] = _Q10(b, v)   # FAM10 Q-LOCAL-v1: filas posicion/afirmacion de q-local (las listas de resultado.json)
'''
SUSTITUCIONES = {
    U41: (("ENTRADAS-ENF-v1", "    b = (T / area / rel_).read_bytes()\n",
           "    b = _FUENTE10(T, area, rel_)   # FAM10 ENTRADAS-ENF-v1: rem131 -> integral NUEVO de FAM08 (huellas de su ejecución); rem108 en la raíz Exp8\n"),),
    U44: (("MARCADOR-W-v1", 'W = Path(r"@@W_BS1@@")\n',
           'W = __import__("pathlib").PureWindowsPath("@@W_BS2@@")   # FAM10 MARCADOR-W-v1: directorio de los libros como marcador (no se lee)\n'),
          ("MARCADOR-R-v1", "T = Y.parent\n",
           'T = __import__("pathlib").PureWindowsPath("@@R_BS2@@", "tmp")   # FAM10 MARCADOR-R-v1: raíz histórica como marcador (solo derivado_de.area)\n'),
          ("AUTORIDAD-EXTRAIDA-v1", ("    b = (W / n).read_bytes()\n", '    assert H(b) == h, ("LIBRO_O_DICTAMEN_NO_AUTENTICO", n)\n'),
           "    b = _LIBRO10(k, n, h)   # FAM10 AUTORIDAD-EXTRAIDA-v1: resumen ligado a la huella del original (libro) o huella extraída (dictamen)\n"),
          ("ENLACE-SINTESIS-v1", ('qp = libro["Q"]["products"]\n', "    qres[v] = json.loads(b)\n"), _U44_PRODUCTOS)),
    U47: (("ENLACE-INTEGRACION-v1 (S)", 'S = R / "tmp" / "paso4_correcciones_sintesis_exp8_desde_rem160"\n',
           "S = _SINTESIS10()   # FAM10 ENLACE-INTEGRACION-v1: carpeta de la síntesis NUEVA validada\n"),
          ("ENLACE-INTEGRACION-v1 (AUT)", ("AUT = {  # clave: (ruta, sha256)\n", "BYTES, DOC = {}, {}\n"),
           "AUT = _AUT10(Y)   # FAM10 ENLACE-INTEGRACION-v1: las mismas 26 claves; cada papel lo ocupa la pieza local de enlace/ENLACE_INTEGRACION.json\n"
           "BYTES, DOC = {}, {}\n")),
    AUD: (("AUDITORIA-REM148-v1 (E)", "E=T/'paso4_integracion_final_enf_desde_rem131'\n", "E=_E10   # FAM10 AUDITORIA-REM148-v1: integral ENF NUEVO de FAM08\n"),
          ("AUDITORIA-REM148-v1 (brechas)", "JL(E/'integ_conciliacion_ENF_INTEGRAL/brechas_celdas.jsonl')", "JL(E/'conciliacion/brechas_celdas.jsonl')"),
          ("AUDITORIA-REM148-v1 (techos)", "JL(E/'integ_ensamblado_ENF_INTEGRAL/enf_techos_integrados.jsonl')", "JL(E/'ensamblado/enf_techos_integrados.jsonl')"),
          ("AUDITORIA-REM148-v1 (producto)", "product=Y/'exp8/ENF_POR_AFIRMACION.jsonl'", "product=_PRODUCTO10")),
}


def adaptado(n: str) -> str:
    """GUION-v1: bytes de <n> (una proyección se autentica por su original) con sus sustituciones (un bloque se fija por su primera y su
    última línea; cada original, una sola vez)."""
    src = (BASE / n).read_bytes()
    need(sha10(src) == codigo()[n], "CODIGO_FAM10_DISTINTO: %s" % n)
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
        except Exception as e:  # noqa: BLE001
            out[n] = _sin_base("%s: %s" % (type(e).__name__, e))[:200]
    return out


# ================================================================================================ ayudas inyectadas
ESTADO: dict = {}


def fuente10(T, area, rel_) -> bytes:
    """ENTRADAS-ENF-v1: las cuatro fuentes rem131 salen del integral NUEVO; el resto, de la raíz Exp8."""
    if area == A131:
        sub, n = rel_.split("/", 1)
        m = {"integ_conciliacion_ENF_INTEGRAL": "conciliacion", "integ_ensamblado_ENF_INTEGRAL": "ensamblado"}
        need(sub in m, "FUENTE_REM131_AJENA: %s" % rel_)
        return (Path(ESTADO["enf_integral"]) / m[sub] / n).read_bytes()
    return (Path(T) / area / rel_).read_bytes()


def libro10(k: str, n: str, h: str) -> bytes:
    """AUTORIDAD-EXTRAIDA-v1: resumen del libro (campos que lee el código) ligado a la huella del original, o huella extraída del dictamen."""
    fu = fuentes()
    if n.endswith(".json"):
        a = fu["autoridad"].get(k) or {}
        need(a.get("libro") == n and a.get("original_sha256") == h, "LIBRO_SIN_RESUMEN_LIGADO: %s" % n)
        raw = (BASE / a["archivo"]).read_bytes()
        need(json.loads(raw)["_resumen_fam10"]["original_sha256"] == h, "RESUMEN_DE_LIBRO_AJENO: %s" % n)
        return raw
    need(any(x["origen"].endswith("/" + n) and x["sha256"] == h for x in fu["solo_procedencia"].values()), "DICTAMEN_NO_EXTRAIDO: %s" % n)
    return b""


def q10(b: bytes, version: str) -> dict:
    """Q-LOCAL-v1: salida de q-local (cabecera + filas posicion/afirmacion) -> {posiciones, afirmaciones} como en resultado.json."""
    ls = [json.loads(x) for x in b.decode("utf-8").splitlines() if x.strip()]
    need(ls and ls[0].get("tipo") == "cabecera" and ls[0].get("version") == version and ls[0].get("m") == "1/2", "Q_LOCAL_SIN_CABECERA_%s" % version)
    pos = [x["fila"] for x in ls[1:] if x.get("tipo") == "posicion"]
    afs = [x["fila"] for x in ls[1:] if x.get("tipo") == "afirmacion"]
    need(len(pos) + len(afs) == len(ls) - 1 and all(f.get("version") == version for f in pos + afs), "Q_LOCAL_FILAS_AJENAS_%s" % version)
    return {"posiciones": pos, "afirmaciones": afs}


def _ayudas() -> dict:
    return {"_FUENTE10": fuente10, "_LIBRO10": libro10, "_ENTRADAS10": lambda: dict(ESTADO["entradas_sintesis"]), "_Q10": q10,
            "_SINTESIS10": lambda: Path(ESTADO["sintesis"]), "_AUT10": lambda Y: dict(ESTADO["aut"](Y))}


def _ejecutar(n: str, args: list) -> tuple:
    """Texto adaptado de <n> como __main__ (sys.argv = [<base>/<n>, *args], cwd = la base) -> (rc, salida JSON, stdout, excepción)."""
    txt = adaptado(n)
    p = BASE / n
    g = {"__name__": "__main__", "__file__": str(p), "__builtins__": builtins}
    g.update(_ayudas())
    viejo, ruta, buf, rc, exc, cwd = sys.argv, list(sys.path), io.StringIO(), 0, None, os.getcwd()
    sys.argv = [str(p)] + [str(x) for x in args]
    try:
        os.chdir(BASE)
        with contextlib.redirect_stdout(buf):
            exec(compile(txt, str(p), "exec"), g)
    except SystemExit as ex:
        rc = 0 if ex.code is None else ex.code
    except Exception:  # noqa: BLE001  (se registra; nunca se toma por éxito)
        rc, exc = None, _sin_base(traceback.format_exc())
    finally:
        sys.argv = viejo
        sys.path[:] = ruta
        os.chdir(cwd)
    texto = _sin_base(buf.getvalue())
    try:
        ult = json.loads(texto)
    except ValueError:
        lin = [x for x in texto.splitlines() if x.strip()]
        try:
            ult = json.loads(lin[-1]) if lin else {}
        except ValueError:
            ult = {}
    return rc, ult, texto, exc


# ================================================================================================ entradas (registros de las familias previas)
def _archivos(d: Path) -> dict:
    return {rel(p): sha_archivo(p) for p in sorted(Path(d).rglob("*")) if p.is_file()}


def entrada_fam08(d, reg) -> dict:
    """Integral ENF de fam08-integrar con su comparación INTEGRAL aceptada; productos con la huella fijada por la ejecución."""
    d, reg = _dentro(d), _dentro(reg)
    ej = leer(d / "ejecucion.json")
    need(ej.get("comando") == "fam08-integrar" and ej.get("exito") is True and ej.get("etiqueta", "").startswith("REPRODUCCION LIMPIA FAM08")
         and ej["conciliacion"]["veredicto"]["aceptada"] is True and ej["ensamblado"]["veredicto"]["aceptada"] is True, "ENF_INTEGRAL_NO_ES_UNA_INTEGRACION_FAM08_ACEPTADA")
    r = leer(reg)
    need(r.get("comando") == "fam08-comparar" and r.get("tarea") == "INTEGRAL" and r.get("nueva") == rel(d)
         and (r.get("estado") or {}).get("reproduccion") == "aceptada", "REGISTRO_FAM08_NO_ACEPTADO_O_AJENO")
    prods = {"conciliacion/" + k: v for k, v in ej["conciliacion"]["productos"].items()}
    prods.update({"ensamblado/" + k: v for k, v in ej["ensamblado"]["productos"].items()})
    for k, v in prods.items():
        need(sha_archivo(d / k) == v, "PRODUCTO_FAM08_CAMBIADO: %s" % k)
    return {"carpeta": rel(d), "registro": rel(reg), "registro_sha256": sha_archivo(reg), "ejecucion_sha256": sha_archivo(d / "ejecucion.json"),
            "productos_sha256": {rel(d / k): v for k, v in sorted(prods.items())},
            "procedencia_de_entradas": {k: (v.get("procedencia") if isinstance(v, dict) and "procedencia" in v
                                            else {t: (w or {}).get("procedencia") for t, w in v.items()} if isinstance(v, dict) else v)
                                        for k, v in (r.get("entradas") or {}).items()},
            "naturaleza": r.get("naturaleza")}


def entrada_cov(d, reg) -> dict:
    d, reg = _dentro(d), _dentro(reg)
    ej = leer(d / "ejecucion.json")
    need(ej.get("comando") == "fam11-ensamblar" and ej.get("exito") is True and ej["conciliacion"]["veredicto"]["aceptada"] is True,
         "COV_NO_ES_UN_ENSAMBLADO_FAM11_ACEPTADO")
    r = leer(reg)
    need(r.get("comando") == "fam11-comparar" and r.get("tarea") == "ENSAMBLADO" and r.get("nueva") == rel(d)
         and (r.get("estado") or {}).get("reproduccion") == "aceptada", "REGISTRO_FAM11_NO_ACEPTADO_O_AJENO")
    p = d / "CONCILIACION" / "CONCILIACION_COV.jsonl"
    need(sha_archivo(p) == ej["productos"]["CONCILIACION_COV.jsonl"], "CONCILIACION_COV_CAMBIADA")
    return {"carpeta": rel(d), "registro": rel(reg), "registro_sha256": sha_archivo(reg), "ejecucion_sha256": sha_archivo(d / "ejecucion.json"),
            "producto": rel(p), "producto_sha256": sha_archivo(p), "procedencia_de_entradas": r.get("entradas"), "naturaleza": r.get("naturaleza")}


def entrada_b(d, reg, unidad: str) -> dict:
    """B1/B2 de fam11-unidad con su registro de fam11-validar aceptado (evidencia, lectura y validación con su huella)."""
    d, reg = _dentro(d), _dentro(reg)
    ej = leer(d / "ejecucion.json")
    need(ej.get("etiqueta", "").startswith("REPRODUCCION LIMPIA FAM11") and ej.get("tarea") == unidad + "-TRABAJO" and ej.get("exito") is True,
         "%s_NO_ES_UNA_UNIDAD_FAM11_COMPLETA" % unidad)
    r = leer(reg)
    need(r.get("comando") == "fam11-validar" and r.get("tarea") == unidad + "-VALIDACION" and r.get("origen") == rel(d) and r.get("aceptada") is True
         and (r.get("veredicto") or {}).get("aceptada") is True, "REGISTRO_%s_NO_ACEPTADO_O_AJENO" % unidad)
    f = {"evidencia": d / "TRABAJO" / ("EVIDENCIA_%s.json" % unidad), "lectura": d / "VALIDACION" / ("LECTURA_%s.json" % unidad),
         "validacion": d / "VALIDACION" / ("VALIDACION_%s.json" % unidad)}
    for k, p in f.items():
        need(sha_archivo(p) == r[k + "_sha256"], "%s_%s_CAMBIADA_DESPUES_DE_VALIDAR" % (unidad, k.upper()))
    return {"carpeta": rel(d), "registro": rel(reg), "registro_sha256": sha_archivo(reg), "ejecucion_sha256": sha_archivo(d / "ejecucion.json"),
            "archivos": {k: rel(p) for k, p in f.items()}, "enlace_b1": r.get("enlace_b1")}


def entrada_p7(p) -> dict:
    p = _dentro(p)
    d = leer(p)
    need(d.get("operacion") == "p7-suplemento" and d.get("concordante") is True and all((d.get("controles") or {}).values())
         and len(d.get("filas") or []) == 7, "P7_NO_ES_UN_SUPLEMENTO_CONCORDANTE")
    return {"archivo": rel(p), "sha256": sha_archivo(p), "filas": d["filas"]}


def entrada_q(d) -> dict:
    d = _dentro(d)
    r = leer(d / "resumen.json")
    need(r.get("operacion") == "q-local" and r.get("concordante") is True and r.get("m") == "1/2", "Q_LOCAL_NO_CONCORDANTE")
    out = {"carpeta": rel(d), "resumen_sha256": sha_archivo(d / "resumen.json")}
    for v in ("contrato", "conservadora"):
        out[v] = {"archivo": rel(d / ("q_local_%s.jsonl" % v)), "sha256": sha_archivo(d / ("q_local_%s.jsonl" % v))}
        need(out[v]["sha256"] is not None and all(r["versiones"][v]["controles"].values()), "Q_LOCAL_%s_AUSENTE" % v.upper())
    return out


def entrada_fam10(d, reg, tarea: str) -> dict:
    """Etapa FAM10 completa con su registro de fam10-validar ACEPTADO (los productos siguen con la misma huella)."""
    d, reg = _dentro(d), _dentro(reg)
    ej = leer(d / "ejecucion.json") if (d / "ejecucion.json").is_file() else {}
    need(ej.get("etiqueta") == ETIQUETA and ej.get("tarea") == tarea and ej.get("exito") is True, "ENTRADA_NO_ES_UNA_ETAPA_%s_COMPLETA" % tarea)
    r = leer(reg)
    need(r.get("comando") == "fam10-validar" and r.get("tarea") == tarea and r.get("aceptada") is True and r.get("origen") == rel(d)
         and r.get("inventory_sha256") == sha_archivo(d / "ejecucion.json"), "REGISTRO_DE_VALIDACION_NO_ACEPTADO_O_AJENO: %s" % tarea)
    for k, v in ej["productos_sha256"].items():
        need(sha_archivo(BASE / k) == v, "PRODUCTO_CAMBIADO_DESPUES_DE_VALIDAR: %s" % k)
    return {"carpeta": rel(d), "registro": rel(reg), "registro_sha256": sha_archivo(reg), "ejecucion_sha256": sha_archivo(d / "ejecucion.json"),
            "productos_sha256": dict(ej["productos_sha256"])}


def entradas_de(tarea: str, entradas: dict) -> dict:
    req = ENTRADAS_DE[tarea]
    need(set(entradas or {}) == set(req), "ENTRADAS_DE_%s: se esperan exactamente %s" % (tarea, sorted(req)))
    e = entradas
    if tarea == "ENF":
        return {"enf_integral": entrada_fam08(e["enf_integral"], e["registro_enf_integral"])}
    if tarea == "SINTESIS":
        return {"enf": entrada_fam10(e["enf"], e["validacion_enf"], "ENF"), "cov": entrada_cov(e["cov"], e["registro_cov"]),
                "p7": entrada_p7(e["p7"]), "q_local": entrada_q(e["q_local"])}
    b1 = entrada_b(e["b1"], e["validacion_b1"], "B1")
    b2 = entrada_b(e["b2"], e["validacion_b2"], "B2")
    eb = b2.get("enlace_b1") or {}
    need(eb.get("unidad_b1") == b1["carpeta"] and eb.get("registro_validacion") == b1["registro"], "B2_NO_CONSUME_ESTE_B1")
    return {"sintesis": entrada_fam10(e["sintesis"], e["validacion_sintesis"], "SINTESIS"), "b1": b1, "b2": b2}


# ================================================================================================ etapas
def _autenticacion_local(e: dict) -> dict:
    fu = {x["archivo"]: x["sha256"] for x in fuentes()["archivos"]}
    a108 = {}
    for r_ in ("conciliacion/ensamblajes/T7_anexo.json", "conciliacion/EXP8_TABLA.json"):
        a = "%s/tmp/%s/%s" % (T10, A108, r_)
        a108[r_] = {"sha256": fu[a], "observado": sha_archivo(BASE / a), "archivo": a, "fijado_por": "fuentes_fam10.json"}
        a108[r_]["conforme"] = a108[r_]["sha256"] == a108[r_]["observado"]
    a131 = {}
    for h, sub in (("integ_conciliacion_ENF_INTEGRAL", "conciliacion"), ("integ_ensamblado_ENF_INTEGRAL", "ensamblado")):
        for n in {"conciliacion": ("brechas_celdas.jsonl", "techos_pares.jsonl"), "ensamblado": ("enf_brechas_resueltas.jsonl", "enf_techos_integrados.jsonl")}[sub]:
            a = "%s/%s/%s" % (e["carpeta"], sub, n)
            a131["%s/%s" % (h, n)] = {"sha256": e["productos_sha256"][a], "observado": sha_archivo(BASE / a), "archivo": a,
                                      "fijado_por": "ejecución de fam08-integrar (%s/ejecucion.json)" % e["carpeta"]}
            a131["%s/%s" % (h, n)]["conforme"] = a131["%s/%s" % (h, n)]["sha256"] == a131["%s/%s" % (h, n)]["observado"]
    doc = {"kind": "autenticacion-local-fam10", "naturaleza": ("ENTRADAS-ENF-v1: ocupa el papel de AUTENTICACION_FUENTES_REM147.json para U41; rem108 desde "
                                                               "la raíz Exp8 (fuentes_fam10.json) y rem131 desde el integral NUEVO de FAM08 con las huellas "
                                                               "fijadas por su ejecución; no autentica documentos de W"),
           "areas": {A108: {"archivos": a108}, A131: {"archivos": a131, "registro": e["registro"], "registro_sha256": e["registro_sha256"]}}}
    doc["conforme"] = all(x["conforme"] for a in doc["areas"].values() for x in a["archivos"].values())
    return doc


def _etapa_enf(sal: Path, ent: dict) -> dict:
    e = ent["enf_integral"]
    aut = _autenticacion_local(e)
    need(aut["conforme"], "AUTENTICACION_LOCAL_NO_CONFORME")
    (sal / "fuentes").mkdir(parents=True)
    pa = sal / "fuentes" / "AUTENTICACION_LOCAL_FAM10.json"
    _escribir_x(pa, aut)
    ESTADO.clear()
    ESTADO["enf_integral"] = e["carpeta"]
    rc, ult, stdout, exc = _ejecutar(U41, [T10, rel(pa), rel(sal)])
    (sal / "conciliar_stdout.txt").write_text(stdout, encoding="utf-8", newline="\n")
    prods = {rel(sal / n): sha_archivo(sal / n) for n in ("ENF_POR_AFIRMACION.jsonl", "COBERTURA_EXP8.json", "COBERTURA_EXP8.md", "RESUMEN_POR_PAIS.json")
             if (sal / n).is_file()}
    prods[rel(pa)] = sha_archivo(pa)
    return {"guion": U41, "rc": rc, "excepcion": exc, "conforme": ult.get("conforme"), "fallos": ult.get("fallos"), "recuentos": ult.get("recuentos"),
            "testigos": ult.get("testigos"), "productos_sha256": prods, "exito": rc == 0 and exc is None and ult.get("conforme") is True and len(prods) == 5}


def _etapa_sintesis(sal: Path, ent: dict) -> dict:
    enf, cov, p7, q = ent["enf"], ent["cov"], ent["p7"], ent["q_local"]
    (sal / "entradas").mkdir(parents=True)
    pp = sal / "entradas" / "SUPLEMENTO_P7.jsonl"
    with pp.open("xb") as fh:
        for f in p7["filas"]:
            fh.write(json.dumps(f, ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\n")
    enf_p = "%s/ENF_POR_AFIRMACION.jsonl" % enf["carpeta"]
    E10 = {"ENF": (enf_p, enf["productos_sha256"][enf_p]), "COV": (cov["producto"], cov["producto_sha256"]), "P7": (rel(pp), sha_archivo(pp)),
           "Q_contrato": (q["contrato"]["archivo"], q["contrato"]["sha256"]), "Q_conservadora": (q["conservadora"]["archivo"], q["conservadora"]["sha256"])}
    enlace = {"kind": "enlace-sintesis-fam10", "adaptacion": "ENLACE-SINTESIS-v1 / Q-LOCAL-v1 / AUTORIDAD-EXTRAIDA-v1",
              "naturaleza": ("los productos que U44 cita como autorizados por sus libros son aquí los NUEVOS, cada uno ligado a su registro; el campo "
                             "autorizada_por del manifiesto nombra el PAPEL (libro histórico y su huella), no una aceptación de Codex de estos bytes"),
              "productos": {k: {"ruta": v[0], "sha256": v[1]} for k, v in E10.items()},
              "registros": {"ENF": {"registro": enf["registro"], "sha256": enf["registro_sha256"], "tipo": "fam10-validar ENF aceptado"},
                            "COV": {"registro": cov["registro"], "sha256": cov["registro_sha256"], "tipo": "fam11-comparar ENSAMBLADO aceptado",
                                    "procedencia_de_entradas": cov["procedencia_de_entradas"]},
                            "P7": {"origen": p7["archivo"], "sha256": p7["sha256"], "tipo": "p7-suplemento concordante (filas serializadas con sort_keys)"},
                            "Q": {"carpeta": q["carpeta"], "resumen_sha256": q["resumen_sha256"], "tipo": "q-local concordante"}},
              "libros": {k: v for k, v in fuentes()["autoridad"].items()}}
    _escribir_x(sal / "ENLACE_SINTESIS.json", enlace)
    ESTADO.clear()
    ESTADO["entradas_sintesis"] = E10
    rc, ult, stdout, exc = _ejecutar(U44, [rel(sal)])
    (sal / "constructor_stdout.txt").write_text(stdout, encoding="utf-8", newline="\n")
    prods = {rel(sal / n): sha_archivo(sal / n) for n in ("sintesis/EXP8_POR_AFIRMACION.jsonl", "sintesis/RESUMEN_EXP8.json", "fuentes/MANIFIESTO_SINTESIS.json")
             if (sal / n).is_file()}
    prods.update({rel(pp): sha_archivo(pp), rel(sal / "ENLACE_SINTESIS.json"): sha_archivo(sal / "ENLACE_SINTESIS.json"),
                  rel(sal / "constructor_stdout.txt"): sha_archivo(sal / "constructor_stdout.txt")})
    coj = (ult or {}).get("cotejos") or {}
    return {"guion": U44, "rc": rc, "excepcion": exc, "cotejos": coj, "filas_sha256": (ult or {}).get("filas_sha256"), "entradas_sintesis": E10,
            "productos_sha256": prods, "exito": rc == 0 and exc is None and bool(coj) and all(v for k, v in coj.items() if k != "nota") and len(prods) == 6}


def _libros_locales(sal: Path, ent: dict) -> dict:
    """ENLACE-INTEGRACION-v1: piezas locales que ocupan los papeles de libros, auditoría y enlace de rem170 (derivadas de la lectura validada)."""
    s, b1, b2 = ent["sintesis"], ent["b1"], ent["b2"]
    ed = sal / "enlace"
    ed.mkdir(parents=True)
    filas_p = BASE / s["carpeta"] / "sintesis" / "EXP8_POR_AFIRMACION.jsonl"
    S = [json.loads(x) for x in lineas_de(filas_p)]
    pos = {f["afirmacion"]: i for i, f in enumerate(S)}
    l1, l2 = leer(BASE / b1["archivos"]["lectura"]), leer(BASE / b2["archivos"]["lectura"])
    ev = leer(BASE / b2["archivos"]["evidencia"])
    U_hex = l1["datos_validados"]["U_C2_hex"]
    U = Fraction(float.fromhex(U_hex))
    ag = ev["b1"]["afirmacion_grupo"]
    dv = l2["datos_validados"]
    lect = {g["grupo"]: g for g in l2["lectura"]["grupos"]}
    chk = {"U_C2_hex_lectura_b1": l1["lectura"]["U_C2_hex"] == U_hex and float.fromhex(U_hex) == l1["datos_validados"]["U_C2"],
           "U_C2_lectura_b2_igual_b1": Fraction(dv["U_C2"]) == U and all(Fraction(g["U_C2"]) == U for g in lect.values()),
           "seis_grupos": sorted(dv["grupos"]) == sorted(lect) and len(lect) == 6, "contextos_pendientes_0": dv["contextos_pendientes"] == 0}
    grupos, ver = [], {}
    for g in sorted(dv["grupos"]):
        x = dv["grupos"][g]
        L = Fraction(float.fromhex(x["L_K1_hex"]))
        G = U - L
        m = -EPS - G
        afs = list(lect[g]["afirmaciones"])
        chk["L_K1_hex_float_" + g] = L == Fraction(x["L_K1"]) and lect[g]["L_K1_hex"] == x["L_K1_hex"]
        chk["G_hi_igual_lectura_b2_" + g] = Fraction(lect[g]["G_hi_exacto"]) == G
        chk["afirmaciones_evidencia_igual_lectura_" + g] = sorted(afs) == sorted(a for a, gg in ag.items() if gg == g)
        ver[g] = (G, "robust_infeasible" if G <= -EPS else "sin_resolucion")
        grupos.append({"group": g, "contexts": x["contextos"], "L_K1": x["L_K1"], "L_K1_hex": x["L_K1_hex"], "G_hi_exact": fx(G), "G_hi": float(G),
                       "margin_below_minus_eps_exact": fx(m), "margin": float(m), "claims": afs, "accepted_transformed_verdict": ver[g][1],
                       "parent_verdict_unchanged": True})
    claims = []
    for a in sorted(ag):
        need(a in pos, "AFIRMACION_B2_FUERA_DE_LA_SINTESIS: %s" % a)
        f = S[pos[a]]
        G, v = ver[ag[a]]
        esc = f["COV"]["escenario"]
        claims.append({"afirmacion": a, "grupo": ag[a], "parent_category": f["categoria_original"], "historical_COV_conclusion": f["COV"]["conclusion_historica"],
                       "accepted_COV_verdict": v, "G_hi_exact": fx(G), "eps": "1/100",
                       "scenario": "ABL-COV phi/2" if esc.startswith("ABL-COV phi/2 ") else esc, "source_synthesis_line": pos[a] + 1})
    desconocidas = sorted(f["afirmacion"] for f in S if f["conjunto_padre"] == "inconclusa" and f["COV"]["conclusion"] == "no_decidida_por_testigos")
    chk["doce_son_las_desconocidas_de_la_sintesis"] = sorted(ag) == desconocidas and len(ag) == 12
    chk["doce_colombianas"] = all(S[pos[a]]["dimensiones"]["pais"] == "COL" for a in ag if a in pos)
    chk["regla_inclusiva_en_los_seis_grupos"] = all(v == "robust_infeasible" for _, v in ver.values())
    chk["union_1920"] = dv["contextos_acotados"] == 1920
    # inventarios locales de B1 y B2 (papel de audit/entrega.json de las entregas históricas)
    piezas_ = {}
    for u, b in (("B1", b1), ("B2", b2)):
        inv = {"kind": "inventario-local-fam10", "unidad": u, "carpeta": b["carpeta"], "archivos": _archivos(BASE / b["carpeta"]),
               "registro_validacion": {"ruta": b["registro"], "sha256": b["registro_sha256"]},
               "naturaleza": "ocupa el papel del inventario de la entrega %s histórica para U47 (archivos de la carpeta NUEVA)" % u}
        p = ed / ("INVENTARIO_%s_LOCAL.json" % u)
        _escribir_x(p, inv)
        piezas_["inventario_" + u] = p
    sp = s["carpeta"] + "/sintesis/EXP8_POR_AFIRMACION.jsonl"
    enl = {"kind": "enlace-doce-local-fam10", "synthesis": sp, "synthesis_sha256": sha_archivo(filas_p),
           "naturaleza": "ocupa el papel de review_20261108_rem170_claims_join.json: enlace de las doce afirmaciones B2 con las líneas de la síntesis NUEVA",
           "claims": [{"afirmacion": c["afirmacion"], "grupo": c["grupo"], "linea": c["source_synthesis_line"], "categoria_original": c["parent_category"],
                       "conclusion_COV": S[c["source_synthesis_line"] - 1]["COV"]["conclusion"], "conclusion_COV_historica": c["historical_COV_conclusion"],
                       "pais": S[c["source_synthesis_line"] - 1]["dimensiones"]["pais"]} for c in claims]}
    _escribir_x(ed / "ENLACE_DOCE_LOCAL.json", enl)
    aud = {"kind": "auditoria-b2-local-fam10", "naturaleza": ("ocupa el papel de la auditoría rem170: aritmética exacta U_C2 − L_K1 desde la lectura B1 "
                                                             "y B2 validadas y enlace de las doce; NO es una auditoría de Codex"),
           "U_C2": {"hex": U_hex, "exacto": fx(U)}, "eps": "1/100", "regla": "G_hi = U_C2 − L_K1 ≤ −1/100 (inclusiva)",
           "grupos": {g["group"]: {"L_K1_hex": g["L_K1_hex"], "G_hi_exacto": g["G_hi_exact"], "margen_exacto": g["margin_below_minus_eps_exact"],
                                   "veredicto": g["accepted_transformed_verdict"]} for g in grupos},
           "comprobaciones": chk, "aceptada": all(chk.values())}
    _escribir_x(ed / "AUDITORIA_B2_LOCAL.json", aud)
    lb1 = {"kind": "libro-b1-local-fam10", "naturaleza": "ocupa el papel del libro B1 rem167 para U47; NO es un libro de Codex: deriva de la lectura B1 validada",
           "products": {str(Path(b1["archivos"]["lectura"])): sha_archivo(BASE / b1["archivos"]["lectura"])},
           "inventory_sha256": sha_archivo(piezas_["inventario_B1"]), "U_C2": l1["datos_validados"]["U_C2"], "U_C2_hex": U_hex, "U_C2_exact": fx(U),
           "registro_validacion": {"ruta": b1["registro"], "sha256": b1["registro_sha256"]}}
    _escribir_x(ed / "LIBRO_B1_LOCAL.json", lb1)
    X = {"X_estado_b2": b2["carpeta"] + "/ejecucion.json", "X_evidencia_b2": b2["archivos"]["evidencia"], "X_plan_inicio": b2["carpeta"] + "/TRABAJO/PLAN_INICIO.json",
         "X_validacion_b2": b2["archivos"]["validacion"], "X_lectura_b2": b2["archivos"]["lectura"]}
    todos = all(v == "robust_infeasible" for _, v in ver.values())
    lb2 = {"kind": "libro-b2-local-fam10",
           "naturaleza": ("ocupa el papel del libro B2 rem170 para U47; NO es un libro de Codex: grupos, cotas y doce afirmaciones derivados de la "
                          "lectura B1 → B2 validada y de la síntesis NUEVA; G_hi y el margen, con aritmética exacta; «accepted_*» = regla inclusiva "
                          "cumplida y registro B2 aceptado"),
           "products": {str(Path(v)): sha_archivo(BASE / v) for v in X.values()}, "inventory_sha256": sha_archivo(piezas_["inventario_B2"]),
           "old_synthesis_sha256": sha_archivo(filas_p), "B1_accepted_ledger_sha256": sha_archivo(ed / "LIBRO_B1_LOCAL.json"),
           "review_sha256": b2["registro_sha256"], "audit_sha256": sha_archivo(ed / "AUDITORIA_B2_LOCAL.json"),
           "claims_join_sha256": sha_archivo(ed / "ENLACE_DOCE_LOCAL.json"), "accepted": aud["aceptada"],
           "transformed_classification_accepted": todos, "accepted_verdict_under_COV": "robust_infeasible" if todos else "sin_resolucion",
           "formal_closures": [], "D_EXP8_adopted": False, "N3_adopted": False, "U_C2": l2["datos_validados"]["U_C2"], "U_C2_hex": U_hex, "U_C2_exact": fx(U),
           "groups": grupos, "claims": claims, "claims_count": len(claims), "groups_count": len(grupos)}
    _escribir_x(ed / "LIBRO_B2_LOCAL.json", lb2)
    s_ej = s["carpeta"] + "/ejecucion.json"
    papeles = {
        "dictamen_rem170": (b2["registro"], "registro de fam11-validar B2 aceptado (acto local de aceptación técnica; no es un dictamen de Codex)"),
        "libro_B2": (rel(ed / "LIBRO_B2_LOCAL.json"), "libro B2 LOCAL derivado"),
        "auditoria_rem170": (rel(ed / "AUDITORIA_B2_LOCAL.json"), "auditoría aritmética local"),
        "enlace_rem170": (rel(ed / "ENLACE_DOCE_LOCAL.json"), "enlace local de las doce"),
        "hallazgos_rem170": (rel(ed / "ENLACE_INTEGRACION.json"), "esta declaración de enlace (no hay hallazgos de revisor)"),
        "libro_B1": (rel(ed / "LIBRO_B1_LOCAL.json"), "libro B1 LOCAL derivado"),
        "libro_sintesis_rem161": (s["registro"], "registro de fam10-validar SINTESIS aceptado"),
        "libro_P7": (fuentes()["autoridad"]["P7"]["archivo"], "resumen del libro rem155 (campos que lee U47)"),
        "libro_Q_DIAG": (fuentes()["autoridad"]["Q_DIAG"]["archivo"], "resumen del libro rem156 (campos que lee U47)"),
        "S_inventario": (s_ej, "ejecución de la etapa SINTESIS (inventario de sus productos)"),
        "S_informe": (s["carpeta"] + "/constructor_stdout.txt", "salida del constructor de la síntesis"),
        "S_filas": (sp, "filas de la síntesis NUEVA"), "S_resumen": (s["carpeta"] + "/sintesis/RESUMEN_EXP8.json", "resumen de la síntesis NUEVA"),
        "S_manifiesto": (s["carpeta"] + "/fuentes/MANIFIESTO_SINTESIS.json", "manifiesto de la síntesis NUEVA"),
        "S_constructor": (U44, "constructor de la síntesis (proyección saneada del original e96814df…)"),
        "X_inventario": (rel(piezas_["inventario_B2"]), "inventario local de la carpeta B2 NUEVA"),
        "X_informe": (b2["carpeta"] + "/trabajo_stdout.txt", "salida del trabajador B2"),
        **{k: (v, "producto B2 NUEVO") for k, v in X.items()},
        "B1_inventario": (rel(piezas_["inventario_B1"]), "inventario local de la carpeta B1 NUEVA"),
        "B1_lectura": (b1["archivos"]["lectura"], "lectura B1 NUEVA validada"),
        "soporte_rem162": ("datos/fam11/fuentes/CONTEXTO_COL_POR_GRUPO.json", "soporte rem162 (copia exacta de FAM11)"),
        "esquema_declarado": (rel(sal / "construccion" / "ESQUEMA_DECLARADO_REM170.json"), "esquema declarado (copia exacta, escrita antes de construir)")}
    decl = {"kind": "enlace-integracion-fam10", "adaptacion": "ENLACE-INTEGRACION-v1",
            "naturaleza": ("tabla de papeles de U47: cada clave de autenticación histórica la ocupa la pieza local indicada; los nombres de archivo "
                           "que U47 escribe en resolucion_global.procedencia son ETIQUETAS de papel; las huellas son las de estas piezas"),
            "papeles": {k: {"ruta": v[0], "sha256": (sha_archivo(BASE / v[0]) if k != "hallazgos_rem170" else None), "pieza": v[1]} for k, v in papeles.items()}}
    _escribir_x(ed / "ENLACE_INTEGRACION.json", decl)
    aut = {k: (Path(v[0]), sha_archivo(BASE / v[0])) for k, v in papeles.items() if k != "esquema_declarado"}
    return {"aut": aut, "comprobaciones": chk, "aceptada": aud["aceptada"]}


def _etapa_integracion(sal: Path, ent: dict) -> dict:
    (sal / "construccion").mkdir(parents=True)
    pe = sal / "construccion" / "ESQUEMA_DECLARADO_REM170.json"
    with pe.open("xb") as fh:
        fh.write((BASE / ESQUEMA).read_bytes())
    loc = _libros_locales(sal, ent)
    need(sorted(loc["aut"]) + ["esquema_declarado"] != [], "SIN_PAPELES")
    aut = loc["aut"]

    def aut10(Y):
        out = dict(aut)
        out["esquema_declarado"] = (Path(Y) / "construccion/ESQUEMA_DECLARADO_REM170.json", "f4e474457cf0e70135f02da7cb0333ec8be6f7334452969c9a1ffb7bb33dd443")
        need(len(out) == 26, "AUT10_NO_TIENE_26_CLAVES")
        return out
    ESTADO.clear()
    ESTADO["sintesis"] = ent["sintesis"]["carpeta"]
    ESTADO["aut"] = aut10
    rc, ult, stdout, exc = _ejecutar(U47, [T10, rel(sal)])
    (sal / "constructor_stdout.txt").write_text(stdout, encoding="utf-8", newline="\n")
    prods = {rel(sal / n): sha_archivo(sal / n) for n in ("sintesis/EXP8_POR_AFIRMACION.jsonl", "sintesis/COV12_RESOLUCION_GLOBAL.jsonl",
                                                          "sintesis/RESUMEN_EXP8.json", "fuentes/MANIFIESTO_SINTESIS.json") if (sal / n).is_file()}
    for p in sorted((sal / "enlace").glob("*.json")):
        prods[rel(p)] = sha_archivo(p)
    prods[rel(pe)] = sha_archivo(pe)
    coj = (ult or {}).get("cotejos") or {}
    return {"guion": U47, "rc": rc, "excepcion": exc, "cotejos": coj, "enlace_local": {"comprobaciones": loc["comprobaciones"], "aceptada": loc["aceptada"]},
            "productos_sha256": prods, "exito": rc == 0 and exc is None and loc["aceptada"] and bool(coj) and all(v for k, v in coj.items() if k != "nota")}


ETAPA_FN = {"ENF": _etapa_enf, "SINTESIS": _etapa_sintesis, "INTEGRACION": _etapa_integracion}


def lecturas(rastro, informe: dict) -> dict:
    en = informe["en_el_paquete"]
    return {"archivo": "archivos_leidos.json", "en_el_paquete": len(en), "aperturas_del_interprete": informe["aperturas_del_interprete"],
            "fuera_del_paquete_y_del_interprete": informe["fuera_del_paquete_y_del_interprete"],
            "codigo_fam10_leido": sorted(x for x in en if x in codigo()), "autoridad_leida": sorted(x for x in en if x.startswith("datos/fam10/autoridad/")),
            "raiz_exp8_leidos": sum(1 for x in en if x.startswith(T10 + "/")),
            "referencias_leidas": sorted(x for x in en if x.startswith("referencias/")),
            "salidas_leidas": sorted(x for x in rastro.dentro if x.startswith("salidas/") and (BASE / x).is_file()),
            "referencia_esperada_leida": any(x.startswith(PROHIBIDAS) for x in en)}


def entorno() -> dict:
    import platform
    return {"python": platform.python_version(), "hash_seed": os.environ.get("PYTHONHASHSEED"), "hash_randomization": sys.flags.hash_randomization,
            "hilos": {k: os.environ.get(k) for k in F1().HILOS}, "TZ": os.environ.get("TZ")}


def correr(tarea: str, salida: Path, entradas: dict) -> dict:
    """fam10-etapa: una etapa en la carpeta NUEVA `salida` (dentro de la base)."""
    T0 = time.time()
    rastro = F1().Rastro()
    need(tarea in ETAPAS, "ETAPA_FUERA_DE_FAM10: %s" % tarea)
    malos = fuentes_alteradas("calculo")
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam10.json; no se calcula): %s" % malos[:5])
    ent = entradas_de(tarea, entradas)
    salida = Path(salida)
    need(not salida.exists(), "LA_SALIDA_YA_EXISTE")
    salida.mkdir(parents=True)
    sal = _dentro(salida)
    inicio = utc()
    det = ETAPA_FN[tarea](sal, ent)
    fin = utc()
    informe = rastro.informe()
    (sal / "archivos_leidos.json").write_bytes((json.dumps(informe, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    ej = {"etiqueta": ETIQUETA, "tarea": tarea, "operacion": OPERACION_DE[tarea], "naturaleza": NATURALEZA[tarea], "adaptaciones": list(ADAPTACIONES),
          "entradas": {k: {kk: vv for kk, vv in v.items() if kk != "filas"} for k, v in ent.items()}, "inicio_utc": inicio, "fin_utc": fin,
          "detalle": {k: v for k, v in det.items() if k != "productos_sha256"}, "rc": det.get("rc"), "excepcion": det.get("excepcion"),
          "productos_sha256": det.get("productos_sha256") or {},
          "codigo": {det["guion"]: {"archivo_sha256": sha_archivo(BASE / det["guion"]), "original_sha256": codigo()[det["guion"]],
                                    "adaptado_sha256": sha(adaptado(det["guion"]).encode("utf-8")),
                                    "sustituciones": [s[0] for s in SUSTITUCIONES[det["guion"]]]}},
          "segundos": round(time.time() - T0, 3), "entorno": entorno(), "lecturas": lecturas(rastro, informe)}
    ej["exito"] = bool(det.get("exito")) and not ej["lecturas"]["fuera_del_paquete_y_del_interprete"] and not ej["lecturas"]["referencia_esperada_leida"]
    _escribir(sal / "ejecucion.json", ej)
    return ej


# ================================================================================================ validación (sin la referencia)
def _auditoria_enf(nueva: Path, integral: str) -> dict:
    """AUDITORIA-REM148-v1: parte científica de la auditoría rem148 sobre el producto NUEVO (enlaces, G padre y cotas certificadas)."""
    checks, source_hashes = {}, {}

    def ck(n, v):
        checks[n] = bool(v)
        if not v:
            raise AssertionError(n)

    def HF(p):
        return sha(Path(p).read_bytes())

    def auth(p, h):
        p = Path(p)
        real = HF(p)
        assert real == h, str(p)
        source_hashes[str(p)] = real
        return p
    ns = {"T": R10 / "tmp", "F": Fraction, "Counter": Counter, "H": sha, "HF": HF, "J": lambda p: json.loads(Path(p).read_bytes()),
          "JL": lambda p: [json.loads(x) for x in Path(p).read_bytes().splitlines() if x.strip()], "checks": checks, "source_hashes": source_hashes,
          "ck": ck, "auth": auth, "_E10": BASE / integral, "_PRODUCTO10": nueva / "ENF_POR_AFIRMACION.jsonl", "__builtins__": builtins}
    exc = None
    try:
        exec(compile(adaptado(AUD), str(BASE / AUD), "exec"), ns)
    except Exception:  # noqa: BLE001
        exc = _sin_base(traceback.format_exc())[-1500:]
    rows = ns.get("rows") or []
    margins = ns.get("margins") or []
    counts = Counter(r["conclusion"] for r in rows)
    return {"bloque": AUD, "excepcion": exc, "comprobaciones": checks, "recuentos": dict(sorted(counts.items())),
            "ranuras_enlazadas": ns.get("slots"), "celdas_unicas": len(ns.get("cells") or ()), "margen_minimo": fx(min(margins)) if margins else None,
            "garantias": dict(ns.get("guarantee") or {}), "cruce_de_signos": dict(ns.get("sign_cross") or {}),
            "por_pais": {k: dict(v) for k, v in (ns.get("countries") or {}).items()}, "filas": rows,
            "aceptada": exc is None and len(checks) == 6 and all(checks.values())}


def _validar_enf(nueva: Path, ej: dict) -> dict:
    integral = ej["entradas"]["enf_integral"]["carpeta"]
    aud = _auditoria_enf(nueva, integral)
    cov = leer(nueva / "COBERTURA_EXP8.json")
    ls = lineas_de(nueva / "ENF_POR_AFIRMACION.jsonl")
    filas = [json.loads(x) for x in ls]
    est = {"cobertura_conforme": cov.get("conforme") is True and cov.get("fallos") == [],
           "filas_1728_unicas": len(filas) == 1728 and len({f["afirmacion"] for f in filas}) == 1728,
           "serializacion_reproducible": all(json.dumps(f, ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\n" == x for f, x in zip(filas, ls)),
           "huella_declarada_en_cobertura": cov.get("ENF_POR_AFIRMACION_sha256") == sha_archivo(nueva / "ENF_POR_AFIRMACION.jsonl"),
           "filas_padre_leidas_dos_por_robusta": (cov.get("testigos") or {}).get("filas_padre_leidas_para_cell_id_de_robustas")
           == 2 * sum(1 for f in filas if f["categoria_original"] == "robusta_infactible_certificada")}
    # comprobación científica de la línea 175 de la auditoría rem148 (fuera del bloque 49–116): resumen por país = afirmaciones reconstruidas
    rp = leer(nueva / "RESUMEN_POR_PAIS.json").get("por_pais") or {}
    est["resumen_por_pais_igual_a_las_afirmaciones_reconstruidas"] = bool(rp) and set(rp) == set(aud["por_pais"]) and all(
        v["universo"]["canal_eta_f"] == aud["por_pais"][k] for k, v in rp.items())
    canal = Counter(f["canal_eta_f"] for f in filas)
    return {"validador": ("U42 NO LOCALIZADO: se ejecuta la parte científica de la auditoría rem148, que por decisión del autor (2026-11-18, "
                          "L-ENF-AFIRMACION-AUDITORIA-REM148) es la validación del ENF regenerado; no acredita la identidad de U42"),
            "auditoria_rem148": aud, "estructura": est, "canal_eta_f": dict(sorted(canal.items())),
            "productos_sha256": {k: v for k, v in ej["productos_sha256"].items()}, "aceptada": aud["aceptada"] and all(est.values())}


LADO_ENF = ("clave_transformada_sha256", "cell_id", "unidad", "conjunto", "estado_evidencia", "estado_techo_historico", "origen_G", "resolucion",
            "certificado_resolucion_sha256", "signo_padre", "signo_enf", "G_padre_ENF", "C2_enf", "K1_reutilizado", "G_enf", "dG", "veredicto_T7",
            "enlazado", "motivo_no_enlace")
LADO_COV = ("clave_cov", "cell_id", "unidad", "signo_padre", "signo_cov_certificado", "g_lo", "g_hi", "C2_cov", "G_padre", "K1", "error_R", "error_normalizado")


def _sel(d, ks):
    return {k: d.get(k) for k in ks} if isinstance(d, dict) else None


def _validar_sintesis(nueva: Path, ej: dict) -> dict:
    E10 = ej["detalle"]["entradas_sintesis"]
    for k, (r_, h) in E10.items():
        need(sha_archivo(BASE / r_) == h, "ENTRADA_DE_LA_SINTESIS_CAMBIADA: %s" % k)
    E = {f["afirmacion"]: f for f in leer_jsonl(BASE / E10["ENF"][0])}
    C = {f["afirmacion"]: f for f in leer_jsonl(BASE / E10["COV"][0])}
    P = leer_jsonl(BASE / E10["P7"][0])
    PA = {f["afirmacion"]: f for f in P}
    Q = {v: q10((BASE / E10["Q_" + v][0]).read_bytes(), v) for v in ("contrato", "conservadora")}
    QA = {v: {a["afirmacion"]: a for a in Q[v]["afirmaciones"]} for v in Q}
    QP = {v: {(p["afirmacion"], p["lado"]): p for p in Q[v]["posiciones"]} for v in Q}
    ls = lineas_de(nueva / "sintesis" / "EXP8_POR_AFIRMACION.jsonl")
    filas = [json.loads(x) for x in ls]
    res = leer(nueva / "sintesis" / "RESUMEN_EXP8.json")
    man = leer(nueva / "fuentes" / "MANIFIESTO_SINTESIS.json")
    qd = json.loads(libro10("Q_DIAG", fuentes()["autoridad"]["Q_DIAG"]["libro"], fuentes()["autoridad"]["Q_DIAG"]["original_sha256"]))
    malos = Counter()
    for f in filas:
        a = f["afirmacion"]
        e, c, p = E.get(a), C.get(a), PA.get(a)
        if e is None or c is None:
            malos["clave_ausente_en_ENF_o_COV"] += 1
            continue
        if f["categoria_original"] != e["categoria_original"] or f["categoria_original"] != c["categoria_original"]:
            malos["categoria"] += 1
        for lado in ("sup", "inf"):
            if f["ENF"]["lados"][lado] != _sel(e.get(lado), LADO_ENF):
                malos["ENF_lado"] += 1
            if f["COV"]["lados"][lado] != _sel(c.get(lado), LADO_COV):
                malos["COV_lado"] += 1
        if (f["ENF"]["conclusion_historica"], f["ENF"]["cobertura_historica"], f["ENF"]["descompuesta_rem108"]) != (e["canal_eta_f"], e["cobertura_ENF"], e.get("descompuesta_rem108")):
            malos["ENF_historico"] += 1
        if (f["COV"]["conclusion_historica"], f["COV"]["cobertura_historica"]) != (c["canal_phi"], c["cobertura_COV"]):
            malos["COV_historico"] += 1
        for v in ("contrato", "conservadora"):
            qa, fv = QA[v].get(a) or {}, f["Q"]["versiones"][v]
            if (fv["canal"], fv["region"], fv["lados_demostrados"], fv["cobertura"]) != (qa.get("canal"), qa.get("region"), qa.get("lados_demostrados"), qa.get("cobertura")):
                malos["Q_afirmacion_" + v] += 1
            for lado in ("sup", "inf"):
                if fv["posiciones"][lado] != _sel(QP[v].get((a, lado)), ("g_lo", "g_hi", "lado_veredicto", "signo", "unidad", "origen")):
                    malos["Q_posicion_" + v] += 1
        if p is not None:
            if not (f["P7"] and f["P7"]["aplicaciones"] == 1 and f["P7"]["unidad"] == p["unidad"] and f["ENF"]["conclusion"] == p["canales"]["ENF"]["canal"]
                    and f["COV"]["conclusion"] == p["canales"]["COV"]["canal"] and f["ENF"]["suplemento_P7"] and f["COV"]["suplemento_P7"]):
                malos["P7_aplicacion"] += 1
        elif f["P7"] is not None or f["ENF"]["conclusion"] != e["canal_eta_f"] or f["COV"]["conclusion"] != c["canal_phi"]:
            malos["P7_fuera_de_sus_siete"] += 1
    inc = [f for f in filas if f["conjunto_padre"] == "inconclusa"]
    rob = [f for f in filas if f["conjunto_padre"] == "robusta"]
    cnt = lambda it: dict(sorted(Counter(it).items()))  # noqa: E731
    enf_f, cov_f = cnt(f["ENF"]["conclusion"] for f in filas), cnt(f["COV"]["conclusion"] for f in filas)
    cov_nd_inc = [f for f in inc if f["COV"]["conclusion"] == "no_decidida_por_testigos"]
    cov_nd_rob = [f for f in rob if f["COV"]["conclusion"] == "no_decidida_por_testigos"]
    pres = [f for f in inc if f["COV"]["conclusion"] == "inconclusa_preservada" and f["COV"]["lados"]["sup"] and f["COV"]["lados"]["inf"]]
    eps_ok = all(Fraction(f["COV"]["lados"]["sup"]["g_lo"]) > -EPS and Fraction(f["COV"]["lados"]["inf"]["g_hi"]) < EPS for f in pres
                 if not f["P7"])
    ambos_neg = [f for f in pres if f["COV"]["lados"]["sup"]["signo_cov_certificado"] == -1 and f["COV"]["lados"]["inf"]["signo_cov_certificado"] == -1]
    pos_q = Counter(f["Q"]["versiones"]["contrato"]["posiciones"][l]["origen"] for f in filas for l in ("sup", "inf"))
    q_ok = {v: cnt(f["Q"]["versiones"][v]["canal"] for f in filas) for v in ("contrato", "conservadora")}
    p7f = [f for f in filas if f["P7"]]
    mg = qd["margins"]
    chk = {
        "filas_1728_unicas_mismo_universo": len(filas) == 1728 and {f["afirmacion"] for f in filas} == set(E) == set(C),
        "serializacion_reproducible": all(json.dumps(f, ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\n" == x for f, x in zip(filas, ls)),
        "enlaces_ENF_COV_Q_P7_por_clave_y_lado": not malos,
        "padre_1712_inconclusas_16_robustas": len(inc) == 1712 and len(rob) == 16 and all(f["dimensiones"]["pais"] == "MEX" for f in rob),
        "ENF_1712_preservadas_16_sin_decidir": enf_f == {"inconclusa_preservada": 1712, ENF_NODEC: 16},
        "COV_1700_preservadas_28_sin_decidir": cov_f == {"inconclusa_preservada": 1700, "no_decidida_por_testigos": 28},
        "COV_sin_decidir_12_COL_inconclusas_16_MEX_robustas": len(cov_nd_inc) == 12 and all(f["dimensiones"]["pais"] == "COL" for f in cov_nd_inc)
        and len(cov_nd_rob) == 16 and all(f["dimensiones"]["pais"] == "MEX" for f in cov_nd_rob),
        "regla_eps_COV_preservadas_ambos_testigos": eps_ok,
        "COV_ocho_micro_con_ambos_negativos": len(ambos_neg) == 8 and all(f["dimensiones"]["bloque"] == "micro" for f in ambos_neg),
        "Q_por_version_3456_posiciones_1712_preservadas_16_refutadas": all(len(Q[v]["posiciones"]) == 3456 and q_ok[v] == {"inconclusa_preservada": 1712,
                                                                                                                           "robustez_refutada_por_testigo_sup": 16} for v in Q),
        "Q_posiciones_3449_padre_7_P7": dict(pos_q) == {"filas_padre_aceptadas": 3449, "suplemento_P7_lado_padre_faltante": 7},
        "P7_siete_una_vez_cuatro_unidades": len(p7f) == 7 and len(P) == 7 and len(PA) == 7 and all(f["P7"]["aplicaciones"] == 1 for f in p7f)
        and len({f["P7"]["unidad"] for f in p7f}) == 4,
        "descomposiciones_1705_y_siete_sin_descomposicion_son_P7": sum(1 for f in filas if f["ENF"]["descompuesta_rem108"] is True) == 1705
        and sorted(f["afirmacion"] for f in inc if f["ENF"]["descompuesta_rem108"] is not True) == sorted(PA),
        "Q_m_1_2_separado_del_diagnostico_general": res["Q"]["m"] == "1/2" and all(f["Q"]["m"] == "1/2" for f in filas)
        and res["Q"]["diagnostico_general"]["dominio"] == qd["domain"],
        "m_estrella_exactas_conservadas": res["Q"]["diagnostico_general"]["m_estrella_contrato"]["exacto"] == mg["contrato"]["max_inf_threshold"]
        and res["Q"]["diagnostico_general"]["m_estrella_conservadora"]["exacto"] == mg["conservadora"]["max_inf_threshold"]
        and all(Fraction(mg[v]["max_inf_threshold"]) for v in ("contrato", "conservadora")),
        "resumen_ligado_a_las_filas": res["filas_sha256"] == sha_archivo(nueva / "sintesis" / "EXP8_POR_AFIRMACION.jsonl")
        and all(v for k, v in res["cotejos_esperados_del_encargo"].items() if k != "nota"),
        "manifiesto_ligado_a_las_salidas": all(sha_archivo(nueva / k) == v for k, v in man["salidas"].items())
        and all(sha_archivo(BASE / x["ruta"].replace("\\", "/")) == x["sha256"] for x in man["fuentes"].values() if "bytes" in x)}
    return {"validador": ("U45 no se ejecuta (verifica la ronda histórica rem160 completa: inventarios, libros, textos y negativos); validación "
                          "local desde las filas y las entradas"),
            "comprobaciones": chk, "discrepancias_de_enlace": dict(malos),
            "recuentos": {"ENF": enf_f, "COV": cov_f, "Q": q_ok, "posiciones_Q": dict(pos_q), "P7": len(p7f), "COV_ambos_negativos": len(ambos_neg)},
            "aceptada": all(chk.values())}


def _validar_integracion(nueva: Path, ej: dict) -> dict:
    ent = ej["entradas"]
    sp = BASE / ent["sintesis"]["carpeta"] / "sintesis" / "EXP8_POR_AFIRMACION.jsonl"
    need(sha_archivo(sp) == ent["sintesis"]["productos_sha256"][rel(sp)], "SINTESIS_CAMBIADA")
    SL, NL = lineas_de(sp), lineas_de(nueva / "sintesis" / "EXP8_POR_AFIRMACION.jsonl")
    S, N = [json.loads(x) for x in SL], [json.loads(x) for x in NL]
    l1, l2 = leer(BASE / ent["b1"]["archivos"]["lectura"]), leer(BASE / ent["b2"]["archivos"]["lectura"])
    ag = leer(BASE / ent["b2"]["archivos"]["evidencia"])["b1"]["afirmacion_grupo"]
    U = Fraction(float.fromhex(l1["datos_validados"]["U_C2_hex"]))
    G = {g: U - Fraction(float.fromhex(x["L_K1_hex"])) for g, x in l2["datos_validados"]["grupos"].items()}
    lect = {g["grupo"]: g["afirmaciones"] for g in l2["lectura"]["grupos"]}
    cambiadas = [i for i, (a, b) in enumerate(zip(SL, NL)) if a != b]
    doce = {S[i]["afirmacion"] for i in cambiadas}
    desconocidas = {f["afirmacion"] for f in S if f["conjunto_padre"] == "inconclusa" and f["COV"]["conclusion"] == "no_decidida_por_testigos"}
    DECL = ("COV", "se_sabe", "no_se_concluye")
    malas = Counter()
    for i in cambiadas:
        f, n = S[i], N[i]
        a = f["afirmacion"]
        rg = n["COV"].get("resolucion_global") or {}
        g = ag.get(a)
        if any(canon(n[k]) != canon(f[k]) for k in set(f) | set(n) if k not in DECL):
            malas["ruta_no_declarada"] += 1
        if any(canon(n["COV"].get(k)) != canon(f["COV"].get(k)) for k in set(f["COV"]) | set(n["COV"]) if k not in ("conclusion", "resolucion_global")):
            malas["ruta_COV_no_declarada"] += 1
        if not (n["COV"]["conclusion"] == "robust_infeasible" and n["COV"]["conclusion_historica"] == "no_decidida_por_testigos"
                and n["categoria_original"] == f["categoria_original"] and n["conjunto_padre"] == "inconclusa"):
            malas["veredicto_o_historico"] += 1
        if not (g and rg.get("grupo") == g and Fraction(rg["G_hi"]["exacto"]) == G[g] and G[g] <= -EPS
                and Fraction(rg["margen_bajo_menos_eps"]["exacto"]) == -EPS - G[g] and rg.get("eps") == "1/100"
                and rg.get("afirmaciones_del_grupo") == lect.get(g) and rg.get("escenario") == n["COV"]["escenario"]):
            malas["aritmetica_o_grupo"] += 1
    cnt = lambda it: dict(sorted(Counter(it).items()))  # noqa: E731
    cov_f = cnt(f["COV"]["conclusion"] for f in N)
    sc = [(f, l) for f in N for l in (f["COV"]["cambio_de_signo_certificado"] or [])]
    c12 = leer_jsonl(nueva / "sintesis" / "COV12_RESOLUCION_GLOBAL.jsonl")
    filas_sha = sha_archivo(nueva / "sintesis" / "EXP8_POR_AFIRMACION.jsonl")
    pos = {f["afirmacion"]: i for i, f in enumerate(N)}
    res = leer(nueva / "sintesis" / "RESUMEN_EXP8.json")
    man = leer(nueva / "fuentes" / "MANIFIESTO_SINTESIS.json")
    chk = {
        "filas_1728_mismo_orden": len(N) == len(S) == 1728 and [f["afirmacion"] for f in N] == [f["afirmacion"] for f in S],
        "cambian_exactamente_las_doce": len(cambiadas) == 12 and doce == desconocidas == set(ag),
        "doce_colombianas": all(S[i]["dimensiones"]["pais"] == "COL" for i in cambiadas),
        "otras_1716_identicas_byte_a_byte": sum(1 for a, b in zip(SL, NL) if a == b) == 1716,
        "doce_solo_rutas_declaradas_y_aritmetica_exacta": not malas,
        "regla_inclusiva_seis_grupos": len(G) == 6 and all(v <= -EPS for v in G.values()),
        "COV_final_1700_12_16": cov_f == {"inconclusa_preservada": 1700, "no_decidida_por_testigos": 16, "robust_infeasible": 12}
        and all(f["dimensiones"]["pais"] == "MEX" and f["conjunto_padre"] == "robusta" for f in N if f["COV"]["conclusion"] == "no_decidida_por_testigos"),
        "veinte_cambios_de_signo_aparte": len(sc) == 20 and cnt(f["COV"]["conclusion"] for f, _ in sc) == {"inconclusa_preservada": 8, "robust_infeasible": 12},
        "ENF_Q_P7_sin_cambios": all(canon(n[k]) == canon(f[k]) for f, n in zip(S, N) for k in ("ENF", "Q", "P7", "categoria_original", "padre")),
        "COV12_doce_lineas_ligadas": len(c12) == 12 and {x["afirmacion"] for x in c12} == doce
        and all(x["linea_sintesis_rem170"] == pos[x["afirmacion"]] + 1 and x["fila_rem170_canon_sha256"] == sha(canon(N[pos[x["afirmacion"]]]))
                and x["fila_rem160_linea_sha256"] == sha(SL[pos[x["afirmacion"]]]) and x["sintesis_rem170_filas_sha256"] == filas_sha
                and canon(x["resolucion_global"]) == canon(N[pos[x["afirmacion"]]]["COV"]["resolucion_global"]) for x in c12),
        "resumen_ligado_a_las_filas": res["filas_sha256"] == filas_sha and all(v for k, v in res["cotejos_esperados_del_encargo"].items() if k != "nota"),
        "manifiesto_ligado_a_las_salidas": all(sha_archivo(nueva / k) == v for k, v in man["salidas"].items())}
    return {"validador": ("U48 no se ejecuta (verifica la ronda histórica rem170 completa: inventarios, veinte libros, matrices y textos); "
                          "validación local: aritmética exacta desde la lectura B1/B2 validada y conservación byte a byte"),
            "comprobaciones": chk, "discrepancias": dict(malas),
            "recuentos": {"COV": cov_f, "cambios_de_signo": len(sc), "lineas_cambiadas": len(cambiadas), "lineas_identicas": 1728 - len(cambiadas),
                          "G_hi_por_grupo": {g: fx(v) for g, v in sorted(G.items())}},
            "aceptada": all(chk.values())}


def validar(nueva: Path) -> dict:
    """fam10-validar: SIN la referencia. ENF: parte científica de la auditoría rem148 (U42 no localizado; L-ENF-AFIRMACION-AUDITORIA-REM148) y estructura; SINTESIS e INTEGRACION:
    validación local desde filas y entradas."""
    t0 = time.time()
    rastro = F1().Rastro()
    nueva = _dentro(nueva)
    ej = leer(nueva / "ejecucion.json") if (nueva / "ejecucion.json").is_file() else {}
    tarea = ej.get("tarea")
    need(ej.get("etiqueta") == ETIQUETA and tarea in ETAPAS, "CARPETA_SIN_ETAPA_FAM10")
    malos = fuentes_alteradas("calculo")
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam10.json; no se valida): %s" % malos[:5])
    for k, v in ej["productos_sha256"].items():
        need(sha_archivo(BASE / k) == v, "PRODUCTO_CAMBIADO_DESDE_LA_ETAPA: %s" % k)
    r = {"comando": "fam10-validar", "tarea": tarea, "operacion": OPERACION_DE[tarea], "origen": rel(nueva),
         "inventory_sha256": sha_archivo(nueva / "ejecucion.json"), "etapa_exito": ej.get("exito") is True}
    exc = None
    try:
        r.update({"ENF": _validar_enf, "SINTESIS": _validar_sintesis, "INTEGRACION": _validar_integracion}[tarea](nueva, ej))
    except Exception:  # noqa: BLE001
        exc = _sin_base(traceback.format_exc())[-1500:]
    informe = rastro.informe()
    r["excepcion"] = exc
    r["lecturas"] = lecturas(rastro, informe)
    r["aceptada"] = (exc is None and bool(r.get("aceptada")) and r["etapa_exito"] and not r["lecturas"]["fuera_del_paquete_y_del_interprete"]
                     and not r["lecturas"]["referencia_esperada_leida"])
    r["segundos"] = round(time.time() - t0, 3)
    return r


# ================================================================================================ comparación (después de producir)
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


def _js(x) -> str:
    return json.dumps(x, ensure_ascii=False, sort_keys=True)


_HUELLAS: dict = {}


def _sha_c(p: Path):
    """Huella de un archivo, memorizada dentro de una comparación (los archivos no cambian mientras se compara)."""
    k = str(p)
    if k not in _HUELLAS:
        _HUELLAS[k] = sha_archivo(p)
    return _HUELLAS[k]


def _ruta_de(v: str, bases: tuple):
    q = v.replace("\\", "/")
    for b in bases:
        p = (Path(b) / q) if not Path(q).is_absolute() else Path(q)
        if p.exists():
            return p
    return None


def _clasificar(p: tuple, a, b, hn: dict, ctx: dict) -> dict:
    """Tipo de una diferencia: procedencia (ruta, hora, tiempo, huella, huella de código, tamaño) con su vínculo comprobado, o científica."""
    d = {"campo": "/".join(str(x) for x in p), "nuevo": a if a is not _FALTA else "<ausente>", "referencia": b if b is not _FALTA else "<ausente>"}
    if a is _FALTA or b is _FALTA:
        return dict(d, tipo="cientifica")
    last = p[-1] if p else None
    if isinstance(a, str) and isinstance(b, str):
        if last in ("ruta", "area"):
            f = _ruta_de(a, ctx["bases"])
            hs = hn.get(p[:-1] + ("sha256",))
            ok = f is not None and (hs is None or (f.is_file() and _sha_c(f) == hs))
            return dict(d, tipo="procedencia:ruta", vinculo=rel(f) if f is not None else None, vinculo_ok=ok)
        if last == CAMPO_CERTIFICADO and HEX64.fullmatch(a) and HEX64.fullmatch(b):
            return dict(d, tipo="procedencia:certificado_reemitido", **_vinculo_certificado(p, a, b, hn, ctx))
        if HEX64.fullmatch(a) and HEX64.fullmatch(b):
            if original().get(a) == b:
                return dict(d, tipo="procedencia:huella_de_codigo", vinculo="proyección saneada %s… del original %s… (fuentes_fam10.json)" % (a[:8], b[:8]),
                            vinculo_ok=True)
            v = ctx["hashes"].get(a)
            return dict(d, tipo="procedencia:huella", vinculo=v, vinculo_ok=v is not None)
        if last in ("utc", "inicio_utc", "fin_utc"):
            try:
                dt.datetime.fromisoformat(a)
                ok = True
            except ValueError:
                ok = False
            return dict(d, tipo="procedencia:hora", vinculo="hora de esta ejecución", vinculo_ok=ok)
    if last == "segundos" and len(p) >= 2 and p[-2] == "garantia_clave":
        clave = hn.get(p[:-2] + ("clave_transformada_sha256",))
        v = ctx.get("segundos", {}).get(clave, _FALTA)
        return dict(d, tipo="procedencia:tiempo", vinculo="fila_historica.segundos de %s en el integral NUEVO" % clave, vinculo_ok=v == a)
    if last == "bytes" and (p[:-1] + ("ruta",)) in hn:
        f = _ruta_de(hn[p[:-1] + ("ruta",)], ctx["bases"])
        return dict(d, tipo="procedencia:tamano", vinculo=rel(f) if f else None, vinculo_ok=bool(f) and f.is_file() and f.stat().st_size == a)
    return dict(d, tipo="cientifica")


def _dif(nuevo, ref, ctx: dict) -> list:
    hn, hr = dict(_hojas(nuevo)), dict(_hojas(ref))
    out = []
    for p in sorted(set(hn) | set(hr), key=lambda t: [str(x) for x in t]):
        a, b = hn.get(p, _FALTA), hr.get(p, _FALTA)
        if a is not _FALTA and b is not _FALTA and _js(a) == _js(b):
            continue
        out.append(_clasificar(p, a, b, hn, ctx))
    return out


def _generico(campo: str) -> str:
    return re.sub(r"/\d+(?=/|$)", "/[]", campo)


def _resumir(difs: list, clave: str | None = None) -> dict:
    """Diferencias agrupadas por campo genérico y tipo; las científicas, listadas (hasta 40)."""
    proc, cient = {}, []
    for x in difs:
        if x["tipo"] == "cientifica":
            cient.append(dict(x, clave=clave) if clave else x)
            continue
        k = "%s | %s" % (_generico(x["campo"]), x["tipo"])
        g = proc.setdefault(k, {"tipo": x["tipo"], "campo": _generico(x["campo"]), "n": 0, "vinculos_ok": 0, "ejemplo": None})
        g["n"] += 1
        g["vinculos_ok"] += bool(x.get("vinculo_ok"))
        if g["ejemplo"] is None:
            g["ejemplo"] = dict(x, clave=clave) if clave else x
    return {"procedencia": proc, "cientificas": cient}


def _fusionar(a: dict, b: dict) -> dict:
    for k, g in b["procedencia"].items():
        if k in a["procedencia"]:
            a["procedencia"][k]["n"] += g["n"]
            a["procedencia"][k]["vinculos_ok"] += g["vinculos_ok"]
        else:
            a["procedencia"][k] = g
    a["cientificas"] += b["cientificas"]
    return a


def _comparar_filas(nuevas: list, refs: list, ctx: dict, clave: str = "afirmacion") -> dict:
    kn, kr = [f[clave] for f in nuevas], [f[clave] for f in refs]
    N, Rf = {f[clave]: f for f in nuevas}, {f[clave]: f for f in refs}
    tot = {"procedencia": {}, "cientificas": []}
    escen = Counter()
    for k in kn:
        if k not in Rf:
            continue
        r = _resumir(_dif(N[k], Rf[k], ctx), k)
        for x in r["cientificas"]:
            escen[x["campo"].split("/", 1)[0]] += 1
        _fusionar(tot, r)
    sin = sum(1 for k in kn if k in Rf and _js(N[k]) == _js(Rf[k]))
    return {"filas_nuevas": len(nuevas), "filas_referencia": len(refs), "faltan": sorted(set(kr) - set(kn))[:20], "ajenas": sorted(set(kn) - set(kr))[:20],
            "duplicadas": len(kn) - len(set(kn)), "mismo_orden": kn == kr, "filas_identicas": sin,
            "procedencia": sorted(tot["procedencia"].values(), key=lambda g: g["campo"]), "cientificas_n": len(tot["cientificas"]),
            "cientificas": tot["cientificas"][:40], "cientificas_por_bloque": dict(escen),
            "procedencia_vinculada": all(g["n"] == g["vinculos_ok"] for g in tot["procedencia"].values())}


def _comparar_doc(nuevo, ref, ctx: dict) -> dict:
    r = _resumir(_dif(nuevo, ref, ctx))
    return {"identico": _js(nuevo) == _js(ref), "procedencia": sorted(r["procedencia"].values(), key=lambda g: g["campo"]),
            "cientificas_n": len(r["cientificas"]), "cientificas": r["cientificas"][:40],
            "procedencia_vinculada": all(g["n"] == g["vinculos_ok"] for g in r["procedencia"].values())}


def _contexto(nueva: Path, ej: dict) -> dict:
    """Huellas conocidas (archivos de la ejecución y de sus entradas, piezas del paquete) para comprobar el vínculo de cada huella cambiada."""
    hs = {}
    carpetas = {nueva}
    for v in ej["entradas"].values():
        if isinstance(v, dict) and v.get("carpeta"):
            carpetas.add(BASE / v["carpeta"])
        for k in ("registro", "archivo"):
            if isinstance(v, dict) and isinstance(v.get(k), str):
                hs[sha_archivo(BASE / v[k])] = v[k]
    for d in sorted(carpetas, key=str):
        for p in sorted(Path(d).rglob("*")):
            if p.is_file():
                hs.setdefault(sha_archivo(p), rel(p))
    for v in ej["entradas"].values():           # registros de las etapas FAM10 previas y sus entradas
        if isinstance(v, dict) and v.get("carpeta") and (BASE / v["carpeta"] / "ejecucion.json").is_file():
            e2 = leer(BASE / v["carpeta"] / "ejecucion.json")
            for w in (e2.get("entradas") or {}).values():
                if isinstance(w, dict):
                    for k in ("carpeta",):
                        if w.get(k) and (BASE / w[k]).is_dir():
                            for p in sorted((BASE / w[k]).rglob("*")):
                                if p.is_file():
                                    hs.setdefault(sha_archivo(p), rel(p))
                    for k in ("registro", "archivo"):
                        if isinstance(w.get(k), str):
                            hs.setdefault(sha_archivo(BASE / w[k]), w[k])
    for x in piezas():
        hs.setdefault(x["sha256"], x["archivo"])
    return {"hashes": hs, "bases": (BASE, nueva), "ejecucion": ej}


# ================================================================================================ VINCULO-CERTIFICADO-v1
# La huella de ENF/lados/sup/certificado_resolucion_sha256 (sup/... en la etapa ENF) no se busca entre las huellas conocidas: se liga al
# certificado que el integral ENF NUEVO declara como reemitido por fam08-recuperar, con todas sus comprobaciones. La referencia es la huella
# del certificado aceptado (el original de la proyección guardada en datos/fam08; SANEADO-v1 de FAM08).
CERT_FAM08 = ("datos/fam08/CERTIFICADO_d59edf8a_I2.json", "9e2ac47289e8c239c8352a70819babb285e28c03f3c3cfd906230950a9039f72",
              "cc1aa49abf64585dd500838d1120d02c938a571f4be6fe159e3ab42fc697daaa")   # (proyección, su huella, huella del original aceptado)
CAMPO_CERTIFICADO = "certificado_resolucion_sha256"
T1_ENF = "ABL-ENF-T1"


def _integral_de(ej: dict) -> dict:
    """Entrada enf_integral de una etapa, siguiendo su cadena de etapas FAM10 validadas (INTEGRACION -> SINTESIS -> ENF -> integral)."""
    e = ej.get("entradas") or {}
    if isinstance(e.get("enf_integral"), dict):
        return e["enf_integral"]
    for k, t in (("enf", "ENF"), ("sintesis", "SINTESIS")):
        if isinstance(e.get(k), dict):
            x = entrada_fam10(BASE / e[k]["carpeta"], BASE / e[k]["registro"], t)
            need(x["ejecucion_sha256"] == e[k].get("ejecucion_sha256") and x["registro_sha256"] == e[k].get("registro_sha256"),
                 "CADENA_FAM10_CAMBIADA_DESPUES_DE_CONSUMIRSE: %s" % k)
            return _integral_de(leer(BASE / e[k]["carpeta"] / "ejecucion.json"))
    raise Fam10Error("ETAPA_SIN_INTEGRAL_ENF")


def _bytes_derivados(doc: dict, proy: dict, fin: str) -> bytes:
    """Como fam08-comparar RECUPERACION: el certificado con la ruta y la huella de su fuente repuestas por las de la proyección aceptada,
    serializado como lo escribe el certificador (indent=1, fin de línea de los bytes nuevos)."""
    d2 = json.loads(json.dumps(doc))
    d2["fuente_techo"]["ruta"] = proy["fuente_techo"]["ruta"]
    d2["fuente_techo"]["sha256"] = proy["fuente_techo"]["sha256"]
    return (json.dumps(d2, ensure_ascii=False, indent=1) + "\n").replace("\n", fin).encode("utf-8")


def certificado_reemitido(ej: dict) -> dict:
    """VINCULO-CERTIFICADO-v1: el certificado reemitido que consume el integral ENF de la etapa, con sus comprobaciones. ok solo si:
    (1) el integral es una integración FAM08 aceptada (fam08-integrar + fam08-comparar INTEGRAL) y su ejecución y su comparación declaran el
        mismo certificado, de procedencia «nuevo»;
    (2) los bytes del archivo tienen la huella declarada;
    (3) clave: la del certificado aceptado (clave y clave_completa_sha256), en el archivo de esa clave;
    (4) fuente: fuente_techo es el enf_techos.jsonl de la T1 que consume el integral, con la huella de sus bytes;
    (5) lo emitió fam08-recuperar sobre esa T1 (RECUPERACION_T1.json: archivo y huella) y su comparación fam08-comparar RECUPERACION, junto a
        la recuperación en la misma corrida, quedó aceptada, con huella derivada igual a la proyección y original = la referencia;
    (6) con la ruta y la huella de su fuente repuestas, los bytes son exactamente la proyección aceptada, cuyo original registra
        fuentes_fam08.json (saneado)."""
    fallos, out = [], {"regla": "VINCULO-CERTIFICADO-v1 (src/fam10.py)", "original_sha256": CERT_FAM08[2]}

    def chk(c, m):
        if not c:
            fallos.append(m)
        return bool(c)
    try:
        ent = _integral_de(ej)
        d, reg = _dentro(BASE / ent["carpeta"]), _dentro(BASE / ent["registro"])
        out["integral"] = rel(d)
        try:
            entrada_fam08(d, reg)
        except Fam10Error as ex:
            fallos.append("INTEGRAL_NO_ACEPTADO: %s" % ex)
        ei, ri = leer(d / "ejecucion.json"), leer(reg)
        c = (ei.get("entradas") or {}).get("certificado") or {}
        out.update(archivo=c.get("archivo"), sha256=c.get("sha256"))
        if not chk(c.get("procedencia") == "nuevo" and isinstance(c.get("archivo"), str) and HEX64.fullmatch(str(c.get("sha256"))),
                   "INTEGRAL_SIN_CERTIFICADO_REEMITIDO"):
            return dict(out, fallos=fallos, ok=False)
        chk(((ri.get("entradas") or {}).get("certificado") or {}) == c, "CERTIFICADO_DISTINTO_EN_LA_COMPARACION_INTEGRAL")
        cp = _dentro(BASE / c["archivo"])
        raw = cp.read_bytes() if cp.is_file() else b""
        chk(raw and sha(raw) == c["sha256"], "BYTES_DEL_CERTIFICADO_DISTINTOS_DE_SU_HUELLA")
        pp = BASE / CERT_FAM08[0]
        chk(sha_archivo(pp) == CERT_FAM08[1], "PROYECCION_DEL_CERTIFICADO_ACEPTADO_ALTERADA")
        proy = leer(pp)
        try:
            doc = json.loads(raw.decode("utf-8"))
        except ValueError:
            doc = {}
        chk(isinstance(doc, dict) and doc.get("kind") == proy.get("kind"), "NO_ES_UN_CERTIFICADO_DE_SALTO")
        out["clave"] = doc.get("clave") if isinstance(doc, dict) else None
        chk(isinstance(doc, dict) and doc.get("clave") == proy.get("clave") and doc.get("clave_completa_sha256") == proy.get("clave_completa_sha256")
            and str(doc.get("clave_completa_sha256")).startswith(str(doc.get("clave"))) and cp.name == Path(CERT_FAM08[0]).name,
            "CERTIFICADO_DE_OTRA_CLAVE")
        t1 = (((ei.get("entradas") or {}).get("tareas") or {}).get(T1_ENF) or {}).get("carpeta")
        ft = (doc.get("fuente_techo") or {}) if isinstance(doc, dict) else {}
        out["fuente"] = ft.get("ruta")
        chk(isinstance(t1, str) and ft.get("ruta") == t1 + "/salida/enf_techos.jsonl", "FUENTE_DEL_CERTIFICADO_NO_ES_LA_T1_DEL_INTEGRAL")
        fp = BASE / str(ft.get("ruta"))
        chk(isinstance(ft.get("ruta"), str) and fp.is_file() and sha_archivo(fp) == ft.get("sha256"), "HUELLA_DE_LA_FUENTE_DISTINTA_DE_SUS_BYTES")
        rec = cp.parent.parent
        rr = leer(rec / "RECUPERACION_T1.json") if (cp.parent.name == "certificado" and (rec / "RECUPERACION_T1.json").is_file()) else {}
        cr = rr.get("certificado_reemitido") or {}
        chk(rr.get("comando") == "fam08-recuperar" and rr.get("exito") is True and cr.get("rc") == 0 and cr.get("archivo") == c["archivo"]
            and cr.get("sha256") == c["sha256"] and (rr.get("t1_entrada") or {}).get("carpeta") == t1, "CERTIFICADO_NO_EMITIDO_POR_LA_RECUPERACION_DE_ESA_T1")
        comps = []
        for q in sorted(rec.parent.glob("*.comparacion.json")):
            try:
                x = leer(q)
            except (OSError, ValueError):
                continue
            if isinstance(x, dict) and x.get("comando") == "fam08-comparar" and x.get("tarea") == "RECUPERACION" and x.get("nueva") == rel(rec):
                comps.append((q, x))
        if chk(len(comps) == 1, "COMPARACION_DE_RECUPERACION_AUSENTE_O_DUPLICADA: %d" % len(comps)):
            q, x = comps[0]
            out["comparacion_recuperacion"] = rel(q)
            hd = (x.get("certificado") or {}).get("huella_derivada") or {}
            chk((x.get("estado") or {}).get("reproduccion") == "aceptada" and not (x.get("estado") or {}).get("motivos"), "COMPARACION_DE_RECUPERACION_NO_ACEPTADA")
            chk(hd.get("igual_a_la_proyeccion") is True and hd.get("proyeccion_sha256") == CERT_FAM08[1] and hd.get("original_sha256") == CERT_FAM08[2]
                and (x.get("t1_entrada") or {}).get("carpeta") == t1, "COMPARACION_DE_RECUPERACION_DE_OTRO_CERTIFICADO")
        fin = "\r\n" if b"\r\n" in raw else "\n"
        chk(isinstance(doc, dict) and isinstance(doc.get("fuente_techo"), dict) and sha(_bytes_derivados(doc, proy, fin)) == CERT_FAM08[1],
            "CERTIFICADO_DISTINTO_DEL_ACEPTADO_CON_SU_FUENTE_REPUESTA")
        sane = [s for s in (leer(BASE / "fuentes_fam08.json").get("saneado") or []) if s.get("archivo") == CERT_FAM08[0]]
        chk(len(sane) == 1 and sane[0].get("sha256") == CERT_FAM08[1] and sane[0].get("sha256_original") == CERT_FAM08[2]
            and sane[0].get("restituye_el_original") is True, "ORIGINAL_DEL_CERTIFICADO_NO_REGISTRADO_EN_FAM08")
    except (Fam10Error, OSError, ValueError, KeyError, TypeError, AttributeError) as ex:
        fallos.append("CADENA_DEL_CERTIFICADO: %s: %s" % (type(ex).__name__, _sin_base(str(ex))))
    return dict(out, fallos=fallos, ok=not fallos)


def _vinculo_certificado(p: tuple, a: str, b: str, hn: dict, ctx: dict) -> dict:
    """Vínculo de una fila: el certificado de la etapa (calculado una vez por comparación), su huella = la de la fila, la clave de la fila =
    la del certificado y la referencia = el original aceptado."""
    if "certificado" not in ctx:
        ctx["certificado"] = certificado_reemitido(ctx["ejecucion"])
    cr = ctx["certificado"]
    clave = hn.get(p[:-1] + ("clave_transformada_sha256",))
    f = list(cr["fallos"])
    if a != cr.get("sha256"):
        f.append("HUELLA_DE_LA_FILA_NO_ES_LA_DEL_CERTIFICADO_REEMITIDO")
    if clave != cr.get("clave"):
        f.append("CLAVE_DE_LA_FILA_DISTINTA_DE_LA_DEL_CERTIFICADO: %s" % clave)
    if b != CERT_FAM08[2]:
        f.append("REFERENCIA_NO_ES_EL_CERTIFICADO_ACEPTADO")
    v = ("certificado reemitido %s (clave %s; fuente %s; recuperación aceptada en %s); con su fuente repuesta = proyección %s… del original %s…"
         % (cr.get("archivo"), cr.get("clave"), cr.get("fuente"), cr.get("comparacion_recuperacion"), CERT_FAM08[1][:8], CERT_FAM08[2][:8]))
    return {"vinculo": v if not f else None, "vinculo_ok": not f, **({"fallos": f[:6]} if f else {})}


def _segundos_integral(carpeta: str) -> dict:
    return {x["clave_transformada_sha256"]: (x.get("fila_historica") or {}).get("segundos")
            for x in leer_jsonl(BASE / carpeta / "ensamblado" / "enf_techos_integrados.jsonl")}


def _comparar_enf(nueva: Path, ej: dict, val: dict, ctx: dict) -> dict:
    ctx["segundos"] = _segundos_integral(ej["entradas"]["enf_integral"]["carpeta"])
    ref_p = BASE / "datos/fam11/cov/ENF_POR_AFIRMACION.jsonl"
    filas = _comparar_filas(leer_jsonl(nueva / "ENF_POR_AFIRMACION.jsonl"), leer_jsonl(ref_p), ctx)
    filas["bytes_identicos"] = sha_archivo(nueva / "ENF_POR_AFIRMACION.jsonl") == sha_archivo(ref_p)
    filas["referencia"] = {"archivo": rel(ref_p), "sha256": sha_archivo(ref_p), "nota": "producto rem147 aceptado en rem148 (copia de FAM11)"}
    docs = {n: _comparar_doc(leer(nueva / n), leer(REF / "rem147" / n), ctx) for n in ("COBERTURA_EXP8.json", "RESUMEN_POR_PAIS.json")}
    md_n, md_r = (nueva / "COBERTURA_EXP8.md").read_text(encoding="utf-8"), (REF / "rem147" / "COBERTURA_EXP8.md").read_text(encoding="utf-8")
    docs["COBERTURA_EXP8.md"] = {"identico": md_n == md_r, "cientificas_n": sum(1 for a, b in zip(md_n.splitlines(), md_r.splitlines()) if a != b)
                                 + abs(len(md_n.splitlines()) - len(md_r.splitlines())), "procedencia": [], "procedencia_vinculada": True}
    lb = leer(REF / "rem148" / "LIBRO_ENF.resumen.json")
    # la validación no aceptada puede no traer la auditoría: se repite aquí (filas parciales si se detiene)
    aud = val.get("auditoria_rem148") or _auditoria_enf(nueva, ej["entradas"]["enf_integral"]["carpeta"])
    rows_n = {r["afirmacion"]: r for r in aud["filas"]}
    rows_r = {r["afirmacion"]: r for r in lb["rows"]}
    cnt = aud["recuentos"]
    mios = {"claims": len(rows_n), "inconclusive_parent": sum(1 for r in aud["filas"] if r["category"] != "robusta_infactible_certificada"),
            "inconclusive_preserved_ENF": cnt.get("inconclusa_preservada"), "partial_not_robust_infeasible": cnt.get("parcial_no_robusta_infactible"),
            "partial_not_robust_feasible": cnt.get("parcial_no_robusta_factible"),
            "parent_robust_infeasible_ENF_undecided": sum(v for k, v in cnt.items() if k.startswith("no_decidida")),
            "witness_slots_linked": aud["ranuras_enlazadas"], "unique_cells": aud["celdas_unicas"],
            "minimum_certified_margin_from_economic_threshold": aud["margen_minimo"], "by_country": aud["por_pais"]}
    libro = {"recuentos": {k: {"nuevo": v, "libro": lb.get(k), "igual": _js(v) == _js(lb.get(k))} for k, v in mios.items()},
             "filas_con_cotas": {"nuevas": len(rows_n), "libro": len(rows_r), "iguales": sum(1 for k, v in rows_n.items() if _js(v) == _js(rows_r.get(k))),
                                 "distintas": sorted(k for k, v in rows_n.items() if _js(v) != _js(rows_r.get(k)))[:20]},
             "producto_del_libro": {"libro": lb.get("product_sha256"), "nuevo": sha_archivo(nueva / "ENF_POR_AFIRMACION.jsonl")}}
    libro["igual"] = all(x["igual"] for x in libro["recuentos"].values()) and libro["filas_con_cotas"]["iguales"] == len(rows_r) == len(rows_n)
    ok = (filas["cientificas_n"] == 0 and not filas["faltan"] and not filas["ajenas"] and filas["procedencia_vinculada"]
          and all(d["cientificas_n"] == 0 and d["procedencia_vinculada"] for d in docs.values()) and libro["igual"])
    return {"filas": filas, "documentos": docs, "frente_al_libro_rem148": libro, "cumple": ok}


def _recuentos_sintesis(filas: list) -> dict:
    inc = [f for f in filas if f["conjunto_padre"] == "inconclusa"]
    rob = [f for f in filas if f["conjunto_padre"] == "robusta"]
    q = {v: Counter(f["Q"]["versiones"][v]["canal"] for f in filas) for v in ("contrato", "conservadora")}
    return {"original_inconclusive": len(inc), "original_robust_infeasible_MEX": sum(1 for f in rob if f["dimensiones"]["pais"] == "MEX"),
            "ENF_inconclusive_preserved": sum(1 for f in inc if f["ENF"]["conclusion"] == "inconclusa_preservada"),
            "COV_inconclusive_preserved": sum(1 for f in inc if f["COV"]["conclusion"] == "inconclusa_preservada"),
            "COV_inconclusive_unknown": sum(1 for f in inc if f["COV"]["conclusion"] == "no_decidida_por_testigos"),
            "ENF_COV_original_robust_unknown_each": len(rob) if all(f["ENF"]["conclusion"] == ENF_NODEC and f["COV"]["conclusion"] == "no_decidida_por_testigos" for f in rob) else None,
            "Q_half_preserved_each_version": q["contrato"]["inconclusa_preservada"] if q["contrato"] == q["conservadora"] else None,
            "Q_half_infeasible_robustness_refuted_by_sup_each_version": q["contrato"]["robustez_refutada_por_testigo_sup"] if q["contrato"] == q["conservadora"] else None,
            "Q_positions_each_version": 2 * len(filas), "P7_claims_applied_once": sum(1 for f in filas if f["P7"] and f["P7"]["aplicaciones"] == 1),
            "historical_decompositions": sum(1 for f in filas if f["ENF"]["descompuesta_rem108"] is True)}


def _recuentos_integracion(filas: list, sl: list, nl: list) -> dict:
    cnt = lambda it: dict(Counter(it))  # noqa: E731
    sc = [(f, l) for f in filas for l in (f["COV"]["cambio_de_signo_certificado"] or [])]
    return {"claims": len(filas), "parent_inconclusive": sum(1 for f in filas if f["conjunto_padre"] == "inconclusa"),
            "parent_robust_infeasible_MEX": sum(1 for f in filas if f["conjunto_padre"] == "robusta" and f["dimensiones"]["pais"] == "MEX"),
            "COV": cnt(f["COV"]["conclusion"] for f in filas), "ENF": cnt(f["ENF"]["conclusion"] for f in filas),
            "Q_contrato": cnt(f["Q"]["versiones"]["contrato"]["canal"] for f in filas), "Q_conservadora": cnt(f["Q"]["versiones"]["conservadora"]["canal"] for f in filas),
            "COV_sign_changes": len(sc), "COV_signs_in_preserved": sum(1 for f, _ in sc if f["COV"]["conclusion"] == "inconclusa_preservada"),
            "COV_signs_in_new_robust": sum(1 for f, _ in sc if f["COV"]["conclusion"] == "robust_infeasible"),
            "P7_claims": sum(1 for f in filas if f["P7"]), "P7_units": len({f["P7"]["unidad"] for f in filas if f["P7"]}),
            "historical_decompositions": sum(1 for f in filas if f["ENF"]["descompuesta_rem108"] is True),
            "unchanged_rows": sum(1 for a, b in zip(sl, nl) if a == b), "updated_rows": sum(1 for a, b in zip(sl, nl) if a != b)}


def _frente_al_libro(mios: dict, lb: dict) -> dict:
    out = {k: {"nuevo": v, "libro": lb.get(k), "igual": _js(v) == _js(lb.get(k))} for k, v in mios.items() if k in lb}
    return {"recuentos": out, "igual": bool(out) and all(x["igual"] for x in out.values()), "sin_equivalente_en_el_libro": sorted(set(mios) - set(lb))}


def _comparar_sintesis(nueva: Path, ej: dict, val: dict, ctx: dict) -> dict:
    ls = lineas_de(nueva / "sintesis" / "EXP8_POR_AFIRMACION.jsonl")
    for i, x in enumerate(ls):
        ctx["hashes"].setdefault(sha(x), "línea %d de %s" % (i + 1, rel(nueva / "sintesis" / "EXP8_POR_AFIRMACION.jsonl")))
    filas_n = [json.loads(x) for x in ls]
    filas = _comparar_filas(filas_n, leer_jsonl(REF / "rem160" / "EXP8_POR_AFIRMACION.jsonl"), ctx)
    docs = {"RESUMEN_EXP8.json": _comparar_doc(leer(nueva / "sintesis" / "RESUMEN_EXP8.json"), leer(REF / "rem160" / "RESUMEN_EXP8.json"), ctx),
            "MANIFIESTO_SINTESIS.json": _comparar_doc(leer(nueva / "fuentes" / "MANIFIESTO_SINTESIS.json"), leer(REF / "rem160" / "MANIFIESTO_SINTESIS.json"), ctx)}
    lb = leer(REF / "rem161" / "LIBRO_SINTESIS.resumen.json")
    libro = _frente_al_libro(_recuentos_sintesis(filas_n), lb["counts"])
    libro["filas_cientificas"] = {"nuevo": len(filas_n), "libro": lb.get("scientific_rows")}
    ok = (filas["cientificas_n"] == 0 and not filas["faltan"] and not filas["ajenas"] and filas["procedencia_vinculada"]
          and all(d["cientificas_n"] == 0 and d["procedencia_vinculada"] for d in docs.values()) and libro["igual"] and len(filas_n) == lb.get("scientific_rows"))
    return {"filas": filas, "documentos": docs, "frente_al_libro_rem161": libro, "cumple": ok}


def _comparar_integracion(nueva: Path, ej: dict, val: dict, ctx: dict) -> dict:
    sp = BASE / ej["entradas"]["sintesis"]["carpeta"] / "sintesis" / "EXP8_POR_AFIRMACION.jsonl"
    sl, nl = lineas_de(sp), lineas_de(nueva / "sintesis" / "EXP8_POR_AFIRMACION.jsonl")
    for i, x in enumerate(sl):
        ctx["hashes"].setdefault(sha(x), "línea %d de %s" % (i + 1, rel(sp)))
    filas_n = [json.loads(x) for x in nl]
    for i, f in enumerate(filas_n):
        ctx["hashes"].setdefault(sha(canon(f)), "fila %d (canónica) de %s" % (i + 1, rel(nueva / "sintesis" / "EXP8_POR_AFIRMACION.jsonl")))
    filas = _comparar_filas(filas_n, leer_jsonl(REF / "rem171" / "EXP8_POR_AFIRMACION.jsonl"), ctx)
    c12_ref = BASE / "referencias/fam11/rem170/COV12_RESOLUCION_GLOBAL.jsonl"
    c12 = _comparar_filas(leer_jsonl(nueva / "sintesis" / "COV12_RESOLUCION_GLOBAL.jsonl"), leer_jsonl(c12_ref), ctx)
    c12["referencia"] = {"archivo": rel(c12_ref), "sha256": sha_archivo(c12_ref)}
    docs = {"RESUMEN_EXP8.json": _comparar_doc(leer(nueva / "sintesis" / "RESUMEN_EXP8.json"), leer(REF / "rem171" / "RESUMEN_EXP8.json"), ctx),
            "MANIFIESTO_SINTESIS.json": _comparar_doc(leer(nueva / "fuentes" / "MANIFIESTO_SINTESIS.json"), leer(REF / "rem171" / "MANIFIESTO_SINTESIS.json"), ctx)}
    lb = leer(REF / "rem171" / "LIBRO_INTEGRACION.resumen.json")
    libro = _frente_al_libro(_recuentos_integracion(filas_n, sl, nl), lb["counts"])
    ref160 = {f["afirmacion"]: f for f in leer_jsonl(REF / "rem160" / "EXP8_POR_AFIRMACION.jsonl")}
    ref171 = leer_jsonl(REF / "rem171" / "EXP8_POR_AFIRMACION.jsonl")
    cambiadas_ref = sorted(f["afirmacion"] for f in ref171 if _js(f) != _js(ref160.get(f["afirmacion"])))
    cambiadas_n = sorted(json.loads(b)["afirmacion"] for a, b in zip(sl, nl) if a != b)
    doce = {"nuevas": cambiadas_n, "aceptadas_rem170_rem171": cambiadas_ref, "iguales": cambiadas_n == cambiadas_ref and len(cambiadas_n) == 12}
    ok = (filas["cientificas_n"] == 0 and not filas["faltan"] and not filas["ajenas"] and filas["procedencia_vinculada"]
          and c12["cientificas_n"] == 0 and not c12["faltan"] and not c12["ajenas"] and c12["procedencia_vinculada"]
          and all(d["cientificas_n"] == 0 and d["procedencia_vinculada"] for d in docs.values()) and libro["igual"] and doce["iguales"])
    return {"filas": filas, "COV12": c12, "documentos": docs, "frente_al_libro_rem171": libro, "doce_claves": doce, "cumple": ok}


def comparar(tarea: str, nueva: Path, validacion: Path) -> dict:
    """fam10-comparar: DESPUÉS de producir y validar. Igualdad exacta del contenido científico por clave y escenario; cada diferencia de ruta,
    hora o huella se identifica y se comprueba su vínculo; una huella de código distinta se declara con su valor real."""
    t0 = time.time()
    _HUELLAS.clear()
    nueva, validacion = _dentro(nueva), _dentro(validacion)
    ej = leer(nueva / "ejecucion.json")
    need(ej.get("etiqueta") == ETIQUETA and ej.get("tarea") == tarea, "CARPETA_DE_OTRA_ETAPA")
    val = leer(validacion)
    need(val.get("comando") == "fam10-validar" and val.get("tarea") == tarea and val.get("origen") == rel(nueva)
         and val.get("inventory_sha256") == sha_archivo(nueva / "ejecucion.json"), "VALIDACION_AJENA")
    ctx = _contexto(nueva, ej)
    det = {"ENF": _comparar_enf, "SINTESIS": _comparar_sintesis, "INTEGRACION": _comparar_integracion}[tarea](nueva, ej, val, ctx)
    cod = ej["codigo"]
    motivos = []
    if not val.get("aceptada"):
        motivos.append("validación no aceptada")
    if not det["cumple"]:
        motivos.append("diferencias científicas, procedencia sin vínculo o recuentos distintos del libro")
    return {"comando": "fam10-comparar", "tarea": tarea, "operacion": OPERACION_DE[tarea], "nueva": rel(nueva), "validacion": rel(validacion),
            "validacion_aceptada": val.get("aceptada") is True, "regla": "COMPARACION-FAM10-v1 (src/fam10.py)", "codigo": cod, **det,
            **({"certificado_reemitido": ctx["certificado"]} if "certificado" in ctx else {}),
            "estado": {"reproduccion": "aceptada" if not motivos else "no_aceptada", "motivos": motivos}, "segundos": round(time.time() - t0, 3)}


# ================================================================================================ orden única, comprobación y receta
def tabla(entradas: dict, salida: Path) -> dict:
    """fam10-tabla: ENF -> validar -> SINTESIS -> validar -> INTEGRACION -> validar; después, las tres comparaciones. Una sola orden."""
    t0 = time.time()
    need(set(entradas or {}) == set(TABLA), "fam10-tabla requiere exactamente --entrada %s" % ", ".join(TABLA))
    salida = Path(salida)
    need(not salida.exists(), "LA_SALIDA_YA_EXISTE")
    malos = fuentes_alteradas("calculo")
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam10.json; no se calcula): %s" % malos[:5])
    # todas las entradas externas, con sus registros, ANTES de crear la carpeta (las de SINTESIS/INTEGRACION las vuelve a comprobar cada etapa)
    entrada_fam08(entradas["enf_integral"], entradas["registro_enf_integral"])
    entrada_cov(entradas["cov"], entradas["registro_cov"])
    entrada_p7(entradas["p7"])
    entrada_q(entradas["q_local"])
    b1 = entrada_b(entradas["b1"], entradas["validacion_b1"], "B1")
    b2 = entrada_b(entradas["b2"], entradas["validacion_b2"], "B2")
    eb = b2.get("enlace_b1") or {}
    need(eb.get("unidad_b1") == b1["carpeta"] and eb.get("registro_validacion") == b1["registro"], "B2_NO_CONSUME_ESTE_B1")
    salida.mkdir(parents=True)
    sal = _dentro(salida)
    pasos, ok = [], True
    ent = {"ENF": {k: entradas[k] for k in ENTRADAS_DE["ENF"]}}
    previas = {}
    for t in ETAPAS:
        d, v = sal / t.lower(), sal / (t.lower() + ".validacion.json")
        if t == "SINTESIS":
            e = {"enf": previas["ENF"][0], "validacion_enf": previas["ENF"][1], "cov": entradas["cov"], "registro_cov": entradas["registro_cov"],
                 "p7": entradas["p7"], "q_local": entradas["q_local"]}
        elif t == "INTEGRACION":
            e = {"sintesis": previas["SINTESIS"][0], "validacion_sintesis": previas["SINTESIS"][1], "b1": entradas["b1"], "validacion_b1": entradas["validacion_b1"],
                 "b2": entradas["b2"], "validacion_b2": entradas["validacion_b2"]}
        else:
            e = ent["ENF"]
        try:
            ej = correr(t, d, e)
        except Fam10Error as ex:
            pasos.append({"etapa": t, "exito": False, "error": str(ex)})
            ok = False
            break
        r = validar(d)
        _escribir_x(v, r)
        pasos.append({"etapa": t, "carpeta": rel(d), "exito": ej["exito"], "rc": ej["rc"], "excepcion": (ej["excepcion"] or "")[-600:] or None,
                      "validacion": rel(v), "aceptada": r["aceptada"], "referencia_esperada_leida": ej["lecturas"]["referencia_esperada_leida"]
                      or r["lecturas"]["referencia_esperada_leida"]})
        if not (ej["exito"] and r["aceptada"]):
            ok = False
            break
        previas[t] = (d, v)
    comps = {}
    if ok:
        for t in ETAPAS:
            c = comparar(t, sal / t.lower(), sal / (t.lower() + ".validacion.json"))
            _escribir_x(sal / (t.lower() + ".comparacion.json"), c)
            comps[t] = {"archivo": rel(sal / (t.lower() + ".comparacion.json")), "estado": c["estado"]}
    final = {}
    if ok:
        vi = leer(sal / "integracion.validacion.json")
        fin = sal / "integracion" / "sintesis"
        final = {"filas": rel(fin / "EXP8_POR_AFIRMACION.jsonl"), "filas_sha256": sha_archivo(fin / "EXP8_POR_AFIRMACION.jsonl"),
                 "resumen": rel(fin / "RESUMEN_EXP8.json"), "resolucion_doce": rel(fin / "COV12_RESOLUCION_GLOBAL.jsonl"),
                 "resolucion_doce_sha256": sha_archivo(fin / "COV12_RESOLUCION_GLOBAL.jsonl"), "recuentos": vi["recuentos"]}
    return {"comando": "fam10-tabla", "etiqueta": ETIQUETA, "entradas": {k: str(v) for k, v in entradas.items()}, "pasos": pasos, "comparaciones": comps,
            "tabla_final": final, "cumple": ok and all(c["estado"]["reproduccion"] == "aceptada" for c in comps.values()) and len(comps) == 3,
            "segundos": round(time.time() - t0, 3)}


def comprobar() -> dict:
    t0 = time.time()
    malos = fuentes_alteradas("todo")
    fu = fuentes()
    out = {"comando": "fam10-comprobar", "calculo": "ninguno", "fuentes": {"piezas": len(piezas()), "alteradas": malos},
           "sustituciones": sustituciones_ok(),
           "codigo": {n: {"archivo_sha256": sha_archivo(BASE / n), "original_sha256": h,
                          "corresponde": (BASE / n).is_file() and sha10((BASE / n).read_bytes()) == h} for n, h in codigo().items()},
           "autoridad": {k: (BASE / v["archivo"]).is_file() for k, v in fu["autoridad"].items()},
           "referencias": {x["archivo"]: sha_archivo(BASE / x["archivo"]) == x["sha256"] for x in piezas() if x["archivo"].startswith(("referencias/fam10/",) + PROHIBIDAS)},
           "solo_procedencia": sorted(fu["solo_procedencia"]), "filas_padre": fu["filas_padre"], "receta": {"pasos": len(receta()["pasos"])}}
    out["cumple"] = (not malos and all(v is True for v in out["sustituciones"].values()) and all(x["corresponde"] for x in out["codigo"].values())
                     and all(out["autoridad"].values()) and all(out["referencias"].values()))
    out["segundos"] = round(time.time() - t0, 3)
    return out


def receta() -> dict:
    py = "<python de .venv-fam01> -B -P -s -X utf8 reproducir.py"
    s = "salidas/fam10/<ejecucion>/"
    ent = ("--entrada enf_integral=<carpeta de fam08-integrar> --entrada registro_enf_integral=<su registro de fam08-comparar INTEGRAL aceptado> "
           "--entrada cov=<carpeta de fam11-ensamblar> --entrada registro_cov=<su registro de fam11-comparar ENSAMBLADO aceptado> "
           "--entrada p7=<archivo de p7-suplemento concordante> --entrada q_local=<carpeta de q-local concordante> "
           "--entrada b1=<carpeta de fam11-unidad B1> --entrada validacion_b1=<su registro de fam11-validar aceptado> "
           "--entrada b2=<carpeta de fam11-unidad B2 sobre ese B1> --entrada validacion_b2=<su registro de fam11-validar aceptado>")
    pasos = [
        {"paso": "comprobar", "orden": py + " fam10-comprobar --salida " + s + "comprobar.json", "calculo": "ninguno"},
        {"paso": "entradas (familias previas)", "ordenes": [
            "FAM08 (fam08-receta, paso integral): fam08-integrar ... --salida salidas/fam08/<ejecucion>/integral y fam08-comparar --tarea INTEGRAL",
            "FAM11 (fam11-receta, ensamblado_y_conciliacion): fam11-ensamblar ... --salida salidas/fam11/<ejecucion>/ensamblado y fam11-comparar --tarea ENSAMBLADO",
            "FAM11 (fam11-receta, B1 y B2): fam11-unidad --tarea B1 / B2 --b1 ... y fam11-validar de cada una",
            "FAM12: p7-suplemento --salida salidas/p7_suplemento_<n>.json y q-local --salida salidas/q_local_<n>"],
         "calculo": "el de cada familia (no lo repite FAM10)"},
        {"paso": "tabla (orden única)", "orden": py + " fam10-tabla " + ent + " --salida " + s + "tabla",
         "calculo": "regeneración documental y aritmética exacta: ENF, SINTESIS e INTEGRACION con sus validaciones y, después, las tres comparaciones"},
        {"paso": "por etapas (equivalente)", "ordenes": [
            py + " fam10-etapa --tarea ENF --entrada enf_integral=... --entrada registro_enf_integral=... --salida " + s + "enf",
            py + " fam10-validar --nueva " + s + "enf --salida " + s + "enf.validacion.json",
            py + " fam10-etapa --tarea SINTESIS --entrada enf=" + s + "enf --entrada validacion_enf=" + s + "enf.validacion.json --entrada cov=... "
            "--entrada registro_cov=... --entrada p7=... --entrada q_local=... --salida " + s + "sintesis",
            py + " fam10-validar --nueva " + s + "sintesis --salida " + s + "sintesis.validacion.json",
            py + " fam10-etapa --tarea INTEGRACION --entrada sintesis=" + s + "sintesis --entrada validacion_sintesis=" + s + "sintesis.validacion.json "
            "--entrada b1=... --entrada validacion_b1=... --entrada b2=... --entrada validacion_b2=... --salida " + s + "integracion",
            py + " fam10-validar --nueva " + s + "integracion --salida " + s + "integracion.validacion.json"]
         + [py + " fam10-comparar --tarea %s --nueva %s%s --validacion %s%s.validacion.json --salida %s%s.comparacion.json" % (t, s, t.lower(), s, t.lower(), s, t.lower())
            for t in ETAPAS]}]
    return {"comando": "fam10-receta", "estado": "lista (no ejecuta nada)", "pasos": pasos,
            "cobertura": {"operaciones": [OPERACION_DE[t] for t in ETAPAS], "etapas": list(ETAPAS)},
            "nota": ("las entradas son carpetas o archivos DENTRO de la base (cualquier nombre; no hace falta una carpeta salidas/ previa); cada una se "
                     "acepta solo con su registro aceptado; las referencias se leen únicamente en las comparaciones")}
