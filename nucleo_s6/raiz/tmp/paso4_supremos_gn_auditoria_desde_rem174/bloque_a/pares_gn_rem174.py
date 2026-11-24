# -*- coding: utf-8 -*-
"""rem174 — BLOQUE A: producto documental de los ocho pares G/N históricos y mapa de cobertura 8/383/391.

Derivación declarada: la lógica de localización y cotejo procede de W/review_20261108_rem174_localization.py (21714d26…) y
W/review_20261108_rem174_documentary_checks.py (7fed38b5…), leídos y NO ejecutados (escriben en W). Cambios: destinos propios en Y; se
autentican además la raíz rem174 (196b4e24…), el dictamen rem118 (ea0dcf8e…, §3 conserva los certificados) y la conciliación E4 contra el
inventario fijado por el libro L_rem122; cada lado lleva todos sus campos persistidos (primitivas, menú, dominio τ con bordes, registro,
huella, estado, garantía, C2, B_pot, error normalizado, valor y cotas en R, testigo e identidad histórica) y su coincidencia con el mapa
aceptado; no se emite ninguna búsqueda de §18.7 aquí.
Solo biblioteca estándar: lee bytes guardados y compara intervalos ya certificados con Fraction; no importa el modelo ni reconstruye
intervalos, B_pot o puntos. Uso: pares_gn_rem174.py <R> <Y> <salida_relativa_a_Y>"""
import hashlib
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

R, Y = Path(sys.argv[1]), Path(sys.argv[2])
OUT = Y / sys.argv[3]
OUT.mkdir(parents=False, exist_ok=False)
W = Path(r"@@W_BS1@@")
T = R / "tmp"
H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
FUENTES, INV = {}, {}


def lee(p, esperado=None):
    b = Path(p).read_bytes()
    h = H(b)
    if esperado is not None:
        assert h == esperado, ("HUELLA", str(p), h)
    FUENTES[str(p)] = {"sha256": h, "bytes": len(b)}
    return b


def inventario(area):
    if area not in INV:
        b = lee(T / area / "audit/entrega.json")
        INV[area] = (json.loads(b), H(b))
    return INV[area]


def miembro(area, rel):
    inv, ih = inventario(area)
    b = lee(T / area / rel)
    e = inv["files"][rel]
    assert H(b) == e["sha256"] and len(b) == e["bytes"], ("MIEMBRO_NO_AUTENTICO", area, rel)
    return b, ih


# ------------------------------------------------------------ raíz, autoridades y fuentes fijadas
RAIZ = json.loads(lee(W / "FUENTES_SUPREMOS_GN_AUDITORIA_PROD4_6_REM174.json", "196b4e24750d4bb1234a71d36a672b4056487c96b7300bd23c253c0e4db9e0ea"))
PIN_FUENTES = {Path(k.replace("\\", "/")).as_posix(): v for k, v in RAIZ["source_files_sha256"].items()}
D118 = lee(W / "review_20261029_rem118_dictamen.txt", "ea0dcf8eb9de234aee279f799e4153c528c0ea84890f4c919485c98c755bc6bd").decode("utf-8").splitlines()
CERT = json.loads(lee(W / "review_20261029_rem118_certificates.json", "f294a7b4787a95244145728ccdf31ac75aab046fbce6c7c37a96e8b8b1d77362"))
L122 = json.loads(lee(W / "review_20261029_rem122_E4_aceptada.json", "8b70afc6398664534451f3945fe3b93e9dfdca48190deaf887a70e92eca19608"))
assert not CERT["failures"] and CERT["units"] == 2111
CERT_FILAS = {r["unit"]: r for r in CERT["rows"]}

mb, ih_mapa = miembro("paso4_impacto_certificados_desde_rem117", "impacto/MAPA_IMPACTO_REM117.json")
assert ih_mapa in D118[10], "INVENTARIO_DEL_MAPA_NO_CITADO_POR_D_rem118"
MAPA = json.loads(mb)
cb, ih_conc = miembro("paso4_e4_coord_desde_rem121", "conciliacion/CONCILIACION_E4_REM121.json")
assert L122["inventory_sha256"] == ih_conc, "CONCILIACION_E4_NO_FIJADA_POR_L_rem122"
CONC = json.loads(cb)
l2b, _ = miembro("paso4_lote2_cobertura_desde_rem114", "lote2/LOTE2_MANIFIESTO.json")
e4b, _ = miembro("paso4_lote2_cobertura_desde_rem114", "lote2/LOTE2E4_MANIFIESTO.json")
for nombre, b in (("LOTE2_MANIFIESTO.json", l2b), ("LOTE2E4_MANIFIESTO.json", e4b)):
    k = (R / "tmp/paso4_lote2_cobertura_desde_rem114/lote2" / nombre).as_posix()
    assert PIN_FUENTES.get(k) == H(b), ("MANIFIESTO_NO_FIJADO_POR_LA_RAIZ_REM174", nombre)
