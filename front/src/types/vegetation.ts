import { type DataType, GeoLevel } from "@/utils/enum"

export interface VegetationData {
  id: string
  geolevel: GeoLevel
  datatype: DataType
}
