export const IPAVE_ZONE_COLOR: Record<string | number, string> = {
  "herbacee": "#ffccaa",
  "arbustif": "#648525",
  "arborescent": "#006a00"
}

export const IPAVE_ZONES = Object.keys(IPAVE_ZONE_COLOR) as string[]

export const IPAVE_COLOR_MAP = [
  "herbacee",
  IPAVE_ZONE_COLOR["herbacee"],
  "arbustif",
  IPAVE_ZONE_COLOR["arbustif"],
  "arborescent",
  IPAVE_ZONE_COLOR["arborescent"],
]

const strateDescription: Record<string | number, string> = {
  "herbacee": "Strate herbacée",
  "arbustif": "Strate arbustive < 1.5m",
  "arborescent": "Strate arborée > 1.5m"
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
