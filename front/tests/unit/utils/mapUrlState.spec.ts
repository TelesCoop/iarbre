import { describe, it, expect } from "vitest"
import { buildMapDisplayQuery, parseMapDisplayState } from "@/utils/mapUrlState"
import {
  DataType,
  MapStyle,
  OverlayLayer,
  PublicBuildingCategory,
  ALL_PUBLIC_BUILDING_CATEGORIES
} from "@/utils/enum"

describe("parseMapDisplayState", () => {
  it("returns the default display when the query is empty", () => {
    expect(parseMapDisplayState({}, DataType.PLANTABILITY)).toEqual({
      filters: [],
      mapStyle: MapStyle.OSM,
      overlayLayers: []
    })
  })

  it("reads the basemap", () => {
    const state = parseMapDisplayState({ basemap: "satellite" }, DataType.PLANTABILITY)

    expect(state.mapStyle).toBe(MapStyle.SATELLITE)
  })

  it("ignores a basemap the background selector does not offer", () => {
    const state = parseMapDisplayState({ basemap: "cadastre" }, DataType.PLANTABILITY)

    expect(state.mapStyle).toBe(MapStyle.OSM)
  })

  it("reads the overlay layers", () => {
    const state = parseMapDisplayState({ layers: "qpv,panoramax" }, DataType.PLANTABILITY)

    expect(state.overlayLayers).toEqual([OverlayLayer.QPV, OverlayLayer.PANORAMAX])
  })

  it("drops unknown overlay layers", () => {
    const state = parseMapDisplayState({ layers: "qpv,unknown" }, DataType.PLANTABILITY)

    expect(state.overlayLayers).toEqual([OverlayLayer.QPV])
  })

  it("reads plantability filters as numbers", () => {
    const state = parseMapDisplayState({ filters: "2,4" }, DataType.PLANTABILITY)

    expect(state.filters).toEqual([2, 4])
  })

  it("reads vulnerability filters as numbers", () => {
    const state = parseMapDisplayState({ filters: "3,5" }, DataType.VULNERABILITY)

    expect(state.filters).toEqual([3, 5])
  })

  it("drops numeric filters that are not numbers", () => {
    const state = parseMapDisplayState({ filters: "2,abc" }, DataType.PLANTABILITY)

    expect(state.filters).toEqual([2])
  })

  it("reads filters of other data types as strings", () => {
    const state = parseMapDisplayState({ filters: "1,A" }, DataType.CLIMATE_ZONE)

    expect(state.filters).toEqual(["1", "A"])
  })

  it("reads biosphere filters as ranges and legacy labels", () => {
    const state = parseMapDisplayState(
      { filters: "0-12,Entre 87% et 100%" },
      DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY
    )

    expect(state.filters).toEqual(["Entre 0% et 12%", "Entre 87% et 100%"])
  })

  it("merges a repeated query parameter", () => {
    const state = parseMapDisplayState({ layers: ["qpv", "cadastre"] }, DataType.PLANTABILITY)

    expect(state.overlayLayers).toEqual([OverlayLayer.QPV, OverlayLayer.CADASTRE])
  })

  it("reads the known categories in the enum order", () => {
    const state = parseMapDisplayState(
      { buildings: "sante,unknown,enseignement" },
      DataType.PLANTABILITY
    )

    expect(state.publicBuildingCategories).toEqual([
      PublicBuildingCategory.ENSEIGNEMENT,
      PublicBuildingCategory.SANTE
    ])
  })
})

describe("buildMapDisplayQuery", () => {
  it("omits everything for the default display", () => {
    expect(
      buildMapDisplayQuery({ filters: [], mapStyle: MapStyle.OSM, overlayLayers: [] })
    ).toEqual({})
  })

  it("writes a non-default basemap", () => {
    expect(
      buildMapDisplayQuery({ filters: [], mapStyle: MapStyle.ORTHOPHOTO, overlayLayers: [] })
    ).toEqual({ basemap: "orthophoto" })
  })

  it("writes the visible overlay layers as a comma-separated list", () => {
    expect(
      buildMapDisplayQuery({
        filters: [],
        mapStyle: MapStyle.OSM,
        overlayLayers: [OverlayLayer.QPV, OverlayLayer.BOUNDARY]
      })
    ).toEqual({ layers: "qpv,boundary" })
  })

  it("writes the filters as a comma-separated list", () => {
    expect(
      buildMapDisplayQuery({ filters: [2, 4], mapStyle: MapStyle.OSM, overlayLayers: [] })
    ).toEqual({ filters: "2,4" })
  })

  it("writes biosphere filters as ranges", () => {
    expect(
      buildMapDisplayQuery({
        filters: ["Entre 0% et 12%", "Entre 87% et 100%"],
        mapStyle: MapStyle.OSM,
        overlayLayers: []
      })
    ).toEqual({ filters: "0-12,87-100" })
  })

  it("produces a query that parses back to the same display", () => {
    const state = {
      filters: [2, 4],
      mapStyle: MapStyle.SATELLITE,
      overlayLayers: [OverlayLayer.QPV, OverlayLayer.CADASTRE]
    }

    expect(parseMapDisplayState(buildMapDisplayQuery(state), DataType.PLANTABILITY)).toEqual(state)
  })

  it("omits the public building categories when all are selected", () => {
    expect(
      buildMapDisplayQuery({
        filters: [],
        mapStyle: MapStyle.OSM,
        overlayLayers: [],
        publicBuildingCategories: ALL_PUBLIC_BUILDING_CATEGORIES
      })
    ).toEqual({})
  })

  it("writes the selected public building categories in the enum order", () => {
    expect(
      buildMapDisplayQuery({
        filters: [],
        mapStyle: MapStyle.OSM,
        overlayLayers: [OverlayLayer.PUBLIC_BUILDINGS],
        publicBuildingCategories: [
          PublicBuildingCategory.SANTE,
          PublicBuildingCategory.ENSEIGNEMENT
        ]
      })
    ).toEqual({ layers: "public_buildings", buildings: "enseignement,sante" })
  })

  it("omits the public building categories when the layer is hidden", () => {
    expect(
      buildMapDisplayQuery({
        filters: [],
        mapStyle: MapStyle.OSM,
        overlayLayers: [OverlayLayer.QPV],
        publicBuildingCategories: [PublicBuildingCategory.SANTE]
      })
    ).toEqual({ layers: "qpv" })
  })

  it("writes an empty value when no public building category is selected", () => {
    const state = {
      filters: [],
      mapStyle: MapStyle.OSM,
      overlayLayers: [OverlayLayer.PUBLIC_BUILDINGS],
      publicBuildingCategories: []
    }

    expect(buildMapDisplayQuery(state)).toEqual({ layers: "public_buildings", buildings: "" })
    expect(parseMapDisplayState(buildMapDisplayQuery(state), DataType.PLANTABILITY)).toEqual(state)
  })
})
