"""FAM13 (tablas y validaciones históricas: T1/T2 de rem107, T7/T7_anexo de rem108, validaciones E1235/E1_i2, matriz v4 de Exp0; integridad S1).

Operaciones del catálogo:
- F13-HISTORICAS (VI desde el 2026-11-18 por L-F13-VALIDADOR-REM191; sus etapas regeneran o comprueban sin modelo): cuatro etapas.
  T1T2          tablas_diseno de generar_matriz_rem107.py (U59) sobre §6.2–§6.3 del plan y D7 2a25893b; escritura con el bloque exacto de rem107.
  T7            unidades, analizar_claim y ensamblajes de generar_matriz_rem108.py (U59) sobre el paquete pv12, el registro v4 y cell_selection;
                escritura con el bloque exacto de rem108 (T7.csv, T7_anexo.csv/.json y COBERTURA.json, parte T7).
  VALIDACIONES  resultados_E1235_i1.json y resultados_E1_i2.json evalúan el modelo: NO se regeneran. Se autentican por huella (producto aceptado
                y prerregistro) y se recalcula desde los valores guardados toda la aritmética que no evalúa el modelo (criterios, Richardson,
                Romberg, dispersiones, razones, formas cerradas, referencia decimal de E3, búsqueda ternaria de E5 en la muestra guardada).
  MATRIZ_V4     versión A2 ejecutada de derivar_h4_h30_r1 (rem134) sobre la matriz A3 de rem133: H4, H30 y R1; las otras 39 filas, de A3.
- F13-S1 (verificación de integridad): nombres y SHA-256 de los 40 públicos aceptados, el mapa rem187 y la fe de erratas rem188 (proyección
  32892f0a… ligada al original 283fffd5…); los 19 internos solo por huella (cotejados en el origen durante la extracción; no se distribuyen).
U60 (validador histórico) NO está localizado (búsqueda acotada en fuentes_fam13.json): la validación de cada etapa hace comprobaciones
independientes sobre las salidas NUEVAS (para T7, el bloque T7 de prueba_ensamblajes.py de rem108); eso no acredita U60. El autor adoptó
L-F13-VALIDADOR-REM191 (2026-11-18): F13-HISTORICAS pasa de RD a VI y lo que hacen estas etapas se conserva como evidencia adicional.

Adaptaciones (no cambian fórmulas, claves, criterios ni la serialización; cada original se sustituye una sola vez y se autentica por su huella):
- GUION-v1: cada guion corre desde sus bytes con las sustituciones de SUSTITUCIONES, en el proceso, con cwd = la base; los de rem107/rem108 como
  módulo (se llaman sus funciones), A2 como __main__. La raíz histórica R es nucleo_s6/raiz (espejo de las rutas que leen).
- ESCRITURA-v1: T1/T2 y T7 se escriben con el bloque exacto de main() de su guion (sin la sangría de main), con OUT = la carpeta de la etapa.
- PLAN-EXTRACTO-v1 (rem107): tablas_diseno lee las líneas §6.2–§6.3 del extracto ligado a la huella del plan (08fc6295…).
- INVENTARIO-PROYECTADO-v1 / FILAS-FAM01-v1 / NUCLEO-INSTALADO-v1 / ENSAMBLAJE-T7-v1 (rem108): inventarios de entrega proyectados (huella del
  original), filas de unidad desde las copias exactas de FAM01, claims.py del núcleo instalado (24438732…, el del original) y ensamblajes que
  termina tras T7 (T8 y la admisibilidad no son de FAM13).
- INVENTARIO-H4-v1 / HUELLA-SANEADA-v1 (A2): el bucle H4 recorre la lista proyectada de cada entrega (copia única por archivo, una sola versión);
  HF devuelve la huella del original solo para las proyecciones saneadas declaradas (vectores.json de D2).
- MODULOS-AISLADOS: paper2b del núcleo instalado (T7) y el de la entrega de referencia (R1 de A2) no se mezclan: se purgan de sys.modules.
"""
from __future__ import annotations

import builtins
import contextlib
import csv
import datetime as dt
import importlib.util
import io
import json
import os
import re
import sys
import time
import traceback
import types
from collections import Counter
from decimal import Decimal, localcontext
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
ETIQUETA = "REPRODUCCION LIMPIA FAM13 NO OFICIAL"
RAIZ = BASE / "nucleo_s6/raiz"
DATOS = BASE / "datos/fam13"
REF = BASE / "referencias/fam13"
A107 = "paso4_conciliacion_portabilidad_desde_rem107"
A108 = "paso4_conciliacion_portabilidad_desde_rem108"
A133 = "paso4_exp0_lambda_captura_desde_rem133"
A134 = "paso4_exp0_lambda_autenticada_desde_rem134"
U59A = "nucleo_s6/raiz/tmp/%s/conciliacion/generar_matriz_rem107.py" % A107
U59B = "nucleo_s6/raiz/tmp/%s/conciliacion/generar_matriz_rem108.py" % A108
A2 = "nucleo_s6/raiz/tmp/%s/a_exp0/ejecutado/derivar_h4_h30_r1.A2.py" % A134
PRUEBA = "nucleo_s6/raiz/tmp/%s/pruebas/prueba_ensamblajes.py" % A108
ORIGINAL = {U59A: "c6a96856bcb0b09211f764fe82535cf0e8ea7499ca61c1dde0f73bbbff1d20b6", U59B: "8954fdd4ab7a7fb076f3a3bd347dd12b363122d4cbe91d2fab724ce0b40d4335",
            A2: "3305e831ef0a96867f3357cecee284e9be8906a8fb78c9aa4f0d35dc22beaf65", PRUEBA: "63e965b1c680a33a4fb6c04ead6ba30bee828cfa2dbe72f1c46886269d618304"}
T7_ANEXO_REF = "nucleo_s6/exp8/tmp/%s/conciliacion/ensamblajes/T7_anexo.json" % A108
ETAPAS = ("T1T2", "T7", "VALIDACIONES", "MATRIZ_V4", "S1")
OPERACION_DE = {"T1T2": "F13-HISTORICAS", "T7": "F13-HISTORICAS", "VALIDACIONES": "F13-HISTORICAS", "MATRIZ_V4": "F13-HISTORICAS", "S1": "F13-S1"}
PRODUCTOS = {"P_t1": ("T1T2", "ensamblajes/T1.csv", "T1.csv (rem107)"), "P_t2": ("T1T2", "ensamblajes/T2.csv", "T2.csv (rem107)"),
             "P_t7_csv": ("T7", "ensamblajes/T7.csv", "T7.csv (rem108)"), "P_t7_anexo": ("T7", "ensamblajes/T7_anexo.json", "T7_anexo.json (rem108)"),
             "P_val_e1235": ("VALIDACIONES", None, "resultados_E1235_i1.json (rem107)"), "P_val_e1i2": ("VALIDACIONES", None, "resultados_E1_i2.json (rem107)"),
             "P_matriz_v4": ("MATRIZ_V4", "salida_a2/MATRIZ_REVISADA_v4.json", "MATRIZ_REVISADA_v4.json (rem134, salida_a2)")}
PROHIBIDAS = ("referencias/fam13/", T7_ANEXO_REF)
ADAPTACIONES = ("GUION-v1", "ESCRITURA-v1", "PLAN-EXTRACTO-v1", "INVENTARIO-PROYECTADO-v1", "FILAS-FAM01-v1", "NUCLEO-INSTALADO-v1", "ENSAMBLAJE-T7-v1",
                "INVENTARIO-H4-v1", "HUELLA-SANEADA-v1", "MODULOS-AISLADOS")
NATURALEZA = {"T1T2": "regeneración documental: tablas_diseno (U59 rem107) sobre §6.2–§6.3 del plan y D7 2a25893b",
              "T7": "regeneración documental: unidades/analizar_claim/ensamblajes (U59 rem108) sobre pv12, registro v4 y cell_selection",
              "VALIDACIONES": "autenticación por huella y recálculo aritmético desde valores guardados (sin evaluar el modelo; no se regenera)",
              "MATRIZ_V4": "regeneración documental: derivar_h4_h30_r1 A2 (rem134) sobre la matriz A3 de rem133 (sin modelo)",
              "S1": "verificación de integridad: nombres y SHA-256 aceptados (sin reconstruir vistas ni repetir baterías)"}
HEX64 = re.compile(r"[0-9a-f]{64}")


class Fam13Error(Exception):
    pass


def need(c, m: str):
    if not c:
        raise Fam13Error(m)


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
        _CACHE["fu"] = leer(BASE / "fuentes_fam13.json")
    return _CACHE["fu"]


def _datos(n: str) -> dict:
    if n not in _CACHE:
        p = DATOS / n
        h = next((x["sha256"] for x in fuentes()["archivos"] if x["archivo"] == rel(p)), None)
        raw = p.read_bytes()
        need(h is not None and sha(raw) == h, "DATO_FAM13_AUSENTE_O_ALTERADO: %s" % rel(p))
        _CACHE[n] = json.loads(raw)
    return _CACHE[n]


def original() -> dict:
    """Huella de una proyección saneada -> huella de su original (fuentes_fam13.json)."""
    return {x["sha256"]: x["sha256_original"] for x in fuentes()["saneado"] if x.get("restituye_el_original") is True}


def piezas() -> list:
    fu = fuentes()
    return fu["archivos"] + fu["reutilizados"]


def _filas_fam01() -> list:
    """(archivo FAM01, huella fijada por el inventario proyectado) de cada fila de unidad que T7 lee."""
    inv = _datos("t7/INVENTARIOS_PROYECTADOS.json")["entregas"]
    out = []
    for k, a in _datos("t7/FILAS_FAM01.json")["filas"].items():
        ent, r = k.split("/", 1)
        out.append((a, inv[ent]["files"][r]["sha256"]))
    return out


