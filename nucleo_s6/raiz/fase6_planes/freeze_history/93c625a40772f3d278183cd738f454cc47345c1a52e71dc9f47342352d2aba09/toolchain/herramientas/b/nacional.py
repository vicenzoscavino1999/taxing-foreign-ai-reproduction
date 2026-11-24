"""Proveedores nacionales de Paquete B desde dependencias autenticadas (D7 fijado -> D2, D6 v2, bundles CA2).

- Vía ESTRICTA (E0/E3): dominio conjunto de primitivas D2 (`dominios_candidatos.json`, vista <país>_2023), términos de
  los cuatro shares y denominador; cuatro dependencias exactas (d2_snapshot, d6_snapshot, precision, joint_domain)
  resueltas en los manifiestos D2/D6 fijados por el manifiesto D7. B elige después los vértices extremos de lambda.
- Vía CONDICIONAL (E1/E2): un estado por año ancla del caso (s_L_bar del D2 del año, shares D6 2023 de la edición),
  primitivas del vector publicado del bundle; clave macro-ca2-v2 construida con `validadores/ca2_key.conditional_key`
  (CA2Validator con adaptadores reales) en la primera llamada de cada (caso, país) y recompuesta de forma idéntica.
Nada de este módulo calcula lambda, C2 ni G. Toda ruta y hash sale del manifiesto D7 seleccionado; nada se descubre.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from fractions import Fraction
from pathlib import Path

from paper2b import keys as K
from paper2b import macro as MC
from paper2b.d7build import base_set_id, editions


class NationalError(RuntimeError):
    pass


def need(test, code):
    if not test:
        raise NationalError(code)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def exact_fraction(text: str) -> Fraction:
    """Fracción exacta de D6 v2 (`{"numerator": "...", "denominator": "..."}` con enteros en cadena)."""
    obj = json.loads(text)
    need(isinstance(obj, dict) and set(obj) == {"numerator", "denominator"}, "D6_EXACT_SHARE_FORMAT")
    return Fraction(int(obj["numerator"]), int(obj["denominator"]))


TERMS = {"s_L_bar": "COE", "s_bar_iva": "VAT", "s_bar_otros_productos": "OTHER_PRODUCTS", "s_bar_produccion": "PRODUCTION"}
COMPONENT_SHARE = {"iva": "s_bar_iva", "otros_productos": "s_bar_otros_productos", "produccion": "s_bar_produccion"}


class Providers:
    def __init__(self, root: Path, contracts, d7view, *, protocol_sha256: str, technical: dict):
        self.root, self.C, self.d7 = Path(root), contracts, d7view
        self.protocol, self.technical = protocol_sha256, technical
        deps = {d["role"]: d for d in d7view.manifest["input_dependencies"]}
        self.d2m = self._manifest(deps["d2_version"])
        self.d6m = self._manifest(deps["d6_v2_version"])
        self.idx_dep = deps["ca2_bundles_index"]
        self.ev = d7view.evidence
        reg = self.ev["EV.REGISTRY"]
        raw = self._artifact(reg["source_path"], reg["payload_sha256"])
        self.registry = json.loads(raw)
        self.set_case = {}
        for entry in self.registry["entries"]:
            for ed in editions(entry):
                for block in ("macro", "micro"):
                    self.set_case[base_set_id(entry, ed, block)] = (entry, ed or "pub", block)
        self._key_cache = {}

    # ------------------------------------------------------------------------------------------ autenticación
    def _artifact(self, rel: str, digest: str) -> bytes:
        raw = (self.root / rel).read_bytes()
        need(sha(raw) == digest, "NATIONAL_ARTIFACT_HASH:" + rel)
        return raw

    def _manifest(self, dep: dict) -> dict:
        raw = self._artifact(dep["path"], dep["sha256"])
        m = json.loads(raw)
        files = {e.get("path", e.get("relative_path")): e["sha256"] for e in m["files"]}
        return {"path": dep["path"], "sha256": dep["sha256"], "dir": str(Path(dep["path"]).parent.as_posix()), "files": files}

    def _dependency(self, role: str, man: dict, artifact_rel: str, pk: dict) -> dict:
        raw = (self.root / artifact_rel).read_bytes()
        name = Path(artifact_rel).relative_to(man["dir"]).as_posix()
        need(man["files"].get(name) == sha(raw), f"NATIONAL_ARTIFACT_NOT_IN_MANIFEST:{role}:{name}")
        return {"role": role, "manifest_path": man["path"], "manifest_sha256": man["sha256"], "artifact_path": artifact_rel,
                "artifact_sha256": sha(raw), "record_pk": pk}

    def base_of(self, set_id: str) -> str:
        base = set_id
        while base not in self.set_case and "." in base:
            base = base.rsplit(".", 1)[0]
        need(base in self.set_case, "NATIONAL_SET_UNKNOWN:" + set_id)
        return base

    # ------------------------------------------------------------------------------------------ proveedor
    def national(self, set_id: str, country: str) -> list:
        entry, ed, block = self.set_case[self.base_of(set_id)]
        need(country in entry["country_set"], "NATIONAL_COUNTRY_OUTSIDE_CASE")
        strict = sorted(entry["scenarios"]) == ["E0", "E3"]
        return [self.strict_state(entry, ed, country)] if strict else self.conditional_states(entry, ed, country)

    def strict_state(self, entry: dict, ed: str, c: str) -> dict:
        preg = entry["preregistration_id"]
        j = self.ev[f"EV.JOINT.{c}.2023"]
        raw = self._artifact(j["source_path"], j["payload_sha256"])
        view = json.loads(raw)["views"][f"{c}_2023"]
        need(view["D2"]["precision"] == "pass" and view["D6"]["precision"] == "pass", "STRICT_PRECISION_NOT_PASS:" + c)
        domains = {p: (Fraction(lo), Fraction(hi)) for p, (lo, hi) in view["primitive_domains"].items()}
        terms = {k: [(p, Fraction(coef)) for p, coef in view["derived"][d]["terms"]] for k, d in TERMS.items()}
        den = view["derived"]["PIB"]["terms"]
        need(len(den) == 1 and Fraction(den[0][1]) == 1, "STRICT_DENOMINATOR_NOT_SINGLE_PRIMITIVE")
        d2e, pre = self.ev[f"EV.D2.{c}.2023"], self.ev[f"EV.PREC.{c}.2023"]
        d6e = self.ev[next(k for k in sorted(self.ev) if k.startswith(f"EV.D6.{preg}.{c}."))]
        deps = [self._dependency("d2_snapshot", self.d2m, d2e["source_path"], {"country_id": c, "observation_year": 2023}),
                self._dependency("d6_snapshot", self.d6m, d6e["source_path"], {"preregistration_id": preg, "country_id": c}),
                self._dependency("joint_domain", self.d2m, j["source_path"], {"view": f"{c}_2023"}),
                self._dependency("precision", self.d2m, pre["source_path"], {"country_id": c})]
        return {"kind": "strict_domain", "domains": domains, "terms": terms, "denominator": den[0][0], "preregistration_id": preg,
                "edition": ed, "anchor_year": 2023, "unit": "national_currency_million", "joint_domain_sha256": sha(raw),
                "dependencies": sorted(deps, key=lambda d: d["role"])}

    def resolver(self):
        """Resolutor de bundles CA2 por hash (índice autenticado vía D7) para la validación semántica del consumidor."""
        from paper2b import claves_condicionales as CK
        idx_raw = self._artifact(self.idx_dep["path"], self.idx_dep["sha256"])
        return CK.BundleResolver(self.root, {b["sha256"]: b["path"] for b in json.loads(idx_raw)["bundles"]})

    def _bundle(self, preg: str):
        idx_raw = self._artifact(self.idx_dep["path"], self.idx_dep["sha256"])
        b = next(x for x in json.loads(idx_raw)["bundles"] if x["preregistration_id"] == preg)
        ev = self.ev[f"EV.BUNDLE.{preg}"]
        need(ev["source_path"] == b["path"] and ev["payload_sha256"] == b["sha256"], "BUNDLE_D7_VS_INDEX:" + preg)
        raw = self._artifact(b["path"], b["sha256"])
        return b, raw, json.loads(raw)

    def conditional_states(self, entry: dict, ed: str, c: str) -> list:
        preg = entry["preregistration_id"]
        b, raw, tab = self._bundle(preg)
        vec = {v["vector_id"]: v for v in tab["ca2_vectors"]}
        members = {}
        for m in tab["ca2_members"]:
            members.setdefault(m["vector_id"], {})[m["concept"]] = Fraction(m["value_literal"])
        d6_ed = entry["vectors"][c]["D6"]["source_id"] if ed == "pub" else next(r for r in entry["revisions"][c] if r["label"] == ed)["D6"]["source_id"]
        comps = {}
        for k, v in sorted(self.ev.items()):
            pre = f"EV.D6.{preg}.{c}.{d6_ed}."
            if k.startswith(pre):
                comps[k[len(pre):]] = v
        need(sorted(comps) == sorted(COMPONENT_SHARE), f"CONDITIONAL_D6_COMPONENTS:{preg}:{c}:{d6_ed}")
        tax = {r["component_id"]: r for r in csv.DictReader(io.StringIO(self._artifact(
            comps["iva"]["source_path"], comps["iva"]["payload_sha256"]).decode("utf-8")))
            if r["preregistration_id"] == preg and r["country_id"] == c and r["edition"] == d6_ed}
        need(sorted(tax) == sorted(COMPONENT_SHARE), "CONDITIONAL_D6_ROWS")
        shares6 = {COMPONENT_SHARE[k]: exact_fraction(r["share_exact_json"]) for k, r in tax.items()}
        out, seen = [], set()
        for row in sorted((r for r in tab["ca2_inputs"] if r["country_id"] == c), key=lambda r: (r["anchor_year"], r["case_id"])):
            case = next(x for x in tab["ca2_cases"] if x["case_id"] == row["case_id"])
            if vec[row["d6_vector_id"]]["source_id"] != d6_ed:
                continue
            ident = (row["anchor_year"], row["d2_vector_id"], row["d6_vector_id"])
            if ident in seen:            # un estado por año ancla; los contextos de celda entran por la clave
                continue
            seen.add(ident)
            d2 = members[row["d2_vector_id"]]
            sL = d2["COE"] / d2["PIB"]
            prim = tuple(sorted([(f"{row['d2_vector_id']}:{k}", v, vec[row["d2_vector_id"]]["unit"]) for k, v in d2.items()] +
                                [(f"{row['d6_vector_id']}:{k}", v, vec[row["d6_vector_id"]]["unit"])
                                 for k, v in members[row["d6_vector_id"]].items()]))
            shares = dict(shares6, s_L_bar=sL)
            st = MC.NationalState(c, preg, "conditional", ed, int(row["anchor_year"]), "published_vector", prim,
                                  tuple((k, shares[k]) for k in MC.SHARE_KEYS), b["sha256"], ())
            self._key_cache.setdefault(("row", preg, c, int(row["anchor_year"]), ed), (case, row))
            out.append(st)
        need(out, f"CONDITIONAL_NO_STATES:{preg}:{c}:{ed}")
        return out

    def conditional_key(self, state, om: dict, block: str, context):
        """macro-ca2-v2 del contexto de celda (diseño, menú, caso D4): la primera vez por (caso, país) se construye con
        ca2_key.conditional_key (validación completa del bundle con adaptadores reales) y se exige igualdad."""
        preg, c = state.preregistration_id, state.country_id
        need(context is not None, "CONDITIONAL_KEY_REQUIRES_CELL_CONTEXT")
        b, raw, tab = self._bundle(preg)
        label = "{}-{}-{}".format(*context)
        _, row0 = self._key_cache[("row", preg, c, state.anchor_year, state.edition)]
        rows = [r for r in tab["ca2_inputs"] if r["country_id"] == c and r["anchor_year"] == state.anchor_year
                and r["d6_vector_id"] == row0["d6_vector_id"] and r["case_id"].endswith(":" + label)]
        need(len(rows) == 1, f"CONDITIONAL_CONTEXT_ROW:{preg}:{c}:{state.anchor_year}:{label}")
        row = rows[0]
        case = next(x for x in tab["ca2_cases"] if x["case_id"] == row["case_id"])
        vectors = {v["vector_id"]: v for v in tab["ca2_vectors"]}
        payload = K.macro_ca2_v2(b["sha256"], case, c, row, vectors, om["common_sha"], block, self.protocol, self.technical)
        key = ("validated", row["case_id"], c)
        if key not in self._key_cache:
            self._key_cache[key] = self.validate_key(raw, b, row["case_id"], c, om["common_sha"], block) == payload
            need(self._key_cache[key], "CONDITIONAL_KEY_DIFFERS_FROM_CA2_KEY")
        return payload, K.H(payload)

    def validate_key(self, raw: bytes, b: dict, case_id: str, c: str, common_sha: str, block: str) -> dict:
        from herramientas.ca2_bundles.construir_bundles import build_bundle
        from herramientas.nacionales.adaptadores_ca2 import contracts as national_contracts
        from herramientas.s3.validadores.ca2 import CA2Validator
        from herramientas.s3.validadores.ca2_key import conditional_key
        idx = json.loads(self._artifact(self.idx_dep["path"], self.idx_dep["sha256"]))
        entry = next(e for e in self.registry["entries"] if e["preregistration_id"] == b["preregistration_id"])
        nc = national_contracts()
        ctx = {k: [dict(x, context=None) for x in idx["contexts"][k]] for k in entry["country_set"]}
        _, adapters = build_bundle(entry, nc, ctx, f"fase2_datos/recepcion_nacional/versions/{idx['reception_tree_sha256']}/")
        res = conditional_key(raw, b["sha256"], CA2Validator(nc, self.root, adapters), case_id, c, common_values_sha256=common_sha,
                              eta_w_block=block, protocol_sha256=self.protocol, technical=self.technical)
        return res["payload"]
