"""python -m scripts.price_volume register|replay|verify (local research only)."""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from scripts import asymmetric_regime as prior
from scripts import historical_calendar_v2 as calv2
from scripts.causal_map.__main__ import load_inputs
from scripts.historical_validation import __main__ as historical
from scripts.price_volume import core as c

h = prior.h
ROOT = h.ROOT
OUT = ROOT/'artifacts/price-volume'
LOCK = ROOT/'research/price-volume-lock.json'
RESULT = ROOT/'research/price-volume-results.json'
PROOF = ROOT/'research/price-volume-verification.json'
REPORT = ROOT/'docs/PRICE_VOLUME_DEVELOPMENT_EXPLORATION.md'
BLOCKS = ('COMBINED', '2019_2021', '2024_2026')
METHOD = dict(
    date='2026-10-25', status='EXPLORATORY_CONSUMED_DEVELOPMENT_POOL',
    universe='Exactly previous1151 priorATR-ready sessions:733 historical plus418 recent. Missing17 ATR dates remain excluded, not imputed. Every variant reported, no best-only selection.',
    daily='Cash-session RTH closes, including known early closes, at calendar close capped16:00. SMA20 needs20 immediately preceding cash-session closes, all complete; unknown days invalidate windows rather than being skipped. Yesterday close and SMA20 are available before09:30. No additional5day momentum filter. Current-day SMA20 includes its terminal RTH close and19 previous cash closes, known only after16:00.',
    rolls='Daily closes translated by cumulative frozen point-in-time Panama offset, never prices used for fills. Each spread must be available before activation09:30. No close or volume history bridges2021--2024. Intraday raw active contract unchanged.',
    volume='Aligned5minute RTH bars. G1 compares completed trigger volume with exactly20 preceding completed5m RTH bars, carried across sessions but cleared by missing/invalid blocks; exclude trigger itself. G2 compares climax with arithmetic mean of all earlier completed5m RTH bars of that session, exclude climax and confirmation; no time-of-day normalization added.',
    G1='Long only, prior close>SMA20. Completed reversal confirms at09:45..14:30 inclusive; next minute open. Pullback>=0.50 priorATR already established before reversal block, after most recent running-high minute (its own low cannot prove ordering). Reversal close>open and>previous5mhigh and volume>1.5reference. Stop=min(pullback/reversal low-1tick,entry-0.35ATR rounded outward). Three fixed exits:15:55open; RTHhigh frozen at signal; entry+1.0priorATR. No dynamic hindsight high.',
    G2='ONL and first-hour-low tested separately, each unfiltered and prior bull only. ONL requires existing930minute context. First-hour-low unavailable until10:30. Climax breaks below level from prior5mclose>=level and volume>2.0prior-session-block mean; immediately next5mclose>level; entry next open, confirmation boundary<=14:00. Stop=climaxlow-1tick; a gap making stop>=entry is invalid, not silently repaired. Three exits:causal RTHVWAP,entry+0.75priorATR,15:55open. Max one first signal per variant/day, no later reentry after invalid stop.',
    VWAP='RTH09:30 anchored cumulative HLC3*volume/volume, no overnight. At minute i target uses only minutes<i, rounds up to tick, becomes a resting limit; updated next minute only. If at/below entry it is immediately marketable:zero gross and full fee, not an extra profitability filter.',
    G3='Strong full RTH:close location>=0.85,range>0.85priorATR,close>terminalSMA20. Requested15:59close->next actual cash-session09:30open or10:00open are explicitly nonexecutable close-anchor references. Also report causal first16:00open entries for same two endpoints. Do not claim exact close fill after observing final bar. These4rows have no stop. Signal day must be in pool; next cash endpoint and same active contract required; never jump to next eligible day or bridge2021--2024.',
    G3_DIP='Previous actual cash session strong day must be in pool, current day must also be in1151pool. Resting buy limit=09:30open-0.25current priorATR rounded down, first fill09:30..11:59; cancel12:00; flat15:55open. No extra stop/target was specified, none added. Gap limit fills conservatively at limit, no favorable improvement.',
    execution='All long,1NQ,at most1trade/model/day. $24.50RT=1.225pt once per fill. No reoptimization/extra costs. Stops at adverse open if gapped; otherwise stop priority in unresolved intrabar conflicts. Resting limits/targets require1tick trade-through. Entry-bar target only if entry established at open or close beyond target proves later crossing. Targets marketable at later open precede later intrabar stop. No arbitrary max-loss cap.',
    overnight_quality='Require known endpoints and same active contract. Retain raw observed intermediate prices without zero filling; report missing scheduled holding minutes and gaps separately. Overnight DD is observed-mark DD, not a guaranteed worst-tick bound. No trading/margin claim.',
    metrics='N trades; winrate andPF on net tradePnL; DD on chronological observed minute opens/closes plus known exitfills, fee charged atentry. Quarterly attribution by entry day, positive/quarters with trades. Combined and both blocks mandatory, even zero cells. All20 variants descriptive, no confirmatory p-value or independent-validation claim.',
    publication='Local append-only report/JSON/private ledgers. No Git commit/push/deploy requested. Preserve earlier research including uncommitted asymmetric-regime files byte-identically.')


