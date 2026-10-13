import { describe, it, expect } from "vitest"
import {
  BiosphereIntegrityLegendName,
  BiosphereIntegrityDetailLegendName,
  toDetailFilters,
  toCoarseFilters
} from "@/utils/biosphere_functional_integrity"

describe("biosphere filter conversion", () => {
  it("splits a coarse class into its two detail classes", () => {
    expect(toDetailFilters([BiosphereIntegrityLegendName.LOW])).toEqual([
      BiosphereIntegrityDetailLegendName.LOW_1,
      BiosphereIntegrityDetailLegendName.LOW_2
    ])
  })

  it("merges detail classes into their coarse class", () => {
    expect(
      toCoarseFilters([
        BiosphereIntegrityDetailLegendName.LOW_1,
        BiosphereIntegrityDetailLegendName.LOW_2,
        BiosphereIntegrityDetailLegendName.HIGH_2
      ])
    ).toEqual([BiosphereIntegrityLegendName.LOW, BiosphereIntegrityLegendName.HIGH])
  })

  it("round-trips coarse filters", () => {
    const coarse = [BiosphereIntegrityLegendName.CRITICAL, BiosphereIntegrityLegendName.GOOD]
    expect(toCoarseFilters(toDetailFilters(coarse))).toEqual(coarse)
  })

  it("leaves already converted values untouched", () => {
    const detail = [BiosphereIntegrityDetailLegendName.MID_1]
    expect(toDetailFilters(detail)).toEqual(detail)
    const coarse = [BiosphereIntegrityLegendName.MID]
    expect(toCoarseFilters(coarse)).toEqual(coarse)
  })
})
