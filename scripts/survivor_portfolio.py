"""Fixed ATR sizing audit of consumed samples; never opens 2019-21 prices."""
import argparse
import csv
import json
import subprocess
from pathlib import Path
import numpy as np
from scripts.month_turn_audit import load_samples, curve_drawdown, dump
from scripts.edge_marathon.core import select, fill
from scripts.edge_marathon.features import calendar_context
from scripts.edge_marathon.stats import holm
from scripts.oos_preparation.adapter import sha

ROOT=Path(__file__).resolve().parents[1]
MODELS=('TOM_RTH','COMPRESSED_BREAK5','SWEEP_REV_1200')
VARIANTS=('NQ_ATR','MNQ_FRACTIONAL','MNQ_INTEGER')
BUDGET=1000.
MNQ_COST=6.5
PROTOCOL=ROOT/'research/three-survivors-protocol.json'
LOCK=ROOT/'research/three-survivors-lock.json'
RESULT=ROOT/'research/three-survivors-results.json'


def register():
    if LOCK.exists(): return verify()
    if PROTOCOL.exists(): raise ValueError('Partial protocol exists; inspect before proceeding')
    protocol=dict(id='THREE-SURVIVORS-ATR-PORTFOLIO-20261022', status='EXPLORATORY_CONSUMED_DATA_ONLY',
        models=list(MODELS), source_samples=['DISCOVERY','CONTINUOUS_2022_2024_UNVERIFIED'],
        rules='Original core.select/core.fill unchanged. TOM last cash day and first3; compression prior range<0.65 priorATR, first5m close breakout, next open to RTHclose; sweep exactly one overnight side in first30m,09:59backinside and reversal vsopen,10:00open to11:59close.',
        sizing=dict(atr='Prior-known ATR14 only; missing/nonpositive -> size0, counted explicitly, no price filling.',
            R='ATR scale, not stop-loss or maximum loss. netNQ_R=(gross_points-1.225)/ATR.',
            dollar_ATR_budget=BUDGET, MNQ_point_value=2., MNQ_RT_cost=MNQ_COST,
            MNQ_cost_basis='Provisional $4.50 RT commission/fees plus2ticks perleg ($2 total). Not actual broker quote. Never divide NQ fees by10.',
            standalone_qty='B/(2*ATR)', sleeve_qty='B/(3*2*ATR)',
            integer='floor before entry, may be0; no minimum1 and no forced budget increase.',
            portfolio='Exactly1/3 each, idle capital remains idle, no netting cost credits, no fitted weights.',
            MNQ_limit='NQ bar execution proxy only. Fractional contracts not tradeable; MNQ launched2019May6. No margin/capital claim.'),
        daily='All435/493 sessions, no-signal and missing-size days are0, dailyendpoint correlations; ATRready-only sensitivity separately.',
        risk='Closed-day cumulative drawdown plus minute-close marked drawdown; fullRT charged atentry; raw contract prices only; sqrt252 mean(dailyPnL_R)/sampleSD, not return on account capital.',
        inference=dict(reps=10000, seed=20261022301, block='2 consecutive calendar months, joint identical block indexes across ALL models and variants; pooled daily sums/counts.',
                       CI='Nominal95% percentile CI of meanR/day and Sharpe; totalCI=meanCI*originalN. Approximate centered-bootstrap two-sided p, not exact.',
                       family='8 exploratory NQ_ATR dailymean tests:3models+portfolio x2sources, Holm8. Not correction for all historical research; no promotion.'),
        future_data='No2019-21 outcome release; intake metadata allowed. Both existing datasets consumed and selected; older contract identity unverified.',
        references=['https://www.cmegroup.com/markets/equities/nasdaq/micro-e-mini-nasdaq-100.contractSpecs.html',
                    'https://www.cmegroup.com/articles/faqs/frequently-asked-questions-micro-e-mini-equity-index-futures.html'])
    dump(PROTOCOL,protocol,exclusive=True)
    names=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    # Mutable new intake progress is not a research freeze; original intake01 remains protected.
    protected={n:sha(ROOT/n) for n in names if n and (ROOT/n).is_file() and n not in ('research/afternoon-historical-intake-batch02.json',)}
    dump(LOCK,dict(protocol_sha256=sha(PROTOCOL), protected_files=protected),exclusive=True)
    return verify()


