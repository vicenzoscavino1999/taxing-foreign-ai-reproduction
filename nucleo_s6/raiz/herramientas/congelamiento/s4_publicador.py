"""Publicación S4 (bloque 2, CANDIDATA SIN EMITIR): autoridad consumidora sucesora de S3 para D7/B/D8.

Mismo orden de confianza que S3: código revisado -> ancla externa de la política S4 -> inventarios cerrados (decisión,
autorización del autor, toolchain completa con los módulos del bloque 2) -> recibo separado con autor externo ->
compuerta real en copia aislada -> transacción recuperable -> verificación.

S3 queda como antecedente verificable (s3_antecedent): su manifiesto, Markdown, ledger, puntero, descriptor, documentos y
los bytes de su toolchain se archivan en fase6_planes/freeze_history/<S3>/ y se reautentican con el validador S3
(s3_compat) sin exigir su inventario cerrado de módulos (ampliado legítimamente por S4). Ningún módulo S1/S2/S3 se
modifica. D2, D6 v2, bundles CA2 y certificados siguen autenticándose con la autoridad S3 (antecedente).

Ensayo aislado: solo en una raíz con la marca ENSAYO_AISLADO_S4.json se acepta aprobación FICTICIA. La raíz original no
tiene la marca: allí toda aprobación ficticia se rechaza.

Compuerta (bloque 3, corrige H-1): UNA sola lógica para la compuerta real y la de ensayo (solo cambian el nombre y la
autoridad registrada): 11 suites históricas en sus fronteras S1/1dda; las 2 suites S3 (s3, integración 1.5) en la
FRONTERA S3 RECONSTRUIDA (herramientas/s4/frontera_s3.py: el control de inventario cerrado S3 se conserva y pasa allí);
la batería del bloque 2 sobre los bytes del candidato con piso exacto y su informe ligado (V02/V03); inventario cerrado S4
y transición S3->S4 comprobados; entorno del perfil 'integracion' exigido al proceso de la compuerta y comprobado en una
sonda hija con el mismo intérprete. El resultado identifica frontera, código, suite, entorno y autoridad comprobados.

Corrección R1 (revisión B3-4): check_gate exige SIEMPRE el contexto completo (política, toolchains S3 y S4
autenticadas, raíz) y deriva de fuentes autenticadas cada campo que comprueba: fronteras S1 (archivo S1) y S3
(frontera_s3.descriptor_esperado), transición exacta, código (pin y bundle S4), entorno (huella INCRUSTADA, recalculada y
comparada con el manifiesto y el lock de la política), informe de la batería (INCRUSTADO byte a byte: su hash, su
resumen y su identidad de código y de suite, recalculada en la raíz con ejecutar_b.code_manifest_sha256). Las rutas de
publicación (emitted) y verificación (verify) pasan ese contexto; nada se omite por parámetros opcionales.

CLI: python herramientas/congelamiento/s4_publicador.py <comando> --s4-policy-sha256 … --s4-receipt-sha256 … --s4-author …
"""
from __future__ import annotations

import argparse
import copy
import csv
import io
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from herramientas.s3.validadores import s3_compat as S3C  # noqa: E402
from herramientas.s3.validadores.core import canon, sha, strict_json, inside, require  # noqa: E402
from herramientas.s3.validadores.temporal import instant  # noqa: E402
from herramientas.s4.validadores import s4_compat as S4C  # noqa: E402
from herramientas.congelamiento import s3_publicador as S3P  # noqa: E402
from herramientas.bloque2 import entorno_sucesor as ES  # noqa: E402

MODE = S4C.MODE
S3 = S4C.S3_PACKAGE
S3_JSON = S4C.S3_MANIFEST
STATUS = 'declared_consumer_authority_successor'
REASON = 'block2_D7_B_D8_consumer_authority_with_author_authorization'
LIVE, MD, POINTER, LEDGER = S3P.LIVE, S3P.MD, S3P.POINTER, S3P.LEDGER
JOURNAL = 'fase6_planes/s4_pending_transaction.json'
CANDIDATE = 'herramientas/s4'
POLICY = CANDIDATE + '/s4/compatibilidad_s4.json'
SELECTION = CANDIDATE + '/s4/seleccion_candidata.json'
S3_INSTALLED = S3P.prefix(S4C.S3_POLICY)
S3_ARCHIVE = f'fase6_planes/freeze_history/{S3}/'
TRIAL_MARK = 'ENSAYO_AISLADO_S4.json'
FAMILIES_ABSENT = ('fase2_datos/d7_calibracion', 'fase2_datos/b_frontera', 'fase2_datos/d8', 'reports/official')
BLOCK2_SUITES = (('herramientas/bloque2/run_suite.py', 325),)    # piso = conteo exacto revisado (bloque 3, revisión R1-R3)
FRONTERA_S3 = 'frontera_S3_reconstruida'
CANDIDATO_S4 = 'candidato_S4'
GATE_KEYS = {'gate', 'status', 'policy_sha256', 'prepared_sha256', 'started_at', 'finished_at', 'errors', 'boundary', 'suites',
             'environment', 'code', 'transition', 'authority'}
REQUIRED_TOOLCHAIN = S3P.REQUIRED_TOOLCHAIN | {
    'herramientas/congelamiento/s4_publicador.py', 'herramientas/s4/validadores/s4_compat.py',
    'herramientas/s4/preparar_candidato.py', 'herramientas/d7/construir_d7.py', 'herramientas/b/ejecutar_b.py',
    'herramientas/d8/auditor.py', 'herramientas/bloque2/autoridad.py', 'herramientas/bloque2/familias.py',
    'herramientas/bloque2/sintetico.py', 'herramientas/bloque2/run_suite.py', 'src/paper2b/run.py', 'src/paper2b/model.py',
    'src/paper2b/supremum.py', 'src/paper2b/rules.py', 'src/paper2b/d7build.py', 'herramientas/s4/frontera_s3.py',
    'herramientas/s4/paquete_a.py', 'herramientas/bloque2/entorno_sucesor.py'}


def encoded(obj) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read(root, rel) -> bytes:
    return inside(Path(root), rel).read_bytes()


def get(root, rel):
    return strict_json(read(root, rel))


def prefix(pin) -> str:
    require(type(pin) is str and re.fullmatch('[a-f0-9]{64}', pin), 'pin externo S4 requerido')
    return 'fase6_planes/integracion_s4/versions/' + pin + '/'


