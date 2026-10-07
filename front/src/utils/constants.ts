import type { MapParams } from "@/types/map"
import { DEFAULT_LAYER_KEY } from "@/utils/rasterLayers"

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
  layer: DEFAULT_LAYER_KEY,
  lng: DEFAULT_MAP_CENTER.lng,
  lat: DEFAULT_MAP_CENTER.lat,
  zoom: 14
}
