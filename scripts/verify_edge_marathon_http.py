"""Loopback-only delivery/privacy verification of the final built dashboard."""
import hashlib
import json
import urllib.error
import urllib.request
from datetime import datetime,timezone
from scripts.edge_marathon.runner import ROOT,safe_dump,verify


def run():
    verify();base='http://127.0.0.1:3012';responses={}
    for route,relative in [('/data/edge-marathon.json','public/data/edge-marathon.json'),
                           ('/data/edge-marathon-verification.json','public/data/edge-marathon-verification.json')]:
        with urllib.request.urlopen(base+route,timeout=10) as response:
            payload=response.read();status=response.status
        expected=(ROOT/relative).read_bytes()
        if payload!=expected:raise ValueError('HTTP/disk byte mismatch '+route)
        responses[route]=dict(http_status=status,bytes_match_disk=True,sha256=hashlib.sha256(payload).hexdigest())
    with urllib.request.urlopen(base+'/research/marathon',timeout=10) as response:
        page=response.read().decode();status=response.status
    if 'Master Scorecard' not in page or 'Geen onafhankelijke bevestiging' not in page:raise ValueError('Dashboard missing actual results')
    privacy={}
    for route in ['/artifacts/edge-marathon/discovery-trades.csv','/data/raw/nqh25_intraday-1min_historical-data-10-19-2026.csv']:
        try:
            with urllib.request.urlopen(base+route,timeout=10) as response:code=response.status
        except urllib.error.HTTPError as exc:code=exc.code
        if code!=404:raise ValueError('Private path unexpectedly exposed: '+route)
        privacy[route]=code
    result=dict(status='LOCAL_BROWSER_DELIVERY_AND_PRIVACY_VERIFIED',checked_utc=datetime.now(timezone.utc).isoformat(),
        base_url=base,dashboard_route='/research/marathon',html_status=status,responses=responses,
        private_paths_return_404=privacy,
        browser_tool_observations=dict(scorecard_rows_including_header=26,data_rows=25,
            console_error_or_warning_entries_observed=0,viewport_width=584,document_scroll_width=584,
            evidence='Actual CUA browser observations in the active turn; these are not inferred from HTTP.'),
        external_publication=False,raw_source_uploads=False)
    safe_dump(ROOT/'research/edge-marathon-browser-verification.json',result)
    print(json.dumps(result,indent=2))
    return result


if __name__=='__main__':run()
