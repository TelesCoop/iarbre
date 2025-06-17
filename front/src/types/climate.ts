import type { DataType, GeoLevel } from "@/utils/enum"

export enum ClimateDataDetailsKey {
  HRE = "hre",
  ARE = "are",
  BUR = "bur",
  ROR = "ror",
  BSR = "bsr",
  WAR = "war",
  VER = "ver",
  VHR = "vhr"
}

export interface ClimateDataDetails {
  [ClimateDataDetailsKey.HRE]: number // Hauteur moyenne du bâti (en m)
  [ClimateDataDetailsKey.ARE]: number // Superficie moyenne du bâti (en m²)
  [ClimateDataDetailsKey.BUR]: number // Taux de surface bâtie (en %)
  [ClimateDataDetailsKey.ROR]: number // Taux de surface minérale imperméable (en %)
  [ClimateDataDetailsKey.BSR]: number // Taux de sol nu perméable (en %)
  [ClimateDataDetailsKey.WAR]: number // Taux de surface en eau (en %)
  [ClimateDataDetailsKey.VER]: number // Taux de végétation (en %)
  [ClimateDataDetailsKey.VHR]: number // Part de végétation arborée sur la végétation globale (en %)
}

export enum ClimateCategory {
  BUILDING = "Caractéristiques du bâti",
  SURFACES = "Types de surfaces",
  VEGETATION = "Végétation et eau"
}

export interface ClimateData {
  details: ClimateDataDetails

  datatype: DataType
  geolevel: GeoLevel
  id: number

  geometry: string
  mapGeometry: string
}
