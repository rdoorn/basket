"""Seed data: Recipe 1 — Macaroni alla Siciliana.

Transcribes Recipe 1 faithfully into a :class:`Recipe`, preserving the
elaborate Dutch instructions (including per-step reasoning) verbatim. Also
provides :func:`seed_if_empty` to insert it once when the recipe collection is
empty (idempotent).
"""
from app.domain.pet import PetFood
from app.domain.recipe import Ingredient, Recipe, Step
from app.domain.staple import Staple
from app.domain.staples import normalize_name
from app.ports.pet_food_repo import PetFoodRepo
from app.ports.recipe_repo import RecipeRepo
from app.ports.staple_repo import StapleRepo

SEED_RECIPE_ID = "macaroni-alla-siciliana"

# The "heb ik vast wel" starter list: the legacy hardcoded defaults plus the
# bake staples (suiker, zwarte sesam, instant gist, basterdsuiker). Names are
# normalized on create by the repo.
STAPLE_SEED: list[str] = [
    "olijfolie",
    "citroensap",
    "chilivlokken",
    "gehakt",
    "rundergehakt",
    "zout",
    "zwarte peper",
    "venkelzaad",
    "suiker",
    "zwarte sesam",
    "instant gist",
    "basterdsuiker",
]

# Editable, cavia-friendly starter list. ``weight_g`` is a static guess of the
# grams per purchase-unit used only as a guide by ``pet_service``.
PET_FOOD_SEED: list[PetFood] = [
    PetFood(id="paprika", name="paprika", weight_g=150),
    PetFood(id="komkommer", name="komkommer", weight_g=400),
    PetFood(id="ijsbergsla", name="ijsbergsla", weight_g=400),
    PetFood(id="wortel", name="wortel", weight_g=80),
    PetFood(id="andijvie", name="andijvie", weight_g=300),
    PetFood(id="veldsla", name="veldsla", weight_g=100),
    PetFood(id="koolrabi", name="koolrabi", weight_g=300),
    PetFood(id="mais-vers", name="mais (vers)", weight_g=250),
    PetFood(id="witlof", name="witlof", weight_g=150),
    PetFood(id="babyromaine", name="babyromaine", weight_g=200),
]


