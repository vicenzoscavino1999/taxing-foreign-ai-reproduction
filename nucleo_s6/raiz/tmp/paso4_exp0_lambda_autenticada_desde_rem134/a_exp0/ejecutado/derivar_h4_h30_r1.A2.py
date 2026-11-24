"""rem134 — PROD4.1-A: las tres comprobaciones residuales de Exp0 sobre la matriz A3 de rem133 (solo lectura salvo <salida>/; sin modelo).
H4  inspección AST de literales de los objetos de §9.3 en el código histórico autenticado de las corridas (núcleo candidato de cada entrega,
    una sola versión por archivo comprobada por sha256) y en los módulos del original que importaban (nacional.py, ejecutar_b.py, d7build del
    productor D7). Clasifica: comparación de dominio/caso límite, valor por defecto, asignación/argumento/dict literal; marca los relevantes.
H30 índice canónico de derivación de la fase D-3 (árbol activo del certificado D3 que fija D7) con las reglas exactas del diseño (§D-3:
    esquema cerrado, conteo, claves, rutas, hashes y bundle hash del informe de fase), más los enlaces D7 → D2/D6/índice de bundles.
R1  cada vinculación declared_scenario de D7 frente a su rango DOCUMENTADO aplicable: formulas.json (soporte primario) con la transformación
    declarada del conjunto, reproducida con primary_supports/transform del d7build histórico (funciones de datos).
Uso: python -B -I -X utf8 derivar_h4_h30_r1.py <raiz> <area> <salida>"""
import ast
import collections
import csv
import hashlib
import json
import re
import sys
import time
from decimal import Decimal
from pathlib import Path

R, A, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
T = R / "tmp"
T0 = time.time()
HF = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()  # noqa: E731
OUT.mkdir(parents=True, exist_ok=False)
FALLOS, AUT = [], {}


def need(t, c):
    if not t:
        FALLOS.append(c)
    return bool(t)


def inv(area):
    p = T / area / "audit/entrega.json"
    return HF(p), json.loads(p.read_bytes())["files"]


P133 = "paso4_exp0_lambda_captura_desde_rem133"
h133, f133 = inv(P133)
need(h133 == "b635d0b31662f6947e8358b10a2fb53885d9a97f9dd66113766462e2ecbb2642", "PARTIDA")
for rel in ("a_exp0/salida_a3/MATRIZ_REVISADA.json", "a_exp0/salida_a3/input_audit_report_v2.json", "a_exp0/salida_a3/UNIVERSOS_POR_CORRIDA.json"):
    need(f133[rel]["sha256"] == HF(T / P133 / rel), "A3:" + rel)
    AUT[rel] = f133[rel]["sha256"]
MAT = {m["requisito"]: m for m in json.loads((T / P133 / "a_exp0/salida_a3/MATRIZ_REVISADA.json").read_bytes())["filas"]}
IAR = json.loads((T / P133 / "a_exp0/salida_a3/input_audit_report_v2.json").read_bytes())["filas"]
UNIV = json.loads((T / P133 / "a_exp0/salida_a3/UNIVERSOS_POR_CORRIDA.json").read_bytes())["corridas"]
D7T = "10a0bd5bb8ea48d54d1bd0916b072afcf8cd5a4eed9c5ec16a90a728f021b739"
D7 = R / "fase2_datos/d7_calibracion/versions" / D7T
d7m = json.loads((D7 / "d7_manifest.json").read_bytes())
D7F = {f["path"]: f["sha256"] for f in d7m["files"]}
for p, h in D7F.items():
    need(HF(D7 / p) == h, "D7:" + p)
DEPS = {d["role"]: d for d in d7m["input_dependencies"]}


