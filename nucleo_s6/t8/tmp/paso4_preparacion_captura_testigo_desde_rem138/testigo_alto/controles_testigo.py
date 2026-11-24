"""rem138 — C3 TESTIGO ALTO: CONTROLES PREVIOS de la clave e8b1f7fd… (solo lectura; escribe en exclusiva <salida>/CONTROLES_TESTIGO.json).
a) Pertenencia: regenera el plan implícito 6cec0a6d desde su generador fijado (unidades.plan_units, igual en el núcleo histórico de lima1855 y en
   la instalación; nodos L0 de D7 10a0bd5b; configuración de plan de BRUN-cb33e6b2 reconstruida en rem132) y lo compara con el plan de rem132;
   después reconstruye de forma dirigida la unidad de ESA celda en cada conjunto base (índices de nodo, prefijo k, unit_id) y su dominio D7.
b) Identidad: autentica la plantilla en su fuente (fila frontier_context de BRUN-cb33e6b2), recalcula su clave y la propuesta, fija los bytes
   reales de los 13 archivos del techo de EQ-TECHO-T8-1 y recalcula tolerances_sha256 desde el literal; compara con la instalación actual.
c) Dominio: el motor usa float(bar_tau) = binary64(0.6) < 3/5; encierro VERIFICADO (comparaciones racionales exactas) de márgenes de adopción
   y de R/B_pot en tres puntos (3/5 de rem137, la esquina binary64 y uno interior 19/32 con holgura).
d) Cobertura: las 40 filas pendientes (RESTO_C3 de rem136) con v exacto frente a la cota inferior verificada y la banda 2·1e-7.
No importa paper2b.model/modelos/supremum ni llama a capture_ceiling, sup_bound, evaluate, bridge ni mallas. Decimal solo PROPONE candidatos;
cada encierro de potencia se acepta solo si lo^n <= x^m <= hi^n se cumple con Fraction exacta.
Uso: python -B -I -X utf8 controles_testigo.py <raiz> <area> <salida>"""
import ast
import csv
import collections
import hashlib
import importlib.util
import json
import math
import sys
import time
from decimal import Decimal, getcontext
from fractions import Fraction as Fr
from itertools import product
from pathlib import Path

R, X, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
T = R / "tmp"
T0 = time.time()
sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
HF = lambda p: sha(Path(p).read_bytes())  # noqa: E731
canon = lambda v: json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")  # noqa: E731
H = lambda v: sha(canon(v))  # noqa: E731
OUT.mkdir(parents=True, exist_ok=False)
FALLOS, AUT = [], {}
CLAVE = "e8b1f7fdb9c7017605e0a4162fc6688e7b6ed01d2308ff72106ed6cf6834a97b"
PLAN = "6cec0a6d662104dab6a490cea647cd24ae995819a416eaf3cfd4fd9f3c060e42"
RUN_T = "BRUN-cb33e6b24039acc84fb1a065"
CEI_T = "CEI:25038b0a61bb4d08da69c5751a7bf669216e9a51"
KEY_T = "bd8a89326568c932e019ee62134b2ab54065a3755b864176bf608496e7663570"


def need(t, codigo):
    if not t:
        FALLOS.append(codigo)
    return bool(t)


# ------------------------------------------------------------------------------------------------- fuentes autenticadas
SELLOS = {"paso4_emision_lambda_conexion_captura_desde_rem137": "59188e65c2d8dd665679f3b47780e2859633505b260127cc435c772431bf92b2",
          "paso4_procedencia_cota_desde_rem136": "16a2e53e21ba1d3615616bc598ea281ec078f55a5bd97b96a4ae9746934a4087",
          "paso4_emision_lambda_captura_desde_rem135": "313719680b730727b64d3260359030486c2b8449b68632b32805d4b19051bdd3",
          "paso4_exp0_t8_desde_rem132": "542036fdd1be7f38e56c7c9f39320f40da644477ea3072d1dc1c198d683b39f9",
          "remanente_s1df_s2_s3_h4_paso4_3_7_2026-10-10_lima1855": "1bb94b75d57c4b97e9ebf662bc6cc6117e3b8b30792e46d6d1e5ef1a36ea8cdd"}
INV = {}
for area, s in SELLOS.items():
    p = T / area / "audit/entrega.json"
    need(HF(p) == s, "SELLO_DISTINTO:" + area)
    INV[area] = json.loads(p.read_bytes())["files"]
