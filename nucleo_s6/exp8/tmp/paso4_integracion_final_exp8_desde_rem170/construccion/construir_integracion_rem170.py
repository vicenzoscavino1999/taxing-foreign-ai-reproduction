"""rem170 — CONSTRUCTOR DOCUMENTAL de la integración final de Exp8 tras B1+B2 aceptados (PROD4.5.6).
Deriva una copia NUEVA de las 1.728 filas de la síntesis aceptada rem160 (S, inventario 3bcebf12…): integra en las doce afirmaciones COV del
libro complementario B2 (review_20261108_rem170_B2_COV12_aceptada.json, d53bbe82…) la clasificación transformada aceptada robust_infeasible
con su cota global B1+B2, conserva la lectura histórica no_decidida_por_testigos y deja intactas, byte a byte, las 1.716 filas ajenas.
No es cálculo científico: solo autentica, lee resultados aceptados, enlaza por claves completas, comprueba con aritmética racional exacta las
fracciones guardadas (U_C2 − L_K1 ≤ −1/100) y recuenta. No importa paper2b ni llama a C2, K1, macro.bridge, GridCell.Q, modelo, supremos,
techos, mallas, S6 ni búsquedas. Las rutas de campo que puede cambiar están declaradas antes en construccion/ESQUEMA_DECLARADO_REM170.json;
si una fila exigiera otra, se detiene con rc 3.
Escribe en exclusiva (destinos nuevos): <Y>/sintesis/EXP8_POR_AFIRMACION.jsonl, <Y>/sintesis/COV12_RESOLUCION_GLOBAL.jsonl,
<Y>/sintesis/RESUMEN_EXP8.json y <Y>/fuentes/MANIFIESTO_SINTESIS.json.
Uso: python -B -I -X utf8 construir_integracion_rem170.py <R> <Y>"""
import copy
import datetime as dt
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

R = Path(sys.argv[1])
Y = Path(sys.argv[2])
W = Path(r"@@W_BS1@@")
S = R / "tmp" / "paso4_correcciones_sintesis_exp8_desde_rem160"
X = R / "tmp" / "paso4_produccion_b2_doce_cov_desde_rem169"
B1A = R / "tmp" / "paso4_produccion_b1_doce_cov_desde_rem166"
P162 = R / "tmp" / "paso4_preparacion_precisa_doce_cov_desde_rem162"
H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
canon = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))  # noqa: E731
EPS = Fraction(1, 100)


class Bloqueo(Exception):
    pass


def exige(c, *motivo):
    if not c:
        raise Bloqueo(motivo)