def build_seed_recipe() -> Recipe:
    """Return the seeded Macaroni alla Siciliana recipe (frisse variant).

    Ingredients are grouped (Pasta / Basis / Tomatenbasis / Kruiden /
    Frisse afwerking) with quantities and units from the source. The gehakt
    ingredient carries ``source="external"`` (reserved: still shown but
    excluded from store totals later). A synthetic ``prep`` step 0
    (mise en place, ~10 min, marked as an estimate) precedes the nine cooking
    steps.
    """
    ingredients = [
        # Pasta
        Ingredient(group="Pasta", name="macaroni", quantity=350, unit="g"),
        # Basis
        Ingredient(
            group="Basis",
            name="gehakt",
            quantity=300,
            unit="g",
            note="zonder zout van de boerderij",
        ),
        Ingredient(
            group="Basis", name="ui", quantity=1, unit="stuk", note="groot, fijngesneden"
        ),
        Ingredient(
            group="Basis", name="knoflook", quantity=2, unit="teen", note="fijngehakt"
        ),
        Ingredient(group="Basis", name="rode paprika", quantity=1, unit="stuk"),
        Ingredient(group="Basis", name="courgette", quantity=1, unit="stuk"),
        Ingredient(group="Basis", name="olijfolie", quantity=2, unit="el"),
        # Tomatenbasis
        Ingredient(
            group="Tomatenbasis", name="tomatenblokjes", quantity=400, unit="g"
        ),
        Ingredient(group="Tomatenbasis", name="passata", quantity=200, unit="g"),
        Ingredient(group="Tomatenbasis", name="tomatenpuree", quantity=1, unit="el"),
        # Kruiden
        Ingredient(group="Kruiden", name="venkelzaad", quantity=0.5, unit="tl"),
        Ingredient(group="Kruiden", name="oregano", quantity=1, unit="tl"),
        Ingredient(group="Kruiden", name="chilivlokken", quantity=0.25, unit="tl"),
        Ingredient(group="Kruiden", name="laurierblad", quantity=1, unit="blad"),
        Ingredient(
            group="Kruiden",
            name="zout",
            quantity=1,
            unit="tl",
            note="verdeeld, later bijstellen",
        ),
        Ingredient(
            group="Kruiden",
            name="zwarte peper",
            quantity=None,
            unit=None,
            note="royaal, naar smaak",
        ),
        # Frisse afwerking
        Ingredient(
            group="Frisse afwerking",
            name="citroenrasp",
            quantity=1,
            unit="citroen",
            note="rasp van 1 citroen",
        ),
        Ingredient(
            group="Frisse afwerking",
            name="citroensap",
            quantity=0.5,
            unit="citroen",
            note="sap van ⅓ tot ½ citroen, naar smaak",
        ),
        Ingredient(
            group="Frisse afwerking",
            name="basilicum",
            quantity=None,
            unit=None,
            note="handvol verse blaadjes",
        ),
        Ingredient(
            group="Frisse afwerking", name="Parmezaan", quantity=35, unit="g"
        ),
        Ingredient(
            group="Frisse afwerking",
            name="pastawater",
            quantity=0.5,
            unit="kop",
            note="apart houden voor het binden",
        ),
    ]

    steps = [
        Step(
            order=0,
            title="Mise en place",
            phase="prep",
            duration_min_low=10,
            duration_min_high=10,
            instructions=(
                "Snijd de ui fijn, hak de knoflook, snijd de paprika in blokjes en "
                "de courgette in halve maantjes of blokjes. Rasp de Parmezaan en de "
                "citroenschil en zet alle kruiden klaar. Door alles vooraf klaar te "
                "zetten kook je straks zonder onderbreken door. (De 10 minuten zijn "
                "een schatting die je zelf kunt aanpassen.)"
            ),
        ),
        Step(
            order=1,
            title="Gehakt bakken",
            phase="cook",
            duration_min_low=8,
            duration_min_high=10,
            instructions=(
                "Gebruik 300 g gehakt, 1 el olijfolie, ½ tl zout en zwarte peper. "
                "Bak op middelhoog tot hoog vuur. Belangrijk: eerst laten liggen, "
                "goed laten bruinen, de randjes donker laten worden. Doel: veel "
                "smaak opbouwen."
            ),
        ),
        Step(
            order=2,
            title="Ui + venkel + knoflook",
            phase="cook",
            duration_min_low=6,
            duration_min_high=8,
            instructions=(
                "Voeg 1 grote ui, 1 tl venkelzaad, 3 tenen knoflook en ½ tl "
                "chilivlokken toe. Bak tot de ui zacht en licht goudkleurig is. De "
                "venkel moet geurig worden, niet verbranden."
            ),
        ),
        Step(
            order=3,
            title="Paprika + courgette",
            phase="cook",
            duration_min_low=6,
            duration_min_high=7,
            instructions=(
                "Voeg 1 rode paprika, 1 kleine courgette en een snuf zout toe. Bak "
                "tot de paprika zachter wordt en de courgette licht kleurt. Niet "
                "helemaal kapot bakken."
            ),
        ),
        Step(
            order=4,
            title="Tomatenpuree bakken",
            phase="cook",
            duration_min_low=2,
            duration_min_high=2,
            instructions=(
                "Voeg 1 el tomatenpuree toe en bak kort mee tot hij iets donkerder "
                "wordt. Dit haalt het rauwe eraf."
            ),
        ),
        Step(
            order=5,
            title="Saus opbouwen",
            phase="cook",
            duration_min_low=20,
            duration_min_high=25,
            instructions=(
                "Voeg 1 blik tomatenblokjes (400 g), 200 g passata, 1 tl oregano, "
                "1 laurierblad, ½ tl zout en zwarte peper toe. Goed roeren en op "
                "laag vuur laten sudderen. Roer elke 5–7 minuten; wordt het te dik, "
                "voeg dan een klein scheutje water toe. Belangrijk: de saus moet "
                "losser blijven dan je vaste recept."
            ),
        ),
        Step(
            order=6,
            title="Pasta koken",
            phase="cook",
            duration_min_low=10,
            duration_min_high=12,
            instructions=(
                "Kook 350 g macaroni in ruim gezouten water al dente. Bewaar ½ kop "
                "pastawater voordat je afgiet."
            ),
        ),
        Step(
            order=7,
            title="Frisse afwerking",
            phase="finish",
            duration_min_low=2,
            duration_min_high=2,
            instructions=(
                "Zet het vuur laag of uit. Voeg de rasp van 1 citroen, het sap van "
                "⅓ citroen (proeven, eventueel meer), 1 flinke hand basilicum en "
                "20 g Parmezaan toe. Roer door de saus. Dit is waar de frisheid "
                "binnenkomt — niet eerder toevoegen."
            ),
        ),
        Step(
            order=8,
            title="Mengen",
            phase="finish",
            duration_min_low=2,
            duration_min_high=3,
            instructions=(
                "Voeg de gekookte macaroni toe en meng met ½ kop pastawater, beetje "
                "bij beetje. Roer goed door. De saus moet glanzen en mooi binden — "
                "niet droog."
            ),
        ),
        Step(
            order=9,
            title="Afmaken",
            phase="finish",
            duration_min_low=1,
            duration_min_high=1,
            instructions=(
                "Laatste toevoeging: 15 g extra Parmezaan, zwarte peper naar smaak "
                "en 1 el olijfolie. Proef op zout- en zuurbalans."
            ),
        ),
    ]

    return Recipe(
        id=SEED_RECIPE_ID,
        title="Macaroni alla Siciliana (frisse variant, zonder olijven)",
        icon="🍝",
        description=(
            "Lichter, frisser, aromatischer, maar nog steeds stevig en vullend."
        ),
        servings=4,
        total_time_min_low=50,
        total_time_min_high=60,
        tags=["pasta", "zomer"],
        notes="Gehakt zonder zout.",
        ingredients=ingredients,
        steps=steps,
    )


