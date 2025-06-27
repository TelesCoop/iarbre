import { type LayerConfig, LayerRenderMode } from "@/types/map"
import { DataType, GeoLevel } from "@/utils/enum"
import { VulnerabilityMode as VulnerabilityModeType } from "@/utils/vulnerability"
import type { AddLayerObject, DataDrivenPropertyValueSpecification } from "maplibre-gl"
import { getLayerId } from "@/utils/map"
import type { Ref } from "vue"

export const configureLayersProperties = (
  layerConfig: LayerConfig,
  geolevel: GeoLevel,
  sourceId: string,
  fillColorMap: Record<DataType, any>,
  vulnerabilityMode: VulnerabilityModeType
): AddLayerObject => {
  const layerId = getLayerId(layerConfig.dataType, geolevel)
  const renderMode = layerConfig.renderMode
  const smartOpacity = layerConfig.opacity
  const radiusField =
    layerConfig.dataType === DataType.VULNERABILITY ? `indice_${vulnerabilityMode}` : "indice"
  const maxRadius = layerConfig.dataType === DataType.VULNERABILITY ? 9 : 10
  const baseLayer = {
    id: layerId,
    source: sourceId,
    "source-layer": `${geolevel}--${layerConfig.dataType}`,
    layout: {}
  }

  switch (renderMode) {
    case LayerRenderMode.FILL:
      return {
        ...baseLayer,
        type: "fill",
        paint: {
          "fill-color": fillColorMap[
            layerConfig.dataType
          ] as DataDrivenPropertyValueSpecification<"ExpressionSpecification">,
          "fill-outline-color": "#00000000",
          "fill-opacity": smartOpacity
        }
      } as AddLayerObject

    case LayerRenderMode.SYMBOL:
      if (layerConfig.dataType === DataType.PLANTABILITY) {
        return {
          ...baseLayer,
          type: "symbol",
          layout: {
            "symbol-placement": "point",
            "icon-image": [
              "case",
              [">=", ["get", "indice"], 7],
              "tree-icon",
              [">=", ["get", "indice"], 4],
              "warning-icon",
              "none-icon"
            ],
            "icon-size": ["interpolate", ["linear"], ["zoom"], 10, 0.8, 15, 1.2],
            "icon-allow-overlap": false,
            "icon-ignore-placement": false,
            "symbol-spacing": 200,
            "symbol-avoid-edges": true
          },
          paint: {
            "icon-opacity": smartOpacity
          }
        } as AddLayerObject
      }
      return {
        ...baseLayer,
        type: "circle",
        layout: {
          "circle-sort-key": ["get", radiusField]
        },
        paint: {
          "circle-color": fillColorMap[
            layerConfig.dataType
          ] as DataDrivenPropertyValueSpecification<"ExpressionSpecification">,
          "circle-radius": [
            "interpolate",
            ["linear"],
            ["get", radiusField],
            0,
            4,
            maxRadius / 2,
            8,
            maxRadius,
            16
          ],
          "circle-opacity": Math.min(0.8, smartOpacity + 0.2),
          "circle-stroke-width": ["interpolate", ["linear"], ["zoom"], 10, 1, 15, 2, 20, 3],
          "circle-stroke-color": "#ffffff",
          "circle-stroke-opacity": 1.0
        }
      } as AddLayerObject
    default:
      return {
        ...baseLayer,
        type: "fill",
        paint: {
          "fill-color": fillColorMap[
            layerConfig.dataType
          ] as DataDrivenPropertyValueSpecification<"ExpressionSpecification">,
          "fill-outline-color": "#00000000",
          "fill-opacity": smartOpacity
        }
      } as AddLayerObject
  }
}

export const calculateZIndex = (
  activeLayers: Ref<LayerConfig[]>,
  dataType: DataType,
  renderMode: LayerRenderMode
): number => {
  const zIndexRanges = {
    [DataType.PLANTABILITY]: { min: 100, max: Infinity },
    [DataType.VULNERABILITY]: { min: 50, max: 99 },
    [DataType.CLIMATE_ZONE]: { min: 10, max: 49 }
  }

  if (
    dataType === DataType.PLANTABILITY &&
    ![LayerRenderMode.FILL, LayerRenderMode.SYMBOL].includes(renderMode)
  ) {
    return Math.max(...activeLayers.value.map((l) => l.zIndex), 0) + 1
  }

  const range = zIndexRanges[dataType]
  if (!range) {
    return Math.max(...activeLayers.value.map((l) => l.zIndex), 0) + 1
  }

  const existingIndexes = activeLayers.value
    .map((l) => l.zIndex)
    .filter((zIndex) => zIndex >= range.min && zIndex <= range.max)

  return existingIndexes.length > 0 ? Math.max(...existingIndexes) + 1 : range.min
}
