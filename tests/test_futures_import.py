import csv
import json
from pathlib import Path
import pandas as pd
import pytest
from quantlab.futures_import import stage_futures_csv,main
from quantlab.futures_csv import REQUIRED

def source(tmp_path,rows=None):
    path=tmp_path/'bars.csv'
    samples=rows or [
        ['2026-10-19T13:30:00Z','NQZ26','20000','20001','19999.75','20000.25','14'],
        ['2026-10-19T13:31:00Z','NQZ26','20000.25','20001','20000','20000.75','18']]
    with path.open('w',newline='') as h:
        w=csv.writer(h);w.writerow(REQUIRED);w.writerows(samples)
    return path

def test_contract_native_staging_marks_unverified(tmp_path):
    path=source(tmp_path)
    dest=tmp_path/'stage.parquet'
    result=stage_futures_csv(path,dest,instrument='NQ',source='licensed-vendor-to-be-verified')
    assert result['rows']==2 and not result['trading_edge_validation_allowed']
    assert result['structural_validation']['contracts']=={'NQZ26':2}
    d=pd.read_parquet(dest)
    assert d.market_type.tolist()==['future','future']
    assert set(d.venue)=={'CME_UNVERIFIED'}

def test_cli_writes_report_and_parquet(tmp_path):
    path=source(tmp_path);dest=tmp_path/'clean.parquet'
    assert main(['--input',str(path),'--out',str(dest),
                 '--instrument','NQ','--source','unverified-user-export'])==0
    quality=json.loads((tmp_path/'clean.quality.json').read_text())
    assert quality['contract_provenance_verified'] is False
    assert dest.exists()

def test_reject_cfd_source(tmp_path):
    with pytest.raises(ValueError,match='non-CFD'):
        stage_futures_csv(source(tmp_path),tmp_path/'out.parquet',instrument='NQ',source='Dukascopy')

def test_reject_invalid_tick_before_parquet(tmp_path):
    rows=[['2026-10-19T13:30:00Z','NQZ26','20000','20001.10','19999.75','20000.25','14']]
    with pytest.raises(ValueError,match='tick'):
        stage_futures_csv(source(tmp_path,rows),tmp_path/'out.parquet',instrument='NQ',source='broker-export')
    assert not (tmp_path/'out.parquet').exists()
