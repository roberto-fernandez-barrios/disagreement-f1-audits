"""Elementary agreement-query controls; exact F1 sign, no fitted surrogate."""
import csv, json, datetime
import numpy as np
from pilot import HERE, cases, sha, write
from decision import counts, grid, metric

POLICIES=['uniform','alternating','magnitude']
REPS=32

def affine(k):
    d=k['u']-k['v']; e=d+k['b']-k['a']
    const=d*(k['u']+k['v']+k['n11'])+k['u']*k['b']-k['v']*k['a']
    return const,d,e

def curve(const, w, labels, order):
    w=w[order]; z=labels[order]
    low=const+int(np.minimum(w,0).sum())
    high=const+int(np.maximum(w,0).sum())
    lo=np.r_[low,low+np.cumsum(w*z-np.minimum(w,0))]
    hi=np.r_[high,high+np.cumsum(w*z-np.maximum(w,0))]
    truth=const+int(w@z)
    assert (lo<=truth).all() and (truth<=hi).all() and lo[-1]==hi[-1]==truth
    verdict=np.where(lo>0,1,np.where(hi<0,-1,np.where((lo==0)&(hi==0),0,2)))
    assert ((verdict==2)|(verdict==np.sign(truth))).all()
    return int(np.flatnonzero(verdict!=2)[0]),lo,hi

def validate():
    rng=np.random.default_rng(90210)
    for _ in range(200):
        n=9;q,c,y=rng.integers(0,2,(3,n));y[0]=0;y[1]=1
        k=counts(q,c,y);const,d,e=affine(k);ii=np.flatnonzero(q==c)
        w=np.where(q[ii]==0,d,e);order=rng.permutation(len(ii))
        stop,lo,hi=curve(const,w,y[ii],order)
        for t in range(len(ii)+1):
            observed=ii[order[:t]];n0=int((q[observed]==0).sum());n1=t-n0
            s0=int(y[observed[q[observed]==0]].sum());t0=int(y[observed[q[observed]==1]].sum())
            g=grid(k,bounds=(s0,s0+k['n00']-n0,t0,t0+k['n11']-n1),interior=False)
            assert lo[t]==g['f1_numerator'].min() and hi[t]==g['f1_numerator'].max()
    return {'random_partial_paths':200,'status':'passed'}

def main():
    out=HERE/'results/audit';out.mkdir(parents=True,exist_ok=True)
    write(out/'execution.json',{'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'protocol_sha256':sha(HERE/'DECISION_TRAS_PILOTO.txt'),'code_sha256':sha(HERE/'audit.py'),
        'code':{f:sha(HERE/f) for f in ['audit.py','decision.py','pilot.py','test_decision.py']},
        'replicates':REPS,'policies':POLICIES,'validation':validate()})
    rows=[];all_stops=[]
    for task,seed,model,is_pilot,pred,labels,meta in cases():
        # Use frozen snapshots, never refreshed original files.
        pred=HERE/'inputs/data'/pred.relative_to(HERE.parents[1])
        labels=HERE/'inputs/data'/labels.relative_to(HERE.parents[1])
        with np.load(pred,allow_pickle=False) as z:
            q=z['quantum_prediction'].astype(int);c=z['classical_predictions'].astype(int);idx=z['target_indices']
        with np.load(labels,allow_pickle=False) as z:
            y=z['target_labels'].astype(int);assert np.array_equal(idx,z['target_indices'])
        unique={}
        for j in range(c.shape[1]):unique.setdefault(c[:,j].tobytes(),j)
        cell=f'{task}/{seed}/{model}'
        for j in unique.values():
            h=c[:,j];k=counts(q,h,y);const,d,e=affine(k)
            ii=np.flatnonzero(q==h);groups=q[ii];w=np.where(groups==0,d,e)
            labels_a=y[ii];A=len(ii)
            # Integer numerator truth checked against independent F1 computation.
            truth=const+int(w@labels_a)
            assert np.sign(truth)==np.sign(round(metric(q,y,'f1')-metric(h,y,'f1'),12))
            stops=np.empty((3,REPS),int)
            for rep in range(REPS):
                rng=np.random.default_rng(rep)
                uniform=rng.permutation(A)
                zs=[uniform[groups[uniform]==a].tolist() for a in [0,1]]
                alternating=[]
                # Alternate shuffled strata, starting stratum balanced by repeat.
                for t in range(max(map(len,zs),default=0)):
                    for a in [rep%2,1-rep%2]:
                        if t<len(zs[a]):alternating.append(zs[a][t])
                magnitude=uniform[np.argsort(-np.abs(w[uniform]),kind='stable')]
                for pi,order in enumerate([uniform,np.array(alternating,int),magnitude]):
                    stops[pi,rep],lo,hi=curve(const,w,labels_a,order)
            ix=len(all_stops);all_stops.append(stops)
            base={'index':ix,'cell':cell,'task':task,'seed':seed,'model':model,'stage':'pilot' if is_pilot else 'confirmation',
                  'j':j,'D':k['a']+k['b'],'A':A,'initially_decided':int((stops==0).all()),'truth_sign':int(np.sign(truth))}
            for pi,policy in enumerate(POLICIES):
                row={**base,'policy':policy,'mean_extra':float(stops[pi].mean()),
                     'min_extra':int(stops[pi].min()),'max_extra':int(stops[pi].max()),
                     'mean_total':float(k['a']+k['b']+stops[pi].mean())}
                for budget in [.1,.25,.5]:row[f'certified_{budget}']=float((stops[pi]<=int(budget*A)).mean())
                rows.append(row)
        print(cell,flush=True)
    np.savez_compressed(out/'stops.npz',stops=np.array(all_stops,dtype=np.int16))
    with (out/'pairs.csv').open('w',newline='',encoding='utf-8') as f:
        wcsv=csv.DictWriter(f,fieldnames=list(rows[0]));wcsv.writeheader();wcsv.writerows(rows)
    write(out/'completed.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pairs':len(all_stops),'trajectories':len(all_stops)*3*REPS})

if __name__=='__main__':main()
