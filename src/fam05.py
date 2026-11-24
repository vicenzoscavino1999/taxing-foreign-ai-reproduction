"""FAM05 (lote 2: L1-ELAST y L1-LAMBDA): comprobación sin cálculo de entradas, referencias y cobertura; cálculo de una tarea o de una
unidad seleccionada por la ruta de tarea_lote.py del lote 2 con el núcleo C0; validación por validar_lote.py del lote 2; comparación con la
ejecución aceptada rem120 (productos del catálogo FAM05, libro rem121) y receta completa (sin ejecutarla).

Los nombres internos de las tareas siguen siendo L1-ELAST y L1-LAMBDA aunque son del LOTE 2; la procedencia «lote 1» solo se refiere a
las 70 filas históricas reutilizadas.

Operaciones del catálogo y unidades (no se confunden mallas, fronteras cubiertas, equivalencias y filas):
- F05-ELAST-C0 (RN): 393 mallas nuevas (clave «diseño|j|frontier_id» del manifiesto; 285 de una dimensión y 108 de dos) con 4.125 nodos;
  cubren 527 fronteras equivalentes, y otras 39 equivalencias ya aceptadas completan las 566 fronteras cubiertas del manifiesto. Cada
  nodo da una fila «point» y, si y solo si hay kink, sus filas left_limit/right_limit; cada fila lleva su topología del núcleo C0;
- F05-ELAST-HIST (VI): 6 mallas del suplemento (suplemento_topologia) con 70 filas numéricas ACEPTADAS del lote 1 (fuente autenticada por
  el manifiesto). No se recalculan: se copian sin cambios, reciben la topología del núcleo tras comprobar la compatibilidad del estencil y
  su procedencia se publica en suplemento_procedencia.jsonl (70 filas). Es una unidad única «SUPLEMENTO» (la fuente se autentica por su
  número total de filas: las 6 mallas van juntas). Con ellas son 399 mallas, 4.195 filas y 572 fronteras cubiertas;
- F05-LAMBDA (RN): 12 pares «conjunto|país» × (con, sin) = 24 filas. Estados nacionales por par según el anexo: 9 (CMP-E1, seis pares),
  1 (COL-E2-2023, cuatro pares) o 32 candidatos estrictos (PER-E0E3, dos pares; enumeración de su definición, 128 vértices de caja).
  Llamadas a macro.bridge: 4 por estado (dos variantes × dos testigos): 232 publicados + 256 estrictos = 488.

Piezas (copias exactas; ver fuentes_fam05.json): nucleo_s6/lote2 (tarea_lote.py, conexion_lambda.py, conexion_frontera.py, validar_lote.py),
nucleo_s6/c0/src/paper2b (núcleo C0, con el inventario completo de su instalación), datos/fam05 (manifiesto, anexo, paquete rem119, alcance y
la fuente aceptada del suplemento) y el contexto S6 de FAM01 (solo L1-LAMBDA: estados nacionales).

Adaptaciones de interfaz (no cambian fórmulas, mallas, tolerancias, presupuestos ni criterios):
- TAREA-AST-v2: tarea_lote.py tiene código de entrada al nivel superior; no se importa. Se compilan desde sus bytes exactos (árbol
  sintáctico, con sus números de línea) sus funciones dom_manifiesto, proveedor_real, estrictos, calc_lambda, fuente_suplemento, calc_elast,
  producto y tope, y las SENTENCIAS DE PRODUCCIÓN de cada tarea (L1-LAMBDA desde «est = estrictos(ctx, ml)» hasta su cierre, sin la rama
  hasta-seleccion; L1-ELAST desde «calc_elast(fr_)» hasta su cierre), en un espacio con los mismos nombres (CLX, CFR, MC, M, RUN, FR, Fr,
  SINT, SAL, out, H, R, man, T0, TOPE, o, ctx, ml, fr_). Solo se sustituye fin (FIN-v1): en lugar de escribir --resultado e invocar
  SystemExit, devuelve estado, motivo y campos al adaptador, que escribe resultado.json con el mismo esquema (out.update(estado, motivo,
  pared_s, **campos)).
- PUERTA-v1: la puerta de producción (alcance v3 + decisión humana nativa) no se ejecuta ni se reconstruye; los pilotos los autoriza el
  encargo de FAM05 y la receta completa queda para el Paso 3. modo = «produccion» es el que exige el validador; la etiqueta es NO OFICIAL.
- CONTEXTO-FAM05-v1 (solo L1-LAMBDA): en lugar de seleccion_paso4.configurar/contexto del despliegue operativo (f293a0a6…, run_class
  paso4_operativo_s6), fam01.Contexto con ese run_class y el núcleo C0 delante. De él la ruta usa solo ctx.inp.national. Antes de calcular
  se informa, sin evaluar λπ, que sus estados reproducen el anexo (huellas; en los estrictos, definición y enumeración).
- NUCLEO-C0-v1: el núcleo de trabajador y validador es nucleo_s6/c0 (src/paper2b de C0). aprobacion_alcance.identidad_instalacion, que
  ambos usan solo para la identidad de la instalación, se sirve con un módulo mínimo del mismo nombre (identidad_c0): comprueba que los
  archivos copiados son exactamente los del inventario declarado (sin __pycache__) y devuelve la identidad canónica de ese inventario
  (misma fórmula; d0bf5cd6…). Otro contenido ⇒ otra identidad ⇒ el validador da NUCLEO_DE_OTRA_IDENTIDAD (rc 4) y el cálculo no empieza.
- RUTA-SUPLEMENTO-v1: R (raíz de las rutas relativas del manifiesto en trabajador y validador) = datos/fam05/fuente_suplemento, donde la
  fuente aceptada está en la ruta que declara el manifiesto; se sigue autenticando por su sha256.
- SELECCION-UNIDAD-v1 y VALIDADOR-v2: una unidad (malla nueva, «SUPLEMENTO» o par) se calcula pasando a la ruta la parte del manifiesto de
  ESA unidad completa; validar_lote.py se ejecuta como guion desde sus bytes exactos con las sustituciones de SUSTITUCIONES_VALIDADOR (cada
  original aparece una sola vez): ubicación del núcleo y selección opcional (también en las mallas del suplemento). Sin selección se
  comporta como el original. Las comprobaciones del manifiesto completo que la selección omite (total de puntos) las hace fam05-comprobar.
- RELOJ-PILOTO-v1: reloj interno = tope de trabajo − holgura del conductor (2400 − 120 = 2280 s); el límite externo lo pone el supervisor.
"""
from __future__ import annotations

import ast
import builtins
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import sys
import time
import types
from collections import Counter
from fractions import Fraction as Fr
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RAIZ = BASE / "nucleo_s6" / "raiz"
INST = BASE / "nucleo_s6" / "instalacion"
C0 = BASE / "nucleo_s6" / "c0"
LOTE = BASE / "nucleo_s6" / "lote2"
DATOS = BASE / "datos" / "fam05"
FUENTE_SUP = DATOS / "fuente_suplemento"
REF = BASE / "referencias" / "fam05" / "rem120"
C0_IDENTIDAD = "d0bf5cd6e413ae4dcdd18eafb0bf7269cac22a487b4d46cb6b1737b5e5c971ae"
CODIGO = {"tarea_lote.py": "dca9d79b2d7c89bdd09e4e99293a158cb7fdc4cf8951df51561c68b019386456",
          "conexion_lambda.py": "9dbdc7322e303f11f4b33897dd11de3e7ce8327636637e75bc246222391138b3",
          "conexion_frontera.py": "4fb1915d7cf7ca39bf9385f975665a75b32717558096870d7d9213d151be2527",
          "validar_lote.py": "d95e2beb0c0f67a96984d4346fe1c77e5b44539eb97769ba3f09ecbb67ea4f19"}
MANIFIESTO = ("LOTE2_MANIFIESTO.json", "b1cf8af5eab8aa22c53ec279bd5660dbf57847b6be8f874c56af7d71f9cd4bab")
ANEXO = ("COBERTURA_NACIONAL_LOTE2.json", "5bea51535665167e1d22ecf0c8c2a54289233a7871faeae13dacc31a13a1600c")
PAQUETE = ("PAQUETE_LOTE1.json", "265c29f43ac4ad9c16dfe70da7c830cd027e0bab6bd9dffa561536b114981f32")
ALCANCE = ("alcance_lote2.json", "ca5afe75c034aa13abe7e616f559a8e61061e0c4501677e15887bd6b0d6d9a2e")
DESPLIEGUE_SHA256 = "f293a0a62d2cb6bf3517e72a0bfc589ee703685d4434c2cdae4b4cd1b5085d6c"   # despliegue operativo de la receta rem119 (no se copia)
TAREAS = ("L1-ELAST", "L1-LAMBDA")
PRODUCTOS = {"L1-ELAST": ("frontier_result.jsonl", "suplemento_procedencia.jsonl"), "L1-LAMBDA": ("lambda_envolvente.jsonl",)}
OPERACIONES = {"F05-ELAST-C0": "L1-ELAST (393 mallas nuevas)", "F05-ELAST-HIST": "L1-ELAST (SUPLEMENTO: 6 mallas, 70 filas históricas)",
               "F05-LAMBDA": "L1-LAMBDA (12 pares)"}
SUPLEMENTO = "SUPLEMENTO"
TOPE_TRABAJO, HOLGURA, TOPE_VALIDACION = 2400.0, 120.0, 300.0     # conductor (estado_lote de rem120: parametros)
RUN_CLASS = "paso4_operativo_s6"
ETIQUETA = "REPRODUCCION LIMPIA FAM05 NO OFICIAL"
FUNCIONES_TAREA = ("dom_manifiesto", "proveedor_real", "estrictos", "calc_lambda", "fuente_suplemento", "calc_elast", "producto", "tope")
CLAVES_ESTRUCTURALES = ("a", "beta_tilde", "c_legal", "eta_d", "eta_f", "gamma", "kappa_tilde", "phi", "rho", "t", "u_theta", "z_cost", "z_m")
ADAPTACIONES = ("TAREA-AST-v2", "FIN-v1", "PUERTA-v1", "CONTEXTO-FAM05-v1 (solo L1-LAMBDA)", "NUCLEO-C0-v1", "RUTA-SUPLEMENTO-v1",
                "SELECCION-UNIDAD-v1", "VALIDADOR-v2", "RELOJ-PILOTO-v1")
