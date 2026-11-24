"""Publicación documental S3 (subpaso 1.5). No invoca productores económicos ni el modelo.

Sucesor de S2 (paquete 29654c6a…). Orden de confianza: código revisado local -> ancla externa de la política ->
inventarios cerrados (normativo aprobado, artefactos adoptados, autorización del autor, toolchain) -> recibo separado
con autor externo -> compuerta FZ-S3-TESTS-GREEN real en copia aislada -> transacción recuperable -> verificación.

S2 queda como antecedente verificable: su manifiesto, Markdown, ledger, puntero, descriptor, documentos y los bytes
de su toolchain se archivan en fase6_planes/freeze_history/<S2>/ y se reautentican con el validador histórico S2.
Ningún módulo de la toolchain S1 ni S2 se modifica: S3 solo añade módulos.

CLI (no pasa por congelar.py, cuyos bytes fija la toolchain S1):
  python herramientas/congelamiento/s3_publicador.py <comando> --s3-policy-sha256 … --s3-receipt-sha256 … --s3-author …
"""
from __future__ import annotations

import argparse
import copy
import csv
import io
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from herramientas.s3.validadores import s3_compat as S  # noqa: E402
from herramientas.s3.validadores.core import canon, sha, strict_json, inside, require  # noqa: E402
from herramientas.s3.validadores.temporal import instant  # noqa: E402
from herramientas.congelamiento import s2_publicador as S2P  # noqa: E402

MODE = S.MODE
S1 = S2P.S1
S2 = S.S2_PACKAGE
S2_JSON = S.S2_MANIFEST
S2_MD = 'a9ae7407b5b2b42843719f0eaa3d4d00fde1152657012a9f313eef967c622795'
STATUS = 'declared_post_data_amendment'
REASON = 'incorporate_1_5_A1E_v2_CA2_3_CA2_2X_r2_PER_V2_COL_2024p_reception_D2_with_author_authorization'
LIVE = S2P.LIVE
MD = S2P.MD
POINTER = S2P.POINTER
LEDGER = S2P.LEDGER
JOURNAL = 'fase6_planes/s3_pending_transaction.json'
CANDIDATE = 'herramientas/s3'
POLICY = CANDIDATE + '/s3/compatibilidad_s3.json'
SELECTION = CANDIDATE + '/s3/seleccion_candidata.json'
S2_INSTALLED = 'fase6_planes/integracion_s2/versions/' + S.S2_POLICY + '/'
S2_ARCHIVE = f'fase6_planes/freeze_history/{S2}/'
DOWNSTREAM_ABSENT = ('reports/official', 'fase2_datos/d6_tax_shares/input_snapshot.json', 'fase2_datos/d6_tax_shares/output',
                     'fase2_datos/d6_tax_shares/active_product.json', 'fase2_datos/d7_calibracion', 'fase2_datos/d8',
                     'fase2_datos/d6_tax_shares_v2', 'fase2_datos/d2_cuentas_nacionales/active_product.json',
                     'fase2_datos/d2_cuentas_nacionales/versions', 'fase2_datos/ca2_bundles', 'fase2_datos/certificados_reuso')
REQUIRED_TOOLCHAIN = {'herramientas/congelamiento/congelar.py', 'herramientas/congelamiento/s2_publicador.py',
                      'herramientas/congelamiento/s3_publicador.py', 'herramientas/pruebas/run_authoritative_suites.py',
                      'herramientas/pruebas/authoritative_lock.py', 'herramientas/pruebas/s3_gate.py',
                      'herramientas/d6/construir_d6.py', 'herramientas/d6/construir_d6_v2.py', 'herramientas/s3/run_suite.py',
                      'herramientas/integracion_1_5/run_suite.py',
                      'herramientas/nacionales/construir_d2.py', 'herramientas/d7/preparar_d7_a_v2.py',
                      'herramientas/dependent_documentation/dependent_documentation_v3.py',
                      'herramientas/ca2_bundles/construir_bundles.py', 'herramientas/reuso/certificados.py'}


def encoded(obj) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read(root, rel) -> bytes:
    return inside(Path(root), rel).read_bytes()


def get(root, rel):
    return strict_json(read(root, rel))


