<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"
import { computed } from "vue"

const mapStore = useMapStore()

const isDataTypeSelected = (dataType: DataType) => {
  return mapStore.selectedDataTypes.has(dataType)
}

const toggleDataType = (dataType: DataType) => {
  mapStore.toggleDataType(dataType)
}

const options = [
  {
    label: DataTypeToLabel[DataType.PLANTABILITY],
    value: DataType.PLANTABILITY
  },
  {
    label: DataTypeToLabel[DataType.LOCAL_CLIMATE_ZONES],
    value: DataType.LOCAL_CLIMATE_ZONES
  },
  {
    label: DataTypeToLabel[DataType.VULNERABILITY],
    value: DataType.VULNERABILITY
  }
]
</script>

<template>
  <div class="layer-switcher" data-cy="layer-switcher">
    <div class="text-sm font-medium mb-2">Calques de données</div>
    <div class="space-y-2">
      <div v-for="option in options" :key="option.value" class="flex items-center">
        <Checkbox
          :model-value="isDataTypeSelected(option.value)"
          :binary="true"
          :input-id="option.value"
          class="mr-2"
          @update:model-value="toggleDataType(option.value)"
        />
        <label :for="option.value" class="text-xs cursor-pointer select-none">
          {{ option.label }}
        </label>
      </div>
    </div>
  </div>
</template>
