import type {
  MaplibreGeocoderApiConfig,
  MaplibreGeocoderFeatureResults,
  CarmenGeojsonFeature
} from "@maplibre/maplibre-gl-geocoder"

export const LIMIT_GEOCODE_CITY_CODE = 69123
export const GEOCODER_SELECTORS = {
  CONTAINER: ".maplibregl-ctrl-geocoder",
  INPUT: ".maplibregl-ctrl-geocoder--input",
  SEARCH_ICON: ".maplibregl-ctrl-geocoder--icon-search"
}

export const GEOCODER_STYLE = {
  COLLAPSED: {
    CONTAINER_WIDTH: "29px",
    INPUT_WIDTH: "0",
    INPUT_PADDING: "0"
  },
  EXPANDED: {
    CONTAINER_WIDTH: "320px",
    INPUT_WIDTH: "100%",
    INPUT_PADDING: "6px 35px"
  }
}

export const geocoderApi = {
  forwardGeocode: async (
    config: MaplibreGeocoderApiConfig
  ): Promise<MaplibreGeocoderFeatureResults> => {
    const features: CarmenGeojsonFeature[] = []
    try {
      const limit = config.limit || 5
      const request = `https://api-adresse.data.gouv.fr/search/?q=${encodeURIComponent(
        config.query as string
      )}&limit=${limit}&citycode=${LIMIT_GEOCODE_CITY_CODE}`

      const response = await fetch(request)
      const data = await response.json()

      for (const feature of data.features) {
        const coordinates = feature.geometry.coordinates

        const point: CarmenGeojsonFeature = {
          id: feature.properties.id,
          type: "Feature",
          geometry: {
            type: "Point",
            coordinates: coordinates
          },
          place_name: feature.properties.label,
          properties: {
            ...feature.properties,
            display_name: feature.properties.label
          },
          text: feature.properties.label,
          place_type: ["place"]
        }
        features.push(point)
      }
    } catch (e) {
      console.error(`Échec de la géolocalisation avec l'erreur: ${e}`)
    }

    return {
      features,
      type: "FeatureCollection"
    }
  }
}

export const collapseSearchBar = (): void => {
  const geocoderContainer = document.querySelector<HTMLDivElement>(GEOCODER_SELECTORS.CONTAINER)
  const geocoderInput = document.querySelector<HTMLInputElement>(GEOCODER_SELECTORS.INPUT)

  if (geocoderContainer && geocoderInput) {
    geocoderContainer.style.width = GEOCODER_STYLE.COLLAPSED.CONTAINER_WIDTH
    geocoderInput.style.width = GEOCODER_STYLE.COLLAPSED.INPUT_WIDTH
    geocoderInput.style.padding = GEOCODER_STYLE.COLLAPSED.INPUT_PADDING
  }
}

export const expandSearchBar = (): void => {
  const geocoderContainer = document.querySelector<HTMLDivElement>(GEOCODER_SELECTORS.CONTAINER)
  const geocoderInput = document.querySelector<HTMLInputElement>(GEOCODER_SELECTORS.INPUT)

  if (geocoderContainer && geocoderInput) {
    geocoderContainer.style.width = GEOCODER_STYLE.EXPANDED.CONTAINER_WIDTH
    geocoderInput.style.width = GEOCODER_STYLE.EXPANDED.INPUT_WIDTH
    geocoderInput.style.padding = GEOCODER_STYLE.EXPANDED.INPUT_PADDING
    geocoderInput.focus()
  }
}

export const initializeExpandableSearchBar = (): void => {
  const geocoderInput = document.querySelector<HTMLInputElement>(GEOCODER_SELECTORS.INPUT)
  const geocoderContainer = document.querySelector<HTMLDivElement>(GEOCODER_SELECTORS.CONTAINER)

  if (!geocoderInput || !geocoderContainer) {
    console.warn("Impossible to find the geocoder input or container")
    return
  }

  collapseSearchBar()
  geocoderContainer.addEventListener("click", (e: MouseEvent) => {
    const target = e.target as HTMLElement
    if (target.closest(GEOCODER_SELECTORS.SEARCH_ICON) || target === geocoderContainer) {
      expandSearchBar()
    }
  })

  document.addEventListener("click", (e: MouseEvent) => {
    const target = e.target as HTMLElement
    if (!geocoderContainer.contains(target) && geocoderInput.value === "") {
      collapseSearchBar()
    }
  })
}