L2, E4M = json.loads(l2b), json.loads(e4b)


def clave(valores, dominio, j, d):
    return (tuple(sorted((n, str(Fraction(v))) for n, v in valores.items())),
            tuple(sorted((n, v if isinstance(v, bool) else str(Fraction(v))) for n, v in dominio.items())), j, d)


# ------------------------------------------------------------ registros persistentes (mapa aceptado por D_rem118 §3)
REG, PORCLAVE, UNID = {}, defaultdict(list), defaultdict(list)
for fila in MAPA["unidades_detalle"]:
    rec = fila["certificado"]["registro"]
    cf = CERT_FILAS[fila["unidad"]]
    assert cf["record"] == rec and all(cf["checks"].values()) and cf["contract"] == fila["contrato"], ("REM118_FILA", fila["unidad"])
    UNID[rec].append({"unidad": fila["unidad"], "contrato": fila["contrato"], "entrega": fila["entrega"], "j": fila["j"], "diseno": fila["diseno"],
                      "C2": fila["C2"], "certificado_mapa": {k: fila["certificado"][k] for k in ("error_kind", "estado", "C2", "lower", "upper", "numerical_error",
                                                                                                    "final_n", "tau_d_testigo", "valido")},
                      "rem118_comprobaciones": cf["checks"]})
    if rec in REG:
        continue
    area, rel = rec.split("/", 1)
    rb, ih = miembro(area, rel)
    assert PIN_FUENTES.get((T / rec).as_posix()) == H(rb), ("REGISTRO_NO_FIJADO_POR_LA_RAIZ_REM174", rec)
    doc = json.loads(rb)
    c, p = doc["contenido"]["ceiling"], doc["contenido"]["payload"]
    assert doc["esquema"] == "techo-persistente-v2" and c["status"] == "complete" and c["sup"]["error_kind"] == "certified_bound", ("NO_ES_TECHO_CERTIFICADO", rec)
    k = clave({x["parameter_id"]: x["value"] for x in p["values"]}, p["tau_domain"], p["instrument_j"], p["design_v"])
    REG[rec] = {"doc": doc, "sha256": H(rb), "bytes": len(rb), "area": area, "inventario_area_sha256": ih, "clave": k}
    PORCLAVE[k].append(rec)
for rec, us in UNID.items():
    c = REG[rec]["doc"]["contenido"]["ceiling"]
    for u in us:
        cm = u["certificado_mapa"]
        assert (cm["C2"], cm["numerical_error"], cm["lower"], cm["upper"], cm["final_n"], cm["estado"], cm["error_kind"]) == \
            (c["C2"], c["numerical_error"], c["sup"]["lower"], c["sup"]["upper"], c["sup"]["final_n"], c["status"], c["sup"]["error_kind"]), ("CONTENIDO_DISTINTO_DEL_MAPA", rec)

# ------------------------------------------------------------ fronteras de los manifiestos (estructura exacta de cada lado)
FRONT = {}
for nombre, mm in (("LOTE2_MANIFIESTO", L2), ("LOTE2E4_MANIFIESTO", E4M)):
    for etiqueta, fila in mm["L1-ELAST"]["fronteras"].items():
        d, j = etiqueta.split("|")[:2]
        for fid in {fila["frontier_id"], *fila.get("frontier_ids_equivalentes", [])}:
            FRONT.setdefault(fid, (fila, d, j, nombre, etiqueta))
        # las contrapartes E4 llevan la fila estructural exacta de su lado original (malla_de_origen = diseño|menú|frontera)
        origen = (fila.get("origen") or {}).get("malla_de_origen")
        if origen:
            od, oj, of = origen.split("|", 2)
            FRONT.setdefault(of, (fila, od, oj, nombre + " (malla_de_origen)", etiqueta))


def lado(fid, d, j):
    fila, dd, jj, man, et = FRONT[fid]
    assert dd == d and jj == j, ("FRONTERA_CON_OTRO_DISENO_O_MENU", fid)
    k = clave(fila["clave_estructural"], fila["dominio_tau"], j, d)
    return {"frontera": fid, "manifiesto": man, "etiqueta": et, "registros": PORCLAVE.get(k, [])}, k


