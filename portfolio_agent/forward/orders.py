"""Causal target planning and demo-only firewall. No LLM or web order endpoint."""
from datetime import timedelta
from decimal import ROUND_FLOOR,ROUND_CEILING
import json
from .common import dec,digest,stamp
from .broker import BrokerFailure
from .products import validate_binding,session_open
from .store import ACTIVE
from portfolio_agent.calendars import NY,next_session,stamp as ny_stamp


def plan_targets(advice,profile_weights,snapshot,bindings,quotes,previous,now,policy_hash):
    """Same target weights, monthly adds/state changes and paid cap trims.

    Quote-based demo execution is not claimed identical to auction-price fills.
    No unsettled future sale is spent. Existing unrelated positions block planning.
    """
    signal=advice['signal_day'];day=next_session(signal)
    due=ny_stamp(day,'09:31');now=stamp(now)
    if now<due:return dict(status='WAITING_FOR_EXECUTION_WINDOW',orders=[])
    if now>due+timedelta(minutes=5):return dict(status='EXECUTION_WINDOW_MISSED_NO_BACKFILL',orders=[])
    if advice['state_code']<0:return dict(status='DATA_HALT',orders=[])
    by_role={b['research_key']:b for b in bindings}
    if len(by_role)!=len(bindings) or not {'QQQ','TQQQ'}.issubset(by_role):return dict(status='PRODUCT_BINDINGS_PENDING',orders=[])
    tickers={b['ticker'] for b in bindings}
    positions=snapshot['positions']
    if any(p['instrument']['ticker'] not in tickers and dec(p['quantity'])!=0 for p in positions):return dict(status='UNMANAGED_ACCOUNT_POSITION',orders=[])
    if any(dec(p.get('quantityInPies',0))!=0 for p in positions):return dict(status='PIE_OWNERSHIP_NOT_SUPPORTED',orders=[])
    cash=dec(snapshot['account']['cash']['availableToTrade'])
    nav=dec(snapshot.get('strategy_nav',snapshot['account']['totalValue']));reserve=max(dec(10),nav/100)
    if nav<=0 or cash<0:return dict(status='INVALID_ACCOUNT_VALUE',orders=[])
    prior=previous.get('targets',{});month=previous.get('month')!=day[:7]
    output=[];waiting_cash=False
    for role,sleeve,field,w in [('QQQ','core','core_weight',profile_weights[0]),('TQQQ','trend','trend_weight',profile_weights[1])]:
        binding=by_role[role];ticker=binding['ticker'];quote=quotes.get(ticker)
        if not quote:return dict(status='FRESH_EXECUTION_QUOTE_MISSING',orders=[])
        ask,bid=dec(quote['ask']),dec(quote['bid']);lot=dec(binding['lot']);tick=dec(binding['price_tick'])
        if ask<=0 or bid<=0 or ask<bid or lot<=0 or tick<=0:return dict(status='INVALID_QUOTE_OR_LOT',orders=[])
        found=[p for p in positions if p['instrument']['ticker']==ticker]
        if len(found)>1:return dict(status='DUPLICATE_ACCOUNT_POSITION',orders=[])
        have=dec(found[0]['quantity']) if found else dec(0)
        available=dec(found[0]['quantityAvailableForTrading']) if found else dec(0)
        weight=dec(advice[field]);target=(nav-reserve)*weight
        if have*bid>target:
            quantity=-min(available,have-(target/bid/lot).to_integral_value(rounding=ROUND_FLOOR)*lot)
            price=(bid/tick).to_integral_value(rounding=ROUND_FLOOR)*tick
        elif month or prior.get(field)!=str(weight):
            amount=min(max(dec(0),target-have*ask),max(dec(0),cash-reserve))
            if amount<dec(binding['minimum_notional']) and target-have*ask>=dec(binding['minimum_notional']):waiting_cash=True
            # Leave a5bp friction reserve; actual quote cost is checked again below.
            price=(ask/tick).to_integral_value(rounding=ROUND_CEILING)*tick
            quantity=(amount/(price*dec('1.0005'))/lot).to_integral_value(rounding=ROUND_FLOOR)*lot
        else:continue
        if not quantity or abs(quantity)*price<dec(binding['minimum_notional']):continue
        identity=[str(snapshot['account']['id']),day,sleeve,ticker,'BUY' if quantity>0 else 'SELL','forward-v1']
        if digest(identity) in previous.get('attempted_ids',[]):continue
        if quantity>0:cash-=quantity*price*dec('1.0005')
        output.append(dict(id=digest(identity),signal_day=signal,day=day,sleeve=sleeve,ticker=ticker,
            research_key=role,quantity=str(quantity),limitPrice=str(price),currency=binding['currency'],
            policy_hash=policy_hash,account=str(snapshot['account']['id']),execute_at=due.isoformat(),
            expires_at=(due+timedelta(minutes=5)).isoformat(),created_at=now.isoformat()))
    output.sort(key=lambda p:dec(p['quantity'])>0)
    return dict(status='PLANNED' if output else 'WAITING_FOR_AVAILABLE_CASH' if waiting_cash else 'HOLD',orders=output,targets={k:str(advice[k]) for k in ('core_weight','trend_weight')},month=day[:7])


