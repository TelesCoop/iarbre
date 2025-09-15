export interface ContextDataFactor {
  key: string
  label: string
  value: string
  icon: string
  impact?: string | null
  description?: string
  unit?: string
}

export interface ContextDataFactorGroup {
  category: string
  label: string
  icon: string
  factors: ContextDataFactor[]
  hasPositiveImpact?: boolean
  hasNegativeImpact?: boolean
  description?: string
}

export type ContextDataColorScheme = "plantability" | "climate" | "vulnerability"

// Vulnerability-specific extended factor for Day/Night functionality
export interface ContextDataVulnerabilityFactor extends ContextDataFactor {
  dayScore?: number | null
  nightScore?: number | null
  factorId?: string
}

// Extended group for vulnerability with score badges support
export interface ContextDataVulnerabilityGroup extends ContextDataFactorGroup {
  factors: ContextDataVulnerabilityFactor[]
  categoryScores?: {
    day: number | null
    night: number | null
  }
}
