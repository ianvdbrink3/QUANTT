"""Release checks must fail on missing evidence and recover on real publication."""
from copy import deepcopy
from datetime import timedelta
import json,hashlib
import pytest
from test_forward import policy,snapshot,binding,quote,now,market_fixture,Response,MemoryTransport,intent
from portfolio_agent.forward.common import ROOT,atomic_bytes,atomic,config,digest
from portfolio_agent.forward.market import parse_nasdaq,confirm_sources,parse_daily
from portfolio_agent.forward.readiness import assess,products
from portfolio_agent.forward.history import sync
from portfolio_agent.forward.store import Store
from portfolio_agent.forward.products import quantity_step
from portfolio_agent.forward.orders import authorize
from portfolio_agent.forward.broker import Trading212Demo,BrokerFailure
from portfolio_agent.forward.agent import qualifying_session,account_reconciled
from portfolio_agent.calendars import stamp as ny_stamp


def nasdaq(day='10/29/2026',symbol='QQQ',close='100.00'):
    return dict(status=dict(rCode=200),data=dict(symbol=symbol,tradesTable=dict(rows=[dict(date=day,close=close)])))


@pytest.mark.parametrize('case',['yesterday','duplicate','symbol','status','nonfinite','negative'])
def test_nasdaq_exact_closed_day_symbol_and_unique_finite_price(case):
    b=nasdaq();day='2026-10-29'
    if case=='yesterday':day='2026-10-30'
    if case=='duplicate':b['data']['tradesTable']['rows']*=2
    if case=='symbol':b['data']['symbol']='SPY'
    if case=='status':b['status']['rCode']=400
    if case=='nonfinite':b['data']['tradesTable']['rows'][0]['close']='nan'
    if case=='negative':b['data']['tradesTable']['rows'][0]['close']='-1'
    with pytest.raises(ValueError):parse_nasdaq(b,'QQQ',day)
    assert parse_nasdaq(nasdaq(close='$1,234.50'),'QQQ','2026-10-29')==1234.5


def test_independent_price_conflict_cannot_be_selected_away(tmp_path):
    frame=parse_daily(market_fixture(),now());frames={'QQQ':frame,'TQQQ':frame}
    def source(symbol,day,at,root):return (float(frame.close.iloc[-1])*(1.01 if symbol=='QQQ' else 1),'a'*64)
    rows=confirm_sources(frames,now(),tmp_path,source)
    assert [r['status'] for r in rows]==['PRICE_CONFLICT','MATCHED']


def test_late_secondary_publication_retries_without_rewriting_primary(tmp_path,monkeypatch):
    from portfolio_agent.forward import agent
    monkeypatch.setattr(agent,'ROOT',tmp_path)
    monkeypatch.delenv('QUANT_T212_DEMO_KEY',raising=False);monkeypatch.delenv('QUANT_T212_DEMO_SECRET',raising=False)
    raw=json.loads((ROOT/'config/portfolio-forward.json').read_text());p=tmp_path/'c.json';p.write_text(json.dumps(raw));calls=[]
    def acquire(at,root):
        calls.append('PRIMARY');frames={};sources=[]
        for symbol in ('QQQ','TQQQ'):
            body=market_fixture();buf=json.dumps(body).encode();sha=hashlib.sha256(buf).hexdigest();atomic_bytes(root/'sources'/f'{symbol}-{sha}.json',buf)
            frames[symbol]=parse_daily(body,at);sources.append(dict(symbol=symbol,sha256=sha,available_at=at.isoformat()))
        return frames,sources,[dict(symbol=s,day='2026-10-29',status='UNAVAILABLE') for s in frames]
    def confirm(frames,at,root):
        calls.append('SECONDARY');return [dict(symbol=s,day='2026-10-29',status='MATCHED',sha256='a'*64) for s in frames]
    first=agent.tick(p,now=now(),acquirer=acquire,confirmer=confirm)
    root=tmp_path/raw['root'];before={f.name:f.read_bytes() for f in (root/'sources').glob('*')}
    second=agent.tick(p,now=now()+timedelta(minutes=16),acquirer=acquire,confirmer=confirm)
    assert first['market']['independent_check']=='NOT_CONFIRMED'
    assert second['market']['independent_check']=='MATCHED' and calls==['PRIMARY','SECONDARY']
    assert before=={f.name:f.read_bytes() for f in (root/'sources').glob('*')}
    assert second['trial']['qualified_sessions']==0 and second['orders']['total']==0


def full_check(tmp_path):
    c=policy(tmp_path);c['bindings']=[binding(),binding('TQQQ')];s=snapshot();q={x['ticker']:dict(quote(x['research_key']),provider='TEST_FIXTURE',source_sha256='a'*64) for x in c['bindings']}
    return c,s,q,Store(tmp_path/'j.db')


