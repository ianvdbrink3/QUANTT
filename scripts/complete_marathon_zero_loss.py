"""Documented completeness correction: no-loss PF is not a reason to omit history.

No model, signal, threshold, date or family added. The original release and
original history are preserved. This selected cell had not been outcome-
evaluated on historical samples. No-loss PF stays undefined, not certified.
"""
import json
import numpy as np
import pandas as pd
from scripts.edge_marathon.runner import ROOT,OUT,verify,safe_dump,scored
from scripts.edge_marathon.data import historical_samples
from scripts.edge_marathon.core import catalog,select,fill
from scripts.edge_marathon.stats import holm
from scripts.afternoon_inference_round import sha


def run():
    verify()
    d=json.loads((OUT/'discovery.json').read_text())
    release=json.loads((OUT/'historical-release.json').read_text())
    additional=[n for n,r in d['models'].items() if not n.startswith('TOM_') and
        r['metrics']['trades']>0 and r['metrics']['net_points']>0 and r['metrics'].get('profit_factor') is None and n not in release['selected']]
    original=OUT/'historical.json';preserved=OUT/'historical-before-zero-loss-completion.json'
    payload=original.read_bytes()
    if preserved.exists() and preserved.read_bytes()!=payload:
        # The completeness pass is idempotent; replay the base history route
        # before calling it again when source-reloading the whole pipeline.
        current=json.loads(payload)
        if 'completeness_addendum' in current:return current
        raise ValueError('Original history changed before completeness pass')
    if not preserved.exists():preserved.write_bytes(payload)
    amendment=dict(status='COMPLETENESS_ONLY_NO_NEW_STRATEGY_OR_PARAMETERS',
        original_release_sha256=sha(OUT/'historical-release.json'),original_history_sha256=sha(preserved),
        additional_models=additional,registered_family_size=25,
        reason='Positive discovery PnL with no observed losing trades has no finite PF estimate. Include such predefined rows in descriptive historical replication rather than silently omitting an all-win subgroup. This does not promote or assign an infinite certified PF.',
        prior_historical_outcomes_for_these_rows_computed=False,
        qualification='Engineering completeness amendment after original selected rows were inspected; not an independent new preregistration. No threshold/model/horizon/period changes.')
    path=OUT/'historical-zero-loss-release.json'
    if path.exists() and json.loads(path.read_text())!=amendment:raise ValueError('Completeness addendum changed')
    safe_dump(path,amendment)
    # Only now evaluate the missing registered cell on historical samples.
    h=json.loads(payload);samples,_=historical_samples()
    for sample in samples:
        name=sample['name'];state=sample['state']
        if state is None or name not in h['samples'] or 'models' not in h['samples'][name]:continue
        ledger=OUT/(name.lower()+'-trades.csv')
        rows=pd.read_csv(ledger).to_dict('records')
        additions=[]
        for day in sample['included']:
            prices,ctx=state[day]
            for event in select(prices,ctx):
                if event['model'] not in additional:continue
                r=fill(event,prices,ctx);r.update(day=day,source_sample=name,tom_position=ctx.get('tom_position'));additions.append(r)
        rows.extend(additions)
        scores=scored(rows,list(pd.bdate_range(sample['days'][0],sample['days'][-1]).strftime('%Y-%m-%d')),state,sample['included'])
        h['samples'][name]['models']=scores
        h['samples'][name]['selected_model_ids']=sorted(set(h['samples'][name]['selected_model_ids'])|set(additional))
        h['samples'][name]['zero_loss_completeness_events']=len(additions)
        # Preserve existing ledger column order. Net values are exact to3dp;
        # 10dp serialization does not change the exchange tick/cost arithmetic.
        pd.DataFrame(rows).to_csv(ledger,index=False,float_format='%.10f')
    pairs=[(s,n) for s,r in h['samples'].items() if 'models' in r for n in catalog()]
    for (s,n),p in zip(pairs,holm([h['samples'][s]['models'][n]['inference']['signflip_p'] for s,n in pairs])):
        h['samples'][s]['models'][n]['inference']['signflip_holm_all_historical_sources']=p
    h['completeness_addendum']=amendment
    safe_dump(original,h)
    print('No-loss completeness cells evaluated without new hypotheses:',additional,flush=True)
    return h


if __name__=='__main__':run()
