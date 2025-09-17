import { ref } from "vue"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import type { ClimateData } from "@/types/climate"
import { getTileDetails } from "@/services/tileService"
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToGeolevel } from "@/utils/enum"

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
      mapStore.selectedDataType === DataType.PLANTABILITY
    ) {
      if (!data.value) {
        data.value = {
          id: stringId,
          plantabilityNormalizedIndice: +indexValue,
          plantabilityIndice: +indexValue,
          details: source_values,
          geolevel: DataTypeToGeolevel[mapStore.selectedDataType],
          datatype: DataType.PLANTABILITY,
          iris: 0,
          city: 0
        } as PlantabilityData
      } else if (data.value.datatype === DataType.PLANTABILITY) {
        ;(data.value as PlantabilityData).plantabilityNormalizedIndice = +indexValue
        ;(data.value as PlantabilityData).details = source_values
      }
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
