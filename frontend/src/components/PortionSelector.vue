<script setup lang="ts">
import { computed, ref, watch } from 'vue'

const props = defineProps<{ modelValue: number }>()
const emit = defineEmits<{ (e: 'update:modelValue', value: number): void }>()

const presets = [0.5, 1, 1.5, 2]

const isCustom = computed(() => !presets.includes(props.modelValue))
const customValue = ref<number>(props.modelValue)

watch(
  () => props.modelValue,
  (v) => {
    customValue.value = v
  },
)

function selectPreset(value: number): void {
  emit('update:modelValue', value)
}

function onCustomInput(event: Event): void {
  const raw = (event.target as HTMLInputElement).value
  const value = Number(raw)
  if (Number.isFinite(value) && value > 0) {
    emit('update:modelValue', value)
  }
}
</script>

<template>
  <div class="portions" @click.stop>
    <button
      v-for="p in presets"
      :key="p"
      type="button"
      class="chip"
      :class="{ active: modelValue === p }"
      @click="selectPreset(p)"
    >
      {{ p }}×
    </button>
    <input
      class="custom"
      :class="{ active: isCustom }"
      type="number"
      min="0.25"
      step="0.25"
      :value="customValue"
      title="Aangepast aantal"
      @input="onCustomInput"
    />
  </div>
</template>

<style scoped>
.portions {
  display: flex;
  gap: 0.25rem;
  align-items: center;
  flex-wrap: wrap;
}

.chip {
  padding: 0.15rem 0.4rem;
  font-size: 0.78rem;
  border-radius: 999px;
}

.chip.active {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}

.custom {
  width: 4rem;
  padding: 0.15rem 0.3rem;
  font-size: 0.78rem;
}

.custom.active {
  border-color: var(--accent);
}
</style>
