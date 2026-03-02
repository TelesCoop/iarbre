import type { VegetationIndice } from "@/types/vegetation"

type StrateInfo = { label: string; color: string }

const STRATE_MAP: Record<VegetationIndice, StrateInfo> = {
  herbacee: { label: "Strate herbacée", color: "#C8D96F" },
  arbustif: { label: "Strate arbustive < 1.5m", color: "#3A9144" },
  arborescent: { label: "Strate arborée > 1.5m", color: "#14452F" }
}

export const VEGESTRATE_COLOR_MAP = [
  ...Object.entries(STRATE_MAP).flatMap(([k, v]) => [k, v.color]),
  "#00000000"
]

export const VegetationLegend: Record<string, string> = Object.fromEntries(
  Object.values(STRATE_MAP).map(({ label, color }) => [label, color])
)

export function getZoneDesc(zone: string): string {
  return STRATE_MAP[zone as VegetationIndice]?.label ?? "Description de strate non possible"
}

export function getZoneColor(zone: string): string {
  return STRATE_MAP[zone as VegetationIndice]?.color ?? "#CCCCCC"
}
