When Disagreement Labels Do Not Identify F1 Rankings
==================================================

Reproducibility artifact 1.1.0 for the six-page author manuscript V4,
prepared for the general track of ESANN 2027. See the release/Zenodo record
for current submission status; this artifact does not imply acceptance.

Permanent version: https://doi.org/10.5281/zenodo.23647323

Repository: https://github.com/roberto-fernandez-barrios/disagreement-f1-audits

Roberto Fernández-Barrios, Iker Pastor-López, Asier González-Santocildes,
and Pablo García Bringas. Faculty of Engineering, University of Deusto.

What the audit does
-------------------

Given two fixed binary prediction vectors, labels on all their disagreements,
and optionally exact prevalence, the audit computes the sharp F1-difference
interval over compatible completions. It either certifies a choice or requires
additional agreement labels. It separates strict-winner/exact-tie identification,
a weak winner with zero loss, and a minimax choice with at most 0.01 absolute F1
loss. Equal predicted-positive counts identify the sign without prevalence.
The result specializes TDC/Polo partial-identification frameworks; the explicit
audit and its decision consequences form an incremental contribution.

Version 1.1.0 adds the verified weak-zero control and an initial-certification
versus tolerance figure, plus clearer exposition and direct source attribution.
The underlying benchmark, original sign stops and positive-tolerance trajectories
are unchanged: 36 dependent cells, 3,200 pairs, three query policies and 32 seeds.
The initial interval analysis retains 0<P<n; query trajectories include P=0,n.
All additions are retrospective. The original eight-cell pilot and 28-cell
analytical holdout remain distinguishable; this is not a prospective study.

Reproduce
---------

Requirements: Python, numpy, matplotlib, pypdf and pdfplumber; versions are in
CONFIG.json and execution records. No network, original feature data, training
or external provider is needed. Verify the supplied package::

    python -B closure_v4/verify_v4.py

Reconstruct only the additions to V3 (including every weak-zero stop and the
six-point tolerance sensitivity), then render the shortened table::

    python -B closure_v4/analyze.py
    python -B closure_v4/render_table.py

Compile with an existing MiKTeX installation and verify::

    python -B build.py
    python -B closure_v4/verify_v4.py

For TeX Live, adapt only the MiKTeX-specific --disable-installer option in
build.py. The official template is included; no automatic installation occurs.
To reconstruct the older V3 campaign as well, run ``python -B reproduce.py``
before the V4 commands above. It need not be repeated for editorial changes.
The legacy package.py builds the earlier review layout; use the published
versioned ZIP for this complete V4 release.

Evidence and interpretation
---------------------------

* output/pdf/paper.pdf and manuscript/: delivered PDF, sources, vector figure.
* inputs/data/: 90 frozen derived TDC files (DATA_MANIFEST.json).
* inputs/validation_v3/: 4,140 source/ID-validation scores, rule and source hashes.
* results/v3/: original paired/marginal bounds, costs, selections and trajectories.
* results/v4/: zero-loss costs, rational tolerance sensitivity, descriptive cell
  dispersion, execution record and table trace.
* closure_v4/weak_zero_*: preserved earlier reviewer diagnostic and stop array,
  independently checked by analyze.py; not a retrospective preregistration.
* PROTOCOLO_PILOTO.txt and its lock: unchanged original protocol.
* REVISION_V3_PROTOCOL.txt and closure_v4/RESEARCH_NOTE.txt: retrospective context.
* results/reproduction.json: unchanged V3 scientific code/input/output hashes.
* results/v4_verification.json and results/clean_reproduction_v4.json: checks.
* PACKAGE_MANIFEST.json: SHA-256 for each distributed file except itself.

Means are averaged over orders, then pairs within cells, then cells; pair-weighted
alternatives are labeled separately. The cells, pairs and seeds are dependent.
The figure uses all 36 cells: 79.15% at tolerance 0.01 differs from the 79.46%
in the 28 reserved cells. Ranges are descriptive, not confidence intervals.
Full labels verify realized regret but do not select comparators or query orders.
The closest-Hamming 3/36 and validation-selected 6/36 material ambiguities are
different designs from the all-configuration pool. Costs are not universal minima.

No raw feature tables, other manuscripts, private review prompts or credentials
are redistributed. Raw validation caches are not bundled; derived metrics and
locally verified source hashes are supplied. Acquisition scripts are retained
for provenance and are not needed for autonomous reconstruction.

Provenance and licenses
-----------------------

The theoretical TDC preprint https://arxiv.org/abs/2610.00080v1 is distinct from
its prediction artifact https://doi.org/10.5281/zenodo.21776862 (version 1.1.6)
and from this audit's artifact 1.1.0. See CITATION.cff and THIRD_PARTY_NOTICES.txt.
Software/results: BSD-3-Clause; article: CC BY 4.0; template: original license.
Codex assisted literature, design, mathematical checks, code, analysis and writing;
Claude Fable 5.1 with xhigh effort provided independent AI review. This is not
conference peer review. The authors retain responsibility. No specific funding.
