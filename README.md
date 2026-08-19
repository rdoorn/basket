# Basket

Een no-login webapp om een weekmenu samen te stellen door recepten op een kalender te
slepen. Uit het menu wordt automatisch een boodschappenlijst afgeleid (geschaald naar het
aantal eters) en per supermarkt een prijs berekend om te zien waar het het goedkoopst is.

> Status: **v0.1** — werkende app met een *mock* prijsbron. Echte Albert Heijn / Picnic
> integraties volgen later achter dezelfde port.

## Snel starten

Vereist: Docker (bijv. Colima), en voor lokaal ontwikkelen `uv` (backend) en `pnpm`
(frontend).

```bash
make build   # bouwt mongo/api/frontend images
make up      # start alles in de achtergrond
make ps      # status
make logs    # volg logs
make down    # stoppen
```

Daarna:

- Frontend (UI): <http://localhost:8173>
- API: <http://localhost:18420> (bijv. `curl http://localhost:18420/recipes`)
- MongoDB: `mongodb://localhost:47017/basket`

De poorten zijn bewust niet-standaard gekozen. Bij de eerste start seedt de API één recept
(Macaroni alla Siciliana).

## Functionaliteit (v0.1)

- **Kalender** — 14 dagen vanaf vandaag; sleep een recept naar een dag. Sleep tussen dagen
  om te wisselen (swap) of te verplaatsen (move).
- **Porties** — per dag een vermenigvuldiger (0.5× / 1× / 1.5× / 2× of eigen waarde),
  altijd t.o.v. het aantal personen waarvoor het recept beschreven is.
- **Boodschappenlijst** — automatisch afgeleid uit het menu, geaggregeerd en geschaald.
- **Recepten** — toevoegen, bewerken, verwijderen (maaltijd of 🍞 baksel); en een
  leesweergave met icoon, volledige ingrediëntenlijst, kooktijd-overzicht (prep vs. actief
  koken) en de uitgebreide stappen.
- **Extra's** — sleep een recept (bijv. een baksel) naar de Extra's-zone naast de kalender
  om het zonder dag aan de boodschappen toe te voegen, met eigen ×-portie.
- **Huisdiervoer** — een bewerkbare lijst van wat je huisdier lust (met een geschat gewicht
  per stuk). De app vult automatisch tot een wekelijks streefgewicht (± ¼ kg, standaard
  ~1 kg): de goedkoopste + willekeurige items. Elk item is te vervangen (↻) of te
  regenereren; de selectie komt in de boodschappen en telt mee in de prijs.
- **Kopen** — overzicht met per supermarkt de prijs per ingrediënt en het totaal, de
  goedkoopste uitgelicht (nu via de mock-prijsbron).

## Architectuur

Ports & adapters (hexagonaal). Vue 3 (pnpm) → REST/JSON → FastAPI (uv) → services → ports →
adapters (MongoDB, prijsbron). Supermarkten en de database zijn adapters; het domein bevat
geen framework- of vendor-code. De mock-prijsbron implementeert dezelfde port die Albert
Heijn / Picnic later invullen.

```
backend/   FastAPI, uv        app/{domain,services,ports,adapters,api}
frontend/  Vue 3 + Vite, pnpm src/{views,components,stores,api}
docker-compose.yml, Makefile
docs/plans/                   ontwerp + implementatieplan
```

## Ontwikkelen & testen

```bash
# Backend (in backend/)
uv sync
uv run pytest -v
uv run flake8 app tests

# Frontend (in frontend/)
pnpm install
pnpm vitest run
pnpm build

# Backend-tests + lint in één keer
make test-backend
```

## Randvoorwaarden

- **Dependency-versheid (3 dagen):** geen release nieuwer dan 3 dagen. Backend via uv
  `exclude-newer`; frontend via pnpm `minimum-release-age`. Alle versies gepind.
- **Geen login;** data in MongoDB.
- **Python:** PEP 8/257/484/561/20, flake8 en pytest.

## Later uit te werken

- Echte prijsadapters voor Albert Heijn en Picnic (credentials, API/scraping).
- Ingrediënt-normalisatie & merk-pinning (bijv. `spaghetti` → `Grand'Italia spaghetti`) met
  een "niet beschikbaar → alternatief / niet kopen / recept aanpassen"-melding.
- Externe bron-ingrediënten (bijv. gehakt van de boerderij) buiten de winkeltotalen, met een
  "vriezer of kopen?"-keuze.
- Seizoensbewust automatisch genereren van het weekmenu.