def verify():
    prior.verify()
    lock = json.loads(LOCK.read_text())
    if lock['method'] != METHOD:
        raise ValueError('Method changed after registration')
    for name, digest in lock['files'].items():
        if h.sha(ROOT/name) != digest:
            raise ValueError('Protected bytes changed: '+name)
    if PROOF.exists():
        for name, digest in json.loads(PROOF.read_text())['files'].items():
            if h.sha(ROOT/name) != digest:
                raise ValueError('Output changed: '+name)
    return dict(status='FROZEN_INPUTS_AND_PRIOR_REPORTS_UNCHANGED', protected=len(lock['files']))


def register():
    if LOCK.exists():
        return verify()
    prior.verify()
    names = subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    files = {n:h.sha(ROOT/n) for n in names if n and (ROOT/n).is_file()}
    h.dump(LOCK, dict(method=METHOD,files=files,models=list(c.MODELS),
                     anchor_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()))
    return dict(status='ALL20_VARIANTS_RECORDED_BEFORE_OUTCOMES', protected=len(files))


def daily_features(active, days, calendar, rolls):
    """Sequential daily and volume history, no cross-block forward fill."""
    groups = dict(tuple(active.groupby('trade_date')))
    closes, volumes, result = [], [], {}
    for day in days:
        offset = 0.
        for roll in rolls:
            if roll['session'] <= day:
                if pd.Timestamp(roll['spread_available_utc']) > h.at(day,'09:30'):
                    raise ValueError('Future rollover spread')
                offset += roll['spread_points']
        ready = len(closes)>=20 and all(np.isfinite(closes[-20:]))
        before = float(np.mean(closes[-20:])+offset) if ready else np.nan
        yesterday = closes[-1]+offset if closes and np.isfinite(closes[-1]) else np.nan
        rec = dict(sma_prior=before, prior_daily_close=yesterday,
                   bull=bool(yesterday>before) if ready else None, prior_volumes=list(volumes[-20:]))
        g = groups.get(day, active.iloc[:0])
        grid = calendar.grid(day)
        ix = grid[(grid>=h.at(day,'09:30')) & (grid<h.at(day,'16:00'))]
        rth = g.reindex(ix)
        valid = len(ix)>0 and rth[list(c.FIELDS)].notna().all().all()
        raw_close = float(rth.close.iloc[-1]) if valid else np.nan
        rec['sma_today'] = (float(np.mean(closes[-19:]+[raw_close-offset])+offset)
                            if valid and len(closes)>=19 and all(np.isfinite(closes[-19:])) else np.nan)
        result[day] = rec
        closes.append(raw_close-offset)
        # Block gaps clear volume history; do not reinterpret missing prints as0.
        fullix = pd.date_range(h.at(day,'09:30'),h.at(day,'16:00'),freq='min',inclusive='left')
        for j in range(0,len(ix),5):
            chunk=rth.iloc[j:j+5]
            if len(chunk)==5 and chunk[list(c.FIELDS)].notna().all().all():
                volumes.append(float(chunk.volume.sum()));volumes=volumes[-20:]
            else:
                volumes=[]
        if len(ix)==0 or (len(ix)==390 and not ix.equals(fullix)):
            volumes=[]
    return result


