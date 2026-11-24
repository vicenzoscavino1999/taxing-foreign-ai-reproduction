"""Preimágenes de claves de CLAVES_DE_CALCULO.json (key-contract-2) y extensión macro-ca2-v2.

Todas las claves = SHA256(JSON canónico compacto sin LF). Decimales como cadenas canónicas exactas; filas de valores
ordenadas por parameter_id; dependencias por role. La validación de forma la hace Contracts.key del núcleo S3.
Omega no contiene país ni snapshot; la clave estructural no contiene país; la macro sí.
"""
from __future__ import annotations

import hashlib
import json

from .numeric import canon_dec


def canon(value) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")


def H(value) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def value_rows(values: dict, ids: list, units: dict) -> list:
    rows = []
    for pid in sorted(ids):
        if pid not in values:
            raise KeyError("primitiva ausente en la proyección: " + pid)
        rows.append({"parameter_id": pid, "value": canon_dec(values[pid]), "value_unit": units[pid]})
    return rows


def common_values(values: dict, keys_contract: dict, units: dict) -> dict:
    return {"kind": "common-values-v2", "values": value_rows(values, keys_contract["common_primitive_ids"], units)}


def omega_identity(support_set_id: str, scenario_id: str, common_payload: dict) -> dict:
    return {"kind": "omega-identity-v2", "support_set_id": support_set_id, "scenario_id": scenario_id,
            "primitive_values_sha256": H(common_payload)}


def omega_id(identity: dict) -> str:
    return "OMG:" + H(identity)


def tau_domain(instrument: str, bar_d, bar_f) -> dict:
    d_on = instrument in ("d", "df")
    f_on = instrument in ("f", "df")
    return {"tau_d_lower": "0", "tau_d_upper": canon_dec(bar_d) if d_on else "0",
            "tau_f_lower": "0", "tau_f_upper": canon_dec(bar_f) if f_on else "0",
            "tau_d_lower_closed": True, "tau_d_upper_closed": True,
            "tau_f_lower_closed": True, "tau_f_upper_closed": True}


def structural(values: dict, keys_contract: dict, units: dict, design: str, instrument: str, bar_d, bar_f,
               theory_sha256: str, technical: dict) -> dict:
    return {"kind": "structural-v2", "values": value_rows(values, keys_contract["structural_primitive_ids"], units),
            "design_v": design, "instrument_j": instrument, "tau_domain": tau_domain(instrument, bar_d, bar_f),
            "theory_sha256": theory_sha256, "technical": technical}


def point(structural_key_sha256: str, tau_d, tau_f, side: str, branch_id: str) -> dict:
    return {"kind": "point-v2", "structural_key_sha256": structural_key_sha256, "tau_d": canon_dec(tau_d),
            "tau_f": canon_dec(tau_f), "side": side, "branch_id": branch_id}


def national_state(primitive_rows: list, shares: dict, joint_domain_sha256: str) -> dict:
    return {"kind": "national-state-v2", "primitive_values": primitive_rows,
            "shares": {k: canon_dec(v) for k, v in shares.items()}, "joint_domain_sha256": joint_domain_sha256}


def macro_strict(country: str, block: str, values: dict, keys_contract: dict, units: dict, national: dict,
                 dependencies: list, protocol_sha256: str, technical: dict) -> dict:
    return {"kind": "macro-v2", "country_id": country, "eta_w_block": block,
            "values": value_rows(values, keys_contract["macro_primitive_ids"], units), "national_state": national,
            "national_dependencies": sorted(dependencies, key=lambda d: d["role"]), "protocol_sha256": protocol_sha256,
            "technical": technical}


def macro_ca2_v2(bundle_sha256: str, case: dict, country: str, input_row: dict, vectors: dict, common_values_sha256: str,
                 block: str, protocol_sha256: str, technical: dict) -> dict:
    """Clave condicional E1/E2 (extensiones_s2.json macro_ca2_v2_fields), misma construcción que validadores/ca2_key."""
    return {"kind": "macro-ca2-v2", "bundle_sha256": bundle_sha256, "case_id": case["case_id"], "scenario": case["scenario"],
            "preregistration_id": case["preregistration_id"], "case_type": case["case_type"],
            "country_set": case["country_set"], "country_id": country, "anchor_year": input_row["anchor_year"],
            "d2_vector_sha256": vectors[input_row["d2_vector_id"]]["vector_sha256"],
            "d6_vector_sha256": vectors[input_row["d6_vector_id"]]["vector_sha256"],
            "context_sha256": input_row["context_sha256"], "common_values_sha256": common_values_sha256,
            "eta_w_block": block, "protocol_sha256": protocol_sha256, "technical": technical}


def external(macro_key_sha256: str, dependency: dict, cell, crosswalk_sha256: str, bound: str, gain_share,
             dme_gai, technical: dict) -> dict:
    return {"kind": "external-v2", "macro_key_sha256": macro_key_sha256, "external_dependency": dependency,
            "external_cell_id": cell.external_cell_id, "crosswalk_sha256": crosswalk_sha256,
            "policy_variant_id": cell.policy_variant_id, "regime_id": cell.regime_id,
            "requirement_basis": cell.requirement_basis, "xi": canon_dec(cell.xi), "layer": cell.layer,
            "bound_variant": bound, "gain_share": canon_dec(gain_share), "DME_gAI": canon_dec(dme_gai),
            "technical": technical}


def confrontation(run_id: str, omega: str, country: str, block: str, design: str, instrument: str, case: str,
                  matrix_hash: str, structural_sha: str, macro_sha: str, external_sha: str, technical: dict) -> dict:
    return {"kind": "confrontation-v2", "run_id": run_id, "omega_id": omega, "country_id": country, "eta_w_block": block,
            "design_v": design, "instrument_j": instrument, "availability_case_id": case,
            "availability_matrix_hash": matrix_hash, "structural_key_sha256": structural_sha,
            "macro_key_sha256": macro_sha, "external_key_sha256": external_sha, "technical": technical}
