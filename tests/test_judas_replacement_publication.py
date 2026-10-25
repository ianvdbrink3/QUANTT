import csv
import json
import pytest
from scripts import publish_judas_replacement as pub
from scripts.judas_replacement import __main__ as run


def test_append_only_public_rows_are_exact_verified_aggregates():
    public=json.loads(pub.PUBLIC.read_text());source=json.loads(run.RESULT.read_text())
    assert len(public['winner_rows'])==42 and len(public['winner_names'])==7
    for row,original in zip(public['winner_rows'],source['winner_rows']):
        assert row=={k:original[k] for k in pub.WIN}
    for b in run.PERIODS:
        for m,row in public['performance'][b].items():
            original=source['performance'][b][m]
            assert all(row[k]==original[k] for k in pub.PORT)
            assert sum(q['net_R'] for q in row['quarterly'])==pytest.approx(row['net_R'])
    assert len(list(csv.DictReader((run.ROOT/'public/reports/SEVEN_ICT_VARIANTS.csv').open())))==42
    assert len(list(csv.DictReader((run.ROOT/'public/reports/JUDAS_PORTFOLIO_PERFORMANCE.csv').open())))==12
    assert len(list(csv.DictReader((run.ROOT/'public/reports/JUDAS_REPLACEMENT_INFERENCE.csv').open())))==9


def test_public_export_omits_private_prices_and_times():
    x=json.loads(pub.PUBLIC.read_text())
    forbidden={'path_points','entry_price','exit_price','entry_time','exit_time','entry_bar','exit_bar','open','high','low','close','volume','daily_panels','source_verification'}
    def visit(v):
        if isinstance(v,dict):
            assert not forbidden&set(v)
            for child in v.values():visit(child)
        elif isinstance(v,list):
            for child in v:visit(child)
    visit(x)
    assert x['raw_data_published'] is False and x['independent_validation'] is False


def test_export_hashes_byte_copies_and_all_previous_files_remain_immutable():
    manifest=json.loads(pub.MANIFEST.read_text())
    for name,digest in manifest['files_sha256'].items():assert run.h.sha(run.ROOT/name)==digest
    assert run.REPORT.read_bytes()==(run.ROOT/'public/reports/JUDAS_ONE_FOR_ONE_REPLACEMENT.md').read_bytes()
    run.verify()