def rows(p):
    with open(p, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


# ------------------------------------------------------------------------------------------------- H4
OBJ = {"a": "a", "theta": "θ", "rho": "ρ", "beta_tilde": "β̃", "beta": "β̃", "delta_tilde": "δ̃", "kappa_tilde": "κ̃_0", "kappa0": "κ̃_0", "eta_d": "η_d",
       "eta_f": "η_f", "phi": "φ", "z_m": "z_m", "eta_w": "η_w", "eta_H": "η_H", "s_L_bar": "s̄_L", "s_bar_iva": "s_T^marg", "s_bar_otros_productos": "s_T^marg",
       "s_bar_produccion": "s_T^marg", "pi_iva": "s_T^marg", "pi_otros_productos": "s_T^marg", "pi_produccion": "s_T^marg", "t_F_eff": "t_F,eff", "t_I_eff": "t_I,eff",
       "s_AI": "s_AI", "s_FN": "s_FN", "c_legal": "c_legal", "omega_tail": "ω_tail", "bar_tau_d": "τ̄_d", "bar_tau_f": "τ̄_f", "bar_d": "τ̄_d", "bar_f": "τ̄_f",
       "eps_econ": "ε_econ", "epsilon_econ": "ε_econ", "eps_num": "ε_num", "epsilon_num": "ε_num"}


def nombre(n):
    if isinstance(n, ast.Name):
        return n.id
    if isinstance(n, ast.Attribute):
        return n.attr
    if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) and isinstance(n.slice.value, str):
        return n.slice.value
    return None


def literal(n):
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
        n = n.operand
    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
        return True
    if isinstance(n, ast.Call) and getattr(n.func, "id", getattr(n.func, "attr", "")) in ("Decimal", "Fraction", "F", "float") and n.args \
            and isinstance(n.args[0], ast.Constant) and re.fullmatch(r"-?[0-9.eE/+-]+", str(n.args[0].value)):
        return True
    return False


def escanear(p):
    src = p.read_text(encoding="utf-8")
    tree = ast.parse(src)
    out = []
    for node in ast.walk(tree):
        hits = []
        if isinstance(node, ast.Compare):
            lados = [node.left] + list(node.comparators)
            ids = [nombre(x) for x in lados if nombre(x) in OBJ]
            if ids and any(literal(x) for x in lados):
                hits.append(("comparacion_dominio_o_caso_limite", ids[0]))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            tg = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in tg:
                if nombre(t) in OBJ and node.value is not None and literal(node.value):
                    hits.append(("asignacion_literal", nombre(t)))
        elif isinstance(node, ast.Call):
            for k in node.keywords:
                if k.arg in OBJ and literal(k.value):
                    hits.append(("argumento_literal", k.arg))
        elif isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and k.value in OBJ and literal(v):
                    hits.append(("dict_literal", k.value))
        elif isinstance(node, (ast.FunctionDef, ast.Lambda)):
            args = node.args
            pos = args.args[len(args.args) - len(args.defaults):] if args.defaults else []
            for a_, d in list(zip(pos, args.defaults)) + [(a_, d) for a_, d in zip(args.kwonlyargs, args.kw_defaults) if d is not None]:
                if a_.arg in OBJ and literal(d):
                    hits.append(("valor_por_defecto", a_.arg))
        for clase, ident in hits:
            out.append({"archivo": p.name, "linea": node.lineno, "objeto": OBJ[ident], "identificador": ident, "clase": clase,
                        "codigo": ast.get_source_segment(src, node)[:160] if ast.get_source_segment(src, node) else None})
    return out


ENT = sorted({u["entrega"] for u in UNIV.values()})
versiones = collections.defaultdict(lambda: collections.defaultdict(list))
for ent in ENT:
    _, files = inv(ent)
    for p in sorted((T / ent / "candidato/src/paper2b").glob("*.py")) + sorted((T / ent / "candidato/herramientas/b").glob("*.py")):
        rel = p.relative_to(T / ent).as_posix()
        h = HF(p)
        need(files.get(rel, {}).get("sha256") == h, "NUCLEO_NO_AUTENTICO:%s/%s" % (ent, rel))
        versiones[rel][h].append(ent)
S5TC = R / "fase6_planes/freeze_history/93c625a40772f3d278183cd738f454cc47345c1a52e71dc9f47342352d2aba09/toolchain"
ORIG = {"herramientas/b/nacional.py": R / "herramientas/b/nacional.py", "herramientas/b/ejecutar_b.py": R / "herramientas/b/ejecutar_b.py",
        "herramientas/d7/construir_d7.py (productor D7)": S5TC / "herramientas/d7/construir_d7.py"}
orig_auth = {k: {"sha256": HF(v), "igual_toolchain_S5": HF(v) == HF(S5TC / k.split(" ")[0]) if (S5TC / k.split(" ")[0]).is_file() else None} for k, v in ORIG.items()}
need(orig_auth["herramientas/d7/construir_d7.py (productor D7)"]["sha256"] == d7m["producer_sha256"], "PRODUCTOR_D7")
H4 = []
ref_ent = ENT[0]
for rel, vs in sorted(versiones.items()):
    for h, ents in vs.items():
        for x in escanear(T / ents[0] / rel):
            H4.append(dict(x, ruta=rel, sha256=h, entregas=len(ents)))
