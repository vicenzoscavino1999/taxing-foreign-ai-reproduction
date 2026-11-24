"""Ubicaciones fijadas de los lectores nacionales incorporados en 1.5 (A-06).

Selección explícita: la recepción se identifica por el hash de su árbol, nunca por «la más reciente». El registro de
casos, el catálogo CA2-3, la rueda de xlrd y el lector D2 legado también se fijan por hash antes de usarse.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RECEPTION_TREE = '866aa139fb50578cae1ec5d77e1f98e6a5b87b56780aa1d95a118dffc5644984'
RECEPTION = ROOT / 'fase2_datos/recepcion_nacional/versions' / RECEPTION_TREE
S3_TREE = ROOT / 'herramientas/s3'
CATALOG_DIR = S3_TREE / 'contratos'
REGISTRY_FILE = S3_TREE / 'contratos_adicionales/REGISTRO_CASOS_A1E_V2.json'
REGISTRY_SHA256 = '18344e5fff14865f35c47d24babee4edd9840316c36d11e038f4f0de2288c95d'
XLRD_WHEEL = HERE / 'vendor/xlrd-2.0.2-py2.py3-none-any.whl'
XLRD_WHEEL_SHA256 = 'ea762c3d29f4cca48d82df517b6d89fbce4db3107f9d78713e48cd321d5c9aa9'
LEGACY_D2 = ROOT / 'fase2_datos/d2_cuentas_nacionales/construir_labor_income_shares.py'
LEGACY_D2_SHA256 = 'e5d7304fefb50d19cc8ad95774d9a7e29ce20ad65a8ba6e3147355c23dd902c1'


class ReceptionError(ValueError):
    pass


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canon(value) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')


def need(test, message):
    if not test:
        raise ReceptionError(message)


def verify_reception(root: Path | None = None) -> dict:
    """Autentica la recepción completa: conjunto exacto de archivos, hashes, bytes y árbol fijado."""
    base = (Path(root) / 'fase2_datos/recepcion_nacional/versions' / RECEPTION_TREE) if root else RECEPTION
    manifest = json.loads((base / 'recepcion_manifest.json').read_bytes())
    files = manifest['files']
    need(manifest['tree_sha256'] == RECEPTION_TREE == sha(canon(files)), 'árbol de la recepción distinto del fijado')
    need([f['path'] for f in files] == sorted({f['path'] for f in files}), 'inventario de recepción desordenado o duplicado')
    observed = sorted(q.relative_to(base).as_posix() for q in base.rglob('*') if q.is_file() and q.name != 'recepcion_manifest.json')
    need(observed == [f['path'] for f in files], 'recepción ampliada o incompleta')
    for f in files:
        raw = (base / f['path']).read_bytes()
        need(sha(raw) == f['sha256'] and len(raw) == f['bytes'], 'archivo de recepción alterado: ' + f['path'])
    need(manifest['private_originals_included'] is False and manifest['source_admission'] is False, 'estado de la recepción')
    return {'tree_sha256': RECEPTION_TREE, 'files': len(files), 'manifest_sha256': sha((base / 'recepcion_manifest.json').read_bytes())}


def load_xlrd():
    """xlrd 2.0.2 desde la rueda fijada (solo lectura del .xls chileno); nunca una instalación ajena."""
    need(sha(XLRD_WHEEL.read_bytes()) == XLRD_WHEEL_SHA256, 'rueda xlrd alterada')
    if 'xlrd' in sys.modules:
        need(Path(sys.modules['xlrd'].__file__).resolve().is_relative_to(XLRD_WHEEL.resolve()), 'xlrd ajeno ya cargado')
        return sys.modules['xlrd']
    sys.path.insert(0, str(XLRD_WHEEL))
    try:
        import xlrd  # noqa: PLC0415
    finally:
        sys.path.remove(str(XLRD_WHEEL))
    return xlrd


def load_legacy_d2():
    """Constructor D2 legado del proyecto (lectores de la cuenta UN legada), fijado por hash."""
    name = 'herramientas_nacionales_legacy_d2'
    if name in sys.modules:
        return sys.modules[name]
    need(sha(LEGACY_D2.read_bytes()) == LEGACY_D2_SHA256, 'constructor D2 legado alterado')
    spec = importlib.util.spec_from_file_location(name, LEGACY_D2)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_registry_bytes() -> bytes:
    raw = REGISTRY_FILE.read_bytes()
    need(sha(raw) == REGISTRY_SHA256, 'registro A1-E v2 distinto del aprobado')
    return raw
