import { describe, it, expect } from "vitest"
import { buildColorRamp, buildTileUrl } from "@/utils/hourlyRaster"
import { PET_RASTER } from "@/utils/pet"

const PET_LEGEND = PET_RASTER.classes

const TRANSPARENT = "rgba(0,0,0,0)"

const rampStops = (visibleValues: number[] = []) => {
  const [, , , ...flat] = buildColorRamp(PET_LEGEND, visibleValues) as unknown as unknown[]
  const stops: { value: number; color: string }[] = []
  for (let i = 0; i < flat.length; i += 2) {
    stops.push({ value: flat[i] as number, color: flat[i + 1] as string })
  }
  return stops
}

const colorAt = (value: number, visibleValues: number[] = []) => {
  const stops = rampStops(visibleValues)
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

  it("keeps the colour ramp stops strictly ascending", () => {
    const stops = rampStops()
    for (let i = 1; i < stops.length; i++) {
      expect(stops[i].value).toBeGreaterThan(stops[i - 1].value)
    }
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
