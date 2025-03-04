import { computed, ref } from "vue"
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
  isLoaded: boolean
  isLoading: boolean
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
      color: "#4CAF50",
      isLoaded: false,
      isLoading: false
    },
    {
      modelType: ModelType.VEGETATION,
      visibility: LayerVisibility.HIDDEN,
      title: "Vegetation",
      color: "#8BC34A",
      isLoaded: false,
      isLoading: false
    },
    {
      modelType: ModelType.TEMPERATURE,
      visibility: LayerVisibility.HIDDEN,
      title: "Temperature",
      color: "#FF5722",
      isLoaded: false,
      isLoading: false
    },
    {
      modelType: ModelType.WATER,
      visibility: LayerVisibility.HIDDEN,
      title: "Water",
      color: "#2196F3",
      isLoaded: false,
      isLoading: false
    }
  ])

  // Get visible layers
  const visibleLayers = computed(() => {
    return availableLayers.value.filter((layer) => layer.visibility === LayerVisibility.VISIBLE)
  })

  // Get layers that are currently loading
  const loadingLayers = computed(() => {
    return availableLayers.value.filter((layer) => layer.isLoading)
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

  // Setup a single layer with optimized loading
  const setupLayer = async (map: Map, modelType: ModelType, mapId: string): Promise<void> => {
    const layer = availableLayers.value.find((l) => l.modelType === modelType)
    if (!layer) return

    // If already loaded or loading, don't do anything
    if (layer.isLoaded || layer.isLoading) return

    // Mark as loading
    layer.isLoading = true

    try {
      const sourceId = getSourceIdByModelType(modelType)
      const layerId = getLayerIdByModelType(modelType)

      // Check if source already exists
      if (!map.getSource(sourceId)) {
        const tileUrl = `${FULL_BASE_API_URL}/tiles/${modelType}/{z}/{x}/{y}.mvt`

        map.addSource(sourceId, {
          type: "vector",
          tiles: [tileUrl],
          minzoom: MIN_ZOOM
        })
      }

      // Check if layer already exists
      if (!map.getLayer(layerId)) {
        map.addLayer({
          id: layerId,
          type: "fill",
          source: sourceId,
          "source-layer": modelType,
          layout: {
            visibility: layer.visibility === LayerVisibility.VISIBLE ? "visible" : "none"
          },
          paint: {
            "fill-color": ["get", "color"],
            "fill-opacity": 0.6
          }
        })

        // Setup click handler
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

      // Wait for source to load with a timeout
      await new Promise<void>((resolve, reject) => {
        const source = map.getSource(sourceId)
        if (!source) {
          reject(new Error(`Source ${sourceId} not found`))
          return
        }

        // Check if already loaded
        if (source.loaded()) {
          resolve()
          return
        }

        // Set a timeout to prevent infinite waiting
        const timeout = setTimeout(() => {
          console.warn(`Loading timeout for layer ${modelType}`)
          resolve() // Resolve anyway to prevent blocking
        }, 5000)

        // Check loading status periodically
        const checkLoading = () => {
          if (source.loaded()) {
            clearTimeout(timeout)
            resolve()
            return
          }
          setTimeout(checkLoading, 100)
        }
        checkLoading()
      })

      // Mark as loaded
      layer.isLoaded = true
      console.info(`Layer ${modelType} loaded successfully`)
    } catch (error) {
      console.error(`Error loading layer ${modelType}:`, error)
    } finally {
      // Mark as not loading anymore
      layer.isLoading = false
    }
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

  // Toggle layer visibility with lazy loading
  const toggleLayerVisibility = async (modelType: ModelType, mapId: string) => {
    const layer = availableLayers.value.find((l) => l.modelType === modelType)
    if (!layer) return

    const map = mapInstancesByIds.value[mapId]
    if (!map) return

    // Toggle visibility
    const newVisibility =
      layer.visibility === LayerVisibility.VISIBLE
        ? LayerVisibility.HIDDEN
        : LayerVisibility.VISIBLE

    layer.visibility = newVisibility

    // If making visible and not loaded yet, load the layer
    if (newVisibility === LayerVisibility.VISIBLE && !layer.isLoaded) {
      await setupLayer(map, modelType, mapId)
    }

    // Update layer visibility in the map if it exists
    const layerId = getLayerIdByModelType(modelType)
    if (map.getLayer(layerId)) {
      const visibility = newVisibility === LayerVisibility.VISIBLE ? "visible" : "none"
      map.setLayoutProperty(layerId, "visibility", visibility)
    }
  }

  // Set layer visibility
  const setLayerVisibility = async (
    modelType: ModelType,
    visibility: LayerVisibility,
    mapId: string
  ) => {
    const layer = availableLayers.value.find((l) => l.modelType === modelType)
    if (!layer) return

    const map = mapInstancesByIds.value[mapId]
    if (!map) return

    // Set visibility
    layer.visibility = visibility

    // If making visible and not loaded yet, load the layer
    if (visibility === LayerVisibility.VISIBLE && !layer.isLoaded) {
      await setupLayer(map, modelType, mapId)
    }

    // Update layer visibility in the map if it exists
    const layerId = getLayerIdByModelType(modelType)
    if (map.getLayer(layerId)) {
      const mapVisibility = visibility === LayerVisibility.VISIBLE ? "visible" : "none"
      map.setLayoutProperty(layerId, "visibility", mapVisibility)
    }
  }

  // Initialize only the visible layers
  const initVisibleLayers = async (mapInstance: Map, mapId: string) => {
    const visibleLayerModels = availableLayers.value
      .filter((layer) => layer.visibility === LayerVisibility.VISIBLE)
      .map((layer) => layer.modelType)

    // Load visible layers in parallel
    await Promise.all(
      visibleLayerModels.map((modelType) => setupLayer(mapInstance, modelType, mapId))
    )
  }

  const initMap = (mapId: string) => {
    mapInstancesByIds.value[mapId] = new Map({
      container: mapId,
      style: "map/map-style.json",
      center: [4.8537684279176645, 45.75773479280862],
      zoom: 16
    })

    const mapInstance = mapInstancesByIds.value[mapId]
    mapInstance.on("style.load", () => {
      mapInstance.on("moveend", () => {
        console.log(mapInstance.getCenter())
        console.log(mapInstance.getZoom())
      })

      // Only initialize visible layers
      initVisibleLayers(mapInstance, mapId)
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
    loadingLayers,
    toggleLayerVisibility,
    setLayerVisibility
  }
})