def inputs():
    old, masks, _, oldsource, _, active_old = historical.inputs()
    recent, _, included, recsource, active_recent, rec_calendar, rec_rolls = load_inputs()
    old_calendar = calv2.CalendarV2()
    old_rolls=json.loads((calv2.OUT/'fixed-spreads.json').read_text())
    datasets={}
    for name, state, selected, active, calendar, rolls in (
        ('2019_2021',old,masks['PRIMARY_STRICT'],active_old,old_calendar,old_rolls),
        ('2024_2026',recent,included,active_recent,rec_calendar,rec_rolls)):
        dates=[d for d in selected if np.isfinite(state[d][1]['atr']) and state[d][1]['atr']>0]
        start,end=str(active.trade_date.min()),str(active.trade_date.max())
        cash=h.cash_dates(start,end)
        context=daily_features(active,cash,calendar,rolls)
        datasets[name]=dict(state=state,dates=dates,active=active,cash=cash,calendar=calendar,features=context)
    if [len(datasets[k]['dates']) for k in BLOCKS[1:]] != [733,418]:
        raise ValueError('1151-session sample changed')
    return datasets,dict(historical=oldsource,recent=recsource)


def attach(trade, day, block, model, path):
    return dict(trade,day=day,quarter=str(pd.Period(day,freq='Q')),block=block,model=model,marks=path)


def overnight(data, day, nextday, reference, end_clock):
    active=data['active'];groups=data['groups'];g=groups.get(day);ng=groups.get(nextday)
    if g is None or ng is None:
        return None,'MISSING_NEXT_SESSION'
    if len(set(g.contract))!=1 or len(set(ng.contract))!=1 or g.contract.iloc[0]!=ng.contract.iloc[0]:
        return None,'CONTRACT_SWITCH'
    start,end=h.at(day,'16:00'),h.at(nextday,end_clock)
    rows=active.loc[(active.index>=start)&(active.index<=end)]
    if end not in rows.index or (not reference and start not in rows.index):
        return None,'MISSING_ENDPOINT'
    if 'usable' in rows and not rows.usable.all():
        return None,'INVALID_HOLDING_BAR'
    entry=float(data['state'][day][0]['close'][-1]) if reference else float(rows.loc[start,'open'])
    exit_=float(rows.loc[end,'open'])
    path=[-c.FEE]
    for time,row in rows.iterrows():
        path.append(float(row.open)-entry-c.FEE)
        if time<end:
            path.append(float(row.close)-entry-c.FEE)
    scheduled=[]
    for d in pd.bdate_range(day,nextday).strftime('%Y-%m-%d'):
        scheduled.extend(data['calendar'].grid(d))
    expected=pd.DatetimeIndex(scheduled)
    expected=expected[(expected>=start)&(expected<end)]
    missing=len(expected.difference(rows.index))
    return dict(entry_price=entry,exit_price=exit_,entry_clock='CLOSE_REFERENCE' if reference else '16:00',
                exit_day=nextday,exit_clock=end_clock,reason='TIME_NEXT_SESSION',
                gross_points=exit_-entry,net_points=exit_-entry-c.FEE,
                missing_holding_minutes=missing,marks=path),'FILLED'