def fuentes_alteradas(uso: str = "todo") -> list:
    """«calculo»: código y datos (sin referencias ni las piezas S1 que juzga la etapa S1: públicos, mapa y fe de erratas; el resumen de huellas
    aceptadas sí); «todo»: también referencias y S1."""
    def juzga_s1(a):
        return a.startswith("datos/fam13/s1/") and a != "datos/fam13/s1/HUELLAS_ACEPTADAS_S1.json"
    malos = [x["archivo"] for x in piezas() if (uso == "todo" or not (x["archivo"].startswith(("referencias/fam13/", T7_ANEXO_REF)) or juzga_s1(x["archivo"])))
             and sha_archivo(BASE / x["archivo"]) != x["sha256"]]
    try:
        malos += [a for a, h in _filas_fam01() if sha_archivo(BASE / a) != h]
    except (Fam13Error, OSError, KeyError, ValueError) as e:
        malos.append("datos/fam13/t7: %s" % e)
    return malos


# ================================================================================================ sustituciones
_H4 = '''for ent in ENT:
    _, files = _INV13(ent)   # FAM13 INVENTARIO-H4-v1: entradas proyectadas del inventario ORIGINAL de la entrega (datos/fam13/v4)
    for rel, p in _NUCLEO13(T, ent):   # FAM13 INVENTARIO-H4-v1: archivos del glob histórico de la entrega, en su orden; copia única en el espejo
        h = HF(p)
        need(files.get(rel, {}).get("sha256") == h, "NUCLEO_NO_AUTENTICO:%s/%s" % (ent, rel))
        versiones[rel][h].append(ent)
'''
SUSTITUCIONES = {
    U59A: (("PLAN-EXTRACTO-v1", '    txt = (R / FIJADOS["diseno"][0]).read_text(encoding="utf-8").splitlines()\n',
            "    txt = _PLAN13()   # FAM13 PLAN-EXTRACTO-v1: líneas §6.2–§6.3 del plan (extracto ligado a 08fc6295…)\n"),),
    U59B: (("INVENTARIO-PROYECTADO-v1", ('            p = self.T / nombre / "audit/entrega.json"\n',
                                         '            self.inv[nombre] = (H(raw) if raw else None, d.get("files") if isinstance(d.get("files"), dict) else None, list(excl))\n'),
            "            self.inv[nombre] = _INVENTARIO13(nombre)   # FAM13 INVENTARIO-PROYECTADO-v1: (huella del inventario ORIGINAL, entradas consultadas, exclusiones)\n"),
           ("FILAS-FAM01-v1 (archivo)", "        p = self.T / nombre / rel\n",
            "        p = _RUTA13(self.T, nombre, rel)   # FAM13 FILAS-FAM01-v1: filas de unidad desde las copias exactas de FAM01\n"),
           ("FILAS-FAM01-v1 (unidad)", "            d = json.loads((T / ent / rel).read_bytes())\n",
            "            d = json.loads(_RUTA13(T, ent, rel).read_bytes())   # FAM13 FILAS-FAM01-v1\n"),
           ("NUCLEO-INSTALADO-v1", '    sys.path.insert(0, str(R / "paso4/instalacion/src"))\n    from paper2b import claims as CL\n',
            "    sys.path.insert(0, str(_INSTALACION13))   # FAM13 NUCLEO-INSTALADO-v1: nucleo_s6/instalacion/src (claims.py 24438732…, el del original)\n"
            "    from paper2b import claims as CL\n"),
           ("ENSAMBLAJE-T7-v1", "    filas8, grupos = [], {}\n",
            '    return {"T7": T7, "T7_anexo": anexo7, "_cobertura": {"T7": cobertura7}}   # FAM13 ENSAMBLAJE-T7-v1: T8 y admisibilidad fuera de FAM13\n'
            "    filas8, grupos = [], {}\n")),
    A2: (("HUELLA-SANEADA-v1", "HF = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()  # noqa: E731\n",
          "HF = _HF13   # FAM13 HUELLA-SANEADA-v1: huella real; la del original solo para las proyecciones saneadas declaradas (vectores.json de D2)\n"),
         ("INVENTARIO-H4-v1", ("for ent in ENT:\n", "        versiones[rel][h].append(ent)\n"), _H4)),
}
# bloques exactos (primera y última línea, cada una única) que se ejecutan tal cual, sin la sangría de su función
BLOQUES = {
    "ESCRITURA-T1T2": (U59A, '    (OUT / "ensamblajes").mkdir()',
                       "                wr.writerow({k: (json.dumps(r[k], ensure_ascii=False) if isinstance(r.get(k), dict) else r.get(k)) for k in cols})"),
    "ESCRITURA-T7": (U59B, '    cob_ens = ens.pop("_cobertura")', '    (OUT / "ensamblajes/COBERTURA.json").write_text('),
    "PRUEBA-T7": (PRUEBA, 'por = {f["afirmacion"]: f for f in a7}', '    caso("T7-N %s se rechaza" % nombre, True, r != "ACEPTADO")'),
}


def sha13(b: bytes) -> str:
    h = sha(b)
    return original().get(h, h)


def adaptado(n: str) -> str:
    """GUION-v1: bytes de <n> (autenticados por la huella de su original) con sus sustituciones (un bloque se fija por su primera y su
    última línea; cada original, una sola vez)."""
    src = (BASE / n).read_bytes()
    need(sha13(src) == ORIGINAL[n], "CODIGO_FAM13_DISTINTO: %s" % n)
    txt = src.decode("utf-8")
    nl = "\r\n" if "\r\n" in txt else "\n"          # generar_matriz_rem107.py tiene finales CRLF: anclas y sustitutos con los del archivo
    need(nl == "\n" or txt.count("\n") == txt.count("\r\n"), "FINALES_DE_LINEA_MIXTOS: %s" % n)
    for i, a, b in SUSTITUCIONES.get(n, ()):
        a = tuple(x.replace("\n", nl) for x in a) if isinstance(a, tuple) else a.replace("\n", nl)
        b = b.replace("\n", nl)
        if isinstance(a, tuple):
            need(txt.count(a[0]) == 1 and txt.count(a[1]) == 1 and txt.index(a[0]) < txt.index(a[1]), "SUSTITUCION_NO_UNICA: %s %s" % (n, i))
            a = txt[txt.index(a[0]):txt.index(a[1]) + len(a[1])]
        need(txt.count(a) == 1, "SUSTITUCION_NO_UNICA: %s %s" % (n, i))
        txt = txt.replace(a, b)
    return txt


def bloque(k: str) -> tuple:
    """(texto sin sangría, primera línea, última línea) del bloque exacto <k> del guion original autenticado."""
    n, a, b = BLOQUES[k]
    src = (BASE / n).read_bytes()
    need(sha13(src) == ORIGINAL[n], "CODIGO_FAM13_DISTINTO: %s" % n)
    lin = src.decode("utf-8").splitlines(keepends=True)
    ia = [i for i, x in enumerate(lin) if x.startswith(a)]
    ib = [i for i, x in enumerate(lin) if x.startswith(b)]
    need(len(ia) == 1 and len(ib) == 1 and ia[0] <= ib[0], "BLOQUE_NO_UNICO: %s" % k)
    sang = len(lin[ia[0]]) - len(lin[ia[0]].lstrip(" "))
    cuerpo = lin[ia[0]:ib[0] + 1]
    need(all(not x.strip() or x.startswith(" " * sang) for x in cuerpo), "BLOQUE_CON_SANGRIA_MENOR: %s" % k)
    return "".join(x[sang:] if x.strip() else x for x in cuerpo), ia[0] + 1, ib[0] + 1


def sustituciones_ok() -> dict:
    out = {}
    for n in SUSTITUCIONES:
        try:
            compile(adaptado(n), n, "exec")
            out[n] = True
        except Exception as e:  # noqa: BLE001
            out[n] = _sin_base("%s: %s" % (type(e).__name__, e))[:200]
    for k in BLOQUES:
        try:
            compile(bloque(k)[0], k, "exec")
            out[k] = True
        except Exception as e:  # noqa: BLE001
            out[k] = _sin_base("%s: %s" % (type(e).__name__, e))[:200]
    return out


# ================================================================================================ ayudas inyectadas
def _plan13() -> list:
    ep = fuentes()["extracto_plan"]
    p = BASE / ep["archivo"]
    need(sha_archivo(p) == ep["sha256"] and ep["sha256_original"] == "08fc62957ca33f413cb0c82760426b4d57b7d37f24421d6c35d5670a23e47c9a", "EXTRACTO_DEL_PLAN_ALTERADO")
    return p.read_text(encoding="utf-8").splitlines()


def _inventario13(nombre: str) -> tuple:
    e = _datos("t7/INVENTARIOS_PROYECTADOS.json")["entregas"].get(nombre)
    if e is None:
        return (None, None, [])
    return (e["inventario_sha256"], dict(e["files"]), list(e["externos"]))


def _ruta13(T, ent, r) -> Path:
    a = _datos("t7/FILAS_FAM01.json")["filas"].get("%s/%s" % (ent, r))
    return BASE / a if a else Path(T) / ent / r


def _hf13(p) -> str:
    """HUELLA-SANEADA-v1: la huella del original solo para una proyección saneada declarada en fuentes_fam13.json con esa misma ruta."""
    p = Path(p)
    h = sha_archivo(p)
    try:
        r = rel(p)
    except ValueError:
        return h
    m = {x["archivo"]: (x["sha256"], x["sha256_original"]) for x in fuentes()["saneado"] if x.get("restituye_el_original") is True}
    return m[r][1] if r in m and m[r][0] == h else h


def _inv13(ent: str) -> tuple:
    e = _datos("v4/NUCLEO_H4_POR_ENTREGA.json")["entregas"][ent]
    return e["inventario_sha256"], {r: {"sha256": h} for r, h in e["archivos"]}


