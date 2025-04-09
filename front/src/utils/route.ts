import { useRouter } from "vue-router"
import { useMapStore } from "@/stores/map"
import { Map } from "maplibre-gl"
import type { DataType } from "./enum"

export function updateMapRoute(
  router: ReturnType<typeof useRouter>,
  options: {
    map?: Map
    dataType?: DataType
  }
) {
  const mapStore = useMapStore()

  const route = router.currentRoute.value

  const { zoom, lat, lng } = options.map
    ? {
        zoom: Math.round(options.map.getZoom()),
        lat: Math.round(100000 * options.map.getCenter().lat) / 100000,
        lng: Math.round(100000 * options.map.getCenter().lng) / 100000
      }
    : {
        zoom: route.params.zoom,
        lat: route.params.lat,
        lng: route.params.lng
      }

  router.replace({
    name: "mapWithUrlParams",
    params: {
      dataType: options.dataType || mapStore.selectedDataType,
      zoom,
      lat,
      lng
    }
  })
}
