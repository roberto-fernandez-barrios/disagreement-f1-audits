Audit your own pair
===================

The public adapter calls the unchanged ``tolerance.py`` implementation. It
accepts only the predictions and labels you provide; it never reads benchmark
labels. This is a deterministic finite-batch audit, not a trained estimator.

Input
-----

Create a JSON object with these fields:

* ``q`` and ``c``: equally sized, nonempty arrays of integer 0/1 predictions.
* ``labels``: the same number of entries, each integer 0, integer 1, or ``null``.
  Label every disagreement. Leave unqueried agreements ``null``.
* ``prevalence`` (optional): the exact integer number of positive labels,
  between 0 and ``n`` inclusive. Omit it or use ``null`` when unknown.

An estimated prevalence must not be supplied as exact side information.
Inconsistent counts, missing disagreement labels, booleans in place of integers,
and nonfinite or negative tolerances are rejected.

Run::

    python tools/manage.py audit examples/ten_items.json --epsilon 0.01

The tolerance is an **absolute F1 difference**. Decimal strings are converted
to exact fractions. Both interval endpoints are returned as fractions and
decimal approximations; the stopping decision uses the exact fractions.

Output and decisions
--------------------

``paired_interval`` is the sharp hull of ``F1(q)-F1(c)`` over all compatible
completions. ``separate_interval`` subtracts the marginal score intervals on
the same feasible set; it is valid but can be wider.

``minimum_worst_case_regret`` is the smaller of ``max(0,-L)`` and ``max(0,U)``.
If it is at most epsilon, ``action`` is ``choose`` and ``chosen_model`` identifies
the minimax choice, breaking equal-regret ties in favor of ``q``. Otherwise
``action`` is ``query_agreements`` and ``chosen_model`` is ``null``. An
uncertified candidate is never presented as a certified selection.

The output distinguishes strict-winner/exact-tie identification, a zero-loss
choice, and a choice at the requested tolerance. Epsilon zero may certify a
weak winner without resolving strict victory versus exact tie. A positive
tolerance does not require the whole interval to lie in ``[-epsilon,epsilon]``.

Updating an audit
-----------------

Replace newly acquired agreement labels with 0 or 1 and run the command again.
The feasible count rectangle shrinks automatically. In the ten-item example,
revealing positions 3, 4 and 5 (zero based) as positive forces ``t=3``. With
``P=4`` the difference is then exactly ``-2/35`` and model ``c`` is certified
even at epsilon zero. No labels outside the supplied observations are consulted.

The adapter includes ``P=0`` and ``P=n`` and uses ``0/0=0`` for F1. This differs
from the original initial-information figure's stated ``0<P<n`` restriction.
Query trajectories and the theoretical certificate include both extremes.

Python use
----------

From the repository root::

    from tools.audit_pair import audit
    result = audit({"q": [0], "c": [0], "labels": [None]}, epsilon="0")
    assert result["chosen_model"] == "q"

Assumptions and complexity
--------------------------

Predictions are fixed and observed labels are correct. The guarantee concerns
these two models on this batch; it does not cover future data, noisy labels,
macro-F1, multiclass metrics or an adaptively selected model family. Exact
magnitude bounds enumerate feasible positive counts in O(n) time and memory.
For large batches, assess memory and runtime before integrating this prototype.
The package is research software, not a labeling service or deployment system.
