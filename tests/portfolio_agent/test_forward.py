"""Forward advice, demo protocol, outage recovery and honest observation evidence."""
from copy import deepcopy
from datetime import datetime,timedelta,timezone
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import hashlib,json,os,threading
import numpy as np
import pandas as pd
import pytest
import requests

from portfolio_agent.forward.common import config,ROOT,atomic,atomic_bytes,dec,digest
from portfolio_agent.forward.market import expected_completed,parse_daily,decisions
from portfolio_agent.forward.agent import load_cache,account_reconciled,qualifying_session
from portfolio_agent.forward.broker import BASE,Trading212Demo,BrokerFailure
from portfolio_agent.forward.store import Store
from portfolio_agent.forward.orders import plan_targets,authorize,DemoExecutor
from portfolio_agent.forward.products import validate_binding,session_open
from portfolio_agent.forward.secrets import read_credentials
from portfolio_agent.signal_engine import features
from portfolio_agent.agent_advisor import advise
from portfolio_agent.calendars import NY,is_session,stamp as ny_stamp


def now():return ny_stamp('2026-10-30','09:31').astimezone(timezone.utc)


def policy(tmp_path):
    body=json.loads((ROOT/'config/portfolio-forward.json').read_text());body.update(mode='DEMO',demo_orders_enabled=True,account_currency='USD',max_order_value='1000')
    path=tmp_path/'c.json';path.write_text(json.dumps(body));return config(path)


def binding(role='QQQ'):
    return dict(research_key=role,ticker=role+'_US_EQ',isin='TEST_ISIN_'+role,currency='USD',schedule_id=1,lot='0.000001',price_tick='.01',minimum_notional='1',
        history_validated=True,session_validated=True,structure_verified=True,account_permission_verified=True)


def snapshot():
    return dict(environment='TRADING212_DEMO',observed_at=now().isoformat(),independent_prices_current=True,
        account=dict(id=123,currency='USD',cash=dict(availableToTrade=1000,reservedForOrders=0),totalValue=1000),positions=[],working_orders=[],transactions=[],dividends=[],cash_history_complete=True,
        instruments=[dict(ticker=binding(r)['ticker'],isin=binding(r)['isin'],currencyCode='USD',type='ETF',maxOpenQuantity=10000,workingScheduleId=1) for r in ('QQQ','TQQQ')],
        exchanges=[dict(id=1,workingSchedules=[dict(id=1,timeEvents=[dict(date=ny_stamp('2026-10-30','09:30').isoformat(),type='OPEN'),dict(date=ny_stamp('2026-10-30','16:00').isoformat(),type='CLOSE')])])])


def quote(role='QQQ'):
    return dict(ticker=role+'_US_EQ',observed_at=now().isoformat(),bid='99.99',ask='100',currency='USD',synthetic=False,verified_execution_quote=True)


def intent(c):
    return dict(id='a'*64,signal_day='2026-10-29',day='2026-10-30',sleeve='core',research_key='QQQ',ticker='QQQ_US_EQ',quantity='1',limitPrice='100',currency='USD',policy_hash=c['hash'],account='123',
        execute_at=now().isoformat(),expires_at=(now()+timedelta(minutes=5)).isoformat(),created_at=now().isoformat())


def market_fixture(end='2026-10-30'):
    days=[d for d in pd.date_range('2018-01-01',end).strftime('%Y-%m-%d') if is_session(d)]
    c=100+np.arange(len(days))*.05+np.sin(np.arange(len(days))*.03)
    timestamps=[int(ny_stamp(d,'09:30').timestamp()) for d in days]
    quote_=dict(open=(c-.2).tolist(),high=(c+1).tolist(),low=(c-1).tolist(),close=c.tolist(),volume=[1000]*len(days))
    return dict(chart=dict(result=[dict(meta=dict(currency='USD'),timestamp=timestamps,indicators=dict(quote=[quote_]))],error=None))


@pytest.mark.parametrize('time,expected',[
    ('2026-10-30T19:59:00+00:00','2026-10-29'),('2026-10-30T20:09:59+00:00','2026-10-29'),
    ('2026-10-30T20:10:00+00:00','2026-10-30'),('2026-11-02T21:10:00+00:00','2026-11-02'),
    ('2026-11-27T18:10:00+00:00','2026-11-27'),('2026-11-26T22:00:00+00:00','2026-11-25')])