def _nucleo13(T, ent: str) -> list:
    d = _datos("v4/NUCLEO_H4_POR_ENTREGA.json")
    return [(r, Path(T) / d["copia_unica"][r] / r) for r, _ in d["entregas"][ent]["archivos"]]


def _ayudas() -> dict:
    return {"_PLAN13": _plan13, "_INVENTARIO13": _inventario13, "_RUTA13": _ruta13, "_INSTALACION13": BASE / "nucleo_s6/instalacion/src",
            "_HF13": _hf13, "_INV13": _inv13, "_NUCLEO13": _nucleo13}


def _purgar():
    """MODULOS-AISLADOS: ningún paper2b de una etapa queda en sys.modules para la siguiente."""
    for k in [k for k in sys.modules if k == "paper2b" or k.startswith("paper2b.")]:
        del sys.modules[k]


@contextlib.contextmanager
def _aislado():
    ruta, cwd = list(sys.path), os.getcwd()
    _purgar()
    try:
        os.chdir(BASE)
        yield
    finally:
        sys.path[:] = ruta
        os.chdir(cwd)
        _purgar()


def _modulo(n: str) -> dict:
    """Texto adaptado de <n> ejecutado como MÓDULO (no __main__): sus funciones y constantes."""
    g = {"__name__": "fam13_" + Path(n).stem.replace(".", "_"), "__file__": str(BASE / n), "__builtins__": builtins}
    g.update(_ayudas())
    exec(compile(adaptado(n), str(BASE / n), "exec"), g)
    return g


def _ejecutar_bloque(k: str, g: dict, **v):
    txt, _, _ = bloque(k)
    g.update(v)
    exec(compile(txt, "%s:%s" % (BLOQUES[k][0], k), "exec"), g)


def _ejecutar(n: str, args: list) -> tuple:
    """Texto adaptado de <n> como __main__ (sys.argv = [<base>/<n>, *args], cwd = la base) -> (rc, salida JSON, stdout, excepción)."""
    txt = adaptado(n)
    p = BASE / n
    g = {"__name__": "__main__", "__file__": str(p), "__builtins__": builtins}
    g.update(_ayudas())
    viejo, buf, rc, exc = sys.argv, io.StringIO(), 0, None
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
    texto = _sin_base(buf.getvalue())
    try:
        ult = json.loads(texto)
    except ValueError:
        ult = {}
    return rc, ult, texto, exc


def _productos(d: Path) -> dict:
    return {rel(p): sha_archivo(p) for p in sorted(Path(d).rglob("*")) if p.is_file() and p.name not in ("ejecucion.json", "archivos_leidos.json")}


# ================================================================================================ etapas
def _etapa_t1t2(sal: Path) -> dict:
    with _aislado():
        g = _modulo(U59A)
        T1, T2, c8 = g["tablas_diseno"](RAIZ)
        _ejecutar_bloque("ESCRITURA-T1T2", g, OUT=sal, ens={"T1": T1, "T2": T2})
    return {"guiones": [U59A], "bloques": ["ESCRITURA-T1T2"], "filas": {"T1": len(T1), "T2": len(T2)},
            "C8": {"filas_b_c": len(c8["filas_b_c"]), "D7_source_evidence_filas": c8["D7_source_evidence_filas"]}, "exito": True}


def _etapa_t7(sal: Path) -> dict:
    fu = fuentes()["t7"]
    with _aislado():
        g = _modulo(U59B)
        T = RAIZ / "tmp"
        E = g["Entregas"](T)
        U, aut, rech = g["unidades"](RAIZ, E)
        REG, SEL = g["REG"], g["SEL"]
        need(sha_archivo(T / REG[0] / REG[2]) == REG[3], "REGISTRO_V4_DISTINTO")
        need(sha_archivo(T / SEL[0] / SEL[2]) == fu["cell_selection_sha256"], "CELL_SELECTION_DISTINTA")
        reg = json.loads((T / REG[0] / REG[2]).read_bytes())["afirmaciones"]
        sel = json.loads((T / SEL[0] / SEL[2]).read_bytes())
        ens = g["ensamblajes"](RAIZ, U, reg, sel)
        need(set(ens) == {"T7", "T7_anexo", "_cobertura"}, "ENSAMBLAJE_T7_INESPERADO")
        _ejecutar_bloque("ESCRITURA-T7", g, OUT=sal, ens=ens)
    testigos = {r["cell_id"] for r in sel["S1"] if r.get("reason") in ("witness_sup", "witness_inf") and r.get("cell_id")}
    motivos = Counter(m for _, m in rech)
    return {"guiones": [U59B], "bloques": ["ESCRITURA-T7"], "paquetes": {"conformes": sum(a["conforme"] for a in aut), "total": len(aut)},
            "unidades_aceptadas": len(U), "unidades_rechazadas": dict(motivos),
            "rechazadas_que_son_testigo": sorted(u for u, _ in rech if u in testigos)[:10], "testigos_unicos": len(testigos),
            "nota": ("las unidades rechazadas por AUSENTE son las del paquete pv12 sin copia en FAM01 (no son testigo de ninguna afirmación; "
                     "fuentes_fam13.json t7.unidades_sin_copia)"),
            "exito": all(a["conforme"] for a in aut) and set(motivos) <= {"AUSENTE"} and motivos.get("AUSENTE", 0) == fu["unidades_sin_copia"]
            and not any(u in testigos for u, _ in rech)}


def _etapa_matriz(sal: Path) -> dict:
    with _aislado():
        rc, ult, texto, exc = _ejecutar(A2, [RAIZ, RAIZ / "tmp" / A134, sal / "salida_a2"])
    return {"guiones": [A2], "rc": rc, "excepcion": exc, "resumen_impreso": {k: ult.get(k) for k in ("fallos", "conforme", "matriz", "R1")},
            "exito": rc == 0 and exc is None and ult.get("conforme") is True}


# ------------------------------------------------------------------------------------------------ validaciones E1235 / E1_i2
def _k(x: float) -> str:
    return json.dumps(x)


def _cmp(nuevo, guardado) -> dict:
    return {"recalculado": nuevo, "guardado": guardado, "igual": _js(json.loads(json.dumps(nuevo))) == _js(guardado)}


def _ref_e3(t: float, phi: float) -> float:
    """Referencia decimal de 50 dígitos de validaciones_sinteticas.py (E3, def ref): ((1−τ)^φ − (1−τ))/τ."""
    with localcontext() as c:
        c.prec = 50
        xx = Decimal(1) - Decimal(repr(t))
        return float((xx ** Decimal(repr(phi)) - xx) / Decimal(repr(t)))


