import type {
  MaplibreGeocoderApiConfig,
  MaplibreGeocoderFeatureResults,
  CarmenGeojsonFeature
} from "@maplibre/maplibre-gl-geocoder"

export const GEOCODER_API_URL = "https://photon.komoot.io/api/"

const LYON_CENTER = { lat: 45.75, lon: 4.85 }
const LYON_BBOX = {
  west: 4.65,
  east: 5.15,
  south: 45.55,
  north: 45.95
}

const isInBbox = (lon: number, lat: number): boolean => {
  return (
    lon >= LYON_BBOX.west &&
    lon <= LYON_BBOX.east &&
    lat >= LYON_BBOX.south &&
    lat <= LYON_BBOX.north
  )
}

const fetchGeocode = async (query: string): Promise<CarmenGeojsonFeature[]> => {
  const features: CarmenGeojsonFeature[] = []
  const bboxParam = `${LYON_BBOX.west},${LYON_BBOX.south},${LYON_BBOX.east},${LYON_BBOX.north}`
  const request = `${GEOCODER_API_URL}?q=${encodeURIComponent(query)}&lat=${LYON_CENTER.lat}&lon=${LYON_CENTER.lon}&bbox=${bboxParam}&limit=10`

  const response = await fetch(request)
  const geojson = await response.json()

  for (const feature of geojson.features) {
    const [lon, lat] = feature.geometry.coordinates
    if (!isInBbox(lon, lat)) {
      continue
    }

    const props = feature.properties
    const placeName = [props.name, props.city, props.country].filter(Boolean).join(", ")

    const point: CarmenGeojsonFeature = {
      id: props.osm_id,
      type: "Feature",
      geometry: feature.geometry,
      center: feature.geometry.coordinates as [number, number],
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
