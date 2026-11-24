"""Subpaso 1.4: revisión de comparabilidad de las revisiones colombianas 2023p y 2024p (base 2015).

Solo lee los snapshots autenticados del registro. Cada comprobación se hace sobre bytes; el veredicto es
'comparable_for_E2_individual' solo si todas pasan. Un conjunto observado de dos revisiones no es un intervalo
de confianza ni una garantía sobre revisiones futuras.
"""
from fractions import Fraction as F
import json
from .nacionales import NationalAdapter, read_source, source_config, xlsx_cells, values, pair_check, projected, roles, dec, need, write_json

REVISIONS = (('2023p', 'COL_2023', 'selected'), ('2024p', 'COL_2024p', 'COL_2024p'))
YEARS = tuple(range(2015, 2024))
LABELS = {'K29': 'PRODUCTO INTERNO BRUTO', 'J36': 'D.1', 'J47': 'B.2b', 'J48': 'B.3b', 'J62': 'D.2', 'J63': 'D.21', 'J64': 'D211',
          'J68': 'D.29', 'J69': 'D.3', 'J70': 'D.31', 'J71': 'D.39'}
HEADER = {'A4': 'Cuentas Económicas Integradas - CEI', 'A6': 'Valores a precios corrientes', 'A7': 'En miles de millones de pesos', 'A8': 'Base 2015'}


def txt(c, sh, k): return str((c[sh].get(k) or {}).get('value') or '').strip()
def num(c, sh, k):
    v = (c[sh].get(k) or {}).get('value'); need(v not in (None, ''), f'missing {sh}!{k}'); return F(str(v))


