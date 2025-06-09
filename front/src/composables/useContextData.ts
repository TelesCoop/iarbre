import { ref } from "vue"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import { getTileDetails } from "@/services/tileService"
import { useMapStore } from "@/stores/map"

export function useContextData() {
  const data = ref<PlantabilityData | VulnerabilityData | {} | null>(null)
  const mapStore = useMapStore()

  const setData = async (featureId: string | number) => {
    if (!featureId) return null
    const stringId = String(featureId)
    const tile = await getTileDetails(stringId, mapStore.selectedDataType)
    console.log(tile)
    if (!tile) {
      data.value = {}
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
