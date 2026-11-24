"""rem160 — RUTA ÚNICA DE CONSTRUCCIÓN CORREGIDA (derivada de construir_sintesis_rem159.py, ed5c199b…, sellado en rem159 d823217f…). Únicos
cambios de lógica: los campos interpretativos se_sabe y no_se_concluye (hallazgos rem160 P4-EXP8-EPS-SIGNOS y P4-EXP8-NO-DECIDIDAS-N3: la
inconclusión se describe por las desigualdades con ε=1/100, sin exigir signos opuestos; las doce COV no decididas quedan desconocidas y la
categoría padre se presenta solo como histórico), más los metadatos kind/manifiesto. Todo campo numérico, categoría, cota, fuente y
localizador se construye exactamente igual que en rem159. Las frases que dependen de los datos se seleccionan por condiciones sobre las cotas
guardadas (fracciones exactas), nunca por una lista de identificadores.
Antes, rem159 — RUTA ÚNICA DE CONSTRUCCIÓN de la síntesis Exp8 por afirmación (PROD4.5.6). Derivado documental, CANDIDATO para revisión: no es
producción ni reemplaza libros o tablas históricas. Solo lee productos aceptados autenticados por huella contra su libro o dictamen, los enlaza
por el identificador estable de afirmación, aplica el suplemento P7 UNA vez (overlay_rule del libro rem155) y cuenta. No llama al modelo, K1,
bridge, GridCell.Q, supremos ni contextos S6; no importa paquetes científicos ni vuelve a ejecutar validadores o conductores; no reconstruye
superficies ni supremos. Aritmética: solo lectura de cotas guardadas (texto racional) y recuentos.
Escribe en exclusiva (destinos nuevos): <Y>/fuentes/MANIFIESTO_SINTESIS.json, <Y>/sintesis/EXP8_POR_AFIRMACION.jsonl, <Y>/sintesis/RESUMEN_EXP8.json.
Uso: python -B -I -X utf8 construir_sintesis_rem160.py <Y>"""
import datetime as dt
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

Y = Path(sys.argv[1])
T = Y.parent
W = Path(r"@@W_BS1@@")
H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
LIBROS = {"ENF": ("review_20261105_rem148_EXP8_ENF_aceptada.json", "74342fd08788103af28fcba180e864a91a6c02cd7737d67bb5e94e6123ead571"),
          "COV": ("review_20261105_rem152_COV_aceptada.json", "accdf8abd212e41ea34719853ec36ba09f3a0f1e54b3309ec6925a018eb1490c"),
          "P7": ("review_20261105_rem155_P7_aceptado.json", "ae2c36e5d5c509b879eb9c423e7564e215ee1bf3d85617e4e3cf3039fca6d652"),
          "Q": ("review_20261106_rem159_Q_local_aceptada.json", "a6946c0e8fbe06db29f9f9fef9afdf91621ff2354d6eacbb169ac6a751c8db5e"),
          "Q_DIAG": ("review_20261106_rem156_Q_diagnostico.json", "7609b7bdfb0bc66305100d3b2967e7612e5430d36f1d653c54f25ba49d4f1301"),
          "ENF_ORIGEN": ("review_20261101_rem132_ENF_integral_aceptado.json", "500537615c2c0deebebec90165f6aae5fe2e7272b8fe1976ca00376a8c34debf")}
DICT = {"rem148": ("review_20261105_rem148_dictamen.txt", "3e7977c33dd5a4b74870c8efb4959b66cbaedcd1028fad544d92c45aaaea42d1"),
        "rem149": ("review_20261105_rem149_dictamen.txt", "669af810c99a8a1c24b52a589f53996de7d89a775b52a51c40e005049d2b72b5"),
        "rem157": ("review_20261106_rem157_dictamen.txt", "65e4ccba0ef8ed89e0b0e5908cce2f4f66bc026fbc6f85bcbc959c0be6040c52"),
        "rem158": ("review_20261106_rem158_dictamen.txt", "6a9173e21d10f29e68359a11f2a269a458273d3dd1654aae49067c2cfb09e51b"),
        "rem159": ("review_20261106_rem159_dictamen.txt", "58998d564ae69d8a7348447309c4faedf8c911f88d68c6fa2361b55db848714b"),
        "eleccion_m_Q": ("review_20261106_rem158_eleccion_m_Q.json", "1b95216b1785d4b9284a23297bf4ebc1f84a28768b011c53018251a59cec7643")}
