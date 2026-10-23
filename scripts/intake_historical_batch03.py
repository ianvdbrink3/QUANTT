"""Receipt-only continuation; preserve batch01/02 and all research outcomes."""
import csv
import io
import json
from collections import Counter
from scripts.intake_historical_first_six import ROOT,DOWNLOADS,RAW,inspect,stage,sha,snapshot

START=ROOT/'research/afternoon-historical-intake-batch03-start.json'
RESULT=ROOT/'research/afternoon-historical-intake-batch03.json'


def run():
    before=snapshot()
    old_paths=[ROOT/'research/afternoon-historical-intake-batch01.json',ROOT/'research/afternoon-historical-intake-batch02-final.json']
    plan_path=ROOT/'research/afternoon-historical-download-plan.json'
    plan=json.loads(plan_path.read_text())['rows']
    if not START.exists():
        old=[r for p in old_paths for r in json.loads(p.read_text())['files']]
        known={r['filename']:r['sha256'] for r in old}
        completed={r['sequence'] for r in old}
        start=dict(date='2026-10-22',prior_blocks=len(completed),completed_sequences=sorted(completed),
                   prior_register_sha256={str(p.relative_to(ROOT)):sha(p) for p in old_paths},
                   prior_files=known,plan_sha256=sha(plan_path))
        START.write_text(json.dumps(start,indent=2)+'\n')
    start=json.loads(START.read_text())
    for p,expected in start['prior_register_sha256'].items():
        if sha(ROOT/p)!=expected:raise ValueError('Prior receipt changed: '+p)
    if sha(plan_path)!=start['plan_sha256']:raise ValueError('Fixed request plan changed')
    records=[];empty=[];contracts={r['contract'] for r in plan}
    received_paths=set()
    for export_date in ('10-22-2026','10-23-2026'):
        received_paths.update(DOWNLOADS.glob('nq*_intraday-1min_historical-data-'+export_date+'*.csv'))
    for path in sorted(received_paths):
        contract=path.name.split('_')[0].upper()
        if contract not in contracts:continue
        if path.name in start['prior_files']:
            if sha(path)!=start['prior_files'][path.name]:raise ValueError('Prior raw source changed')
            continue
        labels=[r['Time'][:10] for r in csv.DictReader(io.StringIO(path.read_text(encoding='utf-8-sig'))) if r.get('Time','')[:4].isdigit()]
        if not labels:
            empty.append(dict(filename=path.name,sha256=sha(path)));continue
        a,b=min(labels),max(labels)
        matches=[r for r in plan if r['contract']==contract and r['start_iso']<=a<=b<=r['end_iso']]
        if len(matches)!=1:raise ValueError('Out-of-plan or ambiguous source '+path.name)
        record,_=inspect(path,matches[0]);target=RAW/path.name;stage(path,target)
        record.update(private_copy=str(target.relative_to(ROOT)),private_copy_gitignored=True,
                      private_copy_byte_identical=sha(target)==record['sha256'])
        records.append(record)
    completed=set(start['completed_sequences']);new={r['sequence'] for r in records}-completed
    all_done=completed|new;missing=[r for r in plan if r['sequence'] not in all_done]
    result=dict(status='INTAKE_ONLY_NO_NEW_OUTCOMES',date='2026-10-23',start_sha256=sha(START),
        prior_blocks=start['prior_blocks'],new_unique_blocks=len(new),physical_new_files=len(records),
        total_plan_blocks_received=len(all_done),pending_plan_blocks=len(missing),
        metadata_flagged_files=sum(bool(r['metadata_issue_counts']) for r in records),empty_files=empty,
        numeric_OHLCV_read=False,signals_computed=False,new_holdout_run=False,
        purchases=False,new_accounts=False,subscription_changes=False,publication=False,
        files=records,remaining=missing)
    RESULT.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    if before!=snapshot():raise ValueError('Tracked files changed')
    print(json.dumps({k:v for k,v in result.items() if k not in ('files','remaining')}))
    return result


if __name__=='__main__':run()
