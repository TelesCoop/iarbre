import { useApiGet } from "@/api"
import type { FeatureCollection } from "geojson"

export const getCityBoundaries = async (): Promise<FeatureCollection | null> => {
  try {
    const req = await useApiGet<FeatureCollection>(
      "boundaries/cities/",
      "Impossible de récupérer les contours des communes"
    )
    return req.data || null
  } catch (error) {
    console.error("Error retrieving city boundaries:", error)
    return null
  }
}