def authorize(c,intent,quote,snapshot,binding,store,now):
    now=stamp(now)
    if c['mode']!='DEMO' or not c['demo_orders_enabled']:raise ValueError('DEMO_ORDERS_NOT_ARMED')
    if c['s1_enabled'] or intent.get('sleeve') not in ('core','trend'):raise ValueError('S1_DISABLED')
    if c['hash']!=intent['policy_hash']:raise ValueError('POLICY_MISMATCH')
    if str(snapshot['account']['id'])!=intent['account']:raise ValueError('ACCOUNT_MISMATCH')
    if snapshot.get('environment')!='TRADING212_DEMO':raise ValueError('DEMO_ACCOUNT_EVIDENCE_REQUIRED')
    if dec(intent['quantity'])>0 and snapshot.get('independent_prices_current') is not True:raise ValueError('INDEPENDENT_DATA_CHECK_PENDING')
    if not 0<=(now-stamp(snapshot['observed_at'])).total_seconds()<=10:raise ValueError('ACCOUNT_SNAPSHOT_STALE')
    if not stamp(intent['execute_at'])<=now<=stamp(intent['expires_at']):raise ValueError('ORDER_WINDOW_CLOSED')
    if not 0<=(now-stamp(quote['observed_at'])).total_seconds()<=c['max_quote_age_seconds']:raise ValueError('QUOTE_STALE_OR_FUTURE')
    if quote.get('verified_execution_quote') is not True or quote.get('ticker')!=intent['ticker']:raise ValueError('EXECUTION_QUOTE_NOT_VERIFIED')
    if quote.get('synthetic') is not False:raise ValueError('SYNTHETIC_QUOTE_NOT_BROKER_EVIDENCE')
    item,schedule=validate_binding(binding,snapshot['instruments'],snapshot['account'],snapshot['exchanges'])
    if not session_open(schedule,now):raise ValueError('BROKER_MARKET_NOT_OPEN')
    bid,ask=dec(quote['bid']),dec(quote['ask']);qty,price=dec(intent['quantity']),dec(intent['limitPrice'])
    if bid<=0 or ask<bid or not qty or price<=0:raise ValueError('INVALID_QUOTE_OR_ORDER')
    if qty%dec(binding['lot']) or price%dec(binding['price_tick']):raise ValueError('LOT_OR_TICK_MISMATCH')
    if quote.get('currency')!=binding['currency']:raise ValueError('QUOTE_CURRENCY_MISMATCH')
    current_units=sum((dec(p['quantity']) for p in snapshot['positions'] if p['instrument']['ticker']==intent['ticker']),dec(0))
    if current_units+qty<0 or current_units+qty>dec(item['maxOpenQuantity']):raise ValueError('BROKER_QUANTITY_LIMIT')
    if abs(qty)*price>dec(c['max_order_value']):raise ValueError('DEMO_ORDER_VALUE_CAP')
    if abs(qty)*price<dec(binding['minimum_notional']):raise ValueError('BROKER_MINIMUM_NOTIONAL')
    if qty>0 and (store.unresolved() or store.get('halt')):raise ValueError('ORDER_OR_ACCOUNT_HALTED')
    if qty>0 and intent['sleeve']=='trend' and snapshot.get('risk_warning'):raise ValueError('DRAWDOWN_WARNING_3X_BLOCK')
    if any(p.get('instrument',{}).get('ticker')==intent['ticker'] and dec(p.get('quantityInPies',0)) for p in snapshot['positions']):raise ValueError('PIE_OWNERSHIP_NOT_SUPPORTED')
    if any((p.get('ticker') or p.get('instrument',{}).get('ticker'))==intent['ticker'] for p in snapshot['working_orders']):raise ValueError('EXISTING_BROKER_ORDER')
    if qty<0:
        available=sum((dec(p['quantityAvailableForTrading']) for p in snapshot['positions'] if p['instrument']['ticker']==intent['ticker']),dec(0))
        if abs(qty)>available:raise ValueError('OVERSELL')
        if price>bid or price<bid-dec(binding['price_tick']):raise ValueError('INVALID_EXIT_LIMIT')
    else:
        if (ask-bid)/((ask+bid)/2)*10000+dec(1)>dec(c['max_roundtrip_bp']):raise ValueError('FRICTION_GATE')
        if price<ask or price>ask+dec(binding['price_tick']):raise ValueError('INVALID_ENTRY_LIMIT')
        nav=dec(snapshot.get('strategy_nav',snapshot['account']['totalValue']));cash=dec(snapshot['account']['cash']['availableToTrade'])
        reserved=sum((abs(dec(json.loads(r['payload'])['quantity']))*dec(json.loads(r['payload'])['limitPrice']) for r in store.orders() if r['status'] in ACTIVE and dec(json.loads(r['payload'])['quantity'])>0),dec(0))
        if qty*price*dec('1.0005')+reserved>cash-max(dec(10),nav/100):raise ValueError('CASH_OR_RESERVE_LIMIT')
        # Every existing and working position counts towards the frozen profile cap.
        from portfolio_agent.regime import WEIGHTS
        cap=dec(WEIGHTS[c['profile']][0 if intent['sleeve']=='core' else 1])*(nav-max(dec(10),nav/100))
        held=sum((dec(p['quantity'])*ask for p in snapshot['positions'] if p['instrument']['ticker']==intent['ticker']),dec(0))
        pending=sum((abs(dec(json.loads(r['payload'])['quantity']))*price for r in store.orders() if r['status'] in ACTIVE and json.loads(r['payload'])['ticker']==intent['ticker'] and dec(json.loads(r['payload'])['quantity'])>0),dec(0))
        if held+pending+qty*price>cap:raise ValueError('PROFILE_EXPOSURE_CAP')
    return True


