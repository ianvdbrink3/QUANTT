# Reproductie vNext, naast bevroren Baseline v0.9

Installeer de bestaande vastgezette Python-afhankelijkheden. Plaats uitsluitend
de originele 30 CSV's met ongewijzigde bestandsnamen in de genegeerde `data/raw/`.
De hashes worden gecontroleerd tegen het bestaande protocol.

`npm run verify:continuous` herbouwt de contractfeatures vanaf de ruwe bars,
controleert eerst de oorspronkelijke gecombineerde v0.9-aantallen en uitkomsten,
berekent vervolgens de drie bekende rollspreads en de point-in-time continue
indicatoren, simuleert alle vier ongewijzigde strategieën op de ruwe contractprijzen,
controleert alle fills en kosten, en reproduceert de nieuwe publieke aggregaten
inclusief de feature-matrix. De uitvoer moet exact overeenkomen met
`public/data/research-continuous.json`. Het commando publiceert niets.

Een bewuste nieuwe lokale export kan met
`.venv/bin/python -m scripts.reproduce_research.run_continuous --publish`.
Dit overschrijft alleen de afzonderlijke vNext-export en het bijbehorende
onderzoeksdocument, nooit de 0.9-bestanden. Dit is geen holdout-herregistratie.

Private uitvoer in `artifacts/continuous-vnext/`:

- `daily-indicators.csv`: per sessie de as-of ATR en PDH/PDL, huidige basis-offset
  en pas na RTH bekende diagnostische dagrange/TR-kolommen. Die laatste kolommen
  worden nooit als vooraf bekende tradefeatures gebruikt.
- `day-context.csv`: alle dagen die voor ten minste één strategie eligible zijn,
  met afzonderlijke beschikbaarheidstijden voor 09:30- en 09:45-velden.
- `trade-context.csv`: alle trades, met vóór entry nog onbekende velden leeg.
- `trades.csv`, `eligibility.csv`, `summary.json`, `REPORT.md`.

De openings-RVOL gebruikt een 14-sessie gemiddelde van de actieve contractstroom;
de oorspronkelijke signaalfilter gebruikt nog steeds zijn contracteigen,
same-clock 20-observatie mediaan met minimum 10. Dit zijn bewust twee
verschillende maten. De nieuwe contextfeatures veranderen geen handelsregel.

Geen tick-aantallen in de bron: Relative Ticks en volume/ticks zijn leeg met een
expliciete bronbeperkingsstatus. De NQ-prijsstap van 0,25 punt is geen telling van
transacties en wordt hiervoor niet gebruikt.

Alle featurecontrasten zijn beschrijvend. De globale Holm-familie omvat 40 tests,
inclusief kleine/constante groepen met p=1. Vijf-sessie block-bootstrap houdt
niet-trade- en ontbrekende featuredagen in de tijdas. Geen datagedreven grens,
filteroptimalisatie, strategiepromotie of causale claim. Intrabar MFE blijft een
minuutbar-bovengrens, geen exacte gemeten excursie tot het fill-moment.
