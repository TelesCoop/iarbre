<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import VulnerabilityContextTool from "@/components/contextTools/VulnerabilityContextTool.vue"
import { computed } from "vue"

const mapStore = useMapStore()
const show = computed(() => {
  return mapStore.selectedDataType === DataType.VULNERABILITY
})
</script>

<template>
  <div v-if="show" class="map-tool-container" data-cy="map-context-tools">
    <vulnerability-context-tool />
  </div>
</template>

<style>
@reference "@/styles/main.css";
.context-menu-tools {
  @apply flex flex-col gap-2 w-full;
  @apply p-2 md:p-4;
}

.context-menu-tool {
  @apply flex items-center gap-2;
}

.context-menu-title {
  @apply text-primary-500 font-accent text-sm font-semibold;
}
</style>
