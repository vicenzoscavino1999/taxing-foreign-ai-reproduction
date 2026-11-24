"""Productores de las cinco coordenadas de contexto que los bundles CA2 (1.5) dejaron como «pending_producer_D7_B».

Cada bundle fija, por hash, la DEFINICIÓN normativa de cinco coordenadas (estado estructural, bloque laboral, pi,
requerimiento externo, gain_share) con value=null. Este módulo:
- autentica esas definiciones (archivo del componente por hash, estado pendiente, valor nulo, documento normativo
  idéntico byte a byte al instalado bajo S3 y mismo manifiesto de contrato);
- produce el VALOR por celda B exclusivamente desde filas B ya validadas (omega_values, lambda_pi_envelope,
  cell_context), sin rellenar nulos con cero ni constantes, y liga cada valor al hash de su definición.
Omega común, clave estructural y clave macro nacional se mantienen separadas: aquí solo se leen, no se fusionan.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .keys import H

PENDING = {"structural_state": "contratos/CLAVES_DE_CALCULO.md", "labor_block": "contratos/CONTRATOS_D7_B_D8.md",
           "pi": "contratos/CONTRATOS_D7_B_D8.md", "external_requirement": "contratos/CONTRATOS_D7_B_D8.md",
           "gain_share": "contratos/CLAVES_DE_CALCULO.md"}
STRUCTURAL_13 = ("a", "beta_tilde", "c_legal", "eta_d", "eta_f", "gamma", "kappa_tilde", "phi", "rho", "t", "u_theta", "z_cost", "z_m")
PI = ("pi_iva", "pi_otros_productos", "pi_produccion")


class ContextError(ValueError):
    pass


def need(test, code):
    if not test:
        raise ContextError(code)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def definitions_from_bundles(root: Path, index_rel: str, index_sha256: str, *, installed_prefix: str, contract_sha256: str) -> dict:
    """Definiciones autenticadas desde el índice de bundles CA2 fijado (vía nacional)."""
    root = Path(root)
    raw = (root / index_rel).read_bytes()
    need(sha(raw) == index_sha256, "CONTEXT_BUNDLE_INDEX_HASH")
    comps = json.loads(raw)["components"]
    out = {}
    for field, c in comps.items():
        name = c["coordinate"]
        need(name in PENDING and field == name + "_sha256", "CONTEXT_COMPONENT_UNKNOWN:" + field)
        craw = (root / c["path"]).read_bytes()
        need(sha(craw) == c["sha256"], "CONTEXT_COMPONENT_HASH:" + name)
        rec = json.loads(craw)
        need(rec["status"] == "pending_producer_D7_B" and rec["value"] is None, "CONTEXT_COMPONENT_NOT_PENDING:" + name)
        d = rec["normative_definition"]
        need(d["document"] == installed_prefix + PENDING[name] and d["contract_manifest_sha256"] == contract_sha256,
             "CONTEXT_DEFINITION_DOCUMENT:" + name)
        need(sha((root / d["document"]).read_bytes()) == d["sha256"], "CONTEXT_DEFINITION_BYTES:" + name)
        out[name] = {"definition_sha256": c["sha256"], "document": d["document"], "document_sha256": d["sha256"]}
    need(set(out) == set(PENDING), "CONTEXT_COMPONENTS_EXACT")
    return out


def definitions_from_installed(root: Path, *, installed_prefix: str) -> dict:
    """Definiciones desde los documentos normativos instalados (mundos sintéticos, sin bundle CA2)."""
    out = {}
    for name, doc in PENDING.items():
        raw = (Path(root) / installed_prefix / doc).read_bytes()
        out[name] = {"definition_sha256": H({"coordinate": name, "document": installed_prefix + doc, "sha256": sha(raw)}),
                     "document": installed_prefix + doc, "document_sha256": sha(raw)}
    return out


def produce(cell: dict, omega_values: dict, macro: dict, definitions: dict) -> dict:
    """Valores de las cinco coordenadas para una celda B. omega_values: parameter_id -> valor decimal canónico (str)."""
    for pid in STRUCTURAL_13 + PI + ("gain_share", "eta_w", "eta_H"):
        need(omega_values.get(pid) is not None, "CONTEXT_VALUE_MISSING:" + pid)
    need(macro["omega_id"] == cell["omega_id"] and macro["macro_key_sha256"] == cell["expected_macro_key_sha256"], "CONTEXT_MACRO_JOIN")
    need(macro["eta_w_block"] == cell["eta_w_block"] and macro["eta_w"] == omega_values["eta_w"], "CONTEXT_LABOR_BLOCK")
    for k in ("external_cell_id", "layer", "bound_variant", "policy_variant_id", "xi"):
        need(cell.get(k) is not None, "CONTEXT_EXTERNAL_MISSING:" + k)
    values = {"structural_state": {p: omega_values[p] for p in STRUCTURAL_13},
              "labor_block": {"eta_w_block": cell["eta_w_block"], "eta_w": omega_values["eta_w"], "eta_H": omega_values["eta_H"]},
              "pi": {p: omega_values[p] for p in PI},
              "external_requirement": {k: cell[k] for k in ("external_cell_id", "layer", "bound_variant", "policy_variant_id", "xi")},
              "gain_share": omega_values["gain_share"]}
    out = {name: {"definition_sha256": definitions[name]["definition_sha256"], "value": values[name]} for name in PENDING}
    return {"cell_id": cell["cell_id"], "coordinates": out, "context_values_sha256": H(out)}


def produce_all(tables: dict, definitions: dict) -> tuple[list, list]:
    """Todas las celdas con confrontación completa. Devuelve (registros, errores) sin detenerse en el primero."""
    vals = {}
    for r in tables["omega_values"]:
        vals.setdefault(r["omega_id"], {})[r["parameter_id"]] = r["value"]
    macros = {m["macro_id"]: m for m in tables["lambda_pi_envelope"]}
    cells = {c["cell_id"]: c for c in tables["cell_context"]}
    records, errors = [], []
    for conf in tables["confrontation_result"]:
        if conf["computation_status"] != "complete":
            continue
        c = cells[conf["cell_id"]]
        try:
            records.append(produce(c, vals.get(c["omega_id"], {}), macros[conf["macro_id"]], definitions))
        except (ContextError, KeyError) as exc:
            errors.append(f"{conf['cell_id']}: {exc}")
    return records, errors
