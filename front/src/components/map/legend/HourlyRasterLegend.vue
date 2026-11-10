<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { DataTypeToLabel } from "@/utils/enum"
import { HOURLY_RASTERS, formatHour } from "@/utils/hourlyRaster"

const mapStore = useMapStore()

const raster = computed(() => HOURLY_RASTERS[mapStore.selectedDataType]!)

const title = computed(() =>
  [
    DataTypeToLabel[mapStore.selectedDataType],
    ...(raster.value.years ? [mapStore.rasterYear] : []),
    formatHour(mapStore.rasterHour)
  ].join(" - ")
)
</script>

<template>
  <div class="flex flex-col items-center gap-1 lg:gap-2 font-sans" data-cy="hourly-raster-legend">
    <div class="legend-header">
      <span class="legend-title">{{ title }}</span>
    </div>
    <div class="legend-content">
      <div class="legend-label">
        <span class="legend-axis-indicator">−</span>
        <span class="legend-axis-text">{{ raster.axisLabels[0] }}</span>
      </div>
      <div class="legend-scale" role="list">
        <ScoreLabel
          v-for="(item, index) in raster.classes"
          :key="item.value"
          :background-color="item.color"
          :class="[
            index === 0 ? 'rounded-l' : '',
            index === raster.classes.length - 1 ? 'rounded-r' : '',
            mapStore.isFiltered(item.value) ? 'z-10 relative' : ''
          ]"
          :clickable="true"
          :is-selected="mapStore.isFiltered(item.value)"
          :label="item.label"
          :score="item.value"
          :title="`${item.label} : ${item.detail} - Cliquez pour ${mapStore.isFiltered(item.value) ? 'désactiver' : 'activer'} le filtre`"
          role="listitem"
          @click="mapStore.toggleAndApplyFilter"
        />
      </div>
      <div class="legend-label">
        <span class="legend-axis-text">{{ raster.axisLabels[1] }}</span>
        <span class="legend-axis-indicator">+</span>
      </div>
    </div>
  </div>
</template>
