"""Descriptive, nonoverlapping morning anatomy; no strategy or inference run."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.afternoon_falsification import verify as verify_afternoon
from scripts.causal_map.__main__ import verify as verify_map
from scripts.oos_preparation.adapter import at, sha
from scripts.oos_preparation.year import forbid_scoring, load_registered
from scripts.oos_preparation.route import select_active
from scripts.reproduce_research.next_engine import Activation
from scripts.register_afternoon_candidate import verify as verify_candidate

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'artifacts/morning-recovery-anatomy'
PROTOCOL = ROOT/'research/morning-recovery-anatomy-protocol.json'
LOCK = ROOT/'research/morning-recovery-anatomy-lock.json'


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n')


def register():
    verify_candidate(); verify_afternoon(); verify_map()
    protocol = dict(status='DESCRIPTIVE_NONOVERLAPPING_WINDOWS_NO_NEW_HYPOTHESIS_TESTS',
        sample='Same435 complete RTH days; existing69 Gap-Down and101 A_ONL_ACCEPT 60m-event days,21 overlap,149 unique. No new level thresholds or optimized subgroups.',
        first_window='09:30 Open to09:44 Close. Classify strictly negative, strictly positive, exactly zero separately. Known at09:45 under internally supported bar-start convention.',
        following_window='09:45 Open to10:29 Close, exactly45 bars. Direct long-signed end-start price change and10000*ln(end/start). No09:30-09:44 bar or09:44close-to09:45open gap enters following return.',
        requested_a='Only69 Gap-Down days partitioned by first-window sign; retain zero days even if empty.',
        requested_b='Requested48 Gap-only,80 ONL-only,21 both are retrospective whole-day event labels. They cannot all be represented as known at09:45.',
        timing_audit='Report ONL confirmation boundary<=15 (known09:45),16..60 (later through10:30),>60 (after the following window). No event boundary shift or redefining101-day sample.',
        causal_companion='Separately partition G union O_early, where O_early is exactly the frozen ONL days confirmed by09:45. G-only means no ONL confirmed YET, not no future ONL. Never use later ONL to select this companion sample.',
        output='Counts, means, medians, P10/P25/P75/P90, fraction following return>0, and descriptive between-group differences. No p-values, confidence intervals, significance claims, costs, entries, stops, targets, PnL or filters.',
        check='First-window classification unchanged by truncating at09:45 or mutating later prices. Direct45-minute outcome, endpoint-gap reconciliation and fresh source-reload exact replay. Separate15:00 candidate lock must remain intact.',
        publication='Local only; no new GitHub/Vercel release authorized.')
    files = ['scripts/morning_recovery_anatomy.py', 'research/morning-recovery-anatomy-protocol.json',
        'research/afternoon-candidate-v1-lock.json', 'artifacts/causal-map/COMPLETED.json',
        'artifacts/causal-map/events-horizons.csv', 'artifacts/raw-market/quality.json',
        'research/oos-year-sources.json', 'research/holdout-protocol.json', 'research/oos-year-rollovers.json']
    if PROTOCOL.exists() and json.loads(PROTOCOL.read_text()) != protocol:
        raise ValueError('Refuse protocol replacement')
    dump(PROTOCOL, protocol)
    snapshot = dict(status='LOCKED_BEFORE_NEW_0945_1030_OUTCOMES',
        files_sha256={name:sha(ROOT/name) for name in files})
    if LOCK.exists() and json.loads(LOCK.read_text()) != snapshot:
        raise ValueError('Refuse lock replacement')
    dump(LOCK, snapshot)
    return dict(status=snapshot['status'], locked_files=len(files))


def preflight():
    verify_candidate(); verify_afternoon(); verify_map()
    for name, digest in json.loads(LOCK.read_text())['files_sha256'].items():
        if sha(ROOT/name) != digest:
            raise ValueError('Frozen method changed: '+name)


def early_status(prices):
    if len(prices['close']) < 15 or len(prices['open']) < 1:
        raise ValueError('Incomplete first quarter')
    value = float(prices['close'][14]-prices['open'][0])
    return 'NEGATIVE' if value < 0 else ('POSITIVE' if value > 0 else 'FLAT')


def measurement(prices):
    if any(len(prices[z]) != 60 or not np.isfinite(prices[z]).all() for z in ('open','close')):
        raise ValueError('No shortened or imputed morning window')
    o0, c14, o15, c59 = (float(prices['open'][0]), float(prices['close'][14]),
                        float(prices['open'][15]), float(prices['close'][59]))
    if min(o0, c14, o15, c59) <= 0:
        raise ValueError('Invalid log-price input')
    result = dict(first_quarter_status=early_status(prices), early_points=c14-o0,
        boundary_gap=o15-c14, following_points=c59-o15, following_logbps=10000*np.log(c59/o15))
    assert np.isclose(result['early_points']+result['boundary_gap']+result['following_points'], c59-o0, rtol=0, atol=1e-10)
    return result


def known_groups(gaps, onl_boundaries):
    early = {day for day, boundary in onl_boundaries.items() if boundary <= 15}
    return dict(GAP_ONLY_KNOWN_0945=gaps-early, ONL_ONLY_KNOWN_0945=early-gaps, BOTH_KNOWN_0945=gaps&early)


def description(frame, days, view, group):
    g = frame[frame.day.isin(days)]
    result = dict(view=view, group=group, days=len(g))
    for metric in ('following_points', 'following_logbps'):
        v = g[metric].to_numpy(float)
        result[metric] = dict(mean=float(np.mean(v)) if len(v) else None,
            median=float(np.median(v)) if len(v) else None,
            **{name:float(np.quantile(v,q)) if len(v) else None for name,q in [('p10',.1),('p25',.25),('p75',.75),('p90',.9)]})
    result['positive_fraction'] = float(g.following_points.gt(0).mean()) if len(g) else None
    return result


def frozen_groups():
    f = pd.read_csv(ROOT/'artifacts/causal-map/events-horizons.csv',
        usecols=['day','mechanism','boundary','horizon'])
    g = f[f.mechanism.eq('B_GAP_DOWN_0930') & f.horizon.eq('60')]
    o = f[f.mechanism.eq('A_ONL_ACCEPT') & f.horizon.eq('60')]
    assert g.day.is_unique and o.day.is_unique
    gaps, boundaries = set(g.day), dict(zip(o.day, o.boundary.astype(int)))
    onl = set(boundaries)
    assert (len(gaps),len(onl),len(gaps&onl),len(gaps|onl)) == (69,101,21,149)
    return gaps, boundaries


def load_active():
    full, manifest, _ = load_registered()
    a = json.loads((ROOT/'research/holdout-protocol.json').read_text())
    b = json.loads((ROOT/'research/oos-year-rollovers.json').read_text())
    schedule = [Activation('NQH25','2024-12-30'),Activation('NQM25','2025-03-19')]
    schedule += [Activation(r['to'],r['effective_session']) for r in a['rollovers']+b['rollovers']]
    return select_active(full,schedule), len(manifest['warmup_sources'])+len(manifest['sources'])


def extract(active, days):
    groups = {d:g for d,g in active.groupby('trade_date')}
    records = []
    for day in sorted(days):
        index = pd.date_range(at(day,'09:30'),at(day,'10:30'),freq='min',inclusive='left')
        g = groups[day].reindex(index)
        p = {z:g[z].to_numpy(float) for z in ('open','close')}
        r = measurement(p)
        prefix = {z:v[:15] for z,v in p.items()}
        assert early_status(prefix) == r['first_quarter_status']
        mutated = {z:v.copy() for z,v in p.items()}
        for value in mutated.values():
            value[15:] *= 2
        assert early_status(mutated) == r['first_quarter_status']
        assert g.contract.nunique() == 1
        records.append(dict(day=day,**r))
    return pd.DataFrame(records)


def calculations(frame, gaps, onl_boundaries):
    onl = set(onl_boundaries)
    whole = dict(GAP_ONLY=gaps-onl, ONL_ONLY=onl-gaps, BOTH=gaps&onl)
    known = known_groups(gaps,onl_boundaries)
    rows = []
    for sign in ('NEGATIVE','POSITIVE','FLAT'):
        selected = set(frame[frame.first_quarter_status.eq(sign)].day)&gaps
        rows.append(description(frame,selected,'GAP_OPENING_SIGN',sign))
    for view, groups in [('RETROSPECTIVE_149',whole),('KNOWN_AT_0945',known)]:
        for group, members in groups.items():
            rows.append(description(frame,members,view,group))
    timing = []
    for group, members in whole.items():
        onl_days = members&onl
        timing.append(dict(group=group,days=len(members),ONL_days=len(onl_days),
            known_by0945=sum(onl_boundaries[d]<=15 for d in onl_days),
            later_through1030=sum(15<onl_boundaries[d]<=60 for d in onl_days),
            after1030=sum(onl_boundaries[d]>60 for d in onl_days)))
    differences = []
    for view in ('RETROSPECTIVE_149','KNOWN_AT_0945'):
        selected = [r for r in rows if r['view']==view]
        for i,a in enumerate(selected):
            for b in selected[i+1:]:
                differences.append(dict(view=view,comparison=a['group']+' minus '+b['group'],
                    mean_difference_points=a['following_points']['mean']-b['following_points']['mean'],
                    median_difference_points=a['following_points']['median']-b['following_points']['median']))
    return dict(tables=rows, timing=timing, descriptive_differences=differences)


def verify():
    preflight()
    done = json.loads((OUT/'COMPLETED.json').read_text())
    for name,digest in done['files_sha256'].items():
        if sha(ROOT/name) != digest:
            raise ValueError('Anatomy evidence changed: '+name)
    return done['verification']


def run():
    preflight()
    if (OUT/'COMPLETED.json').exists():
        raise ValueError('Closed descriptive round; use --verify')
    gaps, boundaries = frozen_groups()
    days = gaps|set(boundaries)
    complete = {r['day'] for r in json.loads((ROOT/'artifacts/raw-market/quality.json').read_text()) if r['included']}
    assert days <= complete
    with forbid_scoring():
        active, source_count = load_active()
        frame = extract(active,days)
        active2, _ = load_active()
        replay = extract(active2,days)
    pd.testing.assert_frame_equal(frame,replay,check_exact=True)
    result = calculations(frame,gaps,boundaries)
    assert result == calculations(replay,gaps,boundaries)
    OUT.mkdir(parents=True,exist_ok=True)
    frame.to_csv(OUT/'measurements.csv',index=False,float_format='%.17g')
    replay.to_csv(OUT/'measurements-replay.csv',index=False,float_format='%.17g')
    assert sha(OUT/'measurements.csv') == sha(OUT/'measurements-replay.csv')
    verification = dict(source_files=source_count,frozen_universe_days=435,requested_unique_days=149,
        known_at0945_unique_days=len(set().union(*known_groups(gaps,boundaries).values())),
        first_quarter_prefix_checks=len(days),first_quarter_future_mutation_checks=len(days),
        exact_source_replay=True,nonoverlapping_bars=True,new_afternoon_runs=0,new_strategy_runs=0,new_pvalues=0,
        protected_archive_files=verify_candidate()['protected_archive_files'])
    dump(OUT/'summary.json',dict(status='DESCRIPTIVE_ONLY_NO_NEW_MODEL',**result,verification=verification,
        protocol_sha256=sha(PROTOCOL),candidate_lock_sha256=sha(ROOT/'research/afternoon-candidate-v1-lock.json')))
    names=['measurements.csv','measurements-replay.csv','summary.json']
    dump(OUT/'COMPLETED.json',dict(verification=verification,
        files_sha256={str((OUT/n).relative_to(ROOT)):sha(OUT/n) for n in names}))
    preflight()
    print(json.dumps(verification,indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--register',action='store_true')
    mode.add_argument('--run',action='store_true')
    mode.add_argument('--verify',action='store_true')
    args = p.parse_args()
    if args.register:
        print(json.dumps(register(),indent=2))
    elif args.verify:
        print(json.dumps(verify(),indent=2))
    else:
        run()
