"""Usage: python comparar.py output_directory, using the public replication venv."""
import concurrent.futures, hashlib, json, math, os, subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
PILOT = HERE/'kernels'
MAN = HERE/'inputs/points.json'
MESH = HERE/'inputs/mesh.jsonl'
RANGES = dict(a=(1.1,2.5),beta_tilde=(.25,4),eta_d=(.1,4),eta_f=(.1,8),kappa_tilde=(.005,.2),phi=(0,1),rho=(.4,1),u_theta=(.1,.9),z_cost=(1,100))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):
    return json.loads(path.read_bytes())
def save(path,value):
    with path.open('x',encoding='utf8') as f:
        json.dump(value,f,ensure_ascii=False,allow_nan=False,indent=2)
def selection():
    assert sha(MESH)=='402613ed99d4e47b27d7d55811674268f95fd0ed1c905cae404488727242f090'
    assert sha(MAN)=='9be3e436c39cdce596a0d0eaff5caddecf1202e5f42a61c7f17a918fe84827e8'
    rows={}
    for l in MESH.read_bytes().splitlines():
        r=json.loads(l)
        if r['side']=='point':
            rows.setdefault(r['frontier_id'],[]).append(r)
    selected={}
    for design in ('G','N'):
        eligible=[]
        for k,v in load(MAN)['L1-ELAST']['fronteras'].items():
            ds,menu,fid=k.split('|');p={k:float(n) for k,n in v['clave_estructural'].items()}
            if ds!=design or menu!='df' or not 0<p['phi']<1:continue
            nodes=[r for r in rows[fid] if 0<r['tau_f']<=.15 and r['tau_d']<=.35 and 'IF' in r['topology'].split('->') and r['computation_status']=='complete']
            if nodes:
                interior=sum(lo<p[i]<hi for i,(lo,hi) in RANGES.items())
                eligible.append((-interior,fid,p,nodes,v))
        score,fid,p,nodes,v=min(eligible,key=lambda c:c[:2])
        source=HERE/'inputs'/f'{design}.json'
        assert sha(source)=={'G': '131571e02f4cc56783fdc7852f3b2ded4fb55e32599639f0661c9e56ace1fcc4', 'N': 'f6739b420cd24b6234f53b0165dfd0cd953dabd9f9ce242384f83ed7eb323c99'}[design]
        cc=next(c for c in load(source)['capture_ceiling_result'] if c['frontier_id']==fid)
        selected[design]=dict(id=fid,parameters=p,nodes=[{k:r[k] for k in ('tau_d','tau_f','CS','topology')} for r in nodes],eligible=len(eligible),interior=-score,old=cc,source_sha256=v['filas_sha256'],mesh_sha256='007095a94b7d1fce18aea6214c56c45b370e9a6eb5b0e415da6a0cc09a26ea8c',manifest_sha256='b1cf8af5eab8aa22c53ec279bd5660dbf57847b6be8f874c56af7d71f9cd4bab')
    return selected