for k, p in ORIG.items():
    for x in escanear(p):
        H4.append(dict(x, ruta=k, sha256=orig_auth[k]["sha256"], entregas="original"))
# revisión dirigida de los casos relevantes (no comparaciones): literales de soportes/bloques fuera del registro
txt_d7b = (T / ref_ent / "candidato/src/paper2b/d7build.py").read_text(encoding="utf-8")
blocks = [i for i, l in enumerate(txt_d7b.splitlines(), 1) if re.match(r'^BLOCKS = \{"micro": \("0\.05", "0\.2"\), "macro": \("0\.4", "1"\)\}', l)]
txt_run = (T / ref_ent / "candidato/src/paper2b/run.py").read_text(encoding="utf-8")
umbral = [i for i, l in enumerate(txt_run.splitlines(), 1) if 'Decimal("0.4") <= v <= Decimal("1")' in l or 'v < Decimal("0.3")' in l]
FORM = R / "fase6_planes/integracion_s4/versions/560026466c07259d759cdd435a80e37561b0226228383a5a2c1fef5d501fa4d2/contratos_enmienda/contratos/formulas.json"
need(HF(FORM) == "db828d3c00b2fe09377489007b7a2097288b11ddce5c3630a9ea7174e2ca3ddd", "FORMULAS")
FJ = json.loads(FORM.read_bytes())
ew = FJ["parameters"].get("eta_w", {})
sup_ew = {(r["support_set_id"].rsplit(".", 1)[-1] if r["support_set_id"].count(".") == 1 else None): (r["lower"], r["upper"]) for r in rows(D7 / "support_set.csv")
          if r["parameter_id"] == "eta_w" and r["support_set_id"].count(".") == 1}
tol = [x for x in H4 if x["ruta"] == "herramientas/b/ejecutar_b.py" or x["objeto"] in ("ε_num", "ε_econ")]
# A2 (rem134): anotación DIRIGIDA de cada literal que no es comparación, leída en su contexto del código histórico
ANOT = {("candidato/src/paper2b/model.py", "c_legal"): "valor por defecto del campo State.c_legal = 1.0, igual a la constante institucional fija del registro; "
        "la corrida lo pasa desde D7 (run.py: values['c_legal']) y comprueba c_legal != 1 → no es calibración oculta",
        ("candidato/src/paper2b/modelos.py", "φ@229"): "estado de RELLENO con φ=0.5 para obtener B_pot (que no depende de φ); φ se recorre después como argumento "
        "del motor en la cota por φ → no fija el valor de φ",
        ("candidato/src/paper2b/run.py", "φ@833"): "phi_fiscal: mismo estado de relleno φ=0.5 para B_pot; la partición recorre φ en [0, 1] → no fija φ",
        ("candidato/src/paper2b/modelos.py", "φ@637"): "proveedor SUSTITUTO sintético (SURROGATE_TAG): intercepto de C2 afín en φ=0 → punto de evaluación "
        "matemático de un sustituto, no del modelo teórico certificado"}
for x in H4:
    k = (x["ruta"], x["identificador"]) if x["identificador"] == "c_legal" else (x["ruta"], "%s@%d" % (x["objeto"], x["linea"]))
    if k in ANOT:
        x["anotacion"] = ANOT[k]
        x["clase_final"] = "no_calibracion_oculta"
    elif x["clase"] == "comparacion_dominio_o_caso_limite":
        x["clase_final"] = "comparacion_dominio_o_caso_limite"
    else:
        x["clase_final"] = "sin_anotar"