def verify():
    lock=json.loads(LOCK.read_text())
    for name,expected in lock['protected_files'].items():
        if sha(ROOT/name)!=expected: raise ValueError('Protected file changed: '+name)
    if sha(PROTOCOL)!=lock['protocol_sha256']: raise ValueError('Sizing protocol changed')
    return lock


def scaled(gross, atr, fraction=1., variant='NQ_ATR'):
    if not np.isfinite(atr) or atr<=0: return 0.,0.,0.
    if variant=='NQ_ATR': return fraction*(gross-1.225)/atr, fraction/atr, fraction*1.225/atr
    qty=fraction*BUDGET/(2*atr)
    if variant=='MNQ_INTEGER': qty=float(np.floor(qty))
    elif variant!='MNQ_FRACTIONAL': raise ValueError('Unregistered variant')
    fee=qty*MNQ_COST/BUDGET
    return qty*(2*gross-MNQ_COST)/BUDGET,qty,fee


def marked_curve(trades, prices, fractions, variant):
    """391 checkpoints: opening boundary, then390 closes. FullRT atentry."""
    path=np.zeros(391)
    for trade,fraction in zip(trades,fractions):
        a,b=trade['entry'],trade['end']; atr=trade['atr']
        if atr is None or atr<=0: continue
        _,qty,fee=scaled(0.,atr,fraction,variant)
        multiplier=qty if variant=='NQ_ATR' else qty*2/BUDGET
        path[a:]-=fee
        moves=trade['direction']*(np.asarray(prices['close'][a:b])-trade['entry_price'])*multiplier
        path[a+1:b+1]+=moves
        path[b+1:]+=moves[-1]
    return path


def statistics(values, marked):
    values=np.asarray(values,float);sd=values.std(ddof=1)
    eq=np.r_[0.,np.cumsum(values)]; losses=-values[values<0].sum()
    return dict(total_R=float(values.sum()),mean_R_per_day=float(values.mean()),median_R_per_day=float(np.median(values)),
        sharpe_daily_annualized=float(np.sqrt(252)*values.mean()/sd) if sd>0 else None,
        daily_close_drawdown_R=curve_drawdown(values), minute_close_drawdown_R=curve_drawdown(marked),
        worst_day_R=float(values.min()),positive_days=int((values>0).sum()),
        profit_factor=float(values[values>0].sum()/losses) if losses>0 else None)


def bootstrap(dates, matrix, seed=20261022301, reps=10000):
    months=sorted({d[:7] for d in dates}); n=len(months)
    sums=np.zeros((n,matrix.shape[1])); squares=sums.copy();counts=np.zeros(n)
    for i,m in enumerate(months):
        x=matrix[[d[:7]==m for d in dates]];sums[i]=x.sum(axis=0);squares[i]=(x*x).sum(axis=0);counts[i]=len(x)
    rng=np.random.default_rng(seed)
    start=rng.integers(0,n-1,size=(reps,int(np.ceil(n/2))))
    ix=(start[:,:,None]+np.arange(2)).reshape(reps,-1)[:,:n]
    ns=counts[ix].sum(axis=1)[:,None]; ss=sums[ix].sum(axis=1)
    means=ss/ns; variance=(squares[ix].sum(axis=1)-ss*ss/ns)/(ns-1)
    sharpe=np.divide(np.sqrt(252)*means,np.sqrt(np.maximum(0,variance)),out=np.zeros_like(means),where=variance>0)
    original=matrix.mean(axis=0)
    return [dict(mean_R_ci95=list(map(float,np.quantile(means[:,j],[.025,.975]))),
                 total_R_fixed_N_ci95=list(map(float,np.quantile(means[:,j],[.025,.975])*len(dates))),
                 sharpe_ci95=list(map(float,np.quantile(sharpe[:,j],[.025,.975]))),
                 p_raw=float((1+(np.abs(means[:,j]-original[j])>=abs(original[j])-1e-12).sum())/(reps+1)),
                 months=n,replications=reps) for j in range(matrix.shape[1])]


