"""Local audit report from fixed outputs; no scoring or publication."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run():
    r = json.loads((ROOT/'research/afternoon-gonogo-audit-results.json').read_text())
    access = json.loads((ROOT/'research/afternoon-gonogo-access.json').read_text())
    lines = ['# 15:00-kandidaat: gecombineerde go/no-go-audit', '', '22 oktober 2026. V2 blijft bevroren. Geen nieuwe backtest, selectie, parameteroptimalisatie of echte order.', '',
        '## Besluit', '',
        '| Onderdeel | Oordeel | Betekenis |', '|---|---|---|',
        '| Implementatie van de bevroren statistiek | PASS_NUMERICAL_RECONCILIATION | Matrixberekening, oude scalaire HAC en vectorcode geven dezelfde SE tot 1e-12. Dit is een afzonderlijke formulering door dezelfde assistent, geen externe reviewer. |',
        '| Algemene nulkalibratie van HAC(5)/t + Holm2 | NOT_CLEARED_FOR_CONFIRMATORY_RELEASE | Niet robuust 5% onder alle vooraf vastgelegde nulscenario’s. Geen bandbreedte/toets geselecteerd of v2 aangepast. |',
        '| Kosteloze historische toegang op dit moment | EXISTING_TRIAL_ENTITLEMENT_CONFIRMED | Bestaande Safari-account heeft Premier-proeftoegang en het 1m-exportformulier is bereikbaar. Geen onbeperkte gratis dienst; exacte exports/quotum nog niet getest. |',
        '| Uitvoering rond 15:00 | UNVERIFIED_NO_QUOTE_OR_FILL_EVIDENCE | De $24,50-aanname is aanwezig, niet empirisch gecertificeerd. Geen real-time BBO/fills beschikbaar in geregistreerde bronnen. |',
        '| Nieuwe onafhankelijke toets of live-model | NO_GO | Data-intake en aanvullende meetlatbeoordeling mogen worden voorbereid; dit is geen vrijgave voor rendementstoets, live orders of een quote-pilot. |', '',
        '## 1. Afzonderlijke numerieke controle', '',
        'Voor de vaste 162 reeds verbruikte cohortdagen worden uitsluitend de gecentreerde residuen uit de vorige haalbaarheidsanalyse gebruikt. Het ontdekkingsgemiddelde wordt niet getoetst. Geen nieuwe data-uitkomsten gelezen.',
        'De tweede formulering construeert expliciet de kalenderkernel K(i,j)=max(0,1-|i-j|/6) en berekent SᵀKS × n/(n−1). De nul op niet-geselecteerde dagen geldt alleen voor invloedsscores, niet als een verzonnen nulrendement in de event-steekproef.',
        f"Gelijke standaardfouten in punten: 2m={r['implementation_check']['se_points'][0]:.12f}; 15m={r['implementation_check']['se_points'][1]:.12f}. Verschil matrix/scalair/vector <1e-12. Geen aanwijzing voor een implementatiefout in deze specifieke SE-/Holm-berekeningen; dit certificeert niet de hele engine of de inferentie.", '',
        '## 2. Nulkalibratie en oorzaakdiagnose', '',
        'Per cel 10.000 synthetische panels, seed vooraf vastgelegd. Drie vaste kalenderlengten (125/250/500), beide horizons gepaard. De bevroren HAC(5), event-dagencorrectie, t-vrijheidsgraden en Holm2 blijven exact gelijk. Geen model gekozen op de gunstigste p-waarde.', '',
        '| Nulmodel | Geplande sessies | Gem. geselecteerd | Holm enige richting % | Positief familiesucces % | Negatief familiesucces % |', '|---|---:|---:|---:|---:|---:|']
    for x in r['null_models']:
        lines.append(f"| {x['model']} | {x['scheduled_sessions']} | {x['mean_selected']:.1f} | {100*x['any_sign_FWER']['rate']:.2f} | {100*x['positive_family']['rate']:.2f} | {100*x['negative_family']['rate']:.2f} |")
    b = r['block20_variance_diagnostic']
    lines += ['', 'Alle Monte-Carlo-Wilsonintervallen en 42 gedeeltelijke nulscenario’s staan onverkort in de JSON. Positief en negatief kunnen tegelijk voorkomen op verschillende horizons; percentages hoeven niet exact bij elkaar op te tellen. De gezamenlijke nul is niet voldoende voor sterke FWER-controle: daarom zijn ook scenario’s met +4 netto punten op één horizon en een echte nul op de andere meegenomen.', '',
        '### Wat de gecontroleerde contrasten laten zien', '',
        '- Bij onafhankelijke Gaussische waarnemingen ligt de totale familieverwerping bij 250/500 sessies ongeveer op 5%; bij slechts circa 45 geselecteerde dagen (125 sessies) hoger. Het gaat dus niet om een evident kapotte Holm-implementatie.',
        '- Dikke staarten alleen (t5) reproduceren de grote block20-afwijking niet in deze vaste controle. Het negatieve-scheefheidsmodel geeft juist vaker foutieve positieve ondersteuning; alleen naar het gunstige positieve percentage in één empirisch nulmodel kijken is onvoldoende.',
        '- Empirische block1/5/20 gebruiken dezelfde marginale residuen. De sterkere block20-afwijking wijst op relevantie van afhankelijkheid en de gekozen covariantiemeetlat. Ook na symmetrisering van hele paired blokken blijft de afwijking bestaan: scheefheid alleen verklaart haar niet. Deze nulmodellen veranderen meer dan één eigenschap; dit is een modeldiagnose, geen unieke causale verklaring voor marktrendementen.',
        f"- In het bekende stationaire circulaire-block20-model is de ware asymptotische variantiecoëfficiënt {b['true_to_HAC5_variance_ratio'][0]:.4f}× (2m) en {b['true_to_HAC5_variance_ratio'][1]:.4f}× (15m) de verwachte populatie-HAC5-coëfficiënt. HAC5 downweight lags1–5 en negeert lags6–19. Dit levert in dit model een concrete onderschattingsroute; het is geen bewezen toekomstige NQ-covariantie of voorstel om automatisch lag20 te gebruiken.", '',
        '**Gevolg:** de eerdere power-/134-dagenraming blijft een planningsscenario, geen goedgekeurde minimale proefomvang. Er is geen vervangende toets geselecteerd. Voor confirmatoire vrijgave is een afzonderlijke, vooraf vastgelegde inferentiebeoordeling nodig. Een betere nulkalibratie bewijst op zichzelf nog geen edge.', '',
        '## 3. Werkelijk beschikbare data: belangrijke bijstelling', '',
        'De vorige inventaris kon de accountrechten niet bevestigen. Deze audit heeft de bestaande Safari-sessie wel kunnen openen: het account is ingelogd en de accountpagina bevestigt actieve Premier-proeftoegang. Het NQZ25 historical-downloadformulier biedt Intraday/1 minuut en noemt 20.000 records per aanvraag. De proefperiode is niet nieuw aangegaan door de assistent.', '',
        'Dat recht is tijdelijk en niet hetzelfde als een permanent gratis bronabonnement. De abonnements-/betalingsdetails staan uitsluitend in het genegeerde private bewijsbestand; geen kaart- of adresgegevens bewaard. De gebruiker is in de chat gewezen op de automatische verlenging en directe beëindiging van proeftoegang bij opzeggen. Er is niets gewijzigd of opgezegd.', '',
        'Er is NIET op Download geklikt: beschikbaarheid van een niet-leeg bestand voor een concreet ouder contract, resterend dagquotum en gebruiksrechten voor de beoogde verwerking zijn nog geen bewezen intake. De formulierdefaults zijn geen datadekkingsbewijs. Er is ook geen API-/BBO-/tickrecht aangetoond. De pagina vermeldt vertraging van 10 of 15 minuten voor futuresquotes. Zo’n scherm kan geen realtime uitvoeringsprijs om 15:00:00 bewijzen.', '',
        'Een geautoriseerde historische intake zonder nieuwe kosten is nu een concrete route, geen bewezen kant-en-klare onafhankelijke dataset. Eerst contracten/datumbereik, bronhashes, opwarming, kalender, rollovers en eerdere toegang vastleggen. Geen resultaten bekijken tijdens kwaliteitsintake. Een andere vendor op dezelfde 435 ontdekkingsdagen maakt die dagen niet onafhankelijk.', '',
        'De [officiële historische-downloadhulp](https://help.barchart.com/support/solutions/articles/242748-how-can-i-download-historical-data-) bevestigt Premier-minuutgeschiedenis, maar is oud en noemt nog 10.000 records; het huidige geobserveerde formulier noemt 20.000. Dit onderscheid is expliciet, niet stilzwijgend opgelost door één bron te kiezen.', '',
        '## 4. Uitvoerbaarheid en kosten zonder dubbeltelling', '',
        '| Rekengrondslag | Correcte aftrek | Wat niet dubbel aftrekken |', '|---|---|---|',
        '| Bevroren raw-bar onderzoeksankers | 1,000 pt uitvoeringsreserve + 0,225 pt commissie = 1,225 pt / $24,50 RT | Niet nogmaals automatisch een spreadpost bovenop deze reeds bestaande reserve |',
        '| Werkelijk vastgelegde koop-/verkoopfills | Geobserveerde verkoopfill minus koopfill, daarna werkelijke commissie/fees die nog niet in P&L zitten | Spread/slippage zitten al in het verschil met de referentieprijzen; geen extra forfaitaire 1,225 pt |',
        '| Quote-proxy: eerste geldige ask na instaptijd en bid na uitstaptijd | Bid_exit − Ask_entry − nog niet ingebedde adverse uitvoeringskosten − 0,225 pt veronderstelde commissie | De gekruiste spread zit al in ask/bid; niet nogmaals volledige spread of $20 reserve rekenen |', '',
        'V2 gebruikt 15:00-open→15:01-close (bekend om15:02) en 15:00-open→15:14-close (bekend om15:15). Een werkelijke tijdorder kan pas op/na de grens en na latency worden uitgevoerd; een afsluitende laatste transactie is geen gegarandeerde fill op die grens. De quote-proxy hoort daarom bij uitvoeringsonderzoek, niet als selectieve vervanging van v2-uitkomsten. Geen gunstige vertraging of beste uitvoerprijs achteraf kiezen.', '',
        'De geregistreerde CSV-kolommen bevatten OHLCV, geen bid/ask, quote-/ontvangsttijd, orderbevestiging, queue of fills. Twee ticks per kant zijn een veronderstelling, niet aangetoond te ruim of te krap. Ook het commissiebedrag is een bevroren aanname, geen geverifieerd actueel brokerall-in tarief.', '',
        'Het [CME Liquidity Tool](https://www.cmegroup.com/tools-information/cme-liquidity-tool.html) en de [methodologie](https://www.cmegroup.com/education/articles-and-reports/understanding-the-cme-liquidity-tool-methodology) kunnen geaggregeerde spread/depth/cost-to-trade context geven, maar gecertificeerde specifieke instap-/uitstapquotes en brokerlatency ontbreken. Geauthenticeerde tooldata is niet opgehaald. Gratis liquiditeitsstatistieken zijn geen gratis tickfeed.', '',
        '## 5. Concreet vervolg, nog niet uitgevoerd', '',
        '1. Behandel bestaande Premier-proeftoegang als tijdelijke mogelijkheid, niet als kostenloos doorlopend abonnement. Beslis zelf over verlenging/opzegging; de audit autoriseert geen wijziging.',
        '2. Bereid één afgescheiden oudere-contract-intake voor, zonder rendementstoets. Benut alleen reeds toegestane exports zonder nieuwe kosten. Geen marktuitkomsten openen voordat het onafhankelijke venster en protocol vastliggen.',
        '3. Laat de inferentie vóór nieuwe toetsvrijgave afzonderlijk beoordelen en zo nodig versioneren. Geen stilzwijgende v2-wijziging, nieuwe bandbreedte op de geobserveerde uitkomst of herkeuring van ontdekkingsdagen.',
        '4. Geen technische schaduwproef starten totdat een passende legale quote-/tijdbron is bevestigd. Een later geautoriseerde technische proef gebruikt vooraf gekozen sessies buiten de bevestigende steekproef en geen echte orders.', '',
        '## Reproductie', '',
        '`python -m scripts.afternoon_gonogo_audit` reproduceert alleen de vastgelegde synthetische kalibratie. `python -m scripts.report_afternoon_gonogo` schrijft dit lokale rapport. V2, 73 bevroren en 115 beschermde archiefbestanden worden niet aangepast. De eerdere haalbaarheidsrapporten blijven als historisch beslisspoor intact. Geen GitHub-push of Vercel-publicatie in deze opdracht.', '']
    (ROOT/'docs/AFTERNOON_GO_NO_GO_AUDIT.md').write_text('\n'.join(lines))


if __name__ == '__main__':
    run()
