"""Local forward observer; any broker capability remains demo-only and explicit."""
from datetime import timedelta
from pathlib import Path
import json
import os
import time
from .common import ROOT,atomic,config,digest,stamp,utcnow
from .store import Store,ACTIVE
from .market import acquire,decisions,expected_completed,parse_daily,confirm_sources
from .broker import Trading212Demo,BrokerFailure
from .products import CANDIDATES,validate_binding
from .orders import plan_targets,DemoExecutor
from .secrets import read_credentials
from .risk import update_risk
from .quotes import read_quotes
from .readiness import assess,products as review_products
from .history import sync as sync_cash_history
from portfolio_agent.regime import WEIGHTS
from portfolio_agent.calendars import NY,is_session,early_close,stamp as ny_stamp


def credentials_present(root):
    return all(read_credentials(root))


def load_cache(root,cache):
    import hashlib
    frames={}
    for source in cache['sources']:
        symbol=source['symbol']
        if symbol not in ('QQQ','TQQQ') or len(source['sha256'])!=64:raise ValueError('CACHE_METADATA_INVALID')
        p=root/'sources'/f"{symbol}-{source['sha256']}.json"
        raw=p.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=source['sha256']:raise ValueError('CACHE_HASH_MISMATCH')
        # A partial bar never becomes final merely because the wall clock advanced.
        frames[symbol]=parse_daily(json.loads(raw),stamp(source['available_at']))
    if set(frames)!={'QQQ','TQQQ'}:raise ValueError('CACHE_INCOMPLETE')
    return frames


def broker_snapshot(client,now,independent=False,metadata=None,store=None):
    account=client.read('/equity/account/summary')
    if not isinstance(account,dict) or not {'id','currency','cash','totalValue'}.issubset(account):raise ValueError('ACCOUNT_SCHEMA_INVALID')
    positions=client.read('/equity/positions');orders=client.read('/equity/orders')
    if not isinstance(positions,list) or not isinstance(orders,list):raise ValueError('BROKER_SNAPSHOT_SCHEMA_INVALID')
    catalog=metadata or dict(instruments=client.read('/equity/metadata/instruments'),exchanges=client.read('/equity/metadata/exchanges'))
    if store is not None:
        tx,tx_complete=sync_cash_history(client,store,'transactions');div,div_complete=sync_cash_history(client,store,'dividends')
    else:
        transactions=client.read('/equity/history/transactions?limit=50');dividends=client.read('/equity/history/dividends?limit=50')
        if not all(isinstance(v,dict) and isinstance(v.get('items'),list) for v in (transactions,dividends)):raise ValueError('CASH_HISTORY_SCHEMA_INVALID')
        tx,div=transactions['items'],dividends['items'];tx_complete=not transactions.get('nextPagePath');div_complete=not dividends.get('nextPagePath')
    return dict(environment='TRADING212_DEMO',account=account,positions=positions,working_orders=orders,
        instruments=catalog['instruments'],exchanges=catalog['exchanges'],observed_at=stamp(now).isoformat(),independent_prices_current=independent,
        transactions=tx,dividends=div,cash_history_complete=tx_complete and div_complete)


