# Accountlevenscyclus S1/S2-Judas — 26 oktober 2026

Status: BESCHRIJVEND ONTWIKKELINGSONDERZOEK; GEEN PROP-FIRM-GOEDKEURING.

Uitsluitend drie bestaande modellen op 1 of 2 MNQ, exacte 18:00-entry en twee
bestaande Judas-varianten. Geen derde intraday-motor of nieuwe signaalzoektocht.
Alle 1.171 cashsessies zijn ontwikkelingsdata. Huidige regels worden retrospectief
toegepast op NQ-prijzen als MNQ-proxy. Voor MNQ zijn $3,22 Topstep en voorlopig
$6,50 Builder roundtrip aangenomen, inclusief slippage; geen persoonlijke fillquote.

## Hoofdvergelijking: gelijk venster van 252 cashsessies

Elke accountstart heeft een volledig jaar aan mogelijke follow-up (498 starts in
2019–2021; 171 in het recentere blok). De recente feitelijke reeks begint 27 januari
2025. Geen sprong over ontbrekende jaren. Kolommen payout zijn percentages van ALLE
gestarte accounts. Dezelfde dagen overlappen tussen starts; geen onafhankelijke
herhaalde experimenten en geen confirmatoire p-waarden.

Een account stopt na de tweede payout, een floor-/inactiviteitsbreuk of de horizon.
Actieve accounts zijn gecensureerd, niet mislukt. 'Netto $' is ontvangen cash na
winstdeling minus betaalde abonnementen en activatie, tot dit eindpunt. Dit is geen
verwachting over de resterende levensduur. Achtergebleven simulatie-equity is geen
ontvangen inkomen. UNKNOWN heeft onopgeloste bronminuten: dan is de all-start
puntverwachting niet identificeerbaar en staat er ONBEKEND.

