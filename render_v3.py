"""Generate manuscript tables directly from V3 cell-weighted summaries."""
import json
from pilot import HERE,sha,write

def main():
    s=json.loads((HERE/'results/v3/summary.json').read_text());lines=[]
    for known,label in [(0,'Unknown'),(1,'Exact')]:
        for method,name in [('paired','Paired'),('separate','Separate')]:
            r=s['intervals'][f'confirmation/interior=1/known={known}/{method}']['cell_mean']
            lines.append(f"{label} & {name} & {r['width']:.3f} & {100*r['exact']:.2f} & {100*r['epsilon']:.2f} \\\\")
    (HERE/'manuscript/interval_rows.tex').write_text('\n'.join(lines[:-1]+[lines[-1][:-2]])+'\n')
    lines=[]
    for cohort,label in [('all','All pairs'),('validation_selected','Validation'),('nearest','Nearest')]:
        for policy,name in [('uniform','Uniform'),('alternating','Alternating'),('magnitude','Magnitude')]:
            r=s['costs'][f'all/{cohort}/{policy}']['cell_mean']
            lines.append(f"{label} & {name} & {r['D']:.1f} & {r['exact_extra']:.2f} & {r['epsilon_extra']:.2f} & {r['exact_total']:.2f} & {r['epsilon_total']:.2f} \\\\")
    (HERE/'manuscript/cost_rows.tex').write_text('\n'.join(lines[:-1]+[lines[-1][:-2]])+'\n')
    write(HERE/'results/v3/table_trace.json',{'source_sha256':sha(HERE/'results/v3/summary.json'),
        'script_sha256':sha(HERE/'render_v3.py'),'outputs':{f:sha(HERE/'manuscript'/f) for f in ['interval_rows.tex','cost_rows.tex']}})

if __name__=='__main__':main()
