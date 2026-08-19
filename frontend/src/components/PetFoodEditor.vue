<script setup lang="ts">
import { ref } from 'vue'
import { useMenuStore } from '../stores/menu'

const store = useMenuStore()

const name = ref('')
const grams = ref<number>(100)

function onAdd(): void {
  const trimmed = name.value.trim()
  const weightG = Math.max(0, Math.round(Number(grams.value)))
  if (!trimmed || !Number.isFinite(weightG) || weightG <= 0) {
    return
  }
  store
    .addPetFood(trimmed, weightG)
    .then(() => {
      name.value = ''
      grams.value = 100
    })
    .catch(() => undefined)
}

function onRemove(id: string): void {
  store.deletePetFood(id).catch(() => undefined)
}
</script>

<template>
  <div class="editor">
    <div class="add-row">
      <input
        v-model="name"
        class="name-input"
        type="text"
        placeholder="Naam"
        @keyup.enter="onAdd"
      />
      <input
        v-model.number="grams"
        class="grams-input"
        type="number"
        min="1"
        step="10"
        title="Geschatte grammen per stuk"
      />
      <span class="unit">g</span>
      <button type="button" class="add" @click="onAdd">Toevoegen</button>
    </div>

    <p v-if="store.petFoods.length === 0" class="empty">Nog geen voer in de lijst.</p>
    <ul v-else>
      <li v-for="food in store.petFoods" :key="food.id">
        <span class="name">{{ food.name }}</span>
        <span class="grams">{{ food.weightG }} g</span>
        <button
          type="button"
          class="remove"
          title="Verwijder"
          @click="onRemove(food.id)"
        >
          ✕
        </button>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.editor {
  margin-top: 0.6rem;
}

.add-row {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin-bottom: 0.6rem;
}

.name-input {
  flex: 1;
  min-width: 0;
  padding: 0.2rem 0.35rem;
  font-size: 0.82rem;
}

.grams-input {
  width: 4.2rem;
  padding: 0.2rem 0.35rem;
  font-size: 0.82rem;
}

.unit {
  color: var(--muted);
  font-size: 0.8rem;
}

.add {
  padding: 0.2rem 0.5rem;
  font-size: 0.8rem;
}

.empty {
  color: var(--muted);
  font-size: 0.82rem;
}

ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.2rem 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.85rem;
}

.name {
  flex: 1;
}

.grams {
  color: var(--muted);
  white-space: nowrap;
}

.remove {
  padding: 0 0.35rem;
  font-size: 0.75rem;
  line-height: 1.4;
}
</style>
