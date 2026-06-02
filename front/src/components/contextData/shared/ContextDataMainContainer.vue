<script lang="ts" setup>
import { computed } from "vue"
import type { ContextDataMainContainerProps } from "@/types/contextData"
import EmptyMessage from "@/components/EmptyMessage.vue"
import AppButton from "@/components/shared/AppButton.vue"
import IconInfo from "@/components/icons/IconInfo.vue"
import { useMapStore } from "@/stores/map"
import { DataTypeToDocumentationUrl } from "@/utils/enum"

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

const mapStore = useMapStore()

const documentationUrl = computed(() => DataTypeToDocumentationUrl[mapStore.selectedDataType])

const openMethodology = () => {
  window.open(documentationUrl.value, "_blank", "noopener,noreferrer")
}
</script>

<template>
  <div
    :aria-describedby="ariaDescribedBy"
    :aria-labelledby="ariaLabelledBy"
    :class="['context-panel', colorScheme === 'plantability' ? 'items-center' : '']"
    role="dialog"
  >
    <div class="panel-content">
      <div class="panel-methodology">
        <AppButton
          class="methodology-button"
          data-cy="methodology-button"
          size="sm"
          title="Documentation sur la méthodologie - nouvelle fenêtre"
          variant="primary"
          @click="openMethodology"
        >
          <template #icon-left>
            <IconInfo :size="14" aria-hidden="true" />
          </template>
          Voir la méthodologie
        </AppButton>
      </div>

      <div v-if="data" class="data-layout">
        <div v-if="$slots.score" class="score-section">
          <slot :data="data" name="score" />
        </div>

        <div class="content-section">
          <slot :data="data" :full-height="fullHeight" name="content" />
          <div v-if="$slots.legend" class="legend-section">
            <slot :data="data" name="legend" />
          </div>
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
  @apply flex flex-col min-h-0 flex-1;
}

.panel-content {
  @apply py-3 md:py-4 flex flex-col gap-4 md:gap-5 text-sm min-h-0 flex-1 w-full;
}

.panel-methodology {
  @apply flex justify-end;
}

.methodology-button {
  @apply px-2.5 py-1 text-xs gap-1 whitespace-nowrap;
  @apply bg-primary-900 border-primary-900 text-white;
  @apply hover:bg-primary-800 hover:border-primary-800;
}

.data-layout {
  @apply flex flex-col items-center gap-4 min-h-0 flex-1 w-full;
}

.score-section {
  @apply flex shrink-0 flex-wrap items-center justify-center gap-4 lg:gap-8;
  @apply w-full pb-3 border-b border-gray-100;
}

.content-section {
  @apply flex-1 min-h-0 flex flex-col overflow-y-auto;
  @apply w-full;
}
</style>
