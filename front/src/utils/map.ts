import { DataType, GeoLevel } from "@/utils/enum"
import { Map } from "maplibre-gl"

export const highlightFeature = (map: Map, layerId: string, featureId: string) => {
  map.setPaintProperty(layerId, "fill-outline-color", [
    "match",
    ["get", "id"],
    featureId,
    "#000000",
    "#00000000"
  ])
}

export const clearHighlight = (map: Map, layerId: string) => {
  map.setPaintProperty(layerId, "fill-outline-color", "#00000000")
}

export const getSourceId = (datatype: DataType, geolevel: GeoLevel) => {
  return `${geolevel}-${datatype}-source`
}

export const getLayerId = (datatype: DataType, geolevel: GeoLevel) => {
  return `${geolevel}-${datatype}-layer`
}

export const extractFeatures = (features: Array<any>, datatype: DataType, geolevel: GeoLevel) => {
  if (!features) return undefined

  const feature = features.find(
    (feature: any) => feature.layer.id === getLayerId(datatype, geolevel)
  )

  return feature || undefined
}

export const extractFeatureProperty = (
  features: Array<any>,
  datatype: DataType,
  geolevel: GeoLevel,
  propertyName?: string
) => {
  const feature = extractFeatures(features, datatype, geolevel)
  if (!feature) return undefined
  return propertyName ? feature.properties[propertyName] : feature.properties
}

export const extractFeatureProperties = (
  features: Array<any>,
  datatype: DataType,
  geolevel: GeoLevel
) => {
  return extractFeatureProperty(features, datatype, geolevel)
}

export const setupMapIcons = (map: Map) => {
  const createEmojiIcon = (name: string, emoji: string, size: number) => {
    if (!map.hasImage(name)) {
      const canvas = document.createElement("canvas")
      canvas.width = size
      canvas.height = size
      const ctx = canvas.getContext("2d")

      if (!ctx) return
      ctx.textAlign = "center"
      ctx.textBaseline = "middle"
      ctx.fillText(emoji, size / 2, size / 2)
      const imageData = ctx.getImageData(0, 0, size, size)
      map.addImage(name, imageData)
    }
  }

  createEmojiIcon("tree-icon", "🌳", 24)
  createEmojiIcon("warning-icon", "⚠️", 22)
}
