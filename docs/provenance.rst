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
   current repository interface ``v1.2.0``. See ``RELEASE.json`` for access and
   publication status. A reserved DOI is not evidence of a public deposit.

Reuse and original material
---------------------------

``inputs/data/`` contains 90 frozen derived files. ``DATA_MANIFEST.json`` maps
their SHA-256 hashes. ``inputs/validation_v3/`` contains 4140 validation scores
(36 x 115 candidates), configurations, selection rule and source hashes.
The underlying raw validation caches and original feature tables are not bundled.
No model is refit and no new physical quantum execution is required.

The selection uses maximum validation balanced accuracy with lexicographic
configuration tie-breaking. It was applied retrospectively before examining
the newly selected target results. It is not an invented historical F1 selection.

``PROTOCOLO_PILOTO.txt`` and its lock preserve the original protocol.
``DECISION_TRAS_PILOTO.txt`` and ``REVISION_V3_PROTOCOL.txt`` retain the actual
decisions and later retrospective plan. The original Spanish records remain
unchanged; this English guide explains how to interpret them. ``results/``
contains their execution records, not a reconstructed appearance of preregistration.

``closure_v4/weak_zero_diagnostic.json`` and its array preserve the earlier
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
``NOVEDAD_TDC_Y_ANTECEDENTES.txt`` and the manuscript.

Guarantees assume fixed binary predictions and correct labels and concern a
finite batch and a pair of models. They do not establish generalization,
performance under label noise, macro-F1, multiclass or model-family guarantees.
The benchmark is retrospective, narrow and dependent; a reserved analytical
subset is not prospective confirmation. Compatible extremes need not be likely.

Integrity and review
--------------------

``provenance/v1.1.0_manifest.json`` preserves the previous full manifest.
``provenance/scientific_snapshot.json`` anchors 195 unchanged scientific files
to commit ``c11d6e1bfd34630c075f4a1dd2b8e5b57275011f``. The current
``PACKAGE_MANIFEST.json`` also covers the new tools and documentation.

The V4 records under ``review_claude/reports_v4/`` describe actual independent
AI review by Claude Fable 5.1 with xhigh effort and the focused correction check.
They do not constitute conference peer review. A missing pair of protocol files
in the reviewer's second isolated copy was resolved in the released artifact
and checked by clean extraction. The manuscript and its PDF have not changed
during the repository-interface update. The new interface has its own tests
and CI; it is not retrospectively attributed to Claude's manuscript review.

Licenses and authorship
-----------------------

The confirmed four authors, order, affiliation, roles and absence of specific
funding are retained. AI assistance and author responsibility are disclosed in
the paper. Software/results use BSD-3-Clause, the manuscript CC BY 4.0, and the
ESANN template its original license. See ``THIRD_PARTY_NOTICES.txt`` for details.
No original dataset rights are conveyed by the derived artifact.