H4_REVISION = {
    "eta_w_bloques_en_d7build": {"lineas": blocks, "valores_codigo": {"micro": ["0.05", "0.2"], "macro": ["0.4", "1"]},
                                 "formulas_json_eta_w": ew, "soportes_D7_eta_w": sorted({json.dumps(v) for v in sup_ew.values()}),
                                 "lectura": "los soportes de η_w por bloque los fija el PRODUCTOR de D7 desde un literal de código (BLOCKS), no desde formulas.json; "
                                            "D7 los registra (support_set) y las corridas los LEEN de D7: el núcleo de corrida no esconde el valor, pero su origen "
                                            "es código del productor, no el registro documentado"},
    "eta_w_umbral_de_bloque_en_run": {"lineas": umbral, "lectura": "run.py clasifica el bloque micro/macro de η_w con literales: 0.4 y 1 coinciden con "
                                      "el bloque macro registrado (formulas.json primary_blocks y D7); 0.3 NO está registrado: parte el hueco (0.2, 0.4) "
                                      "entre bloques. Caso mínimo: un η_w en (0.2, 0.4) se clasificaría por un literal no registrado. Alcance: ningún soporte "
                                      "registrado tiene valores en ese hueco (micro [0.05,0.2], macro [0.4,1]), así que no cambia ninguna clasificación de "
                                      "las corridas; es contradicción FORMAL con §9.3, sin impacto numérico"},
    "eta_w_bloques_documentados": {"formulas_json_primary_blocks": ew.get("primary_blocks"), "coinciden_con_BLOCKS_del_productor":
                                   ew.get("primary_blocks") == {"micro": [0.05, 0.2], "macro": [0.4, 1]}},
    "tolerancias_eps_num": {"hits": len(tol), "lectura": "las tolerancias numéricas viven en ejecutar_b.TOLERANCES (literal del original) y se fijan en la "
                            "identidad técnica (tolerances_sha256 de cada corrida); el registro D7 no las contiene"}}
cnt = collections.Counter((x["clase"], x["objeto"]) for x in H4)

