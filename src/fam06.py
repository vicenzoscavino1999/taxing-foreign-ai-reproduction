"""FAM06 (E4: mallas G/N del lote 2 y su conciliación): comprobación sin cálculo de entradas, referencias y cobertura; cálculo de E4 o
de una malla seleccionada por la ruta de tarea_lote.py del lote 2 con el núcleo C0 y el manifiesto E4; validación por validar_lote.py del
lote 2; comparación con la ejecución aceptada rem121; conciliación G/N con el productor histórico (rutas explícitas) y su comparación con
la conciliación aceptada; receta completa (sin ejecutarla).

Operaciones del catálogo (no se confunden):
- F06-MALLAS (RN): L1-ELAST con LOTE2E4_MANIFIESTO.json: 383 mallas nuevas, una por contenido con un solo diseño (clave
  «diseño|j|frontier_id»; 172 d, 101 f y 110 df) con 4.115 nodos; cada nodo da una fila «point» y, si y solo si hay kink, sus filas
  left_limit/right_limit; cada fila lleva su topología del núcleo C0. Sin suplemento ni λπ (el anexo E4 no tiene conjuntos).
- F06-CONCILIACION (RD): regeneración documental y aritmética de 391 pares G/N = 383 contrapartes E4 (malla E4 frente a su malla de origen
  del producto L1-ELAST del lote 2) + 8 pares existentes del manifiesto E4 (ambas mallas en el lote 2); 4.155 puntos emparejados. Por par:
  vínculo (clave estructural, instrumento, dominio τ, diseños G y N), mismos puntos, campos comunes, campos que difieren, topologías, kinks y
  nulos. No impone igualdad numérica entre G y N, no trata un kink como error ni un nulo como cero; las diferencias de topología son
  resultados del contraste. No es otro cálculo del modelo.

Piezas: las de FAM05 sin cambios (código del lote 2 U17/U18, núcleo C0 con su inventario, manifiesto del lote 2 y su producto L1-ELAST
aceptado con el suplemento, lado de origen de la conciliación) y las de fuentes_fam06.json (datos/fam06: manifiesto E4, anexo E4 y alcance;
nucleo_s6/e4: productor de la conciliación; referencias/fam06/rem121).

Adaptaciones (no cambian fórmulas, mallas, tolerancias, presupuestos ni criterios):
- las de FAM05 reutilizadas sin cambios desde src/fam05.py: TAREA-AST-v2, FIN-v1, PUERTA-v1, NUCLEO-C0-v1, SELECCION-UNIDAD-v1,
  VALIDADOR-v2 (mismas sustituciones) y RELOJ-PILOTO-v1 (2400 − 120 = 2280 s; el límite externo lo pone el supervisor);
- MANIFIESTO-E4-v1: la misma ruta con el manifiesto y el anexo E4 explícitos (datos/fam06). R (raíz de las rutas relativas del
  manifiesto) = datos/fam06; E4 no declara rutas relativas (sin suplemento), así que no se lee nada a través de R;
- CONCILIADOR-v1: conciliacion_e4_rem121.py se ejecuta desde sus bytes exactos con las sustituciones de SUSTITUCIONES_CONCILIADOR (cada
  original, una sola vez): rutas explícitas de manifiestos y productos (en lugar de la raíz y el área de rem121); las huellas fijas del
  producto del lote 2 se sustituyen por las que declara SU resultado.json (como ya hacía con E4) y la autenticación de cada lado pasa al
  adaptador (guardado: huella del catálogo; nuevo: validación aceptada de esos bytes); selección opcional de pares (pilotos); y el universo
  padre (572 constante) se deriva de los manifiestos (fronteras cubiertas por el lote 2 ∪ orígenes de E4). Nunca lee la conciliación
  esperada para producir la suya.
"""
from __future__ import annotations

import builtins
import contextlib
import importlib.util
import io
import json
import sys
import time
import traceback
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
DATOS = BASE / "datos" / "fam06"
REF = BASE / "referencias" / "fam06" / "rem121"
REF_CONC = REF / "conciliacion" / "CONCILIACION_E4_REM121.json"
CONC = BASE / "nucleo_s6" / "e4" / "conciliacion_e4_rem121.py"
CONC_SHA = "5ccb9f8fe668e08cf192a82bedf4b5c480147c4a0726da656270d01e03b88721"
MANIFIESTO = ("LOTE2E4_MANIFIESTO.json", "d430b39db2cea7801cdcf8b55f0455063270d58f5aebea57776241fcde04b4af")
ANEXO = ("COBERTURA_NACIONAL_LOTE2E4.json", "6015226d99b7b2a2b959f3990666142bea16eb1b929eee1923532c7303a8ee80")
ALCANCE = ("alcance_lote2e4.json", "5471d1d3728b84b63b195ae6afe5c70c6ee3bb27a3ebef91c222c967fc3ff067")
TAREA = "L1-ELAST"
TAREAS = ("L1-ELAST", "CONCILIACION")
PRODUCTO = "frontier_result.jsonl"
PRODUCTO_CONC = "CONCILIACION_E4.json"
GUARDADO = "guardado"
OPERACIONES = {"F06-MALLAS": "L1-ELAST con el manifiesto E4 (383 mallas nuevas, 4.115 nodos)",
               "F06-CONCILIACION": "391 pares G/N (383 contrapartes E4 + 8 existentes; 4.155 puntos)"}
ETIQUETA = "REPRODUCCION LIMPIA FAM06 NO OFICIAL"
REGENERACION = "regeneración sobre entradas guardadas"
ADAPTACIONES = ("TAREA-AST-v2", "FIN-v1", "PUERTA-v1", "NUCLEO-C0-v1", "SELECCION-UNIDAD-v1", "VALIDADOR-v2", "RELOJ-PILOTO-v1",
                "MANIFIESTO-E4-v1")
# producto de cada objeto en el catálogo: (operación, id). E4 y su conciliación (FAM06); lado de origen = productos del lote 2 (FAM05).
REF_CATALOGO = {PRODUCTO: ("F06-MALLAS", "P_e4_frontier"), "CONCILIACION_E4_REM121.json": ("F06-CONCILIACION", "P_conc_e4")}
ORIGEN_CATALOGO = {"frontier_result.jsonl": ("F05-ELAST-C0", "P_elast_lote2"),
                   "suplemento_procedencia.jsonl": ("F05-ELAST-HIST", "L_rem121:suplemento_procedencia.jsonl")}
SUSTITUCIONES_CONCILIADOR = (
    ("RUTAS-EXPLICITAS", 'R, A, SAL = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])\nT = R / "tmp"',
     'ENT, SAL = json.loads(sys.argv[1]), Path(sys.argv[2])\nSEL = ENT["pares"]'),
    ("RUTAS-PRODUCTOS", 'L = T / "paso4_suplemento_topologia_desde_rem119/lote2"\nE4 = A / "lote2e4_REM121_E4/L1-ELAST"\n'
                        'ACC = T / "paso4_lote2_e4_desde_rem120/lote2_REM120_LOTE2/L1-ELAST/salida"',
     'E4 = Path(ENT["e4"])\nACC = Path(ENT["lote2"]) / "salida"'),
    ("HUELLAS-DECLARADAS-LOTE2", 'assert HF(ACC / "frontier_result.jsonl") == "007095a94b7d1fce18aea6214c56c45b370e9a6eb5b0e415da6a0cc09a26ea8c"\n'
                                 'assert HF(ACC / "suplemento_procedencia.jsonl") == "d6a12af3818993288d8b1f1cbbb87eb7cb64bf2ee25492ae4ff1d95cc2e55b39"',
     'res2 = json.loads((ACC.parent / "resultado.json").read_bytes())\n'
     'assert HF(ACC / "frontier_result.jsonl") == next(p["sha256"] for p in res2["productos"] if p["archivo"] == "frontier_result.jsonl")\n'
     'assert HF(ACC / "suplemento_procedencia.jsonl") == next(p["sha256"] for p in res2["productos"] if p["archivo"] == "suplemento_procedencia.jsonl")'),
    ("RUTAS-MANIFIESTOS", 'm2 = json.loads((L / "LOTE2_MANIFIESTO.json").read_bytes())["L1-ELAST"]\n'
                          'm4 = json.loads((L / "LOTE2E4_MANIFIESTO.json").read_bytes())["L1-ELAST"]\n'
                          'assert HF(L / "LOTE2E4_MANIFIESTO.json") == "d430b39db2cea7801cdcf8b55f0455063270d58f5aebea57776241fcde04b4af"',
     'm2 = json.loads(Path(ENT["manifiesto_lote2"]).read_bytes())["L1-ELAST"]\n'
     'm4 = json.loads(Path(ENT["manifiesto_e4"]).read_bytes())["L1-ELAST"]\n'
     'assert HF(ENT["manifiesto_e4"]) == "d430b39db2cea7801cdcf8b55f0455063270d58f5aebea57776241fcde04b4af"'),
    ("SEL-PARES-E4", 'for k4, v4 in m4["fronteras"].items():',
     'for k4, v4 in [(k, v) for k, v in m4["fronteras"].items() if SEL is None or "E4:" + v["frontier_id"] in SEL]:'),
    ("SEL-PARES-EXISTENTES", 'for i, pe in enumerate(m4["pares_existentes"]):',
     'for i, pe in [(i, pe) for i, pe in enumerate(m4["pares_existentes"]) if SEL is None or "existente:%d" % i in SEL]:'),
    ("PADRES-DERIVADOS", 'pend = [p for p in pares if not p["conciliado"]]',
     'pend = [p for p in pares if not p["conciliado"]]\n'
     '_cub = set(m2["equivalencias_aceptadas"])\n'
     'for _v in m2["fronteras"].values():\n'
     '    _cub |= {_v["frontier_id"], *(_v.get("frontier_ids_equivalentes") or []), *(_v.get("equivalentes_aceptados_por_contenido") or [])}\n'
     'PADRES = len(_cub | {x for _v in m4["fronteras"].values() for x in _v["origen"]["frontier_ids_origen"]})'),
    ("PADRES-SALIDA", '"universo_padre_sin_cambio": 572', '"universo_padre_sin_cambio": PADRES'))


