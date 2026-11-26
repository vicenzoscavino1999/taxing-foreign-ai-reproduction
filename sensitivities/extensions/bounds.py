"""Analytical sensitivities, evaluated from the distributed records in the paper's units."""
import hashlib
import json
from fractions import Fraction as F


def read(path):
    return json.loads(path.read_bytes())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def witness(rows):
    context, = rows["frontier_context"]
    optimum, = rows["capture_ceiling_result"]
    values = {item["parameter_id"]: F(item["value"])
              for item in context["structural_key_payload"]["values"]}
    share = values["kappa_tilde"] * (values["a"] - 1) / (values["a"] - values["rho"])
    require(context["instrument_j"] == "f" and values["phi"] == 1 and values["eta_f"] == F(1, 10)
            and share == F(1, 5) and optimum["computation_status"] == "complete"
            and F(str(optimum["tau_f_at_sup"])) == F(3, 5), "Unexpected withholding-only witness")
    return context["design_v"], values, optimum


def withholding(root):
    records = {}
    for path in sorted((root / "sensitivities/inputs").glob("*_filas.json")):
        rows = read(path)
        if rows["frontier_context"][0]["instrument_j"] == "f":
            design, values, optimum = witness(rows)
            records[design] = (values, optimum)
    require(set(records) == {"G", "N"} and records["G"][0] == records["N"][0],
            "Expected the two designs at the same structural point")
    results = []
    # At this all-formal witness w=(1-x)/x**alpha, q=x**eta.
    # For alpha=0, w(1-w)**eta peaks at 1/(1+eta). At alpha>=eta the cap binds.
    eta = records["G"][0]["eta_f"]
    for alpha, x in [(F(0), F(1, 11)), (F(1, 2), F(1, 4)), (F(1), F(2, 5))]:
        w = 1 / (1 + eta) if alpha == 0 else F(3, 2)
        rate = w / (1 + w)
        require(w**2 * x**int(2 * alpha) == (1 - x)**2, "Reporting condition")
        tenth_power = (F(1, 5) * w)**10 * x
        ceiling = float(tenth_power) ** 0.1
        results.append(dict(alpha=str(alpha), rate=str(rate), reported_share=float(x)**float(eta),
                            ceiling=ceiling, ceiling_tenth_power=str(tenth_power)))
    for _, optimum in records.values():
        require(abs(results[-1]["ceiling"] - optimum["C_2"]) <= optimum["numerical_error"],
                "Base gross-up result differs from the saved ceiling")
    return results


def colombia(root):
    rate_source = read(root / "referencias/fam11/rem166/TRABAJO/EVIDENCIA_B1.json")
    evidence = read(root / "referencias/fam11/rem169/TRABAJO/EVIDENCIA_B2.json")
    manifest = read(root / "datos/fam11/b2/MANIFIESTO_B2.json")
    require(all(e["estado"] == "complete" and not e["sintetico"] for e in (rate_source, evidence))
            and rate_source["j"] == "f" and rate_source["fijos"]["t"] == 0
            and rate_source["raiz_binaria"]["phi"] == manifest["raiz_binaria"]["phi"] == [0, 0.5]
            and evidence["q"] == manifest["q"], "Colombian support or payment share differs")
    rate = F(float.fromhex(rate_source["cotas_hex"][1]))
    share = F(evidence["q"]["hi_exacto"])
    upper = F("0.18974")
    require(0 < rate < 1 and rate == F(rate_source["cotas"][1])
            and share == F(evidence["q"]["hi"]) and (share * rate)**2 < (1 - rate) * upper**2,
            "The rounded-up Colombian ceiling does not enclose the analytical bound")
    groups = []
    for group in manifest["grupos"]:
        key = group["grupo"]
        item = evidence["grupos"][key]
        requirement = F(float.fromhex(item["L_K1_hex"]))
        ids = sorted(group["afirmaciones"])
        require(item["pendientes"] == 0 and requirement == F(item["L_K1"])
                and len(ids) == 2 and {i.split(":")[-4] for i in ids} == {"G", "N"}
                and all(":COL:f:" in i and i.endswith(":macro:guardrail_deuda") for i in ids)
                and requirement - upper > F("0.01"), f"Unresolved claim in {key}")
        groups.append(dict(group=key, claims=ids, requirement_lower=float(requirement),
                           shortfall_lower=float(requirement - upper)))
    require({g["group"] for g in groups} == {f"K{i}" for i in range(1, 7)}
            and len({i for g in groups for i in g["claims"]}) == 12, "Expected 12 Colombian claims")
    return dict(ceiling_upper=float(upper), squared_upper_exact=str((share * rate)**2 / (1 - rate)),
                groups=groups)


