<script lang="ts" setup>
import { computed, withDefaults } from "vue"
import type { ContextDataMainContainerProps } from "@/types/contextData"
import MapContextHeader from "@/components/contextData/MapContextHeader.vue"
import EmptyMessage from "@/components/EmptyMessage.vue"
import { ZoomToGridSize } from "@/utils/plantability"

interface MainContainerProps extends ContextDataMainContainerProps {
  data?: any | null
  emptyMessage?: string
  zoomLevel?: number | null
  hideDescription?: boolean
  hideEmptyMessage?: boolean
}

const props = withDefaults(defineProps<MainContainerProps>(), {
  data: null,
  emptyMessage: "Cliquez sur un carreau",
  fullHeight: false,
  hideCloseButton: false,
  zoomLevel: null,
  hideDescription: false,
  hideEmptyMessage: false
})

const containerClasses = computed(() => {
  const baseClasses = "map-context-panel"
  return props.colorScheme === "plantability" ? `${baseClasses} item-center` : baseClasses
})

const ariaDescribedBy = computed(() => `${props.colorScheme}-description`)
const ariaLabelledBy = computed(() => `${props.colorScheme}-title`)

const gridSize = computed(() => {
  if (props.zoomLevel) {
    const zoom = Math.floor(props.zoomLevel)
    return ZoomToGridSize[zoom] ?? null
  }
  return null
})
</script>

<template>
  <div
    :aria-describedby="ariaDescribedBy"
    :aria-labelledby="ariaLabelledBy"
    :class="containerClasses"
    role="dialog"
  >
    <map-context-header v-if="!hideDescription" :description="description" :title="title" />
    <div v-if="gridSize && title === 'plantability'" class="mt-2 text-sm text-center font-sans">
      Taille d'un carreau: {{ gridSize }}m <span class="text-xs">(précision maximum de 5m).</span>
    </div>
    <div class="map-context-panel-content">
      <div v-if="data">
        <slot name="score" :data="data" />
        <slot name="content" :data="data" :full-height="fullHeight" />
        <slot name="legend" :data="data" />
      </div>
      <empty-message
        v-else-if="!hideEmptyMessage"
        data-cy="empty-message"
        :message="emptyMessage"
      />
    </div>
  </div>
</template>
