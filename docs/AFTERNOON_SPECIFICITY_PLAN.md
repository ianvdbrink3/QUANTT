# Vastlegging vóór de naburige-kwartiervergelijking

De onderzochte bevinding blijft verkennend op reeds bekeken data. De eerdere
v0.9/vNext-experimenten, wegingsaudit, marktmechanisme-kaart en hun toetsen
blijven ongewijzigd. Dit is geen nieuwe onafhankelijke preregistratie of holdout.

## Bestaande 15:00-bevinding

Op 435 volledige RTH-dagen bedroeg de onvoorwaardelijke 15:00–15:15-beweging
gemiddeld +0,8465517241 punten en mediaan +1,25 punten. De 167 UP/MID-dagen
gaven gemiddeld +7,5404191617 punten en mediaan +4,00 punten. De 131
DOWN/MID-dagen gaven gemiddeld +3,6660305344 punten in neerwaartse richting,
mediaan +2,50 punten. De eerder uitgevoerde overlapbewuste benchmarkvergelijking
gaf een nominale, niet-confirmatoire p van 0,0065074 op log-basispunten.

## Exacte volgende vergelijking

Uitsluitend 14:30–14:45, 14:45–15:00 en 15:00–15:15 NY. Voor ieder tijdstip:
alle 435 dagen, UP/MID en DOWN/MID. Richting wordt bepaald ten opzichte van de
09:30-open op de laatste volledig voltooide minuut. Range is de high-low-range
van alle dan voltooide RTH-bars gedeeld door dezelfde vooraf bekende ATR14.
MID blijft exact [0,5; 1,2), inclusief de eerder gehanteerde exclusieve bovengrens.
De eerste nog niet voltooide bar mag geen selectie-informatie leveren.

Gerapporteerd: aantallen, bruto gemiddelde/mediaan, dezelfde waarden minus
1,225 punten, positieve fracties in de vaste meetrichting en het verschil met
de onvoorwaardelijke benchmark in diezelfde richting. ALL meet opwaarts; DOWN
meet neerwaarts en vergelijkt dus met een blinde neerwaartse benchmark.

Tien vooraf bepaalde contrasten: 15:00 minus elk van de twee eerdere kwartieren
voor de drie ruwe groepsgemiddelden (zes), plus voor de contextmeerwaarde van
UP en DOWN boven hun eigen klokbenchmark (vier). Primaire p-waarden op log-bp,
daggeclusterde gezamenlijke influence scores met overlapcovariantie, vaste
HAC(5)-controle op kalenderafhankelijkheid en één Holm10-correctie. Punten-
intervallen worden afzonderlijk berekend. Geen extra tijdstippen, horizons,
drempels, kwartaalfilters of stop/target-keuzes.

De cohorten worden per klok opnieuw geselecteerd en kunnen veranderen. De
vergelijking schat dus geen causale behandeling op identieke, gefixeerde dagen.
Niet-verwerpen bewijst geen gelijkwaardigheid of algemeen momentum.

## Uitvoering en afbakening

`python -B -m scripts.afternoon_specificity --register` legt code, methode en
inputhashes vast voordat nieuwe buurvenster-uitkomsten worden gelezen.
Daarna één vaste run met een tweede verse bronherlading ter reproductie.
`--verify` controleert de afgesloten resultaten zonder een nieuwe run.

De output wordt lokaal als afzonderlijk rapport en tabellen vastgelegd. Deze
opdracht geeft geen nieuwe toestemming voor GitHub- of productiepublicatie.
Er worden geen handelsstrategieën, fills, stops, targets of optimalisaties gebouwd.
