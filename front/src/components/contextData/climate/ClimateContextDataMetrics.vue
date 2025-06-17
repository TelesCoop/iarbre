<script lang="ts" setup>
import { computed, ref } from "vue"
import { type ClimateData, ClimateDataDetailsKey } from "@/types/climate"

interface ClimateMetricsProps {
  data: ClimateData
}

defineProps<ClimateMetricsProps>()

enum ClimateCategory {
  BUILDING = "Caractéristiques du bâti",
  SURFACES = "Types de surfaces",
  VEGETATION = "Végétation et eau"
}

const climateCategoryToIcon: Record<ClimateCategory, string> = {
  [ClimateCategory.BUILDING]: "🏢",
  [ClimateCategory.SURFACES]: "🛣️",
  [ClimateCategory.VEGETATION]: "🌿"
}

const climateCategoryToDescription: Record<ClimateCategory, string> = {
  [ClimateCategory.BUILDING]: "Indicateurs liés aux bâtiments et à l'urbanisation",
  [ClimateCategory.SURFACES]: "Répartition des différents types de surfaces au sol",
  [ClimateCategory.VEGETATION]: "Présence de végétation et d'eau dans la zone"
}

const climateCategoryOrder = [
  ClimateCategory.BUILDING,
  ClimateCategory.SURFACES,
  ClimateCategory.VEGETATION
]

const expandedCategories = ref<Record<ClimateCategory, boolean>>({
  [ClimateCategory.BUILDING]: true,
  [ClimateCategory.SURFACES]: true,
  [ClimateCategory.VEGETATION]: true
})

const toggleCategory = (category: ClimateCategory) => {
  expandedCategories.value[category] = !expandedCategories.value[category]
}

const metricsByCategory = computed(() => {
  return {
    [ClimateCategory.BUILDING]: [
      {
        key: ClimateDataDetailsKey.HRE,
        label: "Hauteur moyenne du bâti",
        unit: "m",
        description: "Hauteur moyenne des bâtiments dans la zone"
      },
      {
        key: ClimateDataDetailsKey.ARE,
        label: "Superficie moyenne du bâti",
        unit: "m²",
        description: "Superficie moyenne des bâtiments"
      },
      {
        key: ClimateDataDetailsKey.BUR,
        label: "Taux de surface bâtie",
        unit: "%",
        description: "Pourcentage de la surface occupée par des bâtiments"
      }
    ],
    [ClimateCategory.SURFACES]: [
      {
        key: ClimateDataDetailsKey.ROR,
        label: "Surface minérale imperméable",
        unit: "%",
        description: "Pourcentage de surface imperméable (routes, trottoirs, etc.)"
      },
      {
        key: ClimateDataDetailsKey.BSR,
        label: "Sol nu perméable",
        unit: "%",
        description: "Pourcentage de sol nu mais perméable"
      }
    ],
    [ClimateCategory.VEGETATION]: [
      {
        key: ClimateDataDetailsKey.WAR,
        label: "Surface en eau",
        unit: "%",
        description: "Pourcentage de surface occupée par l'eau"
      },
      {
        key: ClimateDataDetailsKey.VER,
        label: "Végétation totale",
        unit: "%",
        description: "Pourcentage de surface couverte par la végétation"
      },
      {
        key: ClimateDataDetailsKey.VHR,
        label: "Végétation arborée",
        unit: "%",
        description: "Part de végétation arborée sur la végétation totale"
      }
    ]
  }
})
</script>

<template>
  <div
    class="max-h-44 xs:max-h-48 sm:max-h-52 md:max-h-56 lg:max-h-56 xl:max-h-100 overflow-y-auto scrollbar border border-gray-200 rounded-lg"
  >
    <div v-for="category in climateCategoryOrder" :key="category" class="overflow-hidden">
      <button
        class="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors duration-200 flex items-center justify-between text-left"
        @click="toggleCategory(category)"
      >
        <div class="flex items-center gap-3">
          <span class="text-lg">{{ climateCategoryToIcon[category] }}</span>
          <div>
            <h3 class="font-medium text-gray-900 text-sm">{{ category }}</h3>
            <p class="text-xs text-gray-600 mt-0.5">
              {{ climateCategoryToDescription[category] }}
            </p>
          </div>
        </div>
        <svg
          :class="[
            'w-5 h-5 text-gray-400 transition-transform duration-200',
            expandedCategories[category] ? 'transform rotate-180' : ''
          ]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            d="M19 9l-7 7-7-7"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
          />
        </svg>
      </button>
      <div v-if="expandedCategories[category]" class="divide-y divide-gray-100">
        <div
          v-for="(metric, index) in metricsByCategory[category]"
          :key="metric.key"
          class="p-4 hover:bg-primary-100 transition-colors duration-150"
        >
          <div class="grid grid-cols-12 gap-3 items-center">
            <div class="col-span-2">
              <div
                class="w-6 h-6 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center text-xs font-bold text-gray-700"
              >
                {{ index + 1 }}
              </div>
            </div>
            <div class="col-span-6">
              <div class="flex flex-col">
                <span class="text-gray-800 font-medium text-sm leading-tight">
                  {{ metric.label }}
                </span>
                <span class="text-xs text-gray-500 mt-1">
                  {{ metric.description }}
                </span>
              </div>
            </div>
            <div class="col-span-4 flex justify-end">
              <div class="text-right">
                <div class="text-lg font-bold text-primary-500">
                  {{ data.details[metric.key] || "N/A" }}
                </div>
                <div class="text-xs text-gray-500 font-medium">
                  {{ metric.unit }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
