"""One-time provenance extraction: reads validation records, never target labels.
Reproduction uses the frozen derived selection inputs, not the parent project.
"""
import csv,json,re,datetime,shutil
import numpy as np
from pilot import HERE,ROOT,TDC,cases,sha,write

def main():
    out=HERE/'inputs/validation_v3';out.mkdir(parents=True,exist_ok=True)
    manifests=[];rows=[]
    summaries=list((TDC/'results').rglob('summary_v4.csv'))
    for task,seed,model,pilot,pred,labels,meta in cases():
        metadata=json.loads(meta.read_text());cell=f'{task}/{seed}/{model}'
        with np.load(pred,allow_pickle=False) as z:
            cfgs=z['classical_cfgs'].tolist();kernels=z['classical_kernels'].tolist();dims=z['classical_dims'].tolist()
        if 'run' in metadata:
            found=[p for p in summaries if p.parent.name==metadata['run']]
            assert len(found)==1,(cell,found)
            p=found[0];raw=p.read_text(encoding='utf-8')
            import hashlib
            digest=hashlib.sha256(raw.encode()).hexdigest()
            assert digest==metadata['summary_v4_sha256'] or sha(p)==metadata['summary_v4_sha256'],(cell,digest)
            with p.open(encoding='utf-8',newline='') as f: entries=list(csv.DictReader(f))
            lookup={r['cfg']:r for r in entries if r['family']=='classical_ext' and r['model']==model and r['split']=='id_val'}
            scores=[float(lookup[c]['balanced_accuracy']) for c in cfgs]
            paths=[p]*len(cfgs)
        else:
            paths=[pred.parent/'candidate_cache'/f'classical_ext__{re.sub(r"[^A-Za-z0-9_.-]+","_",k)}__d{d}.npz' for k,d in zip(kernels,dims)]
            scores=[]
            for p in paths:
                with np.load(p,allow_pickle=False) as z:scores.append(float(z[f'{model}_validation_bacc'].item()))
        assert len(scores)==115 and np.isfinite(scores).all()
        j=min(range(115),key=lambda j:(-scores[j],cfgs[j]))
        for i,(cfg,score,p) in enumerate(zip(cfgs,scores,paths)):
            rows.append({'cell':cell,'j':i,'cfg':cfg,'validation_balanced_accuracy':score,
                'source':p.relative_to(ROOT).as_posix(),'source_sha256':sha(p),'selected':int(i==j)})
        manifests.append({'cell':cell,'selected_j':j,'cfg':cfgs[j],'validation_balanced_accuracy':scores[j]})
    with (out/'validation_scores.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    for name in ['export_gate2_predictions_v10.py','export_partial_identification_v9.py']:
        shutil.copy2(TDC/'scripts/experiments'/name,out/name)
    write(out/'selection.json',{'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'rule':'maximum source/ID-validation BAcc; lexicographic cfg tie; newly applied retrospective P1-style comparator selection',
        'labels_read':False,'cells':manifests})
    write(out/'manifest.json',{p.name:sha(p) for p in out.iterdir() if p.name!='manifest.json'})
    print('Frozen validation-only choices:',len(manifests))

if __name__=='__main__':main()
