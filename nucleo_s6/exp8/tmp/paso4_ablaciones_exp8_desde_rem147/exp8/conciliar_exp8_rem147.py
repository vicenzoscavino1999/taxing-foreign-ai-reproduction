"""rem147 — BLOQUE A: CONCILIACIÓN Exp8 × ENF POR AFIRMACIÓN (solo lectura de fuentes autenticadas en fuentes/AUTENTICACION_FUENTES_REM147.json;
aritmética sobre resultados almacenados; sin evaluar el modelo, sin techos, mallas, bridge, quiebres ni Q).
- Universo: T7_anexo rem108 (1.728 afirmaciones: 1.524 cambio_de_signo_certificado, 188 inconclusa_por_testigos_en_tolerancia, 16
  robusta_infactible_certificada). Inconclusas = 1.712; EXP8_TABLA rem108: 1.705 descompuestas + 7 sin descomposición (4 testigos sin filas).
- Enlace testigo → ENF SOLO por igualdad exacta (unidad, cell_id) con integ_conciliacion_ENF_INTEGRAL/brechas_celdas.jsonl (rem131, ledger rem132);
  cell_id de EXP8_TABLA (sup_cell_id/inf_cell_id) o, para las 16 robustas, de la fila padre autenticada por filas_sha256. Se exige además
  G_padre(ENF) == G del testigo en T7 (mismo float) y que la unidad sea la del T7.
- Canal eta_f a nivel de afirmación (umbral económico §17.1, eps = 0,01; tolerancia de certificado T7 = 1e-4): con el testigo sup enlazado,
  sup_Omega G_enf >= G_enf(testigo sup); con el inf enlazado, inf_Omega G_enf <= G_enf(testigo inf). Solo se declara lo que esas cotas demuestran:
  «inconclusa preservada» (G_enf(sup) > -eps + tol y G_enf(inf) < eps - tol), «no robusta infactible» / «no robusta factible» con un testigo,
  «robustez refutada» en las 16; el resto queda «no decidido por testigos» (exigiría el supremo/ínfimo ENF sobre todo el soporte, no disponible).
  No es causalidad ni ablación del eslabón dominante; la descomposición rem108 es una identidad entre testigos distintos, no un contraste.
Escribe en exclusiva, dentro de <dir_salida>: ENF_POR_AFIRMACION.jsonl, COBERTURA_EXP8.json, COBERTURA_EXP8.md, RESUMEN_POR_PAIS.json.
Uso: python -B -I -X utf8 conciliar_exp8_rem147.py <raiz> <autenticacion.json> <dir_salida>"""
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

R, AUT, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
T = R / "tmp"
H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
EPS, TOL = 0.01, 1e-4
aut = json.loads(AUT.read_bytes())
assert aut["conforme"]


def fuente(area, rel_):
    """Lee una fuente y exige el sha256 autenticado en A1."""
    e = aut["areas"][area]["archivos"][rel_]
    b = (T / area / rel_).read_bytes()
    assert H(b) == e["sha256"] and e["conforme"], rel_
    return b


jl = lambda b: [json.loads(x) for x in b.decode("utf-8").splitlines() if x.strip()]  # noqa: E731
A108, A131 = "paso4_conciliacion_portabilidad_desde_rem108", "paso4_integracion_final_enf_desde_rem131"
t7 = json.loads(fuente(A108, "conciliacion/ensamblajes/T7_anexo.json"))["filas"]
ex = json.loads(fuente(A108, "conciliacion/EXP8_TABLA.json"))
br = jl(fuente(A131, "integ_conciliacion_ENF_INTEGRAL/brechas_celdas.jsonl"))
rs = jl(fuente(A131, "integ_ensamblado_ENF_INTEGRAL/enf_brechas_resueltas.jsonl"))
ti = jl(fuente(A131, "integ_ensamblado_ENF_INTEGRAL/enf_techos_integrados.jsonl"))
tp = jl(fuente(A131, "integ_conciliacion_ENF_INTEGRAL/techos_pares.jsonl"))
fallos = []

