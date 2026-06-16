import type { VegetationIndice } from "@/types/vegetation"

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
export const ELEVATION_BINS = [
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

export const sqrtPos = (value: number) =>
  parseFloat((Math.sqrt(value / ELEVATION_MAX) * 100).toFixed(1))

export const ELEVATION_GRADIENT_CSS = `linear-gradient(to right, ${ELEVATION_BINS.map((b) => `${b.color} ${sqrtPos(b.min)}%`).join(", ")})`

export const ELEVATION_LABEL_STOPS = [
  { label: "0m", position: 0 },
  { label: "10m", position: sqrtPos(10) },
  { label: "20m", position: sqrtPos(20) },
  { label: "40m", position: 100 }
]

export function getZoneDesc(zone: string): string {
  return STRATE_MAP[zone as VegetationIndice]?.label ?? "Description de strate non possible"
}

export function getZoneColor(zone: string): string {
  return STRATE_MAP[zone as VegetationIndice]?.color ?? "#CCCCCC"
}
