"""Pure causal event selection. Outcomes and future bars are separate."""
import numpy as np


def catalog():
    names=['TOM_RTH','TOM_TREND_1000','TOM_OVERNIGHT_1030','TOM_ATR_CAP',
           'FRIDAY_CONT','FRIDAY_REVERT','ON_INVENTORY_CONT','ON_INVENTORY_REVERT',
           'COMPRESSED_BREAK5','SWEEP_REV_1200','SWEEP_REV_1600','AFTERNOON_V2_2','AFTERNOON_V2_15']
    names += [f'AFTERNOON_TOM_{cal}_{reg}_{h}' for cal in ('YES','NO') for reg in ('LOW','MID','HIGH') for h in (2,15)]
    return names


def finite(*x):return all(np.isfinite(z) for z in x)


def select(prices,ctx):
    """Only events whose confirming information is in this prefix are emitted.

    Minute indexes relative to09:30. decision=number of completed RTH bars;
    a confirming close at index29 is known at decision30. Entries at/after
    that boundary. Midnight/calendar and prior ATR are known before the open.
    """
    n=len(prices['close']);events=[]
    def add(name,decision,entry,end,direction):
        events.append(dict(model=name,decision=decision,entry=entry,end=end,direction=direction))
    tom=ctx.get('tom',False)
    if tom:
        add('TOM_OVERNIGHT_1030',-930,-930,60,1)
    if not n:return events
    opening=float(prices['open'][0]);close=prices['close'];hi=prices['high'];lo=prices['low']
    if tom:
        add('TOM_RTH',0,0,390,1)
        if n>=30 and close[29]>opening:add('TOM_TREND_1000',30,30,390,1)
        # Future overnight completeness is only a technical evaluation gate.
        if finite(ctx.get('atr',np.nan),ctx.get('atr_p90',np.nan)) and ctx['atr']<=ctx['atr_p90']:
            add('TOM_ATR_CAP',0,0,390,1)
    if ctx.get('friday',False) and n>=240 and finite(ctx.get('week_open',np.nan)):
        direction=int(np.sign(close[239]-ctx['week_open']))
        if direction:
            add('FRIDAY_CONT',240,240,390,direction)
            add('FRIDAY_REVERT',240,240,390,-direction)
    if ctx.get('inventory_condition',False):
        direction=ctx['overnight_direction']
        add('ON_INVENTORY_CONT',0,0,120,direction)
        add('ON_INVENTORY_REVERT',0,0,120,-direction)
    atr=ctx.get('atr',np.nan);pdh=ctx.get('PDH',np.nan);pdl=ctx.get('PDL',np.nan)
    if finite(atr,pdh,pdl) and atr>0 and (pdh-pdl)<.65*atr:
        for end in range(5,min(n,385)+1,5):
            direction=1 if close[end-1]>pdh else (-1 if close[end-1]<pdl else 0)
            if direction:
                add('COMPRESSED_BREAK5',end,end,390,direction);break
    onh=ctx.get('ONH',np.nan);onl=ctx.get('ONL',np.nan)
    if n>=30 and finite(onh,onl):
        high_swept=np.max(hi[:30])>onh;low_swept=np.min(lo[:30])<onl
        back_inside=onl<close[29]<onh
        # Both-side sweeps are an explicitly excluded ambiguous subgroup.
        direction=1 if low_swept and not high_swept and back_inside and close[29]>opening else (
            -1 if high_swept and not low_swept and back_inside and close[29]<opening else 0)
        if direction:
            add('SWEEP_REV_1200',30,30,150,direction)
            add('SWEEP_REV_1600',30,30,390,direction)
    if n>=300 and finite(atr) and atr>0:
        ratio=(np.max(hi[:300])-np.min(lo[:300]))/atr
        if close[299]>opening and .5<=ratio<1.2:
            for horizon in (2,15):
                add(f'AFTERNOON_V2_{horizon}',300,330,330+horizon,1)
                regime=ctx.get('atr_regime')
                if regime:
                    add(f'AFTERNOON_TOM_{"YES" if tom else "NO"}_{regime}_{horizon}',300,330,330+horizon,1)
    return events


def fill(event,prices,ctx):
    """No stop/target orders. First next-bar open, fixed completed-bar close."""
    start,end,direction=event['entry'],event['end'],event['direction']
    if end>len(prices['close']):raise ValueError('Outcome truncated')
    if start<0:
        if not ctx.get('overnight_complete'):raise ValueError('Missing overnight entry bars')
        entry=ctx['overnight_open']
        highs=np.r_[ctx['overnight_high'],prices['high'][:end]]
        lows=np.r_[ctx['overnight_low'],prices['low'][:end]]
    else:
        if end>len(prices['close']) or start>=len(prices['close']):raise ValueError('Outcome truncated')
        entry=float(prices['open'][start]);highs=prices['high'][start:end];lows=prices['low'][start:end]
    exit_=float(prices['close'][end-1]);gross=direction*(exit_-entry)
    return dict(**event,entry_price=float(entry),exit_price=exit_,gross_points=float(gross),
        net_points=float(gross-1.225),
        mfe_points=float(max(0,np.max(highs)-entry if direction>0 else entry-np.min(lows))),
        mae_points=float(max(0,entry-np.min(lows) if direction>0 else np.max(highs)-entry)),
        atr=float(ctx['atr']) if finite(ctx.get('atr',np.nan)) else None,
        exit_reason='FIXED_TIME',fill_status='BAR_PROXY_NOT_TICK_CERTIFIED')
