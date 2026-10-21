# Causale marktmechanisme-kaart NQ — verkennende scan

## Conclusie en bewijsstatus

435 volledige RTH-dagen, 69 gehashte bronbestanden, 6131 geselecteerde events en 24093 event/horizonregels. Alle32 vooraf vastgelegde mechanismen en128 cellen staan hieronder, ook lege of te kleine groepen.

0 van128 cellen halen5% met BEIDE onzekerheidsmethoden na één globale Holm-correctie over256 toetsen. 100 cellen hebben minstens20 afzonderlijke eventdagen. Dat is een verkennende uitkomst op reeds bekeken data, geen onafhankelijke bevestiging of gevalideerde handelsedge.

Causaal betekent hier uitsluitend dat eventselectie, richting, ankers en gewichten point-in-time zijn. Het betekent niet dat stop-pools, institutionele handel of MOC-orders als oorzaak geïdentificeerd zijn. De economische categorieën zijn hypotheses over prijsreacties, geen waargenomen orderstromen.

De ranglijst is vooraf bepaald: maximum van de twee gecorrigeerde p-waarden, dan absolute gemiddelde log-bp. Een negatieve uitkomst is niet naar positief omgedraaid na de berekening. Kleine groepen met minder dan20 eventdagen krijgen géén p-waarde of interval; hun p=1-placeholder blijft in de correctiefamilie.

## Dekking en causale controles

5220 actuele-data-prefixcontroles; 90 opnieuw opgebouwde contextcontroles rond rollovers/historie-afkappingen. Een tweede volledige event/horizonextractie en statistiekberekening geeft byte-identieke ledgers en identieke aggregaten. Strategie-aanroepen zijn tijdens de bronroute geblokkeerd.

| Context beschikbaar vóór de meting | Dagen |
|---|---:|
| ATR14 | 418 |
| Vorige RTH-dag volledig | 417 |
| Overnight18:00–09:30 volledig | 413 |
| Minstens één1m-volumehistorie van20 sessies | 389 |
| Alle390 volumeklokken met20 sessies | 152 |
| Minstens één5m-volumehistorie | 389 |

De435 dagen zijn het vaste volledige-RTH-universum uit de vorige kwaliteitscontrole. Niet elke dag heeft iedere context. Ontbrekende ATR, prior range, overnightminuten of20-sessie-volumeklokken worden niet ingevuld of vervangen door gunstige subsets. Feestdagen/vroege sluitingen blijven ontbrekende volumeklokken geven waar geen reguliere RTH-bars bestaan.

## Vooraf vastgelegde mechanismen

- A: eerste bereik van PDH, PDL, ONH of ONL in RTH, inclusief openen/overspringen voorbij het niveau. De eerste bevestigingsclose bepaalt ACCEPT versus REJECT. ACCEPT meet naar buiten, REJECT naar binnen. Dit is geen achteraf ingedeelde winnaar/verliezer. Het is ook niet noodzakelijk een fysiek verhandelde touch: een gap over het niveau telt als bereik.
- B: strikt openingsgap boven PDH of onder PDL; daarnaast abs(09:30open − vorigeRTHclose)/ATR14≥1. Meting om09:30 en10:00, steeds met de oorspronkelijke gap/overnight-richting. De extreme overnight-verplaatsing is netto verplaatsing vanaf vorigeRTHclose, niet overnight high-low range.
- C: om09:30 is geen RTH-dagrichting bekend. Daar gebruiken we uitsluitend18:00–09:30richting en range. Om15:00 gebruiken we uitsluitend09:30open tot14:59close en de tot dan waargenomen RTH-range. SMALL<0,5ATR, MID[0,5;1,2), LARGE≥1,2. Rendement steeds met de bekende richting. Nulrichting wordt niet geclassificeerd.
- D: volume van een voltooide1m- of uitgelijnde5m-bar boven het empirische95e percentiel van precies20 voorgaande geplande sessies op die klok, plus een nieuw strikt RTH-extreem. RVOL=current/mean(previous20). Alle20 klokobservaties vereist; de huidige bar telt niet in de referentie. Beide extremen in één bar mogen beide labels geven. Rendement naar het nieuwe extreem: negatief wijst op omkeer.

Deze drempels zijn vóór de uitkomsten vastgelegd, niet op deze scan geoptimaliseerd. Met20 referentiedagen is een95e percentiel een ruwe volumestaartschatting; het betekent niet dat exact5% van toekomstige bars wordt geselecteerd.

## Ankers, horizons en excursies

Een bar met starttijd09:44 is pas09:45 bekend. Vervolgrendement begint op die close; MFE/MAE gebruiken uitsluitend bars vanaf09:45. Om09:30 is het anker de openingsprijs; om10:00 de09:59close; om15:00 de14:59close. Dit zijn onderzoeksankers, geen bewezen uitvoerbare fills.

15m/30m/60m betekenen exact zoveel verstreken minuten; horizons na16:00 worden ontbrekend, nooit ingekort. RTH-slot is de15:59barclose, niet settlement of een beursveilingprijs. Vanaf15:00 zijn60m en RTH-slot identiek; beide gevraagde cellen blijven conservatief in de volledige correctiefamilie. Een event dat pas16:00 bevestigd is telt in het eventregister maar heeft geen vervolgobservatie.

MFE/MAE zijn maximale gunstige/ongunstige OHLC-excursies in de vooraf gekozen richting. Ratio=gemiddelde MFE/gemiddelde MAE, niet het instabiele gemiddelde van individuele ratios met mogelijke nulnoemers. Daarnaast publiceren we medianen en de mediane begrensde balans(MFE−MAE)/(MFE+MAE). Hoogste en laagste prijs hebben geen bekende volgorde binnen een minuut; de ratio is geen winstfactor of bewijs dat beide prijzen verhandelbaar zijn.

## Onzekerheid, toetsen en interpretatie

Puntenschatting=gepoold gemiddelde per event, zonder achteraf gelijke daggewichten. Voor CR1 worden residuen eerst per handelsdag GESOMMEERD en pas dan gekwadrateerd. Standaardfout=sqrt(G/(G−1)×Σdag(score²))/N; t-vrijheidsgraden=G−1 eventdagen. Daardoor creëert het dupliceren van events binnen dezelfde dag geen extra onafhankelijke steekproef.

Een tweede methode gebruikt dezelfde dag-scores met Bartlett-HAC, vaste lags1–5, om samenhang tussen sessies te onderzoeken. Beide tweezijdige p-waarden toetsen een gemiddeld directioneel log-rendement van nul. Eén Holm-familie bevat32×4×2=256 toetsen, inclusief ontbrekende cellen als p=1. Puntenintervallen zijn apart berekend, niet door een gemiddelde prijs omgerekend. Intervallen zijn nominaal95%, niet simultaan95%. Kwartalen, medianen, positieve fracties en excursies zijn beschrijvend en krijgen geen extra significantieclaims.

CR1 veronderstelt onafhankelijke dagclusters; HAC is een beperkte asymptotische robuustheidscontrole, geen garantie tegen elke regimestructuur. Verschillen met nul bewijzen ook niet dat het effect extra voorspellende informatie geeft boven de onvoorwaardelijke drift op hetzelfde tijdstip. Dat onderscheid vereist een afzonderlijk vastgelegde vergelijking, niet achteraf de gunstigste baseline kiezen.

## Kalibratie zonder voorspelbare toekomstige log-rendementen

Vooraf128 panelen van120 synthetische sessies, seed20261024, onafhankelijke Gaussian log-innovaties met8 substeps/minuut en onafhankelijke overnight/volume-innovaties. Exact dezelfde selectie, horizons en CR1/HAC/Holm. 2/128 panelen bevatten een cel die na de gezamenlijke correctie met beide methoden verwerpt. Alle celdekkingen en afwijzingsaantallen staan in de kalibratie-CSV, inclusief groepen met weinig of geen geldige panelen.

Een eindige kalibratie is geen exact bewijs van5% dekking in echte NQ-data. Zeldzame contextgroepen kunnen in dit eenvoudige nulscenario nauwelijks voorkomen. Ze zijn daarmee niet gevalideerd. Verwachte log-innovaties zijn nul; rekenkundige puntprijsveranderingen hebben een Jensen-effect en worden niet als nulmartingaal geclaimd.

## Volledige ranglijst

Alle gecorrigeerde p-waarden zijn hier1. De vooraf vastgelegde rangvolgorde wordt daardoor uitsluitend door effectgrootte bepaald, inclusief kleine groepen. Rang1 is dus nadrukkelijk NIET de sterkste statistische aanwijzing. De hieronder genoemde kleinste ruwe p-waarden zijn alleen een beschrijvende leeswijzer naast de volledige, ongewijzigde ranglijst.

Positief%=aandeel positieve bruto vervolgrendementen in de vooraf bepaalde richting, geen netto handelswinrate. Alle gemiddelden en excursies zijn vóór commissie, spread, slippage en eventuele fill-latency.

