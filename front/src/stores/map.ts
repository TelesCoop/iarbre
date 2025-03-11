import { computed, ref, watch } from "vue"
import { defineStore } from "pinia"
import { Map, Popup, NavigationControl } from "maplibre-gl"
import { FULL_BASE_API_URL, MIN_ZOOM } from "@/utils/constants"
import { GeoLevel, DataType } from "@/utils/enum"
import type { ScorePopupData } from "@/types"

export const useMapStore = defineStore("map", () => {
  const mapInstancesByIds = ref<Record<string, Map>>({})
  const popup = ref<ScorePopupData | undefined>(undefined)
  const selectedDataType = ref<DataType>(DataType.PLANTABILITY)
  const currentGeoLevel = ref<GeoLevel>(GeoLevel.TILE)

  const getSourceId = (datatype: DataType, geolevel: GeoLevel) => {
    return `${datatype}-${geolevel}-source`
  }

  const getLayerId = (datatype: DataType, geolevel: GeoLevel) => {
    return `${datatype}-${geolevel}-layer`
  }

  const extractFeatureIndice = (features: Array<any>, datatype: DataType, geolevel: GeoLevel) => {
    if (!features) return undefined
    const f = features.filter((feature: any) => feature.layer.id === getLayerId(datatype, geolevel))
    if (f.length === 0) return undefined
    return f[0].properties.indice
  }

  const setupTile = (map: Map, datatype: DataType, geolevel: GeoLevel, mapId: string) => {
    const sourceId = getSourceId(datatype, geolevel)
    const layerId = getLayerId(datatype, geolevel)

    map.addLayer({
      id: layerId,
      type: "fill",
      source: sourceId,
      // source-layer must match the name of the encoded tile in mvt_generator.py
      "source-layer": `${geolevel}/${datatype}`,
      layout: {},
      paint: {
        "fill-color": ["get", "color"],
        "fill-opacity": 0.6
      }
    })

    map.on("click", layerId, (e) => {
      popup.value = {
        score: Math.round(10 * extractFeatureIndice(e.features!, datatype, geolevel)),
        lng: e.lngLat.lng,
        lat: e.lngLat.lat
      }

      new Popup()
        .setLngLat(e.lngLat)
        .setDOMContent(document.getElementById(`popup-${mapId}`)!)
        .setMaxWidth("400px")
        .addTo(map)
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
        // This text is tested by Cypress.
        console.info("cypress: map data loaded")
        return
      }
      setTimeout(checkIfLoaded, 100)
    }
    checkIfLoaded()
  }

  const setupControls = (map: Map) => {
    map.addControl(
      new NavigationControl({
        visualizePitch: false,
        visualizeRoll: false,
        showZoom: true,
        showCompass: false
      }),
      "bottom-right"
    )
  }

  const changeDataType = (datatype: DataType) => {
    const previousDataType = selectedDataType.value
    selectedDataType.value = datatype

    // Update all map instances with the new layer
    Object.keys(mapInstancesByIds.value).forEach((mapId) => {
      const mapInstance = mapInstancesByIds.value[mapId]

      // remove existing layers and sources
      mapInstance.removeLayer(getLayerId(previousDataType, currentGeoLevel.value))
      mapInstance.removeSource(getSourceId(previousDataType, currentGeoLevel.value))

      // Add the new layer
      setupSource(mapInstance, selectedDataType.value, currentGeoLevel.value)
      setupTile(mapInstance, selectedDataType.value, currentGeoLevel.value, mapId)
    })
  }

  const initTiles = (mapInstance: Map, mapId: string) => {
    setupSource(mapInstance, selectedDataType.value, currentGeoLevel.value)
    setupTile(mapInstance, selectedDataType.value, currentGeoLevel.value, mapId)
  }

  const initMap = (mapId: string) => {
    mapInstancesByIds.value[mapId] = new Map({
      container: mapId, // container id
      style: "map/map-style.json",
      // center to France,
      center: [4.8537684279176645, 45.75773479280862],
      // zoom to a level where France is visible
      zoom: 16
    })
    // @ts-ignore
    window.map = mapInstancesByIds.value[mapId]

    const mapInstance = mapInstancesByIds.value[mapId]
    mapInstance.on("style.load", () => {
      mapInstance.on("moveend", () => {
        console.log(mapInstance.getCenter())
        console.log(mapInstance.getZoom())
      })
      initTiles(mapInstance, mapId)
      setupControls(mapInstance)
    })
  }
  return {
    mapInstancesByIds,
    initMap,
    popup,
    selectedDataType: selectedDataType,
    currentGeoLevel,
    changeDataType
  }
})
