<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToLabel } from "@/utils/enum"
import { computed } from "vue"
import { updateMapRoute } from "@/utils/route"
import { useRouter } from "vue-router"
import Select from "primevue/select"

const mapStore = useMapStore()
const router = useRouter()

const selectedDataType = computed({
  get: () => mapStore.selectedDataType,
  set: (value: DataType) => {
    mapStore.changeDataType(value)
    updateMapRoute(router, { dataType: mapStore.selectedDataType })
  }
})

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
  <Select
    v-model="selectedDataType"
    :options="options"
    class="w-full"
    data-cy="layer-switcher"
    option-label="label"
    option-value="value"
    placeholder="Sélection de calque"
    show-clear
  />
</template>
