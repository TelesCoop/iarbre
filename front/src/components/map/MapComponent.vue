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
  <div :id="mapId" data-cy="map-component" class="h-full w-full"></div>
  <map-legend />
  <map-sidebar />
  <div :id="`popup-${mapId}`" :style="{ display: mapStore.popupData ? 'block' : 'none' }">
    <map-score-popup
      v-if="mapStore.popupData"
      :score="mapStore.popupData.score"
      :lat="mapStore.popupData.lat"
      :lng="mapStore.popupData.lng"
    />
  </div>
</template>
