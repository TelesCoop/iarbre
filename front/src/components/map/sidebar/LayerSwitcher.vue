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
    <label for="layer-select">Choix du calque</label>
    <select id="layer-select" v-model="selectedLayerValue" class="layer-select">
      <option value="plantability">Plantabilité</option>
      <option value="climate-zones">Zones Climatiques Locales</option>
    </select>
  </div>
</template>

<style lang="sass" scoped>
.layer-select
  width: 100%
  padding: 0.5rem
  border-radius: 0.25rem
  border: 0.0625rem solid #ccc
  background-color: white
  font-size: 1rem
label
  font-family: $accent-font
</style>
