"""Mundos SINTÉTICOS para validar D7 -> B -> D8 sin datos nacionales (RE-05; diseño §19.3).

Todo valor es ficticio y está rotulado: códigos de país del dominio del contrato (el tipo 'country' solo admite
CHL/COL/MEX/PER), pero participaciones, grilla externa, vectores y claves condicionales son inventados y declarados
'synthetic'. La autoridad es FICTICIA (herramientas/bloque2/autoridad.fictitious). Ninguna salida es nacional ni oficial.
Los soportes estructurales se estrechan a singletons (o pocos nudos) para que el cálculo sea pequeño y la cobertura
del continuo quede demostrada por construcción; esa elección es de la prueba, no del modelo ni de A4.
"""
from __future__ import annotations

import copy
import json
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

from paper2b import external as X
from paper2b import keys as K
from paper2b import macro as MC
from paper2b.d7build import COMPONENTS, NATIONAL, base_set_id, editions
from herramientas.bloque2 import autoridad as A

SYN_TAG = "SINTETICO_NO_NACIONAL"
DEFAULT_STRUCT = {"a": "1.5", "rho": "0.8", "kappa_tilde": "0.1", "beta_tilde": "1", "u_theta": "0.5", "z_cost": "10",
                  "eta_d": "1", "eta_f": "1.2", "phi": "0.5"}


def synthetic_formulas(real: dict, struct: dict | None = None, *, macro_singletons: dict | None = None) -> dict:
    """Copia de formulas.json con soportes estructurales singleton (valores de prueba) y macro opcionalmente fijados."""
    f = copy.deepcopy(real)
    for pid, v in (struct or DEFAULT_STRUCT).items():
        if isinstance(v, (list, tuple)):
            vals = [Decimal(str(x)) for x in v]
            f["parameters"][pid]["primary"] = {"kind": "continuous", "lower": float(vals[0]), "upper": float(vals[-1]),
                                               "lower_closed": True, "upper_closed": True, "level0_nodes": [float(x) for x in vals],
                                               "scale": f["parameters"][pid]["primary"].get("scale", "arithmetic")}
        else:
            f["parameters"][pid]["primary"] = {"kind": "singleton", "lower": float(v), "upper": float(v), "lower_closed": True,
                                               "upper_closed": True, "level0_nodes": [float(v)], "scale": "discrete"}
    for pid, v in (macro_singletons or {}).items():
        p = f["parameters"][pid]
        if "primary_nodes" in p:          # eta_H: nudos primarios discretos (la escalera de sensibilidad no cambia)
            p["primary_nodes"] = [float(v)]
            continue
        if "primary_blocks" in p:
            raise ValueError("eta_w se define por bloque; no admite singleton sintético global")
        p["primary"] = {"kind": "singleton", "lower": float(v), "upper": float(v), "lower_closed": True,
                        "upper_closed": True, "level0_nodes": [float(v)], "scale": "discrete"}
    return f


def registry(countries=("PER",), *, preg="SYN-PER-E1", case_type="aplicacion_principal", scenarios=("E1",), claims=None,
             revisions=None) -> dict:
    entry = {"preregistration_id": preg, "case_type": case_type, "country_set": sorted(countries), "scenarios": list(scenarios),
             "claims": claims or {"primary": [2023]}, "revisions": revisions,
             "vectors": None if revisions else {c: {"D6": {"source_id": f"{c}_SYN", "representation": "d6_net",
                                                            "snapshot_sha256": K.H(["syn", c]), "source_vintage": "SYN"}}
                                                for c in countries},
             "description": SYN_TAG, "author_decisions": []}
    return {"registry_id": "SYN", "entries": [entry], "status": SYN_TAG}


