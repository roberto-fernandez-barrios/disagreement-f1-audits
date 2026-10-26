Provenance, scope and historical records
========================================

Three distinct references
-------------------------

1. TDC theory: Fernández-Barrios et al., *Sharp Target-Domain Certificates for
   Quantum-Kernel Advantage under Distribution Shift*,
   `arXiv:2610.00080v1 <https://arxiv.org/abs/2610.00080v1>`_. Theorem 1 and
   Section 4.5 are the theoretical antecedents.
2. TDC predictions: artifact **1.1.6**,
   `10.5281/zenodo.21776862 <https://doi.org/10.5281/zenodo.21776862>`_. This is
   the source of the frozen derived predictions, target labels and metadata.
3. The present F1 audit: scientific snapshot ``v1.1.0`` / manuscript V4;
   current repository interface ``v1.3.0``. See ``reproducibility/release.json`` for access and
   publication status. A reserved DOI is not evidence of a public deposit.

Reuse and original material
---------------------------

``data/predictions/`` contains 90 frozen derived files. ``reproducibility/manifests/original_data.json`` records
their historical paths and SHA-256 hashes. ``reproducibility/frozen_files.json``
maps those identifiers to current public paths. ``data/validation/`` contains 4140 validation scores
(36 x 115 candidates), configurations, selection rule and source hashes.
The underlying raw validation caches and original feature tables are not bundled.
No model is refit and no new physical quantum execution is required.

The selection uses maximum validation balanced accuracy with lexicographic
configuration tie-breaking. It was applied retrospectively before examining
the newly selected target results. It is not an invented historical F1 selection.

``reproducibility/protocols/pilot.txt`` and its lock preserve the original protocol.
``reproducibility/protocols/pilot_decision.txt`` and ``reproducibility/protocols/tolerance.txt`` retain the actual
decisions and later retrospective plan. The original Spanish records remain
unchanged; this English guide explains how to interpret them. ``reproducibility/records/``
contains their execution records, not a reconstructed appearance of preregistration.

``data/controls/weak_zero_diagnostic.json`` and its array preserve the earlier
review diagnostic. Its original generating script was not found. Both the V4
analysis and a separate reviewer implementation reproduced its values; this
closes numerical reproducibility without inventing the missing historical script.

Scientific scope
----------------

The fixed-prevalence characterization specializes TDC/Polo; enumeration of
prevalence and minimax regret are not claimed as new general principles. The
additional value is the explicit post-disagreement solution, its operational
choice/query criterion and the empirical information/cost consequences.
The comparison with nearby literature is preserved in
``reproducibility/history/novelty_comparison.txt`` and the manuscript.

Guarantees assume fixed binary predictions and correct labels and concern a
finite batch and a pair of models. They do not establish generalization,
performance under label noise, macro-F1, multiclass or model-family guarantees.
The benchmark is retrospective, narrow and dependent; a reserved analytical
subset is not prospective confirmation. Compatible extremes need not be likely.

Integrity and historical review
-------------------------------

``reproducibility/manifests/`` preserves the v1.1.0 and v1.2.0 manifests.
``reproducibility/frozen_files.json`` maps 191 unchanged scientific/provenance
files to their current paths and original SHA-256 hashes. They remain anchored
to commit ``c11d6e1bfd34630c075f4a1dd2b8e5b57275011f``. The current
``reproducibility/MANIFEST.json`` covers every delivered file except itself.
``reproducibility/README.rst`` explains the reversible execution layout.

Four AI-review reports are retained in the
`immutable v1.2.0 archive <https://github.com/roberto-fernandez-barrios/disagreement-f1-audits/tree/v1.2.0/review_claude/reports_v4>`_
and the authors' local record. Their exact hashes and URLs remain in the
``archived`` section of the path map. They are not required for reproducing any
result and are not bundled in the current reader-facing artifact.

Those records concern actual V4 review by Claude Fable 5.1, xhigh, and its
focused correction check. A missing pair of protocol files in the reviewer's
second isolated copy was resolved in the released artifact and checked by
clean extraction. This was AI review, not conference peer review. The public
interface and layout have separate tests and CI; they are not retrospectively
attributed to that manuscript review.

Licenses and authorship
-----------------------

The confirmed four authors, order, affiliation, roles and absence of specific
funding are retained. AI assistance and author responsibility are disclosed in
the paper. Software/results use BSD-3-Clause, the manuscript CC BY 4.0, and the
ESANN template its original license. See `license notices <licenses.rst>`_ for current paths and details.
No original dataset rights are conveyed by the derived artifact.
