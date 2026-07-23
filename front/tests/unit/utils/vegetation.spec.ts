import { describe, it, expect } from "vitest"
import {
  sqrtPos,
  ELEVATION_BINS,
  ELEVATION_LABEL_STOPS,
  buildElevationColorRamp,
  normalizeHeightRanges,
  formatHeightRange,
  elevationColorAt,
  heightRangeColor
} from "@/utils/vegetation"

const rampStops = (ranges: Parameters<typeof buildElevationColorRamp>[0]) => {
  const [, , , ...flat] = buildElevationColorRamp(ranges) as unknown as unknown[]
  const stops: { height: number; color: string }[] = []
  for (let i = 0; i < flat.length; i += 2) {
    stops.push({ height: flat[i] as number, color: flat[i + 1] as string })
  }
  return stops
}

const TRANSPARENT = "rgba(0,0,0,0)"

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

describe("normalizeHeightRanges", () => {
  it("drops invalid ranges", () => {
    expect(normalizeHeightRanges([{ min: -1, max: 5 }])).toEqual([])
    expect(normalizeHeightRanges([{ min: 5, max: 2 }])).toEqual([])
    expect(normalizeHeightRanges([{ min: 3, max: 3 }])).toEqual([])
  })

  it("sorts and merges overlapping ranges", () => {
    expect(
      normalizeHeightRanges([
        { min: 15, max: null },
        { min: 2, max: 5 },
        { min: 4, max: 7 }
      ])
    ).toEqual([
      { min: 2, max: 7 },
      { min: 15, max: null }
    ])
  })

  it("does not mutate the given ranges", () => {
    const ranges = [
      { min: 2, max: 5 },
      { min: 4, max: 7 }
    ]
    normalizeHeightRanges(ranges)
    expect(ranges[0].max).toBe(5)
  })

  it("swallows ranges following an open-ended one", () => {
    expect(
      normalizeHeightRanges([
        { min: 10, max: null },
        { min: 20, max: 30 }
      ])
    ).toEqual([{ min: 10, max: null }])
  })
})

describe("formatHeightRange", () => {
  it("formats bounded and open-ended ranges", () => {
    expect(formatHeightRange({ min: 2, max: 5 })).toBe("2 - 5 m")
    expect(formatHeightRange({ min: 15, max: null })).toBe("> 15 m")
  })
})

describe("elevationColorAt", () => {
  it("returns the color of the bin containing the height", () => {
    expect(elevationColorAt(0)).toBe(ELEVATION_BINS[0].color)
    expect(elevationColorAt(3.5)).toBe("#e1daa6")
    expect(elevationColorAt(100)).toBe(ELEVATION_BINS[ELEVATION_BINS.length - 1].color)
  })
})

describe("heightRangeColor", () => {
  it("colors a bounded range by its midpoint and an open-ended one by its min", () => {
    expect(heightRangeColor({ min: 2, max: 6 })).toBe(elevationColorAt(4))
    expect(heightRangeColor({ min: 15, max: null })).toBe(elevationColorAt(15))
  })
})

describe("buildElevationColorRamp", () => {
  it("is an interpolate expression driven by elevation", () => {
    const ramp = buildElevationColorRamp([]) as unknown as unknown[]
    expect(ramp[0]).toBe("interpolate")
    expect(ramp[1]).toEqual(["linear"])
    expect(ramp[2]).toEqual(["elevation"])
  })

  it("keeps stops strictly ascending", () => {
    const stops = rampStops([
      { min: 15, max: null },
      { min: 2, max: 5 }
    ])
    for (let i = 1; i < stops.length; i++) {
      expect(stops[i].height).toBeGreaterThan(stops[i - 1].height)
    }
  })

  it("renders nodata and below-ground values transparent", () => {
    const stops = rampStops([{ min: 2, max: 5 }])
    expect(stops[0]).toEqual({ height: -1, color: TRANSPARENT })
    expect(stops[1].color).toBe(TRANSPARENT)
  })

  it("falls back to the continuous gradient when no range is given", () => {
    const colors = new Set(rampStops([]).map((stop) => stop.color))
    ELEVATION_BINS.forEach((bin) => expect(colors.has(bin.color)).toBe(true))
  })

  it("hides everything outside the requested ranges", () => {
    const stops = rampStops([
      { min: 2, max: 5 },
      { min: 15, max: null }
    ])
    const colorAt = (height: number) => stops.filter((stop) => stop.height <= height).pop()!.color

    expect(colorAt(1)).toBe(TRANSPARENT)
    expect(colorAt(3)).not.toBe(TRANSPARENT)
    expect(colorAt(10)).toBe(TRANSPARENT)
    expect(colorAt(30)).not.toBe(TRANSPARENT)
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
