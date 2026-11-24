"""Versión D2 aprobada (A-06): recomputación desde la recepción, publicación versionada y verificación.

La versión aprobada es el árbol f9d42072… (14 archivos de datos). Aquí se recomputa desde la recepción autenticada
con los lectores incorporados y se exige EXACTAMENTE ese árbol; nunca se copian bytes sin recomputarlos.

Publicación (DB-09): staging aislado -> verificación completa -> mover a versions/<árbol> -> verificar bytes ->
recibo de promoción -> sustituir el puntero active_product.json de forma atómica. La salida legada output/ (manifiesto
78791c19…) queda intacta como predecesora. El puntero se escribe solo después de verificar S3 y la versión.

Consumidores: verify_active(root, expected_tree=..., s3=...) exige selección explícita del árbol aprobado.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from herramientas.nacionales.base import (  # noqa: E402
    RECEPTION_TREE, ReceptionError, canon, need, sha, verify_reception, REGISTRY_SHA256,
)

PRODUCT = 'fase2_datos/d2_cuentas_nacionales'
POINTER = PRODUCT + '/active_product.json'
RECEIPTS = PRODUCT + '/promotion_receipts'
LEGACY_MANIFEST = PRODUCT + '/output/d2_manifest.json'
LEGACY_MANIFEST_SHA256 = '78791c19b28322e581826a5628c6cacbb3a746f6cc62488b43f8665d3ea36ec4'
APPROVED_TREE = 'f9d42072e07dbce5fabb92a4e183bb3390a981318e3a29f0906e8fe990a589c8'
CONTRACT_SHA256 = 'eda3d6e5a0c0c0c318bb075c3314f7c927382c955d76e2dcdd3b5c1f4659af32'
DOSSIER_SEAL = 'd2adfdc090d34c3c03ecd6f70e318352b18dc9c2b56a9da4c611e2c70b2d1b6c'
VERSION_FILES = ('datos/d2_2015_2023.csv', 'datos/d2_primaria_2023.csv', 'datos/d2_revision_bridge.csv', 'datos/puente_revisiones.csv',
                 'datos/conciliaciones.json', 'datos/vectores.json', 'datos/labor_income_shares_candidato.csv',
                 'datos/labor_income_shares_sensitivity_candidato.csv', 'datos/d2_gate_report_candidato.json',
                 'datos/precision_evidence_candidato.csv', 'datos/dominios_candidatos.json', 'datos/correspondencia_csi103.csv',
                 'datos/contraste_csi103.json', 'datos/ca2_evidence_receipts.json')
MANIFEST_NAME = 'd2_manifest.json'
MANIFEST_FIELDS = ('schema_version', 'product_type', 'run_id', 'created_at', 'producer_path', 'producer_sha256',
                   'authority_package_sha256', 'authority_manifest_sha256', 'contract_sha256', 'input_dependencies',
                   'files', 'tree_sha256', 'phase_status')
POINTER_FIELDS = ('schema_version', 'product_type', 'active_tree_sha256', 'active_relative_path', 'active_manifest_sha256',
                  'predecessor_reference', 'promotion_receipt_sha256', 'immutable_tree_sha256s')


def encoded(obj) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def tree_of(files: list[dict]) -> str:
    return sha(canon(files))


def recompute(out: Path) -> dict:
    """Construye todo el candidato nacional en `out` desde la recepción y devuelve el árbol de la versión."""
    verify_reception(ROOT)
    from herramientas.nacionales import nacionales, adaptadores_ca2
    nacionales.build(out)
    adaptadores_ca2.preflight(out)
    files = [{'path': Path(n).name, 'sha256': sha((out / n).read_bytes()), 'bytes': (out / n).stat().st_size}
             for n in sorted(VERSION_FILES, key=lambda n: Path(n).name)]
    return {'tree_sha256': tree_of(files), 'files': files, 'data': {Path(n).name: (out / n).read_bytes() for n in VERSION_FILES}}


def _manifest(tree: str, files: list[dict], authority: dict, created_at: str) -> dict:
    producer = HERE / 'construir_d2.py'
    deps = [
        {'role': 'recepcion_nacional', 'path': f'fase2_datos/recepcion_nacional/versions/{RECEPTION_TREE}/recepcion_manifest.json',
         'sha256': verify_reception(ROOT)['manifest_sha256'], 'tree_sha256': RECEPTION_TREE, 'version': RECEPTION_TREE,
         'authority_package_sha256': authority['package_sha256']},
        {'role': 'registro_casos_A1E_v2', 'path': 'herramientas/s3/contratos_adicionales/REGISTRO_CASOS_A1E_V2.json',
         'sha256': REGISTRY_SHA256, 'tree_sha256': None, 'version': 'A1-E-v2', 'authority_package_sha256': authority['package_sha256']},
        {'role': 'contrato_normativo', 'path': 'herramientas/s3/contratos/contract_manifest.json', 'sha256': CONTRACT_SHA256,
         'tree_sha256': None, 'version': 'CA2-3/macro-ca2-v2', 'authority_package_sha256': authority['package_sha256']},
        {'role': 'expediente_sellado', 'path': f'fase2_datos/recepcion_nacional/versions/{RECEPTION_TREE}/evidencia/sello_expediente.json',
         'sha256': DOSSIER_SEAL, 'tree_sha256': None, 'version': 'SEALED_SANITIZED_DOSSIER_1', 'authority_package_sha256': authority['package_sha256']},
        {'role': 'predecesor_legado', 'path': LEGACY_MANIFEST, 'sha256': LEGACY_MANIFEST_SHA256, 'tree_sha256': None,
         'version': 'D2 legado (UN SNA)', 'authority_package_sha256': None},
    ]
    run_id = 'D2V-' + sha(canon({'tree': tree, 'producer': sha(producer.read_bytes()), 'reception': RECEPTION_TREE}))[:24]
    return {'schema_version': 'D2_VERSION_1', 'product_type': 'd2_cuentas_nacionales', 'run_id': run_id, 'created_at': created_at,
            'producer_path': 'herramientas/nacionales/construir_d2.py', 'producer_sha256': sha(producer.read_bytes()),
            'authority_package_sha256': authority['package_sha256'], 'authority_manifest_sha256': authority['manifest_sha256'],
            'contract_sha256': CONTRACT_SHA256, 'input_dependencies': deps, 'files': files, 'tree_sha256': tree,
            'phase_status': 'complete_incorporated_not_admitted'}


def verify_version(root: Path, tree: str) -> dict:
    """Verificador específico D2: archivos exactos, hashes, árbol y manifiesto (sin autorreferencia)."""
    root = Path(root)
    need(tree == APPROVED_TREE, 'árbol D2 distinto del aprobado')
    directory = root / PRODUCT / 'versions' / tree
    raw = (directory / MANIFEST_NAME).read_bytes()
    m = json.loads(raw)
    need(tuple(m) == MANIFEST_FIELDS, 'manifiesto D2 con campos distintos')
    need(m['schema_version'] == 'D2_VERSION_1' and m['product_type'] == 'd2_cuentas_nacionales', 'tipo de manifiesto D2')
    names = sorted(q.name for q in directory.iterdir() if q.is_file())
    need(names == sorted([f['path'] for f in m['files']] + [MANIFEST_NAME]), 'versión D2 ampliada o incompleta')
    for f in m['files']:
        data = (directory / f['path']).read_bytes()
        need(sha(data) == f['sha256'] and len(data) == f['bytes'], 'archivo D2 alterado: ' + f['path'])
        need(tree.encode() not in data, 'hash autorreferente')
    need(m['tree_sha256'] == tree == tree_of(m['files']), 'árbol D2 no reproducido')
    need(m['contract_sha256'] == CONTRACT_SHA256, 'contrato normativo D2')
    return {'tree_sha256': tree, 'manifest_sha256': sha(raw), 'authority_package_sha256': m['authority_package_sha256'],
            'authority_manifest_sha256': m['authority_manifest_sha256'], 'files': len(m['files'])}


def read_pointer(root: Path) -> tuple[dict, bytes]:
    raw = (Path(root) / POINTER).read_bytes()
    p = json.loads(raw)
    need(tuple(p) == POINTER_FIELDS and p['schema_version'] == 1 and p['product_type'] == 'd2_cuentas_nacionales', 'puntero D2 exacto')
    need(p['active_relative_path'] == 'versions/' + p['active_tree_sha256'] and p['active_tree_sha256'] in p['immutable_tree_sha256s'], 'puntero D2 incoherente')
    need(p['predecessor_reference'] == {'kind': 'legacy_output', 'path': 'output/d2_manifest.json', 'sha256': LEGACY_MANIFEST_SHA256}, 'predecesor D2 legado')
    return p, raw


def verify_active(root: Path, *, expected_tree: str, s3: dict) -> dict:
    """Selección explícita: el puntero activo debe apuntar al árbol pedido y la versión a la autoridad S3 verificada."""
    root = Path(root)
    need(expected_tree == APPROVED_TREE, 'selección D2 distinta de la versión aprobada')
    p, raw = read_pointer(root)
    need(p['active_tree_sha256'] == expected_tree, 'el puntero D2 no selecciona la versión aprobada pedida')
    info = verify_version(root, expected_tree)
    need(p['active_manifest_sha256'] == info['manifest_sha256'], 'puntero D2 y manifiesto incoherentes')
    need(info['authority_package_sha256'] == s3['package_sha256'], 'versión D2 no emitida bajo la autoridad S3 verificada')
    receipt_raw = (root / RECEIPTS / (expected_tree + '.json')).read_bytes()
    need(sha(receipt_raw) == p['promotion_receipt_sha256'], 'recibo de promoción D2 alterado')
    receipt = json.loads(receipt_raw)
    need(receipt['tree_sha256'] == expected_tree and receipt['manifest_sha256'] == info['manifest_sha256'], 'recibo D2 incoherente')
    need(legacy_intact(root), 'salida D2 legada alterada')
    return dict(info, pointer_sha256=sha(raw), promotion_receipt_sha256=p['promotion_receipt_sha256'])


def legacy_intact(root: Path) -> bool:
    return sha((Path(root) / LEGACY_MANIFEST).read_bytes()) == LEGACY_MANIFEST_SHA256


def publish(root: Path, *, s3_policy: str, s3_receipt: str, s3_author: str, authorization_sha256: str) -> dict:
    """Publica la versión aprobada tras verificar S3 y recomputar; el puntero se sustituye al final."""
    root = Path(root).resolve()
    need(root == ROOT.resolve(), 'raíz ajena al productor')
    from herramientas.congelamiento import s3_publicador as S3P
    authority = S3P.verify(root, s3_policy, s3_receipt, s3_author)
    need(authority['status'] == 'verified_S3', 'S3 no verificado')
    need(legacy_intact(root), 'salida D2 legada alterada antes de publicar')
    pointer_path = root / POINTER
    need(not pointer_path.exists(), 'ya existe un puntero D2 nuevo: no se sobrescribe')
    stage_parent = root / 'tmp/d2_version_staging'
    stage_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='d2_', dir=stage_parent) as temp:
        build = Path(temp) / 'build'
        result = recompute(build)
        need(result['tree_sha256'] == APPROVED_TREE, 'la recomputación no reproduce el árbol D2 aprobado: ' + result['tree_sha256'])
        staging = Path(temp) / APPROVED_TREE
        staging.mkdir()
        for name, data in result['data'].items():
            (staging / name).write_bytes(data)
        manifest = _manifest(APPROVED_TREE, result['files'], authority, now())
        (staging / MANIFEST_NAME).write_bytes(encoded(manifest))
        target = root / PRODUCT / 'versions' / APPROVED_TREE
        need(not target.exists(), 'destino inmutable ya existe')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(staging), str(target))
    info = verify_version(root, APPROVED_TREE)
    receipt = {'schema_version': 1, 'product_type': 'd2_cuentas_nacionales', 'tree_sha256': APPROVED_TREE,
               'manifest_sha256': info['manifest_sha256'], 'promoted_at': now(),
               'authorization': {'author_authorization_sha256': authorization_sha256, 'approval': 'A-06',
                                 's3_package_sha256': authority['package_sha256'], 's3_policy_sha256': s3_policy,
                                 's3_receipt_sha256': s3_receipt},
               'verifications': {'s3_verified': True, 'reception_verified': True, 'tree_recomputed_from_reception': True,
                                 'tree_equals_approved': True, 'version_verified': True, 'legacy_output_intact': True},
               'source_admission': False, 'model_execution': False}
    receipt_raw = encoded(receipt)
    (root / RECEIPTS).mkdir(parents=True, exist_ok=True)
    rpath = root / RECEIPTS / (APPROVED_TREE + '.json')
    need(not rpath.exists(), 'recibo ya existe')
    rpath.write_bytes(receipt_raw)
    pointer = {'schema_version': 1, 'product_type': 'd2_cuentas_nacionales', 'active_tree_sha256': APPROVED_TREE,
               'active_relative_path': 'versions/' + APPROVED_TREE, 'active_manifest_sha256': info['manifest_sha256'],
               'predecessor_reference': {'kind': 'legacy_output', 'path': 'output/d2_manifest.json', 'sha256': LEGACY_MANIFEST_SHA256},
               'promotion_receipt_sha256': sha(receipt_raw), 'immutable_tree_sha256s': [APPROVED_TREE]}
    temp = pointer_path.with_name(pointer_path.name + '.' + uuid.uuid4().hex)
    temp.write_bytes(encoded(pointer))
    os.replace(temp, pointer_path)
    return verify_active(root, expected_tree=APPROVED_TREE, s3=authority)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Versión D2 aprobada (1.5)')
    parser.add_argument('command', choices=['recomputar', 'verificar', 'publicar'])
    parser.add_argument('--d2-tree', default=None)
    parser.add_argument('--s3-policy-sha256'); parser.add_argument('--s3-receipt-sha256'); parser.add_argument('--s3-author')
    parser.add_argument('--authorization-sha256')
    args = parser.parse_args(argv)
    try:
        if args.command == 'recomputar':
            with tempfile.TemporaryDirectory(prefix='d2_recompute_', dir=ROOT / 'tmp') as temp:
                r = recompute(Path(temp))
            result = {'tree_sha256': r['tree_sha256'], 'equals_approved': r['tree_sha256'] == APPROVED_TREE, 'files': len(r['files'])}
        elif args.command == 'verificar':
            from herramientas.congelamiento import s3_publicador as S3P
            authority = S3P.verify(ROOT, args.s3_policy_sha256, args.s3_receipt_sha256, args.s3_author)
            result = verify_active(ROOT, expected_tree=args.d2_tree, s3=authority)
        else:
            result = publish(ROOT, s3_policy=args.s3_policy_sha256, s3_receipt=args.s3_receipt_sha256, s3_author=args.s3_author,
                             authorization_sha256=args.authorization_sha256)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ReceptionError, ValueError, OSError, KeyError) as exc:
        print('D2 RECHAZADO: ' + str(exc))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
