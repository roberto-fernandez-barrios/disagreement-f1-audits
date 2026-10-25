"""Frozen-prediction reanalysis. No training, network, or provider operations."""
from pathlib import Path
import hashlib, json, datetime, csv, sys, platform
import numpy as np
from decision import counts, intervals, metric
from test_decision import main as test

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TDC = ROOT / 'articulos/principales/target_domain_certificates'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')

def cases():
    g = TDC/'results/v10/gate2_prospective'
    for task in ['brfss_diabetes','acsfoodstamps']:
        for seed in [42,123,999,7,2024]:
            for model in ['svc','gpc']:
                unit = g/'prediction_locks'/task/f'seed_{seed}'
                yield task,seed,model,seed==42,unit/f'predictions_{model}.npz',g/'sealed_labels'/task/f'seed_{seed}'/'evaluation_labels.npz',unit/f'metadata_{model}.json'
    security=['00_ember_m1','01_ember_m2','02_toniot_scanning_m2_centroid','03_toniot_scanning_natural_cur',
              '04_unsw_dos_m2_centroid','05_unsw_dos_natural_cur','06_unsw_recon_m2_centroid','07_unsw_recon_natural_cur']
    for ix, name in enumerate(security):
        unit=TDC/'results/v9/partial_identification/predictions'/name
        for model in ['svc','gpc']:
            yield unit.name,42,model,ix<2,unit/f'predictions_{model}.npz',unit/'evaluation_labels.npz',unit/f'metadata_{model}.json'

def snapshot(path, manifest, frozen=True):
    rel = path.relative_to(ROOT)
    dest = HERE/'inputs/data'/rel
    dest.parent.mkdir(parents=True,exist_ok=True)
    if frozen:
        expected={k.replace('\\','/'):v for k,v in json.loads((HERE/'DATA_MANIFEST.json').read_text(encoding='utf-8')).items()}
        assert sha(dest)==expected[dest.relative_to(HERE).as_posix()],str(dest)
    else:
        if not dest.exists(): dest.write_bytes(path.read_bytes())
        assert sha(dest)==sha(path), str(path)
    manifest.append({'original':str(rel),'snapshot':str(dest.relative_to(HERE)), 'sha256':sha(dest),'bytes':dest.stat().st_size})
    return dest

def main(stage):
    lock=json.loads((HERE/'PROTOCOLO_PILOTO.lock.json').read_text())
    assert sha(HERE/'PROTOCOLO_PILOTO.txt')==lock['sha256']
    out=HERE/'results'/stage
    out.mkdir(parents=True,exist_ok=True)
    write(out/'execution.json',{'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':stage,
        'execution_kind':'post-review reproduction; original state preserved in history/v1_before_critical_review_20261024T103944Z',
        'protocol':lock,'code':{f:sha(HERE/f) for f in ['pilot.py','decision.py','test_decision.py']},
        'python':sys.version,'numpy':np.__version__,'platform':platform.platform()})
    write(out/'validation.json',test())
    rows=[];manifest=[];summaries=[]
    for task,seed,model,is_pilot,pred,labels,meta in cases():
        if is_pilot != (stage=='pilot'): continue
        pred,labels,meta=[snapshot(p,manifest) for p in [pred,labels,meta]]
        metadata=json.loads(meta.read_text())
        for key in ['prediction_sha256','prediction_artifact_sha256']:
            if key in metadata: assert sha(pred)==metadata[key]
        with np.load(pred,allow_pickle=False) as z:
            q=z['quantum_prediction'].astype(int); c=z['classical_predictions'].astype(int)
            idx=z['target_indices']; cfgs=z['classical_cfgs'].tolist()
        with np.load(labels,allow_pickle=False) as z:
            assert np.array_equal(idx,z['target_indices'])
            y=z['target_labels'].astype(int)
        assert c.shape==(500,115) and q.shape==y.shape==(500,)
        assert all(set(np.unique(z))<= {0,1} for z in [q,c,y])
        unique={}
        for j in range(c.shape[1]): unique.setdefault(c[:,j].tobytes(),[]).append(j)
        cell=f'{task}/{seed}/{model}'; start=len(rows)
        for js in unique.values():
            j=js[0]; h=c[:,j]; k=counts(q,h,y)
            unknown=intervals(k); oracle=intervals(k,prevalence=int(y.sum()))
            boundary=intervals(k,interior=False)
            imputed=y.copy(); imputed[q==h]=q[q==h]
            base={'cell':cell,'task':task,'seed':seed,'model':model,'j':j,'cfg':str(cfgs[j]),
                  'duplicate_count':len(js),'n':len(y),'P':int(y.sum()),**k}
            for name in ['accuracy','ba','f1']:
                lo,hi=unknown[name]['lower'],unknown[name]['upper']
                truth=metric(q,y,name)-metric(h,y,name)
                assert lo-1e-12<=truth<=hi+1e-12
                olo,ohi=oracle[name]['lower'],oracle[name]['upper']
                assert lo-1e-12<=olo<=ohi+1e-12<=hi+2e-12
                naive=metric(q,imputed,name)-metric(h,imputed,name)
                row={**base,'metric':name,**unknown[name],'truth':truth,'width':hi-lo,
                    'strict_reversal':int(lo<-1e-12 and hi>1e-12),'material_reversal':int(lo<=-.01+1e-12 and hi>=.01-1e-12),
                    'oracle_lower':olo,'oracle_upper':ohi,'oracle_width':ohi-olo,
                    'oracle_strict_reversal':int(olo<-1e-12 and ohi>1e-12),
                    'oracle_material_reversal':int(olo<=-.01+1e-12 and ohi>=.01-1e-12),
                    'boundary_lower':boundary[name]['lower'],'boundary_upper':boundary[name]['upper'],
                    'agreement_imputation':naive if np.isfinite(naive) else None}
                rows.append(row)
        local=rows[start:]
        summary={'cell':cell,'unique_pairs':len(unique)}
        for name in ['accuracy','ba','f1']:
            rr=[r for r in local if r['metric']==name]
            summary[name]={k:float(np.mean([r[k] for r in rr])) for k in ['width','strict_reversal','material_reversal','oracle_width','oracle_strict_reversal','oracle_material_reversal']}
        summaries.append(summary)
        print(json.dumps(summary),flush=True)
    write(out/'sources.json',manifest);write(out/'cell_summary.json',summaries)
    with (out/'pairs.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    write(out/'completed.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':len(rows),'cells':len(summaries)})

if __name__=='__main__':
    stage=sys.argv[1] if len(sys.argv)>1 else 'pilot'
    assert stage in ['pilot','confirmation']
    main(stage)
