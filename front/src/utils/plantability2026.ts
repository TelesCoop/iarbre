import { DataType } from "@/utils/enum"
import { MAX_ZOOM } from "@/utils/constants"
import { HOURLY_RASTERS, type RasterClass } from "@/utils/hourlyRaster"
import {
  PLANTABILITY_COLOR_MAP,
  PLANTABILITY_SCORES,
  getPlantabilityScore
} from "@/utils/plantability"

export type Plantability2026Grid = 5 | 1

export const PLANTABILITY_2026_GRIDS: Partial<Record<DataType, Plantability2026Grid>> = {
  [DataType.PLANTABILITY_2026_5M]: 5,
  [DataType.PLANTABILITY_2026_1M]: 1
}

export const PLANTABILITY_2026_CLASSES: RasterClass[] = PLANTABILITY_SCORES.filter(
  (value) => typeof value === "number"
).map((value) => ({
  value,
  color: PLANTABILITY_COLOR_MAP[PLANTABILITY_COLOR_MAP.indexOf(value) + 1] as string,
  label: getPlantabilityScore(value),
  detail: ""
}))

export const isPlantability2026 = (dataType: DataType): boolean =>
  dataType in PLANTABILITY_2026_GRIDS

export const plantability2026TileUrl = (baseApiUrl: string, grid: Plantability2026Grid): string =>
  `${baseApiUrl}/tiles/plantability-2026/{z}/{x}/{y}.png?grid=${grid}`

export const PLANTABILITY_2026_MAX_ZOOM = 20

export const maxZoomFor = (dataType: DataType): number =>
  isPlantability2026(dataType) ? PLANTABILITY_2026_MAX_ZOOM : MAX_ZOOM

export const rasterClasses = (dataType: DataType): RasterClass[] | undefined =>
  HOURLY_RASTERS[dataType]?.classes ??
  (isPlantability2026(dataType) ? PLANTABILITY_2026_CLASSES : undefined)
