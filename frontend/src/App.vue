<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <RouterLink to="/" class="brand">🧺 Basket</RouterLink>
      <nav class="app-nav">
        <RouterLink to="/">Kalender</RouterLink>
        <RouterLink to="/buy">Kopen</RouterLink>
        <RouterLink to="/recipe/new">Recept toevoegen</RouterLink>
      </nav>
    </header>
    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
  background: var(--panel);
  border-bottom: 1px solid var(--border);
}

.brand {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text);
}

.app-nav {
  display: flex;
  gap: 1rem;
}

.app-nav a.router-link-active {
  font-weight: 600;
}

.app-main {
  padding: 1.5rem;
}
</style>
