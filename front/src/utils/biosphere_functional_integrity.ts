export const BIOSPHERE_FUNCTIONAL_INTEGRITY_COLOR_MAP = [
  "#ffffffff",
  0,
  "#a50f15",
  5,
  "#de2d26",
  10,
  "#fb6a4a",
  15,
  "#fca483",
  20,
  "#fecab1",
  25,
  "#f7fcfd",
  30,
  "#e5efe5",
  35,
  "#d4e2dd",
  40,
  "#c2d5cd",
  45,
  "#b0c7bc",
  50,
  "#9fbaac",
  55,
  "#8dad9c",
  60,
  "#7ca08c",
  65,
  "#6a937c",
  70,
  "#58866c",
  75,
  "#356b4b",
  80,
  "#235e3b",
  85,
  "#12512b",
  90,
  "#00441b"
]

export enum BiosphereIntegrityLegendName {
  LOW = "Entre 0% et 25%",
  MID = "Entre 25% et 50%",
  HIGH = "Entre 50% et 100%"
}

export enum BiosphereIntegrityColor {
  LOW = "#a50f15",
  MID = "#f7fcfd",
  HIGH = "#00441b"
}

export const BiosphereIntegrityLegend: Record<
  BiosphereIntegrityLegendName,
  BiosphereIntegrityColor
> = {
  [BiosphereIntegrityLegendName.LOW]: BiosphereIntegrityColor.LOW,
  [BiosphereIntegrityLegendName.MID]: BiosphereIntegrityColor.MID,
  [BiosphereIntegrityLegendName.HIGH]: BiosphereIntegrityColor.HIGH
}

export const BIOSPHERE_INTEGRITY_RANGES: Record<BiosphereIntegrityLegendName, [number, number]> = {
  [BiosphereIntegrityLegendName.LOW]: [0, 25],
  [BiosphereIntegrityLegendName.MID]: [25, 50],
  [BiosphereIntegrityLegendName.HIGH]: [50, 100]
}
