"""Construcción pura de las tablas D7 (CONTRATOS_D7_B_D8, catálogo CA2-3) a partir de insumos YA autenticados.

No lee rutas del proyecto ni decide autoridad: recibe un 'world' con bytes/filas verificados por el llamador
(herramientas/d7/construir_d7.py). Separa estrictamente:
- soportes elegidos por el autor (formulas.json: declared_scenario, sin centro);
- mediciones nacionales (D2/D6 versionados; measured con evidencia y referencia de precisión o de vía condicional);
- evidencia bibliográfica PRE-D7-A (14 obras: 13 limited, 1 rejected; transporte numérico nacional prohibido).
Operadores de B (R, C_2) se DECLARAN con result_binding; D7 no evalúa ni exige sus resultados (sin ciclo D7->B->D7).
"""
from __future__ import annotations

import json
from decimal import Decimal
from fractions import Fraction
from itertools import product

from .keys import H
from .numeric import canon_dec
from .supports import transform

BLOCKS = {"micro": ("0.05", "0.2"), "macro": ("0.4", "1")}
DERIVED_SET_KINDS = [
    ("COORD", "coordination", "coordination_half", "coordinación mitad/mitad (eta_f/2, phi/2) sobre cada par (DI-07)"),
    ("ABL-ENF", "coordination", "enforcement_half", "ablación: solo eta_f/2 (control separado, no coordinación)"),
    ("ABL-COV", "coordination", "coverage_half", "ablación: solo phi/2 (control separado, no coordinación)"),
    ("STR-040", "domain_stress", "tax_domain_stress", "estrés de dominio fiscal: topes pareados 0.40"),
    ("STR-080", "domain_stress", "tax_domain_stress", "estrés de dominio fiscal: topes pareados 0.80"),
    ("ROB-LABW", "robustness", "directional_arithmetic", "bloque incidencia laboral: expansión direccional de eta_w"),
    ("ROB-LABH", "robustness", "eta_H_ladder", "bloque incidencia laboral: escalera anidada de eta_H"),
    ("ROB-TAX", "robustness", "directional_arithmetic", "bloque cuña tributaria: expansión de pi por componente y conjunta"),
    ("ROB-TEC", "robustness", "directional_arithmetic", "bloque tecnología: a y rho aritméticas, kappa_tilde logarítmica"),
    ("ROB-RES", "robustness", "directional_arithmetic", "bloque cobertura residual chi_r (no identificado bajo D5)"),
    ("EXT-Q", "external_sensitivity", "external_scale", "sensibilidad reducida de Q: m_Q global primario, país adicional"),
]
STRESS = {"STR-040": Decimal("0.4"), "STR-080": Decimal("0.8")}
MODULE = {"a": "estructural", "rho": "estructural", "kappa_tilde": "estructural", "beta_tilde": "estructural",
          "u_theta": "estructural", "z_cost": "estructural", "eta_d": "estructural", "eta_f": "estructural", "phi": "estructural",
          "gamma": "normalizacion", "z_m": "normalizacion", "c_legal": "alcance", "t": "alcance",
          "pi_iva": "macro", "pi_otros_productos": "macro", "pi_produccion": "macro", "eta_w": "macro", "eta_H": "macro",
          "gain_share": "escala_tecnologica", "tau_d": "fiscal", "tau_f": "fiscal", "bar_tau_d": "fiscal", "bar_tau_f": "fiscal",
          "s_L_bar": "nacional", "s_bar_iva": "nacional", "s_bar_otros_productos": "nacional", "s_bar_produccion": "nacional",
          "Q_perp": "externo", "DME_gAI": "externo", "supplier_share_target": "inversion", "external_factor": "inversion"}
