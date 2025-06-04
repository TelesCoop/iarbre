import { type DataType, GeoLevel } from "@/utils/enum"

export enum PlantabilityImpact {
  POSITIVE = "positive",
  NEGATIVE = "négative"
}

export enum PlantabilityScore {
  IMPOSSIBLE = "Plantation impossible",
  VERY_CONSTRAINED = "Plantation très contrainte",
  CONSTRAINED = "Plantation contrainte",
  NEUTRAL = "Plantation neutre",
  FAVORED = "Plantation favorisée",
  VERY_FAVORED = "Plantation très favorisée"
}

export enum PlantabilityLandUseKeys {
  SOUCHES_EMPLACEMENTS_LIBRES = "Souches ou emplacements libres",
  ARBRES = "Arbres",
  AERODROME = "Aerodrome",
  PARKINGS = "Parkings",
  SIGNALISATION_TRICOLORE = "Signalisation tricolore et lumineuse matériel",
  STATION_VELOV = "Station velov",
  ARRETS_TRANSPORT = "Arrêts transport en commun",
  PROXIMITE_FACADE = "Proximité façade",
  BATIMENTS = "Bâtiments",
  FRICHES = "Friches",
  ASSAINISSEMENT = "Assainissement",
  PARCS_JARDINS = "Parcs et jardins publics",
  GIRATOIRES = "Giratoires",
  ESPACES_JEUX_PIETONNIER = "Espaces jeux et pietonnier",
  FRICHE_NATURELLE = "Friche naturelle",
  RESEAU_FIBRE = "Réseau Fibre",
  MARCHES_FORAINS = "Marchés forains",
  PISTES_CYCLABLE = "Pistes cyclable",
  PLAN_EAU = "Plan eau",
  PONTS = "Ponts",
  RESEAU_CHALEUR_URBAIN = "Réseau de chaleur urbain",
  VOIES_FERREES = "Voies ferrées",
  STRATE_ARBOREE = "Strate arborée",
  STRATE_BASSE_PELOUSE = "Strate basse et pelouse",
  ESPACES_AGRICOLES = "Espaces agricoles",
  FORETS = "Forêts",
  ESPACES_ARTIFICIALISES = "Espaces artificialisés",
  TRACE_METRO = "Tracé de métro",
  TRACE_TRAMWAY = "Tracé de tramway",
  TRACE_BUS = "Tracé de bus",
  RSX_GAZ = "Rsx gaz",
  RSX_SOUTERRAINS_ERDF = "Rsx souterrains ERDF",
  RSX_AERIENS_ERDF = "Rsx aériens ERDF",
  PMR = "PMR",
  AUTO_PARTAGE = "Auto-partage"
}

export enum PlantabilityOccupationLevel {
  FAIBLE = "faible",
  MOYEN = "moyen",
  FORT = "fort"
}

export enum PlantabilityMetaCategory {
  RESEAUX_INFRASTRUCTURES = "Réseaux et infrastructures",
  INFRASTRUCTURE_TRANSPORT = "Infrastructure de transport",
  BATIMENTS = "Bâtiments",
  ESPACES_VERTS = "Espaces verts",
  AMENAGEMENTS_URBAINS = "Aménagements urbains",
  PLANS_EAU = "Plans d'eau"
}

export interface PlantabilityLandUse {
  [PlantabilityLandUseKeys.SOUCHES_EMPLACEMENTS_LIBRES]?: number
  [PlantabilityLandUseKeys.ARBRES]?: number
  [PlantabilityLandUseKeys.AERODROME]?: number
  [PlantabilityLandUseKeys.PARKINGS]?: number
  [PlantabilityLandUseKeys.SIGNALISATION_TRICOLORE]?: number
  [PlantabilityLandUseKeys.STATION_VELOV]?: number
  [PlantabilityLandUseKeys.ARRETS_TRANSPORT]?: number
  [PlantabilityLandUseKeys.PROXIMITE_FACADE]?: number
  [PlantabilityLandUseKeys.BATIMENTS]?: number
  [PlantabilityLandUseKeys.FRICHES]?: number
  [PlantabilityLandUseKeys.ASSAINISSEMENT]?: number
  [PlantabilityLandUseKeys.PARCS_JARDINS]?: number
  [PlantabilityLandUseKeys.GIRATOIRES]?: number
  [PlantabilityLandUseKeys.ESPACES_JEUX_PIETONNIER]?: number
  [PlantabilityLandUseKeys.FRICHE_NATURELLE]?: number
  [PlantabilityLandUseKeys.RESEAU_FIBRE]?: number
  [PlantabilityLandUseKeys.MARCHES_FORAINS]?: number
  [PlantabilityLandUseKeys.PISTES_CYCLABLE]?: number
  [PlantabilityLandUseKeys.PLAN_EAU]?: number
  [PlantabilityLandUseKeys.PONTS]?: number
  [PlantabilityLandUseKeys.RESEAU_CHALEUR_URBAIN]?: number
  [PlantabilityLandUseKeys.VOIES_FERREES]?: number
  [PlantabilityLandUseKeys.STRATE_ARBOREE]?: number
  [PlantabilityLandUseKeys.STRATE_BASSE_PELOUSE]?: number
  [PlantabilityLandUseKeys.ESPACES_AGRICOLES]?: number
  [PlantabilityLandUseKeys.FORETS]?: number
  [PlantabilityLandUseKeys.ESPACES_ARTIFICIALISES]?: number
  [PlantabilityLandUseKeys.TRACE_METRO]?: number
  [PlantabilityLandUseKeys.TRACE_TRAMWAY]?: number
  [PlantabilityLandUseKeys.TRACE_BUS]?: number
  [PlantabilityLandUseKeys.RSX_GAZ]?: number
  [PlantabilityLandUseKeys.RSX_SOUTERRAINS_ERDF]?: number
  [PlantabilityLandUseKeys.RSX_AERIENS_ERDF]?: number
  [PlantabilityLandUseKeys.PMR]?: number
  [PlantabilityLandUseKeys.AUTO_PARTAGE]?: number
}

interface PlantabilityTileDetails {
  top5LandUse: PlantabilityLandUse
}

export interface PlantabilityTile {
  id: string
  plantabilityNormalizedIndice: number
  plantabilityIndice: number
  details?: PlantabilityTileDetails
  geolevel: GeoLevel
  datatype: DataType
  iris: number
  city: number
}
