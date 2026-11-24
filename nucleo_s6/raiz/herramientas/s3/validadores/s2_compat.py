"""Compatibilidad S2 candidata: verificación pura y propuesta; nunca publica."""
from pathlib import Path
import copy
import sys
import re
from .core import require, sha, H, canon, strict_json, inside, verify_manifest
from .temporal import instant

MODE='successor_freeze_integrated_plans_S2_v1'
POLICY_ID='S2_INTEGRATED_PLANS_AND_SCOPED_V2_V1'
MEX_AUTHORITY={'path':'fase6_planes/DECISION_ORIENTACION_CONTABLE_SNA_PRE_D6_v2.md',
 'sha256':'72eb06355b1972f4f9217f0b485aeb034d701a89268ae8977a5ba08dd8342194',
 'parent_payload_sha256':'077a64fe4272a7163f47fbeb3835428838f89460537480222b7f5d0d5abbf6f6',
 'country_id':'MEX','concepts':['D.31','D.39'],
 'claim_mapping_ids':['MEX_CSI_ACCOUNTING_FRAMEWORK_APPLICABILITY_V1','MEX_CSI_ACCRUAL_BASIS_APPLICABILITY_V1']}
SCOPE={'countries':['CHL','COL','MEX','PER'],'D2_years':list(range(2015,2024)),
       'D6_years':[2023],'quantitative_eligibility_authorized':False,
       'source_admission_authorized':False,'scientific_execution_authorized':False}
PLANS=['candidatos/PLAN_BASE_DE_DATOS_INTEGRADO_BORRADOR.md',
       'candidatos/PLAN_DISENO_INTEGRADO_BORRADOR.md',
       'candidatos/PLAN_REPRODUCCION_INTEGRADO_BORRADOR.md']
POLICY_FIELDS={'schema_version','compatibility_id','status','freeze_mode','scope',
               's1_package_sha256','s1_manifest_sha256','contract_sha256','files',
               'active_plans','created_at','approval','mex_authority','v49_sha256','toolchain_sha256'}


def package(documents):
    require(isinstance(documents,list) and documents,'inventario vacío')
    require(all(type(r) is dict and set(r)=={'path','sha256'} for r in documents),'documentos exactos')
    paths=[r['path'] for r in documents]
    # El congelador conserva el orden semántico de expansión, no orden léxico.
    # El hash de paquete autentica ese orden; nunca reordenar el predecesor.
    require(len(paths)==len(set(paths)),'rutas duplicadas')
    from .core import relative_path
    import re
    for r in documents:
        relative_path(r['path']);require(type(r['sha256']) is str and re.fullmatch('[0-9a-f]{64}',r['sha256']),'hash documento')
    return sha(''.join(r['path']+'\t'+r['sha256']+'\n' for r in documents).encode())


def policy(raw, expected_hash):
    require(sha(raw)==expected_hash,'ancla externa de política S2')
    p=strict_json(raw)
    require(type(p) is dict and set(p)==POLICY_FIELDS,'esquema cerrado S2')
    require(type(p['schema_version']) is int and p['schema_version']==1,'versión S2')
    require(p['compatibility_id']==POLICY_ID and p['freeze_mode']==MODE,'modo/compatibilidad específica S2')
    require(canon(p['scope'])==canon(SCOPE),'alcance científico/quantitativo inmutable')
    require(p['status']=='CANDIDATO_PARA_REVISION_SIN_ACTIVACION' and p['approval'] is None,'no atribuir aprobación a candidato')
    require(p['active_plans']==PLANS,'selección exacta de tres planes')
    require(p['mex_authority']==MEX_AUTHORITY,'no ampliar autoridad MEX ni heredarla tácitamente')
    require(p['v49_sha256']=='0537846d2588ab4e4c77cc54956bfc26f9ed297967fa2d39024859f6dc7d921a','v49 inmutable')
    instant(p['created_at'])
    require(type(p['files']) is dict and p['files'],'archivos candidatos requeridos')
    for key in ('s1_package_sha256','s1_manifest_sha256','contract_sha256','v49_sha256','toolchain_sha256'):
        require(type(p[key]) is str and re.fullmatch('[0-9a-f]{64}',p[key]),'pin inválido: '+key)
    from .core import relative_path
    for rel,meta in p['files'].items():
        relative_path(rel)
        require(type(meta) is dict and set(meta)=={'sha256','bytes'} and type(meta['bytes']) is int and meta['bytes']>=0,'metadatos exactos')
        require(type(meta['sha256']) is str and re.fullmatch('[0-9a-f]{64}',meta['sha256']),'pin de miembro inválido')
    return p


