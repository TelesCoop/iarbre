<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { MapStyle, MapStyleToLabel } from "@/utils/enum"
import { computed } from "vue"

const mapStore = useMapStore()

const selectedMapStyle = computed({
  get: () => mapStore.selectedMapStyle,
  set: (value: MapStyle) => mapStore.changeMapStyle(value)
})

const options = [
  {
    label: MapStyleToLabel[MapStyle.OSM],
    value: MapStyle.OSM
  },
  {
    label: MapStyleToLabel[MapStyle.SATELLITE],
    value: MapStyle.SATELLITE
  }
]
</script>

<template>
  <Select
    v-model="selectedMapStyle"
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
  />
</template>