# ---------------------------------------------------------------- recuentos del universo
cat = Counter(f["categoria_original"] for f in t7)
afs = [f["afirmacion"] for f in t7]
exf = {f["afirmacion"]: f for f in ex["filas"]}
sind = {c["afirmacion"]: c for c in ex["resumen"]["casos_sin_descomposicion"]}
INC = ("cambio_de_signo_certificado", "inconclusa_por_testigos_en_tolerancia")
inconclusas = [f for f in t7 if f["categoria_original"] in INC]
desc = [a for a, f in exf.items() if not f.get("motivo_sin_descomposicion")]
recuentos = {"universo_T7": len(t7), "afirmaciones_unicas": len(set(afs)), "por_categoria": dict(cat), "inconclusas": len(inconclusas),
             "filas_EXP8": len(exf), "descompuestas": len(desc), "sin_descomposicion": len(sind),
             "testigos_sin_filas": {"sup": sum(f["sup_estado_evidencia"] != "filas aceptadas" for f in t7),
                                    "inf": sum(f["inf_estado_evidencia"] != "filas aceptadas" for f in t7)},
             "resumen_EXP8_declarado": {k: ex["resumen"][k] for k in ("inconclusas", "descompuestas", "sin_descomposicion")}}
esper = {"universo_T7": 1728, "afirmaciones_unicas": 1728, "inconclusas": 1712, "descompuestas": 1705, "sin_descomposicion": 7}
for k, v in esper.items():
    if recuentos[k] != v:
        fallos.append("RECUENTO_%s=%s" % (k, recuentos[k]))
if dict(cat) != {"cambio_de_signo_certificado": 1524, "inconclusa_por_testigos_en_tolerancia": 188, "robusta_infactible_certificada": 16}:
    fallos.append("CATEGORIAS_T7_DISTINTAS")
if set(exf) != {f["afirmacion"] for f in inconclusas} or not set(sind) <= set(exf):
    fallos.append("EXP8_NO_ES_EL_CONJUNTO_DE_INCONCLUSAS")

# ---------------------------------------------------------------- índice ENF por (unidad, cell_id)
enf = {}
for b in br:
    k = (b["unidad"], b["cell_id"])
    if k in enf:
        fallos.append("ENF_DUPLICADO")
    enf[k] = b
res_idx = {(x["unidad"], x["cell_id"]): x for x in rs}
tecla = {x["clave_transformada_sha256"]: x for x in ti}
par = {x["clave_enf"]: x for x in tp}
if len(enf) != 1724 or len(res_idx) != 144 or len(tecla) != 26 or len(par) != 26:
    fallos.append("ENF_TAMANOS_DISTINTOS")
unid_enf = Counter(u for u, _ in enf)


def garantia_clave(k):
    t, p = tecla.get(k) or {}, par.get(k) or {}
    fh = t.get("fila_historica") or {}
    return {"origen_techo": p.get("origen_techo"), "resolucion_par": p.get("resolucion"), "estado_fila_historica": fh.get("estado"),
            "error_kind": fh.get("error_kind"), "garantia": fh.get("garantia"), "error_R": fh.get("error_R"), "tarea": fh.get("tarea"),
            "segundos": fh.get("segundos")}


GAR = {k: garantia_clave(k) for k in tecla}


def cell_de_fila_padre(f, lado):
    """cell_id único de la fila padre autenticada (solo para las 16 robustas, que EXP8_TABLA no lista)."""
    ref, sha = f.get(lado + "_ref"), f.get(lado + "_filas_sha256")
    if not ref:
        return None, "sin_fila"
    b = (T / ref).read_bytes()
    if H(b) != sha:
        fallos.append("FILA_PADRE_NO_AUTENTICA:" + ref)
        return None, "fila_no_autentica"
    d = json.loads(b)
    cs = {r.get("cell_id") for r in d.get("cell_context", []) + d.get("confrontation_result", []) if r.get("cell_id")}
    return (cs.pop(), "fila_padre") if len(cs) == 1 else (None, "cell_id_no_unico")


filas_padre_leidas = 0


