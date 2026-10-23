"""Record the local quality-only handoff, without accepting an outcome release."""
import json
from scripts import prepare_historical_contracts as h


def run():
    integrity=h.verify()
    names=['research/historical-preparation-protocol.json','research/historical-preparation-lock.json',
        'research/historical-2019-2021-complete-source-register.json',
        'research/historical-preparation-quality.json','research/historical-preparation-review.json',
        'research/historical-preparation-verification.json','research/historical-preparation-http-verification.json',
        'scripts/prepare_historical_contracts.py','scripts/review_historical_preparation.py',
        'scripts/publish_historical_preparation_local.py','scripts/verify_historical_preparation_http.py',
        'scripts/finalize_historical_preparation.py','tests/test_historical_preparation.py',
        'tests/test_historical_preparation_outputs.py','app/research/historical-preparation/page.tsx',
        'docs/HISTORICAL_2019_2021_PREPARATION.md','docs/HISTORICAL_2019_2021_TECHNICAL_REVIEW.md',
        'public/data/historical-preparation.json','public/data/historical-preparation-review.json',
        'public/reports/HISTORICAL_2019_2021_PREPARATION.md','public/reports/HISTORICAL_2019_2021_TECHNICAL_REVIEW.md']
    names += [str(p.relative_to(h.ROOT)) for p in sorted(h.OUT.glob('*')) if p.is_file()]
    hashes={name:h.sha(h.ROOT/name) for name in names}
    value=dict(status='QUALITY_ONLY_HANDOFF_NOT_FINAL_VALIDATION_RELEASE',date='2026-10-23',
        outcome_release=False,new_2019_2021_strategy_signals=False,external_publication=False,
        files_sha256=hashes,integrity=integrity,
        open_conditions=json.loads((h.ROOT/'research/historical-preparation-review.json').read_text())['remaining_blockers'],
        local_dashboard='http://127.0.0.1:3012/research/historical-preparation')
    path=h.ROOT/'research/historical-preparation-final-manifest.json'
    if path.exists() and json.loads(path.read_text())!=value:
        raise ValueError('Existing handoff changed; create an explicit version, do not replace silently')
    h.dump(path,value)
    print(json.dumps(dict(status=value['status'],hashed_files=len(hashes),**integrity),indent=2))


if __name__=='__main__':run()
