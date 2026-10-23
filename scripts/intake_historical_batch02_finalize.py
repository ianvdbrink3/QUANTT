"""Metadata-only receipt with explicit duplicate-download alias accounting."""
import csv
import io
import json
from collections import Counter
from scripts.intake_historical_first_six import ROOT,DOWNLOADS,RAW,inspect,stage,sha,snapshot


def run():
    before=snapshot();plan=ROOT/'research/afternoon-historical-download-plan.json'
    rows=json.loads(plan.read_text())['rows'];records=[];unmatched=[]
    contracts={r['contract'] for r in rows}
    for path in sorted(DOWNLOADS.glob('nq*_intraday-1min_historical-data-10-22-2026*.csv')):
        contract=path.name.split('_')[0].upper()
        if contract not in contracts:continue
        labels=[r['Time'][:10] for r in csv.DictReader(io.StringIO(path.read_text(encoding='utf-8-sig'))) if r.get('Time','')[:4].isdigit()]
        if not labels:
            unmatched.append(dict(filename=path.name,sha256=sha(path),reason='No valid timestamp labels'));continue
        first,last=min(labels),max(labels)
        matches=[r for r in rows if r['contract']==contract and r['start_iso']<=first<=last<=r['end_iso']]
        if len(matches)!=1:raise ValueError('Ambiguous or out-of-plan file: '+path.name)
        request=matches[0]
        if request['sequence']<=6:continue
        record,_=inspect(path,request);target=RAW/path.name;stage(path,target)
        record.update(private_copy=str(target.relative_to(ROOT)),private_copy_gitignored=True,private_copy_byte_identical=sha(target)==record['sha256'])
        records.append(record)
    counts=Counter(r['sequence'] for r in records)
    unique=set(counts);missing=[r for r in rows[6:] if r['sequence'] not in unique]
    result=dict(status='METADATA_RECEIPT_ONLY_NO_NEW_OUTCOMES',as_of='2026-10-22',plan_sha256=sha(plan),
        prior_received=6,new_unique_blocks=len(unique),new_physical_files=len(records),duplicate_download_aliases=len(records)-len(unique),
        total_plan_blocks_received=6+len(unique),pending_plan_blocks=len(missing),
        metadata_flagged_files=sum(bool(r['metadata_issue_counts']) for r in records),
        source_bars_including_duplicate_downloads=sum(r['parsed_bars'] for r in records),
        numeric_OHLCV_read=False,signals_computed=False,new_holdout_run=False,
        observed_daily_limit=250,limit_reached=False,quota_after_batch_verified=False,
        purchases=False,accounts_created=False,subscription_changed=False,external_publication=False,
        duplicate_counts={str(k):v for k,v in counts.items() if v>1},unmatched_empty_files=unmatched,
        quality='Hashes, headers, rowcounts, source Chicago timestamp bounds/order/duplicates/footer/cap only. Not full numerical quality, CME calendar, volume rolls, eligibility or license certification.',
        files=sorted(records,key=lambda r:(r['sequence'],r['filename'])),remaining=missing)
    if before!=snapshot():raise ValueError('Tracked files changed')
    dump_path=ROOT/'research/afternoon-historical-intake-batch02-final.json'
    dump_path.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('files','remaining')}))
    return result


if __name__=='__main__':run()
