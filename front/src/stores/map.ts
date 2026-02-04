import { computed, ref } from "vue"
import { defineStore } from "pinia"
import { useDebounceFn } from "@vueuse/core"
import { useMapFilters } from "@/composables/useMapFilters"
import {
  Map,
  NavigationControl,
  type AddLayerObject,
  type DataDrivenPropertyValueSpecification
} from "maplibre-gl"
import {
  MAP_CONTROL_POSITION,
  MAX_ZOOM,
  MIN_ZOOM,
  DEFAULT_MAP_CENTER,
  TERRA_DRAW_POLYGON_LAYER
} from "@/utils/constants"
import { GeoLevel, DataType, MapStyle, SelectionMode, DataTypeToGeolevel } from "@/utils/enum"
import mapStyles from "@/map/map-style.json"
import { getFullBaseApiUrl } from "@/api"
import { getQPVData } from "@/services/qpvService"
import { VulnerabilityMode as VulnerabilityModeType } from "@/utils/vulnerability"

import { VULNERABILITY_COLOR_MAP } from "@/utils/vulnerability"
import { PLANTABILITY_COLOR_MAP } from "@/utils/plantability"
import { generateBivariateColorExpression } from "@/utils/plantability_vulnerability"
import { CLIMATE_ZONE_MAP_COLOR_MAP } from "@/utils/climateZone"
import { extractFeatureProperty, getLayerId, getSourceId, highlightFeature } from "@/utils/map"
import { useContextData } from "@/composables/useContextData"
import { getBivariateCoordinates } from "@/utils/plantability_vulnerability"
import { addCenterControl, add3DControl } from "@/utils/mapControls"
import { useShapeDrawing } from "@/composables/useTerraDraw"