A137, A136, A135, A132, L55 = SELLOS


def auten(area, rel):
    b = (T / area / rel).read_bytes()
    h = sha(b)
    need(INV[area].get(rel, {}).get("sha256") == h, "NO_AUTENTICO:%s/%s" % (area, rel))
    AUT.setdefault(area, {})[rel] = h
    return b


TES = json.loads(auten(A137, "c3_acoplada/C3_TESTIGOS.json"))
COTA137 = json.loads(auten(A137, "c3_acoplada/C3_COTA_INFERIOR.json"))
auten(A137, "c3_acoplada/C3_ACOPLADA.md")
auten(A137, "c3_acoplada/C3_ACOPLADA.json")
auten(A137, "c3_acoplada/c3_cota_inferior.py")
RESTO = json.loads(auten(A136, "c_cota/RESTO_C3.json"))
EQ = json.loads(auten(A135, "c_captura/salida_c1b/EQUIVALENCIA_EFECTIVA_TECHO.json"))
IDEN = json.loads(auten(A132, "derivados/salida_d2/t8/IDENTIDAD_Y_PLAN_POR_CORRIDA.json"))
PLAN132 = json.loads(auten(A132, "derivados/salida_d2/t8/plan_unidades.json"))
auten(A132, "derivados/derivar_exp0_t8.py")
FILAS_T = json.loads(auten(L55, "demo/rem3/resultados/S3_P1-PER-G-df-0_filas.json"))
CAND = T / L55 / "candidato"
for rel in ("candidato/herramientas/b/unidades.py", "candidato/src/paper2b/run.py", "candidato/src/paper2b/keys.py", "candidato/src/paper2b/numeric.py",
            "candidato/src/paper2b/supports.py", "candidato/src/paper2b/d7view.py", "candidato/herramientas/b/ejecutar_b.py"):
    auten(L55, rel)
D7T = "10a0bd5bb8ea48d54d1bd0916b072afcf8cd5a4eed9c5ec16a90a728f021b739"
D7 = R / "fase2_datos/d7_calibracion/versions" / D7T
d7m = json.loads((D7 / "d7_manifest.json").read_bytes())
need(d7m["tree_sha256"] == D7T, "D7_ARBOL")
for f in d7m["files"]:
    need(HF(D7 / f["path"]) == f["sha256"], "D7_ARCHIVO:" + f["path"])
spec = importlib.util.spec_from_file_location("numeric_l55", CAND / "src/paper2b/numeric.py")   # solo canon_dec (stdlib); no es el modelo
NUM = importlib.util.module_from_spec(spec)
spec.loader.exec_module(NUM)


def csv_rows(p):
    with open(p, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


SUP = collections.defaultdict(dict)
for r in csv_rows(D7 / "support_set.csv"):
    SUP[(r["support_set_id"], r["parameter_id"])][r["variant_id"]] = r
BIND = {(r["support_set_id"], r["parameter_id"], r["scope_id"]): r for r in csv_rows(D7 / "parameter_bindings.csv")}
TAU = {(r["support_set_id"], r["instrument_j"]): r for r in csv_rows(D7 / "tau_domains.csv")}
SUPID = {r["support_id"]: r for v in SUP.values() for r in v.values()}


def soporte(set_id, pid):           # = D7View.support con el vínculo global (misma regla que rem132)
    v = SUP[(set_id, pid)]
    if len(v) == 1:
        return next(iter(v.values()))
    b = BIND[(set_id, pid, "global")]
    return next(x for x in v.values() if x["support_id"] == b["support_id"])


def nodos(set_id, pid):             # = D7View.nodes: Decimal(repr(float)) de level0_nodes
    return [Decimal(repr(x)) if isinstance(x, float) else Decimal(str(x)) for x in json.loads(soporte(set_id, pid)["level0_nodes"])]


# ------------------------------------------------------------------------------------------------- a) pertenencia
def fuente_funcion(path, nombre):
    src = Path(path).read_text(encoding="utf-8")
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, (ast.FunctionDef,)) and n.name == nombre:
            return ast.get_source_segment(src, n)
    return None


def literal(path, nombre):
    for n in ast.parse(Path(path).read_text(encoding="utf-8")).body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == nombre for t in n.targets):
            return ast.literal_eval(n.value)
    return None


