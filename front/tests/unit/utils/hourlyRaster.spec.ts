import { describe, it, expect } from "vitest"
import { buildColorRamp, buildTileUrl, type RasterClass } from "@/utils/hourlyRaster"
import { PET_RASTER } from "@/utils/pet"
import { SHADOW_RASTER } from "@/utils/shadow"

const PET_LEGEND = PET_RASTER.classes
const SHADOW_LEGEND = SHADOW_RASTER.classes
const TERRARIUM_TREE_SHADE = 7 / 256

const TRANSPARENT = "rgba(0,0,0,0)"

const rampStops = (visibleValues: number[] = [], classes: RasterClass[] = PET_LEGEND) => {
  const [, , , ...flat] = buildColorRamp(classes, visibleValues) as unknown as unknown[]
  const stops: { value: number; color: string }[] = []
  for (let i = 0; i < flat.length; i += 2) {
    stops.push({ value: flat[i] as number, color: flat[i + 1] as string })
  }
  return stops
}

const colorAt = (
  value: number,
  visibleValues: number[] = [],
  classes: RasterClass[] = PET_LEGEND
) => {
  const stops = rampStops(visibleValues, classes)
  if (value <= stops[0].value) return stops[0].color
  const index = stops.findIndex((stop) => stop.value >= value)
  if (index === -1) return stops[stops.length - 1].color
  return stops[index - 1].color === stops[index].color ? stops[index].color : "blend"
}

describe("hourlyRaster", () => {
  it("requests the tiles of the selected year and hour", () => {
    expect(buildTileUrl("https://x/api", PET_RASTER, 7, 2020)).toBe(
      "https://x/api/tiles/pet/{z}/{x}/{y}.png?year=2020&hour=7"
    )
  })

  it("requests the shadow tiles of the selected hour without year", () => {
    expect(buildTileUrl("https://x/api", SHADOW_RASTER, 7, 2020)).toBe(
      "https://x/api/tiles/shadow/{z}/{x}/{y}.png?hour=7"
    )
  })

  it.each([
    { name: "PET", classes: PET_LEGEND },
    { name: "shadow", classes: SHADOW_LEGEND }
  ])("keeps the $name colour ramp stops strictly ascending", ({ classes }) => {
    const stops = rampStops([], classes)
    for (let i = 1; i < stops.length; i++) {
      expect(stops[i].value).toBeGreaterThan(stops[i - 1].value)
    }
  })

  it("paints the terrarium-decoded shadow values with their legend colour and the sun transparent", () => {
    expect([0, TERRARIUM_TREE_SHADE].map((value) => colorAt(value, [], SHADOW_LEGEND))).toEqual(
      SHADOW_LEGEND.map(({ color }) => color)
    )
    expect(colorAt(1, [], SHADOW_LEGEND)).toBe(TRANSPARENT)
    expect(colorAt(-1, [], SHADOW_LEGEND)).toBe(TRANSPARENT)
  })

  it("paints each PET class with its legend colour and the rest transparent", () => {
    expect(PET_LEGEND.map(({ value }) => colorAt(value))).toEqual(
      PET_LEGEND.map(({ color }) => color)
    )
    expect(colorAt(-1)).toBe(TRANSPARENT)
    expect(colorAt(3)).toBe(TRANSPARENT)
    expect(colorAt(10)).toBe(TRANSPARENT)
  })

  it("hides the PET classes not selected in the legend", () => {
    expect(PET_LEGEND.map(({ value }) => colorAt(value, [5, 8]))).toEqual(
      PET_LEGEND.map(({ value, color }) => ([5, 8].includes(value) ? color : TRANSPARENT))
    )
  })
})
