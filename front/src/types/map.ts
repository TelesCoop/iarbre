import { type DataType, type MapStyle, type OverlayLayer } from "@/utils/enum"

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
