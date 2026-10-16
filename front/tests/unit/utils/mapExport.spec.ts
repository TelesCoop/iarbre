import { describe, it, expect, vi, beforeEach } from "vitest"
import type { Map } from "maplibre-gl"
import { DataType } from "@/utils/enum"
import {
  DEFAULT_EXPORT_SIZE,
  ExportFormat,
  MAX_EXPORT_SIDE_PX,
  MIN_EXPORT_SIDE_PX,
  buildExportFileName,
  clampExportSide,
  drawTitleChip,
  encodeMapExport,
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
    scale: vi.fn(),
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

describe("clampExportSide", () => {
  it("rounds and bounds the typed side, keeping the current value when emptied", () => {
    expect(clampExportSide(1234.6, 1600)).toBe(1235)
    expect(clampExportSide(10, 1600)).toBe(MIN_EXPORT_SIDE_PX)
    expect(clampExportSide(100000, 1600)).toBe(MAX_EXPORT_SIDE_PX)
    expect(clampExportSide(Number.NaN, 1600)).toBe(1600)
  })
})

describe("renderMapCanvas", () => {
  beforeEach(() => {
    toCanvasMock.mockReset()
  })

  it("renders a portrait export at the requested pixels without downloading it", async () => {
    const canvas = document.createElement("canvas")
    toCanvasMock.mockResolvedValue(canvas)

    await expect(renderMapCanvas({} as Map, { width: 1080, height: 1920 })).resolves.toBe(canvas)

    const config = generatorConfig.value as {
      size: [number, number]
      dpi: number
      download: boolean
    }
    expect(config.download).toBe(false)
    expect(config.size.map((inches) => Math.round(inches * config.dpi))).toEqual([1080, 1920])
  })

  it("keeps the default frame and raises the pixel density for larger exports", async () => {
    toCanvasMock.mockResolvedValue(document.createElement("canvas"))
    await renderMapCanvas({} as Map, DEFAULT_EXPORT_SIZE)
    const defaultSize = (generatorConfig.value as { size: [number, number] }).size
    await renderMapCanvas({} as Map, { width: 3200, height: 2200 })
    const config = generatorConfig.value as { size: [number, number]; dpi: number }

    expect(config.size).toEqual(defaultSize)
    expect(config.dpi).toBe(192)
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

describe("encodeMapExport", () => {
  it.each([
    [ExportFormat.PNG, "image/png", undefined],
    [ExportFormat.JPEG, "image/jpeg", 0.92]
  ])("encodes the canvas as %s", async (format, mimeType, quality) => {
    const canvas = document.createElement("canvas")
    const blob = new Blob([], { type: mimeType })
    const toBlob = vi
      .spyOn(canvas, "toBlob")
      .mockImplementation((callback: BlobCallback) => callback(blob))

    await expect(encodeMapExport(canvas, format)).resolves.toBe(blob)
    expect(toBlob).toHaveBeenCalledWith(expect.any(Function), mimeType, quality)
  })
})
