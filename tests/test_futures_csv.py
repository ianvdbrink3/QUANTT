"""Regression checks for contract-native CSV safety gate."""
import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from quantlab.futures_csv import validate_contract_csv

FIELDS=['timestamp_utc','contract_id','open','high','low','close','volume']
def bar(ts='2026-10-19T13:30:00Z',contract='NQZ26',high='20001.00'):
    return [ts,contract,'20000.00',high,'19999.75','20000.25','125']

class TestFuturesCSV(unittest.TestCase):
    def check(self,rows,**kwargs):
        with TemporaryDirectory() as d:
            path=Path(d)/'minute.csv'
            with path.open('w',newline='') as stream:
                writer=csv.writer(stream)
                writer.writerow(FIELDS)
                writer.writerows(rows)
            return validate_contract_csv(path,**kwargs)
    def test_valid_contract(self):
        self.assertEqual(self.check([bar(),bar('2026-10-19T13:31:00Z')])['rows'],2)
    def test_gap_not_filled(self):
        result=self.check([bar(),bar('2026-10-19T13:33:00Z')])
        self.assertEqual(result['observed_gaps'][0]['missing_minutes'],2)
    def test_duplicate_fails(self):
        with self.assertRaisesRegex(ValueError,'Duplicate'): self.check([bar(),bar()])
    def test_naive_timestamp_fails(self):
        with self.assertRaisesRegex(ValueError,'UTC'): self.check([bar('2026-10-19T13:30:00')])
    def test_wrong_instrument_fails(self):
        with self.assertRaisesRegex(ValueError,'contract'): self.check([bar(contract='ESZ26')])
    def test_bad_tick_fails(self):
        with self.assertRaisesRegex(ValueError,'tick'): self.check([bar(high='20001.10')])
    def test_bad_ohlc_fails(self):
        with self.assertRaisesRegex(ValueError,'OHLC'): self.check([bar(high='19999.75')])
    def test_rollover_kept_separate(self):
        self.assertEqual(len(self.check([bar(),bar(contract='NQH27')])['contracts']),2)
