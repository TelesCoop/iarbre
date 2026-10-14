import type { ZonePolygon } from "@/stores/zone"

export const encodeZone = (zone: ZonePolygon): string =>
  zone.coordinates[0].map(([lng, lat]) => `${lng.toFixed(5)},${lat.toFixed(5)}`).join("~")

export const decodeZone = (value: string): ZonePolygon | null => {
  const ring = value.split("~").map((pair) => pair.split(",").map(Number) as [number, number])
  if (ring.length < 4 || ring.some((p) => p.length !== 2 || !p.every(Number.isFinite))) return null
  return { type: "Polygon", coordinates: [ring] }
}
