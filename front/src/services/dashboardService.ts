import { useApiGet, useApiPost, useApiPostForBlob } from "@/api"
import type { DashboardData } from "@/types/dashboard"
import type { ZonePolygon } from "@/stores/zone"

export async function fetchDashboard(params?: {
  cityCode?: string
}): Promise<{ data: DashboardData | undefined; error: unknown }> {
  const query = params?.cityCode ? `?city_code=${params.cityCode}` : ""
  return useApiGet<DashboardData>(`dashboard/${query}`)
}

export async function fetchDashboardForZone(
  geometry: ZonePolygon
): Promise<{ data: DashboardData | undefined; error: unknown }> {
  return useApiPost<DashboardData>(
    "dashboard/in-polygon/",
    geometry,
    "Impossible de charger les données du dashboard pour cette zone"
  )
}

export async function exportDashboardPdf(
  html: string
): Promise<{ data: Blob | undefined; error: unknown }> {
  return useApiPostForBlob(
    "dashboard/export-pdf/",
    { html },
    "Impossible de générer le PDF du rapport",
    60_000
  )
}