def testigo(f, e, lado):
    global filas_padre_leidas
    u = f["testigo_" + lado]
    if e is not None:
        cid, via = e.get(lado + "_cell_id"), "EXP8_TABLA"
        if e.get(lado + "_unidad") not in (None, u):
            fallos.append("UNIDAD_EXP8_DISTINTA_DE_T7:" + f["afirmacion"])
    else:
        cid, via = cell_de_fila_padre(f, lado)
        filas_padre_leidas += via == "fila_padre"
    r = {"unidad": u, "cell_id": cid, "origen_cell_id": via, "estado_evidencia": f[lado + "_estado_evidencia"], "G_T7": f.get(lado + "_G"),
         "veredicto_T7": f.get(lado + "_veredicto"), "conjunto": (e or {}).get(lado + "_set"), "j": (e or {}).get(lado + "_j"), "ext": (e or {}).get(lado + "_ext"),
         "cota": (e or {}).get(lado + "_cota"), "bloque": (e or {}).get(lado + "_bloque"), "capa": (e or {}).get(lado + "_capa"), "diseno": (e or {}).get(lado + "_diseno"),
         "pais": (e or {}).get(lado + "_pais")}
    if f[lado + "_estado_evidencia"] != "filas aceptadas":
        r.update(enlazado=False, motivo_no_enlace="testigo sin filas aceptadas (fuera de las 2.276 unidades)")
        return r
    b = enf.get((u, cid))
    if b is None:
        r.update(enlazado=False, motivo_no_enlace=("unidad presente en ENF con otro cell_id" if unid_enf.get(u) else "par (unidad, cell_id) ausente de ENF"))
        return r
    if b["G_padre"] != f[lado + "_G"]:
        fallos.append("G_PADRE_ENF_DISTINTO_DE_T7:%s:%s" % (f["afirmacion"], lado))
    x = res_idx.get((u, cid))
    r.update(enlazado=True, motivo_no_enlace=None, clave_transformada_sha256=b["clave_transformada_sha256"], K1_reutilizado=b["K1_reutilizado"],
             G_padre_ENF=b["G_padre"], C2_enf=b["C2_enf"], G_enf=b["G_enf"], dG=b["dG"], estado_techo_historico=b["estado_techo_historico"], origen_G=b["origen_G"],
             resolucion=(x or {}).get("resolucion"), certificado_resolucion_sha256=(x or {}).get("certificado_sha256"),
             garantia_clave=GAR.get(b["clave_transformada_sha256"]), signo_padre=(b["G_padre"] > 0) - (b["G_padre"] < 0), signo_enf=(b["G_enf"] > 0) - (b["G_enf"] < 0))
    return r


def canal(f, s, i):
    """Lo que las cotas de los testigos enlazados demuestran sobre la clasificación §17.1 en ABL-ENF."""
    rob = f["categoria_original"] == "robusta_infactible_certificada"
    ls, li = s["enlazado"], i["enlazado"]
    cob = "ambos" if ls and li else "solo_sup" if ls else "solo_inf" if li else "ninguno"
    no_inf = ls and s["G_enf"] > -EPS + TOL          # sup_Omega G_enf > -eps: no robusta infactible
    no_fac = li and i["G_enf"] < EPS - TOL           # inf_Omega G_enf < eps: no robusta factible
    tol_s = ls and abs(s["G_enf"] + EPS) <= TOL
    tol_i = li and abs(i["G_enf"] - EPS) <= TOL
    if rob:
        if no_inf:
            c = "robustez_refutada_por_testigo_sup"
        elif tol_s:
            c = "en_tolerancia_no_decidida"
        elif ls:
            c = "no_decidida_por_testigos (mantener la robustez exige el supremo ENF sobre todo el soporte)"
        else:
            c = "sin_cobertura_ENF"
    elif cob == "ambos":
        c = "inconclusa_preservada" if (no_inf and no_fac) else "en_tolerancia_no_decidida" if (tol_s or tol_i) else "no_decidida_por_testigos"
    elif cob == "solo_sup":
        c = "parcial_no_robusta_infactible" if no_inf else "en_tolerancia_no_decidida" if tol_s else "no_decidida_por_testigos"
    elif cob == "solo_inf":
        c = "parcial_no_robusta_factible" if no_fac else "en_tolerancia_no_decidida" if tol_i else "no_decidida_por_testigos"
    else:
        c = "sin_cobertura_ENF"
    return cob, c