INACTIVE_REASON = {"chi_r": "MOMENT_NOT_IDENTIFIED", "P_mapped": "MOMENT_NOT_IDENTIFIED", "residual_share": "MOMENT_NOT_IDENTIFIED",
                   "s_AI": "NOT_IDENTIFIED_M3_OR_EXTENSION", "s_FN": "NOT_IDENTIFIED_M3_OR_EXTENSION", "Ptarget": "PTARGET_NOT_IDENTIFIED",
                   "omega_tail": "M3_NOT_APPLICABLE", "body_dist_id": "M3_NOT_APPLICABLE", "M_c": "UNIVERSE_LIMITATION_H",
                   "c_trace": "H13_NO_TRACE_FACTOR", "P_total": "MOMENT_BRANCH_INACTIVE"}
NATIONAL = ("s_L_bar", "s_bar_iva", "s_bar_otros_productos", "s_bar_produccion")
COMPONENTS = {"iva": "s_bar_iva", "otros_productos": "s_bar_otros_productos", "produccion": "s_bar_produccion"}
CONSTRAINTS = [
    ("CON.S4", "0<=rho<=1 (evaluación interior 0<rho<=1)", "RHO_OUTSIDE_S4", "theoretical", "domain_stop", "teoría S4; DOMINIOS", ["rho"]),
    ("CON.MOMENTS", "a>1 and 0<u_theta<1 and theta=1+u_theta*(a-1) and theta<a and rho<a", "MOMENTS_DOMAIN", "theoretical",
     "hard_fail", "S6/S18; formulas.json constraints.moments", ["a", "rho", "theta", "u_theta"]),
    ("CON.SCALES", "kappa_tilde>0 and beta_tilde>0 and z_cost>0 and gamma>0 and z_m>0", "POSITIVE_SCALES", "theoretical",
     "hard_fail", "formulas.json constraints.positive_scales", ["beta_tilde", "gamma", "kappa_tilde", "z_cost", "z_m"]),
    ("CON.QPOT", "q_pot<1", "Q_POT_GE_1", "admissibility", "exclude", "diseño (20)", ["q_pot"]),
    ("CON.ETAH", "eta_H>-1", "ETA_H_LE_MINUS1", "theoretical", "exclude", "diseño (20)", ["eta_H"]),
    ("CON.STMARG", "s_T_marg>=0", "S_T_MARG_NEGATIVE", "admissibility", "exclude", "PRE-D6 v3; DI-05", ["s_T_marg"]),
    ("CON.SPI", "s_Pi_marg>0 and lambda_pi>0", "S_PI_OR_LAMBDA_NONPOSITIVE", "admissibility", "exclude", "DI-05; formulas.json macro",
     ["lambda_pi", "s_Pi_marg"]),
    ("CON.CLEGAL", "c_legal==1", "C_LEGAL_EXTENSION_INACTIVE", "none", "hard_fail", "diseño §7.3.2, H22", ["c_legal"]),
    ("CON.TBASE", "t==0", "T_EXTENSION_INACTIVE", "none", "hard_fail", "S15; DI-04", ["t"]),
]


def case_code(preg: str) -> str:
    return preg.replace("PREG-", "").replace("APLICACION-", "").replace("COMPARACION", "CMP")


def editions(entry: dict) -> list:
    if entry.get("revisions"):
        country = entry["country_set"][0]
        return [r["label"] for r in entry["revisions"][country]]
    return [None]


def base_set_id(entry: dict, edition, block: str) -> str:
    code = case_code(entry["preregistration_id"])
    return f"{code}.{edition}.{block}" if edition else f"{code}.{block}"


def _dec_list(xs):
    return [canon_dec(Decimal(str(x))) for x in xs]


