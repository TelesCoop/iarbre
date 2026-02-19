import { type DataType, GeoLevel } from "@/utils/enum"

export interface BiosphereIntegrityData {
  id: string
  indice: number
  geolevel: GeoLevel
  datatype: DataType
}
