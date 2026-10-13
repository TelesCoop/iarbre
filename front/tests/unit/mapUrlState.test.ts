import { describe, expect, it } from "vitest"
import { buildMapDisplayQuery, parseMapDisplayState } from "@/utils/mapUrlState"
import { DataType } from "@/utils/enum"
import { DEFAULT_MAP_STYLE } from "@/utils/constants"

describe("biosphere filters in URL", () => {
  it("writes labels as ranges", () => {
    expect(
      buildMapDisplayQuery({
        filters: ["Entre 0% et 12%", "Entre 87% et 100%"],
        mapStyle: DEFAULT_MAP_STYLE,
        overlayLayers: []
      })
    ).toEqual({ filters: "0-12,87-100" })
  })

  it("reads ranges and legacy labels", () => {
    expect(
      parseMapDisplayState(
        { filters: "0-12,Entre 87% et 100%" },
        DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY
      ).filters
    ).toEqual(["Entre 0% et 12%", "Entre 87% et 100%"])
  })
})