filas = []
for f in sorted(t7, key=lambda x: x["afirmacion"]):
    e = exf.get(f["afirmacion"])
    s, i = testigo(f, e, "sup"), testigo(f, e, "inf")
    cob, c = canal(f, s, i)
    filas.append({"afirmacion": f["afirmacion"], "categoria_original": f["categoria_original"], "inconclusa": f["categoria_original"] in INC,
                  "descompuesta_rem108": bool(e) and not e.get("motivo_sin_descomposicion"), "motivo_sin_descomposicion": (e or {}).get("motivo_sin_descomposicion"),
                  **{k: f[k] for k in ("pid", "kind", "familia", "pais", "j", "disponibilidad", "escenario", "diseno", "cota", "bloque", "capa")},
                  "sup": s, "inf": i, "cobertura_ENF": cob, "canal_eta_f": c,
                  "cambio_de_signo_en_testigos_ENF": [lado for lado, t in (("sup", s), ("inf", i)) if t["enlazado"] and t["signo_padre"] != t["signo_enf"]]})

# ---------------------------------------------------------------- agregados con denominadores explícitos
def agrega(sel):
    return {"afirmaciones": len(sel), "cobertura_ENF": dict(Counter(x["cobertura_ENF"] for x in sel)), "canal_eta_f": dict(Counter(x["canal_eta_f"] for x in sel))}


inc = [x for x in filas if x["inconclusa"]]
rob = [x for x in filas if not x["inconclusa"]]
por_pais = {p: {"universo": agrega([x for x in filas if (x["pais"] or "-") == p]), "inconclusas": agrega([x for x in inc if (x["pais"] or "-") == p]),
                "inconclusas_descompuestas": agrega([x for x in inc if (x["pais"] or "-") == p and x["descompuesta_rem108"]]),
                "robustas": agrega([x for x in rob if (x["pais"] or "-") == p])} for p in sorted({x["pais"] or "-" for x in filas})}
por_familia = {fa: agrega([x for x in inc if x["familia"] == fa]) for fa in sorted({x["familia"] for x in filas})}
por_pais_j = {"%s|%s" % (x["pais"], x["sup"]["j"]): 0 for x in inc}
for x in inc:
    por_pais_j["%s|%s" % (x["pais"], x["sup"]["j"])] += 1
