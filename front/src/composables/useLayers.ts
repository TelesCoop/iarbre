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

  // Fonctions utilitaires pour les couches
  const isLayerActive = (dataType: DataType) => {
    return activeLayers.value.some((layer) => layer.dataType === dataType && layer.visible)
  }

  const getActiveLayerMode = (dataType: DataType): LayerRenderMode | null => {
    const layer = activeLayers.value.find((layer) => layer.dataType === dataType && layer.visible)
    return layer ? layer.renderMode : null
  }

  const getAvailableRenderModes = (dataType: DataType): LayerRenderMode[] => {
    switch (dataType) {
      case DataType.CLIMATE_ZONE:
        return [LayerRenderMode.FILL]
      case DataType.VULNERABILITY:
        return [LayerRenderMode.FILL, LayerRenderMode.COLOR_RELIEF]
      case DataType.PLANTABILITY:
        return [LayerRenderMode.FILL, LayerRenderMode.SYMBOL]
      default:
        return [LayerRenderMode.FILL]
    }
  }

  const getRenderModeLabel = (mode: LayerRenderMode): string => {
    switch (mode) {
      case LayerRenderMode.FILL:
        return "Plein"
      case LayerRenderMode.SYMBOL:
        return "Points"
      case LayerRenderMode.COLOR_RELIEF:
        return "Relief couleur"
      default:
        return "Standard"
    }
  }

  const getRenderModeIcon = (mode: LayerRenderMode): string => {
    switch (mode) {
      case LayerRenderMode.FILL:
        return "⬛"
      case LayerRenderMode.SYMBOL:
        return "📍"
      case LayerRenderMode.COLOR_RELIEF:
        return "🎨"
      default:
        return "⬜"
    }
  }

  const activateLayerWithMode = (dataType: DataType, mode: LayerRenderMode) => {
    if (isLayerActive(dataType)) {
      const existingLayer = activeLayers.value.find(
        (layer) => layer.dataType === dataType && layer.visible
      )
      if (existingLayer && existingLayer.renderMode !== mode) {
        // Gestion dynamique des calques pleins lors du changement de mode
        if (mode === LayerRenderMode.FILL) {
          const plantabilityFillLayer = activeLayers.value.find(
            (layer) =>
              layer.dataType === DataType.PLANTABILITY &&
              layer.visible &&
              layer.renderMode === LayerRenderMode.FILL
          )

          if (plantabilityFillLayer && dataType !== DataType.PLANTABILITY) {
            removeLayer(DataType.PLANTABILITY, LayerRenderMode.FILL)
          }
        }

        removeLayer(dataType)
        addLayerWithMode(dataType, mode)
      }
    } else {
      if (mode === LayerRenderMode.FILL) {
        const plantabilityFillLayer = activeLayers.value.find(
          (layer) =>
            layer.dataType === DataType.PLANTABILITY &&
            layer.visible &&
            layer.renderMode === LayerRenderMode.FILL
        )

        if (plantabilityFillLayer && dataType !== DataType.PLANTABILITY) {
          removeLayer(DataType.PLANTABILITY, LayerRenderMode.FILL)
        }
      }

      addLayerWithMode(dataType, mode)
    }
  }

  const deactivateLayer = (dataType: DataType) => {
    removeLayer(dataType)
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
    setUpdateCallback,
    // Nouvelles fonctions utilitaires
    isLayerActive,
    getActiveLayerMode,
    getAvailableRenderModes,
    getRenderModeLabel,
    getRenderModeIcon,
    activateLayerWithMode,
    deactivateLayer
  }
}
