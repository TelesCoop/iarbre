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

export function getZoneDesc(zone: string): string {
  return STRATE_MAP[zone as VegetationIndice]?.label ?? "Description de strate non possible"
}

export function getZoneColor(zone: string): string {
  return STRATE_MAP[zone as VegetationIndice]?.color ?? "#CCCCCC"
}
