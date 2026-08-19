import { beforeEach, describe, expect, it, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useMenuStore } from '../src/stores/menu'
import * as client from '../src/api/client'

// Mock the entire API client module so no network is involved.
vi.mock('../src/api/client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../src/api/client')>()
  return {
    ...actual,
    getWeekMenu: vi.fn(),
    listRecipes: vi.fn(),
    getShoppingList: vi.fn(),
    putAssignment: vi.fn(),
    deleteAssignment: vi.fn(),
    setItemBuy: vi.fn(),
  }
})

const mocked = client as unknown as {
  getWeekMenu: ReturnType<typeof vi.fn>
  listRecipes: ReturnType<typeof vi.fn>
  getShoppingList: ReturnType<typeof vi.fn>
  putAssignment: ReturnType<typeof vi.fn>
  deleteAssignment: ReturnType<typeof vi.fn>
  setItemBuy: ReturnType<typeof vi.fn>
}

describe('menu store — optimistic move/swap/multiplier', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    // API calls resolve but never drive state in these tests (optimistic-first).
    mocked.putAssignment.mockResolvedValue({ assignments: {} })
    mocked.deleteAssignment.mockResolvedValue({ assignments: {} })
    mocked.getShoppingList.mockResolvedValue({ items: [], pantry: [] })
  })

  it('assign() sets an assignment on a day', async () => {
    const store = useMenuStore()
    await store.assign('2026-08-17', 'A', 1)
    expect(store.assignments['2026-08-17']).toEqual({ recipeId: 'A', multiplier: 1 })
    expect(mocked.putAssignment).toHaveBeenCalledWith({
      date: '2026-08-17',
      recipeId: 'A',
      multiplier: 1,
    })
  })

  it('moveOrSwap() moves to an empty day and clears the source', async () => {
    const store = useMenuStore()
    store.assignments['d1'] = { recipeId: 'A', multiplier: 1 }
    await store.moveOrSwap('d1', 'd2')
    expect(store.assignments['d2']).toEqual({ recipeId: 'A', multiplier: 1 })
    expect(store.assignments['d1']).toBeUndefined()
  })

  it('moveOrSwap() swaps when the target day is occupied', async () => {
    const store = useMenuStore()
    store.assignments['d1'] = { recipeId: 'A', multiplier: 1 }
    store.assignments['d2'] = { recipeId: 'B', multiplier: 2 }
    await store.moveOrSwap('d1', 'd2')
    expect(store.assignments['d2']).toEqual({ recipeId: 'A', multiplier: 1 })
    expect(store.assignments['d1']).toEqual({ recipeId: 'B', multiplier: 2 })
  })

  it('moveOrSwap() is a no-op when source and target are the same', async () => {
    const store = useMenuStore()
    store.assignments['d1'] = { recipeId: 'A', multiplier: 1 }
    await store.moveOrSwap('d1', 'd1')
    expect(store.assignments['d1']).toEqual({ recipeId: 'A', multiplier: 1 })
  })

  it('moveOrSwap() does nothing when the source is empty', async () => {
    const store = useMenuStore()
    await store.moveOrSwap('d1', 'd2')
    expect(store.assignments['d1']).toBeUndefined()
    expect(store.assignments['d2']).toBeUndefined()
    expect(mocked.putAssignment).not.toHaveBeenCalled()
  })

  it('moveOrSwap() sends the move with fromDate to the API', async () => {
    const store = useMenuStore()
    store.assignments['d1'] = { recipeId: 'A', multiplier: 1 }
    await store.moveOrSwap('d1', 'd2')
    expect(mocked.putAssignment).toHaveBeenCalledWith({
      date: 'd2',
      recipeId: 'A',
      multiplier: 1,
      fromDate: 'd1',
    })
  })

  it('setMultiplier() updates the multiplier for an occupied day', async () => {
    const store = useMenuStore()
    store.assignments['d1'] = { recipeId: 'A', multiplier: 1 }
    await store.setMultiplier('d1', 2)
    expect(store.assignments['d1']).toEqual({ recipeId: 'A', multiplier: 2 })
    expect(mocked.putAssignment).toHaveBeenCalledWith({
      date: 'd1',
      recipeId: 'A',
      multiplier: 2,
    })
  })

  it('setMultiplier() ignores empty days', async () => {
    const store = useMenuStore()
    await store.setMultiplier('d1', 2)
    expect(store.assignments['d1']).toBeUndefined()
    expect(mocked.putAssignment).not.toHaveBeenCalled()
  })

  it('removeDay() clears an assignment and calls the API', async () => {
    const store = useMenuStore()
    store.assignments['d1'] = { recipeId: 'A', multiplier: 1 }
    await store.removeDay('d1')
    expect(store.assignments['d1']).toBeUndefined()
    expect(mocked.deleteAssignment).toHaveBeenCalledWith('d1')
  })

  it('refreshShoppingList() populates the shopping list and pantry from the API', async () => {
    mocked.getShoppingList.mockResolvedValue({
      items: [{ name: 'macaroni', quantity: 700, unit: 'g', source: 'supermarket', staple: false }],
      pantry: [{ name: 'gehakt', quantity: 300, unit: 'g', source: 'supermarket', staple: true }],
    })
    const store = useMenuStore()
    await store.refreshShoppingList()
    expect(store.shoppingList).toHaveLength(1)
    expect(store.shoppingList[0].name).toBe('macaroni')
    expect(store.pantry).toHaveLength(1)
    expect(store.pantry[0].name).toBe('gehakt')
  })

  it('setItemBuy() moves an item and updates items + pantry from the API', async () => {
    mocked.setItemBuy.mockResolvedValue({
      items: [{ name: 'gehakt', quantity: 300, unit: 'g', source: 'supermarket', staple: true }],
      pantry: [],
    })
    const store = useMenuStore()
    store.pantry = [{ name: 'gehakt', quantity: 300, unit: 'g', source: 'supermarket', staple: true }]
    await store.setItemBuy('gehakt', true)
    expect(mocked.setItemBuy).toHaveBeenCalledWith('gehakt', true)
    expect(store.shoppingList.map((i) => i.name)).toContain('gehakt')
    expect(store.pantry).toHaveLength(0)
  })

  it('loadAll() fills recipes, assignments and shopping list', async () => {
    mocked.listRecipes.mockResolvedValue([
      { id: 'A', title: 'Macaroni', icon: '🍝', description: '' },
    ])
    mocked.getWeekMenu.mockResolvedValue({
      days: [
        { date: '2026-08-17', assignment: { recipeId: 'A', multiplier: 1 } },
        { date: '2026-08-18', assignment: null },
      ],
    })
    mocked.getShoppingList.mockResolvedValue({ items: [] })
    const store = useMenuStore()
    await store.loadAll()
    expect(store.recipes).toHaveLength(1)
    expect(store.days).toHaveLength(2)
    expect(store.assignments['2026-08-17']).toEqual({ recipeId: 'A', multiplier: 1 })
    expect(store.assignments['2026-08-18']).toBeUndefined()
  })

  it('recipeById getter resolves a recipe card by id', async () => {
    mocked.listRecipes.mockResolvedValue([
      { id: 'A', title: 'Macaroni', icon: '🍝', description: '' },
    ])
    mocked.getWeekMenu.mockResolvedValue({ days: [] })
    mocked.getShoppingList.mockResolvedValue({ items: [] })
    const store = useMenuStore()
    await store.loadAll()
    expect(store.recipeById('A')?.title).toBe('Macaroni')
    expect(store.recipeById('missing')).toBeUndefined()
  })
})
