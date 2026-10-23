"""Second source-reload reproduction, with sealed-sample read tripwire."""
import json
from pathlib import Path
from scripts import new_candidates_round01 as runner
from scripts.oos_preparation import year
from scripts.afternoon_inference_round import sha,dump,verify_lock


def run():
    root=runner.ROOT
    out=root/'artifacts/new-candidates-round01'
    files=[runner.OUT,root/'docs/NEW_CANDIDATES_ROUND01_REPORT.md']+sorted(out.glob('*.csv'))
    before={str(p.relative_to(root)):sha(p) for p in files}
    original=year.load_csv;reads=[]
    def guarded(path,contract):
        path=Path(path)
        if 'historical-replication' in str(path) or contract not in ['NQH25','NQM25','NQU25','NQZ25','NQH26','NQM26','NQU26','NQZ26']:
            raise PermissionError('New historical sample access forbidden in exploratory reproduction')
        reads.append(dict(path=str(path.relative_to(root)),contract=contract,sha256=sha(path)))
        return original(path,contract)
    year.load_csv=guarded
    try:runner.run()
    finally:year.load_csv=original
    after={str(p.relative_to(root)):sha(p) for p in files}
    if before!=after:raise ValueError('Source-reload reproduction differs')
    verify_lock();runner.verify()
    result=dict(status='SECOND_SOURCE_RELOAD_BYTE_IDENTICAL',artifacts=after,source_csv_reads=len(reads),
        sealed_sample_tripwire=True,new_historical_sample_reads=0,sources=reads,
        limitation='Second deterministic run on this machine and code, not independent implementation or external researcher')
    dump(root/'research/new-candidates-round01-verification.json',result)
    print(result['status'],len(reads),'source CSV reads',flush=True)


if __name__=='__main__':run()
