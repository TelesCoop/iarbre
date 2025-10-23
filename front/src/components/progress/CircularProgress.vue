<script lang="ts" setup>
import { computed } from "vue"
import type { CircularScoreSize } from "@/types/contextData"

interface CircularProgressProps {
  percentage: number
  strokeWidth?: number
  backgroundColor?: string
  size?: CircularScoreSize
}

const props = withDefaults(defineProps<CircularProgressProps>(), {
  strokeWidth: 8,
  backgroundColor: "text-gray-200",
  size: "normal"
})

// Taille fixe responsive
const svgSize = 120
const radius = computed(() => (svgSize - props.strokeWidth) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const strokeDashOffset = computed(
  () => circumference.value - (circumference.value * props.percentage) / 100
)

const sizeClasses = computed(() => {
  switch (props.size) {
    case "small":
      return "w-16 h-16 sm:w-20 sm:h-20 md:w-24 md:h-24"
    case "large":
      return "w-24 h-24 sm:w-28 sm:h-28 md:w-32 md:h-32"
    case "normal":
    default:
      return "w-20 h-20 sm:w-24 sm:h-24 md:w-28 md:h-28"
  }
})
</script>

<template>
  <svg
    :width="svgSize"
    :height="svgSize"
    :class="[
      'transform -rotate-90 transition-all duration-300 ease-in-out max-w-full',
      sizeClasses
    ]"
    :viewBox="`0 0 ${svgSize} ${svgSize}`"
    role="img"
    preserveAspectRatio="xMidYMid meet"
    v-bind="$attrs"
  >
    <circle
      :cx="svgSize / 2"
      :cy="svgSize / 2"
      :r="radius"
      stroke="currentColor"
      :stroke-width="strokeWidth"
      fill="none"
      class="text-gray-200"
    />
    <circle
      :cx="svgSize / 2"
      :cy="svgSize / 2"
      :r="radius"
      stroke="currentColor"
      :stroke-width="strokeWidth"
      fill="none"
      :class="backgroundColor"
      :stroke-dasharray="circumference"
      :stroke-dashoffset="strokeDashOffset"
      stroke-linecap="round"
      class="transition-all duration-500 ease-in-out"
    />
  </svg>
</template>
