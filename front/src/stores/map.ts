import { computed, ref, watch } from "vue"
import { defineStore } from "pinia"
import { Map, Popup, NavigationControl } from "maplibre-gl"
import { FULL_BASE_API_URL, MIN_ZOOM } from "@/utils/constants"
import { ModelType, LAYERS } from "@/utils/enum"
import type { ScorePopupData } from "@/types"

export const useMapStore = defineStore("map", () => {
  const mapInstancesByIds = ref<Record<string, Map>>({})
  const popup = ref<ScorePopupData | undefined>(undefined)
  const selectedLayer = ref<LAYERS>(LAYERS.PLANTABILITY)
  const currentModelType = ref<ModelType>(ModelType.TILE)

  const getSourceId = (layer: LAYERS, modelType: ModelType) => {
    return `${layer}-${modelType}-source`
  }

  const getLayerId = (layer: LAYERS, modelType: ModelType) => {
    return `${layer}-${modelType}-layer`
  }

  const extractFeatureIndice = (features: Array<any>, layer: LAYERS, modelType: ModelType) => {
    if (!features) return undefined
    const f = features.filter((feature: any) => feature.layer.id === getLayerId(layer, modelType))
    if (f.length === 0) return undefined
    return f[0].properties.indice
  }

  const setupTile = (map: Map, layer: LAYERS, modelType: ModelType, mapId: string) => {
    const sourceId = getSourceId(layer, modelType)
    const layerId = getLayerId(layer, modelType)

    map.addLayer({
      id: layerId,
      type: "fill",
      source: sourceId,
      "source-layer": modelType,
      layout: {},
      paint: {
        "fill-color": ["get", "color"],
        "fill-opacity": 0.6
      }
    })

    map.on("click", layerId, (e) => {
      popup.value = {
        score: Math.round(10 * extractFeatureIndice(e.features!, layer, modelType)),
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

  const setupSource = (map: Map, layer: LAYERS, modelType: ModelType) => {
    const tileUrl = `${FULL_BASE_API_URL}/tiles/${modelType}/${layer}/{z}/{x}/{y}.mvt`
    const sourceId = getSourceId(layer, modelType)

    console.log("### setupsource 0")
    map.addSource(sourceId, {
      type: "vector",
      tiles: [tileUrl],
      minzoom: MIN_ZOOM
    })
    console.log("### setupsource 1")

    const source = map.getSource(sourceId)!
    console.log("### setupsource 2")
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

  const changeLayer = (layerType: LAYERS) => {
    console.log("changelayer 1")
    selectedLayer.value = layerType

    // Update all map instances with the new layer
    Object.keys(mapInstancesByIds.value).forEach((mapId) => {
      console.log("changelayer 1.5")
      const mapInstance = mapInstancesByIds.value[mapId]

      // // Remove existing layers and sources
      const existingLayers = Object.values(LAYERS)
      existingLayers.forEach((layer) => {
        const layerId = getLayerId(layer, currentModelType.value)
        if (mapInstance.getLayer(layerId)) {
          mapInstance.removeLayer(layerId)
        }

        const sourceId = getSourceId(layer, currentModelType.value)
        if (mapInstance.getSource(sourceId)) {
          mapInstance.removeSource(sourceId)
        }
      })
      console.log("changelayer 2")

      // Add the new layer
      setupSource(mapInstance, selectedLayer.value, currentModelType.value)
      console.log("changelayer 3")
      setupTile(mapInstance, selectedLayer.value, currentModelType.value, mapId)
      console.log("changelayer 4")
    })
  }

  const initTiles = (mapInstance: Map, mapId: string) => {
    setupSource(mapInstance, selectedLayer.value, currentModelType.value)
    setupTile(mapInstance, selectedLayer.value, currentModelType.value, mapId)
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
  return { mapInstancesByIds, initMap, popup, selectedLayer, currentModelType, changeLayer }
})
