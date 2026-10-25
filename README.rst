When Disagreement Labels Do Not Identify F1 Rankings
==================================================

Reproducibility artifact 1.0.0 for manuscript V3.1 (six pages), prepared for
ESANN 2027. This repository does not imply submission or acceptance.

Permanent release: https://doi.org/10.5281/zenodo.23642981

Repository: https://github.com/roberto-fernandez-barrios/disagreement-f1-audits

Roberto Fernández-Barrios, Iker Pastor-López, Asier González-Santocildes,
and Pablo García Bringas. Faculty of Engineering, University of Deusto.

What the artifact establishes
----------------------------

After labeling all disagreements between two frozen binary classifiers, a
finite-batch audit can retain ambiguity in their F1 ranking. The code computes
exact paired intervals and compares strict sign identification with a minimax
decision that loses at most 0.01 absolute F1 for every compatible completion.
Equal predicted-positive counts identify the sign without knowing prevalence.
Fixed-prevalence bounds specialize TDC and partial-identification frameworks;
the contribution is a concrete auditing criterion and its empirical analysis.

The retrospective benchmark has 36 dependent cells, 3,200 deduplicated pairs,
three policies and 32 orders. The original pilot/reserved-cell distinction is
preserved. New tolerance, interval and validation-comparator analyses were
performed retrospectively after review, not prospectively preregistered.
Results describe finite-batch identification, not population error rates.

Quick verification and full reproduction
---------------------------------------

Requirements: Python 3.13 (tested), numpy, matplotlib, pypdf, pdfplumber.
The supplied PDF and results can be verified without training or network::

    python -B verify.py

To reconstruct the entire scientific campaign and both manuscript tables::

    python -B reproduce.py

To also compile and validate the manuscript with an existing MiKTeX install::

    python -B reproduce.py --pdf

For TeX Live, adapt only the MiKTeX-specific --disable-installer option in
build.py. No automatic installation occurs. The official template is bundled.
Version details and dependencies are recorded in CONFIG.json and execution logs.

Scientific inputs and outputs
----------------------------

* output/pdf/paper.pdf: the six-page author manuscript; sources in manuscript/.
* inputs/data/: 90 frozen derived files from the TDC 1.1.6 artifact.
* inputs/validation_v3/: 4,140 source/ID-validation scores, selection and hashes.
* results/v3/summary.json: separate cell-weighted and pair-weighted summaries.
* results/v3/intervals.csv: paired and marginal intervals on identical feasible sets.
* results/v3/costs.csv and stops.npz: common-cohort costs and all query trajectories.
* results/v3/table_trace.json: direct linkage from results to the paper's tables.
* PROTOCOLO_PILOTO.txt and its lock: unchanged original protocol and timestamp.
* REVISION_V3_PROTOCOL.txt: transparently retrospective extension and diagnostics.
* results/reproduction.json: scientific code, input and output hashes.
* PACKAGE_MANIFEST.json: SHA-256 for each distributed file except itself.

No original feature datasets, other manuscripts, private revision snapshots,
review prompts or credentials are distributed. Source-validation raw caches are
not bundled; the derived metrics and locally checked source hashes are provided.
prepare.py, fetch_extra.py and prepare_validation_v3.py preserve acquisition
provenance and are not needed for autonomous reproduction.

Version and review provenance
-----------------------------

V3 underwent two independent Claude Code reviews using claude-fable-5-1 with
xhigh effort, with corrections checked and no material issues remaining.
This AI review is not editorial peer review. The V3 reviewed PDF SHA-256 is
00ef86ce626678e6c86d5d7d9a49e4b9c3ded0c3d0458f7290973f81e412d891.
V3.1 changes only the availability sentence in the manuscript and release
documentation. Scientific code, inputs, tables and experimental results are
byte-identical to V3; the campaign was not repeated for this URL-only change.
The current PDF is therefore not the same binary that Claude reviewed.
Codex assisted formulation, checks, programming, analysis and writing; Claude
assisted independent review. Authors remain responsible for the content.
No specific funding supported this article.

Licensing and citation
----------------------

Software and derived analysis outputs: BSD-3-Clause. Article text: CC BY 4.0.
The template retains its own license. See THIRD_PARTY_NOTICES.txt and CITATION.cff.
The theoretical TDC citation https://arxiv.org/abs/2610.00080v1 is distinct from
the prediction artifact https://doi.org/10.5281/zenodo.21776862 (version 1.1.6).
