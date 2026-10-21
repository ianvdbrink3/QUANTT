"""Reproducible year quality/eligibility gate. Future signal/PnL calls forbidden."""
import argparse
import hashlib
import json
from collections import Counter
from contextlib import contextmanager
from pathlib import Path

import pandas as pd

from .adapter import Calendar,at,audit_contract,combine,determine_roll,load_csv,sha
from .route import indicator_state,technical_eligibility,STRATEGIES
from scripts.reproduce_research.next_engine import Activation
from scripts.verify_research_freeze import verify

ROOT=Path(__file__).resolve().parents[2]
START,END='2025-10-01','2026-09-30'


@contextmanager
def forbid_scoring():
    """Runtime tripwire, not merely a statement in the exported JSON."""
    from scripts.reproduce_research import engine
    names=['build_features','hypotheses','simulate','baseline','metrics','bootstrap']
    previous={n:getattr(engine,n) for n in names}
    def denied(*args,**kwargs):
        raise PermissionError('HOLDOUT_LOCKED: signal, feature or PnL function called during preparation')
    try:
        for name in names:setattr(engine,name,denied)
        yield
    finally:
        for name,value in previous.items():setattr(engine,name,value)


def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')


def object_hash(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def register(root=ROOT):
    """One-time migration of previously accepted hashes, not fresh trust-on-use."""
    from .december import SOURCES
    accepted={x['filename']:x['sha256'] for x in json.loads((root/'research/oos-source-register.json').read_text())['sources']}
    accepted.update({name:digest for _,name,digest in SOURCES})
    provenance={}
    def visit(obj):
        if isinstance(obj,dict):
            if 'filename' in obj and 'sha256' in obj:
                name,digest=obj['filename'],obj['sha256']
                if name in accepted and accepted[name]!=digest: raise ValueError('Conflicting intake hash')
                accepted[name]=digest
            for value in obj.values():visit(value)
        elif isinstance(obj,list):
            for value in obj:visit(value)
    for p in sorted((root/'artifacts').glob('nq*26-batch*/audit.json')):
        visit(json.loads(p.read_text()));provenance[str(p.relative_to(root))]=sha(p)
    sources=[]
    for p in sorted((root/'data/raw/oos').glob('*.csv')):
        if p.name not in accepted or sha(p)!=accepted[p.name]:raise ValueError('Unregistered/changed intake '+p.name)
        contract=p.name.split('_')[0].upper()
        b=load_csv(p,contract)
        sources.append(dict(filename=p.name,relative_private_path=str(p.relative_to(root)),contract=contract,
            sha256=sha(p),rows=len(b),first_utc=b.index.min().isoformat(),last_utc=b.index.max().isoformat(),
            cap_warning=len(b)>=19999,prior_access='Quality-only intake; logs incomplete, absolute non-use not certified'))
    historical=json.loads((root/'research/holdout-protocol.json').read_text())['sources']
    result=dict(classification='SOURCES_LOCKED_BEFORE_SIGNALS',period=[START,END],sources=sources,
        warmup_sources=[dict(x,relative_private_path='data/raw/'+x['filename']) for x in historical],
        prior_intake_evidence_sha256=provenance,license_status='UNVERIFIED_NO_RAW_PUBLICATION',
        rule='No Downloads fallback. Require all registered bytes, reject changes and conflicting overlap. Capped U26 exports overlap earlier accepted blocks; cap flag retained, not represented as uncapped.')
    path=root/'research/oos-year-sources.json'
    if path.exists() and json.loads(path.read_text())!=result:raise ValueError('Refuse to replace locked source register')
    dump(path,result)
    return result


def load_registered(root=ROOT):
    manifest=json.loads((root/'research/oos-year-sources.json').read_text())
    parts=[]
    for item in manifest['warmup_sources']+manifest['sources']:
        p=root/item['relative_private_path']
        if sha(p)!=item['sha256']:raise ValueError('Source hash mismatch: '+item['filename'])
        b=load_csv(p,item['contract'])
        if item in manifest['warmup_sources']:b=b[b.trade_date.le('2025-09-30')]
        parts.append(b)
    full=combine(parts,'2024-12-30',END)
    return full,manifest,dict(source_rows=sum(map(len,parts)),reconciled_contract_bars=len(full),
        identical_overlap_rows=sum(map(len,parts))-len(full),conflicting_overlaps=0)


def schedule_for(full,calendar,root=ROOT):
    prior=json.loads((root/'research/holdout-protocol.json').read_text())
    schedule=[Activation('NQH25','2024-12-30'),Activation('NQM25','2025-03-19')]
    schedule += [Activation(r['to'],r['effective_session']) for r in prior['rollovers']]
    rolls=[]
    for old,new,cutoff in [('NQZ25','NQH26','2025-12-18'),('NQH26','NQM26','2026-03-19'),
                            ('NQM26','NQU26','2026-06-17'),('NQU26','NQZ26','2026-09-17')]:
        r=determine_roll(full,old,new,calendar,cutoff)
        truncated=full[full.trade_date.le(r['decision_session'])]
        if determine_roll(truncated,old,new,calendar,r['decision_session'])!=r:raise ValueError('Future roll dependency')
        expected=calendar.grid(r['decision_session'])
        r['decision_missing_by_contract']={c:len(expected.difference(full[full.contract.eq(c)&full.trade_date.eq(r['decision_session'])].index)) for c in [old,new]}
        r['future_truncation_verified']=True
        r['volume_availability']='Observed vendor volumes assumed available by next18NY; not certified publication vintages'
        rolls.append(r);schedule.append(Activation(new,r['effective_session']))
    return schedule,rolls


def quality_rows(active,calendar):
    frames=[]
    for contract,g in active.groupby('contract'):
        a=max(START,g.trade_date.min());b=min(END,g.trade_date.max())
        if a<=b:frames.extend(dict(r,contract=contract) for r in audit_contract(g,calendar,a,b))
    byday={r['day']:r for r in frames}
    rows=[]
    for day in pd.bdate_range(START,END).strftime('%Y-%m-%d'):
        expected=calendar.grid(day)
        if not len(expected):continue
        g=active[active.trade_date.eq(day)]
        r=byday.get(day,dict(day=day,bars=0,expected=len(expected),unresolved_missing=len(expected),
            unexpected=0,standard_clean=False,noon_prefix_complete=False,
            missing_utc=[t.isoformat() for t in expected],contract=None))
        raw_missing=expected.difference(g.index)
        r['missing_including_documented_outage']=len(raw_missing)
        r['documented_outage_minutes']=len(raw_missing)-r['unresolved_missing']
        r['calendar_adjusted_clean']=not len(raw_missing) and r['unexpected']==0
        r['special_session']=day in calendar.registry['closes_ny']
        rows.append(r)
    return rows


def contamination_scan(root=ROOT):
    inspected=[];hits=[]
    # Read dates ONLY, never a future outcome column. Known research artifacts,
    # not an exhaustive filesystem/remote execution log certification.
    for p in sorted((root/'artifacts').glob('**/*trades*.csv')):
        columns=pd.read_csv(p,nrows=0).columns
        if 'trade_date' not in columns:continue
        dates=pd.read_csv(p,usecols=['trade_date']).trade_date.dropna().astype(str)
        entry=dict(path=str(p.relative_to(root)),sha256=sha(p),rows=len(dates),
                   max_date=dates.max() if len(dates) else None)
        inspected.append(entry)
        if dates.between(START,END).any():hits.append(entry['path'])
    return dict(status='CONTAMINATED' if hits else 'NO_FUTURE_TRADE_LEDGER_FOUND_LIMITED_EVIDENCE',
        future_trade_ledgers=hits,inspected=inspected,
        limitation='Local artifact date-column scan only. Not proof of never-execution, human blindness, absent deleted files or remote activity.')


def run(root=ROOT,publish=False):
    freeze=verify(root)
    full,manifest,reconciliation=load_registered(root)
    calendar=Calendar(json.loads((root/'research/oos-year-calendar.json').read_text()))
    schedule,rolls=schedule_for(full,calendar,root)
    # Only these low-level indicator prerequisites; no build_features/hypotheses.
    with forbid_scoring():
        state,daily,_=indicator_state(full,schedule)
    active=state[state.trade_date.between(START,END)]
    quality=quality_rows(active,calendar)
    with forbid_scoring():
        eligibility=technical_eligibility(state,calendar,START,END)
    contamination=contamination_scan(root)
    out=root/'artifacts/oos-year-readiness'
    out.mkdir(parents=True,exist_ok=True)
    eligibility.to_csv(out/'eligibility.csv',index=False)
    dump(out/'quality.json',quality);dump(out/'roll-ledger.json',rolls)
    dump(out/'contamination-audit.json',contamination)
    # ATR values are private prerequisite evidence, not public market series.
    daily.to_csv(out/'indicator-readiness.csv',index=False)
    counts={s:int(eligibility.loc[eligibility.strategy.eq(s),'eligible'].sum()) for s in STRATEGIES}
    exclusions={s:Counter(x for reasons in eligibility.loc[eligibility.strategy.eq(s),'reasons'] for x in reasons) for s in STRATEGIES}
    expected_weekdays=len(pd.bdate_range(START,END))
    result=dict(classification='PRERELEASE_QUALITY_AND_TECHNICAL_ELIGIBILITY_ONLY',
        status='AWAITING_EXPLICIT_RELEASE_NOT_SCORED',period=[START,END],
        source_files=len(manifest['sources']),warmup_source_files=len(manifest['warmup_sources']),
        intake_source_rows_before_overlap=sum(item['rows'] for item in manifest['sources']),
        new_period_reconciled_contract_bars=int(full.trade_date.between(START,END).sum()),
        hashes=dict(sources=sha(root/'research/oos-year-sources.json'),calendar=sha(root/'research/oos-year-calendar.json'),
            frozen_protocol=sha(root/'research/vnext-future-oos-protocol.json'),
            private_roll_ledger=sha(out/'roll-ledger.json'),private_eligibility=sha(out/'eligibility.csv')),
        reconciliation=reconciliation,active_unique_bars=len(active),weekday_dates=expected_weekdays,
        closed_civil_dates=[d for d,v in calendar.registry['closes_ny'].items() if v is None and START<=d<=END],
        scheduled_sessions=len(quality),observed_sessions=int(active.trade_date.nunique()),
        regular_full_clean_days=sum(r['standard_clean'] for r in quality),
        calendar_adjusted_clean_days=sum(r['calendar_adjusted_clean'] for r in quality),
        special_sessions=sum(r['special_session'] for r in quality),
        quality_flagged_days=sum(not r['calendar_adjusted_clean'] for r in quality),
        documented_outage_minutes=sum(r['documented_outage_minutes'] for r in quality),
        unresolved_missing_minutes=sum(r['unresolved_missing'] for r in quality),
        missing_full_sessions=[r['day'] for r in quality if not r['bars']],
        unexpected_minutes=sum(r['unexpected'] for r in quality),
        complete_noon_prefix_days=sum(r['noon_prefix_complete'] for r in quality),
        runtime_scoring_tripwire_passed=True,
        technical_eligible_days=counts,exclusion_reasons=exclusions,
        ineligible_dates={s:eligibility.loc[eligibility.strategy.eq(s)&~eligibility.eligible,'trade_date'].tolist() for s in STRATEGIES},
        quality_exceptions=[{k:v for k,v in r.items() if k!='missing_utc'} for r in quality if not r['standard_clean']],
        unresolved_missing_utc=[t for r in quality for t in r['missing_utc']],
        rollovers=[{k:v for k,v in r.items() if k not in ['old_volume','new_volume','spread_points']} for r in rolls],
        contamination_status=contamination['status'],
        calendar_evidence_limit=calendar.registry['evidence_limit'],
        license_status=manifest['license_status'],scoring_authorized=False,signals_computed=False,
        future_intraday_strategy_features_computed=False,readiness_ATR_and_volume_only=True,
        future_PnL_computed=False,backtest_run=False,freeze=freeze,
        gates=['Explicit human release required for Step4',
               'Limited local non-use evidence: independent never-use certification unavailable',
               'Vendor publication vintages and usage rights not independently certified; no raw/public trade publication'],
        definitions=dict(regular_clean='Exact ordinary18NY-17NY1380-minute grid; no early-close days.',
            calendar_clean='Every scheduled minute present, special closes allowed; documented outage still not clean.',
            eligibility='Frozen primary all-view: priorATR>0 + exact18NY-noon prefix; ORB also nonnull prior same-clock volume09:30-11:00. Not trade count or edge evidence. No imputation.'))
    verify(root)
    dump(out/'summary.json',result)
    if publish:
        dump(root/'public/data/research-oos-year-readiness.json',result)
        dump(root/'research/oos-year-rollovers.json',dict(rollovers=result['rollovers'],private_evidence_sha256=result['hashes']['private_roll_ledger']))
        dump(root/'public/data/research-oos-year-sources.json',manifest)
        dump(root/'public/data/research-oos-year-calendar.json',calendar.registry)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--register',action='store_true');p.add_argument('--publish',action='store_true')
    args=p.parse_args()
    if args.register:register()
    result=run(publish=args.publish)
    print(json.dumps({k:result[k] for k in ['status','source_files','active_unique_bars','scheduled_sessions',
        'regular_full_clean_days','calendar_adjusted_clean_days','unresolved_missing_minutes','technical_eligible_days','signals_computed']},indent=2))


if __name__=='__main__':main()
