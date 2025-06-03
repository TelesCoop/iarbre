<script lang="ts" setup>
import {
  PlantabilityImpact,
  PlantabilityLandUseKeys,
  PlantabilityOccupationLevel,
  type PlantabilityTile
} from "@/types/plantability"
import { computed } from "vue"
import { PLANTABILITY_EMOJIS, PLANTABILITY_FACTORS_IMPACT } from "@/utils/plantability"

const props = defineProps({
  data: {
    required: true,
    type: Object as () => PlantabilityTile
  }
})

const getFactorOccupationLevel = (value: number): PlantabilityOccupationLevel => {
  if (value < 0) {
    return PlantabilityOccupationLevel.FAIBLE
  } else if (value < 33) {
    return PlantabilityOccupationLevel.MOYEN
  } else {
    return PlantabilityOccupationLevel.FORT
  }
}

const computeFactorLabel = (factorName: PlantabilityLandUseKeys, value: number): string => {
  const factorImpact = PLANTABILITY_FACTORS_IMPACT[factorName]

  if (!factorImpact) {
    return "Impact inconnu"
  }

  const occupationLevel = getFactorOccupationLevel(value)
  return `Impact ${factorImpact} ${occupationLevel}`
}

const factors = computed(() => {
  if (!props.data?.details?.top5LandUse) return []
  return Object.entries(props.data.details.top5LandUse).map(([key, value]) => ({
    label: key,
    value: computeFactorLabel(key as PlantabilityLandUseKeys, value),
    icon: PLANTABILITY_EMOJIS[key as keyof typeof PLANTABILITY_EMOJIS] || "", // Emoji par défaut si non trouvé
    impact: PLANTABILITY_FACTORS_IMPACT[key as PlantabilityLandUseKeys] || null
  }))
})
const scorePercentage = computed(() => (props.data.plantabilityNormalizedIndice / 10) * 100)

const emit = defineEmits(["close"])
</script>

<template>
  <div class="plantability-card max-w-md mx-auto bg-white shadow-lg overflow-hidden">
    <div class="bg-primary-500 text-white p-4 relative">
      <div class="flex justify-end">
        <button
          class="h-8 w-8 p-1 rounded-full hover:bg-white transition-colors hover:text-primary-500 text-white"
          data-cy="close-plantability-card"
          aria-label="Fermer la carte de plantabilité"
          @click="emit('close')"
        >
          <i class="pi pi-times text-xl transition-colors"></i>
        </button>
      </div>
      <h2 class="text-xl font-semibold mb-2 pr-8">Score de plantabilité</h2>
      <p class="text-sm">
        <i class="pi pi-info-circle"></i>
        Calcul basée sur la pondération de 30 paramètres
      </p>
    </div>

    <!-- Content -->
    <div class="p-4 flex flex-col gap-4">
      <div class="text-center">
        <div class="relative inline-block">
          <svg class="w-32 h-32 transform -rotate-90" viewBox="0 0 120 120">
            <circle
              cx="60"
              cy="60"
              r="50"
              stroke="currentColor"
              stroke-width="8"
              fill="none"
              class="text-gray-200"
            />
            <!-- Cercle de progression -->
            <circle
              cx="60"
              cy="60"
              r="50"
              stroke="currentColor"
              stroke-width="8"
              fill="none"
              class="text-green-600"
              :stroke-dasharray="314"
              :stroke-dashoffset="314 - (314 * scorePercentage) / 100"
              stroke-linecap="round"
              style="transition: stroke-dashoffset 0.5s ease-in-out"
            />
          </svg>
          <div class="absolute inset-0 flex flex-col items-center justify-center">
            <span class="text-sm text-gray-600">Score :</span>
            <span class="text-3xl font-bold text-gray-800"
              >{{ data.plantabilityNormalizedIndice }}/10</span
            >
          </div>
        </div>
      </div>
      <div>
        <h3 class="text-md font-semibold mb-4 flex items-center gap-2">
          <i class="pi pi-chart-bar text-blue-500"></i>
          Paramètres principaux
        </h3>
        <div class="h-40 sm:h-48 md:h-64 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
          <template v-if="factors.length">
            <div
              v-for="param in factors"
              :key="param.value"
              class="flex items-start gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div
                class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-gray-200 text-gray-700 text-lg"
                :class="{
                  'bg-orange-100': param.impact === PlantabilityImpact.NEGATIVE,
                  'bg-green-100': param.impact === PlantabilityImpact.POSITIVE,
                  'bg-gray-200': !param.impact
                }"
              >
                {{ param.icon }}
              </div>
              <div class="flex-1 min-w-0">
                <h4 class="text-sm font-medium text-gray-900 mb-1">{{ param.label }}</h4>
                <p
                  class="text-sm font-bold"
                  :class="
                    param.impact === PlantabilityImpact.NEGATIVE
                      ? 'text-orange-600'
                      : param.impact === PlantabilityImpact.POSITIVE
                        ? 'text-green-600'
                        : 'text-gray-700'
                  "
                >
                  {{ param.value }}
                </p>
              </div>
            </div>
          </template>
          <template v-else>
            <span class="text-gray-500 text-sm">Aucune donnée disponible</span>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
