import { ref, computed, type Ref } from "vue"
import { DataType, DataTypeToGeolevel } from "@/utils/enum"
import type { FilterSpecification, Map } from "maplibre-gl"
import { getLayerId } from "@/utils/map"

export function useMapFilters() {
  const filteredValues = ref<(number | string)[]>([])

  const hasActiveFilters = computed(() => filteredValues.value.length > 0)
  const activeFiltersCount = computed(() => filteredValues.value.length)

  const toggleFilter = (value: number | string) => {
    const index = filteredValues.value.indexOf(value)
    if (index > -1) {
      filteredValues.value.splice(index, 1)
    } else {
      filteredValues.value.push(value)
    }
  }

  const isFiltered = (value: number | string) => filteredValues.value.includes(value)

  const clearAllFilters = () => {
    filteredValues.value = []
  }

  const applyFilters = (
    mapInstancesByIds: Ref<Record<string, Map>>,
    selectedDataType: Ref<DataType>,
    vulnerabilityMode?: Ref<string>
  ) => {
    if (filteredValues.value.length === 0) {
      Object.values(mapInstancesByIds.value).forEach((mapInstance) => {
        const geoLevel = DataTypeToGeolevel[selectedDataType.value!]
        const layerId = getLayerId(selectedDataType.value!, geoLevel)
        mapInstance.setFilter(layerId, null)
      })
      return
    }

    Object.values(mapInstancesByIds.value).forEach((mapInstance) => {
      const geoLevel = DataTypeToGeolevel[selectedDataType.value!]
      const layerId = getLayerId(selectedDataType.value!, geoLevel)

      let filter = null
      const dataType = selectedDataType.value

      if (dataType === DataType.PLANTABILITY) {
        filter = ["in", ["floor", ["get", "indice"]], ["literal", filteredValues.value]]
      } else if (dataType === DataType.LOCAL_CLIMATE_ZONES) {
        filter = ["in", ["get", "indice"], ["literal", filteredValues.value]]
      } else if (dataType === DataType.VULNERABILITY) {
        filter = [
          "in",
          ["get", `indice_${vulnerabilityMode!.value}`],
          ["literal", filteredValues.value]
        ]
      }

      mapInstance.setFilter(layerId, filter as FilterSpecification)
    })
  }

  return {
    filteredValues,
    toggleFilter,
    clearAllFilters,
    applyFilters,
    hasActiveFilters,
    activeFiltersCount,
    isFiltered
  }
}
