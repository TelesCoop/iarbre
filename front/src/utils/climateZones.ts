import { LOCAL_CLIMATE_ZONES } from "@/config/shared"

const zoneDescriptions: Record<string | number, string> = LOCAL_CLIMATE_ZONES

// Color defined by CEREMA in
// https://www.data.gouv.fr/fr/datasets/r/f80e08a4-ecd1-42a2-a8d6-963af16aec75
export const CLIMATE_ZONE_COLOR: Record<string | number, string> = {
  1: "#8C0000",
  2: "#D10000",
  3: "#FF0000",
  4: "#BF4D00",
  5: "#fa6600",
  6: "#ff9955",
  7: "#faee05",
  8: "#bcbcbc",
  9: "#ffccaa",
  A: "#006a00",
  B: "#00aa00",
  C: "#648525",
  D: "#b9db79",
  E: "#000000",
  F: "#FBF7AE",
  G: "#6A6AFF"
}

export const CLIMATE_ZONE_MAP_COLOR_MAP = [
  "1",
  CLIMATE_ZONE_COLOR[1],
  "2",
  CLIMATE_ZONE_COLOR[2],
  "3",
  CLIMATE_ZONE_COLOR[3],
  "4",
  CLIMATE_ZONE_COLOR[4],
  "5",
  CLIMATE_ZONE_COLOR[5],
  "6",
  CLIMATE_ZONE_COLOR[6],
  "7",
  CLIMATE_ZONE_COLOR[7],
  "8",
  CLIMATE_ZONE_COLOR[8],
  "9",
  CLIMATE_ZONE_COLOR[9],
  "A",
  CLIMATE_ZONE_COLOR["A"],
  "B",
  CLIMATE_ZONE_COLOR["B"],
  "C",
  CLIMATE_ZONE_COLOR["C"],
  "D",
  CLIMATE_ZONE_COLOR["D"],
  "E",
  CLIMATE_ZONE_COLOR["E"],
  "F",
  CLIMATE_ZONE_COLOR["F"],
  "G",
  CLIMATE_ZONE_COLOR["G"],
  "#6A6AFF"
]

export function getZoneDesc(zone: string | number): string {
  if (!(zone in zoneDescriptions)) {
    console.error(`Zone inconnue : "${zone}"`)
    return "Description non disponible"
  }
  return zoneDescriptions[zone]
}

export function getZoneColor(zone: string | number): string {
  if (!(zone in CLIMATE_ZONE_COLOR)) {
    console.error(`Zone inconnue : "${zone}"`)
    return "#CCCCCC"
  }
  return CLIMATE_ZONE_COLOR[zone]
}
