"""Validacion PROD: esquema, relaciones, identidad, testigos y estados separados; sin calculo cientifico."""
from __future__ import annotations

import sys
from pathlib import Path

INSTALACION = Path(__file__).resolve().parents[2]
ESTRUCTURALES = ("a", "rho", "kappa_tilde")


def identidad():
    import hashlib
    return {"archivo": "herramientas/b/validador_prod.py", "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


import copy, json, math, hashlib
from decimal import Decimal
CONTRATO = '7bde9f1549e7c3903a88b41ac1896d81bf8c5eeb1ebee7bd6e960bb5ea2286bb'
PI = ('pi_iva', 'pi_otros_productos', 'pi_produccion')

def raiz_contratos():
    """rem64 (P4-P2-ACEPTACION-IMPORTACION): raíz con los contratos G-NA-1 y los validadores comunes (herramientas.s3 / bloque2) que usa este
    validador, IMPORTABLE también en el proceso de la aceptación común, que no construye el contexto (el trabajador la recibe de
    SP.configurar, que añade raiz_proyecto al final de sys.path: aquí se añade igual)."""
    root = next(p for p in INSTALACION.parents if (p/'herramientas/bloque2/contratos_g_na_1').is_dir())
    if str(root) not in sys.path:
        sys.path.append(str(root))
    return root

def contratos_instalados():
    root = raiz_contratos()
    from herramientas.s3.validadores.core import Contracts
    return Contracts.load(root/'herramientas/bloque2/contratos_g_na_1', CONTRATO)

def identidad_claim(cid):
    p = cid.split(':')
    if len(p) != 11 or p[0] != 'CLM' or p[3] != 'ci':
        raise ValueError('CLAIM_FUERA_DE_SELECCION_CI_INSTALADA')
    return dict(country_id=p[4], instrument_j=p[5], availability_case_id=p[6], design_v=p[7], bound_variant=p[8], eta_w_block=p[9], layer=p[10], claim_scope='country_instrument')

def _evaluadores_ra():
    """rem63: el adaptador R-A INSTALADO junto a este validador (el mismo módulo que carga el trabajador)."""
    import importlib.util
    f=INSTALACION/'herramientas/b/evaluadores_ra.py'
    m=sys.modules.get('evaluadores_ra')
    if m is None or Path(m.__file__).resolve()!=f.resolve():
        sp=importlib.util.spec_from_file_location('evaluadores_ra',f);m=importlib.util.module_from_spec(sp);sys.modules['evaluadores_ra']=m;sp.loader.exec_module(m)
    return m

class ValidadorProdS6:
    """Esquema/FK autenticos y vinculacion exacta; sin evaluar ciencia nueva."""
    def __init__(self, ctx, contracts=None, esperado=None, modo_arnes=False):
        """rem64: `esperado` = vínculo EFECTIVO que fija QUIEN valida (trabajador: sus identidades verificadas; aceptación común: plan,
        tarea, despliegue y entradas ADMITIDOS), nunca leído del producto; cada campo del vínculo del documento debe coincidir."""
        sys.path.insert(0, str(INSTALACION/'src'))
        from paper2b import rules
        self.RU, self.ctx = rules, ctx
        self.esperado = dict(esperado or {})
        self.modo_arnes = bool(modo_arnes)     # rem64: evidencia con origen declarado (réplica/reutilización) solo en arnés
        self.C = contracts if contracts is not None else ctx.C
        lista=json.loads((INSTALACION/'datos/paso4/lista_PROD.json').read_bytes())
        ref=lista['fuentes']['registro']
        root=raiz_contratos()
        ent=root/'tmp'/ref['entrega'];raw=(ent/ref['archivo']).read_bytes()
        if hashlib.sha256((ent/'audit/entrega.json').read_bytes()).hexdigest()!=ref['inventario_sha256'] or hashlib.sha256(raw).hexdigest()!=ref['sha256']:
            raise ValueError('LINEA_BASE_HISTORICA_NO_AUTENTICA')
        self.baseline=json.loads(raw)['afirmaciones']


    def unidad(self, spec, doc, filas):
        try:
            return self._unidad(spec, doc, filas)
        except (OSError, ValueError, TypeError, KeyError, IndexError, ArithmeticError) as e:
            return dict(clasificacion='rechazada', motivos=['CONTRATO: '+str(e)[:250]])

    def _unidad(self, spec, doc, filas):
        from herramientas.s3.validadores.core import Contracts, decimal
        def need(ok, msg):
            if not ok: raise ValueError(msg)
        lista = json.loads((INSTALACION/'datos/paso4/lista_PROD.json').read_bytes())
        need(spec == {s['id']:s for s in lista['unidades']}.get(spec.get('id')), 'ESPECIFICACION_NO_INSTALADA')
        need(all(doc.get(k)==spec[k] for k in ('id','familia','afirmacion')), 'DOCUMENTO_DE_OTRA_UNIDAD')
        need(doc.get('especificacion')==spec, 'DOCUMENTO_SIN_ASIGNACION_EXACTA')
        ident = identidad_claim(spec['afirmacion'])
        brk = spec['familia'] in ('PROD1','PROD2')
        ER = _evaluadores_ra()
        # rem63/rem64: producto del evaluador R-A INSTALADO, ligado al contexto y vínculo EFECTIVOS de quien valida y a su propia evidencia
        need(doc.get('origen')=='evaluadores_ra' and doc.get('evaluador')==ER.identidad(), 'EVALUADOR_RA_NO_INSTALADO')
        vin=doc.get('vinculo') or {}
        need(vin.get('contexto_identidad_sha256') and vin.get('contexto_identidad_sha256')==getattr(self.ctx,'identity_sha256',None), 'CONTEXTO_AJENO')
        need(self.esperado, 'VINCULO_ESPERADO_NO_FIJADO_POR_QUIEN_VALIDA')
        for k,v in sorted(self.esperado.items()):
            need(vin.get(k)==v, 'VINCULO_AJENO: '+k)
        ev=doc.get('evidencia_ra') or {}
        need(self.modo_arnes or 'origen_evidencia' not in ev, 'EVIDENCIA_NO_PRODUCIDA_EN_ESTA_EJECUCION: '+str(ev.get('origen_evidencia'))[:60])
        if brk:
            need(ev.get('afirmacion')==spec['afirmacion'] and ev.get('eje')==spec['parametro'] and ev.get('direccion')==spec['direccion'], 'EVIDENCIA_DE_OTRA_BUSQUEDA')
        else:
            need(ev.get('afirmacion')==spec['afirmacion'] and vin.get('decision_q') is not None, 'EVIDENCIA_Q_DE_OTRA_AFIRMACION_O_SIN_DECISION')
        need(not doc.get('rechazo_tecnico'), 'RECHAZO_TECNICO: '+str(doc.get('rechazo_tecnico'))[:200])
        name = 'support_breakdown_result' if brk else 'external_requirement_sensitivity_result'
        otro = 'external_requirement_sensitivity_result' if brk else 'support_breakdown_result'
        need(len(filas.get(name,[]))==1 and not filas.get(otro), 'COBERTURA_DISTINTA')
        need(set(filas)<={name,otro,'claims','witness_sets','breakdown_witnesses','omega','omega_values'}, 'TABLA_AJENA')
        b=filas[name][0]
        need(b['claim_id']==spec['afirmacion'] and all(b.get(k)==v for k,v in ident.items() if k not in ('layer','claim_scope')), 'IDENTIDAD_DE_RESULTADO_DISTINTA')
        need(len(filas.get('claims',[]))==1, 'CLAIM_DEL_PRODUCTOR_REQUERIDO')
        cl=filas['claims'][0]
        need(cl['claim_id']==spec['afirmacion'] and all(cl.get(k)==v for k,v in ident.items() if k!='design_v'), 'CLAIM_IDENTIDAD_DISTINTA')
        quant=json.loads(cl['quantifier'])
        need(quant.get('design')==ident['design_v'] and quant.get('countries')==[ident['country_id']] and quant.get('instruments')==[ident['instrument_j']], 'CUANTIFICADOR_DISTINTO')
        need(cl['predicate']=='SIGN_UNIFORM_VERDICT_17', 'PREDICADO_DISTINTO')
        need(self.baseline[spec['afirmacion']]['categoria']=='robusta_infactible_certificada' and cl['baseline_status']=='verified', 'LINEA_BASE_DISTINTA_DE_LA_SELECCION_CERTIFICADA')
        if b['computation_status']=='not_applicable':
            need(b['status']=='not_applicable_support_gap' and spec.get('parametro')=='eta_w' and ((ident['eta_w_block']=='micro' and spec['direccion']=='superior') or (ident['eta_w_block']=='macro' and spec['direccion']=='inferior')), 'NA_NO_APLICA_A_ESTA_ASIGNACION')
        tables=copy.deepcopy(filas)
        for tn,rows in tables.items():
            for row in rows:
                for col in self.C.C['tables'][tn]['columns']:
                    v=row.get(col['name'])
                    if v is not None and self.C.C['types'][col['type']]['type']=='decimal':
                        need(type(v) in (str,int,float), 'DECIMAL_INVALIDO')
                        if isinstance(v,float): need(math.isfinite(v), 'VALOR_NO_FINITO')
                        row[col['name']]=decimal(str(v) if isinstance(v,float) else v)
            self.C.table(tn,rows)
        d7=None
        usados={w['omega_id'] for w in tables.get('breakdown_witnesses',[]) if w.get('omega_id')}
        need({o['omega_id'] for o in tables.get('omega',[])}==usados, 'OMEGA_AUSENTE_O_AJENO')
        need(all(v['omega_id'] in usados for v in tables.get('omega_values',[])), 'VALOR_OMEGA_HUERFANO')
        if usados:
            from herramientas.bloque2 import familias as FAM
            from paper2b.d7view import D7View
            need(hashlib.sha256(Path(FAM.__file__).read_bytes()).hexdigest()=='1e4fcbc03157f82814d8b7966c67f1a4fbc724052e3af869e48a30e7af9b9e21', 'VERIFICADOR_D7_AJENO')
            ref=doc['d7_evidencia'];v=Path(ref['version'])
            info=FAM.verify_version(v,'D7',expected_tree=ref['arbol'])
            m=info['manifest']
            need(m['authority_package_sha256']==ref['s6_package'] and m['contract_sha256']==CONTRATO and m['phase_status']=='complete', 'D7_NO_AUTENTICO_COMPLETO')
            need(m['producer_sha256']=='387c12bed46a89ad467546d4b07e770b87996e9d97429dabf2a88da21b940ebe', 'PRODUCTOR_D7_AJENO')
            d7=D7View.load(self.C,v)
            need(d7.phase.get('ready_for_b') is True and d7.phase.get('hard_fail_count')==0, 'D7_NO_LISTO')
            for o in tables['omega']:
                need(o['domain_status']=='admissible', 'TESTIGO_OMEGA_EXCLUIDO')
                need(o['support_set_id'] in quant.get('support_sets',[]), 'OMEGA_FUERA_DEL_CLAIM')
            need('omega_values' in tables, 'OMEGA_SIN_VALORES')
        # Proyeccion contractual: no exigir tablas ajenas al producto. Parametros
        # contra formulas autenticas, omega requerido solo si efectivamente usado.
        cat=copy.deepcopy(self.C.C)
        for tn,rows in tables.items():
            fks=[]
            for fk in cat['tables'][tn]['foreign_keys']:
                if fk['table']=='parameter_registry':
                    for row in rows:
                        pid=row[fk['columns'][0]]
                        need(pid is None or pid in self.C.F['parameters'], 'PARAMETRO_NO_CONTRACTUAL')
                elif any(any(row[k] is not None for k in fk['columns']) for row in rows) or fk['table'] in tables:
                    fks.append(fk)
            cat['tables'][tn]['foreign_keys']=fks
        Contracts(cat,self.C.F,self.C.K).references(dict(d7.tables,**tables) if d7 else tables)
        tables.setdefault('support_breakdown_result', [])
        tables.setdefault('external_requirement_sensitivity_result', [])
        ch=self.RU.Checker(tables,self.C,d7); ch.claims()
        if d7:ch.omega()
        need(not ch.errors, 'REGLAS: '+str(ch.errors[:8]))
        need(Decimal(str(b['epsilon_econ']))==Decimal('0.01'), 'EPSILON_DISTINTO')
        if brk:
            pid=spec['parametro']; joint=pid=='pi_joint'
            direccion='superior' if pid=='eta_H' else spec['direccion']  # RB.ladder_search, enum contractual
            need(b['parameter_id']==(None if joint else pid) and b['direction']==direccion, 'FILA_DE_OTRA_BUSQUEDA')
            block='tecnologia' if pid in ESTRUCTURALES else ('incidencia_laboral' if pid in ('eta_w','eta_H') else 'cuna_tributaria')
            need(b['block_id']==block and b['joint_breakdown']==joint, 'BLOQUE_O_CONJUNTO_DISTINTO')
            need(b['component_id']==(pid.split('_',1)[1] if pid.startswith('pi_') and not joint else None), 'COMPONENTE_DISTINTO')
            need(float(b['support_low_primary'])<=float(b['support_high_primary']), 'SOPORTE_INVERTIDO')
            need(float(b['expansion_factor_r'])>=1, 'FACTOR_FUERA_DOMINIO')
            if b['reached_expansion_factor'] is not None: need(float(b['reached_expansion_factor'])>=1, 'FACTOR_ALCANZADO_FUERA_DOMINIO')
            need(not(pid in ESTRUCTURALES and b['status']=='declared_ladder_exhausted_no_breakdown'), 'E16_AGOTAMIENTO_ESTRUCTURAL_PUBLICADO_COMO_AUSENCIA')
            if b['r_critical'] is not None: need(1<=float(b['r_critical'])<=float(b['expansion_factor_r']), 'CRITICO_FUERA_DOMINIO_EVALUADO')
            need(b['status']==ev.get('status') and b['computation_status']==ev.get('computation_status'), 'RESULTADO_DESLIGADO_DE_LA_EVIDENCIA')
            need((b['r_critical'] is None and (ev.get('status')!='breakdown_found' or ev.get('r_critical') is None)) or
                 (ev.get('r_critical') is not None and Decimal(str(b['r_critical']))==Decimal(str(ev['r_critical']))), 'CRITICO_DESLIGADO_DE_LA_EVIDENCIA')
            from types import SimpleNamespace
            try:
                esperado=ER.testigos_contrato(spec['familia'],spec,SimpleNamespace(witnesses=ev.get('witnesses') or []),None)
            except ER.TestigoNoSerializable as e:
                need(False, 'TESTIGO_NO_SERIALIZABLE: '+str(e)[:120])
            got=[(w['parameter_id'],Decimal(str(w['value']))) for w in sorted(tables.get('breakdown_witnesses',[]),key=lambda w:(w['component_index'],w['witness_index']))]
            need(got==[(w['parameter_id'],Decimal(str(w['value']))) for w in esperado], 'TESTIGO_DESLIGADO_DE_LA_EVIDENCIA')
        else:
            need([b['scale_scope'],b['scale_country_id']]==spec['ambito'] and b['claim_scope']==ident['claim_scope'], 'AMBITO_Q_DISTINTO')
            if b['m_Q_critical'] is not None: need(0<=float(b['m_Q_critical'])<=1, 'Q_FUERA_DOMINIO')
            # rem64: la fila Q se RECALCULA desde la evidencia continua con la decisión sellada que cita el documento
            # rem65 (P4-P2-Q-VALIDACION-EVIDENCIA): coherencia de la evidencia (ER.coherencia_q dentro de mapear_q; D frente al contexto si quien
            # valida lo dispone) y fila Y TESTIGO publicados iguales a los derivados
            try:
                fq=ER.mapear_q(vin.get('decision_q'),spec,ev,ident,getattr(getattr(self.ctx,'inp',None),'dme_gai',None))
            except ValueError as e:
                need(False, 'Q_NO_REPRESENTABLE: '+str(e)[:160])
            for k in ('m_Q_critical','reduction_from_reported','status','computation_status','reason_code'):
                need(str(b.get(k))==str(fq['fila'].get(k)), 'Q_DESLIGADO_DE_LA_EVIDENCIA: '+k)
            wq=tables.get('breakdown_witnesses',[])
            if fq['testigo'] is None:
                need(not wq and b.get('witness_set_id') is None, 'TESTIGO_Q_SIN_DERIVACION')
            else:
                need(len(wq)==1 and wq[0]['parameter_id']==fq['testigo']['parameter_id'] and Decimal(str(wq[0]['value']))==Decimal(str(fq['testigo']['value']))
                     and wq[0].get('omega_id') is None, 'TESTIGO_Q_DISTINTO_DEL_DERIVADO')
        ws=b.get('witness_set_id'); sets=tables.get('witness_sets',[]); ww=tables.get('breakdown_witnesses',[])
        if ws is None:
            need(not sets and not ww, 'TESTIGOS_HUERFANOS')
        else:
            scope='support_breakdown' if brk else 'external_requirement'
            need(len(sets)==1 and sets[0]['witness_set_id']==ws and sets[0]['scope']==scope, 'CONJUNTO_TESTIGO_AJENO')
            need(spec['afirmacion'] in sets[0]['definition'], 'TESTIGO_DE_OTRO_CLAIM')
            need(ww and all(w['witness_set_id']==ws for w in ww), 'TESTIGO_VACIO_O_AJENO')
            params=set(PI) if spec.get('parametro')=='pi_joint' else {spec.get('parametro','gain_share')}
            presentes={w['parameter_id'] for w in ww}
            permitidos=params|({'eta_w','eta_H'} if brk else set())
            need(params<=presentes<=permitidos, 'PRIMITIVAS_TESTIGO_DISTINTAS')
            components={w['component_index'] for w in ww}
            need(components==set(range(b.get('n_components') or 1)), 'COMPONENTES_TESTIGO_DISTINTOS')
            for c in components:
                rows=[w for w in ww if w['component_index']==c]
                need(params<={w['parameter_id'] for w in rows}<=permitidos, 'COMPONENTE_INCOMPLETO')
                ix={w['witness_index'] for w in rows}
                need(ix==set(range(max(ix)+1)), 'INDICES_TESTIGO_DISCONTINUOS')
            for w in ww:
                v=float(w['value']); pid=w['parameter_id']
                if w.get('omega_id'):
                    ov=[z for z in tables['omega_values'] if z['omega_id']==w['omega_id'] and z['parameter_id']==pid]
                    need(len(ov)==1 and Decimal(ov[0]['value'])==Decimal(w['value']), 'TESTIGO_NO_COINCIDE_CON_OMEGA')
                if pid=='a': need(v>1, 'TESTIGO_A_FUERA_DOMINIO')
                elif pid=='rho': need(0<v<=1, 'TESTIGO_RHO_FUERA_DOMINIO')
                elif pid=='kappa_tilde': need(v>0, 'TESTIGO_KAPPA_FUERA_DOMINIO')
                elif pid=='eta_H': need(v>-1, 'TESTIGO_ETA_H_FUERA_DOMINIO')
                elif pid=='gain_share': need(v>0, 'TESTIGO_GAIN_FUERA_DOMINIO')
                # eta_w no tiene cota teorica y pi no se limita a [0,1]:
                # robustness._theoretical y macro.bridge fijan admisibilidad conjunta.
                if brk and pid in params and spec['direccion'] in ('inferior','superior'):
                    need(v<=float(b['support_low_primary']) if spec['direccion']=='inferior' else v>=float(b['support_high_primary']), 'TESTIGO_EN_OTRA_DIRECCION')
        est={'complete':'completa_validada','incomplete':'incompleta_validada','not_applicable':'no_aplicable_validada','failed':'fallida_validada'}.get(b['computation_status'],'rechazada')
        return dict(clasificacion=est,motivos=[],estado_cientifico=b['status'])