def replay_sample(sample,state,included):
    dates=sorted(included); n=len(dates)
    ledger_path=ROOT/('artifacts/edge-marathon/discovery-trades.csv' if sample=='DISCOVERY' else 'artifacts/edge-marathon/continuous_2022_2024_unverified-trades.csv')
    prior={(r['day'],r['model']):r for r in csv.DictReader(ledger_path.open()) if r['model'] in MODELS}
    arrays={v:np.zeros((n,4)) for v in VARIANTS}; marks={v:[] for v in VARIANTS}
    ready=[]; rows=[]; units={v:np.zeros(4) for v in VARIANTS}; cost={v:np.zeros(4) for v in VARIANTS}
    counts={m:dict(original=0,atr_ready=0,missing_ATR_size0=0) for m in MODELS};checked=set()
    for i,day in enumerate(dates):
        prices,ctx=state[day];ctx=dict(ctx);ctx['tom']=bool(calendar_context(day)['tom'])
        if sample=='DISCOVERY' and day<'2025-01-01':ctx['tom']=False
        atr=float(ctx.get('atr',np.nan));ready.append(bool(np.isfinite(atr) and atr>0))
        trades=[dict(fill(event,prices,ctx),day=day) for event in select(prices,ctx) if event['model'] in MODELS]
        for t in trades:
            key=(day,t['model']);old=prior.get(key)
            if old is None: raise ValueError('Unexpected original signal '+str(key))
            for field in ('decision','entry','end','direction','entry_price','exit_price','gross_points','net_points','mfe_points','mae_points'):
                if not np.isclose(float(t[field]),float(old[field]),rtol=0,atol=1e-8):raise ValueError('Original trade replay changed '+str(key)+field)
            checked.add(key);j=MODELS.index(t['model']);counts[t['model']]['original']+=1
            counts[t['model']]['atr_ready' if ready[-1] else 'missing_ATR_size0']+=1
            row=dict(t); row['prior_atr']=atr if ready[-1] else None
            for v in VARIANTS:
                net,q,fee=scaled(t['gross_points'],atr,1.,v);arrays[v][i,j]=net;units[v][j]+=q;cost[v][j]+=fee
                sleeve,sq,sfee=scaled(t['gross_points'],atr,1/3,v);arrays[v][i,3]+=sleeve;units[v][3]+=sq;cost[v][3]+=sfee
                row[v]=dict(net_R=net,qty=q,portfolio_sleeve_qty=sq)
            rows.append(row)
        for v in VARIANTS:
            curves=[]
            for model in MODELS:
                subset=[t for t in trades if t['model']==model]
                curves.append(marked_curve(subset,prices,[1.]*len(subset),v))
            curves.append(marked_curve(trades,prices,[1/3]*len(trades),v))
            marks[v].append(np.asarray(curves).T)
    if checked!=set(prior): raise ValueError('Original trades missing from replay')
    matrix=np.column_stack([arrays[v] for v in VARIANTS]); intervals=bootstrap(dates,matrix,20261022301+(sample!='DISCOVERY'))
    result=dict(days=n,atr_ready_days=sum(ready),missing_ATR_days=n-sum(ready),original_trade_parity=True,counts=counts,variants={})
    for vi,v in enumerate(VARIANTS):
        changes=np.diff(np.vstack([np.zeros((1,4)),np.concatenate([m+arrays[v][:i].sum(axis=0) for i,m in enumerate(marks[v])])]),axis=0)
        result['variants'][v]={}
        for j,model in enumerate((*MODELS,'PORTFOLIO_EQUAL_THIRD')):
            result['variants'][v][model]=dict(**statistics(arrays[v][:,j],changes[:,j]),**intervals[vi*4+j],
                sum_contracts_or_point_weights=float(units[v][j]),cost_R=float(cost[v][j]),
                active_days=int((np.abs(arrays[v][:,j])>1e-12).sum()))
            if v!='NQ_ATR':
                result['variants'][v][model]['total_USD_reference']=float(arrays[v][:,j].sum()*BUDGET)
                result['variants'][v][model]['minute_close_drawdown_USD_reference']=result['variants'][v][model]['minute_close_drawdown_R']*BUDGET
    x=arrays['NQ_ATR'][:,:3]; valid=np.asarray(ready)
    result['daily_net_R_correlation']=np.corrcoef(x.T).tolist()
    result['ATR_ready_daily_net_R_correlation']=np.corrcoef(x[valid].T).tolist()
    active=np.abs(x)>1e-12;result['coactive_days']=(active.astype(int).T@active.astype(int)).tolist()
    if not np.allclose(arrays['NQ_ATR'][:,3],x.mean(axis=1),rtol=0,atol=1e-12):raise ValueError('Fixed third identity failed')
    private=ROOT/'artifacts/three-survivors';private.mkdir(exist_ok=True)
    dump(private/(sample.lower()+'-trades.json'),rows)
    dump(private/(sample.lower()+'-daily.json'),dict(dates=dates,prior_ATR_ready=ready,net_R={v:arrays[v].tolist() for v in VARIANTS}))
    return result


