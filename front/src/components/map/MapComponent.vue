<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { onMounted } from "vue"
import MapLegend from "@/components/map/legend/MapLegend.vue"
import MapScorePopup from "@/components/map/MapScorePopup.vue"
import MapSidebar from "@/components/map/sidebar/MapSidebar.vue"

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
  <map-legend />
  <map-sidebar />
  <div :id="`popup-${mapId}`" :style="{ display: mapStore.popup ? 'block' : 'none' }">
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
