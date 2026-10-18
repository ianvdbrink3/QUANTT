import pandas as pd
import pytest

@pytest.mark.parametrize('day,ny,london',[
    ('2025-03-07',14,8),('2025-03-10',13,8),('2025-03-28',13,8),('2025-03-31',13,7),
    ('2024-03-11',13,8),('2026-03-09',13,8)])
def test_independent_us_europe_dst(day,ny,london):
    n=pd.Timestamp(day+' 09:30',tz='America/New_York').tz_convert('UTC')
    l=pd.Timestamp(day+' 08:00',tz='Europe/London').tz_convert('UTC')
    assert (n.hour,n.minute)==(ny,30)
    assert l.hour==london


def test_dst_roundtrip_fall_duplicate_clock_is_unambiguous():
    index=pd.date_range('2025-11-02T05:00Z',periods=120,freq='min')
    assert index.tz_convert('America/New_York').tz_convert('UTC').equals(index)
    assert index.is_unique
