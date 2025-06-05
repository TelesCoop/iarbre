<script lang="ts" setup>
import { computed } from "vue"

interface CircularProgressProps {
  percentage: number
  strokeWidth?: number
  backgroundColor?: string
}

const props = withDefaults(defineProps<CircularProgressProps>(), {
  strokeWidth: 8,
  backgroundColor: "transparent"
})

// Taille fixe responsive
const size = 120
const radius = computed(() => (size - props.strokeWidth) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const strokeDashOffset = computed(
  () => circumference.value - (circumference.value * props.percentage) / 100
)
</script>

<template>
  <svg
    :width="size"
    :height="size"
    class="transform -rotate-90 transition-all duration-300 ease-in-out w-20 h-20 sm:w-24 sm:h-24 md:w-28 md:h-28 max-w-full"
    :viewBox="`0 0 ${size} ${size}`"
    role="img"
    preserveAspectRatio="xMidYMid meet"
    v-bind="$attrs"
  >
    <circle
      :cx="size / 2"
      :cy="size / 2"
      :r="radius"
      stroke="currentColor"
      :stroke-width="strokeWidth"
      fill="none"
      class="text-gray-200"
    />
    <circle
      :cx="size / 2"
      :cy="size / 2"
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
