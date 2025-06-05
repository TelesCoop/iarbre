<script lang="ts" setup>
import { ref, computed } from "vue"
import { PlantabilityImpact } from "@/types/plantability"
import PlantabilityContextDataItem from "@/components/contextData/plantability/PlantabilityContextDataItem.vue"

interface PlantabilityFactor {
  key: string
  label: string
  value: string
  icon: string
  impact: PlantabilityImpact | null
}

interface PlantabilityFactorGroup {
  category: string
  label: string
  icon: string
  factors: PlantabilityFactor[]
  hasPositiveImpact: boolean
  hasNegativeImpact: boolean
}

interface PlantabilityAccordionItemProps {
  group: PlantabilityFactorGroup
}

const props = defineProps<PlantabilityAccordionItemProps>()
const isExpanded = ref(false)

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const categoryClasses = computed(() => {
  const base =
    "flex items-center justify-between w-full p-3 text-left bg-gray-50 hover:bg-gray-100 focus:bg-gray-100 transition-colors cursor-pointer rounded-r-lg border-l-4"

  if (props.group.hasPositiveImpact && props.group.hasNegativeImpact) {
    return `${base} border-l-yellow-500`
  } else if (props.group.hasPositiveImpact) {
    return `${base} border-l-green-500`
  } else if (props.group.hasNegativeImpact) {
    return `${base} border-l-orange-500`
  }

  return `${base} border-l-gray-400`
})

const impactIndicatorClasses = computed(() => {
  if (props.group.hasPositiveImpact && props.group.hasNegativeImpact) {
    return "w-2 h-2 rounded-full bg-yellow-500"
  } else if (props.group.hasPositiveImpact) {
    return "w-2 h-2 rounded-full bg-green-500"
  } else if (props.group.hasNegativeImpact) {
    return "w-2 h-2 rounded-full bg-orange-500"
  }

  return "w-2 h-2 rounded-full bg-gray-400"
})
</script>

<template>
  <div class="mb-2">
    <button
      :class="categoryClasses"
      :aria-controls="`category-${group.category}`"
      :aria-expanded="isExpanded"
      :data-cy="`category-${group.category}`"
      @click="toggleExpanded"
    >
      <div class="flex items-center gap-3">
        <span class="text-lg">{{ group.icon }}</span>
        <div class="flex-1">
          <h4 class="text-sm font-medium text-gray-900">
            {{ group.label }}
          </h4>
          <p class="text-xs text-gray-600">
            {{ group.factors.length }} paramètre{{ group.factors.length > 1 ? "s" : "" }}
          </p>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <div
          :class="impactIndicatorClasses"
          :title="
            group.hasPositiveImpact && group.hasNegativeImpact
              ? 'Impact mixte'
              : group.hasPositiveImpact
                ? 'Impact positif'
                : group.hasNegativeImpact
                  ? 'Impact négatif'
                  : 'Impact neutre'
          "
        ></div>
        <i
          class="pi transition-transform duration-200"
          :class="isExpanded ? 'pi-chevron-up' : 'pi-chevron-down'"
          aria-hidden="true"
        ></i>
      </div>
    </button>

    <div
      v-show="isExpanded"
      :id="`category-${group.category}`"
      class="mt-2 ml-4 space-y-2 animate-fade-in"
    >
      <plantability-context-data-item
        v-for="factor in group.factors"
        :key="factor.key"
        :item="factor"
      />
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.2s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
