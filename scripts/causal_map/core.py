"""Causal event selection is separate from (necessarily future) outcome scoring.

All anchors are boundaries k of completed minute bars. k=0 is the RTH open;
k=30 is 10:00, after bar29, and k=390 is too late for a forward observation.
No event weights depend on later events. Arrays may be truncated at any k.
"""
from dataclasses import dataclass, asdict

import numpy as np
from scipy.stats import t as student_t

HORIZONS = (15, 30, 60, 'close')
SIZES = ('SMALL', 'MID', 'LARGE')


@dataclass(frozen=True)
class Event:
    mechanism: str
    boundary: int
    anchor: float
    direction: int
    level: float | None = None
    rvol: float | None = None


def catalog():
    rows = []
    for level in ('PDH', 'PDL', 'ONH', 'ONL'):
        for state in ('ACCEPT', 'REJECT'):
            rows.append(dict(id=f'A_{level}_{state}', category='A',
                label=f'{level}: eerste bereik, close '+('voorbij niveau' if state=='ACCEPT' else 'terug aan binnenzijde'),
                direction='naar buiten' if state=='ACCEPT' else 'naar binnen'))
    for kind in ('GAP_UP', 'GAP_DOWN', 'EXTREME_ON_UP', 'EXTREME_ON_DOWN'):
        for clock in ('0930', '1000'):
            rows.append(dict(id=f'B_{kind}_{clock}', category='B', label=f'{kind} vanaf {clock}', direction='met gap/overnight-verplaatsing'))
    for clock in ('0930', '1500'):
        for side in ('UP', 'DOWN'):
            for size in SIZES:
                rows.append(dict(id=f'C_{clock}_{side}_{size}', category='C', label=f'{clock} | {side} | {size}', direction='met reeds bekende sessierichting'))
    for width in (1, 5):
        for side in ('HIGH', 'LOW'):
            rows.append(dict(id=f'D_{width}m_{side}', category='D', label=f'{width}m volumeschok op nieuw {side}', direction='naar nieuw extreem (negatief = omkeer)'))
    return rows


def valid(x):
    return x is not None and np.isfinite(x)


def size_bin(x):
    return 'SMALL' if x < .5 else ('MID' if x < 1.2 else 'LARGE')


