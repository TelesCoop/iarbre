import { type DataType } from "@/utils/enum"

export interface MapScorePopupData {
  lng: number
  lat: number
  id: string
  properties: any
  score: string
}

export enum BlendMode {
  NORMAL = "normal",
  MULTIPLY = "multiply",
  SCREEN = "screen",
  OVERLAY = "overlay",
  DARKEN = "darken",
  LIGHTEN = "lighten",
  COLOR_DODGE = "color-dodge",
  COLOR_BURN = "color-burn",
  HARD_LIGHT = "hard-light",
  SOFT_LIGHT = "soft-light",
  DIFFERENCE = "difference",
  EXCLUSION = "exclusion"
}

export enum LayerRenderMode {
  FILL = "fill",
  PATTERN = "pattern",
  SYMBOL = "symbol",
  OUTLINE = "outline",
  HEATMAP = "heatmap",
  HILLSHADE = "hillshade",
  COLOR_RELIEF = "color-relief"
}

export interface LayerConfig {
  dataType: DataType
  visible: boolean
  opacity: number
  zIndex: number
  filters: (number | string)[]
  blendMode: BlendMode
  renderMode: LayerRenderMode
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
