"""Compatibilidad S4 (bloque 2, CANDIDATA): verificación pura de la política sucesora de S3 que habilitaría a los
consumidores D7/B/D8, de la autorización del autor y del recibo separado. Nunca publica ni activa.

S4 no reinterpreta S3: S3 sigue siendo la autoridad bajo la que se emitieron D2, D6 v2, bundles CA2 y certificados
D3-D5; S4 solo añade la autoridad CONSUMIDORA del bloque 2, con un alcance de banderas explícitas que decide el autor.
El código no fija qué banderas se conceden (es decisión científica/institucional del autor): exige que el alcance de la
política sea exactamente el que cita literalmente el mensaje de autorización, con coherencia jerárquica entre banderas.

Ensayo aislado: una autorización FICTICIA (status y marca FICTICIA_ENSAYO_AISLADO) solo se acepta con
allow_fictitious=True, que el publicador concede únicamente en raíces marcadas como ensayo y nunca en la raíz original.

Bloque 3 (candidato): la política fija además el ENTORNO SUCESOR candidato (campo 'environment' = entorno_sucesor.pins():
perfiles numerico/integracion, manifiestos y locks, plataforma validada, antecedente histórico) y las ATESTACIONES de
reproducción de A y A-ter (campo 'paquete_a', archivos en evidencia/paquete_a/). El autor los aprueba con S4; antes de
eso solo hay conformidad técnica. El recibo identifica también la toolchain (código) y el entorno aprobados.
"""
from pathlib import Path
import copy
import json
import re
from herramientas.s3.validadores.core import require, sha, canon, strict_json, inside, relative_path
from herramientas.s3.validadores.temporal import instant
from herramientas.bloque2 import entorno_sucesor as ES

MODE = 'successor_freeze_block2_D7_B_D8_S4_v1'
POLICY_ID = 'S4_BLOCK2_D7_B_D8_CONSUMER_AUTHORITY_V1'
STATUS = 'POLITICA_SUCESORA_CON_AUTORIZACION_SEPARADA'
S3_PACKAGE = '8aaa27cf12dfe435512ccd60245cc1ed4c70dbf28421eee5aec7c38814fab7b9'
S3_MANIFEST = '0cc606177b865ec58d5bee1a68fb6143dae7a9be4a3cde5c95eb8df54b103ddc'
S3_POLICY = '1192c3caec215f8419939b175be81a8c963b40c693ffcacc638ebd82a6af03fc'
S3_RECEIPT = '3b03a698105da957b9b86728e61566fe6d39e0f9a7049a2e828ee5bf3e65db50'
S3_AUTHOR = 'Vicenzo Scavino'
S3_TOOLCHAIN = 'b1387cbe41544b9d191a603a4e1b54b0f34c47eaf744e8888372b92641456a82'   # toolchain cerrada S3 (131 módulos)
CONTRACT = '4d7e676a2156c7f83b231e812fa39afe417fb6057abb35083f80774fe15e3220'   # enmienda candidata CA2-4
CONTRACT_ANTECEDENT = 'eda3d6e5a0c0c0c318bb075c3314f7c927382c955d76e2dcdd3b5c1f4659af32'   # CA2-3 bajo S3
CONTRACT_DIR = 'contratos_enmienda'
FICTITIOUS = 'FICTICIA_ENSAYO_AISLADO'
DECISION_PATH = 'DECISION_AUTORIDAD_S4_CANDIDATA.md'
AUTHORIZATION_PATH = 'autorizacion/autorizacion_autor_s4.json'
AUTHORIZATION_TEXT = 'autorizacion/AUTORIZACION_AUTOR_S4.txt'
EVIDENCE_DIR = 'evidencia'
PAQUETE_A_FILES = {'A': 'evidencia/paquete_a/atestacion_A.json', 'A-ter': 'evidencia/paquete_a/atestacion_A-ter.json'}
SCOPE_FLAGS = ('d7_production_authorized', 'quantitative_eligibility_authorized', 'b_synthetic_validation_authorized',
               'b_official_run_authorized', 'freeze_run_authorized', 'd8_pre_authorized', 'd8_post_authorized',
               'official_export_authorized', 'source_admission_authorized')
