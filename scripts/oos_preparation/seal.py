"""Publish a content-addressed preparation package, never authorize scoring."""
import json
import subprocess
from pathlib import Path

from .adapter import sha
from .year import dump
from scripts.verify_research_freeze import verify

ROOT=Path(__file__).resolve().parents[2]


def seal(root=ROOT):
    verify(root)
    result=json.loads((root/'public/data/research-oos-year-readiness.json').read_text())
    parity=json.loads((root/'research/oos-year-historical-parity.json').read_text())
    assert parity['status']=='PASS_HISTORICAL_FULL_LEDGER_BYTE_PARITY'
    assert all(sha(root/name)==digest for name,digest in parity['implementation_sha256'].items())
    assert not result['signals_computed'] and not result['future_PnL_computed']
    prereg=json.loads((root/'research/vnext-future-oos-protocol.json').read_text())
    assert prereg['status']=='LOCKED_RULES_NOT_RUN' and prereg['cost_rt_usd']==24.5
    names=['research/oos-year-sources.json','research/oos-year-calendar.json','research/oos-year-rollovers.json',
        'research/oos-year-release-checks.json',
        'research/oos-year-historical-parity.json','research/vnext-future-oos-protocol.json',
        'public/data/research-oos-year-readiness.json','public/data/research-oos-year-sources.json',
        'public/data/research-oos-year-calendar.json','scripts/verify-oos-year','tests/test_oos_year.py',
        'package.json','app/research/nq/DataCollectionUpdate.tsx','app/research/nq/FrozenResearch.tsx','.vercelignore']
    names += [str(p.relative_to(root)) for p in sorted((root/'scripts/oos_preparation').glob('*.py'))]
    package=dict(classification='PRE_SCORING_RELEASE_GATE_NOT_SCORING_PERMISSION',status='AWAITING_EXPLICIT_RELEASE',
        preparation_base_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
        version_anchor='Containing Git commit plus exact per-fileSHA256; no self-referential commit hash',
        files_sha256={name:sha(root/name) for name in names},
        existing_frozen_protocol_sha256=sha(root/'research/vnext-future-oos-protocol.json'),
        primary_strategy=prereg['primary_strategy'],reference_strategies_descriptive_only=prereg['reference_strategies_descriptive_only'],
        period=prereg['test_period'],pass_rule=prereg['pass_rule'],inference=prereg['inference'],
        cost_rt_usd=prereg['cost_rt_usd'],historical_parity=parity,
        release_checks=json.loads((root/'research/oos-year-release-checks.json').read_text()),
        final_technical_eligible_days=result['technical_eligible_days'],
        future_scoring_authorized=False,future_signal_calls=0,future_PnL_calls=0,
        known_limits=result['gates'],
        scope='Step1quality, Step2historical-only replay and prerequisite state, Step3publication. No Step4. No new thresholds or strategies. New preparation package, not a revision of frozen baseline.')
    dump(root/'research/oos-year-preregistration.json',package)
    dump(root/'public/data/research-oos-year-preregistration.json',package)
    lines=['# Jaar-holdout: voorbereiding afgerond, scoring geblokkeerd','',
        'Periode: 1 oktober 2025–30 september 2026. Alleen stappen1–3. Geen toekomstige signalen, entries, trades of P&L berekend. ATR en volume uitsluitend als technische voorwaarden voor eligibility.','',
        '## Datakwaliteit','',
        '| Maatstaf | Aantal |','|---|---:|',
        f"| Bronbestanden nieuwe periode | {result['source_files']} |",
        f"| Historische opwarmbestanden | {result['warmup_source_files']} |",
        f"| Weekdagdatums / geplande sessies | {result['weekday_dates']} / {result['scheduled_sessions']} |",
        f"| Actieve unieke minuutbars | {result['active_unique_bars']} |",
        f"| Schone normale dagen | {result['regular_full_clean_days']} |",
        f"| Kalenderconform complete dagen inclusief vroege sluitingen | {result['calendar_adjusted_clean_days']} |",
        f"| Dagen met ontbrekende minuten | {result['quality_flagged_days']} |",
        f"| Gedocumenteerde storing, ontbrekende minuten | {result['documented_outage_minutes']} |",
        f"| Onverklaarde ontbrekende minuten | {result['unresolved_missing_minutes']} |",
        f"| Volledig ontbrekende sessies / onverwachte minuten | {len(result['missing_full_sessions'])} / {result['unexpected_minutes']} |",'',
        'Kerst2025 en Nieuwjaar2026 zijn de twee gesloten civiele dagen. Schone normale dag = exact1380minuten. Kalenderconform schoon = alle geplande minuten aanwezig, vroege sluiting toegestaan, maar geen ontbrekende storingsminuten. Er is geen imputatie.','',
        '## Technische eligibility','',
        '| Model | Dagen | Rol |','|---|---:|---|']
    for s,count in result['technical_eligible_days'].items():lines.append(f"| {s} | {count} | {'Enige primaire hypothese' if s=='B_ORB15' else 'Uitsluitend beschrijvende referentie'} |")
    lines += ['',result['definitions']['eligibility'],'',
        'Een dag met alleen een gat na12:00 kan eligible blijven. Dit verklaart dat249 groter is dan248 kalenderconform complete dagen. Geen ATR-opwarmuitval na rollovers. De tien uitgesloten datums zijn voor alle modellen gelijk. ORB heeft één aanvullende volumegate-fout op een reeds uitgesloten dag; redenen mogen niet worden opgeteld.','',
        ', '.join(result['ineligible_dates']['B_ORB15']), '',
        '## Uitzonderingen per dag','',
        '| Datum | Geobserveerd / verwacht na storingsattributie | Onverklaard ontbrekend | Storing | Prefix tot12:00 volledig |',
        '|---|---:|---:|---:|---|']
    for r in result['quality_exceptions']:
        lines.append(f"| {r['day']} | {r['bars']} / {r['expected']} | {r['unresolved_missing']} | {r['documented_outage_minutes']} | {'Ja' if r['noon_prefix_complete'] else 'Nee'} |")
    lines += ['', 'Good Friday2026 sluit09:15NY en kan het vereiste18:00–12:00-venster niet vervullen. Thanksgiving en andere vroege sluitingen worden niet automatisch corrupt genoemd. Storingmaskering geldt alleen voor kwaliteitstoeschrijving, niet voor eligibility.','',
        '## Objectieve rollovers','',
        '| Contracten | Volumebesluit | Eerste actieve handelsdag |','|---|---|---|']
    for r in result['rollovers']:lines.append(f"| {r['from']} naar {r['to']} | {r['decision_session']} | {r['effective_session']} |")
    lines += ['', 'Vaste eerste grensgekwalificeerde crossover, incoming waargenomen volume strikt groter dan outgoing; activeren18:00NY op de voorafgaande civiele kalenderdag. Geen kalenderfallback, geen intraday-overgang. Alle vier besluiten onveranderd bij verwijderen van toekomstige dagen. Op16maart ontbreekt één minuut in uitgaand H26; de vooraf vastgelegde boundary-regel eist geen volledige interne minutendekking. Geen claim van officiële CME-totalen.','',
        'De spread gebruikt uitsluitend de laatste gezamenlijke voltooide15:59NY-close vóór activering. Tijdstempels zijn publiek, prijzen en volumetotalen blijven privé met een publieke hash van de volledige ledger. Beide US-DST-overgangen zijn geautomatiseerd getest.','',
        '## Bewijs uitvoeringsroute','',
        'De nieuwe route selecteert actieve contracten en hergebruikt de bevroren continuousATR- en volumehistorie. Alleen voor de historische replay worden intraday features en signalen uitgevoerd. De guard weigert elke signaalroute met een datum na30september2025 vóór featureconstructie. Een runtime-tripwire blokkeert build_features/hypotheses/simulate/baseline/metrics/bootstrap tijdens de jaarvoorbereiding.','',
        'Alle30 historische bronnen opnieuw geladen. De nieuwe route reproduceert435 historische trades en780 eligibility-regels byte-identiek aan de SHA256-verankerde private vNext-ledgers. Alle vier modellen blijven159 historisch eligible dagen houden. Alle73 bevroren bestanden zijn byte-identiek. Het toekomstige jaar is hierbij niet gescoord.','',
        '## Reproductie','',
        '- `npm run verify:oos-year`: private geregistreerde bronnen en kalender opnieuw controleren, ATR-/volumevoorwaarden en eligibility opnieuw bepalen. Geen signalen.',
        '- `npm run verify:oos-year-parity`: uitsluitend2024-12-30–2025-09-30, volledige historische-ledgerpariteit.',
        '- `.venv/bin/python -m pytest -q`: synthetische regressies en integriteitscontroles; CI heeft geen rawdata nodig.',
        '- `npm run verify:freeze`:73bestanden bytecontrole.',
        '- `.venv/bin/python -m scripts.oos_preparation.seal --verify`: inhoudsadres van het preregistratie-pakket controleren.',
        '- Rawdata staat in genegeerd `data/raw/`; private dagledger, exacte ontbrekende timestamps, indicatorstaat en roll-spreads in genegeerd `artifacts/oos-year-readiness/`.', '',
        '## Grenzen en vrijgavemoment','',
        'Geen toekomstige trade-ledger aangetroffen bij controle van de datumkolommen in lokale onderzoeksartefacten. Onvolledige logs bewijzen nooit absoluut niet-gebruik. Calendars zijn productspecifieke broker-/leveranciersreconstructies, geen ondertekend historisch CME-certificaat. Leveranciersrechten en publicatievintages blijven niet onafhankelijk gecertificeerd. Geen ruwe data of individuele trades gepubliceerd. Niets gekocht.','',
        'De bestaande primaire ORB15-hypothese, $24,50RT, vaste periode, bootstrap en gezamenlijke slaagcriteria blijven onveranderd. Referenties mogen niet achteraf worden gepromoveerd. Een eventuele mislukking wordt niet gered door deelperiode, clean-view, extra filter of gecombineerde historie.','',
        '**STOP: wachten op expliciete vrijgave van Stap4, met kennis van de genoemde beperkingen. Dit pakket geeft zelf geen scoringtoestemming en bevat geen holdout-oordeel.**','',
        '## Kalenderbronnen','']
    calendar=json.loads((root/'research/oos-year-calendar.json').read_text())
    lines += ['- '+url for url in calendar['sources']]
    text='\n'.join(lines)+'\n'
    (root/'docs/OOS_YEAR_READINESS_2026-10-21.md').write_text(text)
    (root/'public/data/research-oos-year-readiness.md').write_text(text)
    print('Sealed preparation package; future scoring remains unauthorized.')


def check(root=ROOT):
    verify(root)
    package=json.loads((root/'research/oos-year-preregistration.json').read_text())
    assert package==json.loads((root/'public/data/research-oos-year-preregistration.json').read_text())
    for name,digest in package['files_sha256'].items():
        if sha(root/name)!=digest:raise ValueError('Preparation package changed: '+name)
    assert not package['future_scoring_authorized']
    print('Preparation package hashes verified; no scoring permission.')


if __name__=='__main__':
    import sys
    check() if '--verify' in sys.argv else seal()
