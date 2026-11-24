E=T/'paso4_integracion_final_enf_desde_rem131'
t7=J(T/'paso4_conciliacion_portabilidad_desde_rem108/conciliacion/ensamblajes/T7_anexo.json')['filas']
ex=J(T/'paso4_conciliacion_portabilidad_desde_rem108/conciliacion/EXP8_TABLA.json')
ef={x['afirmacion']:x for x in ex['filas']}
br=JL(E/'integ_conciliacion_ENF_INTEGRAL/brechas_celdas.jsonl'); bmap={(x['unidad'],x['cell_id']):x for x in br}
ceil={x['clave_transformada_sha256']:x for x in JL(E/'integ_ensamblado_ENF_INTEGRAL/enf_techos_integrados.jsonl')}
product=Y/'exp8/ENF_POR_AFIRMACION.jsonl'; output=JL(product); om={x['afirmacion']:x for x in output}
ck('source_and_product_universes',len(t7)==len(output)==len(om)==1728 and len(ef)==1712 and len(bmap)==1724 and len(ceil)==26 and set(om)=={f['afirmacion'] for f in t7})
ck('T7_original_categories',dict(Counter(f['categoria_original'] for f in t7))=={'cambio_de_signo_certificado':1524,'inconclusa_por_testigos_en_tolerancia':188,'robusta_infactible_certificada':16})
rows=[]; cells=set(); slots=0; margins=[]; errors=[]; guarantee=Counter(); sign_cross=Counter(); countries={}
for f in t7:
    out=om[f['afirmacion']]; e=ef.get(f['afirmacion']); bounds={}; linked={}
    for n in ('categoria_original','pid','kind','familia','pais','j','disponibilidad','escenario','diseno','cota','bloque','capa'):
        assert out[n]==f[n],(f['afirmacion'],n)
    for side in ('sup','inf'):
        u=f['testigo_'+side]; so=out[side]
        if e is not None:
            cid=e.get(side+'_cell_id'); assert e.get(side+'_unidad') in (None,u)
        else:
            p=auth(T/f[side+'_ref'],f[side+'_filas_sha256']); data=J(p)
            ids={r['cell_id'] for r in data.get('cell_context',[])+data.get('confrontation_result',[]) if r.get('cell_id')}
            assert len(ids)==1; cid=next(iter(ids))
        assert (so['unidad'],so['cell_id'],so['G_T7'],so['estado_evidencia'])==(u,cid,f.get(side+'_G'),f[side+'_estado_evidencia'])
        avail=f[side+'_estado_evidencia']=='filas aceptadas'; assert so['enlazado']==avail
        linked[side]=avail
        if not avail: continue
        b=bmap[(u,cid)]; slots+=1; cells.add((u,cid))
        assert b['G_padre']==f[side+'_G']
        for n in ('K1_reutilizado','C2_enf','G_enf','dG','clave_transformada_sha256','estado_techo_historico','origen_G'):
            assert so[n]==b[n],(f['afirmacion'],side,n)
        assert so['G_padre_ENF']==b['G_padre']
        assert (b['G_padre']>0)-(b['G_padre']<0)==(b['G_enf']>0)-(b['G_enf']<0)
        c=ceil[b['clave_transformada_sha256']]; ch=c['fila_historica']; guarantee[c['origen']]+=1
        assert ch['C_2']==b['C2_enf'] and ch['error_kind']=='certified_bound'
        low=F(ch['C_2'])-F(ch['error_normalizado']); high=F(ch['C_2'])+F(ch['error_normalizado'])
        if c['origen']=='resolucion_no_alcanzado':
            rr=c['resolucion']; assert rr['resolucion']=='no_alcanzado_demostrado' and rr['esquema_supremo_no_alcanzado']['tau_d_at_sup'] is None
            # Outer enclosure covers both accepted historical guarantee and independent limit certificate.
            low=min(low,F(rr['valor_limite_C2'][0])); high=max(high,F(rr['valor_limite_C2'][1]))
        else: assert ch['estado']=='complete'
        lo=low-F(b['K1_reutilizado']); hi=high-F(b['K1_reutilizado'])
        bounds[side]={'G_lower':str(lo),'G_upper':str(hi),'key':b['clave_transformada_sha256']}
        errors.append(ch['error_normalizado'])
    ns=linked['sup'] and F(bounds['sup']['G_lower'])>F(-1,100)
    ni=linked['inf'] and F(bounds['inf']['G_upper'])<F(1,100)
    if f['afirmacion'] in ef:
        if ns and ni: result='inconclusa_preservada'
        elif ns and not linked['inf']: result='parcial_no_robusta_infactible'
        elif ni and not linked['sup']: result='parcial_no_robusta_factible'
        else: result='no_decidida_por_testigos'
        if ns: margins.append(F(bounds['sup']['G_lower'])+F(1,100))
        if ni: margins.append(F(1,100)-F(bounds['inf']['G_upper']))
        if ns and ni:
            strict=F(bounds['sup']['G_lower'])>0 and F(bounds['inf']['G_upper'])<0
            sign_cross['opposite_signs_certified' if strict else 'economic_inconclusion_not_strict_sign_cross']+=1
    else:
        assert not ns and f['pais']=='MEX'
        result='no_decidida_por_testigos (mantener la robustez exige el supremo ENF sobre todo el soporte)'
    assert result==out['canal_eta_f'],(f['afirmacion'],result,out['canal_eta_f'])
    coverage='ambos' if all(linked.values()) else 'solo_sup' if linked['sup'] else 'solo_inf'
    assert out['cobertura_ENF']==coverage and out['cambio_de_signo_en_testigos_ENF']==[]
    countries.setdefault(f['pais'] or '-',Counter())[result]+=1
    rows.append({'afirmacion':f['afirmacion'],'category':f['categoria_original'],'conclusion':result,'coverage':coverage,'bounds':bounds})
counts=Counter(r['conclusion'] for r in rows)
ck('claims_independently_joined_with_certified_bounds',counts['inconclusa_preservada']==1705 and counts['parcial_no_robusta_infactible']==4 and counts['parcial_no_robusta_factible']==3 and sum(v for k,v in counts.items() if k.startswith('no_decidida'))==16)
ck('3449_slots_1724_exact_cells',slots==3449 and cells==set(bmap))
ck('economic_margins_also_exceed_report_tolerance',min(margins)>F(1,10000))
ck('accepted_sources_unchanged_by_join',all(HF(p)==h for p,h in source_hashes.items()))
