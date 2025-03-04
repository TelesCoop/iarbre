import { computed, ref, reactive } from "vue"
import { defineStore } from "pinia"
import { Map, Popup, NavigationControl } from "maplibre-gl"
import { FULL_BASE_API_URL, MIN_ZOOM } from "@/utils/constants"
import { LayerVisibility, ModelType } from "@/utils/enum"
import type { ScorePopupData } from "@/types"

export interface LayerInfo {
  modelType: ModelType
  visibility: LayerVisibility
  title: string
  color: string
}

export const useMapStore = defineStore("map", () => {
  const mapInstancesByIds = ref<Record<string, Map>>({})
  const popup = ref<ScorePopupData | undefined>(undefined)

  // Define available layers with their properties
  const availableLayers = ref<LayerInfo[]>([
    {
      modelType: ModelType.TILE,
      visibility: LayerVisibility.VISIBLE,
      title: "Plantability",
      color: "#4CAF50"
    },
    {
      modelType: ModelType.VEGETATION,
      visibility: LayerVisibility.HIDDEN,
      title: "Vegetation",
      color: "#8BC34A"
    },
    {
      modelType: ModelType.TEMPERATURE,
      visibility: LayerVisibility.HIDDEN,
      title: "Temperature",
      color: "#FF5722"
    },
    {
      modelType: ModelType.WATER,
      visibility: LayerVisibility.HIDDEN,
      title: "Water",
      color: "#2196F3"
    }
  ])

  // Get visible layers
  const visibleLayers = computed(() => {
    return availableLayers.value.filter((layer) => layer.visibility === LayerVisibility.VISIBLE)
  })

  const getMapInstance = (id: string) => {
    return computed(() => mapInstancesByIds.value[id])
  }

  const getSourceIdByModelType = (modelType: ModelType) => {
    return `${modelType}-source`
  }
  const getLayerIdByModelType = (modelType: ModelType) => {
    return `${modelType}-layer`
  }

  const extractFeatureIndice = (features: Array<any>, modelType: ModelType) => {
    if (!features) return undefined
    const f = features.filter(
      (feature: any) => feature.layer.id === getLayerIdByModelType(modelType)
    )
    if (f.length === 0) return undefined
    return f[0].properties.indice
  }

  const setupTile = (map: Map, modelType: ModelType, mapId: string) => {
    const sourceId = getSourceIdByModelType(modelType)
    const layerId = getLayerIdByModelType(modelType)
    map.addLayer({
      id: layerId,
      type: "fill",
      source: sourceId, // ID of the tile source created above
      "source-layer": modelType,
      layout: {},
      paint: {
        "fill-color": ["get", "color"],
        "fill-opacity": 0.6
      }
    })

    map.on("click", layerId, (e) => {
      popup.value = {
        score: Math.round(10 * extractFeatureIndice(e.features!, modelType)),
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

  const setupSource = (map: Map, modelType: ModelType) => {
    const tileUrl = `${FULL_BASE_API_URL}/tiles/${modelType}/{z}/{x}/{y}.mvt`
    const sourceId = getSourceIdByModelType(modelType)

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

  // Toggle layer visibility
  const toggleLayerVisibility = (modelType: ModelType, mapId: string) => {
    console.log("### 1", modelType)
    const layer = availableLayers.value.find((l) => l.modelType === modelType)
    if (!layer) return

    const map = mapInstancesByIds.value[mapId]
    if (!map) return

    // Toggle visibility
    layer.visibility =
      layer.visibility === LayerVisibility.VISIBLE
        ? LayerVisibility.HIDDEN
        : LayerVisibility.VISIBLE

    // Update layer visibility in the map
    const layerId = getLayerIdByModelType(modelType)
    if (map.getLayer(layerId)) {
      const visibility = layer.visibility === LayerVisibility.VISIBLE ? "visible" : "none"
      map.setLayoutProperty(layerId, "visibility", visibility)
    }
  }

  // Set layer visibility
  const setLayerVisibility = (modelType: ModelType, visibility: LayerVisibility, mapId: string) => {
    const layer = availableLayers.value.find((l) => l.modelType === modelType)
    if (!layer) return

    const map = mapInstancesByIds.value[mapId]
    if (!map) return

    // Set visibility
    layer.visibility = visibility

    // Update layer visibility in the map
    const layerId = getLayerIdByModelType(modelType)
    if (map.getLayer(layerId)) {
      const mapVisibility = visibility === LayerVisibility.VISIBLE ? "visible" : "none"
      map.setLayoutProperty(layerId, "visibility", mapVisibility)
    }
  }

  const initTiles = (mapInstance: Map, mapId: string) => {
    // Initialize all available layers
    for (const layer of availableLayers.value) {
      setupSource(mapInstance, layer.modelType)
      setupTile(mapInstance, layer.modelType, mapId)

      // Set initial visibility
      const layerId = getLayerIdByModelType(layer.modelType)
      const visibility = layer.visibility === LayerVisibility.VISIBLE ? "visible" : "none"
      mapInstance.setLayoutProperty(layerId, "visibility", visibility)
    }
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
  return {
    mapInstancesByIds,
    initMap,
    getMapInstance,
    popup,
    availableLayers,
    visibleLayers,
    toggleLayerVisibility,
    setLayerVisibility
  }
})
