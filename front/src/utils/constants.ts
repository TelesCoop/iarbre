export enum Layout {
  Default = "Default"
}

export const FULL_BASE_API_URL = import.meta.env.PROD
  ? `${window.location.origin}/api`
  : "http://localhost:8000/api"

export const MIN_ZOOM = 12
export const MAX_ZOOM = 20
