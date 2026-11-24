"""DB-02 evidence registry v2: claims, snapshot bindings and a semantic resolver.

A reference is valid only if the claim exists AND its code/status fit the use,
its scope matches country, year and revision, its binding names the same
snapshot, and every selector consumed is inside its scope. Matching strings is
not enough.

Incorporado en 1.5: sin lectura de mensajes institucionales privados (el expediente sellado basta); las
afirmaciones y vínculos se leen de la recepción versionada.
"""
from pathlib import Path
import hashlib, json, re
from .base import RECEPTION as A
CLAIM_FIELDS=('claim_code','claim_summary','evidence_id','evidence_status','receipt_id','scope_cell_or_range','scope_country','scope_sheet','scope_vintage','scope_year','verified_at')
RECEIPT_FIELDS=('attachment_bytes','attachment_media_type','attachment_role','attachment_sha256','claim_scope','institution_id','institutional_reference','message_sha256','receipt_id','received_at','related_publication_url','response_date','source_evidence_id','verification_status')
BINDING_FIELDS=('binding_basis','evidence_id','scope_snapshot_sha256','scope_source_id')
# Which claims may support which use. Institutional facts never stand in for extraction and vice versa.
ROLE_POLICY={
    'account':{'codes':{'account_extraction'},'statuses':{'technical_extraction_authenticated'}},
    'precision':{'codes':{'publication_rule'},'statuses':{'institutional_fact','institutional_fact_series_scope_file_bound_by_metadata'}},
    'exact_zero':{'codes':{'exact_zero'},'statuses':{'institutional_fact'}},
    'concept_cell':{'codes':{'concept_cell_mapping','primitive_mapping'},'statuses':{'technical_correspondence_verified_in_file','technical_interpretation_pending_review'}},
}
class EvidenceError(ValueError):pass
class DossierUnavailable(EvidenceError):
    """Evidence absent (not altered): consumers must return a non-approving state."""
def need(test,msg):
    if not test:raise EvidenceError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()

def load_claims(path=None):
    return load_claims_bytes((path or A/'evidencia/afirmaciones_db02.json').read_bytes())
def load_claims_bytes(raw):
    """Parse claims from bytes already authenticated by the caller (no second read of the file)."""
    rows=json.loads(raw.decode('utf-8'))
    out={}
    for r in rows:
        need(tuple(sorted(r))==CLAIM_FIELDS,'DB-02 claim fields not exact: '+str(r.get('evidence_id')))
        need(r['evidence_id'] not in out,'duplicate evidence_id '+r['evidence_id'])
        out[r['evidence_id']]=r
    return out
def load_bindings(path=None):
    return load_bindings_bytes((path or A/'evidencia/vinculos_afirmacion_snapshot.json').read_bytes())
def load_bindings_bytes(raw):
    rows=json.loads(raw.decode('utf-8'))
    out={}
    for r in rows:
        need(tuple(sorted(r))==BINDING_FIELDS,'binding fields not exact')
        need(r['evidence_id'] not in out,'duplicate binding '+r['evidence_id'])
        out[r['evidence_id']]=r
    return out
def scope_selectors(claim):
    sheet=claim['scope_sheet'];out=set()
    for s in claim['scope_cell_or_range']:
        out.add(s if (sheet is None or '!' in s or s.startswith('PDF:')) else f'{sheet}!{s}')
    return out
def primitive_selectors(member_selector):
    """'Tabulado!R46:1;Tabulado!R53:1' -> {'Tabulado!R46','Tabulado!R53'}; semantic-zero and PDF selectors kept whole."""
    if member_selector.startswith('PDF:'):return {member_selector}
    out=set()
    for part in member_selector.split(';'):
        cell=part.split(':')[0];need(re.fullmatch(r'[^!]+![A-Z]+[0-9]+',cell),'unparseable selector '+part);out.add(cell)
    return out

def resolve(evidence_id,*,role,country,year,vintage,snapshot,selectors,claims=None,bindings=None):
    """Return the claim if it semantically supports this use; raise EvidenceError otherwise."""
    claims=claims if claims is not None else load_claims();bindings=bindings if bindings is not None else load_bindings()
    need(role in ROLE_POLICY,'unknown evidence role '+str(role))
    need(isinstance(evidence_id,str) and evidence_id in claims,'evidence id not found: '+str(evidence_id))
    c=claims[evidence_id];pol=ROLE_POLICY[role]
    need(c['claim_code'] in pol['codes'],f'claim {evidence_id} ({c["claim_code"]}) cannot support {role}')
    need(c['evidence_status'] in pol['statuses'],f'claim {evidence_id} status {c["evidence_status"]} not usable for {role}')
    need(c['scope_country']==country,f'evidence {evidence_id} country {c["scope_country"]} != {country}')
    need(c['scope_year']==year,f'evidence {evidence_id} year {c["scope_year"]} != {year}')
    need(c['scope_vintage']==vintage,f'evidence {evidence_id} revision {c["scope_vintage"]} != {vintage}')
    b=bindings.get(evidence_id);need(b is not None,'evidence '+evidence_id+' has no snapshot binding')
    need(b['scope_snapshot_sha256']==snapshot,f'evidence {evidence_id} bound to another snapshot')
    wanted=set(selectors);need(wanted,'no selectors to resolve')
    need(wanted<=scope_selectors(c),f'selector outside evidence {evidence_id}: {sorted(wanted-scope_selectors(c))}')
    return c
