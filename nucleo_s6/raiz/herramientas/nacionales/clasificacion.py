"""Classification of blocking reasons (finding 3).

Each reason gets exactly one category with its justification and what would resolve it.
A reclassification never removes a blocker: the row status is computed from the reasons,
the categories only say WHO/WHAT can lift each one.
"""
EXTERNAL='external_evidence_indispensable'
INTERNAL='internal_technical_work'
REVIEW='review_or_approval_pending'
NO_DOMAIN='scenario_without_authorized_domain'
DIAGNOSIS='diagnosis_insufficient_for_external_dependency'
LIMIT='limitation_fixed_this_version'  # consolidation 1.4: fixed by the author's decision to close with the available evidence
CATEGORIES=(EXTERNAL,INTERNAL,REVIEW,NO_DOMAIN,DIAGNOSIS,LIMIT)

def _r(category,detail,resolves_by,institution=None,consult=None):
    return {'category':category,'detail':detail,'resolves_by':resolves_by,'institution':institution,'consultation_ref':consult}

def classify(country,year,scenario,reason):
    fam,_,rest=reason.partition(':')
    if reason=='measurement_domain_not_supported':
        return _r(NO_DOMAIN,'E4 keeps measurement_domain null: no defensible domain for unknown statistical errors','a future pre-registered domain with its own justification and review; not an institutional reply')
    if reason=='E2:complete_comparable_revisions_missing':
        return _r(DIAGNOSIS,'no complete comparable prior official revision of the same closure has been identified; UN/AMA legacy levels do not prove comparability',
                  'internal: review the bridge and search for a complete earlier official release (same concepts, unit, base, coverage); only then decide whether a request is needed')
    if reason.endswith(':precision:declared_interpretation'):
        return _r(LIMIT,'publication domain rests on an interpretation declared by the author ("redondeados a tres decimales" read as nearest), not on an institutional rule; an approval by the author does not turn it into an institutional confirmation (D-03)',
                  'only an INEGI statement of the rounding mode would make it institutional; not awaited in this version (MEX participates by E1; strict sensitivity is a future extension)','INEGI','INEGI-modo-redondeo-opcional')
    if reason.endswith(':precision:candidate_pending_review'):
        return _r(REVIEW,'domain constructed, but applying the concept-level D21 rule to the stored primitives F376/I376 is a technical interpretation pending review','reviewer decision on PER_D21_MAPPING; PER authority remains candidate_unapproved')
    if reason.endswith(':precision:fail'):
        return _r(INTERNAL,'publication-domain validation failed for evidence that exists (increment, identity, joint D2/D6 or cross-check contradicted)','diagnose the contradicted check; never widen a domain to obtain PASS')
    # Kept for historical rows only: CA2-2X now represents mixed exact/rounded vectors, so this reason is no longer emitted.
    if reason.endswith(':precision_contract:mixed_exact_rounding'):
        return _r(INTERNAL,'CA2-2 precision_rule allows one kind per receipt; the PER D6 vector mixes an exact zero (DL390) with rounded cells','prepare and test an explicit contract extension (not applied here)')
    role=rest.split(':')[0]
    if country=='CHL' and role in ('coverage','reconciliation'):
        return _r(EXTERNAL,'binding of folio BCCHGCRFAO18898 to the pinned CEI/COU files, independent published GDP of the same closure and documented explanation of the CEI-COU residuals',
                  'BCCh reply scoped to the exact files; recovered request alone does not prove the association','BCCh','BCCh')
    if role=='precision':
        if country=='CHL':return _r(EXTERNAL,'"sexto decimal" does not state rounding, truncation, unit or scope','BCCh rule for the stored values of the pinned files','BCCh','BCCh')
        if country=='COL':return _r(EXTERNAL,'no DANE technical reply on the publication rule per concept/sheet/year; D31=0 is not an accredited exact zero','DANE reply to radicado 202620018777 / complement','DANE','DANE')
        if country=='PER' and year<2023:
            return _r(EXTERNAL,'INEI 4032: rounding rules are not stated in the 2015-2022 publications; this neither confirms nor excludes a rule, and the 2023 answer is not extrapolated',
                      'only INEI can state the rule for the 2015-2022 values of the 1950-2024 edition; optional, affects only strict historical sensitivity','INEI','INEI-historica-opcional')
    raise ValueError('unclassified blocking reason: '+reason)

def classify_row(country,year,scenario,reasons):
    items=[{'reason':r,**classify(country,year,scenario,r)} for r in reasons]
    flags={c:any(i['category']==c for i in items) for c in CATEGORIES}
    return items,flags
