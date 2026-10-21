"""Publish aggregate tables and source-linked audit; never run a strategy."""
import ast
import json
from pathlib import Path

import pandas as pd

from scripts.archive_experiments import verify_archive
from scripts.oos_preparation.adapter import sha
from scripts.oos_preparation.year import dump

ROOT=Path(__file__).resolve().parents[1]
NAMES={'B_ORB15':'ORB15','B_ORB5':'ORB5','A_London_sweep':'London Sweep','C_VWAP_extreme':'VWAP Extreme'}


def f(x,n=3):
    return 'n.v.t.' if x is None else f'{x:,.{n}f}'.replace(',','#').replace('.',',').replace('#','.')


def ci(row,stem='mean_'):
    return '['+f(row.get(stem+'ci_low'))+'; '+f(row.get(stem+'ci_high'))+']'


def table(lines,headers,rows):
    lines += ['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']
    lines += ['| '+' | '.join(str(x) for x in row)+' |' for row in rows]
    lines += ['']


def publish():
    archive=verify_archive()
    a=json.loads((ROOT/'public/data/research-execution-audit.json').read_text())
    d=json.loads((ROOT/'public/data/research-raw-market.json').read_text())
    p=json.loads((ROOT/'research/raw-market-protocol.json').read_text())
    if d['protocol_sha256']!=sha(ROOT/'research/raw-market-protocol.json'):raise ValueError('Protocol changed')
    lines=['# Afgesloten modellen, uitvoeringsaudit en ruw NQ-marktgedrag','',
        '## 1. Archivering','',
        '**ORB5, ORB15, London Sweep en VWAP Extreme: `ARCHIVED_NOT_VALIDATED`.** Dit geldt voor Baseline v0.9, vNext159 en de vaste jaar-holdout. Geen tuning, reddingsfilters of hergebruik als kandidaat. Historische reproductie en uitvoeringstoetsen blijven toegestaan. Het eerdere `HOLDOUT_FAILED` is niet overschreven. Niet-gevalideerd betekent niet dat iedere denkbare variant universeel weerlegd is.','',
        f"Archiefregistratie beschermt {archive['protected_files']} bestanden op SHA-256. De bestaande 73 bevroren bestanden, het voorbereidingspakket, de jaarresultaten en de strategiecode blijven ongewijzigd.",'',
        '## 2. Onafhankelijke controle van de meetlat','',
        'Nieuwe code-inspectie en handmatig afgeleide synthetische voorbeelden, los van de bestaande reproductietest. Geen onafhankelijke tick-/brokerfill-certificatie en geen tweede volledige simulator. Er zijn geen nieuwe strategie-signalen op echte data berekend.','',
        '### Exacte timing en ordertypen','']
    table(lines,['Aspect','Werkelijke code-aanname'],[
        ['Signaal','Afgeronde minuutbar t; timestamp is het begin van die bar. Signaal van 09:45 is pas om 09:46 bekend.'],
        ['Entry','Ruwe open van exact t+1. Het signaal van de 09:45-bar wordt dus op de 09:46-open gevuld. Frictie wordt apart afgetrokken, niet in de ledgerprijs verwerkt.'],
        ['Stop-entry / limit-entry','Niet geïmplementeerd. Alle vier modellen gebruiken next-open market fills, ook ORB en VWAP Extreme. Geen resting breakout-stop of VWAP-limit-entry.'],
        ['Entry en stop in dezelfde minuut','Entry op baropen, bracket direct actief. Deze bar wordt inclusief high/low direct gescand; ook direct verlies is mogelijk.'],
        ['Stop en target in dezelfde minuut','Stop wint. Stop-long: min(stop, baropen); stop-short: max(stop, baropen). Ongunstige gap dus slechter dan stopniveau.'],
        ['Target','Een touch van high/low telt als fill op exact target. Gunstige gaps krijgen geen betere prijs. Werkelijke queue/bid/ask/tickvolgorde ontbreken.'],
        ['Tijdsluiting','Close van de bar 11:59–12:00 NY. exit_bar_utc verwijst naar 11:59 als barlabel, niet naar bewezen executietijd.'],
        ['Afronding','SL-afstand wordt naar beneden op 0,25 afgerond, vaste TP-afstand naar boven. Dichtere stops zijn niet onder alle omstandigheden conservatief. VWAP-target wordt bij long omlaag en bij short omhoog afgerond.'],
        ['VWAP','Per onverschoven contract/handelsdag vanaf 18:00 NY: cumulatief Σ[Volume × (High+Low+Close)/3] / ΣVolume. Gewogen populatie-SD van dezelfde HLC3-proxy. Geen transactie-VWAP.'],
        ['Beschikbaarheid VWAP','Inclusief de actuele afgeronde bar; pas bekend op timestamp+1min. Bij ontbrekende prefix rekent de primitieve functie vanaf de eerste waargenomen bar; de eligibility-gate blokkeert incomplete 18:00–12:00-prefixen.'],
        ['Basiskosten','$24,50RT = 2 ticks per kant ($20) + $4,50 commissie. 1 tick = 0,25 NQ-punt = $5.'],
        ['Extra stopfrictie','+1 tick per stop-fill: +$5 per stop-exit, dus $29,50RT op stoptrades. +2 ticks: +$10, dus $34,50RT. Overige exits blijven $24,50. Er zijn geen stop-entries om extra te belasten.']])
    code=ROOT/'scripts/reproduce_research/engine.py';tree=ast.parse(code.read_text())
    nodes={n.name:n.lineno for n in tree.body if isinstance(n,ast.FunctionDef)}
    lines += ['Broncode (vastgelegde commit, geen wijzigingen): '+', '.join(
        f'[{name}](https://github.com/ianvdbrink3/QUANTT/blob/9c890b1aa752f6941768c50c55f35ee779dbe903/scripts/reproduce_research/engine.py#L{nodes[name]})'
        for name in ['build_features','simulate','hypotheses'])+'.','',
        '### Wat is conservatief?','']+['- '+s for s in a['conservative']]+['',
        '### Blinde vlekken en mogelijke optimistische aannames','']+['- '+s for s in a['blind_spots_or_optimism']]+['',
        'London kan sweep, terugkeer en VWAP-kruising uit dezelfde afgeronde minuut afleiden; de tickvolgorde daarvan is niet bewezen. De entry vindt wel pas daarna plaats. ORB vereist een afgeronde close buiten de range; een eerdere aanraking van de rangegrens is geen entry.','',
        '### Feitelijke conflicten in de bestaande ledgers','']
    table(lines,['Periode','Model','Trades','Stop-exits','Stop op entrybar','Target op entrybar','SL+TP in één bar'],[
        [r['period'],NAMES[r['model']],r['trades'],r['stop_fills'],r['stop_on_entry_bar'],r['target_on_entry_bar'],r['both_stop_target_bars']] for r in a['models']])
    lines += ['Geen SL+TP-conflicten in deze ledger bewijst niet dat de simulator alle mogelijke liveconflicten correct behandelt. Synthetische controles behandelen deze grensgevallen apart.','',
              '### Alleen rekenkundige extra stopfrictie op ongewijzigde trades','']
    table(lines,['Periode','Model','Extra ticks/stop','Extra USD totaal','Netto NQ-punten','Netto USD','PF'],[
        [r['period'],NAMES[r['model']],s['extra_ticks_per_stop_fill'],f(s['extra_cost_usd'],2),f(s['net_points']),f(s['net_usd'],2),f(s['profit_factor'])]
        for r in a['models'] for s in r['scenarios']])
    lines += ['Deze gevoeligheid schat geen werkelijke slippageverdeling en wijzigt geen archived P&L. Hogere kosten veranderen hier geen signalen, stopniveaus, exits of intrabar-volgorde.','',
        '## 3. Strategie-vrij ruw marktgedrag','',
        f"Periode: {d['period'][0]}–{d['period'][1]}. {d['source_files']} hash-gecontroleerde bronnen, {d['scheduled_sessions']} geplande sessies, **{d['complete_RTH_and_boundary_days']} complete RTH-sessies** met 09:29-grensclose; {len(d['excluded_days'])} uitgesloten. {d['prior_same_contract_days']} huidige sessies hebben bruikbare vorige-sessiegegevens in hetzelfde contract. Andere aantallen dan strategie-eligible dagen zijn bewust: geen ATR-/volume-opwarmfilter.",'',
        'Geen entries, stops, targets, kosten of modelselectie. Positief/negatief betekent alleen prijsrichting; geen winst/verlies van een uitvoerbare positie. Alle data zijn eerder verbruikt. Dit is verkenning, geen nieuwe validatie.','',
        '### Vooraf vastgelegde meetdefinities','']
    for key in ['session_sample','cross_day','returns','half_hours','intraday_autocorrelation','daily_correlations','events','event_outcome','event_weighting']:
        lines += [f"- **{key}**: {p[key]}"]
    lines += ['', 'Alle rendementen in de inferentietabellen zijn log-basispunten: 10.000 × ln(C1/C0). 1 bp = 0,01% log-rendement. Close-to-close begint bij de vorige minuutclose; de eerste halfuurgrens is dus 09:29-close, niet 09:30-open. RTH-slot = 15:59-minuteclose, bekend om 16:00 NY.','',
        'High-low range is een spreidingsmaat, niet gerealiseerde variantie. Daarom staat daarnaast RV = wortel van de som van gekwadrateerde 1m-logrendementen. Volumeaandeel is ten opzichte van RTH-volume, niet de volledige Globex-dag.','',
        '### Onzekerheid en meervoudig toetsen','',
        '4.000 circular moving-block bootstrapreplicaties, blokken van vijf chronologische geplande sessies, seed 20261022. Hele dagen inclusief alle overlappende events worden gezamenlijk gewogen. Uitgesloten of observatieloze dagen blijven als maskers in de chronologie; ze worden geen fictieve nulrendementen. Intervallen zijn nominale 95%-percentielintervallen, niet simultaan. P-waarden zijn tweezijdig en gecentreerd, (1 + extremere replicaties)/(B_valid + 1), een benaderende exploratieve nulwaardetoets. CI en p zijn niet exact elkaars inversen. De kleinste resolutie is 1/4001.','',
        'Eén globale Holm-familie van **43** toetsen: 13 gemiddelde halfuurrendementen, zes correlaties, twaalf eventgewogen en twaalf daggewogen gemiddelde vervolgrendementen. Niet-berekenbare toetsen blijven met p=1 in de correctie. Geen nulwaardetoets op positief-gedefinieerde high-low range, RV of volumeaandeel, en geen afzonderlijke toetsen op quantielen. Alle toetsen blijven in de export staan.','',
        '### A. Halfuurstructuur: richting, spreiding en volume','']
    hh=[]
    for r in d['half_hours']:
        for name in ['return_bps','return_points','range_bps','range_points','realized_rv_bps','volume_share']:
            x=r[name];hh.append(dict(clock=r['clock'],measure=name,**x))
    table(lines,['NY-start','Maatstaf','N','Gemiddeld','95%CI gemiddelde','Mediaan','95%CI mediaan','P05','P25','P75','P95','p nominaal','p Holm43'],[
        [r['clock'],r['measure'],r['n'],f(r['mean']),ci(r),f(r['median']),ci(r,'median_'),f(r['p05']),f(r['p25']),f(r['p75']),f(r['p95']),f(r.get('p_value'),6),f(r.get('p_holm_global43'),6)] for r in hh])
    lines += ['volume_share is een fractie (0,10 = 10%). Alle halfuren hebben dezelfde 435 complete sessies.','',
              '### B. Autocorrelatie en Overnight versus RTH','']
    table(lines,['Meting','Paren','Dagen','Pearson r','95%CI','p nominaal','p Holm43'],[
        [r['name'],r['pairs'],r['days'],f(r['coefficient'],6),ci(r,''),f(r['p_value'],6),f(r['p_holm_global43'],6)] for r in d['correlations']])
    lines += ['Het aantal intraday paren is geen aantal onafhankelijke waarnemingen. De onzekerheid resamplet dagen, geen losse paren. Daily close-to-close bevat de tussenliggende overnight; de aparte RTH-beweging is open-to-close. Er wordt niet over een ontbrekende vorige geplande sessie heen gesprongen.','',
              '### C. Vervolgrendementen na waargenomen extremen','']
    ev=[]
    for r in d['events']:
        for weighting,key in [('event','event_weighted_bps'),('equal_event_day','equal_event_day_mean_bps')]:
            ev.append(dict(event=r['event'],horizon=r['horizon'],weighting=weighting,**r[key]))
    table(lines,['Event','Horizon','Weging','N','Dagen','Gem. bp','95%CI gem.','Mediaan bp','95%CI med.','P05','P25','P75','P95','Fractie >0','p nominaal','p Holm43'],[
        [r['event'],r['horizon'],r['weighting'],r['n'],r['days'],f(r['mean']),ci(r),f(r['median']),ci(r,'median_'),f(r['p05']),f(r['p25']),f(r['p75']),f(r['p95']),f(r['positive_fraction']),f(r['p_value'],6),f(r['p_holm_global43'],6)] for r in ev])
    lines += ['**Weging is een ander estimand, geen robuustheidsstempel.** Eventgewogen telt ieder recordmoment even zwaar. Daggewogen neemt eerst per dag het gemiddelde van alle bruikbare events; dat gemiddelde is pas achteraf bekend en hangt af van het uiteindelijke aantal events van die dag. Eventrijke trenddagen en eventarme dagen krijgen daardoor een ander relatief gewicht. Geen van beide is een vooraf uitvoerbare positie of winstberekening. De daggewogen record-effecten mogen niet als tradeable mean-reversion-edge worden gepresenteerd.','',
        'De 15m-, 60m- en slotsteekproeven verschillen door rechtscensoring en tijdstip. Het slotvenster heeft variabele lengte. Een eerste PDH/PDL-touch na een gap kan terugkeer uit de andere richting zijn; deze analyse conditioneert niet op de benaderingsrichting. High en low kunnen in dezelfde bar geraakt worden; de volgorde is onbekend. Alle events overlappen mogelijk, maar blijven binnen hun dag geclusterd.','',
        '#### Puntverdelingen en werkelijke vensterlengte','']
    table(lines,['Event','Horizon','N','Gem. punten','Mediaan','P05','P25','P75','P95','Mediane minuten tot endpoint'],[
        [r['event'],r['horizon'],r['points']['n'],f(r['points']['mean']),f(r['points']['median']),f(r['points']['p05']),f(r['points']['p25']),f(r['points']['p75']),f(r['points']['p95']),f(r['minutes_to_endpoint']['median'])] for r in d['events']])
    lines += ['### Uitsluitingsregister','']
    table(lines,['Datum','Contract','RTH-bars werkelijk','RTH-bars gepland','Redenen'],[
        [q['day'],q['contract'],q['observed_RTH'],q['expected_RTH'],', '.join(q['reasons'])] for q in d['excluded_days']])
    lines += ['### Grenzen van deze metingen','',
        p['inference_limit'],'',
        'De kalender is de eerder gecontroleerde productspecifieke reconstructie; geen nieuwe CME-certificatie. Leveranciersvintages, tickvolgorde, gebruiksrechten en echte brokerfills zijn niet onafhankelijk bewezen. De volledige recordverdeling per minuut blijft privé; alleen aggregaten worden gepubliceerd.','',
        '## Reproductie en verificatie','',
        '- `.venv/bin/python -B -m scripts.archive_experiments` controleert de bestaande archiefregistratie; overschrijft die niet.',
        '- `.venv/bin/python -B -m scripts.execution_reality_audit` leest uitsluitend vastgelegde ledgers en code.',
        '- `.venv/bin/python -B -m scripts.raw_market` laadt bron-CSV’s en gebruikt een runtimeblokkade op strategie-, feature- en simulatiefuncties.',
        '- `.venv/bin/python -B -m scripts.publish_market_review` bouwt rapport en aggregatentabellen.',
        '- `.venv/bin/python -m pytest -q`; `npm run typecheck`; `npm run build`.',
        '- `node scripts/verify-year-holdout` verifieert de eerdere twee runs zonder nieuwe signalen.',
        '',f"Protocol SHA-256: `{d['protocol_sha256']}`.",
        f"Bronregister SHA-256: `{d['source_register_sha256']}`.",
        f"Engine SHA-256: `{a['engine_sha256']}`.",'',
        'Geen nieuw handelsmodel, filter, parameterkeuze of promotievoorstel is onderdeel van deze publicatie.','']
    text='\n'.join(lines)
    (ROOT/'docs/ARCHIVE_EXECUTION_RAW_MARKET_REPORT.md').write_text(text)
    (ROOT/'public/data/research-market-review.md').write_text(text)
    pd.DataFrame(hh).to_csv(ROOT/'public/data/research-raw-market.half-hours.csv',index=False)
    pd.DataFrame(d['correlations']).to_csv(ROOT/'public/data/research-raw-market.correlations.csv',index=False)
    pd.DataFrame(ev).to_csv(ROOT/'public/data/research-raw-market.events.csv',index=False)
    pd.DataFrame(d['tests']).to_csv(ROOT/'public/data/research-raw-market.tests.csv',index=False)
    manifest=dict(status='ARCHIVED_AND_DESCRIPTIVE_ONLY',files_sha256={str(x.relative_to(ROOT)):sha(x)
        for x in sorted((ROOT/'public/data').glob('research-*')) if x.name.startswith(('research-market-review','research-raw-market','research-execution-audit','research-experiment-archive'))},
        definitions_sha256=sha(ROOT/'research/raw-market-protocol.json'),
        calculation_code_sha256=sha(ROOT/'scripts/raw_market.py'),archived_files_verified=archive['protected_files'])
    dump(ROOT/'research/market-review-verification.json',manifest)
    print(json.dumps(dict(report_lines=len(lines),archive=archive,half_hour_rows=len(hh),event_rows=len(ev)),indent=2))


if __name__=='__main__':publish()