def test_completion_clock_handles_dst_holidays_and_early_closes(time,expected):assert expected_completed(datetime.fromisoformat(time))==expected


def test_cached_partial_bar_never_becomes_a_final_bar(tmp_path):
    body=market_fixture();raw=json.dumps(body).encode();sha=hashlib.sha256(raw).hexdigest()
    at=datetime.fromisoformat('2026-10-30T17:00:00+00:00');sources=[]
    for s in ('QQQ','TQQQ'):
        atomic_bytes(tmp_path/'sources'/f'{s}-{sha}.json',raw)
        sources.append(dict(symbol=s,sha256=sha,available_at=at.isoformat()))
    frames=load_cache(tmp_path,dict(sources=sources))
    assert frames['QQQ'].index[-1]=='2026-10-29'
    with pytest.raises(ValueError,match='DAILY_DATA_STALE'):decisions(frames,datetime.fromisoformat('2026-10-30T22:00:00+00:00'))


def test_signal_parity_and_future_truncation():
    body=market_fixture();at=now();frame=parse_daily(body,at);frames={'QQQ':frame,'TQQQ':frame.copy()}
    d=decisions(frames,at)
    for profile in ('defensive','balanced','offensive'):
        expected=advise(frame.close.iloc[-1],features(frame).iloc[-1],frame.close.iloc[-1],features(frame).iloc[-1],profile)
        assert d[profile]['core_weight']==expected['core_weight'] and d[profile]['trend_weight']==expected['trend_weight']
    # Poison only the uncompleted current bar; it cannot affect completed inputs.
    body['chart']['result'][0]['indicators']['quote'][0]['high'][-1]=1e9
    other=parse_daily(body,at);pd.testing.assert_frame_equal(frame,other)


@pytest.mark.parametrize('bad',['duplicate','missing','nan','negative','currency'])
def test_bad_vendor_inputs_block(bad):
    body=market_fixture();r=body['chart']['result'][0]
    if bad=='duplicate':r['timestamp'][500]=r['timestamp'][499]
    if bad=='missing':
        del r['timestamp'][500]
        for values in r['indicators']['quote'][0].values():del values[500]
    if bad=='nan':r['indicators']['quote'][0]['close'][500]=None
    if bad=='negative':r['indicators']['quote'][0]['low'][500]=-1
    if bad=='currency':r['meta']['currency']='GBP'
    with pytest.raises(ValueError):parse_daily(body,now())


@pytest.mark.parametrize('bad',['isin','currency','schedule','history','type'])
def test_product_identity_and_no_automatic_etf_substitution(bad):
    b=binding();s=snapshot()
    if bad=='isin':s['instruments'][0]['isin']='OTHER_ISIN'
    if bad=='currency':s['account']['currency']='EUR'
    if bad=='schedule':b['schedule_id']=2
    if bad=='history':b['history_validated']=False
    if bad=='type':s['instruments'][0]['type']='WARRANT'
    with pytest.raises(ValueError):validate_binding(b,s['instruments'],s['account'],s['exchanges'])


@pytest.mark.parametrize('bad',['mode','policy','account','stale_quote','future_quote','synthetic','spread','cash','lots','tick','value','source','window','exposure'])
def test_demo_firewall_rejects_every_risk_bypass(tmp_path,bad):
    c=policy(tmp_path);i=intent(c);q=quote();s=snapshot();b=binding();store=Store(tmp_path/'j.db')
    try:
        if bad=='mode':c['mode']='ADVICE_ONLY'
        if bad=='policy':i['policy_hash']='wrong'
        if bad=='account':i['account']='real'
        if bad=='stale_quote':q['observed_at']=(now()-timedelta(seconds=3)).isoformat()
        if bad=='future_quote':q['observed_at']=(now()+timedelta(seconds=1)).isoformat()
        if bad=='synthetic':q['synthetic']=True
        if bad=='spread':q['bid']='98'
        if bad=='cash':s['account']['cash']['availableToTrade']=100
        if bad=='lots':i['quantity']='1.0000001'
        if bad=='tick':i['limitPrice']='100.001'
        if bad=='value':c['max_order_value']='50'
        if bad=='source':s['independent_prices_current']=False
        if bad=='window':i['expires_at']=(now()-timedelta(seconds=1)).isoformat()
        if bad=='exposure':i['quantity']='5'
        with pytest.raises(ValueError):authorize(c,i,q,s,b,store,now())
        assert store.orders()==[]
    finally:store.close()