def trial(root) -> bool:
    """Raíz de ensayo aislado: marca exacta presente. La raíz original nunca la contiene."""
    q = Path(root) / TRIAL_MARK
    if not q.is_file():
        return False
    m = strict_json(q.read_bytes())
    require(m == {'schema_version': 1, 'kind': S4C.FICTITIOUS, 'purpose': 'ensayo aislado del mecanismo S4',
                  'authorizes_nothing_in_original': True}, 'marca de ensayo S4 inválida')
    return True


def assert_no_pending(root) -> None:
    for journal in ('fase6_planes/s2_pending_transaction.json', S3P.JOURNAL, JOURNAL):
        require(not (Path(root) / journal).exists(), 'transacción pendiente: ' + journal + ' (recuperar antes de consumir)')


# --------------------------------------------------------------------------------------------- S3 antecedente
def s3_manifest(root):
    for rel in (LIVE, S3_ARCHIVE + 'freeze_plans_manifest.json'):
        q = Path(root) / rel
        if q.is_file() and sha(q.read_bytes()) == S3_JSON:
            obj = strict_json(q.read_bytes())
            require(S3C.package(obj['documents']) == obj['package_sha256'] == S3, 'S3 auténtico')
            return obj, rel
    raise ValueError('S3 exacto ausente o alterado')


def s3_antecedent(root, *, require_archive=False) -> dict:
    """S3 verificable como antecedente, aun con toolchain viva ampliada por el bloque 2 / S4."""
    root = Path(root)
    obj, where = s3_manifest(root)
    live = where == LIVE
    require(not (require_archive and live), 'S3 debe estar archivado como antecedente')
    require(obj['s3']['policy_sha256'] == S4C.S3_POLICY and obj['s3']['approval_sha256'] == S4C.S3_RECEIPT, 'pines S3 del manifiesto')
    installed = root / S3_INSTALLED
    raw = (installed / 'compatibilidad_s3.json').read_bytes()
    S3C.inspect_candidate(installed, root, raw, S4C.S3_POLICY)
    p3 = S3C.policy(raw, S4C.S3_POLICY)
    observed = {q.relative_to(installed).as_posix() for q in installed.rglob('*') if q.is_file()}
    require(observed == set(p3['files']) | {'compatibilidad_s3.json', 'aprobacion_s3.json'}, 'versión S3 instalada ampliada o incompleta')
    S3C.approved_receipt((installed / 'aprobacion_s3.json').read_bytes(), S4C.S3_RECEIPT, p3, S4C.S3_POLICY,
                         obj['freeze_plans_created_at'], S4C.S3_AUTHOR, (installed / S3C.AUTHORIZATION_PATH).read_bytes())
    traw = (installed / 'toolchain_manifest.json').read_bytes()
    require(sha(traw) == p3['toolchain_sha256'], 'toolchain S3 instalada')
    t = strict_json(traw)
    require(t['bundle_sha256'] == sha(canon(t['files'])), 'bundle S3')
    for rel, meta in t['files'].items():
        candidates = (root / rel, root / S3_ARCHIVE / 'toolchain' / rel)
        require(any(q.is_file() and sha(q.read_bytes()) == meta['sha256'] and q.stat().st_size == meta['bytes'] for q in candidates),
                'módulo de la toolchain S3 sin bytes auténticos (vivos o archivados): ' + rel)
    C = S3P.local_freezer(root)
    for row in obj['documents']:
        _, err = C._resolver_bytes_documento_fijado(S3, row['path'], row['sha256'])
        require(not err, 'documento S3 no resoluble: ' + str(err))
    ledger = read(root, LEDGER) if live else read(root, S3_ARCHIVE + 'evidence/compatibilidad_sucesiones.csv')
    require(sha(ledger) == obj['compatibility_ledger_sha256'], 'ledger S3')
    last = list(csv.reader(io.StringIO(ledger.decode('utf-8'))))[-1]
    require(last[:4] == [S3P.S2, S3, S3P.STATUS, S3P.REASON], 'arista S2->S3 del ledger')
    md = read(root, MD) if live else read(root, S3_ARCHIVE + 'freeze_plans_manifest.md')
    require(md == S3P.markdown(obj), 'Markdown S3')
    require(sha(read(root, obj['candidate_selection_relative_path'])) == obj['candidate_selection_sha256'], 'descriptor S3')
    pointer = read(root, POINTER) if live else read(root, S3_ARCHIVE + 'evidence/selection_pointer.json')
    require(strict_json(pointer) == {'schema_version': 1, 'selection_path': obj['candidate_selection_relative_path']}, 'puntero S3')
    s2 = S3P.s2_antecedent(root, require_archive=True)
    return {'status': 'verified_S3_antecedent', 'package_sha256': S3, 'manifest_sha256': S3_JSON, 'live': live,
            'policy_sha256': S4C.S3_POLICY, 'receipt_sha256': S4C.S3_RECEIPT, 'contract_sha256': p3['contract_sha256'],
            'adopted': p3['adopted'], 'scope': p3['scope'], 'installed_prefix': S3_INSTALLED,
            'mex_authority_sha256': p3['mex_authority']['sha256'], 'toolchain_modules': len(t['files']), 'chain': [S3] + s2['chain']}


# --------------------------------------------------------------------------------------------- candidato S4
def toolchain_files(root) -> dict:
    out = {}
    for folder in ('herramientas', 'fase2_datos', 'src'):
        for q in (Path(root) / folder).rglob('*.py'):
            if any(x in q.relative_to(root).parts for x in ('fixtures', '__pycache__', 'comprobaciones')):
                continue
            raw = q.read_bytes()
            out[q.relative_to(root).as_posix()] = {'sha256': sha(raw), 'bytes': len(raw)}
    return dict(sorted(out.items()))


def toolchain(root, directory, p) -> dict:
    raw = (Path(directory) / 'toolchain_manifest.json').read_bytes()
    require(sha(raw) == p['toolchain_sha256'], 'pin de toolchain S4')
    t = strict_json(raw)
    require(set(t) == {'schema_version', 'files', 'bundle_sha256'} and t['schema_version'] == 1, 'toolchain cerrada')
    require(type(t['files']) is dict and t['files'] and t['bundle_sha256'] == sha(canon(t['files'])), 'bundle S4')
    for rel, meta in t['files'].items():
        require(set(meta) == {'sha256', 'bytes'} and type(meta['bytes']) is int, 'toolchain metadatos')
        data = read(root, rel)
        require(sha(data) == meta['sha256'] and len(data) == meta['bytes'], 'módulo instalado alterado: ' + rel)
    require(REQUIRED_TOOLCHAIN <= set(t['files']), 'dependencias ejecutables obligatorias ausentes: ' +
            ','.join(sorted(REQUIRED_TOOLCHAIN - set(t['files']))[:5]))
    require(set(toolchain_files(root)) == set(t['files']), 'inventario cerrado de módulos S4: omisión o miembro adicional')
    return t


