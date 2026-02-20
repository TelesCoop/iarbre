import { defineStore } from "pinia"
import { ref, computed } from "vue"
import type { DashboardData, DashboardScale } from "@/types/dashboard"
import { fetchDashboard } from "@/services/dashboardService"

interface CityOption {
  code: string
  name: string
}

export const useDashboardStore = defineStore("dashboard", () => {
  const selectedScale = ref<DashboardScale>("metropole")
  const selectedCityCode = ref<string | null>(null)
  const selectedIrisCode = ref<string | null>(null)
  const dashboardData = ref<DashboardData | null>(null)
  const cities = ref<CityOption[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const heatMode = ref<"day" | "night">("day")

  const selectedCity = computed(() => {
    if (!selectedCityCode.value) return null
    return cities.value.find((c) => c.code === selectedCityCode.value) ?? null
  })

  async function fetchDashboardData() {
    loading.value = true
    error.value = null

    try {
      const params: { cityCode?: string; irisCode?: string } = {}
      if (selectedScale.value === "commune" && selectedCityCode.value) {
        params.cityCode = selectedCityCode.value
      } else if (selectedScale.value === "iris" && selectedIrisCode.value) {
        params.irisCode = selectedIrisCode.value
      }

      const result = await fetchDashboard(params)

      if (result.error) {
        error.value = "Impossible de charger les données du dashboard"
        return
      }

      dashboardData.value = result.data ?? null

      if (result.data && cities.value.length === 0) {
        const divisions = result.data.plantability.distributionByDivision
        cities.value = divisions
          .map((d) => ({ code: d.code, name: d.name }))
          .sort((a, b) => a.name.localeCompare(b.name))
      }
    } finally {
      loading.value = false
    }
  }

  function setScale(scale: DashboardScale) {
    selectedScale.value = scale
    if (scale === "metropole") {
      selectedCityCode.value = null
      selectedIrisCode.value = null
    }
    fetchDashboardData()
  }

  function setCity(cityCode: string | null) {
    selectedCityCode.value = cityCode
    selectedIrisCode.value = null
    if (cityCode) {
      selectedScale.value = "commune"
    } else {
      selectedScale.value = "metropole"
    }
    fetchDashboardData()
  }

  function toggleHeatMode() {
    heatMode.value = heatMode.value === "day" ? "night" : "day"
  }

  return {
    selectedScale,
    selectedCityCode,
    selectedIrisCode,
    dashboardData,
    cities,
    loading,
    error,
    heatMode,
    selectedCity,
    fetchDashboardData,
    setScale,
    setCity,
    toggleHeatMode
  }
})
