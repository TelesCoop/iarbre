export interface ContextDataFactor {
  key: string
  label: string
  value: string
  icon: string
  impact?: "positive" | "negative" | null
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

export type ContextDataColorScheme = "plantability" | "climate" | "vulnerability" | "vegetation"
export type CircularScoreSize = "small" | "normal" | "large"

export interface ContextDataVulnerabilityFactor extends ContextDataFactor {
  dayScore?: number | null
  nightScore?: number | null
  factorId?: string
}

export interface ContextDataVulnerabilityGroup extends ContextDataFactorGroup {
  factors: ContextDataVulnerabilityFactor[]
  categoryScores?: {
    day: number | null
    night: number | null
  }
}

export interface ContextDataScoreConfig {
  name?: string
  size?: CircularScoreSize
  score: number
  maxScore: number
  percentage: number
  label: string
  colorScheme: ContextDataColorScheme
  unit?: string
}

export interface ContextDataMainContainerProps {
  colorScheme: ContextDataColorScheme
  title: string
  description: string
  fullHeight?: boolean
  hideCloseButton?: boolean
}

export interface ContextDataLegendItem {
  label: string
  color: string
}
