export const SURFACE_COLORS = {
  building: "#F59E0B",
  impermeable: "#6B7280",
  permeableSoil: "#D4A853",
  vegetation: "#55B250",
  water: "#3B82F6"
} as const

export const VEGETATION_COLORS = {
  trees: "#025400",
  bushes: "#55B250",
  grass: "#A6CC4A"
} as const

export const HEAT_COLORS = {
  day: { expo: "#FBBF24", sensibility: "#F59E0B", capaf: "#D97706", accent: "#F59E0B" },
  night: { expo: "#818CF8", sensibility: "#6366F1", capaf: "#4F46E5", accent: "#6366F1" }
} as const