def authenticate(root, pin, *, installed=False):
    root = Path(root)
    fict = trial(root)
    directory = root / prefix(pin) if installed else root / CANDIDATE
    require(directory.is_dir(), 'versión S4 instalada ausente para la política pedida' if installed else 'candidato S4 ausente')
    raw = (directory / 'compatibilidad_s4.json').read_bytes() if installed else read(root, POLICY)
    p = S4C.policy(raw, pin, allow_fictitious=fict)
    S4C.inspect_candidate(directory, root, raw, pin, allow_fictitious=fict)
    if not installed:
        require(get(root, SELECTION) == {'schema_version': 1, 'freeze_mode': MODE}, 'selección candidata S4 ambigua/ampliada')
    t = toolchain(root, directory, p)
    if installed:
        observed = {q.relative_to(directory).as_posix() for q in directory.rglob('*') if q.is_file()}
        require(observed == set(p['files']) | {'compatibilidad_s4.json', 'aprobacion_s4.json'}, 'versión S4 instalada ampliada o incompleta')
    return p, raw, t, directory


def receipt(root, p, pin, receipt_hash, author, created_at, receipt_path, directory):
    require(type(receipt_hash) is str and re.fullmatch('[a-f0-9]{64}', receipt_hash), 'pin EXTERNO del recibo obligatorio')
    require(type(author) is str and bool(author.strip()), 'identidad de autor externa obligatoria')
    raw = read(root, receipt_path)
    auth_raw = (Path(directory) / S4C.AUTHORIZATION_PATH).read_bytes()
    return S4C.approved_receipt(raw, receipt_hash, p, pin, created_at, author, auth_raw), raw


def selection(s3obj, p, pin, receipt_hash):
    pre = prefix(pin)
    docs = copy.deepcopy(s3obj['documents'])
    additions = {pre + rel: meta['sha256'] for rel, meta in p['files'].items()}
    additions[pre + 'compatibilidad_s4.json'] = pin
    additions[pre + 'aprobacion_s4.json'] = receipt_hash
    require(not set(additions) & {r['path'] for r in docs}, 'S4 no sobrescribe pines históricos')
    docs += [{'path': k, 'sha256': v} for k, v in sorted(additions.items())]
    package = S3C.package(docs)
    descriptor = {'schema_version': 1, 'candidate_id': 'S4-' + pin, 'predecessor_package_sha256': S3, 'freeze_mode': MODE,
                  'compatibility_status': STATUS, 'supersedes_reason': REASON, 'documents': [row['path'] for row in docs],
                  'active_plans': list(s3obj['selected_plan_paths_at_freeze']),
                  'historical_plans': list(s3obj['s3']['historical_plans']), 'policy_sha256': pin, 'approval_sha256': receipt_hash,
                  'fictitious_approval': p['fictitious_approval']}
    return docs, package, descriptor


def descriptor_path(pin, receipt_hash) -> str:
    return 'fase6_planes/freeze_candidates/s4_' + pin + '_' + receipt_hash + '.json'


def ledger_bytes(root, s3obj, package, approved_at):
    existing = read(root, LEDGER)
    if sha(existing) != s3obj['compatibility_ledger_sha256']:
        existing = read(root, S3_ARCHIVE + 'evidence/compatibilidad_sucesiones.csv')
    require(sha(existing) == s3obj['compatibility_ledger_sha256'] and existing.endswith(b'\n'), 'ledger S3 exacto')
    out = io.StringIO(newline='')
    csv.writer(out, lineterminator='\n').writerow([S3, package, STATUS, REASON, approved_at])
    return existing + out.getvalue().encode('utf-8'), existing


def gate_contract(fictitious: bool = False) -> tuple:
    """Suites exigidas (IGUALES para la compuerta real y la de ensayo): 11 históricas en sus fronteras S1/1dda, las 2 S3
    en la frontera S3 reconstruida y la batería del bloque 2 sobre el candidato. Pisos exactos, ninguno reducido."""
    from herramientas.pruebas import s3_gate as G
    legacy = tuple(r for r in G.s3_gate_contract() if r[2] in ('S1', '1dda'))
    require(len(legacy) == 11, 'contrato histórico: once suites')
    s3 = tuple((rel, floor, FRONTERA_S3) for rel, floor in G.S3_SUITES)
    block2 = tuple((rel, floor, CANDIDATO_S4) for rel, floor in BLOCK2_SUITES)
    return legacy + s3 + block2


def _authority(fictitious: bool, pin: str) -> dict:
    return {'kind': S4C.FICTITIOUS if fictitious else 'autor_real', 'policy_sha256': pin,
            'note': 'AUTORIDAD FICTICIA DE ENSAYO: no autoriza nada' if fictitious else 'autorización real del autor'}


ENV_KEYS = {'perfil', 'conforms', 'mismatches', 'huella_sha256', 'manifest_sha256', 'lock_sha256', 'executable',
            'executable_sha256', 'sonda_hijo_huella_sha256', 'fingerprint'}
ROW_KEYS = {'path', 'boundary', 'minimum_expected', 'returncode', 'passed', 'total', 'ast_total', 'skipped', 'discovered',
            'output_sha256', 'environment_fingerprint_sha256', 'interpreter'}
# filas de las suites históricas: estructura del corredor histórico (congelar._ejecutar_suites_obligatorias), sin
# 'skipped'/'discovered' y con 'main_block_last'
LEGACY_ROW_KEYS = {'path', 'boundary', 'minimum_expected', 'returncode', 'passed', 'total', 'ast_total', 'main_block_last',
                   'output_sha256', 'environment_fingerprint_sha256', 'interpreter'}
REPORT_SUMMARY = ('total', 'passed', 'failed', 'errors', 'skipped', 'ast_total', 't2_measured', 'code_manifest_sha256',
                  'suite_code_sha256', 'environment_fingerprint_sha256')


