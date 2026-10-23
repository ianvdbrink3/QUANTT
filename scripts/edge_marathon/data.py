"""Read-only source inventory, hash lock and separate historical quality gates."""
import json
import re
from pathlib import Path
import numpy as np
import pandas as pd
from scripts.oos_preparation.adapter import Calendar,at,load_csv,combine,session_dates,sha
from scripts.causal_map.__main__ import prepare
from scripts.oos_preparation.route import select_active
from scripts.reproduce_research.next_engine import Activation
from scripts.reproduce_research.continuous import roll_spreads
from .features import enrich,cash_dates

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/edge-marathon'


def inventory():
    roots=[Path('/Users/ianvandenbrink/Downloads'),ROOT/'data',ROOT.parent/'data',ROOT.parent/'Quantt/data']
    records={};count=0
    for base in roots:
        if not base.exists():continue
        for path in sorted(base.rglob('*.csv')):
            if 'nq' not in path.name.lower() or not path.is_file():continue
            path=path.resolve();digest=sha(path);count+=1
            if digest in records:
                if str(path) not in records[digest]['paths']:records[digest]['paths'].append(str(path))
                continue
            try:columns=list(pd.read_csv(path,nrows=0).columns)
            except Exception as exc:columns=[]
            records[digest]=dict(sha256=digest,filename=path.name,paths=[str(path)],columns=columns,bytes=path.stat().st_size)
    return dict(scanned_paths=count,unique_contents=len(records),roots=list(map(str,roots)),records=list(records.values()))


def verify_source_register():
    source=json.loads((OUT/'source-register.json').read_text())
    for r in source['records']:
        # Check every original/copy, not just the chosen canonical one.
        for path in r['paths']:
            if sha(path)!=r['sha256']:raise ValueError('Source changed: '+path)
    return source


def basic_frame(path,kind):
    raw=pd.read_csv(path)
    key='timestamp ET' if kind=='GENERIC' else 'timestamp'
    fmt='%m/%d/%Y %H:%M' if kind=='GENERIC' else '%Y-%m-%d %H:%M:%S'
    stamps=pd.DatetimeIndex(pd.to_datetime(raw[key],format=fmt,errors='raise')).tz_localize('America/New_York',ambiguous='raise',nonexistent='raise')
    # Vendor-specific convention, independently recorded before this run.
    if kind=='GENERIC':stamps-=pd.Timedelta(minutes=1)
    frame=raw[['open','high','low','close','volume']].apply(pd.to_numeric)
    frame.index=stamps.tz_convert('UTC');frame['contract']='UNVERIFIED_CONTINUOUS'
    frame['trade_date']=session_dates(frame.index)
    return frame