| Firm/payout-route | Model | MNQ | Periode | Starts | Eval gehaald % | Payout1 % | Payout2 % | Unknown % | Actief einde % | Netto $/start |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | 1 | 2019_2021 | 498 | 0.00 | 0.00 | 0.00 | 80.72 | 19.28 | ONBEKEND |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | 1 | 2024_2026 | 171 | 78.95 | 8.19 | 0.00 | 8.19 | 25.15 | ONBEKEND |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | 1 | COMBINED | 669 | 20.18 | 2.09 | 0.00 | 62.18 | 20.78 | ONBEKEND |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | 2 | 2019_2021 | 498 | 0.00 | 0.00 | 0.00 | 80.72 | 19.28 | ONBEKEND |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | 2 | 2024_2026 | 171 | 81.87 | 52.05 | 0.00 | 8.19 | 12.87 | ONBEKEND |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | 2 | COMBINED | 669 | 20.93 | 13.30 | 0.00 | 62.18 | 17.64 | ONBEKEND |
| TOPSTEP_STANDARD | S1-Judas-0830 | 1 | 2019_2021 | 498 | 0.00 | 0.00 | 0.00 | 80.72 | 19.28 | ONBEKEND |
| TOPSTEP_STANDARD | S1-Judas-0830 | 1 | 2024_2026 | 171 | 38.60 | 0.00 | 0.00 | 8.19 | 39.77 | ONBEKEND |
| TOPSTEP_STANDARD | S1-Judas-0830 | 1 | COMBINED | 669 | 9.87 | 0.00 | 0.00 | 62.18 | 24.51 | ONBEKEND |
| TOPSTEP_STANDARD | S1-Judas-0830 | 2 | 2019_2021 | 498 | 0.00 | 0.00 | 0.00 | 80.72 | 19.28 | ONBEKEND |
| TOPSTEP_STANDARD | S1-Judas-0830 | 2 | 2024_2026 | 171 | 61.40 | 42.11 | 0.00 | 8.19 | 0.00 | ONBEKEND |
| TOPSTEP_STANDARD | S1-Judas-0830 | 2 | COMBINED | 669 | 15.70 | 10.76 | 0.00 | 62.18 | 14.35 | ONBEKEND |
| TOPSTEP_STANDARD | S2-Judas | 1 | 2019_2021 | 498 | 0.00 | 0.00 | 0.00 | 100.00 | 0.00 | ONBEKEND |
| TOPSTEP_STANDARD | S2-Judas | 1 | 2024_2026 | 171 | 0.00 | 0.00 | 0.00 | 100.00 | 0.00 | ONBEKEND |
| TOPSTEP_STANDARD | S2-Judas | 1 | COMBINED | 669 | 0.00 | 0.00 | 0.00 | 100.00 | 0.00 | ONBEKEND |
| TOPSTEP_STANDARD | S2-Judas | 2 | 2019_2021 | 498 | 0.20 | 0.00 | 0.00 | 91.57 | 0.00 | ONBEKEND |
| TOPSTEP_STANDARD | S2-Judas | 2 | 2024_2026 | 171 | 3.51 | 0.00 | 0.00 | 63.74 | 0.00 | ONBEKEND |
| TOPSTEP_STANDARD | S2-Judas | 2 | COMBINED | 669 | 1.05 | 0.00 | 0.00 | 84.45 | 0.00 | ONBEKEND |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | 1 | 2019_2021 | 498 | 0.00 | 0.00 | 0.00 | 80.72 | 19.28 | ONBEKEND |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | 1 | 2024_2026 | 171 | 78.95 | 0.00 | 0.00 | 8.19 | 25.15 | ONBEKEND |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | 1 | COMBINED | 669 | 20.18 | 0.00 | 0.00 | 62.18 | 20.78 | ONBEKEND |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | 2 | 2019_2021 | 498 | 0.00 | 0.00 | 0.00 | 80.72 | 19.28 | ONBEKEND |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | 2 | 2024_2026 | 171 | 81.87 | 59.65 | 0.00 | 8.19 | 12.87 | ONBEKEND |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | 2 | COMBINED | 669 | 20.93 | 15.25 | 0.00 | 62.18 | 17.64 | ONBEKEND |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | 1 | 2019_2021 | 498 | 0.00 | 0.00 | 0.00 | 80.72 | 19.28 | ONBEKEND |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | 1 | 2024_2026 | 171 | 38.60 | 0.00 | 0.00 | 8.19 | 39.77 | ONBEKEND |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | 1 | COMBINED | 669 | 9.87 | 0.00 | 0.00 | 62.18 | 24.51 | ONBEKEND |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | 2 | 2019_2021 | 498 | 0.00 | 0.00 | 0.00 | 80.72 | 19.28 | ONBEKEND |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | 2 | 2024_2026 | 171 | 61.40 | 53.22 | 20.47 | 8.19 | 0.00 | ONBEKEND |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | 2 | COMBINED | 669 | 15.70 | 13.60 | 5.23 | 62.18 | 14.35 | ONBEKEND |
| TOPSTEP_CONSISTENCY | S2-Judas | 1 | 2019_2021 | 498 | 0.00 | 0.00 | 0.00 | 100.00 | 0.00 | ONBEKEND |
| TOPSTEP_CONSISTENCY | S2-Judas | 1 | 2024_2026 | 171 | 0.00 | 0.00 | 0.00 | 100.00 | 0.00 | ONBEKEND |
| TOPSTEP_CONSISTENCY | S2-Judas | 1 | COMBINED | 669 | 0.00 | 0.00 | 0.00 | 100.00 | 0.00 | ONBEKEND |
| TOPSTEP_CONSISTENCY | S2-Judas | 2 | 2019_2021 | 498 | 0.20 | 0.00 | 0.00 | 91.57 | 0.00 | ONBEKEND |
| TOPSTEP_CONSISTENCY | S2-Judas | 2 | 2024_2026 | 171 | 3.51 | 0.00 | 0.00 | 63.74 | 0.00 | ONBEKEND |
| TOPSTEP_CONSISTENCY | S2-Judas | 2 | COMBINED | 669 | 1.05 | 0.00 | 0.00 | 84.45 | 0.00 | ONBEKEND |
| MFFU_BUILDER | S1-Judas-Bull0930 | 1 | 2019_2021 | 498 | 0.00 | 0.00 | 0.00 | 9.84 | 0.00 | ONBEKEND |
| MFFU_BUILDER | S1-Judas-Bull0930 | 1 | 2024_2026 | 171 | 0.00 | 0.00 | 0.00 | 2.92 | 0.00 | ONBEKEND |
| MFFU_BUILDER | S1-Judas-Bull0930 | 1 | COMBINED | 669 | 0.00 | 0.00 | 0.00 | 8.07 | 0.00 | ONBEKEND |
| MFFU_BUILDER | S1-Judas-Bull0930 | 2 | 2019_2021 | 498 | 0.00 | 0.00 | 0.00 | 9.84 | 0.00 | ONBEKEND |
| MFFU_BUILDER | S1-Judas-Bull0930 | 2 | 2024_2026 | 171 | 0.00 | 0.00 | 0.00 | 2.92 | 0.00 | ONBEKEND |
| MFFU_BUILDER | S1-Judas-Bull0930 | 2 | COMBINED | 669 | 0.00 | 0.00 | 0.00 | 8.07 | 0.00 | ONBEKEND |
| MFFU_BUILDER | S1-Judas-0830 | 1 | 2019_2021 | 498 | 0.00 | 0.00 | 0.00 | 10.04 | 0.00 | ONBEKEND |
| MFFU_BUILDER | S1-Judas-0830 | 1 | 2024_2026 | 171 | 0.00 | 0.00 | 0.00 | 2.92 | 0.00 | ONBEKEND |
| MFFU_BUILDER | S1-Judas-0830 | 1 | COMBINED | 669 | 0.00 | 0.00 | 0.00 | 8.22 | 0.00 | ONBEKEND |
| MFFU_BUILDER | S1-Judas-0830 | 2 | 2019_2021 | 498 | 0.00 | 0.00 | 0.00 | 10.04 | 0.00 | ONBEKEND |
| MFFU_BUILDER | S1-Judas-0830 | 2 | 2024_2026 | 171 | 0.00 | 0.00 | 0.00 | 2.92 | 0.00 | ONBEKEND |
| MFFU_BUILDER | S1-Judas-0830 | 2 | COMBINED | 669 | 0.00 | 0.00 | 0.00 | 8.22 | 0.00 | ONBEKEND |
| MFFU_BUILDER | S2-Judas | 1 | 2019_2021 | 498 | 0.00 | 0.00 | 0.00 | 61.45 | 0.00 | ONBEKEND |
| MFFU_BUILDER | S2-Judas | 1 | 2024_2026 | 171 | 0.00 | 0.00 | 0.00 | 64.33 | 0.00 | ONBEKEND |
| MFFU_BUILDER | S2-Judas | 1 | COMBINED | 669 | 0.00 | 0.00 | 0.00 | 62.18 | 0.00 | ONBEKEND |
| MFFU_BUILDER | S2-Judas | 2 | 2019_2021 | 498 | 0.20 | 0.00 | 0.00 | 55.62 | 0.00 | ONBEKEND |
| MFFU_BUILDER | S2-Judas | 2 | 2024_2026 | 171 | 4.68 | 0.00 | 0.00 | 61.40 | 0.00 | ONBEKEND |
| MFFU_BUILDER | S2-Judas | 2 | COMBINED | 669 | 1.35 | 0.00 | 0.00 | 57.10 | 0.00 | ONBEKEND |

