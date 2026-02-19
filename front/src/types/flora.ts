export interface LocalFloraSummary {
  totalSpeciesObserved: number
  dominantFamilies: string[]
  dominantGenera: string[]
}

export interface TreeRecommendation {
  scientificName: string
  commonName: string
  score: number
  isNative: boolean
  description: string
  matchedCompanions: string[]
  ecosystemHighlights: string[]
  reasoning: string[]
  inpnValidated: boolean
}

export interface FloraRecommendations {
  localFloraSummary: LocalFloraSummary
  lczContext: string
  lczIndex: string | null
  lczDescription: string | null
  recommendations: TreeRecommendation[]
}
