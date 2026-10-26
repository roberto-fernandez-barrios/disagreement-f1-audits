"""Independent individual-label enumeration of small finite problems."""
import itertools, json
import numpy as np
from decision import counts, intervals, metric, f1_interval_fixed_prevalence


def revision_checks():
    """Review-driven checks, added after the original empirical results existed."""
    extreme = equal_count = fixed_count = 0
    # Includes the reported n=1 all-negative case, P=n, nonidentical predictors,
    # zero F1 denominators, and every binary prediction pair up to n=3.
    for n in range(1, 4):
        vectors = [np.array(z) for z in itertools.product([0, 1], repeat=n)]
        for q, c in itertools.product(vectors, repeat=2):
            for P in (0, n):
                y = np.full(n, int(P == n))
                k = counts(q, c, y)
                result = intervals(k, prevalence=P, interior=False)
                assert not result['ba']['defined']
                assert result['ba']['lower'] is None and result['ba']['upper'] is None
                assert result['ba']['n_defined'] == 0
                for name in ('accuracy', 'f1'):
                    expected = metric(q, y, name)-metric(c, y, name)
                    assert np.allclose([result[name]['lower'], result[name]['upper']], expected)
                json.dumps(result, allow_nan=False)
                assert np.allclose(f1_interval_fixed_prevalence(k, P),
                                   [result['f1']['lower'], result['f1']['upper']])
                extreme += 1
    rng = np.random.default_rng(20261025)
    for _ in range(200):
        n = int(rng.integers(2, 9))
        q, c, y = rng.integers(0, 2, (3, n))
        agree = np.flatnonzero(q == c)
        observed = agree[rng.random(len(agree)) < .5]
        unknown = np.setdiff1d(agree, observed)
        k = counts(q, c, y)
        obs0, obs1 = observed[q[observed] == 0], observed[q[observed] == 1]
        s0, t0 = int(y[obs0].sum()), int(y[obs1].sum())
        bounds = (s0, s0+k['n00']-len(obs0), t0, t0+k['n11']-len(obs1))
        by_p = {}
        for labels in itertools.product([0, 1], repeat=len(unknown)):
            z = y.copy(); z[unknown] = labels
            gap = metric(q, z, 'f1')-metric(c, z, 'f1')
            by_p.setdefault(int(z.sum()), []).append(gap)
            if q.sum() == c.sum():
                assert np.sign(round(gap, 12)) == np.sign(k['u']-k['v'])
                equal_count += 1
        for P, values in by_p.items():
            assert np.allclose(f1_interval_fixed_prevalence(k, P, bounds),
                               [min(values), max(values)])
            fixed_count += 1
    k = dict(n00=2, n11=0, a=0, b=0, u=0, v=0)
    mixed = intervals(k, interior=False)
    assert mixed['ba']['n_defined'] == 1 and mixed['ba']['n_completions'] == 3
    for fn in (lambda: intervals(k, prevalence=0),
               lambda: intervals(k, prevalence=3, interior=False),
               lambda: f1_interval_fixed_prevalence(k, 3)):
        try:
            fn()
        except ValueError as error:
            assert str(error) == 'No admissible completion'
        else:
            raise AssertionError('Empty completion set must be rejected')
    return {'extreme_prevalence_cases': extreme,
            'fixed_prevalence_partial_audit_intervals': fixed_count,
            'equal_prediction_count_completions': equal_count,
            'mixed_ba_domain_and_empty_set_checks': 'passed', 'status': 'passed'}


def main():
    rng = np.random.default_rng(20261024)
    checked = 0
    for n in range(2, 10):
        for rep in range(75):
            q, c, y = rng.integers(0, 2, (3, n))
            y[0], y[1] = 0, 1
            agreement = np.flatnonzero(q == c)
            k = counts(q, c, y)
            for fixed_p in (None, int(y.sum())):
                values = {name: [] for name in ["accuracy", "ba", "f1"]}
                for yy in itertools.product([0, 1], repeat=len(agreement)):
                    z = y.copy(); z[agreement] = yy
                    if not 0 < z.sum() < n or (fixed_p is not None and z.sum() != fixed_p):
                        continue
                    for name in values:
                        values[name].append(metric(q,z,name)-metric(c,z,name))
                result = intervals(k, prevalence=fixed_p)
                for name, vs in values.items():
                    assert np.allclose([min(vs),max(vs)], [result[name]["lower"],result[name]["upper"]]), (k,name)
                checked += 1
    return {"individual_enumeration_problems": checked,
            "review_driven_checks": revision_checks(), "status": "passed"}

if __name__ == "__main__":
    print(json.dumps(main()))
