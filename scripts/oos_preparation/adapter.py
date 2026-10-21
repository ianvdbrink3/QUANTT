"""Strict contract CSV/date/calendar/roll adapter, deliberately without scoring."""
import hashlib
import re
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

FIELDS = ['open', 'high', 'low', 'close', 'volume']
SCHEMA = ['Time', 'Open', 'High', 'Low', 'Latest', 'Change', '%Change', 'Volume']
RENAME = dict(Open='open', High='high', Low='low', Latest='close', Volume='volume')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def at(day, clock):
    return pd.Timestamp(f'{day} {clock}', tz='America/New_York').tz_convert('UTC')


def session_dates(index):
    # Civil NY date: evening at/after 18:00 belongs to the next date.
    local = index.tz_convert('America/New_York').tz_localize(None)
    return (local + pd.Timedelta(hours=6)).strftime('%Y-%m-%d')


def load_csv(path, contract):
    path = Path(path)
    if not re.fullmatch(r'NQ[HMUZ]\d{2}', contract) or not path.name.lower().startswith(contract.lower()+'_'):
        raise ValueError('Explicit quarterly contract must match filename')
    raw = pd.read_csv(path)
    if list(raw.columns) != SCHEMA:
        raise ValueError('Unexpected Barchart schema')
    t = pd.to_datetime(raw.Time, format='%Y-%m-%d %H:%M', errors='coerce')
    footer = raw[t.isna()]
    if not (len(footer) == 1 and str(footer.Time.iloc[0]).startswith('Downloaded from Barchart.com as of ')
            and footer.drop(columns='Time').isna().all().all()):
        raise ValueError('Unexpected non-bar row')
    bars = raw[t.notna()].rename(columns=RENAME)[FIELDS].apply(pd.to_numeric)
    bars.index = pd.DatetimeIndex(t[t.notna()]).tz_localize(
        'America/Chicago', ambiguous='raise', nonexistent='raise').tz_convert('UTC')
    if bars.empty or not bars.index.is_unique or not bars.index.is_monotonic_increasing:
        raise ValueError('Empty, duplicate or unordered source')
    if not np.isfinite(bars.to_numpy()).all():
        raise ValueError('Nonfinite OHLCV')
    prices = bars[FIELDS[:4]]
    if not ((bars.high >= prices.max(axis=1)) & (bars.low <= prices.min(axis=1))).all():
        raise ValueError('Invalid OHLC')
    if not np.isclose(prices.to_numpy()*4, np.rint(prices.to_numpy()*4), rtol=0, atol=1e-8).all():
        raise ValueError('Off-tick price')
    if not ((bars.volume > 0) & (bars.volume == bars.volume.round())).all():
        raise ValueError('Invalid volume')
    bars.volume = bars.volume.astype('int64')
    bars['contract'] = contract
    bars['trade_date'] = session_dates(bars.index)
    return bars


def combine(parts, start, end):
    frame = pd.concat(parts).sort_index()
    dup = frame[frame.reset_index().duplicated(['contract', frame.index.name or 'index'], keep=False).to_numpy()]
    if len(dup) and dup.groupby(['contract', dup.index])[FIELDS].nunique().gt(1).any().any():
        raise ValueError('Conflicting overlapping OHLCV')
    keys = pd.MultiIndex.from_arrays([frame.contract, frame.index])
    frame = frame[~keys.duplicated()]
    return frame[frame.trade_date.between(start, end)]


def stage_immutable(source, target):
    source, target = Path(source), Path(target)
    if target.exists():
        if sha(source) != sha(target):
            raise ValueError('Refusing to replace different raw bytes')
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    if sha(source) != sha(target):
        raise ValueError('Staged hash mismatch')
    return sha(target)


