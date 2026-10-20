import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from verify_release import verify


def test_separate_frozen_discovery_holdout_and_posthoc_release():
    result=verify()
    assert result['status']=='PASS'
    assert result['holdout_status']=='HOLDOUT_FAILED'
    assert not result['raw_required_for_this_offline_guard']