def build_spaghetti_bolognese() -> Recipe:
    """Return the Spaghetti bolognese recipe (2 personen, zonder passata)."""
    ingredients = [
        # Saus
        Ingredient(group="Saus", name="rundergehakt", quantity=200, unit="g"),
        Ingredient(
            group="Saus", name="ui", quantity=1, unit="stuk",
            note="klein, fijngesnipperd",
        ),
        Ingredient(
            group="Saus", name="knoflook", quantity=1, unit="teen",
            note="fijngehakt",
        ),
        Ingredient(
            group="Saus", name="wortel", quantity=0.5, unit="stuk",
            note="in kleine blokjes",
        ),
        Ingredient(group="Saus", name="olijfolie", quantity=1, unit="el"),
        Ingredient(group="Saus", name="tomatenpuree", quantity=1, unit="el"),
        Ingredient(
            group="Saus", name="tomatenblokjes", quantity=400, unit="g",
            note="1 blik",
        ),
        Ingredient(
            group="Saus", name="runderbouillon", quantity=100, unit="ml",
            note="of water met een half bouillonblokje",
        ),
        Ingredient(
            group="Saus", name="oregano", quantity=0.5, unit="tl",
            note="gedroogd",
        ),
        Ingredient(
            group="Saus", name="basilicum", quantity=0.5, unit="tl",
            note="gedroogd",
        ),
        Ingredient(
            group="Saus", name="laurierblad", quantity=1, unit="blad",
            note="optioneel",
        ),
        Ingredient(
            group="Saus", name="suiker", quantity=0.5, unit="tl",
            note="optioneel",
        ),
        Ingredient(
            group="Saus", name="zout", quantity=None, unit=None, note="naar smaak"
        ),
        Ingredient(
            group="Saus", name="zwarte peper", quantity=None, unit=None,
            note="naar smaak",
        ),
        # Pasta
        Ingredient(
            group="Pasta", name="spaghetti", quantity=200, unit="g",
            note="180–200 g",
        ),
        Ingredient(
            group="Pasta", name="zout", quantity=1, unit="el",
            note="voor het kookwater",
        ),
        # Serveren
        Ingredient(
            group="Serveren", name="Parmezaan", quantity=None, unit=None,
            note="geraspt",
        ),
        Ingredient(
            group="Serveren", name="verse basilicum", quantity=None, unit=None,
            note="of peterselie, optioneel",
        ),
    ]
    steps = [
        Step(
            order=0, title="Mise en place", phase="prep",
            duration_min_low=5, duration_min_high=5,
            instructions=(
                "Snipper de ui fijn, snijd de wortel in kleine blokjes, hak de "
                "knoflook en rasp de Parmezaan. Zo kook je straks zonder "
                "onderbreken door. (De 5 minuten zijn een schatting die je zelf "
                "kunt aanpassen.)"
            ),
        ),
        Step(
            order=1, title="Groenten fruiten", phase="cook",
            duration_min_low=6, duration_min_high=6,
            instructions=(
                "Verhit de olijfolie in een grote pan. Bak de ui en wortel 5 "
                "minuten op middelhoog vuur. Voeg de knoflook toe en bak 1 minuut "
                "mee."
            ),
        ),
        Step(
            order=2, title="Gehakt bakken", phase="cook",
            duration_min_low=6, duration_min_high=8,
            instructions=(
                "Voeg het rundergehakt toe en bak het rul en lichtbruin. Breng op "
                "smaak met een beetje zout en peper."
            ),
        ),
        Step(
            order=3, title="Saus maken", phase="cook",
            duration_min_low=45, duration_min_high=60,
            instructions=(
                "Voeg de tomatenpuree toe en bak 2 minuten mee. Voeg dan de "
                "tomatenblokjes, bouillon, oregano, basilicum, laurierblad en "
                "eventueel de suiker toe en roer goed door. Laat de saus 45 tot 60 "
                "minuten zacht pruttelen zonder deksel, af en toe roerend. Prak de "
                "tomaten tijdens het koken eventueel fijn met een houten lepel voor "
                "een gladdere saus."
            ),
        ),
        Step(
            order=4, title="Spaghetti koken", phase="cook",
            duration_min_low=8, duration_min_high=10,
            instructions=(
                "Breng een grote pan water aan de kook en voeg het zout toe. Kook "
                "de spaghetti volgens de verpakking beetgaar. Giet af en bewaar een "
                "klein kopje kookvocht."
            ),
        ),
        Step(
            order=5, title="Afmaken", phase="finish",
            duration_min_low=2, duration_min_high=2,
            instructions=(
                "Verwijder het laurierblad. Is de saus te dik, voeg dan een klein "
                "scheutje pastakookvocht toe. Voor een extra romige smaak kun je "
                "30–50 ml melk of een klontje boter door de saus roeren."
            ),
        ),
        Step(
            order=6, title="Serveren", phase="finish",
            duration_min_low=1, duration_min_high=1,
            instructions=(
                "Verdeel de spaghetti over twee borden, schep de bolognesesaus "
                "erop en bestrooi met geraspte Parmezaan en wat verse basilicum. "
                "Lekker met een groene salade of een stuk stokbrood."
            ),
        ),
    ]
    return Recipe(
        id="spaghetti-bolognese",
        title="Spaghetti bolognese (zonder passata)",
        icon="🍝",
        description=(
            "Klassieke bolognese zonder passata, met wortel en een lange sudder "
            "voor diepe smaak."
        ),
        servings=2,
        total_time_min_low=60,
        total_time_min_high=75,
        tags=["pasta"],
        notes="Zonder passata. De saus wordt lekkerder na een uur sudderen.",
        ingredients=ingredients,
        steps=steps,
    )


