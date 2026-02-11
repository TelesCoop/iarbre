<script lang="ts" setup>
import { computed, ref } from "vue"
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

const isExpanded = ref(false)

const toggle = () => {
  isExpanded.value = !isExpanded.value
}

const isVulnerabilityFactor = (factor: any) => {
  return (
    props.colorScheme === "vulnerability" &&
    (factor.dayScore !== undefined || factor.nightScore !== undefined)
  )
}
</script>

<template>
  <div :data-cy="`category-${group?.category}`" class="accordion-item">
    <button :aria-expanded="isExpanded" class="accordion-header" type="button" @click="toggle">
      <span class="header-icon">{{ group.icon }}</span>
      <span class="header-label">{{ group.label }}</span>
      <VulnerabilityContextDataScoreBadge
        v-if="isVulnerabilityGroup && vulnerabilityCategory && getCategoryScore"
        :category="vulnerabilityCategory"
        :get-category-score="getCategoryScore"
      />
      <svg
        :class="{ rotated: isExpanded }"
        class="chevron-icon"
        fill="none"
        height="12"
        viewBox="0 0 12 12"
        width="12"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M2 4L6 8L10 4"
          stroke="currentColor"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
        />
      </svg>
    </button>
    <table v-show="isExpanded" class="accordion-table">
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
  @apply flex items-center gap-2 w-full px-2.5 py-2 bg-gray-100 border border-gray-200 border-b-0 rounded-t-md;
  @apply cursor-pointer transition-colors duration-200 hover:bg-gray-200;
  @apply text-left;
}

.accordion-header[aria-expanded="false"] {
  @apply rounded-b-md border-b;
}

.chevron-icon {
  @apply flex-shrink-0 text-gray-400 transition-transform duration-200;
}

.chevron-icon.rotated {
  transform: rotate(180deg);
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
