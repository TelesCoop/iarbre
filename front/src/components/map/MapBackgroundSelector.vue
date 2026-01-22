<script lang="ts" setup>
import { ref, computed } from "vue"
import { useMapStore } from "@/stores/map"
import { MapStyle } from "@/utils/enum"

const mapStore = useMapStore()
const isExpanded = ref(false)

const options = [
  {
    value: MapStyle.OSM,
    label: "Plan",
    image: "/images/plan-ville.png"
  },
  {
    value: MapStyle.SATELLITE,
    label: "Satellite",
    image: "/images/satellite.png"
  },
  {
    value: MapStyle.CADASTRE,
    label: "Cadastre",
    image: "/images/cadastre.png"
  }
]

const currentOption = computed(() => {
  return options.find((opt) => opt.value === mapStore.selectedMapStyle) || options[0]
})

const selectStyle = (style: MapStyle) => {
  mapStore.changeMapStyle(style)
  isExpanded.value = false
}

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}
</script>

<template>
  <div class="bg-selector-wrapper">
    <div :class="{ expanded: isExpanded }" class="bg-selector-container">
      <!-- Bouton principal -->
      <button class="bg-selector-toggle" data-cy="bg-selector-toggle" @click="toggleExpanded">
        <div class="bg-selector-toggle-preview">
          <img :alt="currentOption.label" :src="currentOption.image" class="preview-image" />
        </div>
        <span class="bg-selector-toggle-label">{{ currentOption.label }}</span>
      </button>

      <!-- Options dépliées (à droite) -->
      <div v-if="isExpanded" class="bg-selector-options">
        <button
          v-for="option in options"
          :key="option.value"
          :class="{ 'bg-selector-card-selected': mapStore.selectedMapStyle === option.value }"
          :data-cy="`bg-option-${option.value}`"
          class="bg-selector-card"
          @click="selectStyle(option.value)"
        >
          <div class="bg-selector-preview">
            <img :alt="option.label" :src="option.image" class="preview-image" />
          </div>
          <span class="bg-selector-label">{{ option.label }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.bg-selector-wrapper {
  @apply flex flex-col gap-2;
}

.bg-selector-container {
  @apply flex items-center gap-2;
  @apply bg-white rounded-xl shadow-md;
  border: 1px solid rgba(0, 0, 0, 0.05);
  padding: 10px;
  height: 90px;
}

.bg-selector-toggle {
  @apply flex flex-col items-center gap-2;
  @apply cursor-pointer transition-all;
  @apply hover:bg-gray-50 rounded-lg;
  background: transparent;
  border: none;
  height: 100%;
}

.bg-selector-toggle-preview {
  @apply w-12 h-12 rounded flex items-center justify-center;
  @apply bg-gray-100;
  overflow: hidden;
  flex-shrink: 0;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.bg-selector-toggle-label {
  @apply text-sm font-sans text-gray-700 font-medium;
}

.bg-selector-toggle-arrow {
  @apply ml-auto text-gray-500 transition-transform;
}

.bg-selector-options {
  @apply flex items-center gap-2 pl-2 ml-2;
  @apply border-l border-gray-200;
  height: 100%;
}

.bg-selector-card {
  @apply flex flex-col items-center justify-center gap-1.5 p-2 rounded-lg;
  @apply cursor-pointer transition-all;
  @apply border-2 border-transparent;
  background: transparent;
  min-width: 72px;
  height: 100%;
}

.bg-selector-card:hover {
  @apply bg-gray-50;
}

.bg-selector-card-selected {
  @apply bg-primary-50;
}

.bg-selector-preview {
  @apply w-12 h-12 rounded-md flex items-center justify-center;
  @apply bg-gray-100;
  overflow: hidden;
  flex-shrink: 0;
}

.bg-selector-card-selected .bg-selector-preview {
  @apply bg-primary-100;
}

.bg-selector-label {
  @apply text-xs font-sans text-gray-700;
  text-align: center;
}

.bg-selector-card-selected .bg-selector-label {
  @apply text-primary-600 font-semibold;
}
</style>
