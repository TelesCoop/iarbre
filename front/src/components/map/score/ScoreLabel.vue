<script lang="ts" setup>
import { computed } from "vue"
import FilterIndicator from "../legend/FilterIndicator.vue"

interface ScoreLabelProps {
  score: number
  label: string
  isSelected?: boolean
  clickable?: boolean
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

const emit = defineEmits<{
  click: [score: number]
}>()

const backgroundClass = computed(() => SCORE_BG_CLASSES[props.score] || SCORE_BG_CLASSES[0])
const textClass = computed(() => TEXT_SCORE_CLASSES[props.score] || TEXT_SCORE_CLASSES[0])
const isSelected = computed(() => props.isSelected || false)
const isClickable = computed(() => props.clickable || false)

const handleClick = () => {
  if (isClickable.value) {
    emit("click", props.score)
  }
}
</script>

<template>
  <div
    :class="[
      backgroundClass,
      isClickable ? 'cursor-pointer hover:scale-110 transition-transform duration-200' : '',
      isSelected ? 'ring-2 ring-primary-900 scale-105 shadow-md' : ''
    ]"
    :data-score="clickable ? score : undefined"
    :title="
      isClickable
        ? `Score ${score} - Cliquez pour ${isSelected ? 'désactiver' : 'activer'} le filtre`
        : undefined
    "
    class="relative w-[24px] h-[24px] lg:w-[36px] lg:h-[36px] rounded-[2px] flex items-center justify-center font-accent text-sm transform"
    @click="handleClick"
  >
    <span :class="textClass">{{ label }}</span>
    <FilterIndicator :is-visible="isSelected" />
  </div>
</template>
