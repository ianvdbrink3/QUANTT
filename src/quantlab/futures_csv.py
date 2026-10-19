"""Strict contract-native CSV ingestion gate for CME NQ/ES (never CFD conversion).

Required fields: timestamp_utc,contract_id,open,high,low,close,volume.
A timestamp denotes the one-minute bar OPEN, with explicit UTC timezone.
This module only validates: it does not declare the source licensed or CME-authoritative.
"""
from __future__ import annotations
import csv
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

REQUIRED = ('timestamp_utc', 'contract_id', 'open', 'high', 'low', 'close', 'volume')
PRICES = ('open', 'high', 'low', 'close')

def validate_contract_csv(path: str | Path, instrument: str = 'NQ') -> dict:
    """Validate order, tick, source contract and OHLC; flag raw gaps without filling."""
    if instrument not in ('NQ', 'ES', 'MNQ', 'MES'):
        raise ValueError('Unsupported CME instrument')
    tick = Decimal('0.25')
    previous: dict[str, datetime] = {}
    count: dict[str, int] = {}
    gaps: list[dict] = []
    with Path(path).open(newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not set(REQUIRED).issubset(reader.fieldnames):
            raise ValueError(f'Missing columns: {sorted(set(REQUIRED)-set(reader.fieldnames or []))}')
        for line_no, row in enumerate(reader, 2):
            try:
                stamp = datetime.fromisoformat(row['timestamp_utc'].replace('Z', '+00:00'))
                if stamp.tzinfo is None or stamp.utcoffset() != timedelta(0):
                    raise ValueError('Timestamp must have an explicit UTC offset')
                stamp = stamp.astimezone(timezone.utc)
                if stamp.second or stamp.microsecond:
                    raise ValueError('Timestamp must be minute-aligned')
                contract = row['contract_id'].strip().upper()
                if not contract.startswith(instrument) or len(contract) < len(instrument)+2:
                    raise ValueError('Wrong or missing contract ID')
                values = {field: Decimal(row[field]) for field in PRICES+('volume',)}
                if not all(v.is_finite() for v in values.values()):
                    raise ValueError('Non-finite data')
                if any(values[k] <= 0 or values[k] % tick for k in PRICES):
                    raise ValueError('Invalid price or tick alignment')
                if values['volume'] < 0 or values['volume'] != values['volume'].to_integral_value():
                    raise ValueError('Invalid exchange volume')
                if values['high'] < max(values['open'],values['close'],values['low']):
                    raise ValueError('High violates OHLC ordering')
                if values['low'] > min(values['open'],values['close'],values['high']):
                    raise ValueError('Low violates OHLC ordering')
                old = previous.get(contract)
                if old is not None:
                    if stamp <= old:
                        raise ValueError('Duplicate or out-of-order bar within contract')
                    if stamp - old > timedelta(minutes=1):
                        gaps.append({'contract_id':contract, 'previous_utc':old.isoformat(),
                                     'next_utc':stamp.isoformat(),
                                     'missing_minutes':int((stamp-old).total_seconds()/60)-1})
                previous[contract] = stamp
                count[contract] = count.get(contract,0)+1
            except (TypeError, KeyError, InvalidOperation, ValueError) as exc:
                raise ValueError(f'Invalid CSV line {line_no}: {exc}') from exc
    if not count:
        raise ValueError('No bars supplied')
    return {'instrument':instrument,'source_type':'contract_native_futures_csv',
            'bar_timestamp_convention':'bar_open_utc','rows':sum(count.values()),
            'contracts':count,'observed_gaps':gaps,'gaps_are_not_calendar_adjusted':True,
            'futures_source_authenticated':False,
            'note':'Structural checks only; independently verify CME contract provenance, trading calendar and license.'}
