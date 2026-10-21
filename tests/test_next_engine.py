import pandas as pd
import numpy as np
import pytest
from scripts.reproduce_research import engine,holdout_data
from scripts.reproduce_research.next_engine import (
    Activation,ContractATRCache,WarmupNotReady,prepare_with_overlap,active_mask)


def session(contract,day,price=100.):
    return pd.DataFrame({'open':price,'high':price+1,'low':price-1,'close':price,
                         'volume':100,'contract':contract,'trade_date':day},index=holdout_data.grid(day))


@pytest.fixture(scope='module')
def overlap():
    frames=[session('NQU25',d.strftime('%Y-%m-%d'))
            for d in pd.bdate_range('2025-05-20','2025-06-17')]
    frames=[x for x in frames if len(x)]
    frames += [session('NQM25','2025-06-16',20000.),session('NQM25','2025-06-17',20000.)]
    return pd.concat(frames).sort_index()


def test_roll_day1_is_actually_trade_eligible_when_complete_overlap_exists(overlap):
    schedule=[Activation('NQM25','2025-06-16'),Activation('NQU25','2025-06-17')]
    prepared=prepare_with_overlap(overlap,schedule,calendar_grid=holdout_data.grid)
    g=prepared.master[prepared.master.trade_date.eq('2025-06-17')]
    _,eligibility=engine.hypotheses(g)
    assert len(eligibility)==4 and eligibility.eligible.all()
    assert g.contract.unique().tolist()==['NQU25']
    assert g.atr14_prior.eq(2.).all()  # No outgoing 20,000-price jump in ATR.
    assert pd.isna(g.return_1m.iloc[0])  # No cross-contract return.
    assert prepared.atr_cache.require_ready('NQU25','2025-06-17').atr14==2.


def test_filtering_before_warmup_loses_history_but_cache_preloads_it(overlap):
    cache=ContractATRCache.from_bars(overlap)
    assert cache.state('NQU25','2025-06-17').ready
    trimmed=overlap[overlap.contract.eq('NQU25')&overlap.trade_date.ge('2025-06-17')]
    assert ContractATRCache.from_bars(trimmed).state('NQU25','2025-06-17').valid_prior_ranges==0


def test_current_and_future_prices_cannot_change_roll_open_atr(overlap):
    before=ContractATRCache.from_bars(overlap).state('NQU25','2025-06-17')
    changed=overlap.copy()
    changed.loc[changed.contract.eq('NQU25')&changed.trade_date.ge('2025-06-17'),['open','high','low','close']]+=10000
    after=ContractATRCache.from_bars(changed).state('NQU25','2025-06-17')
    assert before==after
    assert max(before.contributing_sessions)<'2025-06-17'
    assert before.asof_utc==pd.Timestamp('2025-06-16T22:00:00Z')


def test_day1_atr_is_not_sufficient_when_prefix_has_a_gap(overlap):
    missing=engine.time_at('2025-06-17','09:00')
    broken=overlap[~(overlap.contract.eq('NQU25')&(overlap.index==missing))]
    prepared=prepare_with_overlap(broken,[Activation('NQM25','2025-06-16'),Activation('NQU25','2025-06-17')],calendar_grid=holdout_data.grid)
    _,e=engine.hypotheses(prepared.master[prepared.master.trade_date.eq('2025-06-17')])
    assert prepared.atr_cache.state('NQU25','2025-06-17').ready
    assert not e.eligible.any()


def test_short_overlap_fails_before_feature_or_signal_computation(monkeypatch):
    full=pd.concat([session('NQU25',d) for d in ['2025-06-12','2025-06-13','2025-06-16','2025-06-17']])
    def forbidden(*args,**kwargs):
        pytest.fail('Feature generation must not run after failed readiness gate')
    monkeypatch.setattr(engine,'build_features',forbidden)
    with pytest.raises(WarmupNotReady,match='2/14'):
        prepare_with_overlap(full,[Activation('NQM25','2025-06-12'),Activation('NQU25','2025-06-17')],calendar_grid=holdout_data.grid)


def test_duplicate_contract_bars_are_not_silently_used(overlap):
    with pytest.raises(ValueError,match='Deduplicate'):
        ContractATRCache.from_bars(pd.concat([overlap,overlap.iloc[:1]]))


def test_calendar_and_timezone_validation(overlap):
    bad=overlap.copy();bad.index=bad.index.tz_localize(None)
    with pytest.raises(ValueError,match='Timezone-aware'):
        ContractATRCache.from_bars(bad)
    with pytest.raises(ValueError,match='increasing'):
        active_mask(overlap,[Activation('NQU25','2025-06-17'),Activation('NQM25','2025-06-16')])
