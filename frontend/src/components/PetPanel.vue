<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useMenuStore } from '../stores/menu'

const store = useMenuStore()

const targetKg = computed(() => (store.petTarget / 1000).toFixed(2))

function decreaseTarget(): void {
  const next = Math.max(0, store.petTarget - 250)
  store.setPetTarget(next).catch(() => undefined)
}

function increaseTarget(): void {
  store.setPetTarget(store.petTarget + 250).catch(() => undefined)
}

function onRegenerate(): void {
  store.regeneratePet().catch(() => undefined)
}

function onReplace(name: string): void {
  store.replacePetFood(name).catch(() => undefined)
}
</script>

<template>
  <aside class="pet">
    <h2>Huisdiervoer ≈ {{ targetKg }} kg</h2>
    <p v-if="store.petCovered > 0" class="covered">
      ~{{ store.petCovered }} g uit restjes
    </p>

    <div class="controls">
      <button type="button" @click="decreaseTarget">−250 g</button>
      <button type="button" @click="increaseTarget">+250 g</button>
      <button type="button" class="regen" @click="onRegenerate">Regenereer</button>
    </div>

    <p v-if="store.petSelection.length === 0" class="empty">
      Nog geen voer gekozen — klik op Regenereer.
    </p>
    <ul v-else>
      <li v-for="food in store.petSelection" :key="food.id">
        <span class="name">{{ food.name }}</span>
        <button
          type="button"
          class="replace"
          title="Vervang door ander voer"
          @click="onReplace(food.name)"
        >
          ↻
        </button>
      </li>
    </ul>

    <RouterLink to="/pet-foods" class="edit-link">Bewerk voerlijst</RouterLink>
  </aside>
</template>

<style scoped>
.pet {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.9rem;
  margin-top: 1rem;
}

.pet h2 {
  margin: 0 0 0.2rem;
  font-size: 1rem;
}

.covered {
  margin: 0 0 0.6rem;
  color: var(--muted);
  font-size: 0.8rem;
}

.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 0.6rem;
}

.controls button {
  padding: 0.2rem 0.5rem;
  font-size: 0.8rem;
}

.regen {
  margin-left: auto;
}

.empty {
  color: var(--muted);
  font-size: 0.85rem;
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
  padding: 0.25rem 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.88rem;
}

.name {
  flex: 1;
}

.replace {
  padding: 0 0.4rem;
  font-size: 0.9rem;
  line-height: 1.3;
}

.edit-link {
  display: inline-block;
  margin-top: 0.6rem;
  font-size: 0.8rem;
}
</style>
