"""Local aggregate report; no source loading, signal generation or deployment."""
import json
import pandas as pd

from scripts.afternoon_specificity import ROOT,OUT,verify,dump
from scripts.oos_preparation.adapter import sha


def f(x,d=3):return f'{x:.{d}f}'.replace('.',',')
def ci(x):return '['+f(x[0])+'; '+f(x[1])+']'


def run():
    verify();data=json.loads((OUT/'summary.json').read_text())
    dump(ROOT/'research/afternoon-specificity-results.json',data)
    pd.DataFrame(data['rows']).to_csv(ROOT/'research/afternoon-specificity-rows.csv',index=False,float_format='%.12g')
    tests=[]
    for r in data['contrasts']:
        tests.append({k:v for k,v in r.items() if k not in ('points','bps')}|dict(delta_points=r['points']['delta'],
            ci_points_low=r['points']['ci95'][0],ci_points_high=r['points']['ci95'][1],
            delta_logbps=r['bps']['delta'],ci_logbps_low=r['bps']['ci95'][0],ci_logbps_high=r['bps']['ci95'][1],
            p_raw_logbps=r['bps']['p_raw'],se_HAC5_logbps=r['bps']['se_HAC5'],se_CR1_logbps=r['bps']['se_CR1']))
    pd.DataFrame(tests).to_csv(ROOT/'research/afternoon-specificity-contrasts.csv',index=False,float_format='%.12g')
    v=data['verification'];names={'ALL':'Onvoorwaardelijk, opwaarts','UP':'Opwaartse context, voortzetting','DOWN':'Neerwaartse context, voortzetting'}
    lines=['# Specificiteit van het15:00-kwartier — vaste naburige vergelijking','',
        '## Afbakening','',
        'Uitsluitend14:30–14:45,14:45–15:00 en15:00–15:15 NY op dezelfde435 volledige RTH-dagen. De UP/DOWN-context wordt op ELK tijdstip opnieuw bepaald: laatste voltooide close ten opzichte van09:30open, en de tot dan opgebouwde RTH-range/vooraf bekende ATR14 in[0,5;1,2). Cohorten mogen daardoor verschillen. Geen latere15:00-selectie teruggeprojecteerd op eerdere kwartieren.','',
        'ALL en UP meten stijgingen. DOWN meet dalingen: positief betekent voortzetting omlaag. De benchmark voor DOWN is dus de negatieve van de onvoorwaardelijke opwaartse drift. Kosten zijn uitsluitend een vaste aftrek van1,225punt, geen entry/fill/stop/target-simulatie. Dezelfde aftrek aan beide kanten valt weg uit het verschil met de benchmark.','',
        'De bestaande15:00-bevinding is vóór de nieuwe uitkomsten apart vastgelegd in AFTERNOON_SPECIFICITY_PLAN.md en het gehashte protocol. Dit is een verkennende vervolgvergelijking op eerder bekeken data, geen onafhankelijke holdout.','',
        '## Volledige vergelijkingstabel','',
        '| Start NY | Groep/richting | Dagen | Gem.bruto pt | Med.bruto pt | Gem.na kosten pt | Med.na kosten pt | Voortzetting/stijging% | Positief na kosten% | Meerwaarde boven eigen benchmark pt |',
        '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in data['rows']:
        lines.append('| '+' | '.join([r['clock'],names[r['group']],str(r['days']),f(r['mean_gross_points']),f(r['median_gross_points']),f(r['mean_cost_only_points']),f(r['median_cost_only_points']),f(100*r['positive_fraction'],1),f(100*r['positive_after_cost_fraction'],1),f(r['premium_points'])])+' |')
    lines+=['','## Toetsen:15:00 minus elk eerder kwartier','',
        'Zes contrasten vergelijken de ruwe gemiddelden van ALL/UP/DOWN; vier vergelijken de UP/DOWN-meerwaarde boven de eigen directionele klokbenchmark. Dit onderscheid voorkomt dat een bijzonder sterk onvoorwaardelijk kwartier automatisch als contextspecifieke meerwaarde wordt behandeld.','',
        'De dag-influence scores van beide steekproeven worden VAN ELKAAR AFGETROKKEN vóór de variantie wordt berekend. Daarmee blijft de covariantie van gedeelde handelsdagen behouden. Primaire inferentie: dag-scores met Bartlett-HAC lags1–5 op de454 geplande kalenderdagen, conservatieve t-vrijheidsgraden, één Holm-correctie over de tien vooraf bepaalde tweezijdige log-bp-toetsen. Geen tweede punten-p-familie. Puntenintervallen zijn afzonderlijk berekend. Alle95%-intervallen zijn nominaal, niet simultaan.','',
        '| Type | Context | Vergelijking | Dagen15:00 / eerder | Gedeelde dagen | Verschil pt | 95%CI pt | Verschil log-bp | 95%CI log-bp | Ruwe p | Holm10 p |',
        '|---|---|---|---:|---:|---:|---|---:|---|---:|---:|']
    for r in data['contrasts']:
        lines.append('| '+' | '.join([r['kind'],r['group'],r['comparison'],f"{r['n15']} / {r['n_other']}",str(r['common_days']),f(r['points']['delta']),ci(r['points']['ci95']),f(r['bps']['delta']),ci(r['bps']['ci95']),f(r['bps']['p_raw'],6),f(r['p_Holm10'],6)])+' |')
    premiums=[r for r in data['contrasts'] if r['kind']=='context_premium']
    raw=[r for r in data['contrasts'] if r['kind']=='raw_mean']
    sigp=[r for r in premiums if r['p_Holm10']<.05]
    sigr=[r for r in raw if r['p_Holm10']<.05]
    lines+=['','## Feitelijk oordeel','',
        f"Van vier contextmeerwaarde-contrasten zijn er{len(sigp)} significant op5% na Holm10. Van zes ruwe-gemiddeldecontrasten zijn dat er{len(sigr)}. De volledige richting en omvang staan in de tabel; significant betekent hier niet automatisch dat15:00 beter is.",'',
        'In deze vaste run is uitsluitend het ruwe UP-gemiddelde van15:00 tegenover14:45 significant na Holm10: +12,498punten, ruwe log-bp-p=0,002604, Holm10-p=0,026037. De UP-meerwaarde boven de eigen klokbenchmark verschilt +8,385punten tegenover14:45, maar Holm10-p=0,082487. Tegenover14:30 bedraagt dit premieverschil +5,981punten, Holm10-p=0,218351. ALL en DOWN tonen geen gecorrigeerd significant tijdsverschil. De beschrijvende UP-voortzetting rond15:00 is dus niet hetzelfde als aangetoonde tijdstipspecifieke contextmeerwaarde.','',
        'Een niet-significant verschil bewijst geen gelijkwaardigheid en ook geen algemeen middagmomentum. Een significant verschil in ruwe groepsgemiddelden bewijst op zichzelf geen extra contextmeerwaarde. De cohorten veranderen tussen klokken: dit is geen causale behandelingseffectschatting op exact dezelfde geselecteerde dagen. Achteraf geselecteerd15:00 en al bekeken data blijven beperkingen, ook na de beperkte Holm10-correctie. Er is geen nieuwe handelsstrategie of promotie naar gevalideerde edge.','',
        '## Reproductie en bescherming','',
        f"{v['source_files']} bronbestanden op geregistreerde hashes gecontroleerd; {v['prefix_checks']} prefixcontroles en {v['future_mutation_checks']} mutatiecontroles geslaagd. De tweede verse bronherlading geeft byte-identieke meetledgers en identieke aggregaten. De oorspronkelijke167 UP-dagen,131 DOWN-dagen en435-daagse15:00-benchmark zijn exact gereproduceerd. Alle{v['protected_archive_files']} beschermde archiefbestanden blijven ongewijzigd.",'',
        'Verificatie: `.venv/bin/python -B -m scripts.afternoon_specificity --verify`. Ruwe prijzen en individuele meetregels blijven in de genegeerde lokale artifacts-map. Rapport en aggregaten zijn lokaal opgeslagen; geen GitHub-push of productiepublicatie uitgevoerd.','']
    report='\n'.join(lines);path=ROOT/'docs/AFTERNOON_SPECIFICITY_REPORT.md';path.write_text(report)
    paths=[path]+[ROOT/'research'/p for p in ('afternoon-specificity-results.json','afternoon-specificity-rows.csv','afternoon-specificity-contrasts.csv')]
    dump(ROOT/'research/afternoon-specificity-report-manifest.json',dict(status=data['status'],files_sha256={str(p.relative_to(ROOT)):sha(p) for p in paths}))
    print(json.dumps(dict(report=str(path),significant_context_premiums=len(sigp),significant_raw_contrasts=len(sigr)),indent=2))


if __name__=='__main__':run()
