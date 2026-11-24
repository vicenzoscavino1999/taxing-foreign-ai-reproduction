"""CA2-2X-PRECISION-2 — extension of the CA2-2 precision_rule, adopted in 1.5 (A-01, author authorization
2026-09-28) next to CA2-2 with explicit dispatch by contract_version in validadores/ca2.py.

Integrated copy of the reference implementation codigo/ca2x.py of the approved delivery (inventory a88b683a...):
semantics unchanged; the only edit is the package-relative import of institucional.

CA2-2 allows one kind per receipt and one rounding unit per member selector, so a member summing several
published cells reads as a single rounded cell and a vector mixing an exact zero with rounded cells cannot
be expressed. CA2-2X keeps the receipt envelope (facts, outcome, precision_rule, common_conflicts) and
changes only the precision_rule payload, marked by contract_version.

Version 2 (2026-09-27, revision R3) binds the rule to the AUTHENTICATED projection of the vector:
  vector_binding  {snapshot_sha256, projection_sha256} where the projection is the list of
                  (concept, member selector) read from the authenticated snapshot bytes;
  consumers must pass that projection to validate(); every selector rule's concept must match it and the
  shared denominator must be the UNIQUE 'PIB' member of that projection (a label declared by the rule
  itself is not evidence).
Version 1 (2026-09-27 candidate, never active) is not accepted as v2 and is not re-read: it had no binding
to the authenticated projection. Rules without contract_version are CA2-2 and keep their CA2-2 meaning.
The CA2-2 branch of the validator rejects CA2-2X payloads (different field set): no silent acceptance; only the
explicit contract_version dispatch reaches validate() below.
Synthetic rules (test support) carry SYNTHETIC_MARK and are never accepted as emitted evidence.
"""
import hashlib, json, re
from fractions import Fraction as F
from .institucional import affine_domain, literal
CONTRACT='CA2-2X-PRECISION-2'
SYNTHETIC_MARK='+SYNTHETIC-NOT-EVIDENCE'
SUPERSEDED={'CA2-2X-PRECISION-1':'candidate of 2026-09-27, never active; no binding to the authenticated projection, so a wrong shared denominator could pass (review finding R3); not accepted as v2 and not re-read'}
RULE_FIELDS=('contract_version','kind','primitives','selector_rules','shared_denominator','vector_binding')
PRIMITIVE_FIELDS=('basis','correspondence','domain','evidence_ids','kind','primitive','rounding_unit','rule_id','status','value')
SELECTOR_FIELDS=('concept','member_domain','rule_locator','selector','terms')
KINDS=('rounding','exact')
class ContractError(ValueError):pass
def need(test,msg):
    if not test:raise ContractError(msg)
def dec(x):return str(literal(F(x)))
def canonical_positive(t):
    need(isinstance(t,str) and re.fullmatch(r'(0|[1-9]\d*)(\.\d*[1-9])?',t) and F(t)>0,'rounding unit must be a canonical positive decimal')
def parse_member(selector):
    """Member selector -> [(primitive, coefficient, flag)]. PDF kept whole.

    Each ';' part is either 'cell:coefficient' or 'cell:semantic_zero:<sha256>[:coefficient]' (coefficient 1 by
    default). A documented semantic zero may therefore appear inside a composite member (PER net route, D-02),
    with the sign of the stored convention; its value is zero and its domain comes from the exact-zero rule."""
    if selector.startswith('PDF:'):return [(selector,F(1),'pdf')]
    out=[]
    for part in selector.split(';'):
        z=re.fullmatch(r'([^!;:]+![A-Z]+\d+):semantic_zero:([0-9a-f]{64})(?::(-?\d+))?',part)
        if z:
            out.append((z.group(1),F(z.group(3) or 1),'semantic_zero'));continue
        m=re.fullmatch(r'([^!;:]+![A-Z]+\d+):(-?\d+)',part);need(m,'unparseable member selector part '+part)
        out.append((m.group(1),F(m.group(2)),'cell'))
    need(len({p for p,_,_ in out})==len(out),'repeated primitive inside one member selector')
    return out