export const useMapStore = defineStore("map", () => {
  const mapInstancesByIds = ref<Record<string, Map>>({})
  const mapEventsListener = ref<Record<string, (e: any) => void>>({})
  const selectedDataType = ref<DataType>(DataType.PLANTABILITY)
  const selectedMapStyle = ref<MapStyle>(MapStyle.OSM)
  const vulnerabilityMode = ref<VulnerabilityModeType>(VulnerabilityModeType.DAY)
  const currentZoom = ref<number>(14)
  const contextData = useContextData(selectedDataType)
  const showQPVLayer = ref<boolean>(false)
  const selectionMode = ref<SelectionMode>(SelectionMode.POINT)
  const isToolbarVisible = ref<boolean>(false)
  const shapeDrawing = useShapeDrawing()
  const clickCoordinates = ref<{ lat: number; lng: number }>({
    lat: DEFAULT_MAP_CENTER.lat,
    lng: DEFAULT_MAP_CENTER.lng
  })
  const isCalculating = ref<boolean>(false)
  const controlsAdded = ref<Record<string, boolean>>({})

  const selectedLegendCell = ref<{ plantability: number; vulnerability: number } | null>(null)
  const use3D = ref<boolean>(false)

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
      [DataType.PLANTABILITY_VULNERABILITY]: bivariateExpression
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
      [DataType.PLANTABILITY_VULNERABILITY]: ["*", ["get", "indice"], HEIGHT_MULTIPLIER]
    }
  })

  const getGeoLevelFromDataType = () => {
    return DataTypeToGeolevel[selectedDataType.value!]
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

    if (datatype === DataType.VEGETATION) {
      // Raster layer for vegetation
      const rasterLayer: AddLayerObject = {
        id: layerId,
        type: "raster",
        source: sourceId,
        layout: {},
        paint: {
          "raster-opacity": 0.7
        }
      }
      return [rasterLayer]
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

  const setupClickEventOnTile = (map: Map, datatype: DataType, geolevel: GeoLevel) => {
    // Skip click events for raster layers (vegetation)
    if (datatype === DataType.VEGETATION) {
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

      // Normal point mode (simple click to select a tile)
      const featureId = extractFeatureProperty(e.features!, datatype, geolevel, "id")
      const score = extractFeatureProperty(e.features!, datatype, geolevel, "indice")
      const sourceValues = extractFeatureProperty(e.features!, datatype, geolevel, "source_values")
      const vulnScoreDay =
        geolevel === GeoLevel.TILE && datatype === DataType.PLANTABILITY_VULNERABILITY
          ? extractFeatureProperty(e.features!, datatype, geolevel, "vulnerability_indice_day")
          : undefined
      const vulnScoreNight =
        geolevel === GeoLevel.TILE && datatype === DataType.PLANTABILITY_VULNERABILITY
          ? extractFeatureProperty(e.features!, datatype, geolevel, "vulnerability_indice_night")
          : undefined
      highlightFeature(map, layerId, featureId)
      // Highlight cell in the legend that correspond to clicked tile
      if (geolevel === GeoLevel.TILE && datatype === DataType.PLANTABILITY_VULNERABILITY) {
        const properties = e.features![0].properties
        if (
          properties &&
          properties.indice !== undefined &&
          properties.vulnerability_indice_day !== undefined
        ) {
          const coords = getBivariateCoordinates(
            properties.indice,
            properties.vulnerability_indice_day
          )
          selectedLegendCell.value = coords
        }
      } else {
        selectedLegendCell.value = null
      }

      // Store click coordinates
      clickCoordinates.value = {
        lat: e.lngLat.lat,
        lng: e.lngLat.lng
      }
      // Conditionally load context data based on geolevel, datatype, and zoom
      if (geolevel === GeoLevel.TILE && datatype === DataType.PLANTABILITY && map.getZoom() < 17) {
        contextData.setData(featureId, score, sourceValues)
      } else if (geolevel === GeoLevel.TILE && datatype === DataType.PLANTABILITY_VULNERABILITY) {
        contextData.setData(featureId, score, sourceValues, vulnScoreDay, vulnScoreNight)
      } else {
        contextData.setData(featureId)
      }
    }
    map.on("click", layerId, clickHandler)
    mapEventsListener.value[layerId] = clickHandler
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

    if (datatype === DataType.VEGETATION) {
      // Raster source for vegetation
      const tileUrl = `${fullBaseApiUrl}/tiles/vegetation/{z}/{x}/{y}.png`
      map.addSource(sourceId, {
        type: "raster",
        tiles: [tileUrl],
        tileSize: 256,
        minzoom: MIN_ZOOM
      })
    } else {
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
    selectedDataType.value = datatype
    clearAllFilters()
    contextData.removeData()
    selectedLegendCell.value = null

    // Update all map instances with the new layer
    Object.keys(mapInstancesByIds.value).forEach((mapId) => {
      const mapInstance = mapInstancesByIds.value[mapId]
      // Clear QPV if existing
      if (mapInstance.getLayer("qpv-border")) {
        removeQPVLayer(mapInstance)
      }
      // remove existing layers and sources
      if (previousDataType !== null) {
        const layerId = getLayerId(previousDataType, previousGeoLevel)
        if (mapInstance.getLayer(layerId)) {
          mapInstance.removeLayer(layerId)
        }
        if (previousDataType !== DataType.VEGETATION && mapInstance.getLayer(`${layerId}-border`)) {
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

  const refreshLayers = () => {
    const currentDataType = selectedDataType.value
    const currentGeoLevel = getGeoLevelFromDataType()
    Object.keys(mapInstancesByIds.value).forEach((mapId) => {
      const mapInstance = mapInstancesByIds.value[mapId]
      const layerId = getLayerId(currentDataType, currentGeoLevel)
      if (mapInstance.getLayer(layerId)) {
        mapInstance.removeLayer(layerId)
      }
      if (currentDataType !== DataType.VEGETATION && mapInstance.getLayer(`${layerId}-border`)) {
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
      // Clear QPV if existing
      if (mapInstance.getLayer("qpv-border")) {
        removeQPVLayer(mapInstance)
      }
      let newStyle: maplibregl.StyleSpecification

      if (mapstyle === MapStyle.CADASTRE) {
        const fullBaseApiUrl = getFullBaseApiUrl()
        newStyle = JSON.parse(
          JSON.stringify(mapStyles.CADASTRE).replace("{API_BASE_URL}", fullBaseApiUrl)
        ) as maplibregl.StyleSpecification
      } else if (mapstyle === MapStyle.SATELLITE) {
        // Reference: https://maplibre.org/maplibre-gl-js/docs/examples/map-tiles/
        // https://www.reddit.com/r/QGIS/comments/q0su5b/comment/hfabj8f/
        newStyle = mapStyles.SATELLITE as maplibregl.StyleSpecification
      } else if (mapstyle === MapStyle.OSM) {
        newStyle = mapStyles.OSM as maplibregl.StyleSpecification
      }

      if (newStyle!) {
        const onStyleReady = () => {
          initTiles(mapInstance)
          setupControls(mapInstance)
          if (showQPVLayer.value) {
            addQPVLayer(mapInstance)
          }
          mapInstance.fire("moveend")
        }

        mapInstance.setStyle(newStyle)
        onStyleReady()
      }
    })
  }

  const initTiles = (mapInstance: Map) => {
    const currentGeoLevel = getGeoLevelFromDataType()
    setupSource(mapInstance, selectedDataType.value!, currentGeoLevel)
    setupTile(mapInstance, selectedDataType.value!, currentGeoLevel)
  }

  // TODO: display loading during the async execution
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

      mapInstance.addLayer(
        {
          id: "qpv-border",
          type: "line",
          source: "qpv-source",
          paint: {
            "line-color": "#ffffff",
            "line-width": 3
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

  const initMap = (mapId: string, initialDatatype: DataType) => {
    selectedDataType.value = initialDatatype
    controlsAdded.value[mapId] = false

    mapInstancesByIds.value[mapId] = new Map({
      container: mapId,
      style: mapStyles.OSM as maplibregl.StyleSpecification,
      maxZoom: MAX_ZOOM,
      minZoom: MIN_ZOOM,
      attributionControl: false
    })

    const mapInstance = mapInstancesByIds.value[mapId]

    const onMapReady = async () => {
      setupControls(mapInstance)
      initTiles(mapInstance)
      shapeDrawing.initDraw(mapInstance)
      // Configure automatic calculation when a shape is finished
      shapeDrawing.onShapeFinished(() => {
        finishShapeSelection()
      })
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

    // Clear contextual data when changing mode
    contextData.removeData()

    // Use Terra Draw to change mode
    shapeDrawing.setMode(mode)

    // In POINT mode (simple click), disable drawing
    if (mode === SelectionMode.POINT) {
      shapeDrawing.stopDrawing()
    }
  }

  const MIN_LOADING_DURATION_MS = 500

  const performCalculation = async () => {
    // Activate loading state
    isCalculating.value = true
    const loadingStartTime = Date.now()

    try {
      // Retrieve aggregated scores in shape via backend API
      const scores = await shapeDrawing.getScoresInShape(selectedDataType.value!)

      if (scores) {
        // Set aggregated scores directly in context
        contextData.data.value = scores
      }
    } finally {
      // Ensure minimum loading duration of 0.5 seconds
      const loadingDuration = Date.now() - loadingStartTime
      if (loadingDuration < MIN_LOADING_DURATION_MS) {
        await new Promise((resolve) =>
          setTimeout(resolve, MIN_LOADING_DURATION_MS - loadingDuration)
        )
      }
      isCalculating.value = false
    }
  }

  // Debounce calculation to avoid multiple rapid calls
  const finishShapeSelection = useDebounceFn(performCalculation, 500, { maxWait: 1000 })

  const isShapeMode = computed(() => selectionMode.value !== SelectionMode.POINT)

  const toggleToolbar = () => {
    isToolbarVisible.value = !isToolbarVisible.value
    // When closing toolbar, return to POINT mode
    if (!isToolbarVisible.value) {
      changeSelectionMode(SelectionMode.POINT)
    }
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
    isToolbarVisible,
    toggleToolbar,
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
      onShapeFinished: shapeDrawing.onShapeFinished
    },
    contextData: {
      data: contextData.data,
      setData: contextData.setData,
      setMultipleData: contextData.setMultipleData,
      removeData: contextData.removeData,
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
    use3D,
    toggle3D
  }
})
