import { type DataType, GeoLevel } from "./utils/enum"

export interface MapScorePopupData {
  lng: number
  lat: number
  id: string
  properties: any
  score: string
}

export interface MapParams {
  lng: number
  lat: number
  zoom: number
  dataType: DataType | null
}

export interface Feedback {
  email: string
  feedback: string
}

interface PlantabilityLandUse {
  "Souches ou emplacements libres"?: number
  Arbres?: number
  Aerodrome?: number
  Parkings?: number
  "Signalisation tricolore et lumineuse matériel"?: number
  "Station velov"?: number
  "Arrêts transport en commun"?: number
  "Proximité façade"?: number
  Bâtiments?: number
  Friches?: number
  Assainissement?: number
  "Parcs et jardins publics"?: number
  Giratoires?: number
  "Espaces jeux et pietonnier"?: number
  "Friche naturelle"?: number
  "Réseau Fibre"?: number
  "Marchés forains"?: number
  "Pistes cyclable"?: number
  "Plan eau"?: number
  Ponts?: number
  "Réseau de chaleur urbain"?: number
  "Voies ferrées"?: number
  "Strate arborée"?: number
  "Strate basse et pelouse"?: number
  "Espaces agricoles"?: number
  Forêts?: number
  "Espaces artificialisés"?: number
  "Tracé de métro"?: number
  "Tracé de tramway"?: number
  "Tracé de bus"?: number
  "Rsx gaz"?: number
  "Rsx souterrains ERDF"?: number
  "Rsx aériens ERDF"?: number
  PMR?: number
  "Auto-partage"?: number
}

interface PlantabilityTileDetails {
  top5LandUse: PlantabilityLandUse
}

export interface PlantabilityTile {
  id: string
  plantability_normalized_indice: number
  plantability_indice: number
  details?: PlantabilityTileDetails
  geolevel: GeoLevel
  datatype: DataType
  iris: number
  city: number
}
