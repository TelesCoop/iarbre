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
    aria-label="Copier les coordonnées"
    class="coordinates-button"
    :class="{ copied: isCopied }"
    data-cy="copy-coords-button"
    type="button"
    @click="handleCopyCoordinates"
  >
    <svg
      class="coordinates-icon"
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
    >
      <circle cx="12" cy="12" r="3" />
      <path d="M12 2v4m0 12v4M2 12h4m12 0h4" />
    </svg>
    <span class="coordinates-text">{{ formattedCoordinates }}</span>
    <span class="copy-indicator">
      <svg
        v-if="isCopied"
        class="check-icon"
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2.5"
      >
        <path d="M20 6L9 17l-5-5" />
      </svg>
      <IconCopy v-else :size="14" class="copy-icon" />
    </span>
  </button>
</template>

<style scoped>
.coordinates-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  font-family: inherit;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.coordinates-button:hover {
  border-color: #426a45;
  background: #f9fafb;
}

.coordinates-button:active {
  transform: scale(0.98);
}

.coordinates-button.copied {
  border-color: #22c55e;
  background: #f0fdf4;
}

.coordinates-icon {
  color: #426a45;
  flex-shrink: 0;
}

.coordinates-text {
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.01em;
}

.copy-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  margin-left: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.15s ease;
}

.coordinates-button:hover .copy-indicator {
  background: #edf5e9;
}

.copy-icon {
  color: #9ca3af;
  transition: color 0.15s ease;
}

.coordinates-button:hover .copy-icon {
  color: #426a45;
}

.check-icon {
  color: #22c55e;
  animation: checkPop 0.3s ease;
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