def model_case_map(countries) -> list:
    rows = []
    for c in sorted(countries):
        rows.append({"country_id": c, "instrument_id": "syn", "national_availability_status": "UNKNOWN", "model_menu": "j_d",
                     "case_id": "domestic_unchanged", "availability_assumed": "false", "quantitative_use": "domestic_menu_unchanged"})
        for j in ("j_df", "j_f"):
            rows.append({"country_id": c, "instrument_id": "syn", "national_availability_status": "UNKNOWN", "model_menu": j,
                         "case_id": "conditional_full", "availability_assumed": "true",
                         "quantitative_use": "conditional_scenario_foreign_leg_enabled"})
            rows.append({"country_id": c, "instrument_id": "syn", "national_availability_status": "UNKNOWN", "model_menu": j,
                         "case_id": "conditional_none", "availability_assumed": "true",
                         "quantitative_use": "conditional_scenario_no_foreign_leg"})
    return rows


def grid(countries, *, cost=0.004, f_admin=0.002, f_trans=0.0008, f_leak=0.0001, s_pb=0.003,
         policies=(("SYNA", 1.0), ("SYNB", 1.5)), xis=("0.0", "0.1")) -> tuple[bytes, list]:
    """Grilla externa ficticia con el esquema exacto de 15 columnas (políticas x 1 régimen x 2 bases x xi)."""
    lines = [",".join(X.COLUMNS)]
    for c in sorted(countries):
        for p, scale in policies:
            for basis in ("baseline", "debt_consistent"):
                for xi in xis:
                    cg = cost * scale
                    ffix = f_admin + f_trans + f_leak
                    dc = s_pb if basis == "debt_consistent" else 0.0
                    q = (1 + float(xi)) * cg + ffix + dc
                    lines.append(",".join([c, p, p, p, "r0", basis, xi, repr(cg), repr(f_admin), repr(f_trans), repr(f_leak),
                                           repr(ffix), repr(ffix - f_leak), repr(dc), repr(q)]))
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    return raw, X.read_grid(raw)


def national_shares(countries, *, sL="0.3", iva="0.05", otros="0.02", prod="0.01", per_country=None) -> dict:
    out = {}
    for c in countries:
        v = (per_country or {}).get(c, {})
        out[c] = {"s_L_bar": Fraction(v.get("sL", sL)), "s_bar_iva": Fraction(v.get("iva", iva)),
                  "s_bar_otros_productos": Fraction(v.get("otros", otros)), "s_bar_produccion": Fraction(v.get("prod", prod))}
    return out