def mexico(root):
    public = root / "datos/fam13/s1/publico"
    bridges = {r["conjunto"]: F(r["lambda_max"]) for r in read(public / "T6.json")["filas"]
               if r["pais"] == "MEX" and r["variante"] == "con" and r["estado"] == "ok"
               and r["lambda_max_alcanzado"]}
    contexts = {}
    for path in (root / "referencias/fam03/paquete/objetos").glob("*/PROD3*ci_MEX_f*guardrail_deuda_global.json"):
        record = read(path)
        contexts[record["afirmacion"]] = record["evidencia_ra"]
    accounting = F(3, 10)
    # Upper bound rounded *up*, certified by taking exact tenth powers.
    reporting = F("0.273734")
    exact10 = accounting**10 * F(2, 5)
    require(reporting**10 > exact10, "Rounding direction of reporting bound")
    exact_value = float(exact10) ** 0.1
    results = []
    for line in (public / "T7_anexo.jsonl").read_bytes().splitlines():
        row = json.loads(line)
        if row["pais"] != "MEX" or row["categoria_original"] != "robusta_infactible_certificada":
            continue
        cid, block = row["afirmacion"], row["bloque"]
        evidence = contexts[cid]
        points = evidence["filas_contexto"]
        require(row["j"] == "f" and row["capa"] == "guardrail_deuda" and evidence["D_dme_gai"] == 0,
                f"Unexpected scope of {cid}")
        gain = max(F(str(v["gain"])) for v in points)
        requirement = min(F(str(v["Q"])) for v in points) / (bridges[f"CMP-E1.{block}|MEX"] * gain)
        common_min = min(F(str(v["Q"])) * F(4, 5) / (F(str(v["s_pi"])) * F(str(v["gain"]))) for v in points)
        require(gain == F(1, 10) and abs(requirement - common_min) < F("1e-12")
                and abs(float(requirement) - row["sup_K1"]) < 1e-12, f"Requirement mismatch in {cid}")
        source = root / "referencias/fam01/originales" / (row["testigo_sup"] + "_filas.json")
        require(hashlib.sha256(source.read_bytes()).hexdigest() == row["sup_filas_sha256"],
                f"Witness mismatch in {cid}")
        design, _, optimum = witness(read(source))
        require(design == row["diseno"] and abs(row["sup_C2"] - exact_value) < 1e-12
                and abs(optimum["C_2"] - exact_value) < 1e-12
                and abs(row["sup_G"] - (exact_value - float(requirement))) < 1e-12, f"Gap mismatch in {cid}")
        require(requirement > accounting and (requirement - accounting >= F(1, 100)) == (block == "macro")
                and requirement - reporting > F(1, 100), f"Shortfall mismatch in {cid}")
        results.append(dict(claim=cid, block=block, requirement=float(requirement),
                            accounting_gap=float(requirement - accounting),
                            reporting_gap=float(requirement) - exact_value))
    require(len(results) == len(contexts) == len({r["claim"] for r in results}) == 16
            and sum(r["block"] == "macro" for r in results) == 8, "Expected eight claims in each block")
    return dict(accounting_upper=float(accounting), reporting_upper_rounded_up=float(reporting),
                reporting_upper_tenth_power=str(exact10), claims=results)


def evaluate(root):
    return dict(units="shares of potential AI gains", withholding=withholding(root),
                colombia=colombia(root), mexico=mexico(root))

