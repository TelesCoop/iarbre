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

const DOCUMENTATION_BASE_URL =
  "https://erasme.notion.site/Documentation-IA-rbre-33444e49a3ad80af8d9ef01b578e1192"

export const DataTypeToDocumentationUrl: Record<DataType, string> = {
  [DataType.PLANTABILITY]:
    "https://erasme.notion.site/Lire-le-score-de-plantabilit-33444e49a3ad8080bb66f23ad06bb6a1",
  [DataType.VULNERABILITY]:
    "https://erasme.notion.site/Comprendre-l-atlas-de-vuln-rabilit-la-chaleur-33644e49a3ad80878f83fa021241cbd1",
  [DataType.PLANTABILITY_VULNERABILITY]:
    "https://erasme.notion.site/Croisement-plantabilit-vuln-rabilit-la-chaleur-33644e49a3ad80b9a0aeeba0910920f8",
  [DataType.VEGESTRATE]:
    "https://erasme.notion.site/L-inventaire-du-v-g-tal-stratifi-expliqu-33644e49a3ad805d95e2de361988c45d",
  [DataType.CLIMATE_ZONE]: DOCUMENTATION_BASE_URL,
  [DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY]:
    "https://erasme.notion.site/Comment-territorialiser-une-limite-plan-taire-35144e49a3ad805681b3f55275b608c4"
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
