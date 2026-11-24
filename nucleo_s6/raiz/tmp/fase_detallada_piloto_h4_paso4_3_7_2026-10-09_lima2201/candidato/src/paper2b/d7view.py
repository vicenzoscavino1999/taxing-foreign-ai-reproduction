"""Vista tipada de un producto D7 (leído y validado con el catálogo; nunca 'el último activo')."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

TABLES = ("authority", "source_evidence", "parameter_registry", "formula_registry", "formula_inputs", "support_sets",
          "support_set", "parameter_bindings", "joint_constraints", "constraint_inputs", "scenario_map",
          "tax_component_supports", "tax_rate_inputs", "d7_admissibility_report", "d7_gate_report", "tau_domains",
          "shared_primitive_members")


class D7ViewError(ValueError):
    pass


@dataclass
class D7View:
    path: Path
    tables: dict
    phase: dict
    manifest: dict
    sets: dict = field(default_factory=dict)
    supports: dict = field(default_factory=dict)
    bindings: dict = field(default_factory=dict)
    tau_domains: dict = field(default_factory=dict)
    scenarios: dict = field(default_factory=dict)
    tax: dict = field(default_factory=dict)
    evidence: dict = field(default_factory=dict)
    rates: dict = field(default_factory=dict)

    @classmethod
    def load(cls, contracts, version_dir: Path, *, manifest_name: str = "d7_manifest.json") -> "D7View":
        version_dir = Path(version_dir)
        manifest = json.loads((version_dir / manifest_name).read_bytes())
        tables = {}
        for name in TABLES:
            rel = contracts.C["tables"][name]["file"].split("/", 1)[1]
            tables[name] = contracts.read_csv(version_dir / rel, name)
        contracts.references(tables)
        phase = json.loads((version_dir / "d7_phase_report.json").read_bytes())
        v = cls(version_dir, tables, phase, manifest)
        v.sets = {r["support_set_id"]: r for r in tables["support_sets"]}
        for r in tables["support_set"]:
            v.supports.setdefault((r["support_set_id"], r["parameter_id"]), {})[r["variant_id"]] = r
        for r in tables["parameter_bindings"]:
            v.bindings[(r["support_set_id"], r["parameter_id"], r["scope_id"])] = r
        for r in tables["tau_domains"]:
            v.tau_domains[(r["support_set_id"], r["instrument_j"])] = r
        v.scenarios = {r["scenario_id"]: r for r in tables["scenario_map"]}
        for r in tables["tax_component_supports"]:
            v.tax.setdefault((r["support_set_id"], r["country_id"]), {})[r["component_id"]] = r
        v.evidence = {r["evidence_id"]: r for r in tables["source_evidence"]}
        v.rates = {r["country_id"]: r for r in tables["tax_rate_inputs"]}
        return v

    def support(self, set_id: str, pid: str, variant: str | None = None) -> dict:
        variants = self.supports[(set_id, pid)]
        if variant is None:
            if len(variants) != 1:
                binding = self.bindings[(set_id, pid, "global")]
                return next(v for v in variants.values() if v["support_id"] == binding["support_id"])
            return next(iter(variants.values()))
        return variants[variant]

    def nodes(self, set_id: str, pid: str) -> list:
        s = self.support(set_id, pid)
        return [Decimal(repr(x)) if isinstance(x, float) else Decimal(str(x)) for x in s["level0_nodes"]]

    def interval(self, set_id: str, pid: str) -> tuple:
        s = self.support(set_id, pid)
        return Decimal(s["lower"]), Decimal(s["upper"])

    def countries(self, set_id: str) -> list:
        return sorted({c for (s, c) in self.tax if s == set_id})

    def layer_scenario(self, set_id: str) -> str:
        return f"SCN:{set_id}"

    def national_bindings(self, set_id: str, country: str) -> dict:
        out = {}
        for pid in ("s_L_bar", "s_bar_iva", "s_bar_otros_productos", "s_bar_produccion"):
            out[pid] = self.bindings[(set_id, pid, f"country:{country}")]
        return out
