<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"
import { PET_LEGEND, formatHour } from "@/utils/pet"

const mapStore = useMapStore()

const title = computed(
  () => `${DataTypeToLabel[DataType.PET]} - ${mapStore.petYear} - ${formatHour(mapStore.petHour)}`
)
</script>

<template>
  <div class="flex flex-col items-center gap-1 lg:gap-2 font-sans" data-cy="pet-legend">
    <div class="legend-header">
      <span class="legend-title">{{ title }}</span>
    </div>
    <div class="legend-content">
      <div class="legend-label">
        <span class="legend-axis-indicator">−</span>
        <span class="legend-axis-text">Frais</span>
      </div>
      <div class="legend-scale" role="list">
        <ScoreLabel
          v-for="(item, index) in PET_LEGEND"
          :key="item.value"
          :background-color="item.color"
          :class="[
            index === 0 ? 'rounded-l' : '',
            index === PET_LEGEND.length - 1 ? 'rounded-r' : '',
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
        <span class="legend-axis-text">Chaud</span>
        <span class="legend-axis-indicator">+</span>
      </div>
    </div>
  </div>
</template>