def inspect_candidate(delivery, project, raw_policy, expected_hash):
    delivery,project=Path(delivery),Path(project)
    p=policy(raw_policy,expected_hash)
    verify_manifest(delivery,p['contract_sha256'])
    m=strict_json((delivery/'contratos/contract_manifest.json').read_bytes())
    required=set(m['files'])|{'contratos/contract_manifest.json','toolchain_manifest.json'}|{q.relative_to(delivery).as_posix() for q in (delivery/'validadores').glob('*.py')}
    require(set(p['files'])==required,'cobertura exacta normativa y de código S2')
    for rel,meta in p['files'].items():
        require(set(meta)=={'sha256','bytes'} and type(meta['bytes']) is int,'meta exacta')
        raw=inside(delivery,rel).read_bytes()
        require(len(raw)==meta['bytes'] and sha(raw)==meta['sha256'],'bytes S2 alterados: '+rel)
    current=project/'fase6_planes/freeze_plans_manifest.json'
    s1raw=current.read_bytes()
    if sha(s1raw)!=p['s1_manifest_sha256']:
        s1raw=inside(project,'fase6_planes/freeze_history/'+p['s1_package_sha256']+'/freeze_plans_manifest.json').read_bytes()
    require(sha(s1raw)==p['s1_manifest_sha256'],'S1 real requerido')
    s1=strict_json(s1raw)
    require(package(s1['documents'])==s1['package_sha256']==p['s1_package_sha256'],'paquete S1')
    require(instant(p['created_at'])>=instant(s1['freeze_plans_created_at']),'política anterior a S1')
    previous_path=list(sys.path);sys.path.insert(0,str(project))
    try:
        from herramientas.d6 import construir_d6 as d6
        require(Path(d6.__file__).resolve()==(project/'herramientas/d6/construir_d6.py').resolve(),'módulo D6 ajeno')
        authority=d6.load_orientation_decision_v2(root=project,require_frozen=False)
        d6._validate_v2_frozen_context(root=project,authority=authority,proposed_bytes=s1raw)
        require(p['mex_authority']=={'path':d6.ORIENTATION_DECISION_V2_PATH,'sha256':d6.ORIENTATION_DECISION_V2_SHA256,
            'parent_payload_sha256':d6.MEX_PARENT_SHA256,'country_id':'MEX','concepts':['D.31','D.39'],
            'claim_mapping_ids':['MEX_CSI_ACCOUNTING_FRAMEWORK_APPLICABILITY_V1','MEX_CSI_ACCRUAL_BASIS_APPLICABILITY_V1']},'alcance V2 distinto del autorizado')
        require(p['v49_sha256']=='0537846d2588ab4e4c77cc54956bfc26f9ed297967fa2d39024859f6dc7d921a','v49 inmutable')
    finally:sys.path[:]=previous_path
    return {'candidate_integrity':'pass','s1_strict_V2':'pass','activation':False,'s1':s1}


