import { ref, computed, type Ref } from "vue"
import { DataType, DataTypeToGeolevel } from "@/utils/enum"
import type { Map } from "maplibre-gl"
import { getLayerId } from "@/utils/map"

export function useMapFilters() {
  const filteredScores = ref<number[]>([])
  const filteredZones = ref<string[]>([])
  const filteredVulnerability = ref<number[]>([])

  const hasActiveFilters = computed(() => {
    return (
      filteredScores.value.length > 0 ||
      filteredZones.value.length > 0 ||
      filteredVulnerability.value.length > 0
    )
  })

  const getActiveFiltersCount = computed(() => {
    return (
      filteredScores.value.length + filteredZones.value.length + filteredVulnerability.value.length
    )
  })

  const getFilterSummary = computed(() => {
    const counts = []
    if (filteredScores.value.length > 0) {
      counts.push(
        `${filteredScores.value.length} score${filteredScores.value.length > 1 ? "s" : ""}`
      )
    }
    if (filteredZones.value.length > 0) {
      counts.push(`${filteredZones.value.length} zone${filteredZones.value.length > 1 ? "s" : ""}`)
    }
    if (filteredVulnerability.value.length > 0) {
      counts.push(
        `${filteredVulnerability.value.length} niveau${filteredVulnerability.value.length > 1 ? "x" : ""}`
      )
    }
    return counts.join(", ")
  })

  const toggleScoreFilter = (score: number) => {
    const index = filteredScores.value.indexOf(score)
    if (index > -1) {
      filteredScores.value.splice(index, 1)
    } else {
      filteredScores.value.push(score)
    }
  }

  const toggleZoneFilter = (zone: string) => {
    const index = filteredZones.value.indexOf(zone)
    if (index > -1) {
      filteredZones.value.splice(index, 1)
    } else {
      filteredZones.value.push(zone)
    }
  }

  const toggleVulnerabilityFilter = (level: number) => {
    const index = filteredVulnerability.value.indexOf(level)
    if (index > -1) {
      filteredVulnerability.value.splice(index, 1)
    } else {
      filteredVulnerability.value.push(level)
    }
  }

  const isScoreFiltered = (score: number) => {
    return filteredScores.value.includes(score)
  }

  const isZoneFiltered = (zone: string) => {
    return filteredZones.value.includes(zone)
  }

  const isVulnerabilityFiltered = (level: number) => {
    return filteredVulnerability.value.includes(level)
  }

  const clearAllFilters = () => {
    filteredScores.value.length = 0
    filteredZones.value.length = 0
    filteredVulnerability.value.length = 0
  }

  const applyFilters = (
    mapInstancesByIds: Ref<Record<string, Map>>,
    selectedDataType: Ref<DataType>,
    vulnerabilityMode: Ref<string>
  ) => {
    Object.keys(mapInstancesByIds.value).forEach((mapId) => {
      const mapInstance = mapInstancesByIds.value[mapId]
      const geoLevel = DataTypeToGeolevel[selectedDataType.value!]
      const layerId = getLayerId(selectedDataType.value!, geoLevel)

      let filterExpression: any = null

      if (selectedDataType.value === DataType.PLANTABILITY && filteredScores.value.length > 0) {
        filterExpression = ["in", ["floor", ["get", "indice"]], ["literal", filteredScores.value]]
      } else if (
        selectedDataType.value === DataType.LOCAL_CLIMATE_ZONES &&
        filteredZones.value.length > 0
      ) {
        filterExpression = ["in", ["get", "indice"], ["literal", filteredZones.value]]
      } else if (
        selectedDataType.value === DataType.VULNERABILITY &&
        filteredVulnerability.value.length > 0
      ) {
        filterExpression = [
          "in",
          ["get", `indice_${vulnerabilityMode.value}`],
          ["literal", filteredVulnerability.value]
        ]
      }

      mapInstance.setFilter(layerId, filterExpression)
    })
  }

  return {
    filteredScores,
    filteredZones,
    filteredVulnerability,

    toggleScoreFilter,
    toggleZoneFilter,
    toggleVulnerabilityFilter,

    isScoreFiltered,
    isZoneFiltered,
    isVulnerabilityFiltered,

    clearAllFilters,
    applyFilters,

    hasActiveFilters,
    getActiveFiltersCount,
    getFilterSummary
  }
}
