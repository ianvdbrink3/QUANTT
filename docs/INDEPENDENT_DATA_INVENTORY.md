# Inventaris onafhankelijke data — 22 oktober 2026

## Besluit

**Geen gratis, volledige, contractgeïdentificeerde en onafhankelijk vrijgegeven NQ-dataset is in deze inventaris bewezen beschikbaar.** Dit is geen uitspraak dat nergens gratis data bestaat. Er is geen nieuwe toets gestart, geen account geopend, geen API-query met kosten uitgevoerd en niets gedownload of gekocht.

170 bestanden geïnspecteerd; 101 unieke byte-inhouden; 0 inventarisfouten. Alleen headers, timestamps, aantallen en SHA-256; geen numerieke OHLCV-analyse van nieuwe/onbevestigde data. Volledig lokaal paden-/hashregister: genegeerd `artifacts/independent-data-inventory.json`.

De inventaris betreft CSV-bestanden met NQ in de naam in Downloads en expliciete lokale projectdatamappen. Geen volledige schijfdoorzoeking of archiefextractie. Datums zijn bronlabels, geen vastgestelde NY-sessies; rijen zijn geen unieke bruikbare minuten of eligible dagen.

## Lokale routes

| Bron | Feitelijke toestand | Beoordeling voor v2 |
|---|---|---|
| Geregistreerde Barchart NQH25 t/m NQZ26 | De bronhashes van de verbruikte 2024-12-30 t/m 2026-09-30 reeks zijn bekend; exports kunnen randen buiten dit venster bevatten | Geen nieuwe holdout door bestanden te hernoemen, opnieuw te downloaden of van leverancier te wisselen |
| Dataset_NQ_1min_2022_2025.csv | Oudere datums aanwezig; bronlabel ET; geen contractkolom of bewezen rollschema | Niet testklaar. Eerder in project bekeken; exacte eerdere uitkomsten/toegang niet volledig aantoonbaar. Een paar ongeziene rijen zijn geen gecertificeerde onafhankelijke dataset |
| archive/NQ_in_* | Diverse timeframes, continue symboolreeks; hoofdzakelijk reeds verbruikte periode | Niet uitwisselbaar met afzonderlijke NQ-contracten; hogere timeframes niet terug te bouwen tot de benodigde minuten |
| frd_sample_futures_NQ | Twee weken recente samples, inclusief 1m; lokale documentatie beschrijft Eastern en startlabels | Mogelijke kleine technische bronvergelijking, geen meerjarige gratis validatiereeks. Warmup/contractbasis en eerder gebruik onbevestigd; niet stilzwijgend als forward aanmerken |
| NQM17-bestanden | 0, 0 parsebare timestamps | Bestandsnaam 2017 bewijst geen historische data; lege exports niet gebruiken |

### Alle unieke bestanden met bronlabels buiten de verbruikte periode

