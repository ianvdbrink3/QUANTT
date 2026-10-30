# QUANT lokale agent — huidige aansluitgids

Bijgewerkt op 30 oktober 2026. De echte Trading 212 Invest-demo is lokaal gekoppeld en alleen-lezen geverifieerd. De sleutels zijn opgeslagen; je hoeft ze niet opnieuw in te voeren. Er zijn nul orders geplaatst. Echte handel blijft technisch uitgesloten.

De huidige complete productcontrole, bewijsstukken en resterende afhankelijkheden staan in [Trading 212: startcontrole en demo-protocol](TRADING212_DEMO_READINESS_2026-10-30.md). De openbare website toont een gedateerde publicatiestand; de actuele lokale heartbeat en privé-administratie blijven op de Mac.

## Wat nu draait

De macOS-adviesdienst controleert iedere minuut de nieuwe afgeronde QQQ/TQQQ-dagdata, de vaste signaalkernel en de demo-administratie. De onafhankelijke Nasdaq-slotprijscontrole probeert een ontbrekende datum iedere 15 minuten opnieuw. Weekenden, US-feestdagen, vroege sluitingen en tijdzones worden verwerkt. S1 blijft uit. Er is geen betaalde LLM-aanroep nodig voor deze controle.

De Mac moet ingeschakeld en wakker zijn. De dienst start bij login en herstart na een crash. Er zijn geen slaap- of beveiligingsinstellingen veranderd. Het dagboek en de bronbestanden blijven bewaard bij stoppen of herstarten.

De configuratie staat op **ADVICE_ONLY**, met demo_orders_enabled=false. Bovendien weigert de werkelijk gebruikte REST-client POST en DELETE. De brede rechten van de demosleutel veranderen die softwareblokkade niet.

## Status bekijken

De lokale controlekamer staat op `/portfolio-os` van de ontwikkelserver. Onder ‘De agent op je Mac’ zie je de actuele controle, bronstand, orderaantallen en alle startpoorten. Het openbare QUANT-dashboard geeft dezelfde soort bouwstatus zonder een live verbinding naar je Mac of broker.

Vanuit de projectmap:

```
.venv/bin/python -m portfolio_agent.forward status
.venv/bin/python -m portfolio_agent.forward preflight
```

De startcontrole kan ook buiten het vijfminutenordervenster aangeven waarom uitvoering nog niet mag. Een succesvolle API-verbinding is geen vrijgave.

## Starten en stoppen

```
.venv/bin/python -m portfolio_agent.forward service-install
.venv/bin/python -m portfolio_agent.forward service-stop
```

De dubbelklikbestanden `tools/start-portfolio-advice.command` en `tools/stop-portfolio-advice.command` doen hetzelfde. Als een `.command`-bestand door jouw bestandskoppeling als tekst opent, voer je het expliciet met `/bin/zsh` uit in je eigen Terminal.

`tools/connect-trading212-demo.command` vraagt de API Key en daarna de API Secret verborgen op. Dit is alleen nodig wanneer je de sleutels zelf vervangt. Sleutels worden niet via chat, browserformulier op Vercel, broncode of dashboard ingevoerd. Het lokale bestand heeft rechten 0600 en staat buiten Git/Vercel. Je hebt deze stap al afgerond.

## Wat nog geen vrijgave heeft

- De actuele slotdatum moet onafhankelijk zijn bevestigd; een eerder bevestigde datum telt niet als de nieuwe datum.
- De exacte brokerproducten, fractierechten, minimale orderwaarde, prijstik en productdata moeten zijn vrijgegeven. De gecontroleerde EUR-catalogus bevat EQQQm_EQ, XNASd_EQ en QQQ3m_EQ. Catalogusvermelding is geen bewijs van uitvoerbaarheid. QQQ3 is een schuld-ETP en geen TQQQ.
- Er is nog geen geverifieerde verse bid/ask-provider gekoppeld. Het openbare Milanese boek is 15 minuten vertraagd; dat voldoet niet aan maximaal twee seconden.
- Pas na deze technische controles volgt een expliciete lokale demo-orderstart. Er is geen LIVE-modus en de website heeft geen orderknoppen.

De huidige proefstand blijft **0/20 echte volledige demo-sessies**. Historische replays, geïnjecteerde testclients en losse sluitingspolls tellen niet. De policyhash omvat zowel de configuratie als de uitvoeringscode. Het gedetailleerde protocol en het theoretische startrooster staan in het actuele rapport.

## Storingen en herstel

Een onzekere aanvraag wordt nooit blind opnieuw verstuurd. Een broker-ACK telt pas als fill na de werkelijke historische uitvoeringsgegevens. Een annulerings-ACK kan nog een late fill krijgen. Cashhistorie wordt met een blijvende cursor opgehaald en met posities, orders en nieuwe cashmutaties vergeleken. Onbekende referenties, incomplete historie en verschillen worden niet als nul gelezen.

Verwijder nooit de database om een blokkade op te heffen. Een onbekende aanvraag zonder broker-ID vereist menselijke controle in de demo; er wordt niet automatisch op een ‘waarschijnlijke order’ gematcht. De bestaande risicolimieten blijven gelden, maar garanderen bij bijvoorbeeld gaps of uitval geen maximale verliesgrens.

Alle privébestanden staan onder `artifacts/portfolio_agent/forward/`. De afzonderlijke brondata, rekeninggegevens, orderpayloads en sleutels worden niet naar GitHub of Vercel gestuurd. Alleen code, tests, veilige samenvattingen en documentatie worden gepubliceerd.
