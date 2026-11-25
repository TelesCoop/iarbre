const EARTH_RADIUS_M = 6378137
const SQUARE_METERS_PER_KM2 = 1_000_000
const M2_DISPLAY_THRESHOLD = 10_000

const toRadians = (degrees: number): number => (degrees * Math.PI) / 180

// Geodesic area (m²) of a WGS84 [lng, lat] ring via spherical excess — not SRID 2154.
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

const areaFormatter = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 })
const km2Formatter = new Intl.NumberFormat("fr-FR", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
})

export const formatArea = (areaM2: number): string => {
  if (areaM2 < M2_DISPLAY_THRESHOLD) {
    return `${areaFormatter.format(areaM2)} m²`
  }
  return `${km2Formatter.format(areaM2 / SQUARE_METERS_PER_KM2)} km²`
}

const toDegrees = (radians: number): number => (radians * 180) / Math.PI

// NOAA general solar position equations, azimuth in degrees clockwise from north.
export const solarAzimuth = (
  dayOfYear: number,
  utcHours: number,
  lat: number,
  lng: number
): number => {
  const gamma = ((2 * Math.PI) / 365) * (dayOfYear - 1 + (utcHours - 12) / 24)
  const equationOfTime =
    229.18 *
    (0.000075 +
      0.001868 * Math.cos(gamma) -
      0.032077 * Math.sin(gamma) -
      0.014615 * Math.cos(2 * gamma) -
      0.040849 * Math.sin(2 * gamma))
  const declination =
    0.006918 -
    0.399912 * Math.cos(gamma) +
    0.070257 * Math.sin(gamma) -
    0.006758 * Math.cos(2 * gamma) +
    0.000907 * Math.sin(2 * gamma) -
    0.002697 * Math.cos(3 * gamma) +
    0.00148 * Math.sin(3 * gamma)
  const hourAngle = toRadians((utcHours * 60 + equationOfTime + 4 * lng) / 4 - 180)
  const latitude = toRadians(lat)
  const azimuthFromSouth = Math.atan2(
    Math.sin(hourAngle),
    Math.cos(hourAngle) * Math.sin(latitude) - Math.tan(declination) * Math.cos(latitude)
  )
  return (toDegrees(azimuthFromSouth) + 180) % 360
}
