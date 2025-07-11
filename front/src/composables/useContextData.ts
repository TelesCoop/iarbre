import { ref } from "vue"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import type { ClimateData } from "@/types/climate"
import { getTileDetails } from "@/services/tileService"
import { useMapStore } from "@/stores/map"

export function useContextData() {
  const data = ref<PlantabilityData | VulnerabilityData | ClimateData | null>(null)
  const mapStore = useMapStore()

  const setData = async (featureId: string | number) => {
    if (!featureId) return null
    const stringId = String(featureId)
    const tile = await getTileDetails(stringId, mapStore.selectedDataType)
    if (!tile) {
      data.value = null
      return
    }

    data.value = tile
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