class Fam06Error(RuntimeError):
    pass


def need(t, codigo):
    if not t:
        raise Fam06Error(codigo)


def fuentes() -> dict:
    return leer(BASE / "fuentes_fam06.json")


def piezas() -> list:
    """fuentes_fam06.json (archivos y reutilizados de FAM05) y los archivos copiados del núcleo C0 (fuentes_fam05.json)."""
    fu = fuentes()
    c0 = [dict(x, papel="núcleo C0 (reutilizado de FAM05)") for x in F5.fuentes()["archivos"] if x["archivo"].startswith("nucleo_s6/c0/")]
    return fu["archivos"] + fu["reutilizados_de_fam05"] + c0


def uso_de(x: dict) -> str:
    p, a = x["papel"], x["archivo"]
    if p.startswith("referencia"):
        return "referencia"
    if p.startswith("entrada guardada"):
        return "entrada_guardada"
    if a.startswith("nucleo_s6/e4/") or p.startswith("entrada de F06-CONCILIACION"):
        return "conciliacion"
    return "comun"


def fuentes_alteradas(uso: str = "todo") -> list:
    """Piezas ausentes o con otra huella. calculo: lo que usa F06-MALLAS; conciliacion: lo que usa F06-CONCILIACION salvo las entradas
    guardadas, que se autentican por lado (y nunca las referencias: la conciliación no lee la esperada)."""
    adm = {"todo": None, "calculo": {"comun"}, "conciliacion": {"comun", "conciliacion"}}[uso]
    return [x["archivo"] for x in piezas() if (adm is None or uso_de(x) in adm) and sha_archivo(BASE / x["archivo"]) != x["sha256"]]


def manifiesto() -> tuple:
    raw = (DATOS / MANIFIESTO[0]).read_bytes()
    need(sha(raw) == MANIFIESTO[1], "MANIFIESTO_E4_DISTINTO")
    man = json.loads(raw)
    need(not str(man.get("kind", "")).endswith("-SINTETICO"), "MANIFIESTO_SINTETICO")
    return raw, man


def anexo() -> dict:
    raw = (DATOS / ANEXO[0]).read_bytes()
    need(sha(raw) == ANEXO[1], "ANEXO_E4_DISTINTO")
    return json.loads(raw)


def catalogo_dato(op: str, ident: str) -> str | None:
    o = next((o for o in leer(BASE / "catalogo.json")["operaciones"] if o["clave"] == op), None)
    return next((p["sha256_aceptado"] for p in (o or {}).get("datos_configuracion", []) if p["id"] == ident), None)


# ================================================================================================ unidades y pilotos
def unidades(man: dict) -> list:
    return [{"unidad": v["frontier_id"], "operacion": "F06-MALLAS", "clave": k, "diseno": k.split("|")[0], "instrumento": k.split("|")[1],
             "dimension_malla": v["dimension_malla"], "nodos": v["puntos_frontier_n4"], "par": "E4:" + v["frontier_id"],
             "malla_de_origen": v["origen"]["malla_de_origen"]} for k, v in man["L1-ELAST"]["fronteras"].items()]


def seleccion(man: dict, unidad: str | None):
    """Filtro de MALLAS del manifiesto E4 (nunca de sus nodos ni de su soporte). None = las 383."""
    if unidad is None:
        return None
    need(unidad in {v["frontier_id"] for v in man["L1-ELAST"]["fronteras"].values()}, "MALLA_FUERA_DEL_MANIFIESTO_E4: %s" % unidad)
    return {"fronteras": [unidad]}


def regla_pilotos(man: dict) -> dict:
    fr_ = man["L1-ELAST"]["fronteras"]
    pil = []
    for j in ("d", "f", "df"):
        k = next(k for k in fr_ if k.split("|")[1] == j)
        v = fr_[k]
        pil.append({"tarea": TAREA, "operacion": "F06-MALLAS", "unidad": v["frontier_id"], "clave": k, "instrumento": j, "par": "E4:" + v["frontier_id"],
                    "malla_de_origen": v["origen"]["malla_de_origen"],
                    "cobertura": ("malla E4 completa: %d nodos (frontier_n = 4, dimensión %d) con sus filas laterales si hay kink y su topología; "
                                  "su pareja G/N se concilia con la malla de origen autenticada del lote 2") % (v["puntos_frontier_n4"], v["dimension_malla"])})
    return {"regla": ("fijados por identificador desde el MANIFIESTO E4 (entrada), antes de calcular y sin mirar resultados: la primera malla de "
                      "cada instrumento d, f y df en el orden del manifiesto; cada piloto es la malla entera (todos sus nodos y laterales)"),
            "pilotos": pil}


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
    el = man["L1-ELAST"]
    return {"comando": "fam06-listar", "calculo": "ninguno", "manifiesto_sha256": sha(raw), "operaciones": OPERACIONES,
            "recuento": {"mallas": len(u), "nodos": sum(x["nodos"] for x in u), "por_instrumento": dict(Counter(x["instrumento"] for x in u)),
                         "por_diseno": dict(Counter(x["diseno"] for x in u)), "pares_existentes": len(el["pares_existentes"]),
                         "pares": len(u) + len(el["pares_existentes"])},
            "unidades": u, "pares_existentes": el["pares_existentes"], "pilotos": fijar_pilotos(man)}


# ================================================================================================ comprobación (sin cálculo científico)
def cobertura_manifiesto(man: dict) -> dict:
    """Mallas y nodos del manifiesto E4 (malla de nodos del núcleo, sin evaluar) y pares G/N contra el manifiesto del lote 2: vínculo de cada
    contraparte con su malla de origen (misma clave estructural, instrumento, dominio τ y malla; otro diseño), pares existentes, puntos
    emparejados y universo padre (fronteras cubiertas por el lote 2 ∪ orígenes de E4)."""
    F5.preparar()
    from paper2b.run import RunConfig
    from paper2b.supremum import axes, nodes
    n = RunConfig().frontier_n
    m2 = leer(F5.DATOS / F5.MANIFIESTO[0])["L1-ELAST"]
    el = man["L1-ELAST"]
    mot = []
    ids2 = {v["frontier_id"]: (k, v) for k, v in m2["fronteras"].items()}
    cub = set(m2["equivalencias_aceptadas"])
    for v in m2["fronteras"].values():
        cub |= {v["frontier_id"], *(v.get("frontier_ids_equivalentes") or []), *(v.get("equivalentes_aceptados_por_contenido") or [])}
    total, por_j, por_d, por_dim, pares_j, origenes, puntos_exist = 0, Counter(), Counter(), Counter(), Counter(), set(), 0
    for k, v in el["fronteras"].items():
        d, j = k.split("|")[:2]
        (dl, dh), (fl, fh) = axes(j, float(v["dominio_tau"]["tau_d_upper"]), float(v["dominio_tau"]["tau_f_upper"]))
        m = len(nodes(dl, dh, n) if dh > dl else [dl]) * len(nodes(fl, fh, n) if fh > fl else [fl])
        total += m
        por_j[j] += 1
        por_d[d] += 1
        por_dim["dim%d" % v["dimension_malla"]] += 1
        if m != v["puntos_frontier_n4"]:
            mot.append("MALLA_DISTINTA_DEL_MANIFIESTO: %s" % v["frontier_id"])
        if [p for p in F5.CLAVES_ESTRUCTURALES if p not in v["clave_estructural"]] or not v["dominio_tau"]:
            mot.append("CLAVE_O_DOMINIO_INCOMPLETO: %s" % k)
        if v.get("suplemento_topologia"):
            mot.append("SUPLEMENTO_EN_E4: %s" % k)
        o = v["origen"]
        ko = o["malla_de_origen"]
        vo = m2["fronteras"].get(ko)
        if (vo is None or vo["clave_estructural"] != v["clave_estructural"] or vo["dominio_tau"] != v["dominio_tau"] or ko.split("|")[1] != j
                or ko.split("|")[0] == d or o.get("diseno_origen") != ko.split("|")[0] or o.get("frontier_id_representante") != vo["frontier_id"]
                or vo["puntos_frontier_n4"] != v["puntos_frontier_n4"]):
            mot.append("PAREJA_CON_CLAVE_DOMINIO_O_MALLA_DISTINTOS: %s" % k)
        if v["frontier_id"] in cub:
            mot.append("CONTRAPARTE_YA_ES_FRONTERA_PADRE: %s" % k)
        origenes |= set(o["frontier_ids_origen"])
        pares_j[j] += 1
    for i, pe in enumerate(el["pares_existentes"]):
        g, nn = ids2.get(pe["G"]), ids2.get(pe["N"])
        if not (g and nn and g[0].split("|")[0] == "G" and nn[0].split("|")[0] == "N" and g[0].split("|")[1] == nn[0].split("|")[1] == pe["j"]
                and g[1]["clave_estructural"] == nn[1]["clave_estructural"] and g[1]["dominio_tau"] == nn[1]["dominio_tau"]):
            mot.append("PAR_EXISTENTE_INCONSISTENTE: %d" % i)
            continue
        pares_j[pe["j"]] += 1
        puntos_exist += g[1]["puntos_frontier_n4"]
    pares = len(el["fronteras"]) + len(el["pares_existentes"])
    if total != el["puntos_totales_frontier_n4"]:
        mot.append("TOTAL_DE_PUNTOS_DISTINTO_DE_LA_MALLA")
    if pares != el["pares_tras_la_opcion"]:
        mot.append("PARES_DISTINTOS_DEL_MANIFIESTO")
    if el.get("topologia_requerida") is not True:
        mot.append("TOPOLOGIA_NO_REQUERIDA")
    if man.get("L1-LAMBDA") != {}:
        mot.append("E4_CON_LAMBDA")
    nuevos = origenes - cub
    if nuevos:
        mot.append("PADRES_NUEVOS: %d" % len(nuevos))
    return {"mallas": len(el["fronteras"]), "nodos": total, "frontier_n": n, "por_instrumento": dict(por_j), "por_diseno": dict(por_d),
            "por_dimension": dict(por_dim),
            "pares": {"total": pares, "contrapartes_e4": len(el["fronteras"]), "existentes": len(el["pares_existentes"]), "por_instrumento": dict(pares_j),
                      "puntos_emparejados": total + puntos_exist, "puntos_de_los_existentes": puntos_exist},
            "universo_padre": {"fronteras_cubiertas_lote2": len(cub), "origenes_e4": len(origenes), "padres_nuevos": len(nuevos), "total": len(cub | origenes)},
            "cumple": not mot, "motivos": mot}


