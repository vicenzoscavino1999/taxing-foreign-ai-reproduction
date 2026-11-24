"""Lectores nacionales incorporados en 1.5 (A-06). Fracciones exactas, sin admisión ni modelo.

Porte de codigo/nacionales.py de la entrega aprobada (inventario a88b683a…): las entradas se leen de la recepción
versionada fase2_datos/recepcion_nacional/versions/<árbol fijado>; los validadores son los de herramientas/s3; el lector
D2 legado es el constructor del proyecto (mismos bytes que el vendor de la entrega). Se retiraron las funciones que
leían correos privados: el expediente sellado basta (R2 del 27-09). Las salidas se escriben en un directorio explícito."""
from pathlib import Path
import sys, json, hashlib, re, csv, io, math
from fractions import Fraction as F
from decimal import Decimal
from functools import lru_cache
from .base import RECEPTION as A, load_xlrd, load_legacy_d2
from herramientas.s3.validadores.institucional import xlsx_cells, InstitutionalSnapshot, literal, nearest_domain, affine_domain, PER_MAIL, CHL_MAIL
from herramientas.s3.validadores.core import H, canon
import fitz
xlrd = load_xlrd()
legacy = load_legacy_d2()
xlsx_cells=lru_cache(maxsize=24)(xlsx_cells)
COUNTRIES=('CHL','COL','MEX','PER')
def sha(b):return hashlib.sha256(b).hexdigest()
def need(test,msg):
    if not test:raise ValueError(msg)
def finite_tree(x):
    if isinstance(x,dict):
        for v in x.values():finite_tree(v)
    elif isinstance(x,(list,tuple)):
        for v in x:finite_tree(v)
    elif isinstance(x,(float,Decimal)):need(math.isfinite(x),'nonfinite nested value')
    elif isinstance(x,str):need(x.strip().lower() not in ('nan','inf','infinity','-inf','+inf','-infinity','+infinity'),'nonfinite literal')
