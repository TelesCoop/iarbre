<script lang="ts" setup>
import { onMounted, ref } from "vue"
import MaplibreGeocoder from "@maplibre/maplibre-gl-geocoder"
import { geocoderApi } from "@/utils/geocoder"
import { useMapStore } from "@/stores/map"
import maplibregl from "maplibre-gl"
import "@maplibre/maplibre-gl-geocoder/dist/maplibre-gl-geocoder.css"

const geocoderContainer = ref<HTMLDivElement>()
const mapStore = useMapStore()

onMounted(() => {
  if (geocoderContainer.value) {
    const mapInstance = mapStore.getMapInstance("map")
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
        mapInstance.flyTo({
          center: e.result.center,
          zoom: 14
        })
      }
    })

    geocoder.addTo(geocoderContainer.value)
  }
})
</script>

<template>
  <div ref="geocoderContainer" style="width: 240px"></div>
</template>
