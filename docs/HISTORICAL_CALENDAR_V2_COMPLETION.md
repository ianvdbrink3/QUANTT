# Afronding kalenderronde — 23 oktober 2026

De afzonderlijke kalender-v2 is geïmplementeerd, tweemaal vanaf de ruwe bronnen gereproduceerd en lokaal zichtbaar gemaakt. Dit is een afgeronde voorbereidingsronde met expliciete resterende bewijsbeperkingen, geen definitieve broncertificering of vrijgave van strategie-uitkomsten.

## Verificatie

- Volledige suite: **702 geslaagd, 0 mislukt, 0 overgeslagen** (62,93 seconden). Vooraf: 633; toegevoegd: 69 kalender-/causaliteits-/bronbehoudtests.
- Typecontrole en productiebuild slagen. De lokale nieuwe pagina, het controle-JSON en de rapportlink antwoorden HTTP 200.
- Dashboard ook in de browser visueel gecontroleerd. Privé-screenshot: `artifacts/historical-calendar-v2/dashboard-preview.png`.
- Twee volledige bronherberekeningen: alle 8 uitvoerbestanden byte-identiek.
- 43 echte toekomst-afknipcontroles; alle 13 vaste rollover-openingen inbegrepen, naast contextwijzigingen, DST en haltdagen.
- Alle 105 ruwe CSV's opnieuw geparseerd; bronhashes van originelen en privé-kopieën gecontroleerd. Exact dezelfde ontdubbelde contractbars en actieve prijzen.
- Alle 585 vooraf bestaande bestanden, inclusief eerder ongetrackte auditbestanden, en 13 private audit-/voorbereidingsbestanden byte-identiek.

## Feitelijke impact

| Technisch contexttype | Heel 2019–2021 vóór → na | Resterende toets vanaf 14 januari 2019 vóór → na |
|---|---:|---:|
| ATR-ready (maandwisseling) | 741 → 741 | 733 → 733 |
| Compressie: ATR + vorige RTH | 714 → 713 | 706 → 705 |
| Sweep: ATR + volledige nacht | 627 → 627 | 619 → 619 |

Geen van deze aantallen telt signalen of trades. De 757 cashsessies omvatten zes halve dagen; 741 hebben een volledig bruikbaar RTH-grid plus 09:29-boundary. De resterende periode heeft respectievelijk 749 cashsessies en 733 schone volledige dagen. Acht eerder bekeken januaridagen blijven apart.

Alleen 2 april 2021 is gecorrigeerd naar een futuresessie tot 09:15 NY. Dit verandert PD-context op 5 april en ATR-context op 14 daaropvolgende evaluatiedagen. Geen andere kalender-, rollover- of kandidaatregel is aangepast.

## Bewijsstatus en beperking

38 kalenderuitzonderingen beoordeeld: drie daggrenzen met directe CME-XLS-cellen, één eerder beoordeeld primair CME-bericht, 25 met gedateerde CME-gelabelde bewaarde tabellen en negen met bijgesneden kopieën. Bewaarde afbeeldingen zijn niet onafhankelijk op CME-authenticiteit gecertificeerd. De negen bijgesneden gevallen blijven voorlopig; zij staan afzonderlijk met hashes en bronnen in het register.

De Barchart-vraag over volumedefinities en ontbrekende minuten blijft open. Geen inbox gelezen en geen ontvangen antwoord geclaimd. De afwijkende rangorde van minuut- versus dagvolume wordt niet achteraf weggecorrigeerd. Exacte NQ-haltseconden, licentie-/redistributierechten en tick-level fillbewijs zijn niet door deze kalenderronde bewezen.

## Bestanden en gebruik

- Volledige analyse: `docs/HISTORICAL_CALENDAR_V2.md`.
- Bronnen/aflezingen/hashes: `research/historical-calendar-v2-sources.json`.
- Uitzonderingen: `research/historical-calendar-v2-exceptions.csv`.
- Freeze: `research/historical-calendar-v2-lock.json`.
- Dubbele reproductie: `research/historical-calendar-v2-verification.json`.
- Test-/build-/UI-bewijs en uitvoerhashes: `research/historical-calendar-v2-completion.json`.
- Lokale dashboardroute: `/research/historical-calendar-v2`.

Reproductie met de bestaande onderzoeksomgeving: `python -m scripts.historical_calendar_v2 verify` of `replay`. De aparte collector downloadt uitsluitend daadwerkelijk ontdekte openbare bronlinks; download is nooit automatische bewijsgoedkeuring.

Geen strategieën, signalen, forward returns, trades of P&L op het nieuwe venster berekend. Geen commit, push of Vercel-uitrol uitgevoerd. De lokale previewserver voor de controle wordt na de inspectie gestopt; de eerder bestaande server en productie zijn niet aangepast. Ruwe bronnen, bronafbeeldingen en numerieke context blijven buiten Git. Publicatie en uitkomstvrijgave vergen een afzonderlijke beslissing.
