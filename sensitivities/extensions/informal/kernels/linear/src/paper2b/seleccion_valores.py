"""CÁLCULO POR VALORES de una celda B del paso 4 (RELACIONES CONTRATO 3.7, NO OFICIAL; núcleo candidato aislado).

Movido a la estructura candidata desde los módulos del área (codigo/demo/universo.py, codigo/demo/celdas.py y
omega_por_valores de codigo/generador_candidato_v2.py) SIN cambios de lógica: universo de una afirmación con metadatos
por contexto (orden de Run.claim_contexts), ω por valores del testigo, frontera/techo, estados macro, celda (las mismas
funciones del núcleo: ceiling, ceiling_rows, states_for, macro_row, cell). Dependencias: solo paper2b (cobertura, keys,
run). El área lo importa desde aquí; no queda delegación a módulos de desarrollo para este cálculo.
"""
from __future__ import annotations

import time
from decimal import Decimal
from itertools import product

from . import cobertura as COV
from . import keys as K
from . import run as RUNMOD

STRUCT = RUNMOD.STRUCT


class SeleccionError(RuntimeError):
    pass


def need(test, code):
    if not test:
        raise SeleccionError(code)


def axes_nodes(view, cfg, set_id: str) -> dict:
    """Nudos estructurales del nivel de la configuración (como codigo/demo/nucleo_v.axes_nodes, con dependencias explícitas)."""
    from .supports import level_nodes
    return {pid: level_nodes(view.nodes(set_id, pid), view.support(set_id, pid)["scale"], cfg.level) for pid in STRUCT}


MACRO = ("eta_w", "gain_share", "pi_iva", "pi_otros_productos", "pi_produccion")


def qmin_table(grid_cells, bounds=("addback_completo", "sin_addback")):
    """(país, capa, cota) -> (min Q, id de la primera celda que lo realiza en el orden de la grilla)."""
    t = {}
    for g in grid_cells:
        for b in bounds:
            k = (g.country_id, g.layer, b)
            q = g.Q(b)
            if k not in t or q < t[k][0]:
                t[k] = (q, g.external_cell_id)
    return t


def state_meta(st) -> dict:
    return {"pais": st.country_id, "preregistro": st.preregistration_id, "canal": st.channel, "edicion": st.edition,
            "anio_ancla": st.anchor_year, "etiqueta": st.label, "dominio_conjunto_sha256": st.joint_domain_sha256}


class Universo:
    def __init__(self, runs: dict, qmin: dict):
        self.runs, self.qmin = runs, qmin
        self._base, self._avail = {}, {}

    def fixed(self, set_id):
        d7 = self.runs[set_id].inp.d7
        fixed_axes = {pid: d7.nodes(set_id, pid) for pid in RUNMOD.FIXED + RUNMOD.BARS}
        out = None
        for fcombo in product(*[fixed_axes[n] for n in sorted(fixed_axes)]):
            fv = dict(zip(sorted(fixed_axes), fcombo))
            if out is None:
                out = fv
            elif fv != out:
                return None
        return out

    def base(self, set_id, block, countries, years, corner):
        key = (set_id, block, tuple(countries), tuple(years))
        if key in self._base:
            return self._base[key]
        r = self.runs[set_id]
        d7 = r.inp.d7
        axes = {}
        for pid in MACRO:
            lo, hi = d7.interval(set_id, pid)
            axes[pid] = [lo] if lo == hi else [lo, hi]
        axes["eta_H"] = d7.nodes(set_id, "eta_H")
        fixed = self.fixed(set_id)
        names = sorted(axes)
        out = []
        for combo in product(*[axes[n] for n in names]):
            mv = dict(zip(names, combo))
            v = dict(corner, **mv, **fixed)
            if r.block_of(v["eta_w"]) != block:
                continue
            for country in countries:
                for st in r.states_for({"set": set_id, "values": v}, country):
                    if st.anchor_year not in years:
                        continue
                    m = RUNMOD.MC.bridge(st.share_dict(), v)
                    out.append((country, st, {k: str(x) for k, x in mv.items()}, float(m.s_Pi_marg), float(m.s_T_marg),
                                float(v["eta_H"]), float(v["gain_share"])))
        self._base[key] = (out, fixed)
        return self._base[key]

    def available(self, set_id, country, j):
        k = (set_id, country, j)
        if k not in self._avail:
            self._avail[k] = bool([c for jj, c, avail, _ in self.runs[set_id].frontier_cases(country) if jj == j and avail])
        return self._avail[k]

    def contexts(self, cl, set_id, corner):
        """[(Context, índice en la base)] en el orden de Run.claim_contexts, y los fijos."""
        base, fixed = self.base(set_id, cl.eta_w_block, cl.countries, cl.years, corner)
        r = self.runs[set_id]
        out = []
        for bi, (country, st, mv, s_pi, s_t, eta_h, gain) in enumerate(base):
            q = self.qmin.get((country, cl.layer, cl.bound_variant))
            if q is None:
                continue
            for j in cl.instruments:
                if not self.available(set_id, country, j):
                    continue
                out.append((COV.Context(cl.design, j, (float(fixed["bar_tau_d"]), float(fixed["bar_tau_f"])), s_pi, s_t, eta_h,
                                        gain, q[0] + r.inp.dme_gai), bi))
        return out, fixed

    def meta(self, cl, set_id, corner, bi):
        base, fixed = self.base(set_id, cl.eta_w_block, cl.countries, cl.years, corner)
        country, st, mv, *_ = base[bi]
        q = self.qmin[(country, cl.layer, cl.bound_variant)]
        return {"pais": country, "estado_nacional": state_meta(st), "macro": mv,
                "celda_externa": {"id": q[1], "Q": q[0], "capa": cl.layer, "cota": cl.bound_variant},
                "dme_gai": self.runs[set_id].inp.dme_gai, "fijos": {k: str(v) for k, v in fixed.items()}}


