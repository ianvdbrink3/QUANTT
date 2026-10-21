"""December source/volume audit. Deliberately no feature or strategy imports."""
import argparse
import json
from pathlib import Path

import pandas as pd

from .adapter import Calendar, audit_contract, combine, determine_roll, load_csv, sha, stage_immutable

ROOT = Path(__file__).resolve().parents[2]
SOURCES = [
    ('NQZ25', 'nqz25_intraday-1min_historical-data-10-21-2026.csv', '17d6d03e8034074fcec3d60a1700c47efafd54680a13fc0f6d83d15c8e62d6e2'),
    ('NQH26', 'nqh26_intraday-1min_historical-data-10-21-2026-2.csv', '68f4548eaf12d3de98a2bff1651f093c715cb8c0f0669989dc00f393483a02fe'),
    ('NQH26', 'nqh26_intraday-1min_historical-data-10-21-2026-3.csv', '59763de75f4c288671297260d8606c54485b7441a663a9f48832e3c311b82642'),
    ('NQH26', 'nqh26_intraday-1min_historical-data-10-21-2026-4.csv', '5a098d8a55810b8f181fbe754903fd596c54608ff6ef4e82922ddbd4c904db86'),
]


def registered_source(root, downloads, name, digest, stage=False):
    target = root/'data/raw/oos'/name
    if stage:
        original = downloads/name
        if sha(original) != digest:
            raise ValueError('December original hash mismatch: '+name)
        stage_immutable(original, target)
    if sha(target) != digest:
        raise ValueError('December staged source hash mismatch: '+name)
    return target


def volume_evidence(frame, calendar):
    rows = []
    for day in pd.bdate_range('2025-12-01', '2025-12-19').strftime('%Y-%m-%d'):
        expected = calendar.grid(day)
        row = {'day': day}
        for contract in ['NQZ25', 'NQH26']:
            b = frame[frame.contract.eq(contract) & frame.trade_date.eq(day)]
            row[contract] = {'bars': len(b), 'volume': int(b.volume.sum()),
                             'missing': len(expected.difference(b.index))}
        rows.append(row)
    return rows


def run(downloads, stage=False):
    protocol = ROOT/'research/december-overlap-protocol.json'
    calendar = Calendar(json.loads(protocol.read_text())['calendar'])
    old_manifest = json.loads((ROOT/'research/oos-source-register.json').read_text())
    # Existing manifests are retained, not rewritten to make previous access disappear.
    old_sources = old_manifest['sources']
    parts, manifest = [], []
    for item in old_sources:
        p = ROOT/item['relative_private_path']
        if sha(p) != item['sha256']:
            raise ValueError('Previously registered source changed')
        parts.append(load_csv(p, 'NQZ25'))
    for contract, name, digest in SOURCES:
        source = registered_source(ROOT, downloads, name, digest, stage)
        b = load_csv(source, contract)
        if len(b) >= 19999:
            raise ValueError('Possible vendor download cap')
        manifest.append({'filename': name, 'contract': contract, 'sha256': digest,
                         'rows': len(b), 'first_utc': b.index.min().isoformat(),
                         'last_utc': b.index.max().isoformat(),
                         'relative_private_path': 'data/raw/oos/'+name})
        parts.append(b)
    full = combine(parts, '2025-12-01', '2025-12-19')
    roll = determine_roll(full, 'NQZ25', 'NQH26', calendar, '2025-12-18')
    daily = volume_evidence(full, calendar)
    preceding = []
    for r in daily:
        b = full[full.contract.eq('NQH26') & full.trade_date.eq(r['day'])]
        expected = calendar.grid(r['day'])
        qualified = (len(b) > 0 and b.index.min() <= expected.min()+pd.Timedelta(minutes=60)
                     and b.index.max() >= expected.max()-pd.Timedelta(minutes=60))
        if (r['day'] < roll['decision_session'] and r['NQZ25']['volume'] > r['NQH26']['volume']
                and r['NQZ25']['missing'] == 0 and qualified):
            preceding.append(r['day'])
    if not preceding:
        raise ValueError('No preceding outgoing-dominant complete session')
    active = full[((full.trade_date < roll['effective_session']) & full.contract.eq('NQZ25')) |
                  ((full.trade_date >= roll['effective_session']) & full.contract.eq('NQH26'))].sort_index()
    # Audit active contract separately; never infer a strategy-eligible day count.
    quality = []
    for contract, a, b in [('NQZ25', '2025-12-01', (pd.Timestamp(roll['effective_session'])-pd.Timedelta(days=1)).strftime('%Y-%m-%d')),
                           ('NQH26', roll['effective_session'], '2025-12-19')]:
        quality += [dict(r, contract=contract) for r in audit_contract(full[full.contract.eq(contract)], calendar, a, b)]
    result = {'classification': 'QUALITY_AND_VOLUME_ONLY_HOLDOUT_UNSCORED',
              'status': 'DECEMBER_OVERLAP_VERIFIED_NOT_FULL_YEAR_READY',
              'protocol_sha256': sha(protocol), 'sources': manifest,
              'source_rows_new': sum(m['rows'] for m in manifest),
              'overlap_duplicate_rows': sum(len(p[p.trade_date.between('2025-12-01','2025-12-19')]) for p in parts)-len(full),
              'conflicting_overlaps': 0, 'preceding_qualified_outgoing_dominant_days': preceding,
              'roll': roll, 'daily_volume': daily,
              'active_unique_bars': len(active), 'active_sessions': len(quality),
              'active_standard_clean_days': sum(r['standard_clean'] for r in quality),
              'active_noon_prefix_complete_days': sum(r['noon_prefix_complete'] for r in quality),
              'active_missing_minutes': sum(r['unresolved_missing'] for r in quality),
              'quality': quality, 'signals_computed': False, 'scoring_run': False,
              'eligible_days': None, 'note': 'No strategy eligibility evaluation. Ordinary-session calendar reconstructed; no raw bars publicly exported.'}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--downloads', type=Path, default=Path('/Users/ianvandenbrink/Downloads'))
    parser.add_argument('--stage', action='store_true')
    parser.add_argument('--publish', action='store_true', help='Aggregate quality/provenance only')
    args = parser.parse_args()
    result = run(args.downloads, args.stage)
    out = ROOT/'artifacts/december-overlap'
    out.mkdir(parents=True, exist_ok=True)
    (out/'audit.json').write_text(json.dumps(result, indent=2)+'\n')
    if args.publish:
        # Exclude daily volumes, prices/spread and individual market bars from public export.
        public = {k: v for k, v in result.items() if k not in ['daily_volume', 'quality', 'roll']}
        public['roll'] = {k: result['roll'][k] for k in ['from', 'to', 'decision_session', 'effective_session', 'effective_utc', 'close_bar_utc', 'spread_available_utc']}
        (ROOT/'public/data/research-december-overlap.json').write_text(json.dumps(public, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['daily_volume', 'quality', 'sources']}, indent=2))


if __name__ == '__main__':
    main()
