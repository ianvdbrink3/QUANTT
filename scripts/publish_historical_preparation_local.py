"""Copy only aggregate quality report to local dashboard. No network writes."""
import json
from scripts.prepare_historical_contracts import ROOT, REPORT, RESULT, PUBLIC, verify, sha, dump


def run():
    integrity=verify()
    data=json.loads(RESULT.read_text())
    assert data['signals_computed'] is False and data['holdout_executed'] is False
    assert RESULT.read_bytes()==PUBLIC.read_bytes()
    assert '/Users/' not in PUBLIC.read_text() and 'entry_price' not in PUBLIC.read_text()
    target=ROOT/'public/reports/HISTORICAL_2019_2021_PREPARATION.md'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(REPORT.read_bytes())
    result=dict(status='LOCAL_AGGREGATE_REPORT_ONLY',external_publication=False,**integrity,
        report_sha256=sha(REPORT),json_sha256=sha(PUBLIC))
    dump(ROOT/'research/historical-preparation-local-publication.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':run()
