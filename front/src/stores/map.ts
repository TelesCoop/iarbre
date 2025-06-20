import { computed, ref, nextTick } from "vue"
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
import type {
  MapScorePopupData,
  LayerConfig,
  MultiLayerPopupData,
  LayerPopupData
} from "@/types/map"
import { FULL_BASE_API_URL } from "@/api"
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

export const useMapStore = defineStore("map", () => {
  const mapInstancesByIds = ref<Record<string, Map>>({})
  const POPUP_MAX_WIDTH = "400px"
  const popupData = ref<MapScorePopupData | undefined>(undefined)
  const multiLayerPopupData = ref<MultiLayerPopupData | undefined>(undefined)
  const popupDomElement = ref<HTMLElement | null>(null)
  const mapEventsListener = ref<Record<string, (e: any) => void>>({})
  const activePopup = ref<Popup | null>(null)
  const selectedDataType = ref<DataType>(DataType.PLANTABILITY)
  const selectedMapStyle = ref<MapStyle>(MapStyle.OSM)
  const vulnerabilityMode = ref<VulnerabilityModeType>(VulnerabilityModeType.DAY)
  const currentZoom = ref<number>(14)
  const contextData = useContextData()

  // Nouvelle gestion multi-calques
  const activeLayers = ref<LayerConfig[]>([
    {
      dataType: DataType.PLANTABILITY,
      visible: true,
      opacity: 0.7,
      zIndex: 1,
      filters: []
    }
  ])

  const isMultiLayerMode = ref<boolean>(false)

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
      multiLayerPopupData.value = undefined
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
    const popup = new Popup().setLngLat(e.lngLat).setMaxWidth(POPUP_MAX_WIDTH)
    activePopup.value = popup.setDOMContent(popupDomElement.value).addTo(map)
    const closeButton = document.getElementsByClassName("maplibregl-popup-close-button")[0]
    closeButton.addEventListener("click", () => {
      clearHighlight(map, layerId)
      contextData.removeData()
    })
  }

  const setupClickEventOnTile = (map: Map, datatype: DataType, geolevel: GeoLevel) => {
    const layerId = getLayerId(datatype, geolevel)

    // En mode mono-calque seulement : gestionnaire spécifique par calque
    // En mode multi-calques, le gestionnaire global est configuré dans updateMapLayers
    if (!isMultiLayerMode.value) {
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
  }

  const setupGlobalClickHandler = (map: Map) => {
    const globalHandlerKey = "global-multi-layer"

    // Supprimer l'ancien gestionnaire s'il existe
    if (mapEventsListener.value[globalHandlerKey]) {
      map.off("click", mapEventsListener.value[globalHandlerKey])
    }

    const globalClickHandler = (e: any) => {
      createMultiLayerPopup(e, map)
    }

    map.on("click", globalClickHandler)
    mapEventsListener.value[globalHandlerKey] = globalClickHandler
  }
  const setupTile = (map: Map, datatype: DataType, geolevel: GeoLevel) => {
    const sourceId = getSourceId(datatype, geolevel)
    const layer = createMapLayer(datatype, geolevel, sourceId)
    map.addLayer(layer)
    setupClickEventOnTile(map, datatype, geolevel)
  }

  const setupSource = (map: Map, datatype: DataType, geolevel: GeoLevel) => {
    const tileUrl = `${FULL_BASE_API_URL}/tiles/${geolevel}/${datatype}/{z}/{x}/{y}.mvt`
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
      // remove existing layers and sources
      if (previousDataType !== null) {
        mapInstance.removeLayer(getLayerId(previousDataType, previousGeoLevel))
        mapInstance.removeSource(getSourceId(previousDataType, previousGeoLevel))
      }
      removeControls(mapInstance)
      initTiles(mapInstance)
      setupControls(mapInstance)
      // MapComponent is listening to moveend event
      mapInstance.fire("moveend")
    })
  }

  const setLayerZoomLimits = (style: maplibregl.StyleSpecification) => {
    for (const layer of style.layers) {
      layer.minzoom = MIN_ZOOM
      layer.maxzoom = MAX_ZOOM
    }
  }

  const changeMapStyle = (mapstyle: MapStyle) => {
    selectedMapStyle.value = mapstyle
    Object.keys(mapInstancesByIds.value).forEach((mapId) => {
      const mapInstance = mapInstancesByIds.value[mapId]
      removeControls(mapInstance)

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
        setLayerZoomLimits(newStyle)
        mapInstance.setStyle(newStyle)
      }

      mapInstance.fire("style.load")
    })
  }

  const initTiles = (mapInstance: Map) => {
    if (isMultiLayerMode.value) {
      // Mode multi-calques : utiliser la nouvelle logique
      activeLayers.value
        .filter((layer) => layer.visible)
        .sort((a, b) => a.zIndex - b.zIndex)
        .forEach((layer) => {
          const geoLevel = DataTypeToGeolevel[layer.dataType]
          setupSource(mapInstance, layer.dataType, geoLevel)
          setupTileWithOpacity(mapInstance, layer.dataType, geoLevel, layer.opacity)
        })
    } else {
      // Mode mono-calque classique
      const currentGeoLevel = getGeoLevelFromDataType()
      setupSource(mapInstance, selectedDataType.value!, currentGeoLevel)
      setupTile(mapInstance, selectedDataType.value!, currentGeoLevel)
    }
  }

  const initMap = (mapId: string, initialDatatype: DataType) => {
    selectedDataType.value = initialDatatype

    // S'assurer que les activeLayers correspondent au selectedDataType initial
    if (!isMultiLayerMode.value) {
      const existingLayer = activeLayers.value.find((layer) => layer.dataType === initialDatatype)
      if (!existingLayer) {
        activeLayers.value = [
          {
            dataType: initialDatatype,
            visible: true,
            opacity: 0.7,
            zIndex: 1,
            filters: []
          }
        ]
      }
    }

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

  // === Nouvelles fonctions multi-calques ===

  const toggleMultiLayerMode = () => {
    isMultiLayerMode.value = !isMultiLayerMode.value

    if (!isMultiLayerMode.value) {
      // Retour au mode mono-calque : garder seulement le premier calque visible
      const firstVisibleLayer = activeLayers.value.find((layer) => layer.visible)
      if (firstVisibleLayer) {
        activeLayers.value = [firstVisibleLayer]
        selectedDataType.value = firstVisibleLayer.dataType
      }
    }

    // Toujours mettre à jour les calques pour reconfigurer les gestionnaires d'événements
    updateMapLayers()
  }

  const addLayer = (dataType: DataType, opacity: number = 0.7) => {
    const existingLayer = activeLayers.value.find((layer) => layer.dataType === dataType)
    if (existingLayer) {
      existingLayer.visible = true
      existingLayer.opacity = opacity
    } else {
      const newZIndex = Math.max(...activeLayers.value.map((l) => l.zIndex), 0) + 1
      activeLayers.value.push({
        dataType,
        visible: true,
        opacity,
        zIndex: newZIndex,
        filters: []
      })
    }
    isMultiLayerMode.value = true
    updateMapLayers()
  }

  const removeLayer = (dataType: DataType) => {
    const index = activeLayers.value.findIndex((layer) => layer.dataType === dataType)
    if (index > -1) {
      activeLayers.value.splice(index, 1)
    }
    if (activeLayers.value.length <= 1) {
      isMultiLayerMode.value = false
    }
    updateMapLayers()
  }

  const toggleLayerVisibility = (dataType: DataType) => {
    const layer = activeLayers.value.find((l) => l.dataType === dataType)
    if (layer) {
      layer.visible = !layer.visible
      updateMapLayers()
    }
  }

  const setLayerOpacity = (dataType: DataType, opacity: number) => {
    const layer = activeLayers.value.find((l) => l.dataType === dataType)
    if (layer) {
      layer.opacity = Math.max(0, Math.min(1, opacity))
      updateMapLayerOpacity(dataType, layer.opacity)
    }
  }

  const updateMapLayerOpacity = (dataType: DataType, opacity: number) => {
    const geoLevel = DataTypeToGeolevel[dataType]
    const layerId = getLayerId(dataType, geoLevel)

    Object.values(mapInstancesByIds.value).forEach((mapInstance) => {
      if (mapInstance.getLayer(layerId)) {
        mapInstance.setPaintProperty(layerId, "fill-opacity", opacity)
      }
    })
  }

  const updateMapLayers = () => {
    Object.values(mapInstancesByIds.value).forEach((mapInstance) => {
      // Nettoyer tous les gestionnaires d'événements existants
      Object.keys(mapEventsListener.value).forEach((key) => {
        if (key === "global-multi-layer") {
          mapInstance.off("click", mapEventsListener.value[key])
        } else {
          mapInstance.off("click", key, mapEventsListener.value[key])
        }
      })
      mapEventsListener.value = {}

      // Supprimer tous les calques existants
      Object.values(DataType).forEach((dataType) => {
        const geoLevel = DataTypeToGeolevel[dataType]
        const layerId = getLayerId(dataType, geoLevel)
        const sourceId = getSourceId(dataType, geoLevel)

        if (mapInstance.getLayer(layerId)) {
          mapInstance.removeLayer(layerId)
        }
        if (mapInstance.getSource(sourceId)) {
          mapInstance.removeSource(sourceId)
        }
      })

      // Configurer le gestionnaire d'événements selon le mode
      if (isMultiLayerMode.value) {
        setupGlobalClickHandler(mapInstance)
      }

      // Ajouter les calques actifs visibles
      activeLayers.value
        .filter((layer) => layer.visible)
        .sort((a, b) => a.zIndex - b.zIndex) // Ordre par zIndex
        .forEach((layer) => {
          const geoLevel = DataTypeToGeolevel[layer.dataType]
          setupSource(mapInstance, layer.dataType, geoLevel)
          setupTileWithOpacity(mapInstance, layer.dataType, geoLevel, layer.opacity)
        })
    })
  }

  const setupTileWithOpacity = (
    map: Map,
    datatype: DataType,
    geolevel: GeoLevel,
    opacity: number
  ) => {
    const sourceId = getSourceId(datatype, geolevel)
    const layer = createMapLayerWithOpacity(datatype, geolevel, sourceId, opacity)
    map.addLayer(layer)
    setupClickEventOnTile(map, datatype, geolevel)
  }

  const createMapLayerWithOpacity = (
    datatype: DataType,
    geolevel: GeoLevel,
    sourceId: string,
    opacity: number
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
        "fill-opacity": opacity
      }
    }
  }

  const createMultiLayerPopup = (e: any, map: Map) => {
    // Vérification de sécurité : ne pas afficher la popup multi-calques en mode simple
    if (!isMultiLayerMode.value) {
      return
    }

    if (!popupDomElement.value) {
      throw new Error("Popup DOM element is not defined")
    }

    removeActivePopup()

    // Collecter les données de tous les calques visibles à cette position
    const layerData: LayerPopupData[] = []

    // Obtenir toutes les features à cette position pour tous les calques actifs
    const visibleLayerIds = activeLayers.value
      .filter((layer) => layer.visible)
      .map((layer) => {
        const geoLevel = DataTypeToGeolevel[layer.dataType]
        return getLayerId(layer.dataType, geoLevel)
      })

    const allFeatures = map.queryRenderedFeatures(e.point, { layers: visibleLayerIds })

    // Grouper les features par calque
    activeLayers.value
      .filter((layer) => layer.visible)
      .forEach((layer) => {
        const geoLevel = DataTypeToGeolevel[layer.dataType]
        const layerId = getLayerId(layer.dataType, geoLevel)

        // Trouver les features pour ce calque spécifique
        const layerFeatures = allFeatures.filter((feature) => feature.layer.id === layerId)

        if (layerFeatures && layerFeatures.length > 0) {
          layerData.push({
            dataType: layer.dataType,
            id: extractFeatureProperty(layerFeatures, layer.dataType, geoLevel, "id"),
            properties: extractFeatureProperties(layerFeatures, layer.dataType, geoLevel),
            score: extractFeatureProperty(layerFeatures, layer.dataType, geoLevel, "indice")
          })
        }
      })

    if (layerData.length > 0) {
      if (isMultiLayerMode.value) {
        // Mode multi-calques : toujours utiliser la popup multi-calques
        multiLayerPopupData.value = {
          lng: e.lngLat.lng,
          lat: e.lngLat.lat,
          layers: layerData
        }
        popupData.value = undefined
      } else {
        // Mode mono-calque
        const singleLayer = layerData[0]
        popupData.value = {
          id: singleLayer.id,
          lng: e.lngLat.lng,
          lat: e.lngLat.lat,
          properties: singleLayer.properties,
          score: singleLayer.score
        }
        multiLayerPopupData.value = undefined
      }

      // Ajouter les highlights pour tous les calques avec des données
      layerData.forEach((data) => {
        const geoLevel = DataTypeToGeolevel[data.dataType]
        const layerId = getLayerId(data.dataType, geoLevel)
        highlightFeature(map, layerId, data.id)
      })

      // S'assurer que l'élément popup est visible avant de l'utiliser
      if (popupDomElement.value) {
        // Forcer la visibilité de l'élément DOM
        popupDomElement.value.style.display = "block"
        popupDomElement.value.style.visibility = "visible"

        const popup = new Popup().setLngLat(e.lngLat).setMaxWidth(POPUP_MAX_WIDTH)
        activePopup.value = popup.setDOMContent(popupDomElement.value).addTo(map)
      }

      const closeButton = document.getElementsByClassName("maplibregl-popup-close-button")[0]
      closeButton?.addEventListener("click", () => {
        // Nettoyer les highlights pour tous les calques avec des données
        layerData.forEach((data) => {
          const geoLevel = DataTypeToGeolevel[data.dataType]
          const layerId = getLayerId(data.dataType, geoLevel)
          clearHighlight(map, layerId)
        })
        contextData.removeData()
      })

      // Mettre à jour les données de contexte avec le premier élément
      if (contextData.data.value && layerData.length > 0) {
        contextData.setData(layerData[0].id)
      }
    }
  }

  return {
    mapInstancesByIds,
    initMap,
    popupData,
    multiLayerPopupData,
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
    // Nouvelles propriétés et méthodes multi-calques
    activeLayers,
    isMultiLayerMode,
    toggleMultiLayerMode,
    addLayer,
    removeLayer,
    toggleLayerVisibility,
    setLayerOpacity,
    updateMapLayers,
    createMultiLayerPopup
  }
})
