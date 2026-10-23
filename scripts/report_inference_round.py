"""Report a locked method rejection honestly; no strategy/data scoring."""
import json

import numpy as np

from scripts.afternoon_inference_round import ROOT, OUT, PROTOCOL, sha, dump, verify_lock, partition
from scripts.register_historical_replication_window import WINDOW, PLAN, verify


def ar_diagnostic(length, rate, phi=.95):
    blocks, _, width=partition(length)
    # Exact population covariance of fixed Gaussian AR score blocks with iid
    # Bernoulli selection; no fitted NQ covariance or market price is used.
    c=np.zeros((8,8))
    for j,a in enumerate(blocks):
        for k,b in enumerate(blocks):
            distance=np.abs(a[:,None]-b[None,:])
            kernel=rate**2*phi**distance
            kernel[distance==0]=rate
            c[j,k]=kernel.mean()
    true=float(c.sum()/64)
    expected=float((np.trace(c)-c.sum()/8)/(8*7))
    return dict(weekdays=length, block_weekdays=width, phi=phi,
                adjacent_score_correlation=float(c[0,1]/np.sqrt(c[0,0]*c[1,1])),
                true_mean_score_variance=true,expected_group_SE_squared=expected,
                true_to_expected_variance=true/expected,
                caveat='Population Gaussian AR(.95) diagnostic with independent selection and no count gate; not exact rejection probability, no inference parameter tuning.')


