"""Independent selector/fill implementation for engineering parity only.

Shares source parsing and precomputed causal contexts, NOT select()/fill().
Written after discovery: not an independent investigator or validation set.
"""
import json
import numpy as np
import pandas as pd
from scripts.edge_marathon.runner import ROOT,OUT,verify,safe_dump
from scripts.edge_marathon.features import enrich
from scripts.edge_marathon.data import historical_samples
from scripts.afternoon_inference_round import sha


def reference(prices,c,day,discovery=False):
    events=[];op=prices['open'][0];closing=prices['close']
    tom=bool(c['tom'] and not (discovery and day<'2025-01-01'))
    def signal(name,entry,end,direction,decision=None):
        events.append((name,entry,end,direction,entry if decision is None else decision))
    if tom:
        signal('TOM_RTH',0,390,1)
        signal('TOM_OVERNIGHT_1030',-930,60,1)
        if closing[29]>op:signal('TOM_TREND_1000',30,390,1)
        if np.isfinite(c['atr_p90']) and np.isfinite(c['atr']) and c['atr']<=c['atr_p90']:
            signal('TOM_ATR_CAP',0,390,1)
    if pd.Timestamp(day).weekday()==4 and np.isfinite(c['week_open']):
        movement=closing[239]-c['week_open']
        if movement:
            direction=1 if movement>0 else -1
            signal('FRIDAY_CONT',240,390,direction)
            signal('FRIDAY_REVERT',240,390,-direction)
    if c['overnight_complete'] and c['overnight_rvol'] is not None and np.isfinite(c['atr']):
        width=c['overnight_high']-c['overnight_low'];change=c['on_close']-c['overnight_open']
        eff=abs(change)/width if width else 0.
        if change!=0 and eff>=.7 and width<=.8*c['atr'] and c['overnight_rvol']>=1.5:
            direction=1 if change>0 else -1
            signal('ON_INVENTORY_CONT',0,120,direction);signal('ON_INVENTORY_REVERT',0,120,-direction)
    if np.isfinite(c['PDH']) and np.isfinite(c['PDL']) and np.isfinite(c['atr']) and c['atr']>0 and c['PDH']-c['PDL']<.65*c['atr']:
        for minute in range(390):
            if minute%5!=4 or minute>=385:continue
            direction=1 if closing[minute]>c['PDH'] else -1 if closing[minute]<c['PDL'] else 0
            if direction:
                signal('COMPRESSED_BREAK5',minute+1,390,direction);break
    if np.isfinite(c['ONH']) and np.isfinite(c['ONL']):
        upper=False;lower=False
        for minute in range(30):
            upper=upper or prices['high'][minute]>c['ONH'];lower=lower or prices['low'][minute]<c['ONL']
        close=closing[29];inside=c['ONL']<close<c['ONH']
        direction=1 if lower and not upper and inside and close>op else -1 if upper and not lower and inside and close<op else 0
        if direction:
            signal('SWEEP_REV_1200',30,150,direction);signal('SWEEP_REV_1600',30,390,direction)
    if np.isfinite(c['atr']) and c['atr']>0:
        high=-np.inf;low=np.inf
        for minute in range(300):
            high=max(high,prices['high'][minute]);low=min(low,prices['low'][minute])
        ratio=(high-low)/c['atr']
        if closing[299]>op and ratio>=.5 and ratio<1.2:
            for horizon in (2,15):
                signal('AFTERNOON_V2_'+str(horizon),330,330+horizon,1,300)
                if c['atr_regime']:
                    label=f'AFTERNOON_TOM_{"YES" if tom else "NO"}_{c["atr_regime"]}_{horizon}'
                    signal(label,330,330+horizon,1,300)
    return events


def reference_fill(prices,c,event):
    name,start,end,direction,decision=event
    if start<0 and not c['overnight_complete']:return None
    entry=c['overnight_open'] if start<0 else prices['open'][start]
    max_up=max_down=0.
    if start<0:
        max_up=max(0.,c['overnight_high']-entry);max_down=max(0.,entry-c['overnight_low'])
    for minute in range(max(0,start),end):
        max_up=max(max_up,prices['high'][minute]-entry);max_down=max(max_down,entry-prices['low'][minute])
    close=prices['close'][end-1];gross=(close-entry)*direction
    return dict(model=name,entry=start,end=end,direction=direction,decision=decision,
        entry_price=float(entry),exit_price=float(close),gross_points=float(gross),net_points=float(gross-1.225),
        mfe_points=float(max_up if direction>0 else max_down),mae_points=float(max_down if direction>0 else max_up))


def compare(sample,state,included,selected=None):
    actual=pd.read_csv(OUT/('discovery-trades.csv' if sample=='DISCOVERY' else sample.lower()+'-trades.csv'))
    expected={}
    for day in included:
        p,c=state[day]
        for e in reference(p,c,day,sample=='DISCOVERY'):
            if selected is not None and e[0] not in selected:continue
            row=reference_fill(p,c,e)
            if row:expected[e[0],day]=row
    keys=set(zip(actual.model,actual.day))
    if keys!=set(expected):raise AssertionError('Independent selector mismatch '+sample+str(keys^set(expected)))
    fields=['entry','end','direction','decision','entry_price','exit_price','gross_points','net_points','mfe_points','mae_points']
    max_difference=0.
    for row in actual.to_dict('records'):
        other=expected[row['model'],row['day']]
        for field in fields:
            error=abs(row[field]-other[field]);max_difference=max(max_difference,error)
            if error>1e-8:raise AssertionError(f'Independent fill mismatch {sample} {row["day"]} {row["model"]} {field}')
    return dict(sample=sample,complete_days=len(included),events=len(expected),compared_fields=fields,
        maximum_absolute_difference=max_difference,status='INDEPENDENT_SELECTOR_AND_FILL_IMPLEMENTATION_MATCH')


def run():
    verify()
    from scripts.causal_map.__main__ import load_inputs
    state,days,inc,_,active,cal,rolls=load_inputs();state=enrich(state,days,active,rolls)
    results=[compare('DISCOVERY',state,inc)]
    h=json.loads((OUT/'historical.json').read_text());samples,_=historical_samples()
    for s in samples:
        if s['state'] is None or not s['included']:continue
        results.append(compare(s['name'],s['state'],s['included'],set(h['samples'][s['name']]['selected_model_ids'])))
    result=dict(status='INDEPENDENT_SELECTOR_FILL_REFERENCE_PARITY_PASSED',samples=results,
        reference_code_sha256=sha(__file__),
        limitation='Independent implementation of fixed selectors and fill/excursion arithmetic, but same author/machine, shared source parser and causal context. Engineering verification, NOT independent market validation.')
    safe_dump(ROOT/'research/edge-marathon-reference-parity.json',result)
    print(result['status'],sum(r['events'] for r in results),'events',flush=True)
    return result


if __name__=='__main__':run()
