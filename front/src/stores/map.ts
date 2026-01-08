import { computed, ref } from "vue"
import { defineStore } from "pinia"
import { useDebounceFn } from "@vueuse/core"
import { useMapFilters } from "@/composables/useMapFilters"
import {
  Map,
  NavigationControl,
  AttributionControl,
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
import {
  GeoLevel,
  DataType,
  MapStyle,
  SelectionMode,
  DataTypeToGeolevel,
  getDataTypeAttributionSource
} from "@/utils/enum"
import mapStyles from "@/map/map-style.json"
import { getFullBaseApiUrl } from "@/api"
import { getQPVData } from "@/services/qpvService"
import { VulnerabilityMode as VulnerabilityModeType } from "@/utils/vulnerability"

import { VULNERABILITY_COLOR_MAP } from "@/utils/vulnerability"
import { PLANTABILITY_COLOR_MAP } from "@/utils/plantability"
import { BIOSPHERE_FUNCTIONAL_INTEGRITY_COLOR_MAP } from "@/utils/biosphere_functional_integrity"
import { generateBivariateColorExpression } from "@/utils/plantability_vulnerability"
import { CLIMATE_ZONE_MAP_COLOR_MAP } from "@/utils/climateZone"
import MaplibreGeocoder from "@maplibre/maplibre-gl-geocoder"
import { geocoderApi } from "@/utils/geocoder"
import "@maplibre/maplibre-gl-geocoder/dist/maplibre-gl-geocoder.css"
import maplibreGl from "maplibre-gl"
import { extractFeatureProperty, getLayerId, getSourceId, highlightFeature } from "@/utils/map"
import { useContextData } from "@/composables/useContextData"
import { getBivariateCoordinates } from "@/utils/plantability_vulnerability"
import { addCenterControl } from "@/utils/mapControls"
import { useShapeDrawing } from "@/composables/useTerraDraw"

export const useMapStore = defineStore("map", () => {
  const mapInstancesByIds = ref<Record<string, Map>>({})
  const mapEventsListener = ref<Record<string, (e: any) => void>>({})
  const selectedDataType = ref<DataType>(DataType.PLANTABILITY)
  const selectedMapStyle = ref<MapStyle>(MapStyle.OSM)
  const vulnerabilityMode = ref<VulnerabilityModeType>(VulnerabilityModeType.DAY)
  const currentZoom = ref<number>(14)
  const contextData = useContextData()
  const showQPVLayer = ref<boolean>(false)
  const selectionMode = ref<SelectionMode>(SelectionMode.POINT)
  const isToolbarVisible = ref<boolean>(false)
  const shapeDrawing = useShapeDrawing()
  const clickCoordinates = ref<{ lat: number; lng: number }>({
    lat: DEFAULT_MAP_CENTER.lat,
    lng: DEFAULT_MAP_CENTER.lng
  })
  const isCalculating = ref<boolean>(false)

  const selectedLegendCell = ref<{ plantability: number; vulnerability: number } | null>(null)

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
    const bivariateExpression = generateBivariateColorExpression()

    return {
      [DataType.PLANTABILITY]: ["match", ["get", "indice"], ...PLANTABILITY_COLOR_MAP],
      [DataType.VULNERABILITY]: [
        "match",
        ["get", `indice_${vulnerabilityMode.value}`],
        ...VULNERABILITY_COLOR_MAP
      ],
      [DataType.CLIMATE_ZONE]: ["match", ["get", "indice"], ...CLIMATE_ZONE_MAP_COLOR_MAP],
      [DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY]: [
        "match",
        ["get", "indice"],
        ...BIOSPHERE_FUNCTIONAL_INTEGRITY_COLOR_MAP
      ],
      [DataType.PLANTABILITY_VULNERABILITY]: bivariateExpression
    }
  })

  const getAttributionSource = async () => {
    const sourceCode =
      "<a href='https://github.com/TelesCoop/iarbre' target='_blank'>Code source</a> | <a href='https://iarbre.fr' target='_blank'>À propos</a>"
    if (!selectedDataType.value) return sourceCode
    const attribution = await getDataTypeAttributionSource(selectedDataType.value)
    return `${attribution} | ${sourceCode}`
  }
  const getGeoLevelFromDataType = () => {
    return DataTypeToGeolevel[selectedDataType.value!]
  }
  const attributionControl = ref(
    new AttributionControl({
      compact: true,
      customAttribution: ""
    })
  )
  const navControl = ref(
    new NavigationControl({
      visualizePitch: false,
      visualizeRoll: false,
      showZoom: true,
      showCompass: false
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
  const geocoderControl = ref(
    new MaplibreGeocoder(
      {
        forwardGeocode: geocoderApi.forwardGeocode
      },
      {
        // @ts-ignore
        maplibregl: maplibreGl,
        marker: false,
        showResultsWhileTyping: true,
        countries: "FR",
        placeholder: "Recherche",
        clearOnBlur: true,
        collapsed: true,
        enableEventLogging: false
      }
    )
  )

  const centerControl = ref({
    onAdd: (map: Map) => addCenterControl(map),
    onRemove: () => {
      const controlElement = document.getElementsByClassName("maplibregl-ctrl-center-container")[0]
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

    const fillLayer: AddLayerObject = {
      id: layerId,
      type: "fill",
      source: sourceId,
      "source-layer": `${geolevel}--${datatype === DataType.PLANTABILITY_VULNERABILITY ? DataType.PLANTABILITY : datatype}`,
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
      "source-layer": `${geolevel}--${datatype === DataType.PLANTABILITY_VULNERABILITY ? DataType.PLANTABILITY : datatype}`,
      layout: {},
      paint: {
        "line-color": "#00000000",
        "line-width": 0
      }
    }

    return [fillLayer, lineLayer]
  }

  const setupClickEventOnTile = (map: Map, datatype: DataType, geolevel: GeoLevel) => {
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
      map.addLayer(layer, beforeId)
    })

    setupClickEventOnTile(map, datatype, geolevel)
  }

  const setupSource = (map: Map, datatype: DataType, geolevel: GeoLevel) => {
    const fullBaseApiUrl = getFullBaseApiUrl()
    const tileDataType =
      datatype === DataType.PLANTABILITY_VULNERABILITY ? DataType.PLANTABILITY : datatype
    const tileUrl = `${fullBaseApiUrl}/tiles/${geolevel}/${tileDataType}/{z}/{x}/{y}.mvt`
    const sourceId = getSourceId(datatype, geolevel)
    map.addSource(sourceId, {
      type: "vector",
      tiles: [tileUrl],
      minzoom: MIN_ZOOM
    })
  }

  const removeControls = (map: Map) => {
    map.removeControl(attributionControl.value)
    map.removeControl(navControl.value)
    map.removeControl(centerControl.value)
    map.removeControl(geocoderControl.value as unknown as maplibreGl.IControl)
  }
  const setupControls = async (map: Map) => {
    // Add the new attribution control
    const attribution = await getAttributionSource()
    attributionControl.value = new AttributionControl({
      compact: true,
      customAttribution: attribution
    })
    map.addControl(attributionControl.value, MAP_CONTROL_POSITION)
    map.addControl(navControl.value, MAP_CONTROL_POSITION)
    map.addControl(centerControl.value, MAP_CONTROL_POSITION)
    map.addControl(geocoderControl.value as unknown as maplibreGl.IControl, MAP_CONTROL_POSITION)
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
        mapInstance.removeLayer(layerId)
        mapInstance.removeLayer(`${layerId}-border`)
        mapInstance.removeSource(getSourceId(previousDataType, previousGeoLevel))
      }
      removeControls(mapInstance)
      initTiles(mapInstance)
      if (showQPVLayer.value) {
        addQPVLayer(mapInstance)
      }
      setupControls(mapInstance).catch(console.error)
      // MapComponent is listening to moveend event
      mapInstance.fire("moveend")
    })

    // If a geometry is drawn, automatically recalculate with the new data type
    const features = shapeDrawing.getSelectedFeatures()
    if (features.length > 0 && selectionMode.value !== SelectionMode.POINT) {
      finishShapeSelection()
    }
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
        mapInstance.setStyle(newStyle)
      }
      if (showQPVLayer.value) {
        addQPVLayer(mapInstance)
      }
      mapInstance.fire("style.load")
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

    mapInstancesByIds.value[mapId] = new Map({
      container: mapId, // container id
      style: mapStyles.OSM as maplibregl.StyleSpecification,
      maxZoom: MAX_ZOOM,
      minZoom: MIN_ZOOM,
      attributionControl: false
    })

    const mapInstance = mapInstancesByIds.value[mapId]
    mapInstance.on("style.load", async () => {
      await setupControls(mapInstance)
      initTiles(mapInstance)
      // Initialize shape drawing
      shapeDrawing.initDraw(mapInstance)
      // Configure automatic calculation when a shape is finished
      shapeDrawing.onShapeFinished(() => {
        finishShapeSelection()
      })
    })

    mapInstance.on("moveend", () => {
      currentZoom.value = mapInstance.getZoom()
    })
    mapInstance.on("load", () => {
      const center = mapInstance.getCenter()
      clickCoordinates.value = {
        lat: center.lat,
        lng: center.lng
      }
    })
    mapInstance.once("render", () => {
      console.info(`cypress: map data ${selectedMapStyle.value!} loaded`)
      console.info(
        `cypress: layer: ${getLayerId(selectedDataType.value!, getGeoLevelFromDataType())} and source: ${getSourceId(selectedDataType.value!, getGeoLevelFromDataType())} loaded.`
      )
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

  return {
    mapInstancesByIds,
    initMap,
    selectedDataType,
    selectedMapStyle,
    changeMapStyle,
    changeDataType,
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
    toggleQPVLayer
  }
})
