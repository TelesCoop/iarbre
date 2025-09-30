import { ref } from "vue"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import type { ClimateData } from "@/types/climate"
import type { PlantabilityVulnerabilityData } from "@/types/vuln_plantability"
import { getTileDetails } from "@/services/tileService"
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToGeolevel } from "@/utils/enum"

export function useContextData() {
  const data = ref<
    PlantabilityData | VulnerabilityData | ClimateData | PlantabilityVulnerabilityData | null
  >(null)
  const mapStore = useMapStore()

  const setData = async (
    featureId: string | number,
    indexValue?: string | number,
    source_values?: any,
    vuln_score_day?: number,
    vuln_score_night?: number
  ) => {
    if (!featureId) return null
    const stringId = String(featureId)
    if (indexValue === undefined) {
      data.value = await getTileDetails(stringId, mapStore.selectedDataType)

      if (!data.value) {
        data.value = null
        return
      }
    } else if (
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
      } else if (data.value.datatype === DataType.PLANT_VULNERABILITY) {
        ;(data.value as PlantabilityVulnerabilityData).plantabilityNormalizedIndice = +indexValue
        ;(data.value as PlantabilityVulnerabilityData).details = source_values
        if (vuln_score_day !== undefined) {
          ;(data.value as PlantabilityVulnerabilityData).vulnerability_indice_day = +vuln_score_day
        }
        if (vuln_score_night !== undefined) {
          ;(data.value as PlantabilityVulnerabilityData).vulnerability_indice_night =
            +vuln_score_night
        }
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
