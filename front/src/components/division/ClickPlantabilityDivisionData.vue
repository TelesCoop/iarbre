<script lang="ts" setup>
import { ref, watch, computed } from "vue"
import { useMapStore } from "@/stores/map"
import { getCities, getIrisList } from "@/services/divisionService"
import type { City, Iris } from "@/types/division"
import type { PlantabilityData } from "@/types/plantability"
import PlantabilityDivisionData from "./PlantabilityDivisionData.vue"
import { ProgressSpinner } from "primevue"
import { useDebounceFn } from "@vueuse/core"

interface ClickPlantabilityDivisionDataProps {
  plantabilityData?: PlantabilityData | null
}

const props = withDefaults(defineProps<ClickPlantabilityDivisionDataProps>(), {
  plantabilityData: null
})

const mapStore = useMapStore()

const cities = ref<City[]>([])
const irisList = ref<Iris[]>([])
const loading = ref(false)

// Extract codes from plantability data if available
const cityCodes = computed(() => {
  console.log("plantabilityData:", props.plantabilityData)
  console.log("cityCodes from props:", props.plantabilityData?.cityCodes)
  return props.plantabilityData?.cityCodes || []
})
const irisCodes = computed(() => {
  console.log("irisCodes from props:", props.plantabilityData?.irisCodes)
  return props.plantabilityData?.irisCodes || []
})

const resetDivisionData = () => {
  cities.value = []
  irisList.value = []
}

const fetchDivisionData = async () => {
  const { lat, lng } = mapStore.clickCoordinates
  console.log("fetchDivisionData called with coordinates:", { lat, lng })

  if (!lat || !lng) {
    console.log("No coordinates, skipping fetch")
    return
  }

  loading.value = true

  try {
    // If we have codes from polygon selection, use them
    if (cityCodes.value.length > 0 || irisCodes.value.length > 0) {
      console.log("Using codes to fetch divisions:", {
        cityCodes: cityCodes.value,
        irisCodes: irisCodes.value
      })
      const [citiesData, irisData] = await Promise.all([
        cityCodes.value.length > 0
          ? getCities({ code__in: cityCodes.value })
          : Promise.resolve(null),
        irisCodes.value.length > 0
          ? getIrisList({ code__in: irisCodes.value })
          : Promise.resolve(null)
      ])

      console.log("Fetched by codes - cities:", citiesData, "iris:", irisData)
      cities.value = citiesData || []
      irisList.value = irisData || []
    } else {
      // Fallback to point intersection for single tile selection
      console.log("Using geometry__intersects for single tile")
      const coordinates: [number, number] = [lng, lat]

      const [citiesData, irisData] = await Promise.all([
        getCities({ geometry__intersects: coordinates }),
        getIrisList({ geometry__intersects: coordinates })
      ])

      console.log("Fetched by intersection - cities:", citiesData, "iris:", irisData)
      cities.value = citiesData || []
      irisList.value = irisData || []
    }
  } catch (error) {
    console.error("Error fetching division data:", error)
    cities.value = []
    irisList.value = []
  } finally {
    loading.value = false
  }
}

const debouncedFetchDivisionData = useDebounceFn(() => {
  fetchDivisionData()
}, 300)

// Watch for changes in click coordinates or plantability data
watch(
  () => [mapStore.clickCoordinates, props.plantabilityData] as const,
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
    <PlantabilityDivisionData v-else :cities="cities" :iris-list="irisList" />
  </div>
</template>