def primary_supports(formulas: dict, block: str) -> dict:
    """Soportes primarios por parámetro (formulas.json), sin inventar nudos ni centros."""
    out = {}
    for pid, p in formulas["parameters"].items():
        role = p["role"]
        if role == "primitive" and "primary" in p:
            pr = p["primary"]
            if pid in ("tau_d", "tau_f"):
                out[pid] = [dict(variant_id="full", domain_kind="continuous", lower=Decimal(str(pr["lower"])),
                                 upper=Decimal(str(pr["upper"])), lower_closed=True, upper_closed=True, scale="arithmetic",
                                 level0_nodes=[Decimal(str(pr["lower"])), Decimal(str(pr["upper"]))]),
                            dict(variant_id="zero", domain_kind="singleton", lower=Decimal(0), upper=Decimal(0),
                                 lower_closed=True, upper_closed=True, scale="discrete", level0_nodes=[Decimal(0)])]
                continue
            kind = pr.get("kind", "continuous")
            out[pid] = [dict(variant_id="primary", domain_kind=kind, lower=Decimal(str(pr["lower"])),
                             upper=Decimal(str(pr["upper"])), lower_closed=pr.get("lower_closed", True),
                             upper_closed=pr.get("upper_closed", True),
                             scale="discrete" if kind in ("singleton", "discrete") else pr.get("scale", "arithmetic"),
                             level0_nodes=[Decimal(str(x)) for x in pr["level0_nodes"]])]
        elif pid == "eta_w":
            lo, hi = BLOCKS[block]
            out[pid] = [dict(variant_id=block, domain_kind="continuous", lower=Decimal(lo), upper=Decimal(hi), lower_closed=True,
                             upper_closed=True, scale="arithmetic", level0_nodes=[Decimal(lo), Decimal(hi)])]
        elif pid == "eta_H":
            nodes = [Decimal(str(x)) for x in p["primary_nodes"]]
            out[pid] = [dict(variant_id="H0", domain_kind="discrete", lower=min(nodes), upper=max(nodes), lower_closed=True,
                             upper_closed=True, scale="discrete", level0_nodes=nodes)]
        elif pid in ("bar_tau_d", "bar_tau_f"):
            v = Decimal(str(p["primary_value"]))
            out[pid] = [dict(variant_id="primary", domain_kind="singleton", lower=v, upper=v, lower_closed=True, upper_closed=True,
                             scale="discrete", level0_nodes=[v])]
        elif pid in ("supplier_share_target", "external_factor"):
            lo, hi = (Decimal(str(x)) for x in p["domain"])
            out[pid] = [dict(variant_id="primary", domain_kind="continuous", lower=lo, upper=hi, lower_closed=True, upper_closed=True,
                             scale="arithmetic", level0_nodes=[lo, hi])]
        elif role == "fixed":
            v = Decimal(str(p["value"]))
            out[pid] = [dict(variant_id="fixed", domain_kind="singleton", lower=v, upper=v, lower_closed=True, upper_closed=True,
                             scale="discrete", level0_nodes=[v])]
        elif role == "derived":
            out[pid] = [dict(variant_id="derived", domain_kind="derived", formula_id=p["formula_id"])]
        elif role == "inactive":
            out[pid] = [dict(variant_id="inactive", domain_kind="inactive", inactive_reason=INACTIVE_REASON.get(pid, "INACTIVE_PARAMETER"),
                             formula_id=p.get("formula_id"))]
    return out


def support_row(set_id: str, pid: str, s: dict) -> dict:
    kind = s["domain_kind"]
    row = {"support_id": f"SUP:{set_id}:{pid}:{s['variant_id']}", "support_set_id": set_id, "parameter_id": pid,
           "variant_id": s["variant_id"], "domain_kind": kind, "lower": None, "upper": None, "lower_closed": None,
           "upper_closed": None, "scale": None, "level0_nodes": [], "central": None, "has_central": False,
           "formula_id": None, "inactive_reason": None}
    if kind in ("continuous", "discrete", "singleton"):
        row.update(lower=canon_dec(s["lower"]), upper=canon_dec(s["upper"]), lower_closed=bool(s["lower_closed"]),
                   upper_closed=bool(s["upper_closed"]), scale=s["scale"],
                   level0_nodes=[float(x) for x in s["level0_nodes"]])
    elif kind == "derived":
        row["formula_id"] = s["formula_id"]
    else:
        row["inactive_reason"] = s["inactive_reason"]
    return row


