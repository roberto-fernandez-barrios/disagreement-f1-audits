Numerical results
=================

These are frozen outputs for the unchanged manuscript V4. All cells, pairs and
orders are dependent benchmark observations; they are not independent tasks.

* ``pilot/``: the original eight-cell pilot.
* ``reserved/``: the 28-cell analytical holdout, still retrospective.
* ``strict_sign/``: the original strict-winner/exact-tie query trajectories.
* ``tolerance/``: paired/marginal intervals, tolerance costs and comparator selection.
* ``tradeoffs/``: the zero-loss control, six tolerance levels and descriptive dispersion.
* ``summary.json``: the original aggregate summary.

The `evidence map <../docs/evidence.rst>`_ links claims to the relevant files and
states the units, cohorts and weights. The tolerance figure displayed in the
README is `tradeoffs/tolerance_sensitivity.png <tradeoffs/tolerance_sensitivity.png>`_.

Execution timestamps, hashes and validation reports are under
``reproducibility/records/``. They retain their original contents. Use
``python tools/manage.py reproduce --scope all`` from the repository root to
reconstruct the results in a disposable working copy; references are preserved.
