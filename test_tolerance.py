"""Independent rational enumeration and sequential replay checks for V3."""
from fractions import Fraction as F
import numpy as np
from decision import counts
from tolerance import hulls,decision,exact_decision,prefix_bounds,first_stop

def brute(k,bounds,P=None,interior=False):
    sl,sh,tl,th=bounds;vals=[];qs=[];cs=[]
    n=sum(k[x] for x in ['n00','n11','a','b'])
    for s in range(sl,sh+1):
        for t in range(tl,th+1):
            p=k['u']+k['v']+s+t
            if P is not None and p!=P:continue
            if interior and p in [0,n]:continue
            dq=p+k['a']+k['n11'];dc=p+k['b']+k['n11']
            q=F(2*(t+k['u']),dq) if dq else F(0)
            c=F(2*(t+k['v']),dc) if dc else F(0)
            qs.append(q);cs.append(c);vals.append(q-c)
    if not vals:raise ValueError('empty')
    return (min(vals),max(vals)),(min(qs)-max(cs),max(qs)-min(cs))

def main():
    rng=np.random.default_rng(91025);checks=0;paths=0
    for iteration in range(700):
        n=int(rng.integers(1,11));q,c,y=rng.integers(0,2,(3,n));k=counts(q,c,y)
        ii=np.flatnonzero(q==c);g=q[ii];order=rng.permutation(len(ii))
        pref=prefix_bounds(k,g,y[ii],order)
        for step in sorted({0,len(ii),len(ii)//2}):
            b=tuple(map(int,pref[step]))
            for P in [None,int(y.sum()),0,n]:
                for interior in [False,True]:
                    try:expected=brute(k,b,P,interior)
                    except ValueError:
                        try:hulls(k,b,P,interior)
                        except ValueError:continue
                        raise AssertionError('empty hull accepted')
                    actual=hulls(k,b,P,interior);assert actual==expected,(k,b,P,actual,expected)
                    assert actual[1][0]<=actual[0][0]<=actual[0][1]<=actual[1][1]
                    for eps in [F(0),F(1,100),F(1,5)]:
                        stop,choice,regret=decision(actual[0],eps)
                        assert stop==(actual[0][0]>=-eps or actual[0][1]<=eps)
                    checks+=1
        for eps in [F(0),F(1,100),F(1,5)]:
            stop,d=first_stop(k,pref,{},eps)
            sequential=next(i for i,b in enumerate(pref) if decision(brute(k,tuple(b))[0],eps)[0])
            assert stop==sequential
            realized=brute(k,tuple(pref[-1]))[0][0]
            assert (max(F(0),-realized) if d[1] else max(F(0),realized))<=eps
            # Replace every future label: the acquired-prefix certificate is unchanged.
            changed=y[ii].copy();changed[order[stop:]]=1-changed[order[stop:]]
            pref2=prefix_bounds(k,g,changed,order)
            assert np.array_equal(pref[stop],pref2[stop]);paths+=1
    assert decision((F(-1,100),F(1,2)))[0]
    assert decision((F(-1,2),F(1,100)))[0]
    assert not decision((F(-11,1000),F(11,1000)))[0]
    assert decision((F(0),F(1,2)),F(0))[0] and not exact_decision((F(0),F(1,2)))
    assert decision((F(-1,100),F(1,100)))[1]==1
    return {'exact_rational_hulls':checks,'sequential_prefix_and_future_label_checks':paths,'status':'passed'}

if __name__=='__main__':print(main())
