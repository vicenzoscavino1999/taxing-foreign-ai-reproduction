"""TEST SUPPORT ONLY — synthetic fixtures for the precision validation.

Nothing produced here is evidence:
  * fixture() returns a Dossier FLAGGED synthetic (built from a copy of the authenticated content, then mutated);
  * validate_synthetic() marks every result synthetic=True and every status 'synthetic_*';
  * rules carry ca2x.SYNTHETIC_MARK, which ca2x.validate(..., emitted=True) rejects;
  * EvidenceAdapter, validate_vector, state and build() never call this module and accept no fixture.
These tools demonstrate representability and rejection paths; they cannot produce a usable receipt.
"""
from . import precision as pr
from .nacionales import NationalAdapter, read_source

def fixture(mutate=None):
    """Synthetic Dossier: copy of the authenticated content, optionally mutated, rebuilt immutable and flagged."""
    base=pr.Dossier.load();content=pr.thaw(base._content)
    if mutate is not None:mutate(content)
    return pr.Dossier._build(content,'SYNTHETIC-NOT-EVIDENCE:'+base.seal,True)

def mutable_cells(country,family,year,revision='selected'):
    """Plain (mutable) copy of the authenticated cells, for synthetic domain-failure cases."""
    a=NationalAdapter(country,family,year,revision);return pr.thaw(pr._cells(a,read_source(a.key)[1]))

def validate_synthetic(country,family,year,revision='selected',*,dossier=None,cells=None):
    """Run the same validation logic with a synthetic dossier and/or synthetic cells; results are marked."""
    if dossier is None and cells is None:raise ValueError('nothing synthetic requested: use precision.validate_vector')
    a=NationalAdapter(country,family,year,revision)
    d=dossier if dossier is not None else pr.Dossier.load()
    return pr._validate(a,d,raw=None,cells=cells,synthetic=True)
