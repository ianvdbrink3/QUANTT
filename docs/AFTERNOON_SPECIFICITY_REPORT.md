# Specificiteit van het15:00-kwartier — vaste naburige vergelijking

## Afbakening

Uitsluitend14:30–14:45,14:45–15:00 en15:00–15:15 NY op dezelfde435 volledige RTH-dagen. De UP/DOWN-context wordt op ELK tijdstip opnieuw bepaald: laatste voltooide close ten opzichte van09:30open, en de tot dan opgebouwde RTH-range/vooraf bekende ATR14 in[0,5;1,2). Cohorten mogen daardoor verschillen. Geen latere15:00-selectie teruggeprojecteerd op eerdere kwartieren.

ALL en UP meten stijgingen. DOWN meet dalingen: positief betekent voortzetting omlaag. De benchmark voor DOWN is dus de negatieve van de onvoorwaardelijke opwaartse drift. Kosten zijn uitsluitend een vaste aftrek van1,225punt, geen entry/fill/stop/target-simulatie. Dezelfde aftrek aan beide kanten valt weg uit het verschil met de benchmark.

De bestaande15:00-bevinding is vóór de nieuwe uitkomsten apart vastgelegd in AFTERNOON_SPECIFICITY_PLAN.md en het gehashte protocol. Dit is een verkennende vervolgvergelijking op eerder bekeken data, geen onafhankelijke holdout.

## Volledige vergelijkingstabel

| Start NY | Groep/richting | Dagen | Gem.bruto pt | Med.bruto pt | Gem.na kosten pt | Med.na kosten pt | Voortzetting/stijging% | Positief na kosten% | Meerwaarde boven eigen benchmark pt |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 14:30 | Onvoorwaardelijk, opwaarts | 435 | 0,142 | 0,750 | -1,083 | -0,475 | 52,2 | 49,4 | 0,000 |
| 14:30 | Opwaartse context, voortzetting | 162 | 0,855 | 0,875 | -0,370 | -0,350 | 53,1 | 49,4 | 0,713 |
| 14:30 | Neerwaartse context, voortzetting | 131 | 0,918 | -0,500 | -0,307 | -1,725 | 48,9 | 48,1 | 1,060 |
| 14:45 | Onvoorwaardelijk, opwaarts | 435 | -3,266 | 1,250 | -4,491 | 0,025 | 52,6 | 50,3 | 0,000 |
| 14:45 | Opwaartse context, voortzetting | 165 | -4,958 | -0,750 | -6,183 | -1,975 | 49,1 | 46,1 | -1,691 |
| 14:45 | Neerwaartse context, voortzetting | 133 | 5,150 | -1,000 | 3,925 | -2,225 | 48,1 | 46,6 | 1,884 |
| 15:00 | Onvoorwaardelijk, opwaarts | 435 | 0,847 | 1,250 | -0,378 | 0,025 | 51,5 | 50,3 | 0,000 |
| 15:00 | Opwaartse context, voortzetting | 167 | 7,540 | 4,000 | 6,315 | 2,775 | 56,9 | 56,3 | 6,694 |
| 15:00 | Neerwaartse context, voortzetting | 131 | 3,666 | 2,500 | 2,441 | 1,275 | 52,7 | 51,9 | 4,513 |

## Toetsen:15:00 minus elk eerder kwartier

Zes contrasten vergelijken de ruwe gemiddelden van ALL/UP/DOWN; vier vergelijken de UP/DOWN-meerwaarde boven de eigen directionele klokbenchmark. Dit onderscheid voorkomt dat een bijzonder sterk onvoorwaardelijk kwartier automatisch als contextspecifieke meerwaarde wordt behandeld.

De dag-influence scores van beide steekproeven worden VAN ELKAAR AFGETROKKEN vóór de variantie wordt berekend. Daarmee blijft de covariantie van gedeelde handelsdagen behouden. Primaire inferentie: dag-scores met Bartlett-HAC lags1–5 op de454 geplande kalenderdagen, conservatieve t-vrijheidsgraden, één Holm-correctie over de tien vooraf bepaalde tweezijdige log-bp-toetsen. Geen tweede punten-p-familie. Puntenintervallen zijn afzonderlijk berekend. Alle95%-intervallen zijn nominaal, niet simultaan.

