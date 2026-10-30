# QUANT-OS — terminal design manifest

Datum: 30 oktober 2026. Scope: uitsluitend Portfolio OS. Onderzoeksresultaten, Python-signalen, brokerregels en bestaande NQ/ES-pagina's blijven ongewijzigd.

## Onderzoek en selectie

Gezocht op GitHub/web naar anti-ai-slop, unslop, cursorrules/clauderules, financiële shadcn-dashboards, OpenBB en Linear. Deze bronnen zijn ontwerpreferenties, geen nieuwe globale agentinstructies. Er zijn geen externe skills, installatiescripts of regelplugins uitgevoerd/geïnstalleerd.

| Bron | Bevinding | Vertaling voor QUANT |
| --- | --- | --- |
| [muris11/anti-ai-slop](https://github.com/muris11/anti-ai-slop) | Een verbodslijst vervangt geen eigen productrichting; herhaling zonder functie is het probleem. | Richting is expliciet: rekenkundige inspectieterminal, geen SaaS-overzicht. |
| [rwcod/anti-ai-slop-ui](https://github.com/rwcod/anti-ai-slop-ui) | Productdoel, tokens, lay-out en review horen vóór componentkeuze. | Eerst dit manifest; daarna één samenhangend raster en browsercontrole. |
| [aahil62/unslop](https://github.com/aahil62/unslop) | Meet problemen, kies richting, controleer wijzigingen visueel. | Vergelijk desktophoogtes, rijdichtheid, overflow en echte interacties. |
| [trisouro/slop-guard](https://github.com/trisouro/slop-guard) | Expliciete regels kunnen met controleerbare checks worden bewaakt. | Statische tests verbieden gradients, shadows, emoji en grote rondingen in de OS-code. |
| [Cursor-regelzoekresultaat](https://github.com/roedyrustam/vibes-plug/blob/main/.cursorrules) | Bevat veel bredere agent-/orkestratie-instructies dan deze ontwerptaak. | Niet overgenomen. Alleen de gebruiker en projectinstructies bepalen uitvoering. |
| [shadcn finance dashboard](https://github.com/shubham-srv/finance-dashboard), [shadcn discussie](https://github.com/shadcn-ui/ui/discussions/3158) | Finance-template is vaak persoonlijk budgetbeheer, niet een handels-/auditterminal. | Geen template, mockauth of stat-card-layout kopiëren; bestaande React-stack behouden. |
| [Linear redesign](https://linear.app/now/how-we-redesigned-the-linear-ui) | Vermindert visuele ruis met consistente headers, tabs, uitlijning en een neutralere hiërarchie. | Smalle commandobalk, gedempte vlakken, geen dominante zijbalk of decoratieve KPI-blokken. |
| [Raycast List](https://developers.raycast.com/api-reference/user-interface/list), [Keyboard](https://developers.raycast.com/api-reference/keyboard) | Zoeken, een extra filter en een gekoppeld detailvlak ondersteunen snel lijstwerk. | Eén geselecteerde dag; audit links en brief/payload direct rechts. Sneltoetsen 1–4 zonder typen te onderscheppen. |
| [OpenBB Workspace](https://docs.openbb.co/workspace), [broncode](https://github.com/OpenBB-finance/workspace) | Tabellen, grafieken en parameters vormen afzonderlijke maar samenwerkende onderdelen. De gevonden repo is sinds 1 oktober 2026 gearchiveerd. | Gebruik het werkruimteprincipe als referentie; geen nieuwe afhankelijkheid op een gearchiveerde codebase. |
| [Koyfin functionaliteit](https://www.koyfin.com/help/topic/functionality/) | Watchlists, kolommen, filters en gekoppelde dashboardonderdelen staan centraal. | Instrumenten naast elkaar in vaste kolommen; dezelfde selectie voedt de inspector. |
| [Bloomberg Terminal](https://bloomberg.com/professional/solution/bloomberg-terminal/) | Meerdere marktmonitors binnen een werkruimte. | Gekoppelde panelen; geen claim op hun interne CSS. |
| [Fey](https://fey.com/) | De huidige site meldt aansluiting bij Wealthsimple en gesloten inschrijving. | Geen actuele Fey-app nagebootst of getest; geen onbewezen interne ontwerprichtlijnen toegeschreven. |

Een merknaam, donkere achtergrond of monospace font maakt een interface niet professioneel. Voor dit product zit de kwaliteit in vergelijkbare kolommen, volledige statusinformatie, voorspelbare selectie en onderscheid tussen historische observatie, rekenaannames en uitvoeringsrecht. De concrete onderstaande waarden zijn onze ontwerpkeuzes en de eisen van de gebruiker, geen gekopieerde productspecificaties.

## Niet-onderhandelbare tokens

| Token | Waarde |
| --- | --- |
| Canvas | `#09090b` |
| Paneel | `#111113` |
| Hairline | `1px solid #27272a` |
| Primair / secundair / gedempt | `#fafafa` / `#a1a1aa` / `#52525b` |
| Positief / waarschuwing / blokkade | `#10b981` / `#f59e0b` / `#ef4444` |
| Font | `"JetBrains Mono", "Geist Mono", "SFMono-Regular", Consolas, monospace` |
| Cijfers | `font-variant-numeric: tabular-nums` op de volledige terminal |
| Body / labels | 12px / 10–11px uppercase, vaste kolomuitlijning |
| Commandobalk / tabrail | 36px / 30px, zonder losse buitenmarges |
| Datariem | 26–28px hoog; diepere inhoud scrolt intern |
| Panelen | Geen shadow, geen gradient, geen zwevende cardmarges; radius 0 |
| Controls | Maximaal 3px radius; zichtbare toetsenbordfocus |

Geen externe fontdownload nodig: lokale fonts vallen terug op systeem-monospace. Geen emoji, neon/cyan/paars, blur, glas, gradient, glow, springanimatie, hero, pill-badge, grote getallencard of marketingcopy. Kleur drukt alleen richting, afwijking, selectie of blokkade uit. Gedempte tekst is alleen voor ondersteunende labels; actieve data blijft contrastrijk.

## Schermarchitectuur

Een desktopwerkruimte gebruikt `100dvh` en vier toetsenbordbereikbare tabs:

1. **Terminal Cockpit:** links de volledige QQQ/TQQQ-signaalmatrix, daaronder anti-whipsaw/timing en S1-regels. Rechts sleeves, Unit-NAV en risico. Onderin een gekoppelde audit/brief-inspector en compacte kostenmatrix.
2. **60D Audit Ledger:** volledige lijst, zoeken en All/Fills/Cost-Blocked/Data-Skips, met detailpaneel rechts.
3. **Cost & Broker Matrix:** conditionele tarieven, 5/10bp-spaardrempels en routebeperkingen.
4. **Dagbrief Inspector:** dagselectie en leesbaar origineel verslag, plus de beschikbare orderpayloads.

De 36px-hoofdbalk draagt systeem, modus, policy, regime, bewijsstatus en klokken. De direct aangesloten tabrail draagt de langere tabnamen en datasetselectie. Zo blijven de vier werkbladen bruikbaar op een MacBook zonder een overladen commandoregel of een tweede landingspagina.

Bij 1440×900 en 1728×1117 moeten de cockpitonderdelen binnen de werkruimte passen, zonder buitenste paginascroll. Tabellen en originele brieven scrollen intern. Op smalle schermen blijft de tekst leesbaar via een verticale opzet; de desktop-100vh-eis mag geen onleesbare mobiele spreadsheet opleveren.

## Bewijsstatus en financiële semantiek

- `SHADOW_ONLY` en `LIVE_LOCKED` zijn permanent zichtbaar.
- `SHADOW_OK` blijft `REPLAY_ONLY/PENDING` zolang geen volledige onafhankelijke forwardfase is afgerond. `ROUTE_VERIFIED` is niet bevestigd; `STRATEGY_EVIDENCE` is onvoldoende. Geen cosmetisch groene go/no-go-statussen.
- Een mathematisch passende kostenpoort is geen `APPROVED_INTENT`. Brokerrechten blijven apart vergrendeld.
- Tijdklokken zijn actueel; marktprijzen hebben een expliciete historische datum. Geen gefingeerde livefeed.
- Profielkeuze is een preview. Auditcurve, actieve policy en echte circuitbreaker veranderen niet door een dropdown. Scenario-inleg is geen gestorte cash.
- Order-id en policyhash worden volledig inspecteerbaar. Niet opgeslagen HMAC-handtekeningen worden niet verzonnen; de oorspronkelijke proceslokale approval is geen blijvend opgeslagen digitale handtekening.
- Unit-NAV, resultaten, fee-aannames en brondata worden door deze herbouw niet opnieuw berekend of aangepast.

## Acceptatiecontrole

- Alle vier de tabs en sneltoetsen werken; toetsen in invoervelden wisselen geen tab.
- Dagselectie werkt met muis en toetsenbord, en koppelt de juiste brief en bijbehorende intents.
- Iedere numerieke cel is monospace/tabular; bedragen en percentages zijn rechts uitgelijnd.
- Geen gradients, shadows, emoji of afgeronde grote cards in de nieuwe OS-broncode.
- Desktop cockpit past op de vastgelegde testvensters; geen horizontale buiten-overflow op mobiel.
- Geen browserconsolefouten; HTTP200; typecheck, build en volledige oude/nieuwe tests groen.
- Beschermde onderzoeks- en NQ/ES-bestanden behouden exact hun vooraf geregistreerde SHA-256.
