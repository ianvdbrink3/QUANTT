#!/usr/bin/env python3
"""Resumable daily M1 ingest with bounded concurrent downloads and audit trail."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import lzma
import subprocess
import tempfile
from pathlib import Path
import random
import sys
import time
import requests
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from quantlab.data import decode_bi5, clean_bars

ROOT = Path(__file__).resolve().parents[1]

class SourceRateLimit(RuntimeError):
    pass


def http_get(url, timeout, transport):
    if transport == 'requests':
        response = requests.get(url, timeout=(15, timeout))
        return response.status_code, response.content, dict(response.headers)
    with tempfile.TemporaryDirectory(prefix='quantt-download-') as tmp:
        payload = Path(tmp)/'payload'
        headers = Path(tmp)/'headers'
        result = subprocess.run(['curl', '--silent', '--show-error', '--location',
            '--proto', '=https', '--proto-redir', '=https', '--connect-timeout', '15',
            '--max-time', str(timeout), '--dump-header', str(headers),
            '--output', str(payload), '--write-out', '%{http_code}', url],
            capture_output=True, timeout=timeout+5)
        if result.returncode:
            raise OSError(f'curl transport error {result.returncode}: {result.stderr.decode().strip()}')
        hdr = headers.read_text().lower()
        return int(result.stdout), payload.read_bytes(), {'challenge': 'x-amzn-waf-action: challenge' in hdr}


def fetch_day(day, symbol, cfg, attempts=5, timeout=45, force=False, transport='curl'):
    daystr = day.isoformat()
    relative = f'{symbol}/{day.year}/{day.month-1:02d}/{day.day:02d}/BID_candles_min_1.bi5'
    url = f"{cfg['data_url']}/{relative}"
    raw = ROOT / 'data/raw' / relative
    parquet = ROOT / f'data/curated/partitions/{symbol}/{daystr}.parquet'
    meta = {'date': daystr, 'symbol': symbol, 'url': url,
            'retrieved_at': datetime.now(timezone.utc).isoformat(), 'attempts': 0}
    for attempt in range(attempts):
        meta['attempts'] = attempt + 1
        try:
            cached = raw.exists() and not force
            if cached:
                payload = raw.read_bytes()
            else:
                status, payload, headers = http_get(url, timeout, transport)
                meta['http_status'] = status
                if status == 429 or headers.get('challenge'):
                    meta.update(status='source_blocked', error='Source rate limit or browser challenge; bulk circuit breaker opened')
                    return meta
                if status in (404, 204):
                    # Missing is not silently promoted to a closed trading day.
                    meta.update(status='unavailable', bytes=0)
                    return meta
                if status != 200:
                    raise OSError(f'HTTP {status}')
            frame = decode_bi5(payload, daystr, cfg['price_divisor'])
            frame, quality = clean_bars(frame, cfg['plausible_price_min'], cfg['plausible_price_max'])
            if len(frame) and quality['price_anomalies'] == len(frame):
                raise ValueError('Every candle fails price validation; check divisor/source')
            if not cached:
                raw.parent.mkdir(parents=True, exist_ok=True)
                temp = raw.with_suffix('.part')
                temp.write_bytes(payload)
                temp.replace(raw)
            parquet.parent.mkdir(parents=True, exist_ok=True)
            temp = parquet.with_suffix('.part')
            frame.to_parquet(temp, compression='zstd')
            temp.replace(parquet)
            meta.update(quality, status='ok' if len(frame) else 'empty', bytes=len(payload),
                        sha256=hashlib.sha256(payload).hexdigest(), cache_hit=cached)
            return meta
        except (requests.RequestException, ValueError, EOFError, OSError, lzma.LZMAError, subprocess.TimeoutExpired) as exc:
            # Corrupt cached bytes are discarded; next attempt re-downloads.
            if raw.exists():
                raw.unlink()
            meta['error'] = f'{type(exc).__name__}: {exc}'
            if attempt + 1 < attempts:
                time.sleep(min(30, 2**attempt) + random.random())
    meta['status'] = 'failed'
    return meta

def run(start, end, symbol='USATECHIDXUSD', workers=4, attempts=5, timeout=45, force=False, transport='curl'):
    cfg = yaml.safe_load((ROOT / 'configs/instruments.yaml').read_text())[symbol]
    days = [start + timedelta(days=i) for i in range((end-start).days)]
    manifest = ROOT / 'data/download_manifest.jsonl'
    manifest.parent.mkdir(parents=True, exist_ok=True)
    errors = []
    # Submit only one bounded batch at a time; stop new requests on a source block.
    completed = 0
    failed_batches = 0
    with ThreadPoolExecutor(max_workers=workers) as pool, manifest.open('a') as handle:
        for offset in range(0, len(days), workers):
            jobs = [pool.submit(fetch_day, d, symbol, cfg, attempts, timeout, force, transport)
                    for d in days[offset:offset+workers]]
            blocked = False
            batch_failed = True
            for future in as_completed(jobs):
                result = future.result()
                completed += 1
                handle.write(json.dumps(result) + '\n')
                handle.flush()
                if result['status'] in ('failed', 'source_blocked'):
                    errors.append(result['date'])
                blocked |= result['status'] == 'source_blocked'
                batch_failed &= result['status'] == 'failed'
                print(f"{completed}/{len(days)} {result['date']} {result['status']} bars={result.get('validated_bars', 0)}", flush=True)
            failed_batches = failed_batches + 1 if batch_failed else 0
            if blocked or failed_batches >= 2:
                print('Source blocked: stopped bulk requests; cached partitions retained. Resume later.', flush=True)
                break
    return errors

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--start', type=date.fromisoformat, required=True)
    p.add_argument('--end', type=date.fromisoformat, default=datetime.now(timezone.utc).date(), help='Exclusive UTC day; current partial day excluded')
    p.add_argument('--symbol', default='USATECHIDXUSD')
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--attempts', type=int, default=5)
    p.add_argument('--timeout', type=int, default=45)
    p.add_argument('--force', action='store_true')
    p.add_argument('--transport', choices=['curl','requests'], default='curl')
    a = p.parse_args()
    if a.start >= a.end or not 1 <= a.workers <= 16 or a.attempts < 1 or a.timeout <= 0:
        p.error('Require start < end, workers 1..16, attempts >=1, timeout >0')
    sys.exit(bool(run(a.start, a.end, a.symbol, a.workers, a.attempts, a.timeout, a.force, a.transport)))
