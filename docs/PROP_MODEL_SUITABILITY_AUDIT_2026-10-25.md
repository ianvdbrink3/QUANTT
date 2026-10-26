# Prop-firm geschiktheid: bouwstenenaudit — 25 oktober 2026

Status: ONTWIKKELINGSONDERZOEK; GEEN GEVALIDEERD PROP-MODEL.

Deze audit hergroepeert uitsluitend bestaande, gevulde intraday-kandidaten uit de
gepubliceerde challenge-run. Geen nieuwe signalen, parameters, stops of targets.
De eerdere challenge-resultaten en de S1/S2-benchmarks blijven ongewijzigd.

## Gemeten bouwstenen

Eén MNQ wordt benaderd met NQ-prijzen, $2 per punt. $3,22 roundtrip omvat het
bestaande commissie-/slippage-rekenmodel; $6,50 is een kostenscenario. Geen van beide
is een gecontroleerde persoonlijke brokerquote. Initial-stop-R = netto dollars /
(oorspronkelijke stopafstand in punten × $2). Dit is geen uitgevoerde position-sizing
met gehele contracten en geen garantie dat een stop tegen de stopprijs wordt gevuld.

Elke rij is zelfstandig gemeten: overlappende kandidaten kunnen niet zomaar worden
opgeteld. Handelsfrequentie is een gemiddelde per 21 cashsessies, geen maandgarantie.
De eerste periode bevat 749 cashsessies; de tweede 422 (feitelijk vanaf 27 januari
2025, ondanks de bestaande bronlabelnaam 2024_2026). De gecombineerde pool is al
bekeken en geselecteerd; positieve cijfers vormen geen onafhankelijke bevestiging.

| Bouwsteen | Periode | N | Trades/21 | Gem. netto $/MNQ | PF $ | Gem. netto stop-R | PF stop-R | Mediaan duur (min) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| J0830 | 2019_2021 | 68 | 1.91 | 10.31 | 1.187 | 0.093 | 1.184 | 229.0 |
| JBULL0930 | 2019_2021 | 39 | 1.09 | 0.45 | 1.009 | 0.171 | 1.399 | 330.0 |
| J1M_TIME | 2019_2021 | 68 | 1.91 | 10.79 | 1.240 | 0.153 | 1.262 | 195.0 |
| PULLBACK | 2019_2021 | 79 | 2.21 | -1.17 | 0.967 | -0.034 | 0.883 | 115.0 |
| ICT1 | 2019_2021 | 126 | 3.53 | 8.07 | 1.179 | -0.077 | 0.878 | 147.5 |
| SB_AM | 2019_2021 | 20 | 0.56 | 8.86 | 1.273 | 0.115 | 1.177 | 38.5 |
| SB_PM | 2019_2021 | 96 | 2.69 | 3.56 | 1.149 | 0.024 | 1.037 | 21.5 |
| J0830 | 2024_2026 | 32 | 1.59 | 51.15 | 1.442 | 0.143 | 1.298 | 233.5 |
| JBULL0930 | 2024_2026 | 18 | 0.90 | 54.47 | 1.759 | 0.337 | 1.956 | 313.0 |
| J1M_TIME | 2024_2026 | 22 | 1.09 | 68.83 | 1.978 | 0.509 | 2.081 | 332.0 |
| PULLBACK | 2024_2026 | 42 | 2.09 | -16.53 | 0.806 | -0.030 | 0.888 | 126.5 |
| ICT1 | 2024_2026 | 82 | 4.08 | 0.44 | 1.004 | -0.019 | 0.968 | 144.5 |
| SB_AM | 2024_2026 | 6 | 0.30 | -18.14 | 0.788 | 0.126 | 1.239 | 165.5 |
| SB_PM | 2024_2026 | 38 | 1.89 | 10.83 | 1.210 | 0.142 | 1.240 | 35.0 |

## Kostengevoeligheid: gemiddeld netto dollarresultaat per 1 MNQ

| Bouwsteen | Periode | Bij $3,22 RT | Bij $6,50 RT |
|---|---|---:|---:|
| J0830 | 2019_2021 | 10.31 | 7.03 |
| JBULL0930 | 2019_2021 | 0.45 | -2.83 |
| J1M_TIME | 2019_2021 | 10.79 | 7.51 |
| PULLBACK | 2019_2021 | -1.17 | -4.45 |
| ICT1 | 2019_2021 | 8.07 | 4.79 |
| SB_AM | 2019_2021 | 8.86 | 5.58 |
| SB_PM | 2019_2021 | 3.56 | 0.28 |
| J0830 | 2024_2026 | 51.15 | 47.88 |
| JBULL0930 | 2024_2026 | 54.47 | 51.19 |
| J1M_TIME | 2024_2026 | 68.83 | 65.55 |
| PULLBACK | 2024_2026 | -16.53 | -19.81 |
| ICT1 | 2024_2026 | 0.44 | -2.84 |
| SB_AM | 2024_2026 | -18.14 | -21.42 |
| SB_PM | 2024_2026 | 10.83 | 7.55 |

