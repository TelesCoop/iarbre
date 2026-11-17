import type { MapParams } from "@/types/map"
import { DataType, MapStyle } from "@/utils/enum"

export enum Layout {
  Default = "Default"
}

export const MIN_ZOOM = 10
export const MAX_ZOOM = 18
export const MAP_CONTROL_POSITION = "bottom-right"

// Villeurbanne, centre of the plantability 2026 rasters
export const DEFAULT_MAP_CENTER = {
  lng: 4.89007,
  lat: 45.77218
}

export const DEFAULT_DATA_TYPE = DataType.PLANTABILITY_2026_1M

export const DEFAULT_MAP_PARAMS: MapParams = {
  dataType: DEFAULT_DATA_TYPE,
  lng: DEFAULT_MAP_CENTER.lng,
  lat: DEFAULT_MAP_CENTER.lat,
  zoom: 14
}

export const DEFAULT_MAP_STYLE = MapStyle.ORTHOPHOTO

// Terra Draw layer name (used to position layers below drawing layers)
export const TERRA_DRAW_POLYGON_LAYER = "td-polygon"
export const TERRA_DRAW_ID_PREFIX = "td-"

// Mirrors the backend ScoresInPolygonView.MAX_POLYGON_AREA_M2 (5 km²): selections
// larger than this are not sent to the server, to avoid saturating it.
export const MAX_SHAPE_AREA_M2 = 5_000_000
