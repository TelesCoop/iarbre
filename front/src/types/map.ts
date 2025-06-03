import { type DataType } from "../utils/enum"

export interface MapScorePopupData {
  lng: number
  lat: number
  id: string
  properties: any
  score: string
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
