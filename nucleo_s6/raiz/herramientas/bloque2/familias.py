"""Familias versionadas D7/B/D8 (DB-09; CONTRATOS_D7_B_D8 'tree', manifiestos, punteros y recibos).

Convención nueva (no altera familias históricas): tree_sha256 = H(lista ordenada {path,sha256,bytes}) de los
archivos científicos; el manifiesto enumera {path,sha256,bytes,rows}, no se incluye a sí mismo, ni puntero, ni recibo.
Publicación: staging aislado -> verificación completa -> movimiento a versions/<tree>/ -> reverificación de bytes.
Puntero y recibo de promoción SOLO con evidencia de acción aprobada; si falla el último paso, el puntero previo sigue.
Archivos desconocidos dentro del árbol se rechazan.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from paper2b.keys import H, canon

MANIFEST_NAME = {"D7": "d7_manifest.json", "B": "b_manifest.json", "D8_pre": "d8_pre_manifest.json",
                 "D8_post": "d8_post_manifest.json"}
PRODUCT_TYPE = {"D7": "d7_calibracion", "B": "b_frontera", "D8_pre": "d8_pre_auditoria", "D8_post": "d8_post_auditoria"}
FAMILY_ROOT = {"D7": "fase2_datos/d7_calibracion", "B": "fase2_datos/b_frontera", "D8_pre": "fase2_datos/d8/pre",
               "D8_post": "fase2_datos/d8/post"}
EXCLUDED = {"active_product.json", "promotion_receipt.json"}

# s6r35: con la raíz S6 SELLADA (P-PREP v2 verifica la instantánea completa) nada posterior a la emisión se escribe dentro de su alcance.
# Los productos de UBICACIÓN FIJA de la cadena posterior van a la zona de salidas (dentro de la raíz, fuera del alcance), según esta tabla
# CERRADA. La zona la decide la autoridad verificada (sucesión S6 registrada por autoridad.from_s6); con cualquier otra autoridad se
# conserva la ruta histórica. Nunca se busca un producto en varias carpetas. D7, D8 (out_root) y exportación (dest) siguen con destino
# explícito.
ZONA_SALIDAS_S6 = "salidas_s6"
UBICACIONES_S6 = {"fase6_planes/freeze_runs": ZONA_SALIDAS_S6 + "/freeze_runs",
                  "fase2_datos/b_frontera": ZONA_SALIDAS_S6 + "/b_frontera",
                  "fase2_datos/d8/entradas": ZONA_SALIDAS_S6 + "/d8/entradas"}


def autoridad_s6(authority) -> bool:
    return "s6" in (getattr(authority, "succession", None) or {})


def ubicacion(rel_historica: str, authority) -> str:
    """Ruta (relativa a la raíz) de un producto de ubicación fija para ESTA autoridad: la declarada en UBICACIONES_S6 con autoridad S6;
    la histórica en otro caso."""
    if not autoridad_s6(authority):
        return rel_historica
    need(rel_historica in UBICACIONES_S6, "UBICACION_S6_NO_DECLARADA:" + rel_historica)
    return UBICACIONES_S6[rel_historica]


class FamilyError(RuntimeError):
    pass


def need(test, code):
    if not test:
        raise FamilyError(code)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def entries_for(files: dict) -> list:
    """files: path -> (bytes, rows|None)."""
    return sorted(({"path": p, "sha256": sha(b), "bytes": len(b), "rows": r} for p, (b, r) in files.items()),
                  key=lambda e: e["path"])


def tree_of(entries: list) -> str:
    return H([{k: e[k] for k in ("path", "sha256", "bytes")} for e in entries])


def manifest(contracts, family: str, *, run_id: str, producer_path: str, producer_sha256: str, authority_package: str,
             authority_manifest: str, contract_sha256: str, dependencies: list, entries: list, phase_status: str,
             created_at: str | None = None) -> bytes:
    from paper2b.tables import json_doc_bytes
    deps = sorted(dependencies, key=lambda d: (d["role"], d["path"]))
    need(len({(d["role"], d["path"]) for d in deps}) == len(deps), "DEPENDENCIA_DUPLICADA")
    for d in deps:
        need(set(d) == {"role", "path", "sha256", "tree_sha256", "version", "authority_package_sha256"}, "DEPENDENCIA_EXACTA")
    doc_name = family + "_manifest"
    obj = {"schema_version": 1, "product_type": PRODUCT_TYPE[family], "run_id": run_id, "created_at": created_at or now(),
           "producer_path": producer_path, "producer_sha256": producer_sha256, "authority_package_sha256": authority_package,
           "authority_manifest_sha256": authority_manifest, "contract_sha256": contract_sha256, "input_dependencies": deps,
           "files": entries, "tree_sha256": tree_of(entries), "phase_status": phase_status}
    return json_doc_bytes(contracts, doc_name, obj)


def write_version(family_root: Path, family: str, files: dict, manifest_bytes: bytes) -> dict:
    """Staging aislado -> versions/<tree>/ (inmutable). No toca el puntero."""
    family_root = Path(family_root)
    entries = entries_for(files)
    tree = tree_of(entries)
    m = json.loads(manifest_bytes)
    need(m["tree_sha256"] == tree and m["files"] == entries, "MANIFIESTO_Y_ARCHIVOS_INCOHERENTES")
    dest = family_root / "versions" / tree
    if dest.exists():
        verify_version(dest, family, expected_tree=tree)
        need((dest / MANIFEST_NAME[family]).read_bytes() == manifest_bytes, "VERSION_EXISTENTE_DISTINTA")
        return {"tree_sha256": tree, "path": dest, "manifest_sha256": sha(manifest_bytes), "created": False}
    staging = family_root / ".staging" / uuid.uuid4().hex
    staging.mkdir(parents=True)
    try:
        for rel, (data, _) in files.items():
            q = staging / rel
            q.parent.mkdir(parents=True, exist_ok=True)
            q.write_bytes(data)
            need(q.read_bytes() == data, "ESCRITURA_STAGING")
        (staging / MANIFEST_NAME[family]).write_bytes(manifest_bytes)
        verify_version(staging, family, expected_tree=tree)
        dest.parent.mkdir(parents=True, exist_ok=True)
        os.replace(staging, dest)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
        parent = family_root / ".staging"
        if parent.exists() and not any(parent.iterdir()):
            parent.rmdir()
    verify_version(dest, family, expected_tree=tree)
    return {"tree_sha256": tree, "path": dest, "manifest_sha256": sha(manifest_bytes), "created": True}


def verify_version(path: Path, family: str, *, expected_tree: str | None = None) -> dict:
    path = Path(path)
    raw = (path / MANIFEST_NAME[family]).read_bytes()
    m = json.loads(raw)
    need(canon(m) + b"\n" == raw, "MANIFIESTO_NO_CANONICO")
    need(m["product_type"] == PRODUCT_TYPE[family] and m["schema_version"] == 1, "MANIFIESTO_FAMILIA")
    listed = {e["path"]: e for e in m["files"]}
    present = {q.relative_to(path).as_posix() for q in path.rglob("*") if q.is_file()}
    present.discard(MANIFEST_NAME[family])
    need(present == set(listed), "ARCHIVOS_DESCONOCIDOS_O_AUSENTES:" + ",".join(sorted(present ^ set(listed))))
    need(not (present & EXCLUDED), "PUNTERO_O_RECIBO_DENTRO_DEL_ARBOL")
    for rel, e in listed.items():
        data = (path / rel).read_bytes()
        need(sha(data) == e["sha256"] and len(data) == e["bytes"], "ARCHIVO_ALTERADO:" + rel)
    need(tree_of(m["files"]) == m["tree_sha256"], "ARBOL_ALTERADO")
    if expected_tree is not None:
        need(m["tree_sha256"] == expected_tree, "ARBOL_DISTINTO_DEL_SELECCIONADO")
    return {"tree_sha256": m["tree_sha256"], "manifest_sha256": sha(raw), "manifest": m, "path": path}


def promote(contracts, family_root: Path, family: str, tree: str, *, authority_id: str, approved_action_evidence_sha256: str,
            checks_manifest_sha256: str, approval_is_real: bool) -> dict:
    """Puntero + recibo de promoción. Sin aprobación real solo en raíces de prueba (approval_is_real=False y marca)."""
    from paper2b.tables import json_doc_bytes
    family_root = Path(family_root)
    info = verify_version(family_root / "versions" / tree, family, expected_tree=tree)
    pointer_path = family_root / "active_product.json"
    old = json.loads(pointer_path.read_bytes()) if pointer_path.exists() else None
    history = (old["immutable_tree_sha256s"] if old else []) + ([tree] if not old or tree not in old["immutable_tree_sha256s"] else [])
    if old and tree in old["immutable_tree_sha256s"]:
        history = [t for t in old["immutable_tree_sha256s"] if t != tree] + [tree]
    receipt = {"receipt_id": f"RCPT:{family}:{tree[:16]}:{uuid.uuid4().hex[:8]}", "product_type": PRODUCT_TYPE[family],
               "new_tree_sha256": tree, "old_tree_sha256": old["active_tree_sha256"] if old else None,
               "authority_id": authority_id, "checks_manifest_sha256": checks_manifest_sha256,
               "approved_action_evidence_sha256": approved_action_evidence_sha256, "promoted_at": now()}
    rraw = json_doc_bytes(contracts, family + "_promotion", receipt)
    rdir = family_root / "promotion_receipts"
    rdir.mkdir(parents=True, exist_ok=True)
    rpath = rdir / (tree + ".json")
    rpath.write_bytes(rraw)
    pointer = {"schema_version": 1, "product_type": PRODUCT_TYPE[family], "active_tree_sha256": tree,
               "active_relative_path": "versions/" + tree, "active_manifest_sha256": info["manifest_sha256"],
               "predecessor_reference": ({"path": "versions/" + old["active_tree_sha256"] + "/" + MANIFEST_NAME[family],
                                          "sha256": old["active_manifest_sha256"], "tree_sha256": old["active_tree_sha256"]}
                                         if old else None),
               "promotion_receipt_sha256": sha(rraw), "immutable_tree_sha256s": history}
    praw = json_doc_bytes(contracts, family + "_pointer", pointer)
    temp = pointer_path.with_name("active_product.json.tmp-" + uuid.uuid4().hex[:8])
    temp.write_bytes(praw)
    os.replace(temp, pointer_path)
    return {"pointer_sha256": sha(praw), "receipt_sha256": sha(rraw), "approval_is_real": approval_is_real}


def read_active(family_root: Path, family: str, *, expected_tree: str) -> dict:
    p = json.loads((Path(family_root) / "active_product.json").read_bytes())
    need(p["active_tree_sha256"] == expected_tree, "PUNTERO_NO_SELECCIONA_EL_ARBOL_PEDIDO")
    info = verify_version(Path(family_root) / p["active_relative_path"], family, expected_tree=expected_tree)
    need(p["active_manifest_sha256"] == info["manifest_sha256"], "PUNTERO_MANIFIESTO")
    rraw = (Path(family_root) / "promotion_receipts" / (expected_tree + ".json")).read_bytes()
    need(sha(rraw) == p["promotion_receipt_sha256"], "RECIBO_ALTERADO")
    return dict(info, pointer=p)


def entries_for_dir(staging: Path) -> list:
    """Entradas {path, sha256, bytes, rows} calculadas en flujo desde archivos ya escritos (sin cargarlos en RAM)."""
    out = []
    for q in sorted(Path(staging).rglob("*")):
        if not q.is_file():
            continue
        h, n, lines = hashlib.sha256(), 0, 0
        with q.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
                n += len(chunk)
                lines += chunk.count(b"\n")
        rel = q.relative_to(staging).as_posix()
        out.append({"path": rel, "sha256": h.hexdigest(), "bytes": n, "rows": (lines - 1) if rel.endswith(".csv") else None})
    return out


def write_version_staged(family_root: Path, family: str, staging: Path, manifest_bytes: bytes) -> dict:
    """Como write_version, pero los archivos ya están escritos (en flujo) en `staging` dentro de family_root/.staging.
    Verifica, renombra atómicamente a versions/<tree>/ o elimina el staging si algo falla (sin emisión parcial)."""
    family_root, staging = Path(family_root), Path(staging)
    try:
        m = json.loads(manifest_bytes)
        entries = [{k: e[k] for k in e} for e in m["files"]]
        tree = tree_of(entries)
        need(m["tree_sha256"] == tree, "MANIFIESTO_Y_ARCHIVOS_INCOHERENTES")
        (staging / MANIFEST_NAME[family]).write_bytes(manifest_bytes)
        verify_version(staging, family, expected_tree=tree)
        dest = family_root / "versions" / tree
        if dest.exists():
            verify_version(dest, family, expected_tree=tree)
            need((dest / MANIFEST_NAME[family]).read_bytes() == manifest_bytes, "VERSION_EXISTENTE_DISTINTA")
            return {"tree_sha256": tree, "path": dest, "manifest_sha256": sha(manifest_bytes), "created": False}
        dest.parent.mkdir(parents=True, exist_ok=True)
        os.replace(staging, dest)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
        parent = family_root / ".staging"
        if parent.exists() and not any(parent.iterdir()):
            parent.rmdir()
    verify_version(dest, family, expected_tree=tree)
    return {"tree_sha256": tree, "path": dest, "manifest_sha256": sha(manifest_bytes), "created": True}
