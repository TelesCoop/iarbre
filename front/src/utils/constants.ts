import type { MapParams } from "@/types/map"
import { DataType } from "@/utils/enum"

export enum Layout {
  Default = "Default"
}

export const MIN_ZOOM = 10
export const MAX_ZOOM = 18
export const MAP_CONTROL_POSITION = "bottom-right"

// Lyon Part-Dieu
export const DEFAULT_MAP_CENTER = {
  lng: 4.85377,
  lat: 45.75773
}

export const DEFAULT_MAP_PARAMS: MapParams = {
  dataType: DataType.PLANTABILITY,
  lng: DEFAULT_MAP_CENTER.lng,
  lat: DEFAULT_MAP_CENTER.lat,
  zoom: 14
}

// Terra Draw layer name (used to position layers below drawing layers)
export const TERRA_DRAW_POLYGON_LAYER = "td-polygon"