## Wat dit betekent

1. De na-10:15 Pullback is in beide perioden netto negatief. De late ICT1 is in
   dollars licht positief, maar negatief in initial-stop-R in beide perioden.
   Ze leveren dus geen aangetoonde risicogenormaliseerde verbetering door ze aan
   Judas toe te voegen. Dit verandert de oorspronkelijke, onbeperkte Pullback niet.
2. Judas heeft circa 1–2 trades per 21 sessies per variant. De gehouden posities
   duren mediaan meerdere uren. Een ochtend-entry betekent geen vrijgevallen
   account voor een tweede ochtend-/middagstrategie. Variantentellingen optellen
   overschat uitvoerbaar volume.
3. SB_PM houdt korter vast, maar heeft circa 2–3 trades per 21 sessies en een kleine
   opbrengst per micro. Het is geen aangetoonde oplossing voor een maandchallenge.
4. De bestaande rolling-studie vond geen combinatie met minstens 10% bekende
   21-sessies-pass-rate in beide perioden. Die grens was een onderzoeksscreen,
   geen bewijscriterium voor toekomstige winst. Ontbrekende overnight-paden en
   achteraf geselecteerde combinaties begrenzen de uitspraken verder.

## Juiste doel: van evaluatie tot uitbetaling

Regels gecontroleerd op 25 oktober 2026; exacte plan en accountfase moeten steeds
apart worden vastgelegd. De eerdere MFFU-simulatie betreft Rapid EOD, niet Builder.

- Topstep Combine 50K: 55% consistency en maximaal 50 micros; de evaluatiewinst
  gaat niet mee naar Express Funded. Automatisering is onder voorwaarden toegestaan.
- Topstep Express: Standard vereist vijf winstdagen van minstens $150 voor payout;
  Consistency drie handelsdagen en 40% consistency. Na een uitbetaling staat de
  verliesvloer permanent op nul. Daarom is pass-rate alleen geen passend einddoel.
- MFFU Builder Default 50K: $3.000 target, $2.000 EOD-verliesvloer, $1.000 dagelijkse
  soft pause en geen consistency in de evaluatie. Sim Funded heeft wél 7 kalenderdagen
  inactiviteitslimiet en 50% payout-consistency. Voor de eerste payout is minimaal
  $2.600 nodig: $2.100 buffer plus $500. De eerdere Rapid EOD-pass-rates mogen niet
  als Builder-resultaten worden gepresenteerd.

Een doel van $3.000 vereist rekenkundig gemiddeld $150 netto bij 20 trades, of $100
bij 30 trades. Dat zijn schaalreferenties, geen vereiste of voorspelling per trade:
variantie, volgorde, trailing floor en consistency bepalen de feitelijke slaagkans.
Meer contracten verhogen zowel opbrengst als het verliesrisico.

## Afgebakend vervolgonderzoek

Onderzoek één intraday-kandidaat met volledige bronpaden en begrensd initiëel risico,
met vooraf vastgelegde regels en een bekende economische reden voor de entry.
Geen nieuwe brede combinatie-/sizingzoektocht en geen verplichte trades voor volume
of inactiviteit. Kies niet achteraf een stop op basis van de beste challenge-score.

Voeg eerst een plan-specifieke levenscyclus toe aan de bestaande meetlat: evaluatie,
nieuw funded beginsaldo, payout-eisen, uitbetaling, resterende verliesbuffer en
overleving daarna. Rapporteer kans op eerste én tweede payout vóór breach, dagen
tot payout en netto ontvangen dollars na evaluatie-, reset- en activatiekosten.
Gebruik geen andere regels om oude resultaten gunstiger te labelen.

Een definitieve kandidaat moet daarna op ongebruikte data of forward paper worden
gemeten met vooraf vastgelegde looptijd/steekproef en faalcriteria. Schijnbaar
gunstige resultaten op deze ontwikkelingspool zijn onvoldoende voor aankoop of
livehandel. Er is in deze audit geen nieuw model gevalideerd en geen account gekocht.

## Bronnen en reproduceerbaarheid

Uitvoeren: `.venv/bin/python -m scripts.audit_prop_components`.
Private kandidaat- en kalenderbestanden worden niet naar publieke output gekopieerd.
De CSV bevat uitsluitend aggregaten. Geen nieuw inferentieel bewijs of p-waarde
uit een achteraf geselecteerde groep; dit is een beschrijvende audit.

- [Topstep evaluation](https://help.topstep.com/en/articles/8284197-trading-combine-parameters)
- [Topstep payouts](https://help.topstep.com/en/articles/8284233-topstep-payout-policy)
- [MFFU Builder](https://help.myfundedfutures.com/en/articles/14290805-builder-plan-50k-a-comprehensive-guide)

Bronhashes SHA-256:

- `candidates.json`: `9b543b4a8e05b96d6e1569d3c8d74f8b481f0c206c79226fd57049861137b1eb`
- `cash-calendar.json`: `8ab82db1a2ed134c1f0d926b4167c121ba4865eaf5703ec2eb561d65d95876de`