def ficha(rec, fid, kfr):
    r = REG[rec]
    doc = r["doc"]
    c, p = doc["contenido"]["ceiling"], doc["contenido"]["payload"]
    s = c["sup"]
    e = Fraction(c["numerical_error"])
    assert r["clave"] == kfr, ("REGISTRO_Y_FRONTERA_CON_ENTRADAS_DISTINTAS", rec)
    return {"frontera": fid, "unidades": UNID[rec], "contratos": sorted({u["contrato"] for u in UNID[rec]}),
            "registro": {"ruta": rec, "sha256": r["sha256"], "bytes": r["bytes"], "area": r["area"], "inventario_area_sha256": r["inventario_area_sha256"],
                         "esquema": doc["esquema"], "clave_compat": doc["clave_compat"], "contenido_sha256": doc["contenido_sha256"], "corrida_sha256": doc["corrida_sha256"]},
            "identidad_historica": {"run_class": doc["identidad_corrida"]["autoridad"]["run_class"], "etiqueta": doc["identidad_corrida"]["autoridad"]["etiqueta"],
                                    "contrato_sha256": doc["identidad_corrida"]["autoridad"]["contrato_sha256"], "tecnica": p["technical"],
                                    "theory_sha256": p["theory_sha256"], "payload_kind": p["kind"], "origen": "certificado histórico conservado (rem118 §3); no recalculado con C0"},
            "primitivas": p["values"], "menu": p["instrument_j"], "diseno": p["design_v"], "dominio_tau": p["tau_domain"], "barras": doc["contenido"]["bars"],
            "estado": c["status"], "instrumento_disponible": c["instrument_available"], "razon": c["reason"],
            "garantia": {"error_kind": s["error_kind"], "alcanzado": s["attained"], "convergido": s["converged"], "final_n": s["final_n"], "clase": "cota_certificada_techo"},
            "escala_normalizada": {"C2": c["C2"], "B_pot": c["B_pot"], "error_normalizado": c["numerical_error"],
                                   "encierro_exacto": [str(Fraction(c["C2"]) - e), str(Fraction(c["C2"]) + e)]},
            "escala_R": {"sup": s["sup"], "lower": s["lower"], "upper": s["upper"], "error_R": s["numerical_error"], "level_values": s["level_values"]},
            "testigo": {"tau_d": s["tau_d"], "tau_f": s["tau_f"], "witnesses": s["witnesses"], "n_jump_points": s["n_jump_points"],
                        "lateral": {"axis": s["lateral_axis"], "low": s["lateral_low"], "high": s["lateral_high"]}}}


# ------------------------------------------------------------ 391 pares conciliados (L_rem122) y los ocho existentes
EXIST = E4M["L1-ELAST"]["pares_existentes"]
assert len(EXIST) == 8
PARES, COB = [], []
for par in CONC["detalle"]:
    j = par["instrumento"]
    lados, claves = {}, {}
    for d in ("G", "N"):
        lados[d], claves[d] = lado(par[d], d, j)
    n_loc = sum(1 for d in ("G", "N") if lados[d]["registros"])
    dup = [d for d in ("G", "N") if len(lados[d]["registros"]) > 1]
    COB.append({"par": par["par"], "instrumento": j, "tipo": "existente" if par["par"].startswith("existente:") else "contraparte_E4",
                "lados": {d: {"frontera": lados[d]["frontera"], "manifiesto": lados[d]["manifiesto"], "registros": lados[d]["registros"]} for d in ("G", "N")},
                "lados_localizados": n_loc, "lados_con_registro_duplicado": dup})
    if n_loc < 2:
        continue
    i = int(par["par"].split(":")[1])
    assert par["par"] == "existente:%d" % i and EXIST[i]["G"] == par["G"] and EXIST[i]["N"] == par["N"] and EXIST[i]["j"] == j, ("PAR_NO_EXISTENTE", par["par"])
    assert not dup and claves["G"][:3] == claves["N"][:3], ("CONTRAPARTE_DUPLICADA_O_ENTRADAS_DISTINTAS", par["par"])
    fg, fn = ficha(lados["G"]["registros"][0], par["G"], claves["G"]), ficha(lados["N"]["registros"][0], par["N"], claves["N"])
    tg, tn = fg["identidad_historica"]["tecnica"], fn["identidad_historica"]["tecnica"]
    dif = {k: {"G": tg[k], "N": tn[k]} for k in sorted(set(tg) | set(tn)) if tg.get(k) != tn.get(k)}
    gl, gh = (Fraction(x) for x in fg["escala_normalizada"]["encierro_exacto"])
    nl, nh = (Fraction(x) for x in fn["escala_normalizada"]["encierro_exacto"])
    res = ("G_sobre_N_certificado" if gl > nh else "N_sobre_G_certificado" if nl > gh else
           "C2_almacenado_igual" if fg["escala_normalizada"]["C2"] == fn["escala_normalizada"]["C2"] else "intervalos_solapados")
    PARES.append({"par": par["par"], "indice_pares_existentes": i, "instrumento": j, "G": fg, "N": fn,
                  "emparejamiento": {"primitivas_iguales": claves["G"][0] == claves["N"][0], "dominio_tau_igual": claves["G"][1] == claves["N"][1],
                                     "menu_igual": fg["menu"] == fn["menu"] == j, "disenos": [fg["diseno"], fn["diseno"]],
                                     "criterio": "identidad exacta de primitivas racionales, dominio τ con bordes, menú y diseño; nunca proximidad numérica"},
                  "diferencias_tecnicas": dif, "teoria_igual": fg["identidad_historica"]["theory_sha256"] == fn["identidad_historica"]["theory_sha256"],
                  "comparacion_normalizada": {"G": [str(gl), str(gh)], "N": [str(nl), str(nh)], "resultado": res, "c2_almacenado_igual": fg["escala_normalizada"]["C2"] == fn["escala_normalizada"]["C2"],
                                              "clase": "aritmetica_exacta", "nota": "comparación racional de intervalos ya certificados (C2 ± error normalizado); no recertifica"},
                  "comparacion_R_informativa": {"G": [fg["escala_R"]["lower"], fg["escala_R"]["upper"]], "N": [fn["escala_R"]["lower"], fn["escala_R"]["upper"]],
                                                "nota": "escala R conservada aparte; no se usa como criterio ni se agrega tolerancia"}})
