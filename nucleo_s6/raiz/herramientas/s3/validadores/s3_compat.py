"""Compatibilidad S3 (subpaso 1.5): verificación pura de la política sucesora, de la autorización del autor y del
recibo separado. Nunca publica ni activa.

Orden de confianza: bytes revisados -> ancla externa de la política -> inventarios cerrados (normativo, adoptado,
código) -> autorización del autor registrada (mensaje con fecha real, sin firma inventada) -> recibo separado que
liga esa autorización al hash de la política -> paquete emitido por el publicador.

La autorización del autor aprueba el paquete revisado (inventario a88b683a…) y autoriza al ejecutor a producir la
sucesión: por eso approved_at (mensaje) es anterior a created_at (política) y el recibo registra bound_at (vínculo
real posterior). Los bytes normativos adoptados deben ser exactamente los aprobados.
"""
from pathlib import Path
import copy
import re
from .core import require, sha, canon, strict_json, inside, verify_manifest, relative_path
from .temporal import instant

MODE = 'successor_freeze_1_5_incorporation_S3_v1'
POLICY_ID = 'S3_A1E_V2_CA2_3_CA2_2X_R2_INCORPORATION_1_5_V1'
STATUS = 'POLITICA_SUCESORA_CON_AUTORIZACION_SEPARADA_SIN_EJECUCION'
S2_PACKAGE = '29654c6a013b6fbb579e476a0cc41cdecbf3c1af8d9a0bcdea14897f83effd87'
S2_MANIFEST = '13e96cf8e877b05154f053dbba3e5c70aea2df4c7865ef92a1f46a7dcdceb0a6'
S2_POLICY = 'ef67dc7f317bdb9243790a74c77722accb6b6e0ccc7a43686252396eb07683a2'
S2_RECEIPT = '8f36ec2c08d337daf654c31fc4145f48ae5059659b9ce88f5f071655d7c2246d'
APPROVED_DELIVERY_INVENTORY = 'a88b683a4b4a6baea40b3b885e2f8180818f6bacf7004034dd75cb874f8b7faf'
APPROVED_CONTRACT = 'eda3d6e5a0c0c0c318bb075c3314f7c927382c955d76e2dcdd3b5c1f4659af32'
APPROVED_D2_TREE = 'f9d42072e07dbce5fabb92a4e183bb3390a981318e3a29f0906e8fe990a589c8'
RECEPTION_TREE = 'f56f23cf7f61e36c46f8a720f8b6eb5976153b4d5cc75136c0669755a8624bc2'
DOSSIER_SEAL = 'd2adfdc090d34c3c03ecd6f70e318352b18dc9c2b56a9da4c611e2c70b2d1b6c'
V49 = '0537846d2588ab4e4c77cc54956bfc26f9ed297967fa2d39024859f6dc7d921a'
AUTHORIZATION_PATH = 'autorizacion/autorizacion_autor_1_5.json'
AUTHORIZATION_TEXT = 'autorizacion/AUTORIZACION_AUTOR_1_5_2026-09-28.txt'
PREREGISTERED = ['PREG-COL-E2-2023', 'PREG-COMPARACION-E1', 'PREG-PER-APLICACION-E0E3', 'PREG-PER-APLICACION-E1']
SCOPE = {'data_domain_countries': ['CHL', 'COL', 'MEX', 'PER'], 'case_countries': ['COL', 'MEX', 'PER'],
         'excluded_countries': ['CHL'], 'D2_years': list(range(2015, 2024)), 'D6_years': [2023],
         'preregistered_cases': PREREGISTERED,
         'source_incorporation_authorized': True, 'consumer_rebuild_authorized': True,
         'source_admission_authorized': False, 'quantitative_eligibility_authorized': False,
         'scientific_execution_authorized': False, 'model_execution_authorized': False}
PLANS = ['candidatos/PLAN_BASE_DE_DATOS_INTEGRADO_BORRADOR.md',
         'candidatos/PLAN_DISENO_INTEGRADO_BORRADOR.md',
         'candidatos/PLAN_REPRODUCCION_INTEGRADO_BORRADOR.md']
