"""Validate immutable inputs, protocols, exact mathematical checks, and PDF layout."""
from pathlib import Path
import json,hashlib
from pypdf import PdfReader
from test_decision import main as test
from audit import validate
from verify_v3 import main as verify_v3
import pilot
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    checks=json.loads((HERE/'DATA_MANIFEST.json').read_text())
    for p,digest in checks.items():assert sha(HERE/p.replace('\\','/'))==digest,p
    # Deliberately point original-project paths at a nonexistent directory.
    # All 108 case-file references (90 distinct files) must resolve from snapshots.
    oldroot,oldtdc=pilot.ROOT,pilot.TDC
    pilot.ROOT=HERE/'tmp/original_projects_not_present'
    assert not pilot.ROOT.exists()
    pilot.TDC=pilot.ROOT/'articulos/principales/target_domain_certificates'
    refs=[]
    for case in pilot.cases():
        for p in case[-3:]:pilot.snapshot(p,refs)
    assert len(refs)==108
    pilot.ROOT,pilot.TDC=oldroot,oldtdc
    lock=json.loads((HERE/'PROTOCOLO_PILOTO.lock.json').read_text())
    assert sha(HERE/'PROTOCOLO_PILOTO.txt')==lock['sha256']
    checked_code = 0
    for stage in ['pilot','confirmation','audit']:
        record=json.loads((HERE/f'results/{stage}/execution.json').read_text())
        for f,digest in record['code'].items():
            assert sha(HERE/f)==digest, f'{stage}: stale code hash: {f}'
            checked_code += 1
    repro=json.loads((HERE/'results/reproduction.json').read_text())
    assert 'completed_utc' in repro
    for group in ['code','inputs','outputs']:
        for f,digest in repro[group].items():
            assert sha(HERE/f)==digest, f'reproduction {group}: {f}'
    build=json.loads((HERE/'output/pdf/validation.json').read_text())
    for f,digest in build['sources'].items():
        assert sha(HERE/f)==digest, f'PDF source: {f}'
    pdf=HERE/'output/pdf/paper.pdf';r=PdfReader(pdf)
    assert len(r.pages)==6
    for p in r.pages:
        assert abs(float(p.mediabox.width)-595.276)<.01
        assert abs(float(p.mediabox.height)-841.890)<.01
    log=(HERE/'output/pdf/paper.log').read_text(encoding='utf-8',errors='replace')
    assert 'Overfull' not in log
    assert 'undefined references' not in log.lower()
    assert sha(pdf)==build['sha256']
    v3=verify_v3()
    report={'v3':v3,'data_files_verified':len(checks),'protocol_sha256':lock['sha256'],
        'enumeration':test(),'partial_audits':validate(),'pdf_pages':len(r.pages),'pdf_sha256':sha(pdf),
        'a4':True,'overfull_boxes':0,'undefined_references':False,'original_projects_required':False,
        'stage_code_hashes_verified':checked_code,'reproduction_manifest_verified':True,
        'pdf_sources_verified':True}
    (HERE/'results/final_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))

if __name__=='__main__':main()