def build_salade_garnalen() -> Recipe:
    """Return the Salade met garnalen recipe (1 grote / 2 lichte porties)."""
    ingredients = [
        # Sla
        Ingredient(
            group="Sla", name="ijsbergsla", quantity=125, unit="g",
            note="hoofdbasis (100–150 g)",
        ),
        Ingredient(
            group="Sla", name="kropsla", quantity=None, unit=None,
            note="klein handje",
        ),
        Ingredient(
            group="Sla", name="rucola", quantity=None, unit=None,
            note="klein handje",
        ),
        Ingredient(
            group="Sla", name="komkommer", quantity=1, unit="stuk",
            note="½–1, in halve plakjes",
        ),
        # Topping
        Ingredient(
            group="Topping", name="Hollandse garnalen", quantity=150, unit="g",
            note="125–150 g",
        ),
        Ingredient(
            group="Topping", name="avocado", quantity=1, unit="stuk",
            note="als rijp; anders ei",
        ),
        Ingredient(
            group="Topping", name="ei", quantity=2, unit="stuk",
            note="hardgekookt, backup als avocado niet rijp is",
        ),
        Ingredient(
            group="Topping", name="croutons", quantity=35, unit="g",
            note="normaal",
        ),
        Ingredient(group="Topping", name="Parmezaan", quantity=15, unit="g"),
        # Dressing
        Ingredient(
            group="Dressing", name="frisse slasaus", quantity=None, unit=None,
            note="bijv. Gauda's Glorie; niet te veel",
        ),
    ]
    steps = [
        Step(
            order=1, title="Sla snijden", phase="prep",
            duration_min_low=3, duration_min_high=3,
            instructions=(
                "Snijd de ijsbergsla grof en voeg de kropsla en rucola toe. Dit is "
                "de koude, knapperige basis met een peppery accent van de rucola."
            ),
        ),
        Step(
            order=2, title="Komkommer & avocado (of ei)", phase="prep",
            duration_min_low=3, duration_min_high=3,
            instructions=(
                "Snijd de komkommer in halve plakjes. Voeg avocado in blokjes toe "
                "als die rijp is (de luxere keuze); anders partjes hardgekookt ei "
                "(de stabielere keuze) voor de romige component."
            ),
        ),
        Step(
            order=3, title="Mengen met slasaus", phase="finish",
            duration_min_low=1, duration_min_high=1,
            instructions=(
                "Meng de sla licht met de frisse slasaus — niet te veel, zodat de "
                "sla knapperig blijft."
            ),
        ),
        Step(
            order=4, title="Garneren", phase="finish",
            duration_min_low=2, duration_min_high=2,
            instructions=(
                "Verdeel de Hollandse garnalen erover voor de zilte smaak, rasp de "
                "Parmezaan erboven en strooi als laatste de croutons erop zodat ze "
                "knapperig blijven."
            ),
        ),
    ]
    return Recipe(
        id="salade-garnalen",
        title="Salade met garnalen",
        icon="🦐",
        description=(
            "Frisse, knapperige salade met Hollandse garnalen, avocado (of ei) en "
            "Parmezaan."
        ),
        servings=2,
        total_time_min_low=10,
        total_time_min_high=15,
        tags=["salade"],
        notes=(
            "Als avocado rijp is: gebruik avocado; anders ei. Ei is de stabielere "
            "keuze, avocado de luxere."
        ),
        ingredients=ingredients,
        steps=steps,
    )


