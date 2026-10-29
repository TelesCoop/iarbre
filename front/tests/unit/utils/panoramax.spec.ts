import { describe, it, expect } from "vitest"
import { buildPanoramaxPictureUrl, formatPanoramaxDate } from "@/utils/panoramax"
import type { PanoramaxPicture } from "maplibre-gl-panoramax"

const picture = (assets: PanoramaxPicture["assets"]): PanoramaxPicture =>
  ({ id: "9d278906-9012-4624-875b-03df1df2c622", assets }) as PanoramaxPicture

describe("buildPanoramaxPictureUrl", () => {
  it("points at the instance serving the picture, not the federated catalog", () => {
    expect(
      buildPanoramaxPictureUrl(
        picture({
          sd: "https://panoramax.ign.fr/api/pictures/9d278906-9012-4624-875b-03df1df2c622/sd.jpg"
        })
      )
    ).toBe("https://panoramax.ign.fr/#focus=pic&pic=9d278906-9012-4624-875b-03df1df2c622")
  })

  it("falls back to another asset when the sd derivate is missing", () => {
    expect(
      buildPanoramaxPictureUrl(picture({ thumb: "https://panoramax.openstreetmap.fr/api/x.jpg" }))
    ).toBe("https://panoramax.openstreetmap.fr/#focus=pic&pic=9d278906-9012-4624-875b-03df1df2c622")
  })

  it("returns null when no asset gives away the instance", () => {
    expect(buildPanoramaxPictureUrl(picture({}))).toBeNull()
  })
})

describe("formatPanoramaxDate", () => {
  it("formats an API datetime in French", () => {
    expect(formatPanoramaxDate("2024-03-12T07:59:25+00:00")).toBe("12 mars 2024")
  })

  it("returns an empty string for a missing or unparsable date", () => {
    expect(formatPanoramaxDate(undefined)).toBe("")
    expect(formatPanoramaxDate("not-a-date")).toBe("")
  })
})
