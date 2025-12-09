export enum VegetationLegendName {
  LOW = "Végétation basse",
  MID = "Végétation moyenne",
  HIGH = "Végétation haute"
}

export enum VegetationColor {
  LOW = "rgb(46, 242, 24)",
  MID = "rgb(228, 242, 24)",
  HIGH = "rgb(22, 81, 15)"
}

export const VegetationLegend: Record<VegetationLegendName, VegetationColor> = {
  [VegetationLegendName.LOW]: VegetationColor.LOW,
  [VegetationLegendName.MID]: VegetationColor.MID,
  [VegetationLegendName.HIGH]: VegetationColor.HIGH
}
