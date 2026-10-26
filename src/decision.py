"""Exact finite-batch metric differences after revealing disagreement labels."""
import numpy as np


def counts(q, c, y):
    return {"n00": int(((q == 0) & (c == 0)).sum()),
            "n11": int(((q == 1) & (c == 1)).sum()),
            "a": int(((q == 1) & (c == 0)).sum()),
            "b": int(((q == 0) & (c == 1)).sum()),
            "u": int(y[(q == 1) & (c == 0)].sum()),
            "v": int(y[(q == 0) & (c == 1)].sum())}


def metric(h, y, name):
    tp = int(((h == 1) & (y == 1)).sum())
    if name == "accuracy":
        return float((h == y).mean())
    if name == "ba":
        p = int(y.sum())
        if p == 0 or p == len(y):
            return float("nan")
        tn = int(((h == 0) & (y == 0)).sum())
        return .5 * (tp / p + tn / (len(y) - p))
    den = int(y.sum() + h.sum())
    return 2 * tp / den if den else 0.


def grid(k, prevalence=None, bounds=None, interior=True):
    """bounds=(s_min,s_max,t_min,t_max), all integer completions attainable."""
    n00, n11, a, b, u, v = [k[x] for x in ["n00", "n11", "a", "b", "u", "v"]]
    n = n00 + n11 + a + b
    sl, sh, tl, th = bounds or (0, n00, 0, n11)
    s, t = np.meshgrid(np.arange(sl, sh + 1), np.arange(tl, th + 1), indexing="ij")
    s, t = s.ravel(), t.ravel()
    p = u + v + s + t
    mask = (p > 0) & (p < n) if interior else np.ones(len(p), bool)
    if prevalence is not None:
        mask &= p == prevalence
    s, t, p = s[mask], t[mask], p[mask]
    if not len(p):
        raise ValueError("No admissible completion")
    dq, dc = p + a + n11, p + b + n11
    f1 = np.divide(2 * (t + u), dq, out=np.zeros(len(p), float), where=dq != 0)
    f1 -= np.divide(2 * (t + v), dc, out=np.zeros(len(p), float), where=dc != 0)
    # BA is undefined when either class is absent. F1 and accuracy remain valid.
    ba = np.full(len(p), np.nan)
    valid_ba = (p > 0) & (p < n)
    pp = p[valid_ba]
    ba[valid_ba] = .5 * ((u - v) / pp + (b - a + u - v) / (n - pp))
    acc = (2 * (u - v) + b - a) / n
    # Cross-multiplication reduces the F1 ranking to an affine agreement score.
    num = (u-v) * p + (b-a) * t + u*b - v*a + (u-v)*n11
    assert np.allclose(f1 * dq * dc / 2, num)
    return {"s": s, "t": t, "p": p, "f1": f1, "ba": ba,
            "accuracy": np.full(len(p), acc), "f1_numerator": num}


def intervals(k, prevalence=None, bounds=None, interior=True):
    """Metric hulls over admissible completions.

    Undefined metrics return null endpoints/witnesses (not a fabricated score).
    n_defined counts completions within that metric's domain; it can be smaller
    than n_completions for BA. An empty completion set still raises ValueError.
    """
    g = grid(k, prevalence, bounds, interior)
    out = {}
    for name in ("accuracy", "ba", "f1"):
        values = g[name]
        keep = np.isfinite(values)
        ii = np.flatnonzero(keep)
        if not len(ii):
            out[name] = {"lower": None, "upper": None, "min_s": None,
                         "min_t": None, "max_s": None, "max_t": None,
                         "defined": False, "n_defined": 0,
                         "n_completions": len(values)}
            continue
        lo, hi = int(ii[np.argmin(values[keep])]), int(ii[np.argmax(values[keep])])
        out[name] = {"lower": float(values[lo]), "upper": float(values[hi]),
                     "min_s": int(g["s"][lo]), "min_t": int(g["t"][lo]),
                     "max_s": int(g["s"][hi]), "max_t": int(g["t"][hi]),
                     "defined": True, "n_defined": int(keep.sum()),
                     "n_completions": len(values)}
    return out


def f1_interval_fixed_prevalence(k, prevalence, bounds=None):
    """Closed-form F1 gap hull at exact P, including P=0,n.

    Endpoints apply to the gap itself because its denominators are fixed.
    They must not be used for a gap with unknown prevalence.
    """
    sl, sh, tl, th = bounds or (0, k['n00'], 0, k['n11'])
    remaining = prevalence - k['u'] - k['v']
    low, high = max(tl, remaining-sh), min(th, remaining-sl)
    if low > high:
        raise ValueError('No admissible completion')
    if prevalence == 0:
        return 0., 0.
    Q, C = k['a'] + k['n11'], k['b'] + k['n11']
    def gap(t):
        return 2*(t+k['u'])/(prevalence+Q)-2*(t+k['v'])/(prevalence+C)
    return tuple(sorted((gap(low), gap(high))))