# Artefactos adoptados fuera del manifiesto normativo: ruta en el árbol S3 -> ruta en la entrega aprobada.
ADOPTED = {'contratos_adicionales/CA2-2X_PRECISION_2.json': 'contratos_candidatos/CA2-2X_PRECISION_2.json',
           'contratos_adicionales/REGISTRO_CASOS_A1E_V2.json': 'contratos_candidatos/REGISTRO_CASOS_A1E_V2.json',
           'autoridades/AUTORIDAD_PER_ORIENTACION_2023_CANDIDATA_V2.json': 'contratos_candidatos/AUTORIDAD_PER_ORIENTACION_2023_CANDIDATA_V2.json',
           'autoridades/AUTORIDAD_COL_ORIENTACION_2024p_CANDIDATA.json': 'contratos_candidatos/AUTORIDAD_COL_ORIENTACION_2024p_CANDIDATA.json'}
EXTRA_MEMBERS = sorted(set(ADOPTED) | {'contratos_adicionales/historico/CA2-2X_PRECISION_1.json',
                                       'autoridades/aprobacion_autoridades_1_5.json', AUTHORIZATION_PATH, AUTHORIZATION_TEXT})
MEX_AUTHORITY = {'path': 'fase6_planes/DECISION_ORIENTACION_CONTABLE_SNA_PRE_D6_v2.md',
                 'sha256': '72eb06355b1972f4f9217f0b485aeb034d701a89268ae8977a5ba08dd8342194',
                 'parent_payload_sha256': '077a64fe4272a7163f47fbeb3835428838f89460537480222b7f5d0d5abbf6f6',
                 'country_id': 'MEX', 'concepts': ['D.31', 'D.39'],
                 'claim_mapping_ids': ['MEX_CSI_ACCOUNTING_FRAMEWORK_APPLICABILITY_V1', 'MEX_CSI_ACCRUAL_BASIS_APPLICABILITY_V1']}
ADOPTED_PINS = {'contract_manifest_sha256': APPROVED_CONTRACT, 'd2_tree_sha256': APPROVED_D2_TREE,
                'reception_tree_sha256': RECEPTION_TREE, 'dossier_seal_sha256': DOSSIER_SEAL,
                'approved_delivery_inventory_sha256': APPROVED_DELIVERY_INVENTORY}
POLICY_FIELDS = {'schema_version', 'compatibility_id', 'status', 'freeze_mode', 'scope', 's2_package_sha256',
                 's2_manifest_sha256', 's2_policy_sha256', 's2_receipt_sha256', 'contract_sha256', 'files', 'active_plans',
                 'created_at', 'approval', 'authorization_sha256', 'adopted', 'mex_authority', 'v49_sha256', 'toolchain_sha256'}
RECEIPT_FIELDS = {'status', 'author', 'approved_at', 'bound_at', 'mechanism', 'signature', 'authorization_sha256',
                  'policy_sha256', 's2_package_sha256', 'contract_sha256', 'scope'}
HEX = re.compile('[0-9a-f]{64}')


def package(documents):
    require(isinstance(documents, list) and documents, 'inventario vacío')
    require(all(type(r) is dict and set(r) == {'path', 'sha256'} for r in documents), 'documentos exactos')
    paths = [r['path'] for r in documents]
    require(len(paths) == len(set(paths)), 'rutas duplicadas')
    for r in documents:
        relative_path(r['path'])
        require(type(r['sha256']) is str and HEX.fullmatch(r['sha256']), 'hash documento')
    return sha(''.join(r['path'] + '\t' + r['sha256'] + '\n' for r in documents).encode())