def test_causal_monthly_planner_does_not_spend_future_sale_proceeds(tmp_path):
    c=policy(tmp_path);s=snapshot();advice=dict(signal_day='2026-10-29',state_code=2,core_weight='.5',trend_weight='0')
    args=(advice,(.5,0,.25,.25),s,[binding(),binding('TQQQ')],{'QQQ_US_EQ':quote(),'TQQQ_US_EQ':quote('TQQQ')},{},now(),c['hash'])
    p=plan_targets(*args);assert p['status']=='PLANNED' and len(p['orders'])==1
    assert dec(p['orders'][0]['quantity'])*100<=495
    before=list(args);before[-2]=now()-timedelta(minutes=1)
    assert plan_targets(*before)['status']=='WAITING_FOR_EXECUTION_WINDOW'
    late=list(args);late[-2]=now()+timedelta(minutes=6)
    assert plan_targets(*late)['status']=='EXECUTION_WINDOW_MISSED_NO_BACKFILL'
    s['account']['cash']['availableToTrade']=10;s['positions']=[dict(instrument=dict(ticker='TQQQ_US_EQ'),quantity=1,quantityAvailableForTrading=1,quantityInPies=0)]
    assert not any(dec(i['quantity'])>0 for i in plan_targets(*args)['orders'])


class Response:
    def __init__(self,status,body):self.status_code=status;self.body=body
    def json(self):return self.body


class MemoryTransport:
    def __init__(self,status=200):self.calls=[];self.status=status
    def request(self,method,url,**kwargs):
        self.calls.append((method,url,kwargs))
        if self.status=='timeout':raise requests.Timeout('NEVER_PRINT_THIS_SECRET')
        if method=='POST':return Response(self.status,dict(id=901,ticker='QQQ_US_EQ',quantity=1,side='BUY',status='NEW'))
        return Response(self.status,{})


def test_demo_only_host_no_redirect_and_rate_limit(tmp_path):
    for bad in ['https://live.trading212.com/api/v0',BASE+'/',BASE+'@evil.example']:
        with pytest.raises(ValueError):Trading212Demo('test','secret',base_url=bad)
    tr=MemoryTransport();client=Trading212Demo('test','secret',transport=tr,clock=lambda:100)
    client.read('/equity/account/summary')
    assert tr.calls[0][2]['allow_redirects'] is False
    with pytest.raises(BrokerFailure,match='RATE_LIMITED'):client.read('/equity/account/summary')
    for bad in ['https://evil.example','/equity/orders/1?x=y','/../equity/orders','/equity/pies']:
        with pytest.raises(ValueError):client.read(bad)
    with pytest.raises(ValueError):client.cancel('1/../../live')


def test_unknown_post_survives_restart_and_is_never_retried(tmp_path):
    c=policy(tmp_path);tr=MemoryTransport('timeout');client=Trading212Demo('test','secret',transport=tr)
    store=Store(tmp_path/'j.db');i=intent(c)
    with pytest.raises(BrokerFailure):DemoExecutor(c,store,client).send(i,quote(),snapshot(),binding(),now())
    assert store.order(i['id'])['status']=='SENT_UNKNOWN';store.close()
    store=Store(tmp_path/'j.db')
    try:
        assert DemoExecutor(c,store,client).send(i,quote(),snapshot(),binding(),now())=='SENT_UNKNOWN'
        assert len(tr.calls)==1 and store.get('halt')=='UNKNOWN_DEMO_SEND_REQUIRES_REVIEW'
        assert 'NEVER_PRINT_THIS_SECRET' not in '\n'.join(r[0] for r in store.db.execute('SELECT payload FROM events'))
    finally:store.close()