def prefix(pin) -> str:
    require(type(pin) is str and re.fullmatch('[a-f0-9]{64}', pin), 'pin externo S3 requerido')
    return 'fase6_planes/integracion_s3/versions/' + pin + '/'


def assert_no_pending(root) -> None:
    for journal in (S2P.JOURNAL, JOURNAL):
        require(not (Path(root) / journal).exists(), 'transacción pendiente: ' + journal + ' (recuperar antes de consumir)')


def local_freezer(root):
    return S2P.local_freezer(root)


# --------------------------------------------------------------------------------------------- S2 antecedente
def s2_manifest(root):
    for rel in (LIVE, S2_ARCHIVE + 'freeze_plans_manifest.json'):
        q = Path(root) / rel
        if q.is_file() and sha(q.read_bytes()) == S2_JSON:
            obj = strict_json(q.read_bytes())
            require(S.package(obj['documents']) == obj['package_sha256'] == S2, 'S2 auténtico')
            return obj, rel
    raise ValueError('S2 exacto ausente o alterado')


def s2_antecedent(root, *, require_archive=False) -> dict:
    """S2 verificable como antecedente, aun con toolchain viva ampliada por S3."""
    root = Path(root)
    obj, where = s2_manifest(root)
    live = where == LIVE
    require(not (require_archive and live), 'S2 debe estar archivado como antecedente')
    require(obj['s2']['policy_sha256'] == S.S2_POLICY and obj['s2']['approval_sha256'] == S.S2_RECEIPT, 'pines S2 del manifiesto')
    installed = root / S2_INSTALLED
    p2, a2 = S.s2_policy_and_receipt(installed, obj['freeze_plans_created_at'])
    observed = {q.relative_to(installed).as_posix() for q in installed.rglob('*') if q.is_file()}
    require(observed == set(p2['files']) | {'compatibilidad_s2.json', 'aprobacion_s2.json'}, 'versión S2 instalada ampliada o incompleta')
    for rel, meta in p2['files'].items():
        raw = (installed / rel).read_bytes()
        require(sha(raw) == meta['sha256'] and len(raw) == meta['bytes'], 'miembro S2 instalado alterado: ' + rel)
    traw = (installed / 'toolchain_manifest.json').read_bytes()
    require(sha(traw) == p2['toolchain_sha256'], 'toolchain S2 instalada')
    t = strict_json(traw)
    require(t['bundle_sha256'] == sha(canon(t['files'])), 'bundle S2')
    for rel, meta in t['files'].items():
        candidates = (root / rel, root / S2_ARCHIVE / 'toolchain' / rel)
        require(any(q.is_file() and sha(q.read_bytes()) == meta['sha256'] and q.stat().st_size == meta['bytes'] for q in candidates),
                'módulo de la toolchain S2 sin bytes auténticos (vivos o archivados): ' + rel)
    C = local_freezer(root)
    for row in obj['documents']:
        _, err = C._resolver_bytes_documento_fijado(S2, row['path'], row['sha256'])
        require(not err, 'documento S2 no resoluble: ' + str(err))
    ledger = read(root, LEDGER) if live else read(root, S2_ARCHIVE + 'evidence/compatibilidad_sucesiones.csv')
    require(sha(ledger) == obj['compatibility_ledger_sha256'], 'ledger S2')
    last = list(csv.reader(io.StringIO(ledger.decode('utf-8'))))[-1]
    require(last[:4] == [S1, S2, 'declared_post_data_amendment', S2P.REASON], 'arista S1->S2 del ledger')
    md = read(root, MD) if live else read(root, S2_ARCHIVE + 'freeze_plans_manifest.md')
    require(sha(md) == S2_MD, 'Markdown S2')
    require(sha(read(root, obj['candidate_selection_relative_path'])) == obj['candidate_selection_sha256'], 'descriptor S2')
    pointer = read(root, POINTER) if live else read(root, S2_ARCHIVE + 'evidence/selection_pointer.json')
    require(strict_json(pointer) == {'schema_version': 1, 'selection_path': obj['candidate_selection_relative_path']}, 'puntero S2')
    chain = S2P.historical_chain(root)
    return {'status': 'verified_S2_antecedent', 'package_sha256': S2, 'manifest_sha256': S2_JSON, 'live': live,
            'policy_sha256': S.S2_POLICY, 'receipt_sha256': S.S2_RECEIPT, 'author': a2['author'],
            'toolchain_modules': len(t['files']), 'chain': [S2] + chain}


