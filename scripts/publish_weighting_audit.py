"""Deterministic methodological addendum; old publications remain untouched."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.weighting_audit.__main__ import ROOT,OUT,LOCK,preflight,verify_completed,dump
from scripts.weighting_audit.core import SIDES,HORIZONS,SCHEMES,wilson
from scripts.oos_preparation.adapter import sha

LABELS={'event':'Ieder event gelijk','equal_day':'Iedere eventdag gelijk',
        'past_count':'Gepoold gewicht1/k','first_record':'Eerste record per dag'}
NULLS={'gaussian_iid':'Gaussian i.i.d.', 'gaussian_clock_scale':'Gaussian met klok- en dagschaal',
       'conditional_bar_reflections':'Spiegelingen echte barvormen'}


def f(x,n=3):
    return 'n.v.t.' if x is None else f'{x:,.{n}f}'.replace(',','#').replace('.',',').replace('#','.')


def interval(values,n=3):return '['+'; '.join(f(v,n) for v in values)+']'


def table(lines,headers,rows):
    lines += ['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']
    lines += ['| '+' | '.join(str(x) for x in row)+' |' for row in rows]
    lines.append('')


def additional_tables(d):
    comparisons=[]
    for r in d['comparisons']:
        row={k:v for k,v in r.items() if k not in ['null','null_event_count']}
        row.update({'null_'+k:v for k,v in r['null'].items()})
        row.update({'null_event_count_'+k:v for k,v in r['null_event_count'].items()})
        comparisons.append(row)
    rates=[]
    for null in NULLS:
        for side in SIDES:
            for horizon in HORIZONS:
                for scheme in SCHEMES[:2]:
                    pair=[r for r in d['zero_test_calibration'] if (r['generator'],r['side'],r['horizon'],r['scheme'])==(null,side,horizon,scheme)]
                    row=dict(generator=null,side=side,horizon=horizon,scheme=scheme,panels=pair[0]['panels'])
                    for r in pair:
                        prefix=r['procedure'];row[prefix+'_rejections']=r['rejections'];row[prefix+'_rate']=r['rate']
                        row[prefix+'_wilson_95']=r['wilson_95']
                    rates.append(row)
    family=[]
    for null in NULLS:
        data=np.load(OUT/(null+'.npz'))
        for procedure,key in [('nominal','calibration_p'),('holm43','calibration_holm43')]:
            p=data[key];indicator=(p<.05).reshape(len(p),-1).any(axis=1);successes=int(indicator.sum())
            family.append(dict(generator=null,procedure=procedure,panels=len(p),panels_with_any_record_rejection=successes,
                rate=successes/len(p),wilson_95=wilson(successes,len(p)),
                note='Any zero rejection among12record tests, not typeI error for a true equal-day zero null'))
    return dict(comparisons=comparisons,zero_calibration=rates,family_calibration=family)


def render(d,t):
    p=d['protocol'];ind=d['independent_reproduction'];sig=sum(r['p_holm72']<.05 for r in d['comparisons'])
    lines=['# Wegingsaudit: dagextremen, eventaantallen en schijnbare voorspelbaarheid','',
        '## Kernuitkomst en afbakening','',
        'Een eventgewogen en een daggewogen gemiddelde meten verschillende grootheden. Het delen door het uiteindelijke aantal events kan in een koersproces met onvoorspelbare toekomstige log-rendementen toch een niet-nul daggemiddelde opleveren. Dat is geen tegenstrijdigheid en op zichzelf geen fout in de optelling. Het is wel een probleem wanneer zo’n daggemiddelde als bewijs voor voorspelbaarheid wordt gebruikt.','',
        f"De nieuwe audit controleert dit met alle256 korte muntworpkoerspaden, een onafhankelijke bronherberekening en **{d['total_null_experiments']:,} nul-experimenten**, samen {d['total_null_days']:,} gesimuleerde handelsdagen. Vier meetwijzen, twee recordsides en drie horizonten staan volledig in de publicatie. De drie nulscenario’s zijn illustratief, geen bewezen NQ-marktmodellen.",'',
        '**Geen nieuw handelsmodel.** De vier basisschermen blijven ARCHIVED_NOT_VALIDATED. Geen entries, stops, targets, koersdoelen, filters voor toekomstige trading, parameterzoektocht of nieuwe holdout. De oorspronkelijke ruwe-marktmetingen en p-waarden zijn niet overschreven.','',
        '### Concrete uitkomst van deze batch','']
    dayrates=[r for r in d['zero_test_calibration'] if r['scheme']=='equal_day' and r['procedure']=='holm43']
    controls=[r for r in d['comparisons'] if r['scheme'] in ['past_count','first_record']]
    lines += [f"- Iedere afzonderlijke daggewogen record/horizontoets verwerpt gemiddelde0 na Holm43 in {min(r['rejections'] for r in dayrates)}–{max(r['rejections'] for r in dayrates)} van128 panelen, in alle drie nulscenario’s. De echte toekomstige richtingsinnovaties blijven daarin onvoorspelbaar.",
        f"- Van alle72 NQ-versus-nulmodelvergelijkingen haalt {sig} de Holm72-grens. Voor de36 vergelijkingen van de twee meetcontroles1/k en eerste record zijn dat {sum(r['p_holm72']<.05 for r in controls)}."]
    for r in d['comparisons']:
        if r['p_holm72']<.05:
            alternatives=[x for x in d['comparisons'] if x['generator']!=r['generator'] and (x['side'],x['horizon'],x['scheme'])==(r['side'],r['horizon'],r['scheme'])]
            lines.append(f"- De overblijvende afwijking betreft {r['side']}, {r['horizon']}, {LABELS[r['scheme']]} tegenover {NULLS[r['generator']]}: NQ {f(r['observed_bps'])} bp versus nulmediaan {f(r['null']['median'])}, Holm72 p={f(r['p_holm72'],6)}. Dezelfde meetwijze tegenover de andere scenario’s: "+'; '.join(NULLS[x['generator']]+': Holm72 p='+f(x['p_holm72'],6) for x in alternatives)+'. Dit is een nulmodelafwijking, geen gevalideerde edge; de Monte-Carlo-resolutiegrens wordt hieronder expliciet behandeld.')
    lines += ['', 'Het kernprobleem is dus niet dat de eerder gepubliceerde daggemiddelden verkeerd waren opgeteld. Hun gebruik als argument voor voorspelbare omkeer is niet gerechtvaardigd: hetzelfde soort effect is aantoonbaar verenigbaar met processen zonder voorspelbare vervolgrendementen. De audit bewijst niet dat iedere mogelijke marktvoorspelling onmogelijk is.','',
        '## 1. Wat wordt precies gemiddeld?','',
        'Voor dag d: N_d = aantal horizon-eligible records, Y_dk = getekend vervolgrendement van record k, S_d = som van Y_dk. D+ telt alleen dagen met minstens één dergelijk record. Alle rendementen zijn log-basispunten; lows krijgen géén omgekeerd teken.','']
    table(lines,['Meting','Formule','Wat is bekend op het eventmoment?'],[
        ['Ieder event gelijk','Σ_d S_d / Σ_d N_d','Het huidige record en de verstreken geschiedenis; het totale aantal events nog niet. De teller is een som van causaal gekozen event-outcomes.'],
        ['Iedere eventdag gelijk','gemiddelde_d(S_d/N_d), alleen N_d>0','Het uiteindelijke N_d is pas aan het einde van het eventvenster bekend. Elk vroeg event krijgt daardoor een achteraf bepaald gewicht.'],
        ['Gepoold1/k','Σ_dk(Y_dk/k) / Σ_dk(1/k)','k is de rang van het huidige record, bekend op het eventmoment. Er volgt géén per-dag renormalisatie. De eindige globale ratio is niet gegarandeerd exact onvertekend.'],
        ['Eerste record','Gemiddelde uitkomst van het eerste record per eventdag','Het optreden van het eerste record is een begrensde stopping time. Dit is een meetcontrole, geen voorgestelde entry of filter.']])
    lines += ['Onder een martingaal voor log-prijzen is het verwachte toekomstige log-rendement na een causaal vastgesteld record nul. Een gewicht dat van latere records afhangt hoeft echter niet onafhankelijk te zijn van dat vervolgrendement. Een beschrijvend daggemiddelde kan dus echt niet-nul zijn in een markt zonder deze voorspelbaarheid.','',
        '### Exacte identiteit','',
        '`eventgemiddelde − daggemiddelde = Cov_pop(N_d, S_d/N_d) / gemiddelde(N_d)`','',
        'Deze identiteit geldt exact over dezelfde eventdagen, zonder regressie of geschatte parameters. Zij verklaart rekenkundig het volledige verschil tussen de twee gemiddelden, maar identificeert géén causaal percentage van een trading edge.','',
        'Een eenvoudig voorbeeld: dag A heeft drie outcomes van +1, dag B één van −3. Het eventgemiddelde is0, het daggemiddelde −1. Geen fout: de weging veranderde. Dit voorbeeld alleen bewijst geen onvoorspelbaar proces; daarvoor volgt de exacte muntworpcontrole.','',
        '### NQ: exacte ontbinding','']
    table(lines,['Record','Horizon','Events','Eventdagen','Eventgem. bp','Daggem. bp','Verschil','95%CI gepaard verschil','Cov(N,daggem.) / gem.N','Numeriek restverschil'],[
        [r['side'],r['horizon'],r['events'],r['days'],f(r['event_mean']),f(r['equal_day_mean']),f(r['event_minus_day']),
         interval(r['paired_gap_95_ci']),f(r['cov_over_mean_count']),f(r['identity_residual'],12)] for r in d['weighting_decomposition']])
    lines += ['### Spreiding van het eventaantal per eventdag','']
    table(lines,['Record','Horizon','Minimum N','Mediaan N','P95 N','Maximum N'],[
        [r['side'],r['horizon'],r['count_min'],f(r['count_median'],1),f(r['count_p95'],1),r['count_max']] for r in d['weighting_decomposition']])
    lines += ['## 2. Exact tegenvoorbeeld: alle256 muntworpkoerspaden','',
        'Acht onafhankelijke symmetrische log-prijsstappen van +1/−1; alle256 paden even waarschijnlijk. Elke bar omvat open en close. De eerste bar vormt alleen het initiële high/low. Records en censoring worden zonder enige marktdata bepaald. Geen drift of voorspelbare volgende stap. De scalar referentie en vectorberekening zijn afzonderlijk geschreven en getest.','']
    table(lines,['Record','Horizon','Paden','Eventdagen','Eventgemiddelde','Daggemiddelde','Gepoold1/k','Eerste record'],[
        [r['side'],r['horizon'],r['equiprobable_paths'],r['event_days'],f(r['event'],6),f(r['equal_day'],6),f(r['past_count'],6),f(r['first_record'],6)] for r in d['exact_enumeration']])
    lines += ['De waarden hebben hier de eenheid van de muntworp-logprijsstap, niet een gekalibreerde NQ-puntwaarde. Dit exacte tegenvoorbeeld toont dat een niet-nul daggewogen recordgemiddelde geen voldoende bewijs voor voorspelbare toekomstige rendementen is. Het zegt niet welk percentage van elk waargenomen NQ-effect door hetzelfde mechanisme ontstaat.','',
        '## 3. Onafhankelijke bron- en formulecontrole','',
        f"{ind['source_files']} bronbestanden opnieuw op SHA-256 gecontroleerd; dezelfde435 complete RTH-dagen en454 geplande sessierijen als eerder. {ind['record_event_horizon_rows']} record/horizonregels onafhankelijk opnieuw geïdentificeerd. Datums, eventlabels, bar-tijden, puntsverschillen en log-rendementen komen overeen met de vorige private eventregels.",'',
        f"Maximaal absoluut verschil met een gepubliceerd gemiddelde: {f(ind['max_abs_published_mean_error_bps'],12)} bp. Maximaal verschil met eerdere 95%-bootstrapgrenzen: {f(ind['max_abs_previous_ci_error_bps'],12)} bp. Maximaal p-verschil van de eerdere gecentreerde nulwaardetoets: {f(ind['max_abs_previous_p_error'],12)}.",'',
        'De nieuwe rekenkern importeert geen eerdere eventextractor, gemiddelden-, bootstrap- of Holm-functie. De bestaande import-/kalender-/contractregisters worden wel hergebruikt: de audit mag de dataset of rolloverkeuze niet veranderen. Runtimeblokkades verhinderen het aanroepen van strategiefuncties tijdens de bronextractie.','',
        '### Alle vier gemeten NQ-estimators','',
        'Nominale 95%-intervallen uit een onafhankelijk geïmplementeerde circular moving-block bootstrap:4.000 replicaties, blokken van vijf geplande sessies, seed20261022. De19 uitgesloten sessies blijven als ontbrekende maskers in de kalender; geen fictieve nulrendementen. Intervallen zijn niet simultaan. Er worden hier geen nieuwe nulwaardep-waarden op de extra meetcontroles geplakt.','']
    table(lines,['Record','Horizon','Meetwijze','Eventdagen','Events','Gemiddelde bp','Nominaal95%CI'],[
        [r['side'],r['horizon'],LABELS[r['scheme']],r['event_days'],r['events'],f(r['mean_bps']),interval(r['nominal_95_mean_ci'])] for r in d['real_estimators']])
    lines += ['## 4. Drie nulscenario’s zonder voorspelbare toekomstige log-rendementen','',
        'Per scenario4.095 onafhankelijke experimenten van435 dagen en390 minuten. Masterseed20261023; per scenario een vooraf afgeleide eigen random stream. Geen gekozen gunstige seed, tussentijdse p-inspectie, uitbreiding of optional stopping. De Gaussian scenario’s gebruiken acht substeps per minuut om OHLC-records te construeren.','']
    for row in p['null_generators']:lines += [f"- **{NULLS[row['name']]}**: {row['description']}"]
    lines += ['', 'De Gaussian modellen zijn onafhankelijk in toekomstige richtingsinnovaties. Variabele volatiliteit kan voorspelbaar zijn zonder dat het conditionele gemiddelde van toekomstige log-rendementen van nul afwijkt. Het spiegelingsmodel houdt de echte barvormen/absolute bewegingen vast maar trekt onafhankelijke richtingsspiegelingen. Die vaste volledige templates zijn een conditioneel nulmodel, geen informatie die als handelsinput wordt gebruikt.','',
        'Het eerste scenario benadert geen ticks, spread of prijsrooster. Het tweede bewaart geen volledige regime-afhankelijkheid. Het derde veronderstelt spiegelingssymmetrie en is geen bewezen invariantie van NQ. De drie scenario’s worden allemaal gerapporteerd; er wordt geen best passend model uitgekozen.','',
        '### Uitsluitend volatiliteitskalibratie, geen fit op vervolgrendement','',
        f"Gepoolde minuut-SD: {f(d['null_calibration']['constant_minute_sigma_bps'])} bp. Dagvolatiliteitsschalen hebben tweede moment {f(d['null_calibration']['daily_scale_second_moment'],6)}. De13 klokfactoren volgen uit gemiddelde gekwadrateerde minuutrendementen per halfuur; geen optimalisatie op de record-outcomes.",'',
        '### Alle72 NQ-versus-nulmodelvergelijkingen','',
        'P2,5/P97,5 hieronder vormen een **nulmodel-predictie-interval voor een experiment van435 dagen**, geen betrouwbaarheidsinterval van het echte effect. Daarnaast staan nulmediaan, gemiddelde en Monte-Carlo-standaardfout van het nulgemiddelde.','',
        'Tweezijdige vergelijkingswaarde: `min(1, 2×min((1+#null≤observed)/4096, (1+#null≥observed)/4096))`. Eén globale Holm-correctie over3×2×3×4=72 vergelijkingen. De minimale ruwe tweezijdige p is2/4096. Deze waarden zijn modelafhankelijke controles, geen nieuwe onafhankelijke of exacte confirmatoire bewijzen: Gaussian kalibratie gebruikt eerder bekeken NQ-data en spiegelingsvaliditeit vereist de genoemde invariantie.','']
    table(lines,['Nulmodel','Record','Horizon','Meetwijze','NQ bp','Nulgem.','MC-SE nulgem.','Nulmediaan','NulP2,5','NulP97,5','NQ−nulmediaan','p modelcheck','p Holm72'],[
        [NULLS[r['generator']],r['side'],r['horizon'],LABELS[r['scheme']],f(r['observed_bps']),f(r['null_mean']),f(r['null_mc_se_mean']),
         f(r['null_median']),f(r['null_p025']),f(r['null_p975']),f(r['observed_minus_null_median']),f(r['p_value'],6),f(r['p_holm72'],6)] for r in t['comparisons']])
    lines += [f"Aantal modelcheck-vergelijkingen onder0,05 na Holm72: **{sig}/72**. Een afwijking verwerpt hoogstens een aspect van dat specifieke nulmodel; zij valideert geen handelsregel. Niet-verwerpen bewijst omgekeerd niet dat NQ exact uit het nulmodel komt.",'',
        'Volledige P05/P25/P50/P75/P95, null-eventaantallen en indicatieve Monte-Carlo-tailprecisie staan in JSON/CSV. Tailprecisie is onzekerheid door het eindige aantal simulaties, niet onzekerheid over de juistheid van het marktmodel.','',
        '### Expliciet: resultaten op de Monte-Carlo-resolutiegrens','']
    boundary=[r for r in d['comparisons'] if r['smaller_tail_count']==0]
    if boundary:
        table(lines,['Nulmodel','Record','Horizon','Meetwijze','Kleinere tailcount','Ruwe p','Holm72','Indicatieve95%-MC-tailprecisie (ruwe p)'],[
            [NULLS[r['generator']],r['side'],r['horizon'],LABELS[r['scheme']],r['smaller_tail_count'],f(r['p_value'],6),f(r['p_holm72'],6),interval(r['mc_precision_95'],6)] for r in boundary])
        lines += ['Bij nul extremere trekkingen is de p-waarde begrensd door de vooraf gekozen simulatieresolutie. De tailprecisie is een indicatief, naar tweezijdig geschaald Wilsoninterval voor de kleinere gesimuleerde staart, geen exact gezamenlijk p-interval en geen zekerheid over het overschrijden van de Holm-grens. Er zijn geen extra trekkingen gedaan om een gewenste beslissing te krijgen.','']
    else:lines += ['Geen vergelijking eindigt met nul trekkingen in de kleinere gesimuleerde staart.','']
    lines += ['## 5. Wat doet de oorspronkelijke nulwaardetoets op onvoorspelbare paden?','',
        'De eerste128 experimenten per scenario worden behandeld als afzonderlijke datasets. Elk krijgt dezelfde4.000 vijf-sessie bootstrapreplicaties als het vorige onderzoek. Twaalf recordtoetsen (twee sides×drie horizonten×twee meetwijzen) worden aangevuld met31 placeholders p=1, zodat de oorspronkelijke Holm43-familiegrootte behouden blijft. Dit is conservatief voor die niet-gesimuleerde toetsen; het reproduceert niet de gezamenlijke verdeling van alle oorspronkelijke43 markttoetsen.','',
        '**Dit heet bewust geen type-I-fout voor het daggemiddelde.** Onder een onvoorspelbaar koersproces kan het echte daggewogen gemiddelde niet-nul zijn. Een correcte toets op gemiddelde0 kan dan terecht verwerpen, terwijl de interpretatie “dus voorspelbare marktbeweging” onjuist is. We meten de frequentie van nulwaardeverwerpingen onder een generator zonder voorspelbaarheid.','']
    table(lines,['Nulmodel','Record','Horizon','Meetwijze','Panelen','Nominale verwerpingen','Fractie','95%Wilson','Holm43 verwerpingen','Fractie','95%Wilson'],[
        [NULLS[r['generator']],r['side'],r['horizon'],LABELS[r['scheme']],r['panels'],r['nominal_rejections'],f(r['nominal_rate']),
         interval(r['nominal_wilson_95']),r['holm43_rejections'],f(r['holm43_rate']),interval(r['holm43_wilson_95'])] for r in t['zero_calibration']])
    lines += ['Wilson-intervallen beschrijven de Monte-Carlo-onzekerheid over de gemeten fractie uit128 panelen; niet het onzekerheidsinterval van een NQ-effect.','',
              '### Panelen met minstens één record-verwerping','']
    table(lines,['Nulmodel','Procedure','Panelen met ≥1','Totaal','Fractie','95%Wilson'],[
        [NULLS[r['generator']],r['procedure'],r['panels_with_any_record_rejection'],r['panels'],f(r['rate']),interval(r['wilson_95'])] for r in t['family_calibration']])
    lines += ['## 6. Wat mogen we hier wel en niet uit concluderen?','',
        '- Het verschil tussen event- en dagweging is exact aan de count/outcome-covariantie gekoppeld. Dat is een verandering van estimand, niet automatisch een programmeerfout.',
        '- Het exacte muntworpvoorbeeld toont dat een niet-nul daggewogen recordeffect kan bestaan zonder voorspelbare toekomstige log-rendementen.',
        '- De nulscenario’s kwantificeren hoe groot dat verschijnsel binnen elk vooraf vastgelegd model kan worden. Zij identificeren geen universeel causaal percentage van een NQ-effect.',
        '- Een block-bootstrap bewaart afhankelijkheid binnen dagen; hij verwijdert geen toekomstafhankelijkheid uit een eindedagsgewicht. Holm corrigeert multipliciteit, niet een verkeerd geïnterpreteerde onderzoeksvraag.',
        '- De meetcontroles1/k en eerste record zijn geen nieuwe handelsvoorstellen. Geen kosten, brokerfills, uitvoerbaarheid of zelfstandige edge zijn getest.',
        '- De oorspronkelijke tabellen blijven geldig als beschrijvende schattingen van hun expliciet gedefinieerde gemiddelden. De significante daggemiddelden mogen niet als bewijs van een vooraf uitvoerbare mean-reversion-edge worden gelezen.',
        '- Alle435 dagen zijn al verbruikt. Deze audit levert geen nieuwe out-of-sample validatie op en heropent geen van de vier gearchiveerde modellen.','',
        '## 7. Methodologische bronnen en reikwijdte','',
        'Het algemene onderscheid tussen een gemiddelde over waarnemingen en een gemiddelde over clusters, wanneer clustergrootte met uitkomsten samenhangt, is behandeld door [Kahan et al., Estimands in cluster-randomized trials](https://academic.oup.com/ije/article/52/1/107/6644521). Die studie betreft klinische trials; de toepassing op eventdagen en de martingaalcontrole hierboven zijn eigen berekeningen, geen claim van die auteurs over NQ.','',
        'Voor eindige randomisatie-/Monte-Carlo-p-waarden en het vermijden van exact nul: [Phipson & Smyth](https://gksmyth.github.io/pubs/PermPValuesPreprint.pdf). De+1-regel maakt een verkeerd gespecificeerd of achteraf gekalibreerd nulmodel niet automatisch exact geldig.','',
        '## 8. Reproductie en bewijsbestanden','',
        '- Methode, code en inputhashes: `research/weighting-audit-lock.json`; definities: `research/weighting-audit-protocol.json`.',
        '- Uitvoering: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 .venv/bin/python -B -m scripts.weighting_audit`.',
        '- Afgeronde batch wordt niet overschreven. Alleen volledig afgeronde scenario-checkpoints met dezelfde methode-/codehash worden bij een onderbreking hergebruikt.',
        '- Verificatie zonder nieuwe simulaties of strategieën: `.venv/bin/python -B -m scripts.weighting_audit --verify`.',
        '- Publicatietabellen opnieuw opbouwen: `.venv/bin/python -B -m scripts.publish_weighting_audit`.',
        '- Tests: `.venv/bin/python -m pytest -q`; dashboard: `npm run typecheck` en `npm run build`.',
        '- De volledige experimentarrays en reële eventregels blijven privé. Alleen geaggregeerde verdelingen en controlegetallen worden gepubliceerd.',
        '',f"Definities SHA-256: `{d['protocol_sha256']}`.",f"Methode-/inputslot SHA-256: `{d['lock_sha256']}`.",
        f"Runtime: Python{d['runtime']['python']}, NumPy{d['runtime']['numpy']}, pandas{d['runtime']['pandas']}. Alle115 beschermde experimentbestanden ongewijzigd.",'']
    return '\n'.join(lines)


def publish():
    verify_completed();d=json.loads((OUT/'summary.json').read_text());t=additional_tables(d)
    report=render(d,t)
    (ROOT/'docs/WEIGHTING_AND_RECORD_SELECTION_AUDIT.md').write_text(report)
    (ROOT/'public/data/research-weighting-audit.md').write_text(report)
    dump(ROOT/'public/data/research-weighting-audit-tables.json',t)
    for name,rows in [('comparisons',t['comparisons']),('calibration',t['zero_calibration']),
                      ('family-calibration',t['family_calibration']),('observed',d['real_estimators']),
                      ('decomposition',d['weighting_decomposition']),('exact',d['exact_enumeration'])]:
        pd.DataFrame(rows).to_csv(ROOT/'public/data'/('research-weighting-audit.'+name+'.csv'),index=False)
    dump(ROOT/'research/weighting-audit-publication.json',dict(status='METHOD_AUDIT_COMPLETE_NO_NEW_MODEL',
        files_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'public/data').glob('research-weighting-audit*'))},
        report_sha256=sha(ROOT/'docs/WEIGHTING_AND_RECORD_SELECTION_AUDIT.md')))
    print(json.dumps(dict(report_lines=len(report.splitlines()),comparisons=len(t['comparisons']),
                         total_null_experiments=d['total_null_experiments'],new_strategy_signals=0),indent=2))


if __name__=='__main__':publish()
