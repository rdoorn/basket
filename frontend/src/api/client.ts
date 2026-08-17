// Typed fetch wrappers for the Basket backend API.
// Base URL comes from the Vite env var injected at build/runtime.

const API_BASE: string = import.meta.env.VITE_API_BASE ?? 'http://localhost:18420'

// ---------------------------------------------------------------------------
// Domain types (mirror the backend contract).
// ---------------------------------------------------------------------------

export interface Ingredient {
  group: string | null
  name: string
  quantity: number | null
  unit: string | null
  note: string | null
  normalized_name: string | null
  brand_override: string | null
  source: string
}

export type StepPhase = 'prep' | 'cook' | 'finish'

export interface Step {
  order: number
  title: string
  phase: StepPhase
  duration_min_low: number | null
  duration_min_high: number | null
  instructions: string
}

export interface Recipe {
  id: string
  title: string
  icon: string
  description: string
  servings: number
  total_time_min_low: number | null
  total_time_min_high: number | null
  tags: string[]
  notes: string | null
  ingredients: Ingredient[]
  steps: Step[]
}

// A recipe payload for create/update (server assigns id on create).
export type RecipeInput = Omit<Recipe, 'id'> & { id?: string }

// Card data returned by the list endpoint.
export interface RecipeCard {
  id: string
  title: string
  icon: string
  description: string
}

export interface Assignment {
  recipeId: string
  multiplier: number
}

export interface WeekMenuDay {
  date: string
  assignment: Assignment | null
}

export interface WeekMenu {
  days: WeekMenuDay[]
}

export interface AssignmentsResponse {
  assignments: Record<string, Assignment>
}

export interface AssignmentUpdate {
  date: string
  recipeId: string
  multiplier: number
  fromDate?: string
}

export interface ShoppingItem {
  name: string
  quantity: number | null
  unit: string | null
  source: string
  staple: boolean
}

export interface ShoppingListResponse {
  // Lines to order (non-staples plus promoted staples).
  items: ShoppingItem[]
  // "Heb ik vast wel" staples the user probably has on hand.
  pantry: ShoppingItem[]
}

export interface PricedItem {
  name: string
  quantity: number | null
  unit: string | null
  unit_price: number
  line_total: number
}

export interface StoreQuote {
  store: string
  total: number
  items: PricedItem[]
}

export interface QuoteResponse {
  quotes: StoreQuote[]
}

// ---------------------------------------------------------------------------
// HTTP helper.
// ---------------------------------------------------------------------------

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const body = await res.text().catch(() => '')
    throw new Error(`API ${init?.method ?? 'GET'} ${path} failed: ${res.status} ${body}`)
  }
  if (res.status === 204) {
    return undefined as T
  }
  return (await res.json()) as T
}

// ---------------------------------------------------------------------------
// Recipe endpoints.
// ---------------------------------------------------------------------------

export function listRecipes(): Promise<RecipeCard[]> {
  return request<RecipeCard[]>('/recipes')
}

export function getRecipe(id: string): Promise<Recipe> {
  return request<Recipe>(`/recipes/${id}`)
}

export function createRecipe(recipe: RecipeInput): Promise<Recipe> {
  return request<Recipe>('/recipes', {
    method: 'POST',
    body: JSON.stringify(recipe),
  })
}

export function updateRecipe(id: string, recipe: RecipeInput): Promise<Recipe> {
  return request<Recipe>(`/recipes/${id}`, {
    method: 'PUT',
    body: JSON.stringify(recipe),
  })
}

export function deleteRecipe(id: string): Promise<void> {
  return request<void>(`/recipes/${id}`, { method: 'DELETE' })
}

// ---------------------------------------------------------------------------
// Weekmenu endpoints.
// ---------------------------------------------------------------------------

export function getWeekMenu(): Promise<WeekMenu> {
  return request<WeekMenu>('/weekmenu')
}

export function putAssignment(update: AssignmentUpdate): Promise<AssignmentsResponse> {
  return request<AssignmentsResponse>('/weekmenu/assignments', {
    method: 'PUT',
    body: JSON.stringify(update),
  })
}

export function deleteAssignment(date: string): Promise<AssignmentsResponse> {
  return request<AssignmentsResponse>(`/weekmenu/assignments/${date}`, {
    method: 'DELETE',
  })
}

// ---------------------------------------------------------------------------
// Shopping list + pricing.
// ---------------------------------------------------------------------------

export function getShoppingList(): Promise<ShoppingListResponse> {
  return request<ShoppingListResponse>('/shopping-list')
}

// Promote (buy=true) or un-promote a "heb ik vast wel" staple.
export function setStaple(name: string, buy: boolean): Promise<ShoppingListResponse> {
  return request<ShoppingListResponse>('/shopping-list/staple', {
    method: 'PUT',
    body: JSON.stringify({ name, buy }),
  })
}

export function quotePricing(): Promise<QuoteResponse> {
  return request<QuoteResponse>('/pricing/quote', { method: 'POST', body: '{}' })
}

export const api = {
  listRecipes,
  getRecipe,
  createRecipe,
  updateRecipe,
  deleteRecipe,
  getWeekMenu,
  putAssignment,
  deleteAssignment,
  getShoppingList,
  setStaple,
  quotePricing,
}

export type Api = typeof api
