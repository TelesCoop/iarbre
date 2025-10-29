import type {
  MaplibreGeocoderApiConfig,
  MaplibreGeocoderFeatureResults,
  CarmenGeojsonFeature
} from "@maplibre/maplibre-gl-geocoder"

export const LIMIT_GEOCODE_CITY_CODE = ""
export const LIMIT_GEOCODE_CITY_NAME = "Rhône"
export const LIMIT_GEOCODE_COUNTRY_NAME = "France"

export const GEOCODER_API_URL = "https://photon.komoot.io/api/"

const formatQueryWithCityAndCountry = (query: string | number[] | undefined): string => {
  return `${query}, ${LIMIT_GEOCODE_CITY_NAME}, ${LIMIT_GEOCODE_CITY_CODE}, ${LIMIT_GEOCODE_COUNTRY_NAME}`
}

const fetchGeocode = async (query: string): Promise<CarmenGeojsonFeature[]> => {
  const features: CarmenGeojsonFeature[] = []
  const formattedQuery = formatQueryWithCityAndCountry(query)
  const request = `${GEOCODER_API_URL}?q=${encodeURIComponent(formattedQuery)}&limit=10`

  const response = await fetch(request)
  const geojson = await response.json()

  for (const feature of geojson.features) {
    const props = feature.properties
    const placeName = [props.name, props.city, props.country].filter(Boolean).join(", ")

    const point: CarmenGeojsonFeature = {
      id: props.osm_id,
      type: "Feature",
      geometry: feature.geometry,
      place_name: placeName,
      properties: props,
      text: props.name || placeName,
      place_type: ["place"]
    }
    features.push(point)
  }

  return features
}

export const geocoderApi = {
  forwardGeocode: async (
    config: MaplibreGeocoderApiConfig
  ): Promise<MaplibreGeocoderFeatureResults> => {
    try {
      const features = await fetchGeocode(config.query as string)
      return {
        features,
        type: "FeatureCollection"
      }
    } catch (e) {
      console.error(`Failed to forwardGeocode with error: ${e}`)
      return {
        features: [],
        type: "FeatureCollection"
      }
    }
  }
}
