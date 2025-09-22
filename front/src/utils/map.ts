import { DataType, GeoLevel } from "@/utils/enum"
import { Map } from "maplibre-gl"

export const highlightFeature = (map: Map, layerId: string, featureId: string) => {
  map.setPaintProperty(`${layerId}-border`, "line-width", ["match", ["get", "id"], featureId, 3, 0])
  map.setPaintProperty(`${layerId}-border`, "line-color", [
    "match",
    ["get", "id"],
    featureId,
    "#FFFFFF",
    "#00000000"
  ])
}

export const clearHighlight = (map: Map, layerId: string) => {
  map.setPaintProperty(`${layerId}-border`, "line-width", 0)
  map.setPaintProperty(`${layerId}-border`, "line-color", "#00000000")
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
