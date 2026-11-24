"""C-A2: preflight de metadatos por selección explícita. Sin escrituras ni solver.

Los adaptadores son código confiable registrado por el llamador. No se importan
plugins elegidos por el documento. Ningún resultado admite fuentes reales.

Enmienda candidata A1-E v2 (27-09-2026, CA2-3 candidato, no activo): cada caso declara
preregistration_id, case_type y country_set, que deben coincidir con ca2.case_registry.
Los inputs de un caso tienen exactamente sus miembros declarados (sin añadir ni retirar);
toda afirmación usa un tipo permitido por su preregistro con exactamente sus años (R1, 28-09) y los
vectores respetan la representación que el preregistro fije (R2, 28-09);
la aplicación principal es solo PER, la comparación internacional incluye PER y la
sensibilidad individual tiene un solo país y no exige PER. Las afirmaciones no mezclan
preregistros y sus países/años son los del registro. El dominio de datos
(types.country) sigue siendo de cuatro países; el conjunto consumido es el del caso.

Subpaso 1.5 (A-01, autorización del autor 2026-09-28): la regla de precisión de un recibo se despacha
explícitamente por contract_version. Sin contract_version -> CA2-2 (sin cambios). CA2-2X-PRECISION-2 ->
validadores/ca2x.validate contra la proyección (concepto, selector) AUTENTICADA por el adaptador de snapshot del
vector; sin esa proyección (vector sin adaptador o llamada directa sin contexto) se rechaza. Cualquier otra
versión, incluidas CA2-2X-PRECISION-1 (reemplazada) y las sintéticas, se rechaza. Nada se reinterpreta.
"""
from pathlib import Path
from .core import require, sha, H, strict_json, inside, ContractError
from .temporal import instant
from . import ca2x