def review():
    checks = []
    def check(cid, ok, detail): checks.append(dict(id=cid, result=bool(ok), detail=detail))
    cells, cfgs = {}, {}
    for lab, key, _ in REVISIONS:
        cfg, raw = read_source(key); cells[lab] = xlsx_cells(raw); cfgs[lab] = cfg
    a, b = cfgs['2023p'], cfgs['2024p']
    check('C01_distinct_revisions', a['sha256'] != b['sha256'] and a['vintage'] != b['vintage'],
          f"snapshots {a['sha256'][:12]} / {b['sha256'][:12]}; vintages {a['vintage']} / {b['vintage']}")
    check('C02_year_status_labels', txt(cells['2023p'], '2023', 'A9') == '2023p' and txt(cells['2024p'], '2023', 'A9') == '2023',
          'hoja 2023: «2023p» en la edición 2023p y «2023» en la edición 2024p (cambio de estado de la cifra)')
    overlap = [y for y in YEARS if str(y) in cells['2023p'] and str(y) in cells['2024p']]
    check('C03_temporal_scope', overlap == list(YEARS),
          f"hojas 2023p: {sorted(k for k in cells['2023p'] if k.isdigit())}; 2024p: {sorted(k for k in cells['2024p'] if k.isdigit())}; preregistro 2015-2023")
    hdr = all(txt(cells[lab], str(y), k) == v for lab in cells for y in YEARS for k, v in HEADER.items())
    check('C04_base_unit_valuation', hdr, 'A4/A6/A7/A8 iguales en todas las hojas 2015-2023 de ambas ediciones: CEI, precios corrientes, miles de millones de pesos, base 2015')
    lab_ok = all(txt(cells[lab], str(y), k) == v for lab in cells for y in YEARS for k, v in LABELS.items())
    check('C05_concepts_and_selectors', lab_ok, 'etiquetas SCN en las mismas celdas (K29, J36, J47, J48, J62-J64, J68-J71) en todas las hojas de ambas ediciones')
    cov = all(num(cells[lab], str(y), 'A36') == num(cells[lab], str(y), 'D36') for lab in cells for y in YEARS)
    check('C06_coverage_domestic', cov, 'remuneración doméstica A36 = D36 (S1 economía total) en todas las hojas; PIB publicado directamente en A29')
    orient = []
    for lab in cells:
        for y in YEARS:
            c = cells[lab]; sh = str(y)
            orient.append(num(c, sh, 'Q62') == num(c, sh, 'Q63') + num(c, sh, 'Q68')
                          and num(c, sh, 'Q69') == num(c, sh, 'Q70') + num(c, sh, 'Q71')
                          and num(c, sh, 'Q70') <= 0 and num(c, sh, 'Q71') <= 0)
    check('C07_orientation_in_file', all(orient), 'en cada hoja: D.2 (Q62) = D.21 + D.29 y D.3 (Q69) = D.31 + D.39, con subvenciones almacenadas ≤ 0 (convención signed_negative_tax)')
    vectors, ident, recon, changes = {}, [], [], []
    for lab, key, rev in REVISIONS:
        for y in YEARS:
            s = NationalAdapter('COL', 'D2', y, rev).read(); m = values(s); vectors[(lab, 'D2', y)] = m
            ident.append(m['PIB'] == m['COE'] + m['GOS'] + m['MI'] + m['TAX_NET'])
            c = cells[lab]; ident.append(m['TAX_NET'] == num(c, str(y), 'Q62') + num(c, str(y), 'Q69'))
        s6 = NationalAdapter('COL', 'D6', 2023, rev).read(); vectors[(lab, 'D6', 2023)] = values(s6)
        d2 = NationalAdapter('COL', 'D2', 2023, rev).read(); p = pair_check(d2, s6)
        recon.append(p['gdp_residual'] == '0' and p['tax_residual'] == '0')
    check('C08_complete_vectors', all(len(vectors[(lab, 'D2', y)]) == 5 for lab in cells for y in YEARS) and all(len(vectors[(lab, 'D6', 2023)]) == 6 for lab in cells),
          'D2 completo (PIB, COE, GOS, MI, TAX_NET) en 9 años y D6 2023 completo (PIB, D21, D211, D29, D31, D39) en ambas ediciones')
    check('C09_identity_and_denominators', all(ident), 'PIB = COE + GOS + MI + TAX_NET exacta y TAX_NET = D.2 + D.3 publicados, en cada año y edición; cada cociente usa el PIB de su propia edición')
    check('C10_D2_D6_same_revision_pairing', all(recon), 'en 2023, D6 comparte PIB y total tributario con el D2 de la misma edición (sin mezclar ediciones)')
    rl = [roles(NationalAdapter('COL', f, y, rev), NationalAdapter('COL', f, y, rev).read()) for _, _, rev in REVISIONS for f, ys in (('D2', YEARS), ('D6', (2023,))) for y in ys]
    check('C11_common_roles', all(all(r[k] == 'pass' for k in ('snapshot', 'provenance', 'concept', 'coverage', 'orientation', 'reconciliation')) for r in rl),
          'los seis roles comunes pasan en los 20 vectores (18 D2 + 2 D6)')
    for y in YEARS:
        for k in ('PIB', 'COE', 'GOS', 'MI', 'TAX_NET'):
            x, z = vectors[('2023p', 'D2', y)][k], vectors[('2024p', 'D2', y)][k]
            if x != z: changes.append(dict(family='D2', year=y, concept=k, value_2023p=dec(x), value_2024p=dec(z), delta=dec(z-x)))
    for k in ('PIB', 'D21', 'D211', 'D29', 'D31', 'D39'):
        x, z = vectors[('2023p', 'D6', 2023)][k], vectors[('2024p', 'D6', 2023)][k]
        if x != z: changes.append(dict(family='D6', year=2023, concept=k, value_2023p=dec(x), value_2024p=dec(z), delta=dec(z-x)))
    d6_unchanged = [k for k in ('D21', 'D211', 'D29', 'D31', 'D39') if vectors[('2023p', 'D6', 2023)][k] == vectors[('2024p', 'D6', 2023)][k]]
    check('C12_revision_is_substantive', len(changes) > 0, f'{len(changes)} valores cambian entre ediciones; los componentes tributarios D6 2023 sin cambio: {d6_unchanged}')
    comparable = all(c['result'] for c in checks)
    shares = {}
    for lab in cells:
        m6 = vectors[(lab, 'D6', 2023)]; s6 = NationalAdapter('COL', 'D6', 2023, dict((l, r) for l, _, r in REVISIONS)[lab]).read()
        shares[lab] = {k: str(v/m6['PIB']) for k, v in projected(s6).items()}
        shares[lab]['COE_2023'] = str(vectors[(lab, 'D2', 2023)]['COE']/vectors[(lab, 'D2', 2023)]['PIB'])
    return {'verdict': 'comparable_for_E2_individual' if comparable else 'not_comparable_E2_not_performed',
            'revisions': {lab: {'snapshot_sha256': cfgs[lab]['sha256'], 'vintage': cfgs[lab]['vintage'], 'source_id': key,
                                'provenance': cfgs[lab].get('official_url') or ('copia local autenticada: ' + str(cfgs[lab].get('status')))} for lab, key, _ in REVISIONS},
            'checks': checks, 'value_changes': changes, 'd6_2023_tax_components_unchanged': d6_unchanged, 'exact_shares_2023': shares,
            'unchanged_years': [y for y in YEARS if not any(ch['year'] == y for ch in changes)],
            'preregistered_design': {'primary_2023': 'cada edición con su propio D2 y D6 2023 (comparten PIB y total dentro de la edición)',
                                     'historical_2015_2022': 'no se preregistra: los vectores D2 2015-2022 son idénticos en ambas ediciones, de modo que un E2 histórico no aportaría variación observada',
                                     'orientation_2024p_D6': 'demostrada en el archivo (C07); la autoridad firmada V1/V2 está ligada al snapshot 2023p: su extensión a 2024p es la decisión D-09'},
            'limits': ['conjunto observado de dos ediciones oficiales; no es un intervalo de confianza ni una distribución',
                       'no garantiza el signo ni la magnitud de revisiones futuras',
                       'no hay precisión acreditada: E2 es condicional (no estricto)',
                       'la edición 2023p proviene de una copia local autenticada por hash (sin URL oficial registrada); la 2024p de la URL oficial del DANE'],
            'model_executed': False}