| Bestand | Timestamp-rijen | Eerste label | Laatste label | Rijen vóór 2024-12-30 | Rijen na 2026-09-30 |
|---|---:|---|---|---:|---:|
| Dataset_NQ_1min_2022_2025.csv | 1048575 | 2022-12-26T18:01:00 | 2025-12-11T20:52:00 | 711173 | 0 |
| NQ_1day_sample.csv | 12 | 2026-10-01T00:00:00 | 2026-10-16T00:00:00 | 0 | 12 |
| NQ_1hour_sample.csv | 270 | 2026-10-01T00:00:00 | 2026-10-16T16:00:00 | 0 | 270 |
| NQ_1min_sample.csv | 16200 | 2026-10-01T00:00:00 | 2026-10-16T16:59:00 | 0 | 16200 |
| NQ_30min_sample.csv | 540 | 2026-10-01T00:00:00 | 2026-10-16T16:30:00 | 0 | 540 |
| NQ_5min_sample.csv | 3240 | 2026-10-01T00:00:00 | 2026-10-16T16:55:00 | 0 | 3240 |
| NQ_in_1_hour.csv | 10504 | 2024-01-01T23:00:00 | 2025-10-10T15:00:00 | 5875 | 0 |
| NQ_in_2_hour.csv | 5479 | 2024-01-01T23:00:00 | 2025-10-10T14:00:00 | 3065 | 0 |
| NQ_in_3_hour.csv | 5712 | 2023-01-02T23:00:00 | 2025-10-10T13:00:00 | 4100 | 0 |
| NQ_in_4_hour.csv | 5817 | 2022-01-02T23:00:00 | 2025-10-10T14:00:00 | 4610 | 0 |
| NQ_in_daily.csv | 6648 | 1999-06-29T22:00:00 | 2025-10-09T22:00:00 | 6452 | 0 |
| NQ_in_monthly.csv | 317 | 1999-05-31T22:00:00 | 2025-09-30T22:00:00 | 307 | 0 |
| NQ_in_weekly.csv | 1372 | 1999-06-27T22:00:00 | 2025-10-05T22:00:00 | 1332 | 0 |
| NQ_point_in_time_1min.csv | 106678 | 2024-12-29T23:00:00+00:00 | 2025-04-17T20:59:00+00:00 | 60 | 0 |
| nqh25_intraday-1min_historical-data-10-19-2026.csv | 11969 | 2024-12-29T17:00:00 | 2025-01-10T15:59:00 | 420 | 0 |

De volledige regel kan tegelijk een groot verbruikt middenstuk bevatten. Buitenvenster-rijen zijn uitsluitend metadata-geïnventariseerd, niet gescoord. Een avondprefix vóór een nieuwe NY-handelsdag is geen extra onafhankelijke volledige sessie.

## Rechten, herkomst en besmettingsrisico

