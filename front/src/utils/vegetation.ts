export enum VegetationLegendName {
  LOW = "Végétation basse",
  MID = "Végétation moyenne",
  HIGH = "Végétation haute"
}

export enum VegetationColor {
  LOW = "#C8D96F",
  MID = "#3A9144",
  HIGH = "#14452F"
}

export const VEGESTRATE_COLOR_MAP = [
  "herbacee",
  VegetationColor.LOW,
  "arbustif",
  VegetationColor.MID,
  "arborescent",
  VegetationColor.HIGH,
  "#00000000"
]

export const VegetationLegend: Record<VegetationLegendName, VegetationColor> = {
  [VegetationLegendName.LOW]: VegetationColor.LOW,
  [VegetationLegendName.MID]: VegetationColor.MID,
  [VegetationLegendName.HIGH]: VegetationColor.HIGH
}
