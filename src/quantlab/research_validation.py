"""QUANT 0.4: deterministic source-neutral statistical research primitives.

All functions operate on already validated observations. They never fetch data,
infer futures contracts from CFDs or assert the existence of a trading edge.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from datetime import date
import numpy as np
import pandas as pd

UTC = 'UTC'
NY = 'America/New_York'

@dataclass(frozen=True)
class Instrument:
    symbol: str
    tick: float
    multiplier: float
    market_type: str = 'future'

    def validate(self):
        if self.symbol not in {'NQ', 'MNQ', 'ES', 'MES'}:
            raise ValueError('Unknown CME futures instrument')
        expected = {'NQ':20,'MNQ':2,'ES':50,'MES':5}
        if self.tick != 0.25 or self.multiplier != expected[self.symbol] or self.market_type!='future':
            raise ValueError('Invalid contract specification')
        return self

def validate_minute_index(frame: pd.DataFrame) -> None:
    idx=frame.index
    if not isinstance(idx,pd.DatetimeIndex) or idx.tz is None or str(idx.tz)!=UTC:
        raise ValueError('Canonical UTC DatetimeIndex required')
    if idx.has_duplicates or not idx.is_monotonic_increasing:
        raise ValueError('Duplicate or unordered timestamps')
    if any(idx.second) or any(idx.microsecond):
        raise ValueError('Bars must start on minute boundaries')

def coverage_report(frame: pd.DataFrame) -> dict:
    validate_minute_index(frame)
    if 'contract_id' not in frame: raise ValueError('Missing contract_id')
    contracts={}
    for contract, group in frame.groupby('contract_id'):
        idx=group.index
        delta=idx.to_series().diff().dropna().dt.total_seconds().div(60)
        contracts[str(contract)]={'observed_bars':len(group),
            'gap_count':int((delta>1).sum()),
            'missing_minutes_between_observations':int((delta[delta>1]-1).sum())}
    return {'contracts':contracts,'calendar_reconciled':False,
            'note':'Observed gaps include valid exchange closures until reconciled.'}

def to_trade_date(index: pd.DatetimeIndex) -> pd.Index:
    if index.tz is None: raise ValueError('Timezone-aware dates required')
    # Futures trade date needs instrument exchange calendar: do not guess it.
    return pd.Index(index.tz_convert(NY).date,name='ny_calendar_date')

def session_window(frame: pd.DataFrame, start: str, end: str) -> pd.Series:
    validate_minute_index(frame)
    a=pd.Timedelta(start+':00').total_seconds()/60
    b=pd.Timedelta(end+':00').total_seconds()/60
    if not 0<=a<b<=1440: raise ValueError('Invalid same-day window')
    local=frame.index.tz_convert(NY)
    minute=local.hour*60+local.minute
    return pd.Series((minute>=a)&(minute<b),index=frame.index)

def opening_range(frame: pd.DataFrame, start='09:30', minutes=15) -> pd.DataFrame:
    validate_minute_index(frame)
    if minutes<=0 or minutes>120: raise ValueError('Invalid range length')
    if not {'contract_id','high','low'}.issubset(frame): raise ValueError('Missing input columns')
    local=frame.index.tz_convert(NY)
    start_min=int(start[:2])*60+int(start[3:])
    if start_min+minutes>1440: raise ValueError('Range crosses calendar day')
    result=[]
    for (day,contract),group in frame.groupby([local.date,frame.contract_id],sort=False):
        lm=group.index.tz_convert(NY)
        nums=lm.hour*60+lm.minute
        cut=group[(nums>=start_min)&(nums<start_min+minutes)]
        if list(nums[(nums>=start_min)&(nums<start_min+minutes)])!=list(range(start_min,start_min+minutes)):
            continue
        result.append({'ny_calendar_date':str(day),'contract_id':contract,
            'range_high':float(cut.high.max()),'range_low':float(cut.low.min()),
            'known_at_utc':cut.index[-1]+pd.Timedelta(minutes=1)})
    return pd.DataFrame(result)

def vwap_known_at(frame: pd.DataFrame) -> pd.DataFrame:
    validate_minute_index(frame)
    if not {'contract_id','volume','high','low','close'}.issubset(frame): raise ValueError('Missing inputs')
    result=frame.copy()
    result['vwap_prior']=np.nan
    result['known_at_utc']=frame.index+pd.Timedelta(minutes=1)
    local=frame.index.tz_convert(NY)
    for (_,contract),group in frame.groupby([local.date,frame.contract_id],sort=False):
        value=(group.high+group.low+group.close)/3
        cvol=group.volume.cumsum().shift(1)
        cpv=(value*group.volume).cumsum().shift(1)
        result.loc[group.index,'vwap_prior']=(cpv/cvol.where(cvol>0)).to_numpy()
    return result

def fixed_events(frame: pd.DataFrame, feature: str, threshold: float, side='above') -> pd.DatetimeIndex:
    validate_minute_index(frame)
    if feature not in frame: raise ValueError('Feature absent')
    if side not in {'above','below'}: raise ValueError('Invalid comparator')
    v=frame[feature]
    flag=v.gt(threshold) if side=='above' else v.lt(threshold)
    # Event timestamp names the just-closed signal bar (decision at next open).
    return frame.index[flag.fillna(False)]

def matched_baseline(events: pd.DataFrame, controls: pd.DataFrame,
                     keys=('hour_et','volatility_regime')) -> dict:
    if 'forward_points' not in events or 'forward_points' not in controls:
        raise ValueError('Both frames require outcome')
    if any(k not in events or k not in controls for k in keys): raise ValueError('Missing matching keys')
    joined=events.merge(controls.groupby(list(keys),dropna=False).forward_points.mean()
                        .rename('baseline_mean').reset_index(),on=list(keys),how='left')
    valid=joined.dropna(subset=['forward_points','baseline_mean'])
    return {'matched_events':len(valid),'unmatched_events':len(joined)-len(valid),
            'mean_excess_points':float((valid.forward_points-valid.baseline_mean).mean()) if len(valid) else None}

def chronological_splits(frame: pd.DataFrame, train=.6, valid=.2, embargo=0) -> dict:
    if not 0<train<1 or not 0<valid<1 or train+valid>=1 or embargo<0:
        raise ValueError('Invalid split parameters')
    n=len(frame)
    a=int(n*train);b=int(n*(train+valid))
    if n<10 or a-embargo<=0 or b-a-2*embargo<=0 or n-b-embargo<=0:
        raise ValueError('Insufficient independent observations')
    return {'train':frame.iloc[:a-embargo].copy(),
            'validation':frame.iloc[a+embargo:b-embargo].copy(),
            'holdout':frame.iloc[b+embargo:].copy(),
            'holdout_sealed':True}

def block_bootstrap_mean(values, block=5, samples=1000, seed=17) -> dict:
    x=np.asarray(values,dtype=float)
    if len(x)<max(20,block) or block<1 or samples<100 or not np.isfinite(x).all():
        raise ValueError('Insufficient valid observations')
    rng=np.random.default_rng(seed); n=len(x)
    means=np.empty(samples)
    for i in range(samples):
        starts=rng.integers(0,n,size=math.ceil(n/block))
        indices=np.concatenate([(s+np.arange(block))%n for s in starts])[:n]
        means[i]=x[indices].mean()
    return {'mean':float(x.mean()),'ci_lower':float(np.quantile(means,.025)),
            'ci_upper':float(np.quantile(means,.975)),'samples':samples,'block':block,'seed':seed}

def fdr_bh(pvalues) -> list[float]:
    p=np.asarray(pvalues,dtype=float)
    if p.ndim!=1 or (p<0).any() or (p>1).any() or not np.isfinite(p).all():
        raise ValueError('Invalid p-values')
    if not len(p): return []
    order=np.argsort(p); ranks=np.arange(1,len(p)+1)
    q=np.minimum.accumulate((p[order]*len(p)/ranks)[::-1])[::-1]
    result=np.empty(len(p));result[order]=np.minimum(q,1)
    return result.tolist()

def cost_sensitivity(gross_points, costs=(0,2,4)) -> dict:
    g=np.asarray(gross_points,dtype=float)
    if not len(g) or not np.isfinite(g).all(): raise ValueError('Missing trades')
    if any(c<0 for c in costs): raise ValueError('Negative costs')
    return {str(c):{'mean_net_points':float((g-c).mean()),
                    'winning_fraction':float(np.mean((g-c)>0))} for c in costs}

def test_manifest(*, data_hash: str, code_ref: str, instrument: Instrument,
                  parameters: dict, synthetic: bool) -> dict:
    instrument.validate()
    if not data_hash or not code_ref: raise ValueError('Missing source provenance')
    manifest={'dataset_hash':data_hash,'code_ref':code_ref,
              'instrument':asdict(instrument),'parameters':parameters,
              'synthetic':synthetic,'edge_validated':False}
    manifest['manifest_sha256']=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
    return manifest
