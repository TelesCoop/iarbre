import { computed, ref } from "vue"
import { defineStore } from "pinia"
import { Map } from "maplibre-gl"
import { FULL_BASE_API_URL, MIN_ZOOM } from "@/utils/constants"
import { ModelType } from "@/utils/enum"
export const useMapStore = defineStore("map", () => {
  const mapInstancesByIds = ref<Record<string, Map>>({})

  const getMapInstance = (id: string) => {
    return computed(() => mapInstancesByIds.value[id])
  }

  const getSourceIdByModelType = (modelType: ModelType) => {
    return `${modelType}-source`
  }
  const getLayerIdByModelType = (modelType: ModelType) => {
    return `${modelType}-layer`
  }

  const setupTile = (map: Map, modelType: ModelType) => {
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
  }

  const setupSource = (map: Map, modelType: ModelType) => {
    const tileUrl = `${FULL_BASE_API_URL}/tiles/${modelType}/{z}/{x}/{y}.mvt`
    const sourceId = getSourceIdByModelType(modelType)

    map.addSource(sourceId, {
      type: "vector",
      tiles: [tileUrl],
      minzoom: MIN_ZOOM
    })
  }
  const initTiles = (mapInstance: Map) => {
    setupSource(mapInstance, ModelType.TILE)
    setupTile(mapInstance, ModelType.TILE)
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
      initTiles(mapInstance)
    })
  }
  return { mapInstancesByIds, initMap, getMapInstance }
})
