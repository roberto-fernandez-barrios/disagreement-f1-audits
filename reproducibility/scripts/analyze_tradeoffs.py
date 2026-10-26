"""Targeted V4 checks/figure. Reuses V3 and independently checks weak-zero stops.

No fitting, new benchmarks, or rerun of positive-tolerance trajectories.
All extensions are retrospective. The earlier reviewer diagnostic is preserved.
"""
from pathlib import Path
import sys,csv,json,hashlib,datetime
from fractions import Fraction as F
from collections import defaultdict
import numpy as np
H=Path(__file__).resolve().parents[1];sys.path.insert(0,str(H))
from pilot import cases,snapshot
from decision import counts
from audit import affine,curve,POLICIES
from revision_v3 import orders,aggregate
from tolerance import hulls,decision

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
readcsv=lambda p:list(csv.DictReader(p.open(encoding='utf8')))
out=H/'results/v4';out.mkdir(exist_ok=True)
old=readcsv(H/'results/v3/pairs.csv')
with np.load(H/'results/v3/stops.npz') as z:v3={key:z[key] for key in ['exact','epsilon']}
weak=np.load(H/'closure_v4/weak_zero_stops.npz')['weak']
diag=json.loads((H/'closure_v4/weak_zero_diagnostic.json').read_text())
for name,digest in diag['sources_sha256'].items():
    if name!='output/pdf/paper.pdf':assert sha(H/name)==digest,name
eps=[F(0),F(1,1000),F(5,1000),F(1,100),F(2,100),F(5,100)]
sensitivity=[];costs=[];ix=0;checked=0
for task,seed,model,pilot,pred,labels,meta in cases():
    pred,labels=[snapshot(p,[]) for p in [pred,labels]]
    with np.load(pred) as z:q=z['quantum_prediction'].astype(int);c=z['classical_predictions'].astype(int);idx=z['target_indices']
    with np.load(labels) as z:y=z['target_labels'].astype(int);assert np.array_equal(idx,z['target_indices'])
    unique={}
    for j in range(c.shape[1]):unique.setdefault(c[:,j].tobytes(),j)
    cell=f'{task}/{seed}/{model}'
    for j in unique.values():
        row=old[ix];assert int(row['index'])==ix and row['cell']==cell and int(row['j'])==j
        h=c[:,j];k=counts(q,h,y);const,d,e=affine(k)
        # Same 0<P<n domain as the original initial-information analysis.
        interval=hulls(k,interior=True)[0]
        for ep in eps:
            certified,choice,regret=decision(interval,ep)
            sensitivity.append({'index':ix,'cell':cell,'stage':row['stage'],'validation_selected':int(row['validation_selected']),
                'epsilon':float(ep),'certified':int(certified),'worst_regret_numerator':regret.numerator,'worst_regret_denominator':regret.denominator})
        agreement=np.flatnonzero(q==h);groups=q[agreement];w=np.where(groups==0,d,e)
        for rep in range(32):
            for pi,order in enumerate(orders(groups,w,rep)):
                stop,lo,hi=curve(const,w,y[agreement],order)
                assert stop==v3['exact'][ix,pi,rep]
                zero=int(np.flatnonzero((lo>=0)|(hi<=0))[0])
                assert zero==weak[ix,pi,rep]
                assert v3['epsilon'][ix,pi,rep]<=zero<=stop
                # Numerator sign and F1 sign agree, including zero denominators.
                assert (lo[zero]>=0 or hi[zero]<=0)
                if zero:assert lo[zero-1]<0<hi[zero-1]
                checked+=1
        for pi,policy in enumerate(POLICIES):
            base={'index':ix,'cell':cell,'policy':policy,'D':int(row['D']),'validation_selected':int(row['validation_selected']),'nearest':int(row['nearest'])}
            for name,arr in [('strict',v3['exact']),('weak_zero',weak),('epsilon',v3['epsilon'])]:
                base[name+'_extra']=float(arr[ix,pi].mean());base[name+'_total']=base['D']+base[name+'_extra']
            costs.append(base)
        ix+=1
    print(cell,flush=True)
assert ix==3200 and checked==307200
def writecsv(name,rows):
    with (out/name).open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
writecsv('sensitivity.csv',sensitivity);writecsv('costs.csv',costs)
summary={'design':'retrospective targeted V4 extension; unknown prevalence; original initial intervals restrict 0<P<n, query paths include P=0,n',
    'weighting':'equal cells; within cell average pairs and within pair average 32 fixed orders; no independent-observation inference',
    'weak_trajectories_verified':checked,'weak_array_sha256':sha(H/'closure_v4/weak_zero_stops.npz'),'costs':[],'sensitivity':[]}
