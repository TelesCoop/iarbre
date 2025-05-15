<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { computed } from "vue"
import { DataType } from "@/utils/enum"

const mapStore = useMapStore()
const show = computed(() => {
  return mapStore.tileDetails
})
</script>

<template>
  <div v-if="show" class="map-tool-container" data-cy="map-context-data">
    <map-context-data-plantability
      v-if="mapStore.selectedDataType === DataType.PLANTABILITY"
      :data="mapStore.tileDetails"
    />
  </div>
</template>

<style>
@reference "@/styles/main.css";
.context-map-data {
  @apply flex flex-col gap-2 w-full;
}
</style>
