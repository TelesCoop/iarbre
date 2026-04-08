import { MapStyle } from "@/utils/enum"

export interface MapStyleSource {
  provider: string
  year?: string
  url?: string
}

export interface MapStyleOption {
  value: MapStyle
  label: string
  image: string
  source: MapStyleSource
}

/**
 * Canonical list of background options exposed by `MapBackgroundSelector` and
 * used to build the maplibre-gl attribution at runtime.
 * This is the single source of truth for labels, images and credits.
 * `value` doubles as the key of the matching entry in `map-style.json`'s
 * `sources` object, keeping source metadata in a single place.
 */
export const MAP_STYLE_OPTIONS: MapStyleOption[] = [
  {
    value: MapStyle.OSM,
    label: "Plan",
    image: "/images/plan-ville.png",
    source: {
      provider: "OpenStreetMap Contributors",
      url: "https://www.openstreetmap.org/copyright"
    }
  },
  {
    value: MapStyle.ORTHOPHOTO,
    label: "Orthophoto",
    image: "/images/orthophoto.png",
    source: {
      provider: "Métropole de Lyon",
      year: "2023",
      url: "https://data.grandlyon.com/portail/fr/jeux-de-donnees/dalles-d-orthophotographie-2023-de-la-metropole-de-lyon/donnees"
    }
  },
  {
    value: MapStyle.SATELLITE,
    label: "Satellite",
    image: "/images/satellite.png",
    source: {
      provider: "Esri World Imagery",
      url: "https://www.arcgis.com/home/item.html?id=10df2279f9684e4a9f6a7f08febac2a9"
    }
  },
  {
    value: MapStyle.CADASTRE,
    label: "Cadastre",
    image: "/images/cadastre.png",
    source: {
      provider: "Cadastre — Etalab",
      url: "https://cadastre.data.gouv.fr/"
    }
  }
]

export const getMapStyleOption = (style: MapStyle): MapStyleOption =>
  MAP_STYLE_OPTIONS.find((opt) => opt.value === style) ?? MAP_STYLE_OPTIONS[0]

/**
 * Build an HTML attribution string for a given map style, suitable for the
 * maplibre-gl attribution widget.
 */
export const buildMapStyleAttribution = (style: MapStyle): string => {
  const option = getMapStyleOption(style)
  const { provider, year, url } = option.source
  const providerHtml = url
    ? `<a href="${url}" target="_blank" rel="noopener">${provider}</a>`
    : provider
  return year ? `${providerHtml} ${year}` : providerHtml
}

/**
 * Inject attributions from the canonical source list into a cloned maplibre
 * style JSON. Each `sources.<MapStyle>` present in the style gets its
 * `attribution` field overwritten with the generated HTML.
 */
export const applyMapStyleAttributions = <T extends { sources?: Record<string, any> }>(
  style: T
): T => {
  if (!style.sources) return style
  for (const option of MAP_STYLE_OPTIONS) {
    const source = style.sources[option.value]
    if (source) {
      source.attribution = buildMapStyleAttribution(option.value)
    }
  }
  return style
}