# --------------------------------------------------------------------------------------------- candidato S3
def toolchain(root, directory, p) -> dict:
    raw = (Path(directory) / 'toolchain_manifest.json').read_bytes()
    require(sha(raw) == p['toolchain_sha256'], 'pin de toolchain S3')
    t = strict_json(raw)
    require(set(t) == {'schema_version', 'files', 'bundle_sha256'} and t['schema_version'] == 1, 'toolchain cerrada')
    require(type(t['files']) is dict and t['files'] and t['bundle_sha256'] == sha(canon(t['files'])), 'bundle S3')
    for rel, meta in t['files'].items():
        require(set(meta) == {'sha256', 'bytes'} and type(meta['bytes']) is int, 'toolchain metadatos')
        data = read(root, rel)
        require(sha(data) == meta['sha256'] and len(data) == meta['bytes'], 'módulo instalado alterado: ' + rel)
    require(REQUIRED_TOOLCHAIN <= set(t['files']), 'dependencias ejecutables obligatorias ausentes')
    observed = set()
    for folder in ('herramientas', 'fase2_datos', 'src'):
        for q in (Path(root) / folder).rglob('*.py'):
            if any(x in q.relative_to(root).parts for x in ('fixtures', '__pycache__', 'comprobaciones')):
                continue
            observed.add(q.relative_to(root).as_posix())
    require(observed == set(t['files']), 'inventario cerrado de módulos S3: omisión o miembro adicional')
    return t


def authenticate(root, pin, *, installed=False):
    root = Path(root)
    directory = root / prefix(pin) if installed else root / CANDIDATE
    require(directory.is_dir(), 'versión S3 instalada ausente para la política pedida' if installed else 'candidato S3 ausente')
    raw = (directory / 'compatibilidad_s3.json').read_bytes() if installed else read(root, POLICY)
    p = S.policy(raw, pin)
    S.inspect_candidate(directory, root, raw, pin)
    if not installed:
        require(get(root, SELECTION) == {'schema_version': 1, 'freeze_mode': MODE, 'active_plans': S.PLANS},
                'selección candidata S3 ambigua/incompleta/ampliada')
    t = toolchain(root, directory, p)
    if installed:
        observed = {q.relative_to(directory).as_posix() for q in directory.rglob('*') if q.is_file()}
        require(observed == set(p['files']) | {'compatibilidad_s3.json', 'aprobacion_s3.json'}, 'versión S3 instalada ampliada o incompleta')
    return p, raw, t, directory


def receipt(root, p, pin, receipt_hash, author, created_at, receipt_path, directory):
    require(type(receipt_hash) is str and re.fullmatch('[a-f0-9]{64}', receipt_hash), 'pin EXTERNO del recibo obligatorio')
    require(type(author) is str and bool(author.strip()), 'identidad de autor externa obligatoria')
    raw = read(root, receipt_path)
    auth_raw = (Path(directory) / S.AUTHORIZATION_PATH).read_bytes()
    return S.approved_receipt(raw, receipt_hash, p, pin, created_at, author, auth_raw), raw


def selection(s2, p, pin, receipt_hash):
    pre = prefix(pin)
    docs = copy.deepcopy(s2['documents'])
    additions = {pre + rel: meta['sha256'] for rel, meta in p['files'].items()}
    additions[pre + 'compatibilidad_s3.json'] = pin
    additions[pre + 'aprobacion_s3.json'] = receipt_hash
    require(not set(additions) & {r['path'] for r in docs}, 'S3 no sobrescribe pines históricos')
    docs += [{'path': k, 'sha256': v} for k, v in sorted(additions.items())]
    package = S.package(docs)
    descriptor = {'schema_version': 1, 'candidate_id': 'S3-' + pin, 'predecessor_package_sha256': S2,
                  'freeze_mode': MODE, 'compatibility_status': STATUS, 'supersedes_reason': REASON,
                  'documents': [row['path'] for row in docs], 'active_plans': [pre + x for x in S.PLANS],
                  'historical_plans': list(s2['selected_plan_paths_at_freeze']) + list(s2['s2']['historical_plans']),
                  'policy_sha256': pin, 'approval_sha256': receipt_hash}
    return docs, package, descriptor


