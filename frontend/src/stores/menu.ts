import { defineStore } from 'pinia'
import {
  getWeekMenu,
  listRecipes,
  getShoppingList,
  putAssignment,
  deleteAssignment,
  type Assignment,
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
  shoppingList: ShoppingItem[]
  loading: boolean
  lastSavedAt: string | null
}

export const useMenuStore = defineStore('menu', {
  state: (): MenuState => ({
    assignments: {},
    days: [],
    recipes: [],
    shoppingList: [],
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
        const [recipes, menu] = await Promise.all([listRecipes(), getWeekMenu()])
        this.recipes = recipes
        this.setDaysFromMenu(menu.days)
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

    async refreshShoppingList(): Promise<void> {
      const res = await getShoppingList()
      this.shoppingList = res.items
    },

    markSaved(): void {
      this.lastSavedAt = new Date().toISOString()
    },
  },
})
