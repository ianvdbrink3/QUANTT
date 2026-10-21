"""Publish already-verified aggregates only; do not rerun research or raw fills."""
import argparse
import json
from pathlib import Path
from .holdout_data import REPO,sha
from .run_volume_path import report


def export(source):
    d=json.loads(source.read_text())
    assert d['classification']=='DESCRIPTIVE_NO_NEW_HOLDOUT_NO_OPTIMIZATION'
    assert d['eligible_days']==159 and d['previous_ORB_eligible']==148
    for name,digest in d['frozen_exports_unchanged_sha256'].items():
        assert sha(REPO/name)==digest, 'Frozen export changed: '+name
    for name,digest in d['code_sha256'].items():
        assert sha(Path(__file__).parent/name)==digest, 'Research code changed since source run: '+name
    for key,views in d['comparison'].items():
        full=views['active_reference_full159'];common=views['active_reference_common148'];extra=views['active_reference_added11']
        assert full['eligible_days']==159 and common['eligible_days']==148 and extra['eligible_days']==11
        assert abs(full['net_points']-common['net_points']-extra['net_points'])<1e-8
        assert full['trades']==d['paths'][key]['trades']==common['trades']+extra['trades']
        assert abs(sum(e['net_points'] for e in d['paths'][key]['exits'])-full['net_points'])<1e-8
    # Explicit allowlist: no raw bars, individual trades, paths, or daily features.
    public={k:d[k] for k in ['classification','period','eligible_days','previous_ORB_eligible',
                             'comparison','paths','measurement','inferential_tests','code_sha256',
                             'frozen_exports_unchanged_sha256']}
    public.update(label='vNext — continuous ATR + volume, 159 shared eligible days',
                  source_summary_sha256=sha(source),cost_rt_usd=24.5,
                  volume_rule='Same NY minute, median of prior maximum 20 observed active sessions, minimum 10; fixed 1.5x signal threshold. Current session excluded.',
                  privacy='Aggregates only; no raw bars or individual trade records.')
    (REPO/'public/data/research-volume-path.json').write_text(json.dumps(public,indent=2,allow_nan=False)+'\n')
    text=report(d)
    (REPO/'public/data/research-volume-path.md').write_text(text)
    (REPO/'docs/VOLUME_PATH_RESEARCH.md').write_text(text)
    print('Published aggregate JSON and Markdown; previous exports unchanged.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=REPO/'artifacts/volume-path-vnext/summary.json')
    export(parser.parse_args().source)
