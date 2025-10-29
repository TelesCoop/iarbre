export const IPAVE_ZONE_COLOR: Record<string | number, string> = {
  herbacee: "#BF5A16",
  arbustif: "#0A3D80",
  arborescent: "#025400"
}

export const IPAVE_ZONES = Object.keys(IPAVE_ZONE_COLOR) as string[]

export const IPAVE_COLOR_MAP = [
  "herbacee",
  IPAVE_ZONE_COLOR["herbacee"],
  "arbustif",
  IPAVE_ZONE_COLOR["arbustif"],
  "arborescent",
  IPAVE_ZONE_COLOR["arborescent"],
  "#CCCCCC" // Default color for unmatched values
]

const strateDescription: Record<string | number, string> = {
  herbacee: "Strate herbacée",
  arbustif: "Strate arbustive < 1.5m",
  arborescent: "Strate arborée > 1.5m"
}

export function getZoneDesc(zone: string | number): string {
  if (!(zone in strateDescription)) {
    console.error(`Strate inconnue : "${zone}"`)
    return "Description de strate non possible"
  }
  return strateDescription[zone]
}

export function getZoneColor(zone: string | number): string {
  if (!(zone in IPAVE_ZONE_COLOR)) {
    console.error(`Strate inconnue : "${zone}"`)
    return "#CCCCCC"
  }
  return IPAVE_ZONE_COLOR[zone]
}
