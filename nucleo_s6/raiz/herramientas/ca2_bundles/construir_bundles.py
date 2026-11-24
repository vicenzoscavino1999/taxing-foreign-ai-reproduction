"""Bundles CA2-3 reales (subpaso 1.5): vectores, miembros y evidencia de los snapshots incorporados; casos y claims
de los cuatro preregistros A1-E v2; contextos auténticos; validación completa con CA2Validator. Sin solver.

Contexto CA2 (context_fields del catálogo) por caso y país:
- design_v ∈ {G, N} (dos diseños del plan) × fila de D4 activo (model_case_map: menú j_d/j_df/j_f y caso jurídico);
- availability_matrix_hash = SHA-256 de availability_matrix.csv del producto D4 activo verificado;
- structural_state, labor_block, pi, external_requirement y gain_share: sus productores (omega/support_set de D7-B y
  la grilla externa) no existen todavía. Cada hash apunta a un registro de componente almacenado que declara
  «pending_producer_D7_B» y su definición normativa fijada por hash: no se inventa ningún valor.
Los contextos y componentes se guardan por contenido (sha256) y los bundles se leen siempre por hash externo.

Claims: kind y años exactamente del preregistro (R1); inner_quantifier 'forall' declarado de forma conservadora
(CONTINGENCIA_A2: no se reemplaza por «existe una celda favorable»; el cuantificador del titular lo fijará el registro
de claims de D7/D8); outer 'forall'; technical_status 'not_run'; interpretation 'none'.
macro-ca2-v2 queda adoptada y probada, pero ninguna clave real se calcula: sus valores comunes, protocolo y huellas
técnicas pertenecen a la corrida del modelo (fuera de 1.5).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = 'fase2_datos/ca2_bundles'
INDEX = 'indice_bundles_1_5.json'
DESIGNS = ('G', 'N')
PENDING = {
    'structural_state_sha256': ('structural_state', 'trece primitivas estructurales de omega (nueve ejes, gamma, z_m, t, c_legal)', 'contratos/CLAVES_DE_CALCULO.md'),
    'labor_block_sha256': ('labor_block', 'bloque eta_w/eta_H (cell_context.eta_w_block ∈ {micro, macro}) y sus valores', 'contratos/CONTRATOS_D7_B_D8.md'),
    'pi_sha256': ('pi', 'coordenadas pi_iva, pi_otros_productos, pi_produccion (support_set; pi_support_id)', 'contratos/CONTRATOS_D7_B_D8.md'),
    'external_requirement_sha256': ('external_requirement', 'requerimiento externo (external_cell_id, capa, cota, variante, xi; grilla externa autenticada)', 'contratos/CONTRATOS_D7_B_D8.md'),
    'gain_share_sha256': ('gain_share', 'gain_share de omega', 'contratos/CLAVES_DE_CALCULO.md'),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def need(test, message):
    if not test:
        raise ValueError(message)


def canon_file(obj) -> bytes:
    from herramientas.s3.validadores.core import canon
    return canon(obj) + b'\n'


def write_addressed(root: Path, folder: str, obj) -> tuple[str, str]:
    raw = canon_file(obj)
    digest = sha(raw)
    rel = f'{folder}/{digest}.json'
    q = root / rel
    if q.exists():
        need(q.read_bytes() == raw, 'archivo direccionado por contenido distinto: ' + rel)
    else:
        q.parent.mkdir(parents=True, exist_ok=True)
        q.write_bytes(raw)
    return rel, digest


# ------------------------------------------------------------------------------------ D4 y contextos
def d4_active(root: Path) -> dict:
    sys.path.insert(0, str(root / 'herramientas/d4'))
    import construir_d4 as d4  # noqa: PLC0415
    info = d4.verify_product(product_root=root / 'fase2_datos/d4_disponibilidad')
    pointer = json.loads((root / 'fase2_datos/d4_disponibilidad/active_product.json').read_bytes())
    version = root / 'fase2_datos/d4_disponibilidad' / pointer['active_relative_path']
    manifest = json.loads((version / 'd4_manifest.json').read_bytes())
    files = {f['relative_path']: f['sha256'] for f in manifest['files']}
    matrix = (version / 'availability_matrix.csv').read_bytes()
    cmap = (version / 'model_case_map.csv').read_bytes()
    need(sha(matrix) == files['availability_matrix.csv'] and sha(cmap) == files['model_case_map.csv'], 'D4 activo alterado')
    rows = list(csv.DictReader(io.StringIO(cmap.decode('utf-8'))))
    return {'pointer_sha256': sha((root / 'fase2_datos/d4_disponibilidad/active_product.json').read_bytes()),
            'tree_sha256': pointer['active_tree_sha256'], 'availability_matrix_sha256': sha(matrix),
            'model_case_map_sha256': sha(cmap), 'rows': rows, 'verified': bool(info)}


def components(root: Path, out: Path, out_rel: str, s3: dict) -> dict:
    result = {}
    for field, (name, meaning, document) in PENDING.items():
        doc = root / s3['installed_prefix'] / document
        record = {'schema_version': 1, 'coordinate': name, 'status': 'pending_producer_D7_B', 'meaning': meaning, 'value': None,
                  'normative_definition': {'document': s3['installed_prefix'] + document, 'sha256': sha(doc.read_bytes()),
                                           'contract_manifest_sha256': s3['contract_sha256']},
                  'authority_package_sha256': s3['package_sha256'],
                  'note': 'sin productor en 1.5; ningún valor inventado; un cambio posterior produce otro hash de contexto'}
        rel, digest = write_addressed(out, 'componentes', record)
        result[field] = {'path': out_rel + '/' + rel, 'sha256': digest, 'coordinate': name}
    return result


def contexts(out: Path, out_rel: str, d4: dict, comp: dict, country: str) -> list[dict]:
    rows = [r for r in d4['rows'] if r['country_id'] == country]
    need(len(rows) == 5 and {r['model_menu'] for r in rows} == {'j_d', 'j_df', 'j_f'}, 'mapa D4 del país incompleto: ' + country)
    result = []
    for design in DESIGNS:
        for r in sorted(rows, key=lambda x: (x['model_menu'], x['case_id'])):
            ctx = {'design_v': design, 'instrument_j': r['model_menu'][2:], 'availability_case_id': r['case_id'],
                   'availability_matrix_hash': d4['availability_matrix_sha256'], **{k: v['sha256'] for k, v in comp.items()}}
            rel, digest = write_addressed(out, 'contextos', ctx)
            result.append({'label': f"{design}-{ctx['instrument_j']}-{r['case_id']}", 'path': out_rel + '/' + rel, 'sha256': digest,
                           'd4_row': r, 'context': ctx})
    return result


# ------------------------------------------------------------------------------------ adaptadores confiables
class SnapshotAdapter:
    def __init__(self, national):
        self.national = national

    def snapshot(self, raw):
        return self.national.snapshot(raw)


class ComparabilityAdapter:
    """Comparabilidad de revisiones COL (CA2-08): revisión 1.4 recalculada sobre bytes (12 comprobaciones)."""
    _review = None

    def __init__(self, source, related):
        self.source, self.related = source, sorted(set(related))

    def evidence(self, raw):
        from herramientas.nacionales import comparabilidad_col
        snap = self.source.snapshot(raw)
        ctx = snap['context']
        facts = {k: ctx[k] for k in ('family', 'country_id', 'observation_year', 'source_id', 'source_vintage', 'unit', 'multiplier', 'accounting_basis')}
        facts.update(role='comparability', snapshot_sha256=self.source.cfg['sha256'], selectors=sorted(m['selector'] for m in snap['members']),
                     related_snapshots=self.related)
        if ComparabilityAdapter._review is None:
            ComparabilityAdapter._review = comparabilidad_col.review()
        review = ComparabilityAdapter._review
        ok = review['verdict'] == 'comparable_for_E2_individual' and all(c['result'] for c in review['checks'])
        snaps = sorted(r['snapshot_sha256'] for r in review['revisions'].values())
        return {'facts': facts, 'outcome': 'pass' if ok and snaps == self.related else 'fail', 'precision_rule': None, 'common_conflicts': []}


# ------------------------------------------------------------------------------------ construcción
def created_at(cfg: dict) -> str:
    value = cfg.get('obtained_at') or cfg.get('accessed_at')
    need(value, 'snapshot sin fecha de obtención registrada')
    return value


class BundleBuilder:
    def __init__(self, contracts, reception_prefix: str):
        self.c = contracts
        self.s = contracts.C['ca2']
        self.prefix = reception_prefix
        self.tables = {k: [] for k in self.s['tables']}
        self.adapters = {}
        self.vectors = {}

    def vector(self, country, family, year, revision):
        from herramientas.nacionales.nacionales import NationalAdapter
        from herramientas.s3.validadores.core import H
        a = NationalAdapter(country, family, year, revision)
        vid = f'{country}_{family}_{year}_{a.key}'
        if vid in self.vectors:
            return self.vectors[vid]
        s = a.read()
        ctx = s['context']
        v = {'vector_id': vid, 'family': ctx['family'], 'country_id': country, 'observation_year': year, 'source_id': a.key,
             'source_vintage': ctx['source_vintage'], 'snapshot_path': self.prefix + a.cfg['path'], 'snapshot_sha256': a.cfg['sha256'],
             'adapter_id': vid, 'representation': ctx['representation'], 'unit': ctx['unit'], 'multiplier': ctx['multiplier'],
             'accounting_basis': ctx['accounting_basis'], 'denominator_member_id': 'PIB'}
        ms = sorted((dict(vector_id=vid, member_id=m['concept'], concept=m['concept'], country_id=country, observation_year=year,
                          source_vintage=ctx['source_vintage'], snapshot_sha256=a.cfg['sha256'], selector=m['selector'], unit=m['unit'],
                          multiplier=m['multiplier'], value_literal=m['value_literal'], denominator_member_id='PIB') for m in s['members']),
                    key=lambda m: m['member_id'])
        v['vector_sha256'] = H({'header': v, 'members': ms})
        self.tables['ca2_vectors'].append(v)
        self.tables['ca2_members'].extend(ms)
        self.adapters[vid] = SnapshotAdapter(a)
        self.vectors[vid] = (v, a, ms)
        return self.vectors[vid]

    def evidence(self, vid, role, related, *, predecessor=None, created=None):
        from herramientas.nacionales.adaptadores_ca2 import EvidenceAdapter
        v, a, ms = self.vectors[vid]
        eid = f'EV_{vid}_{role}'
        if any(e['evidence_id'] == eid for e in self.tables['ca2_evidence']):
            return eid
        e = {'evidence_id': eid, 'vector_id': vid, 'role': role, 'artifact_path': v['snapshot_path'], 'artifact_sha256': v['snapshot_sha256'],
             'adapter_id': f'{vid}:{role}', 'selectors': sorted(m['selector'] for m in ms), 'related_snapshots': sorted(set(related)),
             'created_at': created or created_at(a.cfg), 'predecessor_id': predecessor,
             'relation_kind': 'successor' if predecessor else 'initial', 'against_evidence_ids': [], 'independence_path': None,
             'independence_sha256': None}
        self.tables['ca2_evidence'].append(e)
        self.adapters[e['adapter_id']] = (ComparabilityAdapter(a, related) if role == 'comparability' else EvidenceAdapter(a, role, related))
        return eid

    def vector_with_evidence(self, country, family, year, revision, *, predecessor_vid=None, comparability=None):
        v, a, _ = self.vector(country, family, year, revision)
        vid = v['vector_id']
        roles = list(self.s['mandatory_evidence']) + ['precision'] + (['comparability'] if comparability else [])
        for role in roles:
            related = comparability if role == 'comparability' else [v['snapshot_sha256']]
            pred = f'EV_{predecessor_vid}_{role}' if predecessor_vid else None
            self.evidence(vid, role, related, predecessor=pred)
        return vid

    def finish(self):
        for name, rows in self.tables.items():
            order = self.c.C['tables'][name]['order_by']
            rows.sort(key=lambda r: tuple(r[k] for k in order))
        return self.tables


def build_bundle(entry: dict, contracts, ctx_by_country: dict, reception_prefix: str) -> tuple[dict, dict]:
    """Un bundle por preregistro: todos los contextos auténticos, casos por escenario y año, claims del registro."""
    b = BundleBuilder(contracts, reception_prefix)
    policy = b.s['scenario_policy']
    pid = entry['preregistration_id']
    years = sorted({y for ys in entry['claims'].values() for y in ys})
    revisions = entry.get('revisions') or {}
    vids = {}
    for country in entry['country_set']:
        if revisions:
            labels, prev6, prev2 = [], None, None
            snaps2 = sorted(r['D2']['2023']['snapshot_sha256'] for r in revisions[country])
            snaps6 = sorted(r['D6']['snapshot_sha256'] for r in revisions[country])
            for rev in revisions[country]:
                revision = 'COL_2024p' if rev['D6']['source_id'] == 'COL_2024p' else 'selected'
                d2 = b.vector_with_evidence(country, 'D2', 2023, revision, predecessor_vid=prev2, comparability=snaps2)
                d6 = b.vector_with_evidence(country, 'D6', 2023, revision, predecessor_vid=prev6, comparability=snaps6)
                vids[(country, rev['label'])] = {2023: (d2, d6)}
                prev2, prev6 = d2, d6
                labels.append(rev['label'])
        else:
            d6 = b.vector_with_evidence(country, 'D6', 2023, 'selected')
            per_year = {}
            for y in years:
                d2 = b.vector_with_evidence(country, 'D2', y, 'selected')
                per_year[y] = (d2, d6)
            vids[(country, None)] = per_year
    cases, inputs, claims = [], [], []
    labels = sorted({k[1] for k in vids}, key=lambda x: (x is not None, x or ''))
    for ctx_index in range(len(next(iter(ctx_by_country.values())))):
        ctx_label = ctx_by_country[entry['country_set'][0]][ctx_index]['label']
        ctx_cases = {}
        for scenario in entry['scenarios']:
            for label in labels:
                for y in years:
                    if label is not None and y != 2023:
                        continue
                    cid = ':'.join(x for x in (pid, scenario, str(y), label, ctx_label) if x)
                    cases.append({'case_id': cid, 'scenario': scenario, 'channel': policy[scenario]['channel'],
                                  'precision_claim': policy[scenario]['precision'], 'admissibility': policy[scenario]['admissibility'],
                                  'measurement_domain': None, 'preregistration_id': pid, 'case_type': entry['case_type'],
                                  'country_set': list(entry['country_set'])})
                    ctx_cases.setdefault((scenario, y), []).append(cid)
                    for country in entry['country_set']:
                        ctx = ctx_by_country[country][ctx_index]
                        need(ctx['label'] == ctx_label, 'contextos desalineados entre países')
                        d2, d6 = vids[(country, label)][y]
                        inputs.append({'case_id': cid, 'country_id': country, 'anchor_year': y, 'd2_vector_id': d2, 'd6_vector_id': d6,
                                       'context_path': ctx['path'], 'context_sha256': ctx['sha256']})
        for kind, kyears in sorted(entry['claims'].items()):
            ids = sorted(c for (sc, y), cs in ctx_cases.items() for c in cs if y in kyears)
            claims.append({'claim_id': f'{pid}:{kind}:{ctx_label}', 'kind': kind, 'case_ids': ids,
                           'required_scenarios': sorted(entry['scenarios']), 'countries': list(entry['country_set']),
                           'anchor_years': list(kyears), 'inner_quantifier': 'forall', 'outer_quantifier': 'forall',
                           'technical_status': 'not_run', 'interpretation': 'none'})
    b.tables['ca2_cases'], b.tables['ca2_inputs'], b.tables['ca2_claims'] = cases, inputs, claims
    return b.finish(), b.adapters


def build_all(root: Path, *, out_rel: str, s3: dict, cases: list[str]) -> dict:
    """Construye y valida los bundles en root/out_rel; devuelve el índice (sin escribirlo)."""
    from herramientas.nacionales.base import load_registry_bytes, verify_reception, RECEPTION_TREE
    from herramientas.nacionales.adaptadores_ca2 import contracts as national_contracts
    from herramientas.s3.validadores.ca2 import CA2Validator
    root = Path(root)
    out = root / out_rel
    reception = verify_reception(root)
    registry = json.loads(load_registry_bytes())
    entries = {e['preregistration_id']: e for e in registry['entries']}
    need(cases and sorted(set(cases)) == sorted(cases) and set(cases) <= set(entries), 'casos no preregistrados')
    contracts = national_contracts()
    d4 = d4_active(root)
    comp = components(root, out, out_rel, s3)
    ctx_all, bundles = {}, []
    prefix = f'fase2_datos/recepcion_nacional/versions/{RECEPTION_TREE}/'
    for pid in sorted(cases):
        entry = entries[pid]
        ctx_by_country = {}
        for country in entry['country_set']:
            if country not in ctx_all:
                ctx_all[country] = contexts(out, out_rel, d4, comp, country)
            ctx_by_country[country] = ctx_all[country]
        tables, adapters = build_bundle(entry, contracts, ctx_by_country, prefix)
        raw = canon_file(tables)
        digest = sha(raw)
        rel = f'bundles/{digest}.json'
        q = out / rel
        if q.exists():
            need(q.read_bytes() == raw, 'bundle direccionado distinto')
        else:
            q.parent.mkdir(parents=True, exist_ok=True)
            q.write_bytes(raw)
        result = CA2Validator(contracts, root, adapters).read_bundle(q, digest)
        admissibility = result['case_admissibility']
        expected = {c['case_id']: c['admissibility'] for c in tables['ca2_cases']}
        need(admissibility == expected, 'admisibilidad derivada distinta de la declarada')
        need(result['real_source_admission'] is False and result['production_activation'] is False and result['numerical_validation'] is False, 'retorno CA2')
        counts = {}
        for v in admissibility.values():
            counts[v] = counts.get(v, 0) + 1
        bundles.append({'preregistration_id': pid, 'path': out_rel + '/' + rel, 'sha256': digest, 'bytes': len(raw),
                        'tables': {k: len(v) for k, v in tables.items()}, 'case_admissibility': counts,
                        'evidence_outcomes': {k: v['outcome'] for k, v in sorted(result['evidence_outcomes'].items())},
                        'metadata_validation': result['metadata_validation'], 'real_source_admission': False,
                        'numerical_validation': False, 'production_activation': False})
    return {'schema_version': 1, 'product_type': 'ca2_bundles_1_5', 'authority_package_sha256': s3['package_sha256'],
            'contract_sha256': s3['contract_sha256'], 'reception_tree_sha256': reception['tree_sha256'],
            'registry_sha256': sha(load_registry_bytes()),
            'd4': {k: d4[k] for k in ('pointer_sha256', 'tree_sha256', 'availability_matrix_sha256', 'model_case_map_sha256')},
            'components': comp,
            'contexts': {country: [{'label': c['label'], 'path': c['path'], 'sha256': c['sha256'],
                                    'd4_row': {k: c['d4_row'][k] for k in ('model_menu', 'case_id', 'availability_assumed', 'quantitative_use')}}
                                   for c in ctx] for country, ctx in sorted(ctx_all.items())},
            'bundles': bundles,
            'claims_inner_quantifier': "'forall' declarado de forma conservadora; el cuantificador del titular lo fijará el registro de claims de D7/D8",
            'macro_ca2_v2': 'adoptada y probada; ninguna clave real calculada (valores comunes, protocolo y huellas técnicas son de la corrida del modelo)',
            'model_execution': False}


def publish(root: Path, *, s3_policy: str, s3_receipt: str, s3_author: str, cases: list[str]) -> dict:
    root = Path(root).resolve()
    need(root == ROOT.resolve(), 'raíz ajena')
    from herramientas.congelamiento import s3_publicador as S3P
    authority = S3P.verify(root, s3_policy, s3_receipt, s3_author)
    index_path = root / OUT / INDEX
    need(not index_path.exists(), 'el índice de bundles 1.5 ya existe: no se sobrescribe')
    index = build_all(root, out_rel=OUT, s3=authority, cases=cases)
    raw = (json.dumps(index, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    index_path.write_bytes(raw)
    return {'index_path': OUT + '/' + INDEX, 'index_sha256': sha(raw), 'bundles': [(b['preregistration_id'], b['sha256'], b['case_admissibility']) for b in index['bundles']]}


def verify(root: Path, *, index_sha256: str, s3: dict) -> dict:
    """Relee cada bundle por su hash externo del índice y lo revalida con adaptadores reales."""
    from herramientas.nacionales.adaptadores_ca2 import contracts as national_contracts
    from herramientas.s3.validadores.ca2 import CA2Validator
    root = Path(root)
    raw = (root / OUT / INDEX).read_bytes()
    need(sha(raw) == index_sha256, 'índice de bundles distinto del fijado')
    index = json.loads(raw)
    need(index['authority_package_sha256'] == s3['package_sha256'], 'bundles de otra autoridad')
    registry = json.loads(__import__('herramientas.nacionales.base', fromlist=['x']).load_registry_bytes())
    entries = {e['preregistration_id']: e for e in registry['entries']}
    contracts = national_contracts()
    ctx_by = {country: ctx for country, ctx in index['contexts'].items()}
    out = []
    for bnd in index['bundles']:
        entry = entries[bnd['preregistration_id']]
        tables, adapters = build_bundle(entry, contracts, {c: [dict(x, context=None) for x in ctx_by[c]] for c in entry['country_set']},
                                        f"fase2_datos/recepcion_nacional/versions/{index['reception_tree_sha256']}/")
        need(sha(canon_file(tables)) == bnd['sha256'], 'bundle no reproducido: ' + bnd['preregistration_id'])
        result = CA2Validator(contracts, root, adapters).read_bundle(root / bnd['path'], bnd['sha256'])
        need(sorted(set(result['case_admissibility'].values())) == sorted(bnd['case_admissibility']), 'admisibilidad distinta')
        out.append((bnd['preregistration_id'], 'verified'))
    return {'index_sha256': index_sha256, 'bundles': out}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Bundles CA2 reales (1.5)')
    parser.add_argument('command', choices=['publicar', 'verificar'])
    parser.add_argument('--s3-policy-sha256', required=True); parser.add_argument('--s3-receipt-sha256', required=True)
    parser.add_argument('--s3-author', required=True); parser.add_argument('--cases', default='')
    parser.add_argument('--index-sha256')
    args = parser.parse_args(argv)
    try:
        if args.command == 'publicar':
            result = publish(ROOT, s3_policy=args.s3_policy_sha256, s3_receipt=args.s3_receipt_sha256, s3_author=args.s3_author,
                             cases=[c for c in args.cases.split(',') if c])
        else:
            from herramientas.congelamiento import s3_publicador as S3P
            authority = S3P.verify(ROOT, args.s3_policy_sha256, args.s3_receipt_sha256, args.s3_author)
            result = verify(ROOT, index_sha256=args.index_sha256, s3=authority)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError) as exc:
        print('CA2 RECHAZADO: ' + str(exc))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
