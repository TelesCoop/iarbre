import { getFullBaseApiUrl } from "@/api"

export async function fetchExportScope(
  token: string
): Promise<Record<string, unknown> | null> {
  const res = await fetch(`${getFullBaseApiUrl()}/dashboard/export-scope/${token}/`, {
    credentials: "include"
  })
  if (!res.ok) return null
  return res.json()
}

export async function exportDashboardPdf(
  scope: {
    scale: string
    cityCode?: string | null
    geometry?: unknown
  },
  signal: AbortSignal
): Promise<Blob> {
  const body: Record<string, unknown> = { scale: scope.scale }
  if (scope.cityCode) body.city_code = scope.cityCode
  if (scope.geometry) body.geometry = scope.geometry

  const res = await fetch(`${getFullBaseApiUrl()}/dashboard/export-pdf/`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal
  })
  if (!res.ok) throw new Error(`export failed: ${res.status}`)
  return res.blob()
}