libro = {}
for k, (n, h) in list(LIBROS.items()) + list(DICT.items()):
    b = (W / n).read_bytes()
    assert H(b) == h, ("LIBRO_O_DICTAMEN_NO_AUTENTICO", n)
    if n.endswith(".json"):
        libro[k] = json.loads(b)


def producto(ruta, sha, autoridad, campo):
    p = Path(ruta)
    b = p.read_bytes()
    assert H(b) == sha, ("FUENTE_NO_AUTENTICA", str(p))
    return b, {"ruta": str(p), "sha256": sha, "bytes": len(b), "autorizada_por": {"libro": autoridad, "sha256": dict(LIBROS)[autoridad][1] if autoridad in LIBROS else None,
                                                                                    "campo": campo}}


qp = libro["Q"]["products"]
F = {}
eb, F["ENF_POR_AFIRMACION"] = producto(libro["ENF"]["product"], libro["ENF"]["product_sha256"], "ENF", "product / product_sha256")
cov_ruta = next(r for r in libro["COV"]["products"] if r.endswith("CONCILIACION_COV.jsonl"))
cb, F["CONCILIACION_COV"] = producto(cov_ruta, libro["COV"]["products"][cov_ruta], "COV", "products[...CONCILIACION_COV.jsonl]")
p7_ruta = next(r for r in libro["P7"]["products"] if r.endswith("SUPLEMENTO_P7.jsonl"))
assert libro["P7"]["products"][p7_ruta] == libro["P7"]["summary"]["producto_sha256"], "P7_HUELLA_INCOHERENTE_EN_SU_LIBRO"
pb, F["SUPLEMENTO_P7"] = producto(p7_ruta, libro["P7"]["products"][p7_ruta], "P7", "products[...SUPLEMENTO_P7.jsonl] = summary.producto_sha256")
qres = {}
for v, t in (("contrato", "Q-MAT-CONTRATO"), ("conservadora", "Q-MAT-CONSERVADORA")):
    r = next(x for x in qp if x.endswith(t + "\\resultado.json"))
    b, F["Q_" + v] = producto(r, qp[r], "Q", "products[...%s\\resultado.json]" % t)
    qres[v] = json.loads(b)
F["Q_DIAGNOSTICO_GENERAL"] = {"ruta": str(W / LIBROS["Q_DIAG"][0]), "sha256": LIBROS["Q_DIAG"][1],
                              "autorizada_por": {"libro": "Q", "campo": "general_diagnostic_separate", "sha256": LIBROS["Q"][1]},
                              "uso": "referencia del resultado técnico general 0<m<=1 (diagnóstico aceptado, separado de la producción)"}
assert libro["Q"]["general_diagnostic_separate"]["sha256"] == LIBROS["Q_DIAG"][1], "DIAGNOSTICO_Q_NO_LIGADO"


def jsonl(b):
    return [json.loads(x) for x in b.decode("utf-8").splitlines() if x.strip()]


enf, cov, p7 = jsonl(eb), jsonl(cb), jsonl(pb)
loc = {}
for nombre, filas in (("ENF_POR_AFIRMACION", enf), ("CONCILIACION_COV", cov), ("SUPLEMENTO_P7", p7)):
    ids = [f["afirmacion"] for f in filas]
    assert len(ids) == len(set(ids)), ("DUPLICADO_EN_FUENTE", nombre)
    loc[nombre] = {a: i + 1 for i, a in enumerate(ids)}