def describe(ledger):
    ledger=sorted(ledger,key=lambda t:t['day'])
    gross=np.array([t['gross_points'] for t in ledger]);net=gross-c.FEE
    equity=peak=dd=0.
    for t in ledger:
        values=np.asarray(t['marks'])+equity
        peaks=np.maximum.accumulate(np.r_[peak,values])[1:]
        dd=max(dd,float(max(peaks-values)))
        peak=max(peak,float(max(values)));equity+=t['net_points']
        np.testing.assert_allclose(values[-1],equity,rtol=0,atol=1e-7)
    quarters=[]
    for q in sorted({t['quarter'] for t in ledger}):
        x=[t for t in ledger if t['quarter']==q]
        quarters.append(dict(quarter=q,N=len(x),gross_points=sum(t['gross_points'] for t in x),net_points=sum(t['net_points'] for t in x)))
    return dict(N=len(ledger),gross_points=float(gross.sum()),net_points=float(net.sum()),
                winrate=float(np.mean(net>0)) if len(net) else None,
                profit_factor=float(sum(net[net>0])/-sum(net[net<0])) if (net<0).any() else None,
                max_marked_drawdown=dd,positive_quarters=sum(q['net_points']>0 for q in quarters),
                traded_quarters=len(quarters),quarterly=quarters,
                trades_with_missing_holding_minutes=sum(t.get('missing_holding_minutes',0)>0 for t in ledger),
                missing_holding_minutes=sum(t.get('missing_holding_minutes',0) for t in ledger))


def report(result):
    lines=['# Prijs- en volumemechanismen: ontwikkelingsverkenning','',result['status'],'',
           '1151 sessies:733 historisch,418 recent. Alle20 varianten; geen onafhankelijke bevestiging. REF-rijen zijn niet-uitvoerbare slotankers. N=trades,1NQ,$24.50RT. DD=waargenomen minuut-open/close plus exitfills.','']
    for block in BLOCKS:
        lines += [f'## {block}','', '| Variant | N | Bruto pt | Netto pt | Winrate | PF | Max DD pt | Positieve kwartalen |',
                  '|---|---:|---:|---:|---:|---:|---:|---:|']
        for m,x in result['performance'][block].items():
            win=f"{x['winrate']:.2%}" if x['winrate'] is not None else 'n/a'
            pf=f"{x['profit_factor']:.3f}" if x['profit_factor'] is not None else 'n/a'
            lines.append(f"| {m} | {x['N']} | {x['gross_points']:.3f} | {x['net_points']:.3f} | {win} | {pf} | {x['max_marked_drawdown']:.3f} | {x['positive_quarters']}/{x['traded_quarters']} |")
    lines+=['','## Beschikbaarheid','', '```json',json.dumps(result['availability'],indent=2),'```','',
            '## Vastgelegde definities','']+[f'- {k}: {v}' for k,v in METHOD.items()]
    lines+=['','## Volledige kwartaalverdeling','', '| Blok | Variant | Kwartaal | N | Netto pt |','|---|---|---|---:|---:|']
    for b in BLOCKS:
        for m,x in result['performance'][b].items():
            lines += [f"| {b} | {m} | {q['quarter']} | {q['N']} | {q['net_points']:.3f} |" for q in x['quarterly']]
    return '\n'.join(lines)+'\n'


