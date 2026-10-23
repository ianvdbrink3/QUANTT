# Maandwissel-audit: eerdere onzekerheid en verschillen in steekproef

Dit document verduidelijkt de nieuwe audit zonder bestaande rapporten of berekeningsregels te veranderen.

## Verschillende intervallen zijn geen nieuwe onafhankelijke waarnemingen

Voor dezelfde 81 oorspronkelijke maandwisseltrades en +4.364,025 netto punten bestaan meerdere verkennende onzekerheidsberekeningen:

| Berekening | Nominaal 95%-interval gemiddeld netto NQ-punten |
|---|---|
| Eerdere maandcluster-bootstrap, 21 maanden | [−0,113; +111,695] |
| Marathon, vijfdaagse moving-blockbootstrap | [+1,818; +105,682] |
| Nieuwe audit, tweemaands moving-blockbootstrap | [+3,912; +104,423] |

Deze uitkomsten tonen gevoeligheid voor bootstrapopzet, clustering, randmaanden en toeval van eindige herhalingen. Het nieuwe interval mag niet als vervanging van het minder gunstige eerdere interval worden gebruikt. De auditmethode is vóór deze nieuwe berekening vastgelegd, maar de kandidaat en zijn resultaten waren al bekend. Dit blijft dus geselecteerd, verkennend onderzoek.

De nieuwe audit omvat 22 kalendermaanden, omdat ook de twee complete RTH-sessies van december 2024 in de dagelijkse long-benchmark staan. Conform de bestaande onvolledige-maandregel zijn dit geen ToM-trades. De eerdere ronde vergeleek 81 ToM-dagen met 352 andere dagen in 2025–2026. De nieuwe audit gebruikt het volledige vaste cohort van 435 complete RTH-dagen: 81 ToM tegenover 354 andere dagen. De maandwisseltrades zelf zijn exact gelijk gebleven.

Het eerdere gematchte benchmarkcontrast en het nieuwe ongewogen complementcontrast hebben bovendien verschillende doelgrootheden. De cijfers moeten niet worden gepresenteerd alsof dit herhalingen van één identieke toets op nieuwe data zijn.

## Wat de nieuwe contrasten feitelijk zeggen

In de ontdekkingsperiode bedraagt het ruwe verschil ToM minus andere dagen +63,740 netto punten per blootgestelde dag, met nominaal interval [+12,050; +116,357]. De benaderende ruwe bootstrap-p is 0,01590 en Holm4-p is 0,06359. De ATR-genormaliseerde vergelijking blijft positief, maar haar interval omvat nul en Holm4-p is 0,24928.

In de oudere, onbevestigde bron bedraagt het ruwe verschil +13,095 punten, met interval [−23,104; +43,064] en Holm4-p 0,66813. Ook de ATR-genormaliseerde vergelijking is daar onzeker.

Daaruit volgt niet dat de kalenderpremie nul is. Daaruit volgt evenmin dat zij bewezen positief of uitvoerbaar is. Het formele auditlabel blijft `INSUFFICIENT_EVIDENCE_NO_PROMOTION`.

## Risicovergelijking

De gemiddelde vooraf bekende ATR op ToM-dagen is in beide bronnen iets lager dan op andere dagen. De resultaten rechtvaardigen daarom niet de verklaring dat ToM uitsluitend méér verdient omdat die dagen gemiddeld een hogere ATR hebben. De positieve maar onzekere ATR-genormaliseerde verschillen ondersteunen ook geen stellige regime- of oorzakelijke verklaring.

De gesloten-trade-drawdown onderschat wat tijdens open posities zichtbaar is. Op de ontdekkingsdata is die drawdown 1.307,075 punten; op minuutclose-marks is zij 1.512,825 punten. De mediane MAE per ToM-trade is 102,25 punten en de P95 is 497 punten. Voor één NQ zijn dat respectievelijk circa $30.257 drawdown, $2.045 mediane adverse excursion en $9.940 P95 adverse excursion, zonder garantie dat tick-drawdown niet groter was. Er is geen rekeninggrootte of acceptabele risicogrens afgesproken.

## Bronnen binnen de repository

- `research/new-candidates-round01-results.json`: eerdere `TURN_OF_MONTH_RTH`-uitkomst en maandclusterinterval.
- `artifacts/edge-marathon/discovery.json`: ongewijzigde marathonuitkomst `TOM_RTH`.
- `research/month-turn-audit-results.json`: nieuwe benchmark-, normalisatie- en risicocontrasten.

Geen bestaand resultaat is overschreven en geen ongunstige methode, bron of datum is op basis van deze vergelijking verwijderd.
