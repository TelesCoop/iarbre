import { describe, it, expect } from "vitest"
import { buildColorRamp } from "@/utils/hourlyRaster"
import { PET_RASTER } from "@/utils/pet"
import { DataType } from "@/utils/enum"
import {
  PLANTABILITY_2026_CLASSES,
  PLANTABILITY_2026_GRIDS,
  maxZoomFor,
  plantability2026TileUrl,
  rasterClasses
} from "@/utils/plantability2026"
import { MAX_ZOOM } from "@/utils/constants"

const TRANSPARENT = "rgba(0,0,0,0)"
const NODATA_HEIGHT = -1

const colorAt = (value: number, visibleValues: number[] = []) => {
  const [, , , ...flat] = buildColorRamp(
    PLANTABILITY_2026_CLASSES,
    visibleValues
  ) as unknown as unknown[]
  const stops: { value: number; color: string }[] = []
  for (let i = 0; i < flat.length; i += 2) {
    stops.push({ value: flat[i] as number, color: flat[i + 1] as string })
  }
  if (value <= stops[0].value) return stops[0].color
  const index = stops.findIndex((stop) => stop.value >= value)
  if (index === -1) return stops[stops.length - 1].color
  return stops[index - 1].color === stops[index].color ? stops[index].color : "blend"
}

describe("plantability 2026", () => {
  it("builds the tile url per grid", () => {
    expect(plantability2026TileUrl("http://api", 1)).toBe(
      "http://api/tiles/plantability-2026/{z}/{x}/{y}.png?grid=1"
    )
  })

  it("maps each datatype to its grid", () => {
    expect(PLANTABILITY_2026_GRIDS[DataType.PLANTABILITY_2026_5M]).toBe(5)
    expect(PLANTABILITY_2026_GRIDS[DataType.PLANTABILITY_2026_1M]).toBe(1)
  })

  it("uses production plantability classes and colors", () => {
    expect(PLANTABILITY_2026_CLASSES.map(({ value }) => value)).toEqual([0, 2, 4, 6, 8, 10])
    expect(PLANTABILITY_2026_CLASSES.map(({ color }) => color)).toEqual([
      "#C4C4C4",
      "#BF5A16",
      "#DDAD14",
      "#A6CC4A",
      "#55B250",
      "#025400"
    ])
  })

  it("colors every class when nothing is filtered", () => {
    PLANTABILITY_2026_CLASSES.forEach(({ value, color }) => {
      expect(colorAt(value)).toBe(color)
    })
  })

  it("keeps only filtered classes colored", () => {
    expect(colorAt(6, [6])).toBe("#A6CC4A")
    expect(colorAt(0, [6])).toBe(TRANSPARENT)
    expect(colorAt(10, [6])).toBe(TRANSPARENT)
  })

  it("keeps nodata transparent although class 0 sits next to it", () => {
    expect(colorAt(NODATA_HEIGHT)).toBe(TRANSPARENT)
    expect(colorAt(0)).toBe("#C4C4C4")
  })

  it("returns classes for 2026 and hourly rasters only", () => {
    expect(rasterClasses(DataType.PLANTABILITY_2026_1M)).toBe(PLANTABILITY_2026_CLASSES)
    expect(rasterClasses(DataType.PET)).toBe(PET_RASTER.classes)
    expect(rasterClasses(DataType.PLANTABILITY)).toBeUndefined()
  })

  it("allows zooming to 20 on 2026 layers only", () => {
    expect(maxZoomFor(DataType.PLANTABILITY_2026_1M)).toBe(20)
    expect(maxZoomFor(DataType.PLANTABILITY_2026_5M)).toBe(20)
    expect(maxZoomFor(DataType.PLANTABILITY)).toBe(MAX_ZOOM)
  })
})
