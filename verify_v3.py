"""Verify new provenance, deterministic selections, preserved results and layout."""
import csv,json
import numpy as np
import pdfplumber
from pilot import HERE,sha,write
from test_tolerance import main as test

def main(pdf=True):
    out=HERE/'results/v3'
    record=json.loads((out/'execution.json').read_text())
    for name,digest in record['code'].items():assert sha(HERE/name)==digest,name
    assert record['protocol_sha256']==sha(HERE/'REVISION_V3_PROTOCOL.txt')
    assert record['validation_input_sha256']==sha(HERE/'inputs/validation_v3/manifest.json')
    for name,digest in record['outputs'].items():assert sha(out/name)==digest,name
    manifest=json.loads((HERE/'inputs/validation_v3/manifest.json').read_text())
    for name,digest in manifest.items():assert sha(HERE/'inputs/validation_v3'/name)==digest
    with (HERE/'inputs/validation_v3/validation_scores.csv').open(newline='',encoding='utf8') as f:vals=list(csv.DictReader(f))
    choices=json.loads((HERE/'inputs/validation_v3/selection.json').read_text())['cells']
    for cell in choices:
        rr=[r for r in vals if r['cell']==cell['cell']];assert len(rr)==115
        winner=min(rr,key=lambda r:(-float(r['validation_balanced_accuracy']),r['cfg']))
        assert int(winner['j'])==cell['selected_j'] and winner['cfg']==cell['cfg']
    with (out/'intervals.csv').open(newline='',encoding='utf8') as f:new=list(csv.DictReader(f))
    old={}
    for stage in ['pilot','confirmation']:
        with (HERE/f'results/{stage}/pairs.csv').open(newline='',encoding='utf8') as f:
            for r in csv.DictReader(f):
                if r['metric']=='f1':old[(r['cell'],r['j'])]=r
    compared=0;boundary_equalities=0
    for r in new:
        if r['method']!='paired':continue
        prev=old[(r['cell'],r['j'])]
        prefix='oracle_' if r['known_P']=='1' else ('' if r['interior']=='1' else 'boundary_')
        for end in ['lower','upper']:assert abs(float(r[end])-float(prev[prefix+end]))<1e-12
        if r['interior']=='1':
            assert int(r['material'])==int(prev[('oracle_' if r['known_P']=='1' else '')+'material_reversal'])
            boundary_equalities+=int(float(r['lower'])==-.01 or float(r['upper'])==.01)
        compared+=1
    assert boundary_equalities==0
    oldstops=np.load(HERE/'results/audit/stops.npz')['stops'];newstops=np.load(out/'stops.npz')
    assert np.array_equal(oldstops,newstops['exact']) and (newstops['epsilon']<=oldstops).all()
    trace=json.loads((out/'table_trace.json').read_text())
    assert trace['source_sha256']==sha(out/'summary.json') and trace['script_sha256']==sha(HERE/'render_v3.py')
    for name,digest in trace['outputs'].items():assert sha(HERE/'manuscript'/name)==digest
    report={'tests':test(),'old_paired_intervals_preserved':compared,'boundary_equalities':boundary_equalities,
        'old_query_stops_preserved':int(oldstops.size),'validation_choices_recomputed':len(choices)}
    if pdf:
        pages=[]
        with pdfplumber.open(HERE/'output/pdf/paper.pdf') as doc:
            assert len(doc.pages)==6
            for i,p in enumerate(doc.pages):
                bbox=(min(c['x0'] for c in p.chars),min(c['top'] for c in p.chars),max(c['x1'] for c in p.chars),max(c['bottom'] for c in p.chars))
                margins=[bbox[0]*25.4/72,(p.width-bbox[2])*25.4/72,bbox[1]*25.4/72,(p.height-bbox[3])*25.4/72]
                # Horizontal 0.005 mm tolerance covers font/PDF coordinate rounding.
                assert margins[0]>=43.995 and margins[1]>=43.995,(i,margins)
                assert margins[2]>=52 and margins[3]>=52,(i,margins)
                pages.append(dict(zip(['left_mm','right_mm','top_mm','bottom_mm'],margins)))
        report['pdf_ink_margins']=pages;report['pdf_sha256']=sha(HERE/'output/pdf/paper.pdf')
    write(HERE/'results/v3_verification.json',report);print(json.dumps(report))
    return report

if __name__=='__main__':main()
