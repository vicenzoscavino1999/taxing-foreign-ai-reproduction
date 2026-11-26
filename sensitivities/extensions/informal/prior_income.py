"""Pilot at the two S6.1 points with both tax rates fixed at 15 percent."""
import json
import math
import sys
from dataclasses import replace
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODE = HERE / "kernels" / "linear"
DATA = HERE / "reference"
TD = TF = 0.15


def check_close(actual, expected):
    if not math.isclose(actual, expected, abs_tol=1e-12, rel_tol=1e-12):
        raise ValueError(f"{actual} differs from {expected}")


def compare_payoffs(state, design, burden_prior, interval):
    # Check the interval classification in terms of original income and costs.
    z = (2 * interval.lo if math.isinf(interval.hi)
         else math.sqrt(interval.lo * interval.hi))
    prior_income = state.beta * z
    formal = (1 - burden_prior) * prior_income
    informal = prior_income - state.delta * z**state.theta
    ai_income = state.gamma * z
    ai_cost = model.k_formal(state, TF) * z**state.rho
    ai_burden = model.tilde_d(TD, state.eta_d)
    if design == "G":
        formal_gain = (1 - ai_burden) * ai_income - ai_cost
    else:
        formal_gain = (1 - ai_burden) * (ai_income - ai_cost)
    informal_gain = ai_income - state.kappa0 * z**state.rho
    prior = "F" if formal >= informal else "I"
    options = {"N": max(formal, informal), "F": formal + formal_gain,
               "I": informal + informal_gain}
    if (prior, max(options, key=options.get)) != (interval.prior, interval.label):
        raise ValueError("Interval inconsistent with direct choice of payoffs")


def evaluate(state, design, allow_underreporting):
    burden = model.tilde_d(TD, state.eta_d) if allow_underreporting else TD
    prior_share = model.r_star(TD, state.eta_d) if allow_underreporting else 1.0
    # Only the prior-income tax differential enters the choice between statuses.
    choices = replace(state, beta=state.beta * (burden / TD))
    ev = model.evaluate(choices, TD, TF, design)
    prior_mass = post_mass = exits = entries = total = 0.0
    prior_formal_income = post_formal_income = 0.0
    for iv in ev.intervals:
        compare_payoffs(state, design, burden, iv)
        mass = model.pareto_moment(state.a, state.z_m, 0, iv.lo, iv.hi)
        income = state.beta * model.pareto_moment(state.a, state.z_m, 1, iv.lo, iv.hi)
        formal_before = iv.prior == "F"
        formal_after = iv.label == "F" or (iv.label == "N" and formal_before)
        prior_mass += mass * formal_before
        post_mass += mass * formal_after
        exits += mass * (formal_before and not formal_after)
        entries += mass * (not formal_before and formal_after)
        total += mass
        prior_formal_income += income * formal_before
        post_formal_income += income * formal_after
    check_close(total, 1.0)
    check_close(prior_mass, ev.mass_prior_F)
    check_close(post_mass, prior_mass - exits + entries)
    check_close(entries, 0)
    # Receipts always use actual beta, both with AI and in the no-AI counterfactual.
    prior_tax_change = TD * prior_share * (post_formal_income - prior_formal_income)
    check_close(prior_tax_change, TD * prior_share * ev.E0 * state.beta / choices.beta)
    ai_tax = TD * ev.r * ev.A
    withholding = TF * ev.B_f
    domestic = prior_tax_change + ai_tax
    receipts = (domestic + withholding) / state.B_pot
    if not allow_underreporting:
        check_close(receipts, ev.CS)
    return dict(formal_before=prior_mass, formal_after=post_mass,
                exits=exits, entries=entries, informal_adopters=ev.mass_I,
                topology=ev.topology, prior_income_reported_fraction=prior_share,
                prior_tax_change=prior_tax_change / state.B_pot,
                domestic_ai=ai_tax / state.B_pot, domestic=domestic / state.B_pot,
                withholding=withholding / state.B_pot, total_incremental=receipts)


if __name__ == "__main__":
    manifest = (CODE / "SHA256SUMS_copia.txt").read_text(encoding="utf-8-sig")
    for line in manifest.splitlines():
        expected, path = line.split(" *", 1)
        if sha256((CODE / path).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Kernel hash mismatch for {path}")
    sys.path.insert(0, str(CODE / "src"))
    from paper2b import model

    points = json.loads((DATA / "puntos.json").read_bytes())
    archived = json.loads((DATA / "mallas.json").read_bytes())["fixed"]
    results = {}
    for design, point in points.items():
        state = model.state_from_primitives(point["parameters"])
        original = evaluate(state, design, False)
        ref, = (n for n in archived[design] if (n["td"], n["tf"]) == (TD, TF))
        for key, refkey in (("total_incremental", "CS"), ("formal_before", "prior_formal"),
                            ("exits", "switched"), ("informal_adopters", "informal")):
            check_close(original[key], ref[refkey])
        node, = (n for n in point["nodes"] if (n["tau_d"], n["tau_f"]) == (TD, TF))
        check_close(original["total_incremental"], node["CS"])
        if original["topology"] != ref["topology"] or original["topology"] != node["topology"]:
            raise ValueError(f"{design} topology differs from archive")
        results[design] = dict(id=point["id"], parameters=point["parameters"],
                               base=original, variant=evaluate(state, design, True))
    output = dict(tau_d=TD, tau_f=TF, incidence="E11", rates="fixed",
                  revenue_units="fraction of B_pot relative to the no-AI counterfactual",
                  mass_units="fraction of all establishments", cases=results)
    print(json.dumps(output, indent=2, allow_nan=False))
