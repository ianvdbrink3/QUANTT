"""Append-only closure registry. Reproduction allowed, parameter tuning forbidden."""
import json
import subprocess
from pathlib import Path

from scripts.oos_preparation.adapter import sha
from scripts.oos_preparation.year import dump
from scripts.oos_preparation.seal import check
from scripts.verify_research_freeze import verify

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/'research/archived-experiments.json'
MODELS=['B_ORB5','B_ORB15','A_London_sweep','C_VWAP_extreme']


def verify_archive(root=ROOT):
    d=json.loads((root/'research/archived-experiments.json').read_text())
    if d['status']!='ARCHIVED_NOT_VALIDATED' or set(d['models'])!=set(MODELS):
        raise ValueError('Archive status/model drift')
    for name,digest in d['files_sha256'].items():
        if sha(root/name)!=digest:raise ValueError('Archived experiment bytes changed: '+name)
    return dict(status=d['status'],protected_files=len(d['files_sha256']),models=4)


def register():
    check();verify()
    if REGISTRY.exists():return verify_archive()
    names=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()
    protected=set(json.loads((ROOT/'research/vnext-freeze-manifest.json').read_text())['files_sha256'])
    protected.update(json.loads((ROOT/'research/oos-year-preregistration.json').read_text())['files_sha256'])
    protected.update(p for p in names if p.startswith('scripts/reproduce_research/') or
        p.startswith('public/data/research-year-holdout') or p.startswith('research/year-holdout') or
        p in ['scripts/year_holdout.py','scripts/publish_year_holdout.py','scripts/verify_year_holdout.py',
              'scripts/verify-year-holdout','docs/YEAR_HOLDOUT_2026-10-21.md','app/research/nq/YearHoldoutResults.tsx'])
    data=dict(status='ARCHIVED_NOT_VALIDATED',anchor_commit='9c890b1aa752f6941768c50c55f35ee779dbe903',
        models={s:dict(status='ARCHIVED_NOT_VALIDATED',versions=['Baseline v0.9','vNext159','fixed year holdout'],
            allowed='Historical reproduction and execution audit only',
            prohibited='Parameter tuning, rescue subgroups, renewed promotion or reuse as a candidate') for s in MODELS},
        historical_verdict='HOLDOUT_FAILED is preserved, not rewritten. Archive is a lifecycle status, not proof of universal absence of edge.',
        enforcement='SHA256 regression guard; historical functions retained only for reproducibility, no new runner calls them on real data.',
        files_sha256={p:sha(ROOT/p) for p in sorted(protected)})
    dump(REGISTRY,data);dump(ROOT/'public/data/research-experiment-archive.json',data)
    return verify_archive()


if __name__=='__main__':print(json.dumps(register(),indent=2))
