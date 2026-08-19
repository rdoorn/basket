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
    putExtra: vi.fn(),
    deleteExtra: vi.fn(),
    listPetFoods: vi.fn(),
    addPetFood: vi.fn(),
    deletePetFood: vi.fn(),
    getPet: vi.fn(),
    setPetTarget: vi.fn(),
    regeneratePet: vi.fn(),
    replacePetFood: vi.fn(),
    listStaples: vi.fn(),
    addStaple: vi.fn(),
    deleteStaple: vi.fn(),
  }
})

const mocked = client as unknown as {
  getWeekMenu: ReturnType<typeof vi.fn>
  listRecipes: ReturnType<typeof vi.fn>
  getShoppingList: ReturnType<typeof vi.fn>
  putAssignment: ReturnType<typeof vi.fn>
  deleteAssignment: ReturnType<typeof vi.fn>
  setItemBuy: ReturnType<typeof vi.fn>
  putExtra: ReturnType<typeof vi.fn>
  deleteExtra: ReturnType<typeof vi.fn>
  listPetFoods: ReturnType<typeof vi.fn>
  addPetFood: ReturnType<typeof vi.fn>
  deletePetFood: ReturnType<typeof vi.fn>
  getPet: ReturnType<typeof vi.fn>
  setPetTarget: ReturnType<typeof vi.fn>
  regeneratePet: ReturnType<typeof vi.fn>
  replacePetFood: ReturnType<typeof vi.fn>
  listStaples: ReturnType<typeof vi.fn>
  addStaple: ReturnType<typeof vi.fn>
  deleteStaple: ReturnType<typeof vi.fn>
}

describe('menu store — optimistic move/swap/multiplier', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    // API calls resolve but never drive state in these tests (optimistic-first).
    mocked.putAssignment.mockResolvedValue({ assignments: {} })
    mocked.deleteAssignment.mockResolvedValue({ assignments: {} })
    mocked.getShoppingList.mockResolvedValue({ items: [], pantry: [] })
    // Bag-changing pet/extra calls resolve; specific tests override as needed.
    mocked.putExtra.mockResolvedValue({ days: [], extras: [] })
    mocked.deleteExtra.mockResolvedValue({ days: [], extras: [] })
    mocked.listPetFoods.mockResolvedValue([])
    mocked.addPetFood.mockResolvedValue({ id: 'x', name: 'x', weightG: 0 })
    mocked.deletePetFood.mockResolvedValue([])
    mocked.getPet.mockResolvedValue({ targetG: 1000, selection: [], coveredG: 0 })
    mocked.setPetTarget.mockResolvedValue({ targetG: 1000, selection: [], coveredG: 0 })
    mocked.regeneratePet.mockResolvedValue({ targetG: 1000, selection: [], coveredG: 0 })
    mocked.replacePetFood.mockResolvedValue({ targetG: 1000, selection: [], coveredG: 0 })
    mocked.listStaples.mockResolvedValue([])
    mocked.addStaple.mockResolvedValue({ id: 's1', name: 'suiker' })
    mocked.deleteStaple.mockResolvedValue([])
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
    store.pantry = [
      { name: 'gehakt', quantity: 300, unit: 'g', source: 'supermarket', staple: true, group: null },
    ]
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
      extras: [{ recipeId: 'B', multiplier: 2 }],
    })
    mocked.getShoppingList.mockResolvedValue({ items: [] })
    mocked.getPet.mockResolvedValue({
      targetG: 1500,
      selection: [{ id: 'p1', name: 'wortel', weightG: 80 }],
      coveredG: 120,
    })
    mocked.listPetFoods.mockResolvedValue([{ id: 'p1', name: 'wortel', weightG: 80 }])
    mocked.listStaples.mockResolvedValue([{ id: 's1', name: 'suiker' }])
    const store = useMenuStore()
    await store.loadAll()
    expect(store.recipes).toHaveLength(1)
    expect(store.days).toHaveLength(2)
    expect(store.assignments['2026-08-17']).toEqual({ recipeId: 'A', multiplier: 1 })
    expect(store.assignments['2026-08-18']).toBeUndefined()
    expect(store.extras).toEqual([{ recipeId: 'B', multiplier: 2 }])
    expect(store.petTarget).toBe(1500)
    expect(store.petSelection).toEqual([{ id: 'p1', name: 'wortel', weightG: 80 }])
    expect(store.petFoods).toEqual([{ id: 'p1', name: 'wortel', weightG: 80 }])
    expect(store.petCovered).toBe(120)
    expect(store.staples).toEqual([{ id: 's1', name: 'suiker' }])
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

