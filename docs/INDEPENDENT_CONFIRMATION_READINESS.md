# Onafhankelijke bevestiging: broncontrole en steekproefplanning

## Uitgevoerd

Lokale technische bronvergelijking op vooraf vastgelegde bestaande pilotbestanden, plus reproductie van waarnemingstellingen. Geen nieuwe strategie-, cohort- of P&L-run, aankoop, download, Git-push of productiepublicatie. Kandidaat v2 blijft byte-identiek.

## Wat telt als één van de120?

Eén unieke dag met de bevroren14:30-UP-selectie, geldige vooraf bekendeATR14 en geldige gezamenlijke horizondata. De2m- en15m-uitkomst zijn twee gekoppelde toetsen, niet twee waarnemingen. Alleen geselecteerde dagen binnen de8 vooraf vastgelegde meetblokken tellen voor de conservatieve informatiepoort. Tussen de blokken blijven7×20 weekdagen ongescoord; ook de vaste reststaart telt niet. Niet-geselecteerde dagen krijgen geen verzonnen trade. Hun nul-momentscore in de kalender is geen geselecteerde nulrendementswaarneming.

Bestaande ontdekking: 435 volledigeRTH-dagen, 458 weekdagposities, 162 geselecteerde dagen, 109 gescoorde dagen, 53 geselecteerde dagen in gaps/reststaart. Blokaantallen: [8, 10, 16, 16, 10, 16, 20, 13]. Minimaal120 totaal én8 per blok vereist. Deze109 blijven ontdekkingsdata: elf nieuwe dagen erbij zijn geen onafhankelijke bevestiging.

## Hoe lang verzamelen?

Waargenomen selectie: 37.24% per volledigeRTH-dag; binnen de meetblokken 34.94% per weekdagpositie. Onderstaande planning gebruikt alleen bestaande selectiedatums, geen nieuwe rendementen.

| Vooraf gekozen venster (raming) | Weekdagen | Gescoorde weekdagposities | Verwachte geselecteerde dagen | Verwacht per blok |
|---|---:|---:|---:|---:|
| circa1.0 jaar | 260 | 120 | 41.9 | 5.2 |
| circa2.0 jaar | 520 | 376 | 131.4 | 16.4 |
| circa3.0 jaar | 783 | 640 | 223.6 | 27.9 |

Dit zijn frequentieramingen, geen powerberekening, zekerheid of formeel gekozen forward-einddatum. Twee jaar ligt qua verwachte aantallen slechts beperkt boven de120-grens. Drie jaar geeft meer informatieruimte, maar ook120 waarnemingen bewijzen geen edge en garanderen geen80%power. Niet doorlopen totdat120 of significantie verschijnt. Bij het vaste eindpunt kan DATA_INSUFFICIENT de juiste uitkomst zijn.

## Status van de toetsmethode

De oorspronkelijke v2-specificatie gebruiktHAC5 metHolm2. De120-grens hoort bij de afzonderlijke conservatieve gegroepeerde methode. Die grens is een projectkeuze, geen universele statistische wet. De8 groepen zijn de inferentie-eenheden. Gaps maken dagen niet aantoonbaar onafhankelijk. De factor1,25 uit de tweede synthetische ronde is een voorstel en wijzigt v2 niet automatisch. Een toekomstige vrijgave moet vooraf aangeven welke methode formeel beslist, met behoud van alle bestaande registraties.

[Primaire methodologische bron: Ibragimov en Müller](https://www.princeton.edu/~umueller/tstat.pdf). De geldigheid vraagt passende onafhankelijkheids-/normaliteitsbenaderingen tussen groepen; ons specifieke120-minimum volgt niet uit die publicatie.

## Oudere bronvergelijking

Alle bestaandeNQH24-pilotdatums 2024-01-22 t/m 2024-02-16: 20 dagen met gedeeldeRTH-minuten, 19 volledig gemeenschappelijkeRTH-dagen, 7796 gemeenschappelijke minuten. GenericET-labels zijn uitsluitend met de al vastgelegde min1minuut vertaald; BarchartCT blijft op de bestaande startlabelconventie. Geen tijdverschuivingszoektocht.

| Vergelijking generic minusNQH24 | Aantal | Exact gelijk | Mediane absolute afwijking (pt) | P90 absolute afwijking (pt) | Max (pt) |
|---|---:|---:|---:|---:|---:|
| Minuut open-close | 7796 | 91.47% | 0.000 | 0.000 | 15.000 |
| Minuut high-low | 7796 | 99.59% | 0.000 | 0.000 | 11.500 |
| Onvoorwaardelijk15:00→15:01close | 20 | 85.00% | 0.000 | 0.250 | 15.500 |
| Onvoorwaardelijk15:00→15:14close | 20 | 80.00% | 0.000 | 0.250 | 0.750 |

Volume exact gelijk: 84.92%. Constante dag-offset in closes: 10.00% van gedeelde dagen. Grootste intradayvariatie in de prijs-offset: 16.000pt.

Only existing NQH24 pilot overlap, not all493 older complete RTH days. No contract-level2023 coverage, full historical roll chain, independent tick/BBO source or provenance certification. Agreement on this pilot cannot clear the older negative result; disagreement cannot justify discarding it without diagnosis.

Dit is geen bevestiging of herselectie van de15:00-kandidaat. De eerdere negatieve oudere uitkomst blijft staan. Ontbrekend: volledige contractgeïdentificeerde brondekking voor het oudere tegenbewijs en verifieerbare roll-/publicatieherkomst.

## Twee routes, strikt gescheiden

1. Historische replicatie2019–2021: bestaande vaste kalender behouden;103 geplandeexports,6 in de eerste batch ontvangen,97 nog ontbrekend volgens het oorspronkelijke register. Die aantallen zijn geen actuele bevestiging van gratis exportrechten. Januari2019 is deels al ingezien en blijft expliciet gemeld. Geen nieuwe eindtoets gestart. De volledige kalender heeft640 gescoorde weekdagposities, geen640 gegarandeerde events.

2. Prospectieve schaduwtest: nog niet gestart. Eerst een rechtmatige bestaande feed zonder nieuwe kosten, een onveranderlijke toekomstige start/einddatum, vaste kalenderblokken en vooraf vastgelegde formele meetlat. Cohortbesluit vóór de uitkomst vastleggen, beide horizons meten, uitvoeringsgegevens apart van bar-ankers houden. Geen echte orders of prijsfeed gekoppeld in deze ronde.

Gebruik geenCFD,ES, extra horizons of dubbele leverancierskopieën omNQ-dagen aan te vullen. Historische en forwardresultaten blijven aparte bewijslagen; niet achteraf samenvoegen om een drempel te halen.

## Eerstvolgende drie bestaande historische downloadblokken

| Contract | Vanaf (MM/DD/YYYY) | Tot en met |
|---|---|---|
| NQH19 | 01/14/2019 | 01/27/2019 |
| NQH19 | 01/28/2019 | 02/10/2019 |
| NQH19 | 02/11/2019 | 02/24/2019 |

Alleen ophalen als bestaande exportrechten dit zonder aankoop/verlenging toestaan. Deze lijst voltooit het oude vaste venster en is niet automatisch de aanvullende brondekking voor het negatieve2023–2024-tegenbewijs.

## Controle

489 bestaande bestanden voor en na de run opSHA-256 gelijk; de bestaande530-teststand en rapporten worden niet overschreven. Nieuwe tests/resultaten zijn aanvullend. Protocol en bronhashes zijn vóór deze beperkte vergelijking vastgelegd. Private ankerdetails blijven onderartifacts/.