def world(real_formulas: dict, *, countries=("PER",), struct=None, shares=None, reg=None, eligible=True,
          macro_singletons=None, strict=False, verified_rate=None, national_mode="conditional", model=None) -> dict:
    """Mundo SINTÉTICO. model: proveedor de modelo (None = modelo teórico v2.2; SustitutoCertificado = sustituto
    analítico FICTICIO con encierros demostrativos, solo para probar la ruta certificada de punta a punta)."""
    reg = reg or registry(countries)
    shares = shares or national_shares(countries)
    auth = A.fictitious(scope={"d7_production_authorized": True, "quantitative_eligibility_authorized": eligible,
                               "b_synthetic_validation_authorized": True, "d8_pre_authorized": True, "d8_post_authorized": True},
                        label="mundo sintético")
    ev = [_ev("EV.REGISTRY"), _ev("EV.FORMULAS"), _ev("EV.CATALOG"), _ev("EV.GRID", use="measurement", transport="direct_verified"),
          _ev("EV.DME", use="measurement", transport="direct_verified"), _ev("EV.CROSSWALK"), _ev("EV.D4.MAP"), _ev("EV.D4.MATRIX")]
    national = {}
    d6_tree = K.H(["syn-d6"])
    for entry in reg["entries"]:
        preg = entry["preregistration_id"]
        for ed in editions(entry):
            for c in entry["country_set"]:
                sh = shares[c]
                d6_rows, sdict = {}, {}
                for comp, key in COMPONENTS.items():
                    eid = f"EV.SYN.{preg}.{c}.{ed or 'pub'}.{comp}"
                    ev.append(_ev(eid, use="measurement", transport="direct_verified", precision=f"SYNPREC.{c}"))
                    d6_rows[comp] = {"row_id": f"{preg}:{c}:{ed or 'pub'}:{comp}", "low": sh[key], "high": sh[key], "evidence_id": eid}
                    sdict[key] = {"value": sh[key], "exact": sh[key], "evidence_id": eid}
                seid = f"EV.SYN.{preg}.{c}.{ed or 'pub'}.s_L_bar"
                ev.append(_ev(seid, use="measurement", transport="direct_verified", precision=f"SYNPREC.{c}"))
                sdict["s_L_bar"] = {"value": sh["s_L_bar"], "exact": sh["s_L_bar"], "evidence_id": seid}
                group = [{"d6_tree_sha256": d6_tree, "primitive_id": f"SYNOBS-{c}-{x}", "source_path": "sintetico/obs.csv",
                          "source_locator": f"{c}:{x}", "source_sha256": K.H([c, x]), "unit": "SYN"} for x in ("PIB", "V", "P", "N")]
                national[(preg, ed or "pub", c)] = dict(sdict, d6_rows=d6_rows, primitive_group=group, historical={}, joint=None,
                                                        strict=strict, d6_edition=f"{c}_SYN")
    rates = [{"rate_input_id": f"TRI:{c}:CIT_general", "country_id": c, "regime_id": "general", "legal_effective_date": "not_verified",
              "rate_type": "cit_general_statutory", "value": None, "evidence_id": "EV.REGISTRY", "source_locator": "not_mapped",
              "consumed_section": "tau_d_estatutario", "status": "blocked", "reason_code": "STATUTORY_MAPPING_NOT_VERIFIED"}
             for c in sorted({c for e in reg["entries"] for c in e["country_set"]})]
    if verified_rate is not None:      # tasa SINTÉTICA verificada (solo para ejercitar la sección estatutaria)
        ev.append(_ev("EV.SYN.RATE", use="measurement", transport="direct_verified"))
        rates = [dict(r, legal_effective_date="2023-01-01", value=str(verified_rate), evidence_id="EV.SYN.RATE",
                      source_locator=SYN_TAG, status="verified", reason_code=None) for r in rates]
    matrix_payload = {"kind": "SYNTHETIC_D4_NOT_NATIONAL", "model_case_map": model_case_map(countries)}
    for e in ev:
        if e["evidence_id"] == "EV.D4.MATRIX":
            e["payload_sha256"] = K.H(matrix_payload)
    return {"registry": reg, "formulas": synthetic_formulas(real_formulas, struct, macro_singletons=macro_singletons),
            "authority_row": auth.row(), "authority": auth, "evidence": sorted(ev, key=lambda e: e["evidence_id"]),
            "national": national, "tax_rates": rates, "d4": {"model_case_map": model_case_map(countries), "tree": K.H(["syn-d4"]),
                                                               "matrix_sha256": K.H(matrix_payload), "matrix_payload": matrix_payload},
            "d6": {"tree": d6_tree}, "pre_d7_a": {"inventory": [], "comparability": []}, "data_class": "synthetic",
            "shares": shares, "national_mode": national_mode, "model": model}


def _ev(eid, *, use="formula_input", transport="not_applicable", precision=None):
    return {"evidence_id": eid, "source_id": "SYN", "source_path": "sintetico/" + eid.lower().replace(".", "_") + ".json",
            "payload_sha256": K.H([eid]), "source_locator": SYN_TAG, "source_year": 2023, "source_vintage": "SYN", "unit": "none",
            "multiplier": "1", "universe": SYN_TAG, "identified_object": SYN_TAG, "target_object": SYN_TAG,
            "permitted_use": use, "transport_status": transport, "precision_evidence_id": precision}


D6_CONCEPT = {"s_bar_iva": "V", "s_bar_otros_productos": "P_NET", "s_bar_produccion": "N_PROD"}


