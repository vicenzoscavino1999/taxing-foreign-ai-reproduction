"""INEGI CSI_103.xlsx (multi-year, S.1 Economia interna) and its explicit correspondence
to the annual CSI_yy.xlsx snapshots.

Selectors are never reused between the two structures: rows are located by account block
(II.1.1 generation of income) and SNA code label, columns by year header and side (U/A, R/P).
"""
import re
from .nacionales import need, read_source, NationalAdapter, xlsx_cells, dec, F

# concept -> (SNA code, side). Side: U/A uses, R/P resources.
CONCEPTS={'PIB':('B.1b','R/P'),'COE':('D.1','U/A'),'D2_TOTAL':('D.2','U/A'),'D21':('D.21','U/A'),'D211':('D.211','U/A'),'D29':('D.29','U/A'),
          'D3_TOTAL':('D.3','U/A'),'D31':('D.31','U/A'),'D39':('D.39','U/A'),'GOS':('B.2b','U/A'),'MI':('B.3b','U/A')}
# Selectors consumed by the current extraction (Total columns R/S); they must be found again by label.
EXTRACTION={'PIB':'S34','COE':'R36','D2_TOTAL':'R45','D21':'R46','D211':'R47','D29':'R53','D3_TOTAL':'R54','D31':'R55','D39':'R59','GOS':'R60','MI':'R61'}
def split(ref):
    m=re.fullmatch(r'([A-Z]+)(\d+)',ref);return m.group(1),int(m.group(2))
def generation_rows(tab):
    rows={}
    for ref,v in tab.items():
        col,r=split(ref)
        if col=='A' and v['value']:rows[r]=str(v['value']).strip()
    start=[r for r,t in rows.items() if t=='II.1.1 - Cuenta de generación del ingreso'];need(len(start)==1,'generation account block not unique')
    end=min(r for r,t in rows.items() if r>start[0] and t.startswith('II.1.2'))
    found={}
    for concept,(code,_) in CONCEPTS.items():
        hits=[r for r,t in rows.items() if start[0]<r<end and t.startswith(code+' - ')];need(len(hits)==1,f'code {code} not unique in generation block')
        found[concept]=(hits[0],rows[hits[0]])
    return found
def numeric(tab,ref):
    v=tab.get(ref);need(v is not None and v['type']=='n' and v['value'] not in (None,'','  '),'numeric cell missing '+ref)
    need(v['formula'] is None,'formula cell in published tabulado '+ref);return F(v['value'])

def read_csi103(raw=None):
    cfg,real=read_source('MEX_CSI_103')
    raw=real if raw is None else raw
    need(__import__('hashlib').sha256(raw).hexdigest()==cfg['sha256'],'CSI_103 hash does not match registered download')
    c=xlsx_cells(raw);t=c['Tabulado'];m=c['MetaInfo']
    need(m['C14']['value']=='2026-06-30' and m['C5']['value']=='Nacional' and m['C11']['value']=='Año base 2018' and m['C12']['value']=='2003-01-2024-12','CSI_103 revision/coverage metadata')
    a2,a3=str(t['A2']['value']),str(t['A3']['value'])
    need('Año Base 2018' in a2 and 'Serie 2003-2024' in a2 and '2024 Revisada' in a2,'CSI_103 series header')
    need('Economía interna' in a3 and 'millones de pesos' in a3 and 'Precios corrientes' in a3,'CSI_103 scope/unit header')
    years={}
    for ref,v in t.items():
        col,r=split(ref)
        if r==5 and v['value'] and re.fullmatch(r'\d{4}',str(v['value']).strip()):
            y=int(v['value']);nxt=col[:-1]+chr(ord(col[-1])+1) if col[-1]!='Z' else ('A' if len(col)==1 else chr(ord(col[0])+1))+'A'
            need(t[f'{col}6']['value']=='S.1 - Economía interna','CSI_103 sector header '+col)
            need(t[f'{col}7']['value']=='U/A - Usos/Activos' and t[f'{nxt}7']['value']=='R/P - Recursos/Pasivos','CSI_103 side headers '+col)
            years[y]={'U/A':col,'R/P':nxt}
    need(set(range(2003,2025))<=set(years),'CSI_103 years incomplete')
    rows=generation_rows(t)
    return cfg,t,years,rows

def correspondence_and_contrast():
    cfg,t,years,rows=read_csi103();table=[];mismatches=[]
    for y in range(2015,2024):
        a=NationalAdapter('MEX','D2',y);acfg,araw=read_source(a.key);at=xlsx_cells(araw)['Tabulado']
        need(str(y) in str(at['A3']['value']),'annual file year header')
        arows=generation_rows(at)
        for concept,(code,side) in CONCEPTS.items():
            arow,alabel=arows[concept];row,label=rows[concept]
            need(label==alabel,f'label differs between structures for {concept}')
            ext=EXTRACTION[concept];need(split(ext)[1]==arow,f'extraction selector {ext} is not the labelled row for {concept}')
            s1_col={'U/A':'L','R/P':'M'}[side];tot_col={'U/A':'R','R/P':'S'}[side]
            sel103=f'Tabulado!{years[y][side]}{row}';sel_s1=f'Tabulado!{s1_col}{arow}';sel_tot=f'Tabulado!{tot_col}{arow}'
            v103=numeric(t,sel103.split('!')[1]);vs1=numeric(at,sel_s1.split('!')[1]);vtot=numeric(at,sel_tot.split('!')[1])
            equal=v103==vs1==vtot
            if not equal:mismatches.append({'year':y,'concept':concept,'csi103':dec(v103),'annual_S1':dec(vs1),'annual_total':dec(vtot)})
            table.append(dict(year=y,concept=concept,sna_code=code,side=side,label=label,csi103_snapshot_sha256=cfg['sha256'],csi103_selector=sel103,annual_snapshot_sha256=acfg['sha256'],annual_selector_S1=sel_s1,annual_selector_total=sel_tot,
                              extraction_selector='Tabulado!'+ext,csi103_value=dec(v103),annual_S1_value=dec(vs1),annual_total_value=dec(vtot),equal=equal,correspondence_basis='account block II.1.1 + SNA code label + year header + side header'))
    summary={'csi103_sha256':cfg['sha256'],'csi103_bytes':cfg['bytes'],'metainfo_C14':'2026-06-30','years_compared':list(range(2015,2024)),'concepts':list(CONCEPTS),'cells_compared':len(table),
             'all_equal':not mismatches,'mismatches':mismatches,'pins_changed':False,
             'note':'Same revision (2026-06-30) and same S.1 scope: corroborates extraction and file binding; it is NOT a second revision for E2.'}
    return table,summary
