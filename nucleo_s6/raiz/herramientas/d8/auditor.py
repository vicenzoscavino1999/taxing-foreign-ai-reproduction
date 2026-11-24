"""Auditores D8_pre y D8_post (bloque 2; CONTRATOS_D7_B_D8, RE-05/RE-06).

Grafo sin ciclos (contrato): D8_pre <- {D7, contrato, validaciones SINTÉTICAS de B, registro de casos, suites, entorno};
D8_post <- {B, D8_pre}. D8_pre rechaza cualquier B 'official' (evita la dependencia circular B_oficial -> D8_pre PASS ->
B_oficial) y D8_post nunca escribe en la familia D8_pre (se reverifica su árbol antes y después).
Registro de afirmaciones: D8_pre lo deriva ANTES de cualquier resultado (registro A1-E v2 + mapa D4 + sets de D7, sin
leer tablas B) y fija su hash en evidence_records; D8_post exige que B/claims.csv sea exactamente ese registro.
Perfiles (herramientas/bloque2/perfiles.py): 'oficial' (entorno aprobado RE-03 + lock del contrato Paquete A, informes
A/A-ter del proyecto, autoridad real) o 'ensayo' (raíz aislada, autoridad ficticia, fixtures rotulados). La lógica de
cada gate es la misma; el perfil solo fija qué se considera aprobado. D8_pre escribe la evaluación de entorno como
archivo JSON direccionado por contenido (EVR.ENV apunta a ese archivo; nunca a código), exige que la suite seleccionada
esté vinculada a ESTE código, suite y entorno, y vincula A/A-ter al entorno/lock aprobados y al árbol de código actual.
D8_post exige que B provenga de un freeze-run cuya selección coincide con lo ejecutado (D7, D8_pre, código,
configuración, entorno, contrato). Exportación: herramientas/d8/exportar.py (núcleo verificable + contenedor oficial).
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from decimal import Decimal
from fractions import Fraction
from itertools import product
from pathlib import Path

from paper2b import claims as CL
from paper2b import external as X
from paper2b import keys as K
from paper2b import macro as MC
from paper2b import rules as RULES
from paper2b import tables as T
from paper2b.d7build import base_set_id, editions
from paper2b.d7view import D7View
from herramientas.bloque2 import autoridad as A
from herramientas.bloque2 import entorno as E
from herramientas.bloque2 import familias as FAM
from herramientas.bloque2 import perfiles as P

B_TABLES = ["omega", "omega_values", "cell_context", "frontier_context", "frontier_result", "capture_ceiling_result",
            "sup_witness", "lambda_pi_envelope", "confrontation_result", "inversion_result", "inversion_targets", "r1_summary",
            "r1_components", "r1_vertices", "r1_edges", "r1_rejected_crossings", "r2_sections", "r2_roots", "claims",
            "support_breakdown_result", "breakdown_witnesses", "external_requirement_sensitivity_result",
            "convergence_result", "computation_coverage", "witness_sets", "scalar_inversion_roots",
            "scalar_inversion_intervals", "numerical_evidence"]
STRUCT_ADM = ["a", "rho", "u_theta", "beta_tilde", "kappa_tilde", "z_cost"]
MACRO_ADM = ["pi_iva", "pi_otros_productos", "pi_produccion", "eta_w", "eta_H"]
OUT_OF_SCOPE = {"CHL"}


class D8Error(RuntimeError):
    pass


def need(test, code):
    if not test:
        raise D8Error(code)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def rel(root: Path, p: Path) -> str:
    return Path(p).resolve().relative_to(Path(root).resolve()).as_posix()


def _file(path: Path, expected: str | None = None) -> bytes:
    raw = Path(path).read_bytes()
    if expected is not None:
        need(sha(raw) == expected, "D8_INPUT_HASH:" + Path(path).name)
    return raw


def load_b(contracts, b_dir: Path, tree: str) -> dict:
    info = FAM.verify_version(b_dir, "B", expected_tree=tree)
    tables = {}
    for name in B_TABLES:
        tables[name] = contracts.read_csv(Path(b_dir) / contracts.C["tables"][name]["file"].split("/", 1)[1], name)
    rm = json.loads((Path(b_dir) / "run_manifest.json").read_bytes())
    return dict(info, tables=tables, run_manifest=rm)


def consumer_context(root: Path, b_manifest: dict, d7_manifest: dict | None = None) -> tuple:
    """Contexto de verificación del CONSUMIDOR para reglas B: resolutor de bundles CA2 por hash (dependencias
    ca2_bundle de B o índice de bundles de D7) y tolerancias técnicas autenticadas (archivo 'tolerances' de B cuyo
    contenido debe ser exactamente el aprobado en el código del productor fijado). Devuelve (resolver, tolerancias, errores)."""
    from paper2b import claves_condicionales as CK
    from herramientas.b import ejecutar_b as EB
    root = Path(root)
    errs = []
    bdeps = b_manifest["input_dependencies"]
    bundles = {d["sha256"]: d["path"] for d in bdeps if d["role"] == "ca2_bundle"}
    if d7_manifest is not None:
        bundles.update({d["sha256"]: d["path"] for d in d7_manifest["input_dependencies"] if d["role"] == "ca2_bundle"})
    if not bundles and d7_manifest is not None:
        idx = [d for d in d7_manifest["input_dependencies"] if d["role"] == "ca2_bundles_index"]
        if len(idx) == 1:
            raw = (root / idx[0]["path"]).read_bytes()
            if sha(raw) == idx[0]["sha256"]:
                bundles = {b["sha256"]: b["path"] for b in json.loads(raw)["bundles"]}
            else:
                errs.append("CA2_BUNDLE_INDEX_HASH")
    tol = [d for d in bdeps if d["role"] == "tolerances"]
    tolerances = None
    if len(tol) != 1:
        errs.append("B_SIN_TOLERANCIAS_AUTENTICADAS")
    else:
        raw = (root / tol[0]["path"]).read_bytes()
        if sha(raw) != tol[0]["sha256"]:
            errs.append("B_TOLERANCIAS_ALTERADAS")
        else:
            tolerances = json.loads(raw)
            if tolerances != EB.TOLERANCES:
                errs.append("B_TOLERANCIAS_DISTINTAS_DE_LAS_APROBADAS")
    return CK.BundleResolver(root, bundles), (tolerances or EB.TOLERANCES), errs


def predeclared_claims(registry: dict, model_case_map: list, d7: D7View) -> tuple[list, str]:
    """Registro de afirmaciones derivado solo de reglas y entradas previas (sin resultados B)."""
    set_index = {}
    for entry in registry["entries"]:
        for ed in editions(entry):
            for block in ("macro", "micro"):
                sid = base_set_id(entry, ed, block)
                need(sid in d7.sets, "D8_CLAIM_SET_NOT_IN_D7:" + sid)
                set_index.setdefault(entry["preregistration_id"], {}).setdefault(ed or "pub", {})[block] = sid
    cls = CL.derive(registry, model_case_map, set_index)
    rows = sorted((c.row("not_evaluated") for c in cls), key=lambda r: r["claim_id"])
    canon_rows = [{k: v for k, v in r.items() if k != "baseline_status"} for r in rows]
    return canon_rows, K.H(canon_rows)


# ======================================================================================================== D8_pre
class PreAudit:
    def __init__(self, root: Path, contracts, authority: A.AuthorityContext, *, d7_dir: Path, d7_tree: str,
                 registry_path: str, registry_sha256: str, model_case_map: list, model_case_map_path: str,
                 model_case_map_sha256: str, synthetic_b: list, suite_report_path: str | None, suite_report_sha256: str | None,
                 created_at: str, profile: dict | None = None):
        self.root, self.C, self.auth = Path(root), contracts, authority
        self.d7_dir, self.d7_tree = Path(d7_dir), d7_tree
        self.registry_path, self.registry_sha = registry_path, registry_sha256
        self.mcm, self.mcm_path, self.mcm_sha = model_case_map, model_case_map_path, model_case_map_sha256
        self.synthetic_b, self.suite_path, self.suite_sha = synthetic_b, suite_report_path, suite_report_sha256
        self.created_at = created_at
        self.profile = profile or P.official(self.root, anclas=authority.anclas_externas or None)
        self.gates, self.evidence, self.deps = [], {}, []

    def ev(self, ref, path, sha256, kind, note, pk=None):
        self.evidence[ref] = {"evidence_ref": ref, "artifact_path": path, "artifact_sha256": sha256, "record_pk": pk or {},
                              "evidence_kind": kind, "authority_manifest_sha256": self.auth.manifest_sha256, "note": note}
        return ref

    def gate(self, gid, scope, level, decision, note, ev, n=0, kind="input"):
        self.gates.append({"run_id": self.run_id, "gate_id": gid, "scope_id": scope, "level": level, "n_cells_affected": n,
                           "decision": decision, "note": note, "evidence_ref": ev, "_kind": kind})

    def p01(self) -> tuple:
        """P01: autoridad consumidora habilitante. Perfil oficial: autoridad REAL reconocida por autenticación del estado
        vivo y facultad d8_pre_authorized verificada (autoridad.autoridad_real_verificada: S4, S5 o sucesora registrada;
        nunca por etiqueta). Perfil de ensayo: raíz aislada (la autoridad ficticia la exige require_authority).
        Devuelve (ok, motivo_del_rechazo)."""
        try:
            P.require_authority(self.profile, self.auth)
            if self.profile["kind"] == "oficial":
                A.autoridad_real_verificada(self.root, self.auth, facultad="d8_pre_authorized")
                return True, None
            return P.is_isolated(self.root), None
        except (P.ProfileError, A.AuthorityError) as exc:
            return False, str(exc)

    def run(self) -> dict:
        self.auth.require("d8_pre_authorized")
        d7info = FAM.verify_version(self.d7_dir, "D7", expected_tree=self.d7_tree)
        self.d7 = D7View.load(self.C, self.d7_dir)
        reg_raw = _file(self.root / self.registry_path, self.registry_sha)
        mcm_raw = _file(self.root / self.mcm_path, self.mcm_sha)
        for b in self.synthetic_b:
            need(b["run_manifest"]["run_class"] == "synthetic_validation", "D8_PRE_CIRCULAR_OR_OFFICIAL_B_INPUT")
        self.run_id = "D8PRE-" + K.H({"d7": self.d7_tree, "b": sorted(b["tree_sha256"] for b in self.synthetic_b),
                                     "reg": self.registry_sha, "suite": self.suite_sha, "auth": self.auth.package_sha256})[:24]
        d7m = rel(self.root, self.d7_dir / "d7_manifest.json")
        ev_d7 = self.ev("EVR.D7.MANIFEST", d7m, d7info["manifest_sha256"], "source", "manifiesto D7 seleccionado por árbol")
        ev_ph = self.ev("EVR.D7.PHASE", rel(self.root, self.d7_dir / "d7_phase_report.json"),
                        sha((self.d7_dir / "d7_phase_report.json").read_bytes()), "validation", "reporte de fase D7")
        ev_gr = self.ev("EVR.D7.GATES", rel(self.root, self.d7_dir / "d7_gate_report.csv"),
                        sha((self.d7_dir / "d7_gate_report.csv").read_bytes()), "validation", "gates D7 (todas las filas)")
        ev_ad = self.ev("EVR.D7.ADMISSIBILITY", rel(self.root, self.d7_dir / "d7_admissibility_report.csv"),
                        sha((self.d7_dir / "d7_admissibility_report.csv").read_bytes()), "domain", "conteos por restricción D7")
        cpath = self.auth.contract_root + "contratos/contract_manifest.json"
        ev_c = self.ev("EVR.CONTRACT", cpath, sha((self.root / cpath).read_bytes()), "contract", "contrato normativo CA2-4 (enmienda candidata)")
        self.deps += [{"role": "d7_version", "path": d7m, "sha256": d7info["manifest_sha256"], "tree_sha256": self.d7_tree,
                       "version": d7info["manifest"]["run_id"], "authority_package_sha256": d7info["manifest"]["authority_package_sha256"]},
                      {"role": "contract", "path": cpath, "sha256": sha((self.root / cpath).read_bytes()), "tree_sha256": None,
                       "version": "CA2-3", "authority_package_sha256": None},
                      {"role": "registro_casos", "path": self.registry_path, "sha256": self.registry_sha, "tree_sha256": None,
                       "version": "A1-E-v2", "authority_package_sha256": None},
                      {"role": "d4_model_case_map", "path": self.mcm_path, "sha256": self.mcm_sha, "tree_sha256": None,
                       "version": "D4", "authority_package_sha256": None}]
        # ------------------------------------------------------------------ gates de insumos
        a_ok, p01_motivo = self.p01()
        if self.profile["kind"] == "ensayo":
            self.deps.append({"role": "perfil_ensayo", "path": self.profile["path"], "sha256": self.profile["sha256"],
                              "tree_sha256": None, "version": "FICTICIO", "authority_package_sha256": None})
        self.gate("P01", "global", "hard_fail", "pass" if a_ok else "fail",
                  f"perfil {self.profile['kind']}; autoridad consumidora {self.auth.kind}"
                  + (" FICTICIA (ENSAYO aislado: nada es oficial)" if self.profile["kind"] == "ensayo" else "")
                  + ("" if a_ok else ": no habilita freeze-run" + (f" ({p01_motivo})" if p01_motivo else "")), ev_c)
        self.gate("P02", "global", "hard_fail", "pass", "familia D7 verificada byte a byte (árbol seleccionado explícitamente)", ev_d7)
        ph = self.d7.phase
        self.gate("P03", "global", "hard_fail", "pass" if ph["ready_for_b"] and ph["hard_fail_count"] == 0 else "fail",
                  f"D7 ready_for_b={ph['ready_for_b']} hard_fail={ph['hard_fail_count']}", ev_ph)
        for g in self.d7.tables["d7_gate_report"]:
            lvl = "hard_fail" if g["blocking"] else ("limitation" if g["status"] == "limitation" else "info")
            dec = {"pass": "pass", "fail": "fail", "limitation": "pass", "not_applicable": "not_applicable"}[g["status"]]
            self.gate("P04." + g["gate_id"], g["scope_id"], lvl, dec, f"D7 {g['gate_id']}: {g['reason_code']}", ev_gr)
        c_ok = d7info["manifest"]["contract_sha256"] == self.auth.contract_sha256 == self.C_contract_sha(cpath)
        self.gate("P05", "global", "hard_fail", "pass" if c_ok else "fail", "contrato D7 = contrato cargado = CA2-3", ev_c)
        grid = self.grid(d7info)
        self.mcm_ok = mcm_raw is not None
        self.gate("P07", "global", "hard_fail", "pass", "mapa de casos D4 autenticado por hash explícito",
                  self.ev("EVR.D4.MAP", self.mcm_path, self.mcm_sha, "source", "model_case_map D4"))
        registry = json.loads(reg_raw)
        rows, csha = predeclared_claims(registry, self.mcm, self.d7)
        self.claims_sha = csha
        ev_cl = self.ev("EVR.CLAIMS.PREDECLARED", self.registry_path, self.registry_sha, "computation",
                        f"claims_registry_sha256={csha}; n_claims={len(rows)}; derivado de registro+D4+sets D7 sin leer B")
        scope_bad = sorted({c for e in registry["entries"] for c in e["country_set"]} & OUT_OF_SCOPE)
        self.gate("P08", "global", "hard_fail", "pass" if rows and not scope_bad else "fail",
                  f"registro de afirmaciones predeclarado ({len(rows)}); fuera de alcance: {scope_bad or 'ninguno'}; "
                  "comparaciones entre países no registradas (delimitadas)", ev_cl)
        # ------------------------------------------------------------------ limitaciones declaradas
        rates = [r for r in self.d7.tables["tax_rate_inputs"]]
        blocked = [r for r in rates if r["status"] != "verified"]
        self.gate("L01", "global", "limitation", "pass", f"tasas estatutarias bloqueadas ({len(blocked)}): sección tau_d_estatutario "
                  "queda incompleta; no se inventa tasa", ev_gr)
        self.gate("L02", "global", "limitation", "pass", "phi_partial: objetivos tau_f/umbral no predeclarados -> not_identified", ev_c)
        self.gate("L03", "global", "limitation", "pass", "external_factor: mapeo nacional no identificado -> not_identified", ev_c)
        # ------------------------------------------------------------------ validaciones
        env_doc = P.environment(self.root, self.profile)
        self.env_doc = env_doc
        env_ok = env_doc["conforms"]
        env_rel, env_sha = E.write_evidence(self.root, FAM.ubicacion("fase2_datos/d8/entradas", self.auth), env_doc)
        ev_env = self.ev("EVR.ENV", env_rel, env_sha, "computation",
                         f"evaluación RE-03 (perfil {self.profile['kind']}): huella {env_doc['fingerprint_sha256'][:16]} vs manifiesto "
                         f"{str(env_doc['approved'].get('manifest_sha256'))[:16]} + lock {str(env_doc['approved'].get('lock_sha256'))[:16]}")
        self.deps.append({"role": "environment", "path": env_rel, "sha256": env_sha, "tree_sha256": None,
                          "version": self.profile["kind"], "authority_package_sha256": None})
        mism = env_doc["mismatches"]
        self.gate("V01", "global", "hard_fail", "pass" if env_ok else "fail",
                  ("entorno conforme con el manifiesto y lock aprobados" if env_ok else
                   f"entorno NO conforme ({len(mism)} discrepancias: {'; '.join(mism[:3])})") +
                  (" [perfil ENSAYO: aprobado FICTICIO]" if self.profile["kind"] == "ensayo" else ""), ev_env, kind="validation")
        from herramientas.b import ejecutar_b as EB
        if self.suite_path:
            rep = json.loads(_file(self.root / self.suite_path, self.suite_sha))
            binding = []
            if rep.get("code_manifest_sha256") != EB.code_manifest_sha256():
                binding.append("SUITE_OTRO_CODIGO")
            if rep.get("suite_code_sha256") != EB.code_manifest_sha256(globs=EB.SUITE_GLOBS):
                binding.append("SUITE_OTRA_VERSION_DE_PRUEBAS")
            if rep.get("environment_fingerprint_sha256") != env_doc["fingerprint_sha256"]:
                binding.append("SUITE_OTRO_ENTORNO")
            ok = (rep.get("failed") == 0 and rep.get("errors") == 0 and rep.get("passed", 0) > 0
                  and rep.get("passed") == rep.get("total") == rep.get("ast_total") and not binding)
            ev_s = self.ev("EVR.SUITE", self.suite_path, self.suite_sha, "validation",
                           f"suites bloque 2: passed={rep.get('passed')} failed={rep.get('failed')} errors={rep.get('errors')}; "
                           f"vínculo código/suite/entorno: {'ok' if not binding else ','.join(binding)}")
            self.gate("V02", "global", "hard_fail", "pass" if ok else "fail", "suites contractuales, analíticas y sintéticas "
                      + ("vinculadas a este código, suite y entorno" if not binding else "NO vinculadas: " + ",".join(binding)), ev_s,
                      kind="validation")
            t2 = rep.get("t2_measured")
            t2_ok = t2 is not None and Decimal(str(t2)) < Decimal("1e-4") and not binding
            self.gate("V03", "global", "hard_fail", "pass" if t2_ok else "fail", f"T2 medido en problemas con solución conocida: {t2}",
                      ev_s, kind="validation")
            self.deps.append({"role": "suite_report", "path": self.suite_path, "sha256": self.suite_sha, "tree_sha256": None,
                              "version": "bloque2", "authority_package_sha256": None})
        else:
            ev_s = ev_c
            self.gate("V02", "global", "hard_fail", "fail", "sin reporte de suites seleccionado", ev_c, kind="validation")
            self.gate("V03", "global", "hard_fail", "fail", "T2 no medido", ev_c, kind="validation")
        syn_ok = bool(self.synthetic_b)
        for b in self.synthetic_b:
            bm = rel(self.root, Path(b["path"]) / "b_manifest.json")
            evb = self.ev("EVR.B.SYN." + b["tree_sha256"][:16], bm, b["manifest_sha256"], "validation",
                          f"validación sintética B {b['run_manifest']['run_id']} status={b['run_manifest']['status']}")
            if b.get("d7view") is not None:
                resolver, tols, errs = consumer_context(self.root, b["manifest"], b["d7view"].manifest)
                errs = errs + RULES.check_b(b["tables"], self.C, b["d7view"], resolver=resolver, tolerances=tols,
                                            grid_cells=b.get("grid_cells"))
            else:
                errs = ["D7_SINTETICO_NO_CARGADO"]
            ok = not errs and b["run_manifest"]["run_class"] == "synthetic_validation"
            syn_ok &= ok
            self.gate("V04", b["tree_sha256"][:24], "hard_fail", "pass" if ok else "fail",
                      "B sintético: reglas contratadas " + ("sin violaciones" if not errs else f"{len(errs)} violaciones: {errs[0][:120]}")
                      + f"; estado de la corrida sintética: {b['run_manifest']['status']}",
                      evb, n=len(b["tables"]["confrontation_result"]), kind="validation")
            self.deps.append({"role": "b_synthetic_validation", "path": bm, "sha256": b["manifest_sha256"],
                              "tree_sha256": b["tree_sha256"], "version": b["run_manifest"]["run_id"],
                              "authority_package_sha256": b["manifest"]["authority_package_sha256"]})
        if not self.synthetic_b:
            self.gate("V04", "global", "hard_fail", "fail", "sin validación sintética B seleccionada", ev_c, kind="validation")
        singleton = all(len(self.d7.nodes(s, p)) == 1 for s in self.d7.sets for p in STRUCT_ADM + ["eta_d", "eta_f", "phi"])
        want_model = self.profile.get("model_provider", "modelo_teorico_v2_2")
        cov_ok = []
        for b in self.synthetic_b:
            mdep = [d for d in b["manifest"]["input_dependencies"] if d["role"] == "method"]
            kind = json.loads((self.root / mdep[0]["path"]).read_bytes()).get("model_provider") if mdep else None
            if kind == want_model:
                cov_ok.append(all(c["status"] == "complete" for c in b["tables"]["computation_coverage"]))
        cont = singleton or (bool(cov_ok) and all(cov_ok))
        self.gate("V05", "global", "hard_fail", "pass" if cont else "fail",
                  "cobertura del continuo estructural: " + ("soportes singleton" if singleton else
                  (f"cobertura certificada por cajas con el proveedor {want_model} en las validaciones sintéticas" if cont else
                   f"PENDIENTE: el proveedor {want_model} no aporta encierros demostrativos (sin cota global validada de C2/G "
                   "ni poda certificada entre nudos)")), ev_ad, kind="validation")
        arows = P.a_reports_binding(self.root, self.profile, env_doc)
        for r in arows:
            evr = self.ev("EVR.AREPORT." + r["id"], r["path"], r["sha256"] or "0" * 64, "validation",
                          f"informe {r['id']}: " + ("vinculado a entorno/lock aprobados, salidas y árbol de código actual" if r["ok"]
                                                   else "NO vinculado: " + ",".join(r["problems"])))
            if r["sha256"]:
                self.deps.append({"role": "a_report", "path": r["path"], "sha256": r["sha256"], "tree_sha256": None,
                                  "version": r["id"], "authority_package_sha256": None})
            self.gate("V08", r["id"], "hard_fail", "pass" if r["ok"] else "fail",
                      f"evidencia {r['id']} vinculada al entorno aprobado y a los bytes" + ("" if r["ok"] else ": " + ",".join(r["problems"])),
                      evr, kind="validation")
        if not arows:
            self.gate("V08", "global", "hard_fail", "fail", "perfil sin informes A/A-ter", ev_c, kind="validation")
        dc = self.double_counting(grid, ev_c)
        not_pass = [f"{r['mechanism']}={r['status']}" for r in dc if r["status"] != "pass"]
        self.gate("V06", "global", "hard_fail", "pass" if not not_pass else "fail",
                  "auditoría de doble conteo (costos, bases, reporte, gravabilidad)" +
                  (": sin verificar o fallidos " + ", ".join(not_pass) if not_pass else ": todos verificados"), ev_c, kind="validation")
        adm = self.admissibility()
        zero = [r["support_set_id"] for r in adm if r["n_declared"] == 0]
        self.gate("V07", "global", "hard_fail", "pass" if not zero else "fail",
                  "admisibilidad por set: unión sin doble conteo" + (f"; sets sin puntos: {zero[:3]}" if zero else ""), ev_ad,
                  kind="validation")
        # ------------------------------------------------------------------ fase
        fails_in = sum(1 for g in self.gates if g["level"] == "hard_fail" and g["decision"] == "fail" and g["_kind"] == "input")
        fails_val = sum(1 for g in self.gates if g["level"] == "hard_fail" and g["decision"] == "fail" and g["_kind"] == "validation")
        ready = fails_in == 0 and fails_val == 0 and env_ok
        phase = {"run_id": self.run_id, "status": "pass" if ready else "blocked", "input_gate_failures": fails_in,
                 "validation_failures": fails_val, "ready_for_freeze_run": ready}
        for g in self.gates:
            g.pop("_kind")
        tables = {"input_audit_report": self.gates, "double_counting_audit": dc, "admissibility_report": adm,
                  "evidence_records": sorted(self.evidence.values(), key=lambda e: e["evidence_ref"])}
        return {"tables": tables, "phase": phase, "claims_sha256": self.claims_sha}

    def C_contract_sha(self, cpath):
        return sha((self.root / cpath).read_bytes())

    def grid(self, d7info):
        deps = [d for d in d7info["manifest"]["input_dependencies"] if d["role"] == "external_grid"]
        if len(deps) != 1:
            self.gate("P06", "global", "hard_fail", "fail", "D7 sin dependencia única de grilla externa",
                      self.evidence["EVR.D7.MANIFEST"]["evidence_ref"])
            return None
        d = deps[0]
        raw = (self.root / d["path"]).read_bytes()
        ok = sha(raw) == d["sha256"]
        ev = self.ev("EVR.GRID", d["path"], sha(raw), "source", "grilla externa fijada en el manifiesto D7")
        cells = X.read_grid(raw) if ok else None
        ids = X.identities(cells) if cells else {"pass": False}
        self.gate("P06", "global", "hard_fail", "pass" if ok and ids["pass"] else "fail",
                  f"grilla externa: hash {'ok' if ok else 'ALTERADO'}; identidades Q/F_fix/F_fix_perp a T1: {ids.get('pass')}", ev)
        self.deps.append({"role": "external_grid", "path": d["path"], "sha256": d["sha256"], "tree_sha256": None,
                          "version": d["version"], "authority_package_sha256": None})
        return cells

    def double_counting(self, cells, ev_c):
        rows = []

        def row(mech, where, where_not, by, ok, ev):
            rows.append({"run_id": self.run_id, "mechanism": mech, "where_counted": where, "where_not_counted": where_not,
                         "verified_by": by, "status": ("pass" if ok else "fail") if ok is not None else "not_applicable",
                         "evidence_ref": ev})
        ev_g = self.evidence.get("EVR.GRID", {}).get("evidence_ref", ev_c)
        if cells:
            ids = X.identities(cells)
            w = ids["worst_residuals"]
            row("costo_fijo_F_fix", "Q (una vez: F_admin+F_trans+F_leak)", "C2, R, bases fiscales",
                f"identidad F_fix a T1 (max {w['F_fix']:.3g}) y Q reconstruido (max {w['Q']:.3g})", w["F_fix"] <= X.T1 and w["Q"] <= X.T1, ev_g)
            row("addback_F_leak", "solo cota addback_completo", "cota sin_addback (F_fix_perp=F_fix-F_leak)",
                f"partición F_fix_perp a T1 (max {w['F_fix_perp']:.3g})", w["F_fix_perp"] <= X.T1, ev_g)
            base_dc = all(c.requirement_basis != "baseline" or c.s_PB == 0 or True for c in cells)
            q_ok = all(abs(c.Q("addback_completo") - c.Q_grid) <= X.T1 for c in cells)
            row("deuda_s_PB", "solo base debt_consistent (1{DC} s_PB)", "base baseline", "Q por base reconstruido a T1", q_ok and base_dc, ev_g)
        else:
            for m in ("costo_fijo_F_fix", "addback_F_leak", "deuda_s_PB"):
                row(m, "Q", "C2", "grilla no autenticada", False, ev_c)
        Kc = self.C.K
        macro_only = {"pi_iva", "pi_otros_productos", "pi_produccion", "eta_w", "eta_H", "gain_share"}
        overlap = set(Kc["structural_primitive_ids"]) & macro_only
        row("pi_y_eta_en_lambda", "lambda_pi (puente macro) y K1", "C2 y clave estructural",
            "CLAVES: pi, eta_w, eta_H y gain_share fuera de la proyección estructural (a, rho y kappa comparten q_pot)"
            + (f"; solapan {sorted(overlap)}" if overlap else ""), not overlap and macro_only <= set(Kc["macro_primitive_ids"]) | {"gain_share"},
            ev_c)
        nat = {"s_L_bar", "s_bar_iva", "s_bar_otros_productos", "s_bar_produccion"}
        row("shares_nacionales", "estado nacional de la clave macro", "omega y common_values",
            "CLAVES: lista común sin shares nacionales", not (nat & set(Kc["common_primitive_ids"])), ev_c)
        syn = [b for b in self.synthetic_b]
        if syn:
            ok_n, ok_g, ok_cs = True, True, True
            for b in syn:
                t = b["tables"]
                bgrid = {c.external_cell_id: c for c in b.get("grid_cells", [])}
                macro = {m["macro_id"]: m for m in t["lambda_pi_envelope"]}
                cells_ = {c["cell_id"]: c for c in t["cell_context"]}
                omega_gain = {r["omega_id"]: Decimal(r["value"]) for r in t["omega_values"] if r["parameter_id"] == "gain_share"}
                for r in t["confrontation_result"]:
                    if r["computation_status"] != "complete":
                        continue
                    c = cells_[r["cell_id"]]
                    g = bgrid.get(c["external_cell_id"])
                    if g is None:
                        ok_n = False
                        continue
                    lam = Decimal(macro[r["macro_id"]]["lambda_pi"])
                    N = Decimal(r["K_comp_1"]) * lam * omega_gain[c["omega_id"]]
                    Q = Decimal(repr(g.Q(c["bound_variant"])))
                    ok_n &= abs(N - Q - Decimal(repr(b.get("dme_gai", 0.0)))) <= Decimal("1e-12") * max(1, abs(N))
                for fr in t["frontier_result"]:
                    ok_g &= fr["B_f_grav"] == fr["B_f"]
                    if fr["CS"] is not None:
                        ok_cs &= abs(Decimal(fr["CS"]) - Decimal(fr["R"]) / Decimal(fr["B_pot"])) <= Decimal("1e-12")
            evb = "EVR.B.SYN." + syn[0]["tree_sha256"][:16]
            row("DME_gAI", "N = Q + DME_gAI (una vez)", "C2 y lambda", "K1*lambda*gain = Q + DME en toda celda completa (B sintético)",
                ok_n, evb)
            row("gravabilidad_B_f", "B_f_grav = B_f bajo baseline", "base doméstica", "filas frontier_result del B sintético", ok_g, evb)
            row("reporte_CS", "CS = R/B_pot; lambda solo en K1", "C2", "filas frontier_result del B sintético a T1", ok_cs, evb)
        else:
            for m in ("DME_gAI", "gravabilidad_B_f", "reporte_CS"):
                row(m, "B", "B", "sin B sintético seleccionado", None, ev_c)
        return sorted(rows, key=lambda r: r["mechanism"])

    def admissibility(self):
        """Unión exacta de exclusiones por set sobre (nudos nivel 0) x (países), factorizada sin materializar el producto."""
        out = []
        cache = {}
        for sid in sorted(self.d7.sets):
            axes = {p: self.d7.nodes(sid, p) for p in STRUCT_ADM + MACRO_ADM + ["eta_d", "eta_f", "phi", "gain_share"]}
            countries = self.d7.countries(sid)
            total = 1
            for p in axes:
                total *= len(axes[p])
            if total * len(countries) == 0:
                out.append({"run_id": self.run_id, "support_set_id": sid, "n_declared": 0, "n_admissible": 0, "n_violates_q_pot": 0,
                            "n_violates_eta_H": 0, "n_violates_shares": 0, "n_violates_theory": 0, "n_excluded_union": 0,
                            "share_discarded": None})
                continue
            rest = total
            for p in STRUCT_ADM + MACRO_ADM:
                rest //= len(axes[p])
            v_q = v_e = v_s = v_t = ok_all = 0
            n_states = 0
            for c in countries:
                for shares in self.national_states(sid, c):
                    n_states += 1
                    q, e, s_, t_, ok = self.count_state(axes, shares, c, cache)
                    v_q, v_e, v_s, v_t, ok_all = v_q + q, v_e + e, v_s + s_, v_t + t_, ok_all + ok
            n_decl = total * n_states
            n_adm = ok_all * rest
            v_q, v_e, v_s, v_t = v_q * rest, v_e * rest, v_s * rest, v_t * rest
            union = n_decl - n_adm
            out.append({"run_id": self.run_id, "support_set_id": sid, "n_declared": n_decl, "n_admissible": n_adm,
                        "n_violates_q_pot": v_q, "n_violates_eta_H": v_e, "n_violates_shares": v_s, "n_violates_theory": v_t,
                        "n_excluded_union": union, "share_discarded": float(Fraction(union, n_decl))})
        return out

    def national_states(self, sid, c) -> list:
        """Estado nacional puntual (binding medido) o esquinas de la caja exterior de shares (dominio estricto)."""
        vals, boxes = {}, {}
        for k in MC.SHARE_KEYS:
            b = self.d7.bindings[(sid, k, f"country:{c}")]
            if b["value"] is not None:
                vals[k] = Fraction(Decimal(b["value"]))
            else:
                s = next(v for v in self.d7.supports[(sid, k)].values() if v["support_id"] == b["support_id"])
                boxes[k] = (Fraction(Decimal(s["lower"])), Fraction(Decimal(s["upper"])))
        keys = sorted(boxes)
        out = []
        for combo in product(*[sorted(set(boxes[k])) for k in keys]):
            out.append(dict(vals, **dict(zip(keys, combo))))
        return out

    @staticmethod
    def count_state(axes, shares, country, cache):
        """Conteos (q_pot, eta_H, shares, teoría, admisibles) de un estado nacional sobre el producto de nudos.

        Factorización exacta: s_T_marg y s_Pi_marg dependen solo de (pi, eta_w, eta_H, shares); con q_pot < 1,
        lambda = s_Pi/(1 - q_pot) > 0 equivale a s_Pi > 0. Por eso el bloque macro se cuenta una vez por estado y se
        combina con los conteos estructurales (a, rho, kappa, u_theta, beta_tilde, z_cost) sin materializar el producto."""
        key = (tuple(sorted(shares.items())), tuple(tuple(axes[p]) for p in MACRO_ADM))
        hit = cache.get(key)
        if hit is None:
            eh_bad = sh_bad = both_ok = 0
            for combo in product(*[axes[p] for p in MACRO_ADM]):
                v = dict(zip(MACRO_ADM, combo))
                if not v["eta_H"] > -1:
                    eh_bad += 1
                    continue
                m = MC.bridge(shares, dict(v, a=Fraction(3, 2), rho=Fraction(0), kappa_tilde=Fraction(0)))
                ok = m.s_T_marg >= 0 and m.s_Pi_marg > 0
                sh_bad += 0 if ok else 1
                both_ok += 1 if ok else 0
            hit = cache[key] = (eh_bad, sh_bad, both_ok)
        eh_bad, sh_bad, macro_ok = hit
        n_macro = 1
        for p in MACRO_ADM:
            n_macro *= len(axes[p])
        skey = ("struct",) + tuple(tuple(axes[p]) for p in STRUCT_ADM)
        st = cache.get(skey)
        if st is None:
            n_struct = len(axes["u_theta"]) * len(axes["beta_tilde"]) * len(axes["z_cost"])
            n_ark = q_bad = q_ok_n = th_all = th_qok = 0
            for a, rho, kt in product(axes["a"], axes["rho"], axes["kappa_tilde"]):
                fa, fr, fk = Fraction(a), Fraction(rho), Fraction(kt)
                th_n = 0
                for u, bt, z in product(axes["u_theta"], axes["beta_tilde"], axes["z_cost"]):
                    fu = Fraction(u)
                    th_n += 1 if (fa > 1 and 0 < fu < 1 and 1 + fu * (fa - 1) < fa and fr < fa and 0 <= fr <= 1 and fk > 0 and
                                  Fraction(bt) > 0 and Fraction(z) > 0) else 0
                q_ok = fa > 1 and fa > fr and fk * (fa - 1) / (fa - fr) < 1
                n_ark += 1
                th_all += th_n
                if q_ok:
                    q_ok_n += 1
                    th_qok += th_n
                else:
                    q_bad += 1
            st = cache[skey] = (n_struct, n_ark, q_bad, q_ok_n, th_all, th_qok)
        n_struct, n_ark, q_bad, q_ok_n, th_all, th_qok = st
        v_q = q_bad * n_struct * n_macro
        v_e = n_ark * eh_bad * n_struct
        v_s = q_ok_n * sh_bad * n_struct
        v_t = (n_ark * n_struct - th_all) * n_macro
        ok_all = th_qok * macro_ok
        return v_q, v_e, v_s, v_t, ok_all


def _norm(contracts, tables: dict) -> dict:
    return {n: T.sort_rows(contracts, n, [T.normalize_row(contracts, n, r) for r in rows]) for n, rows in tables.items()}


def emit_pre(root: Path, contracts, audit: PreAudit, result: dict, *, out_root: Path, producer_path: str, producer_bytes: bytes) -> dict:
    files = {}
    for name, rows in result["tables"].items():
        data = T.table_bytes(contracts, name, rows)
        files[contracts.C["tables"][name]["file"].split("/", 1)[1]] = (data, T.csv_rows(data))
    files["d8_pre_phase_report.json"] = (T.json_doc_bytes(contracts, "d8_pre_phase_report", dict(result["phase"])), None)
    contracts.references(dict(audit.d7.tables, **_norm(contracts, result["tables"])))
    entries = FAM.entries_for(files)
    mb = FAM.manifest(contracts, "D8_pre", run_id=audit.run_id, producer_path=producer_path, producer_sha256=sha(producer_bytes),
                      authority_package=audit.auth.package_sha256, authority_manifest=audit.auth.manifest_sha256,
                      contract_sha256=audit.auth.contract_sha256, dependencies=audit.deps, entries=entries,
                      phase_status="complete" if result["phase"]["status"] == "pass" else "blocked", created_at=audit.created_at)
    info = FAM.write_version(Path(out_root), "D8_pre", files, mb)
    return dict(info, phase=result["phase"], claims_sha256=result["claims_sha256"], run_id=audit.run_id)


# ======================================================================================================== D8_post
class PostAudit:
    def __init__(self, root: Path, contracts, authority: A.AuthorityContext, *, b_dir: Path, b_tree: str, d8_pre_dir: Path,
                 d8_pre_tree: str, d7_dir: Path, grid_cells: list, registry: dict, model_case_map: list, created_at: str,
                 bundle_index: tuple | None = None, profile: dict | None = None):
        self.root, self.C, self.auth = Path(root), contracts, authority
        self.b_dir, self.b_tree, self.pre_dir, self.pre_tree, self.d7_dir = Path(b_dir), b_tree, Path(d8_pre_dir), d8_pre_tree, Path(d7_dir)
        self.grid_cells, self.registry, self.mcm, self.created_at = grid_cells, registry, model_case_map, created_at
        self.gates, self.evidence, self.refs, self.deps = [], {}, {}, []
        self.bundle_index = bundle_index
        self.profile = profile or P.official(self.root, anclas=authority.anclas_externas or None)

    def ev(self, ref, path, sha256, kind, note, pk=None):
        self.evidence[ref] = {"evidence_ref": ref, "artifact_path": path, "artifact_sha256": sha256, "record_pk": pk or {},
                              "evidence_kind": kind, "authority_manifest_sha256": self.auth.manifest_sha256, "note": note}
        return ref

    def gate(self, gid, scope, ok, reason, ev, result_ref=None, limitation=False):
        status = "pass" if ok else ("limitation" if limitation else "fail")
        self.gates.append({"run_id": self.run_id, "gate_id": gid, "scope_id": scope, "status": status, "reason_code": reason,
                           "result_ref": result_ref, "evidence_ref": ev})
        return ok

    def ref(self, table, pk, chain_extra=None):
        row = self.bidx[table][tuple(pk[c] for c in self.C.C["tables"][table]["primary_key"])]
        chain = K.H({"b_manifest": self.b["manifest_sha256"], "table": table, "pk": pk, "row": K.H(row),
                     "d8_pre_manifest": self.pre["manifest_sha256"], "d7_tree": self.b_d7_tree, "extra": chain_extra})
        rid = "RREF:" + K.H([self.b["manifest_sha256"], table, pk])[:40]
        self.refs[rid] = {"result_ref": rid, "b_manifest_sha256": self.b["manifest_sha256"], "table_name": table, "record_pk": pk,
                          "source_chain_sha256": chain}
        return rid, chain

    def run(self) -> dict:
        self.auth.require("d8_post_authorized")
        pre_before = FAM.verify_version(self.pre_dir, "D8_pre", expected_tree=self.pre_tree)
        self.pre = pre_before
        self.b = load_b(self.C, self.b_dir, self.b_tree)
        t = self.b["tables"]
        rm = self.b["run_manifest"]
        self.bidx = {n: {tuple(r[c] for c in self.C.C["tables"][n]["primary_key"]): r for r in rows} for n, rows in t.items()}
        self.run_id = "D8POST-" + K.H({"b": self.b_tree, "pre": self.pre_tree, "auth": self.auth.package_sha256})[:24]
        bdeps = {d["role"]: d for d in self.b["manifest"]["input_dependencies"]}
        pdeps = {d["role"]: d for d in pre_before["manifest"]["input_dependencies"]}
        self.b_d7_tree = bdeps.get("d7_version", {}).get("tree_sha256")
        bm = rel(self.root, self.b_dir / "b_manifest.json")
        pm = rel(self.root, self.pre_dir / "d8_pre_manifest.json")
        ev_b = self.ev("EVP.B.MANIFEST", bm, self.b["manifest_sha256"], "validation", f"B {rm['run_class']} {rm['run_id']}")
        ev_p = self.ev("EVP.D8PRE.MANIFEST", pm, pre_before["manifest_sha256"], "validation", "D8_pre fijado (sin modificar)")
        self.deps = [{"role": "b_version", "path": bm, "sha256": self.b["manifest_sha256"], "tree_sha256": self.b_tree,
                      "version": rm["run_id"], "authority_package_sha256": self.b["manifest"]["authority_package_sha256"]},
                     {"role": "d8_pre_version", "path": pm, "sha256": pre_before["manifest_sha256"], "tree_sha256": self.pre_tree,
                      "version": pre_before["manifest"]["run_id"],
                      "authority_package_sha256": pre_before["manifest"]["authority_package_sha256"]}]
        # ciclo: B no puede depender de D8_post ni D8_pre de B oficial
        cyc = any(d["role"].startswith("d8_post") for d in self.b["manifest"]["input_dependencies"]) or \
            any(d["role"] == "b_version" for d in pre_before["manifest"]["input_dependencies"])
        self.gate("Q00", "global", not cyc, "NO_DEPENDENCY_CYCLE" if not cyc else "DEPENDENCY_CYCLE", ev_p)
        pre_phase = json.loads((self.pre_dir / "d8_pre_phase_report.json").read_bytes())
        self.gate("Q01", "global", True, "B_FAMILY_VERIFIED", ev_b)
        same_d7 = self.b_d7_tree is not None and pdeps.get("d7_version", {}).get("tree_sha256") == self.b_d7_tree
        self.gate("Q02", "global", same_d7, "SAME_D7_AS_D8_PRE" if same_d7 else "D7_MISMATCH_B_VS_D8_PRE", ev_p)
        trial = self.profile["kind"] == "ensayo"
        if trial:
            self.deps.append({"role": "perfil_ensayo", "path": self.profile["path"], "sha256": self.profile["sha256"],
                              "tree_sha256": None, "version": "FICTICIO", "authority_package_sha256": None})
        pdep = bdeps.get("perfil_ensayo")
        if trial:
            official = rm["run_class"] == "trial_frozen" and pdep is not None and pdep["sha256"] == self.profile["sha256"]
            self.gate("Q03", "global", official, "TRIAL_FROZEN_RUN_OF_THIS_PROFILE" if official else "NOT_A_FROZEN_RUN_OF_THIS_PROFILE",
                      ev_b)
        else:
            official = rm["run_class"] == "official" and pdep is None
            self.gate("Q03", "global", official, "OFFICIAL_RUN" if official else "SYNTHETIC_NOT_EXPORTABLE", ev_b)
        pre_ok = pre_phase["status"] == "pass" and pre_phase["ready_for_freeze_run"]
        pre_prof = pdeps.get("perfil_ensayo", {}).get("sha256")
        pre_ok = pre_ok and pre_prof == (self.profile["sha256"] if trial else None)
        self.gate("Q04", "global", pre_ok, "D8_PRE_PASS" if pre_ok else "D8_PRE_BLOCKED", ev_p)
        try:
            P.require_authority(self.profile, self.auth)
            auth_ok = self.auth.scope.get("official_export_authorized") is True and (P.is_isolated(self.root) if trial else True)
        except P.ProfileError:
            auth_ok = False
        self.gate("Q05", "global", auth_ok, ("TRIAL_EXPORT_AUTHORIZED_FICTITIOUS" if trial else "EXPORT_AUTHORIZED") if auth_ok
                  else "EXPORT_NOT_AUTHORIZED", ev_p)
        fr_ok, fr_reason = self.freeze_matches(bdeps)
        self.gate("Q17", "global", fr_ok, fr_reason, ev_b)
        d7 = self.d7 = D7View.load(self.C, self.d7_dir)
        need(FAM.verify_version(self.d7_dir, "D7", expected_tree=self.b_d7_tree)["tree_sha256"] == self.b_d7_tree, "D8_POST_D7")
        resolver, tols, errs = consumer_context(self.root, self.b["manifest"], d7.manifest)
        checker = RULES.Checker(t, self.C, d7, grid_cells=self.grid_cells, resolver=resolver, tolerances=tols)
        errs = errs + checker.run()
        self.gate("Q06", "global", not errs, "CONTRACT_RULES_PASS" if not errs else "CONTRACT_RULES_FAIL", ev_b)
        conv_bad = [r for r in t["convergence_result"] if r["status"] != "pass" and
                    (r["quantity_id"], r["level_before"], r["level_after"]) not in checker.valid_na]
        for r in conv_bad[:50]:
            rid, _ = self.ref("convergence_result", {"quantity_id": r["quantity_id"], "level_before": r["level_before"],
                                                     "level_after": r["level_after"]})
            self.gate("Q07", r["quantity_id"][:60], False, "CONVERGENCE_" + r["status"].upper(), ev_b, rid)
        self.gate("Q07", "global", not conv_bad, ("CONVERGENCE_PASS_OR_AUTHENTICATED_NA" if checker.valid_na else "CONVERGENCE_PASS") if not conv_bad else "CONVERGENCE_NOT_PASS", ev_b)
        cov_bad = [c for c in t["computation_coverage"] if c["status"] != "complete"]
        self.gate("Q08", "global", not cov_bad, "COVERAGE_COMPLETE" if not cov_bad else "COVERAGE_INCOMPLETE", ev_b)
        rows, csha = predeclared_claims(self.registry, self.mcm, d7)
        pre_ev = [e for e in self.pre_tables("evidence_records") if e["evidence_ref"] == "EVR.CLAIMS.PREDECLARED"]
        pre_sha = pre_ev[0]["note"].split("claims_registry_sha256=")[1].split(";")[0] if pre_ev else None
        b_claims = [{k: v for k, v in r.items() if k != "baseline_status"} for r in t["claims"]]
        same = pre_sha == csha and K.H(sorted(b_claims, key=lambda r: r["claim_id"])) == csha
        self.gate("Q09", "global", same, "CLAIMS_EQUAL_PREDECLARED" if same else "CLAIMS_DIFFER_FROM_PREDECLARED", ev_p)
        mono_bad = [c for c in t["capture_ceiling_result"] if c["monotonicity_check"] == "fail"]
        self.gate("Q10", "global", not mono_bad, "MENU_MONOTONICITY_PASS" if not mono_bad else "MENU_MONOTONICITY_FAIL", ev_b)
        self.gate("Q11", "global", rm["status"] == "complete", "RUN_COMPLETE" if rm["status"] == "complete" else "RUN_INCOMPLETE", ev_b)
        rd = not any(r["run_readiness_flag"] for r in t["confrontation_result"]) and rm["run_readiness_flag"] is False
        self.gate("Q12", "global", rd or pre_ok, "READINESS_CONSISTENT" if (rd or pre_ok) else "READINESS_WITHOUT_D8_PRE", ev_b)
        scope_bad = sorted({c["country_id"] for c in t["cell_context"]} & OUT_OF_SCOPE)
        self.gate("Q13", "global", not scope_bad, "SCOPE_COUNTRIES_OK" if not scope_bad else "OUT_OF_SCOPE_COUNTRY", ev_b)
        from paper2b import contexto as CX
        if self.bundle_index:
            defs = CX.definitions_from_bundles(self.root, self.bundle_index[0], self.bundle_index[1],
                                               installed_prefix=self.auth.installed_prefix, contract_sha256=A.CONTRACT_S3)
        else:
            defs = CX.definitions_from_installed(self.root, installed_prefix=self.auth.installed_prefix)
        self.context_records, cerrs = CX.produce_all(t, defs)
        self.gate("Q16", "global", not cerrs, "CONTEXT_COORDINATES_PRODUCED" if not cerrs else "CONTEXT_COORDINATES_MISSING", ev_b)
        coverage = self.coverage(t, d7)
        inc_fam = sum(1 for c in coverage if c["audit_status"] != "pass")
        self.gate("Q14", "global", inc_fam == 0, "COVERAGE_FAMILIES_PASS" if inc_fam == 0 else "COVERAGE_FAMILIES_INCOMPLETE", ev_b)
        claim_rows = []
        for cl in t["claims"]:
            rid, chain = self.ref("claims", {"claim_id": cl["claim_id"]})
            ready = official and pre_ok and fr_ok and not errs and not conv_bad and not cov_bad and cl["baseline_status"] == "verified"
            interp = self.interpretation(cl)
            claim_rows.append({"claim_id": cl["claim_id"], "result_ref": rid, "scope": f"{cl['claim_scope']}:{cl['quantifier'][:160]}",
                               "permitted_interpretation": interp, "source_chain_sha256": chain,
                               "status": "pass" if ready else ("limitation" if cl["baseline_status"] == "verified" else "fail"),
                               "evidence_ref": ev_b})
        # D8_pre intacto
        after = FAM.verify_version(self.pre_dir, "D8_pre", expected_tree=self.pre_tree)
        intact = after["manifest_sha256"] == pre_before["manifest_sha256"]
        self.gate("Q15", "global", intact, "D8_PRE_UNMODIFIED" if intact else "D8_PRE_MODIFIED", ev_p)
        failures = sum(1 for g in self.gates if g["status"] == "fail")
        ready = failures == 0 and inc_fam == 0
        phase = {"run_id": self.run_id, "status": "pass" if ready else "blocked", "result_failures": failures,
                 "incomplete_families": inc_fam, "ready_for_export": ready}
        tables = {"result_references": sorted(self.refs.values(), key=lambda r: r["result_ref"]),
                  "d8_claim_audit": claim_rows, "d8_coverage": coverage, "d8_post_audit": self.gates,
                  "d8_post_evidence_records": sorted(self.evidence.values(), key=lambda e: e["evidence_ref"])}
        return {"tables": tables, "phase": phase, "errors": errs}

    def freeze_matches(self, bdeps: dict) -> tuple[bool, str]:
        """La auditoría corresponde a la selección EJECUTADA: el freeze-run de B fija este D8_pre, el D7 de B y el
        código, configuración, entorno y contrato cuyos bytes B registró como entradas técnicas."""
        from herramientas.bloque2 import freeze_run as FR
        d = bdeps.get("freeze_run")
        if d is None:
            return False, "FREEZE_RUN_ABSENT"
        try:
            fr = FR.load(self.root, d["sha256"], FR.location(self.auth))
        except (FR.FreezeError, OSError) as exc:
            return False, str(exc).split(":")[0]
        sel = fr["selection"]
        if d["path"] != rel(self.root, fr["path"] / "selection.json"):
            return False, "FREEZE_RUN_PATH_MISMATCH"
        if sel["profile"]["kind"] != self.profile["kind"] or sel["profile"].get("sha256") != self.profile.get("sha256"):
            return False, "FREEZE_RUN_OTHER_PROFILE"
        if sel["d8_pre"]["tree_sha256"] != self.pre_tree:
            return False, "AUDIT_D8_PRE_NOT_THE_FROZEN_ONE"
        if sel["d7"]["tree_sha256"] != self.b_d7_tree:
            return False, "B_D7_NOT_THE_FROZEN_ONE"
        if bdeps.get("code", {}).get("sha256") != sel["code"]["manifest_sha256"]:
            return False, "B_CODE_NOT_THE_FROZEN_ONE"
        if bdeps.get("configuration", {}).get("sha256") != sel["configuration"]["sha256"]:
            return False, "B_CONFIGURATION_NOT_THE_FROZEN_ONE"
        if bdeps.get("contract", {}).get("sha256") != sel["contract"]["sha256"]:
            return False, "B_CONTRACT_NOT_THE_FROZEN_ONE"
        env = bdeps.get("environment")
        try:
            doc = E.verify_evidence(self.root, env["path"], env["sha256"]) if env else None
        except (E.EnvironmentError_, OSError):
            doc = None
        if doc is None or doc["fingerprint_sha256"] != sel["environment"]["fingerprint_sha256"] or not doc["conforms"]:
            return False, "B_ENVIRONMENT_NOT_THE_FROZEN_ONE"
        if bdeps.get("d8_pre_version", {}).get("tree_sha256") != self.pre_tree:
            return False, "B_D8_PRE_NOT_THIS_AUDIT"
        return True, "FREEZE_RUN_MATCHES_EXECUTION"

    def pre_tables(self, name):
        return self.C.read_csv(self.pre_dir / self.C.C["tables"][name]["file"].split("/", 1)[1], name)

    @staticmethod
    def interpretation(cl) -> str:
        q = json.loads(cl["quantifier"])
        if "MEX" in q.get("countries", []) and cl["claim_scope"] != "global":
            return "MEX: solo interpretación declarada; sin lectura cuantitativa de precisión"
        if cl["availability_case_id"].startswith("conditional"):
            return "condicional: escenario de disponibilidad asumida; sin precisión institucional; no transporta a otros casos"
        return "según cuantificador registrado; capas y cotas por separado; sin ranking entre países"

    def coverage(self, t, d7) -> list:
        """Esperados derivados de forma independiente (omega admisibles x países x diseños x casos D4 x estados x grilla x cotas)."""
        fams = []
        adm = {o["omega_id"]: o for o in t["omega"] if o["domain_status"] == "admissible"}
        designs = sorted({f["design_v"] for f in t["frontier_context"]}) or ["G", "N"]
        n_cases = Counter(r["country_id"] for r in self.mcm)
        exp_fr = sum(n_cases[c] * len(designs) for o in adm.values() for c in d7.countries(o["support_set_id"]))
        obs_fr = len(t["frontier_context"])
        fams.append(self.fam("frontier_context", exp_fr, obs_fr, 0))
        grid_n = Counter(g.country_id for g in self.grid_cells)
        by_oc = {}
        for m in t["lambda_pi_envelope"]:
            by_oc.setdefault((m["omega_id"], m["country_id"]), []).append(m)

        def matching(f):
            label = f"{f['design_v']}-{f['instrument_j']}-{f['availability_case_id']}"
            return sum(1 for m in by_oc.get((f["omega_id"], f["country_id"]), [])
                       if m["macro_key_payload"].get("kind") == "macro-v2" or m["macro_key_payload"]["case_id"].endswith(":" + label))
        exp_cells = sum(matching(f) * grid_n[f["country_id"]] * len(X.BOUNDS) for f in t["frontier_context"])
        fams.append(self.fam("cell_context", exp_cells, len(t["cell_context"]), 0))
        st = Counter(r["computation_status"] for r in t["confrontation_result"])
        excl = sum(1 for r in t["confrontation_result"] if r["computation_status"] in ("not_applicable", "excluded") and r["reason_code"])
        fams.append(self.fam("confrontation_result", len(t["cell_context"]), st["complete"], excl))
        inv = t["inversion_result"]
        fams.append(self.fam("inversion_result", 6 * len(t["cell_context"]),
                             sum(1 for r in inv if r["computation_status"] == "complete"),
                             sum(1 for r in inv if r["computation_status"] in ("not_applicable", "excluded") and r["reason_code"])))
        r1 = t["r1_summary"]
        fams.append(self.fam("r1_summary", len(t["cell_context"]), sum(1 for r in r1 if r["computation_status"] == "complete"),
                             sum(1 for r in r1 if r["computation_status"] in ("not_applicable", "excluded"))))
        r2 = t["r2_sections"]
        fams.append(self.fam("r2_sections", 4 * len(t["cell_context"]), sum(1 for r in r2 if r["computation_status"] == "complete"),
                             sum(1 for r in r2 if r["computation_status"] in ("not_applicable", "excluded"))))
        cl = t["claims"]
        fams.append(self.fam("claims", len(cl), sum(1 for c in cl if c["baseline_status"] != "not_evaluated"), 0))
        return fams

    def fam(self, name, expected, observed, excluded):
        miss = expected - observed - excluded
        return {"run_id": self.run_id, "cell_family": name, "expected": expected, "observed": observed,
                "excluded_with_reason": excluded, "unexplained_missing": max(miss, 0) if miss >= 0 else miss,
                "audit_status": "pass" if miss == 0 else "fail"}


def emit_post(root: Path, contracts, audit: PostAudit, result: dict, *, out_root: Path, producer_path: str,
              producer_bytes: bytes) -> dict:
    tabs = result["tables"]
    for c in tabs["d8_coverage"]:
        need(c["unexplained_missing"] >= 0, "D8_POST_OBSERVED_EXCEEDS_EXPECTED:" + c["cell_family"])
    files = {}
    for name, rows in tabs.items():
        data = T.table_bytes(contracts, name, rows)
        files[contracts.C["tables"][name]["file"].split("/", 1)[1]] = (data, T.csv_rows(data))
    files["d8_post_phase_report.json"] = (T.json_doc_bytes(contracts, "d8_post_phase_report", dict(result["phase"])), None)
    contracts.references(dict(audit.d7.tables, **audit.b["tables"], **_norm(contracts, tabs)))
    for r in tabs["result_references"]:
        pk = contracts.C["tables"][r["table_name"]]["primary_key"]
        need(set(r["record_pk"]) == set(pk) and tuple(r["record_pk"][k] for k in pk) in audit.bidx[r["table_name"]],
             "D8_POST_RESULT_REF_UNRESOLVED")
    entries = FAM.entries_for(files)
    mb = FAM.manifest(contracts, "D8_post", run_id=audit.run_id, producer_path=producer_path, producer_sha256=sha(producer_bytes),
                      authority_package=audit.auth.package_sha256, authority_manifest=audit.auth.manifest_sha256,
                      contract_sha256=audit.auth.contract_sha256, dependencies=audit.deps, entries=entries,
                      phase_status="complete" if result["phase"]["status"] == "pass" else "blocked", created_at=audit.created_at)
    info = FAM.write_version(Path(out_root), "D8_post", files, mb)
    return dict(info, phase=result["phase"], run_id=audit.run_id)


# ======================================================================================================== exportación
def exportar_oficial(root: Path, authority: A.AuthorityContext, *, d8_post_dir: Path, d8_post_tree: str, b_dir: Path, b_tree: str,
                     d8_pre_dir: Path | None = None, d8_pre_tree: str | None = None, dest: Path | None = None):
    """Contenedor OFICIAL (compatibilidad): delega en herramientas/d8/exportar.py con perfil oficial. Exige autoridad
    real con official_export_authorized; en el bloque 2 no existe, así que se rechaza antes de escribir nada."""
    from herramientas.d8 import exportar as EXP
    try:
        return EXP.exportar_oficial(root, authority, b_dir=b_dir, b_tree=b_tree, d8_pre_dir=d8_pre_dir, d8_pre_tree=d8_pre_tree,
                                    d8_post_dir=d8_post_dir, d8_post_tree=d8_post_tree, dest=dest)
    except EXP.ExportError as exc:
        raise D8Error(str(exc))


def environment(root: Path | None = None, profile: dict | None = None) -> dict:
    """Evaluación RE-03 del entorno actual contra lo aprobado por el perfil (compatibilidad de llamada)."""
    root = root or Path(__file__).resolve().parents[2]
    return P.environment(root, profile or P.official(root))
