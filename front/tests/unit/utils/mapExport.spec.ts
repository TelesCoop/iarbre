import { describe, it, expect, vi, beforeEach } from "vitest"
import type { Map } from "maplibre-gl"
import { DataType } from "@/utils/enum"
import {
  EXPORT_HEIGHT_PX,
  EXPORT_WIDTH_PX,
  buildExportFileName,
  drawTitleChip,
  renderMapCanvas
} from "@/utils/mapExport"

const generatorConfig = vi.hoisted(() => ({ value: undefined as unknown }))
const toCanvasMock = vi.hoisted(() => vi.fn())

vi.mock("@watergis/maplibre-gl-export", () => ({
  Format: { PNG: "png" },
  Unit: { in: "in" },
  MapGenerator: class {
    constructor(_map: unknown, config: unknown) {
      generatorConfig.value = config
    }
    toCanvas = toCanvasMock
  }
}))
vi.mock("@watergis/maplibre-gl-export/dist/maplibre-gl-export.css", () => ({}))

const createContextMock = () =>
  ({
    save: vi.fn(),
    restore: vi.fn(),
    beginPath: vi.fn(),
    roundRect: vi.fn(),
    fill: vi.fn(),
    fillText: vi.fn(),
    measureText: vi.fn(() => ({ width: 100 }))
  }) as unknown as CanvasRenderingContext2D

describe("buildExportFileName", () => {
  it("encodes the data type, the center and the rounded zoom", () => {
    expect(buildExportFileName(DataType.PLANTABILITY, 45.757734, 4.853771, 14.4)).toBe(
      "iarbre_plantability_45.75773_4.85377_z14"
    )
  })
})

describe("renderMapCanvas", () => {
  beforeEach(() => {
    toCanvasMock.mockReset()
  })

  it("renders the map at the export size without downloading it", async () => {
    const canvas = document.createElement("canvas")
    toCanvasMock.mockResolvedValue(canvas)

    await expect(renderMapCanvas({} as Map)).resolves.toBe(canvas)

    const config = generatorConfig.value as {
      size: [number, number]
      dpi: number
      download: boolean
    }
    expect(config.download).toBe(false)
    expect(config.size.map((inches) => inches * config.dpi)).toEqual([
      EXPORT_WIDTH_PX,
      EXPORT_HEIGHT_PX
    ])
  })
})

describe("drawTitleChip", () => {
  it("writes the layer label in upper case on a rounded chip", () => {
    const ctx = createContextMock()

    drawTitleChip(ctx, "Plantabilité et chaleur")

    expect(ctx.roundRect).toHaveBeenCalledWith(24, 24, 144, 44, 22)
    expect(ctx.fillText).toHaveBeenCalledWith("PLANTABILITÉ ET CHALEUR", 46, 46)
  })
})
