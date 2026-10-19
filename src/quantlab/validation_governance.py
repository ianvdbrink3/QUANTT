"""Conservative validation governance for source-agnostic QUANT experiments."""
from __future__ import annotations
from dataclasses import dataclass,asdict
from pathlib import Path
import hashlib
import json
import pandas as pd
import numpy as np

@dataclass(frozen=True)
class ResearchFamily:
    family_id: str
    hypothesis_ids: tuple[str,...]
    max_trials: int
    seed: int=17
    def validate(self):
        if not self.family_id or len(set(self.hypothesis_ids))!=len(self.hypothesis_ids) or self.max_trials<1:
            raise ValueError('Invalid experiment family definition')
        if len(self.hypothesis_ids)>self.max_trials:
            raise ValueError('Predeclared family exceeds research budget')
        return self

def purge_overlapping_events(events:pd.DataFrame, cutoff, embargo_minutes=0)->dict:
    """Split event intervals; remove training events overlapping validation.

    Interval endpoints must be precomputed from signal start and forward horizon.
    Train events with end >= cutoff are removed, as are events in embargo.
    """
    required={'event_start_utc','event_end_utc'}
    if not required.issubset(events): raise ValueError('Missing event interval')
    if embargo_minutes<0: raise ValueError('Negative embargo')
    x=events.copy()
    x['event_start_utc']=pd.to_datetime(x.event_start_utc,utc=True)
    x['event_end_utc']=pd.to_datetime(x.event_end_utc,utc=True)
    if x.event_start_utc.isna().any() or x.event_end_utc.isna().any() or (x.event_end_utc<x.event_start_utc).any():
        raise ValueError('Invalid event interval')
    edge=pd.Timestamp(cutoff)
    if edge.tzinfo is None: raise ValueError('Cutoff must be timezone-aware')
    edge=edge.tz_convert('UTC')
    embargo=pd.Timedelta(minutes=embargo_minutes)
    training=x[(x.event_end_utc<edge)&(x.event_end_utc<edge-embargo)]
    later=x[x.event_start_utc>=edge+embargo]
    dropped=len(x)-len(training)-len(later)
    return {'train':training.copy(),'evaluation':later.copy(),'purged_or_embargoed':dropped}

def holdout_lock(path:str|Path, *,data_hash:str, configuration_hash:str, family_id:str)->dict:
    """Immutable one-shot approval barrier, never an automatic holdout-unseal."""
    if not all((data_hash,configuration_hash,family_id)): raise ValueError('Missing holdout identity')
    payload={'data_hash':data_hash,'configuration_hash':configuration_hash,'family_id':family_id,
             'state':'SEALED','unsealed':False}
    target=Path(path);target.parent.mkdir(parents=True,exist_ok=True)
    value=json.dumps(payload,sort_keys=True,separators=(',',':'))
    if target.exists():
        old=target.read_text(encoding='utf-8')
        if old!=value:
            raise ValueError('Holdout lock exists with a different identity')
        return payload
    with target.open('x',encoding='utf-8') as handle:
        handle.write(value)
    return payload

def robustness_gate(values, *,min_events=30, tail_fraction=.05, max_tail_dependency=.5)->dict:
    """Discourage results entirely driven by a few outliers; not a p-value."""
    x=np.asarray(values,dtype=float)
    if not len(x) or not np.isfinite(x).all():
        raise ValueError('Invalid results')
    if not 0<=tail_fraction<.5 or not 0<=max_tail_dependency<=1:
        raise ValueError('Invalid robust-gate thresholds')
    if len(x)<min_events:
        return {'status':'STATISTICALLY INCONCLUSIVE','reason':'INSUFFICIENT EVENTS',
                'events':len(x),'mean':float(x.mean())}
    k=max(1,int(np.ceil(len(x)*tail_fraction)))
    ordered=np.sort(x)
    trimmed=ordered[k:-k]
    full=float(x.mean());trim=float(trimmed.mean())
    # Sign flip is a signal of tail dependence; no validation claim either way
    unstable=np.sign(full)!=np.sign(trim)
    return {'status':'REQUIRES INDEPENDENT VALIDATION' if not unstable else 'STATISTICALLY INCONCLUSIVE',
            'events':len(x),'mean':full,'trimmed_mean':trim,
            'direction_flips_without_tails':bool(unstable),
            'note':'Descriptive fragility screen only; not a tradeable-edge certification'}

def orchestrator_protocol()->dict:
    """Serializable deterministic roles; future LLMs can propose but not approve."""
    return {'version':1,'live_trading_enabled':False,
            'roles':[
               {'name':'Research Director','output':'frozen_hypothesis_config'},
               {'name':'Data Analyst','output':'quality_gate'},
               {'name':'Feature Researcher','output':'known_at_feature_manifest'},
               {'name':'Strategy Researcher','output':'event_specification'},
               {'name':'Quant Validator','output':'independent_validation_report'},
               {'name':'Risk Analyst','output':'cost_and_drawdown_sensitivity'},
               {'name':'Research Auditor','output':'provenance_and_holdout_audit'}],
            'execution':'deterministic_python_only','llm_may_approve_edge':False}
