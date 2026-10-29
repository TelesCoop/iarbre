import { computed, type ComputedRef } from "vue"
import type { RouteLocationRaw } from "vue-router"
import { useMapStore } from "@/stores/map"
import { buildMapDisplayQuery } from "@/utils/mapUrlState"

/**
 * Route to the map that keeps the selected basemap, overlay layers and public building categories.
 * Filters are left out: the map reopens on the default data type.
 */
export function useMapRoute(): ComputedRef<RouteLocationRaw> {
  const mapStore = useMapStore()

  return computed(() => ({
    name: "map",
    query: buildMapDisplayQuery({
      filters: [],
      mapStyle: mapStore.selectedMapStyle,
      overlayLayers: mapStore.visibleOverlayLayers,
      publicBuildingCategories: mapStore.selectedPublicBuildingCategories
    })
  }))
}
