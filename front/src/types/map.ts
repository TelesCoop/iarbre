import {
  type DataType,
  type MapStyle,
  type OverlayLayer,
  type PublicBuildingCategory
} from "@/utils/enum"

export interface MapParams {
  lng: number
  lat: number
  zoom: number
  dataType: DataType | null
}

/** What is shown on top of the map position: score filters, basemap and overlay layers. */
export interface MapDisplayState {
  filters: (number | string)[]
  mapStyle: MapStyle
  overlayLayers: OverlayLayer[]
  /** Public building categories shown, all of them when undefined. */
  publicBuildingCategories?: PublicBuildingCategory[]
}

export interface Feedback {
  email: string
  feedback: string
}

export enum GeometryType {
  POINT = "Point",
  POLYGON = "Polygon",
  LINE_STRING = "LineString"
}