def account_reconciled(store,snapshot):
    """Dedicated empty demo origin; every later share must be explained by fills."""
    if any(p.get('quantityInPies',0) for p in snapshot['positions']):return False
    active_ids={r['broker_id'] for r in store.orders() if r['broker_id'] and r['status'] in ACTIVE}
    if any(str(o.get('id')) not in active_ids for o in snapshot['working_orders']):return False
    expected={}
    from .common import dec
    for row in store.orders():
        p=json.loads(row['payload']);signed=dec(1) if dec(p['quantity'])>0 else dec(-1)
        expected[p['ticker']]=expected.get(p['ticker'],dec(0))+signed*dec(row['filled'])
    actual={p['instrument']['ticker']:dec(p['quantity']) for p in snapshot['positions'] if dec(p['quantity'])}
    expected={k:v for k,v in expected.items() if v}
    if expected!=actual:return False
    # availableToTrade is not asserted to mean settled bankcash.
    cash=dec(snapshot['account']['cash']['availableToTrade'])+dec(snapshot['account']['cash'].get('reservedForOrders',0))
    if cash<0 or dec(snapshot['account']['totalValue'])<=0 or snapshot.get('cash_history_complete') is not True:return False
    events={}
    for event in snapshot.get('transactions',[]):
        if not event.get('reference'):return False
        key='TX:'+str(event['reference'])
        if key in events:return False
        events[key]=event
    for event in snapshot.get('dividends',[]):
        if not event.get('reference'):return False
        key='DIV:'+str(event['reference'])
        if key in events:return False
        events[key]=event
    base=store.get('cash_baseline')
    if base is None:
        if expected or store.orders():return False
        store.set('cash_baseline',dict(account=str(snapshot['account']['id']),currency=snapshot['account']['currency'],cash=str(cash),events=list(events)))
        return True
    if base['account']!=str(snapshot['account']['id']) or base['currency']!=snapshot['account']['currency']:return False
    expected_cash=dec(base['cash'])
    for row in store.orders():
        intent=json.loads(row['payload']);direction=-1 if dec(intent['quantity'])>0 else 1
        expected_cash+=direction*dec(row['notional'])-dec(row['fee'])
    known=store.get('cash_events',{})
    for key,e in events.items():
        if key in base['events']:continue
        if e.get('currency')!=base['currency']:return False
        if key in known:
            if known[key]['digest']!=digest(e):return False
            continue
        if key.startswith('DIV:'):value=dec(e['amount'])
        elif e.get('type')=='DEPOSIT':value=abs(dec(e['amount']))
        elif e.get('type') in ('WITHDRAW','FEE'):value=-abs(dec(e['amount']))
        elif e.get('type') in ('INTEREST_ON_FREE_CASH','LENDING_INTEREST'):value=dec(e['amount'])
        else:return False
        known[key]=dict(digest=digest(e),value=str(value),external_flow=str(value) if e.get('type') in ('DEPOSIT','WITHDRAW') and key.startswith('TX:') else None)
    expected_cash+=sum((dec(v['value']) for v in known.values()),dec(0))
    if abs(expected_cash-cash)>dec('.01'):return False
    store.set('cash_events',known)
    return True


def qualifying_session(store,c,snapshot,now,data_current,reconciled,execution_ready=False,final_account_ready=None):
    """Real demo connection across the full session; fast replays cannot score days."""
    local=now.astimezone(NY);day=local.date().isoformat()
    if not is_session(day):return
    key='coverage:'+day+':'+c['hash'];old=store.get(key)
    if old is None:old=dict(first=now.isoformat(),last=now.isoformat(),gap=False,invalid=False)
    start=ny_stamp(day,'09:20')
    cash_close=ny_stamp(day,'13:00' if early_close(day) else '16:00');close=cash_close+timedelta(minutes=10)
    # Pre-session source publication delays must not poison a future session;
    # every required in-session poll must pass all execution-readiness gates.
    if start<=now<=cash_close:
        if not data_current or not reconciled or not execution_ready:old['invalid']=True
        else:
            old['last_good_rth_poll']=now.isoformat()
            for sha in snapshot.get('signal_source_sha256',[]) if snapshot else []:
                if sha not in old.setdefault('signal_source_sha256',[]):old['signal_source_sha256'].append(sha)
    required_gap=(min(now,cash_close)-max(stamp(old['last']),start)).total_seconds()
    if required_gap>c['poll_seconds']*3:old['gap']=True
    old['last']=now.isoformat();store.set(key,old)
    covers_close=bool(old.get('last_good_rth_poll') and stamp(old['last_good_rth_poll'])>=cash_close-timedelta(seconds=3*c['poll_seconds']))
    complete=stamp(old['first'])<=start and now>=close and covers_close and not old['gap'] and not old.get('invalid',False)
    final_ok=execution_ready if final_account_ready is None else final_account_ready
    if complete and reconciled and final_ok:
        store.observe(day,c['hash'],'BROKER_DEMO_FORWARD',dict(day=day,observed_at=now.isoformat(),account_connected=True,
            reconciled=True,data_current=True,orders_known=not store.unresolved(),coverage_complete=True,
            implementation_hash=c.get('implementation_hash'),signal_source_sha256=old.get('signal_source_sha256',[])))


