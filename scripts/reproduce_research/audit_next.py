"""Private, descriptive audit; never republishes or reruns frozen strategies.

Run: .venv/bin/python -m scripts.reproduce_research.audit_next --run artifacts/holdout-7u52wd25
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from . import holdout_data
from .next_engine import ContractATRCache

ROOT = Path(__file__).resolve().parents[2]
NAMES = {'C_VWAP_extreme':'VWAP Extreme', 'A_London_sweep':'London Sweep',
         'B_ORB15':'ORB 15m', 'B_ORB5':'ORB 5m'}


def metrics(trades):
    p = trades.net_points
    losses = float(-p[p < 0].sum())
    return {'trades':len(p), 'net_points':float(p.sum()),
            'net_usd':float(p.sum()*20),
            'profit_factor':float(p[p > 0].sum()/losses) if losses else None,
            'winrate':float((p > 0).mean()) if len(p) else None,
            'mean_points':float(p.mean()) if len(p) else None}


def audit(run, output):
    protocol = json.loads((ROOT/'research/holdout-protocol.json').read_text())
    reference = json.loads((ROOT/'research/holdout-reference.json').read_text())
    evidence = json.loads((ROOT/'research/holdout-verification-evidence.json').read_text())
    assert holdout_data.sha(ROOT/'research/holdout-reference.json') == evidence['reference_sha256']
    assert holdout_data.sha(ROOT/'research/holdout-protocol.json') == evidence['protocol_sha256']
    for name, digest in reference['code_sha256'].items():
        assert holdout_data.sha(ROOT/'scripts/reproduce_research'/name) == digest, name
    for name, digest in evidence['private_output_sha256'].items():
        assert holdout_data.sha(run/name) == digest, name
    # load_all validates every raw SHA and reconciles per-contract duplicates.
    full, _ = holdout_data.load_all(ROOT/'data/raw', protocol['sources'])
    cache = ContractATRCache.from_bars(full)
    quality = pd.read_csv(run/'session-quality.csv')
    # Independent cache vs every frozen selected session, not just roll dates.
    for row in quality.itertuples():
        state = cache.state(row.contract, row.trade_date)
        assert np.isclose(row.atr14_prior, state.atr14 if state.ready else np.nan, equal_nan=True)
    rolls = []
    for roll in protocol['rollovers']:
        state = cache.state(roll['to'], roll['effective_session'])
        active = quality[quality.contract.eq(roll['to']) & quality.trade_date.ge(state.session)]
        ready = active[active.atr14_prior.notna()]
        rolls.append({'contract':state.contract, 'roll_session':state.session,
                      'valid_prior_TR':state.valid_prior_ranges, 'ATR_ready_day1':state.ready,
                      'first_ready_session':None if ready.empty else ready.trade_date.iloc[0],
                      'selected_sessions_without_ATR':int(active.atr14_prior.isna().sum())})
    trades = pd.read_csv(run/'trades.csv')
    eligible = pd.read_csv(run/'eligibility.csv')
    start, end = reference['period']['start'], reference['period']['end']
    trades = trades[trades.trade_date.between(start,end)]
    eligible = eligible[eligible.trade_date.between(start,end) & eligible.eligible.eq(True)]
    result = {'classification':'DESCRIPTIVE_POST_HOC_NOT_NEW_HOLDOUT',
              'raw_hashes_verified':len(protocol['sources']), 'rollovers':rolls,
              'cost_rt_usd':reference['cost_rt_usd'], 'strategies':{},
              'limitations':'Calendar summer (June-August), not a fitted compression threshold. Missing warmup sessions cause sample selection; no causal or significance claim.'}
    for key, name in NAMES.items():
        t, e = trades[trades.strategy.eq(key)], eligible[eligible.strategy.eq(key)]
        whole = metrics(t)
        frozen = reference['holdout'][key]['all']
        for field in ['trades','net_points','profit_factor','winrate']:
            assert np.isclose(whole[field], frozen['win_rate' if field=='winrate' else field]), (key, field)
        groups = {}
        for group, summer in [('summer',True),('non_summer',False)]:
            dates = e[e.trade_date.between('2025-06-01','2025-08-31').eq(summer)].trade_date
            q = quality[quality.trade_date.isin(dates)]
            groups[group] = {**metrics(t[t.trade_date.isin(dates)]),
                             'eligible_days':len(dates),
                             'mean_prior_RTH_ATR':float(q.atr14_prior.mean()),
                             'mean_premarket_range':float((q.premarket_high-q.premarket_low).mean())}
        result['strategies'][key] = {'name':name, 'whole_holdout':whole, **groups}
    output.mkdir(parents=True, exist_ok=True)
    (output/'audit.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    lines = ['# ATR-overlap en referentiestrategieën', '',
             'Bevroren 0.9-resultaten ongewijzigd. 30 bronhashes en alle zes private outputhashes gecontroleerd.', '',
             '## Rollovercontrole', '',
             '| Contract | Roll | Geldige prior TR | Dag 1 ATR gereed | Eerste ATR-dag | Sessies zonder ATR |',
             '|---|---|---:|---|---|---:|']
    for r in rolls:
        lines.append(f"| {r['contract']} | {r['roll_session']} | {r['valid_prior_TR']}/14 | {r['ATR_ready_day1']} | {r['first_ready_session']} | {r['selected_sessions_without_ATR']} |")
    lines += ['', 'De bestaande engine gebruikte de overlap al. De nieuwe laag maakt contracteigen ATR-status expliciet en blokkeert een onvolledig voorbereide rollover vóór feature-/signaalberekening. Geen prijsvermenging of ontbrekende minuten ingevuld.', '',
              '## Holdout 18 april – 30 september 2025', '',
              'Netto na $24,50 per roundtrip; NQ $20 per punt. Elke strategie heeft 81 eligible dagen.', '',
              '| Strategie | Trades | Netto punten | Netto USD | PF | Winrate |', '|---|---:|---:|---:|---:|---:|']
    for v in result['strategies'].values():
        m=v['whole_holdout']
        lines.append(f"| {v['name']} | {m['trades']} | {m['net_points']:.3f} | {m['net_usd']:.2f} | {m['profit_factor']:.3f} | {m['winrate']:.1%} |")
    lines += ['', '## Kalenderzomer versus overige holdout', '',
              'Juni–augustus vooraf als kalendergroep gekozen, niet geoptimaliseerd. 43 versus 38 eligible dagen.', '',
              '| Strategie | Zomer trades | Zomer netto pt | Zomer PF | Overig netto pt | Overig PF |', '|---|---:|---:|---:|---:|---:|']
    for v in result['strategies'].values():
        a,b=v['summer'],v['non_summer']
        lines.append(f"| {v['name']} | {a['trades']} | {a['net_points']:.3f} | {a['profit_factor']:.3f} | {b['net_points']:.3f} | {b['profit_factor']:.3f} |")
    v=result['strategies']['C_VWAP_extreme']
    lines += ['', f"Gemiddelde vooraf bekende RTH ATR: zomer {v['summer']['mean_prior_RTH_ATR']:.2f} versus overig {v['non_summer']['mean_prior_RTH_ATR']:.2f} punten. Pre-market range: {v['summer']['mean_premarket_range']:.2f} versus {v['non_summer']['mean_premarket_range']:.2f} punten.", '',
              'VWAP profiteerde niet van deze kalenderzomer: verlies, lagere PF en slechter dan beide ORB-modellen op PF. Een hoger winstpercentage impliceert geen positieve verwachting. London Sweep is eveneens een mean-reversionmodel; niet alle mean-reversionmodellen reageren hetzelfde.', '',
              'Dit is beschrijvend: kalenderzomer is geen causale compressietest; 19 zomerse VWAP-trades en uitgesloten warmup-dagen beperken de conclusie. Geen parameterwijziging, nieuwe hypothesepromotie of aanpassing van het holdout-oordeel.']
    (output/'REPORT.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'status':'PASS', 'output':str(output), 'rollovers':rolls},indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=ROOT/'artifacts/next-engine-audit')
    args=parser.parse_args()
    audit(args.run,args.output)