# Implicaciones: una bandera exige las que la preceden en la cadena (ninguna habilitación aislada incoherente).
IMPLIES = {'quantitative_eligibility_authorized': ('d7_production_authorized',),
           'b_synthetic_validation_authorized': ('d7_production_authorized',),
           'd8_pre_authorized': ('d7_production_authorized',),
           'd8_post_authorized': ('d8_pre_authorized',),
           'freeze_run_authorized': ('quantitative_eligibility_authorized', 'd8_pre_authorized', 'b_synthetic_validation_authorized'),
           'b_official_run_authorized': ('freeze_run_authorized',),
           'official_export_authorized': ('b_official_run_authorized', 'd8_post_authorized')}
FIXED_SCOPE = {'preregistered_cases': ['PREG-COL-E2-2023', 'PREG-COMPARACION-E1', 'PREG-PER-APLICACION-E0E3',
                                       'PREG-PER-APLICACION-E1'],
               'case_countries': ['COL', 'MEX', 'PER'], 'excluded_countries': ['CHL'], 'D2_years': list(range(2015, 2024)),
               'D6_years': [2023], 'joint_E2': False, 'E4': False, 'historical_D6': False, 'mex_interpretation_only': True}
PINS = {'d2_tree_sha256': 'f9d42072e07dbce5fabb92a4e183bb3390a981318e3a29f0906e8fe990a589c8',
        'd6_v2_tree_sha256': 'b10f1296226dc94969fa5d14468e8a4fd5c61858e1687e0c2609c66545b60e31',
        'inventory_1_5_sha256': 'b7c3766300b6733ffe5c5f3c85c5522188523cc7e4660210eb3cfdc1189da0ea',
        'inventory_sha256': '8c85db58ee33ab70d0b7a5c411e3cc42773cdf0161c12e1a92142afdbff0127d',
        'comparability_sha256': '2f001377a6273395a7d6d0f5bd64cab6a0797a6a78d644c26773b9c8dce45a35',
        'external_grid_sha256': 'b94b9eedeea87d08071366e2bd8a5b7cd9662ce6f9fd9d7bee42848d6c4c5f90',
        'ca2_bundles_index_sha256': '907767435de0355475e035d14a175d7c42b87337d108753137bd46790652c8e5'}
POLICY_FIELDS = {'schema_version', 'compatibility_id', 'status', 'freeze_mode', 'scope', 'fixed_scope', 's3_package_sha256',
                 's3_manifest_sha256', 's3_policy_sha256', 's3_receipt_sha256', 'contract_sha256', 'files', 'decision_sha256',
                 'created_at', 'approval', 'authorization_sha256', 'pins', 'toolchain_sha256', 'consumer_scope',
                 'fictitious_approval', 'environment', 'paquete_a'}
RECEIPT_FIELDS = {'status', 'author', 'approved_at', 'bound_at', 'mechanism', 'signature', 'authorization_sha256',
                  'policy_sha256', 's3_package_sha256', 'contract_sha256', 'scope', 'fictitious_approval',
                  'toolchain_sha256', 'environment_sha256'}
HEX = re.compile('[0-9a-f]{64}')


def check_scope(scope: dict) -> dict:
    require(type(scope) is dict and set(scope) == set(SCOPE_FLAGS), 'alcance S4: banderas exactas')
    require(all(type(v) is bool for v in scope.values()), 'alcance S4: booleanos')
    for flag, needs in IMPLIES.items():
        if scope[flag]:
            for n in needs:
                require(scope[n], f'alcance S4 incoherente: {flag} exige {n}')
    return scope


