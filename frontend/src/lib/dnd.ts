// Shared drag-and-drop constants and helpers for the calendar.
//
// Native HTML5 DnD rejects a drop (and never fires the `drop` event) when the
// drop target's `dropEffect` is incompatible with the dragged source's
// `effectAllowed`. Library recipe cards drag with `effectAllowed="copy"` while
// cell-to-cell moves use `effectAllowed="move"`, so the day cell must pick a
// matching `dropEffect` per drag — decided here from the dataTransfer types.

export const RECIPE_MIME = 'application/x-basket-recipe'
export const FROMDATE_MIME = 'application/x-basket-fromdate'

/**
 * Return the `dropEffect` a day cell should advertise for the current drag,
 * based on the dataTransfer types present. A cell-to-cell drag (carrying a
 * source date) is a move; anything else (a library recipe) is a copy.
 */
export function dropEffectForTypes(
  types: readonly string[],
): 'copy' | 'move' {
  return types.includes(FROMDATE_MIME) ? 'move' : 'copy'
}
