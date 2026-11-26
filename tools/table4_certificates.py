"""Verify Oxford Table 4 using the archived witnesses and the incidence lemma (Appendix S6)."""
from functools import lru_cache
from math import inf, nextafter
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sensitivities/extensions"))
from bounds import mexico, read, require

ORIGINAL_SIGN = "cambio_de_signo_certificado"
LATER_SIGN = "inconclusa_por_testigos_en_tolerancia"
SHORTFALL = "robusta_infactible_certificada"


def combined_certificates():
    records = read(ROOT / "sensitivities/reference/accepted.json")["results"]
    certificates = {}
    for design in ("G", "N"):
        result = records[f"statutory_{design}_df_base"]["content"]
        low, high = result["intervalo_certificado"]
        require(result["tipo_error"] == "certified_bound" and low <= result["C2"] <= high
                and result["regla"] == "estatutaria" and result["diseno"] == design
                and result["menu"] == "df", f"Invalid combined-menu certificate for {design}")
        certificates[design] = result
    return certificates


def verify_claims(rows):
    """Return one evidence row per claim after checking both allocations against the same requirement."""
    require(len(rows) == len({r["afirmacion"] for r in rows}) == 1728, "Expected 1,728 distinct claims")
    aliases = {a["cell_id_contractual"]: a for a in read(
        ROOT / "nucleo_s6/instalacion/datos/paso4/lista_R2_testigos.json")["unidades"]}
    selected = read(ROOT / "nucleo_s6/raiz/tmp/p1b_global_h4_paso4_3_7_2026-10-09_lima1913"
                    / "demo/b_v2_p1b/cell_selection.json")["S1"]
    choices = {(s["afirmacion"], s["reason"]): s for s in selected}
    with (ROOT / "datos/fam01/definiciones.jsonl").open(encoding="utf-8") as stream:
        definitions = {r["unidad"]: r["definicion"] for r in map(json.loads, stream)}
    statutory = combined_certificates()
    mexican = mexico(ROOT)
    requirements = {r["claim"]: r["requirement"] for r in mexican["claims"]}
    require(set(requirements) == {r["afirmacion"] for r in rows if r["categoria_original"] == SHORTFALL},
            "Global shortfall certificates do not match the claims")
    originals = ROOT / "referencias/fam01/originales"

    @lru_cache(None)
    def witness(cell):
        alias = aliases[cell]
        unit = alias["unidad"]
        definition = definitions[unit]
        data = read(originals / (unit + "_filas.json"))
        record = read(originals / (unit + ".json"))["resultado"]
        ctx, = data["cell_context"]
        frontier, = data["frontier_context"]
        ceiling, = data["capture_ceiling_result"]
        result, = data["confrontation_result"]
        gap, = [g for g in data["convergence_result"] if g["quantity_id"] == "G:" + result["cell_id"]]
        low, high = gap["value_before"], gap["value_after"]
        require(result["cell_id"] == ctx["cell_id"] == record["cell_id"] == alias["cell_id_e12"]
                and ceiling["frontier_id"] == frontier["frontier_id"] == alias["frontier_id"],
                f"Unmatched cell or frontier: {unit}")
        require(result["computation_status"] == "complete" and record["completitud"]["estado"] == "completa"
                and all(record["precomprobaciones"].values()) and record["poscomprobaciones"]["K_comp_1_en_K1"]
                and record["poscomprobaciones"]["C2_interseca_certificado"], f"Incomplete witness: {unit}")
        require(gap["status"] == "pass" and gap["coverage_complete"]
                and gap["method_id"] == "certified_bound_C2_closed_form_K1" and low <= result["G"] <= high
                and definition["K1_en_punto"][0] <= result["K_comp_1"] <= definition["K1_en_punto"][1],
                f"Invalid gap interval or requirement: {unit}")
        return definition, ctx, frontier["structural_key_payload"], low, high

    def claim_witness(row, side):
        claim = row["afirmacion"]
        selected = choices[claim, "witness_" + side]
        cell = row["testigo_" + side]
        definition, ctx, key, low, high = witness(cell)
        # Two vintages can select the same archived cell. Each must name it in its own selection.
        leaf = selected["hoja"].replace(":historical_anchor:", ":primary:")
        require(selected["cell_id"] == cell and selected["estado"] == "definitivo"
                and selected["witness_of"] == claim + ":" + side
                and selected["witness_of"] in aliases[cell]["witness_of"]
                and leaf == definition["claim_id_hoja"].replace(":historical_anchor:", ":primary:"),
                f"Unmatched {side} witness: {claim}")
        require(ctx["layer"] == row["capa"] and ctx["design_v"] == row["diseno"]
                and ctx["bound_variant"] == row["cota"] and ctx["eta_w_block"] == row["bloque"]
                and ctx["instrument_j"] == definition["instrumento_hoja"] and ctx["country_id"] == definition["pais_hoja"]
                and row["j"] in ("null", ctx["instrument_j"]) and row["pais"] in ("null", ctx["country_id"]),
                f"Incompatible {side} witness: {claim}")
        return definition, key, low, high

    evidence = []
    for row in rows:
        claim, category = row["afirmacion"], row["categoria_original"]
        definition, key, linear_low, _ = claim_witness(row, "sup")
        _, _, _, unfavourable_high = claim_witness(row, "inf")
        menu = definition["instrumento_hoja"]
        domain = key["tau_domain"]
        statutory_low = linear_low
        if menu == "df":
            certificate = statutory[row["diseno"]]
            values = {v["parameter_id"]: float(v["value"]) for v in key["values"]}
            require(values == certificate["punto_estructural"] and key["design_v"] == certificate["diseno"]
                    and key["instrument_j"] == "df" and all(
                        float(domain[f"tau_{t}_lower"]) == 0 and domain[f"tau_{t}_lower_closed"]
                        and float(domain[f"tau_{t}_upper"]) == certificate["topes"][f"bar_tau_{t}"]
                        and domain[f"tau_{t}_upper_closed"] for t in ("d", "f")),
                    f"Statutory certificate differs from favourable point or rate domain: {claim}")
            statutory_low = nextafter(certificate["intervalo_certificado"][0] - definition["K1_en_punto"][1], -inf)
        elif menu == "d":
            require(float(domain["tau_f_upper"]) == 0, f"Domestic menu has positive withholding: {claim}")
        else:
            phi, = [float(v["value"]) for v in key["values"] if v["parameter_id"] == "phi"]
            require(menu == "f" and float(domain["tau_d_upper"]) == 0 and phi == definition["punto"]["phi"] == 1,
                    f"Withholding witness requires full gross-up: {claim}")

        # Dominance transfers the archived upper bound at the unfavourable point.
        # The 16 uniform shortfalls additionally need a bound over the entire support.
        global_high = None
        if category == SHORTFALL:
            global_high = nextafter(mexican["reporting_upper_rounded_up"] - nextafter(requirements[claim], -inf), inf)
            require(global_high <= -0.01, f"Global shortfall unresolved: {claim}")
            verdict = "robustly infeasible"
        else:
            require(category in (ORIGINAL_SIGN, LATER_SIGN) and min(linear_low, statutory_low) > 0.01
                    and unfavourable_high < -0.01, f"Opposite signs beyond tolerance unverified: {claim}")
            verdict = "inconclusive"
        evidence.append(dict(claim=claim, classification_both_rules=verdict, original_category=category,
                             favourable_menu=menu, favourable_witness=row["testigo_sup"],
                             unfavourable_witness=row["testigo_inf"], linear_favourable_lower=linear_low,
                             statutory_favourable_lower=statutory_low, unfavourable_upper_both=unfavourable_high,
                             global_upper_both=global_high))
    return evidence

