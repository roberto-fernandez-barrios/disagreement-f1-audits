"""Archive public primary sources and the exact official template, for provenance."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json,urllib.request,hashlib,datetime
from pypdf import PdfReader
HERE=Path(__file__).resolve().parent
URLS={
 'musgrove2023':'https://www.nature.com/articles/s41598-023-48017-4.pdf',
 'gonzalez1985':'https://www.cs.columbia.edu/~verma/classes/uml/ref/clustering_minimize_intercluster_distance_gonzalez.pdf',
 'oglic2018':'https://proceedings.mlr.press/v80/oglic18a/oglic18a.pdf',
 'oglic2018supp':'https://proceedings.mlr.press/v80/oglic18a/oglic18a-supp.pdf',
 'template/esannV2.tex':'https://www.esann.org/system/files/downloads/esannV2.tex',
 'template/esannV2.cls':'https://www.esann.org/system/files/downloads/esannV2.cls'}
def one(k,u):
    p=HERE/'references'/(k if 'template/' in k else k+'.pdf');p.parent.mkdir(parents=True,exist_ok=True)
    if not p.exists():p.write_bytes(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read())
    if p.suffix=='.pdf':
        r=PdfReader(p);p.with_suffix('.txt').write_text('\n'.join(f'=== PAGE {i+1} ===\n'+x.extract_text() for i,x in enumerate(r.pages)),encoding='utf-8')
    return {'id':k,'url':u,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'path':str(p.relative_to(HERE)),'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=3) as pool:r=list(pool.map(lambda kv:one(*kv),URLS.items()))
    (HERE/'references/extra_manifest.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
    print('Sources archived:',len(r))