def _recalculo_i1(res: dict, pre: dict) -> dict:
    """resultados_E1235_i1.json: lo que se reconstruye sin evaluar el modelo (validaciones_sinteticas.py, función ejecutar)."""
    out, solo = {}, {}
    e1 = pre["E1"]
    h, k, tol = e1["h"], len(e1["h"]) - 4, e1["tolerancias"]["derivada"]
    filas, ok1 = [], True
    claves = [(n, dz) for n in e1["estados"] for dz in e1["disenos"]]
    need(len(claves) == len(res["E1"]["filas"]), "E1_I1_FILAS")
    for (n, dz), f in zip(claves, res["E1"]["filas"]):
        need(f["estado"] == n and f["diseno"] == dz and list(f["B_f0_por_eta"]) == [_k(x) for x in e1["eta_f"]], "E1_I1_CLAVES")
        b0 = [f["B_f0_por_eta"][_k(x)] for x in e1["eta_f"]]
        rk = [f["dRdtauf0_por_eta"][_k(x)] for x in e1["eta_f"]]
        exact_b = len(set(b0)) == 1
        esc = max(abs(r) for r in rk) or 1.0
        disp = (max(rk) - min(rk)) / esc
        c = exact_b and f["ingredientes_exactos_tilde_f"] and disp <= tol and b0[0] > 0
        ok1 &= c
        filas.append({"estado": n, "diseno": dz, "B_f0_identicos_exactos": _cmp(exact_b, f["B_f0_identicos_exactos"]),
                      "B_f0_positivo": _cmp(b0[0] > 0, f["B_f0_positivo"]), "dRdtauf0_richardson_h": _cmp(h[k + 1], f["dRdtauf0_richardson_h"]),
                      "dispersion_relativa_richardson": _cmp(disp, f["dispersion_relativa_richardson"]), "conforme": _cmp(c, f["conforme"])})
    out["E1"] = {"filas": filas, "conforme": _cmp(ok1, res["E1"]["conforme"])}
    solo["E1"] = ["B_f0_por_eta", "dRdtauf0_por_eta (Richardson de los cocientes del modelo)", "ingredientes_exactos_tilde_f",
                  "dispersion_relativa_cociente_por_h (los cocientes D(h) no se guardaron en i1)", "topologia_tau_f0"]
    e2, r2 = pre["E2"], res["E2"]
    x = e2["entradas"]
    a, zm, rho, k0, g = x["a"], x["z_m"], x["rho"], x["kappa0"], x["gamma"]
    zai = (k0 / g) ** (1.0 / (1.0 - rho))
    kt = zai / zm if rho == 0 else (k0 / g) / zm ** (1 - rho)
    cerr = {"m_minus": 1 - kt ** (-a / (1 - rho)), "b_minus": 1 - kt ** (-(a - 1) / (1 - rho))}
    ex = r2["exactos"]
    m_minus, b_minus, perdida = ex["masa_no_viable"], ex["participacion_B_pot"], ex["perdida_neta_sobre_B_pot"]
    T, pres = e2["tolerancias"], e2["presentacion_publicada"]
    cs, ok_cs = {}, True
    for dz in e2["tasas_para_R"]["disenos"]:
        v = r2["delta_CS"][dz]
        base_ = v["R"] / r2["B_pot"]
        nv = v["primer_z_formal"] is None or v["primer_z_formal"] >= zai
        cs[dz] = {"CS_base_completa": _cmp(base_, v["CS_base_completa"]), "delta_CS": _cmp(v["CS_base_completa"] - v["CS_solo_viables"], v["delta_CS"]),
                  "no_viables_no_aportan_a_R": _cmp(nv, v["no_viables_no_aportan_a_R"])}
        ok_cs &= v["delta_CS"] < 0 and nv
    e2ok = (abs(m_minus - cerr["m_minus"]) <= T["exacto"] and abs(b_minus - cerr["b_minus"]) <= T["exacto"] and abs(100 * m_minus - pres["masa_pct"]) <= T["presentacion"]
            and abs(100 * b_minus - pres["b_pot_pct"]) <= T["presentacion"] and abs(100 * perdida - pres["neto_pct"]) <= T["presentacion"] and ok_cs)
    out["E2"] = {"kappa_tilde0": _cmp(kt, r2["kappa_tilde0"]), "z_AI": _cmp(zai, r2["z_AI"]), "formas_cerradas_ledger": _cmp(cerr, r2["formas_cerradas_ledger"]),
                 "presentacion_publicada": _cmp(pres, r2["presentacion_publicada"]),
                 "presentacion_recalculada_pct": _cmp({"masa": round(100 * m_minus, 2), "b_pot": round(100 * b_minus, 2), "neto": round(100 * perdida, 2)},
                                                      r2["presentacion_recalculada_pct"]), "delta_CS": cs, "conforme": _cmp(e2ok, r2["conforme"])}
    solo["E2"] = ["B_pot", "exactos (momentos Pareto del núcleo)", "delta_CS.*.R", "delta_CS.*.CS_solo_viables", "delta_CS.*.primer_z_formal",
                  "delta_CS.*.topologia"]
    e3 = pre["E3"]
    filas3, ok3 = [], True
    for phi, f in zip(e3["phi"], res["E3"]["filas"]):
        need(f["phi"] == phi, "E3_CLAVES")
        fin = []
        for t, z in zip(e3["tau_f_finitos"], f["finitos"]):
            need(z["tau_f"] == t, "E3_TAU")
            fin.append({"tau_f": t, "uno_menos_phi": _cmp(1 - phi, z["uno_menos_phi"]), "diferencia": _cmp(z["s_P"] - (1 - phi), z["diferencia"]),
                        "error_vs_referencia": _cmp(abs(z["s_P"] - _ref_e3(t, phi)), z["error_vs_referencia"])})
        dref = []
        for t, z in zip(e3["sucesion"], f["sucesion"]):
            need(z["tau_f"] == t, "E3_SUCESION")
            dref.append(_ref_e3(t, phi) - (1 - phi))
        da = [abs(v) for v in dref]
        mono = all(da[i + 1] < da[i] for i in range(len(da) - 1))
        tolr, dmin = e3["tolerancias"]["referencia"], e3["tolerancias"]["diferencia_minima"]
        c = (all(abs(z["diferencia"]) > dmin for z in f["finitos"]) and all(abs(z["s_P"] - _ref_e3(z["tau_f"], phi)) <= tolr for z in f["finitos"])
             and all(z["error_vs_referencia"] <= tolr for z in f["sucesion"]) and mono and da[-1] < 1e-6)
        ok3 &= c
        filas3.append({"phi": phi, "finitos": fin, "dif_referencia_sucesion": _cmp(dref, [z["dif_referencia"] for z in f["sucesion"]]),
                       "monotona_hacia_0": _cmp(mono, f["monotona_hacia_0"]), "razon_ultimos": _cmp(da[-1] / da[-2], f["razon_ultimos"]),
                       "ultima_diferencia": _cmp(da[-1], f["ultima_diferencia"]),
                       "termino_principal_teorico_ultimo": _cmp(-phi * (1 - phi) * e3["sucesion"][-1] / 2, f["termino_principal_teorico_ultimo"]),
                       "conforme": _cmp(c, f["conforme"])})
    out["E3"] = {"filas": filas3, "conforme": _cmp(ok3, res["E3"]["conforme"])}
    solo["E3"] = ["finitos.s_P (núcleo)", "sucesion.dif_nucleo y sucesion.error_vs_referencia (s_P de la sucesión no se guardó)"]
    e5 = pre["E5"]
    filas5, ok5 = [], True
    for eta, f in zip(e5["eta_d"], res["E5"]["filas"]):
        need(f["eta_d"] == eta, "E5_CLAVES")

        def C(u, eta=eta):
            return u - eta / (eta + 1.0) * (1.0 - (1.0 - u) ** ((eta + 1.0) / eta))
        peor_opt, peor_id = 0.0, 0.0
        mu = f["muestra"]
        need([m["tau_d"] for m in mu] == e5["tau_d"][::24], "E5_MUESTRA")
        for m in mu:
            t, r, tt = m["tau_d"], m["r_star"], m["tilde_d"]
            lo, hi = 0.0, 1.0
            for _ in range(200):
                m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
                if t * m1 + C(1 - m1) < t * m2 + C(1 - m2):
                    hi = m2
                else:
                    lo = m1
            peor_opt = max(peor_opt, abs((lo + hi) / 2 - r))
            peor_id = max(peor_id, abs(tt - (t * r + C(1 - r))))
        dec_m = all(mu[i + 1]["r_star"] < mu[i]["r_star"] for i in range(len(mu) - 1))
        menor_m = all(m["tilde_d"] < m["tau_d"] for m in mu)
        c = (f["r_star_estrictamente_decreciente"] and f["tilde_d_menor_que_tau_d"] and f["max_error_optimo_vs_busqueda"] <= e5["tolerancias"]["optimo"]
             and f["max_error_identidad_tasa_efectiva"] <= e5["tolerancias"]["tasa_efectiva"])
        ok5 &= c
        filas5.append({"eta_d": eta, "muestra_puntos": len(mu), "muestra_error_optimo_max": peor_opt, "muestra_error_identidad_max": peor_id,
                       "muestra_dentro_de_los_maximos_guardados": peor_opt <= f["max_error_optimo_vs_busqueda"] and peor_id <= f["max_error_identidad_tasa_efectiva"],
                       "muestra_decreciente_y_menor": dec_m and menor_m,
                       "conforme_desde_componentes_guardados": _cmp(c, f["conforme"])})
    out["E5"] = {"filas": filas5, "conforme": _cmp(ok5, res["E5"]["conforme"])}
    solo["E5"] = ["r_star y tilde_d fuera de la muestra (cada 24.º punto)", "max/min_brecha_tau_menos_tilde", "max_error_* sobre la rejilla completa",
                  "limite_fuera_del_criterio (η_d = 0)"]
    total = all(res["fuentes_verificadas"].values()) and ok1 and e2ok and ok3 and ok5
    out["conforme_global"] = _cmp(total, res["conforme"])
    solo["global"] = ["fuentes_verificadas (huellas del árbol original en 2026-10-28)", "ejecutado_utc"]
    return {"recalculado": out, "solo_autenticado": solo}


def _recalculo_i2(res: dict, pre: dict, pre2: dict) -> dict:
    """resultados_E1_i2.json: tabla de Romberg, dispersiones y criterios desde D_por_eta y B_f0 guardados (e1_romberg.py, ejecutar)."""
    fx, crit = pre["E1"], pre2["criterios"]
    filas, ok = [], True
    claves = [(n, dz) for n in fx["estados"] for dz in fx["disenos"]]
    need(len(claves) == len(res["filas"]), "E1_I2_FILAS")
    for (n, dz), f in zip(claves, res["filas"]):
        need(f["estado"] == n and f["diseno"] == dz and list(f["D_por_eta"]) == [_k(x) for x in fx["eta_f"]], "E1_I2_CLAVES")
        por = {}
        for ef in fx["eta_f"]:
            D = f["D_por_eta"][_k(ef)]
            need(len(D) == len(fx["h"]), "E1_I2_D")
            T = [D]
            for lvl in range(1, 4):
                p = T[-1]
                T.append([(2 ** lvl * p[i + 1] - p[i]) / (2 ** lvl - 1) for i in range(len(p) - 1)])
            por[ef] = {"B_f0": f["B_f0"][_k(ef)], "D": D, "romberg3": T[3][-1]}
        b0 = {ef: x["B_f0"] for ef, x in por.items()}
        rb = [x["romberg3"] for x in por.values()]
        esc = max(abs(r) for r in rb)
        disp = [(max(x["D"][i] for x in por.values()) - min(x["D"][i] for x in por.values())) / esc for i in range(len(fx["h"]))]
        razones = [disp[i + 1] / disp[i] for i in range(len(disp) - 1)]
        drb = (max(rb) - min(rb)) / esc
        c = len(set(b0.values())) == 1 and all(0.45 <= r <= 0.55 for r in razones) and drb <= crit["romberg"]
        ok &= c
        filas.append({"estado": n, "diseno": dz, "romberg3_por_eta": _cmp(dict(zip(fx["eta_f"], rb)), f["romberg3_por_eta"]),
                      "dispersion_relativa_romberg3": _cmp(drb, f["dispersion_relativa_romberg3"]),
                      "dispersion_relativa_por_h": _cmp(dict(zip(fx["h"], disp)), f["dispersion_relativa_por_h"]),
                      "razones_sucesivas": _cmp(razones, f["razones_sucesivas"]), "conforme": _cmp(c, f["conforme"])})
    return {"recalculado": {"filas": filas, "conforme": _cmp(ok, res["conforme"])},
            "solo_autenticado": {"E1_i2": ["B_f0 (evaluación del modelo en τ_f = 0)", "D_por_eta (cocientes del modelo)", "ejecutado_utc"]}}


