"""Package the local review deliverable; no upload or publication."""
from pathlib import Path
import hashlib,json,zipfile
HERE=Path(__file__).resolve().parent
files=[]
files += [p for p in HERE.iterdir() if p.is_file() and p.suffix in {'.py','.txt','.json'} and p.name!='PACKAGE_MANIFEST.json']
for folder in ['inputs/data','inputs/validation_v3','manuscript','results','references/template','review_claude/reports']:
    files += [p for p in (HERE/folder).rglob('*') if p.is_file() and p.suffix!='.pyc' and 'console' not in p.name]
files += [HERE/'references'/p for p in ['BIBLIOGRAFIA_VERIFICADA.txt','manifest.json','extra_manifest.json','revision_sources.json','TDC_COMPARISON_SOURCES.json','v3_sources.json']]
files += [HERE/'output/pdf'/p for p in ['paper.pdf','paper.log','validation.json','build_1.txt','build_2.txt']]
files=sorted(set(files))
manifest={p.relative_to(HERE).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in files}
mp=HERE/'PACKAGE_MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
out=HERE/'output/ESANN2027_review.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
    for p in files+[mp]:z.write(p,p.relative_to(HERE).as_posix())
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    for name,record in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==record['sha256']
print(json.dumps({'zip':str(out),'files':len(files)+1,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
