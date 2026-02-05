<script lang="ts" setup>
import { ref, computed } from "vue"
import { useMapStore } from "@/stores/map"
import { MapStyle } from "@/utils/enum"

interface MapStyleOption {
  value: MapStyle
  label: string
  image: string
}

const mapStore = useMapStore()
const isExpanded = ref(false)

const options: MapStyleOption[] = [
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

const currentStyle = computed(() => mapStore.selectedMapStyle)

const currentOption = computed(
  () => options.find((opt) => opt.value === currentStyle.value) ?? options[0]
)

const isSelected = (style: MapStyle): boolean => currentStyle.value === style

const handleSelectStyle = (style: MapStyle) => {
  mapStore.changeMapStyle(style)
  isExpanded.value = false
}

const handleToggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === "Escape" && isExpanded.value) {
    isExpanded.value = false
  }
}
</script>

<template>
  <div class="bg-selector-wrapper" @keydown="handleKeydown">
    <div :class="['bg-selector-container', { expanded: isExpanded }]">
      <button
        :aria-expanded="isExpanded"
        aria-controls="bg-selector-options"
        aria-label="Sélectionner le fond de carte"
        class="bg-selector-toggle"
        data-cy="bg-selector-toggle"
        type="button"
        @click="handleToggleExpanded"
      >
        <div class="bg-selector-toggle-preview">
          <img :alt="currentOption.label" :src="currentOption.image" class="preview-image" />
        </div>
        <span class="bg-selector-toggle-label">{{ currentOption.label }}</span>
      </button>

      <div
        id="bg-selector-options"
        :class="['bg-selector-options', { 'is-expanded': isExpanded }]"
        aria-label="Options de fond de carte"
        role="listbox"
      >
        <MapStyleOption
          v-for="option in options"
          :key="option.value"
          :data-cy="`bg-option-${option.value}`"
          :image="option.image"
          :label="option.label"
          :selected="isSelected(option.value)"
          :value="option.value"
          @select="handleSelectStyle"
        />
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
  @apply bg-white rounded-lg;
  @apply border border-gray-200;
  padding: 10px;
  height: 90px;
}

.bg-selector-toggle {
  @apply flex flex-col items-center gap-2;
  @apply cursor-pointer transition-all;
  @apply hover:bg-gray-50 rounded-lg;
  @apply focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-300;
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
  @apply text-xs font-sans text-gray-700 font-medium;
}

@media (min-width: 1024px) {
  .bg-selector-toggle-label {
    @apply text-sm;
  }
}

.bg-selector-options {
  @apply flex items-center gap-2 pl-2 ml-2;
  @apply border-l border-gray-200;
  @apply transition-all duration-300 ease-out;
  height: 100%;
  max-width: 0;
  opacity: 0;
  overflow: hidden;
  padding-left: 0;
  margin-left: 0;
  border-left-width: 0;
}

.bg-selector-options.is-expanded {
  max-width: 300px;
  opacity: 1;
  padding-left: 0.5rem;
  margin-left: 0.5rem;
  border-left-width: 1px;
}
</style>
