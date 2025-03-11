<script setup lang="ts">
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"
import { computed } from "vue"

const mapStore = useMapStore()

const selectedDataType = computed({
  get: () => mapStore.selectedDataType,
  set: (value: DataType) => {
    console.log("changeLayer 0.0")
    mapStore.changeDataType(value)
  }
})
</script>

<template>
  <div>
    <label for="layer-select" class="font-accent">Choix du calque</label>
    <select
      id="layer-select"
      v-model="selectedDataType"
      class="w-full p-2 rounded border border-gray-300 bg-white text-base"
    >
      <option value="plantability">Plantabilité</option>
      <option value="lcz">Zones Climatiques Locales</option>
    </select>
  </div>
</template>
