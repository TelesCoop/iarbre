import { describe, it, expect } from "vitest"
import { computePolygonAreaM2, formatArea } from "@/utils/geo"

describe("computePolygonAreaM2", () => {
  it("returns 0 for a ring with fewer than 3 points", () => {
    expect(
      computePolygonAreaM2([
        [0, 0],
        [0.001, 0]
      ])
    ).toBe(0)
  })

  it("computes the area of a ~111m square near the equator", () => {
    const ring: number[][] = [
      [0, 0],
      [0.001, 0],
      [0.001, 0.001],
      [0, 0.001],
      [0, 0]
    ]
    const area = computePolygonAreaM2(ring)
    expect(area).toBeGreaterThan(12000)
    expect(area).toBeLessThan(12800)
  })

  it("is independent of winding order (absolute value)", () => {
    const cw: number[][] = [
      [0, 0],
      [0.001, 0],
      [0.001, 0.001],
      [0, 0.001]
    ]
    const ccw = [...cw].reverse()
    expect(computePolygonAreaM2(cw)).toBeCloseTo(computePolygonAreaM2(ccw), 3)
  })
})

describe("formatArea", () => {
  it("formats values under 1 ha in m²", () => {
    expect(formatArea(8500)).toBe("8 500 m²")
  })

  it("formats values at or above the threshold in km² with two decimals", () => {
    expect(formatArea(12392)).toBe("0,01 km²")
    expect(formatArea(850000)).toBe("0,85 km²")
  })

  it("switches to km² at the threshold, stays in m² just below", () => {
    expect(formatArea(10000).endsWith("km²")).toBe(true)
    expect(formatArea(9999).endsWith("m²")).toBe(true)
  })
})
