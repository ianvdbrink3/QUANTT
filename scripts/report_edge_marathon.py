"""Complete local report and aggregate-only dashboard export, never raw arrays."""
import json
import re
from collections import Counter
from pathlib import Path
from scripts.edge_marathon.core import catalog
from scripts.edge_marathon.runner import ROOT,OUT,PROTOCOL,LOCK,verify,safe_dump
from scripts.afternoon_inference_round import sha


LABELS={
    'TOM_RTH':'Maandwisseling · RTH-basis',
    'TOM_TREND_1000':'ToM 1A · trend vanaf10:00',
    'TOM_OVERNIGHT_1030':'ToM 1B · overnight tot10:30',
    'TOM_ATR_CAP':'ToM 1C · vooraf bekende ATR-cap',
    'FRIDAY_CONT':'Vrijdag · weektrend voortzetten',
    'FRIDAY_REVERT':'Vrijdag · weektrend omkeren',
    'ON_INVENTORY_CONT':'Globex-inventory · voortzetting',
    'ON_INVENTORY_REVERT':'Globex-inventory · correctie',
    'COMPRESSED_BREAK5':'Compressie · eerste5m-bevestiging',
    'SWEEP_REV_1200':'Vroege mislukte sweep · tot12:00',
    'SWEEP_REV_1600':'Vroege mislukte sweep · tot16:00',
    'AFTERNOON_V2_2':'Bevroren15:00 · 2minuten',
    'AFTERNOON_V2_15':'Bevroren15:00 · 15minuten'}


def f(x,digits=2):
    if x is None:return 'n.v.t.'
    return f'{x:.{digits}f}'


def interval(x):return '['+'; '.join(f(v) for v in x)+']' if x else 'n.v.t.'


