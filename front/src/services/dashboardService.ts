import { useApiGet } from "@/api"
import type { DashboardData } from "@/types/dashboard"

export async function fetchDashboard(params?: {
  cityCode?: string
}): Promise<{ data: DashboardData | undefined; error: unknown }> {
  const query = params?.cityCode ? `?city_code=${params.cityCode}` : ""
  return useApiGet<DashboardData>(`dashboard/${query}`)
}
