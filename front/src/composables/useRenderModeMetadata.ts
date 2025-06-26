import { LayerRenderMode } from "@/types/map"
import { DataType } from "@/utils/enum"

export function useRenderModeMetadata() {
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

  return {
    getAvailableRenderModes,
    getRenderModeLabel,
    getRenderModeIcon
  }
}
