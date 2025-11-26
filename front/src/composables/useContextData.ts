import { ref } from "vue"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import type { ClimateData } from "@/types/climate"
import type { PlantabilityVulnerabilityData } from "@/types/vulnerability_plantability"
import { getTileDetails } from "@/services/tileService"
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToGeolevel } from "@/utils/enum"

export function useContextData() {
  const data = ref<
    Array<PlantabilityData | VulnerabilityData | ClimateData | PlantabilityVulnerabilityData>
  >([])
  const mapStore = useMapStore()

  const setData = async (
    featureId: string | number,
    indexValue?: string | number,
    sourceValues?: any,
    vulnScoreDay?: number,
    vulnScoreNight?: number,
    replace: boolean = true
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
      newData = await getTileDetails(stringId, mapStore.selectedDataType)

      if (!newData) {
        return
      }
    } else if (
      indexValue !== undefined &&
      (mapStore.selectedDataType === DataType.PLANTABILITY ||
        mapStore.selectedDataType === DataType.PLANTABILITY_VULNERABILITY) &&
      (sourceValues !== undefined ||
        mapStore.selectedDataType === DataType.PLANTABILITY_VULNERABILITY)
    ) {
      if (mapStore.selectedDataType === DataType.PLANTABILITY) {
        newData = {
          id: stringId,
          plantabilityNormalizedIndice: +indexValue,
          plantabilityIndice: +indexValue,
          details: sourceValues,
          geolevel: DataTypeToGeolevel[mapStore.selectedDataType],
          datatype: DataType.PLANTABILITY,
          iris: 0,
          city: 0
        } as PlantabilityData
      } else if (mapStore.selectedDataType === DataType.PLANTABILITY_VULNERABILITY) {
        newData = {
          id: stringId,
          plantabilityNormalizedIndice: +indexValue,
          plantabilityIndice: +indexValue,
          vulnerabilityIndiceDay: vulnScoreDay !== undefined ? +vulnScoreDay : 0,
          vulnerabilityIndiceNight: vulnScoreNight !== undefined ? +vulnScoreNight : 0,
          details: sourceValues,
          geolevel: DataTypeToGeolevel[mapStore.selectedDataType],
          datatype: DataType.PLANTABILITY_VULNERABILITY,
          iris: 0,
          city: 0
        } as PlantabilityVulnerabilityData
      }
    }

    if (newData) {
      if (replace) {
        data.value = [newData]
      } else {
        // Vérifier si la tuile n'existe pas déjà dans le tableau
        const existingIndex = data.value.findIndex((item) => item.id === stringId)
        if (existingIndex >= 0) {
          data.value[existingIndex] = newData
        } else {
          data.value.push(newData)
        }
      }
    }
  }

  const setMultipleData = async (featureIds: Array<string | number>) => {
    const promises = featureIds.map(async (featureId) => {
      const stringId = String(featureId)
      const tileData = await getTileDetails(stringId, mapStore.selectedDataType)
      return tileData
    })

    const results = await Promise.all(promises)
    data.value = results.filter(
      (
        item
      ): item is
        | PlantabilityData
        | VulnerabilityData
        | ClimateData
        | PlantabilityVulnerabilityData => item !== null
    )
  }

  const removeData = () => {
    data.value = []
  }

  const toggleContextData = (featureId: string | number) => {
    if (data.value.length === 0) {
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
