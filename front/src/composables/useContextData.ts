import { ref, type Ref } from "vue"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import type { ClimateData } from "@/types/climate"
import type { PlantabilityVulnerabilityData } from "@/types/vulnerability_plantability"
import type { BiosphereIntegrityData } from "@/types/biosphereIntegrity"
import type { VegetationData } from "@/types/vegetation"
import { getTileDetails } from "@/services/tileService"
import { getBiosphereLandCoverAtPoint } from "@/services/biosphereService"
import { DataType, DataTypeToGeolevel, GeoLevel } from "@/utils/enum"

type ContextData =
  | PlantabilityData
  | VulnerabilityData
  | ClimateData
  | PlantabilityVulnerabilityData
  | BiosphereIntegrityData
  | VegetationData
  | null

type SetDataArgs = [
  featureId: string | number,
  indexValue?: string | number,
  sourceValues?: any,
  vulnScoreDay?: number,
  vulnScoreNight?: number,
  lat?: number,
  lng?: number
]

export function useContextData(selectedDataTypeRef: Ref<DataType>) {
  const data = ref<ContextData>(null)
  const error = ref(false)
  const lastArgs = ref<SetDataArgs | null>(null)
  const selectedDataType = selectedDataTypeRef

  const setData = async (...args: SetDataArgs) => {
    const [featureId, indexValue, sourceValues, vulnScoreDay, vulnScoreNight, lat, lng] = args
    if (!featureId) return null
    lastArgs.value = args
    error.value = false
    const stringId = String(featureId)

    let newData: ContextData = null

    try {
      if (indexValue === undefined) {
        newData = await getTileDetails(stringId, selectedDataType.value)

        if (!newData) {
          return
        }
      } else if (selectedDataType.value === DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY) {
        const landCoverData =
          lat !== undefined && lng !== undefined
            ? await getBiosphereLandCoverAtPoint(lat, lng)
            : null
        newData = {
          id: stringId,
          indice: +indexValue,
          geolevel: GeoLevel.BIOSPHERE_FUNCTIONAL_INTEGRITY,
          datatype: DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY,
          landCovers: landCoverData ?? null
        } as BiosphereIntegrityData
      } else if (
        indexValue !== undefined &&
        (selectedDataType.value === DataType.PLANTABILITY ||
          selectedDataType.value === DataType.PLANTABILITY_VULNERABILITY) &&
        (sourceValues !== undefined ||
          selectedDataType.value === DataType.PLANTABILITY_VULNERABILITY)
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
    } catch (e) {
      console.error("Error retrieving context data:", e)
      error.value = true
    }
  }

  const setMultipleData = async (featureIds: Array<string | number>) => {
    if (featureIds.length === 0) return
    error.value = false

    try {
      const stringId = String(featureIds[0])
      data.value = await getTileDetails(stringId, selectedDataType.value)
    } catch (e) {
      console.error("Error retrieving context data:", e)
      error.value = true
    }
  }

  const removeData = () => {
    data.value = null
    error.value = false
    lastArgs.value = null
  }

  const retry = () => {
    if (lastArgs.value) setData(...lastArgs.value)
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
    error,
    setData,
    setMultipleData,
    removeData,
    retry,
    toggleContextData
  }
}
