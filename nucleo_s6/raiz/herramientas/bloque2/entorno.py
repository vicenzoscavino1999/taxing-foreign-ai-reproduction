"""Verificación de entorno RE-03 contra el manifiesto y el lock APROBADOS (Paquete A), no por cadena de versión.

Huella observada (`observe`): implementación y versión de Python, ejecutable (ruta y SHA-256 del lanzador, del
intérprete base y de la DLL de CPython), plataforma/compilación del SO, arquitectura, distribuciones instaladas con
hash del archivo instalado (direct_url.json), BLAS/LAPACK de NumPy (implementación, versión, ancho entero ILP64/LP64,
DYNAMIC_ARCH, MAX_THREADS), política de hilos, locale, zona horaria, semilla de hash y versión de pip.
`compare` devuelve la lista exacta de discrepancias contra el manifiesto aprobado (campos del manifiesto RE-03) y
contra el lock (conjunto EXACTO de distribuciones, versiones y hashes). Vacía = entorno conforme.
`write_evidence` escribe la evidencia como archivo JSON direccionado por contenido: la ruta citada contiene
exactamente los bytes cuyo hash se registra (nunca se asigna el hash de un JSON a una ruta de código).
El entorno canónico (3.12.4, Windows 11 build 22621) no está disponible en esta máquina: aquí la comparación
REPORTA discrepancias; ninguna prueba declara revalidación canónica.
"""
from __future__ import annotations

import hashlib
import json
import locale
import os
import platform
import re
import sys
import time
from pathlib import Path

APPROVED_MANIFEST_PATH = "environment/package_a/environment_manifest.json"
APPROVED_MANIFEST_SHA256 = "3bd72cc82b79179d61ec58fd8440dbc8bbf1f6d28c4babac6f4ad379c1f0abf9"
APPROVED_LOCK_PATH = "environment/package_a/requirements.lock"
APPROVED_LOCK_SHA256 = "3e81920beac139b7a4d992e3cde7847c44d21253059e5de76703a518806e6521"
THREAD_VARS = ("BLIS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
               "VECLIB_MAXIMUM_THREADS")
SCHEMA = "paper2b-environment-fingerprint-v1"


class EnvironmentError_(RuntimeError):
    pass


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _file_sha(p) -> str | None:
    try:
        return sha(Path(p).read_bytes())
    except OSError:
        return None


def _blas() -> dict:
    import numpy
    out = {}
    try:
        cfg = numpy.show_config(mode="dicts").get("Build Dependencies", {})
    except Exception:  # noqa: BLE001
        cfg = {}
    for k in ("blas", "lapack"):
        d = cfg.get(k, {})
        text = str(d.get("openblas configuration", ""))
        impl = "OpenBLAS" if ("openblas" in str(d.get("name", "")).lower() or text.startswith("OpenBLAS")) else d.get("name")
        m = re.search(r"MAX_THREADS=(\d+)", text)
        out[k] = {"implementation": impl, "version": d.get("version"),
                  "integer_width": "ILP64" if "USE64BITINT" in text else ("LP64" if text else None),
                  "dynamic_arch": "DYNAMIC_ARCH" in text, "max_threads": int(m.group(1)) if m else None}
    return out


def _platform() -> str:
    ver = platform.version()
    build = ver.split(".")[-1] if ver else ""
    return f"{platform.system()}-{platform.release()}-build-{build}"


def observe() -> dict:
    import importlib.metadata as md
    import numpy
    pk = {}
    for d in md.distributions():
        name = d.metadata["Name"].lower()
        du = d.read_text("direct_url.json")
        h = None
        if du:
            try:
                h = (json.loads(du).get("archive_info", {}).get("hashes", {}) or {}).get("sha256")
            except ValueError:
                h = None
        rec = d.read_text("RECORD")
        pk[name] = {"version": d.version, "archive_sha256": h, "record_sha256": sha(rec.encode("utf-8")) if rec else None}
    base = getattr(sys, "_base_executable", sys.executable)
    dll = Path(sys.base_prefix) / f"python{sys.version_info[0]}{sys.version_info[1]}.dll"
    blas = _blas()
    tz = os.environ.get("TZ") or ("UTC" if time.timezone == 0 and not time.daylight else "local:" + str(time.timezone))
    return {"schema": SCHEMA, "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "executable": {"path": sys.executable, "sha256": _file_sha(sys.executable), "base_path": base,
                           "base_sha256": _file_sha(base), "runtime_dll_sha256": _file_sha(dll)},
            "platform": _platform(), "architecture": f"{platform.machine()}-{platform.architecture()[0]}",
            "numpy_version": numpy.__version__, "packages": dict(sorted(pk.items())), "blas": blas["blas"],
            "lapack": blas["lapack"], "thread_policy": {k: os.environ.get(k) for k in THREAD_VARS},
            "locale": locale.setlocale(locale.LC_ALL, None), "timezone": tz, "hash_seed": os.environ.get("PYTHONHASHSEED"),
            "pip_version": pk.get("pip", {}).get("version")}


