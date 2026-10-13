export const BIOSPHERE_DETAIL_ZOOM = 14

const NO_DATA_COLOR = "#d4d4d4"

export interface BiosphereClass {
  label: string
  color: string
  min: number
  max: number
}

export const BIOSPHERE_CLASSES: BiosphereClass[] = [
  { label: "Entre 0% et 12%", color: "#d4322c", min: 0, max: 12 },
  { label: "Entre 12% et 25%", color: "#fdbc6e", min: 12, max: 25 },
  { label: "Entre 25% et 50%", color: "#c4e67f", min: 25, max: 50 },
  { label: "Entre 50% et 75%", color: "#64bc61", min: 50, max: 75 },
  { label: "Entre 75% et 100%", color: "#0b7b41", min: 75, max: 100 }
]

export const BIOSPHERE_DETAIL_CLASSES: BiosphereClass[] = [
  { label: "Entre 0% et 6%", color: "#b91327", min: 0, max: 6 },
  { label: "Entre 6% et 12%", color: "#e54f36", min: 6, max: 12 },
  { label: "Entre 12% et 19%", color: "#fa9a59", min: 12, max: 19 },
  { label: "Entre 19% et 25%", color: "#fed988", min: 19, max: 25 },
  { label: "Entre 25% et 37%", color: "#d7ee8e", min: 25, max: 37 },
  { label: "Entre 37% et 50%", color: "#afdd73", min: 37, max: 50 },
  { label: "Entre 50% et 62%", color: "#7fc866", min: 50, max: 62 },
  { label: "Entre 62% et 75%", color: "#48ae5b", min: 62, max: 75 },
  { label: "Entre 75% et 87%", color: "#198d4a", min: 75, max: 87 },
  { label: "Entre 87% et 100%", color: "#006837", min: 87, max: 100 }
]

export const toColorMap = (classes: BiosphereClass[]) => [
  NO_DATA_COLOR,
  ...classes.flatMap((c) => [c.min, c.color])
]

export const biosphereColor = (indice: number, classes: BiosphereClass[]): string =>
  classes.filter((c) => indice >= c.min).at(-1)?.color ?? NO_DATA_COLOR

export const BIOSPHERE_INTEGRITY_ALL_RANGES: Record<string, [number, number]> = Object.fromEntries(
  [...BIOSPHERE_CLASSES, ...BIOSPHERE_DETAIL_CLASSES].map((c) => [c.label, [c.min, c.max]])
)

const isInside = (child: BiosphereClass, parent: BiosphereClass) =>
  child.min >= parent.min && child.max <= parent.max

export const toDetailFilters = (values: (number | string)[]): (number | string)[] =>
  values.flatMap((value) => {
    const parent = BIOSPHERE_CLASSES.find((c) => c.label === value)
    return parent
      ? BIOSPHERE_DETAIL_CLASSES.filter((c) => isInside(c, parent)).map((c) => c.label)
      : [value]
  })

export const toCoarseFilters = (values: (number | string)[]): (number | string)[] => [
  ...new Set(
    values.map((value) => {
      const child = BIOSPHERE_DETAIL_CLASSES.find((c) => c.label === value)
      return child ? BIOSPHERE_CLASSES.find((c) => isInside(child, c))!.label : value
    })
  )
]
