"""Append-only correction of timestamp-unit assumption, no return re-scoring.

The first falsification implementation compared DatetimeIndex.asi8 to a fixed
nanosecond count. Pandas can store that index in microseconds. Unit tests found
this before any new statistical tables were inspected. The completed first
round and its locked source remain intact; only the independent bar audit is
adjudicated here, using timedeltas rather than assumed integer units.
"""
import json
import numpy as np
import pandas as pd

from scripts.afternoon_falsification import ROOT,OUT,verify,dump
from scripts.oos_preparation.adapter import at,sha
from scripts.oos_preparation.year import load_registered,forbid_scoring
from scripts.oos_preparation.route import select_active
from scripts.reproduce_research.next_engine import Activation


def audit_bars(active,days):
    groups={d:g for d,g in active.groupby('trade_date')};rows=[]
    for day in days:
        g=groups[day];expected=pd.DatetimeIndex([at(day,c) for c in ('14:59','15:00','15:01')])
        z=g.loc[g.index.isin(expected)]
        missing=len(expected.difference(z.index));duplicates=int(z.index.duplicated().sum())
        spacing=bool(len(z)==3 and all(z.index[i+1]-z.index[i]==pd.Timedelta(minutes=1) for i in (0,1)))
        p=z[['open','high','low','close']].to_numpy()
        coherent=bool(np.isfinite(p).all() and (z.high>=z[['open','close','low']].max(axis=1)).all() and (z.low<=z[['open','close','high']].min(axis=1)).all())
        tick_grid=bool(np.allclose(p*4,np.rint(p*4),rtol=0,atol=1e-8))
        row=dict(day=day,missing=missing,duplicates=duplicates,spacing60seconds=spacing,coherent=coherent,
            tick_grid=tick_grid,one_contract=z.contract.nunique()==1,one_trade_date=z.trade_date.nunique()==1)
        if not missing and not duplicates:
            row['gap1500']=float(z.at[expected[1],'open']-z.at[expected[0],'close'])
            row['gap1501']=float(z.at[expected[2],'open']-z.at[expected[1],'close'])
        rows.append(row)
    a=pd.DataFrame(rows);gaps=[]
    for name in ('gap1500','gap1501'):
        if name not in a:continue
        x=a[name].dropna().to_numpy()
        gaps.append(dict(pair=name,nonzero_days=int((x!=0).sum()),mean_points=float(x.mean()),median_points=float(np.median(x)),
            min_points=float(x.min()),max_points=float(x.max()),max_absolute_points=float(np.abs(x).max())))
    failures=a[(a.missing>0)|(a.duplicates>0)|~a.spacing60seconds|~a.coherent|~a.tick_grid|~a.one_contract|~a.one_trade_date]
    return dict(days=len(a),expected_bars=3*len(a),observed_bars=3*len(a)-int(a.missing.sum())+int(a.duplicates.sum()),
        missing=int(a.missing.sum()),duplicates=int(a.duplicates.sum()),flagged_days=len(failures),price_gaps=gaps,
        second_source_verified=False,limitation='Same-source unit-independent timestamp/OHLC audit; no independent label semantics, subsecond path or fill certification.'),a


def run():
    verify()
    if (OUT/'time-audit-correction.json').exists():raise ValueError('Corrected audit already recorded, do not overwrite')
    with forbid_scoring():
        full,manifest,_=load_registered()
        a=json.loads((ROOT/'research/holdout-protocol.json').read_text());b=json.loads((ROOT/'research/oos-year-rollovers.json').read_text())
        schedule=[Activation('NQH25','2024-12-30'),Activation('NQM25','2025-03-19')]
        schedule += [Activation(r['to'],r['effective_session']) for r in a['rollovers']+b['rollovers']]
        active=select_active(full,schedule)
    quality=json.loads((ROOT/'artifacts/raw-market/quality.json').read_text());days=[r['day'] for r in quality if r['included']]
    integrity,rows=audit_bars(active,days)
    legacy=json.loads((OUT/'summary.json').read_text())
    old=pd.read_csv(OUT/'bar-audit.csv')
    for column in ('day','missing','duplicates','coherent','tick_grid','one_contract','one_trade_date','gap1500','gap1501'):
        if not np.array_equal(old[column],rows[column]):raise AssertionError('Correction changed more than spacing check: '+column)
    rows.to_csv(OUT/'bar-audit-corrected.csv',index=False,float_format='%.17g')
    correction=dict(status='APPEND_ONLY_UNIT_ASSUMPTION_CORRECTION_NO_STATISTIC_CHANGED',
        reason='Legacy.asi8 spacing compared microsecond timestamps with60e9 assumed nanoseconds; use Timedelta comparisons.',
        correction_detected_by='Synthetic unit tests before inspecting statistical result tables',
        legacy_flagged_days=legacy['integrity']['flagged_days'],corrected_integrity=integrity,
        old_completed_sha256=sha(OUT/'COMPLETED.json'),corrected_csv_sha256=sha(OUT/'bar-audit-corrected.csv'),
        correction_source_sha256=sha(ROOT/'scripts/falsification_time_audit.py'),
        statistical_tables_or_pvalues_changed=False,source_files=len(manifest['sources'])+len(manifest['warmup_sources']))
    dump(OUT/'time-audit-correction.json',correction)
    dump(ROOT/'research/afternoon-falsification-time-audit-correction.json',correction)
    print(json.dumps(dict(flagged_days_before=legacy['integrity']['flagged_days'],flagged_days_after=integrity['flagged_days'],
        changed_statistics=False),indent=2))


if __name__=='__main__':run()