| Type | Context | Vergelijking | Dagen15:00 / eerder | Gedeelde dagen | Verschil pt | 95%CI pt | Verschil log-bp | 95%CI log-bp | Ruwe p | Holm10 p |
|---|---|---|---:|---:|---:|---|---:|---|---:|---:|
| raw_mean | ALL | 15:00 minus 14:30 | 435 / 435 | 435 | 0,705 | [-4,484; 5,894] | 0,009 | [-2,115; 2,132] | 0,993612 | 1,000000 |
| raw_mean | UP | 15:00 minus 14:30 | 167 / 162 | 155 | 6,685 | [0,555; 12,816] | 2,432 | [0,000; 4,864] | 0,049979 | 0,349852 |
| raw_mean | DOWN | 15:00 minus 14:30 | 131 / 131 | 121 | 2,748 | [-7,068; 12,564] | 1,395 | [-2,695; 5,484] | 0,501126 | 1,000000 |
| context_premium | UP | 15:00 minus 14:30 | 167 / 162 | 155 | 5,981 | [0,688; 11,274] | 2,423 | [0,275; 4,572] | 0,027294 | 0,218351 |
| context_premium | DOWN | 15:00 minus 14:30 | 131 / 131 | 121 | 3,453 | [-4,422; 11,328] | 1,403 | [-1,984; 4,791] | 0,414008 | 1,000000 |
| raw_mean | ALL | 15:00 minus 14:45 | 435 / 435 | 435 | 4,113 | [-2,009; 10,235] | 1,813 | [-0,710; 4,335] | 0,158504 | 0,951022 |
| raw_mean | UP | 15:00 minus 14:45 | 167 / 165 | 158 | 12,498 | [4,465; 20,531] | 4,924 | [1,745; 8,104] | 0,002604 | 0,026037 |
| raw_mean | DOWN | 15:00 minus 14:45 | 131 / 133 | 125 | -1,484 | [-12,032; 9,063] | -0,667 | [-4,921; 3,587] | 0,756938 | 1,000000 |
| context_premium | UP | 15:00 minus 14:45 | 167 / 165 | 158 | 8,385 | [2,466; 14,305] | 3,111 | [0,782; 5,441] | 0,009165 | 0,082487 |
| context_premium | DOWN | 15:00 minus 14:45 | 131 / 133 | 125 | 2,628 | [-5,889; 11,146] | 1,146 | [-2,244; 4,536] | 0,504813 | 1,000000 |

## Feitelijk oordeel

Van vier contextmeerwaarde-contrasten zijn er0 significant op5% na Holm10. Van zes ruwe-gemiddeldecontrasten zijn dat er1. De volledige richting en omvang staan in de tabel; significant betekent hier niet automatisch dat15:00 beter is.

In deze vaste run is uitsluitend het ruwe UP-gemiddelde van15:00 tegenover14:45 significant na Holm10: +12,498punten, ruwe log-bp-p=0,002604, Holm10-p=0,026037. De UP-meerwaarde boven de eigen klokbenchmark verschilt +8,385punten tegenover14:45, maar Holm10-p=0,082487. Tegenover14:30 bedraagt dit premieverschil +5,981punten, Holm10-p=0,218351. ALL en DOWN tonen geen gecorrigeerd significant tijdsverschil. De beschrijvende UP-voortzetting rond15:00 is dus niet hetzelfde als aangetoonde tijdstipspecifieke contextmeerwaarde.

Een niet-significant verschil bewijst geen gelijkwaardigheid en ook geen algemeen middagmomentum. Een significant verschil in ruwe groepsgemiddelden bewijst op zichzelf geen extra contextmeerwaarde. De cohorten veranderen tussen klokken: dit is geen causale behandelingseffectschatting op exact dezelfde geselecteerde dagen. Achteraf geselecteerd15:00 en al bekeken data blijven beperkingen, ook na de beperkte Holm10-correctie. Er is geen nieuwe handelsstrategie of promotie naar gevalideerde edge.

## Reproductie en bescherming

69 bronbestanden op geregistreerde hashes gecontroleerd; 1305 prefixcontroles en 1305 mutatiecontroles geslaagd. De tweede verse bronherlading geeft byte-identieke meetledgers en identieke aggregaten. De oorspronkelijke167 UP-dagen,131 DOWN-dagen en435-daagse15:00-benchmark zijn exact gereproduceerd. Alle115 beschermde archiefbestanden blijven ongewijzigd.

Verificatie: `.venv/bin/python -B -m scripts.afternoon_specificity --verify`. Ruwe prijzen en individuele meetregels blijven in de genegeerde lokale artifacts-map. Rapport en aggregaten zijn lokaal opgeslagen; geen GitHub-push of productiepublicatie uitgevoerd.
