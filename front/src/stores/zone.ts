import { defineStore } from "pinia"
import { ref } from "vue"

export interface ZonePolygon {
  type: "Polygon"
  coordinates: [number, number][][]
}

export const useZoneStore = defineStore("zone", () => {
  const drawnGeometry = ref<ZonePolygon | null>(null)

  function setZone(geometry: ZonePolygon) {
    drawnGeometry.value = geometry
  }

  function clearZone() {
    drawnGeometry.value = null
  }

  return { drawnGeometry, setZone, clearZone }
})
