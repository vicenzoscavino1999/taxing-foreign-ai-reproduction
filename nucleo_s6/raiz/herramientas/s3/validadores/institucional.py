"""Lectores candidatos de bytes fijados; no adquisición, admisión ni productor D6."""
from fractions import Fraction
from io import BytesIO
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from .core import require, sha, decimal, H, canon, strict_json

PER = 'dca6ebf37c2c0865a7d579cf73ade2358a459ea51441e2a2ee9d6b4412f158e3'
MEX = '077a64fe4272a7163f47fbeb3835428838f89460537480222b7f5d0d5abbf6f6'
COL = 'fa799bfe8e087ba1921a7c9623490748d0b24985fdf14acb0e53e155c125da5c'
CHL_COU = '4fa4dc3da102ec26a07d2215d0f4fabea2be1a348077f6c5aee2b805d69ed058'
CHL_CEI = '84f025caad43d5df78e5197bf038bb8e790aa3e4e0beb4972503771f11da0460'
PER_MAIL = '90994661e8f21fbaa189067472fc8b3b23be5f79540fb8057476ea38775a0137'
CHL_MAIL = '6412f38aa7be728b286d74871d88b6674c523270277ef6ffe8df24e60f851fb1'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def rational(value):
    require(type(value) in (str, int), 'literal decimal exacto requerido')
    return Fraction(decimal(value))


