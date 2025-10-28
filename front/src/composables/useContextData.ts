import { ref } from "vue"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import type { ClimateData } from "@/types/climate"
import type { PlantabilityVulnerabilityData } from "@/types/vulnerability_plantability"
import type { IpaveData } from "@/types/ipave"
import { getTileDetails } from "@/services/tileService"
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToGeolevel } from "@/utils/enum"

export function useContextData() {
  const data = ref<
    | PlantabilityData
    | VulnerabilityData
    | ClimateData
    | PlantabilityVulnerabilityData
    | IpaveData
    | null
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
      mapStore.selectedDataType === DataType.IPAVE &&
      source_values !== undefined
    ) {
      // Handle IPAVE data: indice is the strate type, source_values contains surface
      if (!data.value) {
        data.value = {
          id: stringId,
          indice: String(indexValue),
          surface: source_values?.surface !== undefined ? +source_values.surface : 0,
          geolevel: DataTypeToGeolevel[mapStore.selectedDataType],
          datatype: DataType.IPAVE
        } as IpaveData
      } else if (data.value.datatype === DataType.IPAVE) {
        ;(data.value as IpaveData).indice = String(indexValue)
        ;(data.value as IpaveData).surface =
          source_values?.surface !== undefined ? +source_values.surface : 0
      }
    } else if (
      indexValue !== undefined &&
      (mapStore.selectedDataType === DataType.PLANTABILITY ||
        mapStore.selectedDataType === DataType.PLANTABILITY_VULNERABILITY) &&
      (source_values !== undefined ||
        mapStore.selectedDataType === DataType.PLANTABILITY_VULNERABILITY)
    ) {
      if (!data.value) {
        if (mapStore.selectedDataType === DataType.PLANTABILITY) {
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
        } else if (mapStore.selectedDataType === DataType.PLANTABILITY_VULNERABILITY) {
          data.value = {
            id: stringId,
            plantabilityNormalizedIndice: +indexValue,
            plantabilityIndice: +indexValue,
            vulnerability_indice_day: vuln_score_day !== undefined ? +vuln_score_day : 0,
            vulnerability_indice_night: vuln_score_night !== undefined ? +vuln_score_night : 0,
            details: source_values,
            geolevel: DataTypeToGeolevel[mapStore.selectedDataType],
            datatype: DataType.PLANTABILITY_VULNERABILITY,
            iris: 0,
            city: 0
          } as PlantabilityVulnerabilityData
        }
      } else if (data.value.datatype === DataType.PLANTABILITY) {
        ;(data.value as PlantabilityData).plantabilityNormalizedIndice = +indexValue
        ;(data.value as PlantabilityData).details = source_values
      } else if (data.value.datatype === DataType.PLANTABILITY_VULNERABILITY) {
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
