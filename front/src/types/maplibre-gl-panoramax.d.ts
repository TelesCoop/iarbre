declare module "maplibre-gl-panoramax" {
  export interface PanoramaxPictureAssets {
    hd?: string
    sd?: string
    thumb?: string
  }

  export interface PanoramaxPicture {
    id: string
    lon: number
    lat: number
    heading: number
    hasCompass: boolean
    hfov: number
    type: "equirectangular" | "flat"
    sequenceId: string
    rankInSequence?: number
    nextId: string | null
    prevId: string | null
    assets: PanoramaxPictureAssets
    producer?: string
    license?: string
    datetime?: string
    homeApi?: string
    exifPose?: { pitch?: number; roll?: number; yaw?: number } | null
    tiles?: unknown
  }

  export const META_API: string
  export const SOURCE_ID: string
  export const SEQUENCES_LAYER: string
  export const PICTURES_LAYER: string

  export function normalizeItem(feature: unknown): PanoramaxPicture
  export function getPicture(id: string, apiBase?: string): Promise<PanoramaxPicture>
  export function searchNearby(
    lon: number,
    lat: number,
    radiusM?: number,
    limit?: number,
    apiBase?: string
  ): Promise<PanoramaxPicture[]>
  export function getSequence(
    collectionId: string,
    limit?: number,
    apiBase?: string
  ): Promise<PanoramaxPicture[]>
}
