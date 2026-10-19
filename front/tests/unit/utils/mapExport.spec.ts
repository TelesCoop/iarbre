import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import type { Map } from "maplibre-gl"
import { DataType } from "@/utils/enum"
import {
  ExportFormat,
  MAX_EXPORT_SIDE_PX,
  MIN_EXPORT_SIDE_PX,
  buildExportFileName,
  drawTitleChip,
  encodeMapExport,
  fitExportSize,
  getExportSizeBounds,
  getViewportExportSize,
  renderMapCanvas
} from "@/utils/mapExport"

const generatorConfig = vi.hoisted(() => ({ value: undefined as unknown }))
const generatorInstance = vi.hoisted(() => ({
  value: undefined as unknown as { renderMapPost: (map: Map) => Map }
}))
const toCanvasMock = vi.hoisted(() => vi.fn())

vi.mock("@watergis/maplibre-gl-export", () => ({
  Format: { PNG: "png" },
  Unit: { in: "in" },
  MapGenerator: class {
    constructor(_map: unknown, config: unknown) {
      generatorConfig.value = config
      generatorInstance.value = this as never
    }
    renderMapPost(map: unknown) {
      return map
    }
    toCanvas = toCanvasMock
  }
}))

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

describe("fitExportSize", () => {
  const frame = { width: 1200, height: 600 }
  const fallback = { width: 2400, height: 1200 }

  it("derives the other side from the viewport ratio", () => {
    expect(fitExportSize(frame, "width", 1800, fallback)).toEqual({ width: 1800, height: 900 })
    expect(fitExportSize(frame, "height", 300, fallback)).toEqual({ width: 600, height: 300 })
  })

  it("bounds both sides while keeping the ratio, and keeps the current size when emptied", () => {
    expect(fitExportSize(frame, "width", 100000, fallback)).toEqual({
      width: MAX_EXPORT_SIDE_PX,
      height: MAX_EXPORT_SIDE_PX / 2
    })
    expect(fitExportSize(frame, "width", 10, fallback)).toEqual({
      width: 2 * MIN_EXPORT_SIDE_PX,
      height: MIN_EXPORT_SIDE_PX
    })
    expect(fitExportSize(frame, "width", Number.NaN, fallback)).toBe(fallback)
  })

  it("exposes the per-side bounds", () => {
    expect(getExportSizeBounds(frame)).toEqual({
      min: { width: 400, height: 200 },
      max: { width: 4096, height: 2048 }
    })
  })
})

describe("renderMapCanvas", () => {
  beforeEach(() => {
    toCanvasMock.mockReset()
  })

  it("renders a portrait export at the requested pixels without downloading it", async () => {
    const canvas = document.createElement("canvas")
    toCanvasMock.mockResolvedValue(canvas)

    await expect(
      renderMapCanvas({} as Map, { width: 1080, height: 1920 }, { width: 540, height: 960 })
    ).resolves.toBe(canvas)

    const config = generatorConfig.value as {
      size: [number, number]
      dpi: number
      download: boolean
    }
    expect(config.download).toBe(false)
    expect(config.size.map((inches) => Math.round(inches * config.dpi))).toEqual([1080, 1920])
  })

  it.each([
    [{ width: 2400, height: 1400 }, 192],
    [{ width: 600, height: 350 }, 48]
  ])("keeps the viewport frame and only changes the pixel density", async (size, dpi) => {
    toCanvasMock.mockResolvedValue(document.createElement("canvas"))
    await renderMapCanvas({} as Map, size, { width: 1200, height: 700 })
    const config = generatorConfig.value as { size: [number, number]; dpi: number }

    expect(config.size).toEqual([1200 / 96, 700 / 96])
    expect(config.dpi).toBe(dpi)
  })

  it("repaints the hidden map once loaded so that its idle event fires", async () => {
    toCanvasMock.mockResolvedValue(document.createElement("canvas"))
    await renderMapCanvas({} as Map, { width: 1200, height: 700 }, { width: 1200, height: 700 })
    const renderMap = { triggerRepaint: vi.fn() } as unknown as Map

    expect(generatorInstance.value.renderMapPost(renderMap)).toBe(renderMap)
    expect(renderMap.triggerRepaint).toHaveBeenCalledOnce()
  })
})

describe("getViewportExportSize", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("matches the visible map at the screen pixel density", () => {
    vi.stubGlobal("devicePixelRatio", 1.5)
    expect(getViewportExportSize({ width: 1200, height: 700 })).toEqual({
      width: 1800,
      height: 1050
    })
  })

  it("caps the definition of high density screens while keeping the ratio", () => {
    vi.stubGlobal("devicePixelRatio", 2)
    expect(getViewportExportSize({ width: 1600, height: 900 })).toEqual({
      width: 2048,
      height: 1152
    })
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
    [ExportFormat.PNG, "image/png"],
    [ExportFormat.JPEG, "image/jpeg"]
  ])("encodes the canvas as %s", async (format, mimeType) => {
    const canvas = document.createElement("canvas")
    const blob = new Blob([], { type: mimeType })
    const toBlob = vi
      .spyOn(canvas, "toBlob")
      .mockImplementation((callback: BlobCallback) => callback(blob))

    await expect(encodeMapExport(canvas, format)).resolves.toBe(blob)
    expect(toBlob).toHaveBeenCalledWith(expect.any(Function), mimeType, 0.92)
  })
})
