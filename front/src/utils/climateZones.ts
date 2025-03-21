export const zoneDescriptions: Record<string, string> = {
  "1": "Ensemble compact de tours",
  "2": "Ensemble compact d'immeubles",
  "3": "Ensemble compact de maisons",
  "4": "Ensemble de tours espacées",
  "5": "Ensemble d'immeubles espacés",
  "6": "Ensemble de maisons espacées",
  "7": "Ensemble dense de constructions légères",
  "8": "Bâtiments bas de grande emprise",
  "9": "Implantation diffuse de maisons",
  A: "Espace densément arboré",
  B: "Ensemble arboré clairsemé",
  C: "Espace végétalisé hétérogène",
  D: "Végétation basse",
  E: "Sol imperméable naturel ou artificiel",
  F: "Sol nu perméable",
  G: "Surface en eau"
}

export const zoneColors: Record<string, string> = {
  "1": "#8C0000",
  "2": "#D10000",
  "3": "#FF0000",
  "4": "#BF4D00",
  "5": "#fa6600",
  "6": "#ff9955",
  "7": "#faee05",
  "8": "#bcbcbc",
  "9": "#ffccaa",
  A: "#006a00",
  B: "#00aa00",
  C: "#648525",
  D: "#b9db79",
  E: "#000000",
  F: "#FBF7AE",
  G: "#6A6AFF"
}

export function getZoneDesc(zone: string): string {
  return zoneDescriptions[zone] || "Description non disponible"
}

export function getZoneColor(zone: string): string {
  return zoneColors[zone] || "#CCCCCC"
}
