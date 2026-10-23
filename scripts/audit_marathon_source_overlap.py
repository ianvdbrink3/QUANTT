"""Fixed-convention source parity, not a new strategy/clock search."""
import json
import numpy as np
import pandas as pd
from scripts.edge_marathon.data import ROOT,OUT,basic_frame,verify_source_register
from scripts.edge_marathon.runner import safe_dump,verify
from scripts.oos_preparation.year import load_registered
from scripts.oos_preparation.route import select_active
from scripts.reproduce_research.next_engine import Activation


def run():
    verify();sources=verify_source_register()
    row=next(r for r in sources['records'] if r['filename']=='Dataset_NQ_1min_2022_2025.csv')
    # Exactly the existing ET bar-end minus1minute convention. No search over
    # shifts, alternative labels, rules, thresholds or holding horizons.
    generic=basic_frame(row['paths'][0],'GENERIC')
    full,_,_=load_registered()
    prior=json.loads((ROOT/'research/holdout-protocol.json').read_text())
    year=json.loads((ROOT/'research/oos-year-rollovers.json').read_text())
    schedule=[Activation('NQH25','2024-12-30'),Activation('NQM25','2025-03-19')]
    schedule += [Activation(r['to'],r['effective_session']) for r in prior['rollovers']+year['rollovers']]
    active=select_active(full,schedule)
    common=generic.index.intersection(active.index)
    clock=common.tz_convert('America/New_York').strftime('%H:%M')
    common=common[(clock>='09:30') & (clock<'16:00')]
    a=generic.loc[common];b=active.loc[common]
    oc=(a.close-a.open).to_numpy()-(b.close-b.open).to_numpy()
    ranges=(a.high-a.low).to_numpy()-(b.high-b.low).to_numpy()
    offsets=pd.DataFrame(dict(offset=(a.close-b.close).to_numpy(),day=b.trade_date.to_numpy()))
    variability=offsets.groupby('day').offset.agg(lambda s:float(s.max()-s.min()))
    checked=[]
    for day,g in b.groupby('trade_date'):
        local=g.index.tz_convert('America/New_York').strftime('%H:%M')
        start=g.index[local=='15:00'];end=g.index[local=='15:01']
        if len(start)!=1 or len(end)!=1:continue
        t,u=start[0],end[0]
        checked.append(float((generic.at[u,'close']-generic.at[t,'open'])-(active.at[u,'close']-active.at[t,'open'])))
    result=dict(status='FIXED_TIMESTAMP_CONVENTION_SOURCE_PARITY_CHECK',common_rth_minutes=len(common),
        common_days=int(b.trade_date.nunique()),volume_exact_fraction=float(np.mean(a.volume.to_numpy()==b.volume.to_numpy())),
        minute_open_close_move_exact_fraction=float(np.mean(np.isclose(oc,0,atol=1e-8,rtol=0))),
        minute_range_exact_fraction=float(np.mean(np.isclose(ranges,0,atol=1e-8,rtol=0))),
        daily_close_offset_constant_fraction=float(np.mean(variability.eq(0))),
        minute_open_close_difference_abs_median=float(np.median(abs(oc))),
        fifteen00_two_minute_anchor_days=len(checked),
        fifteen00_two_minute_move_exact_fraction=float(np.mean(np.isclose(checked,0,rtol=0,atol=1e-8))),
        fifteen00_two_minute_move_difference_abs_median=float(np.median(abs(np.asarray(checked)))),
        source_sha256=row['sha256'],
        caveat='Common observed2024-2025dates only, not proof of older contract chain or vendor independence. Shared feed possible. No shift search, no rules changed, no certification of publication vintage or tick fills.')
    safe_dump(OUT/'source-overlap-parity.json',result)
    # Technical feasibility explanation for zero inventory events, no relaxed
    # threshold or rerun of a modified model.
    from scripts.causal_map.__main__ import load_inputs
    from scripts.edge_marathon.features import enrich
    state,days,included,_,active,cal,rolls=load_inputs();state=enrich(state,days,active,rolls)
    stages=dict(total=len(included),complete_overnight=0,known_atr=0,known_20night_rvol=0,
                efficiency_at_least_07=0,range_at_most_08atr=0,rvol_at_least_15=0,all_three_conditions=0)
    for day in included:
        _,c=state[day]
        if not c['overnight_complete']:continue
        stages['complete_overnight']+=1
        if not np.isfinite(c['atr']):continue
        stages['known_atr']+=1
        if c['overnight_rvol'] is None:continue
        stages['known_20night_rvol']+=1
        width=c['overnight_high']-c['overnight_low']
        efficiency=abs(c['on_close']-c['overnight_open'])/width if width else 0.
        e=efficiency>=.7;r=width<=.8*c['atr'];v=c['overnight_rvol']>=1.5
        stages['efficiency_at_least_07']+=int(e);stages['range_at_most_08atr']+=int(r)
        stages['rvol_at_least_15']+=int(v);stages['all_three_conditions']+=int(e and r and v)
    safe_dump(OUT/'inventory-feasibility.json',dict(counts=stages,
        interpretation='Zero events is feasibility/data insufficiency, not evidence that the inventory mechanism is false. No conditions relaxed after inspection. Individual-condition counts use the same final known-history population, not successive conditional counts.'))
    print(json.dumps(result,indent=2));print(stages,flush=True)


if __name__=='__main__':run()