def parse_lock(raw: bytes) -> dict:
    out = {}
    for line in raw.decode("utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("--") or line.startswith("#"):
            continue
        f = re.match(r"([A-Za-z0-9_.\-]+)==(\S+)\s+--record-sha256=([0-9a-f]{64})$", line)
        if f:      # sintaxis SOLO de locks de ensayo: identidad por RECORD instalado (no existe en el lock aprobado)
            out[f.group(1).lower()] = {"version": f.group(2), "sha256": None, "record_sha256": f.group(3)}
            continue
        m = re.match(r"([A-Za-z0-9_.\-]+)\s*@\s*(\S+)\s+--hash=sha256:([0-9a-f]{64})", line)
        if not m:
            raise EnvironmentError_("LOCK_LINE_UNPARSEABLE:" + line[:60])
        url = m.group(2)
        ver = re.search(r"/[A-Za-z0-9_.]+?-([0-9][A-Za-z0-9_.]*?)-(?:py|cp)", url)
        out[m.group(1).lower()] = {"version": ver.group(1) if ver else None, "sha256": m.group(3)}
    return out


def approved(root, manifest_path: str = APPROVED_MANIFEST_PATH, manifest_sha256: str = APPROVED_MANIFEST_SHA256,
             lock_path: str = APPROVED_LOCK_PATH, lock_sha256: str = APPROVED_LOCK_SHA256) -> dict:
    """Carga el manifiesto y el lock aprobados autenticando sus bytes y su vínculo mutuo."""
    root = Path(root)
    mraw = (root / manifest_path).read_bytes()
    if sha(mraw) != manifest_sha256:
        raise EnvironmentError_("APPROVED_ENVIRONMENT_MANIFEST_HASH")
    lraw = (root / lock_path).read_bytes()
    if sha(lraw) != lock_sha256:
        raise EnvironmentError_("APPROVED_LOCK_HASH")
    man = json.loads(mraw)
    if man.get("lockfile_sha256") != lock_sha256:
        raise EnvironmentError_("APPROVED_MANIFEST_NOT_BOUND_TO_LOCK")
    return {"manifest": man, "manifest_path": manifest_path, "manifest_sha256": manifest_sha256, "lock": parse_lock(lraw),
            "lock_path": lock_path, "lock_sha256": lock_sha256}


def compare(obs: dict, appr: dict) -> list:
    """Discrepancias exactas (vacía = conforme con RE-03 + lock)."""
    man, lock = appr["manifest"], appr["lock"]
    bad = []

    def ne(code, a, b):
        if a != b:
            bad.append(f"{code}:{a}!={b}")
    ne("PYTHON_IMPLEMENTATION", obs["python_implementation"], man["python_implementation"])
    ne("PYTHON_VERSION", obs["python_version"], man["python_version"])
    ne("PLATFORM", obs["platform"], man["platform"])
    ne("ARCHITECTURE", obs["architecture"], man["architecture"])
    ne("PIP_VERSION", obs["pip_version"], man["pip_version"])
    for k in ("blas", "lapack"):
        want = man[k]
        got = obs[k]
        for f in ("implementation", "version", "integer_width"):
            ne(f"{k.upper()}_{f.upper()}", got.get(f), want.get(f))
        if "dynamic_arch" in want:
            ne(f"{k.upper()}_DYNAMIC_ARCH", got.get("dynamic_arch"), want["dynamic_arch"])
        if "max_threads" in want:
            ne(f"{k.upper()}_MAX_THREADS", got.get("max_threads"), want["max_threads"])
    for k, v in sorted(man["thread_policy"].items()):
        ne("THREAD_POLICY_" + k, obs["thread_policy"].get(k), v)
    ne("LOCALE", obs["locale"], man["locale"])
    ne("TIMEZONE", obs["timezone"], man["timezone"])
    ne("HASH_SEED", obs["hash_seed"], man["hash_seed"])
    installed = obs["packages"]
    for name, spec in sorted(lock.items()):
        got = installed.get(name)
        if got is None:
            bad.append("LOCK_PACKAGE_MISSING:" + name)
            continue
        if spec["version"] is not None and got["version"] != spec["version"]:
            bad.append(f"LOCK_PACKAGE_VERSION:{name}:{got['version']}!={spec['version']}")
        if spec.get("record_sha256"):
            if got.get("record_sha256") != spec["record_sha256"]:
                bad.append("LOCK_PACKAGE_RECORD:" + name)
        elif got["archive_sha256"] is None:
            bad.append("LOCK_PACKAGE_HASH_UNVERIFIABLE:" + name)
        elif got["archive_sha256"] != spec["sha256"]:
            bad.append("LOCK_PACKAGE_HASH:" + name)
    extra = sorted(set(installed) - set(lock))
    if extra:
        bad.append("PACKAGES_OUTSIDE_LOCK:" + ",".join(extra))
    for rp in man.get("runtime_packages", []):
        got = installed.get(rp["name"].lower())
        if got is None or got["version"] != rp["version"] or got["archive_sha256"] != rp["sha256"]:
            bad.append("RUNTIME_PACKAGE:" + rp["name"])
    return sorted(set(bad))


def assessment(root, **approved_kw) -> dict:
    """Huella + comparación contra lo aprobado; documento completo de evidencia (sin rutas de código)."""
    obs = observe()
    try:
        appr = approved(root, **approved_kw)
        mism = compare(obs, appr)
        ref = {"manifest_path": appr["manifest_path"], "manifest_sha256": appr["manifest_sha256"], "lock_path": appr["lock_path"],
               "lock_sha256": appr["lock_sha256"]}
    except (OSError, EnvironmentError_, ValueError, KeyError) as exc:
        mism = ["APPROVED_ENVIRONMENT_UNAVAILABLE:" + str(exc)]
        ref = {k: approved_kw.get(k) for k in ("manifest_path", "manifest_sha256", "lock_path", "lock_sha256")}
    return {"schema": SCHEMA, "fingerprint": obs, "fingerprint_sha256": sha(canon(obs)), "approved": ref, "mismatches": mism,
            "conforms": not mism,
            "note": "evidencia de entorno; conforms=false significa que NO es el entorno aprobado (desarrollo)"}


def write_evidence(root, rel_dir: str, doc: dict) -> tuple[str, str]:
    """Escribe el documento de evidencia como <rel_dir>/entorno_<sha16>.json y devuelve (ruta relativa, sha de los bytes)."""
    raw = canon(doc) + b"\n"
    h = sha(raw)
    rel = f"{rel_dir.rstrip('/')}/entorno_{h[:16]}.json"
    q = Path(root) / rel
    q.parent.mkdir(parents=True, exist_ok=True)
    if not q.exists():
        q.write_bytes(raw)
    if q.read_bytes() != raw:
        raise EnvironmentError_("ENVIRONMENT_EVIDENCE_WRITE")
    return rel, h


def verify_evidence(root, rel: str, digest: str) -> dict:
    raw = (Path(root) / rel).read_bytes()
    if sha(raw) != digest:
        raise EnvironmentError_("ENVIRONMENT_EVIDENCE_HASH")
    if not rel.endswith(".json"):
        raise EnvironmentError_("ENVIRONMENT_EVIDENCE_NOT_JSON_PATH")
    doc = json.loads(raw)
    if doc.get("schema") != SCHEMA or doc.get("fingerprint_sha256") != sha(canon(doc["fingerprint"])):
        raise EnvironmentError_("ENVIRONMENT_EVIDENCE_MALFORMED")
    return doc


def fixture_approval(obs: dict | None = None, *, label: str = "FICTICIO") -> tuple[bytes, bytes]:
    """SOLO ENSAYOS: manifiesto 'aprobado' y lock FICTICIOS que describen el entorno observado, para ejercitar la ruta
    positiva de la comparación en una raíz aislada. Rotulados; el perfil oficial exige los hashes aprobados reales."""
    obs = obs or observe()
    lock_lines = ["--only-binary=:all:"]
    for name, p in sorted(obs["packages"].items()):
        if p["archive_sha256"]:
            lock_lines.append(f"{name} @ https://fixture.invalid/{name}-{p['version']}-py3-none-any.whl "
                              f"--hash=sha256:{p['archive_sha256']}")
        else:
            lock_lines.append(f"{name}=={p['version']} --record-sha256={p['record_sha256'] or '0' * 64}")
    lraw = ("\n".join(lock_lines) + "\n").encode("utf-8")
    man = {"architecture": obs["architecture"], "blas": dict(obs["blas"]), "lapack": dict(obs["lapack"]),
           "environment_id": "FIXTURE_" + label, "hash_seed": obs["hash_seed"], "locale": obs["locale"],
           "lockfile_sha256": sha(lraw), "pip_version": obs["pip_version"], "platform": obs["platform"],
           "python_implementation": obs["python_implementation"], "python_version": obs["python_version"],
           "runtime_packages": [], "thread_policy": dict(obs["thread_policy"]), "timezone": obs["timezone"],
           "fixture_label": label}
    return canon(man) + b"\n", lraw


def set_runtime_conventions():
    """Convenciones que el propio programa fija (como Paquete A): locale C. TZ/hilos/semilla vienen del lanzador."""
    try:
        locale.setlocale(locale.LC_ALL, "C")
    except locale.Error:
        pass
