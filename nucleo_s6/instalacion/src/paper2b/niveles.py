"""Comparación entre niveles de refinamiento (ESTRATEGIA §5): cifras, raíces, geometría y afirmaciones.

Compara dos corridas B del mismo D7/configuración salvo el nivel de nudos (L y L+1, anidados: los nudos de L son nudos
de L+1). Las filas se emparejan por CLAVE SEMÁNTICA (no por identificador, que incluye el run_id):
- cifras: C2 por (omega, diseño, país, menú, caso) y G por celda (+ capa, cota y celda externa);
- raíces: número de raíces y tangencias por sección R2; estado de las inversiones endógenas;
- geometría: número y tipos de componentes R1;
- afirmaciones: estado y veredicto por claim_id (los claims son los mismos: registro predeclarado).
Resultado: diferencias máximas, cambios de topología/veredicto y nudos nuevos sin contraparte. La ESTABILIDAD entre
niveles no es cobertura: el informe lo declara y no modifica ningún estado de cobertura (ESTRATEGIA §5 y §8).
"""
from __future__ import annotations

from decimal import Decimal


def _D(x):
    return None if x is None else Decimal(str(x))


def _cell_key(ctx: dict) -> tuple:
    # sin claves con huellas técnicas (la configuración cambia con el nivel): estado nacional + bloque laboral
    return (ctx["omega_id"], ctx["design_v"], ctx["country_id"], ctx["instrument_j"], ctx["availability_case_id"],
            ctx["external_cell_id"], ctx["bound_variant"], ctx["national_state_sha256"], ctx["eta_w_block"])


def _index(t: dict) -> dict:
    ctx = {c["cell_id"]: c for c in t["cell_context"]}
    conf = {_cell_key(ctx[r["cell_id"]]): r for r in t["confrontation_result"]}
    r1 = {_cell_key(ctx[r["cell_id"]]): r for r in t["r1_summary"]}
    comps = {}
    for c in t["r1_components"]:
        comps.setdefault(_cell_key(ctx[c["cell_id"]]), []).append(c["topology_kind"])
    r2 = {_cell_key(ctx[r["cell_id"]]) + (r["section_id"],): r for r in t["r2_sections"]}
    inv = {_cell_key(ctx[r["cell_id"]]) + (r["inversion_id"],): r for r in t["inversion_result"]
           if r["inversion_id"] in ("phi_total", "external_factor")}
    claims = {c["claim_id"]: c for c in t["claims"]}
    return {"conf": conf, "r1": r1, "comps": comps, "r2": r2, "inv": inv, "claims": claims}


def compare(t_lo: dict, t_hi: dict, *, tol: float) -> dict:
    a, b = _index(t_lo), _index(t_hi)
    rep = {"shared_cells": 0, "new_cells_at_finer_level": 0, "missing_at_finer_level": 0, "max_abs_change_C2": 0.0,
           "max_abs_change_G": 0.0, "verdict_changes": 0, "status_changes": 0, "r2_root_count_changes": 0,
           "r1_topology_changes": 0, "endogenous_status_changes": 0, "claim_changes": [], "tolerance": tol}
    for k, ra in a["conf"].items():
        rb = b["conf"].get(k)
        if rb is None:
            rep["missing_at_finer_level"] += 1
            continue
        rep["shared_cells"] += 1
        if ra["computation_status"] != rb["computation_status"]:
            rep["status_changes"] += 1
        if ra["verdict"] != rb["verdict"]:
            rep["verdict_changes"] += 1
        for f, key in (("C_2", "max_abs_change_C2"), ("G", "max_abs_change_G")):
            if ra[f] is not None and rb[f] is not None:
                rep[key] = max(rep[key], float(abs(_D(ra[f]) - _D(rb[f]))))
        r1a, r1b = a["r1"].get(k), b["r1"].get(k)
        if r1a and r1b and (r1a["n_components"] != r1b["n_components"] or
                            sorted(a["comps"].get(k, [])) != sorted(b["comps"].get(k, []))):
            rep["r1_topology_changes"] += 1
    rep["new_cells_at_finer_level"] = sum(1 for k in b["conf"] if k not in a["conf"])
    for k, ra in a["r2"].items():
        rb = b["r2"].get(k)
        if rb is not None and (ra["n_roots_by_section"], ra["n_tangential_roots"]) != (rb["n_roots_by_section"], rb["n_tangential_roots"]):
            rep["r2_root_count_changes"] += 1
    for k, ra in a["inv"].items():
        rb = b["inv"].get(k)
        if rb is not None and (ra["result_status"], ra["n_scalar_solutions"]) != (rb["result_status"], rb["n_scalar_solutions"]):
            rep["endogenous_status_changes"] += 1
    for cid, ca in a["claims"].items():
        cb = b["claims"].get(cid)
        if cb is None or ca["baseline_status"] != cb["baseline_status"]:
            rep["claim_changes"].append({"claim_id": cid, "level_lo": ca["baseline_status"],
                                         "level_hi": None if cb is None else cb["baseline_status"]})
    rep["stable"] = (rep["verdict_changes"] == 0 and rep["status_changes"] == 0 and rep["r2_root_count_changes"] == 0 and
                     rep["r1_topology_changes"] == 0 and rep["endogenous_status_changes"] == 0 and not rep["claim_changes"]
                     and rep["max_abs_change_C2"] <= tol and rep["max_abs_change_G"] <= tol and rep["missing_at_finer_level"] == 0)
    rep["note"] = ("estabilidad entre niveles anidados: evidencia de convergencia de las cifras en nudos compartidos; NO es "
                   "cobertura del continuo (dos mallas estables no certifican ausencia de raíces/componentes entre nudos)")
    return rep
