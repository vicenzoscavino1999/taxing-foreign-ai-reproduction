"""Exportación verificable de resultados auditados (bloque 2: núcleo implementado; ruta oficial bloqueada por autoridad).

Paquete de exportación = selección EXACTA y trazable:
  B/        árbol B auditado (bytes idénticos, incluido b_manifest.json)
  D8_pre/   árbol D8_pre que habilitó el freeze-run
  D8_post/  árbol D8_post que auditó ESE B contra ESE D8_pre (ready_for_export)
  freeze_run/selection.json + sello.json   selección sellada que B autenticó
  cifras/referencias.json   cada cifra exportada = fila B referida por D8_post (result_references), con su hash de fila
                            y su source_chain_sha256 recomputado
  trazabilidad.json          cadena autoridad -> freeze -> D7 -> D8_pre -> B -> D8_post (hashes)
  export_manifest.json       archivos, tamaños, SHA-256, árbol, perfil y rótulo (FICTICIO en ensayos)
Emisión atómica: todo se escribe y verifica en <dest>/.staging/<uuid>/ y solo entonces se renombra a <dest>/<árbol>/.
Ante cualquier error el staging se elimina: no hay emisión parcial. `verify_package` reverifica todo desde el paquete;
`reconstruct` rematerializa las familias en otra raíz y comprueba que reproducen los mismos árboles.
Perfiles: `exportar_ensayo` (autoridad FICTICIA, perfil de ensayo, raíz aislada, destino dentro de ella) y
`exportar_oficial` (autoridad real con official_export_authorized; B 'official'; D8_post del perfil oficial). No hay
conversión de uno a otro: el perfil queda en el manifiesto y el verificador oficial rechaza paquetes de ensayo.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import uuid
from pathlib import Path

from paper2b import keys as K
from herramientas.bloque2 import autoridad as A
from herramientas.bloque2 import familias as FAM
from herramientas.bloque2 import perfiles as P

SCHEMA = "paper2b-export-package-v1"
OFFICIAL_DEST = "fase2_datos/exportacion_oficial"
TRIAL_DEST = "ensayo/exportaciones"
FAMILY_DIRS = {"B": "B", "D8_pre": "D8_pre", "D8_post": "D8_post"}
_FAIL_HOOK = None          # SOLO pruebas: función llamada durante el staging para simular una interrupción


class ExportError(RuntimeError):
    pass


def need(test, code):
    if not test:
        raise ExportError(code)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canon(obj) -> bytes:
    return K.canon(obj) + b"\n"


def _rel(root, p) -> str:
    return Path(p).resolve().relative_to(Path(root).resolve()).as_posix()


def _files_of(version_dir: Path) -> dict:
    return {q.relative_to(version_dir).as_posix(): q.read_bytes() for q in sorted(Path(version_dir).rglob("*")) if q.is_file()}


def _tree(entries: list) -> str:
    return K.H([[e["path"], e["sha256"], e["bytes"]] for e in entries])


def _select(root: Path, profile: dict, authority, *, b_dir, b_tree, d8_pre_dir, d8_pre_tree, d8_post_dir, d8_post_tree) -> dict:
    """Verifica la selección exacta y devuelve los tres árboles + freeze; rechaza con códigos específicos."""
    from herramientas.bloque2 import freeze_run as FR
    try:
        b = FAM.verify_version(b_dir, "B", expected_tree=b_tree)
        post = FAM.verify_version(d8_post_dir, "D8_post", expected_tree=d8_post_tree)
    except (FAM.FamilyError, OSError, ValueError) as exc:
        raise ExportError("EXPORT_EVIDENCE_ALTERED:" + str(exc))
    pdeps = {d["role"]: d for d in post["manifest"]["input_dependencies"]}
    bdep = pdeps.get("b_version")
    need(bdep is not None and bdep["tree_sha256"] == b_tree and bdep["sha256"] == b["manifest_sha256"],
         "EXPORT_SELECTION_MISMATCH:D8_POST_AUDITED_ANOTHER_B")
    predep = pdeps.get("d8_pre_version")
    if d8_pre_tree is None and predep is not None:
        d8_pre_tree = predep["tree_sha256"]
        d8_pre_dir = Path(root) / Path(predep["path"]).parent
    need(d8_pre_dir is not None, "EXPORT_D8_PRE_NOT_SELECTED")
    try:
        pre = FAM.verify_version(d8_pre_dir, "D8_pre", expected_tree=d8_pre_tree)
    except (FAM.FamilyError, OSError, ValueError) as exc:
        raise ExportError("EXPORT_EVIDENCE_ALTERED:" + str(exc))
    need(predep is not None and predep["tree_sha256"] == d8_pre_tree and predep["sha256"] == pre["manifest_sha256"],
         "EXPORT_SELECTION_MISMATCH:D8_POST_USED_ANOTHER_D8_PRE")
    rm = json.loads((Path(b_dir) / "run_manifest.json").read_bytes())
    need(rm["status"] == "complete", "EXPORT_RUN_INCOMPLETE")
    want_class = "official" if profile["kind"] == "oficial" else "trial_frozen"
    need(rm["run_class"] == want_class, "EXPORT_RUN_CLASS_NOT_" + want_class.upper())
    phase = json.loads((Path(d8_post_dir) / "d8_post_phase_report.json").read_bytes())
    need(phase["status"] == "pass" and phase["ready_for_export"] is True, "EXPORT_AUDIT_INVALID:D8_POST_NOT_READY")
    prof_dep = pdeps.get("perfil_ensayo")
    need((prof_dep or {}).get("sha256") == profile.get("sha256"), "EXPORT_AUDIT_OF_ANOTHER_PROFILE")
    bdeps = {d["role"]: d for d in b["manifest"]["input_dependencies"]}
    fdep = bdeps.get("freeze_run")
    need(fdep is not None, "EXPORT_B_WITHOUT_FREEZE_RUN")
    try:
        fr = FR.load(root, fdep["sha256"], FR.location(authority))
    except FR.FreezeError as exc:
        raise ExportError("EXPORT_EVIDENCE_ALTERED:" + str(exc))
    need(fdep.get("path") == FR.rel(root, fr["path"] / "selection.json"), "EXPORT_SELECTION_MISMATCH:FREEZE_RUN_PATH")
    sel = fr["selection"]
    need(sel["d8_pre"]["tree_sha256"] == d8_pre_tree and sel["d7"]["tree_sha256"] == bdeps["d7_version"]["tree_sha256"],
         "EXPORT_SELECTION_MISMATCH:FREEZE_RUN")
    return {"b": b, "pre": pre, "post": post, "fr": fr, "rm": rm, "b_dir": Path(b_dir), "pre_dir": Path(d8_pre_dir),
            "post_dir": Path(d8_post_dir), "trees": {"B": b_tree, "D8_pre": d8_pre_tree, "D8_post": d8_post_tree}}


def _figures(contracts, sel: dict) -> list:
    """Cifras exportadas: exactamente las filas B que D8_post referenció, con hash de fila y cadena recomputada."""
    post_dir, b_dir = sel["post_dir"], sel["b_dir"]
    refs = contracts.read_csv(post_dir / contracts.C["tables"]["result_references"]["file"].split("/", 1)[1], "result_references")
    tables = {}
    out = []
    for r in refs:
        t = r["table_name"]
        if t not in tables:
            rows = contracts.read_csv(b_dir / contracts.C["tables"][t]["file"].split("/", 1)[1], t)
            pk = contracts.C["tables"][t]["primary_key"]
            tables[t] = {tuple(x[k] for k in pk): x for x in rows}
        pk = contracts.C["tables"][t]["primary_key"]
        row = tables[t].get(tuple(r["record_pk"][k] for k in pk))
        need(row is not None, "EXPORT_REFERENCE_UNRESOLVED:" + r["result_ref"])
        need(r["b_manifest_sha256"] == sel["b"]["manifest_sha256"], "EXPORT_REFERENCE_OTHER_B")
        out.append({"result_ref": r["result_ref"], "table": t, "record_pk": r["record_pk"], "row": row,
                    "row_sha256": K.H(row), "source_chain_sha256": r["source_chain_sha256"]})
    return sorted(out, key=lambda x: x["result_ref"])


def build_package(root, contracts, authority, profile: dict, *, b_dir, b_tree, d8_pre_dir, d8_pre_tree, d8_post_dir,
                  d8_post_tree, dest, created_at: str) -> dict:
    """Núcleo común (oficial y ensayo). Escribe <dest>/<árbol>/ atómicamente o no escribe nada."""
    root, dest = Path(root), Path(dest)
    sel = _select(root, profile, authority, b_dir=b_dir, b_tree=b_tree, d8_pre_dir=d8_pre_dir, d8_pre_tree=d8_pre_tree,
                  d8_post_dir=d8_post_dir, d8_post_tree=d8_post_tree)
    files = {}
    for fam, d in (("B", sel["b_dir"]), ("D8_pre", sel["pre_dir"]), ("D8_post", sel["post_dir"])):
        for rp, data in _files_of(d).items():
            files[f"{FAMILY_DIRS[fam]}/{rp}"] = data
    for name in ("selection.json", "sello.json"):
        files["freeze_run/" + name] = (sel["fr"]["path"] / name).read_bytes()
    figs = _figures(contracts, sel)
    files["cifras/referencias.json"] = canon(figs)
    fsel = sel["fr"]["selection"]
    trace = {"authority": {"kind": authority.kind, "package_sha256": authority.package_sha256,
                           "manifest_sha256": authority.manifest_sha256, "fictitious": bool(authority.fictitious)},
             "freeze_run_selection_sha256": sel["fr"]["selection"] and sha(files["freeze_run/selection.json"]),
             "d7_tree_sha256": fsel["d7"]["tree_sha256"], "d8_pre_tree_sha256": sel["trees"]["D8_pre"],
             "b_tree_sha256": sel["trees"]["B"], "d8_post_tree_sha256": sel["trees"]["D8_post"],
             "b_manifest_sha256": sel["b"]["manifest_sha256"], "d8_pre_manifest_sha256": sel["pre"]["manifest_sha256"],
             "d8_post_manifest_sha256": sel["post"]["manifest_sha256"], "contract_sha256": fsel["contract"]["sha256"],
             "code_manifest_sha256": fsel["code"]["manifest_sha256"], "configuration_sha256": fsel["configuration"]["sha256"],
             "environment_fingerprint_sha256": fsel["environment"]["fingerprint_sha256"], "run_id": sel["rm"]["run_id"],
             "n_figures": len(figs)}
    files["trazabilidad.json"] = canon(trace)
    if profile["kind"] == "ensayo":
        files["LEEME_FICTICIO.txt"] = ("PAQUETE DE ENSAYO FICTICIO: autoridad ficticia, datos sintéticos y perfil de ensayo. "
                                       "No es una exportación oficial ni un resultado nacional.\n").encode("utf-8")
    entries = [{"path": k, "sha256": sha(v), "bytes": len(v)} for k, v in sorted(files.items())]
    tree = _tree(entries)
    manifest = {"schema": SCHEMA, "profile": {"kind": profile["kind"], "path": profile.get("path"), "sha256": profile.get("sha256")},
                "label": "FICTICIO" if profile["kind"] == "ensayo" else "OFICIAL", "tree_sha256": tree,
                "selection": {"b_tree_sha256": sel["trees"]["B"], "d8_pre_tree_sha256": sel["trees"]["D8_pre"],
                              "d8_post_tree_sha256": sel["trees"]["D8_post"],
                              "freeze_run_selection_sha256": trace["freeze_run_selection_sha256"]},
                "authority_package_sha256": authority.package_sha256, "created_at": created_at, "files": entries}
    mraw = canon(manifest)
    final = dest / tree
    if final.exists():
        verify_package(final)
        need((final / "export_manifest.json").read_bytes() == mraw, "EXPORT_EXISTING_PACKAGE_DIFFERENT")
        return {"path": final, "tree_sha256": tree, "manifest_sha256": sha(mraw), "created": False}
    staging = dest / ".staging" / uuid.uuid4().hex
    staging.mkdir(parents=True)
    try:
        for k, v in sorted(files.items()):
            q = staging / k
            q.parent.mkdir(parents=True, exist_ok=True)
            q.write_bytes(v)
            if _FAIL_HOOK is not None:
                _FAIL_HOOK(k)
        (staging / "export_manifest.json").write_bytes(mraw)
        verify_package(staging)
        os.replace(staging, final)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
        parent = dest / ".staging"
        if parent.exists() and not any(parent.iterdir()):
            parent.rmdir()
    verify_package(final)
    return {"path": final, "tree_sha256": tree, "manifest_sha256": sha(mraw), "created": True}


def verify_package(pkg, *, require_profile: str | None = None) -> dict:
    """Reverifica un paquete solo desde sus bytes: manifiesto, árbol, familias internas, cadena y cifras."""
    pkg = Path(pkg)
    raw = (pkg / "export_manifest.json").read_bytes()
    m = json.loads(raw)
    need(canon(m) == raw and m.get("schema") == SCHEMA, "EXPORT_PACKAGE_MANIFEST_INVALID")
    if require_profile is not None:
        need(m["profile"]["kind"] == require_profile, "EXPORT_PACKAGE_PROFILE_" + m["profile"]["kind"].upper())
    listed = {e["path"]: e for e in m["files"]}
    present = {q.relative_to(pkg).as_posix() for q in pkg.rglob("*") if q.is_file()} - {"export_manifest.json"}
    need(present == set(listed), "EXPORT_PACKAGE_FILES:" + ",".join(sorted(present ^ set(listed)))[:200])
    for k, e in listed.items():
        data = (pkg / k).read_bytes()
        need(sha(data) == e["sha256"] and len(data) == e["bytes"], "EXPORT_PACKAGE_FILE_ALTERED:" + k)
    need(_tree(m["files"]) == m["tree_sha256"], "EXPORT_PACKAGE_TREE")
    trees = {}
    for fam in ("B", "D8_pre", "D8_post"):
        try:
            trees[fam] = FAM.verify_version(pkg / FAMILY_DIRS[fam], fam)
        except (FAM.FamilyError, OSError, ValueError) as exc:
            raise ExportError("EXPORT_PACKAGE_FAMILY_INVALID:" + fam + ":" + str(exc))
    sel = m["selection"]
    need(trees["B"]["tree_sha256"] == sel["b_tree_sha256"] and trees["D8_pre"]["tree_sha256"] == sel["d8_pre_tree_sha256"]
         and trees["D8_post"]["tree_sha256"] == sel["d8_post_tree_sha256"], "EXPORT_PACKAGE_SELECTION")
    pdeps = {d["role"]: d for d in trees["D8_post"]["manifest"]["input_dependencies"]}
    need(pdeps["b_version"]["tree_sha256"] == sel["b_tree_sha256"] and pdeps["d8_pre_version"]["tree_sha256"] ==
         sel["d8_pre_tree_sha256"], "EXPORT_PACKAGE_CHAIN")
    fsel = (pkg / "freeze_run/selection.json").read_bytes()
    need(sha(fsel) == sel["freeze_run_selection_sha256"], "EXPORT_PACKAGE_FREEZE")
    bdeps = {d["role"]: d for d in trees["B"]["manifest"]["input_dependencies"]}
    need(bdeps["freeze_run"]["sha256"] == sel["freeze_run_selection_sha256"], "EXPORT_PACKAGE_FREEZE_NOT_B")
    need(json.loads(fsel)["d8_pre"]["tree_sha256"] == sel["d8_pre_tree_sha256"], "EXPORT_PACKAGE_FREEZE_D8_PRE")
    phase = json.loads((pkg / "D8_post/d8_post_phase_report.json").read_bytes())
    need(phase["ready_for_export"] is True and phase["status"] == "pass", "EXPORT_PACKAGE_AUDIT_NOT_READY")
    figs = json.loads((pkg / "cifras/referencias.json").read_bytes())
    for f in figs:
        need(K.H(f["row"]) == f["row_sha256"], "EXPORT_PACKAGE_FIGURE_ALTERED:" + f["result_ref"])
    return {"manifest": m, "trees": {k: v["tree_sha256"] for k, v in trees.items()}, "n_figures": len(figs)}


def reconstruct(pkg, out_root) -> dict:
    """Rematerializa B/D8_pre/D8_post desde el paquete en <out_root>/<familia>/versions/<árbol>/ y verifica los árboles."""
    info = verify_package(pkg)
    out = {}
    for fam in ("B", "D8_pre", "D8_post"):
        src = Path(pkg) / FAMILY_DIRS[fam]
        tree = info["trees"][fam]
        dst = Path(out_root) / fam / "versions" / tree
        if not dst.exists():
            shutil.copytree(src, dst)
        out[fam] = FAM.verify_version(dst, fam, expected_tree=tree)["tree_sha256"]
    need(out == info["trees"], "EXPORT_RECONSTRUCTION_MISMATCH")
    return out


def exportar_ensayo(root, contracts, authority, *, profile_path: str, profile_sha: str, b_dir, b_tree, d8_pre_dir=None,
                    d8_pre_tree=None, d8_post_dir, d8_post_tree, created_at: str, dest=None) -> dict:
    """ENSAYO: autoridad ficticia, perfil de ensayo y destino dentro de la raíz aislada. Paquete rotulado FICTICIO."""
    root = Path(root)
    authority.require("official_export_authorized")
    try:
        profile = P.load(root, profile_path, profile_sha, anclas=authority.anclas_externas or None)
        P.require_authority(profile, authority)
    except (P.ProfileError, OSError) as exc:
        raise ExportError("EXPORT_TRIAL_PROFILE:" + str(exc))
    need(profile["kind"] == "ensayo", "EXPORT_TRIAL_REQUIRES_TRIAL_PROFILE")
    dest = Path(dest) if dest is not None else root / TRIAL_DEST
    need(Path(dest).resolve().is_relative_to(root.resolve()) and P.is_isolated(root), "EXPORT_TRIAL_DEST_NOT_ISOLATED")
    need(not Path(dest).resolve().is_relative_to((root / OFFICIAL_DEST).resolve()), "EXPORT_TRIAL_INTO_OFFICIAL_DEST")
    return build_package(root, contracts, authority, profile, b_dir=b_dir, b_tree=b_tree, d8_pre_dir=d8_pre_dir,
                         d8_pre_tree=d8_pre_tree, d8_post_dir=d8_post_dir, d8_post_tree=d8_post_tree, dest=dest,
                         created_at=created_at)


def exportar_oficial(root, authority, *, b_dir, b_tree, d8_post_dir, d8_post_tree, d8_pre_dir=None, d8_pre_tree=None,
                     dest=None, contracts=None, created_at: str | None = None) -> dict:
    """Contenedor OFICIAL. Rechaza toda operación no autorizada ANTES de escribir: autoridad real con
    official_export_authorized, perfil oficial, B 'official' completo, D8_post oficial ready_for_export y freeze-run."""
    authority.require("official_export_authorized")
    need(not authority.fictitious, "EXPORT_FICTITIOUS_AUTHORITY")
    try:
        A.autoridad_real_verificada(root, authority, facultad="official_export_authorized")
    except A.AuthorityError as exc:
        raise ExportError("EXPORT_REQUIRES_VERIFIED_REAL_AUTHORITY:" + str(exc))
    root = Path(root)
    if contracts is None:
        from herramientas.s3.validadores.core import Contracts
        contracts = Contracts.load(root / authority.contract_root, authority.contract_sha256)
    return build_package(root, contracts, authority, P.official(root, anclas=authority.anclas_externas or None), b_dir=b_dir, b_tree=b_tree, d8_pre_dir=d8_pre_dir,
                         d8_pre_tree=d8_pre_tree, d8_post_dir=d8_post_dir, d8_post_tree=d8_post_tree,
                         dest=Path(dest) if dest is not None else root / OFFICIAL_DEST, created_at=created_at or FAM.now())
