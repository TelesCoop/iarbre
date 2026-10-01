import { describe, it, expect, beforeEach, vi } from "vitest"
import { setActivePinia, createPinia } from "pinia"
import type { PanoramaxPicture } from "maplibre-gl-panoramax"
import { useMapStore } from "@/stores/map"
import { getQPVData } from "@/services/qpvService"
import { getCityBoundaries } from "@/services/boundaryService"
import { DataType, MapStyle, OverlayLayer } from "@/utils/enum"
import type { MapDisplayState } from "@/types/map"

interface FakeMap {
  options: { style: { sources: object } }
  sources: Set<string>
  layers: Set<string>
}

const createdMaps = vi.hoisted(() => [] as FakeMap[])

vi.mock("maplibre-gl", () => ({
  Map: class implements FakeMap {
    sources = new Set<string>()
    layers = new Set<string>()

    constructor(public options: FakeMap["options"]) {
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
vi.mock("@/services/boundaryService", () => ({ getCityBoundaries: vi.fn() }))

const EMPTY_FEATURE_COLLECTION: GeoJSON.FeatureCollection = {
  type: "FeatureCollection",
  features: []
}

const displayState = (overrides: Partial<MapDisplayState> = {}): MapDisplayState => ({
  filters: [],
  mapStyle: MapStyle.OSM,
  overlayLayers: [],
  ...overrides
})

const initStoreWithMap = (overrides: Partial<MapDisplayState> = {}) => {
  const store = useMapStore()
  store.initMap("default", DataType.PLANTABILITY, displayState(overrides))
  return { store, map: createdMaps[createdMaps.length - 1] }
}

describe("map store display state", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    createdMaps.length = 0
  })

  it("lists no overlay layer by default", () => {
    const store = useMapStore()

    expect(store.visibleOverlayLayers).toEqual([])
  })

  it("lists the toggled overlay layers", () => {
    const store = useMapStore()

    store.togglePanoramaxLayer()
    store.toggleQPVLayer()

    expect(store.visibleOverlayLayers).toEqual([OverlayLayer.QPV, OverlayLayer.PANORAMAX])
  })

  it("initMap restores the basemap", () => {
    const { store, map } = initStoreWithMap({ mapStyle: MapStyle.SATELLITE })

    expect(store.selectedMapStyle).toBe(MapStyle.SATELLITE)
    expect(Object.keys(map.options.style.sources)).toEqual([MapStyle.SATELLITE])
  })

  it("initMap restores the overlay layers", () => {
    const { store } = initStoreWithMap({
      overlayLayers: [OverlayLayer.QPV, OverlayLayer.BOUNDARY]
    })

    expect(store.showQPVLayer).toBe(true)
    expect(store.showBoundaryLayer).toBe(true)
    expect(store.showCadastreLayer).toBe(false)
    expect(store.showPanoramaxLayer).toBe(false)
  })

  it("initMap hides the overlay layers missing from the display state", () => {
    const store = useMapStore()
    store.toggleCadastreLayer()

    store.initMap("default", DataType.PLANTABILITY, displayState())

    expect(store.visibleOverlayLayers).toEqual([])
  })

  it("initMap restores the filters", () => {
    const { store } = initStoreWithMap({ filters: [2, 4] })

    expect(store.filteredValues).toEqual([2, 4])
  })

  it("initMap clears the filters missing from the display state", () => {
    const store = useMapStore()
    store.toggleFilter(2)

    store.initMap("default", DataType.PLANTABILITY, displayState())

    expect(store.filteredValues).toEqual([])
  })

  it("initMap clears the cadastre and panoramax selections", () => {
    const store = useMapStore()
    store.selectedCadastreParcel = { parcelId: "1", section: "AB", numero: "12", surface: null }
    store.selectedPanoramaxPicture = { id: "picture" } as PanoramaxPicture

    store.initMap("default", DataType.PLANTABILITY, displayState())

    expect(store.selectedCadastreParcel).toBeNull()
    expect(store.selectedPanoramaxPicture).toBeNull()
  })
})

describe.each([
  {
    name: "QPV",
    toggle: "toggleQPVLayer",
    fetchData: getQPVData,
    sourceId: "qpv-source",
    layerId: "qpv-border"
  },
  {
    name: "boundary",
    toggle: "toggleBoundaryLayer",
    fetchData: getCityBoundaries,
    sourceId: "city-boundary-source",
    layerId: "city-boundary"
  }
] as const)("map store $name layer loading", ({ toggle, fetchData, sourceId, layerId }) => {
  let resolveData: (data: GeoJSON.FeatureCollection) => void

  beforeEach(() => {
    setActivePinia(createPinia())
    createdMaps.length = 0
    vi.mocked(fetchData).mockReturnValue(
      new Promise((resolve) => {
        resolveData = resolve
      })
    )
  })

  it("adds the layer once its data is loaded", async () => {
    const { store, map } = initStoreWithMap()

    const toggledOn = store[toggle]()
    resolveData(EMPTY_FEATURE_COLLECTION)
    await toggledOn

    expect(map.sources.has(sourceId)).toBe(true)
    expect(map.layers.has(layerId)).toBe(true)
  })

  it("does not add the layer when it is toggled off while its data loads", async () => {
    const { store, map } = initStoreWithMap()

    const toggledOn = store[toggle]()
    await store[toggle]()
    resolveData(EMPTY_FEATURE_COLLECTION)
    await toggledOn

    expect(map.sources.has(sourceId)).toBe(false)
    expect(map.layers.has(layerId)).toBe(false)
  })

  it("adds the source once when two loads overlap", async () => {
    const { store, map } = initStoreWithMap()

    const firstToggledOn = store[toggle]()
    await store[toggle]()
    const secondToggledOn = store[toggle]()
    resolveData(EMPTY_FEATURE_COLLECTION)
    await Promise.all([firstToggledOn, secondToggledOn])

    expect(map.layers.has(layerId)).toBe(true)
  })
})