@pytest.mark.parametrize('status,expected',[(400,'REJECTED'),(401,'REJECTED'),(429,'SENT_UNKNOWN'),(503,'SENT_UNKNOWN'),(302,'SENT_UNKNOWN')])
def test_http_error_semantics(tmp_path,status,expected):
    c=policy(tmp_path);tr=MemoryTransport(status);client=Trading212Demo('test','secret',transport=tr);store=Store(tmp_path/'j.db');i=intent(c)
    try:
        with pytest.raises(BrokerFailure):DemoExecutor(c,store,client).send(i,quote(),snapshot(),binding(),now())
        assert store.order(i['id'])['status']==expected and len(tr.calls)==1
    finally:store.close()


def test_cancel_ack_is_not_cancelled_and_late_fill_is_valid(tmp_path):
    c=policy(tmp_path);i=intent(c);tr=MemoryTransport();client=Trading212Demo('test','secret',transport=tr);store=Store(tmp_path/'j.db');e=DemoExecutor(c,store,client)
    try:
        assert e.send(i,quote(),snapshot(),binding(),now())=='ACKED'
        assert e.cancel(i['id'])=='CANCEL_REQUESTED'
        assert store.order(i['id'])['filled']=='0'
        order=dict(id=901,status='FILLED',filledQuantity=1)
        fill=dict(id=1,type='TRADE',quantity=1,price=100,walletImpact=dict(taxes=[]))
        assert store.reconcile_order(i['id'],order,[dict(order=order,fill=fill)])=='FILLED'
        assert store.order(i['id'])['notional']=='100'
        assert e.cancel(i['id'])=='FILLED'
    finally:store.close()


def test_partial_fill_duplicate_conflict_and_cash_reconciliation(tmp_path):
    c=policy(tmp_path);i=intent(c);s=snapshot();store=Store(tmp_path/'j.db')
    try:
        assert account_reconciled(store,s)
        store.claim(i);store.acknowledge(i['id'],dict(id=901,ticker='QQQ_US_EQ',quantity=1,side='BUY'))
        order=dict(id=901,status='PARTIALLY_FILLED',filledQuantity=.5)
        fill=dict(id=2,type='TRADE',quantity=.5,price=100,walletImpact=dict(taxes=[dict(currency='USD',quantity=.1)]))
        item=dict(order=order,fill=fill)
        assert store.reconcile_order(i['id'],order,[item,item])=='PARTIAL'
        s['account']['cash']['availableToTrade']=949.9;s['positions']=[dict(instrument=dict(ticker='QQQ_US_EQ'),quantity=.5,quantityInPies=0)]
        assert account_reconciled(store,s)
        s['account']['cash']['availableToTrade']=950
        assert not account_reconciled(store,s)
        bad=deepcopy(item);bad['fill']['price']=99
        with pytest.raises(ValueError,match='CONFLICTING_DUPLICATE'):store.reconcile_order(i['id'],order,[item,bad])
    finally:store.close()


def test_observation_counter_never_counts_fixtures_duplicates_or_incomplete_days(tmp_path):
    s=Store(tmp_path/'j.db')
    try:
        for day in pd.bdate_range('2026-01-01',periods=30).strftime('%Y-%m-%d'):
            s.observe(day,'p','HISTORICAL_FIXTURE',dict(day=day,account_connected=True,reconciled=True,data_current=True,orders_known=True,coverage_complete=True))
        assert s.trial('p')['qualified_sessions']==0
        s.observe('2026-10-29','p','BROKER_DEMO_FORWARD',dict(day='2026-10-29',account_connected=True,reconciled=True,data_current=True,orders_known=True))
        assert s.trial('p')['qualified_sessions']==0
        valid=dict(day='2026-10-30',account_connected=True,reconciled=True,data_current=True,orders_known=True,coverage_complete=True)
        s.observe('2026-10-30','p','BROKER_DEMO_FORWARD',valid);s.observe('2026-10-30','p','BROKER_DEMO_FORWARD',valid)
        assert s.trial('p')['qualified_sessions']==1 and s.trial('different-policy')['qualified_sessions']==0
    finally:s.close()


