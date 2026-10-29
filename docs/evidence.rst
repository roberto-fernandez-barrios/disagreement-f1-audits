From claim to evidence
======================

All results below come from the frozen V4 scientific snapshot. Repository
release 1.4.0 revises literature positioning and attribution, not experiments.

.. list-table:: Evidence map
   :header-rows: 1
   :widths: 28 44 28

   * - Claim / paper element
     - Source
     - Reconstruction / check
   * - Ten-item reversal, fixed P=4
     - ``examples/ten_items.json``; paper Section 1
     - ``tools/manage.py demo``; ``tests/test_interface.py``
   * - Exact sign and magnitude, Q=C, P=0,n
     - ``src/decision.py``, ``src/tolerance.py``; paper Section 2
     - ``tests/scientific/test_decision.py``, ``tests/scientific/test_tolerance.py`` via ``verify``
   * - 20.54% / 10.52% material ambiguity, 28 reserved cells
     - ``results/reserved/pairs.csv`` and ``results/tolerance/summary.json``
     - ``reproduce --scope all``
   * - Paired versus separate intervals
     - ``results/tolerance/intervals.csv`` and ``results/tolerance/summary.json``
     - ``reproduce --scope all``; identical feasible sets
   * - Figure 1: six tolerances, 36 cells
     - ``results/tradeoffs/sensitivity.csv``, ``summary.json``; ``paper/source/tolerance_sensitivity.pdf``
     - ``reproduce``; exact rational decision bounds
   * - Table 1: common-cohort label costs
     - ``results/tolerance/costs.csv`` and ``summary.json``; ``paper/source/cost_rows_v4.tex``
     - ``reproducibility/scripts/render_v3.py`` then ``reproducibility/scripts/render_cost_table.py`` through the public workflow
   * - Zero-loss control and cell dispersion
     - ``data/controls/weak_zero_stops.npz``; ``results/tradeoffs/costs.csv`` and ``summary.json``
     - ``reproduce`` checks all 307200 weak-zero stops
   * - Validation comparator, 6/36 material cases
     - ``data/validation/validation_scores.csv`` and ``selection.json``
     - ``verify`` recomputes 36 choices; ``reproduce --scope all`` checks results
   * - Hamming comparator, 3/36 material cases
     - ``results/tolerance/pairs.csv`` and ``summary.json``
     - ``reproduce --scope all``
   * - 15466 realized-worse choices within tolerance
     - ``results/tolerance/stops.npz`` and ``summary.json``
     - ``reproduce --scope all``; dependent replays, not independent errors

Units and weighting
-------------------

Each cell contains 500 targets, one fixed quantum-kernel predictor and 115
classical configurations. Deduplicating identical classical predictions leaves
3200 pairs. The pilot has 801 pairs in eight cells; the reserved part has 2399
pairs in 28 cells. The all-configuration pool and one-comparator-per-cell designs
answer different questions. They must not share denominators implicitly.

Fractions average equally across eligible cells. Costs average the 32 orders,
then pairs within a cell, then cells. Pair-weighted values are separately labeled.
Initial disagreement labels, additional agreement labels and total labels are
kept distinct; totals are calculated before rounding. Dependencies from shared
targets and subsamples preclude treating the rows as independent population draws.

Interpretation
--------------

Compatible opposite winners describe identification ambiguity, not observed
mistakes. Known prevalence is exact side information. The original material
definition includes margins equal to .01, whereas failure of the minimax
tolerance decision requires strict exceedance. No initial pair lies exactly
on the relevant .01 boundaries in this benchmark.

The paired/marginal comparison ablates shared-label dependence on identical
feasible sets; it does not outperform TDC or Polo when those frameworks are
correctly applied jointly. Reported policy costs do not establish an optimum.
The closest-Hamming design is a sensitivity analysis, not a deployment rule.
Validation selects by balanced accuracy, following TDC's objective, not by F1.