celdas_testigo = {(t["unidad"], t["cell_id"]) for x in filas for t in (x["sup"], x["inf"]) if t["cell_id"]}
celdas_inc = {(t["unidad"], t["cell_id"]) for x in inc for t in (x["sup"], x["inf"]) if t["cell_id"]}
enl = [t for x in filas for t in (x["sup"], x["inf"]) if t["enlazado"]]
cambios = [x["afirmacion"] for x in filas if x["cambio_de_signo_en_testigos_ENF"]]
claves_usadas = Counter(t["clave_transformada_sha256"] for t in enl)
cel_enf_sin_afirmacion = sorted(set(enf) - celdas_testigo)
cov = {"kind": "cobertura-exp8-enf-rem147", "derivado_de_fuentes_existentes": True, "no_es_corrida_aceptada": True,
       "fuentes": {"autenticacion": {"ruta": "fuentes/" + AUT.name, "sha256": H(AUT.read_bytes())},
                   "T7_anexo": aut["areas"][A108]["archivos"]["conciliacion/ensamblajes/T7_anexo.json"]["sha256"],
                   "EXP8_TABLA": aut["areas"][A108]["archivos"]["conciliacion/EXP8_TABLA.json"]["sha256"],
                   "brechas_celdas": aut["areas"][A131]["archivos"]["integ_conciliacion_ENF_INTEGRAL/brechas_celdas.jsonl"]["sha256"],
                   "enf_brechas_resueltas": aut["areas"][A131]["archivos"]["integ_ensamblado_ENF_INTEGRAL/enf_brechas_resueltas.jsonl"]["sha256"],
                   "enf_techos_integrados": aut["areas"][A131]["archivos"]["integ_ensamblado_ENF_INTEGRAL/enf_techos_integrados.jsonl"]["sha256"],
                   "techos_pares": aut["areas"][A131]["archivos"]["integ_conciliacion_ENF_INTEGRAL/techos_pares.jsonl"]["sha256"]},
       "reglas": {"enlace": "igualdad exacta (unidad, cell_id) y G_padre(ENF) == G(T7); nunca por país, prefijo o cantidad",
                  "umbral": "§17.1: sup G <= -eps robusta infactible; inf G >= eps robusta factible; si no, inconclusa; eps = 0,01",
                  "tolerancia": "1e-4 (tolerancia de certificado del T7): una comparación a <= 1e-4 del umbral queda en_tolerancia_no_decidida",
                  "cotas": "sup_Omega G_enf >= G_enf(testigo sup padre); inf_Omega G_enf <= G_enf(testigo inf padre): solo demuestran NO robustez",
                  "lo_que_no_es": "no es clasificación sobre todo el soporte ENF salvo donde las cotas bastan; no es causalidad empírica; no ordena canales; "
                                  "la descomposición rem108 es identidad entre testigos distintos, no ablación",
                  "resolucion": "no_alcanzado_demostrado (144 celdas, clave d59edf8a9d1461d1) separado de complete; sin argmax"},
       "recuentos": recuentos, "fallos": fallos,
       "testigos": {"ranuras": 2 * len(filas), "con_filas": sum(t["estado_evidencia"] == "filas aceptadas" for x in filas for t in (x["sup"], x["inf"])),
                    "enlazadas_ENF": len(enl), "celdas_testigo_unicas_universo": len(celdas_testigo), "celdas_testigo_unicas_inconclusas": len(celdas_inc),
                    "celdas_ENF": len(enf), "celdas_ENF_que_son_testigo": len(set(enf) & celdas_testigo), "celdas_ENF_sin_afirmacion": len(cel_enf_sin_afirmacion),
                    "filas_padre_leidas_para_cell_id_de_robustas": filas_padre_leidas,
                    "motivos_no_enlace": dict(Counter(t["motivo_no_enlace"] for x in filas for t in (x["sup"], x["inf"]) if not t["enlazado"])),
                    "origen_G_de_enlazadas": dict(Counter(t["origen_G"] for t in enl)), "claves_ENF_usadas": len(claves_usadas),
                    "dG_enlazadas": [min(t["dG"] for t in enl), max(t["dG"] for t in enl)] if enl else None,
                    "max_error_R_claves_usadas": max((GAR[k]["error_R"] or 0) for k in claves_usadas) if claves_usadas else None},
       "universo": agrega(filas), "inconclusas": agrega(inc), "inconclusas_descompuestas": agrega([x for x in inc if x["descompuesta_rem108"]]),
       "inconclusas_sin_descomposicion": agrega([x for x in inc if not x["descompuesta_rem108"]]), "robustas": agrega(rob),
       "por_familia_inconclusas": por_familia, "por_pais_j_inconclusas": por_pais_j,
       "afirmaciones_con_cambio_de_signo_en_testigo_ENF": cambios,
       "no_cubierto": {"afirmaciones": [x["afirmacion"] for x in filas if x["cobertura_ENF"] != "ambos"],
                       "causa": "testigo sin filas aceptadas (7 afirmaciones, 4 testigos); ninguna otra causa si la lista coincide con SIETE_CASOS"}}
