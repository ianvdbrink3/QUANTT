# Twee nieuwe verkennende NQ-kandidaten

Uitsluitend bestaande ontdekkingsdata: 30 december 2024–30 september 2026, 435 complete RTH-dagen. Geen onafhankelijke validatie. De historische 2019–2021-steekproef is niet door deze runner gelezen. Geen nieuwe filters, stops, targets of zoeklus. Beide regels en vergelijkingen waren vóór de eerste berekening gehasht.

| Kandidaat | Trades | Netto punten | Netto USD | Winrate | PF | Max gesloten DD pt | Gem. netto pt | Verschil benchmark pt | Nominaal 95%-interval verschil |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| MORNING_TO_CLOSE | 417 | -71.32 | -1426.50 | 48.7% | 0.992 | 2064.55 | -0.17 | -0.75 | [-12.87; 10.53] |
| TURN_OF_MONTH_RTH | 81 | 4364.02 | 87280.50 | 64.2% | 1.706 | 1307.07 | 53.88 | 61.29 | [1.51; 129.71] |

## Vastgelegde regels en vergelijking

- Ochtend-naar-slot: teken van vorige complete RTH-close (causaal omgerekend naar huidig contract) tot 09:59 close. Entry 15:30 open, exit 15:59 close. Vergelijking: altijd long op dezelfde dagen in hetzelfde slot-halfuur. Geen 15:00-hypothese en geen ORB-hergebruik.
- Maandwisseling: laatste plus eerste drie cash-beursdagen, alleen RTH long. Kalenderposities gebruiken ook korte beursdagen; trades uitsluitend op bestaande volledige kwaliteitsdagen. Benchmark: andere volledige dagen in dezelfde maand, gewogen naar aantal maandwissel-events. December 2024 is vooraf uitgesloten als onvolledige kalendermaand.
- Oorspronkelijke literatuur betreft aandelen/ETF’s, niet NQ. Ochtendrichting omvat overnight; maandwisseling hier juist alleen RTH. De laatste is expliciet een aanpassing, niet een exacte replicatie.
- Eén NQ, 1,225 pt ($24,50) per ronde; gevoeligheid +1/+2 extra ticks per kant staat in JSON. Open/close zijn barprijsproxies, geen bewezen uitvoerbare fills. Geen intrabar stopvolgorde. Margin- en intratrade-drawdownrisico zijn niet met gesloten-equity DD afgedekt.

## Onzekerheid en volledige resultaten

De JSON bevat alle maanden/kwartalen, long/short, MFE/MAE-percentielen, verliesdagen en winstconcentratie. Intervallen zijn nominale maandblok-bootstrapintervallen, geen multipliciteitsgecorrigeerd bewijs. Er zijn twee model- en twee benchmarkclaims mogelijk; geen confirmatoire p-waarde of promotie toegekend. Een positieve puntschatting is geen winstgevend gevalideerd model.

Identieke herberekening vanuit dezelfde geladen staat is gecontroleerd. Dit is géén onafhankelijke bronherlaad-reproductie; die status wordt apart geregistreerd. Private tradeledgers blijven Gitignored onder artifacts. Geen GitHub-push of publicatie uitgevoerd.

## Bronnen

- https://smallake.kr/wp-content/uploads/2015/01/SSRN-id2440866.pdf
- https://doi.org/10.2469/faj.v64.n2.11
- https://ir.theice.com/press/news-details/2023/NYSE-Group-Announces-2024-2025-and-2026-Holiday-and-Early-Closings-Calendar/default.aspx
- https://ir.theice.com/press/news-details/2024/The-New-York-Stock-Exchange-Will-Close-Markets-on-January-9-to-Honor-the-Passing-of-Former-President-Jimmy-Carter-on-National-Day-of-Mourning/default.aspx
