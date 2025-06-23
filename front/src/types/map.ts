import { type DataType } from "@/utils/enum"

export interface MapScorePopupData {
  lng: number
  lat: number
  id: string
  properties: any
  score: string
}

export enum LayerRenderMode {
  FILL = "fill",
  SYMBOL = "symbol",
  COLOR_RELIEF = "color-relief"
}

export interface LayerConfig {
  dataType: DataType
  visible: boolean
  opacity: number
  zIndex: number
  filters: (number | string)[]
  renderMode: LayerRenderMode
}

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
