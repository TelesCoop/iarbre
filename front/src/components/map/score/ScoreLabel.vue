<script lang="ts" setup>
import { computed, ref } from "vue"
import FilterIndicator from "../legend/FilterIndicator.vue"

interface ScoreLabelProps {
  score: number
  label: string
  isSelected?: boolean
  clickable?: boolean
  backgroundColor?: string
  backgroundColorClass?: string
}

const props = defineProps<ScoreLabelProps>()

const emit = defineEmits<{
  click: [score: number]
}>()

const scoreLabelRef = ref<HTMLElement | null>(null)
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
    ref="scoreLabelRef"
    :class="[
      'score-label',
      props.backgroundColorClass,
      isClickable ? 'cursor-pointer hover:scale-110 transition-transform duration-200' : '',
      isSelected ? 'border-2 border-primary-900' : ''
    ]"
    :style="{ backgroundColor: props.backgroundColor }"
    :data-score="clickable ? score : undefined"
    :title="
      isClickable
        ? `Score ${score} - Cliquez pour ${isSelected ? 'désactiver' : 'activer'} le filtre`
        : undefined
    "
    @click="handleClick"
  >
    <FilterIndicator :is-visible="isSelected" />
  </div>
</template>

<style scoped>
@reference "@/styles/main.css";

.score-label {
  width: 0.625rem;
  height: 1.125rem;
}

@media (min-width: 1024px) {
  .score-label {
    width: 0.9375rem;
    height: 1.6875rem;
  }
}
</style>
