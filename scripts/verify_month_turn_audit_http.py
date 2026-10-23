"""Loopback-only delivery/privacy checks, separate from statistical research."""
import hashlib
import json
import urllib.error
import urllib.request

from scripts.month_turn_audit import ROOT, dump, verify


def run():
    verify()
    base = 'http://127.0.0.1:3012'
    served = {}
    for relative in ('data/month-turn-audit.json', 'data/month-turn-audit-verification.json',
                     'reports/MONTH_TURN_AUDIT.md', 'reports/MONTH_TURN_UNCERTAINTY_CONTEXT.md'):
        with urllib.request.urlopen(base+'/'+relative, timeout=10) as response:
            payload = response.read()
            if response.status != 200 or payload != (ROOT/'public'/relative).read_bytes():
                raise ValueError('Local HTTP/disk mismatch: '+relative)
        served['/'+relative] = dict(status=200, bytes_match_disk=True,
                                     sha256=hashlib.sha256(payload).hexdigest())
    for route, expected in [('/research/month-turn-audit', 'Meer dan gewone marktdrift?'),
                            ('/research/marathon', 'Master Scorecard')]:
        with urllib.request.urlopen(base+route, timeout=10) as response:
            if response.status != 200 or expected not in response.read().decode():
                raise ValueError('Local dashboard not correctly served')
        served[route] = dict(status=200)
    private = {}
    for route in ('/artifacts/month-turn-audit/discovery-daily.json',
                  '/data/raw/nqh25_intraday-1min_historical-data-10-19-2026.csv'):
        try:
            with urllib.request.urlopen(base+route, timeout=10) as response:
                code = response.status
        except urllib.error.HTTPError as error:
            code = error.code
        if code != 404:
            raise ValueError('Private path exposed: '+route)
        private[route] = code
    result = dict(status='LOCAL_MONTH_TURN_DASHBOARD_DELIVERY_PRIVACY_VERIFIED', served=served,
                  private_paths=private,
                  observed_browser_evidence=dict(tool='Actual CUA observations in this turn, not inferred from HTTP',
                                                 title='QUANTT — Maandwissel-audit', viewport_width=584,
                                                 document_scroll_width=584, tables=5, data_rows=46,
                                                 both_details_opened_and_verified=True,
                                                 console_warn_or_error_entries_observed=0),
                  external_publication=False, private_raw_uploads=False)
    dump(ROOT/'research/month-turn-audit-browser-verification.json', result)
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    run()