assert set(loc["ENF_POR_AFIRMACION"]) == set(loc["CONCILIACION_COV"]) and len(enf) == 1728, "UNIVERSO_ENF_COV_DISTINTO"
E = {f["afirmacion"]: f for f in enf}
C = {f["afirmacion"]: f for f in cov}
P = {f["afirmacion"]: f for f in p7}
assert len(P) == 7 and set(P) <= set(E), "P7_FUERA_DEL_UNIVERSO"
QA = {v: {a["afirmacion"]: a for a in qres[v]["afirmaciones"]} for v in qres}
QP = {v: {(p["afirmacion"], p["lado"]): p for p in qres[v]["posiciones"]} for v in qres}
assert all(set(QA[v]) == set(E) for v in QA), "UNIVERSO_Q_DISTINTO"
ENF_NODEC = "no_decidida_por_testigos (mantener la robustez exige el supremo ENF sobre todo el soporte)"
LADO_ENF = ("clave_transformada_sha256", "cell_id", "unidad", "conjunto", "estado_evidencia", "estado_techo_historico", "origen_G", "resolucion",
            "certificado_resolucion_sha256", "signo_padre", "signo_enf", "G_padre_ENF", "C2_enf", "K1_reutilizado", "G_enf", "dG", "veredicto_T7",
            "enlazado", "motivo_no_enlace")
LADO_COV = ("clave_cov", "cell_id", "unidad", "signo_padre", "signo_cov_certificado", "g_lo", "g_hi", "C2_cov", "G_padre", "K1", "error_R", "error_normalizado")
DIM = ("pais", "pid", "kind", "familia", "j", "escenario", "diseno", "cota", "bloque", "capa", "disponibilidad")


def sel(d, ks):
    return {k: d.get(k) for k in ks} if isinstance(d, dict) else None


