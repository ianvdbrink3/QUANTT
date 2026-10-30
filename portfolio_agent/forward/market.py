"""New immutable forward observations. Never replace historical source snapshots."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from io import StringIO
import hashlib
import json
import numpy as np
import pandas as pd
import requests
from portfolio_agent.calendars import NY,is_session,early_close,stamp as ny_stamp
from portfolio_agent.signal_engine import features
from portfolio_agent.agent_advisor import advise
from .common import stamp,atomic_bytes


def expected_completed(now):
    local=stamp(now).astimezone(NY);day=local.date()
    while True:
        name=day.isoformat()
        if is_session(name) and local>=ny_stamp(name,'13:00' if early_close(name) else '16:00')+timedelta(minutes=10):return name
        day-=timedelta(days=1)


def parse_daily(body,now):
    data=body.get('chart',{}).get('result')
    if body.get('chart',{}).get('error') or not data or len(data)!=1:raise ValueError('VENDOR_RESPONSE_INVALID')
    r=data[0]
    if r.get('meta',{}).get('currency')!='USD':raise ValueError('RESEARCH_CURRENCY_CHANGED')
    dates=pd.to_datetime(r['timestamp'],unit='s',utc=True).tz_convert(NY).strftime('%Y-%m-%d')
    frame=pd.DataFrame(r['indicators']['quote'][0],index=dates)[['open','high','low','close','volume']]
    # Today's incomplete cash bar is not a missing bar; exclude it explicitly.
    frame=frame.loc[frame.index<=expected_completed(now)]
    if not len(frame) or not frame.index.is_unique or not frame.index.is_monotonic_increasing:raise ValueError('INVALID_VENDOR_DATES')
    expected=[d for d in pd.date_range(frame.index[0],frame.index[-1]).strftime('%Y-%m-%d') if is_session(d)]
    if list(frame.index)!=expected:raise ValueError('MISSING_OR_UNEXPECTED_CASH_DAY')
    if len(frame)<504:raise ValueError('FULL_SIGNAL_WARMUP_MISSING')
    features(frame)  # validates OHLCV and rolling input coherence
    return frame.astype(float)


def fetch_yahoo(symbol,now,root,session=None):
    if symbol not in ('QQQ','TQQQ'):raise ValueError('SYMBOL_NOT_ALLOWLISTED')
    http=session or requests.Session()
    r=http.get(f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}',
        params={'period1':1483228800,'period2':int(stamp(now).timestamp()),'interval':'1d','events':'div,splits,capitalGains','includeAdjustedClose':'true'},
        headers={'User-Agent':'QUANT-research/1.0'},timeout=(5,20),allow_redirects=False)
    if r.status_code!=200:raise ValueError('DAILY_VENDOR_HTTP_'+str(r.status_code))
    body=r.json()
    result=body.get('chart',{}).get('result') or []
    if len(result)!=1 or result[0].get('meta',{}).get('symbol')!=symbol:raise ValueError('DAILY_VENDOR_SYMBOL_MISMATCH')
    frame=parse_daily(body,now);payload=r.content;sha=hashlib.sha256(payload).hexdigest()
    target=root/'sources'/f'{symbol}-{sha}.json'
    if not target.exists():atomic_bytes(target,payload)
    elif hashlib.sha256(target.read_bytes()).hexdigest()!=sha:raise ValueError('SOURCE_CACHE_HASH_MISMATCH')
    return frame,dict(provider='Yahoo',symbol=symbol,sha256=sha,available_at=stamp(now).isoformat(),
        last=frame.index[-1],rows=len(frame),price_basis='VENDOR_SPLIT_ADJUSTED_PRICE_NOT_TOTAL_RETURN')


def fetch_secondary(symbol,day,session=None):
    http=session or requests.Session();first=(pd.Timestamp(day)-pd.Timedelta(days=10)).strftime('%Y%m%d')
    r=http.get('https://stooq.com/q/d/l/',params={'s':symbol.lower()+'.us','i':'d','d1':first,'d2':day.replace('-','')},timeout=(5,15),allow_redirects=False)
    if r.status_code!=200:raise ValueError('SECONDARY_VENDOR_UNAVAILABLE')
    data=pd.read_csv(StringIO(r.text))
    if not {'Date','Close'}.issubset(data):raise ValueError('SECONDARY_SCHEMA_UNAVAILABLE')
    found=data[data.Date==day]
    if len(found)!=1 or not np.isfinite(float(found.Close.iloc[0])) or float(found.Close.iloc[0])<=0:raise ValueError('SECONDARY_EXACT_DAY_MISSING')
    return float(found.Close.iloc[0]),hashlib.sha256(r.content).hexdigest()


def acquire(now,root):
    with ThreadPoolExecutor(max_workers=2) as pool:
        values=list(pool.map(lambda s:fetch_yahoo(s,now,root),('QQQ','TQQQ')))
    frames={s:v[0] for s,v in zip(('QQQ','TQQQ'),values)};sources=[v[1] for v in values]
    if not frames['QQQ'].index.equals(frames['TQQQ'].index):raise ValueError('RESEARCH_CALENDAR_MISMATCH')
    day=frames['QQQ'].index[-1]
    confirmations=[]
    for symbol in ('QQQ','TQQQ'):
        try:
            price,sha=fetch_secondary(symbol,day)
            delta=abs(price/float(frames[symbol].close.iloc[-1])-1)*10000
            confirmations.append(dict(provider='Stooq',symbol=symbol,day=day,sha256=sha,difference_bp=delta,status='MATCHED' if delta<=10 else 'PRICE_CONFLICT'))
        except Exception:confirmations.append(dict(provider='Stooq',symbol=symbol,day=day,status='UNAVAILABLE'))
    return frames,sources,confirmations


def decisions(frames,now):
    wanted=expected_completed(now)
    if any(f.index[-1]!=wanted for f in frames.values()):raise ValueError('DAILY_DATA_STALE')
    f={s:features(v) for s,v in frames.items()}
    day=frames['QQQ'].index[-1]
    return {p:dict(advise(float(frames['QQQ'].at[day,'close']),f['QQQ'].loc[day],
                float(frames['TQQQ'].at[day,'close']),f['TQQQ'].loc[day],p),
                signal_day=day,s1_execution='DISABLED_FORWARD_V1',s2_execution='DISABLED_FORWARD_V1')
            for p in ('defensive','balanced','offensive')}