class Calendar:
    def __init__(self, registry):
        self.registry = registry

    def grid(self, day, remove_observed_outage=False):
        if not any(a <= day <= b for a, b in self.registry['reviewed_ranges']):
            raise ValueError('CALENDAR_UNVERIFIED: '+day)
        if pd.Timestamp(day).weekday() >= 5:
            return pd.DatetimeIndex([], tz='UTC')
        close = self.registry['closes_ny'].get(day, '17:00')
        if close is None:
            return pd.DatetimeIndex([], tz='UTC')
        prev = (pd.Timestamp(day)-pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        ix = pd.date_range(at(prev, '18:00'), at(day, close), freq='min', inclusive='left')
        if remove_observed_outage:
            for halt in self.registry.get('observed_outages', []):
                a, b = pd.Timestamp(halt['start_utc']), pd.Timestamp(halt['end_utc'])
                ix = ix[(ix < a) | (ix >= b)]
        return ix


def determine_roll(full, old, new, calendar, decision_through):
    """Volume-only, no future observations beyond decision_through consulted."""
    f = full[full.trade_date.le(decision_through)]
    oldg, newg = f[f.contract.eq(old)], f[f.contract.eq(new)]
    for day in sorted(set(oldg.trade_date) & set(newg.trade_date)):
        expected = calendar.grid(day)
        if not len(expected):
            continue
        a, b = oldg[oldg.trade_date.eq(day)], newg[newg.trade_date.eq(day)]
        if a.index.min() > expected.min() or a.index.max() < expected.max():
            continue
        if b.index.min() > expected.min()+pd.Timedelta(minutes=60) or b.index.max() < expected.max()-pd.Timedelta(minutes=60):
            continue
        av, bv = int(a.volume.sum()), int(b.volume.sum())
        if bv <= av:
            continue
        next_day = pd.Timestamp(day)
        while True:
            next_day += pd.Timedelta(days=1)
            effective = next_day.strftime('%Y-%m-%d')
            if len(calendar.grid(effective)):
                break
        prev = (next_day-pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        activation = at(prev, '18:00')
        # No future joint close can enter the spread.
        oa, nb = oldg[oldg.index < activation], newg[newg.index < activation]
        common = oa.index.intersection(nb.index)
        common = common[common.tz_convert('America/New_York').strftime('%H:%M') == '15:59']
        if not len(common):
            raise ValueError('NO_PRE_ROLL_COMMON_RTH_CLOSE')
        t = common.max()
        return {'from':old, 'to':new, 'decision_session':day, 'old_volume':av,
                'new_volume':bv, 'effective_session':effective, 'effective_utc':activation.isoformat(),
                'close_bar_utc':t.isoformat(), 'spread_available_utc':(t+pd.Timedelta(minutes=1)).isoformat(),
                'spread_points':float(nb.at[t,'close']-oa.at[t,'close'])}
    raise ValueError('DATA_INSUFFICIENT: no evidenced crossover '+old+' -> '+new)


def audit_contract(frame, calendar, start, end):
    if frame.contract.nunique() != 1 or not frame.index.is_unique:
        raise ValueError('One reconciled contract required')
    rows = []
    for day in pd.bdate_range(start, end).strftime('%Y-%m-%d'):
        expected = calendar.grid(day, remove_observed_outage=True)
        prev = (pd.Timestamp(day)-pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        prefix = pd.date_range(at(prev,'18:00'), at(day,'12:00'), freq='min', inclusive='left')
        g = frame[frame.trade_date.eq(day)]
        normal = pd.date_range(at(prev,'18:00'), at(day,'17:00'), freq='min', inclusive='left')
        missing = expected.difference(g.index)
        rows.append({'day':day, 'bars':len(g), 'expected':len(expected), 'unresolved_missing':len(missing),
                     'unexpected':len(g.index.difference(expected)), 'standard_clean':g.index.equals(normal),
                     'noon_prefix_complete':len(prefix.difference(g.index)) == 0,
                     'missing_utc':[t.isoformat() for t in missing]})
    return rows
