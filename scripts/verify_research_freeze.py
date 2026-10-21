"""Offline byte-integrity gate; no source CSVs, signals or backtest required."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify(root=ROOT):
    manifest = json.loads((root/'research/vnext-freeze-manifest.json').read_text())
    failures = []
    for name, digest in manifest['files_sha256'].items():
        path = root/name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            failures.append(name)
    if failures:
        raise ValueError('Frozen research changed: ' + ', '.join(failures))
    return {'status': 'FROZEN_BYTES_VERIFIED', 'freeze_id': manifest['freeze_id'],
            'files': len(manifest['files_sha256']), 'historical_tests': manifest['historical_tests'],
            'eligible_days': manifest['eligible_days'], 'backtest_run': False}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