def worker(out,design,rule,menu):
    d=load(out/'puntos.json')[design]
    src=PILOT/('linear/src' if rule=='E11' else 'statutory/src')
    mf=src.parent/('SHA256SUMS_copia.txt' if rule=='E11' else 'SHA256SUMS_variante.txt')
    for line in mf.read_text('utf-8-sig').splitlines():
        h,n=line.split(' *',1)
        assert sha((src.parent if rule=='E11' else src)/n)==h
    sys.path.insert(0,str(src))
    from paper2b import model,run
    from paper2b.intervalos import Iv
    cfg=run.RunConfig(); kernel=run.provider_for(cfg); st=kernel.state(d['parameters'])
    assert kernel.certified
    def status(x,y):
        e=model.evaluate(st,x,y,design)
        switched=sum(model.pareto_moment(st.a,st.z_m,0,v.lo,v.hi) for v in e.intervals if v.prior=='F' and v.label=='I')
        return dict(switched=switched,prior_formal=e.mass_prior_F,informal=e.mass_I,topology=e.topology,CS=e.CS,E0_over_Bpot=e.E0/st.B_pot)
    if rule=='E11':
        for n in d['nodes']:
            e=status(n['tau_d'],n['tau_f'])
            assert e['topology']==n['topology'] and abs(e['CS']-n['CS'])<1e-12
    previous=None
    for cap in ((.30,.15) if menu=='df' else (0.,)):
        path=out/f'{design}_{rule}_{menu}_{round(100*cap):02d}.json'
        old=d['old']
        if menu=='df' and rule=='E11' and old['computation_status']=='complete' and old['tau_d_at_sup']<=.35 and old['tau_f_at_sup']<=cap:
            c,e=old['C_2'],old['numerical_error']
            z=dict(lo=math.nextafter(c-e,-math.inf),hi=math.nextafter(c+e,math.inf),td=old['tau_d_at_sup'],tf=old['tau_f_at_sup'],status='complete',source='Paso 3')
        elif previous and previous['status']=='complete' and previous['tf']<=cap:
            z={**previous,'source':'larger feasible rectangle'}
        else:
            start=time.monotonic()
            c=kernel.capture_ceiling(st,design,menu,.35,cap,True,cfg.sup)
            s=c.sup;b=kernel.engine(st,design).P.B_pot
            assert s.error_kind=='certified_bound'
            z=dict(lo=(Iv.point(s.lower)/b).lo,hi=(Iv.point(s.upper)/b).hi,td=s.tau_d,tf=s.tau_f,status=c.status,reason=c.reason,error=c.numerical_error,boxes=s.final_n,seconds=time.monotonic()-start,source='new')
        assert 0<=z['td']<=.35 and 0<=z['tf']<=cap and z['lo']<=z['hi']
        z.update(design=design,rule=rule,menu=menu,cap=cap,witness=status(z['td'],z['tf']),at_zero=status(z['td'],0.))
        save(path,z); previous=z
        print(path.name,z['status'],z['lo'],z['hi'],z['witness']['switched'],flush=True)
def summary(out):
    rows=[]
    for d in ('G','N'):
        a=load(out/f'{d}_E11_d_00.json')
        for r in ('E11','estatutaria'):
            for cap in (15,30):
                b=load(out/f'{d}_{r}_df_{cap}.json')
                assert b['lo']>0 and a['lo']>0
                lo=math.nextafter(100*math.nextafter(a['lo']/b['hi'],-math.inf),-math.inf)
                hi=math.nextafter(100*math.nextafter(a['hi']/b['lo'],math.inf),math.inf)
                rows.append(dict(design=d,rule=r,cap=cap,domestic=[a['lo'],a['hi']],combined=[b['lo'],b['hi']],percent=[lo,hi],witness=b['witness'],zero=b['at_zero'],domestic_status=a['status'],combined_status=b['status']))
    save(out/'resumen.json',rows)
def main():
    if sys.argv[1]=='worker':
        worker(Path(sys.argv[2]),*sys.argv[3:]);return
    out=Path(sys.argv[1]).resolve()
    out.mkdir(parents=True,exist_ok=False); save(out/'puntos.json',selection())
    env={**os.environ,'PYTHONHASHSEED':'0','TZ':'UTC'}
    for k in ('BLIS','MKL','NUMEXPR','OMP','OPENBLAS','VECLIB_MAXIMUM'):
        env[k+'_NUM_THREADS' if k!='VECLIB_MAXIMUM' else 'VECLIB_MAXIMUM_THREADS']='1'
    def call(args):
        subprocess.run([sys.executable,'-B','-P','-s',str(Path(__file__).resolve()),'worker',str(out),*args],env=env,check=True)
    jobs=[(d,r,m) for d in ('G','N') for r,m in (('E11','df'),('estatutaria','df'),('E11','d'))]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(call,jobs))
    summary(out)
if __name__=='__main__':
    main()

