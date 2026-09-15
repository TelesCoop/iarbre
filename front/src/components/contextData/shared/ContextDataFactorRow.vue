<script lang="ts" setup>
import VulnerabilityContextDataScore from "@/components/contextData/vulnerability/VulnerabilityContextDataScore.vue"
import type { ContextDataFactor, ContextDataVulnerabilityFactor } from "@/types/contextData"

interface ContextDataFactorRowProps {
  factor: ContextDataFactor
  variant?: "standard" | "vulnerability"
  getScoreColor?: (score: number, factorId: string) => string
  getScoreLabel?: (score: number, factorId: string) => string
}

const props = withDefaults(defineProps<ContextDataFactorRowProps>(), {
  variant: "standard",
  getScoreColor: undefined,
  getScoreLabel: undefined
})

const getFactorId = (factor: ContextDataFactor) => {
  return (factor as ContextDataVulnerabilityFactor).factorId || factor.key
}

const getScoreColor = (score: number, factorId: string) => {
  return props.getScoreColor?.(score, factorId) || "bg-gray-400"
}

const getScoreLabel = (score: number, factorId: string) => {
  return props.getScoreLabel?.(score, factorId) || score.toString()
}

const getImpactClass = (impact: ContextDataFactor["impact"]) => {
  if (impact === "positive") return "factor-value--positive impact-positive"
  if (impact === "negative") return "factor-value--negative impact-negative"
  return ""
}

const getDotClass = (impact: ContextDataFactor["impact"]) => {
  if (impact === "positive") return "factor-dot--positive"
  if (impact === "negative") return "factor-dot--negative"
  return "factor-dot--neutral"
}
</script>

<template>
  <div
    :class="['factor-row', variant === 'vulnerability' && 'factor-row--vulnerability']"
    :data-cy="`factor-${factor.key}`"
  >
    <span :class="['factor-dot', getDotClass(factor.impact)]" />
    <span class="factor-label">{{ factor.label }}</span>

    <template v-if="variant === 'vulnerability'">
      <span class="factor-score">
        <VulnerabilityContextDataScore
          :factor-id="getFactorId(factor)"
          :get-score-color="getScoreColor"
          :get-score-label="getScoreLabel"
          :score="(factor as ContextDataVulnerabilityFactor).dayScore ?? null"
        />
      </span>
      <span class="factor-score">
        <VulnerabilityContextDataScore
          :factor-id="getFactorId(factor)"
          :get-score-color="getScoreColor"
          :get-score-label="getScoreLabel"
          :score="(factor as ContextDataVulnerabilityFactor).nightScore ?? null"
        />
      </span>
    </template>

    <template v-else>
      <span :class="['factor-value', getImpactClass(factor.impact)]">
        {{ factor.value }}
        <span v-if="factor.unit" class="value-unit">{{ factor.unit }}</span>
      </span>
    </template>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.factor-row {
  @apply grid items-start gap-x-2 gap-y-1 text-xs;
  grid-template-columns: 0.5rem minmax(0, 1fr) minmax(4.5rem, max-content);
}

.factor-row--vulnerability {
  @apply items-center;
  grid-template-columns: 0.5rem minmax(0, 1fr) 2.5rem 2.5rem;
}

.factor-dot {
  @apply mt-1.5 h-2 w-2 shrink-0 overflow-hidden rounded-full text-[0px];
}

.factor-row--vulnerability .factor-dot {
  @apply mt-0;
}

.factor-dot--positive {
  @apply bg-primary-500;
}

.factor-dot--negative {
  @apply bg-orange-500;
}

.factor-dot--neutral {
  @apply bg-gray-300;
}

.factor-label {
  @apply min-w-0 text-xs leading-snug text-gray-500;
  overflow-wrap: anywhere;
}

.factor-value {
  @apply whitespace-nowrap text-right text-xs font-semibold tabular-nums text-gray-700;
}

.factor-value--positive {
  @apply text-primary-700;
}

.factor-value--negative {
  @apply text-orange-600;
}

.factor-score {
  @apply mx-auto;
}

.value-unit {
  @apply ml-0.5 text-xs font-normal text-gray-400;
}
</style>
