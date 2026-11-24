"""Reglas contratadas de las tablas B (catálogo CA2-4 candidato, 'rules' de cada tabla) verificadas SOBRE LAS FILAS.

Independiente del productor: no importa run.py ni reutiliza sus estructuras; reconstruye claves desde payloads
(common_values, omega_identity, structural, macro-v2) con el núcleo S3 (Contracts.key / bind_context) y comprueba
estados, nulos condicionales, conteos de tablas hijas, identidades contables (T1) y referencias internas.
Devuelve la lista de violaciones (vacía = conforme). Las filas condicionales macro-ca2-v2 se validan con el esquema
macro_ca2 de la enmienda CA2-4 (forma) y con resolución semántica del bundle, caso, entradas, vectores y contexto de celda.
Garantías numéricas del consumidor (hallazgos B): una fila 'complete' de R1/R2/inversión endógena exige evidencia de
cobertura CERTIFICADA (numerical_evidence status pass); toda raíz publicada tiene residuo <= tolerancia y converged=true;
el margen del veredicto §17 usa la cota certificada del techo o max(estimación, T2 validado).
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from decimal import Decimal

from . import claves_condicionales as CK
from . import keys as K

T1 = Decimal("1e-12")
EPS = Decimal("0.01")
MACRO_CA2_V2 = ["kind", "bundle_sha256", "case_id", "scenario", "preregistration_id", "case_type", "country_set", "country_id",
                "anchor_year", "d2_vector_sha256", "d6_vector_sha256", "context_sha256", "common_values_sha256", "eta_w_block",
                "protocol_sha256", "technical"]
INV_STATUS = {"computed": "complete", "outside_support": "complete", "no_feasible_solution": "complete",
              "not_identified": "not_applicable", "undefined_denominator": "excluded", "failed": "failed", "incomplete": "incomplete"}
VALUE_FIELD = {"lambda_required": "lambda_pi_required", "gain_required": "delta_y_required", "capture_required": "C_2_required",
               "external_factor": "external_factor_required", "phi_partial": "phi_critical_partial", "phi_total": "phi_critical_total"}
ENDOGENOUS = ("external_factor", "phi_total")
BRK_STATUS = {"breakdown_found": "complete", "domain_exhausted_no_breakdown": "complete",
              "declared_ladder_exhausted_no_breakdown": "complete", "theoretical_boundary_no_breakdown": "complete",
              "admissibility_boundary_no_breakdown": "complete", "not_applicable_baseline_inconclusive": "not_applicable",
              "not_applicable_support_gap": "not_applicable", "not_applicable_not_identified": "not_applicable",
              "no_solution": "failed", "incomplete_search": "incomplete"}
QS_STATUS = {"breakdown_found": "complete", "scale_range_exhausted_no_breakdown": "complete",
             "not_applicable_baseline_inconclusive": "not_applicable", "no_solution": "failed", "incomplete_search": "incomplete"}
EDGES = {"rho_upper_S4", "rho_zero_limit", "a_gt1", "theta_gt1", "theta_lt_a", "kappa_positive", "q_pot", "eta_H", "lambda_pi",
         "s_T_marg", "s_Pi_marg", "ninguno"}


def D(x):
    return None if x is None else Decimal(x)


class Checker:
    def __init__(self, tables: dict, contracts, d7, *, technical: dict | None = None, protocol_sha256: str | None = None,
                 grid_cells: list | None = None, resolver=None, tolerances: dict | None = None):
        self.t, self.C, self.d7 = tables, contracts, d7
        self.technical, self.protocol = technical, protocol_sha256
        self.resolver = resolver
        tol = tolerances or {}
        self.t2 = Decimal(str(tol.get("T2_target_capture_share", "1e-4")))
        self.tol_root = Decimal(str(tol.get("T_root_residual", "1e-9")))
        self.pass_evidence = defaultdict(set)
        for e in tables.get("numerical_evidence", []):
            if e["status"] == "pass" and e["result_table"]:
                self.pass_evidence[(e["result_table"], json.dumps(e["record_pk"], sort_keys=True))].add(e["method_id"])
        self.grid = {g.external_cell_id: g for g in grid_cells} if grid_cells is not None else None
        self.errors: list = []
        self.units = {pid: p.get("unit", "not_applicable") for pid, p in contracts.F["parameters"].items()}
        self.by = {name: {} for name in tables}
        for name, rows in tables.items():
            pk = contracts.C["tables"][name]["primary_key"]
            for r in rows:
                self.by[name][tuple(r[k] for k in pk)] = r

    def fail(self, table, pk, msg):
        self.errors.append(f"{table}{json.dumps(pk, sort_keys=True, default=str)}: {msg}")

    def need(self, test, table, pk, msg):
        if not test:
            self.fail(table, pk, msg)

    # ----------------------------------------------------------------------------- omega
    def omega(self):
        vals = defaultdict(dict)
        for r in self.t["omega_values"]:
            vals[r["omega_id"]][r["parameter_id"]] = r
        self.common = {}
        self.identity = {}
        for o in self.t["omega"]:
            oid = o["omega_id"]
            self.need(o["domain_status"] in ("admissible", "excluded"), "omega", oid, "domain_status")
            self.need(o["domain_status"] != "excluded" or o["reason_code"], "omega", oid, "excluido sin motivo")
            self.need(o["scenario_id"] in self.d7.scenarios, "omega", oid, "escenario no registrado en D7")
            self.need(self.d7.scenarios.get(o["scenario_id"], {}).get("support_set_id") == o["support_set_id"], "omega", oid,
                      "scenario.support_set_id no coincide")
            rows = vals.get(oid, {})
            prim = {p: r for p, r in rows.items() if r["formula_id"] is None}
            for p, r in rows.items():
                if r["value"] is None:
                    self.need(r["reason_code"], "omega_values", (oid, p), "null sin motivo")
                if r["formula_id"] is None and r["value"] is not None:
                    b = self.d7.bindings.get((o["support_set_id"], p, "global"))
                    self.need(b is not None and r["binding_id"] == b["binding_id"], "omega_values", (oid, p),
                              "primitiva activa sin binding global del mismo set")
                self.need(p in self.C.K["common_primitive_ids"] or p in self.C.K["common_derived_ids"], "omega_values", (oid, p),
                          "parámetro fuera de la lista común (nacional o resultado B en omega)")
            try:
                common = K.common_values({p: Decimal(prim[p]["value"]) for p in self.C.K["common_primitive_ids"]}, self.C.K,
                                         self.units)
                self.C.key("common_values", common)
                ident = K.omega_identity(o["support_set_id"], o["scenario_id"], common)
                self.C.key("omega_identity", ident)
                self.need(K.omega_id(ident) == oid, "omega", oid, "omega_id no se reconstruye")
                self.need(ident["primitive_values_sha256"] == o["primitive_values_sha256"], "omega", oid,
                          "primitive_values_sha256 no se reconstruye")
                self.common[oid], self.identity[oid] = common, ident
            except Exception as exc:  # noqa: BLE001
                self.fail("omega", oid, "claves comunes: " + str(exc))

    # ----------------------------------------------------------------------------- estructura
    def frontier(self):
        omega = self.by["omega"]
        for f in self.t["frontier_context"]:
            fid = f["frontier_id"]
            o = omega.get((f["omega_id"],))
            self.need(o is not None and o["domain_status"] == "admissible", "frontier_context", fid, "refiere omega excluido")
            sp = f["structural_key_payload"]
            try:
                self.C.key("structural", sp, f["structural_key_sha256"])
            except Exception as exc:  # noqa: BLE001
                self.fail("frontier_context", fid, "clave estructural: " + str(exc))
                continue
            for k in ("design_v", "instrument_j"):
                self.need(sp[k] == f[k], "frontier_context", fid, "columna/payload estructural: " + k)
            if self.technical is not None:
                self.need(sp["technical"] == self.technical, "frontier_context", fid, "huellas técnicas distintas de las del run")
            common = self.common.get(f["omega_id"])
            if common:
                exp = [r for r in common["values"] if r["parameter_id"] in self.C.K["structural_primitive_ids"]]
                self.need(sp["values"] == exp, "frontier_context", fid, "proyección estructural distinta de omega")
                v = {r["parameter_id"]: r["value"] for r in common["values"]}
                for axis in ("d", "f"):
                    cap = v["bar_tau_" + axis] if sp["instrument_j"] in (axis, "df") else "0"
                    self.need(sp["tau_domain"]["tau_" + axis + "_upper"] == cap, "frontier_context", fid, "tope fiscal/omega")
            td = self.d7.tau_domains.get((o["support_set_id"] if o else None, f["instrument_j"]))
            self.need(f["tau_domain_id"].startswith("TAU:"), "frontier_context", fid, "tau_domain_id")

    def frontier_result(self):
        for r in self.t["frontier_result"]:
            pk = (r["frontier_id"], r["point_id"])
            self.need(r["regime"] in ("interior", "esquina_f", "esquina_d", "origen", "borde"), "frontier_result", pk, "regime")
            if r["computation_status"] == "complete":
                for k in ("B_d", "B_f", "R", "B_pot", "CS"):
                    self.need(r[k] is not None, "frontier_result", pk, "complete exige " + k)
                if r["R"] is not None and r["B_pot"] is not None and r["CS"] is not None:
                    self.need(abs(D(r["CS"]) - D(r["R"]) / D(r["B_pot"])) <= T1 * max(1, abs(D(r["CS"]))), "frontier_result", pk,
                              "CS != R/B_pot")
                self.need(r["B_f_grav"] == r["B_f"], "frontier_result", pk, "B_f_grav != B_f bajo baseline")
            else:
                self.need(r["reason_code"], "frontier_result", pk, "no completo sin motivo")

    def ceilings(self):
        wit = defaultdict(list)
        for w in self.t["sup_witness"]:
            wit[w["ceiling_id"]].append(w)
        fr = self.by["frontier_context"]
        avail = defaultdict(dict)
        for c in self.t["capture_ceiling_result"]:
            cid = c["ceiling_id"]
            if not c["instrument_available"]:
                self.need(c["computation_status"] == "not_applicable" and c["C_2"] is None and
                          c["monotonicity_check"] == "not_applicable", "capture_ceiling_result", cid, "no disponible")
                continue
            self.need(c["monotonicity_check"] in ("pass", "fail", "not_applicable"), "capture_ceiling_result", cid, "monotonicity_check")
            if c["computation_status"] == "complete":
                self.need(c["C_2"] is not None and c["numerical_error"] is not None and c["sup_not_attained"] is not None,
                          "capture_ceiling_result", cid, "complete exige C_2, error y sup_not_attained")
                if c["sup_not_attained"]:
                    self.need(c["tau_d_at_sup"] is None and c["tau_f_at_sup"] is None and c["sup_lateral_low"] is not None
                              and c["sup_lateral_high"] is not None and wit.get(cid), "capture_ceiling_result", cid,
                              "sup no alcanzado exige tasas null, laterales y testigos")
                else:
                    self.need(c["tau_d_at_sup"] is not None and c["tau_f_at_sup"] is not None, "capture_ceiling_result", cid,
                              "sup alcanzado exige tasas")
                f = fr.get((c["frontier_id"],))
                if f:
                    avail[(f["omega_id"], f["country_id"], f["design_v"], f["availability_case_id"])][f["instrument_j"]] = c
            else:
                self.need(c["C_2"] is None or c["computation_status"] != "complete", "capture_ceiling_result", cid, "estado")
                self.need(c["reason_code"], "capture_ceiling_result", cid, "no completo sin motivo")
        for cid, ws in wit.items():
            for side in {w["side"] for w in ws}:
                seq = sorted((w for w in ws if w["side"] == side), key=lambda w: w["sequence_index"])
                self.need([w["sequence_index"] for w in seq] == list(range(len(seq))), "sup_witness", cid, "índices desde 0")
                ds = [D(w["approach_distance"]) for w in seq]
                self.need(all(d >= 0 for d in ds) and all(a > b for a, b in zip(ds, ds[1:])), "sup_witness", cid,
                          "distancia no decreciente o negativa")
        # monotonicidad del menú: C2^d <= C2^df y C2^f <= C2^df sobre los mismos (omega, país, diseño); solo disponibles
        for key, byj in self.monotone_groups(avail).items():
            for j, c in byj.items():
                if c["monotonicity_check"] == "not_applicable":
                    continue
                df = byj.get("df")
                if j == "df" or df is None:
                    continue
                ok = D(c["C_2"]) <= D(df["C_2"]) + D(c["numerical_error"]) + D(df["numerical_error"])
                self.need((c["monotonicity_check"] == "pass") == ok, "capture_ceiling_result", c["ceiling_id"],
                          "monotonicity_check no concuerda con C2 de los menús disponibles")

    @staticmethod
    def monotone_groups(avail):
        out = defaultdict(dict)
        for (oid, country, design, case), byj in avail.items():
            for j, c in byj.items():
                out[(oid, country, design)].setdefault(j, c)
        return out

    # ----------------------------------------------------------------------------- macro y confrontación
    def macro(self):
        omega = self.by["omega"]
        for m in self.t["lambda_pi_envelope"]:
            mid = m["macro_id"]
            p = m["macro_key_payload"]
            if m["admissible"]:
                self.need(D(m["q_pot"]) < 1 and D(m["eta_H"]) > -1 and m["lambda_pi"] is not None and D(m["lambda_pi"]) > 0
                          and D(m["s_T_marg"]) >= 0, "lambda_pi_envelope", mid, "admisible viola q_pot/eta_H/lambda/s_T")
                self.need(m["computation_status"] == "complete", "lambda_pi_envelope", mid, "admisible no completo")
            else:
                self.need(m["reason_code"], "lambda_pi_envelope", mid, "inadmisible sin motivo")
            self.need(m["theta_W_negative"] == (D(m["theta_W"]) < 0), "lambda_pi_envelope", mid, "marca theta_W negativa")
            o = omega.get((m["omega_id"],))
            common = self.common.get(m["omega_id"])
            if p.get("kind") == "macro-v2":
                try:
                    self.C.key("macro", p, m["macro_key_sha256"])
                except Exception as exc:  # noqa: BLE001
                    self.fail("lambda_pi_envelope", mid, "clave macro: " + str(exc))
                    continue
                self.need(K.H(p["national_state"]) == m["national_state_sha256"], "lambda_pi_envelope", mid, "estado nacional")
                self.need(p["country_id"] == m["country_id"] and p["eta_w_block"] == m["eta_w_block"], "lambda_pi_envelope", mid,
                          "columna/payload macro")
                if common:
                    exp = [r for r in common["values"] if r["parameter_id"] in self.C.K["macro_primitive_ids"]]
                    self.need(p["values"] == exp, "lambda_pi_envelope", mid, "proyección macro distinta de omega")
                self.need(Decimal(p["national_state"]["shares"]["s_L_bar"]) == D(m["s_L_bar"]), "lambda_pi_envelope", mid,
                          "s_L_bar columna/payload")
            elif p.get("kind") == "macro-ca2-v2":
                for e in CK.check_shape(p, self.C):
                    self.fail("lambda_pi_envelope", mid, "clave condicional: " + e)
                self.need(K.H(p) == m["macro_key_sha256"], "lambda_pi_envelope", mid, "H(payload) != macro_key_sha256")
                self.need(p["country_id"] == m["country_id"] and p["eta_w_block"] == m["eta_w_block"], "lambda_pi_envelope", mid,
                          "columna/payload macro condicional")
                self.need(p["country_id"] in p["country_set"] and p["scenario"] in ("E1", "E2"), "lambda_pi_envelope", mid,
                          "país/escenario condicional")
                if common:
                    self.need(p["common_values_sha256"] == K.H(common), "lambda_pi_envelope", mid, "common_values_sha256 de otro omega")
            else:
                self.fail("lambda_pi_envelope", mid, "tipo de clave macro desconocido")
                continue
            if self.technical is not None:
                self.need(p["technical"] == self.technical, "lambda_pi_envelope", mid, "huellas técnicas distintas de las del run")
            if self.protocol is not None:
                self.need(p["protocol_sha256"] == self.protocol, "lambda_pi_envelope", mid, "protocolo distinto")
            if common:
                v = {r["parameter_id"]: r["value"] for r in common["values"]}
                self.need(m["eta_w"] == v["eta_w"] and m["eta_H"] == v["eta_H"], "lambda_pi_envelope", mid, "eta_w/eta_H vs omega")

    def confrontation(self):
        cells = self.by["cell_context"]
        macros = self.by["lambda_pi_envelope"]
        ceilings = self.by["capture_ceiling_result"]
        fronts = self.by["frontier_context"]
        for c in self.t["cell_context"]:
            self.need(c["bound_variant"] in ("sin_addback", "addback_completo"), "cell_context", c["cell_id"], "bound_variant")
            self.need(c["country_id"] != "GLOBAL", "cell_context", c["cell_id"], "country GLOBAL")
            if self.grid is not None:
                g = self.grid.get(c["external_cell_id"])
                self.need(g is not None and g.layer == c["layer"] and g.requirement_basis == c["requirement_basis"]
                          and g.country_id == c["country_id"], "cell_context", c["cell_id"], "celda externa no reproduce la grilla")
        for r in self.t["confrontation_result"]:
            cid = r["cell_id"]
            cell = cells.get((cid,))
            mac = macros.get((r["macro_id"],))
            cei = ceilings.get((r["ceiling_id"],))
            fr = fronts.get((cei["frontier_id"],)) if cei else None
            if not (cell and mac and cei and fr):
                self.fail("confrontation_result", cid, "referencias de contexto ausentes")
                continue
            for k in ("country_id", "omega_id", "run_id", "eta_w_block", "national_state_sha256"):
                self.need(cell[k] == mac[k], "confrontation_result", cid, "cruce macro: " + k)
            self.need(cell["expected_macro_key_sha256"] == mac["macro_key_sha256"], "confrontation_result", cid, "macro esperado")
            for k in ("country_id", "omega_id", "run_id", "design_v", "instrument_j", "availability_case_id",
                      "availability_matrix_hash"):
                self.need(cell[k] == fr[k], "confrontation_result", cid, "cruce frontera: " + k)
            mp = mac["macro_key_payload"]
            if mp.get("kind") == "macro-ca2-v2":
                label = f"{cell['design_v']}-{cell['instrument_j']}-{cell['availability_case_id']}"
                self.need(mp.get("case_id", "").endswith(":" + label), "confrontation_result", cid,
                          "clave condicional de otro contexto de celda")
                bundle = self.resolver.bundle(mp.get("bundle_sha256")) if self.resolver is not None else None
                if bundle is None:
                    self.fail("confrontation_result", cid, "semántica condicional NO verificable: bundle no resuelto por hash")
                else:
                    for e in CK.check_semantics(mp, bundle=bundle, bundle_bytes_sha=mp["bundle_sha256"],
                                                contexts=self.resolver.contexts(), cell=cell,
                                                common_sha=K.H(self.common[cell["omega_id"]]) if cell["omega_id"] in self.common else "",
                                                protocol_sha=self.protocol or mp["protocol_sha256"],
                                                technical=self.technical or mp["technical"], matrix_hash=cell["availability_matrix_hash"]):
                        self.fail("confrontation_result", cid, "semántica condicional: " + e)
            if mac["macro_key_payload"].get("kind") == "macro-v2" and cell["omega_id"] in self.common:
                try:
                    self.C.bind_context(self.common[cell["omega_id"]], self.identity[cell["omega_id"]], cell, mac, fr)
                except Exception as exc:  # noqa: BLE001
                    self.fail("confrontation_result", cid, "bind_context: " + str(exc))
            st = r["computation_status"]
            if st == "complete":
                self.need(None not in (r["C_2"], r["K_comp_1"], r["G"]), "confrontation_result", cid, "complete exige C2,K,G")
                if None not in (r["C_2"], r["K_comp_1"], r["G"]):
                    g = D(r["G"])
                    self.need(abs(g - (D(r["C_2"]) - D(r["K_comp_1"]))) <= T1 * max(1, abs(g)), "confrontation_result", cid,
                              "G != C2 - K")
                    self.need(r["C_2"] == cei["C_2"], "confrontation_result", cid, "C2 de otro techo")
                    est = D(cei["numerical_error"]) or Decimal(0)
                    certified = "certified_branch_and_bound" in self.pass_evidence.get(
                        ("capture_ceiling_result", json.dumps({"ceiling_id": cei["ceiling_id"]}, sort_keys=True)), set())
                    err = est if certified else max(est, self.t2)
                    want = "factible" if g - err >= EPS else ("infactible" if g + err <= -EPS else "inconcluso")
                    self.need(r["verdict"] == want, "confrontation_result", cid, "veredicto §17 inconsistente con G y error")
                self.need(mac["admissible"] and cell["instrument_available"], "confrontation_result", cid,
                          "complete con macro inadmisible o instrumento no disponible")
            else:
                self.need(r["verdict"] == "no_verdict" and r["run_readiness_flag"] is False and r["G"] is None,
                          "confrontation_result", cid, "no completo exige no_verdict, readiness=false y G null")
                self.need(r["reason_code"], "confrontation_result", cid, "no completo sin motivo")
            self.need(r["run_readiness_flag"] is False, "confrontation_result", cid, "readiness sin D8_pre PASS")

    # ----------------------------------------------------------------------------- inversiones
    def inversions(self):
        roots = Counter((r["cell_id"], r["inversion_id"]) for r in self.t["scalar_inversion_roots"])
        ints = defaultdict(list)
        for r in self.t["scalar_inversion_intervals"]:
            ints[(r["cell_id"], r["inversion_id"])].append(r)
        targets = self.by["inversion_targets"]
        for r in self.t["inversion_result"]:
            pk = (r["cell_id"], r["inversion_id"])
            iid = r["inversion_id"]
            self.need(iid in VALUE_FIELD, "inversion_result", pk, "inversion_id")
            if iid not in VALUE_FIELD:
                continue
            for iid2, f in VALUE_FIELD.items():
                if iid2 != iid:
                    self.need(r[f] is None, "inversion_result", pk, "campo de valor ajeno no nulo: " + f)
            endo = iid in ENDOGENOUS
            self.need(r["method_id"] == ("fixed_point_bracket_bisection" if endo else "algebraic_closed_form"), "inversion_result", pk,
                      "método")
            self.need(INV_STATUS.get(r["result_status"]) == r["computation_status"], "inversion_result", pk, "mapeo de estados")
            self.need(r["no_solution"] == (r["result_status"] == "no_feasible_solution") or not r["no_solution"],
                      "inversion_result", pk, "no_solution solo con no_feasible_solution")
            self.need(not r["outside_support"] or r["result_status"] == "outside_support", "inversion_result", pk,
                      "outside_support solo con ese estado")
            if not endo:
                self.need(r["fixed_point_converged"] is None and r["n_scalar_solutions"] is None and r["n_scalar_intervals"] is None,
                          "inversion_result", pk, "algebraica con campos de punto fijo")
                self.need(roots[pk] == 0 and not ints.get(pk), "scalar_inversion_roots", pk, "hijos de inversión algebraica")
            elif r["computation_status"] == "complete":
                self.need(r["n_scalar_solutions"] == roots[pk] and r["n_scalar_intervals"] == len(ints.get(pk, [])), "inversion_result",
                          pk, "conteos distintos de tablas hijas")
                ev = self.pass_evidence.get(("inversion_result", json.dumps({"cell_id": pk[0], "inversion_id": pk[1]}, sort_keys=True)), set())
                self.need(bool(ev & {"certified_root_search", "invariance_proof"}), "inversion_result", pk,
                          "endógena 'complete' sin cobertura certificada de la búsqueda")
                self.need(r["fixed_point_converged"] is True, "inversion_result", pk, "endógena completa sin convergencia por residuo")
                one = roots[pk] == 1 and not ints.get(pk)
                self.need((r[VALUE_FIELD[iid]] is not None) <= one, "inversion_result", pk, "valor resumen sin raíz única aislada")
                if r[VALUE_FIELD[iid]] is not None:
                    self.need(0 <= D(r[VALUE_FIELD[iid]]) <= 1, "inversion_result", pk, "valor endógeno fuera de [0,1]")
            else:
                self.need(r["n_scalar_solutions"] is None and r[VALUE_FIELD[iid]] is None, "inversion_result", pk,
                          "endógena no completa con valores")
                self.need(roots[pk] == 0 and not ints.get(pk), "scalar_inversion_roots", pk,
                          "hallazgos de una búsqueda incompleta publicados como raíces")
            if r["result_status"] in ("not_identified", "undefined_denominator", "failed", "incomplete") and not endo:
                if iid in ("capture_required",):
                    pass
            if iid == "phi_partial" and r["result_status"] in ("computed", "outside_support"):
                t = targets.get(pk)
                self.need(t is not None and t["tau_f_given"] is not None and 0 < D(t["tau_f_given"]) < 1 and
                          t["supplier_share_target"] is not None, "inversion_result", pk, "phi_partial sin objetivos declarados")
            if r["result_status"] not in ("computed", "outside_support", "no_feasible_solution"):
                self.need(r["reason_code"], "inversion_result", pk, "estado no calculado sin motivo")
        for r in self.t["scalar_inversion_roots"]:
            k = (r["cell_id"], r["inversion_id"])
            self.need(r["inversion_id"] in ENDOGENOUS, "scalar_inversion_roots", k, "solo endógenas")
            self.need(r["converged"] is True and D(r["residual"]) <= self.tol_root, "scalar_inversion_roots", k,
                      "raíz con residuo sobre la tolerancia o no convergida (un salto no es raíz)")
        for pk, rows in ints.items():
            rows = sorted(rows, key=lambda x: x["interval_index"])
            self.need([x["interval_index"] for x in rows] == list(range(len(rows))), "scalar_inversion_intervals", pk, "índices")
            for a in rows:
                self.need(D(a["lower"]) < D(a["upper"]), "scalar_inversion_intervals", pk, "lower<upper")
            for a, b in zip(rows, rows[1:]):
                self.need(D(a["upper"]) < D(b["lower"]), "scalar_inversion_intervals", pk, "intervalos no disjuntos/ordenados")
            ev = [e for e in self.t["numerical_evidence"] if e["result_table"] == "inversion_result"
                  and e["record_pk"] == {"cell_id": pk[0], "inversion_id": pk[1]} and e["status"] == "pass"]
            self.need(bool(ev), "scalar_inversion_intervals", pk, "intervalo sin demostración registrada")

    # ----------------------------------------------------------------------------- geometría
    def geometry(self):
        comps = defaultdict(list)
        for c in self.t["r1_components"]:
            comps[c["cell_id"]].append(c)
            self.need(c["topology_kind"] in ("closed_loop", "open_arc", "branched", "isolated_point"), "r1_components",
                      (c["cell_id"], c["component_id"]), "topology_kind")
            self.need(not c["closed_curve"] or c["topology_kind"] == "closed_loop", "r1_components",
                      (c["cell_id"], c["component_id"]), "closed_curve sin closed_loop")
        verts = {}
        for v in self.t["r1_vertices"]:
            verts[(v["cell_id"], v["component_id"], v["vertex_id"])] = v
            self.need(not v["is_boundary"] or v["boundary_label"], "r1_vertices", (v["cell_id"], v["vertex_id"]), "borde sin etiqueta")
        for e in self.t["r1_edges"]:
            a = verts.get((e["cell_id"], e["component_id"], e["from_vertex_id"]))
            b = verts.get((e["cell_id"], e["component_id"], e["to_vertex_id"]))
            self.need(a is not None and b is not None, "r1_edges", (e["cell_id"], e["edge_id"]), "arista con vértices ausentes en su componente")
            if a is not None and b is not None:
                joint = a["is_boundary"] or b["is_boundary"] or a["branch_id"] == e["branch_id"] or b["branch_id"] == e["branch_id"]
                self.need(joint, "r1_edges", (e["cell_id"], e["edge_id"]), "arista entre ramas sin punto de unión")
        conv = {r["quantity_id"][3:]: r for r in self.t.get("convergence_result", []) if r["quantity_id"].startswith("R1:")}
        vres = defaultdict(list)
        for v in self.t["r1_vertices"]:
            vres[v["cell_id"]].append(D(v["residual"]))
        egeo = defaultdict(list)
        for e in self.t["r1_edges"]:
            # max_residual de una arista es |f| a lo largo de la CUERDA entre vértices (diagnóstico geométrico), no el
            # residuo de una raíz: la garantía de la arista es su cota geométrica
            egeo[e["cell_id"]].append(D(e["geometric_error_bound"]))
        for s in self.t["r1_summary"]:
            cid = s["cell_id"]
            if s["computation_status"] == "complete":
                self.need(s["n_components"] is not None and s["n_components"] == len(comps[cid]), "r1_summary", cid,
                          "n_components distinto de componentes")
                ev = self.pass_evidence.get(("r1_summary", json.dumps({"cell_id": cid}, sort_keys=True)), set())
                self.need("certified_contour" in ev, "r1_summary", cid, "R1 'complete' sin cobertura certificada")
                self.need(not s["no_solution"] or s["n_components"] == 0, "r1_summary", cid, "no_solution con componentes")
                # cobertura no es precisión: 'complete' exige además la cota geométrica y los residuos DEMOSTRADOS dentro de
                # sus tolerancias (la geométrica viaja en la fila de convergencia de R1; la de residuo es T_root_residual)
                cv = conv.get(cid)
                gb = D(s["geometry_error_bound"])
                ok_cv = (cv is not None and cv["status"] == "pass" and cv["tolerance"] is not None and gb is not None
                         and D(cv["change_bound"]) == gb and gb <= D(cv["tolerance"]))
                self.need(ok_cv, "r1_summary", cid, "R1 'complete' sin cota geométrica demostrada dentro de tolerancia")
                self.need(s["residual_bound"] is not None and D(s["residual_bound"]) <= self.tol_root, "r1_summary", cid,
                          "R1 'complete' con residuo sobre la tolerancia")
                self.need(all(r <= self.tol_root for r in vres[cid]), "r1_vertices", cid,
                          "vértice de R1 completo con residuo sobre la tolerancia")
                tol_g = D(cv["tolerance"]) if cv is not None and cv["tolerance"] is not None else None
                self.need(all(tol_g is not None and g <= tol_g for g in egeo[cid]), "r1_edges", cid,
                          "arista de R1 completo con cota geométrica sobre la tolerancia")
            else:
                self.need(s["n_components"] is None and not s["no_solution"] and s["reason_code"], "r1_summary", cid,
                          "incompleto declara cero o sin motivo")
        secs = defaultdict(list)
        roots = defaultdict(list)
        for r in self.t["r2_roots"]:
            roots[(r["cell_id"], r["section_id"])].append(r)
            self.need(r["root_type"] in ("crossing", "tangent", "boundary"), "r2_roots", (r["cell_id"], r["section_id"]), "root_type")
        for s in self.t["r2_sections"]:
            secs[s["cell_id"]].append(s["section_id"])
            pk = (s["cell_id"], s["section_id"])
            rs = sorted(roots[pk], key=lambda r: r["root_index"])
            if s["computation_status"] == "complete":
                self.need(s["n_roots_by_section"] == len(rs), "r2_sections", pk, "conteo de raíces")
                ev = self.pass_evidence.get(("r2_sections", json.dumps({"cell_id": pk[0], "section_id": pk[1]}, sort_keys=True)), set())
                self.need(bool(ev & {"certified_root_search", "certified_empty_by_C2_bound"}), "r2_sections", pk,
                          "R2 'complete' sin cobertura certificada")
                for r in rs:
                    self.need(D(r["residual"]) <= self.tol_root, "r2_roots", pk, "raíz R2 con residuo sobre la tolerancia")
                self.need([r["root_index"] for r in rs] == list(range(len(rs))), "r2_roots", pk, "índices consecutivos")
                self.need(s["n_tangential_roots"] == sum(1 for r in rs if r["root_type"] == "tangent"), "r2_sections", pk,
                          "conteo de tangencias")
                if s["section_id"] == "tau_d_estatutario":
                    rate = self.d7.rates.get(self.by["cell_context"][(s["cell_id"],)]["country_id"])
                    self.need(s["rate_input_id"] is not None and rate is not None and rate["status"] == "verified", "r2_sections", pk,
                              "estatutario completo sin tasa verificada")
            else:
                self.need(s["n_roots_by_section"] is None and s["n_tangential_roots"] is None and not rs, "r2_sections", pk,
                          "incompleto con conteos")
                self.need(s["reason_code"], "r2_sections", pk, "incompleto sin motivo")
        for cid, ss in secs.items():
            self.need(sorted(ss) == sorted(["tau_f_0", "tau_d_0", "paridad", "tau_d_estatutario"]), "r2_sections", cid,
                      "exactamente 4 secciones")

    # ----------------------------------------------------------------------------- afirmaciones y robustez
    def claims(self):
        claims = self.by["claims"]
        for c in self.t["claims"]:
            k = c["claim_id"]
            sc = c["claim_scope"]
            self.need(sc in ("global", "country", "country_instrument"), "claims", k, "claim_scope")
            self.need((sc != "global") or (c["country_id"] is None and c["instrument_j"] is None), "claims", k, "global con país")
            self.need((sc != "country") or c["country_id"] is not None, "claims", k, "country sin país")
            self.need((sc != "country_instrument") or (c["country_id"] is not None and c["instrument_j"] is not None), "claims", k,
                      "country_instrument incompleto")
            self.need(c["baseline_status"] in ("verified", "inconclusive", "not_evaluated"), "claims", k, "baseline_status")
            self.need(D(c["epsilon_econ"]) == EPS, "claims", k, "epsilon_econ")
        for b in self.t["support_breakdown_result"]:
            k = b["breakdown_id"]
            st = b["status"]
            self.need(st in BRK_STATUS and BRK_STATUS[st] == b["computation_status"], "support_breakdown_result", k, "estado/cómputo")
            self.need(b["block_id"] in ("incidencia_laboral", "cuna_tributaria", "tecnologia", "cobertura_residual"),
                      "support_breakdown_result", k, "block_id")
            self.need(b["domain_edge_reached"] in EDGES, "support_breakdown_result", k, "domain_edge_reached")
            self.need(b["boundary_kind"] in ("theoretical", "admissibility", "epistemic", "none"), "support_breakdown_result", k,
                      "boundary_kind")
            self.need(b["scale_kind"] in ("aritmetica", "logaritmica", "escalera_discreta"), "support_breakdown_result", k, "scale_kind")
            if st == "breakdown_found":
                self.need(b["r_critical"] is not None and D(b["r_critical"]) >= 1 and b["witness_set_id"] and
                          (b["n_components"] or 0) >= 1, "support_breakdown_result", k, "quiebre sin r>=1, testigos o componentes")
            else:
                self.need(b["r_critical"] is None, "support_breakdown_result", k, "r_critical fuera de quiebre")
            if st == "theoretical_boundary_no_breakdown":
                self.need(b["boundary_kind"] == "theoretical" and b["reason_code"] and b["boundary_value"] is not None,
                          "support_breakdown_result", k, "frontera teórica incompleta")
            if b["computation_status"] in ("failed", "incomplete", "excluded"):
                self.need(b["reason_code"], "support_breakdown_result", k, "fallo sin motivo")
            if st in ("domain_exhausted_no_breakdown", "declared_ladder_exhausted_no_breakdown",
                      "theoretical_boundary_no_breakdown", "admissibility_boundary_no_breakdown"):
                cl = claims.get((b["claim_id"],))
                self.need(cl is not None and cl["baseline_status"] == "verified", "support_breakdown_result", k,
                          "agotamiento sin baseline verificado")
            self.need(b["component_id"] is None or (b["parameter_id"] or "").startswith("pi_"), "support_breakdown_result", k,
                      "component_id fuera de pi individual")
            if b["joint_breakdown"]:
                self.need(b["omega_id"] is None, "support_breakdown_result", k, "conjunto con omega")
            if b["block_id"] == "cobertura_residual":
                self.need(st == "not_applicable_not_identified" and b["reason_code"] == "MOMENT_NOT_IDENTIFIED" and
                          b["witness_set_id"] is None, "support_breakdown_result", k, "chi_r sin momento identificado")
        for q in self.t["external_requirement_sensitivity_result"]:
            k = q["sensitivity_id"]
            st = q["status"]
            self.need(st in QS_STATUS and QS_STATUS[st] == q["computation_status"], "external_requirement_sensitivity_result", k,
                      "estado/cómputo")
            if st == "breakdown_found":
                self.need(q["m_Q_critical"] is not None and q["witness_set_id"] and
                          abs(D(q["reduction_from_reported"]) - (1 - D(q["m_Q_critical"]))) <= T1,
                          "external_requirement_sensitivity_result", k, "quiebre sin m_Q/reducción/testigos")
            else:
                self.need(q["m_Q_critical"] is None and q["reduction_from_reported"] is None,
                          "external_requirement_sensitivity_result", k, "m_Q fuera de quiebre")
            self.need((q["scale_scope"] == "country") == (q["scale_country_id"] is not None),
                      "external_requirement_sensitivity_result", k, "scale_country_id")
            cl = claims.get((q["claim_id"],))
            self.need(cl is not None and cl["claim_scope"] == q["claim_scope"], "external_requirement_sensitivity_result", k,
                      "claim_scope distinto del claim")
            self.need(q["country_id"] is not None or q["claim_scope"] == "global", "external_requirement_sensitivity_result", k,
                      "país null fuera de global")
            if q["computation_status"] in ("failed", "incomplete"):
                self.need(q["reason_code"], "external_requirement_sensitivity_result", k, "fallo sin motivo")

    # ----------------------------------------------------------------------------- convergencia, cobertura, evidencia
    def audit(self):
        for r in self.t["convergence_result"]:
            k = (r["quantity_id"], r["level_before"], r["level_after"])
            self.need(r["status"] in ("pass", "fail", "incomplete"), "convergence_result", k, "status")
            if r["status"] == "pass":
                # INTEGRACIÓN 3.7: un pass sin cota numérica se REPORTA (antes D(None) rompía la auditoría)
                cb_ok = isinstance(r["change_bound"], (int, float, str)) and not isinstance(r["change_bound"], bool)
                self.need(cb_ok, "convergence_result", k, "pass sin change_bound")
                self.need(cb_ok and r["coverage_complete"] and D(r["change_bound"]) <= D(r["tolerance"]) and r["verdict_changes"] == 0 and
                          r["topology_before"] == r["topology_after"], "convergence_result", k, "pass sin condiciones")
            self.need(self.resolve(r["result_ref"]), "convergence_result", k, "result_ref no resuelve una fila B")
        for c in self.t["computation_coverage"]:
            k = c["work_unit_id"]
            self.need(c["coverage_kind"] in ("evaluated", "certified_pruned", "pending"), "computation_coverage", k, "coverage_kind")
            self.need(c["status"] in ("complete", "incomplete", "failed"), "computation_coverage", k, "status")
            self.need(c["coverage_kind"] != "pending" or c["status"] != "complete", "computation_coverage", k, "pending completo")
            if c["coverage_kind"] == "certified_pruned":
                e = self.by["numerical_evidence"].get((c["evidence_ref"],))
                self.need(e is not None and e["kind"] == "pruning" and e["status"] == "pass" and e["error_bound"] is not None,
                          "computation_coverage", k, "poda sin evidencia")
        for w in self.t["witness_sets"]:
            self.need(w["scope"] in ("support_breakdown", "external_requirement", "scalar_inversion"), "witness_sets",
                      w["witness_set_id"], "scope")
        for e in self.t["numerical_evidence"]:
            k = e["evidence_ref"]
            self.need(e["kind"] in ("regime", "convergence", "pruning", "limit", "coverage", "root"), "numerical_evidence", k, "kind")
            if e["result_table"] is None:
                self.need(e["record_pk"] == {}, "numerical_evidence", k, "sin tabla exige record_pk vacío")
            else:
                pk = self.C.C["tables"][e["result_table"]]["primary_key"] if e["result_table"] in self.C.C["tables"] else None
                self.need(pk is not None and set(e["record_pk"]) == set(pk) and
                          tuple(e["record_pk"][x] for x in pk) in self.by.get(e["result_table"], {}), "numerical_evidence", k,
                          "record_pk no resuelve")

    def resolve(self, ref: str) -> bool:
        try:
            table, pk = ref.split(":", 1)
            pk = json.loads(pk)
            cols = self.C.C["tables"][table]["primary_key"]
            return set(pk) == set(cols) and tuple(pk[c] for c in cols) in self.by.get(table, {})
        except Exception:  # noqa: BLE001
            return False

    def run(self) -> list:
        for step in (self.omega, self.frontier, self.frontier_result, self.ceilings, self.macro, self.confrontation,
                     self.inversions, self.geometry, self.claims, self.audit):
            step()
        return self.errors


def check_b(tables: dict, contracts, d7, **kw) -> list:
    return Checker(tables, contracts, d7, **kw).run()


# ---------------------------------------------------------------------------------------------------------------------
# CANDIDATO PASO 4 E12 (VALIDACION PAQUETE 3.7, NO OFICIAL; copia aislada): reglas de PRESENCIA, cardinalidad, unicidad,
# relaciones y no aplicabilidad justificada de los productos de UNA celda, derivadas de Run.cell/inversions/geometry.
# Código idéntico a codigo/completitud_e12.py (la prueba de puntos candidatos comprueba la igualdad de resultados).
# El CONTENIDO de las evidencias (que exige autoridad y configuración) se verifica en E14 (herramientas/s3/validadores/core.py).
from collections import Counter

ESTADOS_NUCLEO = {"complete", "not_applicable", "incomplete", "failed", "excluded"}
DEFECTUOSOS = {"ausente", "duplicada", "estado_nulo", "estado_desconocido", "no_aplicable_injustificada", "relacion_rota",
               "evidencia_ausente", "id_inesperado"}


def e12_contrato():
    from . import inversion as INV
    from . import sections as R2M
    return {"inversiones": tuple(sorted(INV.INVERSIONS)), "status_to_computation": dict(INV.STATUS_TO_COMPUTATION),
            # método por inversión según el núcleo: phi_partial usa el método por defecto (algebraic_closed_form);
            # external_factor y phi_total, fixed_point_bracket_bisection (run.py, inversion.py)
            "algebraicas": ("capture_required", "gain_required", "lambda_required", "phi_partial"), "secciones": tuple(R2M.SECTIONS),
            "path": R2M._path}


def _e12_filas(rows, tabla, **k):
    return [x for x in rows.get(tabla, []) if all(x.get(a) == b for a, b in k.items())]


def e12_verificar_celda(rows: dict, cid: str, fid: str, *, instrumento: str, barras: tuple, tasa: float | None,
                    run_geometry: bool = True, con_unidad: bool = True, omega_id: str | None = None) -> dict:
    C = e12_contrato()
    partes, motivos = {}, []

    def parte(nombre, estado, motivo=None):
        partes[nombre] = {"estado": estado, "motivo": motivo}
        if estado in DEFECTUOSOS or estado == "incompleta":
            motivos.append("%s: %s%s" % (nombre, estado, (" (" + motivo + ")") if motivo else ""))

    def unica(tabla, nombre, **k):
        fs = _e12_filas(rows, tabla, **k)
        if not fs:
            parte(nombre, "ausente", "%s sin fila para %s" % (tabla, k))
            return None
        if len(fs) > 1:
            parte(nombre, "duplicada", "%d filas %s para %s" % (len(fs), tabla, k))
            return None
        return fs[0]

    def estado_de(nombre, f, justificaciones=None):
        st = f.get("computation_status")
        if st is None:
            parte(nombre, "estado_nulo", "computation_status ausente o nulo")
        elif st not in ESTADOS_NUCLEO:
            parte(nombre, "estado_desconocido", repr(st))
        elif st == "complete":
            parte(nombre, "completa")
        elif st == "not_applicable":
            ok = justificaciones is not None and f.get("reason_code") in justificaciones
            parte(nombre, "no_aplicable_justificada" if ok else "no_aplicable_injustificada", f.get("reason_code"))
        else:
            parte(nombre, "incompleta", "%s: %s" % (st, f.get("reason_code")))

    # ---- contexto de la celda
    cx = unica("cell_context", "contexto", cell_id=cid)
    if cx is not None:
        if omega_id is not None and cx.get("omega_id") != omega_id:
            parte("contexto", "relacion_rota", "omega_id del contexto distinto del de la celda")
        else:
            parte("contexto", "completa")
    # ---- techo
    frc = unica("frontier_context", "frontera", frontier_id=fid)
    if frc is not None:
        parte("frontera", "completa")
    ce = unica("capture_ceiling_result", "techo", frontier_id=fid)
    if ce is not None:
        if ce.get("ceiling_id") != "CEI:" + fid[4:]:
            parte("techo", "relacion_rota", "ceiling_id no deriva del frontier_id")
        else:
            estado_de("techo", ce, {"INSTRUMENT_NOT_AVAILABLE"})
    # ---- confrontación, macro y evidencia de G
    cf = unica("confrontation_result", "confrontacion", cell_id=cid)
    if cf is not None:
        if ce is not None and cf.get("ceiling_id") != ce.get("ceiling_id"):
            parte("confrontacion", "relacion_rota", "ceiling_id de la confrontación distinto del techo de la celda")
        else:
            estado_de("confrontacion", cf, {"INSTRUMENT_NOT_AVAILABLE"})
        mac = _e12_filas(rows, "lambda_pi_envelope", macro_id=cf.get("macro_id"))
        if len(mac) != 1:
            parte("macro", "ausente" if not mac else "duplicada", "%d filas lambda_pi_envelope con macro_id %s" % (len(mac), cf.get("macro_id")))
        else:
            parte("macro", "completa" if mac[0].get("computation_status") == "complete" else "incompleta", mac[0].get("reason_code"))
        g = _e12_filas(rows, "convergence_result", quantity_id="G:" + cid)
        parte("evidencia_G", "completa" if len(g) == 1 else ("evidencia_ausente" if not g else "duplicada"),
              None if len(g) == 1 else "%d filas G:%s" % (len(g), cid))
    # ---- inversiones
    inv = _e12_filas(rows, "inversion_result", cell_id=cid)
    cnt = Counter(x.get("inversion_id") for x in inv)
    for k in sorted(set(cnt) - set(C["inversiones"]), key=str):
        parte("inversion:%s" % k, "id_inesperado", "inversion_id fuera de paper2b.inversion.INVERSIONS")
    for iid in C["inversiones"]:
        nombre = "inversion:" + iid
        fs = [x for x in inv if x.get("inversion_id") == iid]
        if not fs:
            parte(nombre, "ausente", "sin fila inversion_result")
            continue
        if len(fs) > 1:
            parte(nombre, "duplicada", "%d filas" % len(fs))
            continue
        f = fs[0]
        rs, st = f.get("result_status"), f.get("computation_status")
        if rs is None or st is None:
            parte(nombre, "estado_nulo", "result_status o computation_status nulo")
            continue
        metodo = "algebraic_closed_form" if iid in C["algebraicas"] else "fixed_point_bracket_bisection"
        if f.get("method_id") != metodo:
            parte(nombre, "relacion_rota", "method_id %r distinto del del núcleo (%s)" % (f.get("method_id"), metodo))
            continue
        if C["status_to_computation"].get(rs) != st:
            parte(nombre, "relacion_rota", "computation_status %s no corresponde a result_status %s" % (st, rs))
            continue
        if iid not in C["algebraicas"] and rs not in ("not_identified", "undefined_denominator"):
            ev = _e12_filas(rows, "convergence_result", quantity_id="INV:%s:%s" % (cid, iid))
            if len(ev) != 1:
                parte(nombre, "evidencia_ausente" if not ev else "duplicada", "%d filas INV:%s:%s" % (len(ev), cid, iid))
                continue
        if con_unidad and iid in ("lambda_required", "capture_required") and rs in ("computed", "outside_support") and "_fin" not in f:
            parte(nombre, "evidencia_ausente", "falta _fin (cierre de soporte global al ensamblar)")
            continue
        # not_applicable del núcleo = not_identified con motivo (p. ej. TARGETS_NOT_PREDECLARED)
        estado_de(nombre, f, {f.get("reason_code")} if (rs == "not_identified" and f.get("reason_code")) else set())
    if not run_geometry:
        return _e12_cierre(partes, motivos)
    # ---- R1
    r1 = unica("r1_summary", "r1", cell_id=cid)
    if r1 is not None:
        st = r1.get("computation_status")
        if st == "complete":
            comps = _e12_filas(rows, "r1_components", cell_id=cid)
            ids = Counter(x.get("component_id") for x in comps)
            ev = _e12_filas(rows, "convergence_result", quantity_id="R1:" + cid)
            if r1.get("n_components") is None or r1.get("n_components") != len(comps) or any(n > 1 for n in ids.values()):
                parte("r1", "relacion_rota", "n_components %r frente a %d componentes (%s)" % (r1.get("n_components"), len(comps), dict(ids)))
            elif any(not _e12_filas(rows, "r1_vertices", cell_id=cid, component_id=k) for k in ids):
                parte("r1", "evidencia_ausente", "componente sin vértices")
            elif any(len(_e12_filas(rows, "r1_vertices", cell_id=cid, component_id=k)) >= 2 and not _e12_filas(rows, "r1_edges", cell_id=cid, component_id=k) for k in ids):
                # contour.py: una componente-CURVA (>= 2 vértices) lleva aristas; en menús 1-D (d, f) la componente es un
                # PUNTO (1 vértice, side = point, arc_length 0) sin aristas, y es válida
                parte("r1", "evidencia_ausente", "componente-curva sin aristas")
            elif len(ev) != 1:
                parte("r1", "evidencia_ausente" if not ev else "duplicada", "%d filas R1:%s" % (len(ev), cid))
            else:
                parte("r1", "completa")
        else:
            estado_de("r1", r1, set())
    # ---- R2
    sec = _e12_filas(rows, "r2_sections", cell_id=cid)
    cnt = Counter(x.get("section_id") for x in sec)
    for k in sorted(set(cnt) - set(C["secciones"]), key=str):
        parte("r2:%s" % k, "id_inesperado", "section_id fuera de paper2b.sections.SECTIONS")
    for sid in C["secciones"]:
        nombre = "r2:" + sid
        fs = [x for x in sec if x.get("section_id") == sid]
        if not fs:
            parte(nombre, "ausente", "sin fila r2_sections")
            continue
        if len(fs) > 1:
            parte(nombre, "duplicada", "%d filas" % len(fs))
            continue
        f = fs[0]
        st = f.get("computation_status")
        if st == "not_applicable":
            fuera = C["path"](sid, instrumento, barras[0], barras[1], tasa) is None
            ok = f.get("reason_code") == "SECTION_OUTSIDE_MENU" and fuera
            parte(nombre, "no_aplicable_justificada" if ok else "no_aplicable_injustificada",
                  "%s; trayectoria %s del menú" % (f.get("reason_code"), "fuera" if fuera else "DENTRO"))
        elif st == "complete":
            roots = _e12_filas(rows, "r2_roots", cell_id=cid, section_id=sid)
            idx = Counter(x.get("root_index") for x in roots)
            if f.get("n_roots_by_section") is None or f.get("n_roots_by_section") != len(roots) or any(n > 1 for n in idx.values()):
                parte(nombre, "relacion_rota", "n_roots_by_section %r frente a %d raíces" % (f.get("n_roots_by_section"), len(roots)))
            else:
                parte(nombre, "completa")
        else:
            estado_de(nombre, f, set())
    return _e12_cierre(partes, motivos)


def _e12_cierre(partes, motivos):
    est = [p["estado"] for p in partes.values()]
    if any(e in DEFECTUOSOS for e in est):
        estado = "invalida"
    elif any(e == "incompleta" for e in est):
        estado = "incompleta"
    else:
        estado = "completa"
    return {"estado": estado, "partes": partes, "motivos": motivos, "n_partes": len(partes)}


def e12_filas_de_celda(rows: dict, cid: str, fid: str) -> dict:
    """Todas las filas que E12 exige o cita para la celda (para exportar y re-verificar fuera del proceso)."""
    out = {}
    cf = [x for x in rows.get("confrontation_result", []) if x.get("cell_id") == cid]
    macro_ids = {x.get("macro_id") for x in cf}
    for t in ("cell_context", "confrontation_result", "inversion_result", "r1_summary", "r1_components", "r1_vertices", "r1_edges",
              "r1_rejected_crossings", "r2_sections", "r2_roots"):
        out[t] = [x for x in rows.get(t, []) if x.get("cell_id") == cid]
    out["frontier_context"] = [x for x in rows.get("frontier_context", []) if x.get("frontier_id") == fid]
    out["capture_ceiling_result"] = [x for x in rows.get("capture_ceiling_result", []) if x.get("frontier_id") == fid]
    out["lambda_pi_envelope"] = [x for x in rows.get("lambda_pi_envelope", []) if x.get("macro_id") in macro_ids]
    q = {"G:" + cid, "R1:" + cid} | {"INV:%s:%s" % (cid, i) for i in e12_contrato()["inversiones"]}
    out["convergence_result"] = [x for x in rows.get("convergence_result", []) if x.get("quantity_id") in q]
    return out
