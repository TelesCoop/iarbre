<script lang="ts" setup>
import { ref, watch } from "vue"
import { useMapStore } from "@/stores/map"
import { getCities, getIrisList } from "@/services/divisionService"
import type { City, Iris } from "@/types/division"
import PlantabilityDivisionData from "./PlantabilityDivisionData.vue"
import { ProgressSpinner } from "primevue"
import { useDebounceFn } from "@vueuse/core"
const mapStore = useMapStore()

const city = ref<City | null>(null)
const iris = ref<Iris | null>(null)
const loading = ref(false)

const resetDivisionData = () => {
  city.value = null
  iris.value = null
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

    // Fetch cities and iris that intersect with the click point
    const [citiesData, irisData] = await Promise.all([
      getCities({ geometry__intersects: coordinates }),
      getIrisList({ geometry__intersects: coordinates })
    ])

    // Extract the first city and iris from the results
    city.value = citiesData && citiesData.length > 0 ? citiesData[0] : null
    iris.value = irisData && irisData.length > 0 ? irisData[0] : null
  } catch (error) {
    console.error("Error fetching division data:", error)
    city.value = null
    iris.value = null
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
    <PlantabilityDivisionData v-else :city="city" :iris="iris" />
  </div>
</template>