def test_full_session_and_sleep_gap_cannot_fake_a_qualified_day(tmp_path):
    c=policy(tmp_path);s=Store(tmp_path/'j.db');day='2026-10-30'
    try:
        # Connected only at close is insufficient.
        qualifying_session(s,c,{},ny_stamp(day,'16:10'),True,True)
        assert s.trial(c['hash'])['qualified_sessions']==0
        s.db.execute('DELETE FROM settings')
        qualifying_session(s,c,{},ny_stamp(day,'09:20'),True,True)
        qualifying_session(s,c,{},ny_stamp(day,'16:10'),True,True)
        assert s.trial(c['hash'])['qualified_sessions']==0
    finally:s.close()


def test_credentials_owner_only_and_no_environment_leak(tmp_path,monkeypatch):
    monkeypatch.delenv('QUANT_T212_DEMO_KEY',raising=False);monkeypatch.delenv('QUANT_T212_DEMO_SECRET',raising=False)
    assert read_credentials(tmp_path)==('','')
    p=tmp_path/'demo-credentials.json';atomic(p,dict(key='fixture-only',secret='not-a-real-key'))
    assert read_credentials(tmp_path)==('fixture-only','not-a-real-key')
    p.chmod(0o644)
    with pytest.raises(ValueError,match='PERMISSIONS'):read_credentials(tmp_path)


def test_actual_loopback_rest_protocol_and_no_ack_fill_assumption(tmp_path):
    seen=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*_):pass
        def do_POST(self):
            body=json.loads(self.rfile.read(int(self.headers['Content-Length'])));seen.append(body)
            assert self.path=='/api/v0/equity/orders/limit'
            payload=json.dumps(dict(id=901,ticker=body['ticker'],quantity=body['quantity'],side='BUY',status='NEW',filledQuantity=0)).encode()
            self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(payload)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    class LocalTransport:
        def request(self,method,url,**kwargs):
            assert url.startswith(BASE+'/')
            return requests.request(method,'http://127.0.0.1:'+str(server.server_port)+url.removeprefix('https://demo.trading212.com'),**kwargs)
    c=policy(tmp_path);s=Store(tmp_path/'j.db')
    try:
        e=DemoExecutor(c,s,Trading212Demo('dummy','dummy',transport=LocalTransport()));i=intent(c)
        assert e.send(i,quote(),snapshot(),binding(),now())=='ACKED'
        assert e.send(i,quote(),snapshot(),binding(),now())=='ACKED'
        assert len(seen)==1 and seen[0]==dict(ticker='QQQ_US_EQ',quantity=1.,limitPrice=100.,timeValidity='DAY')
        assert s.order(i['id'])['filled']=='0'
    finally:s.close();server.shutdown();server.server_close();thread.join()


def test_existing_identity_cannot_change_its_order_payload(tmp_path):
    c=policy(tmp_path);i=intent(c);tr=MemoryTransport();s=Store(tmp_path/'j.db')
    try:
        e=DemoExecutor(c,s,Trading212Demo('x','y',transport=tr));e.send(i,quote(),snapshot(),binding(),now())
        other=dict(i,quantity='2')
        with pytest.raises(ValueError,match='DIFFERENT_INTENT'):e.send(other,quote(),snapshot(),binding(),now())
        assert len(tr.calls)==1
    finally:s.close()


def test_confirmed_risk_reducing_sell_is_not_blocked_by_buy_circuit(tmp_path):
    c=policy(tmp_path);i=intent(c);i.update(quantity='-1',limitPrice='99.99');s=snapshot()
    s['positions']=[dict(instrument=dict(ticker='QQQ_US_EQ'),quantity=1,quantityAvailableForTrading=1,quantityInPies=0)]
    s['independent_prices_current']=False;store=Store(tmp_path/'j.db')
    try:
        store.halt('DRAWDOWN_HUMAN_REVIEW_REQUIRED')
        assert authorize(c,i,quote(),s,binding(),store,now())
        assert store.claim(i)
    finally:store.close()


