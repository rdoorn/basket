"""Menu service: assign a recipe to a day and resolve move/swap drags.

Pure functions mutating a :class:`~app.domain.menu.WeekMenu` in place. No I/O.
"""
from app.domain.menu import DayAssignment, WeekMenu


def assign(
    menu: WeekMenu,
    date: str,
    recipe_id: str,
    multiplier: float = 1.0,
) -> None:
    """Assign ``recipe_id`` to ``date``, replacing any existing assignment.

    Models the recipe-library-onto-a-day drop.
    """
    menu.set(date, DayAssignment(recipe_id=recipe_id, multiplier=multiplier))


def move_or_swap(menu: WeekMenu, src: str, dst: str) -> None:
    """Move the assignment at ``src`` to ``dst``, swapping if ``dst`` is taken.

    - If ``src`` is empty, nothing happens.
    - If ``src == dst``, nothing happens.
    - If ``dst`` is occupied, the two assignments are swapped.
    - Otherwise the assignment moves and ``src`` is cleared.
    """
    if src == dst:
        return

    src_assignment = menu.get(src)
    if src_assignment is None:
        return

    dst_assignment = menu.get(dst)
    if dst_assignment is None:
        menu.remove(src)
    else:
        menu.set(src, dst_assignment)
    menu.set(dst, src_assignment)
