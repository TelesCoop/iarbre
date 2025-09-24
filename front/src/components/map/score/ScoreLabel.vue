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
      props.backgroundColorClass,
      isClickable ? 'cursor-pointer hover:scale-110 transition-transform duration-200' : '',
      isSelected ? 'ring-2 ring-primary-900' : ''
    ]"
    :style="{ backgroundColor: props.backgroundColor }"
    :data-score="clickable ? score : undefined"
    :title="
      isClickable
        ? `Score ${score} - Cliquez pour ${isSelected ? 'désactiver' : 'activer'} le filtre`
        : undefined
    "
    class="relative flex items-center justify-center font-accent text-xs xs:text-sm transform flex-shrink-0"
    style="width: 11px; height: 27px"
    @click="handleClick"
  >
    <FilterIndicator :is-visible="isSelected" />
  </div>
</template>
