"""One frozen exploratory scan; append-only outputs, independent replay."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .core import (HORIZONS, catalog, select_events, outcome, volume_reference,
                   cluster_inference, holm, encode_events)
from scripts.archive_experiments import verify_archive
from scripts.oos_preparation.adapter import Calendar, at, sha
from scripts.oos_preparation.year import load_registered, forbid_scoring
from scripts.oos_preparation.route import select_active
from scripts.reproduce_research.next_engine import Activation
from scripts.reproduce_research.continuous import roll_spreads

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'artifacts/causal-map'
PROTOCOL = ROOT/'research/causal-map-protocol.json'
LOCK = ROOT/'research/causal-map-lock.json'


def clean(x):
    if isinstance(x,dict): return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple,np.ndarray)): return [clean(v) for v in x]
    if isinstance(x,(np.integer,np.bool_)): return x.item()
    if isinstance(x,(float,np.floating)): return float(x) if np.isfinite(x) else None
    return x


def dump(path, obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(clean(obj),indent=2,allow_nan=False)+'\n')


def protocol():
    return dict(status='EXPLORATORY_CONSUMED_DATA_NOT_NEW_HOLDOUT', anchor_commit='6149e043133487eea69ac9915a4f39e4fc3ae3e4',
        sample='Exactly previous435 complete RTH days; context availability reported separately. No future-day exclusions based on returns.',
        hypotheses=catalog(), horizons=list(HORIZONS),
        A='First reach of each PDH/PDL/ONH/ONL in RTH, including gap-over. First completed close beyond level=ACCEPT; otherwise REJECT. Direction fixed outward for ACCEPT, inward for REJECT. No later classification. First reach at final bar is counted but has no forward horizon.',
        B='Gap up strictly open>PDH; gap down strictly open<PDL. Extreme overnight strictly abs(open-priorRTHclose)/priorATR14>=1.0. At09:30 open and10:00 prior09:59close. Overlapping gap and extreme groups intentionally retained in one family.',
        C='At09:30 use18:00-09:30 overnight direction and range; no RTH direction exists yet. At15:00 use09:30open to14:59close and observed RTH range. Direction UP/DOWN (zero omitted); range/ATR SMALL<0.5, MID[0.5,1.2), LARGE>=1.2. First-half-hour and last-hour are included in four fixed horizons, not MOC order-flow proof.',
        D='Completed aligned1m or5m block volume>linear empirical95th percentile of exactly20 preceding scheduled sessions at same clock; RVOL=current/previous20mean. All20 observations required. New strict RTH extreme relative to bars before block. Skip first block; both-sides blocks may emit both labels. Direction outward; negative forward mean=exhaustion.',
        context='ATR14 mean of14 prior valid complete-session true ranges, point-in-time Panama offsets only when spread known before activation. PDH/PDL/priorclose from immediately previous scheduled complete RTH in current raw basis; no carry through incomplete session. Overnight exact18:00(previous civil date)-09:30 requires all930 minutes; absent levels remain missing. Price outcomes always raw active contract.',
        horizons_rule='k=known boundary, endpointbar=k+h-1 or389; no shortening, no zero-length. Clock09:30 anchor=open; other anchors=last completed close. Excursions only bars k..endpoint; eventbar excluded. RTH close proxy=15:59barclose, not settlement/auction.',
        inference='Pooled event mean. CR1 sandwich of within-day SUM residuals, t(event_days-1), min20 eventdays. Also daily-score HAC with Bartlett lags1..5, same tdf. Global Holm over32x4x2=256 prespecified log-bp zero-mean tests incl unavailable cells p=1. Points CI and MFE/MAE descriptive, no extra p-tests. Rank by maximum of two Holm p-values, then absolute mean bp, not chosen sign.',
        quarters='Every calendar quarter including one-day2024Q4. No quarter p-values, no selection on quarter sign. Quarter counts/means/medians/positive fraction and MFE/MAE all reported.',
        calibration=dict(seed=20261024, panels=128, sessions_per_panel=120, model='Independent zero-mean Gaussian LOG innovations,8substeps/minute, independent overnight logjump and volume. No directional predictability; arithmetic-price Jensen drift is not zero. Same selector, horizons and inference. No rerun to significance.'),
        limitations=['Exploratory scan on consumed data, not preregistered independent confirmation.',
          'Causal means information timing, not causal identification of institutional agents, stops or MOC orders.',
          'Zero-mean drift tests do not establish incremental prediction beyond same-clock unconditional drift.',
          'No execution assumptions, fees, trades or optimal parameters; favorable/adverse paths are not fillable profits.',
          'Same vendor revised OHLCV, no historical publication-vintage certification. Minute timestamps and OHLC hide intrabar ordering.',
          'Small subgroup counts, overlapping horizons, few quarters and asymptotic uncertainty limit interpretation. Nominal CIs are not simultaneous.'])


def register():
    verify_archive()
    p = protocol()
    if PROTOCOL.exists() and json.loads(PROTOCOL.read_text()) != p:
        raise ValueError('Refuse protocol replacement')
    dump(PROTOCOL,p)
    names = ['scripts/causal_map/core.py','scripts/causal_map/__main__.py','research/causal-map-protocol.json',
        'research/oos-year-sources.json','research/oos-year-calendar.json','research/oos-year-rollovers.json',
        'research/holdout-protocol.json','artifacts/raw-market/quality.json']
    names += list(json.loads((ROOT/'research/weighting-audit-lock.json').read_text())['files_sha256'])
    names += list(json.loads((ROOT/'research/weighting-audit-publication.json').read_text())['files_sha256'])
    snap = dict(status='METHOD_CODE_INPUTS_LOCKED_BEFORE_NEW_OUTCOMES', files_sha256={p:sha(ROOT/p) for p in sorted(set(names))})
    if LOCK.exists() and json.loads(LOCK.read_text()) != snap:
        raise ValueError('Locked method changed')
    dump(LOCK,snap)
    return snap


def preflight():
    archive = verify_archive()
    lock = json.loads(LOCK.read_text())
    for name,digest in lock['files_sha256'].items():
        if sha(ROOT/name) != digest: raise ValueError('Locked bytes changed: '+name)
    return archive


def prepare(active, scheduled, calendar, rolls):
    """Sequential point-in-time context; every state stored BEFORE today's update."""
    lookup = {d:g for d,g in active.groupby('trade_date',sort=True)}
    result = {}; hist = []; volume_history = []; previous = None
    for day in scheduled:
        g = lookup.get(day, active.iloc[:0])
        ix = pd.date_range(at(day,'09:30'),at(day,'16:00'),freq='min',inclusive='left')
        rth = g.reindex(ix)
        prices = {z:rth[z].to_numpy(float) for z in ('open','high','low','close','volume')}
        offset = 0.
        for roll in rolls:
            if roll['session'] <= day:
                if roll['spread_available_utc'] > at(day,'09:30'):
                    raise ValueError('Future roll spread')
                offset += roll['spread_points']
        prevday = (pd.Timestamp(day)-pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        onix = pd.date_range(at(prevday,'18:00'),at(day,'09:30'),freq='min',inclusive='left')
        overnight = g.loc[g.index.isin(onix)]
        good_on = overnight.index.equals(onix)
        ctx = dict(opening=float(prices['open'][0]), atr=float(np.mean(hist[-14:])) if len(hist)>=14 else np.nan,
                   PDH=previous['high']+offset if previous else np.nan,
                   PDL=previous['low']+offset if previous else np.nan,
                   prior_close=previous['close']+offset if previous else np.nan,
                   ONH=float(overnight.high.max()) if good_on else np.nan,
                   ONL=float(overnight.low.min()) if good_on else np.nan,
                   on_open=float(overnight.open.iloc[0]) if good_on else np.nan,
                   on_close=float(overnight.close.iloc[-1]) if good_on else np.nan,
                   **volume_reference(volume_history))
        result[day] = (prices,ctx)
        # Missing individual clocks, including early closes, stay missing.
        volume_history.append(prices['volume'])
        volume_history = volume_history[-20:]
        expected = calendar.grid(day)
        expected = expected[(expected>=ix[0]) & (expected<=ix[-1])]
        complete = expected.equals(ix) and np.isfinite(prices['close']).all() and np.isfinite(prices['high']).all() and np.isfinite(prices['low']).all()
        current = None
        if complete:
            current = dict(high=float(prices['high'].max()-offset), low=float(prices['low'].min()-offset), close=float(prices['close'][-1]-offset))
            if previous:
                tr = max(current['high']-current['low'], abs(current['high']-previous['close']), abs(current['low']-previous['close']))
                hist.append(tr)
        previous = current
    return result


def load_inputs():
    full,manifest,reconciliation = load_registered()
    quality = json.loads((ROOT/'artifacts/raw-market/quality.json').read_text())
    days = [q['day'] for q in quality]
    included = [q['day'] for q in quality if q['included']]
    prior = json.loads((ROOT/'research/holdout-protocol.json').read_text())
    year = json.loads((ROOT/'research/oos-year-rollovers.json').read_text())
    schedule = [Activation('NQH25','2024-12-30'),Activation('NQM25','2025-03-19')]
    schedule += [Activation(r['to'],r['effective_session']) for r in prior['rollovers']+year['rollovers']]
    active = select_active(full,schedule)
    calendar = Calendar(json.loads((ROOT/'research/oos-year-calendar.json').read_text()))
    rolls = roll_spreads(full,schedule)
    state = prepare(active,days,calendar,rolls)
    if len(included)!=435 or len(days)!=454: raise ValueError('Sample changed')
    for day in included:
        if not all(np.isfinite(x).all() for x in state[day][0].values()): raise ValueError('Incomplete fixed sample')
    return state,days,included,dict(source_files=len(manifest['sources'])+len(manifest['warmup_sources']),reconciliation=reconciliation),active,calendar,rolls


def extract(state, included):
    records=[]; event_log=[]; eligibility=[]; prefix_checks=0
    for day in included:
        prices,ctx = state[day]
        events = select_events(prices,ctx)
        for k in (0,1,5,15,30,60,120,240,330,360,389,390):
            prefix = {z:x[:k] for z,x in prices.items()}
            got = select_events(prefix,ctx)
            expected = [e for e in events if e.boundary<=k]
            if got != expected: raise AssertionError('Future truncation mismatch '+day+' '+str(k))
            prefix_checks += 1
        for event in events:
            event_log.append(dict(day=day,**encode_events([event])[0]))
            for horizon in HORIZONS:
                value = outcome(prices,event,horizon)
                if value is not None:
                    records.append(dict(day=day,quarter=str(pd.Period(day,freq='Q')),mechanism=event.mechanism,
                        boundary=event.boundary,direction=event.direction,anchor=event.anchor,horizon=str(horizon),**value))
        eligibility.append(dict(day=day,ATR_ready=bool(np.isfinite(ctx['atr'])),PD_ready=bool(np.isfinite(ctx['PDH'])),
            overnight_complete=bool(np.isfinite(ctx['ONH'])),volume1_clocks_ready=int(np.isfinite(ctx['volume_q95_1']).sum()),
            volume5_clocks_ready=int(np.isfinite(ctx['volume_q95_5']).sum()),events=len(events)))
    return pd.DataFrame(records),pd.DataFrame(event_log),eligibility,prefix_checks


def description(g):
    if not len(g):
        return dict(events=0,days=0,mean_points=None,median_points=None,mean_bps=None,median_bps=None,positive_fraction=None,
            mean_mfe_points=None,mean_mae_points=None,mfe_mae_ratio=None,median_mfe_points=None,median_mae_points=None,
            mean_mfe_bps=None,mean_mae_bps=None,mfe_mae_balance_median=None)
    mfe,mae = g.mfe_points.to_numpy(),g.mae_points.to_numpy()
    den = mfe+mae
    return dict(events=len(g),days=g.day.nunique(),mean_points=g.return_points.mean(),median_points=g.return_points.median(),
        mean_bps=g.return_bps.mean(),median_bps=g.return_bps.median(),positive_fraction=(g.return_bps>0).mean(),
        mean_mfe_points=mfe.mean(),mean_mae_points=mae.mean(),mfe_mae_ratio=mfe.mean()/mae.mean() if mae.mean()>0 else None,
        median_mfe_points=float(np.median(mfe)),median_mae_points=float(np.median(mae)),
        mean_mfe_bps=g.mfe_bps.mean(),mean_mae_bps=g.mae_bps.mean(),
        mfe_mae_balance_median=float(np.median(np.divide(mfe-mae,den,out=np.zeros(len(g)),where=den>0))))


def calculate(records, days, included):
    ids = {d:i for i,d in enumerate(days)}
    quarters = sorted({str(pd.Period(d,freq='Q')) for d in included})
    rows=[]; ps=[]
    for mechanism in catalog():
        for horizon in HORIZONS:
            g = records[(records.mechanism==mechanism['id']) & (records.horizon==str(horizon))]
            inf = cluster_inference(g.return_bps,g.day.map(ids),len(days))
            ip = cluster_inference(g.return_points,g.day.map(ids),len(days))
            row = dict(**mechanism,horizon=str(horizon),**description(g),inference_bps=inf,ci95_points=ip['ci95'],hac_ci95_points=ip['hac_ci95'],
                quarters=[dict(quarter=q,**description(g[g.quarter==q])) for q in quarters])
            rows.append(row);ps.extend([inf['p'],inf['hac_p']])
    adj = holm(ps)
    for i,row in enumerate(rows):
        row['p_holm256'] = adj[2*i]; row['hac_p_holm256'] = adj[2*i+1]
        row['ranking_p'] = max(adj[2*i:2*i+2])
    order = sorted(range(len(rows)),key=lambda i:(rows[i]['ranking_p'],-abs(rows[i]['mean_bps'] or 0),rows[i]['id'],rows[i]['horizon']))
    ranks = {i:k+1 for k,i in enumerate(order)}
    for i,row in enumerate(rows): row['rank']=ranks[i]
    return rows


def calibration():
    """Fixed complete-pipeline log-martingale calibration, not actual-market fit."""
    settings = protocol()['calibration']; rng=np.random.default_rng(settings['seed'])
    values={r['id']+'|'+str(h):[] for r in catalog() for h in HORIZONS}
    adjusted=[]; counts=[]
    for rep in range(settings['panels']):
        state={}; hist=[]; vols=[]; prev=None; p=10000.
        dates=pd.bdate_range('2000-01-03',periods=settings['sessions_per_panel']).strftime('%Y-%m-%d').tolist()
        for day in dates:
            onopen=p; opening=p*np.exp(rng.normal(0,.0005*np.sqrt(930)))
            # Prior templates and independent overnight wicks are known before
            # any current RTH innovation. Conditional future log mean remains0.
            onhigh=max(onopen,opening)*np.exp(abs(rng.normal(0,.004)))
            onlow=min(onopen,opening)*np.exp(-abs(rng.normal(0,.004)))
            steps=rng.normal(0,.0005/np.sqrt(8),size=(390,8))
            logpath=np.cumsum(steps.ravel()).reshape(390,8)
            close=opening*np.exp(logpath[:,-1]); opens=np.r_[opening,close[:-1]]
            prices=dict(open=opens,close=close,high=np.maximum(opens,opening*np.exp(logpath.max(axis=1))),
                low=np.minimum(opens,opening*np.exp(logpath.min(axis=1))),volume=rng.lognormal(5,1,390))
            ctx=dict(opening=opening,atr=np.mean(hist[-14:]) if len(hist)>=14 else np.nan,
                PDH=prev['high'] if prev else np.nan,PDL=prev['low'] if prev else np.nan,
                prior_close=prev['close'] if prev else np.nan,ONH=onhigh,ONL=onlow,on_open=onopen,on_close=opening,
                **volume_reference(vols))
            state[day]=(prices,ctx)
            if prev:
                hist.append(max(prices['high'].max()-prices['low'].min(),abs(prices['high'].max()-prev['close']),abs(prices['low'].min()-prev['close'])))
            prev=dict(high=prices['high'].max(),low=prices['low'].min(),close=close[-1]);p=close[-1]
            vols.append(prices['volume']);vols=vols[-20:]
        rs=[]
        for day,(prices,ctx) in state.items():
            for event in select_events(prices,ctx):
                for horizon in HORIZONS:
                    value=outcome(prices,event,horizon)
                    if value is not None:rs.append(dict(day=day,quarter=str(pd.Period(day,freq='Q')),mechanism=event.mechanism,horizon=str(horizon),**value))
        panel=calculate(pd.DataFrame(rs),dates,dates)
        valid_panel=[];adj_panel=[]
        for r in panel:
            key=r['id']+'|'+r['horizon']; inf=r['inference_bps']
            values[key].append(dict(p=inf['p'],hac_p=inf['hac_p'],ci=inf['ci95'],mean=r['mean_bps'],days=r['days']))
            valid_panel.append(inf['p'] is not None);adj_panel.append(r['ranking_p'])
        adjusted.append(adj_panel);counts.append(valid_panel)
        if (rep+1)%16==0:print(f'null calibration {rep+1}/{settings["panels"]}',flush=True)
    rows=[]
    for key,items in values.items():
        good=[x for x in items if x['p'] is not None]
        rows.append(dict(cell=key,valid_panels=len(good),total_panels=len(items),
            nominal_rejections=sum(x['p']<.05 for x in good),hac_nominal_rejections=sum(x['hac_p']<.05 for x in good),
            nominal_coverage=sum(x['ci'][0]<=0<=x['ci'][1] for x in good)/len(good) if good else None,
            median_event_days=np.median([x['days'] for x in items])))
    return dict(settings=settings,rows=rows,
        panels_any_joint_rejection=int((np.asarray(adjusted).min(axis=1)<.05).sum()),
        panels_any_valid=int(np.asarray(counts).any(axis=1).sum()),
        note='Finite synthetic calibration, not proof of nominal coverage under real NQ regimes. Sparse cells remain untested. No arithmetic-point zero-null asserted.')


def verify():
    archive=preflight(); saved=json.loads((OUT/'COMPLETED.json').read_text())
    for name,digest in saved['files_sha256'].items():
        if sha(ROOT/name)!=digest:raise ValueError('Output changed: '+name)
    return dict(status='PASS_FIXED_METHOD_SOURCE_AND_OUTPUT_HASHES',archive=archive,new_strategy_runs=0,**saved['verification'])


def run():
    archive=preflight()
    if (OUT/'COMPLETED.json').exists():raise ValueError('Completed batch exists; --verify only, no significance reruns')
    OUT.mkdir(parents=True,exist_ok=True)
    nullpath=OUT/'calibration.json'
    if nullpath.exists():
        calibration_result=json.loads(nullpath.read_text())
        checkpoint=json.loads((OUT/'calibration-checkpoint.json').read_text())
        if checkpoint!={'sha256':sha(nullpath),'lock_sha256':sha(LOCK)}:raise ValueError('Null checkpoint changed')
    else:
        calibration_result=calibration();dump(nullpath,calibration_result)
        dump(OUT/'calibration-checkpoint.json',dict(sha256=sha(nullpath),lock_sha256=sha(LOCK)))
    print('Load69 hashed sources, no strategy calls',flush=True)
    with forbid_scoring():
        state,days,included,source,active,calendar,rolls=load_inputs()
        records,event_log,eligibility,prefix_checks=extract(state,included)
    # Full preparation truncation at every roll boundary plus two arbitrary
    # history cutoffs. Unlike a feature-only test this recomputes prior state.
    ctx_checks=0
    for day in sorted(set([r['session'] for r in rolls]+[included[100],included[300]])):
        subset=[d for d in days if d<=day]
        if not subset:continue
        truncated=active[active.trade_date.le(day)]
        earlier_rolls=[r for r in rolls if r['session']<=day]
        rebuilt=prepare(truncated,subset,calendar,earlier_rolls)
        for key in ('atr','PDH','PDL','prior_close','ONH','ONL','on_open','on_close','volume_q95_1','volume_q95_5'):
            if not np.allclose(rebuilt[day][1][key],state[day][1][key],rtol=0,atol=0,equal_nan=True):raise AssertionError('Context future leak')
            ctx_checks+=1
    print('Score prespecified horizons; independent second extraction and inference',flush=True)
    rows=calculate(records,days,included)
    # Recompute selection/outcomes, not merely reload saved values.
    replay,elog2,elig2,prefix2=extract(state,included)
    pd.testing.assert_frame_equal(records,replay,check_exact=True)
    pd.testing.assert_frame_equal(event_log,elog2,check_exact=True)
    rows2=calculate(replay,days,included)
    if json.dumps(clean(rows),sort_keys=True)!=json.dumps(clean(rows2),sort_keys=True):raise AssertionError('Independent replay aggregate mismatch')
    records.to_csv(OUT/'events-horizons.csv',index=False,float_format='%.17g')
    event_log.to_csv(OUT/'events.csv',index=False,float_format='%.17g')
    replay.to_csv(OUT/'events-horizons-replay.csv',index=False,float_format='%.17g')
    if sha(OUT/'events-horizons.csv')!=sha(OUT/'events-horizons-replay.csv'):raise AssertionError('Ledger bytes mismatch')
    dump(OUT/'eligibility.json',eligibility)
    verification=dict(complete_RTH_days=len(included),scheduled_sessions=len(days),source_files=source['source_files'],
        selected_events=len(event_log),event_horizon_rows=len(records),future_prefix_checks=prefix_checks,
        recomputed_context_checks=ctx_checks,identical_replay=True,ledger_sha256=sha(OUT/'events-horizons.csv'),
        cells=len(rows),global_test_family=len(rows)*2,protected_archive_files=archive['protected_files'])
    summary=dict(status='EXPLORATORY_CAUSAL_TIMING_SCAN_NOT_VALIDATED_EDGE',protocol_sha256=sha(PROTOCOL),
        method_lock_sha256=sha(LOCK),verification=verification,source=source,
        eligibility_summary=dict(ATR_ready=sum(x['ATR_ready'] for x in eligibility),PD_ready=sum(x['PD_ready'] for x in eligibility),
            overnight_complete=sum(x['overnight_complete'] for x in eligibility),
            days_any_volume1_reference=sum(x['volume1_clocks_ready']>0 for x in eligibility),days_all_volume1_reference=sum(x['volume1_clocks_ready']==390 for x in eligibility),
            days_any_volume5_reference=sum(x['volume5_clocks_ready']>0 for x in eligibility)),
        category_events=event_log.assign(category=event_log.mechanism.str[0]).groupby('category').size().to_dict(),
        rows=rows,calibration=calibration_result,protocol=protocol())
    dump(OUT/'summary.json',summary)
    files=['calibration.json','calibration-checkpoint.json','events-horizons.csv','events.csv','events-horizons-replay.csv','eligibility.json','summary.json']
    dump(OUT/'COMPLETED.json',dict(files_sha256={str((OUT/n).relative_to(ROOT)):sha(OUT/n) for n in files},verification=verification))
    dump(ROOT/'research/causal-map-verification.json',dict(status='PASS',**verification,archive=archive,
        private_evidence_sha256={str((OUT/n).relative_to(ROOT)):sha(OUT/n) for n in files}))
    print(json.dumps(clean(verification),indent=2),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--register',action='store_true');parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    if args.register:print(json.dumps(register(),indent=2))
    elif args.verify:print(json.dumps(verify(),indent=2))
    else:run()
