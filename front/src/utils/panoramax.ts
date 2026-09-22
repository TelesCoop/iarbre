import type { PanoramaxPicture } from "maplibre-gl-panoramax"

export const PANORAMAX_API = "https://api.panoramax.xyz/api"
export const PANORAMAX_HOME_URL = "https://panoramax.fr"
export const PANORAMAX_ATTRIBUTION = `© <a href="${PANORAMAX_HOME_URL}" target="_blank" rel="noopener">Panoramax</a>`

export const PANORAMAX_SOURCE_ID = "panoramax-source"
export const PANORAMAX_SEQUENCES_LAYER = "panoramax-sequences"
export const PANORAMAX_PICTURES_LAYER = "panoramax-pictures"

/** The tile server answers 400 above z15; MapLibre overzooms from there. */
export const PANORAMAX_SOURCE_MAX_ZOOM = 15

/** Coverage tiles weigh ~1.9 MB at z10 against ~0.4 MB at z13 over Lyon. */
export const PANORAMAX_SEQUENCES_MIN_ZOOM = 13

export const PANORAMAX_PICTURES_MIN_ZOOM = 17
export const PANORAMAX_ACTIVATION_ZOOM = 17

export const buildPanoramaxPictureUrl = (picture: PanoramaxPicture): string | null => {
  const asset = picture.assets?.sd ?? picture.assets?.hd ?? picture.assets?.thumb
  if (!asset) return null
  try {
    return `${new URL(asset).origin}/#focus=pic&pic=${picture.id}`
  } catch {
    return null
  }
}

export const formatPanoramaxDate = (datetime?: string): string => {
  if (!datetime) return ""
  const date = new Date(datetime)
  if (Number.isNaN(date.getTime())) return ""
  return date.toLocaleDateString("fr-FR", { day: "2-digit", month: "long", year: "numeric" })
}
