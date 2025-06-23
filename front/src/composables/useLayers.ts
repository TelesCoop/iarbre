import { computed, ref } from "vue"
import type { LayerConfig } from "@/types/map"
import { LayerRenderMode } from "@/types/map"
import { DataType } from "@/utils/enum"
import { calculateZIndex } from "@/utils/layers"

let globalUpdateCallback: (() => void) | null = null

export function useLayers() {
  const activeLayers = ref<LayerConfig[]>([
    {
      dataType: DataType.PLANTABILITY,
      visible: true,
      opacity: 0.7,
      zIndex: 1,
      filters: [],
      renderMode: LayerRenderMode.FILL
    }
  ])

  const isMultiLayerMode = computed(() => {
    return activeLayers.value.length > 1
  })

  const addLayer = (dataType: DataType, opacity: number = 0.7) => {
    const existingLayer = activeLayers.value.find((layer) => layer.dataType === dataType)
    if (existingLayer) {
      existingLayer.visible = true
      existingLayer.opacity = opacity
    } else {
      const newZIndex = calculateZIndex(activeLayers, dataType, LayerRenderMode.FILL)

      activeLayers.value.push({
        dataType,
        visible: true,
        opacity,
        zIndex: newZIndex,
        filters: [],
        renderMode: LayerRenderMode.FILL
      })
    }
    globalUpdateCallback?.()
  }

  const addLayerWithMode = (
    dataType: DataType,
    renderMode: LayerRenderMode,
    opacity: number = 0.7
  ) => {
    const existingLayer = activeLayers.value.find(
      (layer) => layer.dataType === dataType && layer.renderMode === renderMode
    )
    if (existingLayer) {
      existingLayer.visible = true
      existingLayer.opacity = opacity
    } else {
      const newZIndex = calculateZIndex(activeLayers, dataType, renderMode)

      activeLayers.value.push({
        dataType,
        visible: true,
        opacity: opacity,
        zIndex: newZIndex,
        filters: [],
        renderMode: renderMode
      })
    }
    globalUpdateCallback?.()
  }

  const removeLayer = (dataType: DataType, renderMode?: LayerRenderMode) => {
    const index = activeLayers.value.findIndex(
      (layer) =>
        layer.dataType === dataType && (renderMode ? layer.renderMode === renderMode : true)
    )
    if (index > -1) {
      activeLayers.value.splice(index, 1)
    }
    globalUpdateCallback?.()
  }

  const updateLayerOpacity = (
    dataType: DataType,
    opacity: number,
    renderMode?: LayerRenderMode
  ) => {
    const layer = activeLayers.value.find(
      (l) => l.dataType === dataType && (renderMode ? l.renderMode === renderMode : true)
    )
    if (layer) {
      layer.opacity = opacity
    }
  }

  const updateLayerVisibility = (
    dataType: DataType,
    visible: boolean,
    renderMode?: LayerRenderMode
  ) => {
    const layer = activeLayers.value.find(
      (l) => l.dataType === dataType && (renderMode ? l.renderMode === renderMode : true)
    )
    if (layer) {
      layer.visible = visible
    }
  }

  const getLayer = (dataType: DataType, renderMode?: LayerRenderMode): LayerConfig | undefined => {
    return activeLayers.value.find(
      (layer) =>
        layer.dataType === dataType && (renderMode ? layer.renderMode === renderMode : true)
    )
  }

  const hasLayer = (dataType: DataType, renderMode?: LayerRenderMode): boolean => {
    return activeLayers.value.some(
      (layer) =>
        layer.dataType === dataType && (renderMode ? layer.renderMode === renderMode : true)
    )
  }

  const clearAllLayers = () => {
    activeLayers.value = []
  }

  const getVisibleLayers = () => {
    return activeLayers.value.filter((layer) => layer.visible)
  }

  const getLayersByDataType = (dataType: DataType): LayerConfig[] => {
    return activeLayers.value.filter((layer) => layer.dataType === dataType)
  }

  const setUpdateCallback = (callback: () => void) => {
    globalUpdateCallback = callback
  }

  return {
    activeLayers,
    isMultiLayerMode,
    addLayer,
    addLayerWithMode,
    removeLayer,
    updateLayerOpacity,
    updateLayerVisibility,
    getLayer,
    hasLayer,
    clearAllLayers,
    getVisibleLayers,
    getLayersByDataType,
    setUpdateCallback
  }
}
