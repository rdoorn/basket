<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getRecipe, type Ingredient, type Recipe, type Step } from '../api/client'

const props = defineProps<{ id: string }>()
const router = useRouter()

const recipe = ref<Recipe | null>(null)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    recipe.value = await getRecipe(props.id)
  } catch (err) {
    error.value = String(err)
  }
})

// Group ingredients by their `group`, preserving first-seen order.
const groupedIngredients = computed<Array<{ group: string; items: Ingredient[] }>>(() => {
  if (!recipe.value) {
    return []
  }
  const order: string[] = []
  const map = new Map<string, Ingredient[]>()
  for (const ing of recipe.value.ingredients) {
    const key = ing.group ?? 'Overig'
    if (!map.has(key)) {
      map.set(key, [])
      order.push(key)
    }
    map.get(key)!.push(ing)
  }
  return order.map((g) => ({ group: g, items: map.get(g)! }))
})

// Sum step durations per phase group: prep vs. active cook (cook + finish).
function sumPhase(steps: Step[], phases: Step['phase'][]): { low: number; high: number } {
  let low = 0
  let high = 0
  for (const s of steps) {
    if (phases.includes(s.phase)) {
      low += s.duration_min_low ?? 0
      high += s.duration_min_high ?? s.duration_min_low ?? 0
    }
  }
  return { low, high }
}

const timeSummary = computed(() => {
  if (!recipe.value) {
    return null
  }
  const prep = sumPhase(recipe.value.steps, ['prep'])
  const active = sumPhase(recipe.value.steps, ['cook', 'finish'])
  return { prep, active }
})

function formatRange(low: number | null, high: number | null): string {
  if (low === null && high === null) {
    return '—'
  }
  if (low !== null && high !== null && low !== high) {
    return `${low}–${high} min`
  }
  return `${high ?? low} min`
}

const sortedSteps = computed<Step[]>(() => {
  if (!recipe.value) {
    return []
  }
  return [...recipe.value.steps].sort((a, b) => a.order - b.order)
})

function formatQty(ing: Ingredient): string {
  if (ing.quantity === null) {
    return ''
  }
  const qty = Number.isInteger(ing.quantity)
    ? String(ing.quantity)
    : String(ing.quantity)
  return ing.unit ? `${qty} ${ing.unit}` : qty
}

function editRecipe(): void {
  router.push({ name: 'recipe-edit', params: { id: props.id } })
}
</script>

<template>
  <div class="detail">
    <p v-if="error" class="error">Kon recept niet laden: {{ error }}</p>

    <template v-if="recipe">
      <!-- 1. icon + title (+ description) -->
      <header class="hero">
        <span class="icon">{{ recipe.icon }}</span>
        <div>
          <h1>{{ recipe.title }}</h1>
          <p v-if="recipe.description" class="desc">{{ recipe.description }}</p>
          <p class="servings">Basis: {{ recipe.servings }} personen</p>
        </div>
        <button type="button" class="edit" @click="editRecipe">Bewerken</button>
      </header>

      <!-- 2. Full ingredient list first, grouped -->
      <section class="ingredients">
        <h2>Ingrediënten</h2>
        <div v-for="grp in groupedIngredients" :key="grp.group" class="group">
          <h3>{{ grp.group }}</h3>
          <ul>
            <li v-for="(ing, i) in grp.items" :key="`${ing.name}-${i}`">
              <span class="qty">{{ formatQty(ing) }}</span>
              <span class="name">{{ ing.name }}</span>
              <span v-if="ing.note" class="note">({{ ing.note }})</span>
            </li>
          </ul>
        </div>
      </section>

      <!-- 3. Cook-time header: total + prep vs active summary -->
      <section class="timing">
        <h2>Bereidingstijd</h2>
        <div class="time-grid">
          <div>
            <span class="label">Totaal</span>
            <span class="value">
              {{ formatRange(recipe.total_time_min_low, recipe.total_time_min_high) }}
            </span>
          </div>
          <div v-if="timeSummary">
            <span class="label">Voorbereiden (prep)</span>
            <span class="value">
              {{ formatRange(timeSummary.prep.low, timeSummary.prep.high) }}
            </span>
          </div>
          <div v-if="timeSummary">
            <span class="label">Actief koken</span>
            <span class="value">
              {{ formatRange(timeSummary.active.low, timeSummary.active.high) }}
            </span>
          </div>
        </div>
      </section>

      <!-- 4. Steps in order -->
      <section class="steps">
        <h2>Stappen</h2>
        <ol>
          <li v-for="step in sortedSteps" :key="step.order" class="step">
            <div class="step-head">
              <span class="step-title">{{ step.order }}. {{ step.title }}</span>
              <span class="step-meta">
                <span class="phase">{{ step.phase }}</span>
                <span class="dur">
                  {{ formatRange(step.duration_min_low, step.duration_min_high) }}
                </span>
              </span>
            </div>
            <p class="instructions">{{ step.instructions }}</p>
          </li>
        </ol>
      </section>

      <p v-if="recipe.notes" class="recipe-notes"><strong>Notitie:</strong> {{ recipe.notes }}</p>
    </template>
  </div>
</template>

<style scoped>
.detail {
  max-width: 760px;
  margin: 0 auto;
}

.hero {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.hero .icon {
  font-size: 3rem;
  line-height: 1;
}

.hero h1 {
  margin: 0 0 0.25rem;
}

.hero .desc {
  margin: 0;
  color: var(--muted);
}

.hero .servings {
  margin: 0.25rem 0 0;
  font-size: 0.85rem;
  color: var(--muted);
}

.hero .edit {
  margin-left: auto;
}

section {
  margin-top: 1.5rem;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem;
}

h2 {
  margin: 0 0 0.75rem;
  font-size: 1.1rem;
}

.group h3 {
  margin: 0.75rem 0 0.35rem;
  font-size: 0.95rem;
  color: var(--accent);
}

.ingredients ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.ingredients li {
  display: flex;
  gap: 0.5rem;
  padding: 0.2rem 0;
}

.qty {
  min-width: 5rem;
  color: var(--muted);
}

.note {
  color: var(--muted);
  font-style: italic;
}

.time-grid {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.time-grid .label {
  display: block;
  font-size: 0.8rem;
  color: var(--muted);
}

.time-grid .value {
  font-size: 1.1rem;
  font-weight: 600;
}

.steps ol {
  margin: 0;
  padding: 0;
  list-style: none;
}

.step {
  padding: 0.6rem 0;
  border-bottom: 1px solid var(--border);
}

.step:last-child {
  border-bottom: none;
}

.step-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
}

.step-title {
  font-weight: 600;
}

.step-meta {
  display: flex;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: var(--muted);
}

.phase {
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.instructions {
  margin: 0.4rem 0 0;
  white-space: pre-wrap;
}

.recipe-notes {
  margin-top: 1rem;
  color: var(--muted);
}

.error {
  color: #c0392b;
}
</style>