def _hojas_cmp(x, pre=()):
    if isinstance(x, dict) and set(x) == {"recalculado", "guardado", "igual"}:
        yield pre, x["igual"]
    elif isinstance(x, dict):
        for k, v in x.items():
            yield from _hojas_cmp(v, pre + (k,))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from _hojas_cmp(v, pre + (i,))


def _etapa_validaciones(sal: Path) -> dict:
    hu = fuentes()["huellas_aceptadas"]
    V = DATOS / "validaciones"
    raw = {n: (V / n).read_bytes() for n in ("resultados_E1235_i1.json", "resultados_E1_i2.json", "prerregistro_E1235.json", "prerregistro_E1_i2.json")}
    i1, i2 = json.loads(raw["resultados_E1235_i1.json"]), json.loads(raw["resultados_E1_i2.json"])
    pre, pre2 = json.loads(raw["prerregistro_E1235.json"]), json.loads(raw["prerregistro_E1_i2.json"])
    aut = {"P_val_e1235": {"sha256": sha(raw["resultados_E1235_i1.json"]), "aceptado": hu["P_val_e1235"],
                           "prerregistro_ligado": i1["prerregistro_sha256"] == sha(raw["prerregistro_E1235.json"])},
           "P_val_e1i2": {"sha256": sha(raw["resultados_E1_i2.json"]), "aceptado": hu["P_val_e1i2"],
                          "prerregistro_ligado": i2["prerregistro_sha256"] == sha(raw["prerregistro_E1_i2.json"]),
                          "prerregistro_basado_en_E1235": pre2["base"].startswith("prerregistro_E1235.json (%s" % sha(raw["prerregistro_E1235.json"])[:8])
                          and pre2.get("fijado_tras_observar_i1") is True}}
    for v in aut.values():
        v["autenticado"] = v["sha256"] == v["aceptado"] and all(x for k, x in v.items() if k.startswith("prerregistro"))
    r1 = _recalculo_i1(i1, pre)
    r2 = _recalculo_i2(i2, pre, pre2)
    doc = {"kind": "verificacion-validaciones-fam13", "regla": ("los dos resultados evalúan el modelo: no se regeneran; se autentican por huella y "
                                                                "prerregistro y se recalcula desde los valores guardados lo que no evalúa el modelo"),
           "autenticacion": aut, "E1235_i1": r1, "E1_i2": r2,
           "resultado_original_conservado": {"E1_i1_conforme": i1["E1"]["conforme"], "E1_i2_conforme": i2["conforme"],
                                             "lectura": "E1 i1 NO CONFORME (Richardson O(h²) con tolerancia 1e-9) se conserva; E1 i2 (Romberg) CONFORME"}}
    _escribir_x(sal / "VERIFICACION_VALIDACIONES.json", doc)
    hojas = [(p, ok) for r in (r1["recalculado"], r2["recalculado"]) for p, ok in _hojas_cmp(r)]
    return {"guiones": [], "autenticados": {k: v["autenticado"] for k, v in aut.items()}, "campos_recalculados": len(hojas),
            "campos_recalculados_iguales": sum(1 for _, ok in hojas if ok),
            "distintos": ["/".join(map(str, p)) for p, ok in hojas if not ok][:20], "exito": all(v["autenticado"] for v in aut.values())}


# ------------------------------------------------------------------------------------------------ S1
def integridad_s1(d: Path | None = None) -> dict:
    """F13-S1: los 40 públicos (nombre, tamaño y SHA-256), el mapa rem187 y la fe de erratas proyectada contra las huellas aceptadas (resumen
    autenticado por fuentes_fam13.json). d: carpeta con publico/, el mapa y la fe (por omisión, datos/fam13/s1)."""
    hu = _datos("s1/HUELLAS_ACEPTADAS_S1.json")
    d = Path(d) if d is not None else DATOS / "s1"
    esperados = hu["publico"]
    carpeta_publica = d / "publico"
    pub = {p.relative_to(carpeta_publica).as_posix(): p for p in carpeta_publica.rglob("*") if p.is_file()}
    faltan = sorted(set(esperados) - set(pub))
    ajenos = sorted(set(pub) - set(esperados))
    distintos = sorted(n for n, x in esperados.items() if n in pub and (sha_archivo(pub[n]) != x["sha256"] or pub[n].stat().st_size != x["bytes"]))
    mp, ep = d / hu["mapa"]["archivo"], d / hu["fe_de_erratas"]["proyeccion"]["archivo"]
    mapa_ok = mp.is_file() and sha_archivo(mp) == hu["mapa"]["sha256"]
    fe = hu["fe_de_erratas"]
    err = {"proyeccion_sha256": sha_archivo(ep) if ep.is_file() else None, "proyeccion_aceptada": fe["proyeccion"]["sha256"],
           "original_sha256": fe["original"]["sha256"], "original_en_el_paquete": False}
    if ep.is_file():
        e = json.loads(ep.read_bytes())
        err.update(remite_al_mapa=e.get("source_sha256") == hu["mapa"]["sha256"], marcador_en_source_path=str(e.get("source_path", "")).startswith("@@R_FS@@/"),
                   marcadores=ep.read_bytes().count(b"@@R_FS@@"))
    err["conforme"] = (err["proyeccion_sha256"] == err["proyeccion_aceptada"] and err.get("remite_al_mapa") is True and err.get("marcador_en_source_path") is True
                       and err.get("marcadores") == fe["proyeccion"]["marcadores"]["@@R_FS@@"])
    internos = hu["interno_fuera_de_la_distribucion"]
    out = {"publicos": {"aceptados": len(esperados), "presentes": len(pub), "iguales": len(esperados) - len(faltan) - len(distintos),
                        "faltan": faltan, "ajenos": ajenos, "distintos": distintos},
           "mapa": {"archivo": hu["mapa"]["archivo"], "sha256": sha_archivo(mp) if mp.is_file() else None, "aceptado": hu["mapa"]["sha256"], "conforme": mapa_ok},
           "fe_de_erratas": err,
           "internos": {"n": len(internos), "cotejados_en_origen_durante_la_extraccion": sum(1 for x in internos.values() if x["cotejado_en_origen"]),
                        "en_el_paquete": 0, "nota": "fuera de la distribución y de las dependencias de la orden (solo sus huellas aceptadas)"},
           "aceptacion": {k: hu["aceptacion"][k] for k in ("archivo", "sha256", "dictamen_sha256", "verificador_sha256")},
           "cierre": {k: hu["cierre"][k] for k in ("archivo", "sha256")}}
    out["conforme"] = (len(esperados) == 40 and not faltan and not ajenos and not distintos and mapa_ok and err["conforme"] and len(internos) == 19
                       and all(x["cotejado_en_origen"] for x in internos.values()))
    return out


def _etapa_s1(sal: Path) -> dict:
    r = integridad_s1()
    _escribir_x(sal / "INTEGRIDAD_S1.json", r)
    return {"guiones": [], "integridad": {k: r[k] for k in ("publicos", "conforme")}, "exito": True}


ETAPA_FN = {"T1T2": _etapa_t1t2, "T7": _etapa_t7, "VALIDACIONES": _etapa_validaciones, "MATRIZ_V4": _etapa_matriz, "S1": _etapa_s1}


def entorno() -> dict:
    import platform
    return {"python": platform.python_version(), "hash_seed": os.environ.get("PYTHONHASHSEED"), "hash_randomization": sys.flags.hash_randomization,
            "TZ": os.environ.get("TZ"), "separador_de_rutas": os.sep}


def correr(tarea: str, sal: Path) -> dict:
    """Una etapa en la carpeta NUEVA sal (dentro de la base); registra lecturas y productos."""
    T0 = time.time()
    need(tarea in ETAPAS, "ETAPA_FUERA_DE_FAM13: %s" % tarea)
    rastro = F1().Rastro()
    sal = Path(sal)
    need(not sal.exists(), "LA_SALIDA_YA_EXISTE")
    sal.mkdir(parents=True)
    sal = _dentro(sal)
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
            "codigo_leido": sorted(x for x in en if x in ORIGINAL), "filas_fam01_leidas": sum(1 for x in en if x.startswith("referencias/fam01/")),
            "referencias_leidas": sorted(x for x in en if x.startswith("referencias/") and not x.startswith("referencias/fam01/")),
            "referencia_esperada_leida": any(x.startswith(PROHIBIDAS) for x in en)}
    ej = {"etiqueta": ETIQUETA, "tarea": tarea, "operacion": OPERACION_DE[tarea], "naturaleza": NATURALEZA[tarea], "adaptaciones": list(ADAPTACIONES),
          "inicio_utc": inicio, "fin_utc": fin, "detalle": det, "excepcion": exc, "productos_sha256": _productos(sal),
          "codigo": {n: {"archivo_sha256": sha_archivo(BASE / n), "original_sha256": ORIGINAL[n], "adaptado_sha256": sha(adaptado(n).encode("utf-8")),
                         "sustituciones": [s[0] for s in SUSTITUCIONES.get(n, ())]} for n in det.get("guiones", [])},
          "segundos": round(time.time() - T0, 3), "entorno": entorno(), "lecturas": lect}
    ej["exito"] = bool(det.get("exito")) and exc is None and not lect["fuera_del_paquete_y_del_interprete"] and not lect["referencia_esperada_leida"]
    _escribir(sal / "ejecucion.json", ej)
    return ej