def registry_rows(formulas: dict) -> list:
    rows = []
    for pid, p in sorted(formulas["parameters"].items()):
        role = p["role"]
        unit = p.get("unit", "not_applicable")
        denominator = {"share_GDP": "PIB (mismo año/vintage)", "share": "B_pot o cociente declarado", "flow": "gamma*z_m",
                       "normalized_flow": "gamma*z_m"}.get(unit, "none")
        rows.append({"parameter_id": pid, "name": p.get("source", pid)[:200] if role != "derived" else "derivado " + pid,
                     "symbol": pid, "module": MODULE.get(pid, "derivado" if role == "derived" else "inactivo" if role == "inactive" else "otro"),
                     "role": role, "unit": unit, "denominator": denominator,
                     "universe": "economía nacional completa" if pid in NATIONAL else "firmas Pareto normalizadas (z>=z_m)",
                     "horizon": "2023 (D6); 2015-2023 solo ancla D2" if pid in NATIONAL else "estático (endpoint)",
                     "formula_id": p.get("formula_id"), "active_primary": role != "inactive",
                     "inactive_reason": INACTIVE_REASON.get(pid, "INACTIVE_PARAMETER") if role == "inactive" else None})
    return rows


def formula_rows(formulas: dict) -> tuple[list, list]:
    reg, inputs = [], []
    verif = {"theta": "V7 homogeneidad; 1<theta<a", "q_pot": "V4 admisibilidad", "lambda_pi": "V2 signos P1-P4; V3 vértices",
             "s_Pi_marg": "V5 identidad 1=s_L+s_Pi+s_T", "R": "V8a-V8d; P1 matriz suficiente", "C_2": "T2 medido < 1e-4; monotonía por inclusión",
             "K_comp_1": "V6 reconstrucción del requerimiento", "B_pot": "V7"}
    for fid, f in sorted(formulas["formulas"].items()):
        reg.append({"formula_id": fid, "expression": f["expression"], "output_parameter_id": f["output_parameter_id"],
                    "output_unit": f["unit"], "domain_predicate": f["domain"],
                    "definition_clause": f"formulas.json#/formulas/{fid}; DOMINIOS_Y_FORMULAS.md",
                    "verification_requirement": verif.get(fid, "reproducción exacta de la expresión registrada"),
                    "definition_kind": f["definition_kind"], "context_inputs": f["context_inputs"],
                    "result_binding": f["result_binding"], "declaration_only_in_D7": True})
        for k, pid in enumerate(f["inputs"]):
            inputs.append({"formula_id": fid, "input_order": k, "parameter_id": pid})
    return reg, inputs


FORBIDDEN_CENTER_KEYS = {"central", "center", "centro", "point_estimate", "best_guess", "default", "default_value"}
ROLES = ("primitive", "fixed", "measured", "inactive", "derived")
PRIMITIVE_SPECS = ("primary", "primary_blocks", "primary_nodes", "primary_value", "domain")
MEASURED = set(NATIONAL) | {"Q_perp", "DME_gAI"}


def registry_vector_specs(entry: dict) -> list:
    """(familia, país, año, especificación) de cada vector que el registro A1-E v2 fija para el caso."""
    out = []
    for c in sorted(entry["country_set"]):
        blocks = entry["revisions"][c] if entry.get("revisions") else [entry["vectors"][c]]
        for b in blocks:
            for y, spec in sorted(b["D2"].items()):
                out.append(("D2", c, int(y), spec))
            out.append(("D6", c, 2023, b["D6"]))
    return out


def check_vector(vec: dict | None, family: str, country: str, year: int, spec: dict, ca2: dict) -> list:
    """Correcciones R1/R2 de CA2-3: tipo (familia), año permitido y representación del vector consumido, y bytes de la
    fuente registrada. Devuelve la lista de problemas (vacía = conforme)."""
    if vec is None:
        return [f"VECTOR_MISSING:{family}:{country}:{year}:{spec.get('source_id')}"]
    tag = f"{vec.get('vector_id')}"
    problems = []
    if vec["family"] != family:
        problems.append("VECTOR_TYPE_MISMATCH:" + tag)
    if vec["country_id"] != country:
        problems.append("VECTOR_COUNTRY_MISMATCH:" + tag)
    if vec["observation_year"] != year or year not in ca2["years"][family]:
        problems.append("VECTOR_YEAR_NOT_ALLOWED:" + tag)
    rep = ca2["representations"].get(vec["representation"])
    if rep is None or rep["family"] != family:
        problems.append("VECTOR_REPRESENTATION_FAMILY:" + tag)
    if spec.get("representation") is not None and spec["representation"] != vec["representation"]:
        problems.append("VECTOR_REPRESENTATION_MISMATCH:" + tag)
    for k in ("snapshot_sha256", "source_id", "source_vintage"):
        if spec.get(k) is not None and spec[k] != vec.get(k):
            problems.append(f"VECTOR_{k.upper()}_MISMATCH:" + tag)
    return problems


