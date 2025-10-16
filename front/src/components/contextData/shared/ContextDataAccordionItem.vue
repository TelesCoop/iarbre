<script lang="ts" setup>
import { ref, computed } from "vue"
import ContextDataItem from "@/components/contextData/shared/ContextDataItem.vue"
import VulnerabilityContextDataScoreBadge from "@/components/contextData/vulnerability/VulnerabilityContextDataScoreBadge.vue"
import type { ContextDataFactorGroup, ContextDataColorScheme } from "@/types/contextData"
import type { VulnerabilityCategory } from "@/utils/enum"
import { VulnerabilityMode } from "@/utils/vulnerability"

interface ContextDataAccordionItemProps {
  group: ContextDataFactorGroup
  colorScheme?: ContextDataColorScheme
  getCategoryScore?: (category: VulnerabilityCategory, mode: VulnerabilityMode) => number | null
  getScoreColor?: (score: number, factorId: string) => string
  getScoreLabel?: (score: number, factorId: string) => string
}

const props = withDefaults(defineProps<ContextDataAccordionItemProps>(), {
  colorScheme: "plantability"
})

const isExpanded = ref(false)

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const categoryClasses = computed(() => {
  const base =
    "flex items-center justify-between w-full p-3 text-left bg-gray-50 hover:bg-gray-100 focus:bg-gray-100 transition-colors cursor-pointer rounded-r-lg border-l-4"

  if (props.colorScheme === "plantability") {
    if (props.group?.hasPositiveImpact && props.group?.hasNegativeImpact) {
      return `${base} border-l-yellow-500`
    } else if (props.group?.hasPositiveImpact) {
      return `${base} border-l-green-500`
    } else if (props.group?.hasNegativeImpact) {
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

const isVulnerabilityGroup = computed(() => {
  return props.colorScheme === "vulnerability" && props.getCategoryScore !== undefined
})

const vulnerabilityCategory = computed(() => {
  if (!isVulnerabilityGroup.value) return null
  return props.group?.category as VulnerabilityCategory
})
</script>

<template>
  <div class="mb-2">
    <button
      :aria-controls="`category-${group?.category}`"
      :aria-expanded="isExpanded"
      :class="categoryClasses"
      :data-cy="`category-${group?.category}`"
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
        <vulnerability-context-data-score-badge
          v-if="isVulnerabilityGroup && vulnerabilityCategory && getCategoryScore"
          :category="vulnerabilityCategory"
          :get-category-score="getCategoryScore"
        />
        <div
          v-else-if="shouldShowImpactIndicator"
          :class="impactIndicatorClasses"
          :title="impactTitle"
        ></div>
        <i
          :class="isExpanded ? 'pi-chevron-up' : 'pi-chevron-down'"
          aria-hidden="true"
          class="pi transition-transform duration-200"
        ></i>
      </div>
    </button>

    <div
      v-if="isExpanded"
      :id="`category-${group?.category}`"
      class="mt-2 ml-4 space-y-2 animate-fade-in"
    >
      <context-data-item
        v-for="factor in group.factors"
        :key="factor.key"
        :color-scheme="colorScheme"
        :get-score-color="getScoreColor"
        :get-score-label="getScoreLabel"
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