def report(result):
    lines=['# Drie overlevers: vaste ATR-schaling en portefeuille','',
        'Status: EXPLORATORY_CONSUMED_DATA_ONLY — geen onafhankelijk bevestigd winstmodel. Beide bronnen zijn al gebruikt bij selectie. De oudere generieke bron blijft onbevestigd. ATR-schaling bewijst niet dat volatiliteit de eerdere p-waarde veroorzaakte.','',
        '1R = vooraf bekende ATR14, geen stop of verliesmaximum. NQ netto=(bruto−1,225)/ATR. Vaste derde per model, geen herverdeling van ongebruikt budget of kostennetting. Ontbrekende ATR geeft vooraf grootte nul, niet een achteraf berekende ATR. Alle435/493 kalenderdagen blijven in dagelijkse statistieken.','',
        '## Genormaliseerde NQ-resultaten','',
        '| Bron | Model | Trades met ATR / origineel | Netto R | DD dag / minuut R | Sharpe | 95% CI gemiddelde R/dag | Holm8 p |',
        '|---|---|---:|---:|---:|---:|---|---:|']
    for source,s in result['samples'].items():
        for model,r in s['variants']['NQ_ATR'].items():
            c=s['counts'].get(model);cnt=f"{c['atr_ready']} / {c['original']}" if c else 'vaste1/3'
            lines.append(f"| {source} | {model} | {cnt} | {r['total_R']:.4f} | {r['daily_close_drawdown_R']:.4f} / {r['minute_close_drawdown_R']:.4f} | {r['sharpe_daily_annualized']:.3f} | [{r['mean_R_ci95'][0]:.5f}; {r['mean_R_ci95'][1]:.5f}] | {r['p_holm8']:.4f} |")
    lines+=['','Sharpe = √252 × gemiddelde dagelijkse P&L in R / dagelijkse SD; geen account-ROI. Drawdown vanaf nul, markering op minuutclose met volledige RT-kosten bij entry; geen tick-worst-case. CI:10.000 gezamenlijke2-maands clusterbootstrap, nominaal95%, weinig maanden en stationariteit zijn beperkingen. Holm8 corrigeert alleen deze ronde, niet alle voorafgaande selectie.','',
            '## Dagcorrelaties (NQ netto R, inclusief nul-dagen)','', '| Bron | ToM–Compressie | ToM–Sweep | Compressie–Sweep | ATR-ready / alle dagen |','|---|---:|---:|---:|---:|']
    for source,s in result['samples'].items():
        c=s['daily_net_R_correlation'];lines.append(f"| {source} | {c[0][1]:.3f} | {c[0][2]:.3f} | {c[1][2]:.3f} | {s['atr_ready_days']} / {s['days']} |")
    lines+=['','## MNQ-equivalent: vast rekenbudget $1.000 per ATR','',
        'Voorlopige kosten $6,50 per MNQ RT: $4,50 commissie/fees (onbevestigde aanname) +2ticks slippage per kant ($2). Niet $24,50/10. NQ-prijzen als proxy, geen MNQ-executiebewijs. Deelbaar: q=1000/(2×ATR), of1000/(3×2×ATR) per portefeuillesleeve. Geheel: floor(q), ook nul. Geen minimumcontract of achteraf verhoogd budget.','',
        '| Bron | Variant | Model | Contract-RT som | Netto $ | Minuut-DD $ | Sharpe |','|---|---|---|---:|---:|---:|---:|']
    for source,s in result['samples'].items():
        for v in VARIANTS[1:]:
            for model,r in s['variants'][v].items():
                sr='n.v.t.' if r['sharpe_daily_annualized'] is None else f"{r['sharpe_daily_annualized']:.3f}"
                lines.append(f"| {source} | {v} | {model} | {r['sum_contracts_or_point_weights']:.3f} | {r['total_USD_reference']:.2f} | {r['minute_close_drawdown_USD_reference']:.2f} | {sr} |")
    lines+=['','Deelbare contracten zijn niet verhandelbaar. Voor2019 vóór6mei bestaat alleen een hypothetisch MNQ-equivalent; MNQ was toen nog niet gelanceerd. Geen conclusie over marge, accountomvang, risicoacceptatie of toekomstige winst.','',
        '## Registratie en scheiding','',
        'De drie oorspronkelijke signalen plus vaste combinatie zijn apart geregistreerd voor2019–2021. De8 eerder bekeken januari2019-sessies blijven expliciet ontdekt; alleen het restant vanaf14januari kan nog een nieuwe uitkomsttoets vormen. Geen nieuwe2019–2021-signalen of rendementen in deze ronde berekend. Geen push of productiepublicatie.','']
    return '\n'.join(lines)


def run():
    verify(); samples={}
    for sample,state,included in load_samples():
        print('Consumed sample replay: '+sample,flush=True)
        samples[sample]=replay_sample(sample,state,included)
    tested=[r for s in samples.values() for r in s['variants']['NQ_ATR'].values()]
    for r,p in zip(tested,holm([r['p_raw'] for r in tested])):r['p_holm8']=float(p)
    result=dict(status='EXPLORATORY_CONSUMED_DATA_ONLY_NO_PROMOTION',models=list(MODELS),
                protocol_sha256=sha(PROTOCOL),MNQ_RT_cost_assumption=MNQ_COST,dollar_ATR_budget=BUDGET,samples=samples)
    dump(RESULT,result);dump(ROOT/'public/data/three-survivors.json',result)
    text=report(result)
    for path in (ROOT/'docs/THREE_SURVIVORS_ATR_PORTFOLIO.md',ROOT/'public/reports/THREE_SURVIVORS_ATR_PORTFOLIO.md'):path.write_text(text)
    verify();print('Wrote fixed sizing analysis; no unseen outcomes opened.',flush=True)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['register','run','verify']);args=parser.parse_args()
    {'register':register,'run':run,'verify':verify}[args.action]()
