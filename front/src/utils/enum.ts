import { getMetadata } from "../services/metadataService"

export enum GeoLevel {
  TILE = "tile",
  LCZ = "lcz",
  BIOSPHERE_FUNCTIONAL_INTEGRITY = "biosphere_functional_integrity"
}

export enum DataType {
  PLANTABILITY = "plantability",
  VULNERABILITY = "vulnerability",
  CLIMATE_ZONE = "lcz",
  PLANTABILITY_VULNERABILITY = "plantability_vulnerability",
  VEGESTRATE = "vegestrate",
  BIOSPHERE_FUNCTIONAL_INTEGRITY = "biosphere_functional_integrity"
}

export enum MapStyle {
  OSM = "osm",
  ORTHOPHOTO = "orthophoto",
  SATELLITE = "satellite",
  CADASTRE = "cadastre"
}

export enum SelectionMode {
  POINT = "point",
  POLYGON = "polygon",
  RECTANGLE = "rectangle",
  CIRCLE = "circle",
  ANGLED_RECTANGLE = "angled-rectangle",
  SELECT = "select"
}

export const MapStyleToLabel: Record<MapStyle, string> = {
  [MapStyle.OSM]: "Plan de la ville",
  [MapStyle.ORTHOPHOTO]: "Orthophoto Lyon 2023",
  [MapStyle.SATELLITE]: "Images satellite",
  [MapStyle.CADASTRE]: "Cadastre"
}

export const DataTypeToLabel: Record<DataType, string> = {
  [DataType.PLANTABILITY]: "Score de plantabilité",
  [DataType.CLIMATE_ZONE]: "Zones climatiques locales",
  [DataType.VULNERABILITY]: "Vulnérabilité chaleur",
  [DataType.PLANTABILITY_VULNERABILITY]: "Plantabilité et chaleur",
  [DataType.VEGESTRATE]: "Strates végétales",
  [DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY]: "Intégrité fonctionnelle de la biosphère"
}

export const DataTypeToGeolevel: Record<DataType, GeoLevel> = {
  [DataType.PLANTABILITY]: GeoLevel.TILE,
  [DataType.CLIMATE_ZONE]: GeoLevel.LCZ,
  [DataType.VULNERABILITY]: GeoLevel.LCZ,
  [DataType.PLANTABILITY_VULNERABILITY]: GeoLevel.TILE,
  [DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY]: GeoLevel.BIOSPHERE_FUNCTIONAL_INTEGRITY,
  [DataType.VEGESTRATE]: GeoLevel.TILE
}

export const DataTypeToAttributionSource: Record<DataType, string> = {
  [DataType.CLIMATE_ZONE]:
    '<a class="text-primary-500" href="https://www.data.gouv.fr/en/datasets/cartographie-des-zones-climatiques-locales-lcz-de-83-aires-urbaines-de-plus-de-50-000-habitants-2022/" target="_blank">CEREMA (2022-07)</a>',
  [DataType.PLANTABILITY]:
    '<a class="text-primary-500" href="https://documents.exo-dev.fr/notice_utilisation_calque_plantabilite_lyon_V1.pdf" target="_blank">ERASME (2025-03)</a>',
  [DataType.VULNERABILITY]:
    '<a class="text-primary-500" href="https://geoweb.grandlyon.com/portal/apps/storymaps/collections/7e7862ec92694601a7085074dcaf7481?item=3" target="_blank">Grand Lyon (2024-09)</a>',
  [DataType.PLANTABILITY_VULNERABILITY]:
    '<a class="text-primary-500" href="https://documents.exo-dev.fr/notice_utilisation_calque_plantabilite_lyon_V1.pdf" target="_blank">ERASME</a>',
  [DataType.VEGESTRATE]:
    '<a class="text-primary-500" href="https://github.com/TelesCoop/vegestrate/releases/tag/v2.0-metropole-lyon-ir-2023" target="_blank">Vegestrate</a>',
  [DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY]:
    '<a class="text-primary-500" href="https://millenaire3.grandlyon.com/ressources/2025/changement-climatique-comment-territorialiser-la-responsabilite-de-la-metropole-de-lyon-dans-le-depassement-des-limites-planetaires" target="_blank">2025 Emile Balembois — Licence CC BY-NC-SA 4.0</a>'
}

export const getDataTypeAttributionSource = async (dataType: DataType): Promise<string> => {
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
