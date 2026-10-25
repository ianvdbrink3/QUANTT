import numpy as np

MODELS=('S1_SELECTIVE','S2_BROAD_NO_STOP','S2_BROAD_STOP','S3_BASE_1X','S3_NONHOT_1X')


def assemble(selective_stop,pullback,bull_no_stop,bull_stop):
    for label,rows in (('A',selective_stop),('B',pullback),('bull',bull_no_stop),('bull_stop',bull_stop)):
        if len(rows)!=len({t['day'] for t in rows}):
            raise ValueError('Duplicate execution in '+label)
    if {t['day'] for t in bull_no_stop}!={t['day'] for t in bull_stop}:
        raise ValueError('Stop changed overnight entry membership')
    # S3 is one bull position, never bull+A or extra notional on strong days.
    nonhot=[t for t in bull_stop if np.isfinite(t['range_atr']) and t['range_atr']<=.85]
    return dict(S1_SELECTIVE=selective_stop+pullback,
                S2_BROAD_NO_STOP=bull_no_stop+pullback,
                S2_BROAD_STOP=bull_stop+pullback,
                S3_BASE_1X=list(bull_stop),S3_NONHOT_1X=nonhot)


def panel(rows,dates):
    ids={d:i for i,d in enumerate(dates)}
    values=np.zeros((len(dates),len(MODELS)))
    for j,m in enumerate(MODELS):
        for t in rows[m]:
            if t['exit_day'] not in ids:raise ValueError('Missing cash boundary')
            values[ids[t['exit_day']],j]+=t['net_R']
    return values
