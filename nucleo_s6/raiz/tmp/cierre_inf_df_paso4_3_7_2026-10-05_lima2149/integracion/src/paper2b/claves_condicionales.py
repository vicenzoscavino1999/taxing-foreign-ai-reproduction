"""Validación de la clave condicional macro-ca2-v2 (enmienda candidata CA2-4, CLAVES_DE_CALCULO.json schemas.macro_ca2).

Forma: campos exactos y tipos del esquema. Semántica (no basta el nombre de campos ni el hash del payload):
- el bundle se resuelve por bundle_sha256 (bytes autenticados);
- la fila ca2_inputs(case_id, country_id, anchor_year) existe y reproduce d2/d6_vector_sha256 y context_sha256;
- ca2_cases reproduce scenario (E1/E2), preregistration_id, case_type y country_set; country_id ∈ country_set;
- vector D2: familia D2, país, año = anchor_year, representación d2_*; vector D6: familia D6, país, año 2023, d6_*;
- el archivo de contexto (hash = context_sha256) fija design_v, instrument_j, availability_case_id y
  availability_matrix_hash iguales a los de la celda, y case_id termina en <design_v>-<instrument_j>-<caso>;
- common_values_sha256 = H(common_values del omega); protocolo y huellas técnicas = los de la corrida.
La rama condicional no afirma precisión (ninguna evidencia de precisión se inventa).
"""
from __future__ import annotations

import hashlib
import json
import re

from .keys import H

FIELDS = ["kind", "bundle_sha256", "case_id", "scenario", "preregistration_id", "case_type", "country_set", "country_id",
          "anchor_year", "d2_vector_sha256", "d6_vector_sha256", "context_sha256", "common_values_sha256", "eta_w_block",
          "protocol_sha256", "technical"]
TECHNICAL = ("code_sha256", "configuration_sha256", "contract_sha256", "environment_sha256", "method_sha256", "tolerances_sha256")
SHA = re.compile("[0-9a-f]{64}")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def check_shape(p: dict, contracts) -> list:
    errs = []
    schema = contracts.K["schemas"].get("macro_ca2")
    if schema is None:
        return ["CONTRATO_SIN_ESQUEMA_MACRO_CA2 (el contrato cargado no cubre la rama condicional)"]
    if not isinstance(p, dict) or sorted(p) != sorted(schema["fields"]):
        return ["CAMPOS_MACRO_CA2_NO_EXACTOS"]
    idpat = re.compile(contracts.C["types"]["id"]["pattern"])
    countries = contracts.C["types"]["country"]["enum"]
    blocks = contracts.C["types"]["block"]["enum"]
    for k, t in schema["fields"].items():
        v = p[k]
        ok = True
        if t.startswith("literal:"):
            ok = v == t[8:]
        elif t == "sha":
            ok = isinstance(v, str) and SHA.fullmatch(v) is not None
        elif t in ("id", "atom"):
            ok = isinstance(v, str) and idpat.fullmatch(v) is not None
        elif t == "country":
            ok = v in countries
        elif t == "block":
            ok = v in blocks
        elif t == "scenario_conditional":
            ok = v in ("E1", "E2")
        elif t == "d2_year":
            ok = type(v) is int and 2015 <= v <= 2023
        elif t == "country_list":
            ok = isinstance(v, list) and v and v == sorted(set(v)) and all(c in countries for c in v)
        elif t == "technical":
            ok = isinstance(v, dict) and sorted(v) == sorted(TECHNICAL) and all(SHA.fullmatch(str(x)) for x in v.values())
        if not ok:
            errs.append(f"TIPO_MACRO_CA2:{k}")
    return errs


