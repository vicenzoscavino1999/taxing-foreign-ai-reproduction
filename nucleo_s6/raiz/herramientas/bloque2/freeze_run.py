"""Freeze-run: selección inmutable que la corrida oficial de B debe autenticar antes de ejecutar.

La selección vincula: perfil, autoridad, contrato, D7 (árbol + manifiesto), D8_pre (árbol + manifiesto, PASS y
ready_for_freeze_run), código (manifiesto de todos los módulos productores), configuración (hash exacto de RunConfig),
entorno (huella observada + manifiesto/lock aprobados + evidencia), casos (registro, sets base, casos D4, países),
fuentes (dependencias de D7) y la suite / informes A/A-ter que D8_pre autenticó.
- `build_selection` recalcula todo desde bytes y rechaza si D8_pre no auditó ESTE D7, este entorno o este código, o si la
  suite no midió esta configuración.
- `seal` exige `freeze_run_authorized`; escribe <raíz>/<ubicación>/<sha>/{selection,sello}.json vía staging + renombrado
  atómico (inmutable). <ubicación> = location(autoridad): fase6_planes/freeze_runs (histórica) o, con autoridad S6 (raíz sellada por
  P-PREP), salidas_s6/freeze_runs (s6r35; familias.UBICACIONES_S6). `load` exige esa ubicación explícita; nunca busca en otra. En el bloque 2 solo se sella en raíces de ENSAYO aisladas con autoridad
  ficticia (perfil ensayo); el perfil oficial exige autoridad real, que no existe.
- `verify` (llamado por la corrida oficial) recalcula cada vínculo y rechaza con un código específico:
  FREEZE_RUN_ABSENT, FREEZE_RUN_SEAL_INVALID, FREEZE_RUN_OTHER_AUTHORITY, FREEZE_RUN_OTHER_PROFILE,
  FREEZE_RUN_OTHER_D7, FREEZE_RUN_OTHER_D8_PRE, FREEZE_RUN_OTHER_CONTRACT, FREEZE_RUN_CODE_CHANGED,
  FREEZE_RUN_CONFIG_CHANGED, FREEZE_RUN_ENVIRONMENT_CHANGED, FREEZE_RUN_SOURCES_CHANGED, FREEZE_RUN_CASES_CHANGED,
  FREEZE_RUN_INPUT_ALTERED.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import uuid
from pathlib import Path

from herramientas.bloque2 import familias as FAM
from herramientas.bloque2 import perfiles as P

FREEZE_ROOT = "fase6_planes/freeze_runs"                        # histórica (S3/S4/S5 y raíces de ensayo aisladas); se conserva
FREEZE_ROOT_S6 = FAM.UBICACIONES_S6[FREEZE_ROOT]                  # s6r35: raíz S6 sellada (zona de salidas, fuera de la instantánea)
SCHEMA = "paper2b-freeze-run-selection-v1"


class FreezeError(RuntimeError):
    pass


def need(test, code):
    if not test:
        raise FreezeError(code)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"


def rel(root, p) -> str:
    return Path(p).resolve().relative_to(Path(root).resolve()).as_posix()


def location(authority) -> str:
    """Ubicación ÚNICA del sello para esta autoridad (escritura y lectura)."""
    return FAM.ubicacion(FREEZE_ROOT, authority)


def config_sha(cfg_dict: dict) -> str:
    return sha(canon(cfg_dict))


def _pre_deps(pre_manifest: dict) -> dict:
    out = {}
    for d in pre_manifest["input_dependencies"]:
        out.setdefault(d["role"], []).append(d)
    return out


def current_bindings(root, contracts_sha: str, contract_root: str, authority, profile: dict, *, d7_dir, d7_tree: str,
                     d8_pre_dir, d8_pre_tree: str, cfg_dict: dict, code_manifest: dict, env_doc: dict) -> dict:
    """Vínculos recalculados desde bytes (los mismos para construir y para verificar)."""
    root = Path(root)
    d7 = FAM.verify_version(d7_dir, "D7", expected_tree=d7_tree)
    pre = FAM.verify_version(d8_pre_dir, "D8_pre", expected_tree=d8_pre_tree)
    phase = json.loads((Path(d8_pre_dir) / "d8_pre_phase_report.json").read_bytes())
    pdeps = _pre_deps(pre["manifest"])
    d7m = json.loads((Path(d7_dir) / "d7_manifest.json").read_bytes())
    ddeps = {d["role"]: d for d in d7m["input_dependencies"]}
    registry = ddeps.get("registro_casos") or ddeps.get("sintetico_mundo")
    d7phase = json.loads((Path(d7_dir) / "d7_phase_report.json").read_bytes())
    return {
        "schema": SCHEMA,
        "profile": {"kind": profile["kind"], "path": profile.get("path"), "sha256": profile.get("sha256")},
        "authority": {"kind": authority.kind, "package_sha256": authority.package_sha256,
                      "manifest_sha256": authority.manifest_sha256, "fictitious": bool(authority.fictitious)},
        "contract": {"root": contract_root, "sha256": contracts_sha},
        "d7": {"path": rel(root, Path(d7_dir) / "d7_manifest.json"), "tree_sha256": d7_tree, "manifest_sha256": d7["manifest_sha256"],
               "ready_for_b": d7phase.get("ready_for_b")},
        "d8_pre": {"path": rel(root, Path(d8_pre_dir) / "d8_pre_manifest.json"), "tree_sha256": d8_pre_tree,
                   "manifest_sha256": pre["manifest_sha256"], "status": phase.get("status"),
                   "ready_for_freeze_run": phase.get("ready_for_freeze_run"),
                   "audited_d7_tree": (pdeps.get("d7_version") or [{}])[0].get("tree_sha256"),
                   "environment_evidence": [{"path": d["path"], "sha256": d["sha256"]} for d in pdeps.get("environment", [])],
                   "suite_report": [{"path": d["path"], "sha256": d["sha256"]} for d in pdeps.get("suite_report", [])],
                   "a_reports": sorted(({"path": d["path"], "sha256": d["sha256"]} for d in pdeps.get("a_report", [])),
                                       key=lambda x: x["path"])},
        "code": {"manifest_sha256": sha(canon(code_manifest)), "n_files": len(code_manifest.get("files", {}))},
        "configuration": {"sha256": config_sha(cfg_dict), "config": cfg_dict},
        "environment": {"fingerprint_sha256": env_doc["fingerprint_sha256"], "approved": env_doc["approved"],
                        "conforms": env_doc["conforms"]},
        "cases": {"registry": {"path": registry["path"], "sha256": registry["sha256"]} if registry else None,
                  "base_sets": list(cfg_dict.get("base_sets", [])),
                  "d4_model_case_map": {"path": ddeps["d4_model_case_map"]["path"], "sha256": ddeps["d4_model_case_map"]["sha256"]}
                  if "d4_model_case_map" in ddeps else None},
        "sources": sorted(({"role": d["role"], "path": d["path"], "sha256": d["sha256"], "tree_sha256": d.get("tree_sha256")}
                           for d in d7m["input_dependencies"]), key=lambda x: (x["role"], x["path"])),
    }


def build_selection(root, contracts_sha: str, contract_root: str, authority, profile: dict, *, d7_dir, d7_tree, d8_pre_dir,
                    d8_pre_tree, cfg_dict: dict, code_manifest: dict, env_doc: dict) -> dict:
    sel = current_bindings(root, contracts_sha, contract_root, authority, profile, d7_dir=d7_dir, d7_tree=d7_tree,
                           d8_pre_dir=d8_pre_dir, d8_pre_tree=d8_pre_tree, cfg_dict=cfg_dict, code_manifest=code_manifest,
                           env_doc=env_doc)
    need(sel["d7"]["ready_for_b"] is True, "FREEZE_RUN_D7_NOT_READY")
    need(sel["d8_pre"]["status"] == "pass" and sel["d8_pre"]["ready_for_freeze_run"] is True, "FREEZE_RUN_D8_PRE_NOT_PASS")
    need(sel["d8_pre"]["audited_d7_tree"] == d7_tree, "FREEZE_RUN_D8_PRE_AUDITED_OTHER_D7")
    need(env_doc["conforms"], "FREEZE_RUN_ENVIRONMENT_NOT_APPROVED")
    # D8_pre auditó ESTE entorno (evidencia de entorno de D8_pre = huella actual)
    envs = sel["d8_pre"]["environment_evidence"]
    need(len(envs) == 1, "FREEZE_RUN_D8_PRE_WITHOUT_ENVIRONMENT_EVIDENCE")
    from herramientas.bloque2 import entorno as E
    try:
        pre_env = E.verify_evidence(root, envs[0]["path"], envs[0]["sha256"])
    except (OSError, E.EnvironmentError_) as exc:
        raise FreezeError("FREEZE_RUN_D8_PRE_ENVIRONMENT_EVIDENCE:" + str(exc))
    need(pre_env["fingerprint_sha256"] == env_doc["fingerprint_sha256"], "FREEZE_RUN_D8_PRE_AUDITED_OTHER_ENVIRONMENT")
    # la suite que D8_pre autenticó midió ESTE código y ESTA configuración de algoritmo
    suites = sel["d8_pre"]["suite_report"]
    need(len(suites) == 1, "FREEZE_RUN_D8_PRE_WITHOUT_SUITE")
    raw = (Path(root) / suites[0]["path"]).read_bytes()
    need(sha(raw) == suites[0]["sha256"], "FREEZE_RUN_SUITE_ALTERED")
    rep = json.loads(raw)
    need(rep.get("code_manifest_sha256") == sel["code"]["manifest_sha256"], "FREEZE_RUN_SUITE_OTHER_CODE")
    need(rep.get("environment_fingerprint_sha256") == env_doc["fingerprint_sha256"], "FREEZE_RUN_SUITE_OTHER_ENVIRONMENT")
    measured = {sha(canon(c)) for c in rep.get("measured_sup_configs", [])}
    need(sha(canon(cfg_dict["sup"])) in measured, "FREEZE_RUN_SUITE_DID_NOT_MEASURE_THIS_CONFIGURATION")
    return sel


def seal(root, selection: dict, authority, *, created_at: str) -> dict:
    """Sella la selección (inmutable). Perfil ensayo: solo raíz aislada y autoridad ficticia."""
    authority.require("freeze_run_authorized")
    prof = selection["profile"]
    if prof["kind"] == "ensayo":
        need(authority.fictitious, "FREEZE_RUN_TRIAL_REQUIRES_FICTITIOUS_AUTHORITY")
        need(P.is_isolated(root), "FREEZE_RUN_TRIAL_REQUIRES_ISOLATED_ROOT")
    else:
        need(not authority.fictitious, "FREEZE_RUN_OFFICIAL_REJECTS_FICTITIOUS_AUTHORITY")
    need(selection["authority"]["package_sha256"] == authority.package_sha256, "FREEZE_RUN_OTHER_AUTHORITY")
    sraw = canon(selection)
    ssha = sha(sraw)
    seal_doc = {"selection_sha256": ssha, "authority_package_sha256": authority.package_sha256,
                "authority_manifest_sha256": authority.manifest_sha256, "scope_flag": "freeze_run_authorized",
                "fictitious": bool(authority.fictitious), "profile_kind": prof["kind"], "created_at": created_at,
                "note": ("ENSAYO FICTICIO: no es un freeze-run real" if prof["kind"] == "ensayo" else "freeze-run")}
    craw = canon(seal_doc)
    base = Path(root) / location(authority)
    dest = base / ssha
    if dest.exists():
        need((dest / "selection.json").read_bytes() == sraw, "FREEZE_RUN_EXISTING_DIFFERENT")
        return {"selection_sha256": ssha, "path": dest, "seal_sha256": sha((dest / "sello.json").read_bytes()), "created": False}
    staging = base / ".staging" / uuid.uuid4().hex
    staging.mkdir(parents=True)
    try:
        (staging / "selection.json").write_bytes(sraw)
        (staging / "sello.json").write_bytes(craw)
        os.replace(staging, dest)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
        parent = base / ".staging"
        if parent.exists() and not any(parent.iterdir()):
            parent.rmdir()
    return {"selection_sha256": ssha, "path": dest, "seal_sha256": sha(craw), "created": True}


def load(root, selection_sha256: str | None, freeze_root: str = FREEZE_ROOT) -> dict:
    need(selection_sha256 is not None, "FREEZE_RUN_ABSENT")
    need(freeze_root in (FREEZE_ROOT, FREEZE_ROOT_S6) and re.fullmatch(r"[0-9a-f]{64}", str(selection_sha256)) is not None,
         "FREEZE_RUN_INVALID_LOCATION")
    d = Path(root) / freeze_root / selection_sha256
    need((d / "selection.json").is_file() and (d / "sello.json").is_file(), "FREEZE_RUN_ABSENT")
    sraw = (d / "selection.json").read_bytes()
    need(sha(sraw) == selection_sha256, "FREEZE_RUN_INPUT_ALTERED")
    sel = json.loads(sraw)
    need(canon(sel) == sraw and sel.get("schema") == SCHEMA, "FREEZE_RUN_SEAL_INVALID")
    seal_doc = json.loads((d / "sello.json").read_bytes())
    need(seal_doc.get("selection_sha256") == selection_sha256 and seal_doc.get("scope_flag") == "freeze_run_authorized",
         "FREEZE_RUN_SEAL_INVALID")
    need(set(os.listdir(d)) == {"selection.json", "sello.json"}, "FREEZE_RUN_SEAL_INVALID")
    return {"selection": sel, "seal": seal_doc, "path": d}


def verify(root, selection_sha256: str | None, contracts_sha: str, contract_root: str, authority, profile: dict, *, d7_dir,
           d7_tree: str, d8_pre_dir, d8_pre_tree: str, cfg_dict: dict, code_manifest: dict, env_doc: dict) -> dict:
    fr = load(root, selection_sha256, location(authority))
    sel, seal_doc = fr["selection"], fr["seal"]
    need(seal_doc["authority_package_sha256"] == authority.package_sha256 and
         seal_doc["authority_manifest_sha256"] == authority.manifest_sha256 and
         sel["authority"]["package_sha256"] == authority.package_sha256, "FREEZE_RUN_OTHER_AUTHORITY")
    need(sel["profile"] == {"kind": profile["kind"], "path": profile.get("path"), "sha256": profile.get("sha256")} and
         seal_doc["profile_kind"] == profile["kind"], "FREEZE_RUN_OTHER_PROFILE")
    try:
        cur = current_bindings(root, contracts_sha, contract_root, authority, profile, d7_dir=d7_dir, d7_tree=d7_tree,
                               d8_pre_dir=d8_pre_dir, d8_pre_tree=d8_pre_tree, cfg_dict=cfg_dict, code_manifest=code_manifest,
                               env_doc=env_doc)
    except FAM.FamilyError as exc:
        raise FreezeError("FREEZE_RUN_INPUT_ALTERED:" + str(exc))
    need(cur["contract"] == sel["contract"], "FREEZE_RUN_OTHER_CONTRACT")
    need(cur["d7"] == sel["d7"], "FREEZE_RUN_OTHER_D7")
    need(cur["d8_pre"] == sel["d8_pre"], "FREEZE_RUN_OTHER_D8_PRE")
    need(cur["code"] == sel["code"], "FREEZE_RUN_CODE_CHANGED")
    need(cur["configuration"] == sel["configuration"], "FREEZE_RUN_CONFIG_CHANGED")
    need(cur["environment"] == sel["environment"] and env_doc["conforms"], "FREEZE_RUN_ENVIRONMENT_CHANGED")
    need(cur["cases"] == sel["cases"], "FREEZE_RUN_CASES_CHANGED")
    need(cur["sources"] == sel["sources"], "FREEZE_RUN_SOURCES_CHANGED")
    for s in sel["sources"] + [x for x in (sel["cases"]["registry"], sel["cases"]["d4_model_case_map"]) if x]:
        q = Path(root) / s["path"]
        need(q.is_file() and sha(q.read_bytes()) == s["sha256"], "FREEZE_RUN_INPUT_ALTERED:" + s["path"])
    need(cur == sel, "FREEZE_RUN_SELECTION_MISMATCH")
    return {"selection": sel, "selection_sha256": selection_sha256, "path": fr["path"],
            "seal_sha256": sha((fr["path"] / "sello.json").read_bytes())}


def dependency(root, fr: dict) -> dict:
    """Dependencia 'freeze_run' que la corrida y los auditores registran."""
    return {"role": "freeze_run", "path": rel(root, fr["path"] / "selection.json"), "sha256": fr["selection_sha256"],
            "tree_sha256": None, "version": fr["selection"]["profile"]["kind"], "authority_package_sha256":
            fr["selection"]["authority"]["package_sha256"]}
