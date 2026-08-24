export enum BiosphereIntegrityColor {
  CRITICAL = "#d73026",
  LOW = "#BF5A16",
  MID = "#A6CC4A",
  GOOD = "#55B250",
  HIGH = "#025400"
}

export enum BiosphereIntegrityLegendName {
  CRITICAL = "Entre 0% et 12%",
  LOW = "Entre 12% et 25%",
  MID = "Entre 25% et 50%",
  GOOD = "Entre 50% et 75%",
  HIGH = "Entre 75% et 100%"
}

export const BIOSPHERE_FUNCTIONAL_INTEGRITY_COLOR_MAP = [
  "#d4d4d4",
  0,
  BiosphereIntegrityColor.CRITICAL,
  12,
  BiosphereIntegrityColor.LOW,
  25,
  BiosphereIntegrityColor.MID,
  50,
  BiosphereIntegrityColor.GOOD,
  75,
  BiosphereIntegrityColor.HIGH
]

export const BiosphereIntegrityLegend: Record<
  BiosphereIntegrityLegendName,
  BiosphereIntegrityColor
> = {
  [BiosphereIntegrityLegendName.CRITICAL]: BiosphereIntegrityColor.CRITICAL,
  [BiosphereIntegrityLegendName.LOW]: BiosphereIntegrityColor.LOW,
  [BiosphereIntegrityLegendName.MID]: BiosphereIntegrityColor.MID,
  [BiosphereIntegrityLegendName.GOOD]: BiosphereIntegrityColor.GOOD,
  [BiosphereIntegrityLegendName.HIGH]: BiosphereIntegrityColor.HIGH
}

export const BIOSPHERE_INTEGRITY_RANGES: Record<BiosphereIntegrityLegendName, [number, number]> = {
  [BiosphereIntegrityLegendName.CRITICAL]: [0, 12],
  [BiosphereIntegrityLegendName.LOW]: [12, 25],
  [BiosphereIntegrityLegendName.MID]: [25, 50],
  [BiosphereIntegrityLegendName.GOOD]: [50, 75],
  [BiosphereIntegrityLegendName.HIGH]: [75, 100]
}