def resumen_conciliacion(c: dict) -> dict:
    d = c.get("detalle") or []
    topo = [p for p in d if p.get("topologia_igual_en_puntos") != p.get("puntos")]
    return {"pares": len(d), "pares_unicos": len({p["par"] for p in d}), "puntos_emparejados": sum(p.get("puntos", 0) for p in d),
            "conciliados": sum(1 for p in d if p.get("conciliado") is True), "pendientes": len(c.get("pendientes") or []),
            "diferencias_de_topologia": {"pares": len(topo), "puntos": sum(p["puntos"] - p["topologia_igual_en_puntos"] for p in topo if p.get("topologia_igual_en_puntos") is not None)},
            "por_instrumento": dict(Counter(p["instrumento"] for p in d)), "universo_padre": c.get("universo_padre_sin_cambio"),
            "pares_con_kink": c.get("pares_con_kink")}


def cobertura_referencias(man: dict) -> dict:
    mot, r = [], {}
    res = leer(REF / "L1-ELAST/resultado.json")
    val = json.loads((REF / "L1-ELAST/validacion_stdout.txt").read_text(encoding="utf-8"))
    if res.get("estado") != "completa" or res.get("manifiesto_sha256") != MANIFIESTO[1] or val.get("dictamen") != "completa_validada" or val.get("n_fallos") != 0:
        mot.append("REFERENCIA_NO_ACEPTADA: L1-ELAST")
    if res["codigo_sha256"] != {k: F5.CODIGO[k] for k in ("tarea_lote.py", "conexion_lambda.py", "conexion_frontera.py")}:
        mot.append("REFERENCIA_DE_OTRO_CODIGO")
    f = REF / "L1-ELAST/salida" / PRODUCTO
    h = sha_archivo(f)
    fr = leer_jsonl(f) if h else []
    decl = {p["archivo"]: p for p in res["productos"]}
    if h is None or h != F5.catalogo_sha(*REF_CATALOGO[PRODUCTO]) or decl.get(PRODUCTO, {}).get("sha256") != h or decl.get(PRODUCTO, {}).get("filas") != len(fr):
        mot.append("REFERENCIA_ALTERADA_O_AJENA: %s" % PRODUCTO)
    por_f = Counter(x["frontier_id"] for x in fr if x["side"] == "point")
    if dict(por_f) != {v["frontier_id"]: v["puntos_frontier_n4"] for v in man["L1-ELAST"]["fronteras"].values()}:
        mot.append("REFERENCIA_E4_CON_OTROS_NODOS")
    claves = [(x["frontier_id"], x["point_id"], x["side"]) for x in fr]
    r[PRODUCTO] = {"filas": len(fr), "sha256": h, "lados": dict(Counter(x["side"] for x in fr)), "kinks": sum(1 for x in fr if x["kink_adjacent"] is True),
                   "filas_duplicadas": len(claves) - len(set(claves)), "motivos": dict(Counter(str(x["reason_code"]) for x in fr)),
                   "auditoria": dict(Counter(x["audit_status"] for x in fr)), "con_topologia": sum(1 for x in fr if isinstance(x.get("topology"), str) and x["topology"])}
    craw = REF_CONC.read_bytes() if REF_CONC.is_file() else b""
    if sha(craw) != F5.catalogo_sha(*REF_CATALOGO["CONCILIACION_E4_REM121.json"]):
        mot.append("REFERENCIA_ALTERADA_O_AJENA: CONCILIACION_E4_REM121.json")
    c = json.loads(craw) if craw else {}
    if c.get("producto_e4_sha256") != h or c.get("producto_elast_aceptado_sha256") != F5.catalogo_sha(*ORIGEN_CATALOGO["frontier_result.jsonl"]):
        mot.append("CONCILIACION_DE_REFERENCIA_LIGADA_A_OTROS_PRODUCTOS")
    r["conciliacion"] = dict(resumen_conciliacion(c), sha256=sha(craw), producto_e4_sha256=c.get("producto_e4_sha256"),
                             producto_elast_aceptado_sha256=c.get("producto_elast_aceptado_sha256"))
    org = {}
    for n in ORIGEN_CATALOGO:
        org[n] = sha_archivo(F5.REF / "L1-ELAST/salida" / n)
        if org[n] != F5.catalogo_sha(*ORIGEN_CATALOGO[n]):
            mot.append("ORIGEN_GUARDADO_ALTERADO_O_AJENO: %s" % n)
    r["origen_lote2_guardado"] = {"carpeta": rel(F5.REF / "L1-ELAST"), "productos_sha256": org}
    return {"productos": r, "cumple": not mot, "motivos": mot}


