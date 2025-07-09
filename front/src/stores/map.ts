import { computed, ref } from "vue"
import { defineStore } from "pinia"
import { useMapFilters } from "@/composables/useMapFilters"
import {
  Map,
  Popup,
  NavigationControl,
  AttributionControl,
  type AddLayerObject,
  type DataDrivenPropertyValueSpecification
} from "maplibre-gl"
import { MAP_CONTROL_POSITION, MAX_ZOOM, MIN_ZOOM } from "@/utils/constants"
import {
  GeoLevel,
  DataType,
  MapStyle,
  DataTypeToGeolevel,
  DataTypeToAttributionSource
} from "@/utils/enum"
import mapStyles from "../../public/map/map-style.json"
import type { MapScorePopupData } from "@/types/map"
import { FULL_BASE_API_URL } from "@/api"
import { getQPVData } from "@/services/qpvService"
import { VulnerabilityMode as VulnerabilityModeType } from "@/utils/vulnerability"

import { VULNERABILITY_COLOR_MAP } from "@/utils/vulnerability"
import { PLANTABILITY_COLOR_MAP } from "@/utils/plantability"
import { CLIMATE_ZONE_MAP_COLOR_MAP } from "@/utils/climateZone"
import MaplibreGeocoder from "@maplibre/maplibre-gl-geocoder"
import { geocoderApi } from "@/utils/geocoder"
import "@maplibre/maplibre-gl-geocoder/dist/maplibre-gl-geocoder.css"
import maplibreGl from "maplibre-gl"
import {
  clearHighlight,
  extractFeatureProperties,
  extractFeatureProperty,
  getLayerId,
  getSourceId,
  highlightFeature
} from "@/utils/map"
import { useContextData } from "@/composables/useContextData"
import { addCenterControl } from "@/utils/mapControls"
import { useAppStore } from "./app"

