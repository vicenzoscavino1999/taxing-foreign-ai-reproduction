"""G-NA-1 candidata: no aplicabilidad autenticada, distinta de convergencia."""
import csv
import io
import json
from pathlib import Path
from . import keys as K

VERSION = "G-NA-1"
METHOD = "instrument_unavailable_authenticated"


def enabled(contracts):
    return contracts.C.get("g_applicability_version") == VERSION


def authority(d7):
    """Relee D7 y mapa fijado; no confía en etiquetas de las filas B."""
    from herramientas.bloque2 import familias as FAM
    from herramientas.s3.validadores.core import sha
    p = Path(d7.path)
    raw = (p / "d7_manifest.json").read_bytes()
    if json.loads(raw) != d7.manifest:
        raise ValueError("G_NA_D7_MANIFEST_CHANGED")
    FAM.verify_version(p, "D7", expected_tree=d7.manifest["tree_sha256"])
    deps = [x for x in d7.manifest["input_dependencies"] if x["role"] == "d4_model_case_map"]
    if len(deps) != 1:
        raise ValueError("G_NA_D4_MAP_NOT_UNIQUE")
    dep = deps[0]
    rel = Path(dep["path"])
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError("G_NA_D4_PATH")
    candidates = [a / rel for a in p.parents if (a / rel).is_file()]
    if not candidates:
        raise ValueError("G_NA_D4_MAP_ABSENT")
    data = candidates[0].read_bytes()
    if sha(data) != dep["sha256"]:
        raise ValueError("G_NA_D4_MAP_HASH")
    rows = json.loads(data) if rel.suffix == ".json" else list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
    # Relación D7 en memoria con los bytes recién autenticados, incluidos sus anclajes D4.
    source = list(csv.DictReader(io.StringIO((p / "source_evidence.csv").read_text(encoding="utf-8-sig"))))
    pins = [x["payload_sha256"] for x in source if x["evidence_id"] == "EV.D4.MATRIX"]
    if len(pins) != 1 or d7.evidence.get("EV.D4.MATRIX", {}).get("payload_sha256") != pins[0]:
        raise ValueError("G_NA_MATRIX_AUTHORITY")
    matrix_row = next(x for x in source if x["evidence_id"] == "EV.D4.MATRIX")
    root = next(a for a in p.parents if a / rel == candidates[0])
    matrix_rel = Path(matrix_row["source_path"])
    if matrix_rel.is_absolute() or ".." in matrix_rel.parts:
        raise ValueError("G_NA_MATRIX_PATH")
    matrix_raw = (root / matrix_rel).read_bytes()
    if sha(matrix_raw) != pins[0]:
        raise ValueError("G_NA_MATRIX_SOURCE_HASH")
    if matrix_row["source_id"] == "SYN":
        payload = json.loads(matrix_raw)
        if payload != {"kind": "SYNTHETIC_D4_NOT_NATIONAL", "model_case_map": rows}:
            raise ValueError("G_NA_MATRIX_MAP_CONTEXT")
    return rows, pins[0]


def errors(row, tables, auth):
    """Lista de rechazos: vacía solo para una NA completa en sus relaciones."""
    out = []
    def need(ok, msg):
        if not ok: out.append("G_NA_" + msg)
    def one(table, **pk):
        found = [r for r in tables.get(table, []) if all(r.get(k) == v for k, v in pk.items())]
        need(len(found) == 1, "UNIQUE_" + table)
        return found[0] if len(found) == 1 else {}
    cid = row.get("quantity_id", "")[2:]
    need(row.get("quantity_id", "").startswith("G:"), "ONLY_G")
    cx = one("cell_context", cell_id=cid)
    cf = one("confrontation_result", cell_id=cid)
    ce = one("capture_ceiling_result", ceiling_id=cf.get("ceiling_id"))
    fr = one("frontier_context", frontier_id=ce.get("frontier_id"))
    one("convergence_result", quantity_id="G:" + cid)
    ev = one("numerical_evidence", evidence_ref=row.get("evidence_ref"))
    need(row.get("result_ref") == "confrontation_result:" + K.canon({"cell_id": cid}).decode(), "RESULT_REF")
    need(row.get("status") == "not_applicable" and row.get("method_id") == METHOD, "STATUS_METHOD")
    need(row.get("level_before") == 0 and row.get("level_after") == 1, "LEVELS")
    need(row.get("coverage_complete") is False and row.get("verdict_changes") == 0, "NO_NUMERIC_PASS")
    need(all(row.get(k) is None for k in ("value_before", "value_after", "change_bound", "topology_before", "topology_after")), "NUMERIC_CONTENT")
    need(ev.get("kind") == "convergence" and ev.get("status") == "limitation" and ev.get("method_id") == METHOD
         and ev.get("result_table") == "confrontation_result" and ev.get("record_pk") == {"cell_id": cid}
         and ev.get("error_bound") is None, "EVIDENCE")
    need(cx.get("instrument_available") is False and ce.get("instrument_available") is False, "AVAILABLE")
    for obj in (cf, ce):
        need(obj.get("computation_status") == "not_applicable" and obj.get("reason_code") == "INSTRUMENT_NOT_AVAILABLE", "REASON")
    need(cf.get("verdict") == "no_verdict" and all(cf.get(k) is None for k in ("C_2", "K_comp_1", "G")), "CONFRONTATION_NUMERIC")
    need(all(ce.get(k) is None for k in ("C_2", "numerical_error", "tau_d_at_sup", "tau_f_at_sup", "sup_lateral_low", "sup_lateral_high", "sup_not_attained")), "CEILING_NUMERIC")
    for k in ("country_id", "omega_id", "run_id", "design_v", "instrument_j", "availability_case_id", "availability_matrix_hash"):
        need(k in cx and cx.get(k) == fr.get(k), "CONTEXT_" + k)
    if auth is None:
        need(False, "AUTHORITY_ABSENT")
    else:
        rows, matrix = auth
        selected = [r for r in rows if (r.get("country_id"), r.get("model_menu"), r.get("case_id")) ==
                    (cx.get("country_id"), "j_" + cx.get("instrument_j", ""), cx.get("availability_case_id"))]
        need(len(selected) == 1, "D4_ROW")
        need(cx.get("availability_matrix_hash") == matrix, "MATRIX_PIN")
        if len(selected) == 1:
            d4 = selected[0]
            need(d4.get("case_id") == "conditional_none" and d4.get("availability_assumed") == "true"
                 and d4.get("quantitative_use") == "conditional_scenario_no_foreign_leg", "D4_UNAVAILABLE")
            for obj in (cx, ce):
                need(obj.get("availability_assumed") is True and obj.get("availability_status") == d4.get("national_availability_status")
                     and obj.get("availability_source") == d4.get("quantitative_use"), "D4_METADATA")
    return out
