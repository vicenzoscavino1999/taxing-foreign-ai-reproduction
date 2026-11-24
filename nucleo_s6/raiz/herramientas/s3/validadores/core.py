"""Lectores sin escrituras ni evaluación económica. Biblioteca estándar Python 3.12.

Refactoriza canon/decimal, validación de claves, bind_macro y definitions de
la entrega ajuste_contractual 2026-09-12; elimina globals de ruta y fixtures
al importar. El único esquema es el catálogo recibido y CLAVES_DE_CALCULO.
El PASS de estas funciones no es admisión, autoridad, ni validación numérica.
"""
from pathlib import Path
from decimal import Decimal, InvalidOperation
from datetime import datetime
import csv
import hashlib
import io
import json
import math
import re


class ContractError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ContractError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canon(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def H(value):
    return sha(canon(value))


def decimal(value):
    require(type(value) in (str, int, Decimal), 'decimal exacto requerido; float/bool prohibidos')
    try:
        d = Decimal(value)
    except InvalidOperation as e:
        raise ContractError('decimal inválido') from e
    require(d.is_finite(), 'decimal no finito')
    if d == 0:
        return '0'
    s = format(d, 'f')
    return s.rstrip('0').rstrip('.') if '.' in s else s


def strict_json(data, canonical_file=False):
    if isinstance(data, bytes):
        data = data.decode('utf-8')
    def pairs(items):
        result = {}
        for k, v in items:
            require(k not in result, 'miembro JSON duplicado: ' + k)
            result[k] = v
        return result
    def invalid(token):
        raise ContractError('constante JSON no finita: ' + token)
    def finite_float(token):
        value = float(token)
        require(math.isfinite(value), 'número JSON no finito por desbordamiento: ' + token)
        return value
    try:
        result = json.loads(data, object_pairs_hook=pairs, parse_constant=invalid,
                            parse_float=finite_float)
    except (json.JSONDecodeError, UnicodeError) as e:
        raise ContractError('JSON UTF-8 inválido') from e
    if canonical_file:
        require(data.encode('utf-8') == canon(result) + b'\n', 'JSON no canónico con LF único')
    return result


def relative_path(value):
    require(isinstance(value, str) and value and value.isascii(), 'ruta ASCII requerida')
    require(not any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in value), 'ruta no válida')
    require(not value.startswith('/') and '\\' not in value and ':' not in value,
            'ruta absoluta/no POSIX')
    require(all(p not in ('', '.', '..') for p in value.split('/')), 'escape de ruta')
    return value


def inside(root, relative):
    root = Path(root).resolve()
    target = (root / relative_path(relative)).resolve()
    require(target.is_relative_to(root), 'ruta resuelta fuera de raíz')
    return target


