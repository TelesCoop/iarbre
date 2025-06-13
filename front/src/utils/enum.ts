export enum GeoLevel {
  TILE = "tile",
  LCZ = "lcz"
}

export enum DataType {
  PLANTABILITY = "plantability",
  LOCAL_CLIMATE_ZONES = "lcz",
  VULNERABILITY = "vulnerability"
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
  [DataType.LOCAL_CLIMATE_ZONES]: "Zones climatiques locales",
  [DataType.VULNERABILITY]: "Vulnérabilité chaleur"
}

export const DataTypeToGeolevel: Record<DataType, GeoLevel> = {
  [DataType.PLANTABILITY]: GeoLevel.TILE,
  [DataType.LOCAL_CLIMATE_ZONES]: GeoLevel.LCZ,
  [DataType.VULNERABILITY]: GeoLevel.LCZ
}

export const DataTypeToAttributionSource: Record<DataType, string> = {
  [DataType.LOCAL_CLIMATE_ZONES]:
    '<a class="text-primary-500" href="https://www.data.gouv.fr/en/datasets/cartographie-des-zones-climatiques-locales-lcz-de-83-aires-urbaines-de-plus-de-50-000-habitants-2022/" target="_blank">CEREMA</a>',
  [DataType.PLANTABILITY]:
    '<a class="text-primary-500" href="https://datagora.erasme.org/projets/calque-de-plantabilite/" target="_blank">ERASME</a>',
  [DataType.VULNERABILITY]:
    '<a class="text-primary-500" href="https://geoweb.grandlyon.com/portal/apps/storymaps/collections/7e7862ec92694601a7085074dcaf7481?item=3" target="_blank">Grand Lyon</a>'
}

export enum VulnerabilityCategory {
  EXPOSITION = "Exposition",
  CAPACITY_TO_FACE = "Capacité à faire face",
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