describe('menu store — extras', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    mocked.getShoppingList.mockResolvedValue({ items: [], pantry: [] })
  })

  it('addExtra() sets extras from the API response and refreshes the bag', async () => {
    mocked.putExtra.mockResolvedValue({
      days: [],
      extras: [{ recipeId: 'bread', multiplier: 1 }],
    })
    const store = useMenuStore()
    await store.addExtra('bread', 1)
    expect(mocked.putExtra).toHaveBeenCalledWith('bread', 1)
    expect(store.extras).toEqual([{ recipeId: 'bread', multiplier: 1 }])
    expect(mocked.getShoppingList).toHaveBeenCalled()
  })

  it('setExtraMultiplier() updates the extra via putExtra', async () => {
    mocked.putExtra.mockResolvedValue({
      days: [],
      extras: [{ recipeId: 'bread', multiplier: 2 }],
    })
    const store = useMenuStore()
    store.extras = [{ recipeId: 'bread', multiplier: 1 }]
    await store.setExtraMultiplier('bread', 2)
    expect(mocked.putExtra).toHaveBeenCalledWith('bread', 2)
    expect(store.extras).toEqual([{ recipeId: 'bread', multiplier: 2 }])
  })

  it('removeExtra() clears the extra from the API response', async () => {
    mocked.deleteExtra.mockResolvedValue({ days: [], extras: [] })
    const store = useMenuStore()
    store.extras = [{ recipeId: 'bread', multiplier: 1 }]
    await store.removeExtra('bread')
    expect(mocked.deleteExtra).toHaveBeenCalledWith('bread')
    expect(store.extras).toEqual([])
    expect(mocked.getShoppingList).toHaveBeenCalled()
  })
})