EPS = Fraction(1, 100)
filas = []
for a in sorted(E):
    e, c, p = E[a], C[a], P.get(a)
    q = {v: QA[v][a] for v in QA}
    assert e["categoria_original"] == c["categoria_original"] == q["contrato"]["categoria_original"] == q["conservadora"]["categoria_original"], ("CATEGORIA_INCOHERENTE", a)
    assert (p is None) or p["categoria_original"] == e["categoria_original"], ("CATEGORIA_P7_INCOHERENTE", a)
    padre = {}
    for lado in ("sup", "inf"):
        x = QP["contrato"][(a, lado)]
        padre[lado] = {"origen": x["origen"], "unidad": x["unidad"], "fuente_sha256": x["fuente_sha256"], "clave_techo": x["clave_techo"],
                       "cell_id_ENF": (e.get(lado) or {}).get("cell_id")}
    enf_final = p["canales"]["ENF"]["canal"] if p else e["canal_eta_f"]
    cov_final = p["canales"]["COV"]["canal"] if p else c["canal_phi"]
    sup7 = None
    if p:
        sup7 = {"fuente": {"ruta": F["SUPLEMENTO_P7"]["ruta"], "sha256": F["SUPLEMENTO_P7"]["sha256"], "linea": loc["SUPLEMENTO_P7"][a]},
                "unidad": p["unidad"], "cell_id": p["cell_id"], "lado_faltante": p["lado_faltante"], "K1": p["K1"], "K1_tipo": p["K1_tipo"],
                "regla": libro["P7"]["overlay_rule"], "aplicaciones": 1}
    fila = {
        "afirmacion": a,
        "dimensiones": dict(sel(e, DIM), conjunto_sup=(e.get("sup") or {}).get("conjunto"), conjunto_inf=(e.get("inf") or {}).get("conjunto"),
                            fuente_dimensiones="ENF_POR_AFIRMACION (campos guardados; ninguno deducido)"),
        "categoria_original": e["categoria_original"], "conjunto_padre": q["contrato"]["conjunto"], "padre": padre,
        "ENF": {"escenario": "ABL-ENF eta_f/2, resto fijo", "conclusion": enf_final,
                "conclusion_historica": e["canal_eta_f"], "cobertura_historica": e["cobertura_ENF"],
                "cambio_de_signo_en_testigos": e.get("cambio_de_signo_en_testigos_ENF"), "descompuesta_rem108": e.get("descompuesta_rem108"),
                "motivo_sin_descomposicion": e.get("motivo_sin_descomposicion"), "lados": {l: sel(e.get(l), LADO_ENF) for l in ("sup", "inf")},
                "suplemento_P7": (dict(sup7, canal=p["canales"]["ENF"]["canal"], cobertura=p["canales"]["ENF"]["cobertura"],
                                       presente_origen=p["canales"]["ENF"]["presente_origen"]) if p else None),
                "fuente": {"ruta": F["ENF_POR_AFIRMACION"]["ruta"], "sha256": F["ENF_POR_AFIRMACION"]["sha256"], "linea": loc["ENF_POR_AFIRMACION"][a],
                           "libro": LIBROS["ENF"][0]}},
        "COV": {"escenario": "ABL-COV phi/2 (coverage_half), resto fijo", "conclusion": cov_final,
                "conclusion_historica": c["canal_phi"], "cobertura_historica": c["cobertura_COV"],
                "cambio_de_signo_certificado": c.get("cambio_de_signo_certificado_COV"), "lados": {l: sel(c.get(l), LADO_COV) for l in ("sup", "inf")},
                "suplemento_P7": (dict(sup7, canal=p["canales"]["COV"]["canal"], cobertura=p["canales"]["COV"]["cobertura"],
                                       presente_origen=p["canales"]["COV"]["presente_origen"]) if p else None),
                "fuente": {"ruta": F["CONCILIACION_COV"]["ruta"], "sha256": F["CONCILIACION_COV"]["sha256"], "linea": loc["CONCILIACION_COV"][a],
                           "libro": LIBROS["COV"][0]}},
        "Q": {"escenario": "EXT-Q m_Q=1/2 global (sensibilidad exploratoria elegida después del diagnóstico)", "m": "1/2",
              "versiones": {v: {"canal": q[v]["canal"], "region": q[v]["region"], "lados_demostrados": q[v]["lados_demostrados"], "cobertura": q[v]["cobertura"],
                                "posiciones": {l: sel(QP[v][(a, l)], ("g_lo", "g_hi", "lado_veredicto", "signo", "unidad", "origen")) for l in ("sup", "inf")},
                                "fuente": {"ruta": F["Q_" + v]["ruta"], "sha256": F["Q_" + v]["sha256"], "libro": LIBROS["Q"][0]}} for v in ("contrato", "conservadora")},
              "diagnostico_general": {"libro": LIBROS["Q_DIAG"][0], "sha256": LIBROS["Q_DIAG"][1], "dominio": "0<m<=1",
                                      "afirma": ("preservación de la inconclusión bajo la regla eps para todo 0<m<=1" if q["contrato"]["conjunto"] == "inconclusa"
                                                 else "el resultado general no se extiende a las 16 robustas padre")}},
        "P7": sup7,
        "garantias": {"ENF": "techos certified_bound; K1 reutilizado (binary64)", "COV": "techos certified_bound, escala normalizada (error <= 1e-7)",
                      "Q": "racional exacta sobre binary64 guardados; contrato e_C2, conservadora e_G (P7 = contrato)", "eps": "1/100, desigualdades estrictas"},
    }
    # rem160: se_sabe / no_se_concluye por las desigualdades de inconclusión (ε=1/100, estrictas), sin equiparar preservación con signos opuestos.
    sabe, no = [], ["causalidad empírica", "eslabón que provoca el cruce", "orden o dominancia de canales", "política óptima"]
    REGLA = "se conservan dos testigos que satisfacen las desigualdades de inconclusión con ε=0,01 (sup con G>−ε, inf con G<+ε); el criterio no exige signos opuestos"
    cs, ci = c.get("sup"), c.get("inf")
    if fila["conjunto_padre"] == "inconclusa":
        if enf_final == "inconclusa_preservada":
            sabe.append("ENF eta_f/2: " + REGLA + "; la inconclusión persiste en este contraste finito")
        if cov_final == "inconclusa_preservada":
            sabe.append("COV phi/2: " + REGLA + "; la inconclusión persiste en este contraste finito")
            if cs and ci and cs["signo_cov_certificado"] == -1 and ci["signo_cov_certificado"] == -1:
                assert Fraction(cs["g_lo"]) > -EPS and Fraction(ci["g_hi"]) < EPS, ("REGLA_EPS_NO_SE_CUMPLE", a)
                sabe.append("COV phi/2: ambos testigos guardados son negativos (signo certificado −1 en sup y en inf); la inconclusión se conserva porque "
                            "la cota inferior certificada del testigo sup permanece por encima de −ε y la superior del testigo inf por debajo de +ε")
        elif cov_final == "no_decidida_por_testigos":
            lado_sup = ("su cota superior certificada queda por debajo de −ε" if cs and Fraction(cs["g_hi"]) < -EPS
                        else "no queda certificado por encima de −ε")
            lado_inf = ("el testigo inf sigue satisfaciendo G<+ε" if ci and Fraction(ci["g_hi"]) < EPS else "el testigo inf no queda certificado por debajo de +ε")
            sabe.append("COV phi/2: el testigo sup guardado ya no satisface G>−ε (" + lado_sup + "); " + lado_inf + "; con los testigos disponibles "
                        "la clasificación bajo phi/2 queda sin decidir: no se sabe si la afirmación conserva la inconclusión o es robusta en ese escenario")
            no.append("clasificación de la afirmación bajo phi/2: no están demostradas ni la preservación de la inconclusión ni la robustez")
        if all(q[v]["canal"] == "inconclusa_preservada" for v in q):
            sabe.append("Q m=1/2: ambos lados demostrados en contrato y conservadora (sup con G>−ε, inf con G<+ε); inconclusión preservada en el escenario reducido")
        no.append("clasificación de toda la afirmación bajo otras perturbaciones o soportes")
    else:
        sabe.append("ENF y COV: los testigos disponibles no deciden la clasificación en los escenarios transformados; la categoría "
                    "robusta_infactible_certificada se conserva como histórico del escenario padre y no demuestra la categoría transformada")
        sabe.append("Q m=1/2: el testigo sup refuta la robustez infactible en el escenario reducido (ambas versiones); no demuestra robustez factible "
                    "ni invalida el escenario padre; la categoría padre queda intacta como histórico")
        no.extend(["robustez factible", "robustez bajo ENF/COV/Q sobre todo el soporte", "invalidación del resultado del escenario padre"])
    fila["se_sabe"], fila["no_se_concluye"] = sabe, no
    filas.append(fila)