def descriptor_path(pin, receipt_hash) -> str:
    return 'fase6_planes/freeze_candidates/s3_' + pin + '_' + receipt_hash + '.json'


def validate_selection(actual, expected) -> None:
    require(canon(actual) == canon(expected), 'selección S3 ambigua/incompleta/ampliada')
    require(len(actual['active_plans']) == len(set(actual['active_plans'])) == 3, 'tres planes activos únicos')
    require(not set(actual['active_plans']) & set(actual['historical_plans']), 'roles activo/histórico disjuntos')


def ledger_bytes(root, s2, package, approved_at):
    existing = read(root, LEDGER)
    if sha(existing) != s2['compatibility_ledger_sha256']:
        existing = read(root, S2_ARCHIVE + 'evidence/compatibilidad_sucesiones.csv')
    require(sha(existing) == s2['compatibility_ledger_sha256'] and existing.endswith(b'\n'), 'ledger S2 exacto')
    out = io.StringIO(newline='')
    csv.writer(out, lineterminator='\n').writerow([S2, package, STATUS, REASON, approved_at])
    return existing + out.getvalue().encode('utf-8'), existing


def check_gate(gate, s2, pin, prepared_sha) -> None:
    from herramientas.pruebas import s3_gate as G
    require(type(gate) is dict and set(gate) == {'gate', 'status', 'policy_sha256', 'prepared_sha256', 'started_at', 'finished_at',
                                                'errors', 'boundary', 'suites'}, 'compuerta S3 completa')
    require(gate['gate'] == 'FZ-S3-TESTS-GREEN' and gate['status'] == 'GREEN' and gate['errors'] == [], 'compuerta S3 real requerida')
    require(gate != s2['tests_gate'] and gate['policy_sha256'] == pin and gate['prepared_sha256'] == prepared_sha, 'no reutilizar compuerta')
    require(instant(gate['started_at']) <= instant(gate['finished_at']), 'fechas de compuerta')
    require(gate['boundary'].get('package_sha256') == G.S1 and gate['boundary'].get('manifest_sha256') == G.S1_JSON, 'frontera S1 exacta')
    expected = G.s3_gate_contract()
    suites = gate['suites']
    require(type(suites) is list and len(suites) == len(expected), 'todas las suites S3')
    for row, (path, floor, boundary) in zip(suites, expected):
        require(row['path'] == path and row['minimum_expected'] == floor and row['boundary'] == boundary, 'orden/pisos/fronteras de compuerta')
        require(row['returncode'] == 0 and type(row['total']) is int and row['total'] >= floor and row['passed'] == row['total'], 'suite incompleta: ' + path)
        require(row['ast_total'] == row['total'], 'descubrimiento real coherente: ' + path)
        if boundary == 'vivo_S2_pre_S3':
            require(row['discovered'] == row['total'] and row['skipped'] == 0, 'suite S3 sin omisiones: ' + path)
        else:
            require(row['main_block_last'] is True, 'corredor inline histórico: ' + path)
        require(re.fullmatch('[a-f0-9]{64}', row['output_sha256']) is not None, 'salida de suite ausente')


def snapshot(root, p, t, directory) -> dict:
    """Todas las entradas autoritativas (incluida la historia) se re-hashean alrededor de compuerta y promoción."""
    root = Path(root)
    result = {}
    for folder in ('fase1_literatura', 'fase2_datos', 'fase3_metodologia', 'fase4_teoria', 'fase5_cuantificacion', 'fase6_planes',
                   'contracts', 'environment', 'src', 'reports'):
        for q in (root / folder).rglob('*'):
            if q.is_file() and q.relative_to(root).as_posix() not in (JOURNAL, S2P.JOURNAL):
                result[q.relative_to(root).as_posix()] = sha(q.read_bytes())
    for rel in t['files']:
        result[rel] = sha(read(root, rel))
    for rel in p['files']:
        result['candidate:' + rel] = sha((Path(directory) / rel).read_bytes())
    result['candidate:policy'] = sha(read(root, POLICY))
    result['candidate:selection'] = sha(read(root, SELECTION))
    return result


