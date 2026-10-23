import json
import numpy as np
from scripts.survivor_portfolio import ROOT, verify, MODELS


def result():return json.loads((ROOT/'research/three-survivors-results.json').read_text())


def test_frozen_files_preserved():assert len(verify()['protected_files'])>=500


def test_public_aggregate_matches():
    assert (ROOT/'public/data/three-survivors.json').read_bytes()==(ROOT/'research/three-survivors-results.json').read_bytes()


def test_exact_calendar_counts():
    assert [s['days'] for s in result()['samples'].values()]==[435,493]
    assert [s['atr_ready_days'] for s in result()['samples'].values()]==[418,477]


def test_original_signal_parity():
    for s in result()['samples'].values():assert s['original_trade_parity']
    assert [v['original'] for v in result()['samples']['DISCOVERY']['counts'].values()]==[81,109,63]


def test_equal_third_additivity():
    for s in result()['samples'].values():
        r=s['variants']['NQ_ATR']
        assert np.isclose(r['PORTFOLIO_EQUAL_THIRD']['total_R'],sum(r[m]['total_R'] for m in MODELS)/3)


def test_portfolio_intervals_do_not_hide_zero():
    for s in result()['samples'].values():
        lo,hi=s['variants']['NQ_ATR']['PORTFOLIO_EQUAL_THIRD']['total_R_fixed_N_ci95']
        assert lo<0<hi


def test_reference_integer_budget_not_reoptimized():
    d=result()['samples']['DISCOVERY']['variants']['MNQ_INTEGER']['PORTFOLIO_EQUAL_THIRD']
    assert d['sum_contracts_or_point_weights']==0
    assert d['total_USD_reference']==0


def test_prereg_unseen_status_and_old_fragment():
    text=(ROOT/'docs/THREE_SURVIVORS_PREREGISTRATION_2019_2021.md').read_text()
    assert 'REGISTERED_NOT_RELEASED' in text
    assert '2019-01-14' in text
    assert 'Holm6' in text


def test_public_no_private_trade_arrays():
    text=(ROOT/'public/data/three-survivors.json').read_text()
    assert 'entry_price' not in text and '/Users/' not in text and '"dates"' not in text


def test_intake_unique_not_physical_count():
    x=json.loads((ROOT/'research/afternoon-historical-intake-batch02-final.json').read_text())
    assert x['new_unique_blocks']==len({r['sequence'] for r in x['files']})
    assert x['new_unique_blocks']+6+x['pending_plan_blocks']==103


def test_intake_private_copies_byte_identical():
    from scripts.oos_preparation.adapter import sha
    import subprocess
    x=json.loads((ROOT/'research/afternoon-historical-intake-batch02-final.json').read_text())
    for r in x['files']:
        assert sha(ROOT/r['private_copy'])==r['sha256']
        assert subprocess.run(['git','check-ignore','-q',r['private_copy']],cwd=ROOT).returncode==0
