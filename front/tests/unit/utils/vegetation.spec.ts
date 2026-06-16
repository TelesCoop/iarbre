import { describe, it, expect } from "vitest"
import {
  sqrtPos,
  getZoneDesc,
  getZoneColor,
  ELEVATION_BINS,
  ELEVATION_LABEL_STOPS
} from "@/utils/vegetation"

describe("sqrtPos", () => {
  it("returns 0 for 0", () => {
    expect(sqrtPos(0)).toBe(0)
  })

  it("returns 100 for max value (40)", () => {
    expect(sqrtPos(40)).toBe(100)
  })

  it("is monotonically increasing", () => {
    const positions = [0, 1, 4, 10, 20, 40].map(sqrtPos)
    for (let i = 1; i < positions.length; i++) {
      expect(positions[i]).toBeGreaterThan(positions[i - 1])
    }
  })

  it("10m (quarter of max) maps to 50% on a sqrt scale", () => {
    expect(sqrtPos(10)).toBe(50)
  })
})

describe("ELEVATION_BINS", () => {
  it("starts at 0", () => {
    expect(ELEVATION_BINS[0].min).toBe(0)
  })

  it("bins are in ascending order", () => {
    for (let i = 1; i < ELEVATION_BINS.length; i++) {
      expect(ELEVATION_BINS[i].min).toBeGreaterThan(ELEVATION_BINS[i - 1].min)
    }
  })
})

describe("ELEVATION_LABEL_STOPS", () => {
  it("first stop is at position 0", () => {
    expect(ELEVATION_LABEL_STOPS[0].position).toBe(0)
  })

  it("last stop is at position 100", () => {
    expect(ELEVATION_LABEL_STOPS[ELEVATION_LABEL_STOPS.length - 1].position).toBe(100)
  })
})

describe("getZoneDesc", () => {
  it.each([
    ["herbacee", "Strate herbacée"],
    ["arbustif", "Strate arbustive < 1.5m"],
    ["arborescent", "Strate arborée > 1.5m"]
  ])("%s returns correct label", (zone, label) => {
    expect(getZoneDesc(zone)).toBe(label)
  })

  it("returns fallback for unknown zone", () => {
    expect(getZoneDesc("unknown")).toBe("Description de strate non possible")
  })
})

describe("getZoneColor", () => {
  it("returns a hex color for known strates", () => {
    expect(getZoneColor("herbacee")).toMatch(/^#[0-9A-Fa-f]{6}$/)
  })

  it("returns fallback color for unknown zone", () => {
    expect(getZoneColor("unknown")).toBe("#CCCCCC")
  })
})