def policy(raw, expected_hash):
    require(expected_hash is not None and sha(raw) == expected_hash, 'ancla externa de política S3')
    p = strict_json(raw)
    require(type(p) is dict and set(p) == POLICY_FIELDS, 'esquema cerrado S3')
    require(type(p['schema_version']) is int and p['schema_version'] == 1, 'versión S3')
    require(p['compatibility_id'] == POLICY_ID and p['freeze_mode'] == MODE and p['status'] == STATUS, 'modo/compatibilidad S3')
    require(p['approval'] is None, 'la política no se autoaprueba: aprobación en recibo separado')
    require(canon(p['scope']) == canon(SCOPE), 'alcance S3 inmutable')
    require((p['s2_package_sha256'], p['s2_manifest_sha256'], p['s2_policy_sha256'], p['s2_receipt_sha256']) ==
            (S2_PACKAGE, S2_MANIFEST, S2_POLICY, S2_RECEIPT), 'predecesor S2 exacto')
    require(p['contract_sha256'] == APPROVED_CONTRACT, 'manifiesto normativo distinto del aprobado')
    require(p['active_plans'] == PLANS, 'selección exacta de tres planes')
    require(p['mex_authority'] == MEX_AUTHORITY and p['v49_sha256'] == V49, 'autoridad MEX y v49 inmutables')
    require(p['adopted'] == dict(ADOPTED_PINS, artifacts={k: p['files'][k]['sha256'] for k in sorted(ADOPTED)}), 'pines adoptados exactos')
    instant(p['created_at'])
    for key in ('authorization_sha256', 'toolchain_sha256'):
        require(type(p[key]) is str and HEX.fullmatch(p[key]), 'pin inválido: ' + key)
    require(type(p['files']) is dict and p['files'], 'archivos S3 requeridos')
    for rel, meta in p['files'].items():
        relative_path(rel)
        require(type(meta) is dict and set(meta) == {'sha256', 'bytes'} and type(meta['bytes']) is int and meta['bytes'] >= 0, 'metadatos exactos')
        require(type(meta['sha256']) is str and HEX.fullmatch(meta['sha256']), 'pin de miembro inválido')
    require(p['authorization_sha256'] == p['files'][AUTHORIZATION_PATH]['sha256'], 'autorización fijada en la política')
    return p


def authorization(delivery, p=None):
    """Autorización del autor registrada: texto literal con hash, paquete aprobado, D-01..D-09 y A-01..A-07."""
    delivery = Path(delivery)
    raw = inside(delivery, AUTHORIZATION_PATH).read_bytes()
    a = strict_json(raw)
    text = inside(delivery, AUTHORIZATION_TEXT).read_bytes()
    require(a['status'] == 'approved_by_author' and a['signature'] is None, 'autorización del autor sin firma inventada')
    require(a['message']['sha256'] == sha(text) and a['message']['bytes'] == len(text), 'texto de la autorización alterado')
    require(a['message']['path'] == 'herramientas/s3/' + AUTHORIZATION_TEXT, 'ruta del texto de la autorización')
    require(instant(a['approved_at']) == instant(a['message']['received_at']) <= instant(a['registered_at']), 'fechas reales de la autorización')
    pkg = a['approved_package']
    require(pkg['inventory_sha256'] == APPROVED_DELIVERY_INVENTORY and pkg['contract_manifest_sha256'] == APPROVED_CONTRACT
            and pkg['d2_tree_sha256'] == APPROVED_D2_TREE and pkg['s2_package_sha256'] == S2_PACKAGE, 'paquete aprobado distinto')
    body = text.decode('utf-8')
    require(APPROVED_DELIVERY_INVENTORY in body and APPROVED_CONTRACT in body and APPROVED_D2_TREE in body, 'el mensaje no cita el paquete aprobado')
    require('Apruebo D-01 a D-09' in body and 'Apruebo asimismo A-01 a A-07' in body, 'aprobaciones ausentes del mensaje')
    require([d['id'] for d in a['decisions']] == ['D-0%d' % i for i in range(1, 10)] and all(d['status'] == 'approved_by_author' for d in a['decisions']), 'D-01..D-09')
    require([x['id'] for x in a['approvals']] == ['A-0%d' % i for i in range(1, 8)] and all(x['status'] == 'approved_by_author' for x in a['approvals']), 'A-01..A-07')
    for d in a['decisions']:
        require(d['id'] + ': ' + d['text_in_message'] in body, 'decisión no literal en el mensaje: ' + d['id'])
    for rel, src in ADOPTED.items():
        require(sha(inside(delivery, rel).read_bytes()) == pkg['artifacts'][src], 'artefacto adoptado distinto del aprobado: ' + rel)
    for rel in ('contratos/contract_manifest.json', 'contratos/catalogo_contratos.json', 'contratos/extensiones_s2.json', *PLANS,
                'review/CONTINGENCIA_A2.md', 'review/ESTRATEGIA_DE_CALCULO.md'):
        require(sha(inside(delivery, rel).read_bytes()) == pkg['artifacts']['codigo/candidato_s2/' + rel], 'normativo distinto del aprobado: ' + rel)
    if p is not None:
        require(p['authorization_sha256'] == sha(raw), 'política ligada a otra autorización')
    return a, raw


