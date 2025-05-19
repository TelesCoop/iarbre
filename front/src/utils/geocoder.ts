import type {
  MaplibreGeocoderApiConfig,
  MaplibreGeocoderFeatureResults,
  CarmenGeojsonFeature
} from "@maplibre/maplibre-gl-geocoder"

export const LIMIT_GEOCODE_CITY_CODE = "69000"
export const LIMIT_GEOCODE_CITY_NAME = "Lyon"
export const LIMIT_GEOCODE_COUNTRY_NAME = "France"

export const GEOCODER_API_URL = "https://nominatim.openstreetmap.org/search"

const formatQueryWithCityAndCountry = (query: string | number[] | undefined): string => {
  return `${query}, ${LIMIT_GEOCODE_CITY_NAME}, ${LIMIT_GEOCODE_CITY_CODE}, ${LIMIT_GEOCODE_COUNTRY_NAME}`
}
export const geocoderApi = {
  forwardGeocode: async (
    config: MaplibreGeocoderApiConfig
  ): Promise<MaplibreGeocoderFeatureResults> => {
    const features: CarmenGeojsonFeature[] = []
    try {
      const request = `${GEOCODER_API_URL}?q=${formatQueryWithCityAndCountry(
        config.query
      )}&format=geojson&polygon_geojson=1&addressdetails=1`
      const response = await fetch(request)
      const geojson = await response.json()
      for (const feature of geojson.features) {
        const center = [
          feature.bbox[0] + (feature.bbox[2] - feature.bbox[0]) / 2,
          feature.bbox[1] + (feature.bbox[3] - feature.bbox[1]) / 2
        ]
        const point: CarmenGeojsonFeature = {
          id: feature.properties.osm_id,
          type: "Feature",
          geometry: {
            type: "Point",
            coordinates: center
          },
          place_name: feature.properties.display_name,
          properties: feature.properties,
          text: feature.properties.display_name,
          place_type: ["place"]
        }
        features.push(point)
      }
    } catch (e) {
      console.error(`Failed to forwardGeocode with error: ${e}`)
    }

    return {
      features,
      type: "FeatureCollection"
    }
  }
}
