export interface LegendItem {
  color: string
  label: string
  detail?: string
}

export interface RasterLayer {
  key: string
  label: string
  description: string
  attribution: string
  hourly: boolean
  legend: LegendItem[]
}

export const RASTER_LAYERS: RasterLayer[] = [
  {
    key: "pet_index",
    label: "Indice PET - 2023 - 1m - 2090",
    description:
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    attribution: "Métropole de Lyon",
    hourly: true,
    legend: [
      { color: "#ffffcc", label: "18 - 23 °C - Neutre", detail: "Aucun stress thermique" },
      {
        color: "#fed976",
        label: "23 - 29 °C - Légèrement chaud",
        detail: "Léger stress thermique"
      },
      { color: "#fd8d3c", label: "29 - 35 °C - Chaud", detail: "Stress thermique modéré" },
      { color: "#e31a1c", label: "35 - 41 °C - Très chaud", detail: "Fort stress thermique" },
      {
        color: "#800026",
        label: "> 41 °C - Extrêmement chaud",
        detail: "Stress thermique extrême"
      }
    ]
  },
  {
    key: "sun_exposure",
    label: "Exposition solaire - 2023 - 1m - 2090",
    description:
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    attribution: "Métropole de Lyon",
    hourly: false,
    legend: [
      { color: "#ffffcc", label: "0 - 0,2" },
      { color: "#ffeda0", label: "0,2 - 0,4" },
      { color: "#fed976", label: "0,4 - 0,6" },
      { color: "#feb24c", label: "0,6 - 0,8" },
      { color: "#fd8d3c", label: "0,8 - 0,9" },
      { color: "#f03b20", label: "> 0,9" }
    ]
  }
]

export const DEFAULT_LAYER_KEY = RASTER_LAYERS[0].key

export const HOURS = Array.from({ length: 15 }, (_, index) => index + 7)

export const DEFAULT_HOUR = 18

export const getRasterLayer = (key: string): RasterLayer =>
  RASTER_LAYERS.find((layer) => layer.key === key) ?? RASTER_LAYERS[0]

export const formatHour = (hour: number): string => `${hour}h`

export const buildTileUrl = (baseApiUrl: string, layer: RasterLayer, hour: number): string => {
  const params = new URLSearchParams({ mode: layer.key })
  if (layer.hourly) params.set("hour", String(hour))
  return `${baseApiUrl}/tiles/heat/{z}/{x}/{y}.png?${params}`
}

export const buildRasterUrl = (baseApiUrl: string, layer: RasterLayer, hour?: number): string => {
  const url = `${baseApiUrl}/rasters/${layer.key}/`
  return layer.hourly && hour !== undefined ? `${url}?hour=${hour}` : url
}