def synthetic_bundle(w: dict, designs=("G", "N"), component_shas: dict | None = None) -> tuple[dict, dict]:
    """Bundle CA2 SINTÉTICO con la estructura de los bundles 1.5: casos por contexto de celda (diseño-menú-caso D4),
    vectores D2 (d2_combined) y D6 (d6_net) 2023 con miembros publicados ficticios, entradas y archivos de contexto.
    Devuelve (tablas, {nombre_archivo_contexto: contenido})."""
    entry = w["registry"]["entries"][0]
    preg = entry["preregistration_id"]
    comps = component_shas or {k: K.H(["syn-component", k]) for k in ("external_requirement", "gain_share", "labor_block", "pi",
                                                                      "structural_state")}
    vectors, members, cases, inputs, contexts = [], [], [], [], {}
    for c in sorted(entry["country_set"]):
        sh = w["shares"][c]
        pib = Fraction(1000)
        d2m = {"COE": sh["s_L_bar"] * pib, "PIB": pib}
        d6m = {"PIB": pib, **{D6_CONCEPT[k]: sh[k] * pib for k in D6_CONCEPT}}
        for fam, rep, mem in (("D2", "d2_combined", d2m), ("D6", "d6_net", d6m)):
            vid = f"{c}_{fam}_2023_SYN"
            rows = [{"vector_id": vid, "country_id": c, "concept": k, "member_id": k, "value_literal": str(v),
                     "observation_year": 2023, "unit": "SYN", "denominator_member_id": "PIB"} for k, v in sorted(mem.items())]
            members += rows
            vectors.append({"vector_id": vid, "family": fam, "country_id": c, "observation_year": 2023, "representation": rep,
                            "source_id": "SYN", "source_vintage": "SYN", "snapshot_sha256": K.H(["syn-snapshot", c]), "unit": "SYN",
                            "vector_sha256": K.H(rows)})
        for r in model_case_map([c]):
            for dsg in designs:
                label = f"{dsg}-{r['model_menu'][2:]}-{r['case_id']}"
                ctx = dict({"availability_case_id": r["case_id"], "availability_matrix_hash": w["d4"]["matrix_sha256"],
                            "design_v": dsg, "instrument_j": r["model_menu"][2:]},
                           **{k + "_sha256": v for k, v in sorted(comps.items())})
                raw = (json.dumps(ctx, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
                csha = __import__("hashlib").sha256(raw).hexdigest()
                contexts[csha + ".json"] = raw
                case_id = f"{preg}:E1:2023:{label}"
                if not any(x["case_id"] == case_id for x in cases):
                    cases.append({"case_id": case_id, "scenario": "E1", "preregistration_id": preg, "case_type": entry["case_type"],
                                  "country_set": sorted(entry["country_set"]), "channel": "conditional",
                                  "admissibility": "conditional_metadata", "precision_claim": "not_asserted"})
                inputs.append({"case_id": case_id, "country_id": c, "anchor_year": 2023, "d2_vector_id": f"{c}_D2_2023_SYN",
                               "d6_vector_id": f"{c}_D6_2023_SYN", "context_sha256": csha, "context_path": "contextos/" + csha + ".json"})
    tables = {"ca2_cases": sorted(cases, key=lambda x: x["case_id"]), "ca2_inputs": sorted(inputs, key=lambda x: (x["case_id"], x["country_id"])),
              "ca2_members": members, "ca2_vectors": vectors, "tag": SYN_TAG}
    return tables, contexts


def national_provider(w: dict, bundle: dict | None = None, bundle_sha: str | None = None):
    """Estados condicionales sintéticos: un estado por país y año ancla, con primitivas publicadas del bundle."""
    shares = w["shares"]

    def provider(set_id, country):
        entry = w["registry"]["entries"][0]
        sh = shares[country]
        if bundle is None:
            pib = Fraction(1000)
            prim = tuple(sorted([("SYN_PIB", pib, "SYN"), ("SYN_COE", sh["s_L_bar"] * pib, "SYN")]))
            jd = K.H(["syn-bundle", country])
        else:
            prim = tuple(sorted((f"{m['vector_id']}:{m['concept']}", Fraction(m["value_literal"]), m["unit"])
                                for m in bundle["ca2_members"] if m["country_id"] == country))
            jd = bundle_sha
        return [MC.NationalState(country, entry["preregistration_id"], "conditional", "pub", 2023, "published_vector", prim,
                                 tuple((k, sh[k]) for k in MC.SHARE_KEYS), jd)]
    return provider


def conditional_key_provider(w: dict, contracts, technical: dict, protocol_sha: str, bundle: dict | None = None,
                             bundle_sha: str | None = None):
    """Clave macro-ca2-v2 SINTÉTICA construida sobre el bundle sintético (misma función que valida rules.py)."""
    from paper2b import claves_condicionales as CK

    def provider(state, om, block, context):
        entry = w["registry"]["entries"][0]
        label = "-".join(context) if context else "SYN"
        case_id = f"{entry['preregistration_id']}:E1:{state.anchor_year}:{label}"
        payload = CK.build_payload(bundle, bundle_sha, case_id, state.country_id, state.anchor_year, om["common_sha"], block,
                                   protocol_sha, technical)
        return payload, K.H(payload)
    return provider


def joint_domain(countries, shares, *, pib=1000, half_width="0.5") -> dict:
    """Dominio conjunto SINTÉTICO de primitivas (caja de publicación de media unidad) por país."""
    hw = Fraction(half_width)
    out = {}
    for c in sorted(countries):
        sh = shares[c]
        mid = {"SYN_PIB": Fraction(pib), "SYN_COE": sh["s_L_bar"] * pib, "SYN_V": sh["s_bar_iva"] * pib,
               "SYN_O": sh["s_bar_otros_productos"] * pib, "SYN_N": sh["s_bar_produccion"] * pib}
        out[c] = {"primitive_domains": {k: [str(v - hw), str(v + hw)] for k, v in sorted(mid.items())},
                  "terms": {"s_L_bar": [["SYN_COE", "1"]], "s_bar_iva": [["SYN_V", "1"]], "s_bar_otros_productos": [["SYN_O", "1"]],
                            "s_bar_produccion": [["SYN_N", "1"]]}, "denominator": "SYN_PIB", "tag": SYN_TAG}
    return out


def strict_national_provider(w: dict, paths: dict, root):
    """Vía estricta SINTÉTICA: dominio conjunto escrito como archivo real y cuatro dependencias exactas por rol."""
    rel, digest = paths["dominio_conjunto.json"]
    mrel, mdig = paths["mundo.json"]
    doms = json.loads(Path(root).joinpath(rel).read_bytes())

    def dep(role, pk):
        art = (rel, digest) if role == "joint_domain" else (mrel, mdig)
        return {"role": role, "manifest_path": mrel, "manifest_sha256": mdig, "artifact_path": art[0], "artifact_sha256": art[1],
                "record_pk": pk}

    def provider(set_id, country):
        entry = w["registry"]["entries"][0]
        d = doms[country]
        deps = sorted([dep("d2_snapshot", {"country_id": country, "observation_year": 2023}),
                       dep("d6_snapshot", {"preregistration_id": entry["preregistration_id"], "country_id": country}),
                       dep("joint_domain", {"view": country + "_SYN"}), dep("precision", {"country_id": country})],
                      key=lambda x: x["role"])
        return [{"kind": "strict_domain", "domains": {k: (Fraction(lo), Fraction(hi)) for k, (lo, hi) in d["primitive_domains"].items()},
                 "terms": {k: [(pp, Fraction(cf)) for pp, cf in v] for k, v in d["terms"].items()}, "denominator": d["denominator"],
                 "preregistration_id": entry["preregistration_id"], "edition": "pub", "anchor_year": 2023, "unit": "SYN",
                 "joint_domain_sha256": digest, "dependencies": deps}]
    return provider
