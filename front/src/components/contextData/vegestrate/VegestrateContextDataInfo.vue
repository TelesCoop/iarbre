<script lang="ts" setup>
import { computed } from "vue"
import type { VegetationData } from "@/types/vegetation"
import { getZoneDesc, getZoneColor } from "@/utils/vegetation"

interface VegetationContextDataInfoProps {
  data: VegetationData
}

const props = defineProps<VegetationContextDataInfoProps>()

const strateLabel = computed(() => getZoneDesc(props.data.indice))
const strateColor = computed(() => getZoneColor(props.data.indice))

const formattedSurface = computed(() => {
  return props.data.surface.toLocaleString("fr-FR", { maximumFractionDigits: 2 })
})
</script>

<template>
  <div class="space-y-4">
    <!-- Strate Type -->
    <div class="flex flex-col items-center justify-center p-4 bg-gray-50 rounded-lg">
      <div class="flex items-center gap-3 mb-2">
        <div
          class="w-6 h-6 rounded"
          :style="{ backgroundColor: strateColor }"
          :title="strateLabel"
        />
        <span class="text-lg font-semibold text-gray-800">{{ strateLabel }}</span>
      </div>
    </div>

    <!-- Surface -->
    <div class="flex justify-between items-center py-3 px-4 bg-gray-50 rounded-lg">
      <span class="text-sm font-medium text-gray-700">Surface</span>
      <span class="text-lg font-semibold text-gray-900">{{ formattedSurface }} m²</span>
    </div>
  </div>
</template>