def run():
    verify_lock();verify()
    r=json.loads(OUT.read_text());p=json.loads(PROTOCOL.read_text())
    w=json.loads(WINDOW.read_text());d=json.loads(PLAN.read_text())
    prior=json.loads((ROOT/'research/afternoon-feasibility-results.json').read_text())
    failures=[]
    for row in r['null_rows']:
        for s,item in enumerate(row['methods']['group_score_t']):
            for scope in ('unconditional','evaluable_only'):
                x=item[scope]
                if x['simultaneous_upper'] > .06:
                    failures.append(dict(phase=row['phase'],model=row['model'],weekdays=row['weekdays'],
                        null_scenario=['BOTH_ZERO','2M_PLUS4_15M_ZERO','2M_ZERO_15M_PLUS4'][s],
                        summary=scope,rate=x['rate'],simultaneous_upper=x['simultaneous_upper'],
                        evaluable=item['evaluable'],replications=item['total']))
    failures.sort(key=lambda x:x['simultaneous_upper'],reverse=True)
    diag=[ar_diagnostic(length,prior['selection_rate_scheduled']) for length in p['lengths_weekdays']]
    summary=dict(status=r['status'],failed_simultaneous_bounds=len(failures),failures=failures,
                 nominal_alpha=.05,screening_tolerance=.06,calibration_passed=r['calibration_passed'],
                 maximum_upper_bound=r['max_simultaneous_upper'],calendar_diagnostics=diag,
                 synthetic_panels=sum(x['repetitions'] for x in r['null_rows']+r['negative_control']),
                 fixed_window=[w['start'],w['end']],downloads=d['requested_files'],contracts=d['contracts'],
                 recommendation='NO_BULK_COLLECTION_OR_OUTCOME_RELEASE_WHILE_METHOD_NOT_CLEARED',
                 new_market_outcomes_read=False,source_results_sha256=sha(OUT))
    dump(ROOT/'research/afternoon-method-round-summary.json',summary)
    lines=['# Methoderonde en vastlegging van het testvenster','',
        '22 oktober 2026. Alleen stappen 1 en 2 uitgevoerd. Geen nieuwe marktuitkomsten, cohortselectie, backtest, downloads, aankoop, GitHub-push of Vercel-publicatie. Baseline v0.9, vNext, kandidaat v2 en eerdere rapporten zijn ongewijzigd.','',
        '## Besluit','',
        f"**{r['status']}**. De vooraf gekozen alternatieve meetlat haalt de vastgelegde vrijgave-eis niet. Stap 1 is als methoderonde uitgevoerd, maar het onderliggende betrouwbaarheidsprobleem is **niet opgelost**. Er is geen vervangende methode goedgekeurd of als actuele kandidaat ingesteld.",'',
        f"Het venster **{w['start']} t/m {w['end']}** en de bronacquisitie zijn vóór inzage van marktuitkomsten vergrendeld. Dit is historische replicatie, geen bewezen volledig onaangeraakte forwardproef. De lijst bevat **{d['requested_files']} CSV’s / {d['contracts']} contracten**, inclusief opwarming. **Nog niet de hele lijst verzamelen en geen eindtoets draaien** zolang de meetlat niet is vrijgegeven.",'',
        '## 1. Wat vóór de simulatie vastlag','',
        '- Eén alternatieve methode: acht even lange chronologische kalenderblokken met telkens twintig weekdagposities tussenruimte. Geen zoektocht over laglengtes, groepen, gaps, rendementen of strategieparameters.',
        '- Twee tweezijdige horizons, dezelfde selectie en kosten, dezelfde Holm2-familie met alpha 0,05. Geen primaire/secundaire inhoudelijke gate. De nieuwe steekproefpartitionering is een expliciet voorstel voor een afzonderlijk inferentie-addendum, geen stille wijziging van v2.',
        '- Per blok de nulmoment-score A=sum(I×netto punten)/bloklengte. Niet-geselecteerde kalenderposities leveren een nul aan de invloedsscore, geen verzonnen geselecteerde nultrade. De getoonde conditionele gemiddelde punten blijven sum(I×netto punten)/sum(I), niet een achteraf dag- of blokgewogen gemiddelde.',
        '- De p-waarde gebruikt t op de acht nulmoment-scores, met zeven vrijheidsgraden. De intervalfunctie inverteert de scoretoets via A−mu×B en geeft onbegrensde/disjuncte sets als zodanig terug. Geen kunstmatig eindige intervallen.',
        '- Minstens acht geselecteerde dagen per blok en 120 totaal. Onvoldoende informatie geeft beide p-waarden 1 en DATA_INSUFFICIENT; kalender niet comprimeren of verlengen.',
        '- Elf nulmodellen: iid normaal, t5, positieve/negatieve scheefheid, MA(19), AR(0,6/0,9/0,95), volatiliteitsregimes, persistente selectie en MA(19) met persistente selectie. Daarnaast één expliciete niet-mengende negatieve controle buiten de geldigheidsaannamen.',
        '- Twee vooraf gekozen seeds, 10.000 panels per model/kalenderlengte/seed. Drie lengtes: 500, 783 en 1.000 weekdagposities. Gezamenlijke nul én twee deel-nullen: een horizon met +4 hypothetische netto punten, de andere werkelijk nul.',
        '- Alle echte-nulverwerpingen tellen mee, beide tekens. Zowel onvoorwaardelijk als onder panels die de informatiepoort halen. Gelijktijdige eenzijdige Clopper–Pearson-bovengrenzen over alle 396 toetscellen: totale Monte-Carlo-foutkans 0,05 via Bonferroni. Elke bovengrens moest hoogstens 6% zijn. Die 6% was een vooraf vastgelegde numerieke screentolerantie, géén wijziging van de nominale alpha van 5%.','',
        f"Protocol en implementatie zijn vóór de eerste simulatie gehasht. Totaal **{summary['synthetic_panels']:,} synthetische panels**. Invoer: uitsluitend al bestaande samenvattingsgetallen voor selectiefrequentie, SD en correlatie; geen ruwe CSV of nieuwe eventledger numeriek gelezen. Een tweede seed is een afzonderlijke Monte-Carlo-controle, niet een externe onafhankelijke onderzoeker of een byte-identieke volledige reproductierun.",'',
        'De methode is geïnspireerd door [Ibragimov en Müller (2010)](https://www.princeton.edu/~umueller/tstat.pdf). Hun groepsbenadering vereist voldoende onafhankelijke, ongeveer Gaussische groepsinformatie. Dat vereist aannamen over de gegevens; twintig dagen tussenruimte bewijzen die onafhankelijkheid niet. De hier gebruikte nulmoment-implementatie is een eigen toepassing, geen universele eindige-steekproefgarantie uit het artikel.','',
        '## 2. Resultaat van de vooraf vastgelegde vrijgavepoort','',
        f"**{len(failures)} van de 396 bovengrenzen overschrijden 6%.** Grootste bovengrens: **{100*r['max_simultaneous_upper']:.2f}%**. Dat is een onzekerheidsbovengrens, niet de gemeten foutkans zelf. Sommige afwijzingen van de screeneis komen ook door onvoldoende Monte-Carlo-precisie in de kleine evaluabele subgroep, niet alleen door een verhoogde puntschatting.",'',
        '| Seedfase | Model | Kalender | Nulscenario | Populatie panels | Gemeten fout % | Gelijktijdige bovenkant % |',
        '|---|---|---:|---|---|---:|---:|']
    for x in failures[:12]:
        lines.append(f"| {x['phase']} | {x['model']} | {x['weekdays']} | {x['null_scenario']} | {x['summary']} ({x['evaluable']}/{x['replications']} evaluabel) | {100*x['rate']:.2f} | {100*x['simultaneous_upper']:.2f} |")
    lines += ['', 'Ook de vooraf gekozen lengte van 783 weekdagposities haalt de eis niet. Daarom wordt niet achteraf de falende 500-dagencontrole weggelaten, een langere gap gekozen of de tolerantie verruimd. Het resultaat bewijst niet dat iedere bloktoets fout is of dat de marktobservatie afwezig is. Het bewijst dat dit concrete voorstel onder de vooraf gekozen meetlat niet is goedgekeurd.','',
        '### Vergelijking bij het geplande driejaarsvenster','',
        'Hieronder de gezamenlijke nul, onvoorwaardelijke familieverwerping in enige richting. Beide seeds staan apart. De oude HAC5 staat alleen als referentie op precies dezelfde gescoorde kalender, niet als gunstiger alternatief om te kiezen.','',
        '| Model | Fase 1: nieuw % | Fase 2: nieuw % | Fase 1: HAC5 % | Fase 2: HAC5 % |','|---|---:|---:|---:|---:|']
    for model in p['models']:
        rows=[x for x in r['null_rows'] if x['model']==model and x['weekdays']==783]
        values=[100*x['methods'][method][0]['unconditional']['rate'] for method in ('group_score_t','frozen_HAC5') for x in rows]
        lines.append('| '+model+' | '+' | '.join(f'{x:.2f}' for x in values)+' |')
    lines += ['', '### Waarom de AR-stresstest nog restafhankelijkheid heeft','',
        'Voor het vooraf gekozen Gaussische AR(0,95)-model is de populatiecovariantie van de vaste scoreblokken analytisch uit te rekenen. Dit is geen geschatte NQ-autocorrelatie. De twintig-dagen-gap maakt naburige blokken hier niet onafhankelijk.','',
        '| Kalender | Bloklengte | Correlatie naburige scores | Ware variantie / verwachte groeps-SE² |', '|---:|---:|---:|---:|']
    for x in diag: lines.append(f"| {x['weekdays']} | {x['block_weekdays']} | {x['adjacent_score_correlation']:.4f} | {x['true_to_expected_variance']:.4f} |")
    lines += ['', 'Deze verhouding is geen exacte verklaring van de eindige t-verwerpingskans of de selectie-informatiepoort. Ze toont wel een concrete onderschattingsroute in het model. Geen nieuwe gap of groepsaantal is op dit resultaat uitgeprobeerd.','',
        '### Negatieve controle: gedeelde factor over het hele panel','',
        '| Kalender | Fase 1: fout % | Fase 2: fout % |','|---:|---:|---:|']
    for length in p['lengths_weekdays']:
        rows=[x for x in r['negative_control'] if x['weekdays']==length]
        values=[100*x['methods']['group_score_t'][0]['unconditional']['rate'] for x in rows]
        lines.append(f"| {length} | {values[0]:.2f} | {values[1]:.2f} |")
    lines += ['', 'Deze expliciet niet-mengende controle valt buiten de aannamen. Ze laat zien waarom een geslaagde beperkte simulatiesuite nooit universele bescherming tegen elke gezamenlijke marktfactor zou bewijzen.','',
        '## 3. Power: alleen hypothetische planning','',
        'Alle onderstaande effecten zijn al netto na het bevroren kostenmodel. De p-waarden zijn niet op nieuwe marktgegevens berekend. Omdat de kalibratie faalt, zijn dit slechts simulatie-uitkomsten van het afgekeurde voorstel, geen gecertificeerde onderscheidingskansen.','',
        '| Nulruismodel | SD-factor | Effect 2m | Effect 15m | Positief familiesucces % |','|---|---:|---:|---:|---:|']
    for x in r['power_rows']:
        if x['effect_net_points'] not in ([4,0],[0,4],[4,4]): continue
        lines.append(f"| {x['model']} | {x['sigma_multiplier']:.1f} | {x['effect_net_points'][0]} | {x['effect_net_points'][1]} | {100*x['family_positive']['positive_rate']:.2f} |")
    lines += ['', 'Alle +2/+4/+6-scenario’s, beide SD-factoren, nullen, deel-nullen en evaluabele fracties staan onverkort in JSON. Een driejaarskalender geeft niet onder elke afhankelijkheid 80% power. Er is geen venster verlengd om een mooier powergetal te halen.','',
        '## 4. Wat nu wel vaststaat en welke bestanden nodig zijn','',
        '- Vast historisch venster: **2 januari 2019–31 december 2021**, alleen voor een later afzonderlijk vrijgegeven replicatie. Opwarming **19 november 2018–1 januari 2019**. Geen overlap met de 435 ontdekkingsdagen of de NQH24-pilot.',
        '- Eerdere aangetroffen intradaylabels beginnen pas in 2022; de eerdere minuutreeks eind-2022. Dag/week/maanddata van oudere jaren waren al bekeken. Daarom geen claim van absoluut nul eerdere inzage of prospectieve onafhankelijkheid. Bron-/toegangscontrole blijft een vrijgavevoorwaarde.',
        '- 783 weekdagposities zijn geen 783 CME-sessies of eligible dagen. De nieuwe kandidaatmeetlat zou 640 weekdagposities scoren en 143 als tussenruimte/staart reserveren. Echte kwaliteits- en eventaantallen zijn nog onbekend.',
        '- Bronacquisitie: **103 onbewerkte 1m-contractexports**, over **14 contracten**. De volledige lijst staat in [NQ_HISTORICAL_DOWNLOAD_LIST.md](NQ_HISTORICAL_DOWNLOAD_LIST.md). Geen Nearby, geen back-adjusted export, geen total-volume-aggregatie. Zondagen zijn bewust in de blokken opgenomen.',
        '- Contracten: NQZ18 (opwarming); NQH19/M19/U19/Z19; NQH20/M20/U20/Z20; NQH21/M21/U21/Z21; NQH22 uitsluitend voor de december-2021-rollover tot 31 december 2021.',
        '- **Mijn huidige advies: nog geen bulkdownload.** De lijst is een vastgelegde latere behoefte, geen verzoek om nu 103 downloads af te werken. Er is in deze ronde geen goedgekeurde nieuwe meetlat ontstaan.',
        '- Geen nieuwe strategie, filters, stop/target, order, betaalde bron, accountwijziging of automatische verlenging. De empirische uitvoerbaarheid blijft onbewezen.','',
        '## Verificatie en reproduceerbaarheid','',
        '`python -m scripts.afternoon_inference_round prepare` heeft de methodestand vóór simulatie vergrendeld. `python -m scripts.afternoon_inference_round run` reproduceert uitsluitend de synthetische ronde. `python -m scripts.register_historical_replication_window --verify` controleert de datum-/downloadlock. Geen van deze opdrachten voert de nieuwe markthypothese uit.', '',
        f"{r['preserved_files']} bestaande bestanden blijven byte-identiek ten opzichte van de vóór deze ronde vastgelegde hashes. Nieuwe bestanden staan alleen lokaal; de huidige kandidaatpointer blijft v2 en `independent_test_released=false`. De test-/eindverificatie staat in `research/afternoon-method-round-verification.json`.", '']
    (ROOT/'docs/AFTERNOON_METHOD_ROUND_REPORT.md').write_text('\n'.join(lines))
    verify_lock();verify()
    print(json.dumps({k:summary[k] for k in ('status','failed_simultaneous_bounds','synthetic_panels','downloads','contracts')}))


if __name__=='__main__': run()