SUSTITUCIONES_VALIDADOR = (
    ("NUCLEO-C0-v1", 'NUCLEO = Path(__file__).resolve().parents[2] / "paso4_raices_impacto_desde_rem116/candidato_c0/instalacion"',
     'NUCLEO = Path(__file__).resolve().parents[1] / "c0"'),
    ("SEL-ARGUMENTO", 'COB = Path(sys.argv[5]) if len(sys.argv) > 5 else None',
     'COB = Path(sys.argv[5]) if len(sys.argv) > 5 else None\nSEL = json.loads(sys.argv[6]) if len(sys.argv) > 6 else None'),
    ("SEL-LAMBDA", '    esperado = {(s, v) for s in ml for v in ("con", "sin")}',
     '    esperado = {(s, v) for s in ml if SEL is None or s in SEL["conjuntos"] for v in ("con", "sin")}'),
    ("SEL-ELAST", '        ids[v["frontier_id"]] = (key.split("|")[1], v)',
     '        if SEL is None or v["frontier_id"] in SEL["fronteras"]:\n            ids[v["frontier_id"]] = (key.split("|")[1], v)'),
    ("SEL-ELAST-TOTAL", '    if "puntos_totales_frontier_n4" in man["L1-ELAST"] and', '    if SEL is None and "puntos_totales_frontier_n4" in man["L1-ELAST"] and'),
    ("SEL-SUPLEMENTO", '    sup_ids = {v["frontier_id"]: (k.split("|")[0], v) for k, v in fr_man.items() if v.get("suplemento_topologia")}',
     '    sup_ids = {v["frontier_id"]: (k.split("|")[0], v) for k, v in fr_man.items() if v.get("suplemento_topologia")\n'
     '               and (SEL is None or v["frontier_id"] in SEL["fronteras"])}'))


class Fam05Error(RuntimeError):
    pass


class FinTarea(Exception):
    """FIN-v1: cierre de tarea_lote (estado, motivo, campos) sin escribir --resultado ni salir del proceso."""

    def __init__(self, estado, motivo=None, **k):
        super().__init__(estado, motivo)
        self.estado, self.motivo, self.campos = estado, motivo, k


def need(t, codigo):
    if not t:
        raise Fam05Error(codigo)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_archivo(p: Path):
    return sha(Path(p).read_bytes()) if Path(p).is_file() else None


def leer(p: Path):
    return json.loads(Path(p).read_bytes())


def leer_jsonl(p: Path) -> list:
    return [json.loads(x) for x in Path(p).read_text(encoding="utf-8").splitlines() if x.strip()]


def rel(p: Path) -> str:
    p = Path(p).resolve()
    return p.relative_to(BASE.resolve()).as_posix() if p.is_relative_to(BASE.resolve()) else p.name


def cargar(nombre: str, ruta: Path):
    if nombre not in sys.modules:
        sp = importlib.util.spec_from_file_location(nombre, ruta)
        m = importlib.util.module_from_spec(sp)
        sys.modules[nombre] = m
        sp.loader.exec_module(m)
    return sys.modules[nombre]


def F1():
    return cargar("fam01", BASE / "src" / "fam01.py")


def fuentes() -> dict:
    return leer(BASE / "fuentes_fam05.json")


def fuentes_alteradas(sin_referencias: bool = False) -> list:
    """Piezas ausentes o con otra huella. sin_referencias: solo entradas y código (lo que usa el cálculo, que no lee referencias)."""
    return [x["archivo"] for x in fuentes()["archivos"]
            if not (sin_referencias and x["papel"].startswith("referencia")) and sha_archivo(BASE / x["archivo"]) != x["sha256"]]


def manifiesto() -> tuple:
    raw = (DATOS / MANIFIESTO[0]).read_bytes()
    need(sha(raw) == MANIFIESTO[1], "MANIFIESTO_DISTINTO")
    man = json.loads(raw)
    need(not str(man.get("kind", "")).endswith("-SINTETICO"), "MANIFIESTO_SINTETICO")
    return raw, man


def anexo() -> dict:
    raw = (DATOS / ANEXO[0]).read_bytes()
    need(sha(raw) == ANEXO[1], "ANEXO_DE_COBERTURA_DISTINTO")
    return json.loads(raw)