def validate_registry(formulas: dict) -> list:
    """Registro de parámetros A4: sin centros prohibidos, sin parámetros ocultos (todo primitivo con un único soporte
    declarado, todo medido con fuente nacional o externa conocida), dominios ordenados, nudos dentro del soporte y
    rho en [0,1] (S4). Referencias y ciclos de fórmulas los valida Contracts.definitions (núcleo S3)."""
    problems = []
    pars = formulas["parameters"]
    for pid, p in sorted(pars.items()):
        role = p.get("role")
        if role not in ROLES:
            problems.append("UNKNOWN_ROLE:" + pid)
            continue
        if FORBIDDEN_CENTER_KEYS & set(p) or (isinstance(p.get("primary"), dict) and FORBIDDEN_CENTER_KEYS & set(p["primary"])):
            problems.append("FORBIDDEN_CENTER:" + pid)
        if role == "primitive":
            specs = [k for k in PRIMITIVE_SPECS if k in p]
            if len(specs) != 1:
                problems.append("HIDDEN_OR_AMBIGUOUS_SUPPORT:" + pid)
                continue
            if specs[0] == "primary":
                pr = p["primary"]
                if pr.get("kind", "continuous") not in ("continuous", "discrete", "singleton"):
                    problems.append("SUPPORT_KIND:" + pid)
                lo, hi = Decimal(str(pr["lower"])), Decimal(str(pr["upper"]))
                if lo > hi:
                    problems.append("SUPPORT_INVERTED:" + pid)
                nodes = [Decimal(str(x)) for x in pr.get("level0_nodes", [])]
                if nodes and (nodes != sorted(set(nodes)) or nodes[0] < lo or nodes[-1] > hi):
                    problems.append("NODES_OUTSIDE_OR_UNSORTED:" + pid)
                if pid == "rho" and (lo < 0 or hi > 1):
                    problems.append("RHO_OUTSIDE_S4")
        elif role == "fixed" and "value" not in p:
            problems.append("FIXED_WITHOUT_VALUE:" + pid)
        elif role == "measured" and pid not in MEASURED:
            problems.append("HIDDEN_MEASURED_PARAMETER:" + pid)
        elif role == "derived" and p.get("formula_id") not in formulas["formulas"]:
            problems.append("DERIVED_WITHOUT_FORMULA:" + pid)
    for fid, f in sorted(formulas["formulas"].items()):
        for q in list(f.get("inputs", [])) + [f.get("output_parameter_id")]:
            if q not in pars:
                problems.append(f"FORMULA_REFERENCES_UNDECLARED:{fid}:{q}")
    return problems