def tick(path=None,refresh=False,now=None,acquirer=acquire,client=None,confirmer=confirm_sources,probe_only=False):
    now=stamp(now or utcnow());c=config(path);root=ROOT/c['root'];root.mkdir(parents=True,exist_ok=True,mode=0o700)
    store=Store(root/'forward.sqlite3');injected_client=client is not None
    try:
        wanted=expected_completed(now);cache=store.get('market_cache');frames=None;error=None
        retry_at=store.get('market_retry_at')
        refresh_due=refresh or not cache or cache['day']!=wanted
        allowed_retry=not retry_at or now>=stamp(retry_at)
        if refresh_due and allowed_retry:
            try:
                frames,sources,confirmations=acquirer(now,root)
                advice=decisions(frames,now)
                cache=dict(day=wanted,sources=sources,confirmations=confirmations,secondary_checked_at=now.isoformat(),decisions=advice,acquired_at=now.isoformat())
                with store.transaction():store.set('market_cache',cache);store.set('market_retry_at',None);store.set('market_failures',0)
            except Exception as e:
                # Only fixed reason codes leave this boundary. Never serialize HTTP exceptions/headers.
                error=str(e) if isinstance(e,ValueError) and str(e).isupper() and len(str(e))<90 else 'MARKET_REFRESH_UNAVAILABLE'
                with store.transaction():
                    failures=store.get('market_failures',0)+1;store.set('market_failures',failures)
                    store.set('market_retry_at',(now+timedelta(seconds=min(3600,60*2**min(failures-1,6)))).isoformat())
                    store.alert(error,now.astimezone(NY).date().isoformat())
        if frames is None and cache:
            try:frames=load_cache(root,cache)
            except Exception:error='MARKET_CACHE_NOT_VERIFIED'
        data_current=bool(cache and cache['day']==wanted and frames is not None and not error)
        # Failure remains visible; valid advice from a prior cycle is not relabelled current.
        all_advice=decisions(frames,now) if data_current else {}
        confirmed=bool(cache and len(cache.get('confirmations',[]))==2 and {v.get('symbol') for v in cache['confirmations']}=={'QQQ','TQQQ'} and all(v.get('day')==wanted and v.get('status')=='MATCHED' for v in cache['confirmations']))
        if data_current and not confirmed:
            checked=cache.get('secondary_checked_at',cache['acquired_at'])
            if (now-stamp(checked)).total_seconds()>=900:
                cache['confirmations']=confirmer(frames,now,root);cache['secondary_checked_at']=now.isoformat()
                with store.transaction():store.set('market_cache',cache)
        independent=bool(data_current and len(cache.get('confirmations',[]))==2 and {v.get('symbol') for v in cache['confirmations']}=={'QQQ','TQQQ'} and all(v.get('day')==wanted and v.get('status')=='MATCHED' for v in cache['confirmations']))
        broker_status='DEMO_ACCOUNT_NOT_CONFIGURED';snapshot=None;planning=dict(status='WAITING_FOR_DEMO_ACCOUNT',orders=[]);risk=None;reconciled=False;quotes={};real_demo=False
        try:keys=read_credentials(root)
        except Exception:
            keys=('','');broker_status='DEMO_SECRET_FILE_PERMISSIONS_OR_SCHEMA_INVALID'
        if client or all(keys):
            try:
                client=client or Trading212Demo(*keys,allow_mutations=not probe_only and c['mode']=='DEMO' and c['demo_orders_enabled']);meta=store.get('broker_metadata')
                metadata=meta['value'] if meta and (now-stamp(meta['at'])).total_seconds()<3600 else None
                snapshot=broker_snapshot(client,now,independent,metadata,store)
                real_demo=not injected_client
                with store.transaction():
                    if metadata is None:store.set('broker_metadata',dict(at=now.isoformat(),value={k:snapshot[k] for k in ('instruments','exchanges')}))
                    store.set('private_broker_snapshot',snapshot)
                executor=DemoExecutor(c,store,client)
                for row in store.orders():
                    if row['status'] in ACTIVE and row['broker_id']:
                        executor.sync(row['id'])
                        row=store.order(row['id']);intent=json.loads(row['payload'])
                        if not probe_only and c['mode']=='DEMO' and c['demo_orders_enabled'] and row['status'] in ('ACKED','PARTIAL') and now>stamp(intent['expires_at']):executor.cancel(row['id'])
                reconciled=account_reconciled(store,snapshot)
                if not snapshot['cash_history_complete']:
                    broker_status='DEMO_CASH_HISTORY_PAGINATION_PENDING'
                elif not reconciled:
                    # A fill may race the non-atomic REST snapshots. Always block now;
                    # latch after two separate polls, rather than accepting inconsistent cash.
                    with store.transaction():
                        n=store.get('reconcile_failures',0)+1;store.set('reconcile_failures',n)
                        if n>=2:store.halt('DEMO_ACCOUNT_RECONCILIATION_REQUIRED')
                    broker_status='DEMO_RECONCILIATION_REQUIRED'
                else:
                    with store.transaction():
                        store.set('reconcile_failures',0)
                        risk=update_risk(store,c,snapshot)
                    broker_status='DEMO_READ_CONNECTED'
                if all_advice and reconciled:
                    quotes=read_quotes(root)
                    for b in c['bindings']:validate_binding(b,snapshot['instruments'],snapshot['account'],snapshot['exchanges'])
                    current=dict(all_advice[c['profile']])
                    if store.get('halt')=='DRAWDOWN_HUMAN_REVIEW_REQUIRED':current.update(core_weight='0',trend_weight='0')
                    previous=dict(store.get('executed_context',{}),attempted_ids=[r['id'] for r in store.orders()])
                    planning=plan_targets(current,WEIGHTS[c['profile']],snapshot,c['bindings'],quotes,
                        previous,now,c['hash'])
                    if not probe_only and c['mode']=='DEMO' and c['demo_orders_enabled']:
                        for intent in planning['orders']:
                            # Missing independent data blocks buys, not verified exits.
                            from .common import dec
                            if dec(intent['quantity'])>0 and not independent:continue
                            binding=next(b for b in c['bindings'] if b['ticker']==intent['ticker'])
                            executor.send(intent,quotes[intent['ticker']],snapshot,binding,utcnow() if client is not None else now)
                        # Do not mark a target executed until account reconciliation sees its fills.
                        if planning['status']=='HOLD' and not any(r['status'] in ACTIVE for r in store.orders()):
                            with store.transaction():store.set('executed_context',dict(targets=planning['targets'],month=planning['month']))
            except (ValueError,BrokerFailure) as e:
                broker_status=e.code if isinstance(e,BrokerFailure) else (str(e) if str(e).isupper() and len(str(e))<90 else 'DEMO_CHECK_FAILED')
                with store.transaction():store.alert(broker_status,now.astimezone(NY).date().isoformat())
            except Exception:
                broker_status='DEMO_CHECK_FAILED'
                with store.transaction():store.alert(broker_status,now.astimezone(NY).date().isoformat())
        market=dict(expected_day=wanted,source_day=cache['day'] if cache else None,status='CURRENT' if data_current else 'STALE_OR_UNAVAILABLE',error=error,independent_check='MATCHED' if independent else 'NOT_CONFIRMED')
        readiness=assess(c,market,snapshot,quotes,store,now,real_demo=real_demo,reconciled=reconciled)
        with store.transaction():
            final_ready=all(v['passed'] for v in readiness['checks'] if v['code'] not in ('DAILY_PRIMARY','DAILY_INDEPENDENT','EXECUTION_QUOTES'))
            coverage_snapshot=dict(snapshot or {},signal_source_sha256=[v['sha256'] for v in cache.get('sources',[])]) if cache else snapshot
            if not probe_only:qualifying_session(store,c,coverage_snapshot,now,data_current and independent,reconciled,readiness['observation_ready'],final_ready)
            if data_current:store.observe(now.astimezone(NY).date().isoformat(),c['hash'],'LIVE_ADVICE',dict(day=now.astimezone(NY).date().isoformat(),source_day=wanted,observed_at=now.isoformat()))
            if not data_current:store.alert(error or 'DAILY_DATA_STALE',now.astimezone(NY).date().isoformat())
            if data_current and not independent:store.alert('INDEPENDENT_SOURCE_NOT_CONFIRMED',now.astimezone(NY).date().isoformat())
        orders=store.orders();halt=store.get('halt');trial=store.trial(c['hash'])
        state=dict(schema=1,kind='LOCAL_FORWARD_ADVICE_NOT_LIVE_TRADING',checked_at=now.isoformat(),
            mode=c['mode'],live_locked=True,s1_enabled=False,profile=c['profile'],policy_hash=c['hash'],probe_only=probe_only,
            market=market,readiness=readiness,product_review=review_products(snapshot,wanted) if snapshot else [],
            profiles=all_advice,broker=dict(status=broker_status,connected=snapshot is not None,orders_enabled=c['demo_orders_enabled'] and not probe_only,
                bindings=len(c['bindings']),execution_status=planning['status'],evidence_kind='REAL_DEMO_REST' if real_demo else 'FIXTURE_OR_NOT_CONNECTED',reconciled=reconciled),
            orders=dict(total=len(orders),working=sum(r['status'] in ACTIVE for r in orders),unknown=sum(r['status'] in ('SENT_UNKNOWN','CANCEL_UNKNOWN') for r in orders),filled=sum(r['status']=='FILLED' for r in orders)),
            halt=halt,risk=risk,trial=trial,alert_count=store.db.execute('SELECT count(*) FROM alerts').fetchone()[0],
            last_good_refresh=cache['acquired_at'] if cache else None,next_retry=store.get('market_retry_at'),
            candidates=CANDIDATES,watch=dict(interval_seconds=c['poll_seconds'],local_mac_must_be_awake=True),
            blocker='; '.join(v['message'] for v in readiness['checks'] if not v['passed']),
            generated_by='forward-v1',publication='PRIVATE_LOCAL_ONLY')
        atomic(root/'status.json',state)
        return state
    finally:store.close()


