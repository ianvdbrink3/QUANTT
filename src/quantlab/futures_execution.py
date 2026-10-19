"""Deterministic NQ/ES synthetic OHLC-only execution bounds.

No broker fills, no market impact or latency model. Each event is independent;
same-bar stop/target order is unknowable and must be bounded.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
import math
import pandas as pd

@dataclass(frozen=True)
class ExecutionSettings:
    side: Literal['long','short']
    stop_points: float
    target_points: float
    multiplier: float
    tick_size: float=.25
    contracts: int=1
    max_contracts: int=5
    spread_points: float=0.0
    slippage_points_per_side: float=0.0
    commission_usd_per_side_per_contract: float=0.0
    ambiguity: Literal['pessimistic','optimistic','unresolved']='pessimistic'

    def validate(self):
        vals=(self.stop_points,self.target_points,self.multiplier,self.tick_size)
        if any(not math.isfinite(x) or x<=0 for x in vals):
            raise ValueError('Invalid stop, target, multiplier, or tick')
        costs=(self.spread_points,self.slippage_points_per_side,
               self.commission_usd_per_side_per_contract)
        if any(not math.isfinite(x) or x<0 for x in costs):
            raise ValueError('Invalid execution costs')
        if self.contracts<1 or self.contracts>self.max_contracts or self.max_contracts<1:
            raise ValueError('Position exceeds hard risk limit')
        if self.side not in {'long','short'}:
            raise ValueError('Invalid side')
        if self.ambiguity not in {'pessimistic','optimistic','unresolved'}:
            raise ValueError('Unknown OHLC ambiguity model')
        return self

def simulate(path:pd.DataFrame, signal_mid:float, config:ExecutionSettings)->dict:
    config.validate()
    if path.empty or not {'open','high','low','close'}.issubset(path):
        raise ValueError('Missing execution bars')
    if path.index.has_duplicates or not path.index.is_monotonic_increasing:
        raise ValueError('Invalid bar order')
    # Assume signal_mid is executable at the FIRST path bar open only.
    # No gap-free guarantee from signal to next open without external timestamps.
    if not math.isfinite(signal_mid) or signal_mid<=0:
        raise ValueError('Invalid mid')
    if abs(float(path.open.iloc[0])-signal_mid)>1e-9:
        raise ValueError('Entry mid must equal first next-bar open')
    direction=1 if config.side=='long' else -1
    half=config.spread_points/2
    entry=signal_mid+direction*(half+config.slippage_points_per_side)
    stop=entry-direction*config.stop_points
    target=entry+direction*config.target_points
    for timestamp,bar in path.iterrows():
        o,h,l,c=(float(bar[k]) for k in ('open','high','low','close'))
        if not all(math.isfinite(x) and x>0 for x in (o,h,l,c)):
            raise ValueError('Invalid OHLC value')
        if h<max(o,l,c) or l>min(o,h,c):
            raise ValueError('OHLC relation invalid')
        stop_open=o<=stop if direction==1 else o>=stop
        target_open=o>=target if direction==1 else o<=target
        if stop_open:
            price=o  # conservatively worse gap price
            reason='gap_stop'
        elif target_open:
            price=target  # no better than posted target on favorable open
            reason='target_open'
        else:
            stop_hit=l<=stop if direction==1 else h>=stop
            target_hit=h>=target if direction==1 else l<=target
            if stop_hit and target_hit:
                if config.ambiguity=='unresolved':
                    return {'status':'AMBIGUOUS','side':config.side,'net_usd':None,
                            'exit_reason':'same_bar_stop_target','ambiguity':True}
                reason='ambiguous_'+config.ambiguity
                price=stop if config.ambiguity=='pessimistic' else target
            elif stop_hit:
                reason='stop';price=stop
            elif target_hit:
                reason='target';price=target
            else:
                continue
        return _settle(config,entry,price,direction,reason,timestamp)
    return _settle(config,entry,float(path.close.iloc[-1]),direction,
                   'time_exit',path.index[-1])

def _settle(config,entry,exit_mid,direction,reason,at):
    exit_fill=exit_mid-direction*(config.spread_points/2+config.slippage_points_per_side)
    gross_pts=direction*(exit_fill-entry)
    gross_usd=gross_pts*config.multiplier*config.contracts
    commission=2*config.commission_usd_per_side_per_contract*config.contracts
    net_usd=gross_usd-commission
    return {'status':'FILLED','side':config.side,'contracts':config.contracts,
            'entry_fill':entry,'exit_fill':exit_fill,'gross_points':gross_pts,
            'gross_usd':gross_usd,'commission_usd':commission,'net_usd':net_usd,
            'exit_reason':reason,'exit_time':str(at),
            'ambiguity':reason.startswith('ambiguous_')}

def equity_statistics(trades:list[dict],starting_equity:float=100000.0)->dict:
    if not math.isfinite(starting_equity) or starting_equity<=0:
        raise ValueError('Positive starting equity required')
    balance=starting_equity;peak=balance;max_dd=0.0;curve=[balance]
    for trade in trades:
        if trade.get('status')!='FILLED' or trade.get('net_usd') is None:
            raise ValueError('Cannot score incomplete trade')
        balance+=float(trade['net_usd'])
        curve.append(balance)
        peak=max(peak,balance)
        max_dd=max(max_dd,peak-balance)
    return {'start_usd':starting_equity,'end_usd':balance,
            'max_drawdown_usd':max_dd,'equity_curve_usd':curve,
            'scored_trades':len(trades)}
