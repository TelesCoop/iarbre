<script lang="ts" setup>
import { computed } from "vue"
import { MapStyle } from "@/utils/enum"

interface Props {
  value: MapStyle
  label: string
  image: string
  selected: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  select: [value: MapStyle]
}>()

const cardClasses = computed(() => [
  "map-style-option",
  props.selected ? "map-style-option-selected" : ""
])

const handleSelect = () => {
  emit("select", props.value)
}
</script>

<template>
  <button
    :aria-selected="selected"
    :class="cardClasses"
    role="option"
    type="button"
    @click="handleSelect"
  >
    <div class="map-style-option-preview">
      <img :alt="label" :src="image" class="map-style-option-image" />
    </div>
    <span class="map-style-option-label">{{ label }}</span>
  </button>
</template>

<style scoped>
@reference "@/styles/main.css";

.map-style-option {
  @apply flex flex-col items-center justify-center gap-2 p-2 rounded-lg;
  @apply cursor-pointer transition-all;
  @apply border-2 border-transparent;
  @apply focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-300;
  background: transparent;
  min-width: 72px;
  height: 100%;
}

.map-style-option:hover {
  @apply bg-gray-50;
}

.map-style-option-selected {
  @apply bg-primary-50;
}

.map-style-option-preview {
  @apply w-12 h-12 rounded-md flex items-center justify-center;
  @apply bg-gray-100;
  overflow: hidden;
  flex-shrink: 0;
}

.map-style-option-selected .map-style-option-preview {
  @apply bg-primary-100;
}

.map-style-option-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.map-style-option-label {
  @apply text-xs font-sans text-gray-700;
  text-align: center;
}

.map-style-option-selected .map-style-option-label {
  @apply text-primary-600 font-semibold;
}
</style>