INST = R / "paso4/instalacion"
gen_hist = fuente_funcion(CAND / "herramientas/b/unidades.py", "plan_units")
gen_inst = fuente_funcion(INST / "herramientas/b/unidades.py", "plan_units")
STRUCT = literal(CAND / "src/paper2b/run.py", "STRUCT")
FIXED = literal(CAND / "src/paper2b/run.py", "FIXED")
BARS = literal(CAND / "src/paper2b/run.py", "BARS")
ev_sets = fuente_funcion(CAND / "src/paper2b/run.py", "evaluated_sets")
lvl_hist = fuente_funcion(CAND / "src/paper2b/supports.py", "level_nodes")
need(gen_hist is not None and gen_hist == gen_inst, "GENERADOR_DISTINTO")
need(list(STRUCT) == IDEN["corridas"][RUN_T]["STRUCT"], "STRUCT_DISTINTO")
cfg_plan = IDEN["corridas"][RUN_T]["configuracion_plan"]
need(IDEN["corridas"][RUN_T]["configuracion_reconstruida"] is True and IDEN["corridas"][RUN_T]["plan"]["plan_sha256"] == PLAN, "IDENTIDAD_REM132")
need(cfg_plan["level"] == 0 and cfg_plan["derived_suffixes"] == [], "CONFIG_PLAN")
need(all(v.get("plan_sha256") == PLAN for v in EQ["configuracion_y_metodo"].values()) and EQ["plan_sha256"] == PLAN, "PLAN_EQ")
need(RUN_T in EQ["grupos"]["EQ-TECHO-T8-1"] and len(EQ["grupos"]["EQ-TECHO-T8-1"]) == 14, "GRUPO_EQ")
# regeneración completa del plan (prefijos de unidad, NO Omega): nivel 0 => level_nodes devuelve los mismos nudos (solo cuenta su número)
sets_eval = [b for b in cfg_plan["base_sets"]] + ["%s.%s" % (b, s) for b in cfg_plan["base_sets"] for s in cfg_plan["derived_suffixes"]]
units, por_set = [], {}
for set_id in sets_eval:
    sizes = [len(nodos(set_id, p)) for p in STRUCT]
    rest, k = math.prod(sizes), 0
    while rest > cfg_plan["max_unit_nodes"] and k < len(sizes):
        rest //= sizes[k]
        k += 1
    n0 = len(units)
    for idx in product(*[range(sizes[i]) for i in range(k)]):
        prefix = {STRUCT[i]: idx[i] for i in range(k)}
        units.append({"unit_id": "U" + H([set_id, sorted(prefix.items())])[:24], "set_id": set_id, "prefix": prefix})
    por_set[set_id] = {"nodos_por_eje": dict(zip(STRUCT, sizes)), "k_prefijo": k, "puntos_por_unidad": rest, "unidades": len(units) - n0}
