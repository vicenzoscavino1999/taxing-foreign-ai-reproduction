"""Revisión local, piloto P7, operaciones FAM12 (cuatro K1 de P7, suplemento P7 y Q local m=1/2) y FAM01 (listas y marco R3,
carga del núcleo S6, tarea de una o varias unidades R2/R3 con validación productiva, comparación, NA documental y receta completa sin ejecutar)
y FAM02 (R1 global: plan de las 18 tareas, comprobación sin cálculo, tarea C o hojas seleccionadas con validación, comparación y receta)
y FAM03 (quiebres PROD1/PROD2 y Q histórica PROD3: datos sin cálculo, plan, comprobación, una tarea con validación productiva,
revalidación sin cálculo, comparación con el árbol aceptado y receta completa)
y FAM04 (lote 1: L1-ELAST, L1-LAMBDA, L1-COORD: unidades y pilotos, comprobación, una tarea o unidad, validación por validar_lote,
comparación con la ejecución aceptada y receta completa)
y FAM05 (lote 2 con el núcleo C0: L1-ELAST con el suplemento histórico y L1-LAMBDA; mismos comandos que FAM04)
y FAM06 (E4: mallas G/N con el manifiesto E4 y la misma ruta que FAM05; conciliación de los 391 pares con el productor histórico y su comparación)
y FAM07 (COORD del lote 2: tarea de la partición con techos certificados, validación, ensamblado de las 1.532 comparaciones sobre tareas nuevas o
guardadas, verificación de los 20 reutilizados y de las 192 previas, comparación y receta)
y FAM08 (ENF: mallas eta_f/2, pares con el padre, techos ABL-ENF T1–T6 con el caso no alcanzado y su certificado, integración de 26 claves y
1.724 celdas sobre entradas nuevas, guardadas o mixtas, comparación y receta)
y FAM11 (COV: techos ABL-COV T1–T6, ensamblado y conciliación de 1.728 afirmaciones; COV12: B1 con U_C2 certificado y B2 con L_K1 global
sobre el B1 nuevo validado; validación, comparación y receta)
y FAM09 (T8: filas históricas preservadas, emisión λ, captura por fila, techo alto con su validación U36 y emisión de 35 filas, cota C5B;
etapas encadenadas por salidas nuevas validadas, comparación con rem138/rem140/rem141/rem147 y receta)
y FAM10 (tabla final de Exp8: ENF por afirmación, síntesis con P7 y Q local, integración de las doce COV con la lectura B1 → B2; orden única
fam10-tabla con validación por etapa y comparación con rem147/rem160/rem171)
y FAM13 (tablas y validaciones históricas: T1/T2 rem107 y T7 rem108 con U59, validaciones E1235/E1_i2 autenticadas con recálculo aritmético,
matriz v4 de Exp0 con la A2 de rem134; integridad de los 40 públicos S1, el mapa rem187 y su fe de erratas; orden única fam13-reproducir)
y FAM14 (los 391 pares G/N de rem174 regenerados con U62 y validados con la ligadura G/N de U63 rem175, comparados por par y lado con la
cobertura aceptada; integridad de esa cobertura, del registro §18.7 y del derivado público de la adopción rem176; orden única fam14-reproducir)
y el comando general (las 39 operaciones del catálogo conectadas a las llamadas de las recetas: plan sin cálculo, piloto FAM08 + FAM11 +
FAM12 -> FAM10 y modo completo del Paso 3, solo si se elige expresamente; balance por operación).
Ningún cálculo se ejecuta al importar este archivo."""
import argparse
import ast
from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import sysconfig
import time

BASE = Path(__file__).resolve().parent
MANIFIESTOS = ("fuentes_p7.json", "fuentes_fam12.json")
MODULOS_K1 = ("p7_external", "p7_macro", "p7_calculo")


def leer(ruta):
    return json.loads(ruta.read_text(encoding="utf-8"))


def revisar():
    errores = []
    for manifiesto in MANIFIESTOS:
        fuentes = leer(BASE / manifiesto)
        for nombre, esperado in fuentes["archivos_locales"].items():
            archivo = BASE / nombre
            if not archivo.is_file():
                errores.append(nombre + ": falta")
            elif hashlib.sha256(archivo.read_bytes()).hexdigest() != esperado:
                errores.append(nombre + ": huella distinta")
    for archivo in (BASE / "src").glob("*.py"):
        ast.parse(archivo.read_text(encoding="utf-8"), filename=str(archivo))
    return errores


def cargar(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, BASE / "src" / archivo)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = modulo
    spec.loader.exec_module(modulo)
    return modulo


def piloto():
    entradas = leer(BASE / "datos/p7.json")
    external = cargar("p7_external", "external.py")
    macro = cargar("p7_macro", "macro.py")
    calculo = cargar("p7_calculo", "p7_calculo.py")
    resultados = {
        unidad: calculo.derivar_k1(datos, external, macro)
        for unidad, datos in entradas.items()
    }
    referencias = leer(BASE / "referencias/p7.json")
    diferencias = []
    if set(resultados) != set(referencias):
        diferencias.append("unidades distintas")
    for unidad, referencia in referencias.items():
        obtenido = resultados.get(unidad, {})
        for campo, esperado in referencia["valores_hex"].items():
            valor = obtenido.get(campo)
            if not isinstance(valor, float) or valor.hex() != esperado:
                diferencias.append(f"{unidad}: {campo}")
    return {
        "alcance": "Dos K1 de P7 desde entradas ligadas guardadas",
        "python": sys.version,
        "resultados": resultados,
        "comparacion_exacta": not diferencias,
        "diferencias": diferencias,
    }


# ---------------------------------------------------------------- utilidades de comparación (interfaz, sin lógica científica)

def leer_jsonl(ruta):
    with ruta.open(encoding="utf-8") as fuente:
        return [json.loads(linea) for linea in fuente if linea.strip()]


def normal(x):
    """Forma JSON del objeto (los float binary64 se conservan exactos al ida y vuelta)."""
    return json.loads(json.dumps(x, ensure_ascii=False, allow_nan=False))