def inspect_candidate(delivery, project, raw_policy, expected_hash):
    delivery, project = Path(delivery), Path(project)
    p = policy(raw_policy, expected_hash)
    verify_manifest(delivery, p['contract_sha256'])
    m = strict_json((delivery / 'contratos/contract_manifest.json').read_bytes())
    required = (set(m['files']) | {'contratos/contract_manifest.json', 'toolchain_manifest.json'} | set(EXTRA_MEMBERS)
                | {q.relative_to(delivery).as_posix() for q in (delivery / 'validadores').glob('*.py')})
    require(set(p['files']) == required, 'cobertura exacta S3: normativo, adoptado, autorización y código')
    for rel, meta in p['files'].items():
        raw = inside(delivery, rel).read_bytes()
        require(len(raw) == meta['bytes'] and sha(raw) == meta['sha256'], 'bytes S3 alterados: ' + rel)
    authorization(delivery, p)
    from . import institucional as I
    a_raw = inside(delivery, AUTHORIZATION_PATH).read_bytes()
    approval_raw = inside(delivery, 'autoridades/aprobacion_autoridades_1_5.json').read_bytes()
    approval = I.authority_approval(approval_raw, sha(approval_raw), a_raw, author=strict_json(a_raw)['author'])
    authorities = ('autoridades/AUTORIDAD_PER_ORIENTACION_2023_CANDIDATA_V2.json', 'autoridades/AUTORIDAD_COL_ORIENTACION_2024p_CANDIDATA.json')
    require([approval['D-01']['sha256'], approval['D-09']['sha256']] == [p['files'][rel]['sha256'] for rel in authorities],
            'aprobación de autoridades ajena a la política')
    return {'candidate_integrity': 'pass', 'authorization': 'pass', 'activation': False}


def approved_receipt(raw, expected_hash, p, policy_hash, created_at, author, authorization_raw):
    """Recibo separado: liga la autorización del autor (fecha real del mensaje) al hash de la política."""
    require(expected_hash is not None and sha(raw) == expected_hash, 'se necesita pin EXTERNO del recibo S3')
    r = strict_json(raw)
    require(set(r) == RECEIPT_FIELDS, 'recibo S3 exacto')
    auth = strict_json(authorization_raw)
    require(r['status'] == 'approved_by_author' and type(author) is str and author and r['author'] == author == auth['author'], 'autor S3 externo exacto')
    require(r['signature'] is None and r['mechanism'] == 'author_message_registered_by_executor', 'mecanismo real, sin firma inventada')
    require(r['authorization_sha256'] == sha(authorization_raw) == p['authorization_sha256'], 'recibo ligado a otra autorización')
    require(r['approved_at'] == auth['approved_at'], 'fecha de aprobación distinta del mensaje del autor')
    require(r['policy_sha256'] == policy_hash and r['s2_package_sha256'] == S2_PACKAGE and r['contract_sha256'] == p['contract_sha256'], 'aprobación de otros bytes')
    require(canon(r['scope']) == canon(SCOPE), 'aprobación fuera de alcance')
    require(instant(r['approved_at']) <= instant(p['created_at']) <= instant(r['bound_at']) <= instant(created_at), 'orden temporal S3 exacto')
    return r


def s2_policy_and_receipt(installed_dir, created_at):
    """Autentica política y recibo S2 instalados (antecedente) con su propio validador histórico."""
    from herramientas.s2.validadores import s2_compat as S
    installed_dir = Path(installed_dir)
    praw = (installed_dir / 'compatibilidad_s2.json').read_bytes()
    rraw = (installed_dir / 'aprobacion_s2.json').read_bytes()
    p = S.policy(praw, S2_POLICY)
    a = S.approved_receipt(rraw, S2_RECEIPT, p, S2_POLICY, created_at, 'Vicenzo Scavino')
    return p, a


def scope():
    return copy.deepcopy(SCOPE)
