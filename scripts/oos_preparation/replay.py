"""Full historical-only regression; NEVER load future source CSVs here."""
import json
from pathlib import Path
import pandas as pd

from .adapter import Calendar,combine,load_csv,sha
from .route import indicator_state,technical_eligibility,replay_historical,STRATEGIES
from scripts.reproduce_research.next_engine import Activation
from scripts.verify_research_freeze import verify

ROOT=Path(__file__).resolve().parents[2]


def run(root=ROOT):
    verify(root)
    protocol=json.loads((root/'research/holdout-protocol.json').read_text())
    parts=[]
    for item in protocol['sources']:
        p=root/'data/raw'/item['filename']
        if sha(p)!=item['sha256']:raise ValueError('Historical source hash mismatch')
        b=load_csv(p,item['contract']);parts.append(b[b.trade_date.le('2025-09-30')])
    full=combine(parts,'2024-12-30','2025-09-30')
    schedule=[Activation('NQH25','2024-12-30'),Activation('NQM25','2025-03-19')]
    schedule += [Activation(r['to'],r['effective_session']) for r in protocol['rollovers']]
    calendar=Calendar(json.loads((root/'research/oos-year-calendar.json').read_text()))
    print('Historical replay ONLY2024-12-30..2025-09-30,30 registered files',flush=True)
    trades,eligibility=replay_historical(full,schedule,calendar)
    # References independently anchored in frozen retrospective protocol.
    reference=json.loads((root/'research/volume-stability-protocol.json').read_text())['source_sha256']
    results={}
    for name,frame in [('trades',trades),('eligibility',eligibility)]:
        path=root/f'artifacts/volume-path-vnext/{name}.csv'
        if sha(path)!=reference[str(path.relative_to(root))]:raise ValueError('Changed frozen private reference')
        expected=pd.read_csv(path)
        # Full CSV serialization must match, not only aggregate metrics.
        actual=frame.to_csv(index=False)
        if actual!=path.read_text():
            from io import StringIO
            pd.testing.assert_frame_equal(pd.read_csv(StringIO(actual)),expected,check_exact=True)
            raise ValueError('Historical CSV serialization differs: '+name)
        results[name]=dict(rows=len(frame),reference_sha256=sha(path),byte_identical=True)
    print('Historical ledgers byte-identical; independent prerequisite eligibility check',flush=True)
    state,_,_=indicator_state(full,schedule)
    technical=technical_eligibility(state,calendar,'2024-12-30','2025-09-30')
    counts={}
    for s in STRATEGIES:
        expected=set(eligibility.loc[eligibility.strategy.eq(s)&eligibility.eligible,'trade_date'])
        actual=set(technical.loc[technical.strategy.eq(s)&technical.eligible,'trade_date'])
        if expected!=actual:raise ValueError('Readiness predicates differ '+s)
        counts[s]=len(actual)
    assert all(v==159 for v in counts.values())
    freeze=verify(root)
    evidence=dict(status='PASS_HISTORICAL_FULL_LEDGER_BYTE_PARITY',period=['2024-12-30','2025-09-30'],
        source_files=30,future_source_files_opened=0,future_signals_computed=False,
        historical_results=results,technical_eligible_days=counts,freeze=freeze)
    evidence['implementation_sha256']={name:sha(root/name) for name in [
        'scripts/oos_preparation/route.py','scripts/oos_preparation/replay.py',
        'scripts/reproduce_research/engine.py','scripts/reproduce_research/continuous.py',
        'scripts/reproduce_research/volume_path.py']}
    out=root/'research/oos-year-historical-parity.json'
    out.write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence,indent=2),flush=True)
    return evidence


if __name__=='__main__':run()
