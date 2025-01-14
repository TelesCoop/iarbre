export enum Layout {
  Default = "Default"
}

export const FULL_BASE_API_URL =
  import.meta.env.VITE_BASE_API_URL || `${window.location.origin}/api`

export const MIN_ZOOM = 12
export const MAX_ZOOM = 20
