<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  createRecipe,
  deleteRecipe,
  getRecipe,
  updateRecipe,
  type Ingredient,
  type RecipeCategory,
  type RecipeInput,
  type Step,
  type StepPhase,
} from '../api/client'

const props = defineProps<{ id?: string }>()
const router = useRouter()

const isEdit = computed(() => !!props.id)
const saving = ref(false)
const error = ref<string | null>(null)

function emptyIngredient(): Ingredient {
  return {
    group: '',
    name: '',
    quantity: null,
    unit: '',
    note: null,
    normalized_name: null,
    brand_override: null,
    source: 'supermarket',
  }
}

function emptyStep(order: number): Step {
  return {
    order,
    title: '',
    phase: 'cook',
    duration_min_low: null,
    duration_min_high: null,
    instructions: '',
  }
}

const form = reactive<RecipeInput>({
  title: '',
  icon: '🍽️',
  description: '',
  servings: 4,
  category: 'meal',
  total_time_min_low: null,
  total_time_min_high: null,
  tags: [],
  notes: null,
  ingredients: [emptyIngredient()],
  steps: [emptyStep(1)],
})

const phases: StepPhase[] = ['prep', 'cook', 'finish']
const categories: RecipeCategory[] = ['meal', 'bake']

onMounted(async () => {
  if (props.id) {
    try {
      const recipe = await getRecipe(props.id)
      form.title = recipe.title
      form.icon = recipe.icon
      form.description = recipe.description
      form.servings = recipe.servings
      form.category = recipe.category
      form.total_time_min_low = recipe.total_time_min_low
      form.total_time_min_high = recipe.total_time_min_high
      form.tags = recipe.tags
      form.notes = recipe.notes
      form.ingredients = recipe.ingredients.length
        ? recipe.ingredients
        : [emptyIngredient()]
      form.steps = recipe.steps.length ? recipe.steps : [emptyStep(1)]
    } catch (err) {
      error.value = String(err)
    }
  }
})

function addIngredient(): void {
  form.ingredients.push(emptyIngredient())
}

function removeIngredient(index: number): void {
  form.ingredients.splice(index, 1)
}

function addStep(): void {
  form.steps.push(emptyStep(form.steps.length + 1))
}

function removeStep(index: number): void {
  form.steps.splice(index, 1)
  form.steps.forEach((s, i) => {
    s.order = i + 1
  })
}

function normalize(): RecipeInput {
  return {
    ...form,
    ingredients: form.ingredients
      .filter((i) => i.name.trim() !== '')
      .map((i) => ({
        ...i,
        group: i.group && i.group.trim() !== '' ? i.group : null,
        unit: i.unit && i.unit.trim() !== '' ? i.unit : null,
        quantity:
          i.quantity === null || Number.isNaN(i.quantity) ? null : Number(i.quantity),
      })),
    steps: form.steps
      .filter((s) => s.title.trim() !== '' || s.instructions.trim() !== '')
      .map((s, i) => ({
        ...s,
        order: i + 1,
        duration_min_low:
          s.duration_min_low === null ? null : Number(s.duration_min_low),
        duration_min_high:
          s.duration_min_high === null ? null : Number(s.duration_min_high),
      })),
    servings: Number(form.servings),
    total_time_min_low:
      form.total_time_min_low === null ? null : Number(form.total_time_min_low),
    total_time_min_high:
      form.total_time_min_high === null ? null : Number(form.total_time_min_high),
  }
}

async function save(): Promise<void> {
  saving.value = true
  error.value = null
  try {
    const payload = normalize()
    if (props.id) {
      await updateRecipe(props.id, { ...payload, id: props.id })
    } else {
      await createRecipe(payload)
    }
    router.push('/')
  } catch (err) {
    error.value = String(err)
  } finally {
    saving.value = false
  }
}

async function remove(): Promise<void> {
  if (!props.id) {
    return
  }
  if (!confirm('Recept verwijderen?')) {
    return
  }
  try {
    await deleteRecipe(props.id)
    router.push('/')
  } catch (err) {
    error.value = String(err)
  }
}
</script>