assert [p["par"] for p in PARES] == ["existente:%d" % i for i in range(8)], "OCHO_PARES_EXISTENTES"
res_c = Counter(p["comparacion_normalizada"]["resultado"] for p in PARES)
lados_c = Counter(c["lados_localizados"] for c in COB)
un_lado = Counter(c["instrumento"] for c in COB if c["lados_localizados"] == 1)
RESUMEN = {"pares_E4_conciliados": len(COB), "pares_completos": len(PARES), "pares_completos_por_menu": dict(sorted(Counter(p["instrumento"] for p in PARES).items())),
           "pares_un_lado": lados_c.get(1, 0), "pares_un_lado_por_menu": dict(sorted(un_lado.items())), "pares_sin_lado": lados_c.get(0, 0),
           "lados_con_registro_duplicado": sum(len(c["lados_con_registro_duplicado"]) for c in COB),
           "comparaciones": dict(sorted(res_c.items())), "pares_con_diferencias_tecnicas": [p["par"] for p in PARES if p["diferencias_tecnicas"]],
           "registros_distintos_del_mapa": len(REG), "claves_estructurales_distintas": len(PORCLAVE), "unidades_historicas": sum(len(v) for v in UNID.values()),
           "afirmacion_universal": False, "tabla_391_supremos": False,
           "alcance": "ocho pares completos con techos históricos certificados; 383 pares con un solo lado en el corpus examinado (mapa rem117 aceptado por "
                      "rem118 §3); las 391 geometrías E4 son otro objeto (L_rem122). Seis intervalos G certificados por encima de N no prueban diferencia "
                      "universal; la igualdad del C2 guardado en dos pares f no prueba igualdad de supremos ni de funciones."}
REGLA_E4 = {"regla": E4M["L1-ELAST"].get("regla"), "alternativa_sin_opcion": E4M.get("alternativa_sin_opcion")}


def w(nombre, obj):
    with open(OUT / nombre, "x", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=1) + "\n")


w("PARES_GN_REM174.json", {"kind": "pares-gn-historicos-rem174", "naturaleza": "producto documental; no es libro, no es producción C0 ni tabla de 391 supremos",
                           "resumen": RESUMEN, "pares": PARES})
w("COBERTURA_GN_REM174.json", {"kind": "cobertura-gn-rem174", "resumen": RESUMEN, "regla_contrapartes_E4": REGLA_E4, "pares": COB})
w("FUENTES_BLOQUE_A_REM174.json", {"kind": "fuentes-bloque-a-rem174", "fuentes": FUENTES,
                                   "inventarios": {a: h for a, (_, h) in INV.items()},
                                   "cadena": {"registros": "mapa rem117 (miembro del inventario fdc22b85… citado en D_rem118 l.11; §3 conserva los 2.111 certificados) "
                                                           "→ unidades_detalle[*].certificado.registro → registro autenticado por el inventario de su área y por la raíz rem174 "
                                                           "(source_files_sha256); contenido igual al certificado del mapa",
                                              "pares": "CONCILIACION_E4_REM121.json, miembro del inventario fijado por L_rem122 /inventory_sha256",
                                              "fronteras": "LOTE2_MANIFIESTO y LOTE2E4_MANIFIESTO, miembros de su inventario y fijados por la raíz rem174 (identidad documental)"},
                                   "derivacion": {"review_20261108_rem174_localization.py": "21714d2618add458c83f3407a371b7040418c93003b17e99da14d43fa28636f8",
                                                  "review_20261108_rem174_documentary_checks.py": "7fed38b56b2c0ce3bec97ae8c4bbbc94675ee0c8d1dbe5e4c51f6e09e217d23d"}})
print(json.dumps(RESUMEN, ensure_ascii=False))
