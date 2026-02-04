<script lang="ts" setup>
import { ref, watch, onUnmounted } from "vue"
import MaplibreGeocoder from "@maplibre/maplibre-gl-geocoder"
import { geocoderApi } from "@/utils/geocoder"
import { useMapStore } from "@/stores/map"
import maplibregl from "maplibre-gl"
import "@maplibre/maplibre-gl-geocoder/dist/maplibre-gl-geocoder.css"

const geocoderContainer = ref<HTMLDivElement>()
const mapStore = useMapStore()
let geocoderInstance: MaplibreGeocoder | null = null

const initGeocoder = (_mapInstance: maplibregl.Map) => {
  if (!geocoderContainer.value || geocoderInstance) {
    return
  }

  const geocoder = new MaplibreGeocoder(
    {
      forwardGeocode: geocoderApi.forwardGeocode
    },
    {
      maplibregl: maplibregl,
      marker: false,
      showResultsWhileTyping: true,
      countries: "FR",
      placeholder: "Recherche",
      clearOnBlur: true,
      collapsed: false,
      enableEventLogging: false
    }
  )

  geocoder.on("result", (e: any) => {
    if (e.result && e.result.center) {
      const currentMap = mapStore.getMapInstance("default")
      if (currentMap) {
        currentMap.flyTo({
          center: e.result.center,
          zoom: 14
        })
      }
    }
  })

  geocoder.addTo(geocoderContainer.value)
  geocoderInstance = geocoder
}

watch(
  [() => mapStore.mapInstancesByIds["default"], geocoderContainer],
  ([mapInstance, container]) => {
    if (mapInstance && container) {
      initGeocoder(mapInstance)
    }
  },
  { immediate: true }
)

onUnmounted(() => {
  geocoderInstance = null
})
</script>

<template>
  <div ref="geocoderContainer" style="width: 240px"></div>
</template>