# ---- RESUMEN (derivado de las filas) -------------------------------------------------------------------------------------------------------
cnt = lambda it: dict(sorted(Counter(it).items(), key=lambda kv: str(kv[0])))  # noqa: E731
res = {"kind": "resumen-exp8-rem160", "candidato_para_revision": True, "produccion": False, "afirmaciones": len(filas),
       "categoria_original": cnt(f["categoria_original"] for f in filas), "conjunto_padre": cnt(f["conjunto_padre"] for f in filas)}
for canal in ("ENF", "COV"):
    res[canal] = {"final_con_P7": cnt(f[canal]["conclusion"] for f in filas),
                  "historico_sin_P7": cnt(f[canal]["conclusion_historica"] for f in filas),
                  "final_por_conjunto_padre": {cj: cnt(f[canal]["conclusion"] for f in filas if f["conjunto_padre"] == cj) for cj in ("inconclusa", "robusta")},
                  "final_por_categoria_original": {cat: cnt(f[canal]["conclusion"] for f in filas if f["categoria_original"] == cat)
                                                   for cat in sorted({f["categoria_original"] for f in filas})},
                  "suplemento_P7_aplicado": sum(1 for f in filas if f[canal]["suplemento_P7"])}
res["Q"] = {v: {"canal": cnt(f["Q"]["versiones"][v]["canal"] for f in filas),
                "canal_por_conjunto_padre": {cj: cnt(f["Q"]["versiones"][v]["canal"] for f in filas if f["conjunto_padre"] == cj) for cj in ("inconclusa", "robusta")},
                "region": cnt(f["Q"]["versiones"][v]["region"] for f in filas)} for v in ("contrato", "conservadora")}
res["Q"]["m"] = "1/2"
res["Q"]["veredictos_distintos_entre_versiones"] = sum(1 for f in filas for l in ("sup", "inf")
                                                      if f["Q"]["versiones"]["contrato"]["posiciones"][l]["lado_veredicto"] != f["Q"]["versiones"]["conservadora"]["posiciones"][l]["lado_veredicto"])
mg = libro["Q_DIAG"]["margins"]
res["Q"]["diagnostico_general"] = {"libro": LIBROS["Q_DIAG"][0], "dominio": libro["Q_DIAG"]["domain"],
                                   "m_estrella_contrato": {"exacto": mg["contrato"]["max_inf_threshold"], "aprox": mg["contrato"]["max_inf_threshold_float"]},
                                   "m_estrella_conservadora": {"exacto": mg["conservadora"]["max_inf_threshold"], "aprox": mg["conservadora"]["max_inf_threshold_float"]}}
