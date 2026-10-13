import { describe, it, expect } from "vitest"
import {
  BIOSPHERE_CLASSES,
  BIOSPHERE_DETAIL_CLASSES,
  biosphereColor,
  toColorMap,
  toDetailFilters,
  toCoarseFilters
} from "@/utils/biosphere_functional_integrity"

const [CRITICAL, LOW, MID, GOOD, HIGH] = BIOSPHERE_CLASSES.map((c) => c.label)
const DETAIL = BIOSPHERE_DETAIL_CLASSES.map((c) => c.label)

describe("biosphere filter conversion", () => {
  it("splits a coarse class into its two detail classes", () => {
    expect(toDetailFilters([LOW])).toEqual(["Entre 12% et 19%", "Entre 19% et 25%"])
  })

  it("merges detail classes into their coarse class", () => {
    expect(toCoarseFilters(["Entre 12% et 19%", "Entre 19% et 25%", "Entre 87% et 100%"])).toEqual([
      LOW,
      HIGH
    ])
  })

  it("round-trips coarse filters", () => {
    expect(toCoarseFilters(toDetailFilters([CRITICAL, GOOD]))).toEqual([CRITICAL, GOOD])
  })

  it("leaves already converted values untouched", () => {
    expect(toDetailFilters([DETAIL[4]])).toEqual([DETAIL[4]])
    expect(toCoarseFilters([MID])).toEqual([MID])
  })
})

describe("biosphere colors", () => {
  it("builds a maplibre step color map", () => {
    expect(toColorMap(BIOSPHERE_CLASSES)).toEqual([
      "#d4d4d4",
      0,
      "#d73026",
      12,
      "#BF5A16",
      25,
      "#A6CC4A",
      50,
      "#55B250",
      75,
      "#025400"
    ])
  })

  it("picks the class color with lower bound inclusive", () => {
    expect(biosphereColor(0, BIOSPHERE_CLASSES)).toBe("#d73026")
    expect(biosphereColor(25, BIOSPHERE_CLASSES)).toBe("#A6CC4A")
    expect(biosphereColor(24, BIOSPHERE_DETAIL_CLASSES)).toBe("#B68228")
    expect(biosphereColor(100, BIOSPHERE_DETAIL_CLASSES)).toBe("#024500")
    expect(biosphereColor(-1, BIOSPHERE_CLASSES)).toBe("#d4d4d4")
  })
})
