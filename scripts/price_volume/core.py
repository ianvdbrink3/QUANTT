"""Causal selectors and conservative minute execution. No parameter search."""
import numpy as np

TICK = .25
FEE = 1.225
EXIT = 385  # 15:55 open
FIELDS = ('open', 'high', 'low', 'close', 'volume')
G1 = tuple('G1_' + x for x in ('TIME', 'HIGH', 'ATR'))
G2 = tuple(f'G2_{level}_{regime}_{exit_}' for level in ('ONL', 'H1')
           for regime in ('ALL', 'BULL') for exit_ in ('VWAP', 'ATR', 'TIME'))
G3 = ('G3_CLOSE_OPEN_REF', 'G3_CLOSE_1000_REF',
      'G3_1600_OPEN', 'G3_1600_1000', 'G3_DIP_TIME')
MODELS = G1 + G2 + G3


def blocks(p):
    n = len(p['close']) // 5
    return [dict(start=5*j, end=5*j+5, open=float(p['open'][5*j]),
                 high=float(max(p['high'][5*j:5*j+5])),
                 low=float(min(p['low'][5*j:5*j+5])),
                 close=float(p['close'][5*j+4]),
                 volume=float(sum(p['volume'][5*j:5*j+5]))) for j in range(n)]


def pullback(p, start):
    """Only a trough AFTER the most recent peak minute establishes the dip.

    The peak minute's low cannot certify high-before-low ordering.
    """
    if not start:
        return None
    high = float(max(p['high'][:start]))
    peak = int(np.flatnonzero(p['high'][:start] == high)[-1])
    if peak + 1 >= start:
        return None
    return high, float(min(p['low'][peak+1:start]))


def select_g1(p, ctx, prior_volumes):
    if ctx.get('bull') is not True:
        return None
    bs = blocks(p)
    history = list(prior_volumes[-20:])
    for j, b in enumerate(bs):
        reference = np.mean(history[-20:]) if len(history) >= 20 else np.nan
        history.append(b['volume'])
        if not 15 <= b['end'] <= 300 or j == 0:
            continue
        dip = pullback(p, b['start'])
        if dip is None or dip[0]-dip[1] < .50*ctx['atr']:
            continue
        if not (b['close'] > b['open'] and b['close'] > bs[j-1]['high']
                and b['volume'] > 1.5*reference):
            continue
        return dict(boundary=b['end'], low=min(dip[1], b['low'])-TICK,
                    high=float(max(p['high'][:b['end']])), volume_reference=float(reference))
    return None


def select_g2(p, ctx, level_name, bull=False):
    if bull and ctx.get('bull') is not True:
        return None
    bs = blocks(p)
    for j in range(1, len(bs)-1):
        b, confirm = bs[j:j+2]
        if not 5 <= b['end'] or not confirm['end'] <= 270:
            continue
        if level_name == 'ONL':
            level = ctx.get('ONL', np.nan)
        elif level_name == 'H1':
            if b['start'] < 60:
                continue  # first hour cannot be used before 10:30
            level = float(min(p['low'][:60]))
        else:
            raise ValueError('Unknown level')
        reference = float(np.mean([v['volume'] for v in bs[:j]]))
        if (np.isfinite(level) and bs[j-1]['close'] >= level and b['low'] < level
                and b['volume'] > 2.*reference and confirm['close'] > level):
            return dict(boundary=confirm['end'], low=b['low']-TICK,
                        level=float(level), volume_reference=reference)
    return None


def strong_day(p, ctx):
    if len(p['close']) != 390:
        return False  # terminal close is not available earlier
    high, low, close = max(p['high']), min(p['low']), p['close'][-1]
    return bool(high > low and (close-low)/(high-low) >= .85
                and high-low > .85*ctx['atr']
                and np.isfinite(ctx.get('sma_today', np.nan)) and close > ctx['sma_today'])


def vwap_before(p, i):
    if not i:
        return np.nan
    volume = p['volume'][:i]
    typical = (p['high'][:i]+p['low'][:i]+p['close'][:i])/3.
    return float(np.dot(typical, volume)/sum(volume))


