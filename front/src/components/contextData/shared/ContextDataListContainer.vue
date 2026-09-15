<script lang="ts" setup>
import { computed } from "vue"
import ContextDataAccordionItem from "@/components/contextData/shared/ContextDataAccordionItem.vue"
import type { ContextDataFactorGroup, ContextDataColorScheme } from "@/types/contextData"
import type { VulnerabilityCategory } from "@/utils/enum"
import { VulnerabilityMode } from "@/utils/vulnerability"

interface ContextDataListContainerProps {
  groups: ContextDataFactorGroup[]
  colorScheme: ContextDataColorScheme
  variant?: "cards" | "diagnostic"
  fullHeight?: boolean
  scrollable?: boolean
  getCategoryScore?: (category: VulnerabilityCategory, mode: VulnerabilityMode) => number | null
  getScoreColor?: (score: number, factorId: string) => string
  getScoreLabel?: (score: number, factorId: string) => string
  ariaLabel?: string
}

const props = withDefaults(defineProps<ContextDataListContainerProps>(), {
  variant: undefined,
  fullHeight: false,
  scrollable: false,
  getCategoryScore: undefined,
  getScoreColor: undefined,
  getScoreLabel: undefined,
  ariaLabel: "Liste des paramètres par catégorie"
})

const containerClasses = computed(() => {
  const classes = ["data-sections"]
  classes.push(`data-sections--${props.variant || defaultVariant.value}`)
  return classes
})

const defaultVariant = computed(() => {
  return props.colorScheme === "vulnerability" ? "diagnostic" : "cards"
})
</script>

<template>
  <div :class="containerClasses" :aria-label="ariaLabel" role="list">
    <ContextDataAccordionItem
      v-for="group in groups"
      :key="group.category"
      :group="group"
      :color-scheme="colorScheme"
      :variant="variant || defaultVariant"
      :get-category-score="getCategoryScore"
      :get-score-color="getScoreColor"
      :get-score-label="getScoreLabel"
    />
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.data-sections {
  @apply flex flex-col gap-3;
}
</style>
