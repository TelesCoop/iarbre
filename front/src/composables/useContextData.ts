import { ref, type Ref } from "vue"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import type { ClimateData } from "@/types/climate"
import type { PlantabilityVulnerabilityData } from "@/types/vulnerability_plantability"
import { getTileDetails } from "@/services/tileService"
import { DataType, DataTypeToGeolevel } from "@/utils/enum"

export function useContextData(selectedDataTypeRef: Ref<DataType>) {
  const data = ref<
    PlantabilityData | VulnerabilityData | ClimateData | PlantabilityVulnerabilityData | null
  >(null)
  const selectedDataType = selectedDataTypeRef

  const setData = async (
    featureId: string | number,
    indexValue?: string | number,
    sourceValues?: any,
    vulnScoreDay?: number,
    vulnScoreNight?: number
  ) => {
    if (!featureId) return null
    const stringId = String(featureId)

    let newData:
      | PlantabilityData
      | VulnerabilityData
      | ClimateData
      | PlantabilityVulnerabilityData
      | null = null

    if (indexValue === undefined) {
      newData = await getTileDetails(stringId, selectedDataType.value)

      if (!newData) {
        return
      }
    } else if (
      indexValue !== undefined &&
      (selectedDataType.value === DataType.PLANTABILITY ||
        selectedDataType.value === DataType.PLANTABILITY_VULNERABILITY) &&
      (sourceValues !== undefined || selectedDataType.value === DataType.PLANTABILITY_VULNERABILITY)
    ) {
      if (selectedDataType.value === DataType.PLANTABILITY) {
        newData = {
          id: stringId,
          plantabilityNormalizedIndice: +indexValue,
          plantabilityIndice: +indexValue,
          details: sourceValues,
          geolevel: DataTypeToGeolevel[selectedDataType.value],
          datatype: DataType.PLANTABILITY,
          iris: 0,
          city: 0
        } as PlantabilityData
      } else if (selectedDataType.value === DataType.PLANTABILITY_VULNERABILITY) {
        newData = {
          id: stringId,
          plantabilityNormalizedIndice: +indexValue,
          plantabilityIndice: +indexValue,
          vulnerabilityIndiceDay: vulnScoreDay !== undefined ? +vulnScoreDay : 0,
          vulnerabilityIndiceNight: vulnScoreNight !== undefined ? +vulnScoreNight : 0,
          details: sourceValues,
          geolevel: DataTypeToGeolevel[selectedDataType.value],
          datatype: DataType.PLANTABILITY_VULNERABILITY,
          iris: 0,
          city: 0
        } as PlantabilityVulnerabilityData
      }
    }

    if (newData) {
      data.value = newData
    }
  }

  const setMultipleData = async (featureIds: Array<string | number>) => {
    if (featureIds.length === 0) return

    const stringId = String(featureIds[0])
    const tileData = await getTileDetails(stringId, selectedDataType.value)
    data.value = tileData
  }

  const removeData = () => {
    data.value = null
  }

  const toggleContextData = (featureId: string | number) => {
    if (data.value === null) {
      setData(featureId)
    } else {
      removeData()
    }
  }

  return {
    data,
    setData,
    setMultipleData,
    removeData,
    toggleContextData
  }
}
