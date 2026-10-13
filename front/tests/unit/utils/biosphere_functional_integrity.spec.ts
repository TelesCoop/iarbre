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
      "#d4322c",
      12,
      "#fdbc6e",
      25,
      "#c4e67f",
      50,
      "#64bc61",
      75,
      "#0b7b41"
    ])
  })

  it("picks the class color with lower bound inclusive", () => {
    expect(biosphereColor(0, BIOSPHERE_CLASSES)).toBe("#d4322c")
    expect(biosphereColor(25, BIOSPHERE_CLASSES)).toBe("#c4e67f")
    expect(biosphereColor(24, BIOSPHERE_DETAIL_CLASSES)).toBe("#fed988")
    expect(biosphereColor(100, BIOSPHERE_DETAIL_CLASSES)).toBe("#006837")
    expect(biosphereColor(-1, BIOSPHERE_CLASSES)).toBe("#d4d4d4")
  })
})
