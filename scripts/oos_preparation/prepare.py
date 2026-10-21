"""Prepare sources, quality and planning only. No evaluate/backtest command exists."""
import argparse
import json
from pathlib import Path

from .adapter import Calendar, FIELDS, audit_contract, combine, load_csv, sha, stage_immutable
from .power import plan

ROOT = Path(__file__).resolve().parents[2]


def prepare(downloads, stage=False):
    calendar_path = ROOT/'research/oos-calendar-register.json'
    calendar = Calendar(json.loads(calendar_path.read_text()))
    prior_path = ROOT.parent/'reports/nqz25-quarter/quality_report.json'
    prior = json.loads(prior_path.read_text())
    items, parts = [], []
    for i in range(2,8):
        name = f'nqz25_intraday-1min_historical-data-10-19-2026-{i}.csv'
        source = downloads/name
        previous = next(x['sha256'] for x in prior['sources'] if Path(x['path']).name == name)
        if sha(source) != previous:
            raise ValueError('Source changed since prior quality inspection: '+name)
        bars = load_csv(source, 'NQZ25')
        target = ROOT/'data/raw/oos'/name
        if stage:
            stage_immutable(source, target)
        items.append({'filename':name, 'relative_private_path':'data/raw/oos/'+name,
                      'contract':'NQZ25', 'sha256':previous, 'rows':len(bars),
                      'first_utc':bars.index.min().isoformat(), 'last_utc':bars.index.max().isoformat(),
                      'staged_and_verified':target.exists() and sha(target)==previous,
                      'prior_access':'2026-10-19 quality/consolidation; 2026-10-21 inventory and quality audit; no strategy use found, not proven never-used'})
        parts.append(bars)
    bars = combine(parts,'2025-10-01','2025-12-12')
    quality = audit_contract(bars,calendar,'2025-10-01','2025-12-12')
    power = plan(ROOT)
    # Every blocker is explicit. This preparation NEVER converts itself to permission to score.
    blockers = ['Missing NQH26/NQM26/NQU26/NQZ26 and joint pre-roll overlaps',
                'December crossover not established from incoming volume',
                'NQ-specific calendar beyond 2025-12-12 not verified',
                'Vendor usage rights/publication vintages not independently confirmed',
                'Prior strategy non-use cannot be certified from incomplete local execution logs',
                'No authenticated automated Barchart download session available; public page has verification challenge']
    manifest = {'phase':'QUALITY_ONLY_NOT_SCORING_AUTHORIZATION', 'source_timezone':'America/Chicago',
                'session_convention':'Civil NY 18:00-17:00, not CME clearing TradeDate',
                'sources':items, 'calendar_sha256':sha(calendar_path),
                'prior_quality_report_sha256':sha(prior_path),
                'frozen_protocol_sha256':sha(ROOT/'research/vnext-future-oos-protocol.json'),
                'license_status':'PENDING_VERIFICATION_NO_RAW_PUBLICATION'}
    result = {'classification':'PREPARATION_ONLY_HOLDOUT_UNSCORED', 'status':'DATA_INSUFFICIENT',
              'target_period':['2025-10-01','2026-09-30'], 'blockers':blockers,
              'source_manifest':manifest, 'source_bars_in_overlap_blocks':sum(x['rows'] for x in items),
              'unique_bars_oct_dec':len(bars), 'session_dates':len(quality),
              'standard_clean_days':sum(x['standard_clean'] for x in quality),
              'complete_noon_prefix_days':sum(x['noon_prefix_complete'] for x in quality),
              'active_contract_eligible_days':None,
              'eligibility_note':'52 prefix-suitable days conditional on frozen historical warmup; not scored, not certified active through December without H26 volume comparison. Thanksgiving included by unchanged all-view.',
              'unresolved_missing_minutes':sum(x['unresolved_missing'] for x in quality),
              'missing_full_dates':[x['day'] for x in quality if not x['bars']],
              'exceptions':[x for x in quality if not x['standard_clean']],
              'prior_access_evidence':'Existing 2026-10-19 quality report and source hashes match; historical runners capped at Sep30. No October-December strategy ledger found in inspected local outputs. Absence is not proof of non-execution.',
              'scoring_run':False, 'signals_computed':False, 'power_planning':power}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--downloads',type=Path,default=Path('/Users/ianvandenbrink/Downloads'))
    parser.add_argument('--stage-existing',action='store_true')
    parser.add_argument('--output',type=Path,default=ROOT/'artifacts/oos-preparation')
    args = parser.parse_args()
    result = prepare(args.downloads,args.stage_existing)
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    (args.output/'source-manifest.json').write_text(json.dumps(result['source_manifest'],indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','unique_bars_oct_dec','session_dates','standard_clean_days','complete_noon_prefix_days','unresolved_missing_minutes','scoring_run','signals_computed']},indent=2))


if __name__ == '__main__':
    main()