def quality_and_state(frame,sample,closes,rolls=()):
    start,end=frame.trade_date.min(),frame.trade_date.max()
    days=list(pd.bdate_range(start,end).strftime('%Y-%m-%d'))
    calendar=Calendar(dict(reviewed_ranges=[[start,end]],closes_ny=closes))
    rows=[];included=[]
    # Keep scheduled closed/partial positions in context chronology; fully
    # closed days do not erase the previous trading day's context.
    scheduled=[d for d in days if len(calendar.grid(d))]
    if frame.index.has_duplicates:raise ValueError('Duplicate same-stream timestamps: '+sample)
    groups={d:g for d,g in frame.groupby('trade_date')}
    valid_frame=[]
    for day in scheduled:
        g=groups.get(day,frame.iloc[:0]);ix=pd.date_range(at(day,'09:30'),at(day,'16:00'),freq='min',inclusive='left')
        rth=g.reindex(ix);a=rth[['open','high','low','close','volume']].to_numpy(float)
        finite=np.isfinite(a).all(axis=1);prices=a[:,:4]
        coherent=(a[:,1]>=np.max(prices,axis=1))&(a[:,2]<=np.min(prices,axis=1))
        tick=np.isclose(prices*4,np.rint(prices*4),rtol=0,atol=1e-8).all(axis=1)
        volume=(a[:,4]>0)&(a[:,4]==np.rint(a[:,4]))
        normal=closes.get(day,'17:00')=='17:00'
        boundary=at(day,'09:29') in g.index
        good=bool(normal and finite.all() and coherent.all() and tick.all() and volume.all() and boundary)
        if good:included.append(day)
        rows.append(dict(day=day,normal_full_session=normal,full390=bool(finite.all()),boundary0929=boundary,
            missing_rth=int((~finite).sum()),invalid_ohlc=int((finite & ~coherent).sum()),
            off_tick_bars=int((finite & ~tick).sum()),invalid_volume=int((finite & ~volume).sum()),included=good))
    # Input integrity outside RTH is checked too; never forward-fill.
    values=frame[['open','high','low','close','volume']].to_numpy(float)
    if not np.isfinite(values).all():raise ValueError('Nonfinite source OHLCV: '+sample)
    prices=values[:,:4]
    errors=dict(ohlc=int(((values[:,1]<prices.max(axis=1))|(values[:,2]>prices.min(axis=1))).sum()),
        off_tick=int((~np.isclose(prices*4,np.rint(prices*4),rtol=0,atol=1e-8).all(axis=1)).sum()),
        volume=int(((values[:,4]<=0)|(values[:,4]!=np.rint(values[:,4]))).sum()))
    if errors['ohlc'] or errors['off_tick'] or errors['volume']:
        # Do not expose an invalid stream to rolling ATR/overnight features.
        return None,scheduled,[],dict(sample=sample,quality=rows,source_errors=errors,status='SOURCE_INTEGRITY_FAILED_NOT_SCORED')
    state=prepare(frame,scheduled,calendar,list(rolls))
    state=enrich(state,scheduled,frame,list(rolls))
    return state,scheduled,included,dict(sample=sample,quality=rows,source_errors=errors,
        source_bars=len(frame),complete390=sum(r['full390'] for r in rows),eligible_rth=len(included),
        atr_ready=sum(np.isfinite(state[d][1]['atr']) for d in included),
        atr60_ready=sum(state[d][1]['atr_regime'] is not None for d in included),
        on_complete=sum(state[d][1]['overnight_complete'] for d in included),status='TECHNICAL_QC_COMPLETE_NOT_SOURCE_CERTIFICATION')


def older_closes(start,end):
    # Cash-holiday calendar is an explicit reconstruction, not exchange-signed
    # futures settlement/holiday certification. Early days never enter390RTH.
    dates=list(pd.bdate_range(start,end).strftime('%Y-%m-%d'));cash=set(cash_dates(start,end))
    closes={d:'13:00' for d in dates if d not in cash}
    for day in ['2018-12-25','2019-01-01','2023-01-02','2023-04-07','2023-12-25','2024-01-01','2024-03-29','2024-12-25']:
        if start<=day<=end:closes[day]=None
    for day in ['2018-11-23','2018-12-24','2023-07-03','2023-11-24','2024-07-03','2024-11-29','2024-12-24']:
        if start<=day<=end:closes[day]='13:15'
    if start<='2018-12-05'<=end:closes['2018-12-05']='09:30'
    return closes


