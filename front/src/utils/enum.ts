import { getMetadata } from "../services/metadataService"

export enum GeoLevel {
  TILE = "tile",
  LCZ = "lcz"
}

export enum DataType {
  PLANTABILITY = "plantability",
  VULNERABILITY = "vulnerability",
  CLIMATE_ZONE = "lcz",
  PLANTABILITY_VULNERABILITY = "plantability_vulnerability"
}

export enum MapStyle {
  OSM = "Plan",
  SATELLITE = "satellite",
  CADASTRE = "Cadastre"
}

export enum SelectionMode {
  POINT = "point",
  POLYGON = "polygon",
  RECTANGLE = "rectangle",
  CIRCLE = "circle",
  ANGLED_RECTANGLE = "angled-rectangle",
  SECTOR = "sector",
  SELECT = "select"
}

export const MapStyleToLabel: Record<MapStyle, string> = {
  [MapStyle.OSM]: "Plan de la ville",
  [MapStyle.SATELLITE]: "Images satellite",
  [MapStyle.CADASTRE]: "Cadastre"
}

export const DataTypeToLabel: Record<DataType, string> = {
  [DataType.PLANTABILITY]: "🌳 Score de plantabilité",
  [DataType.CLIMATE_ZONE]: "🌆 Zones climatiques locales",
  [DataType.VULNERABILITY]: "🌡️ Vulnérabilité chaleur",
  [DataType.PLANTABILITY_VULNERABILITY]: "🌳🌡️ Plantabilité et chaleur"
}

export const DataTypeToGeolevel: Record<DataType, GeoLevel> = {
  [DataType.PLANTABILITY]: GeoLevel.TILE,
  [DataType.CLIMATE_ZONE]: GeoLevel.LCZ,
  [DataType.VULNERABILITY]: GeoLevel.LCZ,
  [DataType.PLANTABILITY_VULNERABILITY]: GeoLevel.TILE
}

export const DataTypeToAttributionSource: Record<DataType, string> = {
  [DataType.CLIMATE_ZONE]:
    '<a class="text-primary-500" href="https://www.data.gouv.fr/en/datasets/cartographie-des-zones-climatiques-locales-lcz-de-83-aires-urbaines-de-plus-de-50-000-habitants-2022/" target="_blank">CEREMA (2022-07)</a>',
  [DataType.PLANTABILITY]:
    '<a class="text-primary-500" href="https://datagora.erasme.org/projets/calque-de-plantabilite/" target="_blank">ERASME</a>',
  [DataType.VULNERABILITY]:
    '<a class="text-primary-500" href="https://geoweb.grandlyon.com/portal/apps/storymaps/collections/7e7862ec92694601a7085074dcaf7481?item=3" target="_blank">Grand Lyon (2024-09)</a>',
  [DataType.PLANTABILITY_VULNERABILITY]:
    '<a class="text-primary-500" href="https://datagora.erasme.org/projets/calque-de-plantabilite/" target="_blank">ERASME</a>'
}

export const getDataTypeAttributionSource = async (dataType: DataType): Promise<string> => {
  if (dataType === DataType.PLANTABILITY) {
    const metadata = await getMetadata()
    const dateText = metadata?.generationDate ? ` (${metadata.generationDate})` : ""
    return `<a class="text-primary-500" href="https://datagora.erasme.org/projets/calque-de-plantabilite/" target="_blank">ERASME</a>${dateText}`
  }
  return DataTypeToAttributionSource[dataType]
}

export enum VulnerabilityCategory {
  EXPOSITION = "Exposition",
  CAPACITY_TO_FACE = "Difficulté à faire face",
  SENSIBILITY = "Sensibilité"
}

export const VulnerabilityCategoryToIcon: Record<VulnerabilityCategory, string> = {
  [VulnerabilityCategory.EXPOSITION]: "🌡️",
  [VulnerabilityCategory.CAPACITY_TO_FACE]: "🏥",
  [VulnerabilityCategory.SENSIBILITY]: "👥"
}

export const VulnerabilityCategoryToDescription: Record<VulnerabilityCategory, string> = {
  [VulnerabilityCategory.EXPOSITION]: "Facteurs liés à l'exposition à la chaleur",
  [VulnerabilityCategory.CAPACITY_TO_FACE]: "Facteurs de capacité d'adaptation",
  [VulnerabilityCategory.SENSIBILITY]: "Facteurs de sensibilité de la population"
}

export const VulnerabilityCategoryOrder = [
  VulnerabilityCategory.EXPOSITION,
  VulnerabilityCategory.CAPACITY_TO_FACE,
  VulnerabilityCategory.SENSIBILITY
]

export const DataTypeToDownloadLink: Record<DataType, string> = {
  [DataType.PLANTABILITY]:
    "https://data.grandlyon.com/portail/en/jeux-de-donnees/calque-plantabilite-metropole-lyon/info",
  [DataType.CLIMATE_ZONE]:
    "https://www.data.gouv.fr/datasets/cartographie-des-zones-climatiques-locales-lcz-des-88-aires-urbaines-de-plus-de-50-000-habitants-de-france-metropolitaine/#/resources/e0c0f5e4-c8bb-4d33-aec9-ba16b5736102",
  [DataType.VULNERABILITY]:
    "https://data.grandlyon.com/portail/en/jeux-de-donnees/exposition-et-vulnerabilite-aux-fortes-chaleurs-dans-la-metropole-de-lyon/info",
  [DataType.PLANTABILITY_VULNERABILITY]:
    "https://data.grandlyon.com/portail/en/jeux-de-donnees/calque-plantabilite-metropole-lyon/info"
}
