"""Evaluación de casos preregistrados A1-E v2 sobre la matriz por país (sin modelo, sin admisión).

Cada caso exige exactamente los miembros de su country_set. Un miembro no elegible bloquea el caso con su
motivo; el caso nunca se reduce a un subconjunto. Una sensibilidad individual no exige PER.
"""
import json
from .nacionales import need
from .base import REGISTRY_FILE, CATALOG_DIR

READY = {'E0': 'candidate_strict_ready', 'E3': 'candidate_strict_ready', 'E1': 'candidate_conditional_ready', 'E2': 'candidate_conditional_ready'}


class CaseError(ValueError): pass


def load_registry():
    reg = json.loads(REGISTRY_FILE.read_bytes())
    cat = json.loads((CATALOG_DIR/'catalogo_contratos.json').read_bytes())
    embedded = cat['ca2'].get('case_registry')
    if embedded is not None: need(embedded == reg, 'catalog case_registry differs from the registry file')
    return reg


def check_membership(entry, declared, registry):
    """Declared members of a case must equal the preregistered set exactly (no additions, no silent removals)."""
    declared = sorted(declared)
    if declared != sorted(entry['country_set']):
        raise CaseError(f"{entry['preregistration_id']}: miembros {declared} distintos del conjunto preregistrado {entry['country_set']}")
    t, cs = entry['case_type'], entry['country_set']
    if t == 'aplicacion_principal' and cs != [registry['principal_country']]: raise CaseError('aplicación principal distinta de PER')
    if t == 'comparacion_internacional' and (len(cs) < 2 or registry['principal_country'] not in cs): raise CaseError('comparación sin PER o con menos de dos países')
    if t == 'sensibilidad_individual' and len(cs) != 1: raise CaseError('sensibilidad individual con más de un país')
    if set(cs) & set(registry['excluded_this_version']): raise CaseError('país excluido en esta versión')
    return True


def evaluate(matrix_rows, registry=None, col_comparability=None):
    registry = registry or load_registry()
    by = {(r['country_id'], int(r['year']), r['scenario']): r for r in matrix_rows}
    out = []
    for e in registry['entries']:
        check_membership(e, e['country_set'], registry)
        for scenario in e['scenarios']:
            for kind, years in e['claims'].items():
                for y in years:
                    members = []
                    for c in e['country_set']:
                        row = by[(c, y, scenario)]
                        ok = row['status'] == READY[scenario]
                        members.append((c, ok, row['blocking_reasons']))
                    extra = []
                    if e['case_type'] == 'sensibilidad_individual' and scenario == 'E2':
                        if (col_comparability or {}).get('verdict') != 'comparable_for_E2_individual': extra.append('comparability_review_not_passed')
                    blocked = [f'{c}:{why}' for c, ok, why in members if not ok] + extra
                    out.append(dict(preregistration_id=e['preregistration_id'], case_type=e['case_type'], scenario=scenario, claim_kind=kind, anchor_year=y,
                                    members=','.join(e['country_set']), status='candidate' if not blocked else 'blocked', blocking=';'.join(blocked),
                                    author_decisions=';'.join(e['author_decisions']), additional_conditions=';'.join(e.get('additional_conditions', [])),
                                    admission='not_admitted', production_activation=False))
    return out


def disposition(registry, country, year, scenario):
    """Where a country-year-scenario sits in this version: in which preregistered cases, or why not."""
    ids = [e['preregistration_id'] for e in registry['entries'] if country in e['country_set'] and scenario in e['scenarios']
           and any(year in ys for ys in e['claims'].values())]
    if ids: return 'incluido:' + '|'.join(ids)
    if country in registry['excluded_this_version']: return 'excluido_version'
    if scenario == 'E4': return 'no_identificado'
    return 'limitacion_fijada'
