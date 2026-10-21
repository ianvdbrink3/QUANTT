"""Read-only NQ CSV timestamp inventory. Never reads OHLCV or calls an engine.

Outputs metadata only to stdout. Filenames' download dates are NOT data dates.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import pandas as pd


def inspect(path):
    columns = list(pd.read_csv(path, nrows=0).columns)
    key = next((c for c in columns if c.lower() in
                ('time', 'datetime', 'timestamp', 'timestamp et', 'date', 'timestamp_utc')), None)
    if key is None:
        return {'filename': path.name, 'status': 'NO_RECOGNIZED_TIMESTAMP_COLUMN'}
    values = pd.read_csv(path, usecols=[key])[key]
    fmt = '%m/%d/%Y %H:%M' if key.lower() == 'timestamp et' else 'mixed'
    dates = pd.to_datetime(values, format=fmt, errors='coerce')
    valid = dates.dropna()
    contract = re.match(r'(nq[hmuz]\d{2})_', path.name, re.I)
    after = valid[valid >= pd.Timestamp('2025-10-01', tz=valid.dt.tz)]
    sessions = ((valid + pd.Timedelta(hours=7)).dt.normalize() if key == 'Time'
                else (valid + pd.Timedelta(hours=6)).dt.normalize()
                if key.lower() == 'timestamp et' else None)
    return {'filename': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'status': 'TIMESTAMPS_ONLY_NOT_QUALITY_VALIDATED', 'timestamp_column': key,
            'contract_from_filename_only': contract.group(1).upper() if contract else None,
            'timezone': 'America/Chicago (existing Barchart importer convention)' if key == 'Time'
                        else 'America/New_York (column label only)' if key.lower() == 'timestamp et'
                        else 'UNVERIFIED',
            'rows_with_timestamp': len(valid), 'non_timestamp_rows': int(dates.isna().sum()),
            'first_source_timestamp': valid.min().isoformat() if len(valid) else None,
            'last_source_timestamp': valid.max().isoformat() if len(valid) else None,
            'post_sep_rows': len(after),
            'post_sep_civil_session_rows': int(sessions.ge(pd.Timestamp('2025-10-01')).sum()) if sessions is not None else None,
            'last_civil_session_date': sessions.max().date().isoformat() if sessions is not None and len(sessions) else None,
            'post_sep_dates': sorted(after.dt.strftime('%Y-%m-%d').unique().tolist()),
            'ohlcv_read': False, 'backtest_run': False}


def run(roots):
    paths = set()
    errors = []
    for root in roots:
        if not root.exists():
            errors.append({'root': str(root), 'status': 'MISSING'})
            continue
        for path in root.rglob('*'):
            if path.is_file() and path.suffix.lower() == '.csv' and 'nq' in path.name.lower():
                paths.add(path.resolve())
    records = []
    for path in sorted(paths):
        try:
            records.append({'path': str(path), **inspect(path)})
        except (ValueError, OSError, pd.errors.ParserError) as exc:
            errors.append({'path': str(path), 'error': str(exc)})
    return {'scope': [str(p) for p in roots], 'mode': 'TIMESTAMPS_ONLY_NO_SIGNALS',
            'files_scanned': len(paths), 'records': records, 'errors': errors}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('roots', type=Path, nargs='+')
    print(json.dumps(run(parser.parse_args().roots), indent=2))
