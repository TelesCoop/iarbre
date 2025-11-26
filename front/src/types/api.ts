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
  vulnerabilityIndiceDay: number
  vulnerabilityIndiceNight: number
}
