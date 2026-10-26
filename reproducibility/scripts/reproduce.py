"""Rebuild results exclusively from bundled frozen inputs; no network or fitting."""
from pathlib import Path
import subprocess,sys,json,hashlib,datetime
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
record={'started_utc':utc(),'execution_kind':'post-review reproduction, not a new preregistration',
        'code':{p.name:sha(p) for p in sorted(HERE.glob('*.py'))},
        'inputs':{f:sha(HERE/f) for f in ['DATA_MANIFEST.json','CONFIG.json','PROTOCOLO_PILOTO.txt','DECISION_TRAS_PILOTO.txt']}}
recordpath=HERE/'results/reproduction.json'
recordpath.write_text(json.dumps(record,indent=2),encoding='utf-8')
for script,args in [('pilot.py',['pilot']),('pilot.py',['confirmation']),('audit.py',[]),('summarize.py',[]),('revision_v3.py',[]),('render_v3.py',[])]:
    subprocess.run([sys.executable,'-B',str(HERE/script),*args],cwd=HERE,check=True)
record['completed_utc']=utc()
outputs=[p for stage in ['pilot','confirmation','audit'] for p in (HERE/'results'/stage).iterdir() if p.is_file()]
outputs += [HERE/'results/summary.json',HERE/'results/original_figures/results.png',HERE/'results/original_figures/results.svg']
outputs += [p for p in (HERE/'results/v3').iterdir() if p.is_file()]
outputs += [HERE/'manuscript/interval_rows.tex',HERE/'manuscript/cost_rows.tex']
record['outputs']={p.relative_to(HERE).as_posix():sha(p) for p in sorted(outputs)}
recordpath.write_text(json.dumps(record,indent=2),encoding='utf-8')
if '--pdf' in sys.argv:
    subprocess.run([sys.executable,'-B',str(HERE/'build.py')],cwd=HERE,check=True)
    subprocess.run([sys.executable,'-B',str(HERE/'verify.py')],cwd=HERE,check=True)