def prepare(root, pin, rh, author, receipt_path, created_at):
    root = Path(root)
    assert_no_pending(root)
    require(sha(read(root, LIVE)) == S2_JSON, 'S3 requiere S2 vigente exacto')
    p, raw, t, directory = authenticate(root, pin)
    s2, _ = s2_manifest(root)
    antecedent = s2_antecedent(root)
    r, rraw = receipt(root, p, pin, rh, author, created_at, receipt_path, directory)
    require(instant(created_at) > instant(s2['freeze_plans_created_at']), 'sucesor posterior a S2')
    C = local_freezer(root)
    failures, _ = C._validar_adquisicion()
    require(not failures, 'adquisición inválida: ' + '; '.join(failures))
    require(sha(read(root, 'fase2_datos/acquisition_manifest.csv')) == s2['acquisition_manifest_sha256_at_freeze'], 'adquisición cambió desde S2')
    require(sha(read(root, 'fase2_datos/source_catalog/source_catalog.csv')) == s2['source_catalog_sha256'], 'catálogo cambió desde S2')
    for rel in DOWNSTREAM_ABSENT:
        require(not (root / rel).exists(), 'producto posterior a S3 ya presente: ' + rel)
    from herramientas.nacionales.base import verify_reception
    require(verify_reception(root)['tree_sha256'] == S.RECEPTION_TREE, 'recepción nacional instalada distinta')
    docs, package, desc = selection(s2, p, pin, rh)
    ledger, oldledger = ledger_bytes(root, s2, package, r['approved_at'])
    desc_path = descriptor_path(pin, rh)
    proof = {'policy_sha256': pin, 'receipt_sha256': rh, 'expected_author': author, 'created_at': created_at,
             'descriptor': desc, 'antecedent': antecedent, 'snapshot': snapshot(root, p, t, directory)}
    return dict(p=p, raw=raw, t=t, directory=directory, s2=s2, r=r, rraw=rraw, docs=docs, package=package, desc=desc,
                desc_path=desc_path, ledger=ledger, oldledger=oldledger, proof=proof, proof_sha=sha(canon(proof)))


def emitted(pre, gate):
    s2 = pre['s2']
    pin = pre['proof']['policy_sha256']
    rh = pre['proof']['receipt_sha256']
    check_gate(gate, s2, pin, pre['proof_sha'])
    obj = copy.deepcopy(s2)
    obj.update(freeze_mode=MODE, freeze_plans_created_at=pre['proof']['created_at'], package_sha256=pre['package'],
               supersedes_package_sha256=S2, supersedes_reason=REASON, successor_compatibility_status=STATUS,
               compatibility_status=STATUS, candidate_selection_id=pre['desc']['candidate_id'],
               candidate_selection_relative_path=pre['desc_path'], candidate_selection_sha256=sha(encoded(pre['desc'])),
               tests_gate=gate, changed_documents=[], removed_documents=[],
               added_documents=[x['path'] for x in pre['docs'][len(s2['documents']):]],
               compatibility_ledger_sha256=sha(pre['ledger']), documents=pre['docs'],
               selected_plan_paths_at_freeze=pre['desc']['active_plans'],
               selected_plan_sha256s_at_freeze=[pre['p']['files'][rel]['sha256'] for rel in S.PLANS],
               note='S3 documental (1.5): planes y contratos aprobados por el autor, CA2-3/macro-ca2-v2, CA2-2X r2 con despacho, '
                    'autoridades PER V2 y COL 2024p, recepción nacional y D2 aprobado. Sin admisión de fuentes, sin modelo ni resultados.')
    obj['s3'] = {'policy_sha256': pin, 'approval_sha256': rh, 'authorization_sha256': pre['p']['authorization_sha256'],
                 'contract_sha256': pre['p']['contract_sha256'], 'toolchain_sha256': pre['p']['toolchain_sha256'],
                 'bundle_sha256': pre['t']['bundle_sha256'], 'prepared_sha256': pre['proof_sha'],
                 'historical_plans': pre['desc']['historical_plans'], 'adopted': copy.deepcopy(pre['p']['adopted']),
                 'predecessor': {'package_sha256': S2, 'manifest_sha256': S2_JSON, 'policy_sha256': S.S2_POLICY,
                                 'receipt_sha256': S.S2_RECEIPT, 'archive': S2_ARCHIVE},
                 'scope': S.scope(), 'production_activation': False, 'model_execution': False}
    return obj