class Contracts:
    def __init__(self, catalog, formulas, keys):
        self.C, self.F, self.K = catalog, formulas, keys

    @classmethod
    def load(cls, root, expected_manifest_sha256):
        """Autentica una selección explícita antes de interpretar sus esquemas."""
        verify_manifest(root, expected_manifest_sha256)
        return cls(*(strict_json((Path(root) / 'contratos' / name).read_bytes())
                     for name in ('catalogo_contratos.json', 'formulas.json', 'CLAVES_DE_CALCULO.json')))

    def fields(self, value, fields):
        require(isinstance(value, dict) and set(value) == set(fields), 'campos exactos requeridos')
        for key, typ in fields.items():
            self.key_type(value[key], typ)

    def key_type(self, v, t):
        if t.startswith('literal:'):
            require(v == t[8:], 'literal incompatible')
        elif t == 'canonical_decimal':
            require(isinstance(v, str) and decimal(v) == v, 'decimal no canónico')
        elif t == 'sha':
            require(isinstance(v, str) and re.fullmatch('[0-9a-f]{64}', v), 'hash inválido')
        elif t in ('atom', 'id', 'text', 'project_relative_path'):
            require(isinstance(v, str) and v and v.isascii() and
                    all(32 < ord(c) < 127 for c in v), 'token ASCII sin espacios requerido')
            if t in ('atom', 'id'):
                require(re.fullmatch(self.C['types'][t]['pattern'], v), 'ID inválido')
            if t == 'project_relative_path':
                relative_path(v)
        elif t in ('country', 'design', 'instrument', 'block', 'side'):
            require(v in self.C['types'][t]['enum'], 'enumeración incompatible')
        elif t == 'bool':
            require(type(v) is bool, 'bool requerido')
        elif t == 'value_rows':
            require(isinstance(v, list), 'array requerido')
            for row in v:
                self.fields(row, self.K['shapes']['value_rows']['items'])
            ids = [r['parameter_id'] for r in v]
            require(ids == sorted(set(ids)), 'valores duplicados/desordenados')
        elif t == 'national_dependencies':
            require(isinstance(v, list), 'dependencias array')
            for d in v:
                self.key_type(d, 'dependency')
            require([d['role'] for d in v] == sorted(self.K['shapes'][t]['roles']), 'roles exactos/orden')
        elif t == 'typed_pk_object':
            require(isinstance(v, dict) and v, 'PK no vacío')
            for k, x in v.items():
                self.key_type(k, 'atom')
                require(type(x) in (str, int), 'PK scalar tipado sin null/float/bool')
        elif t in self.K['schemas']:
            self.key(t, v)
        elif t in self.K['shapes']:
            self.fields(v, self.K['shapes'][t]['fields'])
        else:
            raise ContractError('tipo de clave no soportado: ' + t)

    def key(self, kind, payload, expected=None):
        require(kind in self.K['schemas'], 'esquema de clave desconocido')
        self.fields(payload, self.K['schemas'][kind]['fields'])
        projections = {'common_values': 'common_primitive_ids', 'structural': 'structural_primitive_ids',
                       'macro': 'macro_primitive_ids'}
        if kind in projections:
            require([r['parameter_id'] for r in payload['values']] == self.K[projections[kind]],
                    'proyección de primitivas incompatible')
            for r in payload['values']:
                require(r['value_unit'] == self.F['parameters'][r['parameter_id']]['unit'],
                        'unidad de primitiva incompatible')
        if kind == 'structural':
            d = payload['tau_domain']
            for axis in ('d', 'f'):
                lo, hi = (Decimal(d[f'tau_{axis}_{x}']) for x in ('lower', 'upper'))
                require(0 <= lo <= hi < 1, 'dominio fiscal inválido')
                require(lo != hi or d[f'tau_{axis}_lower_closed'] and d[f'tau_{axis}_upper_closed'],
                        'singleton abierto/vacío')
                if payload['instrument_j'] in ('d', 'f') and payload['instrument_j'] != axis:
                    require(lo == hi == 0, 'menú exige tasa ausente igual a cero')
        if kind == 'macro':
            dep = next(d for d in payload['national_dependencies'] if d['role'] == 'joint_domain')
            require(dep['artifact_sha256'] == payload['national_state']['joint_domain_sha256'],
                    'dominio conjunto incompatible')
        digest = H(payload)
        if expected is not None:
            self.key_type(expected, 'sha')
            require(digest == expected, 'hash no corresponde a preimagen')
        return digest

    def bind_context(self, common, identity, cell, macro, frontier):
        """Comprueba proyecciones y joins. No autentica fuentes ni calcula shares."""
        common_hash = self.key('common_values', common)
        omega_hash = self.key('omega_identity', identity)
        require(identity['primitive_values_sha256'] == common_hash, 'omega/preimagen alterado')
        require(cell['omega_id'] == 'OMG:' + omega_hash, 'omega incompatible')
        mp, sp = macro['macro_key_payload'], frontier['structural_key_payload']
        self.key('macro', mp, macro['macro_key_sha256'])
        self.key('structural', sp, frontier['structural_key_sha256'])
        for payload, ids in ((mp, 'macro_primitive_ids'), (sp, 'structural_primitive_ids')):
            expected = [r for r in common['values'] if r['parameter_id'] in self.K[ids]]
            require(payload['values'] == expected, 'valores de contexto no coinciden con omega')
        for k in ('country_id', 'omega_id', 'run_id', 'eta_w_block', 'national_state_sha256'):
            require(cell[k] == macro[k], 'cruce de contexto macro: ' + k)
        for k in ('country_id', 'eta_w_block'):
            require(macro[k] == mp[k], 'columna/payload macro: ' + k)
        require(cell['expected_macro_key_sha256'] == macro['macro_key_sha256'], 'macro esperado distinto')
        require(macro['national_state_sha256'] == H(mp['national_state']), 'estado nacional alterado')
        for k in ('country_id', 'omega_id', 'run_id', 'design_v', 'instrument_j',
                  'availability_case_id', 'availability_matrix_hash'):
            require(cell[k] == frontier[k], 'cruce de contexto frontera: ' + k)
        for k in ('design_v', 'instrument_j'):
            require(frontier[k] == sp[k], 'columna/payload estructural: ' + k)
        vals = {r['parameter_id']: r['value'] for r in common['values']}
        for axis in ('d', 'f'):
            cap = vals['bar_tau_' + axis] if sp['instrument_j'] in (axis, 'df') else '0'
            require(sp['tau_domain']['tau_' + axis + '_upper'] == cap, 'tope fiscal/omega incompatible')
        for r in mp['values']:
            if r['parameter_id'] in macro:
                require(decimal(macro[r['parameter_id']]) == r['value'], 'columna macro/valor discordante')
        for k, v in mp['national_state']['shares'].items():
            if k in macro:
                require(decimal(macro[k]) == v, 'columna macro/share discordante')

    def point(self, payload, structural):
        self.key('point', payload)
        require(payload['structural_key_sha256'] == self.key('structural', structural), 'punto/estructura')
        for axis in ('d', 'f'):
            v = Decimal(payload['tau_' + axis]); d = structural['tau_domain']
            lo, hi = (Decimal(d[f'tau_{axis}_{x}']) for x in ('lower', 'upper'))
            require(lo <= v <= hi, 'punto fuera de dominio')
            if payload['side'] == 'point':
                require(v != lo or d[f'tau_{axis}_lower_closed'], 'punto en borde abierto')
                require(v != hi or d[f'tau_{axis}_upper_closed'], 'punto en borde abierto')
        # La existencia económica de branch_id/lateral corresponde al solver futuro.

    def definitions(self, doc=None):
        doc = self.F if doc is None else doc
        pars, defs = doc['parameters'], doc['formulas']
        for p, d in pars.items():
            if d['role'] == 'derived':
                key = d.get('formula_id')
                require(key in defs, 'derivado sin definición: ' + p)
                require(defs[key]['output_parameter_id'] == p and defs[key]['unit'] == d['unit'],
                        'unidad/output de definición incompatible: ' + p)
        result_fields = {(d['result_binding']['table'], d['result_binding']['value_field'])
                         for d in defs.values() if d.get('result_binding')}
        for n, d in defs.items():
            require(d['output_parameter_id'] in pars and all(p in pars for p in d['inputs']), 'referencia de fórmula')
            require(d['declaration_only_in_D7'] is True, 'D7 no puede exigir evaluación B')
            require(d['definition_kind'] in ('algebraic_expression', 'numerical_function', 'numerical_operator'),
                    'tipo de definición')
            require(len(d['inputs']) == len(set(d['inputs'])), 'input de fórmula duplicado')
            seen = set()
            for q in d['context_inputs']:
                require(set(q) == {'table', 'field'}, 'contexto exacto')
                require(q['table'] in self.C['tables'], 'tabla contexto desconocida')
                fields = {c['name'] for c in self.C['tables'][q['table']]['columns']}
                require(q['field'] in fields, 'campo contexto desconocido')
                pair = (q['table'], q['field'])
                require(pair not in seen and pair not in result_fields, 'resultado B como entrada D7/ciclo')
                # Contexto declarativo B solo de las tablas de contexto, nunca salidas computadas.
                if self.C['tables'][q['table']]['family'] == 'B':
                    require(q['table'] in ('omega', 'cell_context', 'frontier_context'), 'entrada requiere resultados B')
                seen.add(pair)
            b = d.get('result_binding')
            if b:
                require(b['table'] in self.C['tables'], 'tabla destino desconocida')
                tab = self.C['tables'][b['table']]
                require(tab['family'] == b['family'] and tab['primary_key'] == b['key_fields'], 'destino/PK incompatible')
                cols = {x['name']: x for x in tab['columns']}
                require(b['value_field'] in cols and cols[b['value_field']]['unit'] == b['stored_unit'], 'unidad almacenada incompatible')
                if b['stored_unit'] == d['unit']:
                    require(b['scale_to_declared_unit'] == '1', 'conversión espuria')
                else:
                    require(n == 'R' and b['stored_unit'] == 'normalized_flow' and d['unit'] == 'flow'
                            and b['scale_to_declared_unit'] == 'gamma*z_m', 'conversión no declarada')
        active, done = set(), set()
        def visit(n):
            if n in done:
                return
            require(n not in active, 'ciclo de definiciones')
            active.add(n)
            for p in defs[n]['inputs']:
                if pars[p]['role'] == 'derived':
                    visit(pars[p]['formula_id'])
            active.remove(n); done.add(n)
        for n in defs:
            visit(n)
        c2 = defs['C_2']
        require(c2['definition_kind'] == 'numerical_operator' and c2['operator'] == 'supremum', 'C_2 debe declarar supremo')
        require(c2['inputs'] == ['R', 'B_pot', 'bar_tau_d', 'bar_tau_f'], 'inputs C_2')
        require(defs['R']['definition_kind'] == 'numerical_function' and pars['R']['value_kind'] == 'numeric_function', 'R funcional')
        require(c2['result_binding']['table'] == 'capture_ceiling_result', 'destino C_2')
        return sorted(done)

    def scalar(self, value, typ):
        spec = self.C['types'][typ]
        if typ == 'json':
            canon(value)
            return
        if spec['type'] == 'decimal':
            self.key_type(value, 'canonical_decimal'); d = Decimal(value)
            for k, compare in (('minimum', lambda a,b:a>=b), ('maximum', lambda a,b:a<=b),
                               ('exclusiveMinimum', lambda a,b:a>b)):
                if k in spec:
                    require(compare(d, Decimal(str(spec[k]))), 'dominio escalar')
        elif spec['type'] == 'integer':
            require(type(value) is int and value >= spec.get('minimum', 0), 'entero tipado')
        elif spec['type'] == 'boolean':
            require(type(value) is bool, 'booleano tipado')
        else:
            require(isinstance(value, str) and len(value) >= spec.get('minLength', 1), 'cadena requerida')
            if 'pattern' in spec:
                require(re.fullmatch(spec['pattern'], value), 'patrón incompatible')
            if 'enum' in spec:
                require(value in spec['enum'], 'enum incompatible')
            if spec.get('relativePOSIX'):
                relative_path(value)
            if spec.get('format') == 'date-time-zone':
                require(datetime.fromisoformat(value).tzinfo is not None, 'fecha sin zona')
            if spec.get('format') == 'exact-date-time-zone':
                from .temporal import instant
                instant(value)

    def table(self, name, rows):
        tab = self.C['tables'][name]; cols = {c['name']: c for c in tab['columns']}
        for row in rows:
            require(set(row) == set(cols), 'columnas exactas: ' + name)
            for k, v in row.items():
                if v is None:
                    require(cols[k]['nullable'], 'null prohibido: ' + k)
                else:
                    self.scalar(v, cols[k]['type'])
        for keys in [tab['primary_key']] + tab['unique']:
            tuples = [tuple(r[k] for k in keys) for r in rows]
            require(all(all(v is not None for v in x) for x in tuples) if keys == tab['primary_key'] else True,
                    'PK null')
            require(len(tuples) == len(set(tuples)), 'PK/UK duplicada')
        order = tab['order_by']
        def typed(row):
            return tuple(Decimal(row[k]) if cols[k]['type'] in ('dec','positive','rate') else row[k] for k in order)
        require(rows == sorted(rows, key=typed), 'orden de filas no canónico')
        return rows

    def read_csv(self, path, name):
        raw = Path(path).read_bytes()
        require(raw.endswith(b'\n') and not raw.endswith(b'\n\n') and b'\r' not in raw and not raw.startswith(b'\xef\xbb\xbf'),
                'CSV UTF-8 LF único sin BOM requerido')
        reader = csv.reader(io.StringIO(raw.decode('utf-8'), newline=''), strict=True)
        tab = self.C['tables'][name]; columns = tab['columns']
        require(next(reader, None) == [c['name'] for c in columns], 'encabezado exacto')
        rows = []
        for items in reader:
            require(len(items) == len(columns), 'ancho CSV incorrecto')
            row = {}
            for c, s in zip(columns, items):
                v = s
                if s == '':
                    v = None
                elif c['type'] == 'int':
                    require(re.fullmatch('0|[1-9][0-9]*', s), 'serialización int'); v = int(s)
                elif c['type'] == 'bool':
                    require(s in ('true','false'), 'serialización bool'); v = s == 'true'
                elif c['type'] == 'json':
                    v = strict_json(s)
                    require(canon(v).decode() == s, 'JSON en CSV no canónico')
                row[c['name']] = v
            rows.append(row)
        return self.table(name, rows)

    def references(self, tables):
        """Relaciones PK/FK declaradas, sin interpretar reglas económicas en prosa."""
        for name, rows in tables.items():
            self.table(name, rows)
            for fk in self.C['tables'][name]['foreign_keys']:
                require(fk['table'] in tables, 'tabla FK no proporcionada: ' + fk['table'])
                targets = {tuple(r[k] for k in fk['target_columns']) for r in tables[fk['table']]}
                for row in rows:
                    values = tuple(row[k] for k in fk['columns'])
                    if all(v is None for v in values) and fk['nullable']:
                        continue
                    require(None not in values and values in targets, 'referencia FK huérfana: ' + name)

    def reference(self, root, dependency, table_name, inventory_reader, country=None, unit=None):
        """Autentica bytes y PK. Adaptador explícito del manifest de cada familia.

        inventory_reader recibe bytes YA autenticados y devuelve (raíz relativa
        del archivo, lista files del contrato correspondiente). No elige activos.
        Esta ronda implementa el adaptador de inventario integrado, no D2/D6 legado.
        """
        self.key_type(dependency, 'dependency')
        mpath = inside(root, dependency['manifest_path']); raw = mpath.read_bytes()
        require(sha(raw) == dependency['manifest_sha256'], 'manifest de referencia alterado')
        family_root, entries = inventory_reader(raw, mpath, Path(root))
        apath = inside(root, dependency['artifact_path'])
        matches = [e for e in entries if inside(family_root, e['path']) == apath]
        require(len(matches) == 1, 'archivo no resuelve de forma única en manifest')
        e = matches[0]; data = apath.read_bytes()
        require(sha(data) == e['sha256'] == dependency['artifact_sha256'] and len(data) == e['bytes'], 'archivo/hash/bytes incompatible')
        tab = self.C['tables'][table_name]; pk = dependency['record_pk']
        require(set(pk) == set(tab['primary_key']), 'PK referida incompatible')
        cols = {c['name']: c for c in tab['columns']}
        for k, v in pk.items():
            self.scalar(v, cols[k]['type'])
        rows = self.read_csv(apath, table_name)
        require(e.get('rows') == len(rows), 'recuento de filas incompatible')
        found = [r for r in rows if all(r[k] == v for k, v in pk.items())]
        require(len(found) == 1, 'registro referido ausente/ambiguo')
        row = found[0]
        if country is not None:
            require(row.get('country_id') == country, 'país de registro autenticado incompatible')
        if unit is not None:
            actual_unit = row.get('unit', row.get('value_unit', cols.get('value', {}).get('unit')))
            require(actual_unit == unit, 'unidad de referencia incompatible')
        return row

    def technical(self, payload, root, dependencies):
        """Resolución explícita por roles input_dependencies; no verifica consentimiento."""
        self.key_type(payload, 'technical')
        for key, expected in payload.items():
            role = key.removesuffix('_sha256')
            candidates = [d for d in dependencies if d['role'] == role]
            require(len(candidates) == 1, 'dependencia técnica ausente/ambigua: ' + role)
            dep = candidates[0]
            require(dep['sha256'] == expected and sha(inside(root, dep['path']).read_bytes()) == expected,
                    'bytes técnicos incompatibles: ' + role)


