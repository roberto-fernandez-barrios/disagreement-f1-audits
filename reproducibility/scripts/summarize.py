"""Descriptive cell-level summaries and publication figure; no iid-pair inference."""
import csv,json
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pilot import HERE,write

SOURCES=['BRFSS','ACS','EMBER','ToN-IoT','UNSW-NB15']
def source(task):
    if 'brfss' in task:return 'BRFSS'
    if 'acs' in task:return 'ACS'
    if 'ember' in task:return 'EMBER'
    if 'toniot' in task:return 'ToN-IoT'
    return 'UNSW-NB15'
def read(p):
    with p.open(encoding='utf-8') as f:return list(csv.DictReader(f))
def mean(rr,k):return float(np.mean([float(r[k]) for r in rr])) if rr else None

def main():
    rows=[]
    for stage in ['pilot','confirmation']:
        for r in read(HERE/f'results/{stage}/pairs.csv'):
            r['stage']=stage;r['source']=source(r['task']);rows.append(r)
    cells=defaultdict(list)
    for r in rows:cells[r['cell']].append(r)
    summaries=[]
    for cell,rr in cells.items():
        f1=[r for r in rr if r['metric']=='f1'];ba=[r for r in rr if r['metric']=='ba']
        r={'cell':cell,'source':rr[0]['source'],'stage':rr[0]['stage'],'pairs':len(f1),
           'ba_material':mean(ba,'material_reversal'),'f1_material':mean(f1,'material_reversal'),
           'f1_oracle_material':mean(f1,'oracle_material_reversal'),
           'f1_strict':mean(f1,'strict_reversal'),'f1_oracle_strict':mean(f1,'oracle_strict_reversal')}
        # Sensitivity: one closest-prediction comparator, chosen without labels.
        closest=min(f1,key=lambda z:(int(z['a'])+int(z['b']),int(z['j'])))
        r['nearest_material']=int(closest['material_reversal']);r['nearest_strict']=int(closest['strict_reversal'])
        r['nearest_D']=int(closest['a'])+int(closest['b']);r['nearest_j']=int(closest['j'])
        r['duplicate_weighted_f1']=float(np.average([int(z['material_reversal']) for z in f1],weights=[int(z['duplicate_count']) for z in f1]))
        r['boundary_changes']=sum((abs(float(z['lower'])-float(z['boundary_lower']))>1e-12 or abs(float(z['upper'])-float(z['boundary_upper']))>1e-12) for z in f1)
        summaries.append(r)
    keys=['ba_material','f1_material','f1_oracle_material','f1_strict','f1_oracle_strict','nearest_material','nearest_strict','nearest_D','duplicate_weighted_f1']
    def agg(rr):return {'cells':len(rr),'pairs':sum(r['pairs'] for r in rr),**{k:mean(rr,k) for k in keys}}
    overall={stage:agg([r for r in summaries if stage=='all' or r['stage']==stage]) for stage in ['pilot','confirmation','all']}
    bysource={s:agg([r for r in summaries if r['source']==s]) for s in SOURCES}
    audit=read(HERE/'results/audit/pairs.csv')
    acells=defaultdict(list)
    for r in audit:acells[r['cell']].append(r)
    astats=[]
    for cell,rr in acells.items():
        for policy in ['uniform','alternating','magnitude']:
            allr=[r for r in rr if r['policy']==policy]
            amb=[r for r in allr if r['initially_decided']=='0']
            astats.append({'cell':cell,'source':source(rr[0]['task']),'stage':rr[0]['stage'],'policy':policy,
                'ambiguous_pairs':len(amb),'all_pairs':len(allr),'mean_extra_all':mean(allr,'mean_extra'),
                'mean_extra_ambiguous':mean(amb,'mean_extra'),'mean_total_ambiguous':mean(amb,'mean_total'),
                'certified_25_ambiguous':mean(amb,'certified_0.25'),'certified_50_ambiguous':mean(amb,'certified_0.5')})
    aa={p:{k:mean([r for r in astats if r['policy']==p and r[k] is not None],k) for k in ['mean_extra_all','mean_extra_ambiguous','mean_total_ambiguous','certified_25_ambiguous','certified_50_ambiguous']} for p in ['uniform','alternating','magnitude']}
    result={'overall':overall,'by_source':bysource,'cells':summaries,'audit':aa,'audit_cells':astats,
            'boundary_changed_intervals':sum(r['boundary_changes'] for r in summaries)}
    stops=np.load(HERE/'results/audit/stops.npz')['stops']
    indexes={cell:[int(r['index']) for r in rr if r['policy']=='uniform' and r['initially_decided']=='0'] for cell,rr in acells.items()}
    grand=np.array([stops[ii].mean(axis=0) for ii in indexes.values() if ii]).mean(axis=0)
    result['audit_order_variation']={p:{'min_grand_mean':float(grand[j].min()),'max_grand_mean':float(grand[j].max())} for j,p in enumerate(['uniform','alternating','magnitude'])}
    result['audit_ambiguous_cells']=sum(bool(ii) for ii in indexes.values())
    result['audit_ambiguous_pairs']=sum(map(len,indexes.values()))
    write(HERE/'results/summary.json',result)
    # Main figure: source-level means; marker/bar patterns remain clear in grayscale.
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':600})
    fig,axes=plt.subplots(2,1,figsize=(4.8,4.1),layout='constrained')
    x=np.arange(5)
    for k,label,offset,color,hatch in [('f1_material','Unknown prevalence',-.18,'.35',''),('f1_oracle_material','Known prevalence',.18,'.8','///')]:
        axes[0].bar(x+offset,[100*bysource[s][k] for s in SOURCES],width=.34,label=label,color=color,hatch=hatch,edgecolor='black',linewidth=.5)
    axes[0].set_xticks(x,SOURCES);axes[0].set_ylabel('Material reversals (%)');axes[0].set_ylim(0,42)
    axes[0].legend(fontsize=7,ncol=2,loc='upper right');axes[0].set_title('(a) F1 rankings after all disagreements are labeled',loc='left',fontsize=8)
    for j,(p,label,color,hatch) in enumerate([('uniform','Uniform','.8',''),('alternating','Alternating','.55','///'),('magnitude','Magnitude','.25','...')]):
        yy=[mean([r for r in astats if r['source']==s and r['policy']==p and r['mean_extra_ambiguous'] is not None],'mean_extra_ambiguous') for s in SOURCES]
        axes[1].bar(x+(j-1)*.24,yy,width=.23,label=label,color=color,hatch=hatch,edgecolor='black',linewidth=.5)
    axes[1].set_xticks(x,SOURCES);axes[1].set_ylabel('Additional labels');axes[1].set_ylim(0,380)
    axes[1].legend(fontsize=7,ncol=3,loc='upper right');axes[1].set_title('(b) Resolve initially undecided F1 signs',loc='left',fontsize=8)
    folder=HERE/'results/original_figures';folder.mkdir(parents=True,exist_ok=True)
    fig.savefig(folder/'results.png',dpi=600);fig.savefig(folder/'results.svg');plt.close(fig)
    print(json.dumps({'overall':overall,'by_source':bysource,'audit':aa,'boundary_changed':result['boundary_changed_intervals']},indent=2))

if __name__=='__main__':main()