def test_planner_respects_allocated_capital_not_full_demo_funds(tmp_path):
    c=policy(tmp_path);s=snapshot();s['account']['totalValue']=50000;s['account']['cash']['availableToTrade']=50000;s['strategy_nav']='1000'
    a=dict(signal_day='2026-10-29',state_code=2,core_weight='.5',trend_weight='0')
    p=plan_targets(a,(.5,0,.25,.25),s,[binding(),binding('TQQQ')],{'QQQ_US_EQ':quote(),'TQQQ_US_EQ':quote('TQQQ')},{},now(),c['hash'])
    assert len(p['orders'])==1 and dec(p['orders'][0]['quantity'])*100<=495
    previous=dict(attempted_ids=[p['orders'][0]['id']])
    assert not plan_targets(a,(.5,0,.25,.25),s,[binding(),binding('TQQQ')],{'QQQ_US_EQ':quote(),'TQQQ_US_EQ':quote('TQQQ')},previous,now(),c['hash'])['orders']


def test_risk_units_ignore_deposits_and_track_allocated_loss(tmp_path):
    from portfolio_agent.forward.risk import update_risk
    c=policy(tmp_path);s=snapshot();s['account']['totalValue']=50000;s['account']['cash']['availableToTrade']=50000;store=Store(tmp_path/'j.db')
    try:
        assert account_reconciled(store,s)
        assert update_risk(store,c,s)['drawdown_pct']==0 and s['strategy_nav']=='1000'
        s['account']['totalValue']=50100;s['account']['cash']['availableToTrade']=50100
        s['transactions']=[dict(reference='d1',currency='USD',type='DEPOSIT',amount=100)]
        assert account_reconciled(store,s)
        assert update_risk(store,c,s)['drawdown_pct']==0
        s['account']['totalValue']=49900
        r=update_risk(store,c,s)
        assert r['drawdown_pct']==pytest.approx(100*(1-900/1100)) and r['halt']
        assert store.get('halt')=='DRAWDOWN_HUMAN_REVIEW_REQUIRED'
    finally:store.close()


def test_history_pagination_is_persistent_and_cursor_confined(tmp_path):
    class T:
        def __init__(self):self.n=0
        def request(self,method,url,**kwargs):
            self.n+=1
            return Response(200,dict(items=[],nextPagePath='/api/v0/equity/history/orders?cursor=2') if self.n==1 else dict(items=[],nextPagePath=None))
    clock=[100.];client=Trading212Demo('x','y',transport=T(),clock=lambda:clock[0])
    _,cursor=client.history_page('QQQ_US_EQ');assert cursor=='/equity/history/orders?cursor=2'
    clock[0]+=5
    assert client.history_page('QQQ_US_EQ',cursor)==([],None)
    with pytest.raises(BrokerFailure,match='CURSOR'):client.history_page('QQQ_US_EQ','https://evil.example')


def test_secret_file_and_readiness_cannot_leak_account_payloads(tmp_path,monkeypatch):
    import portfolio_agent.forward.agent as a
    from portfolio_agent.forward.common import config as load
    path=tmp_path/'config.json';raw=json.loads((ROOT/'config/portfolio-forward.json').read_text());path.write_text(json.dumps(raw))
    monkeypatch.setattr(a,'ROOT',tmp_path)
    root=tmp_path/raw['root'];root.mkdir(parents=True)
    # A synthetic private status includes material the public publisher must ignore.
    private=dict(schema=1,live_locked=True,mode='ADVICE_ONLY',checked_at=now().isoformat(),watch=dict(interval_seconds=60),market=dict(status='CURRENT'),
        account_id='NEVER_PUBLIC',secret='NEVER_PUBLIC',positions=[dict(quantity=123)],broker=dict(connected=True))
    atomic(root/'status.json',private)
    out=a.public_readiness(path)
    assert 'NEVER_PUBLIC' not in json.dumps(out) and out['orders_enabled'] is False
    assert out['forward_trial']['qualified_sessions']==0 and out['demo_account_verified'] is False


def test_service_plist_has_no_secrets_and_only_advice_mode(tmp_path,monkeypatch):
    import portfolio_agent.forward.service as service
    raw=json.loads((ROOT/'config/portfolio-forward.json').read_text());p=tmp_path/'c.json';p.write_text(json.dumps(raw));monkeypatch.setattr(service,'ROOT',tmp_path)
    file=service.render(p);text=file.read_text()
    assert 'RunAtLoad' in text and 'KeepAlive' in text and '<string>watch</string>' in text
    assert 'QUANT_T212_DEMO_KEY' not in text and 'secret' not in text
    raw.update(mode='DEMO',demo_orders_enabled=True);p.write_text(json.dumps(raw))
    with pytest.raises(ValueError,match='ONLY_ADVICE'):service.render(p)


