<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { onMounted } from "vue"
import MapPlantabilityLegend from "@/components/map/MapPlantabilityLegend.vue"
import MapScorePopup from "@/components/map/MapScorePopup.vue"

const props = defineProps({
  mapId: {
    required: true,
    type: String
  }
})

const mapStore = useMapStore()

onMounted(() => {
  mapStore.initMap(props.mapId)
  console.log("initMap", props.mapId)
})
</script>

<template>
  <div :id="mapId" data-cy="map-component" class="map-component"></div>
  <map-plantability-legend />
  <div :id="`popup-${mapId}`" style="{ 'hidden': true }">
    <map-score-popup
      v-if="mapStore.popup"
      :score="mapStore.popup.score"
      :lat="mapStore.popup.lat"
      :lng="mapStore.popup.lng"
    />
  </div>
</template>

<style lang="sass" scoped>
.map-component
  height: 100%
  width: 100%
</style>