def policy(raw, expected_hash, *, allow_fictitious=False):
    require(expected_hash is not None and sha(raw) == expected_hash, 'ancla externa de política S4')
    p = strict_json(raw)
    require(type(p) is dict and set(p) == POLICY_FIELDS, 'esquema cerrado S4')
    require(type(p['schema_version']) is int and p['schema_version'] == 1, 'versión S4')
    require(p['compatibility_id'] == POLICY_ID and p['freeze_mode'] == MODE and p['status'] == STATUS, 'modo/compatibilidad S4')
    require(p['approval'] is None, 'la política no se autoaprueba: aprobación en recibo separado')
    require(type(p['fictitious_approval']) is bool, 'marca de ensayo tipada')
    require(not p['fictitious_approval'] or allow_fictitious, 'aprobación FICTICIA fuera de un ensayo aislado')
    check_scope(p['scope'])
    require(canon(p['fixed_scope']) == canon(FIXED_SCOPE), 'alcance fijo S4 inmutable (casos, países, años, sin E2 conjunto/E4)')
    require((p['s3_package_sha256'], p['s3_manifest_sha256'], p['s3_policy_sha256'], p['s3_receipt_sha256']) ==
            (S3_PACKAGE, S3_MANIFEST, S3_POLICY, S3_RECEIPT), 'predecesor S3 exacto')
    require(p['contract_sha256'] == CONTRACT, 'contrato normativo distinto de la enmienda CA2-4 fijada')
    require(p['pins'] == PINS, 'pines de productos antecedentes exactos')
    require(type(p['consumer_scope']) is str and p['consumer_scope'].strip(), 'descripción de alcance consumidor')
    require(p['fictitious_approval'] == p['consumer_scope'].startswith(FICTITIOUS), 'rótulo FICTICIO visible en el alcance')
    instant(p['created_at'])
    for key in ('authorization_sha256', 'toolchain_sha256', 'decision_sha256'):
        require(type(p[key]) is str and HEX.fullmatch(p[key]), 'pin inválido: ' + key)
    require(type(p['files']) is dict and p['files'], 'archivos S4 requeridos')
    for rel, meta in p['files'].items():
        relative_path(rel)
        require(type(meta) is dict and set(meta) == {'sha256', 'bytes'} and type(meta['bytes']) is int and meta['bytes'] >= 0,
                'metadatos exactos')
        require(type(meta['sha256']) is str and HEX.fullmatch(meta['sha256']), 'pin de miembro inválido')
    require(p['authorization_sha256'] == p['files'][AUTHORIZATION_PATH]['sha256'], 'autorización fijada en la política')
    require(p['decision_sha256'] == p['files'][DECISION_PATH]['sha256'], 'documento de decisión fijado en la política')
    require(p['environment'] == ES.pins(), 'entorno sucesor distinto del contrato candidato declarado (entorno_sucesor.pins)')
    require(type(p['paquete_a']) is dict and set(p['paquete_a']) == set(PAQUETE_A_FILES), 'atestaciones A/A-ter exactas')
    for k, rel in PAQUETE_A_FILES.items():
        require(rel in p['files'] and p['paquete_a'][k] == {'path': rel, 'sha256': p['files'][rel]['sha256']},
                'atestación %s fijada en la política' % k)
    return p


def environment_sha256(p) -> str:
    return sha(canon(p['environment']))


def attestations(delivery, p, project=None) -> dict:
    """Atestaciones A/A-ter del candidato: bytes fijados y validación SEMÁNTICA completa (resultado efectivo, evidencia
    de entorno autenticada y perfil numérico de la raíz del proyecto). La relación con la raíz viva (cadena, estado
    arrastrado, árboles) la comprueba paquete_a.verificar_atestacion al preparar y en la compuerta."""
    from herramientas.s4 import paquete_a as PA
    out = {}
    for k, rel in PAQUETE_A_FILES.items():
        q = inside(Path(delivery), rel)
        raw = q.read_bytes()
        require(sha(raw) == p['paquete_a'][k]['sha256'], 'atestación %s alterada' % k)
        doc = json.loads(raw)
        probs = PA.verificar_atestacion(project, doc, k, p['environment']['perfiles']['numerico'], con_relacion=False,
                                        dir_atestacion=q.parent)
        require(not probs, 'atestación %s inválida: %s' % (k, ','.join(probs)))
        out[k] = doc
    return out


def authorization(delivery, p):
    """Autorización del autor: mensaje literal con hash; cita el hash del documento de decisión y cada bandera concedida."""
    delivery = Path(delivery)
    raw = inside(delivery, AUTHORIZATION_PATH).read_bytes()
    a = strict_json(raw)
    text = inside(delivery, AUTHORIZATION_TEXT).read_bytes()
    require(set(a) == {'status', 'author', 'signature', 'message', 'approved_at', 'registered_at', 'approved_scope',
                       'decision_sha256'}, 'autorización S4 exacta')
    fict = p['fictitious_approval']
    require(a['status'] == (FICTITIOUS if fict else 'approved_by_author'), 'estado de la autorización S4')
    require(a['signature'] is None, 'sin firma inventada')
    require(a['message']['sha256'] == sha(text) and a['message']['bytes'] == len(text), 'texto de la autorización alterado')
    require(a['message']['path'] == 'herramientas/s4/' + AUTHORIZATION_TEXT, 'ruta del texto de la autorización')
    require(instant(a['approved_at']) == instant(a['message']['received_at']) <= instant(a['registered_at']),
            'fechas reales de la autorización')
    body = text.decode('utf-8')
    require(a['decision_sha256'] == p['decision_sha256'] and p['decision_sha256'] in body, 'el mensaje no cita la decisión S4')
    require(canon(a['approved_scope']) == canon(p['scope']), 'alcance aprobado distinto del de la política')
    for flag in SCOPE_FLAGS:
        literal = f'{flag}={"true" if p["scope"][flag] else "false"}'
        require(literal in body, 'bandera no literal en el mensaje: ' + literal)
    if fict:
        require(body.startswith(FICTITIOUS), 'mensaje ficticio sin rótulo inicial')
    else:
        require(FICTITIOUS not in body, 'mensaje real con rótulo de ensayo')
    require(p['authorization_sha256'] == sha(raw), 'política ligada a otra autorización')
    return a, raw


