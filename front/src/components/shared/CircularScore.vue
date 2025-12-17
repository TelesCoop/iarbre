<script lang="ts" setup>
import { computed } from "vue"
import type { ContextDataColorScheme, CircularScoreSize } from "@/types/contextData"
import { getPlantabilityTextColor, getVulnerabilityTextColor } from "@/utils/color"

interface CircularScoreProps {
  score: number
  maxScore: number
  percentage: number
  label: string
  colorScheme: ContextDataColorScheme
  name?: string
  unit?: string
  size?: CircularScoreSize
}

const props = withDefaults(defineProps<CircularScoreProps>(), {
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
  const scoreText = `${props.score}/${props.maxScore}`
  return props.unit ? `${scoreText} ${props.unit}` : scoreText
})

const ariaLabel = computed(() => {
  const baseName = props.name ? ` ${props.name}` : ""
  return `Score de ${props.label}${baseName}: ${props.score} sur ${props.maxScore}`
})

const labelSizeClass = computed(() => {
  switch (props.size) {
    case "small":
      return "text-xs"
    case "large":
      return "text-base"
    case "normal":
    default:
      return "text-sm"
  }
})

const scoreSizeClass = computed(() => {
  switch (props.size) {
    case "small":
      return "text-lg md:text-xl"
    case "large":
      return "text-2xl md:text-xl"
    case "normal":
    default:
      return "text-xl md:text-2xl"
  }
})
</script>

<template>
  <section class="text-center" :aria-labelledby="`score-section-${label}`">
    <h3 :id="`score-section-${label}`" class="sr-only">Score de {{ label }} {{ name }}</h3>

    <div class="relative inline-block">
      <circular-progress
        :percentage="percentage"
        :background-color="textColor"
        :size="size"
        :aria-label="ariaLabel"
        data-cy="circular-progress"
      />

      <div class="absolute inset-0 flex flex-col items-center justify-center">
        <span v-if="name" :class="[labelSizeClass, 'text-gray-600']">{{ name }}:</span>
        <span v-else :class="[labelSizeClass, 'text-gray-600']">Score :</span>
        <span :class="[scoreSizeClass, textColor, 'font-bold']" data-cy="context-data-score">
          {{ scoreDisplay }}
        </span>
      </div>
    </div>
  </section>
</template>

<style scoped>
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
