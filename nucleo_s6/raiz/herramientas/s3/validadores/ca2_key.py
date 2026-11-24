"""Clave candidata para contextos condicionales E1/E2; no cambia macro-v2.

Enmienda A1-E v2 (candidata): la clave pasa a macro-ca2-v2 e incluye preregistration_id, case_type y
country_set del caso, de modo que una aplicación principal, una comparación internacional y una sensibilidad
individual con las mismas entradas de un país nunca comparten clave."""
from .core import require, strict_json, sha, H


def conditional_key(raw, expected_hash, validator, case_id, country, *, common_values_sha256, eta_w_block, protocol_sha256, technical):
    require(sha(raw)==expected_hash,'bundle CA2 externo incorrecto')
    tables=strict_json(raw,canonical_file=True)
    receipt=validator.validate(tables)
    cases=[c for c in tables['ca2_cases'] if c['case_id']==case_id]
    require(len(cases)==1 and cases[0]['scenario'] in ('E1','E2'),'rama condicional E1/E2 requerida')
    require(country in cases[0]['country_set'],'país fuera del conjunto preregistrado del caso')
    rows=[r for r in tables['ca2_inputs'] if r['case_id']==case_id and r['country_id']==country]
    require(len(rows)==1,'contexto de país ausente/ambiguo')
    for value in [expected_hash,common_values_sha256,protocol_sha256]:validator.c.scalar(value,'sha')
    validator.c.scalar(eta_w_block,'block')
    validator.c.key_type(technical,'technical')
    row=rows[0];vectors={v['vector_id']:v for v in tables['ca2_vectors']}
    payload={'kind':'macro-ca2-v2','bundle_sha256':expected_hash,'case_id':case_id,'scenario':cases[0]['scenario'],
             'preregistration_id':cases[0]['preregistration_id'],'case_type':cases[0]['case_type'],'country_set':cases[0]['country_set'],
             'country_id':country,'anchor_year':row['anchor_year'],'d2_vector_sha256':vectors[row['d2_vector_id']]['vector_sha256'],
             'd6_vector_sha256':vectors[row['d6_vector_id']]['vector_sha256'],'context_sha256':row['context_sha256'],
             'common_values_sha256':common_values_sha256,'eta_w_block':eta_w_block,'protocol_sha256':protocol_sha256,'technical':technical}
    return {'payload':payload,'sha256':H(payload),'admissibility':receipt['case_admissibility'][case_id],
            'numerical_validation':False,'production_activation':False}
