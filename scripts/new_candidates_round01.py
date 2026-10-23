"""Two fixed exploratory NQ translations. No new historical-sample access."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scripts.afternoon_inference_round import sha, dump, verify_lock

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/'research/new-candidates-round01-protocol.json'
LOCK=ROOT/'research/new-candidates-round01-lock.json'
OUT=ROOT/'research/new-candidates-round01-results.json'
COST=1.225
CLOSED=set('2024-12-25 2025-01-01 2025-01-09 2025-01-20 2025-02-17 2025-04-18 2025-05-26 2025-06-19 2025-07-04 2025-09-01 2025-11-27 2025-12-25 2026-01-01 2026-01-19 2026-02-16 2026-04-03 2026-05-25 2026-06-19 2026-07-03 2026-09-07'.split())


def cash_calendar(start='2024-12-01',end='2026-09-30'):
    return [d for d in pd.bdate_range(start,end).strftime('%Y-%m-%d') if d not in CLOSED]


def tom_dates():
    dates=pd.DataFrame({'day':cash_calendar()})
    dates['month']=dates.day.str[:7]
    chosen=set()
    for _,g in dates.groupby('month'):
        chosen.update(g.day.iloc[:3]);chosen.add(g.day.iloc[-1])
    return chosen


def morning_direction(prefix_close,prior_close):
    # The function accepts only completed09:30-09:59 closes, not later bars.
    prefix=np.asarray(prefix_close,float)
    if prefix.shape!=(30,): raise ValueError('Exactly thirty completed opening bars required')
    if not np.isfinite(prior_close) or not np.isfinite(prefix).all(): return 0
    return int(np.sign(prefix[-1]-prior_close))


def trade(day,prices,start,stop,direction):
    entry=float(prices['open'][start]);exit_=float(prices['close'][stop-1])
    high=float(np.max(prices['high'][start:stop]));low=float(np.min(prices['low'][start:stop]))
    gross=direction*(exit_-entry)
    return dict(day=day,month=day[:7],quarter=str(pd.Period(day,freq='Q')),direction=int(direction),
        entry=entry,exit=exit_,gross_points=gross,net_points=gross-COST,
        mfe_points=max(0.,high-entry if direction>0 else entry-low),
        mae_points=max(0.,entry-low if direction>0 else high-entry),
        entry_minute=start,exit_minute=stop-1,exit_reason='FIXED_TIME')


def distribution(x):
    x=np.asarray(x,float)
    return dict(zip(['p10','p25','median','p75','p90'],map(float,np.quantile(x,[.1,.25,.5,.75,.9])))) if len(x) else None


def metrics(frame):
    x=frame.net_points.to_numpy(float)
    if not len(x):return {'trades':0}
    eq=np.r_[0.,x.cumsum()]
    loss=-x[x<0].sum();net=float(x.sum())
    return dict(trades=len(x),gross_points=float(frame.gross_points.sum()),net_points=net,net_dollars=net*20,
        mean_net=float(x.mean()),median_net=float(np.median(x)),winrate=float((x>0).mean()),
        profit_factor=float(x[x>0].sum()/loss) if loss else None,
        max_closed_equity_drawdown=float((np.maximum.accumulate(eq)-eq).max()),worst_day=float(x.min()),
        top3_positive_share_of_net=float(np.sort(x[x>0])[-3:].sum()/net) if net>0 else None,
        mfe_points=distribution(frame.mfe_points),mae_points=distribution(frame.mae_points),
        cost_sensitivity=[dict(extra_ticks_per_leg=t,total_cost_points=COST+.5*t,
            mean_net=float(x.mean()-.5*t),net_points=float(x.sum()-.5*t*len(x)),
            net_dollars=float((x.sum()-.5*t*len(x))*20)) for t in [0,1,2]])


def resampled_intervals(frame,benchmark,tom=False):
    months=sorted(set(frame.month)|set(benchmark.month))
    data=[]
    for month in months:
        a=frame[frame.month.eq(month)].net_points.to_numpy(float)
        b=benchmark[benchmark.month.eq(month)].net_points.to_numpy(float)
        if len(a) and not len(b):raise ValueError('Missing within-month benchmark')
        # For morning the benchmark has matching dates; for TOM standardize
        # non-TOM means to each month's number of TOM events.
        if tom:
            baseline=float(b.mean()*len(a)) if len(a) else 0.
        else:
            baseline=float(b.sum())
        data.append([float(a.sum()),len(a),baseline])
    values=np.asarray(data,float)
    rng=np.random.default_rng(20261022051)
    picks=rng.integers(0,len(values),size=(5000,len(values)))
    sums=values[picks].sum(axis=1);valid=sums[:,1]>0
    means=sums[valid,0]/sums[valid,1]
    diff=(sums[valid,0]-sums[valid,2])/sums[valid,1]
    total=values.sum(axis=0)
    return dict(month_clusters=len(months),mean_nominal95=list(map(float,np.quantile(means,[.025,.975]))),
        benchmark_matched_mean=float(total[2]/total[1]),incremental_mean=float((total[0]-total[2])/total[1]),
        incremental_nominal95=list(map(float,np.quantile(diff,[.025,.975]))),
        confirmatory_p=None,formal_status='EXPLORATORY_NOT_VALIDATED',
        interval_limit='Nominal monthly percentile bootstrap, not simultaneous or a universal dependence guarantee')


def prepare():
    verify_lock()
    names=[PROTOCOL,Path(__file__),ROOT/'research/oos-year-sources.json',ROOT/'research/oos-year-rollovers.json',
        ROOT/'research/holdout-protocol.json',ROOT/'research/oos-year-calendar.json',ROOT/'artifacts/raw-market/quality.json',
        ROOT/'scripts/causal_map/__main__.py',ROOT/'scripts/oos_preparation/year.py']
    result=dict(status='LOCKED_BEFORE_FIRST_NEW_CANDIDATE_RUN',inputs={str(p.relative_to(ROOT)):sha(p) for p in names},
        independent_preregistration=False,new_historical_outcomes_released=False)
    if LOCK.exists():verify();return
    with LOCK.open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
    print('Two exploratory rules and benchmarks locked. Independent sample remains sealed.',flush=True)


def verify():
    verify_lock()
    lock=json.loads(LOCK.read_text())
    for name,digest in lock['inputs'].items():
        if sha(ROOT/name)!=digest:raise ValueError('Exploratory input changed: '+name)
    manifest=json.loads((ROOT/'research/oos-year-sources.json').read_text())
    for item in manifest['sources']+manifest['warmup_sources']:
        if 'historical-replication' in item['relative_private_path']:raise PermissionError('Sealed sample')
        if item['contract'] not in ['NQH25','NQM25','NQU25','NQZ25','NQH26','NQM26','NQU26','NQZ26']:
            raise PermissionError('Unexpected contract in exploration')
    return lock


def compute(state,included):
    selected=tom_dates();momentum=[];momentum_base=[];tom=[];other=[];all_rth=[];exclusions=[]
    for day in included:
        if not '2024-12-30'<=day<='2026-09-30':raise PermissionError('Exploration date outside consumed window')
        prices,context=state[day]
        direction=morning_direction(prices['close'][:30],context['prior_close'])
        if direction:
            momentum.append(trade(day,prices,360,390,direction))
            momentum_base.append(trade(day,prices,360,390,1))
        else:exclusions.append(dict(day=day,reason='MISSING_PRIOR_COMPLETE_RTH' if not np.isfinite(context['prior_close']) else 'FLAT_OPENING_SIGNAL'))
        if day<'2025-01-01':continue
        if day not in cash_calendar():raise ValueError('Quality session is not a cash trading day')
        row=trade(day,prices,0,390,1);all_rth.append(row)
        (tom if day in selected else other).append(row)
    frames=dict(MORNING_TO_CLOSE=pd.DataFrame(momentum),TURN_OF_MONTH_RTH=pd.DataFrame(tom))
    bases=dict(MORNING_TO_CLOSE=pd.DataFrame(momentum_base),TURN_OF_MONTH_RTH=pd.DataFrame(other))
    results={}
    for name,frame in frames.items():
        results[name]=dict(metrics=metrics(frame),benchmark=metrics(bases[name]),
            uncertainty=resampled_intervals(frame,bases[name],name=='TURN_OF_MONTH_RTH'),
            quarterly={k:metrics(g) for k,g in frame.groupby('quarter')},
            monthly={k:metrics(g) for k,g in frame.groupby('month')},
            direction={str(k):metrics(g) for k,g in frame.groupby('direction')})
    results['TURN_OF_MONTH_RTH']['all_days_long']=metrics(pd.DataFrame(all_rth))
    return results,frames,bases,exclusions


def run():
    lock=verify()
    # This loader only reads registered2024-2026 sources; no Downloads scanning.
    from scripts.causal_map.__main__ import load_inputs
    state,scheduled,included,provenance,active,calendar,rolls=load_inputs()
    results,frames,bases,exclusions=compute(state,included)
    out=ROOT/'artifacts/new-candidates-round01';out.mkdir(parents=True,exist_ok=True)
    # Recompute rules/ledger independently from immutable state, compare bytes.
    replay,replay_frames,_,_=compute(state,included)
    if results!=replay:raise ValueError('Deterministic replay result mismatch')
    hashes={}
    for name,frame in frames.items():
        payload=frame.to_csv(index=False,float_format='%.10f')
        if payload!=replay_frames[name].to_csv(index=False,float_format='%.10f'):raise ValueError('Ledger replay differs')
        path=out/(name.lower()+'-trades.csv');path.write_text(payload);hashes[str(path.relative_to(ROOT))]=sha(path)
        bases[name].to_csv(out/(name.lower()+'-benchmark.csv'),index=False,float_format='%.10f')
    result=dict(status='TWO_EXPLORATORY_BACKTESTS_COMPLETE_NOT_VALIDATED',rules_sha256=sha(PROTOCOL),
        period=['2024-12-30','2026-09-30'],source_files=provenance['source_files'],fixed_complete_days=len(included),
        new_historical_sample_read=False,frozen_models_changed=False,results=results,
        morning_signal_exclusions=exclusions,ledger_hashes=hashes,deterministic_same_input_replay=True,
        independent_source_reload_verified=False,inputs=lock['inputs'])
    dump(OUT,result);verify()
    lines=['# Twee nieuwe verkennende NQ-kandidaten','',
        'Uitsluitend bestaande ontdekkingsdata: 30 december 2024–30 september 2026, 435 complete RTH-dagen. Geen onafhankelijke validatie. De historische 2019–2021-steekproef is niet door deze runner gelezen. Geen nieuwe filters, stops, targets of zoeklus. Beide regels en vergelijkingen waren vóór de eerste berekening gehasht.','',
        '| Kandidaat | Trades | Netto punten | Netto USD | Winrate | PF | Max gesloten DD pt | Gem. netto pt | Verschil benchmark pt | Nominaal 95%-interval verschil |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    for name,r in results.items():
        m,u=r['metrics'],r['uncertainty'];pf=f"{m['profit_factor']:.3f}" if m['profit_factor'] is not None else 'n.v.t.'
        lines.append(f"| {name} | {m['trades']} | {m['net_points']:.2f} | {m['net_dollars']:.2f} | {100*m['winrate']:.1f}% | {pf} | {m['max_closed_equity_drawdown']:.2f} | {m['mean_net']:.2f} | {u['incremental_mean']:.2f} | [{u['incremental_nominal95'][0]:.2f}; {u['incremental_nominal95'][1]:.2f}] |")
    lines += ['', '## Vastgelegde regels en vergelijking','',
        '- Ochtend-naar-slot: teken van vorige complete RTH-close (causaal omgerekend naar huidig contract) tot 09:59 close. Entry 15:30 open, exit 15:59 close. Vergelijking: altijd long op dezelfde dagen in hetzelfde slot-halfuur. Geen 15:00-hypothese en geen ORB-hergebruik.',
        '- Maandwisseling: laatste plus eerste drie cash-beursdagen, alleen RTH long. Kalenderposities gebruiken ook korte beursdagen; trades uitsluitend op bestaande volledige kwaliteitsdagen. Benchmark: andere volledige dagen in dezelfde maand, gewogen naar aantal maandwissel-events. December 2024 is vooraf uitgesloten als onvolledige kalendermaand.',
        '- Oorspronkelijke literatuur betreft aandelen/ETF’s, niet NQ. Ochtendrichting omvat overnight; maandwisseling hier juist alleen RTH. De laatste is expliciet een aanpassing, niet een exacte replicatie.',
        '- Eén NQ, 1,225 pt ($24,50) per ronde; gevoeligheid +1/+2 extra ticks per kant staat in JSON. Open/close zijn barprijsproxies, geen bewezen uitvoerbare fills. Geen intrabar stopvolgorde. Margin- en intratrade-drawdownrisico zijn niet met gesloten-equity DD afgedekt.','',
        '## Onzekerheid en volledige resultaten','',
        'De JSON bevat alle maanden/kwartalen, long/short, MFE/MAE-percentielen, verliesdagen en winstconcentratie. Intervallen zijn nominale maandblok-bootstrapintervallen, geen multipliciteitsgecorrigeerd bewijs. Er zijn twee model- en twee benchmarkclaims mogelijk; geen confirmatoire p-waarde of promotie toegekend. Een positieve puntschatting is geen winstgevend gevalideerd model.','',
        'Identieke herberekening vanuit dezelfde geladen staat is gecontroleerd. Dit is géén onafhankelijke bronherlaad-reproductie; die status wordt apart geregistreerd. Private tradeledgers blijven Gitignored onder artifacts. Geen GitHub-push of publicatie uitgevoerd.','', '## Bronnen','']
    for url in json.loads(PROTOCOL.read_text())['sources']:lines.append('- '+url)
    (ROOT/'docs/NEW_CANDIDATES_ROUND01_REPORT.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({n:r['metrics'] for n,r in results.items()},indent=2),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','run','verify']);args=parser.parse_args()
    {'prepare':prepare,'run':run,'verify':verify}[args.action]()
