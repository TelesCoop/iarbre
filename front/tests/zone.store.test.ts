import { beforeEach, describe, expect, test } from "vitest"
import { createPinia, setActivePinia } from "pinia"
import { useZoneStore, type ZonePolygon } from "@/stores/zone"

const POLYGON: ZonePolygon = {
  type: "Polygon",
  coordinates: [
    [
      [4.86, 45.8],
      [4.87, 45.8],
      [4.87, 45.81],
      [4.86, 45.8]
    ]
  ]
}

describe("zone store", () => {
  beforeEach(() => setActivePinia(createPinia()))

  test("starts empty", () => {
    expect(useZoneStore().drawnGeometry).toBeNull()
  })

  test("setZone stores the geometry", () => {
    const store = useZoneStore()
    store.setZone(POLYGON)
    expect(store.drawnGeometry).toEqual(POLYGON)
  })

  test("clearZone resets the geometry", () => {
    const store = useZoneStore()
    store.setZone(POLYGON)
    store.clearZone()
    expect(store.drawnGeometry).toBeNull()
  })
})
