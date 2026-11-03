import { describe, it, expect } from "vitest"
import { buildPetTileUrl } from "@/utils/pet"

describe("pet", () => {
  it("requests the tiles of the selected year and hour", () => {
    expect(buildPetTileUrl("https://x/api", 2020, 7)).toBe(
      "https://x/api/tiles/pet/{z}/{x}/{y}.png?year=2020&hour=7"
    )
  })
})
