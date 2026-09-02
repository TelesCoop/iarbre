import { computed, markRaw, ref } from "vue"
import { defineStore } from "pinia"
import { useDebounceFn } from "@vueuse/core"
import { useMapFilters } from "@/composables/useMapFilters"
import {
  Map,
  NavigationControl,
  type GeoJSONSource,
  type AddLayerObject,
  type DataDrivenPropertyValueSpecification
} from "maplibre-gl"
import {
  MAP_CONTROL_POSITION,
  MAX_ZOOM,
  MIN_ZOOM,
  DEFAULT_MAP_CENTER,
  TERRA_DRAW_POLYGON_LAYER,
  MAX_SHAPE_AREA_M2
} from "@/utils/constants"
import { GeoLevel, DataType, MapStyle, SelectionMode, DataTypeToGeolevel } from "@/utils/enum"
import mapStyles from "@/map/map-style.json"
import { applyMapStyleAttributions } from "@/utils/mapStyleOptions"
import { getFullBaseApiUrl } from "@/api"
import { getQPVData } from "@/services/qpvService"
import { getCityBoundaries } from "@/services/boundaryService"
import { getVegetationHeightAtPoint } from "@/services/vegetationService"
import { VulnerabilityMode as VulnerabilityModeType } from "@/utils/vulnerability"

import { VULNERABILITY_COLOR_MAP } from "@/utils/vulnerability"
import { PLANTABILITY_COLOR_MAP, PLANTABILITY_DETAIL_ZOOM } from "@/utils/plantability"
import { BIOSPHERE_FUNCTIONAL_INTEGRITY_COLOR_MAP } from "@/utils/biosphere_functional_integrity"
import { generateBivariateColorExpression } from "@/utils/plantability_vulnerability"
import { CLIMATE_ZONE_MAP_COLOR_MAP } from "@/utils/climateZone"
import {
  VEGESTRATE_COLOR_MAP,
  VEGESTRATE_HEIGHT_MAP,
  VEGESTRATE_TERRAIN_EXAGGERATION,
  buildElevationColorRamp,
  normalizeHeightRanges,
  type HeightRange
} from "@/utils/vegetation"
import { LocalStorageHandler } from "@/utils/LocalStorageHandler"
import { extractFeatureProperty, getLayerId, getSourceId, highlightFeature } from "@/utils/map"
import {
  QPV_CASING_COLOR,
  QPV_CASING_WIDTH,
  QPV_CASING_OPACITY,
  QPV_BORDER_COLOR,
  QPV_BORDER_WIDTH,
  QPV_BORDER_OPACITY,
  CITY_BORDER_COLOR,
  CITY_BORDER_WIDTH,
  CITY_BORDER_OPACITY,
  CADASTRE_COLOR,
  CADASTRE_BORDER_WIDTH,
  CADASTRE_BORDER_OPACITY,
  CADASTRE_SELECTED_BORDER_WIDTH,
  CADASTRE_SELECTED_BORDER_OPACITY,
  CADASTRE_SELECTED_FILL_OPACITY,
  CADASTRE_DEFAULT_FILL_OPACITY,
  CITY_CASING_COLOR,
  CITY_CASING_WIDTH,
  CITY_CASING_OPACITY
} from "@/utils/mapLayers"
import { useContextData } from "@/composables/useContextData"
import { getBivariateCoordinates } from "@/utils/plantability_vulnerability"
import { addCenterControl, add3DControl } from "@/utils/mapControls"
import { useShapeDrawing } from "@/composables/useTerraDraw"
import { computePolygonAreaM2 } from "@/utils/geo"
import type { ZonePolygon } from "@/stores/zone"

const isHeightRange = (range: unknown): range is HeightRange => {
  if (typeof range !== "object" || range === null) return false
  const { min, max } = range as HeightRange
  return typeof min === "number" && (max === null || typeof max === "number")
}

const loadStoredHeightRanges = (): HeightRange[] => {
  const stored = LocalStorageHandler.getItem("vegestrateHeightRanges")
  return Array.isArray(stored) ? normalizeHeightRanges(stored.filter(isHeightRange)) : []
}

