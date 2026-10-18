#!/usr/bin/env python3
"""Audit public source availability from the GitHub runner; never synthesize prices."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import requests

SOURCES={
 'dukascopy_legacy_2024':'https://datafeed.dukascopy.com/datafeed/USATECHIDXUSD/2024/00/03/BID_candles_min_1.bi5',
 'dukascopy_legacy_2026':'https://datafeed.dukascopy.com/datafeed/USATECHIDXUSD/2026/09/15/BID_candles_min_1.bi5',
 'dukascopy_api':'https://jetta.dukascopy.com/v1/candles/minute/USATECH.IDX-USD/BID/2024/1/3',
 'histdata':'https://www.histdata.com/download-free-forex-historical-data/?/ascii/1-minute-bar-quotes/NSXUSD/2024',
 'yahoo_ndx_daily':'https://query1.finance.yahoo.com/v8/finance/chart/%5ENDX?period1=1704067200&period2=1792368000&interval=1d',
}
def probe(item):
 name,url=item
 try:
  response=requests.get(url,timeout=(10,25),headers={'User-Agent':'Mozilla/5.0 QUANTT-Research'})
  row={'name':name,'url':url,'status':response.status_code,'bytes':len(response.content),'sha256':hashlib.sha256(response.content).hexdigest(),'browser_challenge':response.headers.get('x-amzn-waf-action')=='challenge'}
  if name.startswith('dukascopy_legacy') and response.status_code==200:
   import lzma
   raw=lzma.decompress(response.content)
   row['candle_records']=len(raw)//24 if len(raw)%24==0 else None
  if name=='yahoo_ndx_daily' and response.status_code==200:
   value=response.json()['chart']['result'][0]
   row['observations']=len(value.get('timestamp',[]))
  return row
 except Exception as exc:
  return {'name':name,'url':url,'error':f'{type(exc).__name__}: {exc}'}
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=3) as pool:
  rows=list(pool.map(probe,SOURCES.items()))
 result={'generated_at':datetime.now(timezone.utc).isoformat(),'execution_environment':'github-actions','sources':rows}
 path=Path('data/source_probe_report.json');path.parent.mkdir(exist_ok=True)
 path.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
