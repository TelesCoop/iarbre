<script setup lang="ts">
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"
import { computed } from "vue"

const mapStore = useMapStore()

const selectedDataType = computed({
  get: () => mapStore.selectedDataType,
  set: (value: DataType) => mapStore.changeDataType(value)
})
</script>

<template>
  <div data-cy="layer-switcher">
    <label for="layer-select" class="font-accent">Choix du calque</label>
    <select
      id="layer-select"
      v-model="selectedDataType"
      class="w-full p-2 rounded border border-gray-300 bg-white text-base"
    >
      <option :value="DataType.PLANTABILITY">{{ DataTypeToLabel[DataType.PLANTABILITY] }}</option>
      <option :value="DataType.LOCAL_CLIMATE_ZONES">
        {{ DataTypeToLabel[DataType.LOCAL_CLIMATE_ZONES] }}
      </option>
      <option :value="DataType.VULNERABILITY">
        {{ DataTypeToLabel[DataType.VULNERABILITY] }}
      </option>
    </select>
  </div>
</template>
