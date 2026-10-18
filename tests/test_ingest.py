import importlib.util
import lzma
from pathlib import Path
import struct
from datetime import date
import pytest

spec=importlib.util.spec_from_file_location('ingest',Path(__file__).parents[1]/'scripts/dukascopy_ingest.py')
ingest=importlib.util.module_from_spec(spec)
spec.loader.exec_module(ingest)
CFG={'data_url':'https://example.invalid','price_divisor':1000,'plausible_price_min':5000,'plausible_price_max':100000}
PAYLOAD=lzma.compress(struct.pack('>5If',0,20000000,20001000,20000000,20002000,.01))


def test_transient_failure_retries_and_writes_validated_cache(tmp_path,monkeypatch):
    monkeypatch.setattr(ingest,'ROOT',tmp_path)
    calls=[];sleeps=[]
    def fetch(*args):
        calls.append(1)
        if len(calls)<3: raise OSError('timeout')
        return 200,PAYLOAD,{}
    monkeypatch.setattr(ingest,'http_get',fetch)
    monkeypatch.setattr(ingest.time,'sleep',sleeps.append)
    result=ingest.fetch_day(date(2025,3,19),'USATECHIDXUSD',CFG)
    assert result['status']=='ok'
    assert result['attempts']==3
    assert 1<=sleeps[0]<2 and 2<=sleeps[1]<3
    assert len(list(tmp_path.rglob('*.parquet')))==1
    assert not list(tmp_path.rglob('*.part'))


def test_corrupt_payload_retried_not_published(tmp_path,monkeypatch):
    monkeypatch.setattr(ingest,'ROOT',tmp_path)
    monkeypatch.setattr(ingest,'http_get',lambda *a:(200,b'corrupt',{}))
    monkeypatch.setattr(ingest.time,'sleep',lambda *a:None)
    result=ingest.fetch_day(date(2025,3,19),'USATECHIDXUSD',CFG,attempts=2)
    assert result['status']=='failed'
    assert not list(tmp_path.rglob('*.parquet'))


@pytest.mark.parametrize('status,headers',[(429,{}),(202,{'challenge':True})])
def test_source_access_block_opens_circuit_immediately(tmp_path,monkeypatch,status,headers):
    monkeypatch.setattr(ingest,'ROOT',tmp_path)
    monkeypatch.setattr(ingest,'http_get',lambda *a:(status,b'',headers))
    result=ingest.fetch_day(date(2025,3,19),'USATECHIDXUSD',CFG)
    assert result['status']=='source_blocked'
    assert result['attempts']==1
    assert not list(tmp_path.rglob('*.parquet'))


def test_missing_day_not_reported_as_valid_empty_market(tmp_path,monkeypatch):
    monkeypatch.setattr(ingest,'ROOT',tmp_path)
    monkeypatch.setattr(ingest,'http_get',lambda *a:(404,b'',{}))
    result=ingest.fetch_day(date(2025,3,19),'USATECHIDXUSD',CFG)
    assert result['status']=='unavailable'
    assert 'validated_bars' not in result


def test_bulk_circuit_breaker_prevents_new_batches(tmp_path,monkeypatch):
    monkeypatch.setattr(ingest,'ROOT',tmp_path)
    (tmp_path/'configs').mkdir()
    (tmp_path/'configs/instruments.yaml').write_text('USATECHIDXUSD: {}')
    calls=[]
    def fetch(day,*args):
        calls.append(day)
        return {'date':day.isoformat(),'symbol':'USATECHIDXUSD','status':'source_blocked','attempts':1}
    monkeypatch.setattr(ingest,'fetch_day',fetch)
    errors=ingest.run(date(2025,3,1),date(2025,4,1),workers=2)
    assert len(calls)==2
    assert len(errors)==2
    assert len((tmp_path/'data/download_manifest.jsonl').read_text().splitlines())==2


def test_outage_stops_after_two_failed_batches(tmp_path,monkeypatch):
    monkeypatch.setattr(ingest,'ROOT',tmp_path)
    (tmp_path/'configs').mkdir()
    (tmp_path/'configs/instruments.yaml').write_text('USATECHIDXUSD: {}')
    calls=[]
    def fetch(day,*args):
        calls.append(day)
        return {'date':day.isoformat(),'symbol':'USATECHIDXUSD','status':'failed','attempts':5}
    monkeypatch.setattr(ingest,'fetch_day',fetch)
    ingest.run(date(2025,3,1),date(2025,4,1),workers=2)
    assert len(calls)==4
