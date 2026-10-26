"""Public commands. Scientific reference files are never modified by a run."""
from pathlib import Path
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
MANIFEST = "reproducibility/MANIFEST.json"
FROZEN = "reproducibility/frozen_files.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf8"))


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf8", newline="\n")


def safe_file(base, relative):
    path = (base / relative).resolve()
    if not path.is_relative_to(base.resolve()) or not path.is_file():
        raise ValueError(f"Missing or unsafe artifact path: {relative}")
    return path


def check_manifest(root=ROOT):
    manifest = read(root / MANIFEST)
    for name, rec in manifest.items():
        p = safe_file(root, name)
        if sha(p) != rec["sha256"] or p.stat().st_size != rec["bytes"]:
            raise ValueError(f"Artifact integrity mismatch: {name}")
    frozen = read(root / FROZEN)
    for name, rec in frozen["files"].items():
        if sha(safe_file(root, rec["path"])) != rec["sha256"]:
            raise ValueError(f"Frozen scientific file changed: {name}")
    return manifest


def stage(label, manifest):
    base = ROOT / ".work"
    base.mkdir(exist_ok=True)
    target = Path(tempfile.mkdtemp(prefix=label + "-", dir=base))
    for name in list(manifest) + [MANIFEST]:
        source = safe_file(ROOT, name)
        dest = target / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
    return target


