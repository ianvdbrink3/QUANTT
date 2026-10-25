"""Causal closed-bar event chain and minute-resolution, adverse-first execution."""
from dataclasses import dataclass,asdict
import numpy as np

TICK=.25
FEE=1.225
EXIT=385  # RTH15:55 OPEN
FIELDS=('open','high','low','close','volume')

@dataclass(frozen=True)
class Spec:
    family:str
    timeframe:int
    bias:str
    level:str
    mode:str
    target:str
    @property
    def name(self):return f'{self.family}_{self.timeframe}m_{self.bias}_{self.level}_{self.mode}_{self.target}'


def catalog():
    rows=[]
    for tf in (1,5):
        for bias in ('BOTH','BULL_LONG'):
            rows += [Spec('ICT1',tf,bias,level,'REVERSAL',target) for level in ('ON','PRE') for target in ('2R','3R','OPPOSITE_ON')]
            rows += [Spec('ICT2',tf,bias,window,mode,target) for window in ('AM','PM') for mode in ('FADE','CONTINUE') for target in ('2R','3R')]
            rows += [Spec('ICT3',tf,bias,anchor,'JUDAS',target) for anchor in ('OPEN0930','OPEN0830') for target in ('2R','3R','TIME')]
    return rows


def ceil_tick(x):return float(np.ceil(x/TICK-1e-9)*TICK)
def floor_tick(x):return float(np.floor(x/TICK+1e-9)*TICK)