def build():
    verify()
    d=json.loads((OUT/'discovery.json').read_text());h=json.loads((OUT/'historical.json').read_text())
    register=json.loads((OUT/'source-register.json').read_text())
    overlap=json.loads((OUT/'source-overlap-parity.json').read_text()) if (OUT/'source-overlap-parity.json').exists() else None
    feasibility=json.loads((OUT/'inventory-feasibility.json').read_text()) if (OUT/'inventory-feasibility.json').exists() else None
    containers=json.loads((OUT/'non-csv-containers.json').read_text()) if (OUT/'non-csv-containers.json').exists() else None
    verified=json.loads((ROOT/'research/edge-marathon-verification.json').read_text()) if (ROOT/'research/edge-marathon-verification.json').exists() else None
    scorecard=[]
    for name,r in d['models'].items():
        reps=[]
        for sample,value in h['samples'].items():
            if 'models' not in value or name not in value['selected_model_ids']:continue
            m=value['models'][name]['metrics'];inf=value['models'][name]['inference']
            reps.append(dict(sample=sample,trades=m['trades'],net_points=m['net_points'],profit_factor=m.get('profit_factor'),
                ci95=inf['bootstrap95'],p_holm_all_sources=inf['signflip_holm_all_historical_sources'],
                source_certified=False,status='FRAGMENT_OR_UNVERIFIED_SOURCE_NOT_CONFIRMATORY'))
        scorecard.append(dict(id=name,label=LABELS.get(name,name),**r,
            historical_replications=reps,
            final_status='INDEPENDENTLY_UNCONFIRMED_NO_PROMOTION' if r['serious_discovery_candidate'] else 'NO_ROBUST_VALIDATED_EDGE',
            independently_validated=False))
    scorecard.sort(key=lambda r:(not r['serious_discovery_candidate'],r['inference']['signflip_holm25'],
        -(r['metrics'].get('profit_factor') or 0),r['id']))
    for rank,r in enumerate(scorecard,1):r['rank']=rank
    quality=[];unique_days=set()
    for sample,value in h['samples'].items():
        if 'models' not in value:continue
        included=[r['day'] for r in value['quality']['quality'] if r['included'] and value['period'][0]<=r['day']<=value['period'][1]]
        unique_days.update(included)
        quality.append(dict(sample=sample,period=value['period'],complete_days=value['complete_days'],
            overlap_with_other_sources_possible=True,exposure=value['exposure'],source_certified=False,
            note='Warmup/source quality object can cover a wider span than this fragment; reported complete_days is this fragment only.'))
    report_hashes={str(p.relative_to(ROOT)):sha(p) for p in [PROTOCOL,LOCK,OUT/'discovery.json',OUT/'historical.json',OUT/'historical-release.json']}
    result=dict(status='FIVE_PHASE_RESEARCH_COMPLETE_NO_CERTIFIED_PROFITABLE_MODEL',as_of='2026-10-22',
        discovery_complete_days=435,registered_outcomes=25,source_paths=register['scanned_paths'],unique_source_contents=register['unique_contents'],
        additional_unique_calendar_dates=len(unique_days),additional_source_session_counts_not_independent=sum(x['complete_days'] for x in quality),
        independent_validation_passes=0,serious_discovery_rows=[r['id'] for r in scorecard if r['serious_discovery_candidate']],
        scorecard=scorecard,source_quality=quality,phase1_anatomy=d['anatomy'],phase1_cap_control=d['cap_comparable_control'],
        selected_historical_models=sorted(set(d['historical_selection'])|set(h.get('completeness_addendum',{}).get('additional_models',[]))),best_tom_variant=d['best_tom_variant'],
        completeness_addendum=h.get('completeness_addendum'),
        historical_family_size=h['historical_family_size'],source_classification_counts=dict(Counter(x['classification'] for x in h['source_classification'])),
        frozen_v2_original_inference_discovery=d['frozen_v2_replay'],
        frozen_v2_original_inference_historical={s:r['frozen_v2_original_inference'] for s,r in h['samples'].items() if 'models' in r},
        technical_checks=d['checks'],source_overlap_parity=overlap,inventory_feasibility=feasibility,
        ledger_hashes={str(p.relative_to(ROOT)):sha(p) for p in sorted(OUT.glob('*-trades.csv'))},
        inputs=report_hashes,
        inference_limits=['MBB5 confidence intervals are nominal, not family-simultaneous; month-block sensitivity from earlier report preserved.',
            'Holm algebra is exact, MonteCarlo sign-flip p-values are not exact. Sign symmetry and weak dependence assumptions are not proven.',
            'Group8 gap20 variance125 information gate remains unchanged; missing tests p1, no new synthetic studies.',
            'Unverified revised continuous source is not certified independent historical-vintage proof. Do not pool overlapping sources or discovery with replication.',
            'No account-specific risk/margin budget or tick/BBO fills; point-PnLSharpe is not return-on-capitalSharpe.'],
        publication='LOCAL_ONLY_NO_GITHUB_PUSH_OR_VERCEL_DEPLOYMENT',
        protected_archive_and_v2='UNMODIFIED_VERIFY_LOCK')
    safe_dump(ROOT/'research/edge-marathon-results.json',result)
    # Only derived aggregate data in dashboard. No ledger rows, raw arrays,
    # source paths, price samples or private source-register contents.
    public=dict(result)
    public.pop('ledger_hashes');public.pop('technical_checks');public.pop('phase1_anatomy');public.pop('phase1_cap_control')
    public['phase1_paths']=d['anatomy']['groups']
    public['technical_checks_summary']=dict(prefix_truncation_checks=d['checks']['prefix_truncation_checks'],
        future_mutation_checks=d['checks']['future_mutation_checks'],
        technical_exclusions=len(d['checks']['technical_exclusions']))
    safe_dump(ROOT/'public/data/edge-marathon.json',public)
    lines=['# AUTONOMOUS EDGE DISCOVERY REPORT','',
        '22 oktober 2026. Alle vijf aangevraagde fasen zijn uitgevoerd. Eén begrensde ronde met25 vooraf vastgelegde uitkomsten, geen parametergrid. Geen nieuwe synthetische kalibratie, aankoop, download of externe publicatie. Beschermde archieven en de v2-specificatie blijven byte-identiek.','',
        '## Eindoordeel','',
        '**Geen nieuw model is als robuust, onafhankelijk gevalideerd winstgevend model aangetoond.** De15:00-2minutenregel voldoet op de verbruikte ontdekkingsdata aan de operationele ontdekkingsschermen, maar de oudere continuous-bron geeft juist een negatieve tegenuitkomst. Die bron is niet gecertificeerd en de individuele-contractfragmenten zijn te klein voor bevestiging. Geen reddingsfilter of omgekeerd signaal toegevoegd.','',
        f"Onderzocht:435 vaste RTH-dagen; {register['scanned_paths']} lokale CSV-paden /{register['unique_contents']} unieke byte-inhouden. Extra technische sessies tellen per bron op tot{result['additional_source_session_counts_not_independent']}, maar zijn niet allemaal onafhankelijk: {len(unique_days)} verschillende extra kalenderdatums. Overlappende vendors worden nooit gepoold.",'',
        '## Vooraf vastgelegde keuzes en grenzen','',
        '- ToM1A: exact10:00, bevestiging09:59close boven09:30open. Geen10:30/VWAP-alternatieven uitgeprobeerd.',
        '- ToM1B:18:00open tot10:29close. ToM-signaal is alleen kalenderafhankelijk en dus vóór entry bekend. Volledigheid van de latere nacht is uitsluitend een technische evaluatiepoort, niet een vooruitkijkend handelsfilter.',
        '- ToM1C: uitsluiting boven vooraf bekendeP90 van60 eerdere bekende ATR14-waarnemingen, geen halvering/sizing. Ontbrekende opwarming is geen laag-volatiel regime.',
        '- Vrijdag: twee vooraf expliciet concurrerende richtingen vanaf13:30 op basis van de weektrend. Inventory: efficiency>=0,70, range<=0,8ATR en RVOL>=1,5 op20 vooraf volledige nachten. Geen drempel versoepeld nadat nul events bleek.',
        '- Compressie: alleen gesloten5m-bars, eerste bevestiging, volgende baropen, vaste RTH-close. Sweep: exact één kant, bevestiging na eerste30minuten, twee vaste uitstappen. Geen stops of targets die de 1m-intrabarvolgorde zouden veronderstellen.',
        '-12 kalender/ATR-interactiecellen plus de ongewijzigde v2-referentie zijn afzonderlijke verkennende uitkomsten. Geen aanpassing van v2, geen nieuwe actuele modelpointer.',
        '- EénNQ,1,225punt/$24,50 per ronde. Alle entries opbaropen na bevestiging; exits op een vooraf vastgelegde voltooide close. Geen tick/BBO-fillcertificering. Slippage-stress is aanvullend, geen bewijs dat de basisfrictie historisch toereikend was.','',
        '## Fase1 — Maandwisseling ontmanteld','',
        '### Volledig tijdpad van alle81 oorspronkelijke ToM-dagen','',
        '| Deelvenster | N | Gemiddeld bruto pt | P10 | Mediaan | P90 |',
        '|---|---:|---:|---:|---:|---:|']
    for field in ['overnight_points','opening_gap','morning','midday','afternoon','bridge1100','bridge1400','rth_points']:
        r=d['anatomy']['groups']['ALL'][field];q=r['distribution']
        lines.append(f"| {field} | {r['days']} | {f(r['mean'])} | {f(q['p10']) if q else 'n.v.t.'} | {f(q['median']) if q else 'n.v.t.'} | {f(q['p90']) if q else 'n.v.t.'} |")
    lines += ['', 'Morning=09:30–11:00, midday=11:00–14:00, afternoon=14:00–16:00; overnight=18:00–09:30. Endpoint is steeds de laatste voltooide minuutclose. De twee interbarbruggen maken de som exact gelijk aan de brutoRTH-beweging. De openinggap verbindt09:29close met09:30open. Alle81dagen blijven staan; slechts78 hebben de volledige nacht voor de overnightvergelijking. Geen overnight-toeschrijving uit onvolledige bars.','',
        '### Dagpositie binnen het vierdaagse venster','', '| Positie | N RTH | Ochtend gem. | Middag gem. | Slotdeel gem. | Totaal RTH gem. |','|---|---:|---:|---:|---:|---:|']
    for pos in ['T-1','T+1','T+2','T+3']:
        g=d['anatomy']['groups'][pos]
        lines.append(f"| {pos} | {g['rth_points']['days']} | {f(g['morning']['mean'])} | {f(g['midday']['mean'])} | {f(g['afternoon']['mean'])} | {f(g['rth_points']['mean'])} |")
    lines += ['', '### Grootste verliesdagen: waar ontstond het verlies?','',
        '| Dag | Positie | Ochtend pt | Middag pt | Slotdeel pt | Bruto RTH pt |',
        '|---|---|---:|---:|---:|---:|']
    for r in d['anatomy']['worst5_days']:
        lines.append(f"| {r['day']} | {r['position']} | {f(r['morning'])} | {f(r['midday'])} | {f(r['afternoon'])} | {f(r['rth_points'])} |")
    lines += ['', 'De verliesdag3maart2025 is niet alleen een vroege capitulatie: ook na14:00 gaat273,75punt verloren. Andere grote verliezen worden juist in de middag gedeeltelijk teruggewonnen. Dit is tijdpadbeschrijving, geen reden om achteraf een nieuw uitstaptijdstip te kiezen.','',
        '### De drie vaste varianten tegenover de ongewijzigde basis','',
        '| Model | N | Netto pt | PF | Win% | Positieve kwartalen | 95% MBB5 gemiddelde | Holm25 signflip |',
        '|---|---:|---:|---:|---:|---|---|---:|']
    for name in ['TOM_RTH','TOM_TREND_1000','TOM_OVERNIGHT_1030','TOM_ATR_CAP']:
        r=d['models'][name];m=r['metrics'];i=r['inference']
        lines.append(f"| {name} | {m['trades']} | {f(m['net_points'])} | {f(m['profit_factor'],3)} | {f(100*m['winrate'])} | {f(m['positive_quarter_fraction']*m['quarters'],0)}/{m['quarters']} | {interval(i['bootstrap95'])} | {f(i['signflip_holm25'],5)} |")
    cc=d['cap_comparable_control']
    lines += ['', f"ATR-cap op vergelijkbare voorgeschiedenis: {cc['comparable_known_history_days']}ToM-dagen hebben de60ATR-waarnemingen. De baseline op precies die voorgeschiedenis levert{f(cc['matched_baseline']['net_points'])}punt; de cap{f(cc['cap']['net_points'])}punt. {len(cc['missing60history_tom_dates'])}vroegeToM-dagen vallen weg door ontbrekende opwarming. Die verandering mag niet aan de cap worden toegeschreven.",'',
        '**Geen van de drie varianten heeft een positieve95%-ondergrens.** De basis is exact dezelfde81trades/+4.364,025punt als tevoren. Het nieuwe MBB5-interval ligt nipt boven nul, terwijl de eerder vastgelegde maandblok-bootstrap[-0,11;+111,69] bevatte. Dat is gevoeligheid voor de onzekerheidsmethode, geen verbetering van de strategie. Beide blijven zichtbaar; Holm25 geeft de basis geen significantie.','',
        '## Fase2 — Volledige Master Scorecard','',
        'Alle25uitkomsten staan hieronder, inclusief lege cellen. Rangschikking: eerst het vooraf gedefinieerde ontdekkingsscherm, dan Holm25-signflip, danPF; geen keuze op één fraai kwartaal.','',
        '| Rang | Model | N | Netto pt | PF | Win% | Kwartalen +% | 95% MBB5 | Ruwe signflip p | Holm25 | Groep8 Holm25 |',
        '|---:|---|---:|---:|---:|---:|---:|---|---:|---:|---:|']
    for r in scorecard:
        m=r['metrics'];i=r['inference']
        lines.append(f"| {r['rank']} | {r['id']} | {m['trades']} | {f(m['net_points'])} | {f(m.get('profit_factor'),3)} | {f(100*m['winrate']) if m.get('winrate') is not None else 'n.v.t.'} | {f(100*m['positive_quarter_fraction']) if m.get('positive_quarter_fraction') is not None else 'n.v.t.'} | {interval(i['bootstrap95'])} | {f(i['signflip_p'],6)} | {f(i['signflip_holm25'],6)} | {f(i['conservative_holm25'],6)} |")
    lines += ['', '### Onvoorwaardelijke benchmark per model','',
        '| Model | Gem. netto pt | Zelfde klok/directionele benchmark | Verschil pt | Zelfde eventdagen blind long |','|---|---:|---:|---:|---:|']
    for r in scorecard:
        m=r['metrics'];b=r['benchmark']
        lines.append(f"| {r['id']} | {f(m.get('mean_net'))} | {f(b['unconditional_same_clock_mean'])} | {f(b['mean_premium'])} | {f(b['matched_blind_long_mean'])} |")
    lines += ['', 'Voor variabele5m-entry wordt de identieke entry-/exitklok op alle complete dagen gebruikt, met dezelfde oriëntatie en kosten. Dit is een beschrijvende benchmark, geen causaal experiment of extra p-toets. Voor overnight staan alleen nachten met de volledige vereiste vensters in de benchmark.','']
    if feasibility:lines += ['### Waarom inventory geen events gaf','', '```json',json.dumps(feasibility,indent=2),'```','']
    lines += ['### Toetsmethode en grenzen','',
        '-10.000 MBB5-resamples op de oorspronkelijke weekdagkalender, dagclusters en ratio somP&L/aantal geselecteerde events. Niet-geselecteerde dagen zijn nul-invloed, geen verzonnen nultrade. Nominale95%-intervallen, niet gelijktijdig over25modellen.',
        '- Tweezijdige signflip van hele dagclusters: exacte enumeratie bij<=16eventdagen, anders99.999MonteCarlo-trekkingen met plus-onecorrectie. De **Holm-formule is exact**, de MonteCarlo-ruwe p is **niet exact**. Geldigheid veronderstelt passende gezamenlijke teken-symmetrie; niet universeel gewaarborgd bij seriële afhankelijkheid.',
        '- De conservatieve toets gebruikt dezelfde8blokken,20weekdag-gaps, SE×sqrt(1,25), tdf7, minimaal8events/blok én120gescoorde events totaal. Geen poort verlaagd of nieuwe kalibratie gestart. De162v2-events leveren na vaste gaps109gescoorde events: DATA_INSUFFICIENT, p1. Een signflip-succes wordt niet verkocht als goedkeuring door die conservatieve toets.',
        '- De originele v2HAC5/Holm2-uitvoer wordt als afzonderlijke, ongewijzigde-receptreplay weergegeven; geen aanpassing van de bevroren specificatie. Deze ontdekkingsronde en fragmenten zijn niet het oorspronkelijke definitieve fixed-end holdoutvenster.','',
        '## Fase3 — Alle lokale bronnen en de aparte historische controles','',
        '| Bron/fragment | Periode | Complete dagen | Blootstellings-/validatiestatus |','|---|---|---:|---|']
    for q in quality:lines.append(f"| {q['sample']} | {'–'.join(q['period'])} | {q['complete_days']} | {q['exposure']} |")
    lines += ['', 'AlleCSV’s zijn gehasht en byte-identieke kopieën gegroepeerd. De69geregistreerde ontdekkingsbronnen zijn opnieuw streng geladen. Hogere timeframes worden niet opgeschaald. De grote continuous-reeks is alleen vóór30december2024 gescoord, ET bar-endlabel vast één minuut terug, zoals reeds vóór deze ronde gedocumenteerd. De FirstRate-sample is een gedownloade historische oktober2026sample, geen na preregistratie verzamelde forwardreeks.','',
        'Contractfragment2018gebruikt de vastgelegde volume-overgang14december/activatie17december en causale additive offsets voor indicatoren, nooit voor ruwe fills. De acht januaridagen krijgen uitsluitend vooraf bekende opwarming. H24 en de FirstRate-sample lenen geen ontbrekende60ATR-dagen van een andere leverancier of een ander jaar.','',
        f"Historische selectie vóór inzage: besteToM-variant opPF onder positievePF>1,30varianten = **{d['best_tom_variant']}**. Verder v2-paar,ToM-basis als referentie en alle positievePF>1,30fase2rijen. Exacte lijst staat in historical-release.json. Niet-geselecteerde modellen krijgen geen nieuwe historische outcome-evaluatie en blijven p1 in de familie. Daarnaast Holm over alle{h['historical_family_size']}rijen van de vijf bron/fragmentfamilies; geen gunstigste bron uitzoeken.",'',
        '| Fragment | Model | N | Netto pt | PF | 95% MBB5 gemiddelde | Holm alle historische bronnen |','|---|---|---:|---:|---:|---|---:|']
    for sample,value in h['samples'].items():
        if 'models' not in value:continue
        for name in value['selected_model_ids']:
            r=value['models'][name];m=r['metrics'];i=r['inference']
            lines.append(f"| {sample} | {name} | {m['trades']} | {f(m['net_points'])} | {f(m.get('profit_factor'),3)} | {interval(i['bootstrap95'])} | {f(i['signflip_holm_all_historical_sources'],6)} |")
    lines += ['', '**Bronstatus is bepalend:** de493oudere complete sessies geven meer informatie dan acht dagen, maar de contractketen, adjustmentmethode, publicatievintages en absolute eerdere niet-inzage zijn niet bewezen. Die resultaten zijn een afzonderlijke static-vintage-brongevoeligheidscontrole, niet gecertificeerd onafhankelijk point-in-time bewijs. De H24-datums overlappen grotendeels met die bron; geen onafhankelijke replicaties optellen.','']
    if h.get('completeness_addendum'):
        lines += ['### Gedocumenteerde volledigheidscorrectie: geen waargenomen verliestrade','',
            'Eén reeds vastgelegde cel, AFTERNOON_TOM_YES_HIGH_2, heeft6winnaars en dus geen eindige geschattePF. De eerste mechanische selectie behandelde PF=n.v.t. als niet-kwalificerend. Om geen all-win-cel aan de historische controle te onttrekken, is die cel aanvullend geëvalueerd. Het oorspronkelijke bronslot, de oorspronkelijke selectierelease en originele historische uitvoer zijn bewaard. Een apart addendum is vastgelegd vóór uitkomstberekening van deze ontbrekende cel. Geen nieuwe hypothese, filter, horizon, periode of kleinere familie; alle25/125correcties zijn opnieuw inclusief die cel berekend. De no-lossPF blijft n.v.t., niet een als bewezen verkochte oneindigePF. Dit is een expliciete volledigheidscorrectie ná de eerste geselecteerde bronuitkomsten, geen claim dat het addendum een onafhankelijke preregistratie is.','']
    if overlap:lines += ['### Vaste-conventie bronvergelijking op reeds verbruikte overlap','', '```json',json.dumps(overlap,indent=2),'```','']
    if containers:
        lines += ['### Overige lokale containers: geen gemiste NQ-historie','',
            'Ook de bekende project-Parquet/ZIP-containers zijn metadata-only gecontroleerd, zonder archieven uit te pakken of CFDs als futures te herlabelen. De afgeleide NQ-master bevat106.678reeds verbruikte bars. De twee USATECHIDXUSD-Parquetbestanden zijn elk1.440Dukascopy-CFD-bars; de NSXUSD-archieven zijn geen NQ-contractbestanden of niet-importeerbare ZIPs. Geen extra ongebruikte NQ-holdout gevonden in deze bekende containers.','',
            '| Bestand | Rijen indien Parquet | Classificatie |','|---|---:|---|']
        for r in containers['records']:lines.append(f"| {r['filename']} | {r.get('rows','n.v.t.')} | {r['classification']} |")
        lines += ['','Dit betreft de afgesproken projectdatamappen en bekende containers, niet de volledige persoonlijke schijf. Private metadata/hashes staan in non-csv-containers.json.','']
    lines += ['### Bevroren v2: oorspronkelijke inferentie afzonderlijk','', '```json',json.dumps(dict(discovery=d['frozen_v2_replay'],historical=result['frozen_v2_original_inference_historical']),indent=2),'```','',
        'Een klein fragment met vier winstgevende events kan een smal naïef interval geven. Dat vult geen vaste driejaarsproef en de Holmcorrectie/informatiepoort/kwartaalvereiste blijven gelden. Geen HOLDOUT_PASSED op basis van deze fragmenten.','',
        '## Fase4 — Falsificatie en uitvoeringsrisico','',
        'Alle netto positieve rijen krijgen onderstaande controles; ook negatieve rijen blijven in de JSON. Sharpe/Sortino zijn geannualiseerde ratio’s van één-contract dagpunt-P&L inclusief nul op niet-handelsweekdagen, geen rendement op geïnvesteerd kapitaal. Gesloten-equityDD dekt intraday margin calls niet af.','',
        '| Model | DD pt | Slechtste dag pt | Max verliesreeks | Dag Sharpe | Dag Sortino | Top3/net% | Netto zonder top3 | LODO gem. min/max | LOQO gem. min/max | Netto +2ticks/kant |','|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|']
    for r in scorecard:
        m=r['metrics']
        if m['net_points']<=0:continue
        lines.append(f"| {r['id']} | {f(m['drawdown'])} | {f(m['worst_day'])} | {m['max_consecutive_losses']} | {f(m['daily_sharpe'])} | {f(m['daily_sortino'])} | {f(100*m['top3_share_of_net'])} | {f(m['net_without_top3'])} | {interval(m['leave_one_day_out_mean'])} | {interval(m['leave_one_quarter_out_mean'])} | {f(m['slippage'][-1]['net_points'])} |")
    lines += ['', 'Operationele risicopoort vóór de run: DD<=50%netgain, top3<=50%net, netto zondertop3>0, minimaleLOQOmean>0, netto positief bij2extraticks/kant. Dit is een onderzoeksvergelijking en geen veilige positiegrootte voor een onbekende rekening. AlleMAE/MFE-percentielen hieronder blijven daarom zichtbaar.','',
        '| Model | MFE P25 | MFE mediaan | MFE P75 | MAE P25 | MAE mediaan | MAE P75 | MAE P90 | MAE/ATR P95 |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in scorecard:
        m=r['metrics']
        if not m['trades']:continue
        a,b=m['mfe'],m['mae'];ratio=m['mae_atr']
        lines.append(f"| {r['id']} | {f(a['p25'])} | {f(a['median'])} | {f(a['p75'])} | {f(b['p25'])} | {f(b['median'])} | {f(b['p75'])} | {f(b['p90'])} | {f(ratio['p95']) if ratio else 'n.v.t.'} |")
    lines += ['', '### Alle ontdekkingskwartalen per model','', '| Model | Kwartaal | N | Netto pt | Gemiddeld netto pt |','|---|---|---:|---:|---:|']
    for r in scorecard:
        for q,m in r['metrics'].get('quarterly',{}).items():lines.append(f"| {r['id']} | {q} | {m['trades']} | {f(m['net_points'])} | {f(m['mean_net'])} |")
    lines += ['', '### Historische positieve rijen: dezelfde risico- en kwartaalcijfers','',
        'Dezelfde metrics,LODO/LOQO,Sharpe/Sortino,MFE/MAE en kostenscenario’s zijn ook voor ieder historisch model berekend in de lokale historischeJSON. Hieronder staan alle historische rijen met positieve nettoP&L, inclusief kleine fragmenten; nergens wordt een te kleine steekproef gepromoveerd.','',
        '| Bron | Model | N | DD pt | Grootste verliesdag | Top3/net% | LODO | LOQO | MFE mediaan | MAE mediaan | +2ticks net pt |','|---|---|---:|---:|---:|---:|---|---|---:|---:|---:|']
    for sample,value in h['samples'].items():
        if 'models' not in value:continue
        for name,r in value['models'].items():
            m=r['metrics']
            if m['net_points']<=0:continue
            lines.append(f"| {sample} | {name} | {m['trades']} | {f(m['drawdown'])} | {f(m['worst_day'])} | {f(100*m['top3_share_of_net'])} | {interval(m['leave_one_day_out_mean'])} | {interval(m['leave_one_quarter_out_mean'])} | {f(m['mfe']['median'])} | {f(m['mae']['median'])} | {f(m['slippage'][-1]['net_points'])} |")
    lines += ['', '### Volledige kostengevoeligheid op ontdekkingsdata','',
        '| Model | N | $24,50 netto pt | $34,50 netto pt | $44,50 netto pt | Gem. bij $44,50 |','|---|---:|---:|---:|---:|---:|']
    for r in scorecard:
        m=r['metrics']
        if not m['trades']:continue
        costs=m['slippage']
        lines.append(f"| {r['id']} | {m['trades']} | {f(costs[0]['net_points'])} | {f(costs[1]['net_points'])} | {f(costs[2]['net_points'])} | {f(costs[2]['mean_net'])} |")
    lines += ['', '### Historische kalenderkwartalen per geselecteerde rij','',
        '| Bron | Model | Kwartaal | N | Netto pt |','|---|---|---|---:|---:|']
    for sample,value in h['samples'].items():
        if 'models' not in value:continue
        for name in value['selected_model_ids']:
            for quarter,m in value['models'][name]['metrics'].get('quarterly',{}).items():
                lines.append(f"| {sample} | {name} | {quarter} | {m['trades']} | {f(m['net_points'])} |")
    lines += ['', '### Historische positieve rijen: Sharpe, Sortino, verliesreeks en beide extra fricties','',
        '| Bron | Model | Sharpe | Sortino | Verliesreeks | Netto bij $34,50 | Netto bij $44,50 |','|---|---|---:|---:|---:|---:|---:|']
    for sample,value in h['samples'].items():
        if 'models' not in value:continue
        for name,r in value['models'].items():
            m=r['metrics']
            if m['net_points']<=0:continue
            lines.append(f"| {sample} | {name} | {f(m['daily_sharpe'])} | {f(m['daily_sortino'])} | {m['max_consecutive_losses']} | {f(m['slippage'][1]['net_points'])} | {f(m['slippage'][2]['net_points'])} |")
    lines += ['', '## Fase5 — Tests, herberekening en lokale dashboardpagina','',
        f"Op alle435ontdekkingsdagen: {d['checks']['prefix_truncation_checks']}toekomst-afknipcontroles en evenveel latere-barmutaties. Kalender,voorgaandeATR/volume, bevestiging/fill,horizons, legefamiliecellen en nulbeginkapitaal worden apart getest. Historische prefixcontroles staan per bron geregistreerd.",'',
        'Verificatie-evidence (volledige suite, tweede bronherlaad-run, hashes, build/typecheck en browser) wordt afzonderlijk vastgelegd in research/edge-marathon-verification.json. Alleen dat bestand is bewijs van een daadwerkelijk uitgevoerde verificatie; deze rapporttekst claimt geen niet-uitgevoerde test.','',
        'Lokale dashboarduitbreiding: /research/marathon. Afgeleide totalen en tabellen staan in public/data/edge-marathon.json; geen privateCSV’s, tradeledgers, ruwe arrays of absolutebronpaden. Het oude dashboard en alle beschermde bestanden blijven intact. Geen externe synchronisatie gevraagd of uitgevoerd.','',
        '### Reproduceren','', '```sh',
        'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m scripts.edge_marathon.runner verify',
        'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m scripts.edge_marathon.runner discovery',
        'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m scripts.edge_marathon.runner history',
        'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m scripts.complete_marathon_zero_loss',
        'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m scripts.audit_marathon_source_overlap',
        '.venv/bin/python -m scripts.report_edge_marathon',
        '.venv/bin/python -m pytest -q', '```','',
        'Geen wijzigingen na teleurstellende uitkomsten: geen nieuw tijdstip, anderevolumegrens, omkering van de15:00-regel of gunstigsteperiode. Meer modellen op dezelfde verbruikte data krijgen niet vanzelf onafhankelijke bewijskracht.','']
    if verified and verified['status']=='FULL_MARATHON_VERIFICATION_PASSED':
        events=sum(x['events'] for x in verified['independent_reference']['samples'])
        lines += ['', '## Daadwerkelijk uitgevoerde eindverificatie','',
            f"**{verified['tests_passed']} tests geslaagd**, typecheck en productiebuild geslaagd. Afzonderlijk geschreven signaal-/fill-referentie: **{events} events** met dezelfde beslissingen, ankers, kosten en excursies. Deze deelt de bronparser/context en is dus technische verificatie, geen onafhankelijke onderzoeker of marktvalidatie.",'',
            'De volledige tweede bronherlaad-run is byte-identiek. Exacte aantallen en hashes van de uiteindelijke uitvoer staan in research/edge-marathon-verification.json. Het metadata-only containeronderzoek verandert geen modeluitkomst. Alle115beschermde archiefbestanden, de73bevroren onderzoeksbestanden en de v2-specificatie zijn gecontroleerd en intact.','',
            'De oude registratieverifiers bevatten nog de tekst outcomesnotreleased/newruns0. Dat zijn ongewijzigde verklaringen van hun oorspronkelijke registratie, geen uitspraak dat deze nieuwe marathon geen fragmentuitkomsten berekende. Het volledige fixed-end venster2019–2021is niet voltooid of als geslaagde proef geclaimd.','',
            'Holm25/125 corrigeert uitsluitend deze begrensde families, niet alle eerdere scans of adaptieve modelvorming op reeds verbruikte data. Nieuwe synthetische kalibratiestudies zijn niet gedraaid.','']
    lines += ['## Primaire bronnen en volledige protocolhash','']
    for url in json.loads(PROTOCOL.read_text())['sources']:lines.append('- '+url)
    lines += ['', 'Protocol SHA256: '+sha(PROTOCOL), 'Implementatie/bronslot SHA256: '+sha(LOCK),
        'Allebronhashes en privatepaden blijven in het lokale genegeerde bronregister. Publieke resultaatJSON bevat alleen afgeleide statistiek.']
    # Prose-only spacing. Never rewrite hashes, JSON, commands or tables.
    original='\n'.join(lines)+'\n';formatted=[];in_code=False
    for line in lines:
        if line.startswith('```'):
            in_code=not in_code;formatted.append(line);continue
        technical=in_code or line.startswith('|') or bool(re.search(r'[0-9a-f]{64}',line)) or line.startswith('- https://')
        formatted.append(line if technical else re.sub(r'(\d)([A-Za-zÀ-ÿ]{3,})',r'\1 \2',line))
    report='\n'.join(formatted)+'\n'
    if any(digest not in report for digest in re.findall(r'[0-9a-f]{64}',original)):
        raise ValueError('Report formatting changed a SHA256')
    before_json=[json.loads(x) for x in re.findall(r'```json\n(.*?)\n```',original,re.S)]
    after_json=[json.loads(x) for x in re.findall(r'```json\n(.*?)\n```',report,re.S)]
    if before_json!=after_json:raise ValueError('Report formatting changed embedded evidence')
    (ROOT/'docs/AUTONOMOUS_EDGE_DISCOVERY_REPORT.md').write_text(report)
    (ROOT/'public/reports').mkdir(exist_ok=True)
    # Public report omits per-day anatomy and private provenance; use a short
    # derived-only companion rather than copying the complete local report.
    brief='\n'.join(['# QUANTT autonome onderzoeksronde','',result['status'],'',
        '435ontdekkingsdagen,25vaste uitkomsten. Geen gecertificeerd onafhankelijk winstmodel. Alle cijfers en beperkingen staan op/research/marathon en in/data/edge-marathon.json.','',
        'Bronfragmenten zijn apart gehouden. De oudere continuous-bron heeft onbevestigde contract-/vintageherkomst. Geen rawCSV, individuele tradeledger of prijsarray gepubliceerd. Geen nieuweparameters of externeuitrol.'])+'\n'
    (ROOT/'public/reports/AUTONOMOUS_EDGE_DISCOVERY_SUMMARY.md').write_text(brief)
    print(result['status'],len(scorecard),'rows,',len(unique_days),'unique extra dates',flush=True)
    return result


if __name__=='__main__':build()
