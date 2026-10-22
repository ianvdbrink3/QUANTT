# Publicatie van de 15:00-falsificatieronde

De gebruiker heeft na afsluiting van de lokale ronde expliciet publicatie op GitHub `main` en Vercel-productieproject `quantt` vrijgegeven.

## Ongewijzigd onderzoek

- Status: `INTERESTING_OBSERVATION_INDEPENDENTLY_UNCONFIRMED`.
- De oorspronkelijke rapporten, code-locks en berekende resultaten blijven behouden. De publieke kopie van `AFTERNOON_FALSIFICATION_REPORT.md` is byte-identiek aan de lokale momentopname. De toenmalige tekst over uitsluitend lokale opslag is historisch; deze publicatie is later vrijgegeven.
- Het erratum voor de tijdstempel-eenheden blijft zichtbaar. De gecorrigeerde controle keurt 0 van 435 dagen af. Geen rendement of p-waarde is gewijzigd.
- Geen nieuwe bronextractie, strategie-run, parameterwijziging of aanvullende hypothesetoets in deze publicatiestap.

## Publieke route

- Dashboard: `/research/nq#afternoon-falsification`.
- Publiek register: `/data/research-register.json`, afzonderlijk van private experimentledgers.
- Rapport: `/data/AFTERNOON_FALSIFICATION_REPORT.md`.
- Aggregaten: `/data/research-afternoon-falsification.json`.
- CSV-downloads: meettabellen, alle 24 toetsen, kwartaalweglatingen en statusovergangen.
- Export: `.venv/bin/python -B -m scripts.publish_afternoon_falsification`. Dit controleert de gesloten ronde en hashes en publiceert alleen de expliciete aggregaten-allowlist. Geen herberekening van signalen of rendementen.
- Publieke bestandshashes: `research/afternoon-falsification-publication.json`.

## Geslaagde releasecontroles

- Volledige Python-suite: **398 geslaagd** (394 bestaande controles plus 4 publicatiecontroles).
- `npm run typecheck`: geslaagd.
- `npm run build`: geslaagd; `/research/nq` statisch gegenereerd.
- De gegenereerde dashboard-HTML bevat de nieuwe sectie, exacte status en rapportlink.
- 115 beschermde archiefbestanden ongewijzigd; eerdere meetledgers byte-identiek gereproduceerd.
- Rapportkopie, alle publieke aggregaten en publicatiemanifest gecontroleerd op SHA-256.

## Dataminimalisatie voor productie

De release wordt uit de vastgelegde Git-commit opgebouwd met uitsluitend de webmappen `app`, `components`, `lib`, `public` en benodigde buildconfiguratie. Geen `data`, `artifacts`, `private`, lokale Python-omgeving, bron-CSV's, meetledgers of ruwe prijsarrays worden naar Vercel gestuurd. De productie-CLI gebruikt de al bestaande projectkoppeling; geen nieuw account, project of betaalde dienst wordt aangemaakt.

De Git-commit bevat wel de berekeningscode, protocollen, hashes, tests en geaggregeerde rapporten voor controleerbaarheid; private bronbestanden en ledgers blijven genegeerd. De uitkomst blijft een verkennende, onafhankelijk onbevestigde observatie, niet een gevalideerde trading edge.