def select_events(prices, context):
    """Only the supplied prefix and prior-day/overnight context are read.

    Context levels/ATR/volume thresholds must be available by 09:30. Clock
    09:30 uses only the opening price, not the first minute's H/L/C/volume.
    A first reach includes a jump beyond a level; a physical traded touch is
    not asserted. ACCEPT/REJECT is the observed confirming close, not future.
    """
    n = len(prices['close'])
    o, h, l, c, v = (np.asarray(prices[z], float) for z in ('open','high','low','close','volume'))
    opening = context['opening']
    events = []
    atr = context.get('atr')
    def add(name, k, direction, level=None, rvol=None):
        if k > n or k > 390:
            return
        p = opening if k == 0 else float(c[k-1])
        events.append(Event(name, k, p, int(direction), level, rvol))
    for level_name in ('PDH','PDL','ONH','ONL'):
        level = context.get(level_name)
        if not valid(level):
            continue
        side = 1 if level_name.endswith('H') else -1
        hits = np.flatnonzero(h >= level if side == 1 else l <= level)
        if len(hits):
            i = int(hits[0])
            accepted = side*(c[i]-level) > 0
            add(f'A_{level_name}_'+('ACCEPT' if accepted else 'REJECT'), i+1,
                side if accepted else -side, float(level))
    classifications = []
    if valid(context.get('PDH')) and opening > context['PDH']:
        classifications.append(('GAP_UP', 1))
    if valid(context.get('PDL')) and opening < context['PDL']:
        classifications.append(('GAP_DOWN', -1))
    prior_close = context.get('prior_close')
    if valid(atr) and atr > 0 and valid(prior_close):
        movement = (opening-prior_close)/atr
        if abs(movement) >= 1:
            classifications.append(('EXTREME_ON_UP' if movement > 0 else 'EXTREME_ON_DOWN', int(np.sign(movement))))
    for name, side in classifications:
        for clock, k in (('0930',0), ('1000',30)):
            add(f'B_{name}_{clock}', k, side)
    if valid(atr) and atr > 0:
        if valid(context.get('on_open')) and valid(context.get('on_close')) and valid(context.get('ONH')) and valid(context.get('ONL')):
            direction = np.sign(context['on_close']-context['on_open'])
            if direction:
                add(f'C_0930_'+('UP' if direction>0 else 'DOWN')+'_'+size_bin((context['ONH']-context['ONL'])/atr), 0, direction)
        if n >= 330:
            direction = np.sign(c[329]-opening)
            if direction:
                add(f'C_1500_'+('UP' if direction>0 else 'DOWN')+'_'+size_bin((h[:330].max()-l[:330].min())/atr), 330, direction)
    known_h = np.maximum.accumulate(h) if n else np.array([])
    known_l = np.minimum.accumulate(l) if n else np.array([])
    for width in (1,5):
        threshold = context.get(f'volume_q95_{width}', np.full(390//width, np.nan))
        mean = context.get(f'volume_mean_{width}', np.full(390//width, np.nan))
        for end in range(width, n+1, width):
            start = end-width
            if start == 0:
                continue  # no prior RTH extreme for the very first bar/block
            slot = start//width
            if not np.isfinite(threshold[slot]) or not np.isfinite(mean[slot]) or mean[slot] <= 0:
                continue
            volume = float(v[start:end].sum())
            if volume <= threshold[slot]:
                continue
            rvol = volume/mean[slot]
            if h[start:end].max() > known_h[start-1]:
                add(f'D_{width}m_HIGH', end, 1, rvol=float(rvol))
            if l[start:end].min() < known_l[start-1]:
                add(f'D_{width}m_LOW', end, -1, rvol=float(rvol))
    return sorted(events, key=lambda e:(e.boundary,e.mechanism))


def outcome(prices, event, horizon):
    """Exact wall-clock horizon; no shortening at RTH close, no eventbar wicks."""
    k = event.boundary
    j = 389 if horizon == 'close' else k+int(horizon)-1
    n = len(prices['close'])
    if k >= n or j >= n or j < k:
        return None
    p, s = event.anchor, event.direction
    end = float(prices['close'][j])
    high = float(np.max(prices['high'][k:j+1]))
    low = float(np.min(prices['low'][k:j+1]))
    favorable = max(0., high-p) if s==1 else max(0., p-low)
    adverse = max(0., p-low) if s==1 else max(0., high-p)
    # Full OHLC excursions, orientation fixed at the known event; never chosen
    # from the realized sign. No inference about within-bar ordering or fills.
    return dict(return_points=s*(end-p), return_bps=s*10000*np.log(end/p),
        raw_up_points=end-p, raw_up_bps=10000*np.log(end/p),
        mfe_points=favorable, mae_points=adverse,
        mfe_bps=10000*np.log(high/p) if s==1 and high>p else (10000*np.log(p/low) if s==-1 and low<p else 0.),
        mae_bps=10000*np.log(p/low) if s==1 and low<p else (10000*np.log(high/p) if s==-1 and high>p else 0.),
        minutes=j-k+1, endpoint_bar=j)


def cluster_inference(x, day_ids, calendar_size):
    """Intercept-only CR1 sandwich, plus prespecified daily-score HAC(5).

    Point estimate is pooled event mean, NOT equal-day means. Sum residuals
    within day before squaring. Zero score on non-event calendar days does not
    manufacture zero market returns. t degrees of freedom = event days - 1.
    """
    x, ids = np.asarray(x,float), np.asarray(day_ids,int)
    n = len(x); g = len(np.unique(ids))
    empty = dict(se=None, ci95=None, p=None, hac_se=None, hac_ci95=None, hac_p=None)
    if n == 0 or g < 20:
        return dict(empty, status='INSUFFICIENT_CLUSTERS', clusters=g)
    theta = float(x.mean())
    scores = np.bincount(ids, weights=x-theta, minlength=calendar_size)
    factor = g/(g-1)
    meat = float(scores@scores)
    hac = meat
    for lag in range(1,6):
        hac += 2*(1-lag/6)*float(scores[lag:]@scores[:-lag])
    se = np.sqrt(max(0.,factor*meat))/n
    hse = np.sqrt(max(0.,factor*hac))/n
    crit = float(student_t.ppf(.975,g-1))
    def pvalue(err):
        if err == 0:
            return 1. if theta == 0 else 0.
        return float(2*student_t.sf(abs(theta/err),g-1))
    return dict(status='OK', clusters=g, se=float(se), ci95=[theta-crit*se,theta+crit*se], p=pvalue(se),
        hac_se=float(hse), hac_ci95=[theta-crit*hse,theta+crit*hse], hac_p=pvalue(hse))


def holm(values):
    p = np.asarray([1. if x is None else x for x in values])
    order = np.argsort(p,kind='stable')
    a = np.minimum(1.,np.maximum.accumulate(p[order]*(len(p)-np.arange(len(p)))))
    out = np.ones(len(p)); out[order] = a
    return out.tolist()


def volume_reference(history):
    """Exactly the preceding20 scheduled sessions, with missing clocks exposed."""
    refs = {}
    for width in (1,5):
        refs[f'volume_q95_{width}'] = np.full(390//width,np.nan)
        refs[f'volume_mean_{width}'] = np.full(390//width,np.nan)
        if len(history) < 20:
            continue
        x = np.asarray(history[-20:]).reshape(20,390//width,width).sum(axis=2)
        good = np.isfinite(x).all(axis=0)
        refs[f'volume_q95_{width}'][good] = np.quantile(x[:,good],.95,axis=0,method='linear')
        refs[f'volume_mean_{width}'][good] = x[:,good].mean(axis=0)
    return refs


def encode_events(events):
    return [asdict(e) for e in events]
