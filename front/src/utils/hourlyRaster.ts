import type { ExpressionSpecification } from "maplibre-gl"
import { DataType } from "@/utils/enum"
import { PET_RASTER } from "@/utils/pet"
import { SHADOW_RASTER } from "@/utils/shadow"

export interface RasterClass {
  value: number
  color: string
  label: string
  detail: string
}

export interface HourlyRaster {
  endpoint: string
  classes: RasterClass[]
  axisLabels: [string, string]
  columnLabels: [string, string]
  descriptionSummary: string
  years?: readonly number[]
}

export const HOURLY_RASTERS: Partial<Record<DataType, HourlyRaster>> = {
  [DataType.PET]: PET_RASTER,
  [DataType.SHADOW]: SHADOW_RASTER
}

export const isHourlyRaster = (dataType: DataType): boolean => dataType in HOURLY_RASTERS

export const HOURS = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21] as const

export type Hour = (typeof HOURS)[number]

export const DEFAULT_HOUR: Hour = 16

export const formatHour = (hour: number): string => `${hour}h`

export const buildTileUrl = (
  baseApiUrl: string,
  raster: HourlyRaster,
  hour: Hour,
  year: number
): string =>
  `${baseApiUrl}/tiles/${raster.endpoint}/{z}/{x}/{y}.png?${raster.years ? `year=${year}&` : ""}hour=${hour}`

const TRANSPARENT = "rgba(0,0,0,0)"
const RAMP_EPSILON_RATIO = 0.01

const classEdges = (classes: RasterClass[]): number[] => {
  const values = classes.map(({ value }) => value)
  const midpoints = values.slice(1).map((value, index) => (values[index] + value) / 2)
  const first = values[0]
  const last = values[values.length - 1]
  return [
    first - (midpoints[0] - first),
    ...midpoints,
    last + (last - midpoints[midpoints.length - 1])
  ]
}

export const buildColorRamp = (
  classes: RasterClass[],
  visibleValues: number[] = []
): ExpressionSpecification => {
  const edges = classEdges(classes)
  return [
    "interpolate",
    ["linear"],
    ["elevation"],
    ...classes.flatMap(({ value, color }, index) => {
      const lower = edges[index]
      const upper = edges[index + 1]
      const epsilon = (upper - lower) * RAMP_EPSILON_RATIO
      const shown = !visibleValues.length || visibleValues.includes(value) ? color : TRANSPARENT
      return [lower, TRANSPARENT, lower + epsilon, shown, upper - epsilon, shown]
    }),
    edges[edges.length - 1],
    TRANSPARENT
  ] as unknown as ExpressionSpecification
}