# ================================================================================================ núcleo C0 y módulos
def identidad_inventario(inv: dict) -> str:
    """Fórmula de aprobacion_alcance.identidad_instalacion sobre un inventario {ruta: {sha256, bytes}}."""
    return sha(json.dumps(dict(sorted(inv.items())), sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def identidad_c0(raiz=None) -> str:
    """NUCLEO-C0-v1: identidad canónica del inventario declarado de C0 si los archivos presentes en `raiz` (sin __pycache__) son
    exactamente los copiados del inventario y con sus bytes; si no, una identidad que no coincide con ninguna."""
    raiz = Path(raiz or C0)
    inv = fuentes()["nucleo_c0"]["inventario"]
    copiados = {k for k in inv if k.startswith("src/paper2b/")}
    presentes = {p.relative_to(raiz).as_posix() for p in raiz.rglob("*") if p.is_file() and "__pycache__" not in p.parts} if raiz.is_dir() else set()
    if presentes != copiados:
        return "INVENTARIO_NO_CORRESPONDE (faltan %d, ajenos %d)" % (len(copiados - presentes), len(presentes - copiados))
    for k in sorted(copiados):
        b = (raiz / k).read_bytes()
        if sha(b) != inv[k]["sha256"] or len(b) != inv[k]["bytes"]:
            return "INVENTARIO_NO_CORRESPONDE (%s)" % k
    return identidad_inventario({k: {"sha256": v["sha256"], "bytes": v["bytes"]} for k, v in inv.items()})


def modulo_identidad():
    """NUCLEO-C0-v1: módulo mínimo «aprobacion_alcance» (solo identidad_instalacion) para trabajador y validador."""
    m = types.ModuleType("aprobacion_alcance")
    m.__doc__ = "FAM05 NUCLEO-C0-v1: solo identidad_instalacion, desde el inventario declarado de C0 (src/fam05.py)"
    m.__file__ = str(BASE / "src" / "fam05.py")
    m.identidad_instalacion = identidad_c0
    sys.modules["aprobacion_alcance"] = m
    return m


def preparar():
    """sys.path: núcleo C0 delante (el que exigen trabajador y validador del lote 2) y la raíz copiada después (contexto S6)."""
    for p in (str(RAIZ / "src"), str(RAIZ), str(INST / "src"), str(C0 / "src")):
        while p in sys.path:
            sys.path.remove(p)
    sys.path.insert(0, str(RAIZ))
    sys.path.insert(0, str(C0 / "src"))
    import paper2b
    need(Path(paper2b.__file__).resolve().parent == (C0 / "src" / "paper2b").resolve(), "NUCLEO_NO_ES_C0:" + paper2b.__file__)
    modulo_identidad()


def pila():
    preparar()
    for n, h in CODIGO.items():
        need(sha_archivo(LOTE / n) == h, "CODIGO_DEL_LOTE_DISTINTO: %s" % n)
    CLX = cargar("conexion_lambda", LOTE / "conexion_lambda.py")
    CFR = cargar("conexion_frontera", LOTE / "conexion_frontera.py")
    for nom, m in (("conexion_lambda", CLX), ("conexion_frontera", CFR)):
        need(Path(m.__file__).resolve() == (LOTE / (nom + ".py")).resolve(), "CONEXION_DE_OTRO_LOTE: %s" % m.__file__)
    from paper2b import frontier as FR
    from paper2b import macro as MC
    from paper2b import model as M
    from paper2b import run as RUN
    return {"CLX": CLX, "CFR": CFR, "MC": MC, "M": M, "RUN": RUN, "FR": FR}


def ramas_tarea() -> tuple:
    """TAREA-AST-v2: (árbol, funciones, sentencias de producción de L1-LAMBDA y de L1-ELAST) desde los bytes exactos de tarea_lote.py."""
    p = LOTE / "tarea_lote.py"
    src = p.read_bytes()
    need(sha(src) == CODIGO["tarea_lote.py"], "TAREA_LOTE_DISTINTA")
    arbol = ast.parse(src.decode("utf-8"), filename=str(p))
    fn = [n for n in arbol.body if isinstance(n, ast.FunctionDef) and n.name in FUNCIONES_TAREA]
    need(sorted(n.name for n in fn) == sorted(FUNCIONES_TAREA), "FUNCIONES_DE_TAREA_LOTE_AUSENTES")

    def rama(t):
        r = [n for n in arbol.body if isinstance(n, ast.If) and ast.unparse(n.test) == "tarea == '%s'" % t]
        need(len(r) == 1, "RAMA_DE_TAREA_AUSENTE: %s" % t)
        return r[0].body
    bl = rama("L1-LAMBDA")
    need(ast.unparse(bl[0]) == "ml = man['L1-LAMBDA']" and isinstance(bl[1], ast.If)
         and ast.unparse(bl[1].test) == "modo == 'hasta-seleccion' or modo == 'produccion'", "RAMA_LAMBDA_INESPERADA")
    dentro = bl[1].body
    i = next((k for k, n in enumerate(dentro) if ast.unparse(n) == "est = estrictos(ctx, ml)"), None)
    need(i is not None and ast.unparse(dentro[i - 1]) == "ctx = SP.contexto()", "RAMA_LAMBDA_SIN_ESTRICTOS")
    saltadas = [n for n in dentro[i:] if isinstance(n, ast.If) and ast.unparse(n.test) == "modo == 'hasta-seleccion'"]
    lam = [n for n in dentro[i:] if n not in saltadas] + bl[2:]
    need(len(saltadas) == 1 and ast.unparse(lam[-1]).startswith("fin("), "RAMA_LAMBDA_SIN_CIERRE")
    be = rama("L1-ELAST")
    need(ast.unparse(be[0]) == "fr_ = man['L1-ELAST']['fronteras']" and isinstance(be[1], ast.If) and ast.unparse(be[1].test) == "modo == 'hasta-seleccion'"
         and ast.unparse(be[2]) == "filas, procedencia, bloqueadas, fuente = calc_elast(fr_)" and ast.unparse(be[-1]).startswith("fin("), "RAMA_ELAST_INESPERADA")
    ela = be[2:]
    return p, fn, {"L1-LAMBDA": lam, "L1-ELAST": ela}


def espacio(mods: dict, SAL: Path, out: dict, man: dict, T0: float, TOPE: float) -> tuple:
    """Funciones de tarea_lote.py compiladas en su espacio (TAREA-AST-v2) y las sentencias de producción compiladas por tarea."""
    p, fn, ramas = ramas_tarea()

    def fin(estado, motivo=None, **k):              # FIN-v1
        raise FinTarea(estado, motivo, **k)
    ns = dict(mods, Fr=Fr, SINT=False, SAL=SAL, out=out, H=sha, json=json, Path=Path, time=time, sys=sys, R=FUENTE_SUP, man=man, T0=T0,
              TOPE=TOPE, fin=fin, o={"--instalacion": str(C0)}, __builtins__=builtins)
    exec(compile(ast.Module(body=fn, type_ignores=[]), str(p), "exec"), ns)
    cod = {t: compile(ast.Module(body=b, type_ignores=[]), str(p), "exec") for t, b in ramas.items()}
    return ns, cod


def contexto():
    preparar()
    f = F1()
    return f.Contexto(dict(f.parametros(), etiqueta=ETIQUETA, run_class=RUN_CLASS), raiz=RAIZ, inst=INST)


# ================================================================================================ unidades y pilotos
def suplemento_ids(man: dict) -> list:
    return [v["frontier_id"] for v in man["L1-ELAST"]["fronteras"].values() if v.get("suplemento_topologia")]


def unidades(man: dict, an: dict | None = None) -> dict:
    an = an or anexo()
    fr_ = man["L1-ELAST"]["fronteras"]
    sup = [(k, v) for k, v in fr_.items() if v.get("suplemento_topologia")]
    el = [{"unidad": v["frontier_id"], "operacion": "F05-ELAST-C0", "clave": k, "dimension_malla": v["dimension_malla"], "nodos": v["puntos_frontier_n4"]}
          for k, v in fr_.items() if not v.get("suplemento_topologia")]
    el.append({"unidad": SUPLEMENTO, "operacion": "F05-ELAST-HIST", "mallas": [v["frontier_id"] for _, v in sup], "claves": [k for k, _ in sup],
               "nodos": sum(v["puntos_frontier_n4"] for _, v in sup), "filas_historicas": man["L1-ELAST"]["suplemento_fuente"]["filas"]})
    la = [{"unidad": s, "operacion": "F05-LAMBDA", "conjunto": v.get("conjunto", s), "pais": v["pais"], "variantes": sorted(v["variantes"]),
           "dominio_nacional": v.get("dominio_nacional", "publicado"), "estados_nacionales": an["conjuntos"][s]["n_estados"]} for s, v in man["L1-LAMBDA"].items()]
    return {"L1-ELAST": el, "L1-LAMBDA": la}


def seleccion(man: dict, tarea: str, unidad: str | None):
    """Filtro de UNIDADES del lote (nunca del soporte de la unidad). None = tarea completa."""
    if unidad is None:
        return None
    need(tarea in TAREAS, "TAREA_NO_ADMITIDA: %s" % tarea)
    if tarea == "L1-ELAST":
        sup = suplemento_ids(man)
        if unidad == SUPLEMENTO:
            return {"fronteras": sup}
        need(unidad not in sup, "MALLA_DEL_SUPLEMENTO: las 6 mallas históricas forman una sola unidad (--unidad %s)" % SUPLEMENTO)
        need(unidad in {v["frontier_id"] for v in man["L1-ELAST"]["fronteras"].values()}, "FRONTERA_FUERA_DEL_MANIFIESTO: %s" % unidad)
        return {"fronteras": [unidad]}
    need(unidad in man["L1-LAMBDA"], "PAR_FUERA_DEL_MANIFIESTO: %s" % unidad)
    return {"conjuntos": [unidad]}


def regla_pilotos(man: dict) -> dict:
    an = anexo()
    fr_ = man["L1-ELAST"]["fronteras"]
    ke = next(k for k, v in fr_.items() if v["dimension_malla"] == 2 and not v.get("suplemento_topologia"))
    ml = man["L1-LAMBDA"]
    sn = next(s for s, v in ml.items() if v.get("dominio_nacional") != "estricto")
    se = next(s for s, v in ml.items() if v.get("dominio_nacional") == "estricto" and v.get("conjunto", s).startswith("PER-E0E3"))
    sup = [v for v in fr_.values() if v.get("suplemento_topologia")]
    return {"regla": ("fijados por identificador desde el MANIFIESTO (entrada), antes de calcular y sin mirar resultados: ELAST, la primera "
                      "malla nueva bidimensional (dimension_malla = 2, sin suplemento_topologia) en el orden del manifiesto; LAMBDA no estricto, "
                      "el primer par de dominio nacional publicado; LAMBDA estricto, el primer par PER-E0E3 de dominio estricto. Además, la "
                      "unidad SUPLEMENTO (las 6 mallas históricas) como reutilización y verificación, sin recalcular valores numéricos"),
            "pilotos": [{"tarea": "L1-ELAST", "operacion": "F05-ELAST-C0", "unidad": fr_[ke]["frontier_id"], "clave": ke,
                         "cobertura": "malla nueva completa: %d nodos (frontier_n = 4) con sus filas laterales si hay kink y su topología"
                         % fr_[ke]["puntos_frontier_n4"]},
                        {"tarea": "L1-LAMBDA", "operacion": "F05-LAMBDA", "unidad": sn, "pais": ml[sn]["pais"],
                         "cobertura": ("par completo de dominio publicado: variantes con y sin, testigos de máximo y mínimo y los %d estados "
                                       "nacionales del anexo" % an["conjuntos"][sn]["n_estados"])},
                        {"tarea": "L1-LAMBDA", "operacion": "F05-LAMBDA", "unidad": se, "pais": ml[se]["pais"],
                         "cobertura": ("par completo de dominio estricto: variantes con y sin, testigos de máximo y mínimo y los %d candidatos de "
                                       "la enumeración de su definición (%s…)" % (an["conjuntos"][se]["n_estados"], ml[se]["definicion_sha256"][:8]))}],
            "verificacion_historica": {"tarea": "L1-ELAST", "operacion": "F05-ELAST-HIST", "unidad": SUPLEMENTO, "mallas": [v["frontier_id"] for v in sup],
                                       "cobertura": ("las %d filas aceptadas del lote 1 copiadas sin cambios, con la topología del núcleo C0 y la "
                                                     "compatibilidad del estencil; procedencia de %d filas") % ((man["L1-ELAST"]["suplemento_fuente"]["filas"],) * 2)}}


def fijar_pilotos(man: dict) -> dict:
    doc = regla_pilotos(man)
    raw = (json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True) + "\n").encode("utf-8")
    p = DATOS / "pilotos.json"
    if p.exists():
        need(p.read_bytes() == raw, "PILOTOS_FIJADOS_DISTINTOS_DE_LA_REGLA")
    else:
        p.write_bytes(raw)
    return doc


def listar() -> dict:
    raw, man = manifiesto()
    u = unidades(man)
    return {"comando": "fam05-listar", "calculo": "ninguno", "manifiesto_sha256": sha(raw), "operaciones": OPERACIONES,
            "recuento": {"L1-ELAST": {"mallas_nuevas": sum(1 for x in u["L1-ELAST"] if x["unidad"] != SUPLEMENTO), "suplemento": 1},
                         "L1-LAMBDA": {"pares": len(u["L1-LAMBDA"])}},
            "unidades": u, "pilotos": fijar_pilotos(man)}


# ================================================================================================ comprobación (sin cálculo científico)
def cobertura_manifiesto(man: dict, an: dict) -> dict:
    """Mallas, fronteras cubiertas, equivalencias y filas del manifiesto; estados del anexo y presupuesto de bridge (sin λπ ni mallas
    evaluadas: solo la malla de nodos y la enumeración estructural de los dominios estrictos, como el validador)."""
    preparar()
    CLX = cargar("conexion_lambda", LOTE / "conexion_lambda.py")
    from paper2b import macro as MC
    from paper2b.run import RunConfig
    from paper2b.supremum import axes, nodes
    n = RunConfig().frontier_n
    mot = []
    el = man["L1-ELAST"]
    total, nuevas, sup = 0, Counter(), Counter()
    for k, v in el["fronteras"].items():
        j = k.split("|")[1]
        (dl, dh), (fl, fh) = axes(j, float(v["dominio_tau"]["tau_d_upper"]), float(v["dominio_tau"]["tau_f_upper"]))
        m = len(nodes(dl, dh, n) if dh > dl else [dl]) * len(nodes(fl, fh, n) if fh > fl else [fl])
        total += m
        (sup if v.get("suplemento_topologia") else nuevas).update(mallas=1, puntos=m, **{"dim%d" % v["dimension_malla"]: 1})
        if m != v["puntos_frontier_n4"]:
            mot.append("MALLA_DISTINTA_DEL_MANIFIESTO: %s" % v["frontier_id"])
        if [p for p in CLAVES_ESTRUCTURALES if p not in v["clave_estructural"]] or not v["dominio_tau"]:
            mot.append("CLAVE_O_DOMINIO_INCOMPLETO: %s" % k)
        if not v.get("suplemento_topologia"):
            nuevas.update(equivalentes=len(v.get("frontier_ids_equivalentes") or []))
    por_clave = Counter("|".join(k.split("|")[:2]) for k in el["fronteras"])
    cubiertas = nuevas["equivalentes"] + len(el["equivalencias_aceptadas"])
    if total != el["puntos_totales_frontier_n4"]:
        mot.append("TOTAL_DE_PUNTOS_DISTINTO_DE_LA_MALLA")
    if (nuevas["mallas"], nuevas["puntos"]) != (el["mallas_remanentes"], el["puntos_remanentes"]):
        mot.append("MALLAS_NUEVAS_DISTINTAS_DEL_MANIFIESTO")
    if cubiertas != el["frontier_ids_cubiertos"]:
        mot.append("FRONTERAS_CUBIERTAS_DISTINTAS")
    if el.get("topologia_requerida") is not True:
        mot.append("TOPOLOGIA_NO_REQUERIDA")
    # fuente del suplemento (entrada): 70 filas de las 6 mallas con sus nodos (sin recalcular)
    sf = el["suplemento_fuente"]
    fs = FUENTE_SUP / sf["ruta"]
    ids = set(suplemento_ids(man))
    filas_s = [y for y in leer_jsonl(fs) if y.get("frontier_id") in ids] if sha_archivo(fs) == sf["sha256"] else []
    nodos_s = Counter(y["frontier_id"] for y in filas_s if y["side"] == "point")
    if len(filas_s) != sf["filas"] or dict(nodos_s) != {v["frontier_id"]: v["puntos_frontier_n4"] for v in el["fronteras"].values() if v.get("suplemento_topologia")}:
        mot.append("FUENTE_DEL_SUPLEMENTO_DISTINTA")
    ml = man["L1-LAMBDA"]
    if set(an["conjuntos"]) != set(ml):
        mot.append("ANEXO_CON_OTROS_PARES")
    estados, estrictos, bridge = {}, {}, {}
    for s, c in an["conjuntos"].items():
        v = ml.get(s, {})
        hs = [e["shares_sha256"] for e in c["estados"]]
        estados[s] = len(hs)
        bridge[s] = 4 * len(hs)
        if not (c.get("independiente_de_omega") is True and c["n_estados"] == len(hs) and len(set(hs)) == len(hs)
                and [e["orden"] for e in c["estados"]] == list(range(len(hs)))):
            mot.append("ANEXO_INCONSISTENTE: %s" % s)
        if sorted(v.get("variantes", {})) != ["con", "sin"] or c.get("conjunto") != v.get("conjunto", s) or c.get("pais") != v.get("pais"):
            mot.append("PAR_INCOMPLETO_O_DISTINTO: %s" % s)
        if v.get("llamadas_bridge_al_calcular") not in (None, 4 * len(hs)):
            mot.append("PRESUPUESTO_DE_BRIDGE_DISTINTO: %s" % s)
        if (v.get("dominio_nacional") == "estricto") != (c.get("tipo_dominio") == "estricto"):
            mot.append("TIPO_DE_DOMINIO_DISTINTO: %s" % s)
        if c.get("tipo_dominio") == "estricto":
            cand, nv, signo = CLX.vertices_estrictos(MC, c["definicion"])
            estrictos[s] = {"candidatos": len(cand), "vertices_caja": nv, "signo_no_negativo": signo,
                            "definicion_sha256": CLX.definicion_sha256(c["definicion"]),
                            "reproducible": ([x["huella"] for x in cand] == hs and nv == c.get("vertices_caja") and signo is True
                                             and c.get("signo_no_negativo") is True and CLX.definicion_sha256(c["definicion"]) == c.get("definicion_sha256")
                                             == v.get("definicion_sha256"))}
            if not estrictos[s]["reproducible"]:
                mot.append("ANEXO_ESTRICTO_NO_REPRODUCIBLE: %s" % s)
    pres = man.get("presupuesto_llamadas_lambda") or {}
    publ = sum(b for s, b in bridge.items() if s not in estrictos)
    estr = sum(b for s, b in bridge.items() if s in estrictos)
    if (publ, estr) != (pres.get("publicados"), pres.get("estrictos")):
        mot.append("PRESUPUESTO_TOTAL_DE_BRIDGE_DISTINTO")
    return {"L1-ELAST": {"mallas": len(el["fronteras"]), "filas_point": total, "frontier_n": n,
                         "mallas_nuevas": {"mallas": nuevas["mallas"], "nodos": nuevas["puntos"], "una_dimension": nuevas["dim1"], "dos_dimensiones": nuevas["dim2"],
                                           "fronteras_equivalentes": nuevas["equivalentes"]},
                         "equivalencias_ya_aceptadas": len(el["equivalencias_aceptadas"]), "fronteras_cubiertas": cubiertas,
                         "suplemento": {"mallas": sup["mallas"], "nodos": sup["puntos"], "una_dimension": sup["dim1"], "dos_dimensiones": sup["dim2"],
                                        "filas_de_la_fuente": len(filas_s), "fuente_sha256": sf["sha256"]},
                         "fronteras_cubiertas_con_suplemento": cubiertas + sup["mallas"], "mallas_por_diseno_j": dict(sorted(por_clave.items()))},
            "L1-LAMBDA": {"pares": len(ml), "filas_esperadas": 2 * len(ml), "estados_nacionales_del_anexo": estados, "estrictos": estrictos,
                          "llamadas_bridge_esperadas": {"publicados": publ, "estrictos": estr, "total": publ + estr},
                          "presupuesto_del_manifiesto": pres},
            "cumple": not mot, "motivos": mot}


# referencia correcta de cada producto: (operación, id del producto en el catálogo). frontier_result.jsonl del lote 2 (P_elast_lote2) no
# se confunde con el del lote 1 (P_elast_lote1), que es la FUENTE del suplemento (entrada), no una referencia.
REF_CATALOGO = {"frontier_result.jsonl": ("F05-ELAST-C0", "P_elast_lote2"),
                "suplemento_procedencia.jsonl": ("F05-ELAST-HIST", "L_rem121:suplemento_procedencia.jsonl"),
                "lambda_envolvente.jsonl": ("F05-LAMBDA", "P_lambda_lote2")}
FUENTE_CATALOGO = ("F05-ELAST-HIST", "P_elast_lote1")


def catalogo_sha(op: str, ident: str) -> str | None:
    o = next((o for o in leer(BASE / "catalogo.json")["operaciones"] if o["clave"] == op), None)
    return next((p["sha256_aceptado"] for p in (o or {}).get("productos", []) if p["id"] == ident), None)


def ref_aceptada(n: str) -> str | None:
    """Huella aceptada del catálogo para el producto `n` del lote 2."""
    return catalogo_sha(*REF_CATALOGO[n])


def cobertura_referencias(man: dict, an: dict) -> dict:
    mot, r = [], {}
    for t, prods in PRODUCTOS.items():
        res = leer(REF / t / "resultado.json")
        val = json.loads((REF / t / "validacion_stdout.txt").read_text(encoding="utf-8"))
        if res.get("estado") != "completa" or res.get("manifiesto_sha256") != MANIFIESTO[1] or val.get("dictamen") != "completa_validada" or val.get("n_fallos") != 0:
            mot.append("REFERENCIA_NO_ACEPTADA: %s" % t)
        if res["codigo_sha256"] != {k: CODIGO[k] for k in ("tarea_lote.py", "conexion_lambda.py", "conexion_frontera.py")}:
            mot.append("REFERENCIA_DE_OTRO_CODIGO: %s" % t)
        decl = {p["archivo"]: p for p in res["productos"]}
        for n in prods:
            f = REF / t / "salida" / n
            h = sha_archivo(f)
            filas = leer_jsonl(f) if h else []
            if h is None or h != ref_aceptada(n) or decl.get(n, {}).get("filas") != len(filas):
                mot.append("REFERENCIA_ALTERADA_O_AJENA: %s" % n)
            r[n] = {"filas": len(filas), "sha256": h}
    fr = leer_jsonl(REF / "L1-ELAST/salida/frontier_result.jsonl")
    sup = set(suplemento_ids(man))
    por_f = Counter(x["frontier_id"] for x in fr if x["side"] == "point")
    if dict(por_f) != {v["frontier_id"]: v["puntos_frontier_n4"] for v in man["L1-ELAST"]["fronteras"].values()}:
        mot.append("REFERENCIA_ELAST_CON_OTROS_NODOS")
    r["frontier_result.jsonl"].update(lados=dict(Counter(x["side"] for x in fr)), kinks=sum(1 for x in fr if x["kink_adjacent"] is True),
                                      motivos=dict(Counter(str(x["reason_code"]) for x in fr)), auditoria=dict(Counter(x["audit_status"] for x in fr)),
                                      filas_nuevas=sum(1 for x in fr if x["frontier_id"] not in sup), filas_del_suplemento=sum(1 for x in fr if x["frontier_id"] in sup),
                                      con_topologia=sum(1 for x in fr if isinstance(x.get("topology"), str) and x["topology"]))
    pr = leer_jsonl(REF / "L1-ELAST/salida/suplemento_procedencia.jsonl")
    sf = man["L1-ELAST"]["suplemento_fuente"]
    if not all(q.get("frontier_result_sha256") == r["frontier_result.jsonl"]["sha256"] and q.get("instalacion_identidad") == C0_IDENTIDAD
               and q.get("fuente_sha256") == sf["sha256"] and q.get("origen_numerico") == "LOTE1_ACEPTADO" for q in pr):
        mot.append("REFERENCIA_PROCEDENCIA_SIN_VINCULO")
    r["suplemento_procedencia.jsonl"].update(vinculo_frontier_result=sorted({q.get("frontier_result_sha256") for q in pr}),
                                             instalacion_identidad=sorted({q.get("instalacion_identidad") for q in pr}))
    la = leer_jsonl(REF / "L1-LAMBDA/salida/lambda_envolvente.jsonl")
    if sorted((x["conjunto"], x["variante"]) for x in la) != sorted((s, v) for s in man["L1-LAMBDA"] for v in ("con", "sin")):
        mot.append("REFERENCIA_LAMBDA_CON_OTRAS_FILAS")
    ev = {x["conjunto"]: sorted({len(x["evidencia_por_estado"][e]) for e in ("max", "min")}) for x in la}
    if any(ev[s] != [an["conjuntos"][s]["n_estados"]] for s in ev):
        mot.append("REFERENCIA_LAMBDA_CON_OTRA_COBERTURA_NACIONAL")
    r["lambda_envolvente.jsonl"].update(estados=dict(Counter(x["estado"] for x in la)), evidencia_por_par=ev,
                                        llamadas_bridge=sum(x["llamadas_bridge"] for x in la))
    return {"productos": r, "cumple": not mot, "motivos": mot}


def comprobar() -> dict:
    """fam05-comprobar: SIN CÁLCULO CIENTÍFICO (sin contexto, λπ ni filas de malla; la revalidación de las referencias aplica el
    validador a bytes guardados, que reevalúa topologías como en la validación histórica)."""
    r = {"comando": "fam05-comprobar", "calculo": "ninguno"}
    malos = fuentes_alteradas()
    fu = fuentes()
    r["fuentes"] = {"archivos": len(fu["archivos"]), "ausentes_o_distintos": malos[:20]}
    raw, man = manifiesto()
    an, al, pq = anexo(), leer(DATOS / ALCANCE[0]), leer(DATOS / PAQUETE[0])
    cod = {n: sha_archivo(LOTE / n) for n in CODIGO}
    pz, nec = pq["piezas"], pq["alcance_necesario"]
    d7 = F1().parametros()
    d7dir = RAIZ / d7["d7_dir"] / "versions" / d7["d7_tree"]
    r["procedencia"] = {
        "codigo_igual_al_alcance": {k: cod[k] for k in ("tarea_lote.py", "conexion_lambda.py", "conexion_frontera.py")} == al["entradas"]["codigo_lote"],
        "validador_igual_al_alcance": cod["validar_lote.py"] == al["entradas"]["validador_lote"],
        "manifiesto_igual_al_alcance": sha(raw) == al["lote_manifiesto_sha256"] == al["entradas"]["lote_manifiesto"],
        "anexo_igual_al_alcance": ANEXO[1] == al["entradas"]["cobertura_nacional"] == nec["cobertura_nacional"]["LOTE2"],
        "identidad_c0_igual_al_alcance": al["instalacion_identidad"] == C0_IDENTIDAD == pq["nucleo"]["identidad"] == nec["instalacion_identidad"],
        "d7_igual_al_alcance": {n: sha_archivo(d7dir / n) for n in al["entradas"]["d7_sha256"]} == al["entradas"]["d7_sha256"],
        "despliegue_del_alcance": al.get("despliegue_sha256") == DESPLIEGUE_SHA256,
        "piezas_iguales_al_paquete": all(pz[n]["sha256"] == cod[n] for n in CODIGO) and pz[MANIFIESTO[0]]["sha256"] == sha(raw)
                                     and pz[ANEXO[0]]["sha256"] == ANEXO[1],
        "suplemento_igual_al_paquete": (pq["suplemento"]["sha256"], pq["suplemento"]["filas"], pq["suplemento"]["fuente"])
                                       == (man["L1-ELAST"]["suplemento_fuente"]["sha256"], man["L1-ELAST"]["suplemento_fuente"]["filas"],
                                           man["L1-ELAST"]["suplemento_fuente"]["ruta"]),
        "anexo_ligado_al_manifiesto": an.get("kind") == "cobertura-nacional-lote1" and an.get("manifiesto_sha256") == sha(raw),
        "anexo_sin_evaluar_lambda": all(an.get(k) == {"macro.bridge": 0, "macro.strict_vertices": 0}
                                        for k in ("llamadas_durante_preparacion", "llamadas_durante_la_derivacion")),
        "anexo_de_esta_conexion_lambda": an.get("conexion_lambda_sha256") == CODIGO["conexion_lambda.py"],
        "alcance_no_oficial": all(al.get(k) is False for k in ("b_official_run_authorized", "freeze_run_authorized", "official_export_authorized")),
        "alcance_con_las_dos_tareas": all(t in al["tareas"] for t in TAREAS)}
    nc = fu["nucleo_c0"]
    preparar()
    import paper2b
    r["nucleo"] = {"identidad_recalculada": identidad_c0(), "igual_a_la_del_alcance": identidad_c0() == C0_IDENTIDAD,
                   "inventario": nc["archivos"], "copiados": nc["copiados"], "paper2b_cargado_de": rel(Path(paper2b.__file__).parent),
                   "distinto_del_nucleo_de_FAM04": nc["iguales_a_nucleo_s6_instalacion (FAM04)"]["distintos_en_src"],
                   "no_copiados_con_ruta_personal": len(nc["no_copiados_con_ruta_personal"])}
    r["procedencia"]["fuente_suplemento_igual_al_catalogo"] = man["L1-ELAST"]["suplemento_fuente"]["sha256"] == catalogo_sha(*FUENTE_CATALOGO)
    r["cobertura"] = cobertura_manifiesto(man, an)
    r["referencias"] = cobertura_referencias(man, an)
    lb = fu.get("libro_rem121") or {}
    ce, cl, rp = r["cobertura"]["L1-ELAST"], r["cobertura"]["L1-LAMBDA"], r["referencias"]["productos"]
    pares = []
    if lb.get("presente") is True:
        pares = [("ELAST.rows ↔ filas de frontier_result", lb["ELAST"]["rows"], rp["frontier_result.jsonl"]["filas"]),
                 ("ELAST.grids ↔ mallas del manifiesto", lb["ELAST"]["grids"], ce["mallas"]),
                 ("ELAST.new_grids ↔ mallas nuevas", lb["ELAST"]["new_grids"], ce["mallas_nuevas"]["mallas"]),
                 ("ELAST.new_rows ↔ filas nuevas de frontier_result", lb["ELAST"]["new_rows"], rp["frontier_result.jsonl"]["filas_nuevas"]),
                 ("ELAST.historical_rows_exact ↔ filas del suplemento (producto)", lb["ELAST"]["historical_rows_exact"], rp["frontier_result.jsonl"]["filas_del_suplemento"]),
                 ("ELAST.historical_rows_exact ↔ filas de la fuente", lb["ELAST"]["historical_rows_exact"], ce["suplemento"]["filas_de_la_fuente"]),
                 ("ELAST.historical_rows_exact ↔ filas de procedencia", lb["ELAST"]["historical_rows_exact"], rp["suplemento_procedencia.jsonl"]["filas"]),
                 ("ELAST.equivalences_already_accepted ↔ equivalencias del manifiesto", lb["ELAST"]["equivalences_already_accepted"], ce["equivalencias_ya_aceptadas"]),
                 ("ELAST.parent_frontiers_covered_total ↔ cubiertas + suplemento", lb["ELAST"]["parent_frontiers_covered_total"], ce["fronteras_cubiertas_con_suplemento"]),
                 ("LAMBDA.rows ↔ filas de lambda_envolvente", lb["LAMBDA"]["rows"], rp["lambda_envolvente.jsonl"]["filas"]),
                 ("LAMBDA.pairs ↔ pares del manifiesto", lb["LAMBDA"]["pairs"], cl["pares"]),
                 ("LAMBDA.exact_arithmetic_checks ↔ evidencias por estado (= llamadas a bridge)", lb["LAMBDA"]["exact_arithmetic_checks"], rp["lambda_envolvente.jsonl"]["llamadas_bridge"])]
    r["libro_rem121"] = {"presente": lb.get("presente"), "solo_extraccion": True,
                         "recuentos": [{"recuento": a, "libro": b, "archivos": c, "igual": b == c} for a, b, c in pares],
                         "recuentos_iguales": bool(pares) and all(b == c for _, b, c in pares),
                         "cobertura_nacional_igual": lb.get("presente") is True and lb["LAMBDA"]["coverage_counts"] == cl["estados_nacionales_del_anexo"],
                         "alias_iguales_al_manifiesto": (lb.get("ELAST_alias") or {}).get("iguales_a_los_del_manifiesto"),
                         "productos_iguales": lb.get("presente") is True and {n: p["sha256"] for n, p in lb["productos"].items()}
                         == {n: ref_aceptada(n) for n in lb["productos"]},
                         "alcance_de_la_decision": lb.get("alcance_de_la_decision_sha256") == ALCANCE[1]}
    rv = {}
    for t in TAREAS:
        rc, ver, _ = ejecutar_validador(REF / t / "resultado.json", REF / t / "salida", None)
        hist = json.loads((REF / t / "validacion_stdout.txt").read_text(encoding="utf-8"))
        rv[t] = {"rc": rc, "dictamen": ver.get("dictamen"), "n_fallos": ver.get("n_fallos"), "igual_a_la_validacion_historica": ver == hist}
    r["revalidacion_de_las_referencias"] = rv
    pil = leer(DATOS / "pilotos.json") if (DATOS / "pilotos.json").is_file() else None
    r["pilotos"] = {"fijados": [(p["tarea"], p["unidad"]) for p in (pil or {}).get("pilotos", [])],
                    "verificacion_historica": ((pil or {}).get("verificacion_historica") or {}).get("unidad"), "iguales_a_la_regla": pil == regla_pilotos(man)}
    r["receta"] = {"tareas": len(receta()["tareas"])}
    r["cumple"] = (not malos and all(r["procedencia"].values()) and r["nucleo"]["igual_a_la_del_alcance"] and r["cobertura"]["cumple"]
                   and all(v is True for k, v in r["libro_rem121"].items() if k != "recuentos") and r["referencias"]["cumple"]
                   and all(v["rc"] == 0 and v["igual_a_la_validacion_historica"] for v in rv.values()) and r["pilotos"]["iguales_a_la_regla"]
                   and r["receta"]["tareas"] == len(TAREAS))
    return r


# ================================================================================================ cálculo
def declarados() -> set:
    out = set()
    for n in ("fuentes_fam01.json", "fuentes_fam02.json", "fuentes_fam03.json", "fuentes_fam04.json", "fuentes_fam05.json"):
        if (BASE / n).is_file():
            out |= {x["archivo"] for x in leer(BASE / n).get("archivos", [])}
    return out


def lecturas(informe: dict) -> dict:
    dec = declarados()
    propios = ("src/", "reproducir.py", "datos/fam01/", "datos/fam05/", "fuentes_fam0", "catalogo.json")
    sin = [x for x in informe["en_el_paquete"] if x not in dec and not x.startswith(".venv-fam01/") and not x.startswith(propios)]
    return {"archivo": "archivos_leidos.json", "en_el_paquete": len(informe["en_el_paquete"]),
            "del_entorno_venv": sum(1 for x in informe["en_el_paquete"] if x.startswith(".venv-fam01/")),
            "aperturas_del_interprete": informe["aperturas_del_interprete"], "fuera_del_paquete_y_del_interprete": informe["fuera_del_paquete_y_del_interprete"],
            "sin_manifiesto": sin,
            "nucleo_c0_leidos": sum(1 for x in informe["en_el_paquete"] if x.startswith("nucleo_s6/c0/")),
            "src_de_otra_raiz_leidos": {"n": sum(1 for x in informe["en_el_paquete"] if x.startswith(("nucleo_s6/instalacion/src/", "nucleo_s6/raiz/src/"))),
                                        "nota": ("lecturas para hash de EB.code_manifest (identidad técnica documental del contexto FAM01, solo "
                                                 "L1-LAMBDA); no son importaciones: ver nucleo.paper2b_importado_de")},
            "fuente_del_suplemento_leida": any(x.startswith("datos/fam05/fuente_suplemento/") for x in informe["en_el_paquete"]),
            "referencias_leidas": [x for x in informe["en_el_paquete"] if x.startswith("referencias/") and not x.startswith("referencias/fam01/")]}


def _entorno(ctx=None) -> dict:
    import platform
    f = F1()
    if ctx is not None:
        doc, rec = ctx.env_doc, ctx.env_rec
    else:
        preparar()
        from herramientas.bloque2 import entorno as E
        E.set_runtime_conventions()
        ea = f.parametros()["entorno_aprobado"]
        doc = E.assessment(RAIZ, manifest_path=ea["manifest_path"], manifest_sha256=ea["manifest_sha256"], lock_path=ea["lock_path"], lock_sha256=ea["lock_sha256"])
        rec = f.records_sin_lanzadores()
    env_sha = sha(f.canon(doc) + b"\n")
    return {"conforms": doc.get("conforms"), "mismatches": doc.get("mismatches"), "environment_sha256": env_sha, "f2": f.equivalencia_f2(doc, rec, env_sha),
            "f2_alcance": "adoptada solo para FAM01; aquí se informa y no es requisito de FAM05", "python": platform.python_version(),
            "hash_seed": os.environ.get("PYTHONHASHSEED"), "hash_randomization": sys.flags.hash_randomization,
            "hilos": {k: os.environ.get(k) for k in f.HILOS}, "TZ": os.environ.get("TZ")}


def cobertura_contexto(ctx, CLX, MC, ml: dict, an: dict) -> dict:
    """Estados nacionales del contexto de esta base frente al anexo (sin evaluar λπ). Publicados: tipos, número y secuencia de huellas
    shares_sha256 (lo que exige el validador) e identidad completa del estado (informativa). Estrictos: definición única strict_domain con la
    huella del manifiesto y del anexo, y su enumeración estructural (candidatos, vértices de caja, signo) frente al anexo."""
    out = {}
    for s, v in ml.items():
        sts = ctx.inp.national(v.get("conjunto", s), v["pais"])
        c = an["conjuntos"][s]
        esp = c["estados"]
        tipos = sorted({(x.get("kind") if isinstance(x, dict) else type(x).__name__) for x in sts})
        if v.get("dominio_nacional") == "estricto":
            st = sts[0] if len(sts) == 1 and isinstance(sts[0], dict) and sts[0].get("kind") == "strict_domain" else None
            d = {"estados": len(sts), "tipos": tipos, "dominio": "estricto", "definicion_unica": st is not None}
            if st is not None:
                cand, nv, signo = CLX.vertices_estrictos(MC, st)
                d.update(definicion_igual_al_manifiesto=CLX.definicion_sha256(st) == v["definicion_sha256"],
                         definicion_igual_al_anexo=CLX.definicion_sha256(st) == c.get("definicion_sha256"), candidatos=len(cand), vertices_caja=nv,
                         signo_no_negativo=signo, huellas_iguales_al_anexo=[x["huella"] for x in cand] == [e["shares_sha256"] for e in esp])
            d["en_el_anexo"] = len(esp)
            out[s] = d
            continue
        hs = [CLX.huella_shares(x.share_dict()) for x in sts if isinstance(x, MC.NationalState)]
        ids = []
        for x in sts:
            if isinstance(x, MC.NationalState):
                ident = {"country_id": x.country_id, "preregistration_id": x.preregistration_id, "channel": x.channel, "edition": x.edition,
                         "anchor_year": x.anchor_year, "label": x.label, "primitive_values": [[p, str(y), u] for p, y, u in x.primitive_values],
                         "shares": {k: str(y) for k, y in x.shares}, "joint_domain_sha256": x.joint_domain_sha256,
                         "dependencies": json.loads(json.dumps(list(x.dependencies), default=str))}
                ids.append(sha(F1().canon(ident)))
        out[s] = {"estados": len(sts), "tipos": tipos, "dominio": "publicado", "huellas_iguales_al_anexo": hs == [e["shares_sha256"] for e in esp],
                  "identidades_iguales_al_anexo": sum(1 for a, e in zip(ids, esp) if a == e.get("estado_sha256")), "en_el_anexo": len(esp)}
    return out


def correr(tarea: str, salida: Path, unidad: str | None = None, tope: float = TOPE_TRABAJO) -> dict:
    """fam05-unidad: la tarea (o la unidad seleccionada) por la ruta de producción de tarea_lote (TAREA-AST-v2), en la carpeta NUEVA
    `salida`: salida/<productos>, resultado.json (esquema de tarea_lote), ejecucion.json y archivos_leidos.json."""
    T0, c0 = time.time(), time.process_time()
    rastro = F1().Rastro()                       # desde el principio: también las lecturas previas al cálculo
    need(tarea in TAREAS, "TAREA_NO_ADMITIDA: %s" % tarea)
    raw, man = manifiesto()
    sel = seleccion(man, tarea, unidad)
    malos = fuentes_alteradas(sin_referencias=True)
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam05.json; no se calcula): %s" % malos[:5])
    TOPE = float(tope) - HOLGURA
    need(TOPE > 0, "TOPE_INVALIDO")
    mods = pila()
    need(identidad_c0() == C0_IDENTIDAD, "NUCLEO_C0_DE_OTRA_IDENTIDAD (no se calcula)")
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    sal = salida.resolve()
    out = {"tarea": tarea, "modo": "produccion", "manifiesto_sha256": sha(raw), "tope_efectivo_s": TOPE, "sintetico": False,
           "codigo_sha256": {n: sha((LOTE / n).read_bytes()) for n in ("tarea_lote.py", "conexion_lambda.py", "conexion_frontera.py")}, "productos": []}
    ns, cod = espacio(mods, sal / "salida", out, man, T0, TOPE)
    ctx, ej, t_ctx, campos = None, {}, None, {}
    ruta = list(sys.path)
    a0 = time.time()
    try:
        if tarea == "L1-LAMBDA":
            ctx = contexto()
            t_ctx = round(time.time() - a0, 2)
            ml = {s: v for s, v in man["L1-LAMBDA"].items() if sel is None or s in sel["conjuntos"]}
            ej["cobertura_nacional_del_contexto"] = cobertura_contexto(ctx, mods["CLX"], mods["MC"], ml, anexo())
            ns.update(ctx=ctx, ml=ml)
        else:
            ns["fr_"] = {k: v for k, v in man["L1-ELAST"]["fronteras"].items() if sel is None or v["frontier_id"] in sel["fronteras"]}
        a0 = time.time()
        exec(cod[tarea], ns)
        raise Fam05Error("RAMA_SIN_CIERRE")       # la rama de producción siempre termina en fin(...)
    except FinTarea as f:
        estado, motivo, campos = f.estado, f.motivo, f.campos
    finally:
        sys.path[:] = ruta
    t_calc = round(time.time() - a0, 2)
    out.update(estado=estado, motivo=motivo, pared_s=round(time.time() - T0, 2), **campos)
    (sal / "resultado.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    informe = rastro.informe()
    (sal / "archivos_leidos.json").write_bytes((json.dumps(informe, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    ej.update({"tarea": tarea, "unidad": unidad, "operacion": ("F05-LAMBDA" if tarea == "L1-LAMBDA" else "F05-ELAST-HIST" if unidad == SUPLEMENTO
                                                                else "F05-ELAST-C0" if unidad else "F05-ELAST-C0 + F05-ELAST-HIST"),
               "seleccion": sel, "manifiesto_sha256": sha(raw), "etiqueta": ETIQUETA,
               "naturaleza": ("verificación y reutilización: 70 filas aceptadas sin recalcular + topología del núcleo" if unidad == SUPLEMENTO else
                              "cálculo: ruta de producción de tarea_lote.py (bytes exactos) en la base limpia; sin puerta de producción (PUERTA-v1)"),
               "adaptaciones": list(ADAPTACIONES), "reloj": "RELOJ-PILOTO-v1: tope interno %.0f s (= %.0f − %.0f); el límite externo lo pone el supervisor"
               % (TOPE, float(tope), HOLGURA), "resultado": {"estado": estado, "motivo": motivo, "productos": out["productos"]},
               "nucleo": {"identidad": identidad_c0(), "paper2b": rel(Path(mods["M"].__file__).parent),
                          "paper2b_importado_de": sorted({rel(Path(m.__file__).parent) for k, m in list(sys.modules.items())
                                                          if (k == "paper2b" or k.startswith("paper2b.")) and getattr(m, "__file__", None)})},
               "tiempos_s": {"contexto": t_ctx, "calculo": t_calc, "total": round(time.time() - T0, 2), "cpu": round(time.process_time() - c0, 2)},
               "contexto": None if ctx is None else {"identity_sha256": ctx.identity_sha256, "run_class": ctx.identity["run_class"]},
               "entorno": _entorno(ctx), "lecturas": lecturas(informe), "dependencias_fuera_de_la_biblioteca_estandar": F1().dependencias_cargadas()})
    ej["exito"] = estado == "completa"
    (sal / "ejecucion.json").write_bytes(json.dumps(ej, ensure_ascii=False, indent=1, sort_keys=True, default=str).encode("utf-8") + b"\n")
    return ej


# ================================================================================================ validación
def validador_adaptado() -> str:
    """VALIDADOR-v2: bytes exactos de validar_lote.py del lote 2 con las sustituciones declaradas (cada original, una sola vez)."""
    src = (LOTE / "validar_lote.py").read_bytes()
    need(sha(src) == CODIGO["validar_lote.py"], "VALIDADOR_DISTINTO")
    txt = src.decode("utf-8")
    for i, a, b in SUSTITUCIONES_VALIDADOR:
        need(txt.count(a) == 1, "SUSTITUCION_NO_UNICA: %s" % i)
        txt = txt.replace(a, b)
    return txt


def ejecutar_validador(res: Path, sal: Path, sel, cob: Path | None = None, raiz: Path | None = None) -> tuple:
    """El validador como guion (argv como en la suite histórica: raíz, manifiesto, resultado, salida, anexo [, selección]); la raíz es la
    de las rutas relativas del manifiesto (RUTA-SUPLEMENTO-v1)."""
    preparar()
    txt = validador_adaptado()
    cob = DATOS / ANEXO[0] if cob is None else cob
    if "conexion_lambda" in sys.modules:
        need(Path(sys.modules["conexion_lambda"].__file__).resolve() == (LOTE / "conexion_lambda.py").resolve(), "CONEXION_LAMBDA_DE_OTRO_LOTE")
    argv = [str(LOTE / "validar_lote.py"), str(raiz or FUENTE_SUP), str(DATOS / MANIFIESTO[0]), str(res), str(sal), str(cob)] + ([json.dumps(sel)] if sel is not None else [])
    viejo, ruta, buf, rc = sys.argv, list(sys.path), io.StringIO(), None
    sys.argv = argv
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(txt, str(LOTE / "validar_lote.py"), "exec"), {"__name__": "__main__", "__file__": str(LOTE / "validar_lote.py"), "__builtins__": builtins})
    except SystemExit as ex:
        rc = ex.code
    finally:
        sys.argv = viejo
        sys.path[:] = ruta
    lineas = [x for x in buf.getvalue().splitlines() if x.strip()]
    return rc, (json.loads(lineas[-1]) if lineas else {}), buf.getvalue()


def productos_de(nueva: Path, res: dict) -> dict:
    return {p["archivo"]: sha_archivo(Path(nueva) / "salida" / p["archivo"]) for p in res.get("productos") or []}


def validar(nueva: Path, cob: Path | None = None) -> dict:
    """fam05-validar: SIN CÁLCULO. validar_lote.py (VALIDADOR-v2) sobre los bytes guardados de `nueva` (carpeta de fam05-unidad), con la
    selección registrada en su ejecución y el anexo de cobertura nacional del manifiesto."""
    t0 = time.time()
    nueva = Path(nueva).resolve()
    ej = leer(nueva / "ejecucion.json")
    rb = (nueva / "resultado.json").read_bytes()
    rc, ver, _ = ejecutar_validador(nueva / "resultado.json", nueva / "salida", ej.get("seleccion"), cob)
    return {"comando": "fam05-validar", "naturaleza": "validación sin cálculo de bytes guardados", "tarea": ej["tarea"], "unidad": ej.get("unidad"),
            "operacion": ej.get("operacion"), "seleccion": ej.get("seleccion"), "origen": rel(nueva), "resultado_sha256": sha(rb),
            "productos_sha256": productos_de(nueva, json.loads(rb)),
            "validador": {"archivo": "nucleo_s6/lote2/validar_lote.py", "sha256": CODIGO["validar_lote.py"], "adaptacion": [x[0] for x in SUSTITUCIONES_VALIDADOR],
                          "adaptado_sha256": sha(validador_adaptado().encode("utf-8")), "nucleo": "nucleo_s6/c0 (NUCLEO-C0-v1)",
                          "raiz_de_rutas_del_manifiesto": rel(FUENTE_SUP)},
            "anexo": rel(cob) if cob is not None else "datos/fam05/" + ANEXO[0], "rc": rc, "veredicto": ver,
            "aceptada": rc == 0 and ver.get("aceptada") is True and ver.get("dictamen") == "completa_validada", "segundos": round(time.time() - t0, 3)}


# ================================================================================================ comparación
# COMPARACION-FAM05-v1. Contrato de comparadores, filas F05-*, contexto canónico (mismo perfil de entorno .venv-fam01 y MISMO núcleo C0 que
# la referencia rem120; no se compara con valores de otro núcleo): CR-HASH-CANONICO (cada fila idéntica campo a campo con su serialización
# JSON) y CR-DISCRETOS (estados, clasificaciones, NA, claves y conteos exactos, con precedencia). CR-OBJETO-OTRO-ENTORNO no se aplica. Las
# tolerancias internas del validador (T1) siguen siendo suyas y no se usan aquí.
# - frontier_result: filas de las mallas de la unidad (clave frontier_id, point_id, side), incluida «topology».
# - suplemento_procedencia (solo si la unidad contiene el suplemento): mismas claves; VINCULO-PROCEDENCIA-v1: el campo
#   frontier_result_sha256 es un vínculo, no un valor: en la nueva debe ser el sha256 de SU frontier_result.jsonl y en la referencia el del
#   producto aceptado (007095a9…); se muestra y se recomprueba; los demás campos, exactos. Además, las filas del suplemento en
#   frontier_result deben conservar EXACTAMENTE los campos de la fuente aceptada (reutilización) y añadir solo «topology».
# - lambda_envolvente: filas de los pares de la unidad (clave conjunto, variante), con evidencia por estado; llamadas_bridge por unidad.
# En resultado.json: tarea, modo, sintetico, estado, motivo y tope_efectivo_s se comparan; manifiesto y código son identidades; pared_s es
# operativo (se muestra).
CLAVE_FILA = {"frontier_result.jsonl": ("frontier_id", "point_id", "side"), "suplemento_procedencia.jsonl": ("frontier_id", "point_id", "side"),
              "lambda_envolvente.jsonl": ("conjunto", "variante")}
NUMERICOS = {"frontier_result.jsonl": {"tau_d", "tau_f", "B_d", "B_f", "R", "B_pot", "CS", "eps_dd", "eps_df", "eps_fd", "eps_ff", "s_P"},
             "suplemento_procedencia.jsonl": set(),
             "lambda_envolvente.jsonl": {"lambda_max", "lambda_min", "K1_sobre_Q_min", "K1_sobre_Q_max", "theta_W_en_max", "theta_W_en_min", "lambda"}}
VINCULOS = {"suplemento_procedencia.jsonl": ("/frontier_result_sha256",)}


def hojas(v, pref=""):
    if isinstance(v, dict):
        out = {}
        for k in sorted(v):
            out.update(hojas(v[k], pref + "/" + str(k)))
        return out or {pref: {}}
    if isinstance(v, list):
        out = {}
        for i, x in enumerate(v):
            out.update(hojas(x, "%s/%d" % (pref, i)))
        return out or {pref: []}
    return {pref: v}


def en_unidad(n: str, fila: dict, sel) -> bool:
    if sel is None:
        return True
    if n == "lambda_envolvente.jsonl":
        return fila.get("conjunto") in sel["conjuntos"]
    return fila.get("frontier_id") in sel["fronteras"]


def productos_esperados(tarea: str, sel, man: dict) -> tuple:
    if tarea == "L1-LAMBDA":
        return PRODUCTOS[tarea]
    con_sup = sel is None or bool(set(sel["fronteras"]) & set(suplemento_ids(man)))
    return PRODUCTOS[tarea] if con_sup else PRODUCTOS[tarea][:1]


def comparar_producto(n: str, nuevas_l: list, ref_l: list, vinculo: dict | None = None) -> dict:
    kf = CLAVE_FILA[n]
    nuevas, refs = [json.loads(x) for x in nuevas_l], [json.loads(x) for x in ref_l]
    kn, kr = [tuple(f.get(k) for k in kf) for f in nuevas], [tuple(f.get(k) for k in kf) for f in refs]
    dn, dr = dict(zip(kn, nuevas)), dict(zip(kr, refs))
    cob = {"filas_nuevas": len(nuevas), "filas_referencia": len(refs), "faltan": [list(k) for k in kr if k not in dn][:5],
           "ajenas": [list(k) for k in kn if k not in dr][:5], "duplicadas": (len(kn) - len(set(kn))) + (len(kr) - len(set(kr))), "mismo_orden": kn == kr}
    disc, num, vis = [], [], Counter()
    for k in kr:
        if k not in dn:
            continue
        hn, hr = hojas(dn[k]), hojas(dr[k])
        for p in sorted(set(hn) | set(hr)):
            a, b = hn.get(p, "<ausente>"), hr.get(p, "<ausente>")
            if p in VINCULOS.get(n, ()):               # VINCULO-PROCEDENCIA-v1: cada lado con SU frontier_result
                vis[(p, a == (vinculo or {}).get("nueva"), b == (vinculo or {}).get("referencia"))] += 1
                continue
            if json.dumps(a) == json.dumps(b):
                continue
            d = {"fila": list(k), "puntero": p, "nueva": a, "referencia": b}
            numerico = p.split("/")[-1] in NUMERICOS[n] and None not in (a, b) and "<ausente>" not in (a, b)   # valor frente a nulo (NA): discreta
            (num if numerico else disc).append(d)
    vin = None
    if n in VINCULOS:
        vin = {"campo": VINCULOS[n][0], "nueva_esperada": (vinculo or {}).get("nueva"), "referencia_esperada": (vinculo or {}).get("referencia"),
               "filas": sum(vis.values()), "nueva_ligada": sum(c for (p, a, b), c in vis.items() if a), "referencia_ligada": sum(c for (p, a, b), c in vis.items() if b)}
    return {"cobertura": cob, "lineas_identicas": nuevas_l == ref_l, "n_discretas": len(disc), "n_numericas": len(num),
            "discretas": disc[:20], "numericas": num[:20], "vinculo": vin}


def reutilizacion(nueva: Path, man: dict, sel) -> dict:
    """F05-ELAST-HIST: las filas del suplemento de la NUEVA salida frente a la fuente aceptada (entrada): campos idénticos en valor y tipo
    y solo «topology» añadido (sin recalcular nada)."""
    sf = man["L1-ELAST"]["suplemento_fuente"]
    ids = set(suplemento_ids(man)) & set(sel["fronteras"] if sel else suplemento_ids(man))
    fuente = {(y["frontier_id"], y["point_id"], y["side"]): y for y in leer_jsonl(FUENTE_SUP / sf["ruta"]) if y["frontier_id"] in ids}
    filas = [f for f in leer_jsonl(Path(nueva) / "salida/frontier_result.jsonl") if f.get("frontier_id") in ids]
    exactas, malas = 0, []
    for f in filas:
        y = fuente.get((f.get("frontier_id"), f.get("point_id"), f.get("side")))
        ok = y is not None and set(f) - set(y) == {"topology"} and all(c in f and type(f[c]) is type(y[c]) and json.dumps(f[c]) == json.dumps(y[c]) for c in y)
        exactas += ok
        if not ok:
            malas.append("%s:%s:%s" % (f.get("frontier_id"), f.get("point_id"), f.get("side")))
    return {"fuente_sha256": sha_archivo(FUENTE_SUP / sf["ruta"]), "fuente_autentica": sha_archivo(FUENTE_SUP / sf["ruta"]) == sf["sha256"],
            "filas_fuente": len(fuente), "filas_nuevas": len(filas), "exactas_mas_topologia": exactas, "malas": malas[:5],
            "cumple": bool(fuente) and exactas == len(fuente) == len(filas)}


def comparar(tarea: str, nueva: Path, validacion: Path) -> dict:
    """fam05-comparar: salida de fam05-unidad (`nueva`) y su validación (`validacion`, de fam05-validar) frente a la ejecución aceptada
    rem120 restringida a la misma unidad (o completa)."""
    nueva = Path(nueva).resolve()
    raw, man = manifiesto()
    mot = []
    ej = leer(nueva / "ejecucion.json")
    rb = (nueva / "resultado.json").read_bytes()
    res = json.loads(rb)
    sel = ej.get("seleccion")
    if ej.get("tarea") != tarea or res.get("tarea") != tarea:
        mot.append("SALIDA_DE_OTRA_TAREA: %s" % res.get("tarea"))
    if sel != seleccion(man, tarea, ej.get("unidad")):
        mot.append("SELECCION_INCOHERENTE")
    val = leer(validacion) if Path(validacion).is_file() else None
    if val is None:
        mot.append("VALIDACION_AUSENTE")
    else:
        if val.get("origen") != rel(nueva) or val.get("resultado_sha256") != sha(rb) or val.get("productos_sha256") != productos_de(nueva, res) or val.get("tarea") != tarea:
            mot.append("VALIDACION_DE_OTROS_BYTES")
        if val.get("aceptada") is not True:
            mot.append("VALIDACION_NO_ACEPTADA: %s" % ((val.get("veredicto") or {}).get("fallos") or [])[:3])
    if res.get("estado") != "completa":
        mot.append("CALCULO_NO_COMPLETO: %s" % res.get("motivo"))
    ref_res = leer(REF / tarea / "resultado.json")
    decl = {p["archivo"]: p for p in res.get("productos") or []}
    esperados = productos_esperados(tarea, sel, man)
    if sorted(decl) != sorted(esperados):
        mot.append("PRODUCTOS_DE_LA_UNIDAD_DISTINTOS: %s (esperados %s)" % (sorted(decl), list(esperados)))
    vinculo = {"nueva": (decl.get("frontier_result.jsonl") or {}).get("sha256"), "referencia": ref_aceptada("frontier_result.jsonl")}
    objetos = {}
    for n in esperados:
        fref = REF / tarea / "salida" / n
        if sha_archivo(fref) is None or sha_archivo(fref) != ref_aceptada(n):
            mot.append("REFERENCIA_ALTERADA_O_AJENA: %s" % n)
            continue
        d = decl.get(n)
        fn = nueva / "salida" / n
        if d is None or sha_archivo(fn) != d.get("sha256"):
            mot.append("PRODUCTO_AUSENTE_O_ALTERADO: %s" % n)
            continue
        ref_l = [x for x in fref.read_text(encoding="utf-8").splitlines() if x.strip() and en_unidad(n, json.loads(x), sel)]
        nue_l = [x for x in fn.read_text(encoding="utf-8").splitlines() if x.strip()]
        o = comparar_producto(n, nue_l, ref_l, vinculo)
        c = o["cobertura"]
        if c["faltan"] or c["ajenas"] or c["duplicadas"] or not c["mismo_orden"] or c["filas_nuevas"] != c["filas_referencia"] or not ref_l:
            mot.append("COBERTURA_DISTINTA (CR-DISCRETOS): %s" % n)
        if o["n_discretas"]:
            mot.append("DIFERENCIA_DISCRETA (CR-DISCRETOS, precedencia): %s %s" % (n, [x["puntero"] for x in o["discretas"][:4]]))
        if o["n_numericas"]:
            mot.append("DIFERENCIA_NUMERICA (CR-HASH-CANONICO): %s %s" % (n, [x["puntero"] for x in o["numericas"][:4]]))
        if o["vinculo"] is not None and not (o["vinculo"]["filas"] == o["vinculo"]["nueva_ligada"] == o["vinculo"]["referencia_ligada"] == c["filas_referencia"]):
            mot.append("VINCULO_DE_PROCEDENCIA_ROTO (VINCULO-PROCEDENCIA-v1): %s" % n)
        o["filas_decl"] = d.get("filas")
        objetos[n] = o
    rr = {}
    for k in ("tarea", "modo", "sintetico", "estado", "motivo", "tope_efectivo_s"):
        rr[k] = {"nueva": res.get(k), "referencia": ref_res.get(k), "igual": res.get(k) == ref_res.get(k)}
        if not rr[k]["igual"]:
            mot.append("RESULTADO_DISTINTO: %s" % k)
    ident = {"manifiesto_sha256": res.get("manifiesto_sha256") == ref_res.get("manifiesto_sha256") == MANIFIESTO[1],
             "codigo_sha256": res.get("codigo_sha256") == ref_res.get("codigo_sha256"),
             "nucleo_c0": ej.get("nucleo", {}).get("identidad") == C0_IDENTIDAD}
    if not all(ident.values()):
        mot.append("IDENTIDAD_DE_MANIFIESTO_CODIGO_O_NUCLEO_DISTINTA: %s" % [k for k, v in ident.items() if not v])
    deriv = {}
    if tarea == "L1-LAMBDA":
        an = anexo()
        filas_r = [f for f in leer_jsonl(REF / tarea / "salida/lambda_envolvente.jsonl") if en_unidad("lambda_envolvente.jsonl", f, sel)]
        filas_n = leer_jsonl(nueva / "salida/lambda_envolvente.jsonl") if (nueva / "salida/lambda_envolvente.jsonl").is_file() else []
        deriv["llamadas_bridge"] = {"nueva": res.get("llamadas_bridge"), "suma_filas_nuevas": sum(f["llamadas_bridge"] for f in filas_n),
                                    "referencia_unidad": sum(f["llamadas_bridge"] for f in filas_r), "referencia_tarea": ref_res.get("llamadas_bridge"),
                                    "presupuesto_del_anexo": sum(4 * an["conjuntos"][s]["n_estados"] for s in {f["conjunto"] for f in filas_r})}
        b = deriv["llamadas_bridge"]
        if not (b["nueva"] == b["suma_filas_nuevas"] == b["referencia_unidad"] == b["presupuesto_del_anexo"]):
            mot.append("LLAMADAS_BRIDGE_DISTINTAS")
        deriv["estados_por_extremo"] = {f["conjunto"] + "|" + f["variante"]: {"nueva": sorted({len(f["evidencia_por_estado"][e]) for e in ("max", "min")}),
                                                                           "anexo": an["conjuntos"][f["conjunto"]]["n_estados"]} for f in filas_n}
        if any(v["nueva"] != [v["anexo"]] for v in deriv["estados_por_extremo"].values()):
            mot.append("COBERTURA_NACIONAL_DISTINTA_DEL_ANEXO")
    elif "suplemento_procedencia.jsonl" in esperados:
        deriv["reutilizacion_historica"] = reutilizacion(nueva, man, sel)
        if not deriv["reutilizacion_historica"]["cumple"]:
            mot.append("FILAS_HISTORICAS_ALTERADAS (F05-ELAST-HIST)")
    if sel is None:
        deriv["productos"] = {"iguales_a_la_referencia": res.get("productos") == ref_res.get("productos")}
        if not deriv["productos"]["iguales_a_la_referencia"]:
            mot.append("PRODUCTOS_DISTINTOS_DE_LA_TAREA_DE_REFERENCIA")
    return {"comando": "fam05-comparar", "tarea": tarea, "unidad": ej.get("unidad"), "operacion": ej.get("operacion"), "seleccion": sel,
            "regla": "COMPARACION-FAM05-v1 (src/fam05.py)",
            "criterios": ["CR-HASH-CANONICO (mismo perfil de entorno y mismo núcleo C0; exacta)", "CR-DISCRETOS (precedencia)", "VINCULO-PROCEDENCIA-v1"],
            "no_aplicado": "CR-OBJETO-OTRO-ENTORNO (T1, T2_G): no es otro entorno; tampoco se comparan valores con el núcleo de FAM04",
            "referencia": {"ejecucion": "referencias/fam05/rem120/" + tarea, "productos": {n: ref_aceptada(n) for n in esperados},
                           "alcance": "misma unidad (selección)" if sel else "tarea completa"},
            "nueva": rel(nueva), "validacion": rel(Path(validacion)), "objetos": objetos, "resultado": rr, "identidades": ident, "derivados": deriv,
            "operativos": {"pared_s": {"nueva": res.get("pared_s"), "referencia_tarea": ref_res.get("pared_s")}},
            "estado": {"reproduccion": "aceptada" if not mot else "no_aceptada", "motivos": mot}}


# ================================================================================================ receta completa (sin ejecutarla)
def receta() -> dict:
    raw, man = manifiesto()
    an = anexo()
    u = unidades(man, an)
    ordenes = []
    for t in TAREAS:
        d = "salidas/fam05/<ejecucion>/" + t
        ordenes.append({"tarea": t, "operaciones": [k for k, v in OPERACIONES.items() if v.startswith(t)], "productos": list(PRODUCTOS[t]),
                        "referencia": "referencias/fam05/rem120/" + t,
                        "ordenes": ["reproducir.py fam05-unidad --tarea %s --salida %s" % (t, d),
                                    "reproducir.py fam05-validar --nueva %s --salida %s.validacion.json" % (d, d),
                                    "reproducir.py fam05-comparar --tarea %s --nueva %s --validacion %s.validacion.json --salida %s.comparacion.json" % (t, d, d, d)]})
    estados = {s: c["n_estados"] for s, c in an["conjuntos"].items()}
    el = man["L1-ELAST"]
    sup = [v for v in el["fronteras"].values() if v.get("suplemento_topologia")]
    return {"comando": "fam05-receta", "estado": "receta completa preparada; NO ejecutada (el lote pertenece al Paso 3)", "manifiesto_sha256": sha(raw),
            "orden": list(TAREAS), "tareas": ordenes,
            "cobertura": {"L1-ELAST": {"mallas": len(el["fronteras"]), "mallas_nuevas": el["mallas_remanentes"], "nodos_nuevos": el["puntos_remanentes"],
                                       "mallas_suplemento": len(sup), "filas_historicas": el["suplemento_fuente"]["filas"],
                                       "nodos": el["puntos_totales_frontier_n4"], "fronteras_cubiertas": el["frontier_ids_cubiertos"] + len(sup),
                                       "filas": "una «point» por nodo y left_limit/right_limit si y solo si hay kink; procedencia de las 70 filas del suplemento"},
                          "L1-LAMBDA": {"pares": len(u["L1-LAMBDA"]), "filas": 2 * len(u["L1-LAMBDA"]), "estados_nacionales": estados,
                                        "llamadas_bridge": sum(4 * e for e in estados.values())}},
            "previo": ["reproducir.py fam05-comprobar --salida salidas/fam05/<nuevo>.json (sin cálculo científico)"],
            "ejecucion": {"procesos": "una tarea a la vez, sin reintentos", "tope_trabajo_s": TOPE_TRABAJO, "reloj_interno_s": TOPE_TRABAJO - HOLGURA,
                          "tope_validacion_s": TOPE_VALIDACION,
                          "lanzador": "supervisor que termina el árbol de procesos (el mismo de los pilotos), con el tope de trabajo como límite externo",
                          "parada": "si una tarea no queda completa y validada, la siguiente no se lanza",
                          "duracion": "sin estimación: los pilotos no la permiten"},
            "F1": {"reutilizado": ["selección del lote (LOTE2_MANIFIESTO.json; la selección no se re-ejecuta)",
                                   "anexo de cobertura nacional (preparación hasta selección y enumeración estructural, sin λπ)",
                                   "70 filas numéricas aceptadas del lote 1 (suplemento: fuente autenticada, sin recalcular)",
                                   "núcleo C0 (src/paper2b, inventario de su instalación); D7, contratos y datos nacionales de FAM01"],
                   "se_genera_de_nuevo": ["filas frontier_result de las 393 mallas nuevas (4.125 nodos y sus laterales), con topología",
                                          "topología del núcleo de las 70 filas del suplemento y su procedencia",
                                          "24 envolventes λπ de 12 pares (488 evaluaciones de macro.bridge)"],
                   "solo_para_comparar": ["productos y resultados de la ejecución aceptada rem120 (= objetos del catálogo FAM05)"],
                   "no_cubre": ["L1-COORD del lote 2 (FAM07)", "E4 (FAM06)", "FAM04 (lote 1)"]},
            "pilotos": leer(DATOS / "pilotos.json") if (DATOS / "pilotos.json").is_file() else None}