<template>
  <div class="edit">
    <h1>{{ isEdit ? 'Recept bewerken' : 'Nieuw recept' }}</h1>
    <p v-if="error" class="error">{{ error }}</p>

    <section class="card">
      <h2>Basis</h2>
      <div class="row">
        <label class="grow">
          Titel
          <input v-model="form.title" type="text" />
        </label>
        <label class="icon-field">
          Icoon
          <input v-model="form.icon" type="text" maxlength="4" />
        </label>
        <label class="num">
          Personen
          <input v-model.number="form.servings" type="number" min="1" />
        </label>
        <label class="num">
          Categorie
          <select v-model="form.category" class="phase-in">
            <option v-for="c in categories" :key="c" :value="c">
              {{ c === 'bake' ? 'Baksel' : 'Maaltijd' }}
            </option>
          </select>
        </label>
      </div>
      <label class="block">
        Omschrijving
        <input v-model="form.description" type="text" />
      </label>
      <div class="row">
        <label class="num">
          Totale tijd (min, laag)
          <input v-model.number="form.total_time_min_low" type="number" min="0" />
        </label>
        <label class="num">
          Totale tijd (min, hoog)
          <input v-model.number="form.total_time_min_high" type="number" min="0" />
        </label>
      </div>
    </section>

    <section class="card">
      <div class="section-head">
        <h2>Ingrediënten</h2>
        <button type="button" @click="addIngredient">+ Ingrediënt</button>
      </div>
      <div v-for="(ing, i) in form.ingredients" :key="i" class="ing-row">
        <input v-model="ing.group" type="text" placeholder="Groep" class="group-in" />
        <input v-model="ing.name" type="text" placeholder="Naam" class="name-in" />
        <input
          v-model.number="ing.quantity"
          type="number"
          step="any"
          placeholder="Aantal"
          class="qty-in"
        />
        <input v-model="ing.unit" type="text" placeholder="Eenheid" class="unit-in" />
        <button type="button" class="del" @click="removeIngredient(i)">✕</button>
      </div>
    </section>

    <section class="card">
      <div class="section-head">
        <h2>Stappen</h2>
        <button type="button" @click="addStep">+ Stap</button>
      </div>
      <div v-for="(step, i) in form.steps" :key="i" class="step-row">
        <div class="step-top">
          <span class="order">#{{ step.order }}</span>
          <input v-model="step.title" type="text" placeholder="Titel" class="title-in" />
          <select v-model="step.phase" class="phase-in">
            <option v-for="p in phases" :key="p" :value="p">{{ p }}</option>
          </select>
          <input
            v-model.number="step.duration_min_low"
            type="number"
            min="0"
            placeholder="min laag"
            class="dur-in"
          />
          <input
            v-model.number="step.duration_min_high"
            type="number"
            min="0"
            placeholder="min hoog"
            class="dur-in"
          />
          <button type="button" class="del" @click="removeStep(i)">✕</button>
        </div>
        <textarea
          v-model="step.instructions"
          rows="3"
          placeholder="Instructies"
          class="instr-in"
        ></textarea>
      </div>
    </section>

    <div class="actions">
      <button type="button" class="primary" :disabled="saving" @click="save">
        {{ saving ? 'Bezig…' : 'Opslaan' }}
      </button>
      <button v-if="isEdit" type="button" class="danger" @click="remove">Verwijderen</button>
      <button type="button" @click="router.push('/')">Annuleren</button>
    </div>
  </div>
</template>

<style scoped>
.edit {
  max-width: 820px;
  margin: 0 auto;
}

.card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

h2 {
  margin: 0 0 0.75rem;
  font-size: 1.05rem;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.85rem;
  color: var(--muted);
}

.row {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}

.grow {
  flex: 1;
}

.block {
  display: flex;
  flex-direction: column;
  margin-bottom: 0.75rem;
}

.icon-field input {
  width: 4rem;
}

.num input {
  width: 8rem;
}

.ing-row,
.step-top {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  align-items: center;
}

.group-in {
  width: 8rem;
}

.name-in {
  flex: 1;
}

.qty-in {
  width: 6rem;
}

.unit-in {
  width: 6rem;
}

.title-in {
  flex: 1;
}

.phase-in {
  width: 6rem;
}

.dur-in {
  width: 6rem;
}

.order {
  color: var(--muted);
  font-size: 0.85rem;
  min-width: 2rem;
}

.step-row {
  padding-bottom: 0.75rem;
  margin-bottom: 0.75rem;
  border-bottom: 1px solid var(--border);
}

.instr-in {
  width: 100%;
  resize: vertical;
}

.del {
  color: #c0392b;
}

.danger {
  background: #c0392b;
  color: #fff;
  border-color: #c0392b;
}

.actions {
  display: flex;
  gap: 0.5rem;
}
</style>
