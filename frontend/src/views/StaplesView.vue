<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useMenuStore } from '../stores/menu'

const store = useMenuStore()

const name = ref('')

onMounted(() => {
  if (store.staples.length === 0) {
    store.loadStaples().catch(() => undefined)
  }
})

function onAdd(): void {
  const trimmed = name.value.trim()
  if (!trimmed) {
    return
  }
  store
    .addStaple(trimmed)
    .then(() => {
      name.value = ''
    })
    .catch(() => undefined)
}

function onRemove(id: string): void {
  store.deleteStaple(id).catch(() => undefined)
}
</script>

<template>
  <div class="staples">
    <h1>Heb ik vast wel</h1>
    <p class="intro">
      Deze ingrediënten zet Basket standaard op je voorraadlijst in plaats van
      de boodschappenlijst.
    </p>

    <div class="add-row">
      <input
        v-model="name"
        class="name-input"
        type="text"
        placeholder="Naam (bijv. suiker)"
        @keyup.enter="onAdd"
      />
      <button type="button" class="add" @click="onAdd">Toevoegen</button>
    </div>

    <p v-if="store.staples.length === 0" class="empty">
      Nog geen vaste voorraad in de lijst.
    </p>
    <ul v-else>
      <li v-for="staple in store.staples" :key="staple.id">
        <span class="name">{{ staple.name }}</span>
        <button
          type="button"
          class="remove"
          title="Verwijder"
          @click="onRemove(staple.id)"
        >
          ✕
        </button>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.staples {
  max-width: 620px;
  margin: 0 auto;
}

h1 {
  font-size: 1.3rem;
  margin: 0 0 0.5rem;
}

.intro {
  color: var(--muted);
  font-size: 0.9rem;
  margin: 0 0 1rem;
}

.add-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.name-input {
  flex: 1;
  min-width: 0;
  padding: 0.3rem 0.45rem;
  font-size: 0.9rem;
}

.add {
  padding: 0.3rem 0.7rem;
  font-size: 0.85rem;
}

.empty {
  color: var(--muted);
  font-size: 0.9rem;
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
  padding: 0.35rem 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.92rem;
}

.name {
  flex: 1;
}

.remove {
  padding: 0 0.4rem;
  font-size: 0.8rem;
  line-height: 1.4;
  color: #c0392b;
}
</style>
