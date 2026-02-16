<script lang="ts" setup>
import { ref, watch, computed } from "vue"
import { useMapStore } from "@/stores/map"
import { getCities, getIrisList } from "@/services/divisionService"
import type { City, Iris } from "@/types/division"
import type { PlantabilityData } from "@/types/plantability"
import PlantabilityDivisionData from "./PlantabilityDivisionData.vue"
import AppSpinner from "@/components/shared/AppSpinner.vue"
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
  return props.plantabilityData?.cityCodes || []
})
const irisCodes = computed(() => {
  return props.plantabilityData?.irisCodes || []
})

const resetDivisionData = () => {
  cities.value = []
  irisList.value = []
}

const fetchDivisionData = async () => {
  const { lat, lng } = mapStore.clickCoordinates

  if (!lat || !lng) {
    return
  }

  loading.value = true

  try {
    // If we have codes from polygon selection, use them
    if (cityCodes.value.length > 0 || irisCodes.value.length > 0) {
      const [citiesData, irisData] = await Promise.all([
        cityCodes.value.length > 0
          ? getCities({ code__in: cityCodes.value })
          : Promise.resolve(null),
        irisCodes.value.length > 0
          ? getIrisList({ code__in: irisCodes.value })
          : Promise.resolve(null)
      ])

      cities.value = citiesData || []
      irisList.value = irisData || []
    } else {
      // Fallback to point intersection for single tile selection
      const coordinates: [number, number] = [lng, lat]

      const [citiesData, irisData] = await Promise.all([
        getCities({ geometry__intersects: coordinates }),
        getIrisList({ geometry__intersects: coordinates })
      ])

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
      <AppSpinner size="md" color="#426A45" />
    </div>
    <PlantabilityDivisionData v-else :cities="cities" :iris-list="irisList" />
  </div>
</template>