cov["conforme"] = not fallos
OUT.mkdir(parents=True, exist_ok=True)
with (OUT / "ENF_POR_AFIRMACION.jsonl").open("x", encoding="utf-8", newline="\n") as fh:
    for x in filas:
        fh.write(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n")
cov["ENF_POR_AFIRMACION_sha256"] = H((OUT / "ENF_POR_AFIRMACION.jsonl").read_bytes())
with (OUT / "RESUMEN_POR_PAIS.json").open("x", encoding="utf-8", newline="\n") as fh:
    fh.write(json.dumps({"kind": "resumen-por-pais-exp8-enf-rem147", "denominadores": "universo 1.728; inconclusas 1.712; descompuestas 1.705; robustas 16",
                         "por_pais": por_pais}, ensure_ascii=False, indent=1) + "\n")
with (OUT / "COBERTURA_EXP8.json").open("x", encoding="utf-8", newline="\n") as fh:
    fh.write(json.dumps(cov, ensure_ascii=False, indent=1) + "\n")

# ---------------------------------------------------------------- tabla legible
CAN = ["inconclusa_preservada", "parcial_no_robusta_infactible", "parcial_no_robusta_factible", "robustez_refutada_por_testigo_sup",
       "en_tolerancia_no_decidida", "no_decidida_por_testigos", "no_decidida_por_testigos (mantener la robustez exige el supremo ENF sobre todo el soporte)",
       "sin_cobertura_ENF"]
L = ["# Cobertura Exp8 × ENF por afirmación (rem147)", "", "Derivado de fuentes existentes autenticadas; no es una corrida aceptada. Enlace exacto (unidad, cell_id).", "",
     "| ámbito | denominador | ambos | solo sup | solo inf | ninguno |", "|---|---:|---:|---:|---:|---:|"]
for nom, sel in (("universo T7", filas), ("inconclusas", inc), ("inconclusas descompuestas", [x for x in inc if x["descompuesta_rem108"]]),
                 ("inconclusas sin descomposición", [x for x in inc if not x["descompuesta_rem108"]]), ("robustas infactibles", rob)):
    c = Counter(x["cobertura_ENF"] for x in sel)
    L.append("| %s | %d | %d | %d | %d | %d |" % (nom, len(sel), c["ambos"], c["solo_sup"], c["solo_inf"], c["ninguno"]))
L += ["", "## Canal η_f/2 (ABL-ENF) por país: lo que demuestran las cotas de los testigos", "",
      "| país | universo | inconclusas | " + " | ".join(CAN[:6]) + " | sin cobertura |", "|---|---:|---:|" + "---:|" * 7]
for p, v in por_pais.items():
    cu = Counter(x["canal_eta_f"] for x in filas if (x["pais"] or "-") == p)
    L.append("| %s | %d | %d | %s | %d |" % (p, v["universo"]["afirmaciones"], v["inconclusas"]["afirmaciones"],
                                            " | ".join(str(cu[k] + (cu[CAN[6]] if k == "no_decidida_por_testigos" else 0)) for k in CAN[:6]), cu["sin_cobertura_ENF"]))
L += ["", "## Inconclusas por familia", "", "| familia | inconclusas | ambos | inconclusa preservada |", "|---|---:|---:|---:|"]
for fa, v in por_familia.items():
    L.append("| %s | %d | %d | %d |" % (fa, v["afirmaciones"], v["cobertura_ENF"].get("ambos", 0), v["canal_eta_f"].get("inconclusa_preservada", 0)))
tg = cov["testigos"]
L += ["", "## Testigos y celdas", "", "- Ranuras de testigo: %d; con filas aceptadas: %d; enlazadas con ENF: %d." % (tg["ranuras"], tg["con_filas"], tg["enlazadas_ENF"]),
      "- Celdas testigo únicas (unidad, cell_id): %d en el universo, %d en las inconclusas; celdas ENF: %d, de ellas testigo: %d, sin afirmación: %d."
      % (tg["celdas_testigo_unicas_universo"], tg["celdas_testigo_unicas_inconclusas"], tg["celdas_ENF"], tg["celdas_ENF_que_son_testigo"], tg["celdas_ENF_sin_afirmacion"]),
      "- dG en testigos enlazados: %s; afirmaciones con cambio de signo en algún testigo ENF: %d." % (tg["dG_enlazadas"], len(cambios)),
      "- Origen de G en testigos enlazados: %s." % tg["origen_G_de_enlazadas"],
      "- Motivos de no enlace: %s." % tg["motivos_no_enlace"], "",
      "Lectura: «inconclusa_preservada» significa que, con η_f/2 y el resto fijo, los dos testigos padre siguen demostrando sup G_enf > −ε y inf G_enf < ε. "
      "No identifica el eslabón que provoca el cruce ni ordena canales; tampoco convierte signos puntuales en una clasificación de todo el soporte donde las cotas no bastan."]
with (OUT / "COBERTURA_EXP8.md").open("x", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(L) + "\n")
print(json.dumps({"conforme": cov["conforme"], "fallos": fallos[:10], "recuentos": {k: v for k, v in recuentos.items() if not isinstance(v, dict)},
                  "universo": cov["universo"], "inconclusas": cov["inconclusas"], "robustas": cov["robustas"], "testigos": tg, "cambios": len(cambios)},
                 ensure_ascii=False, indent=1))
raise SystemExit(0 if cov["conforme"] else 4)
