"""Read-only localhost dashboard integration check. Never deploys or scores."""
import hashlib
import json
from urllib.request import urlopen
from urllib.error import HTTPError
from scripts.prepare_historical_contracts import ROOT, PUBLIC, REPORT, dump, verify


def run():
    base='http://127.0.0.1:3012'
    checks={}
    for route,path in [('/data/historical-preparation.json',PUBLIC),
        ('/data/historical-preparation-review.json',ROOT/'public/data/historical-preparation-review.json'),
        ('/reports/HISTORICAL_2019_2021_PREPARATION.md',REPORT),
        ('/reports/HISTORICAL_2019_2021_TECHNICAL_REVIEW.md',ROOT/'docs/HISTORICAL_2019_2021_TECHNICAL_REVIEW.md')]:
        with urlopen(base+route,timeout=15) as response:
            body=response.read()
            if body!=path.read_bytes():raise AssertionError('Served data differs: '+route)
            checks[route]=dict(status=response.status,sha256=hashlib.sha256(body).hexdigest())
    with urlopen(base+'/research/historical-preparation',timeout=15) as response:
        text=response.read().decode()
        for expected in ('Alle downloads binnen.','733','706','619','EXPLICIT_OUTCOME_RELEASE_REQUIRED'):
            if expected not in text:raise AssertionError('Rendered output missing '+expected)
        checks['page']=dict(status=response.status,expected_counts_visible=True)
    for route in ('/data/raw/historical-replication-2019-2021/','/artifacts/historical-preparation/active-bars.parquet'):
        try:
            with urlopen(base+route,timeout=15):raise AssertionError('Private path unexpectedly served')
        except HTTPError as exc:
            if exc.code!=404:raise
            checks[route]=dict(status=404)
    result=dict(status='LOCAL_UI_AGGREGATE_FLOW_VERIFIED',checks=checks,integrity=verify(),external_publication=False)
    dump(ROOT/'research/historical-preparation-http-verification.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':run()