- De lokale Kaggle-metadata noemt CC0-1.0; dat is de claim van de uploader, geen onafhankelijk bewijs van beurs-/vendorrechten, bronauthenticiteit of complete contractidentiteit. Niet publiek herdistribueren op basis van die claim alleen.
- Het FirstRate-readme beschrijft startlabels en Eastern tijd. Dat is leveranciersdocumentatie voor die bron, geen bewijs voor Barchart-labels of uitvoerbare tickfills. De [FirstRate-licentie](https://firstratedata.com/about/license) staat afgeleide rapporten toe maar niet ruwe herdistributie; toepasselijkheid op een concrete sample blijft te controleren.
- Oudere historie kan historische replicatie zijn, niet prospectief bewijs. De oude generieke datasets waren eerder in het project aanwezig en besproken. Alleen filenamen/logs kunnen absolute niet-inzage niet bewijzen. Alle 435 ontdekkingsdagen blijven verbruikt, ook op een andere vendor.
- Het bestaande lokale rapport `reports/NQ-data-audit-2026-10-19.md` documenteert dat de grote CSV al volledig op prijsstructuur/VWAP/hiaten is geaudit: vermoeden van additive back-adjustment, onbevestigde contractketen, close-labels en mogelijke Excel-afkapping bij 1.048.575 datarijen. De H25/Z25-audits raadpleegden ook haar timestamps. Dit is aangetoond eerder gebruik, niet automatisch bewijs dat de specifieke 15:00-uitkomsten vóór 2024-12-30 zijn getest. De contamination-audit blijft daarom open, niet stilzwijgend schoon of definitief uitgesloten.
- Een onafgebroken forwardreeks moet pas na een vooraf vastgelegde startdatum en vrijgave beginnen. Reeds aanwezige oktober-2026-samples zijn niet automatisch forward sinds een registratie van 22 oktober.

## Externe gratis routes: actuele publieke bronnen gecontroleerd

| Route | Wat de primaire bron ondersteunt | Wat niet is vastgesteld | Besluit bij budget €0 |
|---|---|---|---|
| Barchart bestaande toegang | [Lidmaatschapsvergelijking](https://www.barchart.com/membership-comparison) onderscheidt gratis algemene downloads van hogere lidmaatschappen; [historische downloadpagina](https://www.barchart.com/stocks/quotes/-TOOL/historical-download) beschrijft intraday-downloads en een 20.000-recordlimiet | Historische NQ-minuutexports zijn niet bewezen inbegrepen bij gratis toegang. Publieke directe pagina geeft verificatie; geen bestaande Barchart-tab in ingeschakelde browser. Actueel abonnement/resterende rechten niet uitgelezen | Alleen een rechtmatig bestaande exportmogelijkheid benutten als zonder betaling bevestigd. Geen nieuw proefabonnement of verlenging |
| FirstRate samples | [FAQ](https://firstratedata.com/about/FAQ) biedt twee weken recente samples en geen andere sampleperioden | Geen kosteloze meerjarige NQ-contracthistorie of onbeperkte dagelijkse collectie bewezen | Alleen kans voor beperkte broncontrole; geen hoofdroute voor power |
| algoseek Sandbox | [Publieke sandboxpagina](https://algoseek.com/sandbox/) noemt maximaal één jaar data en geen creditcard | Geen bevestigde NQ-exportrechten, gekozen perioden of volledigheid in het bestaande account; gebruiker liep eerder tegen Contact Us aan | Geen hernieuwde belofte van gratis NQ. Niet testklaar |
| Databento introductietegoed | [Officiële credits-FAQ](https://databento.com/docs/faqs/usage-pricing-and-data-credits) noemt $125 voor nieuwe gebruikers, zes maanden geldig, één keer per team en geen maandabonnement voor historische usage-based data | Geen onbeperkte gratis bron; geen bevestigde accountgeschiktheid, queryprijs, resterend tegoed of afwezigheid betaalverplichtingen. De [billingdocumentatie](https://databento.com/docs/portal/billing) noemt onbeperkt gebruik als standaard zonder maandlimiet; een limiet is niet automatisch een bewezen harde €0-grens per aanvraag | Mogelijke eenmalige kosteloze historische route als tegoed, quote, licentie en blokkade op eigen betalingen vooraf aantoonbaar zijn. Nu geen account, toggle, API-query of download uitgevoerd |
| CME settlementpagina’s | [CME](https://www.cmegroup.com/trading/about-settlements.html) beschrijft dagelijkse settlementstatistieken als referentie | Geen individuele 15:00/15:01/15:14-transacties; settlement is geen minutebar | Ongeschikt voor certificatie van het twee-minuteneffect of fills |

De Barchart-publieke zoekindex en de rechtstreeks geopende verificatiepagina leveren niet hetzelfde bewijs als een actuele accountcontrole. Gratis tabeldownloads zijn niet hetzelfde als gratis historische minuutexports. Geen Cloudflare-omzeiling of loginpoging gedaan.

## Werkbelasting en volgende beslissing

Een technisch proefpakket via al bestaande toegestane exports: twee vooraf gekozen, volledige 2-weekse contractblokken bij gewone weken en een aparte DST-/rollovercontrole. Niet nu downloaden en geen uitkomsten inspecteren. Volledige sessies en ATR14-opwarmhistorie zijn nodig; alleen het kwartier ophalen volstaat niet voor selectie.

Bij 20.000 records/request is twee kalenderweken van ongeveer tien volledige futuresessies (~13.800 1m-bars) doorgaans een passend blok, geen garantie bij specifieke grenzen. Voor een geheel jaar is circa 26 basisblokken nodig, plus contractoverlap, herstel van gaten en opwarming. Bij één hypothetisch toegestane export/dag dus minstens circa 26 handmatige downloadmomenten/jaar, niet een bewezen gratis recht of vaste kalenderplanning. Dit is een werkraming, geen bestellijst.

**Eindoordeel: formele onafhankelijke toets voorlopig NIET VRIJGEVEN.** Geen geverifieerde gratis onafhankelijke hoofdbron. Eerst actuele bestaande Barchart-exportrechten zonder nieuwe kosten vaststellen, of wachten op aantoonbaar bruikbare kosteloze contractdata. De huidige samples kunnen een beperkte technische vergelijking helpen, maar lossen het steekproefprobleem niet op. Geen collector, nieuwe strategie of eindtoets gebouwd.
