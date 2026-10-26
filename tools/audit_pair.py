"""Validated, label-limited adapter to the unchanged exact F1 implementation."""
from fractions import Fraction
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tolerance import hulls, decision, exact_decision


def audit(payload, epsilon="0.01"):
    """Use only supplied observations; null labels remain unknown.

    All disagreements must have labels. Agreement labels may be supplied as
    they become available. A prevalence is an exact positive count, not a rate
    estimate. This wrapper does not train, acquire labels or use the benchmark.
    """
    q, c, labels = (payload.get(key) for key in ("q", "c", "labels"))
    if not all(isinstance(v, list) for v in (q, c, labels)):
        raise ValueError("q, c and labels must be JSON arrays")
    if not q or len(q) != len(c) or len(q) != len(labels):
        raise ValueError("q, c and labels must have the same nonzero length")
    binary = lambda x: type(x) is int and x in (0, 1)
    if not all(binary(x) for x in q + c):
        raise ValueError("predictions must be integer 0 or 1")
    if not all(x is None or binary(x) for x in labels):
        raise ValueError("labels must be integer 0, integer 1 or null")
    try:
        eps = Fraction(str(epsilon))
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError("epsilon must be a finite nonnegative number") from exc
    if eps < 0:
        raise ValueError("epsilon must be nonnegative")
    p = payload.get("prevalence")
    if p is not None and (type(p) is not int or not 0 <= p <= len(q)):
        raise ValueError("prevalence must be an integer positive count between 0 and n")
    k = dict(n00=0, n11=0, a=0, b=0, u=0, v=0)
    positive = [0, 0]
    unknown = [0, 0]
    for qi, ci, yi in zip(q, c, labels):
        if qi != ci:
            if yi is None:
                raise ValueError("every disagreement must be labeled before this audit")
            k["a" if qi else "b"] += 1
            k["u" if qi else "v"] += yi
        else:
            k["n11" if qi else "n00"] += 1
            unknown[qi] += yi is None
            positive[qi] += yi == 1
    bounds = (positive[0], positive[0] + unknown[0],
              positive[1], positive[1] + unknown[1])
    interval, marginal = hulls(k, bounds=bounds, prevalence=p)
    certified, choice, regret = decision(interval, eps)
    weak = decision(interval, Fraction(0))[0]
    rational = lambda x: {"exact": str(x), "decimal": float(x)}
    return {
        "n": len(q), "disagreement_labels": k["a"] + k["b"],
        "observed_labels": sum(y is not None for y in labels),
        "exact_positive_count": p, "epsilon": rational(eps),
        "paired_interval": [rational(x) for x in interval],
        "separate_interval": [rational(x) for x in marginal],
        "strict_winner_or_exact_tie_identified": exact_decision(interval),
        "zero_loss_choice_certified": weak,
        "tolerance_choice_certified": certified,
        "action": "choose" if certified else "query_agreements",
        "chosen_model": ("q" if choice else "c") if certified else None,
        "minimum_worst_case_regret": rational(regret),
        "tie_break": "q", "guarantee": "finite batch; fixed predictions; correct observed labels",
    }