def projection_digest(projection):
    """SHA-256 of the canonical projection [[concept, selector], ...] in facts.selectors order."""
    rows=[[c,s] for c,s in projection]
    return hashlib.sha256(json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()
def _dom(d):
    need(isinstance(d,(list,tuple)) and len(d)==2,'domain must be [low, high]');a,b=F(d[0]),F(d[1]);need(a<=b,'inverted domain');return a,b

def validate(rule,projection,*,cells=None,snapshot_sha256=None,emitted=True,accept_synthetic=False):
    """projection: [(concept, selector)] read from the AUTHENTICATED snapshot, ordered like facts.selectors.
    Checks exact fields; binding to that projection (and snapshot when given); per-primitive domains recomputed
    from value and unit (and stored cells when given); explicit terms equal to each member selector; member
    domains recomputed with shared primitives grouped; the shared denominator is the unique PIB member.
    Emitted rules must be all 'ok' and never synthetic."""
    need(isinstance(rule,dict),'rule must be a mapping')
    cv=rule.get('contract_version')
    need(cv not in SUPERSEDED,'superseded CA2-2X version, not accepted: '+str(cv))
    synthetic=isinstance(cv,str) and cv.endswith(SYNTHETIC_MARK)
    need(not synthetic or (accept_synthetic and not emitted),'synthetic rule is not evidence and cannot be emitted')
    need(cv==CONTRACT+(SYNTHETIC_MARK if synthetic else ''),'not a CA2-2X-PRECISION-2 rule')
    need(tuple(sorted(rule))==tuple(sorted(RULE_FIELDS)),'CA2-2X rule fields not exact')
    projection=[(c,s) for c,s in projection];selectors=[s for _,s in projection]
    need(len(set(selectors))==len(selectors),'duplicate selector in the authenticated projection')
    vb=rule['vector_binding'];need(isinstance(vb,dict) and set(vb)=={'snapshot_sha256','projection_sha256'},'vector binding fields')
    need(vb['projection_sha256']==projection_digest(projection),'rule is not bound to the authenticated projection')
    if snapshot_sha256 is not None:need(vb['snapshot_sha256']==snapshot_sha256,'rule bound to another snapshot')
    prims={};kinds=set()
    for p in rule['primitives']:
        need(isinstance(p,dict) and tuple(sorted(p))==PRIMITIVE_FIELDS,'CA2-2X primitive fields not exact')
        need(p['primitive'] not in prims,'duplicate primitive '+p['primitive']);need(p['kind'] in KINDS,'primitive kind')
        need(isinstance(p['evidence_ids'],(list,tuple)) and p['evidence_ids'],'primitive without evidence '+p['primitive'])
        need(p['status'] in ('ok','pending_review'),'primitive status');need(not emitted or p['status']=='ok','emitted rule contains a primitive pending review')
        lo,hi=_dom(p['domain'])
        if p['kind']=='rounding':
            canonical_positive(p['rounding_unit']);v=F(p['value']);u=F(p['rounding_unit'])
            need((v/u).denominator==1,'value finer than its declared rounding unit '+p['primitive'])
            need((lo,hi)==(v-u/2,v+u/2),'rounding domain is not the declared closed envelope '+p['primitive'])
        else:
            need(p['rounding_unit'] is None and p['value']=='0' and (lo,hi)==(0,0),'exact primitive must be a documented zero with [0,0]')
        if cells is not None:
            sh,c=p['primitive'].split('!');cell=cells.get(sh,{}).get(c)
            if p['kind']=='exact':need(cell is None or cell.get('value') in (None,'') or F(cell['value'])==0,'exact zero contradicted by stored cell '+p['primitive'])
            else:need(cell is not None and cell.get('formula') is None and F(cell['value'])==F(p['value']),'stored value differs '+p['primitive'])
        prims[p['primitive']]=(lo,hi);kinds.add(p['kind'])
    need(prims,'rule without primitives')
    need(rule['kind']==('mixed' if len(kinds)>1 else next(iter(kinds))),'rule kind does not match its primitives')
    need([s['selector'] for s in rule['selector_rules']]==selectors,'CA2-2X rule does not cover exactly the vector selectors')
    concept_of=dict((s,c) for c,s in projection);used=set()
    for s in rule['selector_rules']:
        need(isinstance(s,dict) and tuple(sorted(s))==SELECTOR_FIELDS,'CA2-2X selector rule fields not exact')
        need(s['concept']==concept_of[s['selector']],'selector rule concept contradicts the authenticated projection: '+s['selector'])
        expected=[[p,str(k)] for p,k,_ in parse_member(s['selector'])]
        need([list(t) for t in s['terms']]==expected,'terms differ from the member selector: a composite cannot be a single cell')
        for p,_ in s['terms']:need(p in prims,'term without primitive '+p);used.add(p)
        need(_dom(s['member_domain'])==affine_domain([(p,k) for p,k in s['terms']],prims),'member domain not propagated from its primitives '+s['selector'])
    need(used==set(prims),'primitives not used by any member')
    pib=[s for c,s in projection if c=='PIB'];need(len(pib)==1,'the authenticated projection must contain exactly one PIB member (absent or ambiguous)')
    den=rule['shared_denominator'];need(isinstance(den,dict) and set(den)=={'concept','member_selector','primitives'},'shared denominator fields')
    need(den['concept']=='PIB','shared denominator concept must be PIB')
    need(den['member_selector']==pib[0],'shared denominator is not the PIB member of the authenticated projection')
    need(list(den['primitives'])==[p for p,_,_ in parse_member(pib[0])],'shared denominator primitives are not the PIB member terms')
    return {'contract':CONTRACT,'kind':rule['kind'],'primitives':len(prims),'members':len(rule['selector_rules']),'synthetic':synthetic}

def interpret(rule,projection=None,**kw):
    """Historical receipts keep their contract; nothing is re-read under a newer meaning."""
    if rule is None:return None
    cv=rule.get('contract_version')
    if cv is None:
        return {'contract':'CA2-2','kind':rule.get('kind'),'per_primitive_semantics':False,
                'note':'legacy single-kind rule: each selector rule covers the whole member; composite members are not given primitive domains'}
    if cv in SUPERSEDED:return {'contract':cv,'status':'superseded_candidate_not_accepted','note':SUPERSEDED[cv]}
    if isinstance(cv,str) and cv.endswith(SYNTHETIC_MARK):return {'contract':cv,'synthetic':True,'usable_as_evidence':False}
    if projection is None:return {'contract':cv,'status':'requires_authenticated_projection_to_validate'}
    return validate(rule,projection,emitted=False,**kw)
