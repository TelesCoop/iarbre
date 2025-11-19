<script lang="ts" setup>
import { computed, ref } from "vue"
import {
  Card,
  Button,
  Accordion,
  AccordionPanel,
  AccordionHeader,
  AccordionContent
} from "primevue"
import type { ContextDataItem } from "@/composables/useContextData"
import { DataType } from "@/utils/enum"
import CircularScore from "@/components/shared/CircularScore.vue"
import type { PlantabilityData } from "@/types/plantability"
import type { VulnerabilityData } from "@/types/vulnerability"
import type { PlantabilityVulnerabilityData } from "@/types/vulnerability_plantability"
import PlantabilityDivisionData from "@/components/division/PlantabilityDivisionData.vue"
import { getCities, getIrisList } from "@/services/divisionService"
import type { City, Iris } from "@/types/division"

interface Props {
  item: ContextDataItem
}

const props = defineProps<Props>()
const emit = defineEmits<{
  remove: [id: string]
}>()

const city = ref<City | null>(null)
const iris = ref<Iris | null>(null)
const loadingDivision = ref(false)
const divisionDataLoaded = ref(false)

const isPlantability = computed(() => props.item.data.datatype === DataType.PLANTABILITY)
const canExpand = computed(() => isPlantability.value)

const score = computed(() => {
  const data = props.item.data
  if (data.datatype === DataType.PLANTABILITY) {
    return (data as PlantabilityData).plantabilityNormalizedIndice
  } else if (data.datatype === DataType.VULNERABILITY) {
    return (data as VulnerabilityData).vulnerabilityIndexDay
  } else if (data.datatype === DataType.PLANTABILITY_VULNERABILITY) {
    return (data as PlantabilityVulnerabilityData).plantabilityNormalizedIndice
  }
  return 0
})

const scorePercentage = computed(() => {
  return score.value * 10
})

const dataTypeName = computed(() => {
  switch (props.item.data.datatype) {
    case DataType.PLANTABILITY:
      return "Plantabilité"
    case DataType.VULNERABILITY:
      return "Vulnérabilité"
    case DataType.PLANTABILITY_VULNERABILITY:
      return "Plantabilité & Vulnérabilité"
    case DataType.CLIMATE_ZONE:
      return "Zone climatique"
    default:
      return "Donnée"
  }
})

const colorScheme = computed(() => {
  switch (props.item.data.datatype) {
    case DataType.PLANTABILITY:
      return "plantability"
    case DataType.VULNERABILITY:
      return "vulnerability"
    case DataType.PLANTABILITY_VULNERABILITY:
      return "bivariate"
    case DataType.CLIMATE_ZONE:
      return "climate"
    default:
      return "plantability"
  }
})

const fetchDivisionData = async () => {
  if (!canExpand.value || divisionDataLoaded.value) return

  loadingDivision.value = true
  try {
    const { lat, lng } = props.item.coordinates
    const coordinates: [number, number] = [lng, lat]

    const [citiesData, irisData] = await Promise.all([
      getCities({ geometry__intersects: coordinates }),
      getIrisList({ geometry__intersects: coordinates })
    ])

    city.value = citiesData && citiesData.length > 0 ? citiesData[0] : null
    iris.value = irisData && irisData.length > 0 ? irisData[0] : null
    divisionDataLoaded.value = true
  } catch (error) {
    console.error("Error fetching division data:", error)
    city.value = null
    iris.value = null
  } finally {
    loadingDivision.value = false
  }
}

const onAccordionOpen = () => {
  if (!divisionDataLoaded.value) {
    fetchDivisionData()
  }
}
</script>

<template>
  <Card class="w-full bg-white rounded-lg border-1 border-gray-200 mb-2">
    <template #content>
      <div class="flex items-center justify-between gap-3 p-2">
        <!-- Score Circle -->
        <div class="flex-shrink-0">
          <circular-score
            :percentage="scorePercentage"
            :color-scheme="colorScheme"
            :size="50"
            :stroke-width="4"
          />
        </div>

        <!-- Info section -->
        <div class="flex-grow min-w-0">
          <div class="text-sm font-semibold text-gray-700 truncate">{{ dataTypeName }}</div>
          <div class="text-xs text-gray-500">
            Position: {{ item.coordinates.lat.toFixed(4) }}, {{ item.coordinates.lng.toFixed(4) }}
          </div>
          <div class="text-xs text-gray-600">Score: {{ score.toFixed(2) }}</div>
        </div>

        <!-- Remove button -->
        <div class="flex-shrink-0">
          <Button
            icon="pi pi-times"
            severity="secondary"
            text
            rounded
            size="small"
            @click="emit('remove', item.data.id)"
          />
        </div>
      </div>

      <!-- Expandable section for plantability -->
      <div v-if="canExpand" class="mt-2">
        <Accordion @update:value="onAccordionOpen">
          <AccordionPanel value="0">
            <AccordionHeader>
              <span class="text-sm">Voir les données aux échelons supérieurs</span>
            </AccordionHeader>
            <AccordionContent>
              <PlantabilityDivisionData v-if="!loadingDivision" :city="city" :iris="iris" />
              <div v-else class="flex justify-center p-4">
                <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
              </div>
            </AccordionContent>
          </AccordionPanel>
        </Accordion>
      </div>
    </template>
  </Card>
</template>
