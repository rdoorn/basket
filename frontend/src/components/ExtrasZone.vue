<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import PortionSelector from './PortionSelector.vue'
import { useMenuStore } from '../stores/menu'
import { RECIPE_MIME } from '../lib/dnd'

const store = useMenuStore()
const router = useRouter()
const dragOver = ref(false)

function onDragOver(event: DragEvent): void {
  const dt = event.dataTransfer
  // Only library recipe cards belong here. Reject day-cell (move) drags by not
  // becoming a drop target, so the browser shows a no-drop cursor instead of a
  // silent no-op. Recipe cards drag with effectAllowed="copy" -> dropEffect copy.
  if (!dt || !dt.types.includes(RECIPE_MIME)) {
    return
  }
  event.preventDefault()
  dragOver.value = true
  dt.dropEffect = 'copy'
}

function onDragLeave(): void {
  dragOver.value = false
}

function onDrop(event: DragEvent): void {
  event.preventDefault()
  dragOver.value = false
  const dt = event.dataTransfer
  if (!dt) {
    return
  }
  const recipeId = dt.getData(RECIPE_MIME)
  if (recipeId) {
    store.addExtra(recipeId, 1).catch(() => undefined)
  }
}

function onMultiplier(recipeId: string, value: number): void {
  store.setExtraMultiplier(recipeId, value).catch(() => undefined)
}

function onRemove(recipeId: string): void {
  store.removeExtra(recipeId).catch(() => undefined)
}

function openDetail(recipeId: string): void {
  router.push({ name: 'recipe-detail', params: { id: recipeId } })
}
</script>

<template>
  <section
    class="extras"
    :class="{ 'drag-over': dragOver }"
    @dragover="onDragOver"
    @dragleave="onDragLeave"
    @drop="onDrop"
  >
    <h2>Extra's</h2>
    <p v-if="store.extras.length === 0" class="empty">
      Sleep hier een recept (bijv. een 🍞 baksel).
    </p>
    <ul v-else>
      <li v-for="extra in store.extras" :key="extra.recipeId" class="extra-card">
        <div class="recipe" @click="openDetail(extra.recipeId)">
          <span class="icon">
            {{ store.recipeById(extra.recipeId)?.icon ?? '🍽️' }}
          </span>
          <span class="title">
            {{ store.recipeById(extra.recipeId)?.title ?? extra.recipeId }}
          </span>
        </div>
        <PortionSelector
          :model-value="extra.multiplier"
          @update:model-value="(v: number) => onMultiplier(extra.recipeId, v)"
        />
        <button
          class="remove"
          type="button"
          title="Verwijder"
          @click="onRemove(extra.recipeId)"
        >
          ✕
        </button>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.extras {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.9rem;
}

.extras.drag-over {
  border-color: var(--accent);
  background: var(--accent-weak);
}

.extras h2 {
  margin: 0 0 0.6rem;
  font-size: 1rem;
}

.empty {
  color: var(--muted);
  font-size: 0.85rem;
}

ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.extra-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 0.5rem;
  border: 1px solid var(--border);
  border-radius: 8px;
}

.recipe {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  cursor: pointer;
}

.recipe .icon {
  font-size: 1.3rem;
}

.recipe .title {
  font-weight: 600;
  font-size: 0.9rem;
}

.remove {
  position: absolute;
  top: -0.2rem;
  right: -0.2rem;
  padding: 0 0.3rem;
  font-size: 0.7rem;
  line-height: 1.4;
}
</style>
