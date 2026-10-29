import { describe, it, expect, beforeEach, vi } from "vitest"
import { setActivePinia, createPinia } from "pinia"
import { useMapRoute } from "@/composables/useMapRoute"
import { useMapStore } from "@/stores/map"
import { MapStyle } from "@/utils/enum"

vi.mock("maplibre-gl", () => ({ Map: class {}, NavigationControl: class {} }))

describe("useMapRoute", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it("targets the bare map route for the default display", () => {
    expect(useMapRoute().value).toEqual({ name: "map", query: {} })
  })

  it("carries the selected basemap and overlay layers", () => {
    const store = useMapStore()
    store.changeMapStyle(MapStyle.SATELLITE)
    store.toggleCadastreLayer()

    expect(useMapRoute().value).toEqual({
      name: "map",
      query: { basemap: "satellite", layers: "cadastre" }
    })
  })

  it("leaves out the filters, which belong to the data type being left", () => {
    const store = useMapStore()
    store.toggleFilter(2)

    expect(useMapRoute().value).toEqual({ name: "map", query: {} })
  })
})
