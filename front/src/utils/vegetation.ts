import type { ExpressionSpecification } from "maplibre-gl"
import type { VegetationIndice } from "@/types/vegetation"

type StrateInfo = {
  label: string
  short: string
  heightCategory: string
  range: string
  color: string
  height: number
}

const STRATE_MAP: Record<VegetationIndice, StrateInfo> = {
  herbacee: {
    label: "Strate herbacée < 1,5 m",
    short: "Herbacée",
    heightCategory: "Basse",
    range: "< 1,5 m",
    color: "#ecdeb1",
    height: 0.5
  },
  arbustif: {
    label: "Strate arbustive 1,5 - 5 m",
    short: "Arbustive",
    heightCategory: "Moyenne",
    range: "1,5 - 5 m",
    color: "#8bb971",
    height: 1.5
  },
  arborescent: {
    label: "Strate arborée > 5 m",
    short: "Arborée",
    heightCategory: "Haute",
    range: "> 5 m",
    color: "#0f6f4f",
    height: 4
  }
}

export const VEGESTRATE_COLOR_MAP = [
  ...Object.entries(STRATE_MAP).flatMap(([k, v]) => [k, v.color]),
  "#00000000"
]

export const VEGESTRATE_HEIGHT_MAP = [
  ...Object.entries(STRATE_MAP).flatMap(([k, v]) => [k, v.height]),
  0
]

export const VegetationLegend = Object.entries(STRATE_MAP).map(([key, { label, color }]) => ({
  indice: key as VegetationIndice,
  label,
  color
}))

const STRATE_ENTRIES_TALLEST_FIRST = (
  Object.entries(STRATE_MAP) as [VegetationIndice, StrateInfo][]
)
  .slice()
  .reverse()

export const STRATE_CATEGORIES = STRATE_ENTRIES_TALLEST_FIRST.map(([indice, { short, range }]) => ({
  indice,
  label: short,
  range
}))

export const HEIGHT_CATEGORIES = STRATE_ENTRIES_TALLEST_FIRST.map(
  ([, { heightCategory, range }]) => ({
    label: heightCategory,
    range
  })
)

export const STRATE_GRADIENT_CSS = `linear-gradient(to top, ${Object.values(STRATE_MAP)
  .map((s) => s.color)
  .join(", ")})`

const ELEVATION_MAX = 40
export const ELEVATION_BINS = [
  { min: 0, color: "#ecdeb1" },
  { min: 1, color: "#e6dcac" },
  { min: 2, color: "#e1daa6" },
  { min: 4, color: "#d5d69b" },
  { min: 7, color: "#c4cf8b" },
  { min: 10, color: "#b3c97b" },
  { min: 15, color: "#8bb971" },
  { min: 20, color: "#63a966" },
  { min: 26, color: "#348e5c" },
  { min: 33, color: "#0f6f4f" }
]

export const sqrtPos = (value: number) =>
  parseFloat((Math.sqrt(value / ELEVATION_MAX) * 100).toFixed(1))

export const ELEVATION_GRADIENT_CSS = `linear-gradient(to right, ${ELEVATION_BINS.map((b) => `${b.color} ${sqrtPos(b.min)}%`).join(", ")})`

export const ELEVATION_LABEL_STOPS = [
  { label: "0m", position: 0 },
  { label: "10m", position: sqrtPos(10) },
  { label: "20m", position: sqrtPos(20) },
  { label: "40m", position: 100 }
]

export type HeightRange = { min: number; max: number | null }

const TRANSPARENT = "rgba(0,0,0,0)"
const RAMP_EPSILON = 0.01
const RAMP_MIN_HEIGHT = -1
const RAMP_MAX_HEIGHT = 1000

type RampStop = [number, string]

export function elevationColorAt(height: number): string {
  return ELEVATION_BINS.reduce(
    (color, bin) => (height >= bin.min ? bin.color : color),
    ELEVATION_BINS[0].color
  )
}

export function normalizeHeightRanges(ranges: HeightRange[]): HeightRange[] {
  const valid = ranges
    .filter(({ min, max }) => min >= 0 && (max === null || max > min))
    .sort((a, b) => a.min - b.min)

  return valid.reduce<HeightRange[]>((merged, range) => {
    const previous = merged[merged.length - 1]
    if (!previous) return [{ ...range }]
    if (previous.max === null) return merged
    if (range.min > previous.max) return [...merged, { ...range }]
    previous.max = range.max === null ? null : Math.max(previous.max, range.max)
    return merged
  }, [])
}

export function formatHeightRange({ min, max }: HeightRange): string {
  return max === null ? `> ${min} m` : `${min} – ${max} m`
}

export function heightRangeColor({ min, max }: HeightRange): string {
  return elevationColorAt(max === null ? min : (min + max) / 2)
}

const continuousStops = (): RampStop[] =>
  ELEVATION_BINS.flatMap((bin, index) => {
    const next = ELEVATION_BINS[index + 1]
    return [
      [bin.min, bin.color],
      [next ? next.min - RAMP_EPSILON : RAMP_MAX_HEIGHT, bin.color]
    ] as RampStop[]
  })

const rangeStops = (ranges: HeightRange[]): RampStop[] =>
  ranges.flatMap(({ min, max }) => {
    const color = heightRangeColor({ min, max })
    const stops: RampStop[] = []
    if (min > 0) stops.push([min - RAMP_EPSILON, TRANSPARENT])
    stops.push([min, color])
    if (max === null) {
      stops.push([RAMP_MAX_HEIGHT, color])
    } else {
      stops.push([max - RAMP_EPSILON, color], [max, TRANSPARENT])
    }
    return stops
  })

export function buildElevationColorRamp(ranges: HeightRange[] = []): ExpressionSpecification {
  const normalized = normalizeHeightRanges(ranges)
  const stops: RampStop[] = [
    [RAMP_MIN_HEIGHT, TRANSPARENT],
    [-RAMP_EPSILON, TRANSPARENT],
    ...(normalized.length ? rangeStops(normalized) : continuousStops())
  ]
  return [
    "interpolate",
    ["linear"],
    ["elevation"],
    ...stops.flat()
  ] as unknown as ExpressionSpecification
}

export function getStrateShort(zone: string): string {
  return STRATE_MAP[zone as VegetationIndice]?.short ?? "—"
}
