"""Registro de afirmaciones (B/claims.csv) derivado de reglas aprobadas ANTES de observar resultados.

Fuentes normativas (no elecciones nuevas):
- diseño §17.1-17.2 y MANIFIESTO D1: G_best_{c,j}(omega) = C2 - min_{p,r,b} K1 dentro del MISMO omega; titular
  país-instrumento: sup_omega G_best <= -eps (infactibilidad robusta); factibilidad robusta: inf_omega G_best >= +eps;
  país: para todos los instrumentos j reportados; varios países: país por país;
- MANIFIESTO D2 / §16.2 y D8: cada cota del crosswalk y cada bloque eta_w por separado; capas nunca fundidas (§17.3);
- CONTINGENCIA_A2 §5: se conserva el cuantificador del claim y se añade la exigencia universal sobre los escenarios y
  estados de fuente preregistrados que el claim cubre (vértices de precisión, años del ancla, ediciones E2);
- registro A1-E v2: preregistros, tipos de afirmación (primary / historical_anchor) y años exactos.
Predicado único: el veredicto §17 del universo del claim es de signo uniforme; su signo se fija en la línea base.
Lo que las reglas no especifican (comparaciones o rankings entre países) NO se registra: queda delimitado.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

EPS_ECON = 0.01
LAYERS = ("buffer_destacado", "guardrail_deuda", "nucleo_contable", "sensibilidad")
BOUNDS = ("addback_completo", "sin_addback")
BLOCKS = ("macro", "micro")
DESIGNS = ("G", "N")
PREDICATE = "SIGN_UNIFORM_VERDICT_17"
PREDICATE_TEXT = ("veredicto §17 de signo uniforme sobre el universo: robust_infeasible si sup G_best <= -eps_econ; "
                  "robust_feasible si inf G_best >= +eps_econ; en otro caso inconclusive (sin afirmación)")
UNDECLARED = ("comparaciones o rankings entre países (el registro A1-E v2 no fija predicado ni cuantificador; §17.3.1 "
              "prohíbe inferir el titular de varios países desde la celda más barata)")


@dataclass(frozen=True)
class Claim:
    claim_id: str
    claim_scope: str
    country_id: str | None
    instrument_j: str | None
    availability_case_id: str
    bound_variant: str
    eta_w_block: str
    layer: str
    design: str
    preregistration_id: str
    kind: str
    years: tuple
    scenarios: tuple
    countries: tuple
    instruments: tuple
    editions: tuple
    support_sets: tuple

    def quantifier(self) -> str:
        q = {"cells": "G_best = max sobre (policy_variant_id, regime_id, requirement_basis) de la capa y cota (§17.2), mismo omega",
             "omega": "forall omega admisible del soporte CONTINUO de los support_sets declarados: nudos evaluados y continuo entre nudos con cobertura certificada (ESTRATEGIA_DE_CALCULO §4-§5); sin cobertura no hay veredicto",
             "national_states": "forall estados nacionales de los escenarios preregistrados (CONTINGENCIA_A2 §5)",
             "countries": list(self.countries), "instruments": list(self.instruments), "design": self.design,
             "preregistration_id": self.preregistration_id, "kind": self.kind, "years": list(self.years),
             "scenarios": list(self.scenarios), "editions": list(self.editions), "support_sets": list(self.support_sets),
             "aggregation": {"global": "país por país", "country": "todos los instrumentos reportados",
                             "country_instrument": "universo de la celda"}[self.claim_scope]}
        return json.dumps(q, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

    def row(self, baseline_status: str) -> dict:
        return {"claim_id": self.claim_id, "claim_scope": self.claim_scope, "country_id": self.country_id,
                "instrument_j": self.instrument_j, "availability_case_id": self.availability_case_id,
                "bound_variant": self.bound_variant, "eta_w_block": self.eta_w_block, "layer": self.layer,
                "predicate": PREDICATE, "quantifier": self.quantifier(), "epsilon_econ": "0.01",
                "baseline_status": baseline_status}


def instruments_for(model_case_map: list, country: str) -> dict:
    """Menús disponibles por escenario jurídico (V5 §7): d siempre; f/df solo con pata extranjera (conditional_full)."""
    out = {"conditional_full": [], "conditional_none": []}
    for r in model_case_map:
        if r["country_id"] != country:
            continue
        j = r["model_menu"].removeprefix("j_")
        if r["case_id"] == "domestic_unchanged":
            out["conditional_full"].append((j, "domestic_unchanged"))
            out["conditional_none"].append((j, "domestic_unchanged"))
        elif r["case_id"] == "conditional_full":
            out["conditional_full"].append((j, "conditional_full"))
    return {k: sorted(set(v)) for k, v in out.items()}


def derive(registry: dict, model_case_map: list, support_sets: dict) -> list[Claim]:
    """support_sets: preregistration_id -> {edition_label: {block: base_support_set_id}}."""
    claims = []
    for entry in registry["entries"]:
        pid = entry["preregistration_id"]
        countries = tuple(sorted(entry["country_set"]))
        sets = support_sets[pid]
        editions = tuple(sorted(sets))
        for kind, years in sorted(entry["claims"].items()):
            for design in DESIGNS:
                for block in BLOCKS:
                    ss = tuple(sorted(sets[e][block] for e in editions))
                    for bound in BOUNDS:
                        for layer in LAYERS:
                            base = dict(bound_variant=bound, eta_w_block=block, layer=layer, design=design,
                                        preregistration_id=pid, kind=kind, years=tuple(years),
                                        scenarios=tuple(entry["scenarios"]), editions=editions, support_sets=ss)
                            for scen in ("conditional_full", "conditional_none"):
                                per_country = {c: instruments_for(model_case_map, c)[scen] for c in countries}
                                for c in countries:
                                    for j, avail in per_country[c]:
                                        cid = f"CLM:{pid}:{kind}:ci:{c}:{j}:{avail}:{design}:{bound}:{block}:{layer}"
                                        if not any(x.claim_id == cid for x in claims):
                                            claims.append(Claim(cid, "country_instrument", c, j, avail, countries=(c,),
                                                                instruments=(j,), **base))
                                    cid = f"CLM:{pid}:{kind}:c:{c}:{scen}:{design}:{bound}:{block}:{layer}"
                                    claims.append(Claim(cid, "country", c, None, scen, countries=(c,),
                                                        instruments=tuple(j for j, _ in per_country[c]), **base))
                                if len(countries) > 1:
                                    cid = f"CLM:{pid}:{kind}:g:{scen}:{design}:{bound}:{block}:{layer}"
                                    claims.append(Claim(cid, "global", None, None, scen, countries=countries,
                                                        instruments=tuple(sorted({j for c in countries for j, _ in per_country[c]})),
                                                        **base))
    claims.sort(key=lambda c: c.claim_id)
    ids = [c.claim_id for c in claims]
    if len(ids) != len(set(ids)):
        raise ValueError("claim_id duplicado")
    return claims


@dataclass
class Verdict:
    status: str            # verified | inconclusive | not_evaluated
    verdict: str           # robust_infeasible | robust_feasible | inconclusive | not_evaluated
    sup_upper: float | None
    inf_lower: float | None
    n_points: int
    reason: str | None = None


def evaluate(points, eps: float = EPS_ECON, *, complete: bool) -> Verdict:
    """points: iterable de (G_best, error_numérico). Cotas certificadas: G - err, G + err (no se suma eps a los datos)."""
    pts = list(points)
    if not complete or not pts or any(g is None for g, _ in pts):
        return Verdict("not_evaluated", "not_evaluated", None, None, len(pts), "UNIVERSE_NOT_COMPLETE")
    sup_upper = max(g + e for g, e in pts)
    inf_lower = min(g - e for g, e in pts)
    if sup_upper <= -eps:
        return Verdict("verified", "robust_infeasible", sup_upper, inf_lower, len(pts))
    if inf_lower >= eps:
        return Verdict("verified", "robust_feasible", sup_upper, inf_lower, len(pts))
    return Verdict("inconclusive", "inconclusive", sup_upper, inf_lower, len(pts))


def holds(verdict_at_baseline: str, points, eps: float = EPS_ECON) -> bool:
    """¿Se sostiene el veredicto de la línea base sobre un universo modificado (robustez)?"""
    pts = list(points)
    if verdict_at_baseline == "robust_infeasible":
        return max(g + e for g, e in pts) <= -eps
    if verdict_at_baseline == "robust_feasible":
        return min(g - e for g, e in pts) >= eps
    raise ValueError("sin afirmación en la línea base")


def evaluate_summary(sup_upper, inf_lower, n: int, *, complete: bool, any_none: bool, eps: float = EPS_ECON) -> Verdict:
    """Igual que evaluate() a partir de estadísticos suficientes (max G+err, min G-err, n) agregados por unidades."""
    if not complete or n == 0 or any_none or sup_upper is None or inf_lower is None:
        return Verdict("not_evaluated", "not_evaluated", None, None, n, "UNIVERSE_NOT_COMPLETE")
    if sup_upper <= -eps:
        return Verdict("verified", "robust_infeasible", sup_upper, inf_lower, n)
    if inf_lower >= eps:
        return Verdict("verified", "robust_feasible", sup_upper, inf_lower, n)
    return Verdict("inconclusive", "inconclusive", sup_upper, inf_lower, n)
