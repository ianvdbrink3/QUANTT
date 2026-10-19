"""Append-only experiment ledger with atomic writes and explicit data provenance."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime,timezone

def record_experiment(path: str | Path, *, hypothesis_id: str, status: str,
                      dataset_hash: str, code_ref: str, parameters: dict,
                      source_kind: str, results: dict) -> dict:
    if source_kind not in {'synthetic_fixture','observed_cfd','observed_future'}:
        raise ValueError('Unknown provenance')
    if status not in {'PROPOSED','SCREENED','REJECTED','REQUIRES_MORE_DATA',
                      'VALIDATION_CANDIDATE','HOLDOUT_PASSED','PAPER_TRADING','RESEARCH_PAUSED'}:
        raise ValueError('Unsupported research status')
    if source_kind=='synthetic_fixture' and status in {'HOLDOUT_PASSED','PAPER_TRADING'}:
        raise ValueError('Synthetic fixtures cannot validate an edge')
    if not all((hypothesis_id,dataset_hash,code_ref)): raise ValueError('Missing audit identity')
    payload={'hypothesis_id':hypothesis_id,'status':status,'dataset_hash':dataset_hash,
             'code_ref':code_ref,'parameters':parameters,'source_kind':source_kind,
             'results':results}
    stable=json.dumps(payload,sort_keys=True,allow_nan=False,separators=(',',':'))
    payload['run_id']=hashlib.sha256(stable.encode()).hexdigest()
    payload['recorded_at_utc']=datetime.now(timezone.utc).isoformat()
    target=Path(path)
    target.parent.mkdir(parents=True,exist_ok=True)
    # Append only, including repeated runs for a clear trail. No prior result overwritten.
    with target.open('a',encoding='utf-8') as out:
        out.write(json.dumps(payload,sort_keys=True,allow_nan=False)+'\n')
        out.flush()
        os.fsync(out.fileno())
    return payload
