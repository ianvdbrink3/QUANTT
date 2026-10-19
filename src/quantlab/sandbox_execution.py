"""Deterministic sandbox fills only; never a source of empirical market edges."""
from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class FillConfig:
    stop_points: float
    target_points: float
    roundtrip_cost_points: float = 0.0
    multiplier: float = 20.0
    ambiguity: str = 'pessimistic'

def simulate_long(path: pd.DataFrame, entry: float, settings: FillConfig) -> dict:
    if settings.stop_points<=0 or settings.target_points<=0 or settings.roundtrip_cost_points<0:
        raise ValueError('Invalid stop, target, or costs')
    if settings.multiplier<=0 or settings.ambiguity not in {'pessimistic','optimistic','unresolved'}:
        raise ValueError('Invalid execution model')
    if path.empty: raise ValueError('No bars')
    if not {'open','high','low','close'}.issubset(path.columns): raise ValueError('Missing OHLC')
    stop=entry-settings.stop_points
    target=entry+settings.target_points
    ambiguity_count=0
    for idx, bar in path.iterrows():
        if bar.high<max(bar.open,bar.close,bar.low) or bar.low>min(bar.open,bar.close,bar.high):
            raise ValueError('Malformed OHLC')
        # Gap-through-stop never fills at the better stop price.
        if bar.open<=stop:
            gross=float(bar.open-entry)
            return _result(gross,settings,'gap_stop',ambiguity_count,idx)
        if bar.open>=target:
            gross=float(target-entry)
            return _result(gross,settings,'target_open',ambiguity_count,idx)
        stop_hit=bar.low<=stop
        target_hit=bar.high>=target
        if stop_hit and target_hit:
            ambiguity_count+=1
            if settings.ambiguity=='unresolved':
                return {'status':'AMBIGUOUS','ambiguous_bars':ambiguity_count,'pnl_points':None,'pnl_usd':None}
            price=stop if settings.ambiguity=='pessimistic' else target
            return _result(price-entry,settings,'ambiguous_'+settings.ambiguity,ambiguity_count,idx)
        if stop_hit: return _result(stop-entry,settings,'stop',ambiguity_count,idx)
        if target_hit: return _result(target-entry,settings,'target',ambiguity_count,idx)
    return _result(float(path.close.iloc[-1]-entry),settings,'time_exit',ambiguity_count,path.index[-1])

def _result(gross,settings,reason,ambiguous,index):
    net=gross-settings.roundtrip_cost_points
    return {'status':'FILLED','exit_reason':reason,'exit_index':str(index),
            'gross_points':gross,'net_points':net,'pnl_points':net,
            'pnl_usd':net*settings.multiplier,'ambiguous_bars':ambiguous}
