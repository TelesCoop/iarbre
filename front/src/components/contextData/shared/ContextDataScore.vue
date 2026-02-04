<script lang="ts" setup>
import { computed } from "vue"
import type { ContextDataScoreConfig } from "@/types/contextData"
import { getPlantabilityTextColor, getVulnerabilityTextColor } from "@/utils/color"

const props = withDefaults(defineProps<ContextDataScoreConfig>(), {
  size: "normal"
})

const textColor = computed(() => {
  switch (props.colorScheme) {
    case "plantability":
      return getPlantabilityTextColor(props.percentage)
    case "vulnerability":
      return getVulnerabilityTextColor(props.score)
    case "climate":
      return "text-primary-600"
    default:
      return "text-gray-700"
  }
})

const scoreDisplay = computed(() => {
  return `${props.score}/${props.maxScore}`
})

const ariaLabel = computed(() => {
  const baseName = props.name ? ` ${props.name}` : ""
  return `Score de ${props.label}${baseName}: ${props.score} sur ${props.maxScore}`
})

const barSegments = computed(() => {
  const segments = []
  const totalSegments = 10
  const filledSegments = Math.round((props.percentage / 100) * totalSegments)

  for (let i = 0; i < totalSegments; i++) {
    segments.push({
      filled: i < filledSegments
    })
  }
  return segments
})
</script>

<template>
  <section :aria-labelledby="`score-section-${label}`" class="score-section">
    <h3 :id="`score-section-${label}`" class="sr-only">Score de {{ label }} {{ name }}</h3>

    <div class="score-card">
      <div class="score-visual">
        <CircularProgress
          :aria-label="ariaLabel"
          :background-color="textColor"
          :percentage="percentage"
          :size="size"
          data-cy="circular-progress"
        />
        <div class="score-overlay">
          <span class="score-label">{{ name || "Moyenne" }}</span>
          <span :class="['score-value', textColor]" data-cy="context-data-score">
            {{ scoreDisplay }}
          </span>
          <span v-if="unit" class="score-unit">{{ unit }}</span>
        </div>
      </div>

      <div class="score-bar-container">
        <div class="bar-labels">
          <span class="bar-label">0</span>
          <span class="bar-label">{{ maxScore }}</span>
        </div>
        <div class="score-bar">
          <span
            v-for="(segment, index) in barSegments"
            :key="index"
            :class="['bar-segment', segment.filled ? textColor : 'is-empty']"
            :style="segment.filled ? 'background-color: currentColor' : ''"
          ></span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
@reference "@/styles/main.css";

.score-section {
  @apply w-full;
}

.score-card {
  @apply flex flex-col items-center gap-4 p-2;
}

.score-visual {
  @apply relative inline-flex items-center justify-center;
}

.score-overlay {
  @apply absolute inset-0 flex flex-col items-center justify-center gap-0.5;
}

.score-label {
  @apply text-xs font-medium text-gray-500 uppercase tracking-tight;
}

.score-value {
  @apply text-2xl font-bold leading-none;
}

.score-unit {
  @apply text-xs font-normal text-gray-400;
}

.score-bar-container {
  @apply w-full max-w-48;
}

.bar-labels {
  @apply flex justify-between mb-1 px-0.5;
}

.bar-label {
  @apply text-xs font-medium text-gray-400;
}

.score-bar {
  @apply flex gap-0.5 w-full h-1.5 p-0.5 bg-gray-100 rounded;
}

.bar-segment {
  @apply flex-1 min-w-1 rounded-sm transition-all duration-200;
}

.bar-segment.is-empty {
  @apply bg-gray-200;
}
</style>
