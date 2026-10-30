"""Frozen deterministic gates, equality handling and hysteresis."""
from enum import IntEnum
import math
import pandas as pd


class State(IntEnum):
    DATA_HALT = -1
    BEAR = 0
    PULLBACK = 1
    BULL = 2


def classify(close, row, healthy=True):
    if not healthy or not all(pd.notna(row.get(k)) and math.isfinite(float(row[k])) for k in ('SMA20','SMA200','ATR14_pre')) or not math.isfinite(float(close)) or close <= 0:
        return State.DATA_HALT
    if close <= row['SMA200']:
        return State.BEAR
    tag = row.get('HIGH_VOL')
    if close <= row['SMA20'] or pd.isna(tag) or bool(tag):
        return State.PULLBACK
    return State.BULL


def trend_states(close, sma, variant='naked'):
    if variant not in ('naked','schmitt','confirm2'):
        raise ValueError('UNKNOWN_VARIANT')
    state = False
    above_count = below_count = 0
    result = []
    for c, s in zip(close, sma, strict=True):
        if not math.isfinite(float(c)) or not math.isfinite(float(s)):
            state = False
            above_count = below_count = 0
        elif variant == 'naked':
            state = c > s
        elif variant == 'schmitt':
            if c > 1.005*s: state = True
            elif c < .995*s: state = False
        else:
            above_count = above_count+1 if c > s else 0
            below_count = below_count+1 if c <= s else 0
            if above_count >= 2: state = True
            elif below_count >= 2: state = False
        result.append(bool(state))
    return result


WEIGHTS = {'defensive': (.5,0.,.25,.25), 'balanced': (.6,.3,.1,0.), 'offensive': (0.,1.,0.,0.)}


def sleeve_targets(state, tqqq_trend, vol_known=True):
    if state in (State.BEAR, State.DATA_HALT): return (0.,0.,0.)
    if state == State.PULLBACK: return (1., .5 if tqqq_trend and vol_known else 0., 0.)
    return (1.,1. if tqqq_trend else 0.,1.)
