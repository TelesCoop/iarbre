<script lang="ts" setup>
import { ref } from "vue"
import { type ClimateData, ClimateCategory } from "@/types/climate"
import { useClimateZone } from "@/composables/useClimateZone"

interface ClimateMetricsProps {
  data: ClimateData
}

defineProps<ClimateMetricsProps>()

const {
  climateCategoryToIcon,
  climateCategoryToDescription,
  climateCategoryOrder,
  climateZoneDetailsByCategory,
  climateCategoryKey
} = useClimateZone()

const expandedCategories = ref<Record<ClimateCategory, boolean>>({
  [ClimateCategory.BUILDING]: false,
  [ClimateCategory.SURFACES]: false,
  [ClimateCategory.VEGETATION]: false
})

const toggleCategory = (category: ClimateCategory) => {
  expandedCategories.value[category] = !expandedCategories.value[category]
}
</script>

<template>
  <div
    class="max-h-44 xs:max-h-48 sm:max-h-52 md:max-h-56 lg:max-h-56 xl:max-h-100 overflow-y-auto scrollbar border border-gray-200 rounded-lg"
  >
    <div v-for="category in climateCategoryOrder" :key="category" class="overflow-hidden">
      <button
        :data-cy="`${climateCategoryKey[category]}`"
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
          v-for="(metric, index) in climateZoneDetailsByCategory[category]"
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
                <div v-if="data.details?.[metric.key]" class="text-lg font-bold text-primary-500">
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
