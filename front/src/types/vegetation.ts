import { type DataType, GeoLevel } from "@/utils/enum"

export type VegetationIndice = "herbacee" | "arbustif" | "arborescent"

export interface VegetationData {
  id: string
  indice: VegetationIndice
  surface: number
  geolevel: GeoLevel
  datatype: DataType
}