def comprobar() -> dict:
    """fam06-comprobar: SIN CÁLCULO CIENTÍFICO (sin filas de malla ni conciliación nueva; la revalidación de la referencia aplica el
    validador a bytes guardados, que reevalúa topologías como en la validación histórica)."""
    r = {"comando": "fam06-comprobar", "calculo": "ninguno"}
    malos = fuentes_alteradas()
    fu = fuentes()
    r["fuentes"] = {"archivos": len(fu["archivos"]), "reutilizados_de_fam05": len(fu["reutilizados_de_fam05"]),
                    "nucleo_c0_reutilizado": sum(1 for x in piezas() if x["archivo"].startswith("nucleo_s6/c0/")), "ausentes_o_distintos": malos[:20]}
    raw, man = manifiesto()
    an, al = anexo(), leer(DATOS / ALCANCE[0])
    cod = {n: sha_archivo(F5.LOTE / n) for n in F5.CODIGO}
    d7 = F1().parametros()
    d7dir = F5.RAIZ / d7["d7_dir"] / "versions" / d7["d7_tree"]
    r["procedencia"] = {
        "codigo_igual_al_de_fam05": cod == F5.CODIGO,
        "codigo_igual_al_alcance": {k: cod[k] for k in ("tarea_lote.py", "conexion_lambda.py", "conexion_frontera.py")} == al["entradas"]["codigo_lote"],
        "validador_igual_al_alcance": cod["validar_lote.py"] == al["entradas"]["validador_lote"],
        "manifiesto_igual_al_alcance": sha(raw) == al["lote_manifiesto_sha256"] == al["entradas"]["lote_manifiesto"],
        "manifiesto_igual_al_catalogo": sha(raw) == catalogo_dato("F06-MALLAS", "manifiesto E4 (entradas.lote_manifiesto)"),
        "alcance_igual_al_catalogo": sha_archivo(DATOS / ALCANCE[0]) == ALCANCE[1] == catalogo_dato("F06-MALLAS", "alcance nativo B"),
        "resultado_de_referencia_igual_al_catalogo": sha_archivo(REF / "L1-ELAST/resultado.json")
        == catalogo_dato("F06-MALLAS", "resultado L1-ELAST (codigo_sha256 y manifiesto_sha256)"),
        "anexo_igual_al_alcance": ANEXO[1] == al["entradas"]["cobertura_nacional"],
        "identidad_c0_igual_al_alcance": al["instalacion_identidad"] == F5.C0_IDENTIDAD,
        "d7_igual_al_alcance_y_al_manifiesto": {n: sha_archivo(d7dir / n) for n in al["entradas"]["d7_sha256"]} == al["entradas"]["d7_sha256"] == man["d7_sha256"],
        "despliegue_del_alcance": al.get("despliegue_sha256") == F5.DESPLIEGUE_SHA256,
        "alcance_no_oficial": all(al.get(k) is False for k in ("b_official_run_authorized", "freeze_run_authorized", "official_export_authorized")),
        "alcance_solo_l1_elast": al.get("tareas") == [TAREA],
        "anexo_ligado_al_manifiesto": an.get("kind") == "cobertura-nacional-lote1" and an.get("manifiesto_sha256") == sha(raw),
        "anexo_sin_conjuntos_ni_evaluaciones": an.get("conjuntos") == {} == man.get("L1-LAMBDA") and all(
            an.get(k) == {"macro.bridge": 0, "macro.strict_vertices": 0} for k in ("llamadas_durante_preparacion", "llamadas_durante_la_derivacion")),
        "anexo_de_esta_conexion_lambda": an.get("conexion_lambda_sha256") == F5.CODIGO["conexion_lambda.py"],
        "manifiesto_lote2_ligado": man["fuentes"]["manifiesto_lote2_rem114_sha256"] == F5.MANIFIESTO[1] == sha_archivo(F5.DATOS / F5.MANIFIESTO[0]),
        "conciliador_igual_al_extraido": sha_archivo(CONC) == CONC_SHA,
        "sustituciones_del_conciliador_unicas": _sustituciones_ok()}
    F5.preparar()
    import paper2b
    r["nucleo"] = {"identidad_recalculada": F5.identidad_c0(), "igual_a_la_del_alcance": F5.identidad_c0() == F5.C0_IDENTIDAD,
                   "paper2b_cargado_de": rel(Path(paper2b.__file__).parent), "declarado_en": "fuentes_fam05.json (nucleo_c0, mismo núcleo que FAM05)"}
    r["cobertura"] = cobertura_manifiesto(man)
    r["referencias"] = cobertura_referencias(man)
    lb = fu.get("libro_rem122") or {}
    ce, rp = r["cobertura"], r["referencias"]["productos"]
    rc_ = rp["conciliacion"]
    pares = []
    if lb.get("presente") is True:
        e = lb["E4"]
        pares = [("E4.rows ↔ filas de frontier_result", e["rows"], rp[PRODUCTO]["filas"]),
                 ("E4.grids ↔ mallas del manifiesto", e["grids"], ce["mallas"]),
                 ("E4.pairs ↔ pares del manifiesto", e["pairs"], ce["pares"]["total"]),
                 ("E4.pairs ↔ pares de la conciliación", e["pairs"], rc_["pares"]),
                 ("E4.paired_points ↔ puntos emparejados del manifiesto", e["paired_points"], ce["pares"]["puntos_emparejados"]),
                 ("E4.paired_points ↔ puntos de la conciliación", e["paired_points"], rc_["puntos_emparejados"]),
                 ("E4.duplicate_pairs ↔ pares repetidos de la conciliación", e["duplicate_pairs"], rc_["pares"] - rc_["pares_unicos"]),
                 ("E4.duplicate_rows ↔ filas repetidas de frontier_result", e["duplicate_rows"], rp[PRODUCTO]["filas_duplicadas"]),
                 ("E4.pending_pairs ↔ pendientes de la conciliación", e["pending_pairs"], rc_["pendientes"]),
                 ("E4.different_topology_pairs ↔ conciliación", e["different_topology_pairs"], rc_["diferencias_de_topologia"]["pares"]),
                 ("E4.different_topology_points ↔ conciliación", e["different_topology_points"], rc_["diferencias_de_topologia"]["puntos"]),
                 ("E4.by_instrument ↔ pares del manifiesto", e["by_instrument"], ce["pares"]["por_instrumento"]),
                 ("E4.by_instrument ↔ conciliación", e["by_instrument"], rc_["por_instrumento"]),
                 ("E4.parent_universe ↔ universo derivado de los manifiestos", e["parent_universe"], ce["universo_padre"]["total"]),
                 ("E4.parent_universe ↔ conciliación", e["parent_universe"], rc_["universo_padre"]),
                 ("E4.kink_rows ↔ filas con kink de frontier_result", e["kink_rows"], rp[PRODUCTO]["kinks"])]
    r["libro_rem122"] = {"presente": lb.get("presente"), "solo_extraccion": True,
                         "recuentos": [{"recuento": a, "libro": b, "archivos": c, "igual": b == c} for a, b, c in pares],
                         "recuentos_iguales": bool(pares) and all(b == c for _, b, c in pares),
                         "productos_iguales": lb.get("presente") is True and {n: p["sha256"] for n, p in lb["productos"].items()} == {PRODUCTO: rp[PRODUCTO]["sha256"]},
                         "alcance_de_la_decision": lb.get("alcance_de_la_decision_sha256") == ALCANCE[1],
                         "dictamen_consultado_es_el_del_libro": (lb.get("dictamen") or {}).get("sha256_del_archivo") == (lb.get("dictamen") or {}).get("sha256_en_el_libro") is not None}
    rc, ver, _ = ejecutar_validador(REF / "L1-ELAST/resultado.json", REF / "L1-ELAST/salida", None)
    hist = json.loads((REF / "L1-ELAST/validacion_stdout.txt").read_text(encoding="utf-8"))
    r["revalidacion_de_la_referencia"] = {"rc": rc, "dictamen": ver.get("dictamen"), "n_fallos": ver.get("n_fallos"), "igual_a_la_validacion_historica": ver == hist}
    pil = leer(DATOS / "pilotos.json") if (DATOS / "pilotos.json").is_file() else None
    r["pilotos"] = {"fijados": [(p["instrumento"], p["unidad"]) for p in (pil or {}).get("pilotos", [])], "iguales_a_la_regla": pil == regla_pilotos(man)}
    r["receta"] = {"pasos": len(receta()["pasos"])}
    r["cumple"] = (not malos and all(r["procedencia"].values()) and r["nucleo"]["igual_a_la_del_alcance"] and r["cobertura"]["cumple"]
                   and r["referencias"]["cumple"] and all(v is True for k, v in r["libro_rem122"].items() if k != "recuentos")
                   and rc == 0 and r["revalidacion_de_la_referencia"]["igual_a_la_validacion_historica"] and r["pilotos"]["iguales_a_la_regla"])
    return r


# ================================================================================================ cálculo (F06-MALLAS)
def declarados() -> set:
    out = set(F5.declarados())
    if (BASE / "fuentes_fam06.json").is_file():
        out |= {x["archivo"] for x in piezas()}
    return out


def lecturas(informe: dict) -> dict:
    dec = declarados()
    propios = ("src/", "reproducir.py", "datos/fam01/", "datos/fam06/", "fuentes_fam0", "catalogo.json")
    sin = [x for x in informe["en_el_paquete"] if x not in dec and not x.startswith(".venv-fam01/") and not x.startswith(propios)]
    return {"archivo": "archivos_leidos.json", "en_el_paquete": len(informe["en_el_paquete"]),
            "del_entorno_venv": sum(1 for x in informe["en_el_paquete"] if x.startswith(".venv-fam01/")),
            "aperturas_del_interprete": informe["aperturas_del_interprete"], "fuera_del_paquete_y_del_interprete": informe["fuera_del_paquete_y_del_interprete"],
            "sin_manifiesto": sin, "nucleo_c0_leidos": sum(1 for x in informe["en_el_paquete"] if x.startswith("nucleo_s6/c0/")),
            "src_de_otra_raiz_leidos": sum(1 for x in informe["en_el_paquete"] if x.startswith(("nucleo_s6/instalacion/src/", "nucleo_s6/raiz/src/"))),
            "datos_de_fam05_leidos": [x for x in informe["en_el_paquete"] if x.startswith("datos/fam05/")],
            "referencias_leidas": [x for x in informe["en_el_paquete"] if x.startswith("referencias/") and not x.startswith("referencias/fam01/")]}


def entorno() -> dict:
    e = F5._entorno(None)
    e["f2_alcance"] = "adoptada solo para FAM01; aquí se informa y no es requisito de FAM06"
    return e