# ---- autenticación ------------------------------------------------------------------------------------------------------------------------
AUT = {  # clave: (ruta, sha256)
    "dictamen_rem170": (W / "review_20261108_rem170_dictamen.txt", "b17fa026d53aa9e839b619d4dcb81de8d925712692e8c0fc47ef453b2c4cbd80"),
    "libro_B2": (W / "review_20261108_rem170_B2_COV12_aceptada.json", "d53bbe822a4df76f57e2826da6786914338dff15671a72d73521f2ee848c80cd"),
    "auditoria_rem170": (W / "review_20261108_rem170_audit_final.json", "aeda909d888709379dc90e4179afbd0f1704e8a3375f1221078e1d2b079b4026"),
    "enlace_rem170": (W / "review_20261108_rem170_claims_join.json", "232fb614d698b9ca5176d9d3b67bd6294485b94267e75a76974b03dd86574117"),
    "hallazgos_rem170": (W / "review_20261108_rem170_findings.json", "698f4af398f564b36f36e735f2b699a575e331d021e3eb566c4f664b62df5275"),
    "libro_B1": (W / "review_20261108_rem167_B1_aceptada.json", "649457712e6f3d33ca596021e5c4878782558579971c4f60a5048455cb1b4535"),
    "libro_sintesis_rem161": (W / "review_20261106_rem161_EXP8_sintesis_aceptada.json", "0d84eb80d10ad530f222ca4b38c5e5ef86be1fcf7afde604243012a3cdd7e707"),
    "libro_P7": (W / "review_20261105_rem155_P7_aceptado.json", "ae2c36e5d5c509b879eb9c423e7564e215ee1bf3d85617e4e3cf3039fca6d652"),
    "libro_Q_DIAG": (W / "review_20261106_rem156_Q_diagnostico.json", "7609b7bdfb0bc66305100d3b2967e7612e5430d36f1d653c54f25ba49d4f1301"),
    "S_inventario": (S / "audit/entrega.json", "3bcebf129042e5006519de16ca205d21cc07db8c5c6a189e4a5abd365cccc4de"),
    "S_informe": (S / "INFORME_REM160.md", "a1af9a13faf5e5144facb514fcb85f73f0bdcaaaec14f6b23fd94e20aeb5e2d9"),
    "S_filas": (S / "sintesis/EXP8_POR_AFIRMACION.jsonl", "816209e40007471265f0a06e529d1d30ed60ca80d445594ce43b57bbdede113f"),
    "S_resumen": (S / "sintesis/RESUMEN_EXP8.json", "1dc9d778b6dcaec13d5f19c8cf9fb8e447e15dc65a1752e13f912da892ea2751"),
    "S_manifiesto": (S / "fuentes/MANIFIESTO_SINTESIS.json", "9adbcc842ff82d8c8487f550a2d9da7eca354da2f8dc761f413e367c19b83389"),
    "S_constructor": (S / "sintesis/construir_sintesis_rem160.py", "e96814df3ae17c4c24463958b7839491ade01e5c1b3e1614cc510d6cbaf84966"),
    "X_inventario": (X / "audit/entrega.json", "b7354ee7d9956fd6e38d929ff471f5af6638339bc335de4592ea6bdc739058b5"),
    "X_informe": (X / "INFORME_REM169.md", "6c51b049d82ed5d20b1916171fdc8f253b8d30a901011c27185aba1d88dff40b"),
    "X_estado_b2": (X / "b2_B2PROD169/estado_b2.json", "a4ccbd1c87db5a9376c39817ee84d92bfc9c336a5fc7e872a2d7ea1998a3c40f"),
    "X_evidencia_b2": (X / "b2_B2PROD169/TRABAJO/EVIDENCIA_B2.json", "dfbe7e6cb7c1c2c97c408797ddb9634be9704ab91892fb3df349f2cc50b0f56d"),
    "X_plan_inicio": (X / "b2_B2PROD169/TRABAJO/PLAN_INICIO.json", "e0e1ff3f76eee7ad6f951790591efbba7037cd0990213a77b4d889308de4bf77"),
    "X_validacion_b2": (X / "b2_B2PROD169/VALIDACION/VALIDACION_B2.json", "aa30bc5b6e2e17bf346acb360be064b15511d24b764500b46b4a01990849366e"),
    "X_lectura_b2": (X / "b2_B2PROD169/VALIDACION/LECTURA_B2.json", "1fd0e1803a7fa4824b750f89a1a1e489232086e99a3469ba205abded28417638"),
    "B1_inventario": (B1A / "audit/entrega.json", "af7678fda72eca202a3fa0e369c35279f13cbc2241c84e702aadcbf4267b6f4c"),
    "B1_lectura": (B1A / "b1_B1PROD166/VALIDACION/LECTURA_B1.json", "ec3db4e494caeb413407157ae0027c39da5e49f712bf83468d63c5c7e35df960"),
    "soporte_rem162": (P162 / "soporte/CONTEXTO_COL_POR_GRUPO.json", "5821bb3dae7d4c4dc93e8e956da8984dfeec931587b16b8e7329231c8819d810"),
    "esquema_declarado": (Y / "construccion/ESQUEMA_DECLARADO_REM170.json", "f4e474457cf0e70135f02da7cb0333ec8be6f7334452969c9a1ffb7bb33dd443"),
}
BYTES, DOC = {}, {}
for k, (p, h) in AUT.items():
    b = p.read_bytes()
    exige(H(b) == h, "FUENTE_NO_AUTENTICA", k, str(p))
    BYTES[k] = b
    if p.suffix == ".json":
        DOC[k] = json.loads(b)
L2, L1 = DOC["libro_B2"], DOC["libro_B1"]
# los productos B2 que se citan son los que fija el libro B2; LECTURA_B1 es la que fija el libro B1
for k in ("X_estado_b2", "X_evidencia_b2", "X_plan_inicio", "X_validacion_b2", "X_lectura_b2"):
    exige(L2["products"].get(str(AUT[k][0])) == AUT[k][1], "PRODUCTO_B2_NO_FIJADO_POR_EL_LIBRO", k)
exige(L1["products"].get(str(AUT["B1_lectura"][0])) == AUT["B1_lectura"][1], "LECTURA_B1_NO_FIJADA_POR_EL_LIBRO_B1")
exige(L2["inventory_sha256"] == AUT["X_inventario"][1] and L1["inventory_sha256"] == AUT["B1_inventario"][1], "INVENTARIOS_DE_LIBROS")
exige(L2["old_synthesis_sha256"] == AUT["S_filas"][1] and DOC["enlace_rem170"]["synthesis_sha256"] == AUT["S_filas"][1], "SINTESIS_BASE_DISTINTA")
exige(DOC["libro_sintesis_rem161"]["inventory_sha256"] == AUT["S_inventario"][1], "S_NO_ES_LA_SINTESIS_ACEPTADA")
exige(L2["B1_accepted_ledger_sha256"] == AUT["libro_B1"][1] and L2["review_sha256"] == AUT["dictamen_rem170"][1]
      and L2["audit_sha256"] == AUT["auditoria_rem170"][1] and L2["claims_join_sha256"] == AUT["enlace_rem170"][1], "LIBRO_B2_ENLACES")
exige(L2["accepted"] is True and L2["transformed_classification_accepted"] is True and L2["accepted_verdict_under_COV"] == "robust_infeasible", "LIBRO_B2_NO_ACEPTA")
exige(L2["formal_closures"] == [] and L2["D_EXP8_adopted"] is False and L2["N3_adopted"] is False, "LIBRO_B2_CIERRES")
ESQ = DOC["esquema_declarado"]

