"""Append-only plan receipt. Never parse new historical OHLCV numerically."""
import csv
import io
import json
from datetime import datetime
from scripts.intake_historical_first_six import ROOT, DOWNLOADS, RAW, inspect, stage, sha, snapshot


def run():
    before = snapshot()
    plan = ROOT/'research/afternoon-historical-download-plan.json'
    rows = json.loads(plan.read_text())['rows'][6:]
    records = []; unmatched = []
    for path in sorted(DOWNLOADS.glob('nq*_intraday-1min_historical-data-10-22-2026*.csv')):
        contract = path.name.split('_')[0].upper()
        # Read only Time strings to match the actual requested block, never suffix guesses.
        reader = csv.DictReader(io.StringIO(path.read_text(encoding='utf-8-sig')))
        labels = [r['Time'][:10] for r in reader if r.get('Time','')[:4].isdigit()]
        if not labels:
            continue
        first, last = min(labels), max(labels)
        candidates = [r for r in rows if r['contract']==contract and r['start_iso']<=first<=last<=r['end_iso']]
        if not candidates:
            if first >= '2019-01-14': unmatched.append(path.name)
            continue
        if len(candidates)!=1: raise ValueError('Ambiguous plan match')
        record, _ = inspect(path, candidates[0])
        target = RAW/path.name; stage(path, target)
        record.update(private_copy=str(target.relative_to(ROOT)), private_copy_gitignored=True,
                      private_copy_byte_identical=sha(target)==record['sha256'])
        records.append(record)
    unique = {r['sequence'] for r in records}
    if len(unique)!=len(records): raise ValueError('Duplicate downloaded plan block; inspect, do not silently count twice')
    result = dict(status='METADATA_ONLY_INTAKE_NOT_QUALITY_OR_OUTCOME_VALIDATION', as_of='2026-10-22',
                  plan_sha256=sha(plan), prior_batch_files=6, new_files=len(records),
                  total_received=6+len(unique), remaining=103-6-len(unique),
                  source_bars=sum(r['parsed_bars'] for r in records),
                  metadata_flagged_files=sum(bool(r['metadata_issue_counts']) for r in records),
                  unmatched_downloads=unmatched, numeric_ohlcv_parsed=False, strategy_outcomes_computed=False,
                  purchases=False, subscription_changes=False, new_accounts=False,
                  access='Existing Barchart trial/session, not a guarantee of permanent free access.',
                  quality_limit='Only timestamps, structure, bounds, footer, cap and hashes. No full RTH, holidays, numeric prices, volume, rollover or licensing certification.',
                  files=sorted(records,key=lambda r:r['sequence']))
    output=ROOT/'research/afternoon-historical-intake-batch02.json'
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    if before!=snapshot(): raise ValueError('Tracked bytes changed')
    print(json.dumps({k:v for k,v in result.items() if k!='files'}))
    return result


if __name__=='__main__': run()
