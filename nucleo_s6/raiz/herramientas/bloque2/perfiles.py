"""Perfiles de verificación para D8_pre, freeze-run, corrida y exportación: OFICIAL o ENSAYO (aislado, ficticio).

El perfil fija QUÉ se considera aprobado (manifiesto de entorno + lock, informes A/A-ter); la lógica de verificación
es la misma en ambos. Reglas:
- oficial: constantes de este módulo (manifiesto/lock del contrato Paquete A e informes A/A-ter del proyecto);
  exige autoridad NO ficticia. En el bloque 2 no existe esa autoridad: toda ruta oficial se rechaza.
- ensayo: archivo JSON direccionado por contenido dentro de una raíz marcada ENSAYO_AISLADO.json (rótulo FICTICIO);
  exige autoridad ficticia. Sus fixtures de entorno/informes están rotulados y nunca se aceptan en el perfil oficial.
Un producto emitido bajo perfil ensayo lleva la dependencia 'perfil_ensayo' y ningún consumidor oficial lo acepta.

Bloque 3 (candidato):
- official(root): sin S4 REAL vigente, lo aprobado hoy (constantes históricas, entorno 22621, sin atestaciones). Con
  S4 real vigente y verificado (s4_publicador.verify), lo que S4 fijó: entorno sucesor (perfil 'integracion' para el
  proceso, 'numerico' para los informes A/A-ter) y las atestaciones instaladas. Un S4 FICTICIO nunca cambia el perfil
  oficial. Nada se aprueba por etiqueta.
- a_reports_binding: un informe puede ligarse (a) directamente (mismo entorno/lock y árbol actual) o (b) mediante una
  ATESTACIÓN de reproducción bit a bit (herramientas/s4/paquete_a.py): entorno del informe = antecedente histórico
  reproducido en el entorno numérico del perfil; árbol del informe = árbol de la era A ligado al actual por el delta
  autorizado de A-ter. Sin atestación válida siguen los rechazos REPORT_OTHER_ENVIRONMENT/LOCK/CODE_TREE.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from herramientas.bloque2 import entorno as E

MARKER = "ENSAYO_AISLADO.json"
TAG = "FICTICIO"
PROFILE_DIR = "ensayo/perfiles"
OFFICIAL_A_REPORTS = (
    {"id": "A", "path": "reports/validation/synthetic_run_manifest.json",
     "sha256": "3f4494e944f44f6281cf75611cf0c65fec3c9a9c07fe22ae18b9ccbe3b6b9bdc",
     "outputs": ("solver_error_report.json", "solver_error_report.csv", "inversion_result.json", "inversion_result.csv")},
    {"id": "A-ter", "path": "reports/validation_tst/tst_run_manifest.json",
     "sha256": "e8d49e3105d83ac371794a999c09840312f153acbdc1c0b78317bcae3f52f9c1",
     "outputs": ("tst_chain_result.json", "tst_chain_result.csv", "tst_validation_report.json", "tst_validation_report.csv")},
)
OUTPUT_FIELD = {"solver_error_report.json": "solver_error_json_sha256", "solver_error_report.csv": "solver_error_csv_sha256",
                "inversion_result.json": "inversion_result_json_sha256", "inversion_result.csv": "inversion_result_csv_sha256",
                "tst_chain_result.json": "tst_chain_result_json_sha256", "tst_chain_result.csv": "tst_chain_result_csv_sha256",
                "tst_validation_report.json": "tst_validation_report_json_sha256",
                "tst_validation_report.csv": "tst_validation_report_csv_sha256"}


class ProfileError(RuntimeError):
    pass


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def official(root=None, *, anclas: dict | None = None) -> dict:
    hist = {"kind": "oficial", "path": None, "sha256": None,
            "environment": {"manifest_path": E.APPROVED_MANIFEST_PATH, "manifest_sha256": E.APPROVED_MANIFEST_SHA256,
                            "lock_path": E.APPROVED_LOCK_PATH, "lock_sha256": E.APPROVED_LOCK_SHA256},
            "a_reports": [dict(r, outputs=list(r["outputs"])) for r in OFFICIAL_A_REPORTS], "code_tree_root": "src/paper2",
            "approval_source": "contrato aprobado vigente (histórico)"}
    if root is None:
        return hist
    s4 = s4_approved(root, anclas=anclas)
    if s4 is None:
        return hist
    env = s4["environment"]["perfiles"]
    reports = []
    for r in OFFICIAL_A_REPORTS:
        att = s4["paquete_a"][r["id"]]
        reports.append(dict(r, outputs=list(r["outputs"]),
                            attestation={"path": s4.get("paquete_a_prefix", s4["installed_prefix"]) + att["path"], "sha256": att["sha256"]}))
    return dict(hist, environment=dict(env["integracion"]), a_reports_environment=dict(env["numerico"]), a_reports=reports,
                approval_source=s4.get("autoridad", "S4") + " real vigente " + s4["package_sha256"])


def perfil_informe(root, *, anclas: dict | None = None) -> tuple[dict, str]:
    """Perfil contra el que el informe de la batería evalúa la CONFORMIDAD del entorno (dato informativo: la huella no
    depende del perfil). Normalmente el oficial. En la ventana de incorporación de un sucesor (S4 vivo declarado que ya no
    verifica porque la toolchain incorporada no es cerrada) el oficial sigue siendo un error controlado; el informe se
    evalúa entonces contra el entorno sucesor 'integracion' (pins aprobados por S4) y declara el motivo."""
    try:
        return official(root, anclas=anclas), "oficial"
    except ProfileError as exc:
        # Una S6 declarada no puede eludir el ancla mediante el perfil informativo.
        live = Path(root) / "fase6_planes/freeze_plans_manifest.json"
        if anclas is not None and "lanzamiento_sha256" in anclas:
            raise
        if (Path(root) / "fase6_planes/s6_pending_transaction.json").exists():
            raise
        if live.is_file():
            obj = json.loads(live.read_bytes())
            if not isinstance(obj, dict) or "s6" in obj or obj.get("freeze_mode") == "successor_freeze_block3_code_S6_v1":
                raise
        from herramientas.bloque2 import entorno_sucesor as ES
        return ({"environment": dict(ES.PERFILES["integracion"])},
                "entorno_sucesor_integracion; perfil oficial indeterminado: " + str(exc))


def s4_approved(root, *, anclas: dict | None = None):
    """S4 REAL vigente y verificado (definición única: herramientas/s4/aprobacion.estado_s4); si no, None.
    Un S4 declarado pero inválido es un error controlado (ProfileError), no un perfil histórico silencioso."""
    from herramientas.s4 import aprobacion as AP
    est = AP.estado_s4(root, anclas=anclas)
    if est["estado"] == "INVALIDO":
        raise ProfileError("S4_VIVO_INVALIDO:" + est["motivo"])
    if anclas is not None and "lanzamiento_sha256" in anclas and est.get("autoridad") != "S6":
        raise ProfileError("CONTEXTO_S6_SIN_AUTORIDAD_S6_VERIFICADA")
    if est["estado"] != "VERIFICADO_REAL":
        return None
    return {"package_sha256": est["package_sha256"], "installed_prefix": est["installed_prefix"],
            "environment": est["environment"], "paquete_a": est["paquete_a"], "autoridad": est.get("autoridad", "S4"),
            "paquete_a_prefix": est.get("paquete_a_prefix", est["installed_prefix"])}


def is_isolated(root) -> bool:
    q = Path(root) / MARKER
    if not q.is_file():
        return False
    try:
        return json.loads(q.read_bytes()).get("tag") == TAG
    except ValueError:
        return False


def mark_isolated(root, purpose: str):
    q = Path(root) / MARKER
    if not q.exists():
        q.write_text(json.dumps({"tag": TAG, "purpose": purpose,
                                 "note": "raíz de ensayo aislada; nada aquí es oficial ni se incorpora al original"},
                                sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def write_trial(root, doc: dict) -> tuple[str, str]:
    """Escribe un perfil de ensayo (rótulo FICTICIO obligatorio) en una raíz aislada; devuelve (ruta, sha)."""
    if not is_isolated(root):
        raise ProfileError("PROFILE_TRIAL_REQUIRES_ISOLATED_ROOT")
    doc = dict(doc, kind="ensayo", tag=TAG)
    raw = json.dumps(doc, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"
    rel = f"{PROFILE_DIR}/perfil_{sha(raw)[:16]}.json"
    q = Path(root) / rel
    q.parent.mkdir(parents=True, exist_ok=True)
    if not q.exists():
        q.write_bytes(raw)
    if q.read_bytes() != raw:
        raise ProfileError("PROFILE_WRITE")
    return rel, sha(raw)


def load(root, path: str | None, digest: str | None, *, anclas: dict | None = None) -> dict:
    """Perfil seleccionado explícitamente: None -> oficial; si no, perfil de ensayo autenticado por hash en raíz aislada."""
    if path is None:
        if digest is not None:
            raise ProfileError("PROFILE_DIGEST_WITHOUT_PATH")
        return official(root, anclas=anclas)
    raw = (Path(root) / path).read_bytes()
    if sha(raw) != digest:
        raise ProfileError("PROFILE_HASH")
    doc = json.loads(raw)
    if doc.get("kind") != "ensayo" or doc.get("tag") != TAG:
        raise ProfileError("PROFILE_NOT_TRIAL")
    if not is_isolated(root):
        raise ProfileError("PROFILE_TRIAL_OUTSIDE_ISOLATED_ROOT")
    return dict(doc, path=path, sha256=digest)


def require_authority(profile: dict, authority) -> None:
    if profile["kind"] == "oficial" and authority.fictitious:
        raise ProfileError("OFFICIAL_PROFILE_REJECTS_FICTITIOUS_AUTHORITY")
    if profile["kind"] == "ensayo" and not authority.fictitious:
        raise ProfileError("TRIAL_PROFILE_REQUIRES_FICTITIOUS_AUTHORITY")


def environment(root, profile: dict) -> dict:
    """Evaluación de entorno contra lo aprobado por el perfil (manifiesto + lock autenticados)."""
    env = profile["environment"]
    return E.assessment(root, manifest_path=env["manifest_path"], manifest_sha256=env["manifest_sha256"],
                        lock_path=env["lock_path"], lock_sha256=env["lock_sha256"])


def code_tree_sha256(root, rel: str) -> str:
    """Árbol de código Paquete A (paper2-tree-v1, solo archivos regulares fuera de __pycache__)."""
    import struct
    import unicodedata
    base = Path(root) / rel

    def nfc(s):
        return unicodedata.normalize("NFC", s)

    def frame(label, payload):      # = paper2.io.canonical.frame / sequence (paper2-tree-v1)
        lb = label.encode("ascii")
        return struct.pack(">I", len(lb)) + lb + struct.pack(">Q", len(payload)) + payload

    files = sorted([p for p in base.rglob("*") if p.is_file() and "__pycache__" not in p.parts],
                   key=lambda p: nfc(p.relative_to(base).as_posix()).encode("utf-8"))
    entries = []
    for p in files:
        data = p.read_bytes()
        entries.append(frame("path", nfc(p.relative_to(base).as_posix()).encode("utf-8"))
                       + frame("size", struct.pack(">Q", len(data))) + frame("sha256", hashlib.sha256(data).digest()))
    seq = (frame("domain", b"paper2-tree-v1") + frame("count", struct.pack(">Q", len(entries)))
           + b"".join(frame("item", e) for e in entries))
    return hashlib.sha256(seq).hexdigest()


def a_reports_binding(root, profile: dict, env_doc: dict) -> list:
    """Vincula cada informe A/A-ter al entorno aprobado (manifiesto y lock), a sus salidas (hash) y al árbol de código
    ACTUAL de Paquete A, directamente o mediante atestación de reproducción. Devuelve filas {id, path, sha256, ok,
    problems, via}."""
    root = Path(root)
    out = []
    appr = profile.get("a_reports_environment") or profile["environment"]
    current_tree = None
    for r in profile["a_reports"]:
        problems = []
        q = root / r["path"]
        if not q.is_file():
            out.append({"id": r["id"], "path": r["path"], "sha256": None, "ok": False, "problems": ["REPORT_MISSING"], "via": None})
            continue
        raw = q.read_bytes()
        rep = json.loads(raw)
        if r.get("sha256") and sha(raw) != r["sha256"]:
            problems.append("REPORT_HASH")
        att_ok, via = False, "directo"
        if r.get("attestation"):
            via = "atestacion"
            from herramientas.s4 import paquete_a as PA
            araw = (root / r["attestation"]["path"]).read_bytes() if (root / r["attestation"]["path"]).is_file() else b""
            if sha(araw) != r["attestation"]["sha256"]:
                problems.append("ATTESTATION_HASH")
            else:
                aprobs = PA.verificar_atestacion(root, json.loads(araw), r["id"], appr,
                                                 dir_atestacion=(root / r["attestation"]["path"]).parent)
                problems += ["ATTESTATION:" + x for x in aprobs]
                att_ok = not aprobs
        env_direct = rep.get("environment_manifest_sha256") == appr["manifest_sha256"]
        lock_direct = rep.get("lockfile_sha256") == appr["lock_sha256"]
        if not env_direct and not (att_ok and rep.get("environment_manifest_sha256") == E.APPROVED_MANIFEST_SHA256):
            problems.append("REPORT_OTHER_ENVIRONMENT")
        if not lock_direct and not (att_ok and rep.get("lockfile_sha256") == E.APPROVED_LOCK_SHA256 == appr["lock_sha256"]):
            problems.append("REPORT_OTHER_LOCK")
        if rep.get("overall_status") != "pass":
            problems.append("REPORT_NOT_PASS")
        for name in r["outputs"]:
            f = q.parent / name
            if not f.is_file() or sha(f.read_bytes()) != rep.get(OUTPUT_FIELD[name]):
                problems.append("REPORT_OUTPUT_HASH:" + name)
        if current_tree is None:
            current_tree = code_tree_sha256(root, profile.get("code_tree_root", "src/paper2"))
        if rep.get("code_tree_sha256") != current_tree and not att_ok:
            problems.append("REPORT_OTHER_CODE_TREE")
        if not env_doc.get("conforms"):
            problems.append("CURRENT_ENVIRONMENT_NOT_APPROVED")
        out.append({"id": r["id"], "path": r["path"], "sha256": sha(raw), "ok": not problems, "problems": problems, "via": via})
    return out
