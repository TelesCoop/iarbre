import { describe, expect, it } from "vitest"
import { decodeZone, encodeZone } from "@/utils/zoneUrl"
import type { ZonePolygon } from "@/stores/zone"

describe("zoneUrl", () => {
  it("round-trips a polygon", () => {
    const zone: ZonePolygon = {
      type: "Polygon",
      coordinates: [
        [
          [4.83512, 45.76012],
          [4.84, 45.76],
          [4.84, 45.77],
          [4.83512, 45.76012]
        ]
      ]
    }
    expect(decodeZone(encodeZone(zone))).toEqual(zone)
  })

  it("rejects malformed input", () => {
    expect(decodeZone("garbage")).toBeNull()
    expect(decodeZone("1,2~3,4")).toBeNull()
    expect(decodeZone("1,2~3,x~5,6~1,2")).toBeNull()
  })
})
