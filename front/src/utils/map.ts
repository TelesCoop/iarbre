import { DataType, GeoLevel } from "@/utils/enum"
import { type AddLayerObject, type DataDrivenPropertyValueSpecification, Map } from "maplibre-gl"

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
