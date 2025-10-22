import { type DataType, GeoLevel } from "@/utils/enum"
import { type PlantabilityDataDetails } from "@/types/plantability"

export interface PlantabilityVulnerabilityData {
  id: string
  plantabilityNormalizedIndice: number
  plantabilityIndice: number
  vulnerability_indice_day: number
  vulnerability_indice_night: number
  details?: PlantabilityDataDetails | string
  geolevel: GeoLevel
  datatype: DataType
  iris: number
  city: number
}