def aggregate(p,tf,start=-90,end=None):
    """p starts08:00NY; relative minute0 is09:30. Incomplete blocks unusable."""
    available=min(len(p['close'])-90,EXIT) if end is None else min(end,len(p['close'])-90,EXIT)
    n=max(0,(available-start)//tf)
    arrays={k:np.asarray(p[k][start+90:start+90+n*tf],float).reshape(n,tf) for k in FIELDS}
    valid=np.logical_and.reduce([np.isfinite(v).all(axis=1) for v in arrays.values()])
    high=arrays['high'].max(axis=1) if n else []
    low=arrays['low'].min(axis=1) if n else []
    volume=arrays['volume'].sum(axis=1)
    result=[]
    for j in range(n):
        s=start+j*tf
        if not valid[j]:result.append(dict(start=s,end=s+tf,valid=False));continue
        result.append(dict(start=s,end=s+tf,valid=True,open=float(arrays['open'][j,0]),high=float(high[j]),
                           low=float(low[j]),close=float(arrays['close'][j,-1]),volume=float(volume[j])))
    return result


def fvg(bars,j,atr):
    if j<2 or not all(x['valid'] for x in bars[j-2:j+1]):return None
    a,b,c=bars[j-2:j+1]
    if c['low']-a['high']>=.03*atr and b['close']-b['open']>=.03*atr:
        return dict(direction=1,entry=c['low'],structural=a['low']-TICK,size=c['low']-a['high'],middle_start=b['start'])
    if a['low']-c['high']>=.03*atr and b['open']-b['close']>=.03*atr:
        return dict(direction=-1,entry=c['high'],structural=a['high']+TICK,size=a['low']-c['high'],middle_start=b['start'])
    return None


def confirmed(bars,j):
    """Center j-2 becomes known only when bar j has closed. Strict2+2 fractal."""
    if j<4 or not all(b['valid'] for b in bars[j-4:j+1]):return {}
    center=bars[j-2];others=bars[j-4:j-2]+bars[j-1:j+1];out={}
    if all(center['high']>b['high'] for b in others):out['high']=center['high']
    if all(center['low']<b['low'] for b in others):out['low']=center['low']
    return out


def allowed(spec,ctx,side):
    if spec.bias=='BULL_LONG' and (side!=1 or ctx.get('bull') is not True):return False
    if spec.family=='ICT3':
        return ctx.get('bull') is True if side==1 else ctx.get('bear') is True
    return True


def window(spec):
    if spec.family=='ICT1':return 0,120
    if spec.family=='ICT2':return (30,90) if spec.level=='AM' else (270,330)
    return 0,60


def opposite(ctx,side):return ctx.get('ONH' if side==1 else 'ONL',np.nan)


def signal(p,ctx,spec,bars=None):
    """Return first fixed order, never consult a later fill or trade outcome.

    Sweeps must close before displacement middle-bar starts. Simultaneous high
    and low sweeps in one signal-timeframe bar are skipped: order unprovable.
    MSS may occur in FVG middle or third bar; its swing was already confirmed
    before that crossing bar. No pivots from future bars or later day extrema.
    """
    atr=ctx['atr'];bars=aggregate(p,spec.timeframe) if bars is None else bars;start,finish=window(spec)
    if spec.family=='ICT1':levels=ctx.get(spec.level)
    elif spec.family=='ICT2':levels=ctx.get(spec.level)
    else:levels=None
    if spec.family!='ICT3' and (levels is None or not np.isfinite(levels).all()):return None
    anchor=ctx.get(spec.level,np.nan) if spec.family=='ICT3' else np.nan
    if spec.family=='ICT3' and not np.isfinite(anchor):return None
    swing={};mss={};sweeps={};seen=set();running_high=-np.inf;running_low=np.inf
    previous=None
    for j,b in enumerate(bars):
        if b['start']>=finish:break
        if not b['valid']:
            # Never carry an inferred structure/sweep chain across unknown bars.
            swing={};mss={};sweeps={};previous=None;continue
        if b['start']>=0:
            running_high=max(running_high,b['high']);running_low=min(running_low,b['low'])
        # Existing confirmed swing only: current confirming bar cannot rewrite
        # the swing level that this same closed bar crossed.
        if previous is not None:
            if 'high' in swing and previous['close']<=swing['high']<b['close']:mss[1]=b['end']
            if 'low' in swing and previous['close']>=swing['low']>b['close']:mss[-1]=b['end']
        if start<=b['start']<finish:
            sweep_allowed=b['start']<45 if spec.family=='ICT3' else True
            if sweep_allowed:
                if spec.family=='ICT3':
                    down=b['low']<=anchor-.15*atr;up=b['high']>=anchor+.15*atr
                else:
                    low,high=levels;down=b['low']<low;up=b['high']>high
                if down and up:seen.update((1,-1))
                if not (down and up):
                    for side,hit in ((1,down),(-1,up)):
                        if hit and side not in seen:
                            sweeps[side]=dict(boundary=b['end'],extreme=b['low'] if side==1 else b['high'])
                            seen.add(side)
                # The extreme may develop after the first sweep, but only
                # completed observations through this signal are accessible.
            for side,state in sweeps.items():
                state['extreme']=min(state['extreme'],b['low']) if side==1 else max(state['extreme'],b['high'])
            gap=fvg(bars,j,atr)
            if gap is not None and b['end']<finish:
                side=gap['direction'];sweep_side=-side if spec.family=='ICT2' and spec.mode=='CONTINUE' else side
                sweep=sweeps.get(sweep_side)
                known_chain=sweep is not None and sweep['boundary']<=gap['middle_start']
                if known_chain and allowed(spec,ctx,side):
                    valid=True;draw=None
                    if spec.family=='ICT1':valid=mss.get(side) in (bars[j-1]['end'],b['end']) and mss.get(side)>sweep['boundary']
                    if spec.family=='ICT2' and spec.mode=='CONTINUE':
                        candidates=[ctx.get(k,np.nan) for k in (('PDH','ONH') if side==1 else ('PDL','ONL'))]
                        candidates=[x for x in candidates if np.isfinite(x) and (x>running_high if side==1 else x<running_low)]
                        valid=bool(candidates);draw=(min(candidates) if side==1 else max(candidates)) if candidates else None
                    if spec.family=='ICT3':valid=side*(b['close']-ctx['OPEN0930'])>0
                    if valid:
                        entry=gap['entry']
                        structural=gap['structural'] if spec.family=='ICT2' else sweep['extreme']-side*TICK
                        stop=floor_tick(min(structural,entry-.10*atr)) if side==1 else ceil_tick(max(structural,entry+.10*atr))
                        risk=side*(entry-stop)
                        target=entry+side*(2 if spec.target=='2R' else 3)*risk if spec.target in ('2R','3R') else opposite(ctx,side) if spec.target=='OPPOSITE_ON' else None
                        if target is not None:target=ceil_tick(target) if side==1 else floor_tick(target)
                        return dict(boundary=b['end'],expires=finish,direction=side,entry=entry,stop=stop,
                                    risk=risk,target=target,valid_target=target is None or (np.isfinite(target) and side*(target-entry)>0),
                                    sweep_boundary=sweep['boundary'],sweep_extreme=sweep['extreme'],mss_boundary=mss.get(side),
                                    fvg_size=gap['size'],draw=draw)
        swing.update(confirmed(bars,j));previous=b
    return None


def execute(p,order,touch=True):
    if order is None:return None,'NO_SIGNAL'
    if not order['valid_target']:return None,'INVALID_FIRST_TARGET_NO_RESELECT'
    side=order['direction'];entry=order['entry'];stop=order['stop'];target=order['target'];entry_ix=None
    # Convert to RTH-array, never examine preactivation/forming-bar lows.
    r={k:np.asarray(p[k][90:],float) for k in FIELDS}
    for i in range(order['boundary'],min(order['expires'],EXIT,len(r['open']))):
        op,hi,lo=(float(r[k][i]) for k in ('open','high','low'))
        required=entry if touch else entry-side*TICK
        hit=lo<=required if side==1 else hi>=required
        if hit:
            entry_ix=i;at_open=op<=required if side==1 else op>=required;break
    if entry_ix is None:return None,'UNFILLED_FIRST_ORDER'
    marks=[-FEE];end=EXIT;exit_=None;reason='TIME_1555';exit_open=True
    for i in range(entry_ix,EXIT):
        op,hi,lo,cl=(float(r[k][i]) for k in ('open','high','low','close'))
        opening_known=i>entry_ix or at_open
        if opening_known and side*(op-stop)<=0:exit_=op;end=i;reason='STOP_GAP';exit_open=True;break
        if opening_known and target is not None and side*(op-target)>=0:
            exit_=target;end=i;reason='TARGET_OPEN';exit_open=True;break
        # Conservative entry-bar and unresolved stop/target conflicts.
        stop_hit=lo<=stop if side==1 else hi>=stop
        if stop_hit:exit_=stop;end=i;reason='STOP';exit_open=False;break
        target_hit=target is not None and (hi>=target if side==1 else lo<=target)
        if target_hit and (opening_known or side*(cl-target)>=0):
            exit_=target;end=i;reason='TARGET';exit_open=False;break
        if opening_known:marks.append(side*(op-entry)-FEE)
        marks.append(side*(cl-entry)-FEE)
    if exit_ is None:exit_=float(r['open'][EXIT])
    if not exit_open and (end>entry_ix or at_open):marks.append(side*(float(r['open'][end])-entry)-FEE)
    gross=side*(exit_-entry);net=gross-FEE;marks.append(net)
    return dict(entry_bar=entry_ix,exit_bar=end,entry_price=entry,exit_price=exit_,stop_price=stop,
                target_price=target,direction=side,initial_risk=order['risk'],gross_points=gross,net_points=net,
                net_stop_R=net/order['risk'],reason=reason,entry_at_open=at_open,exit_at_open=exit_open,path_points=marks),'FILLED'


def retarget(order,ctx,spec):
    if order is None:return None
    out=dict(order);side=out['direction'];entry=out['entry']
    target=entry+side*(2 if spec.target=='2R' else 3)*out['risk'] if spec.target in ('2R','3R') else opposite(ctx,side) if spec.target=='OPPOSITE_ON' else None
    if target is not None:target=ceil_tick(target) if side==1 else floor_tick(target)
    out.update(target=target,valid_target=target is None or (np.isfinite(target) and side*(target-entry)>0))
    return out
