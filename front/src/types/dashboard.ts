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
  totalM2: number
  treesSurfaceM2: number
  bushesSurfaceM2: number
  grassSurfaceM2: number
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

export interface DashboardBuildings {
  averageBuildingFootprintM2: number
}

export interface DashboardBiosphere {
  averageIndice: number
  distribution: Record<string, number>
}

export interface DashboardData {
  city: DashboardCity | null
  areaHa: number
  plantability: DashboardPlantability
  vulnerability: DashboardVulnerability
  vegetation: DashboardVegetation
  lcz: DashboardLcz
  buildings: DashboardBuildings
  biosphere: DashboardBiosphere
}

export interface BubbleItem {
  id: string
  label: string
  value: number
  color: string
}

export type DashboardScale = "metropole" | "commune"
