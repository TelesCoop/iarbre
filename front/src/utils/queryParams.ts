/**
 * Utility functions for building query parameters for API requests.
 */

export interface QueryParams {
  [key: string]: string | string[] | number | boolean | undefined | number[]
}

/**
 * Builds a query string from an object of parameters.
 * Handles arrays by joining them with commas.
 *
 * @param params - Object containing query parameters
 * @returns Query string with leading '?' or empty string if no params
 *
 * @example
 * buildQueryString({ code: "69123" })
 * // Returns: "?code=69123"
 *
 * @example
 * buildQueryString({ code__in: ["69123", "69001"] })
 * // Returns: "?code__in=69123,69001"
 *
 * @example
 * buildQueryString({ code: "69123", active: true })
 * // Returns: "?code=69123&active=true"
 */
export function buildQueryString(params: QueryParams): string {
  const searchParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      if (Array.isArray(value)) {
        // For array values, join with comma (e.g., code__in)
        searchParams.append(key, value.join(","))
      } else {
        // Convert to string for other types
        searchParams.append(key, String(value))
      }
    }
  })

  const queryString = searchParams.toString()
  return queryString ? `?${queryString}` : ""
}
