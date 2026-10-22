"""Close morning research and publish verified allowlisted aggregates only."""
import json

from scripts.morning_recovery_anatomy import ROOT,dump,verify as verify_anatomy
from scripts.morning_recovery_precision import verify as verify_precision
from scripts.register_afternoon_candidate_v2 import verify as verify_candidate
from scripts.publish_afternoon_falsification import publish as refresh_falsification_manifest
from scripts.oos_preparation.adapter import sha

PUBLIC=ROOT/'public/data'
CLOSED='CLOSED_DESCRIPTIVE_NOT_CANDIDATE'
CANDIDATE='CANDIDATE_SPEC_FROZEN_INDEPENDENT_TEST_NOT_RELEASED'


def verify_report_manifest(name):
    manifest=json.loads((ROOT/'research'/name).read_text())
    for path,digest in manifest['files_sha256'].items():
        if sha(ROOT/path)!=digest:
            raise ValueError('Frozen report changed: '+path)


def publish():
    v1=verify_candidate();a=verify_anatomy();p=verify_precision()
    for name in ('morning-recovery-anatomy-report-manifest.json','morning-recovery-precision-report-manifest.json'):
        verify_report_manifest(name)
    copies={
        'docs/AFTERNOON_CANDIDATE_PREREGISTRATION_V2.md':'AFTERNOON_CANDIDATE_PREREGISTRATION_V2.md',
        'docs/MORNING_RECOVERY_ANATOMY.md':'MORNING_RECOVERY_ANATOMY.md',
        'docs/MORNING_RECOVERY_PRECISION.md':'MORNING_RECOVERY_PRECISION.md',
        'research/afternoon-candidate-v2.json':'research-afternoon-candidate-v2.json',
        'research/morning-recovery-anatomy-results.json':'research-morning-anatomy.json',
        'research/morning-recovery-precision-results.json':'research-morning-precision.json'}
    for stem in ('tables','timing','differences'):
        copies[f'research/morning-recovery-anatomy-{stem}.csv']=f'research-morning-anatomy.{stem}.csv'
    for stem in ('intervals','quarters','excursions'):
        copies[f'research/morning-recovery-precision-{stem}.csv']=f'research-morning-precision.{stem}.csv'
    for source,target in copies.items():
        (PUBLIC/target).write_bytes((ROOT/source).read_bytes())
    closure=dict(status='RESEARCH_ROUND_CLOSED_ONE_FORMAL_CANDIDATE',
        active_formal_candidate_ids=['NQ-1430-FIXED-UP-1500-V2'],
        candidate_status=CANDIDATE,future_independent_test_released=False,
        candidate_report='/data/AFTERNOON_CANDIDATE_PREREGISTRATION_V2.md',
        morning_status=CLOSED,
        morning_reports=['/data/MORNING_RECOVERY_ANATOMY.md','/data/MORNING_RECOVERY_PRECISION.md'],
        closure_reason='Onderzoeksbesluit: de ochtendverkenning wordt afgesloten als beschrijvend rapport wegens beperkte precisie en brede excursies bij N=29. Geen kandidaat-model, reddingsfilter of verdere parameter-tuning. Geen universeel bewijs dat elk ochtendherstelmechanisme afwezig is.',
        interpretation='Alle bestaande435 dagen blijven ontdekkingsdata. V2 is uitsluitend een bevroren kandidaat voor nog niet vrijgegeven onafhankelijke toetsing; geen gevalideerde trading edge.',
        historical_publication_note='De rapporten zijn byte-identieke historische momentopnamen. Tekst over uitsluitend lokale publicatie dateert van vóór de latere expliciete publicatievrijgave.',
        verification=dict(candidate=v1,anatomy=a,precision=p,new_afternoon_runs=0,
            new_strategy_runs=0,raw_data_published=False))
    target=ROOT/'research/research-round-closure.json'
    if target.exists() and json.loads(target.read_text())!=closure:
        raise ValueError('Closure decision replacement refused')
    dump(target,closure);dump(PUBLIC/'research-round-closure.json',closure)
    register_path=PUBLIC/'research-register.json'
    register=json.loads(register_path.read_text())
    specifications=[
        ('NQ-1430-FIXED-UP-1500-V2','15:00-kandidaat v2: twee parallelle primaire horizons',CANDIDATE,
            'AFTERNOON_CANDIDATE_PREREGISTRATION_V2.md','research-afternoon-candidate-v2.json',True),
        ('NQ-MORNING-ANATOMY','Ochtendherstel: causale vensters en ONL-timing',CLOSED,
            'MORNING_RECOVERY_ANATOMY.md','research-morning-anatomy.json',False),
        ('NQ-MORNING-PRECISION','Ochtendherstel: onzekerheid, kwartalen en excursies',CLOSED,
            'MORNING_RECOVERY_PRECISION.md','research-morning-precision.json',False)]
    for identifier,title,status,report,aggregate,formal in specifications:
        entry=dict(id=identifier,title=title,status=status,dashboard='/research/nq#research-round',
            report='/data/'+report,aggregates='/data/'+aggregate,report_sha256=sha(PUBLIC/report),
            independent_validation=False,formal_candidate=formal)
        previous=[r for r in register['entries'] if r['id']==identifier]
        if previous and previous!=[entry]:
            raise ValueError('Conflicting public entry: '+identifier)
        if not previous:
            register['entries'].append(entry)
    register['active_formal_candidate_ids']=closure['active_formal_candidate_ids']
    register['future_independent_test_released']=False
    dump(register_path,register)
    # The shared navigation register intentionally grows. Refresh only its
    # publication index hash through the existing deterministic exporter.
    # Old frozen reports, results and protocols are not altered.
    refresh_falsification_manifest()
    files=[PUBLIC/name for name in copies.values()]+[PUBLIC/'research-round-closure.json',register_path]
    manifest=dict(status=closure['status'],report_copies_byte_identical=True,
        shared_register_updated=True,old_falsification_index_hash_refreshed=True,
        new_afternoon_runs=0,new_strategy_runs=0,raw_data_published=False,
        files_sha256={str(path.relative_to(ROOT)):sha(path) for path in files})
    dump(ROOT/'research/research-round-publication.json',manifest)
    print(json.dumps(dict(status=closure['status'],public_files=len(files),raw_data_published=False),indent=2))


if __name__=='__main__':
    publish()