class CA2Validator:
    def __init__(self, contracts, source_root, adapters=None):
        self.c = contracts
        self.s = contracts.C['ca2']
        self.root = Path(source_root)
        self.adapters = dict(adapters or {})

    def array(self, values, typ):
        require(isinstance(values, list), 'CA2 array requerido')
        for value in values:
            self.c.scalar(value, typ)
        require(values == sorted(set(values)), 'CA2 lista duplicada/desordenada')
        return values

    def bytes(self, path, digest):
        raw = inside(self.root, path).read_bytes()
        require(sha(raw) == digest, 'CA2 hash de archivo incorrecto')
        return raw

    def read_bundle(self, path, expected_sha256):
        self.c.scalar(expected_sha256, 'sha')
        raw = Path(path).read_bytes()
        require(sha(raw) == expected_sha256, 'CA2 ancla externa de bundle incompatible')
        result = self.validate(strict_json(raw, canonical_file=True))
        return dict(result, bundle_sha256=expected_sha256)

    def validate(self, tables):
        """Objeto en memoria: solo metadatos; read_bundle añade autenticación externa."""
        require(isinstance(tables, dict) and set(tables) == set(self.s['tables']), 'CA2 tablas exactas')
        require(all(isinstance(rows, list) for rows in tables.values()), 'CA2 filas array')
        self.c.references(tables)
        vectors = {v['vector_id']: v for v in tables['ca2_vectors']}
        cases = {v['case_id']: v for v in tables['ca2_cases']}
        members = {k: [m for m in tables['ca2_members'] if m['vector_id'] == k] for k in vectors}
        evidence = {k: [e for e in tables['ca2_evidence'] if e['vector_id'] == k] for k in vectors}
        statuses, receipts = {}, {}
        for vid, v in vectors.items():
            rep = self.s['representations'][v['representation']]
            require(v['family'] == rep['family'] and v['observation_year'] in self.s['years'][v['family']], 'CA2-01 familia/año')
            ms = members[vid]
            require(sorted(m['concept'] for m in ms) == rep['concepts'], 'CA2-02 vector incompleto/concepto duplicado')
            pib = next(m for m in ms if m['concept'] == 'PIB')
            require(v['denominator_member_id'] == pib['member_id'], 'CA2-02 denominador no PIB propio')
            for m in ms:
                for k in ('country_id', 'observation_year', 'source_vintage', 'snapshot_sha256', 'unit', 'multiplier', 'denominator_member_id'):
                    require(m[k] == v[k], 'CA2-03 mezcla de partidas: ' + k)
            require(v['vector_sha256'] == H({'header': {k:x for k,x in v.items() if k != 'vector_sha256'}, 'members': ms}), 'CA2-02 hash vector')
            raw = self.bytes(v['snapshot_path'], v['snapshot_sha256'])
            adapter = self.adapters.get(v['adapter_id'])
            role_status = {'snapshot': 'pass'}
            if adapter is None:
                role_status['snapshot'] = 'unknown'
            else:
                expected = {'context': {k:v[k] for k in self.s['snapshot_projection']},
                            'members': [{k:m[k] for k in self.s['snapshot_member_projection']} for m in sorted(ms, key=lambda x:x['concept'])]}
                require(adapter.snapshot(raw) == expected, 'CA2-03 extracción snapshot incompatible')
            roles = [e['role'] for e in evidence[vid]]
            require(len(roles) == len(set(roles)), 'CA2-04 rol ambiguo en una versión del vector')
            for role in self.s['mandatory_evidence']:
                role_status[role] = 'fail'  # Ausencia de evidencia común.
            for e in evidence[vid]:
                selectors = self.array(e['selectors'], 'text')
                require(selectors == sorted(m['selector'] for m in ms), 'CA2-04 selectores ajenos/incompletos')
                self.array(e['related_snapshots'], 'sha')
                require(v['snapshot_sha256'] in e['related_snapshots'], 'CA2-04 snapshot ajeno')
                eraw = self.bytes(e['artifact_path'], e['artifact_sha256'])
                ea = self.adapters.get(e['adapter_id'])
                receipt = None
                role_status[e['role']] = 'unknown'
                if ea is None:
                    pass
                else:
                    receipt = ea.evidence(eraw)
                    require(isinstance(receipt, dict) and set(receipt) == set(self.s['evidence_receipt_fields']), 'CA2-04 recibo de adaptador exacto')
                    facts = {k: (e[k] if k in e else v[k]) for k in self.s['evidence_facts']}
                    require(receipt['facts'] == facts, 'CA2-04 alcance de evidencia incompatible')
                    require(receipt['outcome'] in ('pass','fail','unknown'), 'CA2-04 resultado de adaptador')
                    role_status[e['role']] = receipt['outcome']
                    conflicts = self.array(receipt['common_conflicts'], 'ca2_role')
                    require(set(conflicts) <= set(self.s['mandatory_evidence']), 'CA2-04 contradicción común mal clasificada')
                    if conflicts:
                        role_status['common_conflicts'] = 'fail'
                    if e['role'] == 'precision':
                        if receipt['outcome'] == 'pass' or receipt['precision_rule'] is not None:
                            # Proyección autenticada solo si el adaptador de snapshot contrastó los miembros con los bytes.
                            projection = ([(m['concept'], m['selector']) for m in sorted(ms, key=lambda x: x['selector'])]
                                          if role_status['snapshot'] == 'pass' else None)
                            self.precision(receipt['precision_rule'], selectors, projection=projection,
                                           snapshot_sha256=v['snapshot_sha256'])
                    elif e['role'] != 'precision':
                        require(receipt['precision_rule'] is None, 'CA2-05 precisión fuera de rol')
                receipts[e['evidence_id']] = receipt
            statuses[vid] = role_status

        self.chains(tables, vectors)
        inputs, derived, case_statuses = {}, {}, {}
        registry = self.registry()
        entries = {}
        for cid, case in cases.items():
            policy = self.s['scenario_policy'][case['scenario']]
            require(case['channel'] == policy['channel'] and case['precision_claim'] == policy['precision'], 'CA2-05 vía/precisión incompatible')
            require(case['measurement_domain'] is None, 'CA2-05 dominio no autorizado')
            entry = self.case_entry(case, registry)
            entries[cid] = entry
            rows = [r for r in tables['ca2_inputs'] if r['case_id'] == cid]
            # Exactamente los miembros declarados y preregistrados: ni faltan ni sobran países.
            require(sorted(r['country_id'] for r in rows) == entry['country_set'], 'CA2-07 miembros distintos del conjunto preregistrado')
            require(len({r['anchor_year'] for r in rows}) == 1, 'CA2-06 ancla no comparable entre países')
            require(rows[0]['anchor_year'] in sorted({y for ys in entry['claims'].values() for y in ys}), 'CA2-07 año no preregistrado para el caso')
            case_status = []
            for row in rows:
                a, b = (vectors[row[k]] for k in ('d2_vector_id','d6_vector_id'))
                require(a['family'] == 'D2' and b['family'] == 'D6', 'CA2-06 familia del input')
                self.registered_vectors(entry, row, a, b)
                require(a['country_id'] == b['country_id'] == row['country_id'], 'CA2-06 país del input')
                require(a['observation_year'] == row['anchor_year'] and b['observation_year'] == 2023, 'CA2-06 año del input')
                context = strict_json(self.bytes(row['context_path'], row['context_sha256']), canonical_file=True)
                require(isinstance(context, dict) and set(context) == set(self.s['context_fields']), 'CA2-06 contexto exacto')
                for k,t in self.s['context_fields'].items():
                    self.c.scalar(context[k], t)
                for v in (a,b):
                    state = statuses[v['vector_id']]
                    required = ['snapshot', *self.s['mandatory_evidence'], *policy['additional_evidence']]
                    case_status.extend(state.get(role, 'fail') for role in required)
                    case_status.append(state.get('common_conflicts', 'pass'))
                if row['anchor_year'] == 2023:
                    require(all(a[k] == b[k] for k in ('unit','multiplier','accounting_basis')), 'CA2-06 unidad/multiplicador/base entre cuentas incompatible')
                    # Una coincidencia de valores no sustituye conciliación entre fuentes.
                    pair = {a['snapshot_sha256'], b['snapshot_sha256']}
                    if len(pair) > 1:
                        for v in (a,b):
                            ev = [e for e in evidence[v['vector_id']] if e['role'] == 'reconciliation' and pair <= set(e['related_snapshots'])]
                            if not ev:
                                case_status.append('fail')
                    else:
                        pa, pb = (next(m for m in members[v['vector_id']] if m['concept'] == 'PIB') for v in (a,b))
                        require(all(pa[k] == pb[k] for k in ('selector','value_literal','unit','multiplier')), 'CA2-06 PIB compartido incompatible')
            inputs[cid], case_statuses[cid] = rows, case_status

        require(cases and tables['ca2_claims'], 'CA2-07 bundle vacío')
        covered = set()
        for claim in tables['ca2_claims']:
            ids = self.array(claim['case_ids'], 'id')
            scenarios = self.array(claim['required_scenarios'], 'ca2_scenario')
            require(ids and set(ids) <= set(cases), 'CA2-07 casos desconocidos/vacíos')
            covered.update(ids)
            require(scenarios == sorted({cases[k]['scenario'] for k in ids}), 'CA2-07 escenarios incompletos')
            prereg = {cases[k]['preregistration_id'] for k in ids}
            require(len(prereg) == 1, 'CA2-07 afirmación mezcla preregistros o tipos de caso')
            entry = entries[ids[0]]
            countries = entry['country_set']
            require(self.array(claim['countries'], 'country') == countries, 'CA2-07 alcance de países distinto del preregistrado')
            years = self.array(claim['anchor_years'], 'int')
            require(years == sorted({r['anchor_year'] for k in ids for r in inputs[k]}), 'CA2-07 alcance de años')
            require(claim['outer_quantifier'] == 'forall', 'CA2-07 cuantificador externo')
            # Cada escenario declarado cubre los mismos años, no solo la unión.
            for scenario in scenarios:
                require(sorted({r['anchor_year'] for k in ids if cases[k]['scenario'] == scenario for r in inputs[k]}) == years, 'CA2-07 escenario/años incompleto')
            # R1 (revisión 1.4): TODO tipo de afirmación debe estar permitido expresamente por su preregistro y cubrir
            # exactamente los años registrados para ese tipo; cambiar la etiqueta no permite omitir años.
            require(claim['kind'] in entry['claims'], 'CA2-07 tipo de afirmación no preregistrado para el caso: ' + str(claim['kind']))
            require(years == entry['claims'][claim['kind']], 'CA2-07 años distintos de los preregistrados para la afirmación')
            if claim['kind'] == 'historical_anchor':
                require(set(years) <= set(self.s['years']['D2']), 'CA2-06 cobertura histórica')
                for country in countries:
                    rows = [r for k in ids for r in inputs[k] if r['country_id'] == country]
                    require(len({(r['d6_vector_id'],r['context_sha256']) for r in rows}) == 1, 'CA2-06 D6/contexto histórico debe permanecer fijo')
            elif claim['kind'] == 'primary':
                require(years == [2023], 'CA2-06 comparación primaria 2023')
            require(claim['technical_status'] != 'complete', 'CA2-09 la biblioteca no certifica resultado numérico')
            expected_interpretation = 'not_identified' if claim['kind'] == 'measurement_error' and scenarios == ['E4'] else 'none'
            require(claim['interpretation'] == expected_interpretation, 'CA2-09 confusión técnico/interpretación')
            if 'E4' in scenarios:
                require(claim['kind'] == 'measurement_error' and scenarios == ['E4'], 'CA2-09 E4 separado de resultados económicos')
            if 'E2' in scenarios:
                for country in countries:
                    require(len({r['context_sha256'] for k in ids for r in inputs[k] if r['country_id'] == country}) == 1, 'CA2-08 contexto de comparación debe permanecer fijo')
                self.revisions([r for k in ids if cases[k]['scenario'] == 'E2' for r in inputs[k]], vectors, evidence, receipts, case_statuses)
        require(covered == set(cases), 'CA2-07 casos omitidos del alcance')
        used = {r[k] for rows in inputs.values() for r in rows for k in ('d2_vector_id','d6_vector_id')}
        require(used == set(vectors), 'CA2-07 vectores sin caso')
        for cid, case in cases.items():
            state = case_statuses[cid]
            admissible = self.s['scenario_policy'][case['scenario']]['admissibility']
            actual = 'not_admissible' if 'fail' in state else ('pending_evidence' if 'unknown' in state else admissible)
            retained_pending = case['admissibility'] == 'pending_evidence' and actual == admissible
            require(case['admissibility'] == actual or retained_pending, 'CA2-09 admisibilidad declarada no demostrada: ' + actual)
            derived[cid] = 'pending_evidence' if retained_pending else actual
        return {'metadata_validation': 'pass', 'case_admissibility': derived,
                'evidence_outcomes': {eid: {'outcome': r['outcome'] if r else 'unknown', 'common_conflicts': r['common_conflicts'] if r else []} for eid,r in receipts.items()},
                'real_source_admission': False, 'numerical_validation': False,
                'production_activation': False}

    def registry(self):
        reg = self.s.get('case_registry')
        require(isinstance(reg, dict) and isinstance(reg.get('entries'), list) and reg['entries'], 'CA2-07 registro de casos preregistrados ausente')
        domain = sorted(self.c.C['types']['country']['enum'])
        ids = [e['preregistration_id'] for e in reg['entries']]
        require(len(ids) == len(set(ids)), 'CA2-07 preregistro duplicado')
        principal = reg['principal_country']
        require(principal in domain, 'CA2-07 país principal fuera del dominio')
        excluded = set(reg.get('excluded_this_version', {}))
        for e in reg['entries']:
            cs = e['country_set']
            require(cs == sorted(set(cs)) and set(cs) <= set(domain) and not set(cs) & excluded, 'CA2-07 conjunto preregistrado inválido')
            if e['case_type'] == 'aplicacion_principal':
                require(cs == [principal], 'CA2-07 aplicación principal distinta del país principal')
            elif e['case_type'] == 'comparacion_internacional':
                require(len(cs) >= 2 and principal in cs, 'CA2-07 comparación sin país principal o con un solo país')
            elif e['case_type'] == 'sensibilidad_individual':
                require(len(cs) == 1, 'CA2-07 sensibilidad individual con más de un país')
            else:
                require(False, 'CA2-07 tipo de caso desconocido')
            require(set(e['scenarios']) <= set(self.s['scenario_policy']), 'CA2-07 escenario preregistrado desconocido')
            claims = e.get('claims')
            require(isinstance(claims, dict) and claims and set(claims) <= set(self.c.C['types']['ca2_claim_kind']['enum']), 'CA2-07 tipos de afirmación preregistrados inválidos')
            require(all(isinstance(ys, list) and ys and ys == sorted(set(ys)) and all(type(y) is int for y in ys) for ys in claims.values()), 'CA2-07 años preregistrados inválidos')
        return {e['preregistration_id']: e for e in reg['entries']}

    def case_entry(self, case, registry):
        entry = registry.get(case.get('preregistration_id'))
        require(entry is not None, 'CA2-07 caso sin preregistro')
        require(case['case_type'] == entry['case_type'], 'CA2-07 tipo de caso distinto del preregistrado')
        require(self.array(case['country_set'], 'country') == entry['country_set'], 'CA2-07 conjunto declarado distinto del preregistrado')
        require(case['scenario'] in entry['scenarios'], 'CA2-07 escenario no preregistrado para el caso')
        return entry

    def registered_vectors(self, entry, row, d2, d6):
        """Vectores del input dentro de lo preregistrado (snapshot/vintage exactos si el registro los fija)."""
        allowed = []
        if entry.get('vectors'):
            spec = entry['vectors'].get(row['country_id'])
            require(spec is not None, 'CA2-07 país sin vectores preregistrados')
            allowed.append((spec['D2'].get(str(row['anchor_year'])), spec['D6']))
        if entry.get('revisions'):
            for rev in entry['revisions'].get(row['country_id'], []):
                allowed.append((rev['D2'].get(str(row['anchor_year'])), rev['D6']))
        if not allowed:
            return
        def match(v, spec):
            return spec is not None and all(v[k] == spec[k] for k in ('snapshot_sha256', 'source_vintage') if spec.get(k) is not None)
        def same_representation(v, spec):
            # R2 (revisión 1.4): si el preregistro fija la representación, se exige exactamente; distinta o ausente se rechaza.
            return 'representation' not in spec or spec['representation'] is None or v.get('representation') == spec['representation']
        candidates = [(s2, s6) for s2, s6 in allowed if match(d2, s2) and match(d6, s6)]
        require(candidates, 'CA2-07 vector o revisión no preregistrados para el caso')
        require(any(same_representation(d2, s2) and same_representation(d6, s6) for s2, s6 in candidates),
                'CA2-07 representación distinta de la preregistrada o ausente')

    def precision(self, rule, selectors, *, projection=None, snapshot_sha256=None):
        """Despacho explícito por contract_version (A-01, 1.5). CA2-2 conserva su significado sin cambios."""
        if isinstance(rule, dict) and 'contract_version' in rule:
            require(rule['contract_version'] == ca2x.CONTRACT, 'CA2-05 versión de contrato de precisión no adoptada: ' + str(rule['contract_version']))
            require(projection is not None, 'CA2-05 CA2-2X exige la proyección autenticada del vector (sin despacho no se acepta)')
            require([s for _, s in projection] == selectors, 'CA2-05 proyección y selectores del recibo incompatibles')
            try:
                ca2x.validate(rule, projection, snapshot_sha256=snapshot_sha256, emitted=True)
            except ca2x.ContractError as e:
                raise ContractError('CA2-05 CA2-2X: ' + str(e)) from e
            return
        require(isinstance(rule, dict) and set(rule) == set(self.s['precision_rule_fields']), 'CA2-05 regla de precisión ausente')
        require(rule['kind'] in self.s['precision_kinds'] and isinstance(rule['selector_rules'], list), 'CA2-05 regla de precisión')
        fields = dict(self.s['selector_rule_fields'])
        if rule['kind'] == 'exact':
            fields.pop('rounding_unit')
        for r in rule['selector_rules']:
            require(isinstance(r, dict) and set(r) == set(fields), 'CA2-05 regla por selector')
            for k,t in fields.items():
                self.c.scalar(r[k], t)
        require([r['selector'] for r in rule['selector_rules']] == selectors, 'CA2-05 precisión no aplicable a todos los selectores')

    def revisions(self, rows, vectors, evidence, receipts, case_statuses):
        for country, year in sorted({(r['country_id'],r['anchor_year']) for r in rows}):
            group = [r for r in rows if (r['country_id'],r['anchor_year']) == (country,year)]
            require(len({(r['d2_vector_id'],r['d6_vector_id']) for r in group}) >= 2, 'CA2-08 faltan revisiones completas')
            changed = False
            for key in ('d2_vector_id','d6_vector_id'):
                vs = {r[key]: vectors[r[key]] for r in group}
                if len(vs) == 1:
                    continue
                changed = True
                require(len({v['source_vintage'] for v in vs.values()}) == len(vs), 'CA2-08 revisión sin vintage distinto')
                snapshots = sorted(v['snapshot_sha256'] for v in vs.values())
                require(len(set(snapshots)) == len(vs), 'CA2-08 snapshots repetidos')
                require(len({tuple(v[k] for k in ('representation','unit','multiplier','accounting_basis')) for v in vs.values()}) == 1, 'CA2-08 revisiones incompatibles')
                for vid in vs:
                    ev = [e for e in evidence[vid] if e['role'] == 'comparability' and e['related_snapshots'] == snapshots]
                    require(len(ev) == 1, 'CA2-08 falta comparabilidad de revisiones')
                    receipt = receipts[ev[0]['evidence_id']]
                    for row in group:
                        case_statuses[row['case_id']].append(receipt['outcome'] if receipt else 'unknown')
            require(changed, 'CA2-08 pares idénticos')

    def chains(self, tables, vectors):
        entries = {e['evidence_id']: e for e in tables['ca2_evidence']}
        scopes = {eid: self.evidence_scope(e, vectors) for eid,e in entries.items()}
        visited, active = set(), set()
        def visit(eid):
            require(eid not in active, 'CA2-10 ciclo de evidencia')
            if eid in visited:
                return
            active.add(eid)
            e = entries[eid]
            refs = self.array(e['against_evidence_ids'], 'id') + ([e['predecessor_id']] if e['predecessor_id'] is not None else [])
            for ref in refs:
                require(ref in entries, 'CA2-10 enlace ausente')
                visit(ref)
            active.remove(eid); visited.add(eid)
        for eid in entries:
            visit(eid)
        for scope in set(scopes.values()):
            roots = [e for eid,e in entries.items() if scopes[eid] == scope and e['relation_kind'] == 'initial']
            require(len(roots) == 1, 'CA2-10 ámbito requiere una raíz inicial única; no omitir predecesor')
        for e in entries.values():
            instant(e['created_at'])
            kind, pred = e['relation_kind'], e['predecessor_id']
            proof_fields = self.s['lineage']['proof_reference_fields']
            if kind == 'successor':
                require(pred is not None, 'CA2-10 sucesión exige predecesor')
                old = entries[pred]
                require(scopes[pred] == scopes[e['evidence_id']], 'CA2-10 predecesor ajeno')
                require(instant(e['created_at']) > instant(old['created_at']), 'CA2-10 fecha posterior requerida')
            else:
                require(pred is None, 'CA2-10 raíz no lleva predecesor de sucesión')
            if kind != 'independent':
                require(not e['against_evidence_ids'] and all(e[k] is None for k in proof_fields), 'CA2-10 prueba de independencia fuera de rol')
                continue
            require(e['against_evidence_ids'] and all(e[k] is not None for k in proof_fields), 'CA2-10 raíz independiente requiere prueba autenticada')
            require(all(scopes[ref] == scopes[e['evidence_id']] for ref in e['against_evidence_ids']), 'CA2-10 independencia de ámbito ajeno')
            raw = self.bytes(e['independence_path'], e['independence_sha256'])
            adapter = self.adapters.get(e['adapter_id'])
            require(adapter is not None and callable(getattr(adapter,'independence',None)), 'CA2-10 adaptador de independencia pendiente')
            proof = adapter.independence(raw)
            expected = {'evidence_id': e['evidence_id'], 'artifact_sha256': e['artifact_sha256'],
                        'scope': dict(zip(self.s['lineage']['scope_fields'], scopes[e['evidence_id']])),
                        'against_records': [{'evidence_id': ref, 'record_sha256': H(entries[ref])} for ref in e['against_evidence_ids']],
                        'outcome': 'pass'}
            require(isinstance(proof,dict) and set(proof) == set(self.s['lineage']['proof_fields']) and proof == expected, 'CA2-10 independencia no acreditada o fuera de alcance')

    def evidence_scope(self, entry, vectors):
        vector = vectors[entry['vector_id']]
        return tuple(entry[k] if k in entry else vector[k] for k in self.s['lineage']['scope_fields'])

    def validate_transition(self, old_raw, expected_old_sha256, new_tables):
        self.c.scalar(expected_old_sha256, 'sha')
        require(sha(old_raw) == expected_old_sha256, 'CA2-10 ancla anterior incorrecta')
        old = strict_json(old_raw, canonical_file=True)
        self.validate(old)
        for table in self.s['tables']:
            pk = self.c.C['tables'][table]['primary_key']
            new = {tuple(r[k] for k in pk): r for r in new_tables[table]}
            for row in old[table]:
                require(new.get(tuple(row[k] for k in pk)) == row, 'CA2-10 sustitución/borrado de antecedente')
        ov = {v['vector_id']:v for v in old['ca2_vectors']}
        nv = {v['vector_id']:v for v in new_tables['ca2_vectors']}
        oe = {e['evidence_id']:e for e in old['ca2_evidence']}
        for e in new_tables['ca2_evidence']:
            if e['evidence_id'] in oe:
                continue
            scope = self.evidence_scope(e,nv)
            prior = {eid for eid,p in oe.items() if self.evidence_scope(p,ov) == scope}
            if e['relation_kind'] == 'initial':
                require(not prior, 'CA2-10 ámbito antecedente: nueva ID no permite raíz inicial')
            elif e['relation_kind'] == 'independent':
                require(prior and prior <= set(e['against_evidence_ids']), 'CA2-10 independencia debe referir todos los antecedentes de su ámbito')
        result = self.validate(new_tables)
        return dict(result, predecessor_bundle_sha256=expected_old_sha256)