def replay_tree(target):
    """Restore historical paths in a disposable run directory, preserving bytes.

    Old execution records and scripts refer to those paths. This explicit map
    lets readers browse a conventional layout without rewriting that evidence.
    Nothing is downloaded, inferred from labels, or changed in the release tree.
    """
    replay = target / "run"
    replay.mkdir()
    frozen = read(target / FROZEN)
    for original, rec in frozen["files"].items():
        dest = (replay / original).resolve()
        if not dest.is_relative_to(replay.resolve()):
            raise ValueError(f"Unsafe historical path: {original}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(safe_file(target, rec["path"]), dest)
    # The portable build records its own exact source in the build report.
    (replay / "tools").mkdir(exist_ok=True)
    shutil.copy2(target / "tools/manage.py", replay / "tools/manage.py")
    return replay


def reference(original):
    rec = read(ROOT / FROZEN)["files"][original]
    return safe_file(ROOT, rec["path"])


def execute(target, args, name):
    logs = target / "run_logs"; logs.mkdir(exist_ok=True)
    log = logs / (name + ".txt")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", MPLBACKEND="Agg", PYTHONUTF8="1")
    with log.open("w", encoding="utf8") as f:
        result = subprocess.run(args, cwd=target, env=env, stdout=f, stderr=subprocess.STDOUT)
    if result.returncode:
        tail = "\n".join(log.read_text(encoding="utf8", errors="replace").splitlines()[-18:])
        raise RuntimeError(f"{name} failed. Log: {log}\n{tail}")


def script(target, relative):
    execute(target, [sys.executable, "-B", relative], Path(relative).stem)


def equivalent(a, b, where=""):
    """Compare scientific values, not platform newline/ZIP metadata."""
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys(): raise ValueError(f"Different fields: {where}")
        for k in a: equivalent(a[k], b[k], f"{where}/{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b): raise ValueError(f"Different lengths: {where}")
        for i, (x, y) in enumerate(zip(a, b)): equivalent(x, y, f"{where}/{i}")
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if isinstance(a, int) and isinstance(b, int):
            if a != b: raise ValueError(f"Integer mismatch: {where}")
        elif not math.isclose(a, b, rel_tol=0, abs_tol=1e-12):
            raise ValueError(f"Numeric mismatch: {where}: {a} vs {b}")
    elif a != b:
        # CSV cells are strings. Text/configuration identifiers remain exact.
        try:
            if math.isclose(float(a), float(b), rel_tol=0, abs_tol=1e-12): return
        except (ValueError, TypeError): pass
        raise ValueError(f"Value mismatch: {where}: {a!r} vs {b!r}")


def compare(target, files):
    import numpy as np
    for name in files:
        left, right = reference(name), target / name
        if left.suffix == ".json":
            a, b = read(left), read(right)
            # This single documented field measures runtime, not a result.
            if name == "results/v3/summary.json":
                del a["verification"]["elapsed_seconds"]
                del b["verification"]["elapsed_seconds"]
            equivalent(a, b, name)
        elif left.suffix == ".csv":
            def rows(p):
                with p.open(newline="", encoding="utf8") as f: return list(csv.DictReader(f))
            equivalent(rows(left), rows(right), name)
        elif left.suffix == ".npz":
            with np.load(left) as a, np.load(right) as b:
                if set(a.files) != set(b.files): raise ValueError(f"NPZ keys: {name}")
                for key in a.files:
                    if not np.array_equal(a[key], b[key]): raise ValueError(f"NPZ array: {name}/{key}")
        else:
            if left.read_text(encoding="utf8") != right.read_text(encoding="utf8"):
                raise ValueError(f"Text mismatch: {name}")
    return files


def pdf_check(pdf):
    import pdfplumber
    from pypdf import PdfReader
    reader = PdfReader(pdf)
    if len(reader.pages) != 6: raise ValueError("The manuscript must have six pages")
    fonts = {}
    def resources(res):
        res = res.get_object()
        for key, obj in res.get("/Font", {}).items():
            font = obj.get_object()
            if font.get("/Subtype") == "/Type3": raise ValueError("Type 3 font")
            descendants = font.get("/DescendantFonts", [obj])
            for item in descendants:
                fd = item.get_object().get("/FontDescriptor")
                if fd is None or not any(k in fd.get_object() for k in ("/FontFile", "/FontFile2", "/FontFile3")):
                    raise ValueError(f"Unembedded font: {key}")
            fonts[str(font.get("/BaseFont", key))] = True
        for obj in res.get("/XObject", {}).values():
            obj = obj.get_object()
            if "/Resources" in obj: resources(obj["/Resources"])
    margins = []
    with pdfplumber.open(pdf) as doc:
        for page, parsed in zip(reader.pages, doc.pages):
            if abs(float(page.mediabox.width)-595.276) > .01 or abs(float(page.mediabox.height)-841.89) > .01:
                raise ValueError("PDF is not A4")
            resources(page["/Resources"])
            objects = parsed.chars + parsed.images + parsed.curves + parsed.rects + parsed.lines
            bounds = [min(o["x0"] for o in objects), parsed.width-max(o["x1"] for o in objects),
                      min(o["top"] for o in objects), parsed.height-max(o["bottom"] for o in objects)]
            mm = [v*25.4/72 for v in bounds]
            if not (mm[0] >= 43.995 and mm[1] >= 43.995 and min(mm[2:]) >= 52):
                raise ValueError(f"Insufficient margins: {mm}")
            margins.append(mm)
    return {"pages": 6, "a4": True, "all_fonts_embedded": True, "fonts": len(fonts),
            "ink_margins_mm_left_right_top_bottom": margins, "sha256": sha(pdf)}


def build(target):
    tex = shutil.which("pdflatex")
    if not tex: raise RuntimeError("Install MiKTeX or TeX Live separately; pdflatex is not on PATH")
    version = subprocess.check_output([tex, "--version"], text=True, errors="replace")
    flags = ["--disable-installer"] if "miktex" in version.lower() else []
    out = target / "output/pdf"
    cmd = [tex, *flags, "-interaction=nonstopmode", "-halt-on-error", "-file-line-error",
           f"-output-directory={out}", "paper.tex"]
    for i in (1, 2): execute(target / "manuscript", cmd, f"tex-{i}")
    log = (out / "paper.log").read_text(encoding="utf8", errors="replace")
    if "Overfull" in log or "undefined references" in log.lower(): raise ValueError("TeX warnings require correction")
    layout = pdf_check(out / "paper.pdf")
    sources = ["tools/manage.py", "manuscript/paper.tex", "manuscript/esannV2.cls",
               "manuscript/cost_rows_v4.tex", "manuscript/tolerance_sensitivity.pdf"]
    write(out / "validation.json", {**layout, "sources": {n: sha(target/n) for n in sources}})
    script(target, "closure_v4/verify_v4.py")
    return {"pdf": str(out / "paper.pdf"), "engine": version.splitlines()[0], "layout": layout}


def refresh_manifest():
    """Maintainer-only artifact allowlist; excludes local runs and environments."""
    top = {".gitattributes", ".gitignore", ".zenodo.json", "README.rst", "LICENSE",
           "CITATION.cff", "requirements.txt", "requirements.lock"}
    files = [ROOT/n for n in top]
    for folder in ("data", "results", "paper", "reproducibility", "src", "tools", "tests", "examples", "docs", ".github"):
        files.extend(p for p in (ROOT/folder).rglob("*") if p.is_file() and p.suffix != ".pyc" and "__pycache__" not in p.parts
                     and p.relative_to(ROOT).as_posix() != MANIFEST)
    write(ROOT/MANIFEST, {p.relative_to(ROOT).as_posix(): {"sha256": sha(p), "bytes": p.stat().st_size}
                         for p in sorted(set(files))})
    check_manifest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("demo", help="Run the ten-item counterexample without hidden labels")
    a = commands.add_parser("audit", help="Audit your own predictions and observed labels")
    a.add_argument("input", type=Path); a.add_argument("--epsilon", default="0.01")
    commands.add_parser("verify", help="Check frozen bytes, mathematics, interface and delivered PDF")
    r = commands.add_parser("reproduce", help="Reconstruct results in an isolated copy")
    r.add_argument("--scope", choices=("v4", "all"), default="v4")
    commands.add_parser("build", help="Compile and verify a separate PDF with MiKTeX or TeX Live")
    commands.add_parser("package", help="Create a deterministic versioned ZIP from the verified manifest")
    commands.add_parser("manifest", help="Maintainers: refresh the current release manifest")
    args = parser.parse_args()
    if args.command in ("demo", "audit"):
        from tools.audit_pair import audit
        source = ROOT/"examples/ten_items.json" if args.command == "demo" else args.input
        print(json.dumps(audit(read(source), getattr(args, "epsilon", "0.01")), indent=2)); return
    if args.command == "manifest": refresh_manifest(); print("PASS: manifest refreshed; frozen science unchanged"); return
    start = time.perf_counter(); manifest = check_manifest()
    target = stage(args.command, manifest)
    result = {"command": args.command, "reference_files_verified": len(manifest), "workspace": str(target)}
    replay = replay_tree(target) if args.command != "package" else None
    if replay is not None: result["scientific_workspace"] = str(replay)
    if args.command == "verify":
        script(replay, "closure_v4/verify_v4.py")
        execute(target, [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests"], "interface-tests")
        result["pdf"] = pdf_check(target/"paper/paper.pdf")
    elif args.command == "reproduce":
        if args.scope == "all":
            files = [f"results/{s}/{f}" for s in ("pilot", "confirmation") for f in ("pairs.csv", "cell_summary.json")]
            files += ["results/audit/stops.npz", "results/audit/pairs.csv", "results/summary.json"]
            files += ["results/v3/"+f for f in ("intervals.csv", "costs.csv", "pairs.csv", "stops.npz", "summary.json", "validation_ties.json")]
            files += ["manuscript/interval_rows.tex", "manuscript/cost_rows.tex"]
            for name in files: reference(name)
            prior = replay_tree(stage("prior-campaign", manifest))
            script(prior, "reproduce.py")
            result["prior_outputs_compared"] = compare(prior, files)
            result["excluded_performance_metadata"] = ["results/v3/summary.json: verification.elapsed_seconds"]
            result["prior_workspace"] = str(prior)
        script(replay, "closure_v4/analyze.py"); script(replay, "closure_v4/render_table.py")
        result["v4_outputs_compared"] = compare(replay, ["results/v4/summary.json", "results/v4/costs.csv", "results/v4/sensitivity.csv", "manuscript/cost_rows_v4.tex"])
        result["weak_zero_paths_verified"] = read(replay/"results/v4/summary.json")["weak_trajectories_verified"]
        result["float_comparison_absolute_tolerance"] = 1e-12
        result["figure"] = str(replay/"manuscript/tolerance_sensitivity.pdf")
        result["note"] = "Numeric reproduction. Rendering/ZIP metadata may differ by platform; reference files are unchanged."
    elif args.command == "build": result.update(build(replay))
    elif args.command == "package":
        version = read(ROOT/"reproducibility/release.json")["version"]
        archive = target/f"disagreement-f1-audits-v{version}.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=7) as z:
            for name in sorted(list(manifest)+[MANIFEST]):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                z.writestr(info, (ROOT/name).read_bytes(), compresslevel=7)
        with zipfile.ZipFile(archive) as z:
            if z.testzip() is not None: raise ValueError("ZIP CRC failure")
            for name, rec in manifest.items():
                if hashlib.sha256(z.read(name)).hexdigest() != rec["sha256"]: raise ValueError(name)
        result.update(archive=str(archive), sha256=sha(archive))
    check_manifest()
    result.update(status="passed", reference_tree_unchanged=True, elapsed_seconds=time.perf_counter()-start)
    write(target/"RUN_REPORT.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try: main()
    except (ValueError, RuntimeError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr); sys.exit(1)
