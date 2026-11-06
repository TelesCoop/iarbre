import type { ExpressionSpecification } from "maplibre-gl"

export const PET_YEARS = [2020, 2090] as const

export type PetYear = (typeof PET_YEARS)[number]

export const DEFAULT_PET_YEAR: PetYear = 2090

export const PET_HOURS = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21] as const

export type PetHour = (typeof PET_HOURS)[number]

export const DEFAULT_PET_HOUR: PetHour = 16

export const buildPetTileUrl = (baseApiUrl: string, year: PetYear, hour: PetHour): string =>
  `${baseApiUrl}/tiles/pet/{z}/{x}/{y}.png?year=${year}&hour=${hour}`

export interface PetLegendItem {
  value: number
  color: string
  label: string
  detail: string
}

export const PET_LEGEND: PetLegendItem[] = [
  {
    value: 4,
    color: "#9ecae1",
    label: "13 - 18 °C - Légèrement frais",
    detail: "Léger stress dû au froid"
  },
  { value: 5, color: "#ffffcc", label: "18 - 23 °C - Neutre", detail: "Aucun stress thermique" },
  {
    value: 6,
    color: "#fed976",
    label: "23 - 29 °C - Légèrement chaud",
    detail: "Léger stress thermique"
  },
  { value: 7, color: "#fd8d3c", label: "29 - 35 °C - Chaud", detail: "Stress thermique modéré" },
  { value: 8, color: "#e31a1c", label: "35 - 41 °C - Très chaud", detail: "Fort stress thermique" },
  {
    value: 9,
    color: "#800026",
    label: "> 41 °C - Extrêmement chaud",
    detail: "Stress thermique extrême"
  }
]

export const formatHour = (hour: number): string => `${hour}h`

const TRANSPARENT = "rgba(0,0,0,0)"
const CLASS_HALF_WIDTH = 0.5
const RAMP_EPSILON = 0.01

export const buildPetColorRamp = (visibleValues: number[] = []): ExpressionSpecification =>
  [
    "interpolate",
    ["linear"],
    ["elevation"],
    ...PET_LEGEND.flatMap(({ value, color }) => {
      const shown = !visibleValues.length || visibleValues.includes(value) ? color : TRANSPARENT
      return [
        value - CLASS_HALF_WIDTH,
        TRANSPARENT,
        value - CLASS_HALF_WIDTH + RAMP_EPSILON,
        shown,
        value + CLASS_HALF_WIDTH - RAMP_EPSILON,
        shown
      ]
    }),
    PET_LEGEND[PET_LEGEND.length - 1].value + CLASS_HALF_WIDTH,
    TRANSPARENT
  ] as unknown as ExpressionSpecification
