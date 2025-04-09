import { useRouter } from "vue-router"
import { useMapStore } from "@/stores/map"
import { Map } from "maplibre-gl"

export function updateMapRoute(
  router: ReturnType<typeof useRouter>,
  options: {
    map?: Map
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
    name: "mapWithCoords",
    params: {
      dataType: mapStore.selectedDataType,
      zoom,
      lat,
      lng
    }
  })
}
