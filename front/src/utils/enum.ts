export enum GeoLevel {
  TILE = "tile",
  LCZ = "lcz"
}

export enum DataType {
  PLANTABILITY = "plantability",
  VULNERABILITY = "vulnerability",
  CLIMATE_ZONE = "lcz",
  MIX_PLANTABILITY_AND_VULNERABILITY = "mix_plantability_and_vulnerability"
}

export enum MapStyle {
  OSM = "Plan",
  SATELLITE = "satellite",
  CADASTRE = "Cadastre"
}

export const MapStyleToLabel: Record<MapStyle, string> = {
  [MapStyle.OSM]: "Plan de la ville",
  [MapStyle.SATELLITE]: "Images satellite",
  [MapStyle.CADASTRE]: "Cadastre"
}

export const DataTypeToLabel: Record<DataType, string> = {
  [DataType.PLANTABILITY]: "Score de plantabilité",
  [DataType.CLIMATE_ZONE]: "Zones climatiques locales",
  [DataType.VULNERABILITY]: "Vulnérabilité chaleur",
  [DataType.MIX_PLANTABILITY_AND_VULNERABILITY]: "Mix plantabilité et vulnérabilité chaleur"
}

export const DataTypeToGeolevel: Record<DataType, GeoLevel> = {
  [DataType.PLANTABILITY]: GeoLevel.TILE,
  [DataType.CLIMATE_ZONE]: GeoLevel.LCZ,
  [DataType.VULNERABILITY]: GeoLevel.LCZ,
  [DataType.MIX_PLANTABILITY_AND_VULNERABILITY]: GeoLevel.TILE
}

const vulnerabilityDataTypeToAttributionSource =
  '<a class="text-primary-500" href="https://geoweb.grandlyon.com/portal/apps/storymaps/collections/7e7862ec92694601a7085074dcaf7481?item=3" target="_blank">Grand Lyon</a>'
const plantabilityDataTypeToAttributionSource =
  '<a class="text-primary-500" href="https://datagora.erasme.org/projets/calque-de-plantabilite/" target="_blank">ERASME</a>'
export const DataTypeToAttributionSource: Record<DataType, string> = {
  [DataType.CLIMATE_ZONE]:
    '<a class="text-primary-500" href="https://www.data.gouv.fr/en/datasets/cartographie-des-zones-climatiques-locales-lcz-de-83-aires-urbaines-de-plus-de-50-000-habitants-2022/" target="_blank">CEREMA</a>',
  [DataType.PLANTABILITY]: plantabilityDataTypeToAttributionSource,
  [DataType.VULNERABILITY]: vulnerabilityDataTypeToAttributionSource,
  [DataType.MIX_PLANTABILITY_AND_VULNERABILITY]: `${plantabilityDataTypeToAttributionSource} - ${vulnerabilityDataTypeToAttributionSource}`
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
