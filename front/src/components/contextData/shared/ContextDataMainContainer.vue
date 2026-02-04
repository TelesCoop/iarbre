<script lang="ts" setup>
import { computed, withDefaults } from "vue"
import type { ContextDataMainContainerProps } from "@/types/contextData"
import EmptyMessage from "@/components/EmptyMessage.vue"

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

const ariaDescribedBy = computed(() => `${props.colorScheme}-description`)
const ariaLabelledBy = computed(() => `${props.colorScheme}-title`)
</script>

<template>
  <div
    :aria-describedby="ariaDescribedBy"
    :aria-labelledby="ariaLabelledBy"
    :class="['context-panel', colorScheme === 'plantability' ? 'items-center' : '']"
    role="dialog"
  >
    <div class="panel-content">
      <div v-if="data" class="data-layout">
        <div class="score-section">
          <slot :data="data" name="score" />
        </div>

        <div class="content-section">
          <slot :data="data" :full-height="fullHeight" name="content" />
        </div>

        <div v-if="$slots.legend" class="legend-section">
          <slot :data="data" name="legend" />
        </div>
      </div>
      <EmptyMessage v-else-if="!hideEmptyMessage" :message="emptyMessage" data-cy="empty-message" />
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.context-panel {
  @apply bg-white w-full max-w-full transition-all duration-200;
}

.panel-content {
  @apply py-3 md:py-4 flex flex-col gap-4 md:gap-5 text-sm min-h-0;
}

.data-layout {
  @apply flex flex-col gap-4;
}

.score-section {
  @apply flex justify-center pb-3 border-b border-gray-100;
}

.content-section {
  @apply flex-1 min-h-0;
}

.legend-section {
  @apply pt-3 border-t border-gray-100;
}
</style>