def s1_esperado(root) -> dict:
    """Frontera S1 que debe registrar la compuerta, derivada del archivo S1 autenticado (freeze_history)."""
    from herramientas.pruebas import s3_gate as G
    arch = Path(root) / 'fase6_planes/freeze_history' / G.S1
    raw = (arch / 'freeze_plans_manifest.json').read_bytes()
    require(sha(raw) == G.S1_JSON, 'archivo S1 alterado')
    s1 = strict_json(raw)
    ledger = (arch / 'evidence/compatibilidad_sucesiones.csv').read_bytes()
    require(sha(ledger) == s1['compatibility_ledger_sha256'], 'ledger S1 archivado alterado')
    pointer = (arch / 'evidence/selection_pointer.json').read_bytes()
    require(strict_json(pointer) == {'schema_version': 1, 'selection_path': s1['candidate_selection_relative_path']},
            'puntero S1 archivado incoherente')
    return {'boundary': 'S1', 'package_sha256': G.S1, 'manifest_sha256': G.S1_JSON, 'ledger_sha256': sha(ledger),
            'pointer_sha256': sha(pointer)}


def check_gate(gate, s3obj, pin, prepared_sha, *, fictitious, p, t4, t3, root) -> None:
    """Compuerta completa y ligada; cada campo se contrasta con su fuente autenticada (no con otro campo del gate)."""
    from herramientas.bloque2 import entorno as E
    from herramientas.b import ejecutar_b as EB
    from herramientas.pruebas import s3_gate as G
    from herramientas.s4 import frontera_s3 as FS3
    require(p is not None and t4 is not None and t3 is not None and root is not None,
            'contexto de validación incompleto: política, toolchains S3/S4 y raíz obligatorios')
    require(type(gate) is dict and set(gate) == GATE_KEYS, 'compuerta S4 completa (claves exactas)')
    name = 'FZ-S4-TESTS-GREEN-ENSAYO' if fictitious else 'FZ-S4-TESTS-GREEN'
    require(gate['gate'] == name and gate['status'] == 'GREEN' and gate['errors'] == [], 'compuerta S4 real requerida: ' + name)
    require(gate != s3obj['tests_gate'] and gate['policy_sha256'] == pin and gate['prepared_sha256'] == prepared_sha,
            'no reutilizar compuerta (otra política o candidato preparado)')
    require(gate['authority'] == _authority(fictitious, pin), 'autoridad de la compuerta incoherente')
    require(instant(gate['started_at']) <= instant(gate['finished_at']), 'fechas de compuerta')
    # código: pin y bundle de la toolchain S4 autenticada por la política
    require(gate['code'] == {'toolchain_sha256': p['toolchain_sha256'], 'bundle_sha256': t4['bundle_sha256'],
                             'modules': len(t4['files'])} and sha(canon(t4['files'])) == t4['bundle_sha256'],
            'compuerta de otro código (toolchain S4)')
    # fronteras: S1 del archivo autenticado; S3 derivada de las toolchains autenticadas; transición exacta
    b = gate['boundary']
    require(type(b) is dict and set(b) == {'S1', 'S3'}, 'fronteras de compuerta exactas')
    require(b['S1'] == s1_esperado(root), 'frontera S1 exacta (archivo S1, ledger y puntero)')
    FS3.comprobar_descriptor(b['S3'], t3, t4)
    require(gate['transition'] == FS3.descriptor_esperado(t3, t4)['transicion'],
            'transición S3->S4 distinta de la derivada de las toolchains autenticadas')
    # entorno: huella incrustada, recalculada y comparada con el manifiesto y el lock de la política
    env = gate['environment']
    prof = p['environment']['perfiles']['integracion']
    require(type(env) is dict and set(env) == ENV_KEYS, 'entorno de compuerta con campos ausentes o adicionales')
    fp = env['fingerprint']
    require(type(fp) is dict and sha(E.canon(fp)) == env['huella_sha256'], 'huella de entorno no corresponde a la registrada')
    mism = E.compare(fp, E.approved(root, **prof))
    require(env['perfil'] == 'integracion' and (env['manifest_sha256'], env['lock_sha256']) == (prof['manifest_sha256'], prof['lock_sha256'])
            and mism == [] and env['conforms'] is True and env['mismatches'] == [],
            'compuerta de otro entorno (perfil integracion de la política): ' + ';'.join(mism[:3]))
    require((env['executable'], env['executable_sha256']) == (fp['executable']['path'], fp['executable']['sha256']),
            'intérprete de la compuerta distinto del de su huella')
    require(env['sonda_hijo_huella_sha256'] == env['huella_sha256'], 'proceso hijo con otro intérprete/entorno')
    # suites
    expected = gate_contract(fictitious)
    suites = gate['suites']
    require(type(suites) is list and len(suites) == len(expected), 'todas las suites S4 (ninguna omitida)')
    interp = {'executable': env['executable'], 'sha256': env['executable_sha256']}
    for row, (path, floor, boundary) in zip(suites, expected):
        legacy_row = boundary not in (FRONTERA_S3, CANDIDATO_S4)
        require(type(row) is dict and (LEGACY_ROW_KEYS if legacy_row else ROW_KEYS) <= set(row),
                'fila de compuerta incompleta: ' + str(path))
        require(row['path'] == path and row['minimum_expected'] == floor and row['boundary'] == boundary, 'orden/pisos/fronteras de compuerta')
        require(row['returncode'] == 0 and type(row['total']) is int and row['total'] >= floor and row['passed'] == row['total'],
                'suite incompleta: ' + path)
        require(row['ast_total'] == row['total'], 'descubrimiento real coherente: ' + path)
        if boundary in (FRONTERA_S3, CANDIDATO_S4):
            require(row['discovered'] == row['total'] and row['skipped'] == 0, 'suite sin omisiones: ' + path)
            extra = {'report_sha256', 'report', 'report_raw'} if boundary == CANDIDATO_S4 else set()
            require(set(row) == ROW_KEYS | extra, 'fila de compuerta con campos ausentes o adicionales: ' + path)
        else:
            require(set(row) == LEGACY_ROW_KEYS, 'fila histórica con campos ausentes o adicionales: ' + path)
            require(row['main_block_last'] is True, 'corredor inline histórico: ' + path)
        require(re.fullmatch('[a-f0-9]{64}', str(row['output_sha256'])) is not None, 'salida de suite ausente')
        require(row['environment_fingerprint_sha256'] == env['huella_sha256'] and row['interpreter'] == interp,
                'suite ejecutada en otro entorno o intérprete: ' + path)
        if boundary == CANDIDATO_S4:
            raw = row['report_raw']
            require(type(raw) is str and sha(raw.encode('utf-8')) == row['report_sha256'],
                    'informe de la batería: bytes incrustados distintos de su hash')
            try:
                rep = json.loads(raw)
            except ValueError:
                rep = None
            require(type(rep) is dict and row['report'] == {k: rep.get(k) for k in REPORT_SUMMARY},
                    'informe de la batería: resumen distinto del informe incrustado')
            require(rep.get('suite') == path and rep['total'] == rep['passed'] == rep['ast_total'] == row['total']
                    and rep['failed'] == 0 and rep['errors'] == 0 and rep['skipped'] == 0,
                    'informe de la batería incompleto o distinto de la fila')
            require(rep['code_manifest_sha256'] == EB.code_manifest_sha256(Path(root)),
                    'informe de la batería de otro código productor')
            require(rep['suite_code_sha256'] == EB.code_manifest_sha256(Path(root), EB.SUITE_GLOBS),
                    'informe de la batería de otra versión de la suite')
            require(rep['environment_fingerprint_sha256'] == env['huella_sha256'],
                    'informe de la batería ausente o de otro entorno')
            from decimal import Decimal
            require(Decimal(str(rep['t2_measured'])) < Decimal('1e-4'), 'T2 de la batería fuera de 1e-4')


