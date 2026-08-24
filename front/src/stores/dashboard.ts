import { defineStore } from "pinia"
import { ref, computed } from "vue"
import type { DashboardData, DashboardScale } from "@/types/dashboard"
import { fetchDashboard, fetchDashboardForZone } from "@/services/dashboardService"
import { useZoneStore } from "@/stores/zone"

interface CityOption {
  code: string
  name: string
}

export const useDashboardStore = defineStore("dashboard", () => {
  const zoneStore = useZoneStore()

  const selectedScale = ref<DashboardScale>("metropole")
  const selectedCityCode = ref<string | null>(null)
  const dashboardData = ref<DashboardData | null>(null)
  const cities = ref<CityOption[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const selectedCity = computed(() => {
    if (!selectedCityCode.value) return null
    return cities.value.find((c) => c.code === selectedCityCode.value) ?? null
  })

  const hasZone = computed(() => zoneStore.drawnGeometry !== null)

  async function fetchScaleData() {
    const params: { cityCode?: string } = {}
    if (selectedScale.value === "commune" && selectedCityCode.value) {
      params.cityCode = selectedCityCode.value
    }
    return fetchDashboard(params)
  }

  async function fetchZoneData() {
    if (!zoneStore.drawnGeometry) {
      return { data: undefined, error: "no-zone" }
    }
    return fetchDashboardForZone(zoneStore.drawnGeometry)
  }

  async function fetchDashboardData() {
    loading.value = true
    error.value = null

    try {
      const isZone = selectedScale.value === "zone"
      const result = isZone ? await fetchZoneData() : await fetchScaleData()

      if (result.error) {
        error.value = isZone
          ? "Impossible de charger les données pour cette zone"
          : "Impossible de charger les données du dashboard"
        return
      }

      dashboardData.value = result.data ?? null

      if (!isZone && result.data && cities.value.length === 0) {
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
    if (scale !== "commune") {
      selectedCityCode.value = null
    }
    fetchDashboardData()
  }

  function setCity(cityCode: string | null) {
    selectedCityCode.value = cityCode
    if (cityCode) {
      selectedScale.value = "commune"
    } else {
      selectedScale.value = "metropole"
    }
    fetchDashboardData()
  }

  return {
    selectedScale,
    selectedCityCode,
    dashboardData,
    cities,
    loading,
    error,
    selectedCity,
    hasZone,
    fetchDashboardData,
    setScale,
    setCity
  }
})
