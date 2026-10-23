"""Read-only local dashboard/data/report boundary checks."""
import json
import urllib.error
import urllib.request
from scripts.survivor_portfolio import ROOT,dump,verify


def run():
    base='http://127.0.0.1:3012';checks=[]
    for url,local in [('/data/three-survivors.json','public/data/three-survivors.json'),
        ('/data/three-survivors-verification.json','public/data/three-survivors-verification.json'),
        ('/data/three-survivors-preregistration.json','public/data/three-survivors-preregistration.json'),
        ('/reports/THREE_SURVIVORS_ATR_PORTFOLIO.md','public/reports/THREE_SURVIVORS_ATR_PORTFOLIO.md'),
        ('/reports/THREE_SURVIVORS_PREREGISTRATION_2019_2021.md','public/reports/THREE_SURVIVORS_PREREGISTRATION_2019_2021.md')]:
        with urllib.request.urlopen(base+url) as r:
            payload=r.read();assert r.status==200 and payload==(ROOT/local).read_bytes()
        checks.append(dict(route=url,status=200,byte_identical=True))
    with urllib.request.urlopen(base+'/research/three-survivors') as r:
        page=r.read().decode();assert r.status==200
        for text in ('Drie signalen.','4,407','4,220','onbevestigd','Holm8','MNQ','geregistreerd'):
            assert text in page,text
        assert '/Users/' not in page and 'entry_price' not in page
    checks.append(dict(route='/research/three-survivors',status=200,aggregate_rendering=True))
    for private in ('/data/raw/historical-replication-2019-2021/nqh19_intraday-1min_historical-data-10-22-2026-4.csv',
                    '/research/three-survivors-lock.json','/artifacts/three-survivors/discovery-trades.json'):
        try:urllib.request.urlopen(base+private)
        except urllib.error.HTTPError as e:assert e.code==404
        else:raise ValueError('Private research exposed')
        checks.append(dict(route=private,status=404))
    verify()
    result=dict(status='LOCAL_BROWSER_DATA_REPORT_BOUNDARIES_VERIFIED',checks=checks,
        screenshots='Native browser rendering inspected separately; no user Safari interaction needed.',
        server='Local production build only, no external deployment',external_publication=False)
    dump(ROOT/'research/three-survivors-browser-verification.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':run()
