<script lang="ts" setup>
import { computed, ref } from "vue"
import { useMapStore } from "@/stores/map"
import { copyToClipboard } from "@/utils/clipboard"
import { useToast } from "@/composables/useToast"
import IconCopy from "@/components/shared/icons/IconCopy.vue"

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
    <span class="copy-indicator">
      <svg
        v-if="isCopied"
        class="check-icon"
        fill="none"
        stroke="currentColor"
        stroke-width="2.5"
        viewBox="0 0 24 24"
      >
        <path d="M20 6L9 17l-5-5" />
      </svg>
      <IconCopy v-else class="copy-icon" />
    </span>
  </button>
</template>

<style scoped>
@reference "@/styles/main.css";

.coordinates-button {
  @apply flex items-center justify-between w-full;
  @apply gap-1 py-1.5 px-2;
  @apply bg-white border border-gray-200 rounded-lg;
  @apply font-sans text-xs font-medium text-gray-500;
  @apply cursor-pointer transition-all;
}

@media (min-width: 1024px) {
  .coordinates-button {
    @apply w-auto gap-2 py-2 px-3 text-sm justify-start;
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
    @apply w-3.5 h-3.5;
  }
}

.coordinates-text {
  @apply tabular-nums tracking-tight;
}

.copy-indicator {
  @apply flex items-center justify-center shrink-0;
  @apply w-5 h-5 ml-0.5 rounded;
  @apply transition-all;
}

@media (min-width: 1024px) {
  .copy-indicator {
    @apply w-8 h-8 ml-1;
  }
}

.coordinates-button:hover .copy-indicator {
  @apply bg-primary-100;
}

.copy-icon {
  @apply text-gray-400 transition-colors w-4 h-4;
}

@media (min-width: 1024px) {
  .copy-icon {
    @apply w-8 h-8;
  }
}

.coordinates-button:hover .copy-icon {
  @apply text-primary-500;
}

.check-icon {
  @apply text-green-500 w-4 h-4;
  animation: checkPop 0.3s ease;
}

@media (min-width: 1024px) {
  .check-icon {
    @apply w-7 h-7;
  }
}

@keyframes checkPop {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
