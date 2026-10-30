from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import hashlib
import json
import os
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def utcnow(): return datetime.now(timezone.utc)


def stamp(value):
    out=datetime.fromisoformat(value) if isinstance(value,str) else value
    if not isinstance(out,datetime) or out.tzinfo is None:raise ValueError('AWARE_TIMESTAMP_REQUIRED')
    return out.astimezone(timezone.utc)


def dec(value):
    x=Decimal(str(value))
    if not x.is_finite():raise ValueError('NONFINITE_NUMBER')
    return x


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False,default=str).encode()).hexdigest()


def atomic(path,body):
    return atomic_bytes(path,(json.dumps(body,sort_keys=True,indent=2,allow_nan=False,default=str)+'\n').encode())


def atomic_bytes(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd,tmp=tempfile.mkstemp(dir=path.parent,prefix='.'+path.name)
    try:
        os.fchmod(fd,0o600)
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


def config(path=None):
    file=Path(path or ROOT/'config/portfolio-forward.json')
    c=json.loads(file.read_text())
    required={'schema','mode','profile','broker','demo_orders_enabled','s1_enabled','account_currency',
        'max_roundtrip_bp','max_order_value','strategy_initial_capital','max_quote_age_seconds','poll_seconds','root','bindings'}
    if set(c)!=required or c['schema']!=1:raise ValueError('CONFIG_SCHEMA_MISMATCH')
    if c['mode'] not in ('ADVICE_ONLY','DEMO') or c['broker']!='TRADING212_DEMO':raise ValueError('LIVE_ENDPOINTS_DISABLED')
    if type(c['demo_orders_enabled']) is not bool or c['s1_enabled'] is not False:raise ValueError('S1_OR_MODE_NOT_AUTHORIZED')
    if c['demo_orders_enabled'] and c['mode']!='DEMO':raise ValueError('DEMO_ARMING_REQUIRES_DEMO_MODE')
    if c['profile'] not in ('defensive','balanced','offensive'):raise ValueError('INVALID_PROFILE')
    if c['account_currency'] not in ('EUR','USD'):raise ValueError('INVALID_CURRENCY')
    if not 0<dec(c['max_roundtrip_bp'])<=5 or not 0<dec(c['max_order_value'])<=1000:raise ValueError('RISK_LIMIT_INVALID')
    if not 10<=dec(c['strategy_initial_capital'])<=1000:raise ValueError('INITIAL_STRATEGY_CAPITAL_INVALID')
    if type(c['max_quote_age_seconds']) is not int or not 1<=c['max_quote_age_seconds']<=2:raise ValueError('QUOTE_LIMIT_INVALID')
    if type(c['poll_seconds']) is not int or not 30<=c['poll_seconds']<=3600:raise ValueError('POLL_LIMIT_INVALID')
    p=Path(c['root'])
    if p.is_absolute() or '..' in p.parts or p.parts[:3]!=('artifacts','portfolio_agent','forward'):raise ValueError('PRIVATE_OUTPUT_ONLY')
    if not isinstance(c['bindings'],list):raise ValueError('INVALID_BINDINGS')
    files=sorted((ROOT/'portfolio_agent/forward').glob('*.py'))+[ROOT/'portfolio_agent'/f for f in ('signal_engine.py','agent_advisor.py','regime.py','calendars.py')]
    implementation=digest({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    c['implementation_hash']=implementation
    c['hash']=digest(c)
    return c
