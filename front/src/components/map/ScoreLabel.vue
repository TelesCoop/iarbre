<script lang="ts" setup>
import { computed } from "vue"
import type { ScoreLabelSize } from "@/utils/enum"

interface ScoreLabelProps {
  score: number
  label: string
  isSelected?: boolean
}

const SCORE_BG_CLASSES: Record<number, string> = {
  0: "fill-scale-0",
  1: "fill-scale-1",
  2: "fill-scale-2",
  3: "fill-scale-3",
  4: "fill-scale-4",
  5: "fill-scale-5",
  6: "fill-scale-6",
  7: "fill-scale-7",
  8: "fill-scale-8",
  9: "fill-scale-9",
  10: "fill-scale-10"
}

const props = defineProps<ScoreLabelProps>()

const backgroundClass = computed(() => SCORE_BG_CLASSES[props.score] || SCORE_BG_CLASSES[0])
const isSelected = computed(() => props.isSelected || false)
</script>

<template>
  <div class="relative">
    <svg height="60" viewBox="0 0 54 60" width="54" xmlns="http://www.w3.org/2000/svg">
      <path
        :class="backgroundClass"
        :stroke="isSelected ? '#002814' : ''"
        d="M3.85 13.08L23.21 1.9C25.28 0.7 27.84 0.7 29.91 1.9L49.27 13.08C51.34 14.28 52.62 16.49 52.62 18.89V41.25C52.62 43.64 51.34 45.86 49.27 47.06L29.91 58.24C27.84 59.44 25.28 59.44 23.21 58.24L3.85 47.05C1.78 45.85 0.5 43.64 0.5 41.24V18.88C0.5 16.49 1.78 14.27 3.85 13.07V13.08Z"
        stroke-miterlimit="10"
      />
    </svg>
    <span
      class="absolute font-accent inset-0 text-sm flex items-center justify-center text-center"
      >{{ label }}</span
    >
  </div>
</template>

<style scoped></style>
