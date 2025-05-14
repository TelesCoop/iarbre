<script lang="ts" setup>
import { computed } from "vue"

interface ScoreLabelProps {
  score: number
  label: string
  isSelected?: boolean
}

const SCORE_BG_CLASSES: Record<number, string> = {
  0: "bg-scale-0",
  1: "bg-scale-1",
  2: "bg-scale-2",
  3: "bg-scale-3",
  4: "bg-scale-4",
  5: "bg-scale-5",
  6: "bg-scale-6",
  7: "bg-scale-7",
  8: "bg-scale-8",
  9: "bg-scale-9",
  10: "bg-scale-10"
}

const TEXT_SCORE_CLASSES: Record<number, string> = {
  0: "text-black",
  2: "text-white",
  4: "text-black",
  6: "text-black",
  8: "text-black",
  10: "text-white"
}

const props = defineProps<ScoreLabelProps>()

const backgroundClass = computed(() => SCORE_BG_CLASSES[props.score] || SCORE_BG_CLASSES[0])
const textClass = computed(() => TEXT_SCORE_CLASSES[props.score] || TEXT_SCORE_CLASSES[0])
const isSelected = computed(() => props.isSelected || false)
</script>

<template>
  <div
    :class="backgroundClass"
    :stroke="isSelected ? '#002814' : ''"
    class="relative w-[37px] h-[37px] rounded-[2px] flex items-center justify-center font-accent text-sm"
  >
    <span :class="textClass">{{ label }}</span>
  </div>
</template>

<style scoped></style>