def markdown(obj) -> bytes:
    return ('# Congelamiento documental S3 (subpaso 1.5)\n\nPaquete: `' + obj['package_sha256'] + '`\n\nSucede a S2 `' + S2 + '`.\n\n'
            + obj['note'] + '\n\nPlanes activos:\n' + ''.join('- ' + x + '\n' for x in obj['selected_plan_paths_at_freeze'])
            + '\nAutorización del autor: `' + obj['s3']['authorization_sha256'] + '`. Recibo separado: `'
            + obj['s3']['approval_sha256'] + '`.\n').encode('utf-8')


def transaction(root, outputs, revalidate, validate_promoted=lambda: None):
    """Commit multiarchivo recuperable (mismo protocolo que S2, journal propio). JSON vivo al final."""
    root = Path(root).resolve()
    assert_no_pending(root)
    ident = uuid.uuid4().hex
    stage = root / 'tmp/s3_transactions' / ident
    stage.mkdir(parents=True)
    rows = []
    for i, (rel, data) in enumerate(outputs.items()):
        target = inside(root, rel)
        before = target.read_bytes() if target.exists() else None
        if before == data:
            continue
        new = stage / f'{i}.new'
        new.write_bytes(data)
        require(new.read_bytes() == data, 'escritura temporal incompleta')
        old = None
        if before is not None:
            old = stage / f'{i}.old'
            old.write_bytes(before)
            require(old.read_bytes() == before, 'backup incompleto')
        rows.append({'path': rel, 'old': old.relative_to(root).as_posix() if old else None,
                     'old_sha256': sha(before) if before is not None else None,
                     'new': new.relative_to(root).as_posix(), 'new_sha256': sha(data)})
    revalidate()
    journal = {'schema_version': 1, 'rows': rows}
    j = root / JOURNAL
    jtemp = stage / 'journal.new'
    jtemp.write_bytes(encoded(journal))
    require(jtemp.read_bytes() == encoded(journal), 'journal temporal incompleto')
    os.replace(jtemp, j)
    try:
        require(j.read_bytes() == encoded(journal), 'journal incompleto')
        revalidate()
        for row in rows:
            q = inside(root, row['path'])
            current = sha(q.read_bytes()) if q.exists() else None
            require(current == row['old_sha256'], 'TOCTOU destino: ' + row['path'])
            data = read(root, row['new'])
            require(sha(data) == row['new_sha256'], 'TOCTOU staging')
            q.parent.mkdir(parents=True, exist_ok=True)
            temp = q.with_name(q.name + '.s3-' + ident)
            temp.write_bytes(data)
            require(sha(temp.read_bytes()) == row['new_sha256'], 'escritura de promoción')
            os.replace(temp, q)
        require(all(sha(read(root, r['path'])) == r['new_sha256'] for r in rows), 'promoción incompleta')
        validate_promoted()
    except BaseException:
        recover(root)
        raise
    j.unlink()
    (stage / 'committed.json').write_bytes(encoded({'status': 'committed', 'rows': rows}))
    return ident


def recover(root):
    root = Path(root)
    j = root / JOURNAL
    if not j.exists():
        return {'status': 'no_pending_transaction'}
    obj = get(root, JOURNAL)
    require(set(obj) == {'schema_version', 'rows'} and obj['schema_version'] == 1, 'journal inválido')
    for row in reversed(obj['rows']):
        q = inside(root, row['path'])
        current = sha(q.read_bytes()) if q.exists() else None
        require(current in (row['old_sha256'], row['new_sha256']), 'recuperación: cambio ajeno en ' + row['path'])
        if current == row['old_sha256']:
            continue
        if row['old'] is None:
            q.unlink()
        else:
            raw = read(root, row['old'])
            require(sha(raw) == row['old_sha256'], 'backup alterado')
            temp = q.with_name(q.name + '.s3-restore')
            temp.write_bytes(raw)
            os.replace(temp, q)
        require((sha(q.read_bytes()) if q.exists() else None) == row['old_sha256'], 'restauración fallida')
    j.unlink()
    return {'status': 'rolled_back', 'files': len(obj['rows'])}


