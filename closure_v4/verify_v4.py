"""Verify V4 additions and their linkage to the unchanged V3 evidence."""
from pathlib import Path
import json,hashlib,sys,subprocess
H=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
e=json.loads((H/'results/v4/execution.json').read_text())
assert e['script_sha256']==sha(H/'closure_v4/analyze.py')
assert e['baseline_diagnostic_sha256']==sha(H/'closure_v4/weak_zero_diagnostic.json')
for group in ['sources','outputs']:
    for name,digest in e[group].items():assert sha(H/name)==digest,(group,name)
assert e['figure_sha256']==sha(H/'manuscript/tolerance_sensitivity.pdf')
t=json.loads((H/'results/v4/table_trace.json').read_text())
assert t['script_sha256']==sha(H/'closure_v4/render_table.py')
assert t['source_sha256']==sha(H/'manuscript/cost_rows.tex')
assert t['output_sha256']==sha(H/'manuscript/cost_rows_v4.tex')
s=json.loads((H/'results/v4/summary.json').read_text())
assert s['weak_trajectories_verified']==307200
assert s['weak_array_sha256']==sha(H/'closure_v4/weak_zero_stops.npz')
assert len(s['sensitivity'])==6
for r in s['sensitivity']:
    assert r['all']['rows']==3200 and r['all']['cells']==36
    assert r['validation']['rows']==r['validation']['cells']==36
    assert r['reserved']['rows']==2399 and r['reserved']['cells']==28
subprocess.run([sys.executable,'-B',str(H/'verify.py')],cwd=H,check=True)
from pypdf import PdfReader
r=PdfReader(H/'output/pdf/paper.pdf');text='\n'.join(p.extract_text() for p in r.pages)
assert '23647323' in text and '23642981' not in text
for value in ['120.92','92.25','121.16','92.57','74.59','40.29','79.15','79.46','3/36','6/36','14.0/77.0/188.4']:assert value in text,value
result={'v4_provenance_verified':True,'figure_and_table_verified':True,'paper_numbers_present':True,
        'scientific_v3_unchanged':True,'pdf_sha256':sha(H/'output/pdf/paper.pdf'),
        'sources':{name:sha(H/name) for name in ['manuscript/paper.tex','manuscript/tolerance_sensitivity.pdf','manuscript/cost_rows_v4.tex','closure_v4/analyze.py','closure_v4/render_table.py','closure_v4/verify_v4.py']}}
(H/'results/v4_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result))
