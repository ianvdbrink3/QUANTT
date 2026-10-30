import gzip
import json

import numpy as np
import pandas as pd

from scripts.etf_empirical_intake import ROOT,REGISTER,sha
from scripts.etf_minute_intake import REGISTER as MINUTE_REGISTER,read as read_minute


def day_features(frame):
    """Every rolling input is from a completed current/prior daily bar."""
    c=frame.close;p=c.shift(1)
    tr=pd.concat([frame.high-frame.low,(frame.high-p).abs(),(frame.low-p).abs()],axis=1).max(axis=1)
    out=pd.DataFrame(index=frame.index)
    out['SMA20']=c.rolling(20,min_periods=20).mean()
    out['SMA200']=c.rolling(200,min_periods=200).mean()
    out['ATR14']=tr.shift(1).rolling(14,min_periods=14).mean()
    width=frame.high-frame.low
    out['IBS']=(c-frame.low)/width.replace(0,np.nan)
    out['S2']=(c>out.SMA20)&out.SMA20.notna()
    out['S1']=out.S2&(out.IBS>=.85)&(width>.85*out.ATR14)&out.ATR14.notna()
    out['TREND20']=(c>out.SMA20)&out.SMA20.notna()
    out['TREND200']=(c>out.SMA200)&out.SMA200.notna()
    for length in (5,10,20):out[f'momentum{length}']=c/c.shift(length)-1
    return out


def daily():
    sources=json.loads(REGISTER.read_text());frames={};audits={};splits={}
    for item in sources['files']:
        path=ROOT/item['path']
        if sha(path)!=item['sha256']:raise ValueError('Daily source bytes changed')
        body=json.loads(path.read_text())['chart']['result'][0]
        dates=pd.to_datetime(body['timestamp'],unit='s',utc=True).tz_convert('America/New_York').strftime('%Y-%m-%d')
        frame=pd.DataFrame(body['indicators']['quote'][0],index=dates)[['open','high','low','close','volume']]
        frame['adjclose']=body['indicators']['adjclose'][0]['adjclose']
        if not frame.index.is_unique or not frame.index.is_monotonic_increasing:raise ValueError('Invalid daily dates')
        if not np.isfinite(frame.to_numpy()).all() or not (frame>0).all().all():raise ValueError('Invalid daily numeric bars')
        if not ((frame.high>=frame[['open','high','low','close']].max(axis=1))&(frame.low<=frame[['open','high','low','close']].min(axis=1))).all():raise ValueError('Daily OHLC incoherent')
        frame['distribution']=0.;actions=[];split_events=[]
        for kind in ('dividends','capitalGains'):
            for event in body.get('events',{}).get(kind,{}).values():
                day=pd.Timestamp(event['date'],unit='s',tz='UTC').tz_convert('America/New_York').strftime('%Y-%m-%d')
                if day not in frame.index:raise ValueError('Distribution outside observed cash calendar')
                frame.at[day,'distribution']+=event['amount'];actions.append(dict(day=day,amount=event['amount'],kind=kind))
        factor=frame.adjclose/frame.close;errors=[]
        for day in frame.index[1:]:
            previous=frame.index[frame.index.get_loc(day)-1]
            expected=1-frame.at[day,'distribution']/frame.at[previous,'close']
            errors.append(abs(factor.at[previous]/factor.at[day]-expected))
        if max(errors)>2e-5:raise ValueError(('Adjusted-close action reconciliation failed',item['symbol'],max(errors)))
        for event in body.get('events',{}).get('splits',{}).values():
            day=pd.Timestamp(event['date'],unit='s',tz='UTC').tz_convert('America/New_York').strftime('%Y-%m-%d')
            ratio=float(event['numerator'])/float(event['denominator']);i=frame.index.get_loc(day)
            split_events.append(dict(day=day,ratio=ratio,previous_split_adjusted_close=float(frame.close.iloc[i-1]),
                split_adjusted_open=float(frame.open.iloc[i]),normalized_overnight_pct=100*(frame.open.iloc[i]/frame.close.iloc[i-1]-1),
                adj_factor_ratio=float(factor.iloc[i-1]/factor.iloc[i])))
        symbol=item['symbol'];frames[symbol]=frame;splits[symbol]=split_events
        audits[symbol]=dict(rows=len(frame),first=frame.index[0],last=frame.index[-1],
            source_sha256=item['sha256'],actions=actions,splits=split_events,
            adjustment_reconciliation_max_abs_error=float(max(errors)))
    reference=frames['QQQ'].index
    for symbol,frame in frames.items():
        if not frame.index.equals(reference):raise ValueError('Different ETF daily cash calendars '+symbol)
    expected={'2021-01-21':2.,'2022-01-13':2.,'2018-05-24':3.,'2025-11-20':2.}
    actual={v['day']:v['ratio'] for v in splits['TQQQ']}
    if any(actual.get(d)!=r for d,r in expected.items()):raise ValueError('Official TQQQ split mismatch')
    return frames,audits,splits


def minutes():
    registry=json.loads(MINUTE_REGISTER.read_text());frames={};audit={}
    for symbol in ('QQQ','TQQQ'):
        parts=[]
        for item in registry['files']:
            if item['symbol']!=symbol:continue
            path=ROOT/item['path']
            if sha(path)!=item['sha256']:raise ValueError('Minute source bytes changed')
            parts.append(read_minute(path))
        if not parts:
            frames[symbol]=pd.DataFrame();audit[symbol]=dict(files=0,bars=0);continue
        frame=pd.concat(parts).sort_index();duplicates=frame.index.duplicated(keep=False)
        if frame[duplicates].groupby(level=0).nunique().gt(1).any().any():raise ValueError('Conflicting minute duplicates '+symbol)
        repeated=int(frame.index.duplicated().sum());frame=frame[~frame.index.duplicated()]
        frames[symbol]=frame
        audit[symbol]=dict(files=len(parts),bars=len(frame),identical_overlap_bars_removed=repeated,
            zero_volume_bars=int((frame.volume==0).sum()),first=frame.index[0].isoformat(),last=frame.index[-1].isoformat())
    return frames,audit


def frozen_nq_signals():
    result={}
    for era in ('2019_2021','2025_2026'):
        path=ROOT/f'artifacts/own-account/private-NQ-{era}.json.gz'
        block=json.loads(gzip.decompress(path.read_bytes()))
        result[era]={day:{key:bool(f[key]) for key in ('S1','S2')} for day,f in block['features'].items()}
    return result