def build_salade_kip_pesto() -> Recipe:
    """Return the Salade kip pesto recipe (2 personen)."""
    ingredients = [
        # Salade
        Ingredient(
            group="Salade", name="ijsbergsla", quantity=0.5, unit="krop",
            note="of kropsla",
        ),
        Ingredient(
            group="Salade", name="gerookte kipreepjes", quantity=200, unit="g",
            note="150–200 g",
        ),
        Ingredient(
            group="Salade", name="cherrytomaatjes", quantity=200, unit="g",
            note="150–200 g",
        ),
        Ingredient(
            group="Salade", name="komkommer", quantity=0.5, unit="stuk",
            note="half",
        ),
        Ingredient(group="Salade", name="croutons", quantity=75, unit="g"),
        Ingredient(
            group="Salade", name="Parmezaan", quantity=50, unit="g",
            note="40–50 g",
        ),
        Ingredient(
            group="Salade", name="ei", quantity=1, unit="stuk",
            note="optioneel",
        ),
        # Dressing
        Ingredient(
            group="Dressing", name="pesto", quantity=4, unit="el",
            note="begin met 3–4 el, proef; gebruik waarschijnlijk niet alles",
        ),
        Ingredient(group="Dressing", name="olijfolie", quantity=1, unit="el"),
        Ingredient(
            group="Dressing", name="citroensap", quantity=1, unit="el",
            note="eventueel 1½ el voor meer frisheid",
        ),
        Ingredient(group="Dressing", name="water", quantity=2, unit="el"),
        Ingredient(
            group="Dressing", name="zwarte peper", quantity=None, unit=None,
            note="naar smaak",
        ),
    ]
    steps = [
        Step(
            order=1, title="Ei koken (optioneel)", phase="cook",
            duration_min_low=7, duration_min_high=9,
            instructions=(
                "Kook het ei naar wens: 7 minuten voor zacht, 9 minuten voor hard. "
                "Laat afkoelen en snijd in partjes."
            ),
        ),
        Step(
            order=2, title="Groenten snijden", phase="prep",
            duration_min_low=5, duration_min_high=5,
            instructions=(
                "Was de sla en snijd grof, halveer de cherrytomaatjes en snijd de "
                "komkommer in halve plakjes."
            ),
        ),
        Step(
            order=3, title="Kip voorbereiden", phase="prep",
            duration_min_low=2, duration_min_high=2,
            instructions=(
                "Snijd de gerookte kip eventueel in kleinere stukken als de reepjes "
                "groot zijn. Bakken hoeft niet — gerookte kip is al gaar."
            ),
        ),
        Step(
            order=4, title="Dressing maken", phase="finish",
            duration_min_low=2, duration_min_high=2,
            instructions=(
                "Meng 3–4 el pesto met de olijfolie, citroensap, water en peper. "
                "Belangrijk: proef eerst — gerookte kip, Parmezaan en pesto zijn al "
                "hartig en zout. Omdat gerookte kip kouder en zouter is, werkt iets "
                "meer citroen (1½ el) vaak beter om de salade fris te houden."
            ),
        ),
        Step(
            order=5, title="Salade opbouwen", phase="finish",
            duration_min_low=3, duration_min_high=3,
            instructions=(
                "Doe in een grote kom de sla, tomaat, komkommer en kip en meng met "
                "de dressing. Verdeel daarna de croutons, Parmezaan en eventueel het "
                "ei erover."
            ),
        ),
    ]
    return Recipe(
        id="salade-kip-pesto",
        title="Salade kip pesto",
        icon="🥗",
        description=(
            "Snelle salade met gerookte kip en een frisse pestodressing — alleen "
            "snijden en mengen."
        ),
        servings=2,
        total_time_min_low=10,
        total_time_min_high=15,
        tags=["salade"],
        notes=(
            "Met gerookte kip hoef je niets te bakken. Proef de dressing eerst: "
            "kip, Parmezaan en pesto zijn al hartig."
        ),
        ingredients=ingredients,
        steps=steps,
    )


