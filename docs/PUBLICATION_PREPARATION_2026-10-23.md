# Publicatie van de voorbereidingsstand 2019–2021

## Afbakening

De gebruiker heeft op 23 oktober 2026 expliciet gevraagd om de lokale onderzoeksstand naar GitHub main te pushen en rechtstreeks op het bestaande Vercel-productieproject `quantt` te publiceren. Dit geeft geen vrijgave voor nieuwe strategie-signalen of P&L op de geregistreerde historische restperiode.

De publicatie omvat ook de eerdere lokale onderzoeksrondes die nodig zijn voor de reproduceerbaarheid en de drie-kandidatenpagina. De oorspronkelijke rapporten, regels en bronhashes worden niet herschreven. Een afzonderlijke navigatiebalk verwijst vanuit de onderzoekspagina’s naar de actuele kwaliteitsstatus. Oude ontvangststanden blijven als historische rapportage herkenbaar.

## Gecontroleerde stand

- 103 planblokken, 105 fysieke bronbestanden, 14 contracten.
- 1.263.677 unieke contractminuten, nul numerieke OHLCV-fouten en nul conflicterende duplicaten.
- Nieuwe toetsperiode 14 januari 2019–31 december 2021: 733 ATR-ready evaluatiedagen, 706 met compressie-context en 619 met volledige sweep-nachtcontext. Geen trade-aantallen.
- Twee byte-identieke kwaliteits-/importruns. De oude 435 ontdekkingsdagen en oorspronkelijke 81/109/63 trades exact gereproduceerd als regressiecontrole, niet als nieuwe validatie.
- Op 13 echte rollover-openingen blijft de vooraf bekende ATR/context gelijk na afknippen van de actuele RTH en alle latere data.
- De bestaande 550 bestanden, inclusief de eerdere 517-bestandenfreeze, blijven byte-identiek. De uitbreiding voegt publicatie- en navigatiebestanden toe.

## Grenzen blijven zichtbaar

De onafhankelijke toets blijft vergrendeld. De datum-specifieke CME-uitzonderingskalender en de betekenis van ontbrekende vendorvolume-minuten rond enkele rolloverbeslissingen zijn nog niet volledig onderbouwd. Vooral juni 2019 en maart 2020 vragen verdere verificatie. Geen ontbrekende minuut is ingevuld en geen rolloverdatum is op P&L geselecteerd. Licentie-, onafhankelijke timestamp- en tick-fillbevestiging worden niet geclaimd.

## Publicatiebeveiliging

Ruwe CSV’s, privé-Parquetbestanden, lokale research-artifacts, omgevingsbestanden en aanmeldgegevens blijven buiten Git en de Vercel-upload. De Vercel-uploadlijst wordt vóór vrijgave gecontroleerd. De nieuwe publieke kwaliteitspagina bevat tellingen, vlaggen en bronverwijzingen, geen minuutarrays of nieuwe tradeledgers.

De status- en commitbevestiging van de daadwerkelijke publicatie wordt afzonderlijk uit GitHub en Vercel gelezen. Dit document is geen vervanging voor die externe bevestiging.
