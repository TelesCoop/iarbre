<script lang="ts" setup>
import { computed } from "vue"
import type { City } from "@/types/division"

interface IpaveDivisionDataDisplayProps {
  data: City
}

const props = defineProps<IpaveDivisionDataDisplayProps>()

const codeLabel = computed(() => "Code INSEE")

const vegetationData = computed(() => [
  {
    label: "Végétation de voirie haute",
    value: props.data.vegetationVoirieHaute,
    unit: "ha"
  },
  {
    label: "Végétation de voirie moyenne",
    value: props.data.vegetationVoirieMoyenne,
    unit: "ha"
  },
  {
    label: "Végétation de voirie basse",
    value: props.data.vegetationVoirieBasse,
    unit: "ha"
  },
  {
    label: "Végétation de voirie totale",
    value: props.data.vegetationVoirieTotal,
    unit: "ha"
  }
])

const formatValue = (value: number) => {
  if (value === null || value === undefined) return "N/A"
  return value.toLocaleString("fr-FR", { maximumFractionDigits: 2 })
}
</script>

<template>
  <div>
    <div class="mb-4">
      <h4 class="text-base font-semibold text-gray-800 mb-1">{{ data.name || data.code }}</h4>
    </div>

    <div class="space-y-3">
      <div
        v-for="(item, index) in vegetationData"
        :key="index"
        class="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0"
      >
        <span class="text-sm text-gray-700 font-medium">{{ item.label }}</span>
        <span class="text-sm text-gray-900 font-semibold">
          {{ formatValue(item.value) }} {{ item.unit }}
        </span>
      </div>
    </div>
  </div>
</template>
