import { type DataType, GeoLevel } from "@/utils/enum"

export interface IpaveData {
  id: string
  indice: string // herbacee, arbustif, or arborescent
  surface: number
  geolevel: GeoLevel
  datatype: DataType
}