def linea(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def diferencias_json(a, b, ruta=""):
    """Rutas donde dos objetos JSON difieren; números por igualdad exacta y tipo."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out += [f"{ruta}/{k}: falta"] if (k not in a or k not in b) else diferencias_json(a[k], b[k], f"{ruta}/{k}")
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{ruta}: longitud {len(a)} frente a {len(b)}"]
        return [d for i, (x, y) in enumerate(zip(a, b)) for d in diferencias_json(x, y, f"{ruta}/{i}")]
    return [] if (type(a) is type(b) and a == b) else [ruta or "/"]


def comparar_filas(obtenidas, referencia, clave):
    """Comparación campo a campo de dos listas de filas en el mismo orden."""
    obtenidas = normal(obtenidas)
    if obtenidas == referencia:
        return {"filas": len(obtenidas), "filas_distintas": 0, "diferencias": []}
    if len(obtenidas) != len(referencia):
        return {"filas": len(obtenidas), "filas_distintas": None, "diferencias": [f"{len(obtenidas)} filas frente a {len(referencia)} de referencia"]}
    difs = []
    for x, r in zip(obtenidas, referencia):
        difs += [f"{clave(r)}: {d}" for d in diferencias_json(x, r)]
    distintas = sum(x != r for x, r in zip(obtenidas, referencia))
    return {"filas": len(obtenidas), "filas_distintas": distintas, "diferencias": difs[:20], "diferencias_totales": len(difs)}


def dependencias():
    """Módulos cargados fuera de la biblioteca estándar del intérprete y fuera del paquete."""
    rutas = sysconfig.get_paths()
    sitios = [Path(rutas[k]).resolve() for k in ("purelib", "platlib")]
    estandar = [Path(rutas[k]).resolve() for k in ("stdlib", "platstdlib")] + [Path(sys.base_prefix, "DLLs").resolve()]
    fuera, propios = [], []
    for nombre, modulo in sorted(sys.modules.items()):
        archivo = getattr(modulo, "__file__", None)
        if not archivo:
            continue
        p = Path(archivo).resolve()
        if p.is_relative_to(BASE):
            propios.append(nombre)
        elif any(p.is_relative_to(s) for s in sitios) or not any(p.is_relative_to(s) for s in estandar):
            fuera.append(nombre)
    return {"fuera_de_stdlib_y_paquete": fuera, "modulos_del_paquete": propios}


# ---------------------------------------------------------------- P7: cuatro K1

def p7_k1():
    """Cuatro K1 de P7 con derivar_k1 (sin cambios) desde las entradas ligadas guardadas; comparación binary64 exacta."""
    t0 = time.perf_counter()
    entradas = leer(BASE / "datos/p7.json")
    reutilizados = leer(BASE / "datos/p7_k1_reutilizados.json")
    referencias = leer(BASE / "referencias/p7.json")
    ref_reutilizados = leer(BASE / "referencias/p7_k1_reutilizados.json")
    assert not set(entradas) & set(reutilizados) and not set(referencias) & set(ref_reutilizados), "UNIDADES_DUPLICADAS"
    entradas.update(reutilizados)
    referencias.update(ref_reutilizados)
    external = cargar("p7_external", "external.py")
    macro = cargar("p7_macro", "macro.py")
    calculo = cargar("p7_calculo", "p7_calculo.py")
    resultados = {unidad: calculo.derivar_k1(datos, external, macro) for unidad, datos in sorted(entradas.items())}
    diferencias, comparados = [], 0
    if set(resultados) != set(referencias) or len(resultados) != 4:
        diferencias.append("unidades distintas de las cuatro de referencia")
    for unidad, referencia in sorted(referencias.items()):
        obtenido = resultados.get(unidad, {})
        for campo, esperado in sorted(referencia["valores_hex"].items()):
            comparados += 1
            valor = obtenido.get(campo)
            if not isinstance(valor, float) or valor.hex() != esperado:
                diferencias.append(f"{unidad}: {campo}")
    for r in resultados.values():
        r["K1_hex"] = r["K1"].hex() if isinstance(r["K1"], float) else None
    return {"operacion": "p7-k1", "alcance": "Cuatro K1 de P7 (S1-N-df, S1-G-df, S1-N-f, S1-G-d) desde entradas ligadas guardadas",
            "python": sys.version, "resultados": resultados, "valores_comparados": comparados,
            "comparacion_exacta": not diferencias, "diferencias": diferencias, "segundos": round(time.perf_counter() - t0, 3)}


# ---------------------------------------------------------------- P7: suplemento de siete afirmaciones

def p7_suplemento():
    """Recalcula los cuatro K1 y genera las siete filas del suplemento con la regla i5 (eps = 1/100, desigualdades estrictas)."""
    t0 = time.perf_counter()
    k1 = p7_k1()
    if not k1["comparacion_exacta"]:
        return {"operacion": "p7-suplemento", "concordante": False, "motivo": "los cuatro K1 no coinciden con su referencia",
                "k1": k1, "segundos": round(time.perf_counter() - t0, 3)}
    valores_k1 = {u: float.fromhex(r["K1_hex"]) for u, r in k1["resultados"].items()}
    datos = leer(BASE / "datos/p7_suplemento.json")
    G = cargar("conciliar_cov", "conciliar_cov.py")
    S = cargar("p7_suplemento", "p7_suplemento.py")
    filas = S.conciliar_siete(datos, valores_k1, G)
    resumen = S.resumen(filas)
    referencia = leer_jsonl(BASE / "referencias/p7_suplemento.jsonl")
    comparacion = comparar_filas(filas, referencia, lambda r: r["afirmacion"])
    cuerpo = "".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in filas).encode("utf-8")
    comparacion["identidad_bytes_con_referencia"] = cuerpo == (BASE / "referencias/p7_suplemento.jsonl").read_bytes()
    controles = {
        "siete_afirmaciones": len(filas) == 7,
        "cuatro_unidades": {f["unidad"] for f in filas} == set(valores_k1) and len(valores_k1) == 4,
        "COV_inconclusa_preservada_7": resumen["canal_COV"] == {"inconclusa_preservada": 7},
        "ENF_inconclusa_preservada_7": resumen["canal_ENF"] == {"inconclusa_preservada": 7},
        "categorias_originales_conservadas": [f["categoria_original"] for f in filas] == [a["categoria_original"] for a in datos["afirmaciones"]],
        "eps_1_100": G.EPS == Fraction(1, 100) and datos["eps"] == "1/100",
        "K1_de_esta_corrida": all(f["K1"] == valores_k1[f["unidad"]] for f in filas),
    }
    concordante = not comparacion["diferencias"] and all(controles.values())
    return {"operacion": "p7-suplemento", "alcance": "Siete afirmaciones P7 desde K1 recalculados y techos COV/ENF aceptados (no recalculados)",
            "python": sys.version, "k1": {u: {"K1": valores_k1[u], "K1_hex": k1["resultados"][u]["K1_hex"]} for u in sorted(valores_k1)},
            "k1_valores_comparados": k1["valores_comparados"], "k1_comparacion_exacta": True,
            "resumen": resumen, "controles": controles, "comparacion_referencia": comparacion,
            "origen_lado_presente": {c: dict(Counter(f["canales"][c]["presente_origen"] for f in filas)) for c in ("COV", "ENF")},
            "tipo_K1": dict(Counter(f["K1_tipo"] for f in filas)),
            "dependencias": dependencias(), "concordante": concordante, "segundos": round(time.perf_counter() - t0, 3), "filas": filas}


# ---------------------------------------------------------------- Q local, m = 1/2, versiones contrato y conservadora

def q_local(salida):
    """Aritmética exacta G(m) = C_2 − m·K1 sobre las posiciones guardadas; no usa el modelo, K1, bridge, GridCell.Q ni supremos."""
    t0 = time.perf_counter()
    lineas = leer_jsonl(BASE / "datos/q_local.jsonl")
    cabecera, filas = lineas[0], [x["fila"] for x in lineas[1:] if x["tipo"] == "posicion"]
    assert cabecera["tipo"] == "cabecera" and cabecera["posiciones"] == len(filas) == len(lineas) - 1, "ENTRADAS_Q_INCOMPLETAS"
    m = Fraction(cabecera["m"])
    G = cargar("conciliar_cov", "conciliar_cov.py")
    Q = cargar("q_local", "q_local.py")
    p7 = leer(BASE / "datos/p7_suplemento.json")
    ref_conc = leer(BASE / "referencias/q_local_conciliacion.json")
    versiones, porA_de = {}, {}
    salida.mkdir(parents=True)
    for tarea in cabecera["tareas"]:
        version = tarea["version"]
        pos, porA = Q.evaluar(filas, m, version, G)
        conteos = Q.contar(porA)
        porA_de[version] = porA
        ref = leer_jsonl(BASE / f"referencias/q_local_{version}.jsonl")
        ref_pos = [x["fila"] for x in ref if x["tipo"] == "posicion"]
        ref_af = [x["fila"] for x in ref if x["tipo"] == "afirmacion"]
        comp_pos = comparar_filas(pos, ref_pos, lambda r: f'{r["afirmacion"]} {r["lado"]}')
        comp_af = comparar_filas(porA, ref_af, lambda r: r["afirmacion"])
        cuerpo = "".join(linea({"fila": x, "tipo": "posicion"}) for x in normal(pos)) + "".join(linea({"fila": x, "tipo": "afirmacion"}) for x in normal(porA))
        with (salida / f"q_local_{version}.jsonl").open("x", encoding="utf-8", newline="\n") as destino:
            destino.write(linea({"tipo": "cabecera", "operacion": "q-local", "version": version, "m": str(m), "conteos": conteos}))
            destino.write(cuerpo)
        ref_cuerpo = b"".join((BASE / f"referencias/q_local_{version}.jsonl").read_bytes().splitlines(keepends=True)[1:])
        c_inc, c_rob = conteos["inconclusa"], conteos["robusta"]
        versiones[version] = {
            "tarea": tarea["tarea"], "posiciones": len(pos), "afirmaciones": len(porA), "conteos": conteos,
            "conteos_iguales_a_referencia": normal(conteos) == ref[0]["conteos"],
            "comparacion_posiciones": comp_pos, "comparacion_afirmaciones": comp_af,
            "cuerpo_identico_en_bytes_a_referencia": cuerpo.encode("utf-8") == ref_cuerpo,
            "controles": {
                "afirmaciones_1728": len(porA) == 1728, "posiciones_3456": len(pos) == 3456,
                "inconclusas_preservadas_1712": c_inc["afirmaciones"] == 1712 and c_inc["canal"] == {"inconclusa_preservada": 1712},
                "robustas_padre_16_aparte": c_rob["afirmaciones"] == 16 and c_rob["canal"] == {"robustez_refutada_por_testigo_sup": 16},
                "categorias_originales_intactas": Q.categorias_intactas(filas, porA),
            }}
    difs = Q.diferencias_entre_versiones(porA_de["contrato"], porA_de["conservadora"])
    intactas = Q.categorias_intactas(filas, porA_de["contrato"], porA_de["conservadora"])
    claves_padre = [(f["afirmacion"], f["lado"]) for f in filas if f.get("origen") in Q.ORIGENES_PADRE]
    pos_p7 = [f for f in filas if f.get("origen") == "suplemento_P7_lado_padre_faltante"]
    af_p7 = [a["afirmacion"] for a in p7["afirmaciones"]]
    incorporacion_p7 = {
        "posiciones_P7": len(pos_p7), "afirmaciones_P7_distintas": len({f["afirmacion"] for f in pos_p7}),
        "coinciden_con_las_siete_del_suplemento": sorted(f["afirmacion"] for f in pos_p7) == sorted(af_p7),
        "lado_P7_es_el_faltante": all(f["lado"] == next(a["lado_faltante"] for a in p7["afirmaciones"] if a["afirmacion"] == f["afirmacion"]) for f in pos_p7),
        "sin_posiciones_padre_repetidas": len(claves_padre) == len(set(claves_padre)),
    }
    conciliacion = {
        "diferencias_contrato_vs_conservadora": difs, "categorias_originales_intactas": intactas,
        "igual_a_referencia": (difs == ref_conc["diferencias_contrato_vs_conservadora"] and intactas == ref_conc["categorias_originales_intactas"]
                               and all(normal(versiones[t["version"]]["conteos"]) == ref_conc["tareas"][t["tarea"]]["conteos"] for t in cabecera["tareas"])),
    }
    p7_una_vez = (incorporacion_p7["posiciones_P7"] == 7 and incorporacion_p7["afirmaciones_P7_distintas"] == 7
                  and incorporacion_p7["coinciden_con_las_siete_del_suplemento"] and incorporacion_p7["lado_P7_es_el_faltante"]
                  and incorporacion_p7["sin_posiciones_padre_repetidas"])
    deps = dependencias()
    sin_modelo = not [n for n in MODULOS_K1 if n in sys.modules]
    versiones_ok = all(v["conteos_iguales_a_referencia"] and not v["comparacion_posiciones"]["diferencias"]
                       and not v["comparacion_afirmaciones"]["diferencias"] and all(v["controles"].values()) for v in versiones.values())
    concordante = versiones_ok and conciliacion["igual_a_referencia"] and not difs and intactas and p7_una_vez and sin_modelo
    resumen = {"operacion": "q-local", "alcance": "Q local m=1/2, versiones contrato y conservadora, aritmética exacta sobre posiciones guardadas",
               "python": sys.version, "m": str(m), "versiones": versiones, "conciliacion": conciliacion, "incorporacion_P7": incorporacion_p7,
               "sin_modelo_K1_bridge_ni_supremos": sin_modelo, "dependencias": deps, "concordante": concordante,
               "segundos": round(time.perf_counter() - t0, 3)}
    with (salida / "resumen.json").open("x", encoding="utf-8") as destino:
        json.dump(resumen, destino, ensure_ascii=False, indent=2, allow_nan=False)
        destino.write("\n")
    return resumen


# ---------------------------------------------------------------- línea de órdenes

def escribir(salida, resultado):
    salida.parent.mkdir(parents=True, exist_ok=True)
    with salida.open("x", encoding="utf-8") as destino:
        json.dump(resultado, destino, ensure_ascii=False, indent=2, allow_nan=False)
        destino.write("\n")


FAM01 = ("fam01-listas", "fam01-comprobar", "fam01-unidad", "fam01-comparar", "fam01-na", "fam01-receta")
MAX_POR_TAREA = 20      # variante agrupada: unidades por proceso (techos compartidos), para acotar tiempo y longitud de la orden

# GRUPOS-TECHO-C2-v1: las unidades de una misma selección y clave estructural cara van en un mismo proceso fam01-unidad (--unidad
# repetido). El primer cálculo del techo C2 queda en la memoria del proceso (EjecutorSeleccion.techos -> Run.techos_compartidos) y las
# demás unidades lo reutilizan. No cambia presupuestos, cotas, tolerancias, F2, validación ni comparación.
REGLA_GRUPOS_TECHO = "GRUPOS-TECHO-C2-v1"
UMBRAL_TECHO_CARO_S = 300.0     # una clave es cara si algún documento original suyo pagó un techo (tiempos_s.techo_s) de más de 300 s
FACTOR_FRIO = 3.5               # margen sobre el techo y la macro históricos: en frío aquí 1,56–1,91 veces; con 12 procesos, hasta 1,73 veces más
POR_UNIDAD_GRUPO_S = 300.0      # cada unidad del grupo: celda (plazo fiscal de reloj de 120 s, igual que en el original), validación y escritura

# TECHO-FRIO-MEDIDO-F01R2-v1: dos claves de R2 no registran en sus originales el coste de su techo en frío, porque cuando se escribieron el
# techo ya estaba en la memoria del proceso (techo_s ≤ 10,021 s y 0,376 s). En la corrida completa del Paso 3 sus unidades agotaron el
# límite ordinario de 600 s en la fase del techo. Su techo y su macro en frío se midieron en la recuperación aceptada (2026-11-20; llamadas
# completas, validadas y «aceptada_comparacion_limpia_con_F2»). Con esos valores cada clave es cara y su grupo usa la fórmula de
# GRUPOS-TECHO-C2-v1. Estos grupos van después de los demás. No cambia cálculos, presupuestos, cotas, tolerancias, F2, validación ni
# comparación: solo qué unidades comparten proceso y con qué límite externo.
REGLA_TECHO_MEDIDO = "TECHO-FRIO-MEDIDO-F01R2-v1"
TECHOS_MEDIDOS_EN_FRIO = {
    ("R2", "3eb7dcff0c8a69915e1cc00a73c687d5ce3f01ed9eddc7067090eb70a4cf2efd"): {
        "techo_s": 965.48, "macro_s": 122.642,
        "medicion": "recuperación del Paso 3, llamada medida_3eb7dcff_02 (P01233, una unidad, 1.212,0 s, prioridad alta); después, las otras "
                    "14 unidades de la clave en un proceso (2.710,2 s); todas completas, validadas y aceptadas con F2"},
    ("R2", "2fbaf756201eeb09ea1a64403122c4d62c486e609d18564930f868359298d49f"): {
        "techo_s": 848.32, "macro_s": 1.676,
        "medicion": "recuperación del Paso 3, llamada medida_2fbaf756_02 (P02119, una unidad, 974,0 s, prioridad alta); completa, validada "
                    "y aceptada con F2"},
}


def prioridad_alta():
    """PRIORIDAD-ALTA-v1. En Windows, pide que este proceso no sea estrangulado por ahorro de energía (EcoQoS): SetProcessInformation con
    ProcessPowerThrottling, ControlMask = EXECUTION_SPEED y StateMask = 0. Sin esto, un intérprete en segundo plano llegó a recibir un cuarto
    de núcleo (GT05 y GT08 agotaron su límite en la corrida del Paso 3). No cambia ningún cálculo; si falla, se sigue igual."""
    import os
    if os.name != "nt":
        return None
    try:
        import ctypes

        class Estado(ctypes.Structure):
            _fields_ = [("Version", ctypes.c_ulong), ("ControlMask", ctypes.c_ulong), ("StateMask", ctypes.c_ulong)]

        k = ctypes.WinDLL("kernel32", use_last_error=True)
        k.GetCurrentProcess.restype = ctypes.c_void_p
        k.SetProcessInformation.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_ulong)
        k.SetProcessInformation.restype = ctypes.c_int
        e = Estado(1, 1, 0)
        return bool(k.SetProcessInformation(k.GetCurrentProcess(), 4, ctypes.byref(e), ctypes.sizeof(e)))
    except Exception:
        return False


def _planificacion_fam01(F, unidades):
    """Clave estructural, frontera y tiempos históricos de cada unidad numérica, leídos de su documento original autenticado por
    indice_originales.json. Solo deciden qué unidades comparten proceso y con qué límite externo; no entran en el cálculo, la validación
    ni la comparación."""
    indice = F.leer_json(F.REFS / "indice_originales.json")["unidades"]
    out = {}
    for sel, u in unidades:
        F.need(u in indice, "UNIDAD_SIN_ORIGINAL_EN_EL_INDICE")
        db = (F.REFS / "originales" / (u.replace(":", "_") + ".json")).read_bytes()
        F.need(F.sha(db) == indice[u]["documento_sha256"], "DOCUMENTO_ORIGINAL_DISTINTO_DEL_INDICE")
        r = json.loads(db)["resultado"]
        t = r["tiempos_s"]
        out[u] = {"seleccion": sel, "clave": r["clave_estructural"], "frontera": r.get("frontier_id") or "",
                  "techo_s": float(t["techo_s"]), "macro_s": float(t["macro_s"])}
    return out


def limite_grupo_techo(techo_s, macro_s, fronteras, unidades):
    """Límite externo del proceso de un grupo: un techo en frío, una fase macro por frontera distinta y cada unidad; múltiplo de 60 s."""
    return 60.0 * math.ceil((FACTOR_FRIO * (techo_s + fronteras * macro_s) + POR_UNIDAD_GRUPO_S * unidades) / 60.0)


def grupos_techo_fam01(plan_u):
    """Grupos de techo caro: misma selección y clave estructural; ≤ MAX_POR_TAREA por proceso en partes equilibradas, las unidades de una
    misma frontera juntas (orden por frontera e identificador). Devuelve (claves caras, grupos) con su límite justificado."""
    por = {}
    for u, x in plan_u.items():
        por.setdefault((x["seleccion"], x["clave"]), []).append(u)
    caras = {}
    falta = sorted(k[1][:8] for k in TECHOS_MEDIDOS_EN_FRIO if k not in por)
    if falta:
        raise RuntimeError("TECHO_MEDIDO_DE_UNA_CLAVE_AUSENTE: %s" % falta)
    for (sel, clave), us in por.items():
        T = max(plan_u[u]["techo_s"] for u in us)
        M = max(plan_u[u]["macro_s"] for u in us)
        medido = TECHOS_MEDIDOS_EN_FRIO.get((sel, clave))
        if medido is not None:
            if T > UMBRAL_TECHO_CARO_S:
                raise RuntimeError("TECHO_MEDIDO_PARA_UNA_CLAVE_YA_CARA: %s" % clave[:8])
            caras[(sel, clave)] = {"seleccion": sel, "clave_estructural": clave, "unidades": len(us), "techo_historico_s": medido["techo_s"],
                                   "macro_historica_s": medido["macro_s"], "fronteras": len({plan_u[u]["frontera"] for u in us}),
                                   "origen_del_techo": REGLA_TECHO_MEDIDO, "registrado_en_los_originales_s": {"techo_s": T, "macro_s": M},
                                   "medicion": medido["medicion"], "_us": us}
        elif T > UMBRAL_TECHO_CARO_S:
            caras[(sel, clave)] = {"seleccion": sel, "clave_estructural": clave, "unidades": len(us), "techo_historico_s": T,
                                   "macro_historica_s": M,
                                   "fronteras": len({plan_u[u]["frontera"] for u in us}), "_us": us}
    grupos, orden = [], sorted(caras, key=lambda k: ("origen_del_techo" in caras[k], ("R2", "R3").index(k[0]),
                                                     -caras[k]["techo_historico_s"], k[1]))
    for k in orden:
        c = caras[k]
        us = sorted(c.pop("_us"), key=lambda u: (plan_u[u]["frontera"], u))
        partes = -(-len(us) // MAX_POR_TAREA)
        tam = [len(us) // partes + (1 if i < len(us) % partes else 0) for i in range(partes)]
        c["procesos"] = partes
        i = 0
        for n in tam:
            parte = us[i:i + n]
            i += n
            f = len({plan_u[u]["frontera"] for u in parte})
            lim = limite_grupo_techo(c["techo_historico_s"], c["macro_historica_s"], f, n)
            grupos.append({"tarea": "GT%02d" % (len(grupos) + 1), "seleccion": k[0], "clave_estructural": k[1], "unidades": parte,
                           "fronteras": f, "limite_externo_s": lim, "techo": c.get("origen_del_techo", "histórico (originales)"),
                           "calculo_del_limite": "60 × ⌈(%.1f × (%.3f + %d × %.3f) + %.0f × %d) / 60⌉ = %.0f s" % (
                               FACTOR_FRIO, c["techo_historico_s"], f, c["macro_historica_s"], POR_UNIDAD_GRUPO_S, n, lim)})
    return [caras[k] for k in orden], grupos


def _grupo_fam01(sel, d):
    """Clave de agrupación de la variante agrupada (gruesa respecto del grupo CA2 del plan, que el ejecutor vuelve a separar)."""
    if sel == "R2":
        return (d["claim_id_hoja"].split(":")[1], d["pais_hoja"], d["diseno"], d["instrumento_hoja"])
    return (d["conjunto"], d["pais"], d["diseno"], d["menu"])


def receta_fam01():
    """Receta del recorrido completo (PREPARADA, no se ejecuta aquí). Una tarea por unidad numérica: cálculo y validación productiva
    (fam01-unidad) y luego comparación (fam01-comparar); NA documentales (fam01-na). Excepción GRUPOS-TECHO-C2-v1: las unidades de una
    clave estructural cara van en grupos (un proceso fam01-unidad con varias --unidad y una comparación por unidad), al principio para
    que no queden en la cola final. Después, R2 y R3, cada lista por identificador estable."""
    F = cargar("fam01", "fam01.py")
    listas, grupos_ca2, defs = [], {}, F.definiciones()
    for sel in ("R2", "R3"):
        rel, h = F.LISTAS[sel]
        listas += [(sel, u) for u in sorted(F.leer_json(F.INST / rel, h)["unidades"], key=lambda x: x["unidad"])]
    numericas = [(sel, u["unidad"]) for sel, u in listas if u["numerico"]]
    plan_u = _planificacion_fam01(F, numericas)
    claves_caras, grupos = grupos_techo_fam01(plan_u)
    agrupadas = {u: g["tarea"] for g in grupos for u in g["unidades"]}
    pasos = []
    for g in grupos:
        t = "salidas/fam01/%s/grupo_techo_%s" % (g["seleccion"], g["tarea"][2:])
        orden = ["fam01-unidad", "--seleccion", g["seleccion"]]
        for x in g["unidades"]:
            orden += ["--unidad", x]
        pasos.append({"tarea": g["tarea"], "regla": REGLA_GRUPOS_TECHO, "techo": g["techo"], "seleccion": g["seleccion"],
                      "clave_estructural": g["clave_estructural"],
                      "unidades": g["unidades"], "frontera_por_unidad": {x: plan_u[x]["frontera"] for x in g["unidades"]},
                      "limite_externo_s": g["limite_externo_s"], "calculo_del_limite": g["calculo_del_limite"],
                      "ordenes": [orden + ["--salida", t]] + [["fam01-comparar", "--seleccion", g["seleccion"], "--unidad", x, "--nueva", t,
                                                                "--salida", "%s.%s.comparacion.json" % (t, x.replace(":", "_"))] for x in g["unidades"]]})
    for sel, u in listas:
        n = u["unidad"].replace(":", "_")
        if u["numerico"]:
            grupos_ca2.setdefault((sel,) + _grupo_fam01(sel, defs[u["unidad"]]["definicion"]), []).append(u["unidad"])
            if u["unidad"] in agrupadas:
                continue
            sal = "salidas/fam01/%s/%s" % (sel, n)
            pasos.append({"seleccion": sel, "unidad": u["unidad"], "familia": u["familia"], "ordenes": [
                ["fam01-unidad", "--seleccion", sel, "--unidad", u["unidad"], "--salida", sal],
                ["fam01-comparar", "--seleccion", sel, "--unidad", u["unidad"], "--nueva", sal, "--salida", sal + ".comparacion.json"]]})
        else:
            pasos.append({"seleccion": sel, "unidad": u["unidad"], "familia": u["familia"], "ordenes": [
                ["fam01-na", "--unidad", u["unidad"], "--salida", "salidas/fam01/%s/%s.na.json" % (sel, n)]]})
    # cobertura: cada unidad numérica exactamente una vez en un cálculo y una vez en una comparación; las NA, solo en fam01-na
    calc = Counter(o[i + 1] for p in pasos for o in p["ordenes"] if o[0] == "fam01-unidad" for i in range(len(o) - 1) if o[i] == "--unidad")
    comp = Counter(o[o.index("--unidad") + 1] for p in pasos for o in p["ordenes"] if o[0] == "fam01-comparar")
    na = Counter(o[o.index("--unidad") + 1] for p in pasos for o in p["ordenes"] if o[0] == "fam01-na")
    ids_num = Counter(u for _, u in numericas)
    ids_na = Counter(u["unidad"] for _, u in listas if not u["numerico"])
    cobertura = {"numericas": len(numericas), "na": sum(ids_na.values()),
                 "numericas_en_un_calculo_exactamente_una_vez": calc == ids_num and set(calc.values()) == {1},
                 "numericas_comparadas_exactamente_una_vez": comp == ids_num and set(comp.values()) == {1},
                 "na_con_fam01_na_exactamente_una_vez": na == ids_na and set(na.values()) == {1},
                 "na_fuera_de_calculo_y_comparacion": not (set(ids_na) & (set(calc) | set(comp))),
                 "agrupadas": len(agrupadas), "ordinarias": len(numericas) - len(agrupadas)}
    F.need(all(v is True for v in cobertura.values() if isinstance(v, bool)), "COBERTURA_FAM01_NO_CONFORME")
    tareas = []
    for clave in sorted(grupos_ca2, key=lambda k: (("R2", "R3").index(k[0]), grupos_ca2[k][0])):
        us = grupos_ca2[clave]
        for i in range(0, len(us), MAX_POR_TAREA):
            parte, t = us[i:i + MAX_POR_TAREA], "salidas/fam01/%s/T%04d" % (clave[0], len(tareas) + 1)
            orden = ["fam01-unidad", "--seleccion", clave[0]]
            for x in parte:
                orden += ["--unidad", x]
            tareas.append({"tarea": "T%04d" % (len(tareas) + 1), "seleccion": clave[0], "grupo": list(clave[1:]), "unidades": parte,
                           "ordenes": [orden + ["--salida", t]] + [["fam01-comparar", "--seleccion", clave[0], "--unidad", x, "--nueva", t,
                                                                    "--salida", "%s.%s.comparacion.json" % (t, x.replace(":", "_"))] for x in parte]})
    limites = Counter(g["limite_externo_s"] for g in grupos)
    th = {c["clave_estructural"]: (c["techo_historico_s"], c["macro_historica_s"]) for c in claves_caras}
    cobertura_limite = min(((g["limite_externo_s"] - 125.0 * len(g["unidades"])) / (th[g["clave_estructural"]][0] + g["fronteras"] * th[g["clave_estructural"]][1]),
                            g["tarea"]) for g in grupos)
    return {"estado": "preparada, no ejecutada (no autoriza las 1.740 R2 ni las 27 R3 completas)", "condiciones": [
        "intérprete del entorno .venv-fam01 (perfil y lock completos, pip incluido) con -B -P -s -X utf8 y, en el entorno del proceso, "
        "PYTHONHASHSEED=0, TZ=UTC y las seis variables de hilos = 1 (BLIS, MKL, NUMEXPR, OMP, OPENBLAS, VECLIB)",
        "por omisión, un proceso de cálculo a la vez; con general --procesos-fam01 N (1 ≤ N ≤ 12), hasta N llamadas de FAM01 simultáneas, "
        "cada una en su proceso con un hilo numérico; lanzador que termine el árbol de procesos al agotar su límite (piloto: 600 s por unidad); "
        "los grupos de techo caro (%s; para dos claves de R2, techo medido en frío según %s), con el límite propio que declara cada grupo"
        % (REGLA_GRUPOS_TECHO, REGLA_TECHO_MEDIDO),
        "en Windows, cada proceso de reproducir.py pide no ser estrangulado por ahorro de energía (PRIORIDAD-ALTA-v1); no cambia ningún cálculo",
        "carpeta de salida nueva por tarea; nada se sobrescribe",
        "fam01-unidad termina con 0 solo si todas sus unidades quedan calculadas Y validadas por el validador productivo fijado; "
        "fam01-comparar termina con 0 si la reproducción queda «aceptada» (comparador histórico), «aceptada_comparacion_limpia» o "
        "«aceptada_comparacion_limpia_con_F2» (F2-ENTORNO-PORTABLE-v1, adoptada por el autor para FAM01 el 2026-11-16), y con 1 en otro "
        "caso (incluida la validación pendiente); el estado separa siempre la comparación histórica, la limpia y la limpia con F2",
        "F2 solo cubre la ubicación del venv dentro del perfil aprobado (Windows, CPython 3.12.4 oficial); otro entorno no equivalente "
        "deja la reproducción sin aceptar"],
        "lo_que_falta_para_el_lote_completo": [
        "autorización de los lotes y de su tiempo de máquina (Paso 3); el coste se concretará con mediciones, no con los dos pilotos"],
        "grupos_techo": {
            "regla": REGLA_GRUPOS_TECHO,
            "agrupacion": "misma selección y misma clave estructural (clave_estructural del documento original autenticado por "
                          "indice_originales.json); clave cara si algún documento suyo registra techo_s > %.0f s; ≤ %d unidades por proceso, en "
                          "partes equilibradas y con las unidades de una misma frontera juntas; el techo se calcula en el proceso desde las "
                          "entradas del paquete y queda en memoria para las demás unidades (Run.techos_compartidos)" % (UMBRAL_TECHO_CARO_S, MAX_POR_TAREA),
            "limite": "60 × ⌈(%.1f × (techo histórico de la clave + fronteras del grupo × macro histórica de la clave) + %.0f × unidades del grupo) / 60⌉ s"
                      % (FACTOR_FRIO, POR_UNIDAD_GRUPO_S),
            "justificacion_del_limite": [
                "techo histórico: el mayor techo_s de la clave; el grupo lo calcula una vez, en frío",
                "macro histórica: el mayor macro_s de la clave; se cuenta una fase macro por frontera distinta del grupo, porque en los originales "
                "la macro se paga por frontera (21 claves: de 0 a 3 pagos por frontera, en distintos procesos)",
                "factor %.1f: en frío, en este equipo y con un proceso, el techo tardó 1,64–2,09 veces lo del original y la macro 1,56–1,99 "
                "(INFORME_vencimientos_techo.md y ensayo del par de la unidad 30); con 12 procesos, la unidad aceptada más lenta tardó 1,73 "
                "veces lo que con 4 (INFORME_concurrencia_48.md); 2,09 × 1,73 = 3,62" % FACTOR_FRIO,
                "%.0f s por unidad: la celda consume el plazo fiscal de reloj de 120 s (igual en el original) y, en las 274 unidades, como mucho "
                "8,9 s más de previas y resto; con techo reutilizado, una unidad tardó 120–129 s en total" % POR_UNIDAD_GRUPO_S,
                "cobertura: descontados 125 s por unidad, el límite de cada grupo cubre al menos %.2f veces su techo y su macro históricos "
                "(%s)" % cobertura_limite,
                "%s: dos claves de R2 (3eb7dcff…, 2fbaf756…) no registran en sus originales el techo en frío (≤ 10,021 s y 0,376 s, con el "
                "techo ya en memoria); en la corrida completa del Paso 3 sus unidades agotaron los 600 s ordinarios. Su techo y su macro "
                "en frío se midieron en la recuperación aceptada (965,48 y 122,642 s; 848,32 y 1,676 s) y hacen de «históricos» en la "
                "fórmula; sus grupos van al final, tras los de techo registrado" % REGLA_TECHO_MEDIDO],
            "constantes": {"umbral_techo_s": UMBRAL_TECHO_CARO_S, "max_por_proceso": MAX_POR_TAREA, "factor_frio": FACTOR_FRIO,
                           "por_unidad_s": POR_UNIDAD_GRUPO_S},
            "claves_caras": claves_caras, "unidades_agrupadas": len(agrupadas), "grupos": len(grupos),
            "limites_s": {"%.0f" % k: v for k, v in sorted(limites.items())},
            "detalle": [{k: g[k] for k in ("tarea", "seleccion", "clave_estructural", "fronteras", "limite_externo_s", "calculo_del_limite")}
                        | {"unidades": len(g["unidades"])} for g in grupos],
            "ordinarias": "las demás unidades numéricas: una por proceso, límite de 600 s"},
        "variante_agrupada": {"estado": "documentada, no la usa el plan (para los techos caros rige %s)" % REGLA_GRUPOS_TECHO,
                              "regla": "grupo (preregistro, país, diseño, menú) en R2 y (conjunto, país, diseño, menú) en R3; ≤ %d unidades por "
                                       "tarea; mismas comparaciones por unidad" % MAX_POR_TAREA, "tareas": len(tareas), "detalle": tareas},
        "cobertura": cobertura, "unidades": len(listas), "numericas": len(numericas), "na": cobertura["na"],
        "procesos_de_calculo": len(grupos) + cobertura["ordinarias"], "pasos": pasos}


def fam01_main(args, parser):
    import os
    F = cargar("fam01", "fam01.py")
    t0 = time.time()
    unidades = args.unidad or []
    if args.comando == "fam01-unidad":
        if not (args.seleccion and unidades and args.salida):
            parser.error("fam01-unidad requiere --seleccion, una o más --unidad y --salida (carpeta nueva)")
        if args.salida.exists():
            parser.error("la salida ya existe; elija otra ruta")
        if sys.flags.hash_randomization or os.environ.get("PYTHONHASHSEED") != "0":
            parser.error("fam01-unidad exige PYTHONHASHSEED=0 efectivo, como el entorno de origen: lance sin -I/-E (p. ej. -B -P -s -X utf8)")
        print(json.dumps({"unidades_seleccionadas": len(unidades), "seleccion": args.seleccion}, ensure_ascii=False), flush=True)
        r = F.correr(args.seleccion, unidades, args.salida)
        print(json.dumps({"exito": r["exito"], "validacion": {k: r["validacion"][k] for k in ("cumple", "codigos")},
                          "por_unidad": {u: {k: v[k] for k in ("calculo", "estado_generador", "validacion")} for u, v in r["por_unidad"].items()},
                          "entorno": {k: r["entorno"][k] for k in ("conforms", "mismatches")}, "f2_equivalente": r["entorno"]["f2"]["equivalente"],
                          "tiempos_s": r["tiempos_s"]}, ensure_ascii=False))
        return 0 if r["exito"] else 1
    if len(unidades) > 1:
        parser.error("%s admite una sola --unidad" % args.comando)
    unidad = unidades[0] if unidades else None
    if args.salida is not None and args.salida.exists():
        parser.error("la salida ya existe; elija otra ruta")
    codigo = None
    if args.comando == "fam01-listas":
        r = F.comprobar_listas()
        ok = r["cumple"]
    elif args.comando == "fam01-comprobar":
        r = F.comprobar_carga()
        ok = r["cumple"]
    elif args.comando == "fam01-na":
        if not unidad:
            parser.error("fam01-na requiere --unidad")
        r = F.comprobar_na(unidad)
        ok = r["cumple"]
    elif args.comando == "fam01-comparar":
        if not (args.seleccion and unidad and args.nueva and args.salida):
            parser.error("fam01-comparar requiere --seleccion, --unidad, --nueva y --salida")
        r = F.comparar(args.seleccion, unidad, args.nueva)
        rep = r["estado"]["reproduccion"]
        ok = rep in F.ACEPTADAS
    else:
        if args.salida is None:
            parser.error("fam01-receta requiere --salida (archivo nuevo)")
        r = receta_fam01()
        ok = True
    r["segundos"] = round(time.time() - t0, 3)
    if args.salida is not None:
        escribir(args.salida, r)
    print(json.dumps({"comando": args.comando, "cumple": ok, "segundos": r["segundos"],
                      **({"comprobaciones": r["comprobaciones"], "piloto": r.get("piloto")} if "comprobaciones" in r and args.comando == "fam01-listas" else {}),
                      **({k: r[k] for k in ("tecnica_distinta_de_la_tupla_S6_admitida", "archivos_ausentes_o_distintos", "entorno",
                                            "dependencias_fuera_de_la_biblioteca_estandar")}
                         if args.comando == "fam01-comprobar" else {}),
                      **({"saneamiento": {c: {x: v[x] for x in ("sha256_historico", "sha256_publico", "correspondencia_comprobada")}
                                          for c, v in r["saneamiento"].items()}} if args.comando == "fam01-comprobar" else {}),
                      **({"comprobaciones": r["comprobaciones"]} if args.comando == "fam01-na" else {}),
                      **({"estado": r["estado"], "valores_iguales": r["valores"]["iguales"], "nivel_r1": r["nivel_r1"],
                          "motivos_limpia": r["limpia"]["motivos_comparador"],
                          "procedencia_operativa_distinta": r["limpia"]["diagnostico"]["procedencia_operativa_distinta"]}
                         if args.comando == "fam01-comparar" else {})},
                     ensure_ascii=False, indent=1))
    return codigo if codigo is not None else (0 if ok else 1)


FAM02 = ("fam02-listar", "fam02-comprobar", "fam02-unidad", "fam02-validar", "fam02-comparar", "fam02-receta")


def fam02_main(args, parser):
    """FAM02 (R1). Cada comando informa por separado cálculo, validación y comparación; el código 0 corresponde solo al alcance hecho."""
    import os
    F = cargar("fam02", "fam02.py")
    t0 = time.time()
    if args.salida is not None and args.salida.exists():
        parser.error("la salida ya existe; elija otra ruta")
    if args.comando == "fam02-unidad":
        if not (args.tarea and args.salida):
            parser.error("fam02-unidad requiere --tarea (una de las 18 tareas R1), --salida (carpeta nueva dentro de la carpeta de la ejecución) y, "
                         "para una asignación parcial de una tarea C, una o más --hoja")
        if sys.flags.hash_randomization or os.environ.get("PYTHONHASHSEED") != "0":
            parser.error("fam02-unidad exige PYTHONHASHSEED=0 efectivo, como el entorno de origen: lance sin -I/-E (p. ej. -B -P -s -X utf8)")
        print(json.dumps({"tarea": args.tarea, "hojas": args.hoja or "todas", "tope_s": args.tope, "salidas_guardadas": args.salidas_guardadas}, ensure_ascii=False), flush=True)
        r = F.unidad(args.tarea, args.hoja, args.salida, tope=args.tope, conexion=args.salidas_guardadas)
        print(json.dumps(F.resumen_unidad(r), ensure_ascii=False, indent=1, default=str))
        return 0 if r["exito"] else 1
    if args.comando == "fam02-listar":
        plan, cob, reg = F.plan_r1(), F.cobertura(), F.registro_v4()
        sel = F.seleccion_piloto(plan, cob, reg)
        fij = json.loads((F.DATOS / "piloto.json").read_bytes())
        clave = ("tarea", "hoja", "sentido", "extreme_id")
        r = {"comando": args.comando, "plan": plan, "ids_por_tarea": {t["id"]: len(F.ids_de(t["id"], cob)) for t in plan["r1"]},
             "rutas": {t["id"]: F.ruta_de_tarea(t["id"]) for t in plan["r1"]}, "piloto": sel,
             "piloto_igual_al_fijado": {k: sel[k] for k in clave} == {k: fij[k] for k in clave}, "calculo": "ninguno"}
        ok = plan["tareas"] == 18 and not plan["motivos"] and r["piloto_igual_al_fijado"]
    elif args.comando == "fam02-comprobar":
        r = F.comprobar()
        ok = r["cumple"]
    elif args.comando == "fam02-validar":
        if not (args.tarea and args.nueva and args.salida):
            parser.error("fam02-validar requiere --tarea, --nueva (carpeta de fam02-unidad) y --salida (carpeta nueva)")
        r = F.validar(args.tarea, args.nueva, args.salida, enlazar=args.enlazar)
        ok = r["validacion"]["cumple"] is True and (not args.enlazar or (r.get("aceptacion") or {}).get("aceptada") is True)
        print(json.dumps({"comando": args.comando, "cumple": ok, "calculo": r["calculo"], "validacion": r["validacion"], "aceptacion": r.get("aceptacion"),
                          "segundos": r["segundos"]}, ensure_ascii=False, indent=1, default=str))
        return 0 if ok else 1
    elif args.comando == "fam02-comparar":
        if not (args.tarea and args.nueva and args.salida):
            parser.error("fam02-comparar requiere --tarea, --nueva (carpeta de fam02-unidad) y --salida")
        r = F.comparar(args.tarea, args.nueva)
        ok = r["estado"]["reproduccion"] == "aceptada"
    else:
        if args.salida is None:
            parser.error("fam02-receta requiere --salida (archivo nuevo)")
        r = F.receta()
        ok = True
    r["segundos"] = round(time.time() - t0, 3)
    if args.salida is not None:
        escribir(args.salida, r)
    resumen = {"comando": args.comando, "cumple": ok, "segundos": r["segundos"]}
    if args.comando == "fam02-listar":
        resumen.update(orden=r["plan"]["orden_de_ejecucion"], motivos=r["plan"]["motivos"], piloto={k: r["piloto"][k] for k in ("tarea", "hoja", "sentido", "extreme_id")},
                       piloto_igual_al_fijado=r["piloto_igual_al_fijado"])
    elif args.comando == "fam02-comprobar":
        resumen.update(comprobaciones=r["comprobaciones"], tareas_con_error={k: v.get("error") for k, v in r["tareas"].items() if not v.get("ok")},
                       archivos_ausentes_o_distintos=r.get("archivos_ausentes_o_distintos"), entorno=r["entorno"], calculo="ninguno")
    elif args.comando == "fam02-comparar":
        if "ligadura" in r:                          # tareas C
            resumen.update(estado=r["estado"], ligadura=r["ligadura"],
                           requeridos=[{k: x.get(k) for k in ("afirmacion", "sentido", "reproducida")} for x in r["requeridos"]])
        else:                                        # A*, B*, F, D, V
            resumen.update(estado=r["estado"], ligadura_y_validacion={k: r["ligadura_y_validacion"][k] for k in ("cumple", "motivos")},
                           naturaleza=r["naturaleza"], comparacion_cumple=r["comparacion_cumple"])
    else:
        resumen.update(estado=r["estado"], orden=r["orden"], calculo="ninguno")
    print(json.dumps(resumen, ensure_ascii=False, indent=1))
    return 0 if ok else 1


FAM03 = ("fam03-preparar", "fam03-listar", "fam03-comprobar", "fam03-unidad", "fam03-validar", "fam03-comparar", "fam03-receta")


def fam03_main(args, parser):
    """FAM03 (PROD1/PROD2/PROD3). Cálculo, validación y comparación se informan por separado; el código 0 corresponde solo al alcance hecho."""
    import os
    F = cargar("fam03", "fam03.py")
    t0 = time.time()
    if args.salida is not None and args.salida.exists():
        parser.error("la salida ya existe; elija otra ruta")
    if args.comando == "fam03-unidad":
        if not (args.tarea and args.salida):
            parser.error("fam03-unidad requiere --tarea (una tarea PROD del plan; ver fam03-receta) y --salida (carpeta nueva)")
        if sys.flags.hash_randomization or os.environ.get("PYTHONHASHSEED") != "0":
            parser.error("fam03-unidad exige PYTHONHASHSEED=0 efectivo, como el entorno de origen: lance sin -I/-E (p. ej. -B -P -s -X utf8)")
        print(json.dumps({"tarea": args.tarea, "tope_efectivo_s": args.tope}, ensure_ascii=False), flush=True)
        r = F.correr(args.tarea, args.salida, tope_efectivo=args.tope)
        print(json.dumps({k: r[k] for k in ("tarea", "resultado", "validacion", "tiempos_s", "run_id")} | {"lecturas": {k: r["lecturas"][k] for k in (
            "en_el_paquete", "fuera_del_paquete_y_del_interprete", "sin_manifiesto", "referencias_leidas")}}, ensure_ascii=False, indent=1, default=str))
        return 0 if r["exito"] else 1
    if args.comando == "fam03-validar":
        if not (args.nueva and args.salida):
            parser.error("fam03-validar requiere --nueva (carpeta de fam03-unidad) y --salida (carpeta nueva)")
        r = F.validar(args.nueva, args.salida)
        print(json.dumps({"comando": args.comando, "cumple": r["exito"], "naturaleza": r["naturaleza"], "validacion": r["validacion"], "segundos": r["segundos"]},
                         ensure_ascii=False, indent=1, default=str))
        return 0 if r["exito"] else 1
    if args.comando == "fam03-preparar":
        r = F.preparar_datos()
        ok = True
    elif args.comando == "fam03-listar":
        r = F.listar()
        ok = True
    elif args.comando == "fam03-comprobar":
        r = F.comprobar()
        ok = r["cumple"]
    elif args.comando == "fam03-comparar":
        if not (args.tarea and args.nueva and args.salida):
            parser.error("fam03-comparar requiere --tarea, --nueva (carpeta de fam03-unidad o de fam03-validar) y --salida (archivo nuevo)")
        r = F.comparar(args.tarea, args.nueva)
        ok = r["estado"]["reproduccion"] == "aceptada"
    else:
        if args.salida is None:
            parser.error("fam03-receta requiere --salida (archivo nuevo)")
        r = F.receta()
        ok = True
    r["segundos"] = round(time.time() - t0, 3)
    if args.salida is not None:
        escribir(args.salida, r)
    resumen = {"comando": args.comando, "cumple": ok, "segundos": r["segundos"]}
    if args.comando == "fam03-preparar":
        resumen.update(r)
    elif args.comando == "fam03-listar":
        resumen.update(tareas=len(r["tareas"]), pilotos=[x["tarea"] for x in r["pilotos"]["pilotos"]], calculo="ninguno")
    elif args.comando == "fam03-comprobar":
        resumen.update({k: r[k] for k in ("fuentes", "contexto_esperado", "evaluadores_ra", "pilotos", "contexto")}, plan={k: r["plan"].get(k) for k in (
            "verificado", "igual_salvo_lo_declarado", "diferencias_no_declaradas", "motivo")},
                       cobertura={k: r["cobertura"][k] for k in ("unidades_por_familia", "tareas_por_familia", "arboles_catalogo", "estados_en_las_referencias",
                                                                 "declaradas_D4_en_las_referencias", "cumple", "motivos")}, calculo="ninguno")
    elif args.comando == "fam03-comparar":
        resumen.update(estado=r["estado"], cuentas=r["cuentas"], clasificacion_igual=r["clasificacion"]["igual"], naturaleza_nueva=r["naturaleza_nueva"])
    else:
        resumen.update(estado=r["estado"], cobertura=r["cobertura"], calculo="ninguno")
    print(json.dumps(resumen, ensure_ascii=False, indent=1, default=str))
    return 0 if ok else 1


FAM04 = ("fam04-listar", "fam04-comprobar", "fam04-unidad", "fam04-validar", "fam04-comparar", "fam04-receta")


def fam04_main(args, parser):
    """FAM04 (lote 1). Cálculo, validación y comparación se informan por separado; el código 0 corresponde solo al alcance hecho."""
    import os
    F = cargar("fam04", "fam04.py")
    t0 = time.time()
    if args.salida is not None and args.salida.exists():
        parser.error("la salida ya existe; elija otra ruta")
    if args.comando in ("fam04-unidad", "fam04-comparar") and args.tarea not in F.TAREAS:
        parser.error("%s requiere --tarea (una de %s)" % (args.comando, ", ".join(F.TAREAS)))
    if args.comando == "fam04-unidad":
        if args.salida is None or (args.unidad and len(args.unidad) != 1):
            parser.error("fam04-unidad requiere --tarea, --salida (carpeta nueva) y, para una unidad, UNA --unidad (frontera, conjunto o clave transformada)")
        if sys.flags.hash_randomization or os.environ.get("PYTHONHASHSEED") != "0":
            parser.error("fam04-unidad exige PYTHONHASHSEED=0 efectivo: lance sin -I/-E (p. ej. -B -P -s -X utf8)")
        u = args.unidad[0] if args.unidad else None
        print(json.dumps({"tarea": args.tarea, "unidad": u, "tope_trabajo_s": args.tope}, ensure_ascii=False), flush=True)
        r = F.correr(args.tarea, args.salida, unidad=u, tope=args.tope)
        print(json.dumps({k: r[k] for k in ("tarea", "unidad", "resultado", "tiempos_s", "exito")} | {"lecturas": {k: r["lecturas"][k] for k in (
            "en_el_paquete", "fuera_del_paquete_y_del_interprete", "sin_manifiesto", "referencias_leidas", "filas_padre_leidas")}}
                         | ({"cobertura_nacional_del_contexto": r["cobertura_nacional_del_contexto"]} if "cobertura_nacional_del_contexto" in r else {}),
                         ensure_ascii=False, indent=1, default=str))
        return 0 if r["exito"] else 1
    if args.comando == "fam04-listar":
        r = F.listar()
        ok = True
    elif args.comando == "fam04-comprobar":
        r = F.comprobar()
        ok = r["cumple"]
    elif args.comando == "fam04-validar":
        if not (args.nueva and args.salida):
            parser.error("fam04-validar requiere --nueva (carpeta de fam04-unidad) y --salida (archivo nuevo)")
        r = F.validar(args.nueva)
        ok = r["aceptada"]
    elif args.comando == "fam04-comparar":
        if not (args.nueva and args.validacion and args.salida):
            parser.error("fam04-comparar requiere --tarea, --nueva (carpeta de fam04-unidad), --validacion (archivo de fam04-validar) y --salida (archivo nuevo)")
        r = F.comparar(args.tarea, args.nueva, args.validacion)
        ok = r["estado"]["reproduccion"] == "aceptada"
    else:
        if args.salida is None:
            parser.error("fam04-receta requiere --salida (archivo nuevo)")
        r = F.receta()
        ok = True
    r["segundos"] = round(time.time() - t0, 3)
    if args.salida is not None:
        escribir(args.salida, r)
    resumen = {"comando": args.comando, "cumple": ok, "segundos": r["segundos"]}
    if args.comando == "fam04-listar":
        resumen.update(unidades={t: len(v) for t, v in r["unidades"].items()}, pilotos=[(p["tarea"], p["unidad"]) for p in r["pilotos"]["pilotos"]], calculo="ninguno")
    elif args.comando == "fam04-comprobar":
        resumen.update({k: r[k] for k in ("fuentes", "procedencia", "nucleo", "celdas_padre", "revalidacion_de_las_referencias", "pilotos")},
                       cobertura={k: v for k, v in r["cobertura"].items() if k != "L1-ELAST"} | {"L1-ELAST": {k: r["cobertura"]["L1-ELAST"][k] for k in ("fronteras", "nodos_total")}},
                       referencias={"cumple": r["referencias"]["cumple"], "motivos": r["referencias"]["motivos"]}, calculo="ninguno")
    elif args.comando == "fam04-validar":
        resumen.update(tarea=r["tarea"], unidad=r["unidad"], rc=r["rc"], veredicto=r["veredicto"])
    elif args.comando == "fam04-comparar":
        resumen.update(estado=r["estado"], objetos={n: {k: o[k] for k in ("cobertura", "lineas_identicas", "n_discretas", "n_numericas")} for n, o in r["objetos"].items()},
                       resultado_igual={k: v["igual"] for k, v in r["resultado"].items()}, identidades=r["identidades"], derivados=r["derivados"])
    else:
        resumen.update(estado=r["estado"], orden=r["orden"], cobertura=r["cobertura"], calculo="ninguno")
    print(json.dumps(resumen, ensure_ascii=False, indent=1, default=str))
    return 0 if ok else 1


FAM05 = ("fam05-listar", "fam05-comprobar", "fam05-unidad", "fam05-validar", "fam05-comparar", "fam05-receta")


def fam05_main(args, parser):
    """FAM05 (lote 2: L1-ELAST con suplemento histórico y L1-LAMBDA). Misma estructura que FAM04: cálculo, validación y comparación se
    informan por separado; el código 0 corresponde solo al alcance hecho."""
    import os
    F = cargar("fam05", "fam05.py")
    t0 = time.time()
    if args.salida is not None and args.salida.exists():
        parser.error("la salida ya existe; elija otra ruta")
    if args.comando in ("fam05-unidad", "fam05-comparar") and args.tarea not in F.TAREAS:
        parser.error("%s requiere --tarea (una de %s)" % (args.comando, ", ".join(F.TAREAS)))
    if args.comando == "fam05-unidad":
        if args.salida is None or (args.unidad and len(args.unidad) != 1):
            parser.error("fam05-unidad requiere --tarea, --salida (carpeta nueva) y, para una unidad, UNA --unidad (malla nueva, SUPLEMENTO o par conjunto|país)")
        if sys.flags.hash_randomization or os.environ.get("PYTHONHASHSEED") != "0":
            parser.error("fam05-unidad exige PYTHONHASHSEED=0 efectivo: lance sin -I/-E (p. ej. -B -P -s -X utf8)")
        u = args.unidad[0] if args.unidad else None
        print(json.dumps({"tarea": args.tarea, "unidad": u, "tope_trabajo_s": args.tope}, ensure_ascii=False), flush=True)
        r = F.correr(args.tarea, args.salida, unidad=u, tope=args.tope)
        print(json.dumps({k: r[k] for k in ("tarea", "unidad", "operacion", "resultado", "tiempos_s", "nucleo", "exito")} | {"lecturas": {k: r["lecturas"][k] for k in (
            "en_el_paquete", "fuera_del_paquete_y_del_interprete", "sin_manifiesto", "referencias_leidas", "nucleo_c0_leidos",
            "src_de_otra_raiz_leidos")}} | ({"cobertura_nacional_del_contexto": r["cobertura_nacional_del_contexto"]} if "cobertura_nacional_del_contexto" in r else {}),
                         ensure_ascii=False, indent=1, default=str))
        return 0 if r["exito"] else 1
    if args.comando == "fam05-listar":
        r = F.listar()
        ok = True
    elif args.comando == "fam05-comprobar":
        r = F.comprobar()
        ok = r["cumple"]
    elif args.comando == "fam05-validar":
        if not (args.nueva and args.salida):
            parser.error("fam05-validar requiere --nueva (carpeta de fam05-unidad) y --salida (archivo nuevo)")
        r = F.validar(args.nueva)
        ok = r["aceptada"]
    elif args.comando == "fam05-comparar":
        if not (args.nueva and args.validacion and args.salida):
            parser.error("fam05-comparar requiere --tarea, --nueva (carpeta de fam05-unidad), --validacion (archivo de fam05-validar) y --salida (archivo nuevo)")
        r = F.comparar(args.tarea, args.nueva, args.validacion)
        ok = r["estado"]["reproduccion"] == "aceptada"
    else:
        if args.salida is None:
            parser.error("fam05-receta requiere --salida (archivo nuevo)")
        r = F.receta()
        ok = True
    r["segundos"] = round(time.time() - t0, 3)
    if args.salida is not None:
        escribir(args.salida, r)
    resumen = {"comando": args.comando, "cumple": ok, "segundos": r["segundos"]}
    if args.comando == "fam05-listar":
        resumen.update(recuento=r["recuento"], pilotos=[(p["tarea"], p["unidad"]) for p in r["pilotos"]["pilotos"]],
                       verificacion_historica=r["pilotos"]["verificacion_historica"]["unidad"], calculo="ninguno")
    elif args.comando == "fam05-comprobar":
        resumen.update({k: r[k] for k in ("fuentes", "procedencia", "nucleo", "revalidacion_de_las_referencias", "pilotos")},
                       libro_rem121={k: v for k, v in r["libro_rem121"].items() if k != "recuentos"},
                       cobertura={"L1-ELAST": {k: v for k, v in r["cobertura"]["L1-ELAST"].items() if k != "mallas_por_diseno_j"},
                                  "L1-LAMBDA": {k: r["cobertura"]["L1-LAMBDA"][k] for k in ("pares", "filas_esperadas", "llamadas_bridge_esperadas")},
                                  "cumple": r["cobertura"]["cumple"], "motivos": r["cobertura"]["motivos"]},
                       referencias={"cumple": r["referencias"]["cumple"], "motivos": r["referencias"]["motivos"]}, calculo="ninguno")
    elif args.comando == "fam05-validar":
        resumen.update(tarea=r["tarea"], unidad=r["unidad"], rc=r["rc"], veredicto=r["veredicto"])
    elif args.comando == "fam05-comparar":
        resumen.update(estado=r["estado"], objetos={n: {k: o[k] for k in ("cobertura", "lineas_identicas", "n_discretas", "n_numericas", "vinculo")}
                                                    for n, o in r["objetos"].items()},
                       resultado_igual={k: v["igual"] for k, v in r["resultado"].items()}, identidades=r["identidades"], derivados=r["derivados"])
    else:
        resumen.update(estado=r["estado"], orden=r["orden"], cobertura=r["cobertura"], calculo="ninguno")
    print(json.dumps(resumen, ensure_ascii=False, indent=1, default=str))
    return 0 if ok else 1


FAM06 = ("fam06-listar", "fam06-comprobar", "fam06-unidad", "fam06-validar", "fam06-comparar", "fam06-conciliar", "fam06-receta")


def fam06_main(args, parser):
    """FAM06 (E4: 383 mallas G/N y conciliación de 391 pares). Cálculo, validación, conciliación y comparación se informan por separado;
    el código 0 corresponde solo al alcance hecho."""
    import os
    F = cargar("fam06", "fam06.py")
    t0 = time.time()
    if args.salida is not None and args.salida.exists():
        parser.error("la salida ya existe; elija otra ruta")
    if args.comando == "fam06-unidad":
        if args.salida is None or (args.unidad and len(args.unidad) != 1) or args.tarea not in (None, F.TAREA):
            parser.error("fam06-unidad requiere --salida (carpeta nueva) y, para un piloto, UNA --unidad (frontier_id de una malla E4); --tarea, si se da, L1-ELAST")
        if sys.flags.hash_randomization or os.environ.get("PYTHONHASHSEED") != "0":
            parser.error("fam06-unidad exige PYTHONHASHSEED=0 efectivo: lance sin -I/-E (p. ej. -B -P -s -X utf8)")
        u = args.unidad[0] if args.unidad else None
        print(json.dumps({"tarea": F.TAREA, "unidad": u, "tope_trabajo_s": args.tope}, ensure_ascii=False), flush=True)
        r = F.correr(args.salida, unidad=u, tope=args.tope)
        print(json.dumps({k: r[k] for k in ("tarea", "unidad", "operacion", "resultado", "tiempos_s", "nucleo", "exito")} | {"lecturas": {k: r["lecturas"][k] for k in (
            "en_el_paquete", "fuera_del_paquete_y_del_interprete", "sin_manifiesto", "referencias_leidas", "nucleo_c0_leidos", "datos_de_fam05_leidos")}},
                         ensure_ascii=False, indent=1, default=str))
        return 0 if r["exito"] else 1
    if args.comando == "fam06-conciliar":
        if args.salida is None or args.e4 is None or args.lote2 is None:
            parser.error("fam06-conciliar requiere --e4 y --lote2 (carpeta nueva validada o «guardado»), su --validacion-e4 / --validacion-lote2 "
                         "si es carpeta, y --salida (carpeta nueva)")
        r = F.conciliar(args.salida, args.e4, args.lote2, args.validacion_e4, args.validacion_lote2)
        print(json.dumps({k: r[k] for k in ("naturaleza", "acredita", "lados", "pares_seleccionados", "resultado", "lecturas", "tiempos_s", "exito")},
                         ensure_ascii=False, indent=1, default=str))
        return 0 if r["exito"] else 1
    if args.comando == "fam06-listar":
        r = F.listar()
        ok = True
    elif args.comando == "fam06-comprobar":
        r = F.comprobar()
        ok = r["cumple"]
    elif args.comando == "fam06-validar":
        if not (args.nueva and args.salida):
            parser.error("fam06-validar requiere --nueva (carpeta de fam06-unidad) y --salida (archivo nuevo)")
        r = F.validar(args.nueva)
        ok = r["aceptada"]
    elif args.comando == "fam06-comparar":
        if args.tarea not in F.TAREAS or not (args.nueva and args.salida) or (args.tarea == F.TAREA and not args.validacion):
            parser.error("fam06-comparar requiere --tarea L1-ELAST (con --nueva de fam06-unidad y --validacion de fam06-validar) o --tarea CONCILIACION "
                         "(con --nueva de fam06-conciliar), y --salida (archivo nuevo)")
        r = F.comparar_mallas(args.nueva, args.validacion) if args.tarea == F.TAREA else F.comparar_conciliacion(args.nueva)
        ok = r["estado"]["reproduccion"] == "aceptada"
    else:
        if args.salida is None:
            parser.error("fam06-receta requiere --salida (archivo nuevo)")
        r = F.receta()
        ok = True
    r["segundos"] = round(time.time() - t0, 3)
    if args.salida is not None:
        escribir(args.salida, r)
    resumen = {"comando": args.comando, "cumple": ok, "segundos": r["segundos"]}
    if args.comando == "fam06-listar":
        resumen.update(recuento=r["recuento"], pilotos=[(p["instrumento"], p["unidad"]) for p in r["pilotos"]["pilotos"]], calculo="ninguno")
    elif args.comando == "fam06-comprobar":
        resumen.update({k: r[k] for k in ("fuentes", "procedencia", "nucleo", "cobertura", "revalidacion_de_la_referencia", "pilotos")},
                       libro_rem122={k: v for k, v in r["libro_rem122"].items() if k != "recuentos"},
                       referencias={"cumple": r["referencias"]["cumple"], "motivos": r["referencias"]["motivos"],
                                    "conciliacion": r["referencias"]["productos"]["conciliacion"]}, calculo="ninguno")
    elif args.comando == "fam06-validar":
        resumen.update(tarea=r["tarea"], unidad=r["unidad"], rc=r["rc"], veredicto=r["veredicto"])
    elif args.comando == "fam06-comparar" and args.tarea == F.TAREA:
        resumen.update(estado=r["estado"], objetos={n: {k: o[k] for k in ("cobertura", "lineas_identicas", "n_discretas", "n_numericas")} for n, o in r["objetos"].items()},
                       resultado_igual={k: v["igual"] for k, v in r["resultado"].items()}, identidades=r["identidades"], derivados=r["derivados"])
    elif args.comando == "fam06-comparar":
        resumen.update(estado=r["estado"], naturaleza=r["naturaleza"], lados=r["lados"], cobertura=r["cobertura"], n_discretas=r["n_discretas"],
                       bytes_identicos_a_la_referencia=r["bytes_identicos_a_la_referencia"], totales_iguales={k: v["igual"] for k, v in r["totales"].items()},
                       vinculos={k: {x: v[x] for x in ("nueva_ligada_a_sus_bytes", "referencia_ligada_al_catalogo", "igual_a_la_referencia")} for k, v in r["vinculos"].items()},
                       derivados=r["derivados"], topologia_G_N=r["topologia_G_N"])
    else:
        resumen.update(estado=r["estado"], pasos=[p["paso"] for p in r["pasos"]], cobertura=r["cobertura"], calculo="ninguno")
    print(json.dumps(resumen, ensure_ascii=False, indent=1, default=str))
    return 0 if ok else 1


FAM07 = ("fam07-listar", "fam07-comprobar", "fam07-unidad", "fam07-validar", "fam07-comparar", "fam07-ensamblar", "fam07-receta")


def fam07_main(args, parser):
    """FAM07 (COORD del lote 2: seis techos certificados, 20 reutilizados, ensamblado de 1.532 y 192 previas aparte). Cálculo, validación,
    ensamblado y comparación se informan por separado; el código 0 corresponde solo al alcance hecho."""
    import os
    F = cargar("fam07", "fam07.py")
    t0 = time.time()
    if args.salida is not None and args.salida.exists():
        parser.error("la salida ya existe; elija otra ruta")
    if args.comando == "fam07-unidad":
        if args.salida is None or args.tarea not in F.TAREAS:
            parser.error("fam07-unidad requiere --tarea (una de %s) y --salida (carpeta nueva)" % ", ".join(F.TAREAS))
        if sys.flags.hash_randomization or os.environ.get("PYTHONHASHSEED") != "0":
            parser.error("fam07-unidad exige PYTHONHASHSEED=0 efectivo: lance sin -I/-E (p. ej. -B -P -s -X utf8)")
        print(json.dumps({"tarea": args.tarea, "tope_trabajo_s": args.tope}, ensure_ascii=False), flush=True)
        r = F.correr(args.tarea, args.salida, tope=args.tope)
        print(json.dumps({k: r[k] for k in ("tarea", "operacion", "resultado", "techos", "tiempos_s", "exito")} | {"lecturas": {k: r["lecturas"][k] for k in (
            "en_el_paquete", "fuera_del_paquete_y_del_interprete", "sin_manifiesto", "referencias_leidas", "nucleo_c0_leidos", "codigo_coord_leido")}},
                         ensure_ascii=False, indent=1, default=str))
        return 0 if r["exito"] else 1
    if args.comando == "fam07-ensamblar":
        if args.salida is None:
            parser.error("fam07-ensamblar requiere --salida (carpeta nueva) y una --entrada <tarea>=<carpeta de fam07-unidad|guardado> por tarea")
        ent = {}
        for e in args.entrada or []:
            t, sep, v = e.partition("=")
            if not sep or not v or t in ent:
                parser.error("--entrada debe ser <tarea>=<carpeta|guardado>, una por tarea: %s" % e)
            ent[t] = v
        r = F.ensamblar(args.salida, ent)
        print(json.dumps({k: r[k] for k in ("naturaleza", "acredita", "entradas", "rc", "veredicto", "dictamen", "productos", "tiempos_s", "exito")}
                         | {"lecturas": {k: r["lecturas"][k] for k in ("en_el_paquete", "fuera_del_paquete_y_del_interprete", "sin_manifiesto",
                                                                        "referencias_leidas", "ensamblado_esperado_leido")}}, ensure_ascii=False, indent=1, default=str))
        return 0 if r["exito"] else 1
    if args.comando == "fam07-listar":
        r = F.listar()
        ok = True
    elif args.comando == "fam07-comprobar":
        r = F.comprobar()
        ok = r["cumple"]
    elif args.comando == "fam07-validar":
        if not (args.nueva and args.salida):
            parser.error("fam07-validar requiere --nueva (carpeta de una tarea) y --salida (archivo nuevo)")
        r = F.validar(args.nueva)
        ok = r["aceptada"]
    elif args.comando == "fam07-comparar":
        if args.tarea not in F.TAREAS + (F.ENSAMBLADO,) or not (args.nueva and args.salida) or (args.tarea in F.TAREAS and not args.validacion):
            parser.error("fam07-comparar requiere --tarea L1-COORD-R1/R2/R3 (con --nueva de fam07-unidad y --validacion de fam07-validar) o --tarea "
                         "ENSAMBLADO (con --nueva de fam07-ensamblar), y --salida (archivo nuevo)")
        r = F.comparar(args.tarea, args.nueva, args.validacion) if args.tarea in F.TAREAS else F.comparar_ensamblado(args.nueva)
        ok = r["estado"]["reproduccion"] == "aceptada"
    else:
        if args.salida is None:
            parser.error("fam07-receta requiere --salida (archivo nuevo)")
        r = F.receta()
        ok = True
    r["segundos"] = round(time.time() - t0, 3)
    if args.salida is not None:
        escribir(args.salida, r)
    resumen = {"comando": args.comando, "cumple": ok, "segundos": r["segundos"]}
    if args.comando == "fam07-listar":
        resumen.update(recuento=r["recuento"], pilotos=[(p["tarea"], [c["clave"] for c in p["claves"]]) for p in r["pilotos"]["pilotos"]], calculo="ninguno")
    elif args.comando == "fam07-comprobar" and "comprobacion_interrumpida" in r:
        resumen.update(fuentes=r["fuentes"], comprobacion_interrumpida=r["comprobacion_interrumpida"], calculo="ninguno")
    elif args.comando == "fam07-comprobar":
        resumen.update({k: r[k] for k in ("fuentes", "procedencia", "nucleo", "motor", "revalidacion_de_las_referencias", "pilotos")},
                       cobertura={k: v for k, v in r["cobertura"].items() if k not in ("fuera_del_lote",)},
                       reutilizaciones={k: v for k, v in r["reutilizaciones"].items() if k != "fuentes_autenticas"},
                       previas=r["previas"], referencias={"cumple": r["referencias"]["cumple"], "motivos": r["referencias"]["motivos"]},
                       libro_rem125={k: v for k, v in r["libro_rem125"].items() if k != "recuentos"}, calculo="ninguno")
    elif args.comando == "fam07-validar":
        resumen.update(tarea=r["tarea"], rc=r["rc"], veredicto=r["veredicto"])
    elif args.comando == "fam07-comparar" and args.tarea in F.TAREAS:
        resumen.update(estado=r["estado"], objetos={n: {k: o[k] for k in ("cobertura", "lineas_identicas", "n_discretas", "n_numericas", "vinculo")}
                                                    for n, o in r["objetos"].items()},
                       resultado_igual={k: v["igual"] for k, v in r["resultado"].items()}, identidades=r["identidades"],
                       huella_derivada=r["derivados"].get("huella_derivada_de_los_techos"), operativos=r["operativos"])
    elif args.comando == "fam07-comparar":
        resumen.update(estado=r["estado"], naturaleza=r["naturaleza"], recuentos=r["recuentos"], bytes_identicos_a_la_referencia=r["bytes_identicos_a_la_referencia"],
                       objetos={n: {k: o[k] for k in ("cobertura", "lineas_identicas", "n_discretas", "n_numericas", "vinculo")} for n, o in r["objetos"].items()},
                       ensamblado_json={k: r["ensamblado_json"][k] for k in ("vinculos", "n_discretas")})
    else:
        resumen.update(estado=r["estado"], pasos=[p["paso"] for p in r["pasos"]], cobertura=r["cobertura"], calculo="ninguno")
    print(json.dumps(resumen, ensure_ascii=False, indent=1, default=str))
    return 0 if ok else 1


FAM08 = ("fam08-listar", "fam08-comprobar", "fam08-unidad", "fam08-validar", "fam08-comparar", "fam08-conciliar", "fam08-recuperar",
         "fam08-integrar", "fam08-receta")


def _entradas_fam08(args, parser):
    ent = {}
    for e in args.entrada or []:
        t, sep, v = e.partition("=")
        if not sep or not v:
            parser.error("--entrada debe ser <nombre>=<carpeta|archivo|guardado>: %s" % e)
        if t == "piloto":
            ent.setdefault("pilotos", []).append(v)
        elif t in ent:
            parser.error("--entrada repetida: %s" % t)
        else:
            ent[t] = v
    return ent


def fam08_main(args, parser):
    """FAM08 (ENF: mallas eta_f/2 y pares con el padre, techos ABL-ENF T1–T6 con el caso no alcanzado, integración de 26 claves y 1.724
    celdas). Cálculo, validación, recuperación, regeneración y comparación se informan por separado; el código 0 corresponde solo al alcance hecho."""
    import os
    F = cargar("fam08", "fam08.py")
    t0 = time.time()
    if args.salida is not None and args.salida.exists():
        parser.error("la salida ya existe; elija otra ruta")
    lect = ("en_el_paquete", "fuera_del_paquete_y_del_interprete", "sin_manifiesto", "referencias_leidas", "referencia_esperada_leida")
    if args.comando == "fam08-unidad":
        if args.salida is None or args.tarea not in (F.ELAST,) + F.TAREAS or (args.unidad and (args.tarea != F.ELAST or len(args.unidad) != 1)):
            parser.error("fam08-unidad requiere --tarea (L1-ELAST, con --unidad opcional de una malla, o una de %s) y --salida (carpeta nueva)" % ", ".join(F.TAREAS))
        if sys.flags.hash_randomization or os.environ.get("PYTHONHASHSEED") != "0":
            parser.error("fam08-unidad exige PYTHONHASHSEED=0 efectivo: lance sin -I/-E (p. ej. -B -P -s -X utf8)")
        u = args.unidad[0] if args.unidad else None
        print(json.dumps({"tarea": args.tarea, "unidad": u, "tope_trabajo_s": args.tope}, ensure_ascii=False), flush=True)
        r = F.correr(args.tarea, args.salida, u, tope=args.tope)
        print(json.dumps({k: r.get(k) for k in ("tarea", "unidad", "operacion", "resultado", "techos", "tiempos_s", "termino", "exito")}
                         | {"lecturas": {k: r["lecturas"][k] for k in lect[:4] + ("nucleo_c0_leidos", "codigo_enf_leido")}}, ensure_ascii=False, indent=1, default=str))
        return 0 if r["exito"] else 1
    if args.comando in ("fam08-conciliar", "fam08-recuperar", "fam08-integrar"):
        if args.salida is None:
            parser.error("%s requiere --salida (carpeta nueva) y sus --entrada" % args.comando)
        ent = _entradas_fam08(args, parser)
        if args.comando == "fam08-conciliar":
            if set(ent) - {"mallas", "pilotos"} or "mallas" not in ent:
                parser.error("fam08-conciliar requiere --entrada mallas=<carpeta de fam08-unidad L1-ELAST|guardado> y, solo con «guardado», "
                             "--entrada piloto=<carpeta de una malla piloto validada> (repetible)")
            r = F.conciliar(args.salida, ent["mallas"], ent.get("pilotos") or ())
            claves = ("naturaleza", "acredita", "mallas", "rc", "veredicto", "excepcion", "productos", "tiempos_s", "exito")
        elif args.comando == "fam08-recuperar":
            if set(ent) - {F.T1}:
                parser.error("fam08-recuperar admite solo --entrada %s=<carpeta de fam08-unidad|guardado> (por defecto, guardado)" % F.T1)
            r = F.recuperar(args.salida, ent.get(F.T1, F.GUARDADO))
            claves = ("naturaleza", "t1_entrada", "separados", "tiempos_s", "exito")
            r_imp = {"t1": {k: r["t1"].get(k) for k in ("aceptada", "dictamen", "reutilizables", "pendientes")},
                     "con_certificado": {n: {k: (v.get("pendientes") or {}).get(F.CLAVE_NA, {}).get(k) for k in ("estado_recuperacion", "estado_persistido")}
                                         for n, v in r["con_certificado"].items()},
                     "certificado_reemitido": {k: r["certificado_reemitido"][k] for k in ("sha256", "rc", "excepcion")},
                     "pruebas": {k: r["pruebas"][k] for k in ("sha256", "rc", "excepcion")}}
        else:
            r = F.integrar(args.salida, ent)
            claves = ("naturaleza", "acredita", "entradas", "tiempos_s", "exito")
            r_imp = {n: {k: r[n][k] for k in ("rc", "veredicto", "excepcion")} for n in ("ensamblado", "conciliacion")}
        print(json.dumps({k: r.get(k) for k in claves} | (r_imp if args.comando != "fam08-conciliar" else {})
                         | {"lecturas": {k: r["lecturas"][k] for k in lect}}, ensure_ascii=False, indent=1, default=str))
        return 0 if r["exito"] else 1
    if args.comando == "fam08-listar":
        r = F.listar()
        ok = True
    elif args.comando == "fam08-comprobar":
        r = F.comprobar()
        ok = r["cumple"]
    elif args.comando == "fam08-validar":
        if not (args.nueva and args.salida):
            parser.error("fam08-validar requiere --nueva (carpeta de fam08-unidad L1-ELAST o ABL-ENF-T2…T6) y --salida (archivo nuevo)")
        r = F.validar(args.nueva)
        ok = r["aceptada"]
    elif args.comando == "fam08-comparar":
        ok_t = args.tarea in (F.ELAST,) + F.TAREAS
        if not (ok_t or args.tarea in (F.PARES, F.INTEGRAL, F.RECUPERACION)) or not (args.nueva and args.salida) or (ok_t and not args.validacion):
            parser.error("fam08-comparar requiere --tarea L1-ELAST o ABL-ENF-T* (con --nueva de fam08-unidad y --validacion de fam08-validar; "
                         "T1: RECUPERACION_T1.json de fam08-recuperar) o --tarea PARES / RECUPERACION / INTEGRAL (con --nueva de fam08-conciliar / "
                         "fam08-recuperar / fam08-integrar), y --salida (archivo nuevo)")
        if args.tarea == F.ELAST:
            r = F.comparar_mallas(args.nueva, args.validacion)
        elif ok_t:
            r = F.comparar_techos(args.tarea, args.nueva, args.validacion)
        else:
            r = {F.PARES: F.comparar_pares, F.RECUPERACION: F.comparar_recuperacion, F.INTEGRAL: F.comparar_integral}[args.tarea](args.nueva)
        ok = r["estado"]["reproduccion"] == "aceptada"
    else:
        if args.salida is None:
            parser.error("fam08-receta requiere --salida (archivo nuevo)")
        r = F.receta()
        ok = True
    r["segundos"] = round(time.time() - t0, 3)
    if args.salida is not None:
        escribir(args.salida, r)
    resumen = {"comando": args.comando, "cumple": ok, "segundos": r["segundos"]}
    if args.comando == "fam08-listar":
        resumen.update(recuento=r["recuento"], pilotos=[p.get("unidad") or p["tarea"] for p in r["pilotos"]["pilotos"]], calculo="ninguno")
    elif args.comando == "fam08-comprobar" and "comprobacion_interrumpida" in r:
        resumen.update(fuentes=r["fuentes"], comprobacion_interrumpida=r["comprobacion_interrumpida"], calculo="ninguno")
    elif args.comando == "fam08-comprobar":
        resumen.update({k: r[k] for k in ("fuentes", "procedencia", "nucleo", "motor", "pilotos", "receta")}, cobertura=r["cobertura"],
                       referencias=r["referencias"], revalidacion_de_las_guardadas=r["revalidacion_de_las_guardadas"],
                       libros={k: v for k, v in r["libros"].items()}, calculo="ninguno")
    elif args.comando == "fam08-validar":
        resumen.update(tarea=r["tarea"], unidad=r["unidad"], rc=r["rc"], veredicto=r["veredicto"])
    elif args.comando == "fam08-comparar":
        objetos = {n: {k: o.get(k) for k in ("cobertura", "lineas_identicas", "n_discretas", "n_numericas", "vinculo")} for n, o in (r.get("objetos") or {}).items()}
        resumen.update(estado=r["estado"], objetos=objetos,
                       **{k: r[k] for k in ("naturaleza", "acredita", "recuentos", "recuentos_de_la_referencia_iguales", "bytes_identicos_a_la_referencia",
                                            "derivados", "identidades", "operativos", "hechos_de_la_recuperacion", "contrastes", "veredictos_iguales",
                                            "veredicto_del_conciliador_igual") if k in r})
        if "certificado" in r:
            resumen["certificado"] = {"estado": r["certificado"]["estado"], "huella_derivada": r["certificado"]["huella_derivada"],
                                      "ubicacion": r["certificado"]["comparacion_con_la_proyeccion"]["ubicacion"],
                                      "salida_del_certificador_igual": r["certificado"]["salida_del_certificador_igual"]}
        if "documentos" in r:
            resumen["documentos"] = {n: {k: len(v[k]) for k in ("ubicacion", "puerta", "vinculos", "discretas", "numericas")} | {"vinculos_completos": v["vinculos_completos"]}
                                     for n, v in r["documentos"].items()}
    else:
        resumen.update(estado=r["estado"], pasos=[p["paso"] for p in r["pasos"]], cobertura=r["cobertura"], calculo="ninguno")
    print(json.dumps(resumen, ensure_ascii=False, indent=1, default=str))
    return 0 if ok else 1


FAM11 = ("fam11-listar", "fam11-comprobar", "fam11-unidad", "fam11-validar", "fam11-comparar", "fam11-ensamblar", "fam11-receta")


def fam11_main(args, parser):
    """FAM11 (COV: techos ABL-COV T1–T6, ensamblado de 1.724 celdas y conciliación de 1.728 afirmaciones; COV12: B1 con U_C2 certificado y B2
    con L_K1 global sobre el B1 nuevo validado). Cálculo, validación, regeneración y comparación se informan por separado; el código 0
    corresponde solo al alcance hecho. COV y B1/B2 se ejecutan en procesos distintos (el cierre C0 de B1/B2 rechaza paper2b precargado)."""
    import os
    F = cargar("fam11", "fam11.py")
    t0 = time.time()
    if args.salida is not None and args.salida.exists():
        parser.error("la salida ya existe; elija otra ruta")
    if (args.b1 is not None or args.validacion_b1 is not None) and not (args.comando == "fam11-unidad" and args.tarea == "B2"):
        parser.error("--b1 y --validacion-b1 solo con fam11-unidad --tarea B2")
    lect = ("en_el_paquete", "fuera_del_paquete_y_del_interprete", "sin_manifiesto", "referencias_leidas", "referencia_esperada_leida")
    if args.comando == "fam11-unidad":
        if args.salida is None or args.tarea not in F.TAREAS + F.UNIDADES_B or args.unidad:
            parser.error("fam11-unidad requiere --tarea (una de %s, B1 o B2) y --salida (carpeta nueva)" % ", ".join(F.TAREAS))
        if args.tarea == "B2" and (args.b1 is None or args.validacion_b1 is None):
            parser.error("fam11-unidad --tarea B2 requiere --b1 (carpeta de fam11-unidad B1) y --validacion-b1 (su archivo de fam11-validar aceptado)")
        if sys.flags.hash_randomization or os.environ.get("PYTHONHASHSEED") != "0":
            parser.error("fam11-unidad exige PYTHONHASHSEED=0 efectivo: lance sin -I/-E (p. ej. -B -P -s -X utf8)")
        print(json.dumps({"tarea": args.tarea, "tope_trabajo_s": args.tope if args.tarea in F.TAREAS else None}, ensure_ascii=False), flush=True)
        r = F.correr(args.tarea, args.salida, args.b1, args.validacion_b1, tope=args.tope)
        claves = ("tarea", "unidad", "operacion", "resultado", "techos", "rc", "excepcion", "ultima_linea", "evidencia_sha256", "enlace_b1", "tiempos_s",
                  "termino", "exito")
        print(json.dumps({k: r.get(k) for k in claves if k in r}
                         | {"lecturas": {k: r["lecturas"][k] for k in lect[:4] + ("nucleo_c0_leidos", "codigo_fam11_leido")}}, ensure_ascii=False, indent=1, default=str))
        return 0 if r["exito"] else 1
    if args.comando == "fam11-ensamblar":
        if args.salida is None:
            parser.error("fam11-ensamblar requiere --salida (carpeta nueva) y una --entrada <tarea>=<carpeta de fam11-unidad|guardado> por tarea")
        ent = _entradas_fam08(args, parser)
        if set(ent) - set(F.TAREAS) or "pilotos" in ent:
            parser.error("fam11-ensamblar admite solo --entrada ABL-COV-T1…T6=<carpeta de fam11-unidad|guardado>")
        r = F.ensamblar(args.salida, ent)
        print(json.dumps({k: r.get(k) for k in ("naturaleza", "acredita", "entradas", "tiempos_s", "exito")}
                         | {n: {k: r[n].get(k) for k in ("rc", "veredicto", "excepcion")} for n in ("ensamblado", "conciliacion")}
                         | {"lecturas": {k: r["lecturas"][k] for k in lect}}, ensure_ascii=False, indent=1, default=str))
        return 0 if r["exito"] else 1
    if args.comando == "fam11-listar":
        r = F.listar()
        ok = True
    elif args.comando == "fam11-comprobar":
        r = F.comprobar()
        ok = r["cumple"]
    elif args.comando == "fam11-validar":
        if not (args.nueva and args.salida):
            parser.error("fam11-validar requiere --nueva (carpeta de fam11-unidad) y --salida (archivo nuevo)")
        r = F.validar(args.nueva)
        ok = r["aceptada"]
    elif args.comando == "fam11-comparar":
        con_val = args.tarea in F.TAREAS + F.UNIDADES_B
        if not (con_val or args.tarea == F.ENSAMBLADO) or not (args.nueva and args.salida) or (con_val and not args.validacion):
            parser.error("fam11-comparar requiere --tarea ABL-COV-T*, B1 o B2 (con --nueva de fam11-unidad y --validacion de fam11-validar) o "
                         "--tarea ENSAMBLADO (con --nueva de fam11-ensamblar), y --salida (archivo nuevo)")
        r = F.comparar(args.tarea, args.nueva, args.validacion)
        ok = r["estado"]["reproduccion"] == "aceptada"
    else:
        if args.salida is None:
            parser.error("fam11-receta requiere --salida (archivo nuevo)")
        r = F.receta()
        ok = True
    r["segundos"] = round(time.time() - t0, 3)
    if args.salida is not None:
        escribir(args.salida, r)
    resumen = {"comando": args.comando, "cumple": ok, "segundos": r["segundos"]}
    if args.comando == "fam11-listar":
        resumen.update(recuento=r["recuento"], pilotos=[p["unidad"] for p in r["pilotos"]["pilotos"]], calculo="ninguno")
    elif args.comando == "fam11-comprobar" and "comprobacion_interrumpida" in r:
        resumen.update(fuentes=r["fuentes"], comprobacion_interrumpida=r["comprobacion_interrumpida"], calculo="ninguno")
    elif args.comando == "fam11-comprobar":
        resumen.update({k: r[k] for k in ("fuentes", "procedencia", "nucleo", "motor", "pilotos", "receta")}, cobertura=r["cobertura"],
                       reconstruccion_b={u: {k: v for k, v in r["reconstruccion_b"][u].items() if k != "diferencias"} for u in ("B1", "B2")}
                       | {"cumple": r["reconstruccion_b"]["cumple"]},
                       referencias=r["referencias"], revalidacion_de_las_guardadas=r["revalidacion_de_las_guardadas"], libros=r["libros"], calculo="ninguno")
    elif args.comando == "fam11-validar":
        resumen.update(tarea=r["tarea"], unidad=r["unidad"], rc=r["rc"], veredicto=r["veredicto"], excepcion=r.get("excepcion"))
    elif args.comando == "fam11-comparar":
        objetos = {n: {k: o.get(k) for k in ("cobertura", "lineas_identicas", "n_discretas", "n_numericas", "vinculo")} for n, o in (r.get("objetos") or {}).items()}
        resumen.update(estado=r["estado"], objetos=objetos,
                       **{k: r[k] for k in ("naturaleza", "acredita", "entradas", "bytes_identicos_a_la_referencia", "derivados", "identidades", "operativos")
                          if k in r})
        for n in ("documentos", "salidas"):
            if n in r:
                resumen[n] = {d: {k: len(v[k]) for k in ("operativos", "ubicacion", "puerta", "vinculos", "discretas", "numericas")}
                              | {"vinculos_completos": v["vinculos_completos"]} for d, v in r[n].items()}
    else:
        resumen.update(estado=r["estado"], pasos=[p["paso"] for p in r["pasos"]], cobertura=r["cobertura"], calculo="ninguno")
    print(json.dumps(resumen, ensure_ascii=False, indent=1, default=str))
    return 0 if ok else 1


FAM09 = ("fam09-listar", "fam09-comprobar", "fam09-etapa", "fam09-validar", "fam09-comparar", "fam09-receta")


def fam09_main(args, parser):
    """FAM09 (T8: HIST, LAMBDA, CAPTURA, TESTIGO + INCORPORACION, C5B). Cada etapa escribe una carpeta nueva; la siguiente la consume con su
    registro de fam09-validar aceptado (--entrada clave=carpeta --entrada validacion_clave=registro). El testigo se calcula bajo el supervisor
    (límite externo 600 s). Cálculo, validación y comparación se informan por separado."""
    import os
    F = cargar("fam09", "fam09.py")
    t0 = time.time()
    if args.salida is not None and args.salida.exists():
        parser.error("la salida ya existe; elija otra ruta")
    if args.entrada and args.comando != "fam09-etapa":
        parser.error("--entrada solo con fam09-etapa")
    lect = ("en_el_paquete", "fuera_del_paquete_y_del_interprete", "sin_manifiesto", "referencias_leidas", "referencia_esperada_leida")
    if args.comando == "fam09-etapa":
        if args.salida is None or args.tarea not in F.ETAPAS:
            parser.error("fam09-etapa requiere --tarea (una de %s) y --salida (carpeta nueva)" % ", ".join(F.ETAPAS))
        if sys.flags.hash_randomization or os.environ.get("PYTHONHASHSEED") != "0":
            parser.error("fam09-etapa exige PYTHONHASHSEED=0 efectivo: lance sin -I/-E (p. ej. -B -P -s -X utf8)")
        ent = _entradas_fam08(args, parser)
        if "pilotos" in ent:
            parser.error("fam09-etapa admite --entrada <clave>=<carpeta> y --entrada validacion_<clave>=<registro>")
        print(json.dumps({"tarea": args.tarea, "entradas": sorted(ent)}, ensure_ascii=False), flush=True)
        r = F.correr(args.tarea, args.salida, ent)
        claves = ("tarea", "operacion", "naturaleza", "rc", "excepcion", "productos_sha256", "entradas9", "tiempos_s", "exito")
        det = {k: r["detalle"].get(k) for k in ("ultima_linea", "producto_sha256", "resultado_sha256", "segundos_trabajador", "cobertura", "paper2b",
                                                 "fallo", "pasos", "resumen") if k in r["detalle"]}
        print(json.dumps({k: r.get(k) for k in claves} | {"detalle": det}
                         | {"lecturas": {k: r["lecturas"][k] for k in lect + ("nucleo_lima1855_leidos", "instalacion_leidos", "d7_leidos")}},
                         ensure_ascii=False, indent=1, default=str))
        return 0 if r["exito"] else 1
    if args.comando == "fam09-listar":
        r = F.listar()
        ok = True
    elif args.comando == "fam09-comprobar":
        r = F.comprobar()
        ok = r["cumple"]
    elif args.comando == "fam09-validar":
        if not (args.nueva and args.salida):
            parser.error("fam09-validar requiere --nueva (carpeta de fam09-etapa) y --salida (archivo nuevo)")
        r = F.validar(args.nueva)
        ok = r["aceptada"]
    elif args.comando == "fam09-comparar":
        if args.tarea not in F.ETAPAS or not (args.nueva and args.salida and args.validacion):
            parser.error("fam09-comparar requiere --tarea (una de %s), --nueva (carpeta de fam09-etapa), --validacion (su registro de "
                         "fam09-validar) y --salida (archivo nuevo)" % ", ".join(F.ETAPAS))
        r = F.comparar(args.tarea, args.nueva, args.validacion)
        ok = r["estado"]["reproduccion"] == "aceptada"
    else:
        if args.salida is None:
            parser.error("fam09-receta requiere --salida (archivo nuevo)")
        r = F.receta()
        ok = True
    r["segundos"] = round(time.time() - t0, 3)
    if args.salida is not None:
        escribir(args.salida, r)
    resumen = {"comando": args.comando, "cumple": ok, "segundos": r["segundos"]}
    if args.comando == "fam09-listar":
        resumen.update(recuento=r["recuento"], pilotos=[p["unidad"] for p in r["pilotos"]["pilotos"]], calculo="ninguno")
    elif args.comando == "fam09-comprobar":
        resumen.update({k: r[k] for k in ("fuentes", "sustituciones", "declaracion", "pilotos", "referencias", "receta")}, calculo="ninguno")
    elif args.comando == "fam09-validar":
        resumen.update({k: r.get(k) for k in ("tarea", "rc", "veredicto", "excepcion", "conforme", "fallos", "u36", "inventario_sha256",
                                              "resultado_sha256", "aceptada")})
    elif args.comando == "fam09-comparar":
        resumen.update(estado=r["estado"], **{k: r[k] for k in ("producto_sha256", "bytes_identicos_al_aceptado", "frente_al_libro", "procedencia_por_resolucion", "transicion",
                                                                 "frente_a_rem147", "vinculos_derivados", "hist", "recuentos", "particion_por_operacion",
                                                                 "campos", "garantia",
                                                                 "diferencias_locales_resultado", "diferencias_cientificas_resultado",
                                                                 "diferencias_locales_validacion", "diferencias_validacion", "referencia", "cumple")
                                              if k in r})
    else:
        resumen.update(estado=r["estado"], pasos=[p["paso"] for p in r["pasos"]], cobertura=r["cobertura"], calculo="ninguno")
    print(json.dumps(resumen, ensure_ascii=False, indent=1, default=str))
    return 0 if ok else 1


FAM10 = ("fam10-comprobar", "fam10-etapa", "fam10-validar", "fam10-comparar", "fam10-receta", "fam10-tabla")


def fam10_main(args, parser):
    """FAM10 (tabla final de Exp8: ENF por afirmación, síntesis e integración de las doce COV). fam10-tabla es la orden única: encadena las tres
    etapas con su validación y después compara con las entregas aceptadas. Cálculo, validación y comparación se informan por separado."""
    import os
    F = cargar("fam10", "fam10.py")
    t0 = time.time()
    if args.salida is not None and args.salida.exists():
        parser.error("la salida ya existe; elija otra ruta")
    if args.entrada and args.comando not in ("fam10-etapa", "fam10-tabla"):
        parser.error("--entrada solo con fam10-etapa y fam10-tabla")
    if args.comando in ("fam10-etapa", "fam10-tabla"):
        if args.salida is None or (args.comando == "fam10-etapa" and args.tarea not in F.ETAPAS):
            parser.error("%s requiere --salida (carpeta nueva)%s" % (args.comando, " y --tarea (una de %s)" % ", ".join(F.ETAPAS)
                                                                     if args.comando == "fam10-etapa" else ""))
        if sys.flags.hash_randomization or os.environ.get("PYTHONHASHSEED") != "0":
            parser.error("%s exige PYTHONHASHSEED=0 efectivo: lance sin -I/-E (p. ej. -B -P -s -X utf8)" % args.comando)
        ent = _entradas_fam08(args, parser)
        if "pilotos" in ent:
            parser.error("%s admite --entrada <clave>=<carpeta|archivo>" % args.comando)
        print(json.dumps({"comando": args.comando, "tarea": args.tarea, "entradas": sorted(ent)}, ensure_ascii=False), flush=True)
        if args.comando == "fam10-etapa":
            r = F.correr(args.tarea, args.salida, ent)
            print(json.dumps({k: r.get(k) for k in ("tarea", "operacion", "rc", "excepcion", "productos_sha256", "segundos", "exito")}
                             | {"lecturas": {k: r["lecturas"][k] for k in ("en_el_paquete", "fuera_del_paquete_y_del_interprete", "referencias_leidas",
                                                                          "referencia_esperada_leida")}},
                             ensure_ascii=False, indent=1, default=str))
            return 0 if r["exito"] else 1
        r = F.tabla(ent, args.salida)
        escribir(args.salida / "tabla.json", r)
        print(json.dumps({k: r[k] for k in ("pasos", "comparaciones", "tabla_final", "cumple", "segundos")}, ensure_ascii=False, indent=1, default=str))
        return 0 if r["cumple"] else 1
    if args.comando == "fam10-comprobar":
        r = F.comprobar()
        ok = r["cumple"]
    elif args.comando == "fam10-validar":
        if not (args.nueva and args.salida):
            parser.error("fam10-validar requiere --nueva (carpeta de fam10-etapa) y --salida (archivo nuevo)")
        r = F.validar(args.nueva)
        ok = r["aceptada"]
    elif args.comando == "fam10-comparar":
        if args.tarea not in F.ETAPAS or not (args.nueva and args.salida and args.validacion):
            parser.error("fam10-comparar requiere --tarea (una de %s), --nueva (carpeta de fam10-etapa), --validacion (su registro de "
                         "fam10-validar) y --salida (archivo nuevo)" % ", ".join(F.ETAPAS))
        r = F.comparar(args.tarea, args.nueva, args.validacion)
        ok = r["estado"]["reproduccion"] == "aceptada"
    else:
        if args.salida is None:
            parser.error("fam10-receta requiere --salida (archivo nuevo)")
        r = F.receta()
        ok = True
    r["segundos"] = round(time.time() - t0, 3)
    if args.salida is not None:
        escribir(args.salida, r)
    resumen = {"comando": args.comando, "cumple": ok, "segundos": r["segundos"]}
    if args.comando == "fam10-comprobar":
        resumen.update({k: r[k] for k in ("fuentes", "sustituciones", "codigo", "referencias", "receta")}, calculo="ninguno")
    elif args.comando == "fam10-validar":
        resumen.update({k: r.get(k) for k in ("tarea", "validador", "comprobaciones", "estructura", "recuentos", "excepcion", "aceptada")})
    elif args.comando == "fam10-comparar":
        resumen.update(estado=r["estado"], **{k: r[k] for k in ("doce_claves", "frente_al_libro_rem148", "frente_al_libro_rem161", "frente_al_libro_rem171")
                                              if k in r})
    else:
        resumen.update(estado=r["estado"], pasos=[p["paso"] for p in r["pasos"]], cobertura=r["cobertura"], calculo="ninguno")
    print(json.dumps(resumen, ensure_ascii=False, indent=1, default=str))
    return 0 if ok else 1


FAM13 = ("fam13-comprobar", "fam13-reproducir", "fam13-receta")


def fam13_main(args, parser):
    """FAM13 (tablas y validaciones históricas; integridad S1). fam13-reproducir es la orden única: T1T2, T7, VALIDACIONES, MATRIZ_V4 y S1 con
    su validación independiente y, después, las comparaciones y el balance por producto. Sin entradas externas."""
    import os
    F = cargar("fam13", "fam13.py")
    t0 = time.time()
    if args.salida is None:
        parser.error("%s requiere --salida (%s)" % (args.comando, "carpeta nueva" if args.comando == "fam13-reproducir" else "archivo nuevo"))
    if args.salida.exists():
        parser.error("la salida ya existe; elija otra ruta")
    if args.entrada:
        parser.error("FAM13 no admite --entrada (todas las piezas están en el paquete)")
    if args.comando == "fam13-reproducir":
        if sys.flags.hash_randomization or os.environ.get("PYTHONHASHSEED") != "0":
            parser.error("fam13-reproducir exige PYTHONHASHSEED=0 efectivo: lance sin -I/-E (p. ej. -B -P -s -X utf8)")
        r = F.reproducir(args.salida)
        escribir(args.salida / "resumen.json", r)
        print(json.dumps({k: r[k] for k in ("pasos", "comparaciones", "productos_historicos", "S1", "U60", "F13_HISTORICAS_cumple", "F13_S1_conforme",
                                             "cumple", "segundos")}, ensure_ascii=False, indent=1, default=str))
        return 0 if r["cumple"] else 1
    if args.comando == "fam13-comprobar":
        r = F.comprobar()
        ok = r["cumple"]
    else:
        r = F.receta()
        ok = True
    r["segundos"] = round(time.time() - t0, 3)
    escribir(args.salida, r)
    resumen = {"comando": args.comando, "cumple": ok, "segundos": r["segundos"]}
    if args.comando == "fam13-comprobar":
        resumen.update({k: r[k] for k in ("fuentes", "sustituciones", "codigo", "referencias", "S1", "u60", "receta")}, calculo="ninguno")
    else:
        resumen.update(estado=r["estado"], pasos=[p["paso"] for p in r["pasos"]], cobertura=r["cobertura"], calculo="ninguno")
    print(json.dumps(resumen, ensure_ascii=False, indent=1, default=str))
    return 0 if ok else 1


FAM14 = ("fam14-comprobar", "fam14-reproducir", "fam14-receta")


def fam14_main(args, parser):
    """FAM14 (conciliaciones G/N rem174, §18.7 y adopción rem176). fam14-reproducir es la orden única: GN_REGEN (U62, validada con la ligadura
    G/N de U63), GN, LOC_187 y ADOPCION_176 y, después, la comparación por par y lado y el balance por producto. Sin entradas externas."""
    import os
    F = cargar("fam14", "fam14.py")
    t0 = time.time()
    if args.salida is None:
        parser.error("%s requiere --salida (%s)" % (args.comando, "carpeta nueva" if args.comando == "fam14-reproducir" else "archivo nuevo"))
    if args.salida.exists():
        parser.error("la salida ya existe; elija otra ruta")
    if args.entrada:
        parser.error("FAM14 no admite --entrada (todas las piezas están en el paquete)")
    if args.comando == "fam14-reproducir":
        if sys.flags.hash_randomization or os.environ.get("PYTHONHASHSEED") != "0":
            parser.error("fam14-reproducir exige PYTHONHASHSEED=0 efectivo: lance sin -I/-E (p. ej. -B -P -s -X utf8)")
        r = F.reproducir(args.salida)
        escribir(args.salida / "resumen.json", r)
        print(json.dumps({k: r[k] for k in ("pasos", "F14_GN_REGEN", "F14_GN", "F14_187", "F14_176", "balance", "cumple", "segundos")},
                         ensure_ascii=False, indent=1, default=str))
        return 0 if r["cumple"] else 1
    if args.comando == "fam14-comprobar":
        r = F.comprobar()
        ok = r["cumple"]
    else:
        r = F.receta()
        ok = True
    r["segundos"] = round(time.time() - t0, 3)
    escribir(args.salida, r)
    resumen = {"comando": args.comando, "cumple": ok, "segundos": r["segundos"]}
    if args.comando == "fam14-comprobar":
        resumen.update({k: r[k] for k in ("fuentes", "sustituciones", "codigo", "referencias", "integridad", "receta")}, calculo="ninguno")
    else:
        resumen.update(estado=r["estado"], pasos=[p["paso"] for p in r["pasos"]], cobertura=r["cobertura"], calculo="ninguno")
    print(json.dumps(resumen, ensure_ascii=False, indent=1, default=str))
    return 0 if ok else 1


GENERAL = ("general",)


def general_main(args, parser):
    """Comando general: plan (recetas lanzadas sin cálculo y llamadas ordenadas por datos), piloto (FAM08 + FAM11 + FAM12 -> FAM10 con las
    mismas llamadas) o completo (todas, Paso 3). Escribe plan.json, ejecucion.jsonl, balance.json y BALANCE.md en la carpeta nueva."""
    import os
    if args.reanudar:
        if args.salida is None:
            parser.error("general --reanudar requiere --salida <carpeta de la corrida que se reanuda>")
        if args.unidad or args.limite_ensayo_s is not None:
            parser.error("al reanudar, --unidad y --limite-ensayo-s no se dan: se toman de la corrida")
        if args.procesos_fam01 is not None and not 1 <= args.procesos_fam01 <= 12:
            parser.error("--procesos-fam01 admite de 1 a 12 (al reanudar, por omisión el de la corrida)")
        if sys.flags.hash_randomization or os.environ.get("PYTHONHASHSEED") != "0":
            parser.error("general exige PYTHONHASHSEED=0 efectivo: lance sin -I/-E (p. ej. -B -P -s -X utf8)")
        G = cargar("general", "general.py")
        try:
            r = G.reanudar(args.salida, parser, procesos_fam01=args.procesos_fam01, modo=args.modo)
        except G.ErrorGeneral as e:
            print(json.dumps({"comando": "general", "reanudar": args.salida.as_posix(), "error": str(e), "conforme": False}, ensure_ascii=False))
            return 1
        print(json.dumps(r["resumen"], ensure_ascii=False, indent=1, default=str))
        return 0 if r["conforme"] else 1
    if args.modo is None or args.salida is None:
        parser.error("general requiere --modo plan|piloto|completo|ensayo-fam01 (sin valor por omisión: el completo se elige expresamente) y "
                     "--salida (carpeta nueva dentro de la base)")
    if args.salida.exists():
        parser.error("la salida ya existe; elija otra ruta")
    if sys.flags.hash_randomization or os.environ.get("PYTHONHASHSEED") != "0":
        parser.error("general exige PYTHONHASHSEED=0 efectivo: lance sin -I/-E (p. ej. -B -P -s -X utf8)")
    procesos = 1 if args.procesos_fam01 is None else args.procesos_fam01
    if not 1 <= procesos <= 12:
        parser.error("--procesos-fam01 admite de 1 (por omisión: una llamada a la vez) a 12")
    if args.modo == "ensayo-fam01":
        if not args.unidad:
            parser.error("general --modo ensayo-fam01 requiere una o más --unidad (varias: misma selección y mismo grupo de techo caro)")
        if args.limite_ensayo_s is not None and not args.limite_ensayo_s > 0:
            parser.error("--limite-ensayo-s debe ser positivo")
    elif args.unidad or args.limite_ensayo_s is not None:
        parser.error("--unidad y --limite-ensayo-s solo con general --modo ensayo-fam01")
    G = cargar("general", "general.py")
    try:
        r = G.general(args.modo, args.salida, parser, procesos_fam01=procesos,
                      ensayo={"unidades": args.unidad, "limite_s": args.limite_ensayo_s} if args.modo == "ensayo-fam01" else None)
    except G.ErrorGeneral as e:
        print(json.dumps({"comando": "general", "modo": args.modo, "error": str(e), "conforme": False}, ensure_ascii=False))
        return 1
    print(json.dumps(r["resumen"], ensure_ascii=False, indent=1, default=str))
    return 0 if r["conforme"] else 1


def crear_parser():
    """La interfaz de órdenes (también la usa el comando general para comprobar que cada llamada del plan es una orden real)."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("comando", choices=("revisar", "p7", "p7-k1", "p7-suplemento", "q-local") + FAM01 + FAM02 + FAM03 + FAM04 + FAM05 + FAM06 + FAM07 + FAM08
                        + FAM11 + FAM09 + FAM10 + FAM13 + FAM14 + GENERAL)
    parser.add_argument("--modo", choices=("plan", "piloto", "completo", "ensayo-fam01"), help="general: plan (sin cálculo), piloto (FAM08 + FAM11 + "
                        "FAM12 -> FAM10), completo (todas las llamadas del plan; Paso 3) o ensayo-fam01 (las --unidad nombradas en un mismo "
                        "proceso, con sus comparaciones); sin valor por omisión")
    parser.add_argument("--procesos-fam01", type=int, help="general: llamadas de FAM01 simultáneas, de 1 a 12; por omisión 1 (una llamada a la vez); "
                        "las demás familias siempre una a una")
    parser.add_argument("--limite-ensayo-s", type=float, help="general --modo ensayo-fam01: límite externo del proceso de cálculo del ensayo, "
                        "si la orden lo fija; si no, el de la regla de grupos de techo")
    parser.add_argument("--reanudar", action="store_true", help="general: reanuda la corrida de --salida (existente) tras un corte: comprueba "
                        "versión del paquete, entorno y plan; reutiliza las llamadas aceptadas e intactas y repite las demás "
                        "(REANUDACION-PASO3-v1); --modo, si se da, debe ser el de la corrida")
    parser.add_argument("--salida", type=Path, help="archivo nuevo (p7, p7-k1, p7-suplemento, fam01-*) o carpeta nueva (q-local, fam01-unidad; "
                        "general: dentro de la base, p. ej. salidas/general/<carpeta nueva>)")
    parser.add_argument("--seleccion", choices=("R2", "R3"), help="fam01-unidad / fam01-comparar")
    parser.add_argument("--unidad", action="append", help="identificador estable de una unidad de la lista; repetible en fam01-unidad (tarea de varias unidades de la misma lista), una sola en fam01-comparar y fam01-na")
    parser.add_argument("--nueva", type=Path, help="carpeta de salida de fam01-unidad (fam01-comparar) o de fam02-unidad (fam02-comparar)")
    parser.add_argument("--tarea", help="fam02-unidad / fam02-validar / fam02-comparar: tarea R1 (las 18 conectadas; ver fam02-receta); "
                        "fam03-unidad / fam03-comparar: tarea PROD del plan (las 136; ver fam03-receta); "
                        "fam04-unidad / fam04-comparar: L1-ELAST, L1-LAMBDA o L1-COORD (con --unidad, una frontera, conjunto o clave transformada); "
                        "fam05-unidad / fam05-comparar: L1-ELAST o L1-LAMBDA del lote 2 (con --unidad, una malla nueva, SUPLEMENTO o un par conjunto|país); "
                        "fam06-comparar: L1-ELAST (salida de fam06-unidad) o CONCILIACION (salida de fam06-conciliar); "
                        "fam07-unidad / fam07-comparar: L1-COORD-R1, L1-COORD-R2 o L1-COORD-R3 (fam07-comparar también ENSAMBLADO); "
                        "fam08-unidad / fam08-comparar: L1-ELAST (con --unidad, una malla ENF) o ABL-ENF-T1…T6 (fam08-comparar también PARES, "
                        "RECUPERACION e INTEGRAL); fam11-unidad / fam11-comparar: ABL-COV-T1…T6, B1 o B2 (fam11-comparar también ENSAMBLADO); "
                        "fam09-etapa / fam09-comparar: HIST, LAMBDA, CAPTURA, TESTIGO, INCORPORACION o C5B; "
                        "fam10-etapa / fam10-comparar: ENF, SINTESIS o INTEGRACION")
    parser.add_argument("--hoja", action="append", help="fam02-unidad: afirmación ci-df de la tarea (asignación parcial); repetible; sin --hoja, la tarea completa")
    parser.add_argument("--tope", type=float, default=2400.0, help="fam02-unidad: límite externo de la invocación en s (ruta histórica: 2400; piloto: 600); "
                        "fija --tope-proceso = max(60, tope - 300) y deja --tope-afirmacion 300; fam03-unidad: tope EFECTIVO del reloj interno de la "
                        "tarea (como --tope-efectivo de tarea_prod; por defecto el del plan, 2400); el límite externo lo pone el supervisor; "
                        "fam04-unidad / fam05-unidad: tope de trabajo de la suite (2400); reloj interno = tope − 120 (2280, como el conductor del lote)")
    parser.add_argument("--enlazar", action="store_true", help="fam02-validar, rutas por comando: si el cálculo de origen terminó y la revalidación "
                        "cumple, escribe el enlace local en la ejecución de --salida (<ejecucion>/<tarea>); el origen no se toca")
    parser.add_argument("--salidas-guardadas", action="store_true", help="fam02-unidad, rutas por comando (A*, B*, F): PRUEBA DE CONEXIÓN SIN CÁLCULO "
                        "con la salida guardada de cada comando en lugar de ejecutarlo; se enlaza con reproduccion=false y nunca cuenta como reproducción")
    parser.add_argument("--validacion", type=Path, help="fam04-comparar / fam05-comparar / fam06-comparar L1-ELAST: archivo de fam04-validar / fam05-validar / "
                        "fam06-validar de la misma carpeta --nueva")
    parser.add_argument("--e4", help="fam06-conciliar: lado E4 = carpeta de fam06-unidad (validada) o «guardado» (producto aceptado del paquete)")
    parser.add_argument("--lote2", help="fam06-conciliar: lado de origen = carpeta de fam05-unidad L1-ELAST completa (validada) o «guardado»")
    parser.add_argument("--validacion-e4", type=Path, help="fam06-conciliar: archivo de fam06-validar de la carpeta --e4")
    parser.add_argument("--validacion-lote2", type=Path, help="fam06-conciliar: archivo de fam05-validar de la carpeta --lote2")
    parser.add_argument("--entrada", action="append", help="fam07-ensamblar: <tarea>=<carpeta de fam07-unidad|guardado>, una por tarea de la partición; "
                        "una tarea sin --entrada no se sustituye por su referencia (el ensamblado se rechaza); "
                        "fam08-integrar: ABL-ENF-T1…T6=<carpeta de fam08-unidad|guardado>, mallas=<carpeta|guardado>, piloto=<carpeta de una "
                        "malla piloto validada como <carpeta>.validacion.json> (repetible, solo con mallas=guardado) y certificado=<archivo "
                        "reemitido por fam08-recuperar> (opcional); fam08-conciliar: mallas= y piloto=; fam08-recuperar: ABL-ENF-T1=; "
                        "fam11-ensamblar: ABL-COV-T1…T6=<carpeta de fam11-unidad|guardado>, una por tarea; "
                        "fam09-etapa: <clave>=<carpeta de fam09-etapa> y validacion_<clave>=<registro de fam09-validar aceptado> "
                        "(CAPTURA: lambda; INCORPORACION: captura y testigo; C5B: testigo_vista); "
                        "fam10-etapa / fam10-tabla: <clave>=<carpeta|archivo dentro de la base> (ver fam10-receta: ENF: enf_integral y "
                        "registro_enf_integral; SINTESIS: enf, validacion_enf, cov, registro_cov, p7, q_local; INTEGRACION: sintesis, "
                        "validacion_sintesis, b1, validacion_b1, b2, validacion_b2; fam10-tabla: las de ENF, cov, registro_cov, p7, q_local y las de B1/B2)")
    parser.add_argument("--b1", type=Path, help="fam11-unidad --tarea B2: carpeta de fam11-unidad B1 (el B1 NUEVO; nunca el histórico)")
    parser.add_argument("--validacion-b1", type=Path, help="fam11-unidad --tarea B2: archivo de fam11-validar ACEPTADO de esa carpeta B1")
    return parser


