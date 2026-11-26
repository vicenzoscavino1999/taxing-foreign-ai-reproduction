"""Reproduce the post-base sensitivities of the article from the package: Table 2 (lower rate caps, allocation (E11) and
statutory allocation) and the adoption-threshold results of Section 5.1.

All of these were designed after the base results (article, Appendix "chronology"). They are certified ceilings at the
favorable witnesses of Table 3, with the structural point held fixed and the rates re-optimized, plus two floating-point
diagnostics that are NOT certifications.

What it does, from a new output folder (nothing is overwritten):
  1. checks the package kernel (nucleo_s6/instalacion/src, 37 files) and the six witness-row files in inputs/ against
     their manifests;
  2. builds the statutory variant of the kernel in <out>/variant (construir_variante.py: one new module and exact patches)
     and checks it against manifests/variant_SHA256SUMS.txt;
  3. runs 25 computations, each in its own process with the production numerical environment and an external limit of
     2,400 s (calculo.py, testigos_propios.py, diagnostico_salto.py, diagnostico_umbral.py);
  4. compares every result with the accepted results in reference/accepted.json (bit for bit on the certified values,
     intervals, status, rates and box counts; whole documents for the diagnostics);
  5. writes table3.md, table3.csv, threshold.md and summary.json, and checks the rounded cells against the article.
Exit code 0 only if every check passes.

Usage, from the package root with the package Python (see README.md):
  python -B -I sensitivities/run_sensitivities.py [--out salidas/sensitivities_<new name>]
Takes about one minute.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction
from decimal import Decimal
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
PKG = HERE.parent
ENV = {"PYTHONHASHSEED": "0", "TZ": "UTC", "BLIS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1",
       "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "VECLIB_MAXIMUM_THREADS": "1", "PYTHONDONTWRITEBYTECODE": "1"}
LIMIT_S = 2400
CERT_FIELDS = ("C2_hex", "error_hex", "intervalo_certificado", "estado", "motivo", "tau_d_en_sup", "tau_f_en_sup",
               "alcanzado", "cajas", "tipo_error")
TAGS = ((0.15, "015"), (0.30, "030"))

# Table 2 of the article, as printed (percent of the potential AI gain; domestic share in percent of the combined ceiling)
ARTICLE_TABLE3 = {
    ("G", 0.15): ("36.93", "36.93", "33.52", "3.47", "90.8", "90.8"),
    ("G", 0.30): ("41.44", "41.44", "33.52", "8.27", "80.9", "80.9"),
    ("N", 0.15): ("29.37", "29.35", "26.82", "3.47", "91.3", "91.4"),
    ("N", 0.30): ("32.49", "32.40", "26.82", "8.27", "82.5", "82.8"),
}
# Section 5.1 of the article, as printed
ARTICLE_51 = {"statutory_G_base": "0.7821", "statutory_N_base": "0.5518", "E11_G_base": "0.7917", "E11_N_base": "0.5628",
              "decrease_G_pp": "0.952", "decrease_N_pp": "1.097", "jump_statutory_G": "0.588",
              "threshold_statutory_G_015": "0.82", "threshold_statutory_G_030": "0.77"}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def check_manifest(manifest, root):
    bad = []
    for line in Path(manifest).read_text(encoding="utf-8").splitlines():
        h, rel = line.split(maxsplit=1)
        f = Path(root) / rel.lstrip("*")
        if not f.is_file() or sha(f) != h:
            bad.append(rel.lstrip("*"))
    return bad


def steps(out):
    s = []
    for D in "GN":
        for F, tag in TAGS:
            s.append(("E11_%s_df_d035_f%s" % (D, tag), "calculo.py", ["E11", D, "df", "0.35", str(F), "testigo"]))
            s.append(("statutory_%s_df_d035_f%s" % (D, tag), "calculo.py", ["estatutaria", D, "df", "0.35", str(F), "testigo"]))
        s.append(("E11_%s_df_base" % D, "calculo.py", ["E11", D, "df", "0.6", "0.6", "testigo"]))
        s.append(("statutory_%s_df_base" % D, "calculo.py", ["estatutaria", D, "df", "0.6", "0.6", "testigo"]))
    s.append(("own_witnesses", "testigos_propios.py", []))
    for R in ("E11", "estatutaria"):
        for D in "GN":
            s.append(("jump_%s_%s" % (R, D), "diagnostico_salto.py", [R, D]))
    for R in ("E11", "estatutaria"):
        for D in "GN":
            for F, tag in TAGS:
                s.append(("threshold_%s_%s_f%s" % (R, D, tag), "diagnostico_umbral.py", [R, D, str(F), "0.35"]))
    return s


def run_step(out, name, script, args, env, log):
    dest = out / (name + ".json")
    t0 = time.time()
    with open(out / (name + ".console.txt"), "xb") as fo:
        try:
            rc = subprocess.run([sys.executable, "-B", "-I", str(HERE / script), *args, str(dest)], cwd=PKG, env=env,
                                stdin=subprocess.DEVNULL, stdout=fo, stderr=subprocess.STDOUT, timeout=LIMIT_S).returncode
        except subprocess.TimeoutExpired:
            rc = "timeout"
    dt = time.time() - t0
    log.write("%s rc=%s seconds=%.2f\n" % (name, rc, dt))
    log.flush()
    print("  %-34s rc=%s  %.1f s" % (name, rc, dt), flush=True)
    return rc == 0


def compare(name, new, ref):
    """List of differences between a new result and its accepted reference."""
    if name == "own_witnesses":
        diffs = []
        rt = {(t["diseno"], t["menu"]): t for t in ref["testigos"]}
        nt = {(t["diseno"], t["menu"]): t for t in new["testigos"]}
        if set(rt) != set(nt) or new["anexo_sha256"] != ref["anexo_sha256"]:
            return ["witness set or annex differs"]
        for k, r in rt.items():
            n = nt[k]
            for f in ("testigo", "unidades_empatadas", "parametros", "C2_base", "filas_sha256"):
                if n[f] != r[f]:
                    diffs.append("%s %s: %s" % (k, f, "differs"))
            strip = lambda c: {x: y for x, y in c.items() if x != "segundos"}  # noqa: E731
            if [strip(c) for c in n["certificados"]] != [strip(c) for c in r["certificados"]]:
                diffs.append("%s: certificates differ" % (k,))
        return diffs
    if name.startswith(("jump_", "threshold_")):
        return [] if new == ref else ["diagnostic document differs"]
    return [f for f in CERT_FIELDS if new.get(f) != ref.get(f)]


def enclosure(bounds, digits):
    """Format an exact or binary64 interval outward at the requested decimal precision."""
    scale = 10**digits
    low, high = (Fraction(x) * scale for x in bounds)
    lower = low.numerator // low.denominator
    upper = -((-high.numerator) // high.denominator)
    return "[" + ", ".join(format(Decimal(n).scaleb(-digits), f".{digits}f") for n in (lower, upper)) + "]"


def pct(x, nd):
    return "%.*f" % (nd, 100.0 * x)


def main():
    ap = argparse.ArgumentParser(description="Reproduce Table 2 and the Section 5.1 threshold results.")
    ap.add_argument("--out", type=Path, help="new output folder (default: salidas/sensitivities_<UTC time>)")
    a = ap.parse_args()
    out = (PKG / (a.out or Path("salidas") / ("sensitivities_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")))).resolve()
    if out.exists():
        raise SystemExit("the output folder already exists; choose a new one: %s" % out)
    out.mkdir(parents=True)
    checks = {}
    t0 = time.time()
    print("Output:", out)

    # 1. integrity of the kernel and of the inputs
    checks["kernel nucleo_s6/instalacion/src matches manifests/kernel_SHA256SUMS.txt (37 files)"] = \
        not check_manifest(HERE / "manifests" / "kernel_SHA256SUMS.txt", PKG / "nucleo_s6" / "instalacion")
    checks["inputs/ match inputs/SHA256SUMS.txt (6 witness-row files)"] = \
        not check_manifest(HERE / "inputs" / "SHA256SUMS.txt", HERE / "inputs")
    if not all(checks.values()):
        print(json.dumps(checks, indent=1))
        raise SystemExit(1)

    env = dict(os.environ, **ENV, SENS_VARIANTE_SRC=str(out / "variant" / "src"))
    with open(out / "log.txt", "x", encoding="utf-8") as log:
        # 2. statutory variant
        print("Building the statutory variant of the kernel:")
        dest = out / "variant"
        with open(out / "build_variant.console.txt", "xb") as fo:
            rc = subprocess.run([sys.executable, "-B", "-I", str(HERE / "construir_variante.py"), str(dest)], cwd=PKG, env=env,
                                stdin=subprocess.DEVNULL, stdout=fo, stderr=subprocess.STDOUT, timeout=LIMIT_S).returncode
        log.write("build_variant rc=%s\n" % rc)
        checks["statutory variant built (construir_variante.py rc=0)"] = rc == 0
        checks["statutory variant matches manifests/variant_SHA256SUMS.txt (38 files)"] = rc == 0 and \
            (dest / "SHA256SUMS_variante.txt").read_bytes() == (HERE / "manifests" / "variant_SHA256SUMS.txt").read_bytes()
        if not all(checks.values()):
            print(json.dumps(checks, indent=1))
            raise SystemExit(1)
        # 3. computations
        print("Computations (each in its own process):")
        ok_runs = {name: run_step(out, name, script, args, env, log) for name, script, args in steps(out)}
    checks["all 25 computations finished with rc=0"] = all(ok_runs.values())
    if not all(ok_runs.values()):
        print(json.dumps({k: v for k, v in ok_runs.items() if not v}, indent=1))
        raise SystemExit(1)

    # 4. comparison with the accepted results
    ref = read(HERE / "reference" / "accepted.json")
    R = {name: read(out / (name + ".json")) for name, _, _ in steps(out)}
    mism = {}
    for name in R:
        r = ref["results"][name]["content"]
        d = compare(name, R[name], r)
        if d:
            mism[name] = d
    checks["25/25 results identical to the accepted results (reference/accepted.json)"] = not mism

    # 5. Table 2
    own = {(t["diseno"], t["menu"]): t for t in R["own_witnesses"]["testigos"]}
    rows, cells_ok = [], True
    for D in "GN":
        dom = own[(D, "d")]["certificados"][0]
        for F, tag in TAGS:
            E, S = R["E11_%s_df_d035_f%s" % (D, tag)], R["statutory_%s_df_d035_f%s" % (D, tag)]
            fw = next(c for c in own[(D, "f")]["certificados"] if c["topes_activos"][1] == F)
            cells = (pct(E["C2"], 2), pct(S["C2"], 2), pct(dom["C2"], 2), pct(fw["C2"], 2),
                     pct(dom["C2"] / E["C2"], 1), pct(dom["C2"] / S["C2"], 1))
            match = cells == ARTICLE_TABLE3[(D, F)]
            cells_ok &= match
            attained = all(x["alcanzado"] and x["estado"] == "complete" and [x["tau_d_en_sup"], x["tau_f_en_sup"]] == [0.35, F]
                           for x in (E, S))
            rows.append({"design": D, "tau_f_cap": F, "df_E11": E["C2"], "df_E11_interval": E["intervalo_certificado"],
                         "df_statutory": S["C2"], "df_statutory_interval": S["intervalo_certificado"],
                         "d_only": dom["C2"], "d_only_interval": dom["intervalo"], "f_only": fw["C2"], "f_only_interval": fw["intervalo"],
                         "cells": cells, "matches_article": match, "combined_attained_at_caps_both_allocations": attained,
                         "menus_disjoint_E11": Fraction(E["intervalo_certificado"][0]) > Fraction(dom["intervalo"][1])
                         and Fraction(dom["intervalo"][0]) > Fraction(fw["intervalo"][1]),
                         "menus_disjoint_statutory": Fraction(S["intervalo_certificado"][0]) > Fraction(dom["intervalo"][1])
                         and Fraction(dom["intervalo"][0]) > Fraction(fw["intervalo"][1])})
    checks["Table 2: the 24 rounded cells equal the printed article"] = cells_ok
    checks["Table 2: every combined ceiling attained at the caps (0.35; cap) under both allocations"] = \
        all(r["combined_attained_at_caps_both_allocations"] for r in rows)
    checks["Table 2: certified intervals of df, d and f disjoint in every row, both allocations"] = \
        all(r["menus_disjoint_E11"] and r["menus_disjoint_statutory"] for r in rows)
    checks["Table 2: d-only witnesses have tau_f = 0 and f-only witnesses phi = 1 (allocations coincide)"] = all(
        own[(D, "d")]["certificados"][0]["tasas"][1] == 0.0 and own[(D, "f")]["parametros"]["phi"] == 1.0 for D in "GN")

    # Section 5.1
    sG, sN, eG, eN = (R["statutory_G_df_base"], R["statutory_N_df_base"], R["E11_G_df_base"], R["E11_N_df_base"])

    def drop_pp(e, s):  # certified decrease (E11 - statutory), percentage points, from the two intervals
        return (100 * (Fraction(e["intervalo_certificado"][0]) - Fraction(s["intervalo_certificado"][1])),
                100 * (Fraction(e["intervalo_certificado"][1]) - Fraction(s["intervalo_certificado"][0])))
    dG, dN = drop_pp(eG, sG), drop_pp(eN, sN)
    jump = R["jump_estatutaria_G"]["cruce"]
    thr = {(Rr, D, F): R["threshold_%s_%s_f%s" % (Rr, D, tag)] for Rr in ("E11", "estatutaria") for D in "GN" for F, tag in TAGS}
    got51 = {"statutory_G_base": "%.4f" % sG["C2"], "statutory_N_base": "%.4f" % sN["C2"], "E11_G_base": "%.4f" % eG["C2"],
             "E11_N_base": "%.4f" % eN["C2"], "decrease_G_pp": "%.3f" % float(dG[0]), "decrease_N_pp": "%.3f" % float(dN[0]),
             "jump_statutory_G": "%.3f" % jump["ultimo_con_adopcion"]["tau_d"],
             "threshold_statutory_G_015": "%.2f" % thr[("estatutaria", "G", 0.15)]["cruce"]["ultimo_con_adopcion"]["tau_d"],
             "threshold_statutory_G_030": "%.2f" % thr[("estatutaria", "G", 0.30)]["cruce"]["ultimo_con_adopcion"]["tau_d"]}
    checks["Adoption results: ceilings and diagnostics match their reference values"] = got51 == ARTICLE_51
    checks["Section 5.1: gross statutory supremum certified, attainment undecided (SUP_ATTAINMENT_UNDECIDED_AT_JUMP_CURVE)"] = (
        sG["estado"] == "incomplete" and sG["motivo"] == "SUP_ATTAINMENT_UNDECIDED_AT_JUMP_CURVE" and sG["tipo_error"] == "certified_bound"
        and sG["error_certificado"] <= 1e-7)
    checks["Section 5.1: net statutory ceiling and both (E11) base ceilings attained at the caps (0.6; 0.6)"] = all(
        x["estado"] == "complete" and x["alcanzado"] and [x["tau_d_en_sup"], x["tau_f_en_sup"]] == [0.6, 0.6] for x in (sN, eG, eN))
    checks["Section 5.1: certified decreases are positive (intervals do not overlap)"] = dG[0] > 0 and dN[0] > 0
    checks["Section 5.1: with the 0.35 cap, formal establishments adopt at the caps (L > 0) in the gross design"] = all(
        thr[(Rr, "G", F)]["L_en_tope"] > 0 and thr[(Rr, "G", F)]["cruce"]["por_encima_del_tope"] for Rr in ("E11", "estatutaria") for F, _ in TAGS)

    # outputs
    hdr = ("design", "tau_f_cap", "df_E11_pct", "df_statutory_pct", "d_only_pct", "f_only_pct", "domestic_share_E11_pct",
           "domestic_share_statutory_pct", "matches_article")
    with open(out / "table3.csv", "x", encoding="utf-8", newline="\n") as f:
        f.write(",".join(hdr) + "\n")
        for r in rows:
            f.write(",".join([r["design"], "%.2f" % r["tau_f_cap"], *r["cells"], str(r["matches_article"]).lower()]) + "\n")
    L = ["# Table 2 — favorable capture ceilings under lower rate caps (reproduced)", "",
         "Ceilings in percent of the potential AI gain; domestic share = domestic-only ceiling as a percentage of the combined "
         "ceiling. At a domestic cap of 35%, rates are optimized at each menu's favorable base point (Table 3). "
         "G and N denote gross and net domestic taxation. These illustrative scenarios were chosen after the base results.", "",
         "| Design | Withholding cap | Combined, linear | Combined, statutory | Domestic only | Withholding only | Domestic share, linear (%) | Domestic share, statutory (%) |",
         "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append("| %s | %.2f | %s |" % (r["design"], r["tau_f_cap"], " | ".join(r["cells"])))
    L += ["", "### Appendix Tables S7 and S8", "",
          "Ceilings are shares of potential gains. The difference is statutory minus linear, in percentage points. "
          "The domestic shares are percentages of the combined ceiling. Interval endpoints are rounded outward.", "",
          "| Design | Withholding cap | Combined, linear | Combined, statutory | Difference (pp) | Domestic share, linear (%) | Domestic share, statutory (%) |",
          "|---|---:|---|---|---|---|---|"]
    for r in rows:
        linear, statutory, domestic = [
            tuple(map(Fraction, r[k])) for k in ("df_E11_interval", "df_statutory_interval", "d_only_interval")]
        difference = (100*(statutory[0]-linear[1]), 100*(statutory[1]-linear[0]))
        shares = [enclosure((100*domestic[0]/v[1], 100*domestic[1]/v[0]), 4) for v in (linear, statutory)]
        L.append("| %s | %.2f | %s | %s | %s | %s | %s |" % (
            r["design"], r["tau_f_cap"], enclosure(linear, 10), enclosure(statutory, 10),
            enclosure(difference, 6), *shares))
    (out / "table3.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    T = ["# Section 5.1 — formal adoption as the limit (reproduced)", "",
         "## Base caps (0.6; 0.6), combined menu, favorable witnesses", "",
         "| Design | (E11) | Statutory | Statutory status | Certified decrease, pp |", "|---|---|---|---|---|",
         "| G | %.4f | %.4f %s | Attainment open | %s |" % (
             eG["C2"], sG["C2"], enclosure(sG["intervalo_certificado"], 10), enclosure(dG, 6)),
         "| N | %.4f | %.4f %s | Attained at the caps | %s |" % (
             eN["C2"], sN["C2"], enclosure(sN["intervalo_certificado"], 10), enclosure(dN, 6)),
         "",
         "Gross design, statutory allocation: the value of the supremum is certified (error %.1e); whether some pair of rates "
         "attains it remains open." % sG["error_certificado"], "",
         "## Numerical diagnostics of adoption", "",
         "- Gross design, statutory allocation, tau_f = 0.6: formal establishments stop adopting at tau_d ≈ %.3f "
         "(last rate with adoption %r); revenue just below it is %.6f of the potential gain; L at the caps = %.4f." % (
             jump["ultimo_con_adopcion"]["tau_d"], jump["ultimo_con_adopcion"]["tau_d"], jump["ultimo_con_adopcion"]["R_sobre_Bpot"],
             R["jump_estatutaria_G"]["L_en_tope"]),
         "- Gross design, (E11), tau_f = 0.6: L at the caps = %.6f (formal establishments adopt there by a small margin)." % (
             R["jump_E11_G"]["L_en_tope"]),
         "- Domestic cap 0.35, gross design: adoption margin L at the caps and the domestic rate at which formal adoption "
         "would stop (with tau_f at its cap):", ""]
    for Rr in ("E11", "estatutaria"):
        for F, _ in TAGS:
            u = thr[(Rr, "G", F)]
            T.append("  - %s, cap tau_f %.2f: L = %+.4f; threshold tau_d ≈ %.3f (above the 0.35 cap: %s)" % (
                "statutory" if Rr == "estatutaria" else "(E11)", F, u["L_en_tope"], u["cruce"]["ultimo_con_adopcion"]["tau_d"],
                u["cruce"]["por_encima_del_tope"]))
    (out / "threshold.md").write_text("\n".join(T) + "\n", encoding="utf-8")

    summary = {"output": str(out), "seconds": round(time.time() - t0, 1), "checks": checks, "mismatches": mism,
               "table3": rows, "section_5_1": got51,
               "scope": "post-base sensitivities using each menu's favorable structural point (Table 3); under the statutory "
                        "allocation another admissible point could have a higher favorable ceiling, which was not examined; no "
                        "ceilings over the support or classifications were recomputed"}
    (out / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print()
    print((out / "table3.md").read_text(encoding="utf-8"))
    for name, passed in checks.items():
        if not passed:
            print("FAIL  " + name)
    print("Adoption threshold:", out / "threshold.md")
    print("Computed intervals and checks:", out / "summary.json")
    n = sum(checks.values())
    print("%d/%d checks passed in %.0f s. %s" % (n, len(checks), time.time() - t0,
                                                "SENSITIVITIES REPRODUCED" if n == len(checks) else "SOME CHECKS FAILED"))
    return 0 if n == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
