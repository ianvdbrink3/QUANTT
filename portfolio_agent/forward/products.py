"""Exact identity binding, not a ticker-name substitution or inherited backtest."""
from .common import dec

CANDIDATES=[
    dict(key='EQQQ',isin='IE0032077012',kind='UCITS_DIST',leverage=1,
         source='https://www.invesco.com/uk/en/financial-products/etfs/invesco-eqqq-nasdaq-100-ucits-etf-dist.html',verified='PRIOR_REFERENCE_NOT_ACCOUNT_CHECKED'),
    dict(key='XNAS',isin='IE00BMFKG444',kind='UCITS_ACC',leverage=1,
         source='https://etf.dws.com/en-gb/IE00BMFKG444-nasdaq-100-ucits-etf-1c/',verified='ISSUER_ISIN_CHECKED_2026-10-30'),
    dict(key='QQQ3',isin='IE00BLRPRL42',kind='DEBT_ETP_NOT_TQQQ',leverage=3,
         source='https://dataspanapi.wisdomtree.com/pdr/documents/FACTSHEET/WTMA/EU/EN-GB/IE00BLRPRL42/',verified='PRIOR_REFERENCE_NOT_ACCOUNT_CHECKED')]


def validate_binding(binding,instruments,account,exchanges):
    required={'research_key','ticker','isin','currency','schedule_id','lot','price_tick','minimum_notional','history_validated','session_validated','structure_verified','account_permission_verified'}
    if set(binding)!=required:raise ValueError('BINDING_SCHEMA_MISMATCH')
    if binding['research_key'] not in ('QQQ','TQQQ'):raise ValueError('INVALID_RESEARCH_ROLE')
    for flag in ('history_validated','session_validated','structure_verified','account_permission_verified'):
        if binding[flag] is not True:raise ValueError('PRODUCT_NOT_VALIDATED_'+flag.upper())
    matches=[i for i in instruments if i.get('ticker')==binding['ticker']]
    if len(matches)!=1:raise ValueError('EXACT_BROKER_TICKER_REQUIRED')
    item=matches[0]
    if not binding['isin'] or item.get('isin')!=binding['isin']:raise ValueError('ISIN_MISMATCH')
    if item.get('currencyCode')!=binding['currency'] or account.get('currency')!=binding['currency']:
        raise ValueError('PRIMARY_CURRENCY_CONVERSION_NOT_VALIDATED')
    if item.get('type')!='ETF':raise ValueError('INSTRUMENT_STRUCTURE_REVIEW_REQUIRED')
    if item.get('workingScheduleId')!=binding['schedule_id']:raise ValueError('SCHEDULE_ID_MISMATCH')
    schedules=[s for e in exchanges for s in e.get('workingSchedules',[]) if s.get('id')==binding['schedule_id']]
    if len(schedules)!=1 or not schedules[0].get('timeEvents'):raise ValueError('BROKER_SESSION_MISSING')
    if dec(binding['lot'])<=0 or dec(binding['price_tick'])<=0 or dec(binding['minimum_notional'])<=0 or dec(item.get('maxOpenQuantity',0))<=0:
        raise ValueError('LOT_TICK_OR_MAX_QUANTITY_UNVERIFIED')
    return item,schedules[0]


def session_open(schedule,now):
    from .common import stamp
    events=sorted((stamp(e['date']),e['type']) for e in schedule.get('timeEvents',[]) if e.get('type') in ('OPEN','CLOSE','BREAK_START','BREAK_END'))
    state=False;seen=False
    for at,kind in events:
        if at>now:break
        state=kind in ('OPEN','BREAK_END');seen=True
    # Do not extrapolate an old session indefinitely into another day.
    future_close=any(at>now and kind in ('CLOSE','BREAK_START') for at,kind in events)
    return seen and state and future_close
