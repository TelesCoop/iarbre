<script lang="ts" setup>
import { useContextDataStyles } from "@/composables/useContextDataStyles"
import ContextDataAccordionItem from "@/components/contextData/shared/ContextDataAccordionItem.vue"
import type { ContextDataFactorGroup, ContextDataColorScheme } from "@/types/contextData"
import type { VulnerabilityCategory } from "@/utils/enum"
import { VulnerabilityMode } from "@/utils/vulnerability"

interface ContextDataListContainerProps {
  groups: ContextDataFactorGroup[]
  colorScheme: ContextDataColorScheme
  fullHeight?: boolean
  scrollable?: boolean
  getCategoryScore?: (category: VulnerabilityCategory, mode: VulnerabilityMode) => number | null
  getScoreColor?: (score: number, factorId: string) => string
  getScoreLabel?: (score: number, factorId: string) => string
  ariaLabel?: string
}

const props = withDefaults(defineProps<ContextDataListContainerProps>(), {
  fullHeight: false,
  scrollable: false,
  getCategoryScore: undefined,
  getScoreColor: undefined,
  getScoreLabel: undefined,
  ariaLabel: "Liste des paramètres par catégorie"
})

const { getContextListClassesComputed } = useContextDataStyles()
const containerClasses = getContextListClassesComputed(props.fullHeight, props.scrollable)
</script>

<template>
  <div :class="containerClasses" :aria-label="ariaLabel" role="list">
    <ContextDataAccordionItem
      v-for="group in groups"
      :key="group.category"
      :group="group"
      :color-scheme="colorScheme"
      :get-category-score="getCategoryScore"
      :get-score-color="getScoreColor"
      :get-score-label="getScoreLabel"
    />
  </div>
</template>
