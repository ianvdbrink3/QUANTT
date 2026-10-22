# Ochtendherstel: strikt gescheiden eerste kwartier en vervolgvenster

Beschrijvende metingen op de bestaande data, geen handelsmodel of nieuwe significantietoets. De afzonderlijke15:00-kandidaatregistratie is vóór deze uitkomsten bevroren; er zijn geen nieuwe15:00-rendementen berekend.

## Vensters

| Onderdeel | Definitie |
|---|---|
| Tijdzone | America/New_York, bestaande DST-bewuste parser |
| Indeling eerste kwartier | 09:30 Open → 09:44 Close; strikt negatief, positief of exact vlak |
| Uitsluitend gerapporteerd vervolgrendement | 09:45 Open → 10:29 Close,45 minuten, opwaarts positief |
| Geen tijdsoverlap | Geen bar09:30–09:44 of close/open-gap op09:45 in het vervolgresultaat |
| Prijzen | Ruwe actieve contractprijzen; geen contract- of dagovergang in beide vensters |
| Selectie | Bestaande69 Gap-Down- en101 A_ONL_ACCEPT/60m-dagen;21 overlap;149 unieke dagen |
| Interpretatie | Bruto prijsverdeling, geen winstpercentage van een uitvoerbare strategie. Tijdstipcausaliteit onder BAR_START_SUPPORTED_INTERNAL_ONLY, geen bewezen economische oorzaak |

## A.69 Gap-Down-dagen naar het eerste kwartier

| Groep | N | Gem. pt | P10 | P25 | Mediaan | P75 | P90 | Opwaarts % | Gem. log-bp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Negatief / doorzakkend | 29 | 57,457 | -149,850 | -106,750 | 65,250 | 140,750 | 237,450 | 62,069 | 24,151 |
| Positief / opverend | 40 | 5,325 | -132,250 | -50,250 | 32,750 | 68,750 | 130,725 | 60,000 | 3,065 |
| Vlak | 0 | — | — | — | — | — | — | — | — |

Alle getoonde rendementen horen uitsluitend bij09:45–10:30. Vlakke dagen blijven een aparte rij, ook wanneer N=0. Kwantielen gebruiken lineaire interpolatie.

## B. Gevraagde149 dagen: retrospectieve groepsindeling

**De48/80/21-indeling is niet volledig point-in-time om09:45.** Bij55 van101 ONL-dagen is de eerste bevestigingsclose pas later bekend, waarvan29 na10:30. Ook het label alleen-Gap-Down gebruikt achteraf de afwezigheid van een ONL-event in de vaste dagset. Deze tabel is uitsluitend een beschrijving achteraf, geen causale voorspelling vanaf09:45.

| Groep | N | Gem. pt | P10 | P25 | Mediaan | P75 | P90 | Opwaarts % | Gem. log-bp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Alleen Gap-Down (achteraf) | 48 | 23,656 | -170,150 | -65,375 | 46,625 | 92,125 | 150,375 | 64,583 | 11,227 |
| Alleen ONL (achteraf) | 80 | -26,959 | -184,225 | -99,000 | -31,125 | 44,938 | 93,800 | 40,000 | -10,216 |
| Beide (achteraf) | 21 | 35,417 | -113,250 | -45,500 | 14,500 | 124,000 | 175,250 | 52,381 | 13,530 |

### Beschikbaarheid van ONL op het meetmoment

| Retrospectieve groep | N | ONL bekend uiterlijk09:45 | ONL later t/m10:30 | ONL na10:30 |
|---|---:|---:|---:|---:|
| Alleen Gap-Down (achteraf) | 48 | 0 | 0 | 0 |
| Alleen ONL (achteraf) | 80 | 32 | 23 | 25 |
| Beide (achteraf) | 21 | 14 | 3 | 4 |

## C. Afzonderlijke point-in-time vergelijking:101 dagen

Om09:45 zijn69 Gap-Down- en46 ONL-dagen bekend, met14 overlap:101 unieke dagen. De groepen zijn55/32/14. De7 Gap-Down-dagen met pas latere ONL schuiven naar Gap-Down, nog geen ONL bekend. De48 niet-Gap-Down-dagen met pas latere ONL selecteren dit meetmoment niet. Dit is geen uitkomstgestuurde uitsluiting of vervanging van de gevraagde149-tabel.

| Groep | N | Gem. pt | P10 | P25 | Mediaan | P75 | P90 | Opwaarts % | Gem. log-bp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Gap-Down, nog geen ONL om09:45 | 55 | 18,514 | -153,550 | -67,250 | 36,250 | 93,000 | 144,050 | 60,000 | 8,334 |
| ONL bekend09:45, geen Gap-Down | 32 | -12,953 | -179,850 | -99,188 | -27,750 | 75,438 | 160,600 | 46,875 | -4,692 |
| Beide bekend09:45 | 14 | 61,500 | -84,600 | -6,125 | 37,375 | 146,375 | 209,900 | 64,286 | 26,044 |

## Beschrijvende verschillen tussen groepen

Verschillen zijn groepA minus groepB. Geen p-waarden, interval, significantieclaim of geselecteerde winnaar.

| Indeling | Vergelijking | Verschil gemiddelde pt | Verschil mediaan pt |
|---|---|---:|---:|
| RETROSPECTIVE_149 | Alleen Gap-Down (achteraf) minus Alleen ONL (achteraf) | 50,616 | 77,750 |
| RETROSPECTIVE_149 | Alleen Gap-Down (achteraf) minus Beide (achteraf) | -11,760 | 32,125 |
| RETROSPECTIVE_149 | Alleen ONL (achteraf) minus Beide (achteraf) | -62,376 | -45,625 |
| KNOWN_AT_0945 | Gap-Down, nog geen ONL om09:45 minus ONL bekend09:45, geen Gap-Down | 31,467 | 64,000 |
| KNOWN_AT_0945 | Gap-Down, nog geen ONL om09:45 minus Beide bekend09:45 | -42,986 | -1,125 |
| KNOWN_AT_0945 | ONL bekend09:45, geen Gap-Down minus Beide bekend09:45 | -74,453 | -65,125 |

## Afzonderlijk bevroren15:00-specificatie

Zie `AFTERNOON_CANDIDATE_PREREGISTRATION.md` en `research/afternoon-candidate-v1.json`. Primaire horizon15:00-open→15:14-close; secundair15:00-open→15:01-close; één tweezijdige Holm2-familie. Status CANDIDATE_SPEC_FROZEN_INDEPENDENT_TEST_NOT_RELEASED. Geen toekomstige toets zonder afzonderlijk vooraf vastgelegd datavenster/stopregel.

## Verificatie

69 bronbestanden op hashes gecontroleerd; 149 prefix- en evenveel toekomstmutatiecontroles; verse bronreplay byte-identiek; 115 beschermde archiefbestanden ongewijzigd. Geen nieuwe strategie-runs,15:00-runs of p-waarden. Ruwe prijsarrays en meetregels blijven in de genegeerde artifacts-map. Geen GitHub/Vercel-publicatie in deze opdracht.

Protocol SHA-256: `49da7ac9f94d807a943879bb7489ba135ea95e98158786f40d5e492d5be097d8`.
Afzonderlijke kandidaat-lock SHA-256: `3eb649eab7082e95374285beb1f0452254cd1b5e4e23b26190b59d634811cd45`.
