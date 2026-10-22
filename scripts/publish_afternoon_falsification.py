"""Publish allowlisted aggregates only; never recalculate the closed experiment."""
import json

from scripts.afternoon_falsification import ROOT, dump
from scripts.report_afternoon_falsification import corrected_result
from scripts.oos_preparation.adapter import sha

PUBLIC = ROOT / 'public/data'
STATUS = 'INTERESTING_OBSERVATION_INDEPENDENTLY_UNCONFIRMED'


def publish():
    data, verification = corrected_result()
    manifest = json.loads((ROOT / 'research/afternoon-falsification-report-manifest.json').read_text())
    for name, digest in manifest['files_sha256'].items():
        if sha(ROOT / name) != digest:
            raise ValueError('Report evidence drift: ' + name)
    if data['decision_after_time_audit_correction'] != STATUS:
        raise ValueError('Unexpected decision; publication requires review')
    # No per-day prices, raw arrays, source paths or private ledgers are exported.
    aggregate = dict(status=STATUS, title='15:00-effect: vooraf vastgelegde falsificatie',
        analysis_type='EXPLORATORY_ON_PREVIOUSLY_CONSUMED_DATA_NOT_HOLDOUT',
        tables=data['tables'], tests=data['tests'], concentration=data['concentration'],
        leave_quarters=data['leave_quarters'], transitions=data['transitions'],
        integrity=data['integrity'], verification=verification,
        protocol_sha256=data['protocol_sha256'],
        time_audit_correction=dict(reason=data['time_audit_correction']['reason'],
            legacy_flagged_days=data['time_audit_correction']['legacy_flagged_days'],
            corrected_flagged_days=data['integrity']['flagged_days'],
            statistical_tables_or_pvalues_changed=False),
        limitations=['Geen onafhankelijke tweede bron, uitvoerbaarheidsbewijs of gevalideerde trading edge.',
            'Holm24 dekt alleen deze vervolgmeting, niet alle eerdere projectbrede selecties.',
            'Nominale intervallen op punten; primaire tweezijdige toetsen op log-basispunten.',
            'Het oorspronkelijke rapport blijft byte-identiek, inclusief historische lokale-publicatienotitie. Publicatie is later expliciet vrijgegeven.'])
    dump(PUBLIC / 'research-afternoon-falsification.json', aggregate)
    copies = {'docs/AFTERNOON_FALSIFICATION_REPORT.md': 'AFTERNOON_FALSIFICATION_REPORT.md'}
    copies.update({f'research/afternoon-falsification-{stem}.csv': f'research-afternoon-falsification.{stem}.csv'
        for stem in ('rows', 'tests', 'leave-quarters', 'transitions')})
    for source, target in copies.items():
        # Exact artifact copy, not an edited or selectively shortened report.
        (PUBLIC / target).write_bytes((ROOT / source).read_bytes())
    entry = dict(id='NQ-AFTERNOON-FALSIFICATION', title=aggregate['title'], status=STATUS,
        dashboard='/research/nq#afternoon-falsification',
        report='/data/AFTERNOON_FALSIFICATION_REPORT.md',
        aggregates='/data/research-afternoon-falsification.json',
        report_sha256=sha(PUBLIC / 'AFTERNOON_FALSIFICATION_REPORT.md'),
        protocol_sha256=data['protocol_sha256'], complete_RTH_days=435,
        formal_tests=24, independent_validation=False)
    registry_path = PUBLIC / 'research-register.json'
    registry = json.loads(registry_path.read_text()) if registry_path.exists() else dict(
        schema_version=1, scope='Public aggregate research publications; separate from private experiment ledgers.', entries=[])
    existing = [r for r in registry['entries'] if r['id'] == entry['id']]
    if existing and existing != [entry]:
        raise ValueError('Conflicting public research registration')
    if not existing:
        registry['entries'].append(entry)
    dump(registry_path, registry)
    files = [PUBLIC / 'research-afternoon-falsification.json', registry_path,
             *[PUBLIC / name for name in copies.values()]]
    dump(ROOT / 'research/afternoon-falsification-publication.json', dict(
        status=STATUS, archived_files_verified=verification['protected_archive_files'],
        report_unchanged=True, new_strategy_runs=0,
        files_sha256={str(p.relative_to(ROOT)): sha(p) for p in files}))
    print(json.dumps(dict(status=STATUS, public_files=len(files), raw_data_published=False), indent=2))


if __name__ == '__main__':
    publish()
