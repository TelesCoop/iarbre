export const GEOCODER_API_URL = "https://photon.komoot.io/api/"

const LYON_CENTER = { lat: 45.75, lon: 4.85 }
const LYON_BBOX = { west: 4.65, east: 5.15, south: 45.55, north: 45.95 }

export interface GeocoderFeature {
  id: string | number
  center: [number, number]
  name: string
  address: string
  type: string
}

/** Zoom level to use after selecting a result, based on Photon result type. */
export const ZOOM_BY_TYPE: Record<string, number> = {
  house: 17,
  building: 17,
  street: 16,
  district: 14,
  city: 13,
  county: 11,
  state: 8,
  country: 6
}

const isInBbox = (lon: number, lat: number): boolean =>
  lon >= LYON_BBOX.west && lon <= LYON_BBOX.east && lat >= LYON_BBOX.south && lat <= LYON_BBOX.north

export const fetchGeocode = async (query: string): Promise<GeocoderFeature[]> => {
  const bboxParam = `${LYON_BBOX.west},${LYON_BBOX.south},${LYON_BBOX.east},${LYON_BBOX.north}`
  const url = `${GEOCODER_API_URL}?q=${encodeURIComponent(query)}&lat=${LYON_CENTER.lat}&lon=${LYON_CENTER.lon}&bbox=${bboxParam}&limit=10`

  const response = await fetch(url)
  const geojson = await response.json()
  const features: GeocoderFeature[] = []

  for (const feature of geojson.features) {
    const [lon, lat] = feature.geometry.coordinates
    if (!isInBbox(lon, lat)) continue

    const props = feature.properties
    const addressParts = [props.street, props.housenumber, props.city, props.postcode]
      .filter(Boolean)
      .join(", ")

    features.push({
      id: props.osm_id,
      center: feature.geometry.coordinates as [number, number],
      name: props.name || props.street || "",
      address: addressParts,
      type: props.type ?? ""
    })
  }

  return features
}
