"""Deterministic aggregate-only publication; does not select events or score."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.causal_map.__main__ import ROOT, OUT, clean, dump, verify
from scripts.oos_preparation.adapter import sha


def f(x,digits=3):
    return '—' if x is None else f'{x:.{digits}f}'.replace('.',',')


def interval(x):
    return '—' if x is None else '['+f(x[0])+'; '+f(x[1])+']'


def csv(path,records):
    pd.DataFrame(records).to_csv(path,index=False,float_format='%.12g')


def publish():
    checked=verify();data=json.loads((OUT/'summary.json').read_text())
    rows=sorted(data['rows'],key=lambda r:r['rank']);v=data['verification'];cal=data['calibration']
    aggregate=ROOT/'public/data/research-causal-map.json'
    clarification=dict(kind='TEXT_ONLY_ERRATUM_NO_METHOD_OR_RESULTS_CHANGE',
        field='protocol.quarters',original='including one-day2024Q4',
        correction='The fixed435-day sample contains TWO dates in2024Q4:2024-12-30 and2024-12-31. The original method/code/input lock and results are preserved. All quarter event counts use actual source dates, not this mistaken prose.',
        selection_thresholds_horizons_statistics_changed=False)
    dump(aggregate,dict(data,publication_clarification=clarification))
    dump(ROOT/'research/causal-map-clarifications.json',clarification)
    flat=[];quarters=[]
    for row in rows:
        r={k:x for k,x in row.items() if k not in ('quarters','inference_bps','ci95_points','hac_ci95_points')}
        inf=row['inference_bps']
        r.update(p_raw=inf['p'],p_hac_raw=inf['hac_p'],cluster_status=inf['status'],cluster_se_bps=inf['se'],hac_se_bps=inf['hac_se'])
        for key,ci in [('cluster_ci_bps',inf['ci95']),('hac_ci_bps',inf['hac_ci95']),('cluster_ci_points',row['ci95_points']),('hac_ci_points',row['hac_ci95_points'])]:
            r[key+'_low']=ci[0] if ci else None;r[key+'_high']=ci[1] if ci else None
        flat.append(r)
        quarters.extend(dict(mechanism=row['id'],horizon=row['horizon'],**q) for q in row['quarters'])
    base=ROOT/'public/data'
    csv(base/'research-causal-map.ranking.csv',flat)
    csv(base/'research-causal-map.quarters.csv',quarters)
    csv(base/'research-causal-map.calibration.csv',cal['rows'])
    eligible=json.loads((OUT/'eligibility.json').read_text())
    # Day quality/availability only; no raw levels, prices or private ledgers.
    csv(base/'research-causal-map.eligibility.csv',eligible)
    significant=[r for r in rows if r['ranking_p']<.05 and r['inference_bps']['status']=='OK']
    clusters=[r for r in rows if r['inference_bps']['status']=='OK']
    bycategory={k:dict(cells=sum(r['category']==k for r in rows),
        tested_cells=sum(r['category']==k for r in clusters),joint_significant_cells=sum(r['category']==k for r in significant)) for k in 'ABCD'}
    nominal=sorted(clusters,key=lambda r:r['inference_bps']['p'])
    all_tied=all(r['p_holm256']==1 and r['hac_p_holm256']==1 for r in rows)
    lines=['# Causale marktmechanisme-kaart NQ — verkennende scan', '',
      '## Conclusie en bewijsstatus', '',
      f"{v['complete_RTH_days']} volledige RTH-dagen, {v['source_files']} gehashte bronbestanden, {v['selected_events']} geselecteerde events en {v['event_horizon_rows']} event/horizonregels. Alle32 vooraf vastgelegde mechanismen en128 cellen staan hieronder, ook lege of te kleine groepen.", '',
      f"{len(significant)} van128 cellen halen5% met BEIDE onzekerheidsmethoden na één globale Holm-correctie over256 toetsen. {len(clusters)} cellen hebben minstens20 afzonderlijke eventdagen. Dat is een verkennende uitkomst op reeds bekeken data, geen onafhankelijke bevestiging of gevalideerde handelsedge.", '',
      'Causaal betekent hier uitsluitend dat eventselectie, richting, ankers en gewichten point-in-time zijn. Het betekent niet dat stop-pools, institutionele handel of MOC-orders als oorzaak geïdentificeerd zijn. De economische categorieën zijn hypotheses over prijsreacties, geen waargenomen orderstromen.', '',
      'De ranglijst is vooraf bepaald: maximum van de twee gecorrigeerde p-waarden, dan absolute gemiddelde log-bp. Een negatieve uitkomst is niet naar positief omgedraaid na de berekening. Kleine groepen met minder dan20 eventdagen krijgen géén p-waarde of interval; hun p=1-placeholder blijft in de correctiefamilie.', '',
      '## Dekking en causale controles', '',
      f"{v['future_prefix_checks']} actuele-data-prefixcontroles; {v['recomputed_context_checks']} opnieuw opgebouwde contextcontroles rond rollovers/historie-afkappingen. Een tweede volledige event/horizonextractie en statistiekberekening geeft byte-identieke ledgers en identieke aggregaten. Strategie-aanroepen zijn tijdens de bronroute geblokkeerd.", '',
      '| Context beschikbaar vóór de meting | Dagen |','|---|---:|']
    for label,key in [('ATR14','ATR_ready'),('Vorige RTH-dag volledig','PD_ready'),('Overnight18:00–09:30 volledig','overnight_complete'),('Minstens één1m-volumehistorie van20 sessies','days_any_volume1_reference'),('Alle390 volumeklokken met20 sessies','days_all_volume1_reference'),('Minstens één5m-volumehistorie','days_any_volume5_reference')]:
        lines.append(f"| {label} | {data['eligibility_summary'][key]} |")
    lines += ['', 'De435 dagen zijn het vaste volledige-RTH-universum uit de vorige kwaliteitscontrole. Niet elke dag heeft iedere context. Ontbrekende ATR, prior range, overnightminuten of20-sessie-volumeklokken worden niet ingevuld of vervangen door gunstige subsets. Feestdagen/vroege sluitingen blijven ontbrekende volumeklokken geven waar geen reguliere RTH-bars bestaan.', '',
      '## Vooraf vastgelegde mechanismen', '',
      '- A: eerste bereik van PDH, PDL, ONH of ONL in RTH, inclusief openen/overspringen voorbij het niveau. De eerste bevestigingsclose bepaalt ACCEPT versus REJECT. ACCEPT meet naar buiten, REJECT naar binnen. Dit is geen achteraf ingedeelde winnaar/verliezer. Het is ook niet noodzakelijk een fysiek verhandelde touch: een gap over het niveau telt als bereik.',
      '- B: strikt openingsgap boven PDH of onder PDL; daarnaast abs(09:30open − vorigeRTHclose)/ATR14≥1. Meting om09:30 en10:00, steeds met de oorspronkelijke gap/overnight-richting. De extreme overnight-verplaatsing is netto verplaatsing vanaf vorigeRTHclose, niet overnight high-low range.',
      '- C: om09:30 is geen RTH-dagrichting bekend. Daar gebruiken we uitsluitend18:00–09:30richting en range. Om15:00 gebruiken we uitsluitend09:30open tot14:59close en de tot dan waargenomen RTH-range. SMALL<0,5ATR, MID[0,5;1,2), LARGE≥1,2. Rendement steeds met de bekende richting. Nulrichting wordt niet geclassificeerd.',
      '- D: volume van een voltooide1m- of uitgelijnde5m-bar boven het empirische95e percentiel van precies20 voorgaande geplande sessies op die klok, plus een nieuw strikt RTH-extreem. RVOL=current/mean(previous20). Alle20 klokobservaties vereist; de huidige bar telt niet in de referentie. Beide extremen in één bar mogen beide labels geven. Rendement naar het nieuwe extreem: negatief wijst op omkeer.', '',
      'Deze drempels zijn vóór de uitkomsten vastgelegd, niet op deze scan geoptimaliseerd. Met20 referentiedagen is een95e percentiel een ruwe volumestaartschatting; het betekent niet dat exact5% van toekomstige bars wordt geselecteerd.', '',
      '## Ankers, horizons en excursies', '',
      'Een bar met starttijd09:44 is pas09:45 bekend. Vervolgrendement begint op die close; MFE/MAE gebruiken uitsluitend bars vanaf09:45. Om09:30 is het anker de openingsprijs; om10:00 de09:59close; om15:00 de14:59close. Dit zijn onderzoeksankers, geen bewezen uitvoerbare fills.', '',
      '15m/30m/60m betekenen exact zoveel verstreken minuten; horizons na16:00 worden ontbrekend, nooit ingekort. RTH-slot is de15:59barclose, niet settlement of een beursveilingprijs. Vanaf15:00 zijn60m en RTH-slot identiek; beide gevraagde cellen blijven conservatief in de volledige correctiefamilie. Een event dat pas16:00 bevestigd is telt in het eventregister maar heeft geen vervolgobservatie.', '',
      'MFE/MAE zijn maximale gunstige/ongunstige OHLC-excursies in de vooraf gekozen richting. Ratio=gemiddelde MFE/gemiddelde MAE, niet het instabiele gemiddelde van individuele ratios met mogelijke nulnoemers. Daarnaast publiceren we medianen en de mediane begrensde balans(MFE−MAE)/(MFE+MAE). Hoogste en laagste prijs hebben geen bekende volgorde binnen een minuut; de ratio is geen winstfactor of bewijs dat beide prijzen verhandelbaar zijn.', '',
      '## Onzekerheid, toetsen en interpretatie', '',
      'Puntenschatting=gepoold gemiddelde per event, zonder achteraf gelijke daggewichten. Voor CR1 worden residuen eerst per handelsdag GESOMMEERD en pas dan gekwadrateerd. Standaardfout=sqrt(G/(G−1)×Σdag(score²))/N; t-vrijheidsgraden=G−1 eventdagen. Daardoor creëert het dupliceren van events binnen dezelfde dag geen extra onafhankelijke steekproef.', '',
      'Een tweede methode gebruikt dezelfde dag-scores met Bartlett-HAC, vaste lags1–5, om samenhang tussen sessies te onderzoeken. Beide tweezijdige p-waarden toetsen een gemiddeld directioneel log-rendement van nul. Eén Holm-familie bevat32×4×2=256 toetsen, inclusief ontbrekende cellen als p=1. Puntenintervallen zijn apart berekend, niet door een gemiddelde prijs omgerekend. Intervallen zijn nominaal95%, niet simultaan95%. Kwartalen, medianen, positieve fracties en excursies zijn beschrijvend en krijgen geen extra significantieclaims.', '',
      'CR1 veronderstelt onafhankelijke dagclusters; HAC is een beperkte asymptotische robuustheidscontrole, geen garantie tegen elke regimestructuur. Verschillen met nul bewijzen ook niet dat het effect extra voorspellende informatie geeft boven de onvoorwaardelijke drift op hetzelfde tijdstip. Dat onderscheid vereist een afzonderlijk vastgelegde vergelijking, niet achteraf de gunstigste baseline kiezen.', '',
      '## Kalibratie zonder voorspelbare toekomstige log-rendementen', '',
      f"Vooraf128 panelen van120 synthetische sessies, seed20261024, onafhankelijke Gaussian log-innovaties met8 substeps/minuut en onafhankelijke overnight/volume-innovaties. Exact dezelfde selectie, horizons en CR1/HAC/Holm. {cal['panels_any_joint_rejection']}/128 panelen bevatten een cel die na de gezamenlijke correctie met beide methoden verwerpt. Alle celdekkingen en afwijzingsaantallen staan in de kalibratie-CSV, inclusief groepen met weinig of geen geldige panelen.", '',
      'Een eindige kalibratie is geen exact bewijs van5% dekking in echte NQ-data. Zeldzame contextgroepen kunnen in dit eenvoudige nulscenario nauwelijks voorkomen. Ze zijn daarmee niet gevalideerd. Verwachte log-innovaties zijn nul; rekenkundige puntprijsveranderingen hebben een Jensen-effect en worden niet als nulmartingaal geclaimd.', '',
      '## Volledige ranglijst', '',
      ('Alle gecorrigeerde p-waarden zijn hier1. De vooraf vastgelegde rangvolgorde wordt daardoor uitsluitend door effectgrootte bepaald, inclusief kleine groepen. Rang1 is dus nadrukkelijk NIET de sterkste statistische aanwijzing. De hieronder genoemde kleinste ruwe p-waarden zijn alleen een beschrijvende leeswijzer naast de volledige, ongewijzigde ranglijst.' if all_tied else 'Lees rangorde samen met steekproefomvang en beide gecorrigeerde p-waarden.'), '',
      'Positief%=aandeel positieve bruto vervolgrendementen in de vooraf bepaalde richting, geen netto handelswinrate. Alle gemiddelden en excursies zijn vóór commissie, spread, slippage en eventuele fill-latency.', '',
      '| Rang | Mechanisme | Horizon | Events | Dagen | Gem.pt | Med.pt | Gem.bp | Med.bp | Positief% | CR195%bp | pCR1 | pHolm256 | pHAC | pHACHolm256 | MFE/MAE |',
      '|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|']
    for r in rows:
        inf=r['inference_bps']
        lines.append('| '+' | '.join([str(r['rank']),r['id'],r['horizon'],str(r['events']),str(r['days']),f(r['mean_points']),f(r['median_points']),f(r['mean_bps']),f(r['median_bps']),f(100*r['positive_fraction'] if r['positive_fraction'] is not None else None,1),interval(inf['ci95']),f(inf['p'],6),f(r['p_holm256'],6),f(inf['hac_p'],6),f(r['hac_p_holm256'],6),f(r['mfe_mae_ratio'])])+' |')
    lines += ['', '### Beschrijvende leeswijzer: laagste ruwe CR1-p, niet geselecteerd bewijs', '']
    for r in nominal[:3]:
        qs=[q for q in r['quarters'] if q['events']]
        positives=sum(q['mean_bps']>0 for q in qs)
        lines.append(f"- {r['id']} / {r['horizon']}: {r['events']} events, {r['days']} dagen; gemiddeld{f(r['mean_points'])}pt ({f(r['mean_bps'])}bp), mediaan{f(r['median_points'])}pt; positief{f(100*r['positive_fraction'],1)}%; CR195%bp{interval(r['inference_bps']['ci95'])}; ruwp{f(r['inference_bps']['p'],6)}, Holm256{f(r['p_holm256'],6)}; MFE/MAE{f(r['mfe_mae_ratio'])}; {positives}/{len(qs)} waargenomen kwartalen positief. Dit is geen nieuwe selectie- of handelsregel.")
    if all_tied:
        lines += ['', 'Het kleine15:00-vervolgeffect op reeds opwaartse dagen met een middengrote RTH-range heeft de laagste ruwe p. Volumeschokken op5m-highs en neerwaartse smalle-overnightcontext zijn andere nominale voorbeelden. Geen daarvan is na de volledige scan statistisch onderscheiden van nul. Extreme overnight-nettoverplaatsingen≥1ATR tellen slechts10 up- en13 down-dagen: grote zichtbare gemiddelden in die groepen zijn onvoldoende onderbouwd. PDH/PDL/ONH/ONL leveren in deze definities evenmin een gecorrigeerd aantoonbare asymmetrie op.', '']
    lines += ['', '## Kwartaalstabiliteit — alle kwartalen, geen geselecteerde gunstige perioden', '',
      'Iedere cel publiceert alle8 kalenderkwartalen, inclusief de twee datums30–31december2024 in het korte startkwartaal. Een streep betekent geen events, geen nulresultaat. De CSV bevat per kwartaal ook events, unieke dagen, medianen, positieve fracties en excursies. Deze tabel toont gemiddelde log-bp met eventaantal tussen haakjes; een kwartaal is geen nieuwe holdout.', '',
      '| Mechanisme | Horizon | '+' | '.join(q['quarter'] for q in rows[0]['quarters'])+' |',
      '|---|---|'+'---:|'*len(rows[0]['quarters'])]
    for r in rows:
        lines.append('| '+r['id']+' | '+r['horizon']+' | '+' | '.join(f(q['mean_bps'])+' ('+str(q['events'])+')' for q in r['quarters'])+' |')
    lines += ['', '## Replicatie en bescherming', '',
      f"Byte-identieke event/horizonreplay SHA-256: `{v['ledger_sha256']}`. {v['protected_archive_files']} beschermde experimentbestanden en alle eerdere ruwe-markt- en wegingsauditpublicaties blijven ongewijzigd. Geen simulator-, entry-, stop-, target- of netto-P&L-aanroepen. Ruwe CSV’s en eventledgers blijven uitsluitend privé.", '',
      'Tekstuele erratum: het vóór de run vergrendelde protocol noemt2024Q4 ten onrechte een one-day-kwartaal. Het bronuniversum bevat30én31december2024. De daadwerkelijke eventberekeningen en kwartaalindeling gebruiken beide datums correct. De oorspronkelijke lock blijft intact; de verduidelijking is apart vastgelegd in research/causal-map-clarifications.json. Geen selectieregel, drempel of uitkomst is gewijzigd.', '',
      'Reproduceerbare route: `.venv/bin/python -B -m scripts.causal_map --verify` controleert de afgesloten run zonder opnieuw te scannen. De broncode ondersteunt de volledige vaste batch wanneer de afzonderlijke outputmap nog niet bestaat. `python -m scripts.publish_causal_map` publiceert uitsluitend de geverifieerde aggregaten. De gesloten run weigert uitkomstgestuurde herhalingen.', '',
      '## Methodologische bronnen', '',
      '- Clusterafhankelijke inferentie: [Cameron & Miller, A Practitioner’s Guide to Cluster-Robust Inference](https://old.econ.ucdavis.edu/research/papers.html). Onderbouwing voor afhankelijkheid binnen clusters; geen bewijs voor een NQ-effect.',
      '- [Nasdaq Opening and Closing Crosses](https://www.nasdaqtrader.com/trader.aspx?id=openclose): opening/closing auctioncontext van aandelen. Onze NQ-minuutbars bevatten geen NOII/veilingorderstromen; een15:00-tijdvenster mag daarom niet als bewezen MOC-flow worden benoemd.', '']
    report='\n'.join(lines)
    for path in [ROOT/'docs/CAUSAL_MARKET_MECHANISM_MAP.md',base/'research-causal-map.md']:
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(report)
    files=[aggregate,base/'research-causal-map.ranking.csv',base/'research-causal-map.quarters.csv',base/'research-causal-map.calibration.csv',base/'research-causal-map.eligibility.csv',base/'research-causal-map.md']
    dump(ROOT/'research/causal-map-publication.json',dict(status=data['status'],files_sha256={str(p.relative_to(ROOT)):sha(p) for p in files},category_summary=bycategory,
        joint_significant_cells=[dict(mechanism=r['id'],horizon=r['horizon'],ranking_p=r['ranking_p']) for r in significant]))
    print(json.dumps(dict(cells=len(rows),tested=len(clusters),joint_significant=len(significant),categories=bycategory),indent=2))


if __name__=='__main__':publish()
