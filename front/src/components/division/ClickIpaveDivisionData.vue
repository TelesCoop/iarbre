<script lang="ts" setup>
import { ref, watch } from "vue"
import { useMapStore } from "@/stores/map"
import { getCities } from "@/services/divisionService"
import type { City } from "@/types/division"
import IpaveDivisionData from "./IpaveDivisionData.vue"
import { ProgressSpinner } from "primevue"
import { useDebounceFn } from "@vueuse/core"

const mapStore = useMapStore()

const city = ref<City | null>(null)
const loading = ref(false)

const resetDivisionData = () => {
  city.value = null
}

const fetchDivisionData = async () => {
  const { lat, lng } = mapStore.clickCoordinates

  if (!lat || !lng) {
    return
  }

  loading.value = true

  try {
    // Create coordinates array [lng, lat]
    const coordinates: [number, number] = [lng, lat]

    // Fetch city that intersects with the click point
    const citiesData = await getCities({ geometry__intersects: coordinates })

    // Extract the first city from the results
    city.value = citiesData && citiesData.length > 0 ? citiesData[0] : null
  } catch (error) {
    console.error("Error fetching city data for IPAVE:", error)
    city.value = null
  } finally {
    loading.value = false
  }
}

const debouncedFetchDivisionData = useDebounceFn(() => {
  fetchDivisionData()
}, 300)

// Watch for changes in click coordinates
watch(
  () => mapStore.clickCoordinates,
  () => {
    resetDivisionData()
    debouncedFetchDivisionData()
  },
  { deep: true, immediate: true }
)
</script>

<template>
  <div>
    <div v-if="loading" class="flex justify-center p-4">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>
    <IpaveDivisionData v-else :city="city" />
  </div>
</template>
