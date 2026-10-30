"""Evidence-based start checks. A connected account is not an execution release."""
from datetime import timedelta
from .common import stamp,dec
from .products import validate_binding,session_open
from portfolio_agent.calendars import next_session,stamp as ny_stamp

# Legal structure is verified independently of the broker's broad "ETF" label.
PRODUCT_REVIEW={
 'EQQQm_EQ':dict(role='QQQ',isin='IE0032077012',currency='EUR',schedule=75,structure='UCITS_DISTRIBUTING_ETF',issuer='https://www.invesco.com/uk/en/financial-products/etfs/invesco-eqqq-nasdaq-100-ucits-etf-dist.html',history_symbol='EQQQ.MI'),
 'XNASd_EQ':dict(role='QQQ',isin='IE00BMFKG444',currency='EUR',schedule=166,structure='UCITS_ACCUMULATING_ETF',issuer='https://etf.dws.com/en-gb/IE00BMFKG444-nasdaq-100-ucits-etf-1c/',history_symbol='XNAS.DE'),
 'QQQ3m_EQ':dict(role='TQQQ',isin='IE00BLRPRL42',currency='EUR',schedule=75,structure='COLLATERALISED_SWAP_DEBT_ETP_NOT_TQQQ',issuer='https://www.wisdomtree.eu/en-ie/etps/equities/wisdomtree-nasdaq-100-3x-daily-leveraged',history_symbol='QQQ3.MI')}


def products(snapshot,signal_day):
    out=[];due=ny_stamp(next_session(signal_day),'09:31')
    for ticker,r in PRODUCT_REVIEW.items():
        matches=[i for i in snapshot.get('instruments',[]) if i.get('ticker')==ticker]
        item=matches[0] if len(matches)==1 else {}
        schedules=[s for e in snapshot.get('exchanges',[]) for s in e.get('workingSchedules',[]) if s.get('id')==r['schedule']]
        schedule=schedules[0] if len(schedules)==1 else {}
        identity=bool(item and item.get('isin')==r['isin'] and item.get('currencyCode')==r['currency'] and item.get('workingScheduleId')==r['schedule'])
        out.append(dict(ticker=ticker,isin=r['isin'],role=r['role'],currency=r['currency'],legal_structure=r['structure'],issuer=r['issuer'],
            catalog_identity_verified=identity,account_currency_matches=snapshot.get('account',{}).get('currency')==r['currency'],
            next_execution_at_ny=due.isoformat(),next_execution_market_open=session_open(schedule,due),
            actual_fractional_permission_verified=False,actual_tick_size_verified=False,actual_minimum_notional_verified=False,
            historical_execution_parity_verified=False,backtest_performance_inherited=False,
            status='CATALOG_AND_ISSUER_REVIEWED_NOT_ORDER_APPROVED' if identity else 'NOT_VERIFIED'))
    return out


def assess(c,market,snapshot,quotes,store,now,*,real_demo=False,reconciled=False):
    """Always enumerate blockers, including outside the narrow order window."""
    now=stamp(now);checks=[]
    def add(code,ok,message):checks.append(dict(code=code,passed=bool(ok),message=message))
    fresh=bool(snapshot and 0<=(now-stamp(snapshot['observed_at'])).total_seconds()<=15)
    add('DEMO_ACCOUNT',real_demo and fresh,'Echte demo-authenticatie en actuele rekeningcontrole')
    add('DAILY_PRIMARY',market.get('status')=='CURRENT','Voltooide US-dagdata en volledige indicatoropwarming')
    add('DAILY_INDEPENDENT',market.get('independent_check')=='MATCHED','Dezelfde slotdatum onafhankelijk bevestigd')
    add('ACCOUNT_RECONCILIATION',fresh and reconciled,'Posities, orders en cash sluiten aan')
    roles={b.get('research_key') for b in c['bindings']}
    valid=bool(snapshot and roles=={'QQQ','TQQQ'} and len(c['bindings'])==2)
    if valid:
        try:
            for b in c['bindings']:validate_binding(b,snapshot['instruments'],snapshot['account'],snapshot['exchanges'])
        except (ValueError,KeyError,TypeError):valid=False
    add('PRODUCT_BINDINGS',valid,'Exacte producten, valuta, fracties, prijstik, minimum en producthistorie bevestigd')
    quote_ok=valid
    for b in c['bindings']:
        try:
            q=quotes[b['ticker']];age=(now-stamp(q['observed_at'])).total_seconds()
            ok=q.get('verified_execution_quote') is True and q.get('synthetic') is False and q.get('ticker')==b['ticker'] and q.get('currency')==b['currency'] and 0<=age<=c['max_quote_age_seconds']
            ok=ok and dec(q['bid'])>0 and dec(q['ask'])>=dec(q['bid']) and bool(q.get('provider')) and len(q.get('source_sha256',''))==64
            quote_ok=quote_ok and ok
        except (KeyError,TypeError,ValueError):quote_ok=False
    add('EXECUTION_QUOTES',quote_ok,'Werkelijke bid/ask-feed met herkomst, juiste notering en maximaal twee seconden oud')
    add('PERSISTENT_ORDER_STATE',not store.unresolved() and not store.get('halt'),'Geen onzekere orders of blijvende risicoblokkade')
    add('BROKER_AUTOMATION_POLICY',False,'Trading 212 verbiedt algoritmische handel via de API; toepassing op demo en eigen interface moet de broker verduidelijken')
    add('DEMO_RELEASE',False,'Er is geen vrijgegeven route voor automatische demo-orders bij Trading 212')
    technical=all(v['passed'] for v in checks if v['code']!='DEMO_RELEASE')
    ready=all(v['passed'] for v in checks)
    # Quotes are mandatory during the actual order window and while orders work.
    # After a reference exchange closes, an old quote is not itself a failed day.
    from .store import ACTIVE
    day=market.get('source_day');due=ny_stamp(next_session(day),'09:31') if day else None
    quote_required=bool(due and due<=now<=due+timedelta(minutes=5)) or any(o['status'] in ACTIVE for o in store.orders())
    observation_ready=all(v['passed'] for v in checks if v['code']!='EXECUTION_QUOTES') and (quote_ok or not quote_required)
    return dict(status='READY_FOR_DEMO_OBSERVATION' if ready else 'NOT_READY_FOR_DEMO_TRADING',
        technical_checks_passed=technical,ready_to_start=ready,observation_ready=observation_ready,quote_required_now=quote_required,checks=checks,
        blocker_codes=[v['code'] for v in checks if not v['passed']],
        live_locked=True,required_observation_sessions=20)
