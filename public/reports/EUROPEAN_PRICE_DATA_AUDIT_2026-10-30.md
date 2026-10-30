# Europese producthistorie: controle van de prijsvelden

30 oktober 2026. Deze controle gebruikt lokaal bewaarde Yahoo Finance-dagdata en plaatst geen orders. Het gaat om kwaliteitscontrole, geen nieuwe strategie- of prestatietest. De historische Amerikaanse benchmark blijft ongewijzigd.

## Resultaat

Voor de beschikbare rijen van 1 januari 2019 tot en met 30 oktober 2026 is geteld hoe vaak afzonderlijke prijsvelden buiten de opgegeven dagrange vallen. De telling van afwijkingen gebruikt alleen rijen waarvan alle OHLCV-velden eindig zijn; ontbrekende rijen staan apart. De datumgrens garandeert geen volledige historische dekking.

| Symbool | Eindige rijen | Slot boven high | Slot onder low | Open buiten range | Ontbrekend/niet-eindig |
|---|---:|---:|---:|---:|---:|
| EQQQ.MI | 1.989 | 28 | 29 | 0 | 2 |
| QQQ3.MI | 1.990 | 26 | 11 | 0 | 1 |
| XNAS.DE | 1.468 | 0 | 0 | 0 | 2 |

Bij geen van de eindige rijen was de opgegeven high lager dan de low. XNAS.DE begint in de beschikbare data pas in januari 2021 en dekt dus 2019–2020 niet. Een ontbrekende rij betekent hier een bestaande rij met ten minste één ontbrekend of niet-eindig OHLCV-veld; deze telling stelt niet vast hoeveel handelsdagen in de bron ontbreken. Ruw afgeronde waarden kunnen kleine afwijkingen opleveren; de tabel telt ook die. De eerdere controle over het langere beschikbare venster is apart bewaard en kan daardoor andere aantallen tonen.

Een slot buiten de gepubliceerde high/low wijst op verschillende definities, gegevensproblemen of beide. De oorzaak is met deze gegevens niet vastgesteld. De slotkoers is belangrijk voor onze dagafhankelijke signalen. Daarom vervangen, corrigeren of verwijderen we de betreffende waarden niet stilzwijgend en gebruiken we deze bron nog niet als gevalideerde Europese strategiehistorie.

## Wat een tweede bron wel en niet bewijst

De [publieke productpagina van Trading 212 voor QQQ3](https://www.trading212.com/nl/trading-instruments/invest/QQQ3.IT) beschrijft de historische OHLC-waarden als gebaseerd op dagelijkse aankoopprijzen. Dat kan een andere prijssoort zijn dan een transactiekoers of de beursveiling. De pagina bewijst niet wat de officiële slotveiling was, wie de oorspronkelijke dataleverancier is, of welke prijs een order had gekregen. Een overeenkomst of verschil met Yahoo is daarom op zichzelf geen onafhankelijke validatie van de gebruikte slotkoers.

Voor vrijgave is een bron nodig met gedocumenteerde beurs, tijdstempel, prijssoort, handelsuren, corporate actions en gebruiksrechten, en een vergelijking op dezelfde notering en dagen. Voor uitvoerbaarheid blijven daarnaast actuele bied- en laatkoersen en werkelijk toepasbare kosten nodig. De [uitgevende instelling](https://www.wisdomtree.eu/en-ie/etps/equities/wisdomtree-nasdaq-100-3x-daily-leveraged) vermeldt verschillende noteringen van hetzelfde ISIN; een andere beursnotering is geen bewijs van dezelfde uitvoeringsprijs.

## Reproduceerbaarheid en scope

De lokale controlefunctie `audit_price_fields` in `scripts/audit_trading212_readiness.py` verwerkt de lokaal opgeslagen responsbestanden. Hun SHA-256 wordt gecontroleerd tegen het lokale bronregister voordat ze worden gebruikt. De gepubliceerde tabel bevat geen volledige ruwe koersreeks. Testdata worden niet vervangen en de audit geeft geen oordeel over toekomstige rendementen.

De [brokerroutes en openstaande voorwaarden](BROKER_ROUTES_AND_API_POLICY_2026-10-30.md) blijven van toepassing: de Trading 212 API-route is gepauzeerd, en de vereiste realtime data, producttoegang en totale kosten voor een alternatief zijn nog niet bevestigd.
