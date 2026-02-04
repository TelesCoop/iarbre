<script lang="ts" setup>
import { computed } from "vue"
import VulnerabilityContextDataScore from "@/components/contextData/vulnerability/VulnerabilityContextDataScore.vue"
import type {
  ContextDataFactor,
  ContextDataColorScheme,
  ContextDataVulnerabilityFactor
} from "@/types/contextData"

interface ContextDataItemProps {
  item: ContextDataFactor
  colorScheme?: ContextDataColorScheme
  getScoreColor?: (score: number, factorId: string) => string
  getScoreLabel?: (score: number, factorId: string) => string
}

const props = withDefaults(defineProps<ContextDataItemProps>(), {
  colorScheme: "plantability",
  getScoreColor: undefined,
  getScoreLabel: undefined
})

const impactClass = computed(() => {
  if (props.colorScheme === "plantability" && props.item.impact) {
    switch (props.item.impact) {
      case "negative":
        return "impact-negative"
      case "positive":
        return "impact-positive"
      default:
        return ""
    }
  }
  return ""
})

const isVulnerabilityFactor = computed(() => {
  const item = props.item as ContextDataVulnerabilityFactor
  return (
    props.colorScheme === "vulnerability" &&
    (item.dayScore !== undefined || item.nightScore !== undefined)
  )
})

const vulnerabilityScores = computed(() => {
  if (!isVulnerabilityFactor.value) return null

  const item = props.item as ContextDataVulnerabilityFactor
  return {
    day: item.dayScore,
    night: item.nightScore
  }
})
</script>

<template>
  <div :data-cy="`factor-${item.key}`" class="factor-item" role="listitem">
    <div v-if="item.icon" class="factor-icon" data-cy="factor-icon">
      {{ item.icon }}
    </div>

    <div class="factor-content">
      <div class="factor-header">
        <h4 class="factor-label">{{ item.label }}</h4>
        <div v-if="!isVulnerabilityFactor" class="factor-value-inline">
          <span :class="['value-text', impactClass]">{{ item.value }}</span>
          <span v-if="item.unit" class="value-unit">{{ item.unit }}</span>
        </div>
      </div>

      <p v-if="item.description" class="factor-description">
        {{ item.description }}
      </p>

      <div
        v-if="isVulnerabilityFactor && vulnerabilityScores && getScoreColor && getScoreLabel"
        class="vulnerability-scores"
      >
        <div class="score-item">
          <span class="score-label">☀️ Jour</span>
          <VulnerabilityContextDataScore
            :factor-id="(item as ContextDataVulnerabilityFactor).factorId || item.key"
            :get-score-color="getScoreColor"
            :get-score-label="getScoreLabel"
            :score="vulnerabilityScores.day ?? null"
          />
        </div>
        <div class="score-item">
          <span class="score-label">🌙 Nuit</span>
          <VulnerabilityContextDataScore
            :factor-id="(item as ContextDataVulnerabilityFactor).factorId || item.key"
            :get-score-color="getScoreColor"
            :get-score-label="getScoreLabel"
            :score="vulnerabilityScores.night ?? null"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.factor-item {
  @apply flex items-center gap-2 py-2 px-2.5 bg-gray-50 border border-gray-200 rounded-md;
}

.factor-icon {
  @apply flex items-center justify-center w-6 h-6 shrink-0 text-sm;
}

.factor-content {
  @apply flex-1 min-w-0;
}

.factor-header {
  @apply flex items-center justify-between gap-2;
}

.factor-label {
  @apply text-sm font-medium text-gray-700 leading-tight;
}

.factor-value-inline {
  @apply flex items-baseline gap-0.5 shrink-0;
}

.value-text {
  @apply text-sm font-semibold text-gray-800;
}

.value-text.impact-positive {
  @apply text-green-600;
}

.value-text.impact-negative {
  @apply text-orange-600;
}

.value-unit {
  @apply text-xs font-normal text-gray-500;
}

.factor-description {
  @apply text-xs text-gray-500 mt-0.5 leading-snug;
}

.vulnerability-scores {
  @apply flex gap-4 mt-1;
}

.score-item {
  @apply flex items-center gap-1.5;
}

.score-label {
  @apply text-xs font-medium text-gray-500;
}
</style>
