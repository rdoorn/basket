import { describe, expect, it } from 'vitest'
import {
  FROMDATE_MIME,
  RECIPE_MIME,
  dropEffectForTypes,
} from '../src/lib/dnd'

describe('dropEffectForTypes', () => {
  it('returns "copy" for a library recipe drag (matches RecipeCard effectAllowed)', () => {
    // A recipe card is dragged with effectAllowed="copy"; the drop target must
    // answer with a compatible dropEffect or the browser rejects the drop.
    expect(dropEffectForTypes([RECIPE_MIME])).toBe('copy')
  })

  it('returns "move" for a cell-to-cell drag', () => {
    expect(dropEffectForTypes([FROMDATE_MIME])).toBe('move')
  })

  it('prefers "move" when a cell drag also carries a recipe type', () => {
    expect(dropEffectForTypes([RECIPE_MIME, FROMDATE_MIME])).toBe('move')
  })

  it('defaults to "copy" when no known type is present', () => {
    expect(dropEffectForTypes([])).toBe('copy')
  })
})