pos_q = [(f["afirmacion"], l) for f in filas for l in ("sup", "inf")]
res["posiciones_Q"] = {"total": len(pos_q), "por_origen": cnt(f["Q"]["versiones"]["contrato"]["posiciones"][l]["origen"] for f in filas for l in ("sup", "inf")),
                       "nota": "3.456 posiciones Q no son 3.456 afirmaciones ni celdas distintas"}
celdas_base = {f["padre"][l]["unidad"] for f in filas for l in ("sup", "inf") if f["padre"][l]["origen"] == "filas_padre_aceptadas"}
res["celdas"] = {"unidades_padre_base_distintas": len(celdas_base), "unidades_P7": sorted({f["P7"]["unidad"] for f in filas if f["P7"]}),
                 "afirmaciones_con_P7": sum(1 for f in filas if f["P7"]), "afirmaciones_sin_P7": sum(1 for f in filas if not f["P7"]),
                 "nota": "las cuatro unidades P7 siguen separadas del censo base; COL-2024p queda fuera de este nivel (exclusión de alcance)"}
sc = [(f["afirmacion"], l, f["COV"]["lados"][l]) for f in filas for l in (f["COV"]["cambio_de_signo_certificado"] or [])]
res["COV_cambios_de_signo_certificados"] = {
    "ocurrencias": len(sc), "afirmaciones": len({x[0] for x in sc}), "celdas": len({x[2]["cell_id"] for x in sc}), "claves": sorted({x[2]["clave_cov"] for x in sc}),
    "direcciones": cnt("%s->%s" % (x[2]["signo_padre"], x[2]["signo_cov_certificado"]) for x in sc), "lados": cnt(x[1] for x in sc),
    "por_categoria_original": cnt(E[x[0]]["categoria_original"] for x in sc), "conclusion_COV": cnt(C[x[0]]["canal_phi"] for x in sc),
    "nota": "evidencia de posiciones/celdas/afirmaciones; no son cambios de categoría ni prueba de un canal dominante",
    "filas": [{"afirmacion": x[0], "lado": x[1], "clave_cov": x[2]["clave_cov"], "cell_id": x[2]["cell_id"], "signo_padre": x[2]["signo_padre"],
               "signo_cov": x[2]["signo_cov_certificado"], "g_lo": x[2]["g_lo"], "g_hi": x[2]["g_hi"]} for x in sorted(sc)]}
res["ENF_descomposicion_rem108"] = {"descompuestas_true": sum(1 for f in filas if f["ENF"]["descompuesta_rem108"] is True),
                                    "inconclusas_sin_descomposicion_rem108": sorted(f["afirmacion"] for f in filas if f["conjunto_padre"] == "inconclusa" and f["ENF"]["descompuesta_rem108"] is not True),
                                    "nota": "las descomposiciones históricas rem108 no se renombran como 1.712; las siete restantes se completan por el suplemento P7 sin convertirse en descomposiciones rem108"}
resol = [(f["afirmacion"], l, f["ENF"]["lados"][l]) for f in filas for l in ("sup", "inf") if f["ENF"]["lados"][l] and f["ENF"]["lados"][l].get("resolucion")]
res["ENF_resoluciones"] = {"lados_con_resolucion": len(resol), "estado_techo_historico": cnt(x[2].get("estado_techo_historico") for x in resol),
                           "claves": cnt(x[2].get("clave_transformada_sha256") for x in resol),
                           "tipos": cnt(json.dumps(x[2]["resolucion"].get("estado") if isinstance(x[2]["resolucion"], dict) else x[2]["resolucion"], ensure_ascii=False) for x in resol),
                           "estado_techo_historico_todas_las_claves": cnt(f["ENF"]["lados"][l].get("estado_techo_historico") for f in filas for l in ("sup", "inf") if f["ENF"]["lados"][l]),
                           "nota": "se conservan tal como están: cotas y testigos laterales, historial incomplete, sin argmax ni tasas de maximizador"}