def _row_env(row, env_doc):
    row['environment_fingerprint_sha256'] = env_doc['fingerprint_sha256']
    row['interpreter'] = {'executable': sys.executable, 'sha256': sha(Path(sys.executable).read_bytes())}
    return row


def run_block2_suites(root: Path, log_dir: Path, env_doc: dict) -> tuple[list, list]:
    """Batería del bloque 2 con --informe (el mismo informe que consume D8_pre V02/V03; no se repite fuera)."""
    from herramientas.pruebas import s3_gate as G
    errors, rows = [], []
    d = Path(log_dir) / 'bloque2'
    d.mkdir(parents=True, exist_ok=True)
    for rel, floor in BLOCK2_SUITES:
        informe = d / 'informe_suite_bloque2.json'
        env = os.environ.copy()
        env.pop(G.GATE_ENV, None)
        proc = subprocess.run([sys.executable, str(Path(root) / rel), '--informe', str(informe)], cwd=root, env=env,
                              capture_output=True, check=False)
        label = rel.replace('/', '__')
        (d / (label + '.out')).write_bytes(proc.stdout)
        (d / (label + '.err')).write_bytes(proc.stderr)
        text = proc.stdout.decode('utf-8', 'replace')
        reports = [json.loads(line) for line in text.splitlines() if line.startswith('{"discovery":')]
        rep = reports[0] if len(reports) == 1 else {}
        rep_raw = informe.read_bytes() if informe.is_file() else None
        rep_doc = json.loads(rep_raw) if rep_raw is not None else None
        row = {'path': rel, 'boundary': CANDIDATO_S4, 'minimum_expected': floor, 'returncode': proc.returncode,
               'passed': rep.get('passed'), 'total': rep.get('total'), 'ast_total': rep.get('ast_total'),
               'skipped': rep.get('skipped'), 'discovered': len(set(rep.get('ids', []))) if rep else None,
               'output_sha256': sha(proc.stdout + proc.stderr),
               'report_sha256': sha(rep_raw) if rep_raw is not None else None,
               'report': ({k: rep_doc.get(k) for k in REPORT_SUMMARY} if rep_doc else None),
               'report_raw': rep_raw.decode('utf-8') if rep_raw is not None else None}
        rows.append(_row_env(row, env_doc))
        errors += [e.replace('FZ-S3', 'FZ-S4') for e in G.check_discovery_row(row)]
        if not rep_doc or rep_doc.get('environment_fingerprint_sha256') != env_doc['fingerprint_sha256']:
            errors.append('FZ-S4: informe de la batería ausente o de otro entorno')
    return errors, rows


def _probe_child(root) -> str:
    """Sonda: un proceso hijo lanzado como las suites (sys.executable, mismo entorno) informa su huella de entorno."""
    code = ('import sys,json;sys.path[:0]=[%r,%r];from herramientas.bloque2 import entorno as E;E.set_runtime_conventions();'
            'from herramientas.bloque2 import entorno_sucesor as ES;print(json.dumps(ES.evaluar(%r,"integracion")["fingerprint_sha256"]))'
            % (str(root), str(Path(root) / 'src'), str(root)))
    proc = subprocess.run([sys.executable, '-B', '-c', code], cwd=root, capture_output=True, check=False)
    return json.loads(proc.stdout.decode('utf-8').strip().splitlines()[-1]) if proc.returncode == 0 else 'SONDA_FALLIDA'


