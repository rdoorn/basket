<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import PortionSelector from './PortionSelector.vue'
import { FROMDATE_MIME, RECIPE_MIME, dropEffectForTypes } from '../lib/dnd'
import type { Assignment, RecipeCard } from '../api/client'

const props = defineProps<{
  date: string
  assignment: Assignment | null
  recipe: RecipeCard | undefined
}>()

const emit = defineEmits<{
  (e: 'assign', payload: { date: string; recipeId: string }): void
  (e: 'move', payload: { fromDate: string; toDate: string }): void
  (e: 'multiplier', payload: { date: string; multiplier: number }): void
  (e: 'remove', date: string): void
}>()

const router = useRouter()
const dragOver = ref(false)

const label = computed(() => {
  const d = new Date(`${props.date}T00:00:00`)
  const weekday = d.toLocaleDateString('nl-NL', { weekday: 'short' })
  const day = d.toLocaleDateString('nl-NL', { day: 'numeric', month: 'short' })
  return { weekday, day }
})

function onDragStart(event: DragEvent): void {
  if (!event.dataTransfer || !props.assignment) {
    return
  }
  // A cell drag carries its source date (a move/swap).
  event.dataTransfer.setData(FROMDATE_MIME, props.date)
  event.dataTransfer.effectAllowed = 'move'
}

function onDragOver(event: DragEvent): void {
  event.preventDefault()
  dragOver.value = true
  if (event.dataTransfer) {
    // Must match the source's effectAllowed (copy for a library recipe, move
    // for a cell drag) or the browser silently refuses the drop.
    event.dataTransfer.dropEffect = dropEffectForTypes(event.dataTransfer.types)
  }
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
  const fromDate = dt.getData(FROMDATE_MIME)
  if (fromDate) {
    emit('move', { fromDate, toDate: props.date })
    return
  }
  const recipeId = dt.getData(RECIPE_MIME)
  if (recipeId) {
    emit('assign', { date: props.date, recipeId })
  }
}

function openDetail(): void {
  if (props.assignment) {
    router.push({ name: 'recipe-detail', params: { id: props.assignment.recipeId } })
  }
}

function onMultiplier(value: number): void {
  emit('multiplier', { date: props.date, multiplier: value })
}
</script>

<template>
  <div
    class="day-cell"
    :class="{ 'drag-over': dragOver, occupied: !!assignment }"
    @dragover="onDragOver"
    @dragleave="onDragLeave"
    @drop="onDrop"
  >
    <header class="day-head">
      <span class="weekday">{{ label.weekday }}</span>
      <span class="date">{{ label.day }}</span>
    </header>

    <div
      v-if="assignment"
      class="assigned"
      draggable="true"
      @dragstart="onDragStart"
    >
      <div class="recipe" @click="openDetail">
        <span class="icon">{{ recipe?.icon ?? '🍽️' }}</span>
        <span class="title">{{ recipe?.title ?? assignment.recipeId }}</span>
      </div>
      <PortionSelector
        :model-value="assignment.multiplier"
        @update:model-value="onMultiplier"
      />
      <button class="remove" type="button" title="Verwijder" @click="emit('remove', date)">
        ✕
      </button>
    </div>

    <div v-else class="empty">Sleep hier een recept</div>
  </div>
</template>

<style scoped>
.day-cell {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  min-height: 108px;
  padding: 0.5rem;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
}

.day-cell.drag-over {
  border-color: var(--accent);
  background: var(--accent-weak);
}

.day-head {
  display: flex;
  justify-content: space-between;
  font-size: 0.78rem;
  color: var(--muted);
}

.weekday {
  text-transform: capitalize;
  font-weight: 600;
}

.assigned {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  cursor: grab;
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

.empty {
  color: var(--muted);
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  flex: 1;
}
</style>
