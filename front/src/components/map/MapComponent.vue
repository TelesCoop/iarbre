<script lang="ts" setup>
import { useMapStore } from "@/stores/map"
import { onMounted } from "vue"
import { useRouter, useRoute } from "vue-router"
import MapLegend from "@/components/map/legend/MapLegend.vue"
import MapScorePopup from "@/components/map/popup/MapScorePopup.vue"
import MapLayerSwitcher from "@/components/map/layerSwitcher/MapLayerSwitcher.vue"
import { updateMapRoute } from "@/utils/route"
import { DataType } from "@/utils/enum"

const router = useRouter()
const route = useRoute()

const props = defineProps({
  mapId: {
    required: true,
    type: String
  }
})

const mapStore = useMapStore()

onMounted(() => {
  mapStore.initMap(props.mapId)

  if (route) {
    const mapInstance = mapStore.getMapInstance(props.mapId)
    if (route.name === "mapWithUrlParams") {
      const p = route.params
      mapInstance.jumpTo({
        center: [parseFloat(p.lng as string), parseFloat(p.lat as string)],
        zoom: parseFloat(p.zoom as string)
      })
      mapInstance.on("load", () => {
        mapStore.changeDataType(p.dataType as DataType)
      })
    }

    mapInstance.on("moveend", () => {
      updateMapRoute(router, { map: mapInstance })
    })
    updateMapRoute(router, { map: mapInstance })
  }
})
</script>

<template>
  <div :id="mapId" class="h-full w-full" data-cy="map-component"></div>
  <map-legend />
  <map-layer-switcher />
  <div :id="`popup-${mapId}`" :style="{ display: mapStore.popupData ? 'block' : 'none' }">
    <map-score-popup v-if="mapStore.popupData" :popup-data="mapStore.popupData" />
  </div>
</template>
