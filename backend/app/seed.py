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


async def seed_if_empty(repo: RecipeRepo) -> None:
    """Insert the seed recipe when ``repo`` holds no recipes (idempotent)."""
    if await repo.count() == 0:
        await repo.create(build_seed_recipe())