def ceil_tick(value):
    return float(np.ceil(value/TICK-1e-9)*TICK)


def floor_tick(value):
    return float(np.floor(value/TICK+1e-9)*TICK)


def manage(p, start, entry, stop=None, target=None, vwap=False, at_open=True):
    """Long only. Targets require trade-through; stop wins unresolved conflicts."""
    if stop is not None and stop >= entry:
        return None, 'STOP_NOT_BELOW_ENTRY'
    for i in range(start, EXIT):
        op, hi, lo, cl = (float(p[k][i]) for k in ('open', 'high', 'low', 'close'))
        opening_known = i > start or at_open
        level = ceil_tick(vwap_before(p, i)) if vwap else target
        if opening_known and stop is not None and op <= stop:
            return execution(start, i, entry, op, at_open, True, 'STOP_GAP'), 'FILLED'
        # A target already at/below the entry is immediately marketable. Do
        # not credit a historical touch or an impossible favorable fill.
        if i == start and level is not None and level <= entry:
            return execution(start, i, entry, entry, at_open, at_open, 'TARGET_MARKETABLE_ENTRY'), 'FILLED'
        if opening_known and level is not None and op >= level+TICK:
            return execution(start, i, entry, level, at_open, True, 'TARGET_OPEN'), 'FILLED'
        if stop is not None and lo <= stop:
            return execution(start, i, entry, stop, at_open, False, 'STOP'), 'FILLED'
        if level is not None and hi >= level+TICK and (opening_known or cl >= level+TICK):
            return execution(start, i, entry, level, at_open, False, 'TARGET'), 'FILLED'
    return execution(start, EXIT, entry, float(p['open'][EXIT]), at_open, True, 'TIME_1555'), 'FILLED'


def execution(start, end, entry, exit_, entry_open, exit_open, reason):
    return dict(entry_bar=start, exit_bar=end, entry_price=float(entry), exit_price=float(exit_),
                entry_at_open=entry_open, exit_at_open=exit_open, reason=reason,
                gross_points=float(exit_-entry), net_points=float(exit_-entry-FEE))


def execute(p, ctx, model, event):
    if event is None:
        return None, 'NO_SIGNAL'
    i = event['boundary']
    if i >= len(p['open']):
        raise ValueError('Next-bar entry unavailable')
    entry = float(p['open'][i])
    if model in G1:
        # Minimum risk .35 ATR, structural low one tick beyond the dip.
        stop = min(event['low'], floor_tick(entry-.35*ctx['atr']))
        target = event['high'] if model == 'G1_HIGH' else ceil_tick(entry+ctx['atr']) if model == 'G1_ATR' else None
        return manage(p, i, entry, stop=stop, target=target)
    if model in G2:
        target = ceil_tick(entry+.75*ctx['atr']) if model.endswith('_ATR') else None
        return manage(p, i, entry, stop=event['low'], target=target, vwap=model.endswith('_VWAP'))
    raise ValueError('Unknown model')


def dip_entry(p, ctx):
    level = floor_tick(float(p['open'][0])-.25*ctx['atr'])
    for i in range(min(150, len(p['close']))):  # resting order 09:30--11:59
        if p['open'][i] <= level-TICK or p['low'][i] <= level-TICK:
            return manage(p, i, level, at_open=bool(p['open'][i] <= level-TICK))
    return None, 'NO_MORNING_DIP_FILL'


def marks(trade, p):
    """Observed opens/closes, never pre-entry lows/highs or fictitious tick paths."""
    a, b = trade['entry_bar'], trade['exit_bar']
    e = trade['entry_price']
    values = [-FEE]
    for i in range(a, b+1):
        if i == b:
            if not trade['exit_at_open'] and (i > a or trade['entry_at_open']):
                values.append(float(p['open'][i])-e-FEE)
            values.append(trade['net_points'])
        else:
            if i > a or trade['entry_at_open']:
                values.append(float(p['open'][i])-e-FEE)
            values.append(float(p['close'][i])-e-FEE)
    return values
