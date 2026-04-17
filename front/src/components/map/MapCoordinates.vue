<script lang="ts" setup>
import { computed, ref } from "vue"
import { useMapStore } from "@/stores/map"
import { copyToClipboard } from "@/utils/clipboard"
import { useToast } from "@/composables/useToast"

const mapStore = useMapStore()
const toast = useToast()
const isCopied = ref(false)

const formattedCoordinates = computed(() => {
  const { lat, lng } = mapStore.clickCoordinates
  return `${lat.toFixed(5)}° N, ${lng.toFixed(5)}° E`
})

const handleCopyCoordinates = async () => {
  await copyToClipboard(formattedCoordinates.value)
  isCopied.value = true
  toast.add({
    severity: "success",
    summary: "Coordonnées copiées",
    life: 3000,
    group: "br"
  })
  setTimeout(() => {
    isCopied.value = false
  }, 2000)
}
</script>

<template>
  <button
    :class="{ copied: isCopied }"
    aria-label="Copier les coordonnées"
    class="coordinates-button"
    data-cy="copy-coords-button"
    type="button"
    @click="handleCopyCoordinates"
  >
    <svg
      class="coordinates-icon"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      viewBox="0 0 24 24"
    >
      <circle cx="12" cy="12" r="3" />
      <path d="M12 2v4m0 12v4M2 12h4m12 0h4" />
    </svg>
    <span class="coordinates-text">{{ formattedCoordinates }}</span>
  </button>
</template>

<style scoped>
@reference "@/styles/main.css";

.coordinates-button {
  @apply inline-flex items-center;
  @apply gap-1.5 py-1.5 px-2;
  @apply bg-white border border-gray-200 rounded-lg;
  @apply font-sans text-2xs font-medium text-gray-500;
  @apply cursor-pointer transition-all;
  @apply min-w-0;
}

@media (min-width: 1024px) {
  .coordinates-button {
    @apply text-xs py-1.5 px-2.5;
  }
}

.coordinates-button:hover {
  @apply border-primary-500 bg-gray-50;
}

.coordinates-button:active {
  @apply scale-[0.98];
}

.coordinates-button.copied {
  @apply border-green-500 bg-green-50;
}

.coordinates-icon {
  @apply text-primary-500 shrink-0 w-2.5 h-2.5;
}

@media (min-width: 1024px) {
  .coordinates-icon {
    @apply w-3 h-3;
  }
}

.coordinates-text {
  @apply tabular-nums tracking-tight truncate min-w-0;
}
</style>
