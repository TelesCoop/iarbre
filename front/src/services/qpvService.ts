import { useApiGet } from "@/api"
import type { FeatureCollection } from "geojson"

export const getQPVData = async (): Promise<FeatureCollection | null> => {
  try {
    const req = await useApiGet<FeatureCollection>(
      "qpv/",
      "Impossible de récupérer les données QPV"
    )
    return req.data || null
  } catch (error) {
    console.error("Error retrieving QPV data:", error)
    return null
  }
}
