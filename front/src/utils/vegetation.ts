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

export function getZoneDesc(zone: string): string {
  return STRATE_MAP[zone as VegetationIndice]?.label ?? "Description de strate non possible"
}

export function getZoneColor(zone: string): string {
  return STRATE_MAP[zone as VegetationIndice]?.color ?? "#CCCCCC"
}