| Rang | Mechanisme | Horizon | Events | Dagen | Gem.pt | Med.pt | Gem.bp | Med.bp | Positief% | CR195%bp | pCR1 | pHolm256 | pHAC | pHACHolm256 | MFE/MAE |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| 1 | B_EXTREME_ON_UP_0930 | close | 10 | 10 | -150,550 | -50,125 | -62,599 | -17,770 | 40,0 | — | — | 1,000000 | — | 1,000000 | 0,371 |
| 2 | B_EXTREME_ON_DOWN_1000 | close | 13 | 13 | 130,500 | 2,500 | 55,593 | 1,093 | 53,8 | — | — | 1,000000 | — | 1,000000 | 1,076 |
| 3 | B_EXTREME_ON_UP_1000 | close | 10 | 10 | -110,525 | 15,750 | -46,233 | 6,326 | 50,0 | — | — | 1,000000 | — | 1,000000 | 0,560 |
| 4 | C_0930_DOWN_LARGE | 60 | 17 | 17 | -106,029 | -116,250 | -44,844 | -44,985 | 17,6 | — | — | 1,000000 | — | 1,000000 | 0,511 |
| 5 | C_0930_DOWN_LARGE | 30 | 17 | 17 | -69,029 | -41,500 | -32,461 | -22,558 | 23,5 | — | — | 1,000000 | — | 1,000000 | 0,843 |
| 6 | B_EXTREME_ON_DOWN_1000 | 15 | 13 | 13 | -70,673 | -40,000 | -32,205 | -13,736 | 30,8 | — | — | 1,000000 | — | 1,000000 | 0,440 |
| 7 | B_EXTREME_ON_DOWN_0930 | close | 13 | 13 | 88,846 | 46,500 | 31,710 | 15,895 | 53,8 | — | — | 1,000000 | — | 1,000000 | 0,868 |
| 8 | B_EXTREME_ON_DOWN_0930 | 60 | 13 | 13 | -68,365 | -94,000 | -30,642 | -34,707 | 30,8 | — | — | 1,000000 | — | 1,000000 | 0,529 |
| 9 | C_0930_DOWN_LARGE | close | 17 | 17 | -56,250 | -15,000 | -25,119 | -5,151 | 41,2 | — | — | 1,000000 | — | 1,000000 | 0,517 |
| 10 | B_EXTREME_ON_DOWN_0930 | 30 | 13 | 13 | -41,654 | -41,000 | -23,883 | -22,558 | 30,8 | — | — | 1,000000 | — | 1,000000 | 0,863 |
| 11 | C_0930_DOWN_SMALL | close | 48 | 48 | 54,833 | 24,250 | 22,201 | 9,638 | 54,2 | [-0,765; 45,167] | 0,057803 | 1,000000 | 0,080555 | 1,000000 | 1,775 |
| 12 | C_0930_UP_LARGE | close | 14 | 14 | 52,929 | 28,750 | 20,164 | 11,843 | 57,1 | — | — | 1,000000 | — | 1,000000 | 1,088 |
| 13 | B_EXTREME_ON_UP_0930 | 15 | 10 | 10 | -46,450 | -45,250 | -19,827 | -15,683 | 20,0 | — | — | 1,000000 | — | 1,000000 | 0,351 |
| 14 | B_EXTREME_ON_UP_0930 | 30 | 10 | 10 | -40,025 | -45,125 | -16,366 | -16,702 | 30,0 | — | — | 1,000000 | — | 1,000000 | 0,460 |
| 15 | B_GAP_DOWN_0930 | close | 69 | 69 | -35,272 | -56,000 | -15,362 | -22,760 | 42,0 | [-44,400; 13,677] | 0,294881 | 1,000000 | 0,207736 | 1,000000 | 0,789 |
| 16 | C_0930_DOWN_SMALL | 60 | 48 | 48 | 35,917 | 8,500 | 15,184 | 3,441 | 54,2 | [0,669; 29,698] | 0,040707 | 1,000000 | 0,034026 | 1,000000 | 1,799 |
| 17 | B_EXTREME_ON_UP_0930 | 60 | 10 | 10 | -29,075 | -7,250 | -14,002 | -2,449 | 30,0 | — | — | 1,000000 | — | 1,000000 | 0,475 |
| 18 | B_GAP_DOWN_0930 | 60 | 69 | 69 | -33,388 | -43,750 | -13,599 | -18,144 | 36,2 | [-30,374; 3,176] | 0,110353 | 1,000000 | 0,077822 | 1,000000 | 0,760 |
| 19 | D_5m_HIGH | close | 265 | 124 | 25,233 | 14,500 | 12,733 | 6,714 | 56,2 | [-7,176; 32,641] | 0,207923 | 1,000000 | 0,221730 | 1,000000 | 1,250 |
| 20 | A_ONL_REJECT | close | 125 | 125 | -30,114 | -4,250 | -12,522 | -1,794 | 48,8 | [-28,522; 3,477] | 0,123899 | 1,000000 | 0,117591 | 1,000000 | 0,719 |
| 21 | A_ONH_REJECT | close | 117 | 117 | 28,754 | 1,250 | 12,248 | 0,421 | 50,4 | [-5,735; 30,230] | 0,179980 | 1,000000 | 0,157895 | 1,000000 | 1,477 |
| 22 | C_0930_DOWN_MID | close | 114 | 114 | -23,112 | -57,500 | -12,027 | -23,614 | 43,0 | [-30,526; 6,472] | 0,200358 | 1,000000 | 0,215289 | 1,000000 | 1,001 |
| 23 | D_5m_HIGH | 60 | 244 | 116 | 24,351 | 10,250 | 11,811 | 4,340 | 55,7 | [-1,895; 25,517] | 0,090534 | 1,000000 | 0,097837 | 1,000000 | 1,359 |
| 24 | A_PDL_REJECT | close | 68 | 68 | -30,478 | 7,875 | -11,517 | 2,936 | 51,5 | [-30,672; 7,638] | 0,234319 | 1,000000 | 0,223022 | 1,000000 | 0,718 |
| 25 | A_ONL_ACCEPT | 60 | 101 | 101 | -26,458 | -32,250 | -10,574 | -12,916 | 37,6 | [-21,351; 0,203] | 0,054391 | 1,000000 | 0,052286 | 1,000000 | 0,843 |
| 26 | B_EXTREME_ON_DOWN_0930 | 15 | 13 | 13 | 21,173 | -31,000 | 10,548 | -10,426 | 46,2 | — | — | 1,000000 | — | 1,000000 | 1,186 |
| 27 | C_1500_UP_LARGE | 60 | 18 | 18 | -37,153 | -7,250 | -10,023 | -2,814 | 44,4 | — | — | 1,000000 | — | 1,000000 | 0,795 |
| 28 | C_1500_UP_LARGE | close | 18 | 18 | -37,153 | -7,250 | -10,023 | -2,814 | 44,4 | — | — | 1,000000 | — | 1,000000 | 0,795 |
| 29 | B_GAP_DOWN_1000 | 60 | 69 | 69 | -21,188 | -34,000 | -9,579 | -13,939 | 39,1 | [-24,261; 5,103] | 0,197344 | 1,000000 | 0,146813 | 1,000000 | 0,757 |
| 30 | B_GAP_DOWN_0930 | 30 | 69 | 69 | -20,565 | -36,000 | -8,946 | -15,268 | 39,1 | [-21,660; 3,768] | 0,164864 | 1,000000 | 0,169181 | 1,000000 | 0,880 |
| 31 | A_ONL_ACCEPT | 30 | 101 | 101 | -22,579 | -28,000 | -8,917 | -11,282 | 37,6 | [-18,529; 0,695] | 0,068661 | 1,000000 | 0,091252 | 1,000000 | 0,851 |
| 32 | B_GAP_UP_0930 | close | 108 | 108 | -14,900 | -25,500 | -8,642 | -8,804 | 46,3 | [-24,896; 7,611] | 0,294233 | 1,000000 | 0,309844 | 1,000000 | 0,722 |
| 33 | C_0930_DOWN_SMALL | 30 | 48 | 48 | 19,411 | 6,750 | 8,556 | 2,653 | 58,3 | [-0,721; 17,834] | 0,069812 | 1,000000 | 0,079143 | 1,000000 | 1,585 |
| 34 | B_GAP_DOWN_1000 | 15 | 69 | 69 | -18,406 | -12,250 | -8,203 | -4,768 | 40,6 | [-21,849; 5,443] | 0,234491 | 1,000000 | 0,126831 | 1,000000 | 0,745 |
| 35 | C_1500_DOWN_LARGE | 60 | 34 | 34 | 12,456 | -2,250 | 8,168 | -0,811 | 47,1 | [-10,013; 26,349] | 0,367331 | 1,000000 | 0,406532 | 1,000000 | 1,384 |
| 36 | C_1500_DOWN_LARGE | close | 34 | 34 | 12,456 | -2,250 | 8,168 | -0,811 | 47,1 | [-10,013; 26,349] | 0,367331 | 1,000000 | 0,406532 | 1,000000 | 1,384 |
| 37 | C_0930_DOWN_LARGE | 15 | 17 | 17 | 13,250 | -31,000 | 7,454 | -10,426 | 47,1 | — | — | 1,000000 | — | 1,000000 | 1,378 |
| 38 | C_0930_UP_LARGE | 60 | 14 | 14 | 21,982 | -3,250 | 7,108 | -1,119 | 42,9 | — | — | 1,000000 | — | 1,000000 | 0,966 |
| 39 | C_1500_DOWN_LARGE | 15 | 34 | 34 | 15,199 | 8,625 | 7,106 | 3,589 | 52,9 | [-4,138; 18,349] | 0,207455 | 1,000000 | 0,169323 | 1,000000 | 1,263 |
| 40 | C_0930_UP_SMALL | close | 81 | 81 | -19,815 | -19,000 | -7,039 | -8,540 | 49,4 | [-28,474; 14,397] | 0,515326 | 1,000000 | 0,534123 | 1,000000 | 0,728 |
| 41 | A_PDL_REJECT | 15 | 68 | 68 | -18,915 | -7,375 | -6,874 | -3,145 | 44,1 | [-14,411; 0,664] | 0,073202 | 1,000000 | 0,113619 | 1,000000 | 0,706 |
| 42 | D_1m_HIGH | close | 1109 | 240 | 14,179 | 12,500 | 6,777 | 5,076 | 55,7 | [-6,782; 20,336] | 0,325808 | 1,000000 | 0,294474 | 1,000000 | 1,060 |
| 43 | B_EXTREME_ON_DOWN_1000 | 30 | 13 | 13 | -26,712 | -57,500 | -6,759 | -19,196 | 23,1 | — | — | 1,000000 | — | 1,000000 | 0,381 |
| 44 | B_GAP_DOWN_1000 | close | 69 | 69 | -14,707 | -39,750 | -6,416 | -13,651 | 42,0 | [-31,314; 18,482] | 0,608783 | 1,000000 | 0,555222 | 1,000000 | 0,827 |
| 45 | C_1500_DOWN_LARGE | 30 | 34 | 34 | 12,904 | 6,250 | 6,280 | 2,577 | 52,9 | [-6,659; 19,218] | 0,330586 | 1,000000 | 0,313716 | 1,000000 | 1,494 |
| 46 | C_1500_UP_LARGE | 15 | 18 | 18 | 10,639 | 5,875 | 5,961 | 2,618 | 55,6 | — | — | 1,000000 | — | 1,000000 | 1,402 |
| 47 | A_PDH_ACCEPT | 30 | 157 | 157 | -12,774 | -3,250 | -5,782 | -1,352 | 49,0 | [-14,801; 3,238] | 0,207324 | 1,000000 | 0,143045 | 1,000000 | 0,803 |
| 48 | B_GAP_UP_0930 | 30 | 108 | 108 | -13,634 | 2,875 | -5,533 | 1,227 | 50,9 | [-14,560; 3,494] | 0,226985 | 1,000000 | 0,193044 | 1,000000 | 0,740 |
| 49 | A_ONH_ACCEPT | close | 128 | 128 | 16,062 | 9,250 | 5,482 | 4,349 | 53,1 | [-7,878; 18,841] | 0,418345 | 1,000000 | 0,431017 | 1,000000 | 0,930 |
| 50 | A_ONH_REJECT | 15 | 114 | 114 | -9,855 | -5,750 | -5,413 | -2,769 | 47,4 | [-13,554; 2,729] | 0,190485 | 1,000000 | 0,186589 | 1,000000 | 0,963 |
| 51 | A_ONL_REJECT | 30 | 125 | 125 | -11,766 | -6,750 | -5,412 | -2,263 | 48,0 | [-12,520; 1,696] | 0,134381 | 1,000000 | 0,183297 | 1,000000 | 0,811 |
| 52 | D_5m_HIGH | 15 | 257 | 122 | 11,411 | 5,500 | 5,351 | 2,001 | 54,5 | [0,389; 10,312] | 0,034767 | 1,000000 | 0,064578 | 1,000000 | 1,275 |
| 53 | D_1m_HIGH | 60 | 1037 | 236 | 11,400 | 11,500 | 5,278 | 4,623 | 56,7 | [-1,931; 12,487] | 0,150504 | 1,000000 | 0,107712 | 1,000000 | 1,103 |
| 54 | D_5m_LOW | close | 652 | 182 | 9,815 | -16,500 | 5,242 | -6,748 | 46,2 | [-16,762; 27,246] | 0,638880 | 1,000000 | 0,566088 | 1,000000 | 1,169 |
| 55 | D_5m_HIGH | 30 | 254 | 121 | 11,516 | 8,000 | 5,153 | 3,178 | 56,7 | [-2,582; 12,888] | 0,189705 | 1,000000 | 0,098397 | 1,000000 | 1,286 |
| 56 | A_ONL_REJECT | 60 | 124 | 124 | -11,486 | -7,500 | -5,122 | -2,872 | 45,2 | [-15,396; 5,151] | 0,325590 | 1,000000 | 0,344570 | 1,000000 | 0,771 |
| 57 | B_GAP_UP_0930 | 15 | 108 | 108 | -12,053 | 4,375 | -4,917 | 1,776 | 53,7 | [-11,074; 1,240] | 0,116351 | 1,000000 | 0,086476 | 1,000000 | 0,745 |
| 58 | C_0930_UP_MID | close | 123 | 123 | -3,313 | 0,750 | -4,880 | 0,325 | 50,4 | [-24,274; 14,513] | 0,619247 | 1,000000 | 0,620450 | 1,000000 | 0,790 |
| 59 | B_GAP_DOWN_1000 | 30 | 69 | 69 | -12,822 | -23,000 | -4,654 | -8,270 | 36,2 | [-15,256; 5,949] | 0,384194 | 1,000000 | 0,399925 | 1,000000 | 0,697 |
| 60 | B_EXTREME_ON_DOWN_1000 | 60 | 13 | 13 | -17,462 | -26,250 | -4,125 | -12,561 | 38,5 | — | — | 1,000000 | — | 1,000000 | 0,577 |
| 61 | C_0930_DOWN_SMALL | 15 | 48 | 48 | 10,646 | 6,125 | 4,079 | 2,408 | 58,3 | [-1,443; 9,602] | 0,143935 | 1,000000 | 0,122216 | 1,000000 | 1,421 |
| 62 | A_PDH_ACCEPT | 60 | 157 | 157 | -9,688 | 4,500 | -3,958 | 1,655 | 52,2 | [-14,927; 7,011] | 0,477087 | 1,000000 | 0,340088 | 1,000000 | 0,752 |
| 63 | B_GAP_UP_0930 | 60 | 108 | 108 | -10,144 | -9,875 | -3,820 | -4,053 | 47,2 | [-13,248; 5,609] | 0,423701 | 1,000000 | 0,366538 | 1,000000 | 0,729 |
| 64 | A_ONL_ACCEPT | 15 | 101 | 101 | -10,554 | -16,000 | -3,796 | -7,038 | 40,6 | [-10,595; 3,004] | 0,270746 | 1,000000 | 0,301494 | 1,000000 | 0,901 |
| 65 | D_1m_LOW | close | 1989 | 264 | 7,202 | -16,750 | 3,649 | -6,827 | 45,7 | [-15,395; 22,692] | 0,706274 | 1,000000 | 0,649072 | 1,000000 | 1,187 |
| 66 | C_1500_DOWN_MID | 30 | 131 | 131 | 7,550 | 5,750 | 3,474 | 2,099 | 56,5 | [-0,241; 7,189] | 0,066604 | 1,000000 | 0,060363 | 1,000000 | 1,205 |
| 67 | C_0930_UP_MID | 15 | 123 | 123 | -7,591 | 2,750 | -3,227 | 0,922 | 50,4 | [-8,675; 2,222] | 0,243315 | 1,000000 | 0,213912 | 1,000000 | 0,827 |
| 68 | A_ONL_ACCEPT | close | 101 | 101 | -9,762 | -21,250 | -3,120 | -7,325 | 46,5 | [-20,804; 14,563] | 0,727026 | 1,000000 | 0,709671 | 1,000000 | 0,975 |
| 69 | B_GAP_UP_1000 | close | 108 | 108 | -1,266 | 2,125 | -3,109 | 0,868 | 51,9 | [-17,526; 11,308] | 0,669889 | 1,000000 | 0,684300 | 1,000000 | 0,836 |
| 70 | C_0930_DOWN_MID | 15 | 114 | 114 | -6,906 | -9,875 | -3,071 | -4,302 | 43,9 | [-10,275; 4,133] | 0,400177 | 1,000000 | 0,346481 | 1,000000 | 0,915 |
| 71 | C_1500_UP_SMALL | 60 | 40 | 40 | -7,219 | -0,500 | -3,058 | -0,252 | 47,5 | [-8,813; 2,696] | 0,288976 | 1,000000 | 0,337181 | 1,000000 | 0,881 |
| 72 | C_1500_UP_SMALL | close | 40 | 40 | -7,219 | -0,500 | -3,058 | -0,252 | 47,5 | [-8,813; 2,696] | 0,288976 | 1,000000 | 0,337181 | 1,000000 | 0,881 |
| 73 | C_1500_UP_MID | 15 | 167 | 167 | 7,540 | 4,000 | 3,048 | 1,599 | 56,9 | [0,858; 5,238] | 0,006663 | 1,000000 | 0,004375 | 1,000000 | 1,578 |
| 74 | C_1500_DOWN_MID | 60 | 131 | 131 | -6,712 | -6,250 | -2,996 | -2,622 | 47,3 | [-8,420; 2,428] | 0,276561 | 1,000000 | 0,302933 | 1,000000 | 1,088 |
| 75 | C_1500_DOWN_MID | close | 131 | 131 | -6,712 | -6,250 | -2,996 | -2,622 | 47,3 | [-8,420; 2,428] | 0,276561 | 1,000000 | 0,302933 | 1,000000 | 1,088 |
| 76 | A_PDL_REJECT | 60 | 65 | 65 | -7,723 | 0,500 | -2,995 | 0,229 | 50,8 | [-15,515; 9,525] | 0,634330 | 1,000000 | 0,653385 | 1,000000 | 0,819 |
| 77 | A_PDL_ACCEPT | 30 | 110 | 110 | -5,995 | -13,250 | -2,972 | -4,934 | 46,4 | [-12,294; 6,350] | 0,528811 | 1,000000 | 0,514308 | 1,000000 | 1,085 |
| 78 | A_PDL_ACCEPT | 15 | 111 | 111 | 5,928 | 4,500 | 2,933 | 2,119 | 50,5 | [-3,983; 9,850] | 0,402484 | 1,000000 | 0,411261 | 1,000000 | 1,211 |
| 79 | A_PDL_ACCEPT | 60 | 110 | 110 | -7,127 | -20,375 | -2,895 | -7,947 | 44,5 | [-14,725; 8,935] | 0,628664 | 1,000000 | 0,595805 | 1,000000 | 0,996 |
| 80 | A_ONH_ACCEPT | 60 | 124 | 124 | 6,308 | 9,250 | 2,686 | 3,864 | 54,8 | [-4,473; 9,845] | 0,459090 | 1,000000 | 0,468798 | 1,000000 | 0,850 |
| 81 | B_EXTREME_ON_UP_1000 | 30 | 10 | 10 | 10,950 | -8,625 | 2,364 | -3,408 | 40,0 | — | — | 1,000000 | — | 1,000000 | 0,965 |
| 82 | C_0930_UP_SMALL | 60 | 81 | 81 | -6,972 | -11,000 | -2,317 | -4,890 | 48,1 | [-15,193; 10,559] | 0,721193 | 1,000000 | 0,716408 | 1,000000 | 0,835 |
| 83 | A_PDH_REJECT | 60 | 74 | 74 | -5,003 | -2,750 | -2,242 | -1,147 | 47,3 | [-10,984; 6,500] | 0,610846 | 1,000000 | 0,606605 | 1,000000 | 1,089 |
| 84 | C_0930_DOWN_MID | 60 | 114 | 114 | -4,754 | -16,625 | -2,018 | -6,006 | 43,9 | [-13,470; 9,435] | 0,727716 | 1,000000 | 0,718834 | 1,000000 | 0,963 |
| 85 | A_PDH_ACCEPT | 15 | 157 | 157 | -3,325 | 5,250 | -2,006 | 2,399 | 56,1 | [-9,405; 5,393] | 0,593079 | 1,000000 | 0,513515 | 1,000000 | 0,877 |
| 86 | A_PDH_REJECT | close | 78 | 78 | -2,603 | -20,750 | -2,004 | -9,219 | 41,0 | [-16,860; 12,852] | 0,788950 | 1,000000 | 0,797382 | 1,000000 | 1,196 |
| 87 | B_EXTREME_ON_UP_1000 | 60 | 10 | 10 | 2,375 | -12,500 | -2,003 | -5,366 | 40,0 | — | — | 1,000000 | — | 1,000000 | 0,929 |
| 88 | A_PDH_REJECT | 30 | 76 | 76 | -4,092 | -2,125 | -1,969 | -0,948 | 46,1 | [-9,118; 5,179] | 0,584812 | 1,000000 | 0,580121 | 1,000000 | 1,041 |
| 89 | B_GAP_UP_1000 | 30 | 108 | 108 | 3,491 | 8,000 | 1,714 | 2,883 | 56,5 | [-3,655; 7,082] | 0,528222 | 1,000000 | 0,533238 | 1,000000 | 0,883 |
| 90 | A_PDH_ACCEPT | close | 158 | 158 | -0,358 | 13,875 | -1,617 | 5,256 | 54,4 | [-16,953; 13,719] | 0,835276 | 1,000000 | 0,808812 | 1,000000 | 0,795 |
| 91 | B_GAP_DOWN_0930 | 15 | 69 | 69 | -6,018 | -24,500 | -1,615 | -9,823 | 42,0 | [-11,706; 8,475] | 0,750352 | 1,000000 | 0,769644 | 1,000000 | 0,965 |
| 92 | C_1500_UP_MID | 30 | 167 | 167 | 3,933 | 3,500 | 1,505 | 1,442 | 55,1 | [-1,347; 4,358] | 0,299040 | 1,000000 | 0,200817 | 1,000000 | 1,406 |
| 93 | C_1500_DOWN_MID | 15 | 131 | 131 | 3,666 | 2,500 | 1,460 | 1,111 | 52,7 | [-1,044; 3,965] | 0,250830 | 1,000000 | 0,252223 | 1,000000 | 1,157 |
| 94 | C_1500_DOWN_SMALL | 60 | 28 | 28 | -3,509 | 6,375 | -1,452 | 2,941 | 57,1 | [-11,688; 8,784] | 0,773233 | 1,000000 | 0,770358 | 1,000000 | 0,935 |
| 95 | C_1500_DOWN_SMALL | close | 28 | 28 | -3,509 | 6,375 | -1,452 | 2,941 | 57,1 | [-11,688; 8,784] | 0,773233 | 1,000000 | 0,770358 | 1,000000 | 0,935 |
| 96 | C_1500_UP_SMALL | 30 | 40 | 40 | -2,075 | -0,750 | -1,435 | -0,295 | 47,5 | [-5,441; 2,572] | 0,473274 | 1,000000 | 0,466787 | 1,000000 | 1,014 |
| 97 | C_1500_UP_LARGE | 30 | 18 | 18 | -3,458 | 1,250 | 1,431 | 0,502 | 55,6 | — | — | 1,000000 | — | 1,000000 | 1,106 |
| 98 | D_5m_LOW | 60 | 635 | 182 | 4,671 | -7,250 | 1,415 | -3,527 | 47,4 | [-6,593; 9,422] | 0,727805 | 1,000000 | 0,734958 | 1,000000 | 1,099 |
| 99 | C_0930_UP_MID | 30 | 123 | 123 | -2,341 | 1,000 | -1,398 | 0,381 | 51,2 | [-9,153; 6,357] | 0,721843 | 1,000000 | 0,719367 | 1,000000 | 0,875 |
| 100 | D_1m_HIGH | 15 | 1076 | 238 | 2,197 | 1,250 | 1,120 | 0,541 | 51,4 | [-1,166; 3,405] | 0,335453 | 1,000000 | 0,281129 | 1,000000 | 0,995 |
| 101 | A_PDL_REJECT | 30 | 67 | 67 | 2,511 | 14,750 | 1,113 | 5,659 | 53,7 | [-9,104; 11,331] | 0,828425 | 1,000000 | 0,848174 | 1,000000 | 0,823 |
| 102 | C_0930_UP_SMALL | 30 | 81 | 81 | -4,731 | 13,000 | -1,074 | 4,961 | 55,6 | [-12,915; 10,766] | 0,857154 | 1,000000 | 0,848656 | 1,000000 | 0,857 |
| 103 | C_1500_DOWN_SMALL | 30 | 28 | 28 | 2,179 | 1,500 | 1,058 | 0,598 | 57,1 | [-5,723; 7,840] | 0,751271 | 1,000000 | 0,738575 | 1,000000 | 1,023 |
| 104 | D_5m_LOW | 15 | 650 | 182 | -1,525 | -4,625 | -1,025 | -1,885 | 48,2 | [-4,667; 2,618] | 0,579550 | 1,000000 | 0,623551 | 1,000000 | 1,032 |
| 105 | D_5m_LOW | 30 | 645 | 182 | -0,709 | -5,250 | -1,009 | -1,913 | 47,4 | [-7,301; 5,284] | 0,752174 | 1,000000 | 0,758525 | 1,000000 | 1,073 |
| 106 | A_ONL_REJECT | 15 | 125 | 125 | -2,182 | 4,000 | -0,955 | 1,559 | 53,6 | [-6,868; 4,957] | 0,749658 | 1,000000 | 0,785309 | 1,000000 | 0,883 |
| 107 | A_ONH_ACCEPT | 30 | 126 | 126 | -2,379 | 0,375 | -0,940 | 0,105 | 50,0 | [-6,718; 4,837] | 0,747949 | 1,000000 | 0,745902 | 1,000000 | 0,847 |
| 108 | D_1m_LOW | 60 | 1917 | 264 | 3,518 | -7,500 | 0,930 | -2,805 | 47,4 | [-6,906; 8,766] | 0,815361 | 1,000000 | 0,810484 | 1,000000 | 1,140 |
| 109 | D_1m_HIGH | 30 | 1068 | 238 | 1,635 | 1,000 | 0,864 | 0,334 | 51,1 | [-3,615; 5,343] | 0,704212 | 1,000000 | 0,609692 | 1,000000 | 1,068 |
| 110 | C_1500_UP_MID | 60 | 167 | 167 | 1,654 | 3,750 | 0,776 | 1,272 | 50,9 | [-3,811; 5,364] | 0,738666 | 1,000000 | 0,721624 | 1,000000 | 1,187 |
| 111 | C_1500_UP_MID | close | 167 | 167 | 1,654 | 3,750 | 0,776 | 1,272 | 50,9 | [-3,811; 5,364] | 0,738666 | 1,000000 | 0,721624 | 1,000000 | 1,187 |
| 112 | A_ONH_REJECT | 30 | 114 | 114 | 2,031 | 7,625 | 0,732 | 2,932 | 53,5 | [-5,754; 7,218] | 0,823485 | 1,000000 | 0,813121 | 1,000000 | 1,003 |
| 113 | A_PDL_ACCEPT | close | 111 | 111 | -0,441 | -8,500 | -0,706 | -3,310 | 47,7 | [-20,127; 18,716] | 0,942736 | 1,000000 | 0,933326 | 1,000000 | 1,038 |
| 114 | C_0930_DOWN_MID | 30 | 114 | 114 | -1,890 | -13,500 | -0,691 | -6,100 | 44,7 | [-9,777; 8,396] | 0,880537 | 1,000000 | 0,867961 | 1,000000 | 0,956 |
| 115 | C_0930_UP_LARGE | 30 | 14 | 14 | 2,375 | 13,000 | 0,635 | 4,458 | 50,0 | — | — | 1,000000 | — | 1,000000 | 0,854 |
| 116 | B_EXTREME_ON_UP_1000 | 15 | 10 | 10 | 2,600 | 7,750 | 0,623 | 2,987 | 50,0 | — | — | 1,000000 | — | 1,000000 | 0,946 |
| 117 | B_GAP_UP_1000 | 15 | 108 | 108 | -2,190 | 3,250 | -0,579 | 1,460 | 56,5 | [-4,868; 3,710] | 0,789508 | 1,000000 | 0,788174 | 1,000000 | 0,917 |
| 118 | C_0930_UP_LARGE | 15 | 14 | 14 | 2,036 | 2,750 | 0,514 | 1,103 | 57,1 | — | — | 1,000000 | — | 1,000000 | 0,622 |
| 119 | A_ONH_ACCEPT | 15 | 126 | 126 | -0,778 | 5,250 | -0,475 | 2,019 | 55,6 | [-4,705; 3,756] | 0,824523 | 1,000000 | 0,832485 | 1,000000 | 0,863 |
| 120 | A_PDH_REJECT | 15 | 77 | 77 | 0,656 | -0,500 | 0,404 | -0,193 | 49,4 | [-4,921; 5,730] | 0,880202 | 1,000000 | 0,877529 | 1,000000 | 1,095 |
| 121 | C_0930_UP_SMALL | 15 | 81 | 81 | 0,046 | 5,750 | 0,404 | 2,412 | 54,3 | [-6,953; 7,761] | 0,913248 | 1,000000 | 0,909647 | 1,000000 | 0,922 |
| 122 | D_1m_LOW | 15 | 1976 | 264 | 0,013 | -2,500 | -0,305 | -1,052 | 47,9 | [-3,313; 2,704] | 0,841977 | 1,000000 | 0,843041 | 1,000000 | 1,062 |
| 123 | A_ONH_REJECT | 60 | 112 | 112 | 3,181 | -15,500 | 0,292 | -6,458 | 45,5 | [-9,083; 9,667] | 0,950830 | 1,000000 | 0,953893 | 1,000000 | 1,136 |
| 124 | C_1500_DOWN_SMALL | 15 | 28 | 28 | -0,652 | -4,875 | -0,268 | -2,082 | 46,4 | [-4,592; 4,056] | 0,899690 | 1,000000 | 0,895561 | 1,000000 | 0,979 |
| 125 | C_0930_UP_MID | 60 | 123 | 123 | -0,516 | 9,750 | 0,255 | 4,162 | 52,8 | [-9,065; 9,574] | 0,956938 | 1,000000 | 0,951915 | 1,000000 | 0,828 |
| 126 | B_GAP_UP_1000 | 60 | 108 | 108 | -0,220 | 1,375 | -0,232 | 0,566 | 50,9 | [-7,770; 7,306] | 0,951516 | 1,000000 | 0,952359 | 1,000000 | 0,855 |
| 127 | C_1500_UP_SMALL | 15 | 40 | 40 | 0,650 | -0,125 | 0,173 | -0,062 | 50,0 | [-2,435; 2,780] | 0,894095 | 1,000000 | 0,895308 | 1,000000 | 1,064 |
| 128 | D_1m_LOW | 30 | 1951 | 264 | 0,846 | -3,250 | -0,129 | -1,407 | 47,5 | [-6,096; 5,839] | 0,966164 | 1,000000 | 0,962552 | 1,000000 | 1,103 |