# ================================================================================================ validación (sin referencias)
def _csv(p: Path) -> list:
    with Path(p).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _validar_t1t2(d: Path) -> dict:
    t1, t2 = _csv(d / "ensamblajes/T1.csv"), _csv(d / "ensamblajes/T2.csv")
    reg = {r["parameter_id"] for r in _csv(RAIZ / "salidas_s6/d7/versions/2a25893b09c097b2af22ed2e5be9a4014851faf55bbaaf380c7a078f1a740591/parameter_registry.csv")}
    ex = {"T1_nueve_numeros_1_a_9": [r["n"] for r in t1] == [str(i) for i in range(1, 10)],
          "T1_parametros_en_D7": all(r["parametro_D7"] in reg for r in t1),
          "T1_soportes_json": all(isinstance(json.loads(r["soportes_base_D7"]), list) for r in t1),
          "T2_ocho_ecuaciones_a_h": [r["fila"] for r in t2] == list("abcdefgh"),
          "T2_estado_asignado_no_vacio": all(r["estado_asignado"] for r in t2),
          "columnas_ordenadas_regla_rem107": all(list(x[0]) == sorted(x[0], key=lambda k: (k in ("otras_restricciones_rechazos", "nota"), k)) for x in (t1, t2) if x)}
    return {"comprobaciones": ex, "recuentos": {"T1": len(t1), "T2": len(t2)}, "aceptada": all(ex.values())}


def _validar_t7(d: Path) -> dict:
    a7 = json.loads((d / "ensamblajes/T7_anexo.json").read_bytes())["filas"]
    cob = json.loads((d / "ensamblajes/COBERTURA.json").read_bytes())
    t7 = _csv(d / "ensamblajes/T7.csv")
    casos = []

    def caso(cid, esperado, obtenido):
        casos.append({"id": cid, "esperado": esperado, "obtenido": obtenido, "conforme": obtenido == esperado})
    exc = None
    with _aislado():
        try:
            g = _modulo(U59B)
            T = RAIZ / "tmp"
            reg = json.loads((T / g["REG"][0] / g["REG"][2]).read_bytes())["afirmaciones"]
            sys.path.insert(0, str(BASE / "nucleo_s6/instalacion/src"))
            from paper2b import claims as CL  # noqa: E402
            ns = {"reg": reg, "a7": a7, "cob": cob, "M": types.SimpleNamespace(analizar_claim=g["analizar_claim"], REG=g["REG"]), "CL": CL, "caso": caso,
                  "json": json, "__builtins__": builtins}
            exec(compile(bloque("PRUEBA-T7")[0], "%s:PRUEBA-T7" % PRUEBA, "exec"), ns)
        except Exception:  # noqa: BLE001
            exc = _sin_base(traceback.format_exc())[-1500:]
    # recomputación independiente: T7 desde el anexo nuevo (recuentos por clave, G mín/máx) y G de cada testigo = G de sus filas aceptadas
    grupos = {}
    for f in a7:
        k = (f["pais"] or "global(%s)" % f["pid"], f["familia"], f["diseno"], f["cota"], f["capa"], f["bloque"])
        x = grupos.setdefault(k, {"cats": Counter(), "Gsup": [], "Ginf": []})
        x["cats"][f["categoria_original"]] += 1
        for lado in ("sup", "inf"):
            if f.get(lado + "_G") is not None:
                x["G" + lado].append(f[lado + "_G"])
    clave = ("pais_o_ambito", "familia", "diseno", "cota", "capa", "bloque")
    filas_csv = {tuple(r[c] for c in clave): r for r in t7}
    mal = []
    for k, x in grupos.items():
        r = filas_csv.get(k)
        esperado = {**{c: str(n) for c, n in x["cats"].items()}, "total": str(sum(x["cats"].values())),
                    "G_sup_min": repr(min(x["Gsup"])) if x["Gsup"] else "null", "G_sup_max": repr(max(x["Gsup"])) if x["Gsup"] else "null",
                    "G_inf_min": repr(min(x["Ginf"])) if x["Ginf"] else "null", "G_inf_max": repr(max(x["Ginf"])) if x["Ginf"] else "null"}
        if r is None or any(r.get(c) != v for c, v in esperado.items()):
            mal.append(list(k))
    filas_g, mal_g, leidos = 0, [], {}
    for f in a7:
        for lado in ("sup", "inf"):
            if f.get(lado + "_G") is None:
                continue
            filas_g += 1
            ent, r = f[lado + "_ref"].split("/", 1)
            p = _ruta13(RAIZ / "tmp", ent, r)
            if p not in leidos:
                b = p.read_bytes()
                dd = json.loads(b)
                leidos[p] = (sha(b), ((dd.get("confrontation_result") or [{}])[0]).get("G"))
            h, G = leidos[p]
            if h != f[lado + "_filas_sha256"] or G != f[lado + "_G"]:
                mal_g.append([f["afirmacion"], lado])
    c7 = cob.get("T7") or {}
    ex = {"bloque_T7_prueba_ensamblajes_rem108": exc is None and len(casos) == 11 and all(c["conforme"] for c in casos),
          "T7_igual_a_su_recalculo_desde_el_anexo": not mal and len(grupos) == len(t7),
          "T7_total_1728": sum(int(r["total"]) for r in t7) == 1728,
          "testigos_G_y_huella_de_sus_filas": not mal_g and filas_g == c7.get("testigos_con_filas"),
          "testigos_contados": c7.get("testigos_con_filas", 0) + c7.get("testigos_sin_filas", 0) == 2 * len(a7),
          "cobertura_sin_omitidas_ni_ajenas": c7.get("omitidas") == [] and c7.get("ajenas") == [] and c7.get("unicas") == len(a7) == c7.get("fuente")}
    return {"comprobaciones": ex, "casos_prueba_ensamblajes": casos, "excepcion": exc, "t7_mal": mal[:10], "testigos_mal": mal_g[:10],
            "recuentos": {"afirmaciones": len(a7), "filas_T7": len(t7), "por_familia": c7.get("por_familia"), "categorias": c7.get("categorias"),
                          "testigos_con_filas": c7.get("testigos_con_filas"), "testigos_sin_filas": c7.get("testigos_sin_filas"), "archivos_de_filas_leidos": len(leidos)},
            "aceptada": all(ex.values())}


def _validar_validaciones(d: Path) -> dict:
    v = json.loads((d / "VERIFICACION_VALIDACIONES.json").read_bytes())
    por = {k: [ok for _, ok in _hojas_cmp(v[k]["recalculado"])] for k in ("E1235_i1", "E1_i2")}
    ex = {"autenticados_por_huella_y_prerregistro": all(x["autenticado"] for x in v["autenticacion"].values()),
          "recalculo_igual_a_lo_guardado": all(x and all(x) for x in por.values()),
          "E1_i1_no_conforme_conservado": v["resultado_original_conservado"]["E1_i1_conforme"] is False,
          "E1_i2_conforme_conservado": v["resultado_original_conservado"]["E1_i2_conforme"] is True}
    return {"comprobaciones": ex, "recuentos": {k: {"campos_recalculados": len(x), "iguales": sum(x)} for k, x in por.items()}
            | {"P_val_e1235": "E1235_i1", "P_val_e1i2": "E1_i2"}, "aceptada": all(ex.values())}


def _validar_matriz(d: Path) -> dict:
    S = d / "salida_a2"
    mat = json.loads((S / "MATRIZ_REVISADA_v4.json").read_bytes())["filas"]
    res = json.loads((S / "RESUMEN_A_rem134.json").read_bytes())
    a3 = json.loads((RAIZ / "tmp" / A133 / "a_exp0/salida_a3/MATRIZ_REVISADA.json").read_bytes())["filas"]
    iar3 = json.loads((RAIZ / "tmp" / A133 / "a_exp0/salida_a3/input_audit_report_v2.json").read_bytes())["filas"]
    iar4 = json.loads((S / "input_audit_report_v4.json").read_bytes())["filas"]
    A3 = {m["requisito"]: m for m in a3}
    v4 = {m["requisito"]: m for m in mat}
    tres = ("H4", "H30", "R1")
    esperada = {"H4": "retrospectiva_comprobada_con_hallazgo", "H30": "contemporanea", "R1": "retrospectiva_comprobada"}
    ex = {"ejecucion_sin_fallos": res.get("conforme") is True and res.get("fallos") == [],
          "cuarenta_y_dos_requisitos_en_orden_A3": [m["requisito"] for m in mat] == [m["requisito"] for m in a3] and len(mat) == 42,
          "treinta_y_nueve_filas_A3_intactas": all(_js(v4[k]) == _js(A3[k]) for k in A3 if k not in tres),
          "H4_H30_R1_solo_cambian_campos_de_la_revision": all(set(k2 for k2 in set(v4[k]) | set(A3[k]) if v4[k].get(k2) != A3[k].get(k2))
                                                             <= {"clase_evidencia", "resultado", "evidencia", "accion_minima"} for k in tres),
          "clase_de_evidencia_H4_H30_R1": {k: v4[k]["clase_evidencia"] for k in tres} == esperada,
          "informe_de_entradas_fuera_de_H4_H30_R1_intacto": len(iar4) == len(iar3) and all(_js(a) == _js(b) for a, b in zip(iar4, iar3) if a["gate_id"] not in tres)}
    clases = dict(Counter(m["clase_evidencia"] for m in mat))
    return {"comprobaciones": ex, "recuentos": {"requisitos": len(mat), "por_clase_de_evidencia": clases, "A3_por_clase": dict(Counter(m["clase_evidencia"] for m in a3)),
                                                "R1": res.get("R1"), "H4_total": (res.get("H4") or {}).get("total")},
            "lectura": ("H30 es evidencia CONTEMPORÁNEA (índice D-3 y manifiestos fijados por D7); H4 y R1 son reconstrucciones RETROSPECTIVAS "
                        "comprobadas (H4 con hallazgo formal sin impacto numérico); la fila reconstruccion_rem133 y las demás conservan la clase de A3"),
            "aceptada": all(ex.values())}


