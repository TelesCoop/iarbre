<script lang="ts" setup>
import { computed } from "vue"
import { PlantabilityImpact } from "@/types/plantability"

interface PlantabiliyFactor {
  key: string
  label: string
  value: string
  icon: string
  impact: PlantabilityImpact | null
}

interface FactorItemProps {
  item: PlantabiliyFactor
}

const props = defineProps<FactorItemProps>()

const iconClasses = computed(() => {
  const base =
    "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-lg transition-colors"
  switch (props.item.impact) {
    case PlantabilityImpact.NEGATIVE:
      return `${base} bg-orange-100 text-orange-700`
    case PlantabilityImpact.POSITIVE:
      return `${base} bg-green-100 text-green-700`
    default:
      return `${base} bg-gray-200 text-gray-700`
  }
})

const valueClasses = computed(() => {
  const base = "text-sm font-bold transition-colors"

  switch (props.item.impact) {
    case PlantabilityImpact.NEGATIVE:
      return `${base} text-orange-600`
    case PlantabilityImpact.POSITIVE:
      return `${base} text-green-600`
    default:
      return `${base} text-gray-700`
  }
})
</script>

<template>
  <div
    role="listitem"
    class="flex items-start gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 focus-within:bg-gray-100 transition-colors"
    :data-cy="`factor-${item.key}`"
  >
    <div :class="iconClasses" :aria-label="`Icône pour ${item.label}`" data-cy="factor-icon">
      {{ item.icon }}
    </div>

    <div class="flex-1 min-w-0">
      <h4 class="text-sm font-medium text-gray-900 mb-1 truncate">
        {{ item.label }}
      </h4>
      <p :class="valueClasses">
        {{ item.value }}
      </p>
    </div>
  </div>
</template>
