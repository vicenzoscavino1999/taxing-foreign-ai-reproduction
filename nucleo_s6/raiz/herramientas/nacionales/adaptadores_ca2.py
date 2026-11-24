"""CA2 source/evidence adapter, with a national-only preflight extension.

No fake structural/availability/labor context is created to satisfy a full CA2
bundle: those hashes belong to later consumers. Uses the active catalog's exact
vector/member/evidence projections; full CA2Validator remains unchanged.
"""
import json
from .nacionales import *
from .base import CATALOG_DIR
from herramientas.s3.validadores.core import Contracts
from herramientas.s3.validadores.ca2 import CA2Validator
from . import precision as pr

def contracts():
    # 1.5: catálogo CA2-3 (A1-E v2) instalado en herramientas/s3/contratos (manifiesto normativo eda3d6e5…).
    root=CATALOG_DIR
    return Contracts(*(json.loads((root/n).read_text(encoding='utf-8')) for n in ('catalogo_contratos.json','formulas.json','CLAVES_DE_CALCULO.json')))
from herramientas.s3.validadores import ca2x

class EvidenceAdapter:
    """CA2 evidence adapter. The precision receipt comes from precision.validate_vector (the same
    validation that drives roles, domains and eligibility), also when this adapter is used alone.
    It accepts no dossier object or fixture: receipts are only built from the authenticated dossier (R2)."""
    def __init__(self,source,role,related_snapshots):
        need(role in contracts().C['ca2']['mandatory_evidence']+['precision'],'registered evidence role')
        self.source,self.role,self.related=source,role,sorted(set(related_snapshots))
    def evidence(self,raw):
        snap=self.source.snapshot(raw) # authenticity is verified BEFORE role evaluation
        context=snap['context']
        facts={k:context[k] for k in ('family','country_id','observation_year','source_id','source_vintage','unit','multiplier','accounting_basis')}
        facts.update(role=self.role,snapshot_sha256=self.source.cfg['sha256'],selectors=sorted(m['selector'] for m in snap['members']),related_snapshots=self.related)
        need(self.source.cfg['sha256'] in self.related,'source omitted from evidence')
        if self.role=='precision':
            s=self.source;res=pr.validate_vector(s.country,s.family,s.year,s.revision,raw=raw)
            # CA2 outcomes are pass/fail/unknown: pending review or absent evidence is 'unknown', never 'pass'.
            outcome={'pass':'pass','fail':'fail'}.get(res['status'],'unknown');rule=None
            if outcome=='pass':
                # Projection read here from the authenticated snapshot, not taken from the rule (R3).
                projection=[(m['concept'],m['selector']) for m in sorted(snap['members'],key=lambda m:m['selector'])]
                need([x for _,x in projection]==facts['selectors'],'projection order')
                rule=res['rule_v2'];ca2x.validate(rule,projection,cells=pr._cells(s,raw),snapshot_sha256=s.cfg['sha256'],emitted=True)
            return {'facts':facts,'outcome':outcome,'precision_rule':rule,'common_conflicts':[]}
        state=roles(self.source,snap)
        outcome=state[self.role] if state[self.role] in ('pass','fail') else 'unknown'
        return {'facts':facts,'outcome':outcome,'precision_rule':None,'common_conflicts':[]}

def preflight(out):
    catalog=contracts();spec=catalog.C['ca2'];vectors=[];members=[];receipts=[]
    for c in COUNTRIES:
        for family,years in [('D2',range(2015,2024)),('D6',[2023])]:
            for y in years:
                a=NationalAdapter(c,family,y);s=a.read();vid=f'{c}_{family}_{y}'
                ctx=s['context'];v=dict(vector_id=vid,**ctx,snapshot_path=a.cfg['path'],snapshot_sha256=a.cfg['sha256'],adapter_id=vid,denominator_member_id='PIB')
                ms=[dict(vector_id=vid,member_id=m['concept'],**m,country_id=c,observation_year=y,source_vintage=ctx['source_vintage'],snapshot_sha256=v['snapshot_sha256'],denominator_member_id='PIB') for m in s['members']]
                ms.sort(key=lambda m:m['member_id']);v['vector_sha256']=H({'header':v,'members':ms})
                need(sorted(m['concept'] for m in ms)==spec['representations'][v['representation']]['concepts'],'CA2 exact representation')
                for m in ms:
                    for k in ('country_id','observation_year','source_vintage','snapshot_sha256','unit','multiplier','denominator_member_id'):need(m[k]==v[k],'CA2 mixed member scope')
                projection={'context':{k:v[k] for k in spec['snapshot_projection']},'members':[{k:m[k] for k in spec['snapshot_member_projection']} for m in sorted(ms,key=lambda m:m['concept'])]}
                need(a.snapshot(read_source(a.key)[1])==projection,'CA2 source adapter projection')
                vectors.append(v);members.extend(ms)
                related=[a.cfg['sha256']]
                if y==2023:related.append(NationalAdapter(c,'D6' if family=='D2' else 'D2').cfg['sha256'])
                for role in spec['mandatory_evidence']+['precision']:
                    r=EvidenceAdapter(a,role,related).evidence(read_source(a.key)[1]);need(set(r)==set(spec['evidence_receipt_fields']),'CA2 evidence receipt shape')
                    receipts.append({'vector_id':vid,'artifact_path':a.cfg['path'],'artifact_sha256':a.cfg['sha256'],'adapter_id':f'{vid}_{role}',**r})
    for name,rows in [('ca2_vectors',vectors),('ca2_members',members)]:
        fields=catalog.C['tables'][name]['order_by'];rows.sort(key=lambda r:tuple(r[k] for k in fields));catalog.table(name,rows)
    write_json(out/'datos/ca2_vectors.json',vectors);write_json(out/'datos/ca2_members.json',members);write_json(out/'datos/ca2_evidence_receipts.json',receipts)
    prec={r['vector_id']:r['outcome'] for r in receipts if r['facts']['role']=='precision'}
    sample=next(r['precision_rule'] for r in receipts if r['precision_rule'])
    try:CA2Validator(catalog,A).precision(sample,[x['selector'] for x in sample['selector_rules']]);active_rejects=False
    except Exception:active_rejects=True
    result={'extension':'NATIONAL_PREFLIGHT_4','active_contract':'CA2-2 unchanged','precision_contract':ca2x.CONTRACT+' candidate extension, not active','snapshot_projections':len(vectors),'member_rows':len(members),'evidence_receipts':len(receipts),
            'precision_receipts':{k:v for k,v in sorted(prec.items())},'precision_rules_validated_with':'ca2x.validate against authenticated cells','active_CA2_2_validator_rejects_CA2_2X_payload':active_rejects,
            'national_adapter_preflight':'pass','full_CA2_bundle_validation':'not_run_missing_real_consumer_context_not_fabricated','real_source_admission':False,'production_activation':False}
    write_json(out/'review/ca2_preflight.json',result);return result
# Sin punto de entrada: construir_d2.py orquesta el preflight.