def gate_local(root: Path, policy_hash: str, prepared_hash: str, log_dir: Path, *, fictitious: bool) -> dict:
    """Compuerta en la raíz de trabajo (copia aislada). Misma lógica real/ensayo; ver docstring del módulo."""
    from herramientas.pruebas import s3_gate as G
    from herramientas.s4 import frontera_s3 as FS3
    started = now()
    root = Path(root)
    errors, rows = [], []
    env_doc = ES.evaluar(root, 'integracion')
    environment = {'perfil': 'integracion', 'conforms': env_doc['conforms'], 'mismatches': env_doc['mismatches'],
                   'huella_sha256': env_doc['fingerprint_sha256'], 'manifest_sha256': env_doc['approved']['manifest_sha256'],
                   'lock_sha256': env_doc['approved']['lock_sha256'], 'executable': sys.executable,
                   'executable_sha256': sha(Path(sys.executable).read_bytes()), 'sonda_hijo_huella_sha256': _probe_child(root),
                   'fingerprint': env_doc['fingerprint']}
    code, transition, boundary = {}, {}, {'S1': {}, 'S3': {}}
    if not env_doc['conforms']:
        errors.append('FZ-S4: entorno de compuerta no conforme con el perfil integracion: ' + ';'.join(env_doc['mismatches'][:3]))
    else:
        p, _, t4, _ = authenticate(root, policy_hash)            # inventario cerrado S4 sobre sus propios bytes
        code = {'toolchain_sha256': p['toolchain_sha256'], 'bundle_sha256': t4['bundle_sha256'], 'modules': len(t4['files'])}
        legacy_errors, legacy_rows, info = G.run_legacy_at_boundaries(root, Path(log_dir) / 'historicas')
        errors += list(legacy_errors)
        rows += [_row_env(r, env_doc) for r in legacy_rows]
        boundary['S1'] = {k: info[k] for k in ('boundary', 'package_sha256', 'manifest_sha256', 'ledger_sha256', 'pointer_sha256')}
        frontier_parent = root / 'tmp/s4_frontera_s3' / uuid.uuid4().hex
        try:
            desc = FS3.reconstruir(root, frontier_parent / 'repo', t4)
            boundary['S3'] = desc
            transition = desc['transicion']
            for rel, floor in G.S3_SUITES:
                row = G.run_discovery_suite(frontier_parent / 'repo', rel, floor, Path(log_dir) / 's3', boundary_label=FRONTERA_S3)
                rows.append(_row_env(row, env_doc))
                errors += [e.replace('FZ-S3', 'FZ-S4') for e in G.check_discovery_row(row)]
        except (ValueError, OSError, KeyError) as exc:
            errors.append('FZ-S4: frontera S3 no reconstruible: ' + str(exc))
        finally:
            shutil.rmtree(frontier_parent, ignore_errors=True)
        b_errors, b_rows = run_block2_suites(root, log_dir, env_doc)
        errors += b_errors
        rows += b_rows
    return {'gate': 'FZ-S4-TESTS-GREEN-ENSAYO' if fictitious else 'FZ-S4-TESTS-GREEN', 'status': 'GREEN' if not errors else 'RED',
            'policy_sha256': policy_hash, 'prepared_sha256': prepared_hash, 'started_at': started, 'finished_at': now(),
            'errors': errors, 'boundary': boundary, 'suites': rows, 'environment': environment, 'code': code,
            'transition': transition, 'authority': _authority(fictitious, policy_hash)}


def run_s4_gate(root: Path, policy_hash: str, prepared_hash: str, log_dir: Path) -> dict:
    """Copia aislada de la raíz viva y compuerta hija real (proceso separado, sin heredar el lock del publicador)."""
    from herramientas.pruebas import s3_gate as G
    root = Path(root)
    fictitious = trial(root)
    parent = root / 'tmp/s4_gate'
    parent.mkdir(parents=True, exist_ok=True)
    workspace = parent / uuid.uuid4().hex / 'repo'
    G.copy_root(root, workspace)
    env = os.environ.copy()
    for key in (G.TOKEN_ENV, G.OWNER_ENV, G.GATE_ENV):
        env.pop(key, None)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    proc = subprocess.run([sys.executable, '-B', str(workspace / 'herramientas/congelamiento/s4_publicador.py'), '--s4-gate-child',
                           policy_hash, prepared_hash], cwd=workspace, env=env, capture_output=True, check=False)
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    (Path(log_dir) / 'gate_process.out').write_bytes(proc.stdout)
    (Path(log_dir) / 'gate_process.err').write_bytes(proc.stderr)
    child = workspace / 'tmp/s4_gate_child'
    if child.is_dir():
        shutil.copytree(child, Path(log_dir) / 'compuerta_hija', dirs_exist_ok=True)
    result = json.loads((child / 'gate_result.json').read_bytes())
    shutil.rmtree(workspace.parent, ignore_errors=True)
    require(proc.returncode == 0 and result['status'] == 'GREEN', 'compuerta S4 fallida; ver gate_process.err y compuerta_hija/: '
            + '; '.join(result.get('errors', [])[:3]))
    require(result['gate'] == ('FZ-S4-TESTS-GREEN-ENSAYO' if fictitious else 'FZ-S4-TESTS-GREEN'), 'tipo de compuerta')
    return result


