"""Read-only code/ledger audit. Extra friction never re-generates signals/fills."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.archive_experiments import verify_archive
from scripts.oos_preparation.adapter import sha
from scripts.oos_preparation.year import dump

ROOT=Path(__file__).resolve().parents[1]


def extra_stop_friction(trades,ticks):
    if ticks not in [0,1,2]:raise ValueError('Fixed audit scenarios only')
    stop=trades.exit_reason.isin(['stop','stop_both'])
    # One NQ tick is0.25points or$5. Existing entries are next-open market,
    # not stop orders. Extra friction applies only to the observed stop exit.
    x=trades.net_points.to_numpy(float)-stop.to_numpy()*ticks*.25
    loss=-float(x[x<0].sum());n=int(stop.sum())
    return dict(extra_ticks_per_stop_fill=ticks,stop_fills=n,
        extra_cost_points=n*ticks*.25,extra_cost_usd=n*ticks*5.,
        net_points=float(x.sum()),net_usd=float(x.sum()*20),
        profit_factor=float(x[x>0].sum()/loss) if loss else None,
        adjusted_stop_trade_RT_usd=24.5+ticks*5,other_trade_RT_usd=24.5)


def run():
    verify_archive()
    evidence=json.loads((ROOT/'research/year-holdout-verification.json').read_text());tables=[]
    for period in ['year','combined']:
        name='trades-'+period+'.csv';path=ROOT/'artifacts/year-holdout/first'/name
        if sha(path)!=evidence['files_sha256'][name]:raise ValueError('Verified trade ledger changed')
        t=pd.read_csv(path)
        signal=pd.to_datetime(t.signal_utc,utc=True);entry=pd.to_datetime(t.entry_utc,utc=True)
        if not entry.sub(signal).eq(pd.Timedelta(minutes=1)).all():raise ValueError('Entry timing drift')
        if not np.allclose(t.gross_points-t.net_points,1.225):raise ValueError('Baseline cost drift')
        for model,g in t.groupby('strategy'):
            stop=g.exit_reason.isin(['stop','stop_both'])
            row=dict(period=period,model=model,trades=len(g),stop_fills=int(stop.sum()),
                stop_entry_orders=0,limit_entry_orders=0,market_next_open_entries=len(g),
                stop_on_entry_bar=int((stop&g.entry_utc.eq(g.exit_bar_utc)).sum()),
                target_on_entry_bar=int((g.exit_reason.eq('target')&g.entry_utc.eq(g.exit_bar_utc)).sum()),
                both_stop_target_bars=int(g.both_hit_bar.sum()),
                scenarios=[extra_stop_friction(g,k) for k in [0,1,2]])
            tables.append(row)
    code=ROOT/'scripts/reproduce_research/engine.py'
    d=dict(status='READ_ONLY_EXECUTION_REALISM_AUDIT',independence='New source inspection and hand-derived synthetic tests, not broker/tick certification or a second full engine.',
        engine_sha256=sha(code),ledger_hashes={k:v for k,v in evidence['files_sha256'].items() if k.startswith('trades-')},
        strategy_parameters_changed=False,new_real_data_signals=0,models=tables,
        facts=[
          'All four screens call the same simulate function: signal on completed minute t, entry at raw open of exact minute t+1. No stop-entry or limit-entry implementation exists. A close signal is not a close fill.',
          'Entry always precedes entry-bar extrema because it is the bar open; stop/target are active immediately in that same bar. Actual order submission latency and bracket activation are absent.',
          'If stop and target both lie in any scanned bar, stop wins. Long stop exit=min(stop,bar open), short=max(stop,bar open); target exit is capped at target even after a favorable gap.',
          'Timeout fills at11:59 minute close, assumed available at12:00NY. exit_bar_utc is bar-start label, not exact execution timestamp.',
          'Stop distance=floor(0.25ATR/0.25)*0.25 with minimum0.25; fixed target distance=ceil(0.50ATR/0.25)*0.25. VWAP target rounded down for long/up for short and frozen at signal. Closer stops are not universally conservative.',
          'VWAP resets per raw contract/trade_date, intended18:00NY. It is cumulative sum(volume*(high+low+close)/3)/sum(volume), weighted population SD of the same HLC3 proxy. Current minute becomes known at minute end. If prefix incomplete, the computation begins at first observed bar; eligibility rejects incomplete18NY-noon prefixes.',
          'Flat friction1.225points=$24.50RT:2ticks each side=$20 plus$4.50commission. Prices in ledger are raw hypothetical fills, not slippage-adjusted; friction is subtracted separately. Gap loss is already in raw exit, in addition to flat friction.',
          'London sweep, re-entry and VWAP crossing may all be inferred from the same completed bar; no tick-order proof. Entry at next open prevents a fill earlier in that signal bar.',
          'ORB is a completed-close breakout with volume/VWAP checks, not a resting stop order at the opening-range edge. VWAP Extreme fades at next open; it is not a resting VWAP limit entry.'
        ],
        conservative=[
          'Stop priority when both barriers hit; adverse stop gaps use the worse open; favorable target gaps get no improvement.',
          'No interpolation for missing required minutes; no signal-close fill; constant friction also charged on target/time exits.'
        ],
        blind_spots_or_optimism=[
          'Next-open fill assumes zero compute/transmission latency, executable size and no spread/queue restrictions beyond flat fees.',
          'A target touch is assumed filled: queue position, bid/ask side and traded size are unknown. A minute low/high is not proof a limit order filled.',
          'Same-minute bracket readiness and exact intrabar sequence are unobserved; stop-first does not make all fills conservatively certified.',
          'A session VWAP computed from HLC3 is not exchange tick VWAP; historical vendor timestamps/bar-start convention and publication vintage are not independently certified.',
          'Flat2tick-per-side slippage is not calibrated by volatility, spread, order type or stop cascades. Added stop friction is sensitivity only, not an estimated fill distribution.',
          'At12:00 an immediate close fill at the previous minute last trade is an idealization; exact timestamp and latency remain unknown.'
        ])
    dump(ROOT/'public/data/research-execution-audit.json',d)
    rows=[dict(period=r['period'],model=r['model'],trades=r['trades'],stop_on_entry_bar=r['stop_on_entry_bar'],
               target_on_entry_bar=r['target_on_entry_bar'],both_stop_target_bars=r['both_stop_target_bars'],**s)
          for r in tables for s in r['scenarios']]
    pd.DataFrame(rows).to_csv(ROOT/'public/data/research-execution-audit.csv',index=False)
    print(json.dumps(dict(audit_models=len(tables),new_real_data_signal_calls=0),indent=2))


if __name__=='__main__':run()
