<script lang="ts" setup>
import { computed } from "vue"
import VulnerabilityContextDataScoreBadge from "@/components/contextData/vulnerability/VulnerabilityContextDataScoreBadge.vue"
import VulnerabilityContextDataScore from "@/components/contextData/vulnerability/VulnerabilityContextDataScore.vue"
import type {
  ContextDataFactorGroup,
  ContextDataColorScheme,
  ContextDataVulnerabilityFactor
} from "@/types/contextData"
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
  colorScheme: "plantability",
  getCategoryScore: undefined,
  getScoreColor: undefined,
  getScoreLabel: undefined
})

const isVulnerabilityGroup = computed(() => {
  return props.colorScheme === "vulnerability" && props.getCategoryScore !== undefined
})

const vulnerabilityCategory = computed(() => {
  if (!isVulnerabilityGroup.value) return null
  return props.group?.category as VulnerabilityCategory
})

const isVulnerabilityFactor = (factor: any) => {
  return (
    props.colorScheme === "vulnerability" &&
    (factor.dayScore !== undefined || factor.nightScore !== undefined)
  )
}
</script>

<template>
  <div class="accordion-item" :data-cy="`category-${group?.category}`">
    <div class="accordion-header">
      <span class="header-icon">{{ group.icon }}</span>
      <span class="header-label">{{ group.label }}</span>
      <VulnerabilityContextDataScoreBadge
        v-if="isVulnerabilityGroup && vulnerabilityCategory && getCategoryScore"
        :category="vulnerabilityCategory"
        :get-category-score="getCategoryScore"
      />
    </div>
    <table class="accordion-table">
      <tbody>
        <tr
          v-for="(factor, index) in group.factors"
          :key="factor.key"
          :class="{ 'row-border': index < group.factors.length - 1 }"
          :data-cy="`factor-${factor.key}`"
        >
          <td class="cell-icon">
            <span v-if="factor.icon">{{ factor.icon }}</span>
          </td>
          <td class="cell-label">{{ factor.label }}</td>
          <td v-if="isVulnerabilityFactor(factor)" class="cell-vulnerability">
            <div class="vulnerability-scores">
              <span class="score-icon">☀️</span>
              <VulnerabilityContextDataScore
                :factor-id="(factor as ContextDataVulnerabilityFactor).factorId || factor.key"
                :get-score-color="getScoreColor!"
                :get-score-label="getScoreLabel!"
                :score="(factor as ContextDataVulnerabilityFactor).dayScore ?? null"
              />
              <span class="score-icon">🌙</span>
              <VulnerabilityContextDataScore
                :factor-id="(factor as ContextDataVulnerabilityFactor).factorId || factor.key"
                :get-score-color="getScoreColor!"
                :get-score-label="getScoreLabel!"
                :score="(factor as ContextDataVulnerabilityFactor).nightScore ?? null"
              />
            </div>
          </td>
          <td
            v-else
            :class="[
              'cell-value',
              factor.impact === 'positive' ? 'impact-positive' : '',
              factor.impact === 'negative' ? 'impact-negative' : ''
            ]"
          >
            {{ factor.value }}
            <span v-if="factor.unit" class="value-unit">{{ factor.unit }}</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.accordion-item {
  @apply mb-3;
}

.accordion-header {
  @apply flex items-center gap-2 px-2.5 py-2 bg-gray-100 border border-gray-200 border-b-0 rounded-t-md;
}

.header-icon {
  @apply text-sm;
}

.header-label {
  @apply flex-1 text-sm font-semibold text-gray-800;
}

.accordion-table {
  @apply w-full bg-white border border-gray-200 rounded-b-md overflow-hidden;
}

.row-border {
  @apply border-b border-gray-100;
}

.accordion-table td {
  @apply py-1.5 px-2 align-middle;
}

.cell-icon {
  @apply w-6 text-center text-xs;
}

.cell-label {
  @apply text-sm text-gray-700;
}

.cell-vulnerability {
  @apply text-right;
}

.vulnerability-scores {
  @apply flex items-center justify-end gap-1;
}

.score-icon {
  @apply text-xs;
}

.cell-value {
  @apply text-right text-sm font-semibold whitespace-nowrap text-gray-800;
}

.cell-value.impact-positive {
  @apply text-green-600;
}

.cell-value.impact-negative {
  @apply text-orange-600;
}

.value-unit {
  @apply text-xs font-normal text-gray-500 ml-0.5;
}
</style>
