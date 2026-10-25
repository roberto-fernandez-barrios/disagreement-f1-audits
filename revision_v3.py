"""Full retrospective V3 campaign. No network, fitting, or original files."""
import csv,json,datetime,time
from collections import defaultdict
from fractions import Fraction as F
import numpy as np
from pilot import HERE,ROOT,cases,sha,write,snapshot
from decision import counts,metric
from audit import affine,curve,POLICIES,REPS
from tolerance import hulls,decision,exact_decision,prefix_bounds,first_stop
from test_tolerance import main as validate

def orders(groups,w,rep):
    uniform=np.random.default_rng(rep).permutation(len(groups))
    zs=[uniform[groups[uniform]==a].tolist() for a in [0,1]]
    alternate=[]
    for t in range(max(map(len,zs),default=0)):
        for a in [rep%2,1-rep%2]:
            if t<len(zs[a]):alternate.append(zs[a][t])
    return [uniform,np.array(alternate,int),uniform[np.argsort(-np.abs(w[uniform]),kind='stable')]]

def writecsv(path,rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def aggregate(rows,keys):
    cells=defaultdict(list)
    for r in rows:cells[r['cell']].append(r)
    return {'rows':len(rows),'cells':len(cells),
        'cell_mean':{k:float(np.mean([np.mean([r[k] for r in rs]) for rs in cells.values()])) for k in keys},
        'pair_mean':{k:float(np.mean([r[k] for r in rows])) for k in keys}}

def main():
    out=HERE/'results/v3';out.mkdir(parents=True,exist_ok=True);start=time.time()
    rec={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'design':'retrospective, after review; no new prospective holdout',
         'code':{f:sha(HERE/f) for f in ['revision_v3.py','tolerance.py','test_tolerance.py','pilot.py','audit.py','decision.py']},
         'protocol_sha256':sha(HERE/'REVISION_V3_PROTOCOL.txt'),
         'validation_input_sha256':sha(HERE/'inputs/validation_v3/manifest.json'),
         'old_stops_sha256':sha(HERE/'results/audit/stops.npz'),'tests':validate()}
    write(out/'execution.json',rec)
    chosen={r['cell']:r['selected_j'] for r in json.loads((HERE/'inputs/validation_v3/selection.json').read_text())['cells']}
    old=np.load(HERE/'results/audit/stops.npz')['stops'];stops=np.empty_like(old)
    choices=np.empty(old.shape,dtype=np.int8)
    intervalrows=[];costrows=[];pairrows=[];max_realized=F(0);worse=0;worse_pairs=0;initial_worse=0
    validation_scores=list(csv.DictReader((HERE/'inputs/validation_v3/validation_scores.csv').open(encoding='utf8')))
    ties=[]
    for task,seed,model,pilot,pred,labels,meta in cases():
        pred,labels=[snapshot(p,[]) for p in [pred,labels]]
        with np.load(pred,allow_pickle=False) as z:q=z['quantum_prediction'].astype(int);c=z['classical_predictions'].astype(int);idx=z['target_indices']
        with np.load(labels,allow_pickle=False) as z:y=z['target_labels'].astype(int);assert np.array_equal(idx,z['target_indices'])
        unique={}
        for j in range(c.shape[1]):unique.setdefault(c[:,j].tobytes(),j)
        cell=f'{task}/{seed}/{model}';nearest=min(unique.values(),key=lambda j:(int((q!=c[:,j]).sum()),j))
        valj=unique[c[:,chosen[cell]].tobytes()]
        vr=[r for r in validation_scores if r['cell']==cell];maximum=max(float(r['validation_balanced_accuracy']) for r in vr)
        tied=[r for r in vr if float(r['validation_balanced_accuracy'])==maximum]
        tie_js={unique[c[:,int(r['j'])].tobytes()] for r in tied}
        tie_record={'cell':cell,'candidates':[{'j':int(r['j']),'cfg':r['cfg'],'canonical_j':unique[c[:,int(r['j'])].tobytes()]} for r in tied],'outcomes':[]}
        for j in unique.values():
            ix=len(pairrows);h=c[:,j];k=counts(q,h,y);const,d,e=affine(k)
            ii=np.flatnonzero(q==h);groups=q[ii];w=np.where(groups==0,d,e);la=y[ii]
            base={'index':ix,'cell':cell,'stage':'pilot' if pilot else 'confirmation','j':j,
                'nearest':int(j==nearest),'validation_selected':int(j==valj),
                'constant':int(h.min()==h.max()),'D':int((q!=h).sum()),'A':len(ii),
                'Q_minus_C':k['a']-k['b'],'d':d,'e':e,'n00':k['n00'],'n11':k['n11']}
            initial=hulls(k)[0];init_eps=decision(initial)[0];init_exact=exact_decision(initial)
            truth=hulls(k,(int(la[groups==0].sum()),)*2+(int(la[groups==1].sum()),)*2)[0][0]
            if init_eps:
                initial_choice=decision(initial)[1]
                initial_worse+=int((truth<0 and initial_choice==1) or (truth>0 and initial_choice==0))
            assert abs(float(truth)-(metric(q,y,'f1')-metric(h,y,'f1')))<1e-14
            pairrows.append({**base,'initial_exact':int(init_exact),'initial_epsilon':int(init_eps),
                'affine_width':abs(d)*k['n00']+abs(e)*k['n11'],'truth':float(truth)})
            for interior in [True,False]:
                for known in [False,True]:
                    paired,separate=hulls(k,prevalence=int(y.sum()) if known else None,interior=interior)
                    assert separate[0]<=paired[0]<=truth<=paired[1]<=separate[1]
                    if known:
                        p=int(y.sum());lo=max(0,p-k['u']-k['v']-k['n00']);hi=min(k['n11'],p-k['u']-k['v'])
                        expected=F(2*abs(k['b']-k['a'])*(hi-lo),(p+k['a']+k['n11'])*(p+k['b']+k['n11'])) if p else F(0)
                        assert paired[1]-paired[0]==expected
                        # Explicit mechanism for the dependence ablation at known P.
                        if p:
                            sep_expected=F(2*(hi-lo),p+k['a']+k['n11'])+F(2*(hi-lo),p+k['b']+k['n11'])
                            assert separate[1]-separate[0]==sep_expected
                    for name,hull in [('paired',paired),('separate',separate)]:
                        intervalrows.append({**base,'interior':int(interior),'known_P':int(known),'method':name,
                            'lower':float(hull[0]),'upper':float(hull[1]),'width':float(hull[1]-hull[0]),
                            'exact':int(exact_decision(hull)),'weak':int(decision(hull,F(0))[0]),
                            'epsilon':int(decision(hull)[0]),
                            'material':int(hull[0]<=F(-1,100) and hull[1]>=F(1,100))})
            cache={}
            pair_worse=0
            for rep in range(REPS):
                for pi,order in enumerate(orders(groups,w,rep)):
                    exact,_,_=curve(const,w,la,order);assert exact==old[ix,pi,rep],(ix,pi,rep)
                    pref=prefix_bounds(k,groups,la,order)
                    stop,choice=first_stop(k,pref,cache)
                    assert stop<=exact
                    realized=max(F(0),-truth) if choice[1] else max(F(0),truth)
                    assert realized<=F(1,100);max_realized=max(max_realized,realized)
                    stops[ix,pi,rep]=stop
                    choices[ix,pi,rep]=choice[1]
                    pair_worse+=int(realized>0)
            worse+=pair_worse;worse_pairs+=int(pair_worse>0)
            if j in tie_js:
                tie_record['outcomes'].append({'canonical_j':j,'D':base['D'],
                    'material':int(initial[0]<=F(-1,100) and initial[1]>=F(1,100)),
                    'exact_extra':old[ix].mean(axis=1).tolist(),'epsilon_extra':stops[ix].mean(axis=1).tolist()})
            for pi,policy in enumerate(POLICIES):
                costrows.append({**base,'policy':policy,'initial_exact':int(init_exact),'initial_epsilon':int(init_eps),
                    'exact_extra':float(old[ix,pi].mean()),'epsilon_extra':float(stops[ix,pi].mean()),
                    'exact_total':float(base['D']+old[ix,pi].mean()),'epsilon_total':float(base['D']+stops[ix,pi].mean())})
        ties.append(tie_record)
        print(cell,'pairs',len(pairrows),'seconds',round(time.time()-start),flush=True)
    assert len(pairrows)==3200
    writecsv(out/'intervals.csv',intervalrows);writecsv(out/'costs.csv',costrows);writecsv(out/'pairs.csv',pairrows)
    np.savez_compressed(out/'stops.npz',epsilon=stops,exact=old,choice_q=choices)
    summary={'intervals':{},'costs':{}}
    for stage in ['all','pilot','confirmation']:
        for interior in [True,False]:
            for known in [False,True]:
                for method in ['paired','separate']:
                    rr=[r for r in intervalrows if (stage=='all' or r['stage']==stage) and r['interior']==interior and r['known_P']==known and r['method']==method]
                    key=f'{stage}/interior={int(interior)}/known={int(known)}/{method}'
                    summary['intervals'][key]=aggregate(rr,['width','exact','weak','epsilon','material'])
    for cohort in ['all','nearest','validation_selected','exact_undecided','epsilon_undecided']:
        for stage in ['all','confirmation']:
            for policy in POLICIES:
                rr=[r for r in costrows if r['policy']==policy and (stage=='all' or r['stage']==stage)]
                if cohort in ['nearest','validation_selected']:rr=[r for r in rr if r[cohort]]
                elif cohort=='exact_undecided':rr=[r for r in rr if not r['initial_exact']]
                elif cohort=='epsilon_undecided':rr=[r for r in rr if not r['initial_epsilon']]
                summary['costs'][f'{stage}/{cohort}/{policy}']=aggregate(rr,['D','exact_extra','epsilon_extra','exact_total','epsilon_total'])
    summary['sensitivities']={}
    for cohort in ['nearest','validation_selected','nonconstant','equal_counts']:
        rr=[r for r in intervalrows if r['interior']==1 and r['known_P']==0 and r['method']=='paired']
        if cohort in ['nearest','validation_selected']:rr=[r for r in rr if r[cohort]]
        elif cohort=='nonconstant':rr=[r for r in rr if not r['constant']]
        else:rr=[r for r in rr if r['Q_minus_C']==0]
        summary['sensitivities'][cohort]=aggregate(rr,['material','epsilon','exact','width','D','Q_minus_C','n00','n11'])
        summary['sensitivities'][cohort]['material_count']=sum(r['material'] for r in rr)
        summary['sensitivities'][cohort]['strict_reversal_count']=sum(r['lower']<0<r['upper'] for r in rr)
    summary['verification']={'old_stops_identical':True,'trajectories':int(stops.size),'max_realized_regret':float(max_realized),
        'violations':0,'epsilon_boundary_is_rational':True,'elapsed_seconds':time.time()-start}
    summary['realized_choices']={'worse_trajectories':worse,'total_trajectories':int(stops.size),
        'pairs_with_worse_choice':worse_pairs,'initial_worse_pairs':initial_worse,
        'initial_epsilon_decided_pairs':sum(r['initial_epsilon'] for r in pairrows),
        'interpretation':'dependent retrospective choices; worse by at most epsilon, not a certification violation'}
    tie_summary={'cells_with_ties':sum(len(t['candidates'])>1 for t in ties),
        'material_count_range':[sum(min(t['material'] for t in r['outcomes']) for r in ties),sum(max(t['material'] for t in r['outcomes']) for r in ties)],'cost_ranges':{}}
    for pi,policy in enumerate(POLICIES):
        for goal in ['exact','epsilon']:
            for total in [False,True]:
                key=f'{policy}/{goal}/{"total" if total else "extra"}'
                tie_summary['cost_ranges'][key]=[float(np.mean([fn(t[f'{goal}_extra'][pi]+(t['D'] if total else 0) for t in r['outcomes']) for r in ties])) for fn in [min,max]]
    write(out/'validation_ties.json',{'summary':tie_summary,'cells':ties})
    summary['validation_ties']=tie_summary
    write(out/'summary.json',summary)
    rec['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    rec['outputs']={name:sha(out/name) for name in ['intervals.csv','costs.csv','pairs.csv','stops.npz','summary.json','validation_ties.json']}
    write(out/'execution.json',rec)

if __name__=='__main__':main()