## Tijd tot evaluatie en funded-doorgang, gecombineerd op 252 sessies

Tijdsduur is uitsluitend gemeten bij bekende geslaagde evaluaties, geen voorspelde
wachttijd voor alle accounts. Buffer is de eerste funded-equity van $2.600, ook
voor Topstep als vergelijkingspunt; Topstep eist deze buffer niet. Een vroege payout
kan plaatsvinden zonder $2.600 te hebben bereikt. Een ontbrekende ratio betekent
dat er geen bekende evaluatiepass was. Funded-percentages hebben ALLE bekende
evaluatiepasses als noemer; unknown en onvoltooid worden niet stilzwijgend verwijderd.

| Firm | Model | MNQ | Passes | Mediane cashdagen tot pass | Gem. kalenderdagen | Gem. betalingen | Buffer/pass % | Payout1/pass % | Payout2/pass % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | 1 | 135 | 135.00 | 216.42 | 7.72 | 0.00 | 10.37 | 0.00 |
| TOPSTEP_STANDARD | S1-Judas-Bull0930 | 2 | 140 | 61.50 | 116.04 | 4.32 | 12.14 | 63.57 | 0.00 |
| TOPSTEP_STANDARD | S1-Judas-0830 | 1 | 66 | 138.50 | 258.98 | 9.14 | 0.00 | 0.00 | 0.00 |
| TOPSTEP_STANDARD | S1-Judas-0830 | 2 | 105 | 59.00 | 82.62 | 3.24 | 51.43 | 68.57 | 0.00 |
| TOPSTEP_STANDARD | S2-Judas | 1 | 0 | — | — | — | — | — | — |
| TOPSTEP_STANDARD | S2-Judas | 2 | 7 | 8.00 | 18.43 | 1.29 | 0.00 | 0.00 | 0.00 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | 1 | 135 | 135.00 | 216.42 | 7.72 | 0.00 | 0.00 | 0.00 |
| TOPSTEP_CONSISTENCY | S1-Judas-Bull0930 | 2 | 140 | 61.50 | 116.04 | 4.32 | 0.00 | 72.86 | 0.00 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | 1 | 66 | 138.50 | 258.98 | 9.14 | 0.00 | 0.00 | 0.00 |
| TOPSTEP_CONSISTENCY | S1-Judas-0830 | 2 | 105 | 59.00 | 82.62 | 3.24 | 33.33 | 86.67 | 33.33 |
| TOPSTEP_CONSISTENCY | S2-Judas | 1 | 0 | — | — | — | — | — | — |
| TOPSTEP_CONSISTENCY | S2-Judas | 2 | 7 | 8.00 | 18.43 | 1.29 | 0.00 | 0.00 | 0.00 |
| MFFU_BUILDER | S1-Judas-Bull0930 | 1 | 0 | — | — | — | — | — | — |
| MFFU_BUILDER | S1-Judas-Bull0930 | 2 | 0 | — | — | — | — | — | — |
| MFFU_BUILDER | S1-Judas-0830 | 1 | 0 | — | — | — | — | — | — |
| MFFU_BUILDER | S1-Judas-0830 | 2 | 0 | — | — | — | — | — | — |
| MFFU_BUILDER | S2-Judas | 1 | 0 | — | — | — | — | — | — |
| MFFU_BUILDER | S2-Judas | 2 | 9 | 7.00 | 17.78 | 1.00 | 0.00 | 0.00 | 0.00 |

