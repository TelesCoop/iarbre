function getApiRootUrl(): string {
  return import.meta.env.VITE_BASE_API_URL || "http://localhost:8000/api"
}

/** Public API: stable contract, also used by third parties. */
export function getPublicApiUrl(): string {
  return `${getApiRootUrl()}/v1`
}

/** Internal API: routes serving this frontend only. */
export function getAppApiUrl(): string {
  return `${getApiRootUrl()}/app`
}

type MyHeaders = { [key: string]: string }

function getHeaders(withCsrfCookie = false): MyHeaders {
  const cookie = document.cookie
  const headers: MyHeaders = { cookie: cookie, "Content-Type": "application/json" }
  if (withCsrfCookie) {
    const csfrToken = getCsrfCookie()
    if (csfrToken) {
      headers["X-CSRFTOKEN"] = csfrToken
    }
  }
  return headers
}

function getCsrfCookie() {
  const cookie = document.cookie
  if (!cookie) {
    return null
  }
  const csfrRow = cookie.split("; ").find((row) => row.startsWith("csrftoken="))
  if (!csfrRow) {
    return null
  }
  return csfrRow.split("=")[1]
}

async function apiRequestWithCsrfToken<Type>(
  baseUrl: string,
  path: string,
  method: string,
  payload = {},
  onErrorMessage: string = ""
): Promise<{ data: Type | undefined; error: unknown }> {
  try {
    const response = await fetch(`${baseUrl}/${path}`, {
      method: method,
      body: JSON.stringify(payload),
      credentials: "include",
      headers: getHeaders(true)
    })

    if (!response.headers.get("content-type")?.includes("application/json")) {
      if (response.status >= 400) {
        throw response
      }

      return { data: undefined, error: undefined }
    }

    const data = await response.json()

    if (response.status >= 400) {
      // noinspection ExceptionCaughtLocallyJS
      throw data
    }

    return { data, error: undefined }
  } catch (error: unknown) {
    if (onErrorMessage) {
      console.error(error)
    }
    return { error, data: undefined }
  }
}

async function apiGet<Type>(
  baseUrl: string,
  path: string,
  onErrorMessage: string = ""
): Promise<{ data: Type | undefined; error: unknown }> {
  try {
    const response = await fetch(`${baseUrl}/${path}`, {
      method: "GET",
      credentials: "include",
      headers: getHeaders()
    })
    const data = await response.json()
    if (response.status >= 400) {
      // noinspection ExceptionCaughtLocallyJS
      throw data
    }
    return { data, error: undefined }
  } catch (error) {
    if (onErrorMessage) {
      console.error(error)
    }
    return { error, data: undefined }
  }
}

export async function useApiPost<Type>(path: string, payload = {}, onErrorMessage: string = "") {
  return apiRequestWithCsrfToken<Type>(getPublicApiUrl(), path, "POST", payload, onErrorMessage)
}

export async function useApiGet<Type>(path: string, onErrorMessage: string = "") {
  return apiGet<Type>(getPublicApiUrl(), path, onErrorMessage)
}

export async function useAppApiPost<Type>(path: string, payload = {}, onErrorMessage: string = "") {
  return apiRequestWithCsrfToken<Type>(getAppApiUrl(), path, "POST", payload, onErrorMessage)
}

export async function useAppApiGet<Type>(path: string, onErrorMessage: string = "") {
  return apiGet<Type>(getAppApiUrl(), path, onErrorMessage)
}
