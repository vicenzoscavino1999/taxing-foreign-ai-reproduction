"""[Incorporado en 1.5 desde codigo/precision.py de la entrega aprobada; entradas en la recepción versionada.]
Unified precision validation — the ONE decision source for the precision state, CA2 receipts,
candidate domains, DB-05 rows, scientific-table tolerances and eligibility.

PASS for a concrete vector (country, family, year, source revision) requires:
  * the sanitized dossier authenticated by its pinned seal (private originals are not needed);
  * for every rule used, a CURRENT claim (not superseded) whose country, year, source revision,
    snapshot binding and selector/concept scope match, with a receipt linked to a verified origin;
  * a correspondence row for every stored primitive, re-verified against the file bytes;
  * coverage of every primitive the vector consumes;
  * domains constructed and validated: stored cells only, values on the declared increment, identity
    and joint D2/D6 residual domains containing zero, published cross-checks.
Outcomes: absent dossier/evidence or an uncovered primitive -> 'unknown'; altered dossier -> EvidenceError;
failed domain validation -> 'fail'; a correspondence still pending review -> 'candidate_pending_review'.
There is no country/year rule for PASS.

Revision 2026-09-27 (R1, R2, R3):
  * no result cache: every call authenticates the dossier from its bytes; only parsed cells are cached,
    immutable and keyed by the SHA-256 of the authenticated bytes (R1);
  * the ordinary interfaces (validate_vector, state, EvidenceAdapter, build) never accept a dossier object,
    cells or a synthetic flag; Dossier is immutable, built only from bytes against the pinned seal, and
    re-checks its own content digest before use (R2). Synthetic fixtures live in ensayo_precision.py and
    their results are marked synthetic and can never be emitted as receipts;
  * rules are bound to the authenticated projection (concept, selector) and ca2x checks that the shared
    denominator is the PIB member of that projection (R3, CA2-2X-PRECISION-2).

Consolidation 2026-09-27 (subpaso 1.4):
  * a rule whose basis carries a declared interpretation (MEX "redondeados a tres decimales" read as nearest)
    yields 'declared_interpretation', never 'pass': its domains are kept and labelled, but they produce no
    institutional strict pass, no emitted receipt and no DB-05 row (D-03 corrected);
  * PER D6 uses the net route (D-02): V=K376, N_PROD=DL389+DL390, P_NET=E24-N_PROD. F376, I376 and J376 are
    published contrasts, not precision primitives. The D2-D6 total identity holds by construction (shared E24)
    and is reported as such, not as an independent check; the same authenticated PIB primitive is required.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib, json
from types import MappingProxyType
from .nacionales import A, need, dec, ratio, read_source, NationalAdapter, xlsx_cells, xls_cells
from herramientas.s3.validadores.institucional import nearest_domain, affine_domain
from . import evidencia as ev
from herramientas.s3.validadores import ca2x
from herramientas.s3.validadores.ca2x import CONTRACT, parse_member

API_VERSION='PRECISION_API_2'
DOSSIER_ROOT=A/'evidencia'
SEAL_SHA256='edb400e0c7b391c6bd5af67cf708255346525f128e76148adf837988aace04d5'
DOSSIER_FILES=('afirmaciones_db02.json','recibos_db02.json','vinculos_afirmacion_snapshot.json','sucesion_evidencia.json','verificacion_privada_hashes.json','reglas_publicacion.json','correspondencias_primitivas.json')
CLAIM_CONCEPT={'B.1b':'PIB','D.211':'D211','D.21':'D21','D.31':'D31','D.29':'D29','D.39':'D39'}
MEX_ROW_LABELS={'S34':'B.1b','R36':'D.1','R45':'D.2','R46':'D.21','R47':'D.211','R53':'D.29','R54':'D.3','R55':'D.31','R59':'D.39','R60':'B.2b','R61':'B.3b'}
CROSS_CHECK_CELLS={'MEX':['Tabulado!R45','Tabulado!R54']}
PER_RULE_D2='PER_D2_ROUNDING_2023_4032';PER_RULE_D6='PER_NEAREST_2023_4032';PER_ZERO='PER_ZERO_2023_4032';PER_CELLS='PER_COU_CONCEPT_CELLS';PER_D21_MAP='PER_D21_MAPPING'
def mex_rule(year):return f'MEX_CSI_ROUNDING_{year}'
MEX_UNITS={'compilation_unit':'1000 MXN (miles de pesos) - institutional fact INEGI 2026-09-23','publication_increment':'0.001 million MXN = 1000 MXN - institutional fact','publication_domain_half_width':'0.0005 million MXN: documented interpretation of rounding to three decimals; tie rule not declared','relation':'increment equals compilation unit; not assumed exact','total_statistical_error':'not_identified (E4)'}
PER_UNITS={'compilation_unit':'not declared','publication_increment':'1 million PEN','publication_domain_half_width':'0.5 million PEN: nearest unit, no truncation (institutional); tie rule not declared','total_statistical_error':'not_identified (E4)'}
COL_UNITS={'compilation_unit':'1 million COP (millones de pesos) - institutional fact DANE 202610074537','publication_increment':'1 thousand million COP (miles de millones de pesos)','publication_domain_half_width':'0.5 thousand million COP: nearest unit, no truncation (institutional, DANE 202610074537); tie rule not declared','published_zero':'D.31 2023 (Q70) published 0 is a rounded value, not an exact zero; sign undetermined (DANE 202610074537)','scope':'CEI 2023p base 2015 only; 2015-2022 and 2024p not covered','total_statistical_error':'not_identified (E4)'}
def sha(b):return hashlib.sha256(b).hexdigest()

# ------------------------------------------------------------------ elementary checks
def stored_value(cells,selector):
    sh,c=selector.split('!');v=cells.get(sh,{}).get(c)
    need(v is not None and v['type']=='n' and v['value'] not in (None,''),'numeric selector missing '+selector)
    need(v['formula'] is None,'derived cell cannot receive an independent publication domain: '+selector)
    return F(v['value'])
def decimals(value_text):
    t=str(value_text);return len(t.split('.')[1]) if '.' in t else 0
def check_publication_increment(value_text,places,selector):
    need(decimals(value_text)<=places,'value finer than declared publication increment '+selector)
def check_on_increment(value,unit,selector):
    need((F(value)/F(unit)).denominator==1,'value finer than declared publication increment '+selector)
def half_width(dom):return (dom[1]-dom[0])/2
def contains_zero(dom):return dom[0]<=0<=dom[1]
def dom_json(d):return [dec(d[0]),dec(d[1])]
def terms_s(terms):return [(p,str(k)) for p,k in terms]
def ratio_envelope(num_terms,den_terms,domains):
    """Corner envelope; valid only when numerator and denominator share no primitive."""
    need(not ({k for k,_ in num_terms}&{k for k,_ in den_terms}),'shared primitive between numerator and denominator: corner envelope invalid')
    n=affine_domain(terms_s(num_terms),domains);d=affine_domain(terms_s(den_terms),domains);need(d[0]>0,'denominator domain must be positive')
    q=[a/b for a in n for b in d];return {'low':ratio(min(q),1),'high':ratio(max(q),1)}
def verify_correspondence(row,cells):
    """Re-verify a correspondence row against the authenticated workbook cells."""
    sh,c=row['label_selector'].split('!');label=str((cells.get(sh,{}).get(c) or {}).get('value') or '').strip()
    ok=label==row['sna_code'] if row['label_match']=='exact' else label.startswith(row['sna_code']+' - ')
    need(ok,f"correspondence contradicted by file label {row['label_selector']} for {row['primitive']}")
    for sel,expected in (row.get('column_check') or {}).items():
        sh,c=sel.split('!');need(str((cells.get(sh,{}).get(c) or {}).get('value') or '').strip()==expected,'column header check failed '+sel)
    for key,exp in (('formula_selector','expected_formula'),('parent_formula_selector','expected_parent_formula')):
        if row[key]:
            sh,c=row[key].split('!');need((cells.get(sh,{}).get(c) or {}).get('formula')==row[exp].lstrip('+') or (cells.get(sh,{}).get(c) or {}).get('formula')==row[exp],'formula check failed '+row[key])
    return True

# ------------------------------------------------------------------ sealed dossier
def freeze(x):
    """Deep read-only view: mappings become MappingProxyType, lists become tuples."""
    if isinstance(x,(dict,MappingProxyType)):return MappingProxyType({k:freeze(v) for k,v in x.items()})
    if isinstance(x,(list,tuple)):return tuple(freeze(v) for v in x)
    return x
def thaw(x):
    if isinstance(x,(dict,MappingProxyType)):return {k:thaw(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [thaw(v) for v in x]
    return x
def _digest(content):return sha(json.dumps(thaw(content),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8'))
_FIELDS=('claims','bindings','receipts','succession','origin','rules','corr')
class Dossier:
    """Immutable dossier. Ordinary construction: Dossier.load(), from bytes authenticated against the pinned
    seal. Content cannot be changed in place; verify() re-computes the content digest recorded at load, so an
    object altered by bypassing immutability is rejected. Synthetic fixtures (ensayo_precision) are flagged."""
    __slots__=('seal','synthetic','_content','_digest')
    def __init__(self,*a,**k):raise TypeError('Dossier objects are built only by Dossier.load() (authenticated bytes) or by ensayo_precision (synthetic)')
    def __setattr__(self,k,v):raise TypeError('Dossier is immutable')
    def __delattr__(self,k):raise TypeError('Dossier is immutable')
    def __reduce_ex__(self,protocol):raise TypeError('Dossier cannot be copied or pickled; use ensayo_precision.fixture() for synthetic variants')
    @classmethod
    def _build(cls,content,seal,synthetic):
        obj=object.__new__(cls);frozen=freeze(content)
        for k,v in (('seal',seal),('synthetic',synthetic),('_content',frozen),('_digest',_digest(frozen))):object.__setattr__(obj,k,v)
        return obj
    @classmethod
    def load(cls,root=None):
        root=Path(root or DOSSIER_ROOT);seal=root/'sello_expediente.json'
        if not seal.exists():raise ev.DossierUnavailable('sealed dossier unavailable: '+str(root))
        raw=seal.read_bytes();ev.need(sha(raw)==SEAL_SHA256,'dossier seal does not match the pinned hash')
        doc=json.loads(raw);ev.need(tuple(sorted(doc['files']))==tuple(sorted(DOSSIER_FILES)),'dossier seal file list')
        data={}
        for n,h in doc['files'].items():
            p=root/n;ev.need(p.exists(),'sealed dossier file missing: '+n);b=p.read_bytes();ev.need(sha(b)==h,'sealed dossier file altered: '+n);data[n]=b
        load=lambda n:json.loads(data[n].decode('utf-8'))
        claims=ev.load_claims_bytes(data['afirmaciones_db02.json']);bindings=ev.load_bindings_bytes(data['vinculos_afirmacion_snapshot.json'])
        content={'claims':claims,'bindings':bindings,'receipts':{r['receipt_id']:r for r in load('recibos_db02.json')},'succession':load('sucesion_evidencia.json'),
                 'origin':sorted({r['sha256'] for r in load('verificacion_privada_hashes.json')}),'rules':load('reglas_publicacion.json'),'corr':load('correspondencias_primitivas.json')}
        return cls._build(content,sha(raw),False)
    def verify(self):
        ev.need(_digest(self._content)==self._digest,'dossier content differs from its authenticated bytes')
        return self
    def __getattr__(self,k):
        if k in _FIELDS:return self._content[k]
        if k=='superseded':return frozenset(x['predecessor_id'] for x in self._content['succession'] if x['relation']=='successor')
        raise AttributeError(k)
    def resolve(self,eid,*,role,country,year,vintage,snapshot,selectors):
        ev.need(eid not in self.superseded,'evidence superseded, not current: '+str(eid))
        c=ev.resolve(eid,role=role,country=country,year=year,vintage=vintage,snapshot=snapshot,selectors=selectors,claims=self.claims,bindings=self.bindings)
        if c['receipt_id'] is not None:
            r=self.receipts.get(c['receipt_id']);ev.need(r is not None,'claim receipt missing: '+c['receipt_id'])
            ev.need(r['message_sha256'] in self.origin,'receipt not linked to a verified origin: '+c['receipt_id'])
        return c
    def rules_for(self,country,year,source_id,snapshot,vintage):
        out=[]
        for r in self.rules:
            for at in r['applies_to']:
                if r['country_id']==country and at['year']==year and at['source_id']==source_id and at['snapshot_sha256']==snapshot and at['source_vintage']==vintage:out.append((r,at))
        return sorted(out,key=lambda x:x[0]['kind']!='exact')
    def correspondence(self,country,year,snapshot,primitive):
        rows=[r for r in self.corr if (r['country_id'],r['year'],r['snapshot_sha256'],r['primitive'])==(country,year,snapshot,primitive)]
        ev.need(len(rows)<=1,'ambiguous correspondence '+primitive);return rows[0] if rows else None

def require_exact_zero_evidence(snapshot,selector):
    """Exact-zero reading of a blank cell needs current, scoped evidence in the authenticated dossier."""
    d=Dossier.load()
    rules=[(r,at) for r in d.rules for at in r['applies_to'] if r['kind']=='exact' and selector in r['cells'] and at['snapshot_sha256']==snapshot]
    need(len(rules)==1,'exact zero not documented for '+selector);r,at=rules[0]
    for eid in at['cell_evidence']:d.resolve(eid,role='exact_zero',country=r['country_id'],year=at['year'],vintage=at['source_vintage'],snapshot=snapshot,selectors=[selector])
    return r['rule_id']

# ------------------------------------------------------------------ the validation
_CELLS={}
def clear_cache():
    """Deprecated no-op kept for callers of the 27-09 API: there is no result cache any more."""
    return None
def _cells(adapter,raw):
    """Parsed cells of AUTHENTICATED bytes, immutable, cached by (source, year, SHA-256 of the bytes)."""
    if adapter.key=='PER_PDF':return None
    key=(adapter.key,adapter.year,sha(raw))
    if key not in _CELLS:
        _CELLS[key]=freeze(xls_cells(raw,adapter.year) if adapter.key=='CHL_CEI' else xlsx_cells(raw))
    return _CELLS[key]
def _find_path(d,rules,prim,flag,cells,ctx,reasons):
    corr=d.correspondence(ctx['country'],ctx['year'],ctx['snapshot'],prim)
    if corr is None:reasons.append('no_correspondence:'+prim);return None
    verify_correspondence(corr,cells)
    for r,at in rules:
        try:
            if r['kind']=='exact':
                if prim not in r['cells']:continue
                eids=[d.resolve(e,role='exact_zero',selectors=[prim],**ctx)['evidence_id'] for e in at['cell_evidence']]
                return dict(kind='exact',unit=None,rule=r,evidence=eids,corr=corr,status='ok')
            if prim in r['cells']:
                eids=[d.resolve(e,role='precision',selectors=[prim],**ctx)['evidence_id'] for e in at['cell_evidence']]
                return dict(kind='rounding',unit=r['rounding_unit'],rule=r,evidence=eids,corr=corr,status='ok')
            concept=corr['sna_code'] if corr['relation']=='direct' else corr['relation'].split('component_of_')[1]
            if concept in r['concepts']:
                eids=[d.resolve(e,role='precision',selectors=[CLAIM_CONCEPT[concept]],**ctx)['evidence_id'] for e in at['concept_evidence']]
                ev.need(eids,'concept rule without concept evidence')
                eids+=[d.resolve(e,role='concept_cell',selectors=[prim],**ctx)['evidence_id'] for e in corr['evidence_ids']]
                ev.need(corr['evidence_ids'],'concept-level rule needs a correspondence claim for '+prim)
                pending=corr['status']!='technical_correspondence_verified_in_file'
                return dict(kind='rounding',unit=r['rounding_unit'],rule=r,evidence=eids,corr=corr,status='pending_review' if pending else 'ok')
        except ev.EvidenceError as e:
            reasons.append(f'evidence_not_applicable:{r["rule_id"]}:{prim}:{e}')
    reasons.append('no_applicable_rule:'+prim);return None

def validate_vector(country,family,year,revision='selected',*,raw=None,**not_allowed):
    """Ordinary interface. Authenticates the dossier from its bytes on every call (no cache), authenticates the
    snapshot bytes, and never accepts dossier objects, cells or synthetic flags (see ensayo_precision)."""
    if not_allowed:raise TypeError('validate_vector accepts no '+', '.join(sorted(not_allowed))+': synthetic inputs belong to ensayo_precision')
    a=NationalAdapter(country,family,year,revision)
    try:d=Dossier.load()
    except ev.DossierUnavailable:
        return _base_result(a,False,'unknown',['dossier_unavailable'])
    raw=raw if raw is not None else read_source(a.key)[1];need(sha(raw)==a.cfg['sha256'],'snapshot hash does not match registered source')
    return _validate(a,d,raw=raw,cells=None,synthetic=False)
def _base_result(a,synthetic,status=None,reasons=None):
    cfg=a.cfg
    return dict(vector_id=f'{a.country}_{a.family}_{a.year}'+('' if a.revision=='selected' else '_'+a.revision),country_id=a.country,family=a.family,year=a.year,revision=a.revision,source_id=a.key,snapshot_sha256=cfg['sha256'],source_vintage=cfg['vintage'],
                synthetic=synthetic,contract=CONTRACT,status=('synthetic_'+status if synthetic and status else status),reasons=list(reasons or []),checks={},primitives={},members=[],derived={},share_envelopes={},rule_v2=None,dossier_seal=None,multiplier=None,projection=None)
def _validate(a,d,*,raw,cells,synthetic):
    """Internal. Non-synthetic calls require an authentic, unaltered Dossier; synthetic calls mark everything."""
    need(isinstance(d,Dossier),'a Dossier is required')
    if synthetic:need(d.synthetic or cells is not None,'synthetic validation needs a synthetic dossier or synthetic cells')
    else:need(not d.synthetic and cells is None,'ordinary validation cannot use synthetic inputs')
    d.verify()
    country,family,year,revision=a.country,a.family,a.year,a.revision;cfg=a.cfg;snap=cfg['sha256'];vin=cfg['vintage']
    res=dict(vector_id=f'{country}_{family}_{year}'+('' if revision=='selected' else '_'+revision),country_id=country,family=family,year=year,revision=revision,source_id=a.key,snapshot_sha256=snap,source_vintage=vin,
             synthetic=synthetic,contract=CONTRACT,status=None,reasons=[],checks={},primitives={},members=[],derived={},share_envelopes={},rule_v2=None,dossier_seal=None,multiplier=None,projection=None)
    def done(status):
        res['status']='synthetic_'+status if synthetic else status
        return res
    res['dossier_seal']=d.seal
    rules=d.rules_for(country,year,a.key,snap,vin)
    if not rules:res['reasons'].append('no_publication_rule_for_this_vector');return done('unknown')
    raw=raw if raw is not None else read_source(a.key)[1];need(sha(raw)==snap,'snapshot hash does not match registered source')
    snapshot=a.snapshot(raw)
    res['multiplier']=snapshot['context']['multiplier']
    # Authenticated projection (concept, selector) in facts.selectors order: the rule is bound to it (R3).
    res['projection']=[[m['concept'],m['selector']] for m in sorted(snapshot['members'],key=lambda m:m['selector'])]
    cells=cells if cells is not None else _cells(a,raw)
    ctx=dict(country=country,year=year,vintage=vin,snapshot=snap)
    members=[(m['concept'],m['selector'],parse_member(m['selector'])) for m in snapshot['members']]
    prims={}
    for _,_,terms in members:
        for p,_,flag in terms:prims.setdefault(p,flag)
    for p in CROSS_CHECK_CELLS.get(country,[]):prims.setdefault(p,'cross_check')
    paths={};fail=[]
    for p,flag in prims.items():
        try:paths[p]=_find_path(d,rules,p,flag,cells,ctx,res['reasons'])
        except ValueError as e:fail.append(str(e))
    if fail:res['reasons']+=['correspondence_failed:'+x for x in fail];return done('fail')
    if any(v is None for v in paths.values()):return done('unknown')
    doms={}
    for p,path in paths.items():
        try:
            if path['kind']=='exact':
                sh,c=p.split('!');cell=cells.get(sh,{}).get(c)
                need(cell is None or cell.get('value') in (None,'') or F(cell['value'])==0,'exact zero contradicted by stored cell '+p)
                doms[p]=(F(0),F(0));value='0'
            else:
                v=stored_value(cells,p);check_on_increment(v,path['unit'],p);doms[p]=nearest_domain(dec(v),path['unit']);value=dec(v)
            res['primitives'][p]=dict(primitive=p,value=value,kind=path['kind'],rounding_unit=path['unit'],domain=dom_json(doms[p]),rule_id=path['rule']['rule_id'],evidence_ids=path['evidence'],
                                      correspondence={'sna_code':path['corr']['sna_code'],'relation':path['corr']['relation'],'status':path['corr']['status']},
                                      basis=path['rule']['basis_category']+('+documented_interpretation' if path['rule']['interpretation'] else ''),status=path['status'],role='cross_check' if prims[p]=='cross_check' else 'member_term')
        except ValueError as e:fail.append(str(e))
    if fail:res['reasons']+=['domain_validation_failed:'+x for x in fail];return done('fail')
    by={}
    for concept,sel,terms in members:
        t=[(p,k) for p,k,_ in terms];md=affine_domain(terms_s(t),doms);by[concept]=t
        point=sum((k*F(res['primitives'][p]['value']) for p,k in t),F(0))
        res['members'].append(dict(concept=concept,selector=sel,terms=[[p,str(k)] for p,k in t],member_domain=dom_json(md),half_width=dec(half_width(md)),point_from_cells=dec(point)))
        if not synthetic:
            snapval=next(F(m['value_literal']) for m in snapshot['members'] if m['selector']==sel)
            if snapval!=point:fail.append('member value differs from stored cells '+sel)
    def expr(name,t):
        dmn=affine_domain(terms_s(t),doms);res['derived'][name]={'terms':[[p,str(k)] for p,k in t],'domain':dom_json(dmn),'half_width':dec(half_width(dmn))};return dmn
    neg=lambda t:[(p,-k) for p,k in t]
    if family=='D2':
        gm=by['GOS_MI'] if 'GOS_MI' in by else by['GOS']+by['MI']
        expr('PIB',by['PIB']);expr('COE',by['COE']);expr('GOS_MI',gm);expr('TAX_NET',by['TAX_NET'])
        ident=expr('IDENTITY_RESIDUAL',by['COE']+gm+by['TAX_NET']+neg(by['PIB']));res['checks']['identity_residual_contains_zero']=contains_zero(ident)
        if country=='MEX':
            x=expr('PUBLISHED_D2_PLUS_D3_minus_TAX_NET',[('Tabulado!R45',F(1)),('Tabulado!R54',F(1))]+neg(by['TAX_NET']));res['checks']['published_D2_plus_D3_contains_TAX_NET']=contains_zero(x)
        for n,t in (('COE',by['COE']),('GOS_MI',gm),('TAX_NET',by['TAX_NET'])):res['share_envelopes'][n]=ratio_envelope(t,by['PIB'],doms)
    elif 'V' in by:
        # Net route (PER, D-02). Components from shared primitives; totals grouped before propagation.
        vat=by['V'];other=by['P_NET']+neg(by['V']);prod=by['N_PROD'];total=by['P_NET']+by['N_PROD']
        for n,t in (('VAT',vat),('OTHER_PRODUCTS',other),('PRODUCTION',prod),('NET_PRODUCTS_P',by['P_NET']),('TOTAL',total)):expr(n,t)
        for n,t in (('VAT',vat),('OTHER_PRODUCTS',other),('PRODUCTION',prod),('TOTAL',total)):res['share_envelopes'][n]=ratio_envelope(t,by['PIB'],doms)
        a2=NationalAdapter(country,'D2',year,revision)
        d2=_validate(a2,d,raw=read_source(a2.key)[1],cells=cells if synthetic else None,synthetic=synthetic)
        st2=d2['status'].replace('synthetic_','')
        if st2 not in ('pass','candidate_pending_review','declared_interpretation'):res['reasons'].append('joint_D2_not_validated:'+st2);return done('unknown' if st2=='unknown' else 'fail')
        for p,dd in d2['primitives'].items():
            if p in res['primitives']:need(dd['domain']==res['primitives'][p]['domain'],'shared primitive with two assignments '+p)
        d2pib=[(p,F(k)) for p,k in d2['derived']['PIB']['terms']];d2tax=[(p,F(k)) for p,k in d2['derived']['TAX_NET']['terms']]
        res['checks']['same_authenticated_PIB_primitive']=sorted((p,k) for p,k in d2pib)==sorted((p,k) for p,k in by['PIB'])
        alld={**{p:(F(v['domain'][0]),F(v['domain'][1])) for p,v in d2['primitives'].items()},**doms}
        res['identities_by_construction']={}
        for n,t in (('TAX_D2_minus_D6',d2tax+neg(total)),('GDP_D2_minus_D6',d2pib+neg(by['PIB']))):
            dmn=affine_domain(terms_s(t),alld)
            res['identities_by_construction'][n]={'terms':[[p,str(k)] for p,k in t],'domain':dom_json(dmn),
                                                   'nature':'identical shared primitives cancel; not an independent reconciliation test'}
            need(dmn==(F(0),F(0)),'net route no longer shares the D2 primitive: '+n)
        if country=='PER':
            pv=lambda s:stored_value(cells,s)
            gross=sum(pv(s) for s in ('COU_2023!K376','COU_2023!F376','COU_2023!I376','COU_2023!J376'))
            res['published_contrasts']={
                'CEI_E24_equals_COU_gross_components':pv('CEI_2023!E24')==gross+pv('COU_2023!DL389'),
                'CEI_E25_D21-D31_equals_COU_product_components':pv('CEI_2023!E25')==gross,
                'CEI_E26_D29-D39_equals_DL389_plus_zero':pv('CEI_2023!E26')==pv('COU_2023!DL389'),
                'nature':'equalities of published values (F376, I376, J376 are contrasts, not precision primitives)'}
            res['checks'].update({'published_contrast:'+k:v for k,v in res['published_contrasts'].items() if k!='nature'})
    elif 'D211' in by:
        vat=by['D211'];other=by['D21']+neg(by['D211'])+by['D31'];prod=by['D29']+by['D39'];total=by['D21']+by['D31']+by['D29']+by['D39']
        for n,t in (('D21',by['D21']),('D21_minus_D211',by['D21']+neg(by['D211'])),('VAT',vat),('OTHER_PRODUCTS',other),('PRODUCTION',prod),('TOTAL',total)):expr(n,t)
        for n,t in (('VAT',vat),('OTHER_PRODUCTS',other),('PRODUCTION',prod),('TOTAL',total)):res['share_envelopes'][n]=ratio_envelope(t,by['PIB'],doms)
        # Joint D2/D6: the D2 vector of the same country and year, SAME primitive assignment.
        a2=NationalAdapter(country,'D2',year,revision)
        d2=_validate(a2,d,raw=read_source(a2.key)[1],cells=cells if synthetic else None,synthetic=synthetic)
        st2=d2['status'].replace('synthetic_','')
        if st2 not in ('pass','candidate_pending_review','declared_interpretation'):res['reasons'].append('joint_D2_not_validated:'+st2);return done('unknown' if st2=='unknown' else 'fail')
        for p,dd in d2['primitives'].items():
            if p in res['primitives']:need(dd['domain']==res['primitives'][p]['domain'],'shared primitive with two assignments '+p)
        alld={**{p:(F(v['domain'][0]),F(v['domain'][1])) for p,v in d2['primitives'].items()},**doms}
        d2tax=[(p,F(k)) for p,k in d2['derived']['TAX_NET']['terms']];d2pib=[(p,F(k)) for p,k in d2['derived']['PIB']['terms']]
        for n,t in (('TAX_D2_minus_D6',d2tax+neg(total)),('GDP_D2_minus_D6',d2pib+neg(by['PIB']))):
            dmn=affine_domain(terms_s(t),alld);res['derived'][n]={'terms':[[p,str(k)] for p,k in t],'domain':dom_json(dmn),'half_width':dec(half_width(dmn))};res['checks'][n+'_contains_zero']=contains_zero(dmn)
        if country=='PER':
            pv=lambda s:stored_value(cells,s)
            res['checks']['CEI_E25_D21-D31_equals_COU']=pv('CEI_2023!E25')==sum(pv(s) for s in ('COU_2023!K376','COU_2023!F376','COU_2023!I376','COU_2023!J376'))
            res['checks']['CEI_E26_D29-D39_equals_COU']=pv('CEI_2023!E26')==pv('COU_2023!DL389')
    bad=[k for k,v in res['checks'].items() if v is not True]
    if fail or bad:res['reasons']+=['domain_validation_failed:'+x for x in fail+bad];return done('fail')
    # CA2-2X representation of the vector (built even if pending; emitted by adapters only on pass).
    member_prims=[p for p in res['primitives'] if res['primitives'][p]['role']=='member_term']
    kinds={res['primitives'][p]['kind'] for p in member_prims}
    rule={'contract_version':CONTRACT+(ca2x.SYNTHETIC_MARK if synthetic else ''),'kind':'mixed' if len(kinds)>1 else next(iter(kinds)),
          'primitives':[{k:v for k,v in res['primitives'][p].items() if k!='role'} for p in sorted(member_prims)],
          'selector_rules':[{'selector':m['selector'],'concept':m['concept'],'terms':m['terms'],'member_domain':m['member_domain'],'rule_locator':'dossier:'+d.seal[:16]+':'+';'.join(sorted({res['primitives'][p]['rule_id'] for p,_ in m['terms']}))} for m in sorted(res['members'],key=lambda m:m['selector'])],
          'shared_denominator':{'concept':'PIB','member_selector':next(m['selector'] for m in res['members'] if m['concept']=='PIB'),'primitives':[p for p,_ in by['PIB']]},
          'vector_binding':{'snapshot_sha256':snap,'projection_sha256':ca2x.projection_digest(res['projection'])}}
    ca2x.validate(rule,res['projection'],cells=cells,snapshot_sha256=snap,emitted=False,accept_synthetic=synthetic)
    res['rule_v2']=rule
    if any(res['primitives'][p]['status']!='ok' for p in res['primitives']):return done('candidate_pending_review')
    # D-03 corrected: a declared interpretation keeps its labelled domains but is never an institutional pass.
    if any(res['primitives'][p]['basis'].endswith('+documented_interpretation') for p in res['primitives']):
        res['reasons'].append('declared_interpretation_not_institutional_precision');return done('declared_interpretation')
    return done('pass')

# ------------------------------------------------------------------ consumers (all derived from validate_vector)
def precision_state(adapter):return validate_vector(adapter.country,adapter.family,adapter.year,adapter.revision)['status']
def state(country,family,year):return validate_vector(country,family,year)['status']
def identity_tolerance_ncu(country,year):
    """Legacy semantics (sum of half-widths of the published identity primitives, in NCU), computed from the validation."""
    r=validate_vector(country,'D2',year)
    if r['status']!='pass':return None
    return F(r['derived']['IDENTITY_RESIDUAL']['half_width'])*F(r['multiplier'])
def per_2023():
    d2=validate_vector('PER','D2',2023);d6=validate_vector('PER','D6',2023)
    prim={**{p:v['domain'] for p,v in d2['primitives'].items()},**{p:v['domain'] for p,v in d6['primitives'].items()}}
    return {'country_id':'PER','year':2023,'snapshot_sha256':d2['snapshot_sha256'],'source_vintage':d2['source_vintage'],'units':PER_UNITS,'primitive_domains':dict(sorted(prim.items())),
            'derived':{**d2['derived'],**d6['derived']},'share_envelopes':{**d2['share_envelopes'],**d6['share_envelopes']},'published_contrasts':d6.get('published_contrasts'),'identities_by_construction':d6.get('identities_by_construction'),
            'D2':{'precision':d2['status'],'reasons':d2['reasons']},'D6':{'precision':d6['status'],'reasons':d6['reasons']},'representation_D6':'d6_net (D-02 candidate)','authority':'PER candidate orientation authority remains candidate_unapproved (D-01)','production_activation':False}
def col_2023():
    d2=validate_vector('COL','D2',2023);d6=validate_vector('COL','D6',2023)
    prim={**{p:v['domain'] for p,v in d2['primitives'].items()},**{p:v['domain'] for p,v in d6['primitives'].items()}}
    return {'country_id':'COL','year':2023,'snapshot_sha256':d2['snapshot_sha256'],'source_vintage':d2['source_vintage'],'units':COL_UNITS,'primitive_domains':dict(sorted(prim.items())),
            'derived':{**d2['derived'],**d6['derived']},'share_envelopes':{**d2['share_envelopes'],**d6['share_envelopes']},
            'D2':{'precision':d2['status'],'reasons':d2['reasons']},'D6':{'precision':d6['status'],'reasons':d6['reasons']},'representation_D6':'d6_gross',
            'evidence':'DANE 202610074537 (file bound by metadata, not by hash)','production_activation':False}
def mex_year(year,family='D2'):
    r=validate_vector('MEX',family,year)
    return {'label':'dominios bajo interpretación declarada (D-03): no precisión institucional, no emitibles, sin pase estricto','country_id':'MEX','family':family,'year':year,'snapshot_sha256':r['snapshot_sha256'],'source_vintage':r['source_vintage'],'units':MEX_UNITS,
            'primitive_domains':{p:v['domain'] for p,v in sorted(r['primitives'].items())},'derived':r['derived'],'share_envelopes':r['share_envelopes'],'precision':r['status'],'reasons':r['reasons'],'production_activation':False}
def precision_evidence_rows(results):
    """DB-05 precision_evidence, exact field list, from validated primitives only (pass or pending)."""
    rows=[];seen=set()
    for r in results:
        if r['status'] not in ('pass','candidate_pending_review'):continue
        country=r['country_id'];unit={'PER':'PEN','MEX':'MXN','COL':'COP','CHL':'CLP'}[country]
        for p,v in r['primitives'].items():
            key=(r['snapshot_sha256'],p)
            if key in seen:continue
            seen.add(key)
            exact=v['kind']=='exact'
            rows.append(dict(precision_id=f'PREC_{country}_{r["snapshot_sha256"][:12]}_{p.replace("!","_")}',source_snapshot_id=r['snapshot_sha256'],selector=p,unit=unit,multiplier=r['multiplier'],
                             rounding_rule=('exact_documented' if exact else v['rule_id']),rounding_unit=v['rounding_unit'] or '',interval_low=v['domain'][0],interval_high=v['domain'][1],
                             exactness_status=('exact_zero_documented' if exact else 'rounded_published_value'+('' if v['status']=='ok' else '_mapping_pending_review')),
                             evidence_id=';'.join(v['evidence_ids']),evidence_scope=f"{country} {r['year']} {v['correspondence']['sna_code']} ({v['correspondence']['relation']}; {v['basis']})"))
    return rows