@pytest.mark.parametrize('case',['unverified_broker','unarmed','independent','identity','quote','halt','reconciliation'])
def test_every_release_dependency_is_mandatory(tmp_path,case):
    c,s,q,store=full_check(tmp_path);market=dict(status='CURRENT',independent_check='MATCHED',source_day='2026-10-29');real=True;reconciled=True
    try:
        if case=='unverified_broker':real=False
        if case=='unarmed':c['mode']='ADVICE_ONLY';c['demo_orders_enabled']=False
        if case=='independent':market['independent_check']='NOT_CONFIRMED'
        if case=='identity':c['bindings'][0]['isin']='WRONG'
        if case=='quote':q={}
        if case=='halt':store.halt('REVIEW_REQUIRED')
        if case=='reconciliation':reconciled=False
        r=assess(c,market,s,q,store,now(),real_demo=real,reconciled=reconciled)
        assert not r['ready_to_start'] and r['blocker_codes'] and not r['observation_ready']
    finally:store.close()


def test_execution_quotes_not_required_after_close_but_mandatory_at_order_time(tmp_path):
    c,s,q,store=full_check(tmp_path)
    try:
        market=dict(status='CURRENT',independent_check='MATCHED',source_day='2026-10-29')
        assert assess(c,market,s,q,store,now(),real_demo=True,reconciled=True)['ready_to_start']
        assert not assess(c,market,s,{},store,now(),real_demo=True,reconciled=True)['observation_ready']
        at=ny_stamp('2026-10-30','16:10');s['observed_at']=at.isoformat();market['source_day']='2026-10-30'
        r=assess(c,market,s,{},store,at,real_demo=True,reconciled=True)
        assert r['observation_ready'] and not r['quote_required_now'] and not r['ready_to_start']
    finally:store.close()


def test_readonly_rest_client_rejects_mutations_even_with_broad_api_rights():
    tr=MemoryTransport();client=Trading212Demo('dummy','dummy',transport=tr,allow_mutations=False)
    with pytest.raises(BrokerFailure,match='READ_ONLY'):client.submit_limit(dict(ticker='QQQ_US_EQ',quantity=1,limitPrice=100))
    with pytest.raises(BrokerFailure,match='READ_ONLY'):client.cancel('901')
    assert tr.calls==[]


def transaction(ref,day,amount=1):return dict(reference=ref,dateTime=day,currency='USD',type='DEPOSIT',amount=amount)


class Pages:
    def __init__(self,values):self.values=list(values);self.paths=[]
    def read(self,path):self.paths.append(path);return self.values.pop(0)


def test_cash_pagination_survives_restart_and_verified_archive_rejoins_head(tmp_path):
    first=transaction('new','2026-10-30T10:00:00Z');last=transaction('old','2026-10-29T10:00:00Z')
    p=Pages([dict(items=[first],nextPagePath='/api/v0/equity/history/transactions?cursor=2')]);store=Store(tmp_path/'j.db')
    assert sync(p,store,'transactions')==([],False);store.close()
    store=Store(tmp_path/'j.db')
    try:
        p=Pages([dict(items=[last],nextPagePath=None)])
        rows,complete=sync(p,store,'transactions');assert complete and {v['reference'] for v in rows}=={'new','old'}
        assert p.paths==['/equity/history/transactions?cursor=2']
        newer=transaction('newer','2026-10-30T11:00:00Z');p=Pages([dict(items=[newer,first],nextPagePath='/api/v0/equity/history/transactions?cursor=already-known-tail')])
        rows,complete=sync(p,store,'transactions');assert complete and len(rows)==3
        # Rewritten cash events cannot silently change the established archive.
        p=Pages([dict(items=[dict(first,amount=999)],nextPagePath=None)])
        with pytest.raises(ValueError,match='CONFLICT'):sync(p,store,'transactions')
    finally:store.close()


@pytest.mark.parametrize('cursor',['https://evil.example/key','/api/v0/equity/history/orders?cursor=2','/api/v0/equity/history/transactions?cursor=2&url=secret'])
def test_cash_cursor_cannot_escape_its_read_only_endpoint(tmp_path,cursor):
    s=Store(tmp_path/'j.db')
    try:
        p=Pages([dict(items=[transaction('x','2026-10-30T10:00:00Z')],nextPagePath=cursor)])
        with pytest.raises(ValueError,match='CURSOR'):sync(p,s,'transactions')
    finally:s.close()


@pytest.mark.parametrize('price,step',[('.09','1'),('.1','.1'),('1','.01'),('10','.001'),('100','.0001'),('1000','.00001'),('10000','.000001'),('100000','.0000001')])
def test_quantity_precision_matches_published_price_bands(price,step):assert quantity_step(price)==__import__('decimal').Decimal(step)


