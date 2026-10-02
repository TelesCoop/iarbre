import { describe, it, expect, beforeEach, vi } from "vitest"
import { setActivePinia, createPinia } from "pinia"
import type { PanoramaxPicture } from "maplibre-gl-panoramax"
import { useMapStore } from "@/stores/map"
import { getQPVData } from "@/services/qpvService"
import { DataType, MapStyle } from "@/utils/enum"

const createdMaps = vi.hoisted(() => [] as { sources: Set<string>; layers: Set<string> }[])

vi.mock("maplibre-gl", () => ({
  Map: class {
    sources = new Set<string>()
    layers = new Set<string>()

    constructor() {
      createdMaps.push(this)
    }

    isStyleLoaded = () => false
    once = () => undefined
    on = () => undefined
    getSource = (id: string) => (this.sources.has(id) ? {} : undefined)
    addSource = (id: string) => {
      if (this.sources.has(id)) throw new Error(`Source "${id}" already exists.`)
      this.sources.add(id)
    }
    removeSource = (id: string) => this.sources.delete(id)
    getLayer = (id: string) => (this.layers.has(id) ? {} : undefined)
    addLayer = ({ id }: { id: string }) => this.layers.add(id)
    removeLayer = (id: string) => this.layers.delete(id)
  },
  NavigationControl: class {}
}))
vi.mock("@/services/qpvService", () => ({ getQPVData: vi.fn() }))

const DEFAULT_DISPLAY = { filters: [], mapStyle: MapStyle.OSM, overlayLayers: [] }

describe("map store display state", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    createdMaps.length = 0
  })

  it("initMap resets the filters and selections left by a previous visit", () => {
    const store = useMapStore()
    store.toggleFilter(2)
    store.toggleCadastreLayer()
    store.selectedCadastreParcel = { parcelId: "1", section: "AB", numero: "12", surface: null }
    store.selectedPanoramaxPicture = { id: "picture" } as PanoramaxPicture

    store.initMap("default", DataType.PLANTABILITY, DEFAULT_DISPLAY)

    expect(store.filteredValues).toEqual([])
    expect(store.visibleOverlayLayers).toEqual([])
    expect(store.selectedCadastreParcel).toBeNull()
    expect(store.selectedPanoramaxPicture).toBeNull()
  })

  describe("QPV layer loading", () => {
    let resolveData: (data: GeoJSON.FeatureCollection) => void

    beforeEach(() => {
      vi.mocked(getQPVData).mockReturnValue(
        new Promise((resolve) => {
          resolveData = resolve
        })
      )
    })

    it("does not add the layer when it is toggled off while its data loads", async () => {
      const store = useMapStore()
      store.initMap("default", DataType.PLANTABILITY, DEFAULT_DISPLAY)

      const toggledOn = store.toggleQPVLayer()
      await store.toggleQPVLayer()
      resolveData({ type: "FeatureCollection", features: [] })
      await toggledOn

      expect(createdMaps[0].layers.has("qpv-border")).toBe(false)
    })

    it("adds the source once when two loads overlap", async () => {
      const store = useMapStore()
      store.initMap("default", DataType.PLANTABILITY, DEFAULT_DISPLAY)

      const firstToggledOn = store.toggleQPVLayer()
      await store.toggleQPVLayer()
      const secondToggledOn = store.toggleQPVLayer()
      resolveData({ type: "FeatureCollection", features: [] })
      await Promise.all([firstToggledOn, secondToggledOn])

      expect(createdMaps[0].layers.has("qpv-border")).toBe(true)
    })
  })
})
