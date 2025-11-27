import { type DataType } from "@/utils/enum"

export interface MapParams {
  lng: number
  lat: number
  zoom: number
  dataType: DataType | null
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