def integrated_inventory(raw, manifest_path, project_root):
    """Lee files del contrato integrado; comprueba árbol, sin aprobar la familia."""
    doc = strict_json(raw, canonical_file=True)
    entries = doc['files']
    require(isinstance(entries, list), 'files debe ser lista')
    paths = [e['path'] for e in entries]
    require(paths == sorted(set(paths)), 'inventario duplicado/desordenado')
    for e in entries:
        require(set(e) == {'path','sha256','bytes','rows'}, 'entrada files exacta')
        relative_path(e['path'])
        require(type(e['bytes']) is int and e['bytes'] >= 0, 'bytes entero')
        require(isinstance(e['sha256'], str) and re.fullmatch('[0-9a-f]{64}', e['sha256']), 'SHA files')
        require(e['rows'] is None or type(e['rows']) is int and e['rows'] >= 0, 'rows entero/null')
        require(Path(e['path']).name not in (manifest_path.name, 'active_product.json', 'promotion_receipt.json'), 'archivo excluido en árbol')
    require(doc['tree_sha256'] == H([{k:e[k] for k in ('path','sha256','bytes')} for e in entries]), 'tree hash alterado')
    return manifest_path.parent, entries


def verify_manifest(root, expected_sha256):
    root = Path(root)
    raw = (root / 'contratos/contract_manifest.json').read_bytes()
    require(sha(raw) == expected_sha256, 'ancla de manifest normativo incompatible')
    m = strict_json(raw)
    require(m['path_base'] == 'delivery_root' and m['self_excluded'] is True, 'base/autorreferencia normativa')
    files = m['files']
    required = {p.relative_to(root).as_posix() for p in (root/'contratos').iterdir() if p.is_file() and p.name != 'contract_manifest.json'}
    required.update('candidatos/' + name for name in ('PLAN_DISENO_INTEGRADO_BORRADOR.md',
                    'PLAN_BASE_DE_DATOS_INTEGRADO_BORRADOR.md', 'PLAN_REPRODUCCION_INTEGRADO_BORRADOR.md'))
    required.add('review/ESTRATEGIA_DE_CALCULO.md')
    required.add('review/CONTINGENCIA_A2.md')
    require(set(files) == required, 'cobertura normativa exacta incompatible')
    require('contratos/contract_manifest.json' not in files, 'manifest autorreferente')
    for rel, meta in files.items():
        require(set(meta) == {'sha256','bytes'} and type(meta['bytes']) is int, 'metadatos de inventario')
        data = inside(root, rel).read_bytes()
        require(sha(data) == meta['sha256'] and len(data) == meta['bytes'], 'integridad normativa: ' + rel)
        require(expected_sha256.encode() not in data, 'ciclo de hash normativo')
    return m