def build_dierbroodjes() -> Recipe:
    """Return the Zachte Dierbroodjes bake recipe (Japanse/Koreaanse stijl).

    A ``category="bake"`` recipe with a soft, enriched dough (broodmeel, ei,
    melk, boter) shaped into little animals and decorated. The steps preserve
    the full elaborate Dutch text — mixing, two kneading phases, chilling,
    portioning, shaping, a second proof (vingertest), decorating and baking to
    a 93–95 °C core — including the reasoning and notes verbatim. Ingredients
    are grouped Deeg / Decoratie / Glans.
    """
    ingredients = [
        # Deeg
        Ingredient(
            group="Deeg",
            name="broodmeel",
            quantity=310,
            unit="g",
            note="tarwebloem met hoog eiwitgehalte; volgende keer broodmeel",
        ),
        Ingredient(group="Deeg", name="suiker", quantity=28, unit="g"),
        Ingredient(group="Deeg", name="zout", quantity=3, unit="g"),
        Ingredient(
            group="Deeg", name="instant gist", quantity=3.5, unit="g"
        ),
        Ingredient(
            group="Deeg",
            name="ei",
            quantity=56,
            unit="g",
            note="losgeklopt, ongeveer 1 middelgroot ei",
        ),
        Ingredient(
            group="Deeg",
            name="melk",
            quantity=155,
            unit="g",
            note="lauwwarm",
        ),
        Ingredient(
            group="Deeg",
            name="ongezouten boter",
            quantity=31,
            unit="g",
            note="op kamertemperatuur, in blokjes",
        ),
        # Decoratie
        Ingredient(
            group="Decoratie",
            name="zwarte sesam",
            quantity=None,
            unit=None,
            note="voor oogjes",
        ),
        Ingredient(
            group="Decoratie",
            name="ham",
            quantity=None,
            unit=None,
            note="voor snuitjes/oortjes, optioneel",
        ),
        Ingredient(
            group="Decoratie",
            name="nori",
            quantity=None,
            unit=None,
            note="voor detail, optioneel",
        ),
        # Glans
        Ingredient(
            group="Glans",
            name="melk",
            quantity=None,
            unit=None,
            note="dun laagje, optioneel",
        ),
    ]

    steps = [
        Step(
            order=1,
            title="Droge en natte ingrediënten mengen",
            phase="prep",
            duration_min_low=5,
            duration_min_high=5,
            instructions=(
                "Doe het broodmeel, de suiker, het zout en de instant gist in "
                "een kom. Houd het zout en de gist bij het toevoegen even uit "
                "elkaar zodat het zout de gist niet direct remt. Voeg het "
                "losgeklopte ei en de lauwwarme melk toe en meng tot er geen "
                "droog meel meer zichtbaar is. Het deeg is in dit stadium nog "
                "plakkerig en ruw — dat hoort zo."
            ),
        ),
        Step(
            order=2,
            title="Eerste kneedfase",
            phase="prep",
            duration_min_low=8,
            duration_min_high=10,
            instructions=(
                "Kneed het deeg 8 tot 10 minuten (machine op stand 2 of met de "
                "hand) tot het samenkomt tot een gladdere, elastische bal. Het "
                "deeg moet zich van de rand van de kom losmaken maar mag onderin "
                "nog licht plakken. Nog niet perfect glad — de boter komt zo."
            ),
        ),
        Step(
            order=3,
            title="Boter toevoegen",
            phase="prep",
            duration_min_low=8,
            duration_min_high=10,
            instructions=(
                "Voeg de zachte boter beetje bij beetje toe, een paar blokjes "
                "tegelijk, en kneed steeds door tot de boter volledig is "
                "opgenomen voordat je meer toevoegt. Het deeg valt eerst weer "
                "uit elkaar en wordt vettig; blijf kneden tot het opnieuw "
                "samenkomt tot een soepel, glanzend geheel. Dit duurt nog eens "
                "8 tot 10 minuten."
            ),
        ),
        Step(
            order=4,
            title="Uitkneden tot vliesje",
            phase="prep",
            duration_min_low=3,
            duration_min_high=5,
            instructions=(
                "Kneed door tot het deeg het vliesstadium (windowpane) haalt: "
                "trek een stukje deeg voorzichtig uit; het moet zo dun rekken "
                "dat je er licht doorheen ziet zonder direct te scheuren. Dit "
                "geeft de karakteristieke pluizige, draderige structuur van "
                "zacht Japans/Koreaans brood."
            ),
        ),
        Step(
            order=5,
            title="Koelen in de vriezer",
            phase="cook",
            duration_min_low=30,
            duration_min_high=30,
            instructions=(
                "Leg het deeg ongeveer 30 minuten in de vriezer (of langer in "
                "de koelkast). Dit verstevigt de boter en het deeg, waardoor het "
                "straks veel makkelijker te vormen is en niet plakt. Het is geen "
                "volledige rijs — het gaat vooral om koelen en licht ontspannen "
                "van het deeg."
            ),
        ),
        Step(
            order=6,
            title="Verdelen in porties",
            phase="prep",
            duration_min_low=5,
            duration_min_high=5,
            instructions=(
                "Weeg het deeg en verdeel het in 8 gelijke stukken van ongeveer "
                "73 g. Werk elk stuk kort bol door de randen naar onderen te "
                "vouwen, zodat je een strak boloppervlak krijgt. Dek de bolletjes "
                "af met een vochtige doek zodat ze niet uitdrogen terwijl je "
                "vormt."
            ),
        ),
        Step(
            order=7,
            title="Dieren vormen",
            phase="prep",
            duration_min_low=15,
            duration_min_high=20,
            instructions=(
                "Vorm van elk bolletje een dier: knijp oortjes uit voor een "
                "beertje of konijn, rol dunne slierten voor staartjes of "
                "snuitjes, en gebruik kleine deegstukjes voor uitstekende "
                "details. Druk toevoegingen goed aan zodat ze tijdens het bakken "
                "niet loslaten. Werk rustig — een strak, glad oppervlak bakt het "
                "mooist op."
            ),
        ),
        Step(
            order=8,
            title="Tweede rijs (vingertest)",
            phase="cook",
            duration_min_low=60,
            duration_min_high=90,
            instructions=(
                "Laat de gevormde dieren afgedekt 60 tot 90 minuten rijzen op "
                "een warme, tochtvrije plek tot ze duidelijk zijn opgezwollen. "
                "Controleer met de vingertest: druk zachtjes met een licht "
                "bevochtigde vinger in het deeg. Veert het langzaam en niet "
                "helemaal terug (er blijft een kleine deuk staan), dan is het "
                "klaar. Veert het meteen volledig terug, laat dan nog even "
                "doorrijzen."
            ),
        ),
        Step(
            order=9,
            title="Decoreren en bestrijken",
            phase="finish",
            duration_min_low=5,
            duration_min_high=5,
            instructions=(
                "Bestrijk de broodjes desgewenst heel dun met melk of losgeklopt "
                "ei voor een zachte glans (te dik bestrijken maakt de details "
                "dof). Zet oogjes met zwarte sesam en gebruik stukjes ham of "
                "nori voor snuitjes, oortjes of andere details. Doe dit vlak voor "
                "het bakken zodat de decoraties op hun plek blijven."
            ),
        ),
        Step(
            order=10,
            title="Bakken",
            phase="cook",
            duration_min_low=20,
            duration_min_high=23,
            instructions=(
                "Bak de broodjes in een op 170 °C voorverwarmde oven 20 tot 23 "
                "minuten tot ze licht goudbruin zijn. Ze zijn gaar bij een "
                "kerntemperatuur van 93 tot 95 °C — meet met een "
                "kernthermometer voor zekerheid. Worden ze te snel donker, dek "
                "ze dan losjes af met folie."
            ),
        ),
        Step(
            order=11,
            title="Laten liggen en afkoelen",
            phase="finish",
            duration_min_low=25,
            duration_min_high=35,
            instructions=(
                "Laat de broodjes eerst 5 minuten in de vorm/op de plaat liggen "
                "en haal ze daarna voorzichtig over op een rooster. Laat ze nog "
                "20 tot 30 minuten volledig afkoelen. Snijd of trek ze niet "
                "direct open: het kruim moet nog nazetten, anders wordt het "
                "klef. Afgekoeld zijn ze pluizig en zacht."
            ),
        ),
    ]

    return Recipe(
        id="zachte-dierbroodjes",
        title="Zachte Dierbroodjes (Japanse/Koreaanse stijl)",
        icon="🍞",
        description=(
            "Zachte, pluizige verrijkte broodjes in dierenvorm — met ei, melk "
            "en boter voor een luchtige, draderige structuur."
        ),
        category="bake",
        servings=8,
        total_time_min_low=150,
        total_time_min_high=185,
        tags=["bake", "brood"],
        notes=(
            "Rijstijden zijn in de totale tijd meegerekend. Gebruik volgende "
            "keer broodmeel voor nog meer pluizigheid. Vertrouw op de "
            "vingertest voor de tweede rijs en op een kern van 93–95 °C voor "
            "gaarheid; snijd de broodjes niet direct na het bakken open."
        ),
        ingredients=ingredients,
        steps=steps,
    )