def approved_receipt(raw, expected_hash, p, policy_hash, created_at, author):
    require(expected_hash is not None and sha(raw)==expected_hash,'se necesita pin EXTERNO del consentimiento nuevo S2')
    a=strict_json(raw)
    require(set(a)=={'status','author','approved_at','policy_sha256','s1_package_sha256','contract_sha256','scope'},'recibo S2 exacto')
    require(a['status']=='approved_by_author' and type(author) is str and author and a['author']==author,'autoridad S2 no aprobada')
    require(a['policy_sha256']==policy_hash and a['s1_package_sha256']==p['s1_package_sha256'] and a['contract_sha256']==p['contract_sha256'],'aprobación de otros bytes')
    require(canon(a['scope'])==canon(SCOPE),'aprobación fuera de alcance')
    require(instant(p['created_at'])<=instant(a['approved_at'])<=instant(created_at),'orden temporal S2 exacto')
    return a


def proposal(s1, p, policy_raw, policy_hash, approval_raw, approval_hash, *, created_at, author):
    """Constructor documental sin escritura. El llamador debe inspeccionar bytes.

    No hereda tests_gate: esta propuesta no es un freeze emitible; la integración
    futura debe agregar una compuerta oficial nueva antes de publicación.
    """
    require(policy(policy_raw,policy_hash)==p,'política inconsistente')
    require(package(s1['documents'])==s1['package_sha256']==p['s1_package_sha256'],'predecesor incorrecto')
    require(instant(created_at)>instant(s1['freeze_plans_created_at']),'sucesor no posterior')
    approved_receipt(approval_raw,approval_hash,p,policy_hash,created_at,author)
    prefix='fase6_planes/integracion_s2/versions/'+policy_hash+'/'
    additions={prefix+k:v['sha256'] for k,v in p['files'].items()}
    additions[prefix+'compatibilidad_s2.json']=policy_hash
    additions[prefix+'aprobacion_s2.json']=approval_hash
    old={r['path']:r['sha256'] for r in s1['documents']}
    require(not set(old)&set(additions),'S2 no sobrescribe pines históricos')
    docs=copy.deepcopy(s1['documents'])+[{'path':k,'sha256':v} for k,v in sorted(additions.items())]
    return {'schema_version':1,'status':'PROSPECTIVE_ONLY_NOT_EMITTED','freeze_mode':MODE,
            'created_at':created_at,'supersedes_package_sha256':s1['package_sha256'],
            'supersedes_manifest_sha256':p['s1_manifest_sha256'],'policy_sha256':policy_hash,
            'approval_sha256':approval_hash,'documents':docs,'package_sha256':package(docs),
            'active_plans':[prefix+x for x in PLANS],'scope':copy.deepcopy(SCOPE),
            'tests_gate':None,'production_activation':False}


def validate_proposal(actual, s1, p, policy_raw, policy_hash, approval_raw, approval_hash, *, author):
    expected=proposal(s1,p,policy_raw,policy_hash,approval_raw,approval_hash,created_at=actual['created_at'],author=author)
    require(canon(actual)==canon(expected),'propuesta S2 ampliada, incompleta o mutada')
    return {'specific_compatibility':'pass','production_activation':False,'quantitative_eligibility_authorized':False}


def consume_v2_candidate(delivery, project, actual, policy_raw, policy_hash, approval_raw, approval_hash, *, author):
    """Consumidor prospectivo S2 con consentimiento propio; devuelve referencia.

    No acepta el alcance aprobado S1 como sustituto del nuevo consentimiento.
    No devuelve elegibilidad de fuente ni escribe un producto cuantitativo.
    """
    p=policy(policy_raw,policy_hash)
    # Rechazar falta de consentimiento ANTES de resolver la autoridad histórica.
    approved_receipt(approval_raw,approval_hash,p,policy_hash,actual['created_at'],author)
    inspected=inspect_candidate(delivery,project,policy_raw,policy_hash)
    result=validate_proposal(actual,inspected['s1'],p,policy_raw,policy_hash,approval_raw,approval_hash,author=author)
    return dict(result,consumer='S2_prospective_scoped_V2',authority=copy.deepcopy(p['mex_authority']),
                policy_sha256=policy_hash,approval_sha256=approval_hash,source_admission_authorized=False)
