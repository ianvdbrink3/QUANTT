"""Official v0 protocol, demo host only; no retry on non-idempotent mutations."""
import base64
import json
import os
import re
import threading
import time
from urllib.parse import urlparse,parse_qs
import requests
from requests.adapters import HTTPAdapter
from .common import dec

BASE='https://demo.trading212.com/api/v0'
READS={'/equity/account/summary','/equity/positions','/equity/orders','/equity/metadata/instruments','/equity/metadata/exchanges','/equity/history/orders','/equity/history/dividends','/equity/history/transactions'}
PERIODS={'/equity/account/summary':5,'/equity/positions':1,'/equity/orders':1,
         '/equity/metadata/instruments':50,'/equity/metadata/exchanges':50,'/equity/history/orders':3,
         '/equity/history/dividends':3,'/equity/history/transactions':3,'/equity/orders/limit':2}


class BrokerFailure(RuntimeError):
    def __init__(self,code,ambiguous=False):self.code=code;self.ambiguous=ambiguous;super().__init__(code)


class Trading212Demo:
    live_enabled=False
    def __init__(self,key=None,secret=None,base_url=BASE,transport=None,clock=time.monotonic,allow_mutations=True):
        if base_url!=BASE:raise ValueError('ONLY_OFFICIAL_DEMO_HOST_ALLOWED')
        key=os.environ.get('QUANT_T212_DEMO_KEY','') if key is None else key
        secret=os.environ.get('QUANT_T212_DEMO_SECRET','') if secret is None else secret
        if not key or not secret:raise BrokerFailure('DEMO_CREDENTIALS_MISSING')
        # The broker's current API terms prohibit algorithmic trading.  A
        # production network client therefore cannot send or cancel orders;
        # explicitly injected transports remain available for offline tests.
        self._allow_mutations=allow_mutations is True and transport is not None
        self._auth='Basic '+base64.b64encode((key+':'+secret).encode()).decode()
        self._transport=transport or requests.Session();self._clock=clock;self._next={};self._lock=threading.Lock()
        if transport is None:
            self._transport.trust_env=False
            self._transport.mount('https://',HTTPAdapter(max_retries=0))

    def _request(self,method,path,payload=None):
        if method!='GET' and not self._allow_mutations:raise BrokerFailure('DEMO_MUTATIONS_DISABLED_READ_ONLY')
        parsed=urlparse(path);query=parse_qs(parsed.query)
        if parsed.scheme or parsed.netloc or parsed.fragment or '..' in path:raise ValueError('BROKER_PATH_NOT_ALLOWLISTED')
        resource=parsed.path
        numeric=bool(re.fullmatch(r'/equity/orders/[0-9]+',resource))
        if method=='GET':
            if resource not in READS and not numeric:raise ValueError('BROKER_PATH_NOT_ALLOWLISTED')
            if query and (resource not in ('/equity/history/orders','/equity/history/dividends','/equity/history/transactions') or set(query)-{'cursor','limit','ticker'}):raise ValueError('BROKER_QUERY_NOT_ALLOWLISTED')
        elif method=='POST':
            if resource!='/equity/orders/limit' or parsed.query:raise ValueError('ONLY_DEMO_LIMIT_ORDERS_SUPPORTED')
        elif method=='DELETE':
            if not numeric or parsed.query:raise ValueError('ONLY_KNOWN_ORDER_CANCELLATION_SUPPORTED')
        else:raise ValueError('METHOD_DISABLED')
        bucket=method+(':/equity/orders/id' if numeric else ':'+resource)
        with self._lock:
            now=self._clock()
            if self._next.get(bucket,0)>now:raise BrokerFailure('DEMO_RATE_LIMITED')
            self._next[bucket]=now+PERIODS.get(resource,1)
        try:
            r=self._transport.request(method,BASE+path,headers={'Authorization':self._auth,'Accept':'application/json'},
                json=payload,timeout=(5,10),allow_redirects=False)
        except requests.RequestException:raise BrokerFailure('DEMO_CONNECTION_UNCERTAIN',ambiguous=method!='GET') from None
        if r.status_code==429:
            with self._lock:self._next[bucket]=self._clock()+max(30,PERIODS.get(resource,1))
        if r.status_code!=200:raise BrokerFailure('DEMO_HTTP_'+str(r.status_code),ambiguous=method!='GET' and (r.status_code>=500 or r.status_code in (408,429) or 300<=r.status_code<400))
        if method=='DELETE':return None
        try:return r.json()
        except (ValueError,TypeError):raise BrokerFailure('DEMO_RESPONSE_UNCERTAIN',ambiguous=method!='GET') from None

    def read(self,path):return self._request('GET',path)
    def submit_limit(self,intent):
        quantity=dec(intent['quantity']);price=dec(intent['limitPrice'])
        if not quantity or price<=0 or not re.fullmatch(r'[A-Za-z0-9_.-]{1,60}',intent['ticker']):raise ValueError('INVALID_DEMO_LIMIT')
        return self._request('POST','/equity/orders/limit',dict(ticker=intent['ticker'],quantity=float(quantity),limitPrice=float(price),timeValidity='DAY'))
    def cancel(self,id):return self._request('DELETE','/equity/orders/'+str(id))

    def history_page(self,ticker,cursor_path=None):
        if not re.fullmatch(r'[A-Za-z0-9_.-]{1,60}',ticker):raise ValueError('INVALID_TICKER')
        path=cursor_path or '/equity/history/orders?limit=50&ticker='+ticker
        if not path.startswith('/equity/history/orders?'):raise BrokerFailure('HISTORY_CURSOR_REJECTED')
        body=self.read(path)
        if not isinstance(body,dict) or not isinstance(body.get('items'),list):raise BrokerFailure('HISTORY_SCHEMA_INVALID')
        next_=body.get('nextPagePath')
        if next_:
            if not next_.startswith('/api/v0/equity/history/orders?'):raise BrokerFailure('HISTORY_CURSOR_REJECTED')
            next_=next_.removeprefix('/api/v0')
        return body['items'],next_
