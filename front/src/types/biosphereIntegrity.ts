import { type DataType, GeoLevel } from "@/utils/enum"

export interface LandCoverRecord {
  landCover: string
  landCoverLabel: string
  binary: boolean | null
  percentage: number
}

export interface BiosphereIntegrityData {
  id: string
  indice: number
  geolevel: GeoLevel
  datatype: DataType
  landCovers?: LandCoverRecord[] | null
}