describe('menu store — pet', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    mocked.getShoppingList.mockResolvedValue({ items: [], pantry: [] })
  })

  it('loadPet() fills target, selection and coverage', async () => {
    mocked.getPet.mockResolvedValue({
      targetG: 1250,
      selection: [{ id: 'p1', name: 'paprika', weightG: 150 }],
      coveredG: 200,
    })
    const store = useMenuStore()
    await store.loadPet()
    expect(store.petTarget).toBe(1250)
    expect(store.petSelection).toEqual([{ id: 'p1', name: 'paprika', weightG: 150 }])
    expect(store.petCovered).toBe(200)
  })

  it('regeneratePet() updates target + selection + coverage and refreshes the bag', async () => {
    mocked.regeneratePet.mockResolvedValue({
      targetG: 1000,
      selection: [{ id: 'p2', name: 'komkommer', weightG: 400 }],
      coveredG: 150,
    })
    const store = useMenuStore()
    await store.regeneratePet()
    expect(mocked.regeneratePet).toHaveBeenCalled()
    expect(store.petTarget).toBe(1000)
    expect(store.petSelection).toEqual([{ id: 'p2', name: 'komkommer', weightG: 400 }])
    expect(store.petCovered).toBe(150)
    expect(mocked.getShoppingList).toHaveBeenCalled()
  })

  it('setPetTarget() updates target + selection', async () => {
    mocked.setPetTarget.mockResolvedValue({
      targetG: 1500,
      selection: [{ id: 'p3', name: 'wortel', weightG: 80 }],
    })
    const store = useMenuStore()
    await store.setPetTarget(1500)
    expect(mocked.setPetTarget).toHaveBeenCalledWith(1500)
    expect(store.petTarget).toBe(1500)
    expect(store.petSelection).toEqual([{ id: 'p3', name: 'wortel', weightG: 80 }])
    expect(mocked.getShoppingList).toHaveBeenCalled()
  })

  it('replacePetFood() swaps and updates the selection', async () => {
    mocked.replacePetFood.mockResolvedValue({
      targetG: 1000,
      selection: [{ id: 'p4', name: 'andijvie', weightG: 300 }],
    })
    const store = useMenuStore()
    await store.replacePetFood('paprika')
    expect(mocked.replacePetFood).toHaveBeenCalledWith('paprika')
    expect(store.petSelection).toEqual([{ id: 'p4', name: 'andijvie', weightG: 300 }])
    expect(mocked.getShoppingList).toHaveBeenCalled()
  })

  it('loadPetFoods() fills the editable food list', async () => {
    mocked.listPetFoods.mockResolvedValue([{ id: 'p1', name: 'paprika', weightG: 150 }])
    const store = useMenuStore()
    await store.loadPetFoods()
    expect(store.petFoods).toEqual([{ id: 'p1', name: 'paprika', weightG: 150 }])
  })

  it('addPetFood() appends via the API then reloads the list', async () => {
    mocked.addPetFood.mockResolvedValue({ id: 'p9', name: 'sla', weightG: 400 })
    mocked.listPetFoods.mockResolvedValue([{ id: 'p9', name: 'sla', weightG: 400 }])
    const store = useMenuStore()
    await store.addPetFood('sla', 400)
    expect(mocked.addPetFood).toHaveBeenCalledWith('sla', 400)
    expect(store.petFoods).toEqual([{ id: 'p9', name: 'sla', weightG: 400 }])
  })

  it('deletePetFood() updates the list from the API response', async () => {
    mocked.deletePetFood.mockResolvedValue([{ id: 'p1', name: 'paprika', weightG: 150 }])
    const store = useMenuStore()
    store.petFoods = [
      { id: 'p1', name: 'paprika', weightG: 150 },
      { id: 'p2', name: 'sla', weightG: 400 },
    ]
    await store.deletePetFood('p2')
    expect(mocked.deletePetFood).toHaveBeenCalledWith('p2')
    expect(store.petFoods).toEqual([{ id: 'p1', name: 'paprika', weightG: 150 }])
  })
})

describe('menu store — staples', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('loadStaples() fills the staples list', async () => {
    mocked.listStaples.mockResolvedValue([
      { id: 's1', name: 'suiker' },
      { id: 's2', name: 'zout' },
    ])
    const store = useMenuStore()
    await store.loadStaples()
    expect(mocked.listStaples).toHaveBeenCalled()
    expect(store.staples).toEqual([
      { id: 's1', name: 'suiker' },
      { id: 's2', name: 'zout' },
    ])
  })

  it('addStaple() creates via the API then reloads the list', async () => {
    mocked.addStaple.mockResolvedValue({ id: 's3', name: 'kaneel' })
    mocked.listStaples.mockResolvedValue([{ id: 's3', name: 'kaneel' }])
    const store = useMenuStore()
    await store.addStaple('Kaneel')
    expect(mocked.addStaple).toHaveBeenCalledWith('Kaneel')
    expect(store.staples).toEqual([{ id: 's3', name: 'kaneel' }])
  })

  it('deleteStaple() updates the list from the API response', async () => {
    mocked.deleteStaple.mockResolvedValue([{ id: 's1', name: 'suiker' }])
    const store = useMenuStore()
    store.staples = [
      { id: 's1', name: 'suiker' },
      { id: 's2', name: 'zout' },
    ]
    await store.deleteStaple('s2')
    expect(mocked.deleteStaple).toHaveBeenCalledWith('s2')
    expect(store.staples).toEqual([{ id: 's1', name: 'suiker' }])
  })
})
