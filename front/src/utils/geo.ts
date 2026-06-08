const EARTH_RADIUS_M = 6378137
const SQUARE_METERS_PER_KM2 = 1_000_000
// Below this, an area reads better in m² than in (tiny) fractions of a km².
const M2_DISPLAY_THRESHOLD = 10_000

const toRadians = (degrees: number): number => (degrees * Math.PI) / 180

/**
 * Geodesic area of a polygon ring expressed in square meters, using the
 * spherical excess formula. Input coordinates are WGS84 [lng, lat] pairs
 * (TerraDraw / MapLibre space) — not the backend SRID 2154 Lambert.
 */
export const computePolygonAreaM2 = (ring: number[][]): number => {
  if (ring.length < 3) return 0

  let total = 0
  for (let i = 0; i < ring.length; i++) {
    const [lng1, lat1] = ring[i]
    const [lng2, lat2] = ring[(i + 1) % ring.length]
    total += toRadians(lng2 - lng1) * (2 + Math.sin(toRadians(lat1)) + Math.sin(toRadians(lat2)))
  }

  return Math.abs((total * EARTH_RADIUS_M * EARTH_RADIUS_M) / 2)
}

// Built once to avoid reallocating the Intl object on every format call.
const areaFormatter = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 })
const km2Formatter = new Intl.NumberFormat("fr-FR", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
})

/** Human-readable area: m² for small selections, km² above the threshold. */
export const formatArea = (areaM2: number): string => {
  if (areaM2 < M2_DISPLAY_THRESHOLD) {
    return `${areaFormatter.format(areaM2)} m²`
  }
  return `${km2Formatter.format(areaM2 / SQUARE_METERS_PER_KM2)} km²`
}
