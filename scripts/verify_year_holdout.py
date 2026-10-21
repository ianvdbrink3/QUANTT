"""Verify completed results and all registered raw bytes without a third scoring run."""
import json

from scripts.year_holdout import ROOT,OUTPUT,preflight,compare_runs
from scripts.oos_preparation.year import load_registered
from scripts.oos_preparation.adapter import sha
from scripts.verify_research_freeze import verify


def verify_completed():
    preflight()
    _,sources,_=load_registered()
    reference=json.loads((ROOT/'research/year-holdout-verification.json').read_text())
    actual=compare_runs()
    if actual['files_sha256']!=reference['files_sha256']:raise ValueError('Completed private outputs changed')
    for name,digest in reference['publication_files_sha256'].items():
        for run in ['first','reproduction']:
            if sha(OUTPUT/run/'publication'/name)!=digest:raise ValueError('Publication output changed')
        suffix={'results.json':'json','REPORT.md':'md'}.get(name,name)
        if sha(ROOT/'public/data'/('research-year-holdout.'+suffix))!=digest:
            raise ValueError('Public export differs from verified source run')
    verify()
    return dict(status='PASS_SOURCE_HASHES_AND_BYTE_IDENTICAL_RESULTS',
        source_files_verified=len(sources['sources'])+len(sources['warmup_sources']),
        private_files=len(reference['files_sha256']),publication_files=len(reference['publication_files_sha256']),
        new_scoring_invocations=0,frozen_files=73)


if __name__=='__main__':print(json.dumps(verify_completed(),indent=2))
