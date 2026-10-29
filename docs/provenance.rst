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
   current release ``v1.4.0`` / manuscript V5. See ``reproducibility/release.json`` for access and
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

The fixed-prevalence characterization specializes Kuboyama/TDC/Polo; enumeration of
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

Benchmark lineage and V5 attribution
-----------------------------------

The F1 audit reuses predictions, not raw records or newly trained models.
The 20 BRFSS Diabetes and ACS FoodStamps cells derive from TableShift
(Gardner, Popovic and Schmidt, NeurIPS 36, 2023;
https://arxiv.org/abs/2312.07577), pinned upstream at
``fca9429814703a07e3902d005d46563a207b7f0a``. Their original sources are
CDC BRFSS and US Census ACS PUMS. The other 16 cells use eight security
scenarios from the TDC 1.1.6 release:

* EMBER histogram/byte-entropy ``m1`` and ``m2`` scenarios; Anderson and Roth,
  arXiv:1804.04637v2 (2018).
* UNSW-NB15 DoS/Reconnaissance, constructed and held-out attack scenarios;
  Moustafa and Slay, MilCIS (2015), DOI 10.1109/MilCIS.2015.7348942.
  Upstream scripts consume official training/test CSVs and 39 numeric features.
* ToN-IoT scanning, constructed and held-out attack scenarios. The effective
  source is original processed **network** ``train_test_network.csv``, not
  sensor telemetry and not NF-ToN-IoT. The upstream preparation script
  ``scripts/data/prepare_paper2_ton_iot_q1_gate.py`` names this RAW_PATH;
  ``scripts/netflow/run_netflow_grid.py`` consumes its
  ``ton_iot_ref_no_scanning_binary.csv`` / ``ton_iot_cur_scanning_binary.csv``
  exports. Metadata identifies the corresponding ``02``/``03`` prediction
  cells and source summary/target-index hashes. Use Moustafa, *A new distributed
  architecture for evaluating AI-based security systems at the edge: Network
  TON_IoT datasets*, Sustainable Cities and Society 72:102994 (2021),
  https://doi.org/10.1016/j.scs.2021.102994. The generic telemetry reference in
  upstream TDC does not identify this component; the preparation code does.

Original preparation excludes identifiers/label derivatives and encodes network
categories before the TDC experiments. No transformation is rerun here.
The exact reused prediction hashes remain in the historical data manifest.
The network task shift is a held-out attack/capture regime, not a verified
chronological split. Raw data rights remain with the benchmark providers.

Kuboyama (arXiv:2609.18622v1, Theorem 1, Proposition 1, Section 4.5) already
provides joint all-completion certificates, agreement relevance and tolerance.
At known prevalence the weighted-error representation of 1-F1 connects to his
framework, but sharp bounds must constrain the number of positives. At unknown
prevalence the denominators vary. V5 claims the explicit two-count F1 solution
and its consequences, not those general principles. Musgrove et al. (Scientific
Reports 13:20987, 2023) additionally assume transferable baseline performance.
Okanovic et al. (AISTATS 2025, 2035-2043) address label-efficient best/near-best
selection, not our deterministic all-completion F1 guarantee. Lipton's final
ECML PKDD publication (2014, 225-239) is cited with Narayanaswamy, verified on
his own homepage despite the publisher metadata spelling variant.
