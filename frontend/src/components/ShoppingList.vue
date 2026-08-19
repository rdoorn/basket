<script setup lang="ts">
import type { ShoppingItem } from '../api/client'

defineProps<{ items: ShoppingItem[] }>()

const emit = defineEmits<{ (e: 'demote', name: string): void }>()

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
  <aside class="shopping">
    <h2>Boodschappenlijst</h2>
    <p v-if="items.length === 0" class="empty">Nog geen recepten ingepland.</p>
    <ul v-else>
      <li v-for="item in items" :key="`${item.name}-${item.unit}`">
        <button
          class="demote"
          type="button"
          title="Verplaats naar 'heb ik vast wel'"
          @click="emit('demote', item.name)"
        >
          −
        </button>
        <span class="name">{{ item.name }}</span>
        <span class="qty">{{ formatQty(item) }}</span>
      </li>
    </ul>
  </aside>
</template>

<style scoped>
.shopping {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.9rem;
}

.shopping h2 {
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

.qty {
  color: var(--muted);
  white-space: nowrap;
}

.demote {
  padding: 0 0.4rem;
  font-size: 0.85rem;
  line-height: 1.3;
}
</style>
