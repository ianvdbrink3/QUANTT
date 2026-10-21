"""Publish only preparation metadata and CONSUMED-data planning aggregates."""
import json
from pathlib import Path

from .adapter import sha

ROOT = Path(__file__).resolve().parents[2]


def run():
    source = ROOT/'artifacts/oos-preparation/summary.json'
    d = json.loads(source.read_text())
    if d['scoring_run'] or d['signals_computed'] or d['status'] != 'DATA_INSUFFICIENT':
        raise ValueError('Only unscored blocked preparation may be published here')
    keys = ['classification','status','target_period','blockers','unique_bars_oct_dec','session_dates',
            'standard_clean_days','complete_noon_prefix_days','active_contract_eligible_days',
            'eligibility_note','unresolved_missing_minutes','missing_full_dates','prior_access_evidence',
            'scoring_run','signals_computed','power_planning']
    public = {k:d[k] for k in keys}
    public['quality_exceptions'] = d['exceptions']
    public['source_count'] = len(d['source_manifest']['sources'])
    public['source_manifest_sha256'] = sha(source.parent/'source-manifest.json')
    public['calendar_sha256'] = d['source_manifest']['calendar_sha256']
    public['frozen_protocol_sha256'] = d['source_manifest']['frozen_protocol_sha256']
    public['download_plan'] = json.loads((ROOT/'research/oos-download-plan.json').read_text())
    public['sealing_limit'] = 'Software separation and integrity checks, NOT OS-level access control or proof nobody inspected prices.'
    out = ROOT/'public/data/research-oos-preparation.json'
    out.write_text(json.dumps(public,indent=2)+'\n')
    registry = ROOT/'research/oos-source-register.json'
    registry.write_text(json.dumps(d['source_manifest'],indent=2)+'\n')
    print(json.dumps({'published_aggregate_sha256':sha(out),'source_register_sha256':sha(registry),'future_returns_published':False}))


if __name__ == '__main__':
    run()