def _gate_child() -> int:
    policy_hash, prepared_hash = sys.argv[2:4]
    require(re.fullmatch('[a-f0-9]{64}', policy_hash) and re.fullmatch('[a-f0-9]{64}', prepared_hash), 'digests')
    require(sha((ROOT / LIVE).read_bytes()) == S3_JSON, 'la compuerta S4 exige S3 vivo exacto')
    from herramientas.bloque2 import entorno as E
    E.set_runtime_conventions()
    log_dir = ROOT / 'tmp/s4_gate_child'
    log_dir.mkdir(parents=True, exist_ok=True)
    from herramientas.pruebas.authoritative_lock import interprocess_lock
    with interprocess_lock(owner_label='S4-compuerta-hija'):
        result = gate_local(ROOT, policy_hash, prepared_hash, log_dir, fictitious=trial(ROOT))
    (log_dir / 'gate_result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return 0 if result['status'] == 'GREEN' else 1


def snapshot(root, p, t, directory) -> dict:
    """Todas las entradas autoritativas (incluida la historia) se re-hashean alrededor de compuerta y promoción."""
    root = Path(root)
    result = {}
    for folder in ('fase1_literatura', 'fase2_datos', 'fase3_metodologia', 'fase4_teoria', 'fase5_cuantificacion', 'fase6_planes',
                   'contracts', 'environment', 'src', 'reports'):
        for q in (root / folder).rglob('*'):
            if q.is_file() and q.relative_to(root).as_posix() not in (JOURNAL, S3P.JOURNAL) and '__pycache__' not in q.parts:
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
    require(sha(read(root, LIVE)) == S3_JSON, 'S4 requiere S3 vigente exacto')
    p, raw, t, directory = authenticate(root, pin)
    s3obj, _ = s3_manifest(root)
    antecedent = s3_antecedent(root)
    from herramientas.s4 import frontera_s3 as FS3
    _, t3 = FS3.s3_toolchain(root)
    from herramientas.s4 import paquete_a as PA
    for k, rel in S4C.PAQUETE_A_FILES.items():
        probs = PA.verificar_atestacion(root, json.loads((Path(directory) / rel).read_bytes()), k,
                                        p['environment']['perfiles']['numerico'])
        require(not probs, 'atestación %s sin relación de autoridad válida: %s' % (k, ','.join(probs)))
    r, rraw = receipt(root, p, pin, rh, author, created_at, receipt_path, directory)
    require(instant(created_at) > instant(s3obj['freeze_plans_created_at']), 'sucesor posterior a S3')
    for rel in FAMILIES_ABSENT:
        require(not (root / rel).exists(), 'producto posterior a S4 ya presente: ' + rel)
    docs, package, desc = selection(s3obj, p, pin, rh)
    ledger, oldledger = ledger_bytes(root, s3obj, package, r['approved_at'])
    desc_path = descriptor_path(pin, rh)
    proof = {'policy_sha256': pin, 'receipt_sha256': rh, 'expected_author': author, 'created_at': created_at,
             'descriptor': desc, 'antecedent': antecedent, 'snapshot': snapshot(root, p, t, directory)}
    return dict(p=p, raw=raw, t=t, t3=t3, root=root, directory=directory, s3=s3obj, r=r, rraw=rraw, docs=docs, package=package, desc=desc,
                desc_path=desc_path, ledger=ledger, oldledger=oldledger, proof=proof, proof_sha=sha(canon(proof)),
                antecedent=antecedent)


def emitted(pre, gate):
    s3obj = pre['s3']
    p = pre['p']
    pin = pre['proof']['policy_sha256']
    rh = pre['proof']['receipt_sha256']
    check_gate(gate, s3obj, pin, pre['proof_sha'], fictitious=p['fictitious_approval'], p=p, t4=pre['t'], t3=pre['t3'],
               root=pre['root'])
    obj = copy.deepcopy(s3obj)
    obj.update(freeze_mode=MODE, freeze_plans_created_at=pre['proof']['created_at'], package_sha256=pre['package'],
               supersedes_package_sha256=S3, supersedes_reason=REASON, successor_compatibility_status=STATUS,
               compatibility_status=STATUS, candidate_selection_id=pre['desc']['candidate_id'],
               candidate_selection_relative_path=pre['desc_path'], candidate_selection_sha256=sha(encoded(pre['desc'])),
               tests_gate=gate, changed_documents=[], removed_documents=[],
               added_documents=[x['path'] for x in pre['docs'][len(s3obj['documents']):]],
               compatibility_ledger_sha256=sha(pre['ledger']), documents=pre['docs'],
               note=('S4 (bloque 2): autoridad consumidora D7/B/D8 con alcance de banderas aprobado por el autor; S3 archivado '
                     'como antecedente de D2/D6/bundles/certificados.' + (' ENSAYO FICTICIO: no autoriza nada.' if
                                                                          p['fictitious_approval'] else '')))
    obj['s4'] = {'policy_sha256': pin, 'approval_sha256': rh, 'authorization_sha256': p['authorization_sha256'],
                 'decision_sha256': p['decision_sha256'], 'contract_sha256': p['contract_sha256'],
                 'toolchain_sha256': p['toolchain_sha256'], 'bundle_sha256': pre['t']['bundle_sha256'],
                 'environment_sha256': S4C.environment_sha256(p), 'environment': copy.deepcopy(p['environment']),
                 'paquete_a': copy.deepcopy(p['paquete_a']),
                 'prepared_sha256': pre['proof_sha'], 'scope': copy.deepcopy(p['scope']), 'fixed_scope': copy.deepcopy(p['fixed_scope']),
                 'pins': copy.deepcopy(p['pins']), 'consumer_scope': p['consumer_scope'],
                 'fictitious_approval': p['fictitious_approval'],
                 'predecessor': {'package_sha256': S3, 'manifest_sha256': S3_JSON, 'policy_sha256': S4C.S3_POLICY,
                                 'receipt_sha256': S4C.S3_RECEIPT, 'archive': S3_ARCHIVE},
                 'production_activation': False}
    return obj


def markdown(obj) -> bytes:
    s4 = obj['s4']
    flags = ''.join(f'- {k}: {"sí" if v else "no"}\n' for k, v in s4['scope'].items())
    return ('# Congelamiento S4 (bloque 2: autoridad consumidora D7/B/D8)\n\nPaquete: `' + obj['package_sha256'] + '`\n\nSucede a S3 `'
            + S3 + '`.\n\n' + obj['note'] + '\n\nAlcance:\n' + flags + '\nAutorización del autor: `' + s4['authorization_sha256']
            + '`. Recibo separado: `' + s4['approval_sha256'] + '`.\n').encode('utf-8')


def transaction(root, outputs, revalidate, validate_promoted=lambda: None):
    """Commit multiarchivo recuperable (mismo protocolo que S2/S3, journal propio). JSON vivo al final."""
    root = Path(root).resolve()
    assert_no_pending(root)
    ident = uuid.uuid4().hex
    stage = root / 'tmp/s4_transactions' / ident
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
            temp = q.with_name(q.name + '.s4-' + ident)
            temp.write_bytes(data)
            require(sha(temp.read_bytes()) == row['new_sha256'], 'escritura de promoción')
            os.replace(temp, q)
            if os.environ.get('S4_TRIAL_CRASH_AFTER') == row['path'] and trial(root):
                raise RuntimeError('fallo inducido de ensayo tras ' + row['path'])
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
            temp = q.with_name(q.name + '.s4-restore')
            temp.write_bytes(raw)
            os.replace(temp, q)
        require((sha(q.read_bytes()) if q.exists() else None) == row['old_sha256'], 'restauración fallida')
    j.unlink()
    return {'status': 'rolled_back', 'files': len(obj['rows'])}


def publish(root, pin, rh, author, receipt_path, *, log_dir, gate_runner=None):
    from herramientas.pruebas.authoritative_lock import interprocess_lock
    root = Path(root)
    with interprocess_lock(owner_label='S4-publicador'):
        created = now()
        pre = prepare(root, pin, rh, author, receipt_path, created)
        gate = (gate_runner or run_s4_gate)(root, pin, pre['proof_sha'], Path(log_dir))
        require(prepare(root, pin, rh, author, receipt_path, created)['proof'] == pre['proof'], 'TOCTOU durante compuerta')
        obj = emitted(pre, gate)
        out = {}
        s3obj = pre['s3']
        for rel, name in ((LIVE, 'freeze_plans_manifest.json'), (MD, 'freeze_plans_manifest.md'),
                          (LEDGER, 'evidence/compatibilidad_sucesiones.csv'), (POINTER, 'evidence/selection_pointer.json')):
            out[S3_ARCHIVE + name] = read(root, rel)
        out[S3_ARCHIVE + 'evidence/freeze_candidate_selection.json'] = read(root, s3obj['candidate_selection_relative_path'])
        C = S3P.local_freezer(root)
        for row in s3obj['documents']:
            path, err = C._resolver_bytes_documento_fijado(S3, row['path'], row['sha256'])
            require(not err, str(err))
            out[S3_ARCHIVE + 'documents/' + row['path']] = path.read_bytes()
        t3 = strict_json((root / S3_INSTALLED / 'toolchain_manifest.json').read_bytes())
        for rel, meta in t3['files'].items():
            data = read(root, rel)
            require(sha(data) == meta['sha256'], 'toolchain S3 viva alterada antes de archivar: ' + rel)
            out[S3_ARCHIVE + 'toolchain/' + rel] = data
        dest = prefix(pin)
        for rel in pre['p']['files']:
            out[dest + rel] = (pre['directory'] / rel).read_bytes()
        out[dest + 'compatibilidad_s4.json'] = pre['raw']
        out[dest + 'aprobacion_s4.json'] = pre['rraw']
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
        return dict(verify(root, pin, rh, author), transaction=ident)


def verify(root, pin, rh, author, *, _allow_pending=False):
    root = Path(root)
    if not _allow_pending:
        assert_no_pending(root)
    p, raw, t, directory = authenticate(root, pin, installed=True)
    live_raw = read(root, LIVE)
    actual = strict_json(live_raw)
    require(actual.get('freeze_mode') == MODE, 'S4 no vigente')
    antecedent = s3_antecedent(root, require_archive=True)
    s3obj, _ = s3_manifest(root)
    r, _ = receipt(root, p, pin, rh, author, actual['freeze_plans_created_at'], prefix(pin) + 'aprobacion_s4.json', directory)
    docs, package, desc = selection(s3obj, p, pin, rh)
    ledger, _ = ledger_bytes(root, s3obj, package, r['approved_at'])
    from herramientas.s4 import frontera_s3 as FS3
    _, t3 = FS3.s3_toolchain(root)
    pre = dict(s3=s3obj, p=p, t=t, t3=t3, root=root, docs=docs, package=package, desc=desc, desc_path=descriptor_path(pin, rh), ledger=ledger,
               proof={'policy_sha256': pin, 'receipt_sha256': rh, 'created_at': actual['freeze_plans_created_at']},
               proof_sha=actual['s4']['prepared_sha256'])
    require(canon(actual) == canon(emitted(pre, actual['tests_gate'])), 'manifiesto S4 completo alterado/herencia incorrecta')
    require(instant(r['approved_at']) <= instant(p['created_at']) <= instant(r['bound_at']) <= instant(actual['freeze_plans_created_at'])
            <= instant(actual['tests_gate']['started_at']), 'secuencia de emisión S4')
    require(canon(get(root, pre['desc_path'])) == canon(desc), 'selección S4 ambigua/incompleta/ampliada')
    require(get(root, POINTER) == {'schema_version': 1, 'selection_path': pre['desc_path']}, 'puntero de selección incoherente')
    require(read(root, MD) == markdown(actual), 'Markdown incoherente')
    require(read(root, LEDGER) == ledger, 'arista específica/ledger alterado')
    C = S3P.local_freezer(root)
    for row in docs:
        _, err = C._resolver_bytes_documento_fijado(package, row['path'], row['sha256'])
        require(not err, 'documento instalado/fijado alterado: ' + str(err))
    require(sha(read(root, S3_ARCHIVE + 'freeze_plans_manifest.json')) == S3_JSON, 'archivo S3 modificado')
    chain = [package] + antecedent['chain']
    return {'status': 'verified_S4', 'package_sha256': package, 'manifest_sha256': sha(live_raw), 'chain': chain,
            'chain_length': len(chain), 'decision_path': prefix(pin) + S4C.DECISION_PATH, 'decision_sha256': p['decision_sha256'],
            'consumer_scope': p['consumer_scope'], 'scope': S4C.scope_of(p), 'pins': dict(p['pins']),
            'fictitious_approval': p['fictitious_approval'], 'installed_prefix': prefix(pin), 'approved_at': r['approved_at'],
            'contract_sha256': p['contract_sha256'], 'contract_root': prefix(pin) + S4C.CONTRACT_DIR + '/',
            'antecedent_s3': {k: antecedent[k] for k in ('package_sha256', 'manifest_sha256', 'contract_sha256', 'installed_prefix',
                                                         'adopted', 'mex_authority_sha256')},
            'production_activation': False}


def main(argv, root=ROOT):
    parser = argparse.ArgumentParser(description='Publicación S4 (bloque 2, candidata)')
    parser.add_argument('command', choices=['verificar-candidato', 'verificar', 'verificar-antecedente-s3', 'congelar', 'recuperar-s4'])
    parser.add_argument('--s4-policy-sha256')
    parser.add_argument('--s4-receipt-sha256')
    parser.add_argument('--s4-author')
    parser.add_argument('--s4-receipt')
    parser.add_argument('--s4-log-dir', default='tmp/s4_gate_logs')
    args = parser.parse_args(argv)
    try:
        root = Path(root).resolve()
        if args.command == 'recuperar-s4':
            from herramientas.pruebas.authoritative_lock import interprocess_lock
            with interprocess_lock(owner_label='S4-recovery'):
                result = recover(root)
        elif args.command == 'verificar-antecedente-s3':
            result = s3_antecedent(root)
            result['chain_length'] = len(result['chain'])
        elif args.command == 'verificar-candidato':
            p, _, t, _ = authenticate(root, args.s4_policy_sha256)
            antecedent = s3_antecedent(root)
            result = {'candidate_integrity': 'pass', 'approval_present': False, 'activation': False, 'scope': p['scope'],
                      'fictitious_approval': p['fictitious_approval'], 'toolchain_modules': len(t['files']),
                      'antecedent': antecedent['status']}
            if args.s4_receipt:
                pre = prepare(root, args.s4_policy_sha256, args.s4_receipt_sha256, args.s4_author, args.s4_receipt, now())
                result.update(package_sha256=pre['package'], approval_present=True, prepared_sha256=pre['proof_sha'])
        elif args.command == 'congelar':
            require(args.s4_receipt is not None, 'recibo S4 ausente')
            logdir = inside(root, args.s4_log_dir)
            logdir.mkdir(parents=True, exist_ok=True)
            result = publish(root, args.s4_policy_sha256, args.s4_receipt_sha256, args.s4_author, args.s4_receipt, log_dir=logdir)
        else:
            result = verify(root, args.s4_policy_sha256, args.s4_receipt_sha256, args.s4_author)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, RuntimeError) as exc:
        print('S4 RECHAZADO: ' + str(exc))
        return 1


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--s4-gate-child':
        raise SystemExit(_gate_child())
    raise SystemExit(main(sys.argv[1:]))
