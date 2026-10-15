import type { Map } from "maplibre-gl"
import type { DataType } from "@/utils/enum"

export const EXPORT_WIDTH_PX = 1600
export const EXPORT_HEIGHT_PX = 1100

const CSS_DPI = 96
const OVERLAY_MARGIN_PX = 24
const CHIP_FONT_SIZE_PX = 20
const CHIP_PADDING_X_PX = 22
const CHIP_HEIGHT_PX = 44

export const buildExportFileName = (dataType: DataType, lat: number, lng: number, zoom: number) =>
  `iarbre_${dataType}_${lat.toFixed(5)}_${lng.toFixed(5)}_z${Math.round(zoom)}`

export const renderMapCanvas = async (map: Map): Promise<HTMLCanvasElement> => {
  const [{ MapGenerator, Format, Unit }] = await Promise.all([
    import("@watergis/maplibre-gl-export"),
    import("@watergis/maplibre-gl-export/dist/maplibre-gl-export.css")
  ])
  const generator = new MapGenerator(map, {
    size: [EXPORT_WIDTH_PX / CSS_DPI, EXPORT_HEIGHT_PX / CSS_DPI],
    unit: Unit.in,
    dpi: CSS_DPI,
    format: Format.PNG,
    download: false,
    northIconOptions: { visibility: "none" },
    scalebarOptions: { position: "bottom-right" },
    attributionOptions: { position: "bottom-right" }
  })
  return generator.toCanvas()
}

const readThemeToken = (name: string, fallback: string) =>
  getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback

export const drawTitleChip = (ctx: CanvasRenderingContext2D, label: string) => {
  const text = label.toUpperCase()
  ctx.save()
  ctx.font = `600 ${CHIP_FONT_SIZE_PX}px ${readThemeToken("--font-sans", "sans-serif")}`
  ctx.letterSpacing = "1.5px"
  const width = ctx.measureText(text).width + 2 * CHIP_PADDING_X_PX
  ctx.fillStyle = "rgba(255, 255, 255, 0.92)"
  ctx.beginPath()
  ctx.roundRect(OVERLAY_MARGIN_PX, OVERLAY_MARGIN_PX, width, CHIP_HEIGHT_PX, CHIP_HEIGHT_PX / 2)
  ctx.fill()
  ctx.fillStyle = readThemeToken("--color-primary-900", "black")
  ctx.textBaseline = "middle"
  ctx.fillText(text, OVERLAY_MARGIN_PX + CHIP_PADDING_X_PX, OVERLAY_MARGIN_PX + CHIP_HEIGHT_PX / 2)
  ctx.restore()
}

export const drawLegend = async (ctx: CanvasRenderingContext2D, legendElement: HTMLElement) => {
  const { toCanvas } = await import("html-to-image")
  const legend = await toCanvas(legendElement, { pixelRatio: 1 })
  if (legend.width === 0 || legend.height === 0) return
  ctx.drawImage(legend, OVERLAY_MARGIN_PX, ctx.canvas.height - legend.height - OVERLAY_MARGIN_PX)
}

export const generateMapExport = async (
  map: Map,
  label: string,
  legendElement: HTMLElement | null
): Promise<Blob> => {
  const canvas = await renderMapCanvas(map)
  const ctx = canvas.getContext("2d")
  if (!ctx) throw new Error("Failed to get 2D context for the export canvas")
  drawTitleChip(ctx, label)
  if (legendElement) await drawLegend(ctx, legendElement)
  return new Promise((resolve, reject) =>
    canvas.toBlob(
      (blob) => (blob ? resolve(blob) : reject(new Error("Failed to encode the PNG"))),
      "image/png"
    )
  )
}
