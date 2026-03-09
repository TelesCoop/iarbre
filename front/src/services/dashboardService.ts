import { useApiGet } from "@/api"
import type { DashboardData } from "@/types/dashboard"

export async function fetchDashboard(params?: {
  cityCode?: string
  irisCode?: string
}): Promise<{ data: DashboardData | undefined; error: unknown }> {
  const queryParts: string[] = []
  if (params?.cityCode) {
    queryParts.push(`city_code=${params.cityCode}`)
  }
  if (params?.irisCode) {
    queryParts.push(`iris_code=${params.irisCode}`)
  }
  const query = queryParts.length > 0 ? `?${queryParts.join("&")}` : ""
  return useApiGet<DashboardData>(`dashboard/${query}`)
}