plan_regenerado = H(units)
pl132 = PLAN132["planes"][0]
need(plan_regenerado == PLAN, "PLAN_REGENERADO_DISTINTO")
need(pl132["plan_sha256"] == PLAN and H(pl132["units"]) == PLAN and pl132["units"] == units, "PLAN_REM132_DISTINTO")
ids = {u["unit_id"]: u for u in units}
# celda dirigida
CELDA = {"a": "1.1", "beta_tilde": "0.25", "eta_d": "0.1", "eta_f": "0.1", "kappa_tilde": "0.2", "phi": "0.75", "rho": "1", "u_theta": "0.9", "z_cost": "1"}
FIJOS = {"c_legal": "1", "gamma": "1", "t": "0", "z_m": "1"}
celda_por_set = {}
for set_id in sets_eval:
    idx, dom = {}, {}
    for p in STRUCT:
        s, ns, v = soporte(set_id, p), nodos(set_id, p), Decimal(CELDA[p])
        idx[p] = ns.index(v) if v in ns else None
        lo, hi = Decimal(s["lower"]), Decimal(s["upper"])
        dom[p] = {"support_id": s["support_id"], "nodos_L0": [str(x) for x in ns], "indice": idx[p], "lower": s["lower"], "upper": s["upper"],
                  "cerrado": [s["lower_closed"], s["upper_closed"]], "dentro": lo <= v <= hi}
    fijos = {p: [str(x) for x in nodos(set_id, p)] for p in FIXED + BARS}
    k = por_set[set_id]["k_prefijo"]
    ok_nodos = all(i is not None for i in idx.values())
    uid = "U" + H([set_id, sorted({p: idx[p] for p in STRUCT[:k]}.items())])[:24] if ok_nodos else None
    tau = TAU.get((set_id, "df"))
    td_s, tf_s = (SUPID.get(tau["tau_d_support_id"]), SUPID.get(tau["tau_f_support_id"])) if tau else (None, None)
    celda_por_set[set_id] = {"indices": idx, "dominios": dom, "k_prefijo": k, "unit_id": uid, "unidad_en_plan": uid in ids,
                             "prefijo": {p: idx[p] for p in STRUCT[:k]} if ok_nodos else None,
                             "resto_en_la_unidad": {p: idx[p] for p in STRUCT[k:]} if ok_nodos else None,
                             "fijos_y_barras_D7": fijos,
                             "tau_df": {"tau_domain_id": tau["tau_domain_id"] if tau else None,
                                        "tau_d": [td_s["lower"], td_s["upper"], td_s["lower_closed"], td_s["upper_closed"]] if td_s else None,
                                        "tau_f": [tf_s["lower"], tf_s["upper"], tf_s["lower_closed"], tf_s["upper_closed"]] if tf_s else None}}
    need(ok_nodos and uid in ids and ids[uid]["prefix"] == celda_por_set[set_id]["prefijo"], "CELDA_FUERA_DEL_PLAN:" + set_id)
    need(all(d["dentro"] for d in dom.values()), "CELDA_FUERA_DE_DOMINIO:" + set_id)
    need(all(fijos[p] == [FIJOS[p]] or [str(Decimal(x).normalize()) for x in fijos[p]] == [FIJOS[p]] for p in FIXED), "FIJOS_DISTINTOS:" + set_id)
    need(fijos["bar_tau_d"] == ["0.6"] and fijos["bar_tau_f"] == ["0.6"], "BARRAS_DISTINTAS:" + set_id)
    need(tau is not None and td_s["upper"] == "0.6" and tf_s["upper"] == "0.6" and td_s["lower"] == "0" and tf_s["lower"] == "0", "TAU_DF:" + set_id)
pertenencia = {"plan_sha256": PLAN, "plan_regenerado_sha256": plan_regenerado, "unidades": len(units), "por_set": por_set,
               "igual_al_plan_rem132": pl132["units"] == units,
               "generador": {"funcion": "plan_units", "historico": {"ruta": "tmp/%s/candidato/herramientas/b/unidades.py" % L55,
                                                                    "sha256": HF(CAND / "herramientas/b/unidades.py")},
                             "instalacion": {"ruta": "paso4/instalacion/herramientas/b/unidades.py", "sha256": HF(INST / "herramientas/b/unidades.py")},
                             "texto_de_la_funcion_identico": gen_hist == gen_inst, "texto_sha256": sha(gen_hist.encode("utf-8")) if gen_hist else None},
               "evaluated_sets_texto_sha256": sha(ev_sets.encode("utf-8")) if ev_sets else None,
               "level_nodes_texto_sha256": sha(lvl_hist.encode("utf-8")) if lvl_hist else None,
               "STRUCT": list(STRUCT), "FIXED": list(FIXED), "BARS": list(BARS), "configuracion_plan": cfg_plan,
               "seleccion": ("la corrida monolítica evalúa cada omega = producto de nudos L0 por eje STRUCT x vértices macro x fijos; una unidad "
                             "fija los índices de los k primeros ejes (run.py omegas: axes[pid] = [axes[pid][prefix[pid]]]); el techo se pide por "
                             "(omega, diseño en designs, instrumento con dominio tau_domains) y se cachea por la clave estructural, que solo "
                             "depende de STRUCT+FIXED, diseño, instrumento, barras, teoría y técnica"),
               "celda": CELDA, "diseno": "G", "instrumento": "df", "por_conjunto": celda_por_set,
               "unit_ids": sorted({v["unit_id"] for v in celda_por_set.values()})}

