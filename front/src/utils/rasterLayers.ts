import type { LayerSpecification } from "maplibre-gl"
import { LAYER_330300 } from "@/utils/layers330300"

export interface LegendItem {
  color: string
  label: string
  detail?: string
}

export interface LayerToggle {
  key: string
  label: string
  layerIds: string[]
  defaultHidden?: boolean
}

export interface LegendCard extends LayerToggle {
  description: string
  legendStyle: "tile" | "outline" | "swatch"
  legend: LegendItem[]
  subToggles?: LayerToggle[]
}

export interface RasterLayer {
  key: string
  label: string
  description: string
  attribution: string
  hourly: boolean
  legend: LegendItem[]
  cards?: LegendCard[]
  vectorSource?: {
    tilesPath: string
    maxzoom: number
    bounds: [number, number, number, number]
  }
  styleLayers?: LayerSpecification[]
}

export const RASTER_LAYERS: RasterLayer[] = [LAYER_330300]

export const DEFAULT_LAYER_KEY = RASTER_LAYERS[0].key

export const HOURS = Array.from({ length: 15 }, (_, index) => index + 7)

export const DEFAULT_HOUR = 16

export const getRasterLayer = (key: string): RasterLayer =>
  RASTER_LAYERS.find((layer) => layer.key === key) ?? RASTER_LAYERS[0]

export const formatHour = (hour: number): string => `${hour}h`

export const buildTileUrl = (
  baseApiUrl: string,
  layer: RasterLayer,
  hour: number,
  hiddenClasses: number[] = []
): string => {
  const params = new URLSearchParams({ mode: layer.key })
  if (layer.hourly) params.set("hour", String(hour))
  if (hiddenClasses.length) {
    const visibleClasses = layer.legend
      .map((_, index) => index)
      .filter((index) => !hiddenClasses.includes(index))
    params.set("classes", visibleClasses.join(","))
  }
  return `${baseApiUrl}/tiles/heat/{z}/{x}/{y}.png?${params}`
}

export const buildRasterUrl = (baseApiUrl: string, layer: RasterLayer, hour?: number): string => {
  const url = `${baseApiUrl}/rasters/${layer.key}/`
  return layer.hourly && hour !== undefined ? `${url}?hour=${hour}` : url
}

export const buildMediaTileUrl = (baseApiUrl: string, tilesPath: string): string =>
  `${baseApiUrl.replace(/\/api\/?$/, "")}/media/${tilesPath}/{z}/{x}/{y}.pbf`

export const layerToggles = (layer: RasterLayer): LayerToggle[] =>
  (layer.cards ?? []).flatMap((card) => [card, ...(card.subToggles ?? [])])

export const defaultHiddenToggles = (layer: RasterLayer): string[] =>
  layerToggles(layer)
    .filter((toggle) => toggle.defaultHidden)
    .map((toggle) => toggle.key)