def test_nominal_millionth_lot_cannot_bypass_current_price_band(tmp_path):
    c=policy(tmp_path);s=Store(tmp_path/'j.db');i=intent(c);i['quantity']='1.00001'
    try:
        with pytest.raises(ValueError,match='LOT_OR_TICK'):authorize(c,i,quote(),snapshot(),binding(),s,now())
    finally:s.close()


def test_overnight_sleep_does_not_poison_an_otherwise_full_future_session(tmp_path):
    c=policy(tmp_path);s=Store(tmp_path/'j.db');day='2026-10-30'
    try:
        qualifying_session(s,c,{},ny_stamp(day,'01:00'),False,False,False)
        qualifying_session(s,c,{},ny_stamp(day,'09:19'),True,True,True)
        for m in range(411):qualifying_session(s,c,{},ny_stamp(day,'09:20')+timedelta(minutes=m),True,True,True)
        assert s.trial(c['hash'])['qualified_sessions']==1
    finally:s.close()


def test_connected_unconfigured_account_cannot_score_twenty_good_days(tmp_path):
    c=policy(tmp_path);s=Store(tmp_path/'j.db');day='2026-10-30'
    try:
        for m in range(411):qualifying_session(s,c,{},ny_stamp(day,'09:20')+timedelta(minutes=m),True,True,False)
        assert s.trial(c['hash'])['qualified_sessions']==0
    finally:s.close()


def test_interest_is_income_not_an_external_capital_contribution(tmp_path):
    s=Store(tmp_path/'j.db');b=snapshot()
    try:
        assert account_reconciled(s,b)
        b['account']['cash']['availableToTrade']=1001;b['account']['totalValue']=1001
        b['transactions']=[dict(reference='interest',type='INTEREST_ON_FREE_CASH',amount=1,currency='USD')]
        assert account_reconciled(s,b)
        assert s.get('cash_events')['TX:interest']['external_flow'] is None
    finally:s.close()


def test_broker_etf_label_does_not_hide_legal_etp_structure():
    s=snapshot();s['account']['currency']='EUR';s['instruments']=[dict(ticker='QQQ3m_EQ',isin='IE00BLRPRL42',currencyCode='EUR',type='ETF',workingScheduleId=75)]
    p=next(p for p in products(s,'2026-10-30') if p['ticker']=='QQQ3m_EQ')
    assert p['catalog_identity_verified'] and p['legal_structure']=='COLLATERALISED_SWAP_DEBT_ETP_NOT_TQQQ'
    assert p['backtest_performance_inherited'] is False and p['actual_fractional_permission_verified'] is False


def test_late_next_session_input_publication_does_not_erase_a_good_previous_session(tmp_path):
    c=policy(tmp_path);s=Store(tmp_path/'j.db');day='2026-10-30'
    try:
        for m in range(401):qualifying_session(s,c,{'signal_source_sha256':['a'*64]},ny_stamp(day,'09:20')+timedelta(minutes=m),True,True,True)
        # At16:10 the next day's inputs may still lack independent confirmation.
        qualifying_session(s,c,{},ny_stamp(day,'16:10'),False,True,False,True)
        assert s.trial(c['hash'])['qualified_sessions']==1
        row=s.db.execute('SELECT payload FROM observations').fetchone()[0]
        assert json.loads(row)['signal_source_sha256']==['a'*64]
    finally:s.close()


def test_missing_closing_coverage_cannot_be_hidden_by_late_success(tmp_path):
    c=policy(tmp_path);s=Store(tmp_path/'j.db');day='2026-10-30'
    try:
        for m in range(390):qualifying_session(s,c,{},ny_stamp(day,'09:20')+timedelta(minutes=m),True,True,True)
        qualifying_session(s,c,{},ny_stamp(day,'16:10'),True,True,True,True)
        assert s.trial(c['hash'])['qualified_sessions']==0
    finally:s.close()