def status(path=None,now=None):
    c=config(path);now=stamp(now or utcnow());p=ROOT/c['root']/'status.json'
    if not p.exists():return dict(schema=1,live_locked=True,mode=c['mode'],status='NOT_STARTED',trial=dict(qualified_sessions=0,required_sessions=20))
    body=json.loads(p.read_text());age=(now-stamp(body['checked_at'])).total_seconds()
    body['watch']['heartbeat_age_seconds']=max(0,int(age));body['watch']['heartbeat_status']='RECENT' if 0<=age<=3*c['poll_seconds'] else 'WATCHER_NOT_RECENT'
    return body


def public_readiness(path=None):
    """Public, dated evidence snapshot; never a remote broker control channel."""
    s=status(path);c=config(path);broker=s.get('broker',{});r=s.get('readiness',{})
    real=bool(s.get('policy_hash')==c['hash'] and s.get('watch',{}).get('heartbeat_status')=='RECENT' and broker.get('connected') is True and broker.get('evidence_kind')=='REAL_DEMO_REST')
    ready=bool(real and r.get('ready_to_start'))
    checks=[dict(code=v['code'],passed=bool(v['passed']),message=v['message']) for v in r.get('checks',[])]
    if not checks:
        checks=[dict(code='START_CHECKS_NOT_RUN',passed=False,message='Volledige startcontrole nog niet uitgevoerd')]
    blockers=[v['message'] for v in checks if not v['passed']]
    count=s.get('trial',{}).get('qualified_sessions',0) if real else 0
    if count<20:blockers.append('Twintig echte volledige demo-observatiedagen ontbreken')
    return dict(schema=1,kind='PUBLIC_SETUP_SNAPSHOT_NOT_A_LIVE_MAC_CONNECTION',published_at=utcnow().isoformat(),
        live_locked=True,mode=c['mode'],broker_target='Trading 212 demo',
        demo_account_verified=real,forward_trial=dict(qualified_sessions=count,required_sessions=20,status='WAITING_FOR_REAL_DEMO_OBSERVATIONS' if real else 'WAITING_FOR_DEMO_ACCOUNT'),
        market={k:s.get('market',{}).get(k) for k in ('status','source_day','expected_day','independent_check')},last_local_check=s.get('checked_at'),
        advice_preview={p:{k:v.get(k) for k in ('state','state_code','core_weight','trend_weight','signal_day')} for p,v in s.get('profiles',{}).items()},
        broker_status='DEMO_READ_VERIFIED_AT_PUBLICATION' if real else 'ACCOUNT_NOT_VERIFIED_AT_PUBLICATION',orders_enabled=c['demo_orders_enabled'],
        readiness=dict(status=r.get('status','NOT_READY_FOR_DEMO_TRADING'),ready_to_start=ready,checks=checks,blocker_codes=[v['code'] for v in checks if not v['passed']]),
        product_review=[{k:p.get(k) for k in ('ticker','isin','role','currency','legal_structure','issuer','catalog_identity_verified','account_currency_matches','next_execution_at_ny','next_execution_market_open','actual_fractional_permission_verified','actual_tick_size_verified','actual_minimum_notional_verified','historical_execution_parity_verified','backtest_performance_inherited','status')} for p in s.get('product_review',[])],
        steps=[dict(number=1,label='Productidentiteit',status='CATALOG_REVIEWED_BINDINGS_PENDING' if s.get('product_review') else 'ACCOUNT_CATALOG_PENDING'),
            dict(number=2,label='Dagelijkse lokale agent',status='BUILT_ADVICE_ONLY'),
            dict(number=3,label='Orderopslag en herstart',status='TESTED_WITH_FIXTURES_NOT_BROKER'),
            dict(number=4,label='Controlekamer',status='BUILT'),
            dict(number=5,label='Trading 212-demo',status='REAL_DEMO_READ_VERIFIED' if real else 'CLIENT_BUILT_ACCOUNT_NOT_CONNECTED'),
            dict(number=6,label='Twintig beursdagen proef',status='READY_TO_START' if ready else 'BLOCKED_BY_START_CHECKS')],
        blockers=blockers,
        note='Gedateerde publicatiestand. Een geverifieerde demolezing is geen ordervrijgave. Actuele heartbeat en privé-orderstatus staan alleen op je Mac.')


def watch(path=None,stop=None):
    """launchd restarts this read-only-by-default process; no missed-order catch-up."""
    c=config(path)
    while stop is None or not stop.is_set():
        try:tick(path)
        except Exception:
            # No credential-bearing traceback in unattended logs.
            root=ROOT/c['root'];atomic(root/'watch-error.json',dict(at=utcnow().isoformat(),reason='WATCH_CYCLE_FAILED'))
        if stop is not None:stop.wait(c['poll_seconds'])
        else:time.sleep(c['poll_seconds'])
