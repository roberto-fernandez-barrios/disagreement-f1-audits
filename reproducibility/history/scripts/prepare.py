"""Read-only snapshots and public primary sources. Never runs source code."""
from pathlib import Path
import hashlib, json, datetime, urllib.request, concurrent.futures
from pypdf import PdfReader

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')

LOCAL=[
'AGENTS.md','JANUS_CONTINUITY.json','JANUS_PATHS.json',
'documento tesis/fuentes/preliminares.tex','documento tesis/fuentes/12_conclusiones.tex',
'documento tesis/fuentes/d_trazabilidad.tex','articulos/LEEME.txt',
'articulos/principales/target_domain_certificates/manuscript/sn-article.tex',
'articulos/principales/target_domain_certificates/manuscript/supplementary.tex',
'articulos/principales/target_domain_certificates/manuscript/sn-bibliography.bib',
'articulos/principales/target_domain_certificates/src/analysis/partial_identification.py',
'articulos/principales/validate-before-commit/manuscript/main_springer.tex',
'articulos/principales/certification-cost/RESEARCH_STATE.md',
'proyectos/Athena/hybrid-quantum-classical-integrity/publication/tdsc/main.tex',
'proyectos/Athena/athena-aegis-runtime-assurance/README.md',
'exploraciones/robustez_etiquetas_2026-10-23/INFORME.txt',
'exploraciones/seleccion_ACD_2026-10-23/INFORME_DECISION.txt',
'exploraciones/multiplicidad_candidatos_2026-10-23/INFORME_DECISION.txt',
'exploraciones/nueva_linea_decisiones_2026-10-23/LINEAS_Y_ANTECEDENTES.txt',
'exploraciones/metainvestigacion_fpr_corpus_2026-10-24/PROTOCOLO.txt',
]
PUBLIC={
'sawade2010':'https://papers.neurips.cc/paper_files/paper/2010/file/d7a728a67d909e714c0774e22cb806f2-Paper.pdf',
'sawade2012':'https://papers.nips.cc/paper/4495-active-comparison-of-prediction-models.pdf',
'polo2024':'https://papers.nips.cc/paper/2024/file/f4c6bec746b0aeca8c2cd15096f1ad1f-Paper-Conference.pdf',
'dervovic2025':'https://raw.githubusercontent.com/mlresearch/v258/main/assets/dervovic25a/dervovic25a.pdf',
'kossen2021':'https://proceedings.mlr.press/v139/kossen21a/kossen21a.pdf',
'coda2025':'https://openaccess.thecvf.com/content/ICCV2025/papers/Kay_Consensus-Driven_Active_Model_Selection_ICCV_2025_paper.pdf',
'esann_guidelines':'https://www.esann.org/author_guidelines',
'esann_dates':'https://www.esann.org/',
'esann_scope':'https://www.esann.org/node/3',
'esann_sessions':'https://www.esann.org/special-sessions',
'esann_exclusivity':'https://www.esann.org/node/6',
'ijcnn':'https://ijcnn.org/2027/authors/call-for-papers',
'ifipsec':'https://ifipsec.org/cfp.html',
'deusto':'https://www.deusto.es/document/es/dirs-guia-de-programa-ingenieria-en.pdf',
}
def fetch(item):
    key,url=item; suffix='.pdf' if '.pdf' in url else '.html'
    p=HERE/'references'/f'{key}{suffix}'
    row=dict(id=key,url=url,utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    try:
        if not p.exists():
            req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(req,timeout=35) as r: data=r.read(15000000)
            if suffix=='.pdf': assert data.startswith(b'%PDF')
            p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        if suffix=='.pdf':
            reader=PdfReader(p)
            text='\n\n'.join(f'=== PAGE {i+1} ===\n'+(pg.extract_text() or '') for i,pg in enumerate(reader.pages))
            p.with_suffix('.txt').write_text(text,encoding='utf8')
            row['pages']=len(reader.pages)
        row.update(status='downloaded',sha256=sha(p),bytes=p.stat().st_size,path=str(p.relative_to(HERE)))
    except Exception as e:row.update(status='failed',error=str(e))
    return row
if __name__=='__main__':
    rows=[]
    for rel in LOCAL:
        p=ROOT/rel
        if not p.is_file():rows.append(dict(relative=rel,status='not_found'));continue
        dst=HERE/'inputs'/'documents'/rel;dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists(): assert sha(dst)==sha(p),str(p)
        else:dst.write_bytes(p.read_bytes())
        rows.append(dict(relative=rel,status='copied',sha256=sha(p),bytes=p.stat().st_size))
    save(HERE/'inputs/documents_manifest.json',rows)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: out=list(pool.map(fetch,PUBLIC.items()))
    save(HERE/'references/manifest.json',out)
    print(json.dumps([dict(id=x['id'],status=x['status'],pages=x.get('pages'),error=x.get('error')) for x in out],indent=2))