def historical_samples():
    source=verify_source_register();records=source['records'];classified=[]
    contract_parts={};generic=None;frd=None
    registered=json.loads((ROOT/'research/oos-year-sources.json').read_text())
    consumed={x['sha256'] for x in registered['sources']+registered['warmup_sources']}
    for r in records:
        path=Path(r['paths'][0]);name=path.name.lower();classification='NOT_ADDITIONAL_MINUTE_DATA'
        if r['sha256'] in consumed:classification='REGISTERED_CONSUMED_SOURCE_NO_NEW_HOLDOUT'
        elif re.match(r'nq(?:z18|h19|h24)_intraday-1min_',name):
            contract=name.split('_')[0].upper()
            try:
                g=load_csv(path,contract);contract_parts.setdefault(contract,[]).append(g)
                classification='EXPLICIT_CONTRACT_FRAGMENT'
            except ValueError as exc:classification='REJECTED_CONTRACT_'+str(exc)
        elif name=='dataset_nq_1min_2022_2025.csv':
            generic=basic_frame(path,'GENERIC')
            generic=generic[generic.trade_date.lt('2024-12-30')]
            classification='OLDER_CONTINUOUS_PRIOR_EXPOSURE_AND_ADJUSTMENT_UNVERIFIED'
        elif name=='nq_1min_sample.csv':
            frd=basic_frame(path,'FRD');frd=frd[frd.trade_date.gt('2026-09-30')]
            classification='POST_DISCOVERY_VENDOR_SAMPLE_NOT_PROSPECTIVE_FORWARD'
        elif 'intraday-1min' in name or 'point_in_time_1min' in name:
            classification='EMPTY_OR_CONSUMED_DATE_SOURCE_NOT_EXTRA_VALIDATED_HISTORY'
        elif r['columns'] and ('datetime' in r['columns'] or 'timestamp' in r['columns']):
            classification='COARSE_FRAME_OR_CONSUMED_CONTINUOUS_NOT_UPSAMPLED'
        classified.append(dict(filename=r['filename'],sha256=r['sha256'],classification=classification))
    samples=[]
    if contract_parts.get('NQZ18') and contract_parts.get('NQH19'):
        full=combine(contract_parts['NQZ18']+contract_parts['NQH19'],'2018-11-19','2019-01-13')
        schedule=[Activation('NQZ18','2018-11-19'),Activation('NQH19','2018-12-17')]
        active=select_active(full,schedule);rolls=roll_spreads(full,schedule)
        state,days,inc,q=quality_and_state(active,'BARCHART_2018_2019',older_closes('2018-11-19','2019-01-13'),rolls)
        for name,a,b,label in [('CONTRACT_2018_WARMUP','2018-11-19','2018-12-31','ADDITIONAL_HISTORICAL_WARMUP_EXPLORATORY'),
                               ('CONTRACT_2019_FRAGMENT','2019-01-02','2019-01-11','SMALL_HISTORICAL_REPLICATION_FRAGMENT_NOT_FIXED_END_TEST')]:
            samples.append(dict(name=name,state=state,days=[d for d in days if a<=d<=b],included=[d for d in inc if a<=d<=b],
                quality=q,exposure=label,source_certified=False,calendar_limit='2018Nov23close provisional; no complete three-year sample'))
    if contract_parts.get('NQH24'):
        active=combine(contract_parts['NQH24'],'2024-01-01','2024-12-29')
        state,days,inc,q=quality_and_state(active,'CONTRACT_PILOT_2024',older_closes(active.trade_date.min(),active.trade_date.max()))
        samples.append(dict(name='CONTRACT_PILOT_2024',state=state,days=days,included=inc,quality=q,
            exposure='PRIOR_TECHNICAL_PILOT_NO_CERTIFIED_ABSOLUTE_BLINDNESS',source_certified=False))
    for name,frame,limit in [('CONTINUOUS_2022_2024_UNVERIFIED',generic,'Prior project exposure; missing contract chain; backadjustment and timestamp publication-vintage unverified. Static-vintage sensitivity, NOT independent causal NQ validation.'),
                             ('VENDOR_SAMPLE_OCT2026',frd,'No explicit contract identity or overlap warmup. Already downloaded historical sample, not prospective forward.')]:
        if frame is None or frame.empty:continue
        state,days,inc,q=quality_and_state(frame,name,older_closes(frame.trade_date.min(),frame.trade_date.max()))
        samples.append(dict(name=name,state=state,days=days,included=inc,quality=q,
            exposure=limit,source_certified=False))
    return samples,classified
