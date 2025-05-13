// Constants pour les sélecteurs et les dimensions
import { LIMIT_GEOCODE_CITY_CODE } from "@/utils/constants"
import type {
  MaplibreGeocoderApiConfig,
  MaplibreGeocoderFeatureResults,
  CarmenGeojsonFeature
} from "@maplibre/maplibre-gl-geocoder"

const SELECTORS = {
  CONTAINER: ".maplibregl-ctrl-geocoder",
  INPUT: ".maplibregl-ctrl-geocoder--input",
  SEARCH_ICON: ".maplibregl-ctrl-geocoder--icon-search"
}

const GEOCODER_STYLE = {
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
      // Format pour l'API adresse.data.gouv.fr
      const limit = config.limit || 5 // Valeur par défaut si non fournie
      const request = `https://api-adresse.data.gouv.fr/search/?q=${encodeURIComponent(
        config.query as string
      )}&limit=${limit}&citycode=${LIMIT_GEOCODE_CITY_CODE}`

      const response = await fetch(request)
      const data = await response.json()

      // Format différent de l'API adresse.data.gouv.fr
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
  const geocoderContainer = document.querySelector<HTMLDivElement>(SELECTORS.CONTAINER)
  const geocoderInput = document.querySelector<HTMLInputElement>(SELECTORS.INPUT)

  if (geocoderContainer && geocoderInput) {
    geocoderContainer.style.width = GEOCODER_STYLE.COLLAPSED.CONTAINER_WIDTH
    geocoderInput.style.width = GEOCODER_STYLE.COLLAPSED.INPUT_WIDTH
    geocoderInput.style.padding = GEOCODER_STYLE.COLLAPSED.INPUT_PADDING
  }
}

export const expandSearchBar = (): void => {
  const geocoderContainer = document.querySelector<HTMLDivElement>(SELECTORS.CONTAINER)
  const geocoderInput = document.querySelector<HTMLInputElement>(SELECTORS.INPUT)

  if (geocoderContainer && geocoderInput) {
    geocoderContainer.style.width = GEOCODER_STYLE.EXPANDED.CONTAINER_WIDTH
    geocoderInput.style.width = GEOCODER_STYLE.EXPANDED.INPUT_WIDTH
    geocoderInput.style.padding = GEOCODER_STYLE.EXPANDED.INPUT_PADDING
    geocoderInput.focus()
  }
}

export const initializeExpandableSearchBar = (): void => {
  const geocoderInput = document.querySelector<HTMLInputElement>(SELECTORS.INPUT)
  const geocoderContainer = document.querySelector<HTMLDivElement>(SELECTORS.CONTAINER)

  if (!geocoderInput || !geocoderContainer) {
    console.warn("Impossible to find the geocoder input or container")
    return
  }

  // Initialiser en état replié
  collapseSearchBar()

  geocoderContainer.addEventListener("click", (e: MouseEvent) => {
    const target = e.target as HTMLElement
    if (target.closest(SELECTORS.SEARCH_ICON) || target === geocoderContainer) {
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