def omega_por_valores(r, set_id, punto, mv):
    ov = {pid: [Decimal(repr(float(punto[pid])))] for pid in STRUCT}
    for pid in MACRO:
        ov[pid] = [Decimal(str(mv[pid]))]
    ov["eta_H"] = [Decimal(str(mv["eta_H"]))]
    vals = list(r.omega_points(set_id, overrides=ov))
    need(len(vals) == 1, "OMEGA_POR_VALORES_NO_UNICO:%d" % len(vals))
    values = vals[0]
    oid, common, ok, reason, derived, ident = r.omega_row(set_id, values)
    if oid not in r.omegas:
        r.omegas[oid] = {"set": set_id, "values": values, "admissible": ok, "derived": derived, "common_sha": K.H(common),
                         "block": r.block_of(values["eta_w"])}
        r.rows["omega"].append({"omega_id": oid, "support_set_id": set_id, "scenario_id": r.inp.d7.layer_scenario(set_id),
                                "primitive_values_sha256": ident["primitive_values_sha256"],
                                "domain_status": "admissible" if ok else "excluded", "reason_code": reason})
    return oid, ok, reason


def omega_list(r) -> list:
    """Omegas admisibles del punto estructural, en orden determinista (id)."""
    if not r.omegas:
        r.build_omegas()
    return sorted(oid for oid, om in r.omegas.items() if om["admissible"])


def frontier(r, oid: str, country: str, design: str, j: str, case: str) -> tuple[dict, float]:
    """Frontera/techo de la combinación (mismo cuerpo que Run.build_frontiers para una sola tupla). Devuelve (fr, seg)."""
    om = r.omegas[oid]
    rows = [x for x in r.frontier_cases(country) if x[0] == j and x[1] == case]
    need(len(rows) == 1, "PILOT_CASE_NOT_IN_D4_MAP:%s:%s:%s" % (country, j, case))
    _, _, available, d4row = rows[0]
    tau_id = f"TAU:{om['set']}:{j}"
    fid = "FRN:" + K.H({"r": r.run_id, "d": design, "c": country, "j": j, "a": case, "o": oid, "t": tau_id})[:40]
    t0 = time.time()
    skey, hit = r.ceiling(om["values"], design, j) if available else r.structural_only(om["values"], design, j)
    secs = time.time() - t0
    r.rows["frontier_context"].append({
        "frontier_id": fid, "run_id": r.run_id, "design_v": design, "country_id": country, "instrument_j": j,
        "availability_case_id": case, "availability_matrix_hash": r.inp.availability_matrix_hash, "omega_id": oid,
        "structural_key_sha256": skey, "tau_domain_id": tau_id, "structural_key_payload": hit["payload"]})
    fr = {"frontier_id": fid, "skey": skey, "hit": hit, "available": available, "d4": d4row}
    r.frontiers = getattr(r, "frontiers", {})
    r.frontiers[(oid, country, design, j, case)] = fr
    r.ceiling_rows(fid, hit, available, d4row, om)
    return fr, secs


def macro_states(r, oid: str, country: str, design: str, j: str, case: str) -> list:
    """Filas macro de la combinación (mismo cuerpo que Run.build_macro para un omega y país)."""
    om = r.omegas[oid]
    before = len(r.macros.get((oid, country), []))
    for st in r.states_for(om, country):
        if st.channel == "strict":
            r.macro_row(oid, om, country, st, None)
        else:
            r.macro_row(oid, om, country, st, (design, j, case))
    ms = r.macros.get((oid, country), [])[before:]
    return [m for m in ms if m["context"] in (None, (design, j, case))]


def grid_cells(r, country: str) -> list:
    return [c for c in r.inp.grid_cells if c.country_id == country]


def build_cell(r, oid, country, design, j, case, fr, mac, gcell, bound) -> str:
    """Celda (mismo cuerpo que Run.build_cells -> Run.cell). Devuelve el cell_id."""
    n0 = len(r.rows["confrontation_result"])
    r.cell(r.omegas[oid], oid, country, design, j, case, fr, mac, gcell, bound)
    return r.rows["confrontation_result"][n0]["cell_id"]