class DemoExecutor:
    def __init__(self,c,store,broker):self.c,self.store,self.broker=c,store,broker
    def send(self,intent,quote,snapshot,binding,now):
        existing=self.store.order(intent['id'])
        if existing:
            original=json.loads(existing['payload'])
            if any(original[k]!=intent[k] for k in ('ticker','quantity','limitPrice','policy_hash','execute_at','expires_at')):raise ValueError('EXISTING_DIFFERENT_INTENT_REQUIRES_REVIEW')
            return existing['status']
        authorize(self.c,intent,quote,snapshot,binding,self.store,now)
        if not self.store.claim(intent):return self.store.order(intent['id'])['status']
        try:
            response=self.broker.submit_limit(intent)
            self.store.acknowledge(intent['id'],response)
        except BrokerFailure as e:
            with self.store.transaction():
                if not e.ambiguous:
                    self.store.db.execute('UPDATE orders SET status="REJECTED" WHERE id=?',(intent['id'],))
                else:self.store.halt('UNKNOWN_DEMO_SEND_REQUIRES_REVIEW')
                self.store.event('DEMO_SEND_ERROR',dict(id=intent['id'],reason=e.code))
            raise
        except Exception:
            with self.store.transaction():self.store.halt('UNKNOWN_DEMO_ACK_REQUIRES_REVIEW')
            raise ValueError('UNKNOWN_DEMO_ACK_REQUIRES_REVIEW') from None
        return self.store.order(intent['id'])['status']

    def sync(self,id):
        row=self.store.order(id)
        if not row or not row['broker_id']:raise ValueError('UNIDENTIFIED_ORDER_REQUIRES_REVIEW')
        intent=json.loads(row['payload']);key='history:'+id;buffer=self.store.get(key,dict(items=[],cursor=None,seen=[]))
        items,next_=self.broker.history_page(intent['ticker'],buffer['cursor'])
        if next_ and (next_ in buffer['seen'] or len(buffer['seen'])>=20):raise ValueError('HISTORY_CURSOR_LOOP_OR_LIMIT')
        buffer['items'].extend(items)
        if next_:
            buffer['cursor']=next_;buffer['seen'].append(next_)
            with self.store.transaction():self.store.set(key,buffer)
            return 'HISTORY_PAGINATION_PENDING'
        try:order=self.broker.read('/equity/orders/'+row['broker_id'])
        except BrokerFailure as e:
            if e.code!='DEMO_HTTP_404':raise
            matches=[p['order'] for p in buffer['items'] if str(p.get('order',{}).get('id'))==row['broker_id']]
            if not matches:raise ValueError('ORDER_NOT_FOUND_IS_NOT_A_CANCEL')
            order=matches[-1]
        try:result=self.store.reconcile_order(id,order,buffer['items'])
        except ValueError:
            with self.store.transaction():self.store.halt('DEMO_RECONCILIATION_MISMATCH')
            raise
        with self.store.transaction():self.store.set(key,dict(items=[],cursor=None,seen=[]))
        return result

    def cancel(self,id):
        row=self.store.order(id)
        if not row or not row['broker_id']:raise ValueError('UNKNOWN_ORDER_CANNOT_CANCEL')
        if row['status'] in ('CANCELLED','FILLED','REJECTED'):return row['status']
        with self.store.transaction():self.store.db.execute('UPDATE orders SET status="CANCEL_UNKNOWN" WHERE id=?',(id,))
        try:self.broker.cancel(row['broker_id'])
        except Exception:
            with self.store.transaction():self.store.halt('UNKNOWN_CANCEL_REQUIRES_REVIEW')
            raise ValueError('UNKNOWN_CANCEL_REQUIRES_REVIEW') from None
        with self.store.transaction():self.store.db.execute('UPDATE orders SET status="CANCEL_REQUESTED" WHERE id=?',(id,))
        return 'CANCEL_REQUESTED'  # GET/history must confirm cancellation; late fills remain valid.
