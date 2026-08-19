<script setup lang="ts">
import { onMounted } from 'vue'
import { useMenuStore } from '../stores/menu'
import PetFoodEditor from '../components/PetFoodEditor.vue'

const store = useMenuStore()

onMounted(() => {
  if (store.petFoods.length === 0) {
    store.loadPetFoods().catch(() => undefined)
  }
})
</script>

<template>
  <div class="pet-foods">
    <h1>Huisdiervoer</h1>
    <p class="intro">
      Beheer de lijst met groenten en snacks die Basket kan kiezen voor het
      wekelijkse huisdiervoer.
    </p>
    <PetFoodEditor />
  </div>
</template>

<style scoped>
.pet-foods {
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
</style>
