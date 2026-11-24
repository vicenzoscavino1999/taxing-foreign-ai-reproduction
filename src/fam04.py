"""FAM04 (lote 1: L1-ELAST, L1-LAMBDA, L1-COORD): comprobación sin cálculo de entradas, referencias y cobertura; cálculo de una tarea o de
una unidad seleccionada por la ruta de tarea_lote.py; validación por validar_lote.py; comparación con la ejecución productiva aceptada
(rem112, productos del catálogo F04-LOTE1) y receta completa (sin ejecutarla).

Unidades del lote (no se confunden):
- L1-ELAST: 6 fronteras (clave «diseño|j» del manifiesto) con 70 nodos de malla en total (frontier_n = 4: 5 nodos en d o f, 25 en df); cada
  nodo da una fila «point» y, si y solo si hay kink, sus filas left_limit/right_limit;
- L1-LAMBDA: 2 conjuntos nacionales (PER-E1.macro, PER-E1.micro) × 2 variantes (con, sin) = 4 filas; cada fila evalúa los 9 estados
  nacionales del anexo en el testigo del máximo y en el del mínimo (36 llamadas a macro.bridge por conjunto);
- L1-COORD: 12 claves transformadas (12 techos C2') y 192 celdas padre (192 comparaciones, 16 por clave).

Piezas (copias exactas; ver fuentes_fam04.json): nucleo_s6/lote1 (tarea_lote.py, conexion_lambda.py, conexion_frontera.py, validar_lote.py),
datos/fam04 (manifiesto, anexo de cobertura nacional, paquete y alcance; los dos últimos solo cruzan huellas), núcleo paper2b de la
instalación (FAM01: idéntico byte a byte al que exigen el trabajador y el validador), contexto S6 de FAM01 (solo L1-LAMBDA: estados
nacionales) y filas de las 192 celdas padre (referencias/fam01/originales, para autenticar K1 y G reutilizados).

Adaptaciones de interfaz (no cambian fórmulas, mallas, tolerancias, presupuestos ni criterios):
- TAREA-AST-v1: tarea_lote.py tiene código de entrada al nivel superior (argumentos, puerta de producción, cierre); no se importa. Sus funciones
  dom_manifiesto, proveedor_real, calc_lambda, calc_elast, calc_coord y producto se compilan desde sus bytes exactos (árbol sintáctico, con sus
  números de línea) en un espacio con los mismos nombres (CLX, CFR, MC, M, RUN, FR, Fr, SINT, tope, SAL, out, H). El documento
  resultado.json y el estado final siguen las reglas de su cierre (fin): mismo esquema y mismas condiciones de «completa»/«incompleta».
- PUERTA-v1: la puerta de producción de tarea_lote (alcance v3 + decisión humana nativa leída de la transcripción) no se ejecuta ni se
  reconstruye; los pilotos los autoriza el encargo de FAM04 y la receta completa queda para el Paso 3. modo = «produccion» es el que exige el
  validador para el manifiesto real (no sintético); la etiqueta de esta base es NO OFICIAL.
- CONTEXTO-FAM04-v1 (solo L1-LAMBDA): fam01.Contexto (la construcción de RunInputs de ContextoS6 sin capa administrativa, la misma que el
  contexto «portable» del candidato, que solo omite encargo y procedencia) con run_class = paso4_operativo_s6, el del despliegue de la
  producción (f293a0a6…). De él la ruta usa solo ctx.inp.national (proveedor_real).
- SELECCION-UNIDAD-v1: una unidad (frontera, conjunto o clave transformada) se calcula pasando a calc_* la parte del manifiesto de ESA unidad
  completa (todos sus nodos, variantes, estados y celdas padre); el validador recibe la selección y restringe a ella sus conjuntos esperados
  (VALIDADOR-v1). Sin selección, la tarea completa.
- VALIDADOR-v1: validar_lote.py (también código de entrada al nivel superior) se ejecuta como guion, desde sus bytes exactos con las
  sustituciones declaradas en SUSTITUCIONES_VALIDADOR (cada texto original aparece una sola vez): núcleo de la instalación de esta base y
  selección opcional. Sin selección se comporta como el original (lo comprueba local/pruebas_fam04.py frente al original sin cambios). Las
  comprobaciones del manifiesto completo que la selección omite (total de puntos de malla, techos nuevos únicos) las hace fam04-comprobar.
- RELOJ-PILOTO-v1: reloj interno de la tarea = tope de trabajo − holgura del conductor (2400 − 120 = 2280 s, el de la producción); el límite
  externo de cada invocación lo pone el supervisor (600 s en los pilotos): si se agota, la tarea queda incompleta; nada se reduce.
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
from collections import Counter
from fractions import Fraction as Fr
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RAIZ = BASE / "nucleo_s6" / "raiz"
INST = BASE / "nucleo_s6" / "instalacion"
LOTE = BASE / "nucleo_s6" / "lote1"
DATOS = BASE / "datos" / "fam04"
REF = BASE / "referencias" / "fam04" / "rem112"
ORIG01 = BASE / "referencias" / "fam01" / "originales"
CODIGO = {"tarea_lote.py": "331a23c9b79cc7f00a697c5cc4c26b14204b37a8824ec8ffc368f57098009356",
          "conexion_lambda.py": "bc498b810819ae57fbe40c849ad4e9d015650069e7053246304701fa9afb71d6",
          "conexion_frontera.py": "cac8b7ec3214ea37ffb985079fde972b682af4ebb8e5c64361d933a7b346147c",
          "validar_lote.py": "d12d3e7607cc39f99bb623263b67c14fdb449923d1e3cda43df6d361431f5b34"}
MANIFIESTO = ("LOTE1_MANIFIESTO.json", "19ecd7d3eb0e42a67d46678a6b447f064c8011a27361c8777330ddade9e8ebb9")
ANEXO = ("COBERTURA_NACIONAL_LOTE1.json", "268a63d592905dd0add16d968e253b08bc737212ca4fa7c7adead1730263b50e")
PAQUETE = ("PAQUETE_LOTE1.json", "5a457def0ef36aed51ec6ee2931983ed5c25837d993ba614e4eddfd847248067")
ALCANCE = ("alcance_lote1.json", "8fa9c49e756f16df77d09eff6662ac5914688fde2a78f8861d554fa020fa767d")
TAREAS = ("L1-ELAST", "L1-LAMBDA", "L1-COORD")                    # orden de las suites del paquete (PAQUETE_LOTE1.suites.orden)
PRODUCTOS = {"L1-ELAST": ("frontier_result.jsonl",), "L1-LAMBDA": ("lambda_envolvente.jsonl",), "L1-COORD": ("coord_techos.jsonl", "coord_comparacion.jsonl")}
TOPE_TRABAJO, HOLGURA, TOPE_VALIDACION = 2400.0, 120.0, 300.0     # conductor rem111 (estado_lote de rem112: parametros)
RUN_CLASS = "paso4_operativo_s6"
ETIQUETA = "REPRODUCCION LIMPIA FAM04 NO OFICIAL"
FUNCIONES_TAREA = ("dom_manifiesto", "proveedor_real", "calc_lambda", "calc_elast", "calc_coord", "producto")
CLAVES_ESTRUCTURALES = ("a", "beta_tilde", "c_legal", "eta_d", "eta_f", "gamma", "kappa_tilde", "phi", "rho", "t", "u_theta", "z_cost", "z_m")
ADAPTACIONES = ("TAREA-AST-v1", "PUERTA-v1", "CONTEXTO-FAM04-v1 (solo L1-LAMBDA)", "SELECCION-UNIDAD-v1", "VALIDADOR-v1", "RELOJ-PILOTO-v1")
SUSTITUCIONES_VALIDADOR = (
    ("NUCLEO-v1", 'sys.path.insert(0, str(R / "paso4/instalacion/src"))', 'sys.path.insert(0, str(R / "src"))'),
    ("SEL-ARGUMENTO", 'COB = Path(sys.argv[5]) if len(sys.argv) > 5 else None',
     'COB = Path(sys.argv[5]) if len(sys.argv) > 5 else None\nSEL = json.loads(sys.argv[6]) if len(sys.argv) > 6 else None'),
    ("SEL-LAMBDA", '    esperado = {(s, v) for s in ml for v in ("con", "sin")}',
     '    esperado = {(s, v) for s in ml if SEL is None or s in SEL["conjuntos"] for v in ("con", "sin")}'),
    ("SEL-ELAST", '        ids[v["frontier_id"]] = (key.split("|")[1], v)',
     '        if SEL is None or v["frontier_id"] in SEL["fronteras"]:\n            ids[v["frontier_id"]] = (key.split("|")[1], v)'),
    ("SEL-ELAST-TOTAL", '    if "puntos_totales_frontier_n4" in man["L1-ELAST"] and', '    if SEL is None and "puntos_totales_frontier_n4" in man["L1-ELAST"] and'),
    ("SEL-COORD-TECHOS", '    sel = set(co["claves_transformadas"])', '    sel = set(co["claves_transformadas"]) if SEL is None else set(SEL["claves"])'),
    ("SEL-COORD-UNICOS", '    if "techos_nuevos_unicos" in co and', '    if SEL is None and "techos_nuevos_unicos" in co and'),
    ("SEL-COORD-CELDAS", '    cel = {c["unidad"]: c for c in co["celdas"]}',
     '    cel = {c["unidad"]: c for c in co["celdas"] if SEL is None or c["clave_transformada_sha256"] in SEL["claves"]}'))


class Fam04Error(RuntimeError):
    pass


class TopeAlcanzado(Exception):
    pass


def need(t, codigo):
    if not t:
        raise Fam04Error(codigo)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_archivo(p: Path):
    return sha(Path(p).read_bytes()) if Path(p).is_file() else None


def leer(p: Path):
    return json.loads(Path(p).read_bytes())


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
    return leer(BASE / "fuentes_fam04.json")


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


# ================================================================================================ módulos
def preparar():
    """sys.path: núcleo paper2b de la instalación delante (el que exigen trabajador y validador) y la raíz copiada después (contexto S6)."""
    for p in (str(RAIZ / "src"), str(RAIZ), str(INST / "src")):
        while p in sys.path:
            sys.path.remove(p)
    sys.path.insert(0, str(RAIZ))
    sys.path.insert(0, str(INST / "src"))
    import paper2b
    need(Path(paper2b.__file__).resolve().parent == (INST / "src" / "paper2b").resolve(), "NUCLEO_NO_ES_EL_DE_LA_INSTALACION:" + paper2b.__file__)


def pila():
    preparar()
    for n, h in CODIGO.items():
        need(sha_archivo(LOTE / n) == h, "CODIGO_DEL_LOTE_DISTINTO: %s" % n)
    CLX = cargar("conexion_lambda", LOTE / "conexion_lambda.py")
    CFR = cargar("conexion_frontera", LOTE / "conexion_frontera.py")
    from paper2b import frontier as FR
    from paper2b import macro as MC
    from paper2b import model as M
    from paper2b import run as RUN
    return {"CLX": CLX, "CFR": CFR, "MC": MC, "M": M, "RUN": RUN, "FR": FR}


def funciones_tarea(mods: dict, SAL: Path, out: dict, tope) -> dict:
    """TAREA-AST-v1: las funciones de tarea_lote.py compiladas desde sus bytes exactos, sin ejecutar su código de entrada."""
    p = LOTE / "tarea_lote.py"
    src = p.read_bytes()
    need(sha(src) == CODIGO["tarea_lote.py"], "TAREA_LOTE_DISTINTA")
    arbol = ast.parse(src.decode("utf-8"), filename=str(p))
    fn = [n for n in arbol.body if isinstance(n, ast.FunctionDef) and n.name in FUNCIONES_TAREA]
    need(sorted(n.name for n in fn) == sorted(FUNCIONES_TAREA), "FUNCIONES_DE_TAREA_LOTE_AUSENTES")
    ns = dict(mods, Fr=Fr, SINT=False, tope=tope, SAL=SAL, out=out, H=sha, json=json, Path=Path, time=time, __builtins__=builtins)
    exec(compile(ast.Module(body=fn, type_ignores=[]), str(p), "exec"), ns)
    return ns


def contexto():
    preparar()
    f = F1()
    return f.Contexto(dict(f.parametros(), etiqueta=ETIQUETA, run_class=RUN_CLASS), raiz=RAIZ, inst=INST)


# ================================================================================================ unidades y pilotos
def unidades(man: dict, an: dict | None = None) -> dict:
    an = an or anexo()
    co = man["L1-COORD"]
    por_clave = {}
    for c in co["celdas"]:
        por_clave.setdefault(c["clave_transformada_sha256"], []).append(c["unidad"])
    return {"L1-ELAST": [{"unidad": v["frontier_id"], "clave": k, "dimension_malla": v["dimension_malla"], "nodos": v["puntos_frontier_n4"]}
                         for k, v in man["L1-ELAST"]["fronteras"].items()],
            "L1-LAMBDA": [{"unidad": s, "pais": v["pais"], "variantes": sorted(v["variantes"]), "estados_nacionales": an["conjuntos"][s]["n_estados"]}
                          for s, v in man["L1-LAMBDA"].items()],
            "L1-COORD": [{"unidad": k, "diseno": co["claves_transformadas"][k]["diseno"], "j": co["claves_transformadas"][k]["j"], "celdas": len(u)}
                         for k, u in por_clave.items()]}


def seleccion(man: dict, tarea: str, unidad: str | None):
    """Filtro de UNIDADES del lote (nunca del soporte de la unidad). None = tarea completa."""
    if unidad is None:
        return None
    if tarea == "L1-ELAST":
        need(unidad in {v["frontier_id"] for v in man["L1-ELAST"]["fronteras"].values()}, "FRONTERA_FUERA_DEL_MANIFIESTO: %s" % unidad)
        return {"fronteras": [unidad]}
    if tarea == "L1-LAMBDA":
        need(unidad in man["L1-LAMBDA"], "CONJUNTO_FUERA_DEL_MANIFIESTO: %s" % unidad)
        return {"conjuntos": [unidad]}
    need(unidad in man["L1-COORD"]["claves_transformadas"], "CLAVE_FUERA_DEL_MANIFIESTO: %s" % unidad)
    return {"claves": [unidad]}


def regla_pilotos(man: dict) -> dict:
    fr_ = man["L1-ELAST"]["fronteras"]
    ke = next(k for k, v in fr_.items() if v["dimension_malla"] == 2)
    s = next(iter(man["L1-LAMBDA"]))
    co = man["L1-COORD"]
    kc = next(c["clave_transformada_sha256"] for c in co["celdas"] if co["claves_transformadas"][c["clave_transformada_sha256"]]["j"] == "df")
    celdas = [c["unidad"] for c in co["celdas"] if c["clave_transformada_sha256"] == kc]
    return {"regla": ("fijados por identificador desde el MANIFIESTO (entrada), antes de calcular y sin mirar resultados: ELAST, la primera "
                      "frontera bidimensional (dimension_malla = 2: τ_d y τ_f); LAMBDA, el primer conjunto nacional; COORD, la primera clave "
                      "transformada con j = df (dominio τ bidimensional) en el orden de las celdas del manifiesto"),
            "pilotos": [{"tarea": "L1-ELAST", "unidad": fr_[ke]["frontier_id"], "clave": ke,
                         "cobertura": "frontera completa: %d nodos de malla (frontier_n = 4) con sus filas laterales si hay kink" % fr_[ke]["puntos_frontier_n4"]},
                        {"tarea": "L1-LAMBDA", "unidad": s, "pais": man["L1-LAMBDA"][s]["pais"],
                         "cobertura": ("conjunto completo: variantes con y sin, testigos de máximo y mínimo y todos los estados nacionales del anexo; "
                                       "en la variante sin, el testigo de λ_max del manifiesto está en la frontera θ_W = %s"
                                       % man["L1-LAMBDA"][s]["variantes"]["sin"]["theta_W_en_max"])},
                        {"tarea": "L1-COORD", "unidad": kc, "diseno": co["claves_transformadas"][kc]["diseno"], "j": "df",
                         "cobertura": "clave completa: un techo C2' sobre todo su dominio τ y las comparaciones de sus %d celdas padre" % len(celdas),
                         "celdas_padre": celdas}]}


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
    return {"comando": "fam04-listar", "calculo": "ninguno", "manifiesto_sha256": sha(raw), "unidades": unidades(man), "pilotos": fijar_pilotos(man)}


# ================================================================================================ comprobación (sin cálculo científico)
def autenticar_padres(celdas: list) -> dict:
    """Como «tarea_lote --modo hasta-seleccion» en L1-COORD: filas de la celda padre con su huella y su K1/G = los del manifiesto (las filas
    están en el paquete por FAM01, referencias/fam01/originales)."""
    malos = []
    for c in celdas:
        p = ORIG01 / Path(c["ref"]).name
        if not p.is_file() or sha(p.read_bytes()) != c["filas_sha256"]:
            malos.append(c["unidad"])
            continue
        cr = (json.loads(p.read_bytes()).get("confrontation_result") or [{}])[0]
        if cr.get("K_comp_1") != c["K1_reutilizado"] or cr.get("G") != c["G_padre"]:
            malos.append(c["unidad"])
    return {"celdas": len(celdas), "k1_reutilizados": len(celdas) - len(malos), "malos": malos[:5], "cumple": not malos and bool(celdas)}


def cobertura_manifiesto(man: dict, an: dict) -> dict:
    preparar()
    from paper2b.run import RunConfig
    from paper2b.supremum import axes, nodes
    n = RunConfig().frontier_n
    mot = []
    el = man["L1-ELAST"]
    por_f, total = {}, 0
    for k, v in el["fronteras"].items():
        j = k.split("|")[1]
        (dl, dh), (fl, fh) = axes(j, float(v["dominio_tau"]["tau_d_upper"]), float(v["dominio_tau"]["tau_f_upper"]))
        m = len(nodes(dl, dh, n) if dh > dl else [dl]) * len(nodes(fl, fh, n) if fh > fl else [fl])
        por_f[v["frontier_id"]] = m
        total += m
        if m != v["puntos_frontier_n4"]:
            mot.append("MALLA_DISTINTA_DEL_MANIFIESTO: %s" % v["frontier_id"])
        if [p for p in CLAVES_ESTRUCTURALES if p not in v["clave_estructural"]] or not v["dominio_tau"]:
            mot.append("CLAVE_O_DOMINIO_INCOMPLETO: %s" % k)
    if total != el["puntos_totales_frontier_n4"]:
        mot.append("TOTAL_DE_PUNTOS_DISTINTO_DE_LA_MALLA")
    ml = man["L1-LAMBDA"]
    if set(an["conjuntos"]) != set(ml):
        mot.append("ANEXO_CON_OTROS_CONJUNTOS")
    estados = {}
    for s, c in an["conjuntos"].items():
        hs = [e["shares_sha256"] for e in c["estados"]]
        estados[s] = len(hs)
        if not (c.get("independiente_de_omega") is True and c["n_estados"] == len(hs) and len(set(hs)) == len(hs)
                and [e["orden"] for e in c["estados"]] == list(range(len(hs)))):
            mot.append("ANEXO_INCONSISTENTE: %s" % s)
        if sorted(ml.get(s, {}).get("variantes", {})) != ["con", "sin"]:
            mot.append("VARIANTES_INCOMPLETAS: %s" % s)
    co = man["L1-COORD"]
    cnt = Counter(c["clave_transformada_sha256"] for c in co["celdas"])
    if set(cnt) != set(co["claves_transformadas"]) or len(cnt) != co["techos_nuevos_unicos"]:
        mot.append("CLAVES_TRANSFORMADAS_DISTINTAS_DE_LAS_CELDAS")
    if len(co["celdas"]) != co["celdas_padre_testigo"] or len({c["unidad"] for c in co["celdas"]}) != len(co["celdas"]):
        mot.append("CELDAS_PADRE_DISTINTAS")
    por_djm = Counter("%s|%s|%s" % (c["diseno"], c["j"], c["menu"]) for c in co["celdas"])
    if dict(por_djm) != co["por_diseno_j_menu"]:
        mot.append("CELDAS_POR_DISENO_J_MENU_DISTINTAS")
    return {"L1-ELAST": {"fronteras": len(por_f), "nodos_por_frontera": por_f, "nodos_total": total, "frontier_n": n},
            "L1-LAMBDA": {"conjuntos": len(ml), "filas_esperadas": 2 * len(ml), "estados_nacionales_del_anexo": estados,
                          "llamadas_bridge_esperadas": sum(2 * 2 * e for e in estados.values())},
            "L1-COORD": {"claves": len(cnt), "techos_esperados": len(cnt), "celdas_padre": len(co["celdas"]), "comparaciones_esperadas": len(co["celdas"]),
                         "celdas_por_clave": sorted(set(cnt.values()))},
            "cumple": not mot, "motivos": mot}


def leer_jsonl(p: Path) -> list:
    return [json.loads(x) for x in Path(p).read_text(encoding="utf-8").splitlines() if x.strip()]


def productos_catalogo() -> dict:
    c = leer(BASE / "catalogo.json")
    op = next(o for o in c["operaciones"] if o["clave"] == "F04-LOTE1")
    return {Path(p["objeto"]).name: p["sha256_aceptado"] for p in op["productos"]}


def cobertura_referencias(man: dict) -> dict:
    cat = productos_catalogo()
    mot, r = [], {}
    for t, prods in PRODUCTOS.items():
        res = leer(REF / t / "resultado.json")
        val = json.loads((REF / t / "validacion_stdout.txt").read_text(encoding="utf-8"))
        if res.get("estado") != "completa" or res.get("manifiesto_sha256") != MANIFIESTO[1] or val.get("dictamen") != "completa_validada" or val.get("n_fallos") != 0:
            mot.append("REFERENCIA_NO_ACEPTADA: %s" % t)
        if {k: v for k, v in res["codigo_sha256"].items()} != {k: CODIGO[k] for k in ("tarea_lote.py", "conexion_lambda.py", "conexion_frontera.py")}:
            mot.append("REFERENCIA_DE_OTRO_CODIGO: %s" % t)
        decl = {p["archivo"]: p for p in res["productos"]}
        for n in prods:
            f = REF / t / "salida" / n
            h = sha_archivo(f)
            filas = leer_jsonl(f) if h else []
            if h != cat.get(n) or decl.get(n, {}).get("sha256") != h or decl.get(n, {}).get("filas") != len(filas):
                mot.append("REFERENCIA_ALTERADA_O_AJENA: %s" % n)
            r[n] = {"filas": len(filas), "sha256": h}
    fr = leer_jsonl(REF / "L1-ELAST/salida/frontier_result.jsonl")
    por_f = Counter(x["frontier_id"] for x in fr if x["side"] == "point")
    nodos = {v["frontier_id"]: v["puntos_frontier_n4"] for v in man["L1-ELAST"]["fronteras"].values()}
    if dict(por_f) != nodos:
        mot.append("REFERENCIA_ELAST_CON_OTROS_NODOS")
    r["frontier_result.jsonl"].update(lados=dict(Counter(x["side"] for x in fr)), kinks=sum(1 for x in fr if x["kink_adjacent"] is True),
                                      motivos=dict(Counter(str(x["reason_code"]) for x in fr)), auditoria=dict(Counter(x["audit_status"] for x in fr)))
    la = leer_jsonl(REF / "L1-LAMBDA/salida/lambda_envolvente.jsonl")
    if sorted((x["conjunto"], x["variante"]) for x in la) != sorted((s, v) for s in man["L1-LAMBDA"] for v in ("con", "sin")):
        mot.append("REFERENCIA_LAMBDA_CON_OTRAS_FILAS")
    r["lambda_envolvente.jsonl"].update(estados=dict(Counter(x["estado"] for x in la)),
                                        evidencia_por_extremo=sorted({len(x["evidencia_por_estado"][e]) for x in la for e in ("max", "min")}),
                                        llamadas_bridge=sum(x["llamadas_bridge"] for x in la))
    te = leer_jsonl(REF / "L1-COORD/salida/coord_techos.jsonl")
    cp = leer_jsonl(REF / "L1-COORD/salida/coord_comparacion.jsonl")
    if sorted(x["clave_transformada_sha256"] for x in te) != sorted(man["L1-COORD"]["claves_transformadas"]):
        mot.append("REFERENCIA_COORD_CON_OTRAS_CLAVES")
    if [x["unidad"] for x in cp] != [c["unidad"] for c in man["L1-COORD"]["celdas"]]:
        mot.append("REFERENCIA_COORD_CON_OTRAS_CELDAS")
    r["coord_techos.jsonl"].update(estados=dict(Counter(x["estado"] for x in te)))
    return {"productos": r, "cumple": not mot, "motivos": mot}


def comprobar() -> dict:
    """fam04-comprobar: SIN CÁLCULO CIENTÍFICO (sin contexto, malla ni techos; la revalidación de las referencias aplica el validador a
    bytes guardados)."""
    r = {"comando": "fam04-comprobar", "calculo": "ninguno"}
    malos = fuentes_alteradas()
    fu = fuentes()
    r["fuentes"] = {"archivos": len(fu["archivos"]), "ausentes_o_distintos": malos[:20]}
    raw, man = manifiesto()
    an, al, pq = anexo(), leer(DATOS / ALCANCE[0]), leer(DATOS / PAQUETE[0])
    cod = {n: sha_archivo(LOTE / n) for n in CODIGO}
    pz = pq["piezas"]
    r["procedencia"] = {
        "codigo_igual_al_alcance": {k: cod[k] for k in ("tarea_lote.py", "conexion_lambda.py", "conexion_frontera.py")} == al["entradas"]["codigo_lote"],
        "validador_igual_al_alcance": cod["validar_lote.py"] == al["entradas"]["validador_lote"],
        "manifiesto_igual_al_alcance": sha(raw) == al["lote_manifiesto_sha256"] == al["entradas"]["lote_manifiesto"],
        "anexo_igual_al_alcance": ANEXO[1] == al["entradas"]["cobertura_nacional"],
        "piezas_iguales_al_paquete": all(pz[n]["sha256"] == cod[n] for n in CODIGO) and pz[MANIFIESTO[0]]["sha256"] == sha(raw)
                                     and pz[ANEXO[0]]["sha256"] == ANEXO[1],
        "anexo_ligado_al_manifiesto": an.get("kind") == "cobertura-nacional-lote1" and an.get("manifiesto_sha256") == sha(raw)
                                      and an.get("origen") == "preparacion_hasta_seleccion",
        "anexo_sin_evaluar_lambda": an.get("llamadas_durante_preparacion") == {"macro.bridge": 0, "macro.strict_vertices": 0},
        "alcance_no_oficial": all(al.get(k) is False for k in ("b_official_run_authorized", "freeze_run_authorized", "official_export_authorized"))}
    nr = fu["nucleo_requerido"]["archivos"]
    presentes = sorted(p.name for p in (INST / "src/paper2b").glob("*.py"))
    r["nucleo"] = {"archivos": len(nr), "iguales": sum(1 for k, v in nr.items() if sha_archivo(INST / "src/paper2b" / k) == v["sha256"] == v["candidato_rem107"]),
                   "otros_presentes": sorted(set(presentes) - set(nr))}
    r["cobertura"] = cobertura_manifiesto(man, an)
    r["celdas_padre"] = autenticar_padres(man["L1-COORD"]["celdas"])
    r["referencias"] = cobertura_referencias(man)
    rv = {}
    for t in TAREAS:
        rc, ver, _ = ejecutar_validador(REF / t / "resultado.json", REF / t / "salida", None)
        hist = json.loads((REF / t / "validacion_stdout.txt").read_text(encoding="utf-8"))
        rv[t] = {"rc": rc, "dictamen": ver.get("dictamen"), "n_fallos": ver.get("n_fallos"), "igual_a_la_validacion_historica": ver == hist}
    r["revalidacion_de_las_referencias"] = rv
    pil = leer(DATOS / "pilotos.json") if (DATOS / "pilotos.json").is_file() else None
    r["pilotos"] = {"fijados": [(p["tarea"], p["unidad"]) for p in (pil or {}).get("pilotos", [])], "iguales_a_la_regla": pil == regla_pilotos(man)}
    r["receta"] = {"tareas": len(receta()["tareas"])}
    r["cumple"] = (not malos and all(r["procedencia"].values()) and r["nucleo"]["iguales"] == len(nr) and not r["nucleo"]["otros_presentes"]
                   and r["cobertura"]["cumple"] and r["celdas_padre"]["cumple"] and r["referencias"]["cumple"]
                   and all(v["rc"] == 0 and v["igual_a_la_validacion_historica"] for v in rv.values()) and r["pilotos"]["iguales_a_la_regla"]
                   and r["receta"]["tareas"] == len(TAREAS))
    return r


# ================================================================================================ cálculo
def declarados() -> set:
    out = set()
    for n in ("fuentes_fam01.json", "fuentes_fam02.json", "fuentes_fam03.json", "fuentes_fam04.json"):
        if (BASE / n).is_file():
            out |= {x["archivo"] for x in leer(BASE / n).get("archivos", [])}
    return out


def lecturas(informe: dict) -> dict:
    dec = declarados()
    propios = ("src/", "reproducir.py", "datos/fam01/", "datos/fam04/", "fuentes_fam0", "catalogo.json")
    sin = [x for x in informe["en_el_paquete"] if x not in dec and not x.startswith(".venv-fam01/") and not x.startswith(propios)]
    return {"archivo": "archivos_leidos.json", "en_el_paquete": len(informe["en_el_paquete"]),
            "del_entorno_venv": sum(1 for x in informe["en_el_paquete"] if x.startswith(".venv-fam01/")),
            "aperturas_del_interprete": informe["aperturas_del_interprete"], "fuera_del_paquete_y_del_interprete": informe["fuera_del_paquete_y_del_interprete"],
            "sin_manifiesto": sin,
            "filas_padre_leidas": sum(1 for x in informe["en_el_paquete"] if x.startswith("referencias/fam01/originales/")),   # entradas F1 de L1-COORD
            "referencias_leidas": [x for x in informe["en_el_paquete"] if x.startswith("referencias/") and not x.startswith("referencias/fam01/originales/")]}


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
            "f2_alcance": "adoptada solo para FAM01; aquí se informa y no es requisito de FAM04", "python": platform.python_version(),
            "hash_seed": os.environ.get("PYTHONHASHSEED"), "hash_randomization": sys.flags.hash_randomization,
            "hilos": {k: os.environ.get(k) for k in f.HILOS}, "TZ": os.environ.get("TZ")}


def cobertura_contexto(ctx, CLX, MC, ml: dict, an: dict) -> dict:
    """Estados nacionales del contexto de esta base frente al anexo (sin evaluar λπ): tipos, número y secuencia de huellas shares_sha256
    (la identidad que exige el validador); estado_sha256 (identidad completa del NationalState, como cobertura_nacional.py) se informa."""
    out = {}
    for s, v in ml.items():
        sts = ctx.inp.national(s, v["pais"])
        esp = an["conjuntos"][s]["estados"]
        tipos = sorted({(x.get("kind") if isinstance(x, dict) else type(x).__name__) for x in sts})
        hs = [CLX.huella_shares(x.share_dict()) for x in sts if isinstance(x, MC.NationalState)]
        ids = []
        for x in sts:
            if isinstance(x, MC.NationalState):
                ident = {"country_id": x.country_id, "preregistration_id": x.preregistration_id, "channel": x.channel, "edition": x.edition,
                         "anchor_year": x.anchor_year, "label": x.label, "primitive_values": [[p, str(y), u] for p, y, u in x.primitive_values],
                         "shares": {k: str(y) for k, y in x.shares}, "joint_domain_sha256": x.joint_domain_sha256,
                         "dependencies": json.loads(json.dumps(list(x.dependencies), default=str))}
                ids.append(sha(F1().canon(ident)))
        out[s] = {"estados": len(sts), "tipos": tipos, "huellas_iguales_al_anexo": hs == [e["shares_sha256"] for e in esp],
                  "identidades_iguales_al_anexo": sum(1 for a, e in zip(ids, esp) if a == e["estado_sha256"]), "en_el_anexo": len(esp)}
    return out


def correr(tarea: str, salida: Path, unidad: str | None = None, tope: float = TOPE_TRABAJO) -> dict:
    """fam04-unidad: la tarea (o la unidad seleccionada) por calc_* de tarea_lote, en la carpeta NUEVA `salida`: salida/<productos>,
    resultado.json (esquema de tarea_lote), ejecucion.json y archivos_leidos.json. La validación y la comparación son otros pasos."""
    T0, c0 = time.time(), time.process_time()
    rastro = F1().Rastro()                       # desde el principio: también las lecturas previas al cálculo (fuentes, manifiesto, filas padre)
    need(tarea in TAREAS, "TAREA_NO_ADMITIDA: %s" % tarea)
    raw, man = manifiesto()
    sel = seleccion(man, tarea, unidad)
    malos = fuentes_alteradas(sin_referencias=True)
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam04.json; no se calcula): %s" % malos[:5])
    TOPE = float(tope) - HOLGURA
    need(TOPE > 0, "TOPE_INVALIDO")
    co = man["L1-COORD"]
    if sel is not None and tarea == "L1-COORD":
        co = dict(co, celdas=[c for c in co["celdas"] if c["clave_transformada_sha256"] in sel["claves"]])
    padres = autenticar_padres(co["celdas"]) if tarea == "L1-COORD" else None     # K1/G reutilizados (F1): antes de calcular
    need(padres is None or padres["cumple"], "CELDA_PADRE_NO_AUTENTICA (no se calcula): %s" % (padres or {}).get("malos"))
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    sal = salida.resolve()
    mods = pila()
    out = {"tarea": tarea, "modo": "produccion", "manifiesto_sha256": sha(raw), "tope_efectivo_s": TOPE, "sintetico": False,
           "codigo_sha256": {n: sha((LOTE / n).read_bytes()) for n in ("tarea_lote.py", "conexion_lambda.py", "conexion_frontera.py")}, "productos": []}

    def tope_():
        if time.time() - T0 > TOPE:
            raise TopeAlcanzado()
    ns = funciones_tarea(mods, sal / "salida", out, tope_)
    ctx, ej, t_ctx = None, {}, None
    a0 = time.time()
    try:
        if tarea == "L1-LAMBDA":
            ctx = contexto()
            t_ctx = round(time.time() - a0, 2)
            ml = {s: v for s, v in man["L1-LAMBDA"].items() if sel is None or s in sel["conjuntos"]}
            ej["cobertura_nacional_del_contexto"] = cobertura_contexto(ctx, mods["CLX"], mods["MC"], ml, anexo())
            a0 = time.time()
            filas = ns["calc_lambda"](ml, {s: ns["proveedor_real"](ctx, s, v["pais"]) for s, v in ml.items()})
            ns["producto"]("lambda_envolvente.jsonl", filas)
            out["llamadas_bridge"] = sum(f.get("llamadas_bridge", 0) for f in filas)
            ok = bool(filas) and all(f["estado"] == "ok" for f in filas)
            estado, motivo = ("completa", None) if ok else ("incompleta", "ENVOLVENTE_NO_CUBIERTA: %s" % [(f["conjunto"], f["variante"], f["estado"]) for f in filas if f["estado"] != "ok"])
        elif tarea == "L1-ELAST":
            fr_ = {k: v for k, v in man["L1-ELAST"]["fronteras"].items() if sel is None or v["frontier_id"] in sel["fronteras"]}
            filas = ns["calc_elast"](fr_)
            ns["producto"]("frontier_result.jsonl", filas)
            fallidas = [f["frontier_id"] + ":" + f["point_id"] for f in filas if f.get("computation_status") != "complete" or f.get("audit_status") not in ("pass", "limitation")]
            estado, motivo = ("completa", None) if filas and not fallidas else ("incompleta", "FILAS_CON_CALCULO_FALLIDO: %s" % fallidas[:5])
        else:
            import math
            ej["celdas_padre"] = padres
            techos, comp = ns["calc_coord"](co)
            ns["producto"]("coord_techos.jsonl", techos)
            ns["producto"]("coord_comparacion.jsonl", comp)
            malos_t = [t["clave_transformada_sha256"] for t in techos if t["estado"] != "complete" or t["C_2"] is None or t["error"] is None
                       or not math.isfinite(t["C_2"]) or not math.isfinite(t["error"])]
            estado, motivo = ("completa", None) if techos and not malos_t else ("incompleta", "TECHOS_INCOMPLETOS: %s" % malos_t[:5])
    except TopeAlcanzado:
        estado, motivo = "incompleta", "TOPE_ALCANZADO (lo parcial no se publica como terminado)"
    t_calc = round(time.time() - a0, 2)
    out.update(estado=estado, motivo=motivo, pared_s=round(time.time() - T0, 2))
    (sal / "resultado.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    informe = rastro.informe()
    (sal / "archivos_leidos.json").write_bytes((json.dumps(informe, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    ej.update({"tarea": tarea, "unidad": unidad, "seleccion": sel, "manifiesto_sha256": sha(raw), "etiqueta": ETIQUETA,
               "naturaleza": "cálculo: funciones calc_* de tarea_lote.py (bytes exactos) en la base limpia; sin puerta de producción (PUERTA-v1)",
               "adaptaciones": list(ADAPTACIONES), "reloj": "RELOJ-PILOTO-v1: tope interno %.0f s (= %.0f − %.0f); el límite externo lo pone el supervisor"
               % (TOPE, float(tope), HOLGURA), "resultado": {"estado": estado, "motivo": motivo, "productos": out["productos"]},
               "tiempos_s": {"contexto": t_ctx, "calculo": t_calc, "total": round(time.time() - T0, 2), "cpu": round(time.process_time() - c0, 2)},
               "contexto": None if ctx is None else {"identity_sha256": ctx.identity_sha256, "run_class": ctx.identity["run_class"]},
               "entorno": _entorno(ctx), "lecturas": lecturas(informe), "dependencias_fuera_de_la_biblioteca_estandar": F1().dependencias_cargadas()})
    ej["exito"] = estado == "completa"
    (sal / "ejecucion.json").write_bytes(json.dumps(ej, ensure_ascii=False, indent=1, sort_keys=True, default=str).encode("utf-8") + b"\n")
    return ej


# ================================================================================================ validación
def validador_adaptado() -> str:
    """VALIDADOR-v1: bytes exactos de validar_lote.py con las sustituciones declaradas (cada original, una sola vez)."""
    src = (LOTE / "validar_lote.py").read_bytes()
    need(sha(src) == CODIGO["validar_lote.py"], "VALIDADOR_DISTINTO")
    txt = src.decode("utf-8")
    for i, a, b in SUSTITUCIONES_VALIDADOR:
        need(txt.count(a) == 1, "SUSTITUCION_NO_UNICA: %s" % i)
        txt = txt.replace(a, b)
    return txt


def ejecutar_validador(res: Path, sal: Path, sel, cob: Path | None = None) -> tuple:
    """El validador como guion (argv como en la suite histórica: raíz, manifiesto, resultado, salida, anexo [, selección])."""
    txt = validador_adaptado()
    cob = DATOS / ANEXO[0] if cob is None else cob
    argv = [str(LOTE / "validar_lote.py"), str(INST), str(DATOS / MANIFIESTO[0]), str(res), str(sal), str(cob)] + ([json.dumps(sel)] if sel is not None else [])
    viejo, buf, rc = sys.argv, io.StringIO(), None
    sys.argv = argv
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(txt, str(LOTE / "validar_lote.py"), "exec"), {"__name__": "__main__", "__file__": str(LOTE / "validar_lote.py"), "__builtins__": builtins})
    except SystemExit as ex:
        rc = ex.code
    finally:
        sys.argv = viejo
    lineas = [x for x in buf.getvalue().splitlines() if x.strip()]
    return rc, (json.loads(lineas[-1]) if lineas else {}), buf.getvalue()


def productos_de(nueva: Path, res: dict) -> dict:
    return {p["archivo"]: sha_archivo(Path(nueva) / "salida" / p["archivo"]) for p in res.get("productos") or []}


def validar(nueva: Path, cob: Path | None = None) -> dict:
    """fam04-validar: SIN CÁLCULO. validar_lote.py (VALIDADOR-v1) sobre los bytes guardados de `nueva` (carpeta de fam04-unidad), con la
    selección registrada en su ejecución y el anexo de cobertura nacional del manifiesto."""
    t0 = time.time()
    nueva = Path(nueva).resolve()
    ej = leer(nueva / "ejecucion.json")
    rb = (nueva / "resultado.json").read_bytes()
    rc, ver, _ = ejecutar_validador(nueva / "resultado.json", nueva / "salida", ej.get("seleccion"), cob)
    return {"comando": "fam04-validar", "naturaleza": "validación sin cálculo de bytes guardados", "tarea": ej["tarea"], "unidad": ej.get("unidad"),
            "seleccion": ej.get("seleccion"), "origen": rel(nueva), "resultado_sha256": sha(rb), "productos_sha256": productos_de(nueva, json.loads(rb)),
            "validador": {"archivo": "nucleo_s6/lote1/validar_lote.py", "sha256": CODIGO["validar_lote.py"], "adaptacion": [x[0] for x in SUSTITUCIONES_VALIDADOR],
                          "adaptado_sha256": sha(validador_adaptado().encode("utf-8"))},
            "anexo": rel(cob) if cob is not None else "datos/fam04/" + ANEXO[0], "rc": rc, "veredicto": ver,
            "aceptada": rc == 0 and ver.get("aceptada") is True and ver.get("dictamen") == "completa_validada", "segundos": round(time.time() - t0, 3)}


# ================================================================================================ comparación
# COMPARACION-FAM04-v1. Contrato de comparadores, fila F04-LOTE1, contexto canónico (mismo perfil de entorno .venv-fam01; el comparador
# compara documentos y no certifica el entorno): CR-HASH-CANONICO (contenido científico idéntico: aquí, cada fila idéntica campo a campo con
# su serialización JSON) y CR-DISCRETOS (estados, clasificaciones, NA, claves y conteos exactos, con precedencia). CR-OBJETO-OTRO-ENTORNO
# (T1, T2_G) no se aplica: no es otro entorno. Las tolerancias internas del validador (T1) siguen siendo suyas y no se usan aquí.
# Por fila: cobertura de claves exacta (sin faltantes, ajenas ni duplicadas) y en el mismo orden; diferencias por campo, separadas en
# discretas (incluido valor frente a nulo) y numéricas. En resultado.json: tarea, modo, sintetico, estado y motivo se comparan; manifiesto y
# código son identidades (iguales a los del lote); productos y llamadas_bridge se derivan de las filas; tope_efectivo_s es presupuesto (se
# compara); pared_s es operativo (se muestra).
CLAVE_FILA = {"frontier_result.jsonl": ("frontier_id", "point_id", "side"), "lambda_envolvente.jsonl": ("conjunto", "variante"),
              "coord_techos.jsonl": ("clave_transformada_sha256",), "coord_comparacion.jsonl": ("unidad",)}
NUMERICOS = {"frontier_result.jsonl": {"tau_d", "tau_f", "B_d", "B_f", "R", "B_pot", "CS", "eps_dd", "eps_df", "eps_fd", "eps_ff", "s_P"},
             "lambda_envolvente.jsonl": {"lambda_max", "lambda_min", "K1_sobre_Q_min", "K1_sobre_Q_max", "theta_W_en_max", "theta_W_en_min", "lambda"},
             "coord_techos.jsonl": {"C_2", "error"}, "coord_comparacion.jsonl": {"K1_reutilizado", "G_padre", "C2_coord", "G_coord"}}


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


def en_unidad(n: str, fila: dict, sel, man: dict) -> bool:
    if sel is None:
        return True
    if n == "frontier_result.jsonl":
        return fila.get("frontier_id") in sel["fronteras"]
    if n == "lambda_envolvente.jsonl":
        return fila.get("conjunto") in sel["conjuntos"]
    if n == "coord_techos.jsonl":
        return fila.get("clave_transformada_sha256") in sel["claves"]
    return fila.get("unidad") in {c["unidad"] for c in man["L1-COORD"]["celdas"] if c["clave_transformada_sha256"] in sel["claves"]}


def comparar_producto(n: str, nuevas_l: list, ref_l: list) -> dict:
    kf = CLAVE_FILA[n]
    nuevas, refs = [json.loads(x) for x in nuevas_l], [json.loads(x) for x in ref_l]
    kn, kr = [tuple(f.get(k) for k in kf) for f in nuevas], [tuple(f.get(k) for k in kf) for f in refs]
    dn, dr = dict(zip(kn, nuevas)), dict(zip(kr, refs))
    cob = {"filas_nuevas": len(nuevas), "filas_referencia": len(refs), "faltan": [list(k) for k in kr if k not in dn][:5],
           "ajenas": [list(k) for k in kn if k not in dr][:5], "duplicadas": (len(kn) - len(set(kn))) + (len(kr) - len(set(kr))), "mismo_orden": kn == kr}
    disc, num = [], []
    for k in kr:
        if k not in dn:
            continue
        hn, hr = hojas(dn[k]), hojas(dr[k])
        for p in sorted(set(hn) | set(hr)):
            a, b = hn.get(p, "<ausente>"), hr.get(p, "<ausente>")
            if json.dumps(a) == json.dumps(b):
                continue
            d = {"fila": list(k), "puntero": p, "nueva": a, "referencia": b}
            numerico = p.split("/")[-1] in NUMERICOS[n] and None not in (a, b) and "<ausente>" not in (a, b)   # valor frente a nulo (NA): discreta
            (num if numerico else disc).append(d)
    return {"cobertura": cob, "lineas_identicas": nuevas_l == ref_l, "n_discretas": len(disc), "n_numericas": len(num),
            "discretas": disc[:20], "numericas": num[:20]}


def comparar(tarea: str, nueva: Path, validacion: Path) -> dict:
    """fam04-comparar: salida de fam04-unidad (`nueva`) y su validación (`validacion`, de fam04-validar) frente a la ejecución aceptada de
    rem112 restringida a la misma unidad (o completa)."""
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
    cat = productos_catalogo()
    ref_res = leer(REF / tarea / "resultado.json")
    objetos = {}
    for n in PRODUCTOS[tarea]:
        fref = REF / tarea / "salida" / n
        if sha_archivo(fref) != cat.get(n):
            mot.append("REFERENCIA_ALTERADA_O_AJENA: %s" % n)
            continue
        decl = {p["archivo"]: p for p in res.get("productos") or []}.get(n)
        fn = nueva / "salida" / n
        if decl is None or sha_archivo(fn) != decl.get("sha256"):
            mot.append("PRODUCTO_AUSENTE_O_ALTERADO: %s" % n)
            continue
        ref_l = [x for x in fref.read_text(encoding="utf-8").splitlines() if x.strip() and en_unidad(n, json.loads(x), sel, man)]
        nue_l = [x for x in fn.read_text(encoding="utf-8").splitlines() if x.strip()]
        o = comparar_producto(n, nue_l, ref_l)
        c = o["cobertura"]
        if c["faltan"] or c["ajenas"] or c["duplicadas"] or not c["mismo_orden"] or c["filas_nuevas"] != c["filas_referencia"] or not ref_l:
            mot.append("COBERTURA_DISTINTA (CR-DISCRETOS): %s" % n)
        if o["n_discretas"]:
            mot.append("DIFERENCIA_DISCRETA (CR-DISCRETOS, precedencia): %s %s" % (n, [d["puntero"] for d in o["discretas"][:4]]))
        if o["n_numericas"]:
            mot.append("DIFERENCIA_NUMERICA (CR-HASH-CANONICO): %s %s" % (n, [d["puntero"] for d in o["numericas"][:4]]))
        o["filas_decl"] = decl.get("filas")
        objetos[n] = o
    rr = {}
    for k in ("tarea", "modo", "sintetico", "estado", "motivo", "tope_efectivo_s"):
        rr[k] = {"nueva": res.get(k), "referencia": ref_res.get(k), "igual": res.get(k) == ref_res.get(k)}
        if not rr[k]["igual"]:
            mot.append("RESULTADO_DISTINTO: %s" % k)
    ident = {"manifiesto_sha256": res.get("manifiesto_sha256") == ref_res.get("manifiesto_sha256") == MANIFIESTO[1],
             "codigo_sha256": res.get("codigo_sha256") == ref_res.get("codigo_sha256")}
    if not all(ident.values()):
        mot.append("IDENTIDAD_DE_MANIFIESTO_O_CODIGO_DISTINTA: %s" % [k for k, v in ident.items() if not v])
    deriv = {}
    if tarea == "L1-LAMBDA":
        filas_r = [json.loads(x) for x in (REF / tarea / "salida/lambda_envolvente.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
        filas_n = leer_jsonl(nueva / "salida/lambda_envolvente.jsonl") if (nueva / "salida/lambda_envolvente.jsonl").is_file() else []
        deriv["llamadas_bridge"] = {"nueva": res.get("llamadas_bridge"), "suma_filas_nuevas": sum(f["llamadas_bridge"] for f in filas_n),
                                    "referencia_unidad": sum(f["llamadas_bridge"] for f in filas_r if en_unidad("lambda_envolvente.jsonl", f, sel, man)),
                                    "referencia_tarea": ref_res.get("llamadas_bridge")}
        if not (deriv["llamadas_bridge"]["nueva"] == deriv["llamadas_bridge"]["suma_filas_nuevas"] == deriv["llamadas_bridge"]["referencia_unidad"]):
            mot.append("LLAMADAS_BRIDGE_DISTINTAS")
    if sel is None:
        deriv["productos"] = {"iguales_a_la_referencia": res.get("productos") == ref_res.get("productos")}
        if not deriv["productos"]["iguales_a_la_referencia"]:
            mot.append("PRODUCTOS_DISTINTOS_DE_LA_TAREA_DE_REFERENCIA")
    return {"comando": "fam04-comparar", "tarea": tarea, "unidad": ej.get("unidad"), "seleccion": sel, "regla": "COMPARACION-FAM04-v1 (src/fam04.py)",
            "criterios": ["CR-HASH-CANONICO (mismo perfil de entorno; exacta)", "CR-DISCRETOS (precedencia)"], "no_aplicado": "CR-OBJETO-OTRO-ENTORNO (T1, T2_G): no es otro entorno",
            "referencia": {"ejecucion": "referencias/fam04/rem112/" + tarea, "productos": {n: cat.get(n) for n in PRODUCTOS[tarea]},
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
        d = "salidas/fam04/<ejecucion>/" + t
        ordenes.append({"tarea": t, "unidades": len(u[t]), "productos": list(PRODUCTOS[t]), "referencia": "referencias/fam04/rem112/" + t,
                        "ordenes": ["reproducir.py fam04-unidad --tarea %s --salida %s" % (t, d),
                                    "reproducir.py fam04-validar --nueva %s --salida %s.validacion.json" % (d, d),
                                    "reproducir.py fam04-comparar --tarea %s --nueva %s --validacion %s.validacion.json --salida %s.comparacion.json" % (t, d, d, d)]})
    estados = {s: c["n_estados"] for s, c in an["conjuntos"].items()}
    return {"comando": "fam04-receta", "estado": "receta completa preparada; NO ejecutada (el lote pertenece al Paso 3)", "manifiesto_sha256": sha(raw),
            "orden": list(TAREAS), "tareas": ordenes,
            "cobertura": {"L1-ELAST": {"fronteras": len(u["L1-ELAST"]), "nodos": man["L1-ELAST"]["puntos_totales_frontier_n4"],
                                       "filas": "una «point» por nodo y left_limit/right_limit si y solo si hay kink"},
                          "L1-LAMBDA": {"conjuntos": len(u["L1-LAMBDA"]), "filas": 2 * len(u["L1-LAMBDA"]), "estados_nacionales": estados,
                                        "llamadas_bridge": sum(4 * e for e in estados.values())},
                          "L1-COORD": {"claves": len(u["L1-COORD"]), "techos": len(u["L1-COORD"]), "celdas_padre": len(man["L1-COORD"]["celdas"]),
                                       "comparaciones": len(man["L1-COORD"]["celdas"])}},
            "previo": ["reproducir.py fam04-comprobar --salida salidas/fam04/<nuevo>.json (sin cálculo científico)"],
            "ejecucion": {"procesos": "una tarea a la vez (una_tarea_activa del paquete), sin reintentos", "tope_trabajo_s": TOPE_TRABAJO,
                          "reloj_interno_s": TOPE_TRABAJO - HOLGURA, "tope_validacion_s": TOPE_VALIDACION,
                          "lanzador": "supervisor que termina el árbol de procesos (el mismo de los pilotos), con el tope de trabajo como límite externo",
                          "parada": "si una tarea no queda completa y validada, la siguiente no se lanza (paquete: parada)",
                          "duracion": "sin estimación: los pilotos no la permiten"},
            "F1": {"reutilizado": ["selección del lote (LOTE1_MANIFIESTO.json; la selección no se re-ejecuta)",
                                   "anexo de cobertura nacional (preparación hasta selección, sin λπ)",
                                   "K1 y G de las 192 celdas padre (manifiesto; filas autenticadas en referencias/fam01/originales)",
                                   "núcleo paper2b, D7, contratos y datos nacionales de FAM01"],
                   "se_genera_de_nuevo": ["filas frontier_result de las 6 fronteras (70 nodos y sus laterales)", "4 envolventes λπ (72 evaluaciones de macro.bridge)",
                                          "12 techos C2' sobre las claves transformadas", "192 comparaciones G_COORD = C2' − K1"],
                   "solo_para_comparar": ["productos y resultados de la ejecución aceptada rem112 (= objetos del catálogo F04-LOTE1)"],
                   "no_cubre": ["FAM05 (lote 2)", "FAM07 (alcance adicional de COORD)"]},
            "pilotos": leer(DATOS / "pilotos.json") if (DATOS / "pilotos.json").is_file() else None}
