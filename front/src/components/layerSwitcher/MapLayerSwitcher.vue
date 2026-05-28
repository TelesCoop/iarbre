<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { DataTypeToDocumentationUrl } from "@/utils/enum"

interface Props {
  withBorder?: boolean
  showContextTools?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  withBorder: true,
  showContextTools: true
})

const mapStore = useMapStore()

const documentationUrl = computed(() => DataTypeToDocumentationUrl[mapStore.selectedDataType])
</script>

<template>
  <div
    :class="['layer-switcher-stack', { 'map-tool-container': props.withBorder }]"
    data-cy="map-layer-switcher"
  >
    <LayerSwitcher />
    <a
      :href="documentationUrl"
      class="methodology-link"
      target="_blank"
      rel="noopener external"
      title="Documentation sur la méthodologie - nouvelle fenêtre"
    >
      Voir la méthodologie
    </a>
    <MapContextTools v-if="props.showContextTools" />
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.methodology-link {
  @apply self-start text-xs font-medium text-gray-600 underline underline-offset-4;
  @apply transition-colors duration-200 hover:text-primary-700;
}

.layer-switcher-stack {
  @apply flex flex-col gap-2 w-full;
}
</style>
