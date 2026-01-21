export enum VegetationLegendName {
  LOW = "Végétation basse",
  MID = "Végétation moyenne",
  HIGH = "Végétation haute"
}

export enum VegetationColor {
  LOW = "#9DC183",
  MID = "#588157",
  HIGH = "#2D5A16"
}

export const VegetationLegend: Record<VegetationLegendName, VegetationColor> = {
  [VegetationLegendName.LOW]: VegetationColor.LOW,
  [VegetationLegendName.MID]: VegetationColor.MID,
  [VegetationLegendName.HIGH]: VegetationColor.HIGH
}
