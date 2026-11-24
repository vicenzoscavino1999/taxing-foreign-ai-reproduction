"""Execution-inventory fingerprint of this copy of the package, and which distributed version it is.

The fingerprint is the SHA-256 of the list «path<TAB>bytes<TAB>sha256» of every file that the computation can read,
computed with src/general.py:huella_ejecucion (the function the resume check of `general` also uses). It excludes
salidas/, local/, .venv*, __pycache__, extraccion/ (except one FAM02 file), insumos_externos/, the documentation
(root *.md, docs/, tools/, sensitivities/, CITATION.cff, run.ps1) and Git files.

The copy is recognized as
- "public": the archive as distributed, without the six national-accounts sheets that are not redistributed;
- "public_with_downloaded_sheets": the archive plus some of the six sheets (for example the five that
  `run.ps1 inputs` downloads), each with its expected SHA-256;
- "complete": the archive plus the six sheets, as the full analysis requires.

Usage: python -B -I tools/fingerprint.py [--expect any|complete]
Exit code 0 if the copy is one of these versions (and "complete", if that is expected), 1 otherwise.
"""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = "nucleo_s6/raiz/fase2_datos/recepcion_nacional/versions/866aa139fb50578cae1ec5d77e1f98e6a5b87b56780aa1d95a118dffc5644984/snapshots"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--expect", choices=("any", "complete"), default="any")
    a = ap.parse_args()
    G = load("general_of_this_copy", ROOT / "src" / "general.py")
    rows = {}
    original = G.sha_archivo

    def record(p):
        s = original(p)
        r = Path(p).resolve().relative_to(ROOT).as_posix()
        rows[r] = "%s\t%d\t%s" % (r, Path(p).stat().st_size, s)
        return s

    G.sha_archivo = record
    h = G.huella_ejecucion(ROOT)
    v = json.loads((ROOT / "tools" / "version.json").read_text(encoding="utf-8"))
    inv = v["execution_inventory"]

    # the six sheets and their expected hashes, as insumos_externos/obtener_insumos.py declares them
    ob = load("inputs_of_this_copy", ROOT / "insumos_externos" / "obtener_insumos.py")
    expected = {n: e for n, _, _, e in ob.DESCARGAS}
    expected[ob.BUNDLE[0]] = ob.BUNDLE[2]
    expected[ob.PER[0]] = ob.PER[2]
    six = {"%s/%s" % (SNAP, n): (n, e) for n, e in expected.items()}
    sheets, bad = {}, False
    for r, (n, e) in sorted(six.items()):
        if r not in rows:
            sheets[n] = "absent"
        elif rows[r].rsplit("\t", 1)[1] == e:
            sheets[n] = "present, expected SHA-256"
        else:
            sheets[n] = "present, DIFFERENT SHA-256"
            bad = True
    # fingerprint of the copy without the six sheets, built as huella_ejecucion builds it
    rest = [rows[r] for r in sorted(rows, key=lambda s: s.encode("utf-16-be")) if r not in six]
    without = hashlib.sha256(("\n".join(rest) + "\n").encode("utf-8")).hexdigest()

    if h["sha256"] == inv["complete"]["sha256"]:
        which, meaning = "complete", inv["complete"]["meaning"]
    elif h["sha256"] == inv["public"]["sha256"]:
        which, meaning = "public", inv["public"]["meaning"]
    elif without == inv["public"]["sha256"] and not bad:
        k = sum(s != "absent" for s in sheets.values())
        which = "public_with_downloaded_sheets"
        meaning = ("the distributed archive plus %d of the six sheets, each with its expected hash; table4 needs the five "
                   "downloadable ones, verify and full need all six" % k)
    else:
        which, meaning = None, "unknown: this copy differs from the distributed version"
    ok = which is not None and (a.expect == "any" or which == "complete")
    print(json.dumps({"package_version": v["version"], "fingerprint": h, "recognized_as": which, "meaning": meaning,
                      "six_sheets": sheets, "expected": a.expect, "ok": ok}, indent=1, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
