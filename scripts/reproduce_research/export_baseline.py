"""Additive baseline view; never edits frozen reference files."""
import json
from .holdout_data import REPO, sha


def export():
    source=REPO/'research/holdout-reference.json'
    data=json.loads(source.read_text())
    result={'label':'Baseline v0.9','period':data['period'],
            'source_sha256':sha(source),'cost_rt_usd':data['cost_rt_usd'],
            'rollover_readiness_regression_tests':7,
            'verified_suite_before_continuous_extension':168,
            'interpretation':'All four screens fail positive net profitability on the observed holdout; not proof of universal absence of an edge. Only ORB15 was the primary hypothesis.',
            'screens':[{ 'id':key,'status':'HOLDOUT_FAILED' if key=='B_ORB15' else 'REFERENCE_NEGATIVE_NET',
                        **data['holdout'][key]['all']} for key in
                       ['A_London_sweep','B_ORB5','B_ORB15','C_VWAP_extreme']]}
    assert all(x['net_points']<0 and x['profit_factor']<1 for x in result['screens'])
    (REPO/'public/data/research-baseline09.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    export()
