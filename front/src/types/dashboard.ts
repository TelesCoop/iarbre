export interface DashboardCity {
  id: number
  code: string
  name: string
}

export interface DashboardPlantabilityDivision {
  code: string
  name: string
  averageNormalizedIndice: number
  distribution: Record<string, number>
}

export interface DashboardPlantability {
  averageNormalizedIndice: number
  distribution: Record<string, number>
  distributionByDivision: DashboardPlantabilityDivision[]
}

export interface DashboardVulnerability {
  averageDay: number
  averageNight: number
  expoDay: number
  expoNight: number
  sensibilityDay: number
  sensibilityNight: number
  capafDay: number
  capafNight: number
}

export interface DashboardVegetation {
  totalHa: number
  treesSurfaceHa: number
  bushesSurfaceHa: number
  grassSurfaceHa: number
}

export interface DashboardLcz {
  averageBuildingSurfaceRate: number
  averageBuildingHeight: number
  impermeableSurfaceRate: number
  permeableSoilRate: number
  buildingRate: number
  treeCoverRate: number
  totalVegetationRate: number
  waterRate: number
}

export interface DashboardData {
  city: DashboardCity | null
  areaHa: number
  plantability: DashboardPlantability
  vulnerability: DashboardVulnerability
  vegetation: DashboardVegetation
  lcz: DashboardLcz
}

export interface BubbleItem {
  id: string
  label: string
  value: number
  color: string
}

export type DashboardScale = "metropole" | "commune" | "iris"
