"""NYSE cash calendar 2017–2028, with mourning closures and zone-aware jobs."""
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from dateutil.easter import easter

NY = ZoneInfo('America/New_York')
NL = ZoneInfo('Europe/Amsterdam')


def observed(day):
    return day-timedelta(days=1) if day.weekday()==5 else day+timedelta(days=1) if day.weekday()==6 else day


def nth(year,month,weekday,n):
    d = date(year,month,1)
    return d+timedelta(days=(weekday-d.weekday())%7+7*(n-1))


def holidays(year):
    if not 2017 <= year <= 2028: raise ValueError('CALENDAR_OUTSIDE_VERIFIED_RANGE')
    last_may = date(year,6,1)-timedelta(days=1)
    memorial = last_may-timedelta(days=last_may.weekday())
    days = {nth(year,1,0,3),nth(year,2,0,3),easter(year)-timedelta(days=2),memorial,
            observed(date(year,7,4)),nth(year,9,0,1),nth(year,11,3,4),observed(date(year,12,25))}
    # NYSE does not observe Saturday New Year's Day on the preceding Friday.
    newyear = date(year,1,1)
    if newyear.weekday()!=5: days.add(observed(newyear))
    if year>=2022: days.add(observed(date(year,6,19)))
    if year==2018: days.add(date(2018,12,5))
    if year==2025: days.add(date(2025,1,9))
    return days


def is_session(day):
    d=date.fromisoformat(str(day))
    return d.weekday()<5 and d not in holidays(d.year)


def early_close(day):
    d=date.fromisoformat(str(day))
    return is_session(day) and (d==nth(d.year,11,3,4)+timedelta(days=1) or (d.month,d.day) in ((7,3),(12,24)))


def stamp(day,clock):
    return datetime.fromisoformat(f'{day}T{clock}').replace(tzinfo=NY)


def schedule(day):
    if not is_session(day): return {}
    close='13:00' if early_close(day) else '16:00'
    end=stamp(day,close)
    return {'pre_open':stamp(day,'09:20'),'open_orders':stamp(day,'09:31'),
            'pre_close':end-timedelta(minutes=10),'close':end,
            's1_entry':None if early_close(day) else end+timedelta(minutes=1),
            'brief':end+timedelta(minutes=2),'core_finalize':end+timedelta(minutes=5)}


def next_session(day):
    d=date.fromisoformat(str(day))+timedelta(days=1)
    while not is_session(str(d)): d+=timedelta(days=1)
    return str(d)


def us_settlement_day(day):
    """US equities T+2 historically, T+1 from 2024-05-28; bank holidays excluded."""
    d=date.fromisoformat(day);remaining=1 if day>='2024-05-28' else 2
    while remaining:
        d+=timedelta(days=1)
        bank_extra={nth(d.year,10,0,2),observed(date(d.year,11,11)),observed(date(d.year,1,1))}
        if d.year>=2021:bank_extra.add(observed(date(d.year,6,19)))
        if is_session(str(d)) and d not in bank_extra:remaining-=1
    return str(d)
