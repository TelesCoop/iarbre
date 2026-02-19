import { useApiGet } from "@/api"
import type { FloraRecommendations } from "@/types/flora"

export const getFloraRecommendations = async (
  lat: number,
  lng: number,
  plantabilityScore?: number
): Promise<FloraRecommendations | null> => {
  try {
    let url = `flora/recommendations/?lat=${lat}&lng=${lng}`
    if (plantabilityScore !== undefined) {
      url += `&plantability_score=${plantabilityScore}`
    }
    const req = await useApiGet<FloraRecommendations>(
      url,
      "Unable to retrieve flora recommendations"
    )
    return req.data ?? null
  } catch (error) {
    console.error("Error retrieving flora recommendations:", error)
    return null
  }
}