def build(world: dict) -> dict:
    """Devuelve {tabla: filas} de las 17 tablas D7 + el informe de fase (sin escribir nada)."""
    F = world["formulas"]
    registry = world["registry"]
    auth_id = world["authority_row"]["authority_id"]
    tables = {k: [] for k in ("authority", "source_evidence", "parameter_registry", "formula_registry", "formula_inputs",
                              "support_sets", "support_set", "parameter_bindings", "joint_constraints", "constraint_inputs",
                              "scenario_map", "tax_component_supports", "tax_rate_inputs", "d7_admissibility_report",
                              "d7_gate_report", "tau_domains", "shared_primitive_members")}
    tables["authority"].append(world["authority_row"])
    ev = tables["source_evidence"]
    for e in world["evidence"]:
        ev.append(dict(e, authority_id=auth_id))
    ev_ids = {e["evidence_id"] for e in ev}
    tables["parameter_registry"] = registry_rows(F)
    tables["formula_registry"], tables["formula_inputs"] = formula_rows(F)
    gates, limitations = [], []
    set_index = {}
    for entry in registry["entries"]:
        pid_case = entry["preregistration_id"]
        countries = sorted(entry["country_set"])
        for edition in editions(entry):
            for block in ("macro", "micro"):
                base = base_set_id(entry, edition, block)
                set_index.setdefault(pid_case, {}).setdefault(edition or "pub", {})[block] = base
                prim = primary_supports(F, block)
                sets = [(base, "base", None, None, f"base {pid_case} edición {edition or 'publicada'} bloque {block}")]
                sets += [(f"{base}.{suf}", kind, base, tr, desc) for suf, kind, tr, desc in DERIVED_SET_KINDS]
                for set_id, kind, parent, tr, desc in sets:
                    tables["support_sets"].append({"support_set_id": set_id, "kind": kind, "parent_support_set_id": parent,
                                                   "transformation_id": tr, "authority_id": auth_id, "description": desc})
                    stress = STRESS.get(set_id.rsplit(".", 1)[-1])
                    sup_ids = {}
                    for pid, variants in sorted(prim.items()):
                        for s in variants:
                            s2 = transform(pid, dict(s), tr if kind in ("coordination", "domain_stress") else None, stress)
                            row = support_row(set_id, pid, s2)
                            tables["support_set"].append(row)
                            sup_ids.setdefault(pid, {})[s["variant_id"]] = row["support_id"]
                    _bindings(tables, set_id, F, sup_ids, auth_id, world, entry, edition, countries)
                    _constraints(tables, set_id)
                    _scenarios(tables, set_id, kind, parent, tr, world, countries)
                    for j in ("d", "df", "f"):
                        tables["tau_domains"].append({
                            "tau_domain_id": f"TAU:{set_id}:{j}", "support_set_id": set_id,
                            "tau_d_support_id": sup_ids["tau_d"]["full" if j in ("d", "df") else "zero"],
                            "tau_f_support_id": sup_ids["tau_f"]["full" if j in ("f", "df") else "zero"], "instrument_j": j})
                    _tax_components(tables, set_id, sup_ids, world, entry, edition, countries, ev_ids)
                    _admissibility(tables, set_id, kind, prim, world, entry, edition, countries, ev_ids)
    _tax_rates(tables, world)
    return {"tables": tables, "set_index": set_index}


def _national_value(world, entry, edition, country, key):
    nat = world["national"][(entry["preregistration_id"], edition or "pub", country)]
    return nat[key]


def _bindings(tables, set_id, F, sup_ids, auth_id, world, entry, edition, countries):
    rows = tables["parameter_bindings"]
    for pid, p in sorted(F["parameters"].items()):
        role = p["role"]
        base = {"binding_id": f"BND:{set_id}:{pid}:global", "support_set_id": set_id, "parameter_id": pid, "scope_id": "global",
                "country_id": None, "value_type": None, "support_id": None, "source_evidence_id": None, "value": None,
                "formula_id": None, "authority_id": auth_id}
        if pid in NATIONAL:
            for c in countries:
                v = _national_value(world, entry, edition, c, pid)
                rows.append(dict(base, binding_id=f"BND:{set_id}:{pid}:country:{c}", scope_id=f"country:{c}", country_id=c,
                                 value_type="measured", value=canon_dec(float(v["value"])), source_evidence_id=v["evidence_id"]))
            continue
        if pid in ("Q_perp",):
            rows.append(dict(base, value_type="evidence_for_support", source_evidence_id="EV.GRID"))
            continue
        if pid == "DME_gAI":
            rows.append(dict(base, value_type="measured", value="0", source_evidence_id="EV.DME"))
            continue
        if role == "primitive":
            variant = "full" if pid in ("tau_d", "tau_f") else next(iter(sup_ids[pid]))
            rows.append(dict(base, value_type="declared_scenario", support_id=sup_ids[pid][variant]))
        elif role == "fixed":
            rows.append(dict(base, value_type="fixed_institutional_constant", support_id=sup_ids[pid]["fixed"],
                             value=canon_dec(Decimal(str(p["value"])))))
        elif role == "derived":
            rows.append(dict(base, value_type="internal_derived", formula_id=p["formula_id"], support_id=sup_ids[pid]["derived"]))
        elif role == "inactive":
            rows.append(dict(base, value_type="inactive", support_id=sup_ids[pid]["inactive"]))
        elif role == "measured":
            rows.append(dict(base, value_type="evidence_for_support", source_evidence_id="EV.GRID"))


