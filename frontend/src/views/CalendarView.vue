<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMenuStore } from '../stores/menu'
import RecipeCard from '../components/RecipeCard.vue'
import DayCell from '../components/DayCell.vue'
import ShoppingList from '../components/ShoppingList.vue'
import PantryList from '../components/PantryList.vue'

const store = useMenuStore()
const router = useRouter()

const toast = ref<string | null>(null)
let toastTimer: ReturnType<typeof setTimeout> | undefined

function showToast(message: string): void {
  toast.value = message
  if (toastTimer) {
    clearTimeout(toastTimer)
  }
  toastTimer = setTimeout(() => {
    toast.value = null
  }, 2500)
}

onMounted(() => {
  store.loadAll().catch((err) => showToast(`Laden mislukt: ${String(err)}`))
})

function onAssign(payload: { date: string; recipeId: string }): void {
  const existing = store.assignments[payload.date]
  const multiplier = existing ? existing.multiplier : 1
  store
    .assign(payload.date, payload.recipeId, multiplier)
    .catch((err) => showToast(`Opslaan mislukt: ${String(err)}`))
}

function onMove(payload: { fromDate: string; toDate: string }): void {
  store
    .moveOrSwap(payload.fromDate, payload.toDate)
    .catch((err) => showToast(`Verplaatsen mislukt: ${String(err)}`))
}

function onMultiplier(payload: { date: string; multiplier: number }): void {
  store
    .setMultiplier(payload.date, payload.multiplier)
    .catch((err) => showToast(`Opslaan mislukt: ${String(err)}`))
}

function onRemove(date: string): void {
  store.removeDay(date).catch((err) => showToast(`Verwijderen mislukt: ${String(err)}`))
}

function onSave(): void {
  // All calendar changes auto-save; Save is an explicit confirmation snapshot.
  store.markSaved()
  showToast('Weekmenu opgeslagen ✓')
}

function onPromote(name: string): void {
  store.setStaple(name, true).catch((err) => showToast(`Toevoegen mislukt: ${String(err)}`))
}

function onUnpromote(name: string): void {
  store.setStaple(name, false).catch((err) => showToast(`Terugzetten mislukt: ${String(err)}`))
}
</script>

<template>
  <div class="calendar">
    <div class="toolbar">
      <h1>Weekmenu</h1>
      <div class="actions">
        <button type="button" @click="onSave">Opslaan</button>
        <button type="button" @click="router.push('/recipe/new')">Recept toevoegen</button>
        <button type="button" class="primary" @click="router.push('/buy')">Kopen</button>
      </div>
    </div>

    <div class="layout">
      <section class="library">
        <h2>Recepten</h2>
        <p v-if="store.recipes.length === 0" class="empty">Nog geen recepten.</p>
        <RecipeCard v-for="r in store.recipes" :key="r.id" :recipe="r" />
      </section>

      <section class="grid">
        <DayCell
          v-for="date in store.days"
          :key="date"
          :date="date"
          :assignment="store.assignments[date] ?? null"
          :recipe="
            store.assignments[date]
              ? store.recipeById(store.assignments[date].recipeId)
              : undefined
          "
          @assign="onAssign"
          @move="onMove"
          @multiplier="onMultiplier"
          @remove="onRemove"
        />
      </section>

      <div class="side">
        <ShoppingList :items="store.shoppingList" @unpromote="onUnpromote" />
        <PantryList :items="store.pantry" @promote="onPromote" />
      </div>
    </div>

    <transition name="fade">
      <div v-if="toast" class="toast">{{ toast }}</div>
    </transition>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.toolbar h1 {
  margin: 0;
  font-size: 1.4rem;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.layout {
  display: grid;
  grid-template-columns: 240px 1fr 280px;
  gap: 1rem;
  align-items: start;
}

.library {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.library h2 {
  margin: 0;
  font-size: 1rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.5rem;
}

.empty {
  color: var(--muted);
  font-size: 0.85rem;
}

.toast {
  position: fixed;
  bottom: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  background: #1f2430;
  color: #fff;
  padding: 0.6rem 1rem;
  border-radius: 8px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 1100px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