DIMS = ("pais", "kind", "familia", "j", "escenario", "diseno", "cota", "bloque", "capa")
res["por_dimension"] = {}
for d in DIMS:
    vals = sorted({str(f["dimensiones"][d]) for f in filas})
    res["por_dimension"][d] = {v: {"denominador": sum(1 for f in filas if str(f["dimensiones"][d]) == v),
                                   "categoria_original": cnt(f["categoria_original"] for f in filas if str(f["dimensiones"][d]) == v),
                                   "ENF": cnt(f["ENF"]["conclusion"] for f in filas if str(f["dimensiones"][d]) == v),
                                   "COV": cnt(f["COV"]["conclusion"] for f in filas if str(f["dimensiones"][d]) == v),
                                   "Q_contrato": cnt(f["Q"]["versiones"]["contrato"]["canal"] for f in filas if str(f["dimensiones"][d]) == v)} for v in vals}
res["por_pais_y_bloque"] = {}
for f in filas:
    k = "%s|%s" % (f["dimensiones"]["pais"], f["dimensiones"]["bloque"])
    r = res["por_pais_y_bloque"].setdefault(k, {"denominador": 0, "ENF": Counter(), "COV": Counter(), "Q_contrato": Counter()})
    r["denominador"] += 1
    r["ENF"][f["ENF"]["conclusion"]] += 1
    r["COV"][f["COV"]["conclusion"]] += 1
    r["Q_contrato"][f["Q"]["versiones"]["contrato"]["canal"]] += 1
res["por_pais_y_bloque"] = {k: {kk: (dict(vv) if isinstance(vv, Counter) else vv) for kk, vv in v.items()} for k, v in sorted(res["por_pais_y_bloque"].items())}
res["nota_dimensiones"] = ("conteos documentales con denominador explícito; no son probabilidades ni tasas; pais '-' o None se conserva tal como lo da la "
                           "fuente (no se deduce); bloque macro/micro no se mezcla en por_pais_y_bloque; ninguna celda de referencia elegida a posteriori")
res["listas"] = {"COV_no_decididas_inconclusas": sorted(f["afirmacion"] for f in filas if f["conjunto_padre"] == "inconclusa" and f["COV"]["conclusion"] == "no_decidida_por_testigos"),
                 "robustas_padre": sorted(f["afirmacion"] for f in filas if f["conjunto_padre"] == "robusta"),
                 "P7": sorted(f["afirmacion"] for f in filas if f["P7"]),
                 "ENF_no_alcanzadas_preservadas_rem155": libro["P7"].get("nonattained_ENF_claims_preserved")}
res["cotejos_esperados_del_encargo"] = {
    "padre_1712_inconclusas_16_robustas": res["conjunto_padre"] == {"inconclusa": 1712, "robusta": 16},
    "categorias_1524_188_16": res["categoria_original"] == {"cambio_de_signo_certificado": 1524, "inconclusa_por_testigos_en_tolerancia": 188, "robusta_infactible_certificada": 16},
    "ENF_1712_preservadas_16_no_decididas": res["ENF"]["final_con_P7"] == {"inconclusa_preservada": 1712, ENF_NODEC: 16},
    "COV_1700_preservadas_28_no_decididas_12_mas_16": res["COV"]["final_con_P7"] == {"inconclusa_preservada": 1700, "no_decidida_por_testigos": 28}
    and res["COV"]["final_por_conjunto_padre"]["inconclusa"].get("no_decidida_por_testigos") == 12 and res["COV"]["final_por_conjunto_padre"]["robusta"] == {"no_decidida_por_testigos": 16},
    "Q_1712_preservadas_16_refutadas_ambas_versiones": all(res["Q"][v]["canal"] == {"inconclusa_preservada": 1712, "robustez_refutada_por_testigo_sup": 16} for v in ("contrato", "conservadora")),
    "COV_20_cambios_de_signo_dos_claves": res["COV_cambios_de_signo_certificados"]["ocurrencias"] == 20 and len(res["COV_cambios_de_signo_certificados"]["claves"]) == 2,
    "P7_siete_una_vez_cuatro_unidades": res["celdas"]["afirmaciones_con_P7"] == 7 and len(res["celdas"]["unidades_P7"]) == 4 and res["ENF"]["suplemento_P7_aplicado"] == 7 and res["COV"]["suplemento_P7_aplicado"] == 7,
    "posiciones_3456_3449_7": res["posiciones_Q"]["total"] == 3456 and res["posiciones_Q"]["por_origen"] == {"filas_padre_aceptadas": 3449, "suplemento_P7_lado_padre_faltante": 7},
    "nota": "valores comparados con los recuentos DERIVADOS de las filas; no se escriben en las filas"}
