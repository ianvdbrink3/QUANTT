"""Fixed anti-whipsaw and portfolio study. Frozen empirical inputs are read-only."""
import csv
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from portfolio_agent.signal_engine import features
from portfolio_agent.regime import trend_states, classify, sleeve_targets, WEIGHTS
from portfolio_agent.calendars import early_close, is_session
from scripts.etf_empirical.data import daily, minutes
from scripts.etf_empirical.core import holding, at
from scripts.own_account.core import metrics

ROOT=Path(__file__).resolve().parents[1]
PERIODS={'CONTINUOUS':('2019-01-14','2026-09-30'),'2022':('2022-01-03','2022-12-30')}
OUT=ROOT/'artifacts/portfolio_agent/study'


def write_csv(path, rows):
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)


def holm(values):
    order=np.argsort(values,kind='stable');out=np.empty(len(values));last=0.
    for rank,i in enumerate(order):
        last=max(last,min(1.,float(values[i])*(len(values)-rank)));out[i]=last
    return out.tolist()


def block_test(values, dates, seed=200, reps=4096):
    """Calendar-month cluster bootstrap, centered two-sided mean test."""
    groups={}
    for d,x in zip(dates,values,strict=True):groups.setdefault(d[:7],[]).append(float(x))
    sums=np.array([sum(v) for v in groups.values()]);counts=np.array([len(v) for v in groups.values()])
    mean=float(np.mean(values));rng=np.random.default_rng(seed)
    ix=rng.integers(0,len(sums),(reps,len(sums)))
    boot=sums[ix].sum(axis=1)/counts[ix].sum(axis=1)
    p=(1+int(np.count_nonzero(np.abs(boot-mean)>=abs(mean))))/(reps+1)
    return dict(mean_daily_net=float(mean),ci95_low=float(np.quantile(boot,.025)),
                ci95_high=float(np.quantile(boot,.975)),p_raw=float(p),bootstrap_months=len(sums))


def pack(run, **labels):
    s=run['summary']
    return dict(**labels,N=s.get('N'),orders=s.get('orders'),
        switches=s.get('switches'),
        costs_account_units=s.get('total_model_costs'),CAGR_pct=s.get('annualized_growth_pct'),
        total_return_pct=s.get('total_return_pct'),max_DD_pct=s.get('closed_cycle_MDD_pct'),
        Sharpe=s.get('Sharpe'),Sortino=s.get('Sortino'),TUW_sessions=s.get('max_TUW_sessions'),
        TUW_calendar_days=s.get('max_TUW_calendar_days'))


def target_hold(frame, days, targets, bp):
    """Previous close fractional target, next open; trade only target changes.

    Monthly rebalance and daily exposure cap trim are charged, never free.
    """
    cash=1000.;q=0.;last=1000.;fees=0.;orders=0;entries=0;rets=[];previous_target=None
    index=list(frame.index)
    for i,d in enumerate(days):
        prev=index[index.index(d)-1];op=float(frame.at[d,'open']);cl=float(frame.at[d,'close'])
        cash+=q*float(frame.at[d,'distribution']);nav=cash+q*op
        target=float(targets.loc[prev]);month_start=i==0 or days[i-1][:7]!=d[:7]
        wanted=target*nav/op
        if previous_target!=target or month_start or q*op>target*nav+1e-8:
            delta=wanted-q;fee=abs(delta)*op*bp/20000.
            if delta>0:delta=min(delta,max(0.,cash/(op*(1+bp/20000.))))
            fee=abs(delta)*op*bp/20000.;cash-=delta*op+fee;q+=delta
            if abs(delta)>1e-9:orders+=1;fees+=fee;entries+=int(delta>0)
        previous_target=target
        if i==len(days)-1 and q:
            fee=q*cl*bp/20000.;cash+=q*cl-fee;q=0.;fees+=fee;orders+=1
        nav=cash+q*cl;rets.append(nav/last-1);last=nav
    prev_index={b:a for a,b in zip(index,index[1:])}
    scheduled=[float(targets.loc[prev_index[d]]) for d in days]
    switches=sum(a!=b for a,b in zip(scheduled,scheduled[1:]))
    return dict(summary=dict(**metrics(rets,days),N=entries,orders=orders,total_model_costs=fees,switches=switches),daily_returns=rets)


