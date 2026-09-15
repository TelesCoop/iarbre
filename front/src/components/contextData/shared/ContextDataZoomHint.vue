<script lang="ts" setup>
import { computed } from "vue"
import AppButton from "@/components/shared/AppButton.vue"
import { useMapStore } from "@/stores/map"

interface ContextDataZoomHintProps {
  /** "in" reveals finer detail, "out" reveals the wider distribution */
  direction: "in" | "out"
  message: string
  targetZoom: number
  label?: string
}

const props = withDefaults(defineProps<ContextDataZoomHintProps>(), {
  label: undefined
})

const mapStore = useMapStore()

const buttonLabel = computed(
  () => props.label ?? (props.direction === "in" ? "Zoomer" : "Dézoomer")
)
const dataCy = computed(() => (props.direction === "in" ? "zoom-hint" : "zoom-out-hint"))

const applyZoom = () => mapStore.zoomTo(props.targetZoom)
</script>

<template>
  <div :data-cy="dataCy" class="zoom-hint" role="status">
    <span class="zoom-hint-icon" aria-hidden="true">
      <svg
        fill="none"
        height="12"
        stroke="currentColor"
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        viewBox="0 0 24 24"
        width="12"
      >
        <circle cx="11" cy="11" r="7" />
        <line x1="21" x2="16.65" y1="21" y2="16.65" />
        <line x1="8" x2="14" y1="11" y2="11" />
        <line v-if="direction === 'in'" x1="11" x2="11" y1="8" y2="14" />
      </svg>
    </span>
    <p class="zoom-hint-text">{{ message }}</p>
    <AppButton
      :data-cy="`${dataCy}-button`"
      class="zoom-hint-button"
      size="sm"
      :variant="direction === 'in' ? 'primary' : 'outline'"
      @click="applyZoom"
    >
      {{ buttonLabel }}
    </AppButton>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.zoom-hint {
  @apply flex items-center gap-2 mt-2 px-2 py-1.5;
  @apply rounded-md border border-primary-100 bg-primary-50;
}

.zoom-hint-icon {
  @apply flex items-center justify-center shrink-0;
  @apply w-5 h-5 rounded-full bg-white text-primary-500;
}

.zoom-hint-text {
  @apply flex-1 leading-tight text-primary-900;
  @apply text-xs lg:text-sm;
}

.zoom-hint-button {
  @apply shrink-0 px-2 py-0.5 gap-1;
  @apply text-2xs lg:text-xs;
}
</style>
