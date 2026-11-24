"""D7 (bloque 2): productor completo del registro, soportes, fórmulas, restricciones, escenarios, dominios fiscales,
procedencias y manifiesto del catálogo CA2-3 (CONTRATOS_D7_B_D8.md).

Entradas autenticadas por selección explícita (nunca «el último activo»):
- autoridad consumidora (herramientas/bloque2/autoridad.py): S3 vigente RECHAZA; S4 sucesora con recibo del autor;
- contratos: manifiesto normativo eda3d6e5… de la versión S3 instalada (catálogo, formulas.json, claves);
- D2 árbol f9d42072… (verify_active con la autoridad bajo la que se emitió: S3 como antecedente);
- D6 v2 árbol b10f1296… (verify_active con los cuatro casos preregistrados);
- D3-D5 por sus certificados de reutilización emitidos bajo S3; D4 model_case_map y matriz por hash;
- grilla externa b94b9eed… y evidencia D_ME = 0 (documentos del paquete congelado);
- PRE-D7-A v2: inventario y comparabilidad recomputados y comparados con las huellas fijadas por la autoridad;
- bundles CA2 1.5 por índice 90776743… (vectores publicados; vía condicional E1/E2).
Sucesora S5 (bloque 3, B3-5, candidata): D2, D6 v2 e índice de bundles son las versiones SUCESORAS verificadas por la
autoridad (idénticas a su adopción; ninguna constante de este módulo las sustituye); tax_rate_inputs desde el mapeo A6
solo si S5 lo aprueba; G13 por caso con requisitos técnicos y de datos y decisión explícita (herramientas/s5/elegibilidad.py).
No evalúa R ni C_2 (declaraciones con result_binding); no ejecuta el modelo; no promueve punteros sin aprobación.

CLI:
  python herramientas/d7/construir_d7.py verificar-autoridad --autoridad s3|s4|s5 --policy … --receipt … --author …
  python herramientas/d7/construir_d7.py construir --autoridad s4|s5 … --d2-tree … --d6-tree … --cases … --salida <dir>
  python herramientas/d7/construir_d7.py verificar --producto <dir>/versions/<tree> --tree <tree>
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from paper2b import d7build as DB  # noqa: E402
from paper2b import tables as T  # noqa: E402
from paper2b.keys import H, canon  # noqa: E402
from paper2b.numeric import canon_dec  # noqa: E402
from herramientas.bloque2 import autoridad as A  # noqa: E402
from herramientas.bloque2 import familias as FAM  # noqa: E402

D2_TREE = "f9d42072e07dbce5fabb92a4e183bb3390a981318e3a29f0906e8fe990a589c8"
D6_TREE = "b10f1296226dc94969fa5d14468e8a4fd5c61858e1687e0c2609c66545b60e31"
GRID = "fase5_cuantificacion/extraccion_grilla/grilla_efectiva.csv"
GRID_SHA = "b94b9eedeea87d08071366e2bd8a5b7cd9662ce6f9fd9d7bee42848d6c4c5f90"
DME_DOC = "fase5_cuantificacion/MANIFIESTO_ENVOLVENTE.md"
BUNDLE_INDEX = "fase2_datos/ca2_bundles/indice_bundles_1_5.json"
BUNDLE_INDEX_SHA = "907767435de0355475e035d14a175d7c42b87337d108753137bd46790652c8e5"
THEORY = "fase4_teoria/baseline_model_v2_2.md"
CASES = ["PREG-COL-E2-2023", "PREG-COMPARACION-E1", "PREG-PER-APLICACION-E0E3", "PREG-PER-APLICACION-E1"]
PRE_D7_A_PINS = {"inventory_sha256": "8c85db58ee33ab70d0b7a5c411e3cc42773cdf0161c12e1a92142afdbff0127d",
                 "comparability_sha256": "2f001377a6273395a7d6d0f5bd64cab6a0797a6a78d644c26773b9c8dce45a35"}


class D7Error(RuntimeError):
    pass


def need(test, code):
    if not test:
        raise D7Error(code)


def sha(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()


def frac(obj) -> Fraction:
    if isinstance(obj, str):
        obj = json.loads(obj)
    return Fraction(int(obj["numerator"]), int(obj["denominator"]))


def read_csv(path: Path) -> list[dict]:
    return list(csv.DictReader(io.StringIO(path.read_bytes().decode("utf-8"), newline="")))


def contracts_for(root: Path, authority: A.AuthorityContext):
    from herramientas.s3.validadores.core import Contracts
    return Contracts.load(Path(root) / authority.contract_root, authority.contract_sha256)


def evidence(eid, source_id, path, payload, locator, year, vintage, unit, universe, ident, target, use, transport,
             precision=None, multiplier="1"):
    return {"evidence_id": eid, "source_id": source_id, "source_path": path, "payload_sha256": payload,
            "source_locator": locator, "source_year": year, "source_vintage": vintage, "unit": unit, "multiplier": multiplier,
            "universe": universe, "identified_object": ident, "target_object": target, "permitted_use": use,
            "transport_status": transport, "precision_evidence_id": precision}


# ------------------------------------------------------------------------------------- mundo nacional (lectura)
def national_world(root: Path, authority: A.AuthorityContext, *, d2_tree: str, d6_tree: str, cases: list[str]) -> dict:
    """Lee y autentica todos los insumos nacionales. Solo lectura."""
    root = Path(root)
    from herramientas.nacionales import construir_d2
    from herramientas.d6 import construir_d6_v2 as D6
    from herramientas.reuso import certificados
    prod = authority.products_authority
    need(sorted(cases) == sorted(CASES), "D7_CASES_EXACT")
    succ = authority.succession
    if succ:                                   # S5: versiones sucesoras verificadas por la autoridad (no constantes)
        pr = succ["productos"]
        need(d2_tree == succ["adopcion"]["d2_tree_sha256"] == pr["d2"]["tree_sha256"], "D7_D2_TREE_NOT_ADOPTED_BY_S5")
        need(d6_tree == pr["d6"]["tree_sha256"], "D7_D6_TREE_NOT_PUBLISHED_UNDER_S5")
        d2, d6 = dict(pr["d2"]), dict(pr["d6"])
        index_rel, index_sha = pr["bundles"]["index_path"], pr["bundles"]["index_sha256"]
    else:
        need(d2_tree == D2_TREE and d6_tree == D6_TREE, "D7_PRODUCT_VERSION_NOT_AUTHORIZED_BY_" + authority.kind.upper())
        d2 = construir_d2.verify_active(root, expected_tree=d2_tree, s3=prod)
        d6 = D6.verify_active(root, s3=prod, d2_tree=d2_tree, cases=sorted(cases))
        index_rel, index_sha = BUNDLE_INDEX, BUNDLE_INDEX_SHA
    need(d6["tree_sha256"] == d6_tree, "D7_D6_TREE_SELECTION")
    certs = certificados.verify(root, authority=prod)
    need(sorted(certs) == ["D3", "D4", "D5"], "D7_REUSE_CERTIFICATES")
    pre = Path(authority.installed_prefix)
    reg_raw = (root / pre / "contratos_adicionales/REGISTRO_CASOS_A1E_V2.json").read_bytes()
    formulas_raw = (root / authority.contract_root / "contratos/formulas.json").read_bytes()
    catalog_raw = (root / authority.contract_root / "contratos/catalogo_contratos.json").read_bytes()
    registry = json.loads(reg_raw)
    d2v = root / "fase2_datos/d2_cuentas_nacionales/versions" / d2_tree
    d6v = root / "fase2_datos/d6_tax_shares_v2/versions" / d6_tree
    files = {"d2_primary": d2v / "labor_income_shares_candidato.csv", "d2_hist": d2v / "labor_income_shares_sensitivity_candidato.csv",
             "d2_precision": d2v / "precision_evidence_candidato.csv", "d2_domains": d2v / "dominios_candidatos.json",
             "d2_manifest": d2v / "d2_manifest.json", "d6_tax": d6v / "tax_shares_marg.csv", "d6_obs": d6v / "sna_observations.csv",
             "d6_der": d6v / "sna_derivations.csv", "d6_manifest": d6v / "d6_manifest.json"}
    d2_manifest = json.loads(files["d2_manifest"].read_bytes())
    listed = {e["path"]: e["sha256"] for e in d2_manifest["files"]}
    for key in ("d2_primary", "d2_hist", "d2_precision", "d2_domains"):
        need(listed.get(files[key].name) == sha(files[key].read_bytes()), "D7_D2_FILE_NOT_IN_MANIFEST:" + key)
    d6_manifest = json.loads(files["d6_manifest"].read_bytes())
    d6_listed = {e.get("path", e.get("relative_path")): e["sha256"] for e in d6_manifest["files"]}
    for key in ("d6_tax", "d6_obs", "d6_der"):
        need(d6_listed.get(files[key].name) == sha(files[key].read_bytes()), "D7_D6_FILE_NOT_IN_MANIFEST:" + key)
    grid_raw = (root / GRID).read_bytes()
    need(sha(grid_raw) == GRID_SHA, "D7_GRID_HASH")
    idx_raw = (root / index_rel).read_bytes()
    need(sha(idx_raw) == index_sha, "D7_BUNDLE_INDEX_HASH")
    bundles = json.loads(idx_raw)
    need(certs["D4"]["tree_sha256"] == bundles["d4"]["tree_sha256"], "D7_D4_TREE_CERTIFIED_VS_BUNDLES")
    d4v = root / "fase2_datos/d4_disponibilidad/versions" / bundles["d4"]["tree_sha256"]
    need(sha((d4v / "model_case_map.csv").read_bytes()) == bundles["d4"]["model_case_map_sha256"], "D7_D4_CASE_MAP")
    need(sha((d4v / "availability_matrix.csv").read_bytes()) == bundles["d4"]["availability_matrix_sha256"], "D7_D4_MATRIX")
    pre_d7a = pre_d7_a_rows(root, authority)
    world = {"root": root, "registry": registry, "registry_raw": reg_raw, "formulas": json.loads(formulas_raw),
             "ca2_policy": json.loads(catalog_raw)["ca2"],
             "formulas_raw": formulas_raw, "catalog_raw": catalog_raw, "d2": d2, "d6": dict(d6, tree=d6_tree),
             "d2_files": files, "certs": certs, "grid_raw": grid_raw, "bundles": bundles, "bundle_index_raw": idx_raw,
             "versions": {"d2_tree": d2_tree, "d6_tree": d6_tree, "bundle_index": index_rel, "bundle_index_sha256": index_sha},
             "d4": {"tree": bundles["d4"]["tree_sha256"], "dir": d4v, "model_case_map": read_csv(d4v / "model_case_map.csv"),
                    "matrix_sha256": bundles["d4"]["availability_matrix_sha256"]},
             "pre_d7_a": pre_d7a, "data_class": "national"}
    world["national"], world["evidence"] = national_inputs(world, authority)
    world["tax_rates"] = statutory_rates(root, world, authority)
    world["authority_row"] = authority.row()
    return world


def pre_d7_a_rows(root: Path, authority: A.AuthorityContext) -> dict:
    """Recomputa inventario y comparabilidad PRE-D7-A (v1 intacta) y exige las huellas fijadas por la autoridad."""
    sys.path.insert(0, str(Path(root) / "herramientas/d7"))
    import preparar_d7_a as V1
    from herramientas.d7 import preparar_d7_a_v2 as V2
    plan_rows = V1._parse_authoritative_rows((Path(root) / V2.TABLE_PLAN).read_text(encoding="utf-8"))
    inventory, comparability, missing = V1._build_rows(Path(root), plan_rows)
    V1._validate_rows(inventory, comparability)
    inv_bytes = V1._csv_bytes(V1.INVENTORY_FIELDS, inventory, "global_evidence_id")
    cmp_bytes = V1._csv_bytes(V1.COMPARABILITY_FIELDS, comparability, "comparability_id")
    pins = dict(PRE_D7_A_PINS, **{k: v for k, v in authority.pins.items() if k in PRE_D7_A_PINS})
    need(sha(inv_bytes) == pins["inventory_sha256"] and sha(cmp_bytes) == pins["comparability_sha256"], "D7_PRE_D7_A_PINS")
    need(not missing, "D7_PRE_D7_A_MISSING_PDFS")
    return {"inventory": inventory, "comparability": comparability, "inventory_sha256": sha(inv_bytes),
            "comparability_sha256": sha(cmp_bytes)}


def _bundle_tables(world, preg):
    b = next(x for x in world["bundles"]["bundles"] if x["preregistration_id"] == preg)
    raw = (world["root"] / b["path"]).read_bytes()
    need(sha(raw) == b["sha256"], "D7_BUNDLE_HASH:" + preg)
    return b, json.loads(raw)


def national_inputs(world, authority):
    """Por (preregistro, edición, país): s_L_bar, tres shares D6 exactos, filas D6 y grupo de primitivas compartidas."""
    root = world["root"]
    f = world["d2_files"]
    d2p = {(r["country_id"], int(r["observation_year"])): r for r in read_csv(f["d2_primary"])}
    d2h = {(r["country_id"], int(r["observation_year"])): r for r in read_csv(f["d2_hist"])}
    tax = read_csv(f["d6_tax"])
    obs = {r["observation_id"]: r for r in read_csv(f["d6_obs"])}
    der = {r["derivation_id"]: r for r in read_csv(f["d6_der"])}
    rel = lambda p: p.relative_to(root).as_posix()
    ev = []
    add = ev.append
    add(evidence("EV.REGISTRY", "A1-E-v2", authority.installed_prefix + "contratos_adicionales/REGISTRO_CASOS_A1E_V2.json",
                 sha(world["registry_raw"]), "entries", 2023, "A1-E-v2", "none", "casos preregistrados", "casos, miembros, años",
                 "universo de claims", "formula_input", "not_applicable"))
    add(evidence("EV.FORMULAS", "formulas.json", authority.contract_root + "contratos/formulas.json", sha(world["formulas_raw"]),
                 "parameters;formulas;transformations;constraints", 2023, "contract-eda3d6e5", "none", "contrato normativo",
                 "soportes y fórmulas", "D7 registry/support_set", "formula_input", "not_applicable"))
    add(evidence("EV.CATALOG", "catalogo_contratos.json", authority.contract_root + "contratos/catalogo_contratos.json",
                 sha(world["catalog_raw"]), "tables", 2023, "integrated-ca2-4-candidato", "none", "contrato normativo", "esquemas",
                 "tablas D7/B/D8", "formula_input", "not_applicable"))
    add(evidence("EV.GRID", "grilla_efectiva", GRID, GRID_SHA, "1200 celdas; 15 columnas", 2034, "official_4c_tierA_baseline_official_v2",
                 "share_GDP", "requerimiento externo por país/política/régimen/base/xi", "Q (cotas del crosswalk)", "K_comp_1",
                 "measurement", "direct_verified"))
    add(evidence("EV.DME", "MANIFIESTO_ENVOLVENTE", DME_DOC, sha((root / DME_DOC).read_bytes()), "D6: D^ME=0 en toda la grilla",
                 2034, "2026-07-26", "share_GDP", "salidas fiscal_space del paquete compañero", "D_ME=0", "DME_gAI",
                 "measurement", "direct_verified"))
    add(evidence("EV.CROSSWALK", "MANIFIESTO_ENVOLVENTE", DME_DOC, sha((root / DME_DOC).read_bytes()), "D2: dos cotas del crosswalk",
                 2034, "2026-07-26", "none", "partición de F_fix", "sin_addback/addback_completo", "bound_variant",
                 "formula_input", "not_applicable"))
    d4 = world["d4"]
    add(evidence("EV.D4.MAP", "D4", rel(d4["dir"] / "model_case_map.csv"), sha((d4["dir"] / "model_case_map.csv").read_bytes()),
                 "model_case_map", 2023, d4["tree"], "none", "pares fuente-residencia (V5)", "menús j_d/j_f/j_df por caso",
                 "availability_case_id", "formula_input", "not_applicable"))
    add(evidence("EV.D4.MATRIX", "D4", rel(d4["dir"] / "availability_matrix.csv"), d4["matrix_sha256"], "availability_matrix", 2023,
                 d4["tree"], "none", "pares fuente-residencia (V5)", "16 pares inciertos", "availability_matrix_hash",
                 "formula_input", "not_applicable"))
    for key in ("D3", "D5"):
        c = world["certs"][key]
        add(evidence(f"EV.{key}", key, c.get("path", f"fase2_datos/certificados_reuso/CERT-REUSO-{key}-A1E-v2.json"),
                     c["certificate_sha256"], "certificado de reutilización", 2023, "A1E-v2", "none",
                     "limitación aceptada (M3/establecimientos)" if key == "D3" else "limitación aceptada (sin Ptarget)",
                     "limitación tipada", "no consumido numéricamente", "plausibility_only", "not_applicable"))
    for inv, cmpr in zip(sorted(world["pre_d7_a"]["inventory"], key=lambda r: r["global_evidence_id"]),
                         sorted(world["pre_d7_a"]["comparability"], key=lambda r: r["global_evidence_id"])):
        rejected = cmpr["direct_transport_status"] == "rejected"
        add(evidence(f"EV.PRED7A.{inv['global_evidence_id']}", inv["source_id"], inv["source_artifact_relative_path"],
                     inv["source_artifact_sha256"], cmpr["comparability_id"], 2023, "PRE-D7-A v2", "none",
                     cmpr["source_geography"] + " / " + cmpr["source_population_unit"], cmpr["identified_object"],
                     cmpr["target_object"], "rejected" if rejected else "plausibility_only", "rejected" if rejected else "limited"))
    national = {}
    domains = json.loads(f["d2_domains"].read_bytes())
    for entry in world["registry"]["entries"]:
        preg = entry["preregistration_id"]
        bmeta, btab = _bundle_tables(world, preg)
        vecs = {(v["family"], v["country_id"], v["observation_year"], v["source_id"]): v for v in btab["ca2_vectors"]}
        problems = [p for fam, c, y, spec in DB.registry_vector_specs(entry)
                    for p in DB.check_vector(vecs.get((fam, c, y, spec["source_id"])), fam, c, y, spec, world["ca2_policy"])]
        need(not problems, "D7_VECTOR_R1_R2:" + preg + ":" + ";".join(problems[:5]))
        add(evidence(f"EV.BUNDLE.{preg}", "ca2_bundle", bmeta["path"], bmeta["sha256"], "ca2_vectors;ca2_members;ca2_cases", 2023,
                     "CA2-3", "none", "vectores publicados completos (vía condicional)", "vectores D2/D6", "estado nacional E1/E2",
                     "measurement", "direct_verified"))
        strict = entry["scenarios"] in (["E0", "E3"], ["E3", "E0"])
        for edition in DB.editions(entry):
            ed_key = edition or "pub"
            for c in sorted(entry["country_set"]):
                if edition:
                    rev = next(r for r in entry["revisions"][c] if r["label"] == edition)
                    d6_edition = rev["D6"]["source_id"]
                else:
                    d6_edition = entry["vectors"][c]["D6"]["source_id"]
                rows = [r for r in tax if r["preregistration_id"] == preg and r["country_id"] == c and r["edition"] == d6_edition]
                need(len(rows) == 3, f"D7_D6_ROWS:{preg}:{c}:{d6_edition}")
                d6_rows, shares, group = {}, {}, []
                for r in rows:
                    comp = r["component_id"]
                    exact = frac(r["share_exact_json"])
                    eid = f"EV.D6.{preg}.{c}.{d6_edition}.{comp}"
                    prec = None
                    if strict:
                        need(r["strict_pass"] == "true" and r["precision_asserted"] == "true", "D7_STRICT_PRECISION:" + eid)
                        lo, hi = Fraction(r["share_low_exact"]), Fraction(r["share_high_exact"])
                        prec = f"PREC.D6.{c}.{r['precision_receipt_sha256'][:16]}"
                    else:
                        lo = hi = exact
                        prec = f"CA2COND.{preg}.{c}.{ed_key}"
                    add(evidence(eid, r["source_snapshot_id"][:16], rel(f["d6_tax"]), sha(f["d6_tax"].read_bytes()),
                                 f"tax_share_row_fk={preg}:{c}:{d6_edition}:{comp}", 2023, r["source_vintage"], "share_GDP",
                                 "economía nacional completa", f"s_bar_{comp} = {r['derivation_id']}", DB.COMPONENTS[comp],
                                 "measurement", "direct_verified", prec))
                    d6_rows[comp] = {"row_id": f"{preg}:{c}:{d6_edition}:{comp}", "low": lo, "high": hi, "evidence_id": eid}
                    shares[DB.COMPONENTS[comp]] = {"value": exact, "exact": exact, "evidence_id": eid}
                    d = der[r["derivation_id"]]
                    ids = json.loads(d["input_observation_ids_json"]) + [d["denominator_observation_id"]]
                    for oid in ids:
                        o = obs[oid]
                        if not any(m["primitive_id"] == oid for m in group):
                            group.append({"d6_tree_sha256": world["d6"]["tree"], "primitive_id": oid,
                                          "source_path": rel(f["d6_obs"]), "source_locator": o["source_row_selector"],
                                          "source_sha256": o["source_snapshot_id"], "unit": o["unit"]})
                group.sort(key=lambda m: m["primitive_id"])
                # s_L_bar: D2 aprobado (propio PIB); edición E2 2024p desde el vector publicado del bundle autenticado
                if edition and d6_edition != entry["revisions"][c][0]["D6"]["source_id"]:
                    members = {m["concept"]: Fraction(m["value_literal"]) for m in btab["ca2_members"]
                               if m["vector_id"] == f"{c}_D2_2023_{d6_edition}"}
                    sL = members["COE"] / members["PIB"]
                    seid = f"EV.D2.{c}.2023.{d6_edition}"
                    add(evidence(seid, d6_edition, bmeta["path"], bmeta["sha256"], f"ca2_members:{c}_D2_2023_{d6_edition}:COE/PIB",
                                 2023, rev["D2"]["2023"]["source_vintage"], "share_GDP", "economía nacional completa",
                                 "s_L_bar = COE/PIB", "s_L_bar", "measurement", "direct_verified", f"CA2COND.{preg}.{c}.{ed_key}"))
                else:
                    row = d2p[(c, 2023)]
                    sL = frac(row["coe_gdp_exact"])
                    seid = f"EV.D2.{c}.2023"
                    if not any(e["evidence_id"] == seid for e in ev):
                        add(evidence(seid, row["source_id"], rel(f["d2_primary"]), sha(f["d2_primary"].read_bytes()),
                                     f"country_id={c};observation_year=2023", 2023, row["source_vintage"], "share_GDP",
                                     "economía nacional completa (remuneración doméstica)", "s_L_bar = COE/PIB", "s_L_bar",
                                     "measurement", "direct_verified",
                                     f"PRECSET.{c}.2023" if row["precision_basis"] == "source_declared_rounding_interval" else f"CA2COND.{c}.2023"))
                shares["s_L_bar"] = {"value": sL, "exact": sL, "evidence_id": seid}
                hist = {}
                for y in entry["claims"].get("historical_anchor", []):
                    if y == 2023:
                        continue
                    hrow = d2h[(c, y)]
                    heid = f"EV.D2.{c}.{y}"
                    if not any(e["evidence_id"] == heid for e in ev):
                        add(evidence(heid, hrow["source_id"], rel(f["d2_hist"]), sha(f["d2_hist"].read_bytes()),
                                     f"country_id={c};observation_year={y}", y, hrow["source_vintage"], "share_GDP",
                                     "economía nacional completa", "s_L_bar ancla histórica (D6 2023 fijo)", "s_L_bar",
                                     "measurement", "direct_verified", f"CA2COND.{c}.{y}"))
                    hist[y] = {"value": frac(hrow["coe_gdp_exact"]), "evidence_id": heid}
                joint = None
                if strict:
                    view = domains["views"][f"{c}_2023"]
                    joint = {"view": f"{c}_2023", "primitive_domains": view["primitive_domains"],
                             "terms": {"s_L_bar": view["derived"]["COE"]["terms"], "s_bar_iva": view["derived"]["VAT"]["terms"],
                                       "s_bar_otros_productos": view["derived"]["OTHER_PRODUCTS"]["terms"],
                                       "s_bar_produccion": view["derived"]["PRODUCTION"]["terms"]},
                             "denominator": view["derived"]["PIB"]["terms"][0][0], "path": rel(f["d2_domains"]),
                             "sha256": sha(f["d2_domains"].read_bytes())}
                    if not any(e["evidence_id"] == f"EV.JOINT.{c}.2023" for e in ev):
                        add(evidence(f"EV.JOINT.{c}.2023", "D2_domains", rel(f["d2_domains"]), sha(f["d2_domains"].read_bytes()),
                                     f"views.{c}_2023", 2023, view["source_vintage"], "national_currency_million",
                                     "dominio conjunto de primitivas compartidas", "caja de publicación (media unidad)",
                                     "estados nacionales E0/E3", "measurement", "direct_verified", f"PRECSET.{c}.2023"))
                        add(evidence(f"EV.PREC.{c}.2023", "D2_precision", rel(f["d2_precision"]), sha(f["d2_precision"].read_bytes()),
                                     f"source_snapshot_id={view['snapshot_sha256']}", 2023, view["source_vintage"],
                                     "national_currency_million", "precisión de publicación acreditada", "reglas por selector",
                                     "precisión E0/E3", "measurement", "direct_verified", f"PRECSET.{c}.2023"))
                national[(preg, ed_key, c)] = dict(shares, d6_rows=d6_rows, primitive_group=group, historical=hist,
                                                   joint=joint, strict=strict, d6_edition=d6_edition)
    ev.sort(key=lambda e: e["evidence_id"])
    return national, ev


def statutory_rates(root: Path, world: dict, authority: A.AuthorityContext | None = None) -> list:
    """A6: sin mapeo verificado (selector, régimen, vigencia, unidad) la sección estatutaria queda BLOQUEADA.
    Con S5: filas desde el mapeo A6 instalado, `verified` solo si la autoridad lo aprueba (herramientas/s5/a6.py)."""
    if authority is not None and authority.succession:
        from herramientas.s5 import a6 as A6
        return A6.filas(root, authority, world, evidence)
    rows = []
    acq = read_csv(root / "fase2_datos/acquisition_manifest.csv")
    countries = sorted({c for e in world["registry"]["entries"] for c in e["country_set"]})
    for c in countries:
        cands = [r for r in acq if r["dataset_id"] == "LEGISLACION_CIT_A6" and r["country"] == c and r["access_result"] == "obtenido"]
        need(len(cands) == 1, "D7_A6_ACQUISITION:" + c)
        eid = f"EV.A6.{c}"
        path, payload = cands[0]["raw_path"], cands[0]["file_hash"]
        need(sha((root / path).read_bytes()) == payload, "D7_A6_PAYLOAD:" + c)
        world.setdefault("extra_evidence", []).append(evidence(
            eid, "LEGISLACION_CIT_A6", path, payload, "sin selector verificado", 2023, "adquisicion D1", "rate",
            "legislación CIT", "tasa estatutaria (no mapeada)", "tau_d_estatutario", "rejected", "not_applicable"))
        rows.append({"rate_input_id": f"TRI:{c}:CIT_general", "country_id": c, "regime_id": "general",
                     "legal_effective_date": "not_verified", "rate_type": "cit_general_statutory", "value": None,
                     "evidence_id": eid, "source_locator": "not_mapped", "consumed_section": "tau_d_estatutario",
                     "status": "blocked", "reason_code": "STATUTORY_MAPPING_NOT_VERIFIED"})
    return rows


# ------------------------------------------------------------------------------------- construcción y compuertas
def build_product(world: dict, contracts, authority: A.AuthorityContext) -> dict:
    problems = DB.validate_registry(world["formulas"])
    need(not problems, "D7_REGISTRY_INVALID:" + ";".join(problems[:8]))
    try:
        contracts.definitions(world["formulas"])
    except Exception as exc:  # noqa: BLE001
        raise D7Error("D7_FORMULA_GRAPH_INVALID:" + str(exc)) from exc
    world.setdefault("extra_evidence", [])
    world["evidence"] = sorted(world["evidence"] + world["extra_evidence"], key=lambda e: e["evidence_id"])
    out = DB.build(world)
    tables = out["tables"]
    gates, eligible, expected = gate_rows(world, tables, contracts, authority, out["set_index"])
    tables["d7_gate_report"] = gates
    hard = sum(1 for g in gates if g["status"] == "fail" and g["blocking"])
    lim = sum(1 for g in gates if g["status"] == "limitation")
    ready_b = hard == 0 and eligible == expected
    phase = {"phase_status": "complete" if ready_b else "blocked", "expected_countries": expected,
             "eligible_countries": eligible, "hard_fail_count": hard, "limitation_count": lim, "ready_for_b": ready_b,
             "ready_for_d8_input_audit": all(g["status"] != "fail" for g in gates if g["gate_id"] in ("G01", "G02", "G06"))}
    files = {}
    for name, rows in tables.items():
        data = T.table_bytes(contracts, name, rows)
        files[contracts.C["tables"][name]["file"].split("/", 1)[1]] = (data, T.csv_rows(data))
    files["d7_phase_report.json"] = (T.json_doc_bytes(contracts, "d7_phase_report", dict(phase)), None)
    return {"files": files, "phase": phase, "set_index": out["set_index"], "tables": tables}


def gate_rows(world, tables, contracts, authority, set_index):
    rows = []

    def gate(gid, scope, status, reason, ev, required=True):
        rows.append({"gate_id": gid, "scope_id": scope, "required": required, "status": status, "reason_code": reason,
                     "evidence_id": ev, "blocking": bool(required and status == "fail")})
    try:
        norm = {n: [T.normalize_row(contracts, n, r) for r in rs] for n, rs in tables.items() if n != "d7_gate_report"}
        norm = {n: T.sort_rows(contracts, n, rs) for n, rs in norm.items()}
        contracts.references(norm)
        gate("G01", "global", "pass", "SCHEMA_PK_FK_PASS", "EV.CATALOG")
    except Exception as exc:  # noqa: BLE001
        gate("G01", "global", "fail", "SCHEMA_PK_FK_FAIL", "EV.CATALOG")
        world.setdefault("gate_errors", []).append(str(exc))
    gate("G02", "global", "pass" if not authority.fictitious or world["data_class"] == "synthetic" else "fail",
         "AUTHORITY_" + authority.kind.upper().replace("-", "_"), "EV.REGISTRY")
    expected = sorted({c for e in world["registry"]["entries"] for c in e["country_set"]})
    eligible = []
    for entry in world["registry"]["entries"]:
        preg = entry["preregistration_id"]
        ok = all(len([r for r in tables["tax_component_supports"] if r["support_set_id"] == s and r["country_id"] in entry["country_set"]])
                 == 3 * len(entry["country_set"]) for ed in set_index[preg].values() for s in ed.values())
        gate("G03", preg, "pass" if ok else "fail", "MEMBERS_EXACT_3X" if ok else "MEMBERS_INCOMPLETE", "EV.REGISTRY")
    F = world["formulas"]["parameters"]
    sup = tables["support_set"]
    units_ok = all(r["unit"] == F[r["parameter_id"]].get("unit", "not_applicable") and (r["unit"] != "not_applicable" or r["role"] == "inactive") for r in tables["parameter_registry"]) and all(
        r["lower"] == r["upper"] == "1" for r in sup if r["parameter_id"] in ("gamma", "z_m"))
    gate("G04", "global", "pass" if units_ok else "fail", "UNITS_NORMALIZED_GAMMA_ZM_1" if units_ok else "UNITS_NOT_NORMALIZED",
         "EV.FORMULAS")
    reg_problems = DB.validate_registry(world["formulas"])
    no_center = not any(r["has_central"] or r["central"] is not None for r in sup)
    rho_ok = all(Decimal(r["lower"]) >= 0 and Decimal(r["upper"]) <= 1 for r in sup if r["parameter_id"] == "rho")
    nodes_ok = all(not r["level0_nodes"] or (Decimal(str(min(r["level0_nodes"]))) >= Decimal(r["lower"]) and
                                             Decimal(str(max(r["level0_nodes"]))) <= Decimal(r["upper"])) for r in sup
                   if r["lower"] is not None)
    s_ok = not reg_problems and no_center and rho_ok and nodes_ok
    gate("G05", "global", "pass" if s_ok else "fail", "SUPPORTS_A4_NO_CENTER_RHO_LE_1" if s_ok else "SUPPORTS_INVALID", "EV.FORMULAS")
    try:
        contracts.definitions(world["formulas"])
        gate("G06", "global", "pass", "FORMULAS_ACYCLIC_C2_OPERATOR", "EV.FORMULAS")
    except Exception:  # noqa: BLE001
        gate("G06", "global", "fail", "FORMULA_GRAPH_INVALID", "EV.FORMULAS")
    adm_ok = all(r["accepted_count"] > 0 for r in tables["d7_admissibility_report"])
    gate("G07", "global", "pass" if adm_ok else "fail", "ADMISSIBLE_NONEMPTY" if adm_ok else "EMPTY_ADMISSIBLE_SET", "EV.FORMULAS")
    pred = [e for e in world["evidence"] if e["evidence_id"].startswith("EV.PRED7A.")]
    t_ok = len(pred) in (0, 14) and all(e["transport_status"] in ("limited", "rejected") for e in pred)
    gate("G08", "global", "pass" if t_ok else "fail", "NO_NUMERIC_TRANSPORT" if t_ok else "TRANSPORT_VIOLATION", "EV.FORMULAS")
    gate("G09", "global", "limitation", "V5_CONDITIONAL_CASES_16_UNCERTAIN_PAIRS", "EV.D4.MATRIX", required=False)
    gate("G10", "global", "limitation", "ACCEPTED_LIMITATIONS_D3_D5_A6_CHI_R", "EV.FORMULAS", required=False)
    legal_ok = all(r["lower"] == r["upper"] == "1" for r in sup if r["parameter_id"] == "c_legal") and all(
        r["lower"] == r["upper"] == "0" for r in sup if r["parameter_id"] == "t")
    no_companion = not any("companion" in (r["transformation_id"] or "") or "c_trace" in (r["transformation_id"] or "")
                           for r in tables["scenario_map"])
    trace_inactive = all(r["active_primary"] is False for r in tables["parameter_registry"] if r["parameter_id"] == "c_trace")
    ok11 = legal_ok and no_companion and trace_inactive
    gate("G11", "global", "pass" if ok11 else "fail", "NO_COMPANION_SCENARIO_SUPPORT_C_LEGAL_1_NO_C_TRACE" if ok11
         else "COMPANION_OR_C_LEGAL_VIOLATION", "EV.CROSSWALK")
    pii = [e["evidence_id"] for e in tables["source_evidence"] if str(e["source_path"]).lower().endswith(".eml")
           or any("@" in str(e[k] or "") for k in ("source_path", "source_locator", "universe", "identified_object"))]
    gate("G12", "global", "pass" if not pii else "fail", "NO_PII_NO_EML_IN_PRODUCT" if not pii else "PII_OR_EML_IN_PRODUCT",
         "EV.REGISTRY")
    registered = {r["parameter_id"] for r in tables["parameter_registry"]}
    used = ({r["parameter_id"] for r in sup} | {r["parameter_id"] for r in tables["parameter_bindings"]}
            | {r["parameter_id"] for r in tables["formula_inputs"]} | {r["parameter_id"] for r in tables["constraint_inputs"]})
    bound = {(r["support_set_id"], r["parameter_id"]) for r in tables["parameter_bindings"]}
    unbound = [(s["support_set_id"], pid) for s in tables["support_sets"] for pid in contracts.K["common_primitive_ids"]
               if (s["support_set_id"], pid) not in bound]
    hidden = sorted(used - registered)
    ok14 = not hidden and not unbound
    gate("G14", "global", "pass" if ok14 else "fail", "NO_HIDDEN_PARAMETERS" if ok14 else "HIDDEN_OR_UNBOUND_PARAMETERS",
         "EV.FORMULAS")
    if world.get("data_class") != "national":       # mundo sintético de plomería: sin casos nacionales que evaluar
        elig = authority.scope.get("quantitative_eligibility_authorized") is True
        for entry in world["registry"]["entries"]:
            gate("G13", entry["preregistration_id"], "pass" if elig else "fail",
                 "QUANTITATIVE_ELIGIBILITY_AUTHORIZED" if elig else "ELIGIBILITY_NOT_AUTHORIZED", "EV.REGISTRY")
        return sorted(rows, key=lambda r: (r["gate_id"], r["scope_id"])), (expected[:] if elig else []), expected
    from herramientas.s5 import elegibilidad as EL
    eligible_set, matrix = set(), []
    for entry in world["registry"]["entries"]:
        preg = entry["preregistration_id"]
        req = EL.requisitos(entry, world, tables, rows)
        st, reason = EL.g13(entry, req, authority, rows)
        gate("G13", preg, st, reason, "EV.REGISTRY")
        matrix.append(dict(req, g13=st, g13_reason=reason))
        if st == "pass":
            eligible_set |= set(entry["country_set"])
    world["eligibility_matrix"] = matrix
    eligible = sorted(eligible_set)
    return sorted(rows, key=lambda r: (r["gate_id"], r["scope_id"])), eligible, expected


def produce(world: dict, contracts, authority: A.AuthorityContext, out_root: Path, *, producer_path: str,
            producer_bytes: bytes, dependencies: list, created_at: str | None = None) -> dict:
    authority.require("d7_production_authorized")
    prod = build_product(world, contracts, authority)
    entries = FAM.entries_for(prod["files"])
    run_id = "D7-" + H({"authority": authority.package_sha256, "tree": FAM.tree_of(entries), "producer": sha(producer_bytes)})[:24]
    mbytes = FAM.manifest(contracts, "D7", run_id=run_id, producer_path=producer_path, producer_sha256=sha(producer_bytes),
                          authority_package=authority.package_sha256, authority_manifest=authority.manifest_sha256,
                          contract_sha256=authority.contract_sha256, dependencies=dependencies, entries=entries,
                          phase_status=prod["phase"]["phase_status"], created_at=created_at)
    info = FAM.write_version(out_root, "D7", prod["files"], mbytes)
    return dict(info, phase=prod["phase"], set_index=prod["set_index"], run_id=run_id,
                gate_errors=world.get("gate_errors", []))


def national_dependencies(world: dict, authority: A.AuthorityContext) -> list:
    root = world["root"]
    rel = lambda p: Path(p).relative_to(root).as_posix()
    f = world["d2_files"]
    pkg = authority.products_authority["package_sha256"]
    vers = world["versions"]
    npkg = authority.succession["s5"]["package_sha256"] if authority.succession else pkg   # autoridad de D2/D6/índice
    deps = [
        {"role": "autoridad_consumidora", "path": "fase6_planes/freeze_plans_manifest.json", "sha256": authority.manifest_sha256,
         "tree_sha256": None, "version": authority.kind, "authority_package_sha256": authority.package_sha256},
        {"role": "d2_version", "path": rel(f["d2_manifest"]), "sha256": sha(f["d2_manifest"].read_bytes()), "tree_sha256": vers["d2_tree"],
         "version": vers["d2_tree"], "authority_package_sha256": npkg},
        {"role": "d6_v2_version", "path": rel(f["d6_manifest"]), "sha256": sha(f["d6_manifest"].read_bytes()), "tree_sha256": vers["d6_tree"],
         "version": vers["d6_tree"], "authority_package_sha256": npkg},
        {"role": "d4_model_case_map", "path": rel(world["d4"]["dir"] / "model_case_map.csv"),
         "sha256": sha((world["d4"]["dir"] / "model_case_map.csv").read_bytes()), "tree_sha256": world["d4"]["tree"],
         "version": world["d4"]["tree"], "authority_package_sha256": pkg},
        {"role": "external_grid", "path": GRID, "sha256": GRID_SHA, "tree_sha256": None, "version": "official_4c_tierA_baseline_official_v2",
         "authority_package_sha256": None},
        {"role": "ca2_bundles_index", "path": vers["bundle_index"], "sha256": vers["bundle_index_sha256"], "tree_sha256": None,
         "version": "S5" if authority.succession else "1.5", "authority_package_sha256": npkg},
        {"role": "contrato_normativo", "path": authority.contract_root + "contratos/contract_manifest.json", "sha256": authority.contract_sha256,
         "tree_sha256": None, "version": "CA2-3", "authority_package_sha256": pkg},
        {"role": "pre_d7_a_v2_inventario", "path": "herramientas/d7/preparar_d7_a_v2.py",
         "sha256": sha((root / "herramientas/d7/preparar_d7_a_v2.py").read_bytes()), "tree_sha256": None,
         "version": world["pre_d7_a"]["inventory_sha256"], "authority_package_sha256": pkg},
    ]
    for k in ("D3", "D4", "D5"):
        c = world["certs"][k]
        deps.append({"role": f"certificado_{k}", "path": c.get("path", f"fase2_datos/certificados_reuso/CERT-REUSO-{k}-A1E-v2.json"),
                     "sha256": c["certificate_sha256"], "tree_sha256": None, "version": "A1E-v2", "authority_package_sha256": pkg})
    return deps


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="D7 (bloque 2)")
    ap.add_argument("command", choices=["verificar-autoridad", "construir", "verificar"])
    ap.add_argument("--s6-lanzamiento-sha256", help="SHA-256 EXTERNO de autorización; volver a aportar tras reubicar; no se deduce del paquete")
    ap.add_argument("--autoridad", choices=["s3", "s4", "s5", "s6"], default="s3")
    ap.add_argument("--policy")
    ap.add_argument("--receipt")
    ap.add_argument("--author")
    ap.add_argument("--d2-tree", default=D2_TREE)
    ap.add_argument("--d6-tree", default=D6_TREE)
    ap.add_argument("--cases", default=",".join(CASES))
    ap.add_argument("--salida")
    ap.add_argument("--producto")
    ap.add_argument("--tree")
    args = ap.parse_args(argv)
    try:
        if args.command == "verificar":
            info = FAM.verify_version(Path(args.producto), "D7", expected_tree=args.tree)
            print(json.dumps({"status": "verified_D7", "tree_sha256": info["tree_sha256"],
                              "manifest_sha256": info["manifest_sha256"], "phase_status": info["manifest"]["phase_status"]}))
            return 0
        extra = {"lanzamiento_sha256": args.s6_lanzamiento_sha256} if args.autoridad == "s6" else {}
        if args.s6_lanzamiento_sha256 is not None and args.autoridad != "s6":
            raise A.AuthorityError("ANCLA_S6_CON_OTRA_AUTORIDAD")
        ctx = {"s3": A.from_s3, "s4": A.from_s4, "s5": A.from_s5, "s6": A.from_s6}[args.autoridad](ROOT, args.policy, args.receipt, args.author, **extra)
        ctx.require("d7_production_authorized")
        if args.command == "verificar-autoridad":
            print(json.dumps({"authority": ctx.kind, "scope": ctx.scope}))
            return 0
        need(args.salida, "D7_OUTPUT_REQUIRED")
        world = national_world(ROOT, ctx, d2_tree=args.d2_tree, d6_tree=args.d6_tree, cases=sorted(args.cases.split(",")))
        contracts = contracts_for(ROOT, ctx)
        me = Path(__file__)
        res = produce(world, contracts, ctx, Path(args.salida), producer_path=me.relative_to(ROOT).as_posix(),
                      producer_bytes=me.read_bytes(), dependencies=national_dependencies(world, ctx))
        print(json.dumps({"tree_sha256": res["tree_sha256"], "manifest_sha256": res["manifest_sha256"], "phase": res["phase"],
                          "run_id": res["run_id"], "authority": ctx.kind, "gate_errors": res["gate_errors"],
                          "eligibility_matrix": world.get("eligibility_matrix")}, ensure_ascii=False))
        return 0
    except (A.AuthorityError, D7Error, FAM.FamilyError, ValueError, KeyError, OSError, RuntimeError) as exc:
        print("D7 RECHAZADO: " + type(exc).__name__ + ": " + str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