# ---- base S ---------------------------------------------------------------------------------------------------------------------------------
lineas = BYTES["S_filas"].splitlines(keepends=True)
exige(len(lineas) == 1728 and all(x.endswith(b"\n") for x in lineas), "S_FILAS_NO_SON_1728")
S_FILAS = [json.loads(x) for x in lineas]
for x, f in zip(lineas, S_FILAS):
    exige(json.dumps(f, ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\n" == x, "S_FILA_NO_REPRODUCIBLE", f.get("afirmacion"))
POS = {}
for i, f in enumerate(S_FILAS):
    exige(f["afirmacion"] not in POS, "S_CLAVE_DUPLICADA", f["afirmacion"])
    POS[f["afirmacion"]] = i

# ---- las doce, por clave completa del libro ---------------------------------------------------------------------------------------------------
GRUPOS = {g["group"]: g for g in L2["groups"]}
exige(len(L2["claims"]) == 12 and len(GRUPOS) == 6 and L2["claims_count"] == 12 and L2["groups_count"] == 6, "LIBRO_B2_RECUENTOS")
evid_ag = DOC["X_evidencia_b2"]["b1"]["afirmacion_grupo"]
sop = DOC["soporte_rem162"]
lect = {g["grupo"]: g for g in DOC["X_lectura_b2"]["lectura"]["grupos"]}
DOCE = {}
for c in L2["claims"]:
    a = c["afirmacion"]
    exige(a not in DOCE, "LIBRO_B2_CLAVE_DUPLICADA", a)
    exige(sum(1 for f in S_FILAS if f["afirmacion"] == a) == 1, "SIN_COINCIDENCIA_UNICA_EN_S", a)
    g = c["grupo"]
    exige([k for k, v in GRUPOS.items() if a in v["claims"]] == [g], "GRUPO_NO_UNICO", a)
    exige(evid_ag.get(a) == g and a in sop["por_grupo_X"][g]["afirmaciones"], "GRUPO_DISTINTO_EN_EVIDENCIA_O_SOPORTE", a)
    exige(POS[a] + 1 == c["source_synthesis_line"], "LINEA_DE_S_DISTINTA", a)
    f = S_FILAS[POS[a]]
    exige(f["conjunto_padre"] == "inconclusa" and f["categoria_original"] == c["parent_category"], "CATEGORIA_PADRE_DISTINTA", a)
    exige(f["COV"]["conclusion"] == "no_decidida_por_testigos" == c["historical_COV_conclusion"] == f["COV"]["conclusion_historica"], "NO_ERA_DESCONOCIDA", a)
    exige(c["accepted_COV_verdict"] == "robust_infeasible" and c["eps"] == "1/100" and c["scenario"] == "ABL-COV phi/2", "VEREDICTO_O_ESCENARIO", a)
    exige(f["COV"]["escenario"] == "ABL-COV phi/2 (coverage_half), resto fijo", "ESCENARIO_DE_FILA", a)
    DOCE[a] = c
desconocidas_S = {f["afirmacion"] for f in S_FILAS if f["conjunto_padre"] == "inconclusa" and f["COV"]["conclusion"] == "no_decidida_por_testigos"}
exige(set(DOCE) == desconocidas_S and len(DOCE) == 12, "LAS_DOCE_NO_SON_LAS_DESCONOCIDAS_HISTORICAS")
exige(set(evid_ag) == set(DOCE), "EVIDENCIA_B2_OTRAS_AFIRMACIONES")

# ---- aritmética exacta de las cotas guardadas ---------------------------------------------------------------------------------------------
U_hex = L2["U_C2_hex"]
U = Fraction(float.fromhex(U_hex))
exige(U == Fraction(L2["U_C2_exact"]) == Fraction(L2["U_C2"]) == Fraction(L1["U_C2_exact"]) == Fraction(L1["U_C2"]) and L1["U_C2_hex"] == U_hex, "U_C2_INCOHERENTE")
exige(Fraction(DOC["X_lectura_b2"]["datos_validados"]["U_C2"]) == U, "U_C2_LECTURA_B2")
ARIT = {}
for g, gr in sorted(GRUPOS.items()):
    L = Fraction(float.fromhex(gr["L_K1_hex"]))
    exige(L == Fraction(gr["L_K1"]), "L_K1_HEX_FLOAT", g)
    exige(lect[g]["L_K1_hex"] == gr["L_K1_hex"] and DOC["X_lectura_b2"]["datos_validados"]["grupos"][g]["L_K1_hex"] == gr["L_K1_hex"], "L_K1_LECTURA_B2", g)
    exige(DOC["X_lectura_b2"]["datos_validados"]["grupos"][g]["pendientes"] == 0, "CONTEXTOS_PENDIENTES", g)
    G = U - L
    exige(G == Fraction(gr["G_hi_exact"]), "G_HI_NO_ES_U_MENOS_L", g)
    exige(G <= -EPS, "G_HI_NO_CUMPLE_EPS", g)
    m = -EPS - G
    exige(m == Fraction(gr["margin_below_minus_eps_exact"]) and m >= 0, "MARGEN", g)
    exige(gr["contexts"] == sop["por_grupo_X"][g]["contextos_K1_efectivos"] == DOC["X_lectura_b2"]["datos_validados"]["grupos"][g]["contextos"], "CONTEXTOS_GRUPO", g)
    exige(gr["accepted_transformed_verdict"] == "robust_infeasible" and gr["parent_verdict_unchanged"] is True, "VEREDICTO_GRUPO", g)
    ARIT[g] = {"L": L, "G": G, "m": m}
union = DOC["X_lectura_b2"]["datos_validados"]["contextos_acotados"]
exige(union == sop["resumen"]["contextos_K1_efectivos_union"] == 1920 and DOC["X_lectura_b2"]["datos_validados"]["contextos_pendientes"] == 0, "UNION_1920")
exige(sum(g["contexts"] for g in GRUPOS.values()) == 2304 and sop["resumen"]["suma_doce_antes_dedup"] == 4608, "TAMANOS_2304_4608")
exige(sop["resumen"]["inclusiones_de_grupo_por_claves"] == {"K5": ["K1", "K3"], "K6": ["K2", "K4"]}, "INCLUSIONES")
POR_AF_SOP = {p["afirmacion"]: p for p in sop["por_afirmacion"]}


def fx(q):
    return "%d/%d" % (q.numerator, q.denominator)


FRASE_NO_ANTERIOR = "clasificación de la afirmación bajo phi/2: no están demostradas ni la preservación de la inconclusión ni la robustez"


def resolucion(a, f):
    c = DOCE[a]
    g = c["grupo"]
    gr = GRUPOS[g]
    ar = ARIT[g]
    ps = POR_AF_SOP[a]
    i_sabe = [i for i, s in enumerate(f["se_sabe"]) if s.startswith("COV phi/2:")]
    j_no = [j for j, s in enumerate(f["no_se_concluye"]) if s == FRASE_NO_ANTERIOR]
    exige(len(i_sabe) == 1 and len(j_no) == 1, "FRASES_COV_NO_UNICAS", a)
    return {
        "estado": "vigente",
        "veredicto": "robust_infeasible",
        "escenario": "ABL-COV phi/2 (coverage_half), resto fijo",
        "nivel_de_evidencia": "cota_global",
        "grupo": g,
        "afirmaciones_del_grupo": list(gr["claims"]),
        "eps": "1/100",
        "regla": "G <= U_C2 - L_K1 <= -eps, borde incluido; coincide con la clasificación infeasible de cobertura.classify",
        "U_C2": {"float": L2["U_C2"], "hex": U_hex, "exacto": L2["U_C2_exact"], "fuente": "B1 (libro rem167)",
                 "naturaleza": "encierro superior certificado sobre la raíz fija; no es máximo puntual ni argmax"},
        "L_K1": {"float": gr["L_K1"], "hex": gr["L_K1_hex"], "exacto": fx(ar["L"]), "fuente": "B2 (libro rem170)",
                 "naturaleza": "cota inferior global de K1 sobre los contextos del grupo"},
        "G_hi": {"exacto": gr["G_hi_exact"], "float": gr["G_hi"]},
        "margen_bajo_menos_eps": {"exacto": gr["margin_below_minus_eps_exact"], "float": gr["margin"]},
        "soporte": {"contextos_del_grupo": gr["contexts"], "ediciones": ps["ediciones"], "contextos_antes_dedup_de_la_afirmacion": ps["contextos_antes_dedup"],
                    "union_efectiva_seis_grupos": union, "suma_tamanos_grupo": 2304, "contextos_antes_dedup_doce": 4608,
                    "inclusiones": "K5 ⊂ K1∩K3; K6 ⊂ K2∩K4", "fuente": "soporte rem162 CONTEXTO_COL_POR_GRUPO.json (5821bb3d…), LECTURA_B2 (1fd0e180…)",
                    "nota": "soporte contractual de la cota global; 2024p pertenece al soporte E2 de esta cota y no convierte COL-2024p en celdas testigo COORD/ENF/COV, cuya exclusión de alcance se mantiene"},
        "prueba": "Para todo estado del soporte transformado del grupo, C2 <= U_C2 (B1) y K1 >= L_K1 (B2); por tanto G = C2 - K1 <= U_C2 - L_K1 = G_hi <= -1/100.",
        "no_requiere": ["que ambos extremos se alcancen simultáneamente", "un argmax ni un testigo de máximo"],
        "procedencia": {
            "B1": {"libro": "review_20261108_rem167_B1_aceptada.json", "sha256": AUT["libro_B1"][1], "entrega_inventario": AUT["B1_inventario"][1],
                   "lectura": "b1_B1PROD166/VALIDACION/LECTURA_B1.json", "lectura_sha256": AUT["B1_lectura"][1]},
            "B2": {"libro": "review_20261108_rem170_B2_COV12_aceptada.json", "sha256": AUT["libro_B2"][1], "libro_numero": 20,
                   "entrega_inventario": AUT["X_inventario"][1], "evidencia_sha256": AUT["X_evidencia_b2"][1],
                   "validacion_sha256": AUT["X_validacion_b2"][1], "lectura_sha256": AUT["X_lectura_b2"][1]},
            "dictamen": {"archivo": "review_20261108_rem170_dictamen.txt", "sha256": AUT["dictamen_rem170"][1]},
            "auditoria": {"archivo": "review_20261108_rem170_audit_final.json", "sha256": AUT["auditoria_rem170"][1], "comprobaciones": "63/63"},
            "enlace": {"archivo": "review_20261108_rem170_claims_join.json", "sha256": AUT["enlace_rem170"][1], "comprobaciones": "8/8"},
            "sintesis_rem160": {"filas_sha256": AUT["S_filas"][1], "linea": POS[a] + 1}},
        "lectura_anterior": {"conclusion": f["COV"]["conclusion"], "se_sabe_rem160": f["se_sabe"][i_sabe[0]], "no_se_concluye_rem160": FRASE_NO_ANTERIOR,
                             "estado": "histórica; superada como estado vigente por la resolución global aceptada en el dictamen rem170",
                             "testigos": "COV.lados y COV.fuente de esta fila (intactos)"},
        "limites": ["robustez dentro del modelo y del soporte contractual declarado", "no es inviabilidad económica empírica",
                    "no prueba causalidad institucional ni identifica un canal dominante", "no ordena canales ni países", "no es una política óptima",
                    "seis grupos G/N con soportes solapados: no son doce observaciones independientes"]}


def frase_sabe(rg):
    return ("COV phi/2 (vigente, B1+B2 aceptados en el dictamen rem170): robust_infeasible dentro del modelo y del soporte contractual del grupo %s "
            "(%d contextos), por cota global: en todo estado del soporte transformado C2 ≤ U_C2 (B1) y K1 ≥ L_K1 (B2), luego G ≤ U_C2 − L_K1 = %s ≤ −ε "
            "(ε=1/100, borde incluido); la prueba no exige que ambos extremos se alcancen a la vez ni un argmax. Histórico (rem152/rem160): con los "
            "testigos guardados la clasificación quedaba no_decidida_por_testigos (el testigo sup dejó de satisfacer G>−ε y el inf satisface G<+ε); "
            "ese cambio de signo del testigo se conserva como evidencia histórica y no es la prueba de la clasificación vigente"
            % (rg["grupo"], rg["soporte"]["contextos_del_grupo"], rg["G_hi"]["exacto"]))


NO_NUEVA = "clasificación bajo phi/2 fuera del modelo y del soporte contractual del grupo; la robustez infactible vigente no es inviabilidad económica empírica"
NO_AÑADIDA = "independencia entre afirmaciones: forman seis pares G/N con soportes solapados, no doce observaciones independientes"

# ---- filas nuevas -------------------------------------------------------------------------------------------------------------------------------
NUEVAS, SALIDA, SUPL = [], [], []
for i, f in enumerate(S_FILAS):
    a = f["afirmacion"]
    if a not in DOCE:
        NUEVAS.append(f)
        SALIDA.append(lineas[i])
        continue
    n = copy.deepcopy(f)
    rg = resolucion(a, f)
    n["COV"]["conclusion"] = "robust_infeasible"
    n["COV"]["resolucion_global"] = rg
    n["se_sabe"] = [frase_sabe(rg) if s.startswith("COV phi/2:") else s for s in f["se_sabe"]]
    n["no_se_concluye"] = [NO_NUEVA if s == FRASE_NO_ANTERIOR else s for s in f["no_se_concluye"]] + [NO_AÑADIDA]
    # comprobación de rutas declaradas
    for k in f:
        if k not in ("COV", "se_sabe", "no_se_concluye"):
            exige(canon(n[k]) == canon(f[k]), "RUTA_NO_DECLARADA", a, k)
    exige(set(n["COV"]) == set(f["COV"]) | {"resolucion_global"}, "CLAVES_COV", a)
    for k in f["COV"]:
        if k != "conclusion":
            exige(canon(n["COV"][k]) == canon(f["COV"][k]), "RUTA_COV_NO_DECLARADA", a, k)
    NUEVAS.append(n)
    b = json.dumps(n, ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\n"
    SALIDA.append(b)
    SUPL.append({"afirmacion": a, "grupo": rg["grupo"], "linea_sintesis_rem170": i + 1, "linea_sintesis_rem160": i + 1,
                 "fila_rem170_canon_sha256": H(canon(n).encode("utf-8")), "fila_rem160_linea_sha256": H(lineas[i]),
                 "categoria_original": f["categoria_original"], "conjunto_padre": f["conjunto_padre"],
                 "conclusion_COV_historica": f["COV"]["conclusion_historica"], "conclusion_COV_vigente": "robust_infeasible",
                 "entrada_libro_B2": DOCE[a], "libro_B2": {"archivo": "review_20261108_rem170_B2_COV12_aceptada.json", "sha256": AUT["libro_B2"][1]},
                 "resolucion_global": rg})
exige(len(SUPL) == 12 and len(NUEVAS) == 1728, "RECUENTO_SALIDA")

# ---- RESUMEN (derivado de las filas nuevas; misma lógica que rem160) ---------------------------------------------------------------------
filas = NUEVAS
cnt = lambda it: dict(sorted(Counter(it).items(), key=lambda kv: str(kv[0])))  # noqa: E731
res = {"kind": "resumen-exp8-rem170", "candidato_para_revision": True, "produccion": False, "afirmaciones": len(filas),
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
mg = DOC["libro_Q_DIAG"]["margins"]
res["Q"]["diagnostico_general"] = {"libro": "review_20261106_rem156_Q_diagnostico.json", "dominio": DOC["libro_Q_DIAG"]["domain"],
                                   "m_estrella_contrato": {"exacto": mg["contrato"]["max_inf_threshold"], "aprox": mg["contrato"]["max_inf_threshold_float"]},
                                   "m_estrella_conservadora": {"exacto": mg["conservadora"]["max_inf_threshold"], "aprox": mg["conservadora"]["max_inf_threshold_float"]}}
res["posiciones_Q"] = {"total": sum(2 for f in filas), "por_origen": cnt(f["Q"]["versiones"]["contrato"]["posiciones"][l]["origen"] for f in filas for l in ("sup", "inf")),
                       "nota": "3.456 posiciones Q no son 3.456 afirmaciones ni celdas distintas"}
celdas_base = {f["padre"][l]["unidad"] for f in filas for l in ("sup", "inf") if f["padre"][l]["origen"] == "filas_padre_aceptadas"}
res["celdas"] = {"unidades_padre_base_distintas": len(celdas_base), "unidades_P7": sorted({f["P7"]["unidad"] for f in filas if f["P7"]}),
                 "afirmaciones_con_P7": sum(1 for f in filas if f["P7"]), "afirmaciones_sin_P7": sum(1 for f in filas if not f["P7"]),
                 "nota": "las cuatro unidades P7 siguen separadas del censo base; COL-2024p queda fuera de este nivel (exclusión de alcance)"}
FA = {f["afirmacion"]: f for f in filas}
sc = [(f["afirmacion"], l, f["COV"]["lados"][l]) for f in filas for l in (f["COV"]["cambio_de_signo_certificado"] or [])]
res["COV_cambios_de_signo_certificados"] = {
    "ocurrencias": len(sc), "afirmaciones": len({x[0] for x in sc}), "celdas": len({x[2]["cell_id"] for x in sc}), "claves": sorted({x[2]["clave_cov"] for x in sc}),
    "direcciones": cnt("%s->%s" % (x[2]["signo_padre"], x[2]["signo_cov_certificado"]) for x in sc), "lados": cnt(x[1] for x in sc),
    "por_categoria_original": cnt(FA[x[0]]["categoria_original"] for x in sc), "conclusion_COV": cnt(FA[x[0]]["COV"]["conclusion"] for x in sc),
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
                 "ENF_no_alcanzadas_preservadas_rem155": DOC["libro_P7"].get("nonattained_ENF_claims_preserved"),
                 "COV_robust_infeasible_desde_inconclusas": sorted(f["afirmacion"] for f in filas if f["conjunto_padre"] == "inconclusa" and f["COV"]["conclusion"] == "robust_infeasible"),
                 "COV_no_decididas_robustas_padre": sorted(f["afirmacion"] for f in filas if f["conjunto_padre"] == "robusta" and f["COV"]["conclusion"] == "no_decidida_por_testigos")}
res["COV_resolucion_global"] = {
    "afirmaciones": sum(1 for f in filas if "resolucion_global" in f["COV"]),
    "grupos": cnt(f["COV"]["resolucion_global"]["grupo"] for f in filas if "resolucion_global" in f["COV"]),
    "veredicto": cnt(f["COV"]["resolucion_global"]["veredicto"] for f in filas if "resolucion_global" in f["COV"]),
    "por_grupo": {g: {"contextos": gr["contexts"], "L_K1_hex": gr["L_K1_hex"], "G_hi_exacto": gr["G_hi_exact"],
                      "afirmaciones": sorted(f["afirmacion"] for f in filas if "resolucion_global" in f["COV"] and f["COV"]["resolucion_global"]["grupo"] == g)}
                  for g, gr in sorted(GRUPOS.items())},
    "U_C2_hex": U_hex, "U_C2_exacto": L2["U_C2_exact"], "eps": "1/100",
    "contextos": {"suma_tamanos_grupo": sum(g["contexts"] for g in GRUPOS.values()), "union_efectiva": union, "antes_dedup_doce": 4608,
                  "inclusiones": {"K5": ["K1", "K3"], "K6": ["K2", "K4"]}},
    "libro": "review_20261108_rem170_B2_COV12_aceptada.json", "libro_sha256": AUT["libro_B2"][1],
    "nota": "doce afirmaciones en seis grupos G/N con soportes solapados; no son doce observaciones independientes; la prueba es la cota global B1+B2, no el cambio de signo de los testigos"}
res["derivado_de"] = {"area": str(S), "inventario_sha256": AUT["S_inventario"][1], "resumen_sha256": AUT["S_resumen"][1], "filas_sha256": AUT["S_filas"][1],
                      "nota": "fuente histórica de la base; las claves no declaradas en el esquema son idénticas a las del resumen rem160"}
cp = res["COV"]["final_por_conjunto_padre"]
res["cotejos_esperados_del_encargo"] = {
    "padre_1712_inconclusas_16_robustas": res["conjunto_padre"] == {"inconclusa": 1712, "robusta": 16},
    "categorias_1524_188_16": res["categoria_original"] == {"cambio_de_signo_certificado": 1524, "inconclusa_por_testigos_en_tolerancia": 188, "robusta_infactible_certificada": 16},
    "ENF_1712_preservadas_16_no_decididas": sorted(res["ENF"]["final_con_P7"].values()) == [16, 1712] and res["ENF"]["final_con_P7"].get("inconclusa_preservada") == 1712
    and res["ENF"]["final_por_conjunto_padre"]["inconclusa"] == {"inconclusa_preservada": 1712},
    "COV_1700_preservadas_12_robust_infeasible_16_no_decididas": res["COV"]["final_con_P7"] == {"inconclusa_preservada": 1700, "no_decidida_por_testigos": 16, "robust_infeasible": 12}
    and cp["inconclusa"] == {"inconclusa_preservada": 1700, "robust_infeasible": 12} and cp["robusta"] == {"no_decidida_por_testigos": 16},
    "COV_historico_sin_cambios": res["COV"]["historico_sin_P7"] == DOC["S_resumen"]["COV"]["historico_sin_P7"],
    "Q_1712_preservadas_16_refutadas_ambas_versiones": all(res["Q"][v]["canal"] == {"inconclusa_preservada": 1712, "robustez_refutada_por_testigo_sup": 16} for v in ("contrato", "conservadora"))
    and res["Q"]["veredictos_distintos_entre_versiones"] == 0,
    "COV_20_cambios_de_signo_8_preservadas_12_resueltas": res["COV_cambios_de_signo_certificados"]["ocurrencias"] == 20 and len(res["COV_cambios_de_signo_certificados"]["claves"]) == 2
    and res["COV_cambios_de_signo_certificados"]["conclusion_COV"] == {"inconclusa_preservada": 8, "robust_infeasible": 12},
    "P7_siete_una_vez_cuatro_unidades": res["celdas"]["afirmaciones_con_P7"] == 7 and len(res["celdas"]["unidades_P7"]) == 4 and res["ENF"]["suplemento_P7_aplicado"] == 7 and res["COV"]["suplemento_P7_aplicado"] == 7,
    "posiciones_3456_3449_7": res["posiciones_Q"]["total"] == 3456 and res["posiciones_Q"]["por_origen"] == {"filas_padre_aceptadas": 3449, "suplemento_P7_lado_padre_faltante": 7},
    "ENF_descompuestas_1705": res["ENF_descomposicion_rem108"]["descompuestas_true"] == 1705,
    "doce_en_seis_grupos_2304_1920_4608": res["COV_resolucion_global"]["afirmaciones"] == 12 and len(res["COV_resolucion_global"]["grupos"]) == 6
    and res["COV_resolucion_global"]["contextos"]["suma_tamanos_grupo"] == 2304 and res["COV_resolucion_global"]["contextos"]["union_efectiva"] == 1920,
    "nota": "valores comparados con los recuentos DERIVADOS de las filas; no se escriben en las filas"}
# claves del resumen fuera del esquema declarado: idénticas a S
CAMBIAN = {"kind", "utc", "filas_sha256", "COV", "COV_cambios_de_signo_certificados", "por_dimension", "por_pais_y_bloque", "listas", "cotejos_esperados_del_encargo"}
NUEVAS_CLAVES = {"COV_resolucion_global", "derivado_de"}
canon_json = lambda o: canon(json.loads(json.dumps(o, ensure_ascii=False)))  # noqa: E731  (intento 2: claves None -> "null" como en el archivo)
for k in DOC["S_resumen"]:
    if k not in CAMBIAN:
        exige(canon_json(res[k]) == canon(DOC["S_resumen"][k]), "RESUMEN_CLAVE_NO_DECLARADA_CAMBIA", k)
exige(set(res) | {"utc", "filas_sha256"} == set(DOC["S_resumen"]) | NUEVAS_CLAVES, "RESUMEN_CLAVES")

# ---- salidas -------------------------------------------------------------------------------------------------------------------------------------
(Y / "fuentes").mkdir(exist_ok=True)
(Y / "sintesis").mkdir(exist_ok=True)
with (Y / "sintesis/EXP8_POR_AFIRMACION.jsonl").open("xb") as fh:
    for b in SALIDA:
        fh.write(b)
filas_sha = H((Y / "sintesis/EXP8_POR_AFIRMACION.jsonl").read_bytes())
for s in SUPL:
    s["sintesis_rem170_filas_sha256"] = filas_sha
with (Y / "sintesis/COV12_RESOLUCION_GLOBAL.jsonl").open("x", encoding="utf-8", newline="\n") as fh:
    for s in SUPL:
        fh.write(json.dumps(s, ensure_ascii=False, sort_keys=True) + "\n")
res["filas_sha256"] = filas_sha
res["utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
with (Y / "sintesis/RESUMEN_EXP8.json").open("x", encoding="utf-8", newline="\n") as fh:
    fh.write(json.dumps(res, ensure_ascii=False, indent=1) + "\n")
MS = DOC["S_manifiesto"]
man = {"kind": "manifiesto-sintesis-exp8-rem170", "utc": res["utc"], "candidato_para_revision": True,
       "naturaleza": "INTEGRACION DOCUMENTAL EXP8 B1+B2 ACEPTADOS, SIN CALCULO CIENTIFICO NUEVO NI ALCANCE PRODUCTIVO",
       "fuente_historica": {"area": str(S), "inventario_sha256": AUT["S_inventario"][1], "filas_sha256": AUT["S_filas"][1], "resumen_sha256": AUT["S_resumen"][1],
                            "manifiesto_sha256": AUT["S_manifiesto"][1], "constructor_sha256": AUT["S_constructor"][1], "informe_sha256": AUT["S_informe"][1],
                            "libro_de_aceptacion": {"archivo": "review_20261106_rem161_EXP8_sintesis_aceptada.json", "sha256": AUT["libro_sintesis_rem161"][1]},
                            "uso": "base de las 1.728 filas: 1.716 ajenas copiadas byte a byte y, en las doce, todos los campos padre, ENF, Q, P7 y la evidencia COV histórica; NO es la autoridad de la clasificación transformada de las doce"},
       "autoridad_de_actualizacion": {
           "dictamen_rem170": {"ruta": str(AUT["dictamen_rem170"][0]), "sha256": AUT["dictamen_rem170"][1]},
           "libro_B2_COV12": {"ruta": str(AUT["libro_B2"][0]), "sha256": AUT["libro_B2"][1], "numero": 20},
           "libro_B1": {"ruta": str(AUT["libro_B1"][0]), "sha256": AUT["libro_B1"][1]},
           "auditoria_rem170": {"ruta": str(AUT["auditoria_rem170"][0]), "sha256": AUT["auditoria_rem170"][1]},
           "enlace_rem170": {"ruta": str(AUT["enlace_rem170"][0]), "sha256": AUT["enlace_rem170"][1]},
           "hallazgos_rem170": {"ruta": str(AUT["hallazgos_rem170"][0]), "sha256": AUT["hallazgos_rem170"][1]},
           "productos_B2": {k: {"ruta": str(AUT[k][0]), "sha256": AUT[k][1], "fijado_por": "libro_B2.products"}
                            for k in ("X_estado_b2", "X_evidencia_b2", "X_plan_inicio", "X_validacion_b2", "X_lectura_b2")},
           "entrega_B2_inventario": {"ruta": str(AUT["X_inventario"][0]), "sha256": AUT["X_inventario"][1]},
           "informe_rem169": {"ruta": str(AUT["X_informe"][0]), "sha256": AUT["X_informe"][1]},
           "lectura_B1": {"ruta": str(AUT["B1_lectura"][0]), "sha256": AUT["B1_lectura"][1], "fijado_por": "libro_B1.products"},
           "entrega_B1_inventario": {"ruta": str(AUT["B1_inventario"][0]), "sha256": AUT["B1_inventario"][1]},
           "soporte_rem162": {"ruta": str(AUT["soporte_rem162"][0]), "sha256": AUT["soporte_rem162"][1], "fijado_por": "auditoría rem170 source_hashes"},
           "uso": "autoridad única de la clasificación vigente robust_infeasible de las doce y de su cota global"},
       "referencias_de_la_base": {"libros": MS["libros"], "dictamenes_y_registros": MS["dictamenes_y_registros"], "fuentes": MS["fuentes"],
                                  "excepcion_integridad_ENF": MS["excepcion_integridad_ENF"], "referencias_no_autoridad": MS["referencias_no_autoridad"],
                                  "nota": "copiados sin cambios del manifiesto rem160: procedencia de los campos de la base"},
       "esquema_declarado": {"ruta": "construccion/ESQUEMA_DECLARADO_REM170.json", "sha256": AUT["esquema_declarado"][1]},
       "campos_cambiados": {"filas_doce": ["COV.conclusion", "COV.resolucion_global (nueva)", "se_sabe[elemento «COV phi/2:»]",
                                           "no_se_concluye[elemento de la clasificación bajo phi/2]", "no_se_concluye (+1 elemento al final)"],
                            "filas_ajenas": "ninguno: 1.716 líneas idénticas byte a byte",
                            "resumen": sorted(CAMBIAN), "resumen_nuevas": sorted(NUEVAS_CLAVES)},
       "salidas": {"sintesis/EXP8_POR_AFIRMACION.jsonl": filas_sha,
                   "sintesis/COV12_RESOLUCION_GLOBAL.jsonl": H((Y / "sintesis/COV12_RESOLUCION_GLOBAL.jsonl").read_bytes()),
                   "sintesis/RESUMEN_EXP8.json": H((Y / "sintesis/RESUMEN_EXP8.json").read_bytes())},
       "construccion": {"script": "construccion/construir_integracion_rem170.py", "sha256": H(Path(__file__).read_bytes())}}
with (Y / "fuentes/MANIFIESTO_SINTESIS.json").open("x", encoding="utf-8", newline="\n") as fh:
    fh.write(json.dumps(man, ensure_ascii=False, indent=1) + "\n")
coj = res["cotejos_esperados_del_encargo"]
print(json.dumps({"filas": len(filas), "suplemento": len(SUPL), "cotejos": coj, "salidas": man["salidas"]}, ensure_ascii=False))
raise SystemExit(0 if all(v for k, v in coj.items() if k != "nota") else 3)
