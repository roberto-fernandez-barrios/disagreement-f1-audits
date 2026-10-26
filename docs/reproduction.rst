Reproduce the artifact
======================

Start from the versioned release ZIP, or check out its Git tag. Neither Git nor
the original thesis workspace is required after extracting the ZIP.

Environment
-----------

Python 3.13 is the supported and tested runtime. ``requirements.txt`` records
the direct analysis dependencies; ``requirements.lock`` pins all runtime
dependency versions resolved in a fresh environment. The archival environment
in ``reproducibility/environment/original.json`` describes the original scientific runs and is preserved.
The new environment is checked against those frozen results.

Create an environment with ``python -m venv .venv``. Install the lock using
``.venv/bin/python -m pip install -r requirements.lock`` on Linux/macOS or
``.venv/Scripts/python.exe -m pip install -r requirements.lock`` on Windows.
Use that same interpreter for every command below. Activation is optional;
no PowerShell execution-policy change is needed.

CI runs the numerical workflow on Ubuntu 24.04 and Windows 2022 with Python
3.13, and a TeX Live PDF build on Ubuntu. macOS installation syntax is shown
for convenience; macOS is not included in the tested CI matrix. No global
packages are installed by the scripts.

Verification
------------

``python tools/manage.py verify`` checks the full package manifest and the
191 frozen scientific/provenance files inherited from ``v1.1.0``. It then runs the existing
exact tests, audit checks and provenance chain, the new label-limited interface
tests, and the delivered PDF's page size, margins and embedded fonts.

The historical verifiers write result reports. The wrapper therefore copies
the manifest-listed files to a new ``.work/verify-*`` directory and reconstructs
the recorded historical paths under its ``run/`` subdirectory before running them. Its final check ensures the reference tree was not changed.

Reconstruction scopes
---------------------

``python tools/manage.py reproduce`` reconstructs the V4 additions: all 307200
zero-loss stopping points, six tolerance levels, descriptive cell dispersion,
the figure and shortened cost table. It reuses the frozen V3 positive-tolerance
trajectories, exactly as the V4 study did. This is the default CI scope.

``python tools/manage.py reproduce --scope all`` also reconstructs the original
pilot, 28-cell analytical holdout, exact-sign audit, paired/marginal intervals,
positive-tolerance trajectories, validation selection summaries and V3 tables.
The older campaign and V4 extension use separate working copies. This preserves
the historical hash chain instead of silently replacing V4's frozen inputs
with newly serialized outputs.

Scientific CSV/JSON values are compared to the reference with absolute tolerance
``1e-12`` and no relative tolerance; integer counts and NPZ arrays must match
exactly. The only excluded JSON field is
``results/tolerance/summary.json: verification.elapsed_seconds``, which measures
runtime. The V4 analysis itself checks every weak-zero stop against the saved
array. Timestamps, platform newline encoding, compressed-file metadata and
font-library serialization are not scientific estimands. Regenerated figures
may have different bytes across platforms even when all plotted values match.
The original files remain byte-identical and are separately hash-verified.

Every successful command prints ``"status": "passed"``, elapsed time and the
path to ``RUN_REPORT.json``. Detailed subprocess logs are in that run's
``run_logs/`` directories. A failure returns a nonzero exit code and a log path.
The scripts do not silently accept changed reference values.

PDF compilation
---------------

``python tools/manage.py build`` uses an existing ``pdflatex`` from either
MiKTeX or TeX Live. It detects the engine; the MiKTeX-only installer-disabling
flag is not passed to TeX Live. It performs two passes, checks six A4 pages,
embedded non-Type-3 fonts, no overfull boxes or undefined references, and
minimum ink margins of 44/44/52/52 mm (0.005 mm horizontal coordinate tolerance).

Required TeX packages: the included ESANN class, lmodern, graphicx, amsmath,
amssymb, array, booktabs and url. On a standard Ubuntu TeX Live installation,
``texlive-latex-recommended`` and ``lmodern`` supply the dependencies. Installing
TeX is a separate environment step; the command never installs it automatically.

The rebuilt PDF is placed under ``.work/build-*/run/output/pdf/``. It is checked
against the current sources and numerical claims. TeX engines and timestamps
can change PDF bytes; the canonical delivered PDF remains
``paper/paper.pdf`` with SHA-256
``515eddd63862fbdd1240308baba22067b50d9e009d692c61b41cc3cd5cc672ce``.

Runtime and resources
---------------------

No GPU, QPU, provider account, model fitting or original feature-table download
is involved. After dependencies are installed, the workflows operate offline.
Runs report their own elapsed time; the release validation record provides
measured reference timings. The full campaign costs more than the V4-only
reconstruction. Verification, reconstruction and compilation copy the public
tree and restore a separate execution tree, using roughly twice the expanded
artifact size per run (the full campaign uses a second such workspace).
Retain reports you need and remove old working copies
using your usual file manager. Reference files are outside those directories.

Historical execution paths
--------------------------

Use ``tools/manage.py`` as the public entry point. Scientific source files were
moved, not edited. Their recorded paths and SHA-256 hashes are mapped explicitly
by ``reproducibility/frozen_files.json``. Before verification, reconstruction or
compilation, the wrapper copies those bytes to their historical paths inside
``.work/<command>-*/run/``. It does not fetch files or reconstruct source code.

This keeps the original protocols, script hashes and execution records valid.
The raw scripts under ``reproducibility/scripts/`` and ``tests/scientific/`` are
not independent entry points in the reorganized tree. The current interface
tests run against the public layout; original scientific verifiers run against
the restored layout. Both are checked in CI. Legacy acquisition/packaging
scripts are retained under ``reproducibility/history/scripts/`` for provenance.

Versioning and packaging
------------------------

``python tools/manage.py package`` validates the current manifest and writes a
ZIP with sorted paths, normalized timestamps and fixed permissions. It checks
every entry's SHA-256 before reporting the archive hash. Repeating it in the
same supported environment yields identical ZIP bytes. The tag, release assets
and manifest identify the exact delivered version. The previous releases remain
available; new work never silently replaces an old artifact.