### Beschrijvende leeswijzer: laagste ruwe CR1-p, niet geselecteerd bewijs

- C_1500_UP_MID / 15: 167 events, 167 dagen; gemiddeld7,540pt (3,048bp), mediaan4,000pt; positief56,9%; CR195%bp[0,858; 5,238]; ruwp0,006663, Holm2561,000000; MFE/MAE1,578; 6/7 waargenomen kwartalen positief. Dit is geen nieuwe selectie- of handelsregel.
- D_5m_HIGH / 15: 257 events, 122 dagen; gemiddeld11,411pt (5,351bp), mediaan5,500pt; positief54,5%; CR195%bp[0,389; 10,312]; ruwp0,034767, Holm2561,000000; MFE/MAE1,275; 6/7 waargenomen kwartalen positief. Dit is geen nieuwe selectie- of handelsregel.
- C_0930_DOWN_SMALL / 60: 48 events, 48 dagen; gemiddeld35,917pt (15,184bp), mediaan8,500pt; positief54,2%; CR195%bp[0,669; 29,698]; ruwp0,040707, Holm2561,000000; MFE/MAE1,799; 5/7 waargenomen kwartalen positief. Dit is geen nieuwe selectie- of handelsregel.

Het kleine15:00-vervolgeffect op reeds opwaartse dagen met een middengrote RTH-range heeft de laagste ruwe p. Volumeschokken op5m-highs en neerwaartse smalle-overnightcontext zijn andere nominale voorbeelden. Geen daarvan is na de volledige scan statistisch onderscheiden van nul. Extreme overnight-nettoverplaatsingen≥1ATR tellen slechts10 up- en13 down-dagen: grote zichtbare gemiddelden in die groepen zijn onvoldoende onderbouwd. PDH/PDL/ONH/ONL leveren in deze definities evenmin een gecorrigeerd aantoonbare asymmetrie op.


