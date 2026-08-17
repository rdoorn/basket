<script setup lang="ts">
import type { ShoppingItem } from '../api/client'

defineProps<{ items: ShoppingItem[] }>()

const emit = defineEmits<{ (e: 'promote', name: string): void }>()

function formatQty(item: ShoppingItem): string {
  if (item.quantity === null) {
    return ''
  }
  const qty = Number.isInteger(item.quantity)
    ? String(item.quantity)
    : item.quantity.toFixed(2).replace(/\.?0+$/, '')
  return item.unit ? `${qty} ${item.unit}` : qty
}
</script>

<template>
  <aside class="pantry">
    <h2>Heb ik vast wel</h2>
    <p class="hint">Klik op + om iets toch te bestellen.</p>
    <p v-if="items.length === 0" class="empty">Niets nodig uit de voorraad.</p>
    <ul v-else>
      <li v-for="item in items" :key="`${item.name}-${item.unit}`">
        <button
          class="promote"
          type="button"
          title="Voeg toe aan boodschappenlijst"
          @click="emit('promote', item.name)"
        >
          +
        </button>
        <span class="name">{{ item.name }}</span>
        <span class="qty">{{ formatQty(item) }}</span>
      </li>
    </ul>
  </aside>
</template>

<style scoped>
.pantry {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.9rem;
  margin-top: 1rem;
}

.pantry h2 {
  margin: 0 0 0.2rem;
  font-size: 1rem;
}

.hint {
  margin: 0 0 0.5rem;
  color: var(--muted);
  font-size: 0.78rem;
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

.promote {
  padding: 0 0.4rem;
  font-size: 0.85rem;
  line-height: 1.3;
}

.name {
  flex: 1;
}

.qty {
  color: var(--muted);
  white-space: nowrap;
}
</style>