def test_execution_quotes_require_private_file_and_provenance(tmp_path):
    from portfolio_agent.forward.quotes import read_quotes
    assert read_quotes(tmp_path)=={}
    q=dict(quote(),provider='TEST_ONLY',source_sha256='a'*64)
    p=tmp_path/'execution-quotes.json';atomic(p,dict(schema=1,quotes={'QQQ_US_EQ':q}))
    assert read_quotes(tmp_path)['QQQ_US_EQ']['provider']=='TEST_ONLY'
    p.chmod(0o644)
    with pytest.raises(ValueError,match='PERMISSIONS'):read_quotes(tmp_path)


def test_wrong_vendor_symbol_never_enters_cache(tmp_path):
    from portfolio_agent.forward.market import fetch_yahoo
    class WrongVendor:
        def get(self,*args,**kwargs):
            body=market_fixture();body['chart']['result'][0]['meta']['symbol']='SPY'
            return Response(200,body)
    with pytest.raises(ValueError,match='SYMBOL_MISMATCH'):fetch_yahoo('QQQ',now(),tmp_path,WrongVendor())
    assert not (tmp_path/'sources').exists()


@pytest.mark.parametrize('bad',['id','ticker','side'])
def test_reconciliation_cannot_attach_another_order(tmp_path,bad):
    c=policy(tmp_path);i=intent(c);s=Store(tmp_path/'j.db')
    try:
        s.claim(i);s.acknowledge(i['id'],dict(id=901,ticker=i['ticker'],quantity=1,side='BUY'))
        order=dict(id=901,ticker=i['ticker'],side='BUY',status='NEW',filledQuantity=0)
        order[bad]={'id':902,'ticker':'WRONG','side':'SELL'}[bad]
        with pytest.raises(ValueError,match='MISMATCH'):s.reconcile_order(i['id'],order,[])
        assert s.order(i['id'])['status']=='ACKED'
    finally:s.close()


def test_bad_mid_session_data_cannot_be_hidden_by_good_closing_poll(tmp_path):
    c=policy(tmp_path);s=Store(tmp_path/'j.db');day='2026-10-30'
    try:
        start=ny_stamp(day,'09:20')
        for minute in range(411):
            qualifying_session(s,c,{},start+timedelta(minutes=minute),minute!=100,True)
        assert s.trial(c['hash'])['qualified_sessions']==0
    finally:s.close()


def test_actual_tick_advice_restart_reuses_verified_cache_without_any_orders(tmp_path,monkeypatch):
    from portfolio_agent.forward import agent
    monkeypatch.setattr(agent,'ROOT',tmp_path)
    monkeypatch.delenv('QUANT_T212_DEMO_KEY',raising=False);monkeypatch.delenv('QUANT_T212_DEMO_SECRET',raising=False)
    body=json.loads((ROOT/'config/portfolio-forward.json').read_text());p=tmp_path/'policy.json';p.write_text(json.dumps(body));calls=[]
    def source(at,root):
        calls.append(at);frames={};sources=[];confirmations=[]
        for symbol in ('QQQ','TQQQ'):
            raw_body=market_fixture();raw_body['chart']['result'][0]['meta']['symbol']=symbol
            raw=json.dumps(raw_body).encode();sha=hashlib.sha256(raw).hexdigest();atomic_bytes(root/'sources'/f'{symbol}-{sha}.json',raw)
            frames[symbol]=parse_daily(raw_body,at);sources.append(dict(symbol=symbol,sha256=sha,available_at=at.isoformat()))
            confirmations.append(dict(symbol=symbol,status='MATCHED'))
        return frames,sources,confirmations
    first=agent.tick(p,now=now(),acquirer=source)
    second=agent.tick(p,now=now()+timedelta(seconds=60),acquirer=source)
    assert len(calls)==1 and first['profiles']==second['profiles']
    assert second['market']['status']=='CURRENT' and second['broker']['orders_enabled'] is False
    assert second['orders']==dict(total=0,working=0,unknown=0,filled=0)
    assert second['trial']['qualified_sessions']==0
