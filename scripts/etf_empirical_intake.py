"""Immutable public daily-price and corporate-action snapshots; no credentials."""
import concurrent.futures
import datetime as dt
import hashlib
import json
from pathlib import Path

import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw/etf-empirical-2026-10-29'
REGISTER=ROOT/'research/etf-empirical-sources-2026-10-29.json'
START=int(dt.datetime(2017,1,1,tzinfo=dt.timezone.utc).timestamp())
END=int(dt.datetime(2026,10,29,tzinfo=dt.timezone.utc).timestamp())


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fetch(symbol):
    path=RAW/f'{symbol}_yahoo_daily_2017-01-01_2026-10-28.json'
    url=f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}'
    params=dict(period1=START,period2=END,interval='1d',events='div,splits,capitalGains',includeAdjustedClose='true')
    if path.exists():
        payload=path.read_bytes();status='EXISTING_IMMUTABLE_SOURCE'
    else:
        response=requests.get(url,params=params,headers={'User-Agent':'Mozilla/5.0'},timeout=30)
        response.raise_for_status();payload=response.content
        body=json.loads(payload)
        if body['chart'].get('error') or not body['chart'].get('result'):raise ValueError('Yahoo did not return price data')
        RAW.mkdir(parents=True,exist_ok=True);path.write_bytes(payload);status='DOWNLOADED_PUBLIC_SOURCE'
    result=json.loads(payload)['chart']['result'][0]
    dates=pd.to_datetime(result['timestamp'],unit='s',utc=True).tz_convert('America/New_York').strftime('%Y-%m-%d')
    return dict(symbol=symbol,path=str(path.relative_to(ROOT)),sha256=sha(path),url=url,
        params=params,rows=len(dates),first=str(dates[0]),last=str(dates[-1]),status=status,
        dividend_events=len(result.get('events',{}).get('dividends',{})),
        split_events=len(result.get('events',{}).get('splits',{})))


def run():
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(fetch,('QQQ','TQQQ','SPY','UPRO')))
    RAW.mkdir(parents=True,exist_ok=True)
    data=dict(date='2026-10-29',status='IMMUTABLE_ETF_DAILY_SOURCES_CORPORATE_ACTIONS_INCLUDED',
        price_adjustment='Vendor quote OHLC are split-adjusted. Adjusted close additionally incorporates distributions; corporate actions retained. Verify factors before returns.',
        files=rows,minute_sources=[])
    if REGISTER.exists():
        previous=json.loads(REGISTER.read_text())
        if [(r['path'],r['sha256']) for r in previous['files']]!=[(r['path'],r['sha256']) for r in rows]:
            raise ValueError('Refusing to replace a different existing source register')
    else:REGISTER.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    print(json.dumps(rows,indent=2))


if __name__=='__main__':run()
