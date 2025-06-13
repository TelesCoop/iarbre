import type { LngLatBounds } from "maplibre-gl"
import type { FeatureCollection, Feature, Polygon, MultiPolygon } from "geojson"

export interface EpciInfo {
  code: string
  nom: string
  codeDepartement: string
  codeRegion: string
  population: number
}

export interface CadastreProperties {
  id: string
  commune: string
  prefixe: string
  section: string
  numero: string
  contenance: number
  arpente: boolean
  created: string
  updated: string
}

export type CadastreParcel = Feature<Polygon | MultiPolygon, CadastreProperties>

export type CadastreResponse = FeatureCollection<Polygon | MultiPolygon, CadastreProperties>

async function fetchExternalApi<T>(url: string): Promise<{ data: T | undefined; error: unknown }> {
  try {
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    const data = await response.json()
    return { data, error: undefined }
  } catch (error) {
    console.error(`Error fetching ${url}:`, error)
    return { error, data: undefined }
  }
}

export async function getEpcisInBounds(bounds: LngLatBounds): Promise<EpciInfo[]> {
  const sw = bounds.getSouthWest()
  const ne = bounds.getNorthEast()

  const url = `https://geo.api.gouv.fr/epcis?geometry=polygon&lon=${sw.lng}&lat=${sw.lat}&lon=${ne.lng}&lat=${ne.lat}&format=json&fields=code,nom,codeDepartement,codeRegion,population`

  const { data, error } = await fetchExternalApi<EpciInfo[]>(url)
  if (error || !data) {
    return []
  }

  return data
}

export async function getCadastreForEpci(codeEpci: string): Promise<CadastreResponse> {
  const url = `https://cadastre.data.gouv.fr/bundler/cadastre-etalab/epcis/${codeEpci}/geojson/parcelles`

  const { data, error } = await fetchExternalApi<CadastreResponse>(url)
  if (error || !data) {
    return {
      type: "FeatureCollection",
      features: []
    } as CadastreResponse
  }

  return data
}

export async function getCadastreInBounds(bounds: LngLatBounds): Promise<CadastreResponse> {
  const epcis = await getEpcisInBounds(bounds)
  const allFeatures: CadastreParcel[] = []

  await Promise.all(
    epcis.map(async (epci) => {
      const cadastreData = await getCadastreForEpci(epci.code)
      allFeatures.push(...cadastreData.features)
    })
  )

  return {
    type: "FeatureCollection",
    features: allFeatures
  } as CadastreResponse
}
