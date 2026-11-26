"""Requerimiento externo (diseño (23)-(25), (27); MANIFIESTO_ENVOLVENTE D1-D2; §8.2 capas).

Grilla autenticada fase5_cuantificacion/extraccion_grilla/grilla_efectiva.csv (1200 celdas, 15 columnas).
Dos cotas del crosswalk (§16.2), nunca fundidas:
  sin_addback      Q = (1+xi) c_gross + F_fix_perp + 1{DC} s_PB   (solo administrativo y transición; F_leak fuera)
  addback_completo Q = (1+xi) c_gross + F_fix      + 1{DC} s_PB   (replica el requerimiento bruto del compañero)
Capas (§8.2): núcleo contable (baseline, xi=0), guardrail de deuda (debt_consistent, xi=0), buffer destacado (xi=0.10),
sensibilidades (xi in {0.05,0.25,0.50}). K1 = (Q + DME_gAI)/(lambda gain_share) (24); G = C2 - K1 (27).
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from fractions import Fraction

COLUMNS = ["country_id", "policy_id", "policy_variant_id", "gmi_version", "regime_id", "requirement_basis", "xi",
           "cost_gross_gdp", "F_admin", "F_trans", "F_leak", "F_fix", "F_fix_perp", "s_PB", "Q"]
BOUNDS = ("addback_completo", "sin_addback")
T1 = 1e-12


class GridError(ValueError):
    pass


@dataclass(frozen=True)
class GridCell:
    country_id: str
    policy_variant_id: str
    regime_id: str
    requirement_basis: str
    xi: str
    cost_gross: float
    F_admin: float
    F_trans: float
    F_leak: float
    F_fix: float
    F_fix_perp: float
    s_PB: float
    Q_grid: float

    @property
    def external_cell_id(self) -> str:
        return f"EXT:{self.country_id}:{self.policy_variant_id}:{self.regime_id}:{self.requirement_basis}:{self.xi}"

    @property
    def layer(self) -> str:
        return layer(self.requirement_basis, self.xi)

    def record_pk(self) -> dict:
        return {"country_id": self.country_id, "policy_variant_id": self.policy_variant_id, "regime_id": self.regime_id,
                "requirement_basis": self.requirement_basis, "xi": self.xi}

    def Q(self, bound: str) -> float:
        dc = self.s_PB if self.requirement_basis == "debt_consistent" else 0.0
        xi = float(self.xi)
        if bound == "sin_addback":
            return (1.0 + xi) * self.cost_gross + self.F_fix_perp + dc
        if bound == "addback_completo":
            return (1.0 + xi) * self.cost_gross + self.F_fix + dc
        raise GridError("cota desconocida")


def layer(basis: str, xi: str) -> str:
    x = Fraction(xi)
    if x == 0:
        if basis == "baseline":
            return "nucleo_contable"
        if basis == "debt_consistent":
            return "guardrail_deuda"
        raise GridError("base desconocida")
    if x == Fraction(1, 10):
        return "buffer_destacado"
    if x in (Fraction(1, 20), Fraction(1, 4), Fraction(1, 2)):
        return "sensibilidad"
    raise GridError("xi fuera de la grilla declarada")


def read_grid(raw: bytes) -> list[GridCell]:
    text = raw.decode("utf-8")
    rows = list(csv.reader(io.StringIO(text, newline="")))
    if not rows or rows[0] != COLUMNS:
        raise GridError("esquema exacto de 15 columnas")
    out = []
    for r in rows[1:]:
        if len(r) != len(COLUMNS):
            raise GridError("ancho de fila")
        d = dict(zip(COLUMNS, r))
        cell = GridCell(d["country_id"], d["policy_variant_id"], d["regime_id"], d["requirement_basis"], d["xi"],
                        *(float(d[k]) for k in ("cost_gross_gdp", "F_admin", "F_trans", "F_leak", "F_fix", "F_fix_perp", "s_PB", "Q")))
        out.append(cell)
    ids = [c.external_cell_id for c in out]
    if len(ids) != len(set(ids)):
        raise GridError("celda externa duplicada")
    return out


def identities(cells: list[GridCell]) -> dict:
    """V6: reconstrucción del requerimiento dentro de T1 = 1e-12; partición de F_fix; capas particionan la grilla."""
    worst = {"Q": 0.0, "F_fix": 0.0, "F_fix_perp": 0.0}
    for c in cells:
        worst["Q"] = max(worst["Q"], abs(c.Q("addback_completo") - c.Q_grid))
        worst["F_fix"] = max(worst["F_fix"], abs(c.F_admin + c.F_trans + c.F_leak - c.F_fix))
        worst["F_fix_perp"] = max(worst["F_fix_perp"], abs(c.F_fix - c.F_leak - c.F_fix_perp))
    counts = {}
    for c in cells:
        counts[c.layer] = counts.get(c.layer, 0) + 1
    return {"worst_residuals": worst, "pass": all(v <= T1 for v in worst.values()), "layer_counts": dict(sorted(counts.items()))}


def K1(Q: float, dme_gai: float, lambda_pi: float, gain_share: float) -> float | None:
    """(24): definido solo con lambda > 0 y gain_share > 0; en otro caso None (sin valor inventado)."""
    if not (lambda_pi > 0 and gain_share > 0):
        return None
    return (Q + dme_gai) / (lambda_pi * gain_share)