# ------------------------------------------------------------------------------------------------- b) identidad
fc = [r for r in FILAS_T["frontier_context"] if r["structural_key_sha256"] == KEY_T]
cc = [r for r in FILAS_T["capture_ceiling_result"] if r["ceiling_id"] == CEI_T]
need(len(fc) >= 1 and len(cc) == 1, "PLANTILLA_SIN_FUENTE")
pay_t = fc[0]["structural_key_payload"] if isinstance(fc[0]["structural_key_payload"], dict) else json.loads(fc[0]["structural_key_payload"])
need(sha(canon(pay_t)) == KEY_T and fc[0]["run_id"] == RUN_T, "PLANTILLA_CLAVE")
tpl = TES["plantilla"]
need(tpl["structural_key_sha256"] == KEY_T and tpl["ceiling_id"] == CEI_T, "PLANTILLA_REF")
for campo in ("technical", "tau_domain", "theory_sha256"):
    need(tpl[campo] == pay_t[campo], "PLANTILLA_CAMPO:" + campo)
prop = [c for c in TES["propuesta_etapa_1_en_orden"] if c["structural_key_sha256"] == CLAVE]
need(len(prop) == 1, "PROPUESTA_AUSENTE")
pay = prop[0]["payload"]
need(sha(canon(pay)) == CLAVE, "CLAVE_NO_REPRODUCE")
need({k: v for k, v in pay.items() if k != "values"} == {k: v for k, v in pay_t.items() if k != "values"}, "PAYLOAD_NO_SOLO_VALORES")
unid_t = {r["parameter_id"]: r["value_unit"] for r in pay_t["values"]}
esperado = dict(CELDA, **FIJOS)
fila_valor = {r["parameter_id"]: r for r in pay["values"]}
need(sorted(fila_valor) == sorted(unid_t) == sorted(esperado), "PRIMITIVAS_DISTINTAS")
for p, r in fila_valor.items():
    need(r["value_unit"] == unid_t[p], "UNIDAD:" + p)
    need(r["value"] == NUM.canon_dec(Decimal(esperado[p])), "CANON_DEC:" + p)
# clave recomputada desde D7 (no desde la propuesta): valores de nodo D7 del primer conjunto, canon_dec y plantilla
s0 = sets_eval[0]
vals_d7 = {p: nodos(s0, p)[celda_por_set[s0]["indices"][p]] for p in STRUCT}
vals_d7.update({p: nodos(s0, p)[0] for p in FIXED})
pay_d7 = dict(pay_t, values=[{"parameter_id": p, "value": NUM.canon_dec(vals_d7[p]), "value_unit": unid_t[p]} for p in sorted(vals_d7)])
need(sha(canon(pay_d7)) == CLAVE, "CLAVE_DESDE_D7_DISTINTA")
cm = EQ["configuracion_y_metodo"][RUN_T]
tec = pay_t["technical"]
need(tec["configuration_sha256"] == cm["configuration_sha256"] and tec["method_sha256"] == cm["method_sha256"]
     and all(tec[k] == cm[k] for k in ("code_sha256", "contract_sha256", "environment_sha256", "tolerances_sha256")), "TECNICA_NO_ES_DE_LA_CORRIDA")
need(cm["configuracion_recalculada"] is True and cm["metodo_recalculado"] is True, "CONFIG_METODO_NO_RECALCULADOS")
tol = literal(CAND / "herramientas/b/ejecutar_b.py", "TOLERANCES")
tol_sha = sha(canon(tol) + b"\n")
need(tol_sha == tec["tolerances_sha256"], "TOLERANCIAS_DISTINTAS")
claves_techo = {}
for f, lista in EQ["archivos_clave_del_techo"].items():
    h_hist = HF(CAND / "src/paper2b" / f)
    h_inv = INV[L55].get("candidato/src/paper2b/" + f, {}).get("sha256")
    pi = INST / "src/paper2b" / f
    h_inst = HF(pi) if pi.exists() else None
    claves_techo[f] = {"historico_lima1855": h_hist, "inventario_lima1855": h_inv, "eq_techo": lista, "instalacion_actual": h_inst,
                       "historico_igual_eq": lista == [h_hist] and h_inv == h_hist, "instalacion_igual": h_inst == h_hist}
    need(lista == [h_hist] and h_inv == h_hist, "ARCHIVO_TECHO:" + f)
