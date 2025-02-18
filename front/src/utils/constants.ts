export enum Layout {
  Default = "Default"
}

const IS_LOCAL_DEV = import.meta.env.TELESCOOP_DEV === 1

export const FULL_BASE_API_URL = IS_LOCAL_DEV
  ? "http://localhost:8000/api"
  : import.meta.env.VITE_BASE_API_URL || `${window.location.origin}/api`

export const MIN_ZOOM = 12
export const MAX_ZOOM = 20
