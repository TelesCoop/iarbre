<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { onMounted } from "vue"
import { useRouter, useRoute } from "vue-router"
import MapLegend from "@/components/map/legend/MapLegend.vue"
import MapScorePopup from "@/components/map/MapScorePopup.vue"
import MapSidebar from "@/components/map/sidebar/MapSidebar.vue"
import { Map } from "maplibre-gl"

const router = useRouter()
const route = useRoute()

const props = defineProps({
  mapId: {
    required: true,
    type: String
  }
})

const updateRouteCoords = (map: Map) => {
  const coords = map.getCenter()
  router.replace({
    name: "mapWithCoords",
    params: {
      zoom: Math.round(map.getZoom()),
      lng: Math.round(100000 * coords.lng) / 100000,
      lat: Math.round(100000 * coords.lat) / 100000
    }
  })
}

const mapStore = useMapStore()

onMounted(() => {
  mapStore.initMap(props.mapId)
  console.log("initMap", props.mapId)

  const mapInstance = mapStore.getMapInstance(props.mapId)
  if (route.name === "mapWithCoords") {
    const p = route.params
    mapInstance.jumpTo({
      center: [parseFloat(p.lng as string), parseFloat(p.lat as string)],
      zoom: parseFloat(p.zoom as string)
    })
  }

  mapInstance.on("moveend", () => updateRouteCoords(mapInstance))
  updateRouteCoords(mapInstance)
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
