<template>
  <div class="map-sidebar">
    <div class="card">
      <select v-model="selectedLayerValue" class="layer-select">
        <option value="plantability">Plantabilité</option>
        <option value="climate-zones">Zones Climatiques Locales</option>
      </select>
    </div>
  </div>
</template>

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

<style lang="sass" scoped>
.map-sidebar
  position: absolute
  top: 0
  left: 0
  max-width: 18.75rem
  background-color: transparent
  padding: 1rem

.layer-select
  width: 100%
  padding: 0.5rem
  border-radius: 0.25rem
  border: 0.0625rem solid #ccc
  background-color: white
  font-size: 1rem
</style>