## Kwartaalstabiliteit — alle kwartalen, geen geselecteerde gunstige perioden

Iedere cel publiceert alle8 kalenderkwartalen, inclusief de twee datums30–31december2024 in het korte startkwartaal. Een streep betekent geen events, geen nulresultaat. De CSV bevat per kwartaal ook events, unieke dagen, medianen, positieve fracties en excursies. Deze tabel toont gemiddelde log-bp met eventaantal tussen haakjes; een kwartaal is geen nieuwe holdout.

| Mechanisme | Horizon | 2024Q4 | 2025Q1 | 2025Q2 | 2025Q3 | 2025Q4 | 2026Q1 | 2026Q2 | 2026Q3 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B_EXTREME_ON_UP_0930 | close | — (0) | — (0) | 14,689 (1) | -166,985 (1) | -135,737 (3) | -79,777 (1) | 1,431 (3) | 8,997 (1) |
| B_EXTREME_ON_DOWN_1000 | close | — (0) | 35,805 (1) | 80,572 (4) | 1,093 (1) | 115,152 (1) | — (0) | 106,796 (3) | -24,007 (3) |
| B_EXTREME_ON_UP_1000 | close | — (0) | — (0) | 78,230 (1) | -134,930 (1) | -152,340 (3) | -56,220 (1) | 29,587 (3) | 18,844 (1) |
| C_0930_DOWN_LARGE | 60 | — (0) | -114,849 (1) | -35,516 (4) | -12,640 (2) | -65,174 (3) | -55,245 (1) | -42,787 (4) | -29,122 (2) |
| C_0930_DOWN_LARGE | 30 | — (0) | -99,276 (1) | -66,580 (4) | 15,673 (2) | -39,543 (3) | -2,430 (1) | -23,831 (4) | -0,602 (2) |
| B_EXTREME_ON_DOWN_1000 | 15 | — (0) | 20,528 (1) | -69,423 (4) | -11,247 (1) | 9,086 (1) | — (0) | -37,263 (3) | -15,848 (3) |
| B_EXTREME_ON_DOWN_0930 | close | — (0) | -63,471 (1) | 11,093 (4) | 90,063 (1) | 63,522 (1) | — (0) | 128,127 (3) | -35,546 (3) |
| B_EXTREME_ON_DOWN_0930 | 60 | — (0) | -114,849 (1) | -41,222 (4) | 44,604 (1) | -47,281 (1) | — (0) | -7,658 (3) | -30,984 (3) |
| C_0930_DOWN_LARGE | close | — (0) | -63,471 (1) | -17,432 (4) | 6,974 (2) | -45,962 (3) | 7,092 (1) | -38,664 (4) | -11,162 (2) |
| B_EXTREME_ON_DOWN_0930 | 30 | — (0) | -99,276 (1) | -69,479 (4) | 88,971 (1) | -51,630 (1) | — (0) | 21,331 (3) | -11,539 (3) |
| C_0930_DOWN_SMALL | close | — (0) | 63,163 (6) | -16,826 (8) | 24,426 (9) | 1,001 (12) | 80,270 (3) | 57,228 (3) | 25,276 (7) |
| C_0930_UP_LARGE | close | — (0) | — (0) | 0,553 (3) | — (0) | 38,496 (1) | 39,659 (4) | -13,476 (3) | 41,309 (3) |
| B_EXTREME_ON_UP_0930 | 15 | — (0) | — (0) | -67,631 (1) | -46,746 (1) | -12,511 (3) | 0,675 (1) | -7,003 (3) | -26,028 (1) |
| B_EXTREME_ON_UP_0930 | 30 | — (0) | — (0) | -63,541 (1) | -32,055 (1) | 16,603 (3) | -23,557 (1) | -28,156 (3) | -9,847 (1) |
| B_GAP_DOWN_0930 | close | — (0) | -46,744 (12) | -4,502 (12) | 13,470 (3) | -11,332 (9) | -11,558 (14) | 0,703 (8) | -20,657 (11) |
| C_0930_DOWN_SMALL | 60 | — (0) | 31,289 (6) | -0,149 (8) | 8,210 (9) | 21,553 (12) | 62,566 (3) | -3,692 (3) | 4,733 (7) |
| B_EXTREME_ON_UP_0930 | 60 | — (0) | — (0) | -85,093 (1) | -45,371 (1) | 11,970 (3) | -24,040 (1) | -6,498 (3) | -1,935 (1) |
| B_GAP_DOWN_0930 | 60 | — (0) | -8,752 (12) | -22,605 (12) | -4,168 (3) | -11,983 (9) | -7,607 (14) | -14,077 (8) | -20,237 (11) |
| D_5m_HIGH | close | — (0) | 33,918 (17) | 39,329 (51) | 6,135 (42) | 4,930 (32) | 1,753 (30) | 8,962 (32) | 0,606 (61) |
| A_ONL_REJECT | close | — (0) | -47,412 (18) | -0,280 (18) | 10,221 (22) | -41,781 (16) | 16,058 (21) | -31,217 (10) | -14,411 (20) |
| A_ONH_REJECT | close | — (0) | 37,666 (19) | 25,000 (21) | -5,154 (19) | 14,579 (15) | -55,775 (10) | 18,905 (20) | 19,323 (13) |
| C_0930_DOWN_MID | close | — (0) | -49,438 (15) | -72,764 (13) | 0,502 (10) | 4,090 (13) | 0,933 (26) | 7,069 (13) | 5,921 (24) |
| D_5m_HIGH | 60 | — (0) | 5,184 (13) | 38,375 (48) | 1,087 (39) | 16,976 (29) | 9,411 (26) | 7,528 (30) | -0,556 (59) |
| A_PDL_REJECT | close | — (0) | -39,827 (10) | 25,302 (7) | 14,080 (7) | -31,357 (12) | 3,424 (11) | 4,488 (10) | -33,349 (11) |
| A_ONL_ACCEPT | 60 | 17,643 (2) | -28,020 (13) | -16,944 (7) | 1,873 (14) | -6,467 (19) | 3,154 (16) | -20,822 (16) | -17,218 (14) |
| B_EXTREME_ON_DOWN_0930 | 15 | — (0) | -70,172 (1) | 26,989 (4) | 72,924 (1) | -12,811 (1) | — (0) | 20,608 (3) | -7,530 (3) |
| C_1500_UP_LARGE | 60 | — (0) | -108,253 (1) | 90,672 (4) | -3,697 (2) | -42,737 (4) | -65,447 (1) | 35,609 (3) | -99,299 (3) |
| C_1500_UP_LARGE | close | — (0) | -108,253 (1) | 90,672 (4) | -3,697 (2) | -42,737 (4) | -65,447 (1) | 35,609 (3) | -99,299 (3) |
| B_GAP_DOWN_1000 | 60 | — (0) | -12,647 (12) | -18,427 (12) | -34,303 (3) | 10,593 (9) | -11,504 (14) | -17,233 (8) | 1,676 (11) |
| B_GAP_DOWN_0930 | 30 | — (0) | -11,606 (12) | -18,126 (12) | 35,535 (3) | -11,020 (9) | -8,465 (14) | -1,114 (8) | -12,770 (11) |
| A_ONL_ACCEPT | 30 | 6,180 (2) | -13,126 (13) | -18,085 (7) | 2,606 (14) | -9,096 (19) | 3,680 (16) | -24,804 (16) | -10,100 (14) |
| B_GAP_UP_0930 | close | — (0) | -34,156 (15) | -19,091 (16) | -28,357 (17) | -29,143 (16) | -12,005 (7) | 26,587 (20) | 22,652 (17) |
| C_0930_DOWN_SMALL | 30 | — (0) | 23,089 (6) | 7,527 (8) | 3,519 (9) | 3,699 (12) | 36,571 (3) | -7,977 (3) | 7,161 (7) |
| B_GAP_DOWN_1000 | 15 | — (0) | 11,531 (12) | -33,210 (12) | -16,988 (3) | 4,962 (9) | -8,657 (14) | -18,590 (8) | -2,693 (11) |
| C_1500_DOWN_LARGE | 60 | — (0) | 49,892 (4) | 51,106 (3) | -14,589 (7) | 27,595 (8) | -9,067 (6) | -30,345 (4) | -9,011 (2) |
| C_1500_DOWN_LARGE | close | — (0) | 49,892 (4) | 51,106 (3) | -14,589 (7) | 27,595 (8) | -9,067 (6) | -30,345 (4) | -9,011 (2) |
| C_0930_DOWN_LARGE | 15 | — (0) | -70,172 (1) | 25,389 (4) | 25,651 (2) | 6,125 (3) | 2,127 (1) | 7,642 (4) | -3,518 (2) |
| C_0930_UP_LARGE | 60 | — (0) | — (0) | -31,975 (3) | — (0) | -0,302 (1) | 54,481 (4) | -51,984 (3) | 44,591 (3) |
| C_1500_DOWN_LARGE | 15 | — (0) | 27,332 (4) | 21,548 (3) | -4,963 (7) | 9,511 (8) | -0,084 (6) | 1,399 (4) | 10,597 (2) |
| C_0930_UP_SMALL | close | — (0) | -5,413 (13) | -6,543 (14) | -8,075 (12) | -0,613 (14) | -61,274 (5) | 25,072 (16) | -56,780 (7) |
| A_PDL_REJECT | 15 | — (0) | -13,683 (10) | 17,342 (7) | 11,110 (7) | -21,651 (12) | 4,925 (11) | -1,801 (10) | -27,827 (11) |
| D_1m_HIGH | close | — (0) | 21,332 (71) | 18,740 (231) | 3,409 (167) | -10,191 (153) | 0,724 (136) | 10,690 (136) | 5,163 (215) |
| B_EXTREME_ON_DOWN_1000 | 30 | — (0) | -15,573 (1) | 28,257 (4) | -44,367 (1) | 4,349 (1) | — (0) | -28,989 (3) | -19,444 (3) |
| B_GAP_DOWN_1000 | close | — (0) | -35,138 (12) | 13,624 (12) | -22,065 (3) | -0,312 (9) | -3,092 (14) | 1,817 (8) | -7,887 (11) |
| C_1500_DOWN_LARGE | 30 | — (0) | 40,164 (4) | 10,086 (3) | -10,922 (7) | 11,785 (8) | 1,725 (6) | -2,249 (4) | 1,714 (2) |
| C_1500_UP_LARGE | 15 | — (0) | 23,253 (1) | 30,038 (4) | -3,548 (2) | -2,227 (4) | -19,618 (1) | 19,060 (3) | -19,220 (3) |
| A_PDH_ACCEPT | 30 | — (0) | -2,714 (17) | -25,086 (24) | 5,199 (23) | 4,382 (23) | -6,547 (21) | -7,737 (28) | -5,989 (21) |
| B_GAP_UP_0930 | 30 | — (0) | -2,781 (15) | -14,546 (16) | 0,127 (17) | -9,052 (16) | 5,043 (7) | -14,707 (20) | 4,610 (17) |
| A_ONH_ACCEPT | close | — (0) | 5,411 (16) | 7,883 (20) | 0,601 (13) | -16,005 (22) | -19,453 (20) | 33,166 (23) | 30,567 (14) |
| A_ONH_REJECT | 15 | — (0) | 5,821 (18) | -35,865 (19) | -0,588 (19) | 0,490 (15) | -14,504 (10) | 6,435 (20) | -1,556 (13) |
| A_ONL_REJECT | 30 | — (0) | -12,951 (18) | -15,006 (18) | -8,879 (22) | -9,290 (16) | 17,359 (21) | 6,411 (10) | -12,896 (20) |
| D_5m_HIGH | 15 | — (0) | -6,887 (16) | 15,789 (50) | 4,966 (40) | 5,340 (31) | 4,200 (29) | 1,733 (31) | 2,602 (60) |
| D_1m_HIGH | 60 | — (0) | -6,297 (63) | 17,143 (219) | 0,662 (156) | 4,532 (134) | 1,504 (129) | 5,580 (127) | 2,405 (209) |
| D_5m_LOW | close | — (0) | 21,348 (48) | 12,407 (85) | -11,719 (102) | 32,385 (153) | -11,125 (93) | -4,352 (87) | -11,998 (84) |
| D_5m_HIGH | 30 | — (0) | -3,644 (15) | 11,904 (48) | 3,969 (40) | 9,968 (31) | -1,550 (29) | 7,183 (31) | 2,443 (60) |
| A_ONL_REJECT | 60 | — (0) | -32,343 (18) | 10,255 (18) | -1,175 (22) | -30,293 (16) | 15,940 (20) | 13,779 (10) | -9,183 (20) |
| B_GAP_UP_0930 | 15 | — (0) | 0,017 (15) | -12,787 (16) | -3,296 (17) | -11,407 (16) | 3,762 (7) | -9,333 (20) | 4,244 (17) |
| C_0930_UP_MID | close | — (0) | -113,687 (6) | -28,673 (16) | 5,300 (22) | -46,717 (18) | -0,821 (19) | 45,105 (21) | 15,871 (21) |
| B_GAP_DOWN_1000 | 30 | — (0) | 2,854 (12) | -4,479 (12) | -39,703 (3) | -0,963 (9) | 0,859 (14) | -12,963 (8) | -7,467 (11) |
| B_EXTREME_ON_DOWN_1000 | 60 | — (0) | 10,669 (1) | 18,510 (4) | -20,409 (1) | 33,195 (1) | — (0) | -16,634 (3) | -33,739 (3) |
| C_0930_DOWN_SMALL | 15 | — (0) | 4,606 (6) | -5,312 (8) | 5,496 (9) | 7,957 (12) | 8,914 (3) | 1,038 (3) | 5,124 (7) |
| A_PDH_ACCEPT | 60 | — (0) | 1,138 (17) | -8,922 (24) | 2,669 (23) | 4,955 (23) | -12,628 (21) | -1,164 (28) | -14,484 (21) |
| B_GAP_UP_0930 | 60 | — (0) | -2,013 (15) | -1,972 (16) | -9,311 (17) | -7,892 (16) | 11,658 (7) | -5,329 (20) | -2,426 (17) |
| A_ONL_ACCEPT | 15 | -17,153 (2) | 2,202 (13) | 5,310 (7) | 6,687 (14) | -10,367 (19) | -6,837 (16) | -1,091 (16) | -13,190 (14) |
| D_1m_LOW | close | — (0) | 14,228 (166) | -3,024 (265) | -9,793 (351) | 30,774 (437) | 0,375 (294) | -5,108 (230) | -13,207 (246) |
| C_1500_DOWN_MID | 30 | — (0) | 5,308 (14) | 13,163 (17) | 2,473 (20) | -3,806 (15) | 8,307 (22) | -1,939 (18) | 0,672 (25) |
| C_0930_UP_MID | 15 | — (0) | -21,175 (6) | -8,631 (16) | -1,682 (22) | -4,404 (18) | 2,775 (19) | -4,086 (21) | 0,838 (21) |
| A_ONL_ACCEPT | close | 14,750 (2) | -3,820 (13) | -22,174 (7) | 11,767 (14) | 7,222 (19) | 24,358 (16) | -47,684 (16) | -4,893 (14) |
| B_GAP_UP_1000 | close | — (0) | -31,375 (15) | -4,545 (16) | -28,484 (17) | -20,091 (16) | -17,048 (7) | 41,294 (20) | 18,041 (17) |
| C_0930_DOWN_MID | 15 | — (0) | -5,106 (15) | -21,719 (13) | 11,920 (10) | 11,241 (13) | -5,140 (26) | -8,178 (13) | -0,689 (24) |
| C_1500_UP_SMALL | 60 | — (0) | 4,587 (6) | -11,448 (8) | 7,674 (4) | -6,449 (11) | -1,686 (3) | 1,553 (2) | -2,679 (6) |
| C_1500_UP_SMALL | close | — (0) | 4,587 (6) | -11,448 (8) | 7,674 (4) | -6,449 (11) | -1,686 (3) | 1,553 (2) | -2,679 (6) |
| C_1500_UP_MID | 15 | — (0) | 6,803 (19) | 2,060 (22) | -0,681 (27) | 4,184 (20) | 1,552 (25) | 6,047 (33) | 1,467 (21) |
| C_1500_DOWN_MID | 60 | — (0) | 2,848 (14) | -12,055 (17) | -1,831 (20) | -4,239 (15) | 0,846 (22) | -7,891 (18) | -0,149 (25) |
| C_1500_DOWN_MID | close | — (0) | 2,848 (14) | -12,055 (17) | -1,831 (20) | -4,239 (15) | 0,846 (22) | -7,891 (18) | -0,149 (25) |
| A_PDL_REJECT | 60 | — (0) | -22,188 (9) | 32,113 (7) | 2,755 (7) | -26,129 (12) | 15,366 (11) | 16,104 (9) | -23,948 (10) |
| A_PDL_ACCEPT | 30 | -32,317 (1) | -10,171 (20) | -18,299 (14) | 14,871 (15) | -11,177 (14) | 13,777 (20) | -7,261 (10) | -6,532 (16) |
| A_PDL_ACCEPT | 15 | 2,119 (1) | -0,486 (20) | 4,787 (14) | 8,861 (16) | 2,041 (14) | 4,323 (20) | 2,260 (10) | -0,827 (16) |
| A_PDL_ACCEPT | 60 | 5,887 (1) | 1,155 (20) | -19,175 (14) | 4,034 (15) | -5,849 (14) | 13,377 (20) | -6,752 (10) | -16,099 (16) |
| A_ONH_ACCEPT | 60 | — (0) | 9,013 (16) | 5,687 (19) | -3,323 (12) | 3,976 (21) | -8,493 (20) | 5,930 (22) | 5,470 (14) |
| B_EXTREME_ON_UP_1000 | 30 | — (0) | — (0) | -21,552 (1) | -13,316 (1) | -4,633 (3) | -0,483 (1) | 21,658 (3) | 7,912 (1) |
| C_0930_UP_SMALL | 60 | — (0) | -3,004 (13) | 4,248 (14) | -20,135 (12) | 11,438 (14) | -6,868 (5) | 8,154 (16) | -31,818 (7) |
| A_PDH_REJECT | 60 | — (0) | -4,699 (9) | -9,696 (12) | 3,517 (13) | 5,821 (8) | 0,826 (8) | -3,690 (13) | -5,288 (11) |
| C_0930_DOWN_MID | 60 | — (0) | -6,127 (15) | -24,759 (13) | 1,355 (10) | 0,777 (13) | 8,712 (26) | -6,442 (13) | 0,723 (24) |
| A_PDH_ACCEPT | 15 | — (0) | 8,297 (17) | -20,578 (24) | 2,425 (23) | 0,707 (23) | -7,190 (21) | -0,333 (28) | 6,010 (21) |
| A_PDH_REJECT | close | — (0) | -19,987 (9) | -19,117 (13) | -3,588 (14) | 33,978 (8) | 26,994 (10) | -20,756 (13) | 4,581 (11) |
| B_EXTREME_ON_UP_1000 | 60 | — (0) | — (0) | -7,700 (1) | -54,752 (1) | -20,510 (3) | 7,826 (1) | 33,052 (3) | -3,032 (1) |
| A_PDH_REJECT | 30 | — (0) | -8,189 (9) | -9,009 (12) | -0,732 (13) | 9,566 (8) | 4,392 (10) | -0,954 (13) | -6,033 (11) |
| B_GAP_UP_1000 | 30 | — (0) | 0,768 (15) | 12,574 (16) | -9,438 (17) | 1,160 (16) | 6,615 (7) | 9,378 (20) | -7,036 (17) |
| A_PDH_ACCEPT | close | — (0) | -18,270 (17) | -5,044 (25) | -2,232 (23) | -27,316 (23) | -1,958 (21) | 31,334 (28) | 1,168 (21) |
| B_GAP_DOWN_0930 | 15 | — (0) | -5,272 (12) | -1,020 (12) | 35,475 (3) | 14,356 (9) | -13,603 (14) | 8,417 (8) | -13,498 (11) |
| C_1500_UP_MID | 30 | — (0) | 1,078 (19) | -0,201 (22) | 0,361 (27) | 3,052 (20) | -1,910 (25) | 5,389 (33) | 1,640 (21) |
| C_1500_DOWN_MID | 15 | — (0) | 5,636 (14) | -2,231 (17) | 2,214 (20) | -1,065 (15) | 3,394 (22) | -3,232 (18) | 4,222 (25) |
| C_1500_DOWN_SMALL | 60 | — (0) | -56,513 (1) | 1,684 (8) | 0,098 (3) | 6,672 (4) | -2,284 (3) | -12,991 (2) | 1,176 (7) |
| C_1500_DOWN_SMALL | close | — (0) | -56,513 (1) | 1,684 (8) | 0,098 (3) | 6,672 (4) | -2,284 (3) | -12,991 (2) | 1,176 (7) |
| C_1500_UP_SMALL | 30 | — (0) | 0,097 (6) | -10,446 (8) | 0,382 (4) | 1,179 (11) | -2,497 (3) | -5,236 (2) | 4,845 (6) |
| C_1500_UP_LARGE | 30 | — (0) | 25,672 (1) | 48,564 (4) | -6,447 (2) | -15,600 (4) | -59,560 (1) | 23,389 (3) | -43,162 (3) |
| D_5m_LOW | 60 | — (0) | 5,603 (48) | -18,809 (77) | -6,807 (102) | 15,667 (145) | 8,806 (92) | 8,458 (87) | -12,449 (84) |
| C_0930_UP_MID | 30 | — (0) | -56,727 (6) | -2,415 (16) | -0,833 (22) | 1,034 (18) | 5,579 (19) | 6,195 (21) | -1,395 (21) |
| D_1m_HIGH | 15 | — (0) | -4,103 (69) | 4,708 (226) | 2,235 (162) | 1,774 (144) | -3,943 (134) | 0,183 (129) | 1,468 (212) |
| A_PDL_REJECT | 30 | — (0) | -12,151 (10) | 33,184 (7) | 16,316 (7) | -19,434 (12) | 7,072 (11) | 10,362 (9) | -8,021 (11) |
| C_0930_UP_SMALL | 30 | — (0) | 9,918 (13) | 5,997 (14) | -20,128 (12) | 10,653 (14) | -12,773 (5) | -5,765 (16) | -7,344 (7) |
| C_1500_DOWN_SMALL | 30 | — (0) | -19,523 (1) | 1,699 (8) | 2,615 (3) | 10,062 (4) | 1,438 (3) | -11,145 (2) | 0,778 (7) |
| D_5m_LOW | 15 | — (0) | -1,022 (48) | -14,566 (84) | 0,481 (102) | 3,865 (152) | 2,857 (93) | -3,513 (87) | 0,120 (84) |
| D_5m_LOW | 30 | — (0) | -2,413 (48) | -20,937 (83) | -2,949 (102) | 6,543 (149) | 4,137 (92) | 5,056 (87) | -3,470 (84) |
| A_ONL_REJECT | 15 | — (0) | -8,013 (18) | 4,612 (18) | -6,186 (22) | -13,653 (16) | 19,338 (21) | 10,671 (10) | -10,823 (20) |
| A_ONH_ACCEPT | 30 | — (0) | 1,016 (16) | 6,558 (19) | -6,201 (12) | -1,576 (22) | -16,843 (20) | 5,105 (23) | 4,944 (14) |
| D_1m_LOW | 60 | — (0) | -1,412 (165) | -19,295 (232) | -3,914 (350) | 13,637 (413) | 11,140 (281) | 7,371 (230) | -10,550 (246) |
| D_1m_HIGH | 30 | — (0) | -10,112 (68) | 6,328 (223) | 1,002 (161) | 2,016 (142) | -5,658 (134) | -0,003 (129) | 2,420 (211) |
| C_1500_UP_MID | 60 | — (0) | 1,283 (19) | -0,203 (22) | 0,896 (27) | -1,458 (20) | -0,901 (25) | 4,950 (33) | -1,243 (21) |
| C_1500_UP_MID | close | — (0) | 1,283 (19) | -0,203 (22) | 0,896 (27) | -1,458 (20) | -0,901 (25) | 4,950 (33) | -1,243 (21) |
| A_ONH_REJECT | 30 | — (0) | 18,608 (18) | -11,471 (19) | 4,082 (19) | -4,096 (15) | -14,843 (10) | 5,171 (20) | -0,358 (13) |
| A_PDL_ACCEPT | close | 9,067 (1) | -5,461 (20) | -14,228 (14) | -1,569 (16) | 7,864 (14) | 9,772 (20) | 2,056 (10) | -4,997 (16) |
| C_0930_DOWN_MID | 30 | — (0) | -4,214 (15) | -14,032 (13) | 15,668 (10) | 0,386 (13) | 4,642 (26) | 1,837 (13) | -5,809 (24) |
| C_0930_UP_LARGE | 30 | — (0) | — (0) | -21,274 (3) | — (0) | 25,446 (1) | 34,157 (4) | -65,421 (3) | 35,634 (3) |
| B_EXTREME_ON_UP_1000 | 15 | — (0) | — (0) | 24,145 (1) | -0,211 (1) | -23,093 (3) | 6,184 (1) | 12,689 (3) | 7,323 (1) |
| B_GAP_UP_1000 | 15 | — (0) | -0,057 (15) | 4,946 (16) | -3,984 (17) | -1,877 (16) | 1,350 (7) | 9,748 (20) | -14,557 (17) |
| C_0930_UP_LARGE | 15 | — (0) | — (0) | -14,989 (3) | — (0) | -5,339 (1) | 34,644 (4) | -32,008 (3) | 4,981 (3) |
| A_ONH_ACCEPT | 15 | — (0) | -5,301 (16) | 6,003 (19) | 0,758 (12) | -1,538 (22) | -10,166 (20) | 3,080 (23) | 4,869 (14) |
| A_PDH_REJECT | 15 | — (0) | -5,804 (9) | 2,212 (13) | 2,456 (13) | 10,748 (8) | 2,090 (10) | -9,482 (13) | 3,551 (11) |
| C_0930_UP_SMALL | 15 | — (0) | 2,797 (13) | 4,663 (14) | -8,880 (12) | 6,130 (14) | -5,080 (5) | 2,878 (16) | -9,831 (7) |
| D_1m_LOW | 15 | — (0) | 2,439 (166) | -10,971 (260) | 1,498 (350) | 1,339 (433) | 3,499 (291) | -1,533 (230) | 0,306 (246) |
| A_ONH_REJECT | 60 | — (0) | 20,873 (18) | -27,099 (17) | 1,936 (19) | 7,838 (15) | -34,559 (10) | 13,986 (20) | 2,249 (13) |
| C_1500_DOWN_SMALL | 15 | — (0) | -6,435 (1) | -2,199 (8) | 2,678 (3) | 6,361 (4) | 0,991 (3) | -9,124 (2) | -0,241 (7) |
| C_0930_UP_MID | 60 | — (0) | -23,873 (6) | 12,542 (16) | -0,178 (22) | -3,588 (18) | 6,160 (19) | 1,947 (21) | -5,501 (21) |
| B_GAP_UP_1000 | 60 | — (0) | -9,957 (15) | 16,521 (16) | -20,968 (17) | -4,520 (16) | 3,760 (7) | 21,615 (20) | -9,991 (17) |
| C_1500_UP_SMALL | 15 | — (0) | 5,321 (6) | -3,469 (8) | -3,943 (4) | 0,540 (11) | 1,339 (3) | -6,809 (2) | 3,694 (6) |
| D_1m_LOW | 30 | — (0) | -1,876 (165) | -14,583 (253) | -0,096 (350) | 3,489 (424) | 5,998 (283) | 4,986 (230) | -2,203 (246) |