## Kosten, payout-beleid en beperkingen

- Topstep Standard-prijs: $49 per 30 kalenderdagen zolang evaluatie loopt, $149
  activatie bij pass; geen funded-abonnement. Hoofdroute XFA Standard: vijf dagen
  minstens $150 netto; aparte Consistency-route: drie dagen en 40%. 90% winstdeling,
  50K-caps respectievelijk $2.000/$3.000, minimum $125. Na payout floor nul.
- Builder Default: $153 eenmalig, geen activatie. $2.000 EOD-floor en $1.000 DLL;
  geen eval-consistency. Funded: buffer $2.100 plus minstens $500, twee dagen en
  48 uur, 50% cycle-consistency, 80% winstdeling, maximaal $2.000 per payout.
  Na eerste payout floor $100. De aanvullende inactiviteitsregel omvat bij nieuwe
  aankopen ook de evaluatie. Geen vakantie-ontheffing of geforceerde keep-alive.
- Verzoek het maximum dat op de eerste eligible EOD mag, geen geoptimaliseerd
  uitstel. Approval/credit direct aangenomen. Opnieuw kwalificeren na iedere payout;
  bruto withdrawal volledig uit saldo, alleen aandeel trader als ontvangen cash.
- Eén gestart account, zonder betaalde resets/reactivaties. Netto per start is
  dus inclusief de initiële aankoop, maar geen automatisch retry-budget. Geen
  belastingen, wisselkoers, transferkosten, API- of automatiseringsabonnementen.
