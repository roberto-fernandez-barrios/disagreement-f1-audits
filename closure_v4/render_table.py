"""V4 prints all/validation rows; the unchanged V3 output retains all cohorts."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=H/'manuscript/cost_rows.tex';target=H/'manuscript/cost_rows_v4.tex'
lines=source.read_text(encoding='utf8').splitlines()
assert len(lines)==9 and all(x.startswith(('All pairs','Validation')) for x in lines[:6])
selected=lines[:6]
selected[-1]=selected[-1].rstrip()
if selected[-1].endswith('\\\\'):selected[-1]=selected[-1][:-2].rstrip()
target.write_text('\n'.join(selected),encoding='utf8')
(H/'results/v4/table_trace.json').write_text(json.dumps({'script_sha256':sha(Path(__file__)),
    'source_sha256':sha(source),'output_sha256':sha(target),'selection':'first six rows (all pairs and validation); no recalculation/rounding change'},indent=2),encoding='utf8')
