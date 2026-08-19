<script setup lang="ts">
import { useRouter } from 'vue-router'
import { RECIPE_MIME } from '../lib/dnd'
import type { RecipeCard } from '../api/client'

const props = defineProps<{ recipe: RecipeCard }>()
const router = useRouter()

function onDragStart(event: DragEvent): void {
  if (!event.dataTransfer) {
    return
  }
  // A card drag carries only the recipe id (a new assignment).
  event.dataTransfer.setData(RECIPE_MIME, props.recipe.id)
  event.dataTransfer.effectAllowed = 'copy'
}

function openDetail(): void {
  router.push({ name: 'recipe-detail', params: { id: props.recipe.id } })
}
</script>

<template>
  <div
    class="recipe-card"
    draggable="true"
    @dragstart="onDragStart"
    @click="openDetail"
  >
    <span class="icon">{{ recipe.icon }}</span>
    <div class="body">
      <div class="title">
        {{ recipe.title }}
        <span v-if="recipe.category === 'bake'" class="badge" title="Baksel">🍞</span>
      </div>
      <div class="desc">{{ recipe.description }}</div>
    </div>
  </div>
</template>

<style scoped>
.recipe-card {
  display: flex;
  gap: 0.6rem;
  align-items: flex-start;
  padding: 0.6rem;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: grab;
}

.recipe-card:hover {
  border-color: var(--accent);
}

.icon {
  font-size: 1.6rem;
  line-height: 1;
}

.title {
  font-weight: 600;
}

.badge {
  margin-left: 0.25rem;
  font-size: 0.9rem;
}

.desc {
  font-size: 0.82rem;
  color: var(--muted);
}
</style>