for cohort in ['all','validation','nearest']:
    for policy in POLICIES:
        selected=[r for r in costs if r['policy']==policy and (cohort=='all' or r['validation_selected' if cohort=='validation' else 'nearest'])]
        keys=['D']+[name+'_'+metric for name in ['strict','weak_zero','epsilon'] for metric in ['extra','total']]
        agg=aggregate(selected,keys);rec={'cohort':cohort,'policy':policy,**agg};summary['costs'].append(rec)
        prior=next(r for r in diag['costs'] if r['cohort']==cohort and r['policy']==policy)
        for name in ['strict','weak_zero','epsilon']:assert abs(agg['cell_mean'][name+'_total']-prior[name])<1e-10
for ep in eps:
    rec={'epsilon':float(ep)}
    for cohort in ['all','validation','reserved']:
        selected=[r for r in sensitivity if r['epsilon']==float(ep) and (cohort=='all' or (r['validation_selected'] if cohort=='validation' else r['stage']=='confirmation'))]
        rec[cohort]=aggregate(selected,['certified'])
    summary['sensitivity'].append(rec)
    prior=next(r for r in diag['initial_tolerance_sensitivity'] if r['epsilon']==float(ep))
    assert abs(rec['all']['cell_mean']['certified']-prior['equal_cell_all'])<1e-12
    assert abs(rec['validation']['cell_mean']['certified']-prior['validation'])<1e-12
cells=defaultdict(list)
for r in costs:
    if r['policy']=='magnitude':cells[r['cell']].append(r['epsilon_total'])
means={cell:float(np.mean(v)) for cell,v in cells.items()}
summary['magnitude_epsilon_cell_costs']=means
summary['descriptive_cell_cost_range']={'minimum':min(means.values()),'median':float(np.median(list(means.values()))),'maximum':max(means.values()),'cells':len(means)}
(out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')

# Vector figure: no interpolated query-cost trajectories, no confidence bands.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size':9,'axes.labelsize':9,'legend.fontsize':8.5,'pdf.fonttype':42,'ps.fonttype':42})
fig,ax=plt.subplots(figsize=(4.6,1.55),layout='constrained')
xx=[float(e) for e in eps]
for cohort,color,marker,label in [('all','#20639b','o','All pairs (equal cell weights)'),('validation','#b54a1a','s','Validation-selected pairs')]:
    yy=[100*r[cohort]['cell_mean']['certified'] for r in summary['sensitivity']]
    ax.plot(xx,yy,color=color,marker=marker,ms=4,lw=1.4,label=label)
ax.axvline(.01,color='0.55',ls=':',lw=.8)
ax.set(xlabel=r'Absolute F1 tolerance $\varepsilon$',ylabel='Certified (%)',ylim=(65,100),xlim=(-.001,.051))
ax.set_xticks([0,.01,.02,.03,.04,.05],['0','0.01','0.02','0.03','0.04','0.05']);ax.set_yticks([70,80,90,100])
ax.grid(axis='y',alpha=.2);ax.legend(loc='lower right',frameon=False)
fig.savefig(H/'manuscript/tolerance_sensitivity.pdf',metadata={'CreationDate':None,'ModDate':None})
fig.savefig(out/'tolerance_sensitivity.png',dpi=600);plt.close(fig)
record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'script_sha256':sha(Path(__file__)),
    'baseline_diagnostic_sha256':sha(H/'closure_v4/weak_zero_diagnostic.json'),
    'sources':{f:sha(H/f) for f in ['results/v3/pairs.csv','results/v3/intervals.csv','results/v3/stops.npz','audit.py','tolerance.py','revision_v3.py','decision.py','pilot.py','DATA_MANIFEST.json']},
    'outputs':{p.relative_to(H).as_posix():sha(p) for p in sorted(out.iterdir()) if p.name in {'sensitivity.csv','costs.csv','summary.json','tolerance_sensitivity.png'}},
    'figure_sha256':sha(H/'manuscript/tolerance_sensitivity.pdf'),'weak_stops_reproduced_exactly':True}
(out/'execution.json').write_text(json.dumps(record,indent=2),encoding='utf8')
print(json.dumps({'verified_trajectories':checked,'dispersion':summary['descriptive_cell_cost_range']}))
