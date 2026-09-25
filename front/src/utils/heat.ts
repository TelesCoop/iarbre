export enum HeatMode {
  PET_INDEX = "pet_index",
  SUN_EXPOSURE = "sun_exposure"
}

export const HeatModeToParams: Record<HeatMode, { rasterKey: string; hourly: boolean }> = {
  [HeatMode.PET_INDEX]: { rasterKey: "pet_index", hourly: true },
  [HeatMode.SUN_EXPOSURE]: { rasterKey: "sun_exposure", hourly: false }
}

export const HeatModeToLabel: Record<HeatMode, string> = {
  [HeatMode.PET_INDEX]: "Indice PET - 2023 - 1m - 2090",
  [HeatMode.SUN_EXPOSURE]: "Exposition solaire - 2023 - 1m - 2090"
}

export const HeatModeToDescription: Record<HeatMode, string> = {
  [HeatMode.PET_INDEX]:
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
  [HeatMode.SUN_EXPOSURE]:
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
}

export const HEAT_HOURS = Array.from({ length: 15 }, (_, index) => index + 7)

export const DEFAULT_HEAT_HOUR = 17

export function isHourlyMode(mode: HeatMode): boolean {
  return HeatModeToParams[mode].hourly
}

export function formatHeatHour(hour: number): string {
  return `${hour}h`
}

export function buildHeatTileParams(
  mode: HeatMode,
  hour: number = DEFAULT_HEAT_HOUR
): URLSearchParams {
  const { rasterKey, hourly } = HeatModeToParams[mode]
  return new URLSearchParams(hourly ? { mode: rasterKey, hour: String(hour) } : { mode: rasterKey })
}

export function buildHeatTileUrl(
  baseApiUrl: string,
  mode: HeatMode,
  hour: number = DEFAULT_HEAT_HOUR
): string {
  return `${baseApiUrl}/tiles/heat/{z}/{x}/{y}.png?${buildHeatTileParams(mode, hour)}`
}

export function buildHeatRasterUrl(
  baseApiUrl: string,
  mode: HeatMode,
  hour: number = DEFAULT_HEAT_HOUR
): string {
  const { rasterKey, hourly } = HeatModeToParams[mode]
  const url = `${baseApiUrl}/rasters/${rasterKey}/`
  return hourly ? `${url}?${new URLSearchParams({ hour: String(hour) })}` : url
}

export const PET_INDEX_LEGEND = [
  {
    indice: 5,
    range: "18 - 23 °C",
    perception: "Neutre",
    stress: "Aucun stress thermique",
    color: "#ffffcc"
  },
  {
    indice: 6,
    range: "23 - 29 °C",
    perception: "Légèrement chaud",
    stress: "Léger stress thermique",
    color: "#fed976"
  },
  {
    indice: 7,
    range: "29 - 35 °C",
    perception: "Chaud",
    stress: "Stress thermique modéré",
    color: "#fd8d3c"
  },
  {
    indice: 8,
    range: "35 - 41 °C",
    perception: "Très chaud",
    stress: "Fort stress thermique",
    color: "#e31a1c"
  },
  {
    indice: 9,
    range: "> 41 °C",
    perception: "Extrêmement chaud",
    stress: "Stress thermique extrême",
    color: "#800026"
  }
]

export const SUN_EXPOSURE_LEGEND = [
  { range: "0 - 0,2", color: "#ffffcc" },
  { range: "0,2 - 0,4", color: "#ffeda0" },
  { range: "0,4 - 0,6", color: "#fed976" },
  { range: "0,6 - 0,8", color: "#feb24c" },
  { range: "0,8 - 0,9", color: "#fd8d3c" },
  { range: "> 0,9", color: "#f03b20" }
]
