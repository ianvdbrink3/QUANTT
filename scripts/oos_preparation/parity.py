"""Local raw-data parity only: no historical or future strategy evaluation."""
import json
from pathlib import Path

import pandas as pd

from .adapter import Calendar, FIELDS, combine, determine_roll, load_csv, sha
from scripts.reproduce_research import barchart

ROOT = Path(__file__).resolve().parents[2]


def verify():
    protocol = json.loads((ROOT/'research/holdout-protocol.json').read_text())
    calendar = Calendar(json.loads((ROOT/'research/oos-calendar-register.json').read_text()))
    parts = []
    for item in protocol['sources']:
        path = ROOT/'data/raw'/item['filename']
        if sha(path) != item['sha256']:
            raise ValueError('Historical source hash mismatch')
        old, _ = barchart.load(path)
        new = load_csv(path,item['contract'])
        pd.testing.assert_frame_equal(old,new[FIELDS])
        assert list(new.trade_date) == list(barchart.trade_dates(old.index).strftime('%Y-%m-%d'))
        parts.append(new)
    full = combine(parts,'2024-12-30','2025-09-30')
    rolls = []
    for prior in protocol['rollovers']:
        r = determine_roll(full,prior['from'],prior['to'],calendar,prior['decision_session'])
        for key,value in prior.items():
            assert r[key] == value, (key,r[key],value)
        rolls.append(r)
    return {'status':'PASS_DATA_PARITY_NO_SCORING', 'source_files':len(parts),
            'reconciled_contract_bars':len(full), 'rolls':rolls,
            'strategies_called':0, 'future_rows_read':0}


if __name__ == '__main__':
    print(json.dumps(verify(),indent=2))