techo_t = cc[0]
identidad = {"plantilla": {"fuente": "tmp/%s/demo/rem3/resultados/S3_P1-PER-G-df-0_filas.json" % L55, "fila_frontier_context": {k: fc[0][k] for k in (
                 "frontier_id", "run_id", "omega_id", "tau_domain_id", "design_v", "instrument_j", "availability_matrix_hash")},
                           "clave_plantilla_recalculada": sha(canon(pay_t)), "techo_plantilla": techo_t},
             "clave_propuesta_recalculada": sha(canon(pay)), "clave_desde_nodos_D7": sha(canon(pay_d7)),
             "tecnica_historica_de_la_clave": tec, "corrida": RUN_T, "run_class": cm["run_class"],
             "grupo": "EQ-TECHO-T8-1", "corridas_del_grupo": len(EQ["grupos"]["EQ-TECHO-T8-1"]), "iguales_en_las_14": EQ["iguales_en_las_14"],
             "config_sup": cm["sup"], "inversion_budget_seconds": cm["inversion_budget_seconds"], "proveedor": cm["model_provider"],
             "garantia_plataforma": EQ["garantia_plataforma"], "tolerancias": {"literal": tol, "sha256_recalculado": tol_sha},
             "bytes_reales_del_techo": claves_techo,
             "instalacion_difiere_en": sorted(f for f, v in claves_techo.items() if not v["instalacion_igual"]),
             "identidad_declarada_vs_derivada": (
                 "La clave e8b1f7fd… lleva la técnica HISTÓRICA de BRUN-cb33e6b2 (código 037d20d3, configuración 71e369bb, método e6e019c3, "
                 "contrato 4d7e676a, entorno 41b467a1, tolerancias 0fc40e7d). configuración y método están recalculados por rem135 (EQ-TECHO-T8-1); "
                 "las tolerancias se recalculan aquí desde el literal; los 13 archivos del techo se fijan por bytes reales del núcleo histórico. "
                 "code_sha256 y environment_sha256 son huellas registradas de documentos (manifiesto de código CODE_GLOBS, perfil RE-03) que no "
                 "se conservan como archivo: la ejecución futura registra la huella DERIVADA de lo que realmente carga y la conserva junto a la "
                 "declarada; si difieren, no se reescribe la declarada ni se atribuye el hash histórico a código nuevo. La instalación actual "
                 "difiere en run.py (y lo que se liste), por eso el trabajador usa los bytes del núcleo histórico de lima1855.")}

# ------------------------------------------------------------------------------------------------- c) dominio: encierros verificados
getcontext().prec = 90
EPS = Fr(1, 10 ** 60)


def pot(x: Fr, e: Fr):
    """[lo, hi] con lo <= x^e <= hi, x en (0,1) racional, e racional; verificado con potencias enteras exactas."""
    m, n = e.numerator, e.denominator
    base = x if m >= 0 else 1 / x
    t = base ** abs(m)
    a = Fr(((Decimal(base.numerator) / Decimal(base.denominator)).ln() * Decimal(abs(m)) / Decimal(n)).exp())   # candidato, no prueba
    lo, hi = a - EPS, a + EPS
    if not (lo > 0 and lo ** n <= t <= hi ** n):
        raise ArithmeticError("ENCIERRO_NO_VERIFICADO")
    return (lo, hi)


def iadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def isub(a, b):
    return (a[0] - b[1], a[1] - b[0])


def imul(a, b):
    ps = [a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1]]
    return (min(ps), max(ps))


def k_(c):
    return (Fr(c), Fr(c))


