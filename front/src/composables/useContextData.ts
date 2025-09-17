import { ref } from "vue"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import type { ClimateData } from "@/types/climate"
import { getTileDetails } from "@/services/tileService"
import { useMapStore } from "@/stores/map"
import { DataType } from "@/utils/enum"

export function useContextData() {
  const data = ref<PlantabilityData | VulnerabilityData | ClimateData | null>(null)
  const mapStore = useMapStore()

  const setData = async (
    featureId: string | number,
    indexValue?: string | number,
    source_values?: any
  ) => {
    if (!featureId) return null
    const stringId = String(featureId)
    if (indexValue === undefined) {
      const tile = await getTileDetails(stringId, mapStore.selectedDataType)
      data.value = tile

      if (!tile) {
        data.value = null
        return
      }
    }
    if (
      indexValue !== undefined &&
      source_values !== undefined &&
      data.value &&
      data.value.datatype === DataType.PLANTABILITY
    ) {
      ;(data.value as PlantabilityData).plantabilityNormalizedIndice = +indexValue
      ;(data.value as PlantabilityData).details = source_values
    }
  }
  const removeData = () => {
    data.value = null
  }

  const toggleContextData = (featureId: string | number) => {
    if (!data.value) {
      setData(featureId)
    } else {
      removeData()
    }
  }
  return {
    data,
    setData,
    removeData,
    toggleContextData
  }
}
