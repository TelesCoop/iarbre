<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { MapType, MapTypeToLabel } from "@/utils/enum"
import { computed } from "vue"

const mapStore = useMapStore()

const selectedMapType = computed({
  get: () => mapStore.selectedMapType,
  set: (value: MapType) => mapStore.changeMapType(value)
})

const options = [
  {
    label: MapTypeToLabel[MapType.OSM],
    value: MapType.OSM
  },
  {
    label: MapTypeToLabel[MapType.SATELLITE],
    value: MapType.SATELLITE
  }
]
</script>

<template>
  <Select
    v-model="selectedMapType"
    :options="options"
    :pt="{
      root: 'text-sm',
      optionLabel: 'text-xs'
    }"
    class="w-full"
    data-cy="map-switcher"
    option-label="label"
    option-value="value"
    placeholder="Sélection de carte"
    show-clear
  />
</template>
