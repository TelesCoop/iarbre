<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import VulnerabilityContextTool from "@/components/map/contextTools/VulnerabilityContextTool.vue"
import { computed } from "vue"

const mapStore = useMapStore()
const show = computed(() => {
  return mapStore.selectedDataType === DataType.VULNERABILITY
})
</script>

<template>
  <div
    v-if="show"
    class="rounded-md w-[23.75rem] bg-white p-4 border-primary-500 border-0.5 shadow-lg z-10 flex items-center gap-4"
    data-cy="map-context-tools"
  >
    <vulnerability-context-tool />
  </div>
</template>

<style>
@reference "@/styles/main.css";
.context-menu-tools {
  @apply flex flex-col gap-2 w-full;
}

.context-menu-tool {
  @apply flex items-center gap-2;
}

.context-menu-title {
  @apply text-primary-500 font-accent text-sm font-semibold;
}
</style>