def dec(q: Fr, cifras=40):
    """Lectura decimal TRUNCADA hacia abajo (solo presentación; los criterios usan Fraction)."""
    s = q.numerator * 10 ** cifras // q.denominator
    return "%s%d.%0*d" % ("-" if s < 0 else "", abs(s) // 10 ** cifras, cifras, abs(s) % 10 ** cifras)


def evaluar_punto(td_, tf_, eta_d, eta_f, phi, kap, beta_t):
    xd, xf = 1 - td_, 1 - tf_
    r = pot(xd, eta_d)
    tdt = imul(isub(k_(1), pot(xd, 1 + eta_d)), k_(1 / (1 + eta_d)))                    # t̃_d = (1 - x^(1+η))/(1+η)
    al = eta_f - phi
    xa, xa1 = pot(xf, al), pot(xf, al + 1)
    Q = imul(k_(tf_), xa)                                                                  # Q = τ_f x^α
    hid = imul(k_(eta_f), isub(imul(isub(k_(1), xa), k_(1 / al)), imul(isub(k_(1), xa1), k_(1 / (al + 1)))))
    tft = iadd(Q, hid)                                                                     # t̃_f = Q + η_f ∫ s(1-s)^(α-1)
    kF = imul(k_(kap), iadd(k_(1), imul(k_(phi), tft)))
    tb = k_(td_ * beta_t)
    m1 = isub(k_(1), tb)                                                                   # F0-I0 >= (1 - τ_d β̃) z
    m2 = isub(isub(k_(1), tdt), kF)                                                        # F1-F0 = ((1-t̃_d) - k_F) z  (G, ρ=1)
    m3 = isub(k_(1), iadd(iadd(tb, tdt), imul(k_(kap * phi), tft)))                        # F1-I1 >= (1 - τβ̃ - t̃_d - κ̃φ t̃_f) z
    val = iadd(imul(k_(td_), r), imul(k_(kap), Q))                                         # R/B_pot = τ_d r + κ̃ Q
    todo_F = m1[0] > 0 and m2[0] > 0 and m3[0] >= 0
    f = lambda i: {"lo": dec(i[0]), "hi": dec(i[1]), "ancho": float(i[1] - i[0])}  # noqa: E731
    return {"todo_F_demostrado": todo_F, "margen_F0_I0": f(m1), "margen_F1_F0": f(m2), "margen_F1_I1": f(m3), "Q": f(Q), "t_tilde_d": f(tdt),
            "t_tilde_f": f(tft), "k_F": f(kF), "R_sobre_Bpot": f(val)}, val, todo_F


B64 = Fr(0.6)                      # binary64(0.6) = valor exacto que usa el motor (float(Decimal("0.6")))
TRES_QUINTOS = Fr(3, 5)
INTERIOR = Fr(19, 32)              # exacto en binary64; interior con holgura
par = dict(eta_d=Fr(1, 10), eta_f=Fr(1, 10), phi=Fr(3, 4), kap=Fr(1, 5), beta_t=Fr(1, 4))
need(Fr(float(Decimal("0.6"))) == B64 and B64 < TRES_QUINTOS, "BINARY64")
theta = 1 + Fr(9, 10) * (Fr(11, 10) - 1)
puntos, vals = {}, {}
for nombre, tau in (("rem137_3_5_racional", TRES_QUINTOS), ("esquina_binary64_0_6", B64), ("interior_19_32", INTERIOR)):
    res, val, ok = evaluar_punto(tau, tau, **par)
    en_motor = 0 <= tau <= B64
    res.update(tau_d=str(tau), tau_f=str(tau), tau_decimal=dec(tau, 60),
               en_dominio_del_motor=en_motor, en_dominio_de_la_clave=0 <= tau <= TRES_QUINTOS,
               holgura_inferior=str(tau), holgura_superior_motor=str(B64 - tau), holgura_superior_motor_float=float(B64 - tau))
    puntos[nombre], vals[nombre] = res, (val, ok, en_motor)
need(not puntos["rem137_3_5_racional"]["en_dominio_del_motor"], "TRES_QUINTOS_DENTRO")
need(vals["interior_19_32"][1] and vals["interior_19_32"][2] and B64 - INTERIOR > Fr(6, 1000), "INTERIOR_NO_FACTIBLE")
need(vals["esquina_binary64_0_6"][1] and vals["esquina_binary64_0_6"][2], "ESQUINA_NO_FACTIBLE")
L_int = vals["interior_19_32"][0][0]
L_esq = vals["esquina_binary64_0_6"][0][0]
dominio = {"clave": {"tau_d_upper": "0.6", "tau_f_upper": "0.6", "cerrado": True, "lectura": "Decimal 0.6 = 3/5 en el payload (canon_dec)"},
           "motor": {"bd_bf": "float(v['bar_tau_d']) = binary64(0.6) = %s/%s" % (B64.numerator, B64.denominator),
                     "diferencia_3_5_menos_b64": "%s/%s" % ((TRES_QUINTOS - B64).numerator, (TRES_QUINTOS - B64).denominator),
                     "diferencia_float": float(TRES_QUINTOS - B64), "axes_df": "supremum.axes('df', bd, bf) = ((0, bd), (0, bf))",
                     "consecuencia": "3/5 NO pertenece al dominio que recorre el motor; todo punto del motor (incluido el de su testigo) está en [0, b64(0.6)]² ⊂ [0, 3/5]²"},
           "theta": str(theta), "theta_mayor_que_1": theta > 1, "delta": "1 (z_cost = 1)", "gamma_z_m": "1",
           "derivacion": "reutiliza la derivación simbólica de rem137 (c3_cota_inferior.py, todo F con prior F para z >= 1 con z^θ >= z); "
                         "aquí solo cambian el punto y la aritmética (encierro verificado en vez de Decimal a 60 dígitos)",
           "puntos": puntos, "punto_elegido": "interior_19_32",
           "cota_inferior_verificada_interior": dec(L_int),
           "cota_inferior_verificada_esquina": dec(L_esq)}

# ------------------------------------------------------------------------------------------------- d) cobertura
BANDA = Fr(1, 10 ** 7)
filas = sorted(RESTO["filas"], key=lambda t: Fr(t["v_exacto"]))
need(len(filas) == 40 and all(Fr(t["v_exacto"]) == Fr(float(t["v"])) for t in filas), "RESTO_C3")
paises_celda = sorted({s.split("-")[0] for s in sets_eval})
cob = []
for t in filas:
    v = Fr(t["v_exacto"])
    cob.append({"fila": t["fila"], "run": t["run"], "grupo": t["grupo"], "pais": t["pais"], "v": t["v"], "v_exacto": t["v_exacto"],
                "grupo_compatible": t["grupo"] == "EQ-TECHO-T8-1",
                "garantizada_si_testigo_cumple": t["grupo"] == "EQ-TECHO-T8-1" and v <= L_int - 2 * BANDA,
                "v_menor_o_igual_cota_interior": v <= L_int, "v_menor_o_igual_cota_esquina": v <= L_esq})
gar = [c["fila"] for c in cob if c["garantizada_si_testigo_cumple"]]
cobertura = {"criterio_futuro": ("fila cubierta si v <= C2 - err del techo certificado de la clave (complete, sup_not_attained=false, "
                                 "err <= 1e-7) y la fila es del grupo EQ-TECHO-T8-1 con la autoridad de fuentes extendida; el testigo inferior "
                                 "compatible es el punto τ* del propio techo (lo_s) o el punto interior verificado aquí"),
             "argumento_minimo": ("sup >= L (punto interior verificado) y C2 - err >= sup - 2 err >= L - 2e-7 si err <= 1e-7: toda fila con "
                                  "v <= L - 2e-7 quedaría cubierta por un techo que cumpla la garantía; las demás dependen del C2 real"),
             "cota_L_interior": dominio["cota_inferior_verificada_interior"], "banda": "1e-7", "filas": cob,
             "garantizadas_si_cumple": len(gar), "garantizadas_lista": gar,
             "no_cubribles_por_esta_clave": [c["fila"] for c in cob if not c["v_menor_o_igual_cota_esquina"]],
             "paises_de_los_conjuntos_de_la_celda": paises_celda, "paises_de_las_filas": dict(collections.Counter(t["pais"] for t in filas)),
             "nota": "las cifras son PREVISIÓN; ninguna fila se suma a producción ni a C2 en rem138"}

doc = {"kind": "controles-testigo-alto-rem138", "experimental": True, "productivo": False, "clave": CLAVE, "plan": PLAN,
       "fuentes_autenticadas": AUT, "sellos": SELLOS, "d7": {"arbol": D7T, "manifiesto_sha256": HF(D7 / "d7_manifest.json")},
       "a_pertenencia": pertenencia, "b_identidad": identidad, "c_dominio": dominio, "d_cobertura": cobertura,
       "no_hace": ["importar o ejecutar model/modelos/supremum/encierros", "capture_ceiling, sup_bound, evaluate, bridge, mallas", "enumerar Omega"],
       "fallos": FALLOS, "conforme": not FALLOS, "segundos": round(time.time() - T0, 2)}
with (OUT / "CONTROLES_TESTIGO.json").open("x", encoding="utf-8") as fh:
    fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
print(json.dumps({"conforme": doc["conforme"], "fallos": FALLOS, "plan": plan_regenerado, "unit_ids": pertenencia["unit_ids"],
                  "cota_interior": dominio["cota_inferior_verificada_interior"], "cota_esquina": dominio["cota_inferior_verificada_esquina"],
                  "rem137": puntos["rem137_3_5_racional"]["R_sobre_Bpot"]["lo"], "garantizadas": len(gar),
                  "instalacion_difiere_en": identidad["instalacion_difiere_en"], "segundos": doc["segundos"]}, ensure_ascii=False))
raise SystemExit(0 if doc["conforme"] else 4)
