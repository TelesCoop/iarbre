import { readFileSync } from "node:fs"
import { join } from "node:path"
import { describe, it, expect } from "vitest"

const STYLESHEETS = ["main.css", "maplibre.css"]
const HOVER_MEDIA_QUERY = "@media (hover: hover)"

/** Selectors of the `:hover` rules that are not nested in a hover-capable media query. */
const findUnguardedHoverSelectors = (css: string): string[] => {
  const openBlocks: string[] = []
  const unguarded: string[] = []
  let header = ""

  for (const char of css.replace(/\/\*[\s\S]*?\*\//g, "")) {
    if (char === "{") {
      const selector = header.trim()
      if (selector.includes(":hover") && !openBlocks.includes(HOVER_MEDIA_QUERY)) {
        unguarded.push(selector)
      }
      openBlocks.push(selector)
      header = ""
    } else if (char === "}") {
      openBlocks.pop()
      header = ""
    } else if (char === ";") {
      header = ""
    } else {
      header += char
    }
  }
  return unguarded
}

describe("hover styles", () => {
  // Touch screens keep `:hover` after a tap; outside this media query the hover
  // colours stick and can leave a whitened icon on a white button.
  it.each(STYLESHEETS)("%s scopes every :hover rule to hover-capable devices", (path) => {
    expect(
      findUnguardedHoverSelectors(
        readFileSync(join(import.meta.dirname, "../../../src/styles", path), "utf-8")
      )
    ).toEqual([])
  })
})