# ------------------------------------------------------------------------------------------------- H30
CERT3 = R / "fase2_datos/certificados_reuso/CERT-REUSO-D3-A1E-v2.json"
need(HF(CERT3) == DEPS["certificado_D3"]["sha256"], "CERT_D3")
tree3 = json.loads(CERT3.read_bytes())["active_tree_sha256"]
D3 = R / "fase2_datos/d3_universo/versions" / tree3
raw_ix = (D3 / "derivation_manifests_index.json").read_bytes()
ix = json.loads(raw_ix)
fase = rows(D3 / "d3_phase_report.csv")
cw = rows(D3 / "crosswalk_evidence.csv")
canon = json.dumps(ix, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
ents = ix.get("manifests", [])
claves = [(e.get("country_id"), e.get("crosswalk_id"), e.get("mapped_mass_evidence_id")) for e in ents] if isinstance(ents, list) else []
paths_cw = sorted({r.get("derivation_manifest_path") for r in cw if r.get("derivation_manifest_path") not in (None, "", "null")})
H30 = {"arbol_D3_activo": tree3, "certificado_D3": {"ruta": str(CERT3.relative_to(R)), "sha256": HF(CERT3), "igual_dependencia_D7": True},
       "indice": {"ruta": str((D3 / "derivation_manifests_index.json").relative_to(R)), "sha256_bytes": hashlib.sha256(raw_ix).hexdigest(),
                  "sha256_canonico": hashlib.sha256(canon).hexdigest(), "contenido": ix},
       "comprobaciones": {
           "esquema_cerrado": set(ix) == {"schema_version", "manifest_count", "manifests"} and type(ix["schema_version"]) is int and ix["schema_version"] == 1
           and type(ix["manifest_count"]) is int and ix["manifest_count"] >= 0 and isinstance(ix["manifests"], list),
           "conteo_coherente": isinstance(ents, list) and ix.get("manifest_count") == len(ents),
           "entradas_cinco_campos": all(set(e) == {"country_id", "crosswalk_id", "mapped_mass_evidence_id", "relative_path", "sha256"} for e in ents),
           "claves_unicas_y_ordenadas": len(set(claves)) == len(claves) and claves == sorted(claves),
           "rutas_relativas_sin_escape": all(not e["relative_path"].startswith("/") and ".." not in e["relative_path"].split("/") and "\\" not in e["relative_path"] for e in ents),
           "hashes_reproducen": all((D3 / e["relative_path"]).is_file() and HF(D3 / e["relative_path"]) == e["sha256"] for e in ents),
           "evidencia_sin_manifiesto_no_indexado": set(paths_cw) <= {e["relative_path"] for e in ents},
           "fase_una_fila": len(fase) == 1,
           "fase_conteo_igual": len(fase) == 1 and int(fase[0]["derivation_manifest_count"]) == ix.get("manifest_count"),
           "fase_bundle_igual_bytes": len(fase) == 1 and fase[0]["derivation_manifests_bundle_sha256"] in (hashlib.sha256(raw_ix).hexdigest(), hashlib.sha256(canon).hexdigest()),
           "fase_otros_hashes": {k: len(fase) == 1 and fase[0][k + "_sha256"] == HF(D3 / (k + ".csv")) for k in ("universe_crosswalk", "crosswalk_evidence", "firm_universe", "size_distribution", "d3_gate_report")},
           "fase_estado": fase[0]["phase_status"] if fase else None},
       "nota": "índice VACÍO (manifest_count 0) admitido por el diseño; su hash nunca es nulo"}
H30["comprobaciones"]["fase_bundle_es_bytes_del_archivo"] = len(fase) == 1 and fase[0]["derivation_manifests_bundle_sha256"] == hashlib.sha256(raw_ix).hexdigest()
ENL = {}
for role in ("d2_version", "d6_v2_version"):
    d = DEPS[role]
    mp = R / d["path"]
    ok_m = HF(mp) == d["sha256"]
    m = json.loads(mp.read_bytes())
    fl = m.get("files", [])
    malos = [f.get("path", f.get("relative_path")) for f in fl if not (mp.parent / f.get("path", f.get("relative_path"))).is_file()
             or HF(mp.parent / f.get("path", f.get("relative_path"))) != f["sha256"]]
    rutas = [f.get("path", f.get("relative_path")) for f in fl]
    ENL[role] = {"manifiesto": d["path"], "hash_dependencia_ok": ok_m, "archivos": len(fl), "malos": malos, "duplicados": len(rutas) - len(set(rutas)),
                 "rutas_absolutas_o_escape": [r_ for r_ in rutas if r_.startswith("/") or ".." in r_.split("/") or ":" in r_],
                 "arbol_D7_igual_carpeta": d.get("tree_sha256") == mp.parent.name, "arbol_declarado_en_manifiesto": m.get("tree_sha256")}
d = DEPS["ca2_bundles_index"]
ixb = json.loads((R / d["path"]).read_bytes())
refs = []
for b in ixb["bundles"]:
    refs.append(("bundle", b["path"], b["sha256"]))
for k, c in ixb["components"].items():
    refs.append(("componente", c["path"], c["sha256"]))
for pais, cs in ixb["contexts"].items():
    for c in cs:
        refs.append(("contexto", c["path"], c["sha256"]))
mal = [r_ for r_ in refs if not (R / r_[1]).is_file() or HF(R / r_[1]) != r_[2]]
ENL["ca2_bundles_index"] = {"indice": d["path"], "hash_dependencia_ok": HF(R / d["path"]) == d["sha256"], "referencias": len(refs),
                            "por_tipo": dict(collections.Counter(r_[0] for r_ in refs)), "malas": mal[:10], "n_malas": len(mal),
                            "rutas_repetidas_mismo_hash": len(refs) - len({r_[1] for r_ in refs}),
                            "rutas_con_hash_en_conflicto": sorted(p for p in {r_[1] for r_ in refs} if len({r_[2] for r_ in refs if r_[1] == p}) > 1),
                            "nota_repetidas": "un mismo contexto (archivo y hash) compartido por varios países; no es duplicado conflictivo",
                            "evidencia_D7_de_bundles_coincide": all(any(e["source_path"] == b["path"] and e["payload_sha256"] == b["sha256"] for e in rows(D7 / "source_evidence.csv"))
                                                                     for b in ixb["bundles"])}
H30["enlaces_D7_D2_D6_bundles"] = ENL

# ------------------------------------------------------------------------------------------------- R1
SRC = T / ref_ent / "candidato/src"
sys.path[:0] = [str(SRC)]
from paper2b import d7build as D7B  # noqa: E402
from paper2b.supports import transform  # noqa: E402
SS = {r["support_set_id"]: r for r in rows(D7 / "support_sets.csv")}
SUP = {r["support_id"]: r for r in rows(D7 / "support_set.csv")}
BND = [r for r in rows(D7 / "parameter_bindings.csv") if r["value_type"] == "declared_scenario"]
STRESS = getattr(D7B, "STRESS", {})


def base_de(s):
    while SS[s]["parent_support_set_id"]:
        s = SS[s]["parent_support_set_id"]
    return s


def norm(x):
    return [Decimal(repr(v)) if isinstance(v, float) else Decimal(str(v)) for v in x]


R1 = []
for b in BND:
    s, pid = b["support_set_id"], b["parameter_id"]
    row = SUP.get(b["support_id"])
    block = base_de(s).rsplit(".", 1)[-1]
    prim = D7B.primary_supports(FJ, block).get(pid)
    kind, tr = SS[s]["kind"], SS[s]["transformation_id"] or None
    if not row or not prim:
        R1.append({"binding_id": b["binding_id"], "parametro": pid, "conjunto": s, "estado": "desconocido", "motivo": "sin soporte D7 o sin rango documentado"})
        continue
    var = next((v for v in prim if "SUP:%s:%s:%s" % (s, pid, v["variant_id"]) == b["support_id"]), None)
    if var is None:
        R1.append({"binding_id": b["binding_id"], "parametro": pid, "conjunto": s, "estado": "desconocido", "motivo": "variante del binding no documentada"})
        continue
    esp = transform(pid, dict(var), tr if kind in ("coordination", "domain_stress") else None, STRESS.get(s.rsplit(".", 1)[-1]))
    real = {"lower": Decimal(row["lower"]) if row["lower"] else None, "upper": Decimal(row["upper"]) if row["upper"] else None,
            "lower_closed": row["lower_closed"] == "true", "upper_closed": row["upper_closed"] == "true", "kind": row["domain_kind"],
            "nodes": norm(json.loads(row["level0_nodes"])) if row["level0_nodes"] else []}
    doc = {"lower": Decimal(str(esp["lower"])), "upper": Decimal(str(esp["upper"])), "lower_closed": bool(esp["lower_closed"]),
           "upper_closed": bool(esp["upper_closed"]), "kind": esp["domain_kind"], "nodes": [Decimal(str(v)) for v in esp["level0_nodes"]]}
    dentro = all((doc["lower"] < v or (doc["lower_closed"] and v == doc["lower"])) and (v < doc["upper"] or (doc["upper_closed"] and v == doc["upper"])) for v in real["nodes"])
    igual = real == doc
    fuente = FJ["parameters"].get(pid, {}).get("source")
    R1.append({"binding_id": b["binding_id"], "parametro": pid, "conjunto": s, "capa": kind, "transformacion": tr,
               "estado": "coincide_con_rango_documentado" if igual else ("dentro_del_rango_documentado" if dentro else "fuera_de_rango_documentado"),
               "fuente_documental": fuente, "documentado": {k: str(v) if not isinstance(v, list) else [str(x) for x in v] for k, v in doc.items()},
               "d7": {k: str(v) if not isinstance(v, list) else [str(x) for x in v] for k, v in real.items()}})
r1c = collections.Counter(x["estado"] for x in R1)

# ------------------------------------------------------------------------------------------------- matriz v4
REV = {k: dict(v) for k, v in MAT.items()}
h4_rel = [x for x in H4 if x["clase"] != "comparacion_dominio_o_caso_limite"]
sin_anotar = [x for x in H4 if x["clase_final"] == "sin_anotar"]
need(not sin_anotar, "H4_SIN_ANOTAR:%s" % [(x["ruta"], x["linea"]) for x in sin_anotar])
REV["H4"].update(clase_evidencia="retrospectiva_comprobada_con_hallazgo", resultado="sin_calibracion_oculta; hallazgo_formal_sin_impacto_numerico",
                 evidencia="%d literales de objetos §9.3 en el núcleo histórico (una versión): %d comparaciones de dominio/caso límite y %d anotados como no "
                           "calibración (c_legal por defecto = constante fija; φ de relleno para B_pot; intercepto de un sustituto sintético). Hallazgo "
                           "formal: umbrales literales de bloque de η_w en run.py (0.4/1 registrados; 0.3 no registrado, en el hueco sin soporte) y "
                           "BLOCKS del productor D7 que duplica primary_blocks de formulas.json. ε_num/ε_econ no se identifican por nombre: las "
                           "tolerancias se fijan por la identidad técnica (tolerances_sha256)" % (len(H4), sum(x["clase_final"] == "comparacion_dominio_o_caso_limite" for x in H4),
                                                                                                 sum(x["clase_final"] == "no_calibracion_oculta" for x in H4)),
                 accion_minima="decisión del revisor: si los literales de bloque/tolerancia, coincidentes con el registro y fijados por hash, satisfacen §9.3 o exigen leerlos del registro en una sucesión de código")
okh30 = all(v is True for k, v in H30["comprobaciones"].items() if isinstance(v, bool)) and all(H30["comprobaciones"]["fase_otros_hashes"].values()) \
    and all(e["hash_dependencia_ok"] and not e.get("malos") and not e.get("n_malas") for e in ENL.values())
REV["H30"].update(clase_evidencia="contemporanea" if okh30 else "pendiente_tecnica", resultado="comprobada" if okh30 else "falla",
                  evidencia="índice D-3 %s: %s; enlaces D2/D6/bundles %s" % (tree3[:12], {k: v for k, v in H30["comprobaciones"].items() if k != "fase_otros_hashes"},
                                                                             {k: (v["hash_dependencia_ok"], v.get("archivos", v.get("referencias"))) for k, v in ENL.items()}),
                  accion_minima=None if okh30 else "revisar los fallos listados en H30_INDICE_DERIVACION.json")
okr1 = r1c.get("fuera_de_rango_documentado", 0) == 0 and r1c.get("desconocido", 0) == 0
REV["R1"].update(clase_evidencia="retrospectiva_comprobada" if okr1 else "pendiente_tecnica", resultado="comprobada" if okr1 else "parcial",
                 evidencia="%d vinculaciones declared_scenario: %s (rango documentado = formulas.json + transformación declarada del conjunto)" % (len(R1), dict(r1c)),
                 accion_minima=None if okr1 else "revisar fuera de rango/desconocidos en R1_ESCENARIOS.json")
IAR2 = []
for f in IAR:
    x = dict(f)
    g = f["gate_id"]
    if g in ("H4", "H30", "R1"):
        rv = REV[g]
        x["clase_evidencia_v3"], x["resultado_v3"] = rv["clase_evidencia"], rv["resultado"]
        x["note"] = rv["evidencia"][:400]
        if g == "H30" and okh30:
            x["decision"], x["origen"] = "pass_contemporaneo_datos", dict(f["origen"], decision="índice D-3 y manifiestos fijados por D7 (rem134)")
        if g == "R1" and okr1:
            x["decision"] = "pass_retrospectivo_datos"
        if g == "H4":
            x["decision"] = None
    IAR2.append(x)


def esc(rel, obj):
    with (OUT / rel).open("x", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False, indent=1, default=str) + "\n")