def seed_recipes() -> list[Recipe]:
    """Return every recipe that ships with the app."""
    return [
        build_seed_recipe(),
        build_spaghetti_bolognese(),
        build_salade_garnalen(),
        build_salade_kip_pesto(),
        build_dierbroodjes(),
    ]


async def seed_missing(repo: RecipeRepo) -> None:
    """Insert any shipped recipe that is not yet stored (idempotent).

    Seeds by id so newly added recipes appear on the next start even when the
    database already holds earlier ones.
    """
    for recipe in seed_recipes():
        if await repo.get(recipe.id) is None:
            await repo.create(recipe)


async def seed_pet_foods_missing(repo: PetFoodRepo) -> None:
    """Insert any starter pet food not already present (idempotent, by name).

    Seeds by normalized name so newly added starter foods appear on a later
    start even when the collection already holds earlier ones. Existing foods
    (and a user's own additions) are left untouched.
    """
    existing = {normalize_name(food.name) for food in await repo.list()}
    for food in PET_FOOD_SEED:
        if normalize_name(food.name) not in existing:
            await repo.create(food)


async def seed_staples_if_empty(repo: StapleRepo) -> None:
    """Insert the "heb ik vast wel" starter list once when it is empty.

    Idempotent: seeds only when no staples exist yet, so a user's edits to the
    list are never overwritten on a later start. The repo normalizes each name.
    """
    if await repo.count() > 0:
        return
    for name in STAPLE_SEED:
        await repo.create(Staple(id="", name=name))
