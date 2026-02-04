<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"
import { computed } from "vue"
import AppSelect from "@/components/shared/AppSelect.vue"

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
    label: DataTypeToLabel[DataType.PLANTABILITY_VULNERABILITY],
    value: DataType.PLANTABILITY_VULNERABILITY
  },
  {
    label: DataTypeToLabel[DataType.VEGETATION],
    value: DataType.VEGETATION
  }
]
</script>

<template>
  <AppSelect
    v-model="selectedDataType"
    :options="options"
    class="w-full"
    data-cy="layer-switcher"
    option-label="label"
    option-value="value"
    placeholder="Sélection de calque"
  />
</template>
