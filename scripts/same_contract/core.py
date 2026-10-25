"""Contract choice contains no prices, volumes after selection, or next-day route."""
import pandas as pd
from scripts import prepare_historical_contracts as h


def successor(contract):
    cycle='HMUZ'; i=cycle.index(contract[2]); year=int(contract[3:])
    return 'NQ'+cycle[(i+1)%4]+f'{year+(i==3):02d}'


def choose(day, nextcash, initial, rolls):
    """Freeze at 09:30, re-confirm at15:55. Calendar expiry guard is preknown.

    Only activations already effective before today's RTH may choose a contract.
    Tomorrow's route and today's completed futures volume are not consulted.
    """
    cutoff=h.at(day,'09:30'); contract=initial; available=None
    for r in sorted(rolls,key=lambda x:x['effective_session']):
        effective=pd.Timestamp(r['effective_utc'])
        if effective>cutoff:continue
        # The decision session must already be over before this RTH session.
        if r['decision_session']>=day:raise ValueError('Future volume decision')
        contract=r['to'];available=effective.isoformat()
    original=contract
    while h.at(h.expiry(contract),'09:30')<=h.at(nextcash,'09:30'):
        contract=successor(contract)
    return dict(contract=contract,rth_contract=original,expiry_guard=contract!=original,
                selected_at_utc=cutoff.isoformat(),route_available_utc=available,
                expiry_date=h.expiry(contract),selection='PREKNOWN_RTH_ROUTE_WITH_CALENDAR_EXPIRY_GUARD')


def path(full_contract, day, nextday, calendar):
    """Both fills and every intervening observation are the exact held contract."""
    start,end=h.at(day,'16:00'),h.at(nextday,'09:30')
    rows=full_contract.loc[start:end]
    if start not in rows.index or end not in rows.index:return None,'MISSING_SAME_CONTRACT_ENDPOINT'
    if not rows.index.is_unique or rows.contract.nunique()!=1:raise ValueError('Mixed/duplicate contract path')
    if 'usable' in rows and not rows.usable.all():return None,'INVALID_HOLDING_BAR'
    # Recent sources are numerically validated by load_csv; historical rows carry usable.
    if 'numeric_valid' in rows and not rows.numeric_valid.all():return None,'INVALID_HOLDING_BAR'
    expected=[]
    for d in pd.bdate_range(day,nextday).strftime('%Y-%m-%d'):expected.extend(calendar.grid(d))
    expected=pd.DatetimeIndex(expected);expected=expected[(expected>=start)&(expected<end)]
    fields=('open','high','low','close','volume')
    return (rows.index,{k:rows[k].to_numpy(float) for k in fields},expected.difference(rows.index)),'FILLED'