def publish(root, pin, rh, author, receipt_path, *, log_dir):
    from herramientas.pruebas import s3_gate as G
    from herramientas.pruebas.authoritative_lock import interprocess_lock
    root = Path(root)
    with interprocess_lock(owner_label='S3-publicador'):
        created = now()
        pre = prepare(root, pin, rh, author, receipt_path, created)
        gate = G.run_s3_gate(pin, pre['proof_sha'], Path(log_dir))
        require(prepare(root, pin, rh, author, receipt_path, created)['proof'] == pre['proof'], 'TOCTOU durante compuerta')
        obj = emitted(pre, gate)
        out = {}
        s2 = pre['s2']
        for rel, name in ((LIVE, 'freeze_plans_manifest.json'), (MD, 'freeze_plans_manifest.md'),
                          (LEDGER, 'evidence/compatibilidad_sucesiones.csv'), (POINTER, 'evidence/selection_pointer.json')):
            out[S2_ARCHIVE + name] = read(root, rel)
        out[S2_ARCHIVE + 'evidence/freeze_candidate_selection.json'] = read(root, s2['candidate_selection_relative_path'])
        C = local_freezer(root)
        for row in s2['documents']:
            path, err = C._resolver_bytes_documento_fijado(S2, row['path'], row['sha256'])
            require(not err, str(err))
            out[S2_ARCHIVE + 'documents/' + row['path']] = path.read_bytes()
        t2 = strict_json((root / S2_INSTALLED / 'toolchain_manifest.json').read_bytes())
        for rel, meta in t2['files'].items():
            data = read(root, rel)
            require(sha(data) == meta['sha256'], 'toolchain S2 viva alterada antes de archivar: ' + rel)
            out[S2_ARCHIVE + 'toolchain/' + rel] = data
        dest = prefix(pin)
        for rel in pre['p']['files']:
            out[dest + rel] = (pre['directory'] / rel).read_bytes()
        out[dest + 'compatibilidad_s3.json'] = pre['raw']
        out[dest + 'aprobacion_s3.json'] = pre['rraw']
        out[pre['desc_path']] = encoded(pre['desc'])
        for rel, data in out.items():
            q = inside(root, rel)
            require(not q.exists() or q.read_bytes() == data, 'destino inmutable existente distinto: ' + rel)
        out[LEDGER] = pre['ledger']
        out[POINTER] = encoded({'schema_version': 1, 'selection_path': pre['desc_path']})
        out[MD] = markdown(obj)
        out[LIVE] = encoded(obj)

        def revalidate():
            require(snapshot(root, pre['p'], pre['t'], pre['directory']) == pre['proof']['snapshot'], 'TOCTOU antes de promoción')
            require(sha(read(root, receipt_path)) == rh, 'TOCTOU recibo')
        ident = transaction(root, out, revalidate, lambda: verify(root, pin, rh, author, _allow_pending=True))
        result = verify(root, pin, rh, author)
        return dict(result, transaction=ident)


