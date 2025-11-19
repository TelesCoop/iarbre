import { ref } from "vue"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import type { ClimateData } from "@/types/climate"
import type { PlantabilityVulnerabilityData } from "@/types/vulnerability_plantability"
import { getTileDetails } from "@/services/tileService"
import { useMapStore } from "@/stores/map"
import { DataType, DataTypeToGeolevel } from "@/utils/enum"

export type ContextDataItem = {
  data: PlantabilityData | VulnerabilityData | ClimateData | PlantabilityVulnerabilityData
  coordinates: { lat: number; lng: number }
}

export function useContextData() {
  // Current context data - the most recent click, displayed in full
  const currentContextData = ref<ContextDataItem | null>(null)
  // Selected context data - list of items the user wants to keep for comparison
  const selectedContextData = ref<ContextDataItem[]>([])
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

    let newData: ContextDataItem | null = null

    if (indexValue === undefined) {
      newData = await getTileDetails(stringId, mapStore.selectedDataType)

      if (!newData) {
        return
      }
    } else if (
      indexValue !== undefined &&
      (mapStore.selectedDataType === DataType.PLANTABILITY ||
        mapStore.selectedDataType === DataType.PLANTABILITY_VULNERABILITY) &&
      (source_values !== undefined ||
        mapStore.selectedDataType === DataType.PLANTABILITY_VULNERABILITY)
    ) {
      if (mapStore.selectedDataType === DataType.PLANTABILITY) {
        newData = {
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
        newData = {
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
    }

    // Set new data as current
    if (newData) {
      // Get current coordinates from the map store
      const coordinates = { ...mapStore.clickCoordinates }

      // Set the new item as current (don't automatically move previous to selected)
      currentContextData.value = { data: newData, coordinates }
    }
  }

  const addCurrentToSelected = () => {
    if (!currentContextData.value) return

    // Check if it's not already in the selected list
    const existsInSelected = selectedContextData.value.some(
      (item) => item.data.id === currentContextData.value!.data.id
    )
    if (!existsInSelected) {
      selectedContextData.value.push(currentContextData.value)
    }
  }

  const removeData = (itemId?: string) => {
    if (itemId) {
      // Remove specific item from selected list by id
      const index = selectedContextData.value.findIndex((item) => item.data.id === itemId)
      if (index !== -1) {
        selectedContextData.value.splice(index, 1)
      }
      // Also check if it's the current item
      if (currentContextData.value && currentContextData.value.data.id === itemId) {
        currentContextData.value = null
      }
    } else {
      // Remove all items
      currentContextData.value = null
      selectedContextData.value = []
    }
  }

  const toggleContextData = (featureId: string | number) => {
    const stringId = String(featureId)
    const isCurrent = currentContextData.value?.data.id === stringId
    const existsInSelected = selectedContextData.value.some((item) => item.data.id === stringId)

    if (isCurrent || existsInSelected) {
      // Item exists, remove it
      removeData(stringId)
    } else {
      // Item doesn't exist, add it
      setData(featureId)
    }
  }

  return {
    currentContextData,
    selectedContextData,
    setData,
    removeData,
    toggleContextData,
    addCurrentToSelected
  }
}