def correr(salida: Path, unidad: str | None = None, tope: float = F5.TOPE_TRABAJO) -> dict:
    """fam06-unidad: E4 (o la malla seleccionada) por la ruta de producción de tarea_lote (TAREA-AST-v2, MANIFIESTO-E4-v1), en la carpeta
    NUEVA `salida`: salida/frontier_result.jsonl, resultado.json (esquema de tarea_lote), ejecucion.json y archivos_leidos.json."""
    T0, c0 = time.time(), time.process_time()
    rastro = F1().Rastro()                       # desde el principio: también las lecturas previas al cálculo
    raw, man = manifiesto()
    sel = seleccion(man, unidad)
    malos = fuentes_alteradas("calculo")
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam06.json; no se calcula): %s" % malos[:5])
    TOPE = float(tope) - F5.HOLGURA
    need(TOPE > 0, "TOPE_INVALIDO")
    mods = F5.pila()
    need(F5.identidad_c0() == F5.C0_IDENTIDAD, "NUCLEO_C0_DE_OTRA_IDENTIDAD (no se calcula)")
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    sal = salida.resolve()
    out = {"tarea": TAREA, "modo": "produccion", "manifiesto_sha256": sha(raw), "tope_efectivo_s": TOPE, "sintetico": False,
           "codigo_sha256": {n: sha((F5.LOTE / n).read_bytes()) for n in ("tarea_lote.py", "conexion_lambda.py", "conexion_frontera.py")}, "productos": []}
    ns, cod = F5.espacio(mods, sal / "salida", out, man, T0, TOPE)
    ns["R"] = DATOS                               # MANIFIESTO-E4-v1 (E4 no declara rutas relativas)
    ns["fr_"] = {k: v for k, v in man["L1-ELAST"]["fronteras"].items() if sel is None or v["frontier_id"] in sel["fronteras"]}
    ruta, campos = list(sys.path), {}
    a0 = time.time()
    try:
        exec(cod[TAREA], ns)
        raise Fam06Error("RAMA_SIN_CIERRE")       # la rama de producción siempre termina en fin(...)
    except F5.FinTarea as f:
        estado, motivo, campos = f.estado, f.motivo, f.campos
    finally:
        sys.path[:] = ruta
    t_calc = round(time.time() - a0, 2)
    out.update(estado=estado, motivo=motivo, pared_s=round(time.time() - T0, 2), **campos)
    (sal / "resultado.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    informe = rastro.informe()
    (sal / "archivos_leidos.json").write_bytes((json.dumps(informe, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    ej = {"tarea": TAREA, "unidad": unidad, "operacion": "F06-MALLAS", "seleccion": sel, "manifiesto_sha256": sha(raw), "etiqueta": ETIQUETA,
          "naturaleza": "cálculo: ruta de producción de tarea_lote.py (bytes exactos) con el manifiesto E4 en la base limpia; sin puerta de producción (PUERTA-v1)",
          "alcance": "una malla E4 completa (piloto); no es un supremo certificado sobre todo el soporte" if sel else "las 383 mallas E4",
          "adaptaciones": list(ADAPTACIONES), "reloj": "RELOJ-PILOTO-v1: tope interno %.0f s (= %.0f − %.0f); el límite externo lo pone el supervisor"
          % (TOPE, float(tope), F5.HOLGURA), "resultado": {"estado": estado, "motivo": motivo, "productos": out["productos"]},
          "nucleo": {"identidad": F5.identidad_c0(), "paper2b": rel(Path(mods["M"].__file__).parent),
                     "paper2b_importado_de": sorted({rel(Path(m.__file__).parent) for k, m in list(sys.modules.items())
                                                     if (k == "paper2b" or k.startswith("paper2b.")) and getattr(m, "__file__", None)})},
          "tiempos_s": {"calculo": t_calc, "total": round(time.time() - T0, 2), "cpu": round(time.process_time() - c0, 2)},
          "entorno": entorno(), "lecturas": lecturas(informe), "dependencias_fuera_de_la_biblioteca_estandar": F1().dependencias_cargadas()}
    ej["exito"] = estado == "completa"
    (sal / "ejecucion.json").write_bytes(json.dumps(ej, ensure_ascii=False, indent=1, sort_keys=True, default=str).encode("utf-8") + b"\n")
    return ej


# ================================================================================================ validación
def ejecutar_validador(res: Path, sal: Path, sel, cob: Path | None = None, man_p: Path | None = None) -> tuple:
    """validar_lote.py del lote 2 (VALIDADOR-v2 de FAM05, mismas sustituciones) como guion, con el manifiesto y el anexo E4 (argv como en
    la receta: raíz, manifiesto, resultado, salida, anexo [, selección]); raíz = datos/fam06 (MANIFIESTO-E4-v1)."""
    F5.preparar()
    txt = F5.validador_adaptado()
    cob = DATOS / ANEXO[0] if cob is None else cob
    man_p = DATOS / MANIFIESTO[0] if man_p is None else man_p
    if "conexion_lambda" in sys.modules:
        need(Path(sys.modules["conexion_lambda"].__file__).resolve() == (F5.LOTE / "conexion_lambda.py").resolve(), "CONEXION_LAMBDA_DE_OTRO_LOTE")
    v = F5.LOTE / "validar_lote.py"
    argv = [str(v), str(DATOS), str(man_p), str(res), str(sal), str(cob)] + ([json.dumps(sel)] if sel is not None else [])
    viejo, ruta, buf, rc = sys.argv, list(sys.path), io.StringIO(), None
    sys.argv = argv
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(txt, str(v), "exec"), {"__name__": "__main__", "__file__": str(v), "__builtins__": builtins})
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
    """fam06-validar: SIN CÁLCULO. validar_lote.py (VALIDADOR-v2) sobre los bytes guardados de `nueva` (carpeta de fam06-unidad), con la
    selección registrada en su ejecución, el manifiesto E4 y su anexo."""
    t0 = time.time()
    nueva = Path(nueva).resolve()
    ej = leer(nueva / "ejecucion.json")
    rb = (nueva / "resultado.json").read_bytes()
    rc, ver, _ = ejecutar_validador(nueva / "resultado.json", nueva / "salida", ej.get("seleccion"), cob)
    return {"comando": "fam06-validar", "naturaleza": "validación sin cálculo de bytes guardados", "tarea": ej["tarea"], "unidad": ej.get("unidad"),
            "operacion": ej.get("operacion"), "seleccion": ej.get("seleccion"), "origen": rel(nueva), "resultado_sha256": sha(rb),
            "productos_sha256": productos_de(nueva, json.loads(rb)),
            "validador": {"archivo": "nucleo_s6/lote2/validar_lote.py", "sha256": F5.CODIGO["validar_lote.py"], "adaptacion": [x[0] for x in F5.SUSTITUCIONES_VALIDADOR],
                          "adaptado_sha256": sha(F5.validador_adaptado().encode("utf-8")), "nucleo": "nucleo_s6/c0 (NUCLEO-C0-v1)",
                          "manifiesto": "datos/fam06/" + MANIFIESTO[0], "raiz_de_rutas_del_manifiesto": rel(DATOS)},
            "anexo": rel(cob) if cob is not None else "datos/fam06/" + ANEXO[0], "rc": rc, "veredicto": ver,
            "aceptada": rc == 0 and ver.get("aceptada") is True and ver.get("dictamen") == "completa_validada", "segundos": round(time.time() - t0, 3)}


# ================================================================================================ comparación de mallas
# COMPARACION-FAM06-MALLAS-v1 (= COMPARACION-FAM05-v1 en lo aplicable): mismo perfil de entorno .venv-fam01 y MISMO núcleo C0 que la
# referencia rem121. CR-HASH-CANONICO (cada fila de frontier_result de las mallas de la unidad idéntica campo a campo con su serialización
# JSON, incluida «topology») y CR-DISCRETOS (estados, clasificaciones, NA, claves y conteos exactos, con precedencia). Las tolerancias
# internas del validador (T1) no se usan aquí. En resultado.json: tarea, modo, sintetico, estado, motivo y tope_efectivo_s se comparan;
# manifiesto, código y núcleo son identidades; pared_s es operativo (se muestra).
def comparar_mallas(nueva: Path, validacion: Path) -> dict:
    nueva = Path(nueva).resolve()
    raw, man = manifiesto()
    mot = []
    ej = leer(nueva / "ejecucion.json")
    rb = (nueva / "resultado.json").read_bytes()
    res = json.loads(rb)
    sel = ej.get("seleccion")
    if ej.get("tarea") != TAREA or res.get("tarea") != TAREA or ej.get("operacion") != "F06-MALLAS":
        mot.append("SALIDA_DE_OTRA_TAREA: %s / %s" % (res.get("tarea"), ej.get("operacion")))
    if sel != seleccion(man, ej.get("unidad")):
        mot.append("SELECCION_INCOHERENTE")
    val = leer(validacion) if Path(validacion).is_file() else None
    if val is None:
        mot.append("VALIDACION_AUSENTE")
    else:
        if (val.get("comando") != "fam06-validar" or val.get("origen") != rel(nueva) or val.get("resultado_sha256") != sha(rb)
                or val.get("productos_sha256") != productos_de(nueva, res) or val.get("tarea") != TAREA):
            mot.append("VALIDACION_DE_OTROS_BYTES")
        if val.get("aceptada") is not True:
            mot.append("VALIDACION_NO_ACEPTADA: %s" % ((val.get("veredicto") or {}).get("fallos") or [])[:3])
    if res.get("estado") != "completa":
        mot.append("CALCULO_NO_COMPLETO: %s" % res.get("motivo"))
    ref_res = leer(REF / "L1-ELAST/resultado.json")
    decl = {p["archivo"]: p for p in res.get("productos") or []}
    if sorted(decl) != [PRODUCTO]:
        mot.append("PRODUCTOS_DISTINTOS: %s" % sorted(decl))
    objetos = {}
    fref = REF / "L1-ELAST/salida" / PRODUCTO
    fn = nueva / "salida" / PRODUCTO
    d = decl.get(PRODUCTO)
    if sha_archivo(fref) is None or sha_archivo(fref) != F5.catalogo_sha(*REF_CATALOGO[PRODUCTO]):
        mot.append("REFERENCIA_ALTERADA_O_AJENA: %s" % PRODUCTO)
    elif d is None or sha_archivo(fn) != d.get("sha256"):
        mot.append("PRODUCTO_AUSENTE_O_ALTERADO: %s" % PRODUCTO)
    else:
        ref_l = [x for x in fref.read_text(encoding="utf-8").splitlines() if x.strip() and F5.en_unidad(PRODUCTO, json.loads(x), sel)]
        nue_l = [x for x in fn.read_text(encoding="utf-8").splitlines() if x.strip()]
        o = F5.comparar_producto(PRODUCTO, nue_l, ref_l, None)
        c = o["cobertura"]
        if c["faltan"] or c["ajenas"] or c["duplicadas"] or not c["mismo_orden"] or c["filas_nuevas"] != c["filas_referencia"] or not ref_l:
            mot.append("COBERTURA_DISTINTA (CR-DISCRETOS): %s" % PRODUCTO)
        if o["n_discretas"]:
            mot.append("DIFERENCIA_DISCRETA (CR-DISCRETOS, precedencia): %s %s" % (PRODUCTO, [x["puntero"] for x in o["discretas"][:4]]))
        if o["n_numericas"]:
            mot.append("DIFERENCIA_NUMERICA (CR-HASH-CANONICO): %s %s" % (PRODUCTO, [x["puntero"] for x in o["numericas"][:4]]))
        o["filas_decl"] = d.get("filas")
        objetos[PRODUCTO] = o
    rr = {}
    for k in ("tarea", "modo", "sintetico", "estado", "motivo", "tope_efectivo_s"):
        rr[k] = {"nueva": res.get(k), "referencia": ref_res.get(k), "igual": res.get(k) == ref_res.get(k)}
        if not rr[k]["igual"]:
            mot.append("RESULTADO_DISTINTO: %s" % k)
    ident = {"manifiesto_sha256": res.get("manifiesto_sha256") == ref_res.get("manifiesto_sha256") == MANIFIESTO[1],
             "codigo_sha256": res.get("codigo_sha256") == ref_res.get("codigo_sha256"), "nucleo_c0": ej.get("nucleo", {}).get("identidad") == F5.C0_IDENTIDAD}
    if not all(ident.values()):
        mot.append("IDENTIDAD_DE_MANIFIESTO_CODIGO_O_NUCLEO_DISTINTA: %s" % [k for k, v in ident.items() if not v])
    deriv = {}
    if sel is None:
        deriv["productos"] = {"iguales_a_la_referencia": res.get("productos") == ref_res.get("productos")}
        if not deriv["productos"]["iguales_a_la_referencia"]:
            mot.append("PRODUCTOS_DISTINTOS_DE_LA_TAREA_DE_REFERENCIA")
    return {"comando": "fam06-comparar", "tarea": TAREA, "unidad": ej.get("unidad"), "operacion": "F06-MALLAS", "seleccion": sel,
            "regla": "COMPARACION-FAM06-MALLAS-v1 (src/fam06.py)", "criterios": ["CR-HASH-CANONICO (mismo perfil de entorno y mismo núcleo C0; exacta)", "CR-DISCRETOS (precedencia)"],
            "no_aplicado": "CR-OBJETO-OTRO-ENTORNO (T1, T2_G): no es otro entorno",
            "referencia": {"ejecucion": "referencias/fam06/rem121/L1-ELAST", "productos": {PRODUCTO: F5.catalogo_sha(*REF_CATALOGO[PRODUCTO])},
                           "alcance": "misma malla (selección)" if sel else "las 383 mallas"},
            "nueva": rel(nueva), "validacion": rel(Path(validacion)), "objetos": objetos, "resultado": rr, "identidades": ident, "derivados": deriv,
            "operativos": {"resultado.json/pared_s": {"nueva": res.get("pared_s"), "referencia_tarea": ref_res.get("pared_s")}},
            "estado": {"reproduccion": "aceptada" if not mot else "no_aceptada", "motivos": mot}}


# ================================================================================================ conciliación (F06-CONCILIACION)
def conciliador_adaptado() -> str:
    need(CONC.is_file(), "CONCILIADOR_AUSENTE")
    src = CONC.read_bytes()
    need(sha(src) == CONC_SHA, "CONCILIADOR_DISTINTO")
    txt = src.decode("utf-8")
    for i, a, b in SUSTITUCIONES_CONCILIADOR:
        need(txt.count(a) == 1, "SUSTITUCION_NO_UNICA: %s" % i)
        txt = txt.replace(a, b)
    return txt


def _sustituciones_ok() -> bool:
    try:
        conciliador_adaptado()
        return True
    except Fam06Error:
        return False


def lado(nombre: str, arg, val) -> dict:
    """Un lado de la conciliación. «guardado»: el producto aceptado del paquete (E4: referencias/fam06/rem121; lote 2: el de FAM05), con la
    huella del catálogo, REUTILIZADO. Una carpeta: salida nueva de fam06-unidad (E4) o de fam05-unidad L1-ELAST completa (lote 2) con su
    validación aceptada de ESOS bytes, RECALCULADA."""
    e4 = nombre == "E4"
    prods = (PRODUCTO,) if e4 else tuple(ORIGEN_CATALOGO)
    need(arg is not None, "LADO_%s_SIN_DECLARAR (carpeta nueva o «%s»)" % (nombre.upper(), GUARDADO))
    if str(arg) == GUARDADO:
        d = (REF if e4 else F5.REF) / "L1-ELAST"
        cat = REF_CATALOGO if e4 else ORIGEN_CATALOGO
        act = {n: sha_archivo(d / "salida" / n) for n in prods}
        need(act == {n: F5.catalogo_sha(*cat[n]) for n in prods}, "%s_GUARDADO_ALTERADO_O_AJENO: %s" % (nombre.upper(), act))
        res = leer(d / "resultado.json")
        need({p["archivo"]: p["sha256"] for p in res["productos"] if p["archivo"] in prods} == act, "%s_GUARDADO_CON_OTRA_DECLARACION" % nombre.upper())
        return {"lado": nombre, "dir": d, "carpeta": rel(d), "origen": "reutilizado", "seleccion": None, "validacion": None, "productos_sha256": act,
                "naturaleza": "producto aceptado guardado (catálogo %s); no se recalcula" % ", ".join(cat[n][1] for n in prods)}
    d = Path(arg).resolve()
    need(val is not None and Path(val).is_file(), "VALIDACION_AUSENTE (%s)" % nombre)
    v = leer(val)
    ej = leer(d / "ejecucion.json")
    if not e4:
        need(ej.get("seleccion") is None, "LOTE2_PARCIAL: el lado de origen nuevo debe ser la tarea L1-ELAST completa de FAM05 (o «%s»)" % GUARDADO)
    rb = (d / "resultado.json").read_bytes()
    res = json.loads(rb)
    act = productos_de(d, res)
    need(v.get("origen") == rel(d) and v.get("resultado_sha256") == sha(rb) and v.get("productos_sha256") == act, "VALIDACION_DE_OTROS_BYTES (%s)" % nombre)
    need(v.get("aceptada") is True, "VALIDACION_NO_ACEPTADA (%s)" % nombre)
    need(all(act.get(p["archivo"]) == p["sha256"] for p in res["productos"]) and set(act) == set(prods), "PRODUCTOS_AUSENTES_O_ALTERADOS (%s)" % nombre)
    need(res.get("tarea") == TAREA and res.get("estado") == "completa", "SALIDA_NO_COMPLETA (%s)" % nombre)
    if e4:
        need(v.get("comando") == "fam06-validar" and res.get("manifiesto_sha256") == MANIFIESTO[1], "SALIDA_E4_DE_OTRO_MANIFIESTO")
    else:
        need(v.get("comando") == "fam05-validar" and res.get("manifiesto_sha256") == F5.MANIFIESTO[1], "SALIDA_LOTE2_DE_OTRO_MANIFIESTO")
    return {"lado": nombre, "dir": d, "carpeta": rel(d), "origen": "recalculado", "seleccion": ej.get("seleccion"), "validacion": rel(Path(val)),
            "productos_sha256": act, "naturaleza": "salida nueva validada (%s de %s)" % (v.get("comando"), rel(d))}


def ejecutar_conciliador(ent: dict, prod: Path) -> tuple:
    txt = conciliador_adaptado()
    viejo, buf, rc, err = sys.argv, io.StringIO(), 0, None
    sys.argv = [str(CONC), json.dumps(ent, ensure_ascii=False), str(prod)]
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(txt, str(CONC), "exec"), {"__name__": "__main__", "__file__": str(CONC), "__builtins__": builtins})
    except AssertionError as ex:
        ln = traceback.extract_tb(ex.__traceback__)[-1].lineno
        rc, err = 1, "ASERCION_DEL_CONCILIADOR (línea adaptada %d): %s" % (ln, txt.splitlines()[ln - 1].strip())
    except (KeyError, TypeError, ValueError, OSError) as ex:
        rc, err = 1, "%s: %s" % (type(ex).__name__, ex)
    finally:
        sys.argv = viejo
    return rc, buf.getvalue(), err


def conciliar(salida: Path, e4, lote2, val_e4=None, val_lote2=None) -> dict:
    """fam06-conciliar: conciliación G/N con el productor histórico (CONCILIADOR-v1) sobre los dos lados DECLARADOS (E4 y lote 2: carpeta
    nueva validada o «guardado»). Si E4 es una malla (piloto), solo su par. Escribe en la carpeta NUEVA `salida` CONCILIACION_E4.json
    (esquema histórico) y ejecucion.json (lados, entradas, naturaleza, lecturas). No lee la conciliación esperada."""
    T0 = time.time()
    rastro = F1().Rastro()
    need(sys.flags.optimize == 0, "ASERCIONES_DESACTIVADAS (-O): el conciliador comprueba con assert")
    malos = fuentes_alteradas("conciliacion")
    need(not malos, "DEPENDENCIA_AUSENTE_O_ALTERADA (fuentes_fam06.json; no se concilia): %s" % malos[:5])
    raw4, man4 = manifiesto()
    m2p = F5.DATOS / F5.MANIFIESTO[0]
    raw2 = m2p.read_bytes()
    need(sha(raw2) == man4["fuentes"]["manifiesto_lote2_rem114_sha256"] == F5.MANIFIESTO[1], "MANIFIESTO_LOTE2_DISTINTO")
    l4, l2 = lado("E4", e4, val_e4), lado("lote2", lote2, val_lote2)
    sel = l4["seleccion"]
    pares = None if sel is None else ["E4:" + f for f in sel["fronteras"]]
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=False)
    prod = salida.resolve() / PRODUCTO_CONC
    ent = {"manifiesto_lote2": str(m2p), "manifiesto_e4": str(DATOS / MANIFIESTO[0]), "lote2": str(l2["dir"]), "e4": str(l4["dir"]), "pares": pares}
    a0 = time.time()
    rc, stdout, err = ejecutar_conciliador(ent, prod)
    t_conc = round(time.time() - a0, 3)
    if l4["origen"] == l2["origen"] == "reutilizado":
        nat = REGENERACION + ": los 391 pares desde los productos aceptados guardados; ninguna malla se recalcula"
        acredita = "F06-CONCILIACION como regeneración documental; NO acredita la ejecución de F06-MALLAS"
    elif l4["origen"] == l2["origen"] == "recalculado":
        nat = "conciliación de salidas nuevas validadas de FAM06 (E4) y FAM05 (lote 2)"
        acredita = "F06-CONCILIACION sobre mallas recalculadas" + (" (selección)" if pares else "")
    else:
        nueva = "E4" if l4["origen"] == "recalculado" else "lote 2"
        nat = "conciliación mixta: lado %s recalculado (salida nueva validada); el otro lado reutiliza el producto aceptado guardado" % nueva
        acredita = ("piloto: el par de la malla E4 recalculada con su malla de origen autenticada (reutilizada); no es la conciliación completa"
                    if pares else "conciliación mixta: no sustituye la conciliación de las salidas nuevas de ambos lados")
    informe = rastro.informe()
    leidas = informe["en_el_paquete"]
    resumen = None
    with contextlib.suppress(ValueError):
        resumen = json.loads(stdout) if stdout.strip() else None
    ej = {"comando": "fam06-conciliar", "operacion": "F06-CONCILIACION", "etiqueta": ETIQUETA, "naturaleza": nat, "acredita": acredita,
          "lados": {n: {k: x[k] for k in ("carpeta", "origen", "naturaleza", "seleccion", "validacion", "productos_sha256")} for n, x in (("E4", l4), ("lote2", l2))},
          "pares_seleccionados": pares,
          "entradas": {"manifiesto_e4": {"archivo": rel(DATOS / MANIFIESTO[0]), "sha256": sha(raw4)}, "manifiesto_lote2": {"archivo": rel(m2p), "sha256": sha(raw2)}},
          "conciliador": {"archivo": rel(CONC), "sha256": CONC_SHA, "adaptacion": "CONCILIADOR-v1: " + ", ".join(x[0] for x in SUSTITUCIONES_CONCILIADOR),
                          "adaptado_sha256": sha(conciliador_adaptado().encode("utf-8"))},
          "resultado": {"rc": rc, "error": err, "producto": PRODUCTO_CONC, "producto_sha256": sha_archivo(prod), "resumen": resumen},
          "lecturas": {"en_el_paquete": len(leidas), "fuera_del_paquete_y_del_interprete": informe["fuera_del_paquete_y_del_interprete"],
                       "referencias_leidas": [x for x in leidas if x.startswith("referencias/")],
                       "conciliacion_esperada_leida": any(x.startswith("referencias/fam06/rem121/conciliacion/") for x in leidas),
                       "nota": "las carpetas nuevas de salidas/ no se listan (Rastro); sus huellas están en «lados»"},
          "tiempos_s": {"conciliacion": t_conc, "total": round(time.time() - T0, 3)}}
    ej["exito"] = rc == 0 and ej["resultado"]["producto_sha256"] is not None and not ej["lecturas"]["conciliacion_esperada_leida"]
    (salida / "archivos_leidos.json").write_bytes((json.dumps(informe, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    (salida / "ejecucion.json").write_bytes(json.dumps(ej, ensure_ascii=False, indent=1, sort_keys=True, default=str).encode("utf-8") + b"\n")
    return ej


# ================================================================================================ comparación de la conciliación
# COMPARACION-FAM06-CONCILIACION-v1: CR-DISCRETOS exacto (todo el objeto es discreto: claves, vínculos, recuentos, estados) frente a la
# conciliación aceptada (P_conc_e4), restringida a los pares de la nueva si es una selección. Detalle por par (clave «par», sin faltantes,
# ajenos ni repetidos y en el mismo orden): cada hoja idéntica. Totales: si no hay selección, cada campo idéntico al de la referencia; en
# todo caso, cada total de la nueva debe derivarse de SU detalle con las fórmulas del productor. VINCULOS: producto_e4_sha256 y
# producto_elast_aceptado_sha256 son vínculos, no valores: en la nueva deben ser las huellas de los bytes de SUS lados (recomprobadas sobre
# esos bytes) y en la referencia las del catálogo; se muestran ambas. No hay campos operativos en el producto (la duración está en
# ejecucion.json). Control positivo: las diferencias de topología G/N (17 pares, 36 puntos en la referencia completa) se conservan.
VINCULOS_CONC = {"producto_e4_sha256": ("E4", PRODUCTO, REF_CATALOGO[PRODUCTO]),
                 "producto_elast_aceptado_sha256": ("lote2", "frontier_result.jsonl", ORIGEN_CATALOGO["frontier_result.jsonl"])}


def agregados(d: list) -> dict:
    """Totales del productor (mismas fórmulas que conciliacion_e4_rem121.py) a partir de un detalle."""
    pend = [p for p in d if not p["conciliado"]]
    return {"pares": len(d), "contrapartes_e4": sum(1 for p in d if p["par"].startswith("E4:")), "existentes": sum(1 for p in d if p["par"].startswith("existente")),
            "conciliados": len(d) - len(pend), "pendientes": [{k: p[k] for k in ("par", "G", "N", "vinculo", "mismos_puntos")} for p in pend],
            "puntos_contraparte_total": sum(p["puntos"] for p in d if p["par"].startswith("E4:")),
            "origenes": dict(Counter(p["origen"] for p in d)), "por_instrumento": dict(Counter(p["instrumento"] for p in d)),
            "topologia_igual_en_todos_los_puntos": sum(1 for p in d if p.get("topologia_igual_en_puntos") == p["puntos"]),
            "pares_con_kink": {"G": sum(1 for p in d if (p.get("puntos_con_kink") or {}).get("G")), "N": sum(1 for p in d if (p.get("puntos_con_kink") or {}).get("N"))}}


def comparar_conciliacion(nueva: Path) -> dict:
    nueva = Path(nueva).resolve()
    mot = []
    ej = leer(nueva / "ejecucion.json")
    pn = nueva / PRODUCTO_CONC
    if ej.get("comando") != "fam06-conciliar" or not pn.is_file() or sha_archivo(pn) != ej["resultado"].get("producto_sha256"):
        mot.append("CONCILIACION_AUSENTE_O_ALTERADA")
        cn = {}
    else:
        cn = leer(pn)
    if ej.get("exito") is not True:
        mot.append("CONCILIACION_NO_TERMINADA: %s" % ej.get("resultado", {}).get("error"))
    craw = REF_CONC.read_bytes() if REF_CONC.is_file() else b""
    if sha(craw) != F5.catalogo_sha(*REF_CATALOGO["CONCILIACION_E4_REM121.json"]):
        mot.append("REFERENCIA_ALTERADA_O_AJENA: CONCILIACION_E4_REM121.json")
    cr = json.loads(craw) if craw else {"detalle": []}
    sel = ej.get("pares_seleccionados")
    dr = [p for p in cr["detalle"] if sel is None or p["par"] in sel]
    dn = cn.get("detalle") or []
    kn, kr = [p.get("par") for p in dn], [p["par"] for p in dr]
    cob = {"pares_nuevos": len(dn), "pares_referencia": len(dr), "faltan": [k for k in kr if k not in kn][:5], "ajenos": [k for k in kn if k not in kr][:5],
           "repetidos": (len(kn) - len(set(kn))) + (len(kr) - len(set(kr))), "mismo_orden": kn == kr}
    if cob["faltan"] or cob["ajenos"] or cob["repetidos"] or not cob["mismo_orden"] or not dr:
        mot.append("COBERTURA_DE_PARES_DISTINTA (CR-DISCRETOS)")
    disc = []
    pn_ = dict(zip(kn, dn))
    for p in dr:
        q = pn_.get(p["par"])
        if q is None:
            continue
        hn, hr = F5.hojas(q), F5.hojas(p)
        for k in sorted(set(hn) | set(hr)):
            a, b = hn.get(k, "<ausente>"), hr.get(k, "<ausente>")
            if json.dumps(a) != json.dumps(b):
                disc.append({"par": p["par"], "puntero": k, "nueva": a, "referencia": b})
    if disc:
        mot.append("DIFERENCIA_DISCRETA_EN_EL_DETALLE: %s" % ["%s %s" % (x["par"], x["puntero"]) for x in disc[:4]])
    tot_n = {k: v for k, v in cn.items() if k != "detalle"}
    tot_r = {k: v for k, v in cr.items() if k != "detalle"}
    an = agregados(dn) if dn else {}
    deriv = {"totales_de_la_nueva_derivados_de_su_detalle": bool(an) and all(tot_n.get(k) == v for k, v in an.items()),
             "agregados_iguales_a_los_de_la_referencia_restringida": an == agregados(dr) if dn and dr else False}
    if not deriv["totales_de_la_nueva_derivados_de_su_detalle"]:
        mot.append("TOTALES_NO_DERIVADOS_DEL_DETALLE")
    totales = {}
    if sel is None:
        for k in sorted(set(tot_n) | set(tot_r)):
            if k in VINCULOS_CONC:
                continue
            totales[k] = {"nueva": tot_n.get(k), "referencia": tot_r.get(k), "igual": tot_n.get(k) == tot_r.get(k)}
            if not totales[k]["igual"]:
                mot.append("TOTAL_DISTINTO: %s" % k)
    else:
        totales["universo_padre_sin_cambio"] = {"nueva": tot_n.get("universo_padre_sin_cambio"), "referencia": tot_r.get("universo_padre_sin_cambio"),
                                                "igual": tot_n.get("universo_padre_sin_cambio") == tot_r.get("universo_padre_sin_cambio")}
        if not totales["universo_padre_sin_cambio"]["igual"]:
            mot.append("TOTAL_DISTINTO: universo_padre_sin_cambio")
    vin = {}
    for campo, (ld, n, cat) in VINCULOS_CONC.items():
        lado_ = (ej.get("lados") or {}).get(ld) or {}
        f = BASE / lado_.get("carpeta", "<ausente>") / "salida" / n if lado_.get("carpeta") else None
        propio = sha_archivo(f) if f is not None else None
        vin[campo] = {"nueva": tot_n.get(campo), "bytes_de_su_lado": propio, "registrado_en_la_ejecucion": (lado_.get("productos_sha256") or {}).get(n),
                      "referencia": tot_r.get(campo), "catalogo": F5.catalogo_sha(*cat), "lado": ld, "origen_del_lado": lado_.get("origen")}
        vin[campo]["nueva_ligada_a_sus_bytes"] = vin[campo]["nueva"] == propio == vin[campo]["registrado_en_la_ejecucion"] is not None
        vin[campo]["referencia_ligada_al_catalogo"] = vin[campo]["referencia"] == vin[campo]["catalogo"] is not None
        vin[campo]["igual_a_la_referencia"] = vin[campo]["nueva"] == vin[campo]["referencia"]
        if not (vin[campo]["nueva_ligada_a_sus_bytes"] and vin[campo]["referencia_ligada_al_catalogo"]):
            mot.append("VINCULO_ROTO: %s" % campo)
    topo = {"nueva": resumen_conciliacion(cn)["diferencias_de_topologia"] if dn else None,
            "referencia": resumen_conciliacion({"detalle": dr})["diferencias_de_topologia"],
            "nota": "control positivo: diferencias legítimas del contraste G/N; deben conservarse (no son errores)"}
    return {"comando": "fam06-comparar", "tarea": "CONCILIACION", "operacion": "F06-CONCILIACION", "naturaleza": ej.get("naturaleza"), "acredita": ej.get("acredita"),
            "lados": {k: {x: v.get(x) for x in ("origen", "carpeta")} for k, v in (ej.get("lados") or {}).items()},
            "regla": "COMPARACION-FAM06-CONCILIACION-v1 (src/fam06.py)", "criterios": ["CR-DISCRETOS (exacto; todo el objeto es discreto)", "VINCULOS por lado"],
            "referencia": {"archivo": rel(REF_CONC), "sha256": sha(craw), "catalogo": "P_conc_e4", "alcance": "pares seleccionados" if sel else "los 391 pares"},
            "nueva": rel(nueva), "bytes_identicos_a_la_referencia": sha_archivo(pn) == sha(craw),
            "cobertura": cob, "n_discretas": len(disc), "discretas": disc[:20], "totales": totales, "vinculos": vin, "derivados": deriv,
            "topologia_G_N": topo, "operativos": {"ejecucion.json/tiempos_s": ej.get("tiempos_s")},
            "estado": {"reproduccion": "aceptada" if not mot else "no_aceptada", "motivos": mot}}


# ================================================================================================ receta completa (sin ejecutarla)
def receta() -> dict:
    raw, man = manifiesto()
    el = man["L1-ELAST"]
    e4, l2 = "salidas/fam06/<ejecucion>/L1-ELAST", "salidas/fam05/<ejecucion>/L1-ELAST"
    c = "salidas/fam06/<ejecucion>/conciliacion"
    pasos = [{"paso": "F06-MALLAS", "ordenes": ["reproducir.py fam06-unidad --salida %s" % e4,
                                                "reproducir.py fam06-validar --nueva %s --salida %s.validacion.json" % (e4, e4),
                                                "reproducir.py fam06-comparar --tarea L1-ELAST --nueva %s --validacion %s.validacion.json --salida %s.comparacion.json" % (e4, e4, e4)]},
             {"paso": "lado de origen (F05-ELAST-C0 + F05-ELAST-HIST, receta de FAM05)",
              "ordenes": ["reproducir.py fam05-unidad --tarea L1-ELAST --salida %s" % l2,
                          "reproducir.py fam05-validar --nueva %s --salida %s.validacion.json" % (l2, l2),
                          "reproducir.py fam05-comparar --tarea L1-ELAST --nueva %s --validacion %s.validacion.json --salida %s.comparacion.json" % (l2, l2, l2)]},
             {"paso": "F06-CONCILIACION", "ordenes": ["reproducir.py fam06-conciliar --e4 %s --validacion-e4 %s.validacion.json --lote2 %s --validacion-lote2 "
                                                      "%s.validacion.json --salida %s" % (e4, e4, l2, l2, c),
                                                      "reproducir.py fam06-comparar --tarea CONCILIACION --nueva %s --salida %s.comparacion.json" % (c, c)]}]
    return {"comando": "fam06-receta", "estado": "receta completa preparada; NO ejecutada (el lote pertenece al Paso 3)", "manifiesto_sha256": sha(raw),
            "previo": ["reproducir.py fam06-comprobar --salida salidas/fam06/<nuevo>.json (sin cálculo científico)"], "pasos": pasos,
            "cobertura": {"F06-MALLAS": {"mallas": len(el["fronteras"]), "nodos": el["puntos_totales_frontier_n4"],
                                         "filas": "una «point» por nodo y left_limit/right_limit si y solo si hay kink, con su topología del núcleo C0"},
                          "F06-CONCILIACION": {"pares": el["pares_tras_la_opcion"], "contrapartes_e4": len(el["fronteras"]), "existentes": len(el["pares_existentes"])}},
            "ejecucion": {"procesos": "un cálculo a la vez, sin reintentos", "tope_trabajo_s": F5.TOPE_TRABAJO, "reloj_interno_s": F5.TOPE_TRABAJO - F5.HOLGURA,
                          "tope_validacion_s": F5.TOPE_VALIDACION,
                          "lanzador": "supervisor que termina el árbol de procesos (el mismo de los pilotos), con el tope de trabajo como límite externo",
                          "parada": "si un paso no queda completo, validado y aceptado, el siguiente no se lanza",
                          "lados": ("la conciliación de la receta usa las DOS salidas nuevas validadas; «guardado» (producto aceptado del paquete) solo "
                                    "sirve para la regeneración documental o los pilotos, y queda declarado en ejecucion.json (lados, naturaleza)"),
                          "duracion": "sin estimación: los pilotos no la permiten"},
            "F1": {"reutilizado": ["selección de E4 (LOTE2E4_MANIFIESTO.json; no se re-ejecuta)", "código del lote 2 y núcleo C0 de FAM05",
                                   "manifiesto del lote 2 (mallas de origen y pares existentes)"],
                   "se_genera_de_nuevo": ["filas frontier_result de las 383 mallas E4 (4.115 nodos y sus laterales), con topología",
                                          "conciliación de los 391 pares desde las salidas nuevas validadas"],
                   "solo_para_comparar": ["frontier_result y conciliación de la ejecución aceptada rem121 (= objetos del catálogo FAM06)"],
                   "no_cubre": ["L1-COORD y su recuperación (FAM07)", "búsquedas de supremos", "otras familias"]},
            "pilotos": leer(DATOS / "pilotos.json") if (DATOS / "pilotos.json").is_file() else None}
