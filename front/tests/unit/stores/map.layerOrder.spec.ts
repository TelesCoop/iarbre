import { describe, it, expect, beforeEach, vi } from "vitest"
import { setActivePinia, createPinia } from "pinia"
import type { Map } from "maplibre-gl"
import { useMapStore } from "@/stores/map"
import { getLayerId } from "@/utils/map"
import { DataType, GeoLevel } from "@/utils/enum"
import { TERRA_DRAW_POLYGON_LAYER } from "@/utils/constants"
import { createFakeMap } from "../../helpers/fakeMap"

vi.mock("maplibre-gl", () => ({ Map: class {}, NavigationControl: class {} }))

const DATA_LAYER_ID = getLayerId(DataType.PLANTABILITY, GeoLevel.TILE)

describe("map store 2D/3D switch", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it.each([
    ["with", [TERRA_DRAW_POLYGON_LAYER]],
    ["without", []]
  ])("keeps the QPV borders above the data layer %s Terra Draw", (_, topLayerIds) => {
    const store = useMapStore()
    const layerIds = ["basemap", DATA_LAYER_ID, "qpv-border-casing", "qpv-border", ...topLayerIds]
    const map = createFakeMap([...layerIds])
    store.mapInstancesByIds = { default: map as unknown as Map }

    store.toggle3D()

    expect(map.layerIds).toEqual(layerIds)
  })
})
