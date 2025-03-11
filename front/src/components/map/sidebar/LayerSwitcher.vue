<script setup lang="ts">
import { useMapStore } from "@/stores/map"
import { LAYERS } from "@/utils/enum"
import { computed } from "vue"

const mapStore = useMapStore()

const selectedLayerValue = computed({
  get: () => mapStore.selectedLayer,
  set: (value: LAYERS) => {
    console.log("changeLayer 0.0")
    mapStore.changeLayer(value)
  }
})
</script>

<template>
  <div>
    <label for="layer-select" class="font-accent">Choix du calque</label>
    <select
      id="layer-select"
      v-model="selectedLayerValue"
      class="w-full p-2 rounded border border-gray-300 bg-white text-base"
    >
      <option value="plantability">Plantabilité</option>
      <option value="climate-zones">Zones Climatiques Locales</option>
    </select>
  </div>
</template>
