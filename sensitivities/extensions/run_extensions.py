"""Reproduce the revised article's additional results using the public package."""
import argparse
import json
from math import floor
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from bounds import evaluate, read, require


def reproduce_menus(output):
    source = HERE / "informal"
    def run(script, *arguments, stdout=None):
        subprocess.run([sys.executable, "-B", "-s", str(source / script), *map(str, arguments)],
                       cwd=source, check=True, stdout=stdout)
    run("comparar.py", output)
    run("mallas.py", output / "mallas.json")
    with (output / "prior_income.json").open("xb") as stream:
        run("prior_income.py", stdout=stream)
    files = {p.name for p in (source / "reference").glob("*.json")}
    require(len(files) == 14 and files == {p.name for p in output.glob("*.json")}, "Missing menu results")
    for name in sorted(files):
        expected = read(source / "reference" / name)
        actual = read(output / name)
        if name.startswith(("G_", "N_")):
            expected.pop("seconds")
            actual.pop("seconds")
        require(actual == expected, f"Scientific results differ in {name}")


def summary(output, bounds):
    menus = output / "menus"
    rows = read(menus / "resumen.json")
    grids = read(menus / "mallas.json")
    cases = read(menus / "prior_income.json")["cases"]
    text = ["# Results for the revised article", "", "## Domestic and combined menus", "",
            "Each row compares independently optimized menus at the same structural point. "
            "The two economies were selected because some formerly formal establishments adopt informally at rates on the model grid.",
            "", "| Design | Withholding cap | Incidence | Domestic ceiling / combined ceiling |",
            "|---|---:|---|---:|"]
    designs = {"G": "Gross", "N": "Net"}
    incidence = {"E11": "Linear", "estatutaria": "Statutory"}
    for row in rows:
        lo, hi = row["percent"]
        require(f"{lo:.1f}" == f"{hi:.1f}", "Ratio rounding differs across certificate endpoints")
        text.append(f"| {designs[row['design']]} | {row['cap']}% | {incidence[row['rule']]} | {lo:.1f}% |")
    text += ["", "The grid comparison evaluates recorded rates. A grid maximum can differ from the continuous ceiling.", ""]
    for cap, grid in grids["grids"].items():
        selected = [r for r in grid if r["some"]]
        text.append(f"- At a {cap}% withholding cap, {len(selected)} of {len(grid)} grids have a maximizing "
                    "policy at which some formerly formal establishments adopt informally.")
    text += ["", "## Reporting prior income with both tax rates at 15%", "",
             "Receipts are measured relative to the no-AI economy under each reporting rule, as a percentage "
             "of potential AI gains. Formal shares refer to all establishments after adoption.", "",
             "| Design | Formal share, base | Formal share, reporting allowed | Incremental receipts, base | Incremental receipts, reporting allowed |",
             "|---|---:|---:|---:|---:|"]
    for design, case in cases.items():
        base, alternative = case["base"], case["variant"]
        text.append(f"| {designs[design]} | {base['formal_after']:.2%} | {alternative['formal_after']:.2%} | "
                    f"{base['total_incremental']:.3%} | {alternative['total_incremental']:.3%} |")
    text += ["", "Allowing underreporting of prior income increases incremental receipts in both economies. "
             "At these rates the loss of tax on prior income still exceeds the receipts from AI profits and withholding.",
             "", "## Withholding alone at the original favorable point", "",
             "Full contractual gross-up is held fixed. The schedule parameter changes the cost of concealing a payment.", "",
             "| Cost parameter | Maximizing withholding rate | Ceiling as a share of potential gains |", "|---:|---:|---:|"]
    from fractions import Fraction
    for r in bounds["withholding"]:
        text.append(f"| {r['alpha']} | {float(Fraction(r['rate'])):.2%} | {r['ceiling']:.4f} |")
    col = bounds["colombia"]
    count = sum(len(g["claims"]) for g in col["groups"])
    text += ["", "## Colombia and Mexico", "",
             f"In Colombia, halving contractual incidence with concealment costs fixed gives a withholding-only "
             f"upper bound of {col['ceiling_upper']:.5f}. All {count} macro, debt-consistent claims clear the "
             f"one-point shortfall criterion. Each shortfall exceeds "
             f"{floor(100000*min(g['shortfall_lower'] for g in col['groups']))/1000:.3f} percentage points of potential gains.", "",
             "In Mexico the accounting ceiling is 0.30. The model's reporting response lowers the upper bound "
             "to 0.273734 (rounded up). Shortfalls below are requirements minus ceilings, in percentage points of potential gains.", "",
             "| Block | Claims | Shortfall with full reporting | Shortfall with model reporting |",
             "|---|---:|---:|---:|"]
    for block in ("macro", "micro"):
        part = [r for r in bounds["mexico"]["claims"] if r["block"] == block]
        def gap_range(field):
            vals = [100 * r[field] for r in part]
            return f"{min(vals):.2f} to {max(vals):.2f}"
        text.append(f"| {block.title()} | {len(part)} | {gap_range('accounting_gap')} | {gap_range('reporting_gap')} |")
    text += ["", "The accounting bound establishes the one-point margin for eight macro claims. "
             "The reporting response establishes it for the eight micro claims.", "",
             "The certified menu intervals, grid results and fixed-rate pilot are in [menus/](menus/). "
             "The inputs to the inequalities and individual claim results are in [bounds.json](bounds.json).", ""]
    return "\n".join(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    output = parser.parse_args().out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    reproduce_menus(output / "menus")
    bounds = evaluate(ROOT)
    (output / "bounds.json").write_text(json.dumps(bounds, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (output / "results.md").write_text(summary(output, bounds), encoding="utf-8")
    print(f"EXTENSIONS REPRODUCED. Results: {output / 'results.md'}")


if __name__ == "__main__":
    main()

