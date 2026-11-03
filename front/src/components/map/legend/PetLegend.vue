<script lang="ts" setup>
import { computed } from "vue"
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"
import { PET_LEGEND, formatHour } from "@/utils/pet"
import LegendItem from "@/components/map/legend/LegendItem.vue"

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
    <div class="strate-list" role="list">
      <div
        v-for="item in PET_LEGEND"
        :key="item.value"
        class="strate-item"
        role="listitem"
        :title="item.detail"
      >
        <LegendItem :label="item.label" :color="item.color" />
      </div>
    </div>
  </div>
</template>
