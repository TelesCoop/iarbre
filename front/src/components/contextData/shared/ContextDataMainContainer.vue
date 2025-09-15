<script lang="ts" setup>
import { computed, withDefaults } from "vue"
import type { ContextDataMainContainerProps } from "@/types/contextData"
import MapContextHeader from "@/components/contextData/MapContextHeader.vue"
import EmptyMessage from "@/components/EmptyMessage.vue"

interface MainContainerProps extends ContextDataMainContainerProps {
  data?: any | null
  emptyMessage?: string
}

const props = withDefaults(defineProps<MainContainerProps>(), {
  data: null,
  emptyMessage: "Cliquez sur un carreau",
  fullHeight: false,
  hideCloseButton: false
})

const containerClasses = computed(() => {
  const baseClasses = "map-context-panel"
  return props.colorScheme === "plantability" ? `${baseClasses} item-center` : baseClasses
})

const ariaDescribedBy = computed(() => `${props.colorScheme}-description`)
const ariaLabelledBy = computed(() => `${props.colorScheme}-title`)
</script>

<template>
  <div
    :aria-describedby="ariaDescribedBy"
    :aria-labelledby="ariaLabelledBy"
    :class="containerClasses"
    role="dialog"
  >
    <map-context-header :description="description" />
    <div class="map-context-panel-content">
      <div v-if="data">
        <slot name="score" :data="data" />
        <slot name="content" :data="data" :full-height="fullHeight" />
        <slot name="legend" :data="data" />
      </div>
      <empty-message v-else data-cy="empty-message" :message="emptyMessage" />
    </div>
  </div>
</template>
