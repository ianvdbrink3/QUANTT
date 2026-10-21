"""Next-generation overlap-first orchestration; frozen 0.9 files stay unchanged.

No fallback ATR, cross-contract price mixing, missing-bar fill or forced eligibility.
The gate makes an insufficient roll a visible data error BEFORE signal computation.
"""
from dataclasses import dataclass
from typing import Callable
import numpy as np
import pandas as pd
from . import engine


@dataclass(frozen=True)
class ATRState:
    contract: str
    session: str
    asof_utc: pd.Timestamp
    valid_prior_ranges: int
    atr14: float | None
    contributing_sessions: tuple[str,...]

    @property
    def ready(self):
        return self.atr14 is not None and self.atr14 > 0


class WarmupNotReady(ValueError):
    pass


class ContractATRCache:
    """Immutable as-of states for active AND inactive contract sessions."""
    def __init__(self, states):
        self._states = states

    @classmethod
    def from_bars(cls, full):
        required={'contract','trade_date','open','high','low','close','volume'}
        if not required.issubset(full.columns):
            raise ValueError('Missing canonical contract OHLCV columns')
        if not isinstance(full.index,pd.DatetimeIndex) or full.index.tz is None:
            raise ValueError('Timezone-aware bar timestamps required')
        if full[['contract','trade_date']].isna().any().any():
            raise ValueError('Missing contract/session identity')
        states={}
        for contract,raw in full.groupby('contract'):
            if raw.index.has_duplicates:
                raise ValueError('Deduplicate and reconcile source overlap first: '+contract)
            raw=raw.sort_index()
            history=[]
            previous_complete=False
            previous_close=np.nan
            for day,g in raw.groupby('trade_date',sort=True):
                prev=(pd.Timestamp(day)-pd.Timedelta(days=1)).strftime('%Y-%m-%d')
                asof=engine.time_at(prev,'18:00')
                contributing=history[-14:]
                atr=float(np.mean([x[1] for x in contributing])) if len(contributing)==14 else None
                states[contract,day]=ATRState(contract,day,asof,len(history),atr,
                                              tuple(x[0] for x in contributing))
                a,b=engine.time_at(day,'09:30'),engine.time_at(day,'16:00')
                rth=engine.window(g,a,b)
                complete=engine.complete(rth,a,b)
                if complete and previous_complete:
                    tr=max(float(rth.high.max()-rth.low.min()),
                           abs(float(rth.high.max())-previous_close),
                           abs(float(rth.low.min())-previous_close))
                    if not np.isfinite(tr) or tr<0:
                        raise ValueError('Invalid same-contract RTH true range')
                    history.append((day,tr))
                previous_complete=complete
                previous_close=float(rth.close.iloc[-1]) if complete else np.nan
        return cls(states)

    def state(self, contract, session):
        try:
            return self._states[contract,session]
        except KeyError as exc:
            raise WarmupNotReady(f'No source session for {contract} {session}') from exc

    def require_ready(self, contract, session):
        state=self.state(contract,session)
        if not state.ready:
            raise WarmupNotReady(f'{contract} {session}: {state.valid_prior_ranges}/14 valid prior same-contract TR; refusing a fabricated or transferred ATR')
        return state


@dataclass(frozen=True)
class Activation:
    contract: str
    session: str


@dataclass
class PreparedResearch:
    master: pd.DataFrame
    daily: pd.DataFrame
    snapshots: pd.DataFrame
    gaps: pd.DataFrame
    atr_cache: ContractATRCache


def active_mask(frame, schedule):
    if not schedule or any(a.session>=b.session for a,b in zip(schedule,schedule[1:])):
        raise ValueError('Activation schedule must have unique increasing session dates')
    mask=np.zeros(len(frame),dtype=bool)
    for i,item in enumerate(schedule):
        selected=frame.contract.eq(item.contract)&frame.trade_date.ge(item.session)
        if i+1<len(schedule):
            selected &= frame.trade_date.lt(schedule[i+1].session)
        mask |= selected.to_numpy()
    return mask


def prepare_with_overlap(full, schedule, *, calendar_grid:Callable, require_day1_atr=True):
    """All source history first, activation last. No strategy runs in this function.

    ATR readiness is necessary but not sufficient for trade eligibility: the
    frozen prefix, same-clock volume history and required windows still apply.
    """
    active_mask(full,schedule)  # Validate before any feature computation.
    cache=ContractATRCache.from_bars(full)
    if require_day1_atr:
        for item in schedule[1:]:
            cache.require_ready(item.contract,item.session)
    old=engine.expected_grid
    engine.expected_grid=calendar_grid
    try:
        enriched,daily,snapshots,gaps=engine.build_features(full)
    finally:
        engine.expected_grid=old
    # The cache must reproduce the frozen contract-native ATR, not redefine it.
    for row in daily.itertuples():
        state=cache.state(row.contract,row.trade_date)
        expected=state.atr14 if state.atr14 is not None else np.nan
        if not np.isclose(row.atr14_prior,expected,equal_nan=True):
            raise ValueError('Frozen ATR/cache disagreement')
    master=enriched.loc[active_mask(enriched,schedule)].sort_index()
    if not master.index.is_unique or master.groupby('trade_date').contract.nunique().gt(1).any():
        raise ValueError('Activation selected mixed/duplicate contract bars')
    return PreparedResearch(master,daily.loc[active_mask(daily,schedule)],
                            snapshots.loc[active_mask(snapshots,schedule)],
                            gaps.loc[active_mask(gaps,schedule)] if len(gaps) else gaps,cache)
