# Portfolio OS — publicatie

Het openbare dashboard op `/portfolio-os` gebruikt alleen gesaneerde historische onderzoekssamenvattingen. De homepage verwijst naar dit dashboard. Bestaande onderzoeksroutes en bevroren resultaten blijven intact.

De vier exports onder `public/data/portfolio-os/` bevatten per replay 60 dagsamenvattingen, de Unit-NAV-curve, geaggregeerde sleeve-balansen en alleen ordermetadata. Marktprijzen dragen hun historische peildatum. Er is geen livefeed of brokerverbinding.

Private bron-CSV's, de SQLite-database, event-/fill-ledgers, accountnamen, orderaantallen en limietprijzen blijven buiten deze publicatie. De Nederlandstalige publieke dagbrief is een gemarkeerde samenvatting; het oorspronkelijke volledige verslag blijft lokaal. Intent- en policyhashes blijven inspecteerbaar.

De lokale ontwikkelomgeving behoudt de lokale read-only API. De productiebuild gebruikt uitsluitend statische JSON-exports; Python of een verbinding met de Mac is niet nodig. Alle uitvoeringspoorten blijven vergrendeld.

De kostencalculator werkt in de browser met dezelfde conditionele formules. Verificatie: 98 scenario's over vier brokers en beide kostenpoorten kwamen overeen met de lokale Decimal-engine. Dit blijft een kostenmodel, geen bevestiging van brokerrechten of actuele tarieven. Tijdklokken gebruiken de huidige US/EU-DST-regels, onafhankelijk van de datum van de export.

## Controles

- `npm run typecheck`
- `npm run build`
- `node --test tests/portfolio-public.test.mjs`: acht tests voor hashes, privacy, dekking, kosten, DST, previews en filters.
- De bestaande lokale onderzoeks- en engine-suite is apart gedraaid: 1.740 tests groen; vier bestaande NumPy-waarschuwingen.
- De openbare productiebuild is vóór publicatie in de browser getest, inclusief budgetwijziging, profielpreview, filters en ordermetadata.

## Exports vernieuwen

Vanuit een lokale checkout met de private engine en datasets:

```
python3 scripts/export_portfolio_public.py --source-root /pad/naar/lokale/onderzoekscheckout
node --test tests/portfolio-public.test.mjs
```

Review alleen de allowlisted exports en commit die expliciet. De manifestatie bevat de SHA-256-hash van elk JSON-bestand. Publiceer nooit de lokale datamap of database. De export start geen backtest, signaalberekening of brokeractie.