def write_json(path,obj):
    finite_tree(obj);path.parent.mkdir(parents=True,exist_ok=True)
    # Bytes with LF: hashes must not depend on platform newline translation.
    path.write_bytes((json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n').encode('utf-8'))
def write_csv(path,rows,fields=None):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
def q(x):
    need(type(x) in (str,int,F),'exact input required');return F(x)
def dec(x):return str(literal(F(x)))
def ratio(n,d):
    need(F(d)>0,'positive denominator required');r=F(n)/F(d)
    return {'numerator':str(r.numerator),'denominator':str(r.denominator)}
def source_config():
    raw=(A/'evidencia/registro_snapshots.json').read_bytes()
    need(sha(raw) in ('2d15e6a8b5e23e0e68fb1a78f5090b25c65ba5d7c7fa8c11f2f155387f86ab1c',  # registro historico
                   'cd986a5cba5114acc66c678cb596ff7598c112af5f66dfd33d7fa518e11d7706'),  # copia publica SAN-RUTAS-v1 del historico (solo cambia 'origin'; fuentes_fam01.json)
         'source registry changed; reviewed code/pins required')
    return json.loads(raw)
def read_source(key):
    cfg=source_config()[key];raw=(A/cfg['path']).read_bytes()
    need(sha(raw)==cfg['sha256'],'snapshot hash mismatch '+key)
    return cfg,raw
def assert_shared_dependency(terms,claimed):
    actual={}
    for key,k in terms:actual[key]=actual.get(key,F(0))+q(k)
    actual={k:dec(v) for k,v in actual.items() if v}
    need(actual==claimed,'shared primitive dependence lost or treated independently')
def cell(c,s):
    sh,pos=s.split('!');v=c[sh].get(pos)
    need(v is not None and v['type']=='n' and v['value'] is not None,'numeric selector missing '+s)
    return q(v['value'])
@lru_cache(maxsize=12)
def xls_cells(raw,year):
    w=xlrd.open_workbook(file_contents=raw);s=w.sheet_by_name(str(year));out={}
    def col(n):
        text=''
        while n:n,r=divmod(n-1,26);text=chr(65+r)+text
        return text
    for r in range(s.nrows):
        for c in range(s.ncols):
            v=s.cell(r,c);out[col(c+1)+str(r+1)]={'value':str(v.value) if v.ctype==2 else v.value,'type':'n' if v.ctype==2 else 's','formula':None}
    return {str(year):out}
@lru_cache(maxsize=10)
def pdf_account(raw,year):
    need(2015<=year<=2023,'PDF year outside registry')
    page_no=405+year-2015;doc=fitz.open(stream=raw,filetype='pdf');page=doc[page_no-1];text=page.get_text()
    need('Cuentas Económicas Integradas' in text and str(year) in text and 'Millones de soles' in text,'PDF scope mismatch')
    words=page.get_text('words');values={};selectors={}
    for concept,code in [('PIB','B.1b'),('COE','D.1'),('GOS','B.2b'),('MI','B.3b'),('TAX_NET','D.2-D.3')]:
        anchors=[w for w in words if w[4]==code];need(len(anchors)==1,'ambiguous PDF code '+code)
        y=(anchors[0][1]+anchors[0][3])/2
        ws=sorted((w for w in words if 198<=w[0]<223 and abs((w[1]+w[3])/2-y)<1),key=lambda w:w[0])
        val=''.join(w[4] for w in ws);need(bool(re.fullmatch(r'-?\d+',val)),'PDF domestic column invalid '+code)
        values[concept]=F(val);selectors[concept]=f'PDF:p{page_no}:Empleos/EconomiaTotal:{code}:x[198,223):y={y}'
    doc.close();return values,selectors

class NationalAdapter:
    """Registry supplied by executable caller; scope and bytes checked before extraction."""
    def __init__(self,country,family,year=2023,revision='selected'):
        need(country in COUNTRIES and family in ('D2','D6'),'country/family')
        need(2015<=year<=2023 and (family=='D2' or year==2023),'year scope')
        need(revision in ('selected','COL_2024p','PER_pdf_2023'),'revision registry')
        need(revision=='selected' or (country=='COL' and revision=='COL_2024p') or (country=='PER' and revision=='PER_pdf_2023' and year==2023 and family=='D2'),'revision scope')
        self.country,self.family,self.year,self.revision=country,family,year,revision
        self.key=('PER_PDF' if country=='PER' and (year<2023 or revision=='PER_pdf_2023') else f'MEX_{year}' if country=='MEX' else 'COL_2024p' if revision=='COL_2024p' else 'CHL_CEI' if country=='CHL' and family=='D2' else 'CHL_COU' if country=='CHL' else country+'_2023')
        self.cfg=source_config()[self.key]
    def snapshot(self,raw):
        need(sha(raw)==self.cfg['sha256'],'hash does not match registered source')
        c,f,y=self.country,self.family,self.year
        members=[];primitives={}
        def add(concept,*terms):
            val=sum((F(k)*cell(cells,s) for s,k in terms),F(0));sel=';'.join(f'{s}:{k}' for s,k in terms)
            members.append(dict(concept=concept,selector=sel,unit=unit,multiplier=mult,value_literal=dec(val)))
        unit={'PER':'PEN','MEX':'MXN','COL':'COP','CHL':'CLP'}[c];mult='1000000' if c in ('PER','MEX') else '1000000000'
        if self.key=='PER_PDF':
            vals,sels=pdf_account(raw,y)
            members=[dict(concept=k,selector=sels[k],unit=unit,multiplier=mult,value_literal=dec(v)) for k,v in vals.items()]
        else:
            cells=xls_cells(raw,y) if self.key=='CHL_CEI' else xlsx_cells(raw)
            if c=='PER':
                # Active source adapter includes authenticated semantic zero, verified separately below.
                snap=InstitutionalSnapshot(c,f).snapshot(raw);members=snap['members']
                if f=='D6':
                    # Exact-zero reading of the blank DL390 needs current scoped evidence in the sealed dossier (no private EML).
                    from . import precision;precision.require_exact_zero_evidence(self.cfg['sha256'],'COU_2023!DL390')
            elif c=='MEX':
                header=cells['Tabulado'];need(str(y) in str(header['A3']['value']) and '2018' in str(header['A2']['value']),'MEX year/base mismatch')
                need(cells['MetaInfo']['C14']['value']=='2026-06-30' and cells['MetaInfo']['C5']['value']=='Nacional','MEX revision/coverage mismatch')
                for a,b in [('S34','M34'),('R36','L36'),('R60','L60'),('R61','L61')]:need(cell(cells,'Tabulado!'+a)==cell(cells,'Tabulado!'+b),'domestic versus total discrepancy')
                add('PIB',('Tabulado!S34',1))
                if f=='D2':
                    for k,s in [('COE','R36'),('GOS','R60'),('MI','R61')]:add(k,('Tabulado!'+s,1))
                    add('TAX_NET',*[(f'Tabulado!{s}',1) for s in ('R46','R53','R55','R59')])
                else:
                    for k,s in [('D21','R46'),('D211','R47'),('D29','R53'),('D31','R55'),('D39','R59')]:add(k,('Tabulado!'+s,1))
            elif c=='COL':
                sh=str(y);need(sh in cells and 'PRODUCTO INTERNO BRUTO' in str(cells[sh]['K29']['value']),'COL GDP label/year')
                for pos,code in [('J36','D.1'),('J47','B.2b'),('J48','B.3b'),('J63','D.21'),('J68','D.29'),('J70','D.31'),('J71','D.39')]:need(cells[sh][pos]['value'].strip()==code,'COL concept selector mismatch')
                need(cells[sh]['A7']['value']=='En miles de millones de pesos','COL unit mismatch')
                need(cell(cells,sh+'!A36')==cell(cells,sh+'!D36'),'COL domestic remuneration mismatch')
                add('PIB',(sh+'!A29',1))
                if f=='D2':
                    for k,s in [('COE','A36'),('GOS','A47'),('MI','A48')]:add(k,(sh+'!'+s,1))
                    add('TAX_NET',*[(sh+'!'+s,1) for s in ('Q63','Q68','Q70','Q71')])
                else:
                    for k,s in [('D21','Q63'),('D211','Q64'),('D29','Q68'),('D31','Q70'),('D39','Q71')]:add(k,(sh+'!'+s,1))
            elif f=='D2':
                need(str(y) in str(cells[str(y)]['B5']['value']),'CHL year mismatch')
                for k,s in [('COE','D22'),('GOS_MI','D24'),('TAX_NET','D30')]:add(k,(str(y)+'!'+s,1))
                add('PIB',*[(str(y)+'!'+s,1) for s in ('D22','D24','D30')])
            else:members=InstitutionalSnapshot('CHL','D6').snapshot(raw)['members']
        context=dict(family=f,country_id=c,observation_year=y,source_id=self.key,source_vintage=self.cfg['vintage'],representation=('d2_combined' if c=='CHL' else 'd2_split') if f=='D2' else ('d6_net' if c in ('CHL','PER') else 'd6_gross'),unit=unit,multiplier=mult,accounting_basis={'PER':'SNA2008_base2007','COL':'SNA2008_base2015','MEX':'SNA2008_base2018','CHL':'SNA2008_reference2018'}[c])
        result={'context':context,'members':sorted(members,key=lambda m:m['concept'])};finite_tree(result);return result
    def read(self):return self.snapshot(read_source(self.key)[1])
def values(s):return {m['concept']:F(m['value_literal']) for m in s['members']}
def components_sum(m):return m['COE']+m['TAX_NET']+(m['GOS_MI'] if 'GOS_MI' in m else m['GOS']+m['MI'])
def identity_residual_level(m):
    """Level diagnostic, sign COMPONENTS minus GDP, same unit/multiplier as the inputs."""
    return components_sum(m)-m['PIB']
def identity_residual_ratio(m):
    """Historical D2 definition: (COE + GOS + MI + TAX_NET - GDP) / GDP; GOS_MI when published combined."""
    need(m['PIB']>0,'positive GDP required for identity_residual');return identity_residual_level(m)/m['PIB']
def residual(s):
    # Sign is components minus GDP (the previous candidate exported GDP minus components).
    return identity_residual_level(values(s))
def display15(frac):
    """Legacy 15-decimal display of an exact ratio; -0 normalized. Not source precision."""
    t=format(Decimal(frac.numerator)/Decimal(frac.denominator),'.15f')
    return t[1:] if t.startswith('-') and Decimal(t)==0 else t
def identity_fields(m,multiplier):
    """Exported identity fields: historical ratio plus a separately named level diagnostic."""
    lvl=identity_residual_level(m);rat=identity_residual_ratio(m)
    return {'identity_residual':display15(rat),'identity_residual_exact':json.dumps(ratio(lvl,m['PIB'])),'identity_residual_level':dec(lvl),'identity_residual_level_ncu':dec(lvl*F(multiplier))}
def projected(d6):
    m=values(d6);c=d6['context']['country_id']
    if d6['context']['representation']=='d6_net':terms={'VAT':m['V'],'OTHER_PRODUCTS':m['P_NET']-m['V'],'PRODUCTION':m['N_PROD']}
    else:
        # Published subsidies are signed negative; orientation is multiplication, never abs.
        need(m['D31']<=0 and m['D39']<=0,'unexpected published subsidy orientation')
        terms={'VAT':m['D211'],'OTHER_PRODUCTS':m['D21']-m['D211']+m['D31'],'PRODUCTION':m['D29']+m['D39']}
    return terms
def pair_check(d2,d6):
    a,b=d2['context'],d6['context'];need(a['country_id']==b['country_id'],'country pair')
    need(a['family']=='D2' and b['family']=='D6' and b['observation_year']==2023,'family/year pair')
    for k in ('unit','multiplier','accounting_basis'):need(a[k]==b[k],'unit/base pair mismatch')
    if a['observation_year']!=2023:return {'kind':'historical_own_denominator_fixed_D6_2023','gdp_residual':None,'tax_residual':None}
    need(a['source_vintage']==b['source_vintage'],'mixed vintages')
    x,y=values(d2),values(d6);return {'kind':'primary','gdp_residual':dec(x['PIB']-y['PIB']),'tax_residual':dec(x['TAX_NET']-sum(projected(d6).values()))}
def roles(adapter,snapshot):
    c,f=adapter.country,adapter.family
    raw=read_source(adapter.key)[1]
    need(adapter.snapshot(raw)==snapshot,'projection differs from authenticated source')
    status={r:'pass' for r in ('snapshot','provenance','concept','coverage','orientation','reconciliation')}
    from . import precision  # lazy: precision imports this module
    status['precision']=precision.precision_state(adapter)  # the single effective validation, never a fixed rule
    if c=='CHL':
        status.update(coverage='unknown',reconciliation='unknown')
        # Derived market GDP cannot be called independent published GDP.
    elif f=='D2' and residual(snapshot)!=0:status['reconciliation']='unknown'
    if f=='D6':
        projected(snapshot)
        a=NationalAdapter(c,'D2',2023,adapter.revision if c=='COL' else 'selected').read();p=pair_check(a,snapshot)
        if p['gdp_residual']!='0' or p['tax_residual']!='0':status['reconciliation']='unknown'
        if c=='PER':
            # Net route: the D2-D6 total is equal by construction (shared E24). Reconciliation rests on the
            # published contrasts of the same file, which must hold exactly.
            status['reconciliation']='pass' if all(per_published_contrasts(raw).values()) and status['reconciliation']=='pass' else 'fail'
    return status
def per_published_contrasts(raw):
    """Equalities of PUBLISHED values of the PER workbook (F376, I376, J376 as contrasts, not precision primitives)."""
    need(sha(raw)==source_config()['PER_2023']['sha256'],'PER snapshot')
    c=xlsx_cells(raw);v=lambda s:cell(c,s)
    gross=v('COU_2023!K376')+v('COU_2023!F376')+v('COU_2023!I376')+v('COU_2023!J376')
    return {'CEI_E24_equals_COU_gross_components':v('CEI_2023!E24')==gross+v('COU_2023!DL389'),
            'CEI_E25_equals_COU_product_components':v('CEI_2023!E25')==gross,
            'CEI_E26_equals_DL389_plus_zero':v('CEI_2023!E26')==v('COU_2023!DL389'),
            'Resumen_D14_equals_E14':v('Resumen!D14')==v('Resumen!E14'),
            'Resumen_D11_PIB_check_zero':v('Resumen!D11')==0}
def compare_col_revisions(year):
    aa=[NationalAdapter('COL','D2',year,r) for r in ('selected','COL_2024p')]
    ss=[a.read() for a in aa]
    need(aa[0].cfg['sha256']!=aa[1].cfg['sha256'] and ss[0]['context']['source_vintage']!=ss[1]['context']['source_vintage'],'distinct revisions required')
    for field in ('representation','unit','multiplier','accounting_basis'):
        need(ss[0]['context'][field]==ss[1]['context'][field],'revision comparison incompatible')
    need([m['concept'] for m in ss[0]['members']]==[m['concept'] for m in ss[1]['members']],'complete concepts in revisions required')
    outcomes=[roles(a,s) for a,s in zip(aa,ss)]
    if year==2023:
        b=NationalAdapter('COL','D6',2023,'COL_2024p');outcomes.append(roles(b,b.read()))
    complete=all(all(v[r]=='pass' for r in ('concept','coverage','orientation','provenance','reconciliation')) for v in outcomes)
    return dict(year=year,related_snapshots=sorted(a.cfg['sha256'] for a in aa),complete_vectors=True,comparability_technical=complete,status='implemented_pending_review' if complete else 'pending_reconciliation',D6_policy='own_complete_revised_D6_2023' if year==2023 else 'fixed_selected_D6_2023',production_activation=False)
READY={'E0':'candidate_strict_ready','E3':'candidate_strict_ready','E1':'candidate_conditional_ready','E2':'candidate_conditional_ready'}
def eligibility(d2,d6,scenario,complete_revisions=False,comparability=False,extra_reasons=()):
    """Status is 'blocked' whenever any reason remains; WHO can lift each reason is classified separately."""
    need(scenario in ('E0','E1','E2','E3','E4'),'unknown scenario')
    if scenario=='E4':return 'not_identified',['measurement_domain_not_supported']
    reasons=[]
    for family,state in [('D2',d2),('D6',d6)]:
        for role in ('snapshot','provenance','concept','coverage','orientation','reconciliation'):
            if state.get(role)!='pass':reasons.append(f'{family}:{role}:{state.get(role,"missing")}')
        if scenario in ('E0','E3') and state.get('precision')!='pass':reasons.append(f'{family}:precision:{state.get("precision","missing")}')
    if scenario=='E2' and not (complete_revisions and comparability):reasons.append('E2:complete_comparable_revisions_missing')
    if scenario in ('E0','E3'):reasons.extend(extra_reasons)
    return ('blocked' if reasons else READY[scenario]),reasons
def four_country_case(rows):
    need(sorted(r['country_id'] for r in rows)==list(COUNTRIES),'four complete countries required')
    statuses={r['status'] for r in rows}
    if len(statuses)==1 and next(iter(statuses)) in READY.values():return next(iter(statuses))
    return 'blocked'
def check_label(actual,claimed):need(actual==claimed,'eligibility label not demonstrated')
def scope_evidence(claim,country,year,vintage,selector):
    need((claim['scope_country'],claim['scope_year'],claim['scope_vintage'])==(country,year,vintage),'evidence out of scope')
    need(selector in claim['scope_cell_or_range'],'selector outside evidence')

def legacy_accounts():
    _,raw=read_source('UN_bundle');members,_=legacy.read_bundle(A/source_config()['UN_bundle']['path'])
    ama_name=next(n for n in members if 'ama_gdp' in n);ama,_=legacy.parse_ama_gdp(members[ama_name]);out={}
    for c in COUNTRIES:
        blob=read_source('UN_COL')[1] if c=='COL' else members[next(n for n in members if 'table401_'+c in n)]
        pan=legacy.parse_table_csv(legacy.unzip_single_csv(blob,c),c)
        for y in range(2015,2024):
            v=pan.values[y];g=F(ama[c][y]);d={'PIB':g,'COE':F(v['D.1'])}
            if c=='CHL':d.update(GOS_MI=F(v['B.1*g'])-d['COE']-F(v['D.2-D.3']),TAX_NET=F(v['D.2-D.3'])+g-F(v['B.1*g']))
            else:d.update(GOS=F(v['B.2g']),MI=F(v['B.3g']),TAX_NET=F(v['D.2-D.3']))
            out[(c,y)]=d
    return out

def build(out):
    """Escribe en out/datos y out/review; no escribe en la recepción."""
    from . import evidencia as ev, precision as pr, clasificacion as cl, mex_csi103, comparabilidad_col
    claims=ev.load_claims();bindings=ev.load_bindings()
    snapshots=[];adapters={};states={};d2=[];old=legacy_accounts();bridge=[];recon=[];d6rows=[]
    legacy_manifest=A/'evidencia/d2_manifest_antecesor.json';oldh=sha(legacy_manifest.read_bytes())
    need(oldh=='78791c19b28322e581826a5628c6cacbb3a746f6cc62488b43f8665d3ea36ec4','legacy manifest pin')
    oldmeta_raw=(A/'evidencia/d2_sensibilidad_antecesora.csv').read_bytes()
    need(sha(oldmeta_raw)==json.loads(legacy_manifest.read_bytes())['artifacts']['labor_income_shares_sensitivity.csv']['sha256'],'legacy metadata pin')
    oldmeta={(r['country_id'],int(r['observation_year'])):r for r in csv.DictReader(io.StringIO(oldmeta_raw.decode('utf-8-sig')))}
    # Candidate publication-precision domains (strict route only) and their DB-05 rows.
    validations=[pr.validate_vector(c,f,y) for c in COUNTRIES for f,ys in (('D2',range(2015,2024)),('D6',[2023])) for y in ys]
    vres={(v['country_id'],v['family'],v['year']):v for v in validations}
    per=pr.per_2023();mex={y:pr.mex_year(y,'D2') for y in range(2015,2024)};mex6=pr.mex_year(2023,'D6')
    prec_rows=pr.precision_evidence_rows(validations);prec_by_key={(r['source_snapshot_id'],r['selector']):r for r in prec_rows}
    for r in prec_rows:
        for eid in r['evidence_id'].split(';'):need(eid in claims,'precision evidence id not in DB-02 registry: '+eid)
    def precision_ids(snapshot,member_selector):
        ids=[]
        for p in sorted(ev.primitive_selectors(member_selector)):
            r=prec_by_key.get((snapshot,p));need(r is not None,'accredited vector without primitive precision row '+p);ids.append(r['precision_id'])
        return ';'.join(ids)
    for c in COUNTRIES:
        b=NationalAdapter(c,'D6');b6=b.read();states[(c,'D6',2023)]=roles(b,b6)
        snapshots.append({'id':f'{c}_D6_2023','source':b.cfg,**b6});adapters[f'{c}_D6_2023']=b
        for name,val in projected(b6).items():
            d6rows.append(dict(country_id=c,year=2023,component=name,value=dec(val),gdp=dec(values(b6)['PIB']),share_exact=ratio(val,values(b6)['PIB']),snapshot_sha256=b.cfg['sha256'],source_vintage=b.cfg['vintage'],unit=b6['context']['unit'],multiplier=b6['context']['multiplier'],denominator_id=f'{c}_D6_2023:PIB',status='evaluation_candidate_not_admitted',
                               precision_state=states[(c,'D6',2023)]['precision'],precision_interval=(vres[(c,'D6',2023)]['derived'][name]['domain'] if vres[(c,'D6',2023)]['status'] in ('pass','candidate_pending_review') else None)))
        for y in range(2015,2024):
            a=NationalAdapter(c,'D2',y);s=a.read();st=roles(a,s);states[(c,'D2',y)]=st
            snapshots.append({'id':f'{c}_D2_{y}','source':a.cfg,**s});adapters[f'{c}_D2_{y}']=a
            m=values(s);gm=m.get('GOS_MI',m.get('GOS',F(0))+m.get('MI',F(0)));sel={mm['concept']:mm['selector'] for mm in s['members']}
            # Finding 1: evidence_id is a DB-02 claim, resolved semantically; source_id is the registry key.
            evid=f'D2_{c}_{y}';scope=dict(country=c,year=y,vintage=a.cfg['vintage'],snapshot=a.cfg['sha256'],claims=claims,bindings=bindings)
            ev.resolve(evid,role='account',selectors=list(sel.values()),**scope)
            pid=';'.join(precision_ids(a.cfg['sha256'],sel[k]) for k in sorted(sel)) if st['precision']=='pass' else ''
            idf=identity_fields(m,s['context']['multiplier'])
            row=dict(country_id=c,year=y,PIB=dec(m['PIB']),COE=dec(m['COE']),GOS=dec(m['GOS']) if 'GOS' in m else '',MI=dec(m['MI']) if 'MI' in m else '',GOS_MI=dec(gm),TAX_NET=dec(m['TAX_NET']),unit=s['context']['unit'],multiplier=s['context']['multiplier'],base=s['context']['accounting_basis'],domestic_or_resident='domestic',valuation='market_prices',
                     source_snapshot_id=a.cfg['sha256'],source_id=a.key,source_vintage=a.cfg['vintage'],publication_status=('provisional' if c=='PER' and y in (2022,2023) else 'see_source_year_header'),PIB_kind='derived_from_income_components' if c=='CHL' else 'published',
                     identity_residual=idf['identity_residual'],identity_residual_exact=idf['identity_residual_exact'],identity_residual_level=idf['identity_residual_level'],identity_residual_level_convention='COE+GOS+MI+TAX_NET-PIB (GOS_MI if combined); unit and multiplier of this row',
                     COE_GDP_exact=json.dumps(ratio(m['COE'],m['PIB'])),GOS_MI_GDP_exact=json.dumps(ratio(gm,m['PIB'])),TAX_NET_GDP_exact=json.dumps(ratio(m['TAX_NET'],m['PIB'])),evidence_id=evid,precision_id=pid,precision_state=st['precision'],candidate_status='complete_extraction_pending_review')
            d2.append(row);recon.append(dict(country_id=c,year=y,d2_identity_residual=row['identity_residual'],d2_identity_residual_level=row['identity_residual_level'],independent_PIB=c!='CHL',**pair_check(s,b6)))
            mult=F(s['context']['multiplier'])
            for concept,val in m.items():
                ev.resolve(evid,role='account',selectors=[sel[concept]],**scope)  # per-concept scope, not just the account
                ov=old[(c,y)][concept]/mult
                bridge.append(dict(country_id=c,year=y,concept_id=concept,old_manifest_sha256=oldh,new_source_snapshot_id=a.cfg['sha256'],old_value=dec(ov),new_value=dec(val),unit=s['context']['unit'],multiplier=str(mult),old_vintage=oldmeta[(c,y)]['source_vintage'],new_vintage=a.cfg['vintage'],delta=dec(val-ov),reason='complete_national_account_revision; legacy levels re-extracted from raw; no ratio inversion',
                                   evidence_id=evid,precision_id=precision_ids(a.cfg['sha256'],sel[concept]) if st['precision']=='pass' else '',new_source_id=a.key,new_selector=sel[concept],old_source_id='UN_SNA_MAIN_legacy',precision_state=st['precision']))
    matrix=[]
    from . import casos
    registry=casos.load_registry();col_comp=comparabilidad_col.review()
    extra={}  # CA2-2X represents mixed exact/rounded vectors: the former internal blocker no longer applies
    for y in range(2015,2024):
        for scenario in ('E0','E1','E2','E3','E4'):
            rows=[]
            for c in COUNTRIES:
                comp=compare_col_revisions(y) if c=='COL' and scenario=='E2' else None
                status,why=eligibility(states[(c,'D2',y)],states[(c,'D6',2023)],scenario,complete_revisions=bool(comp and comp['complete_vectors']),comparability=bool(comp and comp['comparability_technical']),extra_reasons=extra.get((c,y),[]))
                items,flags=cl.classify_row(c,y,scenario,why)
                open_items=['source admission and production activation not authorized (1.5)']
                if c=='PER':open_items.append('D-01 PER orientation authority: author decision pending')
                if c=='PER' and y==2023 and scenario in ('E0','E3'):open_items.append('D-02 PER net representation: author decision pending')
                if c=='COL' and scenario=='E2' and y==2023:open_items.append('D-09 COL 2024p orientation extension: author decision pending')
                row=dict(country_id=c,year=y,scenario=scenario,status=status,blocking_reasons=';'.join(why),blocking_classification=json.dumps(items,ensure_ascii=False,sort_keys=True),**flags,
                         precision_state_D2=states[(c,'D2',y)]['precision'],precision_state_D6_2023=states[(c,'D6',2023)]['precision'],precision_required=scenario in ('E0','E3'),
                         admitted_limitation='publication_precision_not_asserted' if scenario in ('E1','E2') else '',all_applicable_routes_blocked=any(states[(c,f,yr)][r]!='pass' for f,yr in [('D2',y),('D6',2023)] for r in ('snapshot','provenance','concept','coverage','orientation','reconciliation')),
                         open_items_non_blocking=';'.join(open_items),version_disposition=casos.disposition(registry,c,y,scenario),production_activation=False)
                rows.append(row);matrix.append(row)
    joint=casos.evaluate(matrix,registry,col_comp)
    d2_fields=list(d2[0]);write_json(out/'datos/vectores.json',snapshots);write_csv(out/'datos/d2_2015_2023.csv',d2,d2_fields);write_csv(out/'datos/d2_primaria_2023.csv',[r for r in d2 if r['year']==2023],d2_fields)
    db03=['country_id','year','concept_id','old_manifest_sha256','new_source_snapshot_id','old_value','new_value','unit','multiplier','old_vintage','new_vintage','delta','reason','evidence_id','precision_id']
    write_csv(out/'datos/d2_revision_bridge.csv',[{k:r[k] for k in db03} for r in bridge],db03)  # DB-03 exact field list
    write_csv(out/'datos/puente_revisiones.csv',bridge)  # extended: source ids, selector and precision state
    scientific=[]
    for r in d2:
        def displayed_ratio(field):
            # Display serialization only; the adjacent exact ratio is authoritative.
            return display15(F(r[field])/F(r['PIB']))
        a=NationalAdapter(r['country_id'],'D2',r['year']);acc=r['precision_state']=='pass'
        tol=pr.identity_tolerance_ncu(r['country_id'],r['year']) if acc else None
        lvl_ncu=F(r['identity_residual_level'])*F(r['multiplier'])  # same value as identity_fields()['identity_residual_level_ncu']
        rule=';'.join(sorted({e for v in vres[(r['country_id'],'D2',r['year'])]['primitives'].values() for e in v['evidence_ids']})) if acc else ''
        scientific.append(dict(country_id=r['country_id'],observation_year=r['year'],source_snapshot_id=r['source_snapshot_id'],source_vintage=r['source_vintage'],coe_gdp=displayed_ratio('COE'),gos_mi_gdp=displayed_ratio('GOS_MI'),taxes_net_gdp=displayed_ratio('TAX_NET'),gdp_market_prices=dec(F(r['PIB'])*F(r['multiplier'])),
            identity_residual=r['identity_residual'],precision_basis='source_declared_rounding_interval' if acc else ('declared_interpretation_not_institutional' if r['precision_state']=='declared_interpretation' else 'unknown_publication_rule_for_complete_vector'),precision_source_id=rule,precision_half_width_ncu=dec(tol) if acc else '',
            rounding_consistency_status=('PASS' if abs(lvl_ncu)<=tol else 'FAIL') if acc else 'NOT_VALIDATED',s_L_bar=displayed_ratio('COE'),mi_partition_status='D2_NO_PARTITION',source_id=a.key,retrieved_at=a.cfg.get('accessed_at',a.cfg.get('obtained_at','')),source_status='candidate_not_admitted',source_evidence_id=r['evidence_id'],precision_id=r['precision_id'],
            domestic_or_resident='domestic',valuation_basis='market_prices_derived' if r['country_id']=='CHL' else 'market_prices_published',coe_gdp_exact=r['COE_GDP_exact'],gos_mi_gdp_exact=r['GOS_MI_GDP_exact'],taxes_net_gdp_exact=r['TAX_NET_GDP_exact'],
            identity_residual_exact=r['identity_residual_exact'],identity_residual_level_ncu=dec(lvl_ncu),identity_residual_level_convention='COE+GOS+MI+TAX_NET-PIB in national currency units (multiplier applied)',display_serialization='15_decimal_places_not_source_precision'))
        need(scientific[-1]['rounding_consistency_status']!='FAIL','identity outside accredited publication tolerance '+r['country_id']+str(r['year']))
    write_csv(out/'datos/labor_income_shares_sensitivity_candidato.csv',scientific)
    write_csv(out/'datos/labor_income_shares_candidato.csv',[r for r in scientific if r['observation_year']==2023])
    write_csv(out/'datos/precision_evidence_candidato.csv',prec_rows,['precision_id','source_snapshot_id','selector','unit','multiplier','rounding_rule','rounding_unit','interval_low','interval_high','exactness_status','evidence_id','evidence_scope'])
    write_json(out/'datos/dominios_candidatos.json',{'source':'precision.validate_vector (single effective validation)','dossier_seal':pr.SEAL_SHA256,'validations':validations,'views':{'PER_2023':per,'COL_2023':pr.col_2023(),'MEX_D2':{str(y):v for y,v in mex.items()},'MEX_D6_2023':mex6},
        'others':'CHL: no publication rule in the dossier; COL 2015-2022 and 2024p: DANE 202610074537 covers only the 2023p annex base 2015 (not extrapolated); PER 2015-2022: rule not stated in publications (INEI 4032), not extrapolated'})
    write_json(out/'datos/per_precision_conjunta.json',per)
    table,summary=mex_csi103.correspondence_and_contrast();write_csv(out/'datos/correspondencia_csi103.csv',table);write_json(out/'datos/contraste_csi103.json',summary)
    need(summary['all_equal'],'CSI_103 contrast mismatch: diagnose before consuming')
    write_json(out/'datos/d2_gate_report_candidato.json',{'schema_version':'NATIONAL_PREFLIGHT_3','precision_contract':pr.CONTRACT+' (candidate extension, not active)','complete_country_years':len(d2),'source_hash_checks':'pass','extraction_checks':'pass','evidence_references':'resolved_semantically_DB-02','identity_residual':'historical_ratio_definition','legacy_scientific_columns_retained':True,'accounting_identity':'exact_on_published_literals_except_CHL_identity_constructed',
        'precision_complete_vector':{v['vector_id']:v['status'] for v in validations},'four_country_admission':False,'source_admission':False,'production_activation':False})
    write_json(out/'datos/d6_proyecciones_2023.json',d6rows);write_json(out/'datos/conciliaciones.json',recon)
    write_csv(out/'review/elegibilidad.csv',matrix);write_csv(out/'review/casos_preregistrados.csv',joint)
    # D-03 corrected: MEX domains are kept ONLY as domains under a declared interpretation (never a strict pass).
    write_json(out/'datos/dominios_interpretacion_declarada_MEX.json',{'label':'dominios bajo interpretación declarada («redondeados a tres decimales» leído como redondeo al más cercano); no precisión institucional; no emitibles; sin rama de cálculo en esta versión',
        'status_by_vector':{v['vector_id']:v['status'] for v in validations if v['country_id']=='MEX'},
        'domains':{v['vector_id']:{'primitives':{p:x['domain'] for p,x in v['primitives'].items()},'derived':v['derived']} for v in validations if v['country_id']=='MEX'}})
    write_json(out/'datos/roles.json',[dict(country_id=c,family=f,year=y,roles=v) for (c,f,y),v in states.items()])
    old_accounts=[]
    for (c,y),v in old.items():
        lvl=identity_residual_level(v)
        old_accounts.append(dict(country_id=c,year=y,unit={'CHL':'CLP','COL':'COP','MEX':'MXN','PER':'PEN'}[c],multiplier='1',values={k:dec(x) for k,x in v.items()},source_vintage=oldmeta[(c,y)]['source_vintage'],source_snapshot_id=oldmeta[(c,y)]['source_snapshot_id'],identity_residual=display15(identity_residual_ratio(v)),identity_residual_level=dec(lvl),precision_reused=False,E2_comparability='not_demonstrated_by_common_SNA_label_alone',old_values_from_raw_not_shares=True))
    write_json(out/'datos/cuentas_antecesoras_reextraidas.json',old_accounts)
    revisions=[]
    for y in range(2015,2024):
        a=NationalAdapter('COL','D2',y,'COL_2024p');s=a.read();m=values(s)
        revisions.append({'id':f'COL_D2_{y}_2024p','source':a.cfg,**s,'identity_residual':display15(identity_residual_ratio(m)),'identity_residual_level':dec(identity_residual_level(m)),'comparability':'same_base2015_and_account_labels; candidate_review_required; primary_requires_own_revised_D6'})
    alt=NationalAdapter('COL','D6',2023,'COL_2024p');revisions.append({'id':'COL_D6_2023_2024p','source':alt.cfg,**alt.read()})
    pdf=NationalAdapter('PER','D2',2023,'PER_pdf_2023').read();need(values(pdf)==values(NationalAdapter('PER','D2').read()),'PER PDF differs from authenticated attachment')
    write_json(out/'datos/revisiones_completas_COL.json',revisions)
    write_json(out/'datos/comparabilidad_COL.json',[compare_col_revisions(y) for y in range(2015,2024)])
    orientation=[]
    for c in ('PER','MEX','COL'):
        s=NationalAdapter(c,'D6').read()
        if c=='PER':
            for sel,concept,val,coef in (('COU_2023!K376','D211 (V)','66351',1),('COU_2023!DL389','D29 (en N_PROD y P_NET)','6997',1),('CEI_2023!E24','D2-D3 (en P_NET)','82846',1),('COU_2023!DL390','D39 cero exacto (en N_PROD y P_NET)','0',-1)):
                orientation.append(dict(country_id=c,year=2023,concept=concept,selector=sel,raw_value=val,operation='multiply',coefficient=coef,oriented_value=dec(coef*F(val)),exact_zero_accredited=sel=='COU_2023!DL390',authority='PER_candidate_unapproved (D-01); net route D-02'))
            orientation.append(dict(country_id=c,year=2023,concept='D31 (contraste publicado, no consumido)',selector='COU_2023!J376',raw_value='-1505',operation='multiply',coefficient=-1,oriented_value='1505',exact_zero_accredited=False,authority='PER_candidate_unapproved (D-01)'))
            continue
        for m in s['members']:
            coefficient=-1 if m['concept'] in ('D31','D39') else 1
            orientation.append(dict(country_id=c,year=2023,concept=m['concept'],selector=m['selector'],raw_value=m['value_literal'],operation='multiply',coefficient=coefficient,oriented_value=dec(coefficient*F(m['value_literal'])),exact_zero_accredited=c=='PER' and m['concept']=='D39',authority='PER_candidate_unapproved' if c=='PER' else 'source_sign_technical_candidate_not_general_V2_admission'))
    write_json(out/'datos/orientacion_candidata.json',orientation)
    write_json(out/'review/resumen_ejecucion.json',{'D2_rows':len(d2),'bridge_rows':len(bridge),'D6_components':len(d6rows),'eligibility_rows':len(matrix),'preregistered_case_rows':len(joint),'precision_evidence_rows':len(prec_rows),'csi103_cells_compared':summary['cells_compared'],'PER_2023_publication_matches_attachment':True,'legacy_manifest_sha256':oldh,'model_executed':False,'production_activation':False})
    return snapshots,adapters,states
# Sin punto de entrada: construir_d2.py orquesta build(out) y el preflight CA2.
