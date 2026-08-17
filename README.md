# Basket

Een webapp die uit vooraf toegevoegde menu's automatisch een weekmenu samenstelt en
vervolgens uitrekent waar je de bijbehorende boodschappen het goedkoopst kunt halen.

> Status: **concept**. Dit document beschrijft het idee. De uitwerking volgt later.

## Het idee

Je bouwt een collectie van menu's (gerechten met ingrediënten). De app genereert daaruit
een weekmenu. Op basis van dat weekmenu stelt de app een boodschappenlijst samen en
vergelijkt die online bij supermarkten om de goedkoopste optie te bepalen. Daarbij houdt
de app rekening met het seizoen: gerechten met seizoensgebonden of beter beschikbare
ingrediënten krijgen voorrang.

## Kernfunctionaliteit

- **Menubeheer** — gerechten/menu's vooraf toevoegen met hun ingrediënten.
- **Weekmenu genereren** — automatisch een menu voor de week samenstellen uit de collectie.
- **Boodschappenlijst** — ingrediënten van het weekmenu bundelen tot één lijst.
- **Prijsvergelijking** — online kijken bij **Albert Heijn** en **Picnic** waar de
  boodschappen het goedkoopst zijn.
- **Seizoensbewust** — rekening houden met seizoensgerechten en beschikbaarheid van
  ingrediënten bij het genereren van het weekmenu.

## Tech stack

- **Backend**: Python
- **Frontend**: Vue
- **Package/tooling**: [uv](https://github.com/astral-sh/uv)
  - Geen tools/dependencies gebruiken die minder dan 7 dagen oud zijn.
- **Deployment**: alles draait in containers.

## Later uit te werken

- Architectuur backend/frontend en API-contract.
- Datamodel voor menu's, gerechten en ingrediënten.
- Hoe prijzen bij Albert Heijn en Picnic worden opgehaald (API, scraping, beschikbaarheid).
- Bron en logica voor seizoensinformatie.
- Algoritme voor het genereren van het weekmenu (variatie, voorkeuren, dieetwensen).
- Container-setup (Dockerfiles, compose, lokale ontwikkelomgeving).
- Authenticatie / gebruikers (indien nodig).