def portfolio(frames, fs, days, profile, bp, paths, s1_enabled=True):
    """Daily-mark development model, separate sleeves, monthly paid rebalance.

    Missing S1 anchors or stop paths never become fabricated zero returns:
    the reported full-strategy result is censored if any required path is unknown.
    """
    w=WEIGHTS[profile];weights=np.array(w[:3]);cash=np.array(weights*990.);permanent=10.+w[3]*990.
    q=np.zeros(2);last=1000.;fees=0.;orders=0;entries=0;ret=[];missing=0;unknown=0;prior_targets=None
    pending=None;all_days=list(frames['QQQ'].index);switches=0
    for i,d in enumerate(days):
        j=all_days.index(d);prev=all_days[j-1]
        op=np.array([frames[s].at[d,'open'] for s in ('QQQ','TQQQ')],float)
        cl=np.array([frames[s].at[d,'close'] for s in ('QQQ','TQQQ')],float)
        cash[:2]+=q*np.array([frames[s].at[d,'distribution'] for s in ('QQQ','TQQQ')],float)
        # Overnight liquidation is observed at <=09:31. Its sleeve stays separate.
        if pending is not None:
            cash[2]+=pending['proceeds'];pending=None
        nav=permanent+float(cash.sum()+np.dot(q,op))
        state=classify(float(frames['QQQ'].at[prev,'close']),fs['QQQ'].loc[prev])
        t=bool(frames['TQQQ'].at[prev,'close']>fs['TQQQ'].at[prev,'SMA200'])
        known=pd.notna(fs['QQQ'].at[prev,'HIGH_VOL'])
        targets=np.array(sleeve_targets(state,t,known)[:2])
        month=i==0 or days[i-1][:7]!=d[:7]
        # Rebalance actual sleeve wealth monthly; trades at the next open pay costs.
        budgets=weights*(nav-max(10.,.01*nav)) if month else np.r_[cash[:2]+q*op,cash[2]]
        wanted=budgets[:2]*targets/op
        caps=np.array([weights[0],weights[1]])*(nav-max(10.,.01*nav))/op
        trim=q>caps+1e-9
        change=np.ones(2,dtype=bool) if prior_targets is None else targets!=prior_targets
        if prior_targets is not None:switches+=int(np.count_nonzero(change))
        desired=np.where(change|month|trim,np.minimum(wanted,caps),q)
        # Sell before buys; no leverage or cross-sleeve double-spending.
        for k in range(2):
            delta=min(0.,desired[k]-q[k]);fee=-delta*op[k]*bp/20000.
            cash[k]-=delta*op[k]+fee;q[k]+=delta;fees+=fee;orders+=int(delta< -1e-9)
        if month:
            free=permanent+float(cash.sum());need=np.maximum(0.,budgets-np.r_[q*op,0.])
            factor=min(1.,free/need.sum()) if need.sum() else 0.
            cash=need*factor;permanent=free-float(cash.sum())
        for k in range(2):
            delta=max(0.,desired[k]-q[k]);delta=min(delta,max(0.,cash[k]/(op[k]*(1+bp/20000.))))
            fee=delta*op[k]*bp/20000.;cash[k]-=delta*op[k]+fee;q[k]+=delta;fees+=fee
            orders+=int(delta>1e-9);entries+=int(delta>1e-9)
        prior_targets=targets
        current_state=classify(float(frames['QQQ'].at[d,'close']),fs['QQQ'].loc[d])
        if s1_enabled and weights[2]>0 and current_state.value==2 and bool(fs['QQQ'].at[d,'S1']) and not early_close(d) and i<len(days)-1:
            path=paths.get(d)
            if path is None:missing+=1
            else:
                unknown+=int(not path['stop_data_complete'])
                entry=path['entry'];stop=path['stop_price'];distance=entry-stop
                nav_close=permanent+float(cash.sum()+np.dot(q,cl))
                units=min(cash[2]/(entry*(1+bp/20000.)),.005*nav_close/(distance+entry*bp/10000.))
                buyfee=units*entry*bp/20000.;sellfee=units*path['exit']*bp/20000.
                cash[2]-=units*entry+buyfee
                # Mark overnight at entry today; actual observed exit accounted tomorrow.
                pending=dict(mark=units*entry,proceeds=units*(path['exit']+path.get('distribution',0.))-sellfee)
                fees+=buyfee+sellfee;orders+=2;entries+=1;switches+=2
        if i==len(days)-1:
            for k in range(2):
                fee=q[k]*cl[k]*bp/20000.;cash[k]+=q[k]*cl[k]-fee;fees+=fee;orders+=int(q[k]>0);q[k]=0.
        nav=permanent+float(cash.sum()+np.dot(q,cl))+(pending['mark'] if pending else 0.)
        if nav<=0 or (cash< -1e-7).any():raise ValueError('RESEARCH_CASH_INVARIANT')
        ret.append(nav/last-1);last=nav
    return dict(summary=dict(**metrics(ret,days),N=entries,orders=orders,total_model_costs=fees,switches=switches),
                daily_returns=ret,missing_s1_anchors=missing,unknown_s1_stop_paths=unknown)


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    protocol=dict(status='DEVELOPMENT_ONLY_FIXED_MATRIX',variants=['naked','schmitt','confirm2'],costs=[2,5,10],
        periods=PERIODS,primary_test='Two-sided mean daily net return vs zero; monthly cluster bootstrap4096; Holm6 separately continuous and2022 at2bp; sensitivities reuse primary labels',
        portfolio='Monthly paid rebalance,1percent/min10cash reserve,.5percentNAV S1 plannedstop risk; gated state machine. Missing S1anchors or stop paths censor full-strategy metrics; separate S1_OFF executable design.')
    protocolpath=ROOT/'research/portfolio-agent-study-protocol-2026-10-30.json'
    if protocolpath.exists():assert json.loads(protocolpath.read_text())==json.loads(json.dumps(protocol))
    else:protocolpath.write_text(json.dumps(protocol,indent=2)+'\n')
    frames,quality,splits=daily();fs={s:features(frames[s]) for s in ('QQQ','TQQQ')}
    private=json.loads(gzip.decompress((ROOT/'artifacts/etf-empirical/private-ledgers-and-daily-panels.json.gz').read_bytes()))
    paths={}
    for period in ('2019_2021','2025_2026','CRASH_2022'):
        for p in private['ledgers'][f'{period}|TQQQ:MIN_S1:LATENCY:ETF_ATR050:2bp']:paths[p['day']]=p
    rows=[];panels={};tests=[];timing_events=[];parity=[]
    for period,(a,b) in PERIODS.items():
        days=list(frames['QQQ'].loc[a:b].index)
        for symbol in ('QQQ','TQQQ'):
            for variant in ('naked','schmitt','confirm2'):
                flags=pd.Series(trend_states(frames[symbol].close,fs[symbol].SMA200,variant),index=frames[symbol].index)
                f=pd.DataFrame({'RULE':flags},index=flags.index)
                for bp in (2,5,10):
                    value=holding(frames[symbol],f,days,'RULE',bp)
                    row=pack(value,period=period,asset=symbol,model=variant,RT_bp=bp,status='DAILY_NEXT_OPEN_DEVELOPMENT')
                    row['switches']=sum(flags.loc[days].astype(int).diff().fillna(0).abs())
                    rows.append(row);panels[(period,symbol,variant,bp)]=value['daily_returns']
                    if bp==2:
                        t=block_test(value['daily_returns'],days);tests.append(dict(period=period,asset=symbol,model=variant,**t))
                    if variant=='naked' and bp==2:
                        original=holding(frames[symbol],pd.DataFrame({'TREND200':flags}),days,'TREND200',bp)
                        assert value==original
                        frozen=next(r for r in json.loads((ROOT/'research/etf-empirical-results-2026-10-29.json').read_text())['results'] if r['asset']==symbol and r['model']=='TREND200' and r['period']==('CRASH_2022' if period=='2022' else 'CONTINUOUS_2019_2026') and r['RT_bp']==bp)
                        assert abs(value['summary']['annualized_growth_pct']-frozen['annualized_growth_pct'])<1e-10
                        parity.append(dict(period=period,asset=symbol,CAGR_exact=True))
                if period=='CONTINUOUS':
                    all_dates=list(frames[symbol].index);was=False
                    for d in days:
                        j=all_dates.index(d);desired=bool(flags.iloc[j-1])
                        if desired!=was:timing_events.append(dict(asset=symbol,variant=variant,day=d,side='BUY' if desired else 'SELL',daily_open=float(frames[symbol].at[d,'open'])))
                        was=desired
        states=[classify(float(frames['QQQ'].at[d,'close']),fs['QQQ'].loc[d]) for d in frames['QQQ'].index]
        for symbol,k in (('QQQ',0),('TQQQ',1)):
            targets=pd.Series([sleeve_targets(state, bool(frames['TQQQ'].at[d,'close']>fs['TQQQ'].at[d,'SMA200']),pd.notna(fs['QQQ'].at[d,'HIGH_VOL']))[k] for d,state in zip(frames['QQQ'].index,states)],index=frames['QQQ'].index)
            for bp in (2,5,10):rows.append(pack(target_hold(frames[symbol],days,targets,bp),period=period,asset=symbol,model='GATED',RT_bp=bp,status='NEW_STATE_MACHINE_DEVELOPMENT'))
        for profile in WEIGHTS:
            for enabled in (True,False):
                if profile=='offensive' and not enabled:continue
                for bp in (2,5,10):
                    value=portfolio(frames,fs,days,profile,bp,paths,enabled)
                    unknown=value['missing_s1_anchors']+value['unknown_s1_stop_paths']
                    row=pack(value,period=period,asset='PORTFOLIO',model=profile+('' if enabled else '_S1_OFF'),RT_bp=bp,
                        status='CENSORED_UNKNOWN_S1_PATHS' if unknown else 'DAILY_MARK_DEVELOPMENT')
                    row.update(missing_s1_anchors=value['missing_s1_anchors'],unknown_s1_stop_paths=value['unknown_s1_stop_paths'])
                    if unknown:
                        row.update({f'observed_only_{k}':row[k] for k in ('CAGR_pct','total_return_pct','max_DD_pct','Sharpe','Sortino','costs_account_units','N','orders','switches')})
                    if unknown:
                        for key in ('CAGR_pct','total_return_pct','max_DD_pct','Sharpe','Sortino','TUW_sessions','TUW_calendar_days','costs_account_units','N','orders','switches'):row[key]=None
                    rows.append(row)
    for period in PERIODS:
        family=[r for r in tests if r['period']==period]
        corrected=holm([r['p_raw'] for r in family])
        for r,p in zip(family,corrected):r['p_Holm6']=p
    for r in rows:
        match=next((t for t in tests if t['period']==r['period'] and t['asset']==r['asset'] and t['model']==r['model']),None)
        if match:r.update({k:match[k] for k in ('p_raw','p_Holm6','ci95_low','ci95_high')},test_RT_bp=2)
    print('Daily matrix complete; loading verified minute anchors',flush=True)
    mins,minaudit=minutes();timing=[]
    for e in timing_events:
        t=at(e['day'],'09:31');frame=mins[e['asset']]
        ok=t in frame.index and frame.at[t,'volume']>0
        price=float(frame.at[t,'open']) if ok else None
        timing.append(dict(e,minute_open=price,status='MATCHED' if ok else 'MISSING_EXACT_0931',
            difference_points=price-e['daily_open'] if ok else None,
            adverse_bp=(1 if e['side']=='BUY' else -1)*(price/e['daily_open']-1)*10000 if ok else None))
    write_csv(ROOT/'research/ANTI_WHIPSAW_RESULTS_2026-10-30.csv',rows)
    write_csv(ROOT/'research/ANTI_WHIPSAW_TIMING_2026-10-30.csv',timing)
    output=dict(protocol=protocol,rows=rows,tests=tests,timing=timing,baseline_parity=parity,minute_quality=minaudit)
    (OUT/'results.json').write_text(json.dumps(output,indent=2,allow_nan=False))
    lines=['# Anti-whipsaw en portefeuilleonderzoek — 30 oktober 2026','',
        '**Ontwikkelingsonderzoek; geen onafhankelijk bewijs en geen echte brokerfills.**',
        'De volledige matrix staat in [CSV](../research/ANTI_WHIPSAW_RESULTS_2026-10-30.csv). Kosten zijn accountunits vanaf 1.000, niet omgerekende eurofees. Cashrente/FX nul. Terminale liquidatie is een expliciete testgrens.',
        '', '## Vaste zes modellen: 2 bp RT', '',
        '| Periode | ETF | Regel | Wissels | Orders | Kosten | CAGR % | DD % | Sharpe | Sortino | TUW sessies | Totaal % | Holm6 p |',
        '| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    def fmt(x):return 'ONBEKEND' if x is None else f'{x:.4f}' if isinstance(x,float) else str(x)
    for r in rows:
        if r['asset']!='PORTFOLIO' and r['model']!='GATED' and r['RT_bp']==2:
            lines.append('| '+' | '.join(fmt(r.get(k)) for k in ('period','asset','model','switches','orders','costs_account_units','CAGR_pct','max_DD_pct','Sharpe','Sortino','TUW_sessions','total_return_pct','p_Holm6'))+' |')
    lines+=['','De zes tweezijdige toetsen betreffen het gemiddelde dagelijkse netto rendement versus nul, kalendermaand-clusterbootstrap (4.096 trekkingen). Holm6 afzonderlijk voor continu en 2022 bij 2 bp. Dit toetst **niet** of een buffer beter is dan de naakte lijn; significante marktgroei is geen bewijs van incrementele filterwaarde. 5/10 bp zijn vaste gevoeligheden; de CSV herhaalt hun 2bp-toetslabel, zonder extra verborgen familie. Alle zes resultaten worden getoond.','',
        'Wissels tellen signaalomslagen binnen het venster; orders omvatten instap, eindgrens en herbelegging van uitkeringen. De drie varianten hebben identieke volgende-open uitvoering en opwarming. Vier baseline-reproducties sluiten exact aan op de bevroren QQQ/TQQQ-TREND200-CAGR.','',
        '## Gated engine en ontwerpportefeuilles, alle kosten', '',
        '| Periode | Model | ETF | RT bp | N | Kosten | CAGR % | DD % | Sharpe | Sortino | TUW | Totaal % | Status |',
        '| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |']
    for r in rows:
        if r['asset']=='PORTFOLIO' or r['model']=='GATED':
            lines.append('| '+' | '.join(fmt(r.get(k)) for k in ('period','model','asset','RT_bp','N','costs_account_units','CAGR_pct','max_DD_pct','Sharpe','Sortino','TUW_sessions','total_return_pct','status'))+' |')
    lines+=['','**S1-bewijsgat:** 2023–2024 heeft geen minuutdekking en veel geobserveerde overnight-stoppaden zijn incompleet. De volledige Defensief/Gebalanceerd-cijfers worden daarom gecensureerd als vereiste S1-paden onbekend zijn. Geen ontbrekende nacht wordt als bewezen nulrendement voorgesteld. De aparte S1_OFF-varianten houden die sleeve cash en zijn volledig door te rekenen; zij zijn een andere, veilig uitvoerbare ontwerpfase. Ook 2022 heeft onbekende stoppaden.','',
        'Nieuwe portfolio-replay: maandelijkse betaalde herweging, 1%/min10 reserve, S1 maximaal 0,5% NAV gepland stoprisico, halve 3x in Staat1, eigen TQQQ-SMA200 blijft vereist. Dagelijkse NAV is geen intraminuutrisico. Kostenplafond/circuit breakers van de operationele bot zijn afzonderlijke hardguards; de studie forceert de vaste 2/5/10bp-scenario’s en behandelt die niet als geobserveerde quotes. De CSV bevat target-wisselingen naast het echte aantal orders. Bij gecensureerde S1-modellen staan afzonderlijke observed_only-kolommen: uitsluitend beschikbare stoppaden, ontbrekende nachten cash. Dit is nadrukkelijk geen volledige-strategieperformance en mag niet voor promotie of rangschikking worden gebruikt.','',
        '## Timingcontrole: dezelfde kernwisselingen, beschikbare minuten','',
        '| ETF | Regel | Kernorders | Gematcht | Ontbreekt | Gem. adverse bp | Mediaan adverse bp |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for s in ('QQQ','TQQQ'):
        for v in ('naked','schmitt','confirm2'):
            a=[x for x in timing if x['asset']==s and x['variant']==v];b=[x['adverse_bp'] for x in a if x['adverse_bp'] is not None]
            lines.append(f'| {s} | {v} | {len(a)} | {len(b)} | {len(a)-len(b)} | {np.mean(b):.4f} | {np.median(b):.4f} |')
    lines+=['','Positief adverse bp betekent duurder kopen/goedkoper verkopen om09:31. Ontbrekende ankers blijven ontbrekend: geen vervangende eerste print. Dit is een gepaarde prijsvergelijking van echte kernwisselingen, geen volledig 09:31-CAGR over 2023–2024 zonder minuten. [Detailtabel](../research/ANTI_WHIPSAW_TIMING_2026-10-30.csv).','',
        '## Reproductie','', '`python -m scripts.portfolio_agent_study` schrijft alleen nieuwe aggregaten en lokale artefacten. Bestaande brondata en onderzoekscode worden niet gewijzigd. De volledige kostenmatrix bevat ook de 2022-resultaten. Geen parameter is na uitkomsten aangepast.']
    (ROOT/'docs/ANTI_WHIPSAW_AND_PORTFOLIO_STUDY_2026-10-30.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(dict(rows=len(rows),timing_events=len(timing),baseline_parity=len(parity))))


if __name__=='__main__':run()
