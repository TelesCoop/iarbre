import type { VegetationIndice } from "@/types/vegetation"

export enum VegestrateMode {
  RAW_2018_02 = "raw_2018_02",
  POSTPROCESS_V3_2018_02 = "postprocess_v3_2018_02",
  RAW_2023_02 = "raw_2023_02",
  POSTPROCESS_V1_2023_02 = "postprocess_v1_2023_02",
  POSTPROCESS_V2_2023_02 = "postprocess_v2_2023_02",
  POSTPROCESS_V3_2023_02 = "postprocess_v3_2023_02"
}

export const VegestrateModeToParams: Record<
  VegestrateMode,
  { year: number; resolution: string; postprocess: boolean; version: number | null }
> = {
  [VegestrateMode.RAW_2018_02]: { year: 2018, resolution: "02", postprocess: false, version: null },
  [VegestrateMode.POSTPROCESS_V3_2018_02]: {
    year: 2018,
    resolution: "02",
    postprocess: true,
    version: 3
  },
  [VegestrateMode.RAW_2023_02]: { year: 2023, resolution: "02", postprocess: false, version: null },
  [VegestrateMode.POSTPROCESS_V1_2023_02]: {
    year: 2023,
    resolution: "02",
    postprocess: true,
    version: 1
  },
  [VegestrateMode.POSTPROCESS_V2_2023_02]: {
    year: 2023,
    resolution: "02",
    postprocess: true,
    version: 2
  },
  [VegestrateMode.POSTPROCESS_V3_2023_02]: {
    year: 2023,
    resolution: "02",
    postprocess: true,
    version: 3
  }
}

export const VegestrateModeToLabel: Record<VegestrateMode, string> = {
  [VegestrateMode.RAW_2018_02]: "2018 - 20cms - brut",
  [VegestrateMode.POSTPROCESS_V3_2018_02]: "2018 - 20cms - post-traitement v3",
  [VegestrateMode.RAW_2023_02]: "2023 - 20cms - brut",
  [VegestrateMode.POSTPROCESS_V1_2023_02]: "2023 - 20cms - post-traitement v1",
  [VegestrateMode.POSTPROCESS_V2_2023_02]: "2023 - 20cms - post-traitement v2",
  [VegestrateMode.POSTPROCESS_V3_2023_02]: "2023 - 20cms - post-traitement v3"
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

export function getZoneDesc(zone: string): string {
  return STRATE_MAP[zone as VegetationIndice]?.label ?? "Description de strate non possible"
}

export function getZoneColor(zone: string): string {
  return STRATE_MAP[zone as VegetationIndice]?.color ?? "#CCCCCC"
}