def run(directory):
    verify();directory.mkdir(parents=True,exist_ok=True)
    datasets,sources=inputs();ledgers={m:[] for m in c.MODELS};availability={};prefix_checks=0
    for block,data in datasets.items():
        state,dates=data['state'],data['dates'];eligible=set(dates)
        data['groups']=dict(tuple(data['active'].groupby('trade_date')))
        nextcash=dict(zip(data['cash'][:-1],data['cash'][1:]))
        counts=dict(sessions=len(dates),bull_ready=0,bull_days=0,strong_days=0,ONL_ready=0,
                    volume20_ready_at0945=0,status_counts={})
        def status(model,code):
            key=model+':'+code;counts['status_counts'][key]=counts['status_counts'].get(key,0)+1
        strong={}
        for day in dates:
            p,base=state[day];ctx=dict(base,**data['features'][day])
            counts['bull_ready']+=ctx['bull'] is not None;counts['bull_days']+=ctx['bull'] is True
            counts['ONL_ready']+=bool(np.isfinite(ctx['ONL']))
            counts['volume20_ready_at0945']+=len(ctx['prior_volumes'])>=18
            ev1=c.select_g1(p,ctx,ctx['prior_volumes'])
            events={m:ev1 for m in c.G1}
            for level in ('ONL','H1'):
                for bull in (False,True):
                    ev=c.select_g2(p,ctx,level,bull)
                    for target in ('VWAP','ATR','TIME'):
                        events[f'G2_{level}_{"BULL" if bull else "ALL"}_{target}']=ev
            # Real-data future truncation: only selectors, never future fills.
            for m,ev in events.items():
                if ev is None:continue
                k=ev['boundary'];prefix={key:values[:k] for key,values in p.items()}
                check=(c.select_g1(prefix,ctx,ctx['prior_volumes']) if m in c.G1 else
                       c.select_g2(prefix,ctx,m.split('_')[1],m.split('_')[2]=='BULL'))
                if check!=ev:raise AssertionError('Future-sensitive event '+day+' '+m)
                prefix_checks+=1
            for model,ev in events.items():
                trade,code=c.execute(p,ctx,model,ev);status(model,code)
                if trade:
                    ledgers[model].append(attach(trade,day,block,model,c.marks(trade,p)))
            strong[day]=c.strong_day(p,ctx)
        counts['strong_days']=sum(strong.values())
        for day in dates:
            if not strong[day]:continue
            nextday=nextcash.get(day)
            for model in c.G3[:4]:
                if nextday is None:
                    status(model,'NO_NEXT_CASH_SESSION');continue
                reference=model.endswith('_REF');end='10:00' if '1000' in model else '09:30'
                trade,code=overnight(data,day,nextday,reference,end);status(model,code)
                if trade:
                    path=trade.pop('marks');ledgers[model].append(attach(trade,day,block,model,path))
            if nextday not in eligible:
                status('G3_DIP_TIME','NEXT_SESSION_OUTSIDE_POOL');continue
            p,base=state[nextday];ctx=dict(base,**data['features'][nextday])
            # Same frozen rule as overnight: no synthetic roll-gap exposure.
            if data['groups'][day].contract.iloc[0]!=data['groups'][nextday].contract.iloc[0]:
                status('G3_DIP_TIME','CONTRACT_SWITCH');continue
            trade,code=c.dip_entry(p,ctx);status('G3_DIP_TIME',code)
            if trade:
                trade['signal_day']=day
                ledgers['G3_DIP_TIME'].append(attach(trade,nextday,block,'G3_DIP_TIME',c.marks(trade,p)))
        availability[block]=counts
    performance={b:{m:describe([t for t in rows if b=='COMBINED' or t['block']==b])
                    for m,rows in ledgers.items()} for b in BLOCKS}
    for m in c.MODELS:
        for key in ('N','gross_points','net_points'):
            np.testing.assert_allclose(performance['COMBINED'][m][key],sum(performance[b][m][key] for b in BLOCKS[1:]),rtol=0,atol=1e-7)
    result=dict(status='EXPLORATORY_DEVELOPMENT_NOT_INDEPENDENT_VALIDATION',sessions=1151,
                method=METHOD,source_verification=sources,availability=availability,
                performance=performance,future_truncation_checks=prefix_checks,method_sha256=h.sha(LOCK))
    h.dump(directory/'summary.json',result)
    for m,rows in ledgers.items():h.dump(directory/(m+'-trades.json'),rows)
    (directory/'report.md').write_text(report(result))
    verify()
    return result


def replay():
    if PROOF.exists():return verify()
    result=run(OUT/'run1');print('All fixed variants complete; independently replaying source CSVs',flush=True)
    run(OUT/'run2')
    hashes=lambda folder:{p.name:h.sha(p) for p in folder.iterdir() if p.is_file()}
    first,second=hashes(OUT/'run1'),hashes(OUT/'run2')
    if first!=second:raise AssertionError('Replay differs')
    h.dump(RESULT,result);REPORT.write_bytes((OUT/'run1/report.md').read_bytes())
    paths=[RESULT,REPORT]+[folder/name for folder in (OUT/'run1',OUT/'run2') for name in first]
    h.dump(PROOF,dict(status='BYTE_IDENTICAL_TWO_SOURCE_REPLAYS',files={str(p.relative_to(ROOT)):h.sha(p) for p in paths}))
    return dict(status='COMPLETE',variants=len(c.MODELS),sessions=1151,future_truncation_checks=result['future_truncation_checks'])


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('register','replay','verify'))
    print(json.dumps(globals()[parser.parse_args().action](),indent=2))
