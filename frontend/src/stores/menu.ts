import { defineStore } from 'pinia'
import {
  getWeekMenu,
  listRecipes,
  getShoppingList,
  putAssignment,
  deleteAssignment,
  setItemBuy,
  putExtra,
  deleteExtra,
  listPetFoods,
  addPetFood,
  deletePetFood,
  getPet,
  setPetTarget,
  regeneratePet,
  replacePetFood,
  type Assignment,
  type Extra,
  type PetFood,
  type RecipeCard,
  type ShoppingItem,
  type WeekMenuDay,
} from '../api/client'

interface MenuState {
  // date (YYYY-MM-DD) -> assignment; absence means the day is empty.
  assignments: Record<string, Assignment>
  // ordered 14-day window from the backend.
  days: string[]
  recipes: RecipeCard[]
  // Recipes in the bag without a date (Extra's zone).
  extras: Extra[]
  shoppingList: ShoppingItem[]
  // "Heb ik vast wel" staples not yet promoted into the shopping list.
  pantry: ShoppingItem[]
  // Weekly pet-food weight target in grams.
  petTarget: number
  // Currently chosen pet foods.
  petSelection: PetFood[]
  // Editable master list of pet foods.
  petFoods: PetFood[]
  loading: boolean
  lastSavedAt: string | null
}

export const useMenuStore = defineStore('menu', {
  state: (): MenuState => ({
    assignments: {},
    days: [],
    recipes: [],
    extras: [],
    shoppingList: [],
    pantry: [],
    petTarget: 1000,
    petSelection: [],
    petFoods: [],
    loading: false,
    lastSavedAt: null,
  }),

  getters: {
    recipeById: (state) => {
      return (id: string): RecipeCard | undefined =>
        state.recipes.find((r) => r.id === id)
    },
  },

  actions: {
    // Load everything needed for the calendar in one pass.
    async loadAll(): Promise<void> {
      this.loading = true
      try {
        const [recipes, menu, pet, petFoods] = await Promise.all([
          listRecipes(),
          getWeekMenu(),
          getPet(),
          listPetFoods(),
        ])
        this.recipes = recipes
        this.setDaysFromMenu(menu.days)
        this.extras = menu.extras ?? []
        this.petTarget = pet.targetG
        this.petSelection = pet.selection
        this.petFoods = petFoods
        await this.refreshShoppingList()
      } finally {
        this.loading = false
      }
    },

    setDaysFromMenu(days: WeekMenuDay[]): void {
      this.days = days.map((d) => d.date)
      const next: Record<string, Assignment> = {}
      for (const day of days) {
        if (day.assignment) {
          next[day.date] = { ...day.assignment }
        }
      }
      this.assignments = next
    },

    // Assign a recipe to a (possibly occupied) day — overwrites optimistically.
    async assign(date: string, recipeId: string, multiplier: number): Promise<void> {
      this.assignments[date] = { recipeId, multiplier }
      await putAssignment({ date, recipeId, multiplier })
      await this.refreshShoppingList()
    },

    // Move a recipe from one day to another. Mirrors backend semantics:
    //   - empty target  -> move (source cleared)
    //   - occupied target -> swap
    async moveOrSwap(fromDate: string, toDate: string): Promise<void> {
      if (fromDate === toDate) {
        return
      }
      const source = this.assignments[fromDate]
      if (!source) {
        return
      }
      const target = this.assignments[toDate]

      // Optimistic local resolution.
      this.assignments[toDate] = { ...source }
      if (target) {
        this.assignments[fromDate] = { ...target }
      } else {
        delete this.assignments[fromDate]
      }

      await putAssignment({
        date: toDate,
        recipeId: source.recipeId,
        multiplier: source.multiplier,
        fromDate,
      })
      await this.refreshShoppingList()
    },

    // Change the portion multiplier for an occupied day.
    async setMultiplier(date: string, multiplier: number): Promise<void> {
      const current = this.assignments[date]
      if (!current) {
        return
      }
      this.assignments[date] = { ...current, multiplier }
      await putAssignment({ date, recipeId: current.recipeId, multiplier })
      await this.refreshShoppingList()
    },

    // Clear a day.
    async removeDay(date: string): Promise<void> {
      if (!this.assignments[date]) {
        return
      }
      delete this.assignments[date]
      await deleteAssignment(date)
      await this.refreshShoppingList()
    },

    // --- Extra's (dateless recipes) -------------------------------------

    // Append or update an extra, then refresh the bag.
    async addExtra(recipeId: string, multiplier: number): Promise<void> {
      const menu = await putExtra(recipeId, multiplier)
      this.extras = menu.extras ?? []
      await this.refreshShoppingList()
    },

    // Change an extra's portion multiplier.
    async setExtraMultiplier(recipeId: string, multiplier: number): Promise<void> {
      const menu = await putExtra(recipeId, multiplier)
      this.extras = menu.extras ?? []
      await this.refreshShoppingList()
    },

    // Remove an extra from the bag.
    async removeExtra(recipeId: string): Promise<void> {
      const menu = await deleteExtra(recipeId)
      this.extras = menu.extras ?? []
      await this.refreshShoppingList()
    },

    // --- Pet food -------------------------------------------------------

    // Load the current pet target + selection (no bag refresh needed).
    async loadPet(): Promise<void> {
      const pet = await getPet()
      this.petTarget = pet.targetG
      this.petSelection = pet.selection
    },

    // Rebuild the pet selection from scratch and refresh the bag.
    async regeneratePet(): Promise<void> {
      const pet = await regeneratePet()
      this.petTarget = pet.targetG
      this.petSelection = pet.selection
      await this.refreshShoppingList()
    },

    // Adjust the weekly weight target (grams); re-selects and refreshes.
    async setPetTarget(targetG: number): Promise<void> {
      const pet = await setPetTarget(targetG)
      this.petTarget = pet.targetG
      this.petSelection = pet.selection
      await this.refreshShoppingList()
    },

    // Swap one selected food for a random unselected one.
    async replacePetFood(name: string): Promise<void> {
      const pet = await replacePetFood(name)
      this.petTarget = pet.targetG
      this.petSelection = pet.selection
      await this.refreshShoppingList()
    },

    // Load the editable master pet-food list.
    async loadPetFoods(): Promise<void> {
      this.petFoods = await listPetFoods()
    },

    // Add a food to the master list, then reload it.
    async addPetFood(name: string, weightG: number): Promise<void> {
      await addPetFood(name, weightG)
      this.petFoods = await listPetFoods()
    },

    // Remove a food from the master list (API returns the updated list).
    async deletePetFood(id: string): Promise<void> {
      this.petFoods = await deletePetFood(id)
    },

    async refreshShoppingList(): Promise<void> {
      const res = await getShoppingList()
      this.shoppingList = res.items
      this.pantry = res.pantry ?? []
    },

    // Move an ingredient between the shopping list (buy=true) and the
    // "heb ik vast wel" list (buy=false).
    async setItemBuy(name: string, buy: boolean): Promise<void> {
      const res = await setItemBuy(name, buy)
      this.shoppingList = res.items
      this.pantry = res.pantry ?? []
    },

    markSaved(): void {
      this.lastSavedAt = new Date().toISOString()
    },
  },
})
