<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { quotePricing, type StoreQuote } from '../api/client'

const router = useRouter()
const quotes = ref<StoreQuote[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const res = await quotePricing()
    quotes.value = res.quotes
  } catch (err) {
    error.value = String(err)
  } finally {
    loading.value = false
  }
})

const cheapestStore = computed<string | null>(() => {
  if (quotes.value.length === 0) {
    return null
  }
  return quotes.value.reduce((best, q) => (q.total < best.total ? q : best)).store
})

function money(value: number): string {
  return `€ ${value.toFixed(2)}`
}
</script>

<template>
  <div class="buy">
    <div class="toolbar">
      <h1>Kopen — prijsvergelijking</h1>
      <button type="button" @click="router.push('/')">Terug naar kalender</button>
    </div>

    <p v-if="loading">Prijzen ophalen…</p>
    <p v-else-if="error" class="error">Kon prijzen niet ophalen: {{ error }}</p>
    <p v-else-if="quotes.length === 0" class="empty">
      Geen boodschappen om te vergelijken. Plan eerst recepten in.
    </p>

    <div v-else class="stores">
      <section
        v-for="quote in quotes"
        :key="quote.store"
        class="store"
        :class="{ cheapest: quote.store === cheapestStore }"
      >
        <header class="store-head">
          <h2>
            {{ quote.store }}
            <span v-if="quote.store === cheapestStore" class="badge">goedkoopst</span>
          </h2>
          <span class="total">{{ money(quote.total) }}</span>
        </header>
        <table>
          <thead>
            <tr>
              <th>Ingrediënt</th>
              <th class="num">Aantal</th>
              <th>Eenheid</th>
              <th class="num">Stukprijs</th>
              <th class="num">Regeltotaal</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, i) in quote.items" :key="`${item.name}-${i}`">
              <td>{{ item.name }}</td>
              <td class="num">{{ item.quantity ?? '' }}</td>
              <td>{{ item.unit ?? '' }}</td>
              <td class="num">{{ money(item.unit_price) }}</td>
              <td class="num">{{ money(item.line_total) }}</td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td colspan="4" class="total-label">Totaal</td>
              <td class="num total-value">{{ money(quote.total) }}</td>
            </tr>
          </tfoot>
        </table>
      </section>
    </div>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.toolbar h1 {
  margin: 0;
  font-size: 1.4rem;
}

.stores {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 1rem;
}

.store {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem;
}

.store.cheapest {
  background: var(--cheap);
  border-color: var(--cheap-border);
}

.store-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 0.5rem;
}

.store-head h2 {
  margin: 0;
  font-size: 1.1rem;
}

.badge {
  margin-left: 0.5rem;
  font-size: 0.7rem;
  background: var(--cheap-border);
  color: #fff;
  border-radius: 999px;
  padding: 0.1rem 0.5rem;
  vertical-align: middle;
}

.total {
  font-weight: 700;
  font-size: 1.15rem;
}

.num {
  text-align: right;
}

.total-label {
  text-align: right;
  font-weight: 600;
}

.total-value {
  font-weight: 700;
}

.error {
  color: #c0392b;
}

.empty {
  color: var(--muted);
}
</style>
