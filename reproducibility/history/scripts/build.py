"""Build the official-template review PDF using an existing local TeX install."""
from pathlib import Path
import shutil,subprocess,json,hashlib
from pypdf import PdfReader

HERE=Path(__file__).resolve().parent
source=HERE/'manuscript';out=HERE/'output/pdf';out.mkdir(parents=True,exist_ok=True)
style=HERE/'references/template/esannV2.cls'
shutil.copy2(style,source/'esannV2.cls')
tex=shutil.which('pdflatex')
if not tex:raise RuntimeError('An existing pdflatex installation is required; no auto-install is attempted.')
for run in range(2):
    result=subprocess.run([tex,'--disable-installer','-interaction=nonstopmode','-halt-on-error',
        '-file-line-error',f'-output-directory={out}','paper.tex'],cwd=source,capture_output=True,text=True,errors='replace')
    (out/f'build_{run+1}.txt').write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
    if result.returncode:raise RuntimeError(f'pdflatex failed; see {out}/build_{run+1}.txt')
reader=PdfReader(out/'paper.pdf')
report={'pages':len(reader.pages),'sha256':hashlib.sha256((out/'paper.pdf').read_bytes()).hexdigest(),
        'sources':{p.relative_to(HERE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in [HERE/'build.py', source/'paper.tex',source/'esannV2.cls',source/'interval_rows.tex',source/'cost_rows.tex']},
        'page_sizes_points':[[float(p.mediabox.width),float(p.mediabox.height)] for p in reader.pages],
        'template_sha256':hashlib.sha256(style.read_bytes()).hexdigest()}
(out/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(out/'extracted.txt').write_text('\n'.join(f'=== PAGE {i+1} ===\n'+p.extract_text() for i,p in enumerate(reader.pages)),encoding='utf-8')
print(json.dumps(report))
