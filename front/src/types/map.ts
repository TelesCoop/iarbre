import { type DataType } from "@/utils/enum"

export interface MapScorePopupData {
  lng: number
  lat: number
  id: string
  properties: any
  score: string
}

export interface MultiLayerPopupData {
  lng: number
  lat: number
  layers: LayerPopupData[]
}

export interface LayerPopupData {
  dataType: DataType
  id: string
  properties: any
  score: string
}

export interface LayerConfig {
  dataType: DataType
  visible: boolean
  opacity: number
  zIndex: number
  filters: (number | string)[]
}

export interface FilterConfig {
  dataType: DataType
  filteredValues: (number | string)[]
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