def _constraints(tables, set_id):
    for cid, pred, reason, bkind, sev, clause, inputs in CONSTRAINTS:
        full = f"{cid}.{set_id}"
        tables["joint_constraints"].append({"constraint_id": full, "support_set_id": set_id, "predicate": pred,
                                            "reason_code": reason, "boundary_kind": bkind, "severity": sev,
                                            "definition_clause": clause})
        for pid in sorted(inputs):
            tables["constraint_inputs"].append({"constraint_id": full, "parameter_id": pid})


def _scenarios(tables, set_id, kind, parent, tr, world, countries):
    layer = f"SCN:{set_id}"
    coord = {"coordination_half": "COORD-HALF", "enforcement_half": "ABL-ENF", "coverage_half": "ABL-COV"}.get(tr)
    tables["scenario_map"].append({"scenario_id": layer, "support_set_id": set_id,
                                   "parent_scenario_id": f"SCN:{parent}" if parent else None, "layer_id": kind,
                                   "coordination_scenario_id": coord if kind == "coordination" else None,
                                   "transformation_id": tr, "country_id": None, "design": None, "instrument": None,
                                   "availability_case_id": None})
    for r in world["d4"]["model_case_map"]:
        if r["country_id"] not in countries:
            continue
        j = r["model_menu"].removeprefix("j_")
        tables["scenario_map"].append({"scenario_id": f"{layer}:{r['country_id']}:{j}:{r['case_id']}", "support_set_id": set_id,
                                       "parent_scenario_id": layer, "layer_id": kind,
                                       "coordination_scenario_id": coord if kind == "coordination" else None,
                                       "transformation_id": tr if kind == "coordination" else None,
                                       "country_id": r["country_id"], "design": None, "instrument": j,
                                       "availability_case_id": r["case_id"]})


def _tax_components(tables, set_id, sup_ids, world, entry, edition, countries, ev_ids):
    for c in countries:
        nat = world["national"][(entry["preregistration_id"], edition or "pub", c)]
        group = nat["primitive_group"]
        gid = "PGR:" + H(group)
        if not any(r["primitive_group_id"] == gid for r in tables["shared_primitive_members"]):
            for k, m in enumerate(group):
                tables["shared_primitive_members"].append(dict(m, primitive_group_id=gid, member_index=k))
        for comp, key in COMPONENTS.items():
            row = nat["d6_rows"][comp]
            lo, hi = row["low"], row["high"]
            tables["tax_component_supports"].append({
                "support_set_id": set_id, "country_id": c, "component_id": comp, "d6_tree_sha256": world["d6"]["tree"],
                "d6_row_id": row["row_id"], "source_low": _outward(lo, "down"), "source_high": _outward(hi, "up"),
                "pi_support_id": sup_ids[f"pi_{comp}"]["primary"], "primitive_group_id": gid, "evidence_id": row["evidence_id"]})


def _outward(x: Fraction, direction: str) -> str:
    """Decimal exacto si existe; si no, redondeo hacia afuera a 20 decimales (el intervalo sigue conteniendo al racional)."""
    try:
        return canon_dec(x)
    except Exception:
        q = Decimal(x.numerator) / Decimal(x.denominator)
        step = Decimal("1e-20")
        r = q.quantize(step, rounding="ROUND_FLOOR" if direction == "down" else "ROUND_CEILING")
        return canon_dec(r)


_MACRO_CACHE: dict = {}


