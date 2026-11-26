"""Table 3, favorable column, recomputed from scratch: summary of the six FAM01 trials run by `run.ps1 table4`.

Each trial (`reproducir.py general --modo ensayo-fam01 --unidad C2:<design>:<menu>:sup`) recomputes one favorable
witness of Table 3 with the full chain (structural point, frontier, certified ceiling C_2, validation) and compares it
with its accepted original. This script reads the six results and their comparisons.

Usage: python -B -I tools/table4.py <folder with the six trial folders>
Writes <folder>/table4.md; exit code 0 if the six reproductions are accepted and the values equal the printed article.
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
BASE = Path(sys.argv[1]).resolve()
ACCEPTED = ("aceptada", "aceptada_comparacion_limpia", "aceptada_comparacion_limpia_con_F2")
ARTICLE = {("df", "G"): "0.7917", ("df", "N"): "0.5628", ("d", "G"): "0.5475", ("d", "N"): "0.4380",
           ("f", "G"): "0.2737", ("f", "N"): "0.2737"}
MENUS = {"df": "Both instruments (df)", "d": "Domestic tax only (d)", "f": "Withholding only (f)"}


def main():
    L = ["# Table 3 — favorable witnesses recomputed from scratch (six FAM01 units)", "",
         "| Instrument menu | Design | Unit | C_2 recomputed | Certified error | Original C_2 | Reproduction | = article |",
         "|---|---|---|---|---|---|---|---|"]
    all_ok = True
    for (j, D), art in ARTICLE.items():
        u = "C2:%s:%s:sup" % (D, j)
        n = u.replace(":", "_")
        trial = BASE / ("%s_%s" % (D, j)) / "fam01" / "R2"
        try:
            new = json.loads((trial / "ensayo" / "comparables" / (n + ".json")).read_text(encoding="utf-8"))["resultado"]["techo"]
            comp = json.loads((trial / ("ensayo.%s.comparacion.json" % n)).read_text(encoding="utf-8"))
            state = comp["estado"]["reproduccion"]
        except (OSError, KeyError, ValueError) as e:
            L.append("| %s | %s | %s | missing (%s) | | | | NO |" % (MENUS[j], D, u, type(e).__name__))
            all_ok = False
            continue
        orig = json.loads((ROOT / "referencias" / "fam01" / "originales" / (n + ".json")).read_text(encoding="utf-8"))["resultado"]["techo"]
        ok = state in ACCEPTED and "%.4f" % new["C_2"] == art and new["computation_status"] == "complete"
        all_ok &= ok
        L.append("| %s | %s | `%s` | %.10f | %.1e | %.10f | %s | %s |" % (MENUS[j], D, u, new["C_2"], new["numerical_error"], orig["C_2"],
                                                                     state, "yes" if ok else "NO"))
    (BASE / "table4.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    print()
    print("TABLE 3 (FAVORABLE COLUMN) REPRODUCED" if all_ok else "SOME CHECKS FAILED")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
