"""Date/contract adapter shared by readiness and historical replay.

Future scoring is deliberately unavailable. Readiness computes ONLY prior ATR,
same-clock volume history and exact-window completeness, never VWAP or signals.
"""
import numpy as np
import pandas as pd

from .adapter import at
from scripts.reproduce_research.continuous import continuous_daily, apply_indicators
from scripts.reproduce_research.next_engine import active_mask
from scripts.reproduce_research.volume_path import active_volume_history

STRATEGIES = ['A_London_sweep','B_ORB5','B_ORB15','C_VWAP_extreme']
HISTORICAL_END = '2025-09-30'


def select_active(full, schedule):
    active = full.loc[active_mask(full,schedule)].sort_index()
    if active.index.has_duplicates or active.groupby('trade_date').contract.nunique().gt(1).any():
        raise ValueError('Mixed or duplicate active stream')
    return active


def indicator_state(full, schedule):
    active = select_active(full,schedule)
    daily, rolls = continuous_daily(full,schedule)
    lookup = daily.set_index('trade_date')
    state = active_volume_history(active)
    state['atr14_prior'] = state.trade_date.map(lookup.atr14_continuous)
    return state, daily, rolls


def technical_eligibility(state, calendar, start, end):
    """Same predicates as frozen hypotheses, including missing-day failures.

    No signal columns are required or inspected. Missing current bars never
    turn a required window into a shorter 'complete' window.
    """
    groups = {d:g for d,g in state.groupby('trade_date',sort=True)}
    rows=[]
    for day in pd.bdate_range(start,end).strftime('%Y-%m-%d'):
        if not len(calendar.grid(day)):
            continue
        g=groups.get(day,state.iloc[:0])
        prev=(pd.Timestamp(day)-pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        prefix=pd.date_range(at(prev,'18:00'),at(day,'12:00'),freq='min',inclusive='left')
        actual=g.index[(g.index>=prefix.min()) & (g.index<at(day,'12:00'))]
        prefix_good=actual.equals(prefix)
        atr=float(g.atr14_prior.iloc[0]) if len(g) else np.nan
        atr_good=bool(np.isfinite(atr) and atr>0)
        refs=g.loc[(g.index>=at(day,'09:30')) & (g.index<at(day,'11:00')),'prior_same_minute_median_volume']
        # Frozen predicate is len>0 and all nonnull; prefix already enforces90.
        volume_good=bool(len(refs)>0 and refs.notna().all())
        for strategy in STRATEGIES:
            reasons=[]
            if not len(g): reasons.append('missing_session')
            if not prefix_good: reasons.append('incomplete_18_to_noon_prefix')
            if not atr_good: reasons.append('prior_ATR_not_ready')
            if strategy.startswith('B') and not volume_good: reasons.append('same_clock_volume_not_ready')
            rows.append(dict(strategy=strategy,trade_date=day,eligible=not reasons,
                reasons=reasons,prefix_complete=prefix_good,atr_ready=atr_good,
                volume_ready=volume_good,contract=g.contract.iloc[0] if len(g) else None))
    return pd.DataFrame(rows)


def historical_features(full, schedule, calendar):
    # Guard BEFORE any feature construction. No allow-future flag exists.
    if full.empty or not full.trade_date.le(HISTORICAL_END).all():
        raise PermissionError('HOLDOUT_LOCKED: no future features or scoring authorized')
    from scripts.reproduce_research import engine
    old=engine.expected_grid
    try:
        engine.expected_grid=calendar.grid
        enriched,_,_,_=engine.build_features(full)
    finally:
        engine.expected_grid=old
    master=select_active(enriched,schedule)
    daily,_=continuous_daily(full,schedule)
    return active_volume_history(apply_indicators(master,daily))


def replay_historical(full, schedule, calendar):
    if full.empty or not full.trade_date.le(HISTORICAL_END).all():
        raise PermissionError('HOLDOUT_LOCKED: scoring route rejects dates after2025-09-30')
    from scripts.reproduce_research import engine
    return engine.hypotheses(historical_features(full,schedule,calendar))