# ---- salidas -------------------------------------------------------------------------------------------------------------------------------
(Y / "fuentes").mkdir(exist_ok=True)
(Y / "sintesis").mkdir(exist_ok=True)
with (Y / "sintesis/EXP8_POR_AFIRMACION.jsonl").open("x", encoding="utf-8", newline="\n") as fh:
    for f in filas:
        fh.write(json.dumps(f, ensure_ascii=False, sort_keys=True) + "\n")
filas_sha = H((Y / "sintesis/EXP8_POR_AFIRMACION.jsonl").read_bytes())
res["filas_sha256"] = filas_sha
res["utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
with (Y / "sintesis/RESUMEN_EXP8.json").open("x", encoding="utf-8", newline="\n") as fh:
    fh.write(json.dumps(res, ensure_ascii=False, indent=1) + "\n")
man = {"kind": "manifiesto-sintesis-exp8-rem160", "utc": res["utc"], "candidato_para_revision": True,
       "derivado_de": {"area": str(T / "paso4_sintesis_exp8_desde_rem159"), "inventario_sha256": "d823217f731ed52179cb32fde6efefda3a4bda70f92412ec52e55737e715caa9",
                       "filas_sha256": "e2889c3f66b3c5dee16b13a42881a4ff5cab3a4e17c782c90267730e2a334d7c",
                       "resumen_sha256": "c64b5eb4118dd5475f143fe225dd4723260d041e8421cd5b936500ea2f8ae932",
                       "manifiesto_sha256": "72a737cea2b5fafd62d6b272b51506ea372f084aba08f5bb5387c34e42f1f463",
                       "constructor_sha256": "ed5c199b2071018a0145fdf8083dd779a79f952465af38374b410490dedc8ae8",
                       "nota": "referencia para la comprobación de invariancia; NO es autoridad científica: las fuentes siguen siendo los productos fijados por sus libros"},
       "campos_interpretativos_cambiados": {"filas": ["se_sabe", "no_se_concluye"], "resumen": ["kind", "utc", "filas_sha256"],
                                           "motivo": "hallazgos rem160 P4-EXP8-EPS-SIGNOS y P4-EXP8-NO-DECIDIDAS-N3"},
       "libros": {k: {"ruta": str(W / n), "sha256": h} for k, (n, h) in LIBROS.items()},
       "dictamenes_y_registros": {k: {"ruta": str(W / n), "sha256": h} for k, (n, h) in DICT.items()},
       "fuentes": F, "excepcion_integridad_ENF": {"area": libro["ENF"]["area"], "inventario_original_conforme": libro["ENF"]["original_inventory_conforme"],
                                                 "integridad_observada_sha256": libro["ENF"]["observed_integrity_sha256"],
                                                 "nota": "el producto ENF se autentica por su huella fijada en el libro rem148; la excepción rem147 (logs/sello.txt) se conserva"},
       "referencias_no_autoridad": {"MATRIZ_CANALES_LOCALES rem156": "solo con los límites ratificados por rem157/rem158/rem159",
                                    "FICHA_D_EXP8 rem148": "antecedente para el diferencial; no estado vigente", "N3_PROPUESTA rem148": "antecedente para el diferencial; no estado vigente"},
       "salidas": {"sintesis/EXP8_POR_AFIRMACION.jsonl": filas_sha, "sintesis/RESUMEN_EXP8.json": H((Y / "sintesis/RESUMEN_EXP8.json").read_bytes())},
       "construccion": {"script": "sintesis/construir_sintesis_rem160.py", "sha256": H(Path(__file__).read_bytes())}}
with (Y / "fuentes/MANIFIESTO_SINTESIS.json").open("x", encoding="utf-8", newline="\n") as fh:
    fh.write(json.dumps(man, ensure_ascii=False, indent=1) + "\n")
print(json.dumps({"filas": len(filas), "cotejos": res["cotejos_esperados_del_encargo"], "filas_sha256": filas_sha}, ensure_ascii=False))
raise SystemExit(0 if all(v for k, v in res["cotejos_esperados_del_encargo"].items() if k != "nota") else 3)