export const useMapStore = defineStore("map", () => {
  const mapInstancesByIds = ref<Record<string, Map>>({})
  const POPUP_MAX_WIDTH = "400px"
  const MOBILE_MAX_WIDTH = "300px"
  const popupData = ref<MapScorePopupData | undefined>(undefined)
  const popupDomElement = ref<HTMLElement | null>(null)
  const mapEventsListener = ref<Record<string, (e: any) => void>>({})
  const activePopup = ref<Popup | null>(null)
  const selectedDataType = ref<DataType>(DataType.PLANTABILITY)
  const selectedMapStyle = ref<MapStyle>(MapStyle.OSM)
  const vulnerabilityMode = ref<VulnerabilityModeType>(VulnerabilityModeType.DAY)
  const currentZoom = ref<number>(14)
  const contextData = useContextData()
  const showQPVLayer = ref<boolean>(false)

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
    return {
      [DataType.PLANTABILITY]: ["match", ["get", "indice"], ...PLANTABILITY_COLOR_MAP],
      [DataType.VULNERABILITY]: [
        "match",
        ["get", `indice_${vulnerabilityMode.value}`],
        ...VULNERABILITY_COLOR_MAP
      ],
      [DataType.CLIMATE_ZONE]: ["match", ["get", "indice"], ...CLIMATE_ZONE_MAP_COLOR_MAP]
    }
  })

  const getAttributionSource = () => {
    const sourceCode =
      "<a href='https://github.com/TelesCoop/iarbre' target='_blank'>Code source</a> | <a href='https://iarbre.fr' target='_blank'>À propos</a>"
    if (!selectedDataType.value) return sourceCode
    return `${DataTypeToAttributionSource[selectedDataType.value]} | ${sourceCode}`
  }
  const getGeoLevelFromDataType = () => {
    return DataTypeToGeolevel[selectedDataType.value!]
  }
  const attributionControl = ref(
    new AttributionControl({
      compact: true,
      customAttribution: getAttributionSource()
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
    onRemove: (map: Map) => {
      const controlElement = document.getElementsByClassName("maplibregl-ctrl-center-container")[0]
      if (controlElement) {
        controlElement.remove()
      }
    }
  })

  const removeActivePopup = () => {
    if (activePopup.value) {
      activePopup.value.remove()
      activePopup.value = null
      popupData.value = undefined
    }
  }

  const getMapInstance = (mapId: string): Map => {
    return mapInstancesByIds.value[mapId]
  }

  const createMapLayer = (
    datatype: DataType,
    geolevel: GeoLevel,
    sourceId: string
  ): AddLayerObject => {
    const layerId = getLayerId(datatype, geolevel)
    return {
      id: layerId,
      type: "fill",
      source: sourceId,
      "source-layer": `${geolevel}--${datatype}`,
      layout: {},
      paint: {
        "fill-color": FILL_COLOR_MAP.value[
          datatype
        ] as DataDrivenPropertyValueSpecification<"ExpressionSpecification">,
        "fill-outline-color": "#00000000",
        "fill-opacity": 0.5
      }
    }
  }

  function createStripesPattern(value: number) {
    // Calculer l'espacement des rayures (plus la valeur est élevée, plus les rayures sont proches)
    const spacing = Math.max(2, 20 - value * 2) // Espacement de 2px à 18px

    // Créer un canvas pour le pattern
    const canvas = document.createElement("canvas")
    const ctx = canvas.getContext("2d")

    // Taille du pattern
    const size = spacing * 2
    canvas.width = size
    canvas.height = size

    // Fond transparent
    ctx.clearRect(0, 0, size, size)

    // Dessiner les rayures diagonales noires
    ctx.strokeStyle = "black"
    ctx.lineWidth = 1

    // Rayures diagonales (45 degrés)
    ctx.beginPath()
    for (let i = -size; i <= size * 2; i += spacing) {
      ctx.moveTo(i, 0)
      ctx.lineTo(i + size, size)
    }
    ctx.stroke()

    return canvas
  }

  const setupStrippedPattern = (map: Map) => {
    // Add stripped pattern images from public repo
    map
      .loadImage("/map/stripped-1.png")
      .then((response) => {
        map.addImage("stripes-1", response.data)
        map.addImage("stripes-2", response.data)
        map.addImage("stripes-3", response.data)
        map.addImage("stripes-4", response.data)
        map.addImage("stripes-5", response.data)
      })
      .catch((error) => {
        console.error("Failed to load stripped-1.png:", error)
      })

    map
      .loadImage("/map/stripped-2.png")
      .then((response) => {
        map.addImage("stripes-6", response.data)
        map.addImage("stripes-7", response.data)
        map.addImage("stripes-8", response.data)
        map.addImage("stripes-9", response.data)
      })
      .catch((error) => {
        console.error("Failed to load stripped-2.png:", error)
      })
  }

  const createStrippedMapLayer = (
    datatype: DataType,
    geolevel: GeoLevel,
    sourceId: string
  ): [AddLayerObject, AddLayerObject] => {
    const layerId = getLayerId(datatype, geolevel)
    return [
      {
        id: layerId,
        type: "fill",
        source: sourceId,
        "source-layer": `${geolevel}--${datatype}`,
        layout: {},
        paint: {
          "fill-pattern": [
            "match",
            ["get", `indice_${vulnerabilityMode.value}`],
            1,
            "stripes-1",
            2,
            "stripes-2",
            3,
            "stripes-3",
            4,
            "stripes-4",
            5,
            "stripes-5",
            6,
            "stripes-6",
            7,
            "stripes-7",
            8,
            "stripes-8",
            9,
            "stripes-9",
            "stripes-1" // valeur par défaut
          ]
        }
      },
      {
        id: `${layerId}-border`,
        type: "fill",
        source: sourceId,
        "source-layer": `${geolevel}--${datatype}`,
        layout: {},
        paint: {
          "line-width": 10,
          // black
          "fill-outline-color": "#000000"
        }
      }
    ]
  }

  const createPopup = (
    e: any,
    map: Map,
    datatype: DataType,
    geolevel: GeoLevel,
    layerId: string
  ) => {
    if (!popupDomElement.value) {
      throw new Error("Popup DOM element is not defined")
    }

    removeActivePopup()
    popupData.value = {
      id: extractFeatureProperty(e.features!, datatype, geolevel, "id"),
      lng: e.lngLat.lng,
      lat: e.lngLat.lat,
      properties: extractFeatureProperties(e.features!, datatype, geolevel),
      score: extractFeatureProperty(e.features!, datatype, geolevel, `indice`)
    }
    const maxWidth = useAppStore().isMobile ? MOBILE_MAX_WIDTH : POPUP_MAX_WIDTH
    const popup = new Popup().setLngLat(e.lngLat).setMaxWidth(maxWidth)
    activePopup.value = popup.setDOMContent(popupDomElement.value).addTo(map)
    const closeButton = document.getElementsByClassName("maplibregl-popup-close-button")[0]
    closeButton.addEventListener("click", () => {
      clearHighlight(map, layerId)
      contextData.removeData()
    })
  }

  const setupClickEventOnTile = (map: Map, datatype: DataType, geolevel: GeoLevel) => {
    const layerId = getLayerId(datatype, geolevel)
    if (mapEventsListener.value[layerId]) {
      map.off("click", layerId, mapEventsListener.value[layerId])
    }
    const clickHandler = (e: any) => {
      const featureId = extractFeatureProperty(e.features!, datatype, geolevel, "id")
      highlightFeature(map, layerId, featureId)
      createPopup(e, map, datatype, geolevel, layerId)
      if (contextData.data.value) {
        contextData.setData(featureId)
      }
    }
    map.on("click", layerId, clickHandler)
    mapEventsListener.value[layerId] = clickHandler
  }
  const setupTile = (map: Map, datatype: DataType, geolevel: GeoLevel) => {
    if (datatype === DataType.MIX_PLANTABILITY_AND_VULNERABILITY) {
      const layer = createMapLayer(
        DataType.PLANTABILITY,
        DataTypeToGeolevel[DataType.PLANTABILITY],
        getSourceId(DataType.PLANTABILITY, DataTypeToGeolevel[DataType.PLANTABILITY])
      )

      const layer2 = createStrippedMapLayer(
        DataType.VULNERABILITY,
        DataTypeToGeolevel[DataType.VULNERABILITY],
        getSourceId(DataType.VULNERABILITY, DataTypeToGeolevel[DataType.VULNERABILITY])
      )
      map.addLayer(layer)
      map.addLayer(layer2[0], layer.id)
      map.addLayer(layer2[1], layer2[0].id)
    } else {
      const sourceId = getSourceId(datatype, geolevel)

      const layer = createMapLayer(datatype, geolevel, sourceId)
      map.addLayer(layer)
    }

    setupClickEventOnTile(map, datatype, geolevel)
  }

  const getSourceTileUrl = (datatype: DataType, geolevel: GeoLevel) => {
    return `${FULL_BASE_API_URL}/tiles/${geolevel}/${datatype}/{z}/{x}/{y}.mvt`
  }
  const getSourceIds = (dataType: DataType, geoLevel: GeoLevel) => {
    const sourceIds = []
    if (dataType !== DataType.MIX_PLANTABILITY_AND_VULNERABILITY) {
      sourceIds.push(getSourceId(dataType, geoLevel))
    } else {
      sourceIds.push(getSourceId(DataType.PLANTABILITY, DataTypeToGeolevel[DataType.PLANTABILITY]))
      sourceIds.push(
        getSourceId(DataType.VULNERABILITY, DataTypeToGeolevel[DataType.VULNERABILITY])
      )
    }
    return sourceIds
  }
  const setupSource = (map: Map, datatype: DataType, geolevel: GeoLevel) => {
    let tilesUrl = []

    if (datatype !== DataType.MIX_PLANTABILITY_AND_VULNERABILITY) {
      const sourceId = getSourceId(datatype, geolevel)

      tilesUrl = [getSourceTileUrl(datatype, geolevel)]
      map.addSource(sourceId, {
        type: "vector",
        tiles: tilesUrl,
        minzoom: MIN_ZOOM
      })
    } else {
      const source1 = getSourceId(DataType.PLANTABILITY, DataTypeToGeolevel[DataType.PLANTABILITY])
      const source2 = getSourceId(
        DataType.VULNERABILITY,
        DataTypeToGeolevel[DataType.VULNERABILITY]
      )
      map.addSource(source1, {
        type: "vector",
        tiles: [getSourceTileUrl(DataType.PLANTABILITY, DataTypeToGeolevel[DataType.PLANTABILITY])],
        minzoom: MIN_ZOOM
      })
      map.addSource(source2, {
        type: "vector",
        tiles: [
          getSourceTileUrl(DataType.VULNERABILITY, DataTypeToGeolevel[DataType.VULNERABILITY])
        ],
        minzoom: MIN_ZOOM
      })
    }
  }

  const removeControls = (map: Map) => {
    map.removeControl(attributionControl.value)
    map.removeControl(navControl.value)
    map.removeControl(centerControl.value)
    map.removeControl(geocoderControl.value as unknown as maplibreGl.IControl)
  }
  const setupControls = (map: Map) => {
    // Add the new attribution control
    attributionControl.value = new AttributionControl({
      compact: true,
      customAttribution: getAttributionSource()
    })
    map.addControl(attributionControl.value, MAP_CONTROL_POSITION)
    map.addControl(navControl.value, MAP_CONTROL_POSITION)
    map.addControl(centerControl.value, MAP_CONTROL_POSITION)
    map.addControl(geocoderControl.value as unknown as maplibreGl.IControl, MAP_CONTROL_POSITION)
  }

  const removeSources = (
    mapInstance: Map,
    previousDataType: DataType,
    previousGeoLevel: GeoLevel
  ) => {
    const sourceIds = getSourceIds(previousDataType, previousGeoLevel)
    sourceIds.forEach((sourceId) => {
      mapInstance.removeSource(sourceId)
    })
  }

  const changeDataType = (datatype: DataType) => {
    removeActivePopup()
    const previousDataType = selectedDataType.value!
    const previousGeoLevel = getGeoLevelFromDataType()
    selectedDataType.value = datatype
    // Clear filters when changing data type
    clearAllFilters()
    // Update all map instances with the new layer
    Object.keys(mapInstancesByIds.value).forEach((mapId) => {
      const mapInstance = mapInstancesByIds.value[mapId]
      // Clear QPV if existing
      if (mapInstance.getLayer("qpv-border")) {
        removeQPVLayer(mapInstance)
      }
      // remove existing layers and sources
      if (previousDataType !== null) {
        removeSources(mapInstance, previousDataType, previousGeoLevel)
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
        newStyle = JSON.parse(
          JSON.stringify(mapStyles.CADASTRE).replace("{API_BASE_URL}", FULL_BASE_API_URL)
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
      addQPVLayer(mapInstance)
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
      mapInstance.addLayer({
        id: "qpv-border",
        type: "line",
        source: "qpv-source",
        paint: {
          "line-color": "#ffffff",
          "line-width": 3
        }
      })
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
    mapInstance.on("style.load", () => {
      setupControls(mapInstance)
      setupStrippedPattern(mapInstance)
      initTiles(mapInstance)
      popupDomElement.value = document.getElementById(`popup-${mapId}`)
    })

    mapInstance.on("moveend", () => {
      currentZoom.value = mapInstance.getZoom()
    })
    mapInstance.once("render", () => {
      console.info(`cypress: map data ${selectedMapStyle.value!} loaded`)
      console.info(
        `cypress: layer: ${getLayerId(selectedDataType.value!, getGeoLevelFromDataType())} and source: ${getSourceId(selectedDataType.value!, getGeoLevelFromDataType())} loaded.`
      )
    })
  }

  return {
    mapInstancesByIds,
    initMap,
    popupData,
    selectedDataType,
    selectedMapStyle,
    changeMapStyle,
    changeDataType,
    getMapInstance,
    vulnerabilityMode,
    currentZoom,
    contextData: {
      data: contextData.data,
      setData: contextData.setData,
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