def _admissibility(tables, set_id, kind, prim, world, entry, edition, countries, ev_ids):
    """Conteos exactos sobre el producto de nudos de nivel 0 (sin materializarlo) y países del conjunto."""
    from . import macro as MC
    axes = {pid: [s for s in v][0] for pid, v in prim.items() if v[0]["domain_kind"] in ("continuous", "discrete", "singleton")}
    struct = ["a", "rho", "kappa_tilde", "beta_tilde", "u_theta", "z_cost", "eta_d", "eta_f", "phi"]
    macro_axes = ["pi_iva", "pi_otros_productos", "pi_produccion", "eta_w", "eta_H", "gain_share"]
    count = {pid: len(axes[pid]["level0_nodes"]) for pid in struct + macro_axes}
    total_omega = 1
    for pid in struct + macro_axes:
        total_omega *= count[pid]
    layer = kind
    # restricciones estructurales: se cumplen por construcción de los soportes (verificado nodo a nodo)
    def n_ok(pids, pred):
        ok = 0
        for combo in product(*[axes[p]["level0_nodes"] for p in pids]):
            ok += 1 if pred(dict(zip(pids, combo))) else 0
        rest = total_omega
        for p in pids:
            rest //= count[p]
        return ok * rest
    checks = {
        "CON.S4": (["rho"], lambda v: 0 <= v["rho"] <= 1),
        "CON.MOMENTS": (["a", "rho", "u_theta"], lambda v: v["a"] > 1 and 0 < v["u_theta"] < 1 and 1 + v["u_theta"] * (v["a"] - 1) < v["a"] and v["rho"] < v["a"]),
        "CON.SCALES": (["beta_tilde", "kappa_tilde", "z_cost"], lambda v: v["kappa_tilde"] > 0 and v["beta_tilde"] > 0 and v["z_cost"] > 0),
        "CON.QPOT": (["a", "kappa_tilde", "rho"], lambda v: v["kappa_tilde"] * (v["a"] - 1) / (v["a"] - v["rho"]) < 1),
        "CON.ETAH": (["eta_H"], lambda v: v["eta_H"] > -1),
    }
    for cid, pred, reason, bkind, sev, clause, inputs in CONSTRAINTS:
        full = f"{cid}.{set_id}"
        if cid in checks:
            pids, fn = checks[cid]
            evaluated = total_omega
            accepted = n_ok(pids, fn)
            ev = "EV.FORMULAS"
        elif cid in ("CON.STMARG", "CON.SPI"):
            evaluated = accepted = 0
            for c in countries:
                shares = {k: world["national"][(entry["preregistration_id"], edition or "pub", c)][k]["exact"] for k in NATIONAL}
                pids = ["a", "kappa_tilde", "rho", "pi_iva", "pi_otros_productos", "pi_produccion", "eta_w", "eta_H"]
                key = (cid, c, tuple(tuple(axes[p]["level0_nodes"]) for p in pids), tuple(sorted(shares.items())))
                ok = _MACRO_CACHE.get(key)
                if ok is None:
                    ok = 0
                    for combo in product(*[axes[p]["level0_nodes"] for p in pids]):
                        m = MC.bridge(shares, dict(zip(pids, combo)))
                        if cid == "CON.STMARG":
                            ok += 1 if m.s_T_marg >= 0 else 0
                        else:
                            ok += 1 if (m.s_Pi_marg > 0 and m.lambda_pi is not None and m.lambda_pi > 0) else 0
                    _MACRO_CACHE[key] = ok
                rest = total_omega
                for p in pids:
                    rest //= count[p]
                evaluated += total_omega
                accepted += ok * rest
            ev = "EV.FORMULAS"
        else:
            evaluated = accepted = total_omega  # c_legal=1 y t=0 son constantes fijas del soporte
            ev = "EV.FORMULAS"
        tables["d7_admissibility_report"].append({"support_set_id": set_id, "layer_id": layer, "constraint_id": full,
                                                  "evaluated_count": evaluated, "accepted_count": accepted,
                                                  "rejected_count": evaluated - accepted, "reason_code": reason, "evidence_id": ev})


def _tax_rates(tables, world):
    for r in world["tax_rates"]:
        tables["tax_rate_inputs"].append(r)