## Replicatie en bescherming

Byte-identieke event/horizonreplay SHA-256: `50bb51d5492178d676371ed3dce3dba484f94a620c213be36e4af0f2490f099e`. 115 beschermde experimentbestanden en alle eerdere ruwe-markt- en wegingsauditpublicaties blijven ongewijzigd. Geen simulator-, entry-, stop-, target- of netto-P&L-aanroepen. Ruwe CSV’s en eventledgers blijven uitsluitend privé.

Tekstuele erratum: het vóór de run vergrendelde protocol noemt2024Q4 ten onrechte een one-day-kwartaal. Het bronuniversum bevat30én31december2024. De daadwerkelijke eventberekeningen en kwartaalindeling gebruiken beide datums correct. De oorspronkelijke lock blijft intact; de verduidelijking is apart vastgelegd in research/causal-map-clarifications.json. Geen selectieregel, drempel of uitkomst is gewijzigd.

Reproduceerbare route: `.venv/bin/python -B -m scripts.causal_map --verify` controleert de afgesloten run zonder opnieuw te scannen. De broncode ondersteunt de volledige vaste batch wanneer de afzonderlijke outputmap nog niet bestaat. `python -m scripts.publish_causal_map` publiceert uitsluitend de geverifieerde aggregaten. De gesloten run weigert uitkomstgestuurde herhalingen.

## Methodologische bronnen

- Clusterafhankelijke inferentie: [Cameron & Miller, A Practitioner’s Guide to Cluster-Robust Inference](https://old.econ.ucdavis.edu/research/papers.html). Onderbouwing voor afhankelijkheid binnen clusters; geen bewijs voor een NQ-effect.
- [Nasdaq Opening and Closing Crosses](https://www.nasdaqtrader.com/trader.aspx?id=openclose): opening/closing auctioncontext van aandelen. Onze NQ-minuutbars bevatten geen NOII/veilingorderstromen; een15:00-tijdvenster mag daarom niet als bewezen MOC-flow worden benoemd.
