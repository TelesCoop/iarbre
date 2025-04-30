import { ref } from "vue"
import { defineStore } from "pinia"
import { Map, Popup, NavigationControl, AttributionControl } from "maplibre-gl"
import { MAP_CONTROL_POSITION, MAX_ZOOM, MIN_ZOOM } from "@/utils/constants"
import { GeoLevel, DataType, DataTypeToGeolevel, DataTypeToAttributionSource } from "@/utils/enum"
import type { MapScorePopupData } from "@/types"
import { FULL_BASE_API_URL } from "@/api"
import { VULNERABILITY_COLOR_MAP } from "@/utils/vulnerability"
import { PLANTABILITY_COLOR_MAP } from "@/utils/plantability"
import { CLIMATE_ZONE_MAP_COLOR_MAP } from "@/utils/climateZones"

// reference https://docs.mapbox.com/style-spec/reference/expressions/#round
const FILL_COLOR_MAP = {
  [DataType.PLANTABILITY]: ["match", ["floor", ["get", "indice"]], ...PLANTABILITY_COLOR_MAP],
  [DataType.VULNERABILITY]: ["match", ["get", "indice_day"], ...VULNERABILITY_COLOR_MAP],
  [DataType.LOCAL_CLIMATE_ZONES]: ["match", ["get", "indice"], ...CLIMATE_ZONE_MAP_COLOR_MAP]
}
export const useMapStore = defineStore("map", () => {
  const mapInstancesByIds = ref<Record<string, Map>>({})
  const popupData = ref<MapScorePopupData | undefined>(undefined)
  const popupDomElement = ref<HTMLElement | null>(null)
  const activePopup = ref<Popup | null>(null)

  const selectedDataType = ref<DataType | null>(null)

  const getAttributionSource = () => {
    if (!selectedDataType.value) return ""
    return DataTypeToAttributionSource[selectedDataType.value] || ""
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

  const removeActivePopup = () => {
    if (activePopup.value) {
      activePopup.value.remove()
      activePopup.value = null
      popupData.value = undefined
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
    if (datatype === null) return

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
        "fill-color": FILL_COLOR_MAP[datatype] as any,
        "fill-outline-color": "#00000000",
        "fill-opacity": 0.6
      }
    })
    map.on("click", layerId, (e) => {
      if (!popupDomElement.value) throw new Error("Popupdomelement is not defined")
      removeActivePopup()

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
    if (selectedDataType.value == datatype) return
    removeActivePopup()

    const previousDataType = selectedDataType.value!
    const previousGeoLevel = getGeoLevelFromDataType()

    selectedDataType.value = datatype

    // Update all map instances with the new layer
    Object.keys(mapInstancesByIds.value).forEach((mapId) => {
      const mapInstance = mapInstancesByIds.value[mapId]

      // remove existing layers and sources
      if (previousDataType !== null) {
        mapInstance.removeLayer(getLayerId(previousDataType, previousGeoLevel))
        mapInstance.removeSource(getSourceId(previousDataType, previousGeoLevel))
      }
      mapInstance.removeControl(attributionControl.value)
      mapInstance.removeControl(navControl.value)

      // Add the new layer
      const currentGeoLevel = getGeoLevelFromDataType()
      setupSource(mapInstance, selectedDataType.value!, currentGeoLevel)
      setupTile(mapInstance, selectedDataType.value!, currentGeoLevel)
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
    const currentGeoLevel = getGeoLevelFromDataType()

    setupSource(mapInstance, selectedDataType.value!, currentGeoLevel)
    setupTile(mapInstance, selectedDataType.value!, currentGeoLevel)
    popupDomElement.value = document.getElementById(`popup-${mapId}`)
  }

  const initMap = (mapId: string, initialDatatype: DataType | null) => {
    selectedDataType.value = initialDatatype
    mapInstancesByIds.value[mapId] = new Map({
      container: mapId, // container id
      style: "/map/map-style.json",
      maxZoom: MAX_ZOOM - 1,
      minZoom: MIN_ZOOM,
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
    changeDataType,
    getMapInstance
  }
})