esc("H4_LITERALES.json", {"kind": "h4-literales-rem134", "objetos_9_3": sorted(set(OBJ.values())), "versiones_por_archivo": {k: len(v) for k, v in versiones.items()},
                          "originales": orig_auth, "conteo": {"%s|%s" % k: n for k, n in sorted(cnt.items())}, "revision": H4_REVISION, "hallazgos": H4})
esc("H30_INDICE_DERIVACION.json", H30)
esc("R1_ESCENARIOS.json", {"kind": "r1-escenarios-rem134", "conteo": dict(r1c), "filas": R1})
esc("MATRIZ_REVISADA_v4.json", {"kind": "matriz-exp0-v4-rem134", "base": "A3 rem133 (%s)" % AUT["a_exp0/salida_a3/MATRIZ_REVISADA.json"][:16], "filas": list(REV.values())})
esc("input_audit_report_v4.json", {"kind": "input-audit-report-v4-rem134", "filas": IAR2})
RES = {"segundos": round(time.time() - T0, 1), "fallos": FALLOS, "conforme": not FALLOS, "H4": {"total": len(H4), "por_clase": dict(collections.Counter(x["clase"] for x in H4)),
       "versiones_unicas": all(len(v) == 1 for v in versiones.values()), "relevantes_no_comparacion": len(h4_rel)}, "H30": {"ok": okh30, "comprobaciones": H30["comprobaciones"],
       "enlaces": {k: {x: v[x] for x in v if x not in ("malas",)} for k, v in ENL.items()}}, "R1": dict(r1c), "matriz": dict(collections.Counter(v["clase_evidencia"] for v in REV.values()))}
esc("RESUMEN_A_rem134.json", RES)
print(json.dumps(RES, ensure_ascii=False, indent=1, default=str))
raise SystemExit(0 if not FALLOS else 4)
