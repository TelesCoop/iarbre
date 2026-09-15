import { onBeforeUnmount, onMounted, watch, type ComputedRef } from "vue"
import type { Map } from "maplibre-gl"
import { useMapStore } from "@/stores/map"

/**
 * Keeps a screen-space anchor in sync with the map's current shape drawing:
 * re-attaches the map "render" listener whenever the map instance changes,
 * and refreshes derived state whenever the drawing state or live area changes.
 */
export function useMapRenderSync(
  mapInstance: ComputedRef<Map | null>,
  reproject: () => void,
  refresh: () => void
) {
  const mapStore = useMapStore()

  let attached = false
  const attach = () => {
    const map = mapInstance.value
    if (!map || attached) return
    map.on("render", reproject)
    attached = true
    refresh()
  }

  onMounted(attach)
  watch(mapInstance, attach)
  watch(() => [mapStore.drawingState, mapStore.liveArea], refresh)

  onBeforeUnmount(() => {
    const map = mapInstance.value
    if (map && attached) map.off("render", reproject)
    attached = false
  })
}