# ---------------------------------------------------------------------------------------------------------------------
# CANDIDATO PASO 4 (CONTRATO PAQUETE 3.7, NO OFICIAL; copia aislada; no incorporado): E14 para paquetes por SELECCIÓN.
def validar_paquete_seleccion(pdir, ref=None, V=None) -> dict:
    """E14 candidato por la RUTA COMÚN, que vive junto a este archivo (paquete_seleccion.py) con sus reglas de contenido
    en el núcleo candidato (paper2b/contrato_paquete.py). Dependencias INYECTADAS (y autenticadas por la ruta):
    flujo, generador, tabla v3 y contexto S5 del ÁREA (codigo/flujo_paso4_v2.py y lo que declara en CODIGO), que todavía
    no tienen equivalente en los archivos oficiales. Sin `ref` el resultado es PARCIAL (cumple = False, completa = False).
    Nunca habilita official(): la ruta rechaza cualquier petición oficial (OFICIAL_NO_AUTORIZADO)."""
    import importlib.util as _ilu
    import sys as _sys
    _n = "cand_seleccion_paso4"
    if _n not in _sys.modules:                         # punto de entrada CANDIDATO: provee las dependencias de la ruta
        _sp = _ilu.spec_from_file_location(_n, Path(__file__).resolve().parents[2] / "b/seleccion_paso4.py")
        _m = _ilu.module_from_spec(_sp)
        _sys.modules[_n] = _m
        _sp.loader.exec_module(_m)
    _FP = _sys.modules[_n]
    PS = _FP.P2
    if Path(PS.__file__).resolve() != Path(__file__).with_name("paquete_seleccion.py").resolve():
        raise RuntimeError("RUTA_COMUN_NO_CANDIDATA: %s" % PS.__file__)
    if V is None and ref is not None:
        V = _FP.verificador(ref.ctx, ref)
    return PS.validar(pdir, ref, V)
