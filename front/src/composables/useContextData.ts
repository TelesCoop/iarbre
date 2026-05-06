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

export function useContextData(selectedDataTypeRef: Ref<DataType>) {
  const data = ref<ContextData>(null)
  const selectedDataType = selectedDataTypeRef

  const setData = async (
    featureId: string | number,
    indexValue?: string | number,
    sourceValues?: any,
    vulnScoreDay?: number,
    vulnScoreNight?: number,
    lat?: number,
    lng?: number
  ) => {
    if (!featureId) return null
    const stringId = String(featureId)

    let newData: ContextData = null

    if (indexValue === undefined) {
      newData = await getTileDetails(stringId, selectedDataType.value)

      if (!newData) {
        return
      }
    } else if (selectedDataType.value === DataType.BIOSPHERE_FUNCTIONAL_INTEGRITY) {
      const landCoverData =
        lat !== undefined && lng !== undefined ? await getBiosphereLandCoverAtPoint(lat, lng) : null
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
