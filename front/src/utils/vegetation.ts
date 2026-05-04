import type { VegetationIndice } from "@/types/vegetation"

export enum VegestrateMode {
  RAW_2018_02 = "raw_2018_02",
  POSTPROCESS_V3_2018_02 = "postprocess_v3_2018_02",
  RAW_2023_02 = "raw_2023_02",
  POSTPROCESS_V1_2023_02 = "postprocess_v1_2023_02",
  POSTPROCESS_V2_2023_02 = "postprocess_v2_2023_02",
  POSTPROCESS_V3_2023_02 = "postprocess_v3_2023_02",
  POSTPROCESS_V3_2023_ELEVATION_02 = "postprocess_v3_2023_elevation_02"
}

export const VegestrateModeToParams: Record<
  VegestrateMode,
  { year: number; resolution: string; postprocess: boolean; version: number | null; kind: string }
> = {
  [VegestrateMode.RAW_2018_02]: {
    year: 2018,
    resolution: "02",
    postprocess: false,
    version: null,
    kind: "class"
  },
  [VegestrateMode.POSTPROCESS_V3_2018_02]: {
    year: 2018,
    resolution: "02",
    postprocess: true,
    version: 3,
    kind: "class"
  },
  [VegestrateMode.RAW_2023_02]: {
    year: 2023,
    resolution: "02",
    postprocess: false,
    version: null,
    kind: "class"
  },
  [VegestrateMode.POSTPROCESS_V1_2023_02]: {
    year: 2023,
    resolution: "02",
    postprocess: true,
    version: 1,
    kind: "class"
  },
  [VegestrateMode.POSTPROCESS_V2_2023_02]: {
    year: 2023,
    resolution: "02",
    postprocess: true,
    version: 2,
    kind: "class"
  },
  [VegestrateMode.POSTPROCESS_V3_2023_02]: {
    year: 2023,
    resolution: "02",
    postprocess: true,
    version: 3,
    kind: "class"
  },
  [VegestrateMode.POSTPROCESS_V3_2023_ELEVATION_02]: {
    year: 2023,
    resolution: "02",
    postprocess: true,
    version: 3,
    kind: "elevation"
  }
}

export const VegestrateModeToLabel: Record<VegestrateMode, string> = {
  [VegestrateMode.RAW_2018_02]: "2018 - 20cms - brut",
  [VegestrateMode.POSTPROCESS_V3_2018_02]: "2018 - 20cms - post-traitement v3",
  [VegestrateMode.RAW_2023_02]: "2023 - 20cms - brut",
  [VegestrateMode.POSTPROCESS_V1_2023_02]: "2023 - 20cms - post-traitement v1",
  [VegestrateMode.POSTPROCESS_V2_2023_02]: "2023 - 20cms - post-traitement v2",
  [VegestrateMode.POSTPROCESS_V3_2023_02]: "2023 - 20cms - post-traitement v3",
  [VegestrateMode.POSTPROCESS_V3_2023_ELEVATION_02]: "2023 - 20cms - post-traitement v3 - hauteur"
}

type StrateInfo = { label: string; color: string; height: number }

const STRATE_MAP: Record<VegetationIndice, StrateInfo> = {
  herbacee: { label: "Strate herbacée", color: "#C8D96F", height: 0.5 },
  arbustif: { label: "Strate arbustive < 1.5m", color: "#3A9144", height: 1.5 },
  arborescent: { label: "Strate arborée > 1.5m", color: "#14452F", height: 4 }
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

const ELEVATION_MAX = 40
const ELEVATION_BINS = [
  { min: 0, color: "var(--color-primary-50)" },
  { min: 1, color: "var(--color-primary-100)" },
  { min: 2, color: "var(--color-primary-200)" },
  { min: 4, color: "var(--color-primary-300)" },
  { min: 7, color: "var(--color-primary-400)" },
  { min: 10, color: "var(--color-primary-500)" },
  { min: 15, color: "var(--color-primary-600)" },
  { min: 20, color: "var(--color-primary-700)" },
  { min: 26, color: "var(--color-primary-800)" },
  { min: 33, color: "var(--color-primary-900)" }
]

const sqrtPos = (value: number) => parseFloat((Math.sqrt(value / ELEVATION_MAX) * 100).toFixed(1))

export const ELEVATION_GRADIENT_CSS = `linear-gradient(to right, ${ELEVATION_BINS.map((b) => `${b.color} ${sqrtPos(b.min)}%`).join(", ")})`

export const ELEVATION_LABEL_STOPS = [
  { label: "0m", position: 0 },
  { label: "10m", position: sqrtPos(10) },
  { label: "40m", position: 100 }
]

export function isElevationMode(mode: VegestrateMode): boolean {
  return VegestrateModeToParams[mode].kind === "elevation"
}

export function getZoneDesc(zone: string): string {
  return STRATE_MAP[zone as VegetationIndice]?.label ?? "Description de strate non possible"
}

export function getZoneColor(zone: string): string {
  return STRATE_MAP[zone as VegetationIndice]?.color ?? "#CCCCCC"
}