def literal(value):
    """Serializa racional decimal finito sin precisión de contexto Decimal."""
    value = Fraction(value)
    n, d, power = value.numerator, value.denominator, 0
    while d % 2 == 0: d //= 2
    while d % 5 == 0: d //= 5
    require(d == 1, 'racional no decimal finito')
    scale = 1
    while scale % value.denominator:
        scale *= 10; power += 1
    integer = abs(n) * (scale // value.denominator)
    s = str(integer).zfill(power + 1)
    if power: s = s[:-power] + '.' + s[-power:]
    return decimal(('-' if n < 0 else '') + s)


def xlsx_cells(raw):
    with ZipFile(BytesIO(raw)) as z:
        shared = []
        if 'xl/sharedStrings.xml' in z.namelist():
            shared = [''.join(t.text or '' for t in si.findall('.//s:t', NS))
                      for si in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        rels = {r.attrib['Id']: r.attrib['Target'] for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        result = {}
        for sheet in ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet', NS):
            target = rels[sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
            target = target.lstrip('/') if target.startswith('/') else 'xl/' + target
            cells = {}
            for c in ET.fromstring(z.read(target)).findall('.//s:sheetData/s:row/s:c', NS):
                v, f = c.find('s:v', NS), c.find('s:f', NS)
                value = v.text if v is not None else None
                if c.get('t') == 's' and value is not None: value = shared[int(value)]
                if c.get('t') == 'inlineStr': value = ''.join(t.text or '' for t in c.findall('.//s:t', NS))
                cells[c.attrib['r']] = {'value': value, 'formula': f.text if f is not None else None, 'type': c.get('t', 'n')}
            result[sheet.attrib['name']] = cells
        return result


def source_claims(raw):
    """Curación explícita del texto exacto autenticado; no confía en flags del JSON."""
    digest = sha(raw)
    if digest == PER_MAIL:
        return {'source_sha256': digest, 'country_id': 'PER', 'year': 2023,
                'snapshot_sha256': PER, 'precision': 'nearest_unit',
                'precision_concepts': ['PIB', 'D211', 'D21', 'D31', 'D29', 'D39'],
                'zero_exact': ['COU_2023!DL390'], 'accrual': ['D211', 'D21', 'D31', 'D29'],
                'tie_rule': None, 'subject_reference': '3916', 'body_reference': '3918'}
    if digest == CHL_MAIL:
        return {'source_sha256': digest, 'country_id': 'CHL', 'year': None,
                'snapshot_sha256': None, 'precision': 'sixth_decimal_unspecified_rule',
                'same_closure_declared': True, 'cei_cou_equivalence_declared': True,
                'binding_to_concrete_snapshots': 'pending_original_request', 'rounding_rule': None}
    raise ValueError('evidencia institucional no registrada o alterada')


def nearest_domain(value, unit='1'):
    width = rational(unit); require(width > 0, 'unidad de redondeo positiva')
    center = rational(value)
    return center-width/2, center+width/2  # envolvente exterior; empates sin regla inventada


def affine_domain(terms, domains):
    """Agrupa IDs antes de propagar: las primitivas compartidas se cancelan."""
    coefficients = {}
    for key, coefficient in terms:
        coefficients[key] = coefficients.get(key, Fraction(0)) + rational(coefficient)
    lower = upper = Fraction(0)
    for key, coefficient in coefficients.items():
        if coefficient == 0: continue
        require(key in domains and domains[key] is not None, 'precisión primitiva pendiente: ' + key)
        a, b = domains[key]; require(a <= b, 'dominio invertido')
        x, y = coefficient*a, coefficient*b
        lower += min(x, y); upper += max(x, y)
    return lower, upper


def oriented_domain(domain, multiplier):
    require(type(multiplier) is int and multiplier in (-1, 1), 'orientación inválida')
    a,b=domain
    return min(a*multiplier,b*multiplier),max(a*multiplier,b*multiplier)


class InstitutionalSnapshot:
    """Registro confiable elegido por el llamador, nunca por el documento fuente.

    D2/D6 designan proyecciones de lectura CA2; no son productos publicados.
    XLS usa un lector xlrd provisto/autenticado por el llamador, sin instalarlo.
    """
    def __init__(self, country, family, *, xls_reader=None):
        require(country in ('PER','MEX','COL','CHL') and family in ('D2','D6'), 'ámbito no soportado')
        self.country, self.family, self.xls_reader = country, family, xls_reader

    def snapshot(self, raw):
        c, family = self.country, self.family
        expected = {'PER':PER,'MEX':MEX,'COL':COL,'CHL':CHL_CEI if family=='D2' else CHL_COU}[c]
        require(sha(raw)==expected, 'snapshot no coincide con registro cerrado')
        if c=='CHL' and family=='D2':
            require(self.xls_reader is not None, 'lector XLS autenticado requerido')
            sheet=self.xls_reader(raw)
            cells={'2023':{k:{'value':v,'type':'n','formula':None} for k,v in sheet.items()}}
        else: cells=xlsx_cells(raw)
        def get(selector):
            sheet,cell=selector.split('!'); item=cells[sheet].get(cell)
            require(item is not None and item['type']=='n' and item['value'] is not None, 'celda numérica ausente: '+selector)
            return rational(item['value'])
        def expression(parts):
            return literal(sum((rational(k)*get(s) for s,k in parts),Fraction(0)))
        unit={'PER':'PEN','MEX':'MXN','COL':'COP','CHL':'CLP'}[c]
        vintage={'PER':'INEI_1950_2024_oct2025','MEX':'CSI_2003_2024_revisada_jun2026','COL':'CEI_base2015_2025-02-17','CHL':'Anuario2025_snapshot_pinned'}[c]
        members=[]
        def add(concept,*parts):
            selector=';'.join(s+':'+str(k) for s,k in parts)
            members.append(dict(concept=concept,selector=selector,unit=unit,multiplier='1000000' if c in ('PER','MEX') else '1000000000',value_literal=expression(parts)))
        if c=='PER':
            add('PIB',('CEI_2023!E19',1))
            if family=='D2':
                for concept,cell in [('COE','E21'),('GOS','E27'),('MI','E28'),('TAX_NET','E24')]:add(concept,('CEI_2023!'+cell,1))
            else:
                # Ruta neta candidata (D-02, DB-04 net_equivalent): V=D.211, N=D.29+D.39 (DL390 cero exacto
                # documentado, valor almacenado negativo por convención), P=(D.2-D.3)-N con el total nombrado E24.
                # F376, I376 y J376 no son primitivas de esta ruta: quedan como contrastes publicados.
                require(cells['COU_2023'].get('DL390',{}).get('value') is None, 'DL390 ya no es el blanco autenticado')
                zero='COU_2023!DL390:semantic_zero:'+PER_MAIL
                add('V',('COU_2023!K376',1))
                members.append(dict(concept='N_PROD',selector='COU_2023!DL389:1;'+zero,unit=unit,multiplier='1000000',
                                    value_literal=expression([('COU_2023!DL389',1)])))
                members.append(dict(concept='P_NET',selector='CEI_2023!E24:1;COU_2023!DL389:-1;'+zero+':-1',unit=unit,multiplier='1000000',
                                    value_literal=expression([('CEI_2023!E24',1),('COU_2023!DL389',-1)])))
        elif c=='MEX':
            add('PIB',('Tabulado!S34',1))
            if family=='D2':
                for concept,cell in [('COE','R36'),('GOS','R60'),('MI','R61')]:add(concept,('Tabulado!'+cell,1))
                add('TAX_NET',*[('Tabulado!'+x,1) for x in ('R46','R53','R55','R59')])
            else:
                for concept,cell in [('D21','R46'),('D211','R47'),('D29','R53'),('D31','R55'),('D39','R59')]:add(concept,('Tabulado!'+cell,1))
        elif c=='COL':
            add('PIB',('2023!A29',1))
            if family=='D2':
                for concept,cell in [('COE','A36'),('GOS','A47'),('MI','A48')]:add(concept,('2023!'+cell,1))
                add('TAX_NET',*[('2023!'+x,1) for x in ('Q63','Q68','Q70','Q71')])
            else:
                for concept,cell in [('D21','Q63'),('D211','Q64'),('D29','Q68'),('D31','Q70'),('D39','Q71')]:add(concept,('2023!'+cell,1))
        elif family=='D2':
            for concept,cell in [('COE','D22'),('GOS_MI','D24'),('TAX_NET','D30')]:add(concept,('2023!'+cell,1))
            add('PIB',('2023!D22',1),('2023!D24',1),('2023!D30',1))
        else:
            add('PIB',('23!P16',1),('2!F29',1),('2!G29',1),('2!J29',1))
            add('V',('2!J29',1));add('P_NET',('2!F29',1),('2!G29',1),('2!J29',1));add('N_PROD',('23!P29',1))
        representation=('d2_combined' if c=='CHL' else 'd2_split') if family=='D2' else ('d6_net' if c in ('CHL','PER') else 'd6_gross')
        context=dict(family=family,country_id=c,observation_year=2023,source_id=c+'_pinned_national_accounts',source_vintage=vintage,representation=representation,unit=unit,multiplier=members[0]['multiplier'],accounting_basis='published_national_accounts_scope_review_pending')
        return {'context':context,'members':sorted(members,key=lambda m:m['concept'])}


def account_diagnostic(snapshot):
    require(snapshot['context']['family']=='D2','solo cuenta D2 de lectura')
    m={r['concept']:rational(r['value_literal']) for r in snapshot['members']}
    residual=m['PIB']-m['COE']-m['TAX_NET']-(m['GOS_MI'] if 'GOS_MI' in m else m['GOS']+m['MI'])
    independent=';' not in next(r['selector'] for r in snapshot['members'] if r['concept']=='PIB')
    return {'residual':literal(residual),'published_identity_exact':residual==0 if independent else None,
            'independent_published_PIB':independent,'construction_identity_exact':residual==0,
            'source_admitted':False,'numerical_model_executed':False}


def per_precision(raw_xlsx, raw_mail, *, accept_d21_primitive_mapping=False):
    require(type(accept_d21_primitive_mapping) is bool,'aceptación técnica booleana')
    require(sha(raw_xlsx)==PER,'snapshot PER ajeno');claim=source_claims(raw_mail)
    require(claim['source_sha256']==PER_MAIL,'evidencia PER requerida')
    a=xlsx_cells(raw_xlsx); domains={}
    for selector in ['CEI_2023!E19','COU_2023!K376','COU_2023!J376','COU_2023!DL389']:
        sh,cell=selector.split('!');domains[selector]=nearest_domain(a[sh][cell]['value'])
    domains['COU_2023!DL390']=(Fraction(0),Fraction(0))
    for cell in ['F376','I376']:
        domains['COU_2023!'+cell]=nearest_domain(a['COU_2023'][cell]['value']) if accept_d21_primitive_mapping else None
    return domains


def inspect_per_authority(raw_authority, expected_hash, raw_xlsx, raw_mail):
    require(sha(raw_authority)==expected_hash,'ancla autoridad PER')
    expected={'schema_version':1,'authority_id':'PER_INEI_ORIENTATION_2023_CANDIDATE_V1',
      'status':'candidate_unapproved','author':None,'approved_at':None,'country_id':'PER','year':2023,
      'snapshot_sha256':PER,'unit':'PEN','multiplier':'1000000',
      'operations':[{'concept':'D31','selector':'COU_2023!J376','operation':'multiply','multiplier':-1},
        {'concept':'D39','selector':'COU_2023!DL390','operation':'semantic_exact_zero','value':'0','source_sha256':PER_MAIL}],
      'raw_rewrite_authorized':False,'quantitative_eligibility_authorized':False,'activation':False}
    require(canon(strict_json(raw_authority))==canon(expected),'autoridad PER ampliada o alterada')
    require(sha(raw_mail)==PER_MAIL,'evidencia de cero exacto requerida')
    snap=InstitutionalSnapshot('PER','D6').snapshot(raw_xlsx)  # autentica el snapshot; la ruta neta no consume D.31
    j376=rational(xlsx_cells(raw_xlsx)['COU_2023']['J376']['value'])
    return {'candidate_authority':'pass','normalized_D31':literal(-j376),'D31_consumed_by_net_route':False,
            'semantic_D39':'0','source_admission':False,'production_activation':False}


class ScopedEvidence:
    """Recibo CA2 derivado de una fuente registrada y de un snapshot autenticado.

    No convierte una aclaración parcial en pase de todos los roles/celdas.
    La cadena institucional es sucesión: no fabrica prueba de independencia.
    """
    def __init__(self, snapshot_raw, snapshot_adapter, role, related_snapshots):
        require(type(snapshot_adapter) is InstitutionalSnapshot,'adaptador institucional cerrado requerido')
        self.snapshot_doc=snapshot_adapter.snapshot(snapshot_raw)
        snapshot_sha256=sha(snapshot_raw)
        self.digest=snapshot_sha256;self.role=role
        require(role in ('concept','coverage','orientation','provenance','reconciliation','precision','comparability'),'rol desconocido')
        require(related_snapshots==sorted(set(related_snapshots)) and snapshot_sha256 in related_snapshots,'snapshots relacionados inválidos')
        self.related=related_snapshots

    def evidence(self, raw):
        claim=source_claims(raw);snap=self.snapshot_doc;ctx=snap['context']
        require(ctx['country_id']==claim['country_id'],'país de evidencia ajeno')
        if claim['snapshot_sha256'] is not None: require(claim['snapshot_sha256']==self.digest,'snapshot de evidencia ajeno')
        require(ctx['observation_year']==2023,'no extrapolar a años históricos')
        fields=('family','country_id','observation_year','source_id','source_vintage','unit','multiplier','accounting_basis')
        facts={k:ctx[k] for k in fields}
        facts.update(role=self.role,snapshot_sha256=self.digest,selectors=sorted(r['selector'] for r in snap['members']),related_snapshots=self.related)
        # Solo procedencia PER une de manera demostrada correo y adjunto.
        outcome='pass' if claim['country_id']=='PER' and self.role=='provenance' else 'unknown'
        return {'facts':facts,'outcome':outcome,'precision_rule':None,'common_conflicts':[]}


# ----------------------------------------------------------------------------------------------------------
# Subpaso 1.5 (A-04, D-01, D-09): formalización de las autoridades de orientación PER V2 y COL 2024p.
# Los bytes aprobados son los candidatos revisados (sin reescritura); la aprobación consta en un registro
# separado (autoridades/aprobacion_autoridades_1_5.json) ligado por hash a la autorización del autor.
# No hay firma inventada. inspect_per_authority (V1) queda sin cambios y no se reinterpreta.
PER_V2_AUTHORITY = '3035f689517f4f7a73d3b5bb97c2f6258b9657c128896a990506a5d5225ef0a7'
COL_2024P_AUTHORITY = '8a77f0f94502a6e3b21ddb31260bfed457c135e3254614173858101b9853d3aa'
COL_2024P = '18de220550313fddd23e792bf08b5090867f6a7d24d50f9e23a55f7cab209613'
PER_4032 = 'dfa3eec642a87b356cf6c72aa8401471e5b96278534cfacf6605c982c6657d9c'
AUTHORITY_APPROVAL_FIELDS = {'schema_version', 'status', 'approved_at', 'author', 'authorization_sha256', 'signature',
                             'formalized_at', 'formalized_by', 'authorities'}
PER_V2_SELECTORS = ('CEI_2023!E19', 'CEI_2023!E21', 'CEI_2023!E24', 'CEI_2023!E27', 'CEI_2023!E28', 'COU_2023!K376',
                    'COU_2023!F376', 'COU_2023!I376', 'COU_2023!J376', 'COU_2023!DL389', 'COU_2023!DL390')


def authority_approval(raw_approval, expected_hash, authorization_raw, *, author):
    """Registro de aprobación de autoridades: exacto, ligado a la autorización del autor, sin firma inventada."""
    require(sha(raw_approval) == expected_hash, 'ancla externa del registro de aprobación de autoridades')
    a = strict_json(raw_approval)
    require(isinstance(a, dict) and set(a) == AUTHORITY_APPROVAL_FIELDS, 'registro de aprobación de autoridades exacto')
    auth = strict_json(authorization_raw)
    require(a['schema_version'] == 1 and a['status'] == 'approved_by_author' and a['signature'] is None, 'aprobación sin firma inventada')
    require(a['author'] == author == auth['author'] and a['approved_at'] == auth['approved_at'], 'autor/fecha distintos de la autorización')
    require(a['authorization_sha256'] == sha(authorization_raw) and auth['status'] == 'approved_by_author', 'autorización del autor no vinculada')
    decisions = {d['id'] for d in auth['decisions'] if d['status'] == 'approved_by_author'}
    approvals = {x['id'] for x in auth['approvals'] if x['status'] == 'approved_by_author'}
    require({'D-01', 'D-09'} <= decisions and 'A-04' in approvals, 'D-01, D-09 y A-04 aprobados requeridos')
    rows = a['authorities']
    require(isinstance(rows, list) and [r.get('decision') for r in rows] == ['D-01', 'D-09'], 'autoridades aprobadas exactas y ordenadas')
    expected = {'D-01': ('PER_INEI_ORIENTATION_2023_CANDIDATE_V2', PER_V2_AUTHORITY),
                'D-09': ('COL_DANE_ORIENTATION_2024p_CANDIDATE_V1', COL_2024P_AUTHORITY)}
    for r in rows:
        require(set(r) == {'decision', 'authority_id', 'path', 'sha256', 'scope'}, 'fila de autoridad aprobada exacta')
        require((r['authority_id'], r['sha256']) == expected[r['decision']], 'autoridad aprobada distinta de la revisada')
        require(r['sha256'] == auth['approved_package']['artifacts'][r['path'].replace('autoridades/', 'contratos_candidatos/')],
                'bytes aprobados distintos del paquete autorizado')
    return {r['decision']: r for r in rows}


def inspect_per_authority_v2(raw_authority, expected_hash, raw_xlsx, approval):
    """Autoridad PER V2 aprobada (D-01): solo PER, 2023, snapshot dca6…, sus selectores. No acredita precisión."""
    require(sha(raw_authority) == expected_hash == PER_V2_AUTHORITY, 'ancla autoridad PER V2')
    require(approval['D-01']['sha256'] == expected_hash, 'autoridad PER V2 sin aprobación registrada')
    a = strict_json(raw_authority)
    require(a['schema_version'] == 2 and a['authority_id'] == 'PER_INEI_ORIENTATION_2023_CANDIDATE_V2', 'identidad PER V2')
    require((a['country_id'], a['year'], a['snapshot_sha256'], a['unit'], a['multiplier']) == ('PER', 2023, PER, 'PEN', '1000000'), 'alcance PER V2')
    require(a['raw_rewrite_authorized'] is False and a['quantitative_eligibility_authorized'] is False and a['activation'] is False, 'PER V2 no amplía autorizaciones')
    require(a['supersedes_candidate'] == 'PER_INEI_ORIENTATION_2023_CANDIDATE_V1', 'V2 sucede a V1 sin reinterpretarla')
    ops = {o['concept']: o for o in a['operations']}
    require(set(ops) == {'D31', 'D39'} and len(a['operations']) == 2, 'operaciones PER V2 exactas')
    require((ops['D31']['selector'], ops['D31']['operation'], ops['D31']['multiplier']) == ('COU_2023!J376', 'multiply', -1), 'orientación D.31')
    require(ops['D31']['not_consumed_by'] == ['R-N'], 'la ruta neta no consume D.31')
    z = ops['D39']
    require((z['selector'], z['operation'], z['value'], z['source_sha256'], z['corroborated_by_sha256']) ==
            ('COU_2023!DL390', 'semantic_exact_zero', '0', PER_MAIL, PER_4032) and z['raw_cell_kept_blank'] is True, 'cero exacto D.39')
    selectors = sorted(c['selector'] for c in a['admitted_correspondences'] if 'selector' in c)
    require(selectors == sorted(PER_V2_SELECTORS), 'correspondencias PER V2 exactas')
    require(sha(raw_xlsx) == PER, 'snapshot PER ajeno')
    cells = xlsx_cells(raw_xlsx)
    def value(selector):
        sh, k = selector.split('!')
        return (cells[sh].get(k) or {}).get('value')
    require(value('COU_2023!DL390') is None, 'DL390 ya no es el blanco autenticado')
    j376 = rational(value('COU_2023!J376'))
    require(j376 < 0, 'D.31 almacenado con signo negativo')
    for s in PER_V2_SELECTORS:
        if s != 'COU_2023!DL390':
            rational(value(s))
    require((cells['Resumen'].get('D18') or {}).get('formula') == '+D19+D21+D20', 'fórmula D.21 del archivo')
    require((cells['Resumen'].get('D26') or {}).get('formula') == '+COU_2023!DL390', 'vínculo D.39 del archivo')
    return {'authority': a['authority_id'], 'status': 'approved_by_author (D-01)', 'normalized_D31': literal(-j376),
            'D31_consumed_by_net_route': False, 'semantic_D39': '0', 'selectors': selectors,
            'years': [2023], 'snapshot_sha256': PER, 'precision_accredited_by_authority': False,
            'source_admission': False, 'production_activation': False}


def per_v2_applies(country, year, snapshot_sha256, selector):
    """La autoridad V2 no se extiende a otros países, años, snapshots ni selectores (D-01)."""
    return country == 'PER' and year == 2023 and snapshot_sha256 == PER and selector in PER_V2_SELECTORS


def inspect_col_authority_2024p(raw_authority, expected_hash, raw_xlsx, approval):
    """Orientación COL (D.31/D.39) extendida al snapshot 2024p (D-09). Q70=0 publicado NO es cero exacto (D-05)."""
    require(sha(raw_authority) == expected_hash == COL_2024P_AUTHORITY, 'ancla autoridad COL 2024p')
    require(approval['D-09']['sha256'] == expected_hash, 'autoridad COL 2024p sin aprobación registrada')
    a = strict_json(raw_authority)
    require(a['authority_id'] == 'COL_DANE_ORIENTATION_2024p_CANDIDATE_V1' and a['country_id'] == 'COL' and a['year'] == 2023, 'identidad COL 2024p')
    require((a['snapshot_sha256'], a['sheet'], a['unit'], a['multiplier']) == (COL_2024P, '2023', 'COP', '1000000000'), 'alcance COL 2024p')
    require(a['raw_rewrite_authorized'] is False and a['quantitative_eligibility_authorized'] is False and a['activation'] is False, 'COL 2024p no amplía autorizaciones')
    ops = {o['concept']: o for o in a['operations']}
    require(set(ops) == {'D31', 'D39'} and len(a['operations']) == 2, 'operaciones COL 2024p exactas')
    require((ops['D31']['selector'], ops['D31']['multiplier'], ops['D31']['exact_zero_accredited']) == ('2023!Q70', -1, False), 'D.31 COL 2024p sin cero exacto')
    require((ops['D39']['selector'], ops['D39']['multiplier']) == ('2023!Q71', -1), 'D.39 COL 2024p')
    require(sha(raw_xlsx) == COL_2024P, 'snapshot COL 2024p ajeno')
    cells = xlsx_cells(raw_xlsx)['2023']
    def num(k):
        return rational(cells[k]['value'])
    require(str(cells['J70']['value']).strip() == 'D.31' and str(cells['J71']['value']).strip() == 'D.39', 'etiquetas SCN en el archivo')
    require(literal(num('Q70')) == ops['D31']['published_value'] and literal(num('Q71')) == ops['D39']['published_value'], 'valores publicados')
    require(num('Q69') == num('Q70') + num('Q71') and num('Q70') <= 0 and num('Q71') <= 0, 'convención signed_negative_tax en el archivo')
    return {'authority': a['authority_id'], 'status': 'approved_by_author (D-09)', 'snapshot_sha256': COL_2024P,
            'normalized_D31': literal(-num('Q70')), 'normalized_D39': literal(-num('Q71')),
            'published_zero_is_exact_zero': False, 'scope_use': 'PREG-COL-E2-2023', 'years': [2023],
            'precision_accredited_by_authority': False, 'source_admission': False, 'production_activation': False}


def col_2024p_applies(country, year, snapshot_sha256, selector):
    """La extensión D-09 cubre solo D.31/D.39 del snapshot 2024p, hoja 2023."""
    return country == 'COL' and year == 2023 and snapshot_sha256 == COL_2024P and selector in ('2023!Q70', '2023!Q71')