- Strategiestops worden niet veranderd. Een DLL liquideert met een causale
  1m-barrier-aanname en pauzeert de dag. Gaps vullen slechter dan de drempel. De
  OHLC-volgorde is conservatief; intrabar-extremen zijn geen tick-fillbewijs.
- Volumeselectie/prijsankers uit de eerdere kernen worden hergebruikt; geen
  stille contractwissel in een positie. Ontbrekende geplande bronminuten worden
  nooit naar nul rendement of overleving vertaald. Accountvloer vóór het eerste
  datagat kan wel een bekende breuk bewijzen.
- Inactiviteit wordt conservatief als sluiting behandeld; officiële tekst noemt
  discretionaire sluiting. NY-kalenderdagen tellen, ook weekend/feestdag. Voor
  Topstep >30 dagen; Builder zeven. Een echte fill vereist, geen kunstmatige orders.

## Gevoeligheid en alle startdatums

`summary.csv` bevat beide perioden en gecombineerd, zowel iedere start tot het eigen
era-einde als het gelijke 252-sessievenster. Daarnaast één expliciet hypothetische
Builder-variant zonder eval-inactiviteitsafsluiting; dit is geen geverifieerd koopbaar
account. Zo wordt het verschil tussen marktverlies en inactiviteit zichtbaar.
De per-start registratie met alle milestones/fees staat privé in artifacts en wordt
niet in het dashboard gepubliceerd. Geen bestaande kernen of rapporten gewijzigd.

Reproduceren: `.venv/bin/python -m scripts.prop_lifecycle register`, vervolgens
`paths`, `run`, `verify`. Eén nieuwe bronpadreconstructie; twee deterministische
accountreplays met byte-identieke uitkomsten, niet twee nieuwe signaalbacktests.

## Bronnen (geraadpleegd 26 oktober 2026)

- [topstep_pricing](https://help.topstep.com/en/articles/14289835-topstep-pricing-and-payment-questions)
- [topstep_subscription](https://help.topstep.com/en/articles/8284121-trading-combine-subscriptions)
- [topstep_XFA](https://help.topstep.com/en/articles/8284215-express-funded-account-parameters)
- [topstep_payout](https://help.topstep.com/en/articles/8284233-topstep-payout-policy)
- [topstep_floor](https://help.topstep.com/en/articles/8284204-what-is-the-maximum-loss-limit)
- [builder](https://help.myfundedfutures.com/en/articles/14290805-builder-plan-50k-a-comprehensive-guide)
- [builder_one_time](https://myfundedfutures.com/)
- [builder_inactivity](https://help.myfundedfutures.com/en/articles/16596524-inactivity-rule-one-time-payment-model)
- [builder_payout_floor](https://help.myfundedfutures.com/en/articles/13745661-payout-policy-overview-best-and-fastest-prop-firm-payouts)
- [mffu_open_loss](https://help.myfundedfutures.com/en/articles/8348565-end-of-day-eod-drawdown-explained)
