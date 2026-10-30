"""Flow-adjusted risk on allocated capital, not a misleading50k demo balance."""
from .common import dec

LIMITS={'defensive':(dec('.10'),dec('.15')),'balanced':(dec('.20'),dec('.25')),'offensive':(dec('.35'),dec('.40'))}


def update_risk(store,c,snapshot):
    base=store.get('cash_baseline')
    if not base:raise ValueError('RISK_BASELINE_RECONCILIATION_REQUIRED')
    account=str(snapshot['account']['id']);initial=dec(c['strategy_initial_capital'])
    value=dec(snapshot['account']['totalValue']);state=store.get('strategy_risk')
    if state is None:
        if value<initial:raise ValueError('STRATEGY_CAPITAL_EXCEEDS_DEMO_FUNDS')
        state=dict(account=account,initial=str(initial),unallocated=str(value-initial),units=str(initial),peak='1',applied_flows=[])
    if state['account']!=account or dec(state['initial'])!=initial:raise ValueError('STRATEGY_CAPITAL_CHANGE_REQUIRES_REVIEW')
    nav=value-dec(state['unallocated']);units=dec(state['units'])
    events=store.get('cash_events',{})
    fresh={k:v for k,v in events.items() if v.get('external_flow') and k not in state['applied_flows']}
    flow=sum((dec(v['external_flow']) for v in fresh.values()),dec(0))
    if flow:
        before=nav-flow
        if before<=0 or nav<=0:raise ValueError('INVALID_CAPITAL_FLOW')
        units*=nav/before;state['applied_flows'].extend(fresh)
    if units<=0:raise ValueError('INVALID_RISK_UNITS')
    unit=nav/units;peak=max(unit,dec(state['peak']));dd=1-unit/peak
    state.update(units=str(units),peak=str(peak))
    store.set('strategy_risk',state)
    warning,hard=LIMITS[c['profile']]
    if dd>=hard:store.halt('DRAWDOWN_HUMAN_REVIEW_REQUIRED')
    snapshot['strategy_nav']=str(nav);snapshot['risk_warning']=dd>=warning
    return dict(drawdown_pct=float(dd*100),warning=dd>=warning,hard_limit_pct=float(hard*100),halt=dd>=hard,
        basis='FLOW_ADJUSTED_ALLOCATED_CAPITAL',not_a_guaranteed_loss_cap=True)
