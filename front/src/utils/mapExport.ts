import type { Map } from "maplibre-gl"
import type { DPIType } from "@watergis/maplibre-gl-export"
import type { DataType } from "@/utils/enum"

export interface ExportSize {
  width: number
  height: number
}

export const DEFAULT_EXPORT_SIZE: ExportSize = { width: 1600, height: 1100 }
export const MIN_EXPORT_SIDE_PX = 200
export const MAX_EXPORT_SIDE_PX = 8000

export enum ExportFormat {
  PNG = "png",
  JPEG = "jpg"
}

export const EXPORT_FORMATS: { label: string; value: ExportFormat }[] = [
  { label: "PNG", value: ExportFormat.PNG },
  { label: "JPEG", value: ExportFormat.JPEG }
]

const CSS_DPI = 96
const BASE_FRAME_SIDE_PX = 1600
const JPEG_QUALITY = 0.92
const OVERLAY_MARGIN_PX = 24
const CHIP_FONT_SIZE_PX = 20
const CHIP_PADDING_X_PX = 22
const CHIP_HEIGHT_PX = 44

export const clampExportSide = (value: number, fallback: number) =>
  Number.isFinite(value)
    ? Math.min(MAX_EXPORT_SIDE_PX, Math.max(MIN_EXPORT_SIDE_PX, Math.round(value)))
    : fallback

export const getExportScale = ({ width, height }: ExportSize) =>
  Math.max(1, Math.max(width, height) / BASE_FRAME_SIDE_PX)

export const buildExportFileName = (dataType: DataType, lat: number, lng: number, zoom: number) =>
  `iarbre_${dataType}_${lat.toFixed(5)}_${lng.toFixed(5)}_z${Math.round(zoom)}`

export const renderMapCanvas = async (map: Map, size: ExportSize): Promise<HTMLCanvasElement> => {
  const [{ MapGenerator, Format, Unit }] = await Promise.all([
    import("@watergis/maplibre-gl-export"),
    import("@watergis/maplibre-gl-export/dist/maplibre-gl-export.css")
  ])
  const scale = getExportScale(size)
  const generator = new MapGenerator(map, {
    size: [size.width / scale / CSS_DPI, size.height / scale / CSS_DPI],
    unit: Unit.in,
    dpi: (CSS_DPI * scale) as DPIType,
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

export const drawTitleChip = (ctx: CanvasRenderingContext2D, label: string, scale = 1) => {
  const text = label.toUpperCase()
  ctx.save()
  ctx.scale(scale, scale)
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

export const drawLegend = async (
  ctx: CanvasRenderingContext2D,
  legendElement: HTMLElement,
  scale = 1
) => {
  const { toCanvas } = await import("html-to-image")
  const legend = await toCanvas(legendElement, { pixelRatio: scale })
  if (legend.width === 0 || legend.height === 0) return
  const margin = OVERLAY_MARGIN_PX * scale
  ctx.drawImage(legend, margin, ctx.canvas.height - legend.height - margin)
}

export const generateMapExport = async (
  map: Map,
  label: string,
  legendElement: HTMLElement | null,
  size: ExportSize = DEFAULT_EXPORT_SIZE
): Promise<HTMLCanvasElement> => {
  const canvas = await renderMapCanvas(map, size)
  const ctx = canvas.getContext("2d")
  if (!ctx) throw new Error("Failed to get 2D context for the export canvas")
  const scale = getExportScale(size)
  drawTitleChip(ctx, label, scale)
  if (legendElement) await drawLegend(ctx, legendElement, scale)
  return canvas
}

const canvasToBlob = (canvas: HTMLCanvasElement, type: string, quality?: number) =>
  new Promise<Blob>((resolve, reject) =>
    canvas.toBlob(
      (blob) => (blob ? resolve(blob) : reject(new Error(`Failed to encode the ${type} image`))),
      type,
      quality
    )
  )

export const encodeMapExport = (canvas: HTMLCanvasElement, format: ExportFormat): Promise<Blob> =>
  format === ExportFormat.JPEG
    ? canvasToBlob(canvas, "image/jpeg", JPEG_QUALITY)
    : canvasToBlob(canvas, "image/png")
