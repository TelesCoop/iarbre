import { useApiGet } from "@/api"
import type { City, Iris } from "@/types/division"
import { buildQueryString, type QueryParams } from "@/utils/queryParams"

interface DivisionQueryParams extends QueryParams {
  code?: string
  code__in?: string[]
  /** Coordinates [lng, lat] to find divisions that intersect with the point */
  geometry__intersects?: [number, number]
}

/**
 * Retrieves cities based on query parameters.
 * @param params - Query parameters (code, code__in, geometry__intersects)
 * @returns Promise with array of cities or null
 *
 * @example
 * // Get cities by code
 * getCities({ code: "69123" })
 *
 * @example
 * // Get cities by multiple codes
 * getCities({ code__in: ["69123", "69001"] })
 *
 * @example
 * // Get cities at coordinates
 * getCities({ geometry__intersects: [4.792, 45.756] })
 */
export const getCities = async (params?: DivisionQueryParams): Promise<City[] | null> => {
  try {
    const queryString = params ? buildQueryString(params) : ""
    const req = await useApiGet<City[]>(
      `cities/${queryString}`,
      "Impossible de récupérer les données des villes"
    )
    return req.data || null
  } catch (error) {
    console.error("Error retrieving cities:", error)
    return null
  }
}

/**
 * Retrieves a single city by ID.
 * @param id - The city ID
 * @returns Promise with the city or null
 */
export const getCity = async (id: number): Promise<City | null> => {
  try {
    const req = await useApiGet<City>(
      `cities/${id}/`,
      `Impossible de récupérer la ville avec l'id ${id}`
    )
    return req.data || null
  } catch (error) {
    console.error("Error retrieving city:", error)
    return null
  }
}

/**
 * Retrieves IRIS based on query parameters.
 * @param params - Query parameters (code, code__in, geometry__intersects)
 * @returns Promise with array of IRIS or null
 *
 * @example
 * // Get IRIS by code
 * getIrisList({ code: "691230101" })
 *
 * @example
 * // Get IRIS by multiple codes
 * getIrisList({ code__in: ["691230101", "691230102"] })
 *
 * @example
 * // Get IRIS at coordinates
 * getIrisList({ geometry__intersects: [4.792, 45.756] })
 */
export const getIrisList = async (params?: DivisionQueryParams): Promise<Iris[] | null> => {
  try {
    const queryString = params ? buildQueryString(params) : ""
    const req = await useApiGet<Iris[]>(
      `iris/${queryString}`,
      "Impossible de récupérer les données des IRIS"
    )
    return req.data || null
  } catch (error) {
    console.error("Error retrieving IRIS:", error)
    return null
  }
}

/**
 * Retrieves a single IRIS by ID.
 * @param id - The IRIS ID
 * @returns Promise with the IRIS or null
 */
export const getIris = async (id: number): Promise<Iris | null> => {
  try {
    const req = await useApiGet<Iris>(
      `iris/${id}/`,
      `Impossible de récupérer l'IRIS avec l'id ${id}`
    )
    return req.data || null
  } catch (error) {
    console.error("Error retrieving IRIS:", error)
    return null
  }
}
