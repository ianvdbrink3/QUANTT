"""Prespecified descriptive contrasts, one GLOBAL Holm family, no filters fitted."""
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from . import engine


def statistic(a,b,kind):
    good=np.isfinite(a)&np.isfinite(b)
    a,b=a[good],b[good]
    if len(a)<10: return np.nan
    if kind=='difference':
        return float(b[a==1].mean()-b[a==0].mean()) if min((a==1).sum(),(a==0).sum())>=5 else np.nan
    a,b=rankdata(a),rankdata(b)
    if np.std(a)==0 or np.std(b)==0: return np.nan
    return float(np.corrcoef(a,b)[0,1])


def matrix(features,dates,reps=2000):
    tests=[]; groups=[]
    rng=np.random.default_rng(20261021)
    n=len(dates)
    starts=rng.integers(0,n,size=(reps,int(np.ceil(n/5))))
    indices=((starts[:,:,None]+np.arange(5))%n).reshape(reps,-1)[:,:n]
    locations=['INSIDE_PRIOR_RANGE','GAP_ABOVE_PDH','GAP_BELOW_PDL']
    for strategy,t in features.groupby('strategy'):
        for field in ['opening_location','overnight_regime']:
            for label,g in t.groupby(field):
                groups.append({'strategy':strategy,'feature':field,'group':label,'trades':len(g),
                               'net_points':float(g.net_points.sum()),'mean_net_points':float(g.net_points.mean()),
                               'median_MFE_points':float(g.mfe_bar_bound_points.median())})
        for feature in ['opening_RVOL14','overnight_range_ATR']:
            g=t[t[feature].notna()]
            groups.append({'strategy':strategy,'feature':feature,'group':'continuous_complete_cases',
                           'trades':len(g),'net_points':float(g.net_points.sum()),
                           'mean_net_points':float(g.net_points.mean()) if len(g) else None,
                           'median_MFE_points':float(g.mfe_bar_bound_points.median()) if len(g) else None})
        specs=[('opening_location',a,b) for i,a in enumerate(locations) for b in locations[i+1:]]
        specs += [(f,None,None) for f in ['opening_RVOL14','overnight_range_ATR']]
        aligned=t.set_index('trade_date').reindex(dates)
        for feature,left,right in specs:
            if left:
                a=aligned[feature].map({left:1.,right:0.}).to_numpy(dtype=float); kind='difference'
            else:
                a=pd.to_numeric(aligned[feature],errors='coerce').to_numpy();kind='spearman'
            for outcome in ['net_points','mfe_bar_bound_points']:
                b=aligned[outcome].to_numpy(dtype=float); estimate=statistic(a,b,kind)
                boot=np.array([statistic(a[ix],b[ix],kind) for ix in indices]) if np.isfinite(estimate) else np.array([])
                boot=boot[np.isfinite(boot)]
                valid=np.isfinite(estimate) and len(boot)>=reps*.9
                p=float((1+(abs(boot-estimate)>=abs(estimate)).sum())/(len(boot)+1)) if valid else 1.
                tests.append({'strategy':strategy,'feature':feature,'left':left,'right':right,
                              'outcome':outcome,'statistic':kind,'estimate':estimate,
                              'complete_cases':int((np.isfinite(a)&np.isfinite(b)).sum()),
                              'testable':bool(valid),'p_raw':p,
                              'ci_low':float(np.quantile(boot,.025)) if valid else None,
                              'ci_high':float(np.quantile(boot,.975)) if valid else None})
    for row,p in zip(tests,engine.holm([r['p_raw'] for r in tests])):
        row['p_holm_global']=float(p)
    return {'groups':groups,'tests':tests,'multiplicity_family_size':len(tests),
            'method':'Exploratory centered circular 5-observed-session block bootstrap, 2000 draws, seed 20261021; missing/non-trade days retained in resampling. Global Holm over all 40 contrasts (4 strategies x 5 features/contrasts x 2 outcomes). Untestable p=1 retained. Approximate observational inference, not causal or independent validation.',
            'selection':'No fitted cutoffs. Prior-location pairs; continuous RVOL and overnight/ATR Spearman. Overnight compressed<0.5 and expanded>1.2 are descriptive existing-regime groups only. MFE is the frozen minute-bar bound through exit, not tick-exact.'}
