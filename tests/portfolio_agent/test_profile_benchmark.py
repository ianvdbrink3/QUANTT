"""Cash-flow timing, future cutoff, real sources and result integrity."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import pytest

from scripts.profile_benchmark import profile_replay, statistics, fx_frames, MODELS
from scripts.etf_empirical.core import holding
from portfolio_agent.signal_engine import features

ROOT=Path(__file__).resolve().parents[2]


def fixture():
    ix=pd.bdate_range('2018-01-01',periods=650).strftime('%Y-%m-%d')
    c=100+np.arange(len(ix))*.03+np.sin(np.arange(len(ix))*.15)
    f=pd.DataFrame(dict(open=c-.1,high=c+.5,low=c-.5,close=c,volume=10000,distribution=0.),index=ix)
    frames={'QQQ':f,'TQQQ':f.copy()}
    fs={s:features(v).assign(_close=v.close) for s,v in frames.items()}
    return frames,fs,list(ix[400:])


@pytest.mark.parametrize('profile',['defensive','balanced','offensive'])
def test_future_truncation_preserves_decisions_and_all_prior_nav(profile):
    frames,fs,days=fixture()
    a=profile_replay(frames,fs,days,profile,2,100)
    cutoff=days[120]
    prefix={s:v.loc[:cutoff].copy() for s,v in frames.items()}
    pf={s:features(v).assign(_close=v.close) for s,v in prefix.items()}
    b=profile_replay(prefix,pf,days[:121],profile,2,100)
    # Final close liquidation is an explicit endpoint, not a signal.
    assert a['daily_NAV'][:120]==b['daily_NAV'][:120]
    assert a['audit'][:120]==b['audit'][:120]
    assert all(r['decision_day']<r['day'] for r in a['audit'])


def test_monthly_flow_is_not_a_return_or_backdated_purchase():
    frames,fs,days=fixture()
    a=profile_replay(frames,fs,days,'defensive',2,100)
    b=profile_replay(frames,fs,days,'defensive',2,0)
    first=next(i for i,r in enumerate(a['audit']) if r['flow'])
    assert a['audit'][first]['shares']==b['audit'][first]['shares']
    assert a['daily_NAV'][first]==pytest.approx(b['daily_NAV'][first]+100)
    assert a['daily_returns'][:first+1]==b['daily_returns'][:first+1]
    assert a['audit'][first+1]['shares'][0]>b['audit'][first+1]['shares'][0]
    assert a['contributions'][-1]==1000+100*(len({d[:7] for d in days})-1)


def test_dividend_entitlement_is_once_and_not_adjclose_twice():
    ix=['2020-01-01','2020-01-02','2020-01-03','2020-01-06']
    f=pd.DataFrame(dict(open=[100,100,99,99],close=[100,100,99,99],distribution=[0,0,1,0]),index=ix)
    flags=pd.DataFrame({'TREND200':[True,False,False,False]},index=ix)
    # Buy Jan2, own ex-date Jan3 even though we sell at Jan3 open.
    r=holding(f,flags,ix[1:],'TREND200',0)
    assert r['summary']['ending_capital']==1000
    assert r['daily_returns']==[0,0,0]


def test_flat_market_and_nonzero_fees_do_not_generate_profit():
    frames,fs,days=fixture()
    for f in frames.values():
        f.loc[:,['open','close']]=100.
    a=profile_replay(frames,fs,days,'balanced',0,100)
    assert a['daily_NAV'][-1]==pytest.approx(a['contributions'][-1])
    assert np.max(np.abs(a['daily_returns']))<1e-12
    b=profile_replay(frames,fs,days,'balanced',10,100)
    assert b['daily_NAV'][-1]<b['contributions'][-1]
    assert b['fees']>0


def test_fx_open_uses_only_a_prior_date_ecb_reference():
    from scripts.etf_empirical.data import daily
    from scripts.profile_benchmark import FX
    f,_,_=daily();e=fx_frames(f)
    rates=pd.read_csv(FX).set_index('TIME_PERIOD').OBS_VALUE
    day='2022-03-07';rate=rates.loc[rates.index<day].iloc[-1]
    assert e['QQQ'].at[day,'open']==f['QQQ'].at[day,'open']/rate
    assert e['QQQ'].at[day,'close']==f['QQQ'].at[day,'close']/rates.loc[day]


def test_metric_cagr_and_recovery_known_path():
    r=statistics([.1,-.1,0,.2],['2020-01-02','2020-01-03','2020-01-06','2020-01-07'],1188,1000)
    assert r['total_growth_pct']==pytest.approx(18.8)
    assert r['max_DD_pct']==pytest.approx(10)
    assert r['max_underwater_sessions']==2
    assert r['last_drawdown_unrecovered'] is False


def test_published_full_history_coverage_flow_and_unscored_s1_are_honest():
    p=ROOT/'public/data/portfolio-os/profile-benchmark.json';b=json.loads(p.read_text())
    assert len(b['days'])==1967 and b['first']=='2019-01-02' and b['last']=='2026-10-28'
    assert sum(d.startswith('2022-') for d in b['days'])==251
    assert sum(d.startswith('2020-') for d in b['days'])==253
    assert b['s1']['required']==b['s1']['missing_anchors']+b['s1']['anchors']
    assert b['s1']['anchors']==b['s1']['complete_stop_paths']+b['s1']['incomplete_stop_paths']
    assert b['s1']['status']=='CENSORED_UNKNOWN_S1_PATHS'
    assert not any('|defensive'==k[-10:] or '|balanced'==k[-9:] for k in b['curves'])
    assert b['archived_zero_flow_parity_max_error']==dict(defensive=0,balanced=0,offensive=0)
    for row in b['rows']:
        if row['period']!='FULL':continue
        key=f"{row['currency']}|{row['RT_bp']}|{row['monthly']}|{row['model']}"
        assert len(b['curves'][key])==1967
        assert b['curves'][key][-1]==pytest.approx(row['ending'],abs=.00001)
        assert row['contributions']==(10300 if row['monthly'] else 1000)
        assert row['profit']==pytest.approx(row['ending']-row['contributions'])
    lock=json.loads((ROOT/'research/profile-benchmark-register-2026-10-30.json').read_text())
    assert lock['independent_reload_byte_identical'] is True
    assert lock['public_output_sha256']==hashlib.sha256(p.read_bytes()).hexdigest()


@pytest.mark.parametrize('currency',['EUR','USD'])
def test_cost_sensitivity_all_fixed_models(currency):
    b=json.loads((ROOT/'public/data/portfolio-os/profile-benchmark.json').read_text())
    for model in MODELS:
        for monthly in (0,100):
            rows={r['RT_bp']:r for r in b['rows'] if (r['currency'],r['model'],r['monthly'],r['period'])==(currency,model,monthly,'FULL')}
            assert rows[10]['ending']<rows[2]['ending']