def check_semantics(p: dict, *, bundle: dict, bundle_bytes_sha: str, contexts: dict, cell: dict | None, common_sha: str,
                    protocol_sha: str, technical: dict, matrix_hash: str | None = None) -> list:
    """bundle: tablas del bundle; contexts: sha -> contenido del archivo de contexto (bytes autenticados)."""
    errs = []
    if p["bundle_sha256"] != bundle_bytes_sha:
        return ["BUNDLE_NO_CORRESPONDE"]
    cases = [c for c in bundle["ca2_cases"] if c["case_id"] == p["case_id"]]
    if len(cases) != 1:
        return ["CASO_AUSENTE_EN_BUNDLE"]
    case = cases[0]
    for k in ("scenario", "preregistration_id", "case_type", "country_set"):
        if case[k] != p[k]:
            errs.append("CASO_DISTINTO:" + k)
    if p["scenario"] not in ("E1", "E2"):
        errs.append("ESCENARIO_NO_CONDICIONAL")
    if p["country_id"] not in p["country_set"]:
        errs.append("PAIS_FUERA_DEL_CONJUNTO")
    rows = [r for r in bundle["ca2_inputs"] if r["case_id"] == p["case_id"] and r["country_id"] == p["country_id"]
            and r["anchor_year"] == p["anchor_year"]]
    if len(rows) != 1:
        return errs + ["ENTRADA_AUSENTE_O_AMBIGUA"]
    row = rows[0]
    vec = {v["vector_id"]: v for v in bundle["ca2_vectors"]}
    d2, d6 = vec.get(row["d2_vector_id"]), vec.get(row["d6_vector_id"])
    if d2 is None or d2["vector_sha256"] != p["d2_vector_sha256"]:
        errs.append("VECTOR_D2_DISTINTO")
    elif not (d2["family"] == "D2" and d2["country_id"] == p["country_id"] and d2["observation_year"] == p["anchor_year"]
              and str(d2["representation"]).startswith("d2_")):
        errs.append("VECTOR_D2_TIPO_ANIO_REPRESENTACION")
    if d6 is None or d6["vector_sha256"] != p["d6_vector_sha256"]:
        errs.append("VECTOR_D6_DISTINTO")
    elif not (d6["family"] == "D6" and d6["country_id"] == p["country_id"] and d6["observation_year"] == 2023
              and str(d6["representation"]).startswith("d6_")):
        errs.append("VECTOR_D6_TIPO_ANIO_REPRESENTACION")
    if row["context_sha256"] != p["context_sha256"]:
        errs.append("CONTEXTO_DISTINTO_DE_LA_ENTRADA")
    ctx = contexts.get(p["context_sha256"])
    if ctx is None:
        errs.append("CONTEXTO_NO_RESUELTO")
    elif cell is not None:
        label = f"{cell['design_v']}-{cell['instrument_j']}-{cell['availability_case_id']}"
        if not p["case_id"].endswith(":" + label):
            errs.append("CASO_DE_OTRO_CONTEXTO_DE_CELDA")
        for k in ("design_v", "instrument_j", "availability_case_id"):
            if ctx.get(k) != cell[k]:
                errs.append("CONTEXTO_CELDA_DISTINTO:" + k)
        if matrix_hash is not None and ctx.get("availability_matrix_hash") != matrix_hash:
            errs.append("CONTEXTO_MATRIZ_D4_DISTINTA")
    if p["common_values_sha256"] != common_sha:
        errs.append("OMEGA_COMUN_DISTINTO")
    if p["protocol_sha256"] != protocol_sha:
        errs.append("PROTOCOLO_DISTINTO")
    if p["technical"] != technical:
        errs.append("HUELLAS_TECNICAS_DISTINTAS")
    return errs


def build_payload(bundle: dict, bundle_sha: str, case_id: str, country: str, anchor_year: int, common_sha: str, block: str,
                  protocol_sha: str, technical: dict) -> dict:
    """Misma construcción que validadores/ca2_key.conditional_key, sobre tablas ya autenticadas."""
    case = next(c for c in bundle["ca2_cases"] if c["case_id"] == case_id)
    row = next(r for r in bundle["ca2_inputs"] if r["case_id"] == case_id and r["country_id"] == country
               and r["anchor_year"] == anchor_year)
    vec = {v["vector_id"]: v for v in bundle["ca2_vectors"]}
    return {"kind": "macro-ca2-v2", "bundle_sha256": bundle_sha, "case_id": case_id, "scenario": case["scenario"],
            "preregistration_id": case["preregistration_id"], "case_type": case["case_type"], "country_set": case["country_set"],
            "country_id": country, "anchor_year": row["anchor_year"], "d2_vector_sha256": vec[row["d2_vector_id"]]["vector_sha256"],
            "d6_vector_sha256": vec[row["d6_vector_id"]]["vector_sha256"], "context_sha256": row["context_sha256"],
            "common_values_sha256": common_sha, "eta_w_block": block, "protocol_sha256": protocol_sha, "technical": technical}


class BundleResolver:
    """Resuelve bundles por hash ({bundle_sha: ruta autenticada}) y sus contextos a partir de ca2_inputs
    (context_path relativo al proyecto o al directorio del bundle; el contenido debe tener el hash declarado)."""

    def __init__(self, root, bundles: dict):
        from pathlib import Path
        self.root = Path(root)
        self.bundles = dict(bundles)
        self._cache, self._ctx = {}, {}

    def bundle(self, bsha: str):
        if bsha not in self._cache:
            rel = self.bundles.get(bsha)
            if rel is None:
                return None
            raw = (self.root / rel).read_bytes()
            if sha(raw) != bsha:
                return None
            tables = json.loads(raw)
            self._cache[bsha] = tables
            base = (self.root / rel).parent
            for r in tables.get("ca2_inputs", []):
                cands = [self.root / r["context_path"], base / r["context_path"]]
                for q in cands:
                    if q.is_file():
                        craw = q.read_bytes()
                        if sha(craw) == r["context_sha256"]:
                            self._ctx[r["context_sha256"]] = json.loads(craw)
                            break
        return self._cache[bsha]

    def contexts(self) -> dict:
        return self._ctx
