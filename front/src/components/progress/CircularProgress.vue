<script lang="ts" setup>
import { computed } from "vue"

interface CircularProgressProps {
  percentage: number
  size?: number
  strokeWidth?: number
  color?: string
  backgroundColor?: string
}

const props = withDefaults(defineProps<CircularProgressProps>(), {
  size: 120,
  strokeWidth: 8,
  color: "text-green-600",
  backgroundColor: "text-gray-200"
})

const radius = computed(() => (props.size - props.strokeWidth) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const strokeDashOffset = computed(
  () => circumference.value - (circumference.value * props.percentage) / 100
)
</script>

<template>
  <svg
    :width="size"
    :height="size"
    class="transform -rotate-90"
    :viewBox="`0 0 ${size} ${size}`"
    role="img"
    v-bind="$attrs"
  >
    <circle
      :cx="size / 2"
      :cy="size / 2"
      :r="radius"
      stroke="currentColor"
      :stroke-width="strokeWidth"
      fill="none"
      :class="backgroundColor"
    />
    <circle
      :cx="size / 2"
      :cy="size / 2"
      :r="radius"
      stroke="currentColor"
      :stroke-width="strokeWidth"
      fill="none"
      :class="color"
      :stroke-dasharray="circumference"
      :stroke-dashoffset="strokeDashOffset"
      stroke-linecap="round"
      class="transition-all duration-500 ease-in-out"
    />
  </svg>
</template>
