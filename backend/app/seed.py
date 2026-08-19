"""Seed data: Recipe 1 — Macaroni alla Siciliana.

Transcribes Recipe 1 faithfully into a :class:`Recipe`, preserving the
elaborate Dutch instructions (including per-step reasoning) verbatim. Also
provides :func:`seed_if_empty` to insert it once when the recipe collection is
empty (idempotent).
"""
from app.domain.recipe import Ingredient, Recipe, Step
from app.ports.recipe_repo import RecipeRepo

SEED_RECIPE_ID = "macaroni-alla-siciliana"


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


def seed_recipes() -> list[Recipe]:
    """Return every recipe that ships with the app."""
    return [
        build_seed_recipe(),
        build_spaghetti_bolognese(),
        build_salade_garnalen(),
        build_salade_kip_pesto(),
    ]


async def seed_missing(repo: RecipeRepo) -> None:
    """Insert any shipped recipe that is not yet stored (idempotent).

    Seeds by id so newly added recipes appear on the next start even when the
    database already holds earlier ones.
    """
    for recipe in seed_recipes():
        if await repo.get(recipe.id) is None:
            await repo.create(recipe)