def _validar_s1(d: Path) -> dict:
    r = json.loads((d / "INTEGRIDAD_S1.json").read_bytes())
    return {"comprobaciones": {"integridad_conforme": r["conforme"] is True}, "recuentos": r["publicos"], "aceptada": r["conforme"] is True}


VALIDAR_FN = {"T1T2": _validar_t1t2, "T7": _validar_t7, "VALIDACIONES": _validar_validaciones, "MATRIZ_V4": _validar_matriz, "S1": _validar_s1}


def validar(d: Path) -> dict:
    """Comprobaciones independientes sobre la salida NUEVA, sin leer las referencias (U60 no localizado; L-F13-VALIDADOR-REM191 adoptada)."""
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
    r.update({"comando": "fam13-validar", "tarea": ej["tarea"], "origen": rel(d), "inventory_sha256": sha_archivo(d / "ejecucion.json"),
              "validador": ("U60 NO LOCALIZADO: comprobaciones independientes sobre la salida nueva (para T7, el bloque T7 de prueba_ensamblajes.py "
                            "de rem108); no acredita U60. L-F13-VALIDADOR-REM191 adoptada por el autor (2026-11-18): F13-HISTORICAS es VI y "
                            "esta validación se conserva como evidencia adicional"),
              "lecturas": {"en_el_paquete": len(inf["en_el_paquete"]), "fuera_del_paquete_y_del_interprete": inf["fuera_del_paquete_y_del_interprete"],
                           "referencia_esperada_leida": any(x.startswith(PROHIBIDAS) for x in inf["en_el_paquete"])},
              "segundos": round(time.time() - t0, 3)})
    r["aceptada"] = bool(r["aceptada"]) and not r["lecturas"]["referencia_esperada_leida"] and not r["lecturas"]["fuera_del_paquete_y_del_interprete"]
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
    """Tipo de una diferencia: procedencia (tiempo, ruta, huella) con su vínculo comprobado, o científica."""
    d = {"campo": "/".join(str(x) for x in p), "nuevo": a if a is not _FALTA else "<ausente>", "referencia": b if b is not _FALTA else "<ausente>"}
    if a is _FALTA or b is _FALTA:
        return dict(d, tipo="cientifica")
    last = p[-1] if p else None
    if last == "segundos" and len(p) == 1 and isinstance(a, (int, float)):
        return dict(d, tipo="procedencia:tiempo", vinculo="segundos de esta ejecución (RESUMEN)", vinculo_ok=True)
    if isinstance(a, str) and isinstance(b, str):
        if last == "ruta":
            q = RAIZ / a.replace("\\", "/")
            ok = a.replace("\\", "/") == b.replace("\\", "/") and q.is_file()
            return dict(d, tipo="procedencia:ruta (separador del sistema)", vinculo=rel(q) if q.is_file() else None, vinculo_ok=ok)
        if HEX64.fullmatch(a) and HEX64.fullmatch(b):
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


def _comparar_filas(nuevas: list, refs: list, clave, ctx: dict) -> dict:
    kf = (lambda f: tuple(f[c] for c in clave)) if isinstance(clave, tuple) else (lambda f: f[clave])
    kn, kr = [kf(f) for f in nuevas], [kf(f) for f in refs]
    N, Rf = dict(zip(kn, nuevas)), dict(zip(kr, refs))
    difs = []
    for k in kn:
        if k in Rf:
            difs += [dict(x, clave=list(k) if isinstance(k, tuple) else k) for x in _dif(N[k], Rf[k], ctx)]
    r = _resumen(difs)
    r.update({"filas_nuevas": len(nuevas), "filas_referencia": len(refs), "faltan": [list(x) if isinstance(x, tuple) else x for x in sorted(set(kr) - set(kn))][:20],
              "ajenas": [list(x) if isinstance(x, tuple) else x for x in sorted(set(kn) - set(kr))][:20], "duplicadas": len(kn) - len(set(kn)),
              "mismo_orden": kn == kr, "filas_identicas": sum(1 for k in kn if k in Rf and _js(N[k]) == _js(Rf[k]))})
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


def _comparar_t1t2(d: Path, ctx: dict) -> dict:
    hu = fuentes()["huellas_aceptadas"]
    out = {}
    for k, n, cl in (("P_t1", "T1.csv", "n"), ("P_t2", "T2.csv", "fila")):
        b = _bytes(d / "ensamblajes" / n, REF / "rem107" / n, hu[k])
        f = _comparar_filas(_csv(d / "ensamblajes" / n), _csv(REF / "rem107" / n), cl, ctx)
        out[k] = {"bytes": b, "filas": f, "cumple": f["cumple"] and b["bytes_identicos"] and b["igual_a_la_huella_aceptada"]}
    return {"productos": out, "cumple": all(x["cumple"] for x in out.values())}


def _comparar_t7(d: Path, ctx: dict) -> dict:
    hu = fuentes()["huellas_aceptadas"]
    clave = ("pais_o_ambito", "familia", "diseno", "cota", "capa", "bloque")
    b7 = _bytes(d / "ensamblajes/T7.csv", REF / "rem108/T7.csv", hu["P_t7_csv"])
    f7 = _comparar_filas(_csv(d / "ensamblajes/T7.csv"), _csv(REF / "rem108/T7.csv"), clave, ctx)
    ba = _bytes(d / "ensamblajes/T7_anexo.json", BASE / T7_ANEXO_REF, hu["P_t7_anexo"])
    fa = _comparar_filas(json.loads((d / "ensamblajes/T7_anexo.json").read_bytes())["filas"], json.loads((BASE / T7_ANEXO_REF).read_bytes())["filas"], "afirmacion", ctx)
    cob = _resumen(_dif(json.loads((d / "ensamblajes/COBERTURA.json").read_bytes())["T7"], json.loads((REF / "rem108/COBERTURA.json").read_bytes())["T7"], ctx))
    cob["cumple"] = cob["cientificas_n"] == 0 and cob["procedencia_vinculada"]
    out = {"P_t7_csv": {"bytes": b7, "filas": f7, "cumple": f7["cumple"] and b7["bytes_identicos"] and b7["igual_a_la_huella_aceptada"]},
           "P_t7_anexo": {"bytes": ba, "filas": fa, "cumple": fa["cumple"] and ba["bytes_identicos"] and ba["igual_a_la_huella_aceptada"],
                          "referencia_doble_papel": ("T7_anexo aceptado de FAM10 (070f3c8e…): también es entrada de F10-ENF-AFIRMACION (U41, "
                                                     "conciliar_exp8_rem147.py) y de la copia de sus filas padre; aquí solo se compara")}}
    return {"productos": out, "COBERTURA_T7": cob, "T7_anexo_csv": {"nuevo_sha256": sha_archivo(d / "ensamblajes/T7_anexo.csv"),
                                                                    "nota": "producto auxiliar del mismo bloque de escritura; sin referencia en el catálogo"},
            "cumple": all(x["cumple"] for x in out.values()) and cob["cumple"]}


def _comparar_validaciones(d: Path, ctx: dict) -> dict:
    v = json.loads((d / "VERIFICACION_VALIDACIONES.json").read_bytes())
    out = {}
    for k in ("P_val_e1235", "P_val_e1i2"):
        a = v["autenticacion"][k]
        out[k] = {"regenerado": False, "motivo": "evalúa el modelo (fuera del alcance: sin evaluar el modelo)", "autenticado_por_huella": a["autenticado"],
                  "sha256": a["sha256"], "aceptado": a["aceptado"], "cumple": a["autenticado"]}
    return {"productos": out, "cumple": all(x["cumple"] for x in out.values())}


def _comparar_matriz(d: Path, ctx: dict) -> dict:
    hu = fuentes()["huellas_aceptadas"]
    S, RS = d / "salida_a2", REF / "rem134/salida_a2"
    docs = {}
    for n in ("H4_LITERALES.json", "H30_INDICE_DERIVACION.json", "R1_ESCENARIOS.json", "MATRIZ_REVISADA_v4.json", "RESUMEN_A_rem134.json", "input_audit_report_v4.json"):
        b = _bytes(S / n, RS / n, hu["P_matriz_v4"] if n == "MATRIZ_REVISADA_v4.json" else None)
        r = _resumen(_dif(json.loads((S / n).read_bytes()), json.loads((RS / n).read_bytes()), ctx))
        docs[n] = {"bytes": b, **r, "cumple": r["cientificas_n"] == 0 and r["procedencia_vinculada"]}
    mf = _comparar_filas(json.loads((S / "MATRIZ_REVISADA_v4.json").read_bytes())["filas"], json.loads((RS / "MATRIZ_REVISADA_v4.json").read_bytes())["filas"],
                         "requisito", ctx)
    out = {"P_matriz_v4": {"bytes": docs["MATRIZ_REVISADA_v4.json"]["bytes"], "filas": mf,
                           "cumple": mf["cumple"] and docs["MATRIZ_REVISADA_v4.json"]["bytes"]["igual_a_la_huella_aceptada"]}}
    return {"productos": out, "documentos_A2": docs, "cumple": out["P_matriz_v4"]["cumple"] and all(x["cumple"] for x in docs.values())}


def _comparar_s1(d: Path, ctx: dict) -> dict:
    r = json.loads((d / "INTEGRIDAD_S1.json").read_bytes())
    return {"productos": {}, "integridad": r, "cumple": r["conforme"] is True}


COMPARAR_FN = {"T1T2": _comparar_t1t2, "T7": _comparar_t7, "VALIDACIONES": _comparar_validaciones, "MATRIZ_V4": _comparar_matriz, "S1": _comparar_s1}