def test_reused_metadata_does_not_extend_its_own_expiration(tmp_path,monkeypatch):
    from portfolio_agent.forward import agent
    monkeypatch.setattr(agent,'ROOT',tmp_path)
    monkeypatch.delenv('QUANT_T212_DEMO_KEY',raising=False);monkeypatch.delenv('QUANT_T212_DEMO_SECRET',raising=False)
    raw=json.loads((ROOT/'config/portfolio-forward.json').read_text());p=tmp_path/'c.json';p.write_text(json.dumps(raw));calls=[];fixture=snapshot()
    class ReadClient:
        def read(self,path):
            calls.append(path)
            if path=='/equity/account/summary':return fixture['account']
            if path=='/equity/positions':return []
            if path=='/equity/orders':return []
            if path=='/equity/metadata/instruments':return fixture['instruments']
            if path=='/equity/metadata/exchanges':return fixture['exchanges']
            if path.startswith('/equity/history/'):return dict(items=[],nextPagePath=None)
            raise AssertionError(path)
    def acquire(at,root):
        frames={};sources=[]
        for symbol in ('QQQ','TQQQ'):
            body=market_fixture();buf=json.dumps(body).encode();sha=hashlib.sha256(buf).hexdigest();atomic_bytes(root/'sources'/f'{symbol}-{sha}.json',buf)
            frames[symbol]=parse_daily(body,at);sources.append(dict(symbol=symbol,sha256=sha,available_at=at.isoformat()))
        return frames,sources,[dict(symbol=s,day='2026-10-29',status='MATCHED') for s in frames]
    client=ReadClient()
    for dt in (0,60,3601):agent.tick(p,now=now()+timedelta(seconds=dt),acquirer=acquire,client=client)
    assert calls.count('/equity/metadata/instruments')==2 and calls.count('/equity/metadata/exchanges')==2
    store=Store(tmp_path/raw['root']/'forward.sqlite3')
    try:assert store.trial(config(p)['hash'])['qualified_sessions']==0
    finally:store.close()


def test_code_version_is_part_of_the_observation_policy():
    c=config()
    assert len(c['implementation_hash'])==64
    body={k:v for k,v in c.items() if k!='hash'}
    assert digest(body)==c['hash']
    assert digest(dict(body,implementation_hash='0'*64))!=c['hash']


def test_product_source_audit_distinguishes_nan_from_incoherent_ohlc():
    from scripts.audit_trading212_readiness import audit_daily
    b=market_fixture();r=b['chart']['result'][0];r['meta'].update(symbol='EQQQ.MI',currency='EUR',fullExchangeName='Milan',exchangeTimezoneName='Europe/Rome')
    # One missing bar and a distinct closing price outside a valid positive range.
    r['indicators']['quote'][0]['open'][500]=None
    r['indicators']['quote'][0]['high'][600]=r['indicators']['quote'][0]['low'][600]-.1
    a=audit_daily(b)
    assert a['missing_or_nonfinite_bars']==1 and a['ohlc_inconsistent_bars']==1 and a['invalid_total']==2
    assert a['historical_performance_inherited'] is False


def test_nasdaq_request_uses_nonzero_iso_range_but_only_accepts_requested_day(tmp_path):
    from portfolio_agent.forward.market import fetch_nasdaq
    class Vendor:
        def get(self,url,**kwargs):
            assert kwargs['params']['fromdate']=='2026-10-22'
            assert kwargs['params']['todate']=='2026-10-30'
            assert kwargs['allow_redirects'] is False
            body=nasdaq();r=Response(200,body);r.content=json.dumps(body).encode();return r
    price,sha=fetch_nasdaq('QQQ','2026-10-29',now(),tmp_path,Vendor())
    assert price==100 and len(sha)==64
    assert list((tmp_path/'sources').glob('Nasdaq-QQQ-*.json'))


def test_preflight_probe_cannot_send_or_score_even_if_config_is_armed(tmp_path,monkeypatch):
    from portfolio_agent.forward import agent
    monkeypatch.setattr(agent,'ROOT',tmp_path)
    monkeypatch.delenv('QUANT_T212_DEMO_KEY',raising=False);monkeypatch.delenv('QUANT_T212_DEMO_SECRET',raising=False)
    raw=json.loads((ROOT/'config/portfolio-forward.json').read_text());raw.update(mode='DEMO',demo_orders_enabled=True,account_currency='USD',bindings=[binding(),binding('TQQQ')])
    p=tmp_path/'c.json';p.write_text(json.dumps(raw));fixture=snapshot()
    monkeypatch.setattr(agent,'broker_snapshot',lambda *args,**kwargs:deepcopy(fixture))
    quotes={b['ticker']:dict(quote(b['research_key']),provider='FIXTURE_ONLY',source_sha256='a'*64) for b in raw['bindings']}
    monkeypatch.setattr(agent,'read_quotes',lambda root:quotes)
    frame=parse_daily(market_fixture(),now())
    def acquire(at,root):return {'QQQ':frame,'TQQQ':frame},[],[dict(symbol=s,day='2026-10-29',status='MATCHED') for s in ('QQQ','TQQQ')]
    transport=MemoryTransport();client=Trading212Demo('dummy','dummy',transport=transport)
    out=agent.tick(p,now=now(),client=client,acquirer=acquire,probe_only=True)
    assert out['probe_only'] and out['broker']['orders_enabled'] is False and transport.calls==[] and out['orders']['total']==0
    store=Store(tmp_path/raw['root']/'forward.sqlite3')
    try:
        assert store.db.execute('SELECT count(*) FROM observations WHERE kind="BROKER_DEMO_FORWARD"').fetchone()[0]==0
        assert store.get('coverage:2026-10-30:'+config(p)['hash']) is None
    finally:store.close()
