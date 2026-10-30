#!/usr/bin/env python3
"""Reproduce local product-data and start-evidence audit without any broker order."""
from pathlib import Path
import hashlib,json,sys
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from portfolio_agent.forward.common import ROOT,config,atomic,utcnow
from portfolio_agent.forward.agent import status
from portfolio_agent.forward.store import Store
from portfolio_agent.calendars import is_session,stamp as ny_stamp


def audit_daily(body):
    result=body['chart']['result'][0];meta=result['meta']
    dates=pd.to_datetime(result['timestamp'],unit='s',utc=True).tz_convert(meta['exchangeTimezoneName']).strftime('%Y-%m-%d')
    frame=pd.DataFrame(result['indicators']['quote'][0],index=dates)[['open','high','low','close','volume']].astype(float)
    missing=~np.isfinite(frame).all(axis=1)
    price_bad=(frame[['open','high','low','close']]<=0).any(axis=1)
    upper=(frame[['open','low','close']].max(axis=1)-frame.high).clip(lower=0)
    lower=(frame.low-frame[['open','high','close']].min(axis=1)).clip(lower=0)
    range_bad=(upper>0)|(lower>0)
    return dict(symbol=meta['symbol'],currency=meta['currency'],exchange=meta['fullExchangeName'],timezone=meta['exchangeTimezoneName'],
        first=dates[0],last=dates[-1],rows=len(frame),duplicate_dates=int(dates.duplicated().sum()),
        missing_or_nonfinite_bars=int(missing.sum()),nonpositive_price_bars=int(price_bad.sum()),ohlc_inconsistent_bars=int(range_bad.sum()),
        ohlc_inconsistent_above_one_cent=int(((upper>.01)|(lower>.01)).sum()),
        invalid_total=int((missing|price_bad|range_bad).sum()),invalid_dates=dates[missing|price_bad|range_bad].tolist(),
        year_counts={str(y):int((dates.str[:4]==str(y)).sum()) for y in range(2019,2027)},
        dividends=len(result.get('events',{}).get('dividends',{})),splits=len(result.get('events',{}).get('splits',{})),
        minute_execution_parity_verified=False,historical_performance_inherited=False)


def build():
    c=config();root=ROOT/c['root'];folder=root/'readiness';probes=json.loads((folder/'source-probes.json').read_text());data=[]
    for probe in probes:
        if not probe['name'].startswith('yahoo-'):continue
        raw=(folder/(probe['name']+'-'+probe['sha256']+'.response')).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=probe['sha256']:raise ValueError('AUDIT_SOURCE_HASH_MISMATCH')
        out=audit_daily(json.loads(raw));out.update(source_sha256=probe['sha256'],received_at=probe['at']);data.append(out)
    atomic(folder/'european-daily-audit.json',data)
    s=status()
    dates=[d for d in pd.date_range('2026-11-02','2026-12-10').strftime('%Y-%m-%d') if is_session(d)][:20]
    safe_data=[{k:v for k,v in item.items() if k!='invalid_dates'} for item in data]
    report=dict(schema=1,checked_at=utcnow().isoformat(),status='NOT_READY_FOR_DEMO_TRADING',
        policy_hash=c['hash'],implementation_hash=c['implementation_hash'],orders_enabled=False,live_locked=True,
        broker=dict(real_demo_read_verified=s.get('broker',{}).get('evidence_kind')=='REAL_DEMO_REST' and s.get('broker',{}).get('connected') is True,
            reconciled=s.get('broker',{}).get('reconciled',False),status=s.get('broker',{}).get('status')),
        start_checks=s.get('readiness',{}),product_review=s.get('product_review',[]),european_daily_data=safe_data,
        independent_past_day_proof=json.loads((folder/'nasdaq-independent-past-day-proof.json').read_text()),
        public_product_page=dict(url='https://www.trading212.com/nl/trading-instruments/invest/QQQ3.IT',
            isin='IE00BLRPRL42',ticker='QQQ3m_EQ',currency='EUR',venue='Borsa Italiana',
            opened_in_safari=True,account_order_permissions_verified=False),
        demo_ticket_inspection=json.loads((folder/'qqq3-empty-ticket-observation.json').read_text()),
        execution_feed=dict(status='NO_VERIFIED_FRESH_BID_ASK_PROVIDER',required_max_age_seconds=2,
            trading212_public_api_quote_endpoint=False,borsa_italiana_public_book_delay_minutes=15,
            source='https://www.borsaitaliana.it/borsa/etc-etn/dettaglio.html?isin=IE00BLRPRL42&lang=it&mic=ETFP'),
        trial=dict(actual_sessions=s.get('trial',{}).get('qualified_sessions',0),required_sessions=20,
            theoretical_first_date_if_ready=dates[0],theoretical_twentieth_date_if_ready=dates[-1],
            next_order_ny=ny_stamp(dates[0],'09:31').isoformat(),next_order_nl=ny_stamp(dates[0],'09:31').astimezone(ZoneInfo('Europe/Amsterdam')).isoformat(),
            note='Theoretisch rooster, geen ingeplande order of begonnen proef'),
        costs=dict(new_purchases=0,new_paid_accounts=0),raw_prices_published=False,private_ledgers_published=False,
        baseline_research_changed=False)
    atomic(folder/'local-readiness-audit.json',report)
    # Publication has no account ID, balances, positions, orders or authentication values.
    atomic(ROOT/'research/trading212-readiness-verification-2026-10-30.json',report)
    print(json.dumps(dict(status=report['status'],products=len(data),actual_sessions=report['trial']['actual_sessions'],policy_hash=c['hash'])))


if __name__=='__main__':build()
