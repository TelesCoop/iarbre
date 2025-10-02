<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"
import { computed } from "vue"

const mapStore = useMapStore()

const selectedDataType = computed({
  get: () => mapStore.selectedDataType,
  set: (value: DataType) => mapStore.changeDataType(value)
})

const options = [
  {
    label: DataTypeToLabel[DataType.PLANTABILITY],
    value: DataType.PLANTABILITY
  },
  {
    label: DataTypeToLabel[DataType.VULNERABILITY],
    value: DataType.VULNERABILITY
  },
  {
    label: DataTypeToLabel[DataType.CLIMATE_ZONE],
    value: DataType.CLIMATE_ZONE
  },
  {
    label: DataTypeToLabel[DataType.PLANT_VULNERABILITY],
    value: DataType.PLANT_VULNERABILITY
  }
]
</script>

<template>
  <Select
    v-model="selectedDataType"
    :options="options"
    :pt="{
      root: 'text-sm',
      optionLabel: 'text-xs'
    }"
    class="w-full"
    data-cy="layer-switcher"
    option-label="label"
    option-value="value"
    placeholder="Sélection de calque"
  />
</template>
