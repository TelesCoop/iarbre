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