def comparar(d: Path, validacion: Path) -> dict:
    """DESPUÉS de producir y validar: igualdad exacta del contenido científico por clave (clasificaciones de G, estados, recuentos); cada
    diferencia de ruta, hora o huella se identifica y se comprueba su vínculo; una diferencia científica deja el producto pendiente."""
    t0 = time.time()
    d, validacion = _dentro(d), _dentro(validacion)
    ej = leer(d / "ejecucion.json")
    val = leer(validacion)
    need(ej.get("etiqueta") == ETIQUETA and val.get("comando") == "fam13-validar" and val.get("origen") == rel(d)
         and val.get("inventory_sha256") == sha_archivo(d / "ejecucion.json"), "VALIDACION_AJENA")
    det = COMPARAR_FN[ej["tarea"]](d, _contexto(d))
    motivos = []
    if not val.get("aceptada"):
        motivos.append("validación no aceptada")
    if not det["cumple"]:
        motivos.append("diferencias científicas, procedencia sin vínculo o bytes distintos de la huella aceptada")
    return {"comando": "fam13-comparar", "tarea": ej["tarea"], "operacion": OPERACION_DE[ej["tarea"]], "nueva": rel(d), "validacion": rel(validacion),
            "regla": "COMPARACION-FAM13-v1 (src/fam13.py)", **det, "estado": {"reproduccion": "aceptada" if not motivos else "no_aceptada", "motivos": motivos},
            "segundos": round(time.time() - t0, 3)}


# ================================================================================================ orden única, comprobación y receta
def _balance(comps: dict, vals: dict, ejs: dict) -> list:
    hu = fuentes()["huellas_aceptadas"]
    filas = []
    for k, (et, f, nombre) in PRODUCTOS.items():
        c = (comps.get(et) or {}).get("productos", {}).get(k) or {}
        ej, va = ejs.get(et) or {}, vals.get(et) or {}
        if et == "VALIDACIONES":
            rc_ = va.get("recuentos") or {}
            vv = rc_.get(rc_.get(k, ""), {}) if isinstance(rc_.get(k), str) else {}
            filas.append({"producto": k, "archivo": nombre, "sha256_aceptado": hu[k], "regenerado": "no (evalúa el modelo; fuera del alcance)",
                          "comprobado_por_huella": "sí: el archivo es el aceptado (%s…) y su prerregistro está ligado" % hu[k][:8] if c.get("autenticado_por_huella") else "no",
                          "recalculo_desde_valores_guardados": "%s/%s campos recalculados iguales a los guardados" % (vv.get("iguales"), vv.get("campos_recalculados")),
                          "pendiente": ["regenerar los valores del modelo (B_f0, cocientes D(h), momentos Pareto, s_P, r*, τ̃_d): requiere evaluar el modelo"]
                          + ([] if va.get("aceptada") else ["recálculo con diferencias o validación no aceptada"])})
            continue
        b = c.get("bytes") or {}
        fl = c.get("filas") or {}
        pend = []
        if not ej.get("exito"):
            pend.append("etapa sin éxito")
        if not va.get("aceptada"):
            pend.append("validación independiente no aceptada")
        if fl.get("cientificas_n"):
            pend.append("%d diferencias científicas" % fl["cientificas_n"])
        if c and not c.get("cumple"):
            pend.append("comparación no cumple")
        filas.append({"producto": k, "archivo": nombre, "sha256_aceptado": hu[k], "regenerado": "sí (%s/%s)" % (et.lower(), f) if (BASE / ej.get("_carpeta", "") / f).is_file() else "no",
                      "sha256_nuevo": b.get("nuevo_sha256"), "comprobado_por_huella": "sí (bytes = aceptado)" if b.get("igual_a_la_huella_aceptada") else "no",
                      "filas": {x: fl.get(x) for x in ("filas_nuevas", "filas_referencia", "filas_identicas", "cientificas_n")}, "pendiente": pend})
    return filas


def reproducir(salida: Path) -> dict:
    """fam13-reproducir: T1T2, T7, VALIDACIONES, MATRIZ_V4 y S1, cada una con su validación; después, las comparaciones y el balance."""
    t0 = time.time()
    salida = Path(salida)
    need(not salida.exists(), "LA_SALIDA_YA_EXISTE")
    malos = fuentes_alteradas("calculo")
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam13.json; no se calcula): %s" % malos[:5])
    salida.mkdir(parents=True)
    sal = _dentro(salida)
    pasos, ejs, vals, comps = [], {}, {}, {}
    for t in ETAPAS:
        d, v = sal / t.lower(), sal / (t.lower() + ".validacion.json")
        ej = correr(t, d)
        ej["_carpeta"] = rel(d)
        ejs[t] = ej
        r = validar(d)
        _escribir_x(v, r)
        vals[t] = r
        pasos.append({"etapa": t, "operacion": OPERACION_DE[t], "carpeta": rel(d), "exito": ej["exito"], "excepcion": (ej["excepcion"] or "")[-600:] or None,
                      "validacion": rel(v), "aceptada": r["aceptada"], "segundos": ej["segundos"],
                      "referencia_esperada_leida": ej["lecturas"]["referencia_esperada_leida"] or r["lecturas"]["referencia_esperada_leida"]})
    for t in ETAPAS:
        if ejs[t]["exito"]:
            c = comparar(sal / t.lower(), sal / (t.lower() + ".validacion.json"))
            _escribir_x(sal / (t.lower() + ".comparacion.json"), c)
            comps[t] = c
    balance = _balance(comps, vals, ejs)
    s1 = (comps.get("S1") or {}).get("integridad") or {}
    hist = all(ejs[t]["exito"] and vals[t]["aceptada"] and (comps.get(t) or {}).get("estado", {}).get("reproduccion") == "aceptada"
               for t in ETAPAS if t != "S1")
    return {"comando": "fam13-reproducir", "etiqueta": ETIQUETA, "salida": rel(sal), "pasos": pasos,
            "comparaciones": {t: {"archivo": rel(sal / (t.lower() + ".comparacion.json")), "estado": c["estado"]} for t, c in comps.items()},
            "productos_historicos": balance,
            "S1": {"conforme": s1.get("conforme"), "publicos": s1.get("publicos"), "mapa": s1.get("mapa"), "fe_de_erratas": s1.get("fe_de_erratas"),
                   "internos": s1.get("internos")},
            "U60": {"estado": "no localizado",
                    "limitacion_adoptada": ("L-F13-VALIDADOR-REM191 (decisión del autor, 2026-11-18): F13-HISTORICAS pasa de RD a VI; se conservan "
                                            "como evidencia los cinco productos regenerados y los dos del modelo comprobados sobre valores guardados"),
                    "comprobado_independientemente": {t: sorted(k for k, v in (vals[t].get("comprobaciones") or {}).items() if v) for t in ETAPAS if t != "S1"}},
            "F13_HISTORICAS_cumple": hist, "F13_S1_conforme": s1.get("conforme") is True, "cumple": hist and s1.get("conforme") is True,
            "segundos": round(time.time() - t0, 3), "entorno": entorno()}


def comprobar() -> dict:
    t0 = time.time()
    malos = fuentes_alteradas("todo")
    out = {"comando": "fam13-comprobar", "calculo": "ninguno", "fuentes": {"piezas": len(piezas()), "filas_fam01": len(_filas_fam01()), "alteradas": malos},
           "sustituciones": sustituciones_ok(),
           "codigo": {n: {"archivo_sha256": sha_archivo(BASE / n), "original_sha256": h, "corresponde": (BASE / n).is_file() and sha13((BASE / n).read_bytes()) == h}
                      for n, h in ORIGINAL.items()},
           "referencias": {x["archivo"]: sha_archivo(BASE / x["archivo"]) == x["sha256"] for x in piezas() if x["archivo"].startswith(PROHIBIDAS)},
           "S1": {k: v for k, v in integridad_s1().items() if k in ("publicos", "mapa", "conforme")},
           "u60": {"estado": "no localizado", "limitacion_adoptada": "L-F13-VALIDADOR-REM191 (2026-11-18; F13-HISTORICAS es VI)",
                   "candidatos_examinados": len(fuentes()["u60_busqueda"]),
                   "con_huella_aceptada_citada": [x["archivo"] for x in fuentes()["u60_busqueda"] if x.get("huellas_aceptadas_citadas")]},
           "receta": {"pasos": len(receta()["pasos"])}}
    out["cumple"] = (not malos and all(v is True for v in out["sustituciones"].values()) and all(x["corresponde"] for x in out["codigo"].values())
                     and all(out["referencias"].values()) and out["S1"]["conforme"])
    out["segundos"] = round(time.time() - t0, 3)
    return out


def receta() -> dict:
    py = "<python de .venv-fam01> -B -P -s -X utf8 reproducir.py"
    s = "salidas/fam13/<ejecucion>"
    pasos = [{"paso": "comprobar", "orden": py + " fam13-comprobar --salida " + s + "_comprobar.json", "calculo": "ninguno"},
             {"paso": "orden única", "orden": py + " fam13-reproducir --salida " + s,
              "calculo": ("T1T2 y T7 (U59), MATRIZ_V4 (A2 rem134): regeneración documental sin modelo; VALIDACIONES: autenticación y recálculo "
                          "aritmético desde valores guardados; S1: integridad por huella. Cada etapa con su validación independiente y, después, "
                          "las comparaciones y el balance por producto (resumen.json)")}]
    return {"comando": "fam13-receta", "estado": "lista (no ejecuta nada)", "pasos": pasos,
            "cobertura": {"operaciones": ["F13-HISTORICAS", "F13-S1"], "etapas": list(ETAPAS), "productos": list(PRODUCTOS)},
            "nota": ("sin entradas externas: todas las piezas están en el paquete (nucleo_s6/raiz, datos/fam13, referencias/fam01/originales para las "
                     "filas de unidad de T7); las referencias (referencias/fam13 y el T7_anexo de FAM10) solo se leen al comparar; los 19 internos "
                     "de S1 no están en el paquete ni se necesitan")}
