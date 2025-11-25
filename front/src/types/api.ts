/**
 * Types pour les réponses API
 */

export interface BaseScoresResponse {
  datatype: string
  count: number
  irisCodes: string[]
  cityCodes: string[]
}

export interface PlantabilityScoresResponse extends BaseScoresResponse {
  plantabilityNormalizedIndice: number
  plantabilityIndice: number
  distribution: { [key: string]: number }
}

export interface VulnerabilityScoresResponse extends BaseScoresResponse {
  vulnerability_indice_day: number
  vulnerability_indice_night: number
  vulnerabilityIndexDay: number
  vulnerabilityIndexNight: number
  distribution_day: { [key: string]: number }
  distribution_night: { [key: string]: number }
}

export interface LczScoresResponse extends BaseScoresResponse {
  lcz_primary: string | null
  distribution: { [key: string]: number }
}
