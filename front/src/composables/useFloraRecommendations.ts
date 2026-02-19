import { ref } from "vue"
import type { FloraRecommendations } from "@/types/flora"
import { getFloraRecommendations } from "@/services/floraService"

export function useFloraRecommendations() {
  const recommendations = ref<FloraRecommendations | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchRecommendations = async (lat: number, lng: number, plantabilityScore?: number) => {
    loading.value = true
    error.value = null

    try {
      const result = await getFloraRecommendations(lat, lng, plantabilityScore)
      if (result) {
        recommendations.value = result
      } else {
        error.value = "Aucune donnée disponible pour cette localisation."
      }
    } catch {
      error.value = "Erreur lors de la récupération des recommandations."
    } finally {
      loading.value = false
    }
  }

  const clear = () => {
    recommendations.value = null
    error.value = null
  }

  return {
    recommendations,
    loading,
    error,
    fetchRecommendations,
    clear
  }
}