def verify(root, pin, rh, author, *, _allow_pending=False):
    root = Path(root)
    if not _allow_pending:
        assert_no_pending(root)
    p, raw, t, directory = authenticate(root, pin, installed=True)
    live_raw = read(root, LIVE)
    actual = strict_json(live_raw)
    require(actual.get('freeze_mode') == MODE, 'S3 no vigente')
    antecedent = s2_antecedent(root, require_archive=True)
    s2, _ = s2_manifest(root)
    r, _ = receipt(root, p, pin, rh, author, actual['freeze_plans_created_at'], prefix(pin) + 'aprobacion_s3.json', directory)
    docs, package, desc = selection(s2, p, pin, rh)
    ledger, _ = ledger_bytes(root, s2, package, r['approved_at'])
    pre = dict(s2=s2, p=p, t=t, docs=docs, package=package, desc=desc, desc_path=descriptor_path(pin, rh), ledger=ledger,
               proof={'policy_sha256': pin, 'receipt_sha256': rh, 'created_at': actual['freeze_plans_created_at']},
               proof_sha=actual['s3']['prepared_sha256'])
    require(canon(actual) == canon(emitted(pre, actual['tests_gate'])), 'manifiesto S3 completo alterado/herencia incorrecta')
    require(instant(r['approved_at']) <= instant(p['created_at']) <= instant(r['bound_at']) <= instant(actual['freeze_plans_created_at'])
            <= instant(actual['tests_gate']['started_at']), 'secuencia de emisión S3')
    validate_selection(get(root, pre['desc_path']), desc)
    require(get(root, POINTER) == {'schema_version': 1, 'selection_path': pre['desc_path']}, 'puntero de selección incoherente')
    require(read(root, MD) == markdown(actual), 'Markdown incoherente')
    require(read(root, LEDGER) == ledger, 'arista específica/ledger alterado')
    C = local_freezer(root)
    for row in docs:
        _, err = C._resolver_bytes_documento_fijado(package, row['path'], row['sha256'])
        require(not err, 'documento instalado/fijado alterado: ' + str(err))
    require(sha(read(root, S2_ARCHIVE + 'freeze_plans_manifest.json')) == S2_JSON, 'archivo S2 modificado')
    chain = [package] + antecedent['chain']
    return {'status': 'verified_S3', 'package_sha256': package, 'manifest_sha256': sha(live_raw), 'chain': chain,
            'chain_length': len(chain), 'active_plans': desc['active_plans'], 'authorization_sha256': p['authorization_sha256'],
            'approved_at': r['approved_at'], 'contract_sha256': p['contract_sha256'], 'adopted': p['adopted'],
            'scope': p['scope'], 'predecessor': {'package_sha256': S2, 'status': antecedent['status']},
            'installed_prefix': prefix(pin), 'production_activation': False, 'model_execution': False}


def main(argv, root=ROOT):
    parser = argparse.ArgumentParser(description='Publicación documental S3 (1.5)')
    parser.add_argument('command', choices=['verificar-candidato', 'verificar', 'verificar-cadena', 'verificar-antecedente-s2',
                                            'congelar', 'recuperar-s3'])
    parser.add_argument('--s3-policy-sha256')
    parser.add_argument('--s3-receipt-sha256')
    parser.add_argument('--s3-author')
    parser.add_argument('--s3-receipt')
    parser.add_argument('--s3-log-dir', default='tmp/s3_gate_logs')
    args = parser.parse_args(argv)
    try:
        root = Path(root).resolve()
        if args.command == 'recuperar-s3':
            from herramientas.pruebas.authoritative_lock import interprocess_lock
            with interprocess_lock(owner_label='S3-recovery'):
                result = recover(root)
        elif args.command == 'verificar-antecedente-s2':
            result = s2_antecedent(root)
            result['chain_length'] = len(result['chain'])
        elif args.command == 'verificar-candidato':
            p, _, t, _ = authenticate(root, args.s3_policy_sha256)
            antecedent = s2_antecedent(root)
            result = {'candidate_integrity': 'pass', 'approval_present': False, 'activation': False, 'active_plans': p['active_plans'],
                      'toolchain_modules': len(t['files']), 'antecedent': antecedent['status']}
            if args.s3_receipt:
                pre = prepare(root, args.s3_policy_sha256, args.s3_receipt_sha256, args.s3_author, args.s3_receipt, now())
                result.update(package_sha256=pre['package'], approval_present=True, prepared_sha256=pre['proof_sha'])
        elif args.command == 'congelar':
            require(args.s3_receipt is not None, 'recibo S3 ausente')
            logdir = inside(root, args.s3_log_dir)
            logdir.mkdir(parents=True, exist_ok=True)
            result = publish(root, args.s3_policy_sha256, args.s3_receipt_sha256, args.s3_author, args.s3_receipt, log_dir=logdir)
        else:
            result = verify(root, args.s3_policy_sha256, args.s3_receipt_sha256, args.s3_author)
            if args.command == 'verificar-cadena':
                result = {'status': result['status'], 'chain_length': result['chain_length'], 'chain': result['chain']}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, RuntimeError) as exc:
        print('S3 RECHAZADO: ' + str(exc))
        return 1


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
