import lzma
import struct
import numpy as np
import pandas as pd
import pytest
from quantlab.data import decode_bi5, clean_bars, aggregate, contiguous_returns


def encode(rows):
    return lzma.compress(b''.join(struct.pack('>5If',*r) for r in rows))


def test_decoder_scale_ohlc_and_utc():
    payload=encode([(0,19495332,19498287,19493698,19504065,.02),(60,19498287,19498000,19497000,19500000,.01)])
    f=decode_bi5(payload,'2025-03-19')
    assert f.index[0]==pd.Timestamp('2025-03-19T00:00:00Z')
    assert f.open.iloc[0]==19495.332
    assert f.high.iloc[0]==19504.065
    assert f.low.iloc[0]==19493.698
    assert f.close.iloc[0]==19498.287
    assert clean_bars(f)[1]['price_anomalies']==0


def test_wrong_price_scale_rejected():
    payload=encode([(0,19495332,19498287,19493698,19504065,.02)])
    _,q=clean_bars(decode_bi5(payload,'2025-03-19',1))
    assert q['price_anomalies']==1
    assert q['validated_bars']==0


def test_filter_only_zero_volume_degenerate_bars():
    f=decode_bi5(encode([(0,20000000,20000000,20000000,20000000,0),
                       (60,20000000,20000000,20000000,20000000,.1),
                       (120,20000000,20001000,20000000,20001000,0)]),'2025-03-19')
    cleaned,q=clean_bars(f)
    assert q['flat_bars_filtered']==1
    assert cleaned.is_market_open.tolist()==[False,True,True]
    assert len(aggregate(cleaned,'5min'))==1
    assert aggregate(cleaned,'5min').minute_count.iloc[0]==2


@pytest.mark.parametrize('rows',[
    [(60,20000000,20000000,20000000,20000000,.1),(60,20000000,20000000,20000000,20000000,.1)],
    [(86400,20000000,20000000,20000000,20000000,.1)],
    [(1,20000000,20000000,20000000,20000000,.1)]])
def test_invalid_offsets_fail_closed(rows):
    with pytest.raises(ValueError): decode_bi5(encode(rows),'2025-03-19')


def test_truncated_record_rejected():
    with pytest.raises(ValueError): decode_bi5(lzma.compress(b'abc'),'2025-03-19')


def test_no_returns_across_missing_minutes():
    f=pd.DataFrame({'close':[100,101,110]},index=pd.to_datetime(['2025-03-19T12:00Z','2025-03-19T12:01Z','2025-03-19T12:05Z']))
    r=contiguous_returns(f)
    assert np.isclose(r.iloc[1],np.log(1.01))
    assert pd.isna(r.iloc[2])


def test_invalid_ohlc_and_volume_excluded():
    f=decode_bi5(encode([(0,20000000,20002000,20000000,20001000,.1),
                       (60,20000000,20000000,20000000,20000000,-1)]),'2025-03-19')
    assert clean_bars(f)[1]['price_anomalies']==2
