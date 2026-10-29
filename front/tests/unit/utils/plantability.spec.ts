import { describe, it, expect } from "vitest"
import { getScoreDistribution } from "@/utils/plantability"

describe("getScoreDistribution", () => {
  it("rebuilds the score distribution from the count properties", () => {
    expect(
      getScoreDistribution({ id: "538400_5733300", indice: 2, count_2: 40, count_6: 23 })
    ).toEqual({ "2": 40, "6": 23 })
  })

  it("ignores count properties of unknown scores", () => {
    expect(getScoreDistribution({ count_0: 3, count_5: 7 })).toEqual({ "0": 3 })
  })

  it("returns undefined when the feature has no counts", () => {
    expect(
      getScoreDistribution({ id: 39524659, indice: 0, source_values: "[2.0]" })
    ).toBeUndefined()
    expect(getScoreDistribution(undefined)).toBeUndefined()
  })
})
