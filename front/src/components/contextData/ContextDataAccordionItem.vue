<script lang="ts" setup>
import { ref, computed } from "vue"
import ContextDataItem from "@/components/contextData/ContextDataItem.vue"

export interface ContextDataFactor {
  key: string
  label: string
  value: string
  icon: string
  impact?: string | null
  description?: string
  unit?: string
}

export interface ContextDataFactorGroup {
  category: string
  label: string
  icon: string
  factors: ContextDataFactor[]
  hasPositiveImpact?: boolean
  hasNegativeImpact?: boolean
  description?: string
}

interface ContextDataAccordionItemProps {
  group: ContextDataFactorGroup
  colorScheme?: "plantability" | "climate" | "vulnerability"
  layout?: "card" | "table"
}

const props = withDefaults(defineProps<ContextDataAccordionItemProps>(), {
  colorScheme: "plantability",
  layout: "card"
})

const isExpanded = ref(false)

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const categoryClasses = computed(() => {
  const base =
    "flex items-center justify-between w-full p-3 text-left bg-gray-50 hover:bg-gray-100 focus:bg-gray-100 transition-colors cursor-pointer rounded-r-lg border-l-4"

  if (props.colorScheme === "plantability") {
    if (props.group.hasPositiveImpact && props.group.hasNegativeImpact) {
      return `${base} border-l-yellow-500`
    } else if (props.group.hasPositiveImpact) {
      return `${base} border-l-green-500`
    } else if (props.group.hasNegativeImpact) {
      return `${base} border-l-orange-500`
    }
  } else {
    return `${base} border-l-primary-500`
  }

  return `${base} border-l-gray-400`
})

const impactIndicatorClasses = computed(() => {
  if (props.colorScheme === "plantability") {
    if (props.group.hasPositiveImpact && props.group.hasNegativeImpact) {
      return "w-2 h-2 rounded-full bg-yellow-500"
    } else if (props.group.hasPositiveImpact) {
      return "w-2 h-2 rounded-full bg-green-500"
    } else if (props.group.hasNegativeImpact) {
      return "w-2 h-2 rounded-full bg-orange-500"
    }
  }

  return "w-2 h-2 rounded-full bg-gray-400"
})

const shouldShowImpactIndicator = computed(() => {
  return (
    props.colorScheme === "plantability" &&
    (props.group.hasPositiveImpact || props.group.hasNegativeImpact)
  )
})

const impactTitle = computed(() => {
  if (props.colorScheme !== "plantability") return ""

  if (props.group.hasPositiveImpact && props.group.hasNegativeImpact) {
    return "Impact mixte"
  } else if (props.group.hasPositiveImpact) {
    return "Impact positif"
  } else if (props.group.hasNegativeImpact) {
    return "Impact négatif"
  }

  return "Impact neutre"
})

const expandedContentClasses = computed(() => {
  const base = "animate-fade-in"
  if (props.layout === "table") {
    return `divide-y divide-gray-50 ${base}`
  }
  return `mt-2 ml-4 space-y-2 ${base}`
})

const containerClasses = computed(() => {
  if (props.layout === "table") {
    return ""
  }
  return "mb-2"
})
</script>

<template>
  <div :class="containerClasses">
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
            {{
              group.description ||
              `${group.factors.length} paramètre${group.factors.length > 1 ? "s" : ""}`
            }}
          </p>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <div
          v-if="shouldShowImpactIndicator"
          :class="impactIndicatorClasses"
          :title="impactTitle"
        ></div>
        <i
          class="pi transition-transform duration-200"
          :class="isExpanded ? 'pi-chevron-up' : 'pi-chevron-down'"
          aria-hidden="true"
        ></i>
      </div>
    </button>

    <div v-if="isExpanded" :id="`category-${group.category}`" :class="expandedContentClasses">
      <context-data-item
        v-for="factor in group.factors"
        :key="factor.key"
        :item="factor"
        :color-scheme="colorScheme"
        :layout="layout"
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
