"""Persistent demo outbox: ambiguous sends stay blocked, also after restart."""
from contextlib import contextmanager
from pathlib import Path
import json
import os
import sqlite3
from .common import digest,dec

UNRESOLVED={'SENT_UNKNOWN','CANCEL_UNKNOWN'}
ACTIVE={'SENT_UNKNOWN','ACKED','PARTIAL','CANCEL_REQUESTED','CANCEL_UNKNOWN'}


class Store:
    def __init__(self,path):
        Path(path).parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.db=sqlite3.connect(path,timeout=10,isolation_level=None)
        self.db.row_factory=sqlite3.Row
        os.chmod(path,0o600)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS orders(id TEXT PRIMARY KEY,payload TEXT NOT NULL,status TEXT NOT NULL,broker_id TEXT UNIQUE,filled TEXT NOT NULL DEFAULT '0',notional TEXT NOT NULL DEFAULT '0',fee TEXT NOT NULL DEFAULT '0');
        CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY,kind TEXT NOT NULL,payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS observations(day TEXT NOT NULL,config_hash TEXT NOT NULL,kind TEXT NOT NULL,payload TEXT NOT NULL,PRIMARY KEY(day,config_hash,kind));
        CREATE TABLE IF NOT EXISTS alerts(id TEXT PRIMARY KEY,payload TEXT NOT NULL);
        ''')

    def close(self):self.db.close()

    @contextmanager
    def transaction(self):
        self.db.execute('BEGIN IMMEDIATE')
        try:yield;self.db.execute('COMMIT')
        except BaseException:self.db.execute('ROLLBACK');raise

    def get(self,key,default=None):
        row=self.db.execute('SELECT value FROM settings WHERE key=?',(key,)).fetchone()
        return json.loads(row[0]) if row else default

    def set(self,key,value):self.db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',(key,json.dumps(value,sort_keys=True,default=str)))
    def event(self,kind,payload):self.db.execute('INSERT INTO events(kind,payload) VALUES(?,?)',(kind,json.dumps(payload,sort_keys=True,default=str)))
    def order(self,id):
        row=self.db.execute('SELECT * FROM orders WHERE id=?',(id,)).fetchone()
        return dict(row) if row else None
    def orders(self):return [dict(r) for r in self.db.execute('SELECT * FROM orders ORDER BY rowid')]
    def unresolved(self):return any(r['status'] in UNRESOLVED for r in self.orders())
    def halt(self,reason):self.set('halt',reason)

    def claim(self,intent):
        """Commit before POST. Competing processes can send an identity at most once."""
        with self.transaction():
            row=self.order(intent['id']);body=json.dumps(intent,sort_keys=True)
            if row:
                if row['payload']!=body:raise ValueError('INTENT_COLLISION')
                return False
            if dec(intent['quantity'])>0 and (self.get('halt') or self.unresolved()):raise ValueError('UNRESOLVED_ORDER_OR_HALT')
            self.db.execute('INSERT INTO orders(id,payload,status) VALUES(?,?,?)',(intent['id'],body,'SENT_UNKNOWN'))
            self.event('DEMO_SEND_CLAIMED',dict(id=intent['id']))
        return True

    def acknowledge(self,id,response):
        with self.transaction():
            row=self.order(id)
            if not row or response.get('id') is None:raise ValueError('INVALID_DEMO_ACK')
            bid=str(response['id'])
            if not bid.isdigit():raise ValueError('INVALID_BROKER_ID')
            p=json.loads(row['payload']);signed=dec(p['quantity'])
            ticker=response.get('ticker') or response.get('instrument',{}).get('ticker')
            side=response.get('side', 'BUY' if dec(response.get('quantity',0))>0 else 'SELL')
            if ticker!=p['ticker'] or abs(dec(response.get('quantity',0)))!=abs(signed) or side!=('BUY' if signed>0 else 'SELL'):raise ValueError('DEMO_ACK_IDENTITY_MISMATCH')
            self.db.execute('UPDATE orders SET broker_id=?,status=? WHERE id=?',(bid,'ACKED',id))
            self.event('DEMO_ACK',dict(id=id,broker_id=bid))

    def reconcile_order(self,id,order,history):
        """Only immutable trade fills establish prices/fees; a POST ack is not a fill."""
        with self.transaction():
            row=self.order(id)
            if not row or not row['broker_id']:raise ValueError('UNIDENTIFIED_ORDER_REQUIRES_REVIEW')
            intent=json.loads(row['payload']);wanted=abs(dec(intent['quantity']));qty=dec(0);notional=dec(0);fee=dec(0);seen={}
            if order and str(order.get('id'))!=row['broker_id']:raise ValueError('RECONCILIATION_ORDER_ID_MISMATCH')
            for candidate in ([order] if order else [])+[h.get('order',{}) for h in history if str(h.get('order',{}).get('id'))==row['broker_id']]:
                ticker=candidate.get('ticker') or candidate.get('instrument',{}).get('ticker')
                if ticker is not None and ticker!=intent['ticker']:raise ValueError('RECONCILIATION_TICKER_MISMATCH')
                if candidate.get('side') is not None and candidate['side']!=('BUY' if dec(intent['quantity'])>0 else 'SELL'):raise ValueError('RECONCILIATION_SIDE_MISMATCH')
            for item in history:
                o=item.get('order',{});fill=item.get('fill')
                if str(o.get('id'))!=row['broker_id'] or not fill:continue
                if fill.get('type')!='TRADE':raise ValueError('CORPORATE_ACTION_RECONCILIATION_REQUIRED')
                key=str(fill.get('id'));finger=digest(fill)
                if key in seen:
                    if seen[key]!=finger:raise ValueError('CONFLICTING_DUPLICATE_FILL')
                    continue
                seen[key]=finger;q=abs(dec(fill['quantity']));price=dec(fill['price'])
                if q<=0 or price<=0:raise ValueError('INVALID_FILL')
                limit=dec(intent['limitPrice'])
                if (dec(intent['quantity'])>0 and price>limit) or (dec(intent['quantity'])<0 and price<limit):raise ValueError('LIMIT_FILL_VIOLATION')
                qty+=q;notional+=q*price
                for tax in fill.get('walletImpact',{}).get('taxes',[]):
                    if tax.get('currency') not in (None,intent['currency']):raise ValueError('FEE_CURRENCY_UNVERIFIED')
                    fee+=abs(dec(tax.get('quantity',tax.get('amount',0))))
            if qty>wanted or qty<dec(row['filled']):raise ValueError('OVERFILL_OR_HISTORY_INCOMPLETE')
            status=order.get('status') if order else None
            reported=abs(dec(order.get('filledQuantity',0))) if order else qty
            if reported!=qty:raise ValueError('FILL_PRICE_HISTORY_INCOMPLETE')
            if qty==wanted:target='FILLED'
            elif status in ('CANCELLED','REJECTED'):target=status
            elif status in ('CANCELLING',):target='CANCEL_REQUESTED'
            elif status in ('NEW','CONFIRMED','UNCONFIRMED','LOCAL','PARTIALLY_FILLED'):target='PARTIAL' if qty else 'ACKED'
            else:raise ValueError('BROKER_ORDER_STATUS_UNRESOLVED')
            self.db.execute('UPDATE orders SET status=?,filled=?,notional=?,fee=? WHERE id=?',(target,str(qty),str(notional),str(fee),id))
            self.event('DEMO_RECONCILED',dict(id=id,status=target,filled=str(qty)))
            return target

    def observe(self,day,policy,kind,payload):
        if kind not in ('LIVE_ADVICE','BROKER_DEMO_FORWARD','HISTORICAL_FIXTURE'):raise ValueError('INVALID_OBSERVATION_KIND')
        self.db.execute('INSERT OR IGNORE INTO observations VALUES(?,?,?,?)',(day,policy,kind,json.dumps(payload,sort_keys=True,default=str)))

    def alert(self,reason,day):
        id=digest([reason,day])
        self.db.execute('INSERT OR IGNORE INTO alerts VALUES(?,?)',(id,json.dumps(dict(reason=reason,day=day))))

    def trial(self,policy):
        rows=[json.loads(r[0]) for r in self.db.execute('SELECT payload FROM observations WHERE config_hash=? AND kind="BROKER_DEMO_FORWARD"',(policy,))]
        valid=[r for r in rows if r.get('account_connected') is True and r.get('reconciled') is True and r.get('data_current') is True and r.get('orders_known') is True and r.get('coverage_complete') is True]
        dates=sorted({r['day'] for r in valid})
        return dict(required_sessions=20,qualified_sessions=len(dates),dates=dates,
            status='TECHNICAL_OBSERVATION_COMPLETE_NOT_PROFIT_PROOF' if len(dates)>=20 else 'WAITING_FOR_REAL_DEMO_OBSERVATIONS')
