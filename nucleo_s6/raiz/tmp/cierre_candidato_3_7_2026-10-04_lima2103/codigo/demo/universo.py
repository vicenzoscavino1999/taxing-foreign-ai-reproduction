"""Universo de una afirmación con metadatos por contexto (VALIDACIÓN 3.7, NO OFICIAL).

Reproduce el bucle de `Run.claim_contexts` (src/paper2b/run.py:1079-1120) en el mismo orden (combinación macro ordenada
por nombre -> país -> estado nacional -> instrumento) y además conserva, por contexto, de dónde sale cada número: vértice
macro, estado nacional, celda externa que realiza min Q de (país, capa, cota) y fijos. La parte por estado (states_for +
MC.bridge) se calcula una vez por (conjunto, bloque, países, años) y se reutiliza entre afirmaciones (refactor exacto;
la igualdad con el original se comprueba en el verificador).
"""
from __future__ import annotations

from itertools import product

from paper2b import cobertura as COV
from paper2b import run as RUNMOD

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
