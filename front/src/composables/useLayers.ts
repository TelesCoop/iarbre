import { computed, ref } from "vue"
import type { LayerConfig } from "@/types/map"
import { LayerRenderMode } from "@/types/map"
import { DataType } from "@/utils/enum"
import { calculateZIndex } from "@/utils/layers"
import { useRenderModeMetadata } from "./useRenderModeMetadata"

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

  const { getAvailableRenderModes, getRenderModeLabel, getRenderModeIcon } = useRenderModeMetadata()

  const findLayer = (dataType: DataType, renderMode?: LayerRenderMode): LayerConfig | undefined => {
    return activeLayers.value.find(
      (layer) =>
        layer.dataType === dataType && (renderMode ? layer.renderMode === renderMode : true)
    )
  }

  const findVisibleLayer = (dataType: DataType): LayerConfig | undefined => {
    return activeLayers.value.find((layer) => layer.dataType === dataType && layer.visible)
  }

  const createLayerConfig = (
    dataType: DataType,
    renderMode: LayerRenderMode,
    opacity: number
  ): LayerConfig => {
    return {
      dataType,
      visible: true,
      opacity,
      zIndex: calculateZIndex(activeLayers, dataType, renderMode),
      filters: [],
      renderMode
    }
  }

  const handleFillModeConflict = (dataType: DataType) => {
    if (dataType === DataType.PLANTABILITY) return

    const plantabilityFillLayer = activeLayers.value.find(
      (layer) =>
        layer.dataType === DataType.PLANTABILITY &&
        layer.visible &&
        layer.renderMode === LayerRenderMode.FILL
    )

    if (plantabilityFillLayer) {
      removeLayer(DataType.PLANTABILITY, LayerRenderMode.FILL)
    }
  }

  const addLayer = (dataType: DataType, opacity: number = 0.7) => {
    const existingLayer = findLayer(dataType)
    if (existingLayer) {
      existingLayer.visible = true
      existingLayer.opacity = opacity
    } else {
      activeLayers.value.push(createLayerConfig(dataType, LayerRenderMode.FILL, opacity))
    }
    globalUpdateCallback?.()
  }

  const addLayerWithMode = (
    dataType: DataType,
    renderMode: LayerRenderMode,
    opacity: number = 0.7
  ) => {
    const existingLayer = findLayer(dataType, renderMode)
    if (existingLayer) {
      existingLayer.visible = true
      existingLayer.opacity = opacity
    } else {
      activeLayers.value.push(createLayerConfig(dataType, renderMode, opacity))
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
    const layer = findLayer(dataType, renderMode)
    if (layer) {
      layer.opacity = opacity
    }
  }

  const updateLayerVisibility = (
    dataType: DataType,
    visible: boolean,
    renderMode?: LayerRenderMode
  ) => {
    const layer = findLayer(dataType, renderMode)
    if (layer) {
      layer.visible = visible
    }
  }

  const hasLayer = (dataType: DataType, renderMode?: LayerRenderMode): boolean => {
    return !!findLayer(dataType, renderMode)
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

  const isLayerActive = (dataType: DataType) => {
    return !!findVisibleLayer(dataType)
  }

  const getActiveLayerMode = (dataType: DataType): LayerRenderMode | null => {
    const layer = findVisibleLayer(dataType)
    return layer ? layer.renderMode : null
  }

  const activateLayerWithMode = (dataType: DataType, mode: LayerRenderMode) => {
    const existingLayer = findVisibleLayer(dataType)

    if (existingLayer) {
      removeLayer(dataType)
      if (existingLayer.renderMode === mode) {
        return
      }
    }

    if (mode === LayerRenderMode.FILL) {
      handleFillModeConflict(dataType)
    }

    addLayerWithMode(dataType, mode)
  }

  return {
    activeLayers,
    isMultiLayerMode,
    addLayer,
    addLayerWithMode,
    removeLayer,
    updateLayerOpacity,
    updateLayerVisibility,
    findLayer,
    hasLayer,
    clearAllLayers,
    getVisibleLayers,
    getLayersByDataType,
    setUpdateCallback,
    isLayerActive,
    getActiveLayerMode,
    getAvailableRenderModes,
    getRenderModeLabel,
    getRenderModeIcon,
    activateLayerWithMode
  }
}