def inspect_candidate(delivery, project, raw_policy, expected_hash, *, allow_fictitious=False):
    delivery = Path(delivery)
    p = policy(raw_policy, expected_hash, allow_fictitious=allow_fictitious)
    required = ({DECISION_PATH, 'toolchain_manifest.json', AUTHORIZATION_PATH, AUTHORIZATION_TEXT}
                | {q.relative_to(delivery).as_posix() for q in (delivery / 'validadores').glob('*.py')}
                | {q.relative_to(delivery).as_posix() for q in (delivery / CONTRACT_DIR).rglob('*') if q.is_file()}
                | {q.relative_to(delivery).as_posix() for q in (delivery / EVIDENCE_DIR).rglob('*')
                   if q.is_file() and '__pycache__' not in q.parts})
    require(set(p['files']) == required, 'cobertura exacta S4: decisión, toolchain, autorización, código y evidencia')
    for rel, meta in p['files'].items():
        raw = inside(delivery, rel).read_bytes()
        require(len(raw) == meta['bytes'] and sha(raw) == meta['sha256'], 'bytes S4 alterados: ' + rel)
    require(p['toolchain_sha256'] == p['files']['toolchain_manifest.json']['sha256'], 'toolchain fijada en la política')
    from herramientas.s3.validadores.core import verify_manifest
    verify_manifest(delivery / CONTRACT_DIR, p['contract_sha256'])
    attestations(delivery, p, project)
    authorization(delivery, p)
    return {'candidate_integrity': 'pass', 'authorization': 'pass', 'fictitious_approval': p['fictitious_approval'],
            'activation': False}


def approved_receipt(raw, expected_hash, p, policy_hash, created_at, author, authorization_raw):
    """Recibo separado: liga la autorización del autor (fecha real del mensaje) al hash de la política."""
    require(expected_hash is not None and sha(raw) == expected_hash, 'se necesita pin EXTERNO del recibo S4')
    r = strict_json(raw)
    require(set(r) == RECEIPT_FIELDS, 'recibo S4 exacto')
    auth = strict_json(authorization_raw)
    require(r['fictitious_approval'] == p['fictitious_approval'], 'marca de ensayo del recibo')
    require(r['status'] == (FICTITIOUS if p['fictitious_approval'] else 'approved_by_author'), 'estado del recibo S4')
    require(type(author) is str and author and r['author'] == author == auth['author'], 'autor S4 externo exacto')
    require(r['signature'] is None and r['mechanism'] == 'author_message_registered_by_executor', 'mecanismo real, sin firma inventada')
    require(r['authorization_sha256'] == sha(authorization_raw) == p['authorization_sha256'], 'recibo ligado a otra autorización')
    require(r['approved_at'] == auth['approved_at'], 'fecha de aprobación distinta del mensaje del autor')
    require(r['policy_sha256'] == policy_hash, 'recibo de otro candidato (política distinta)')
    require(r['s3_package_sha256'] == S3_PACKAGE and r['contract_sha256'] == p['contract_sha256'], 'aprobación de otros bytes')
    require(r['toolchain_sha256'] == p['toolchain_sha256'], 'recibo de otro código (toolchain distinta)')
    require(r['environment_sha256'] == environment_sha256(p) == ES.pins_sha256(), 'recibo de otro entorno')
    require(canon(r['scope']) == canon(p['scope']), 'aprobación fuera de alcance')
    require(instant(r['approved_at']) <= instant(p['created_at']) <= instant(r['bound_at']) <= instant(created_at), 'orden temporal S4 exacto')
    return r


def scope_of(p) -> dict:
    return copy.deepcopy(p['scope'])
