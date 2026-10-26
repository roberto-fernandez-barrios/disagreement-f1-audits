"""Exact paired and marginal F1 hulls, with rational stopping decisions."""
from fractions import Fraction
import numpy as np


def hulls(k, bounds=None, prevalence=None, interior=False):
    """Enumerate integer P and the two feasible t endpoints at each P.

    At fixed P each score and their difference is affine in t; taking their
    extrema over these endpoints and then over all feasible P is exact.
    No unknown-prevalence corner shortcut is used. Return rational endpoints.
    """
    sl, sh, tl, th = bounds or (0, k['n00'], 0, k['n11'])
    u,v = k['u'],k['v']; Q=k['a']+k['n11']; C=k['b']+k['n11']
    n=k['n00']+k['n11']+k['a']+k['b']
    # Exact cross products below fit int64 for n<=10000. Larger batches use
    # Python integers; floating candidates are always verified rationally.
    dtype=np.int64 if n<=10000 else object
    p=np.arange(u+v+sl+tl,u+v+sh+th+1,dtype=dtype) if prevalence is None else np.array([prevalence],dtype=dtype)
    low=np.maximum(tl,p-u-v-sh); high=np.minimum(th,p-u-v-sl)
    mask=low<=high
    if interior: mask &= (p>0)&(p<n)
    p=np.repeat(p[mask],2); t=np.column_stack((low[mask],high[mask])).ravel()
    if not len(p): raise ValueError('No admissible completion')
    dq=p+Q;dc=p+C
    # Replace a zero-denominator score by its stipulated value zero.
    nq=2*(t+u);nc=2*(t+v)
    dq=np.where(dq==0,1,dq);dc=np.where(dc==0,1,dc)
    nums=nq*dc-nc*dq; dens=dq*dc
    def extrema(ns,ds):
        vals=ns/ds
        i,j=int(np.argmin(vals)),int(np.argmax(vals))
        if not ((ns*ds[i]>=ns[i]*ds).all() and (ns*ds[j]<=ns[j]*ds).all()):
            exact=[Fraction(int(a),int(b)) for a,b in zip(ns,ds)]
            return min(exact),max(exact)
        return (Fraction(int(ns[i]),int(ds[i])),Fraction(int(ns[j]),int(ds[j])))
    paired=extrema(nums,dens); qm=extrema(nq,dq);cm=extrema(nc,dc)
    return paired,(qm[0]-cm[1],qm[1]-cm[0])


def decision(interval, epsilon=Fraction(1,100)):
    """Minimax regret, ties choose q. A certifiable choice is batch epsilon-best."""
    L,U=interval;rq=max(Fraction(0),-L);rc=max(Fraction(0),U)
    choice=1 if rq<=rc else 0
    return min(rq,rc)<=epsilon,choice,min(rq,rc)


def exact_decision(interval):
    L,U=interval
    return L>0 or U<0 or L==U==0


def prefix_bounds(k, groups, acquired_labels, order):
    """Retrospective prefix table; each row depends only on labels in its prefix."""
    g=groups[order];z=acquired_labels[order]
    ns=np.r_[0,np.cumsum(g==0)];nt=np.r_[0,np.cumsum(g==1)]
    s=np.r_[0,np.cumsum(z*(g==0))];t=np.r_[0,np.cumsum(z*(g==1))]
    return np.column_stack((s,s+k['n00']-ns,t,t+k['n11']-nt))


def first_stop(k, prefixes, cache, epsilon=Fraction(1,100)):
    def check(i):
        key=tuple(map(int,prefixes[i]))
        if key not in cache: cache[key]=hulls(k,key)[0]
        return decision(cache[key],epsilon)
    if check(0)[0]:return 0,check(0)
    lo,hi=0,len(prefixes)-1
    assert check(hi)[0]
    # Nested feasible sets make the stopping predicate monotone. Binary search
    # is only a replay acceleration, not part of acquisition or its inputs.
    while hi-lo>1:
        mid=(lo+hi)//2
        if check(mid)[0]:hi=mid
        else:lo=mid
    assert not check(hi-1)[0] and check(hi)[0]
    return hi,check(hi)
