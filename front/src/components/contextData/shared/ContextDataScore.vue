<script lang="ts" setup>
import { computed } from "vue"
import type { ContextDataScoreConfig } from "@/types/contextData"
import { getPlantabilityTextColor, getVulnerabilityTextColor } from "@/utils/color"

interface ContextDataScoreProps extends ContextDataScoreConfig {
  name?: string
}

const props = defineProps<ContextDataScoreProps>()

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
</script>

<template>
  <section class="text-center" :aria-labelledby="`score-section-${label}`">
    <h3 :id="`score-section-${label}`" class="sr-only">Score de {{ label }} {{ name }}</h3>

    <div class="relative inline-block">
      <circular-progress
        :percentage="percentage"
        :background-color="textColor"
        :aria-label="ariaLabel"
        data-cy="circular-progress"
      />

      <div class="absolute inset-0 flex flex-col items-center justify-center">
        <span v-if="name" class="text-sm text-gray-600">{{ name }}:</span>
        <span v-else class="text-sm text-gray-600">Score :</span>
        <span class="text-xl md:text-3xl font-bold" :class="textColor" data-cy="context-data-score">
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
