"""Read the archived E11 menus, evaluate status shares, and extract common-policy checks."""
import json, sys
from collections import defaultdict
from pathlib import Path
import comparar as c
sys.path.insert(0, str(c.PILOT/'linear/src'))
from paper2b import model, run
def status(st, td, tf, des):
    e=model.evaluate(st,td,tf,des)
    n=sum(model.pareto_moment(st.a,st.z_m,0,v.lo,v.hi) for v in e.intervals if v.prior=='F' and v.label=='I')
    return dict(td=td,tf=tf,CS=e.CS,switched=n,prior_formal=e.mass_prior_F,informal=e.mass_I,topology=e.topology)
def measures():
    cfg=run.RunConfig();k=run.provider_for(cfg); sel=c.selection()
    rows=defaultdict(list)
    for ln in c.MESH.read_bytes().splitlines():
        r=json.loads(ln)
        if r['side']=='point':rows[r['frontier_id']].append(r)
    out={15:[],30:[]}; common={}
    for key,v in c.load(c.MAN)['L1-ELAST']['fronteras'].items():
        design,menu,fid=key.split('|')
        if menu!='df':continue
        p={a:float(b) for a,b in v['clave_estructural'].items()};st=k.state(p)
        if fid==sel[design]['id']:
            common[design]=[status(st,.15,tf,design) for tf in (0,.15)]
        for cap in (15,30):
            nodes=[a for a in rows[fid] if a['tau_d']<=.35 and a['tau_f']<=cap/100]
            assert len(nodes)==(6 if cap==15 else 9) and all(a['computation_status']=='complete' for a in nodes)
            base=max(a['CS'] for a in nodes if a['tau_f']==0)
            best=max(a['CS'] for a in nodes)
            winners=[a for a in nodes if a['CS']==best]
            winner_switch=['IF' in a['topology'].split('->') for a in winners]
            record=dict(id=fid,design=design,phi=p['phi'],domestic=base,combined=best,ties=len(winners),some=any(winner_switch),all=all(winner_switch))
            if any(winner_switch):
                assert best>0
                vals=[status(st,a['tau_d'],a['tau_f'],design) for a in winners]
                assert all(abs(x['CS']-best)<1e-12 for x in vals)
                record.update(percent=100*base/best,winners=vals)
            out[cap].append(record)
    assert len(out[15])==len(out[30])==110
    return dict(fixed=common,grids=out)
if __name__=='__main__':
    data=measures()
    c.save(Path(sys.argv[1]),data)
    for key,v in data['fixed'].items():
        print(key,*[(x['CS'],x['switched']) for x in v])
    for cap,rs in data['grids'].items():
        print(cap,[(x['id'][4:12],round(x['percent'],3),round(100*x['winners'][0]['switched'],2),x['ties'],x['all']) for x in rs if x['some']])
