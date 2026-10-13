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

export const BIOSPHERE_DETAIL_ZOOM = 15

export enum BiosphereIntegrityDetailColor {
  CRITICAL_1 = "#BC261D",
  CRITICAL_2 = "#CF3F20",
  LOW_1 = "#C74B1C",
  LOW_2 = "#B68228",
  MID_1 = "#AFA438",
  MID_2 = "#8AC34C",
  GOOD_1 = "#71BB4E",
  GOOD_2 = "#389134",
  HIGH_1 = "#1F751C",
  HIGH_2 = "#024500"
}

export enum BiosphereIntegrityDetailLegendName {
  CRITICAL_1 = "Entre 0% et 6%",
  CRITICAL_2 = "Entre 6% et 12%",
  LOW_1 = "Entre 12% et 19%",
  LOW_2 = "Entre 19% et 25%",
  MID_1 = "Entre 25% et 37%",
  MID_2 = "Entre 37% et 50%",
  GOOD_1 = "Entre 50% et 62%",
  GOOD_2 = "Entre 62% et 75%",
  HIGH_1 = "Entre 75% et 87%",
  HIGH_2 = "Entre 87% et 100%"
}

export const BIOSPHERE_FUNCTIONAL_INTEGRITY_DETAIL_COLOR_MAP = [
  "#d4d4d4",
  0,
  BiosphereIntegrityDetailColor.CRITICAL_1,
  6,
  BiosphereIntegrityDetailColor.CRITICAL_2,
  12,
  BiosphereIntegrityDetailColor.LOW_1,
  19,
  BiosphereIntegrityDetailColor.LOW_2,
  25,
  BiosphereIntegrityDetailColor.MID_1,
  37,
  BiosphereIntegrityDetailColor.MID_2,
  50,
  BiosphereIntegrityDetailColor.GOOD_1,
  62,
  BiosphereIntegrityDetailColor.GOOD_2,
  75,
  BiosphereIntegrityDetailColor.HIGH_1,
  87,
  BiosphereIntegrityDetailColor.HIGH_2
]

export const BiosphereIntegrityDetailLegend: Record<
  BiosphereIntegrityDetailLegendName,
  BiosphereIntegrityDetailColor
> = {
  [BiosphereIntegrityDetailLegendName.CRITICAL_1]: BiosphereIntegrityDetailColor.CRITICAL_1,
  [BiosphereIntegrityDetailLegendName.CRITICAL_2]: BiosphereIntegrityDetailColor.CRITICAL_2,
  [BiosphereIntegrityDetailLegendName.LOW_1]: BiosphereIntegrityDetailColor.LOW_1,
  [BiosphereIntegrityDetailLegendName.LOW_2]: BiosphereIntegrityDetailColor.LOW_2,
  [BiosphereIntegrityDetailLegendName.MID_1]: BiosphereIntegrityDetailColor.MID_1,
  [BiosphereIntegrityDetailLegendName.MID_2]: BiosphereIntegrityDetailColor.MID_2,
  [BiosphereIntegrityDetailLegendName.GOOD_1]: BiosphereIntegrityDetailColor.GOOD_1,
  [BiosphereIntegrityDetailLegendName.GOOD_2]: BiosphereIntegrityDetailColor.GOOD_2,
  [BiosphereIntegrityDetailLegendName.HIGH_1]: BiosphereIntegrityDetailColor.HIGH_1,
  [BiosphereIntegrityDetailLegendName.HIGH_2]: BiosphereIntegrityDetailColor.HIGH_2
}

export const BIOSPHERE_INTEGRITY_DETAIL_RANGES: Record<
  BiosphereIntegrityDetailLegendName,
  [number, number]
> = {
  [BiosphereIntegrityDetailLegendName.CRITICAL_1]: [0, 6],
  [BiosphereIntegrityDetailLegendName.CRITICAL_2]: [6, 12],
  [BiosphereIntegrityDetailLegendName.LOW_1]: [12, 19],
  [BiosphereIntegrityDetailLegendName.LOW_2]: [19, 25],
  [BiosphereIntegrityDetailLegendName.MID_1]: [25, 37],
  [BiosphereIntegrityDetailLegendName.MID_2]: [37, 50],
  [BiosphereIntegrityDetailLegendName.GOOD_1]: [50, 62],
  [BiosphereIntegrityDetailLegendName.GOOD_2]: [62, 75],
  [BiosphereIntegrityDetailLegendName.HIGH_1]: [75, 87],
  [BiosphereIntegrityDetailLegendName.HIGH_2]: [87, 100]
}

export const BIOSPHERE_INTEGRITY_ALL_RANGES: Record<string, [number, number]> = {
  ...BIOSPHERE_INTEGRITY_RANGES,
  ...BIOSPHERE_INTEGRITY_DETAIL_RANGES
}

const parentOf = (detail: string): string => {
  const [detailMin, detailMax] = BIOSPHERE_INTEGRITY_ALL_RANGES[detail]
  return Object.entries(BIOSPHERE_INTEGRITY_RANGES).find(
    ([, [min, max]]) => detailMin >= min && detailMax <= max
  )![0]
}

export const toDetailFilters = (values: (number | string)[]): (number | string)[] =>
  values.flatMap((value) =>
    value in BIOSPHERE_INTEGRITY_RANGES
      ? Object.keys(BIOSPHERE_INTEGRITY_DETAIL_RANGES).filter((d) => parentOf(d) === value)
      : [value]
  )

export const toCoarseFilters = (values: (number | string)[]): (number | string)[] => [
  ...new Set(
    values.map((value) =>
      typeof value === "string" && value in BIOSPHERE_INTEGRITY_DETAIL_RANGES
        ? parentOf(value)
        : value
    )
  )
]