def main():
    prioridad_alta()
    parser = crear_parser()
    args = parser.parse_args()
    if (args.modo is not None or args.procesos_fam01 is not None or args.limite_ensayo_s is not None or args.reanudar) and args.comando not in GENERAL:
        parser.error("--modo, --procesos-fam01, --limite-ensayo-s y --reanudar solo con general")
    errores = revisar()
    if errores:
        print(json.dumps({"errores": errores}, ensure_ascii=False))
        return 1
    if args.comando in FAM01:
        return fam01_main(args, parser)
    if args.comando in FAM02:
        return fam02_main(args, parser)
    if args.comando in FAM03:
        return fam03_main(args, parser)
    if args.comando in FAM04:
        return fam04_main(args, parser)
    if args.comando in FAM05:
        return fam05_main(args, parser)
    if args.comando in FAM06:
        return fam06_main(args, parser)
    if args.comando in FAM07:
        return fam07_main(args, parser)
    if args.comando in FAM08:
        return fam08_main(args, parser)
    if args.comando in FAM11:
        return fam11_main(args, parser)
    if args.comando in FAM09:
        return fam09_main(args, parser)
    if args.comando in FAM10:
        return fam10_main(args, parser)
    if args.comando in FAM13:
        return fam13_main(args, parser)
    if args.comando in FAM14:
        return fam14_main(args, parser)
    if args.comando in GENERAL:
        return general_main(args, parser)
    if args.comando == "revisar":
        print("Archivos y sintaxis conformes. Ningún cálculo ejecutado.")
        return 0
    if args.salida is None:
        parser.error(f"{args.comando} requiere --salida con una ruta nueva")
    if args.salida.exists():
        parser.error("la salida ya existe; elija otra ruta")
    if args.comando == "p7":
        resultado = piloto()
        escribir(args.salida, resultado)
        print(json.dumps({"salida": str(args.salida), "concordante": resultado["comparacion_exacta"]}))
        return 0 if resultado["comparacion_exacta"] else 1
    if args.comando == "q-local":
        resultado = q_local(args.salida)
        concordante = resultado["concordante"]
    else:
        resultado = p7_k1() if args.comando == "p7-k1" else p7_suplemento()
        concordante = resultado.get("comparacion_exacta", resultado.get("concordante"))
        if args.comando == "p7-k1":
            resultado["dependencias"] = dependencias()
        escribir(args.salida, resultado)
    print(json.dumps({"salida": str(args.salida), "concordante": concordante, "segundos": resultado["segundos"]}, ensure_ascii=False))
    return 0 if concordante else 1


if __name__ == "__main__":
    raise SystemExit(main())
