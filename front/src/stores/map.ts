import { ref } from "vue"
import { defineStore } from "pinia"
import { Map, Popup, NavigationControl, AttributionControl } from "maplibre-gl"
import { MAP_CONTROL_POSITION, MIN_ZOOM } from "@/utils/constants"
import { GeoLevel, DataType, DataTypeToGeolevel, DataTypeToAttributionSource } from "@/utils/enum"
import type { MapScorePopupData } from "@/types"
import { FULL_BASE_API_URL } from "@/api"

// reference https://docs.mapbox.com/style-spec/reference/expressions/#round
const FILL_COLOR_MAP = {
  [DataType.PLANTABILITY]: [
    "match",
    ["floor", ["get", "indice"]],
    0,
    "#E0E0E0",
    1,
    "#E0E0E0",
    2,
    "#F0F1C0",
    3,
    "#F0F1C0",
    4,
    "#E5E09A",
    5,
    "#E5E09A",
    6,
    "#B7D990",
    7,
    "#B7D990",
    8,
    "#71BB72",
    9,
    "#71BB72",
    10,
    "#006837",
    "#E0E0E0"
  ],
  [DataType.VULNERABILITY]: [
    "match",
    ["get", "indice_day"],
    1,
    "#31AFF5",
    2,
    "#7785A3",
    3,
    "#E6E3D1",
    4,
    "#D1BB3B",
    5,
    "#C06329",
    6,
    "#E03F08",
    7,
    "#B61C02",
    8,
    "#7A0403",
    "#353A47"
  ],
  // Color defined by CEREMA in
  // https://www.data.gouv.fr/fr/datasets/r/f80e08a4-ecd1-42a2-a8d6-963af16aec75
  [DataType.LOCAL_CLIMATE_ZONES]: [
    "match",
    ["get", "indice"],
    "1",
    "#8C0000",
    "2",
    "#D10000",
    "3",
    "#FF0000",
    "4",
    "#BF4D00",
    "5",
    "#fa6600",
    "6",
    "#ff9955",
    "7",
    "#faee05",
    "8",
    "#bcbcbc",
    "9",
    "#ffccaa",
    "A",
    "#006a00",
    "B",
    "#00aa00",
    "C",
    "#648525",
    "D",
    "#b9db79",
    "E",
    "#000000",
    "F",
    "#FBF7AE",
    "#6A6AFF"
  ]
}
export const useMapStore = defineStore("map", () => {
  const mapInstancesByIds = ref<Record<string, Map>>({})
  const popupData = ref<MapScorePopupData | undefined>(undefined)
  const popupDomElement = ref<HTMLElement | null>(null)
  const activePopup = ref<Popup | null>(null)
  const activeFeatureId = ref<number>(-1)

  const selectedDataType = ref<DataType>(DataType.PLANTABILITY)
  const currentGeoLevel = ref<GeoLevel>(GeoLevel.TILE)
  const getAttributionSource = () => {
    return DataTypeToAttributionSource[selectedDataType.value] || ""
  }
  const getGeoLevelFromDataType = () => {
    return DataTypeToGeolevel[selectedDataType.value] || GeoLevel.LCZ
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

  const removeActivePopup = () => {
    if (activePopup.value) {
      activePopup.value.remove()
      activePopup.value = null
    }
  }

  const getSourceId = (datatype: DataType, geolevel: GeoLevel) => {
    return `${geolevel}-${datatype}-source`
  }

  const getLayerId = (datatype: DataType, geolevel: GeoLevel) => {
    return `${geolevel}-${datatype}-layer`
  }

  const getMapInstance = (mapId: string): Map => {
    return mapInstancesByIds.value[mapId]
  }
  const extractFeatures = (features: Array<any>, datatype: DataType, geolevel: GeoLevel) => {
    if (!features) return undefined

    const feature = features.find(
      (feature: any) => feature.layer.id === getLayerId(datatype, geolevel)
    )

    return feature || undefined
  }

  const extractFeatureProperty = (
    features: Array<any>,
    datatype: DataType,
    geolevel: GeoLevel,
    propertyName?: string
  ) => {
    const feature = extractFeatures(features, datatype, geolevel)
    if (!feature) return undefined

    return propertyName ? feature.properties[propertyName] : feature.properties
  }

  const extractFeatureIndex = (features: Array<any>, datatype: DataType, geolevel: GeoLevel) => {
    return extractFeatureProperty(features, datatype, geolevel, "indice")
  }

  const extractFeatureProperties = (
    features: Array<any>,
    datatype: DataType,
    geolevel: GeoLevel
  ) => {
    return extractFeatureProperty(features, datatype, geolevel)
  }

  const setupTile = (map: Map, datatype: DataType, geolevel: GeoLevel) => {
    const sourceId = getSourceId(datatype, geolevel)
    const layerId = getLayerId(datatype, geolevel)

    map.addLayer({
      id: layerId,
      type: "fill",
      source: sourceId,
      // source-layer must match the name of the encoded tile in mvt_generator.py
      "source-layer": `${geolevel}--${datatype}`,
      layout: {},
      paint: {
        "fill-color": FILL_COLOR_MAP[datatype],
        "fill-outline-color": "#00000000",
        "fill-opacity": 0.6
      }
    })
    map.on("click", layerId, (e) => {
      if (!popupDomElement.value) throw new Error("Popupdomelement is not defined")
      popupData.value = {
        id: extractFeatureIndex(e.features!, datatype, geolevel),
        lng: e.lngLat.lng,
        lat: e.lngLat.lat,
        properties: extractFeatureProperties(e.features!, datatype, geolevel)
      }

      const featureId = extractFeatureProperty(e.features!, datatype, geolevel, "id")
      map.setPaintProperty(layerId, "fill-outline-color", [
        "match",
        ["get", "id"],
        featureId,
        "#000000",
        "#00000000"
      ])

      removeActivePopup()

      activePopup.value = new Popup()
        .setLngLat(e.lngLat)
        .setDOMContent(popupDomElement.value)
        .setMaxWidth("400px")
        .addTo(map)

      document
        .getElementsByClassName("maplibregl-popup-close-button")[0]
        .addEventListener("click", () =>
          map.setPaintProperty(layerId, "fill-outline-color", "#00000000")
        )
    })
  }

  const setupSource = (map: Map, datatype: DataType, geolevel: GeoLevel) => {
    const tileUrl = `${FULL_BASE_API_URL}/tiles/${geolevel}/${datatype}/{z}/{x}/{y}.mvt`
    const sourceId = getSourceId(datatype, geolevel)
    map.addSource(sourceId, {
      type: "vector",
      tiles: [tileUrl],
      minzoom: MIN_ZOOM
    })

    const source = map.getSource(sourceId)!
    const checkIfLoaded = () => {
      if (source.loaded()) {
        console.info("cypress: map data loaded")
        return
      }
      setTimeout(checkIfLoaded, 100)
    }
    checkIfLoaded()
  }

  const setupControls = (map: Map) => {
    map.addControl(navControl.value, MAP_CONTROL_POSITION)
  }

  const changeDataType = (datatype: DataType) => {
    removeActivePopup()

    const previousDataType = selectedDataType.value
    selectedDataType.value = datatype

    const previousGeoLevel = currentGeoLevel.value
    currentGeoLevel.value = getGeoLevelFromDataType()

    // Update all map instances with the new layer
    Object.keys(mapInstancesByIds.value).forEach((mapId) => {
      const mapInstance = mapInstancesByIds.value[mapId]

      // remove existing layers and sources
      mapInstance.removeLayer(getLayerId(previousDataType, previousGeoLevel))
      mapInstance.removeSource(getSourceId(previousDataType, previousGeoLevel))
      mapInstance.removeControl(attributionControl.value)
      mapInstance.removeControl(navControl.value)

      // Add the new layer
      setupSource(mapInstance, selectedDataType.value, currentGeoLevel.value)
      setupTile(mapInstance, selectedDataType.value, currentGeoLevel.value)
      attributionControl.value = new AttributionControl({
        compact: true,
        customAttribution: getAttributionSource()
      })
      mapInstance.addControl(attributionControl.value, MAP_CONTROL_POSITION)
      setupControls(mapInstance)

      // MapComponent is listening to moveend event
      mapInstance.fire("moveend")
    })
  }

  const initTiles = (mapInstance: Map, mapId: string) => {
    setupSource(mapInstance, selectedDataType.value, currentGeoLevel.value)
    setupTile(mapInstance, selectedDataType.value, currentGeoLevel.value)
    popupDomElement.value = document.getElementById(`popup-${mapId}`)
  }

  const initMap = (mapId: string) => {
    mapInstancesByIds.value[mapId] = new Map({
      container: mapId, // container id
      style: "/map/map-style.json",
      attributionControl: false
    })

    const mapInstance = mapInstancesByIds.value[mapId]
    mapInstance.on("style.load", () => {
      mapInstance.addControl(attributionControl.value, MAP_CONTROL_POSITION)
      setupControls(mapInstance)
      initTiles(mapInstance, mapId)
    })
  }

  return {
    mapInstancesByIds,
    initMap,
    popupData,
    selectedDataType,
    currentGeoLevel,
    changeDataType,
    getMapInstance
  }
})
