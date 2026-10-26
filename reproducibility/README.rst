Reproducibility record
======================

Run the public commands from the repository root; start with
`the reproduction guide <../docs/reproduction.rst>`_. This directory holds the
scientific execution record rather than the reader's main entry point.

* ``protocols/``: the original plans and subsequent research decisions.
* ``scripts/``: frozen analysis, rendering and scientific verification code.
* ``records/``: original execution records, checks and PDF build logs.
* ``manifests/``: original data and earlier release manifests.
* ``environment/``: the original scientific environment description.
* ``source_exports/``: the TDC validation exporters retained for provenance.
* ``history/``: earlier acquisition/packaging scripts, figures and notes.
* ``MANIFEST.json``: SHA-256 and size of every current delivered file except itself.
* ``frozen_files.json``: original path, current path and SHA-256 for frozen files.
* ``release.json`` and ``version.json``: repository and manuscript version records.

Why a path map is needed
------------------------

The original execution records identify scripts and inputs by both path and
hash. Editing those scripts to match a new folder layout would break that
historical chain. Version 1.3.0 instead moves their exact bytes and records a
one-to-one mapping in ``frozen_files.json``. No scientific input, output or
source file is reconstructed from a description.

``tools/manage.py`` first copies the public artifact into ``.work/``. It then
restores the recorded paths under that run's ``run/`` subdirectory and executes
the unchanged scientific scripts there. New interface tests exercise the public
layout. Original mathematical and provenance checks exercise the restored
layout. The wrapper checks the reference tree again when the command finishes.

All 191 retained frozen scientific/provenance files preserve their SHA-256.
The four AI-review reports formerly included in the artifact are available in
the `v1.2.0 archive <https://github.com/roberto-fernandez-barrios/disagreement-f1-audits/tree/v1.2.0/review_claude/reports_v4>`_.
Their exact hashes and links are recorded under ``archived`` in the map. They
are not required for any computation and are not fetched by the workflow.

Historical records retain their original paths, language and dates. The mapping
changes how the files are organized, not the chronology or scientific claims.
