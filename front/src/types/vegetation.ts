import { type DataType, GeoLevel } from "@/utils/enum"

export type VegetationIndice = "herbacee" | "arbustif" | "arborescent"

export interface SoilOccupancyData {
  classId: number
  code: string
  label: string | null
  datatype: "soil_occupancy"
  geolevel: GeoLevel
}

export interface VegetationData {
  id: string
  indice: VegetationIndice
  surface: number
  geolevel: GeoLevel
  datatype: DataType
  soilOccupancy?: SoilOccupancyData | null
}