export const useMapStore = defineStore("map", () => {
  const mapInstancesByIds = ref<Record<string, Map>>({})
  const mapEventsListener = ref<Record<string, (e: any) => void>>({})
  const selectedDataType = ref<DataType>(DataType.PLANTABILITY)
  const selectedMapStyle = ref<MapStyle>(MapStyle.OSM)
  const vulnerabilityMode = ref<VulnerabilityModeType>(VulnerabilityModeType.DAY)
  const currentZoom = ref<number>(14)
  const contextData = useContextData(selectedDataType)
  const showQPVLayer = ref<boolean>(false)
  const showBoundaryLayer = ref<boolean>(false)
  const showCadastreLayer = ref<boolean>(false)
  const selectedCadastreParcel = ref<{
    parcelId: string
    section: string
    numero: string
    surface: number | null
  } | null>(null)
  const selectionMode = ref<SelectionMode>(SelectionMode.POINT)
  const shapeEditing = ref<boolean>(false)
  const liveArea = ref<number | null>(null)
  const shapeDrawing = useShapeDrawing()
  const clickCoordinates = ref<{ lat: number; lng: number }>({
    lat: DEFAULT_MAP_CENTER.lat,
    lng: DEFAULT_MAP_CENTER.lng
  })
  const isCalculating = ref<boolean>(false)
  const controlsAdded = ref<Record<string, boolean>>({})

  const selectedLegendCell = ref<{ plantability: number; vulnerability: number } | null>(null)
  const use3D = ref<boolean>(false)
  const showVegestrateHeight = ref<boolean>(false)
  const vegestrateHeightRanges = ref<HeightRange[]>(loadStoredHeightRanges())
  const vegetationHeightAtPoint = ref<number | null | undefined>(undefined)
  const heightMapClickHandler = ref<((e: any) => void) | null>(null)
  const heightMapZoomHandler = ref<(() => void) | null>(null)

  const {
    clearAllFilters,
    applyFilters,
    hasActiveFilters,
    isFiltered,
    filteredValues,
    toggleFilter,
    activeFiltersCount
  } = useMapFilters()

  // reference https://docs.mapbox.com/style-spec/reference/expressions
  const FILL_COLOR_MAP = computed(() => {
    const bivariateExpression = generateBivariateColorExpression(vulnerabilityMode.value)

    return {
      [DataType.PLANTABILITY]: ["match", ["get", "indice"], ...PLANTABILITY_COLOR_MAP],
      [DataType.VULNERABILITY]: [
        "match",
        ["get", `indice_${vulnerabilityMode.value}`],
        ...VULNERABILITY_COLOR_MAP
      ],
      [DataType.CLIMATE_ZONE]: ["match", ["get", "indice"], ...CLIMATE_ZONE_MAP_COLOR_MAP],
      [DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY]: [
        "step",
        ["get", "indice"],
        ...BIOSPHERE_FUNCTIONAL_INTEGRITY_COLOR_MAP
      ],
      [DataType.PLANTABILITY_VULNERABILITY]: bivariateExpression,
      [DataType.VEGESTRATE]: ["match", ["get", "indice"], ...VEGESTRATE_COLOR_MAP]
    }
  })

  const HEIGHT_MULTIPLIER = 15
  const EXTRUSION_HEIGHT_MAP = computed(() => {
    return {
      [DataType.PLANTABILITY]: ["*", ["get", "indice"], HEIGHT_MULTIPLIER],
      [DataType.VULNERABILITY]: [
        "*",
        ["get", `indice_${vulnerabilityMode.value}`],
        HEIGHT_MULTIPLIER
      ],
      [DataType.CLIMATE_ZONE]: ["*", ["get", "indice"], HEIGHT_MULTIPLIER],
      [DataType.PLANTABILITY_VULNERABILITY]: ["*", ["get", "indice"], HEIGHT_MULTIPLIER],
      [DataType.VEGESTRATE]: [
        "*",
        ["match", ["get", "indice"], ...VEGESTRATE_HEIGHT_MAP],
        HEIGHT_MULTIPLIER
      ],
      [DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY]: ["*", ["get", "indice"], HEIGHT_MULTIPLIER / 100]
    }
  })

  const getGeoLevelFromDataType = () => {
    return DataTypeToGeolevel[selectedDataType.value!]
  }

  const isVegestrateHeightMode = (datatype: DataType) =>
    datatype === DataType.VEGESTRATE && showVegestrateHeight.value

  /**
   * Deep-clone the raw maplibre style JSON for a given MapStyle, inject the
   * backend base URL and the Carto basemap key where needed and apply
   * centralized source attributions. When no Carto key is configured, the
   * `?key=` parameter is dropped so the keyless basemaps are used.
   * Reference: https://maplibre.org/maplibre-gl-js/docs/examples/map-tiles/
   * https://www.reddit.com/r/QGIS/comments/q0su5b/comment/hfabj8f/
   */
  const loadMapStyle = (style: MapStyle): maplibregl.StyleSpecification => {
    const cartoApiKey = import.meta.env.VITE_CARTO_API_KEY
    const rawStyle = JSON.stringify(mapStyles[style])
      .replace("{API_BASE_URL}", getFullBaseApiUrl())
      .replace(/\?key=\{CARTO_API_KEY\}/g, cartoApiKey ? `?key=${cartoApiKey}` : "")
    return applyMapStyleAttributions(JSON.parse(rawStyle)) as maplibregl.StyleSpecification
  }
  const navControl = ref(
    new NavigationControl({
      visualizePitch: true,
      visualizeRoll: false,
      showZoom: true,
      showCompass: true
    })
  )

  const toggleAndApplyFilter = (value: number | string) => {
    toggleFilter(value)
    applyFilters(mapInstancesByIds, selectedDataType, vulnerabilityMode)
  }

  const resetFilters = () => {
    clearAllFilters()
    applyFilters(mapInstancesByIds, selectedDataType, vulnerabilityMode)
  }

  const centerControl = ref({
    onAdd: (map: Map) => addCenterControl(map),
    onRemove: () => {
      const controlElement = document.getElementsByClassName("maplibregl-ctrl-center-container")[0]
      if (controlElement) {
        controlElement.remove()
      }
    }
  })

  const control3D = ref({
    onAdd: () => add3DControl(use3D, toggle3D),
    onRemove: () => {
      const controlElement = document.getElementsByClassName("maplibregl-ctrl-3d-container")[0]
      if (controlElement) {
        controlElement.remove()
      }
    }
  })

  const getMapInstance = (mapId: string): Map => {
    return mapInstancesByIds.value[mapId]
  }

  const createMapLayers = (
    datatype: DataType,
    geolevel: GeoLevel,
    sourceId: string
  ): AddLayerObject[] => {
    const layerId = getLayerId(datatype, geolevel)

    if (isVegestrateHeightMode(datatype)) {
      return [
        {
          id: layerId,
          type: "color-relief",
          source: sourceId,
          layout: {},
          paint: {
            "color-relief-opacity": 0.8,
            "color-relief-color": buildElevationColorRamp(vegestrateHeightRanges.value)
          }
        }
      ]
    }

    const sourceLayer = `${geolevel}--${datatype === DataType.PLANTABILITY_VULNERABILITY ? DataType.PLANTABILITY : datatype}`

    if (use3D.value) {
      const extrusionLayer: AddLayerObject = {
        id: layerId,
        type: "fill-extrusion",
        source: sourceId,
        "source-layer": sourceLayer,
        layout: {},
        paint: {
          "fill-extrusion-color": FILL_COLOR_MAP.value[
            datatype
          ] as DataDrivenPropertyValueSpecification<"ExpressionSpecification">,
          "fill-extrusion-height": EXTRUSION_HEIGHT_MAP.value[
            datatype
          ] as DataDrivenPropertyValueSpecification<number>,
          "fill-extrusion-base": 0,
          "fill-extrusion-opacity": 0.7
        }
      }
      return [extrusionLayer]
    }

    const fillLayer: AddLayerObject = {
      id: layerId,
      type: "fill",
      source: sourceId,
      "source-layer": sourceLayer,
      layout: {},
      paint: {
        "fill-color": FILL_COLOR_MAP.value[
          datatype
        ] as DataDrivenPropertyValueSpecification<"ExpressionSpecification">,
        "fill-opacity": 0.5,
        "fill-outline-color": "#00000000"
      }
    }

    const lineLayer: AddLayerObject = {
      id: `${layerId}-border`,
      type: "line",
      source: sourceId,
      "source-layer": sourceLayer,
      layout: {},
      paint: {
        "line-color": "#00000000",
        "line-width": 0
      }
    }

    return [fillLayer, lineLayer]
  }

  const CLICK_MARKER_SOURCE = "ifb-click-square-source"
  const CLICK_MARKER_CASING_LAYER = "ifb-click-marker-casing-layer"
  const CLICK_MARKER_LAYER = "ifb-click-square-layer"
  const IFB_CLICK_CIRCLE_SOURCE = "ifb-click-circle-source"
  const IFB_CLICK_CIRCLE_LAYER = "ifb-click-circle-layer"
  const IFB_CIRCLE_RADIUS_M = 500

  const CROSS_HALF_SIZE_PX = 9

  const metersPerPixel = (map: Map, lat: number) =>
    (156543.03392 * Math.cos((lat * Math.PI) / 180)) / 2 ** map.getZoom()

  const CLICK_MARKER_STYLES = {
    square: {
      halfSizeM: () => 2,
      width: QPV_CASING_WIDTH,
      casingWidth: 0
    },
    cross: {
      halfSizeM: (map: Map, lat: number) => CROSS_HALF_SIZE_PX * metersPerPixel(map, lat),
      width: 2,
      casingWidth: 5
    }
  }
  type ClickMarkerShape = keyof typeof CLICK_MARKER_STYLES

  const drawClickMarker = (
    map: Map,
    lat: number,
    lng: number,
    shape: ClickMarkerShape,
    withCircle = true
  ) => {
    const { halfSizeM, width, casingWidth } = CLICK_MARKER_STYLES[shape]
    const sizeM = halfSizeM(map, lat)
    const latOffset = sizeM / 111320
    const lngOffset = sizeM / (111320 * Math.cos((lat * Math.PI) / 180))
    const marker = {
      type: "Feature" as const,
      geometry:
        shape === "square"
          ? {
              type: "Polygon" as const,
              coordinates: [
                [
                  [lng - lngOffset, lat - latOffset],
                  [lng + lngOffset, lat - latOffset],
                  [lng + lngOffset, lat + latOffset],
                  [lng - lngOffset, lat + latOffset],
                  [lng - lngOffset, lat - latOffset]
                ]
              ]
            }
          : {
              type: "MultiLineString" as const,
              coordinates: [
                [
                  [lng - lngOffset, lat],
                  [lng + lngOffset, lat]
                ],
                [
                  [lng, lat - latOffset],
                  [lng, lat + latOffset]
                ]
              ]
            },
      properties: {}
    }
    const source = map.getSource(CLICK_MARKER_SOURCE) as GeoJSONSource | undefined
    if (source) {
      source.setData(marker)
    } else {
      map.addSource(CLICK_MARKER_SOURCE, { type: "geojson", data: marker })
      map.addLayer({
        id: CLICK_MARKER_CASING_LAYER,
        type: "line",
        source: CLICK_MARKER_SOURCE,
        layout: { "line-cap": "round" },
        paint: {
          "line-color": QPV_BORDER_COLOR,
          "line-width": casingWidth,
          "line-opacity": QPV_CASING_OPACITY
        }
      })
      map.addLayer({
        id: CLICK_MARKER_LAYER,
        type: "line",
        source: CLICK_MARKER_SOURCE,
        layout: { "line-cap": "round" },
        paint: {
          "line-color": QPV_CASING_COLOR,
          "line-width": width,
          "line-opacity": QPV_CASING_OPACITY
        }
      })
    }

    if (!withCircle) return

    const latRadiusDeg = IFB_CIRCLE_RADIUS_M / 111320
    const lngRadiusDeg = IFB_CIRCLE_RADIUS_M / (111320 * Math.cos((lat * Math.PI) / 180))
    const steps = 64
    const circleCoords = Array.from({ length: steps + 1 }, (_, i) => {
      const angle = (i * 2 * Math.PI) / steps
      return [lng + lngRadiusDeg * Math.cos(angle), lat + latRadiusDeg * Math.sin(angle)]
    })
    const circle = {
      type: "Feature" as const,
      geometry: { type: "Polygon" as const, coordinates: [circleCoords] },
      properties: {}
    }
    const circleSource = map.getSource(IFB_CLICK_CIRCLE_SOURCE) as GeoJSONSource | undefined
    if (circleSource) {
      circleSource.setData(circle)
    } else {
      map.addSource(IFB_CLICK_CIRCLE_SOURCE, { type: "geojson", data: circle })
      map.addLayer({
        id: IFB_CLICK_CIRCLE_LAYER,
        type: "line",
        source: IFB_CLICK_CIRCLE_SOURCE,
        paint: { "line-color": "#FFFFFF", "line-width": 2 }
      })
    }
    console.info("cypress: IFB click square drawn")
  }

  const removeClickMarker = (map: Map) => {
    for (const layerId of [CLICK_MARKER_CASING_LAYER, CLICK_MARKER_LAYER, IFB_CLICK_CIRCLE_LAYER]) {
      if (map.getLayer(layerId)) {
        map.removeLayer(layerId)
      }
    }
    for (const sourceId of [CLICK_MARKER_SOURCE, IFB_CLICK_CIRCLE_SOURCE]) {
      if (map.getSource(sourceId)) {
        map.removeSource(sourceId)
      }
    }
    console.info("cypress: IFB click square removed")
  }

  const applyTileSelection = (
    map: Map,
    datatype: DataType,
    geolevel: GeoLevel,
    features: any[],
    lngLat: { lng: number; lat: number }
  ) => {
    const layerId = getLayerId(datatype, geolevel)
    const featureId = extractFeatureProperty(features, datatype, geolevel, "id")
    const score = extractFeatureProperty(features, datatype, geolevel, "indice")
    const sourceValues = extractFeatureProperty(features, datatype, geolevel, "source_values")
    const vulnScoreDay =
      geolevel === GeoLevel.TILE && datatype === DataType.PLANTABILITY_VULNERABILITY
        ? extractFeatureProperty(features, datatype, geolevel, "vulnerability_indice_day")
        : undefined
    const vulnScoreNight =
      geolevel === GeoLevel.TILE && datatype === DataType.PLANTABILITY_VULNERABILITY
        ? extractFeatureProperty(features, datatype, geolevel, "vulnerability_indice_night")
        : undefined
    if (datatype === DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY) {
      drawClickMarker(map, lngLat.lat, lngLat.lng, "square")
    } else {
      highlightFeature(map, layerId, featureId)
    }
    // Highlight cell in the legend that correspond to clicked tile
    if (geolevel === GeoLevel.TILE && datatype === DataType.PLANTABILITY_VULNERABILITY) {
      const properties = features[0].properties
      if (
        properties &&
        properties.indice !== undefined &&
        properties.vulnerability_indice_day !== undefined
      ) {
        selectedLegendCell.value = getBivariateCoordinates(
          properties.indice,
          properties.vulnerability_indice_day
        )
      }
    } else {
      selectedLegendCell.value = null
    }

    clickCoordinates.value = { lat: lngLat.lat, lng: lngLat.lng }

    // Conditionally load context data based on geolevel, datatype, and zoom
    if (
      geolevel === GeoLevel.TILE &&
      datatype === DataType.PLANTABILITY &&
      map.getZoom() < PLANTABILITY_DETAIL_ZOOM
    ) {
      contextData.setData(featureId, score, sourceValues)
    } else if (geolevel === GeoLevel.TILE && datatype === DataType.PLANTABILITY_VULNERABILITY) {
      contextData.setData(featureId, score, sourceValues, vulnScoreDay, vulnScoreNight)
    } else if (datatype === DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY) {
      contextData.setData(featureId, score, undefined, undefined, undefined, lngLat.lat, lngLat.lng)
    } else {
      contextData.setData(featureId)
    }
  }

  const setupClickEventOnTile = (map: Map, datatype: DataType, geolevel: GeoLevel) => {
    if (heightMapClickHandler.value) {
      map.off("click", heightMapClickHandler.value)
      heightMapClickHandler.value = null
    }
    if (heightMapZoomHandler.value) {
      map.off("zoom", heightMapZoomHandler.value)
      heightMapZoomHandler.value = null
    }
    if (isVegestrateHeightMode(datatype)) {
      const handler = async (e: any) => {
        if (selectionMode.value !== SelectionMode.POINT) return
        clickCoordinates.value = { lat: e.lngLat.lat, lng: e.lngLat.lng }
        drawClickMarker(map, e.lngLat.lat, e.lngLat.lng, "cross", false)
        vegetationHeightAtPoint.value = await getVegetationHeightAtPoint(e.lngLat.lat, e.lngLat.lng)
      }
      map.on("click", handler)
      heightMapClickHandler.value = handler

      const zoomHandler = () => {
        if (!map.getLayer(CLICK_MARKER_LAYER)) return
        const { lat, lng } = clickCoordinates.value
        drawClickMarker(map, lat, lng, "cross", false)
      }
      map.on("zoom", zoomHandler)
      heightMapZoomHandler.value = zoomHandler
      return
    }
    const layerId = getLayerId(datatype, geolevel)
    if (mapEventsListener.value[layerId]) {
      map.off("click", layerId, mapEventsListener.value[layerId])
    }
    const clickHandler = (e: any) => {
      // If we are in POINT mode (simple click), handle click normally
      // Other modes are handled automatically by Terra Draw
      if (selectionMode.value !== SelectionMode.POINT) {
        return
      }
      applyTileSelection(map, datatype, geolevel, e.features!, {
        lng: e.lngLat.lng,
        lat: e.lngLat.lat
      })
    }
    map.on("click", layerId, clickHandler)
    mapEventsListener.value[layerId] = clickHandler
  }

  /**
   * Re-query the tile under the currently selected coordinates and recompute the
   * context data for the current zoom (land-use detail when zoomed in, score
   * distribution when zoomed out). Called after a programmatic zoom.
   */
  const recalculateAtSelection = () => {
    const map = mapInstancesByIds.value["default"]
    if (!map || !contextData.data.value) return
    const datatype = selectedDataType.value
    if (!datatype) return
    const geolevel = getGeoLevelFromDataType()
    const layerId = getLayerId(datatype, geolevel)
    if (!map.getLayer(layerId)) return
    const { lng, lat } = clickCoordinates.value
    const features = map.queryRenderedFeatures(map.project([lng, lat]), { layers: [layerId] })
    if (features.length) {
      applyTileSelection(map, datatype, geolevel, features, { lng, lat })
    }
  }

  const setupTile = (map: Map, datatype: DataType, geolevel: GeoLevel) => {
    const sourceId = getSourceId(datatype, geolevel)
    const layers = createMapLayers(datatype, geolevel, sourceId)

    // Add layers before Terra Draw layers so they are underneath
    const beforeId = map.getLayer(TERRA_DRAW_POLYGON_LAYER) ? TERRA_DRAW_POLYGON_LAYER : undefined

    layers.forEach((layer) => {
      if (!map.getLayer(layer.id)) {
        map.addLayer(layer, beforeId)
      }
    })

    setupClickEventOnTile(map, datatype, geolevel)
  }

  const setupSource = (map: Map, datatype: DataType, geolevel: GeoLevel) => {
    const fullBaseApiUrl = getFullBaseApiUrl()
    const sourceId = getSourceId(datatype, geolevel)

    if (isVegestrateHeightMode(datatype)) {
      const tileUrl = `${fullBaseApiUrl}/tiles/vegetation-height/{z}/{x}/{y}.png?kind=raw`
      map.addSource(sourceId, {
        type: "raster-dem",
        encoding: "terrarium",
        tiles: [tileUrl],
        tileSize: 256,
        minzoom: MIN_ZOOM
      })
      return
    }

    // Vector source for other data types
    const tileDataType =
      datatype === DataType.PLANTABILITY_VULNERABILITY ? DataType.PLANTABILITY : datatype
    const tileUrl = `${fullBaseApiUrl}/tiles/${geolevel}/${tileDataType}/{z}/{x}/{y}.mvt`
    map.addSource(sourceId, {
      type: "vector",
      tiles: [tileUrl],
      minzoom: MIN_ZOOM
    })
  }

  const getMapId = (map: Map): string => {
    return Object.keys(mapInstancesByIds.value).find((key) => mapInstancesByIds.value[key] === map)!
  }

  const removeControls = (map: Map) => {
    const mapId = getMapId(map)
    if (!controlsAdded.value[mapId]) return

    try {
      map.removeControl(navControl.value)
      map.removeControl(centerControl.value)
      map.removeControl(control3D.value)
      controlsAdded.value[mapId] = false
    } catch {
      // Control may not be added yet
    }
  }

  const setupControls = (map: Map) => {
    const mapId = getMapId(map)
    if (!controlsAdded.value[mapId]) {
      map.addControl(control3D.value, MAP_CONTROL_POSITION)
      map.addControl(navControl.value, MAP_CONTROL_POSITION)
      map.addControl(centerControl.value, MAP_CONTROL_POSITION)
      controlsAdded.value[mapId] = true
    }
  }

  const changeDataType = (datatype: DataType) => {
    const previousDataType = selectedDataType.value!
    const previousGeoLevel = getGeoLevelFromDataType()
    if (datatype !== DataType.VEGESTRATE) showVegestrateHeight.value = false
    selectedDataType.value = datatype
    clearAllFilters()
    contextData.removeData()
    vegetationHeightAtPoint.value = undefined
    selectedLegendCell.value = null

    // Update all map instances with the new layer
    Object.keys(mapInstancesByIds.value).forEach((mapId) => {
      const mapInstance = mapInstancesByIds.value[mapId]
      // Clear overlay layers before removing sources
      if (mapInstance.getLayer("qpv-border")) {
        removeQPVLayer(mapInstance)
      }
      if (mapInstance.getLayer("city-boundary")) {
        removeBoundaryLayers(mapInstance)
      }
      if (mapInstance.getLayer("cadastre-fill")) {
        removeCadastreLayer(mapInstance)
      }
      if (mapInstance.getLayer(CLICK_MARKER_LAYER)) {
        removeClickMarker(mapInstance)
      }
      // remove existing layers and sources
      if (previousDataType !== null) {
        clearTerrain(mapInstance)
        const layerId = getLayerId(previousDataType, previousGeoLevel)
        if (mapInstance.getLayer(layerId)) {
          mapInstance.removeLayer(layerId)
        }
        if (mapInstance.getLayer(`${layerId}-border`)) {
          mapInstance.removeLayer(`${layerId}-border`)
        }
        const sourceId = getSourceId(previousDataType, previousGeoLevel)
        if (mapInstance.getSource(sourceId)) {
          mapInstance.removeSource(sourceId)
        }
      }
      removeControls(mapInstance)
      initTiles(mapInstance)
      if (showQPVLayer.value) {
        addQPVLayer(mapInstance)
      }
      if (showBoundaryLayer.value) {
        addBoundaryLayers(mapInstance)
      }
      if (showCadastreLayer.value) {
        addCadastreLayer(mapInstance)
      }
      setupControls(mapInstance)
      // MapComponent is listening to moveend event
      mapInstance.fire("moveend")
    })

    // If a geometry is drawn, automatically recalculate with the new data type
    const features = shapeDrawing.getSelectedFeatures()
    if (features.length > 0 && selectionMode.value !== SelectionMode.POINT) {
      finishShapeSelection()
    }
  }

  const refreshDatatype = () => {
    changeDataType(selectedDataType.value)
  }

  const toggleVegestrateHeight = () => {
    showVegestrateHeight.value = !showVegestrateHeight.value
    refreshDatatype()
  }

  const setVegestrateHeightRanges = (ranges: HeightRange[]) => {
    if (!showVegestrateHeight.value) return
    const normalized = normalizeHeightRanges(ranges)
    vegestrateHeightRanges.value = normalized
    LocalStorageHandler.setItem("vegestrateHeightRanges", normalized)
    const ramp = buildElevationColorRamp(normalized)
    const layerId = getLayerId(DataType.VEGESTRATE, getGeoLevelFromDataType())
    Object.values(mapInstancesByIds.value).forEach((mapInstance) => {
      if (mapInstance.getLayer(layerId)) {
        mapInstance.setPaintProperty(layerId, "color-relief-color", ramp)
      }
    })
  }

  const refreshLayers = () => {
    const currentDataType = selectedDataType.value
    const currentGeoLevel = getGeoLevelFromDataType()
    Object.keys(mapInstancesByIds.value).forEach((mapId) => {
      const mapInstance = mapInstancesByIds.value[mapId]
      const layerId = getLayerId(currentDataType, currentGeoLevel)
      if (mapInstance.getLayer(layerId)) {
        mapInstance.removeLayer(layerId)
      }
      if (mapInstance.getLayer(`${layerId}-border`)) {
        mapInstance.removeLayer(`${layerId}-border`)
      }
      setupTile(mapInstance, currentDataType, currentGeoLevel)
    })
  }

  const changeMapStyle = (mapstyle: MapStyle) => {
    selectedMapStyle.value = mapstyle
    Object.keys(mapInstancesByIds.value).forEach((mapId) => {
      const mapInstance = mapInstancesByIds.value[mapId]
      removeControls(mapInstance)
      clearTerrain(mapInstance)
      // Clear overlay layers before style change
      if (mapInstance.getLayer("qpv-border")) {
        removeQPVLayer(mapInstance)
      }
      if (mapInstance.getLayer("city-boundary")) {
        removeBoundaryLayers(mapInstance)
      }
      if (mapInstance.getLayer("cadastre-fill")) {
        removeCadastreLayer(mapInstance)
      }
      const newStyle = loadMapStyle(mapstyle)

      if (newStyle) {
        const onStyleReady = () => {
          initTiles(mapInstance)
          setupControls(mapInstance)
          if (showQPVLayer.value) {
            addQPVLayer(mapInstance)
          }
          if (showBoundaryLayer.value) {
            addBoundaryLayers(mapInstance)
          }
          if (showCadastreLayer.value) {
            addCadastreLayer(mapInstance)
          }
          mapInstance.fire("moveend")
        }

        mapInstance.setStyle(newStyle)
        onStyleReady()
      }
    })
  }

  const applyVegestrateTerrain = (mapInstance: Map, datatype: DataType) => {
    if (!isVegestrateHeightMode(datatype) || !use3D.value) return
    const sourceId = getSourceId(datatype, DataTypeToGeolevel[datatype])
    if (!mapInstance.getSource(sourceId)) return
    mapInstance.setTerrain({ source: sourceId, exaggeration: VEGESTRATE_TERRAIN_EXAGGERATION })
    console.info("cypress: vegestrate terrain enabled")
  }

  const clearTerrain = (mapInstance: Map) => {
    if (!mapInstance.getTerrain()) return
    mapInstance.setTerrain(null)
    console.info("cypress: vegestrate terrain disabled")
  }

  const initTiles = (mapInstance: Map) => {
    const currentGeoLevel = getGeoLevelFromDataType()
    setupSource(mapInstance, selectedDataType.value!, currentGeoLevel)
    setupTile(mapInstance, selectedDataType.value!, currentGeoLevel)
    applyVegestrateTerrain(mapInstance, selectedDataType.value!)
  }

  const addQPVLayer = async (mapInstance: Map) => {
    if (!mapInstance.getSource("qpv-source")) {
      const data = await getQPVData()
      if (!data) {
        return
      }

      mapInstance.addSource("qpv-source", {
        type: "geojson",
        data: data
      })
    }

    if (!mapInstance.getLayer("qpv-border")) {
      // Add QPV layer before Terra Draw layers so it is underneath
      const beforeId = mapInstance.getLayer(TERRA_DRAW_POLYGON_LAYER)
        ? TERRA_DRAW_POLYGON_LAYER
        : undefined

      // White casing drawn first so the coloured line stays legible on any basemap
      mapInstance.addLayer(
        {
          id: "qpv-border-casing",
          type: "line",
          source: "qpv-source",
          paint: {
            "line-color": QPV_CASING_COLOR,
            "line-width": QPV_CASING_WIDTH,
            "line-opacity": QPV_CASING_OPACITY
          }
        },
        beforeId
      )

      // Main QPV border drawn on top of the casing
      mapInstance.addLayer(
        {
          id: "qpv-border",
          type: "line",
          source: "qpv-source",
          paint: {
            "line-color": QPV_BORDER_COLOR,
            "line-width": QPV_BORDER_WIDTH,
            "line-opacity": QPV_BORDER_OPACITY
          }
        },
        beforeId
      )
    }
    mapInstance.once("render", () => {
      console.info(`cypress: QPV data loaded`)
    })
  }

  const removeQPVLayer = (mapInstance: Map) => {
    if (mapInstance.getLayer("qpv-border")) {
      mapInstance.removeLayer("qpv-border")
    }
    if (mapInstance.getLayer("qpv-border-casing")) {
      mapInstance.removeLayer("qpv-border-casing")
      mapInstance.once("render", () => {
        console.info(`cypress: QPV data removed`)
      })
    }
    if (mapInstance.getSource("qpv-source")) {
      mapInstance.removeSource("qpv-source")
    }
  }

  const toggleQPVLayer = async () => {
    showQPVLayer.value = !showQPVLayer.value

    for (const mapId of Object.keys(mapInstancesByIds.value)) {
      const mapInstance = mapInstancesByIds.value[mapId]

      if (showQPVLayer.value) {
        await addQPVLayer(mapInstance)
      } else {
        removeQPVLayer(mapInstance)
      }
    }
  }

  const addBoundaryLayers = async (mapInstance: Map) => {
    if (!mapInstance.getSource("city-boundary-source")) {
      const cityData = await getCityBoundaries()
      if (!cityData) return

      mapInstance.addSource("city-boundary-source", {
        type: "geojson",
        data: cityData
      })
    }

    const beforeId = mapInstance.getLayer(TERRA_DRAW_POLYGON_LAYER)
      ? TERRA_DRAW_POLYGON_LAYER
      : undefined

    if (!mapInstance.getLayer("city-boundary")) {
      // White casing drawn first so the coloured line stays legible on any basemap
      mapInstance.addLayer(
        {
          id: "city-boundary-border-casing",
          type: "line",
          source: "city-boundary-source",
          paint: {
            "line-color": CITY_CASING_COLOR,
            "line-width": CITY_CASING_WIDTH,
            "line-opacity": CITY_CASING_OPACITY
          }
        },
        beforeId
      )
      mapInstance.addLayer(
        {
          id: "city-boundary",
          type: "line",
          source: "city-boundary-source",
          paint: {
            "line-color": CITY_BORDER_COLOR,
            "line-width": CITY_BORDER_WIDTH,
            "line-opacity": CITY_BORDER_OPACITY
          }
        },
        beforeId
      )
    }
  }

  const removeBoundaryLayers = (mapInstance: Map) => {
    if (mapInstance.getLayer("city-boundary")) {
      mapInstance.removeLayer("city-boundary")
    }
    if (mapInstance.getLayer("city-boundary-border-casing")) {
      mapInstance.removeLayer("city-boundary-border-casing")
    }
    if (mapInstance.getSource("city-boundary-source")) {
      mapInstance.removeSource("city-boundary-source")
    }
  }

  const toggleBoundaryLayer = async () => {
    showBoundaryLayer.value = !showBoundaryLayer.value

    for (const mapId of Object.keys(mapInstancesByIds.value)) {
      const mapInstance = mapInstancesByIds.value[mapId]

      if (showBoundaryLayer.value) {
        await addBoundaryLayers(mapInstance)
      } else {
        removeBoundaryLayers(mapInstance)
      }
    }
  }

  const cadastreClickHandlers = ref<Record<string, (e: any) => void>>({})
  const cadastreMouseEnterHandlers = ref<Record<string, () => void>>({})
  const cadastreMouseLeaveHandlers = ref<Record<string, () => void>>({})

  const addCadastreLayer = (mapInstance: Map) => {
    const fullBaseApiUrl = getFullBaseApiUrl()
    const mapId = getMapId(mapInstance)

    if (!mapInstance.getSource("cadastre-source")) {
      mapInstance.addSource("cadastre-source", {
        type: "vector",
        tiles: [`${fullBaseApiUrl}/tiles/cadastre/cadastre/{z}/{x}/{y}.mvt`],
        minzoom: MIN_ZOOM,
        maxzoom: MAX_ZOOM - 1
      })
    }

    const beforeId = mapInstance.getLayer(TERRA_DRAW_POLYGON_LAYER)
      ? TERRA_DRAW_POLYGON_LAYER
      : undefined

    if (!mapInstance.getLayer("cadastre-fill")) {
      mapInstance.addLayer(
        {
          id: "cadastre-fill",
          type: "fill",
          source: "cadastre-source",
          "source-layer": "cadastre--cadastre",
          paint: {
            "fill-color": CADASTRE_COLOR,
            "fill-opacity": 0.0
          }
        },
        beforeId
      )
    }

    if (!mapInstance.getLayer("cadastre-border")) {
      mapInstance.addLayer(
        {
          id: "cadastre-border",
          type: "line",
          source: "cadastre-source",
          "source-layer": "cadastre--cadastre",
          paint: {
            "line-color": CADASTRE_COLOR,
            "line-width": CADASTRE_BORDER_WIDTH,
            "line-opacity": CADASTRE_BORDER_OPACITY
          }
        },
        beforeId
      )
    }

    const clickHandler = (e: any) => {
      if (!e.features || e.features.length === 0) return

      const featureProps = e.features[0].properties
      const parcelId = featureProps.parcel_id

      selectedCadastreParcel.value = {
        parcelId: parcelId ?? "",
        section: featureProps.section ?? "",
        numero: featureProps.numero ?? "",
        surface: featureProps.surface ?? null
      }

      mapInstance.setPaintProperty("cadastre-fill", "fill-opacity", [
        "match",
        ["get", "parcel_id"],
        parcelId,
        CADASTRE_SELECTED_FILL_OPACITY,
        CADASTRE_DEFAULT_FILL_OPACITY
      ])
      mapInstance.setPaintProperty("cadastre-border", "line-width", [
        "match",
        ["get", "parcel_id"],
        parcelId,
        CADASTRE_SELECTED_BORDER_WIDTH,
        CADASTRE_BORDER_WIDTH
      ])
      mapInstance.setPaintProperty("cadastre-border", "line-opacity", [
        "match",
        ["get", "parcel_id"],
        parcelId,
        CADASTRE_SELECTED_BORDER_OPACITY,
        CADASTRE_BORDER_OPACITY
      ])
    }

    const mouseEnterHandler = () => {
      mapInstance.getCanvas().style.cursor = "pointer"
    }
    const mouseLeaveHandler = () => {
      mapInstance.getCanvas().style.cursor = ""
    }

    mapInstance.on("click", "cadastre-fill", clickHandler)
    mapInstance.on("mouseenter", "cadastre-fill", mouseEnterHandler)
    mapInstance.on("mouseleave", "cadastre-fill", mouseLeaveHandler)

    cadastreClickHandlers.value[mapId] = clickHandler
    cadastreMouseEnterHandlers.value[mapId] = mouseEnterHandler
    cadastreMouseLeaveHandlers.value[mapId] = mouseLeaveHandler

    mapInstance.once("render", () => {
      console.info("cypress: cadastre data loaded")
    })
  }

  const clearCadastreSelection = () => {
    if (!selectedCadastreParcel.value) return
    selectedCadastreParcel.value = null

    for (const mapId of Object.keys(mapInstancesByIds.value)) {
      const mapInstance = mapInstancesByIds.value[mapId]
      if (!mapInstance.getLayer("cadastre-fill")) continue
      mapInstance.setPaintProperty("cadastre-fill", "fill-opacity", CADASTRE_DEFAULT_FILL_OPACITY)
      mapInstance.setPaintProperty("cadastre-border", "line-width", CADASTRE_BORDER_WIDTH)
      mapInstance.setPaintProperty("cadastre-border", "line-opacity", CADASTRE_BORDER_OPACITY)
    }
  }

  const removeCadastreLayer = (mapInstance: Map) => {
    const mapId = getMapId(mapInstance)

    selectedCadastreParcel.value = null

    if (cadastreClickHandlers.value[mapId]) {
      mapInstance.off("click", "cadastre-fill", cadastreClickHandlers.value[mapId])
      delete cadastreClickHandlers.value[mapId]
    }
    if (cadastreMouseEnterHandlers.value[mapId]) {
      mapInstance.off("mouseenter", "cadastre-fill", cadastreMouseEnterHandlers.value[mapId])
      delete cadastreMouseEnterHandlers.value[mapId]
    }
    if (cadastreMouseLeaveHandlers.value[mapId]) {
      mapInstance.off("mouseleave", "cadastre-fill", cadastreMouseLeaveHandlers.value[mapId])
      delete cadastreMouseLeaveHandlers.value[mapId]
    }

    if (mapInstance.getLayer("cadastre-fill")) {
      mapInstance.removeLayer("cadastre-fill")
    }
    if (mapInstance.getLayer("cadastre-border")) {
      mapInstance.removeLayer("cadastre-border")
    }
    if (mapInstance.getSource("cadastre-source")) {
      mapInstance.removeSource("cadastre-source")
    }

    mapInstance.once("render", () => {
      console.info("cypress: cadastre data removed")
    })
  }

  const toggleCadastreLayer = () => {
    showCadastreLayer.value = !showCadastreLayer.value

    for (const mapId of Object.keys(mapInstancesByIds.value)) {
      const mapInstance = mapInstancesByIds.value[mapId]

      if (showCadastreLayer.value) {
        addCadastreLayer(mapInstance)
      } else {
        removeCadastreLayer(mapInstance)
      }
    }
  }

  const initMap = (mapId: string, initialDatatype: DataType) => {
    selectedDataType.value = initialDatatype
    controlsAdded.value[mapId] = false

    mapInstancesByIds.value[mapId] = markRaw(
      new Map({
        container: mapId,
        style: loadMapStyle(MapStyle.OSM),
        maxZoom: MAX_ZOOM,
        minZoom: MIN_ZOOM,
        attributionControl: false
      })
    )

    const mapInstance = mapInstancesByIds.value[mapId]

    const onMapReady = async () => {
      setupControls(mapInstance)
      initTiles(mapInstance)
      shapeDrawing.initDraw(mapInstance)
      shapeDrawing.onShapeFinished(() => {
        markShapeFinished()
        recomputeLiveArea()
        requestScoreIfWithinLimit()
      })
      shapeDrawing.onShapeChanged(() => {
        recomputeLiveArea()
        if (shapeEditing.value) {
          requestScoreIfWithinLimit()
        }
      })
      mapInstance.off("click", handleEditingMapClick)
      mapInstance.on("click", handleEditingMapClick)
      mapInstance.once("render", () => {
        console.info(`cypress: map data ${selectedMapStyle.value!} loaded`)
        console.info(
          `cypress: layer: ${getLayerId(selectedDataType.value!, getGeoLevelFromDataType())} and source: ${getSourceId(selectedDataType.value!, getGeoLevelFromDataType())} loaded.`
        )
      })
    }

    if (mapInstance.isStyleLoaded()) {
      onMapReady()
    } else {
      mapInstance.once("style.load", onMapReady)
    }

    mapInstance.on("moveend", () => {
      currentZoom.value = mapInstance.getZoom()
    })
    mapInstance.once("load", () => {
      const center = mapInstance.getCenter()
      clickCoordinates.value = {
        lat: center.lat,
        lng: center.lng
      }
    })
  }

  const changeSelectionMode = (mode: SelectionMode) => {
    selectionMode.value = mode

    contextData.removeData()

    shapeDrawing.setMode(mode)

    if (mode === SelectionMode.POINT) {
      shapeDrawing.stopDrawing()
    }
  }

  const MIN_LOADING_DURATION_MS = 500

  const performCalculation = async () => {
    isCalculating.value = true
    contextData.error.value = false
    const loadingStartTime = Date.now()

    try {
      const scores = await shapeDrawing.getScoresInShape(selectedDataType.value!)

      if (scores) {
        contextData.data.value = scores
      }
    } catch (e) {
      console.error("Error retrieving scores in shape:", e)
      contextData.data.value = null
      contextData.error.value = true
    } finally {
      const loadingDuration = Date.now() - loadingStartTime
      if (loadingDuration < MIN_LOADING_DURATION_MS) {
        await new Promise((resolve) =>
          setTimeout(resolve, MIN_LOADING_DURATION_MS - loadingDuration)
        )
      }
      isCalculating.value = false
    }
  }

  const finishShapeSelection = useDebounceFn(performCalculation, 500, { maxWait: 1000 })

  const isShapeMode = computed(() => selectionMode.value !== SelectionMode.POINT)

  const hasShapeContextData = computed(
    () =>
      isShapeMode.value &&
      !isCalculating.value &&
      !contextData.error.value &&
      contextData.data.value != null
  )

  const getDrawnPolygon = (): ZonePolygon | null => {
    const ring = shapeDrawing.getCurrentShapeCoordinates()
    if (!ring || ring.length < 3) return null
    return { type: "Polygon", coordinates: [ring as [number, number][]] }
  }

  const retryContextData = () => {
    if (isShapeMode.value) {
      performCalculation()
    } else {
      contextData.retry()
    }
  }

  const drawingState = computed<"point" | "drawing" | "editing">(() => {
    if (selectionMode.value === SelectionMode.POINT) return "point"
    return shapeEditing.value ? "editing" : "drawing"
  })

  const recomputeLiveArea = () => {
    const ring = shapeDrawing.getCurrentShapeCoordinates()
    liveArea.value = ring ? computePolygonAreaM2(ring) : null
  }

  const isAreaTooLarge = computed(
    () => liveArea.value !== null && liveArea.value > MAX_SHAPE_AREA_M2
  )

  const requestScoreIfWithinLimit = () => {
    if (isAreaTooLarge.value) {
      contextData.removeData()
    } else {
      finishShapeSelection()
    }
  }

  const resetToDrawingState = (mode: SelectionMode) => {
    shapeEditing.value = false
    liveArea.value = null
    changeSelectionMode(mode)
  }

  const enterShapeMode = (mode: SelectionMode) => resetToDrawingState(mode)

  const startNewShape = (mode: SelectionMode) => resetToDrawingState(mode)

  const markShapeFinished = () => {
    shapeEditing.value = true
  }

  const REDRAW_MARGIN_PX = 24

  const handleEditingMapClick = (e: { point: { x: number; y: number } }) => {
    if (drawingState.value !== "editing") return
    const map = mapInstancesByIds.value["default"]
    const ring = shapeDrawing.getCurrentShapeCoordinates()
    if (!map || !ring) return

    const screen = ring.map((coord) => map.project(coord as [number, number]))
    const xs = screen.map((p) => p.x)
    const ys = screen.map((p) => p.y)
    const outside =
      e.point.x < Math.min(...xs) - REDRAW_MARGIN_PX ||
      e.point.x > Math.max(...xs) + REDRAW_MARGIN_PX ||
      e.point.y < Math.min(...ys) - REDRAW_MARGIN_PX ||
      e.point.y > Math.max(...ys) + REDRAW_MARGIN_PX

    if (outside) startNewShape(selectionMode.value)
  }

  const exitShapeMode = () => {
    shapeEditing.value = false
    liveArea.value = null
    shapeDrawing.clearDrawing()
    changeSelectionMode(SelectionMode.POINT)
  }

  const toggle3D = () => {
    use3D.value = !use3D.value
    Object.keys(mapInstancesByIds.value).forEach((mapId) => {
      const mapInstance = mapInstancesByIds.value[mapId]
      if (use3D.value) {
        mapInstance.easeTo({ pitch: 45, duration: 500 })
      } else {
        mapInstance.easeTo({ pitch: 0, duration: 500 })
      }
    })
    refreshLayers()
    Object.values(mapInstancesByIds.value).forEach((mapInstance) => {
      if (use3D.value) {
        applyVegestrateTerrain(mapInstance, selectedDataType.value!)
      } else {
        clearTerrain(mapInstance)
      }
    })
  }

  const zoomTo = (targetZoom: number) => {
    const mapInstance = mapInstancesByIds.value["default"]
    if (!mapInstance) return
    mapInstance.easeTo({
      center: [clickCoordinates.value.lng, clickCoordinates.value.lat],
      zoom: targetZoom,
      duration: 600
    })
    mapInstance.once("idle", recalculateAtSelection)
  }

  return {
    mapInstancesByIds,
    initMap,
    selectedDataType,
    selectedMapStyle,
    changeMapStyle,
    changeDataType,
    refreshDatatype,
    getMapInstance,
    vulnerabilityMode,
    currentZoom,
    clickCoordinates,
    selectedLegendCell,
    selectionMode,
    isShapeMode,
    hasShapeContextData,
    getDrawnPolygon,
    shapeEditing,
    liveArea,
    isAreaTooLarge,
    drawingState,
    enterShapeMode,
    startNewShape,
    markShapeFinished,
    handleEditingMapClick,
    exitShapeMode,
    changeSelectionMode,
    finishShapeSelection,
    isCalculating,
    shapeDrawing: {
      isDrawing: shapeDrawing.isDrawing,
      drawingPoints: shapeDrawing.drawingPoints,
      currentMode: shapeDrawing.currentMode,
      setMode: shapeDrawing.setMode,
      clearDrawing: shapeDrawing.clearDrawing,
      getSelectedFeatures: shapeDrawing.getSelectedFeatures,
      onShapeFinished: shapeDrawing.onShapeFinished,
      onShapeChanged: shapeDrawing.onShapeChanged,
      getCurrentShapeCoordinates: shapeDrawing.getCurrentShapeCoordinates,
      finishCurrentPolygon: shapeDrawing.finishCurrentPolygon
    },
    contextData: {
      data: contextData.data,
      error: contextData.error,
      setData: contextData.setData,
      setMultipleData: contextData.setMultipleData,
      removeData: contextData.removeData,
      retry: retryContextData,
      toggleContextData: contextData.toggleContextData
    },
    clearAllFilters,
    applyFilters,
    hasActiveFilters,
    isFiltered,
    filteredValues,
    toggleFilter,
    activeFiltersCount,
    toggleAndApplyFilter,
    resetFilters,
    showQPVLayer,
    toggleQPVLayer,
    showBoundaryLayer,
    toggleBoundaryLayer,
    showCadastreLayer,
    toggleCadastreLayer,
    selectedCadastreParcel,
    clearCadastreSelection,
    use3D,
    toggle3D,
    zoomTo,
    showVegestrateHeight,
    toggleVegestrateHeight,
    vegestrateHeightRanges,
    setVegestrateHeightRanges,
    vegetationHeightAtPoint
  }
})
