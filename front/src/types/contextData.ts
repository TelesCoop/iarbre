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
